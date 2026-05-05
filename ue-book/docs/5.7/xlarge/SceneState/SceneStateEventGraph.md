# Motion Design Scene State

> （Description 为空，基于源码分析）为虚拟制作（Virtual Production）和 Motion Design 工作流提供场景状态管理框架。它通过状态机、事件系统和数据绑定，实现对复杂场景中对象状态、动画和交互逻辑的集中控制与驱动。

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Scene State 插件旨在解决虚拟制作和 Motion Design 项目中场景状态管理的复杂性。它提供了一个结构化的框架，用于定义、驱动和同步场景中各个元素的状态。核心思想是将场景视为一个由多个状态组成的系统，通过状态机来管理状态之间的转换，并通过事件和数据绑定来响应外部输入（如用户交互、时间轴、其他系统信号）和驱动场景变化（如动画播放、材质切换、物体显隐）。这避免了在蓝图或代码中编写大量零散、难以维护的状态管理逻辑。

## 使用场景

-   **虚拟制作 (Virtual Production)**：在 LED 墙或绿幕拍摄中，管理虚拟场景的灯光、天气、时间（昼夜循环）等环境状态，并根据拍摄脚本或导演指令进行平滑切换。
-   **Motion Design**：创建复杂的动态图形动画序列，其中多个元素的动画、颜色、形状需要根据时间轴或交互事件进行精确的同步和状态转换。
-   **交互式体验**：构建博物馆展品、主题公园游乐设施或产品展示中的交互式场景，根据用户的输入（如按钮、传感器）触发不同的场景状态和反馈。
-   **游戏内过场动画与事件**：管理游戏中的过场动画序列、环境叙事事件或复杂的机关谜题，这些通常涉及多个对象的状态联动。

## 蓝图用法

> 注：由于未提供具体头文件，以下节点基于模块名称和常见 UE5 状态机/事件模式推断。实际节点请参考引擎内蓝图上下文菜单。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Scene State Machine` | 创建并初始化一个场景状态机实例。 | `USceneStateMachineComponent` 或类似 |
| `Set State` | 强制状态机切换到指定的状态。 | `USceneStateMachineComponent` |
| `Trigger Event` | 向状态机或事件系统发送一个自定义事件，可能触发状态转换。 | `USceneStateEventSubsystem` 或类似 |
| `Bind Property to State` | 将一个对象的属性（如可见性、材质参数）绑定到状态机的某个状态或数据值。 | `USceneStateBindingComponent` |
| `Get Current State` | 获取状态机当前所处的状态。 | `USceneStateMachineComponent` |

### 使用示例（蓝图描述）

1.  **创建状态机**：在场景中的某个 Actor（如 `SceneStateManager`）上添加 `SceneStateMachineComponent`。在蓝图的 `BeginPlay` 事件中，调用 `Create Scene State Machine` 节点进行初始化。
2.  **定义状态与转换**：在状态机编辑器（可能是自定义的图表编辑器）中，创建“白天”、“夜晚”、“黄昏”等状态节点。在状态节点之间绘制转换线，并设置转换条件（如接收到 `TimeOfDayChanged` 事件，或某个数据值大于阈值）。
3.  **绑定场景对象**：选中场景中的灯光 Actor，在其蓝图中添加 `SceneStateBindingComponent`。将该组件的某个属性（如灯光的强度或颜色）绑定到状态机中“夜晚”状态对应的输出数据上。
4.  **触发事件**：在游戏逻辑或 Sequencer 时间轴中，当需要切换时间时，调用 `Trigger Event` 节点发送 `TimeOfDayChanged` 事件。状态机接收到事件后，根据当前状态和转换规则，自动切换到新状态，并驱动所有绑定的场景对象更新。

## C++ 用法

> 注：以下示例基于模块结构和 UE5 常见模式推断，具体 API 请参考引擎源码。

### 头文件引入

```cpp
// 核心状态机功能
#include "SceneState.h"
// 事件系统
#include "SceneStateEvent.h"
// 数据绑定
#include "SceneStateBinding.h"
```

### 基本用法

```cpp
// 假设在一个 Actor 的组件中管理状态机
#include "Components/SceneStateMachineComponent.h" // 假设的组件头文件

void AMySceneActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取或创建状态机组件
    if (USceneStateMachineComponent* StateMachine = FindComponentByClass<USceneStateMachineComponent>())
    {
        // 初始化状态机，可能需要传入一个状态机资产（USceneStateMachineAsset）
        StateMachine->InitializeStateMachine(MyStateMachineAsset);

        // 监听状态变化
        StateMachine->OnStateChanged.AddDynamic(this, &AMySceneActor::HandleStateChanged);
    }
}

void AMySceneActor::HandleStateChanged(FName OldState, FName NewState)
{
    UE_LOG(LogTemp, Log, TEXT("State changed from %s to %s"), *OldState.ToString(), *NewState.ToString());
    // 在此处执行状态切换后的逻辑
}
```

### 进阶用法

```cpp
// 结合事件系统和数据绑定
#include "SceneStateEventSubsystem.h"
#include "SceneStateBindingComponent.h"

