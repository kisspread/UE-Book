# Enhanced Input Code Quality Unreal Test Plugin

> Simplified testing of the Enhanced Input for Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 增强输入代码质量测试插件 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CQTestEnhancedInput` (DeveloperTool), `CQTestEnhancedInputTests` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestEnhancedInput) | |

## 用途

该插件的核心目的是为 **Enhanced Input** 系统提供一套专用的自动化测试框架和工具。它解决了一个具体问题：在编写依赖于 Enhanced Input（如输入映射、输入触发器、输入修改器）的逻辑的单元测试或集成测试时，需要手动模拟和驱动输入状态，过程繁琐且容易出错。

该插件通过提供 `ACQTestInputTestActor` 等基类，封装了输入模拟和验证的复杂度，使开发者能够更简洁、清晰地编写针对输入逻辑的测试用例。它本质上是 CQTest 测试框架在 Enhanced Input 领域的扩展和补充。

## 使用场景

-   **你在开发一个使用 Enhanced Input 系统的游戏** → 你需要为角色的移动、技能释放等输入逻辑编写自动化测试。
-   **你需要测试输入映射上下文的切换** → 验证在不同游戏状态（如菜单、战斗）下，输入是否按预期绑定到正确的动作。
-   **你需要测试输入修改器（如死区、缩放）或触发器（如长按、连击）** → 确保这些组件在复杂输入场景下的行为正确。
-   **你正在使用 CQTest 框架，并希望为其添加对 Enhanced Input 的测试支持**。

## 蓝图用法

该插件主要面向 C++ 自动化测试，未提供直接的、供游戏逻辑使用的蓝图节点。其价值在于测试框架的集成。

## C++ 用法

### 头文件引入

```cpp
#include "CQTestEnhancedInput.h"
// 通常与 CQTest 头文件一起使用
#include "CQTest.h"
```

### 基本用法

`ACQTestInputTestActor` 是核心测试 Actor 基类，它简化了输入模拟。以下示例展示了如何测试一个按下 `IA_MoveForward` 动作后角色移动的逻辑。

```cpp
// 来源：基于 CQTestEnhancedInputTests 模块中测试用例的风格
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMyInputTest, "MyGame.Input.MoveForward", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FMyInputTest::RunTest(const FString& Parameters)
{
    // GIVEN: 一个游戏世界和一个待测试的 Pawn
    UWorld* World = FAutomationEditorCommonUtils::CreateNewMap();
    APawn* TestPawn = World->SpawnActor<APawn>();

    // WHEN: 使用 CQTest 的测试 Actor 模拟向前移动输入
    // ACQTestInputTestActor 负责处理 Enhanced Input 子系统和输入模拟
    ACQTestInputTestActor* InputActor = World->SpawnActor<ACQTestInputTestActor>();
    InputActor->SetupInputComponent(); // 初始化输入组件

    // 模拟按下“向前移动”输入动作
    InputActor->PressInputAction(FName("IA_MoveForward"));

    // THEN: 断言 Pawn 的移动符合预期（此处为伪代码，具体断言逻辑取决于你的游戏逻辑）
    FVector OriginalLocation = TestPawn->GetActorLocation();
    // Tick 世界以使移动生效
    World->Tick(LEVELTICK_All, 0.1f);
    FVector NewLocation = TestPawn->GetActorLocation();

    TestTrue(TEXT("Pawn should have moved forward."), NewLocation.X > OriginalLocation.X);

    // 释放输入并清理
    InputActor->ReleaseInputAction(FName("IA_MoveForward"));
    World->DestroyWorld(true);

    return true;
}
```

### 进阶用法

可以组合使用 `PressInputAction`, `ReleaseInputAction` 和 `TriggerInputAction` 来模拟更复杂的输入序列（如“长按”），并测试输入修改器的效果。

## Demo 示例

一个完整的测试类，演示如何测试一个带有“冲刺”状态的输入修改器。

```cpp
// MySprintInputTest.h
#pragma once
#include "CoreMinimal.h"
#include "CQTest.h"

// 声明一个简单的自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSprintModifierTest, "MyGame.Input.SprintModifier", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

// MySprintInputTest.cpp
#include "MySprintInputTest.h"
#include "CQTestEnhancedInput.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerInput.h"
#include "InputAction.h"
#include "InputMappingContext.h"

bool FSprintModifierTest::RunTest(const FString& Parameters)
{
    UWorld* World = FAutomationEditorCommonUtils::CreateNewMap();
    APawn* TestPawn = World->SpawnActor<APawn>();

    // GIVEN: 一个输入测试 Actor，并加载包含冲刺修改器的输入映射上下文
    ACQTestInputTestActor* InputActor = World->SpawnActor<ACQTestInputTestActor>();
    InputActor->SetupInputComponent();

    // 假设你的输入映射中，IA_Move 动作关联了一个名为 “SprintModifier” 的输入修改器，
    // 当同时按下 IA_Sprint 时，移动速度会加倍。
    // 这里我们直接模拟动作。

    // WHEN: 仅模拟移动
    InputActor->PressInputAction(FName("IA_Move"));
    World->Tick(LEVELTICK_All, 0.1f);
    float NormalSpeed = TestPawn->GetVelocity().Size();

    // WHEN: 模拟移动 + 冲刺
    InputActor->PressInputAction(FName("IA_Sprint")); // 激活冲刺修改器
    World->Tick(LEVELTICK_All, 0.1f);
    float SprintSpeed = TestPawn->GetVelocity().Size();

    // THEN: 冲刺时的速度应显著大于正常速度
    TestTrue(TEXT("Sprint speed should be greater than normal speed."), SprintSpeed > NormalSpeed * 1.5f);

    // 清理
    InputActor->ReleaseInputAction(FName("IA_Sprint"));
    InputActor->ReleaseInputAction(FName("IA_Move"));
    World->DestroyWorld(true);

    return true;
}
```

## 模块依赖

从 Build.cs 分析，使用此插件需要以下依赖：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 插件所测试的核心输入系统 |
| `CQTest` | 插件所扩展的基础代码质量测试框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复了编译器关于忽略 `nodiscard` 函数返回值的警告。 |
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为源文件添加了 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏，属于引擎代码规范更新。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 统一了模块的导出符号设置（`dllexport`），是基础设施维护。 |
| 2024-09-05 | `695acb19` | Upgrading the CQTest plugin to an Engine module... | 初始提交，将 CQTest 升级为引擎模块，并创建此增强输入专用插件。 |

### 维护评价

-   **创建时间**：创建于 2024 年 9 月，非常“年轻”的插件。
-   **最近更新频率**：近期有维护性更新（如修复编译警告、代码规范统一），但无重大的功能性变更。
-   **活跃状态**：处于**维护中**。更新主要是跟随引擎的代码规范和基础构建系统调整，并非开发新功能。
-   **已知限制**：插件被标记为 `IsBetaVersion: true`，表明它可能尚未被视为完全稳定，且默认未启用。
-   **推荐度**：如果你需要为使用 **Enhanced Input** 的系统编写 **C++ 自动化测试**，并且已经采用了 **CQTest** 框架，那么这个插件是**推荐使用**的。它能显著简化输入相关的测试代码。如果你的需求不涉及自动化测试，则无需关注此插件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestEnhancedInput)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestEnhancedInput/Source/CQTestEnhancedInputTests)