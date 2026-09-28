"""Reproduce the Trial 002 repeated-view and dark-pixel sensitivity probe.

Usage: python trial002_source_bound_probe.py PATH_TO_2097 PATH_TO_2098
Requires OpenCV 5.0.0 and NumPy. Outputs JSON to stdout.
The ROI was selected manually on 2097 and is not a calibrated material mask.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np


def read(path):
    b = Path(path).read_bytes()
    im = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
    if im is None:
        raise ValueError(f"Cannot decode {path}")
    return im, hashlib.sha256(b).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("image_2097")
    p.add_argument("image_2098")
    args = p.parse_args()
    a, sha_a = read(args.image_2097)
    b, sha_b = read(args.image_2098)
    orb = cv2.ORB_create(nfeatures=3000)
    ka, da = orb.detectAndCompute(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), None)
    kb, db = orb.detectAndCompute(cv2.cvtColor(b, cv2.COLOR_BGR2GRAY), None)
    candidates = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(da, db, k=2)
    good = [first for first, second in candidates if first.distance < 0.75 * second.distance]
    inliers = 0
    if len(good) >= 8:
        src = np.float32([ka[m.queryIdx].pt for m in good])
        dst = np.float32([kb[m.trainIdx].pt for m in good])
        _, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5)
        inliers = int(mask.sum()) if mask is not None else 0
    gray = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    x0, y0, x1, y1 = 220, 520, 1040, 1090
    if a.shape[1] != 1152 or a.shape[0] != 1536:
        raise ValueError("2097 dimensions differ from the recorded ROI geometry")
    roi = gray[y0:y1, x0:x1]
    sensitivity = [
        {"gray_below": t, "dark_pixels": int((roi < t).sum()),
         "roi_pixels": int(roi.size), "fraction": round(float((roi < t).mean()), 3)}
        for t in (65, 80, 95, 110)
    ]
    print(json.dumps({
        "opencv": cv2.__version__, "inputs": [
            {"name": Path(args.image_2097).name, "sha256": sha_a},
            {"name": Path(args.image_2098).name, "sha256": sha_b}],
        "orb": {"nfeatures": 3000, "ratio": 0.75, "ransac_pixels": 5,
                "good_matches": len(good), "inliers": inliers},
        "roi_xyxy": [x0, y0, x1, y1], "threshold_sensitivity": sensitivity,
        "decision": "ABSTAIN_PHYSICAL_OR_COMPLETION_MEASUREMENT",
    }, indent=2))


if __name__ == "__main__":
    main()
