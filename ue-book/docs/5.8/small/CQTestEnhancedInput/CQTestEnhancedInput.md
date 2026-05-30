# CQTestEnhancedInput

> Simplified testing of the Enhanced Input for Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 增强输入测试插件 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CQTestEnhancedInput` (DeveloperTool), `CQTestEnhancedInputTests` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestEnhancedInput) | |

## 用途

此插件是 CQTest（代码质量测试）框架的一部分，专门用于简化增强输入系统（Enhanced Input System）的自动化测试。它提供了一套工具类，让开发者能够在单元测试和集成测试中模拟玩家输入，而无需依赖复杂的框架或手动操作。

**核心解决的问题**：在编写测试代码时，如何程序化地注入和验证输入动作（Input Action）的效果，例如测试角色是否根据输入正确移动，或者技能是否在特定按键组合后触发。

## 使用场景

- 你正在为一个使用 Enhanced Input 的角色编写自动化移动测试。
- 你需要验证某个游戏逻辑（如技能释放）是否正确地响应了特定的输入组合。
- 你希望在测试中模拟持续性的输入（如按住按键移动一段时间）。
- 你在为 Enhanced Input 的相关功能开发或维护测试用例。

## 蓝图用法

该插件主要面向 C++ 测试代码，未暴露 `BlueprintCallable` 函数。其核心是供自动化测试框架（如 CQTest）在 C++ 层面调用的测试工具类。

### 核心类

| 类/结构体 | 说明 |
|---|---|
| `FTestAction` | 基础测试动作类，封装了一个输入动作及其目标值。 |
| `FInputTestActions` | 动作处理器，负责管理一组 `FTestAction` 的队列并在 Pawn 上执行。 |
| `FPawnTestActions` | (示例) 针对 Pawn 移动的特定测试动作封装，提供了如 `PerformMovement()` 的便捷方法。 |

## C++ 用法

### 头文件引入

```cpp
#include "Components/InputTestActions.h"
```

### 基本用法

以下代码展示了如何在 CQTest 测试用例中，使用 `FInputTestActions` 来测试一个 Pawn 的移动。该示例创建了一个持续 1 秒的“向前移动”输入，并断言 Pawn 在移动后会最终停下。

**来源**: `Source/CQTestEnhancedInputTests/...`（测试示例，实际使用可参考此结构）。

```cpp
// 在测试 fixture 中
TUniquePtr<FMapTestSpawner> Spawner;
TUniquePtr<FInputTestActions> InputActions;
APawn* Player;

BEFORE_EACH()
{
    // 1. 加载包含待测试 Pawn 的地图
    Spawner = MakeUnique<FMapTestSpawner>(TEXT("/Game/Path/To/TestMap"), TEXT("TestMap"));
    Spawner->AddWaitUntilLoadedCommand(TestRunner);
}

TEST_METHOD(PlayerMovesForward_WhenInputApplied)
{
    TestCommandBuilder
        // 2. 等待直到地图加载完成并能找到玩家 Pawn
        .StartWhen([this]() { return Spawner->FindFirstPlayerPawn() != nullptr; })
        .Then([this]() {
            Player = Spawner->FindFirstPlayerPawn();
            // 3. 为目标 Pawn 创建输入动作处理器
            InputActions = MakeUnique<FInputTestActions>(Player);
        })
        .Then([this]() {
            // 4. 定义并执行一个测试动作：向Y轴正方向移动
            FInputActionValue MoveValue(FVector2D(0.0f, 1.0f)); // Y=1.0 表示向前
            // 5. PerformAction 第一个参数是执行逻辑，第二个是持续条件（持续1秒）
            InputActions->PerformAction(
                [MoveValue](const APawn* Pawn) {
                    // 模拟输入：将动作值作用于 Pawn 的控制器
                    // 具体实现可能涉及调用 Pawn 的某个蓝图可调用函数或直接修改控制器
                },
                [this]() -> bool {
                    // 持续 1 秒
                    static FDateTime StartTime = FDateTime::UtcNow();
                    return (FDateTime::UtcNow() - StartTime) < FTimespan::FromSeconds(1.0);
                }
            );
        })
        .Then([this]() {
            // 6. 断言：在输入施加后，Pawn 的速度应大于零
            ASSERT_THAT(IsTrue(Player->GetVelocity().Length() > UE_KINDA_SMALL_NUMBER));
        })
        // 7. 可以添加另一个等待条件，直到 Pawn 完全停下
        .Until([this]() {
            return Player->GetVelocity().IsNearlyZero();
        });
}
```

### 进阶用法

`FInputTestActions` 可以串行执行多个动作。以下伪代码展示了如何先执行移动，然后立即执行一个跳跃动作。

```cpp
// ... 在测试步骤中
InputActions->PerformAction(/* 移动逻辑 */, /* 持续0.5秒的谓词 */);
InputActions->PerformAction(/* 跳跃逻辑 (触发布尔值输入) */);

