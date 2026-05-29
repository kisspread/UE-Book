# Runtime Tests

> Automated tests for runtime code used in both editor and cooked builds

| 属性 | 值 |
|---|---|
| 中文名 | 运行时测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RuntimeTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-09-21 |
| 年龄标签 | 👴 老古董（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/RuntimeTests) | |

## 用途

这是一个 Epic 内部使用的自动化测试框架插件，专门为引擎运行时代码提供测试支持。它不是面向普通开发者的功能插件，而是用于验证引擎 Tick 系统、Mass Entity 处理器、着色器精度等底层运行时功能的正确性。

该插件默认关闭（`EnabledByDefault: false`），仅在需要执行引擎自动化测试时手动启用。它提供了：
- 一个可控的测试用 Actor（`AEngineTestTickActor`），可精确测试 Tick 顺序、计数和性能
- 一个基于 Mass Entity 框架的测试处理器（`UEngineTickTestProcessor`）
- 一套自动化测试基类（`FEngineTickTestBase`），封装了测试世界的创建、销毁、Actor 生成等常见操作
- 着色器精度比较测试（`FCompareBasepassShaders`），用于检测不同精度级别下着色器行为的一致性

## 使用场景

- 你需要验证自定义 Tick 逻辑的执行顺序和正确性 → 使用 `AEngineTestTickActor` 和 `FEngineTickTestBase`
- 你在开发 Mass Entity 相关功能，需要测试处理器调度 → 使用 `UEngineTickTestProcessor`
- 你需要比较着色器在不同精度下的渲染差异 → 使用 `FCompareBasepassShaders`
- 你正在为引擎运行时代码编写自动化测试套件 → 此插件提供了基础设施

## 蓝图用法

该插件不提供面向蓝图用户的节点，其所有功能均为 C++ 自动化测试服务。

### 可访问的蓝图属性

`AEngineTestTickActor` 的部分属性可通过蓝图只读访问（用于调试/观察）：

| 属性 | 说明 | 所在类 |
|---|---|---|
| `TickCount` | 自上次重置以来的 Tick 次数 | `AEngineTestTickActor` |
| `TickOrder` | 当前帧中的 Tick 顺序（1 = 第一个） | `AEngineTestTickActor` |
| `bShouldIncrementTickCount` | 是否递增 TickCount | `AEngineTestTickActor` |
| `bShouldDoMath` | 是否执行数学运算（性能测试） | `AEngineTestTickActor` |
| `MathCounter` | 数学运算计数器 | `AEngineTestTickActor` |
| `MathIncrement` | 数学运算步进值 | `AEngineTestTickActor` |
| `MathLimit` | 数学运算上限 | `AEngineTestTickActor` |

## C++ 用法

### 头文件引入

```cpp
#include "EngineRuntimeTests.h"
```

### 基本用法

从 `FEngineTickTestBase` 派生自定义自动化测试类，测试 Tick 系统行为。

```cpp
// 来源: Engine/Plugins/Tests/RuntimeTests/Source/RuntimeTests/Public/EngineRuntimeTests.h

// 定义一个自动化测试
class FMyTickTest : public FEngineTickTestBase
{
public:
    FMyTickTest(const FString& InName, const bool bInComplexTask)
        : FEngineTickTestBase(InName, bInComplexTask)
    {}

    virtual bool RunTest(const FString& Parameters) override
    {
        // 1. 创建测试世界
        if (!CreateTestWorld())
        {
            return false;
        }

        // 2. 生成测试 Actor
        if (!CreateTestActors(10, AEngineTestTickActor::StaticClass()))
        {
            return false;
        }

        // 3. 开始游戏，准备 Tick
        if (!BeginPlayInTestWorld())
        {
            return false;
        }

        // 4. Tick 一帧
        if (!TickTestWorld(0.01f))
        {
            return false;
        }

        // 5. 验证每个 Actor 的 TickCount 是否为 1
        if (!CheckTickCount(TEXT("First Tick"), 1))
        {
            return false;
        }

        // 6. 清理
        DestroyAllTestActors();
        DestroyTestWorld();

        return ReportAnyErrors();
    }
};
```

### 进阶用法

使用 Mass Entity 处理器进行批量 Tick 测试，自定义处理函数：

