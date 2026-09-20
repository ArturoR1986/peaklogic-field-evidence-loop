from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import cv2
import numpy as np
from .schemas import QualityMetrics


@dataclass(frozen=True)
class SampledFrame:
    frame_index: int
    timestamp_seconds: float
    frame: np.ndarray
    quality: QualityMetrics
    hash_bits: np.ndarray


def analyze_quality(
    image: np.ndarray,
    min_sharpness: float = 45.0,
    min_luminance: float = 25.0,
    max_luminance: float = 235.0,
    min_width: int = 320,
    min_height: int = 240,
) -> QualityMetrics:
    if image is None or image.size == 0:
        return QualityMetrics(0.0, 0.0, 0, 0, False, ("empty_image",))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    luminance = float(gray.mean())
    h, w = gray.shape[:2]
    reasons: list[str] = []
    if sharpness < min_sharpness:
        reasons.append("blurred")
    if luminance < min_luminance:
        reasons.append("underexposed")
    if luminance > max_luminance:
        reasons.append("overexposed")
    if w < min_width or h < min_height:
        reasons.append("low_resolution")
    return QualityMetrics(sharpness, luminance, w, h, not reasons, tuple(reasons))


def average_hash(image: np.ndarray, size: int = 16) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    small = cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA)
    return (small >= small.mean()).reshape(-1)


def hamming_distance(a: np.ndarray, b: np.ndarray) -> int:
    return int(np.count_nonzero(a != b))


def is_near_duplicate(a: np.ndarray, b: np.ndarray, max_hamming: int = 14) -> bool:
    return hamming_distance(average_hash(a), average_hash(b)) <= max_hamming


def sample_video(
    path: str | Path,
    sample_fps: float = 1.5,
    max_candidates: int = 120,
    novelty_hamming: int = 18,
) -> list[SampledFrame]:
    """Sample a bounded walkthrough while preserving coverage across its full duration.

    The candidate cap is applied by widening the sampling stride, not by stopping
    early after N retained frames. This prevents long walkthroughs from silently
    dropping the final portion of the job.
    """
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    requested_step = max(1, round(fps / sample_fps))
    bounded_step = requested_step
    if max_candidates > 0 and total_frames > 0:
        bounded_step = max(requested_step, math.ceil(total_frames / max_candidates))

    retained: list[SampledFrame] = []
    frame_index = -1
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_index += 1
        if frame_index % bounded_step:
            continue
        quality = analyze_quality(frame)
        if not quality.usable:
            continue
        bits = average_hash(frame)
        if retained and hamming_distance(bits, retained[-1].hash_bits) < novelty_hamming:
            continue
        retained.append(
            SampledFrame(
                frame_index=frame_index,
                timestamp_seconds=frame_index / fps,
                frame=frame,
                quality=quality,
                hash_bits=bits,
            )
        )
    cap.release()

    if max_candidates > 0 and len(retained) > max_candidates:
        indices = np.linspace(0, len(retained) - 1, num=max_candidates, dtype=int)
        retained = [retained[int(i)] for i in indices]
    return retained
