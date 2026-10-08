"""曲库：背景音乐只从用户的歌单里选，不生成。

  bgm-analysis.json  (bgm-ingest.py)  tempo / beats / energy / sections / loudness
  bgm-tags.json      (tagging pass)   categories / mood / energy / vocal / copyright / use
  -> MG视频工作台/bgm.json             merged, slim; read by the workbench page and `mgw bgm-list`

A film's soundtrack is a cue plan (bgm-plan.json) written by the Agent:

  {"cues": [{"song": "qq-…", "start": 0, "end": 12.5, "from": 40.0,
             "fade_in": 0.3, "fade_out": 1.0, "gain_db": 0, "why": "开头钩子，用副歌抓人"}, …]}

start/end are film seconds; `from` is the offset inside the song. Cues may be any length and any
number; consecutive cues crossfade (the earlier cue keeps playing for its fade_out).
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
APPDIR = HERE.parents[3] / "MG视频工作台"
BGM_DIR = APPDIR / "bgm"
INDEX = APPDIR / "bgm.json"
HISTORY = APPDIR / "bgm-history.json"
ANALYSIS = HERE / "bgm-analysis.json"
TAGS = HERE / "bgm-tags.json"

CATEGORIES = ["欢快搞怪", "轻快日常", "温馨治愈", "抒情钢琴", "激昂燃向", "史诗大气",
              "科技电子", "悬疑紧张", "复古爵士", "异域风情", "节日欢庆", "动漫游戏"]
SR = 48000
SONG_LUFS = -20.0       # every song is levelled to this before mixing, so no song is louder than another


def _load(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def export_index() -> dict:
    an, tags = _load(ANALYSIS, {}), _load(TAGS, {})
    songs = []
    for sid, a in an.items():
        if "duration" not in a:
            continue
        t = tags.get(sid, {})
        songs.append({
            "id": sid, "name": a["name"], "artist": a["artist"], "album": a.get("album", ""),
            "file": a["file"], "duration": a["duration"], "bpm": a.get("bpm"),
            "lufs": a.get("lufs"), "preview_start": a.get("preview_start", 0),
            "intro_end": a.get("intro_end", 0), "beat_period": a.get("beat_period"),
            "energy_avg": a.get("energy_avg"),
            "sections": a.get("sections", []),
            "categories": [c for c in t.get("categories", []) if c in CATEGORIES] or ["轻快日常"],
            "mood": t.get("mood", ""), "energy": t.get("energy") or _energy_word(a.get("energy_avg")),
            "vocal": t.get("vocal", "none"), "copyright_risk": bool(t.get("copyright_risk")),
            "use": t.get("use", ""),
        })
    songs.sort(key=lambda s: (s["categories"][0], s["name"]))
    data = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "categories": CATEGORIES,
            "count": len(songs), "songs": songs}
    INDEX.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return data


def _energy_word(v) -> str:
    v = v or 0
    return "high" if v >= 0.6 else "low" if v < 0.4 else "mid"


def index() -> dict:
    if not INDEX.is_file():
        return export_index()
    return _load(INDEX, {"songs": []})


def songs_by_id() -> dict[str, dict]:
    return {s["id"]: s for s in index().get("songs", [])}


def recent_uses(days: float = 3.0) -> dict[str, int]:
    cut = time.time() - days * 86400
    out: dict[str, int] = {}
    for h in _load(HISTORY, []):
        if h.get("ts", 0) >= cut:
            for sid in h.get("songs", []):
                out[sid] = out.get(sid, 0) + 1
    return out


# -- rendering ----------------------------------------------------------------

_cache: dict[str, np.ndarray] = {}


def _decode(sid: str) -> np.ndarray:
    if sid not in _cache:
        raw = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
                              "-i", str(BGM_DIR / f"{sid}.mp3"), "-f", "f32le", "-ac", "2",
                              "-ar", str(SR), "-"], capture_output=True, check=True).stdout
        _cache[sid] = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
    return _cache[sid]


def _slice(audio: np.ndarray, start: float, n: int, loop_from: float) -> np.ndarray:
    """n frames from `start`; when the song runs out, continue from `loop_from`."""
    out = np.zeros((n, 2), dtype=np.float32)
    pos, i = int(start * SR), 0
    loop = min(int(loop_from * SR), max(0, len(audio) - SR))
    while i < n:
        if pos >= len(audio):
            pos = loop
        take = min(n - i, len(audio) - pos)
        out[i:i + take] = audio[pos:pos + take]
        i += take
        pos += take
    return out


def _fade(seg: np.ndarray, fin: float, fout: float) -> None:
    n = len(seg)
    a, b = min(n, int(fin * SR)), min(n, int(fout * SR))
    if a > 0:
        seg[:a] *= (np.sin(np.linspace(0, np.pi / 2, a)) ** 2)[:, None]
    if b > 0:
        seg[n - b:] *= (np.cos(np.linspace(0, np.pi / 2, b)) ** 2)[:, None]


def validate(plan: dict, duration: float, picked: list[str] | None) -> tuple[list[dict], list[str]]:
    """Return (normalised cues, warnings). Raises ValueError on hard errors."""
    lib = songs_by_id()
    cues = sorted(plan.get("cues", []), key=lambda c: float(c["start"]))
    if not cues:
        raise ValueError("配乐方案里没有任何 cue")
    errs, warns, out = [], [], []
    for i, c in enumerate(cues):
        sid = str(c.get("song", ""))
        if sid not in lib:
            errs.append(f"第 {i + 1} 段：曲库里没有 {sid}")
            continue
        s, e = float(c["start"]), float(c["end"])
        if not (0 <= s < e <= duration + 0.05):
            errs.append(f"第 {i + 1} 段：时间 {s}–{e} 超出 0–{duration}")
            continue
        frm = float(c.get("from", lib[sid].get("preview_start", 0)))
        if frm >= lib[sid]["duration"]:
            errs.append(f"第 {i + 1} 段：from={frm} 超过歌曲长度 {lib[sid]['duration']}")
            continue
        out.append({"song": sid, "start": round(s, 3), "end": round(min(e, duration), 3), "from": round(frm, 3),
                    "fade_in": float(c.get("fade_in", 0.0 if i == 0 else 0.6)),
                    "fade_out": float(c.get("fade_out", 1.5 if i == len(cues) - 1 else 0.8)),
                    "gain_db": float(c.get("gain_db", 0.0)), "why": str(c.get("why", "")),
                    "name": lib[sid]["name"], "artist": lib[sid]["artist"]})
    if picked:
        used = {c["song"] for c in out}
        extra = sorted(used - set(picked))
        missing = [p for p in picked if p not in used]
        if extra:
            errs.append(f"用户选了歌，只能用选中的歌；多用了：{extra}")
    if errs:
        raise ValueError("；".join(errs))
    if picked and missing:
        # 选太多放不下时允许挑着用，但要在汇报里告诉用户
        warns.append(f"用户选的歌有 {len(missing)} 首没用上：{missing}，请在汇报里说明原因")
    for a, b in zip(out, out[1:]):
        if b["start"] - a["end"] > 0.5:
            warns.append(f"{a['end']}–{b['start']} 秒没有配乐")
    if out[0]["start"] > 0.5:
        warns.append(f"开头 0–{out[0]['start']} 秒没有配乐")
    if duration - out[-1]["end"] > 0.5:
        warns.append(f"结尾 {out[-1]['end']}–{duration} 秒没有配乐")
    return out, warns


def render(cues: list[dict], duration: float, out: Path) -> None:
    lib = songs_by_id()
    n_total = int(round(duration * SR))
    mix = np.zeros((n_total, 2), dtype=np.float32)
    for i, c in enumerate(cues):
        song = lib[c["song"]]
        tail = c["fade_out"] if i < len(cues) - 1 else 0.0          # overlap into the next cue
        s0 = int(c["start"] * SR)
        n = min(n_total - s0, int((c["end"] - c["start"] + tail) * SR))
        if n <= 0:
            continue
        seg = _slice(_decode(c["song"]), c["from"], n, song.get("intro_end", 0) or 0)
        gain = SONG_LUFS - (song.get("lufs") or -14.0) + c["gain_db"]
        seg *= np.float32(10 ** (gain / 20))
        _fade(seg, c["fade_in"], c["fade_out"])
        mix[s0:s0 + n] += seg
    peak = float(np.abs(mix).max() or 1)
    if peak > 0.98:
        mix *= 0.98 / peak
    import soundfile as sf
    sf.write(str(out), mix, SR, subtype="PCM_24")


def record_use(job_id: str, cues: list[dict]) -> None:
    hist = _load(HISTORY, [])
    hist = [h for h in hist if h.get("job") != job_id][-300:]
    hist.append({"job": job_id, "ts": time.time(), "songs": sorted({c["song"] for c in cues})})
    HISTORY.write_text(json.dumps(hist, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
