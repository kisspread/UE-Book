# Mass Crowd

> Spline based AI crowd system

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置文件、内容资产） |
| 模块 | `MassCrowd` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassCrowd) | |

## 用途

MassCrowd 是基于 Mass Entity 框架和 ZoneGraph 路径系统的大规模人群仿真插件。它解决的核心问题是：**在 ZoneGraph 定义的路网上高效管理成千上万的行人实体**，包括车道追踪、交叉路口等待、密度控制、障碍物避让和网络复制。

与基础的 MassNavigation 不同，MassCrowd 专门针对行人场景做了以下扩展：

- **车道级密度控制**：通过 ZoneGraph Tag 定义不同密度，交叉路口选择时根据权重维持整体密度均衡
- **交叉路口等待机制**：支持临时关闭车道（如红绿灯），行人实体在等待区域排队，车道重新开放后有序进入
- **人群专用 LOD**：独立于交通系统的人群 LOD 处理器，实现并行化
- **网络复制**：专门的人群 Agent 复制管线（Bubble 机制），支持多人在线场景

## 使用场景

- 你在做城市模拟游戏，需要在街道上生成大量行人 → 用 MassCrowd
- 你需要交叉路口红绿灯控制行人通行 → MassCrowd 的车道关闭/等待机制
- 你已经在用 MassAI + ZoneGraph 做 NPC 寻路，想要更高效的人群管理 → 用 MassCrowd 替代逐个 Actor 的方案
- 你需要多人在线游戏中同步大量人群实体 → MassCrowd 的复制系统

## 蓝图用法

MassCrowd 本身提供的蓝图接口较少，核心逻辑通过 Trait 和 Processor 自动注册。以下是可以直接在蓝图中使用的组件：

### 核心组件

| 组件 | 说明 | 所在类 |
|---|---|---|
| `ZoneGraphCrowdLaneAnnotations` | ZoneGraph 注解组件，处理车道状态变化事件，维护 Opened/Closed 标记 | `UZoneGraphCrowdLaneAnnotations` |
| `MassCrowdLaneDataRenderingComponent` | 调试渲染组件，显示车道状态、密度、占用信息 | `UMassCrowdLaneDataRenderingComponent` |

### Entity Template Trait

在 Mass Entity 模板编辑器中可以添加以下 Trait：

| Trait | 显示名称 | 说明 |
|---|---|---|
| `UMassCrowdMemberTrait` | CrowdMember | 标记实体为人群成员，添加 `FMassCrowdTag` 和 `FMassCrowdLaneTrackingFragment` |
| `UMassCrowdVisualizationTrait` | Crowd Visualization | 人群可视化 Trait，继承自 `UMassVisualizationTrait` |
| `UMassCrowdServerRepresentationTrait` | Crowd Server Representation | 服务端表示 Trait，可配置模板 Actor 类 |

### 使用示例（蓝图描述）

1. 在场景中的 ZoneGraphData Actor 上添加 `UZoneGraphCrowdLaneAnnotations` 组件
2. 配置 `CloseLaneTag` 和 `WaitingLaneTag` 指向你定义的 ZoneGraph Tag
3. 创建 Mass Entity 模板，添加 CrowdMember + Crowd Visualization + 路径跟随相关 Trait
4. 使用 MassSpawner 生成实体

## C++ 用法

### 头文件引入

```cpp
#include "MassCrowdSubsystem.h"
#include "MassCrowdFragments.h"
#include "MassCrowdTypes.h"
```

### 基本用法 — 查询人群车道数据

