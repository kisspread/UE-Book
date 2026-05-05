# ChaosDataflowSolver

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（物理资产） |
| 模块 | `ChaosDataflowSolver` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosDataflowSolver) | |

## 用途

ChaosDataflowSolver 是一个实验性插件，其核心功能是作为 **Dataflow 图形化编程系统与 Chaos 物理引擎之间的桥梁**。它提供了一个 Actor (`AChaosDataflowSolverActor`) 和一个 Component (`UChaosSolverBindingComponent`)，用于将 UE 中的物理组件（如 `UPrimitiveComponent`、`UInstancedStaticMeshComponent`）连接到基于 Dataflow 的 Chaos 物理求解器。

该插件解决的问题是：允许开发者通过 Dataflow 的可视化节点图来定义和驱动物理模拟流程，而不是完全依赖传统的物理资产或蓝图。它为需要高度定制化、程序化或数据驱动的物理模拟场景（如复杂的破坏系统、程序化生成的物体交互）提供了一种新的实验性工作流。

## 使用场景

- **你需要通过 Dataflow 图形化编程来控制物理模拟**：使用 `AChaosDataflowSolverActor` 作为 Dataflow 物理求解器的载体，并通过 `UChaosSolverBindingComponent` 将场景中的物理物体绑定到该求解器。
- **你希望将现有的物理资产（如带有碰撞的静态网格）集成到 Dataflow 工作流中**：通过 `UChaosSolverBindingComponent` 将这些组件的物理体注册到 Dataflow 求解器中进行模拟。
- **你正在实验 Chaos 物理引擎的新 API（RigidPhysics）**：该插件内部使用了 `RigidPhysics` 模块来创建和管理刚体，是探索该新 API 的一个入口。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Solver Active` | 控制求解器是否能够模拟其控制的粒子。 | `AChaosDataflowSolverActor` |
| `Simulation Actor` (属性) | 指向用于模拟的 `AChaosDataflowSolverActor` 实例。 | `UChaosSolverBindingComponent` |
| `Keep Kinematic In Original` (属性) | 控制是否在原始组件中保持运动学状态。 | `UChaosSolverBindingComponent` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `AChaosDataflowSolverActor`。
2.  在需要参与 Dataflow 物理模拟的 Actor 上，添加 `UChaosSolverBindingComponent`。
3.  在 `UChaosSolverBindingComponent` 的细节面板中，将 `Simulation Actor` 属性指向场景中的 `AChaosDataflowSolverActor`。
4.  通过蓝图调用 `AChaosDataflowSolverActor` 的 `Set Solver Active` 节点来启动或停止模拟。
5.  `AChaosDataflowSolverActor` 内部会通过其 `SimulationAsset` 属性（`FDataflowSimulationAsset`）引用一个 Dataflow 资产，该资产定义了具体的模拟逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosDataflowSolverActor.h"
#include "ChaosSolverBindingComponent.h"
```

### 基本用法

创建一个求解器 Actor 并注册一个物理组件。

```cpp
// 假设在某个 Actor 或 Component 的 BeginPlay 中
UWorld* World = GetWorld();
if (World)
{
    // 1. 生成求解器 Actor
    FActorSpawnParameters SpawnParams;
    AChaosDataflowSolverActor* SolverActor = World->SpawnActor<AChaosDataflowSolverActor>(AChaosDataflowSolverActor::StaticClass(), FTransform::Identity, SpawnParams);

    // 2. 获取需要绑定的物理组件 (例如，当前 Actor 的根组件)
    UPrimitiveComponent* PhysicsComponent = Cast<UPrimitiveComponent>(GetRootComponent());
    if (SolverActor && PhysicsComponent)
    {
        // 3. 将物理组件注册到求解器
        SolverActor->RegisterPhysicsComponent(PhysicsComponent);
        // 4. 激活求解器
        SolverActor->SetSolverActive(true);
    }
}
```
*来源：基于 `AChaosDataflowSolverActor` 的公共接口推断。*

