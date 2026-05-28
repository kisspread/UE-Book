# Enhanced Input

> Input handling that allows for contextual and dynamic mappings.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 增强输入 |
| 分类 | Input |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EnhancedInput` (Runtime), `InputBlueprintNodes` (UncookedOnly), `InputEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-03-04 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput) | |

## 用途

Enhanced Input 是 UE5 的现代输入系统，替代了传统 `UInputComponent` + `UPlayerInput` 的映射方式。它解决的核心问题是：**传统输入系统无法在运行时灵活切换上下文映射，且难以处理复杂的输入逻辑（如组合键、长按、摇杆死区等）**。

Enhanced Input 引入三个核心概念：
- **Input Action（输入动作）**：抽象的游戏动作（如"跳跃"、"开火"），与具体按键解耦
- **Input Mapping Context（输入映射上下文）**：一组"动作 → 按键"映射的集合，可在运行时动态添加/移除/切换优先级
- **Input Trigger / Input Modifier（触发器 / 修改器）**：对输入值进行条件判断（如"长按 0.5 秒才触发"）和数值变换（如"死区过滤"、"取反"）

这使得同一按键在不同游戏状态下可以触发完全不同的行为，非常适合需要上下文敏感输入的游戏（如：驾驶时按键控制载具，步行时同一按键控制角色移动）。

## 使用场景

- 你需要在不同游戏状态间切换输入映射（如战斗/驾驶/UI）→ 用 Input Mapping Context 的动态切换
- 你需要检测复杂的输入模式（长按、双击、组合键）→ 用 Input Trigger
- 你需要在编辑器工具中响应输入事件 → 用 Enhanced Input Editor Subsystem
- 你需要支持按键重映射（玩家自定义按键）→ 用 Player Mappable Key Settings
- 你需要对输入值做预处理（死区、曲线、取反）→ 用 Input Modifier

## 蓝图用法

Enhanced Input 在蓝图中主要通过 **Enhanced Input Component** 的事件绑定节点和 **Add Mapping Context** 函数使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Bind Action` | 将 Input Action 绑定到委托，监听触发事件（Triggered/Started/Ongoing/Completed/Canceled） | `UEnhancedInputComponent` |
| `Bind Action Value` | 绑定并获取带类型的输入值（bool/float/Vector2D/Vector） | `UEnhancedInputComponent` |
| `Add Mapping Context` | 为玩家添加一个输入映射上下文，可指定优先级 | `UEnhancedInputSubsystemInterface` |
| `Remove Mapping Context` | 移除玩家的输入映射上下文 | `UEnhancedInputSubsystemInterface` |
| `Request Rebuild Control Mappings` | 强制重建控制映射（修改映射后需要调用） | `UEnhancedInputSubsystemInterface` |
| `Get Mapping Context` / `Get All Mapping Contexts` | 查询当前已应用的映射上下文 | `UEnhancedInputSubsystemInterface` |
| `Push Input Component` | 将输入组件压入编辑器子系统的处理栈 | `UEnhancedInputEditorSubsystem` |
| `Start Consuming Input` | 启动编辑器子系统的输入消费（使 Input Action 委托在编辑器中触发） | `UEnhancedInputEditorSubsystem` |

### 使用示例（蓝图描述）

**基本输入绑定流程：**

1. 创建 `Input Action` 资产（如 `IA_Jump`），设置值类型（如 `bool`）
2. 创建 `Input Mapping Context` 资产（如 `IMC_Default`），添加映射：`IA_Jump` → `Space Bar`
3. 在 PlayerController 或 Character 的 BeginPlay 中：
   - 获取 `Enhanced Input Subsystem`（通过 `Get Player Subsystem` 节点）
   - 调用 `Add Mapping Context`，传入 `IMC_Default`，优先级设为 `0`
4. 在 `SetupPlayerInputComponent` 中：
   - 获取 `Enhanced Input Component` 引用
   - 调用 `Bind Action`，传入 `IA_Jump`，事件类型选 `Started`
   - 连接到自定义的 `Jump` 函数

**上下文切换流程：**

当玩家进入载具时：
1. 调用 `Remove Mapping Context` 移除 `IMC_Default`
2. 调用 `Add Mapping Context` 添加 `IMC_Vehicle`（优先级可相同或更高）

当玩家离开载具时反向操作。

## C++ 用法

### 头文件引入

```cpp
#include "EnhancedInputSubsystemInterface.h"   // 子系统接口
#include "EnhancedInputComponent.h"             // 输入组件
#include "EnhancedInputSubsystems.h"            // 子系统实现（包含 LocalPlayer 版本）
#include "InputMappingContext.h"                // 映射上下文资产
#include "InputAction.h"                        // 输入动作资产
```

### 基本用法

```cpp
// 来源: Tests/EnhancedInputTest.cpp - 基本映射上下文绑定流程

