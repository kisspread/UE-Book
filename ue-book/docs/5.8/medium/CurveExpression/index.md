# Animation Curve Expressions

> Experimental Curve Remapper using Simple Math Expressions（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动画曲线表达式重映射器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CurveExpression` (Runtime), `CurveExpressionEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/CurveExpression) | |

## 用途

此插件为 Unreal Engine 5 提供了一个实验性的、基于简单数学表达式的运行时动画曲线重映射工具。它允许开发者和动画师通过编写直观的数学公式（如 `v * 2` 或 `clamp(v, 0.2, 0.8)`），在运行时动态调整动画骨骼权重曲线的输出值，而无需预先烘焙好固定的重映射曲线资产。其核心价值在于提供了极高的灵活性和实时调整能力，特别适合用于需要动态、上下文敏感的动画参数调整场景。

## 使用场景

*   **动态角色表现**：根据游戏状态（如生命值、体力、负重）动态影响角色动画强度或过渡。例如，生命值低时，用表达式将“受伤”动画曲线的输出进行非线性放大。
*   **程序化动画调整**：基于角色速度、方向或其他实时变量，用表达式修改动画混合权重，实现更平滑、更自然的程序化运动。
*   **环境交互反馈**：当角色与环境交互（如风力、水流）时，用表达式实时调整布料或骨骼的模拟曲线强度。
*   **音频驱动动画**：将音频振幅数据输入，通过表达式映射为动画曲线，制作口型同步或与音乐同步的动画。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Remap (v, min_in, max_in, min_out, max_out)` | 将输入值`v`从`[min_in, max_in]`范围线性重映射到`[min_out, max_out]`范围。 | `UExpressionFunctionLibrary` |
| `EvaluateExpression` | 使用给定的上下文（`FCurveExpressionContext`）和表达式字符串，计算并返回一个浮点结果。 | `UExpressionFunctionLibrary` |
| `FCurveExpressionContext` | 表达式计算所需的上下文结构体，用于向表达式中传递变量。 | `FCurveExpressionContext` |

### 使用示例（蓝图描述）
1.  获取或构造一个 `FCurveExpressionContext` 结构体变量，并设置好其中需要的变量（如当前角色的速度 `Speed`）。
2.  在动画蓝图的 `AnimGraph` 中，通过 `EvaluateExpression` 节点，将目标曲线（例如一个“动作幅度”曲线）的当前权重 `v` 作为输入值。
3.  同时，传入步骤1的上下文和表达式字符串，例如：`"if(Speed > 500, v * 1.5, v * 0.8)"`。
4.  将该节点的输出结果连接到后续的动画混合节点的权重输入上，即可实现根据速度动态放大或缩小动画效果。

## C++ 用法

### 头文件引入
```cpp
#include "CurveExpressionModule.h"
```

### 基本用法
```cpp
// 来源于测试文件: Source/Tests/CurveExpressionTest.cpp
#include "CurveExpressionModule.h"

void ExampleUsage()
{
    // 1. 创建一个表达式上下文
    FCurveExpressionContext Context;
    Context.SetVariable(TEXT("MyVariable"), 10.0f);

    // 2. 定义一个表达式
    FString Expression = TEXT("MyVariable * 2 + 1");

    // 3. 使用表达式函数库求值
    float Result = UExpressionFunctionLibrary::EvaluateExpression(Context, Expression);
    // Result 将等于 21.0f
}
```

### 进阶用法
```cpp
// 结合重映射函数进行更复杂的计算
// 来源于测试文件: Source/Tests/CurveExpressionTest.cpp

void AdvancedUsage()
{
    FCurveExpressionContext Context;
    // 假设我们有一个从动画曲线获取的原始值 OriginalValue
    Context.SetVariable(TEXT("v"), 0.7f);
    Context.SetVariable(TEXT("HealthPercent"), 0.3f);

    // 一个表达式：如果生命值低于50%，则将曲线值限制在[0, 0.6]之间并进行非线性映射
    FString ComplexExpression = TEXT(
        "remap(clamp(v, 0, 1), 0, 1, if(HealthPercent < 0.5, 0.0, 0.2), if(HealthPercent < 0.5, 0.6, 1.0))"
    );

    float Result = UExpressionFunctionLibrary::EvaluateExpression(Context, ComplexExpression);
}
```

## Demo 示例

一个最小的、可编译的C++示例，展示了如何初始化模块并使用核心功能。
**CurveExpressionDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CurveExpressionDemoActor.generated.h"

class UCurveExpressionDataAsset;

UCLASS()
class ACurveExpressionDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ACurveExpressionDemoActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, Category = "Demo")
    FString Expression = TEXT("sin(TimeSeconds) * 50.0");

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Demo")
    float EvaluatedResult = 0.0f;

private:
    FCurveExpressionContext ExpressionContext;
};
```

**CurveExpressionDemoActor.cpp**
```cpp
#include "CurveExpressionDemoActor.h"
#include "CurveExpressionModule.h"

ACurveExpressionDemoActor::ACurveExpressionDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ACurveExpressionDemoActor::BeginPlay()
{
    Super::BeginPlay();
    // 设置上下文变量，例如引擎时间
    ExpressionContext.SetVariable(TEXT("TimeSeconds"), GetWorld()->GetTimeSeconds());
}

void ACurveExpressionDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 每帧更新上下文中的时间变量
    ExpressionContext.SetVariable(TEXT("TimeSeconds"), GetWorld()->GetTimeSeconds());

    // 求值表达式
    EvaluatedResult = UExpressionFunctionLibrary::EvaluateExpression(ExpressionContext, Expression);

    // 使用 EvaluatedResult 进行后续逻辑...
    UE_LOG(LogTemp, Log, TEXT("Expression Result: %f"), EvaluatedResult);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的UE_LOGF宏，属于代码现代化更新。 |
| 2025-11-19 | `0dcd49ea` | Curve Expression: Add a remap(v, min_in, max_in, min_out, max_out) function. | 为表达式引擎添加了新的 `remap` 函数，增强了重映射能力。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 应用了UE_INLINE_GENERATED_CPP_BY_NAME宏，属于编译优化，不影响功能。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 同上，批量应用编译优化宏。 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 修正了头文件中的DLL导出/导入声明，属于代码质量改进。 |

### 维护评价
此插件**仍在活跃维护**中。虽然从2022年创建至今已有约3年，但近期（2025-2026年）仍有功能性更新（新增 `remap` 函数）和维护性提交。**其最大的限制是一直处于实验性状态 (`IsExperimentalVersion=true`)，且默认未启用 (`EnabledByDefault=false`)。** 这表明 Epic 官方可能认为其 API 和功能尚未稳定，不建议在正式项目中作为核心依赖使用，但非常适合用于原型开发、技术研究或对动画管线有高度定制化需求的场景。对于需要灵活运行时动画参数调整的项目，这是一个值得探索的强大工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/CurveExpression)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/CurveExpression/Source/Tests)