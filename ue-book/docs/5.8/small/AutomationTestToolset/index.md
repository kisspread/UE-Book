# Automation Test Toolset

> Automation test discovery and execution tools.

| 属性 | 值 |
|---|---|
| 中文名 | 自动化测试工具集 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomationTestToolset` (Editor), `AutomationTestToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset) | |

## 用途

为 LLM（大语言模型）工具调用提供自动化测试的发现与执行能力。该插件是一套"工具集"（Toolset），暴露一组可供 AI Agent 通过 `ToolsetRegistry` 框架调用的函数，实现：

- **发现测试**：异步初始化自动化测试会话，枚举所有可用测试
- **筛选与运行**：按名称/标签过滤测试，批量异步执行
- **状态查询与控制**：轮询执行状态、获取详细结果、中止运行

本质上，它让 AI Agent 能像人类开发者一样"跑测试、看结果"，是 UE5 AI 辅助开发工具链的一部分。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [AutomationTestToolset](AutomationTestToolset.md) | Editor | 核心工具集定义 + `UEditorSubsystem` 控制器生命周期管理 |
| [AutomationTestToolsetTests](AutomationTestToolsetTests.md) | Editor | CQTest 测试（9 个用例，覆盖所有工具函数） |

## 使用场景

- 你正在构建 AI 辅助开发工作流，需要让 LLM Agent 能自动运行和检查自动化测试
- 你使用 `ToolsetRegistry` 框架开发 AI 工具集，需要一个测试执行的参考实现
- 你需要在编辑器内通过脚本或 AI 批量发现和运行测试，而不想手动操作 Session Frontend

> ⚠️ 本插件默认禁用且为实验性功能，需在插件设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset)
- 依赖插件：[ToolsetRegistry](../Toolsets/ToolsetRegistry/index.md)