# 管线手册：从提示词到 video.mp4

所有路径以 `SKILL_DIR` = 本 skill 根目录（即 `mg-motion-styles/`）为准。
上游仓库的目录结构被原样保留在 `vendor/` 下，**这个布局不能改**——片内的
`/assets/...`、`/node_modules/...` 路径都相对 `vendor/` 解析。

```text
mg-motion-styles/
  SKILL.md
  references/            蒸馏层：风格卡、骨架、管线、新增风格
  scripts/               setup.sh / render.sh / fetch-fonts.sh
  vendor/                ← 上游仓库原样镜像（可直接运行）
    harness/render.mjs   ROOT = vendor/（由脚本位置决定）
    lib/audio/           mgaudio 配乐工具包 + 103 个 CC0 乐器采样
    assets/              共用纹理 / HDRI / 字体清单
    demos/<slug>/        16 支片的源码（index.html + audio.py + cues.json + 工具脚本）
    prompts/<slug>.md    16 份完整原始提示词
    package.json / requirements.txt / requirements-full.txt / rubric.md / template.md
```

## 1. 环境依赖

| 组件 | 用途 | 本机状态 |
|---|---|---|
| Node ≥ 20 | 渲染脚本与各片依赖 | ✅ v24.21.0 |
| Google Chrome | 无头逐帧截图 | ✅ /Applications/Google Chrome.app |
| ffmpeg | 合成视频 / 测量响度 | ✅ 7.1 |
| Python 3.11+ | 配乐与素材脚本 | ✅ 3.13 |
| Blender 5.x | 仅 04-3d-render 需要 | ❌ 未安装 |

非 macOS 或 Chrome 不在默认路径时，设 `MG_CHROME=/path/to/chrome`。
Linux/NVIDIA 用 `MG_GPU_ARGS` 覆盖 GPU 参数（脚本默认 darwin 走 ANGLE/Metal）。

## 2. 首次安装（一次即可）

```bash
bash "$SKILL_DIR/scripts/setup.sh"
```

等价于：

```bash
cd "$SKILL_DIR/vendor"
npm install                                     # d3 opentype.js puppeteer-core simplex-noise three topojson-client
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt                 # 配乐 + 质检所需的最小集合
bash ../scripts/fetch-fonts.sh                  # 抓取开源字体（否则画面会回落系统字体）
```

- `npm install` **必须在 `vendor/` 根目录执行**，否则片内的 `/node_modules/...` 会 404。
- `requirements.txt` 是做片必需的最小集合；生成素材用的额外库（pillow / opencv / rembg 等）
  在 `requirements-full.txt` 里，用 `bash scripts/setup.sh --full` 一并安装。
- 本机 `python3` 是 3.13：原钉的 `matplotlib==3.9.1` 没有 3.13 wheel，已放宽为 `>=3.9.2,<4`（仅用于画频谱图，不影响音频）。

## 3. 做一支片的标准流程

```bash
cd "$SKILL_DIR/vendor"
. .venv/bin/activate                            # 用 setup.sh 建的虚拟环境

WORK=demos/my-film                              # 新片放在 demos/ 下（保证相对路径成立）
cp -R demos/12-aurora-glass "$WORK"             # ① 拿最接近的参考实现当骨架
# ② 改 index.html / js：画面与动画；改 cues.json：节拍表

python3 "$WORK/audio.py"                        # ③ 配乐 → $WORK/out/audio.wav（+ 频谱 PNG）
node harness/render.mjs "$WORK"                 # ④ 渲染 → $WORK/out/video.mp4（自动拾取 out/audio.wav）
```

要点：

- 页面必须在设置 `window.__ready = true` 之前定义 `window.renderAt = async (t) => {...}`，
  且可选 `window.DEMO = {width, height, fps, duration}`。**每帧都是 t 的纯函数**：不能用实时时钟、
  不能用状态触发的 CSS transition、随机数必须带种子。
- `cues.json` 是画面与声音共用的唯一节拍表：先定 drop / outro / 各击打点，再让两边都读它。
- 先出静帧再出动画：`node harness/render.mjs "$WORK" --stills 0.5,2,4.25,8.5` → `out/stills/*.png`。
- 低分辨率快速预览：`--scale 0.5`；要运动模糊：`--mb 4 --shutter 0.5`。

### render.mjs 参数速查

```text
node harness/render.mjs <demoDir> [options]
  --out path.mp4      --audio path.wav（默认自动找 <demoDir>/out/audio.wav）   --noaudio
  --mb 4 --shutter .5 --workers 2        # 运动模糊采样 / 快门角 / 并行 worker（默认 1）
  --from 0 --to 10 --scale .5            # 只渲一段 / 低分辨率预览
  --w 1080 --h 1920 --fps 30 --duration 10
  --stills 0.5,2,4.25                     # 只出静帧，不合成视频
  --crf 14                                # x264 质量
  --page other.html --query k=v           # 换入口页 / 传 query
  --mkv out.mkv                           # 无损 ffv1（无音轨）
```

机器级并发上限由 `MG_RENDER_SLOTS`（默认 3）控制，渲染锁在 `/tmp/mg-render-slots`。

## 4. 配乐（mgaudio）

`vendor/lib/audio/README.md` 是完整 API 手册（务必读）。速记：

```python
import sys; sys.path.insert(0, 'lib/audio')     # 从 vendor/ 根目录
import mgaudio as mg
from mgaudio import recipes, sfx

m = recipes.synthwave(bpm=100, key='A', drop=4.80, outro=8.40)   # 配方按风格选
m.sfx(sfx.whoosh(0.8, 'sci', direction=1), at=3.90)              # at= 传视觉事件时刻
m.sfx(sfx.impact('cinematic'), at=4.80, gain=-2, verb=-10)
res = m.export('out/audio.wav', lufs=-14, tp=-1, spectrogram='out/audio_spec.png')
```

