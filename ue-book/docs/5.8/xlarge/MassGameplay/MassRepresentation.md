# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（基于 MassEntity 的大规模智能体模拟实现）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产、可视化配置） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

---

## 用途

MassGameplay 是 UE5 Mass 框架的**游戏逻辑层**实现，它在底层 MassEntity（ECS 数据库）之上构建了一整套面向游戏场景的子系统。插件解决的核心问题是：**当你需要在同一场景中驱动成千上万个智能体（Agent）时，传统 Actor 模式的性能远远不够**。

MassGameplay 通过以下方式解决大规模实体管理问题：

- **ECS 架构**：数据与逻辑分离，实体只是数据行，处理器（Processor）按 Archetype 批量执行
- **LOD 分级**：根据距离/可见性自动在高精度 Actor、低精度 Actor、实例化静态网格（ISM）、蒙皮网格实例（ISKM）、不可见之间无缝切换
- **表示层抽象**（MassRepresentation）：统一管理实体的视觉表现，自动处理 Actor 生成/回收、ISM 实例添加/移除
- **复制支持**（MassReplication）：为多人游戏场景提供 Mass 实体的网络同步
- **移动与导航**（MassMovement + MassAI）：批量计算路径与移动

**为什么需要单独启用**：此插件是实验性的，依赖 MassEntity 基础设施，仅在你的项目确实需要大规模实体模拟时才有意义。

---

## 使用场景

- 你在做一个开放世界游戏，需要场景中有数百个 NPC 在城市中行走 → 用 MassGameplay（MassMovement + MassRepresentation + MassLOD）
- 你在做一个 RTS 游戏，需要管理上千个单位的寻路、战斗和视觉表现 → 用 MassGameplay
- 你需要让大量 AI 实体在移动到离玩家远处时自动降级为静态网格以节省性能 → 用 MassRepresentation 的 LOD 系统
- 你需要让大量复制（Replicated）的实体在客户端有不同的视觉表现 → 用 MassRepresentation 的 Actor 管理系统
- 你只需要 ECS 数据层，不需要游戏逻辑 → 只用 MassEntity，不需要 MassGameplay

---

## 蓝图用法

MassRepresentation 模块的主要交互通过 `UMassRepresentationSubsystem` 和 Trait 系统进行。底层实体操作主要在 C++ 层完成，但 Trait 配置可在蓝图中完成。

### 核心 Trait（实体模板配置）

| Trait | 说明 | 适用场景 |
|---|---|---|
| `UMassMovableVisualizationTrait` | 可移动实体的可视化配置（Actor + ISM + ISKM） | 移动中的 NPC、车辆 |
| `UMassStationaryVisualizationTrait` | 静止实体的可视化配置（仅 ISM/ISKM） | 静态装饰物、建筑 |
| `UMassStationaryDistanceVisualizationTrait` | 基于距离 LOD 的静止实体可视化 | 大量静态物体的远景管理 |

### 核心片段（Fragment）说明

| 片段 | 说明 | 所在类 |
|---|---|---|
| `FMassRepresentationFragment` | 存储当前/上一帧的表示类型、Actor 索引、ISM 句柄 | 数据片段 |
| `FMassRepresentationLODFragment` | 存储 LOD 等级、可见性、LOD 重要性 | 数据片段 |
| `FMassRepresentationAnimationFragment` | 存储动画播放数据 | 数据片段 |
| `FMassStaticRepresentationTag` | 标记使用静态网格表示的实体 | 标签 |

### 配置参数（ConstSharedFragment）

**FMassRepresentationParameters** 中的关键配置项：

| 参数 | 说明 | 默认值 |
|---|---|---|
| `LODRepresentation[4]` | 每个 LOD 级别使用的表示类型 | High: Actor, Low: Actor, Medium: ISM, Off: None |
| `NotVisibleUpdateRate` | 不可见实体的更新间隔（秒） | 0.5 |
| `bKeepLowResActors` | 切换到 ISM 时是否保留低精度 Actor | true |
| `bWaitForActorVisualReadiness` | Actor 游戏资源加载完成前是否等待 | false |
| `bForceActorRepresentationForExternalActors` | 外部 Actor 是否强制使用 Actor 表示 | false |
| `bSpreadFirstVisualizationUpdate` | 是否将首次可视化更新分散到多帧 | false |

**FMassVisualizationLODParameters** 中的 LOD 距离配置：

| 参数 | 说明 | 默认值 |
|---|---|---|
| `BaseLODDistance[4]` | 各 LOD 的触发距离 | 0, 1000, 2500, 10000 |
| `VisibleLODDistance[4]` | 可见状态下的 LOD 距离 | 0, 2000, 4000, 15000 |
| `LODMaxCount[4]` | 每个 LOD 的最大实体数量 | 50, 100, 500, MAX |
| `DistanceToFrustum` | 距视锥体多远内视为可见 | 0 |
| `DistanceToFrustumHysteresis` | 视锥体可见的滞后距离 | 0 |

### 使用示例（蓝图描述）

