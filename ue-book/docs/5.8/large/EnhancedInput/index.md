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
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput) | |

## 用途

Enhanced Input 插件旨在全面取代 UE4 时代的旧输入系统。它提供了一套完全数据驱动、支持上下文敏感和动态映射的输入处理框架。其核心解决的问题是：在复杂游戏（如拥有多种载具、UI 状态、技能释放状态的游戏）中，同一按键在不同情境下需要触发完全不同的逻辑。它通过将输入动作（Action）与映射上下文（Context）解耦，实现了输入的灵活配置、复用和运行时动态切换，极大地提升了输入系统的可扩展性和可维护性。

## 使用场景

-   **复杂状态管理游戏**：你的角色在地面、水中、驾驶载具、打开菜单时，同一个按键（如 WASD）需要执行完全不同的移动逻辑 → 使用不同的输入映射上下文来管理状态。
-   **多设备与键位自定义**：你的游戏需要同时支持键盘、鼠标、手柄，并且允许玩家深度自定义键位映射，同时处理组合键和长按等高级输入 → 使用 Enhanced Input 的输入动作、修饰器（Modifier）和触发器（Trigger）系统。
-   **动态输入系统**：你的游戏需要根据游戏进程（如获得新能力后解锁新按键组合）在运行时动态添加、移除或修改输入映射 → 使用运行时的映射上下文管理 API。
-   **数据驱动开发**：你希望输入方案完全由设计师通过编辑器资产（数据资产）来配置，而非在代码中硬编码 → 将输入动作、映射、修饰器等定义为 UDataAsset。

## 蓝图用法

核心功能分布在 `EnhancedInput` 运行时模块和 `InputBlueprintNodes` 蓝图节点模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Input Action Value` | 获取一个输入动作（UInputAction）在当前帧的输入值（矢量/标量/布尔）。 | `UEnhancedInputLibrary` |
| `Create Enhanced Input Local Player Subsystem` | 创建并返回增强输入本地玩家子系统实例，是蓝图中使用增强输入的基础。 | `UEnhancedInputLibrary` |
| `Add Mapping Context` | 将一个输入映射上下文（UInputMappingContext）添加到当前玩家的输入系统中。 | `UEnhancedInputSubsystemInterface` |
| `Remove Mapping Context` | 从当前玩家的输入系统中移除一个输入映射上下文。 | `UEnhancedInputSubsystemInterface` |
| `Bind Action` | 将一个输入动作与一个蓝图事件或函数绑定。这是响应输入的最基本方法。 | `UEnhancedInputComponent` |

### 使用示例（蓝图描述）

1.  **初始化**：在角色（Character）或玩家控制器（PlayerController）的 `BeginPlay` 事件中，使用 `Create Enhanced Input Local Player Subsystem` 节点创建子系统，然后使用 `Add Mapping Context` 节点添加默认的输入映射上下文资产。
2.  **绑定输入**：在角色或控制器组件中，获取一个 `EnhancedInputComponent` 节点。使用 `Bind Action` 节点，将一个 `UInputAction` 资产（例如 `IA_Jump`）绑定到一个自定义事件（如 `On Jump Triggered`）。当该动作被触发时，你的事件就会被调用。
3.  **读取输入值**：在绑定的事件中，可以使用 `Get Input Action Value` 节点传入对应的 `UInputAction`，以获取 `FInputActionValue`，从而得到 `bool`, `float` 或 `FVector` 类型的输入值。

## C++ 用法

重点从测试用例和官方示例中提取。

### 头文件引入

```cpp
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputMappingContext.h"
```

### 基本用法

```cpp
// 在角色或控制器中
// 1. 定义成员变量
UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = Input, meta = (AllowPrivateAccess = "true"))
UInputMappingContext* DefaultMappingContext;

UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = Input, meta = (AllowPrivateAccess = "true"))
UInputAction* MoveAction;

UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = Input, meta = (AllowPrivateAccess = "true"))
UInputAction* LookAction;

// 2. 在 BeginPlay 或 PossessedBy 中添加映射上下文
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 获取增强输入子系统
    if (APlayerController* PlayerController = Cast<APlayerController>(Controller))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
        {
            Subsystem->AddMappingContext(DefaultMappingContext, 0);
        }
    }
}

// 3. 在 SetupPlayerInputComponent 中绑定输入
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    // 将玩家输入组件转换为增强输入组件
    UEnhancedInputComponent* EnhancedInputComponent = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);

    // 绑定移动动作
    EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);

    // 绑定视角动作
    EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::Look);
}
```

### 进阶用法

结合自定义输入处理器（Processor）和运行时修改映射上下文。

```cpp
// 1. 绑定带有处理器（Modifier/Trigger）的动作值
// MoveAction 的修饰器可能已经配置了“死区”或“取反”
EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);