```cpp
// 获取 MassCrowd 子系统
UMassCrowdSubsystem* CrowdSubsystem = GetWorld()->GetSubsystem<UMassCrowdSubsystem>();

// 检查是否有指定 ZoneGraph 的人群数据
if (CrowdSubsystem->HasCrowdDataForZoneGraph(DataHandle))
{
    // 获取车道运行时数据
    TOptional<FZoneGraphCrowdLaneData> LaneData = CrowdSubsystem->GetCrowdLaneData(LaneHandle);
    if (LaneData.IsSet())
    {
        ECrowdLaneState State = LaneData.GetValue().GetState();
        // ECrowdLaneState::Opened 或 ECrowdLaneState::Closed
    }

    // 获取车道占用追踪数据（实体计数）
    const FCrowdTrackingLaneData* TrackingData = CrowdSubsystem->GetCrowdTrackingLaneData(LaneHandle);
    if (TrackingData)
    {
        int32 NumEntities = TrackingData->NumEntitiesOnLane;
    }

    // 获取等待区域数据
    const FCrowdWaitAreaData* WaitArea = CrowdSubsystem->GetCrowdWaitingAreaData(LaneHandle);
    if (WaitArea)
    {
        int32 FreeSlots = WaitArea->GetNumFreeSlots();
    }
}
```

### 进阶用法 — 控制车道状态

```cpp
// 关闭一条车道（例如红绿灯变红）
FZoneGraphLaneHandle LaneHandle = ...;
CrowdSubsystem->SetLaneState(LaneHandle, ECrowdLaneState::Closed);

// 重新开放车道
CrowdSubsystem->SetLaneState(LaneHandle, ECrowdLaneState::Opened);

// 获取密度权重（用于交叉路口车道选择）
FZoneGraphTagMask LaneTagMask = ...;
float Weight = CrowdSubsystem->GetDensityWeight(LaneHandle, LaneTagMask);
```

### 进阶用法 — 等待槽位管理

```cpp
// 实体在交叉路口等待时获取一个等待槽位
FMassEntityHandle Entity = ...;
FVector EntityPosition = ...;
FVector OutSlotPosition, OutSlotDirection;
int32 SlotIndex = CrowdSubsystem->AcquireWaitingSlot(
    Entity, EntityPosition, WaitingLaneHandle,
    OutSlotPosition, OutSlotDirection);

if (SlotIndex != INDEX_NONE)
{
    // 移动到 OutSlotPosition 等待
}

// 通过后释放槽位
CrowdSubsystem->ReleaseWaitingSlot(Entity, WaitingLaneHandle, SlotIndex);
```

### StateTree Task

MassCrowd 提供两个 StateTree Task，用于在 StateTree 行为树中驱动人群行为：

```cpp
// FMassZoneGraphFindWanderTarget: 在 ZoneGraph 上寻找漫游目标
// 输出: FMassZoneGraphTargetLocation WanderTargetLocation
// 参数: FZoneGraphTagFilter AllowedAnnotationTags（过滤允许的注解标签）

// FMassCrowdClaimWaitSlot: 申请等待槽位并输出位置
// 输出: FMassZoneGraphTargetLocation WaitSlotLocation
// 进入状态时自动申请槽位，退出时自动释放
```

## Demo 示例

### 自定义人群处理器（读取人群数据）

```cpp
// MyCrowdProcessor.h
#pragma once

#include "MassProcessor.h"
#include "MyCrowdProcessor.generated.h"

UCLASS()
class UMyCrowdProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyCrowdProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyCrowdProcessor.cpp
#include "MyCrowdProcessor.h"
#include "MassCrowdFragments.h"
#include "MassCrowdSubsystem.h"
#include "MassExecutionContext.h"

UMyCrowdProcessor::UMyCrowdProcessor()
{
    ExecutionOrder.ExecuteInGroup = TEXT("MyCrowdGroup");
    ExecutionOrder.ExecuteAfter.Add(TEXT("MassCrowdLaneTracking"));
    bAutoRegisterWithProcessingPhases = true;
}

void UMyCrowdProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMassCrowdTag>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassCrowdLaneTrackingFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.RegisterWithProcessor(*this);
}

void UMyCrowdProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    UMassCrowdSubsystem* CrowdSubsystem = EntityManager.GetWorld()->GetSubsystem<UMassCrowdSubsystem>();

    EntityQuery.ForEachEntityChunk(EntityManager, Context, 
        [&CrowdSubsystem](FMassExecutionContext& Context)
    {
        const TConstArrayView<FMassCrowdLaneTrackingFragment> LaneTrackingList = 
            Context.GetFragmentView<FMassCrowdLaneTrackingFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FZoneGraphLaneHandle& LaneHandle = LaneTrackingList[i].TrackedLaneHandle;
            if (LaneHandle.IsValid())
            {
                const FCrowdTrackingLaneData* TrackingData = 
                    CrowdSubsystem->GetCrowdTrackingLaneData(LaneHandle);
                // 处理人群数据...
            }
        }
    });
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "MassEntity",
    "MassCommon",
    "MassCrowd",
    "ZoneGraph"
});
```

