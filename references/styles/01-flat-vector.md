# 扁平矢量动画 Flat / Vector 2D Motion Graphics

> 蒸馏自 `mg-styles-15` · 展示序号 #03 · 原片《popwise — One Dot》 · 难度：入门
> 完整原始提示词：`vendor/prompts/01-flat-vector.md` · 参考实现源码：`vendor/demos/01-flat-vector/`

## 什么时候选它
SaaS 产品解释、品牌科普、企业年报；要干净、好懂、节奏轻快。最稳的通用款。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.pop(...)`
- 技术路线：HTML: SVG + GSAP (CustomEase/CustomBounce/MorphSVG); motion blur mb=4 for fast moves
- 建议主色：#2B2BFF #FF5A4E #FFC62B #2EE6A8 #FFF6E9 #151433

## 这是什么风格
MG 动画最主流的基本盘风格，源自 Google Material/企业解释视频（explainer）传统。纯色几何化的人物与场景、无描边或极简描边、大色块撞色，一切元素都是矢量形状。常见于 SaaS 产品宣传、科普解说、企业年报视频。

**视觉特征**：纯色大色块, 几何化角色, 无渐变或极少渐变, 干净留白, 高饱和品牌色板, 元素弹性入退场

## 关键技法（可执行）
- AE Shape Layer + 父子级 null 控制层级，人物四肢用锚点旋转做 rig
- 弹性缓动是灵魂：overshoot 用 cubic-bezier(0.34,1.56,0.64,1) 或 AE 里 70~85% influence 的贝塞尔手柄；入场'预备-冲出-回弹'三段式
- 元素错峰入场（stagger 2~4 帧），同一时刻只让一个主体动
- 30fps 居多；位移动画带 10% 左右 squash&stretch 增加弹性
- 转场常用色块擦除（shape wipe）或元素飞出带动整场切换

## 原片节拍参考（Creative seed）
「一镜到底的扁平世界」One-continuous-shot brand explainer, the canonical Motion-Ocean/Google-explainer form, pushed to showreel polish.
- 0.0–1.2s HOOK: empty bold color field; a single saturated circle drops in with the three-phase anticipation → stretch → squash → overshoot → settle. Immediately readable craft.
- 1.2–3.0s: the circle becomes the sun; a flat city pops up building-by-building with 2–4 frame stagger (each with its own mini overshoot), clouds slide, birds flap.
- 3.0–5.5s: camera pushes into one window → a geometric character at a desk (limb rig with anchor rotations, head bob, blink) reacts; phone pings.
- 5.5–8.0s: the notification bubble expands to fill the frame as a SHAPE WIPE transition; inside, icons burst in a choreographed rhythm (bar chart grows, check mark draws, heart pops, coin flips).
- 8.0–10.0s: element-driven transition — everything collapses/flies into a logo lockup for an invented brand (e.g. "Popwise") + tagline, elastic settle, 1s hold with micro-motion.
Rules: one hero moves at a time; squash&stretch ~10%; secondary action & follow-through; element-driven transitions (an object flies out and carries the cut); strictly flat (no gradients), bold 5–6 color palette (e.g. ultramarine #2B2BFF, coral #FF5A4E, sunflower #FFC62B, mint #2EE6A8, cream #FFF6E9, ink #151433).
Sound: upbeat future-bass/pop ~120 BPM; pop/boing/whoosh on each entry, synced to the frame.

## 音频
- 配方：`recipes.pop`
- 音效设计：upbeat future-bass/pop ~120 BPM; pop/boing/whoosh on each entry, synced to the frame.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
