---
name: mg-motion-styles
description: 用代码制作 MG 动态设计短片（默认 10 秒样片；工作台任务可任意时长、带本地 TTS 旁白与字幕、横竖屏可选），内置 16 种风格的完整规范、逐字提示词、可运行参考源码、配乐工具包与无头渲染管线（扁平矢量、一笔画线条、等轴 2.5D、3D 渲染、逐帧手绘、拼贴、液态、形变、包豪斯、Synthwave/VHS、弥散渐变玻璃拟态、像素风、综艺花字、回形针贴纸科普、赛博 HUD、小螃蟹手绘抒情 MV）。当用户要求做 MG 动画 / 动态设计 / 动效短片 / 动态海报 / 片头包装 / logo 演绎 / 品牌 ident / 知识科普动画 / 带旁白的解说视频，或指定用上面某一种风格做视频，或让你执行 mg-jobs/<id>/brief.md 时使用。也用于把新风格蒸馏进这个 skill。不用于剪辑已有实拍素材、给现有视频加字幕或做纯实拍剪辑。
---

# MG 动态设计短片制作（16 种风格）

把「一句需求」变成一支 10 秒、`video.mp4` 交付的 MG 动画：画面、动画、配乐、音效全部由代码生成。
本 skill 蒸馏自开源项目 **mg-styles-15**，15 种风格的完整规范与可运行实现都在 `vendor/`，可离线复现。

## 何时用 / 不用

- **用**：做 MG 动画、动态设计短片、动态海报、片头/logo 包装、品牌 ident、科普解说动画；
  用户点名某种风格（如「做一支包豪斯风格的」「要赛博朋克 HUD 那种」）。
- **不用**：剪辑已有实拍素材、给现有视频加字幕/配音、纯实拍 vlog 剪辑。

## 先读什么

| 你要做的事 | 读 |
|---|---|
| 执行工作台发来的任务 | 先读该任务的 `mg-jobs/<id>/brief.md`，再读 `references/narrated-production.md`（覆盖默认硬规格） |
| 打开工作台 | 双击项目根目录的「启动MG视频工作台.command」（或 `bash workbench/start.sh`）：选风格 → 写想法和时长 → 选音色（试听 / 微调 / 造音色 / 克隆）→ 生成 |
| 挑风格（文本） | `references/styles/INDEX.md`（16 种）|
| 看某个风格的全部细节 | `references/styles/<slug>.md` |
| 组装/改写提示词 | `references/universal-skeleton.md`（通用段逐字复制） |
| 跑通环境、渲染、配乐、QC | `references/pipeline.md` |
| 新增第 16 种风格 | `references/add-style.md` + `references/template.md` |
| 找 AI 独立评审再改一轮 | `references/rubric.md` |
| 要原始素材 | `vendor/prompts/<slug>.md`（逐字提示词）、`vendor/demos/<slug>/`（源码）、`vendor/lib/audio/README.md`（音频 API 全手册） |

## 标准流程

1. **选风格**。按需求在 `references/styles/INDEX.md` 里挑；用户没指定就给 2–3 个候选并说明差异，
   让用户拍板，不要闷头开工。默认横屏 1920×1080·30fps·10.000s。
2. **对齐内容**。明确这四件事：主题/文案、品牌名（必须虚构）、配色、落版（logo + tagline）。
   用户没给就按该风格的 Creative seed 先出方向，别用默认模板糊弄。
3. **组装提示词**：`references/universal-skeleton.md` 的通用段逐字复制 +
   选定的 `Style / Output / Suggested technical route / Creative seed / Signature features`。
   `Signature features` **绝不删改**——它决定这支片还能不能被一眼认出。
4. **搭工程**。在 `vendor/demos/` 下建 `<slug>` 工程，最省力的做法是复制最接近的现有 demo 当骨架
   （它已经满足 `renderAt(t)` 契约、cues.json 结构、audio.py 的路径写法）。
5. **先静帧后动画**。`--stills 0.5,2,4.25,8.5` 出关键帧，逐张看构图/字距/负空间，改到没有
   「默认感、AI 模板感」再写运动。**不允许**跳过这一步直接渲染整片。
