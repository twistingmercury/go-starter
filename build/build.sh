#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-${PROJ_ROOT}/dist}"

BUILD_VER="${BUILD_VER:-$(git -C "${PROJ_ROOT}" describe --tags --abbrev=0 2>/dev/null || echo '0.0.0.dev0')}"

build() {
  printf "\n=== exporting binaries ===\n"
  docker build --rm --no-cache --pull \
    --file "${SCRIPT_DIR}/Dockerfile" \
    --build-arg BUILD_VER="${BUILD_VER}" \
    --target export \
    --output "type=local,dest=${OUTPUT_DIR}" \
    --tag "go-starter:${BUILD_VER}" \
    "${PROJ_ROOT}"

  printf "\nBinaries exported to: %s\n" "${OUTPUT_DIR}"
}

main() {
  build
}

main "$@"
