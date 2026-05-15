# Automation Test Toolset

> Automation test discovery and execution tools.

| 属性 | 值 |
|---|---|
| 中文名 | 自动化测试工具集 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomationTestToolset` (Editor), `AutomationTestToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset) | |

## 用途

该插件的核心是为 AI 助手（如 LLM）提供一套标准化的工具（Toolset），用于在编辑器内发现、选择和执行自动化测试。它解决的核心问题是：让 AI 能够像开发者一样，通过函数调用（Tool Call）与 UE 编辑器的自动化测试系统进行交互，从而在持续集成（CI）或 AI 辅助开发流程中自动运行测试、诊断失败原因。

## 使用场景

-   **AI 驱动的 CI/CD**：在自动化流水线中，AI 助手可以使用 `DiscoverTests` 初始化测试环境，通过 `ListTests` 过滤出需要运行的测试，调用 `RunTests` 执行，并使用 `GetTestStatus` 和 `GetTestResults` 轮询结果。
-   **AI 辅助开发与调试**：开发者可以口头指示 AI 助手“运行所有与玩家移动相关的测试”，AI 助手内部会调用该插件提供的工具来执行命令并反馈结果。
-   **自动化测试管理**：提供结构化的 JSON 数据，便于外部脚本或工具解析测试列表和结果，用于生成报告或触发后续流程。

## 蓝图用法

此插件主要设计用于被其他插件（如 ToolsetRegistry）的工具函数封装，但其核心功能也通过 `UFUNCTION(BlueprintCallable)` 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DiscoverTests` | 初始化测试发现会话（异步，首次调用约15秒） | `UAutomationTestController` |
| `ListTests` | 返回按名称和标签过滤的测试路径列表（JSON） | `UAutomationTestController` |
| `RunTests` | 异步执行指定的测试，完成后返回结果（JSON） | `UAutomationTestController` |
| `RunTestsByFilter` | 根据过滤条件快速批量选择并运行测试 | `UAutomationTestController` |
| `GetTestStatus` | 轮询当前测试执行控制器的状态 | `UAutomationTestController` |
| `GetTestResults` | 获取详细的结果，包含每个测试的错误和警告 | `UAutomationTestController` |
| `StopTests` | 中止正在运行的测试 | `UAutomationTestController` |

### 使用示例（蓝图描述）

1.  **获取测试列表**：
    -   调用 `DiscoverTests` 节点，并连接一个 `Delay` 节点等待约15秒。
    -   之后调用 `ListTests` 节点，设置 `NameFilter` (如 “Player.”）和 `Limit` (如 10)。
    -   将输出的 `TestPaths` (FString) 节点连接到 `Print String` 或解析节点，即可看到 JSON 格式的测试路径列表。

2.  **运行并检查结果**：
    -   先调用 `ListTests` 获取一个测试名称。
    -   创建一个 `String` 数组，填入测试名称。
    -   调用 `RunTests` 节点，输入该数组。
    -   使用 `While` 循环配合 `Delay` 和 `GetTestStatus` 节点轮询状态。
    -   当状态指示完成后，调用 `GetTestResults` 获取详细结果。

## C++ 用法

### 头文件引入

```cpp
#include "AutomationTestController.h"
```

### 基本用法

来自测试用例的典型用法，展示如何初始化和获取测试列表。

```cpp
// 假设在一个 EditorSubsystem 或类似的上下文中
#include "AutomationTestController.h"

void RunAutomationWorkflow()
{
    // 1. 获取全局唯一的测试控制器实例
    UAutomationTestController* TestController = UAutomationTestController::Get();

    // 2. 初始化发现会话 (这是异步的，首次调用需要等待)
    TestController->DiscoverTests();

    // 3. 等待发现完成 (实际使用中需要轮询或回调，此处为示意)
    // FPlatformProcess::Sleep(15.0f);

    // 4. 获取过滤后的测试列表
    const FString Filter = TEXT("MyGame.");
    const int32 Limit = 50;
    FString JsonTestPaths = TestController->ListTests(Filter, TEXT(""), Limit);

    // 解析 JSON 字符串获取测试名称数组...
    // 例如：TArray<FString> TestNames = ParseTestPathsFromJson(JsonTestPaths);
}
```
**来源**: 推断自 `AutomationTestController` 的公共接口和 `AutomationTestToolsetTests` 的测试逻辑。

### 进阶用法

结合 `RunTests` 和状态轮询的完整流程。

```cpp
void RunAndMonitorTests(const TArray<FString>& TestNames)
{
    UAutomationTestController* Controller = UAutomationTestController::Get();

    // 1. 异步启动测试
    Controller->RunTests(TestNames);

    // 2. 轮询状态直到完成
    while (true)
    {
        FString StatusJson = Controller->GetTestStatus();
        // 解析 StatusJson，检查状态字段
        if (/* 状态为 Completed 或 Failed */)
        {
            break;
        }
        FPlatformProcess::Sleep(1.0f); // 避免过于频繁的轮询
    }

    // 3. 获取详细结果
    FString ResultsJson = Controller->GetTestResults();
    // 解析 ResultsJson 获取每个测试的通过状态、错误信息、日志等
}
```
**来源**: 综合自工具函数的设计模式。

## Demo 示例

一个演示如何从 C++ 代码调用核心功能的最小示例。

```cpp
// MyTestRunner.h
#pragma once