## 模块依赖

从 `MassCrowd.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass Entity 框架核心（Entity、Fragment、Tag） |
| `MassCommon` | Mass 通用类型和工具 |
| `MassActors` | Mass Actor 生成与管理 |
| `MassLOD` | Mass LOD 计算与分级 |
| `MassMovement` | Mass 移动系统 |
| `MassNavigation` | Mass 导航系统 |
| `MassZoneGraphNavigation` | Mass + ZoneGraph 导航集成 |
| `MassReplication` | Mass 网络复制框架 |
| `MassAIReplication` | Mass AI 专用复制逻辑 |
| `MassSignals` | Mass 信号系统（用于车道变更通知） |
| `MassSimulation` | Mass 仿真循环 |
| `MassSpawner` | Mass 实体生成器 |
| `MassRepresentation` | Mass 可视化表示（ISM、Actor） |
| `MassAIBehavior` | Mass AI 行为框架（StateTree 集成） |
| `AIModule` | AI 基础模块 |
| `Core` / `CoreUObject` / `Engine` | 引擎基础模块 |
| `NetCore` | 网络核心 |
| `StateTreeModule` | StateTree 行为树框架 |
| `ZoneGraph` | ZoneGraph 路网系统 |
| `ZoneGraphAnnotations` | ZoneGraph 注解系统（车道状态标记） |
| `ZoneGraphDebug` | ZoneGraph 调试工具 |

**插件级依赖**（在 .uplugin 中声明）：ZoneGraph、MassGameplay、MassAI、StateTree

## 维护状态

### 近期更新

1. `2a264ce3c015` | 2025-07-11 | Used UnrealCodeFixup to fix dll storage on code
   - 自动化代码修复工具批量修正 DLL 导出宏，无功能性变更

2. `04930821cdf6` | 2025-07-11 | Run UnrealCodeFixup to add #include UE_INLINE_GENERATED_CPP_BY_NAME to files where possible
   - 自动化工具添加 UE_INLINE_GENERATED_CPP_BY_NAME 头文件包含，编译优化相关

3. `52abf4910fa1` | 2025-05-26 | Mass Observers can now differentiate between Add and Created operations as well as between Remove and Destroy operations
   - Mass 框架层面的 Observer 处理器改进，MassCrowd 的 Observer 处理器（如 `UMassCrowdLaneTrackingDestructor`、`UMassCrowdDynamicObstacleInitializer` 等）受益于此变更

### 维护评价

MassCrowd 插件自 2021 年 9 月创建以来持续维护。最近的更新集中在 2025 年 5-7 月，主要是框架层面的自动代码修复和 Mass Observer 机制改进，说明该插件仍在 Epic 的维护范围内。

**注意**：
- 该插件标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 可能随版本变化
- 作为 Mass Entity 框架的上层应用，其稳定性依赖于底层 Mass 模块的成熟度
- 推荐在需要大规模人群仿真的项目中使用，但需做好 API 变更的准备
- 与 MassTraffic 插件共享部分架构设计，但针对行人场景做了独立优化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassCrowd)
- 官方文档（无）
