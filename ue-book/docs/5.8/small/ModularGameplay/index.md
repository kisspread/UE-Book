# Modular Gameplay

> Base classes and subsystems to support modular use of the gameplay framework

| 属性 | 值 |
|---|---|
| 中文名 | 模块化玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModularGameplay` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-31 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModularGameplay) | |

## 用途

ModularGameplay 插件为 Unreal 的 Gameplay 框架提供**模块化组件注入**和**初始化状态协调**机制。它解决的核心问题是：游戏功能插件（Game Feature Plugins）需要在不修改基础 Actor 类的情况下，动态地向 Actor 注入组件和行为。

具体来说，插件提供两大系统：

1. **Component Request System（组件请求系统）**：允许任何模块声明"当某类 Actor 出现时，自动附加某个组件"，Actor 通过 `AddReceiver`/`RemoveReceiver` 显式接受这些组件注入。请求是引用计数的，多个来源请求同一组件只会添加一个。

2. **Init State System（初始化状态系统）**：基于 GameplayTag 的初始化状态机，用于协调多个模块化组件之间的初始化顺序。组件可以声明自己实现了某个"Feature"，并通过标签状态（如 `Spawned` → `DataAvailable` → `DataInitialized` → `GameReady`）逐步推进初始化，其他组件可以监听这些状态变化来决定自己的初始化时机。

这个插件是 **Game Feature System** 的基础设施，主要被 Lyra 等 Epic 官方项目使用，支撑其高度模块化的架构设计。

## 使用场景

- 你在使用 Game Feature Plugin 架构，需要在不修改基础代码的情况下向 Actor 动态注入功能组件 → 用 ModularGameplay
- 你有多个独立模块需要按特定顺序初始化，且彼此之间有依赖关系 → 用 Init State System
- 你在开发类似 Lyra 的模块化游戏框架，需要让 Pawn、Controller、GameState 等支持功能扩展 → 继承对应的 Component 基类
- 你需要在不同插件之间实现松耦合的功能注册和事件通知 → 用 Extension Handler 机制

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Receiver` | 注册 Actor 为组件接收者，使其接受自动组件注入 | `UGameFrameworkComponentManager` |
| `Remove Receiver` | 取消 Actor 的组件接收者注册 | `UGameFrameworkComponentManager` |
| `Send Extension Event` | 向指定 Actor 发送自定义扩展事件 | `UGameFrameworkComponentManager` |
| `Register And Call For Actor Init State` | 监听指定 Actor 的初始化状态变化 | `UGameFrameworkComponentManager` |
| `Unregister Actor Init State Delegate` | 取消 Actor 初始化状态监听 | `UGameFrameworkComponentManager` |
| `Register And Call For Class Init State` | 监听某类 Actor 的初始化状态变化 | `UGameFrameworkComponentManager` |
| `Unregister Class Init State Delegate` | 取消类初始化状态监听 | `UGameFrameworkComponentManager` |

### Init State 接口节点（组件蓝图中可用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Feature Name` | 获取当前对象实现的功能名称 | `IGameFrameworkInitStateInterface` |
| `Get Init State` | 获取当前初始化状态标签 | `IGameFrameworkInitStateInterface` |
| `Has Reached Init State` | 检查是否已达到指定的初始化状态 | `IGameFrameworkInitStateInterface` |
| `Register And Call For Init State Change` | 注册并监听自身功能的初始化状态变化 | `IGameFrameworkInitStateInterface` |
| `Unregister Init State Delegate` | 取消初始化状态变化监听 | `IGameFrameworkInitStateInterface` |

### 使用示例

**自动向 Actor 注入组件：**

1. 在游戏初始化时，通过 `Get Game Instance → Get Subsystem (GameFrameworkComponentManager)` 获取管理器
2. 调用 `Add Component Request`，指定目标 Actor 类和要注入的组件类
3. 保持返回的 Handle 引用（句柄销毁时请求会被移除）
4. 在目标 Actor 的 `BeginPlay` 中调用 `Add Receiver`，注册自己为接收者
5. 组件会自动被创建并附加到该 Actor 上

**监听初始化状态：**

1. 在组件蓝图中实现 `Get Feature Name` 返回一个唯一名称（如 `"HealthComponent"`）
2. 在组件准备就绪时调用 `Try To Change Init State` 推进到下一状态
3. 其他组件通过 `Register And Call For Init State Change` 监听特定功能达到特定状态后执行初始化

## C++ 用法

### 头文件引入

```cpp
#include "Components/GameFrameworkComponentManager.h"
#include "Components/GameFrameworkComponent.h"
#include "Components/GameFrameworkInitStateInterface.h"
#include "Components/PawnComponent.h"
#include "Components/ControllerComponent.h"
#include "Components/GameStateComponent.h"
#include "Components/PlayerStateComponent.h"
```

