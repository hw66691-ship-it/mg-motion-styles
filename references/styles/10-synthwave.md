# 80s Synthwave / VHS Retro: 80s Synthwave / VHS / Y2K

> 蒸馏自 `mg-styles-15` · 展示序号 #12 · 原片《NEON DRIVE — Midnight 1986》 · 难度：进阶
> 完整原始提示词：`vendor/prompts/10-synthwave.md` · 参考实现源码：`vendor/demos/10-synthwave/`

## 什么时候选它
复古怀旧、游戏/潮流品牌、标题序列；要霓虹与镀铬字。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.synthwave(...)`
- 技术路线：HTML WebGL (perspective grid, sun, mountains shader) + canvas chrome text + CSS/SVG glow; VHS pass
- 建议主色：见下方 Creative seed

## 这是什么风格
对特定年代媒介美学的整体引用：80s synthwave 是霓虹网格+日落渐变+镀铬字；VHS 是扫描线+色偏+磁带噪声；Y2K 千禧风是液态镀铬金属、酸性绿紫、拟物系统窗口和低保真 3D。近两年 Y2K 在音乐视频与潮流品牌片中强势回潮，B站模板市场大量供应'酸性镀铬'素材。

**视觉特征**：霓虹辉光, 透视网格地平线, 扫描线与RGB色偏, 镀铬金属字, 酸性配色, 拟物窗口UI

## 关键技法（可执行）
- synthwave 三件套：透视网格滚动（一点透视 grid + 纵向位移循环）、日落多层渐变球、双层辉光（内层紧 4px 高亮+外层散 30px 低透明）
- VHS 做旧链：RGB split（红蓝通道各偏 1~2px）→ 扫描线（2px 间隔 10% 黑条）→ 波浪扭曲抖动（每秒 1~2 次随机 glitch 抽帧）→ 4:3 圆角遮罩
- Y2K 镀铬字：极高对比的多段金属渐变 + bevel 高光 + 环境映射感反光，配 lens flare
- Y2K 运动语言：弹窗式 pop 出现、光标点击、窗口拖拽，界面拟物即动画叙事
- 帧率故意不稳：关键段落抽帧到 15fps 或倒放 2 帧制造磁带卡顿

## 原片节拍参考（Creative seed）
「OUTRUN 1986」The quintessential 80s synthwave title sequence.
- Starry night, striped retro sun (horizontal band cut-outs, magenta→orange→yellow), wireframe mountains, palm silhouettes, neon magenta/cyan perspective grid rushing toward the camera.
- 0–1s: VHS tracking noise + 'PLAY ▶' OSD; 1–4s: camera flies low over the grid, sun rises; 4–6s: CHROME title (e.g. "NEON DRIVE", multi-stop metallic gradient, bevel highlight, star glint sweeping across) SLAMS in with a lens flare; 6–7.5s: pink neon script word (e.g. "Midnight") writes on like a neon tube with flicker; 7.5–10s: sustained ride, subtle VHS chroma bleed/scanlines, end on the hero frame.
- Double glow (tight ~4px + wide ~30px), deep purple sky gradient.
Sound: synthwave — gated-reverb snare, arpeggiated saw bass, lush pads, big chord + crash on the title slam.

## 音频
- 配方：`recipes.synthwave`
- 音效设计：synthwave — gated-reverb snare, arpeggiated saw bass, lush pads, big chord + crash on the title slam.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
