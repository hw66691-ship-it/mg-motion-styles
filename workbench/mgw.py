"""Production CLI for workbench jobs (run via workbench/mgw).

  mgw narrate <job_dir> [--only 003,007] [--detach]   synthesise script.json -> narration/
  mgw assemble <job_dir> [--starts starts.json] [--duration S] [--gap 0.35] [--lead-in 0.6]
                                                     lay lines on the timeline -> voice.wav + timeline.json
  mgw mix <job_dir> --music music.wav [--sfx sfx.wav] [--voice voice.wav] [--out audio.wav]
                                                     duck music under the voice, 48 kHz stereo, -14 LUFS
  mgw status <job_dir> "<phase>" "<message>"          update the workbench progress panel
  mgw voice-clone <audio> --name N [--text "..."] [--lang zh]
                                                      save an authorised reference clip as a voice
  mgw voice-design --name N --prompt "..." [--category female] [--zh "..."] [--en "..."]
                                                      design a new voice from a text description
  mgw bgm-list [--category 欢快搞怪] [--q 关键词] [--ids a,b]   show the song library (曲库)
  mgw bgm-render <job_dir> [--plan bgm-plan.json]     cue plan -> music.wav (songs only from the library)
  mgw render <job_dir> -- <render.mjs args>           render with a machine-wide queue (max 2 at once)
  mgw library-add <job_dir> [--model "Opus 5.5"]       copy final.mp4 + cover into the 作品库
                                                      (MG视频工作台/library/) and index it

narrate goes through the running workbench server when it is up (so only one TTS model is
ever resident); otherwise it loads the model in-process.
The two voice commands always refresh workbench/voices.json + previews/ (the static library the
BigApple preview app reads), and they generate the audition clips for the new voice.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import voicecore as vc  # noqa: E402

# bootstrap-deps.sh puts node / ffmpeg / python3 in ~/.local/bin; make sure subprocesses find them.
os.environ["PATH"] = os.pathsep.join([str(Path.home() / ".local/bin"), "/opt/homebrew/bin", "/usr/local/bin", os.environ.get("PATH", "")])


def _server() -> dict | None:
    info = vc._json_load(vc.SERVER_INFO, None)
    if not info:
        return None
    try:
        with urllib.request.urlopen(info["url"] + "api/health", timeout=3) as r:
            if json.load(r).get("app") == "mg-workbench":
                return info
    except Exception:
        return None
    return None


def _call(info: dict, path: str, body: dict | None = None, timeout: float = 30.0) -> dict:
    req = urllib.request.Request(info["url"] + path.lstrip("/"))
    if body is not None:
        req.data = json.dumps(body).encode("utf-8")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-MGW-Token", info["token"])
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _export_voices() -> None:
    """Refresh the static voice library the BigApple preview app reads."""
    try:
        subprocess.run([sys.executable, str(HERE / "export-voices.py")],
                       check=True, timeout=900)
    except Exception as exc:
        print(f"⚠ 静态音色表刷新失败：{exc}", file=sys.stderr)


def _prime(vid: str, langs: tuple[str, ...], info: dict | None) -> None:
    for lang in langs:
        try:
            if info:
                _call(info, "/api/preview", {"voice": vid, "lang": lang}, timeout=900)
            else:
                vc.preview(vid, lang)
        except Exception as exc:
            print(f"⚠ 试听 {vid}/{lang} 失败：{exc}", file=sys.stderr)


def _log(job: Path, text: str) -> None:
    with open(job / "progress.log", "a", encoding="utf-8") as fh:
        fh.write(f"[{time.strftime('%H:%M:%S')}] {text}\n")


LOCKS = vc.SERVER_INFO.parent / "locks"
RENDER_SLOTS = 2          # 本机最多同时渲染 2 条，其余排队


@contextlib.contextmanager
def _slot_lock(kind: str, slots: int, job: Path, waiting: str):
    """Hold one of `slots` machine-wide locks for `kind`; wait (and say so) while all are busy."""
    LOCKS.mkdir(parents=True, exist_ok=True)
    told = False
    while True:
        for i in range(slots):
            fh = open(LOCKS / f"{kind}-{i}.lock", "a+")   # "a+"：试锁时不清空持有者写的任务名
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                fh.close()
                continue
            fh.seek(0); fh.truncate(); fh.write(f"{job}\n"); fh.flush()
            try:
                yield i
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)
                fh.close()
            return
        if not told:
            busy = []
            for i in range(slots):
                try:
                    busy.append(Path((LOCKS / f"{kind}-{i}.lock").read_text().strip()).name)
                except Exception:
                    pass
            msg = f"{waiting}：正在做 {', '.join(b for b in busy if b) or '其它任务'}"
            print(msg, flush=True)
            if (job / "request.json").is_file():
                _log(job, "⏳ " + msg)
            told = True
        time.sleep(3)


def cmd_narrate(a: argparse.Namespace) -> int:
    job = Path(a.job).resolve()
    only = [s.strip() for s in a.only.split(",")] if a.only else None
    info = _server()
    if info and job.parent.name == "mg-jobs":
        st = _call(info, "/api/narrate", {"id": job.name, "only": only})
        print(f"已交给工作台合成（{job.name}）", flush=True)
        if a.detach:
            return 0
        last = ""
        while st.get("state") == "running":
            time.sleep(3)
            st = _call(info, f"/api/jobs/{job.name}").get("narration") or {}
            msg = f"{st.get('done', 0)}/{st.get('total', 0)} {st.get('message', '')}"
            if msg != last:
                print(msg, flush=True)
                last = msg
        if st.get("state") != "done":
            print(f"失败：{st.get('message')}", file=sys.stderr)
            return 1
    else:
        # 没有工作台服务时在本进程里合成：全机一次只允许一条，避免多个模型同时进内存
        with _slot_lock("tts", 1, job, "配音排队中（同一时间只合成一条）"):
            vc.narrate(job, lambda i, n, m: print(f"{i}/{n} {m}", flush=True), only=only)
    m = vc._json_load(job / "narration" / "manifest.json", {})
    print(json.dumps({"segments": [{k: s[k] for k in ("id", "duration", "text")} for s in m["segments"]],
                      "speech_total": m["speech_total"], "model": m["model"], "note": m.get("note", "")},
                     ensure_ascii=False, indent=1))
    return 0


def cmd_assemble(a: argparse.Namespace) -> int:
    job = Path(a.job).resolve()
    req = vc._json_load(job / "request.json", {})
    duration = a.duration or float(req["duration"])
    starts = vc._json_load(Path(a.starts), {}) if a.starts else None
    res = vc.assemble(job, duration, starts, lead_in=a.lead_in, gap=a.gap)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


def cmd_mix(a: argparse.Namespace) -> int:
    """music.wav + voice.wav -> 48 kHz stereo audio.wav, music ducked under speech, -14 LUFS."""
    import subprocess

    job = Path(a.job).resolve()
    req = vc._json_load(job / "request.json", {})
    dur = a.duration or float(req["duration"])
    voice = Path(a.voice or job / "voice.wav")
    out = Path(a.out or job / "audio.wav")
    # 三层：旁白 > 音效 > 背景音乐。音乐在说话时被侧链压低；音效不压，跟着画面卡点
    sfx = Path(a.sfx) if a.sfx else None
    graph = (
        f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={a.music_db}dB,apad,atrim=0:{dur:.6f}[m];"
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{dur:.6f},asplit=2[v][k];"
        f"[m][k]sidechaincompress=threshold=0.015:ratio={a.duck_ratio}:attack=15:release=450:makeup=1[md];"
    )
    if sfx:
        graph += (f"[2:a]aresample=48000,aformat=channel_layouts=stereo,volume={a.sfx_db}dB,apad,"
                  f"atrim=0:{dur:.6f}[fx];"
                  f"[v][fx][md]amix=inputs=3:normalize=0:duration=first,atrim=0:{dur:.6f}[o]")
    else:
        graph += f"[v][md]amix=inputs=2:normalize=0:duration=first,atrim=0:{dur:.6f}[o]"
    ff = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-loglevel", "error"]
    raw = out.with_name(out.stem + ".premaster.wav")
    ins = ["-i", a.music, "-i", str(voice)] + (["-i", str(sfx)] if sfx else [])
    subprocess.run(ff + ins + ["-filter_complex", graph, "-map", "[o]",
                         "-t", f"{dur:.6f}", "-c:a", "pcm_s16le", str(raw)], check=True)

    def measure(path: Path) -> tuple[str, str]:
        txt = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-af",
                              "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
        tail = txt[txt.rfind("Summary:"):].split("\n")
        get = lambda key: next((l.split(":")[1].strip() for l in tail if l.strip().startswith(key)), "?")
        return get("I:"), get("Peak:")

    # Two-pass: measure, apply static gain to -14 LUFS, then a true-peak limiter at -1 dBTP.
    i_raw, _ = measure(raw)
    gain = -14.0 - float(i_raw.split()[0])
    subprocess.run(ff + ["-i", str(raw), "-af",
                         f"volume={gain:.2f}dB,alimiter=limit=0.89:attack=2:release=60:level=disabled,"
                         f"atrim=0:{dur:.6f}", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(out)],
                   check=True)
    raw.unlink(missing_ok=True)
    lufs, peak = measure(out)
    import soundfile as sf
    print(json.dumps({"out": str(out), "duration": round(sf.info(str(out)).duration, 3),
                      "integrated": lufs, "true_peak": peak}, ensure_ascii=False))
    return 0


def cmd_status(a: argparse.Namespace) -> int:
    job = Path(a.job).resolve()
    cur = vc._json_load(job / "status.json", {})
    cur.update({"state": "done" if a.phase == "done" else "running", "phase": a.phase,
                "message": a.message, "updated": time.strftime("%Y-%m-%d %H:%M:%S")})
    vc._json_dump(job / "status.json", cur)
    _log(job, f"▶ [{a.phase}] {a.message}")
    _progress_update(job)
    return 0


# 花费：BigApple 每轮回复的 token_usage.cost_usd 记在本机 bigapple.db，只读查询，按会话求和
BA_DB = Path.home() / ".bigapple" / "bigapple.db"


def _session_cost(req: dict) -> float | None:
    title = str(req.get("session_title") or "")
    if not title or not BA_DB.is_file():
        return None
    import sqlite3
    started = _started_ts(req)
    try:
        con = sqlite3.connect(f"file:{BA_DB}?mode=ro", uri=True, timeout=3)
        rows = con.execute(
            "select s.id, strftime('%s', s.created_at), "
            "coalesce(sum(json_extract(m.token_usage, '$.cost_usd')), 0) "
            "from chat_sessions s left join messages m on m.session_id = s.id and m.token_usage != '' "
            "where s.title in (?, ?) group by s.id", (title, "[App] " + title)).fetchall()
        con.close()
    except Exception:
        return None
    if not rows:
        return None
    # 同名会话可能有多个：取创建时间离开工时间最近的那个
    sid, _, usd = min(rows, key=lambda r: abs(float(r[1] or 0) - started) if started else 0)
    return round(float(usd or 0), 3)


# 预览页读不到隐藏目录和 mg-jobs 里的状态，这里汇总一份放到可见的 MG视频工作台/progress.json
PROGRESS = HERE.parents[3] / "MG视频工作台" / "progress.json"


def _progress_update(job: Path) -> None:
    try:
        req = vc._json_load(job / "request.json", {})
        st = vc._json_load(job / "status.json", {})
        PROGRESS.parent.mkdir(exist_ok=True)
        with open(PROGRESS.with_suffix(".lock"), "w") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            allp = vc._json_load(PROGRESS, {})
            allp[job.name] = {"state": st.get("state", ""), "phase": st.get("phase", ""),
                              "message": st.get("message", ""), "updated": st.get("updated", ""),
                              "started_ts": req.get("started_ts"), "session_title": req.get("session_title", ""),
                              "final": (job / "final.mp4").is_file(), "cost_usd": _session_cost(req)}
            vc._json_dump(PROGRESS, dict(sorted(allp.items(), reverse=True)[:60]))
            fcntl.flock(lk, fcntl.LOCK_UN)
    except Exception as exc:  # 进度汇总失败不能影响出片
        print(f"progress.json 更新失败：{exc}", file=sys.stderr)


def cmd_voice_clone(a: argparse.Namespace) -> int:
    src = Path(a.audio).expanduser().resolve()
    if not src.is_file():
        print(f"找不到音频：{src}", file=sys.stderr)
        return 2
    info = _server()
    try:
        if info:
            r = _call(info, "/api/voices/clone", {
                "audio_b64": base64.b64encode(src.read_bytes()).decode(),
                "filename": src.name, "name": a.name, "ref_text": a.text,
                "lang": a.lang, "authorised": True}, timeout=600)
        else:
            r = vc.clone_save(src.read_bytes(), src.name, a.name, a.text, True,
                              vc.LANGS.get(a.lang, "Chinese"))
    except Exception as exc:
        print(f"克隆失败：{exc}", file=sys.stderr)
        return 1
    vid = r.get("id") or a.name
    _prime(vid, ("zh", "en"), info)
    _export_voices()
    print(json.dumps({"id": vid, "name": r.get("name"), "kind": "clone"},
                     ensure_ascii=False))
    return 0


def cmd_voice_design(a: argparse.Namespace) -> int:
    info = _server()
    lines = {k: v for k, v in (("zh", a.zh), ("en", a.en)) if v}
    try:
        if info:
            d = _call(info, "/api/voices/design", {"description": a.prompt, "lang": a.lang},
                      timeout=900)
            r = _call(info, "/api/voices/design/save",
                      {"draft": d["draft"], "name": a.name, "category": a.category,
                       "preview_lines": lines}, timeout=300)
        else:
            d = vc.design_draft(a.prompt, a.lang)
            r = vc.design_save(d["draft"], a.name, category=a.category, preview_lines=lines)
    except Exception as exc:
        print(f"造音色失败：{exc}", file=sys.stderr)
        return 1
    vid = r.get("id") or a.name
    _prime(vid, ("zh", "en"), info)
    _export_voices()
    print(json.dumps({"id": vid, "name": r.get("name"), "kind": "design"},
                     ensure_ascii=False))
    return 0


def cmd_bgm_list(a: argparse.Namespace) -> int:
    """Print the song library compactly so the Agent can choose cues."""
    import bgmlib
    if a.refresh:
        bgmlib.export_index()
    songs = bgmlib.index().get("songs", [])
    if a.ids:
        want = {x.strip() for x in a.ids.split(",") if x.strip()}
        songs = [s for s in songs if s["id"] in want]
    if a.category:
        songs = [s for s in songs if a.category in s["categories"]]
    if a.q:
        q = a.q.lower()
        songs = [s for s in songs if q in (s["name"] + s["artist"] + s["album"] + s["mood"]).lower()]
    recent = bgmlib.recent_uses()
    if a.json:
        print(json.dumps(songs, ensure_ascii=False))
        return 0
    for s in songs:
        secs = " ".join(f"{x['start']:.0f}-{x['end']:.0f}{x['level'][0]}" for x in s["sections"])
        flags = (" 🎤" + s["vocal"] if s["vocal"] != "none" else "") + (" ©" if s["copyright_risk"] else "") \
            + (f" 最近用过{recent[s['id']]}次" if s["id"] in recent else "")
        print(f"{s['id']} | {s['name']} - {s['artist']} | {s['duration']:.0f}s {s['bpm'] or '?'}bpm "
              f"{s['energy']} | {'/'.join(s['categories'])} | {s['mood']} | {s['use']}{flags}\n    段落: {secs}")
    print(f"共 {len(songs)} 首（段落 l/m/h = 低/中/高能量，单位秒）")
    return 0


def cmd_bgm_render(a: argparse.Namespace) -> int:
    """bgm-plan.json -> music.wav (only songs from the library), + bgm-used.json for the UI."""
    import bgmlib
    job = Path(a.job).resolve()
    req = vc._json_load(job / "request.json", {})
    dur = a.duration or float(req.get("duration_seconds") or req["duration"])
    plan_path = Path(a.plan) if a.plan else job / "bgm-plan.json"
    plan = vc._json_load(plan_path, None)
    if not plan:
        print(f"找不到配乐方案：{plan_path}", file=sys.stderr)
        return 2
    picked = ((req.get("music") or {}).get("picked")) or None
    try:
        cues, warns = bgmlib.validate(plan, dur, picked)
    except ValueError as exc:
        print(f"配乐方案不合格：{exc}", file=sys.stderr)
        return 1
    out = Path(a.out) if a.out else job / "music.wav"
    bgmlib.render(cues, dur, out)
    used = {"mode": "picked" if picked else "auto", "picked": picked or [], "cues": cues,
            "songs": sorted({c["name"] + " - " + c["artist"] for c in cues})}
    vc._json_dump(job / "bgm-used.json", used)
    bgmlib.record_use(job.name, cues)
    _log(job, f"🎵 配乐 {len(cues)} 段 / {len(used['songs'])} 首歌")
    print(json.dumps({"out": str(out), "cues": len(cues), "songs": used["songs"], "warnings": warns},
                     ensure_ascii=False, indent=1))
    return 0


def cmd_render(a: argparse.Namespace) -> int:
    """node harness/render.mjs …, but at most RENDER_SLOTS renders run on this machine at once."""
    job = Path(a.job).resolve()
    args = list(a.rest)
    if args and args[0] == "--":
        args = args[1:]
    if "--workers" not in args:
        args += ["--workers", "3"]
    vendor = HERE.parent / "vendor"
    with _slot_lock("render", RENDER_SLOTS, job, f"渲染排队中（本机最多同时渲染 {RENDER_SLOTS} 条）") as slot:
        _log(job, f"🎬 开始渲染（槽位 {slot + 1}/{RENDER_SLOTS}）")
        print(f"开始渲染（槽位 {slot + 1}/{RENDER_SLOTS}）", flush=True)
        r = subprocess.run(["node", "harness/render.mjs", *args], cwd=vendor)
    _log(job, "🎬 渲染结束" + ("" if r.returncode == 0 else f"（失败，退出码 {r.returncode}）"))
    return r.returncode


# 作品库：每支成片复制一份到 <project>/MG视频工作台/library/，并登记进 library.json
LIBRARY = HERE.parents[3] / "MG视频工作台" / "library"
LIBRARY_INDEX = LIBRARY.parent / "library.json"


def _media_seconds(p: Path) -> float:
    """Real duration via ffmpeg (the local ffprobe is a shim)."""
    try:
        err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p)], capture_output=True,
                             text=True, timeout=30).stderr
        h, m, s = err.split("Duration: ", 1)[1].split(",", 1)[0].split(":")
        return round(int(h) * 3600 + int(m) * 60 + float(s), 2)
    except Exception:
        return 0.0


def _started_ts(req: dict) -> float:
    if req.get("started_ts"):
        return float(req["started_ts"])
    raw = str(req.get("created", ""))
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):  # 本地服务 / 预览页 toLocaleString
        try:
            return time.mktime(time.strptime(raw, fmt))
        except ValueError:
            continue
    return 0.0


def cmd_library_add(a: argparse.Namespace) -> int:
    job = Path(a.job).resolve()
    final = job / "final.mp4"
    if not final.is_file():
        print(f"没有成片：{final}", file=sys.stderr)
        return 2
    req = vc._json_load(job / "request.json", {})
    style = req.get("style")
    style_cn = style.get("cn", "") if isinstance(style, dict) else req.get("style_cn", "")
    style_slug = style.get("slug", "") if isinstance(style, dict) else str(style or "")
    title = ""
    try:
        title = next((l[2:].strip() for l in (job / "brief.md").read_text(encoding="utf-8").splitlines()
                      if l.startswith("# ")), "")
    except Exception:
        pass
    idea = str(req.get("idea", ""))
    LIBRARY.mkdir(parents=True, exist_ok=True)
    vid_name = f"{job.name}.mp4"
    shutil.copy2(final, LIBRARY / vid_name)
    cover_name = ""
    for c in ("cover.png", "cover.jpg"):
        if (job / c).is_file():
            cover_name = f"{job.name}{Path(c).suffix}"
            shutil.copy2(job / c, LIBRARY / cover_name)
            break
    started = _started_ts(req)
    voice = req.get("voice") or {}
    entry = {
        "id": job.name, "title": title or idea[:24] or job.name, "idea": idea,
        "style": style_slug, "style_cn": style_cn,
        "model": a.model or req.get("model_label") or req.get("model") or "",
        "seconds": _media_seconds(final),
        "aspect": req.get("aspect", ""), "language": req.get("language", ""),
        "voice": req.get("voice_name") or voice.get("id", ""),
        "created": req.get("created", ""),
        "finished": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(final.stat().st_mtime)),
        "elapsed_min": round((final.stat().st_mtime - started) / 60, 1) if started else None,
        "video": f"library/{vid_name}", "cover": f"library/{cover_name}" if cover_name else "",
        "session": req.get("session_title", ""),
        "music": vc._json_load(job / "bgm-used.json", {}).get("cues", []),
        "music_mode": vc._json_load(job / "bgm-used.json", {}).get("mode", ""),
        "cost_usd": _session_cost(req),
    }
    lib = vc._json_load(LIBRARY_INDEX, [])
    lib = [x for x in lib if x.get("id") != job.name] + [entry]
    lib.sort(key=lambda x: x.get("finished", ""), reverse=True)
    vc._json_dump(LIBRARY_INDEX, lib)
    _progress_update(job)
    # library-add 跑在出片那一轮里面，这一轮的花费要等它结束才记账：后台等会话空闲后再补一次
    subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "cost-refresh", "--wait", job.name],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    print(json.dumps({"library": str(LIBRARY_INDEX), "video": str(LIBRARY / vid_name),
                      "model": entry["model"], "elapsed_min": entry["elapsed_min"]},
                     ensure_ascii=False))
    return 0


def cmd_cost_refresh(a: argparse.Namespace) -> int:
    """Re-read every job's BigApple session cost into progress.json and library.json."""
    jobs = HERE.parents[3] / "mg-jobs"
    if a.wait:
        title = str(vc._json_load(jobs / a.wait / "request.json", {}).get("session_title") or "")
        import sqlite3
        for _ in range(240):                       # 最多等 2 小时
            time.sleep(30)
            try:
                con = sqlite3.connect(f"file:{BA_DB}?mode=ro", uri=True, timeout=3)
                busy = con.execute("select count(*) from chat_sessions where title in (?, ?) "
                                   "and runtime_status = 'running'", (title, "[App] " + title)).fetchone()[0]
                con.close()
            except Exception:
                busy = 0
            if not busy:
                time.sleep(10)
                break
    for d in sorted(jobs.iterdir()) if jobs.is_dir() else []:
        if (d / "request.json").is_file() and (d / "status.json").is_file():
            _progress_update(d)
    lib = vc._json_load(LIBRARY_INDEX, [])
    for x in lib:
        d = jobs / x.get("id", "")
        if (d / "request.json").is_file():
            c = _session_cost(vc._json_load(d / "request.json", {}))
            if c is not None:
                x["cost_usd"] = c
    if lib:
        vc._json_dump(LIBRARY_INDEX, lib)
    print(json.dumps({x["id"]: x.get("cost_usd") for x in lib}, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="mgw")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("narrate"); n.add_argument("job"); n.add_argument("--only", default="")
    n.add_argument("--detach", action="store_true"); n.set_defaults(func=cmd_narrate)
    s = sub.add_parser("assemble"); s.add_argument("job"); s.add_argument("--starts", default="")
    s.add_argument("--duration", type=float, default=0.0); s.add_argument("--gap", type=float, default=0.35)
    s.add_argument("--lead-in", type=float, default=0.6); s.set_defaults(func=cmd_assemble)
    x = sub.add_parser("mix"); x.add_argument("job"); x.add_argument("--music", required=True)
    x.add_argument("--voice", default=""); x.add_argument("--out", default="")
    x.add_argument("--duration", type=float, default=0.0); x.add_argument("--music-db", type=float, default=-4.0)
    x.add_argument("--duck-ratio", type=float, default=6.0); x.add_argument("--sfx", default="")
    x.add_argument("--sfx-db", type=float, default=0.0); x.set_defaults(func=cmd_mix)
    t = sub.add_parser("status"); t.add_argument("job"); t.add_argument("phase"); t.add_argument("message")
    t.set_defaults(func=cmd_status)
    c = sub.add_parser("voice-clone"); c.add_argument("audio")
    c.add_argument("--name", required=True); c.add_argument("--text", default="")
    c.add_argument("--lang", default="zh"); c.set_defaults(func=cmd_voice_clone)
    d = sub.add_parser("voice-design"); d.add_argument("--name", required=True)
    d.add_argument("--prompt", required=True); d.add_argument("--category", default="mine")
    d.add_argument("--zh", default=""); d.add_argument("--en", default="")
    d.add_argument("--lang", default="zh"); d.set_defaults(func=cmd_voice_design)
    lb = sub.add_parser("library-add"); lb.add_argument("job"); lb.add_argument("--model", default="")
    lb.set_defaults(func=cmd_library_add)
    ct = sub.add_parser("cost-refresh"); ct.add_argument("--wait", default="")
    ct.set_defaults(func=cmd_cost_refresh)
    bl = sub.add_parser("bgm-list"); bl.add_argument("--category", default=""); bl.add_argument("--q", default="")
    bl.add_argument("--ids", default=""); bl.add_argument("--json", action="store_true")
    bl.add_argument("--refresh", action="store_true"); bl.set_defaults(func=cmd_bgm_list)
    br = sub.add_parser("bgm-render"); br.add_argument("job"); br.add_argument("--plan", default="")
    br.add_argument("--out", default=""); br.add_argument("--duration", type=float, default=0.0)
    br.set_defaults(func=cmd_bgm_render)
    rd = sub.add_parser("render"); rd.add_argument("job"); rd.add_argument("rest", nargs=argparse.REMAINDER)
    rd.set_defaults(func=cmd_render)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