### 基本用法：注册组件请求

以下示例展示如何声明"当某类 Pawn 出现时，自动添加自定义组件"：

```cpp
// 在游戏初始化（如 GameInstance::Init 或模块 StartupModule）中注册请求
void UMyGameInstance::Init()
{
    Super::Init();

    UGameFrameworkComponentManager* ComponentManager = GetSubsystem<UGameFrameworkComponentManager>();
    if (ComponentManager)
    {
        // 当任何 ABasicCharacter 的实例被注册为 Receiver 时，自动附加 UMyHealthComponent
        ComponentRequestHandle = ComponentManager->AddComponentRequest(
            ABasicCharacter::StaticClass(),
            UMyHealthComponent::StaticClass()
        );
    }
}
```

### 基本用法：Actor 注册为接收者

```cpp
// 在 Actor 的 BeginPlay 中注册
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 注册自身为组件接收者，触发已注册的组件请求
    UGameFrameworkComponentManager::AddGameFrameworkComponentReceiver(this);
}

void AMyCharacter::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 取消注册
    UGameFrameworkComponentManager::RemoveGameFrameworkComponentReceiver(this);

    Super::EndPlay(EndPlayReason);
}
```

### 进阶用法：实现 Init State 接口

以下示例展示如何让组件参与初始化状态协调系统。参考 Lyra 中 `ULyraHealthComponent` 的典型实现模式：

```cpp
// MyHealthComponent.h
UCLASS()
class UMyHealthComponent : public UPawnComponent, public IGameFrameworkInitStateInterface
{
    GENERATED_BODY()

public:
    UMyHealthComponent(const FObjectInitializer& ObjectInitializer);

    // --- IGameFrameworkInitStateInterface ---
    virtual FName GetFeatureName() const override { return TEXT("HealthComponent"); }
    virtual void CheckDefaultInitialization() override;

    // 可选：自定义状态转换条件
    virtual bool CanChangeInitState(
        UGameFrameworkComponentManager* Manager,
        FGameplayTag CurrentState,
        FGameplayTag DesiredState) const override;

protected:
    virtual void HandleChangeInitState(
        UGameFrameworkComponentManager* Manager,
        FGameplayTag CurrentState,
        FGameplayTag DesiredState) override;
};
```

```cpp
// MyHealthComponent.cpp
#include "Components/GameFrameworkComponentManager.h"

UMyHealthComponent::UMyHealthComponent(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

bool UMyHealthComponent::CanChangeInitState(
    UGameFrameworkComponentManager* Manager,
    FGameplayTag CurrentState,
    FGameplayTag DesiredState) const
{
    check(Manager);

    const FGameplayTag DataAvailable = FGameplayTag::RequestGameplayTag(FName("InitState.DataAvailable"));
    const FGameplayTag DataInitialized = FGameplayTag::RequestGameplayTag(FName("InitState.DataInitialized"));
    const FGameplayTag GameplayReady = FGameplayTag::RequestGameplayTag(FName("InitState.GameplayReady"));

    // DataAvailable → DataInitialized：检查依赖的其他功能是否就绪
    if (!CurrentState.IsValid() && DesiredState == DataAvailable)
    {
        return true;
    }
    if (CurrentState == DataAvailable && DesiredState == DataInitialized)
    {
        // 确认所有依赖功能已达到 DataInitialized
        return Manager->HaveAllFeaturesReachedInitState(GetOwner(), DataInitialized, GetFeatureName());
    }
    if (CurrentState == DataInitialized && DesiredState == GameplayReady)
    {
        return true;
    }

    return false;
}

void UMyHealthComponent::HandleChangeInitState(
    UGameFrameworkComponentManager* Manager,
    FGameplayTag CurrentState,
    FGameplayTag DesiredState)
{
    // 在状态转换时执行实际初始化逻辑
    if (DesiredState == FGameplayTag::RequestGameplayTag(FName("InitState.DataInitialized")))
    {
        // 初始化属性、绑定事件等
    }
}

void UMyHealthComponent::CheckDefaultInitialization()
{
    // 自动尝试推进初始化状态链
    static const TArray<FGameplayTag> StateChain = {
        FGameplayTag::RequestGameplayTag(FName("InitState.Spawned")),
        FGameplayTag::RequestGameplayTag(FName("InitState.DataAvailable")),
        FGameplayTag::RequestGameplayTag(FName("InitState.DataInitialized")),
        FGameplayTag::RequestGameplayTag(FName("InitState.GameplayReady"))
    };
    ContinueInitStateChain(StateChain);
}
```

### 进阶用法：监听其他功能的初始化状态

