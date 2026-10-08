# 赛博朋克 HUD / FUI Cyberpunk HUD / FUI

> 蒸馏自 `mg-styles-15` · 展示序号 #08 · 原片《KESTREL-9 · Target Acquired》 · 难度：进阶
> 完整原始提示词：`vendor/prompts/22-hud.md` · 参考实现源码：`vendor/demos/22-hud/`

## 什么时候选它
数码测评、游戏剪辑、军事航天科普、AI 演示；要科技感皮肤。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.darksynth(...)`
- 技术路线：HTML: SVG/Canvas FUI layers + Three.js wireframe hologram; seeded random data; glow/scanline post pass
- 建议主色：#00E5FF #FF6A00

## 这是什么风格
模拟科幻电影/游戏界面的抬头显示包装：青橙霓虹线框、目标锁定框、雷达扫描、数据流小字。在科技数码测评、游戏剪辑（赛博朋克2077、EVA 二创）、军事航天科普和 AI 产品演示中作为『科技感』的默认皮肤，B 站 AE HUD 案例教程播放量达 20 万。

**视觉特征**：青色/橙色霓虹线框, 目标锁定框与十字准星, 雷达/环形扫描 loop, 等宽小字数据流与打字机文字, 六边形网格与辉光

## 关键技法（可执行）
- 线框生长：SVG stroke-dasharray/dashoffset 描边动画，元素按层级错帧展开
- 环形雷达：conic-gradient 扫描扇区旋转 loop + 目标点闪烁
- 数字滚动：随机数快速跳变 3~5 帧后落定真实值；文字打字机 + 光标闪烁
- 锁定框：四角括号从大到小收缩吸附目标（scale 1.4→1.0 + 快出缓入）
- 全局外发光（glow）+ 轻微色差 + 扫描线叠加统一质感

## 原片节拍参考（Creative seed）
「目标锁定 TARGET ACQUIRED」Cyberpunk HUD / FUI, film-UI grade (Territory Studio-level density & restraint).
- Deep teal-black; cyan #00E5FF linework with orange/red #FF6A00 alert state; hex grid, concentric rotating rings with ticks, radar sweep (conic) with blips, data columns (monospace numbers rolling 3–5 frames then settling), typewriter status lines with cursor, sparkline graphs, a central Three.js wireframe hologram (globe or drone) with scanlines.
- Layered build-up: lines draw on in hierarchical staggered order → data comes alive → a target is found → lock brackets snap 1.4 → 1.0 (fast-out slow-in) → everything flips to alert orange with 'TARGET LOCKED / 目标锁定', coordinates "N31°14′ E121°29′".
- Glow, slight chromatic aberration, scanlines, restrained micro-glitches.
Sound: darksynth pulse + HUD beeps, scan sweeps, ascending lock-on tone, alarm on lock.

## 音频
- 配方：`recipes.darksynth`
- 音效设计：darksynth pulse + HUD beeps, scan sweeps, ascending lock-on tone, alarm on lock.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
