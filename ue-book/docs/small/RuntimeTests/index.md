# Runtime Tests

> Automated tests for runtime code used in both editor and cooked builds

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ✅ `CanContainContent: true` |
| 模块 | RuntimeTests (Runtime, LoadingPhase: PreDefault) |
| 创建时间 | 2016-09-21 |
| 年龄标签 | 👴 老古董（~9.6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/RuntimeTests) | |

## 用途

RuntimeTests 是 Epic Games 官方维护的 **引擎运行时自动化测试插件**，用于验证 UE 引擎核心运行时系统（特别是 Tick 系统、Mass Entity、异步消息、TaskSync）的正确性和性能。

它不是一个面向项目开发的功能插件，而是 **引擎 CI/测试基础设施的一部分**。主要解决的问题：

- **Tick 系统验证**：测试 Actor Tick 的执行顺序、优先级、依赖关系、TickInterval 等行为是否正确
- **性能基准测试**：对比不同 Tick 方式（标准 Tick、TaskGraph、Tasks API、FTSTicker、Mass Processor、AsyncMessage）的性能差异
- **Shader 精度对比**：比较 FP16 和 FP32 Shader 的视觉差异与性能差异
- **Slate 富文本解析测试**：验证 RichText Markup 的解析正确性
- **脚本模糊测试**：对引擎暴露给蓝图的 API 进行 fuzz testing，检测崩溃

## 使用场景

- 你在开发引擎或引擎插件，需要验证 Tick 系统改动没有引入回归 → 运行 `System.Engine.Tick.*` 测试
- 你在评估不同的 actor tick 方案的性能 → 使用 `FPerfTickTest` 配置 CVar 进行对比
- 你在修改 Shader 精度或渲染管线 → 使用 `FCompareBasepassShaders` 对比截图
- 你在给引擎贡献代码，需要跑自动化测试验证 → 启用此插件并执行测试

> ⚠️ **注意**：此插件默认禁用（`EnabledByDefault: false`），需要在 Edit → Plugins 中手动启用，或在 `.uproject` 的 `Plugins` 数组中显式添加。

## 蓝图用法

此插件不提供面向蓝图的功能性节点。其中的 `AEngineTestTickActor` 类暴露了 `BlueprintReadOnly` 属性（如 `TickCount`、`TickOrder`、`bShouldIncrementTickCount` 等），但这些仅供自动化测试读取，不构成常规蓝图 API。

## C++ 用法

此插件提供的类和基类主要面向 **编写引擎级别的自动化测试**。

### 核心测试类

| 类 | 说明 |
|---|---|
| `AEngineTestTickActor` | 测试用 Actor，记录 Tick 次数和顺序，可选做数学运算模拟负载 |
| `UEngineTickTestProcessor` | 测试用 Mass Processor，支持自定义执行函数和 SyncPoint |
| `FEngineTickTestBase` | 自动化测试基类，封装了创建测试 World、生成 Actor、Tick、检查结果等流程 |
| `FCompareBasepassShaders` | Shader 精度对比的复杂自动化测试 |

### 头文件引入

```cpp
#include "EngineRuntimeTests.h"          // Tick 测试基础设施
#include "ShaderComparisonTests.h"       // Shader 对比测试
#include "RuntimeTests.h"               // 模块入口
```

### 基本用法：基于 FEngineTickTestBase 写 Tick 测试

`FEngineTickTestBase` 提供了完整的测试 World 生命周期管理，继承它即可快速编写 Tick 相关测试。

```cpp
// 来源: EngineRuntimeTests.cpp - FBasicTickTest

IMPLEMENT_CUSTOM_SIMPLE_AUTOMATION_TEST(
    FMyTickTest,
    FEngineTickTestBase,
    "System.MyModule.TickTest",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext
    | EAutomationTestFlags::ServerContext | EAutomationTestFlags::EngineFilter
)

bool FMyTickTest::RunTest(const FString& Parameters)
{
    // 1. 创建测试 World
    if (!CreateTestWorld())
        return false;

    bool bSuccess = true;

    // 2. 生成 10 个测试 Actor
    bSuccess &= CreateTestActors(10, AEngineTestTickActor::StaticClass());
    // 3. 开始 Play
    bSuccess &= BeginPlayInTestWorld();

    if (bSuccess)
    {
        // 4. Tick 5 帧
        for (int32 i = 0; i < 5; i++)
        {
            TickTestWorld(0.01f);
        }

        // 5. 验证每个 Actor 的 TickCount == 5
        CheckTickCount(TEXT("MyTest"), 5);
    }

    // 6. 清理
    bSuccess &= DestroyTestWorld();
    return bSuccess && !ReportAnyErrors();
}
```

### 进阶用法：性能对比测试

`FPerfTickTest` 通过 Console Variable 控制测试参数，可对比多种 Tick 方式的性能：

```cpp
// 来源: EngineRuntimeTests.cpp - FPerfTickTest
// 控制参数 CVar:
//   Automation.Test.EngineTickPerf.ActorCount   - Actor 数量（默认 1000）
//   Automation.Test.EngineTickPerf.TickCount    - Tick 帧数（默认 1000）
//   Automation.Test.EngineTickPerf.Options      - 选项位域（0=无依赖, 1=Tick依赖, 2=TickInterval, 3=两者）
//   Automation.Test.EngineTickPerf.RunTests     - 指定运行的测试名（空=全部）

// 支持的测试方法：
// - WorldActorTick       : 标准引擎 Tick（TaskGraph 调度）
// - TaskGraph            : 直接使用 TaskGraph API
// - BaseTask             : 使用 UE::Tasks API
// - WorldTSTicker        : 使用 FTSTicker
// - GameplayMessageSystem: 使用 AsyncMessage 系统
// - MassProcessor        : 使用 Mass Entity Processor
// - TaskSyncManager      : 使用 TaskSyncManager 协调
```

