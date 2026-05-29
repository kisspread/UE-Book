# Mass Gameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、调试工具） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 UE5 大规模实体框架 **MassEntity** 的上层游戏玩法实现。它解决了"如何高效模拟成千上万个智能体（NPC、人群、生物群落等）"这一核心问题。

传统的 AActor 模型每个角色都是独立对象，拥有独立的 Tick、组件和蓝图逻辑，当数量达到数千时 CPU 开销巨大。MassGameplay 基于 MassEntity 的 ECS（实体组件系统）架构，将智能体的数据（Fragment）与行为（Processor）解耦，实现数据导向的批量处理，从而支撑海量实体的高效运行。

该插件提供以下核心能力：

- **MassMovement**：批量计算实体的移动与导航
- **MassRepresentation / MassLOD**：根据距离动态切换实体的渲染表示（ISM 静态网格、Actor 实例、不可见），支持 LOD 分级
- **MassSpawner**：在世界中批量生成/销毁 Mass 实体
- **MassReplication**：将 Mass 实体状态同步到联网客户端
- **MassEQS**：将 EQS（环境查询系统）请求异步分发到 Mass Processor 执行，实现大规模空间查询
- **MassActors**：在 Mass 实体与 Actor 之间建立桥梁，支持混合使用
- **MassSmartObjects**：集成 SmartObject 系统，让实体可与场景中的交互点互动
- **MassGameplayDebug**：运行时可视化调试工具

**注意**：此插件标记为实验性且默认禁用，需要手动在项目设置中启用。它依赖于 MassEntity 基础框架（`Engine/Plugins/Runtime/MassEntity`）。

## 使用场景

- 你在做开放世界游戏，需要在场景中模拟上千个 NPC 走路、排队、闲逛 → 用 MassGameplay（MassMovement + MassRepresentation + MassSpawner）
- 你需要对大量实体进行空间查询（如"找到我周围 500 个 NPC 中带有 TagA 的"） → 用 MassEQS 集成 EQS
- 你需要根据玩家距离动态切换实体的渲染方式（ISM → Actor → 不可见） → 用 MassLOD + MassRepresentation
- 你需要在多人游戏中同步大量 AI 实体状态 → 用 MassReplication
- 你需要让大量实体与场景中的 SmartObject（如门、长椅）交互 → 用 MassSmartObjects

## 蓝图用法

MassEQS 模块提供了完整的蓝图函数库，用于在蓝图中与 Mass 实体的 EQS 查询结果交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SendSignalToEntity` | 向指定 Mass 实体发送信号（通过 SignalSubsystem） | `UMassEQSBlueprintLibrary` |
| `EntityToString` | 将 Mass 实体转为调试字符串 | `UMassEQSBlueprintLibrary` |
| `GetCachedEntityPosition` | 获取实体在查询时缓存的位置 | `UMassEQSBlueprintLibrary` |
| `GetCurrentEntityPosition` | 获取实体的实时当前位置 | `UMassEQSBlueprintLibrary` |
| `EntityComparison` | 比较两个实体是否相同 | `UMassEQSBlueprintLibrary` |
| `ContainsEntity` | 检查数组中是否包含某实体 | `UMassEQSBlueprintLibrary` |
| `GetEnviromentQueryResultAsEntityInfo` | 将 EQS 查询结果转换为实体信息数组 | `UMassEQSBlueprintLibrary` |

### 蓝图使用示例

**场景：通过 EQS 查询周围实体并发送信号**

1. 在 Actor 蓝图中，使用 `Run Environment Query` 节点运行一个已配置好的 EQS 查询资产（该资产需使用 `MassEntityHandles` Generator 和 `MassEntityTags` Test）
2. 将 `Run Environment Query` 的返回值（`UEnvQueryInstanceBlueprintWrapper`）传入 `GetEnviromentQueryResultAsEntityInfo` 节点
3. 该节点返回 `TArray<FMassEnvQueryEntityInfoBlueprintWrapper>`，使用 `ForEachLoop` 遍历
4. 对每个实体，调用 `SendSignalToEntity`（传入 Owner Actor、EntityInfo 和信号名称 FName）发送行为信号

**场景：比较和过滤实体**

1. 使用 `ContainsEntity` 节点检查某个实体是否在已知列表中
2. 使用 `EntityComparison` 节点判断两个 EQS 结果是否指向同一实体
3. 使用 `EntityToString` 节点输出调试信息

## C++ 用法

### 头文件引入

```cpp
// MassEQS 核心类型
#include "MassEQSTypes.h"
#include "MassEQS.h"

