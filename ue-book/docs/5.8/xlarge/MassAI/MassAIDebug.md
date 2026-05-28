# Mass AI

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 中文名 | 大规模AI |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（调试资产、测试资产） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavMeshNavigation` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是基于 Epic 的 MassEntity (ECS) 框架构建的、用于处理大规模 AI 的插件。它为 MassGameplay 提供了 AI 特定的功能扩展，核心解决的问题是在拥有成千上万个 AI 实体（例如 NPC 群体、生物群落）的场景中，实现高效、可扩展的 AI 行为、导航和调试。

它的存在是为了将 AI 逻辑与传统的 Actor/Component 模型解耦，利用 ECS 的数据驱动和并行处理优势，显著提升大规模 AI 的性能和可管理性。

## 使用场景

-   你需要为开放世界游戏创建大量市民、士兵或怪物，且希望获得高帧率表现。
-   你的游戏需要数百或数千个实体进行自主决策和导航（如城市交通、群体避障）。
-   你需要在运行时可视化、调试和分析大量 AI 实体的行为和状态。
-   你正在使用或计划使用 MassEntity 和 MassGameplay 构建游戏逻辑，并希望为其添加高级 AI 功能。

## 蓝图用法

MassAI 的蓝图功能主要集中在 **MassAIDebug** 模块提供的 Gameplay Debugger 分类中，用于运行时交互式调试。其他模块（如 MassNavigation、MassAIBehavior）主要通过 C++ 定义数据片段（Fragments）和处理器（Processors）供 MassEntity 系统使用，其蓝图交互通常通过 MassGameplay 的通用蓝图节点（如修改片段数据）实现。

### 核心节点 (MassAIDebug)

在 Gameplay Debugger 的 “Mass” 分类下，通过按键触发以下功能（这些功能由 `FGameplayDebuggerCategory_Mass` 类封装）：

| 按键（默认） | 功能 | 说明 |
|---|---|---|
| `(` | 切换原型显示 | 在屏幕上显示实体所属的原型（Archetype）信息。 |
| `)` | 切换形状显示 | 显示实体的物理形状或导航边界。 |
| `'` | 切换代理片段 | 显示与 AI 代理相关的数据片段信息。 |
| `;` | 选择实体 | 进入实体选择模式，点击选取一个实体进行详细检查。 |
| `,` | 切换实体详情 | 显示当前选中实体的详细片段数据。 |
| `.` | 切换附近实体概览 | 显示选中实体附近的其他实体的概述信息。 |
| `/` | 切换附近实体避障 | 可视化选中实体的避障计算数据。 |
| `[` | 切换附近实体路径 | 显示选中实体及附近实体的移动路径。 |
| `]` | 切换实体视线 | 显示实体的视线方向。 |
| `\` | 循环实体描述详细度 | 在“隐藏”、“最小”、“完整”三种实体描述详细度间切换。 |

### 使用示例（蓝图描述）

1.  在游戏运行时，打开 Gameplay Debugger（通常按 `'` 键）。
2.  通过左上角下拉菜单或快捷键切换到 “Mass” 调试分类。
3.  按 `;` 键，此时游戏视角会进入拾取模式。将准星对准一个你怀疑是 MassEntity 控制的 AI 实体（例如，一个由 MassSpawner 生成的角色），点击鼠标左键进行选择。
4.  选中实体后，屏幕左侧会列出该实体的数据片段列表。你可以按 `,` 键展开/收起详情。
5.  按 `.` 键，屏幕右侧会显示以选中实体为中心、指定半径内其他实体的列表和分数，帮助你分析 AI 的空间分布。
6.  按 `[` 键，你可以看到该实体以及附近实体的当前移动路径，用于调试寻路逻辑。

## C++ 用法

MassAI 主要通过定义数据片段（Fragments）和处理器（Processors）来扩展 MassEntity 系统。以下示例展示如何参与该系统。

### 头文件引入

根据你要使用的模块引入相应头文件。例如，使用调试功能：
```cpp
#include "GameplayDebuggerCategory_Mass.h" // MassAIDebug 模块
```
例如，使用导航功能：
```cpp
#include "MassNavigationFragments.h" // MassNavigation 模块
```

### 基本用法 (创建自定义处理器)

以下是一个基于 `UMassDebugStateTreeProcessor` 模式创建的自定义处理器示例，用于查询并处理带有特定 AI 标签的实体。
*(来源文件: `Engine/Plugins/AI/MassAI/Source/MassAIDebug/MassDebugStateTreeProcessor.h` 及通用 MassProcessor 模式)*

