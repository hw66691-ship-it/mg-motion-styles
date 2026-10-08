#!/usr/bin/env bash
# 从 GitHub 下载完整版 mg-motion-styles，覆盖安装到本 skill 目录，然后安装依赖。
# 可重复运行；已是完整版时只重跑 setup。
set -euo pipefail

REPO="hw66691-ship-it/mg-motion-styles"
ZIP_URL="https://github.com/$REPO/archive/refs/heads/main.zip"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "安装目录：$SKILL_DIR"

if [ ! -d "$SKILL_DIR/vendor" ] || [ ! -d "$SKILL_DIR/references" ]; then
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT

  echo "==> 下载 $ZIP_URL"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 3 -o "$TMP/skill.zip" "$ZIP_URL"
  else
    wget -O "$TMP/skill.zip" "$ZIP_URL"
  fi

  echo "==> 解压"
  unzip -q "$TMP/skill.zip" -d "$TMP"
  SRC="$TMP/mg-motion-styles-main"
  [ -f "$SRC/SKILL.md" ] || { echo "下载内容不完整：找不到 SKILL.md" >&2; exit 1; }

  echo "==> 覆盖到 skill 目录"
  cp -R "$SRC/." "$SKILL_DIR/"
else
  echo "已是完整版，跳过下载。"
fi

echo "==> 安装依赖"
bash "$SKILL_DIR/scripts/setup.sh" "$@"

echo "完成。请重新读取 $SKILL_DIR/SKILL.md 开始使用。"
