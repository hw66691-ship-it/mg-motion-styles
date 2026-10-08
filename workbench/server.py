"""MG workbench server: styles + voices + narration + production jobs, 127.0.0.1 only.

Start with workbench/start.sh (uses ~/local-video-dubbing/venv). Every POST needs the
per-launch token injected into index.html, and the Host header must be loopback, so
other web pages and DNS-rebinding tricks cannot drive the TTS engine or start jobs.
"""

from __future__ import annotations

import base64
import json
import os
import secrets
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import voicecore as vc  # noqa: E402

SKILL = HERE.parent
# <project>/.claude/skills/mg-motion-styles -> <project>
PROJECT = SKILL.parents[2] if SKILL.parent.name == "skills" else SKILL.parent
JOBS = PROJECT / "mg-jobs"
# 作品库（mgw library-add 写入）
APPDIR = PROJECT / "MG视频工作台"
LIBRARY = APPDIR / "library"
CONFIG = Path("~/.config/mg-workbench/config.json").expanduser()
SERVER_INFO = vc.SERVER_INFO
PORT = int(os.environ.get("MGW_PORT", "7870"))
TOKEN = secrets.token_urlsafe(24)
MAX_BODY = 60 * 1024 * 1024

CLAUDE_CANDIDATES = [
    "/Applications/BigApple.app/Contents/Resources/standalone/node_modules/"
    "@anthropic-ai/claude-agent-sdk-darwin-arm64/claude",
]

# ---------------------------------------------------------------------------
# Config (relay key) - stored outside the project, 0600, never sent back whole
# ---------------------------------------------------------------------------


def load_config() -> dict[str, Any]:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(patch: dict[str, Any]) -> dict[str, Any]:
    cfg = load_config()
    for k in ("base_url", "api_key", "model"):
        if k in patch and patch[k] is not None:
            v = str(patch[k]).strip()
            if k == "api_key" and v.startswith("•"):
                continue          # masked value echoed back unchanged
            cfg[k] = v
    if "use_key" in patch:
        cfg["use_key"] = bool(patch["use_key"])
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    os.chmod(CONFIG, 0o600)
    return public_config()


def public_config() -> dict[str, Any]:
    cfg = load_config()
    key = cfg.get("api_key", "")
    return {"base_url": cfg.get("base_url", ""), "model": cfg.get("model") or "claude-opus-5-5",
            "has_key": bool(key), "api_key": ("•" * 8 + key[-4:]) if key else "",
            "use_key": bool(cfg.get("use_key")), "claude": claude_bin() or ""}


def claude_bin() -> str | None:
    for c in CLAUDE_CANDIDATES:
        if Path(c).is_file():
            return c
    found = subprocess.run(["/bin/sh", "-lc", "command -v claude"], capture_output=True, text=True)
    return found.stdout.strip() or None


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def styles() -> list[dict[str, Any]]:
    data = json.loads((HERE / "styles.json").read_text(encoding="utf-8"))
    return data


def parse_duration(raw: str) -> float:
    """'1:30' / '90' / '90s' / '90秒' / '1分30秒' / '2m' -> seconds."""
    s = str(raw).strip().lower().replace("：", ":").replace(" ", "")
    if not s:
        raise ValueError("请填写时长")
    if ":" in s:
        parts = [float(p or 0) for p in s.split(":")]
        sec = 0.0
        for p in parts:
            sec = sec * 60 + p
        return sec
    for unit in ("分钟", "分", "min", "m"):
        if unit in s:
            m, _, rest = s.partition(unit)
            rest = rest.rstrip("秒s") or "0"
            return float(m or 0) * 60 + float(rest)
    return float(s.rstrip("秒s"))


def fmt_duration(sec: float) -> str:
    m, s = divmod(round(sec), 60)
    return f"{m}:{s:02d}"


# ---------------------------------------------------------------------------
# Production jobs
#   mg-jobs/<id>/request.json  what the user asked for (style, idea, duration, voice...)
#   mg-jobs/<id>/brief.md      full instructions for Opus (rendered from brief_template.md)
#   mg-jobs/<id>/status.json   {state, phase, message, updated}
#   mg-jobs/<id>/progress.log  human-readable progress lines
# ---------------------------------------------------------------------------

RUNNING: dict[str, subprocess.Popen] = {}
NARRATIONS: dict[str, dict[str, Any]] = {}


