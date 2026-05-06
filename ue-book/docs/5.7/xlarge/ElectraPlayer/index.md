# Electra Player

> Cross platform media player for local files and internet streaming.  
> Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 电子播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（C++ 模块） |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/ElectraPlayer) | |

## 总体用途

Electra Player 是 Epic 提供的现代跨平台媒体播放解决方案，支持本地文件、HLS/DASH 等流媒体播放，并针对桌面平台提供了高性能的 MP4 优化播放器（Protron）。它通过多个子模块分工协作，将底层解码、解复用、渲染与 UE 的媒体框架（`UMediaPlayer`、媒体纹理等）无缝集成，是虚幻引擎中推荐使用的视频回放插件。

## 模块列表

点击模块名查看详细文档。

| 模块 | 一句话说明 | 文档 |
|---|---|---|
| `ElectraPlayerFactory` | 播放器工厂，负责创建和管理播放器实例 | [ElectraPlayerFactory.md](ElectraPlayerFactory.md) |
| `ElectraPlayerPlugin` | 插件集成层，将 Electra 播放器注册到 UE 媒体框架，提供 `UMediaPlayer` 支持 | [ElectraPlayerPlugin.md](ElectraPlayerPlugin.md) |
| `ElectraPlayerPluginHandler` | 桥接 `ElectraPlayerRuntime` 与 UE 插件接口，处理回调与事件 | [ElectraPlayerPluginHandler.md](ElectraPlayerPluginHandler.md) |
| `ElectraPlayerRuntime` | 核心运行时，实现解复用、解码、渲染等流媒体播放逻辑 | [ElectraPlayerRuntime.md](ElectraPlayerRuntime.md) |
| `ElectraProtron` | 桌面优化的 MP4 快速播放器，侧重本地文件回放性能 | [ElectraProtron.md](ElectraProtron.md) |
| `ElectraProtronFactory` | Protron 播放器的工厂模块 | [ElectraProtronFactory.md](ElectraProtronFactory.md) |

## 使用场景

- 在游戏或应用中嵌入视频播放（片头、过场、UI 视频）
- 从网络流式传输直播或点播内容（HLS、DASH、mp4 等）
- 需要高性能本地 MP4 播放（桌面平台）时，可选用 Protron 模式
- 与其他 UE 媒体管线（媒体纹理、音频输出）无缝配合

## 维护状态

### 近期更新

- 2025-10-01 `31d4710d` — 改进回放事件支持；为 HLS VoD 流添加转换为重放事件的能力
- 2025-09-29 `d34a730c` — 仅当启用了时长检查时，才发出媒体段不匹配警告
- 2025-09-29 `49fa2b76` — 根据媒体段实际时长调整最大 Live 边缘延迟
- 2025-09-23 `0dc995dc` — 使用 VoD 资源作为同步事件时，支持通过 DataAsset 循环播放
- 2025-09-11 `d9f531d6` — 合并多行字符串为单行

### 维护评价

Electra Player 是 Epic 在 5.7 中引入的新一代媒体播放插件，创建时间极短，近期持续有功能性更新（如回放事件、Live 边缘调整等），开发活跃。该插件填补了老旧的 `MediaPlayer` 在跨平台流媒体和优化方面的不足，推荐在新项目中优先使用。暂无已知重大限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer/Tests)（若存在）