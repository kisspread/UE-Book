# Cable Component

> A simulated cable component.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | CableComponent (Runtime, PreDefault) |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CableComponent) | |

## 用途

CableComponent 提供了一个基于 **Verlet 积分（Position-Based Dynamics）** 的绳索/线缆物理模拟组件。它将绳索离散为多个粒子（`FCableParticle`），通过约束求解器在每帧迭代中维持粒子间距离，从而实现绳索的悬垂、摆动和碰撞效果。

核心实现位于 `UCableComponent`（继承自 `UMeshComponent`），它同时负责：
- **物理模拟**：Verlet 积分 + 约束求解（可选子步进和刚度约束）
- **几何渲染**：将模拟结果生成圆柱形网格（可配置段数和侧面数）
- **端点附着**：支持将首尾端固定到任意 Actor/Component 的 Socket

## 使用场景

- **角色装饰**：头发丝带、披风飘带、武器挂绳等需要自然摆动效果的物件
- **环境道具**：悬挂在天花板的电缆、桥梁悬索、旗帜绳索
- **机械装置**：起重机吊缆、传送带连接线、电梯钢缆
- **交互物体**：可抓取的绳子、摆锤连线

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAttachEndToComponent` | 将线缆末端附着到指定 Component（可选 Socket） | `UCableComponent` |
| `SetAttachEndTo` | 将线缆末端附着到指定 Actor 的某个 Component 属性 | `UCableComponent` |
| `GetAttachedActor` | 获取线缆末端附着的 Actor | `UCableComponent` |
| `GetAttachedComponent` | 获取线缆末端附着的 Component | `UCableComponent` |
| `GetCableParticleLocations` | 获取线缆所有粒子的世界空间位置（用于碰撞检测或附加特效） | `UCableComponent` |

### 关键属性（BlueprintReadWrite）

| 属性 | 类别 | 说明 |
|---|---|---|
| `bAttachStart` | Cable | 是否将起点固定到组件变换位置 |
| `bAttachEnd` | Cable | 是否将终点固定到 AttachEndTo 或 EndLocation |
| `EndLocation` | Cable | 终点相对位置（未附着时使用） |
| `CableLength` | Cable | 线缆松弛长度 |
| `SolverIterations` | Cable | 约束求解迭代次数（越大越硬，范围 1-16） |
| `CableWidth` | Cable Rendering | 线缆几何宽度 |
| `NumSides` | Cable Rendering | 线缆截面侧面数 |
| `TileMaterial` | Cable Rendering | 材质沿长度方向重复次数 |
| `CableForce` | Cable Forces | 施加在所有粒子上的世界空间力向量 |
| `CableGravityScale` | Cable Forces | 重力缩放系数 |
| `bEnableCollision` | Advanced | 实验性：启用世界碰撞（性能开销大） |
| `CollisionFriction` | Advanced | 碰撞时的滑动摩擦系数（0-1） |
| `bEnableStiffness` | Advanced | 启用刚度约束 |
| `bUseSubstepping` | Advanced | 启用子步进模拟 |
| `TeleportDistanceThreshold` | Teleport | 瞬移检测距离阈值 |
| `TeleportRotationThreshold` | Teleport | 瞬移检测旋转阈值 |
| `bResetAfterTeleport` | Teleport | 瞬移后重置粒子位置和速度 |
| `bTeleportAfterReattach` | Teleport | 重新附着后执行瞬移校正 |

### 使用示例（蓝图描述）

**快速创建线缆**：
1. 在场景中放置 `ACableActor`（它自带一个 `UCableComponent`）
2. 在 Details 面板中调整 `CableLength`、`CableWidth`、`NumSegments` 等参数
3. 勾选 `bAttachStart` 将起点固定

**动态附着末端**：
1. 获取目标 Actor 的某个 Component 引用
2. 调用 `SetAttachEndToComponent(TargetComponent)` 将线缆末端附着到目标
3. 设置 `bAttachEnd = true` 激活末端附着

**读取粒子位置用于特效**：
1. 调用 `GetCableParticleLocations` 获取位置数组
2. 在每个位置生成粒子特效或 Niagara emitter

## C++ 用法

### 头文件引入

```cpp
#include "CableComponent.h"
#include "CableActor.h"
```

### 基本用法

```cpp
// 在 Actor 中创建并配置 CableComponent
void AMyActor::SetupCable()
{
    CableComp = CreateDefaultSubobject<UCableComponent>(TEXT("Cable"));
    CableComp->SetupAttachment(RootComponent);

    // 基本参数
    CableComp->CableLength = 200.0f;
    CableComp->NumSegments = 10;
    CableComp->CableWidth = 2.0f;
    CableComp->NumSides = 4;

    // 附着设置
    CableComp->bAttachStart = true;   // 起点固定到组件位置
    CableComp->bAttachEnd = false;    // 终点自由摆动

    // 物理参数
    CableComp->CableGravityScale = 1.0f;
    CableComp->SolverIterations = 4;
    CableComp->bEnableStiffness = false;

    // 渲染
    CableComp->SetMaterial(0, MyCableMaterial);
    CableComp->TileMaterial = 1.0f;
}
```

### 进阶用法

```cpp
// 动态附着线缆末端到另一个 Actor 的组件
void AMyActor::AttachCableEnd(AActor* TargetActor)
{
    if (TargetActor && CableComp)
    {
        // 附着到目标 Actor 的根组件
        CableComp->SetAttachEndToComponent(TargetActor->GetRootComponent());
        CableComp->bAttachEnd = true;
    }
}

