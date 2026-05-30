# Enhanced Input Code Quality Unreal Test Plugin

> Simplified testing of the Enhanced Input for Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 增强输入测试助手 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CQTestEnhancedInput` (DeveloperTool), `CQTestEnhancedInputTests` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestEnhancedInput) | |

## 用途

该插件是 **CQTest（Code Quality Test）** 框架的一部分，专门用于简化 **Enhanced Input** 系统的自动化测试。它的核心价值在于提供一套辅助工具，允许开发者在编写输入相关的单元测试时，无需创建完整的游戏世界、玩家控制器或真实的输入设备，从而能够快速、隔离地验证输入动作（`UInputAction`）的绑定、触发事件（`ETriggerEvent`）和模拟输入注入是否按预期工作。

简而言之，它解决了在测试环境中模拟和验证复杂输入系统的难题，是编写健壮输入逻辑的“测试桩”。

## 使用场景

- 你正在使用 **Enhanced Input** 系统处理玩家输入。
- 你需要为角色的移动、跳跃、射击等输入逻辑编写自动化测试。
- 在测试环境中，你希望避免实例化一个完整的 `APlayerController` 或依赖底层输入设备。
- 你需要验证当一个输入动作（如“前进”）被触发时，`ETriggerEvent::Started`、`ETriggerEvent::Ongoing`、`ETriggerEvent::Completed` 等事件是否在正确的时机被调用。

## 蓝图用法

该插件**不包含蓝图资产或蓝图节点**。其所有功能均通过 C++ 的测试框架（如 Unreal Automation Testing）和提供的 C++ 辅助类来使用，旨在服务于开发者编写底层测试代码。

## C++ 用法

本插件的核心是两个辅助类：`FCQTestInputSubsystemHelper` 用于快速搭建一个模拟的输入子系统环境，`FCQTestPawnTestActions` 继承自 `FInputTestActions` 并封装了常用的输入测试操作。

### 头文件引入

```cpp
#include "CQTestInputTestHelper.h"
```

### 基本用法

使用 `FCQTestInputSubsystemHelper` 为测试中的 `APawn` 模拟一个输入环境。

```cpp
// 来自 Private/CQTestInputTestHelper.h

// 假设在测试中已经创建或获取了一个 APawn* TestPawn
FCQTestInputSubsystemHelper InputHelper(TestPawn);

// 模拟按下“TestButtonAction”，并验证它触发了 ETriggerEvent::Started
bool bWasTriggered = InputHelper.ActionExpectedEvent(
    FCQTestInputSubsystemHelper::TestButtonActionName,
    ETriggerEvent::Started
);

// 同样，可以验证轴向输入
InputHelper.ActionExpectedEvent(
    FCQTestInputSubsystemHelper::TestAxisActionName,
    ETriggerEvent::Triggered // 轴向输入通常持续触发
);
```

### 进阶用法

使用 `FCQTestPawnTestActions` 来执行更复杂的输入模拟并验证状态。这个类在内部创建了 `FCQTestInputSubsystemHelper`，并提供了 `PressButton`、`HoldAxis`、`IsTriggered`、`IsCompleted` 等便捷方法。

```cpp
// 假设在测试类中
void FMyInputTest::RunTest(FString const& Parameters, FAutomationTestBase* Test)
{
    // ... 创建世界和 Pawn ...
    APawn* TestPawn = GetTestPawn();

    // 创建测试动作辅助器
    FCQTestPawnTestActions TestActions(TestPawn);

    // 1. 模拟按下“TestButtonAction”按钮
    TestActions.PressButton(FCQTestInputSubsystemHelper::TestButtonActionName);

    // 2. 验证按钮动作是否已触发
    if (!TestActions.IsTriggered(FCQTestInputSubsystemHelper::TestButtonActionName))
    {
        Test->AddError(TEXT("Button action was not triggered after press."));
    }

    // 3. 模拟按住一个轴向输入一段时间（例如，模拟摇杆前推1秒）
    FInputActionValue AxisValue(FVector(0.0f, 1.0f, 0.0f)); // Y轴为正，模拟“前进”
    TestActions.HoldAxis(
        FCQTestInputSubsystemHelper::TestAxisActionName,
        AxisValue,
        FTimespan::FromSeconds(1.0) // 按住1秒
    );

    // 4. 在按住期间和之后，验证轴向动作的触发和完成事件
    // HoldAxis 会自动推进测试框架的时间，模拟输入持续过程
    // 可以使用 TestActions.IsTriggered(...) 和 TestActions.IsCompleted(...) 来检查状态
}
```

## Demo 示例

一个完整的、可编译的最小自动化测试示例，展示如何测试一个角色的“前进”输入。

**MyCharacterInputTest.h**
```cpp
#pragma once
#include "Misc/AutomationTest.h"

