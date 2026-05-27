# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 中文名 | UAF 自动化测试 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产与测试用例） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

本插件是 UAF（Unified Animation Framework）的自动化测试套件，**仅面向 UAF 框架开发者**，不面向最终用户。

它为 UAF 的核心子系统提供全面的自动化测试覆盖，包括：

- **值运行时（Value Runtime）测试**：验证 Transformer（变换器）在 bound/unbound 属性上的正确性，支持一元和二元变换器的原地（in-place）和非原地（out-of-place）操作
- **动画图（AnimGraph）测试**：测试 UAF 动画图节点的执行与计算
- **动画节点数据测试**：提供各种参数类型的测试数据结构（bool、int、float、FVector、FTransform、FQuat、TObjectPtr、TArray 等），用于验证 RigVM 参数系统
- **变量引用测试**：验证属性重命名等序列化兼容性
- **迭代器测试**：提供通用的迭代器查找、排序验证工具

该插件的存在是为了保证 UAF 在频繁迭代中不发生回归，是 UAF 质量保障体系的一部分。

## 使用场景

- 你是 UAF 框架的开发者，需要验证 Transformer 的数学计算正确性 → 本插件的 `FTransformerUnaryTest` / `FTransformerBinaryTest` 工具类
- 你需要测试 RigVM 参数绑定是否支持所有基础类型 → 参考 `FAnimNextParamTypeTestStruct` 中列出的完整类型覆盖
- 你在修改 UAF 值运行时的迭代器实现 → 使用 `IteratorTestUtils.h` 中的通用验证工具
- 你需要在 UAF 测试前后清理状态 → 使用 `FUtils::CleanupAfterTests()`

## 蓝图用法

本插件为纯测试模块，**不提供面向用户的蓝图节点**。`AnimNextVariablesTest.h` 中的 `UAnimNextTestFuncLib` 仅供内部自动化测试使用：

### 测试辅助节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetObj` | 获取测试用的 FuncLib 单例（内部测试用） | `UAnimNextTestFuncLib` |
| `GetValueB` | 返回测试值 42（内部测试用） | `UAnimNextTestFuncLib` |
| `GetValueC` | 返回测试值 12345（内部测试用） | `UAnimNextTestFuncLib` |

> ⚠️ 这些节点标记为 `BlueprintCallable`，但属于测试基础设施，不建议在生产蓝图中使用。

## C++ 用法

本插件的 C++ API 全部为测试辅助工具，供编写 UAF 自动化测试时使用。

### 头文件引入

```cpp
#include "UAF/ValueRuntime/Transformers/TransformerTestUtil.h"
#include "UAF/ValueRuntime/IteratorTestUtils.h"
#include "Public/AnimNextTest.h"
```

### 基本用法 — Transformer 一元测试

使用 `FTransformerUnaryTest` 验证单输入 Transformer 的正确性。来源：`Private/UAF/ValueRuntime/Transformers/TransformerTestUtil.h`

```cpp
// 定义一个一元变换器测试：对 float 类型的 "Weight" 属性执行变换
UE::UAF::Tests::FTransformerUnaryTest<float, false> UnaryTest;
UnaryTest.AttributeName = FName("Weight");
UnaryTest.Input = 0.5f;

// 定义如何应用变换器
UnaryTest.ApplyTransformer = [](const FValueBundleHeap& Input, FValueBundleHeap& Output)
{
    // 调用被测 Transformer
    // MyTransformer::Apply(Input, Output);
};

// 定义如何验证结果
UnaryTest.IsExpectedResult = [](TOptional<float> Result) -> TOptional<FString>
{
    if (!Result.IsSet())
    {
        return TEXT("Expected result to be set");
    }
    if (!FMath::IsNearlyEqual(*Result, 1.0f))
    {
        return FString::Printf(TEXT("Expected 1.0, got %f"), *Result);
    }
    return {};  // 无错误，测试通过
};

// 执行测试
UnaryTest.Run(this /* FAutomationTestBase* */, NamedSet);
```

### 基本用法 — 迭代器测试工具

使用 `IteratorTestUtils.h` 中的模板函数验证迭代器行为。来源：`Private/UAF/ValueRuntime/IteratorTestUtils.h`

```cpp
using namespace UE::UAF::Tests;

// 检查迭代器中是否包含特定值
bool bFound = FindWithBy(MyIterator, ExpectedValue, [](auto& It) { return It.GetValue(); });

// 获取迭代器大小
int32 Size = IteratorSize(MyIterator);

// 验证迭代器是否按指定顺序排序
bool bSorted = IteratorSortedByPredicate(MyIterator,
    [](auto& It) { return It.GetSortKey(); },  // 投影函数
    [](const auto& A, const auto& B) { return A < B; }  // 排序谓词
);
```

### 基本用法 — 测试清理

```cpp
#include "AnimNextTest.h"

// 在每个测试用例结束后调用，清理事务缓冲区和垃圾回收
UE::UAF::Tests::FUtils::CleanupAfterTests();

// 获取测试用 World
UWorld* TestWorld = UE::UAF::Tests::FUtils::GetWorld();
```

### 进阶用法 — Transformer 二元测试与 Layer 特化

`FTransformerBinaryTest` 支持双输入变换器测试，并且对 `FLayer` 提供了模板特化。来源：`Private/UAF/ValueRuntime/Transformers/TransformerTestUtil.h`

