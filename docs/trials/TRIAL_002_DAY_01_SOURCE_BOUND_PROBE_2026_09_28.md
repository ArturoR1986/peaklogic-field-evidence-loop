# Trial 002 — Day 01 source-bound OpenCV 5 probe

Date: 2026-09-28. Job key: `Trial-002-BMW-Thoma-20266878`. State: **technical evidence unresolved; human review pending**.

## Source, input and boundary

The photographed Peter Gerber work-preparation sheet for BMW Thoma / project 20266878 directs four tasks: workshop gutter and PU/FLK detail after a water-trace check; workshop composite-sheet ridge-joint check; sales-room trapezoidal-sheet ridge joints sealed with FLK; and connections behind the entrance roof sealed with FLK. The annotated aerial image and detail sheet suggest locations but do not give surveyed image coordinates, required coverage dimensions or an approved acceptance threshold.

The 42-entry Day 01 photo set was decoded under pinned OpenCV 5.0.0. An exact-hash pair (`1000052084.jpg`, `1000052084b.jpg`) leaves 41 unique photo byte streams. A companion JSONL manifest binds every raw photo to the job, day, exact Drive file ID, SHA-256, dimensions and a **candidate visual scene**. No individual photo's physical zone or work-order component has yet been independently verified; all 42 records retain `zone_verified=false`, `component_verified=false`, `evidence_state=UNRESOLVED`. The scene candidates are visual grouping aids, not completed work claims.

## Bounded observation and geometry probe

Candidate images `1000052097.jpg` and `1000052098.jpg` show a dark local patch adjacent to sheet metal from different framing. Under OpenCV 5.0.0, ORB (3,000 features per image), BF Hamming 0.75 ratio test and 5-pixel RANSAC homography produced **647 good matches and 609 inliers** (0.941 inlier fraction) in the preserved script. This supports a repeated-view association for this visible patch. It does not establish which marked roof zone it belongs to, when the material was applied, its product identity or the result of a seal.

On `2097` (1152 × 1536 pixels), a manually selected image ROI `[x0=220,y0=520,x1=1040,y1=1090]` is 820 × 570 = 467,400 pixels. A simple grayscale dark-pixel fraction within that ROI varies materially with threshold:

| Gray value below | Dark pixels | Fraction of ROI |
| ---: | ---: | ---: |
| 65 | 140,890 | 0.301 |
| 80 | 193,578 | 0.414 |
| 95 | 242,994 | 0.520 |
| 110 | 276,561 | 0.592 |

The ROI also contains shadow, debris and adjacent dark areas. A threshold chosen after seeing the photo is not a validated material segmentation. There is no physical scale, perspective rectification, work-order coverage tolerance, product confirmation or site-zone binding. Consequently **abstain from a real-world patch-area, coverage, FLK compliance, or completed-joint measurement**. The pixel fractions are an algorithm-sensitivity probe, not a pass/fail metric.

## Evidence loop trace

| Stage | Recorded result |
| --- | --- |
| Source requirement | Check/seal specified ridge joints or connections with FLK, depending on the actual zone. The source does not state a measurable photo-based area threshold. |
| Input/provenance | Trial 002 Day 01 `2097` and `2098`; exact Drive IDs and hashes in the companion manifest. |
| CV observation | Same visible patch is strongly associated by 609 RANSAC inliers. Dark-pixel output changes from 30.1% to 59.2% across four plausible thresholds. |
| Uncertainty/failure | Zone and product unverified; ROI manually selected; shadow and debris confound segmentation; no scale or governing quantitative rule. |
| EvidenceState | `UNRESOLVED` for workmanship/completion; `OBSERVED_CONTEXT` only for presence of a visible patch. |
| Action | Bind the patch to a marked roof zone and specific joint, obtain the approved detail and process/material record, then ask a qualified human to assess the evidence. Do not promote to completion. |

Additional failure cases: the exact duplicate `2084b` must not count as independent proof, and the soft `2061` image must not independently satisfy a fine-detail proof point. Repeated-view ORB checks also associated `2089`/`2090` (1,305 inliers), `2078`/`2079` (765), `2085`/`2086` (1,301), and `2092`/`2093` (731). These are candidate scene links only; calibrated probabilities and chronology are not inferred.

## Competition result and next gate

This is a real-media, source-linked OpenCV 5 observation → uncertainty → abstain/action trace, including duplicate and segmentation failure cases. It **does not pass** the stronger end-to-end completion claim: the visual scene map is provisional, there is no source-approved physical measurement threshold, no validated semantic material detector, no persistent application EvidenceState run, and no qualified human acceptance. The next useful test is to bind one actual joint to the approved detail and obtain a defensible scale or choose a categorical open/closed visual state with independent labels and an abstain rule.

Sources: [Trial 002 Drive root](https://drive.google.com/drive/folders/1pW086sQsOK0roatuznGfmIx2axo-KAXZ), [orientation photos](https://drive.google.com/drive/folders/11SDMsu1km8UQQ8f_TWUba3r2wwzzNXx0), [Day 01 manifest](https://docs.google.com/document/d/1ISK5c65BPrgIR7Ra-SWRYPcNCgK09Z_PQpTwvtY3u-c/edit). OpenCV values were computed in the local pinned wheel runtime. The JSONL companion records file-level hashes and Drive IDs; the exact probe script is preserved with the trial record.
