# AutomationTestToolset

> Automation test discovery and execution tools.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 自动化测试工具箱 |
| 分类 | Toolsets |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomationTestToolset` (Editor), `AutomationTestToolsetTests` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset) | |

## 用途

`AutomationTestToolset` 是一个为 **AI 助手 (MCP 客户端)** 设计的工具集插件。它并非传统的自动化测试框架，而是将 Unreal Engine 内部的 `IAutomationControllerManager` API（即 “Session Frontend” 窗口使用的同一后端）封装成一系列静态工具函数，并通过 `UToolsetRegistry` 暴露给 AI。

它解决的核心问题是：**让 AI 助手能够程序化地发现、筛选并执行引擎的自动化测试，并获取结构化 (JSON) 的测试结果**，从而实现自动化测试工作流的集成。

## 使用场景

- 你正在为 Unreal Engine 开发一个 AI 助手或 MCP 客户端，需要它能自动运行游戏或项目的测试套件。
- 你希望通过自然语言指令（如 “运行所有性能测试”）来触发测试，并获取易读的报告。
- 你需要将测试执行集成到 CI/CD 流程或持续集成管道的 AI 控制逻辑中。

## 蓝图用法

该插件的所有主要函数都标记了 `UFUNCTION(meta = (AICallable))`，意味着它们被设计为可被 AI 工具调用。在蓝图中，它们表现为静态函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DiscoverTests` | 初始化测试发现（异步），首次调用耗时较长，需等待完成。 | `UAutomationTestToolset` |
| `ListTests` | 根据名称或标签筛选可用测试，返回 JSON 列表。 | `UAutomationTestToolset` |
| `RunTests` | 通过测试名称列表运行指定的测试（异步）。 | `UAutomationTestToolset` |
| `RunTestsByFilter` | 通过表达式快速筛选并运行一批测试（异步，更高效）。 | `UAutomationTestToolset` |
| `GetTestStatus` | 获取自动化控制器的轻量级状态快照。 | `UAutomationTestToolset` |
| `GetTestResults` | 获取最近一次测试运行的详细结果。 | `UAutomationTestToolset` |
| `StopTests` | 停止所有正在运行的测试。 | `UAutomationTestToolset` |

### 使用示例（蓝图描述）

一个典型的蓝图工作流如下：
1. 调用 `DiscoverTests` 节点，获取其返回的 `UToolCallAsyncResultString*`，并使用 `Delay` 或 `AsyncTask` 等待其完成。
2. 成功后，调用 `ListTests` 并可传入 `NameFilter` (如 “System.Engine”) 来查看可用测试。
3. 将 `ListTests` 返回的 JSON 字符串解析后，取出测试路径数组。
4. 将测试路径数组传给 `RunTests` 节点，获取新的异步结果对象。
5. 等待 `RunTests` 的异步结果完成，或使用 `GetTestStatus` 节点进行轮询。
6. 最后，调用 `GetTestResults` 节点获取详细的 JSON 格式结果报告。

## C++ 用法

### 头文件引入

```cpp
#include "AutomationTestToolset.h"
```

### 基本用法

以下示例展示了如何通过 C++ 使用该工具集来运行测试。来源：基于 `UAutomationTestToolset` 的公开 API 构造。

```cpp
// 1. 首先初始化并等待测试发现完成
UToolCallAsyncResultString* DiscoveryResult = UAutomationTestToolset::DiscoverTests();
// 通常需要将此对象绑定到一个委托，以在异步操作完成时收到通知。
// 例如：DiscoveryResult->OnCompleted.AddDynamic(this, &UMyClass::OnTestsDiscovered);

// 2. 在 OnTestsDiscovered 回调中，列出并运行测试
void UMyClass::OnTestsDiscovered(const FString& ResultJson)
{
    if (!ResultJson.IsEmpty()) // 假设成功
    {
        // 列出测试
        FString TestListJson = UAutomationTestToolset::ListTests(TEXT("MySuite"));

        // 解析 JSON 数组获取测试名称（示例，需自行实现 JSON 解析）
        TArray<FString> TestNames = /* ... Parse TestListJson ... */;

        // 3. 运行测试
        UToolCallAsyncResultString* RunResult = UAutomationTestToolset::RunTests(TestNames);
        RunResult->OnCompleted.AddDynamic(this, &UMyClass::OnTestsCompleted);
    }
}

// 4. 获取结果
void UMyClass::OnTestsCompleted(const FString& ResultJson)
{
    FString DetailedResults = UAutomationTestToolset::GetTestResults();
    UE_LOG(LogTemp, Log, TEXT("Test Results:\n%s"), *DetailedResults);
}
```

### 进阶用法

使用 `RunTestsByFilter` 进行高效的批量测试，这是推荐的方式，尤其是在测试用例数量庞大时。

