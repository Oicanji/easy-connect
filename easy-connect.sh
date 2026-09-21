#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"

if [[ -x "${ROOT}/dist/EasyConnect/EasyConnect" ]]; then
  exec "${ROOT}/dist/EasyConnect/EasyConnect" "$@"
fi

if [[ -x "${ROOT}/EasyConnect" ]]; then
  exec "${ROOT}/EasyConnect" "$@"
fi

if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  exec "${ROOT}/.venv/bin/python" -m easy_connect "$@"
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 -m easy_connect "$@"
fi

echo "Python 3 nao encontrado. Instale python3 ou crie .venv no projeto." >&2
exit 1