def _restart_self() -> None:
    """Re-exec this server. Used when a TTS call is stuck and cannot be interrupted."""
    time.sleep(0.6)
    os.execv(sys.executable, [sys.executable, str(HERE / "server.py"),
                              "--port", str(PORT), "--no-browser"])


def job_dir(job_id: str) -> Path:
    if not job_id or "/" in job_id or ".." in job_id:
        raise ValueError("bad job id")
    d = JOBS / job_id
    if not d.is_dir():
        raise FileNotFoundError(f"任务不存在: {job_id}")
    return d


def set_status(d: Path, state: str, message: str = "", phase: str = "") -> None:
    cur = vc._json_load(d / "status.json", {})
    cur.update({"state": state, "updated": time.strftime("%Y-%m-%d %H:%M:%S")})
    if message:
        cur["message"] = message
    if phase:
        cur["phase"] = phase
    vc._json_dump(d / "status.json", cur)


def log_line(d: Path, text: str) -> None:
    with open(d / "progress.log", "a", encoding="utf-8") as fh:
        fh.write(f"[{time.strftime('%H:%M:%S')}] {text.strip()}\n")


def music_line(music: dict[str, Any]) -> str:
    picked = music.get("picked") or []
    if not picked:
        return "选歌：用户没选，**从整个曲库里自己找**，按起伏逐段配，首数不限。"
    import bgmlib
    lib = bgmlib.songs_by_id()
    names = "、".join(f"`{p}`（{lib[p]['name']}）" if p in lib else f"`{p}`" for p in picked)
    return (f"选歌：用户选了 {len(picked)} 首，**只能用这些**，尽量都用上、放进合适的位置；"
            f"片子太短放不下时挑最合适的用，并在汇报里说明哪几首没用上、为什么：{names}")


def render_brief(req: dict[str, Any], d: Path) -> str:
    tpl = (HERE / "brief_template.md").read_text(encoding="utf-8")
    style = req["style"]
    w, h = (1080, 1920) if req["aspect"] == "9:16" else (1920, 1080)
    fields = {
        "JOB_DIR": str(d), "SKILL_DIR": str(SKILL), "WORKBENCH": str(HERE),
        "STYLE_SLUG": style["slug"], "STYLE_NAME": f"{style['cn']}（{style['en']}）",
        "IDEA": req["idea"], "DURATION": f"{req['duration']:.3f}",
        "DURATION_HUMAN": fmt_duration(req["duration"]), "ASPECT": req["aspect"],
        "WIDTH": str(w), "HEIGHT": str(h), "LANG": vc.LANG_LABELS.get(req["language"], req["language"]),
        "VOICE": req["voice"]["id"], "SUBTITLES": "开启（自动生成并烧进画面）" if req["subtitles"] else "关闭",
        "PYTHON": sys.executable, "MUSIC": music_line(req.get("music") or {}),
    }
    for k, v in fields.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    return tpl


_refresh_timer: threading.Timer | None = None


def refresh_preview_copy(delay: float = 8.0) -> None:
    """改完音色设置后，几秒内（合并连续拖动）在后台刷新 BigApple 预览用的静态音色表和试听。"""
    global _refresh_timer
    if _refresh_timer:
        _refresh_timer.cancel()
    def run() -> None:
        try:
            subprocess.run([sys.executable, str(HERE / "export-voices.py")], timeout=1800,
                           env={**os.environ, "PYTHONPATH": os.environ.get("PYTHONPATH", "")},
                           capture_output=True)
        except Exception as exc:
            print(f"⚠ 刷新预览音色表失败：{exc}", file=sys.stderr)
    _refresh_timer = threading.Timer(delay, run)
    _refresh_timer.daemon = True
    _refresh_timer.start()


def kickoff_prompt(d: Path) -> str:
    label = vc._json_load(d / "request.json", {}).get("model_label") or ""
    tip = f"（工作台选的出片模型：{label}。请先在 BigApple 对话里把模型切到它再发送。）\n" if label else ""
    return (f"{tip}用 mg-motion-styles skill 完成这个视频制作任务：先完整阅读 {d}/brief.md，"
            f"然后按里面的步骤一路做到 {d}/final.mp4，中途不要停下来问我。")


