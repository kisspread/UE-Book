# Enhanced Input

> Input handling that allows for contextual and dynamic mappings.

| 属性 | 值 |
|---|---|
| 中文名 | 增强输入系统 |
| 分类 | Input |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EnhancedInput` (Runtime), `InputBlueprintNodes` (UncookedOnly), `InputEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-03-04 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput) | |

## 用途

Enhanced Input 是 UE5 的新一代输入系统，用于替代旧版 Action/Axis 映射系统。它解决了旧系统的核心痛点：

- **上下文驱动的输入映射**：通过 Input Mapping Context（输入映射上下文）按场景切换按键绑定，如从步行切换到驾驶时自动替换控制方案
- **运行时动态重映射**：支持在游戏中随时添加/移除映射上下文，无需重启或重新配置
- **输入值的修饰链（Modifier）**：在原始输入值到达游戏逻辑前，可串联死区、平滑、缩放等处理
- **触发条件系统（Trigger）**：定义输入行为如何触发——按下即触发、长按触发、释放触发、组合键触发等
- **输入模式过滤**：基于 GameplayTag 容器控制当前哪些映射上下文生效
- **玩家可重映射支持**：内置用户设置系统，支持玩家自定义按键绑定、多键位槽、键位配置文件

本质上，Enhanced Input 将"按键→动作"的映射从静态配置变为可编程的运行时系统。

## 使用场景

