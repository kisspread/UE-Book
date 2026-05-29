# Capture Manager Devices

> The Capture Manager Devices contains devices that can be used from the Capture Manager layout of the LiveLink Hub（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器设备 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（设备集成蓝图资产） |
| 模块 | `CPSLiveLinkDevice` (Runtime), `MonoVideoIngestDevice` (Runtime), `StereoVideoIngestDevice` (Runtime), `TakeArchiveIngestDevice` (Runtime), `VideoLiveLinkDeviceCommon` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices) | |

## 用途

这个插件为虚幻引擎的 **Live Link Hub** 的 **Capture Manager** 布局提供了具体的数据源设备实现。它解决了如何将各种视频摄取设备（如 Live Link Face 应用、立体摄影机、视频文件）接入并管理的问题。它本质上是 Live Link 设备类型的具体化，为 Live Link 系统提供了多样化的视频数据输入能力。

## 使用场景

- 你的虚拟制片团队使用 Live Link Hub 集中管理多个视频源设备 → 使用此插件提供的设备来定义和连接这些设备。
- 你需要将来自 Live Link Face iOS 应用的单目视频流接入虚幻引擎 → 使用 `MonoVideoIngestDevice`。
- 你需要处理来自立体摄影机或视频文件的左右眼视频流 → 使用 `StereoVideoIngestDevice`。
- 你需要从已录制的 `.take` 文件归档中回放视频数据 → 使用 `TakeArchiveIngestDevice`。

## 模块列表

- **[CPSLiveLinkDevice](CPSLiveLinkDevice.md)**：基础设备类，为 Capture Manager 提供 Live Link 设备框架。
- **[VideoLiveLinkDeviceCommon](VideoLiveLinkDeviceCommon.md)**：视频类 Live Link 设备的公共基类和工具，提供媒体播放、连接指示等通用功能。
- **[MonoVideoIngestDevice](MonoVideoIngestDevice.md)**：处理单目视频摄取（例如来自 Live Link Face 应用）的设备实现。
- **[StereoVideoIngestDevice](StereoVideoIngestDevice.md)**：处理立体视频摄取（左右眼分离）的设备实现。
- **[TakeArchiveIngestDevice](TakeArchiveIngestDevice.md)**：从 Unreal `.take` 归档文件中摄取视频数据的设备实现。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `222ac128` | StereoVideoIngest: Fix component name consistency across ingest devices | 修复立体视频设备组件命名不一致的问题 |
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 为 CaptureManagerCore 添加 CPS 客户端模块（关联变更） |
| 2026-04-27 | `778f07fc` | [CaptureManager] Fix log category ODR violations in video devices | 修复视频设备中日志类别的 ODR 违规 |
| 2026-04-27 | `334822cd` | Add ConfigureMediaSource virtual hook to ULiveLinkFaceDevice | 为 Live Link Face 设备添加媒体源配置虚函数钩子 |
| 2026-04-21 | `40065f3e` | Added connection indicator for Live Link Face devices | 为 Live Link Face 设备添加连接状态指示器 |

### 维护评价

插件创建于2025年初，近期（2026年4-5月）有多次活跃的功能更新和Bug修复，表明其处于**活跃维护**状态。作为 Capture Manager 和 Live Link Hub 生态的一部分，它是 Epic 官方虚拟制片工作流的组件，推荐在相关项目中使用。

**注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用才能使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices)
- [官方文档]()（.uplugin 中未提供 DocsURL）