# UAF Layering

> Framework to define a layering setup in UAF（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | UAF 分层框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、编辑器工具） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAFLayering 是 UAF (Unreal Animation Framework) 框架下的一个子系统，旨在提供一套标准化的**动画层栈（Layer Stack）** 定义与管理框架。它解决的核心问题是：如何在 UAF 系统内，以数据驱动和可视化编辑的方式，将复杂的动画逻辑（如基础移动、上半身武器动画、受击反应、表情等）分解并组合成可复用的层。插件提供了资产类型、编辑器工具和运行时支持，让开发者可以清晰地构建和调试多层动画混合。

## 使用场景

- 你需要为角色构建一个复杂的、可分层的动画状态机。
- 你希望将动画逻辑（如待机、移动、攻击、技能）模块化，并通过资产（Layer Stack）进行组合，而不是在蓝图中硬编码复杂的动画图表。
- 你的项目使用 UAF 作为动画基础，需要一套官方的、与 UAF 生态深度集成的分层解决方案。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`UAFLayering`](UAFLayering.md) | Runtime | **核心运行时模块**。定义了分层资产（如 `UAnimationLayerStack`）的数据结构、运行时求值逻辑以及与 UAF 的集成接口。 |
| [`UAFLayeringEditor`](UAFLayeringEditor.md) | Runtime* | **编辑器工具模块**。提供了层栈资产（`UAnimationLayerStack`）的专用编辑器界面，用于可视化地配置和预览层栈。 |
| [`UAFLayeringUncookedOnly`](UAFLayeringUncookedOnly.md) | Runtime* | **未打包专用模块**。包含仅在开发编辑器环境中使用的功能，如资产转换器、编辑器自定义布局等，确保打包时不会包含多余代码。 |
| [`UAFLayeringTests`](UAFLayeringTests.md) | Runtime* | **测试模块**。包含针对该插件功能的自动化测试用例，用于验证层栈的创建、序列化和运行时行为。 |

*（注：虽然用户提供的模块类型信息显示为 Runtime，但根据 UE 插件开发惯例，`Editor` 和 `UncookedOnly` 模块通常对应 `Editor` 和 `UncookedOnly` 类型，此处可能为信息误差，实际开发时应以具体 Build.cs 为准。）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- 官方文档（暂无）

---
*本文档基于 .uplugin 元数据、模块概述和 git 历史生成。详细 API 与用法请参阅各子模块文档。*