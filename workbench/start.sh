#!/bin/sh
# 启动 MG 视频工作台（风格 + 本地配音），仅监听 127.0.0.1。已在运行就直接打开浏览器。
HERE="$(cd "$(dirname "$0")" && pwd)"
LVD="${LVD_HOME:-$HOME/local-video-dubbing}"
PORT="${MGW_PORT:-7870}"
mkdir -p "$LVD/workbench" 2>/dev/null && printf '%s\n' "$HERE" > "$LVD/workbench/location"
if curl -s --max-time 2 "http://127.0.0.1:$PORT/api/health" | grep -q mg-workbench; then
  open "http://127.0.0.1:$PORT/"; exit 0
fi
if [ ! -x "$LVD/venv/bin/python" ]; then
  echo "找不到本地配音环境：$LVD/venv（先安装 local-video-dubbing）" >&2; exit 1
fi
export LVD_HOME="$LVD"
export PYTHONPATH="$LVD/app"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$LVD/tools/sox/bin:$PATH"
export PYTORCH_ENABLE_MPS_FALLBACK=1 TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
exec "$LVD/venv/bin/python" "$HERE/server.py" --port "$PORT" "$@"
