# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 中文名 | UAF 测试套件 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

UAFTestSuites 是 **UAF（Unified Animation Framework，统一动画框架）** 的自动化测试插件，专门为 UAF 核心系统提供全面的单元测试和集成测试覆盖。

该插件解决的核心问题是：UAF 框架引入了一套全新的属性值绑定、值变换器（Transformer）、迭代器和动画图系统，这些系统涉及复杂的数据流和内存管理（绑定值/非绑定值的双通道处理）。UAFTestSuites 提供了结构化的测试基础设施，确保：

- **值变换器**（如 Layer 混合、一元/二元变换）在 bound 和 unbound 两种通道上均能正确工作
- **动画图节点**（RigVM 结构体）的输入输出计算正确
- **属性类型系统**覆盖所有基础类型（bool、int、float、FVector、FTransform、FQuat 等）及数组变体
- **迭代器**的查找、排序、投影功能正常
- **变量引用**和序列化在重命名等场景下保持稳定

插件存在的意义是为 UAF 实验性框架的质量保驾护航——没有这套测试，UAF 的持续重构和迭代将充满风险。

## 使用场景

- 你是 **UAF 框架开发者**，需要验证对值变换器的改动没有引入回归 → 运行 UAFTestSuites 中的 Transformer 测试
- 你在 **开发新的 UAF 动画图节点**，需要确保 RigVM 结构体的输入输出正确 → 参考测试用例编写自己的测试
- 你在 **扩展 UAF 属性类型系统**，需要验证新类型的 bound/unbound 双通道处理 → 使用 `FTransformerUnaryTest` / `FTransformerBinaryTest` 测试模板
- 你在 **排查 UAF 值变换 Bug**，需要一个干净的测试骨架和 SetBinding 设置 → 使用 `BuildSetBinding` 工具函数快速构造测试环境

## 蓝图用法

该插件主要面向自动化测试，公开的蓝图 API 非常有限。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetObj` | 获取 UAnimNextTestFuncLib 测试单例对象 | `UAnimNextTestFuncLib` |
| `GetValueB` | 返回测试值 B（默认 42） | `UAnimNextTestFuncLib` |
| `GetValueC` | 返回测试值 C（默认 12345） | `UAnimNextTestFuncLib` |

> ⚠️ 这些节点仅供测试使用，不应用于生产代码。

### 使用示例（蓝图描述）

在蓝图测试中：
1. 调用 `GetObj`（传入 `UUAFComponent`）获取测试函数库单例
2. 调用 `GetValueB` / `GetValueC` 验证函数库的值访问机制
3. 这些测试主要验证蓝图与 C++ 函数库的交互是否正常

## C++ 用法

### 头文件引入

```cpp
#include "AnimNextTest.h"
// 测试工具（仅在测试模块内可用）
#include "UAF/ValueRuntime/Transformers/TransformerTestUtil.h"
#include "UAF/ValueRuntime/IteratorTestUtils.h"
#include "AnimNextVariablesTest.h"
```

### 基本用法：构建测试用 SetBinding

来源：`Private/UAF/ValueRuntime/Transformers/TransformerTestUtil.h`

```cpp
using namespace UE::UAF::Tests;

// 创建一个用于测试的 SetBinding，包含预定义的层次结构
// (Everything Set) → SetA → SetB, SetC
auto SetBindingResult = BuildSetBinding([](TNonNullPtr<USkeleton> Skeleton)
{
    // 可选：对骨架进行自定义修改
});

if (SetBindingResult.HasValue())
{
    UAbstractSkeletonSetBinding* Binding = SetBindingResult.GetValue();
    // 使用 Binding 进行后续测试...
}
```

### 基本用法：一元变换器测试

来源：`Private/UAF/ValueRuntime/Transformers/TransformerTestUtil.h`

```cpp
// 测试一个对单个属性执行的变换器
FTransformerUnaryTest<float, false> Test;
Test.AttributeName = FName("MyFloatAttribute");
Test.Input = 3.14f;

// 定义如何应用变换器（支持 in-place 和 out-of-place）
Test.ApplyTransformer = [](const FValueBundleHeap& Input, FValueBundleHeap& Output)
{
    // 执行变换逻辑...
};

// 定义预期结果验证
Test.IsExpectedResult = [](TOptional<float> Result) -> TOptional<FString>
{
    if (!Result.IsSet())
        return FString("结果为空");
    if (!FMath::IsNearlyEqual(*Result, 6.28f))
        return FString::Printf(TEXT("期望 6.28，实际 %f"), *Result);
    return {};  // 通过
};

// 运行测试（自动测试 bound 和 unbound 两种通道）
Test.Run(*this, NamedSet);
```

### 进阶用法：二元变换器测试与 Inplace 支持

来源：`Private/UAF/ValueRuntime/Transformers/TransformerTestUtil.h`

```cpp
// 测试接受两个输入的变换器（如加法、混合等）
FTransformerBinaryTest<FMyAddTransformer, float, EInplaceTransformationSupport::Allow> Test;
Test.AttributeName = FName("Weight");
Test.InputA = 1.0f;
Test.InputB = 2.0f;

Test.ApplyTransformer = [](const FValueBundleHeap& A, const FValueBundleHeap& B, FValueBundleHeap& Out)
{
    // 二元变换逻辑...
};

Test.IsExpectedResult = [](TOptional<float> Result) -> TOptional<FString>
{
    if (!Result.IsSet())
        return FString("结果为空");
    if (!FMath::IsNearlyEqual(*Result, 3.0f))
        return FString::Printf(TEXT("期望 3.0，实际 %f"), *Result);
    return {};
};

