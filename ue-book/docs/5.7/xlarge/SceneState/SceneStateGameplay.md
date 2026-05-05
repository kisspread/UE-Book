# Motion Design Scene State

> （Description 为空）

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、状态机资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Motion Design Scene State 是一个用于虚拟制作（Virtual Production）场景的状态管理系统。它提供了一个基于状态机（State Machine）的框架，用于定义、管理和驱动场景中各种元素（如灯光、几何体、材质、动画等）的状态和过渡。该插件旨在为 Motion Design 工作流提供一种结构化的方式来控制复杂的场景状态序列，例如在虚拟制片中切换不同的场景布局、灯光预设或动画阶段。它通过蓝图资产和编辑器工具，让设计师和艺术家能够直观地构建和调试场景状态逻辑，而无需编写大量 C++ 代码。

## 使用场景

- 你在进行虚拟制片（Virtual Production），需要管理一个包含多个灯光、道具和摄像机预设的复杂场景，并希望在它们之间平滑过渡。
- 你需要为 Motion Design 项目创建一系列可重复、可编辑的场景状态（如“开场”、“特写”、“全景”），并控制它们之间的触发和切换逻辑。
- 你希望将场景状态的管理与游戏逻辑解耦，使其更专注于视觉呈现和流程控制。
- 你需要一个可视化的状态机编辑器来设计和调试场景状态之间的复杂过渡条件。

## 蓝图用法

该插件的核心蓝图接口主要通过 `ASceneStateActor` 和 `USceneStateComponent` 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Scene State` | 获取此 Actor 或 Component 当前关联的 `USceneStateObject` 实例。 | `ASceneStateActor`, `USceneStateComponent` |
| `Set Scene State Class` | 设置此 Actor 或 Component 应使用的 `USceneStateObject` 的类。 | `ASceneStateActor`, `USceneStateComponent` |
| `Get Scene State Class` | 获取此 Actor 或 Component 当前设置的 `USceneStateObject` 类。 | `ASceneStateActor`, `USceneStateComponent` |

### 使用示例（蓝图描述）

1.  **创建场景状态 Actor**：在场景中放置一个 `ASceneStateActor`。在它的细节面板中，你可以通过 `Set Scene State Class` 节点或直接在属性中指定一个自定义的 `USceneStateObject` 子类。
2.  **获取状态对象**：在其他蓝图中，你可以通过 `Get Actor of Class` 节点找到场景中的 `ASceneStateActor`，然后调用 `Get Scene State` 来获取其状态对象实例，进而调用状态对象上的自定义函数来查询或触发状态变化。
3.  **使用组件**：你也可以将 `USceneStateComponent` 添加到任何现有的 Actor 上，使其具备场景状态管理能力。用法与 Actor 类似。

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateComponent.h"
#include "SceneStateActor.h"
#include "SceneStateObject.h" // 假设的状态对象基类
```

### 基本用法

以下示例展示如何在 C++ 中创建一个自定义的场景状态对象，并将其与一个 Actor 关联。

```cpp
// MySceneState.h
#pragma once
#include "SceneStateObject.h"
#include "MySceneState.generated.h"

UCLASS()
class UMySceneState : public USceneStateObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable)
    void ActivateLightShow();
};

// MyActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class USceneStateComponent;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    AMyActor();
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USceneStateComponent> SceneStateComp;
};

// MyActor.cpp
#include "MyActor.h"
#include "SceneStateComponent.h"
#include "MySceneState.h"

AMyActor::AMyActor()
{
    SceneStateComp = CreateDefaultSubobject<USceneStateComponent>(TEXT("SceneState"));
    // 设置要使用的状态类
    SceneStateComp->SetSceneStateClass(UMySceneState::StaticClass());
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    // 获取状态对象并调用方法
    if (UMySceneState* MyState = Cast<UMySceneState>(SceneStateComp->GetSceneState()))
    {
        MyState->ActivateLightShow();
    }
}
```

### 进阶用法

结合 `USceneStateComponentPlayer`，可以实现更精细的控制。`Player` 负责驱动状态机的更新，并为状态提供上下文（如所属的 Actor）。

