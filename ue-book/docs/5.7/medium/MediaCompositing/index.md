# Media Compositing

> Actors, components and Sequencer extensions for compositing media

| 属性 | 值 |
|---|---|
| 中文名 | 媒体合成 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `MediaCompositing` (Runtime), `MediaCompositingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-24 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaCompositing) | |

## 总体用途

Media Compositing 插件为 Unreal Engine 的 Sequencer 提供了一组 Actor、组件和轨道扩展，用于将媒体资源（视频、图像序列）作为时间轴的一部分进行合成、回放和渲染。它允许用户在序列器中直接控制媒体播放器、媒体纹理及平面网格体等，实现过场动画中的视频嵌入、背景叠加、画中画等合成效果。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [MediaCompositing](MediaCompositing.md) | Runtime | 核心运行时模块，包含媒体合成所需的 Actor、组件（如 `MediaPlane`）、Sequencer 轨道及播放逻辑 |
| [MediaCompositingEditor](MediaCompositingEditor.md) | Editor | 编辑器模块，提供 Media Plane Actor 的放置、旋钮定制、轨道 UI 支持以及编辑器内的预览功能 |

## 使用场景

- 制作电影级过场动画时，将预渲染的视频作为背景或前景元素嵌入到场景中
- 在虚拟制片环境中混合实时渲染与录制的媒体片段
- 需要精确按帧对齐的媒体回放（如参考视频、字幕轨道）
- 在 Sequencer 中实现多路视频合成（例如画中画、分屏效果）

## 维护状态

插件创建于 2025 年 9 月，近期持续有功能修复与优化提交（帧对齐修复、编辑器稳定性改进），维护活跃，推荐在支持媒体合成需求的场景中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaCompositing)
- [MediaCompositing 运行时模块文档](MediaCompositing.md)
- [MediaCompositingEditor 编辑器模块文档](MediaCompositingEditor.md)