- 你需要根据游戏状态切换输入方案（如菜单、步行、驾驶、飞行各自独立控制）→ 使用多个 InputMappingContext 按上下文动态添加/移除
- 你需要自定义输入触发逻辑（如蓄力攻击需要按住超过 1 秒）→ 使用自定义 UInputTrigger
- 你需要对输入值做后处理（如手柄摇杆死区、鼠标灵敏度曲线）→ 使用 UInputModifier 链
- 你正在开发支持按键重映射的游戏设置菜单 → 使用 UEnhancedInputUserSettings 和 UEnhancedPlayerMappableKeyProfile
- 你需要支持多平台差异化的控制方案 → 使用 UEnhancedInputPlatformSettings 和映射上下文重定向
- 你有一个没有 PlayerController 的 Actor 需要接收输入（如世界中的交互门锁）→ 使用 UEnhancedInputWorldSubsystem

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Mapping Context` | 向玩家添加输入映射上下文（带优先级） | `IEnhancedInputSubsystemInterface` |
| `Remove Mapping Context` | 移除指定输入映射上下文 | `IEnhancedInputSubsystemInterface` |
| `Clear All Mappings` | 移除所有已应用的映射上下文 | `IEnhancedInputSubsystemInterface` |
| `Inject Input For Action` | 模拟输入注入到指定 Input Action | `IEnhancedInputSubsystemInterface` |
| `Inject Input Vector For Action` | 以 Vector 值注入输入 | `IEnhancedInputSubsystemInterface` |
| `Start Continuous Input Injection For Action` | 开始持续注入输入（每帧） | `IEnhancedInputSubsystemInterface` |
| `Stop Continuous Input Injection For Action` | 停止持续注入输入 | `IEnhancedInputSubsystemInterface` |
| `Set Input Mode` | 设置当前输入模式标签容器 | `IEnhancedInputSubsystemInterface` |
| `Add Tag To Input Mode` | 向当前输入模式追加标签 | `IEnhancedInputSubsystemInterface` |
| `Remove Tag From Input Mode` | 从当前输入模式移除标签 | `IEnhancedInputSubsystemInterface` |
| `Request Rebuild Control Mappings` | 请求重建控制映射 | `IEnhancedInputSubsystemInterface` |
| `Query Keys Mapped To Action` | 查询映射到指定动作的所有按键 | `IEnhancedInputSubsystemInterface` |
| `Has Mapping Context` | 检查映射上下文是否已应用 | `IEnhancedInputSubsystemInterface` |
| `Query Map Key In Active Context Set` | 检查按键映射是否安全可添加 | `IEnhancedInputSubsystemInterface` |
| `Get All Player Mappable Action Key Mappings` | 获取所有玩家可映射的按键映射 | `IEnhancedInputSubsystemInterface` |
| `Get Enhanced Input User Settings` | 获取用户输入设置对象 | `IEnhancedInputSubsystemInterface` |
| `Request Rebuild Control Mappings Using Context` | 对使用指定上下文的所有子系统请求重建 | `UEnhancedInputLibrary` |
| `Break Input Action Value` | 将 ActionValue 拆分为 X/Y/Z 和类型 | `UEnhancedInputLibrary` |
| `Make Input Action Value Of Type` | 从 X/Y/Z 和类型构建 ActionValue | `UEnhancedInputLibrary` |
| `Map Key` | 在映射上下文中将按键绑定到动作 | `UInputMappingContext` |
| `Unmap Key` | 在映射上下文中解绑按键 | `UInputMappingContext` |
| `Unmap All` | 清除映射上下文中所有映射 | `UInputMappingContext` |
| `Add Actor Input Component` | 将 Actor 的输入组件添加到世界子系统栈（实验性） | `UEnhancedInputWorldSubsystem` |

### 蓝图委托

| 委托 | 说明 | 所在类 |
|---|---|---|
| `ControlMappingsRebuiltDelegate` | 控制映射重建完成时触发 | `UEnhancedInputLocalPlayerSubsystem` |
| `OnMappingContextAdded` | 映射上下文被添加时触发 | `UEnhancedInputLocalPlayerSubsystem` |
| `OnMappingContextRemoved` | 映射上下文被移除时触发 | `UEnhancedInputLocalPlayerSubsystem` |
| `OnPostUserSettingsInitialized` | 用户设置对象首次加载完成后触发 | `UEnhancedInputLocalPlayerSubsystem` |

### 使用示例（蓝图描述）

**基础输入绑定流程**：

1. 创建 `UInputAction` 资产（如 "Jump"），设置 ValueType（Boolean/Axis1D/Axis2D/Axis3D）和触发器（Triggers）
2. 创建 `UInputMappingContext` 资产，添加按键映射：将 Space 键绑定到 "Jump" 动作
3. 在角色蓝图的 BeginPlay 中，通过 `Get Player Subsystem → Add Mapping Context` 添加映射上下文（优先级 0）
4. 在角色蓝图中，`EnhancedInputAction` 事件节点（蓝图自动出现）绑定 "Jump"，监听 `Triggered` 事件执行跳跃逻辑

**上下文切换示例（步行↔驾驶）**：

1. 保存两个映射上下文引用：`WalkingContext` 和 `DrivingContext`
2. 进入载具时：`Remove Mapping Context(WalkingContext)` → `Add Mapping Context(DrivingContext, Priority=1)`
3. 离开载具时：`Remove Mapping Context(DrivingContext)` → `Add Mapping Context(WalkingContext, Priority=0)`

## C++ 用法

### 头文件引入

```cpp
#include "EnhancedInput/Public/EnhancedInputSubsystemInterface.h"
#include "EnhancedInput/Public/EnhancedInputComponent.h"
#include "EnhancedInput/Public/EnhancedInputSubsystems.h"
#include "EnhancedInput/Public/InputMappingContext.h"
#include "EnhancedInput/Public/InputAction.h"
#include "EnhancedInput/Public/InputTriggers.h"
#include "EnhancedInput/Public/InputModifiers.h"
```

### 基本用法

**绑定 Input Action 到 C++ 委托**：

```cpp
// 来源: Public/EnhancedInputComponent.h - BindAction 模板
// 在 SetupPlayerInputComponent 中绑定
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(PlayerInputComponent);
    if (EIC)
    {
        // 绑定到成员函数，监听 Triggered 事件
        EIC->BindAction(JumpAction, ETriggerEvent::Triggered, this, &AMyCharacter::OnJumpTriggered);
        
        // 绑定到成员函数，监听 Started（按下瞬间）和 Completed（释放瞬间）
        EIC->BindAction(FireAction, ETriggerEvent::Started, this, &AMyCharacter::OnFireStarted);
        EIC->BindAction(FireAction, ETriggerEvent::Completed, this, &AMyCharacter::OnFireCompleted);
    }
}
```

**添加/移除映射上下文**：

```cpp
// 来源: Public/EnhancedInputSubsystemInterface.h - AddMappingContext
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (APlayerController* PC = Cast<APlayerController>(GetController()))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem = 
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
        {
            // 添加映射上下文，优先级 0
            Subsystem->AddMappingContext(DefaultMappingContext, 0);
        }
    }
}
```

**获取输入动作值**：

```cpp
// 来源: Public/InputAction.h - FInputActionInstance
void AMyCharacter::OnMovementTriggered(const FInputActionValue& Value)
{
    // Axis2D 值（如左摇杆）
    FVector2D MoveInput = Value.Get<FVector2D>();
    
    // 对应的 Action 实例数据可获取更多信息
    // FInputActionInstance 包含 ElapsedProcessedTime、TriggeredTime 等
}
```

### 进阶用法

**自定义 Trigger**：

```cpp
// 来源: Public/InputTriggers.h - UInputTrigger
UCLASS(meta=(DisplayName="Long Press"))
class UInputTriggerLongPress : public UInputTriggerTimedBase
{
    GENERATED_BODY()

public:
    // 需要按住的时间阈值
    UPROPERTY(EditAnywhere, Config, Category="Trigger Settings")
    float HoldTimeThreshold = 1.0f;

protected:
    virtual ETriggerState UpdateState_Implementation(
        const UEnhancedPlayerInput* PlayerInput, 
        FInputActionValue ModifiedValue, 
        float DeltaTime) override
    {
        // 先调用父类更新 HeldDuration
        ETriggerState SuperState = Super::UpdateState_Implementation(PlayerInput, ModifiedValue, DeltaTime);
        
        if (SuperState == ETriggerState::Ongoing && HeldDuration >= HoldTimeThreshold)
        {
            return ETriggerState::Triggered;
        }
        return SuperState;
    }
};
```

**自定义 Modifier**：

```cpp
// 来源: Public/InputModifiers.h - UInputModifier
UCLASS(meta=(DisplayName="Custom Sensitivity"))
class UInputModifierSensitivity : public UInputModifier
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category=Settings)
    float Sensitivity = 1.0f;