- **sync 语义**：`at=` 是*视觉事件时刻*，不是偏移量。whoosh 对齐掠过峰值；
  riser / reverse cymbal / charge / lock_on 对齐**终点**（击打点）。
- 导出后**一定去看频谱 PNG 和 warnings**，再听一遍。
- 配方选择：`synthwave` 10-synthwave、`darksynth` 22-hud、`chiptune` 20-pixel、`techno` 09-bauhaus、
  `pop` 01-flat-vector / 04-3d-render、`future_bass` 07-liquid / 08-morph、`lofi` 05-cel-boil / 06-collage、
  `ambient` 12-aurora-glass / 04-3d-render / 02-line-art、`explainer` 19-paperclip / 03-isometric、
  `variety` 18-hanazi、`ambient(flavor='piano')` 23-xiaopangxie。
- SFX 家族齐全：motion / tension-hits / UI / liquid / paper-desk / glitch / retro-media /
  sci-fi-HUD / magic / 8-bit / cartoon-综艺 / text。

### 音频 QC

```bash
python3 -m mgaudio out/audio.wav --png out/spec.png --hits 1.2,4.8
```

合格线：时长恰好 10.000 s、LUFS −14 ±0.6、TP ≤ −1 dBTP、无 DC / 削波 / 相位问题、
最静段 ≤ 0.6 s。`mg.analyze()` 返回 `warnings` 列表，逐条清掉。

## 5. 字体（重要缺口）

字体文件**不在上游仓库里**（授权各异、中文字体很大）。**缺字体不只是字形不同——片子在
`document.fonts.load()` 处会直接抛错，`window.__ready` 永不置位，渲染会挂 5 分钟后失败。**
所以这是必做步骤：`bash scripts/fetch-fonts.sh`。清单见 `vendor/assets/fonts/README.md`
（含每个字体应放的确切路径），`@font-face` 声明在 `vendor/assets/fonts/fonts.css`。
脚本已抓取 31 个 OFL 字体，并用 fontTools 从可变字体实例化 demo 自带的静态字体
（03 的 Unbounded-800、07 的 Fraunces-Liquid-72-900-Soft、08 的 Outfit-SemiBold），
10 的 MrDafoe 直接复制。**未覆盖**厂商自有授权的中文字体（阿里巴巴普惠体、阿里妈妈数黑体、
HarmonyOS Sans SC、抖音美好体）与资源圆体、缝合像素字体，需按需手动放置。

常用且开源可商用的：Inter、Poppins、Anton、Bebas Neue、DM Sans、Fredoka、JetBrains Mono、
IBM Plex Mono、Cormorant Garamond、Instrument Serif、Caveat、Chakra Petch、Michroma、
Luckiest Guy、Noto Sans SC、Noto Serif SC、LXGW Marker Gothic、Long Cang、Alibaba PuHuiTi、
HarmonyOS Sans SC、Alimama ShuHeiTi、Douyin Sans、Fusion Pixel 12。

新做片子时优先只依赖已就位/易获取的字体，并在 `CREDITS.md` 记录授权。需要时说一声，
可按清单把开源字体抓到对应路径。

## 6. Blender（仅 04-3d-render）

```bash
cd "$SKILL_DIR/vendor/demos/04-3d-render"
python3 blender/make_letters.py                     # 充气字母网格（*.ply 已附带）
python3 blender/sim.py                              # 物理模拟 → work/anim.npz + out/events.json
blender -b --factory-startup -P blender/scene.py    # 搭场景
blender -b work/scene.blend -P blender/render.py -- --range 0:239   # 240 帧 PNG 序列
python3 audio.py && cd ../.. && node harness/render.mjs demos/04-3d-render
```

本机未装 Blender；不想装就走 `Suggested technical route` 允许的替代路线
（HTML/Three.js 近似软体质感），并在报告里说明为什么换路线。

## 7. 交付与质检

```bash
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 out/video.mp4
ffmpeg -hide_banner -i out/video.mp4 -filter_complex ebur128=peak=true -f null -   # 看 I / peak
```

### 本机环境注意事项

- **`ffprobe` 可能是垫片**（作者机器上的情况，你的机器不一定）：没有原生 arm64 ffprobe，`~/.local/bin/ffprobe` 是只支持
  两种查询的 Python 垫片，`-show_streams`、`-of json` 等都会返回无效结果（`-version` 返回 `0`）。
  要查真实流信息请直接用真实 ffmpeg：
  `python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"` 找到的 ffmpeg，执行 `<ffmpeg> -i out/video.mp4`。
- **`harness/render.mjs` 有一处本地补丁**（见文件内 `[local patch]` 注释）：本机 ffmpeg 下
  `apad` 配 `-shortest` 不会截断音轨，容器会多出 ≈0.58 s 静音（实测 10.58 s）。
  补丁显式传入 `-t <目标时长>`，保证成品精确 10.000 s。视频本身一直是精确的 300 帧。

交付前逐条过：恰好 10.00 s、分辨率与帧率符合 `Output`、有音轨且 ≈ −14 LUFS、TP ≤ −1 dBTP、
无黑帧/无静止死段、视觉击打对齐音频起音、无回落字体或豆腐块、无边缘裁切、细线不闪、
渐变无 banding。然后按 `references/rubric.md` 找另一个会话独立评审一轮再改。