// Run 会自动测试：Out-of-place、In-place A、In-place B 三种模式
Test.Run(*this, NamedSet);
```

### 进阶用法：Layer 变换器的特殊测试

来源：`Private/UAF/ValueRuntime/Transformers/TransformerTestUtil.h`

```cpp
// FLayer 变换器有专门的模板特化，支持 base/layer 双命名集
FTransformerBinaryTest<Transformers::FLayer, FQuat, EInplaceTransformationSupport::Allow> LayerTest;
LayerTest.AttributeName = FName("Rotation");
LayerTest.WeightB = 0.5f;  // Layer 权重
LayerTest.InputA = FQuat::Identity;       // Base 值
LayerTest.InputB = FQuat(FRotator(0, 90, 0));  // Layer 值

LayerTest.IsExpectedResult = [](TOptional<FQuat> Result) -> TOptional<FString>
{
    // 验证加权混合结果
    return {};
};

// Layer 测试需要两个命名集（base 和 layer）
LayerTest.Run(*this, NamedSetBase, NamedSetLayer);
```

### 进阶用法：迭代器工具函数

来源：`Private/UAF/ValueRuntime/IteratorTestUtils.h`

```cpp
using namespace UE::UAF::Tests;

// 查找迭代器中包含指定值的元素（带投影函数）
bool bFound = FindWithBy(MyIterator, TargetValue, [](auto& It) { return It.GetValue(); });

// 带自定义谓词的查找
bool bFoundCustom = FindWithByPredicate(MyIterator, TargetValue,
    [](auto& It) { return It.GetKey(); },
    [](const auto& A, const auto& B) { return A.Compare(B) == 0; });

// 获取迭代器大小
int32 Count = IteratorSize(MyIterator);

// 验证迭代器是否已排序
bool bSorted = IteratorSortedByPredicate(MyIterator,
    [](auto& It) { return It.GetValue(); },
    [](float A, float B) { return A <= B; });
```

### 进阶用法：测试清理

来源：`Public/AnimNextTest.h`

```cpp
using namespace UE::UAF::Tests;

// 每个测试结束后清理环境（清除事务缓冲区、回收垃圾）
FUtils::CleanupAfterTests();

// 获取测试用 World
UWorld* TestWorld = FUtils::GetWorld();
```

## Demo 示例

一个完整的测试用例，演示如何测试一个自定义值变换器：

```cpp
// MyTransformerTest.h
#pragma once

#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"
#include "AnimNextTest.h"
#include "UAF/ValueRuntime/Transformers/TransformerTestUtil.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyAddTransformerTest,
    "UAF.Transformers.Add",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMyAddTransformerTest::RunTest(const FString& Parameters)
{
    using namespace UE::UAF::Tests;

    // 1. 构建测试用 SetBinding
    auto BindingResult = BuildSetBinding(nullptr);
    if (!BindingResult.HasValue())
    {
        AddError(FString::Printf(TEXT("Failed to build SetBinding: %s"), *BindingResult.GetError()));
        return false;
    }

    // 2. 配置一元变换器测试
    FTransformerUnaryTest<float, false> FloatTest;
    FloatTest.AttributeName = FName("Speed");
    FloatTest.Input = 5.0f;

    FloatTest.ApplyTransformer = [](const FValueBundleHeap& In, FValueBundleHeap& Out)
    {
        // 模拟一个将值翻倍的变换器
        // 实际实现会调用真正的 Transformer::Apply
    };

    FloatTest.IsExpectedResult = [](TOptional<float> Result) -> TOptional<FString>
    {
        if (!Result.IsSet())
            return TEXT("结果为空");
        if (!FMath::IsNearlyEqual(*Result, 10.0f))
            return FString::Printf(TEXT("期望 10.0, 实际 %f"), *Result);
        return {};
    };

    // 3. 运行测试
    FloatTest.Run(*this, BindingResult.GetValue()->GetNamedSet());

    // 4. 清理
    FUtils::CleanupAfterTests();

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 核心框架（属性绑定、值变换器、值空间等） |
| `RigVM` | 动画图运行时（FRigVMStructMutable 基类） |
| `AnimNextCore` | 动画框架核心（FAnimNextParamType 等类型） |

> 该插件作为测试套件，依赖被测系统的所有核心模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复 MSVC 与 Clang 间的函数类型转换警告兼容性 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串中 32/64 位说明符不匹配的问题 |
| 2026-04-14 | `12eb7efc` | Fix FBindableXxx binding serialization issues when used with UAF traits | 修复 UAF 特性系统中 FBindableXxx 的序列化问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将 GetComponent 重命名为 GetOrAddComponent 以更准确反映其功能 |

### 维护评价

UAFTestSuites 是一个 **活跃维护中** 的实验性测试插件：

- **创建时间**：2026-02-10，非常年轻（约 3 个月）
- **更新频率**：近 1 个月内有 4 次提交，更新密集
- **更新内容**：主要是编译警告修复、格式化修复、序列化修复等质量改进，说明 UAF 框架仍处于快速迭代阶段
- **实验性状态**：`IsExperimentalVersion=true`，属于 UAF 实验性框架的一部分
- **注意事项**：作为实验性插件，API 和测试结构可能随 UAF 框架的演进而大幅变更
- **推荐使用**：✅ 强烈推荐 UAF 框架开发者使用，这是验证 UAF 系统正确性的核心测试基础设施。非 UAF 开发者无需关注。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites/Source)