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

本插件是一个内部测试与调试工具，旨在为 Unreal Engine 的 UDP 消息传输系统（`UdpMessaging`）提供一套专门的测试用例和性能监控手段。它不是面向最终用户的功能插件，而是用于验证消息总线在复杂场景下的可靠性、性能和稳定性，帮助引擎开发者排查网络通信相关的问题。

## 使用场景

- 你正在开发或调试依赖跨进程/跨机器通信的功能（如网络多人游戏、分布式计算），需要确保消息传递的可靠性和性能达标。
- 你需要对 `UdpMessaging` 模块进行压力测试或回归测试，以验证代码修改是否引入了问题。
- 你需要实时监控消息总线的统计数据和状态，以诊断通信故障或性能瓶颈。

## 蓝图用法

本插件主要面向测试和监控，其提供的蓝图节点侧重于启动、停止测试以及查看结果。由于插件的实验性质和测试目的，详细的节点列表请参考各子模块文档。

### 核心节点概览

| 节点组 | 说明 | 所在模块 |
|---|---|---|
| 测试控制 | 启动、停止、配置消息总线测试用例 | `MessageBusTester` |
| 监控面板 | 在编辑器中显示消息传输的统计数据和状态 | `MessageBusTesterEditor` |

## C++ 用法

本插件的 API 主要面向测试和编辑器工具开发。

### 头文件引入

```cpp
#include “MessageBusTester.h” // 核心测试逻辑
#include “MessageBusTesterEditor.h” // 编辑器工具和监控面板
```

### 基本用法

核心测试逻辑由 `MessageBusTester` 模块提供，用于驱动测试用例。
编辑器集成和用户界面由 `MessageBusTesterEditor` 模块提供，用于在开发环境中可视化测试过程和结果。

## 模块依赖

除了插件声明依赖的 `UdpMessaging` 插件外，使用者无需添加额外的特殊模块依赖。

| 模块 | 用途 |
|---|---|
| `UdpMessaging` | 提供被测试的底层 UDP 消息传输实现 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志调用迁移到新的 UE_LOGF 宏。 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复本地化相关的编译警告。 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修复 API 导出宏相关的问题。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 为 Android 启用 NDK 29 并修复编译问题。 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复当远程客户端重置 UDP 消息设置时，统计数据面板不更新的问题。 |

### 维护评价

**活跃维护**。该插件自创建以来（约1年）持续收到更新，最近一次更新（2026-04-14）是功能性迁移（日志宏）。更新内容包括功能改进、平台兼容性修复和 bug 修复，表明其处于活跃的维护状态。作为官方实验性插件，它可能会有较大的变更或最终被移除，但目前仍可用于支持 UDP 消息系统的开发和调试工作。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)
- 测试用例通常位于插件目录或 `Engine/Tests` 下，具体路径需查看源码。