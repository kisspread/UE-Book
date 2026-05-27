# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI行为组件 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

该插件为AI代理提供了可配置、可封装的行为系统。它旨在解决AI行为逻辑复杂、难以复用和管理的问题。通过将AI的特定行为（如移动、攻击、拾取物品等）封装成独立的"行为"类，开发者可以创建高度模块化、易于组合和重用的AI逻辑单元。这些行为设计为"fire-and-forget"（发出即忘），意味着一旦触发，行为会自行管理其执行过程和终止条件，减轻了上层系统（如行为树或AI控制器）的直接管理负担。

## 使用场景

- 你需要为AI角色实现多种复杂、可复用的行为模式（如巡逻、追击、使用掩体、交互等），并希望它们能独立运行。
- 你希望将AI行为与具体的AI决策逻辑（如行为树）解耦，使行为本身可以独立开发和测试。
- 你正在使用Gameplay Ability System (GAS)，并希望将AI行为作为能力（Ability）来触发和管理，实现与GAS的深度集成。
- 你需要为大量不同类型的AI代理提供标准化的行为接口，但每个代理的行为实现又各不相同。

## 模块列表

| 模块 | 类型 | 功能简介 |
|---|---|---|
| `GameplayBehaviorsModule` | Runtime | 提供游戏行为系统的核心运行时功能，包括行为基类、行为容器、任务节点等。 |
| `GameplayBehaviorsModule` | UncookedOnly | 仅在未打包的编辑器环境中加载，可能包含用于编辑器预览、调试或特定烘焙过程的代码。 |
| `GameplayBehaviorsEditorModule` | Editor | 提供编辑器专用的功能，如自定义资产编辑器、节点编辑器、行为预览和调试工具等。 |

## 使用场景（详细）

- **游戏玩法原型开发**：快速为不同AI角色配置组合不同的行为，测试游戏玩法。
- **大型项目AI系统**：将复杂的AI逻辑拆分为独立、可单元测试的行为组件。
- **与GAS集成的AI**：将AI行为作为Gameplay Ability来触发，利用GAS的堆栈、冷却、效果等机制管理AI行为。
- **模组化AI**：允许玩家或模组作者通过组合现有行为来创建新的AI角色类型。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 核心依赖。此插件与GAS深度集成，行为可能作为Gameplay Ability实现或与之交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到新的UE_LOGF，提升日志功能和一致性。 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 修复了一个bug：`FValueOrBlackboardKeyBase::ToString`函数不再是仅工具可用，使其在运行时也能正确工作。 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 对行为树节点的内存管理进行了清理和优化，可能修复了内存泄漏或提高了性能。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加了`UE_INLINE_GENERATED_CPP_BY_NAME`宏，用于内联生成代码，可能提升编译效率和代码组织。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 使用LyraGame构建目标来发现并转换所有文件，为方法和静态变量添加了DLL导出声明，确保在插件外部能正确链接。 |

### 维护评价

- **活跃维护**：插件创建于约4年前，且在2025年4月至2026年4月期间有多次实质性更新（功能优化、bug修复、代码迁移）。
- **实验性状态**：插件目前仍处于**实验性**阶段（`IsBetaVersion=true`），默认未启用，API和功能可能发生变化。
- **依赖关系**：强依赖于`GameplayAbilities`插件，表明其设计紧密围绕GAS。
- **推荐使用**：适合需要高度模块化AI行为系统，并且已经在使用或计划使用GAS的项目。由于是实验性插件，不建议在追求稳定性的生产项目中直接使用，但非常适合原型开发和探索性项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)