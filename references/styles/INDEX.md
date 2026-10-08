# 风格总表（16 种）

序号是展示页编号；`slug` 是提示词与源码目录名。每个 `slug` 对应本目录一份蒸馏卡，
完整原始提示词在 `vendor/prompts/<slug>.md`，可运行的参考实现在 `vendor/demos/<slug>/`。

## 速查表

| # | slug | 中文名 | English | 原片 | 配乐配方 | 难度 |
|---|---|---|---|---|---|---|
| 01 | `05-cel-boil` | 逐帧手绘 / 线条沸腾 | Cel Animation / Frame-by-Frame | HAND MADE | `lofi` | 进阶 |
| 02 | `03-isometric` | 等轴 2.5D | Isometric / 2.5D | ISOPOLIS — Let the City Grow | `explainer` | 进阶 |
| 03 | `01-flat-vector` | 扁平矢量动画 | Flat / Vector 2D Motion Graphics | popwise — One Dot | `pop` | 入门 |
| 04 | `02-line-art` | 线条动画 | Line Art / Line Animation | ATELIER LINEA — One Line | `ambient` | 入门 |
| 05 | `04-3d-render` | 3D 渲染系 | 3D Render / CGI Motion Design | soft. — Soft Landing | `ambient` | 困难 |
| 06 | `08-morph` | 形变动画 | Morphing / Shape Morph | morphe. — One Shape, Every Story | `future_bass` | 入门 |
| 07 | `19-paperclip` | 粗描边贴纸科普 MG | Bold-outline Sticker Explainer | How Many Elements Hide in a Phone? | `explainer` | 进阶 |
| 08 | `22-hud` | 赛博朋克 HUD / FUI | Cyberpunk HUD / FUI | KESTREL-9 · Target Acquired | `darksynth` | 进阶 |
| 09 | `06-collage` | 拼贴剪贴 | Collage / Cutout Animation | NOGGIN Quarterly | `lofi` | 进阶 |
| 10 | `12-aurora-glass` | 弥散渐变 / 玻璃拟态 | Aurora Gradient & Glassmorphism | Aurora — Think in Light | `ambient` | 进阶 |
| 11 | `09-bauhaus` | 几何构成 / 包豪斯 | Geometric / Bauhaus Motion | KONSTRUKTION · 20 Beats | `techno` | 入门 |
| 12 | `10-synthwave` | 80s Synthwave / VHS | Retro: 80s Synthwave / VHS / Y2K | NEON DRIVE — Midnight 1986 | `synthwave` | 进阶 |
| 13 | `20-pixel` | 像素风 | Pixel Art / 8-bit | PIXEL QUEST | `chiptune` | 入门 |
| 14 | `07-liquid` | 液态流动 | Liquid Motion | drop. — It All Starts with a Drop | `future_bass` | 进阶 |
| 15 | `18-hanazi` | 综艺花字（9:16 竖屏） | Variety Show Kinetic Captions | Miaowu Diary EP.07 | `variety` | 入门 |
| 16 | `23-xiaopangxie` | 小螃蟹风格 | Little Crab Storybook Lyric MV | 抖音小螃蟹系列（5 支参考片） | `ambient`(piano) | 入门 |

## 按需求挑

| 你要的效果 | 选 |
|---|---|
| 干净好懂、SaaS/产品解释、最稳的通用款 | 03 `01-flat-vector` |
| 高级克制、一笔画、奢侈品/建筑/金融 | 04 `02-line-art` |
| 信息密度高又可爱、架构图/App 演示 | 02 `03-isometric` |
| 真实材质、糖果软胶、产品片/品牌 ident | 05 `04-3d-render`（需 Blender） |
| 手作温度、卡通角色、烟火水花 | 01 `05-cel-boil` |
| 复古超现实、杂志感、音乐/潮流 | 09 `06-collage` |
| 解压有机、液体转场、音乐视频 | 14 `07-liquid` |
| 苹果发布会级图形叙事、图标串联 | 06 `08-morph` |
| 机械理性卡点、动态海报 | 11 `09-bauhaus` |
| 霓虹镀铬、标题序列、复古怀旧 | 12 `10-synthwave` |
| 慢透贵、AI 产品发布（当下默认皮肤） | 10 `12-aurora-glass` |
| 竖屏、vlog/萌宠/综艺、情绪化字幕 | 15 `18-hanazi` |
| 硬核科普、财经知识区、信息图表 | 07 `19-paperclip` |
| 低分辨率颗粒、游戏区/8-bit | 13 `20-pixel` |
| 科技感皮肤、测评/游戏/AI 演示 | 08 `22-hud` |
| 可爱治愈、歌曲卡点、中文歌词字幕、情感叙事 MV | 16 `23-xiaopangxie` |

## 组合与变体

- 风格可以**混**（如 aurora 底 + 玻璃 UI + HUD 线框），但同一支片里只让**一种风格做主导**，
  否则会变成素材堆砌。改混时以主导风格的 Signature features 为准。
- 竖屏不是裁切：把横屏的横向串联改成纵向推进，标题与安全边距重排。
- 改配色只动 Creative seed 里的色值，保留明度关系与色数上限（如扁平矢量 5–6 色、包豪斯 5 色）。

机器可读版本：`references/styles.json`（含 slug、序号、配方、难度、技术路线、视觉特征、色值、规格）。
