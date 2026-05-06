# Timecode Synchronizer (Deprecated)

> This plugin has been deprecated and will be removed in a future engine version. Please update your project to use the features of the TimedDataMonitor plugin instead.
> An asset that will become the TimecodeProvider once all the inputs get synchronized to a timecode.

| 属性 | 值 |
|---|---|
| 中文名 | 时间码同步器（已废弃） |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TimecodeSynchronizer` (Runtime), `TimecodeSynchronizerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TimecodeSynchronizer) | |

## 总体用途

本插件用于在**虚拟制作**工作流中同步多个媒体输入源的时间码。它提供一个 `TimecodeSynchronizer` 资产，当所有输入与一个共同的时间码同步后，该资产本身会成为引擎的 `TimecodeProvider`。

**重要：此插件已被废弃，不再推荐使用。请使用 `TimedDataMonitor` 插件替代。**

## 模块列表

| 模块 | 类型 | 一句话说明 | 文档 |
|---|---|---|---|
| `TimecodeSynchronizer` | Runtime | 核心运行时模块，定义同步逻辑与 `TimecodeSynchronizer` 资产类 | [TimecodeSynchronizer.md](TimecodeSynchronizer.md) |
| `TimecodeSynchronizerEditor` | Editor | 编辑器模块，提供资产 UI 和设置管理 | [TimecodeSynchronizerEditor.md](TimecodeSynchronizerEditor.md) |

## 使用场景

- **虚拟制片现场**：需要将多个摄像机、媒体服务器播放器的时间码对齐，确保录制/播放帧同步。
- **多机位同步直播**：对多个带有时间码源的输入进行统一同步。
- **迁移到新系统**：如果项目正在使用此插件，建议尽快迁移到 `TimedDataMonitor` 以获得长期支持和更多功能。

## 维护状态

⚠️ **已废弃**：该插件在 `.uplugin` 中明确标记为废弃，计划在未来的引擎版本中移除。Git 历史显示近期仅有一些编译和代码清理的提交，没有功能性更新。

### 近期更新
- 2025-06-13 b3edcb21 — Replace some usages of FORCEINLINE with inline in MovieScene modules.
- 2023-11-29 c98c8912 — Fix C4702 warnings
- 2023-02-18 e599d19e — Removing redundant Private includes.
- 2023-01-16 bbc37aa2 — [Engine/Plugins]
- 2022-10-21 610c4676 — Update vendor links for built-in plugins to use secure protocol.

### 维护评价
- **创建于 2022 年**，活跃时间短暂。
- 自 2023 年底起无实质性功能更新，**已停止活跃维护**。
- 官方已明确废弃，**不推荐在新项目中使用**。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaPlayerEditor` | 提供媒体播放器编辑支持 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TimecodeSynchronizer)
- [TimecodeSynchronizer 运行时模块文档](TimecodeSynchronizer.md)
- [TimecodeSynchronizerEditor 编辑器模块文档](TimecodeSynchronizerEditor.md)