# Animation Curve Expressions

> Experimental Curve Remapper using Simple Math Expressions

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CurveExpression` (Runtime), `CurveExpressionEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-15 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/CurveExpression) | |

## 用途

CurveExpression 提供了一套**基于数学表达式的动画曲线重映射系统**。它允许你用简单的数学表达式（如 `Walk_Run * 0.5 + IdleWeight`）来定义一个动画曲线如何从其他曲线计算得出，而不是使用传统的蓝图节点逐个设置曲线值。

这个 plugin 解决的核心问题是：在动画混合过程中，经常需要根据一个或多个源曲线的值来计算目标曲线的值。传统方式需要大量的蓝图节点或 C++ 代码来做这些简单的数学运算。CurveExpression 用一个简洁的文本表达式语法替代了这些繁琐的工作。

plugin 包含三个主要组件：
1. **Expression Evaluator** — 一个独立的数学表达式解析和执行引擎（基于 Shunting Yard 算法）
2. **RemapCurves 动画节点** — 在动画蓝图中使用的 AnimNode，通过表达式重映射曲线
3. **CurveExpressionsDataAsset** — 可复用的表达式数据资产

## 使用场景

- 你在做角色动画混合，需要将 `Walk` 和 `Run` 曲线按权重混合为一个输出曲线 → 在 AnimGraph 中使用 RemapCurves 节点，表达式写 `Walk * BlendWeight + Run * (1 - BlendWeight)`
- 你需要从一个骨骼网格的动画曲线计算另一个骨骼网格的曲线 → 使用 RemapCurvesFromMesh 节点，表达式引用源网格的曲线名
- 你有一组常用的曲线映射逻辑需要在多个动画蓝图中复用 → 创建 CurveExpressionsDataAsset 资产，在多个节点中引用
- 你需要用 `clamp`、`sin`、`abs` 等数学函数来对曲线值进行变换 → 表达式支持内置函数，如 `clamp(SourceCurve, 0, 1)`
- 你想在运行时动态修改曲线映射逻辑 → 使用 ExpressionMap 模式，通过蓝图传入 `TMap<FName, FString>`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Expression Map` | 创建一个 `TMap<FName, FString>` 表达式映射，可在蓝图中传给 RemapCurves 节点 | `UK2Node_MakeCurveExpressionMap` |

### AnimGraph 节点

在动画蓝图的 AnimGraph 编辑器中，可添加以下节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Remap Curves` | 使用表达式重映射当前姿态的动画曲线 | `UAnimGraphNode_RemapCurves` |
| `Remap Curves From Mesh` | 使用表达式从另一个骨骼网格的曲线重映射 | `UAnimGraphNode_RemapCurvesFromMesh` |

这两个节点在 AnimGraph 中位于 **Animation > Curve Expression** 分类下。

### 表达式源（Expression Source）

RemapCurves 节点支持三种表达式源，通过 `ExpressionSource` 属性切换：

| 源 | 说明 |
|---|---|
| `ExpressionList` | 直接在节点属性中编写表达式文本（默认） |
| `DataAsset` | 引用一个 `UCurveExpressionsDataAsset` 资产 |
| `ExpressionMap` | 通过蓝图引脚传入 `TMap<FName, FString>`，支持运行时动态修改 |

### 使用示例（蓝图描述）

**基本曲线重映射：**

1. 在 AnimGraph 中添加一个 **Remap Curves** 节点
2. 将 Source Pose 连接到上游动画节点的输出
3. 在节点 Details 面板的 **Expressions > Expression List > Assignment Expressions** 文本框中输入表达式：
   ```
   OutputAlpha = InputA * 0.7 + InputB * 0.3
   ClampedValue = clamp(Weight, 0, 1)
   ```
4. 每行格式为 `目标曲线名 = 数学表达式`
5. 表达式中的变量名会被自动识别为源曲线名，运行时从当前动画姿态的曲线中读取值

**使用 Expression Map（蓝图运行时动态设置）：**

1. 在蓝图中使用 **Make Expression Map** 节点（在 Animation > Curve Expression 分类下）
2. 在节点属性中编辑表达式列表
3. 将输出的 Map 引脚连接到 Remap Curves 节点的 `CurveExpressions` 引脚
4. 在 Remap Curves 节点上将 Expression Source 设为 `ExpressionMap`

**移除曲线：**

使用 `-CurveName` 语法（行首减号）或 `TargetCurve = undef()` 来标记需要移除的曲线。

## 表达式语法

### 运算符

| 运算符 | 说明 | 示例 |
|---|---|---|
| `+` | 加法 | `a + b` |
| `-` | 减法 | `a - b` |
| `*` | 乘法 | `a * 2` |
| `/` | 除法（除零返回 0） | `a / b` |
| `%` | 取模（模零返回 0） | `a % 10` |
| `**` | 幂运算 | `a ** 2` |
| `//` | 整除（向下取整） | `a // 3` |
| `-`（一元） | 取负 | `-a` |
| `()` | 括号分组 | `(a + b) * c` |

