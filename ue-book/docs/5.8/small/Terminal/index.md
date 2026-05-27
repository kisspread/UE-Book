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

在 Unreal Editor 内部嵌入一个原生 Slate 终端模拟器，通过 PTY（伪终端）连接真实的 shell 会话（如 bash、cmd、PowerShell）。开发者无需切换窗口即可在编辑器内执行命令行操作，例如运行构建脚本、查看日志、管理版本控制等。

与传统第三方终端相比，该插件深度集成于编辑器 Slate 框架，支持完整的键盘/修饰键转发（包括组合键），并在编辑器关闭时智能检测未完成的输出会话，避免意外中断。

> ⚠️ 当前为实验性插件，**默认未启用**。需在 Plugins 面板中手动启用。

## 使用场景

- 你需要在编辑器内快速执行 shell 命令（构建、测试、git 操作）而不切换窗口
- 你希望终端与编辑器深度集成，支持 Slate 主题和快捷键
- 你在开发 Editor 工具链，需要内嵌终端来运行自定义脚本

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `Terminal` | Editor | 核心终端模拟器，PTY 连接、Slate UI 渲染、键位转发、会话管理 |
| `TerminalTests` | Editor | 自动化测试模块 |

## 模块依赖

从 Build.cs 分析，Terminal 插件无特殊外部依赖，仅依赖标准编辑器框架模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器类型转换警告，提升可移植性 |
| 2026-05-12 | `91d5944f` | [Terminal] Surface session activity and prompt before closing the editor mid-output. | 关闭编辑器时检测未完成输出并提示用户 |
| 2026-04-28 | `2832901f` | [Terminal] Drop `defaultconfig` from `UTerminalSettings`. | 移除设置类的 defaultconfig 标记 |
| 2026-04-20 | `c9454ad1` | [Terminal] Forward full key/modifier matrix to the *PTY* via a dedicated translator. | 实现完整的键盘/修饰键矩阵转发到 PTY |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新式 UE_LOGF |

### 维护评价

- **状态**：🆕 新生插件，创建于 2026 年 4 月，持续有功能性提交
- **活跃度**：近一个月内有多次实质性更新（键位转发、会话安全、跨平台兼容），开发节奏活跃
- **风险**：实验性插件，API 和行为可能随版本变化
- **推荐度**：适合早期体验，不建议在生产环境依赖。关注后续是否晋升为正式插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal)