# Messaging Debugger

> Provides a visual debugger for the messaging sub-system.

| 属性 | 值 |
|---|---|
| 中文名 | 消息调试器 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessagingDebugger` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Messaging/MessagingDebugger) | |

## 用途

Messaging Debugger 是一个编辑器工具，为 UE 的消息总线系统提供可视化调试界面。它解决的核心问题是：在使用 `UMessaging` 系统进行进程间通信（IPC）或进程内通信时，开发者难以追踪消息的发送、路由、接收和处理情况。此插件提供了一个类似 IDE 调试器的界面，可以实时查看消息流、设置断点、检查消息内容和性能延迟，从而极大地简化了消息系统的调试和性能分析工作。

## 使用场景

- 你在开发一个使用 UE 消息总线（`FMessageEndpoint`）进行模块间通信的复杂系统时，需要查看消息是否被正确发送和接收。
- 你需要诊断消息系统中的性能瓶颈，例如某个消息处理时间过长。
- 你需要调试分布式系统，查看消息在不同进程（如服务器和客户端）间的传递情况。
- 你需要设置断点，暂停消息处理流程，以检查特定消息类型或来自特定端点的消息。

## 蓝图用法

该插件是一个纯编辑器工具，没有暴露任何蓝图可调用的函数或属性。所有功能均在编辑器窗口中通过 UI 交互完成。

## C++ 用法

该插件主要通过其提供的编辑器面板和命令使用，不直接提供 C++ API 给用户代码。其内部逻辑依赖于引擎的消息追踪系统 `IMessageTracer`。

### 头文件引入

由于是编辑器插件，且模块类型为 `UncookedOnly`，通常无需在运行时代码中包含其头文件。若需在编辑器工具中集成，可参考其内部结构。

## Demo 示例

由于此插件是一个完整的编辑器应用，无需代码示例。使用步骤如下：

1.  **启用插件**：在编辑器中，前往 `编辑 > 插件`，搜索 “Messaging Debugger” 并启用。
2.  **打开窗口**：重启编辑器后，通过菜单 `窗口 > 开发者工具 > 消息调试器` 打开调试器面板。
3.  **开始调试**：
    *   点击工具栏上的 **开始（Start）** 按钮开始记录消息。
    *   在 `消息历史（Message History）` 选项卡中查看所有被捕获的消息。
    *   通过 `端点（Endpoints）`、`类型（Types）` 等面板设置过滤器，聚焦于特定消息。
    *   在 `消息详情（Message Details）` 面板中检查选中消息的详细信息，如发送者、接收者、延迟和内容。
    *   可以设置断点（`Breakpoints` 选项卡），让调试器在特定消息被处理时暂停。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复编译器关于不可达代码的警告。 |
| 2024-11-26 | `68ae0fe3` | [Spatial Metrics Profiler] Refactor to support loading plugins properly, loading in ini files etc. I... | 为支持 Spatial Metrics Profiler 插件加载进行了重构，属于底层系统调整。 |
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight. ItemHeight and ItemWidth are only us... | 废弃了 Slate 列表项高度的旧接口，插件内部相应更新。 |
| 2024-02-29 | `37131d49` | [Messaging Debugger] | 标记为消息调试器插件的特定提交（可能为元数据更新）。 |
| 2024-02-23 | `15bede99` | Entire engine compiling with -DisableUnity -IncludeHeaders | 引擎整体编译配置变更，插件随之适配。 |

### 维护评价

**维护状态：不活跃**

- **年龄**：插件创建于 2014 年，已超过 10 年，属于引擎中的“老古董”组件。
- **更新频率**：最近的实质性功能性更新远在 2014 年。近几次更新（2024-2025）均为底层编译、Slate 接口或支撑其他工具的适配性修改，并未增加新功能或修复已知的用户体验问题。
- **实验性状态**：插件的 `.uplugin` 明确标记为 `IsBetaVersion: true`，且默认未启用。这表明它可能从未达到完全稳定的生产状态。
- **已知限制**：从代码中可见，部分功能（如消息历史过滤器 `FMessagingDebuggerMessageFilter`）被注释为 `@todo gmp: implement`，表明功能不完整。
- **推荐使用**：**谨慎使用**。该工具对于理解引擎消息系统内部工作原理或进行简单调试仍有价值。但由于其长期的 beta 状态、缺乏功能更新以及可能存在的未完成特性，不建议在核心生产流程或关键项目中依赖它。它更适合作为开发者探索和学习的辅助工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Messaging/MessagingDebugger)