from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np


@dataclass(frozen=True)
class Classification:
    label: str
    confidence: float
    raw_label: str | None = None
    source: str = "opencv_dnn"


class ProofPointClassifier:
    """Interface boundary for proof-point classification."""

    def predict(self, image: np.ndarray) -> Classification:
        raise NotImplementedError


class OpenCVDNNProofPointClassifier(ProofPointClassifier):
    """Bounded OpenCV DNN classifier adapter.

    This adapter is real inference plumbing, not a trained competition model by
    itself. Model performance must be measured separately on representative media.
    """

    def __init__(
        self,
        *,
        net,
        labels: Sequence[str],
        input_size: tuple[int, int] = (224, 224),
        confidence_threshold: float = 0.65,
        scalefactor: float = 1.0 / 255.0,
        mean: tuple[float, float, float] = (0.0, 0.0, 0.0),
        swap_rb: bool = True,
        output_is_probabilities: bool = False,
    ) -> None:
        if not labels:
            raise ValueError("labels are required")
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1")
        self.net = net
        self.labels = tuple(labels)
        self.input_size = input_size
        self.confidence_threshold = confidence_threshold
        self.scalefactor = scalefactor
        self.mean = mean
        self.swap_rb = swap_rb
        self.output_is_probabilities = output_is_probabilities

    @classmethod
    def from_onnx(
        cls,
        model_path: str | Path,
        *,
        labels: Sequence[str],
        **kwargs,
    ) -> "OpenCVDNNProofPointClassifier":
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(model_path)
        net = cv2.dnn.readNetFromONNX(str(model_path))
        return cls(net=net, labels=labels, **kwargs)

    @staticmethod
    def _softmax(values: np.ndarray) -> np.ndarray:
        values = values.astype(np.float64)
        values = values - np.max(values)
        exp = np.exp(values)
        denom = exp.sum()
        if not np.isfinite(denom) or denom <= 0:
            raise ValueError("invalid classifier output")
        return exp / denom

    def predict(self, image: np.ndarray) -> Classification:
        if image is None or image.size == 0:
            raise ValueError("classifier received an empty image")
        blob = cv2.dnn.blobFromImage(
            image,
            scalefactor=self.scalefactor,
            size=self.input_size,
            mean=self.mean,
            swapRB=self.swap_rb,
            crop=False,
        )
        self.net.setInput(blob)
        raw = np.asarray(self.net.forward()).reshape(-1)
        if raw.size != len(self.labels):
            raise ValueError(
                f"class count mismatch: model returned {raw.size}, labels define {len(self.labels)}"
            )
        if self.output_is_probabilities:
            probs = raw.astype(np.float64)
            total = probs.sum()
            if np.any(probs < 0) or not np.isfinite(total) or total <= 0:
                raise ValueError("invalid probability output")
            probs = probs / total
        else:
            probs = self._softmax(raw)

        index = int(np.argmax(probs))
        raw_label = self.labels[index]
        confidence = float(probs[index])
        label = raw_label if confidence >= self.confidence_threshold else "unsupported"
        return Classification(
            label=label,
            confidence=confidence,
            raw_label=raw_label,
            source="opencv_dnn",
        )
