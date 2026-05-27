# MessageBus Tester

> Plugin to test and monitor message bus reliability（照抄，不翻译）

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

MessageBus Tester 是一个用于 **测试和调试 UDP 消息传输系统** 的专用工具。它并非一个面向最终用户的功能性插件，而是为引擎开发者和测试人员提供一套标准化的测试用例，用于验证底层 UDP 消息传输组件（特别是 `UdpMessaging` 插件）的可靠性、性能和正确性。它的存在是为了在开发阶段保障消息总线核心代码的健壮性，并为复杂的消息场景提供可重复的测试方案。

## 使用场景

- **消息系统开发者**：在开发或修改 UDP 消息传输层（如 `UdpMessaging`）后，运行此插件的测试用例来验证功能、发现回归问题。
- **性能与可靠性测试**：需要系统性地评估消息总线在压力、网络抖动或特定负载模式下的表现。
- **通信问题调试**：当怀疑消息丢失、乱序或重复时，使用该插件提供的测试场景来隔离和复现问题。
- **集成验证**：确保新接入的消息通道或服务能够正确地与现有消息总线框架协同工作。

## 模块列表

| 模块 | 说明 |
|---|---|
| `MessageBusTester` | 核心运行时模块，包含测试逻辑、测试用例以及与 UDP 消息传输交互的测试客户端/服务端。仅在指定的 `MessageBusTesterApp` 程序中加载。 |
| `MessageBusTesterEditor` | 编辑器工具模块（UncookedOnly），提供在编辑器内配置、启动和监控测试的辅助功能。仅在 `MessageBusTesterApp` 中可用。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧版 UE_LOG 迁移至新版 UE_LOGF。 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复了本地化相关的编译警告。 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修正了 API 导出宏的使用。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 为 Android 启用 NDK 29 并修复相关编译问题。 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复了当远程客户端重置 UDP 消息设置时，统计面板不更新的问题。 |

### 维护评价

该插件作为 **实验性** 工具，主要用于引擎内部测试，不面向最终用户。从创建时间看是一个较新的插件（约1年）。近期更新（2026年4月）表明其仍被纳入引擎的常规维护周期中，主要进行代码现代化（日志宏迁移）和编译警告修复等基础维护工作，但没有重大的功能迭代。考虑到其“实验性”和“仅用于测试”的定位，**推荐在开发或测试消息总线时使用，但不应作为稳定API在生产环境中依赖**。其维护状态可视为 **实验性维护中**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)