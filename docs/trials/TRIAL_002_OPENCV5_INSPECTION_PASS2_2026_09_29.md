# Work order 2 — OpenCV 5 inspection execution, 29 September 2026

Project 20266878, BMW Thoma. Service/inspection purpose: identify suspected water entry points and assess available repair evidence at the workshop gutter, workshop ridge, sales-room ridge, and entrance-roof connections.

## Executed

Pinned OpenCV 5.0.0 (wheel 5.0.0.93), NumPy 2.3.2. All 42 Day 01 photo entries decoded, 41 unique byte streams. Orientation documents excluded. Algorithm: local dark-feature extraction using a 21-pixel elliptical black-hat kernel, response threshold 25, 3-pixel closing, connected-component area >=30 pixels, extent >=25 pixels, bounding-box elongation >=2. Seven manually selected development regions. Pixel criteria are uncalibrated and do not measure defect dimensions.

## Results and real failures

| Region | Algorithm regions | Assessment after overlay review |
|---|---:|---|
| 2097 central split | 0 | Missed the visually suspected opening. |
| 2094 raised edge | 1 | Small box on tool region; intended raised edge not localized. |
| 2078 curled patch | 1 | Small texture region; intended opening not localized. |
| 2085 disrupted joint | 1 | Broad box spanning ROI; insufficiently specific. |
| 2085 shadow region | 6 | Multiple nuisance proposals; darkness/texture confused with target. |
| 2088 applied coating | 6 | Multiple nuisance proposals; coating is not itself a leak finding. |
| 2075 staining | 1 | Staining proposal does not establish an opening. |

Decision: REJECT_THIS_BASELINE_FOR_DEFECT_DECISIONS. This is a real OpenCV execution and a failed development approach, not a successful water-entry detector. No precision/recall or independent accuracy claim: labels are assistant hypotheses, regions were manually selected, and cases are not held out.

## Work-order evidence decisions

The four visual suspected-water-entry candidates (2097,2094,2078,2085) remain human-review items. Exact allocation to the four work-order targets remains unresolved; no target is marked complete. Gutter water-looking appearance and wall staining warrant inspection but do not establish origin. Image 2088 shows treatment activity, not accepted sealing. Product, substrate, specified 2cm PU installation, preparation, curing and final acceptance remain unverified. The original sealed condition in 2094 may have been altered by preparation.

## Next change

Replace generic dark-feature extraction with a method that uses the expected seam or repair boundary and distinguishes tool edges, shadows, coating and texture. Obtain Arturo's labels and component mapping before an independent evaluation. Preserve same-detail groups. No physical leak confirmation or workmanship acceptance is issued.

Artifacts: reproducible script, results.json (source hashes, manual regions, parameters and candidate coordinates), inspection_candidates.jpg (red algorithm proposals). Red boxes are proposals, not confirmed defects.
