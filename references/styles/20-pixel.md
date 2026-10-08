# 像素风 Pixel Art / 8-bit

> 蒸馏自 `mg-styles-15` · 展示序号 #13 · 原片《PIXEL QUEST》 · 难度：入门
> 完整原始提示词：`vendor/prompts/20-pixel.md` · 参考实现源码：`vendor/demos/20-pixel/`

## 什么时候选它
游戏区、8-bit MV、怀旧营销；要低分辨率大颗粒。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.chiptune(...)`
- 技术路线：HTML Canvas at 320×180 internal resolution, integer-scaled ×6 with nearest-neighbour; sprites authored as pixel arrays in code; limited palette
- 建议主色：见下方 Creative seed

## 这是什么风格
低分辨率大颗粒像素 + 有限色板 + 低帧率精灵动画的复古游戏美学，在 B 站游戏区（MC、泰拉瑞亚、独立游戏）、8-bit 音乐 MV 和品牌怀旧营销中常见；Aseprite 教程在 B 站有 10 万+ 播放的稳定学习生态。

**视觉特征**：大颗粒像素与硬边缘, 有限色板(8~32色), 8~12fps 精灵帧动画, 抖动渐变 dithering, CRT 扫描线滤镜

## 关键技法（可执行）
- Aseprite 绘制精灵表（sprite sheet）+ 序列帧循环（走路 6~8 帧、呼吸 2~4 帧）
- 缩放必须最近邻插值（CSS image-rendering: pixelated），杜绝抗锯齿糊边
- 动画用 steps() 阶梯时序而非平滑缓动，保持逐帧感
- 视差卷轴背景：远中近三层不同速度整像素平移
- 可选 CRT 后处理：扫描线+桶形畸变+磷光辉光

## 原片节拍参考（Creative seed）
「像素冒险 PIXEL QUEST」A retro side-scroller title/attract sequence.
- Internal 320×180, ×6 nearest-neighbour; limited palette (PICO-8-like 16–32 colours) with dithered sky gradient; 3–4 parallax layers (sky, far mountains, mid forest/city, near ground tiles) moving by whole pixels.
- Hero sprite (hand-authored 16×16–24×24, 6–8 frame run cycle at ~10–12 fps) runs, jumps, collects coins (sparkle), bops a slime; the palette shifts day → sunset; a treasure chest opens with a light burst.
- Dialogue box with pixel CJK font typing 「欢迎来到像素世界！」; chunky pixel logo "PIXEL QUEST" drops in with shine sweep; optional CRT pass (scanlines, slight barrel, phosphor glow) that doesn't blur pixels into mush.
- Strictly: nearest-neighbour, integer pixel positions, stepped timing (no smooth easing on sprites).
Sound: chiptune (pulse lead, triangle bass, noise drums) + jump/coin/chest SFX.

## 音频
- 配方：`recipes.chiptune`
- 音效设计：chiptune (pulse lead, triangle bass, noise drums) + jump/coin/chest SFX.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
