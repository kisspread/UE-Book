# UAF Pose Search

> Pose Search integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF姿态搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFPoseSearch` (Runtime), `UAFPoseSearchUncookedOnly` (Runtime), `UAFPoseSearchTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch) | |

## 用途

UAFPoseSearch 插件是 Unreal Animation Framework (UAF) 框架中对 Epic 的 `PoseSearch` 模块的集成。它的核心作用是在 UAF 的**动画图**系统（AnimNext）中，提供**基于姿态搜索的运动匹配（Motion Matching）** 能力。

它解决的关键问题是：在 UAF 框架下，如何根据角色当前的运动轨迹（Trajectory）和历史姿态，从动画数据库中自动搜索并匹配出最合适的动画片段，并将其无缝地应用到角色上，从而实现高质量、响应迅速的角色动画。

该插件并非一个独立的功能模块，而是 UAF 生态的一部分，它将 `PoseSearch` 模块的强大搜索能力“桥接”到了 UAF 的**Trait（特性）系统**和**RigVM** 节点中，使得开发者可以在 UAF 的动画图中方便地使用运动匹配功能。

## 使用场景

- **角色运动动画**：你需要为一个第一人称射击游戏（FPS）或第三人称动作游戏创建流畅的移动、转向和停止动画。角色的移动速度、方向变化快速，传统的动画状态机难以维护，运动匹配可以从数据库中自动选取最佳动画片段。
- **动画混合与过渡**：角色需要在奔跑、跳跃、蹲伏、瞄准等多种状态间平滑切换，且切换的时机由复杂的玩家输入或游戏逻辑决定。
- **交互式动画**：角色需要与其他角色或物体进行精确的交互动画（如互动动作、战斗同步），需要根据双方的相对位置和运动状态在数据库中搜索匹配的动画对。
- **使用 UAF 框架的项目**：你的项目已经采用了 UAF 框架来构建动画系统，并希望在此框架内集成成熟的运动匹配解决方案。

## 蓝图用法

UAFPoseSearch 主要通过 UAF 的 **Trait（特性）节点**和 **RigVM 节点**暴露其功能。

### 核心 Trait 节点

这些是 UAF 动画图中的核心功能节点，通过 `FAnimNextTraitSharedData` 结构体暴露属性。

| 节点 | 说明 | 所在类/结构体 |
|---|---|---|
| Motion Matching | 运动匹配主 Trait。根据轨迹和配置，从 PoseSearch 数据库中搜索最佳动画。 | `FMotionMatchingTraitSharedData` |
| Pose History | 姿态历史收集器 Trait。持续收集角色指定骨骼和曲线的历史数据，并可生成轨迹，为运动匹配提供输入。 | `FAnimNextHistoryCollectorTraitSharedData` |
| Pose Search Result Emulator | 姿态搜索结果模拟器 Trait（实验性）。用于调试或模拟，直接输入一个姿态搜索结果来驱动动画播放。 | `FPoseSearchResultEmulatorTraitSharedData` |

### 核心 RigVM 节点

这些节点在 UAF 的 RigVM 动画图中使用，用于查询和操作姿态搜索数据。

| 节点 | 说明 | 所在结构体 |
|---|---|---|
| Get Selected Database | 从姿态搜索结果中获取被选中的数据库资产。 | `FRigUnit_PoseSearchResultGetSelectedDatabase` |
| Get Database Tags | 获取指定姿态搜索数据库的元数据标签。 | `FRigUnit_PoseSearchDatabaseGetTags` |
| Generate Trajectory from CMC | 从 `UCharacterMovementComponent` 生成用于运动匹配的轨迹数据。 | `FRigUnit_GenerateCharacterMovementComponentTrajectory` |
| Debug Draw Trajectory | 调试绘制轨迹，可在视口中可视化轨迹数据。 | `FRigUnit_DebugDrawTrajectory` |
| Multi Anim Get Animation Asset | 从 `UMultiAnimAsset` 中根据角色名（Role）获取对应的动画资产。 | `FRigUnit_MultiAnimGetAnimationAsset` |
| Get Motion Match Interaction Constraint | 获取运动匹配交互约束的属性（变换和距离）。 | `FRigUnit_GetMotionMatchInteractionConstraint` |

