# MassNavMeshNavigation

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 中文名 | NavMesh导航模块 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（导航片段、处理器） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavMeshNavigation` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI) | |

## 用途

`MassNavMeshNavigation` 是 `MassAI` 插件中的一个核心模块，专为基于 Unreal Engine Navigation Mesh (NavMesh) 的大规模 AI 实体导航而设计。它解决了在存在大量需要寻路和移动的 AI 代理时，传统逐个代理处理方式带来的性能瓶颈问题。

该模块通过将导航数据（如路径点、边界信息）组织为 Mass 框架的片段 (`Fragment`)，并使用专用的处理器 (`Processor`) 进行批量、缓存友好的计算，从而高效地管理成百上千个 AI 实体的路径跟随、路径更新和移动意图。它扩展了 `MassGameplay` 的移动系统，使其能够处理基于 NavMesh 的复杂路径跟随逻辑。

## 使用场景

- **大规模 RTS/MOBA 游戏**：管理成百上千个单位在 NavMesh 上的集体移动和寻路。
- **开放世界游戏的 NPC 群体**：为城镇、街道或战场上的大量 NPC 提供高效、自动化的导航能力。
- **模拟游戏**：在《模拟城市》或主题公园模拟等游戏中，驱动大量市民或游客的自主移动。
- **任何需要高性能 AI 移动的场景**：当你需要让大量 AI 角色在复杂地形上自主移动，且性能是关键考量时，应使用此模块。

## 蓝图用法

本模块的蓝图接口主要集中在实体特征 (`Trait`) 和工具函数上，用于配置和触发导航行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `NavMesh Navigation` (Trait) | 为实体模板添加 NavMesh 导航能力，配置所需的数据片段。 | `UMassNavMeshNavigationTrait` |
| `ActivateActionStand` | 工具函数，用于将实体的移动目标设置为“站立”状态，并重置短路径。 | `UE::MassNavigation` (命名空间) |
| `ActivateActionAnimate` | 工具函数，用于激活实体的动画移动意图。 | `UE::MassNavigation` (命名空间) |

### 使用示例（蓝图描述）

1.  **配置实体导航能力**：在实体生成器（Entity Spawner）或 Mass Actor 中，添加 `NavMesh Navigation` Trait。这会在生成的实体上自动添加 `FMassNavMeshShortPathFragment` 和 `FMassNavMeshCachedPathFragment` 等必要的导航数据片段。
2.  **在行为逻辑中触发导航**：在自定义的蓝图或行为处理器中，当需要一个实体开始移动到某个地点时，可以通过 `RequestShortPath` 函数（C++层）或相关的信号系统，为该实体的 `FMassNavMeshShortPathFragment` 请求一条新的短路径。
3.  **处理路径跟随**：`UMassNavMeshPathFollowProcessor` 会自动处理所有带有 `FMassNavMeshShortPathFragment` 的实体，根据路径点更新它们的移动目标。蓝图通常不直接操作此处理器，而是通过修改片段数据来间接影响移动。
4.  **动画同步**：使用 `ActivateActionAnimate` 函数来通知移动系统，实体应该开始播放移动动画，这通常与路径跟随处理器的输出配合使用。

## C++ 用法

### 头文件引入

要使用此模块的功能，需要包含对应的公共头文件。

```cpp
#include "MassNavMeshNavigation/MassNavMeshNavigationFragments.h"   // 数据片段
#include "MassNavMeshNavigation/MassNavMeshNavigationProcessors.h" // 处理器
#include "MassNavMeshNavigation/MassNavMeshNavigationUtils.h"     // 工具函数
```

### 基本用法

**配置查询和处理片段（来自处理器源码模式）**

自定义处理器时，需要查询包含 `FMassNavMeshShortPathFragment` 的实体进行处理。

```cpp
// 简化自 UMassNavMeshPathFollowProcessor::ConfigureQueries
void UMyCustomNavProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    Super::ConfigureQueries(EntityManager);

    // 查询需要路径跟随更新的实体：必须有短路径片段和移动目标片段
    EntityQuery.AddRequirement<FMassNavMeshShortPathFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadWrite);
    // ... 添加其他需求的片段，如 Transform
    EntityQuery.RegisterWithProcessor(*this);
}
```

**请求短路径（模拟内部逻辑）**

当实体需要新路径时，会调用 `FMassNavMeshShortPathFragment::RequestShortPath`。

```cpp
// 假设我们已经有了导航路径 (FNavPathSharedPtr) 和走廊数据 (TSharedPtr<FNavCorridor>)
FMassNavMeshShortPathFragment& ShortPathFragment = /* 从实体获取 */;

