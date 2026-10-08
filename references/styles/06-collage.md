# 拼贴剪贴 Collage / Cutout Animation

> 蒸馏自 `mg-styles-15` · 展示序号 #09 · 原片《NOGGIN Quarterly》 · 难度：进阶
> 完整原始提示词：`vendor/prompts/06-collage.md` · 参考实现源码：`vendor/demos/06-collage/`

## 什么时候选它
音乐类、街头潮流、脑洞二创；要复古超现实和杂志感。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.lofi(...)`
- 技术路线：HTML: DOM/Canvas with PNG cutouts from /assets/images (rembg), SVG/CSS white-edge + halftone filters; stepped 12 fps (render 30 fps, hold motion on 12 fps grid)
- 建议主色：见下方 Creative seed

## 这是什么风格
把老照片、报纸、手撕纸片剪出来重新拼装的复古超现实风格，源头是 Monty Python 和苏联构成主义海报。人物头身比例失衡、嘴巴单独开合、半调网点纹理是标志。近年与'杂志风'合流，成为音乐类、街头潮流类短视频的高频风格。

**视觉特征**：照片剪影白描边, 半调网点, 报纸纹理, 比例失衡的超现实拼装, 定格式抽帧运动

## 关键技法（可执行）
- 素材处理：人物/物件抠图后加 2~4px 白描边（剪刀剪出来的感觉）+ 半调 halftone 滤镜
- 关节动画：锚点设在肩/肘/颌，做 puppet 式分段旋转，嘴巴用两三张替换帧开合
- 刻意降帧：主体运动 12fps 甚至 6fps（stop-motion 感），位置加 ±2px 随机抖动模拟手摆
- 图层结构：背景纸纹 → 大形色块 → 照片剪影 → 手写涂鸦/胶带贴纸 → 颗粒调整层
- 转场用'手把元素拍上来'或整页翻纸

## 原片节拍参考（Creative seed）
「脑洞拼贴」Surreal Dada/Monty-Python cutout collage in a modern editorial magazine finish.
- Newsprint/kraft paper ground; a public-domain Victorian portrait cutout with rough white scissor edge + halftone; the top of the head FLIPS OPEN like a lid (Terry Gilliam homage) revealing deep space (NASA PD imagery) from which flowers, birds, planets, pointing hands and a vintage rocket spill out.
- Jaw/mouth on a separate cut flaps with the sound; hands slap elements onto the page; torn-paper strips; bold constructivist red/black diagonal typography (e.g. "THE MIND IS A COLLAGE" / 脑洞大开).
- Motion on 12 fps (even 6 fps for some holds) with ±2px hand-placement jitter; paper-flip / torn-paper transition to the end card.
Sound: vinyl crackle, jazzy boom-bap bed, paper rustles, scissors snips, slaps and a comic 'pop' when the lid opens.

## 音频
- 配方：`recipes.lofi`
- 音效设计：vinyl crackle, jazzy boom-bap bed, paper rustles, scissors snips, slaps and a comic 'pop' when the lid opens.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
