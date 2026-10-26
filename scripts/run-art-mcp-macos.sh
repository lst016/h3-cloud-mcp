#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export AUTODL_ART_TOKEN="$(security find-generic-password -a "$(id -un)" -s h3-cloud-mcp-autodl-art -w)"
export H3_ART_ENABLE_PAID=1
export H3_ART_MAX_ESTIMATED_CNY="${H3_ART_MAX_ESTIMATED_CNY:-0.25}"
export H3_ART_MAX_TASKS_PER_SESSION="${H3_ART_MAX_TASKS_PER_SESSION:-1}"
export H3_OUTPUT_DIR="${H3_OUTPUT_DIR:-$project_dir/outputs}"

exec uv run --project "$project_dir" h3-cloud-mcp
