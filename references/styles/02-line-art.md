# 线条动画 Line Art / Line Animation

> 蒸馏自 `mg-styles-15` · 展示序号 #04 · 原片《ATELIER LINEA — One Line》 · 难度：入门
> 完整原始提示词：`vendor/prompts/02-line-art.md` · 参考实现源码：`vendor/demos/02-line-art/`

## 什么时候选它
奢侈品、金融、建筑、logo 演绎；要高级、克制、留白大。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.ambient(...)`
- 技术路线：HTML: SVG paths + stroke-dashoffset (getTotalLength) + GSAP; a virtual camera that follows the pen tip
- 建议主色：#0B1320 #E9D7A5

## 这是什么风格
以单色细线为唯一造型语言，线条自我描绘（draw-on）、延伸、转折并变形为下一个图形，一笔连成整支片子。极简高级感强，常见于奢侈品、金融、建筑类品牌片和 logo 动画。

**视觉特征**：等宽细线, 单色或双色, 大量负空间, 线条连续生长, 线面转换瞬间

## 关键技法（可执行）
- 核心是 stroke 描绘：AE 用 Trim Paths 0→100%，Web 端用 SVG stroke-dasharray/dashoffset
- 线宽全片恒定（2~4px），转角处让描绘速度略减速，用 easeInOut cubic-bezier(0.65,0,0.35,1)
- '一笔画'叙事：上一图形的尾线即下一图形的起线，路径提前在 Illustrator 里连好
- 线转面：描完轮廓后用同路径的 fill 从锚点扩展填充
- 配合微小的端点圆头（round cap）与路径抖动可增加手绘感

## 原片节拍参考（Creative seed）
「一笔画」One-line narrative for a luxury / architecture brand — the whole film is ONE continuous line.
- Deep midnight ground (#0B1320 or near-black) + a single champagne-gold line (#E9D7A5), constant ~3px, round caps, a softly glowing pen tip that leads the draw.
- Story (continuous path, the tail of each figure is the start of the next): a seed → sprouts into a sapling → branches become the structural lines of a building → the building outline extends into a skyline/horizon → the horizon line lifts and loops into a monogram logo → LINE-TO-FILL moment (logo fills with gold from its anchor) → thin letter-spaced serif wordmark (e.g. "ATELIER LINEA") fades up.
- Draw speed eases into corners (cubic-bezier(0.65,0,0.35,1)); the virtual camera drifts/pushes to keep the tip in frame, then dollies out at the end to reveal the whole drawing composed as a poster; older line segments dim to ~35% as the camera moves on.
Sound: minimal felt piano + soft string swell; a pen-on-paper whisper whose loudness follows tip speed; delicate chime on the fill.

## 音频
- 配方：`recipes.ambient`
- 音效设计：minimal felt piano + soft string swell; a pen-on-paper whisper whose loudness follows tip speed; delicate chime on the fill.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
