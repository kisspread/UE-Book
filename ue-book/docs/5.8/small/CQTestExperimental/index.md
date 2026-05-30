# CQTestExperimental

> Simplified testing of experimental features for Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 实验性测试插件 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CQTestExperimentalTests` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestExperimental) | |

## 用途

该插件是 Epic Games 为验证 **Unreal Engine 实验性功能**而提供的一个隔离测试框架。其核心目的不是提供给最终游戏使用的运行时功能，而是作为一个专用的“沙盒”，允许引擎开发者和早期技术验证者，为即将到来的、尚未完全稳定的引擎特性编写自动化测试用例，确保其正确性和稳定性。目前，其主要功能是支持对 **Iris 复制系统**等新兴功能的测试。

## 使用场景

- 你是一名引擎开发者或技术美术，正在测试一个尚未正式发布的实验性引擎功能（如新的网络复制方案 Iris）。
- 你需要一个与主游戏代码隔离的环境来编写和运行针对该功能的单元测试或集成测试。
- 你需要快速验证某个实验性 API 的行为是否符合预期。

## 蓝图用法

该插件本身主要是一个 C++ 测试框架，不提供运行时蓝图节点。其测试类（如 `UAutomationTestBase`）通常在自动化测试管线中通过命令行调用，而非在游戏逻辑中直接使用。

## C++ 用法

该插件提供的核心是用于编写特定实验性功能测试的基类和辅助对象。

### 头文件引入

你需要引入测试专用的头文件，并确保你的测试模块依赖 `CQTestExperimentalTests`。

```cpp
#include "Iris/CQTestObjects.h"
```

### 基本用法

`CQTestObjects.h` 中定义了用于 Iris 复制系统测试的专用类。以下是如何在你的自动化测试中使用它们的基本步骤。

**1. 定义一个继承自 CQTest 测试基类的测试类：**
```cpp
// 在你的测试文件中
#include "Misc/AutomationTest.h"
#include "Iris/CQTestObjects.h"

// 定义一个自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMyIrisReplicationTest,
    "ProjectName.Feature.IrisReplication",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMyIrisReplicationTest::RunTest(const FString& Parameters)
{
    // GIVEN - 设置测试环境
    // 使用插件提供的专用 GameInstance 和 GameMode 进行隔离测试
    UIrisTestGameInstanceClass* TestGameInstance = NewObject<UIrisTestGameInstanceClass>();
    AIrisTestGameMode* TestGameMode = GetWorld()->SpawnActor<AIrisTestGameMode>();

    // WHEN - 执行被测操作
    // 创建一个用于复制测试的 Actor
    AIrisTestReplicatedActor* TestActor = GetWorld()->SpawnActor<AIrisTestReplicatedActor>();
    const int32 OriginalValue = TestActor->ReplicatedInt;

    // THEN - 验证结果
    TestEqual(TEXT("The replicated int should have a default value"), TestActor->ReplicatedInt, 0);
    TestTrue(TEXT("GameInstance should be accessible"), TestGameInstance != nullptr);

    return true;
}
```
*代码灵感来源于 `CQTestObjects.h` 中定义的 `UIrisTestGameInstanceClass`、`AIrisTestGameMode` 和 `AIrisTestReplicatedActor`。*

### 进阶用法

更复杂的测试可能涉及模拟网络环境、验证属性同步等。`AIrisTestReplicatedActor` 已配置了 `ReplicatedInt` 属性，是测试 `GetLifetimeReplicatedProps` 和复制基本类型的理想对象。

```cpp
// 进阶测试：验证属性复制声明是否正确
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FIrisReplicationPropsTest,
    "ProjectName.Feature.IrisReplication.LifetimeProps",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FIrisReplicationPropsTest::RunTest(const FString& Parameters)
{
    AIrisTestReplicatedActor* TestActor = GetWorld()->SpawnActor<AIrisTestReplicatedActor>();

    TArray<FLifetimeProperty> LifetimeProps;
    TestActor->GetLifetimeReplicatedProps(LifetimeProps);

    // 验证 ReplicatedInt 属性是否在复制列表中
    const bool bFoundReplicatedInt = LifetimeProps.ContainsByPredicate([](const FLifetimeProperty& Prop){
        // 通过反射或属性名检查 (简化示意)
        return true; 
    });

    TestTrue(TEXT("ReplicatedInt should be in the lifetime properties list"), bFoundReplicatedInt);
    return true;
}
```

## Demo 示例

由于这是一个测试框架插件，其“Demo”就是它自身提供的测试用例文件。最简单的示例是查看并运行 `Engine/Plugins/Tests/CQTestExperimental/Source/CQTestExperimentalTests/` 目录下的测试源码。

```cpp
// 一个最小的、用于演示框架用法的测试文件结构
// MyMinimalIrisTest.cpp
#include "Misc/AutomationTest.h"
#include "Iris/CQTestObjects.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMinimalIrisTest,
    "Minimal.Example.IrisTest",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMinimalIrisTest::RunTest(const FString& Parameters)
{
    // 使用插件提供的对象进行最简单的断言
    AIrisTestReplicatedActor* Actor = NewObject<AIrisTestReplicatedActor>();
    TestEqual(TEXT("Default ReplicatedInt is 0"), Actor->ReplicatedInt, 0);
    return true;
}
```

## 模块依赖

要使用此插件的测试功能编写你自己的测试，你的测试模块的 `.Build.cs` 文件需要添加以下依赖：

```csharp
// 在你的 .Build.cs 文件中
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    // 依赖本测试插件的模块
    "CQTestExperimentalTests"
});
```

| 模块 | 用途 |
|---|---|
| `CQTestExperimentalTests` | 提供 Iris 测试专用对象（GameInstance, GameMode, Actor 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-06 | `34f9b137` | Mark CQ testing modules as DeveloperTool | 将 CQ 测试模块标记为开发者工具类型，明确其用途。 |
| 2026-01-10 | `d8dbe85f` | [Backout] - CL49608042 | 回退了编号为 CL49608042 的更改。 |
| 2026-01-06 | `5ccf1877` | Check disallowed modules when not linking | 在不链接时检查禁止使用的模块。 |
| 2025-07-30 | `75860784` | Fix for null entries in ClientConnections array | 修复了 ClientConnections 数组中的空指针问题。 |
| 2025-05-09 | `b9141519` | Added support for the upcoming Iris replication system as part of the new CQTestExperimental plugin | 初始提交，新增 CQTestExperimental 插件以支持即将到来的 Iris 复制系统。 |

### 维护评价

- **年龄**：插件创建于 2025 年 5 月，非常年轻。
- **更新频率**：在创建后约 9 个月（至 2026 年 2 月）有持续更新，主要涉及构建配置调整和问题修复，表明处于活跃的维护和适配阶段。
- **性质**：作为实验性功能的测试插件，其更新节奏与相关实验性功能的开发进度紧密相关。它本身不是一个需要长期稳定维护的功能插件。
- **推荐**：**仅推荐用于测试目的**。如果你正在开发或验证 Iris 等实验性引擎功能，这是官方提供的标准测试框架，应当使用。对于常规项目开发，则无需关注此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestExperimental)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/CQTestExperimental/Source/CQTestExperimentalTests)