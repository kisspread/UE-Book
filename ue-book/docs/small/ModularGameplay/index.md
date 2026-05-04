# Modular Gameplay

> Base classes and subsystems to support modular use of the gameplay framework

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否（需手动启用） |
| 包含内容 | 否 |
| 模块 | ModularGameplay (Runtime, LoadingPhase=PreDefault) |
| 创建时间 | 2021-01-08 |
| 年龄标签 | 👴 老古董（约5年） |
| 实验性 | ⚠️ 是（IsBetaVersion=true） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModularGameplay) | |

## 用途

ModularGameplay 提供了一套**组件化（modular）的游戏框架扩展系统**，解决的核心问题是：**如何在不修改基础游戏框架类（如 APawn、AController、AGameStateBase 等）的前提下，通过插件/模块化方式向这些 Actor 注入功能**。

传统方式下，如果你想给所有 Pawn 添加一个自定义能力（比如冲刺），你需要修改 APawn 子类或在 GameMode 里写逻辑。ModularGameplay 的做法是：

1. **GameFrameworkComponentManager**（GameInstance 子系统）作为中央管理器
2. 插件/模块通过 `AddComponentRequest` 声明"我要在某类 Actor 上自动挂载这个组件"
3. Actor 通过 `AddReceiver`/`RemoveReceiver` 注册/注销自己为"接收者"
4. 当接收者被创建时，管理器自动实例化所有请求的组件

这使得 **Lyra**、**Game Features** 等框架能在运行时动态添加/移除功能模块，是 UE5 模块化游戏架构的基础设施。

## 使用场景

- 你在做一款需要支持 DLC/插件式内容的游戏（如 Lyra） → 用 ModularGameplay 让 DLC 模块自动向 Pawn 注入组件
- 你需要多个独立团队开发不同功能（战斗、背包、技能），但都作用于同一个 Pawn → 每个模块独立请求组件挂载，互不干扰
- 你需要组件之间有初始化顺序依赖（A 组件初始化后 B 才能开始） → 用 InitState 系统协调初始化状态机
- 你想让 GameFeature 插件在运行时动态启用/禁用功能 → ModularGameplay 是 GameFeature 系统的底层支撑

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Receiver` | 将 Actor 注册为组件接收者，之后可自动获得请求的组件 | `UGameFrameworkComponentManager` |
| `Remove Receiver` | 注销 Actor 的接收者身份，自动销毁管理器创建的组件 | `UGameFrameworkComponentManager` |
| `Send Extension Event` | 向接收者发送自定义扩展事件 | `UGameFrameworkComponentManager` |
| `Get Init State` | 获取当前 Actor Feature 的初始化状态 | `IGameFrameworkInitStateInterface` |
| `Has Reached Init State` | 检查 Feature 是否已到达指定初始化状态 | `IGameFrameworkInitStateInterface` |
| `Register And Call For Init State Change` | 注册蓝图委托监听初始化状态变化 | `IGameFrameworkInitStateInterface` |

### 使用示例（蓝图描述）

**场景：在蓝图中监听 Pawn 的初始化状态**

1. 在你的 PawnComponent 蓝图中，调用 `Get Init State` 获取当前状态
2. 使用 `Register And Call For Init State Change`，设置 `RequiredState` 为你关心的 GameplayTag（如 `InitState.DataAvailable`），连接一个自定义事件作为委托
3. 当 Feature 的初始化状态推进到 `RequiredState` 或更晚时，你的委托会被调用

## C++ 用法

### 头文件引入

```cpp
#include "Components/GameFrameworkComponentManager.h"
#include "Components/GameFrameworkComponent.h"
#include "Components/PawnComponent.h"
#include "Components/ControllerComponent.h"
#include "Components/PlayerStateComponent.h"
#include "Components/GameStateComponent.h"
#include "Components/GameFrameworkInitStateInterface.h"
```

### 基本用法：请求自动挂载组件

在你的 GameInstanceSubsystem 或模块初始化时，请求管理器自动在指定 Actor 类上挂载组件：

```cpp
// 来源: GameFrameworkComponentManager.h - AddComponentRequest

// 获取管理器
UGameFrameworkComponentManager* Manager = UGameInstance::GetSubsystem<UGameFrameworkComponentManager>(GameInstance);

// 请求在所有 AMyCharacter 上自动挂载 UMyAbilityComponent
ComponentRequestHandle = Manager->AddComponentRequest(
    AMyCharacter::StaticClass(),  // 目标 Actor 类
    UMyAbilityComponent::StaticClass()  // 要挂载的组件类
);

