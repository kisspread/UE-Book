# MassRepresentation

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模实体可视化 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、实体模板） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassRepresentation 是 MassGameplay 插件中负责**视觉表现管理**的核心模块。它解决的核心问题是：当场景中有成千上万个实体（Agent）时，如何高效地管理它们的视觉呈现。

该模块实现了**多级 LOD 表现切换系统**，根据实体与摄像机的距离和可见性，自动在不同视觉表现之间切换：

1. **HighResSpawnedActor** — 完整的高精度 Actor（近距离）
2. **LowResSpawnedActor** — 低精度 Actor（中近距离）
3. **SkinnedMeshInstance** — 实例化骨骼网格体（中远距离，支持动画）
4. **StaticMeshInstance** — 实例化静态网格体（远距离，最高效）
5. **None** — 不渲染（超出视距或完全被剔除）

这种分层设计使得数万个实体可以同时存在于场景中，同时保证近处的实体有完整的交互和动画能力，远处的实体使用极其高效的实例化渲染。

## 使用场景

- 你正在开发大规模 NPC 人群系统（城市、战场、集市）→ 使用 MassRepresentation 管理人群的 LOD 切换
- 你需要数千个带动画的角色在场景中行走 → 使用 SkinnedMeshInstance 远距离表现，近距离切换为 SpawnedActor
- 你有一个 RTS 游戏需要渲染大量单位 → 使用 StaticMeshInstance 进行高效的远距离渲染
- 你需要基于距离自动管理实体的可见性和视觉精度 → 配置 FMassVisualizationLODParameters 距离阈值

## 蓝图用法

MassRepresentation 模块主要通过 **Entity Trait（实体特征）** 和 **Data Asset（数据资产）** 在蓝图中配置，而非直接暴露大量蓝图节点。

### 核心配置类

| 类 | 说明 | 所在模块 |
|---|---|---|
| `UMassVisualizationTrait` | 已废弃，配置静态网格/骨骼网格/Actor 表现的完整特征 | `MassRepresentation` |
| `UMassStationaryVisualizationTrait` | 静态实体的可视化特征（推荐） | `MassRepresentation` |
| `UMassMovableVisualizationTrait` | 动态实体的可视化特征（推荐） | `MassRepresentation` |
| `UMassDistanceVisualizationTrait` | 已废弃，基于距离 LOD 的简化可视化特征 | `MassRepresentation` |
| `UMassStationaryDistanceVisualizationTrait` | 静态实体的距离 LOD 特征（推荐） | `MassRepresentation` |

### Entity Template 配置流程

在 MassEntity 模板中添加可视化特征时，你需要配置以下属性：

**FMassRepresentationParameters** — 表现参数：

| 属性 | 说明 |
|---|---|
| `LODRepresentation[4]` | 每个 LOD 级别对应的表现类型数组 |
| `bForceActorRepresentationForExternalActors` | 是否强制外部 Actor 使用 Actor 表现 |
| `bKeepLowResActors` | 使用 ISM 时是否保留禁用的低精度 Actor |
| `bKeepActorExtraFrame` | 切换到 ISM 时多保留一帧 Actor |
| `bWaitForActorVisualReadiness` | 切换到 Actor 时等待视觉就绪 |
| `NotVisibleUpdateRate` | 不可见实体的更新间隔（秒） |

**FMassVisualizationLODParameters** — LOD 距离参数：

| 属性 | 说明 |
|---|---|
| `BaseLODDistance[4]` | 各 LOD 级别生效的基础距离 |
| `VisibleLODDistance[4]` | 可见状态下各 LOD 级别距离 |
| `LODMaxCount[4]` | 每个 LOD 级别的最大实体数量 |
| `DistanceToFrustum` | 视锥体外但仍算可见的距离范围 |
| `DistanceToFrustumHysteresis` | 视锥体剔除的滞后距离 |

### 使用示例（蓝图描述）

**创建一个 NPC 人群实体模板：**

