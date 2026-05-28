# Enhanced Input

> Input handling that allows for contextual and dynamic mappings.

| 属性 | 值 |
|---|---|
| 中文名 | 增强输入 |
| 分类 | Input |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EnhancedInput` (Runtime), `InputBlueprintNodes` (UncookedOnly), `InputEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-03-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput) | |

## 用途

Enhanced Input 是 Unreal Engine 的新一代输入系统，旨在取代旧的、基于轴（Axis）和动作（Action）映射的输入系统。它通过引入“输入动作（Input Action）”、“输入映射上下文（Input Mapping Context）”和“触发器（Trigger）/修饰器（Modifier）”等概念，提供了一种高度灵活、上下文感知且支持动态修改的输入处理框架。

**核心解决的问题**：
1.  **上下文切换**：游戏不同状态（如主菜单、探索、驾驶）需要完全不同的输入方案，传统系统难以干净利落地切换。Enhanced Input 允许在运行时激活或停用不同的 `InputMappingContext` 资产，实现无缝的输入方案切换。
2.  **动态映射**：在游戏过程中动态修改键位绑定（例如，玩家重绑定按键），无需重启或重新加载关卡即可生效。
3.  **复杂输入逻辑**：将一个物理按键的输入（按下、按住、释放、长按、双击等）抽象为一个“输入动作”，并通过“触发器”和“修饰器”链式处理原始输入，最终生成有意义的动作值（如向量、布尔值）。

**为什么存在**：传统输入系统功能有限，配置分散（在项目设置和蓝图中），不支持运行时修改，且难以实现复杂的输入组合逻辑。Enhanced Input 将输入逻辑资产化、模块化，提供了更强大、更清晰、更易维护的解决方案。

## 使用场景

-   **需要多种操控模式的游戏**：例如一个开放世界游戏，在徒步、驾车、菜单界面时，需要完全不同的输入响应。
-   **支持玩家自定义键位的游戏**：Enhanced Input 的设计天然支持运行时修改映射，非常适合需要重绑定功能的游戏。
-   **需要复杂输入反馈的游戏**：例如格斗游戏的连续技判定，或需要区分“轻按”与“长按”的交互系统。
-   **UI 输入与游戏输入共存**：通过 `InputMappingContext` 的优先级，可以优雅地处理当 UI 打开时游戏输入的暂停或转换。

## 蓝图用法

Enhanced Input 在蓝图层面主要通过一系列自定义节点（K2Node）来暴露其核心功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnhancedInputAction` (Event) | 蓝图中监听特定 `UInputAction` 资产触发事件的节点。根据 `ETriggerEvent`（如 Started, Ongoing, Completed, Canceled）触发不同的执行引脚。 | `UK2Node_EnhancedInputAction` |
| `Get Input Action Value` | 蓝图中获取特定 `UInputAction` 当前值的节点。值可以是 `bool`, `float`, `FVector` 等，具体取决于动作的值类型。 | `UK2Node_GetInputActionValue` |
| `Debug Key` (Event) | 用于调试的特殊事件节点，可以绑定特定的物理按键（如键盘键、手柄按钮）并在游戏运行时直接触发，方便快速测试。 | `UK2Node_InputDebugKey` |
| `Input Action Value Accessor` | 一个辅助节点，用于在动态绑定（如 Widget）中访问 `InputAction` 的值。 | `UK2Node_InputActionValueAccessor` |

### 使用示例（蓝图描述）

1.  **监听跳跃动作**：
    -   从 `Event Graph` 拖出，搜索并放置 `EnhancedInputAction` 节点。
    -   在节点属性中，指定一个预先创建好的 `IA_Jump`（跳跃动作）资产。
    -   将节点的 `Started` 引脚连接到执行逻辑，例如调用角色的 `Jump` 函数。
    -   将节点的 `Completed` 引脚连接到 `Stop Jumping` 函数。

2.  **获取移动输入值**：
    -   放置 `Get Input Action Value` 节点，指定 `IA_Move`（移动动作）资产。
    -   该节点会输出一个 `FVector2D` 或 `FVector` 类型的值（取决于 `IA_Move` 的配置），代表二维或三维移动向量。
    -   将此向量值输入到角色移动组件的 `Add Movement Input` 节点，通常需要乘以 `Delta Time`。

3.  **切换输入上下文**：
    -   使用 `Get Player Controller` 和 `Get Enhanced Input Local Player Subsystem` 节点获取子系统。
    -   调用子系统的 `Remove Mapping Context` 节点移除当前的控制方案（如 `IMC_Default`）。
    -   调用 `Add Mapping Context` 节点添加新的方案（如 `IMC_Vehicle`），并指定一个优先级（Priority）。优先级高的上下文会覆盖低优先级上下文中相同的按键映射。

## C++ 用法

Enhanced Input 的 C++ API 核心在于 `UEnhancedInputComponent` 和 `UEnhancedInputLocalPlayerSubsystem`。

### 头文件引入

```cpp
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputMappingContext.h"
```

### 基本用法

在你的角色或控制器类中，使用增强输入组件绑定动作。
（**来源**: 引擎标准角色控制器模板及文档）

```cpp
// MyCharacter.h
#pragma once
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
	GENERATED_BODY()
protected:
	// 在编辑器中指定资产
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TObjectPtr<UInputMappingContext> DefaultMappingContext;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TObjectPtr<UInputAction> JumpAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TObjectPtr<UInputAction> MoveAction;

	virtual void BeginPlay() override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"

