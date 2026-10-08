#!/usr/bin/env python3
"""Export the local voice library into this folder for the BigApple preview app.

`/ba/v1` only works inside BigApple HTML preview, and that page cannot read
`~/local-video-dubbing/workbench`. So we mirror the voice list plus the
pre-generated audition clips here as plain static files.

Run after adding voices, or after priming a new language:

    PYTHONPATH=$HOME/local-video-dubbing/app \
      $HOME/local-video-dubbing/venv/bin/python export-voices.py
"""

from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import voicecore as vc  # noqa: E402

WANT_LANGS = ("zh", "en", "ja", "ko")
MUST_LANGS = ("zh", "en")       # 这两种语言缺试听就现场补合成，保证预览页每个音色都能试听


def _server():
    """Running workbench server (owns the TTS model), or None."""
    try:
        import urllib.request
        info = json.loads(vc.SERVER_INFO.read_text(encoding="utf-8"))
        with urllib.request.urlopen(info["url"] + "api/health", timeout=3) as r:
            return info if json.load(r).get("app") == "mg-workbench" else None
    except Exception:
        return None


def _generate(info, vid: str, lang: str) -> dict | None:
    """Synthesise one audition clip through the server; never loads a second model in-process."""
    import urllib.request
    req = urllib.request.Request(info["url"] + "api/preview",
                                 data=json.dumps({"voice": vid, "lang": lang}).encode(),
                                 headers={"Content-Type": "application/json", "X-MGW-Token": info["token"]})
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            out = json.load(r)
        return out if out.get("file") else None
    except Exception as exc:
        print(f"⚠ 补合成试听失败 {vid}/{lang}：{exc}", file=sys.stderr)
        return None


def main() -> int:
    out_previews = HERE / "previews"
    out_previews.mkdir(exist_ok=True)
    voices = vc.list_voices()
    info = _server()
    clips: dict[str, dict[str, str]] = {}
    texts: dict[str, dict[str, str]] = {}
    copied = 0
    for v in voices:
        vid = v["id"]
        for lang in WANT_LANGS:
            try:
                p = vc.preview(vid, lang, generate=False)
                if not p.get("file") and lang in MUST_LANGS:
                    # 改过语速/音高/试听句后旧试听就失效了：先现场补合成，补不了就退回默认设置那条
                    p = (_generate(info, vid, lang) if info else None) or \
                        vc.preview(vid, lang, settings=dict(vc.DEFAULT_SETTINGS), generate=False)
            except Exception:
                continue
            if not p.get("file"):
                if lang in MUST_LANGS:
                    print(f"⚠ {vid}/{lang} 没有试听（工作台服务没开，无法补合成）", file=sys.stderr)
                continue
            src = vc.PREVIEWS / p["file"]
            if not src.is_file():
                continue
            dst = out_previews / p["file"]
            if not dst.is_file() or dst.stat().st_mtime < src.stat().st_mtime:
                shutil.copy2(src, dst)
                copied += 1
            clips.setdefault(lang, {})[vid] = f"previews/{p['file']}"
            texts.setdefault(lang, {})[vid] = p.get("text") or ""
    payload = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "langs": vc.LANG_LABELS,
        "instruct_model": vc.instruct_model_ready(),
        "design_model": vc.design_model_ready(),
        "categories": vc.catalog_categories(),
        "preview_clips": clips,
        "preview_texts": texts,
        "voices": [
            {k: v[k] for k in ("id", "name", "kind", "desc", "category", "native",
                               "design_prompt", "tunable", "settings") if k in v}
            for v in voices
        ],
    }
    (HERE / "voices.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    total = sum(len(c) for c in clips.values())
    print(f"voices.json：{len(voices)} 个音色，{total} 条试听（新复制 {copied} 个文件）")
    sync_preview_app()
    return 0


# BigApple 预览不读隐藏目录（.claude/），所以在项目根目录放一份可见的副本
PREVIEW_APP = HERE.parents[3] / "MG视频工作台"
APP_FILES = ("index.html", "styles.json", "voices.json")
APP_DIRS = ("covers", "previews")


def sync_preview_app() -> None:
    PREVIEW_APP.mkdir(exist_ok=True)
    for name in APP_FILES:
        shutil.copy2(HERE / name, PREVIEW_APP / name)
    # 预览副本不经过本地服务，项目目录（BigApple 建会话要用）直接写进页面
    page = PREVIEW_APP / "index.html"
    page.write_text(page.read_text(encoding="utf-8").replace("__MGW_PROJECT__", str(HERE.parents[3])),
                    encoding="utf-8")
    for name in APP_DIRS:
        shutil.copytree(HERE / name, PREVIEW_APP / name, dirs_exist_ok=True)
    print(f"预览副本已同步：{PREVIEW_APP / 'index.html'}")


if __name__ == "__main__":
    raise SystemExit(main())