// 蓝图函数库
#include "MassEQSBlueprintLibrary.h"

// EQS 子系统
#include "MassEQSSubsystem.h"

// EQS 生成器与测试基类
#include "Generators/MassEnvQueryGenerator.h"
#include "Tests/MassEnvQueryTest.h"

// 实用工具
#include "MassEQSUtils.h"
```

### 基本用法：获取 EQS 查询结果中的实体信息

从 `MassEQSUtils` 的接口可知，可以直接从 EQS 结果中提取 Mass 实体信息：

```cpp
// 来源：Public/MassEQSUtils.h

#include "MassEQSUtils.h"
#include "EnvironmentQuery/EnvQueryInstance.h"

// 从 EQS 查询实例中获取所有实体信息
void MyFunction(const FEnvQueryInstance& QueryInstance)
{
    TArray<FMassEnvQueryEntityInfo> EntityInfos;
    FMassEQSUtils::GetAllAsEntityInfo(QueryInstance, EntityInfos);

    // 获取所有实体句柄
    TArray<FMassEntityHandle> Handles;
    FMassEQSUtils::GetEntityHandles(EntityInfos, Handles);

    // 现在可以使用 MassEntity API 操作这些实体
    for (const FMassEntityHandle& Handle : Handles)
    {
        // 通过 FMassEntityManager 操作实体...
    }
}
```

### 进阶用法：创建自定义 Mass EQS Test

通过继承 `UMassEnvQueryTest` 并实现 `IMassEQSRequestInterface`，可以创建自定义的大规模实体过滤测试：

```cpp
// 来源：Public/Tests/MassEnvQueryTest.h, Public/MassEQSTypes.h

#include "Tests/MassEnvQueryTest.h"
#include "MassEQSTypes.h"
#include "MassEQSSubsystem.h"

// 自定义请求数据
struct FMyCustomEQSRequestData : public FMassEQSRequestData
{
    float MinHealth;
    float MaxDistance;
    
    FMyCustomEQSRequestData(float InMinHealth, float InMaxDistance)
        : MinHealth(InMinHealth), MaxDistance(InMaxDistance) {}
};

// 自定义结果数据
struct FMyCustomEQSResultData : public FMassEQSRequestData
{
    TMap<FMassEntityHandle, bool> ResultMap;
    
    FMyCustomEQSResultData(TMap<FMassEntityHandle, bool>&& InMap)
        : ResultMap(MoveTemp(InMap)) {}
};

// 自定义 EQS Test
UCLASS()
class UMyMassEnvQueryTest_Custom : public UMassEnvQueryTest
{
    GENERATED_UCLASS_BODY()

public:
    // 创建请求数据，发送到 MassEQSSubsystem
    virtual TUniquePtr<FMassEQSRequestData> GetRequestData(
        FEnvQueryInstance& QueryInstance) const override
    {
        return MakeUnique<FMyCustomEQSRequestData>(MinHealth, MaxDistance);
    }

    virtual UClass* GetRequestClass() const override { return StaticClass(); }

    // 尝试获取 Mass Processor 处理后的结果
    virtual bool TryAcquireResults(
        FEnvQueryInstance& QueryInstance) const override
    {
        // 从 MassEQSSubsystem 获取结果
        // 成功则将结果写入 QueryInstance 的评分
        return true;
    }

protected:
    UPROPERTY(EditAnywhere, Category = "CustomTest")
    float MinHealth = 0.5f;
    
