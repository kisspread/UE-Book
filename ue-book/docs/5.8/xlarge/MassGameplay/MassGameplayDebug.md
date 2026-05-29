# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模仿真 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是一个基于 MassEntity 框架构建的大型智能体仿真系统。它提供了一套完整的游戏实体（Agent）行为、移动、视觉呈现、LOD 管理、网络复制和调试的解决方案。这个插件的核心目的是在 Unreal Engine 中高效地模拟和渲染数以千计甚至数以万计的游戏角色，适用于开放世界、大规模战斗、城市人口模拟等需要极高实体密度的场景。它不是传统 AI 的替代品，而是处理超大规模实体管理的底层框架，使得开发者能够将传统的基于蓝图/行为树的游戏逻辑“批处理”式地应用到海量实体上。

## 使用场景

-   你在开发一个开放世界游戏，需要同时在场景中显示数千个平民、士兵或动物，并且它们需要具备基本的行为逻辑 → 使用 MassGameplay 的实体生成、移动和表示系统。
-   你需要创建一个大规模 RTS 游戏，单位数量远超传统 Actor 的管理能力 → 使用 MassGameplay 来管理单位的状态、寻路和战斗逻辑。
-   你需要实现复杂的 crowd simulation，如体育场、广场上的人群流动 → 结合 MassMovement 和 MassRepresentation 模块。
-   你需要对大量实体进行网络同步，并且追求带宽和性能的极致优化 → 使用 MassReplication 模块。
-   你需要对运行中的大规模仿真进行性能分析和可视化调试 → 使用 MassGameplayDebug 模块。

## 蓝图用法

MassGameplay 的核心蓝图 API 集中在实体的生成、配置和管理上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Entities In Context` | 在指定上下文（如 Mass Spawner）中生成一批实体。 | `AMassSpawner` |
| `Get Entity Manager` | 获取当前世界/上下文的实体管理器单例。 | `UWorld` |
| `Kill Entity` | 销毁一个指定的实体句柄。 | `FMassEntityFunctionLibrary` |
| `Get Entity Fragment Data` | 获取指定实体上特定类型片段（Fragment）的数据（只读）。 | `FMassEntityFunctionLibrary` |
| `Set Entity Fragment Data` | 设置指定实体上特定类型片段（Fragment）的数据（可写）。 | `FMassEntityFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **生成实体**：首先在场景中放置一个 `MassSpawner` Actor。在它的细节面板或通过蓝图调用 `Spawn Entities In Context` 节点，指定要生成的实体模板（`MassEntityTemplate`）和数量。模板定义了实体包含哪些片段（移动、表示、行为等）。
2.  **查询与修改实体数据**：在某个事件触发时（如玩家进入区域），使用 `Get Entity Manager` 获取管理器，然后通过 `Get Entity Fragment Data` / `Set Entity Fragment_data` 节点读取或修改特定实体的状态（例如，将其“警觉”片段的布尔值设为 true）。
3.  **调试可视化**：启用调试后，可以使用 `MassGameplayDebug` 模块提供的功能，在游戏视图中看到实体的状态、移动轨迹和LOD层级。

## C++ 用法

以下示例展示了如何从 C++ 侧与 MassGameplay 系统进行基础交互。

### 头文件引入

```cpp
#include "MassEntityTypes.h"
#include "MassEntitySubsystem.h"
#include "MassSpawnerSubsystem.h"
// 根据具体功能，可能还需要引入其他模块头文件，例如:
// #include "MassMovementTypes.h"
// #include "MassRepresentationTypes.h"
```

### 基本用法

**创建一个简单的实体查询（Processor 内部）**：
```cpp
// 在 UMassProcessor 的 ConfigureQueries 中定义查询
void UMyProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 查询所有包含 FDataFragment_Position 和 FMassMovementFragment 的实体
    EntityQuery.AddRequirement<FDataFragment_Position>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassMovementFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.RegisterWithProcessor(*this);
}

// 在 Execute 中处理查询结果
void UMyProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取数组访问器
        const TConstArrayView<FDataFragment_Position> PositionList = Context.GetFragmentView<FDataFragment_Position>();
        const TArrayView<FMassMovementFragment> MovementList = Context.GetMutableFragmentView<FMassMovementFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            // 读取位置，修改移动速度
            const FVector& Position = PositionList[i].Position;
            MovementList[i].MaxSpeed = 500.0f; // 设置一个新速度
        }
    });
}
```

