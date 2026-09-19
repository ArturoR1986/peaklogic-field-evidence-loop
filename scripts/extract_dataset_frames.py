from __future__ import annotations

import argparse
from pathlib import Path
import cv2

from peaklogic_field_evidence.dataset import DatasetRecord, write_manifest
from peaklogic_field_evidence.media import sample_video


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract bounded, usable, non-redundant candidate frames for labeling.")
    parser.add_argument("video")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--sample-fps", type=float, default=1.5)
    parser.add_argument("--prefix", default="candidate")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = sample_video(args.video, sample_fps=args.sample_fps)
    records = []
    for idx, sampled in enumerate(frames, start=1):
        name = f"{args.prefix}_{idx:04d}_t{sampled.timestamp_seconds:.2f}.jpg"
        path = output_dir / name
        if not cv2.imwrite(str(path), sampled.frame):
            raise RuntimeError(f"Failed to write frame: {path}")
        records.append(DatasetRecord(
            record_id=f"{args.prefix}-{idx:04d}",
            media_path=str(path),
            media_type="video_frame",
            label="unsupported",
            split="unassigned",
            source_media_path=str(args.video),
            source_timestamp_seconds=sampled.timestamp_seconds,
            notes="Candidate frame; label must be reviewed before training.",
        ))
    write_manifest(records, args.manifest)
    print(f"retained_frames={len(records)} manifest={args.manifest}")


if __name__ == "__main__":
    main()
