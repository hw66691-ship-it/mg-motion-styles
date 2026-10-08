# 逐帧手绘 / 线条沸腾 Cel Animation / Frame-by-Frame

> 蒸馏自 `mg-styles-15` · 展示序号 #01 · 原片《HAND MADE》 · 难度：进阶
> 完整原始提示词：`vendor/prompts/05-cel-boil.md` · 参考实现源码：`vendor/demos/05-cel-boil/`

## 什么时候选它
有手作温度的插画叙事、卡通角色、烟火水花特效点缀。

## 硬规格
- 输出：1920×1080 · 30 fps · 240 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.lofi(...)`
- 技术路线：HTML Canvas2D: custom variable-width brush renderer (centreline + pressure → outline polygon), boil = 3–4 jitter variants cycled every 2 frames; paper texture multiply
- 建议主色：见下方 Creative seed

## 这是什么风格
手绘逐帧或在矢量动画上叠加逐帧质感，标志性特征是 line boil——线条每隔几帧轻微抖动，仿佛画面在'呼吸'。Giant Ant、Buck 等工作室大量使用 cel 元素（烟、水花、速度线）点缀主动画，反数字精致感的核心手段。

**视觉特征**：线条持续微抖(boil), 一拍二/一拍三节奏, smear拖影帧, 手绘烟火水花点缀, 纸纹底

## 关键技法（可执行）
- 打帧节奏：24fps 下'一拍二'（实际12fps）为主，快动作切'一拍一'，静止镜头'一拍三'
- line boil 伪造法：AE 用 Turbulent Displace（数量2~5、大小50）+ 每 2 帧随机化 evolution + Posterize Time 12fps；真 boil 则画 3~4 张微差线稿循环
- smear frame：快速位移的中间帧把物体拉长 150%~300% 只保留 1 帧
- cel FX 点缀层：烟/水花/闪电用纯手绘逐帧叠在矢量主体上（Buck 式 hybrid）
- 整体叠纸纹（multiply 10~15%）统一手作气质

## 原片节拍参考（Creative seed）
「手作魔法」Hand-made frame-by-frame magic, Buck/Giant-Ant hybrid (clean shapes + hand-drawn cel FX), animated on 2s at 24 fps.
- Warm paper ground; ink linework that BOILS (lines redrawn with slight variation every 2 frames); fills slightly off-register like hand colouring.
- Story: a matchstick strikes (SMEAR frame, on 1s for the fast action) → a flame spirit character jumps out, anticipation + squash, dances (on 2s) → it bursts into cel FX: smoke puffs curling, sparks, star bursts, speed lines → the FX re-form into hand-lettered title (e.g. "HAND MADE" or 手作) that keeps boiling on a 1s hold (on 3s for the hold).
- Palette 3–4 colours: ink black, tomato red, sunny yellow, cream paper; paper grain multiply 10–15%.
Sound: playful jazzy pizzicato/xylophone bed + cartoon SFX: strike, fwoosh, pop, poof, sparkle — synced to the frame.

## 音频
- 配方：`recipes.lofi`
- 音效设计：playful jazzy pizzicato/xylophone bed + cartoon SFX: strike, fwoosh, pop, poof, sparkle — synced to the frame.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
