# MetaHuman Crowd

> Support for crowds of MetaHumans（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman 资产管线） |
| 模块 | `MetaHumanCrowd` (Runtime), `MetaHumanCrowdEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCrowd) | |

## 用途

MetaHuman Crowd 插件的核心目标是将高保真度的 MetaHuman 角色集成到 Unreal Engine 的 Mass Entity 人群模拟系统中。它解决了在大规模人群场景中使用 MetaHuman 时面临的两个关键挑战：

1.  **动画性能**：为每个 MetaHuman 实体分配独立的动画轨道（Animation Track）会导致 GPU 动画计算开销巨大。本插件引入了一个**共享动画轨道池**（`FSharedAnimTrackPool`），通过为每个动画序列创建少量相位偏移的“稳态轨道”（Steady-State Tracks）并让多个实体共享，以及为动画过渡提供临时的“混合轨道”（Blend Tracks），来显著减少 GPU 动画评估次数。
2.  **外观与资产管线管理**：MetaHuman 的外观（头部、身体、服装、发型）由复杂的资产管线生成。本插件提供了一套专用的 **Item Pipeline**（`UMetaHumanCrowdHeadPipeline`, `UMetaHumanCrowdCharacterPipeline` 等），用于为人群构建和组装优化后的 MetaHuman 资产，并管理其材质参数（如发色、服装颜色）在实例化渲染中的传递。

简而言之，这个插件是让 MetaHuman 能够以高性能、可管理的方式在 Mass 人群中“活起来”的桥梁。

## 使用场景

-   **开放世界游戏**：你需要在城市街道、广场等场景中填充大量外观各异、行为自然的 NPC，同时保持可接受的性能。
-   **影视预览与虚拟制片**：你需要快速生成背景人群，用于镜头预览或实时虚拟场景，要求角色具有电影级的视觉质量。
-   **建筑可视化**：在大型建筑或城市规划的实时演示中，需要添加大量逼真的人物以增强场景的真实感和规模感。
-   **任何需要结合 MetaHuman 视觉质量与 Mass 系统规模的场景**。

## 蓝图用法

本插件主要通过接口和 Mass 系统配置在蓝图中使用，直接暴露的蓝图节点较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set MetaHuman Mass Anim Desc` | 设置由 Mass 系统驱动的动画描述（动画序列、播放位置等）。 | `IMetahumanMassCrowdActorBlueprintInterface` |
| `Get MetaHuman Mass Anim Desc` | 获取当前由 Mass 系统驱动的动画描述。 | `IMetahumanMassCrowdActorBlueprintInterface` |
| `Set Trajectory` | 设置由 Mass 系统计算的运动轨迹，用于驱动角色的移动和转向。 | `IMetahumanMassCrowdActorBlueprintInterface` |
| `Wait For Streaming Assets` | 同步等待 Mass Spawner 所需的所有资产（如 MetaHuman 实例）加载完成。 | `AMetaHumanMassSpawner` |

### 使用示例（蓝图描述）

1.  **创建 MetaHuman 人群 Actor**：
    *   创建一个新的 Actor 蓝图类。
    *   在该蓝图类中，实现 `IMetahumanMassCrowdActorBlueprintInterface` 接口。
    *   在接口函数 `SetMetaHumanMassAnimDesc` 中，根据传入的 `FMetahumanMassAnimDesc` 数据，驱动你蓝图中角色的动画蓝图（Anim Blueprint）或动画组件。
    *   在 `SetTrajectory` 中，根据传入的 `FTransformTrajectory` 更新角色的移动目标。

2.  **配置 Mass Spawner**：
    *   在场景中放置一个 `AMetaHumanMassSpawner` 或 `AMassSpawner`。
    *   在其 `Mass Entity Config` 中，使用 `UMetaHumanMassCrowdVisualizationTrait` 作为可视化 Trait。
    *   在该 Trait 的 `Character Instances` 数组中，配置你准备好的 `UMetaHumanCharacterInstance` 资产，定义人群的外观池。
    *   配置 `Parent AnimSequence` 为包含人群基础动画的 `UAnimSequenceTransformProviderData`。
    *   调整 `SteadyStateTracksPerSequence` 和 `MaxBlendTracks` 以平衡动画多样性和性能。

3.  **触发生成**：
    *   通过 Mass Spawner 的 `Spawn Entities` 函数或相关逻辑生成人群实体。
    *   Mass 系统会自动为实体分配外观、驱动动画，并通过你实现的接口将状态同步到 Actor 蓝图中。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCrowd.h"
