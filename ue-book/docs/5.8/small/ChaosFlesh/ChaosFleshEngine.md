# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 柔体物理 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是基于 Chaos 物理引擎的**可变形体（软体）体积仿真系统**。它使用四面体网格（Tetrahedral Mesh）对物体进行体积离散化，模拟肌肉、脂肪、果冻等柔性物质的物理行为。

该插件解决的核心问题是：在运行时对非刚体物体进行真实物理仿真，包括弹性变形、重力、阻尼、碰撞、肌肉激活等效果。它通过 Dataflow 图形系统驱动仿真流程，支持 GPU 加速蒙皮变形，并能与骨骼网格体（SkeletalMesh）进行绑定，实现仿真结果驱动角色动画。

与传统 Cloth（布料）系统不同，ChaosFlesh 是**体积仿真**而非表面仿真，适合需要保持体积不变性的软体物体。

## 使用场景

- 你需要模拟角色的肌肉膨胀/收缩效果（如健身游戏中的肌肉隆起）
- 你需要对可变形物体进行物理仿真（如果冻、面包、软组织）
- 你正在制作医疗/手术模拟，需要仿真软组织的物理行为
- 你需要将仿真结果绑定到骨骼网格体上，驱动皮肤变形（Blend Shape 效果）
- 你希望通过 Dataflow 节点图自定义仿真流程

## 蓝图用法

### 核心 Actor 与组件

该插件提供了完整的 Actor-Component 架构来组织仿真场景：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableSimulation` | 将可变形体注册到求解器 Actor 开始仿真 | `AFleshActor` / `UDeformablePhysicsComponent` |
| `DisableSimulation` | 从求解器中注销可变形体并停止仿真 | `UDeformablePhysicsComponent` |
| `EnableSimulationFromActor` | 从 DeformableSolverActor 启用仿真 | `UDeformablePhysicsComponent` |
| `SetRestCollection` | 设置 FleshAsset 作为仿真的静止状态参考 | `UDeformableTetrahedralComponent` |
| `GetRestCollection` | 获取当前的 FleshAsset | `UDeformableTetrahedralComponent` |
| `GetSkeletalMeshEmbeddedPositions` | 获取四面体网格变形后的骨骼绑定位置 | `UDeformableTetrahedralComponent` |
| `ResetSimulationProperties` | 重置求解器的所有仿真参数 | `UDeformableSolverComponent` |

### 约束管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddConstrainedBodies` | 在两个 FleshComponent 之间添加约束 | `UDeformableConstraintsComponent` |
| `RemoveConstrainedBodies` | 移除两个 FleshComponent 之间的约束 | `UDeformableConstraintsComponent` |

### 碰撞体管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddStaticMeshComponent` | 将静态网格体注册为可变形体的碰撞对象 | `UDeformableCollisionsComponent` |
| `RemoveStaticMeshComponent` | 移除静态网格体碰撞对象 | `UDeformableCollisionsComponent` |

### FleshAsset 配置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDataflowAsset` | 设置用于生成/驱动仿真的 Dataflow 图资产 | `UFleshAsset` |
| `GetDataflowAsset` | 获取当前 Dataflow 图资产 | `UFleshAsset` |
| `SetDataflowTerminal` | 设置 Dataflow 图的终端节点名称 | `UFleshAsset` |
| `GetDataflowTerminal` | 获取 Dataflow 终端节点名称 | `UFleshAsset` |

### 使用示例（蓝图描述）

**基本仿真设置流程：**

1. 在场景中放置一个 `DeformableSolverActor` 作为物理求解器
2. 放置一个 `FleshActor`，在 Details 面板中设置 `FleshComponent` 的 `RestCollection`（一个预先创建好的 `FleshAsset`）
3. 在 `FleshActor` 的 Details 面板中，将 `PrimarySolver` 指向第一步创建的 `DeformableSolverActor`
4. 调用 `FleshActor::EnableSimulation`，传入求解器 Actor 引用
5. 仿真开始，`FleshComponent` 的 `ProceduralMeshComponent` 将渲染变形后的四面体网格

**将仿真结果绑定到骨骼网格体：**

