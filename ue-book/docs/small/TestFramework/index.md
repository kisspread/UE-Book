# TestFramework

> UE5 Automation Test 框架的自测试插件，验证 `BEGIN_DEFINE_SPEC` / `Describe` / `It` / `LatentIt` 等宏以及 `AddExpectedError` / `AddExpectedMessage` 预期错误机制的正确性。

| 属性 | 值 |
|---|---|
| 分类 | Tests |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | TestFramework (DeveloperTool) |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/TestFramework) | |

## 用途

TestFramework 并不是一个提供给游戏开发者使用的功能插件，而是 **UE5 Automation Test 框架的自测试（self-test）插件**。它通过两组 Spec 测试来验证引擎核心测试框架本身的行为是否正确：

1. **AutomationSpec 测试** — 验证 `Describe` / `It` / `BeforeEach` / `AfterEach` / `xIt` / `xDescribe` / `LatentIt` 等 BDD 风格测试宏的嵌套、执行顺序、异步执行和禁用机制。
2. **AutomationExpectedMessage 测试** — 验证 `AddExpectedError` / `AddExpectedErrorPlain` / `AddExpectedMessage` 预期消息匹配机制，包括正则匹配、精确匹配、`Contains` 模式、大小写不敏感、重复去重、出现次数控制等。

简单来说：**它是测试"测试框架"的测试。**

## 使用场景

- 你正在为 UE5 的 Automation Test 框架贡献代码，需要回归验证 → 运行此插件的测试
- 你想学习 `BEGIN_DEFINE_SPEC` / `Describe` / `It` 等 BDD 风格测试宏的最佳写法 → 参考此插件的源码作为范例
- 你想了解 `AddExpectedError` 的各种匹配模式和边界行为 → 参考 `AutomationExpectedMessage.spec.cpp`
- 你想了解嵌套 `Describe` 中 `BeforeEach` / `AfterEach` 的执行顺序 → 参考 `AutomationSpec.spec.cpp`

## 蓝图用法

此插件不包含任何蓝图可调用接口。它是一个纯 C++ 开发者工具插件，仅包含自动化测试代码。

## C++ 用法

此插件的代码本身就是学习 UE5 Automation Test 框架的最佳范例。

### 头文件引入

```cpp
#include "Misc/AutomationTest.h"
```

### 基本用法：BDD 风格 Spec 测试

来源：`Source/TestFramework/Private/AutomationSpec.spec.cpp`

```cpp
// 定义一个 Spec 测试类
BEGIN_DEFINE_SPEC(MyTestSpec, "MyPlugin.MyCategory", EAutomationTestFlags::EngineFilter | EAutomationTestFlags_ApplicationContextMask)
    bool Foo;
    FString RunOrder;
END_DEFINE_SPEC(MyTestSpec)

void MyTestSpec::Define()
{
    // Describe 定义一组相关测试
    Describe("A feature group", [this]()
    {
        // BeforeEach 在每个 It 之前执行
        BeforeEach([this]()
        {
            Foo = false;
            RunOrder = TEXT("A");
        });

        // It 定义单个测试用例
        It("should do something", [this]()
        {
            Foo = true;
            TestEqual("Foo", Foo, true);
        });

        // AfterEach 在每个 It 之后执行
        AfterEach([this]()
        {
            RunOrder += TEXT("Z");
            TestEqual("RunOrder", RunOrder, TEXT("AZ"));
        });
    });
}
```

**关键宏说明：**

| 宏 | 说明 |
|---|---|
| `BEGIN_DEFINE_SPEC(ClassName, TestName, Flags)` | 定义 Spec 测试类，可声明成员变量 |
| `END_DEFINE_SPEC(ClassName)` | 结束定义 |
| `Describe("name", [this](){ ... })` | 定义一组测试，类似 RSpec/Jasmine 的 describe |
| `It("name", [this](){ ... })` | 定义单个测试用例 |
| `BeforeEach([this](){ ... })` | 每个 It 之前的 setup |
| `AfterEach([this](){ ... })` | 每个 It 之后的 teardown |
| `xIt(...)` | 禁用某个 It（前缀 x = skip） |
| `xDescribe(...)` | 禁用整个 Describe |
| `LatentIt("name", [this](const FDoneDelegate Done){ ... })` | 异步测试，需调用 `Done.Execute()` 完成 |

### 禁用测试