#include "Mass/IMetahumanMassCrowdActorBlueprintInterface.h"
#include "Mass/MetaHumanMassAnimDesc.h"
#include "Mass/MetaHumanMassCrowdVisualizationTrait.h"
```

### 基本用法

**1. 实现人群 Actor 接口**

创建一个继承自 `AActor` 并实现 `IMetahumanMassCrowdActorBlueprintInterface` 的类。

```cpp
// MyMetaHumanCrowdActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "Mass/IMetahumanMassCrowdActorBlueprintInterface.h"
#include "MyMetaHumanCrowdActor.generated.h"

UCLASS()
class AMyMetaHumanCrowdActor : public AActor, public IMetahumanMassCrowdActorBlueprintInterface
{
    GENERATED_BODY()

public:
    // IMetahumanMassCrowdActorBlueprintInterface
    virtual void SetMetaHumanMassAnimDesc_Implementation(const FMetahumanMassAnimDesc& NewAnimDesc) override;
    virtual FMetahumanMassAnimDesc GetMetaHumanMassAnimDesc_Implementation() const override;
    virtual void SetTrajectory_Implementation(const FTransformTrajectory& NewTrajectory) override;

private:
    FMetahumanMassAnimDesc CurrentAnimDesc;
    FTransformTrajectory CurrentTrajectory;
};
```

```cpp
// MyMetaHumanCrowdActor.cpp
#include "MyMetaHumanCrowdActor.h"

void AMyMetaHumanCrowdActor::SetMetaHumanMassAnimDesc_Implementation(const FMetahumanMassAnimDesc& NewAnimDesc)
{
    CurrentAnimDesc = NewAnimDesc;
    // 在此处将动画数据传递给你的动画蓝图或组件
    // 例如：GetMesh()->GetAnimInstance()->...
}

FMetahumanMassAnimDesc AMyMetaHumanCrowdActor::GetMetaHumanMassAnimDesc_Implementation() const
{
    return CurrentAnimDesc;
}

void AMyMetaHumanCrowdActor::SetTrajectory_Implementation(const FTransformTrajectory& NewTrajectory)
{
    CurrentTrajectory = NewTrajectory;
    // 在此处使用轨迹数据驱动角色移动
    // 例如：更新移动组件的目标点
}
```

**2. 配置 Mass 可视化 Trait (C++)**

通常在编辑器中配置，但也可以在代码中动态创建。

```cpp
// 假设你有一个 UMetaHumanMassCrowdVisualizationTrait 的指针
UMetaHumanMassCrowdVisualizationTrait* CrowdTrait = NewObject<UMetaHumanMassCrowdVisualizationTrait>();
CrowdTrait->CharacterInstances.Add(MyCharacterInstance1);
CrowdTrait->CharacterInstances.Add(MyCharacterInstance2);
CrowdTrait->ParentAnimSequence = MyAnimSequenceProvider;
CrowdTrait->SteadyStateTracksPerSequence = 5; // 增加动画多样性
CrowdTrait->MaxBlendTracks = 100; // 允许更多同时进行的动画过渡
```

### 进阶用法

**自定义动画轨道分配策略**

插件提供了 `IAnimSequenceTrackProvider` 接口，允许你替换默认的共享轨道池策略。

```cpp
#include "Mass/MetaHumanMassAnimSequenceTrackProvider.h"

class FMyCustomTrackProvider : public IAnimSequenceTrackProvider
{
public:
    virtual int32 ResolveAnimTrack(...) override { /* 自定义分配逻辑 */ }
    virtual void OnEntityRemoved(...) override { /* 自定义清理逻辑 */ }
    virtual void PostProcessEntities(...) override { /* 自定义后处理 */ }
    virtual FMassSkinnedMeshResolvedAnimState GetResolvedAnimState(...) const override { /* 自定义状态读取 */ }
};

// 在某个地方（例如子系统初始化时）设置自定义提供者
// 注意：这需要深入集成到 Mass 可视化子系统中，通常通过修改或扩展 UMetaHumanMassRepresentationSubsystem 实现。
```

## Demo 示例

一个最小化的、可编译的 MetaHuman 人群 Actor 实现。

```cpp
// SimpleMetaHumanCrowdActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "Mass/IMetahumanMassCrowdActorBlueprintInterface.h"
#include "SimpleMetaHumanCrowdActor.generated.h"

class USkeletalMeshComponent;
class UAnimInstance;

UCLASS()
class ASimpleMetaHumanCrowdActor : public AActor, public IMetahumanMassCrowdActorBlueprintInterface
{
    GENERATED_BODY()

public:
    ASimpleMetaHumanCrowdActor();

