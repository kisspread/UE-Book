# HTN Planner

> [EXPERIMENTAL] Adds experimental support for Hierarchical Task Network (HTN) planner to the UE4's AI module

| 属性 | 值 |
|---|---|
| 中文名 | 分层任务网络规划器 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HTNPlanner` (Runtime), `HTNTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-04-17 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/HTNPlanner) | |

## 用途

HTN Planner 为 UE 的 AI 系统引入了**分层任务网络（Hierarchical Task Network）**规划能力。HTN 是一种经典 AI 规划范式，与 UE 内置的行为树（Behavior Tree）互补：

- **行为树**适合反应式的决策逻辑（条件驱动），适合"遇到 X 就做 Y"的模式。
- **HTN 规划器**适合**目标驱动的多步骤计划**，能将高层任务递归分解为可执行的原子操作序列，适合"要达成目标 Z，先做 A，再做 B，最后做 C"的模式。

该插件提供了一个 `UHTNBrainComponent` 作为 AI 控制器的大脑组件，可以替代或配合 `UBehaviorTreeComponent` 使用。规划器会根据世界状态（World State）自动搜索满足目标的任务分解方案。

**当前状态**：该插件自 2018 年创建以来一直处于实验阶段（`IsBetaVersion=true`），近 7 年未有功能性更新，仅有编译兼容性修复。不建议在生产环境中使用。

## 使用场景

- 你需要一个 AI 角色能够**自动规划多步骤行动序列**（例如：去仓库拿武器 → 移动到掩体 → 开火），而不是手动在行为树中编写每个分支
- 你的游戏 AI 需要处理**复杂的目标分解**，例如 RTS 游戏中单位需要"建造基地"这个目标自动分解为：采集资源 → 建造建筑 → 生产单位
- 你想研究或实验 HTN 规划算法在 UE 中的实现方式

## 蓝图用法

由于该插件处于实验阶段，公开的蓝图 API 非常有限。从源码可确认的核心类为 `UHTNBrainComponent`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UHTNBrainComponent` | HTN 大脑组件，挂载到 AIController 上作为规划执行器 | `UHTNBrainComponent` |

### 使用示例（蓝图描述）

1. 在 AIController 蓝图中添加 `UHTNBrainComponent` 组件
2. 该组件会替代标准的 `UBehaviorTreeComponent` 作为 AI 决策核心
3. 通过 HTN 领域定义（Domain）描述可用的任务分解方法和前置条件
4. 规划器根据当前世界状态和目标自动搜索可行的任务序列

## C++ 用法

### 头文件引入

```cpp
#include "HTNPlannerModule.h"
```

### 基本用法

从测试模块中的 Mock 实现可以看到 HTNBrainComponent 的基本继承方式：

```cpp
// 来源: Source/HTNTestSuite/Private/MockHTN.h

#include "HTNBrainComponent.h"

UCLASS()
class UMockHTNComponent : public UHTNBrainComponent
{
    GENERATED_BODY()

public:
    // 继承 UHTNBrainComponent，获得 HTN 规划能力
    // 内部维护 TaskPriorityQueue 用于任务优先级管理
};
```

## Demo 示例

一个继承 HTNBrainComponent 的最小示例：

```cpp
// MyHTNBrain.h
#pragma once

#include "CoreMinimal.h"
#include "HTNBrainComponent.h"
#include "MyHTNBrain.generated.h"

UCLASS(ClassGroup=(AI), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyHTNBrain : public UHTNBrainComponent
{
    GENERATED_BODY()

public:
    UMyHTNBrain();

    // HTNBrainComponent 提供了任务优先级队列管理
    // 可通过重写相关虚函数自定义规划行为
};
```

```cpp
// MyHTNBrain.cpp
#include "MyHTNBrain.h"

UMyHTNBrain::UMyHTNBrain()
{
    PrimaryComponentTick.bCanEverTick = true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 编辑器框架支持 |
| `UnrealEd` | 编辑器工具（注意：Runtime 模块不应依赖此模块，这是已知的架构问题） |

⚠️ **重要提示**：HTNPlanner 模块类型为 `Runtime`，但其 Build.cs 依赖了 `EditorFramework` 和 `UnrealEd`。这会导致打包后的游戏构建失败。这是该插件保持实验状态的原因之一，如需用于生产，需要修正这些依赖关系。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复 printf 格式说明符 |
| 2025-12-16 | `7e659465` | Fixed HTNPlanner's Build.cs | 修复构建配置文件 |
| 2025-07-15 | `35e62d59` | Fix/silence V530 unhandled return value warnings | 修复静态分析未处理返回值警告 |
| 2025-06-10 | `b08804f0` | Replace some usages of FORCEINLINE with inline in AI modules. | AI 模块中替换 FORCEINLINE 为 inline |

### 维护评价

⚠️ **不推荐在生产环境使用。**

- **创建时间**：2018 年 4 月，距今约 7 年
- **更新频率**：近一年有 5 次提交，但全部是**编译兼容性修复**（日志宏迁移、格式修复、构建配置修正等），没有任何功能性更新
- **活跃状态**：仅被动维护，确保能在新版 UE 中编译通过，未进行功能开发
- **已知限制**：
  - 一直处于实验/Beta 状态（`IsBetaVersion=true`）
  - 默认未启用（`EnabledByDefault=false`）
  - Runtime 模块错误依赖了编辑器模块（`UnrealEd`、`EditorFramework`），无法正常打包
  - 公开 API 极少，文档缺失
  - 版本号仍为 0.01
- **结论**：该插件是 Epic 早期对 HTN 规划的实验性探索，从未达到生产就绪状态。如需 HTN 功能，建议参考此实现自行开发，或使用社区方案（如 NodeAI 等第三方 HTN 插件）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/HTNPlanner)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/HTNPlanner/Source/HTNTestSuite)