```cpp
void UMyAbilityComponent::BeginPlay()
{
    Super::BeginPlay();

    // 注册自身为 Init State 功能
    RegisterInitStateFeature();

    // 监听 HealthComponent 达到 DataInitialized 后再推进自身初始化
    BindOnActorInitStateChanged(
        TEXT("HealthComponent"),
        FGameplayTag::RequestGameplayTag(FName("InitState.DataInitialized")),
        /*bCallIfReached=*/ true
    );
}
```

## Demo 示例

一个最小可编译的自定义 PawnComponent，展示模块化组件注入 + Init State 协调：

```cpp
// MyStaminaComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/PawnComponent.h"
#include "Components/GameFrameworkInitStateInterface.h"
#include "MyStaminaComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyStaminaComponent : public UPawnComponent, public IGameFrameworkInitStateInterface
{
    GENERATED_BODY()

public:
    UMyStaminaComponent(const FObjectInitializer& ObjectInitializer);

    // IGameFrameworkInitStateInterface
    virtual FName GetFeatureName() const override { return TEXT("StaminaComponent"); }
    virtual void CheckDefaultInitialization() override;

    // 蓝图可读属性
    UPROPERTY(BlueprintReadOnly, Category = "Stamina")
    float CurrentStamina = 100.f;

    UPROPERTY(BlueprintReadOnly, Category = "Stamina")
    float MaxStamina = 100.f;

protected:
    virtual void HandleChangeInitState(
        UGameFrameworkComponentManager* Manager,
        FGameplayTag CurrentState,
        FGameplayTag DesiredState) override;
};
```

```cpp
// MyStaminaComponent.cpp
#include "MyStaminaComponent.h"
#include "Components/GameFrameworkComponentManager.h"

UMyStaminaComponent::UMyStaminaComponent(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

void UMyStaminaComponent::CheckDefaultInitialization()
{
    // ContinueInitStateChain 会依次尝试推进状态：Spawned → DataAvailable → DataInitialized → GameplayReady
    // 每一步都会调用 CanChangeInitState 检查条件
    static const TArray<FGameplayTag> StateChain = {
        FGameplayTag::RequestGameplayTag(FName("InitState.Spawned")),
        FGameplayTag::RequestGameplayTag(FName("InitState.DataAvailable")),
        FGameplayTag::RequestGameplayTag(FName("InitState.DataInitialized")),
        FGameplayTag::RequestGameplayTag(FName("InitState.GameplayReady"))
    };
    ContinueInitStateChain(StateChain);
}

void UMyStaminaComponent::HandleChangeInitState(
    UGameFrameworkComponentManager* Manager,
    FGameplayTag CurrentState,
    FGameplayTag DesiredState)
{
    if (DesiredState == FGameplayTag::RequestGameplayTag(FName("InitState.DataInitialized")))
    {
        // 在数据初始化阶段设置初始耐力值
        CurrentStamina = MaxStamina;
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等 + GameplayTags）。

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 初始化状态使用 `FGameplayTag` 进行状态标识和协调 |

> 注意：`GameplayTags` 虽然不是最罕见的模块，但它是本插件 Init State 系统的核心依赖，使用者需要在 Build.cs 中显式添加。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `47c2d6b1` | Unregister GameFrameworkComponentManager delegates before their owning module winds down | 修复模块卸载时委托未注销导致的崩溃 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中枚举值输出乱码 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移为新格式 |
| 2025-08-13 | `69179628` | Skip execution of GameFrameworkComponentManager unregister callbacks during engine shutdown, as the | 引擎关闭时跳过注销回调避免崩溃 |
| 2025-06-10 | `1be7adc4` | Replace some usages of FORCEINLINE with inline in GameplayFramework modules. | 替换 FORCEINLINE 为 inline 的代码风格修正 |

### 维护评价

**活跃维护中。** 该插件自 UE 5.2 起作为 Beta 存在于 Experimental 目录，于 2024 年 1 月正式迁移到 Runtime。最近的更新集中在 2026 年 4 月，主要是稳定性修复（模块卸载安全、格式化输出修正）和内部代码迁移。

关键评估点：
- **Beta 状态**：`IsBetaVersion=true` 且 `EnabledByDefault=false`，表明 Epic 仍未将其视为稳定 API，接口可能在后续版本变动
- **活跃度**：最近 6 个月内有多次实质性提交，维护积极
- **核心依赖**：该插件是 Lyra 架构的基础设施，Game Feature Plugin 系统深度依赖它，短期内不太可能被废弃
- **风险提示**：作为 Beta 插件，生产环境使用需注意版本升级时的 API 兼容性

**推荐使用**，尤其是如果你在采用 Game Feature Plugin 架构或 Lyra 式模块化设计。但需接受 Beta 状态下的潜在 API 变更风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModularGameplay)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-features-and-plugins-in-unreal-engine)（Game Feature 系统文档，涵盖 ModularGameplay 的使用场景）