1. 创建一个 `FleshAsset`，在其中设置 `TargetDeformationSkeleton`（目标骨骼网格体）
2. 通过 Dataflow 图生成四面体网格并绑定到骨骼
3. 在 `UDeformableTetrahedralComponent` 上调用 `GetSkeletalMeshEmbeddedPositions`
4. 传入 `Format` 参数选择输出格式（World/Component/Bone 空间的位置或增量）
5. 将返回的位置数据应用到骨骼网格体的顶点

**多物体约束仿真：**

1. 放置多个 `FleshActor`，各自拥有独立的 `FleshAsset`
2. 放置一个 `ADeformableConstraintsActor`
3. 在其 `SourceBodies` 和 `TargetBodies` 数组中添加需要约束的 `FleshActor`
4. 设置 `PrimarySolver`，调用 `EnableSimulation`，系统自动创建约束

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFlesh/FleshAsset.h"
#include "ChaosFlesh/FleshComponent.h"
#include "ChaosFlesh/FleshActor.h"
#include "ChaosFlesh/ChaosDeformableSolverActor.h"
#include "ChaosFlesh/ChaosDeformableTetrahedralComponent.h"
#include "ChaosFlesh/ChaosDeformableSolverComponent.h"
#include "ChaosFlesh/ChaosDeformableConstraintsComponent.h"
#include "ChaosFlesh/ChaosDeformableCollisionsComponent.h"
```

### 基本用法

**获取仿真的嵌入位置（用于驱动骨骼网格体变形）：**

来源：`Public/ChaosFlesh/ChaosDeformableTetrahedralComponent.h`

```cpp
// 获取四面体仿真变形后的位置
// Format 支持：WorldPos, WorldDelta, ComponentPos, ComponentDelta, BonePos, BoneDelta
UDeformableTetrahedralComponent* FleshComp = GetFleshComponent();

TArray<FVector> Positions = FleshComp->GetSkeletalMeshEmbeddedPositions(
    ChaosDeformableBindingOption::WorldPos,  // 输出世界空间位置
    FTransform::Identity,                     // 骨骼偏移变换
    NAME_None,                                // 骨骼名（BonePos/BoneDelta 时使用）
    1.0f                                      // 仿真混合权重
);

// 将位置应用到顶点
for (int32 i = 0; i < Positions.Num(); ++i)
{
    // 应用位置...
}
```

**配置求解器仿真参数：**

来源：`Public/ChaosFlesh/ChaosDeformableSolverGroups.h`

```cpp
// 创建求解器并配置参数
UDeformableSolverComponent* Solver = FindComponentByClass<UDeformableSolverComponent>();

// 时间步进设置
Solver->SolverTiming.NumSubSteps = 2;
Solver->SolverTiming.NumSolverIterations = 5;
Solver->SolverTiming.FixTimeStep = false;
Solver->SolverTiming.TimeStepSize = 0.05f;
Solver->SolverTiming.ExecutionModel = EDeformableExecutionModel::Chaos_Deformable_PostPhysics;

// 约束设置
Solver->SolverConstraints.bEnablePositionTargets = true;
Solver->SolverConstraints.bEnableKinematics = true;
Solver->SolverConstraints.CorotatedConstraints.bEnableCorotatedConstraint = true;

// 碰撞设置
Solver->SolverCollisions.bUseFloor = true;

// 力设置
Solver->SolverForces.bEnableGravity = true;
```

**配置组件物理属性：**

来源：`Public/ChaosFlesh/ChaosDeformableTetrahedralComponent.h`

```cpp
UDeformableTetrahedralComponent* FleshComp = ...;

// 设置仿真空间
FleshComp->SimulationSpace.SimSpace = ChaosDeformableSimSpace::World;
FleshComp->SimulationSpace.SimSpaceBoneName = FName("pelvis");

// 设置体力
FleshComp->BodyForces.bApplyGravity = true;
FleshComp->BodyForces.DampingMultiplier = 0.5f;
FleshComp->BodyForces.StiffnessMultiplier = 1.0f;
FleshComp->BodyForces.IncompressibilityMultiplier = 0.8f;
FleshComp->BodyForces.InflationMultiplier = 0.5f;

