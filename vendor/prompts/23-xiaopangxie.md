# 小螃蟹风格 Little Crab Storybook Lyric MV

**原片**：抖音小螃蟹系列抒情卡点 MV（5 支参考片）· 1280×720 · 24/30 fps · 31–118 秒 · 方块小蟹 + 中文歌词叙事

**源码**：[demos/23-xiaopangxie/](../demos/23-xiaopangxie/)

## 怎么用

1. 新建一个空文件夹，在里面打开一个能写代码、能执行命令的 AI 助手（例如 Claude Code）。本机需要能跑网页渲染（Node + Chrome）和 ffmpeg。
2. 把下面「提示词」整段复制进去发送。
3. 想换成自己的内容：改 `Creative seed` 里的故事、品牌名、文案和配色，或者改 `Output` 里的尺寸（比如竖屏 1080×1920）。不要删 `Signature features` 那一段，它是这种风格被一眼认出来的依据。
4. 参考片是 30–120 秒的整首歌卡点 MV；本提示词按本仓库统一规格出 **10 秒**短片。要做整首歌：把 `Output` 的时长改成歌曲长度，并按歌词逐句排 `cues.json` 后分段渲染再拼接。

## 提示词

```text
You are the director, motion designer, engineer and sound designer of ONE 10-second motion-design film.
The goal is the most classic, yet most stunning form of this style — award-shortlist / high-end commercial quality. A clean,
template-looking result is a fail. Benchmarks: Buck, ManvsMachine, Ordinary Folk, Giant Ant, Territory Studio, Apple keynote
motion, Pentagram motion identities, top Behance/Motionographer features, top 抖音/B站 designer accounts.

# Style
小螃蟹风格 Little Crab Storybook Lyric MV

# Output (fixed)
- 1920×1080, 30 fps, exactly 10.000 s (300 frames), H.264 MP4 with stereo AAC audio (48 kHz), mastered to −14 LUFS
  integrated, true peak ≤ −1 dBTP. Final file: video.mp4.

# Suggested technical route
HTML Canvas2D: flat hand-drawn shapes built from rounded rects + polygon wobble (crayon edge); paper-grain and mottle
overlay (overlay/multiply) for the picture-book tooth; characters animated on STEPPED holds (quantise the pose to 10–12 fps)
with a 6–9 px body bob and delayed accessory wobble; camera does the big moves (pan/push on held poses); one deterministic
renderAt(t) drawing pass per frame.
(You may choose a better route if it clearly raises quality; say why.)

# Creative seed
「我陪你看完这场雨」A quiet rain-night duet between two little crabs, the canonical 抖音 小螃蟹 lyric-MV form.
- 0.0–1.2s HOOK: paper-white frame; rain starts as short hand-drawn strokes; the orange crab walks in from the right on stepped
  holds, legs shuffling, body bobbing 6–9 px, and shakes the rain off. Nothing smooth: poses hold 3–5 frames.
- 1.2–3.0s: the pink crab walks in under an umbrella and stops beside it; a soft landing settles them both; the city skyline
  behind is a flat silhouette stack with a landmark tower, windows still dark.
- 3.0–5.0s: they turn to each other; a small flower sprouts on the pink crab's head; the rain thins and a cloud gap opens.
- 5.0–7.0s HERO: the camera pushes in; the moon clears the skyline with a soft halo; hearts and 4-point sparkles rise
  between them in beat-synced groups; the umbrella tilts to cover them both.
- 7.0–9.0s: the city's windows light up as a wave from the centre outwards — each window pops 1.5× and settles (0.42 s);
  the rain stops; the palette warms from indigo night to dusty peach.
- 8.6–10.0s: pull to a held end card — the two crabs side by side, hand-lettered title 小螃蟹 + a thin romanised tagline,
  with living micro-motion (paper breathing, 1–2 px sparkle drift).
Palette (flat, no gradients on the characters): terracotta crab #B4623F, dusty pink crab #D4819A, indigo sky #171A2E,
slate blue #2E3760, warm window #F2C14E, paper #E9E3D6, ink #2A2230. Heavy rounded CJK for the lyric line, playful
hand-lettered for the title.
Sound: warm felt-piano ballad at ~78 BPM in F major (Imaj9 – vi9 – IVmaj9 – V6/9); rain bed that fades as the lights come on;
soft footsteps on the walk-in, a bell when the flower sprouts, a swell + soft impact on the moon, dings walking upward as
the windows light.

You are the director: you may change the concept, copy, story beats and brand names if you find a stronger idea, but the
result must remain the CANONICAL, instantly-recognisable form of this style and must hit its signature features below.

# Signature features and key techniques (the result is judged against these)
抖音「小螃蟹」系列抒情卡点 MV：一只有四条小短腿的方块螃蟹当主角，在纸感手绘场景里演一段小故事，配中文歌词字幕。出自短视频个人创作者（@知渊 / @问我春风 / @WshigKsong 一类账号），是 2025–26 年 AI 辅助手绘 MV 的高频范式，用于歌曲宣发、情感叙事、品牌软性植入。
视觉特征 方块小蟹(宽壳+两侧肩角+4条短腿), 粗描边平涂+纸纹蜡笔颗粒, 低饱和夜色与暖窗黄, 大色块无渐变, 底边黄字深描边歌词, 简笔场景(城市剪影/成排小屋/雪夜森林/室内一角), 星芒爱心音符粒子
关键技法 角色构造：宽圆角矩形壳（宽高比约 1.6:1）＋壳顶两侧肩角（各向外扩约 15%，是辨识关键）＋4 条短腿（宽约壳宽 10%，长约壳高 35%）＋两条细手臂；眼睛三选一：`><` 尖角（最标志）、`^^` 圆眯、圆点；腮红用小椭圆
抽帧动画是灵魂：角色姿态量化到 10~12 fps（如 floor(t*11)/11），静止姿态保持 3~5 帧；禁止用平滑 30fps 补间，否则立刻失去手作感
身体 bob 幅度 6~9px、步频约 1.2~1.5 步/秒；伞/花/帽子等配件延迟 2 帧反向摆动做 follow-through
手绘 boil：整层每 2~3 帧做 ±0.7~1.5px 的重摆，配合顶点抖动让线条像在呼吸
描边恒定约 3px（随角色缩放），线色用深棕/深紫（#4E2A18 / #542E3A）而非纯黑，圆头圆角
纸感三件套：细颗粒（512px 噪声）＋粗颗粒（放大 2.1×）叠 'overlay' ＋大块径向色斑做水渍；总强度 5~15%
场景用平涂大色块搭：远景剪影 → 中景楼/屋 → 地面 → 栏杆道具；窗灯按「中心向两侧」波浪式点亮，每扇灯 0.42s 带 1.5× overshoot pop
字幕：底边居中黄字 #FFD84D ＋ 11px 深色描边 ＋ 上下渐隐黑底带；出入场 0.34s，带 1.05× 弹性 overshoot
粒子：四角星芒、爱心、音符按节拍成组出现，生命周期 1.5~1.7s，正弦淡入淡出并缓慢上浮
转场用撕纸/裂纹竖向分割或元素飞出带动切换，不要交叉淡化
节奏：一个镜头一个主动作，镜头负责平移与推近，角色只做小幅定格表演

# How to work
1. Treatment. Write down one clear idea: a hook in the first 0.5 s (never open on more than 0.3 s of empty or black), an
   escalation, one unmistakable hero moment at ~60–75 % of the runtime, and a composed end frame held ~0.8–1.2 s with living
   micro-motion. Map every signature feature above to a moment. Keep one cue sheet (beats and hit times) that both the
   picture and the sound read from.
2. Key frames before motion. Build the look, render stills at 6–10 key times and actually look at them. Each still should be
   poster-worthy: composition, hierarchy, negative space, type set properly (kerning, line-height, weight contrast, CJK
   punctuation, ~5 % safe margins). Iterate until nothing looks default, generic, cramped or "AI-template".
3. Motion. Build the choreography and preview at low resolution. Step through the fastest moves frame by frame: spacing,
   easing, arcs, overlap, anticipation and follow-through, motion blur. No unintended dead spans; the energy follows the music.
4. Sound. Write genre-correct music and sound design locked to the cue sheet. Check that visual hits land on audio onsets.
   Master to the output spec.
5. Final. Render at full resolution (motion blur where apt), then check: exactly 10.00 s, resolution, fps, audio present and at
   the right loudness, no black frames, no fallback fonts or tofu, no clipped elements at the frame edges, no shimmer on thin
   lines, no gradient banding. Fix and repeat until you would submit it to a festival.
6. Write an honest self-critique: what is strongest, what is weakest, what you would do with more time.

# Rules
- Rendering must be deterministic: every frame is a pure function of time t. Seeded randomness only; physics and particles
  precomputed or closed-form; no real-time clocks; no state-triggered CSS transitions. A reliable route: a web page that can
  draw any time t on request, captured frame by frame with a headless browser and encoded with ffmpeg (or a Blender script
  that renders a PNG sequence).
- Assets: only CC0 / public domain / OFL / Apache / free-for-commercial-use. Record each source and licence in CREDITS.md.
  No real brand trademarks; invent brand names.
- On-screen text must be correct and natural: idiomatic Chinese, proper CJK punctuation, no typos.

# Craft checklist (what a jury looks for)
- Style authenticity: an expert names the style in one second; every signature technique is present and executed correctly.
- Motion craft: purposeful easing (no linear unless mechanical by design), overlap and stagger, anticipation and
  follow-through, arcs, squash and stretch where the style allows, consistent physics, motion blur where apt; transitions
  carried by elements, not crossfades.
- Rhythm: hits locked to the music; contrast between busy and calm; no monotony.
- Design: strong composition, grid, typographic hierarchy, controlled palette; texture and finishing (grain, glow, vignette)
  only where the style wants it; nothing looks accidental.
- Technical polish: no jitter (unless intended), no popping, no aliasing, no banding, no fallback fonts, no half-loaded images.
- Sound: genre-correct, musical, synced, mastered.

# Before you deliver, score yourself honestly
1–10 on style fidelity, concept wow, motion craft, design & typography, finish & texture, sound & sync, technical
(6 = template-level, 8 = high-end agency, 9 = award shortlist). Aim for 9; fix whatever scores lowest first.

# Deliver
video.mp4, plus a short report: the concept in two sentences; a beat sheet with timecodes; how each signature feature is
realised; the tech route; check numbers (duration, resolution, fps, loudness, true peak); your honest top-3 weaknesses.
```
