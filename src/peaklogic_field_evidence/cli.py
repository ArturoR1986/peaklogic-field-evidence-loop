from __future__ import annotations

import argparse
import json
import cv2

from .demo import run_trace_demo
from .document_scan import scan_document
from .media import analyze_quality, sample_video
from .ocr import extract_text, extract_key_fields
from .runtime import runtime_info, require_opencv5
from .templates import match_template


def cmd_doctor(_: argparse.Namespace) -> int:
    info = runtime_info()
    payload = {
        "opencv_version": info.opencv_version,
        "opencv_major": info.opencv_major,
        "has_dnn": info.has_dnn,
        "has_img_hash": info.has_img_hash,
        "competition_runtime_ok": info.opencv_major == 5,
    }
    print(json.dumps(payload, indent=2))
    require_opencv5()
    return 0


def cmd_image(args: argparse.Namespace) -> int:
    image = cv2.imread(args.path)
    if image is None:
        raise SystemExit(f"Could not read image: {args.path}")
    q = analyze_quality(image)
    print(json.dumps(q.__dict__, indent=2))
    return 0


def cmd_video(args: argparse.Namespace) -> int:
    frames = sample_video(args.path, sample_fps=args.sample_fps)
    print(json.dumps([
        {
            "frame_index": f.frame_index,
            "timestamp_seconds": round(f.timestamp_seconds, 3),
            "sharpness": round(f.quality.sharpness, 2),
            "mean_luminance": round(f.quality.mean_luminance, 2),
        } for f in frames
    ], indent=2))
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    image = cv2.imread(args.path)
    if image is None:
        raise SystemExit(f"Could not read image: {args.path}")
    result = scan_document(image)
    if not result.found_document or result.cleaned is None:
        print(json.dumps({"found_document": False, "action": "request_rescan"}, indent=2))
        return 2
    text = extract_text(result.cleaned, lang=args.lang)
    fields = extract_key_fields(text)
    template = match_template(fields.get("task", text))
    payload = {
        "found_document": True,
        "text": text,
        "fields": fields,
        "template_id": template.id if template else None,
        "quality_critical": template.quality_critical if template else None,
        "next_action": "load_template" if template else "human_confirm_task_type",
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_cleaned:
        cv2.imwrite(args.output_cleaned, result.cleaned)
    return 0


def cmd_trace_demo(args: argparse.Namespace) -> int:
    payload = run_trace_demo(args.trace)
    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="peaklogic-evidence")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("doctor", help="Verify exact OpenCV competition runtime")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("analyze-image", help="Analyze deterministic image quality")
    p.add_argument("path")
    p.set_defaults(func=cmd_image)

    p = sub.add_parser("sample-video", help="Reduce a bounded video to usable, non-redundant frames")
    p.add_argument("path")
    p.add_argument("--sample-fps", type=float, default=1.5)
    p.set_defaults(func=cmd_video)

    p = sub.add_parser("scan-work-order", help="Rectify/clean a work-order image, OCR it, and map a known template")
    p.add_argument("path")
    p.add_argument("--lang", default="eng")
    p.add_argument("--output-cleaned")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("trace-demo", help="Run the bounded Agentic Vision trace demo and write JSONL audit events")
    p.add_argument("--trace", default="outputs/agentic_trace_demo.jsonl")
    p.set_defaults(func=cmd_trace_demo)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
