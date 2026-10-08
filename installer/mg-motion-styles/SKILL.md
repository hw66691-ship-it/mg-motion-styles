---
name: mg-motion-styles
description: 用代码制作 MG 动态设计短片（16 种风格：扁平矢量、一笔画线条、等轴 2.5D、3D 渲染、逐帧手绘、拼贴、液态、形变、包豪斯、Synthwave/VHS、弥散渐变玻璃拟态、像素风、综艺花字、回形针贴纸科普、赛博 HUD、小螃蟹手绘抒情 MV），带本地 TTS 旁白、字幕、配乐与无头渲染管线。当用户要求做 MG 动画 / 动态设计 / 动效短片 / 动态海报 / 片头包装 / logo 演绎 / 品牌 ident / 知识科普动画 / 带旁白的解说视频，或点名上面某种风格时使用。首次使用会自动从 GitHub 下载完整 skill。不用于剪辑已有实拍素材或给现有视频加字幕。
---

# MG 动态设计短片（安装引导）

这是 mg-motion-styles 的轻量安装包。完整内容（风格规范、参考源码、渲染管线，约 150 MB）放在 GitHub：

- 仓库：https://github.com/hw66691-ship-it/mg-motion-styles
- 下载：https://github.com/hw66691-ship-it/mg-motion-styles/archive/refs/heads/main.zip

## 被调用时先做这一步

1. 检查本 skill 目录下是否已有 `vendor/` 目录和 `references/` 目录。
   - **已有** → 已经是完整版，直接读本目录的 `SKILL.md`（安装后会被完整版覆盖）按其流程工作。
   - **没有** → 运行安装脚本：

     ```bash
     bash "<本 skill 目录>/scripts/install.sh"
     ```

     脚本会下载上面的 zip，解压覆盖到本 skill 目录，并运行完整版的 `scripts/setup.sh`
     安装 Node / Python 依赖和开源字体。需要联网，首次约几分钟。
2. 安装成功后，**重新读取本目录下的 `SKILL.md`**（此时已是完整版说明），再按它处理用户的需求。
3. 安装失败时把脚本的报错原样告诉用户。常见原因：没装 node / python3 / ffmpeg，
   或网络无法访问 github.com。不要自行编造替代流程。

## 依赖

Node.js、Python 3、ffmpeg、Google Chrome（无头渲染）；可选 Blender（3D 风格）、
本地 Qwen3-TTS（旁白配音）。详见完整版 README。
