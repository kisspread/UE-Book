# Enhanced Input

> Input handling that allows for contextual and dynamic mappings.

| 属性 | 值 |
|---|---|
| 分类 | Input |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EnhancedInput` (Runtime), `InputBlueprintNodes` (UncookedOnly), `InputEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput) | |

## 用途

Enhanced Input 是 UE5 的官方输入系统，替代了 UE4 的 Legacy Input System（Action/Axis Mapping）。它提供了一套完整的、基于 **逻辑动作（Input Action）** 的输入处理框架，将物理按键与游戏行为完全解耦。

核心设计由三个层次组成：

1. **输入动作（Input Action）**：独立资产，定义逻辑行为（如 Jump、Fire）和值类型（Bool/1D/2D/3D）
2. **输入映射上下文（Input Mapping Context）**：将物理按键映射到动作，支持动态添加/移除、优先级排序、Profile 覆盖
3. **触发器（Trigger）与修改器（Modifier）**：在映射之上附加条件逻辑（长按、连击、组合键）和值处理（死区、平滑、响应曲线）

系统通过两个子系统运行：`UEnhancedInputLocalPlayerSubsystem`（常规玩家输入）和 `UEnhancedInputWorldSubsystem`（无 PlayerController 的 Actor 输入）。蓝图侧由 `InputBlueprintNodes` 模块提供自定义 K2 节点和事件绑定，编辑器侧由 `InputEditor` 模块提供资产创建、Details 面板自定义和编辑器内输入处理。

Epic 自己的第一方游戏（如 Fortnite）也在使用此系统。

## 使用场景

- **多输入方案切换**：步行/载具/菜单各有独立的 Input Mapping Context，运行时动态添加/移除即可无缝切换
- **复杂输入行为**：长按、双击、连招、组合键——通过 Trigger 系统声明式配置，无需手写计时器
- **摇杆优化**：死区处理、响应曲线、平滑——通过 Modifier 链组合实现
- **运行时按键重绑定**：Player Mappable Key Settings + EnhancedInputUserSettings 支持玩家自定义按键
- **UI 输入**：Widget 蓝图中使用 EnhancedInputAction 节点，自动注册输入
- **编辑器工具输入**：Editor Utility Widget 或编辑器工具中捕获键盘/鼠标事件（`UEnhancedInputEditorSubsystem`）
- **无 PlayerController 的 Actor 输入**：World Subsystem 允许任意 Actor 参与输入处理

## 蓝图用法

### 核心节点

