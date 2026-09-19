import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from http.server import ThreadingHTTPServer

from peaklogic_field_evidence.service import EvidenceService, _Handler


def start_server():
    service = EvidenceService(api_key="field-secret", review_api_key="review-secret")
    handler = type("TestEvidenceHandler", (_Handler,), {"service": service})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, service


def request_json(url, *, method="GET", token=None, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_health_is_available_without_credentials():
    server, _ = start_server()
    try:
        port = server.server_address[1]
        status, payload = request_json(f"http://127.0.0.1:{port}/health")
        assert status == 200
        assert payload["status"] == "ok"
        assert payload["auth_required"] is True
        assert payload["review_auth_configured"] is True
    finally:
        server.shutdown()
        server.server_close()


def test_field_credential_cannot_record_professional_review():
    server, service = start_server()
    try:
        port = server.server_address[1]
        status, payload = request_json(
            f"http://127.0.0.1:{port}/v1/review/decision",
            method="POST",
            token="field-secret",
            payload={
                "status": "needs_follow_up",
                "actor": "reviewer",
                "note": "Need more evidence.",
            },
        )
        assert status == 403
        assert payload["error"] == "review_forbidden"
        assert service.loop.state.professional_review_status == "pending"
    finally:
        server.shutdown()
        server.server_close()


def test_reviewer_credential_records_human_review():
    server, service = start_server()
    try:
        port = server.server_address[1]
        status, payload = request_json(
            f"http://127.0.0.1:{port}/v1/review/decision",
            method="POST",
            token="review-secret",
            payload={
                "status": "needs_follow_up",
                "actor": "qualified-reviewer",
                "note": "Need non-visual confirmation.",
            },
        )
        assert status == 200
        assert payload["professional_review_status"] == "needs_follow_up"
        assert service.loop.state.professional_review_actor == "qualified-reviewer"
        assert service.loop.recorder.events[-1].event_type == "human_review"
    finally:
        server.shutdown()
        server.server_close()


def test_evidence_endpoint_requires_field_credential():
    server, _ = start_server()
    try:
        port = server.server_address[1]
        status, payload = request_json(
            f"http://127.0.0.1:{port}/v1/evidence/stage",
            method="POST",
            payload={"stage": "before_cover"},
        )
        assert status == 401
        assert payload["error"] == "unauthorized"
    finally:
        server.shutdown()
        server.server_close()
