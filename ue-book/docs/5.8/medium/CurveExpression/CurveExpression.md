# Animation Curve Expressions

> Experimental Curve Remapper using Simple Math Expressions

| 属性 | 值 |
|---|---|
| 中文名 | 动画曲线表达式 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CurveExpression` (Runtime), `CurveExpressionEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/CurveExpression) | |

## 用途

这是一个用于动画曲线的表达式引擎插件，允许使用类似Python语法的简单数学表达式，在运行时对动画权重曲线进行动态重映射和计算。

**核心问题**：在复杂的动画系统中，经常需要对多个动画曲线进行数学运算来生成新的权重或值。传统方式需要手动编写蓝图或C++代码，而这个插件提供了一种声明式的、表达式驱动的方式，可以在编辑器中配置，在运行时高效计算。

**主要优势**：
- 声明式配置：在数据资产或蓝图中配置表达式，无需编写代码
- 运行时高效：表达式编译为优化后的字节码，执行速度快
- 支持动态常量：可以在运行时提供变量值给表达式使用
- 实时验证：在编辑器中验证表达式语法和依赖关系

## 使用场景

- 你需要在动画蓝图中基于多个动画曲线的值计算出一个新的混合权重，例如 `curve1 * 0.5 + curve2 * 0.3`
- 你想为不同的动画状态创建复杂的数学关系，而无需每次都创建新的动画蓝图节点
- 你需要将源角色的动画曲线重映射到目标角色上，但两个角色的动画曲线名称或范围不同
- 你想创建可重用的动画曲线变换逻辑，可以存储在数据资产中供多个角色使用
- 你需要在运行时基于游戏状态动态调整动画曲线的计算方式（通过动态常量）

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FAnimNode_RemapCurves` | 基于表达式列表重映射动画曲线 | `FAnimNode_RemapCurves` |
| `FAnimNode_RemapCurvesFromMesh` | 从源网格体获取曲线并进行表达式重映射 | `FAnimNode_RemapCurvesFromMesh` |
| `FAnimNode_RemapCurvesBase::ParseAndCacheExpressions` | 解析并缓存表达式 | `FAnimNode_RemapCurvesBase` |
| `FCurveExpressionsDataAsset::GetCompiledExpressionData` | 获取编译后的表达式数据 | `UCurveExpressionsDataAsset` |

### 使用示例（蓝图描述）

在动画蓝图中，你可以：

1. **添加CurveExpression节点**：在动画图中右键搜索"Remap Curves"或"Remap Curves From Mesh"节点
2. **配置表达式源**：在节点详情面板中，选择表达式来源：
   - **ExpressionList**：直接在节点中输入表达式（如 `head_scale * 0.8 + body_scale * 0.2`）
   - **DataAsset**：选择一个 `CurveExpressionsDataAsset` 数据资产
   - **ExpressionMap**：使用TMap<FName, FString>映射
3. **连接输入**：将源姿态连接到"Source Pose"引脚
4. **传递常量**（可选）：如果表达式使用变量（如 `head_scale`），可以通过"Expression Map"引脚传递运行时值
5. **获取结果**：经过表达式计算后的动画曲线会应用到输出姿态中

**表达式语法示例**：
```
// 简单运算
curve1 + curve2
curve1 * 0.5

// 带括号的复杂表达式
(curve1 + curve2) * 0.3

// 使用常量
weight * speed_multiplier

// 调用内置函数
remap(curve1, 0.0, 1.0, 0.5, 2.0)  // 重映射范围
```

## C++ 用法

### 头文件引入

```cpp
#include "AnimNode_RemapCurvesBase.h"
#include "ExpressionEvaluator.h"
#include "CurveExpressionsDataAsset.h"
```

### 基本用法

**1. 解析和执行单个表达式**（来自 ExpressionEvaluator.h）

```cpp
// 创建表达式引擎
CurveExpression::Evaluator::FEngine ExpressionEngine;

