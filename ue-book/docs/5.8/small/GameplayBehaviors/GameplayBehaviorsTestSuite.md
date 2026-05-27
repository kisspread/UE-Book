# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | 游戏行为 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

GameplayBehaviors 为 AI 代理（Agent）提供封装好的"即发即忘"（fire-and-forget）行为系统。它解决的核心问题是：在使用 GameplayAbilities 系统的项目中，如何以模块化、解耦的方式定义和执行 AI 行为，而不是将所有 AI 逻辑硬编码到行为树或 AI Controller 中。

与传统的行为树（Behavior Tree）不同，GameplayBehaviors 倾向于将 AI 行为封装为独立的、可复用的行为组件，这些行为可以在触发后独立运行，无需调用方持续关注其执行状态。这种设计模式特别适合：

- 需要与 GameplayAbilities 系统深度集成的 AI 逻辑
- 多个 AI 代理共享同一套行为定义
- 行为之间需要灵活组合和切换的场景

该插件依赖 GameplayAbilities 插件，说明其设计定位是 GA 生态的 AI 行为扩展层。

## 使用场景

- 你正在使用 GameplayAbilities 系统构建游戏，需要一套与 GA 配套的 AI 行为框架 → 用 GameplayBehaviors
- 你需要将 AI 的攻击、巡逻、追击等行为封装为独立的、可触发执行的模块 → 用 GameplayBehaviors
- 你需要 AI 行为能够触发 GameplayEffect 或与 GameplayTag 系统交互 → 用 GameplayBehaviors
- 你需要在行为树之外提供一种更轻量级的 AI 行为定义方式 → 用 GameplayBehaviors

## 蓝图用法

> ⚠️ **注意**：该插件处于实验性（Beta）阶段，且源码访问受限，以下信息基于已有分析，实际 API 请以源码为准。

由于源码分析信息有限，蓝图 API 细节请参考插件源码中的 `Public/*.h` 头文件。该插件的核心类可能包括行为定义类和行为管理器类，用于在蓝图中创建和触发 AI 行为。

## C++ 用法

> ⚠️ 由于该插件为实验性插件，以下信息基于有限的源码分析，请结合实际源码使用。

### 头文件引入

```cpp
#include "GameplayBehaviorsModule.h"
```

### 基本用法

该插件提供了一个独立的 Runtime 模块 `GameplayBehaviorsModule`，使用前需确保：

1. 在项目的 `.uproject` 或 `.Build.cs` 中启用该插件
2. 你的模块依赖 GameplayAbilities 和 GameplayBehaviors 模块

## Demo 示例

> 由于该插件处于实验性阶段且源码信息有限，暂无可编译的最小示例。请参考 Lyra 示例项目中的 AI 相关代码，该项目可能包含该插件的实际使用案例。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 核心依赖，提供 GameplayAbility 系统、GameplayEffect、GameplayTag 等基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-03-27 | `2ef401e4` | FValueOrBlackboardKeyBase::ToString is not tool only | 移除 FValueOrBlackboardKeyBase::ToString 的仅限工具限制 |
| 2026-03-27 | `3d027aeb` | Node memory cleanup | 节点内存清理优化 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 为所有方法和静态变量添加 DLL 导出修饰符 |

### 维护评价

- **创建时间**：2021-09-28，从内部仓库迁移到 Experimental 目录
- **最近更新**：2026 年 4 月仍有活跃更新，近期改动集中在代码现代化（日志宏迁移、内联宏、DLL 导出规范）
- **实验性状态**：插件始终标记为 `IsBetaVersion = true` 且 `EnabledByDefault = false`，说明 Epic 将其视为实验性功能
- **活跃程度**：更新频率较低但持续有维护性提交，说明该插件仍在被维护，但开发重心不在功能扩展
- **已知限制**：作为实验性插件，API 可能在未来版本中发生破坏性变更；需要手动启用
- **推荐程度**：如果你的项目重度依赖 GameplayAbilities 且需要结构化的 AI 行为封装，可以尝试使用，但需做好 API 变更的准备。对于生产项目，建议关注其何时从 Experimental 毕业

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)
- [GameplayAbilities 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GameplayBehaviors)（前置依赖）
- 官方文档：暂无