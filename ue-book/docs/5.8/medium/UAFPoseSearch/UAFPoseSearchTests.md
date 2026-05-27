# UAF Pose Search

> Pose Search integration for UAF.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | UAF姿势搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFPoseSearch` (Runtime), `UAFPoseSearchUncookedOnly` (Runtime), `UAFPoseSearchTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch) | |

## 用途
该插件旨在将 Unreal Animation Framework (UAF) 系统与 Pose Search 功能进行深度集成。其核心目的是扩展 UAF 的动画评估器（Evaluators），使其能够利用 Pose Search 的强大能力来检索和匹配动画姿势，从而为动画师和程序员提供更智能、数据驱动的动画过渡与混合方案。它解决了在 UAF 工作流中无缝引入高级姿势检索功能的问题。

## 使用场景
- **基于动作匹配的动画系统**：你需要一个角色能够根据上下文（如速度、方向）从一个庞大的动画数据库中，平滑、智能地切换到最合适的动画片段。
- **程序化动画生成**：你希望 UAF 能够根据角色的当前状态（例如骨骼位置）动态查找并混合最匹配的动画，以实现更自然的运动。
- **动画状态机优化**：在复杂的动画状态机中，减少对传统状态和过渡规则的依赖，转而使用基于内容检索的、更灵活的动画决策。

## 蓝图用法
该插件作为运行时集成，主要提供在动画蓝图或行为树中使用的姿势检索评估器节点。

### 核心节点
（基于源码分析，该插件的核心功能通常封装在评估器中，以节点形式暴露）
| 节点 | 说明 | 所在类 |
|---|---|---|
| `UAnimNode_UAFPoseSearch` | 一个动画图节点，用于在当前的 UAF 动画流程中执行姿势查询。 | `UAnimNode_UAFPoseSearch` |

### 使用示例（蓝图描述）
在动画蓝图的动画图（AnimGraph）中，你可以添加 `UAFPoseSearch` 节点。连接该节点的输入（例如来自“状态机”或“动画层”的输出），配置其内部的姿势搜索器（PoseSearcher）资产，即可根据输入的动画姿态或上下文，在指定的动画库中查找最佳匹配的动画片段并输出。

## C++ 用法
### 头文件引入
```cpp
#include "UAFPoseSearch/UAFPoseSearch.h"
```
### 基本用法
以下示例展示如何在代码中创建一个姿势搜索器并执行基础查询。
*(基于 `Tests/UAFPoseSearchTests` 目录中的测试用例逻辑推断)*
```cpp
// 假设已包含必要的头文件
#include "PoseSearch/PoseSearchContext.h"
#include "UAFPoseSearch/UAFPoseSearch.h"

// 创建一个上下文对象，用于执行搜索
FPoseSearchContext SearchContext;

// 设置搜索的动画数据库和查询参数
SearchContext.SetDatabase(MyAnimationDatabase);
// ... 其他配置，如查询骨骼、容差等

// 执行查询，获取结果
FPoseSearchResult SearchResult = SearchContext.Search(MyQueryPoseData);

if (SearchResult.IsValid())
{
    // 获取最佳匹配的动画序列及其采样位置
    UAnimSequence* MatchedAnim = SearchResult.GetAnimSequence();
    float SampleTime = SearchResult.GetSampleTime();
    // ... 进一步处理，例如播放该动画片段
}
```
### 进阶用法
结合 UAF 的求值器，可以在更复杂的动画逻辑中使用。
```cpp
// 在 UAF 的求值器链中集成姿势搜索
// 可能需要创建或配置一个类似 UUAFPoseSearchEvaluator 的对象
UUAFPoseSearchEvaluator* PoseSearchEvaluator = NewObject<UUAFPoseSearchEvaluator>();
PoseSearchEvaluator->Initialize(MyPoseSearcherSettings); // 配置搜索设置

// 在动画评估过程中调用
FAnimationEvaluationContext EvalContext;
// ... 填充上下文信息
PoseSearchEvaluator->Evaluate(EvalContext);

// 获取评估结果，这可能包含混合权重或目标动画信息
FPoseSearchEvaluatorOutput Output = PoseSearchEvaluator->GetOutput();
// ... 将结果用于动画混合
```

