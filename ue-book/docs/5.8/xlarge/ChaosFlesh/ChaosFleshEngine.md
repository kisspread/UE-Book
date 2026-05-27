# Chaos Flesh

> Chaos Flesh Simulation（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | 柔体仿真 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Dataflow 图资产、Flesh 资产） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是基于 Chaos 物理引擎构建的**体素化柔体（Flesh）仿真系统**。它使用**四面体网格（Tetrahedral Mesh）**作为体积离散化手段，模拟软组织、肌肉等可变形物体的物理行为。

核心解决问题：
- **体积保持的柔体变形**：通过四面体有限元方法实现体积守恒的软体仿真，不同于基于表面的布料仿真
- **骨骼网格绑定**：将四面体仿真结果通过权重绑定（Bindings）传递到骨骼网格体表面，驱动皮肤变形
- **肌肉激活驱动**：支持基于原点-插入点长度的肌肉激活，可从动画曲线覆盖
- **GPU 变形管线**：通过 Compute Framework 的 Data Interface 将绑定数据上送 GPU，实现高效的蒙皮变形
- **Dataflow 驱动**：资产的几何数据通过 Dataflow 图节点管线生成，支持程序化内容创作

## 使用场景

- 你在制作角色的肌肉、脂肪等软组织物理效果 → 用 ChaosFlesh 配合骨骼网格绑定
- 你需要体积保持的柔体仿真（如果冻、内脏） → 用 ChaosFlesh 的四面体有限元求解器
- 你希望通过 Dataflow 图程序化生成仿真资产 → 用 FleshAsset + Dataflow 图
- 你需要在 GPU 端高效计算蒙皮变形 → 用 UDIFleshDeformer Data Interface
- 你需要记录/回放柔体仿真结果 → 用 Chaos Cache + FFleshCacheAdapter
- 你需要柔体与场景的环境碰撞检测 → 用 UDeformableGameplayComponent 的射线检测

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRestCollection` | 设置静态 Flesh 资产（仿真休息状态） | `UDeformableTetrahedralComponent` |
| `GetRestCollection` | 获取当前静态 Flesh 资产 | `UDeformableTetrahedralComponent` |
| `GetSkeletalMeshEmbeddedPositions` | 获取绑定在四面体中的骨骼点位（支持多种空间格式） | `UDeformableTetrahedralComponent` |
| `EnableSimulation` | 将组件注册到求解器并启动仿真 | `UDeformablePhysicsComponent` |
| `DisableSimulation` | 从求解器注销并停止仿真 | `UDeformablePhysicsComponent` |
| `EnableSimulationFromActor` | 从求解器 Actor 启用仿真 | `UDeformablePhysicsComponent` |
| `ResetSimulationProperties` | 重置求解器属性（时间步、碰撞、约束等） | `UDeformableSolverComponent` |
| `AddConstrainedBodies` | 添加两个 Flesh 组件之间的约束 | `UDeformableConstraintsComponent` |
| `RemoveConstrainedBodies` | 移除两个 Flesh 组件之间的约束 | `UDeformableConstraintsComponent` |
| `AddStaticMeshComponent` | 添加静态网格作为碰撞体 | `UDeformableCollisionsComponent` |
| `RemoveStaticMeshComponent` | 移除碰撞体 | `UDeformableCollisionsComponent` |
| `SetDataflowAsset` | 设置 Flesh 资产的 Dataflow 图 | `UFleshAsset` |
| `SetDataflowTerminal` | 设置 Dataflow 图的终端节点名 | `UFleshAsset` |
| `EnableSimulation` (Actor) | Actor 级别启用仿真 | `AFleshActor` |

### 使用示例（蓝图描述）

**基础柔体仿真设置：**

1. 在场景中放置一个 `ADeformableSolverActor`（求解器 Actor）
2. 放置一个 `AFleshActor`（Flesh Actor），在 Details 面板设置 `PrimarySolver` 指向求解器
3. 在 FleshActor 的 FleshComponent 上设置 `RestCollection` 指向一个 `UFleshAsset`
4. 在 UFleshAsset 上配置 Dataflow 图以生成四面体网格数据
5. 在求解器组件上调整 `SolverTiming`（子步数、迭代次数）、`BodyForces`（重力、刚度、阻尼）等参数
6. 调用 `EnableSimulation` 开始仿真

**获取变形后骨骼位置：**

1. 创建一个 `UDeformableTetrahedralComponent` 并注册到求解器
2. 设置 `RestCollection`（需包含 `TargetDeformationSkeleton` 绑定数据）
3. 调用 `GetSkeletalMeshEmbeddedPositions`，传入格式（World/Component/Bone 空间的位置或增量）、目标骨骼名称和混合权重
4. 返回的 `TArray<FVector>` 即为变形后的骨骼点位置

**柔体约束设置：**

1. 放置 `ADeformableConstraintsActor`，关联两个 `AFleshActor` 到 `SourceBodies` 和 `TargetBodies`
2. 设置 `PrimarySolver` 指向求解器
3. 调用 `EnableSimulation` 绑定到求解器

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFlesh/ChaosDeformableTetrahedralComponent.h"
#include "ChaosFlesh/ChaosDeformableSolverComponent.h"
#include "ChaosFlesh/FleshAsset.h"
#include "ChaosFlesh/ChaosDeformablePhysicsComponent.h"
#include "ChaosFlesh/ChaosDeformableGameplayComponent.h"
#include "ChaosFlesh/FleshDynamicAsset.h"
#include "ChaosFlesh/SimulationAsset.h"
#include "DataInterfaces/DIFleshDeformer.h"
#include "ChaosFlesh/ChaosDeformableGPUBuffers.h"
```