// 解析表达式
FStringView Expression(TEXT("curve1 * 0.5 + curve2"));
auto ParseResult = ExpressionEngine.Parse(Expression);

if (ParseResult.IsType<CurveExpression::Evaluator::FExpressionObject>())
{
    // 表达式解析成功
    const auto& ExpressionObject = ParseResult.Get<CurveExpression::Evaluator::FExpressionObject>();
    
    // 执行表达式，提供常量值
    auto Result = ExpressionEngine.Execute(ExpressionObject, 
        [](FName ConstantName) -> TOptional<float>
        {
            // 根据常量名返回值
            if (ConstantName == "curve1") return 1.0f;
            if (ConstantName == "curve2") return 0.5f;
            return TOptional<float>(); // 返回空表示常量未定义
        });
    
    // 使用结果
    UE_LOG(LogTemp, Log, TEXT("Expression result: %f"), Result);
}
else
{
    // 解析错误
    const auto& Error = ParseResult.Get<CurveExpression::Evaluator::FParseError>();
    UE_LOG(LogTemp, Error, TEXT("Expression error: %s at position %d-%d"), 
        *Error.Message, Error.Location.Start, Error.Location.End);
}
```

**2. 验证表达式语法**

```cpp
CurveExpression::Evaluator::FEngine ExpressionEngine;
FStringView Expression(TEXT("curve1 * 0.5 + "));

auto Error = ExpressionEngine.Verify(Expression);
if (Error.IsSet())
{
    UE_LOG(LogTemp, Warning, TEXT("Invalid expression: %s"), *Error.GetValue().Message);
}
```

### 进阶用法

**1. 在自定义动画节点中使用表达式系统**

```cpp
// 在你的动画节点中继承并扩展FAnimNode_RemapCurvesBase
USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyCustomRemapper : public FAnimNode_RemapCurvesBase
{
    GENERATED_BODY()
    
    virtual void Evaluate_AnyThread(FPoseContext& Output) override
    {
        // 获取编译后的表达式
        const auto& CompiledAssignments = GetCompiledAssignments();
        
        // 执行所有表达式
        for (const auto& Pair : CompiledAssignments)
        {
            const FName& TargetCurve = Pair.Key;
            const auto& Expression = Pair.Value;
            
            // 执行表达式，提供当前的曲线值作为常量
            float Result = ExpressionEngine.Execute(Expression, 
                [this](FName ConstantName) -> TOptional<float>
                {
                    // 从源姿态获取曲线值
                    if (SourceCurveValues.Contains(ConstantName))
                    {
                        return SourceCurveValues[ConstantName];
                    }
                    return TOptional<float>();
                });
            
            // 将结果应用到输出曲线
            Output.Curve.Set(TargetCurve, Result);
        }
    }
    
private:
    CurveExpression::Evaluator::FEngine ExpressionEngine;
    TMap<FName, float> SourceCurveValues;
};
```

**2. 使用数据资产存储复杂表达式**

```cpp
// 创建或加载数据资产
UCurveExpressionsDataAsset* DataAsset = LoadObject<UCurveExpressionsDataAsset>(
    nullptr, TEXT("/Game/Animations/CurveExpressions.Default"));

