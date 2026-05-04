# EnhancedInput 模块

> EnhancedInput 的核心运行时模块，提供逻辑输入动作（Input Action）、输入映射上下文（Input Mapping Context）、触发器（Trigger）、修改器（Modifier）以及子系统（Subsystem）的完整实现。

| 属性 | 值 |
|---|---|
| 分类 | 输入（Input） |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EnhancedInput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/EnhancedInput) | |

## 用途

EnhancedInput 模块是 UE5 Enhanced Input 系统的运行时核心。它替代了 UE4 时代的 Legacy Input System（Action/Axis Mapping），提供了一套基于 **逻辑动作** 的输入处理框架。

核心设计思想：将「物理按键」与「游戏行为」解耦。开发者定义 **Input Action**（如 Jump、Fire），然后通过 **Input Mapping Context** 将不同的物理按键映射到这些动作上。映射可以动态切换、分优先级、带有触发条件和值修改器。

与 Legacy Input 相比，EnhancedInput 解决了以下问题：
- 无法动态切换输入映射 → Input Mapping Context 可随时添加/移除
- 按键和行为紧耦合 → Action 是独立资产，可复用
- 缺乏触发条件 → Trigger 系统支持按下、释放、长按、连击等
- 值处理能力弱 → Modifier 系统支持死区、平滑、响应曲线等

## 使用场景

- 你在做一个需要多套输入方案切换的游戏（如步行/载具/菜单）→ 用 Input Mapping Context 动态切换
- 你需要实现长按、双击、组合键等复杂输入行为 → 用 Trigger 系统
- 你需要对摇杆输入做死区处理或响应曲线 → 用 Modifier 系统
- 你需要运行时重新绑定按键 → 用 Player Mappable Key Settings
- 你需要在没有 PlayerController 的 Actor 上处理输入 → 用 EnhancedInputWorldSubsystem

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Mapping Context` | 添加输入映射上下文，指定优先级 | `IEnhancedInputSubsystemInterface` |
| `Remove Mapping Context` | 移除输入映射上下文 | `IEnhancedInputSubsystemInterface` |
| `Inject Input For Action` | 模拟输入，注入指定值到某个 Action | `IEnhancedInputSubsystemInterface` |
| `Map Key` | 在 Mapping Context 中将按键映射到 Action | `UInputMappingContext` |
| `Unmap Key` | 取消按键映射 | `UInputMappingContext` |
| `Unmap All` | 清空所有映射 | `UInputMappingContext` |
| `Break Input Action Value` | 将 Action Value 拆分为 X/Y/Z + Type | `UEnhancedInputLibrary` |
| `Make Input Action Value Of Type` | 从 X/Y/Z 构建 Action Value | `UEnhancedInputLibrary` |
| `Query Keys Mapped To Action` | 查询当前映射中某 Action 绑定的所有按键 | `IEnhancedInputSubsystemInterface` |
| `Request Rebuild Control Mappings` | 请求重建控制映射 | `IEnhancedInputSubsystemInterface` |
| `Add Actor Input Component` | 将 Actor 的输入组件加入 World Subsystem | `UEnhancedInputWorldSubsystem` |
| `Set Input Mode` | 设置当前输入模式（Gameplay Tag） | `IEnhancedInputSubsystemInterface` |
| `Start Continuous Input Injection` | 开始持续注入输入（每帧） | `IEnhancedInputSubsystemInterface` |
| `Stop Continuous Input Injection` | 停止持续注入输入 | `IEnhancedInputSubsystemInterface` |
| `Flush Player Input` | 刷新玩家按下的按键 | `UEnhancedInputLibrary` |

### 使用示例（蓝图描述）

**添加输入映射上下文：**
在 BeginPlay 中，获取 Enhanced Input Local Player Subsystem → 调用 `Add Mapping Context`，传入你的 UInputMappingContext 资产和优先级（如 0）。

**绑定 Action 事件：**
在 Actor 的蓝图中，使用 Enhanced Input Component 的 `Bind Action` 节点，选择你的 UInputAction 资产，选择 Trigger Event（如 Triggered），连接到自定义事件。

**动态切换映射：**
在游戏状态变化时（如进入载具），先 `Remove Mapping Context` 移除步行映射，再 `Add Mapping Context` 添加载具映射。

## C++ 用法

### 头文件引入

```cpp
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "InputTriggers.h"
#include "InputModifiers.h"
```

### 基本用法

**绑定 Input Action（来自 InputBindingTest.cpp）：**

```cpp
// 获取 EnhancedInputComponent 并绑定 Action
UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(InputComponent);
// BindAction 支持多种签名：无参、带 Value、带 Instance
EIC->BindAction(JumpAction, ETriggerEvent::Started, this, &AMyCharacter::OnJump);
EIC->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::OnMove);
EIC->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::OnLook);

