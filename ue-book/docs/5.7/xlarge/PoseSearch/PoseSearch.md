# Pose Search

> Framework for indexing and searching pose features. Used in techniques such as Motion Matching.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、数据资产、蓝图资产） |
| 模块 | `PoseSearch` (Runtime), `PoseSearchEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-06-16 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PoseSearch) | |

## 用途

PoseSearch 是 UE5 的**运动匹配（Motion Matching）**核心框架。它解决的核心问题是：**如何从大量动画片段中，实时找到最匹配当前角色姿态和运动意图的那一段动画**。

传统动画状态机需要手动定义状态和过渡条件，而 Motion Matching 通过将动画数据库中的每一帧都索引为一个高维特征向量（包含骨骼位置、速度、轨迹等），在运行时将当前角色的特征向量与数据库中的所有候选项进行比对，自动选择最相似的动画片段播放。

该插件提供了：
- **特征通道系统**：可配置的特征提取通道（骨骼姿态、轨迹、速度、朝向、曲线等），定义"用什么维度来描述一帧动画"
- **数据库索引**：将动画资产预处理为特征向量数据库，支持异步构建和缓存
- **运行时搜索**：高效的最近邻搜索算法，从数据库中找到最佳匹配
- **多角色交互**：支持多个角色同时参与的交互式运动匹配（如双人握手、格斗）
- **事件驱动搜索**：支持基于 GameplayTag 的事件触发搜索，可配合播放速率调整

**注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你在做一个需要流畅角色运动的游戏（如第三人称动作游戏）→ 用 PoseSearch 实现 Motion Matching 替代复杂的状态机
- 你有大量动作捕捉数据需要智能选择播放 → 用 PoseSearchDatabase 索引动画，运行时自动匹配
- 你需要角色根据移动意图（摇杆输入）自动选择合适的转向、加速、减速动画 → 配置 Trajectory 通道
- 你需要两个或多个角色进行同步交互动画（如双人格斗、搬运重物）→ 用 MotionMatchingInteraction 节点和 UPoseSearchInteractionAsset
- 你需要在特定事件发生时（如攻击命中）搜索最合适的动画 → 用 FPoseSearchEvent 配合 TimeToEvent 通道

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConvertToMotionMatchingNode` | 将 AnimNodeReference 转换为 MotionMatching 节点引用 | `UMotionMatchingAnimNodeLibrary` |
| `GetMotionMatchingSearchResult` | 获取当前运动匹配搜索结果（选中的动画、代价等） | `UMotionMatchingAnimNodeLibrary` |
| `SetDatabaseToSearch` | 动态设置运动匹配节点要搜索的数据库 | `UMotionMatchingAnimNodeLibrary` |
| `OverrideMotionMatchingBlendSettings` | 覆盖运动匹配的混合参数 | `UMotionMatchingAnimNodeLibrary` |
| `ConvertToPoseHistoryNode` | 将 AnimNodeReference 转换为 PoseHistory 节点引用 | `UPoseSearchHistoryCollectorAnimNodeLibrary` |
| `GetPoseHistoryNodeTransformTrajectory` | 获取姿态历史节点的轨迹数据 | `UPoseSearchHistoryCollectorAnimNodeLibrary` |
| `SetPoseHistoryNodeTransformTrajectory` | 设置姿态历史节点的轨迹数据 | `UPoseSearchHistoryCollectorAnimNodeLibrary` |
| `MotionMatchInteraction_Pure` | 执行多角色交互式运动匹配搜索 | `UPoseSearchInteractionLibrary` |
| `MotionMatchInteraction` | 执行多角色交互式运动匹配搜索（非纯函数版） | `UPoseSearchInteractionLibrary` |
| `GetMontageContinuingProperties` | 获取蒙太奇的继续播放属性 | `UPoseSearchInteractionLibrary` |
| `ConvertToMotionMatchingInteractionNode` | 转换为交互式运动匹配节点引用 | `UMotionMatchingInteractionAnimNodeLibrary` |
| `SetAvailabilities` | 设置交互节点的可用性列表 | `UMotionMatchingInteractionAnimNodeLibrary` |
| `IsInteracting` | 检查交互节点是否正在交互中 | `UMotionMatchingInteractionAnimNodeLibrary` |
| `UpdatePoseSearchEvent` | 更新运动匹配事件状态 | `UPoseSearchEventLibrary` |
| `GetAnimationAsset` | 获取多角色资产中指定角色的动画 | `UMultiAnimAsset` |
| `GetOrigin` | 获取多角色资产中指定角色的原点变换 | `UMultiAnimAsset` |

