# MP4 (ISO/IEC 14496-12) utilities

> Provides helpers to work with mp4 files

| 属性 | 值 |
|---|---|
| 分类 | Media |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MP4Utilities` (Runtime), `MP4Boxes` (Runtime), `MP4Muxer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-02-25 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MP4Utilities) | |

## 用途

MP4Utilities 插件提供了一套底层工具，用于在 Unreal Engine 中直接操作符合 ISO/IEC 14496-12 (MP4 容器格式) 标准的文件。它解决了引擎内置媒体框架之外，需要对 MP4 文件进行精细解析、创建或修改的底层需求，例如自定义视频封装、提取特定轨道数据或构建非标准的媒体流。

## 使用场景

- 你需要从 MP4 文件中解析并提取特定的元数据（如章节信息、自定义原子）。
- 你需要在运行时动态创建或修改 MP4 文件的容器结构。
- 你正在开发一个自定义的媒体播放器或编辑器，需要直接操作 MP4 的底层盒子（Box）结构。
- 你需要将多个音视频流多路复用（Mux）到一个 MP4 文件中。

## 模块列表

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| `MP4Utilities` | 提供顶层的、面向用户的 MP4 文件操作辅助函数和工具类。 | [MP4Utilities.md](MP4Utilities.md) |
| `MP4Boxes` | 实现 MP4 文件格式的核心数据结构，用于解析和构建 MP4 容器中的各种“盒子”（Box）。 | [MP4Boxes.md](MP4Boxes.md) |
| `MP4Muxer` | 负责将多个媒体轨道（如音频、视频）多路复用打包成一个完整的 MP4 文件。 | [MP4Muxer.md](MP4Muxer.md) |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MP4Utilities)