6. **配乐与渲染**。先 `python3 audio.py`（看频谱 PNG、清掉 warnings），再
   `node harness/render.mjs <demoDir>`（自动拾取 `out/audio.wav`）。低分辨率预览用 `--scale 0.5`。
7. **质检 + 迭代**。过 `references/pipeline.md` 第 7 节的清单，然后按 `references/rubric.md`
   找另一个会话独立评审，把评审意见贴回来改一轮。原片都是「制作 → 评审 → 修改」跑了两轮。
8. **交付**。`video.mp4` + 简短报告：两句话概念、带时码的节拍表、每个 Signature feature 如何落地、
   技术路线、核对数值（时长/分辨率/帧率/响度/TP）、自己诚实的三条弱点。

## 铁律

- **确定性渲染**：每一帧是时间 t 的纯函数。随机数带种子，物理/粒子预计算或闭式解，
  不用实时时钟，不用状态触发的 CSS transition，否则逐帧渲染会漂移。
- **素材合法**：只用 CC0 / 公有领域 / OFL / Apache / 可商用免费素材，逐个在 `CREDITS.md` 记录来源与授权；
  品牌名一律虚构，不用真实商标。
- **中文上屏文案**要地道、标点规范（全角、直角引号一致），不允许错别字与机翻腔。
- **只让一种风格做主导**。可以混（如 aurora 底 + 玻璃 UI），但以主导风格的 Signature features 为准，
  否则会退化成素材堆砌。
- **竖屏不是裁切**：改尺寸要重排构图、标题与安全边距。
- 硬规格默认：1920×1080、30 fps、恰好 10.000 s、H.264 MP4 + 立体声 AAC 48 kHz、
  −14 LUFS integrated、true peak ≤ −1 dBTP、成品名 `video.mp4`（04/05 用 24fps，18 用 1080×1920）。

## 环境

Node + Chrome + ffmpeg 必需（本机已具备）；Blender 仅 04-3d-render 需要（本机未装）。
首次运行 `bash scripts/setup.sh` 安装依赖，细节与命令见 `references/pipeline.md`。
辅助脚本：`scripts/setup.sh`（装 Node 依赖 + Python 环境，`--full` 装生成素材的全套）、
`scripts/fetch-fonts.sh`（必做，抓开源字体）、`scripts/render.sh`（配乐 + 渲染一条命令）。

## 目录

```text
SKILL.md                 本文件
workbench/               MG 视频工作台（本地服务，仅 127.0.0.1）
  start.sh               启动（复用 ~/local-video-dubbing 的语音环境与模型）
  server.py voicecore.py 服务端：风格、音色库、试听、造音色、克隆、旁白合成、任务
  mgw                    制作期命令行：narrate / assemble / mix / status
  brief_template.md      任务说明模板（生成到 mg-jobs/<id>/brief.md）
  index.html styles.json 前端页面与 16 套风格数据
  voice-catalog.json     音色目录：6 类 48 个可造音色（描述 + 中英试听句）
  covers/                16 张风格封面（6 张为参考实现真实帧，10 张为 AI 生成）
references/              蒸馏层
  styles/INDEX.md        15 种风格速查 + 按需求挑
  styles/<slug>.md       每种风格一张蒸馏卡（15 张）
  styles.json            机器可读版本
  universal-skeleton.md  通用提示词骨架（逐字）
  pipeline.md            环境 / 渲染 / 配乐 / QC 手册
  narrated-production.md 旁白长片（任意时长、字幕、竖屏）的规则与工具
  add-style.md           新增风格的工作流
  rubric.md template.md  评审提示词 / 新风格模板
scripts/                 setup.sh / render.sh
vendor/                  上游仓库原样镜像（harness / lib / assets / demos / prompts）
CREDITS.md               来源与授权说明
```

## 工作台任务

工作台生成的任务放在项目根目录 `mg-jobs/<id>/`。有中转站 Key 时，工作台会在后台调起 Claude Code 自动执行；没有 Key 时，会把开工指令复制给用户，由用户粘贴到 BigApple。
两种方式都按 `brief.md` 一路做到 `final.mp4`，**不中途提问**。旁白一律用 `workbench/mgw` 在本地合成，不调用任何云端 TTS。

## 音色库

