# Mass Crowd

> Spline based AI crowd system（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 人群系统 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MassCrowd` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassCrowd) | |

## 用途

Mass Crowd 插件提供了一个**基于 ZoneGraph（区域图）的、可扩展的高性能人群模拟系统**。它利用 Unreal Engine 的 Mass Entity 框架来管理成百上千甚至上万个 AI 代理（NPC），并将其约束在预先绘制的样条线道路网络（ZoneGraph）上。

该插件解决了大规模人群模拟的核心问题：
1.  **路径与决策**：NPC 不是随机游走，而是严格遵循 ZoneGraph 定义的车道和交叉口。插件为每条车道构建运行时数据，用于支持分支决策（如在交叉口选择转向）。
2.  **密度与流量控制**：通过“密度标签”（Density Tag）和“权重”系统，在交叉口进行车道选择，以维持整体的人群密度平衡，避免所有 NPC 涌向同一条路。
3.  **状态管理**：支持车道的动态开启和关闭（如模拟交通灯），并为需要等待的场景（如等待车道开放）提供专门的等待区域（Wait Area）和槽位（Slot）管理。
4.  **性能优化**：集成 Mass 框架的批处理和并行处理能力，并包含 LOD（细节层级）系统，确保大量实体的高效渲染和模拟。

简单来说，它是 UE5 中构建可信、可控、高性能的城市级或场馆级 NPC 人群的底层核心框架。

## 使用场景

-   **开放世界游戏**：你需要在城市街道上生成大量自然行走、等待红绿灯、会避让其他 NPC 和障碍物的行人。
-   **大型场馆模拟**：你需要模拟体育场、商场、广场等场所中成百上千观众或访客的流动与聚集。
-   **需要基于路网的人群行为**：你不希望 NPC 完全自由移动，而是希望他们遵循特定的道路网络、在交叉口做出选择性决策。
-   **需要动态改变人群流向**：例如，根据剧情关闭某条街道，或模拟交通灯控制人群过马路。

**不适用场景**：小规模、无固定路径、需要复杂寻路的 AI（例如 RTS 中的士兵、需自行寻路避开复杂障碍的角色），这些更适合使用传统的 AI 系统（如 Behavior Tree + NavMesh）。

## 蓝图用法

Mass Crowd 主要通过 `UMassCrowdSubsystem` 子系统提供蓝图可调用的接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Has Crowd Data For Zone Graph` | 检查指定的 ZoneGraph 是否已生成人群运行时数据 | `UMassCrowdSubsystem` |
| `Get Crowd Data` | 获取指定 ZoneGraph 的人群运行时数据（只读） | `UMassCrowdSubsystem` |
| `Get Crowd Lane Data` | 获取指定车道的人群数据（状态、密度等） | `UMassCrowdSubsystem` |
| `Get Crowd Tracking Lane Data` | 获取指定车道的实体跟踪数据（当前有多少实体在此车道） | `UMassCrowdSubsystem` |
| `Get Crowd Branching Lane Data` | 获取指定车道的分支数据 | `UMassCrowdSubsystem` |
| `Get Crowd Waiting Area Data` | 获取指定车道的等待区域数据（槽位占用情况） | `UMassCrowdSubsystem` |
| `Get Lane State` | 获取车道的当前状态（打开/关闭） | `UMassCrowdSubsystem` |
| `Set Lane State` | 设置车道的状态（打开/关闭），例如模拟交通灯 | `UMassCrowdSubsystem` |
| `Acquire Waiting Slot` | 为实体在指定的等待车道上获取一个等待槽位 | `UMassCrowdSubsystem` |
| `Release Waiting Slot` | 释放之前获取的等待槽位 | `UMassCrowdSubsystem` |
| `Get Density Mask` | 获取所有可能的密度标签掩码 | `UMassCrowdSubsystem` |
| `Get Density Weight` | 根据车道的密度标签获取其权重 | `UMassCrowdSubsystem` |

### 使用示例（蓝图描述）