void AMyCharacter::BeginPlay()
{
	Super::BeginPlay();

	// 将输入映射上下文添加到本地玩家子系统
	if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
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

	// 确保输入组件是增强输入组件类型
	if (UEnhancedInputComponent* EnhancedInputComponent = CastChecked<UEnhancedInputComponent>(PlayerInputComponent))
	{
		// 绑定跳跃动作
		EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
		EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);

		// 绑定移动动作
		EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
	}
}

// 注意：Move函数的签名需要与动作值类型匹配
void AMyCharacter::Move(const FInputActionValue& Value)
{
	// 获取2D向量输入
	FVector2D MovementVector = Value.Get<FVector2D>();
	// ... 应用移动逻辑
}
```

### 进阶用法

动态修改输入映射和处理触发事件。
（**来源**: 复杂输入处理模式）

```cpp
// 在某个事件（如进入载具）后，切换输入方案
void AMyCharacter::EnterVehicle()
{
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
		{
			// 移除默认移动映射，添加载具映射
			Subsystem->RemoveMappingContext(DefaultMappingContext);
			Subsystem->AddMappingContext(VehicleMappingContext, 1); // 使用更高优先级
		}
	}
}

// 处理一个长按动作
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	// ...
	EnhancedInputComponent->BindAction(ChargeAction, ETriggerEvent::Started, this, &AMyCharacter::OnChargeStart);
	EnhancedInputComponent->BindAction(ChargeAction, ETriggerEvent::Triggered, this, &AMyCharacter::OnChargeHold);
	EnhancedInputComponent->BindAction(ChargeAction, ETriggerEvent::Completed, this, &AMyCharacter::OnChargeRelease);
	// ...
}
```

## Demo 示例

一个可编译的最小角色控制器示例，演示 Enhanced Input 的基础绑定。

### MyCharacter.h
```cpp
#pragma once
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AMyCharacter();

protected:
	virtual void BeginPlay() override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	// 输入相关资产
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputMappingContext> DefaultMappingContext;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputAction> MoveAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UInputAction> LookAction;

	// 处理输入
	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);
};
```

### MyCharacter.cpp
```cpp
#include "MyCharacter.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"

AMyCharacter::AMyCharacter()
{
	PrimaryActorTick.bCanEverTick = false;

	SpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArm"));
	SpringArm->SetupAttachment(GetMesh());
	SpringArm->TargetArmLength = 400.0f;
	SpringArm->bUsePawnControlRotation = true;

	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(SpringArm, USpringArmComponent::SocketName);
	Camera->bUsePawnControlRotation = false;

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;
}

void AMyCharacter::BeginPlay()
{
	Super::BeginPlay();
	if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
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
	if (UEnhancedInputComponent* EnhancedInputComponent = CastChecked<UEnhancedInputComponent>(PlayerInputComponent))
	{
		EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
		EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::Look);
	}
}

void AMyCharacter::Move(const FInputActionValue& Value)
{
	FVector2D MovementVector = Value.Get<FVector2D>();
	if (Controller != nullptr)
	{
		const FRotator Rotation = Controller->GetControlRotation();
		const FRotator YawRotation(0, Rotation.Yaw, 0);
		const FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
		const FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);
		AddMovementInput(ForwardDirection, MovementVector.Y);
		AddMovementInput(RightDirection, MovementVector.X);
	}
}

void AMyCharacter::Look(const FInputActionValue& Value)
{
	FVector2D LookAxisVector = Value.Get<FVector2D>();
	if (Controller != nullptr)
	{
		AddControllerYawInput(LookAxisVector.X);
		AddControllerPitchInput(LookAxisVector.Y);
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 核心运行时逻辑，提供 `InputAction`, `InputMappingContext`, `EnhancedInputComponent` 等基础类。 |
| `InputBlueprintNodes` | 提供用于在蓝图中操作 Enhanced Input 的自定义 K2 节点。 |
| `InputEditor` | 提供编辑器内的资产工厂、自定义面板和图表支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `34669ae9` | Fix for input key requiring two presses to call input action | 修复了需要按两次键才能触发输入动作的问题。 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复了当成员属性为空（常见于Python脚本修改）时，PostEditChangeProperty重写导致的崩溃。 |
| 2026-05-12 | `d4c5b12a` | Changed InputModifier and InputTrigger properties from EditInstanceOnly to EditAnywhere, so that the | 将输入修饰器和触发器的属性从“仅编辑实例”改为“任意编辑”，允许在资产默认值中设置。 |
| 2026-05-12 | `19302c0b` | == This is a re-submit of 52955526, but fixed the unit tests for it == | 重新提交了之前的改动，并修复了相关单元测试。 |
| 2026-04-30 | `a24a9c37` | [Enhanced Input] Add a CVar to skip ignoring analog FKeys when input is flushed with enhanced input. | 添加了一个CVar，用于在增强输入刷新时跳过忽略模拟F键的行为。 |

### 维护评价

Enhanced Input 插件自 2022 年从实验性阶段毕业并成为默认启用的核心插件以来，一直受到 Epic Games 的**积极维护**。

-   **活跃度高**：从最近的提交记录来看，团队持续修复关键 bug（如输入响应问题、崩溃），并进行功能优化和属性可见性调整。
-   **功能成熟**：作为 UE5 的默认输入系统，其架构稳定，功能丰富，社区和官方文档支持良好。
-   **推荐使用**：对于任何新开始的 UE5 项目，**强烈推荐使用 Enhanced Input** 作为标准输入系统。它比旧系统更强大、更灵活，是未来的方向。对于从 UE4 迁移的项目，也建议逐步迁移到此系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/EnhancedInput)
- [官方文档](https://docs.unrealengine.com/en-US/enhanced-input-in-unreal-engine/)