// 从缓存的完整路径（Corridor）中提取一小段作为短路径
if (ShortPathFragment.RequestShortPath(CachedPathFragment->Corridor, NextStartIndex, LeadingPoints, EndDistance))
{
    // 短路径请求成功，处理器将在下一帧处理这个实体的移动
}
```

### 进阶用法

**组合边界处理器与路径跟随**

`UMassNavMeshNavigationBoundaryProcessor` 使用 `FMassNavMeshShortPathFragment` 的数据来填充 `FMassNavigationEdgesFragment`，为移动系统提供障碍物边界信息。这两个处理器协同工作：

```cpp
// UMassNavMeshNavigationBoundaryProcessor::Execute 的核心逻辑（简化）
// 获取实体的短路径，用路径点计算左右边界，写入到 FMassNavigationEdgesFragment
for (FMassEntityHandle Entity : Context.GetEntities())
{
    FMassNavMeshShortPathFragment& ShortPath = Context.GetMutableFragment<FMassNavMeshShortPathFragment>(Entity);
    FMassNavigationEdgesFragment& Edges = Context.GetMutableFragment<FMassNavigationEdgesFragment>(Entity);

    // 基于 ShortPath.Points 和当前位置，计算 Edges.Left 和 Edges.Right
    CalculateNavigationEdges(ShortPath, EntityLocation, Edges);
}
```

**处理路径完成状态**

路径跟随处理器会检查实体是否到达路径终点。

```cpp
// 简化自 UMassNavMeshPathFollowProcessor::CheckEndOfPathReached
void UMassNavMeshPathFollowProcessor::CheckEndOfPathReached(...)
{
    const FVector PathEndPoint = ShortPath.Points[EndPointIndex].Position;
    const float DistanceToPathEnd = FVector::Distance(EntityLocation, PathEndPoint);

    // 检查是否满足结束距离阈值
    if (DistanceToPathEnd <= ShortPath.EndReachedDistance)
    {
        ShortPath.bDone = true; // 标记路径跟随完成
        // 可以发送信号通知其他系统（如行为树）
        SignalSubsystem->SignalEntities(UE::Mass::Signals::FollowPathComplete, {Entity});
    }
}
```

## Demo 示例

以下是一个最小化的自定义处理器示例，展示如何集成 `MassNavMeshNavigation` 模块来检查实体的路径跟随状态。

```cpp
// MyNavStatusChecker.h
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MyNavStatusChecker.generated.h"

UCLASS()
class UMyNavStatusChecker : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyNavStatusChecker();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyNavStatusChecker.cpp
#include "MyNavStatusChecker.h"
#include "MassNavMeshNavigation/MassNavMeshNavigationFragments.h"
#include "MassCommonFragments.h" // 用于 FTransformFragment

UMyNavStatusChecker::UMyNavStatusChecker()
{
    // 设置处理器执行顺序，确保在路径跟随之后
    ProcessingPhase = EMassProcessingPhase::PostPhysics;
    ExecutionFlags = static_cast<int32>(EProcessorExecutionFlags::All);
}

void UMyNavStatusChecker::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 我们需要读取路径状态和实体位置
    EntityQuery.AddRequirement<FMassNavMeshShortPathFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.RegisterWithProcessor(*this);
}