// 读取线缆粒子位置，在每个节点生成音效
void AMyActor::SpawnEffectsAlongCable()
{
    TArray<FVector> Locations;
    CableComp->GetCableParticleLocations(Locations);

    for (const FVector& Loc : Locations)
    {
        // 例如在每个粒子位置生成轨迹粒子
        UNiagaraFunctionLibrary::SpawnSystemAtLocation(
            GetWorld(), TrailSystem, Loc);
    }
}

// 启用实验性碰撞（注意性能影响）
void AMyActor::EnableCableCollision()
{
    CableComp->bEnableCollision = true;
    CableComp->CollisionFriction = 0.3f;
}
```

## Demo 示例

一个完整的最小可运行示例：在头顶挂一根会摆动的线缆。

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "CableComponent"  // 添加此依赖
});
```

### SwingingCable.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SwingingCable.generated.h"

class UCableComponent;

UCLASS()
class ASwingingCable : public AActor
{
    GENERATED_BODY()

public:
    ASwingingCable();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UCableComponent> Cable;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cable")
    float DefaultLength = 150.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cable")
    FVector WindForce = FVector(50.0f, 0.0f, 0.0f);
};
```

### SwingingCable.cpp

```cpp
#include "SwingingCable.h"
#include "CableComponent.h"

ASwingingCable::ASwingingCable()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建根组件
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));

    // 创建线缆
    Cable = CreateDefaultSubobject<UCableComponent>(TEXT("Cable"));
    Cable->SetupAttachment(RootComponent);

    // 配置线缆
    Cable->CableLength = DefaultLength;
    Cable->NumSegments = 8;
    Cable->CableWidth = 1.5f;
    Cable->NumSides = 4;
    Cable->SolverIterations = 6;
    Cable->bAttachStart = true;
    Cable->bAttachEnd = false;
    Cable->EndLocation = FVector(0.0f, 0.0f, -DefaultLength);

    // 力和重力
    Cable->CableForce = WindForce;
    Cable->CableGravityScale = 1.0f;

    // 渲染优化
    Cable->bSkipCableUpdateWhenNotVisible = true;
    Cable->bSkipCableUpdateWhenNotOwnerRecentlyRendered = true;
}
```

### 使用方式

1. 将 `ASwingingCable` 拖入场景
2. 在 Details 面板调整 `DefaultLength`、`WindForce`
3. 如需末端附着，在 BeginPlay 中调用 `Cable->SetAttachEndToComponent()`
4. Play 后线缆会自然下垂并在风力作用下摆动

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、Component 等） |
| `RenderCore` | 渲染核心（SceneProxy 等） |
| `RHI` | 渲染硬件接口 |

使用者只需在 Build.cs 中添加 `CableComponent` 模块依赖即可，以上依赖会自动传递。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-26 | `ce867df` | [HWRT] Refactored FRayTracingInstanceCollector to handle multiple views instead of a single reference view. | **硬件光线追踪适配**：重构了光线追踪实例收集器以支持多视图，CableComponent 的 RT 几何体生成代码随之更新。属于底层渲染架构重构，非功能性变更。 |
| 2025-08-15 | `35304c1` | [HWRT] Re-create evicted cable component RT geometry so it becomes resident. | **光线追踪 Bug 修复**：修复了 CableComponent 的光线追踪几何体被驱逐后无法重新创建的问题。这是一个实际的 bug fix。 |
| 2025-06-18 | `08316db` | Cache the ShaderPlatform inside MaterialResource, derive the FeatureLevel from that ShaderPlatform. | **渲染管线优化**：材质资源中缓存 ShaderPlatform 的全局重构，CableComponent 的材质系统随之适配。 |

### 维护评价

- **年龄**：创建于 2014 年 3 月，已存在约 **12 年**，属于 🏛️ **文物级** 组件
- **最近更新**：2025 年 8 月，距今约 8 个月，有实质性更新
- **更新模式**：近期 3 次更新全部来自 **HWRT（硬件光线追踪）** 基础设施重构，说明 CableComponent 作为渲染组件被纳入了引擎级的光线追踪支持体系，但插件本身的功能（物理模拟、约束求解）并未有任何改动
- **稳定性**：作为 Epic 官方示例插件，代码极为精简（约 600 行核心代码），结构稳定，几乎不会出问题
- **限制**：
  - 碰撞检测（`bEnableCollision`）仍标记为 **EXPERIMENTAL**，12 年来一直未"毕业"
  - 仅支持简单的圆柱形几何，不支持自定义横截面
  - 没有自带的测试用例（Test Case）
- **推荐度**：⭐⭐⭐⭐ **推荐使用**。对于简单线缆需求，它是零依赖、零配置的即用方案。如果需要更复杂的绳索模拟（多绳交互、断裂、可变截面），应考虑第三方方案或自研。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CableComponent)
- [CableComponent.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/CableComponent/Source/CableComponent/Classes/CableComponent.h)
- [CableActor.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/CableComponent/Source/CableComponent/Classes/CableActor.h)
