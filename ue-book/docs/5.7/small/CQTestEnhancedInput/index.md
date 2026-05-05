# Enhanced Input Code Quality Unreal Test Plugin

> Simplified testing of the Enhanced Input for Unreal Engine

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | CQTestEnhancedInput (DeveloperTool), CQTestEnhancedInputTests (DeveloperTool) |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/CQTestEnhancedInput) | |

## 用途

CQTestEnhancedInput 是 [CQTest](../CQTest/index.md) 测试框架的扩展插件，专门解决 **Enhanced Input 系统的自动化测试** 问题。

在 UE5 中，Enhanced Input 系统涉及 `UEnhancedInputComponent`、`UEnhancedInputLocalPlayerSubsystem`、`UInputMappingContext` 等多个组件，手动搭建测试环境非常繁琐。这个插件提供了：

- **输入注入能力**：通过 `InjectInputForAction` 直接向 Pawn 注入输入动作，无需模拟键盘/手柄事件
- **持续输入支持**：支持需要按住一段时间的轴输入（如移动摇杆），通过 ticker 每帧持续触发
- **Mock 输入子系统**：在没有完整 Player Controller 链路的测试环境中模拟 Enhanced Input 子系统
- **动作队列管理**：支持排队多个输入动作、设置持续时间、提前终止等

## 使用场景

- 你在用 CQTest 写自动化测试，需要验证角色的输入响应逻辑 → 用 CQTestEnhancedInput
- 你需要测试「按下按钮触发技能」「持续按住摇杆移动」等输入驱动的行为 → 用 CQTestEnhancedInput
- 你需要在没有完整游戏框架的情况下测试 Enhanced Input 绑定是否正确 → 用 CQTestEnhancedInput 的 Mock 子系统

## 蓝图用法

本插件为纯 C++ 测试工具，不提供蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "CQTest.h"
#include "Components/InputTestActions.h"
#include "Components/MapTestSpawner.h"
```

### 核心概念

插件的核心设计是 **Action 模式**：

1. **`FTestAction`** — 单次输入动作的基类，持有 `InputActionName`（动作名）和 `InputActionValue`（输入值）
2. **`FInputTestActions`** — 动作管理器，负责将 `FTestAction` 注入到目标 Pawn，并处理持续输入的 ticker 逻辑

`FTestAction::operator()` 内部通过以下链路注入输入：
```
Pawn → PlayerController → LocalPlayer → UEnhancedInputLocalPlayerSubsystem
→ UEnhancedPlayerInput → InjectInputForAction()
```

如果 Pawn 上的 `InputComponent` 找不到指定的 InputAction，会继续在 PlayerController 的 `InputComponent` 上查找。

### 基本用法：定义自定义输入动作

```cpp
// 定义一个按钮按下动作
struct FPressButtonAction : public FTestAction
{
    FPressButtonAction(const FString& ButtonName)
    {
        InputActionName = ButtonName;
        InputActionValue = FInputActionValue(true);  // Boolean 类型
    }
};

// 定义一个轴输入动作
struct FMoveForwardAction : public FTestAction
{
    FMoveForwardAction()
    {
        InputActionName = TEXT("MoveForward");
        InputActionValue = FInputActionValue(FVector2D(0.0f, 1.0f));  // 2D 轴
    }
};
```

### 基本用法：创建动作管理器并注入输入

```cpp
// 创建管理器，绑定到目标 Pawn
FInputTestActions TestActions(MyPawn);

// 单次注入（无 Predicate = 立即执行一次）
TestActions.PerformAction(FPressButtonAction("Jump"));

