# Code Quality Tests Unreal Test Plugin

> Tests for the CQTest Unreal Engine module（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 代码质量测试插件 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CQTestTests` (DeveloperTool) |
| 实验性 | 否 |
| 创建时间 | 2023-03-29 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTest) | |

## 用途

CQTest 是对 Unreal Engine 自动化测试基础类 `FAutomationTestBase` 的扩展。它旨在为编写复杂、场景化的 C++ 单元测试提供一个更强大、更便捷的框架。其主要解决的问题和存在的价值在于：

1.  **提供测试夹具 (Test Fixtures)**：允许为每个测试或测试套件设置特定的初始状态（如生成 Actor、配置 GameMode），并在测试完成后自动清理，避免测试间的状态污染。
2.  **自动化状态重置**：通过 `BEFORE_EACH` 和 `AFTER_EACH` 宏，在测试生命周期的关键点执行代码，确保每个测试都在一个干净、一致的环境中运行。
3.  **扩展测试能力**：提供了标准 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 宏之外的更多测试定义宏，支持参数化测试等高级功能。

它让开发者能够更专注于测试逻辑本身，而不是测试环境的搭建和清理工作。

## 使用场景

-   你需要测试一个依赖于特定 `UWorld` 设置、GameMode 或已生成 Actor 的逻辑 → 使用 CQTest 的测试夹具来自动创建和销毁这些对象。
-   你正在测试网络复制相关的功能（如 `Replicated` 属性），需要一个配置好的网络环境 → 使用 CQTest 快速搭建测试所需的世界和连接。
-   你编写了多个相互关联的测试，它们共享相同的复杂初始化步骤 → 使用 `BEFORE_EACH` 避免代码重复。
-   你需要验证代码在预期错误或警告日志下的行为 → 使用 `ClearExpectedError` 等辅助函数进行精确控制。

## 蓝图用法

CQTest 是一个 **DeveloperTool** 类型的测试插件，其核心功能通过 C++ 宏和函数提供，**没有暴露 BlueprintCallable 节点**。它的使用完全在 C++ 自动化测试代码中。

## C++ 用法

CQTest 的核心用法是通过其提供的宏来定义和增强测试用例。

### 头文件引入

根据你要使用的功能，可能需要包含以下头文件：

```cpp
#include "CQTest.h" // 包含核心测试宏和基础类
```

### 基本用法

**1. 定义一个简单的 CQTest 测试类**

使用 `TEST_PURE_VIRTUAL` 宏来替代标准的 `IMPLEMENT_SIMPLE_AUTOMATION_TEST`，以获得夹具支持。

```cpp
// 来源：基于 CQTest 核心设计的典型用法
#include "CQTest.h"

class FMySimpleTest : public CQTestBase
{
    using CQTestBase::CQTestBase; // 继承构造函数

    TEST_PURE_VIRTUAL(FMySimpleTest, "Project.MyFeature.SimpleTest")

    void SetupTest() override
    {
        // 每个测试开始前执行，可以在这里生成测试对象
        // 例如：测试Actor = SpawnActor<ATestActor>();
    }

    void TearDownTest() override
    {
        // 每个测试结束后执行，自动清理资源
        // CQTestBase 通常会处理世界和对象的销毁，自定义清理也可在此进行
    }

    void RunTest() override
    {
        // 你的具体测试逻辑
        TestTrue("Feature should be valid", MyFeature->IsValid());
    }
};
```

**2. 使用 `BEFORE_EACH` 和 `AFTER_EACH` 进行更细粒度的控制**

这些宏在每个 `TEST` 方法执行前后运行，适合为一组相关测试设置共同状态。

```cpp
// 来源：基于 CQTest 夹具模式的设计
class FMyActorTest : public CQTestBase
{
    // ... TEST_PURE_VIRTUAL 声明 ...

    // 在每个 TEST 方法前执行
    BEFORE_EACH()
    {
        // 例如，在一个专用的测试世界中生成Actor
        TestActor = GetWorld()->SpawnActor<ATestActorWithProperties>();
    }

    // 在每个 TEST 方法后执行
    AFTER_EACH()
    {
        // 可以在此进行额外的清理，例如重置某些状态
    }

    // 具体的测试点 1
    TEST(FeatureA)
    {
        TestNotNull("Actor should exist", TestActor);
        TestEqual("Initial value", TestActor->Int32Property, 0);
    }

    // 具体的测试点 2
    TEST(FeatureB)
    {
        // 上一个 TEST 结束后，BEFORE_EACH 会再次执行，确保 TestActor 是新生成的
        TestActor->Int32Property = 100;
        TestEqual("Modified value", TestActor->Int32Property, 100);
    }

private:
    ATestActorWithProperties* TestActor = nullptr;
};
```

**3. 使用测试辅助函数处理预期错误**

CQTest 提供了清除预期日志消息的功能，用于测试预期的失败路径。

```cpp
// 来源：CQTestUnitTestHelper.h 中声明的函数
#include "CQTestUnitTestHelper.h" // 包含辅助函数

TEST(HandleExpectedFailure)
{
    // 设置预期的错误消息
    AddExpectedError(TEXT("Accessed None"));

    // 执行一个会触发预期错误的操作
    CallFunctionThatAccessesNull();

    // 测试框架会检查是否收到了预期的错误
    // 可以选择性地手动清除预期错误以允许测试通过（在AFTER_EACH中可能需要）
    ClearExpectedError(*this, TEXT("Accessed None"));
}
```

### 进阶用法

结合多个功能测试复杂场景。

```cpp
class FNetworkReplicationTest : public CQTestBase
{
    // ... TEST_PURE_VIRTUAL 声明 ...

