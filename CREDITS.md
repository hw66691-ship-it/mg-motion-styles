# 来源与授权

## 上游项目

本 skill 的 `vendor/` 目录是开源项目 **mg-styles-15** 的逐字镜像（源码、提示词、配乐工具包、
渲染脚本、参考素材），来自 https://github.com/Vincentwei1021/mg-styles-15 。

- 上游项目以 **MIT License** 发布，许可证原文见 `vendor/LICENSE`。
- `vendor/` 内除下列第三方素材外的内容，版权归上游作者所有。
- 上游的成片视频（`videos/`，约 441 MB）未镜像；在线观看：
  https://vincentwei1021.github.io/mg-styles-15/

## 第三方素材

- **乐器采样**（`vendor/lib/audio/samples/`，103 个文件）：来自 **VCSL（Versilian Studios
  Community Sample Library）**，CC0 公有领域。
- **纹理与 HDRI**（`vendor/assets/`）：上游项目声明为 CC0 / 公有领域来源。
- **字体**：未包含在本仓库中（授权各异、中文字体体积大）。清单与放置路径见
  `vendor/assets/fonts/README.md`。生成新片时只使用 OFL / 免费商用字体，并在此处补记。

## 字体

`scripts/fetch-fonts.sh` 抓取的字体均为 OFL 或免费商用授权，来源为 Google Fonts 等官方仓库；
厂商自有授权字体（阿里巴巴普惠体、阿里妈妈数黑体、HarmonyOS Sans SC、抖音美好体、
资源圆体、缝合像素字体）未自动下载，需从官方渠道获取后放到 `vendor/assets/fonts/` 对应路径。

## 对 vendor/ 的本地改动

为让上游代码在本机跑通，做了两处最小改动，均已在代码内用注释标出：

1. `harness/render.mjs` —— 输出编码增加显式 `-t <目标时长>`。
   原因：本机 ffmpeg 下 `apad` + `-shortest` 不截断音轨，容器时长会变成 10.58 s，
   违反「exactly 10.000 s」硬规格。
2. `requirements.txt` —— `matplotlib==3.9.1` 改为 `matplotlib>=3.9.2,<4`。
   原因：该版本在 Python 3.13 上没有 wheel，会导致安装失败。原完整清单保留为
   `requirements-full.txt`。
3. `lib/audio/samples/index.json` —— 过滤到只保留**实际存在**的采样条目。
   原因：上游索引列了 598 条，但仓库只提交了 102 个 FLAC，导致
   `samples.inst('piano')` 之类的调用必定抛 `LibsndfileError`，钢琴/马林巴等
   采样乐器全部不可用。过滤后 15 类乐器恢复可用（piano 39 个采样，音域 MIDI 27–87）。
   原始索引备份为 `lib/audio/samples/index-full.json`。

其余 `vendor/` 内容与上游一致。

## 第 16 套风格「小螃蟹」的来源

`references/styles/23-xiaopangxie.md`、`vendor/prompts/23-xiaopangxie.md`、
`vendor/demos/23-xiaopangxie/`（`index.html` / `cues.json` / `audio.py`）为本次新增，
依据用户提供的 5 支抖音参考片蒸馏：

- `d73c441e343d471ca834683f662980dc.mp4`（雨夜城市 · 方块小蟹 · 蜡笔质感）
- `fb009a64cc7ef3373f57b1c9973f8719.mp4`（雪夜狐狸与电影院 · 纸雕质感）
- `里昂说AI_用Opus5.5纯代码直出《手写的从前》MV.mp4`（校园 · 手写从前 MV）
- `94c1a30c7d774ebca8b1d0bcf0495de0_raw.mp4`（车站与列车 · 夜戏）
- `ecaf612b80287ff63b1ceba42ce1242f_raw.mp4`（桌面 UI + 巨型排版 + 小螃蟹）

参考片版权归原视频作者所有，此处仅用于提取风格特征；本 skill 内的提示词、
风格卡与参考实现均为重新编写，不含参考片素材、画面或音频。

## 风格封面（`workbench/covers/`）

- 6 张来自各风格参考实现的**真实渲染帧**（离线渲染 8.20s 帧）：`02-line-art`、
  `05-cel-boil`、`07-liquid`、`09-bauhaus`、`10-synthwave`、`23-xiaopangxie`。
- 其余 10 张（`01-flat-vector`、`03-isometric`、`04-3d-render`、`06-collage`、`08-morph`、
  `12-aurora-glass`、`18-hanazi`、`19-paperclip`、`20-pixel`、`22-hud`）由 AI 生成，
  原因是对应参考实现在本机无法完整渲染（缺厂商授权中文字体或实拍素材），
  以及 3D 风格依赖未安装的 Blender 序列帧。
  生成用的提示词严格按各风格卡片的「视觉特征 / 关键技法 / 配色」撰写，仅为封面示意，
  不参与出片流程。

## 本 skill 新增内容

`SKILL.md`、`references/`、`scripts/` 为本次蒸馏产出，不含上游成片与字体。
