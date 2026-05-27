# Terminal

> Native Slate terminal emulator.

| 属性 | 值 |
|---|---|
| 中文名 | 终端 |
| 分类 | Editor/Tools |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Terminal` (Editor), `TerminalTests` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2026-04-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal) | |

## 用途

该插件在 Unreal Editor 内部提供了一个原生的、基于 Slate 的终端模拟器。它允许开发者直接在编辑器 UI 中打开终端窗口，执行系统命令、运行脚本或与各种命令行工具进行交互，无需频繁切换到外部的终端应用。这对于需要将命令行工作流集成到编辑器开发环境中的场景非常有用。

## 使用场景

- 你需要在 UE5 编辑器中快速执行构建脚本、版本控制（如 Git）命令或自定义的批处理文件。
- 你正在开发一个需要与外部命令行程序交互的编辑器工具或自动化流程。
- 你希望在编辑器内调试或监控与命令行工具的交互，而不想离开当前的工作环境。

## 蓝图用法

该插件主要面向编辑器 C++ 开发，暂未发现公开的蓝图 API。

## C++ 用法

### 头文件引入

由于是编辑器插件，相关功能主要在 `Terminal` 模块中。
```cpp
#include "TerminalModule.h"
```

### 基本用法

该插件的核心是 `FTerminalModule`，它管理着终端会话的创建和生命周期。通常，你会通过获取该模块来启动一个新的终端实例。

### 进阶用法

高级用法涉及自定义终端会话，例如向 *PTY*（伪终端）发送特定的按键序列，或监听会话输出和状态变化。可以参考 `UTerminalSettings` 和相关类的接口。

## Demo 示例

一个最小的示例可能涉及获取终端模块并打开一个默认终端窗口。由于插件主要提供编辑器 UI 集成，一个纯 C++ 的最小示例可能过于简化，核心在于通过 `FTerminalModule` 启动会话。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。此插件是编辑器工具，依赖的均为 UE 编辑器常见模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器（MSVC/Clang）的函数类型转换警告。 |
| 2026-05-12 | `91d5944f` | [Terminal] Surface session activity and prompt before closing the editor mid-output. | 在终端有输出时关闭编辑器，会弹出提示，防止误操作。 |
| 2026-04-28 | `2832901f` | [Terminal] Drop `defaultconfig` from `UTerminalSettings`. | 从 `UTerminalSettings` 类中移除了 `defaultconfig` 标记。 |
| 2026-04-20 | `c9454ad1` | [Terminal] Forward full key/modifier matrix to the *PTY* via a dedicated translator. | 通过专用翻译器将完整的按键和修饰符组合发送到伪终端（*PTY*）。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏 `UE_LOG` 迁移为新版 `UE_LOGF`。 |

### 维护评价

- **创建时间**：该插件是 2026 年 4 月刚迁移到 Experimental 目录的新插件。
- **更新频率**：近期更新频繁，主要集中在功能完善（会话管理、按键转发）和代码质量改进（警告修复、日志迁移）上。
- **活跃状态**：**正在活跃开发**。
- **已知限制**：插件标记为 `IsExperimentalVersion = true` 且 `EnabledByDefault = false`，表明它处于实验阶段，API 和功能可能会发生变化。
- **推荐使用**：可以尝试和贡献，但不建议在需要高度稳定性的生产环境中使用。它非常适合对编辑器工具链有扩展兴趣的开发者。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal/Source/TerminalTests)