### 基本用法

**创建并配置 Flesh 求解器和组件：**

```cpp
// 基于 Public/ChaosFlesh/ChaosDeformableSolverComponent.h 和 ChaosDeformableTetrahedralComponent.h

// 1. 创建求解器 Actor（或使用已有的 ADeformableSolverActor）
ADeformableSolverActor* SolverActor = GetWorld()->SpawnActor<ADeformableSolverActor>();
UDeformableSolverComponent* SolverComp = SolverActor->GetDeformableSolverComponent();

// 2. 配置求解器属性
SolverComp->SolverTiming.NumSubSteps = 4;
SolverComp->SolverTiming.NumSolverIterations = 10;
SolverComp->SolverTiming.bDoThreadedAdvance = true;
SolverComp->SolverTiming.ExecutionModel = EDeformableExecutionModel::Chaos_Deformable_PostPhysics;

// 3. 配置力和约束
SolverComp->SolverForces.bEnableGravity = true;
SolverComp->SolverConstraints.bEnablePositionTargets = true;
SolverComp->SolverConstraints.CorotatedConstraints.bEnableCorotatedConstraint = true;

// 4. 配置碰撞
SolverComp->SolverCollisions.bUseFloor = true;
SolverComp->SolverConstraints.GaussSeidelConstraints.bUseGaussSeidelConstraints = true;
SolverComp->SolverConstraints.GaussSeidelConstraints.SpringCollision.bDoSpringCollision = true;
```

**注册 Flesh 组件到求解器：**

```cpp
// 基于 Public/ChaosFlesh/ChaosDeformablePhysicsComponent.h

// 通过蓝图可用的方法注册
UDeformableTetrahedralComponent* FleshComp = /* 获取组件 */;
UDeformableSolverComponent* SolverComp = /* 获取求解器 */;
FleshComp->EnableSimulation(SolverComp);

// 或从 Actor 启用
FleshComp->EnableSimulationFromActor(SolverActor);
```

**设置 Flesh 资产并获取变形位置：**