protected:
    virtual FInputActionValue ModifyRaw_Implementation(
        const UEnhancedPlayerInput* PlayerInput,
        FInputActionValue CurrentValue,
        float DeltaTime) override
    {
        return CurrentValue * Sensitivity;
    }
};
```

**Lambda 绑定**：

```cpp
// 来源: Public/EnhancedInputComponent.h - BindActionValueLambda
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(PlayerInputComponent);
    
    // 使用 lambda 绑定
    EIC->BindActionValueLambda(MoveAction, ETriggerEvent::Triggered,
        [this](const FInputActionValue& Value)
        {
            FVector2D Input = Value.Get<FVector2D>();
            AddMovementInput(GetActorForwardVector(), Input.Y);
            AddMovementInput(GetActorRightVector(), Input.X);
        });
    
    // 仅获取值，不触发委托
    FEnhancedInputActionValueBinding& ValueBinding = EIC->BindActionValue(LookAction);
    // 后续可通过 ValueBinding.GetValue() 查询
}
```

**输入注入**：

```cpp
// 来源: Public/EnhancedInputSubsystemInterface.h - InjectInputForAction
void AMyAIController::SimulateInput()
{
    if (UEnhancedInputLocalPlayerSubsystem* Subsystem = GetInputSubsystem())
    {
        // 注入单次输入
        Subsystem->InjectInputForAction(JumpAction, FInputActionValue(true));
        
        // 开始持续注入移动输入
        Subsystem->StartContinuousInputInjectionForAction(
            MoveAction, 
            FInputActionValue(FVector2D(0.0f, 1.0f)),  // 向前
            {},  // 无额外 modifier
            {}   // 无额外 trigger
        );
        
        // 后续停止
        // Subsystem->StopContinuousInputInjectionForAction(MoveAction);
    }
}
```

## Demo 示例

**MyCharacter.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
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
    AMyCharacter();

protected:
    virtual void BeginPlay() override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

    // 要在蓝图中设置的输入资产引用
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputMappingContext> DefaultMappingContext;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> MoveAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> LookAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> JumpAction;

    // 输入回调函数
    void OnMoveTriggered(const FInputActionValue& Value);
    void OnLookTriggered(const FInputActionValue& Value);
    void OnJumpTriggered();
};
```

