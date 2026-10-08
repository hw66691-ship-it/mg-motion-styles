# 通用提示词骨架（15 种风格共用）

每一份风格提示词 = **通用部分**（15 份一字不差）+ **风格专属部分**。
原始 15 份提示词逐字保存在 `vendor/prompts/*.md`，可直接使用。本文件是把通用部分抽出来，
便于组合新风格的提示词。

## 一份提示词的完整结构

```text
You are the director, …              ← 固定开场（所有风格相同）
# Style                              ← 风格名（中文 + English）
# Output (fixed)                     ← 硬规格：尺寸/帧率/时长/编码/响度
# Suggested technical route          ← 技术路线
# Creative seed                      ← 唯一可自由替换的部分：故事 / 配色 / 音效
# Signature features and key techniques   ← 不可删，决定风格辨识度
# How to work                        ← 固定收尾
# Rules                              ← 固定收尾
# Craft checklist (what a jury looks for)  ← 固定收尾
# Before you deliver, score yourself honestly ← 固定收尾
# Deliver                            ← 固定收尾
```

## 固定开场（逐字）

```text
You are the director, motion designer, engineer and sound designer of ONE 10-second motion-design film.
The goal is the most classic, yet most stunning form of this style — award-shortlist / high-end commercial quality. A clean,
template-looking result is a fail. Benchmarks: Buck, ManvsMachine, Ordinary Folk, Giant Ant, Territory Studio, Apple keynote
motion, Pentagram motion identities, top Behance/Motionographer features, top 抖音/B站 designer accounts.
```

## Output 硬规格

横屏（14 种风格的默认）：

```text
# Output (fixed)
- 1920×1080, 30 fps, exactly 10.000 s (300 frames), H.264 MP4 with stereo AAC audio (48 kHz), mastered to −14 LUFS
  integrated, true peak ≤ −1 dBTP. Final file: video.mp4.
```

横屏电影帧率（04-3d-render、05-cel-boil 用 24 fps / 240 frames）：

```text
- 1920×1080, 24 fps, exactly 10.000 s (240 frames), H.264 MP4 with stereo AAC audio (48 kHz), …
```

竖屏（18-hanazi 用）：

```text
- 1080×1920, 30 fps, exactly 10.000 s (300 frames), H.264 MP4 with stereo AAC audio (48 kHz), …
```

> 改尺寸/时长就改这一段，技法部分不动。竖屏必须重排构图，不是把横屏裁一刀。

## 固定收尾（逐字，15 份完全相同）

```text
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

## 组装 / 改写规则

- **只换 Creative seed**：故事线、品牌名（必须虚构）、文案、配色、落版 logo。
- **可改 Output**：尺寸、帧率、时长——但改完要重新核对构图与节奏。
- **绝不删 Signature features**：这是风格被一眼认出来的依据。
- **提示词正文用英文**，风格说明与文案用中文；中文上屏文案要地道、标点规范。
- 每次生成本来就不可能一次到位：原片都是「制作 → 独立评审 → 修改」跑了两轮，
  评审提示词见 `references/rubric.md`（同 `vendor/rubric.md`）。
