#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
command -v python3 >/dev/null 2>&1 || { echo '需要 Python 3，请先安装。' >&2; exit 1; }
exec python3 "$project_dir/scripts/vim_env.py" stop