### 进阶用法

**通过特质（Trait）向实体模板添加自定义行为**：
```cpp
UCLASS()
class UMyTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()
protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        // 向实体模板添加一个自定义的逻辑片段
        BuildContext.AddFragment<FMyCustomLogicFragment>();

        // 添加一个状态标签，用于筛选
        BuildContext.AddTag<FMyCustomStateTag>();

        // 注册一个观察者处理器，当该标签被添加/移除时触发逻辑
        BuildContext.AddObserver<FMassObserverManager::OnTagAdded>(GET_OVERRIDEN_OBSERVER_NAME(FMyCustomStateTag), UMyObserverProcessor::StaticClass());
    }
};
```

## Demo 示例

下面是一个极简的 C++ 示例，展示了如何定义一个简单的处理器来移动所有带位置和移动片段的实体。

**MyMovementProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MyMovementProcessor.generated.h"

UCLASS()
class MASSGAMEPLAY_API UMyMovementProcessor : public UMassProcessor
{
	GENERATED_BODY()

public:
	UMyMovementProcessor();

protected:
	virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
	virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
	FMassEntityQuery EntityQuery;
};
```

**MyMovementProcessor.cpp**
```cpp
#include "MyMovementProcessor.h"
#include "MassMovementTypes.h"
#include "MassCommonTypes.h"

UMyMovementProcessor::UMyMovementProcessor()
{
	// 设置执行优先级（可选）
	ExecutionFlags = static_cast<int32>(EProcessorExecutionFlags::All);
	// bAutoRegisterWithProcessingPhases = true; // 如果需要自动注册
}

void UMyMovementProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
	// 需要可写的移动片段和只读的位置片段
	EntityQuery.AddRequirement<FMassMovementFragment>(EMassFragmentAccess::ReadWrite);
	EntityQuery.AddRequirement<FDataFragment_Position>(EMassFragmentAccess::ReadOnly);
	// 可选：添加标签过滤
	EntityQuery.AddTagRequirement<FMassMovementTag>(EMassFragmentPresence::All);
	EntityQuery.RegisterWithProcessor(*this);
}

void UMyMovementProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
	EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
	{
		const TArrayView<FMassMovementFragment> MovementFragments = Context.GetMutableFragmentView<FMassMovementFragment>();
		const TConstArrayView<FDataFragment_Position> PositionFragments = Context.GetFragmentView<FDataFragment_Position>();

		for (int32 i = 0; i < Context.GetNumEntities(); ++i)
		{
			FMassMovementFragment& Movement = MovementFragments[i];
			const FVector& CurrentPosition = PositionFragments[i].Position;

			// 简单示例：让所有实体向前移动
			FVector DesiredVelocity = FVector::ForwardVector * Movement.MaxSpeed;
			Movement.Velocity = DesiredVelocity;
		}
	});
}
```

## 模块依赖

MassGameplay 依赖于其内部的多个子模块。要在你自己的游戏模块中使用它，你需要在你的 `Build.cs` 中添加对相关模块的依赖。

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的核心框架，提供实体管理、查询和处理器的基础。 |
| `MassCommon` | 包含通用的实体片段、标签和基础处理器。 |
| `MassMovement` | 处理实体的移动、路径跟随和避障。 |
| `MassRepresentation` | 处理实体的视觉表现（如ISMC、Actor）。 |
| `MassLOD` | 管理实体的LOD，根据距离和可见性动态调整行为和表现。 |
| `MassGameplayDebug` | 提供调试、可视化和诊断工具。 |
| `MassSpawner` | 提供实体的生成、配置和管理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 撤销了 MassAgentComponent 的某项更改，修复了引入的问题。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 改进实体表示逻辑，在关闭实例化静态网格体（ISM）前等待 Actor 就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在 Mass 人群仿真中对非傀儡 Actor 的处理问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 LOD 计算器中基于观察者的LOD路径存在的一簇缺陷。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | 优化了实体表示中一个帧保留标志的计算方式，使其使用新的引擎接口。 |

### 维护评价

MassGameplay 是一个大型且活跃维护的实验性插件。从近期提交记录来看，更新非常频繁（几乎每天都有提交），且集中在核心功能（表示、LOD）的修复和优化上。创建于 2021 年，已有约 5 年历史，但得益于 Epic Games 的持续投入，其代码库仍然在快速演进。

**主要特点**：
*   **实验性**：`IsExperimentalVersion=true` 且默认未启用 (`EnabledByDefault=false`)，表明其API和功能仍在发展变化中。
*   **活跃开发**：近期提交记录显示开发者仍在积极修复问题、优化性能和添加新功能。
*   **核心功能**：是实现超大规模实体仿真的官方方案，与 MassEntity 框架深度集成。
*   **复杂性**：API 和概念较为复杂，需要一定的学习和理解成本。

**推荐使用**：对于有明确大规模实体仿真需求（数百上千以上）且愿意投入时间学习和调试的项目，MassGameplay 是目前官方支持的最佳选择。但对于实体数量较少或需要高度复杂个体AI的项目，传统的 Actor + AI 系统可能更为直接。由于是实验性插件，使用前需做好应对API变动的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]() （暂无公开链接）
- [测试用例]() （测试用例可能位于 `Engine/Tests/MassGameplayTestSuite` 或项目内部）

---
# MassGameplayDebug

> MassGameplay 的调试与可视化子模块。

| 属性 | 值 |
|---|---|
| 中文名 | 大规模调试 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MassGameplayDebug` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayDebug) | |

