# Representative Media Workspace

Keep raw/staged jobsite media outside Git history by default.

Suggested local layout:

```text
raw/photos/
raw/videos/
candidates/
manifests/
splits/
```

Use `scripts/extract_dataset_frames.py` to reduce a short walkthrough video to bounded, usable, non-redundant labeling candidates.

Only commit media when rights, privacy, and competition-sharing status are explicitly clear.
