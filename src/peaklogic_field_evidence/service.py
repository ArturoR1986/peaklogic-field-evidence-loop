from __future__ import annotations

import argparse
import base64
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import cv2
import numpy as np

from .classifier import OpenCVDNNProofPointClassifier
from .dataset import PROOF_POINT_LABELS
from .orchestrator import EvidenceLoop
from .runtime import runtime_info
from .templates import registry
from .trace import TraceRecorder

DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def decode_image_bytes(payload: bytes) -> np.ndarray:
    if not payload:
        raise ValueError("empty image payload")
    array = np.frombuffer(payload, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise ValueError("payload is not a decodable image")
    return image


class EvidenceService:
    """Small AWS-ready HTTP service around the bounded Evidence Loop."""

    def __init__(
        self,
        *,
        trace_path: str | None = None,
        max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES,
        model_path: str | None = None,
        model_labels: tuple[str, ...] | None = None,
    ) -> None:
        self.max_upload_bytes = max_upload_bytes
        classifier = None
        if model_path:
            labels = model_labels or PROOF_POINT_LABELS
            classifier = OpenCVDNNProofPointClassifier.from_onnx(
                model_path,
                labels=labels,
            )
        template = registry()[0]
        self.loop = EvidenceLoop(
            template,
            recorder=TraceRecorder(trace_path) if trace_path else TraceRecorder(),
            classifier=classifier,
        )

    def health(self) -> dict:
        info = runtime_info()
        return {
            "status": "ok",
            "opencv_version": info.opencv_version,
            "opencv_major": info.opencv_major,
            "competition_runtime_ok": info.opencv_major == 5,
            "template_id": self.loop.template.id,
            "classifier_loaded": self.loop.classifier is not None,
            "professional_review_status": self.loop.state.professional_review_status,
        }

    def process_image_bytes(self, payload: bytes, *, media_id: str) -> dict:
        if len(payload) > self.max_upload_bytes:
            raise ValueError(f"image exceeds max upload size of {self.max_upload_bytes} bytes")
        image = decode_image_bytes(payload)
        observation, action = self.loop.process_image(image, media_id=media_id)
        return {
            "media_id": media_id,
            "quality": observation.quality.__dict__,
            "duplicate_of": observation.duplicate_of,
            "proof_point_label": observation.proof_point_label,
            "proof_point_confidence": observation.proof_point_confidence,
            "proof_point_source": observation.proof_point_source,
            "action": action.action.value,
            "reason": action.reason,
            "proof_point_id": action.proof_point_id,
        }

    def advance_stage(self, stage: str) -> dict:
        action = self.loop.advance_stage(stage)
        return {
            "stage": self.loop.state.current_stage,
            "action": action.action.value,
            "reason": action.reason,
            "proof_point_id": action.proof_point_id,
        }

    def review_packet(self) -> dict:
        return self.loop.review_packet()


class _Handler(BaseHTTPRequestHandler):
    service: EvidenceService

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0"))
        if length > self.service.max_upload_bytes:
            raise ValueError("request body exceeds configured upload limit")
        return self.rfile.read(length)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json(200, self.service.health())
            return
        if parsed.path == "/v1/evidence/review":
            self._json(200, self.service.review_packet())
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/v1/evidence/image":
                query = parse_qs(parsed.query)
                media_id = query.get("media_id", ["upload"])[0]
                result = self.service.process_image_bytes(self._read_body(), media_id=media_id)
                self._json(200, result)
                return
            if parsed.path == "/v1/evidence/stage":
                raw = self._read_body()
                payload = json.loads(raw.decode("utf-8"))
                self._json(200, self.service.advance_stage(payload["stage"]))
                return
            self._json(404, {"error": "not_found"})
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self._json(400, {"error": "bad_request", "detail": str(exc)})

    def log_message(self, format: str, *args) -> None:
        # Keep stdout clean for structured container logs.
        return


def build_service_from_env() -> EvidenceService:
    model_path = os.getenv("PROOF_MODEL_PATH")
    labels_env = os.getenv("PROOF_MODEL_LABELS")
    labels = tuple(x.strip() for x in labels_env.split(",") if x.strip()) if labels_env else None
    return EvidenceService(
        trace_path=os.getenv("TRACE_PATH", "/tmp/peaklogic-evidence-trace.jsonl"),
        max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", str(DEFAULT_MAX_UPLOAD_BYTES))),
        model_path=model_path,
        model_labels=labels,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Print health payload and exit without opening a port")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8080")))
    args = parser.parse_args()

    service = build_service_from_env()
    if args.check:
        print(json.dumps(service.health(), indent=2))
        return

    handler = type("EvidenceRequestHandler", (_Handler,), {"service": service})
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(json.dumps({"event": "server_started", "host": args.host, "port": args.port}))
    server.serve_forever()


if __name__ == "__main__":
    main()