1. 创建一个 `UMassEntityConfigAsset`
2. 添加 `UMassStationaryVisualizationTrait` 或 `UMassMovableVisualizationTrait`
3. 在特征中配置：
   - `StaticMeshInstanceDesc` → 设置静态网格体（如一个低面数角色模型）
   - `SkinnedMeshInstanceDesc` → 设置骨骼网格体（如带动画的角色模型）
   - `HighResTemplateActor` → 设置近距离高精度 Actor 类
   - `LowResTemplateActor` → 设置低精度 Actor 类
   - `Params.LODRepresentation` → 配置各 LOD 对应表现：
     - `[0] HighResSpawnedActor`
     - `[1] LowResSpawnedActor`
     - `[2] SkinnedMeshInstance`
     - `[3] StaticMeshInstance`
4. 在 `LODParams` 中配置距离阈值和最大数量限制

## C++ 用法

### 头文件引入

```cpp
#include "MassRepresentationSubsystem.h"
#include "MassRepresentationFragments.h"
#include "MassRepresentationTypes.h"
#include "MassRepresentationProcessor.h"
#include "MassRepresentationActorManagement.h"
```

### 基本用法 — 注册静态网格体可视化描述

通过 `UMassRepresentationSubsystem` 注册静态网格体表现类型，供实体使用：

```cpp
// 在你的初始化代码中获取 RepresentationSubsystem
UMassRepresentationSubsystem* RepSubsystem = GetWorld()->GetSubsystem<UMassRepresentationSubsystem>();
check(RepSubsystem);

// 创建一个静态网格体可视化描述
FStaticMeshInstanceVisualizationDesc Desc;
FMassStaticMeshInstanceVisualizationMeshDesc& MeshDesc = Desc.Meshes.AddDefaulted_GetRef();
MeshDesc.Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Meshes/SimpleCharacter"));
MeshDesc.bCastShadows = true;
MeshDesc.Mobility = EComponentMobility::Movable;

// 注册描述并获取句柄
FStaticMeshInstanceVisualizationDescHandle Handle = RepSubsystem->FindOrAddStaticMeshDesc(Desc);
```

来源：`MassRepresentationSubsystem.h` — `FindOrAddStaticMeshDesc` 函数定义

### 基本用法 — 通过模板 Actor 管理实体表现

当实体需要从 ISM 切换到完整 Actor 时，通过子系统请求 Actor 生成：

```cpp
// 注册一个模板 Actor 类
int16 TemplateActorIndex = RepSubsystem->FindOrAddTemplateActor(MyCharacterClass);

// 请求生成或获取一个 Actor
FMassActorSpawnRequestHandle SpawnHandle;
FTransform SpawnTransform = EntityTransform;
float Priority = RepSubsystem->GetSpawnPriority(LODFragment); // 越小优先级越高

AActor* SpawnedActor = RepSubsystem->GetOrRequestSpawnActorFromTemplate(
    MassAgent,
    SpawnTransform,
    TemplateActorIndex,
    SpawnHandle,
    Priority,
    FMassActorPreSpawnDelegate(),
    FMassActorPostSpawnDelegate()
);

if (SpawnedActor)
{
    // Actor 已经就绪，可以使用
}
```

来源：`MassRepresentationSubsystem.h` — `GetOrRequestSpawnActorFromTemplate` 函数定义

### 基本用法 — 读取实体的 LOD 和表现状态

```cpp
// 在 Processor 的 Execute 方法中
Context.ForEachEntityChunk([this](FMassExecutionContext& Context)
{
    TConstArrayView<FMassRepresentationFragment> RepList = Context.GetFragmentView<FMassRepresentationFragment>();
    TConstArrayView<FMassRepresentationLODFragment> LODList = Context.GetFragmentView<FMassRepresentationLODFragment>();

    for (int32 i = 0; i < Context.GetNumEntities(); ++i)
    {
        const FMassRepresentationFragment& Rep = RepList[i];
        const FMassRepresentationLODFragment& LOD = LODList[i];

        // 检查当前表现类型
        EMassRepresentationType CurrentType = Rep.CurrentRepresentation;
        
        // 检查 LOD 级别
        EMassLOD::Type CurrentLOD = LOD.LOD;
        float LODSignificance = LOD.LODSignificance;
        
        // 检查可见性
        EMassVisibility Visibility = LOD.Visibility;
    }
});
```

