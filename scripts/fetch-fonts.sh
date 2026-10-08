#!/usr/bin/env bash
# 按 vendor/assets/fonts/README.md 的清单抓取开源字体到对应路径。
# 只抓 OFL / 免费商用字体；已存在的文件跳过。缺字体时页面会回落系统字体，字形与成片不一致。
# 用法: bash scripts/fetch-fonts.sh [--dry-run]
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SKILL_DIR/vendor"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1

GF="https://raw.githubusercontent.com/google/fonts/main"
ok=0; skip=0; fail=0
failed_list=""

# dest|url   （%5B = [ ，curl 用 -g 关闭 globbing）
FONTS=(
"latin/anton/Anton-Regular.ttf|$GF/ofl/anton/Anton-Regular.ttf"
"latin/archivo/Archivo-Italic-VF.ttf|$GF/ofl/archivo/Archivo-Italic%5Bwdth,wght%5D.ttf"
"latin/bebasneue/BebasNeue-Regular.ttf|$GF/ofl/bebasneue/BebasNeue-Regular.ttf"
"latin/caveat/Caveat-VF.ttf|$GF/ofl/caveat/Caveat%5Bwght%5D.ttf"
"latin/chakrapetch/ChakraPetch-SemiBold.ttf|$GF/ofl/chakrapetch/ChakraPetch-SemiBold.ttf"
"latin/cormorantgaramond/CormorantGaramond-VF.ttf|$GF/ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"
"latin/dmsans/DMSans-VF.ttf|$GF/ofl/dmsans/DMSans%5Bopsz,wght%5D.ttf"
"latin/fredoka/Fredoka-VF.ttf|$GF/ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf"
"latin/ibmplexmono/IBMPlexMono-Medium.ttf|$GF/ofl/ibmplexmono/IBMPlexMono-Medium.ttf"
"latin/ibmplexmono/IBMPlexMono-SemiBold.ttf|$GF/ofl/ibmplexmono/IBMPlexMono-SemiBold.ttf"
"latin/instrumentserif/InstrumentSerif-Regular.ttf|$GF/ofl/instrumentserif/InstrumentSerif-Regular.ttf"
"latin/instrumentserif/InstrumentSerif-Italic.ttf|$GF/ofl/instrumentserif/InstrumentSerif-Italic.ttf"
"latin/inter/Inter-VF.ttf|$GF/ofl/inter/Inter%5Bopsz,wght%5D.ttf"
"latin/jetbrainsmono/JetBrainsMono-VF.ttf|$GF/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"
"latin/luckiestguy/LuckiestGuy-Regular.ttf|$GF/apache/luckiestguy/LuckiestGuy-Regular.ttf"
"latin/michroma/Michroma-Regular.ttf|$GF/ofl/michroma/Michroma-Regular.ttf"
"latin/poppins/Poppins-Black.ttf|$GF/ofl/poppins/Poppins-Black.ttf"
"latin/poppins/Poppins-SemiBold.ttf|$GF/ofl/poppins/Poppins-SemiBold.ttf"
"latin/pressstart2p/PressStart2P-Regular.ttf|$GF/ofl/pressstart2p/PressStart2P-Regular.ttf"
"latin/rajdhani/Rajdhani-Bold.ttf|$GF/ofl/rajdhani/Rajdhani-Bold.ttf"
"latin/rajdhani/Rajdhani-SemiBold.ttf|$GF/ofl/rajdhani/Rajdhani-SemiBold.ttf"
"latin/sora/Sora-VF.ttf|$GF/ofl/sora/Sora%5Bwght%5D.ttf"
"latin/unbounded/Unbounded-VF.ttf|$GF/ofl/unbounded/Unbounded%5Bwght%5D.ttf"
"latin/vt323/VT323-Regular.ttf|$GF/ofl/vt323/VT323-Regular.ttf"
"latin/mrdafoe/MrDafoe-Regular.ttf|$GF/ofl/mrdafoe/MrDafoe-Regular.ttf"
"latin/outfit/Outfit-SemiBold.ttf|$GF/ofl/outfit/Outfit%5Bwght%5D.ttf"
"cjk/notosanssc/NotoSansSC-VF.ttf|$GF/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
"cjk/notoserifsc/NotoSerifSC-VF.ttf|$GF/ofl/notoserifsc/NotoSerifSC%5Bwght%5D.ttf"
"cjk/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf|$GF/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf"
"cjk/longcang/LongCang-Regular.ttf|$GF/ofl/longcang/LongCang-Regular.ttf"
"cjk/lxgwmarkergothic/LXGWMarkerGothic-Regular.ttf|$GF/ofl/lxgwmarkergothic/LXGWMarkerGothic-Regular.ttf"
)