### 进阶用法：TaskSyncManager 测试

测试展示了如何用 `UE::Tick::FTaskSyncManager` 协调 Tick 和 Mass Entity 的执行顺序：

```cpp
// 来源: EngineRuntimeTests.cpp - FTaskSyncTest
// 注册 SyncPoint
UE::Tick::FSyncPointDescription Description;
Description.RegisteredName = FName("MyTask");
Description.SourceName = FName("MySource");
Description.EventType = UE::Tick::ESyncPointEventType::GameThreadTask_HighPriority;
Description.ActivationRules = UE::Tick::ESyncPointActivationRules::WaitForAllWork;
Description.FirstPossibleTickGroup = TG_PrePhysics;
Description.LastPossibleTickGroup = TG_PostPhysics;

SyncManager->RegisterNewSyncPoint(Description);

// 注册 WorkHandle 并请求执行
UE::Tick::FSyncPointId SyncPointId = SyncManager->FindSyncPoint(World, FName("MyTask"));
UE::Tick::FActiveSyncWorkHandle WorkHandle;
SyncManager->RegisterWorkHandle(SyncPointId, WorkHandle);
WorkHandle.ReserveFutureWork(UE::Tick::ESyncWorkRepetition::Once);
WorkHandle.RequestWork(&Actor->PrimaryActorTick, UE::Tick::ESyncWorkRepetition::EveryFrame);
```

### Console Variable 参考

| CVar | 默认值 | 说明 |
|---|---|---|
| `Automation.Test.EngineTickPerf.Options` | `0` | 性能测试选项位域：0=无特殊配置，1=添加 Tick 依赖，2=添加 TickInterval，3=两者 |
| `Automation.Test.EngineTickPerf.ActorCount` | `1000` | 性能测试的 Actor 数量 |
| `Automation.Test.EngineTickPerf.TickCount` | `1000` | 性能测试的 Tick 帧数 |
| `Automation.Test.EngineTickPerf.RunTests` | `""` | 指定运行哪些子测试（空格分隔），空则运行所有默认启用的测试 |

## 包含的测试列表

| 测试路径 | 类型 | 说明 |
|---|---|---|
| `System.Engine.Tick.BasicTest` | Functional | 基本 Tick 功能正确性 |
| `System.Engine.Tick.OrderTest` | Functional | Tick 顺序、优先级、依赖、TickInterval |
| `System.Engine.Tick.TaskSyncTest` | Functional | TaskSyncManager 与 Mass/AsyncMessage 协调 |
| `System.Engine.Tick.PerfTest` | Performance | 多种 Tick 方式性能对比 |
| `System.Engine.CompareShaderPrecision` | Functional (Disabled) | FP16 vs FP32 Shader 精度与性能对比 |
| `System.Slate.RichText.MarkupProcessing` | Smoke | Slate 富文本标记解析正确性 |
| `Test.ScriptFuzzing` | Console Command | 蓝图暴露 API 的模糊测试 |

## Demo 示例

由于此插件是引擎测试基础设施，通常不作为项目依赖使用。如果你想在自己的模块中编写类似的 Tick 测试：

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
});
```

**最小测试示例**：
```cpp
// MyModuleTests.h
#pragma once
#include "Misc/AutomationTest.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMySimpleTickTest,
    "MyModule.Tick.SimpleTest",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter
)

bool FMySimpleTickTest::RunTest(const FString& Parameters)
{
    // 使用 RuntimeTests 的 FTestWorldWrapper 或手动创建 World
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false, TEXT("MyTestWorld"));
    if (!TestNotNull(TEXT("World created"), World))
        return false;

    // ... 你的测试逻辑 ...

    World->DestroyWorld(false);
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、TArray、FString 等 |
| `MassEntity` | Mass Entity 系统（Archetype、Processor、Query） |
| `CoreUObject` | UObject 系统 |
| `Engine` | World、Actor、Tick 等引擎核心 |
| `Slate` | Slate UI 框架（富文本测试） |
| `SlateCore` | Slate 核心类型 |
| `AsyncMessageSystem` | 异步消息系统（测试 Tick 与消息协调） |
| `GameplayTags` | GameplayTag 系统（消息 ID） |
| `ScreenShotComparisonTools` | 截图对比工具（仅 Editor 构建，Shader 测试用） |

插件依赖：`AsyncMessageSystem`

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | 为有对应 .gen.cpp 的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` | 工具化代码修复，无功能变更 |
| 2025-06-10 | `675fd5ae` | 修复 EngineRuntimeTests.h 编译错误 | 编译修复 |
| 2025-06-06 | `27791de9` | UHT namespace 支持 + TaskSyncManager 移入 UE::Tick namespace | 引擎重构的一部分 |

### 维护评价

- **创建时间**：2016-09-21，已存在约 9.6 年
- **更新频率**：最近更新在 2025 年 7 月，属于被动维护（随引擎重构批量更新）
- **活跃程度**：⚠️ **维护不活跃** —— 更新均为编译修复和代码规范化，无功能性改进
- **定位**：引擎内部测试基础设施，不是面向项目开发的功能插件
- **推荐使用**：仅当你在开发引擎本身或需要参考 Tick 测试写法时才有价值。普通项目开发不需要此插件

> ⚠️ 此插件默认禁用。它包含的是引擎级别的自动化测试用例，不会为你的项目提供额外功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/RuntimeTests)
- 官方文档：无（内部测试插件）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/RuntimeTests/Source/RuntimeTests/Private)