```cpp
// 基于 Public/ChaosFlesh/ChaosDeformableTetrahedralComponent.h

// 设置 RestCollection
UDeformableTetrahedralComponent* TetComp = /* 组件 */;
TetComp->SetRestCollection(MyFleshAsset);

// 配置仿真空间
TetComp->SimulationSpace.SimSpace = ChaosDeformableSimSpace::World;
TetComp->SimulationSpace.SimSpaceBoneName = FName("pelvis");

// 配置体力
TetComp->BodyForces.bApplyGravity = true;
TetComp->BodyForces.DampingMultiplier = 0.5f;
TetComp->BodyForces.StiffnessMultiplier = 1.0f;
TetComp->MassMultiplier = 1.0f;

// 仿真后获取绑定位置
FTransform Offset = FTransform::Identity;
TArray<FVector> Positions = TetComp->GetSkeletalMeshEmbeddedPositions(
    ChaosDeformableBindingOption::WorldPos,
    Offset,
    FName("spine_01"),
    1.0f  // SimulationBlendWeight
);
```

### 进阶用法

**GPU 变形管线配置：**

```cpp
// 基于 Public/ChaosFlesh/ChaosFleshDeformerBufferManager.h

// 获取 GPU Buffer Manager
UDeformableTetrahedralComponent* TetComp = /* 组件 */;
Chaos::Softs::FChaosFleshDeformableGPUManager& GPUManager = TetComp->GetGPUBufferManager();

// 设置组件所有者
GPUManager.SetOwner(TetComp);

// 注册 GPU Buffer 消费者
const void* ConsumerID = /* 通常是 MeshComponent 或 Deformer 的指针 */;
GPUManager.RegisterGPUBufferConsumer(ConsumerID);

// 初始化绑定缓冲（按网格名和 LOD 索引）
FName MeshName = FName("Body");
int32 LodIndex = 0;
bool bSuccess = GPUManager.InitGPUBindingsBuffer(ConsumerID, MeshName, LodIndex, /*ForceInit=*/false);

// 每帧更新 GPU 缓冲
GPUManager.UpdateGPUBuffers();

// 获取绑定数据（包含顶点、父节点、权重、偏移、遮罩等缓冲）
const auto* Bindings = GPUManager.GetBindingsBuffer(ConsumerID, MeshName, LodIndex);
if (Bindings)
{
    const auto& VerticesBuf = Bindings->GetVerticesBuffer();
    const auto& ParentsBuf = Bindings->GetParentsBuffer();
    const auto& WeightsBuf = Bindings->GetWeightsBuffer();
}
```

**GPU 缓冲对象使用：**

```cpp
// 基于 Public/ChaosFlesh/ChaosDeformableGPUBuffers.h

// 浮点缓冲
UE::ChaosDeformable::FFloatArrayBufferWithSRV FloatBuffer;
FloatBuffer.SetBufferName(TEXT("MyFloatBuffer"));
FloatBuffer.Init(MyFloatArray);  // TArray<float>
// 渲染线程自动初始化 RHI 资源

// 半精度缓冲（节省带宽）
UE::ChaosDeformable::FHalfArrayBufferWithSRV HalfBuffer;
HalfBuffer.SetBufferName(TEXT("MyHalfBuffer"));
HalfBuffer.Init(MyFloatArray);  // 自动 float -> FFloat16 转换
HalfBuffer.Init(MyVector3fArray.GetData(), MyVector3fArray.Num());  // 从 FVector3f

// 整数索引缓冲（自动选择 uint8/uint16/uint32 压缩）
UE::ChaosDeformable::FIndexArrayBufferWithSRV IndexBuffer;
IndexBuffer.SetBufferName(TEXT("MyIndexBuffer"));
IndexBuffer.Init(MyIntVector4Array);  // 自动压缩
IndexBuffer.Force32BitPacking();  // 强制 32 位
```

**Flesh 资产的编辑模式（线程安全）：**