    UPROPERTY(EditAnywhere, Category = "CustomTest")
    float MaxDistance = 1000.f;
};
```

### 使用 MassEQSSubsystem 异步管理请求

```cpp
// 来源：Public/MassEQSSubsystem.h

#include "MassEQSSubsystem.h"

void UseEQSSubsystem(UWorld* World)
{
    // 获取 MassEQS 子系统（线程安全）
    UMassEQSSubsystem* EQSSubsystem = World->GetSubsystem<UMassEQSSubsystem>();
    if (!EQSSubsystem) return;

    // 推送请求到队列，返回唯一句柄
    // FMassEQSRequestHandle Handle = EQSSubsystem->PushRequest(...);

    // 处理完成后提交结果
    // EQSSubsystem->SubmitResults(Handle, MoveTemp(ResultData));

    // 在 EQS 端尝试获取结果
    // TUniquePtr<FMassEQSRequestData> Results = EQSSubsystem->TryAcquireResults(Handle);

    // 取消未完成的请求
    // EQSSubsystem->CancelRequest(Handle);
}
```

## Demo 示例

以下示例展示如何创建一个自定义的 Mass EQS Generator，在指定半径内查找所有拥有特定 Fragment 的 Mass 实体：

**MyMassEnvQueryGenerator_VisibleEntities.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Generators/MassEnvQueryGenerator_MassEntityHandles.h"
#include "MyMassEnvQueryGenerator_VisibleEntities.generated.h"

// 自定义请求数据
struct FVisibleEntitiesRequestData : public FMassEQSRequestData
{
    TArray<FVector> ContextPositions;
    float SearchRadius;
    float MinLOD;

    FVisibleEntitiesRequestData(const TArray<FVector>& InPositions,
                                 float InRadius, float InMinLOD)
        : ContextPositions(InPositions)
        , SearchRadius(InRadius)
        , MinLOD(InMinLOD) {}
};

UCLASS(meta = (DisplayName = "Visible Mass Entities"))
class MYPROJECT_API UMyMassEnvQueryGenerator_VisibleEntities
    : public UMassEnvQueryGenerator
{
    GENERATED_UCLASS_BODY()

public:
    virtual TUniquePtr<FMassEQSRequestData> GetRequestData(
        FEnvQueryInstance& QueryInstance) const override;
    virtual UClass* GetRequestClass() const override { return StaticClass(); }
    virtual bool TryAcquireResults(
        FEnvQueryInstance& QueryInstance) const override;

protected:
    UPROPERTY(EditDefaultsOnly, Category = Generator)
    FAIDataProviderFloatValue SearchRadius;

    UPROPERTY(EditDefaultsOnly, Category = Generator)
    FAIDataProviderFloatValue MinLODLevel;

    UPROPERTY(EditAnywhere, Category = Generator)
    TSubclassOf<UEnvQueryContext> SearchCenter;
};
```

**MyMassEnvQueryGenerator_VisibleEntities.cpp**

