# Motion Design Camera

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheCamera` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheCamera) | |

## 用途

`AvalancheCamera` 模块是 Motion Design (Avalanche) 插件中负责**场景相机管理**的核心子模块。它解决的主要问题是：在虚拟制作（Virtual Production）和广播场景中，需要对多个场景（Scenes）的相机进行优先级排序和混合过渡控制。

该模块提供了一套系统，允许为场景中的 Actor 设置相机优先级，并定义切换到该相机时的过渡参数（如混合时间、混合函数）。通过 `UAvaCameraSubsystem`，系统能够根据场景的注册状态和优先级，自动决定哪个相机（View Target）应该成为当前玩家的视图目标，并执行平滑的混合过渡。这使得在 Motion Design 的复杂场景中，相机的切换和过渡可以自动化、程序化地管理，而无需手动在蓝图或 Sequencer 中设置每一个过渡。

## 使用场景

- **虚拟制作广播**：在直播或录制的虚拟制作场景中，需要根据节目流程（如 State Tree 状态切换）自动切换不同场景的相机视角。
- **多场景管理**：当一个关卡中包含多个独立的 Motion Design 场景（由 `ULevel` 表示）时，需要根据场景的激活状态和优先级来决定最终的相机输出。
- **平滑相机过渡**：需要在不同相机视角之间实现平滑、可控的混合效果，例如淡入淡出、线性插值等。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` | 获取当前世界对应的 `UAvaCameraSubsystem` 实例。 | `UAvaCameraSubsystem` |
| `RegisterScene` | 向子系统注册一个场景（关卡），使其相机参与优先级计算。 | `UAvaCameraSubsystem` |
| `UnregisterScene` | 从子系统注销一个场景。 | `UAvaCameraSubsystem` |
| `ConditionallyUpdateViewTarget` | 根据当前已注册场景的相机优先级，条件性地更新玩家的视图目标。 | `UAvaCameraSubsystem` |
| `Priority` | 获取或设置相机优先级修改器的优先级值。 | `UAvaCameraPriorityModifier` |
| `TransitionParams` | 获取或设置相机优先级修改器的过渡参数。 | `UAvaCameraPriorityModifier` |

### 使用示例（蓝图描述）

1.  **为 Actor 添加相机优先级**：
    - 在场景中的相机 Actor（或任何 Actor）上，添加 `UAvaCameraPriorityModifier` 组件。
    - 在细节面板中设置 `Priority`（数值越大优先级越高）和 `TransitionParams`（如混合时间）。

2.  **管理场景相机**：
    - 在场景初始化时（例如 `BeginPlay`），调用 `UAvaCameraSubsystem::Get` 获取子系统。
    - 调用 `RegisterScene` 并传入当前场景的 `ULevel` 对象，将该场景的相机注册到系统中。
    - 当场景结束或需要移除时，调用 `UnregisterScene`。

3.  **触发相机更新**：
    - 在需要评估和切换相机的时机（例如 State Tree 状态变化后），调用 `ConditionallyUpdateViewTarget`。系统会自动选择优先级最高的相机并执行混合过渡。

## C++ 用法

### 头文件引入

```cpp
#include "AvaCameraSubsystem.h"
#include "AvaCameraPriorityModifier.h"
```

### 基本用法

**获取并使用相机子系统** (来源: `AvaCameraSubsystem.h`)

```cpp
// 在需要管理相机的代码中（例如一个自定义的场景管理器）
void AMySceneManager::ActivateScene()
{
    // 1. 获取相机子系统
    UAvaCameraSubsystem* CameraSubsystem = UAvaCameraSubsystem::Get(this);
    if (!CameraSubsystem)
    {
        return;
    }

    // 2. 注册当前场景（假设 MyLevel 是当前场景的 ULevel*）
    CameraSubsystem->RegisterScene(MyLevel);

    // 3. 请求更新视图目标（可选，通常由状态变化触发）
    CameraSubsystem->ConditionallyUpdateViewTarget(MyLevel);
}

void AMySceneManager::DeactivateScene()
{
    UAvaCameraSubsystem* CameraSubsystem = UAvaCameraSubsystem::Get(this);
    if (CameraSubsystem)
    {
        // 注销场景
        CameraSubsystem->UnregisterScene(MyLevel);
    }
}
```

**配置相机优先级修改器** (来源: `AvaCameraPriorityModifier.h`)

```cpp
// 假设你有一个 AActor* TargetActor
void SetupCameraPriority(AActor* TargetActor, int32 NewPriority, const FViewTargetTransitionParams& NewParams)
{
    // 查找或创建修改器组件
    UAvaCameraPriorityModifier* Modifier = TargetActor->FindComponentByClass<UAvaCameraPriorityModifier>();
    if (!Modifier)
    {
        Modifier = NewObject<UAvaCameraPriorityModifier>(TargetActor);
        Modifier->RegisterComponent();
    }

    // 设置属性（注意：这些是 EditInstanceOnly，通常在编辑器设置，但运行时也可通过代码修改）
    // 注意：直接修改 UPROPERTY 需要确保对象是可编辑的，或者使用 Setter 函数（如果提供）。
    // 这里仅为演示，实际使用中可能需要通过其他方式（如蓝图接口）来安全地修改。
    // Modifier->Priority = NewPriority;
    // Modifier->TransitionParams = NewParams;
}
```