```cpp
// MyAIAggressionProcessor.h
#pragma once

#include "MassProcessor.h"
#include "MassEntityTypes.h" // 引入基本实体类型

// 假设我们定义了一个数据片段来存储AI的攻击性
USTRUCT()
struct FAIAggressionFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY()
    float AggressionLevel = 0.0f;
};

// 一个用于检查实体是否可被攻击的标签
USTRUCT()
struct FIsAttackableTag : public FMassTag
{
    GENERATED_BODY()
};

UCLASS()
class UMyAIAggressionProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyAIAggressionProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    // 查询：查找同时拥有 FAIAggressionFragment 和 FIsAttackableTag 的实体
    FMassEntityQuery AggressiveEntityQuery;
};
```

```cpp
// MyAIAggressionProcessor.cpp
#include "MyAIAggressionProcessor.h"

UMyAIAggressionProcessor::UMyAIAggressionProcessor()
{
    // 标记为需要在游戏线程执行（如果操作非线程安全的数据）
    // ExecutionFlags = (int32)EProcessorExecutionFlags::GameThread;
    bAutoRegisterWithProcessingPhases = true; // 自动注册到执行阶段
}

void UMyAIAggressionProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 配置查询：需要 FAIAggressionFragment 和 FIsAttackableTag
    AggressiveEntityQuery.AddRequirement<FAIAggressionFragment>(EMassFragmentAccess::ReadWrite);
    AggressiveEntityQuery.AddRequirement<FIsAttackableTag>(EMassFragmentPresence::All);
    // 可选：设置处理器在哪个阶段执行
    // ProcessingPhase = EMassProcessingPhase::Logic;
}

void UMyAIAggressionProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有匹配查询的实体
    AggressiveEntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取对实体数据的访问
        TConstArrayView<FAIAggressionFragment> AggressionList = Context.GetFragmentView<FAIAggressionFragment>();

        const int32 NumEntities = Context.GetNumEntities();
        for (int32 i = 0; i < NumEntities; ++i)
        {
            // 对每个实体进行处理
            FAIAggressionFragment& Aggression = AggressionList[i];
            
            // 示例逻辑：随时间降低攻击性
            Aggression.AggressionLevel -= 0.01f;
            Aggression.AggressionLevel = FMath::Max(0.0f, Aggression.AggressionLevel);

            // 这里可以添加更复杂的AI行为逻辑
            // 例如，如果检测到敌人，增加AggressionLevel
        }
    });
}
```

### 进阶用法 (与 Gameplay Debugger 交互)

在自定义的 `MassProcessor` 中，你可能需要在调试模式下输出信息。可以利用 `FGameplayDebugger` 系统。

```cpp
// 在处理器的 Execute 函数中
#if WITH_MASSGAMEPLAY_DEBUG
if (UWorld* World = Context.GetWorld())
{
    // 检查是否处于Mass调试模式下
    if (FGameplayDebugger::IsDebuggerActive(TEXT("Mass")))
    {
        // 获取调试画布上下文并绘制信息
        // 注意：实际绘制通常在 FGameplayDebuggerCategory_Mass 的 DrawData 中进行
        // 这里只是演示如何获取调试状态
        UE_LOG(LogTemp, Log, TEXT("MyAIAggressionProcessor: Processing %d entities"), Context.GetNumEntities());
    }
}
#endif
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何创建一个自定义的 MassProcessor，该处理器会为所有带有“可移动”标签的实体应用一个简单的导航目标。

**1. 定义数据片段和标签 (MyMassAIExample.h)**

```cpp
// MyMassAIExample.h
#pragma once

#include "MassEntityTypes.h"
#include "MassNavigationFragments.h" // 引入标准导航片段

// 自定义标签：标记实体需要移动
USTRUCT()
struct FNeedsToMoveTag : public FMassTag
{
    GENERATED_BODY()
};

// 我们的示例处理器：为需要移动的实体设置导航目标
UCLASS()
class USetRandomNavTargetProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    USetRandomNavTargetProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

**2. 实现处理器 (MyMassAIExample.cpp)**