```cpp
// 基于 Public/ChaosFlesh/FleshAsset.h

// 通过 Edit 对象修改 FleshCollection（自动触发失效和通知）
{
    FFleshAssetEdit EditObject = MyFleshAsset->EditCollection();
    if (TSharedPtr<FFleshCollection> Collection = EditObject.GetFleshCollection())
    {
        // 在此处修改集合数据
        // 析构 EditObject 时自动调用 PostEditCallback
    }
}

// 只读访问
TSharedPtr<const FFleshCollection> RestCollection = MyFleshAsset->GetFleshCollection();
const TManagedArray<FVector3f>* Positions = RestCollection->FindPositions();

// 获取材料列表
TArray<FSkeletalMaterial> Materials = MyFleshAsset->GetMaterials();

// Dataflow 配置
MyFleshAsset->SetDataflowAsset(MyDataflowGraph);
MyFleshAsset->SetDataflowTerminal(TEXT("FleshAssetTerminal"));
```

**Dataflow 内容读写：**

```cpp
// 基于 Public/ChaosFlesh/FleshAsset.h - UDataflowFleshContent

// UFleshAsset 实现了 IDataflowContentOwner 和 IDataflowInstanceInterface
// 可以通过 Dataflow 求值图来生成几何数据

// 创建 Dataflow 内容对象
TObjectPtr<UDataflowBaseContent> Content = MyFleshAsset->CreateDataflowContent();

// 写入 Dataflow 内容（从资产到内容对象）
MyFleshAsset->WriteDataflowContent(Content);

// 从内容对象读回
MyFleshAsset->ReadDataflowContent(Content);

// 获取 Dataflow 实例
FDataflowInstance& Instance = MyFleshAsset->GetDataflowInstance();
```

**约束组件使用：**

```cpp
// 基于 Public/ChaosFlesh/ChaosDeformableConstraintsComponent.h

UDeformableConstraintsComponent* ConstraintsComp = /* 获取约束组件 */;

// 配置约束参数
FDeformableConstraintParameters Params;
Params.Stiffness = 100000.f;
Params.Damping = 1.f;
// Type 可选 Kinematic 等 EDeformableConstraintType

// 添加两个 Flesh 组件之间的约束
UFleshComponent* Source = /* 源组件 */;
UFleshComponent* Target = /* 目标组件 */;
ConstraintsComp->AddConstrainedBodies(Source, Target, Params);

// 移除约束
ConstraintsComp->RemoveConstrainedBodies(Source, Target, Params);

// 读取当前约束列表
TArray<FConstraintObject>& Constraints = ConstraintsComp->Constraints;
```

**环境碰撞检测（游戏玩法组件）：**

```cpp
// 基于 Public/ChaosFlesh/ChaosDeformableGameplayComponent.h

UDeformableGameplayComponent* GameplayComp = /* 组件 */;

// 配置环境碰撞
GameplayComp->GameplayColllisions.RigBoundRayCasts.bEnableRigBoundRaycasts = true;
GameplayComp->GameplayColllisions.RigBoundRayCasts.MaxNumTests = 10;
GameplayComp->GameplayColllisions.RigBoundRayCasts.bTestDownOnly = true;
GameplayComp->GameplayColllisions.RigBoundRayCasts.TestRange = 0.5f;
GameplayComp->GameplayColllisions.RigBoundRayCasts.CollisionChannel = ECC_WorldStatic;

// 添加跳过碰撞的组件
GameplayComp->GameplayColllisions.RigBoundRayCasts.EnvironmentCollisionsSkipList.Add(MySkipComponent);
```

## Demo 示例

### 最小 Flesh 仿真示例

**MyFleshSimulationActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChaosFlesh/ChaosDeformableSolverActor.h"
#include "ChaosFlesh/ChaosDeformableSolverComponent.h"
#include "ChaosFlesh/ChaosDeformableTetrahedralComponent.h"
#include "ChaosFlesh/FleshAsset.h"
#include "MyFleshSimulationActor.generated.h"

