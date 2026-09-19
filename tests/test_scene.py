import cv2
import numpy as np

from peaklogic_field_evidence.scene import analyze_scene_association


def textured_scene(seed=7):
    rng = np.random.default_rng(seed)
    image = rng.integers(0, 80, size=(480, 640, 3), dtype=np.uint8)
    for i in range(12):
        x = 30 + (i % 4) * 145
        y = 30 + (i // 4) * 135
        cv2.rectangle(image, (x, y), (x + 80, y + 70), (180 + i * 3, 210, 240), 3)
        cv2.putText(image, str(i), (x + 20, y + 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    return image


def test_scene_metrics_find_geometry_for_translated_same_scene():
    a = textured_scene()
    matrix = np.float32([[1, 0, 18], [0, 1, 12]])
    b = cv2.warpAffine(a, matrix, (640, 480))
    result = analyze_scene_association(a, b)
    assert result.good_matches >= 4
    assert result.homography_found is True
    assert result.inliers >= 4
    assert 0.0 <= result.association_score <= 1.0


def test_scene_metrics_handle_featureless_images_without_forcing_match():
    a = np.full((480, 640, 3), 100, dtype=np.uint8)
    b = np.full((480, 640, 3), 140, dtype=np.uint8)
    result = analyze_scene_association(a, b)
    assert result.good_matches == 0
    assert result.homography_found is False
    assert result.association_score == 0.0
