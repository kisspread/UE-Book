# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 混沌软体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Dataflow图、测试资源） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

Chaos Flesh 是 Unreal Engine 5 中基于 Chaos 物理引擎的**高级可变形体（软体）模拟系统**。它超越了传统的布料模拟，提供了一个完整的框架，用于模拟具有体积、质量以及复杂材质属性（如刚度、阻尼、可压缩性）的物体。其核心是使用**四面体网格**作为物理模拟的代理，能够实现真实感更强的肌肉、器官、果冻、橡胶等软体效果。

该插件解决的主要问题包括：
1.  **体积保持**：模拟具有内部体积的物体，防止其坍缩。
2.  **真实的材质响应**：通过参数（如杨氏模量、泊松比）模拟不同软硬程度的材质。
3.  **与动画系统交互**：能够将物理模拟的结果应用到骨骼网格体上，驱动骨骼或顶点变形。
4.  **GPU 加速**：提供 GPU 缓冲区管理器，优化渲染和计算性能。

它主要面向需要高级软体物理效果的游戏、影视预览、虚拟仿真等场景。

## 使用场景

-   你在开发一个需要模拟肌肉颤动或脂肪抖动的角色（如格斗游戏中的打击效果、体育游戏中运动员的肉体碰撞）。
-   你需要创建可变形的环境物体，如果冻、橡胶玩具、布满黏液的生物等。
-   你需要一个软体物体能够与角色动画（骨骼）进行交互，例如软体旗帜附着在移动的旗杆上。
-   你正在研究或测试基于物理的生物力学或材料模拟，需要可编程、可扩展的物理求解器。

## 蓝图用法

系统的核心是组件化和资产化。主要通过 `UDeformableTetrahedralComponent` 及其子类来驱动模拟。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Rest Collection` | 设置组件使用的静态/休止状态资源 (`UFleshAsset`)，定义了模拟的初始形态、网格和属性。 | `UDeformableTetrahedralComponent` |
| `Get Rest Collection` | 获取当前设置的休止状态资源。 | `UDeformableTetrahedralComponent` |
| `Get Skeletal Mesh Embedded Positions` | 获取由物理模拟变形后的骨骼网格体顶点位置，用于驱动渲染网格。支持多种输出格式（世界/组件/骨骼空间）。 | `UDeformableTetrahedralComponent` |
| `Enable Simulation` | 将可变形体组件注册到指定的求解器组件 (`UDeformableSolverComponent`)，开始参与模拟。 | `UDeformablePhysicsComponent` |
| `Disable Simulation` | 将组件从求解器中注销，停止模拟。 | `UDeformablePhysicsComponent` |
| `Add Constrained Bodies` | 向约束组件 (`UDeformableConstraintsComponent`) 添加一对可变形体之间的约束关系。 | `UDeformableConstraintsComponent` |
| `Add Static Mesh Component` | 向碰撞组件 (`UDeformableCollisionsComponent`) 添加一个静态网格体作为碰撞体。 | `UDeformableCollisionsComponent` |

### 使用示例（蓝图描述）

1.  **基本设置**：
    *   在场景中放置一个 `AFleshActor` 或 `ADeformableSolverActor`。
    *   在 `AFleshActor` 的详情面板中，为其 `FleshComponent` 指定一个创建好的 `UFleshAsset`。
    *   放置一个 `ADeformableSolverActor` 作为全局求解器。
    *   在 `AFleshActor` 的 `PrimarySolver` 属性中指向刚才放置的求解器 Actor。
    *   调用 `Enable Simulation` 节点，将 FleshActor 注册到求解器。

2.  **驱动骨骼网格体**：
    *   在 `UFleshAsset` 中设置 `TargetDeformationSkeleton`。
    *   在游戏运行时，通过 `Get Skeletal Mesh Embedded Positions` 节点获取模拟后的顶点数据。
    *   将这些数据通过 `Set Morph Target` 或自定义变形器（如 Compute Deformer）应用到用于渲染的骨骼网格体组件上。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFlesh/FleshAsset.h"
#include "ChaosFlesh/ChaosDeformableTetrahedralComponent.h"
#include "ChaosFlesh/ChaosDeformableSolverComponent.h"
```

### 基本用法

```cpp
// 基于 FleshAsset.h 中的 UFleshAsset 接口
// 创建并配置一个 FleshAsset
void SetupFleshAsset()
{
    UFleshAsset* FleshAsset = NewObject<UFleshAsset>();

    // 通过 EditCollection 安全地编辑底层的 FFleshCollection
    FFleshAssetEdit Edit = FleshAsset->EditCollection();
    if (TSharedPtr<FFleshCollection> Collection = Edit.GetFleshCollection())
    {
        // 在这里修改集合数据，例如设置位置、四面体等
        // Collection->SetPositions(...);
    }
    // Edit 对象析构时会自动通知资产更新

    // 设置关联的骨骼网格体用于动画绑定
    FleshAsset->SkeletalMesh = MySkeletalMesh;
    // 设置用于变形的目标骨架
    FleshAsset->TargetDeformationSkeleton = MyDeformationSkeleton;

    // 配置物理求解器参数（可选）
    // FleshAsset->PreviewSolverTiming.NumSubSteps = 4;
}
```

### 进阶用法