1. **配置 MassEntity Template**：在你的 Entity Template 数据资产中添加 `MassMovableVisualizationTrait`，在细节面板中设置：
   - `HighResTemplateActor` → 选择你的完整 AI 角色蓝图
   - `LowResTemplateActor` → 选择简化版角色蓝图
   - `StaticMeshInstanceDesc` → 配置一个带 LOD 的静态网格
   - `LODParams.BaseLODDistance` → 设置各级别触发距离

2. **Spawn 实体**：使用 `MassSpawner` 模块的 Spawn 节点批量生成实体，Representation 系统会自动根据距离选择合适的视觉表现。

---

## C++ 用法

### 头文件引入

```cpp
#include "MassRepresentationSubsystem.h"
#include "MassRepresentationFragments.h"
#include "MassRepresentationTypes.h"
#include "MassRepresentationProcessor.h"
#include "MassRepresentationActorManagement.h"
```

### 基本用法

**1. 获取子系统并注册静态网格可视化描述**

```cpp
// 在你的初始化代码中
UMassRepresentationSubsystem* RepSubsystem = GetWorld()->GetSubsystem<UMassRepresentationSubsystem>();
check(RepSubsystem);

// 创建一个静态网格可视化描述
FStaticMeshInstanceVisualizationDesc Desc;
FMassStaticMeshInstanceVisualizationMeshDesc MeshDesc;
MeshDesc.Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Meshes/SM_AgentLowRes"));
MeshDesc.bCastShadows = true;
MeshDesc.SetSignificanceRange(EMassLOD::Medium, EMassLOD::Off);
Desc.Meshes.Add(MeshDesc);

// 注册并获得句柄
FStaticMeshInstanceVisualizationDescHandle Handle = RepSubsystem->FindOrAddStaticMeshDesc(Desc);
```

**2. 管理模板 Actor 的生成与释放**

```cpp
// 注册模板 Actor 类
int16 TemplateActorIndex = RepSubsystem->FindOrAddTemplateActor(MyAgentActorClass);

// 请求生成或获取 Actor
FMassActorSpawnRequestHandle SpawnRequestHandle;
AActor* AgentActor = RepSubsystem->GetOrRequestSpawnActorFromTemplate(
    MassEntityHandle,
    SpawnTransform,
    TemplateActorIndex,
    SpawnRequestHandle,
    /*Priority=*/ 0.0f,
    FMassActorPreSpawnDelegate(),
    FMassActorPostSpawnDelegate()
);

// 释放 Actor（完成时调用）
RepSubsystem->ReleaseTemplateActorOrCancelSpawning(
    MassEntityHandle,
    TemplateActorIndex,
    AgentActor,
    SpawnRequestHandle
);
```

**3. 自定义 Actor 管理行为**

```cpp
UCLASS()
class UMyRepresentationActorManagement : public UMassRepresentationActorManagement
{
    GENERATED_BODY()
public:
    // 自定义 Actor 就绪检测（例如等待骨骼网格流式加载完成）
    virtual bool IsActorReadyForRepresentation(const AActor& Actor) const override
    {
        // 在专用服务器上直接返回 true
        if (Actor.GetWorld()->GetNetMode() == NM_DedicatedServer)
        {
            return true;
        }
        
        // 检查骨骼网格是否加载完成
        const USkeletalMeshComponent* SkelMesh = Actor.FindComponentByClass<USkeletalMeshComponent>();
        if (SkelMesh && SkelMesh->IsRegistered())
        {
            return !SkelMesh->bPendingInitialize || SkelMesh->GetSkeletalMeshAsset() != nullptr;
        }
        return true;
    }

    // 自定义生成优先级
    virtual float GetSpawnPriority(const FMassRepresentationLODFragment& Representation) const override
    {
        // 可见实体优先生成
        return Representation.Visibility == EMassVisibility::CanBeSeen ? 0.0f : 100.0f;
    }
};
```

### 进阶用法

**在自定义 Processor 中集成表示系统更新**

```cpp
UCLASS()
class UMyCustomProcessor : public UMassRepresentationProcessor
{
    GENERATED_BODY()
public:
    UMyCustomProcessor()
    {
        // 在构造函数中配置执行阶段
        ExecutionOrder.ExecuteAfter.Add(UE::Mass::Processor::Names::LOD);
        ExecutionOrder.ExecuteBefore.Add(UE::Mass::Processor::Names::Representation);
    }

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override
    {
        Super::ConfigureQueries(EntityManager);
        
        EntityQuery.AddRequirement<FMassRepresentationFragment>(EMassFragmentAccess::ReadWrite);
        EntityQuery.AddRequirement<FMassRepresentationLODFragment>(EMassFragmentAccess::ReadOnly);
        EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
        EntityQuery.AddTagRequirement<FMassVisualizationProcessorTag>(EMassFragmentPresence::All);
    }

    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override
    {
        EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
        {
            // 调用基类的表示更新逻辑
            UpdateRepresentation(Context, UpdateParams);
            
            // 你的自定义逻辑...
        });
    }
};
```

**动态修改 LOD 参数**

```cpp
// 获取共享 Fragment 修改 LOD 距离
FMassVisualizationLODSharedFragment* LODSharedFragment = /* 从 archetype 获取 */;
if (LODSharedFragment)
{
    // 动态调整 LOD 距离计算器的参数
    // 注意：通常在 Trait 的 BuildTemplate 阶段配置
}
```

