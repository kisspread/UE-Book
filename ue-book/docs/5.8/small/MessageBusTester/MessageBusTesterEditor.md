# MessageBus Tester

> Plugin to test and monitor message bus reliability

| 属性 | 值 |
|---|---|
| 中文名 | 消息总线测试器 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessageBusTester` (Runtime), `MessageBusTesterEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester) | |

## 用途

MessageBusTester 是一个用于**测试和监控 Unreal Engine UDP 消息总线（UdpMessaging）可靠性**的内部实验性工具。它不是一个面向最终用户的通用功能插件，而是一个为引擎网络团队设计的**自动化压力测试和诊断工具**。

**核心问题解决**：UE 的底层 UDP 消息传输系统在复杂的网络环境（如高丢包、高延迟、大负载）下的稳定性和性能表现，需要通过特定的测试用例来验证和优化。此插件提供了这些标准化的测试用例和配套的监控界面。

**存在意义**：它允许开发者（主要是引擎网络团队）创建、执行并监控各种“测试计划”，以模拟不同负载下的消息传输场景，从而：
1.  验证 UDP 消息传输的可靠性保证（如重传、确认机制）。
2.  收集并分析网络传输统计数据（如吞吐量、往返时延、丢包率）。
3.  为底层网络代码的优化和 bug 修复提供定量的测试依据。

## 使用场景

-   **引擎网络开发**：你是 Epic 或自定义引擎的网络模块开发者，在修改或优化 `UdpMessaging` 模块后，需要运行回归测试来确保改动没有引入性能回退或功能故障。
-   **多人游戏底层网络调试**：你在开发对网络性能要求极高的多人游戏（如竞技 FPS 或大规模 MMO），需要模拟极端网络条件来测试客户端/服务器通信的边界情况。
-   **构建自定义消息传输系统**：你在基于 UE 的消息总线架构构建自定义的网络层，需要一个基准测试框架来评估你的实现。

**注意**：此插件默认未启用（`Installed: false`），且仅供名为 `MessageBusTesterApp` 的特定程序使用，这意味着它通常不会出现在标准的游戏项目中。

## 蓝图用法

此插件主要提供**编辑器 UI 和独立的测试应用框架**，不包含任何公开的蓝图可调用节点（BlueprintCallable）或属性（BlueprintReadWrite）。所有功能都通过其专用的编辑器面板和独立的测试应用程序界面来操作。

## C++ 用法

此插件**不提供供外部项目集成的公共 C++ API**。它的设计目标是作为一个自包含的测试工具。主要的代码结构是：
-   `MessageBusTester` 模块：包含测试逻辑的核心运行时代码。
-   `MessageBusTesterEditor` 模块：包含用于显示测试状态、网络统计和测试计划管理的 Slate UI。

因此，无法在游戏项目或编辑器插件中直接调用其功能。用法是编译并运行 `MessageBusTesterApp`。

## Demo 示例

由于这是一个独立的测试应用而非功能库，无法提供一个集成到游戏中的最小代码示例。要使用此工具，你需要：
1.  在 UE 源码环境中启用并编译此插件。
2.  编译并运行 `MessageBusTesterApp` 目标。
3.  在该应用程序中，通过其内置 UI 管理测试计划、发现网络中的其他测试器实例，并观察传输统计数据。

## 模块依赖

从 `MessageBusTesterEditor.Build.cs` 分析，要使用此插件的编辑器部分，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `MessageBusTester` | 提供核心的测试器逻辑和接口 |
| `UdpMessaging` | 提供底层的 UDP 消息传输实现，是被测试的对象 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 格式。 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复了本地化相关的编译警告。 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修正了 API 导出宏的使用问题。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 为 Android 平台启用 NDK 29，并修复相关编译问题。 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复了当远程客户端重置其 UDP 消息设置时，统计面板不更新的问题。 |

### 维护评价

-   **活跃维护**：尽管是实验性插件，但最近的提交记录显示（截至 2026 年 4 月），它仍在持续进行更新和维护，包括编译修复、平台适配和 bug 修复。
-   **内部工具**：它服务于特定的内部团队（UE 网络团队），因此更新可能与底层网络模块的改动紧密相关。
-   **实验性/测试专用**：由于 `.uplugin` 中 `IsBetaVersion: true` 且 `SupportedPrograms` 限制，这表明它是一个内部测试工具，其 API 和行为在未来可能会发生变化，甚至被移除。
-   **推荐使用**：仅推荐给需要进行 UE 底层 UDP 消息总线性能与可靠性基准测试的高级开发者或引擎程序员。对于大多数游戏项目，此插件没有直接用途。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)