1.  **查询与监控**：在蓝图中，首先通过 `Get Game Instance Subsystem` 节点获取 `UMassCrowdSubsystem`。使用 `Has Crowd Data For Zone Graph` 检查你的 `AZoneGraphData` Actor 是否已准备好，然后用 `Get Crowd Lane Data` 轮询特定车道的流量，用于 UI 显示。
2.  **控制交通**：当你的游戏逻辑需要关闭一条车道时（例如事故），调用 `Set Lane State`，传入 `ECrowdLaneState::Closed`。人群会自动在路口等待或选择其他道路。
3.  **管理等待**：在交叉口或狭窄通道，你可以使用 `Acquire Waiting Slot` 为一个即将到达的 NPC 预订一个位置，确保它们能有序排队。

## C++ 用法

该插件的核心使用模式是通过 `UMassCrowdSubsystem` 来管理和查询人群数据。

### 头文件引入

```cpp
#include "MassCrowdSubsystem.h"
#include "MassCrowdTypes.h"
```

### 基本用法

```cpp
// 获取 MassCrowd 子系统
UMassCrowdSubsystem* CrowdSubsystem = UWorld::GetSubsystem<UMassCrowdSubsystem>(World);
if (!CrowdSubsystem)
{
    return;
}

// 假设你有一个 ZoneGraphData 句柄 (FZoneGraphDataHandle)
FZoneGraphDataHandle MyGraphDataHandle = ...;

// 1. 检查子系统是否包含该图的数据
if (CrowdSubsystem->HasCrowdDataForZoneGraph(MyGraphDataHandle))
{
    // 2. 获取车道句柄并改变其状态
    FZoneGraphLaneHandle SomeLaneHandle = ...;
    bool bSuccess = CrowdSubsystem->SetLaneState(SomeLaneHandle, ECrowdLaneState::Closed);

    // 3. 查询车道状态
    ECrowdLaneState CurrentState = CrowdSubsystem->GetLaneState(SomeLaneHandle);

    // 4. 查询车道上的实体数量
    const FCrowdTrackingLaneData* TrackingData = CrowdSubsystem->GetCrowdTrackingLaneData(SomeLaneHandle);
    if (TrackingData)
    {
        int32 EntityCount = TrackingData->NumEntitiesOnLane;
    }
}
```

### 进阶用法

管理一个需要过马路的 NPC：
```cpp
// 假设实体 Entity 正在接近一个红灯路口 (CrossingLaneHandle)
FZoneGraphLaneHandle CrossingLaneHandle = ...;

// 1. 为实体申请一个等待槽位
FVector SlotPosition, SlotDirection;
int32 SlotIndex = CrowdSubsystem->AcquireWaitingSlot(Entity, Entity->GetActorLocation(), CrossingLaneHandle, SlotPosition, SlotDirection);

if (SlotIndex != INDEX_NONE)
{
    // 2. 将 NPC 移动到 SlotPosition，面向 SlotDirection 等待
    // ... (设置移动目标)
    // NPC 等待逻辑...
}

// 3. 当灯变绿时（车道状态变为 Opened），释放槽位
CrowdSubsystem->ReleaseWaitingSlot(Entity, CrossingLaneHandle, SlotIndex);
```

## Demo 示例

一个最小的测试 Actor，用于查询并关闭指定车道。

### MassCrowdTestActor.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ZoneGraphTypes.h"
#include "MassCrowdTestActor.generated.h"

UCLASS()
class AMassCrowdTestActor : public AActor
{
    GENERATED_BODY()

public:
    AMassCrowdTestActor();

    // 在编辑器中指定一个 ZoneGraph 车道
    UPROPERTY(EditAnywhere, Category = "Crowd Test")
    FZoneGraphLaneHandle TargetLane;

    // 要设置的新状态
    UPROPERTY(EditAnywhere, Category = "Crowd Test")
    ECrowdLaneState NewLaneState = ECrowdLaneState::Closed;

    // 调用此函数来测试关闭车道
    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Crowd Test")
    void TestCloseLane();

    // 调用此函数来测试查询数据
    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Crowd Test")
    void TestQueryLaneData();
};
```

### MassCrowdTestActor.cpp

```cpp
#include "MassCrowdTestActor.h"
#include "MassCrowdSubsystem.h"
#include "MassCrowdTypes.h"
#include "ZoneGraphSubsystem.h"