// 回调签名示例
void OnJump() { /* Jump logic */ }
void OnMove(const FInputActionValue& Value) {
    FVector2D MoveInput = Value.Get<FVector2D>();
    // ...
}
void OnLook(const FInputActionInstance& Instance) {
    FVector2D LookDelta = Instance.GetValue().Get<FVector2D>();
    float ElapsedTime = Instance.GetElapsedTime();
}
```

**添加/移除 Mapping Context（来自 InputSystemTest.cpp）：**

```cpp
UEnhancedInputLocalPlayerSubsystem* Subsystem = 
    ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer());

// 添加映射上下文，优先级 0
FModifyContextOptions Options;
Options.bIgnoreAllPressedKeysUntilRelease = true;
Subsystem->AddMappingContext(MyMappingContext, 0, Options);

// 移除映射上下文
Subsystem->RemoveMappingContext(MyMappingContext);
```

**注入输入（来自 InputSystemTest.cpp）：**

```cpp
// 单次注入
Subsystem->InjectInputForAction(TestAction, FInputActionValue(0.5f), Modifiers, Triggers);

// 持续注入（每帧自动应用）
Subsystem->StartContinuousInputInjectionForAction(TestAction, FInputActionValue(0.5f), Modifiers, Triggers);
// 更新持续注入的值
Subsystem->UpdateValueOfContinuousInputInjectionForAction(TestAction, FInputActionValue(0.8f));
// 停止持续注入
Subsystem->StopContinuousInputInjectionForAction(TestAction);
```

### 进阶用法

**自定义 Trigger：**

```cpp
// 继承 UInputTrigger 实现自定义触发逻辑
UCLASS()
class UInputTriggerDoubleTap : public UInputTrigger
{
    GENERATED_BODY()
protected:
    virtual ETriggerState UpdateState_Implementation(
        const UEnhancedPlayerInput* PlayerInput, 
        FInputActionValue ModifiedValue, 
        float DeltaTime) override
    {
        // 你的自定义触发逻辑
        // 返回 ETriggerState::None / Ongoing / Triggered
    }
};
```

**自定义 Modifier：**

```cpp
// 继承 UInputModifier 实现自定义值修改
UCLASS()
class UInputModifierCustom : public UInputModifier
{
    GENERATED_BODY()
protected:
    virtual FInputActionValue ModifyRaw_Implementation(
        const UEnhancedPlayerInput* PlayerInput, 
        FInputActionValue CurrentValue, 
        float DeltaTime) override
    {
        // 修改输入值
        return CurrentValue * 2.0f;
    }
};
```

**查询映射冲突（来自 InputSystemTest.cpp）：**

```cpp
TArray<FMappingQueryIssue> Issues;
EMappingQueryResult Result = Subsystem->QueryMapKeyInActiveContextSet(
    MyContext, MyAction, EKeys::SpaceBar, Issues, EMappingQueryIssue::NoIssue);

