from pathlib import Path
import cv2
import numpy as np

out = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "generated"
out.mkdir(parents=True, exist_ok=True)

page = np.full((900, 650, 3), 255, dtype=np.uint8)
lines = [
    ("WORK ORDER # A-101", 90),
    ("SITE: DEMO ROOF", 165),
    ("AREA: ROOF ZONE A", 240),
    ("TASK: INSTALL SAFETY ANCHOR", 315),
]
for text, y in lines:
    cv2.putText(page, text, (45,y), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0,0,0), 2, cv2.LINE_AA)
cv2.rectangle(page, (20,20),(630,880),(0,0,0),3)

src = np.float32([[0,0],[649,0],[649,899],[0,899]])
dst = np.float32([[110,80],[770,115],[805,1040],[70,980]])
M = cv2.getPerspectiveTransform(src,dst)
canvas = np.full((1120,900,3),50,dtype=np.uint8)
warped = cv2.warpPerspective(page,M,(900,1120),borderValue=(50,50,50))
mask = cv2.warpPerspective(np.full((900,650),255,dtype=np.uint8),M,(900,1120))
canvas[mask>0]=warped[mask>0]
cv2.imwrite(str(out/"work_order_skewed.png"),canvas)
print(out/"work_order_skewed.png")
