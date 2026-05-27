# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI 行为管理器 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

GameplayBehaviors 插件为 AI 代理提供了一个结构化的框架，用于定义和管理复杂的、即发即忘（fire-and-forget）的行为序列。它不仅仅是一个简单的任务系统，而是整合了行为树（BehaviorTree）、感知系统（Perception System）集成以及行为模式管理，旨在为构建复杂的 AI 决策逻辑提供基础构件。它解决了在复杂场景下 AI 行为的组织、触发和执行问题。

## 模块列表

| 模块 | 用途 |
|---|---|
| `GameplayBehaviorsModule` | 核心运行时模块，提供行为组件、行为定义和感知器类。 |
| `GameplayBehaviorsModule` (UncookedOnly) | 处理蓝图相关资产和逻辑，仅在编辑器中用于开发，不包含在打包产品中。 |
| `GameplayBehaviorsEditorModule` | 编辑器支持模块，提供行为树节点、自定义资产编辑器和调试可视化工具。 |

## 使用场景

*   当你的 AI 需要执行一系列复杂的、相互关联的动作（如“接近目标 -> 观察 -> 开火 -> 躲避”）并可以被外部事件打断时。
*   当你需要将 AI 行为与游戏技能系统（Gameplay Ability System）深度集成，实现基于能力的行为触发。
*   当你需要在编辑器中可视化、调试和编辑 AI 行为模式，并希望利用引擎内置的行为树框架时。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移旧式日志宏到新版，优化性能和使用一致性。 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 修改函数访问权限，使其在运行时也可用。 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 修复了行为树节点可能存在的内存泄漏问题。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联宏，优化编译和代码生成。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 配置动态链接库导出符号，确保模块在外部可正确使用。 |

### 维护评价

该插件仍处于**实验性阶段（IsBetaVersion=true）**，且默认未启用。从提交历史看，它仍在持续获得维护性更新（如日志迁移、编译优化、内存修复），表明 Epic 对其内部使用或未来发展有所关注。然而，其更新频率不高，且没有迹象表明它会很快离开实验状态。对于生产项目，建议仅在明确需要其提供的、不同于标准行为树的特定结构（如与GAS深度集成）且愿意承担实验性风险的情况下使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- [官方文档](https://epicgames.com)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)