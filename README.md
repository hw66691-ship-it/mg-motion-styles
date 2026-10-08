# mg-motion-styles

用代码制作 MG 动态设计短片的 Claude Code / BigApple skill：16 种风格的规范、逐字提示词、可运行参考源码、配乐工具包和无头渲染管线。详细用法见 `SKILL.md`。

## 安装

把整个仓库放进项目的 `.claude/skills/` 目录：

```bash
cd <你的项目>/.claude/skills
git clone https://github.com/hw66691-ship-it/mg-motion-styles.git
bash mg-motion-styles/scripts/setup.sh      # npm 依赖 + Python 虚拟环境 + 开源字体
```

不想用 git 可以下载 zip：https://github.com/hw66691-ship-it/mg-motion-styles/archive/refs/heads/main.zip ，解压后把文件夹改名为 `mg-motion-styles`。

## 依赖

- 必需：Node.js、Python 3.11+、ffmpeg、Chrome。缺哪个，`setup.sh` 就自动下载哪个，装到 `~/.local`，不需要管理员权限。也可以用 `MG_CHROME` 指定浏览器。
- 厂商字体（HarmonyOS Sans、阿里巴巴普惠体等）不能随仓库分发；缺字体时渲染会自动改用 Noto Sans SC
- 可选：Blender（只有 `04-3d-render` 风格需要）
- `workbench/` 的本地配音（旁白 TTS）需要另装 local-video-dubbing 环境和 Qwen3-TTS 模型（默认路径 `~/local-video-dubbing`，可用 `LVD_HOME` 修改）。没有它也能做片，只是不能生成旁白。
- 工作台配乐默认从 `~/Desktop/伴奏歌单/*.mp3` 导入你自己的曲库（`workbench/bgm-ingest.py`）。仓库不附带歌曲。

## 授权

`vendor/` 来自 [mg-styles-15](https://github.com/Vincentwei1021/mg-styles-15)，MIT License（见 `vendor/LICENSE`）。第三方素材和字体的来源见 `CREDITS.md`。