```cpp
// 使用过滤表达式直接运行测试，无需先列出再筛选
UToolCallAsyncResultString* FilterRunResult = UAutomationTestToolset::RunTestsByFilter(
    TEXT("StartsWith:System.Engine+Group:Smoke") // 运行所有 System.Engine 开头且属于 Smoke 组的测试
);
FilterRunResult->OnCompleted.AddDynamic(this, &UMyClass::OnTestsCompleted);
```

## Demo 示例

一个最小的、可运行的控制台命令示例，展示完整流程。

```cpp
// MyTestRunner.h
#pragma once
#include "CoreMinimal.h"
#include "AutomationTestToolset.h"
#include "MyTestRunner.generated.h"

UCLASS()
class UMyTestRunner : public UObject
{
    GENERATED_BODY()
public:
    void RunSampleTests();
private:
    UFUNCTION()
    void OnDiscoveryComplete(const FString& Result);

    UFUNCTION()
    void OnRunComplete(const FString& Result);
};
```

```cpp
// MyTestRunner.cpp
#include "MyTestRunner.h"
#include "Misc/DefaultValueHelper.h"

void UMyTestRunner::RunSampleTests()
{
    // 第一步：发现测试
    UToolCallAsyncResultString* Discovery = UAutomationTestToolset::DiscoverTests();
    if (Discovery)
    {
        Discovery->OnCompleted.AddDynamic(this, &UMyTestRunner::OnDiscoveryComplete);
        UE_LOG(LogTemp, Warning, TEXT("Test discovery started..."));
    }
}

void UMyTestRunner::OnDiscoveryComplete(const FString& Result)
{
    UE_LOG(LogTemp, Warning, TEXT("Discovery complete: %s"), *Result);

    // 第二步：筛选并运行测试
    FString Filter = TEXT("StartsWith:System.Engine.Automation");
    UToolCallAsyncResultString* RunTask = UAutomationTestToolset::RunTestsByFilter(Filter);
    if (RunTask)
    {
        RunTask->OnCompleted.AddDynamic(this, &UMyTestRunner::OnRunComplete);
        UE_LOG(LogTemp, Warning, TEXT("Running tests matching filter: %s"), *Filter);
    }
}

void UMyTestRunner::OnRunComplete(const FString& Result)
{
    UE_LOG(LogTemp, Warning, TEXT("Test run completed."));
    // 第三步：获取并显示详细结果
    FString DetailedResults = UAutomationTestToolset::GetTestResults();
    UE_LOG(LogTemp, Warning, TEXT("Detailed Results:\n%s"), *DetailedResults);
}

// 在其他地方（如一个自定义的控制台命令）调用：
// UMyTestRunner* Runner = NewObject<UMyTestRunner>();
// Runner->RunSampleTests();
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供 `UToolsetDefinition` 基类和注册机制，是此插件作为 AI 工具集的基础。 |
| `AutomationController` | 提供 `IAutomationControllerManager` 核心接口，用于发现、管理和运行自动化测试。 |
| `SessionServices` | 用于发现本地编辑器会话和自动化工作者。 |
| `MessagingCommon` | 会话管理系统的依赖项。 |
| `Serialization` | 用于构建 JSON 结果字符串。 |

**注意**：此插件还隐式依赖于引擎核心模块，如 `Core`, `CoreUObject`, `Engine`，但根据规范，这些常见依赖不再列出。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `675a8bed` | AutomationTestToolset: add RunTestsByFilter for fast batch test selection | 添加了 `RunTestsByFilter` 函数，实现通过表达式快速筛选运行测试。 |
| 2026-04-30 | `bbe30475` | [ToolsetRegistry] Iterate Python automation tests without restarting the editor | 支持在不重启编辑器的情况下迭代 Python 自动化测试。 |
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 改变了工具集定义判定哪些 UFunction 为工具的方法。 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回滚了一次提交（CL52878047）。 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 早期关于工具判定方法的修改（后被部分回滚）。 |

### 维护评价

- **创建时间**：插件非常新，创建于 2026 年 4 月。
- **活跃度**：最近一个月内有多次提交，包括重要的功能添加（`RunTestsByFilter`）和 API 调整，表明**处于活跃开发阶段**。
- **状态**：插件标记为 `IsExperimentalVersion = true` 且 `EnabledByDefault = false`，这明确说明它是实验性的，接口和功能未来可能发生变化。
- **推荐**：由于其**实验性质**和**较短的生命周期**，目前不建议在生产环境中作为关键依赖。但它对于构建实验性的 AI 辅助测试工作流具有明确价值，值得保持关注和尝试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset)
- 官方文档：暂无
- 测试用例：位于插件自身的 `AutomationTestToolsetTests` 模块中，包含 9 个基于 CQTest 的测试。