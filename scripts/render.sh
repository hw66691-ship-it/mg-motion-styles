#!/usr/bin/env bash
# 一条命令出片：配乐 → 渲染。
#   bash scripts/render.sh demos/<slug> [render.mjs 的其它参数...]
# 例：bash scripts/render.sh demos/12-aurora-glass --scale 0.5
#     bash scripts/render.sh demos/12-aurora-glass --stills 0.5,2,4.25,8.5
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="$SKILL_DIR/vendor"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

if [ $# -lt 1 ]; then
  echo "用法: bash scripts/render.sh <demoDir> [render.mjs 参数...]" >&2
  echo "例如: bash scripts/render.sh demos/12-aurora-glass" >&2
  exit 2
fi

DEMO="$1"; shift
cd "$VENDOR"

# demoDir 支持相对 vendor/ 或相对当前目录的写法
if [ ! -d "$DEMO" ] && [ -d "$VENDOR/$DEMO" ]; then DEMO="$VENDOR/$DEMO"; fi
if [ ! -d "$DEMO" ]; then echo "找不到工程目录: $1" >&2; exit 2; fi

if [ -f "$VENDOR/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "$VENDOR/.venv/bin/activate"
else
  echo "提示: 未发现 .venv，先运行 bash scripts/setup.sh" >&2
fi

if [ -f "$DEMO/audio.py" ] && [ ! -f "$DEMO/out/audio.wav" ]; then
  echo "==> 配乐 $DEMO/audio.py"
  ( cd "$DEMO" && python3 audio.py )
elif [ -f "$DEMO/out/audio.wav" ]; then
  echo "==> 已有 $DEMO/out/audio.wav，跳过配乐（要先改配乐请删掉它）"
fi

echo "==> 渲染 $DEMO"
node harness/render.mjs "$DEMO" "$@"
