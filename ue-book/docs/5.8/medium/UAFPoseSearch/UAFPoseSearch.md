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

本插件的核心功能是将 Unreal Engine 的 **Pose Search（姿态搜索）** 系统集成到新一代动画框架 **UAF（Unreal Animation Framework）** 中。它解决的核心问题是：**在 UAF 动画系统中，如何高效地根据角色当前状态（如轨迹、历史姿态）和运动目标，从预定义的动画数据库中搜索并播放最匹配的动画片段**。

具体来说，它实现了以下能力：
1.  **Motion Matching（动作匹配）**：通过 `FMotionMatchingTrait` 实现核心的动作匹配逻辑，能够实时搜索动画数据库并平滑过渡到匹配的动画。
2.  **姿态历史收集**：通过 `FAnimNextHistoryCollectorTrait` 收集角色骨骼和曲线的历史信息，为 Pose Search 查询提供必要的上下文数据。
3.  **轨迹生成与利用**：提供了从角色移动组件生成轨迹的工具节点（`FRigUnit_GenerateCharacterMovementComponentTrajectory`），并将轨迹数据用于 Pose Search 查询。
4.  **与 UAF 系统深度集成**：以 UAF 的 Trait（特性）和 RigUnit（控制单元）形式暴露功能，使开发者能在 UAF 动画蓝图中以模块化的方式组合这些功能。
5.  **交互支持**：支持基于角色间交互的动画搜索和对齐（Warping）。

简而言之，该插件使得基于 UAF 构建的角色动画系统能够利用 Pose Search 技术，实现更动态、更高质量的动画混合与过渡。

## 使用场景

*   **你在为开放世界或复杂动作游戏开发角色运动系统** → 使用 `Motion Matching Trait` 配合 `Pose History Trait` 和轨迹生成节点，实现根据玩家输入和环境实时选择最合适的跑步、行走、转身动画。
*   **你需要实现角色间的复杂交互动画**（如双人舞、格斗）→ 利用 `Motion Matching Trait` 的交互相关属性（如 `Availabilities`、`bValidateResultAgainstAvailabilities`），并可能结合 `Interaction Alignment` 等 Notify。
*   **你在 UAF 动画蓝图中需要调试动画搜索逻辑** → 使用 `Debug Draw Trajectory` 和 `Get Selected Database` 等调试节点来可视化轨迹和搜索结果。
*   **你想为特定游戏逻辑（如跳跃、特技）配置不同搜索频率** → 调整 `Motion Matching Trait` 的 `SearchThrottleTime` 和 `bShouldSearch` 参数。

## 蓝图用法

本插件主要以 UAF 的 Trait 和 RigUnit 节点形式提供蓝图功能，可在 UAF 动画蓝图中使用。

### 核心节点（RigUnit）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Selected Database` | 从 Pose Search 结果中获取被选中的动画数据库 | `FRigUnit_PoseSearchResultGetSelectedDatabase` |
| `Get Database Tags` | 获取指定 Pose Search 数据库的元数据标签 | `FRigUnit_PoseSearchDatabaseGetTags` |
| `Multi Anim Get Animation Asset` | 从 `UMultiAnimAsset` 中按角色（Role）获取对应的动画资产 | `FRigUnit_MultiAnimGetAnimationAsset` |
| `Generate Trajectory from Character Movement Component` | 根据角色移动组件生成用于姿态搜索的轨迹 | `FRigUnit_GenerateCharacterMovementComponentTrajectory` |
| `Debug Draw Trajectory` | 调试绘制变换轨迹 | `FRigUnit_DebugDrawTrajectory` |
| `Get Motion Match Interaction Constraint` | 获取与动画交互约束相关的属性（如目标变换） | `FRigUnit_GetMotionMatchInteractionConstraint` |

### 核心 Trait（特性）

| Trait 名称 | 显示名称 | 说明 |
|---|---|---|
| `FMotionMatchingTraitSharedData` | Motion Matching | 核心动作匹配特性，包含搜索数据库、混合参数、播放率等所有配置 |
| `FAnimNextHistoryCollectorTraitSharedData` | Pose History | 姿态历史收集特性，用于记录骨骼和曲线历史以供搜索使用 |
| `FPoseSearchResultEmulatorTraitSharedData` | Pose Search Result Emulator | 用于模拟 Pose Search 结果的特性，主要用于测试 |

### 使用示例（蓝图描述）

