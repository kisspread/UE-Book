# Terminal

> Native Slate terminal emulator.

| 属性 | 值 |
|---|---|
| 中文名 | 终端模拟器 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Terminal` (Editor), `TerminalTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal) | |

## 用途

Terminal 是一个原生的 Slate 终端模拟器插件，将完整的命令行终端嵌入 Unreal Editor 内部。它基于 PTY（伪终端）实现，允许开发者在编辑器中直接运行 shell 命令、脚本和外部工具，无需切换到外部终端窗口。

插件的核心架构包括：
- **PTY 后端**：通过伪终端与系统 shell 交互，支持完整的终端 I/O
- **键位翻译器**：将 Unreal 的按键/修饰键事件完整转换为终端可识别的转义序列
- **会话管理**：追踪终端活动状态，支持在编辑器关闭时（尤其是输出进行中）给出提示
- **设置系统**：通过 `UTerminalSettings` 提供可配置选项

该插件解决的核心问题是：在游戏开发工作流中，开发者经常需要执行命令行操作（构建脚本、版本控制、远程部署等），但切换到外部终端会打断工作流。Terminal 将这一切集成到编辑器内部。

## 使用场景

- 你需要在编辑器内执行 shell 命令（如 git、构建脚本、远程部署工具）→ 用 Terminal
- 你在开发自动化工具链，需要在编辑器内监控命令行输出 → 用 Terminal
- 你想减少在编辑器和外部终端之间的窗口切换 → 用 Terminal
- 你需要一个集成在 Slate UI 中的可嵌入终端控件 → 用 Terminal

> ⚠️ **注意**：此插件为 **实验性** 且 **默认未启用**。需要在 Editor Preferences → Plugins 中手动启用，或在项目配置中显式添加。

## 蓝图用法

Terminal 是一个编辑器工具插件，主要通过 Slate UI 和编辑器菜单交互，而非暴露为蓝图节点。作为编辑器专用模块，其大部分 API 面向 C++ 用户。

### 设置类

| 属性 | 说明 | 所在类 |
|---|---|---|
| `UTerminalSettings` | 终端插件的全局配置项 | `UTerminalSettings` |

> 终端设置可通过 Editor Preferences 中的 Terminal 分类进行配置。

## C++ 用法

### 头文件引入

```cpp
#include "Terminal.h"
```

### 基本用法

Terminal 插件提供了 PTY 会话管理和 Slate 终端控件。以下展示了核心的键位翻译和会话管理概念：

```cpp
// Terminal 的核心工作流：
// 1. 创建 PTY 会话
// 2. 通过键位翻译器将按键转换为终端转义序列
// 3. 将转义序列发送给 PTY
// 4. 从 PTY 读取输出并渲染到 Slate 控件

// 键位翻译：UE 按键事件 → 终端转义序列
// 插件内部维护了完整的按键/修饰键到 ANSI 转义序列的映射矩阵
```

### 进阶用法

```cpp
// Terminal 支持会话活动追踪
// 当终端正在输出内容时，如果用户尝试关闭编辑器
// 插件会弹出提示，避免意外中断正在进行的命令

// 设置系统：UTerminalSettings 曾使用 DefaultConfig，后改为无配置装饰
// 这意味着设置可能使用其他配置策略（如 PerUserConfig 或运行时修改）
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Slate`, `SlateCore` | 终端 UI 渲染框架 |
| `Terminal` | 核心终端模拟器模块（TerminalTests 依赖） |

> 无特殊依赖（仅标准 Core/Engine/Slate 等）。PTY 相关的系统调用由引擎内部封装，不对外暴露依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器的函数类型转换警告 |
| 2026-05-12 | `91d5944f` | [Terminal] Surface session activity and prompt before closing the editor mid-output. | 输出进行中关闭编辑器时弹出提示 |
| 2026-04-28 | `2832901f` | [Terminal] Drop `defaultconfig` from `UTerminalSettings`. | 移除设置类的默认配置修饰符 |
| 2026-04-20 | `c9454ad1` | [Terminal] Forward full key/modifier matrix to the *PTY* via a dedicated translator. | 通过专用翻译器转发完整按键矩阵到 PTY |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |

### 维护评价

- **状态**：🟢 活跃开发中
- **创建时间**：约 0 年（2026 年 4 月）
- **更新频率**：约每周 1-2 次提交，持续迭代核心功能
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，仍处于实验阶段
- **已知限制**：
  - 编辑器专用，不支持运行时/打包构建
  - 实验性 API，接口可能随版本变化
  - `NoRedist=true`，不可再分发

**推荐使用**：适合早期采用者和需要评估编辑器内终端方案的团队。功能持续完善中（键位处理、会话管理等），但作为实验性插件，生产环境使用需谨慎。预计随 UE5 后续版本逐步稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal)