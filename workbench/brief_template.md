# 制作任务（来自 MG 视频工作台）

你是这支片子的导演、编剧和工程师。按下面步骤**一路做到成片**，中途不要停下来提问；拿不准的地方自己做合理决定，并在最后的报告里说明。

## 需求

| 项 | 值 |
|---|---|
| 风格 | **{{STYLE_NAME}}**（`{{STYLE_SLUG}}`） |
| 时长 | **{{DURATION_HUMAN}}（{{DURATION}} 秒，严格按这个时长出片）** |
| 画幅 | {{ASPECT}}（{{WIDTH}}×{{HEIGHT}}，30 fps） |
| 旁白语言 | {{LANG}} |
| 音色 | `{{VOICE}}`（设置都在 `request.json` 里，**不要改**） |
| 字幕 | {{SUBTITLES}} |

用户的想法（这是创意方向，不是台词。台词由你来写）：

> {{IDEA}}

- 任务目录：`{{JOB_DIR}}`（下面写的相对路径都相对这个目录）
- Skill 目录：`{{SKILL_DIR}}`
- 制作命令行：`{{WORKBENCH}}/mgw`

## 进度汇报

每进入一个阶段先跑一次下面的命令，工作台进度面板会显示：

```bash
"{{WORKBENCH}}/mgw" status "{{JOB_DIR}}" <阶段> "<一句话说明>"
```

阶段依次是 plan、script、voice、storyboard、build、music、render、verify、done。

## 步骤

### 1. plan：读规范

读这几份文件：
- `{{SKILL_DIR}}/SKILL.md`
- `references/styles/{{STYLE_SLUG}}.md`（风格卡）
- `vendor/prompts/{{STYLE_SLUG}}.md`（逐字提示词，Signature features 一条都不能丢）
- `references/narrated-production.md`（长片和旁白片的做法，**必读**）

参考实现在 `vendor/demos/{{STYLE_SLUG}}/`。

### 2. script：写台词

按目标时长写旁白，存成 `script.json`，格式是 `{"segments":[{"id":"001","text":"..."}, ...]}`。

- 一句一段。中文每句 8 到 28 字，英文每句 5 到 18 个词。
- 估算语速（rate=1.0 时）：中文约 3.6 字/秒，英文约 2.5 词/秒（本机实测）。
- 纯语音总长控制在目标时长的 70% 到 85%。剩下的时间留给开场、停顿和落版。
- 标点就是停顿，不要写语音念不出来的符号。

### 3. voice：合成并量时长

```bash
"{{WORKBENCH}}/mgw" narrate "{{JOB_DIR}}"
```

- 这一步在本地合成，比较慢，约为音频时长的 4 倍。超过 8 分钟就加 `--detach` 放到后台，再用 `mgw narrate` 轮询，已经合成好的句子会自动复用。
- 看输出里的 `speech_total`：
  - 如果不在目标时长的 65% 到 90% 之间，就增删或改写句子，然后重跑（只有改过的句子会重新合成）。
  - 最多改 3 轮。
- 不要用改语速来凑时长。语速是用户在音色设置里定的。

### 4. storyboard：分镜并铺时间轴

1. 按台词分场景，给每句定开始时间，写进 `starts.json`，格式是 `{"001": 0.8, "002": 4.1, ...}`。
2. 运行 `mgw assemble "{{JOB_DIR}}" --starts starts.json`，生成 `voice.wav` 和 `timeline.json`，里面有每句的真实起止时间。
3. 如果有 warnings，说明句子被截断了，要调整后重跑。

### 5. build：写画面

1. 把最接近的参考实现复制到 `scene/`，作为起点。
2. 设置 `window.DEMO = {width:{{WIDTH}}, height:{{HEIGHT}}, fps:30, duration:{{DURATION}}}`。
3. 画面节拍要跟 `timeline.json` 对齐：哪句话出来，对应的画面就出来。
4. 角色、品牌、logo 一律原创，不得照搬任何现有 IP。
5. 字幕开启时，在画面层里按 `timeline.json` 逐句渲染字幕。字体和描边要符合这个风格，放在安全区内，自动换行。
6. 先渲几张静帧检查：`node {{SKILL_DIR}}/vendor/harness/render.mjs scene --stills 1,<中间>,<结尾前1秒>`。

### 6. music：配乐（只从曲库选歌，禁止生成背景音乐）

{{MUSIC}}

1. `mgw bgm-list` 看曲库，按 `references/narrated-production.md` 的「配乐」一节写 `bgm-plan.json`：逐段按情绪起伏选歌，不限首数和每段长短。
2. `mgw bgm-render "{{JOB_DIR}}"` → `music.wav`。报错就按提示改方案重跑。
3. 动作音效：`scene/audio.py` 里用 mgaudio 的 sfx 按画面动作卡点，导出 `sfx.wav`（{{DURATION}} 秒）。
4. 混音：`mgw mix "{{JOB_DIR}}" --music music.wav --sfx sfx.wav`，输出 `audio.wav`。

### 7. render：出片（自动排队，本机最多 2 条同时渲染）

```bash
"{{WORKBENCH}}/mgw" render "{{JOB_DIR}}" -- "{{JOB_DIR}}/scene" --audio "{{JOB_DIR}}/audio.wav" \
  --w {{WIDTH}} --h {{HEIGHT}} --fps 30 --duration {{DURATION}} --workers 3 --out "{{JOB_DIR}}/final.mp4"
```

长片渲染要用 `nohup … > render.log 2>&1 &` 放到后台，然后轮询 `render.log`（排队时会写「渲染排队中」），别让单条命令超时。

### 8. verify：验收

用真实的 ffmpeg 检查（本机的 ffprobe 是垫片，不可信）：
- 时长 = {{DURATION}} 秒，误差不超过 1 帧
- 分辨率 {{WIDTH}}×{{HEIGHT}}，有音轨
- 抽 3 张帧看画面和字幕是否正常

任何一项不合格就修好再出片。

### 9. done：汇报

1. 存进作品库：`mgw library-add "{{JOB_DIR}}" --model "<你当前实际用的模型名>"`（会复制成片和封面到 `MG视频工作台/library/`，并登记风格模板、模型、用时）。
2. 运行 `mgw status … done "成片完成"`，然后用 3 到 5 句话报告：台词主题、总时长、做了哪些取舍、`final.mp4` 的路径。