```cpp
// 基于 ChaosDeformableTetrahedralComponent.h 和 ChaosDeformableSolverComponent.h
// 动态创建和控制模拟
void AdvancedSimulationControl()
{
    // 1. 创建求解器组件
    UDeformableSolverComponent* SolverComp = NewObject<UDeformableSolverComponent>(MyActor);
    SolverComp->RegisterComponent();

    // 配置求解器参数
    SolverComp->SolverTiming.NumSubSteps = 4;
    SolverComp->SolverTiming.NumSolverIterations = 8;
    SolverComp->SolverForces.bEnableGravity = true;

    // 2. 创建可变形体组件并绑定
    UDeformableTetrahedralComponent* TetComp = NewObject<UDeformableTetrahedralComponent>(MyActor);
    TetComp->RegisterComponent();

    // 设置资产
    UFleshAsset* Asset = /* ... */;
    TetComp->SetRestCollection(Asset);

    // 将组件注册到求解器
    TetComp->EnableSimulation(SolverComp);

    // 3. 在运行时查询模拟结果
    // 假设我们在 Tick 中
    void ATickActor::Tick(float DeltaTime)
    {
        Super::Tick(DeltaTime);

        // 获取模拟后的骨骼位置（世界坐标）
        TArray<FVector> DeformedPositions = TetComp->GetSkeletalMeshEmbeddedPositions(
            ChaosDeformableBindingOption::WorldPos,
            FTransform::Identity,
            NAME_None,
            1.0f);

        // 使用 DeformedPositions 更新渲染网格...
    }
}
```

## Demo 示例

一个最小的可编译示例，演示如何创建求解器和可变形体组件。

**ChaosFleshDemoActor.h**
```cpp
#pragma once

#include "GameFramework/Actor.h"
#include "ChaosFleshDemoActor.generated.h"

class UDeformableSolverComponent;
class UDeformableTetrahedralComponent;
class UFleshAsset;

UCLASS()
class AChaosFleshDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AChaosFleshDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Physics")
    TObjectPtr<UDeformableSolverComponent> SolverComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Physics")
    TObjectPtr<UDeformableTetrahedralComponent> TetrahedralComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Physics")
    TObjectPtr<UFleshAsset> FleshAsset;
};
```

**ChaosFleshDemoActor.cpp**
```cpp
#include "ChaosFleshDemoActor.h"
#include "ChaosFlesh/ChaosDeformableSolverComponent.h"
#include "ChaosFlesh/ChaosDeformableTetrahedralComponent.h"
#include "ChaosFlesh/FleshAsset.h"

AChaosFleshDemoActor::AChaosFleshDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建求解器组件
    SolverComponent = CreateDefaultSubobject<UDeformableSolverComponent>(TEXT("Solver"));
    SolverComponent->SetIsReplicated(false);

    // 创建可变形四面体组件
    TetrahedralComponent = CreateDefaultSubobject<UDeformableTetrahedralComponent>(TEXT("Tetrahedral"));
    TetrahedralComponent->SetupAttachment(RootComponent);
}

void AChaosFleshDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 设置资产并开始模拟
    if (FleshAsset)
    {
        TetrahedralComponent->SetRestCollection(FleshAsset);
    }
    // 将组件注册到求解器以启动模拟
    TetrahedralComponent->EnableSimulation(SolverComponent);
}
```

## 模块依赖

该插件深度依赖于 Chaos 物理系统和 UE 的 Deformable（可变形体）框架。要在你的模块中使用它，需要在 `Build.cs` 中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `ChaosFlesh` | 核心基础模块，包含集合 (`FFleshCollection`) 和通用类型。 |
| `ChaosFleshEngine` | 运行时引擎模块，包含所有 Actor、Component、Asset 类的实现。**使用此插件的主要接口**。 |
| `Chaos` | Chaos 物理引擎核心，提供底层的求解器、粒子、约束等基础系统。 |
| `Deformable` | 可变形体框架，提供 `FDeformableSolver`、`FThreadingProxy` 等抽象和基础设施。 |
| `Dataflow` | 可选。如果使用 Dataflow 图来生成或驱动模拟数据，则需要此模块。 |
| `GeometryProcessing` | 可选。用于网格生成、四面体化等几何处理操作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为单精度的警告。 |
| 2026-05-12 | `981bc9da` | Dataflow: | 更新 Dataflow 相关节点（具体信息不足）。 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理了纤维场生成节点的代码。 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复了遮罩缓冲区从偏移缓冲区错误赋值的bug。 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃了 FleshAsset 中的 StaticMesh 属性。 |

### 维护评价

**维护状态：活跃维护中**。

Chaos Flesh 插件自 2022 年创建以来，一直处于积极的开发和迭代中。从近期的提交历史可以看出，团队在不断修复 bug（如缓冲区赋值错误、编译警告）、清理代码、废弃过时接口，并扩展功能（如 Dataflow 集成）。最近一次更新就在一周前，表明该模块是 Epic 当前工作重点的一部分。

由于它仍标记为 **实验性 (`IsExperimentalVersion = true`) 且默认未启用 (`EnabledByDefault = false`)**，意味着 API 可能会有变动，且需要用户手动在项目设置中启用。它适合用于原型开发、研究或对最新技术有需求的项目，但在生产环境中使用时需要密切关注版本更新和潜在的 API 破坏性变更。

**推荐使用**：如果你的项目确实需要高质量的实时软体物理模拟，并且能够接受实验性 API 的不稳定性，那么 Chaos Flesh 是 UE5 中目前最强大和官方的解决方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
-   [官方文档]() (暂无公开文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh/Tests) (可能存在)