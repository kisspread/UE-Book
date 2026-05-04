# TestSamples

> 测试框架事件回调示例插件，展示如何监听 Automation Test Framework 的生命周期事件。

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | TestSamples (Editor) |
| 创建时间 | 2021-12-01 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/TestSamples) | |

## 用途

TestSamples 是一个纯示例/模板插件，演示如何通过 `FAutomationTestFramework` 的事件委托系统来监听测试执行的各个阶段。它不提供任何实际的测试功能，而是作为开发者编写自定义测试基础设施时的参考实现。

核心价值：如果你想在测试运行前做环境准备、测试运行后做清理、或在特定测试节进入/退出时执行额外逻辑，这个插件展示了标准的实现模式。

## 使用场景

- 你需要在自动化测试运行前初始化自定义测试环境（如启动外部服务、准备数据库连接）→ 参考 `OnBeforeAllTests` 回调
- 你需要在所有测试完成后做全局清理（如删除临时文件、重置全局状态）→ 参考 `OnAfterAllTests` 回调
- 你需要追踪每个测试用例的开始和结束（如自定义日志、性能计时）→ 参考 `OnTestStart`/`OnTestEnd` 回调
- 你需要对特定测试分组执行前置/后置逻辑 → 参考 `OnEnteringTestSection`/`OnLeavingTestSection` 回调

## 蓝图用法

此插件不暴露任何蓝图接口。它是纯 C++ 模块，功能通过 `FAutomationTestFramework` 事件委托实现。

## C++ 用法

### 头文件引入

```cpp
#include "Misc/AutomationTest.h"
#include "Modules/ModuleInterface.h"
```

### 基本用法：监听测试生命周期事件

TestSamples 展示了 `FAutomationTestFramework` 提供的三类事件：

**1. 全局测试批事件（Before/After All Tests）**

```cpp
// 来源: Engine/Plugins/Tests/TestSamples/Source/TestSamples/Private/TestSamples.cpp

// 注册回调 — 在 StartupModule() 中
FAutomationTestFramework::Get().OnBeforeAllTestsEvent.AddRaw(
    this, &FMyModule::OnBeforeAllTests);
FAutomationTestFramework::Get().OnAfterAllTestsEvent.AddRaw(
    this, &FMyModule::OnAfterAllTests);

// 回调实现
void FMyModule::OnBeforeAllTests()
{
    UE_LOG(LogMyModule, Log, TEXT("Start running tests"));
}

void FMyModule::OnAfterAllTests()
{
    UE_LOG(LogMyModule, Log, TEXT("Running tests completed"));
}
```

**2. 单个测试事件（Test Start/End）**

```cpp
// 注册回调
FAutomationTestFramework::Get().OnTestStartEvent.AddRaw(
    this, &FMyModule::OnTestStart);
FAutomationTestFramework::Get().OnTestEndEvent.AddRaw(
    this, &FMyModule::OnTestEnd);

// 回调实现 — 接收 FAutomationTestBase* 参数
void FMyModule::OnTestStart(FAutomationTestBase* Test)
{
    if (Test != nullptr)
    {
        UE_LOG(LogMyModule, Verbose, TEXT("Starting test: %s"),
            *Test->GetTestFullName());
    }
}
```

**3. 测试节事件（Test Section Enter/Leave）**

```cpp
// 注册回调 — 需要指定节名称
FAutomationTestFramework::Get().GetOnEnteringTestSection(TEXT("TestFramework"))
    .AddRaw(this, &FMyModule::OnEnteringTestSection);
FAutomationTestFramework::Get().GetOnLeavingTestSection(TEXT("TestFramework"))
    .AddRaw(this, &FMyModule::OnLeavingTestSection);

// 回调实现
void FMyModule::OnEnteringTestSection(const FString& Section)
{
    UE_LOG(LogMyModule, Verbose, TEXT("Entering section %s"), *Section);
}
```

### 进阶用法：清理回调

所有注册的回调都应在 `ShutdownModule()` 中清理，防止悬挂指针：

```cpp
// 来源: Engine/Plugins/Tests/TestSamples/Source/TestSamples/Private/TestSamples.cpp

void FTestSamplesModule::ShutdownModule()
{
    FAutomationTestFramework::Get().OnTestStartEvent.RemoveAll(this);
    FAutomationTestFramework::Get().OnTestEndEvent.RemoveAll(this);
    FAutomationTestFramework::Get().OnBeforeAllTestsEvent.RemoveAll(this);
    FAutomationTestFramework::Get().OnAfterAllTestsEvent.RemoveAll(this);
    FAutomationTestFramework::Get().GetOnEnteringTestSection(TEXT("TestFramework"))
        .RemoveAll(this);
    FAutomationTestFramework::Get().GetOnLeavingTestSection(TEXT("TestFramework"))
        .RemoveAll(this);
}
```