### 内置函数

| 函数 | 参数数量 | 说明 |
|---|---|---|
| `clamp(value, min, max)` | 3 | 将值限制在 [min, max] 范围内 |
| `min(a, b)` | 2 | 取较小值 |
| `max(a, b)` | 2 | 取较大值 |
| `abs(value)` | 1 | 绝对值 |
| `round(value)` | 1 | 四舍五入 |
| `ceil(value)` | 1 | 向上取整 |
| `floor(value)` | 1 | 向下取整 |
| `sin(value)` | 1 | 正弦（弧度） |
| `cos(value)` | 1 | 余弦（弧度） |
| `tan(value)` | 1 | 正切（弧度） |
| `asin(value)` | 1 | 反正弦 |
| `acos(value)` | 1 | 反余弦 |
| `atan(value)` | 1 | 反正切 |
| `sqrt(value)` | 1 | 平方根 |
| `isqrt(value)` | 1 | 平方根的倒数 |
| `log(value)` | 1 | 自然对数 |
| `exp(value)` | 1 | e 的幂 |
| `pi()` | 0 | 圆周率 π |
| `e()` | 0 | 自然常数 e |
| `undef()` | 0 | 返回 NaN，用于标记曲线移除 |

### 特殊常量名规则

- 常量名以字母或下划线开头，后跟字母、数字或下划线
- 如果常量名以数字开头、包含空格或运算符字符，需要用**单引号**包裹：`'curve(1)' * 2.0`
- 常量名在运行时会被解析为动画曲线名，通过回调函数获取实际值

## C++ 用法

### 头文件引入

```cpp
#include "ExpressionEvaluator.h"
#include "CurveExpressionsDataAsset.h"
```

### 基本用法 — 表达式求值

表达式引擎 `CurveExpression::Evaluator::FEngine` 可独立使用，不依赖动画系统。

```cpp
using namespace CurveExpression::Evaluator;

// 创建表达式引擎实例
FEngine Engine;

// 方式一：一步完成解析 + 执行
TOptional<float> Result = Engine.Evaluate(
    TEXT("a + b * 2"),
    [](FName InName) -> TOptional<float>
    {
        if (InName == FName("a")) return 1.0f;
        if (InName == FName("b")) return 3.0f;
        return {};  // 未知常量返回空
    }
);
// Result = 7.0f
```

*来源：`Source/Runtime/Public/ExpressionEvaluator.h`*

### 进阶用法 — 解析后复用

解析阶段会将表达式编译为内部字节码（RPN 格式），适合多次执行时只解析一次：

```cpp
using namespace CurveExpression::Evaluator;

FEngine Engine;

// 解析表达式
TVariant<FExpressionObject, FParseError> ParseResult = Engine.Parse(TEXT("x * 2 + 1"));

if (FExpressionObject* Expression = ParseResult.TryGet<FExpressionObject>())
{
    // 多次执行同一表达式，只需解析一次
    auto ConstantEval = [](FName InName) -> TOptional<float>
    {
        if (InName == FName("x")) return 5.0f;
        return {};
    };
    
    float Value1 = Engine.Execute(*Expression, ConstantEval);  // 11.0f
    
    // 更换常量值重新执行
    auto ConstantEval2 = [](FName InName) -> TOptional<float>
    {
        if (InName == FName("x")) return 10.0f;
        return {};
    };
    
    float Value2 = Engine.Execute(*Expression, ConstantEval2); // 21.0f
}
else if (FParseError* Error = ParseResult.TryGet<FParseError>())
{
    UE_LOG(LogTemp, Error, TEXT("Parse error: %s"), *Error->Message);
}
```

*来源：`Source/Runtime/Public/ExpressionEvaluator.h`*

### 验证表达式

```cpp
// 验证表达式语法是否正确（不检查常量值）
TOptional<FParseError> Error = Engine.Verify(TEXT("a + b"));
if (Error.IsSet())
{
    UE_LOG(LogTemp, Error, TEXT("Error at column %d: %s"),
        Error->Location.Start, *Error->Message);
}
```

*来源：`Source/Runtime/Private/ExpressionEvaluator.cpp`*

### 使用 CurveExpressionsDataAsset

```cpp
// 获取编译后的表达式数据
TSharedPtr<const FExpressionData> Data = MyDataAsset->GetCompiledExpressionData();

if (Data.IsValid())
{
    // 遍历所有编译后的表达式
    for (const auto& Pair : Data->ExpressionMap)
    {
        FName TargetCurve = Pair.Key;
        const FExpressionObject& Expression = Pair.Value;
        // 使用 FEngine::Execute 执行...
    }
    
    // 获取所有使用的常量名（即源曲线名）
    for (const FName& ConstantName : Data->NamedConstants)
    {
        // 这些是表达式中引用的变量名
    }
}
```

