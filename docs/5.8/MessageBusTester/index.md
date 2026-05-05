# MessageBus Tester

> Plugin to test and monitor message bus reliability（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessageBusTester` (Runtime), `MessageBusTesterEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MessageBusTester) | |

## 用途

这是一个用于**测试和监控 Unreal Engine 消息总线（MessageBus）可靠性**的专用工具插件。它并非面向最终游戏运行时，而是为开发者提供一个独立的测试程序（`MessageBusTesterApp`），用于在受控环境下模拟、发送、接收和验证消息，以评估消息总线在各种网络条件和负载下的稳定性与性能。

## 使用场景

- 你正在开发一个依赖 `UdpMessaging` 或自定义消息总线的多人游戏或分布式系统，需要验证其底层通信的可靠性。
- 你需要一个独立的、可配置的测试工具来模拟高并发消息、网络延迟或丢包场景，以发现潜在的消息丢失或顺序错乱问题。
- 你正在调试或优化消息总线的性能，需要一个基准测试环境来收集数据。

## 蓝图用法

无公开蓝图 API。此插件主要为 C++ 独立测试程序设计。

## C++ 用法

此插件的核心功能通过其提供的独立测试程序 `MessageBusTesterApp` 来使用。开发者通常不直接在游戏模块中调用其 API，而是通过配置和运行该测试程序来进行验证。

### 模块功能概述

- **`MessageBusTester` (Runtime)**：提供消息总线测试的核心逻辑、测试用例和监控功能。
- **`MessageBusTesterEditor` (UncookedOnly)**：提供编辑器集成，可能用于配置测试参数或查看测试结果。

详细的 API 和实现请参阅各子模块文档：
- [MessageBusTester 模块文档](MessageBusTester.md)
- [MessageBusTesterEditor 模块文档](MessageBusTesterEditor.md)

## Demo 示例

此插件本身即是一个完整的测试程序。以下是一个概念性的最小使用流程，展示如何在你的开发环境中启动和使用它：

1.  **启用插件**：在你的 UE 项目或源码构建中，确保 `MessageBusTester` 插件已启用。
2.  **构建独立程序**：编译 `MessageBusTesterApp` 目标。这通常通过 UnrealBuildTool (UBT) 完成。
3.  **运行测试**：启动编译好的 `MessageBusTesterApp` 可执行文件。程序将根据其内部逻辑或配置文件，开始执行一系列消息总线测试。
4.  **监控结果**：观察程序的输出日志或使用其可能提供的监控界面，查看测试结果、性能指标和错误报告。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UdpMessaging` | 提供基于 UDP 的消息传输实现，是本插件的主要测试对象 |
| `Messaging` | 提供 UE 核心消息总线框架 |

## 维护状态

### 近期更新

（基于提供的创建时间，此插件为全新创建，暂无历史提交记录）

### 维护评价

- **年龄**：插件创建于 2025 年 11 月，非常新。
- **状态**：标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明它仍处于**实验性/测试阶段**，并非稳定功能。
- **维护**：作为实验性插件，其维护状态和未来路线图取决于 Epic 的内部开发计划。目前来看，它是一个专用的开发工具。
- **推荐**：仅推荐给需要深入测试 UE 消息总线底层可靠性的**高级开发者或引擎程序员**。普通游戏开发者通常无需直接使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MessageBusTester)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MessageBusTester/Tests) (如果存在)