# Trial 001 — OpenCV 5 representative runtime proof (2026-09-26)

## Scope and environment

Fresh isolated Python 3.12 environment installed from the repository's pinned versions:
- opencv-contrib-python-headless==5.0.0.93
- numpy==2.3.2

Runtime reported `cv2.__version__ == 5.0.0`; `cv2.dnn` and `cv2.img_hash` were present. Docker was unavailable in this execution workspace, so this is a pinned-wheel proof, **not** a container run or the repository's full EvidenceState service.

Source media were fetched from the Trial 001 Drive record and decoded as JPEG:
- Day 06 `1000051975.jpg`, SHA-256 `34dcba4f8639ff6e96f8585fcde20d5cf262a713db02263a4ae72353563ebd59`
- Day 06 `1000051976.jpg`, SHA-256 `9c200a07e9ebfba3a63f147a84b02d71363efd65c29bfdecaac21ef9f83c567f`
- Day 02 known failure `1000051469.jpg`, SHA-256 `1e34fe0fc72d92d0f6315e5f3931263b5b2262ca6f30758ca50efb9060db7996`

## Observed results

| File | Dimensions | Laplacian variance | Mean grayscale | Gate |
| --- | ---: | ---: | ---: | --- |
| Day 06 1975 | 1152 × 1536 | 228.84 | 153.72 | Pass |
| Day 06 1976 | 1536 × 1152 | 50.07 | 168.04 | Pass |
| Day 02 1469 | 1536 × 1152 | 2.46 | 175.10 | Fail: blur |

Gate used here: Laplacian variance >= 45, mean grayscale 25–235, minimum 320 × 240. The failed value reproduces the previously recorded Day 02 blur observation in the exact OpenCV 5 runtime.

On Day 06 1975 ↔ 1976, OpenCV 5 ORB (2,000 features), Hamming matching, 0.75 ratio filter and RANSAC homography (5 px threshold) produced 35 ratio-filtered matches, 22 RANSAC inliers, and an inlier ratio of 0.629. This is same-scene geometric support only; it is not a calibrated probability or proof of installation quality.

## Reproduction

Install the two pinned packages in a clean environment, download the three named Trial 001 files, verify their hashes, then run the following against local paths:

```python
import cv2, numpy as np
from pathlib import Path
paths = [Path("1000051975.jpg"), Path("1000051976.jpg"), Path("1000051469.jpg")]
assert cv2.__version__ == "5.0.0"
for p in paths:
    im = cv2.imdecode(np.frombuffer(p.read_bytes(), np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    luminance = gray.mean()
    usable = sharpness >= 45 and 25 <= luminance <= 235 and im.shape[1] >= 320 and im.shape[0] >= 240
    print(p.name, im.shape[1], im.shape[0], round(sharpness, 2), round(luminance, 2), usable)
```

The pair experiment used `cv2.ORB_create(nfeatures=2000)`, `BFMatcher(cv2.NORM_HAMMING).knnMatch(k=2)`, Lowe ratio `m.distance < 0.75*n.distance`, and `cv2.findHomography(..., cv2.RANSAC, 5.0)`.

## Boundary and next gate

This proves the pinned OpenCV 5 wheel executes quality and geometric operations on real Trial 001 media, including a known failure. It does **not** yet prove full Days 1–6 ingestion, relevance classification, source-grounded Sarnabar spacing, component EvidenceState transitions, calibrated performance, container execution, AWS deployment, or professional acceptance. Next: run the repository's job-bound pipeline in its pinned container on a selected source-bound Sarnabar component; persist observation, uncertainty/abstention, action and trace.
