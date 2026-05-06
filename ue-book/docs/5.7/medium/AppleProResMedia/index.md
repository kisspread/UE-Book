# Apple ProRes Media

> Implements video playback and the export of the Apple ProRes Codec.  Apple ProRes is a high quality, lossy video compression format.

| 属性 | 值 |
|---|---|
| 中文名 | Apple ProRes 媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleProResMedia` (Runtime), `ProResToolbox` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-08-07 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AppleProResMedia) | |

## 总体用途

AppleProResMedia 提供 Apple ProRes 格式（高质量有损视频压缩）的**播放**和**导出**能力。  
- **播放**：通过 WmfMedia 框架在 Windows 和 macOS 上解码 ProRes 视频文件。  
- **导出**：与 Movie Render Pipeline（影片渲染管线）集成，允许渲染输出为 .mov 的 ProRes 编码视频。  
- 该插件封装了 Apple 官方的 `ProResToolbox` 编解码库，并处理动态加载以优化编辑器启动时间。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [AppleProResMedia](AppleProResMedia.md) | Runtime | 核心模块，封装 ProRes 播放/导出的编辑器与运行时 API，并管理第三方库加载。 |
| [ProResToolbox](ProResToolbox.md) | External | Apple 官方 ProRes 解码/编码库的 UE 封装，提供底层编解码接口。 |

## 使用场景

- **电影渲染输出**：在 Movie Render Queue 中选择 Apple ProRes 编码格式（如 ProRes 422 HQ、ProRes 4444）导出高质量视频。  
- **播放 ProRes 素材**：在关卡中播放 .mov ProRes 视频（需启用 WmfMedia 媒体源）。  
- **自定义媒体管道**：开发者可通过 C++ 直接调用 `AppleProResMedia` 模块的编解码功能，集成到自定义媒体播放器或导出工具中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AppleProResMedia)
- [Apple ProRes 官方文档](https://developer.apple.com/documentation/prores)