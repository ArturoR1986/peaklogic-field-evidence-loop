"""OpenCV 5 development probe; manual ROIs, no leak classification or accuracy claim."""
import cv2, numpy as np, json, hashlib, argparse
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('root'); p.add_argument('output'); a=p.parse_args()
assert cv2.__version__=='5.0.0'
root=Path(a.root); out=Path(a.output); out.mkdir(exist_ok=True)
# Normalized manually selected regions; labels are assistant hypotheses, not ground truth.
cases=[('2097',(0.42,0.47,0.58,0.63),'split patch'),('2094',(0.12,0.46,0.62,0.84),'raised repair edge'),('2078',(0.30,0.60,0.90,0.91),'curled patch'),('2085',(0.34,0.32,0.65,0.52),'joint at metal'),('2085',(0.03,0.18,0.32,0.57),'shadow confounder'),('2088',(0.15,0.46,0.48,0.66),'applied coating confounder'),('2075',(0.51,0.48,0.68,0.67),'staining confounder')]
records=[]; panels=[]
files=sorted(root.glob('attachments/**/*.jpg')); audit=[]
for path in files:
 if not path.name.startswith('10000520'): continue
 if not (2055 <= int(path.stem[:10][-4:]) <= 2098): continue
 raw=path.read_bytes(); im=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
 if im is not None: audit.append({'file':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'dimensions':[im.shape[1],im.shape[0]]})
for i,(num,box,meaning) in enumerate(cases):
 path=next(f for f in files if f.name==f'100005{num}.jpg'); raw=path.read_bytes(); im=cv2.imdecode(np.frombuffer(raw,np.uint8),1); h,w=im.shape[:2]
 x0,y0,x1,y1=[int(v*d) for v,d in zip(box,(w,h,w,h))]; roi=im[y0:y1,x0:x1]; gray=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
 bh=cv2.morphologyEx(gray,cv2.MORPH_BLACKHAT,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(21,21)))
 mask=np.uint8(bh>=25)*255
 mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
 n,labels,stats,centroids=cv2.connectedComponentsWithStats(mask)
 kept=[]; overlay=roi.copy()
 for j in range(1,n):
  x,y,bw,bhgt,area=map(int,stats[j]); elong=max(bw,bhgt)/max(1,min(bw,bhgt))
  if area>=30 and max(bw,bhgt)>=25 and elong>=2:
   kept.append({'bbox_xyxy':[x+x0,y+y0,x+bw+x0,y+bhgt+y0],'area_pixels':area}); cv2.rectangle(overlay,(x,y),(x+bw,y+bhgt),(0,0,255),2)
 rec={'file':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'manual_roi_xyxy':[x0,y0,x1,y1],'assistant_hypothesis':meaning,'algorithm_candidates':kept,'decision':'HUMAN_REVIEW_REQUIRED','work_order_target':'UNRESOLVED'};records.append(rec)
 panel=cv2.resize(overlay,(420,300)); banner=np.full((55,420,3),255,np.uint8); cv2.putText(banner,f'{num}: {meaning}',(8,22),0,.52,(0,0,0),1);cv2.putText(banner,f'{len(kept)} algorithm regions; manual ROI',(8,44),0,.48,(0,0,0),1);panels.append(np.vstack([banner,panel]))
while len(panels)%2: panels.append(np.full_like(panels[0],255))
cv2.imwrite(str(out/'inspection_candidates.jpg'),np.vstack([np.hstack(panels[i:i+2]) for i in range(0,len(panels),2)]))
result={'opencv':cv2.__version__,'numpy':np.__version__,'method':{'blackhat_kernel':21,'threshold':25,'close_kernel':3,'min_area':30,'min_extent':25,'min_bbox_elongation':2},'manual_roi':True,'decoded_entries':len(audit),'unique_sha256':len(set(r['sha256'] for r in audit)),'audit':audit,'cases':records,'boundary':'Development localization only. No leak classifier, held-out labels, physical measurement or acceptance.'}
(out/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps({'opencv':result['opencv'],'decoded':len(audit),'unique':result['unique_sha256'],'cases':[(r['file'],r['assistant_hypothesis'],len(r['algorithm_candidates'])) for r in records]},indent=2))