来源：`Source/TestFramework/Private/AutomationSpec.spec.cpp`

```cpp
Describe("A Describe 2", [this]()
{
    // xIt 前缀表示跳过此测试
    xIt("will not run disabled specs", [this]()
    {
        TestEqual("Foo", Foo, true);  // 不会执行
    });

    // xDescribe 跳过整个分组
    xDescribe("with disabled nested Describes", [this]()
    {
        It("will not run specs within those Describes", [this]()
        {
            // 不会执行
        });
    });
});
```

### 异步测试

来源：`Source/TestFramework/Private/AutomationSpec.spec.cpp`

```cpp
Describe("A spec async", [this]()
{
    Describe("will run BeforeEach and AfterEach blocks", [this]()
    {
        It("", EAsyncExecution::ThreadPool, [this]()
        {
            RunOrder += TEXT("B");
            // 此 Lambda 在线程池中执行
        });
    });
});

Describe("LatentIt", [this]()
{
    // LatentIt 用于需要等待的异步操作
    LatentIt("", [this](const FDoneDelegate Done)
    {
        Async(EAsyncExecution::ThreadPool, [this, Done]()
        {
            FPlatformProcess::Sleep(0.3f);
            Done.Execute();  // 必须调用 Done 来标记完成
        });
    });

    // LatentIt 也支持指定异步执行方式
    LatentIt("", EAsyncExecution::ThreadPool, [this](const FDoneDelegate Done)
    {
        FPlatformProcess::Sleep(0.1f);
        Done.Execute();
    });
});
```

### 预期错误（Expected Error）

来源：`Source/TestFramework/Private/AutomationExpectedMessage.spec.cpp`

```cpp
Describe("A defined expected error in a test", [this]()
{
    // Contains 模式：消息包含指定字符串即匹配
    It("will match a message that contains the pattern", [this]()
    {
        AddExpectedError(TEXT("Expected Error"), EAutomationExpectedErrorFlags::Contains, 1);
        AddError(TEXT("Some Expected Error not caught"));  // 匹配成功
    });

    // Exact 模式：消息必须完全匹配
    It("will match exact messages", [this]()
    {
        AddExpectedError(TEXT("Expected Exact Error"), EAutomationExpectedErrorFlags::Exact, 1);
        AddError(TEXT("Expected Exact Error"));  // 匹配成功
    });

    // 正则模式：默认使用正则表达式匹配
    It("will match regex patterns", [this]()
    {
        AddExpectedError(TEXT("Response \\\\(-?\\\\d+\\\\)"), EAutomationExpectedErrorFlags::Contains, 4);
        AddError(TEXT("Response (0)"));
        AddError(TEXT("Response (1)"));
        AddError(FString::Printf(TEXT("Response (%d)"), MIN_int64));
        AddError(FString::Printf(TEXT("Response (%d)"), MAX_uint64));
    });

    // 纯文本模式：不使用正则，按字面意思匹配
    It("will match plain string pattern", [this]()
    {
        AddExpectedErrorPlain(TEXT("Expected Error"), EAutomationExpectedErrorFlags::Contains, 1);
        AddError(TEXT("Some Expected Error not caught"));
    });

    // 出现次数为 0 表示"不应该出现此错误"
    It("will not match with zero occurrences", [this]()
    {
        AddExpectedError(TEXT("Expected Error"), EAutomationExpectedErrorFlags::Contains, 0);
        // 如果此错误出现，测试会失败
    });

    // 重复的预期错误会被去重
    It("will not duplicate expected errors", [this]()
    {
        AddExpectedError(TEXT("Expected Error"), EAutomationExpectedErrorFlags::Contains, 1);
        AddExpectedError(TEXT("Expected Error"), EAutomationExpectedErrorFlags::Contains, 1);
        // 只算一次
    });
});
```

**`AddExpectedError` 参数说明：**

| 参数 | 说明 |
|---|---|
| `Message` | 匹配模式（默认为正则表达式） |
| `Flags` | `Exact`（精确匹配）或 `Contains`（包含匹配） |
| `Occurrences` | 预期出现次数，-1 表示任意次数，0 表示不应出现 |

**`AddExpectedMessage` 扩展版本：**

```cpp
// 可以指定日志级别
AddExpectedMessage(TEXT("suppress this error message"), ELogVerbosity::Error, 
    EAutomationExpectedMessageFlags::Contains, 1);
```

