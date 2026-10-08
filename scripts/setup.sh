#!/usr/bin/env bash
# 安装 mg-motion-styles 的依赖（Node 包 + Python 虚拟环境）。
# 可重复运行；已就绪的部分会跳过。
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="$SKILL_DIR/vendor"

echo "SKILL_DIR = $SKILL_DIR"

missing=0
for cmd in node npm python3 ffmpeg; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  ok   $cmd  $($cmd --version 2>&1 | head -1)"
  else
    echo "  MISS $cmd  → 请先安装" >&2
    missing=1
  fi
done
if [ ! -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ] && [ -z "${MG_CHROME:-}" ]; then
  echo "  warn 未找到 Google Chrome；设 MG_CHROME=/path/to/chrome 指定" >&2
fi
command -v blender >/dev/null 2>&1 || echo "  warn 未找到 Blender（仅 04-3d-render 需要）"
[ "$missing" -eq 0 ] || { echo "缺少必需组件，已中止。" >&2; exit 1; }

echo "==> npm install（在 vendor/ 根目录，片内 /node_modules 路径依赖它）"
cd "$VENDOR"
npm install --no-fund --no-audit

echo "==> Python 虚拟环境 + 依赖"
if [ ! -d "$VENDOR/.venv" ]; then
  python3 -m venv "$VENDOR/.venv"
fi
# shellcheck disable=SC1091
. "$VENDOR/.venv/bin/activate"
python -m pip install --upgrade pip >/dev/null
if [ "${1:-}" = "--full" ]; then
  echo "    安装完整依赖（含 rembg/opencv 等生成素材用的库，体积大、耗时长）"
  pip install -r "$VENDOR/requirements-full.txt"
else
  echo "    安装做片必需依赖（配乐 + 质检）；生成素材用的额外库请用 --full"
  pip install -r "$VENDOR/requirements.txt"
fi

echo "==> 字体（上游仓库不含字体文件；缺字体画面会回落系统字体）"
bash "$SKILL_DIR/scripts/fetch-fonts.sh" || echo "  warn 字体抓取未全部成功，见上方清单"

echo
echo "完成。用法："
echo "  cd \"$VENDOR\" && . .venv/bin/activate"
echo "  python3 demos/<slug>/audio.py"
echo "  node harness/render.mjs demos/<slug>"
