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

`MessageBusTester` 是一个专为开发者设计的**测试与调试工具**。它并非面向最终用户，其核心目的是提供一套测试用例，用于评估和验证 Unreal Engine 中 UDP 消息传输（`UdpMessaging`）的可靠性、性能与正确性。通过模拟各种消息发送/接收场景，该插件帮助开发团队分析消息总线的使用模式，确保底层网络代码在复杂情况下的健壮性。需要注意的是，这是一个实验性（Beta）插件，其功能和接口在未来版本中可能会发生重大变更或被移除。

## 使用场景

- **网络功能开发与调试**：当你正在开发或调试依赖于 UDP 消息传输的游戏功能或编辑器工具时，可以使用此插件作为基准测试工具，验证消息收发逻辑是否正确。
- **性能压力测试**：需要评估 `UdpMessaging` 模块在高负载、大消息量或网络不稳定情况下的表现时，可以使用此插件的测试用例进行模拟。
- **引擎底层代码验证**：在 Unreal Engine 源码层面，用于回归测试，确保对消息总线系统的修改不会引入错误。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `MessageBusTester` | Runtime | 提供核心测试逻辑、测试用例和独立的测试应用程序。 |
| `MessageBusTesterEditor` | UncookedOnly | 提供在编辑器环境下运行和监控测试的集成与 UI 组件。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester/Source/MessageBusTester/Tests)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新的 `UE_LOGF` 格式。 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复了本地化相关的编译警告。 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修正了 API 导出宏，以确保正确的模块可见性。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 为 Android 启用 NDK 29 并修复相关编译问题。 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复了远端客户端重置 UDP 消息设置后，统计面板不更新的问题。 |

### 维护评价

该插件创建于 2025 年底，属于一个较新的实验性组件。从 git 历史看，创建后有多次维护性更新，包括编译问题修复、代码现代化（日志宏迁移）和特定功能修复（统计面板）。最近一次更新在 2026 年 4 月，表明它目前仍处于**维护中**状态。由于其 `IsBetaVersion=true` 且 `EnabledByDefault=false`，它明确为测试目的服务，并不面向生产环境。开发者可以将其用作消息总线功能的参考和调试工具，但应意识到其 API 和行为可能不稳定。**推荐**在需要深入测试或调试 UDP 消息功能时使用。