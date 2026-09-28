# Trial 002 — BMW Thoma / 20266878 — Day 01 intake and evidence baseline

Date of analysis: 2026-09-28. Status: **Day 01 intake closed; technical and human review open.**

## Job binding and source

Parent job: Trial 002, BMW Thoma, project 20266878, Untere Ziel 3, 79350 Sexau. The photographed Peter Gerber `Arbeitsvorbereitung` sheet prints an execution date of 03.09.2026; this is a planned/execution field on the document, not proof of the image capture date. The Drive intake was populated on 2026-09-26. Do not merge these media with Trial 001.

Three orientation photographs are in `00_Work_Order_and_Orientation`: `1000052052.jpg` (work preparation), `1000052053.jpg` (annotated aerial plan), and `1000052054.jpg` (annotated details). The work preparation lists four tasks:

1. Seal the workshop gutter and add 2 cm PU, turning up at sheet metal; first check whether water traces are present.
2. Check the joints in the composite-sheet ridge over the workshop.
3. Seal the sheet-metal ridge joints on the trapezoidal-sheet roof over the sales room with FLK.
4. Seal connections behind the entrance roof with FLK.

The annotated detail page marks three locations/classes: 2 cm PU and FLK fleece, a ridge joint with FLK, and connections with FLK. The aerial markings give broad context, not surveyed coordinates or definitive component counts. The materials list includes four buckets of FLK Bauder, two rolls of 26 cm fleece, FLK accessories, sandpaper, 8 m² of 20 mm PU, two canisters of solvent, and one sack of rags. Exact product identity, approved detail and quantities actually installed remain unverified.

## Preserved media and machine pass

- `01_Raw_Photos/Day_01`: 42 JPEG file entries (`1000052055.jpg` to `1000052098.jpg` with gaps and `1000052084b.jpg`). All 42 decode under OpenCV 5.0.0; dimensions are 1152×1536 or 1536×1152.
- SHA-256 identifies `1000052084.jpg` and `1000052084b.jpg` as an exact duplicate pair. Preserve both raw files but count one unique image for evaluation: 41 unique photo byte streams.
- Laplacian variance flags `1000052061.jpg` (27.26) and `1000052060.jpg` (38.47) as the lowest-texture/softness candidates. Direct inspection shows `2061` has a soft close-up of a wall/gutter interface and cannot reliably establish a fine detail. `2060` is dominated by a smooth surface and its low score alone is not a blur verdict. These are triage measurements, not calibrated pass/fail thresholds.
- `02_Raw_Videos/Day_01/1000052062.mp4`: 73,450,462 bytes, SHA-256 `82743ec140f15122618e09f979c68f14e085b5f537b96274a9d0c496af115f29`, 850 frames at about 30 fps, approximately 28.33 seconds. Eight frames at 0, 4, 8, 12, 16, 20, 24 and 27 seconds decoded under OpenCV 5.0.0. The clip shows a close inspection of a wet-looking surface and interface with a gloved hand. Full-frame semantic/video continuity evaluation has not been performed.

The raw files and Day 01 manifest are in the separate Trial 002 Drive folder. File gaps in a camera sequence are not proof that media is missing; the manifest says no further Day 01 media is expected.

## Provisional evidence state by work-order item

| Work-order item | Day 01 observation | Evidence state and action |
| --- | --- | --- |
| Workshop gutter, water-trace check, PU and FLK turn-up | Multiple gutter/interface views, wet-looking surfaces and local dark patches are visible. Video samples inspect a surface closely. | **Observed context; completion unresolved.** Bind each view to the specific workshop zone; distinguish water appearance from a documented leak test or dryness measurement. Verify before/after, PU placement and FLK detail against approved documents and human records. |
| Workshop composite-sheet ridge joints | Broad sheet roof and several joint/interface views appear in the set. | **Partially observed; check outcome unresolved.** The photos alone do not establish each expected joint or the result of an inspection. |
| Sales-room trapezoidal-sheet ridge FLK | Several photos show dark local patches near sheet-metal edges/ridges. | **Application-like appearance; specification and completion unresolved.** Bind patch locations to the sales-room roof before counting them against the order; no adhesion, preparation or watertightness conclusion. |
| Connections behind entrance roof | Wall-base and narrow run views show connection context; some close-ups are soft. | **Observed context; final closure unresolved.** Associate before/after views to the annotated entrance-roof location; do not use `2061` alone as fine-detail proof. |

The scene grouping above is a visual orientation, not a per-image verified map. The approved work order is the task authority; appearance alone does not establish material identity or completed quantities.

## Concrete failure and next bounded execution

The duplicate alias `2084b` would inflate a naive evidence count; exact-hash deduplication prevents that. The soft `2061` close-up is a second evidence-readiness failure for fine detail. Neither should advance a completion state.

Next run: assign all 41 unique photos and the video to day/zone/component with traceable IDs; resolve the expected component map from the work order and marked plan; compare before/after coverage for the four tasks; then perform one bounded geometry or visual-state check under the pinned competition runtime with an abstain case. Keep any missed before-cover proof as a gap. A qualified human must review workmanship, safety, manufacturer and acceptance conclusions before external use.

## Source locations and limits

- [Trial 002 Drive root](https://drive.google.com/drive/folders/1pW086sQsOK0roatuznGfmIx2axo-KAXZ)
- [Day 01 manifest](https://docs.google.com/document/d/1ISK5c65BPrgIR7Ra-SWRYPcNCgK09Z_PQpTwvtY3u-c/edit)
- [Orientation images](https://drive.google.com/drive/folders/11SDMsu1km8UQQ8f_TWUba3r2wwzzNXx0)
- [Day 01 photos](https://drive.google.com/drive/folders/1yhmj_eo0q0kIgOhFl90ZSlIb_O7sDzNg)
- [Day 01 video](https://drive.google.com/file/d/1L2YlLrmXZSItlggfb-i5i6jah9XzbA_N/view)

This is an intake and representative visual review, not a complete per-component OpenCV decision trace or professional closeout.
