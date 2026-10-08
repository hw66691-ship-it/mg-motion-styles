# 等轴 2.5D Isometric / 2.5D

> 蒸馏自 `mg-styles-15` · 展示序号 #02 · 原片《ISOPOLIS — Let the City Grow》 · 难度：进阶
> 完整原始提示词：`vendor/prompts/03-isometric.md` · 参考实现源码：`vendor/demos/03-isometric/`

## 什么时候选它
科技公司架构图、App 功能演示、数据机房；要信息密度高又可爱。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.explainer(...)`
- 技术路线：HTML: Three.js OrthographicCamera at true isometric angle + soft shadows + AO (three/addons postprocessing), or SVG with SSR matrix faces
- 建议主色：见下方 Creative seed

## 这是什么风格
以 30° 等轴测投影展示微缩世界：小城市、办公室切片、数据机房，无灭点、处处等比。信息密度高又不失可爱，是科技公司架构图动画和 App 功能演示的标配。School of Motion 有专门的 isometric mograph 教程系列。

**视觉特征**：30°等角投影, 无透视灭点, 微缩场景, 楼房生长动画, 平行滑轨式运镜

## 关键技法（可执行）
- SSR 公式造等轴面：Scale 纵向 86.6% → Shear/skew ±30° → Rotate ∓30°，三个面分别做后拼合
- 假 3D 靠图层排序：Z 序=画面 y 坐标，物体沿等轴网格移动时保持 2:1 像素斜率
- 楼房'生长'：底面先落位，立面用 scaleY 从 0 拉起 + 顶面延迟 2~3 帧盖上
- 运镜是整组平移（无旋转），配合前中后景 1:0.8:0.6 的视差速度
- AE 里可用真 3D 图层+正交相机（无透视）偷懒，Motion Design School 的 Isometric Camera 技巧即此路

## 原片节拍参考（Creative seed）
「微缩智慧城」An isometric miniature city / data campus that builds itself — the School-of-Motion isometric mograph showpiece.
- True isometric camera (orthographic, 35.264° elevation, 45° azimuth), no perspective, pastel studio palette (lavender ground, mint, peach, sky blue, white) with soft shadows + ambient occlusion so it reads like a premium Dribbble/Behance hero.
- 0–2s: ground tiles flip/drop in as a wave from the centre (tiny bounce each);
- 2–5s: buildings GROW — base lands, walls scaleY from 0 with overshoot, roof caps 2–3 frames later; trees pop; windows light up in sequence;
- 5–8s: life — cars loop along roads, a little train, drones carrying packets, glowing data streams pulse between buildings, a wind turbine spins; camera does parallel slides (no rotation) with 1 : 0.8 : 0.6 parallax layers (foreground clouds);
- 8–10s: pull back to reveal the whole island floating in a pastel void; title card set ON the isometric plane (text skewed into iso space) e.g. "SMART CITY OS".
Sound: bright plucky tech melody (FM marimba/pluck), soft clicks/pops for every tile/building landing, airy whoosh on the pull-back.

## 音频
- 配方：`recipes.explainer`
- 音效设计：bright plucky tech melody (FM marimba/pluck), soft clicks/pops for every tile/building landing, airy whoosh on the pull-back.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
