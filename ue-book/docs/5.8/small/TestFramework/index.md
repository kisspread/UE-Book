# TestFramework

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 测试框架插件 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TestFramework` (DeveloperTool) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/TestFramework) | |

## 用途

TestFramework 插件并非一个功能性的运行时框架，而是作为 UE 引擎**自动化测试基础设施的补充和扩展模块**。它主要连接并增强 `EngineTest` 构建图，为引擎级的自动化测试提供更丰富的工具和功能支持，例如对测试日志的精细捕获与匹配，以及对延迟测试（Latent Test）和异步测试（Async Test）用例的补充覆盖。

## 使用场景

- 你是一名引擎或工具开发者，需要为引擎核心功能编写复杂的自动化测试。
- 你的测试需要验证特定日志消息的输出（错误、警告或自定义显示消息）。
- 你需要编写包含异步操作、等待或延迟步骤的测试用例。

## 蓝图用法

在该插件公开的头文件（`TestFramework.h`）中，未发现 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 标记的蓝图可调用函数或属性。该插件主要服务于 C++ 自动化测试框架。

## C++ 用法

该插件的使用紧密集成在 UE 的自动化测试框架（`AutomationTest.h`）中，通过扩展其功能来辅助编写测试用例。

### 头文件引入

```cpp
#include "TestFramework.h" // 主要用于模块加载
// 更多功能通常通过自动化测试框架本身的头文件引入，例如：
#include "Misc/AutomationTest.h"
```

### 基本用法

该插件通过提供额外的测试宏或辅助类来扩展标准测试。一个典型用例是期望特定日志消息。

*示例来源：基于 Git commit `6349dbe0` 和 `02f16ed3` 推断的用法*
```cpp
#include "Misc/AutomationTest.h"

// 定义一个简单的自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMyLogTest, “MyProject.Logger.MessageTest”, EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::EngineFilter)

bool FMyLogTest::RunTest(const FString& Parameters)
{
    // 使用扩展的日志捕获/期望功能
    // 假设插件提供了类似以下的宏或函数来简化测试
    // 注意：具体宏名需查阅最新源码，此处为示例性描述
    {
        // 开始期望一条错误日志，并指定预期出现次数
        // FExpectedLogError ExpectedError(TEXT(“Something went wrong!”), 1);
        
        // 执行会触发日志的操作
        UE_LOG(LogTemp, Error, TEXT(“Something went wrong!”));
        
        // 验证是否收到了预期的日志（宏在作用域结束时自动验证）
    }
    
    return true;
}
```

### 进阶用法：Latent（延迟）测试

从 commit `f389ff03` 中可以看出，该插件对 Latent 测试用例提供了支持。

```cpp
// 使用 Latent 宏定义需要异步等待或延迟的测试
// IMPLEMENT_COMPLEX_AUTOMATION_TEST 宏是定义延迟测试的标准方式
IMPLEMENT_COMPLEX_AUTOMATION_TEST(FMyLatentTest, “MyProject.Async.LatentTestExample”, EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::EngineFilter)

void FMyLatentTest::GetTests(TArray<FString>& OutBeautifiedNames, TArray<FString>& OutTestCommands) const
{
    // 定义不同的测试变体
    OutBeautifiedNames.Add(TEXT(“Variant1”));
    OutTestCommands.Add(TEXT(“”));
}