void UMyNavStatusChecker::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有符合条件的实体
    EntityQuery.ForEachEntityChunk(Context, [&](FMassExecutionContext& Context)
    {
        const TConstArrayView<FMassNavMeshShortPathFragment> ShortPathList = Context.GetFragmentView<FMassNavMeshShortPathFragment>();
        const TConstArrayView<FTransformFragment> TransformList = Context.GetFragmentView<FTransformFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FMassNavMeshShortPathFragment& ShortPath = ShortPathList[i];
            const FVector EntityLocation = TransformList[i].GetTransform().GetLocation();

            // 检查路径状态
            if (ShortPath.IsDone())
            {
                UE_LOG(LogTemp, Log, TEXT("Entity %s has finished following its NavMesh path."), *Context.GetEntity(i).ToString());
                // 在这里执行路径完成后的逻辑
            }
            else
            {
                // 可以打印当前进度
                UE_LOG(LogTemp, Verbose, TEXT("Entity %s is following path, progress distance: %.2f"),
                    *Context.GetEntity(i).ToString(), ShortPath.MoveTargetProgressDistance);
            }
        }
    });
}
```

**注意**: 实际使用中，你需要确保 `UMyNavStatusChecker` 被正确注册到实体管理器中，并且其执行顺序与 `UMassNavMeshPathFollowProcessor` 配合。

## 模块依赖

从 `MassNavMeshNavigation.Build.cs` 分析，该模块的主要依赖如下：

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心的 Mass 实体框架，提供片段、处理器、实体管理器等基础。 |
| `MassNavigation` | Mass 移动系统模块，提供通用的移动片段（如 `FMassMoveTargetFragment`）和移动处理器接口。 |
| `NavigationSystem` | UE 的导航系统核心模块，提供 `FNavPath`, `FNavCorridor` 等导航数据结构和查询接口。 |
| `AIModule` | AI 模块，可能提供与行为树或AI感知相关的集成。 |

**注意**：此模块的 `Build.cs` 还列出了对 `EditorFramework` 和 `UnrealEd` 的依赖，这通常意味着该模块包含了一些仅在编辑器环境下使用的代码（例如用于调试或可视化），但这些不影响核心运行时功能的使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 移除 INFINITY 的使用以修复在最新 Windows SDK 上的编译错误。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量转换为单精度时产生的警告代码。 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | 修复 Mass 调试器在处理无效实体时运行的问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中使用的域枚举可能导致乱码输出的问题。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | (与本模块关联性较弱，可能为其他AI模块的提交) |

### 维护评价

- **创建时间**：2021年9月，已存在近5年。
- **最近更新**：最后一次实质性更新（针对 `MassAI` 插件根目录）停留在2024年11月左右。2026年的提交主要是针对 **编译警告和错误** 的修复（如 `INFINITY` 和 `double` 截断警告），属于平台兼容性维护，而非新功能开发或重大架构变更。
- **维护状态**：**维护不活跃**。核心功能已趋于稳定，近两年没有新功能或重大重构的迹象。更新仅限于必要的编译修复。
- **已知问题/限制**：作为实验性（`IsExperimentalVersion`）且默认禁用（`EnabledByDefault=false`）的插件，其 API 和功能可能在未来版本中发生变化，不建议在需要长期稳定支持的生产项目中重度依赖。
- **推荐使用**：**谨慎推荐**。如果你正在开发一个对 AI 移动性能有极高要求、且愿意接受实验性 API 可能变动的大型项目，可以尝试使用。对于中小型项目或对稳定性要求高的项目，建议先评估标准 `MassGameplay` 移动系统是否能满足需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)
- [官方文档](https://docs.unrealengine.com/) (暂无特定文档链接，可查阅通用的 Mass 框架和 AI 文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassAITestSuite) (MassAITestSuite 模块包含相关测试)