if (Result == EMappingQueryResult::NotMappable)
{
    // 存在映射冲突
    for (const FMappingQueryIssue& Issue : Issues)
    {
        // Issue.Issue: HiddenByExistingMapping / HidesExistingMapping 等
        // Issue.BlockingAction: 冲突的 Action
        // Issue.BlockingContext: 冲突的 Mapping Context
    }
}
```

**输入模式过滤（基于 Gameplay Tag）：**

```cpp
// 设置输入模式
FGameplayTagContainer ModeTags;
ModeTags.AddTag(FGameplayTag::RequestGameplayTag(TEXT("InputMode.Gameplay")));
Subsystem->SetInputMode(ModeTags);

// 追加标签
Subsystem->AppendTagsToInputMode(TagsToAdd, Options);

// 在 Input Mapping Context 上配置过滤规则
// InputModeFilterOptions: UseProjectDefaultQuery / UseCustomQuery / DoNotFilter
```

**World Subsystem（无 PlayerController 的 Actor 输入）：**

```cpp
UEnhancedInputWorldSubsystem* WorldSubsystem = 
    GetWorld()->GetSubsystem<UEnhancedInputWorldSubsystem>();

// 将 Actor 注册到 World Subsystem
WorldSubsystem->AddActorInputComponent(MyActor);

// Actor 需要启用输入
MyActor->SetActorEnableCollision(true);
MyActor->EnableInput(nullptr); // 无 PlayerController
```

## 模块依赖

EnhancedInput 模块的所有依赖都是 **Private**（内部依赖），使用者无需在自己的 Build.cs 中显式依赖这些模块。

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、数学库 |
| `CoreUObject` | UObject 系统、反射、序列化 |
| `Engine` | PlayerInput、PlayerController、DataAsset |
| `InputCore` | FKey、EKeys 等输入核心类型 |
| `Slate` / `SlateCore` | UI 框架（用于调试显示） |
| `ApplicationCore` | 平台应用层 |
| `DeveloperSettings` | 项目设置基类 |
| `GameplayTags` | Gameplay Tag 系统（用于输入模式过滤） |

**使用者需要做的：** 在你的模块 Build.cs 中添加对 `EnhancedInput` 的 PublicDependencyModuleNames 即可，它会自动传递所有必要的依赖。

## 模块核心类一览

| 类 | 说明 |
|---|---|
| `UInputAction` | 逻辑输入动作资产（如 Jump、Fire），定义值类型、触发器、修改器 |
| `UInputMappingContext` | 输入映射上下文，包含一组 Key→Action 映射，支持 Profile Override |
| `FEnhancedActionKeyMapping` | 单个 Key→Action 映射，可携带自己的 Trigger 和 Modifier |
| `FInputActionValue` | 输入动作的运行时值，支持 Boolean / Axis1D / Axis2D / Axis3D |
| `FInputActionInstance` | 动作实例，包含值、触发事件、经过时间等完整状态 |
| `UInputTrigger` (基类) | 触发器基类，决定 Action 何时触发 |
| `UInputTriggerDown` | 按下时持续触发（默认行为） |
| `UInputTriggerPressed` | 仅按下瞬间触发一次 |
| `UInputTriggerReleased` | 释放时触发 |
| `UInputTriggerHold` | 长按指定时间后触发 |
| `UInputTriggerHoldAndRelease` | 长按后释放时触发 |
| `UInputTriggerTap` | 短按（快速按下释放）触发 |
| `UInputTriggerRepeatedTap` | 连续点击触发（如双击） |
| `UInputTriggerPulse` | 按住时按间隔重复触发 |
| `UInputTriggerChordAction` | 组合键触发（需另一 Action 同时触发） |
| `UInputTriggerCombo` | 连招触发（按顺序完成多个 Action） |
| `UInputModifier` (基类) | 修改器基类，修改输入值 |
| `UInputModifierDeadZone` | 死区处理（Axial / Radial / UnscaledRadial） |
| `UInputModifierScalar` | 标量乘法 |
| `UInputModifierNegate` | 取反 |
| `UInputModifierSmooth` | 平滑 |
| `UInputModifierSmoothDelta` | 平滑差值（多种插值方式） |
| `UInputModifierResponseCurveExponential` | 指数响应曲线 |
| `UInputModifierResponseCurveUser` | 自定义曲线响应 |
| `UInputModifierFOVScaling` | FOV 缩放 |
| `UInputModifierToWorldSpace` | 输入空间转世界空间 |
| `UInputModifierSwizzleAxis` | 轴交换 |
| `UInputModifierScaleByDeltaTime` | 按帧时间缩放 |
| `UEnhancedInputComponent` | Actor 组件，提供 BindAction 等绑定方法 |
| `UEnhancedPlayerInput` | 增强版 PlayerInput，处理映射评估和触发逻辑 |
| `UEnhancedInputLocalPlayerSubsystem` | 每 LocalPlayer 的子系统，管理映射上下文和用户设置 |
| `UEnhancedInputWorldSubsystem` | 每 World 的子系统，支持无 PlayerController 的 Actor 输入 |
| `IEnhancedInputSubsystemInterface` | 子系统公共接口，定义 AddMappingContext 等核心方法 |
| `UEnhancedInputLibrary` | 蓝图函数库，提供 Break/Make Value 等工具函数 |
| `UEnhancedInputUserSettings` | 用户输入设置，支持按键重映射和 Profile |
| `UPlayerMappableKeySettings` | 玩家可映射按键的元数据（显示名、分类等） |

## Demo 示例

### 最小可运行示例

**MyCharacter.h**

```cpp
#pragma once

