# 液态流动 Liquid Motion

> 蒸馏自 `mg-styles-15` · 展示序号 #14 · 原片《drop. — It All Starts with a Drop》 · 难度：进阶
> 完整原始提示词：`vendor/prompts/07-liquid.md` · 参考实现源码：`vendor/demos/07-liquid/`

## 什么时候选它
音乐视频、食品饮料、转场包装；要解压、有机、高能量。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.future_bass(...)`
- 技术路线：HTML WebGL2 fragment shader: 2D SDF metaballs (smooth-min) + fake 3D lighting from field gradient normals, text SDF for the logo
- 建议主色：见下方 Creative seed

## 这是什么风格
图形像液体一样流动、拉丝、滴落、融合：转场是一泼颜料漫过屏幕，logo 从一滴液体聚合成形。有机、解压、高能量，广泛用于音乐视频、食品饮料广告和转场包装。

**视觉特征**：波浪边缘转场, 拉丝与滴落, metaball融合, 次级液滴跟随, 有机曲线永不直线

## 关键技法（可执行）
- 液态转场：遮罩路径手 K 波浪形前沿扫过画面，前沿加 3~5 个错相位的凸起
- metaball 融合的通用伪造法：高斯模糊(20px+) → 提高对比度阈值（AE 用 Levels 收紧、Web 用 feColorMatrix alpha 阈值），两球靠近即自动'粘连'
- 拉丝-断裂-回弹：主形离开时留一条细颈，断裂瞬间两端各回弹 2~3 帧
- 缓动前快后慢 cubic-bezier(0.22,1,0.36,1)，液体只会被'甩'出去不会匀速
- 次级液滴延迟主体 2~3 帧跟随（follow-through），落地做扁平化 squash

## 原片节拍参考（Creative seed）
「液态创世」Liquid logo genesis — glossy, organic, high energy.
- Deep plum ground; glossy candy liquid (hot orange → pink → violet) with specular highlights and fresnel rim so it reads like thick 3D liquid, not flat blobs.
- 0–2s: droplets fall and splash with squash on landing; 2–4s: blobs merge via metaball fusion — stretched necks, snap, 2–3 frame rebound; secondary droplets follow 2–3 frames late;
- 4–6s: a big liquid wave floods across the frame as a transition (wavy front with 3–5 phase-offset bulges);
- 6–8.5s: the liquid coalesces into a wordmark (e.g. "FLUX") — text SDF blended with the metaballs;
- 8.5–10s: a last drip falls from the logo and ripples; hold.
Ease: flung, never uniform (cubic-bezier(0.22,1,0.36,1)).
Sound: bubbly gloops, pour, splash, drip, deep bass swell under a glossy synth bed.

## 音频
- 配方：`recipes.future_bass`
- 音效设计：bubbly gloops, pour, splash, drip, deep bass swell under a glossy synth bed.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