def create_job(body: dict[str, Any]) -> dict[str, Any]:
    idea = str(body.get("idea", "")).strip()
    if not idea:
        raise ValueError("请先写下你对这支视频的想法")
    duration = parse_duration(body.get("duration", ""))
    if duration < 3:
        raise ValueError("时长至少 3 秒")
    style = next((s for s in styles() if s["slug"] == body.get("style")), None)
    if style is None:
        raise ValueError("请选择风格")
    voice_id = str(body.get("voice") or "")
    vc.get_voice(voice_id)
    settings = {**vc.get_settings(voice_id), **(body.get("voice_settings") or {})}
    lang = body.get("language") if body.get("language") in vc.LANGS else "zh"
    aspect = "9:16" if body.get("aspect") == "9:16" else "16:9"
    job_id = time.strftime("%Y%m%d-%H%M%S") + "-" + style["slug"].split("-", 1)[-1]
    d = JOBS / job_id
    d.mkdir(parents=True)
    req = {"id": job_id, "created": time.strftime("%Y-%m-%d %H:%M:%S"),
           "style": {k: style[k] for k in ("slug", "cn", "en", "recipe")},
           "idea": idea, "duration": duration, "duration_human": fmt_duration(duration),
           "aspect": aspect, "language": lang, "subtitles": bool(body.get("subtitles", True)),
           "voice": {"id": voice_id, "settings": settings},
           "model": str(body.get("model") or ""), "model_label": str(body.get("model_label") or ""),
           "music": {"picked": [str(x) for x in ((body.get("music") or {}).get("picked") or [])]},
           "started_ts": int(time.time())}
    vc._json_dump(d / "request.json", req)
    (d / "brief.md").write_text(render_brief(req, d), encoding="utf-8")
    set_status(d, "created", "任务已创建", "queued")
    log_line(d, f"创建任务：{style['cn']} · {fmt_duration(duration)} · {aspect} · 音色 {voice_id}")
    if body.get("dispatch") == "agent":
        # 页面直接调 BigApple /ba/v1 开会话；这里只备好任务目录和开工指令
        set_status(d, "created", "正在交给 BigApple…", "dispatch")
        return {"id": job_id, "mode": "agent", "prompt": agent_prompt(d), "project": str(PROJECT)}
    return start_job(job_id)


def agent_prompt(d: Path) -> str:
    return (f"【MG 视频工作台任务】用 mg-motion-styles skill 完成这个视频制作任务：先完整阅读 {d}/brief.md，"
            f"然后按里面的步骤一路做到 {d}/final.mp4。这个会话就是这支片的制作现场，中途不要停下来问我。"
            f"每进入一个阶段都要跑 brief 里的 mgw status 命令，工作台靠它显示进度。"
            f"完成后最后一段用固定格式列出成片和封面的绝对路径：\n"
            f"文件已生成，点击下面路径打开：\n<绝对路径，每行一个>\n如果无法打开，请回复“帮我打开”。")


def record_dispatch(job_id: str, b: dict[str, Any]) -> dict[str, Any]:
    d = job_dir(job_id)
    info = {k: str(b.get(k) or "") for k in ("session_id", "request_id", "model", "title")}
    info["ts"] = int(time.time())
    vc._json_dump(d / "session.json", info)
    set_status(d, "running", "已交给 BigApple 开工", "dispatch")
    log_line(d, f"🧠 已交给 BigApple（{info['title'] or info['session_id']}）")
    return job_info(d)


def record_finish(job_id: str, b: dict[str, Any]) -> dict[str, Any]:
    d = job_dir(job_id)
    st = vc._json_load(d / "status.json", {})
    if b.get("error"):
        if st.get("state") not in ("done", "stopped"):
            set_status(d, "failed", f"BigApple 返回错误：{b['error']}", "failed")
    elif (d / "final.mp4").is_file():
        if st.get("state") != "done":
            set_status(d, "done", "成片完成", "done")
    elif st.get("state") == "running":
        set_status(d, "failed", "BigApple 这一轮结束了，但没有产出 final.mp4", "failed")
    if b.get("text"):
        (d / "agent-reply.md").write_text(str(b["text"]), encoding="utf-8")
    return job_info(d)