在 UAF 动画蓝图中：
1.  添加一个 `Pose History` Trait，配置要收集的骨骼（`CollectedBones`）和采样间隔（`SamplingInterval`）。
2.  如果需要轨迹生成，添加 `Generate Trajectory from Character Movement Component` 节点，连接 `CharacterMovementComponent` 和 `TrajectoryData`。
3.  将生成的轨迹输入到 `Pose History` Trait 的 `Trajectory` 引脚（如果 `bGenerateTrajectory` 为 false）。
4.  添加 `Motion Matching` Trait，将其 `Databases` 属性设置为你的 `UPoseSearchDatabase` 资产。
5.  （可选）连接 `Pose History` Trait 输出的 `PoseHistoryReferenceVariable` 到 `Motion Matching` Trait 的输入，或通过变量系统共享。
6.  调整 `Motion Matching` Trait 的 `SearchThrottleTime`、`BlendArguments` 等参数以控制搜索行为和混合效果。

## C++ 用法

### 头文件引入

```cpp
// 引入主模块头文件
#include "UAFPoseSearch.h"

// 如果需要使用具体的 Trait 或 RigUnit
#include "Internal/MotionMatchingTraitData.h"
#include "Internal/HistoryCollectorTraitData.h"
#include "Private/RigUnit_GenerateCharacterMovementComponentTrajectory.h"
```

### 基本用法

```cpp
// 示例：在 C++ 中创建并配置一个 Motion Matching Trait 的共享数据（通常用于工具或高级运行时配置）
#include "Internal/MotionMatchingTraitData.h"

void SetupMotionMatchingTrait()
{
    FMotionMatchingTraitSharedData MatchingData;
    
    // 设置搜索的数据库（需要先有一个 UPoseSearchDatabase* 指针）
    MatchingData.Databases.Add(MyPoseSearchDatabase);
    
    // 配置混合参数
    MatchingData.BlendArguments.BlendTime = 0.2f;
    MatchingData.BlendArguments.BlendOption = EAlphaBlendOption::Linear;
    
    // 设置搜索节流时间，例如每0.1秒搜索一次
    MatchingData.SearchThrottleTime = 0.1f;
    
    // 通过 FAnimNextTraitSharedData 接口传递给 UAF 系统
    // ... 具体使用方式取决于你如何构建 UAF 图
}
```

### 进阶用法

结合多个组件构建搜索系统：

```cpp
// 示例：概念性地展示如何组合 Pose History 和 Motion Matching 的逻辑（UAF 系统内部会处理 Trait 的组合）
void ConceptualPoseSearchSystem()
{
    // 1. 创建历史收集器数据
    FAnimNextHistoryCollectorTraitSharedData HistoryData;
    HistoryData.PoseCount = 20; // 收集过去20帧的姿势
    HistoryData.CollectedBones.Add(FBoneReference(TEXT("pelvis")));
    HistoryData.CollectedBones.Add(FBoneReference(TEXT("spine_01")));
    HistoryData.bGenerateTrajectory = false; // 使用外部提供的轨迹
    
    // 2. 准备轨迹数据（例如，从 Gameplay 逻辑计算得出）
    FTransformTrajectory Trajectory;
    // ... 填充轨迹样本 ...
    
    // 3. 配置动作匹配数据
    FMotionMatchingTraitSharedData MatchingData;
    MatchingData.Databases.Add(SomeDatabase);
    MatchingData.SearchThrottleTime = 0.05f; // 高频搜索
    MatchingData.PlayRate = FFloatInterval(0.8f, 1.2f); // 允许一定的播放速率调整
    
    // 4. 在 UAF 图的构建过程中，将这些数据应用到对应的 Trait 节点上
    // 具体实现依赖于你扩展或使用 UAF 图编辑器的方式。
}
```

## Demo 示例

以下是一个最小的 C++ 示例，展示了如何定义一个使用 `Motion Matching Trait` 的简单 UAF Trait（假设你已经熟悉 UAF Trait 的创建流程）。