来源：`MassRepresentationFragments.h` — `FMassRepresentationFragment` 和 `FMassRepresentationLODFragment` 结构定义

### 进阶用法 — 自定义 Actor 表现管理

通过继承 `UMassRepresentationActorManagement` 自定义 Actor 的生成和就绪检测行为：

```cpp
UCLASS()
class UMyActorManagement : public UMassRepresentationActorManagement
{
    GENERATED_BODY()
public:
    // 自定义 Actor 就绪检测 — 例如等待资源流式加载完成
    virtual bool IsActorReadyForRepresentation(const AActor& Actor) const override
    {
        // 专用服务器直接返回 true
        if (Actor.GetWorld()->GetNetMode() == NM_DedicatedServer)
        {
            return true;
        }

        // 检查 SkeletalMesh 是否已加载完成
        if (const ACharacter* Character = Cast<ACharacter>(&Actor))
        {
            if (USkeletalMeshComponent* SKComp = Character->GetMesh())
            {
                return SKComp->GetSkeletalMeshAsset() != nullptr 
                    && SKComp->GetSkeletalMeshAsset()->GetResourceForRendering() != nullptr;
            }
        }
        return true;
    }

    // 自定义生成优先级
    virtual float GetSpawnPriority(const FMassRepresentationLODFragment& Representation) const override
    {
        // LOD 越高优先级越高（值越小）
        return static_cast<float>(Representation.LOD);
    }
};
```

来源：`MassRepresentationActorManagement.h` — 虚函数定义，以及 `MassRepresentationFragments.h` 中 `FMassRepresentationParameters::RepresentationActorManagementClass` 的使用方式

### 进阶用法 — 从 ISM 数据中读取实例信息

```cpp
// 通过 VisualizationComponent 获取所有 ISM 信息
UMassVisualizationComponent* VisComp = RepSubsystem->GetVisualizationComponent();
FMassInstancedStaticMeshInfoArrayView Infos = VisComp->GetMutableInstancedStaticMeshInfos();

for (int32 i = 0; i < Infos.Num(); ++i)
{
    FMassInstancedStaticMeshInfo& Info = Infos[i];
    // Info 包含静态网格体描述、ISM 组件引用、LOD Significance 范围等
}
```

来源：`MassVisualizationComponent.h` — `GetMutableVisualInfos` 和 `MassRepresentationTypes.h` — `FMassInstancedStaticMeshInfo`

### 进阶用法 — 骨骼网格体实例的动画数据处理

```cpp
// 消费动画数据并推送到 InstancedSkinnedMeshComponent
// 通过 UMassConsumeInstancedSkinnedMeshAnimationProcessor 实现
void UMyAnimProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // ... 在 ForEachEntityChunk 中
    FAnimSequenceTrackAutoPlayData AnimData;
    AnimData.AnimSequence = MyAnimSequence;
    AnimData.PlayRate = 1.0f;
    AnimData.StartingPosition = CurrentTime;

    UMassConsumeInstancedSkinnedMeshAnimationProcessor::UpdateMeshAnimation(
        EntityHandle, MeshInfo, AnimData, LODSignificance, PrevLODSignificance
    );
}
```

来源：`MassRepresentationAnimationProcessor.h` — `UMassConsumeInstancedSkinnedMeshAnimationProcessor` 类定义

## Demo 示例

### 最小可编译示例 — 创建一个带 LOD 表现的自定义 Processor