void AMyCharacter::Move(const FInputActionValue& Value)
{
    FVector2D MovementVector = Value.Get<FVector2D>();
    // ... 处理移动逻辑
}

// 2. 运行时切换映射上下文（例如进入车辆时）
void AMyCharacter::EnterVehicle()
{
    if (APlayerController* PC = Cast<APlayerController>(GetController()))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
        {
            // 移除默认的地面移动上下文
            Subsystem->RemoveMappingContext(DefaultMappingContext);
            // 添加载具驾驶上下文
            Subsystem->AddMappingContext(VehicleMappingContext, 0);
        }
    }
}
```

## Demo 示例

一个最小的 C++ 角色输入绑定示例。

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "MyCharacter.generated.h"

class UInputMappingContext;
class UInputAction;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

protected:
    virtual void BeginPlay() override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);

private:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = Input, meta = (AllowPrivateAccess = "true"))
    UInputMappingContext* DefaultMappingContext;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = Input, meta = (AllowPrivateAccess = "true"))
    UInputAction* MoveAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = Input, meta = (AllowPrivateAccess = "true"))
    UInputAction* LookAction;
};

// MyCharacter.cpp
#include "MyCharacter.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (APlayerController* PlayerController = Cast<APlayerController>(Controller))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
        {
            Subsystem->AddMappingContext(DefaultMappingContext, 0);
        }
    }
}

void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    UEnhancedInputComponent* EnhancedInputComponent = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);
    EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
    EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::Look);
}

void AMyCharacter::Move(const FInputActionValue& Value)
{
    // Value.Get<FVector2D>().X 对应左右，.Y 对应前后
    FVector2D MovementVector = Value.Get<FVector2D>();
    // ... 实现移动
}

void AMyCharacter::Look(const FInputActionValue& Value)
{
    FVector2D LookAxisVector = Value.Get<FVector2D>();
    // ... 实现视角旋转
}
```

## 模块依赖

要使用 Enhanced Input 插件，你的模块通常需要在 `Build.cs` 中添加以下依赖。大部分是标准依赖，但 `EnhancedInput` 模块本身是必需的。

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 核心运行时库，包含子系统、输入组件、输入动作等所有主要类。 |
| `InputBlueprintNodes` | （如果需要蓝图）提供用于蓝图的函数库和 K2 节点。通常不需要显式依赖，蓝图会自动关联。 |
| `InputEditor` | （仅编辑器）用于在编辑器中可视化和管理输入资产。你的游戏模块通常不需要依赖它。 |

**注意**：在游戏模块的 `Build.cs` 中，通常只需添加 `PublicDependencyModuleNames.AddRange(new string[] { "EnhancedInput" });`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `34669ae9` | Fix for input key requiring two presses to call input action | 修复了按键需要按两次才能触发输入动作的问题。 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复了在 Python 编辑器脚本中调用 PostEditChangeProperty 时因属性为 null 导致的崩溃。 |
| 2026-05-12 | `d4c5b12a` | Changed InputModifier and InputTrigger properties from EditInstanceOnly to EditAnywhere, so that the | 将输入修饰器和触发器的属性从仅实例编辑改为任意位置编辑，提高了资产复用性。 |
| 2026-05-12 | `19302c0b` | == This is a re-submit of 52955526, but fixed the unit tests for it == | 重新提交了一次修改，并修复了相关的单元测试。 |
| 2026-04-30 | `a24a9c37` | [Enhanced Input] Add a CVar to skip ignoring analog FKeys when input is flushed with enhanced input. | 添加了一个控制台变量，用于在刷新输入时跳过忽略模拟键（FKey），增强了模拟键处理的控制。 |

### 维护评价

-   **创建时间**：2022年3月，作为 UE5 的一部分推出。
-   **最近更新频率和内容**：**非常活跃**。最近一个月内有4次提交，内容集中在**关键Bug修复**（如双击触发、编辑器崩溃）和**易用性改进**（修改属性编辑可见性），表明 Epic 持续关注其稳定性和开发者体验。
-   **维护状态**：**积极维护中**。该插件是 UE5 核心输入框架，取代了旧系统，是官方主推方案，维护优先级很高。
-   **已知问题或限制**：作为大型、复杂的系统，学习曲线较陡。从旧输入系统迁移需要一定工作量。
-   **推荐使用**：**强烈推荐**。对于任何新的 UE5 项目，尤其是计划长期维护或输入逻辑复杂的游戏，应首选 Enhanced Input。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput)
-   [官方文档](https://docs.unrealengine.com/en-US/enhanced-input-in-unreal-engine/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput/Source/EnhancedInputTests)