### 使用示例（蓝图描述）

1.  **配置运动匹配（Motion Matching）**：
    在 UAF 动画图中，添加一个 `Motion Matching` Trait 节点。在其属性面板中：
    *   `Databases`：拖入一个或多个 `UPoseSearchDatabase` 资产，这些资产包含了用于搜索的动画片段。
    *   `BlendArguments`：设置混合参数（如混合时间、混合曲线）。
    *   `SearchThrottleTime`：设置搜索频率，避免每帧都进行昂贵的搜索。
    *   `SyncMode`：设置同步模式，用于多角色动画同步。

2.  **提供姿态历史和轨迹输入**：
    `Motion Matching` 节点需要 `PoseHistory` 和 `Trajectory` 数据。通常连接一个 `Pose History` Trait 节点：
    *   将 `Motion Matching` 节点的 `PoseHistory` 输入引脚连接到 `Pose History` 节点的输出。
    *   在 `Pose History` 节点的属性中，配置 `CollectedBones`（需要记录历史的骨骼，如根骨、胯骨、脚骨）和 `CollectedCurves`。
    *   将 `Pose History` 节点的 `Trajectory` 输入引脚连接到 `Generate Trajectory from CMC` RigVM 节点的输出，或者一个直接输入的 `FTransformTrajectory` 资产。

3.  **调试**：
    使用 `Debug Draw Trajectory` 节点连接到轨迹数据，并启用其 `Enabled` 属性，即可在游戏视口中看到轨迹线，方便调试。

## C++ 用法

### 头文件引入

```cpp
// 引入核心 Trait 接口
#include "UAFPoseSearch/IPoseHistory.h"

// 引入特定的 Trait 或 RigVM 节点数据结构（根据需要）
#include "UAFPoseSearch/Internal/MotionMatchingTraitData.h"
#include "UAFPoseSearch/Internal/HistoryCollectorTraitData.h"
// ... 其他需要的头文件
```

### 基本用法

UAFPoseSearch 的核心是实现 `IPoseHistory` 接口，以便在 UAF 动画图的 Trait 系统中传递姿态历史信息。`FHistoryCollectorTrait` 是该接口的一个主要实现。

```cpp
// 示例：在自定义 Trait 中访问 Pose History
// 假设你的 Trait 需要使用姿态历史数据
struct FMyCustomTrait : FAdditiveTrait, IEvaluate
{
    // ... Trait 的其他定义 ...

    virtual void PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const override
    {
        // 通过 Trait 的 Scoped Interface 机制获取 IPoseHistory
        if (const IPoseHistory* PoseHistoryInterface = Context.GetScopedInterface<IPoseHistory>(Binding))
        {
            const UE::PoseSearch::IPoseHistory* PoseHistory = PoseHistoryInterface->GetPoseHistory(Context, Binding);
            if (PoseHistory)
            {
                // 使用 PoseHistory 数据，例如获取最新的历史姿态
                const FPoseHistory& History = PoseHistory->GetHistory();
                // ... 进行你的计算 ...
            }
        }

        // 继续执行默认的 PostEvaluate
        // ...
    }
};
```

### 进阶用法

直接在 C++ 中配置和驱动 `FAnimNextMotionMatchingTask`（底层执行任务）较为复杂，通常由 `FMotionMatchingTrait` Trait 内部管理。更常见的进阶用法是**创建自定义的 PoseSearch Feature Channel**，用于扩展运动匹配的搜索维度。