```cpp
// MySimpleMMTrait.h
#pragma once

#include "CoreMinimal.h"
#include "TraitCore/Trait.h"
#include "TraitInterfaces/IUpdate.h"
#include "TraitInterfaces/IEvaluate.h"
#include "Internal/MotionMatchingTraitData.h"

class UMyAnimInstance; // 假设的动画实例

namespace UE::UAF
{
    struct FMySimpleMMTrait : FAdditiveTrait, IUpdate, IEvaluate
    {
        DECLARE_ANIM_TRAIT(FMySimpleMMTrait, FAdditiveTrait)
        
        // 使用标准的 Motion Matching 共享数据
        using FSharedData = FMotionMatchingTraitSharedData;
        
        struct FInstanceData : FTrait::FInstanceData
        {
            // 可以在此添加实例特定的数据
            TWeakObjectPtr<UMyAnimInstance> AnimInstance;
        };
        
        // IUpdate 接口
        virtual void PreUpdate(FUpdateTraversalContext& Context, const TTraitBinding<IUpdate>& Binding, const FTraitUpdateState& TraitState) const override;
        
        // IEvaluate 接口
        virtual void PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const override;
    };
}
```

```cpp
// MySimpleMMTrait.cpp
#include "MySimpleMMTrait.h"
#include "TraitCore/TraitSharedData.h" // 需要包含 Trait 共享数据头文件

namespace UE::UAF
{
    void FMySimpleMMTrait::PreUpdate(FUpdateTraversalContext& Context, const TTraitBinding<IUpdate>& Binding, const FTraitUpdateState& TraitState) const
    {
        FSharedData* SharedData = Binding.GetSharedData<FSharedData>();
        FInstanceData* InstanceData = Binding.GetInstanceData<FInstanceData>();
        
        if (InstanceData && InstanceData->AnimInstance.IsValid())
        {
            // 在此可以获取或设置动画实例的状态，以影响搜索
            // 例如，根据游戏输入更新搜索参数（虽然更推荐通过 Trait 的 latent pins）。
        }
    }
    
    void FMySimpleMMTrait::PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const
    {
        // 动作匹配的核心逻辑由内置的 FAnimNextMotionMatchingTask 处理。
        // 在此 Trait 中，你可以在评估后执行额外逻辑，例如基于搜索结果更新其他游戏状态。
        // 但通常情况下，不需要在此实现，内置的 MotionMatchingTrait 已经完整封装。
    }
}
```

## 模块依赖

从插件的模块构成和代码引用来看，主要依赖如下（已省略常见的 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `PoseSearch` | **核心依赖**。提供 PoseSearch 数据库、搜索算法、历史记录等基础功能。 |
| `AnimNext` | **核心依赖**。UAF/AnimNext 框架核心，提供 Trait、RigUnit、动画图评估等基础架构。 |
| `ControlRig` | 提供 RigUnit 的执行框架（`FRigUnit_AnimNextBase` 等基础类）。 |
| `AnimationCore` | 提供骨骼引用（`FBoneReference`）、曲线名称等动画基础类型。 |
| `GameplayAbilities` | 可能用于处理更复杂的交互或游戏能力相关的动画需求（从部分交互节点推断）。 |

**说明**：实际使用时，你的 Build.cs 文件需要确保对 `PoseSearch` 和 `AnimNext` 模块有正确的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `7b3fe3c2` | Use FPoseValueBundle in AnimOp value bundle evaluator | 将 AnimOp 值包评估器迁移至使用 FPoseValueBundle，统一数据表示。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，属于日志系统标准化工作。 |
| 2026-04-01 | `e9bc431c` | PoseSearch - removing unnecessary MotionMatchingInteraction node | 移除不再必要的 MotionMatchingInteraction 节点，进行代码清理。 |
| 2026-04-01 | `d6ad87e4` | UAFPoseSearch - consolidating FUAFDebuggerTrackCreator and FDebuggerTrackCreator, since GetTargetTyp | 合并调试轨道创建器，消除冗余代码。 |
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 为只有一个子节点的动画节点添加了修改器动画节点数据基类，优化代码结构。 |

### 维护评价

**综合评价：实验性、活跃开发中**

*   **状态**：该插件于 2025 年 6 月创建，**非常新**，且标记为 `IsExperimentalVersion = true`。
*   **更新频率**：近期（2026年4月）有连续的代码提交，但主要集中在**代码清理、重构和标准化**（如日志迁移、合并冗余类），而非新功能添加。这表明项目可能已进入功能基本实现后的**稳定和优化阶段**。
*   **推荐度**：**不推荐在生产项目中直接使用**。作为实验性模块，其 API 和功能可能在未来版本中发生不兼容的变更。但对于学习 UAF 动画系统、研究 Pose Search 集成，或在原型开发中体验前沿动画技术，它是一个非常有价值参考。
*   **潜在风险**：依赖实验性的 UAF/AnimNext 框架，未来版本升级可能伴随较大改动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch/Tests) （插件内测试模块）