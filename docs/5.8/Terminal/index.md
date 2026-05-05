# Terminal

> Native Slate terminal emulator.

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Terminal` (Editor), `TerminalTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal) | |

## 用途

Terminal 插件提供了一个基于原生 Slate 框架的终端模拟器，嵌入在 Unreal Editor 内部运行。它解决的核心问题是：开发者在编辑器内工作时，无需切换到外部终端窗口即可执行命令行操作。通过将终端直接集成到编辑器 UI 中，开发者可以在同一个界面内完成代码编译、脚本执行、日志查看等工作流，减少窗口切换带来的上下文中断。

该插件目前处于实验阶段，尚未默认启用，需要手动在插件管理器中激活。

## 使用场景

- 你在编辑器内频繁需要执行命令行工具（如构建脚本、自动化测试）→ 用 Terminal 在编辑器内直接操作
- 你需要一个集成在编辑器中的轻量终端，避免反复 Alt-Tab 切换到外部终端
- 你在开发编辑器扩展，需要嵌入一个命令行交互界面 → 参考 Terminal 的 Slate 实现方式

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`Terminal`](Terminal.md) | Editor | 核心终端模拟器模块，提供 Slate 终端 UI 和命令执行功能 |
| [`TerminalTests`](TerminalTests.md) | Editor | 自动化测试模块，验证终端模拟器的核心功能 |

## 蓝图用法

该插件为 Editor 模块，主要面向 C++ 和 Slate 编辑器扩展场景，暂无公开的蓝图 API。详细接口请参阅 [Terminal 模块文档](Terminal.md)。

## C++ 用法

详细的 C++ API 和使用示例请参阅各模块文档：

- [Terminal 模块文档](Terminal.md) — 核心 API、头文件引入、基本用法
- [TerminalTests 模块文档](TerminalTests.md) — 测试用例参考

## 模块依赖

详细依赖关系请参阅各模块文档。该插件无特殊外部依赖，仅依赖标准的 Core/Engine/Slate 等基础模块。

## 维护状态

### 近期更新

- 2026-04-20 `c9454ad1` [Terminal] Forward full key/modifier matrix to the *PTY* via a dedicated translator.
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-09 `98f0c628` [Terminal] Add `StartupCommands` setting to execute commands on new terminal window creation.
- 2026-04-08 `ca248609` [Terminal] Move `Terminal` plugin to `Engine/Plugins/Experimental`.

### 维护评价

- **状态**：🆕 全新实验性插件
- 该插件于 2026 年 4 月首次提交，属于全新的实验性功能
- 标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 可能发生重大变化
- `NoRedist=true` 表示不可单独再分发
- 目前仅有初始提交，尚无后续迭代记录，建议关注后续版本更新
- **建议**：可作为参考和学习用途，暂不建议在生产环境中依赖此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Terminal)
- [Terminal 模块文档](Terminal.md)
- [TerminalTests 模块文档](TerminalTests.md)