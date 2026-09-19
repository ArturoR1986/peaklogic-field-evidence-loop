from __future__ import annotations

from dataclasses import asdict, dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class SceneAssociationMetrics:
    keypoints_a: int
    keypoints_b: int
    candidate_matches: int
    good_matches: int
    inliers: int
    inlier_ratio: float
    association_score: float
    homography_found: bool

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_scene_association(
    image_a: np.ndarray,
    image_b: np.ndarray,
    *,
    nfeatures: int = 1500,
    ratio_threshold: float = 0.75,
    ransac_reproj_threshold: float = 5.0,
    target_good_matches: int = 40,
) -> SceneAssociationMetrics:
    """Return transparent OpenCV feature-match metrics for two views.

    association_score is a bounded heuristic, not a calibrated probability.
    Representative same-area/different-area data is required before choosing a
    decision threshold for competition evaluation.
    """
    if image_a is None or image_a.size == 0 or image_b is None or image_b.size == 0:
        raise ValueError("scene association requires two non-empty images")

    gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY) if image_a.ndim == 3 else image_a
    gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY) if image_b.ndim == 3 else image_b

    orb = cv2.ORB_create(nfeatures=nfeatures)
    kp_a, desc_a = orb.detectAndCompute(gray_a, None)
    kp_b, desc_b = orb.detectAndCompute(gray_b, None)

    n_a, n_b = len(kp_a), len(kp_b)
    if desc_a is None or desc_b is None or n_a < 2 or n_b < 2:
        return SceneAssociationMetrics(n_a, n_b, 0, 0, 0, 0.0, 0.0, False)

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    knn = matcher.knnMatch(desc_a, desc_b, k=2)
    good = []
    for pair in knn:
        if len(pair) != 2:
            continue
        first, second = pair
        if first.distance < ratio_threshold * second.distance:
            good.append(first)

    candidate_matches = len(knn)
    good_count = len(good)
    if good_count < 4:
        score = min(good_count / max(target_good_matches, 1), 1.0) * 0.25
        return SceneAssociationMetrics(
            n_a, n_b, candidate_matches, good_count, 0, 0.0, float(score), False
        )

    src = np.float32([kp_a[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kp_b[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    homography, mask = cv2.findHomography(src, dst, cv2.RANSAC, ransac_reproj_threshold)

    if homography is None or mask is None:
        return SceneAssociationMetrics(
            n_a, n_b, candidate_matches, good_count, 0, 0.0, 0.0, False
        )

    inliers = int(mask.ravel().sum())
    inlier_ratio = inliers / good_count if good_count else 0.0
    match_strength = min(good_count / max(target_good_matches, 1), 1.0)
    score = float(max(0.0, min(1.0, inlier_ratio * match_strength)))
    return SceneAssociationMetrics(
        n_a,
        n_b,
        candidate_matches,
        good_count,
        inliers,
        float(inlier_ratio),
        score,
        True,
    )