### 使用示例（蓝图描述）

**基本 Motion Matching 设置：**

1. 在 AnimGraph 中添加 `MotionMatching` 节点
2. 创建 `UPoseSearchSchema` 资产，配置特征通道（Pose、Trajectory 等）
3. 创建 `UPoseSearchDatabase` 资产，添加动画序列并关联 Schema
4. 将 Database 赋给 MotionMatching 节点的 Database 属性
5. 在 AnimGraph 中添加 `PoseSearchHistoryCollector` 节点收集姿态历史
6. 通过 `GetMotionMatchingSearchResult` 节点获取搜索结果，可用于调试或逻辑判断

**动态切换数据库：**

1. 使用 `ConvertToMotionMatchingNode` 获取节点引用
2. 调用 `SetDatabaseToSearch` 传入新的 Database 和中断模式
3. 运动匹配将在下一帧使用新数据库进行搜索

**多角色交互：**

1. 为每个角色创建 `FPoseSearchInteractionAvailability`，指定 Database、角色过滤和搜索半径
2. 调用 `MotionMatchInteraction_Pure` 传入可用性列表
3. 检查返回的 `FPoseSearchBlueprintResult` 是否有效
4. 使用 `ConvertToMotionMatchingInteractionNode` + `SetAvailabilities` 在 AnimGraph 中设置交互

## C++ 用法

### 头文件引入

```cpp
#include "PoseSearch/PoseSearchLibrary.h"
#include "PoseSearch/PoseSearchDatabase.h"
#include "PoseSearch/PoseSearchSchema.h"
#include "PoseSearch/MotionMatchingAnimNodeLibrary.h"
#include "PoseSearch/PoseSearchInteractionLibrary.h"
#include "PoseSearch/PoseSearchEvent.h"
#include "PoseSearch/PoseSearchAssetSampler.h"
```

### 基本用法 — 动画资产采样

从 `FAnimationAssetSampler` 的接口提取动画姿态数据：

```cpp
#include "PoseSearch/PoseSearchAssetSampler.h"

// 创建采样器并初始化
UE::PoseSearch::FAnimationAssetSampler Sampler;
Sampler.Init(MyAnimationAsset, FTransform::Identity, FVector::ZeroVector);

// 获取动画时长
float PlayLength = Sampler.GetPlayLength();

// 在指定时间提取姿态
FCompactPose OutPose;
Sampler.ExtractPose(0.5f, OutPose);

// 提取根骨骼变换
FTransform RootTransform = Sampler.ExtractRootTransform(0.5f);

// 提取完整姿态（含曲线）
FCompactPose Pose;
FBlendedCurve Curve;
Sampler.ExtractPose(0.5f, Pose, Curve);
```

### 基本用法 — 运动匹配事件

```cpp
#include "PoseSearch/PoseSearchEvent.h"

// 创建运动匹配事件
FPoseSearchEvent SearchEvent;
SearchEvent.EventTag = FGameplayTag::RequestGameplayTag(FName("Event.Attack"));
SearchEvent.TimeToEvent = 0.3f;
SearchEvent.bEnablePoseFilters = true;
SearchEvent.bUsePlayRateRangeOverride = true;
SearchEvent.PlayRateRangeOverride = FFloatInterval(0.8f, 1.2f);

// 在 Tick 中更新事件
FPoseSearchEvent CurrentEvent;
bool bNewEventValid = true;
UPoseSearchEventLibrary::UpdatePoseSearchEvent(SearchEvent, bNewEventValid, DeltaTime, CurrentEvent);
```

### 进阶用法 — 多角色交互

```cpp
#include "PoseSearch/PoseSearchInteractionLibrary.h"
#include "PoseSearch/PoseSearchInteractionAvailability.h"

// 设置交互可用性
TArray<FPoseSearchInteractionAvailability> Availabilities;
FPoseSearchInteractionAvailability& Avail = Availabilities.AddDefaulted_GetRef();
Avail.Database = MyInteractionDatabase;
Avail.RolesFilter.Add(FName("CharacterA"));
Avail.BroadPhaseRadius = 500.f;
Avail.bDisableCollisions = true;

// 执行交互搜索
FPoseSearchBlueprintResult Result = UPoseSearchInteractionLibrary::MotionMatchInteraction_Pure(
    Availabilities, 
    MyAnimInstance, 
    FName("PoseHistory")
);

// 检查结果
if (Result.bIsInteraction && Result.SelectedAnimation)
{
    // 使用 Result.PlayingMontage 获取要播放的蒙太奇
    // 使用 Result.SelectedTime 获取起始时间
    // 使用 Result.SearchCost 获取匹配代价
}
```

