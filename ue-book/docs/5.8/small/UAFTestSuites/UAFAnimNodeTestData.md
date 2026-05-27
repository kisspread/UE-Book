# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 中文名 | UAF测试套件 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试数据资产、测试用结构体） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

本插件是 **UAF（Unreal Animation Framework）** 的自动化测试套件，专为验证 UAF 动画框架的核心功能而存在。它不提供任何面向最终用户的运行时功能，而是为引擎开发者提供以下测试基础设施：

1. **可绑定类型测试数据**：提供覆盖所有常见 `FBindableXxx` 类型（Bool、Float、Double、Int32、Int64、Byte、Name、Vector、Quat、Transform、Object、Enum、Struct）的测试结构体，用于验证变量绑定、子属性绑定、序列化等核心路径。
2. **性能基准测试数据**：包含 10 属性批量绑定结构体 `FUAFAnimNodePerfVars10`，用于 FBindableXxx 批量解析的性能基准测试。
3. **Trait 测试基础设施**：提供带有 `FBindableBool` 属性的测试 Trait 共享数据，用于验证 RigVM 控制器对 Trait Pin 默认值设置的检测。
4. **动画图测试与 CQ 测试**：其他模块（UAFAnimGraphTestSuite、UAFCQTestSuite、UAFTestSuite）提供动画图节点测试和代码质量测试用例。

**本质上，这个插件是 UAF 框架的"测试夹具"——它存在的唯一目的是确保 UAF 的核心功能在引擎开发过程中不被破坏。**

## 使用场景

- **UAF 框架开发者**：在修改 FBindable 类型、动画节点数据、Trait 系统后，运行此测试套件验证回归。
- **动画系统贡献者**：在提交涉及 FBindableXxx 序列化或属性绑定的改动时，通过此套件的测试用例确认兼容性。
- **性能优化工程师**：利用 FUAFAnimNodePerfVars10 进行批量变量绑定的性能基准测试。

> ⚠️ **注意**：此插件为内部测试用途，不建议在生产项目中启用。默认未启用（`Installed=false`）。

## 蓝图用法

本插件为纯 C++ 测试套件，**不提供任何蓝图可调用节点**。所有结构体均标记为测试用途或隐藏（`meta=(Hidden)`），不面向蓝图暴露。

## C++ 用法

### 头文件引入

```cpp
#include "UAFAnimNodeTestVars.h"
#include "UAFTestBindableTraitData.h"
```

### 基本用法：测试变量结构体

以下代码展示了如何使用 `FUAFAnimNodeTestVars` 覆盖所有常见绑定类型的测试场景。

```cpp
// 来源: Source/UAFAnimNodeTestData/Public/UAFAnimNodeTestVars.h

// 创建一个包含所有常见可绑定类型的测试实例
FUAFAnimNodeTestVars TestVars;

// 设置基础类型
TestVars.bBool = true;
TestVars.FloatVal = 3.14f;
TestVars.DoubleVal = 2.718281828;
TestVars.IntVal = 42;

// 设置数学类型
TestVars.VectorVar = FVector(1.0f, 2.0f, 3.0f);
TestVars.QuatVar = FQuat(FVector::UpVector, PI / 4.0f);
TestVars.TransformVar = FTransform(FRotator(0, 90, 0), FVector(100, 0, 0));

// 设置嵌套结构体
TestVars.NestedVar.Vec = FVector(10, 20, 30);
TestVars.NestedVar.Quat = FQuat::Identity;
TestVars.NestedVar.Transform = FTransform::Identity;
```

### 基本用法：可绑定动画节点数据

`FUAFTestAnimNodeData` 展示了 UAF 动画节点如何使用 `FBindableXxx` 类型系统：

```cpp
// 来源: Source/UAFAnimNodeTestData/Public/UAFAnimNodeTestVars.h

using namespace UE::UAF;

// 创建测试动画节点数据
FUAFTestAnimNodeData NodeData;

// 设置各种 FBindable 类型（默认值已在构造时初始化）
// FBindableBool - 布尔绑定
NodeData.BoolVal = FBindableBool(true);

// FBindableFloat / FBindableDouble - 浮点绑定
NodeData.FloatVal = FBindableFloat(3.14f);
NodeData.DoubleVal = FBindableDouble(2.718);

// FBindableInt32 / FBindableInt64 / FBindableByte - 整型绑定
NodeData.Int32Val = FBindableInt32(100);
NodeData.Int64Val = FBindableInt64(100000LL);
NodeData.ByteVal = FBindableByte(255);

// FBindableVector / FBindableQuat / FBindableTransform - 数学类型绑定
NodeData.VectorVal = FBindableVector(FVector(1, 2, 3));
NodeData.QuatVal = FBindableQuat(FQuat::Identity);
NodeData.TransformBindableVal = FBindableTransform(FTransform::Identity);

// FBindableEnum - 枚举绑定
NodeData.EnumVal = FBindableEnum(EUAFAnimNodeTestEnum::Gamma);

// FBindableStruct - 结构体绑定（用于子属性绑定测试）
NodeData.StructVal = FBindableStruct(FUAFAnimNodeTestVars{});
```