工作台的音色分 6 类（女声精选 / 男声精选 / 卡通搞怪 / 旁白解说 / 方言口音 / 外语音色）+「我的音色」。
`workbench/voice-catalog.json` 是音色目录：每条给出名字、分类、中文音色描述（VoiceDesign 提示词）和中英试听句。

- 首次使用跑一次构建：`POST /api/build/start`（或页面里的进度条）。它会用 1.7B VoiceDesign
  把目录里还没有的音色逐个造出来存进 `~/local-video-dubbing/voices/`，再预生成试听音频，
  这样点 🔈 是 0 延迟播放；未预生成的音色现场合成要 10 秒以上。
- 切换「旁白语言」时前端会自动为该语言预热全部音色（后台跑，进度条可见）。
- 想加音色：往 `voice-catalog.json` 加一条（`id` 必须等于 `name`），再调一次 `/api/build/start`；
  也可以直接在页面上「＋ 用文字描述造音色」，造出来的落在「我的音色」类。
- 试听句按 10 字左右写，要能听出音色差别；中英各一句，其它语言用通用句。

### 在 BigApple HTML 预览里用（走 /ba/v1，不需要 Key）

同一个 `workbench/index.html` 有两种跑法，页面启动时访问 `/ba/v1/health` 自己判断：

- **本地模式**（由 127.0.0.1 的服务打开）：数据来自 Python 服务，出片走本机 Claude Code
  或「复制开工指令交给 BigApple 粘贴」。
- **预览模式**（在 BigApple HTML 预览里打开）：`/ba/v1` 可用，音色表与试听改用同目录的
  静态 `voices.json` + `previews/`；点「生成视频」会建一个 BigApple Agent 会话，把任务规格
  （风格 / 想法 / 时长 / 画幅 / 语言 / 字幕 / 音色及其参数）作为 kickoff 发过去，
  由 Agent 在项目里跑 `mgw narrate` → 画面 → `mgw mix`，成片写回 `mg-jobs/<id>/final.mp4`，
  页面直接播放。预览模式不需要中转站 Key，也不用手动粘贴。
- 预览模式也能造音色 / 克隆音色：页面把音频上传给 Agent，Agent 用本机模型跑
  `mgw voice-design` / `mgw voice-clone`，命令会自动刷新静态音色表，页面随后重新读取即可看到新音色。

### 造音色 / 克隆音色

`mgw voice-design` 和 `mgw voice-clone` 是给 Agent 调的命令，做完会自动生成中英试听、
并刷新预览用的静态音色表（`voices.json` + `previews/`）：

```bash
bash .claude/skills/mg-motion-styles/workbench/mgw voice-design \
  --name 御姐 --prompt "成熟自信的年轻女性，中低音区，语速从容" --category female
bash .claude/skills/mg-motion-styles/workbench/mgw voice-clone ref.wav --name 我的声音
```

- **克隆别填 `--text`**：留空走"只提取音色特征"，稳定且快（实测 7 秒参考音频约 20 秒出结果）。
  一旦 `--text` 和音频里念的内容对不上，模型会一直生成不自停，把语音引擎卡死。
- 引擎真卡住了（工作台顶部会显示「语音引擎卡住…点这里重启」），点它走
  `POST /api/engine/reset`，服务会重开进程清掉卡住的那次合成。
- 参考音频 3–30 秒，5–15 秒单人干净人声最好。

## 已知缺口

- **字体不在仓库里，且缺失会导致渲染直接失败**（`document.fonts.load()` 抛错 → `__ready` 不置位）。
  先跑 `bash scripts/fetch-fonts.sh`；厂商授权的中文字体需手动放置，清单见
  `vendor/assets/fonts/README.md`。新做片子优先选已就位的开源可商用字体。
- **成片视频未镜像**（上游 `videos/` 共 441 MB）：需要参考成片就去
  https://vincentwei1021.github.io/mg-styles-15/ 在线看。
- **Blender 未安装**：04 风格需自行安装，或改用允许的替代路线并在报告中说明。
- **`ffprobe` 是本机垫片**，只支持两种查询；核对流信息请用真实 ffmpeg（路径见
  `references/pipeline.md`）。
- **`vendor/harness/render.mjs` 含一处本地补丁**（`-t` 保证精确 10.000 s），
  上游该脚本在本机 ffmpeg 下会输出 10.58 s 容器。改动已用 `[local patch]` 注释标出。
