# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 中文名 | UAF自动化测试套件 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产与代码） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

UAFTestSuites 是一套专门为 Unreal Animation Framework (UAF) 构建的自动化测试插件。它并非面向最终用户的功能插件，而是 UAF 开发团队内部使用的测试基础设施。该插件包含了一系列用于验证 UAF 核心系统正确性、稳定性和性能的测试用例、测试数据结构和测试辅助工具。它解决了 UAF 开发过程中对动画图、动画节点、可绑定数据结构等关键组件进行回归测试和性能基准测试的问题。

## 使用场景

- 你是 UAF 框架的开发者或贡献者，需要为新增或修改的动画节点编写单元测试。
- 你需要验证 `FBindableXxx` 类型的属性绑定、序列化和反序列化是否正确工作。
- 你需要对动画图的更新逻辑或变量解析功能进行压力测试和性能基准测试。
- 你需要一个包含各种基本数据类型（bool, float, vector, transform等）的标准化测试数据结构，以简化测试用例的编写。

## 蓝图用法

此插件为**测试专用**，主要面向 C++ 自动化测试框架，不提供公开的蓝图 API。其内部结构主要用于支持 C++ 测试用例的运行。

## C++ 用法

该插件提供了丰富的测试数据结构和测试节点，用于编写 UAF 相关的自动化测试。

### 头文件引入

根据测试的具体目标，引入对应的测试模块头文件。例如：
```cpp
#include "UAFAnimNodeTestVars.h"
#include "UAFTestBindableTraitData.h"
```

### 基本用法：使用测试数据结构

`UAFAnimNodeTestData` 模块提供了覆盖常见数据类型的测试结构体，可用于构造测试用例。

```cpp
// 来源: UAFAnimNodeTestData/Public/UAFAnimNodeTestVars.h
// 创建一个包含多种数据类型的测试实例，用于验证属性绑定
FUAFAnimNodeTestVars TestVars;
TestVars.bBool = true;
TestVars.FloatVal = 3.14f;
TestVars.VectorVar = FVector(100.f, 200.f, 300.f);
TestVars.QuatVar = FQuat(FVector::UpVector, PI/4.f);

// 对于性能测试，可以使用专为基准测试设计的结构体
FUAFAnimNodePerfVars10 PerfTestVars;
PerfTestVars.f0 = 1.0f;
PerfTestVars.v0 = FVector(1.f, 2.f, 3.f);
// ... 为 f0-f9, v0-v9 赋值，用于后续的批量绑定性能测试
```

### 进阶用法：测试可绑定特性（Trait）数据

`UAFTestBindableTraitData` 模块演示了如何为特性（Trait）系统编写涉及 `FBindable` 属性的测试，特别是验证 `SetPinDefaultValue` 的往返（round-trip）行为。

```cpp
// 来源: UAFTestBindableTraitData/Public/UAFTestBindableTraitData.h
// 1. 获取或创建一个特性共享数据的实例
FUAFTestBindableTraitSharedData TraitData;
// 2. 通过RigVM控制器设置其FBindableBool属性的默认值
//    这个过程会测试序列化、文本比较和变更检测
Controller->SetPinDefaultValue(/* PinPath */, TEXT("true"));
// 3. 验证控制器是否正确地检测到了值的变化
//    (在CQTests中，这通常通过检查事务（Transaction）或脏状态来完成)
```

## Demo 示例

以下是一个最小化的 C++ 自动化测试用例框架，用于测试一个简单的 `FBindableFloat` 属性解析。

```cpp
// MyUAFBindingTest.h
#pragma once
#include "Misc/AutomationTest.h"

// 使用 IMPLEMENT_SIMPLE_AUTOMATION_TEST 宏定义一个简单的自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyUAFBindingTest, // 测试类名
    "MyProject.UAF.Binding.FloatResolvesCorrectly", // 测试在编辑器中的路径
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter
)
```

```cpp
// MyUAFBindingTest.cpp
#include "MyUAFBindingTest.h"
#include "UAFAnimNodeTestVars.h" // 引入测试数据结构

bool FMyUAFBindingTest::RunTest(const FString& Parameters)
{
    // 准备阶段：创建测试数据
    FUAFAnimNodeTestVars TestVars;
    TestVars.FloatVal = 42.0f;

    // 创建一个FBindableFloat，并将其绑定到TestVars的FloatVal属性
    UE::UAF::FBindableFloat BoundFloat;
    BoundFloat.BindToVariable(&FUAFAnimNodeTestVars::FloatVal);

    // 执行阶段：在模拟的更新上下文中解析值
    // （注：真实的FAnimGraphUpdateContext需要通过复杂的测试框架构造）
    // FUAFAnimGraphUpdateContext Context = ...;
    // float ResolvedValue = BoundFloat.Resolve(Context, &TestVars);

    // 验证阶段
    // TestEqual(TEXT("Resolved float value should match source property"), ResolvedValue, 42.0f);

    return true; // 实际应由TestEqual等宏决定返回值
}
```

## 模块依赖

作为测试套件，该插件内部的模块会依赖 UAF 核心模块。使用者（即测试项目）需要确保以下模块可用：

| 模块 | 用途 |
|---|---|
| `AnimNext` | UAF动画框架的核心运行时模块 |
| `ControlRig` | 用于支持涉及控制绑定的测试 |
| `AutomationTest` (引擎) | UE自动化测试框架基础 |
| `UAFCore` | （推断）UAF框架的核心模块，提供 `FUAFAnimNodeData` 等基础类 |
| `RigVM` | （推断）用于测试涉及RigVM蓝图控制器的功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告，提升代码在MSVC和Clang下的兼容性。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化说明符与参数位宽不匹配的问题，避免未定义行为。 |
| 2026-04-14 | `12eb7efc` | Fix FBindableXxx binding serialization issues when used with UAF traits | 修复了可绑定类型在UAF特性中使用时的序列化问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将GetComponent重命名为GetOrAddComponent以更准确反映其功能。 |

### 维护评价

该插件处于**活跃维护**状态。
- **创建时间**：非常新（2026年2月创建）。
- **更新频率**：近期（截至2026年5月）有多次提交，虽然多为编译器警告修复、格式修正和日志宏迁移等维护性工作，但表明该插件仍在持续被关注和改进。
- **活跃度**：作为 UAF 的官方测试套件，其生命周期与 UAF 框架的开发紧密绑定。只要 UAF 框架仍在积极开发，此测试插件就会持续维护。
- **已知问题**：暂无已知的阻碍性问题。其“实验性”状态表明其接口和结构可能会随着 UAF 的迭代而发生变化。
- **推荐**：**仅推荐**给参与 UAF 框架开发或为其编写扩展的开发者使用。对于普通项目，无需启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites/Source) （测试代码位于各模块的源码目录中）