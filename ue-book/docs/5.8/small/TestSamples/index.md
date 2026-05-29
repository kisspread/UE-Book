# Test Samples

>

| 属性 | 值 |
|---|---|
| 中文名 | 测试示例 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TestSamples` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-12-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/TestSamples) | |

## 用途

TestSamples 是 Epic 官方提供的**自动化测试框架事件订阅示例插件**。它不提供面向游戏的功能，而是展示如何在插件中挂接 `FAutomationTestFramework` 的生命周期事件（测试开始/结束、所有测试开始/结束、进入/离开测试章节等）。

这个插件解决的问题是：开发者不知道如何在自己的插件中订阅自动化测试的回调事件。TestSamples 作为一个最小可运行的示例，演示了正确的注册和注销模式。

## 使用场景

- 你正在开发一个编辑器插件，需要在自动化测试运行前后执行自定义逻辑（如重置环境状态、收集额外指标）
- 你想了解 UE5 AutomationTestFramework 的事件系统如何工作
- 你在编写自定义测试工具，需要在每个测试用例的开始/结束时做记录

## 蓝图用法

无蓝图接口。本插件是纯 C++ 模块，不暴露任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。

## C++ 用法

### 头文件引入

```cpp
#include "TestSamples.h"
```

### 基本用法

本插件的核心代码展示如何在模块的 `StartupModule` / `ShutdownModule` 中订阅自动化测试框架事件。

**源文件**: `Engine/Plugins/Tests/TestSamples/TestSamples.h`

```cpp
// 获取自动化测试框架单例
FAutomationTestFramework& Framework = FAutomationTestFramework::Get();

// 订阅"所有测试开始前"事件
Framework.OnBeforeAllTestsEvent.AddRaw(this, &FTestSamplesModule::OnBeforeAllTests);

// 订阅"所有测试结束后"事件
Framework.OnAfterAllTestsEvent.AddRaw(this, &FTestSamplesModule::OnAfterAllTests);

// 订阅单个测试开始/结束事件
Framework.OnTestStartEvent.AddRaw(this, &FTestSamplesModule::OnTestStart);
Framework.OnTestEndEvent.AddRaw(this, &FTestSamplesModule::OnTestEnd);

// 订阅测试章节进入/离开事件
Framework.OnEnteringTestSectionEvent.AddRaw(this, &FTestSamplesModule::OnEnteringTestSection);
Framework.OnLeavingTestSectionEvent.AddRaw(this, &FTestSamplesModule::OnLeavingTestSection);
```

### 回调签名说明

| 事件 | 回调签名 |
|---|---|
| `OnBeforeAllTestsEvent` | `void()` |
| `OnAfterAllTestsEvent` | `void()` |
| `OnTestStartEvent` | `void(FAutomationTestBase* Test)` |
| `OnTestEndEvent` | `void(FAutomationTestBase* Test)` |
| `OnEnteringTestSectionEvent` | `void(const FString& Section)` |
| `OnLeavingTestSectionEvent` | `void(const FString& Section)` |

## Demo 示例

一个完整的、可编译的最小模块示例，展示如何在自定义插件中订阅测试事件：

### TestEventSubscriberModule.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FAutomationTestBase;

class FTestEventSubscriberModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnBeforeAllTests();
    void OnAfterAllTests();
    void OnTestStart(FAutomationTestBase* Test);
    void OnTestEnd(FAutomationTestBase* Test);
    void OnEnteringTestSection(const FString& Section);
    void OnLeavingTestSection(const FString& Section);
};
```

### TestEventSubscriberModule.cpp