```cpp
#include "MyMassEnvQueryGenerator_VisibleEntities.h"
#include "MassEQSSubsystem.h"
#include "MassEQSUtils.h"
#include "EnvironmentQuery/Contexts/EnvQueryContext_Querier.h"
#include "EnvironmentQuery/Items/EnvQueryItemType_Actor.h"

UMyMassEnvQueryGenerator_VisibleEntities::UMyMassEnvQueryGenerator_VisibleEntities(
    const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    SearchCenter = UEnvQueryContext_Querier::StaticClass();
    SearchRadius.DefaultValue = 5000.f;
    MinLODLevel.DefaultValue = 0.f;
    ItemType = UEnvQueryItemType_MassEntityHandle::StaticClass();
}

TUniquePtr<FMassEQSRequestData>
UMyMassEnvQueryGenerator_VisibleEntities::GetRequestData(
    FEnvQueryInstance& QueryInstance) const
{
    // 收集上下文位置
    TArray<FVector> ContextPositions;
    QueryInstance.PrepareContext(SearchCenter, ContextPositions);

    float Radius = 0.f;
    QueryInstance.SetValueOf(SearchRadius, Radius);

    float MinLOD = 0.f;
    QueryInstance.SetValueOf(MinLODLevel, MinLOD);

    return MakeUnique<FVisibleEntitiesRequestData>(
        ContextPositions, Radius, MinLOD);
}

bool UMyMassEnvQueryGenerator_VisibleEntities::TryAcquireResults(
    FEnvQueryInstance& QueryInstance) const
{
    // 从 MassEQSSubsystem 获取处理结果
    TUniquePtr<FMassEQSRequestData> RawData =
        MassEQSRequestHandler.MassEQSSubsystem->TryAcquireResults(
            MassEQSRequestHandler.RequestHandle);

    if (!RawData.IsValid())
    {
        return false; // 结果尚未就绪
    }

    // 转换结果类型
    FMassEnvQueryResultData_MassEntityHandles* ResultData =
        FMassEQSUtils::TryAndEnsureCast<FMassEnvQueryResultData_MassEntityHandles>(RawData);

    if (!ResultData)
    {
        return false;
    }

    // 将结果写入 EQS 查询实例
    QueryInstance.ReserveItemData(ResultData->GeneratedEntityInfo.Num());
    for (const FMassEnvQueryEntityInfo& EntityInfo : ResultData->GeneratedEntityInfo)
    {
        uint8* RawItemData = QueryInstance.AddItemData<UEnvQueryItemType_MassEntityHandle>();
        UEnvQueryItemType_MassEntityHandle::SetValue(RawItemData, EntityInfo);
    }

    return true;
}
```

## 模块依赖

要使用 MassGameplay 插件，你的项目需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架核心，提供 ECS 基础设施（Fragment、Archetype、Processor） |
| `MassEQS` | EQS 与 Mass 实体的桥接，异步空间查询 |
| `MassRepresentation` | 实体渲染表示管理（ISM、Actor、不可见模式切换） |
| `MassMovement` | 实体批量移动与导航 |
| `MassSpawner` | 实体批量生成与销毁 |
| `MassLOD` | 基于距离的实体 LOD 分级 |
| `MassSmartObjects` | 实体与 SmartObject 交互集成 |

> 注意：`MassEntity` 位于 `Engine/Plugins/Runtime/MassEntity`，是使用 MassGameplay 的前提条件。编辑器相关依赖（`MassEntityEditor`、`MassGameplayEditor`）仅在编辑器环境下需要。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚 MassAgentComponent 的之前改动 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 在关闭 ISM 前等待 Actor 就绪，修复渲染切换时序 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复人群系统中非木偶 Actor 的处理逻辑 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复 LOD 计算器中每个观察者的 LOD 路径的多个历史 bug |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 将手动计算的 bDoKeepActorExtraFrame 迁移到新的 UE::M API |

### 维护评价

- **活跃维护**：最近更新集中在 2026 年 5 月，且为实质性功能修复和重构，说明 Epic 持续投入开发
- **实验性状态**：插件仍标记为 `IsExperimentalVersion = true` 且 `EnabledByDefault = false`，表明 API 可能会发生变化，不建议用于需要稳定性的生产项目
- **框架成熟度**：自 2021 年创建以来已迭代约 5 年，模块数量从最初拆分时扩展到 16 个，功能覆盖面广
- **近期关注点**：最近的提交集中在 Representation/LOD 模块的 bug 修复和 Actor 切换时序优化，说明渲染表示层仍在打磨中
- **推荐程度**：⭐⭐⭐ 适合技术预研和实验性项目，生产使用需谨慎评估 API 稳定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [MassEntity 基础框架](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassEntity)
- [MassAI 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)（从 MassGameplay 同期拆分，提供 AI 导航集成）