# Rig Mapper

> A set of animation remapping features

| 属性 | 值 |
|---|---|
| 中文名 | 动画映射器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产，示例映射定义） |
| 模块 | `RigMapper` (Runtime), `RigMapperEditor` (UncookedOnly), `RigMapperDeveloper` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapper) | |

## 用途

RigMapper 插件的核心目标是简化不同动画骨架（Rig）之间的数据映射流程。它并非用于创建 Control Rig 本身，而是用于定义、管理和执行两个 Control Rig 之间的数据转换规则（例如，将一个角色的表情动画数据应用到另一个完全不同面部骨骼结构的角色上）。通过数据驱动的映射定义，可以避免编写复杂的硬编码逻辑，提升动画资产的重用性和制作效率。

## 使用场景

- 你需要将一套标准的表情捕捉动画应用到多个面部骨骼结构（拓扑）各异的虚拟角色身上。
- 你有一个用于驱动手部动画的 Control Rig，现在需要将其输出数据映射到另一个具有不同手指骨骼数量或命名的 Control Rig。
- 你希望在不修改源动画蓝图的情况下，通过配置文件来调整动画参数在不同 Rig 之间的传递方式。

## 模块概览

本插件由三个模块组成，各司其职：

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| [RigMapper](./RigMapper.md) | Runtime | 核心运行时模块，负责加载、解析和执行动画数据的映射规则。 |
| [RigMapperEditor](./RigMapperEditor.md) | UncookedOnly | 编辑器专用模块，提供编辑、测试映射定义（Rig Mapper Definition）资产的 UI 工具。 |
| [RigMapperDeveloper](./RigMapperDeveloper.md) | UncookedOnly | 开发者工具模块，提供用于自动化测试和验证映射定义的功能。 |

## 维护状态

### 近期更新

插件近期处于活跃开发和问题修复阶段。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `ab890466` | [RigMapper] Improved RigMapperDefinition logging and testing | 优化了映射定义的日志记录与测试功能。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量转换为单精度时产生警告的代码。 |
| 2026-05-12 | `40287b95` | [RigMapper] Fixed broken automated tests, added missing automated tests, fixed a bug detected by updated tests. | 修复了失效的自动化测试，补充了缺失的测试，并修复了新测试发现的一个 bug。 |
| 2026-05-12 | `edf81547` | [RigMapper] Made importing inputs/outputs from Control Rig optional in order to reduce clatter | 使从 Control Rig 导入输入/输出端口变为可选，以减少界面杂乱。 |
| 2026-05-12 | `7268ff8e` | [RigMapper] Fixed a bug with comment nodes not fully enclosing selected rig mapper nodes and not tri | 修复了注释节点不能完全包围选中的映射器节点且不能正确触发更新的 bug。 |

### 维护评价

RigMapper 是一个创建时间较短（约2年）的实验性插件。从近期的提交记录来看，开发者正在积极地修复 bug、完善自动化测试和改进用户体验（如减少 UI 杂乱）。作为实验性功能，其 API 和功能可能在未来版本中发生变化。**鉴于其活跃的维护状态和明确的实用价值，推荐在符合其使用场景的实验性或项目内部使用。**

## 模块依赖

要使用本插件，你的模块可能需要依赖以下组件。注意，以下列表仅包含该插件独特或不常见的依赖。

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖，RigMapper 映射的源和目标均为 Control Rig 资产。 |
| `RigLogic` | 插件内部依赖，用于处理更复杂的面部木偶（Face Puppet）系统集成。 |
| `AnimationBlueprintLibrary` | 动画蓝图相关功能支持。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapper)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapper/Tests)