```cpp
// 标准二元变换器测试（非 Layer）
using namespace UE::UAF::Tests;

FTransformerBinaryTest<FMyAddTransformer, float, EInplaceTransformationSupport::Allow> BinaryTest;
BinaryTest.AttributeName = FName("Value");
BinaryTest.InputA = 1.0f;
BinaryTest.InputB = 2.0f;
BinaryTest.ApplyTransformer = [](const FValueBundleHeap& A, const FValueBundleHeap& B, FValueBundleHeap& Out)
{
    // FMyAddTransformer::Apply(A, B, Out);
};
BinaryTest.IsExpectedResult = [](TOptional<float> R) -> TOptional<FString>
{
    return R.IsSet() && FMath::IsNearlyEqual(*R, 3.0f) ? TOptional<FString>{} : TEXT("Expected 3.0");
};
BinaryTest.Run(this, NamedSet);
```

```cpp
// Layer 变换器的特化测试（支持 base/layer 两个 NamedSet）
FTransformerBinaryTest<Transformers::FLayer, float, EInplaceTransformationSupport::Allow> LayerTest;
LayerTest.AttributeName = FName("Alpha");
LayerTest.WeightB = 0.75f;
LayerTest.InputA = 1.0f;       // base 值
LayerTest.InputB = 0.5f;       // layer 值
LayerTest.IsExpectedResult = [](TOptional<float> R) -> TOptional<FString>
{
    return R.IsSet() ? TOptional<FString>{} : TEXT("Expected a value");
};
// Layer 测试需要两个 NamedSet：base 和 layer
LayerTest.Run(this, NamedSetBase, NamedSetLayer);
```

### SetBinding 构建工具

测试中经常需要构建 `UAbstractSkeletonSetBinding`，`BuildSetBinding` 辅助函数简化了这一过程：

```cpp
using namespace UE::UAF::Tests;

// 构建一个带 SetA > SetB, SetC 层级的 SetBinding
auto Result = BuildSetBinding([](TNonNullPtr<USkeleton> Skeleton)
{
    // 可选：对骨架进行修改
    // 例如添加骨骼等
});

if (Result.HasError())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to build set binding: %s"), *Result.GetError());
    return;
}

UAbstractSkeletonSetBinding* SetBinding = Result.GetValue();
// SetBinding 现在包含：
// (Everything Set)
// \_ SetA
//    \_ SetB
//    \_ SetC
```

## Demo 示例

以下是一个完整的自动化测试示例，展示如何使用测试工具类验证自定义 Transformer：

```cpp
// MyTransformerTest.h
#pragma once

#include "Misc/AutomationTest.h"
#include "UAF/ValueRuntime/Transformers/TransformerTestUtil.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyFloatTransformerTest,
    "UAF.ValueRuntime.Transformers.MyFloatTransformer",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

// MyTransformerTest.cpp
#include "MyTransformerTest.h"
#include "AnimNextTest.h"

bool FMyFloatTransformerTest::RunTest(const FString& Parameters)
{
    using namespace UE::UAF::Tests;

    // 构建测试用 SetBinding
    auto SetBindingResult = BuildSetBinding(nullptr);
    if (SetBindingResult.HasError())
    {
        AddError(FString::Printf(TEXT("Failed to build SetBinding: %s"), *SetBindingResult.GetError()));
        return false;
    }

    FAttributeNamedSetPtr NamedSet = /* 从 SetBinding 获取 */;

    // 测试：float 乘法变换器，输入 2.0，期望输出 6.0（乘以 3.0）
    FTransformerUnaryTest<float, false> Test;
    Test.AttributeName = FName("Multiplier");
    Test.Input = 2.0f;

    Test.ApplyTransformer = [](const FValueBundleHeap& Input, FValueBundleHeap& Output)
    {
        // 调用你的 MyMultiplyTransformer::Apply
        // 为简洁起见，这里假设变换器将值乘以 3
        Output = Input;
        // ... 实际的变换逻辑
    };

    Test.IsExpectedResult = [](TOptional<float> Result) -> TOptional<FString>
    {
        if (!Result.IsSet())
        {
            return TEXT("Result should be set");
        }
        if (!FMath::IsNearlyEqual(*Result, 6.0f, KINDA_SMALL_NUMBER))
        {
            return FString::Printf(TEXT("Expected 6.0, got %f"), *Result);
        }
        return {};  // 通过
    };

    Test.Run(*this, NamedSet);

    // 清理
    FUtils::CleanupAfterTests();

    return true;
}
```

## 模块依赖

从 Build.cs 提取。由于本插件为测试专用，依赖的是 UAF 框架本身的模块：

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 核心框架，提供 ValueBundle、AttributeSet、Transformer 等基础类型 |
| `AnimNextRuntime` | 动画运行时，提供 AnimNext 执行上下文与 RigVM 集成 |
| `PropertyBag` | 属性包系统，用于测试 EPropertyBagContainerType 等类型 |

> 部分模块依赖可能未完整列出（Build.cs 文件未提供完整内容）。实际构建时请参考 `Source/UAFTestSuite/UAFTestSuite.Build.cs`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告，确保 MSVC 和 Clang 编译器兼容 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-14 | `12eb7efc` | Fix FBindableXxx binding serialization issues when used with UAF traits | 修复 FBindableXxx 与 UAF traits 配合时的序列化问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将 GetComponent 重命名为 GetOrAddComponent 以匹配实际行为 |

### 维护评价

- **状态**：🆕 新建项目，处于活跃开发阶段
- **年龄**：创建于 2026-02-10，距今约 3 个月
- **更新频率**：近 1 个月内有 5 次提交，更新频繁，涵盖编译器兼容修复、bug 修复、重构和代码清理
- **实验性标记**：`IsExperimentalVersion=true`，属于实验性插件
- **来源**：由 UAFTests 重命名而来（2026-02-10 首次提交），说明 UAF 测试基础设施在持续规范化
- **风险提示**：作为实验性测试插件，API 随 UAF 框架同步变动，不建议外部项目依赖
- **推荐度**：仅推荐 UAF 框架开发者使用和维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [UAF 主插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)（本测试套件所测试的目标框架）