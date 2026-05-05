# DMX Engine

> Functionality and assets for communication with DigitalMultiplexer (DMX) enabled devices

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXBlueprintGraph` (UncookedOnly), `DMXEditor` (Editor), `DMXRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-02-19 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine) | |

## 用途

DMX (Digital Multiplex) 是一种用于控制舞台灯光、特效等设备的行业标准通信协议。DMX Engine 插件为虚幻引擎提供了完整的 DMX 协议栈实现，使引擎能够与真实的 DMX 设备（如灯具、雾机、LED 墙控制器）进行双向通信。它解决了在虚拟制片、现场活动预演和建筑可视化等场景中，将引擎内的灯光、特效数据实时同步到物理世界设备的核心问题。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED Volume 拍摄中，将引擎内虚拟场景的灯光信息实时发送给真实的 LED 灯具，实现虚实灯光同步。
- **现场活动与演出预演**：在引擎中预先编程和模拟复杂的灯光秀、特效序列，并通过 DMX 协议输出到真实的灯光控制台或设备进行验证。
- **建筑与主题公园照明设计**：在引擎中设计并可视化照明方案，并直接控制连接的 DMX 灯具原型或最终设备。
- **交互式装置与艺术**：创建由游戏逻辑或用户输入驱动的动态灯光艺术装置。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `DMXRuntime` | Runtime | 核心运行时模块，提供 DMX 协议栈、端口管理、信号收发、蓝图函数库等基础功能。 |
| `DMXEditor` | Editor | 编辑器工具模块，提供 DMX 库资产编辑器、端口配置界面、协议监控器等开发工具。 |
| `DMXBlueprintGraph` | UncookedOnly | 蓝图图表扩展模块，为 DMX 相关的蓝图节点（如信号发送/接收）提供自定义的图表外观和行为。 |

## 蓝图用法

本插件提供了丰富的蓝图 API，用于在运行时发送和接收 DMX 信号。核心功能包括创建和管理 DMX 端口、发送/接收数据、以及处理信号变化事件。详细的节点列表和用法示例，请参阅子模块文档。

- **核心功能节点**：请参阅 [DMXRuntime 模块文档](DMXRuntime.md)。
- **编辑器工具**：请参阅 [DMXEditor 模块文档](DMXEditor.md)。

## C++ 用法

C++ 开发者可以通过 `DMXRuntime` 模块提供的类（如 `UDMXSubsystem`, `FDMXPort`, `FDMXSignal`）来集成 DMX 功能。详细的 API 说明和代码示例，请参阅 [DMXRuntime 模块文档](DMXRuntime.md)。

## 模块依赖

使用本插件时，你的项目模块通常需要依赖 `DMXRuntime` 模块以访问核心功能。如果需要在编辑器中扩展 DMX 工具，则需要依赖 `DMXEditor`。

| 模块 | 用途 |
|---|---|
| `DMXRuntime` | 访问 DMX 协议栈、端口和信号处理的核心运行时功能。 |
| `DMXProtocol` | 底层的 DMX 协议实现库（被 `DMXRuntime` 依赖）。 |

## 维护状态

### 近期更新

（由于未提供具体的 git log 信息，无法列出近期更新。建议在 UE 源码仓库中执行 `git log --format='%h|%ai|%s' -3 -- 'Engine/Plugins/VirtualProduction/DMX/DMXEngine/'` 获取最新提交记录。）

### 维护评价

DMX Engine 是虚幻引擎虚拟制片工具链中的一个重要组成部分。它创建于 2020 年，已发展超过 5 年，功能相对成熟。作为 Epic Games 官方维护的插件，它通常会跟随引擎版本进行更新和修复。对于需要在虚幻引擎中集成真实 DMX 灯光控制的项目，这是一个**推荐使用**的官方解决方案。建议关注引擎版本更新日志以了解其最新状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine)
- [官方文档]() (暂无)
- [测试用例]() (请在源码仓库中搜索相关测试文件)