UCLASS()
class MYPROJECT_API AMyFleshSimulationActor : public AActor
{
    GENERATED_BODY()

public:
    AMyFleshSimulationActor();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Flesh")
    TObjectPtr<UFleshAsset> FleshAsset;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UDeformableSolverComponent> SolverComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UDeformableTetrahedralComponent> TetrahedralComponent;
};
```

**MyFleshSimulationActor.cpp**
```cpp
#include "MyFleshSimulationActor.h"
#include "ChaosFlesh/ChaosDeformablePhysicsComponent.h"

AMyFleshSimulationActor::AMyFleshSimulationActor()
{
    // 创建求解器组件
    SolverComponent = CreateDefaultSubobject<UDeformableSolverComponent>(TEXT("Solver"));
    SolverComponent->SolverTiming.NumSubSteps = 4;
    SolverComponent->SolverTiming.NumSolverIterations = 10;
    SolverComponent->SolverTiming.bDoThreadedAdvance = true;
    SolverComponent->SolverForces.bEnableGravity = true;
    SolverComponent->SolverConstraints.CorotatedConstraints.bEnableCorotatedConstraint = true;

    // 创建四面体组件
    TetrahedralComponent = CreateDefaultSubobject<UDeformableTetrahedralComponent>(TEXT("Flesh"));
    TetrahedralComponent->BodyForces.bApplyGravity = true;
    TetrahedralComponent->BodyForces.DampingMultiplier = 0.8f;
    TetrahedralComponent->MassMultiplier = 1.0f;
}

void AMyFleshSimulationActor::BeginPlay()
{
    Super::BeginPlay();

    if (FleshAsset && TetrahedralComponent && SolverComponent)
    {
        // 设置 Flesh 资产
        TetrahedralComponent->SetRestCollection(FleshAsset);

        // 注册到求解器
        TetrahedralComponent->EnableSimulation(SolverComponent);

        UE_LOG(LogTemp, Log, TEXT("Flesh simulation initialized with asset: %s"), *FleshAsset->GetName());
    }
}
```

## 模块依赖

> 注：Build.cs 源码未在提供的信息中，以下依赖基于头文件包含关系和类型引用推断。

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心（FDeformableSolver、FPBDEvolution 等） |
| `GeometryCollectionEngine` | 几何集合引擎（FFleshCollection 基于 FManagedArrayCollection） |
| `Dataflow` | Dataflow 图执行框架（FDataflowInstance、UDataflow） |
| `DataflowEngine` | Dataflow 引擎集成（IDataflowContentOwner、IDataflowGeometryCachable） |
| `OptimusCore` | Compute Framework Data Interface（UOptimusComputeDataInterface） |
| `ChaosSolverEngine` | Chaos 求解器引擎适配（FPhysicsSolverInterface） |
| `RenderCore` | GPU 缓冲资源（FVertexBufferWithSRV） |
| `RHI` | RHI 资源创建（FRHICommandListBase） |
| `ProceduralMeshComponent` | 程序化网格渲染（UProceduralMeshComponent） |
| `ChaosCache` | 仿真缓存录制/回放（FComponentCacheAdapter） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-05-12 | `981bc9da` | Dataflow: | Dataflow 相关更新 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理纤维场生成节点代码 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复遮罩缓冲区赋值逻辑错误 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃 FleshAsset 中的 StaticMesh 属性 |

### 维护评价

- **活跃维护**：最近提交集中在 2026 年 5 月，包含 bug 修复、代码清理、废弃旧接口等实质性改动，维护非常活跃
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，仍处于实验阶段，API 可能发生变化
- **API 演进中**：多个属性已标记为废弃（`UE_DEPRECATED`），如 `YoungModulus`、`Damping`、`StaticMesh`、旧的集合访问方式等，建议使用新的 Dataflow 节点替代
- **模块化架构**：5 个模块分工明确（引擎核心、节点、编辑器、废弃节点），代码规模约 170 个源文件，属于中大型插件
- **GPU 管线完善**：包含完整的 GPU 缓冲管理和 Compute Framework Data Interface 支持
- **⚠️ 注意**：作为实验性插件，API 不保证向后兼容，生产环境使用需谨慎。建议密切关注版本更新中的废弃标记

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- 官方文档（暂无）