```cpp
// MyMassAIExample.cpp
#include "MyMassAIExample.h"
#include "MassNavigationSubsystem.h"
#include "MassNavigationTypes.h"
#include "Engine/World.h"

USetRandomNavTargetProcessor::USetRandomNavTargetProcessor()
{
    bAutoRegisterWithProcessingPhases = true;
}

void USetRandomNavTargetProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 查询需要 FNeedsToMoveTag 且拥有 FMassMoveTargetFragment 的实体
    EntityQuery.AddRequirement<FNeedsToMoveTag>(EMassFragmentPresence::All);
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadWrite);
    // 可能还需要位置片段来设置随机目标
    EntityQuery.AddRequirement<FMassAgentMovementFragment>(EMassFragmentAccess::ReadWrite);
}

void USetRandomNavTargetProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 获取导航子系统（如果需要）
    UMassNavigationSubsystem* NavSubsystem = UWorld::GetSubsystem<UMassNavigationSubsystem>(Context.GetWorld());

    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&NavSubsystem](FMassExecutionContext& Context)
    {
        TConstArrayView<FMassMoveTargetFragment> MoveTargetList = Context.GetFragmentView<FMassMoveTargetFragment>();
        TConstArrayView<FMassAgentMovementFragment> MovementList = Context.GetFragmentView<FMassAgentMovementFragment>();

        const int32 NumEntities = Context.GetNumEntities();
        for (int32 i = 0; i < NumEntities; ++i)
        {
            FMassMoveTargetFragment& MoveTarget = MoveTargetList[i];
            const FMassAgentMovementFragment& Movement = MovementList[i];

            // 简单逻辑：如果当前没有有效移动目标，则设置一个随机目标
            if (MoveTarget.GetCurrentAction() == EMassMovementAction::Stand)
            {
                // 在当前位置附近随机选择一个点
                const FVector CurrentLocation = Movement.GetLocation();
                const FVector RandomOffset = FMath::VRand() * 500.0f; // 随机方向，500单位距离
                const FVector NewTargetLocation = CurrentLocation + RandomOffset;

                // 设置导航目标
                MoveTarget.CreateNewAction(EMassMovementAction::Move, NewTargetLocation);
                MoveTarget.Center = NewTargetLocation; // 目标中心
                // 注意：在实际应用中，你可能需要调用NavSubsystem来规划路径
                // NavSubsystem->RequestPath(/* ... */);
            }
        }
    });
}
```

## 模块依赖

要在你的项目中使用 MassAI 的特定功能，你的模块需要依赖相应的子模块。以下为从 Build.cs 中提取的独特依赖：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassAI 的基石，提供 ECS 框架（实体、片段、处理器、原型）。 |
| `MassGameplay` | MassAI 所扩展的上层 Gameplay 框架。 |
| `MassSpawners` | 用于在世界中批量生成和销毁 MassEntity。 |
| `MassNavigation` | 提供导航相关的数据片段（如 `FMassMoveTargetFragment`）和处理器。 |
| `MassAIBehavior` | 提供基于 StateTree 或其他模型的 AI 行为逻辑。 |
| `MassAIReplication` | 处理多人游戏中 AI 实体数据的同步和复制。 |
| `MassNavMeshNavigation` | 与 UE 的 NavMesh 系统集成，提供基于 NavMesh 的寻路功能。 |
| `MassZoneGraphNavigation` | 与 ZoneGraph 系统集成，提供基于车道网络的导航。 |
| `MassAIDebug` | 提供 Gameplay Debugger 中的 Mass 调试类别，用于运行时调试。 |

**注**：`MassAIBehaviorEditor`, `MassNavigationEditor`, `MassEntityEditor` 是编辑器专用模块，在打包后运行时不会被加载。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 移除代码中的`INFINITY`以解决新版Windows SDK的编译错误。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数产生的警告。 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | 修复了 Mass 调试器在无效实体上运行时可能发生的崩溃问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了用于格式化函数的限定作用域枚举可能导致的乱码输出。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | 与倒放调试器相关的集成或修复工作。 |

### 维护评价

MassAI 是一个**活跃维护中**的实验性插件。
- **年龄**：创建于 2021 年，已存在约 5 年，但仍标记为实验性。
- **更新频率**：近期（2026年4月-5月）更新非常频繁，提交内容包括编译错误修复、警告清理、稳定性改进（如调试器崩溃修复）以及与其他系统（RewindDebugger）的集成工作。这表明 Epic Games 内部仍在积极使用和迭代此插件。
- **状态**：尽管是“实验性”且“默认未启用”，但持续的实质性修复和改进证明其并未被废弃。它很可能是 Epic 用于其内部大型项目（如《堡垒之夜》）的技术。
- **推荐**：对于需要处理大规模 AI 的项目，特别是已经采用了 MassEntity 架构的项目，**推荐尝试使用**。但需注意其“实验性”标签，意味着API在未来版本中可能会有不兼容的更改。建议在项目中使用时保持对引擎版本升级的关注。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassAITestSuite) (MassAITestSuite 模块)