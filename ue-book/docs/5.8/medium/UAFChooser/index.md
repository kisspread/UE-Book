# UAF Chooser

> Chooser integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | 动画选择器集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFChooser` (Runtime), `UAFChooserEditor` (Runtime), `UAFChooserUncookedOnly` (Runtime), `UAFChooserTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser) | |

## 用途

本插件是 UE5 新一代动画框架 **Unreal Animation Framework (UAF)** 与 **Chooser 表**系统的集成。UAF 是 Epic 正在开发的实验性动画系统，旨在提供更灵活、数据驱动的动画逻辑。Chooser 表是一种强大的资产类型，用于基于输入条件从一系列选项中选择输出值（如动画片段、蒙太奇或数值）。

`UAFChooser` 插件的核心作用是**将 Chooser 表作为状态逻辑和决策的核心组件，深度集成到 UAF 的动画图（Anim Graph）和动画节点（Anim Node）系统中**。它解决了在 UAF 新范式下，如何高效、清晰地实现基于表格的复杂动画状态机和条件逻辑的问题，使动画师和程序员能够通过数据表格驱动动画状态转换和混合，而非传统的蓝图或 C++ 硬编码。

## 使用场景

- **开发复杂动画状态机**：当你需要为角色实现大量基于输入（如速度、状态、武器类型）的动画状态转换时，使用 Chooser 表来集中管理这些逻辑，比在动画蓝图中用大量节点连接更清晰、更易维护。
- **AI 或玩家状态管理**：利用 Chooser 表根据角色的高层状态（如“巡逻”、“战斗”、“受伤”）或输入动作，快速选择对应的动画集或动画蓝图。
- **数据驱动的动画**：需要频繁调整动画表现逻辑（如动作优先级、混合规则），希望这些调整能通过数据资产（Chooser 表）而非代码修改来实现。

## 蓝图用法

本插件主要提供动画图（AnimGraph）相关的节点和资产类型，蓝图可调用函数较少，核心功能通过动画蓝图编辑器实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AnimNode_ChooserTable` | UAF 动画图中的核心节点，用于在动画求值过程中根据输入条件查询 Chooser 表并输出结果（动画片段、状态等）。 | `FAnimNode_ChooserTable` |

### 使用示例（蓝图描述）

1.  **在 UAF 动画图中使用**：在 UAF 动画蓝图的图中，添加 `Chooser Table` 节点。将角色的运动状态、速度等参数连接到该节点的输入引脚。在节点的属性面板中，指定一个 `Chooser` 资产。节点将根据输入和 Chooser 表的定义，输出对应的动画片段或状态引用，供后续的混合或播放节点使用。
2.  **调试与可视化**：通过 `UAFChooserEditor` 模块提供的调试工具，可以在运行时实时查看 Chooser 表的求值路径和当前选择的结果，帮助定位动画逻辑问题。

## C++ 用法

以下示例基于插件的测试用例和核心类逻辑编写。

### 头文件引入

```cpp
#include "UAFChooser/AnimNode_ChooserTable.h"
#include "Chooser.h"
```

### 基本用法

在自定义的 UAF 动画节点或动画系统逻辑中，创建并求值一个 Chooser 表。
（来源：`Tests/UAFChooserTests` 模块中的测试用例逻辑）

```cpp
// 假设你有一个 FAnimNodeContext 或类似的上下文，以及一个 UChooser 资产指针
UChooser* MyChooserTable = /* ... */;

if (MyChooserTable)
{
    // 构建输入上下文
    FChooserEvaluationContext Context;
    // 添加条件参数，例如一个枚举值
    Context.AddInputParam(FGameplayTag::RequestGameplayTag("Data.Status"), static_cast<int32>(ECharacterStatus::Combat));
    Context.AddInputParam(FGameplayTag::RequestGameplayTag("Data.Speed"), 600.0f);

    // 求值 Chooser 表
    FChooserEvaluationResult Result;
    bool bSuccess = MyChooserTable->Evaluate(Context, Result);

    if (bSuccess)
    {
        // 从结果中获取输出，例如一个动画片段引用
        TSoftObjectPtr<UAnimationAsset> SelectedAnim = Result.GetValue<FAnimChooserSelectedAnimation>(FGameplayTag::RequestGameplayTag("Output.Animation"));
        // ... 使用选出的动画
    }
}
```

### 进阶用法

在自定义的 `UAnimNode_Base` 子类中集成 Chooser 表求值逻辑。
（来源：`UAFChooser` 模块中 `FAnimNode_ChooserTable` 的实现逻辑）

```cpp
// 在你的动画节点的 Evaluate_AnyThread 或类似函数中
void FMyAnimNode::Evaluate_AnyThread(FPoseContext& Output)
{
    // ... 获取角色数据，构建 Chooser 上下文
    FChooserEvaluationContext Context;
    // 从你的节点属性或当前动画实例获取输入数据并填充到 Context

    // 执行求值
    if (UChooser* Table = GetChooserTable())
    {
        FChooserEvaluationResult Result;
        if (Table->Evaluate(Context, Result))
        {
            // 处理结果，例如将选中的动画片段应用到 Output
            // 这可能涉及到连接到子动画图、设置混合权重等
            ApplyChooserResultToPose(Result, Output);
        }
    }
    // ... 后续处理
}
```

## Demo 示例

一个展示如何在 C++ 中定义并求值 Chooser 表的简单示例。

**头文件 (MyChooserDemo.h):**
```cpp
// MyChooserDemo.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "Chooser.h"