> **注意**：`GetOnEnteringTestSection` 和 `GetOnLeavingTestSection` 接受一个 `FString` 参数来指定节名称。节名称对应测试的层级路径，例如测试 `MyTest.Log.Validation.TestTrue` 会在 `MyTest`、`MyTest.Log`、`MyTest.Log.Validation` 三个节分别触发事件。

## Demo 示例

以下是一个完整的自定义模块示例，使用 TestSamples 展示的模式来实现测试计时功能：

### MyTestTimer.Build.cs

```csharp
using UnrealBuildTool;

public class MyTestTimer : ModuleRules
{
    public MyTestTimer(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
        });

        PrivateDependencyModuleNames.AddRange(new string[] {
            "Engine",
        });
    }
}
```

### MyTestTimer.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"
#include "Misc/AutomationTest.h"

class FMyTestTimerModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnTestStart(FAutomationTestBase* Test);
    void OnTestEnd(FAutomationTestBase* Test);

    double CurrentTestStartTime = 0.0;
};
```

### MyTestTimer.cpp

```cpp
#include "MyTestTimer.h"
#include "Misc/AutomationTest.h"
#include "Modules/ModuleManager.h"

DEFINE_LOG_CATEGORY_STATIC(LogMyTestTimer, Log, All);

void FMyTestTimerModule::StartupModule()
{
    FAutomationTestFramework::Get().OnTestStartEvent.AddRaw(
        this, &FMyTestTimerModule::OnTestStart);
    FAutomationTestFramework::Get().OnTestEndEvent.AddRaw(
        this, &FMyTestTimerModule::OnTestEnd);
}

void FMyTestTimerModule::ShutdownModule()
{
    FAutomationTestFramework::Get().OnTestStartEvent.RemoveAll(this);
    FAutomationTestFramework::Get().OnTestEndEvent.RemoveAll(this);
}

void FMyTestTimerModule::OnTestStart(FAutomationTestBase* Test)
{
    if (Test != nullptr)
    {
        CurrentTestStartTime = FPlatformTime::Seconds();
        UE_LOG(LogMyTestTimer, Log, TEXT("⏱️ Started: %s"),
            *Test->GetTestFullName());
    }
}

void FMyTestTimerModule::OnTestEnd(FAutomationTestBase* Test)
{
    if (Test != nullptr)
    {
        double Elapsed = FPlatformTime::Seconds() - CurrentTestStartTime;
        UE_LOG(LogMyTestTimer, Log, TEXT("⏱️ Finished: %s (%.3f sec)"),
            *Test->GetTestFullName(), Elapsed);
    }
}

IMPLEMENT_MODULE(FMyTestTimerModule, MyTestTimer)
```

> **注意**：这是一个 Editor 模块（模块类型需在 `.uplugin` 中设置 `"Type": "Editor"`），因为它依赖 `FAutomationTestFramework`，该框架主要在编辑器环境下使用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、日志系统 |
| `CoreUObject` | UObject 基础设施 |
| `Engine` | 引擎核心（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-11-01 | `4dcbf3ce0c4f` | 引入 OnEnteringTestSectionEvent、OnLeavingTestSectionEvent | 新增测试节进入/退出事件支持，扩展了插件展示的事件类型 |
| 2023-07-24 | `6f6f3510002c` | 实现 OnBeforeAllTestsEvent 和 OnAfterAllTestsEvent | 新增全局测试批前后事件，插件作为这些事件的参考实现 |
| 2023-01-16 | `bbc37aa2f5e6` | IWYU 头文件清理 | 编译优化，无功能变化 |

### 维护评价

- **创建时间**：2021-12-01，约 4.4 年历史
- **更新模式**：被动更新 — 仅在 `FAutomationTestFramework` 添加新事件时同步更新
- **最后实质性更新**：2023-11-01，超过 2 年前
- **性质**：这是一个 **示例/模板插件**，不是功能型插件。代码量极小（仅 1 个模块、2 个源文件），功能完全依赖 `FAutomationTestFramework`
- **状态**：功能完整，不太可能有频繁更新，因为展示的事件 API 已经稳定
- **推荐**：✅ 作为学习测试框架事件系统的参考，或直接复制代码到自己的项目中使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/TestSamples)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/TestSamples/Source)（本插件本身就是示例代码，无单独测试）
