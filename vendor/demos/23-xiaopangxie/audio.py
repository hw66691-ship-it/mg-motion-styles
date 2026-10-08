# 小螃蟹 · 「我陪你看完这场雨」配乐：温暖钢琴叙事 + 雨声铺底，所有击打点对齐 cues.json。
# 78 BPM / F 大调 / Imaj9 - vi9 - IVmaj9 - V6/9，drop=月亮出来的 5.4s，outro=落版 8.6s。
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib', 'audio'))
import mgaudio as mg
from mgaudio import recipes, sfx, theory

HERE = os.path.dirname(os.path.abspath(__file__))
cues = json.load(open(os.path.join(HERE, 'cues.json')))
H_ = cues['hits']
FPS = cues['fps']
T = lambda k: H_[k]

hits = [T('rain'), T('pink_in'), T('together'), T('flower'), T('moon'), T('hearts'), T('lights'), T('title')]

m = recipes.ambient(bpm=cues['bpm'], key=cues['key'], mode='major', flavor='piano',
                    drop=T('moon'), outro=T('title'), hits=tuple(hits), final='Imaj9')
f = m.form
print(f.summary() if hasattr(f, 'summary') else f)
print('tracks:', list(m.tracks))

note = lambda t, i=-1, sh=0: f.chord_at(t, sh)[i]

# ---- 雨：一层很轻的空气噪声铺底，随画面雨势淡出（7.2s 灯亮后收掉）
m.sfx(sfx.whoosh(2.6, 'air', direction=0, peak=0.5), at=T('rain') - 0.35, gain=-9, verb=-8)
m.sfx(sfx.static(3.4, 'radio'), at=T('rain') - 0.30, gain=-26, verb=-10)
m.sfx(sfx.swish(0.30), at=T('rain'), gain=-15, verb=-9)          # 明确雨起的起音
m.group('sfx').automate('gain', [(0, 0), (T('lights') - 0.5, 0), (T('title') - 0.4, -7), (10.0, -14)])

# ---- 脚步：小螃蟹踩着定格节奏走进来（一拍一响，间隔 0.32s）
for i in range(7):
    m.sfx(sfx.click('soft'), at=T('pink_in') - 0.05 + i * 0.155, gain=-15, pan=-0.25 + i * 0.05)
for i in range(7):
    m.sfx(sfx.click('wood'), at=T('rain') + 0.10 + i * 0.155, gain=-17, pan=0.05 + i * 0.05)

# ---- 并肩站定：一记很软的落地
m.sfx(sfx.impact('soft', size=0.7), at=T('together'), gain=-11, verb=-8)

# ---- 头顶开出小花：铃声（F 调内音）
m.sfx(sfx.ding(note(T('flower'), -1, 12)), at=T('flower'), gain=-9, verb=-6)
m.sfx(sfx.sparkle(0.5, density=7, key='F', mode='major_pentatonic', seed=21), at=T('flower') + 0.02, gain=-15, verb=-8)

# ---- 月亮露出：上行渐强 + 柔光击打（drop）
m.sfx(sfx.riser(1.8, 'tonal', note=theory.name(53)), at=T('moon') - 1.8, gain=-13, verb=-8)
m.sfx(sfx.impact('soft', size=1.0), at=T('moon'), gain=-7, verb=-7)
m.sfx(sfx.shimmer_hit(note(T('moon'), -1, 12)), at=T('moon') + 0.01, gain=-12, verb=-7)
m.sfx(sfx.swell(sfx.chime([note(T('moon'), 0, 12)]), 0.9), at=T('moon') - 0.5, gain=-13)

# ---- 心形浮起：两小节魔法音，右左交替
m.sfx(sfx.ding(note(T('hearts'), -1, 12)), at=T('hearts'), gain=-10, verb=-6)
for i in range(5):
    m.sfx(sfx.magic(0.7, key='F', up=True), at=T('hearts') + 0.08 + i * 0.20, gain=-17,
          pan=-0.4 + i * 0.2, verb=-8)

# ---- 城市窗灯波浪式点亮：一串上行叮声（中心向两侧散开）
for i in range(14):
    deg = [1, 2, 3, 4, 5, 6, 7, 8][i % 8]
    m.sfx(sfx.ding(theory.name(65 + deg)), at=T('lights') + i * 0.075, gain=(-10 if i == 0 else -18 + (i % 3)),
          pan=-0.6 + i * 0.09, verb=-6)

# ---- 落版：标题
m.sfx(sfx.chime([note(10.0 - 0.1, -1, 12)]), at=T('title'), gain=-8, verb=-5)
m.sfx(sfx.impact('soft', size=0.85), at=T('title'), gain=-9)

m.master_kw.update(air=2.0, warmth=1.2)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
res = m.export(os.path.join(HERE, 'out/audio.wav'), lufs=-14, tp=-1,
               spectrogram=os.path.join(HERE, 'out/audio_spec.png'))
print({k: res[k] for k in ('duration', 'lufs', 'true_peak', 'stereo_corr', 'longest_gap') if k in res})
print('bands', res.get('bands'))
print('warnings', res.get('warnings'))
print('align', mg.hit_alignment(os.path.join(HERE, 'out/audio.wav'), hits))
