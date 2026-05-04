# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、测试数据） |
| 模块 | `UAFCQTestSuite` (Runtime), `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

UAFTestSuites 是 **Unified Animation Framework (UAF)** 的自动化测试插件，为 UAF 动画框架的各个子系统提供全面的测试覆盖。它不是一个面向最终用户的插件，而是 Epic 内部用于验证 UAF 框架正确性的测试基础设施。

该插件覆盖以下 UAF 子系统的测试：

- **动画图 (AnimGraph)**：验证 UAF 动画图节点的编译、执行和数据流
- **动画节点 (AnimNode)**：测试动画节点的输入输出、属性绑定和执行逻辑
- **CQ 系统**：测试 UAF 的 Command Queue 机制
- **值运行时 (Value Runtime)**：测试值变换器（Transformers）、迭代器、抽象骨骼集合绑定等核心数据结构

## 使用场景

- 你是 UAF 框架的开发者，需要验证框架改动没有破坏已有功能 → 运行此插件中的自动化测试
- 你在研究 UAF 框架的内部实现，想了解各子系统的预期行为 → 阅读测试用例作为参考
- 你在为 UAF 编写新的动画节点或变换器，需要参考测试模式 → 使用 `TransformerTestUtil` 等工具编写自己的测试

**注意**：此插件仅用于开发和测试环境，不应在生产构建中启用。

## 蓝图用法

此插件不包含任何 `BlueprintCallable` 或 `BlueprintReadWrite` API。它是纯 C++ 自动化测试插件，所有测试通过 UE 自动化测试框架（`FAutomationTestBase`）执行。

## C++ 用法

### 头文件引入

```cpp
// 测试工具函数
#include "AnimNextTest.h"

// 迭代器测试工具
#include "UAF/ValueRuntime/IteratorTestUtils.h"

// 变换器测试工具
#include "UAF/ValueRuntime/Transformers/TransformerTestUtil.h"

// 变量引用测试数据
#include "AnimNextVariableReferenceTest.h"

// 变量类型测试数据
#include "AnimNextVariablesTest.h"
```

### 基本用法 — 测试清理工具

测试执行后需要清理事务缓冲区和回收垃圾内存：

```cpp
// 来源: Public/AnimNextTest.h
#include "AnimNextTest.h"

// 在测试结束时调用，清理事务缓冲区并执行垃圾回收
UE::UAF::Tests::FUtils::CleanupAfterTests();

// 获取用于测试的世界对象
UWorld* TestWorld = UE::UAF::Tests::FUtils::GetWorld();
```

### 基本用法 — 迭代器测试工具

`IteratorTestUtils.h` 提供了一组模板函数，用于测试 UAF 迭代器的行为：

```cpp
// 来源: Private/UAF/ValueRuntime/IteratorTestUtils.h
#include "UAF/ValueRuntime/IteratorTestUtils.h"

using namespace UE::UAF::Tests;

// 查找迭代器中是否包含指定值（使用投影函数）
bool bFound = FindWithBy(MyIterator, TargetValue, [](auto& It) { return It.GetValue(); });

// 使用自定义谓词查找
bool bFoundWithPred = FindWithByPredicate(MyIterator, TargetValue,
    [](auto& It) { return It.GetValue(); },
    [](const auto& A, const auto& B) { return FMath::IsNearlyEqual(A, B); });

// 获取迭代器元素数量
int32 Count = IteratorSize(MyIterator);

// 验证迭代器是否按指定顺序排序
bool bSorted = IteratorSortedByPredicate(MyIterator,
    [](auto& It) { return It.GetKey(); },  // 投影函数
    [](const auto& A, const auto& B) { return A < B; });  // 排序谓词
```

### 进阶用法 — 变换器测试框架

`TransformerTestUtil.h` 提供了用于测试 UAF 值变换器的结构化测试框架：

```cpp
// 来源: Private/UAF/ValueRuntime/Transformers/TransformerTestUtil.h
#include "UAF/ValueRuntime/Transformers/TransformerTestUtil.h"

using namespace UE::UAF::Tests;

// 1. 构建测试用的 SetBinding 资产
// 创建层级结构: Everything > SetA > SetB, SetC
auto SetBindingResult = BuildSetBinding([](TNonNullPtr<USkeleton> Skeleton)
{
    // 可选：对骨骼进行自定义修改
    // Skeleton->AddVirtualBone(...);
});