---

## Demo 示例

### 自定义 Trait 定义（.h）

```cpp
// MyAgentVisualizationTrait.h
#pragma once

#include "MassVisualizationTrait.h"
#include "MyAgentVisualizationTrait.generated.h"

UCLASS(meta=(DisplayName="My Agent Visualization"))
class UMyAgentVisualizationTrait : public UMassMovableVisualizationTrait
{
    GENERATED_BODY()

public:
    UMyAgentVisualizationTrait();

    UPROPERTY(EditAnywhere, Category = "Mass|Visual")
    TSubclassOf<UMyRepresentationActorManagement> MyActorManagementClass;

protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override;
};
```

### 自定义 Trait 实现（.cpp）

```cpp
// MyAgentVisualizationTrait.cpp
#include "MyAgentVisualizationTrait.h"
#include "MassRepresentationFragments.h"
#include "MassRepresentationSubsystem.h"
#include "MassEntityTemplateBuildContext.h"

UMyAgentVisualizationTrait::UMyAgentVisualizationTrait()
{
    // 设置默认的 LOD 表示类型
    Params.LODRepresentation[EMassLOD::High] = EMassRepresentationType::HighResSpawnedActor;
    Params.LODRepresentation[EMassLOD::Low] = EMassLOD::LowResSpawnedActor;
    Params.LODRepresentation[EMassLOD::Medium] = EMassRepresentationType::StaticMeshInstance;
    Params.LODRepresentation[EMassLOD::Off] = EMassRepresentationType::None;

    // 启用 Actor 视觉就绪等待
    Params.bWaitForActorVisualReadiness = true;
    
    // 注册自定义 Actor 管理类
    if (MyActorManagementClass)
    {
        Params.RepresentationActorManagementClass = MyActorManagementClass;
    }
}

void UMyAgentVisualizationTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    Super::BuildTemplate(BuildContext, World);
    
    // 在构建模板后，可以添加额外的自定义 Fragment
    // 例如添加动画片段
    BuildContext.AddFragment<FMassRepresentationAnimationFragment>();
}
```

### 自定义 Actor 管理（.h + .cpp）

```cpp
// MyRepresentationActorManagement.h
#pragma once

#include "MassRepresentationActorManagement.h"
#include "MyRepresentationActorManagement.generated.h"

UCLASS()
class UMyRepresentationActorManagement : public UMassRepresentationActorManagement
{
    GENERATED_BODY()

public:
    virtual bool IsActorReadyForRepresentation(const AActor& Actor) const override
    {
        if (Actor.GetWorld()->GetNetMode() == NM_DedicatedServer)
        {
            return true;
        }
        // 等待组件初始化完成
        return Actor.IsActorInitialized();
    }
    
    virtual void SetActorEnabled(const EMassActorEnabledType EnabledType, AActor& Actor, 
        const int32 EntityIdx, FMassCommandBuffer& CommandBuffer) const override
    {
        Super::SetActorEnabled(EnabledType, Actor, EntityIdx, CommandBuffer);
        
        if (EnabledType == EMassActorEnabledType::HighRes)
        {
            // 高精度时启用完整 AI 行为
            CommandBuffer.PushCommand<FMassDeferredSetCommand>([&Actor](FMassEntityManager&)
            {
                // 自定义高精度激活逻辑
            });
        }
    }
};
```

---

## 模块依赖

以下为 MassRepresentation 模块的独特依赖（非通用 Core/Engine 依赖）：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass ECS 底层框架，提供 Entity/Fragment/Processor 基础设施 |
| `MassLOD` | LOD 管理和重要性计算 |
| `MassSpawner` | 实体生成子系统 |
| `SmartObjectsModule` | 智能对象交互支持 |

其他 MassGameplay 子模块之间的依赖关系：MassRepresentation → MassCommon → MassEntity

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回退 MassAgentComponent 的早期改动 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | Actor 等待就绪后再关闭 ISM 表示 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复 Mass 人群中非 Puppet Actor 的处理 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复 LOD 计算器中多处已存在的 per-viewer 路径 Bug |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | 重构 Actor 额外帧保留逻辑 |

### 维护评价

- **活跃维护**：最近持续有功能性更新和 Bug 修复，2026 年 5 月仍有密集提交
- **实验性状态**：`IsExperimentalVersion=true`，API 不稳定，可能在未来版本有较大改动
- **版本较低**：VersionName 为 0.4，表明仍在早期迭代阶段
- **核心架构成熟**：虽然标记为实验性，但 LOD 分级、ISM/Actor 切换、Actor 生成管理等核心机制已相对完善
- **已知限制**：Actor 视觉就绪等待机制刚引入（`bWaitForActorVisualReadiness`），可能存在边界情况
- **推荐程度**：如果你的项目需要大规模实体模拟（>100 个 Agent），且能接受实验性 API，推荐使用。否则建议等待稳定版本

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- 官方文档（无）
- [MassEntity 基础框架](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassEntity)
- [MassAI 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)