## Demo 示例
一个最小化的演示，展示如何初始化姿势搜索并处理一个简单的查询。
```cpp
// UAFPoseSearchDemo.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "PoseSearch/PoseSearchDatabase.h"
#include "UAFPoseSearchDemo.generated.h"

UCLASS(BlueprintType)
class UUAFPoseSearchDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 运行一个简单的姿势搜索演示 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void RunSimpleSearch();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    UPoseSearchDatabase* AnimationDatabase;

    UPROPERTY(BlueprintReadOnly, Category = "Demo")
    UAnimSequence* FoundAnimation;

    UPROPERTY(BlueprintReadOnly, Category = "Demo")
    float FoundTime;
};
```
```cpp
// UAFPoseSearchDemo.cpp
#include "UAFPoseSearchDemo.h"
#include "PoseSearch/PoseSearchContext.h"

void UUAFPoseSearchDemo::RunSimpleSearch()
{
    if (!AnimationDatabase)
    {
        UE_LOG(LogTemp, Warning, TEXT("Demo: AnimationDatabase is not set!"));
        return;
    }

    // 1. 创建搜索上下文
    FPoseSearchContext Context;

    // 2. 设置上下文（这里使用数据库，实际查询需要pose数据）
    Context.SetDatabase(AnimationDatabase);
    // 注意：在实际应用中，你需要提供一个查询用的骨架姿态（FPoseSearchQueryPoseData）。
    // 例如：Context.QueryPoseData = CreateQueryPoseFromCurrentState();

    // 3. 执行搜索
    // 由于缺少实际的查询姿态，此示例逻辑上会失败，但展示了API调用流程。
    // FPoseSearchResult Result = Context.Search(/* QueryPoseData */);

    // 4. 处理结果
    /*
    if (Result.IsValid())
    {
        FoundAnimation = Result.GetAnimSequence();
        FoundTime = Result.GetSampleTime();
        UE_LOG(LogTemp, Log, TEXT("Demo: Found animation '%s' at time %.2f"),
            *FoundAnimation->GetName(), FoundTime);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Demo: Search found no matching pose."));
    }
    */

    UE_LOG(LogTemp, Log, TEXT("UAF Pose Search Demo executed. (Actual search requires valid query pose data)"));
}
```

## 模块依赖
| 模块 | 用途 |
|---|---|
| `PoseSearch` | 提供核心的姿势检索引擎和数据库功能 |
| `UAFAnimation` | UAF (Unreal Animation Framework) 的核心模块，用于集成其评估器系统 |
| `AnimationCore` | 提供动画系统的基础核心类型 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `7b3fe3c2` | Use FPoseValueBundle in AnimOp value bundle evaluator | 评估器改用 FPoseValueBundle，优化数据传递 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF |
| 2026-04-01 | `e9bc431c` | PoseSearch - removing unnecessary MotionMatchingInteraction node | 移除 PoseSearch 中不必要的 MotionMatchingInteraction 节点 |
| 2026-04-01 | `d6ad87e4` | UAFPoseSearch - consolidating FUAFDebuggerTrackCreator and FDebuggerTrackCreator, since GetTargetTyp | 合并调试器轨道创建器，简化代码结构 |
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 为单子节点的动画节点添加修饰符数据基类 |

### 维护评价
该插件是一个**实验性**（`IsExperimentalVersion: true`）且**默认未启用**的组件。从创建时间（2025年6月）来看，它非常新。最近的提交记录显示，在2026年4月仍有积极的开发活动，包括功能优化、代码清理和重构（如合并调试器代码、迁移日志宏）。这些更新表明插件处于**活跃开发阶段**，API 和内部结构可能尚未稳定。

**建议**：
-   **谨慎使用**：鉴于其“实验性”状态，不应在生产项目中作为核心依赖，而应作为技术预览或内部工具链的一部分进行评估。
-   **持续关注**：其紧密集成的 `PoseSearch` 和 `UAFAnimation` 模块也是相对较新的系统，使用时需关注整个技术栈的协同更新。
-   **存在限制**：作为实验性功能，可能存在未记录的行为、性能问题或不完整的文档。建议结合 Epic 的官方技术演示和源码中的测试用例 (`UAFPoseSearchTests`) 来理解其设计意图和最佳实践。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
- [官方文档]：目前没有提供。