```cpp
// 示例：自定义一个基于 AnimNext 变量的距离特征通道
// 继承自 UPoseSearchFeatureChannel_Distance
UCLASS(Experimental, EditInlineNew, Blueprintable, meta = (DisplayName = "Distance from Custom Variable"))
class UMyPoseSearchFeatureChannel_DistanceFromCustomVar : public UPoseSearchFeatureChannel_Distance
{
    GENERATED_BODY()

    UPROPERTY(DisplayName = "Variable", EditAnywhere, Category="Variable")
    FAnimNextVariableReference CustomDistanceVariable;

    // 重写 BuildQuery 方法，将自定义变量的值注入到搜索查询中
    virtual void BuildQuery(UE::PoseSearch::FSearchContext& SearchContext) const override
    {
        // 从 SearchContext 的变量系统中获取自定义变量的值
        const float* CustomDistanceValue = SearchContext.GetVariable<float>(CustomDistanceVariable);
        if (CustomDistanceValue)
        {
            // 使用这个自定义距离值来影响搜索查询
            // 通常调用父类的方法并传递这个值
            FSearchContext::FChannelData ChannelData;
            ChannelData.Data.Add(*CustomDistanceValue);
            SearchContext.AddChannelData(this, ChannelData);
        }
        else
        {
            // 如果变量不存在，使用默认值或父类实现
            Super::BuildQuery(SearchContext);
        }
    }
};
```

## Demo 示例

由于 UAFPoseSearch 是一个集成插件，其“Demo”主要体现为在 UAF 动画图中配置 Trait 节点。以下是一个概念性的最小 C++ 结构，展示了如何定义一个使用 `IPoseHistory` 接口的简单 Trait。

**MyHistoryConsumerTrait.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNext/AnimNextTrait.h"
#include "UAFPoseSearch/IPoseHistory.h" // 关键：引入 IPoseHistory 接口
#include "MyHistoryConsumerTrait.generated.h"

USTRUCT(meta = (DisplayName = "My History Consumer"))
struct FMyHistoryConsumerTraitSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    // 可以添加一些配置属性
    UPROPERTY(EditAnywhere, Category = Settings)
    bool bDoSomethingWithHistory = true;

    // Latent pin 支持
    #define TRAIT_LATENT_PROPERTIES_ENUMERATOR(GeneratorMacro) \
        GeneratorMacro(bDoSomethingWithHistory) \
    
    GENERATE_TRAIT_LATENT_PROPERTIES(FMyHistoryConsumerTraitSharedData, TRAIT_LATENT_PROPERTIES_ENUMERATOR)
    #undef TRAIT_LATENT_PROPERTIES_ENUMERATOR
};

namespace UE::UAF
{
    struct FMyHistoryConsumerTrait : FAdditiveTrait, IEvaluate, IPoseHistory // 实现 IEvaluate 和 IPoseHistory
    {
        DECLARE_ANIM_TRAIT(FMyHistoryConsumerTrait, FAdditiveTrait)

        using FSharedData = FMyHistoryConsumerTraitSharedData;

        struct FInstanceData : FTrait::FInstanceData
        {
            // Trait 的实例数据
        };

        // IEvaluate 实现
        virtual void PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const override;

        // IPoseHistory 实现 - 将调用传递给子 Trait 或提供默认实现
        virtual const UE::PoseSearch::IPoseHistory* GetPoseHistory(FExecutionContext& Context, const TTraitBinding<IPoseHistory>& Binding) const override;
    };
}
```

**MyHistoryConsumerTrait.cpp**
```cpp
#include "MyHistoryConsumerTrait.h"

namespace UE::UAF
{
    void FMyHistoryConsumerTrait::PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const
    {
        // 通过 Binding 获取我们的共享数据
        const FMyHistoryConsumerTraitSharedData& SharedData = Binding.GetSharedData<FMyHistoryConsumerTraitSharedData>();

        if (SharedData.bDoSomethingWithHistory)
        {
            // 尝试从当前动画图上下文中获取 Pose History
            // 这依赖于 Trait 链中上游有某个 Trait（如 FHistoryCollectorTrait）提供了 IPoseHistory
            if (const IPoseHistory* PoseHistoryInterface = Context.GetScopedInterface<IPoseHistory>(Binding))
            {
                const UE::PoseSearch::IPoseHistory* PoseHistory = PoseHistoryInterface->GetPoseHistory(Context, Binding);
                if (PoseHistory)
                {
                    // 成功获取到姿态历史，可以进行你的逻辑
                    // 例如：分析历史轨迹、计算统计数据等
                }
            }
        }

        // 确保评估继续
        FAnimNextTraitFunctions::PostEvaluate(Context, Binding);
    }