```cpp
// MyMassVisualDebugProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MassRepresentationFragments.h"
#include "TransformTypes.h"
#include "MyMassVisualDebugProcessor.generated.h"

UCLASS()
class UMyMassVisualDebugProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyMassVisualDebugProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyMassVisualDebugProcessor.cpp
#include "MyMassVisualDebugProcessor.h"
#include "MassCommonFragments.h"
#include "MassExecutionContext.h"

UMyMassVisualDebugProcessor::UMyMassVisualDebugProcessor()
{
    // 仅在编辑器/开发构建中运行
    bAutoRegisterWithProcessingPhases = true;
    ExecutionFlags = static_cast<int32>(EProcessorExecutionFlags::All);
    ProcessingPhase = EMassProcessingPhase::PostPhysics; // 在表现更新之后执行
}

void UMyMassVisualDebugProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMassRepresentationFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassRepresentationLODFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.RegisterWithProcessor(*this);
}

void UMyMassVisualDebugProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(Context, [](FMassExecutionContext& Context)
    {
        TConstArrayView<FMassRepresentationFragment> RepList = Context.GetFragmentView<FMassRepresentationFragment>();
        TConstArrayView<FMassRepresentationLODFragment> LODList = Context.GetFragmentView<FMassRepresentationLODFragment>();
        TConstArrayView<FTransformFragment> TransformList = Context.GetFragmentView<FTransformFragment>();

        const int32 NumEntities = Context.GetNumEntities();

        // 统计各表现类型的实体数量
        int32 ActorCount = 0;
        int32 ISMCount = 0;
        int32 SkinnedCount = 0;
        int32 NoneCount = 0;

        for (int32 i = 0; i < NumEntities; ++i)
        {
            const FMassRepresentationFragment& Rep = RepList[i];
            switch (Rep.CurrentRepresentation)
            {
                case EMassRepresentationType::HighResSpawnedActor:
                case EMassRepresentationType::LowResSpawnedActor:
                    ActorCount++;
                    break;
                case EMassRepresentationType::StaticMeshInstance:
                    ISMCount++;
                    break;
                case EMassRepresentationType::SkinnedMeshInstance:
                    SkinnedCount++;
                    break;
                case EMassRepresentationType::None:
                    NoneCount++;
                    break;
            }
        }

        UE_LOG(LogTemp, Log, TEXT("Entities in chunk: %d | Actors: %d | ISM: %d | Skinned: %d | None: %d"),
            NumEntities, ActorCount, ISMCount, SkinnedCount, NoneCount);
    });
}
```

## 模块依赖

MassRepresentation 的 Build.cs 声明了以下依赖：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass ECS 核心框架 |
| `MassCommon` | Mass 通用 Fragment 和 Tag |
| `MassLOD` | LOD 计算逻辑 |
| `EditorFramework` | 编辑器框架支持 |
| `UnrealEd` | 编辑器工具 |
| `MassEntityEditor` | Mass Entity 编辑器扩展 |
| `AnimSequenceTrackAutoPlay` | 骨骼网格体动画数据 |

对于使用者的模块，如果要使用 MassRepresentation 的功能，通常需要依赖：
- `MassRepresentation` — 本模块
- `MassEntity` — ECS 核心
- `MassCommon` — 通用 Fragment

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了 MassAgentComponent 的近期修改 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 新增 Actor 视觉就绪等待机制，避免 ISM 过早关闭 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了人群系统中非 Puppet Actor 的处理逻辑 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 LOD 计算器按观察者计算路径中的多个历史 bug |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 将手动计算的 KeepActorExtraFrame 改为使用新的 UE::M 工具函数 |

### 维护评价

MassRepresentation 作为 MassEntity 的上层可视化模块，处于**活跃维护**状态。近期（2026年5月）有多次实质性更新，包括 Actor 就绪等待机制（`bWaitForActorVisualReadiness`）、LOD 计算器 bug 修复等核心功能改进。

该模块是实验性的（`IsExperimentalVersion=true`），且默认未启用（`EnabledByDefault=false`），API 可能随版本迭代发生变化。源码中有明显的废弃标记（如 `UMassVisualizationTrait` 被标记为 DEPRECATED，推荐使用 `MassStationaryVisualizationTrait` 或 `MassMovableVisualizationTrait`）。

**推荐使用**：如果你的项目需要大规模实体的视觉管理，MassRepresentation 是目前 UE5 中最成熟的解决方案。但需注意：
- 需要手动在插件设置中启用
- API 处于实验阶段，升级引擎版本时可能需要适配
- 建议关注 Actor 就绪检测机制（`IsActorReadyForRepresentation`）以避免流式加载时的视觉闪烁

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- 官方文档（暂无）