// TSharedPtr<FComponentRequestHandle> 会在销毁时自动移除请求
// 用成员变量持有它即可保持请求"存活"
```

### 基本用法：Actor 注册为接收者

在你的 Actor（如自定义 Pawn）中注册/注销：

```cpp
// 来源: GameFrameworkComponentManager.h - AddReceiver/RemoveReceiver

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    // 注册为接收者，之后所有匹配的组件请求都会生效
    UGameFrameworkComponentManager::AddGameFrameworkComponentReceiver(this);
}

void AMyCharacter::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 注销接收者，管理器会自动销毁它创建的组件
    UGameFrameworkComponentManager::RemoveGameFrameworkComponentReceiver(this);
    Super::EndPlay(EndPlayReason);
}
```

### 基本用法：使用类型化组件基类

为不同框架类提供便捷的类型访问器：

```cpp
// 来源: PawnComponent.h
// UPawnComponent 自动提供 GetPawn<T>()、GetPlayerState<T>()、GetController<T>()

UCLASS()
class UMyHealthComponent : public UPawnComponent
{
    GENERATED_BODY()
public:
    void TakeDamage(float Damage)
    {
        APawn* MyPawn = GetPawn<APawn>();
        AMyPlayerState* PS = GetPlayerState<AMyPlayerState>();
        // ...
    }
};
```

```cpp
// 来源: ControllerComponent.h
// UControllerComponent 自动提供 GetController<T>()、GetPawn<T>()、GetViewTarget<T>()、GetPlayerViewPoint()

UCLASS()
class UMyInputComponent : public UControllerComponent
{
    GENERATED_BODY()
public:
    void HandleInput()
    {
        APlayerController* PC = GetController<APlayerController>();
        if (IsLocalController())
        {
            // 仅本地控制器处理输入
        }
    }
};
```

### 进阶用法：InitState 状态机

InitState 系统让多个组件协调初始化顺序。每个组件声明自己是一个 Feature，通过 GameplayTag 表示初始化状态：

```cpp
// 来源: GameFrameworkInitStateInterface.h + .cpp

UCLASS()
class UMyDataComponent : public UPawnComponent, public IGameFrameworkInitStateInterface
{
    GENERATED_BODY()

    // 声明此组件实现的 Feature 名称
    virtual FName GetFeatureName() const override { return FName("MyData"); }

    // 注册到 InitState 系统
    virtual void OnRegister() override
    {
        Super::OnRegister();
        RegisterInitStateFeature();  // 向 ComponentManager 注册此 Feature
        BindOnActorInitStateChanged(NAME_None, FGameplayTag(), false);  // 监听所有状态变化
    }

    virtual void OnUnregister() override
    {
        UnregisterInitStateFeature();
        Super::OnUnregister();
    }

    // 当其他 Feature 状态变化时被调用
    virtual void OnActorInitStateChanged(const FActorInitStateChangedParams& Params) override
    {
        // 检查依赖是否就绪，然后推进自己的状态
        CheckDefaultInitialization();
    }

    // 实现初始化状态推进逻辑
    virtual void CheckDefaultInitialization() override
    {
        // ContinueInitStateChain 会按顺序尝试推进状态链
        static const TArray<FGameplayTag> StateChain = {
            FGameplayTag::RequestGameplayTag(FName("InitState.Spawned")),
            FGameplayTag::RequestGameplayTag(FName("InitState.DataAvailable")),
            FGameplayTag::RequestGameplayTag(FName("InitState.DataInitialized")),
            FGameplayTag::RequestGameplayTag(FName("InitState.GameplayReady")),
        };
        ContinueInitStateChain(StateChain);
    }

    // 在推进前检查前置条件
    virtual bool CanChangeInitState(UGameFrameworkComponentManager* Manager,
        FGameplayTag CurrentState, FGameplayTag DesiredState) const override
    {
        const FName FeatureName = GetFeatureName();
        const AActor* Actor = GetOwner();

        // 从 DataAvailable -> DataInitialized 需要所有其他 Feature 也到了 DataAvailable
        if (DesiredState == FGameplayTag::RequestGameplayTag(FName("InitState.DataInitialized")))
        {
            return Manager->HaveAllFeaturesReachedInitState(
                const_cast<AActor*>(Actor),
                FGameplayTag::RequestGameplayTag(FName("InitState.DataAvailable")),
                FeatureName);  // 排除自身
        }
        return true;
    }
};
```

### 进阶用法：扩展事件系统

除了自动挂载组件，你还可以注册委托监听 Actor 生命周期事件：

```cpp
// 来源: GameFrameworkComponentManager.h - AddExtensionHandler

