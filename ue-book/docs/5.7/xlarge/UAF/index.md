# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems

| 属性 | 值 |
|---|---|
| 中文名 | 虚幻动画框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestSuite` (Runtime), `UAFUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF) | |

## 总体用途

UAF 全称 Unreal Animation Framework，是一个实验性插件，旨在为动画系统提供 **函数式数据流定义框架**。它允许开发者以图形化（蓝图）或代码方式设计、组合和复用动画数据处理管线，突破传统动画蓝图在复杂逻辑和跨模块复用方面的限制。该框架包含运行时核心、编辑器扩展（资产向导、图形模式）、测试套件以及仅未打包阶段使用的工具模块。

## 模块列表

| 模块 | 一句话总结 | 文档 |
|---|---|---|
| **UAF** | 运行时核心，定义动画数据流的基础类型、节点和接口。 | [UAF 文档](UAF.md) |
| **UAFEditor** | 编辑器集成模块，提供资产创建向导、图形模式支持及拖放过滤等功能。 | [UAFEditor 文档](UAFEditor.md) |
| **UAFTestSuite** | 测试套件，包含自动化测试用例和示例，用于验证框架正确性。 | [UAFTestSuite 文档](UAFTestSuite.md) |
| **UAFUncookedOnly** | 仅未打包阶段使用的模块，负责蓝图编译、资产处理等编辑器内任务。 | [UAFUncookedOnly 文档](UAFUncookedOnly.md) |

## 使用场景

- 你在开发需要 **自定义动画数据流管线** 的项目（如程序化动画、物理驱动动画、多角色同步）。
- 你希望用 **函数式/数据流范式** 组织动画逻辑，替代传统动画蓝图的顺序执行模式。
- 你需要一种 **可复用、可图型化编辑** 的动画处理组件，方便设计师和程序员协作。
- 你在实验性项目中尝试 UE5 最新的动画扩展能力。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF)
- [测试用例（UAFTestSuite）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF/Source/UAFTestSuite)