#include "CoreMinimal.h"
#include "AutomationTestController.h"

class FMyTestRunner
{
public:
    void StartTestSession();
    void ExecuteFilteredTests(const FString& TestNameFilter);

private:
    TWeakObjectPtr<UAutomationTestController> TestController;
};

// MyTestRunner.cpp
#include "MyTestRunner.h"

void FMyTestRunner::StartTestSession()
{
    TestController = UAutomationTestController::Get();
    if (TestController.IsValid())
    {
        // 启动测试发现会话
        TestController->DiscoverTests();
        UE_LOG(LogTemp, Log, TEXT("Automation test discovery initiated. Please wait ~15 seconds."));
    }
}

void FMyTestRunner::ExecuteFilteredTests(const FString& TestNameFilter)
{
    if (!TestController.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Test controller is not available."));
        return;
    }

    // 1. 获取符合过滤条件的测试列表
    FString TestPathsJson = TestController->ListTests(TestNameFilter, TEXT(""), 100);
    // 注意：实际使用需要解析 JSON 字符串
    // TArray<FString> TestNames = ParseJsonToArray(TestPathsJson);
    TArray<FString> TestNames; // 伪代码，假设已解析

    if (TestNames.Num() > 0)
    {
        // 2. 运行这些测试
        UE_LOG(LogTemp, Log, TEXT("Running %d tests matching filter '%s'."), TestNames.Num(), *TestNameFilter);
        TestController->RunTests(TestNames);

        // 注意：这是一个简化的示例。真实的执行和结果检查是异步的，
        // 需要通过定时轮询 `GetTestStatus()` 和 `GetTestResults()` 来完成。
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No tests found matching the filter '%s'."), *TestNameFilter);
    }
}
```

## 模块依赖

从插件的 `.uplugin` 和 Build.cs 文件推断的依赖关系。

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 插件显式依赖的父插件，用于将本插件的函数注册为 AI 工具 |
| `AutomationController` | UE 内置的自动化测试执行框架核心模块 |
| `MessagingCommon`, `SessionServices`, `SourceControl` | 用于支持测试会话发现、通信及可能的源代码管理集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `675a8bed` | AutomationTestToolset: add RunTestsByFilter for fast batch test selection | 新增 `RunTestsByFilter` 工具，支持按条件快速批量选择测试 |
| 2026-04-30 | `bbe30475` | [ToolsetRegistry] Iterate Python automation tests without restarting the editor | 优化测试迭代流程，避免重启编辑器 |
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools | 调整工具函数识别逻辑，影响本插件的工具注册 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回退了一次提交 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 同上，工具识别逻辑的初次尝试 |

### 维护评价

该插件处于**活跃维护**状态。它创建于 2026 年 4 月，非常年轻（🆕），并在创建后的一个月内有多次功能性更新和优化（如新增 `RunTestsByFilter` 工具）。这些更新表明 Epic 的 AI 工具团队正在积极开发和完善它。

作为实验性插件（`IsExperimentalVersion=true`，`EnabledByDefault=false`），它旨在为特定的前沿工作流（AI 工具集成）提供解决方案，接口和稳定性可能随版本迭代而变化。目前看来，它是一个功能明确、更新及时的实验性工具，适合在受控的编辑器和 CI 环境中进行评估和试用，**推荐对 AI 驱动的自动化测试流程有明确需求的团队关注和试用**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset)
-   官方文档：无
-   测试用例：位于插件内的 `AutomationTestToolsetTests` 模块中