// 带持续时间的注入（通过 Predicate 控制何时停止）
TestActions.PerformAction(
    FMoveForwardAction{},
    [StartTime = FDateTime::UtcNow()]() -> bool {
        FTimespan Elapsed = FDateTime::UtcNow() - StartTime;
        return Elapsed >= FTimespan::FromSeconds(1.0);  // 持续 1 秒后停止
    }
);
```

（来源：`Source/CQTestEnhancedInput/Public/Components/InputTestActions.h` 头部注释示例）

### 进阶用法：完整的 CQTest 测试用例

以下是一个完整的测试类，展示了如何结合 CQTest 框架使用输入测试：

```cpp
// 先定义可复用的 PawnTestActions 子类
class FPawnTestActions : public FInputTestActions
{
public:
    explicit FPawnTestActions(APawn* Pawn) : FInputTestActions(Pawn) {}

    void PerformMovement()
    {
        PerformAction(FMoveForwardAction{}, [this]() -> bool {
            if (StartTime.GetTicks() == 0)
                StartTime = FDateTime::UtcNow();
            FTimespan Elapsed = FDateTime::UtcNow() - StartTime;
            return Elapsed >= FTimespan::FromSeconds(1.0);
        });
    }

    FDateTime StartTime{ 0 };
};

// 测试类
TEST_CLASS(MyInputTest, "InputActions.Movement")
{
    TUniquePtr<FMapTestSpawner> Spawner;
    TUniquePtr<FPawnTestActions> PawnActions;
    APawn* Player;

    bool IsPlayerMoving()
    {
        return !FMath::IsNearlyEqual(Player->GetVelocity().Length(), 0.0, UE_KINDA_SMALL_NUMBER);
    }

    BEFORE_EACH()
    {
        Spawner = MakeUnique<FMapTestSpawner>(TEXT("/Game/Maps/TestMap"), TEXT("TestMap"));
        Spawner->AddWaitUntilLoadedCommand(TestRunner);
    }

    TEST_METHOD(PlayerStartsMoving_ForDuration_EventuallyStops)
    {
        TestCommandBuilder
            .StartWhen([this]() { return nullptr != Spawner->FindFirstPlayerPawn(); })
            .Then([this]() {
                Player = Spawner->FindFirstPlayerPawn();
                PawnActions = MakeUnique<FPawnTestActions>(Player);
            })
            .Then([this]() { PawnActions->PerformMovement(); })
            .Then([this]() { ASSERT_THAT(IsTrue(IsPlayerMoving())); })
            .Until([this]() { return !IsPlayerMoving(); });
    }
};
```

（来源：`Source/CQTestEnhancedInput/Public/Components/InputTestActions.h` 头部注释示例）

### 进阶用法：测试按钮触发与轴输入的完整流程

插件自带的测试用例展示了更贴近实际的用法（来源：`Source/CQTestEnhancedInputTests/Private/Components/InputActionTests.cpp`）：

```cpp
TEST_CLASS(PawnActionTests, "TestFramework.CQTest.Input")
{
    TUniquePtr<FMapTestSpawner> Spawner;
    TUniquePtr<FCQTestPawnTestActions> PawnActions;

    BEFORE_EACH() {
        Spawner = FMapTestSpawner::CreateFromTempLevel(TestCommandBuilder);
        Spawner->AddWaitUntilLoadedCommand(TestRunner);
        TestCommandBuilder
            .StartWhen([this]() { return nullptr != Spawner->FindFirstPlayerPawn(); })
            .Then([this]() {
                PawnActions = MakeUnique<FCQTestPawnTestActions>(
                    Spawner->FindFirstPlayerPawn());
            });
    }

    // 测试按钮按下：触发后立即完成
    TEST_METHOD(PawnAction_TestButtonPressAction)
    {
        TestCommandBuilder
            .Do([this]() {
                PawnActions->PressButton(
                    FCQTestInputSubsystemHelper::TestButtonActionName);
            })
            .Then([this]() {
                ASSERT_THAT(IsTrue(
                    PawnActions->IsTriggered(
                        FCQTestInputSubsystemHelper::TestButtonActionName)));
            })
            .Then([this]() {
                ASSERT_THAT(IsTrue(
                    PawnActions->IsCompleted(
                        FCQTestInputSubsystemHelper::TestButtonActionName)));
            });
    }

    // 测试轴输入：持续按住后最终完成
    TEST_METHOD(PawnAction_TestHoldAxisAction)
    {
        TestCommandBuilder
            .Do([this]() {
                PawnActions->HoldAxis(
                    FCQTestInputSubsystemHelper::TestAxisActionName,
                    FInputActionValue(1.0f),
                    FTimespan::FromMilliseconds(500));
            })
            .Then([this]() {
                ASSERT_THAT(IsTrue(
                    PawnActions->IsTriggered(
                        FCQTestInputSubsystemHelper::TestAxisActionName)));
            })
            .Then([this]() {
                ASSERT_THAT(IsFalse(
                    PawnActions->IsCompleted(
                        FCQTestInputSubsystemHelper::TestAxisActionName)));
            })
            .Until([this]() {
                return PawnActions->IsCompleted(
                    FCQTestInputSubsystemHelper::TestAxisActionName);
            });
    }

    // 测试停止所有动作
    TEST_METHOD(PawnAction_CanClearActiveActions)
    {
        TestCommandBuilder
            .Do([this]() {
                PawnActions->HoldAxis(
                    FCQTestInputSubsystemHelper::TestAxisActionName,
                    FInputActionValue(1.0f),
                    FTimespan::FromSeconds(30));
            })
            .Then([this]() {
                ASSERT_THAT(IsTrue(PawnActions->HasActiveActions()));
            })
            .Then([this]() { PawnActions->StopAllActions(); })
            .Then([this]() {
                ASSERT_THAT(IsFalse(PawnActions->HasActiveActions()));
            });
    }
};
```

## 关键 API 参考

### FTestAction

| 成员 | 类型 | 说明 |
|---|---|---|
| `InputActionName` | `FString` | 要注入的 InputAction 名称（与 Pawn 上绑定的名称匹配） |
| `InputActionValue` | `FInputActionValue` | 注入的输入值（Boolean / Axis1D / Axis2D / Axis3D） |
| `operator()(const APawn*)` | 函数调用运算符 | 执行注入：查找 InputAction → 获取 Subsystem → 调用 `InjectInputForAction` |

### FInputTestActions

| 方法 | 说明 |
|---|---|
| `FInputTestActions(APawn*)` | 构造函数，绑定目标 Pawn |
| `PerformAction(Action, Predicate)` | 核心方法。无 Predicate 时立即执行一次；有 Predicate 时注册到 ticker 每帧执行，直到 Predicate 返回 true |
| `StopAllActions()` | 停止所有正在执行的动作并清空队列 |
| `HasActiveActions()` | 返回是否有排队中的动作 |

### FCQTestPawnTestActions（测试辅助类）

| 方法 | 说明 |
|---|---|
| `PressButton(ButtonName)` | 模拟按钮按下 |
| `HoldAxis(AxisName, Value, Duration)` | 模拟持续按住轴输入指定时长 |
| `IsTriggered(ActionName)` | 检查动作是否已触发（`ETriggerEvent::Triggered`） |
| `IsCompleted(ActionName)` | 检查动作是否已完成（`ETriggerEvent::Completed`） |

## Demo 示例

### 最小可运行测试

**Build.cs 依赖配置：**

```csharp
PrivateDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "InputCore",
    "EnhancedInput",
    "CQTest",
    "CQTestEnhancedInput"
});
```

**MyInputTest.h：**

```cpp
#pragma once