*来源：`Source/Runtime/Public/CurveExpressionsDataAsset.h`*

## Demo 示例

以下是一个完整的最小示例，展示如何在 C++ 中使用表达式引擎进行动画曲线重映射。

### CurveRemapper.h

```cpp
#pragma once

#include "ExpressionEvaluator.h"

class FCurveRemapper
{
public:
    // 解析一个表达式映射表
    bool ParseExpressions(const TMap<FName, FString>& InExpressions);
    
    // 执行所有表达式，输入源曲线值，输出目标曲线值
    TMap<FName, float> Evaluate(const TMap<FName, float>& InSourceCurves) const;

private:
    CurveExpression::Evaluator::FEngine Engine;
    TMap<FName, CurveExpression::Evaluator::FExpressionObject> CompiledExpressions;
};
```

### CurveRemapper.cpp

```cpp
#include "CurveRemapper.h"

bool FCurveRemapper::ParseExpressions(const TMap<FName, FString>& InExpressions)
{
    using namespace CurveExpression::Evaluator;
    
    CompiledExpressions.Reset();
    
    for (const TPair<FName, FString>& Pair : InExpressions)
    {
        TVariant<FExpressionObject, FParseError> Result = Engine.Parse(Pair.Value);
        
        if (FExpressionObject* Expr = Result.TryGet<FExpressionObject>())
        {
            CompiledExpressions.Add(Pair.Key, MoveTemp(*Expr));
        }
        else
        {
            return false;  // 解析失败
        }
    }
    return true;
}

TMap<FName, float> FCurveRemapper::Evaluate(const TMap<FName, float>& InSourceCurves) const
{
    using namespace CurveExpression::Evaluator;
    
    TMap<FName, float> Results;
    
    for (const TTuple<FName, FExpressionObject>& Assignment : CompiledExpressions)
    {
        float Value = Engine.Execute(Assignment.Value,
            [&InSourceCurves](FName InName) -> TOptional<float>
            {
                if (const float* Found = InSourceCurves.Find(InName))
                {
                    return *Found;
                }
                return {};
            });
        
        Results.Add(Assignment.Key, Value);
    }
    
    return Results;
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "CurveExpression"   // 引用 CurveExpression Runtime 模块
});
```

## 模块依赖

### CurveExpression (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、日志 |
| `CoreUObject` | UObject 系统、序列化 |
| `Engine` | UDataAsset、动画系统基础类 |
| `AnimationCore` | 动画核心类型 |

### CurveExpressionEditor (UncookedOnly)

| 模块 | 用途 |
|---|---|
| `AnimGraph` | 动画图编辑器节点基础 |
| `AssetDefinition` | 资产定义系统 |
| `BlueprintGraph` | 蓝图图编辑器（K2Node 基础） |
| `CurveExpression` | 对 Runtime 模块的依赖 |
| `Kismet` | 蓝图编译系统 |
| `KismetCompiler` | 蓝图编译器 |
| `Slate` / `SlateCore` | UI 框架（表达式编辑器文本框） |
| `UnrealEd` | 编辑器基础 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-07-10 | `9803c443` | 为源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏（自动化代码修复） |
| 2025-06-26 | `ec900998` | 同上，另一批文件的内联生成宏添加 |
| 2025-05-30 | `52e3dac1` | 更新头文件的 DLL 导出宏，将 `dllexport` 从类型移到方法/静态变量上（Part 3） |

三次更新均为**自动化工具驱动的代码维护**（UnrealCodeFixup），没有功能性变更。这些是 Epic 的全局代码质量改进，不是专门针对 CurveExpression 的。

### 维护评价

- **创建时间**：2022 年 3 月，约 4 年历史
- **最近更新**：2025 年 7 月，但均为自动化工具维护，**最后一次实质性功能更新时间不明**
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **活跃度**：自创建以来一直处于实验状态，未被提升为正式功能
- **代码质量**：代码结构清晰，有完整的自定义序列化版本管理，表达式引擎实现规范（Shunting Yard 算法）
- **测试用例**：plugin 目录内无测试文件，也没有在 Engine/Tests 中发现相关测试
- **是否推荐使用**：⚠️ 谨慎使用。作为实验性功能，API 可能在未来版本中发生变化。适合用于原型开发和内部工具，不建议在生产环境中作为核心依赖。如果需要稳定的曲线重映射功能，考虑自行实现或等待该功能正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/CurveExpression)
- 官方文档：无（DocsURL 为空）
- 测试用例：无
