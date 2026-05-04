# MassRepresentation

> Implementation of large-scale agent simulation based on MassEntity（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassRepresentation 是 MassGameplay 插件的核心模块之一，专门负责大规模实体（Mass Entity）的**可视化表示**。它解决的核心问题是：如何在拥有成千上万甚至数十万实体的场景中，高效地管理它们的视觉表现。

该模块实现了基于重要性（Significance）和距离（Distance）的 LOD（Level of Detail）系统，能够根据实体与摄像机的距离和重要性，动态地在以下三种表示形式之间切换：
1.  **高精度 Actor**：完整的、具有复杂逻辑和动画的 Actor 实例。
2.  **低精度 Actor**：简化版的 Actor，用于中距离观察。
3.  **静态网格实例（ISM）**：最高效的表示形式，通过实例化静态网格组件（Instanced Static Mesh Component）批量渲染，适用于远距离或大量实体。

此外，它还负责管理 Actor 的生成、回收、启用/禁用，以及 ISM 实例的添加、移除和变换更新，是连接 MassEntity 数据驱动逻辑与游戏世界视觉表现的关键桥梁。

## 使用场景

-   **开放世界游戏**：你需要在大地图上放置成千上万的 NPC、动物或车辆，但无法承受为每个实体都生成一个完整 Actor 的性能开销。
-   **即时战略（RTS）游戏**：你需要渲染大量同类型的作战单位（如士兵、坦克），并希望它们在远距离时能合并渲染以提升性能。
-   **模拟经营游戏**：你需要模拟一个繁忙城市中的大量行人、汽车，它们需要根据玩家视角动态调整细节层次。
-   **任何需要大规模实体可视化的场景**：只要你的游戏需要处理海量实体，并且对渲染性能有严格要求，MassRepresentation 都是理想的解决方案。

## 蓝图用法