// 设置质量
FleshComp->MassMultiplier = 1.0f;
```

### 进阶用法

**通过 Dataflow 图驱动 FleshAsset：**

来源：`Public/ChaosFlesh/FleshAsset.h`

```cpp
// 创建或获取 FleshAsset
UFleshAsset* FleshAsset = NewObject<UFleshAsset>();

// 设置 Dataflow 图资产和终端
FleshAsset->SetDataflowAsset(DataflowAssetPtr);
FleshAsset->SetDataflowTerminal(TEXT("FleshAssetTerminal"));

// 通过编辑器回调修改 FleshCollection
{
    FFleshAssetEdit Edit = FleshAsset->EditCollection();
    if (TSharedPtr<FFleshCollection> Collection = Edit.GetFleshCollection())
    {
        // 编辑集合数据...
    }
    // FFleshAssetEdit 析构时自动触发 PostEditCallback
}

// 获取位置数据
const TManagedArray<FVector3f>* Positions = FleshAsset->FindPositions();
if (Positions)
{
    for (int32 i = 0; i < Positions->Num(); ++i)
    {
        FVector3f Pos = (*Positions)[i];
        // 处理位置数据...
    }
}

// 设置关联的骨骼网格体
FleshAsset->SkeletalMesh = SkeletalMeshPtr;
FleshAsset->Skeleton = SkeletonPtr;
FleshAsset->TargetDeformationSkeleton = DeformationSkeletalMeshPtr;
```

**GPU 缓冲区管理（用于自定义渲染器集成）：**

来源：`Public/ChaosFlesh/ChaosFleshDeformerBufferManager.h`

```cpp
using namespace Chaos::Softs;

UDeformableTetrahedralComponent* FleshComp = ...;
FChaosFleshDeformableGPUManager& GPUManager = FleshComp->GetGPUBufferManager();

// 注册 GPU 缓冲区消费者
const void* ConsumerID = /* your renderer ID */;
GPUManager.RegisterGPUBufferConsumer(ConsumerID);

// 初始化绑定缓冲区（指定 LOD 级别和网格名）
bool bSuccess = GPUManager.InitGPUBindingsBuffer(
    ConsumerID,
    FName("Body"),  // MeshName
    0,              // LodIndex
    false           // ForceInit
);

// 在渲染前更新 GPU 缓冲区（必须在游戏线程调用）
GPUManager.UpdateGPUBuffers();

// 获取绑定缓冲区数据用于自定义着色器
const FChaosFleshDeformableGPUManager::FBindingsBuffer* Bindings =
    GPUManager.GetBindingsBuffer(ConsumerID, FName("Body"), 0);

if (Bindings)
{
    // 获取 GPU 资源引用
    auto& RestVertsBuf = Bindings->GetRestVerticesBuffer();
    auto& VertsBuf = Bindings->GetVerticesBuffer();
    auto& ParentsBuf = Bindings->GetParentsBuffer();
    auto& WeightsBuf = Bindings->GetWeightsBuffer();
    auto& OffsetsBuf = Bindings->GetOffsetsBuffer();
    auto& MaskBuf = Bindings->GetMaskBuffer();
}
```

**GPU 缓冲区类型：**

来源：`Public/ChaosFlesh/ChaosDeformableGPUBuffers.h`

```cpp
using namespace UE::ChaosDeformable;

// 浮点缓冲区
FFloatArrayBufferWithSRV FloatBuf;
FloatBuf.SetBufferName(TEXT("MyFloatBuffer"));
FloatBuf.Init(FloatArray.GetData(), FloatArray.Num());

// 半精度浮点缓冲区（自动将 float 转换为 FFloat16）
FHalfArrayBufferWithSRV HalfBuf;
HalfBuf.Init(Vector3fArray);  // 接受 FVector3f 数组

// 索引缓冲区（自动压缩到最小类型 uint8/uint16/uint32）
FIndexArrayBufferWithSRV IndexBuf;
IndexBuf.Init(IntVector4Array);
IndexBuf.Force32BitPacking();  // 强制使用 32 位