// 可以使用 HasActiveActions() 来检查是否所有动作都已执行完毕
// 也可以在测试结束时调用 StopAllActions() 来清理。
```

## Demo 示例

以下是一个完整的测试用例示例，展示了如何在测试中模拟一次简单的按键点击（例如，使用交互键）。

```cpp
// MyInteractionTest.cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/InputTestActions.h"
#include "CQTest.h" // 假设使用 CQTest 框架

// 测试 Fixture
TEST_CLASS(FInteractionTest, "Gameplay.Interaction")
{
    // 假设的 Spawner 和 Actor 用于测试
    TUniquePtr<FMapTestSpawner> Spawner;
    AActor* TestActor;
    APawn* TestPawn;

    BEFORE_EACH()
    {
        Spawner = MakeUnique<FMapTestSpawner>(TEXT("/Game/TestMaps/InteractionTestMap"), TEXT("InteractionMap"));
        Spawner->AddWaitUntilLoadedCommand(TestRunner);
    }

    AFTER_EACH()
    {
        // 清理
        Spawner.Reset();
    }

    TEST_METHOD(PlayerPressesInteract_ObjectGetsHighlighted)
    {
        TestCommandBuilder
            .StartWhen([this]() {
                TestPawn = Spawner->FindFirstPlayerPawn();
                return TestPawn != nullptr;
            })
            .Then([this]() {
                // 假设 TestActor 是一个可交互的 Actor
                TestActor = Spawner->FindActorByTag<AActor>(FName("InteractableObject"));
                ASSERT_THAT(IsNotNull(TestActor));
            })
            .Then([this]() {
                // 模拟按下交互键 (假设交互动作名为 "IA_Interact")
                FInputTestActions InputActions(TestPawn);
                FInputActionValue InteractValue(true); // 布尔值，表示按键按下

                InputActions.PerformAction(
                    [InteractValue, this](const APawn* Pawn) {
                        // 此处是实际应用输入的逻辑。
                        // 一个简单的方式是调用 Pawn 或 Controller 上的一个蓝图可调用函数，
                        // 该函数接收 InputActionName 和 Value。
                        // 例如: UGameplayStatics::GetPlayerController(this, 0)->InputAction(TEXT("IA_Interact"), InteractValue);
                    },
                    [this]() -> bool {
                        // 只持续一帧（模拟点击）
                        static bool bFirstCall = true;
                        if (bFirstCall) {
                            bFirstCall = false;
                            return true; // 执行一次
                        }
                        return false; // 之后停止
                    }
                );
            })
            .Then([this]() {
                // 断言：检查 TestActor 是否被高亮
                bool bIsHighlighted = TestActor->GetCustomDepthStencilValue() > 0.0f; // 示例检查
                ASSERT_THAT(IsTrue(bIsHighlighted));
            });
    }
};
```

## 模块依赖

从 `Build.cs` 分析，使用此插件的模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 核心依赖，提供增强输入系统的所有基础功能。 |
| `CQTest` | CQTest 测试框架，提供 `TestCommandBuilder`、断言宏等基础设施。 |

无其他特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复了忽略标记为 `[[nodiscard]]` 函数返回值的警告。 |
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为包含生成文件的源码添加了内联宏，以优化编译。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 为所有导出符号添加了 DLL 导入/导出修饰符，增强跨模块兼容性。 |
| 2024-09-05 | `695acb19` | Upgrading the CQTest plugin to an Engine module | 初始提交，将 CQTest 增强输入测试功能作为独立引擎插件引入。 |

### 维护评价

- **创建时间**：2024 年 9 月，是一个非常年轻的插件。
- **更新频率**：自创建以来，有多次维护性提交（编译警告修复、符号导出规范），但尚无新增主要功能。
- **活跃度**：处于活跃的维护阶段，Epic 团队在调整其编译兼容性。
- **状态**：插件标记为 `IsBetaVersion: true` 且 `Installed: false`，表明它是**实验性**的，默认不启用，API 可能发生变化。
- **推荐度**：**推荐用于测试目的**。如果你需要为使用增强输入系统的游戏逻辑编写自动化测试，此插件提供了官方且简化的方法。但需注意其实验性状态，在主要项目中使用前应关注其后续版本变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestEnhancedInput)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestEnhancedInput/Source/CQTestEnhancedInputTests)