#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "MyCharacter.generated.h"

class UInputAction;
class UInputMappingContext;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    // 在编辑器中设置这些资产
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputMappingContext> DefaultMappingContext;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> JumpAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> MoveAction;

protected:
    virtual void BeginPlay() override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

    void OnJumpStarted();
    void OnMove(const FInputActionValue& Value);
};
```

**MyCharacter.cpp**

```cpp
#include "MyCharacter.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "InputAction.h"

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 获取 Enhanced Input 子系统并添加映射上下文
    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem = 
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
        {
            Subsystem->AddMappingContext(DefaultMappingContext, 0);
        }
    }
}

void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    // Cast 到 EnhancedInputComponent
    UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(PlayerInputComponent);
    if (EIC)
    {
        EIC->BindAction(JumpAction, ETriggerEvent::Started, this, &AMyCharacter::OnJumpStarted);
        EIC->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::OnMove);
    }
}

void AMyCharacter::OnJumpStarted()
{
    Jump();
}

void AMyCharacter::OnMove(const FInputActionValue& Value)
{
    FVector2D MoveInput = Value.Get<FVector2D>();
    AddMovementInput(FVector::ForwardVector, MoveInput.Y);
    AddMovementInput(FVector::RightVector, MoveInput.X);
}
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "EnhancedInput" });
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-01 | `17729ba` | 修复部分删除输入节点时的空指针崩溃（UE-316813） |
| 2025-09-29 | `abe732a` | Enhanced Input 通用更新 |
| 2025-09-29 | `4b0c897` | 修复平台设置 PostLoad 时加载插件内对象导致的失败问题 |

### 维护评价

- **创建时间**：2020-09-24（最初在 Experimental 目录下），2022-03-04 迁移到正式插件目录
- **年龄**：约 6 年
- **最近更新**：2025-10-01，活跃维护中
- **状态**：✅ **活跃维护** — 作为 UE5 的官方输入系统，持续有 bug 修复和功能增强
- **推荐使用**：✅ **强烈推荐** — 这是 UE5 的标准输入系统，替代了 Legacy Input，Epic 自己的第一方游戏（如 Fortnite）也在使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/EnhancedInput)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/InputEditor/Private/Tests)