def start_job(job_id: str) -> dict[str, Any]:
    d = job_dir(job_id)
    cfg = load_config()
    if cfg.get("use_key") and cfg.get("api_key") and cfg.get("base_url") and claude_bin():
        return run_headless(d, cfg)
    prompt = kickoff_prompt(d)
    subprocess.run(["pbcopy"], input=prompt.encode("utf-8"))
    subprocess.Popen(["open", "bigapple://open"])
    set_status(d, "handoff", "开工指令已复制，在 BigApple 对话里粘贴发送即可", "handoff")
    log_line(d, "未配置 Key：已复制开工指令并唤起 BigApple")
    return {"id": job_id, "mode": "handoff", "prompt": prompt}


def _child_env(cfg: dict[str, Any]) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("ANTHROPIC_", "CLAUDE_CODE_")) and k != "PYTHONPATH"}
    home = str(Path.home())
    env["PATH"] = ":".join([f"{home}/.local/bin", "/opt/homebrew/bin", "/usr/local/bin",
                            env.get("PATH", "/usr/bin:/bin")])
    model = cfg.get("model") or "claude-opus-5-5"
    env.update({
        "ANTHROPIC_BASE_URL": cfg["base_url"].rstrip("/"),
        # Relays differ on which header they read; send the key both ways.
        "ANTHROPIC_API_KEY": cfg["api_key"], "ANTHROPIC_AUTH_TOKEN": cfg["api_key"],
        "ANTHROPIC_MODEL": model, "ANTHROPIC_DEFAULT_OPUS_MODEL": model,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": model, "ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
        "CLAUDE_CODE_SUBAGENT_MODEL": model,
        "BASH_DEFAULT_TIMEOUT_MS": "600000", "BASH_MAX_TIMEOUT_MS": "3600000",
        "MGW_JOB": "1",
    })
    return env


def _describe_tool(block: dict[str, Any]) -> str:
    name = block.get("name", "tool")
    inp = block.get("input") or {}
    hint = inp.get("description") or inp.get("command") or inp.get("file_path") or inp.get("path") or ""
    hint = str(hint).replace("\n", " ")
    return f"⚙ {name}: {hint[:120]}" if hint else f"⚙ {name}"