// 判断数据类型
int32 Stride = IndexBuf.GetDataStride();  // sizeof(uint8), sizeof(uint16), 或 sizeof(uint32)
```

**环境碰撞检测（Gameplay 组件特有）：**

来源：`Public/ChaosFlesh/ChaosDeformableGameplayComponent.h`

```cpp
UDeformableGameplayComponent* GameplayComp = ...;

// 配置环境碰撞参数
GameplayComp->GameplayColllisions.RigBoundRayCasts.bEnableRigBoundRaycasts = true;
GameplayComp->GameplayColllisions.RigBoundRayCasts.MaxNumTests = 10;
GameplayComp->GameplayColllisions.RigBoundRayCasts.bTestDownOnly = true;
GameplayComp->GameplayColllisions.RigBoundRayCasts.TestRange = 0.5f;
GameplayComp->GameplayColllisions.RigBoundRayCasts.CollisionChannel = ECC_WorldStatic;

// 添加需要跳过的碰撞对象
GameplayComp->GameplayColllisions.RigBoundRayCasts.EnvironmentCollisionsSkipList.Add(
    SomePrimitiveComponent);

// 手动触发环境碰撞检测（通常在 PreSolverUpdate 中自动调用）
GameplayComp->DetectEnvironmentCollisions(
    100,          // MaxNumTests
    true,         // bTestDownOnly
    0.0f,         // TestRange（0.0 = 任何向下的方向）
    ECC_WorldStatic  // CollisionChannel
);
```

**缓存仿真数据（Chaos Cache 系统集成）：**

来源：`Public/ChaosCache/FleshComponentCacheAdapter.h`

```cpp
// FFleshCacheAdapter 自动注册到 Chaos Cache 系统
// 用于录制和回放仿真数据

// 获取可变形体求解器
Chaos::Softs::FDeformableSolver* Solver = 
    Chaos::FFleshCacheAdapter::GetDeformableSolver(PrimitiveComponent);

// 获取组件在演化粒子列表中的范围
Chaos::FRange ParticleRange = 
    Chaos::FFleshCacheAdapter::GetParticleRange(PrimitiveComponent, NumParticles);

// USD 缓存路径（需要 USE_USD_SDK）
#if USE_USD_SDK && DO_USD_CACHING
FString CacheDir = Chaos::FFleshCacheAdapter::GetUSDCacheDirectory(ObservedComponent);
FString CacheFile = Chaos::FFleshCacheAdapter::GetUSDCacheFilePathRO(ObservedComponent, FleshComp);
#endif
```

## Demo 示例

一个完整的可编译的最小示例，展示如何创建和使用 ChaosFlesh 仿真：

```cpp
// MyFleshSimulationComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "ChaosFlesh/FleshAsset.h"
#include "ChaosFlesh/FleshActor.h"
#include "ChaosFlesh/ChaosDeformableSolverActor.h"
#include "ChaosFlesh/ChaosDeformableTetrahedralComponent.h"
#include "MyFleshSimulationComponent.generated.h"

UCLASS(ClassGroup=(Physics), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyFleshSimulationComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyFleshSimulationComponent();

    /** Flesh 资产，存储四面体网格和绑定数据 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Flesh Simulation")
    TObjectPtr<UFleshAsset> FleshAsset;

    /** 物理求解器 Actor */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Flesh Simulation")
    TObjectPtr<ADeformableSolverActor> SolverActor;

    /** 仿真输出的骨骼位置数据 */
    UPROPERTY(BlueprintReadOnly, Category = "Flesh Simulation")
    TArray<FVector> DeformedPositions;

    /** 开始仿真 */
    UFUNCTION(BlueprintCallable, Category = "Flesh Simulation")
    void StartSimulation();

    /** 停止仿真 */
    UFUNCTION(BlueprintCallable, Category = "Flesh Simulation")
    void StopSimulation();

    /** 获取变形后的骨骼绑定位置 */
    UFUNCTION(BlueprintCallable, Category = "Flesh Simulation")
    TArray<FVector> GetDeformedBonePositions();

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, 
        FActorComponentTickFunction* ThisTickFunction) override;

