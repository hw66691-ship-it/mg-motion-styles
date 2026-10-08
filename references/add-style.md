# 新增一种风格（第 16 种及以后）
不需要改本 skill 的代码，只要补齐「一份提示词 + 一个参考实现 + 一张蒸馏卡」三件套。

## 1. 命名与落位

先定 `slug`（小写连字符，如 `23-clay-3d`），然后：

| 产物 | 路径 |
|---|---|
| 完整提示词（逐字，含通用段） | `vendor/prompts/<slug>.md` |
| 参考实现源码 | `vendor/demos/<slug>/` |
| 蒸馏卡 | `references/styles/<slug>.md` |
| 索引条目 | 更新 `references/styles/INDEX.md` 与 `references/styles.json` |

## 2. 写提示词：照 `vendor/template.md` 填四段

```text
# Style
<中文风格名 English style name>

# Output (fixed)
- 1920×1080, 30 fps, exactly 10.000 s (300 frames), H.264 MP4 with stereo AAC audio (48 kHz), mastered to −14 LUFS
  integrated, true peak ≤ −1 dBTP. Final file: video.mp4.

# Suggested technical route
<SVG/Canvas/WebGL/Three.js/Blender… + 关键实现手段>
(You may choose a better route if it clearly raises quality; say why.)

# Creative seed
<「一句话片名」+ 按秒的钩子→升级→高潮→结尾；配色 3–6 个具体色值；字体气质；Sound: …>

# Signature features and key techniques (the result is judged against these)
<来源与用途一两句>
视觉特征 <逗号分隔>
关键技法 <可执行参数，每条一行>
```

通用部分（开头的角色设定 + How to work / Rules / Craft checklist / 自评 / Deliver）
**直接从 `references/universal-skeleton.md` 整段复制**，一字不改。

写好坏的三条线：
- `Signature features` 必须**可检验**：写「overshoot 用 cubic-bezier(0.34,1.56,0.64,1)，错峰 2–4 帧」，
  而不是「动效要有弹性」。
- `Creative seed` 必须**有节拍**：按秒写清钩子/升级/高潮/结尾，否则会做成平铺直叙的模板。
- 品牌名与文案**虚构**，避免商标问题。

## 3. 做参考实现

在 `vendor/demos/<slug>/` 建工程，遵守与现有 15 支相同的契约：

- `index.html`（+ 可选 js）+ `cues.json`（节拍表）+ `audio.py`（配乐）。
- 页面在 `window.__ready = true` 前定义 `window.renderAt(t)`（可选 `window.DEMO = {width,height,fps,duration}`）。
- 每帧是 t 的纯函数；随机带种子；不用实时时钟。
- `audio.py` 里 `sys.path.insert(0, ...'lib','audio')` 的写法照抄现有 demo（相对 `vendor/` 三级深度）。

渲染与配乐命令见 `references/pipeline.md`。

## 4. 配乐：先用现有配方，不够再加

- 优先从现有配方里挑一个最接近的（`synthwave / darksynth / vaporwave / chiptune / techno / acid /
  pop / future_bass / trap / glitch_hop / lofi / ambient / guofeng / variety / explainer`）。
- 确实需要新曲风，就在 `vendor/lib/audio/mgaudio/recipes/` 下加一个模块，按 `base.py` 的
  `new_mix / place_segments / Form / bass_events / comp_events` 套路实现，并注册进
  `recipes/__init__.py` 的 `STYLES` 表（含 slug → recipe / kwargs / 备选 / SFX 调色板）。
- 新风格的 SFX 组合尽量复用 `mgaudio.sfx` 现有函数；缺音色再补。

## 5. 蒸馏卡模板

```markdown
# <中文名> <English Name>

> 蒸馏自 `mg-styles-15`（扩展） · 展示序号 #NN · 难度：入门/进阶/困难
> 完整原始提示词：`vendor/prompts/<slug>.md` · 参考实现源码：`vendor/demos/<slug>/`

## 什么时候选它
<一两句使用场景>

## 硬规格
- 输出：<W×H · fps · frames · 10.000 s · −14 LUFS / TP ≤ −1 dBTP>
- 配乐配方：`mgaudio.recipes.<x>(...)`
- 技术路线：<...>
- 建议主色：<#hex 列表>

## 这是什么风格
<来源与传统>。**视觉特征**：<逗号分隔>

## 关键技法（可执行）
- <参数级技法>

## 原片节拍参考（Creative seed）
<...>

## 音频
- 配方：`recipes.<x>`
- 音效设计：<...>

## 改造点（换成你的内容）
- 换掉：故事线、品牌名（虚构）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`。
```

## 6. 收尾自检

1. 用 `references/rubric.md` 让另一个会话独立评审，分数目标 ≥ 9，改到不再提升。
2. 更新 `references/styles/INDEX.md`（速查表 + 按需求挑）与 `references/styles.json`。
3. 若引入了新素材/字体，在 `CREDITS.md` 记录来源与授权（只允许 CC0 / PD / OFL / Apache / 可商用免费）。
4. 把新提示词与参考实现一并留下，保证下一个人能**只靠这份 skill** 复现。