    // IMetahumanMassCrowdActorBlueprintInterface
    virtual void SetMetaHumanMassAnimDesc_Implementation(const FMetahumanMassAnimDesc& NewAnimDesc) override;
    virtual FMetahumanMassAnimDesc GetMetaHumanMassAnimDesc_Implementation() const override;
    virtual void SetTrajectory_Implementation(const FTransformTrajectory& NewTrajectory) override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    USkeletalMeshComponent* MeshComponent;

private:
    FMetahumanMassAnimDesc CachedAnimDesc;
};
```

```cpp
// SimpleMetaHumanCrowdActor.cpp
#include "SimpleMetaHumanCrowdActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimInstance.h"

ASimpleMetaHumanCrowdActor::ASimpleMetaHumanCrowdActor()
{
    PrimaryActorTick.bCanEverTick = false;

    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;
}

void ASimpleMetaHumanCrowdActor::SetMetaHumanMassAnimDesc_Implementation(const FMetahumanMassAnimDesc& NewAnimDesc)
{
    CachedAnimDesc = NewAnimDesc;
    
    // 简单示例：将动画序列和位置传递给动画实例
    if (UAnimInstance* AnimInstance = MeshComponent->GetAnimInstance())
    {
        // 这里需要根据你的动画蓝图逻辑来具体实现
        // 例如，设置一个变量来驱动状态机
        AnimInstance->SetRootMotionMode(ERootMotionMode::IgnoreRootMotion); // 人群通常由Mass移动驱动
    }
}

FMetahumanMassAnimDesc ASimpleMetaHumanCrowdActor::GetMetaHumanMassAnimDesc_Implementation() const
{
    return CachedAnimDesc;
}

void ASimpleMetaHumanCrowdActor::SetTrajectory_Implementation(const FTransformTrajectory& NewTrajectory)
{
    // 简单示例：将轨迹的第一个点作为移动目标
    if (NewTrajectory.Points.Num() > 0)
    {
        const FVector& TargetLocation = NewTrajectory.Points[0].Position;
        // 在此更新移动逻辑，例如使用 UNavigationSystemV1::SimpleMoveToLocation
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下**独特**的模块（除了常见的 Core, Engine 等）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCrowd` | 插件的核心运行时模块，包含 Mass 处理器、动画轨道池、类型定义等。 |
| `MetaHumanCrowdEditor` | 编辑器模块，提供 MetaHuman 人群资产的构建管线和编辑器工具。 |
| `MassEntity` | Unreal Engine 的 Mass Entity 框架，是本插件的基础。 |
| `MassRepresentation` | Mass 系统的可视化表示子系统，本插件扩展了它以支持 MetaHuman。 |
| `MassNavigation` | Mass 系统的导航和移动组件，用于驱动人群移动。 |
| `MassSmartObjects` | Mass 系统与 Smart Object 的集成，用于人群与场景交互。 |
| `MetaHumanCore` | MetaHuman 的核心运行时库。 |
| `MetaHumanCharacter` | MetaHuman 角色资产和实例管理。 |
| `AnimationCore` | 动画核心库，用于轨迹类型等。 |
| `StateTree` | 状态树系统，用于定义人群的行为逻辑。 |

## 维护状态

### 近期更新

- 2026-04-24 `56296dcc` The MetaHuman Crowd pipeline now does most of its processing on Mesh Descriptions and builds skeleta
- 2026-04-24 `8d3ed3d0` [MHCrowd] Add missing plugin dependencies
- 2026-04-24 `16907471` [MHCrowd] Add in experimental UAF support example for MH Crowds
- 2026-04-23 `a0e976cb` [MHCrowd] Fix for animation merging
- 2026-04-21 `227124bc` [MHCrowd] Add MetaHuman Mass classes to the MHCrowd plugin

### 维护评价

-   **创建时间**：2026 年 4 月，非常新的插件。
-   **实验性状态**：明确标记为实验性，意味着 API 和功能可能会发生重大变化，不建议用于生产环境。
-   **功能完整性**：从源码看，它已经实现了核心功能（Mass 集成、动画池化、资产管线），但可能缺少一些边缘情况的处理和优化。
-   **推荐使用**：**仅推荐用于研究、原型开发和早期技术验证**。如果你需要在生产项目中使用大规模 MetaHuman 人群，建议密切关注此插件的更新，并准备好在 API 变化时进行适配。目前，它更像是 Epic 内部用于推动 MetaHuman 和 Mass 系统集成的“概念验证”和“技术演示”。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCrowd)
-   官方文档：暂无
-   测试用例：暂无公开测试用例路径