MassRepresentation 模块主要通过 `UMassRepresentationSubsystem` 和 `UMassVisualizationComponent` 提供蓝图接口。核心功能围绕“可视化描述（Visualization Description）”的注册和实体表示类型的管理展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindOrAddStaticMeshDesc` | 注册或获取一个静态网格实例的可视化描述，返回其句柄。这是使用 ISM 表示的第一步。 | `UMassRepresentationSubsystem` |
| `GetOrSpawnActorFromTemplate` | 根据模板 Actor 类，获取或生成一个用于表示实体的 Actor 实例。 | `UMassRepresentationSubsystem` |
| `FindOrAddVisualDesc` | 在可视化组件中注册或获取一个视觉描述，用于管理 ISM 实例。 | `UMassVisualizationComponent` |
| `BeginVisualChanges` / `EndVisualChanges` | 标记 ISM 实例变换更新的开始和结束，用于批量处理以提高性能。 | `UMassVisualizationComponent` |
| `DirtyStaticMeshInstances` | 标记所有静态网格实例的渲染状态为“脏”，强制在下一帧更新渲染数据。 | `UMassRepresentationSubsystem` |

### 使用示例（蓝图描述）

1.  **注册可视化描述**：
    *   在游戏初始化时（如 `GameMode` 的 `BeginPlay`），获取 `UMassRepresentationSubsystem`。
    *   创建一个 `FStaticMeshInstanceVisualizationDesc` 结构体，设置其 `StaticMesh`、`Materials` 等属性。
    *   调用 `FindOrAddStaticMeshDesc` 节点，传入该描述，获取一个 `FStaticMeshInstanceVisualizationDescHandle` 句柄。将此句柄存储起来，供后续创建实体模板时使用。

2.  **创建使用该可视化的实体**：
    *   在创建 `MassEntityTemplate` 时，添加一个 `UMassVisualizationTrait`（或其子类，如 `UMassStationaryVisualizationTrait`）。
    *   在该 Trait 的属性中，将上一步获取的句柄赋值给 `StaticMeshInstanceDesc` 相关的属性。
    *   同时，配置 `HighResTemplateActor` 和 `LowResTemplateActor` 属性，指定在不同 LOD 级别下使用的 Actor 类。

3.  **运行时管理**：
    *   当实体被创建后，`MassRepresentationProcessor` 会自动根据其 LOD 和可见性信息，调用子系统来切换其表示形式（Actor 或 ISM）。
    *   如果需要手动触发更新（例如，强制刷新所有 ISM），可以调用 `DirtyStaticMeshInstances`。

## C++ 用法

### 头文件引入

```cpp
#include "MassRepresentationSubsystem.h"
#include "MassRepresentationTypes.h"
#include "MassRepresentationFragments.h"
#include "MassVisualizationTrait.h"
```

### 基本用法

以下代码展示了如何在 C++ 中注册一个静态网格可视化描述，并创建一个使用该描述的实体模板。

```cpp
// 假设在某个初始化函数中
UMassRepresentationSubsystem* RepresentationSubsystem = GetWorld()->GetSubsystem<UMassRepresentationSubsystem>();
if (RepresentationSubsystem)
{
    // 1. 定义静态网格可视化描述
    FStaticMeshInstanceVisualizationDesc MeshDesc;
    MeshDesc.StaticMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Meshes/SM_Tree"));
    MeshDesc.Materials.Add(LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_Tree")));

    // 2. 注册描述并获取句柄
    FStaticMeshInstanceVisualizationDescHandle MeshHandle = RepresentationSubsystem->FindOrAddStaticMeshDesc(MeshDesc);

    // 3. 在构建实体模板时使用该句柄
    FMassEntityTemplateBuildContext BuildContext;
    // ... 添加其他 Fragment 和 Trait ...
    
    // 添加可视化 Trait
    UMassVisualizationTrait* VisTrait = NewObject<UMassVisualizationTrait>(GetTransientPackage());
    VisTrait->StaticMeshInstanceDesc = MeshDesc; // 或者直接设置句柄相关的属性
    VisTrait->HighResTemplateActor = AMyHighResTreeActor::StaticClass();
    VisTrait->LowResTemplateActor = AMyLowResTreeActor::StaticClass();
    BuildContext.AddTrait(*VisTrait, *GetWorld());
}
```

### 进阶用法

自定义一个 Trait 来控制实体的表示行为，并处理 Actor 生成后的初始化。

```cpp
// MyCustomVisualizationTrait.h
UCLASS()
class UMyCustomVisualizationTrait : public UMassVisualizationTrait
{
    GENERATED_BODY()
public:
    // 自定义属性，例如树木的生长阶段
    UPROPERTY(EditAnywhere, Category = "Mass|Visual")
    int32 GrowthStage = 0;

    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override;
};

// MyCustomVisualizationTrait.cpp
void UMyCustomVisualizationTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    Super::BuildTemplate(BuildContext, World);

    // 添加一个自定义 Fragment 来存储生长阶段
    BuildContext.AddFragment<FGrowthStageFragment>();
    // 在模板数据中设置初始值
    // ...
}

// 在 Actor 管理类中处理生成后的初始化
UCLASS()
class UMyActorManagement : public UMassRepresentationActorManagement
{
    GENERATED_BODY()
public:
    virtual EMassActorSpawnRequestAction OnPostActorSpawn(
        const FMassActorSpawnRequestHandle& SpawnRequestHandle,
        FConstStructView SpawnRequest,
        TSharedRef<FMassEntityManager> EntityManager) const override
    {
        // 调用父类处理
        EMassActorSpawnRequestAction Action = Super::OnPostActorSpawn(SpawnRequestHandle, SpawnRequest, EntityManager);

        // 获取生成的 Actor 和关联的实体数据
        AActor* SpawnedActor = /* ... */;
        FMassEntityHandle Entity = /* ... */;
        if (SpawnedActor && Entity.IsSet())
        {
            // 从实体获取生长阶段数据
            const FGrowthStageFragment* GrowthData = EntityManager->GetFragmentDataPtr<FGrowthStageFragment>(Entity);
            if (GrowthData)
            {
                // 初始化 Actor 的视觉效果
                Cast<AMyTreeActor>(SpawnedActor)->SetGrowthStage(GrowthData->Stage);
            }
        }
        return Action;
    }
};
```

## Demo 示例

以下是一个最小化的示例，展示如何创建一个使用 ISM 表示的静态实体。

```cpp
// MyTreeTrait.h
#pragma once
#include "MassStationaryVisualizationTrait.h"
#include "MyTreeTrait.generated.h"

