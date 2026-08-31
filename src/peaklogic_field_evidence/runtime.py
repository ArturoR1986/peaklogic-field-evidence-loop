from __future__ import annotations

from dataclasses import dataclass
import cv2


@dataclass(frozen=True)
class RuntimeInfo:
    opencv_version: str
    opencv_major: int
    has_dnn: bool
    has_img_hash: bool


def runtime_info() -> RuntimeInfo:
    version = cv2.__version__
    major = int(version.split(".", 1)[0])
    return RuntimeInfo(
        opencv_version=version,
        opencv_major=major,
        has_dnn=hasattr(cv2, "dnn"),
        has_img_hash=hasattr(cv2, "img_hash"),
    )


def require_opencv5() -> RuntimeInfo:
    info = runtime_info()
    if info.opencv_major != 5:
        raise RuntimeError(
            f"Competition runtime requires OpenCV 5.x; found {info.opencv_version}. "
            "Install opencv-contrib-python-headless==5.0.0.93 in a clean environment."
        )
    return info