### 嵌套 Describe 的执行顺序

来源：`Source/TestFramework/Private/AutomationSpec.spec.cpp`

这是一个重要的行为特性——嵌套 `Describe` 时，所有层级的 `BeforeEach` / `AfterEach` 都会按从外到内 / 从内到外的顺序执行：

```cpp
Describe("outer", [this]()
{
    BeforeEach([this]() { RunOrder = TEXT("A"); });

    Describe("inner", [this]()
    {
        BeforeEach([this]() { RunOrder += TEXT("B"); });

        It("test", [this]()
        {
            // 此时 RunOrder == "AB"（外层 BeforeEach 先执行）
        });

        AfterEach([this]() { RunOrder += TEXT("Y"); });
    });

    AfterEach([this]()
    {
        RunOrder += TEXT("Z");
        // 此时 RunOrder == "ABYZ"（内层 AfterEach 先执行）
    });
});
```

**执行顺序：外层 BeforeEach → 内层 BeforeEach → It → 内层 AfterEach → 外层 AfterEach**

### 获取预期消息列表

```cpp
TArray<FAutomationExpectedMessage> Errors;

// 获取非抑制的预期消息
GetExpectedMessages(Errors, ELogVerbosity::Warning);

// 获取所有预期消息（包括被抑制的）
const bool bIncludeSuppressed = true;
GetExpectedMessages(Errors, bIncludeSuppressed, ELogVerbosity::Warning);
```

## Demo 示例

此插件本身即为完整示例。最小复现方式：

### 在你的模块中创建 Spec 测试

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
});
```

**MySpecTest.spec.cpp：**
```cpp
// Copyright Your Company. All Rights Reserved.

#include "Misc/AutomationTest.h"

BEGIN_DEFINE_SPEC(FMySpecTest, "MyPlugin.UnitTests", EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)
    int32 Counter;
END_DEFINE_SPEC(FMySpecTest)

void FMySpecTest::Define()
{
    Describe("Counter", [this]()
    {
        BeforeEach([this]()
        {
            Counter = 0;
        });

        It("should start at zero", [this]()
        {
            TestEqual("Initial value", Counter, 0);
        });

        It("should increment", [this]()
        {
            Counter++;
            TestEqual("After increment", Counter, 1);
        });

        It("should handle expected errors", [this]()
        {
            // 告诉框架：我们预期这条错误会出现，不要把它当成测试失败
            AddExpectedError(TEXT("Some expected warning"), EAutomationExpectedErrorFlags::Contains, 1);
            UE_LOG(LogTemp, Warning, TEXT("Some expected warning"));
        });
    });
}
```

## 模块依赖

从 `Build.cs` 提取。要使用此插件的代码模式，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、FString、TArray 等 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能（私有依赖） |

> 注意：`Misc/AutomationTest.h` 头文件来自 `Core` 模块，不需要额外依赖即可使用 Spec 测试宏。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-01-30 | `02f16ed3cd69` | 修复 AutomationSpec 测试中负数 occurrence 的预期错误被错误拾取的问题，新增 `GetExpectedMessages` 方法支持获取所有或仅未抑制的预期消息 |
| 2024-08-30 | `f389ff035118` | 补充 `LatentIt` 和异步 `It` 的缺失测试用例 |
| 2024-06-12 | `e521f5d700f0` | 将 `EAutomationTestFlags::ApplicationContextMask` 替换为 `EAutomationTestFlags_ApplicationContextMask`（API 更新） |

### 维护评价

- **创建时间**：2023-04-03，约 3 年前
- **更新频率**：约每 6-8 个月有一次更新，最近一次在 2025 年 1 月
- **维护状态**：**维护中** — 更新频率适中，内容以修复和补充测试为主
- **是否推荐使用**：此插件不是直接使用的功能插件，而是测试框架的自测试。如果你在学习 UE5 的 Spec 测试写法，此插件的源码是极佳的参考。
- **注意**：`EnabledByDefault: false`，需要在编辑器中手动启用，或通过命令行 `-Plugin=TestFramework` 加载

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/TestFramework)
- [AutomationSpec 测试](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/TestFramework/Source/TestFramework/Private/AutomationSpec.spec.cpp)
- [AutomationExpectedMessage 测试](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/TestFramework/Source/TestFramework/Private/AutomationExpectedMessage.spec.cpp)