#include "CQTest.h"
#include "Components/InputTestActions.h"
#include "Components/MapTestSpawner.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/Pawn.h"

// 定义一个简单的跳跃动作
struct FJumpAction : public FTestAction
{
    FJumpAction()
    {
        InputActionName = TEXT("IA_Jump");
        InputActionValue = FInputActionValue(true);
    }
};

// 定义 Pawn 测试动作管理器
class FMyPawnTestActions : public FInputTestActions
{
public:
    explicit FMyPawnTestActions(APawn* InPawn) : FInputTestActions(InPawn) {}

    void Jump()
    {
        PerformAction(FJumpAction{});
    }

    void MoveForward(float DurationSeconds)
    {
        PerformAction(
            []() {},
            [this, DurationSeconds]() -> bool {
                if (StartTime.GetTicks() == 0)
                    StartTime = FDateTime::UtcNow();
                return (FDateTime::UtcNow() - StartTime) >=
                       FTimespan::FromSeconds(DurationSeconds);
            });
    }

    FDateTime StartTime{ 0 };
};

// 测试类
TEST_CLASS(JumpInputTest, "Input.Jump")
{
    TUniquePtr<FMapTestSpawner> Spawner;
    TUniquePtr<FMyPawnTestActions> PawnActions;

    BEFORE_EACH()
    {
        Spawner = FMapTestSpawner::CreateFromTempLevel(TestCommandBuilder);
        Spawner->AddWaitUntilLoadedCommand(TestRunner);
        TestCommandBuilder
            .StartWhen([this]() {
                return Spawner->FindFirstPlayerPawn() != nullptr;
            })
            .Then([this]() {
                PawnActions = MakeUnique<FMyPawnTestActions>(
                    Spawner->FindFirstPlayerPawn());
            });
    }

    TEST_METHOD(JumpInput_IsInjected)
    {
        TestCommandBuilder
            .Do([this]() { PawnActions->Jump(); })
            .Then([this]() {
                // 在此处验证角色跳跃状态
                APawn* Pawn = Spawner->FindFirstPlayerPawn();
                ASSERT_THAT(IsNotNull(Pawn));
            });
    }
};
```

## 模块依赖

### CQTestEnhancedInput（主模块）

| 模块 | 用途 |
|---|---|
| `Core` | UE 基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Pawn、PlayerController 等） |
| `EnhancedInput` | UE5 Enhanced Input 系统（输入注入核心依赖） |

> 注意：这些依赖在 Build.cs 中声明为 `PrivateDependencyModuleNames`。使用者需要在自己的模块中自行添加对 `CQTestEnhancedInput` 及上述模块的依赖。

### CQTestEnhancedInputTests（测试模块）

| 模块 | 用途 |
|---|---|
| `Core` | UE 基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入核心类型（FKey 等） |
| `EnhancedInput` | Enhanced Input 系统 |
| `CQTest` | CQTest 测试框架 |
| `CQTestEnhancedInput` | 本插件主模块 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-12 | `ce6ff392` | 修复 `FTSTicker::RemoveTicker` 的 `nodiscard` 警告 |
| 2025-07-10 | `abb369e2` | 添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏（批量代码修正） |
| 2025-04-23 | `93a13080` | DLL 导出标记调整（dllstorage 迁移） |

### 维护评价

- **创建时间**：2024-09-05，约 1.6 年历史
- **更新频率**：最近 3 次更新均为编译/链接层面的修复，无功能性变更
- **Beta 状态**：`IsBetaVersion = true`，标记为实验性
- **模块类型**：`DeveloperTool`，仅在开发/测试环境加载
- **代码规模**：非常小（核心代码仅 1 个 .h + 1 个 .cpp），API 简洁稳定
- **评价**：**维护中**。虽然近期无功能性更新，但代码规模小、API 稳定，Epic 在持续做编译兼容性维护。作为 CQTest 框架的 Enhanced Input 扩展，推荐在需要测试输入逻辑时使用。注意 Beta 标记意味着 API 可能在未来版本中变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/CQTestEnhancedInput)
- [CQTest 插件](../CQTest/index.md)（本插件的依赖框架）
- [Enhanced Input 插件](../../large/EnhancedInput/index.md)（被测试的目标系统）