def preflight(cfg: dict[str, Any]) -> None:
    """One 1-token request so a wrong relay URL / key fails in seconds, not after 10 silent retries."""
    import urllib.error
    import urllib.request

    body = json.dumps({"model": cfg.get("model") or "claude-opus-5-5", "max_tokens": 1,
                       "messages": [{"role": "user", "content": "ping"}]}).encode("utf-8")
    req = urllib.request.Request(cfg["base_url"].rstrip("/") + "/v1/messages", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("x-api-key", cfg["api_key"])
    req.add_header("Authorization", f"Bearer {cfg['api_key']}")
    try:
        urllib.request.urlopen(req, timeout=20).read()
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise PermissionError(f"中转站拒绝了这个 Key（HTTP {exc.code}），请在「设置」里检查") from exc
        if exc.code == 404:
            raise ValueError("中转站地址不对（/v1/messages 返回 404），Base URL 一般不需要带 /v1") from exc
        # 400/429/5xx: the relay is reachable and the key was accepted far enough; let the CLI handle it.
    except Exception as exc:
        raise ValueError(f"连不上中转站 {cfg['base_url']}：{exc}") from exc


def run_headless(d: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    job_id = d.name
    if job_id in RUNNING and RUNNING[job_id].poll() is None:
        return {"id": job_id, "mode": "headless", "already": True}
    try:
        preflight(cfg)
    except Exception as exc:
        set_status(d, "failed", str(exc), "preflight")
        log_line(d, f"❌ 启动前检查失败：{exc}")
        raise
    cmd = [claude_bin(), "-p", kickoff_prompt(d), "--output-format", "stream-json", "--verbose",
           "--model", cfg.get("model") or "claude-opus-5-5", "--dangerously-skip-permissions",
           "--add-dir", str(d)]
    raw = open(d / "claude-stream.jsonl", "ab")
    proc = subprocess.Popen(cmd, cwd=str(PROJECT), env=_child_env(cfg), stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
    RUNNING[job_id] = proc
    vc._json_dump(d / "runner.json", {"pid": proc.pid, "started": time.time()})
    set_status(d, "running", "Opus 5.5 已开工", "start")
    log_line(d, "已用中转 Key 在后台启动 Claude Code（无人值守）")

    def pump() -> None:
        final = None
        for line in proc.stdout:            # type: ignore[union-attr]
            raw.write(line); raw.flush()
            try:
                ev = json.loads(line)
            except Exception:
                txt = line.decode("utf-8", "replace").strip()
                if txt:
                    log_line(d, txt[:300])
                continue
            if ev.get("type") == "assistant":
                for block in ev.get("message", {}).get("content", []):
                    if block.get("type") == "text" and block.get("text", "").strip():
                        log_line(d, block["text"].strip().splitlines()[0][:300])
                    elif block.get("type") == "tool_use":
                        log_line(d, _describe_tool(block))
            elif ev.get("type") == "system" and ev.get("subtype") == "api_retry":
                log_line(d, f"⚠ 接口重试 {ev.get('attempt')}/{ev.get('max_retries')}"
                            f"（{ev.get('error_status') or ev.get('error') or '网络错误'}）")
            elif ev.get("type") == "result":
                final = ev
        code = proc.wait()
        raw.close()
        ok = (d / "final.mp4").is_file() and final is not None and not final.get("is_error")
        if ok:
            set_status(d, "done", "成片已完成", "done")
            log_line(d, "✅ 完成：final.mp4")
        elif vc._json_load(d / "status.json", {}).get("state") != "stopped":
            reason = (final or {}).get("result") or f"进程退出码 {code}"
            set_status(d, "failed", str(reason)[:300], "failed")
            log_line(d, f"❌ 未完成：{str(reason)[:300]}")

    threading.Thread(target=pump, daemon=True).start()
    return {"id": job_id, "mode": "headless"}


def stop_job(job_id: str) -> dict[str, Any]:
    d = job_dir(job_id)
    proc = RUNNING.get(job_id)
    pid = proc.pid if proc else vc._json_load(d / "runner.json", {}).get("pid")
    if pid:
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
    set_status(d, "stopped", "已手动停止", "stopped")
    log_line(d, "⏹ 已停止")
    return {"id": job_id, "stopped": True}


def _alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def job_info(d: Path, tail: int = 40) -> dict[str, Any]:
    req = vc._json_load(d / "request.json", {})
    st = vc._json_load(d / "status.json", {})
    dispatched = (d / "session.json").is_file()
    if st.get("state") == "running" and dispatched:
        pass                                  # BigApple 会话在干活，进度由 mgw status 写入
    elif st.get("state") == "running" and d.name not in RUNNING \
            and not _alive(vc._json_load(d / "runner.json", {}).get("pid")):
        st["state"] = "done" if (d / "final.mp4").is_file() else "failed"
        st.setdefault("message", "工作台重启前已结束")
    elif st.get("state") in ("handoff", "created") and (d / "final.mp4").is_file():
        st["state"] = "done"
    try:
        lines = (d / "progress.log").read_text(encoding="utf-8").splitlines()[-tail:]
    except Exception:
        lines = []
    final = d / "final.mp4"
    return {"id": d.name, "request": req, "status": st, "log": lines, "dir": str(d),
            "final": str(final) if final.is_file() else "",
            "narration": NARRATIONS.get(d.name),
            "music": vc._json_load(d / "bgm-used.json", {}).get("cues", []),
            "session": vc._json_load(d / "session.json", {})}


def list_jobs() -> list[dict[str, Any]]:
    if not JOBS.is_dir():
        return []
    dirs = sorted((p for p in JOBS.iterdir() if (p / "request.json").is_file()), reverse=True)
    return [job_info(p, tail=6) for p in dirs[:40]]


def start_narration(job_id: str, only: list[str] | None = None) -> dict[str, Any]:
    d = job_dir(job_id)
    cur = NARRATIONS.get(job_id)
    if cur and cur.get("state") == "running":
        return cur
    state: dict[str, Any] = {"state": "running", "done": 0, "total": 0, "message": "排队中"}
    NARRATIONS[job_id] = state

    def prog(i: int, n: int, msg: str) -> None:
        state.update(done=i, total=n, message=msg)

    def work() -> None:
        try:
            m = vc.narrate(d, prog, only=only)
            state.update(state="done", message=f"完成：{len(m['segments'])} 句，纯语音 {m['speech_total']}s",
                         speech_total=m["speech_total"], note=m.get("note", ""))
            log_line(d, f"🎙 旁白合成完成：{len(m['segments'])} 句 / {m['speech_total']}s")
        except Exception as exc:
            state.update(state="failed", message=f"{type(exc).__name__}: {exc}"[:400])
            log_line(d, f"🎙 旁白合成失败：{exc}")

    threading.Thread(target=work, daemon=True).start()
    return state


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp",
        ".wav": "audio/wav", ".mp3": "audio/mpeg", ".mp4": "video/mp4", ".svg": "image/svg+xml"}
LOOPBACK = {"127.0.0.1", "localhost", "[::1]"}


def voices_payload(lang: str) -> dict[str, Any]:
    payload = vc.voices_payload(lang)
    for v in payload["voices"]:
        try:
            p = vc.preview(v["id"], lang, generate=False)
        except Exception:
            p = {"file": None, "text": vc.preview_line(v["id"], lang)}
        v["preview"] = p["file"]
        v["preview_text"] = p["text"]
    payload["instruct_model"] = vc.instruct_model_ready()
    payload["design_model"] = vc.design_model_ready()
    payload["langs"] = vc.LANG_LABELS
    return payload


class Handler(BaseHTTPRequestHandler):
    server_version = "MGWorkbench/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:  # keep the terminal quiet
        pass

    # -- helpers -----------------------------------------------------------

    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        return host in LOOPBACK

    def _json(self, payload: Any, code: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _file(self, path: Path, root: Path) -> None:
        try:
            path = path.resolve()
            path.relative_to(root.resolve())
        except Exception:
            return self._json({"error": "forbidden"}, 403)
        if not path.is_file():
            return self._json({"error": "not found"}, 404)
        size = path.stat().st_size
        ctype = MIME.get(path.suffix.lower(), "application/octet-stream")
        start, end = 0, size - 1
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):        # Safari needs ranges for <video>/<audio>
            a, _, b = rng[6:].partition("-")
            start = int(a) if a else max(0, size - int(b))
            end = int(b) if a and b else size - 1
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        with open(path, "rb") as fh:
            fh.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = fh.read(min(1 << 20, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)

    def _body(self) -> dict[str, Any]:
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            raise ValueError("上传内容过大（上限 60MB）")
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    # -- GET ---------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        if not self._host_ok():
            return self._json({"error": "bad host"}, 403)
        url = urlparse(self.path)
        p = unquote(url.path)
        q = dict(x.split("=", 1) for x in url.query.split("&") if "=" in x)
        try:
            if p in ("/", "/index.html"):
                html = (HERE / "index.html").read_text(encoding="utf-8").replace("__MGW_TOKEN__", TOKEN).replace("__MGW_PROJECT__", str(PROJECT))
                data = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return self.wfile.write(data)
            if p.startswith("/covers/"):
                return self._file(HERE / p.lstrip("/"), HERE / "covers")
            if p.startswith("/previews/"):
                return self._file(vc.PREVIEWS / p[len("/previews/"):], vc.PREVIEWS)
            if p.startswith("/drafts/"):
                return self._file(vc.DRAFTS / p[len("/drafts/"):], vc.DRAFTS)
            if p.startswith("/jobs/"):
                return self._file(JOBS / p[len("/jobs/"):], JOBS)
            if p.startswith("/library/"):
                return self._file(LIBRARY / p[len("/library/"):], LIBRARY)
            if p.startswith("/bgm/"):
                return self._file(APPDIR / "bgm" / p[len("/bgm/"):], APPDIR / "bgm")
            if p == "/api/bgm":
                return self._json(vc._json_load(APPDIR / "bgm.json", {"songs": []}))
            if p == "/api/library":
                return self._json(vc._json_load(APPDIR / "library.json", []))
            if p == "/api/health":
                return self._json({"ok": True, "app": "mg-workbench", "engine": vc.engine().status()})
            if p == "/api/styles":
                return self._json(styles())
            if p == "/api/voices":
                return self._json(voices_payload(unquote(q.get("lang", "zh"))))
            if p == "/api/config":
                return self._json(public_config())
            if p == "/api/jobs":
                return self._json(list_jobs())
            if p == "/api/build":
                return self._json(vc.build_state())
            if p.startswith("/api/jobs/"):
                return self._json(job_info(job_dir(p.split("/")[3])))
            return self._json({"error": "not found"}, 404)
        except (FileNotFoundError, KeyError) as exc:
            return self._json({"error": str(exc)}, 404)
        except Exception as exc:
            return self._json({"error": f"{type(exc).__name__}: {exc}"}, 500)

    # -- POST --------------------------------------------------------------

    def do_POST(self) -> None:  # noqa: N802
        if not self._host_ok() or self.headers.get("X-MGW-Token") != TOKEN:
            return self._json({"error": "forbidden"}, 403)
        p = urlparse(self.path).path
        try:
            b = self._body()
            if p == "/api/preview":
                return self._json(vc.preview(b["voice"], b.get("lang", "zh"),
                                             settings=b.get("settings"), text=b.get("text", "")))
            if p == "/api/voices/settings":
                res = vc.save_settings(b["voice"], b.get("settings") or {})
                refresh_preview_copy()
                return self._json(res)
            if p == "/api/voices/delete":
                vc.delete_voice(b["voice"])
                return self._json({"ok": True})
            if p == "/api/voices/design":
                return self._json(vc.design_draft(b.get("description", ""), b.get("lang", "zh")))
            if p == "/api/voices/design/save":
                return self._json(vc.design_save(b["draft"], b.get("name", ""), b.get("replace", ""),
                                                 b.get("category", ""), b.get("preview_lines")))
            if p == "/api/voices/meta":
                return self._json(vc.set_voice_meta(b["voice"], b.get("patch") or {}))
            if p == "/api/previews/prime":
                langs = b.get("langs") or ["zh", "en"]
                vc.start_build(langs=langs, voice_ids=b.get("voices"))
                return self._json(vc.build_state())
            if p == "/api/build/start":
                return self._json(vc.start_build(langs=b.get("langs") or ["zh", "en"],
                                                 voice_ids=b.get("voices"),
                                                 refresh=bool(b.get("refresh"))))
            if p == "/api/engine/reset":
                # 合成卡住时（例如克隆的参考文本对不上）线程无法中断，直接重开服务进程。
                payload = {"ok": True, "message": "正在重启语音引擎…"}
                self._json(payload)
                threading.Thread(target=_restart_self, daemon=True).start()
                return
            if p == "/api/voices/clone":
                audio = base64.b64decode(b.get("audio_b64", ""))
                return self._json(vc.clone_save(audio, b.get("filename", "ref.wav"), b.get("name", ""),
                                                b.get("ref_text", ""), bool(b.get("authorised")),
                                                vc.LANGS.get(b.get("lang", "zh"), "Chinese")))
            if p == "/api/config":
                return self._json(save_config(b))
            if p == "/api/jobs":
                return self._json(create_job(b))
            if p == "/api/jobs/start":
                return self._json(start_job(b["id"]))
            if p == "/api/jobs/dispatched":
                return self._json(record_dispatch(b["id"], b))
            if p == "/api/jobs/finished":
                return self._json(record_finish(b["id"], b))
            if p == "/api/jobs/stop":
                return self._json(stop_job(b["id"]))
            if p == "/api/jobs/reveal":
                d = job_dir(b["id"])
                target = d / "final.mp4"
                subprocess.Popen(["open", "-R", str(target)] if target.is_file() else ["open", str(d)])
                return self._json({"ok": True})
            if p == "/api/jobs/copy-prompt":
                prompt = kickoff_prompt(job_dir(b["id"]))
                subprocess.run(["pbcopy"], input=prompt.encode("utf-8"))
                subprocess.Popen(["open", "bigapple://open"])
                return self._json({"ok": True, "prompt": prompt})
            if p == "/api/narrate":
                return self._json(start_narration(b["id"], b.get("only")))
            return self._json({"error": "not found"}, 404)
        except (PermissionError, ValueError) as exc:
            return self._json({"error": str(exc)}, 400)
        except (FileNotFoundError, KeyError) as exc:
            return self._json({"error": str(exc)}, 404)
        except Exception as exc:
            return self._json({"error": f"{type(exc).__name__}: {exc}"[:600]}, 500)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="MG 视频工作台（仅本机 127.0.0.1）")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    vc.engine()
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}/"
    vc._json_dump(SERVER_INFO, {"url": url, "token": TOKEN, "pid": os.getpid()})
    os.chmod(SERVER_INFO, 0o600)
    print(f"MG 视频工作台已启动：{url}（仅本机可访问，关闭此窗口即停止）", flush=True)
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        SERVER_INFO.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
