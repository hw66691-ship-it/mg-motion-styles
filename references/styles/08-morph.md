# 形变动画 Morphing / Shape Morph

> 蒸馏自 `mg-styles-15` · 展示序号 #06 · 原片《morphe. — One Shape, Every Story》 · 难度：入门
> 完整原始提示词：`vendor/prompts/08-morph.md` · 参考实现源码：`vendor/demos/08-morph/`

## 什么时候选它
苹果发布会级图形叙事、图标串联、一形万象的说明片。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.future_bass(...)`
- 技术路线：HTML: SVG + flubber or GSAP MorphSVGPlugin (tune shapeIndex), color-field wipes
- 建议主色：见下方 Creative seed

## 这是什么风格
一个图形丝滑连续地变成另一个图形：手机变成地图钉、咖啡杯变成落日。是图形叙事（visual storytelling）的核心语法，苹果发布会动效和高端 explainer 里最见功力的部分。

**视觉特征**：轮廓连续过渡无跳变, 中介形状桥接, 形变伴随位移旋转, 变形瞬间的挤压拉伸

## 关键技法（可执行）
- 路径对齐是前提：两形状顶点数一致、首顶点方位对应（AE 里重设 first vertex），否则会打结
- 复杂 A→B 不直接变：先收敛为中介简形（圆/胶囊）再展开，'A→圆→B'两段各 8~12 帧
- 形变全程叠加 10~15% squash & stretch 与轻微旋转，掩盖插值的机械感
- 速度曲线中段最快 cubic-bezier(0.7,0,0.3,1)：起止各留 3 帧缓冲
- Web 端用 flubber/polymorph 库做最优顶点匹配插值，效果远好于朴素 SMIL

## 原片节拍参考（Creative seed）
「万物相连」Apple-keynote-grade morph chain: one hero shape continuously becomes 6–8 meaningful icons, on the beat.
- Chain example: coffee cup → (circle) → sun → sunset over sea → gull → paper plane → location pin → heart → invented brand logo "morphe" with wordmark.
- Every A→B goes through a simple intermediate (circle/capsule) with rotation and 10–15% squash&stretch; sub-parts morph in sync (steam → sun rays → waves).
- Background color fields change with each morph (clean color-block wipes); ease cubic-bezier(0.7,0,0.3,1), 3-frame cushions at start/end; no knotting/tangling ever (check every morph mid-point stills).
Sound: rhythmic plucky arpeggio; a pitched whoosh per morph landing on the beat.

## 音频
- 配方：`recipes.future_bass`
- 音效设计：rhythmic plucky arpeggio; a pitched whoosh per morph landing on the beat.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