**运行时节点（EnhancedInput 模块）：**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Mapping Context` | 添加输入映射上下文，指定优先级 | `IEnhancedInputSubsystemInterface` |
| `Remove Mapping Context` | 移除输入映射上下文 | `IEnhancedInputSubsystemInterface` |
| `Inject Input For Action` | 模拟输入，注入指定值到某个 Action | `IEnhancedInputSubsystemInterface` |
| `Map Key` | 在 Mapping Context 中将按键映射到 Action | `UInputMappingContext` |
| `Unmap Key` / `Unmap All` | 取消按键映射 | `UInputMappingContext` |
| `Break Input Action Value` | 将 Action Value 拆分为 X/Y/Z + Type | `UEnhancedInputLibrary` |
| `Make Input Action Value Of Type` | 从 X/Y/Z 构建 Action Value | `UEnhancedInputLibrary` |
| `Query Keys Mapped To Action` | 查询某 Action 绑定的所有按键 | `IEnhancedInputSubsystemInterface` |
| `Request Rebuild Control Mappings` | 请求重建控制映射 | `IEnhancedInputSubsystemInterface` |
| `Set Input Mode` | 设置当前输入模式（Gameplay Tag） | `IEnhancedInputSubsystemInterface` |
| `Flush Player Input` | 刷新玩家按下的按键 | `UEnhancedInputLibrary` |

**蓝图事件节点（InputBlueprintNodes 模块）：**

| 节点 | 菜单路径 | 说明 |
|---|---|---|
| `EnhancedInputAction {ActionName}` | Input > Enhanced Action Events | 输入动作事件，监听 Triggered/Started/Completed 等事件，输出 ActionValue |
| `Get {ActionName}` | Input > Enhanced Action Values | 纯函数，获取当前输入动作值（类型自动匹配 Action 的 ValueType） |
| `Debug Key {Key}` | Input > Debug Events | 调试用键事件（DevelopmentOnly，打包后不执行） |

### 使用示例（蓝图描述）

**添加输入映射上下文：**
在 BeginPlay 中，获取 Enhanced Input Local Player Subsystem → 调用 `Add Mapping Context`，传入你的 UInputMappingContext 资产和优先级（如 0）。

**绑定 Action 事件：**
在 Actor 的蓝图中，使用 Enhanced Input Component 的 `Bind Action` 节点，选择你的 UInputAction 资产，选择 Trigger Event（如 Triggered），连接到自定义事件。或直接使用 `EnhancedInputAction {ActionName}` 事件节点。

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

### 进阶用法

**自定义 Trigger：**

```cpp
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
        // 返回 ETriggerState::None / Ongoing / Triggered
    }
};
```

**自定义 Modifier：**

```cpp
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
    for (const FMappingQueryIssue& Issue : Issues)
    {
        // Issue.BlockingAction / Issue.BlockingContext / Issue.Issue
    }
}
```

**输入模式过滤（基于 Gameplay Tag）：**

```cpp
FGameplayTagContainer ModeTags;
ModeTags.AddTag(FGameplayTag::RequestGameplayTag(TEXT("InputMode.Gameplay")));
Subsystem->SetInputMode(ModeTags);
```

**World Subsystem（无 PlayerController 的 Actor 输入）：**

```cpp
UEnhancedInputWorldSubsystem* WorldSubsystem =
    GetWorld()->GetSubsystem<UEnhancedInputWorldSubsystem>();
WorldSubsystem->AddActorInputComponent(MyActor);
MyActor->EnableInput(nullptr); // 无 PlayerController
```

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

## 模块列表

| 模块 | 类型 | 说明 | 源码 |
|---|---|---|---|
| [EnhancedInput](EnhancedInput.md) | Runtime | 核心运行时：Input Action、Mapping Context、Trigger、Modifier、Subsystem | [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/EnhancedInput) |
| [InputBlueprintNodes](InputBlueprintNodes.md) | UncookedOnly | 蓝图编辑器集成：自定义 K2 节点、事件绑定、资产拖拽、数据验证 | [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/InputBlueprintNodes) |
| [InputEditor](InputEditor.md) | Editor | 编辑器集成：资产工厂、Details 面板自定义、编辑器输入子系统、自动测试框架 | [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/InputEditor) |

## 模块依赖

使用者只需在自己模块的 Build.cs 中添加对 `EnhancedInput` 的 PublicDependencyModuleNames 即可，它会自动传递所有必要的运行时依赖。

| 模块 | 依赖类型 | 用途 |
|---|---|---|
| `EnhancedInput` | Public | 运行时核心，自动传递 Core/CoreUObject/Engine/InputCore/GameplayTags 等依赖 |
| `InputBlueprintNodes` | — | 编辑器自动加载，使用者无需显式依赖 |
| `InputEditor` | — | 编辑器自动加载，使用者无需显式依赖 |

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
- **测试覆盖**：模块内含 7 个测试文件（29 个测试用例），覆盖系统级、绑定、Modifier、Trigger、玩家可重映射键、集成测试
- **推荐使用**：✅ **强烈推荐** — 这是 UE5 的标准输入系统，替代了 Legacy Input，Epic 自己的第一方游戏也在使用

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput)
- [官方文档](https://docs.unrealengine.com/en-US/enhanced-input-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/InputEditor/Private/Tests)
