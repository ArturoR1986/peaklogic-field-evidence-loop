from pathlib import Path
import cv2
import numpy as np
import pytest
from peaklogic_field_evidence.media import sample_video


def make_video(path: Path):
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (640, 480))
    if not writer.isOpened():
        pytest.skip("MJPG VideoWriter unavailable in this OpenCV build")
    for i in range(60):
        frame = np.full((480,640,3), 60, dtype=np.uint8)
        segment = i // 20
        cv2.rectangle(frame, (60 + segment*140, 80), (250 + segment*140, 360), (230,230,230), -1)
        cv2.putText(frame, f"SEGMENT {segment}", (80, 430), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        writer.write(frame)
    writer.release()


def test_video_sampling_reduces_redundancy(tmp_path):
    path = tmp_path / "walkthrough.avi"
    make_video(path)
    frames = sample_video(path, sample_fps=2.0, novelty_hamming=8)
    assert 1 <= len(frames) < 12
    assert all(f.quality.usable for f in frames)
    assert all(f.timestamp_seconds >= 0 for f in frames)