## 用途

MassGameplayDebug 是 MassGameplay 插件中的一个专用子模块，旨在为运行中的大规模实体仿真提供强大的调试和可视化工具。它解决了在成千上万实体中快速定位、检查单个实体状态以及观察整体仿真行为分布的难题。通过这个模块，开发者可以在游戏视图中看到实体的位置、移动方向、当前状态（通过不同形状的 debug shape 表示），并能选中单个实体查看其详细的组件数据。这对于开发、测试和优化基于 MassGameplay 的系统至关重要。

## 使用场景

-   你的游戏正在运行 MassGameplay 仿真，但部分实体行为异常（如卡住、速度不对），你需要在实时运行中查看它们的状态和移动意图 → 启用调试可视化。
-   你需要评估不同 LOD 设置下实体的行为切换是否正确 → 通过观察 debug shape 的颜色或形状变化来判断。
-   你需要向团队成员或测试人员演示实体仿真系统的运行情况 → 启用清晰的 debug 绘制。
-   你在开发新的 MassProcessor，需要验证它是否正确地修改了目标实体的数据 → 选中实体并查看其详细信息。

## 蓝图用法

调试功能通常通过游戏调试器（Gameplay Debugger）或控制台命令激活，而非直接通过蓝图节点调用。但可以通过 C++ 的 `UMassDebuggerSubsystem` 接口进行控制。

### 核心节点（通常在 C++ 中使用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Selected Entity` | 获取当前通过调试器选中的实体句柄。 | `UMassDebuggerSubsystem` |
| `Get Selected Entity Info` | 获取当前选中实体的详细信息字符串。 | `UMassDebuggerSubsystem` |
| `Set Selected Entity` | （内部）设置选中的实体，并触发信息收集。 | `UMassDebuggerSubsystem` |
| `Is Collecting Data` | 查询当前是否正在为某个实体收集调试数据。 | `UMassDebuggerSubsystem` |
| `Reset Debug Shapes` | 清空所有已收集的调试形状数据。 | `UMassDebuggerSubsystem` |

### 使用示例（激活调试）

1.  **激活调试绘制**：在游戏运行时，通常按下 `'`（单引号）键打开 Gameplay Debugger，然后切换到 “Mass” 页签。或者使用控制台命令，例如 `Mass.GameplayDebug.Enable 1`。
2.  **查看实体信息**：在调试模式下，你可以用准心对准一个实体并按下相关键（如 `Shift+F1`）来选中它。此时，屏幕边缘会显示该实体的详细信息（由 `UMassDebuggerSubsystem::AppendSelectedEntityInfo` 收集）。
3.  **观察调试形状**：启用后，场景中的实体会根据其状态和类型显示不同的线条形状（盒子、胶囊、箭头等），颜色可能代表不同的 LOD 级别或状态。

