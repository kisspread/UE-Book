# Timed Data Monitor

> Utilities to monitor inputs that can be time synchronized.

| 属性 | 值 |
|---|---|
| 中文名 | 时间同步数据监控器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TimedDataMonitor` (UncookedOnly), `TimedDataMonitorEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-01-29 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TimedDataMonitor) | |

## 用途

本插件专为虚拟制作流程设计，用于**监控和调试那些需要精确时间同步的数据源**。在虚拟制片或使用 LiveLink 等实时数据驱动场景中，多个数据流（如摄像机追踪、动作捕捉、音频等）必须在时间轴上保持严格对齐，否则会导致音画不同步或物体位置漂移等问题。TimedDataMonitor 提供了可视化工具来实时检查这些数据源的时间戳、延迟和帧率，帮助技术人员快速定位并解决时间同步问题，确保最终画面的一致性和准确性。

## 模块列表

- **TimedDataMonitor** (UncookedOnly): 提供核心的运行时数据监控能力，包含被监控数据源的基础类和接口定义。
- **TimedDataMonitorEditor** (Editor): 提供在编辑器内使用的监控窗口、图表和设置面板，用于直观地可视化和管理时间同步数据。

## 使用场景

- **虚拟制片（Virtual Production）**: 在 LED Volume 拍摄中，需要监控来自 Mo-Sys、Stype 等摄像机追踪系统的数据，确保其与 Unreal Engine 渲染的场景时间同步。
- **实时动作捕捉（Motion Capture）**: 使用 LiveLink 将面捕或动捕数据传输到 UE 时，需要监控数据流的延迟和丢帧情况，以保证角色动画的实时性。
- **多源数据融合**: 当场景同时接收来自多个 LiveLink 源（如相机、灯光、音频）时，需要一个统一的监控界面来确认所有数据的时间基准一致。
- **现场直播（Live Show）**: 在虚拟演唱会或直播中，需要确保所有视觉元素与音轨的时间码完全匹配。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TimedDataMonitor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TimedDataMonitor/Tests)