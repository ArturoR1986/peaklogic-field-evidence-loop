#!/usr/bin/env bash
# Execute only on an already-authorized host. NO AWS provisioning; NO exposed ports.
set -euo pipefail
umask 077
: "${IMAGE_ID:?Set an immutable local sha256 image ID from docker image inspect}"
: "${SOURCE_COMMIT:?Set the full tested Git commit}"
: "${DATA_DIR:?Set absolute directory on the authorized persistent EBS filesystem}"
: "${INPUT_DIR:?Set absolute directory holding the approved read-only image}"
: "${JOB_ID:?}"
: "${MEDIA_ID:?}"
: "${REQUIREMENT_ID:?}"
: "${IMAGE_NAME:?Basename only}"
: "${STATE_SHA256:?Main-reviewed current state hash}"
: "${RUN_NAME:?New simple basename for this execution}"
: "${INPUT_BASIS:?synthetic_control or preserved_field_input}"
[[ "$IMAGE_ID" =~ ^sha256:[0-9a-f]{64}$ ]] || { echo 'Use an immutable local image ID' >&2; exit 2; }
[[ "$SOURCE_COMMIT" =~ ^[0-9a-f]{40}$ ]] || exit 2
[[ "$STATE_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
[[ "$RUN_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]] || exit 2
[[ "$IMAGE_NAME" != */* && "$IMAGE_NAME" != '.' && "$IMAGE_NAME" != '..' ]] || exit 2
[[ "$DATA_DIR" = /* && "$INPUT_DIR" = /* ]] || exit 2
[[ "$INPUT_BASIS" = synthetic_control || "$INPUT_BASIS" = preserved_field_input ]] || exit 2
[[ -f "$DATA_DIR/job.sqlite3" && -f "$INPUT_DIR/$IMAGE_NAME" ]] || exit 2
[[ ! -e "$DATA_DIR/$RUN_NAME" ]] || { echo 'Run directory already exists' >&2; exit 2; }
args=(--rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges
      --user "$(id -u):$(id -g)" --memory 1g --cpus 1 --pids-limit 128
      --tmpfs /tmp:rw,nosuid,noexec,size=128m
      -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 -e OPENCV_IO_MAX_IMAGE_PIXELS=25000000
      --mount "type=bind,source=$DATA_DIR,target=/data"
      --mount "type=bind,source=$INPUT_DIR,target=/input,readonly")
# The application container receives no AWS credentials and has no network.
docker run "${args[@]}" "$IMAGE_ID" python -m peaklogic_field_evidence.f03_runner run \
  --db /data/job.sqlite3 --job-id "$JOB_ID" --media-id "$MEDIA_ID" \
  --requirement-id "$REQUIREMENT_ID" --image "/input/$IMAGE_NAME" \
  --source-commit "$SOURCE_COMMIT" --expected-state-sha256 "$STATE_SHA256" \
  --input-basis "$INPUT_BASIS" --output "/data/$RUN_NAME"
# A different container process reopens the DB from persistent host storage.
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --user "$(id -u):$(id -g)" --memory 1g --cpus 1 --pids-limit 128 \
  -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 \
  --mount "type=bind,source=$DATA_DIR,target=/data,readonly" \
  "$IMAGE_ID" python -m peaklogic_field_evidence.f03_runner verify \
  --db /data/job.sqlite3 --job-id "$JOB_ID" --receipt "/data/$RUN_NAME/receipt.json" \
  > "$DATA_DIR/$RUN_NAME/container-reopen.json"