bool FMyLatentTest::RunTest(const FString& Parameters)
{
    // 这是一个延迟测试，可以使用 ADD_LATENT_AUTOMATION_COMMAND 来排队执行延迟动作
    // 以下为概念性示例，具体命令需查阅框架文档
    ADD_LATENT_AUTOMATION_COMMAND(FEngineWaitLatentCommand(2.0f)); // 等待2秒
    ADD_LATENT_AUTOMATION_COMMAND(FFunctionLatentCommand([this]()
    {
        // 执行一些异步或延迟后的验证
        return true; // 返回 true 表示该命令完成
    }));
    
    return true;
}
```

## Demo 示例

一个使用 `TestFramework` 插件功能进行日志验证的最小测试示例。

**MyLogTest.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “Misc/AutomationTest.h”

// 声明一个测试类
class FTestFrameworkDemo_LogTest : public FAutomationTestBase
{
public:
    FTestFrameworkDemo_LogTest(const FString& InName, const bool bInComplexTask)
        : FAutomationTestBase(InName, bInComplexTask)
    {
    }
    
    // 测试标签，用于在编辑器中过滤
    virtual uint32 GetTestFlags() const override { return EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter; }
    virtual bool IsStressTest() const { return false; }
    virtual uint32 GetRequiredDeviceNum() const override { return 1; }
    
    // 测试实现
    virtual FString GetBeautifiedTestName() const override { return TEXT(“TestFrameworkDemo.LogTest”); }
    virtual void GetTests(TArray<FString>& OutBeautifiedNames, TArray<FString>& OutTestCommands) const override;
    virtual bool RunTest(const FString& Parameters) override;
};
```

**MyLogTest.cpp**
```cpp
#include “MyLogTest.h”

// 注册测试
namespace
{
    FTestFrameworkDemo_LogTest GTestFrameworkDemo_LogTest(TEXT(“TestFrameworkDemo.LogTest”), false);
}

void FTestFrameworkDemo_LogTest::GetTests(TArray<FString>& OutBeautifiedNames, TArray<FString>& OutTestCommands) const
{
    OutBeautifiedNames.Add(TEXT(“Basic”));
    OutTestCommands.Add(TEXT(“”));
}

bool FTestFrameworkDemo_LogTest::RunTest(const FString& Parameters)
{
    // 假设 TestFramework 插件增强了以下期望日志的功能
    // 这里我们模拟一个预期的警告
    UE_LOG(LogTemp, Warning, TEXT(“This is an expected warning for testing.”));
    
    // 在实际项目中，你可以使用类似下面的代码来设置预期：
    // FExpectedLogMessage ExpectedWarning(TEXT(“This is an expected warning for testing.”), ELogVerbosity::Warning);
    // ... 触发代码 ...
    // ExpectedWarning.AssertFulfilled();
    
    // 或者直接使用更高级的宏（如果插件提供）
    // EXPECT_LOG_WARNING(TEXT(“This is an expected warning for testing.”));
    // {
    //     UE_LOG(LogTemp, Warning, TEXT(“This is an expected warning for testing.”));
    // }
    
    return true;
}
```

## 模块依赖

该插件的 Build.cs 主要依赖于标准的测试和自动化相关模块。

| 模块 | 用途 |
|---|---|
| `AutomationController` | 自动化测试控制器和通信 |
| `AutomationMessages` | 自动化测试相关消息定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位与64位格式说明符不匹配导致的问题 |
| 2025-12-10 | `385b778e` | [Backout] - CL49067660 | 回滚了之前的某个改动 |
| 2025-12-09 | `6349dbe0` | Allow capturing non-error/warning/display log messages for automated tests (to match against Expected | 增强了自动化测试中的日志捕获能力，支持非错误/警告/显示类消息 |
| 2025-01-30 | `02f16ed3` | Fixing recently failing AutomationSpec test where adding an expected error with a negative occurrenc | 修复了添加负出现次数预期错误导致测试失败的问题 |
| 2024-08-30 | `f389ff03` | Add tests to cover some missing cases of LatentIt and Async It | 增加了对Latent和异步测试缺失用例的覆盖 |

### 维护评价

该插件创建于 2023 年 4 月，距今约 3 年。从 Git 历史看，它仍在被**维护和更新**，最近一次更新（`769566b4`）发生在 2026 年 4 月。更新内容包括功能增强（如更强大的日志捕获）和 Bug 修复。它作为引擎测试基础设施的一部分，与 `EngineTest` 构建图关联，预计会在引擎开发周期中持续使用和维护。

**推荐使用**：如果你正在为 UE 引擎本身或其核心插件编写复杂的自动化测试，这个插件提供的扩展功能（特别是日志验证和延迟测试支持）是非常有价值的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/TestFramework)