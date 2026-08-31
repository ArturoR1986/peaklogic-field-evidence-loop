from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Classification:
    label: str
    confidence: float


class ProofPointClassifier:
    """Interface boundary for the learned OpenCV DNN proof-point classifier.

    Intentionally not implemented in Build Increment 0. The competition build must
    train/evaluate a bounded classifier on representative workflow media, export it
    to ONNX, then run inference through OpenCV 5 DNN. No filename/rule-based fake
    classifier is permitted as a substitute for measured vision performance.
    """

    def predict(self, image: np.ndarray) -> Classification:
        raise NotImplementedError("Proof-point classifier is Build Gate 2; representative labeled media is required.")
