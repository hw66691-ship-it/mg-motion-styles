"""Voice core for the MG workbench: voice library, per-voice settings, previews,
VoiceDesign / clone creation and narration synthesis on the local Qwen3-TTS stack.

Runs inside ~/local-video-dubbing/venv with PYTHONPATH=<lvd>/app (see start.sh).
Exactly one TTS checkpoint is resident at a time; every synthesis call goes
through the single Engine worker so 16 GB machines never load two models.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Callable, Sequence

from lvd import config
from lvd.tts import TTSEngine, list_reference_voices

SR = 24000
HERE = Path(__file__).resolve().parent
CATALOG_FILE = HERE / "voice-catalog.json"
DATA = Path(os.environ.get("MGW_DATA", config.ROOT / "workbench")).expanduser()
PREVIEWS = DATA / "previews"
DRAFTS = DATA / "drafts"
TRASH = DATA / "trash"
SETTINGS_FILE = DATA / "voice-settings.json"
SERVER_INFO = DATA / "server.json"        # {url, token, pid} of the running workbench (0600)
for _d in (DATA, PREVIEWS, DRAFTS, TRASH):
    _d.mkdir(parents=True, exist_ok=True)

IDLE_UNLOAD_S = 600

# Language code used in the UI -> Qwen3-TTS language name.
LANGS = {
    "zh": "Chinese", "en": "English", "ja": "Japanese", "ko": "Korean",
    "de": "German", "fr": "French", "ru": "Russian", "pt": "Portuguese",
    "es": "Spanish", "it": "Italian",
}
LANG_LABELS = {
    "zh": "中文", "en": "English", "ja": "日本語", "ko": "한국어", "de": "Deutsch",
    "fr": "Français", "ru": "Русский", "pt": "Português", "es": "Español", "it": "Italiano",
}

# ~10-character audition lines, written per voice so the timbre difference is obvious.
PREVIEW_LINES: dict[str, dict[str, str]] = {
    "Vivian":   {"zh": "嘿，今天也要元气满满哦！", "en": "Hey, let's make today amazing!"},
    "Serena":   {"zh": "别着急，慢慢来就好。", "en": "Take a breath, you're doing great."},
    "Uncle_Fu": {"zh": "这个故事，要从很久以前说起。", "en": "Let me tell you an old story."},
    "Dylan":    {"zh": "得嘞，咱这就出发！", "en": "Alright, let's get this going!"},
    "Eric":     {"zh": "巴适得很，走起嘛！", "en": "Sounds good, let's roll!"},
    "Ryan":     {"zh": "准备好了吗？节奏起！", "en": "Ready? Let's drop the beat!"},
    "Aiden":    {"zh": "阳光正好，出去走走吧！", "en": "Sun's out, let's go outside!"},
    "Ono_Anna": {"zh": "今天也请多多关照呀！", "en": "Nice to meet you, let's have fun!",
                 "ja": "今日もよろしくね！"},
    "Sohee":    {"zh": "谢谢你一直陪着我。", "en": "Thank you for always being here.",
                 "ko": "항상 곁에 있어 줘서 고마워."},
}
GENERIC_LINES = {
    "zh": "你好，这是我的声音。", "en": "Hi there, this is my voice.",
    "ja": "こんにちは、これが私の声です。", "ko": "안녕하세요, 제 목소리예요.",
    "de": "Hallo, das ist meine Stimme.", "fr": "Bonjour, voici ma voix.",
    "ru": "Привет, это мой голос.", "pt": "Olá, esta é a minha voz.",
    "es": "Hola, esta es mi voz.", "it": "Ciao, questa è la mia voce.",
}
# Longer line used as the reference clip when a voice is designed from text.
DESIGN_REF = {
    "zh": "大家好，很高兴认识你。接下来，就由我来为你讲述这段故事，希望你会喜欢。",
    "en": "Hello, it's great to meet you. I'll be telling you this story today, and I hope you enjoy it.",
}

DEFAULT_SETTINGS = {"rate": 1.0, "pitch": 0.0, "instruct": "", "sample": ""}

# Category a built-in preset belongs to; anything the user creates without an
# explicit category lands in「我的音色」.
PRESET_CATEGORY = {
    "Vivian": "female", "Serena": "female", "Ono_Anna": "foreign", "Sohee": "foreign",
    "Uncle_Fu": "male", "Dylan": "male", "Eric": "male", "Ryan": "male", "Aiden": "male",
}
MINE_CATEGORY = {"id": "mine", "name": "我的音色", "order": 0}


def catalog() -> dict[str, Any]:
    """The shipped voice catalogue: categories + the design specs behind them."""
    return _json_load(CATALOG_FILE, {"categories": [], "voices": []})


def catalog_categories() -> list[dict[str, Any]]:
    cats = [MINE_CATEGORY, *catalog().get("categories", [])]
    return sorted(cats, key=lambda c: c.get("order", 99))


def catalog_voice(voice_id: str) -> dict[str, Any] | None:
    for spec in catalog().get("voices", []):
        if spec["id"] == voice_id:
            return spec
    return None


def catalog_order_map() -> dict[str, int]:
    return {spec["id"]: i for i, spec in enumerate(catalog().get("voices", []))}


def catalog_order(cat_id: str) -> int:
    return {c["id"]: c.get("order", 99) for c in catalog_categories()}.get(cat_id, 99)


def instruct_model_ready() -> bool:
    return config.model_present("preset_1.7b")


def design_model_ready() -> bool:
    return config.model_present("design")


def preview_line(voice_id: str, lang: str) -> str:
    lines = PREVIEW_LINES.get(voice_id)
    if not lines:
        spec = catalog_voice(voice_id)
        lines = (spec or {}).get("preview") or {}
    return lines.get(lang) or GENERIC_LINES.get(lang) or GENERIC_LINES["en"]


def _json_load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _json_dump(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


# ---------------------------------------------------------------------------
# Per-voice settings (rate / pitch / tone description / custom audition line)
# ---------------------------------------------------------------------------

_settings_lock = threading.Lock()


def get_settings(voice_id: str) -> dict[str, Any]:
    stored = _json_load(SETTINGS_FILE, {}).get(voice_id, {})
    return {**DEFAULT_SETTINGS, **{k: v for k, v in stored.items() if k in DEFAULT_SETTINGS}}


def save_settings(voice_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    if "rate" in patch:
        clean["rate"] = min(2.0, max(0.5, float(patch["rate"])))
    if "pitch" in patch:
        clean["pitch"] = min(12.0, max(-12.0, float(patch["pitch"])))
    if "instruct" in patch:
        clean["instruct"] = str(patch["instruct"] or "").strip()[:300]
    if "sample" in patch:
        clean["sample"] = str(patch["sample"] or "").strip()[:120]
    with _settings_lock:
        allset = _json_load(SETTINGS_FILE, {})
        allset[voice_id] = {**DEFAULT_SETTINGS, **allset.get(voice_id, {}), **clean}
        _json_dump(SETTINGS_FILE, allset)
    return get_settings(voice_id)


# ---------------------------------------------------------------------------
# Voice library: 9 presets + saved clone / designed voices
# ---------------------------------------------------------------------------

def list_voices() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for name, meta in config.SPEAKERS.items():
        out.append({
            "id": name, "name": name.replace("_", " "), "kind": "preset",
            "desc": meta["desc"].split(" / ")[0], "native": meta["native"],
            "category": PRESET_CATEGORY.get(name, "mine"),
            "tunable": {"rate": True, "pitch": True, "instruct": instruct_model_ready()},
        })
    for ref in list_reference_voices():
        if not ref.get("authorised"):
            continue
        kind = "design" if ref.get("source") == "design" else "clone"
        spec = catalog_voice(ref["id"]) or {}
        out.append({
            "id": ref["id"], "name": ref.get("name") or ref["id"], "kind": kind,
            "desc": ref.get("design_prompt") or ref.get("note") or "授权克隆的参考音色",
            "native": ref.get("language") or "Chinese",
            "design_prompt": ref.get("design_prompt", ""),
            "category": ref.get("category") or spec.get("category") or "mine",
            "preview_lines": ref.get("preview_lines") or spec.get("preview") or {},
            "tunable": {"rate": True, "pitch": True, "instruct": False,
                        "redesign": kind == "design" and design_model_ready()},
        })
    for v in out:
        v["settings"] = get_settings(v["id"])
    return out


def voices_payload(lang: str = "zh") -> dict[str, Any]:
    """Everything the voice panel needs: the list, categories and build progress."""
    order = catalog_order_map()
    voices = list_voices()
    for v in voices:
        v["preview_text"] = (v.get("preview_lines") or {}).get(lang) or preview_line(v["id"], lang)
    voices.sort(key=lambda v: (catalog_order(v.get("category", "mine")),
                               0 if v["kind"] == "preset" else 1,
                               order.get(v["id"], 500), v["name"]))
    return {"voices": voices, "categories": catalog_categories(), "build": build_state()}


def get_voice(voice_id: str) -> dict[str, Any]:
    if voice_id in config.SPEAKERS:
        return {"id": voice_id, "kind": "preset"}
    for ref in list_reference_voices():
        if ref["id"] == voice_id and ref.get("authorised"):
            return {**ref, "kind": "design" if ref.get("source") == "design" else "clone"}
    raise KeyError(f"未知音色: {voice_id}")


def plan_model(voice: dict[str, Any], settings: dict[str, Any]) -> tuple[str, str]:
    """Pick the checkpoint for this voice. Returns (voice_mode, note)."""
    if voice["kind"] == "preset":
        if settings.get("instruct"):
            if instruct_model_ready():
                return "preset_1.7b", ""
            return "preset", "未安装 1.7B CustomVoice，语气描述已忽略"
        return "preset", ""
    # Clone and designed voices both speak through the Base checkpoint from their
    # reference clip, so every line keeps exactly the same timbre.
    return "clone", ""


# ---------------------------------------------------------------------------
# Engine: one worker thread, one resident checkpoint, priority queue
# ---------------------------------------------------------------------------

class Engine:
    """Serialises every TTS call. Priority 0 = interactive preview, 1 = narration."""

    def __init__(self) -> None:
        self._q: queue.PriorityQueue = queue.PriorityQueue()
        self._seq = itertools.count()
        self._tts: TTSEngine | None = None
        self._mode: str | None = None
        self._last_used = time.time()
        self.busy: str = ""
        self.busy_since = 0.0
        threading.Thread(target=self._loop, name="tts-worker", daemon=True).start()

    def submit(self, fn: Callable[["Engine"], Any], priority: int = 0, label: str = "") -> Any:
        """Run fn(engine) on the worker thread and block until it finishes."""
        done = threading.Event()
        box: dict[str, Any] = {}
        self._q.put((priority, next(self._seq), fn, label, done, box))
        done.wait()
        if "error" in box:
            raise box["error"]
        return box.get("result")

    def _loop(self) -> None:
        while True:
            try:
                item = self._q.get(timeout=30)
            except queue.Empty:
                if self._tts is not None and time.time() - self._last_used > IDLE_UNLOAD_S:
                    self.unload()
                continue
            _prio, _n, fn, label, done, box = item
            self.busy = label or "合成中"
            self.busy_since = time.time()
            try:
                box["result"] = fn(self)
            except Exception as exc:  # surfaced to the caller
                box["error"] = exc
            finally:
                self.busy = ""
                self.busy_since = 0.0
                self._last_used = time.time()
                done.set()

    # -- called on the worker thread only ---------------------------------

    def tts(self, mode: str) -> TTSEngine:
        if self._tts is None or self._mode != mode:
            self.unload()
            self._tts = TTSEngine(voice_mode=mode, device="auto").load(quiet=True)
            self._mode = mode
        return self._tts

    def unload(self) -> None:
        if self._tts is not None:
            self._tts.unload()
        self._tts, self._mode = None, None

    def status(self) -> dict[str, Any]:
        busy_s = round(time.time() - self.busy_since, 1) if self.busy_since else 0.0
        # 参考文本和音频对不上时模型可能一直生成不自停；超过 4 分钟按"卡住"报给前端。
        return {"loaded": self._mode, "busy": self.busy, "busy_seconds": busy_s,
                "stuck": bool(self.busy and busy_s > 240), "queued": self._q.qsize()}


ENGINE: Engine | None = None


def engine() -> Engine:
    global ENGINE
    if ENGINE is None:
        ENGINE = Engine()
    return ENGINE


def _post_process(raw: Path, out: Path, rate: float, pitch: float) -> float:
    """Apply speaking rate / pitch with FFmpeg and return the clip duration."""
    chain: list[str] = []
    tempo = float(rate or 1.0)
    if abs(pitch) > 1e-3:
        factor = 2.0 ** (pitch / 12.0)
        chain += [f"asetrate={int(round(SR * factor))}", f"aresample={SR}"]
        tempo /= factor           # asetrate also changes speed; compensate
    while tempo > 2.0:
        chain.append("atempo=2.0"); tempo /= 2.0
    while tempo < 0.5:
        chain.append("atempo=0.5"); tempo /= 0.5
    if abs(tempo - 1.0) > 1e-3:
        chain.append(f"atempo={tempo:.5f}")
    chain += ["highpass=f=60", "afade=t=in:st=0:d=0.02"]
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-loglevel", "error",
                    "-i", str(raw), "-af", ",".join(chain), "-ar", str(SR), "-ac", "1",
                    "-c:a", "pcm_s16le", str(out)], check=True)
    import soundfile as sf
    return float(sf.info(str(out)).duration)


def synth_to(voice: dict[str, Any], settings: dict[str, Any], text: str, lang: str,
             out: Path) -> dict[str, Any]:
    """Synthesise one line for a voice. Must run on the worker thread (via Engine.submit)."""
    import soundfile as sf

    mode, note = plan_model(voice, settings)
    started = time.time()
    tts = engine().tts(mode)
    if mode == "clone":
        tts.prepare_clone(voice["audio"], voice.get("ref_text", ""))
    wav, sr = tts.synthesize(text, language=LANGS.get(lang, "Auto"), speaker=voice["id"],
                             instruct=settings.get("instruct", "") if mode == "preset_1.7b" else "")
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = out.with_name(out.stem + ".raw.wav")
    sf.write(str(raw), wav, sr, subtype="PCM_16")
    duration = _post_process(raw, out, settings.get("rate", 1.0), settings.get("pitch", 0.0))
    raw.unlink(missing_ok=True)
    return {"duration": round(duration, 3), "model": mode, "note": note,
            "elapsed": round(time.time() - started, 2)}


# ---------------------------------------------------------------------------
# Previews (cached by voice + language + text + settings)
# ---------------------------------------------------------------------------

def _key(*parts: Any) -> str:
    raw = json.dumps(parts, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def preview(voice_id: str, lang: str, settings: dict[str, Any] | None = None,
            text: str = "", generate: bool = True) -> dict[str, Any]:
    voice = get_voice(voice_id)
    st = {**get_settings(voice_id), **(settings or {})}
    own_lines = voice.get("preview_lines") or {}
    text = (text or st.get("sample") or own_lines.get(lang)
            or preview_line(voice_id, lang)).strip()
    mode, _ = plan_model(voice, st)
    ref_mtime = int(Path(voice["audio"]).stat().st_mtime) if voice.get("audio") else 0
    key = _key(voice_id, lang, text, st["rate"], st["pitch"],
               st["instruct"] if mode == "preset_1.7b" else "", mode, ref_mtime)
    out = PREVIEWS / f"{key}.wav"
    if out.is_file():
        return {"file": out.name, "text": text, "cached": True}
    if not generate:
        return {"file": None, "text": text, "cached": False}
    info = engine().submit(lambda e: synth_to(voice, st, text, lang, out),
                           priority=0, label=f"试听 {voice_id}")
    return {"file": out.name, "text": text, "cached": False, **info}


# ---------------------------------------------------------------------------
# Create voices: design from a text description, or clone authorised audio
# ---------------------------------------------------------------------------

def _slug(name: str) -> str:
    s = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name.strip())
    return s.strip("_")[:40] or f"voice_{int(time.time())}"


def design_draft(description: str, lang: str = "zh") -> dict[str, Any]:
    """Generate a reference clip from a description with the 1.7B VoiceDesign model."""
    import soundfile as sf

    description = (description or "").strip()
    if not description:
        raise ValueError("请先写一段音色描述")
    if not design_model_ready():
        raise RuntimeError("未安装 1.7B VoiceDesign 模型")
    lang = lang if lang in DESIGN_REF else "zh"
    ref_text = DESIGN_REF[lang]
    draft_id = f"d{int(time.time() * 1000)}"
    out = DRAFTS / f"{draft_id}.wav"

    def job(e: Engine) -> dict[str, Any]:
        tts = e.tts("design")
        wav, sr = tts.synthesize(ref_text, language=LANGS[lang], instruct=description)
        sf.write(str(out), wav, sr, subtype="PCM_16")
        return {"duration": round(len(wav) / sr, 2)}

    info = engine().submit(job, priority=0, label="设计音色")
    _json_dump(DRAFTS / f"{draft_id}.json",
               {"description": description, "ref_text": ref_text, "language": LANGS[lang]})
    return {"draft": draft_id, "file": f"drafts/{draft_id}.wav", **info}


def _store_voice(src_wav: Path, name: str, payload: dict[str, Any]) -> dict[str, Any]:
    slug = _slug(name)
    dest_dir = config.VOICES_DIR / slug
    n = 2
    while dest_dir.exists():
        dest_dir = config.VOICES_DIR / f"{slug}_{n}"
        n += 1
    dest_dir.mkdir(parents=True)
    dest = dest_dir / f"{dest_dir.name}.wav"
    shutil.copy2(src_wav, dest)
    meta = {"id": dest_dir.name, "name": name.strip() or dest_dir.name, "audio": str(dest),
            "authorised": True, "created": time.strftime("%Y-%m-%d %H:%M:%S"), **payload}
    _json_dump(dest_dir / "voice.json", meta)
    return meta


def design_save(draft_id: str, name: str, replace_id: str = "",
                category: str = "", preview_lines: dict[str, str] | None = None) -> dict[str, Any]:
    wav = DRAFTS / f"{draft_id}.wav"
    meta = _json_load(DRAFTS / f"{draft_id}.json", None)
    if not wav.is_file() or meta is None:
        raise FileNotFoundError("草稿已过期，请重新生成")
    payload = {"ref_text": meta["ref_text"], "language": meta["language"],
               "source": "design", "design_prompt": meta["description"],
               "note": "VoiceDesign 生成，本机自有音色"}
    if category:
        payload["category"] = category
    if preview_lines:
        payload["preview_lines"] = {k: str(v).strip()[:120] for k, v in preview_lines.items() if v}
    if replace_id:
        # Re-designing an existing voice keeps its id and settings.
        old = get_voice(replace_id)
        shutil.copy2(wav, old["audio"])
        merged = {**_json_load(Path(old["meta_path"]), {}), **payload}
        _json_dump(Path(old["meta_path"]), merged)
        return merged
    return _store_voice(wav, name or meta["description"][:12], payload)


def clone_save(audio_bytes: bytes, filename: str, name: str, ref_text: str,
               authorised: bool, language: str = "Chinese") -> dict[str, Any]:
    if not authorised:
        raise PermissionError("必须确认你已获得该声音的使用授权")
    if not name.strip():
        raise ValueError("请给音色起个名字")
    tmp_in = DRAFTS / f"upload_{int(time.time()*1000)}{Path(filename).suffix or '.wav'}"
    tmp_in.write_bytes(audio_bytes)
    tmp_wav = tmp_in.with_suffix(".norm.wav")
    try:
        subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-loglevel", "error",
                        "-i", str(tmp_in), "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le",
                        str(tmp_wav)], check=True)
        import soundfile as sf
        dur = sf.info(str(tmp_wav)).duration
        if dur < 3 or dur > 30:
            raise ValueError(f"参考音频需要 3–30 秒（当前 {dur:.1f} 秒），5–15 秒干净人声最好")
        return _store_voice(tmp_wav, name, {
            "ref_text": ref_text.strip(), "language": language, "source": "clone",
            "note": "用户上传并确认授权的参考音色",
        })
    finally:
        tmp_in.unlink(missing_ok=True)
        tmp_wav.unlink(missing_ok=True)


def delete_voice(voice_id: str) -> None:
    voice = get_voice(voice_id)
    if voice["kind"] == "preset":
        raise ValueError("内置音色不能删除")
    src = Path(voice["meta_path"]).parent
    shutil.move(str(src), str(TRASH / f"{src.name}_{int(time.time())}"))


# ---------------------------------------------------------------------------
# Voice library builder: design the shipped catalogue, then pre-render previews
# ---------------------------------------------------------------------------

_build_lock = threading.Lock()
BUILD: dict[str, Any] = {
    "running": False, "phase": "", "current": "", "total": 0, "done": 0,
    "failed": [], "started": 0.0, "finished": 0.0, "langs": [], "log": [],
    "phase_started": 0.0,
}


def build_state() -> dict[str, Any]:
    with _build_lock:
        st = {**BUILD, "failed": list(BUILD["failed"]), "log": list(BUILD["log"])[-12:]}
    now = st["finished"] or time.time()
    elapsed = now - st["started"] if st["started"] else 0
    # ETA is per phase: the design phase and the preview phase run at very
    # different speeds, so measuring from the whole-build start lies badly.
    phase_elapsed = now - st["phase_started"] if st.get("phase_started") else 0
    st["elapsed"] = round(elapsed, 1)
    st["eta"] = (round(phase_elapsed / st["done"] * (st["total"] - st["done"]), 1)
                 if st["running"] and st["done"] else 0)
    return st


def _build_set(**kw: Any) -> None:
    with _build_lock:
        if "stage" in kw and kw["stage"] != BUILD.get("stage"):
            BUILD["phase_started"] = time.time()
        BUILD.update(kw)


def _build_log(msg: str) -> None:
    with _build_lock:
        BUILD["log"].append(msg)
        del BUILD["log"][:-40]


def _build_fail(msg: str) -> None:
    with _build_lock:
        BUILD["failed"].append(msg)


def _find_voice(voice_id: str) -> dict[str, Any] | None:
    for ref in list_reference_voices():
        if ref["id"] == voice_id:
            return ref
    return None


def set_voice_meta(voice_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    """Update the display name / category / audition lines of a saved voice."""
    voice = get_voice(voice_id)
    if voice["kind"] == "preset":
        raise ValueError("内置音色不能修改")
    meta_path = Path(voice["meta_path"])
    meta = _json_load(meta_path, {})
    if str(patch.get("name", "")).strip():
        meta["name"] = str(patch["name"]).strip()[:40]
    if str(patch.get("category", "")).strip():
        meta["category"] = str(patch["category"]).strip()[:32]
    if isinstance(patch.get("preview_lines"), dict):
        lines = {k: str(v).strip()[:120] for k, v in patch["preview_lines"].items() if v}
        meta["preview_lines"] = {**meta.get("preview_lines", {}), **lines}
    if str(patch.get("desc", "")).strip():
        meta["note"] = str(patch["desc"]).strip()[:120]
    _json_dump(meta_path, meta)
    return meta


def design_one(spec: dict[str, Any], force: bool = False) -> dict[str, Any]:
    """Design one catalogue voice from its text description (skips existing)."""
    existing = _find_voice(spec["id"])
    if existing and not force:
        set_voice_meta(spec["id"], {"name": spec["name"], "category": spec["category"],
                                    "preview_lines": spec.get("preview") or {}})
        return {"id": spec["id"], "skipped": True}
    if not spec.get("prompt"):
        return {"id": spec["id"], "skipped": True}
    draft = design_draft(spec["prompt"], spec.get("design_lang", "zh"))
    saved = design_save(draft["draft"], spec["name"], category=spec["category"],
                        preview_lines=spec.get("preview") or {})
    set_voice_meta(saved["id"], {"category": spec["category"],
                                 "preview_lines": spec.get("preview") or {}})
    return {"id": saved["id"], "skipped": False, "duration": draft.get("duration")}


def prime_previews(voice_ids: Sequence[str] | None = None,
                   langs: Sequence[str] = ("zh", "en")) -> dict[str, Any]:
    """Pre-render audition clips so a click plays with no synthesis wait."""
    ids = list(voice_ids) if voice_ids else [v["id"] for v in list_voices()]
    made = cached = 0
    failed: list[str] = []
    for vid in ids:
        for lang in langs:
            try:
                if preview(vid, lang).get("cached"):
                    cached += 1
                else:
                    made += 1
            except Exception as exc:  # noqa: BLE001
                failed.append(f"{vid}/{lang}: {type(exc).__name__}: {exc}")
    return {"made": made, "cached": cached, "failed": failed}


def start_build(langs: Sequence[str] = ("zh", "en"), voice_ids: list[str] | None = None,
                refresh: bool = False) -> dict[str, Any]:
    """Background job: design missing catalogue voices, then pre-render previews."""
    with _build_lock:
        if BUILD["running"]:
            return build_state()
        BUILD.update({"running": True, "phase": "准备中", "current": "", "total": 0, "done": 0,
                      "failed": [], "started": time.time(), "finished": 0.0,
                      "langs": list(langs), "log": []})
    threading.Thread(target=_build_worker, args=(tuple(langs), voice_ids, refresh),
                     name="voice-build", daemon=True).start()
    return build_state()


def _build_worker(langs: tuple[str, ...], voice_ids: list[str] | None, refresh: bool) -> None:
    try:
        specs = catalog().get("voices", [])
        if voice_ids:
            specs = [s for s in specs if s["id"] in voice_ids]
        missing = [s for s in specs
                   if s.get("prompt") and (refresh or not _find_voice(s["id"]))]
        _build_set(stage="design", phase=f"造音色 0/{len(missing)}",
                   total=len(missing), done=0)
        for i, spec in enumerate(missing, start=1):
            _build_set(current=spec["name"], phase=f"造音色 {i}/{len(missing)}")
            try:
                design_one(spec, force=refresh)
                _build_log(f"造好音色「{spec['name']}」")
            except Exception as exc:  # noqa: BLE001
                _build_log(f"失败「{spec['name']}」：{exc}")
                _build_fail(f"造音色 {spec['name']}: {exc}")
            _build_set(done=i)
        ids = [s["id"] for s in specs]
        for extra in ("Serena参考",):
            if _find_voice(extra) and extra not in ids:
                ids.append(extra)
        total = len(ids) * len(langs)
        _build_set(stage="previews", phase=f"预生成试听 0/{total}", total=total, done=0)
        done = 0
        for vid in ids:
            _build_set(current=vid)
            for lang in langs:
                done += 1
                try:
                    r = preview(vid, lang)
                    _build_log(f"{'缓存' if r.get('cached') else '新合成'} 试听 {vid}/{lang}")
                except Exception as exc:  # noqa: BLE001
                    _build_log(f"失败 试听 {vid}/{lang}：{exc}")
                    _build_fail(f"试听 {vid}/{lang}: {exc}")
                _build_set(done=done, phase=f"预生成试听 {done}/{total}")
        _build_set(phase="全部完成", current="", finished=time.time())
    except Exception as exc:  # noqa: BLE001
        _build_log(f"构建中断：{type(exc).__name__}: {exc}")
        _build_set(phase=f"中断：{exc}", finished=time.time())
    finally:
        _build_set(running=False)


# ---------------------------------------------------------------------------
# Narration for a production job
#   <job>/request.json  {voice:{id, settings}, language, ...}
#   <job>/script.json   {segments:[{id?, text}]}
# -> <job>/narration/<id>.wav + narration/manifest.json (per-line durations)
# ---------------------------------------------------------------------------

def _job_voice(job: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    req = _json_load(job / "request.json", None)
    if req is None:
        raise FileNotFoundError(f"{job}/request.json 不存在")
    vid = req["voice"]["id"]
    voice = get_voice(vid)
    settings = {**DEFAULT_SETTINGS, **(req["voice"].get("settings") or {})}
    return voice, settings, req.get("language", "zh")


def narrate(job: Path, progress: Callable[[int, int, str], None] | None = None,
            only: list[str] | None = None) -> dict[str, Any]:
    """Synthesise every script line; unchanged lines are reused from cache."""
    job = Path(job)
    voice, settings, lang = _job_voice(job)
    script = _json_load(job / "script.json", None)
    if not script or not script.get("segments"):
        raise ValueError(f"{job}/script.json 缺少 segments")
    nar = job / "narration"
    nar.mkdir(exist_ok=True)
    manifest_path = nar / "manifest.json"
    old = {s["id"]: s for s in _json_load(manifest_path, {}).get("segments", [])}
    mode, note = plan_model(voice, settings)
    segs = script["segments"]
    out_segs: list[dict[str, Any]] = []
    for i, seg in enumerate(segs, start=1):
        sid = str(seg.get("id") or f"{i:03d}")
        text = str(seg["text"]).strip()
        key = _key(voice["id"], lang, text, settings["rate"], settings["pitch"],
                   settings["instruct"] if mode == "preset_1.7b" else "", mode)
        wav = nar / f"{sid}.wav"
        prev = old.get(sid)
        if prev and prev.get("key") == key and wav.is_file() and not (only and sid in only):
            out_segs.append(prev)
            if progress:
                progress(i, len(segs), f"复用 {sid}")
            continue
        if progress:
            progress(i - 1, len(segs), f"合成 {sid}/{len(segs)}")
        info = engine().submit(lambda e, t=text, w=wav: synth_to(voice, settings, t, lang, w),
                               priority=1, label=f"旁白 {i}/{len(segs)}")
        entry = {"id": sid, "text": text, "file": f"narration/{wav.name}", "key": key,
                 "duration": info["duration"]}
        out_segs.append(entry)
        old[sid] = entry
        _json_dump(manifest_path, {"segments": [old[s] for s in old]})
    total = round(sum(s["duration"] for s in out_segs), 3)
    manifest = {"voice": voice["id"], "model": mode, "language": lang, "note": note,
                "settings": settings, "segments": out_segs, "speech_total": total}
    _json_dump(manifest_path, manifest)
    if progress:
        progress(len(segs), len(segs), f"旁白完成，纯语音 {total:.2f}s")
    return manifest


def assemble(job: Path, duration: float, starts: dict[str, float] | None = None,
             lead_in: float = 0.6, gap: float = 0.35) -> dict[str, Any]:
    """Lay the narration lines on the timeline -> voice.wav (48 kHz mono) + timeline.json.

    `starts` maps segment id -> start second (from the storyboard). Missing ids are
    placed after the previous line with `gap`. Lines never overlap.
    """
    import numpy as np
    import soundfile as sf

    job = Path(job)
    manifest = _json_load(job / "narration" / "manifest.json", None)
    if not manifest:
        raise FileNotFoundError("先运行 narrate 生成旁白")
    out_sr = 48000
    total_n = int(round(duration * out_sr))
    track = np.zeros(total_n, dtype=np.float32)
    cursor, timeline, warnings = lead_in, [], []
    for seg in manifest["segments"]:
        data, sr = sf.read(str(job / seg["file"]), dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        if sr != out_sr:
            idx = np.linspace(0, len(data) - 1, int(len(data) * out_sr / sr))
            data = np.interp(idx, np.arange(len(data)), data).astype(np.float32)
        start = max(cursor, float((starts or {}).get(seg["id"], cursor)))
        a = int(round(start * out_sr))
        b = min(total_n, a + len(data))
        if b - a < len(data):
            warnings.append(f"{seg['id']} 超出成片时长，被截断")
        if b > a:
            track[a:b] += data[: b - a]
        end = b / out_sr
        timeline.append({"id": seg["id"], "text": seg["text"],
                         "start": round(start, 3), "end": round(end, 3)})
        cursor = end + gap
    peak = float(np.max(np.abs(track))) or 1.0
    track *= min(1.0, 0.89 / peak)
    sf.write(str(job / "voice.wav"), track, out_sr, subtype="PCM_16")
    result = {"duration": duration, "segments": timeline, "warnings": warnings,
              "speech_end": timeline[-1]["end"] if timeline else 0.0}
    _json_dump(job / "timeline.json", result)
    return result
