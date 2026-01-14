#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

docker_bin=$(command -v docker || true)
docker_mount_args=()
if [ -n "$docker_bin" ]; then
  docker_mount_args=(-v "$docker_bin":/usr/bin/docker:ro)
fi

docker build -f "$repo_root/docker/ci_linux.Dockerfile" -t ghlang-ci-linux "$repo_root"
docker run --rm -v "$repo_root":/repo -v /var/run/docker.sock:/var/run/docker.sock "${docker_mount_args[@]}" ghlang-ci-linux

docker build -f "$repo_root/docker/ci_aur.Dockerfile" -t ghlang-ci-aur "$repo_root"
docker run --rm -v "$repo_root":/repo ghlang-ci-aur