if (SetBindingResult.HasError())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to build set binding: %s"), *SetBindingResult.GetError());
    return;
}

UAbstractSkeletonSetBinding* SetBinding = SetBindingResult.GetValue();

// 2. 使用 FTransformerUnaryTest 测试单输入变换器
FTransformerUnaryTest<float, false> UnaryTest;
UnaryTest.AttributeName = FName("TestFloatAttribute");
UnaryTest.Input = 42.0f;
UnaryTest.ApplyTransformer = [](const FValueBundleHeap& InputValues, FValueBundleHeap& OutputValues)
{
    // 执行变换器逻辑
};
UnaryTest.IsExpectedResult = [](TOptional<float> Result) -> TOptional<FString>
{
    if (!Result.IsSet())
        return TEXT("Expected a result value");
    if (!FMath::IsNearlyEqual(*Result, 84.0f))
        return FString::Printf(TEXT("Expected 84.0, got %f"), *Result);
    return {}; // 通过
};

// 运行测试
UnaryTest.Run(this, NamedSet);
```

### 进阶用法 — 测试数据结构

`FAnimNextParamTypeTestStruct` 包含了 UAF 参数系统支持的所有类型，可用于验证类型序列化和参数传递：

```cpp
// 来源: Private/AnimNextVariablesTest.h
#include "AnimNextVariablesTest.h"

// 该结构体覆盖了 UAF 参数系统的所有支持类型：
// - 基础类型: bool, uint8, int32, int64, float, double
// - 位域: bBitfield0, bBitfield1
// - 字符串类型: FName, FString
// - 数学类型: FVector, FTransform, FQuat
// - 对象类型: UObject*, UClass*, TSubclassOf<>
// - 容器类型: TArray<> (各种基础类型的数组)
// - UAF 特有类型: FAnimNextParamType, EPropertyBagContainerType
```

## Demo 示例

以下是一个完整的最小测试示例，演示如何使用 UAFTestSuites 的工具编写自动化测试：

```cpp
// MyUAFCustomTest.h
#pragma once

#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"
#include "AnimNextTest.h"
#include "UAF/ValueRuntime/IteratorTestUtils.h"

// 定义一个简单的自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyUAFCustomTest,
    "UAF.Custom.ExampleTest",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMyUAFCustomTest::RunTest(const FString& Parameters)
{
    // 使用 UAF 测试工具获取测试世界
    UWorld* World = UE::UAF::Tests::FUtils::GetWorld();
    TestNotNull(TEXT("World should be valid"), World);

    // 使用迭代器工具验证数据
    TArray<int32> TestData = {1, 2, 3, 4, 5};
    auto It = TestData.CreateConstIterator();

    int32 Count = UE::UAF::Tests::IteratorSize(It);
    TestEqual(TEXT("Iterator should have 5 elements"), Count, 5);

    // 验证排序
    It = TestData.CreateConstIterator();
    bool bSorted = UE::UAF::Tests::IteratorSortedByPredicate(
        It,
        [](auto& Iter) { return *Iter; },
        [](int32 A, int32 B) { return A < B; });
    TestTrue(TEXT("Data should be sorted"), bSorted);

    // 测试完成后清理
    UE::UAF::Tests::FUtils::CleanupAfterTests();

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | Unified Animation Framework 核心模块，提供动画图、值运行时等基础设施 |
| `RigVM` | RigVM 虚拟机，UAF 动画图的执行引擎 |
| `AnimNextRuntime` | AnimNext 运行时模块 |

## 维护状态

### 近期更新

由于该插件创建于 2026-03-30，属于较新的实验性插件，暂无足够历史 commit 记录可供分析。

### 维护评价

- **创建时间**：2026-03-30，非常新的插件
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，明确标记为实验性
- **活跃度**：作为 UAF 框架的测试套件，预计会随 UAF 框架的开发持续更新
- **代码质量**：测试覆盖全面，包含迭代器工具、变换器测试框架、类型覆盖测试等，结构清晰
- **推荐使用**：仅推荐 UAF 框架开发者使用。如果你不是 UAF 的贡献者，此插件对你的项目没有直接价值

⚠️ **注意**：此插件是实验性 UAF 框架的一部分，API 可能随时发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [UAF 主插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)