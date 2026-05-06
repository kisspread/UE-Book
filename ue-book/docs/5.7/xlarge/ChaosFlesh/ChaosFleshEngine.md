# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 混沌肉体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Dataflow 资产、蓝图资产） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

Chaos Flesh 是 Epic Games 的实验性物理模拟插件，基于 Chaos 物理系统实现**可变形体的四边体（Tetrahedral）有限元仿真**。它提供了从资产定义（`FFleshCollection`）到运行时求解器（`FDeformableSolver`）的完整管线，支持：

- 基于**四边体网格**的软组织形变模拟（肌肉、脂肪、皮肤等）
- 与**骨骼网格体**绑定，驱动角色蒙皮形变
- 环境碰撞检测与约束（刚体、布料、自身碰撞）
- 通过 **Dataflow** 图形化编辑模拟配置
- **GPU 缓冲区**管理，支持 Compute Shader 驱动的形变输出
- **USD / Chaos Cache** 缓存与回放

该插件解决了传统骨骼动画无法处理的**有机体动态形变**需求，适用于角色皮肤挤压、内脏晃动、生物力学模拟等场景。

## 使用场景

- **角色软组织**：为角色制作真实的腹部、臀部、胸部形变，当角色移动或受力时产生自然挤压。
- **生物力学模拟**：用于医学或游戏中的肌肉/脂肪模拟，结合骨骼动画产生次级运动。
- **物理驱动的面部表情**：通过四边体网格驱动面部皮肤，产生更真实的褶皱和拉伸。
- **交互式变形物体**：玩家推动软体物体（如果冻、气球）时产生实时形变。
- **与 Dataflow 结合**：使用可视化图表配置模拟参数，无需编写 C++ 代码。

## 蓝图用法

### 核心蓝图节点

以下节点来自 `ADeformableSolverActor`、`AFleshActor`、`UDeformablePhysicsComponent` 等公开类型。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableSimulation` | 将此肉体组件注册到指定的求解器，开始模拟 | `AFleshActor`, `ADeformableCollisionsActor` |
| `DisableSimulation` | 从求解器移除该组件，停止模拟 | `UDeformablePhysicsComponent` |
| `AddStaticMeshComponent` | 向碰撞组件添加一个静态网格体作为碰撞对象 | `UDeformableCollisionsComponent` |
| `RemoveStaticMeshComponent` | 从碰撞组件中移除一个静态网格体 | `UDeformableCollisionsComponent` |
| `GetCollisionsComponent` | 获取关联的碰撞组件 | `ADeformableCollisionsActor` |
| `GetDeformableSolverComponent` | 获取求解器组件 | `ADeformableSolverActor` |
| `GetFleshComponent` | 获取肉体组件 | `AFleshActor` |

### 典型蓝图流程

1. 在关卡中放置一个 **ADeformableSolverActor**（求解器角色）和一个 **AFleshActor**（肉体角色）。
2. 设置 **AFleshActor** 的 `FleshComponent` → `FleshAsset`（一个预配置的四边体资产）。
3. 在求解器角色的 `SolverComponent` 中配置模拟参数（如时间步、迭代次数、碰撞设置）。
4. 调用 `AFleshActor` 的 `EnableSimulation`，目标选择求解器角色。
5. 运行时，肉体组件将自动跟随求解器更新，产生形变。
6. 如需环境碰撞，添加 `AStaticMeshActor` 并调用 `AddStaticMeshComponent`。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFlesh/ChaosDeformableTetrahedralComponent.h"
#include "ChaosFlesh/FleshActor.h"
#include "ChaosFlesh/ChaosDeformableSolverActor.h"
```

### 基本用法

```cpp
// 创建求解器角色和肉体角色（通常已在关卡中放置）
ADeformableSolverActor* SolverActor = GetWorld()->SpawnActor<ADeformableSolverActor>();
AFleshActor* FleshActor = GetWorld()->SpawnActor<AFleshActor>();

// 设置肉体资产（需提前加载）
UFleshAsset* FleshAsset = LoadObject<UFleshAsset>(nullptr, TEXT("/Game/Flesh/MyFleshAsset.MyFleshAsset"));
FleshActor->FleshComponent->FleshAsset = FleshAsset;

// 启用模拟
FleshActor->EnableSimulation(SolverActor);
```

### 进阶用法：自定义碰撞组件

```cpp
// 创建碰撞角色
ADeformableCollisionsActor* CollisionActor = GetWorld()->SpawnActor<ADeformableCollisionsActor>();
CollisionActor->EnableSimulation(SolverActor);

// 添加场景中的静态网格体作为碰撞体
for (AStaticMeshActor* StaticActor : WallActors)
{
    CollisionActor->DeformableCollisionsComponent->AddStaticMeshComponent(StaticActor->GetStaticMeshComponent());
}
```

### 从代码设置模拟参数