// 1. 添加 Input Mapping Context
UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer());
FModifyContextOptions Options;
Options.bIgnoreAllPressedKeysUntilRelease = false;
Subsystem->AddMappingContext(InputMappingContext, /*Priority=*/ 0, Options);

// 2. 在 SetupPlayerInputComponent 中绑定 Input Action
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    UEnhancedInputComponent* EnhancedInputComponent = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);

    // 绑定 Triggered 事件（动作被触发时，如按键按下）
    EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Triggered, this, &AMyCharacter::DoJump);

    // 绑定多个事件类型
    EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
    EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Completed, this, &AMyCharacter::StopMove);
}
```

### 进阶用法

```cpp
// 来源: Tests/InputTestFramework.h + Tests/EnhancedInputTest.cpp

// 1. 使用注入输入（Inject Input）- 在测试或程序化场景中模拟输入
Subsystem->InjectInputForAction(JumpAction, FInputActionValue(true));

// 2. 连续注入输入 - 每帧持续注入一个值
Subsystem->InjectInputForAction(MoveAction, FInputActionValue(FVector2D(1.0f, 0.0f)));
// 需要 Tick 后才会被处理
PlayerInput->Tick(DeltaTime);

// 3. 动态移除映射上下文
Subsystem->RemoveMappingContext(InputMappingContext);

// 4. 查询动作是否已被触发
bool bTriggered = false;
EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Triggered, 
    [&bTriggered](const FInputActionInstance& Instance) { bTriggered = true; });

// 5. 编辑器中使用输入子系统（用于 Editor Utility）
UEnhancedInputEditorSubsystem* EditorSubsystem = GEditor->GetEditorSubsystem<UEnhancedInputEditorSubsystem>();
EditorSubsystem->StartConsumingInput();
EditorSubsystem->PushInputComponent(MyEditorInputComponent);
```

## Demo 示例

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UInputAction;
class UInputMappingContext;
struct FInputActionValue;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

protected:
    virtual void BeginPlay() override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);

    // 输入动作资产（在编辑器中指定）
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> MoveAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> LookAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> JumpAction;

    // 输入映射上下文（在编辑器中指定）
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputMappingContext> DefaultMappingContext;
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "EnhancedInputSubsystems.h"
#include "EnhancedInputComponent.h"
#include "InputAction.h"
#include "InputMappingContext.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

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
    UEnhancedInputComponent* EIC = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);

    // 绑定输入动作到成员函数
    EIC->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
    EIC->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::Look);
    EIC->BindAction(JumpAction, ETriggerEvent::Triggered, this, &ACharacter::Jump);
}

void AMyCharacter::Move(const FInputActionValue& Value)
{
    FVector2D MoveInput = Value.Get<FVector2D>();
    AddMovementInput(GetActorForwardVector(), MoveInput.Y);
    AddMovementInput(GetActorRightVector(), MoveInput.X);
}

void AMyCharacter::Look(const FInputActionValue& Value)
{
    FVector2D LookInput = Value.Get<FVector2D>();
    AddControllerYawInput(LookInput.X);
    AddControllerPitchInput(LookInput.Y);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `34669ae9` | Fix for input key requiring two presses to call input action | 修复按键需要按两次才能触发输入动作的问题 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Python... | 修复 Python 编辑属性时 MemberProperty 为空导致的崩溃 |
| 2026-05-12 | `d4c5b12a` | Changed InputModifier and InputTrigger properties from EditInstanceOnly to EditAnywhere, so that the... | 将 InputModifier 和 InputTrigger 属性改为可从父类编辑 |
| 2026-05-12 | `19302c0b` | == This is a re-submit of 52955526, but fixed the unit tests for it == | 重新提交之前的改动并修复了单元测试 |
| 2026-04-30 | `a24a9c37` | [Enhanced Input] Add a CVar to skip ignoring analog FKeys when input is flushed with enhanced input. | 添加 CVar 以在刷新输入时跳过忽略模拟键 |

### 维护评价

Enhanced Input 是 UE5 官方推荐的输入系统，替代了旧版 Input 系统。自 2022 年从 Experimental 迁移到正式目录以来，**一直保持活跃维护**（最近更新在 2026 年 5 月）。

- **创建时间**：约 3 年前（2022-03-04），从 Experimental 迁移
- **更新频率**：非常活跃，最近几周内有多次更新，覆盖 bug 修复、API 优化、新功能
- **维护状态**：🟢 **活跃维护**，作为 UE5 核心输入系统持续得到 Epic 团队支持
- **推荐度**：**强烈推荐使用**。这是 UE5 输入处理的标准方案，新项目应优先使用 Enhanced Input 而非旧版输入系统。文档完善，社区资源丰富。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput)
- [官方文档](https://docs.unrealengine.com/en-US/enhanced-input-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput/Source/InputEditor/Private/Tests)