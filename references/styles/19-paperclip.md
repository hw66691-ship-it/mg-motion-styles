# 粗描边贴纸科普 MG Bold-outline Sticker Explainer

> 蒸馏自 `mg-styles-15` · 展示序号 #07 · 原片《How Many Elements Hide in a Phone?》 · 难度：进阶
> 完整原始提示词：`vendor/prompts/19-paperclip.md` · 参考实现源码：`vendor/demos/19-paperclip/`

## 什么时候选它
硬核科普、财经知识区、企业宣传片；要信息密度与严肃感。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.explainer(...)`
- 技术路线：HTML: one huge canvas (e.g. 6000×3000 px) with a camera transform (long eases), SVG charts, photo stickers with 10px white outline
- 建议主色：#E9EEF2 #FF5A36

## 这是什么风格
回形针 PaperClip 带火的知识区标准包装：实拍图片抠图后加粗白描边变成『贴纸』，与扁平图标、数据图表一起铺在大画布上，镜头平移缩放串联信息点；林超等财经/跨学科 UP 主将其与手写板书、公式卡片结合。至今仍是硬核科普、财经知识区、企业宣传片的主流范式。

**视觉特征**：照片贴纸化（粗白描边）, 蓝灰/米白冷静底色, 扁平图标+精确数据图表, 大画布镜头平移缩放, 信息密度极高的节拍化叙事

## 关键技法（可执行）
- 素材照片抠图 + 8~12px 白描边统一质感，消除图片来源差异
- 超宽大画布布局，摄像机层做平移/缩放（ease 长曲线），一镜串多个信息点
- 图表动效：柱状图生长、数字滚动计数、路径描边生长
- 解说词逐句驱动画面元素入场，语速快、每句必有新视觉元素
- 克制配色（2~3 色）+ 等线字体，保持『严肃感』

## 原片节拍参考（Creative seed）
「回形针式硬核科普」The PaperClip-style knowledge-video look: sticker-ized photos + flat icons + precise charts on a giant canvas with continuous camera moves.
- Topic (write your own tight copy), e.g. 「一部手机里，藏着多少种元素？」.
- Calm blue-grey/off-white canvas (#E9EEF2 + slate), 2–3 colours + one accent (e.g. #FF5A36); equal-weight sans typography, strict alignment.
- One continuous camera path: sticker phone photo (white 10px outline, soft shadow) → exploded-parts stickers with leader-line labels → periodic-table grid where element tiles light up → bar chart grows with count-up "70+" → world map with supply routes drawing → pull out to a bold typographic title card in the 回形针 manner (heavy sans, huge number, small caption).
- Every beat introduces a new visual element; charts are exact (bars to scale, numbers consistent).
Sound: clean tech-explainer bed, UI clicks, ticking during count-up, soft whoosh on camera moves.

## 音频
- 配方：`recipes.explainer`
- 音效设计：clean tech-explainer bed, UI clicks, ticking during count-up, soft whoosh on camera moves.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