    const UE::PoseSearch::IPoseHistory* FMyHistoryConsumerTrait::GetPoseHistory(FExecutionContext& Context, const TTraitBinding<IPoseHistory>& Binding) const
    {
        // 默认实现：尝试将调用传递给子 Trait（如果 Trait 链上有）
        // 或者，如果你的 Trait 本身不提供历史数据，返回 nullptr
        return FAnimNextTraitFunctions::Propagate<IPoseHistory>(Context, Binding);
    }
}
```

## 模块依赖

从源码分析，使用此插件（特别是 `UAFPoseSearch` 模块）主要依赖于动画和运动匹配相关的模块。

| 模块 | 用途 |
|---|---|
| `PoseSearch` | Epic 的核心姿态搜索和运动匹配功能模块。提供数据库资产、搜索算法、特征通道等基础功能。 |
| `AnimNext` | UAF 的核心动画系统，提供 Trait、RigVM 集成等基础架构。 |
| `AnimNextInterface` | AnimNext 的接口定义模块。 |
| `Chooser` | 选择器模块，可能用于 `FPoseHistoryAnimProperty` 等结构体与 Chooser 系统的集成。 |

**说明**：该插件还依赖了常见的动画、核心引擎模块（如 `CoreUObject`, `Engine`, `Core`, `SlateCore` 等），这些属于标准依赖，已按规范省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `7b3fe3c2` | Use FPoseValueBundle in AnimOp value bundle evaluator | 在 AnimOp 值评估器中使用 FPoseValueBundle |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 宏。 |
| 2026-04-01 | `e9bc431c` | PoseSearch - removing unnecessary MotionMatchingInteraction node | 移除了不必要的 MotionMatchingInteraction 节点。 |
| 2026-04-01 | `d6ad87e4` | UAFPoseSearch - consolidating FUAFDebuggerTrackCreator and FDebuggerTrackCreator | 合并了 FUAFDebuggerTrackCreator 和 FDebuggerTrackCreator 调试追踪器。 |
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 为单子节点的动画节点添加了修改器动画节点数据基类。 |

### 维护评价

- **创建时间**：插件于2025年6月创建，非常年轻（约1年）。
- **近期活跃度**：从 Git 历史看，**维护非常活跃**。最近的提交集中在2026年4月，进行了功能优化（如 PoseValueBundle）、代码清理（日志宏迁移）和架构调整（节点合并、基类添加）。这些提交表明插件正在积极开发和完善中。
- **当前状态**：插件在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着它目前是**实验性功能**，API 和功能可能随时发生变化，不建议直接用于生产环境。
- **已知限制**：
    - 作为实验性插件，其稳定性和最终 API 形式尚不确定。
    - 它是 UAF 框架的一部分，使用它需要先理解并采用 UAF（AnimNext）体系。
    - 从源码结构看，包含了一些内部（Internal/）和实验性（Experimental）标记的类，说明部分功能仍在摸索和验证阶段。
- **推荐使用**：
    - **推荐用于**：对 UAF 框架有深入了解，并且正在探索或评估在项目中集成运动匹配功能的团队。它是 UAF 生态中获取此功能的官方途径。
    - **不推荐用于**：直接用于已上线或需要高度稳定性的生产项目。请等待其从实验性毕业或评估 UAF 框架本身的成熟度。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
- [官方文档]( ) （无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch/Tests) （假设在 Tests 子目录下）