### 进阶用法

结合 `FAvaCameraBlendTask` (State Tree Task) 实现状态驱动的相机混合。

```cpp
// 在 State Tree 的 Task 中，你可以链接到相机子系统并执行混合
// 以下为概念性代码，展示了 FAvaCameraBlendTask 如何与子系统交互
EStateTreeRunStatus FAvaCameraBlendTask::EnterState(FStateTreeExecutionContext& InContext, const FStateTreeTransitionResult& InTransition) const
{
    // 从上下文中获取相机子系统句柄
    UAvaCameraSubsystem* CameraSubsystem = InContext.GetExternalData(CameraSubsystemHandle);
    if (!CameraSubsystem)
    {
        return EStateTreeRunStatus::Failed;
    }

    // 获取实例数据（包含是否覆盖过渡参数等设置）
    const FAvaCameraBlendInstanceData& InstanceData = InContext.GetInstanceData(*this);

    // 触发视图目标更新，可能使用覆盖的过渡参数
    const FViewTargetTransitionParams* OverrideParams = InstanceData.bOverrideTransitionParams ? &InstanceData.TransitionParams : nullptr;
    CameraSubsystem->UpdatePlayerControllerViewTarget(OverrideParams);

    return EStateTreeRunStatus::Succeeded;
}
```

## Demo 示例

一个最小的示例，展示如何创建一个带有相机优先级修改器的 Actor，并在运行时通过子系统管理它。

**MyCameraActor.h**
```cpp
#pragma once

#include "GameFramework/Actor.h"
#include "MyCameraActor.generated.h"

class UCameraComponent;
class UAvaCameraPriorityModifier;

UCLASS()
class AMyCameraActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCameraActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
    TObjectPtr<UCameraComponent> CameraComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
    TObjectPtr<UAvaCameraPriorityModifier> PriorityModifier;
};
```

**MyCameraActor.cpp**
```cpp
#include "MyCameraActor.h"
#include "Camera/CameraComponent.h"
#include "AvaCameraPriorityModifier.h"
#include "AvaCameraSubsystem.h"

AMyCameraActor::AMyCameraActor()
{
    PrimaryActorTick.bCanEverTick = false;

    CameraComponent = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    RootComponent = CameraComponent;

    // 创建并附加相机优先级修改器
    PriorityModifier = CreateDefaultSubobject<UAvaCameraPriorityModifier>(TEXT("CameraPriority"));
    // 修改器会自动附加到根组件
}

void AMyCameraActor::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时，将此 Actor 所在的场景注册到相机子系统
    // 注意：在实际的 Motion Design 流程中，场景注册通常由更高级的系统（如场景管理器）处理
    if (ULevel* Level = GetLevel())
    {
        if (UAvaCameraSubsystem* Subsystem = UAvaCameraSubsystem::Get(this))
        {
            Subsystem->RegisterScene(Level);
        }
    }
}
```

## 模块依赖

从模块名称和功能推断，`AvalancheCamera` 模块依赖于 Motion Design 的核心框架和过渡系统。

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | Motion Design 的核心基础模块。 |
| `AvalancheTransition` | 提供状态树过渡任务（`FAvaTransitionTask`）的基类，`FAvaCameraBlendTask` 依赖于此。 |
| `Sequencer` | 用于与电影序列系统集成，可能用于更复杂的相机动画编排。 |

## 维护状态

### 近期更新

```
- 2024-01-30 5e98ccb853ee Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

### 维护评价

- **创建时间**：该模块随 Motion Design 插件于 2024 年 1 月底创建，历史较短。
- **最近更新**：最近一次提交是 2024 年 1 月 30 日，主要是将整个插件从 `Experimental` 目录迁移到 `VirtualProduction` 目录，标志着其正式成为虚拟制作工具链的一部分。此后暂无新的功能性提交记录。
- **维护状态**：**维护中**。作为 Motion Design 插件的核心组件之一，它处于 Epic Games 的维护范围内。虽然近期没有独立的功能更新，但其稳定性依赖于整个 Motion Design 插件的持续开发。
- **已知限制**：该模块高度依赖于 Motion Design 的整体架构（如场景、状态树），单独使用场景有限。
- **推荐使用**：**推荐**。如果你正在使用 UE5 的 Motion Design (Avalanche) 插件进行虚拟制作或广播项目，并且需要程序化、自动化的相机管理功能，那么这个模块是官方提供的标准解决方案，应优先使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheCamera)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/motion-design-in-unreal-engine/) (Motion Design 整体文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche/Tests) (位于插件根目录的 Tests 文件夹)