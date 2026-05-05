# AutomationTestToolset

> Automation test discovery and execution tools.

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomationTestToolset` (Editor), `AutomationTestToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset) | |

## 用途

`AutomationTestToolset` 是一个面向 AI 代理（MCP 客户端）的工具集插件。它封装了 Unreal Engine 的 `IAutomationControllerManager` API（即“会话前端”自动化测试面板的后端），提供了一组简单的函数，允许外部程序（如 AI 助手）以编程方式发现、列出、运行和监控编辑器中的自动化测试。

**核心解决的问题**：为 AI 代理提供一个标准化的接口，使其能够自主地与引擎的自动化测试系统交互，从而实现智能测试选择、执行和结果分析。

## 使用场景

- **AI 驱动的测试执行**：你正在开发一个 AI 助手，需要它能够根据代码变更或特定需求，自动选择并运行相关的自动化测试。
- **持续集成增强**：在 CI/CD 流程中，希望有一个智能层能够动态决定运行哪些测试，而不是运行全部测试。
- **测试探索与调试**：通过 AI 代理快速查询可用的测试列表，或获取特定测试的详细结果，辅助开发者进行调试。

## 蓝图用法

该插件的所有核心功能都通过 `UAutomationTestToolset` 类的静态函数暴露，这些函数均标记为 `BlueprintCallable`，可在蓝图中直接调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DiscoverTests` | 初始化自动化工作器并加载测试列表。必须首先调用，返回异步结果。 | `UAutomationTestToolset` |
| `ListTests` | 列出可用的自动化测试，支持按名称和标签过滤。 | `UAutomationTestToolset` |
| `RunTests` | 运行一组指定的测试，返回异步结果。 | `UAutomationTestToolset` |
| `GetTestResults` | 获取当前或最近一次测试运行的详细结果（JSON格式）。 | `UAutomationTestToolset` |
| `GetTestStatus` | 获取自动化控制器的轻量级状态快照。 | `UAutomationTestToolset` |
| `StopTests` | 停止所有正在运行的测试。 | `UAutomationTestToolset` |

### 使用示例（蓝图描述）

1.  **初始化**：在开始任何测试操作前，调用 `DiscoverTests` 节点。该节点返回一个 `UToolCallAsyncResultString` 对象，你需要将其连接到一个“等待异步操作”节点（如 `Wait for Async Action`），并处理其完成回调。
2.  **查询测试**：在 `DiscoverTests` 成功完成后，调用 `ListTests` 节点。你可以传入 `NameFilter`（如 “MyGame”）和 `TagFilter`（如 “Smoke”）来筛选测试。节点将返回一个 JSON 字符串，包含匹配的测试路径列表。
3.  **执行测试**：从 `ListTests` 返回的 JSON 中解析出测试路径数组，将其作为 `TestNames` 参数传入 `RunTests` 节点。同样，该节点返回一个异步结果，你需要等待其完成以获取最终的测试结果摘要。
4.  **监控与停止**：在测试运行期间，可以随时调用 `GetTestStatus` 查看进度。如果需要中止，调用 `StopTests`。

## C++ 用法

### 头文件引入

```cpp
#include "AutomationTestToolset.h"
```

### 基本用法

以下代码展示了如何使用该插件的核心工作流。由于缺乏具体的测试用例，示例基于头文件中的函数签名和注释构建。

```cpp
// 假设在一个编辑器工具或子系统中
#include "AutomationTestToolset.h"
#include "ToolsetRegistry/ToolCallAsyncResultString.h"

void FMyTestRunner::StartTestDiscovery()
{
    // 1. 开始发现测试
    UToolCallAsyncResultString* DiscoveryFuture = UAutomationTestToolset::DiscoverTests();
    
    // 绑定完成回调
    DiscoveryFuture->OnCompleted.AddLambda([this](const FString& ResultJson, bool bSuccess)
    {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Test discovery succeeded: %s"), *ResultJson);
            // 发现成功后，可以开始列出测试
            ListAvailableTests();
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Test discovery failed: %s"), *ResultJson);
        }
    });
}

void FMyTestRunner::ListAvailableTests()
{
    // 2. 列出所有包含“Unit”标签的测试
    FString TestListJson = UAutomationTestToolset::ListTests(TEXT(""), TEXT("Unit"), 50);
    // 解析 TestListJson 以获取测试路径数组...
}