```cpp
// 在自定义的 Player 中重写方法以提供上下文
class UMyComponentPlayer : public USceneStateComponentPlayer
{
    GENERATED_BODY()
protected:
    virtual bool OnGetContextObject(UObject*& OutContextObject) const override
    {
        // 提供自定义的上下文对象，例如拥有此组件的 Actor
        OutContextObject = GetActor();
        return true;
    }
};

// 在 Component 构造函数中指定自定义 Player
USceneStateComponent::USceneStateComponent(const FObjectInitializer& InObjectInitializer)
    : Super(InObjectInitializer)
{
    // 创建自定义的 Player 实例
    SceneStatePlayer = InObjectInitializer.CreateDefaultSubobject<UMyComponentPlayer>(this, SceneStatePlayerName);
}
```

## Demo 示例

以下是一个最小化的可编译示例，展示如何创建一个简单的场景状态对象和使用它的 Actor。

```cpp
// SimpleSceneState.h
#pragma once
#include "SceneStateObject.h"
#include "SimpleSceneState.generated.h"

UCLASS(Blueprintable)
class USimpleSceneState : public USceneStateObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void ToggleVisibility(bool bVisible);
};

// DemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "DemoActor.generated.h"

class USceneStateComponent;
class USimpleSceneState;

UCLASS()
class ADemoActor : public AActor
{
    GENERATED_BODY()
public:
    ADemoActor();

    UFUNCTION(BlueprintCallable)
    void ActivateState();

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USceneStateComponent> StateComponent;

    UPROPERTY()
    TObjectPtr<USimpleSceneState> CachedState;
};

// DemoActor.cpp
#include "DemoActor.h"
#include "SceneStateComponent.h"
#include "SimpleSceneState.h"

ADemoActor::ADemoActor()
{
    StateComponent = CreateDefaultSubobject<USceneStateComponent>(TEXT("State"));
    StateComponent->SetSceneStateClass(USimpleSceneState::StaticClass());
}

void ADemoActor::ActivateState()
{
    if (!CachedState)
    {
        CachedState = Cast<USimpleSceneState>(StateComponent->GetSceneState());
    }
    if (CachedState)
    {
        CachedState->ToggleVisibility(true);
    }
}

// SimpleSceneState.cpp
#include "SimpleSceneState.h"

void USimpleSceneState::ToggleVisibility(bool bVisible)
{
    // 这里可以添加实际控制场景元素的逻辑
    UE_LOG(LogTemp, Log, TEXT("Scene State Toggled Visibility: %s"), bVisible ? TEXT("True") : TEXT("False"));
}
```

## 模块依赖

从模块结构和命名推断，`SceneStateGameplay` 模块依赖于插件的核心模块。

| 模块 | 用途 |
|---|---|
| `SceneState` | 场景状态系统的核心运行时逻辑，包含状态对象基类、状态机框架等。 |
| `SceneStateBinding` | 处理场景状态与场景中具体对象（如 Actor、Component）的绑定和数据关联。 |
| `SceneStateEvent` | 定义和管理场景状态系统中使用的事件。 |
| `SceneStateTasks` | 提供用于场景状态系统的任务或操作。 |

## 维护状态

### 近期更新

```
- 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

### 维护评价

该插件于 2025 年 4 月创建，非常年轻。最近的 git 记录显示它刚刚从 `Experimental` 目录移动到 `VirtualProduction` 目录，这通常意味着它通过了初步验证，被纳入更正式的开发流程。然而，由于历史记录非常短，且 `.uplugin` 中 `IsBetaVersion` 仍为 `true`，表明它仍处于 **Beta 测试阶段**，API 和功能可能还不稳定。

**综合评价**：这是一个处于积极开发初期的实验性插件。它旨在解决虚拟制作中场景状态管理的特定需求，具有明确的用途。但由于其 Beta 状态和较短的维护历史，**不建议在生产环境中依赖它**。适合用于原型开发、技术预研或对稳定性要求不高的内部工具。建议密切关注后续更新，等待其 API 趋于稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]() （暂无）
- [测试用例]() （暂未在提供的信息中发现）