### 进阶用法 — 镜像数据缓存

```cpp
#include "PoseSearch/PoseSearchMirrorDataCache.h"

// 创建镜像数据缓存
UE::PoseSearch::FMirrorDataCache MirrorCache;
MirrorCache.Init(MyMirrorDataTable, BoneContainer);

// 镜像变换
FTransform MirroredTransform = MirrorCache.MirrorTransform(SourceTransform);

// 镜像姿态
MirrorCache.MirrorPose(CompactPose);
```

## Demo 示例

### 自定义特征通道（蓝图可扩展的曲线通道）

```cpp
// MyCurveChannel.h
#pragma once

#include "PoseSearch/PoseSearchFeatureChannel_Curve.h"
#include "MyCurveChannel.generated.h"

UCLASS(EditInlineNew, meta = (DisplayName = "My Custom Curve Channel"))
class UMyCurveChannel : public UPoseSearchFeatureChannel_Curve
{
    GENERATED_BODY()

public:
    UMyCurveChannel()
    {
        CurveName = FName("DistanceToWall");
        Weight = 1.0f;
        SampleTimeOffset = 0.5f; // 匹配 0.5 秒后的距离值
    }
};
```

### 运行时查询运动匹配结果

```cpp
// MyAnimInstance.h
#pragma once

#include "Animation/AnimInstance.h"
#include "PoseSearch/PoseSearchLibrary.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Motion Matching")
    TObjectPtr<UPoseSearchDatabase> LocomotionDatabase;

    // 在蓝图中调用，获取当前最佳匹配
    UFUNCTION(BlueprintCallable, Category = "Motion Matching")
    FPoseSearchBlueprintResult GetCurrentMatchResult() const;

private:
    FPoseSearchBlueprintResult CachedResult;
};
```

```cpp
// MyAnimInstance.cpp
#include "MyAnimInstance.h"
#include "PoseSearch/PoseSearchLibrary.h"

FPoseSearchBlueprintResult UMyAnimInstance::GetCurrentMatchResult() const
{
    return CachedResult;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `BlendStack` | 动画混合栈，MotionMatching 节点的基类 FAnimNode_BlendStack |
| `Chooser` | 选择器系统，用于参数化姿态搜索 |
| `AnimationWarping` | 动画变形，用于交互式运动匹配中的位置/旋转校正 |
| `GameplayInsights` | 游戏洞察（仅编辑器），用于调试可视化 |

## 维护状态

### 近期更新

```
- a57af5cb418d Allow sampling of mover trajectory at a different (higher frequency) rate than we output to the trajectory, to avoid errors from moves which are not timestep independent. Change use of PoseSearchTrajectoryPredictor so that it is not expected to also set the current transform, it is only expected to predict into the future. This makes the meaning of 'NumPredictionSamples' more consistent throughout the API
- 2347bd961142 PoseSearch - fix for crash when you add a Pose Match Column when the chooser has no data type
- c769ccbe2aca Small fixes for pose search trajectory library.
```

- 最近的更新集中在轨迹预测器 API 改进和 bug 修复，说明该系统仍在积极迭代
- 轨迹采样频率与输出频率解耦，提升了运动匹配的精度
- 修复了 Chooser 集成中的崩溃问题

### 维护评价

**活跃维护中**。PoseSearch 是 Epic Games 为 UE5 Motion Matching 功能开发的核心插件，自 2020 年创建以来持续更新。从代码中可以看到大量 API 在 5.6 版本经历了重构（如 `FPoseSearchQueryTrajectory` 被废弃，替换为 `FTransformTrajectory`），说明该系统仍在快速演进。

**注意事项**：
- 该插件**默认未启用**（`EnabledByDefault: false`），需要在项目设置中手动启用
- 多个功能标记为 `Experimental`（交互系统、轨迹预测器、部分特征通道等），可能在后续版本中发生变化
- 依赖 `BlendStack`、`Chooser`、`AnimationWarping` 等插件，需确保这些插件也已启用
- 320 个源文件的大型插件，学习曲线较陡

**推荐使用**：如果你的项目需要高质量的角色运动系统，且愿意投入时间学习 Motion Matching 的配置流程，PoseSearch 是 UE5 官方提供的最佳方案。对于简单项目，传统的状态机可能更合适。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PoseSearch)
- [官方文档]()（暂无）