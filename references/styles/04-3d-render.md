# 3D 渲染系 3D Render / CGI Motion Design

> 蒸馏自 `mg-styles-15` · 展示序号 #05 · 原片《soft. — Soft Landing》 · 难度：困难
> 完整原始提示词：`vendor/prompts/04-3d-render.md` · 参考实现源码：`vendor/demos/04-3d-render/`

## 什么时候选它
高端产品片、品牌 ident；要真实材质、软胶糖果质感。需 Blender。

## 硬规格
- 输出：1920×1080 · 30 fps · 240 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.ambient(...)`
- 技术路线：Blender 5.1.2 CLI (bpy script → Cycles on Metal GPU with OIDN denoise, or EEVEE if it holds quality) → PNG sequence → ffmpeg; optional HTML overlay pass for typography
- 建议主色：见下方 Creative seed

## 这是什么风格
Cinema 4D + Redshift/Octane 或 Blender 渲染的实体质感动画：软胶、玻璃、金属、布料，配合克隆阵列和物理模拟。是高端产品片（手机、饮料、球鞋）和品牌 ident 的主流，Maxon 官方 Demo Reel 就是该风格的年度风向标。

**视觉特征**：PBR真实材质, 浅景深, 柔和棚拍布光, 克隆器阵列, 软体碰撞, 糖果色软胶质感

## 关键技法（可执行）
- MoGraph 核心：Cloner 克隆器 + Random/Plain Effector 做群体波浪式动画
- 质感三件套：SSS 次表面散射（软胶感）+ AO + HDRI 三点布光
- 运动多用长尾 ease：位移曲线前 20% 完成 80% 路程，收尾极慢，配 motion blur
- 24/25fps 电影帧率 + 浅景深（f/1.8 感）区别于 2D 系的 30fps 利落感
- 常见结构：产品为轴心，粒子/流体/布料围绕它做物理模拟编排

## 原片节拍参考（Creative seed）
「Soft & Satisfying」The C4D/Octane pastel product-ident look (Maxon demo-reel vibe): soft candy materials, cloner arrays, physics-feel motion.
- Pastel studio: infinite cyc backdrop, big soft area lights + HDRI (see /assets/hdri), shallow DOF (f/1.8 feel), 24 fps, real motion blur.
- A MoGraph-style cloner field (geometry-nodes grid of glossy rounded pills/spheres) ripples with an effector wave; a hero object — inflated/bevelled 3D wordmark (e.g. "SOFT" or an invented brand) or a glossy jelly logo — drops in, squash-and-stretch jiggle (damped spring), collides with and displaces the cloner field.
- Material trio: SSS gummy (candy pink / peach), glossy plastic (cream / lilac), frosted glass or chrome accent — with AO, soft reflections, subtle subsurface glow.
- Camera: long-tail ease (80% of the move in the first 20%), ends on a clean hero composition held ~1s.
Sound: ASMR-satisfying soft thuds, squishes, bubbly pops, airy cinematic pad; hits frame-synced to impacts.

## 音频
- 配方：`recipes.ambient`
- 音效设计：ASMR-satisfying soft thuds, squishes, bubbly pops, airy cinematic pad; hits frame-synced to impacts.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