echo "目标目录: $SKILL_DIR/vendor/assets/fonts"
for entry in "${FONTS[@]}"; do
  dest="assets/fonts/${entry%%|*}"; url="${entry#*|}"
  if [ -s "$dest" ]; then echo "  skip  $dest"; skip=$((skip+1)); continue; fi
  if [ "$DRY" -eq 1 ]; then echo "  dry   $dest  ←  $url"; continue; fi
  mkdir -p "$(dirname "$dest")"
  if curl -gsSL --max-time 900 -C - -o "$dest.part" "$url" && [ -s "$dest.part" ] && [ "$(stat -f%z "$dest.part")" -gt 20000 ]; then
    mv "$dest.part" "$dest"; echo "  ok    $dest  ($(du -h "$dest" | cut -f1))"; ok=$((ok+1))
  else
    : > "$dest.part" 2>/dev/null; mv "$dest.part" "$dest" 2>/dev/null || true
    echo "  FAIL  $dest  ←  $url"; fail=$((fail+1)); failed_list="$failed_list\n  $dest"
  fi
done

# ---- demo 自带字体：从已下载的可变字体实例化 / 复制 ----
if [ "$DRY" -eq 0 ]; then
  [ -f assets/fonts/latin/mrdafoe/MrDafoe-Regular.ttf ] && mkdir -p demos/10-synthwave/assets/fonts \
    && cp -n assets/fonts/latin/mrdafoe/MrDafoe-Regular.ttf demos/10-synthwave/assets/fonts/ 2>/dev/null || true
  PY=""
  [ -x .venv/bin/python ] && PY=.venv/bin/python || PY="$(command -v python3 || true)"
  if [ -n "$PY" ] && "$PY" -c "import fontTools" 2>/dev/null; then
    "$PY" - <<'PYEOF2'
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
jobs = [
    ("assets/fonts/latin/unbounded/Unbounded-VF.ttf", "demos/03-isometric/assets/fonts/Unbounded-800-static.ttf", {"wght": 800}),
    ("assets/fonts/latin/outfit/Outfit-SemiBold.ttf",  "demos/08-morph/assets/fonts/Outfit-SemiBold.ttf",     {"wght": 600}),
    ("assets/fonts/latin/fraunces/Fraunces-VF.ttf",    "demos/07-liquid/assets/Fraunces-Liquid-72-900-Soft.ttf", {"wght": 900, "SOFT": 72}),
]
for src, dst, loc in jobs:
    if not os.path.exists(src) or os.path.exists(dst):
        continue
    f = TTFont(src)
    axes = {a.axisTag: a.defaultValue for a in f["fvar"].axes} if "fvar" in f else {}
    full = {tag: loc.get(tag, dv) for tag, dv in axes.items()}
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    instancer.instantiateVariableFont(f, full, inplace=False).save(dst)
    print(f"  ok    {dst}")
PYEOF2
  else
    echo "  warn 未装 fonttools，跳过 demo 自带字体的实例化（pip install fonttools）"
  fi
fi

cat <<'NOTE'

以下中文字体为厂商自有授权（免费商用，但需从官方渠道获取），脚本不自动下载，请手动放到对应路径：
  cjk/alibabapuhuiti3/AlibabaPuHuiTi-3-{55-Regular,65-Medium,85-Bold,105-Heavy,115-Black}.ttf   阿里巴巴普惠体 3.0
  cjk/alimamashuheiti/AlimamaShuHeiTi-Bold.ttf                                                  阿里妈妈数黑体
  cjk/harmonyossanssc/HarmonyOS_Sans_SC_{Light,Regular,Medium,Bold,Black}.ttf                   HarmonyOS Sans SC
  cjk/douyinsans/DouyinSansBold.ttf                                                             抖音美好体
  cjk/resourcehanrounded/ResourceHanRoundedCN-{Bold,Heavy}.ttf                                  资源圆体（OFL，官网/GitHub Release）
  cjk/fusionpixel/fusion-pixel-12px-proportional-zh_hans.ttf                                    缝合像素字体（OFL，GitHub Release）
  其余 03/07/08/10 各 demo 目录下的字体见 vendor/assets/fonts/README.md
NOTE
echo
echo "结果: ok=$ok  skip=$skip  fail=$fail"
[ "$fail" -gt 0 ] && printf "失败清单:%b\n" "$failed_list"
exit 0
