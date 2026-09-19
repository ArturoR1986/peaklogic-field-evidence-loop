# Representative Field Media Capture Protocol

## Purpose
Collect real or safely staged fall-protection-anchor / roofing media so the current OpenCV 5 mechanics can be evaluated on representative inputs.

This is a competition dataset protocol, **not an installation specification**.

Do not perform, alter, loosen, fasten, cover, uncover, or otherwise manipulate safety-critical work solely to create training data. Document only work already being performed by qualified personnel under the applicable manufacturer instructions and site rules.

## First useful batch
Aim first for:
- 40–80 usable still images
- 3–8 short videos
- one consistent anchor/product workflow where possible

This is enough to expose data/label problems and start model work. It is not assumed to be enough for final performance.

## Proof-point labels
- `location_context`
- `product_identification`
- `substrate_context`
- `critical_attachment`
- `process_before_cover`
- `finished_detail`
- `finished_context`
- `unsupported`

The hero class is `critical_attachment`: attachment/fixation evidence while it remains visible and before the roof assembly conceals it.

## Failure media to include
Without creating unsafe conditions, include naturally occurring or harmless capture failures:
- motion blur
- out-of-focus capture
- glare / overexposure
- shadow / underexposure
- partial occlusion
- overly tight crop
- overly wide view
- duplicate / near-duplicate captures
- wrong but visually similar roof area
- unrelated / unsupported media
- low-texture surfaces
- final/completion view where critical concealed proof is absent

## Video
Preferred examples:
- 30–60 second arrival/context walkthrough
- 5–10 second targeted proof clip at a critical visible stage
- 30–60 second completion walkthrough

Do not record continuously.

## Rights and privacy
Each media item must ultimately be classified as:
- owned by the user/PeakLogic,
- staged specifically for the competition,
- explicitly authorized for competition/model use,
- or excluded from training.

Do not scrape manufacturer/public web imagery into the training set merely because it is viewable.

Avoid faces, license plates, customer documents, house numbers, personal information, and unrelated workers where practical.

## Label review questions
For every candidate:
1. What proof point, if any, does the image actually support?
2. Is the relevant region sufficiently visible?
3. Is it genuinely new evidence or a duplicate?
4. Can the intended work area be associated with the job context?
5. Would the evidence remain useful after the next layer hides the detail?
6. Are we claiming only what the pixels can support?

## Evaluation split
Freeze train/validation/test assignment before final evaluation. Do not tune thresholds against the held-out test split.
