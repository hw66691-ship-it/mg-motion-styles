# 几何构成 / 包豪斯 Geometric / Bauhaus Motion

> 蒸馏自 `mg-styles-15` · 展示序号 #11 · 原片《KONSTRUKTION · 20 Beats》 · 难度：入门
> 完整原始提示词：`vendor/prompts/09-bauhaus.md` · 参考实现源码：`vendor/demos/09-bauhaus/`

## 什么时候选它
动态海报、音乐节视觉、设计感品牌片；要机械理性卡点。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.techno(...)`
- 技术路线：HTML: SVG/Canvas + GSAP on a strict modular grid, beat grid at 120 BPM
- 建议主色：#F1E9DA #E03C31 #F2B705 #1E4FA3

## 这是什么风格
圆、三角、矩形在严格网格上做精确的平移、旋转、缩放，三原色+黑白的限定色板，机械理性的秩序美。源自包豪斯与瑞士国际主义平面传统（Adobe 曾与 Bauhaus 档案馆合作 Hidden Treasures 项目），也是动态海报（kinetic poster）的主流语言，与音乐节拍天然合拍。

**视觉特征**：基础几何形, 红黄蓝黑限定色, 严格网格对齐, 旋转以几何中心为轴, 节拍驱动的模块化运动

## 关键技法（可执行）
- 一切运动锚定网格：位移距离=网格模数整数倍，落点必在网格线上
- 缓动克制：easeInOutQuad 或干脆匀速，禁用 overshoot——机械感是特征不是缺陷
- 节拍驱动：每个几何元素在节拍点瞬时出现/翻转，一拍一个动作，类似我们已做的卡点逻辑
- 旋转轴心玩法：绕自身中心、绕边缘顶点、绕画面中心三种交替制造韵律
- 生成式变体：Processing/p5.js 用三角函数相位差批量驱动几何阵列（国内动态海报圈主流做法）

## 原片节拍参考（Creative seed）
「包豪斯动态海报」Bauhaus 1919 kinetic poster — mechanical, rational, musical.
- Cream paper (#F1E9DA), primaries red #E03C31, yellow #F2B705, blue #1E4FA3, black #111; strict modular grid (e.g. 240px modules); every move is an integer number of modules; every landing on a grid line.
- 120 BPM (0.5 s/beat): each beat a module acts — quarter circles rotate 90° about a corner pivot, semicircles slide one module, triangles flip, squares split; rotation pivots alternate (own centre / corner / frame centre).
- 0–2s grid lines draw & the first red circle lands; 2–6s the composition assembles into a Kandinsky/Bauhaus poster; 6–8s phase-shifted cascade wave across the grid on the drop; 8–10s freeze into a perfect poster with Swiss typography: "BAUHAUS" set vertically in heavy geometric sans + small caps "FORM · FARBE · FUNKTION".
- Easing: power2.inOut or linear — NO overshoot; subtle paper tooth + slight print misregistration allowed.
Sound: minimal techno/click — each flip = a pitched click/blip, kick on quarters.

## 音频
- 配方：`recipes.techno`
- 音效设计：minimal techno/click — each flip = a pitched click/blip, kick on quarters.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
