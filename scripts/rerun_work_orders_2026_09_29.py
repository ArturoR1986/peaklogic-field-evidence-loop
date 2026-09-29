import cv2,numpy as np,json,hashlib
from pathlib import Path
assert cv2.__version__=='5.0.0'
paths=[p for p in Path('attachments').glob('**/*.jpg') if p.name in ('1000051975.jpg','1000051976.jpg','1000051469.jpg')]+sorted(Path('day6_final').glob('*.jpg'))
rows=[];panels=[]
for p in paths:
 b=p.read_bytes(); im=cv2.imdecode(np.frombuffer(b,np.uint8),1);g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY); lap=float(cv2.Laplacian(g,cv2.CV_64F).var()); mean=float(g.mean()); valid=lap>=45 and 25<=mean<=235 and min(im.shape[:2])>=240
 rows.append({'trial':'001','file':p.name,'sha256':hashlib.sha256(b).hexdigest(),'dimensions':[im.shape[1],im.shape[0]],'laplacian_variance':round(lap,2),'gray_mean':round(mean,2),'quality_gate':'PASS' if valid else 'FAIL','component_state':'UNRESOLVED','action':'REVIEW_SOURCE_BINDING' if valid else 'DO_NOT_COUNT_AS_PROOF_CLOSED_RECORD_GAP'})
 im=cv2.resize(im,(300,400));cv2.putText(im,p.name,(6,20),0,.5,(0,0,255),1);panels.append(im)
while len(panels)%4:panels.append(np.full_like(panels[0],255))
cv2.imwrite('trial001_rerun_contact.jpg',np.vstack([np.hstack(panels[i:i+4]) for i in range(0,len(panels),4)]))
Path('trial001_rerun_results.json').write_text(json.dumps({'opencv':cv2.__version__,'scope':'13 locally preserved Trial001 images only, not complete six-day run','gate':{'laplacian_min':45,'gray_range':[25,235]},'records':rows},indent=2));print(json.dumps(rows,indent=2))
