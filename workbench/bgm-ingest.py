#!/usr/bin/env python3
"""Ingest the user's song library into the workbench (曲库).

  ~/Desktop/伴奏歌单/*.mp3  ->  <project>/MG视频工作台/bgm/<id>.mp3   (copy, source untouched)
                           ->  workbench/bgm-analysis.json             (tempo, beats, energy, sections, loudness)

Re-run after adding songs; already-analysed files are skipped unless --force.

    PYTHONPATH=$HOME/local-video-dubbing/app \
      $HOME/local-video-dubbing/venv/bin/python bgm-ingest.py [--src DIR] [--force] [--jobs 4]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
APPDIR = HERE.parents[3] / "MG视频工作台"
BGM_DIR = APPDIR / "bgm"
ANALYSIS = HERE / "bgm-analysis.json"
DEFAULT_SRC = Path("~/Desktop/伴奏歌单").expanduser()
ID_RE = re.compile(r"\[([a-z]+-[0-9a-f]+)\]\.mp3$")


def lufs(path: Path) -> float | None:
    txt = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-af", "ebur128",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    tail = txt[txt.rfind("Summary:"):]
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    return float(m.group(1)) if m else None


def analyse(path: Path) -> dict:
    import numpy as np
    import librosa

    y, sr = librosa.load(str(path), sr=22050, mono=True)
    dur = len(y) / sr
    hop = 512
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop)
    tempo = float(np.atleast_1d(tempo)[0])
    beat_t = librosa.frames_to_time(beats, sr=sr, hop_length=hop)

    # energy curve, 1 value per second, normalised 0..1 within the song
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    fps = sr / hop
    n = max(1, int(dur))
    curve = np.array([rms[int(i * fps):int((i + 1) * fps)].mean() if int(i * fps) < len(rms) else 0
                      for i in range(n)])
    curve = curve / (curve.max() or 1)
    centroid = float(librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop).mean())

    # structural sections: agglomerative segmentation on chroma + mfcc, ~1 boundary per 20 s
    feat = np.vstack([librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop),
                      librosa.util.normalize(librosa.feature.mfcc(y=y, sr=sr, hop_length=hop, n_mfcc=13), axis=1)])
    k = int(min(12, max(3, round(dur / 20))))
    try:
        bounds = librosa.segment.agglomerative(feat, k)
        bt = sorted(set([0.0] + [float(t) for t in librosa.frames_to_time(bounds, sr=sr, hop_length=hop)] + [dur]))
    except Exception:
        bt = [0.0, dur]
    # snap boundaries to nearest beat, merge sections shorter than 4 s
    if len(beat_t):
        bt = [0.0] + [float(beat_t[np.argmin(abs(beat_t - t))]) for t in bt[1:-1]] + [dur]
    merged = [bt[0]]
    for t in bt[1:]:
        if t - merged[-1] >= 4 or t == dur:
            merged.append(t)
    sections = []
    for a, b in zip(merged, merged[1:]):
        if b - a < 0.5:
            continue
        e = float(curve[int(a):max(int(a) + 1, int(b))].mean())
        sections.append({"start": round(a, 2), "end": round(b, 2), "energy": round(e, 3)})
    es = sorted(s["energy"] for s in sections) or [0]
    lo, hi = es[len(es) // 3], es[(2 * len(es)) // 3]
    for s in sections:
        s["level"] = "high" if s["energy"] >= hi and s["energy"] > lo else "low" if s["energy"] <= lo else "mid"
    best = max(sections, key=lambda s: s["energy"] * min(1, (s["end"] - s["start"]) / 12)) if sections else None
    intro_end = next((i for i, v in enumerate(curve) if v >= 0.5), 0)
    return {
        "duration": round(dur, 2), "bpm": round(tempo, 1),
        "beats_head": [round(float(t), 3) for t in beat_t[:16]],
        "beat_period": round(60 / tempo, 4) if tempo else None,
        "energy_avg": round(float(curve.mean()), 3), "brightness_hz": round(centroid),
        "energy_curve": [round(float(v), 2) for v in curve],
        "sections": sections, "intro_end": float(intro_end),
        "preview_start": best["start"] if best else 0.0,
        "lufs": lufs(path),
    }


def work(src: str, dst: str) -> tuple[str, dict]:
    sid = ID_RE.search(src).group(1)
    try:
        return sid, analyse(Path(dst))
    except Exception as exc:  # keep going; the song stays usable without analysis
        return sid, {"error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(DEFAULT_SRC))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    src = Path(a.src).expanduser()
    meta_dir = src / "歌词等文件"
    BGM_DIR.mkdir(parents=True, exist_ok=True)
    db = {} if a.force or not ANALYSIS.is_file() else json.loads(ANALYSIS.read_text(encoding="utf-8"))
    todo = []
    for mp3 in sorted(src.glob("*.mp3")):
        m = ID_RE.search(mp3.name)
        if not m:
            print(f"跳过（文件名里没有 id）：{mp3.name}", file=sys.stderr)
            continue
        sid = m.group(1)
        dst = BGM_DIR / f"{sid}.mp3"
        if not dst.is_file() or dst.stat().st_size != mp3.stat().st_size:
            shutil.copy2(mp3, dst)
        meta = {}
        mj = meta_dir / (mp3.stem + ".music.json")
        if mj.is_file():
            meta = json.loads(mj.read_text(encoding="utf-8")).get("song", {})
        name = meta.get("name") or mp3.stem.split(" - ", 1)[-1].rsplit(" [", 1)[0]
        artist = meta.get("artist") or mp3.stem.split(" - ", 1)[0]
        cur = db.get(sid, {})
        cur.update({"id": sid, "name": name, "artist": artist, "album": meta.get("album") or "",
                    "file": f"bgm/{sid}.mp3", "source_name": mp3.name})
        db[sid] = cur
        if "duration" not in cur or "error" in cur:
            todo.append((str(mp3), str(dst)))
    print(f"曲库 {len(db)} 首，待分析 {len(todo)} 首", flush=True)
    done = 0
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        futs = [ex.submit(work, s, d) for s, d in todo]
        for f in as_completed(futs):
            sid, res = f.result()
            db[sid].pop("error", None)
            db[sid].update(res)
            done += 1
            if done % 10 == 0 or done == len(todo):
                ANALYSIS.write_text(json.dumps(db, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                print(f"{done}/{len(todo)}", flush=True)
    ANALYSIS.write_text(json.dumps(db, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    bad = [k for k, v in db.items() if "error" in v]
    print(f"完成：{len(db)} 首，失败 {len(bad)}：{bad[:5]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