void FMyTestRunner::RunSpecificTests(const TArray<FString>& TestPaths)
{
    // 3. 运行指定的测试
    UToolCallAsyncResultString* RunFuture = UAutomationTestToolset::RunTests(TestPaths);
    
    RunFuture->OnCompleted.AddLambda([this](const FString& ResultJson, bool bSuccess)
    {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Test run completed. Results: %s"), *ResultJson);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Test run finished with issues: %s"), *ResultJson);
        }
    });
}
```

### 进阶用法

结合状态查询和停止功能，实现更健壮的测试控制。

```cpp
void FMyTestRunner::MonitorAndPotentiallyStopTests()
{
    // 在测试运行期间轮询状态
    FString StatusJson = UAutomationTestToolset::GetTestStatus();
    // 解析 StatusJson，检查完成百分比或失败数...
    
    // 如果满足某个条件（例如失败率过高），则停止测试
    if (ShouldStopTests())
    {
        bool bStopIssued = UAutomationTestToolset::StopTests();
        if (bStopIssued)
        {
            UE_LOG(LogTemp, Warning, TEXT("Stop request issued for running tests."));
        }
    }
    
    // 获取详细结果（可能在测试完成后调用）
    FString DetailedResultsJson = UAutomationTestToolset::GetTestResults();
    // 解析并处理每个测试的详细错误、警告和耗时...
}
```

## Demo 示例

一个最小的编辑器工具类，演示如何集成 `AutomationTestToolset`。

**MyTestRunnerTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyTestRunnerTool.generated.h"

class UToolCallAsyncResultString;

UCLASS(BlueprintType)
class UMyTestRunnerTool : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "TestRunner")
    void RunAllSmokeTests();

private:
    void OnDiscoveryComplete(const FString& ResultJson, bool bSuccess);
    void OnTestsRunComplete(const FString& ResultJson, bool bSuccess);

    UPROPERTY()
    TObjectPtr<UToolCallAsyncResultString> PendingDiscovery;
    
    UPROPERTY()
    TObjectPtr<UToolCallAsyncResultString> PendingRun;
};
```

**MyTestRunnerTool.cpp**
```cpp
#include "MyTestRunnerTool.h"
#include "AutomationTestToolset.h"
#include "ToolsetRegistry/ToolCallAsyncResultString.h"

void UMyTestRunnerTool::RunAllSmokeTests()
{
    PendingDiscovery = UAutomationTestToolset::DiscoverTests();
    if (PendingDiscovery)
    {
        PendingDiscovery->OnCompleted.AddDynamic(this, &UMyTestRunnerTool::OnDiscoveryComplete);
    }
}

void UMyTestRunnerTool::OnDiscoveryComplete(const FString& ResultJson, bool bSuccess)
{
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("Discovery failed: %s"), *ResultJson);
        return;
    }

    // 列出所有带“Smoke”标签的测试
    FString TestListJson = UAutomationTestToolset::ListTests(TEXT(""), TEXT("Smoke"));
    
    // 简单解析：假设返回格式为 {"tests": ["Path1", "Path2"], ...}
    // 实际项目中应使用 JSON 解析库
    TArray<FString> TestNames;
    // ... 解析 TestListJson 到 TestNames ...
    
    if (!TestNames.IsEmpty())
    {
        PendingRun = UAutomationTestToolset::RunTests(TestNames);
        if (PendingRun)
        {
            PendingRun->OnCompleted.AddDynamic(this, &UMyTestRunnerTool::OnTestsRunComplete);
        }
    }
}

void UMyTestRunnerTool::OnTestsRunComplete(const FString& ResultJson, bool bSuccess)
{
    UE_LOG(LogTemp, Display, TEXT("Smoke tests finished. Success: %s, Details: %s"),
        bSuccess ? TEXT("Yes") : TEXT("No"), *ResultJson);
    // 清理引用
    PendingRun = nullptr;
}
```

## 模块依赖

从 `AutomationTestToolset.Build.cs` 分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供 `UToolsetDefinition` 基类和 `UToolCallAsyncResultString` 等工具集注册与异步通信框架。 |
| `AutomationController` | 提供 `IAutomationControllerManager` 接口，用于与引擎的自动化测试后端通信。 |

## 维护状态

### 近期更新

- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-17 `8c911af5` [Backout] - CL52878047
- 2026-04-17 `9404cd3e` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-14 `b391684d` [AutomationTestToolset] Guard `HandleTestsRefreshed` filter reset behind `bDiscoveryRequested`.
- 2026-04-13 `73b95c3f` [AutomationTestToolset] Move `AutomationTestToolset` tests from `Editor` to `AI.Toolsets` category.

### 维护评价

- **年龄与状态**：这是一个全新的（约 0 年）、实验性的插件，标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`。
- **功能定位**：它服务于一个非常特定的场景——为 AI 代理提供测试控制接口，属于前沿探索性功能。
- **风险与建议**：
    - **高风险**：作为实验性功能，其 API 可能不稳定，随时可能发生重大变更或被移除。
    - **依赖性强**：深度依赖于 `ToolsetRegistry` 和 `AutomationController` 等内部模块，这些模块本身也可能处于变化中。
    - **不推荐生产使用**：目前仅适用于研究、原型开发或内部工具链集成。不建议在需要长期稳定性的项目中依赖此插件。
    - **建议**：密切关注引擎更新日志，关注其从“实验性”状态毕业或被废弃的公告。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset)
- [官方文档]() （暂无）
- [测试用例]() （插件内包含 `AutomationTestToolsetTests` 模块，但具体路径未提供）