if (DataAsset)
{
    // 获取编译后的表达式数据
    TSharedPtr<const FExpressionData> CompiledData = DataAsset->GetCompiledExpressionData();
    
    if (CompiledData.IsValid())
    {
        // 使用编译后的表达式
        const auto& ExpressionMap = CompiledData->ExpressionMap;
        const auto& NamedConstants = CompiledData->NamedConstants;
        
        UE_LOG(LogTemp, Log, TEXT("Loaded %d expressions with %d constants"), 
            ExpressionMap.Num(), NamedConstants.Num());
    }
}
```

## Demo 示例

### MyRemapAnimInstance.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "AnimNode_RemapCurvesBase.h"
#include "MyRemapAnimInstance.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_RemapCurvesWithDebug : public FAnimNode_RemapCurvesBase
{
    GENERATED_BODY()
    
    // 添加调试输出属性
    UPROPERTY(BlueprintReadOnly, Category=Debug)
    float LastExpressionResult = 0.0f;
    
    virtual void Evaluate_AnyThread(FPoseContext& Output) override
    {
        // 调用基类的评估逻辑
        FAnimNode_RemapCurvesBase::Evaluate_AnyThread(Output);
        
        // 调试：获取第一个表达式的结果
        const auto& CompiledAssignments = GetCompiledAssignments();
        if (CompiledAssignments.Num() > 0)
        {
            const auto& FirstPair = *CompiledAssignments.begin();
            const auto& Expression = FirstPair.Value;
            
            CurveExpression::Evaluator::FEngine Engine;
            LastExpressionResult = Engine.Execute(Expression, 
                [&Output](FName ConstantName) -> TOptional<float>
                {
                    // 从输出姿态获取曲线值作为调试常量
                    if (Output.Curve.HasCurve(ConstantName))
                    {
                        return Output.Curve.Get(ConstantName);
                    }
                    return TOptional<float>();
                });
        }
    }
};

UCLASS()
class UMyRemapAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
    
public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category=Expressions)
    FString MyExpression = TEXT("curve1 * 0.8 + curve2 * 0.2");
    
    UPROPERTY(BlueprintReadOnly, Category=Debug)
    float ExpressionResult = 0.0f;
    
protected:
    virtual void NativeUpdateAnimation(float DeltaSeconds) override
    {
        Super::NativeUpdateAnimation(DeltaSeconds);
        
        // 解析表达式
        CurveExpression::Evaluator::FEngine Engine;
        auto ParseResult = Engine.Parse(MyExpression);
        
        if (ParseResult.IsType<CurveExpression::Evaluator::FExpressionObject>())
        {
            const auto& Expression = ParseResult.Get<CurveExpression::Evaluator::FExpressionObject>();
            
            // 模拟执行
            ExpressionResult = Engine.Execute(Expression, 
                [this](FName ConstantName) -> TOptional<float>
                {
                    // 这里可以从游戏状态获取常量值
                    if (ConstantName == "curve1") return 1.0f;
                    if (ConstantName == "curve2") return 0.5f;
                    return TOptional<float>();
                });
        }
    }
};
```

### MyRemapAnimInstance.cpp

```cpp
#include "MyRemapAnimInstance.h"

// 注册自定义动画节点
FAnimNode_RemapCurvesWithDebug::FAnimNode_RemapCurvesWithDebug()
{
    // 设置默认表达式
    ExpressionSource = ERemapCurvesExpressionSource::ExpressionMap;
    CurveExpressions.Add(FName("ResultCurve"), TEXT("source * 0.5"));
    bExpressionsImmutable = true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimGraphRuntime` | 动画图运行时支持 |
| `AnimationCore` | 动画核心功能 |
| `AnimationBlueprintLibrary` | 动画蓝图相关工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至UE_LOGF |
| 2025-11-19 | `0dcd49ea` | Curve Expression: Add a remap(v, min_in, max_in, min_out, max_out) function. | 添加remap重映射函数 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 添加内联生成的CPP文件宏 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 为源文件添加内联生成宏 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup... | 更新头文件的DLL导出宏 |

### 维护评价

**状态**：实验性但活跃维护中

**分析**：
1. **创建时间**：约3年，相对较新的插件
2. **维护频率**：最近一年有多次功能性更新（添加新函数）和维护性更新（代码规范、宏迁移）
3. **活跃度**：仍在积极开发中，最近的更新表明持续改进
4. **实验性**：标记为实验性，说明API可能变化，但由Epic Games维护
5. **推荐使用**：适合在实验性项目中使用，生产环境需谨慎评估

**建议**：可以放心在开发中试用此插件，但注意其实验性状态。建议关注其API变化，特别是在版本升级时。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/CurveExpression)
- [官方文档]() （无，实验性插件通常文档较少）
- [测试用例]() （无专门测试用例，但在AnimGraphRuntime模块中可能有相关测试）