```cpp
#include "TestEventSubscriberModule.h"
#include "Misc/AutomationTest.h"

#define LOCTEXT_NAMESPACE "TestEventSubscriber"

void FTestEventSubscriberModule::StartupModule()
{
    // 仅在编辑器环境中订阅测试事件
#if WITH_EDITOR
    FAutomationTestFramework& Framework = FAutomationTestFramework::Get();

    Framework.OnBeforeAllTestsEvent.AddRaw(this, &FTestEventSubscriberModule::OnBeforeAllTests);
    Framework.OnAfterAllTestsEvent.AddRaw(this, &FTestEventSubscriberModule::OnAfterAllTests);
    Framework.OnTestStartEvent.AddRaw(this, &FTestEventSubscriberModule::OnTestStart);
    Framework.OnTestEndEvent.AddRaw(this, &FTestEventSubscriberModule::OnTestEnd);
    Framework.OnEnteringTestSectionEvent.AddRaw(this, &FTestEventSubscriberModule::OnEnteringTestSection);
    Framework.OnLeavingTestSectionEvent.AddRaw(this, &FTestEventSubscriberModule::OnLeavingTestSection);
#endif
}

void FTestEventSubscriberModule::ShutdownModule()
{
#if WITH_EDITOR
    FAutomationTestFramework& Framework = FAutomationTestFramework::Get();

    Framework.OnBeforeAllTestsEvent.RemoveAll(this);
    Framework.OnAfterAllTestsEvent.RemoveAll(this);
    Framework.OnTestStartEvent.RemoveAll(this);
    Framework.OnTestEndEvent.RemoveAll(this);
    Framework.OnEnteringTestSectionEvent.RemoveAll(this);
    Framework.OnLeavingTestSectionEvent.RemoveAll(this);
#endif
}

void FTestEventSubscriberModule::OnBeforeAllTests()
{
    UE_LOG(LogTemp, Log, TEXT("=== 所有测试即将开始 ==="));
}

void FTestEventSubscriberModule::OnAfterAllTests()
{
    UE_LOG(LogTemp, Log, TEXT("=== 所有测试已完成 ==="));
}

void FTestEventSubscriberModule::OnTestStart(FAutomationTestBase* Test)
{
    if (Test)
    {
        UE_LOG(LogTemp, Log, TEXT("测试开始: %s"), *Test->GetTestFullName());
    }
}

void FTestEventSubscriberModule::OnTestEnd(FAutomationTestBase* Test)
{
    if (Test)
    {
        UE_LOG(LogTemp, Log, TEXT("测试结束: %s"), *Test->GetTestFullName());
    }
}

void FTestEventSubscriberModule::OnEnteringTestSection(const FString& Section)
{
    UE_LOG(LogTemp, Log, TEXT("进入测试章节: %s"), *Section);
}

void FTestEventSubscriberModule::OnLeavingTestSection(const FString& Section)
{
    UE_LOG(LogTemp, Log, TEXT("离开测试章节: %s"), *Section);
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FTestEventSubscriberModule, TestEventSubscriber)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。本插件仅使用 `FAutomationTestFramework`，该类位于 `Runtime/Core` 模块的 `Misc/AutomationTest.h` 中。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移为新的 UE_LOGF 格式 |
| 2023-11-01 | `4dcbf3ce` | Introduce OnEnteringTestSectionEvent, OnLeavingTestSectionEvent | 新增测试章节进入/离开事件 |
| 2023-07-24 | `6f6f3510` | Implement OnBeforeAllTestsEvent and OnAfterAllTestsEvent in FAutomationTestFramework | 新增所有测试开始/结束事件 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录批量调整 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新链接为 HTTPS 协议 |

### 维护评价

- **创建时间**: 2021-12-01，约 4 年前
- **更新频率**: 低频更新，主要是跟随 AutomationTestFramework 的新事件添加而同步更新示例代码
- **维护状态**: 维护中 — 最近一次更新在 2026 年，但属于被动维护（跟随框架改动）
- **定位**: 这是一个**示例/参考插件**，不是面向最终用户的功能插件
- **是否推荐使用**: ✅ 如果你需要了解 AutomationTestFramework 事件系统的用法，这是官方最佳参考；但不要作为游戏功能依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/TestSamples)
- [AutomationTestFramework 源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Source/Runtime/Core/Public/Misc/AutomationTest.h)