```cpp
// 来源: Engine/Plugins/Tests/RuntimeTests/Source/RuntimeTests/Public/EngineRuntimeTests.h

// 创建 Mass Entity 测试处理器
UEngineTickTestProcessor* Processor = NewObject<UEngineTickTestProcessor>();

// 自定义执行函数，替换默认的 ForEachEntityChunk 行为
Processor->ExecutionFunction = [](FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 自定义 Mass Entity 处理逻辑
    // 可以在这里进行批量实体操作、性能测试等
};

// 配置同步点名称（用于任务调度）
Processor->SyncPointName = FName("MyTestSyncPoint");
```

自定义 `AEngineTestTickActor` 的 Tick 行为：

```cpp
// 来源: Engine/Plugins/Tests/RuntimeTests/Source/RuntimeTests/Public/EngineRuntimeTests.h

// 创建带自定义行为的测试 Actor
AEngineTestTickActor* TestActor = GetTestWorld()->SpawnActor<AEngineTestTickActor>();

// 控制是否递增 TickCount（用于测试不同 Tick 条件）
TestActor->bShouldIncrementTickCount = true;

// 启用数学运算（用于性能基准测试）
TestActor->bShouldDoMath = true;
TestActor->MathIncrement = 0.001f;
TestActor->MathLimit = 1000.0f;

// 测试完成后重置状态
TestActor->ResetState();
```

## Demo 示例

一个最小化的运行时 Tick 测试示例：

```cpp
// MyTickTest.h
#pragma once

#include "EngineRuntimeTests.h"
#include "Misc/AutomationTest.h"

// 定义一个简单的 Tick 计数验证测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMySimpleTickTest,
    "MyProject.Runtime.TickOrder",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

// MyTickTest.cpp
#include "MyTickTest.h"

bool FMySimpleTickTest::RunTest(const FString& Parameters)
{
    // 利用 FEngineTickTestBase 的测试基础设施
    FEngineTickTestBase TickHelper(TEXT("TickOrderHelper"), false);

    // 创建测试世界
    if (!TickHelper.CreateTestWorld())
    {
        AddError(TEXT("Failed to create test world"));
        return false;
    }

    // 生成 5 个测试 Actor
    if (!TickHelper.CreateTestActors(5, AEngineTestTickActor::StaticClass()))
    {
        AddError(TEXT("Failed to spawn test actors"));
        return false;
    }

    // 进入游戏模式
    if (!TickHelper.BeginPlayInTestWorld())
    {
        AddError(TEXT("Failed to begin play"));
        return false;
    }

    // 连续 Tick 3 帧
    for (int32 Frame = 0; Frame < 3; ++Frame)
    {
        if (!TickHelper.TickTestWorld(0.016f))
        {
            AddError(FString::Printf(TEXT("Failed to tick frame %d"), Frame));
            return false;
        }
    }

    // 验证每个 Actor 被 Tick 了 3 次
    TickHelper.CheckTickCount(TEXT("ThreeFrames"), 3);

    // 清理并报告
    TickHelper.DestroyAllTestActors();
    TickHelper.DestroyTestWorld();

    return !TickHelper.ReportAnyErrors();
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等），额外依赖 `ScreenShotComparisonTools` 模块（用于着色器比较测试）。

| 模块 | 用途 |
|---|---|
| `ScreenShotComparisonTools` | 截图比较工具，用于着色器精度测试的输出对比 |

插件级依赖：`AsyncMessageSystem`（已启用）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 拆分出 MassCore 模块 |
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏到源文件 |
| 2025-06-10 | `675fd5ae` | CIS issue#936427: Compile errors in EngineRuntimeTests.h, MoverMassTranslators.h and MoverMassTransl | 修复 EngineRuntimeTests.h 的编译错误 |
| 2025-06-06 | `27791de9` | Enable UHT namespace support for Engine, testing this before enabling for all modules. | 为引擎模块启用 UHT 命名空间支持 |

### 维护评价

该插件创建于 2016 年，至今约 10 年历史，属于**老古董**级别。从近期提交记录来看，2025-2026 年的更新均为编译修复、代码现代化宏迁移和 Mass Entity 框架重构的附带改动，**没有功能性更新**。这不是因为插件被废弃，而是因为它作为测试基础设施已经相当稳定，不需要频繁变更。

该插件**默认关闭**，属于 Epic 内部测试工具链的一部分。对于普通 UE5 开发者而言，除非你在编写引擎级别的自动化测试，否则不需要启用此插件。如果你需要了解引擎如何组织运行时测试，可以参考 `FEngineTickTestBase` 的设计模式来构建自己的测试框架。

**注意**：此插件不提供面向最终用户的功能，建议仅在研究引擎源码或编写底层自动化测试时参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/RuntimeTests)