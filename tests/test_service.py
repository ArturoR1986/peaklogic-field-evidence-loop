import cv2
import numpy as np
import pytest

from peaklogic_field_evidence.service import EvidenceService, decode_image_bytes
from peaklogic_field_evidence.schemas import ActionType


def encoded_checkerboard():
    image = np.zeros((600, 800, 3), dtype=np.uint8)
    image[::2, ::2] = 255
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok
    return encoded.tobytes()


def test_service_health_reports_runtime():
    service = EvidenceService()
    health = service.health()
    assert health["status"] == "ok"
    assert health["opencv_major"] >= 4
    assert health["professional_review_status"] == "pending"
    assert health["auth_required"] is False


def test_service_optional_bearer_auth():
    service = EvidenceService(api_key="secret")
    assert service.auth_required is True
    assert service.is_authorized(None) is False
    assert service.is_authorized("Bearer wrong") is False
    assert service.is_authorized("Bearer secret") is True


def test_service_rejects_bad_image_bytes():
    with pytest.raises(ValueError):
        decode_image_bytes(b"not-an-image")


def test_service_processes_image_and_returns_action():
    service = EvidenceService()
    result = service.process_image_bytes(encoded_checkerboard(), media_id="img-1")
    assert result["media_id"] == "img-1"
    assert result["quality"]["usable"] is True
    # Until a real classifier is loaded, usable evidence is not silently accepted.
    assert result["action"] == ActionType.REQUEST_TARGETED_PROOF.value
    assert result["proof_point_source"] is None


def test_service_enforces_upload_limit():
    service = EvidenceService(max_upload_bytes=2)
    with pytest.raises(ValueError):
        service.process_image_bytes(b"abc", media_id="too-big")