AMassCrowdTestActor::AMassCrowdTestActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMassCrowdTestActor::TestCloseLane()
{
    UWorld* World = GetWorld();
    if (!World) return;

    UMassCrowdSubsystem* CrowdSubsystem = World->GetSubsystem<UMassCrowdSubsystem>();
    if (!CrowdSubsystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("MassCrowdSubsystem not found!"));
        return;
    }

    if (!TargetLane.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("TargetLane is not valid."));
        return;
    }

    bool bSuccess = CrowdSubsystem->SetLaneState(TargetLane, NewLaneState);
    UE_LOG(LogTemp, Log, TEXT("SetLaneState for lane %s to %s: %s"),
        *TargetLane.ToString(),
        (NewLaneState == ECrowdLaneState::Opened ? TEXT("Opened") : TEXT("Closed")),
        bSuccess ? TEXT("Success") : TEXT("Failed"));
}

void AMassCrowdTestActor::TestQueryLaneData()
{
    UWorld* World = GetWorld();
    if (!World) return;

    UMassCrowdSubsystem* CrowdSubsystem = World->GetSubsystem<UMassCrowdSubsystem>();
    if (!CrowdSubsystem) return;

    if (!TargetLane.IsValid()) return;

    // 查询状态
    ECrowdLaneState CurrentState = CrowdSubsystem->GetLaneState(TargetLane);
    UE_LOG(LogTemp, Log, TEXT("Current Lane State: %s"),
        (CurrentState == ECrowdLaneState::Opened ? TEXT("Opened") : TEXT("Closed")));

    // 查询跟踪数据
    const FCrowdTrackingLaneData* TrackingData = CrowdSubsystem->GetCrowdTrackingLaneData(TargetLane);
    if (TrackingData)
    {
        UE_LOG(LogTemp, Log, TEXT("Entities on lane: %d"), TrackingData->NumEntitiesOnLane);
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("No tracking data for this lane."));
    }
}
```

## 模块依赖

该插件依赖于 Mass 框架和 ZoneGraph 系统。要在你的模块中使用它，你需要在 `.Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `MassCrowd` | 人群系统核心模块 |
| `ZoneGraph` | 提供基础的道路网络和区域图功能 |
| `MassGameplay` | Mass 框架的游戏玩法层，包含实体、碎片、处理器等核心概念 |
| `MassAI` | Mass 框架的 AI 集成，通常包含行为树/状态树与 Mass 的桥接 |
| `StateTree` | 为 Mass 实体提供行为逻辑的状态树任务（如寻找漫游目标、申请等待槽位） |

**注意**：这些依赖项在 `MassCrowd.uplugin` 中已声明启用，确保它们被正确加载。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在人群模拟中处理非木偶 Actor 的问题 |
| 2026-05-12 | `363b5f58` | [MassRepresentation] Centralize representation-type debug colors and fix MassTraffic.DebugVisualizat | 集中了表现类型的调试颜色并修复了 MassTraffic 的调试可视化 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 将 MassCore 头文件移动到 Public/Mass/ 子目录，并从文件名中去除了 Mass 前缀 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 中提取了独立的 MassCore 模块 |
| 2026-03-19 | `fb672547` | [Mass][ISKM] Add Basic Instanced Skinned Mesh Support To MassRepresentation | 为 MassRepresentation 添加了基础的实例化蒙皮网格体支持 |

### 维护评价

MassCrowd 插件创建于 2021 年，属于 **Mass 生态系统的早期组件**。从近期的提交记录来看（最新提交在 2026 年 5 月），它**仍在积极维护中**，并伴随着整个 Mass 框架的演进而不断更新。近期的改动主要集中在**底层重构**（如模块拆分、文件结构调整）和**功能增强**（如修复特定Actor处理、增加新的网格体支持），而非大规模的功能重写。

尽管插件被标记为**实验性（IsExperimentalVersion = true）** 且**默认未启用（EnabledByDefault = false）**，这表明 Epic 可能对其 API 稳定性或功能完整性仍持谨慎态度，但持续的活跃更新表明它是一个**有生命力且被持续投资的系统**。

**推荐程度**：如果你的项目确实需要**大规模、基于固定路网的人群模拟**，且你愿意承担实验性 API 可能带来的风险，那么 MassCrowd 是目前 UE5 内置的唯一且正在快速发展的官方解决方案，**推荐进行技术预研和集成**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassCrowd)
- [官方文档]()（当前为空）
- [测试用例]()（根据插件结构，测试可能位于 `Engine/Tests/` 目录下，需自行搜索）