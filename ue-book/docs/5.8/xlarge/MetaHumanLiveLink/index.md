# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 实时链接 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 是一套完整的实时动画数据流传输系统，用于将外部设备捕捉的面部和身体动画数据通过 Live Link 协议实时传输到 UE5 中的 MetaHuman 角色。

该插件解决了 MetaHuman 角色动画的实时驱动问题——包括发现和连接 Live Link Face 应用、接收面部/身体动画数据、本地处理动画数据，以及在编辑器中配置和预览实时动画。它是 MetaHuman 实时动画工作流的核心基础设施。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `LiveLinkFaceDiscovery` | Runtime | 发现局域网内的 Live Link Face 追踪应用设备 |
| `LiveLinkFaceSource` | Runtime | 接收来自 Live Link Face 应用的面部动画数据流 |
| `LiveLinkFaceSourceEditor` | Runtime | Live Link Face 数据源的编辑器工具和 UI |
| `MetaHumanLiveLinkSource` | Runtime | MetaHuman 专用 Live Link 数据源，处理面部和身体动画 |
| `MetaHumanLiveLinkSourceEditor` | Runtime | MetaHuman Live Link 数据源的编辑器工具和配置界面 |
| `MetaHumanLocalLiveLinkSource` | Runtime | 本地 MetaHuman Live Link 数据源，处理本地动画数据流 |
| `MetaHumanLocalLiveLinkEditor` | Runtime | 本地 MetaHuman Live Link 的编辑器工具 |

## 使用场景

- **实时面部捕捉**：使用 iPhone 上的 Live Link Face 应用，将面部表情实时映射到 MetaHuman 角色
- **现场直播/虚拟演出**：通过实时数据流驱动 MetaHuman 角色进行虚拟直播或实时演出
- **实时预览**：在编辑器中实时预览动画效果，无需事先录制
- **本地动画处理**：使用本地 Live Link 数据源进行离线或本地动画数据处理
- **身体动画捕捉**：配合身体追踪设备，实现全身 MetaHuman 角色的实时驱动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink)

---

## 子模块文档

| 模块 | 文档 |
|---|---|
| LiveLinkFaceDiscovery | [LiveLinkFaceDiscovery.md](LiveLinkFaceDiscovery.md) |
| LiveLinkFaceSource | [LiveLinkFaceSource.md](LiveLinkFaceSource.md) |
| LiveLinkFaceSourceEditor | [LiveLinkFaceSourceEditor.md](LiveLinkFaceSourceEditor.md) |
| MetaHumanLiveLinkSource | [MetaHumanLiveLinkSource.md](MetaHumanLiveLinkSource.md) |
| MetaHumanLiveLinkSourceEditor | [MetaHumanLiveLinkSourceEditor.md](MetaHumanLiveLinkSourceEditor.md) |
| MetaHumanLocalLiveLinkSource | [MetaHumanLocalLiveLinkSource.md](MetaHumanLocalLiveLinkSource.md) |
| MetaHumanLocalLiveLinkSourceEditor | [MetaHumanLocalLiveLinkSourceEditor.md](MetaHumanLocalLiveLinkSourceEditor.md) |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `9bee2cb0` | [MHA] Expose detection thresholds for body | 暴露身体检测阈值参数供调优 |
| 2026-05-14 | `988b3911` | [MHA] Face animation sequence export changes for combined solve | 面部动画序列导出适配组合求解 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断警告 |
| 2026-05-12 | `8bf9ba92` | [MetaHumanLiveLink] Use AvfMedia for FileMediaSource bundles on Apple platforms | Apple 平台使用 AvfMedia 处理媒体源 |
| 2026-05-12 | `fa06fada` | New ADA model | 更新 ADA 模型 |

### 维护评价

**活跃维护中** ✅

- 插件创建于 2025 年 2 月，至今约 1 年历史
- 最近更新非常密集（2026 年 5 月有多次功能性更新）
- 持续获得功能增强：身体检测阈值暴露、动画导出改进、新模型更新
- 跨平台支持不断完善（Apple 平台媒体适配）
- **强烈推荐使用**：作为 MetaHuman 实时动画的核心基础设施，正在被积极维护和迭代，适合生产环境使用