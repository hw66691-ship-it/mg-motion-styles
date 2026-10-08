#!/usr/bin/env bash
# 自动补齐做片必需的系统组件：Node.js、Python 3、ffmpeg、Chrome。
# 已有的直接用；缺的下载官方/开源预编译包装到用户目录（~/.local），不需要管理员权限。
#   bin   → ~/.local/bin
#   程序  → ~/.local/share/mg-motion-styles/
# 可重复运行。支持 macOS（arm64 / x86_64）和 Linux（x86_64 / arm64）。
set -euo pipefail

BIN="$HOME/.local/bin"
SHARE="$HOME/.local/share/mg-motion-styles"
mkdir -p "$BIN" "$SHARE"
export PATH="$BIN:/opt/homebrew/bin:/usr/local/bin:$PATH"
export npm_config_update_notifier=false

OS="$(uname -s)"; ARCH="$(uname -m)"
case "$OS-$ARCH" in
  Darwin-arm64)  NODE_PLAT=darwin-arm64; UV_PLAT=aarch64-apple-darwin;     FF_WHEEL=macosx_11_0_arm64 ;;
  Darwin-x86_64) NODE_PLAT=darwin-x64;   UV_PLAT=x86_64-apple-darwin;      FF_WHEEL=macosx_10_9_intel.macosx_10_9_x86_64 ;;
  Linux-x86_64)  NODE_PLAT=linux-x64;    UV_PLAT=x86_64-unknown-linux-gnu; FF_WHEEL=manylinux2014_x86_64 ;;
  Linux-aarch64) NODE_PLAT=linux-arm64;  UV_PLAT=aarch64-unknown-linux-gnu; FF_WHEEL=manylinux2014_aarch64 ;;
  *) echo "不支持的系统：$OS-$ARCH，请手动安装 node / python3 / ffmpeg / Chrome" >&2; exit 1 ;;
esac

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fetch() { curl -fsSL --retry 3 -o "$2" "$1"; }

# macOS 上 /usr/bin/python3 可能只是「安装开发者工具」的占位程序，要实际跑一下才算有
have_python() { command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; assert sys.version_info >= (3, 11)' >/dev/null 2>&1; }

# ---------- Node.js ----------
if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
  echo "  ok   node $(node --version)"
else
  echo "==> 下载 Node.js 22 LTS"
  VER="$(curl -fsSL https://nodejs.org/dist/latest-v22.x/SHASUMS256.txt | sed -n "s/.*node-\(v[0-9.]*\)-$NODE_PLAT\.tar\.gz$/\1/p" | head -1)"
  [ -n "$VER" ] || { echo "获取 Node 版本失败" >&2; exit 1; }
  fetch "https://nodejs.org/dist/latest-v22.x/node-$VER-$NODE_PLAT.tar.gz" "$TMP/node.tgz"
  rm -rf "$SHARE/node"; mkdir -p "$SHARE/node"
  tar -xzf "$TMP/node.tgz" -C "$SHARE/node" --strip-components=1
  for b in node npm npx; do ln -sf "$SHARE/node/bin/$b" "$BIN/$b"; done
  hash -r
  echo "  ok   node $(node --version)（装在 $SHARE/node）"
fi

# ---------- Python 3 ----------
if have_python; then
  echo "  ok   python3 $(python3 --version 2>&1)"
else
  echo "==> 下载 Python 3.12（通过 uv 的独立 Python 构建）"
  if ! command -v uv >/dev/null 2>&1; then
    fetch "https://github.com/astral-sh/uv/releases/latest/download/uv-$UV_PLAT.tar.gz" "$TMP/uv.tgz"
    tar -xzf "$TMP/uv.tgz" -C "$TMP"
    cp "$TMP/uv-$UV_PLAT/uv" "$BIN/uv"; chmod +x "$BIN/uv"
  fi
  UV_PYTHON_INSTALL_DIR="$SHARE/python" uv python install 3.12
  PY="$(UV_PYTHON_INSTALL_DIR="$SHARE/python" uv python find 3.12)"
  ln -sf "$PY" "$BIN/python3"
  hash -r
  echo "  ok   python3 $(python3 --version 2>&1)（装在 $SHARE/python）"
fi

# ---------- ffmpeg ----------
if command -v ffmpeg >/dev/null 2>&1; then
  echo "  ok   ffmpeg $(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')"
else
  echo "==> 下载 ffmpeg（imageio-ffmpeg 提供的静态构建）"
  URL="$(curl -fsSL https://pypi.org/pypi/imageio-ffmpeg/json \
    | python3 -c "import sys,json; print(next(u['url'] for u in json.load(sys.stdin)['urls'] if '$FF_WHEEL' in u['filename']))")"
  fetch "$URL" "$TMP/ff.whl"
  mkdir -p "$TMP/ff" && unzip -q "$TMP/ff.whl" -d "$TMP/ff"
  FF="$(find "$TMP/ff/imageio_ffmpeg/binaries" -name 'ffmpeg-*' -type f | head -1)"
  [ -n "$FF" ] || { echo "ffmpeg 解包失败" >&2; exit 1; }
  cp "$FF" "$BIN/ffmpeg"; chmod +x "$BIN/ffmpeg"
  hash -r
  [ "$OS" = Darwin ] && xattr -d com.apple.quarantine "$BIN/ffmpeg" 2>/dev/null || true
  echo "  ok   ffmpeg（装在 $BIN/ffmpeg；此构建不含 ffprobe，管线用 ffmpeg -i 取时长）"
fi

# ---------- Chrome ----------
SYS_CHROME="${MG_SYS_CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ -n "${MG_CHROME:-}" ] && [ -x "$MG_CHROME" ]; then
  echo "  ok   Chrome（MG_CHROME=$MG_CHROME）"
elif [ -x "$SYS_CHROME" ]; then
  echo "  ok   Chrome（$SYS_CHROME）"
elif [ -f "$SHARE/chrome-path" ] && [ -x "$(cat "$SHARE/chrome-path")" ]; then
  echo "  ok   Chrome（$(cat "$SHARE/chrome-path")）"
elif command -v google-chrome >/dev/null 2>&1; then
  command -v google-chrome > "$SHARE/chrome-path"
  echo "  ok   Chrome（$(cat "$SHARE/chrome-path")）"
else
  echo "==> 下载 Chrome for Testing（无头渲染用，约 150 MB）"
  OUT="$(cd "$TMP" && npx -y @puppeteer/browsers@2 install chrome@stable --path "$SHARE/chrome" | tail -1)"
  CH="${OUT#* }"
  [ -x "$CH" ] || { echo "Chrome 安装失败：$OUT" >&2; exit 1; }
  echo "$CH" > "$SHARE/chrome-path"
  echo "  ok   Chrome（$CH）"
fi

if ! command -v blender >/dev/null 2>&1; then
  echo "  提示 未装 Blender：只有 04-3d-render 风格需要，其它风格不受影响"
fi