// 在模块初始化时注册扩展处理
ExtensionHandle = Manager->AddExtensionHandler(
    AMyCharacter::StaticClass(),
    UGameFrameworkComponentManager::FExtensionHandlerDelegate::CreateLambda(
        [](AActor* Actor, FName EventName)
        {
            if (EventName == UGameFrameworkComponentManager::NAME_ReceiverAdded)
            {
                // Actor 刚注册为接收者，组件已挂载
            }
            else if (EventName == UGameFrameworkComponentManager::NAME_GameActorReady)
            {
                // Actor 已准备好，可以开始自定义逻辑
            }
        })
);
```

## Demo 示例

一个最小的可编译示例：通过 ModularGameplay 在自定义 Pawn 上自动挂载一个 Health 组件。

**MyHealthComponent.h**

```cpp
#pragma once

#include "Components/PawnComponent.h"
#include "MyHealthComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyHealthComponent : public UPawnComponent
{
    GENERATED_BODY()

public:
    UMyHealthComponent(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer)
    {
        Health = 100.0f;
    }

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Health")
    float Health;

    UFUNCTION(BlueprintCallable, Category = "Health")
    void ApplyDamage(float Damage)
    {
        Health = FMath::Max(0.0f, Health - Damage);
    }

    UFUNCTION(BlueprintCallable, Category = "Health")
    bool IsAlive() const { return Health > 0.0f; }
};
```

**MyGameInstanceSubsystem.h** — 在这里注册组件请求

```cpp
#pragma once

#include "Subsystems/GameInstanceSubsystem.h"
#include "MyGameInstanceSubsystem.generated.h"

class FComponentRequestHandle;

UCLASS()
class MYGAME_API UMyGameInstanceSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override
    {
        Super::Initialize(Collection);

        // 获取 ComponentManager 并请求在 AMyCharacter 上自动挂载 Health 组件
        UGameFrameworkComponentManager* Manager =
            UGameInstance::GetSubsystem<UGameFrameworkComponentManager>(GetGameInstance());
        if (Manager)
        {
            HealthComponentRequest = Manager->AddComponentRequest(
                TEXT("/Script/MyGame.MyCharacter"),
                UMyHealthComponent::StaticClass());
        }
    }

private:
    TSharedPtr<FComponentRequestHandle> HealthComponentRequest;
};
```

**MyCharacter.cpp** — Pawn 注册为接收者

```cpp
#include "Components/GameFrameworkComponentManager.h"

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    UGameFrameworkComponentManager::AddGameFrameworkComponentReceiver(this);
}

void AMyCharacter::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UGameFrameworkComponentManager::RemoveGameFrameworkComponentReceiver(this);
    Super::EndPlay(EndPlayReason);
}
```

**Build.cs 依赖**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "Engine",
    "ModularGameplay",
    "GameplayTags",  // 如果使用 InitState 系统
});
```

## 模块依赖

你的模块需要依赖以下模块才能使用 ModularGameplay：

| 模块 | 用途 |
|---|---|
| `ModularGameplay` | 本插件模块，提供所有组件基类和 ComponentManager |
| `GameplayTags` | InitState 系统使用 GameplayTag 表示初始化状态 |
| `Core` | UE 核心模块 |
| `Engine` | 引擎模块（AActor、UActorComponent 等） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-08-13 | `69179628` | **Bug 修复**: 在引擎关闭时跳过 ComponentManager 的注销回调，避免访问无效 UWorld |
| 2025-06-10 | `1be7adc4` | **重构**: 将 GameplayFramework 模块中的 `FORCEINLINE` 替换为 `inline` |
| 2025-05-21 | `5bf312e0` | **Bug 修复**: 修复多个请求注册同一 Actor/组件对时，销毁时注销不正确的问题 |

### 维护评价

- **创建时间**: 2021 年 1 月，约 5 年历史
- **最近更新**: 2025 年 8 月，近期有实质性 bug 修复
- **维护状态**: ✅ **活跃维护** — 仍在修复 bug 和改进
- **实验性标记**: ⚠️ `.uplugin` 中 `IsBetaVersion=true`、`EnabledByDefault=false`，表明 Epic 仍将其视为实验性功能，但实际上 Lyra 项目重度依赖此系统
- **已知限制**: `EnabledByDefault=false` 意味着你需要在项目设置中手动启用此插件；请求目标不能是 `AActor` 本身（性能原因）
- **推荐使用**: ✅ 如果你在做模块化架构或使用 GameFeature 系统，这是必选依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ModularGameplay)
- 官方文档: 无（`.uplugin` 中 DocsURL 为空）
- 测试用例: 未找到独立测试文件（此插件无自带测试）
