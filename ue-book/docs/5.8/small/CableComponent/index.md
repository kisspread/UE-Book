# Cable Component

> A simulated cable component.

| 属性 | 值 |
|---|---|
| 中文名 | 绳索组件 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CableComponent` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CableComponent) | |

## 用途

CableComponent 是一个用于模拟绳索、电缆、锁链等柔性物理物体的组件。它基于质点-弹簧模型（Verlet积分），可以实时模拟绳索的物理运动，包括重力、碰撞（实验性）和附加端点。它解决的核心问题是：在不依赖复杂物理骨骼和布料系统的情况下，快速实现高性能的悬垂、摆动的绳索视觉效果。

## 使用场景

- 你需要在游戏中添加可交互的悬挂电缆（如地铁车厢连接处、工业场景中的电线）。
- 你需要角色身上悬挂的装饰性绳索或锁链，并希望它们能随角色移动而自然摆动。
- 你需要实现一个简单的、性能要求不高的布娃娃系统的一部分，用于模拟角色身上的绳索或线缆。

## 蓝图用法

### 核心节点

从 `UCableComponent` 的 `UFUNCTION(BlueprintCallable)` 和 `UPROPERTY(BlueprintReadWrite)` 中提取。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAttachEndToComponent` | 将绳索的末端附加到指定的场景组件（可选择Socket） | `UCableComponent` |
| `SetAttachEndTo` | 将绳索的末端附加到指定Actor的某个组件属性上 | `UCableComponent` |
| `GetAttachedActor` | 获取绳索末端当前附加的Actor | `UCableComponent` |
| `GetAttachedComponent` | 获取绳索末端当前附加的组件 | `UCableComponent` |
| `GetCableParticleLocations` | 获取组成绳索的所有粒子点的世界坐标（用于调试或特效） | `UCableComponent` |
| `bAttachStart` | 属性：是否将绳索起点固定在组件原点 | `UCableComponent` |
| `bAttachEnd` | 属性：是否将绳索末端固定 | `UCableComponent` |
| `CableLength` | 属性：绳索的静止长度 | `UCableComponent` |
| `CableGravityScale` | 属性：世界重力对绳索影响的缩放 | `UCableComponent` |
| `bEnableCollision` | 属性：是否启用碰撞（实验性，性能开销大） | `UCableComponent` |

### 使用示例（蓝图描述）

1.  **基本创建**：在场景中放置一个 `ACableActor`，或者在任何Actor上添加 `UCableComponent`。
2.  **配置物理**：在细节面板（Details）中调整 `CableLength`（长度）、`NumSegments`（细分段数，越多越平滑）、`CableGravityScale`（重力）、`SolverIterations`（刚度）。
3.  **固定端点**：
    *   如果希望绳索起点固定，勾选 `bAttachStart`。
    *   如果希望绳索末端固定，勾选 `bAttachEnd`。然后，在 `AttachEndTo` 属性中指定目标Actor或组件，或在蓝图中调用 `SetAttachEndToComponent` 函数动态连接。
4.  **调整外观**：调整 `CableWidth`（宽度）、`NumSides`（截面边数）、`TileMaterial`（材质平铺）和应用材质。
5.  **施加外力**：通过设置 `CableForce` 属性为绳索施加一个世界空间方向的恒定力（如风力）。

## C++ 用法

### 头文件引入

```cpp
#include "CableComponent.h"
```

### 基本用法

以下示例展示如何在C++中创建并配置一个 `UCableComponent`。

```cpp
// 在某个Actor的头文件中（例如 AMyActor.h）
UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
TObjectPtr<UCableComponent> CableComp;

// 在该Actor的构造函数中（例如 AMyActor::AMyActor()）
CableComp = CreateDefaultSubobject<UCableComponent>(TEXT("Cable"));
CableComp->SetupAttachment(RootComponent);

// 配置基本属性
CableComp->CableLength = 500.0f;
CableComp->NumSegments = 10;
CableComp->CableWidth = 2.0f;
CableComp->CableGravityScale = 1.0f;
CableComp->bAttachStart = true; // 固定在组件原点
```