UCLASS()
class UMyChooserDemo : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Demo")
    UChooser* DemoChooserTable;

    /** 执行一次 Chooser 表求值并打印结果 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void RunDemo();
};
```

**源文件 (MyChooserDemo.cpp):**
```cpp
// MyChooserDemo.cpp
#include "MyChooserDemo.h"
#include "Chooser.h"

void UMyChooserDemo::RunDemo()
{
    if (!DemoChooserTable)
    {
        UE_LOG(LogTemp, Warning, TEXT("Demo Chooser Table is null."));
        return;
    }

    FChooserEvaluationContext Context;
    // 添加一个整型输入
    Context.AddInputParam(FGameplayTag::RequestGameplayTag("Demo.Input.IntValue"), 42);
    // 添加一个布尔输入
    Context.AddInputParam(FGameplayTag::RequestGameplayTag("Demo.Input.BoolValue"), true);

    FChooserEvaluationResult Result;
    if (DemoChooserTable->Evaluate(Context, Result))
    {
        // 尝试获取一个名为“Output.Text”的字符串输出
        FString ResultText = Result.GetValue<FString>(FGameplayTag::RequestGameplayTag("Output.Text"));
        UE_LOG(LogTemp, Log, TEXT("Chooser Evaluation Succeeded! Result Text: %s"), *ResultText);
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Chooser Evaluation had no matching row."));
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，使用者需要依赖以下 **独特** 模块：

| 模块 | 用途 |
|---|---|
| `Chooser` | Chooser 表系统的核心库，提供 `UChooser` 资产和求值逻辑。 |
| `UAF` | Unreal Animation Framework 核心库，提供新的动画节点基类、求值上下文和动画图系统。 |
| `GameplayTags` | 用于在 Chooser 表的输入/输出中标识数据字段。 |
| `AnimationCore` | 提供动画系统的基础类型和工具。 |
| `UAFChooser` | 本插件的核心运行时库。 |
| `UAFChooserEditor` | 本插件的编辑器扩展和调试工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 为只有一个子节点的动画节点添加了修改器动画节点基类 |
| 2026-03-19 | `910301d3` | UAF Anim Node rewind debugger track | 为 UAF 动画节点添加了回退调试器轨道 |
| 2026-03-11 | `bda4ef8e` | Add debug update counter to UAF anim node to enforce invariants | 为 UAF 动画节点添加调试更新计数器以确保不变量 |
| 2026-03-11 | `7da85466` | Implement AnimOp system for new UAF runtime | 为新的 UAF 运行时实现了动画操作（AnimOp）系统 |
| 2026-03-10 | `5a95823d` | AnimNodes Blend stack helper class to avoid too much code duplication (it can be used as either a b | 添加了动画节点混合栈辅助类以避免代码重复 |

### 维护评价

**活跃开发中，但为实验性功能。**

- **创建时间**：插件创建于 2025 年 06 月，非常年轻。
- **更新频率**：最近（2026年3-4月）有非常密集的功能性更新，专注于 UAF 动画节点、调试工具和核心运行时系统的构建。
- **状态**：处于**实验性**开发阶段（`IsExperimentalVersion: true`），功能尚未稳定，API 可能会发生重大变化。
- **结论**：这是一个 Epic 正在积极开发的新系统集成插件。目前**不建议在生产项目中使用**，但非常适合对 UE5 未来动画技术方向感兴趣的学习者和早期实验者。请密切关注其 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser/Tests)
- [父插件 UAF 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)
- [Chooser 表系统源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser)