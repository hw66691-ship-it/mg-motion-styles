# 综艺花字 Variety Show Kinetic Captions

> 蒸馏自 `mg-styles-15` · 展示序号 #15 · 原片《Miaowu Diary EP.07》 · 难度：入门
> 完整原始提示词：`vendor/prompts/18-hanazi.md` · 参考实现源码：`vendor/demos/18-hanazi/`

## 什么时候选它
vlog、萌宠、访谈、搞笑二创；竖屏 9:16，情绪化装饰字幕。

## 硬规格
- 输出：1920×1080 · 30 fps · 300 frames · 精确 10.000 s · H.264 MP4 + 立体声 AAC 48 kHz · −14 LUFS / TP ≤ −1 dBTP · 文件名 `video.mp4`
- 配乐配方：`mgaudio.recipes.variety(...)`
- 技术路线：HTML DOM/SVG: multi-layer text-stroke 花字 components + spring pops + SVG burst/sweat/sparkle decorations over a pet-vlog footage layer (CC0 photos with Ken Burns + handheld shake + punch-ins)
- 建议主色：见下方 Creative seed

## 这是什么风格
源自电视综艺后期的情绪化装饰字幕：多层描边圆体字带弹性入场，跟随人物情绪变色变形，配打击音效。现已下沉为 vlog、萌宠、访谈、搞笑二创的通用包装语言，剪映内置大量花字模板，B 站也有免费花字样式包流通。

**视觉特征**：多层描边圆体/胖体字, 高饱和撞色+白边+投影, 弹性 pop 入场, 配合音效出现, 手绘装饰符号（爆炸框/汗滴/闪光）

## 关键技法（可执行）
- 字体三层结构：填充色+粗白描边+彩色外描边/投影（CSS 可用多层 text-shadow 或 SVG stroke 模拟）
- 入场 overshoot：scale 0→1.15→1.0（约 8 帧），或逐字弹跳错帧 2 帧
- 情绪匹配：吐槽用歪斜手写体、惊讶用放射线爆炸框、尴尬用汗滴符号
- 出现时机对齐笑点/音效，比语音晚 2~3 帧更自然
- 长时间驻留花字加轻微 wiggle 保持活性

## 原片节拍参考（Creative seed）
「萌宠综艺感 vlog」综艺花字 in its native habitat — reactive captions over a pet vlog.
- Base layer that feels like footage: CC0/PD cat or dog photos from /assets/images with slow Ken Burns, subtle handheld shake, snap punch-in zooms on 'moments' (you may also build a stylised scene if photos look weak).
- 花字 moments synced to beats: title "今日份快乐" (fill gradient + thick white stroke + coloured outer stroke + drop shadow, rounded heavy font), "？？？" bouncing question marks, "震惊!!" inside a radial 爆炸框 with speed lines + 放射线 flash, "（小声）" small aside, "绝绝子" with sparkles, sweat drops, a "猫主子认证" stamp.
- Motion: pop 0 → 1.15 → 1.0 in ~8 frames, per-character bounce with 2-frame stagger, slight rotation, gentle wiggle while holding; appear 2–3 frames after the audio/visual moment. High-saturation pink/yellow/cyan with white strokes.
Sound: bouncy variety-show bed (pizzicato/bass/claps) + boing, pop, ding, slide whistle, record scratch on '？？？'.

## 音频
- 配方：`recipes.variety`
- 音效设计：bouncy variety-show bed (pizzicato/bass/claps) + boing, pop, ding, slide whistle, record scratch on '？？？'.

## 改造点（换成你的内容）
- 换掉：故事线与节拍内容、品牌名（必须是虚构的）、文案、配色、落版 logo。
- 不要动：`视觉特征` 与 `关键技法`——这是这个风格被一眼认出来的依据。
- 改尺寸/时长：改 `Output` 段即可，技法不变（竖屏要把构图重排，不是单纯裁切）。