### 进阶用法

通过 `UChaosSolverBindingComponent` 进行更自动化的绑定。该组件在 `BeginPlay` 时会自动查找或处理与 `SimulationActor` 的关联。

```cpp
// 在某个 Actor 的构造函数或初始化函数中
UChaosSolverBindingComponent* BindingComp = CreateDefaultSubobject<UChaosSolverBindingComponent>(TEXT("SolverBinding"));
BindingComp->SimulationActor = /* 指向场景中已存在的 AChaosDataflowSolverActor 的软引用 */;
BindingComp->bKeepKinematicInOriginal = true;
```
*来源：基于 `UChaosSolverBindingComponent` 的成员变量和 `BeginPlay` 逻辑推断。*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个使用 `ChaosDataflowSolver` 的 Actor。

**MyPhysicsActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPhysicsActor.generated.h"

class AChaosDataflowSolverActor;
class UPrimitiveComponent;

UCLASS()
class AMyPhysicsActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPhysicsActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UPrimitiveComponent* PhysicsMesh;

    UPROPERTY()
    AChaosDataflowSolverActor* SolverActor;
};
```

**MyPhysicsActor.cpp**
```cpp
#include "MyPhysicsActor.h"
#include "ChaosDataflowSolverActor.h"
#include "Components/StaticMeshComponent.h"

AMyPhysicsActor::AMyPhysicsActor()
{
    PrimaryActorTick.bCanEverTick = false;

    PhysicsMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PhysicsMesh"));
    RootComponent = PhysicsMesh;
    // 确保网格体有碰撞
    PhysicsMesh->SetSimulatePhysics(true);
}

void AMyPhysicsActor::BeginPlay()
{
    Super::BeginPlay();

    UWorld* World = GetWorld();
    if (World)
    {
        // 生成 Dataflow 求解器
        FActorSpawnParameters SpawnParams;
        SpawnParams.Owner = this;
        SolverActor = World->SpawnActor<AChaosDataflowSolverActor>(AChaosDataflowSolverActor::StaticClass(), GetActorTransform(), SpawnParams);

        if (SolverActor)
        {
            // 将本 Actor 的物理网格体注册到求解器
            SolverActor->RegisterPhysicsComponent(PhysicsMesh);
            // 激活求解器 (需要先为 SolverActor 配置有效的 SimulationAsset)
            // SolverActor->SetSolverActive(true);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigidPhysics` | 提供新的刚体物理 API (`FRigidBodyHandle`, `FRigidSceneHandle` 等)，是插件内部创建和管理物理体的核心。 |
| `Dataflow` | 提供 Dataflow 模拟接口 (`IDataflowPhysicsSolverInterface`, `FDataflowSimulationAsset`) 和模拟管理器。 |
| `Chaos` | Chaos 物理引擎的核心模块，提供调试绘制、形状创建等底层功能。 |

## 维护状态

### 近期更新

- 2026-04-09 f167027d 修复 ChaosDataFlowSolver 中的一个弃用警告。
- 2026-04-08 6d6dbc44 Chaos API：添加 PhysicsService 并移除异步插件对 dataflow 的依赖。
- 2026-03-04 3c8f6206 Chaos API：Shape Instance 第一部分。

### 维护评价

- **创建时间**：2026年2月，非常新的插件。
- **最近更新**：2026年4月仍有活跃提交，主要围绕 Chaos API 的演进和修复。
- **维护状态**：**活跃维护中**。作为实验性插件，它紧跟 Chaos 物理引擎和 Dataflow 系统的最新 API 变化。
- **已知限制**：插件标记为 `Experimental`，且默认未启用 (`Installed: false`)。API 和功能可能在未来版本中发生重大变化或移除。
- **推荐使用**：**仅推荐用于实验和原型开发**。不建议在需要稳定性的生产项目中使用。适合希望探索 Chaos 物理与 Dataflow 结合可能性的开发者。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosDataflowSolver)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosDataflowSolver/Tests) (如果存在)