**MyCharacter.cpp**：

```cpp
#include "MyCharacter.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "InputAction.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
        {
            if (DefaultMappingContext)
            {
                FModifyContextOptions Options;
                Options.bIgnoreAllPressedKeysUntilRelease = true;
                Options.bForceImmediately = false;
                Subsystem->AddMappingContext(DefaultMappingContext, 0, Options);
            }
        }
    }
}

void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(PlayerInputComponent);
    if (!EIC)
    {
        return;
    }

    EIC->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::OnMoveTriggered);
    EIC->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::OnLookTriggered);
    EIC->BindAction(JumpAction, ETriggerEvent::Triggered, this, &AMyCharacter::OnJumpTriggered);
}

void AMyCharacter::OnMoveTriggered(const FInputActionValue& Value)
{
    FVector2D Input = Value.Get<FVector2D>();
    AddMovementInput(GetActorForwardVector(), Input.Y);
    AddMovementInput(GetActorRightVector(), Input.X);
}

void AMyCharacter::OnLookTriggered(const FInputActionValue& Value)
{
    FVector2D Input = Value.Get<FVector2D>();
    AddControllerYawInput(Input.X);
    AddControllerPitchInput(Input.Y);
}

void AMyCharacter::OnJumpTriggered()
{
    Jump();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 输入模式过滤使用 GameplayTag 和 TagQuery 系统 |
| `DataValidation` | 编辑器中对 Input Action/Mapping Context 进行数据验证 |

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `34669ae9` | Fix for input key requiring two presses to call input action | 修复按键需要按两次才能触发输入动作的 bug |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Python scripting is used | 修复 Python 脚本调用时 PostEditChangeProperty 因 MemberProperty 为 null 导致的崩溃 |
| 2026-05-12 | `d4c5b12a` | Changed InputModifier and InputTrigger properties from EditInstanceOnly to EditAnywhere, so that they can be edited | 将 Modifier 和 Trigger 属性从 EditInstanceOnly 改为 EditAnywhere，允许在编辑器中直接编辑 |
| 2026-05-12 | `19302c0b` | This is a re-submit of 52955526, but fixed the unit tests for it | 重新提交之前的改动并修复了对应的单元测试 |
| 2026-04-30 | `a24a9c37` | Add a CVar to skip ignoring analog FKeys when input is flushed with enhanced input | 添加 CVar 控制输入刷新时是否忽略模拟按键 |

### 维护评价

- **创建时间**：2022年3月从 Experimental 迁移到正式目录，距今约 3 年
- **维护状态**：**活跃维护中**。最近提交（2026年5月）显示持续有 bug 修复和功能改进
- **更新频率**：高频率更新，几乎每月都有实质性改动
- **注意事项**：
  - 世界子系统（`UEnhancedInputWorldSubsystem`）仍标记为实验性
  - 组合触发器（`UInputTriggerCombo`）在 5.8 已被废弃
  - `UPlayerMappableInputConfig` 在 5.3 已被废弃，应使用 `UEnhancedInputUserSettings`
- **推荐**：强烈推荐使用。这是 UE5 官方推荐的标准输入系统，已完全取代旧版输入系统。从 UE5.1 起新建项目默认启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput)
- [官方文档](https://docs.unrealengine.com/en-US/enhanced-input-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput/Tests)