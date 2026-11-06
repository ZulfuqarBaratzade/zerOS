#!/bin/bash
# REVIEW ONLY. Do not execute before the user's explicit elevated-smoke approval.
set -euo pipefail
REVIEW_DIR=/tmp/zeros-smoke-review-zt1_720a
SOURCE="$REVIEW_DIR/source"
IMAGE=sha256:d1bab47128ad1679d1ed00f032c4dedc0517b506913dd823f3b4eb3d689c0789
COMMIT=e83d8f1c9b37aa07e5eb246092add31e5ace4d44
test "$(git -C "$SOURCE" rev-parse HEAD)" = "$COMMIT"
test -z "$(git -C "$SOURCE" status --porcelain --untracked-files=all --ignored)"
# No --rm: preserve the stopped container for inspection. Name conflict => stop.
docker --context default run --name zeros-mount-smoke-e83d8f1 \
  --user 0:0 --read-only --network none --cgroupns private \
  --cap-drop ALL --cap-add SYS_ADMIN --cap-add SYS_CHROOT \
  --security-opt no-new-privileges --security-opt apparmor=docker-default \
  --pids-limit 128 --memory 512m \
  --tmpfs /tmp:rw,nosuid,nodev,noexec,size=64m \
  --tmpfs /scratch:rw,nosuid,nodev,noexec,size=16m \
  --mount "type=bind,src=$SOURCE,dst=/src,readonly,bind-propagation=rprivate" \
  --entrypoint /bin/sh "$IMAGE" -ec '
    bash /src/scripts/build.sh --check-environment
    mkdir /scratch/probe
    mounted=no
    cleanup() { if [ "$mounted" = yes ]; then umount /scratch/probe; fi; }
    trap cleanup EXIT
    mount -t tmpfs -o size=1m,nosuid,nodev,noexec zeros-smoke /scratch/probe
    mounted=yes
    printf "tmpfs-ok\n" > /scratch/probe/proof
    test "$(cat /scratch/probe/proof)" = tmpfs-ok
    chroot / /usr/bin/true
    umount /scratch/probe
    mounted=no
    printf "SMOKE_PASS: tmpfs mount/read/write/umount + chroot\n"
  ' 2>&1 | tee "$REVIEW_DIR/smoke.log"