### 进阶用法：性能基准数据

`FUAFAnimNodePerfVars10` 用于批量变量绑定和子属性绑定的性能测试：

```cpp
// 来源: Source/UAFAnimNodeTestData/Public/UAFAnimNodeTestVars.h

FUAFAnimNodePerfVars10 PerfVars;

// 10 个 float 目标用于变量绑定基准测试
PerfVars.f0 = 1.0f;
PerfVars.f1 = 2.0f;
// ... f2 ~ f9

// 10 个 FVector 源用于子属性绑定基准测试（绑定 .X → f0..f9）
PerfVars.v0 = FVector(10.0f, 0, 0);  // .X 绑定到 f0
PerfVars.v1 = FVector(20.0f, 0, 0);  // .X 绑定到 f1
// ... v2 ~ v9
```

### 进阶用法：Trait 共享数据测试

`FUAFTestBindableTraitSharedData` 用于验证 RigVM 控制器对 Trait Pin 的 `SetPinDefaultValue` 检测：

```cpp
// 来源: Source/UAFAnimNodeTestData/Public/UAFTestBindableTraitData.h

using namespace UE::UAF;

// 创建 Trait 共享数据实例
FUAFTestBindableTraitSharedData TraitData;

// 设置 FBindableBool 默认值
// RigVM 控制器应能通过文本比较检测到值变化
TraitData.bTestBool = FBindableBool(true);

// FTestBindableTrait 用于确保 FRigDecorator_AnimNextCppDecorator
// 能在 AddTrait 期间正确解析共享数据结构到已注册的 Trait
```

## Demo 示例

一个最小化的测试结构体使用示例，展示如何创建和操作测试变量：

```cpp
// MyTestHelper.h
#pragma once

#include "UAFAnimNodeTestVars.h"
#include "UAFTestBindableTraitData.h"

struct FMyUAFTestHelper
{
    /** 创建一组预填充的测试变量，用于变量绑定测试 */
    static FUAFAnimNodeTestVars CreateDefaultTestVars();
    
    /** 创建 10 属性性能基准数据 */
    static FUAFAnimNodePerfVars10 CreatePerfBenchmarkData();
};
```

```cpp
// MyTestHelper.cpp
#include "MyTestHelper.h"

FUAFAnimNodeTestVars FMyUAFTestHelper::CreateDefaultTestVars()
{
    FUAFAnimNodeTestVars Vars;
    Vars.bBool = true;
    Vars.FloatVal = 1.0f;
    Vars.DoubleVal = 2.0;
    Vars.IntVal = 42;
    Vars.VectorVar = FVector::ForwardVector;
    Vars.QuatVar = FQuat::Identity;
    Vars.TransformVar = FTransform::Identity;
    Vars.NestedVar.Vec = FVector(10, 20, 30);
    return Vars;
}

FUAFAnimNodePerfVars10 FMyUAFTestHelper::CreatePerfBenchmarkData()
{
    FUAFAnimNodePerfVars10 Perf;
    for (int32 i = 0; i < 10; ++i)
    {
        // 使用反射设置避免硬编码 f0~f9
        // 此处为简化展示，实际测试中通过属性路径访问
    }
    Perf.v0 = FVector(1.0f, 0, 0);
    Perf.v1 = FVector(2.0f, 0, 0);
    return Perf;
}
```

## 模块依赖

由于本插件为测试用途，其依赖主要为 UAF 框架本身。无特殊对外依赖（仅标准 Core/Engine/Slate 等 + UAF 内部模块）。

| 模块 | 用途 |
|---|---|
| `AnimNextEditor` | 动画节点编辑器支持（UAFCQTestSuite 模块） |
| `UAF` | UAF 动画框架核心（被测对象） |
| `AnimNext` | AnimNext 动画节点系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告的跨编译器兼容性 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串中 32/64 位说明符不匹配问题 |
| 2026-04-14 | `12eb7efc` | Fix FBindableXxx binding serialization issues when used with UAF traits | 修复 FBindable 类型在 UAF Trait 中的序列化问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 重命名 GetComponent 为 GetOrAddComponent 以匹配实际行为 |

### 维护评价

- **年龄**：约 3 个月，非常新的插件。
- **活跃度**：🟢 **活跃维护**。最近 1 个月内有多次功能性修复（FBindable 序列化修复、编译器兼容性修复），表明 UAF 框架仍处于积极开发阶段。
- **状态**：实验性插件（`IsExperimentalVersion=true`），随 UAF 框架同步演进。
- **推荐度**：仅限 UAF 框架开发者和贡献者使用。普通项目不应启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [UAFAnimNodeTestData 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites/Source/UAFAnimNodeTestData)