void AMyInteractiveActor::SetupBindings()
{
    // 假设有一个绑定组件
    if (USceneStateBindingComponent* BindingComp = FindComponentByClass<USceneStateBindingComponent>())
    {
        // 将本Actor的某个属性（如bIsVisible）绑定到状态机数据“ObjectVisibility”
        BindingComp->BindBoolPropertyToData(
            GET_MEMBER_NAME_CHECKED(AMyInteractiveActor, bIsVisible),
            FName("ObjectVisibility")
        );
    }

    // 注册一个自定义事件处理器
    if (USceneStateEventSubsystem* EventSub = GetWorld()->GetSubsystem<USceneStateEventSubsystem>())
    {
        EventSub->RegisterEventHandler(
            FName("PlayerInteract"),
            FSceneStateEventHandler::CreateUObject(this, &AMyInteractiveActor::OnPlayerInteract)
        );
    }
}

void AMyInteractiveActor::OnPlayerInteract(const FSceneStateEventContext& Context)
{
    // 处理玩家交互事件，可能触发状态机转换或直接修改数据
    UE_LOG(LogTemp, Log, TEXT("Player interacted!"));
}
```

## Demo 示例

> 由于插件结构复杂且为实验性，此处提供一个概念性的最小示例框架。

**SceneStateDemoActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "SceneStateDemoActor.generated.h"

class USceneStateMachineComponent;
class USceneStateBindingComponent;

UCLASS()
class ASceneStateDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ASceneStateDemoActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Scene State")
    TObjectPtr<USceneStateMachineComponent> StateMachineComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Scene State")
    TObjectPtr<USceneStateBindingComponent> BindingComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Scene State")
    bool bCurrentVisibility = true;

    UFUNCTION()
    void OnStateTransition(FName OldState, FName NewState);
};
```

**SceneStateDemoActor.cpp**
```cpp
#include "SceneStateDemoActor.h"
// 假设的头文件路径
#include "Components/SceneStateMachineComponent.h"
#include "Components/SceneStateBindingComponent.h"

ASceneStateDemoActor::ASceneStateDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    StateMachineComponent = CreateDefaultSubobject<USceneStateMachineComponent>(TEXT("StateMachine"));
    BindingComponent = CreateDefaultSubobject<USceneStateBindingComponent>(TEXT("Binding"));
}

void ASceneStateDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 初始化状态机 (需要资产)
    // StateMachineComponent->InitializeStateMachine(MyAsset);

    // 2. 设置绑定：将 bCurrentVisibility 绑定到状态机数据
    if (BindingComponent)
    {
        BindingComponent->BindBoolPropertyToData(
            GET_MEMBER_NAME_CHECKED(ASceneStateDemoActor, bCurrentVisibility),
            FName("ActorVisibility")
        );
    }

    // 3. 监听状态变化
    if (StateMachineComponent)
    {
        StateMachineComponent->OnStateChanged.AddDynamic(this, &ASceneStateDemoActor::OnStateTransition);
    }
}

void ASceneStateDemoActor::OnStateTransition(FName OldState, FName NewState)
{
    // 状态切换时，绑定的属性 bCurrentVisibility 会根据新状态的数据自动更新
    // 例如，新状态“Hidden”可能将“ActorVisibility”数据设为 false，从而驱动 bCurrentVisibility 变为 false
    SetActorHiddenInGame(!bCurrentVisibility);
}
```

## 模块依赖

> 注：以下依赖基于模块名称和常见虚拟制作插件模式推断。实际依赖请查看各模块的 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `MovieScene` | 用于与 Sequencer 时间轴集成，驱动基于时间的状态变化。 |
| `LevelSequence` | 同上，用于处理关卡序列。 |
| `ControlRig` | 可能用于驱动基于状态的动画或程序化控制。 |
| `Niagara` | 可能用于根据状态触发或修改粒子效果。 |
| `EnhancedInput` | 可能用于将玩家输入映射为状态机事件。 |
| `GameplayAbilities` | 可能用于与 Gameplay Ability System 集成，管理技能相关状态。 |

## 维护状态

### 近期更新

```
- 2025-04-22 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

### 维护评价

-   **创建时间**：插件非常新，创建于 2025 年 4 月。
-   **近期更新**：最近一次提交是将其从 `Experimental` 目录移动到 `VirtualProduction` 目录。这通常意味着插件功能已达到一个相对稳定的里程碑，准备在更专业的领域（虚拟制作）进行推广和使用，但**仍标记为 `IsBetaVersion=true`**。
-   **活跃度**：基于单次提交记录，无法判断长期维护频率。但作为 Epic 官方维护的、与 Motion Design 和 Virtual Production 战略相关的插件，预计会有持续的更新和支持。
-   **已知限制**：作为 Beta 版本，API 和功能可能发生变化。文档和示例可能不完善。
-   **推荐使用**：**谨慎推荐**。如果你正在从事专业的虚拟制作或 Motion Design 项目，并且愿意承担 Beta 版本的风险（如 API 变动、潜在 Bug），可以尝试使用。对于生产环境，建议密切关注其更新日志，并做好应对变化的准备。对于学习或原型开发，这是一个了解现代场景状态管理框架的好例子。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现公开测试用例路径）