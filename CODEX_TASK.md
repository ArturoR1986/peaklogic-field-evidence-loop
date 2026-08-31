# CODEX_TASK - VEG-2026-0001

Implement and harden Build Increment 0 exactly as specified in `BUILD_PACKET.md`.

## Required work
1. Run the repo in a clean Python 3.13 environment with `opencv-contrib-python-headless==5.0.0.93`.
2. Fix any OpenCV 5 API compatibility issues.
3. Run `peaklogic-evidence doctor`; it must pass without an override.
4. Run all tests.
5. Generate the synthetic work-order fixture and run `scan-work-order` against it.
6. Add one deterministic end-to-end demo script that:
   - maps the anchor demo template,
   - receives an unusable capture -> RETAKE,
   - reaches `before_cover` with missing critical proof -> REMIND_CRITICAL_PROOF,
   - accepts critical proof,
   - reaches completion with all proof points -> PREPARE_REVIEW_PACKET.
7. Do not implement the learned classifier yet. Keep the interface explicit and unimplemented until representative labeled media exists.

## Return
- commands executed
- test results
- OpenCV version output
- files changed
- known failures/limitations
- next recommended Build Gate