```cpp
// 获取求解器组件
UDeformableSolverComponent* SolverComp = SolverActor->GetDeformableSolverComponent();
if (SolverComp)
{
    // 调整时间步与迭代次数
    SolverComp->SolverTiming.NumSubSteps = 4;
    SolverComp->SolverTiming.NumSolverIterations = 10;

    // 开启网格碰撞
    SolverComp->SolverGridBasedCollisions.bUseGridBasedConstraints = true;
    SolverComp->SolverGridBasedCollisions.GridDx = 15.0f;
}
```

### 收集形变结果

```cpp
UDeformableTetrahedralComponent* FleshComponent = FleshActor->FleshComponent;
if (FleshComponent)
{
    // 访问模拟后的顶点位置（在游戏线程，需同步）
    const FFleshDynamicAsset* DynamicAsset = FleshComponent->GetFleshDynamicAsset();
    if (DynamicAsset)
    {
        const TManagedArray<FVector3f>* Positions = DynamicAsset->FindPositions();
        if (Positions)
        {
            // 更新渲染网格等
        }
    }
}
```

## Demo 示例

以下是一个最小 C++ 示例，展示如何使一个 StaticMesh 塌陷为四边体并驱动其形变。

### FleshDemoActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChaosFlesh/ChaosDeformableSolverActor.h"
#include "ChaosFlesh/FleshActor.h"
#include "FleshDemoActor.generated.h"

UCLASS()
class AFleshDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AFleshDemoActor();

    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Demo")
    TObjectPtr<ADeformableSolverActor> SolverActor;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Demo")
    TObjectPtr<AFleshActor> FleshActor;
};
```

### FleshDemoActor.cpp

```cpp
#include "FleshDemoActor.h"
#include "ChaosFlesh/FleshAsset.h"

AFleshDemoActor::AFleshDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AFleshDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建求解器
    FActorSpawnParameters SpawnParams;
    SolverActor = GetWorld()->SpawnActor<ADeformableSolverActor>(FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);

    // 创建肉体角色
    FleshActor = GetWorld()->SpawnActor<AFleshActor>(FVector(0, 0, 100), FRotator::ZeroRotator, SpawnParams);

    // 设置肉体资产（需提前在 Content Browser 中创建）
    static ConstructorHelpers::FObjectFinder<UFleshAsset> FleshAssetFinder(TEXT("/Game/Demo/DemoFleshAsset.DemoFleshAsset"));
    if (FleshAssetFinder.Succeeded())
    {
        FleshActor->FleshComponent->FleshAsset = FleshAssetFinder.Object;
    }

    // 启用模拟
    FleshActor->EnableSimulation(SolverActor);
}
```

## 模块依赖

**注意**：以下依赖基于 ChaosFleshEngine 模块的 `Build.cs` 推断。使用时请确保你的模块添加了相应 PublicDependencyModuleNames.

| 模块 | 用途 |
|---|---|
| `Chaos` | 物理引擎核心（动态求解器、粒子、碰撞） |
| `GeometryCollection` | 几何集合管理（FleshCollection 基类） |
| `Dataflow` | 可视化数据流图表编辑 |
| `DataflowEngine` | Dataflow 运行时执行 |
| `ProceduralMeshComponent` | 动态网格生成与更新 |
| `ComputeFramework` | Compute Shader 驱动的形变输出 |
| `OptimusCore` | 优化器数据接口（DIFleshDeformer） |
| `USD (可选)` | 缓存输出到 USD 格式 |
| `ChaosFlesh` | 核心模拟类型定义 |

**省略标准依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore 等。

## 维护状态

### 近期更新

- **2025-10-22** `a1039b21` — USD: Disabled UE allocator in USD for Windows.
- **2025-10-17** `be609b71` — [Backout] - CL47041219
- **2025-10-17** `7ab79237` — USD: Disabled UE allocator in USD for Windows.
- **2025-10-03** `71e223a6` — Dataflow: 增加预览显隐控制
- **2025-10-01** `dca9c2ee` — Add a way for each dataflow editors to hide geometry cache properties in the preview menu based on t

### 维护评价

- **创建时间**：2025-10-01（实验性插件）
- **近期更新**：主要是 USD 和 Dataflow 的编译修复和功能补充，无实质性模拟逻辑更新
- **活跃状态**：**维护中**（最近 1 个月内有提交）
- **注意事项**：插件标记为 `IsExperimentalVersion=true`，API 可能频繁变动。目前不推荐用于生产项目，但适合研究或原型开发。
- **已知问题**：部分功能依赖 USD SDK（可选），且仅在编辑器模式下完整可用；运行时模拟稳定性需验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFleshEditor/Private) *(编辑器测试)*
- [Dataflow 文档](https://docs.unrealengine.com/5.7/en-US/dataflow-in-unreal-engine/) *(通用 Dataflow 概念)*