## C++ 用法

调试模块主要提供数据收集和管理接口，其处理器 (`UDebugVisLocationProcessor`, `UMassProcessor_UpdateDebugVis`) 在后台运行以驱动可视化。

### 头文件引入

```cpp
#include "MassDebuggerSubsystem.h"
#include "MassGameplayDebugTypes.h"
#include "MassDebugDrawHelpers.h"
```

### 基本用法

**在自定义处理器中添加调试形状**：
```cpp
#if WITH_MASSGAMEPLAY_DEBUG
void UMyProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    UMassDebuggerSubsystem* DebugSubsystem = UWorld::GetSubsystem<UMassDebuggerSubsystem>(Context.GetWorld());
    if (DebugSubsystem && DebugSubsystem->IsCollectingData())
    {
        // 如果调试器正在收集数据，为当前实体添加一个红色盒子
        DebugSubsystem->AddShape(EMassEntityDebugShape::Box, /*Location=*/ EntityLocation, /*Size=*/ 100.0f);
    }
    // ... 常规逻辑 ...
}
#endif
```

**获取选中实体的信息**：
```cpp
void AMyDebugActor::ShowSelectedEntityInfo()
{
    UMassDebuggerSubsystem* DebugSubsystem = GetWorld()->GetSubsystem<UMassDebuggerSubsystem>();
    if (DebugSubsystem)
    {
        const FMassEntityHandle& Selected = DebugSubsystem->GetSelectedEntity();
        if (Selected.IsValid())
        {
            const FString& Info = DebugSubsystem->GetSelectedEntityInfo();
            UE_LOG(LogTemp, Log, TEXT("Selected Entity: %s\nDetails: %s"), *Selected.DebugGetDescription(), *Info);
        }
    }
}
```

### 进阶用法

**使用调试绘图助手绘制自定义标记**：
```cpp
void UMyProcessor::DebugDraw(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
#if WITH_MASSGAMEPLAY_DEBUG
    UE::Mass::Debug::FLineBatcher LineBatcher = UE::Mass::Debug::FLineBatcher::MakeLineBatcher(Context.GetWorld());
    
    // 遍历实体并绘制箭头表示移动方向
    auto MovementFragments = Context.GetFragmentView<FMassMovementFragment>();
    auto PositionFragments = Context.GetFragmentView<FDataFragment_Position>();
    for (int32 i = 0; i < Context.GetNumEntities(); ++i)
    {
        const FVector& Pos = PositionFragments[i].Position;
        const FVector& Vel = MovementFragments[i].Velocity;
        if (!Vel.IsNearlyZero())
        {
            FTransform ArrowTransform;
            ArrowTransform.SetLocation(Pos);
            ArrowTransform.SetRotation(Vel.ToOrientationQuat());
            LineBatcher.DrawArrow(ArrowTransform, /*Length=*/100.0f, FColor::Green);
        }
    }
#endif
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心实体框架，调试功能需要与其交互。 |
| `MassGameplay` | 被调试的主体插件，提供了被调试的实体和处理器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | （与主插件同步）撤销了 MassAgentComponent 的某项更改。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | （与主插件同步）改进实体表示逻辑，在关闭ISM前等待Actor就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | （与主插件同步）修复了人群仿真中对非傀儡Actor的处理问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | （与主插件同步）修复了LOD计算器中存在的一簇缺陷。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | （与主插件同步）优化了实体表示中一个帧保留标志的计算方式。 |

### 维护评价

MassGameplayDebug 作为 MassGameplay 的一部分，享受着与主插件相同的维护节奏，处于活跃更新状态。它的更新通常是随着主插件的核心功能（如 Representation， LOD）修复而一并进行的。该模块提供了不可或缺的开发调试工具，对于 MassGameplay 项目的开发效率和问题诊断至关重要。其代码相对独立，但与主插件紧密集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayDebug)
- [官方文档]() （暂无公开链接）
- [测试用例]() （可能集成在 MassGameplayTestSuite 中）