// 一个简单的自动化测试用例
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FCharacterMoveForwardTest,
    "MyProject.Character.Input.MoveForward",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter
)
```

**MyCharacterInputTest.cpp**
```cpp
#include "MyCharacterInputTest.h"
#include "CQTestInputTestHelper.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
#include "EnhancedInputSubsystems.h"

bool FCharacterMoveForwardTest::RunTest(const FString& Parameters)
{
    // 1. 创建最小化的测试世界和角色
    UWorld* World = FAutomationEditorCommonUtils::CreateNewMap();
    ACharacter* TestCharacter = World->SpawnActor<AMyTestCharacter>();
    TestCharacter->SpawnDefaultController(); // 确保控制器存在

    // 2. 使用 CQTest 辅助器模拟输入环境
    FCQTestPawnTestActions TestActions(TestCharacter);

    // 3. 模拟玩家持续按住“移动前进”轴向输入（W键映射到的轴）
    FInputActionValue MoveForwardValue(FVector(0.0f, 1.0f, 0.0f)); // 假设 Y+ 为前进
    FTimespan HoldDuration = FTimespan::FromSeconds(0.5f);
    TestActions.HoldAxis(TEXT("IA_MoveForward"), MoveForwardValue, HoldDuration);

    // 4. 验证：在输入期间，角色应该正在移动
    // （此处需要结合你的角色移动逻辑进行断言，例如检查速度或位置变化）
    // 注意：在纯自动化测试中，世界Tick可能未被驱动，你可能需要手动调用 Tick 或使用 LatentCommand

    // 5. 验证：当轴向输入的持续时间结束，事件应标记为 Completed
    TestTrue(TEXT("Move forward action should be completed after hold duration."),
             TestActions.IsCompleted(TEXT("IA_MoveForward")));

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CQTestEnhancedInput` | CQTest 框架的增强输入基础支持模块，本插件依赖于此 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复了因函数声明了`nodiscard`属性但返回值被忽略导致的编译警告。 |
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为具有对应生成文件的源文件添加了内联生成宏，优化编译。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 统一了DLL符号导出规范，增强了模块的兼容性。 |
| 2024-09-05 | `695acb19` | Upgrading the CQTest plugin to an Engine module | 初始提交，将CQTest插件升级为引擎模块并创建本插件。 |

### 维护评价

该插件创建于 **2024年9月**，距今约1年，属于**较新的插件**。从提交历史看，它**正在被积极维护**，最近一次更新（2025年9月）旨在修复编译警告，这表明 Epic 正在持续关注其代码质量。然而，需要特别注意的是，**该插件在 `.uplugin` 中被标记为 `IsBetaVersion: true`**，并且默认未启用（`Installed: false`）。这明确表示它是一个**实验性功能**，其API和行为在未来引擎版本中可能发生不兼容的更改。

**推荐使用**：如果你正在使用 Unreal Engine 的自动化测试框架（如 FAutomationTest）并深度依赖 Enhanced Input，那么该插件是编写输入测试的宝贵工具。但鉴于其“Beta”状态，建议：
1.  关注其在后续引擎版本中的更新说明。
2.  考虑在项目中将其作为可选依赖，以便在未来 API 变化时更容易调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestEnhancedInput)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestEnhancedInput/Source/CQTestEnhancedInputTests)