### 进阶用法

动态改变绳索末端附着点。

```cpp
// 在BeginPlay或其它函数中，动态附加绳索末端到另一个Actor的组件上
if (AnotherActor)
{
    USceneComponent* TargetComponent = AnotherActor->GetRootComponent();
    CableComp->SetAttachEndToComponent(TargetComponent, TEXT("SocketName"));
}

// 或者，通过属性直接引用
CableComp->AttachEndTo.SetOtherActor(AnotherActor);
CableComp->AttachEndTo.ComponentProperty = TEXT("TargetComponentName");
CableComp->AttachEndToSocketName = TEXT("SocketName");
```

## Demo 示例

一个最小、可编译的示例，展示如何在C++中创建一个带绳索组件的Actor。

**MyCableActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCableActor.generated.h"

class UCableComponent;

UCLASS()
class AMyCableActor : public AActor
{
    GENERATED_BODY()
    
public:    
    AMyCableActor();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Cable")
    TObjectPtr<UCableComponent> CableComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cable")
    AActor* AttachEndToActor;
};
```

**MyCableActor.cpp**
```cpp
#include "MyCableActor.h"
#include "CableComponent.h"
#include "Components/SceneComponent.h"

AMyCableActor::AMyCableActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建根组件
    USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    // 创建绳索组件
    CableComponent = CreateDefaultSubobject<UCableComponent>(TEXT("Cable"));
    CableComponent->SetupAttachment(Root);

    // 基础配置
    CableComponent->CableLength = 300.0f;
    CableComponent->NumSegments = 8;
    CableComponent->CableWidth = 1.5f;
    CableComponent->NumSides = 4; // 方形截面，性能更好
    CableComponent->bAttachStart = true; // 起点固定在此Actor位置
    CableComponent->bAttachEnd = false;  // 末端初始不固定，之后代码设置
    CableComponent->EndLocation = FVector(0.0f, 0.0f, -200.0f); // 初始末端位置
}

// 你可以在BeginPlay中，根据AttachEndToActor的值动态附加末端
// void AMyCableActor::BeginPlay()
// {
//     Super::BeginPlay();
//     if (AttachEndToActor)
//     {
//         CableComponent->SetAttachEndTo(AttachEndToActor, NAME_None, NAME_None);
//     }
// }
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的模块 `CableComponent` 是一个运行时模块，依赖关系较为基础。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 为硬件光线追踪添加 MeshBatchesView 参数，统一网格批次所有权管理。 |
| 2026-04-03 | `cbc9f983` | [HWRT] Refactored management of StaticRayTracingGeometry in FCableSceneProxy. | 重构了绳索场景代理中静态光线追踪几何体的管理。 |
| 2026-02-06 | `af701dad` | [HWRT] Deprecate public FRayTracingGeometry Initializer. | 废弃了公开的 FRayTracingGeometry 初始化器。 |
| 2025-11-10 | `cac25bc4` | PSO Precaching miss fixes: | 修复了 PSO 预缓存未命中的问题。 |
| 2025-08-26 | `ce867df3` | [HWRT] Refactored FRayTracingInstanceCollector to handle multiple views instead of a single referenc | 重构了光线追踪实例收集器以支持多视图，而非单一引用。 |

### 维护评价

CableComponent 是一个创建于 2014 年的**文物级**插件。虽然创建时间很早，但从近期的提交记录（截至 2026 年 5 月）来看，它**仍在活跃维护**。近期的更新主要集中在与现代渲染技术（硬件光线追踪 HWRT）的兼容性重构和性能优化上，这表明 Epic 仍在持续将其适配到新的渲染后端。

**推荐使用**：对于需要简单、高性能绳索模拟的项目，CableComponent 仍然是一个可靠且经过长期验证的选择。它的 API 稳定，蓝图支持良好。需要注意的是，其碰撞功能（`bEnableCollision`）被标记为实验性，且性能开销较大，在生产环境中应谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CableComponent)
- 官方文档：无
- 测试用例：无（未在插件目录内发现标准测试文件）