UCLASS()
class UMyTreeTrait : public UMassStationaryVisualizationTrait
{
    GENERATED_BODY()
public:
    UMyTreeTrait();
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override;
};

// MyTreeTrait.cpp
#include "MyTreeTrait.h"
#include "MassEntityTemplateBuildContext.h"

UMyTreeTrait::UMyTreeTrait()
{
    // 配置默认的静态网格
    StaticMeshInstanceDesc.Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Meshes/SM_Tree"));
    StaticMeshInstanceDesc.Materials.Add(LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_Tree")));
    // 设置为静态，不生成 Actor
    Params.RepresentationTypes[EMassLOD::High] = EMassRepresentationType::StaticMeshInstance;
    Params.RepresentationTypes[EMassLOD::Medium] = EMassRepresentationType::StaticMeshInstance;
    Params.RepresentationTypes[EMassLOD::Low] = EMassLOD::Off;
}

void UMyTreeTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    // 调用父类构建，这会注册可视化描述并添加必要的 Fragment 和 Processor
    Super::BuildTemplate(BuildContext, World);
    
    // 可以在这里添加树木特有的 Fragment，如生命值、类型等
    // BuildContext.AddFragment<FTreeFragment>();
}
```

## 模块依赖

从 Build.cs 分析，MassRepresentation 模块依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassEntity 核心框架，提供实体、片段、处理器等基础概念。 |
| `MassSpawner` | 负责实体的生成和销毁，与表示模块协同管理 Actor 的生命周期。 |
| `MassLOD` | 提供 LOD 计算的基础框架和片段，是距离和可视化 LOD 处理器的基础。 |
| `MassSignals` | 用于在实体状态变化（如表示类型切换）时发送信号。 |
| `MassCommon` | 提供通用的片段、标签和工具函数。 |

## 维护状态

### 近期更新

```
- 2025-10-03 2bfd41dbdd11 [MassGameplay] Added additional null guards around UMassRepresentationSubsystem::VisualizationComponent which may become invalid while the UMassRepresentationSubsystem is still active.
- 2025-09-15 983880c6d877 PR #13067: Mass: Add optional ability for applications to disable invalid mesh desc error messages
- 2025-08-20 fd28bd089269 [Mass] fixed inconsistencies in how CancelSpawningInternal is being used in relation to recent addition of "bImmediate" mode in surrounding context.
```

### 维护评价

MassRepresentation 模块作为 MassGameplay 的核心组件，处于**活跃维护**状态。
-   **创建时间**：约 3 年前，相对年轻。
-   **更新频率**：近期有多次提交，主要集中在**稳定性修复**（如空指针保护）和**功能增强**（如错误消息控制），表明 Epic 仍在积极改进该系统。
-   **实验性状态**：该插件被标记为 `IsExperimentalVersion=true`，且默认未启用 (`EnabledByDefault=false`)。这意味着 API 可能还不稳定，未来版本可能会有重大变更。
-   **已知限制**：作为实验性功能，其文档和社区支持可能不如成熟系统完善。大规模使用时需要深入理解其内部机制以进行性能调优。
-   **推荐使用**：**推荐用于新项目原型开发或对大规模实体有明确需求的项目**，但需要做好应对 API 变更的准备。对于已上线的项目，引入需谨慎评估。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
-   [官方文档]() (暂无)
-   [测试用例]() (路径待确认，通常位于 `Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite/`)