private:
    UPROPERTY()
    TObjectPtr<UDeformableTetrahedralComponent> FleshComponent;

    UPROPERTY()
    TObjectPtr<AFleshActor> FleshActor;

    bool bSimulating = false;
};
```

```cpp
// MyFleshSimulationComponent.cpp
#include "MyFleshSimulationComponent.h"
#include "ChaosFlesh/ChaosDeformableSolverComponent.h"

UMyFleshSimulationComponent::UMyFleshSimulationComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyFleshSimulationComponent::BeginPlay()
{
    Super::BeginPlay();

    // 创建 FleshActor
    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = GetOwner();

    FleshActor = World->SpawnActor<AFleshActor>(
        AFleshActor::StaticClass(),
        GetOwner()->GetActorTransform(),
        SpawnParams);

    if (FleshActor && FleshAsset)
    {
        // 设置 FleshAsset
        FleshComponent = FleshActor->GetFleshComponent();
        if (FleshComponent)
        {
            FleshComponent->SetRestCollection(FleshAsset);
        }
    }
}

void UMyFleshSimulationComponent::StartSimulation()
{
    if (!FleshActor || !SolverActor || bSimulating)
    {
        return;
    }

    // 将 Flesh 注册到求解器并开始仿真
    FleshActor->EnableSimulation(SolverActor);
    bSimulating = true;
}

void UMyFleshSimulationComponent::StopSimulation()
{
    if (!FleshComponent || !bSimulating)
    {
        return;
    }

    FleshComponent->DisableSimulation();
    bSimulating = false;
}

void UMyFleshSimulationComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (bSimulating && FleshComponent)
    {
        // 每帧获取最新的变形位置
        DeformedPositions = FleshComponent->GetSkeletalMeshEmbeddedPositions(
            ChaosDeformableBindingOption::WorldPos,
            FTransform::Identity);
    }
}

TArray<FVector> UMyFleshSimulationComponent::GetDeformedBonePositions()
{
    return DeformedPositions;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心，提供可变形体求解器 |
| `ChaosSolverEngine` | Chaos 求解器引擎集成 |
| `GeometryCollectionEngine` | 几何集合引擎，提供 FManagedArrayCollection |
| `DataflowEngine` | Dataflow 图执行引擎 |
| `DataflowNodes` | Dataflow 节点库 |
| `OptimusCore` | GPU 计算框架（Compute Framework），用于 GPU 蒙皮变形器 |
| `RenderCore` | 渲染核心，GPU 缓冲区管理 |
| `RHI` | 渲染硬件接口 |
| `ProceduralMeshComponent` | 运行时程序化网格渲染 |
| `ChaosCache` | Chaos 缓存系统，用于仿真数据录制/回放 |
| `GeometryFramework` | 几何体框架 |
| `USD` | USD 格式缓存支持（可选） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `981bc9da` | Dataflow: | Dataflow 相关更新 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理纤维场生成节点代码 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复 MaskBuffer 的 NumMaskBuffer 赋值错误 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃 FleshAsset 中的 StaticMesh 属性 |

### 维护评价

**活跃维护中。** 该插件创建于 2022 年 3 月，约 4 年历史，最近提交集中在 2026 年 5 月，说明仍在积极开发。

关键观察：
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **API 快速演进**：代码中存在大量 `UE_DEPRECATED` 标记（5.6、5.7、5.8 各版本都有废弃 API），说明接口仍在频繁变更
- **功能持续完善**：最近的更新涉及 Dataflow 集成、GPU 蒙皮修复、纤维场生成等新功能
- **依赖较多**：依赖 Chaos、Dataflow、Optimus、ChaosCache 等多个子系统，集成复杂度高
- **无正式文档**：`.uplugin` 中 `DocsURL` 为空

**⚠️ 警告**：此插件为实验性功能，API 不稳定，生产环境使用需谨慎。部分属性（如 `YoungModulus`、`Damping`、`FleshAsset::StaticMesh`）已被废弃，应使用 Dataflow 节点替代。

**推荐程度**：如果你需要体积软体仿真功能且愿意跟踪实验性 API 变化，可以使用。否则建议等待正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- [官方文档]()（暂无）