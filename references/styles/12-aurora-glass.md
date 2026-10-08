# 弥散渐变 / 玻璃拟态 Aurora Gradient & Glassmorphism

> 蒸馏自 `mg-styles-15` · 展示序号 #10 · 原片《Aurora — Think in Light》 · 难度：进阶
> 完整原始提示词：`vendor/prompts/12-aurora-glass.md` · 参考实现源码：`vendor/demos/12-aurora-glass/`

## 什么时候选它
AI 产品发布、科技品牌片；要慢、透、贵。当前主流默认皮肤。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.ambient(...)`
- 技术路线：HTML WebGL: aurora mesh-gradient shader + glass refraction (SDF lens, chromatic dispersion) + DOM/CSS backdrop-filter glass cards
- 建议主色：见下方 Creative seed

## 这是什么风格
大面积高斯模糊的彩色光斑（aurora/mesh gradient）缓慢漂移作底，磨砂半透明玻璃卡片浮在其上。苹果 iOS 26 Liquid Glass 与各家 AI 产品发布把这一风格推成 2024-2026 科技品牌片的默认视觉，气质是'慢、透、高级'。

**视觉特征**：大色斑高斯模糊漂移, 磨砂玻璃卡片, 1px高光描边, 邻近色低对比配色, 缓慢呼吸感节奏

## 关键技法（可执行）
- 底层 aurora：3~5 个纯色大圆 blur 80~150px，各自沿贝塞尔路径 20~40 秒漂移循环，彼此 blend 出 mesh gradient 感
- 玻璃卡片配方：backdrop-filter blur(20~40px) + 白色 5~10% 填充 + 1px 白色 30% 内描边 + 大半径圆角
- 配色用邻近色 2~3 色（紫蓝青/橙粉红），撞色会脏；暗底亮斑比亮底更出效果
- 全局叠 3~5% 噪点防 banding（与颗粒质感技法交叉）
- 缓动接近 linear 或 sine 呼吸曲线，一切都慢——快动作会立刻破坏气质；文字入场也只用 opacity+8px 位移

## 原片节拍参考（Creative seed）
「Liquid Glass」2025–26 AI-product-launch aesthetic: slow, translucent, expensive.
- Deep indigo-black base; 4–5 aurora blobs (violet/blue/cyan/magenta, adjacent hues only) drifting on bezier paths, blending into a mesh gradient, 3–5% noise dithering (no banding).
- Frosted glass cards (backdrop blur ~30px, 5–10% white fill, 1px 30% white inner highlight, large radius) float in with parallax depth and slight 3D tilt; micro-UI inside (chat bubble, voice waveform, toggles) animates with opacity + 8px rise.
- WOW: a Liquid-Glass lens (true refraction, chromatic dispersion on the rim, specular edge) glides across and magnifies the aurora and the cards.
- Title (invented product, e.g. "Aurora — think in light") in a light elegant sans; sine/breathing easing everywhere; nothing fast.
Sound: ambient cinematic pad, soft shimmer, very subtle UI ticks.

## 音频
- 配方：`recipes.ambient`
- 音效设计：ambient cinematic pad, soft shimmer, very subtle UI ticks.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