    BEFORE_EACH()
    {
        // 设置一个支持网络复制的世界和游戏模式
        GameMode = GetWorld()->SpawnActor<ACQTestGameMode>();
        // 设置基础的测试数据
        ReplicatedActor = GetWorld()->SpawnActor<ATestReplicatedActor>();
    }

    AFTER_EACH()
    {
        // 清理网络相关状态
        ReplicatedActor = nullptr;
        GameMode = nullptr;
    }

    TEST(ReplicatedIntInitializesToZero)
    {
        // 基于 TestReplicatedActor.h 中的定义
        TestEqual("Replicated Int should start at 0", ReplicatedActor->ReplicatedInt, 0);
    }

    TEST(ReplicatedIntChangesAfterSimulatedUpdate)
    {
        // 模拟一个更新（实际可能需要通过 RPC 或属性复制机制）
        ReplicatedActor->ReplicatedInt = 55;
        // 验证本地值已改变（实际复制测试需要更复杂的场景设置）
        TestEqual("Replicated Int should be updated", ReplicatedActor->ReplicatedInt, 55);
    }

private:
    ACQTestGameMode* GameMode = nullptr;
    ATestReplicatedActor* ReplicatedActor = nullptr;
};
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何使用 CQTest 测试一个简单的 Actor 属性。

**MyCQTestDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "CQTest.h"

// 声明一个使用 CQTest 的测试类
class FMyCQTestDemo : public CQTestBase
{
public:
    // 继承构造函数
    using CQTestBase::CQTestBase;

    // 声明测试套件，名称格式为 “模块.类别.测试名”
    TEST_PURE_VIRTUAL(FMyCQTestDemo, "CQTestDemo.Basic.ActorSpawn")

protected:
    // 每个测试开始前的设置
    void SetupTest() override;
    // 测试逻辑
    void RunTest() override;

private:
    // 测试中使用的 Actor 指针
    AActor* SpawnedActor = nullptr;
};
```

**MyCQTestDemo.cpp**
```cpp
#include "MyCQTestDemo.h"
#include "Engine/World.h"

void FMyCQTestDemo::SetupTest()
{
    // 在测试世界中生成一个基础的 Actor
    // GetWorld() 来自 CQTestBase，它返回一个专用于测试的 UWorld 实例
    if (UWorld* World = GetWorld())
    {
        SpawnedActor = World->SpawnActor<AActor>();
    }
}

void FMyCQTestDemo::RunTest()
{
    // 断言1：Actor 应该成功生成
    TestNotNull(TEXT("Actor should be spawned successfully"), SpawnedActor);

    if (SpawnedActor)
    {
        // 断言2：新生成的 Actor 默认应该是可见的
        TestTrue(TEXT("Actor should be visible by default"), SpawnedActor->IsVisible());

        // 断言3：Actor 的初始位置应该是世界原点
        FVector ActorLocation = SpawnedActor->GetActorLocation();
        TestTrue(TEXT("Actor should start near world origin"), ActorLocation.IsNearlyZero(1.0f));
    }
}

// 注意：不需要手动实现 IMPLEMENT_SIMPLE_AUTOMATION_TEST 宏。
// TEST_PURE_VIRTUAL 宏和 CQTestBase 的结构会处理测试的注册。
// 确保你的模块在 .Build.cs 中依赖了 “CQTestTests” 模块。
```

## 模块依赖

要使用 CQTest 插件，你的测试模块需要在 `Build.cs` 中添加对 `CQTestTests` 模块的依赖。

| 模块 | 用途 |
|---|---|
| `CQTestTests` | CQTest 测试框架的核心实现，提供 `CQTestBase`、测试宏和辅助函数。 |

你的 `YourTestModule.Build.cs` 文件应包含：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "CQTestTests" // 添加对 CQTest 的依赖
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将测试代码中的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏。 |
| 2025-09-15 | `97120dda` | Add support for pointers and TOptional values to CQTestConvert::ToString | 为 `ToString` 函数增加了对指针和 `TOptional` 类型的支持，增强了日志和断言信息的可读性。 |
| 2025-07-30 | `75860784` | Fix for null entries in ClientConnections array | 修复了测试框架中网络连接数组为空条目时可能导致的崩溃问题。 |
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied to source of the Epic Games repository) | 为相关源文件添加了 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏，优化了生成的代码。 |
| 2025-05-29 | `26a10c8f` | CQTest - Support assert macros in base test classes | 增强了 CQTest 框架，使其断言宏（如 `TestTrue`, `TestEqual`）可以在测试基类中正常工作。 |

### 维护评价

-   **活跃维护**：从 git 历史看，该插件在最近一年（截至 2026 年初）仍有持续的更新，包括功能增强（如支持新类型）、bug 修复和引擎宏迁移。
-   **创建时间**：创建于 2023 年 3 月，是一个相对年轻的插件。
-   **实验性**：`.uplugin` 中 `IsBetaVersion` 为 `false`，表明其已脱离实验状态，被认为足够稳定。
-   **已知限制**：这是一个面向开发者的 `DeveloperTool`，**默认未启用 (`Installed: false`)**，需要开发者在插件列表中手动启用后才能使用。
-   **推荐使用**：**推荐**。该插件由 Epic Games 维护，旨在解决 UE 自动化测试中的实际痛点，且维护状态活跃。对于需要编写复杂、有状态的 C++ 自动化测试的项目来说，它是一个非常有价值的工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTest)
-   [官方文档](https://epicgames.com)（无专用文档链接，可参考引擎自动化测试通用文档）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTest/Source/CQTestTests) (插件自身的源码，特别是 `Private` 目录下的文件，即是示例也是测试)