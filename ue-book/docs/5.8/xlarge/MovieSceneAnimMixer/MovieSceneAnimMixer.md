# Sequencer Anim Mixer

> System for mixing layered animation in sequences

| 属性 | 值 |
|---|---|
| 中文名 | 序列器动画混合器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画混合模板） |
| 模块 | `MovieSceneAnimMixer` (Runtime), `MovieSceneAnimMixerEditor` (Runtime), `MovieSceneAnimMixerScripting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieSceneAnimMixer) | |

---

## 用途

MovieSceneAnimMixer 为 Sequencer 提供了一套全新的分层动画混合管线，替代传统的 Skeletal Animation System。它解决的核心问题是：**如何在 Sequencer 中将来自不同来源的动画（动画序列、Control Rig、未来可扩展的类型如面部动画、注视、运动匹配等）模块化地产出、混合，并发送到不同的动画目标（自定义 AnimInstance、蓝图槽位、AnimNext 注入点等）**。

传统 Sequencer 动画处理流程将动画产出和混合逻辑耦合在 Skeletal Animation System 内部，难以扩展。本插件采用 ECS（实体组件系统）架构，通过 Evaluation Task（求值任务）链式执行，使用共享 VM 内存中的 Pose Keyframe 栈来实现混合。这种架构使得：

- **多种动画产出类型**可以在同一个轨道上混合，每种类型只需实现一个将动画转化为 Evaluation Task 的 ECS 系统
- **多种动画目标**可以接收混合结果，包括自定义 AnimInstance、Anim Blueprint 节点、AnimNext 模块注入点等
- **Root Motion** 可以单独提取和混合，支持绝对定位确保序列跳转时的确定性
- **层级式混合**通过 Bus 机制实现跨对象的动画数据共享

---

## 使用场景

- 你在 Sequencer 中需要对同一角色的多个动画轨道进行**分层混合**（如身体动画 + 手部覆盖动画 + 面部动画），且需要精确控制混合权重和优先级
- 你需要将 Sequencer 动画**注入到 AnimNext/UAF 模块**的注入点，用于复杂的动画图管线
- 你需要跨对象共享动画姿态数据（通过 **Bus 总线**机制），例如让多个角色共享某个姿态片段
- 你需要精确控制 **Root Motion** 的应用方式：应用到 Actor、Component、Root Bone 还是作为属性传递
- 你需要在动画片段之间创建**平滑的过渡混合**（Crossfade 或 Inertial Dead Blend）
- 你需要基于骨骼的**逐骨蒙版混合**（Bone Mask），只对特定骨骼施加覆盖动画

---

## 蓝图用法

> ⚠️ 本插件主要面向 Sequencer 编辑器和 C++ 扩展，直接的蓝图节点较少。核心工作流通过 Sequencer UI 完成。

### 动画蓝图节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Sequencer Mixer Target` | Anim Blueprint 中的混合目标节点，通过 TargetName 与 Sequencer 中的轨道匹配 | `FAnimNode_SequencerMixerTarget` |

**使用方式**：在 Anim Blueprint 中添加 `Sequencer Mixer Target` 节点，设置一个唯一的 `TargetName`。然后在 Sequencer 的 Animation Mixer Track 的 Mixed Animation Target 属性中选择 "Anim Blueprint Target" 并填入相同的节点名称。序列器播放时，混合结果会注入到该节点。

### 配置设置

| 属性 | 说明 | 所在类 |
|---|---|---|
| `DefaultInjectionSite` | 默认的 AnimNext 注入站点 | `UMovieSceneAnimMixerSettings` |
| `DefaultUAFModule` | 默认的 UAF 模块 | `UMovieSceneAnimMixerSettings` |

配置路径：**项目设置 → Plugins → Anim Mixer**

---

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneAnimMixerModule.h"
#include "MovieSceneAnimationMixerTrack.h"
#include "Systems/MovieSceneAnimMixerSystem.h"
#include "Systems/MovieSceneRootMotionSystem.h"
#include "AnimMixerBakeEvaluation.h"
#include "AnimMixerBoneMatching.h"
```

### 基本用法：烘焙求值

对混合器在指定时间点进行独立求值，获取混合后的姿态和 Root Motion。适用于预计算或离线烘焙场景。

```cpp
#include "AnimMixerBakeEvaluation.h"
#include "MovieSceneAnimationMixerTrack.h"

// 来源: Public/AnimMixerBakeEvaluation.h

// 获取 Entity Linker 和 Mixer Track
UMovieSceneEntitySystemLinker* Linker = /* ... */;
UE::MovieScene::FInstanceHandle InstanceHandle = /* ... */;
UMovieSceneAnimationMixerTrack* MixerTrack = /* ... */;
FFrameTime Time(100); // 指定帧

// 求值单个时间点
UE::MovieScene::AnimMixerBakeEvaluation::FBakeResult Result = 
    UE::MovieScene::AnimMixerBakeEvaluation::EvaluateAtTime(
        Linker, InstanceHandle, MixerTrack, Time);

if (Result.IsValid())
{
    // Result.RootMotionTransform  - 混合后的 Root Motion（世界空间）
    // Result.AnimationSpaceRootMotion - 动画空间的 Root Motion
    // Result.Pose                  - 混合后的骨骼姿态
    // Result.Curves                - 混合后的动画曲线
    // Result.Attributes            - 混合后的属性
}
```

### 基本用法：批量烘焙

当需要对整个序列进行烘焙时，使用批量接口更高效（只执行一次状态保存/恢复）。

```cpp
// 来源: Public/AnimMixerBakeEvaluation.h

FFrameTime StartTime(0);
FFrameTime FrameStep(1); // 每帧采样
int32 NumSamples = 120;  // 120帧

TArray<UE::MovieScene::AnimMixerBakeEvaluation::FBakeResult> Results = 
    UE::MovieScene::AnimMixerBakeEvaluation::EvaluateRange(
        Linker, InstanceHandle, MixerTrack,
        StartTime, FrameStep, NumSamples);

for (const auto& Result : Results)
{
    // 处理每帧的求值结果
}
```

### 进阶用法：带过滤器的烘焙

使用 BakeFilter 可以选择性地只混合特定 Section 的动画，或跳过 Root Motion 空间转换。

```cpp
// 来源: Public/AnimMixerBakeEvaluation.h

UE::MovieScene::AnimMixerBakeEvaluation::FBakeFilter Filter;
// 只包含指定 Section
Filter.IncludeOnlySections.Add(FObjectKey(TargetSection));
// 或排除某些 Section
Filter.ExcludeSections.Add(FObjectKey(UnwantedSection));
// 限制优先级范围
Filter.MinPriority = 0;
Filter.MaxPriority = 10;
// 跳过 Root Motion 空间转换，获取动画空间原始值
Filter.bSkipRootMotionConversion = true;

auto Result = UE::MovieScene::AnimMixerBakeEvaluation::EvaluateAtTime(
    Linker, InstanceHandle, MixerTrack, Time, Filter);
```

### 进阶用法：骨骼匹配（Bone Matching）

计算一个动画 Section 中指定骨骼与底层姿态的匹配偏移，用于将新动画精确对齐到角色当前位置。

```cpp
// 来源: Public/AnimMixerBoneMatching.h

#include "AnimMixerBoneMatching.h"
#include "MovieSceneBoneMatchData.h"

// 设置匹配参数
FMovieSceneBoneMatchData MatchSettings;
MatchSettings.BoneName = FName("pelvis");
MatchSettings.bMatchLocationX = true;
MatchSettings.bMatchLocationY = true;
MatchSettings.bMatchLocationZ = false;
MatchSettings.bMatchRotationZ = true;
MatchSettings.MatchTimeMode = EBoneMatchTimeMode::AtStartOfSelectedSection;

// 创建匹配上下文
UE::MovieScene::AnimMixerBoneMatching::FBoneMatchingContext Context;
Context.Linker = EntityLinker;
Context.InstanceHandle = InstanceHandle;
Context.MixerTrack = MixerTrack;
Context.CurrentTime = CurrentTime;

// 执行骨骼匹配
FMovieSceneBoneMatchData Result = 
    UE::MovieScene::AnimMixerBoneMatching::ComputeBoneMatch(
        TargetSection, MatchSettings, Context);

if (Result.bIsValid)
{
    // Result.MatchTransform 包含计算出的匹配偏移变换
    FTransform MatchOffset = Result.MatchTransform;
}
```

### 进阶用法：Bus 总线拓扑

Bus 允许跨对象共享动画姿态数据。可以通过工具函数检查和验证 Bus 依赖关系。

```cpp
// 来源: Public/AnimMixerBusUtils.h

#include "AnimMixerBusUtils.h"

// 收集序列中的所有 Bus 名称
TArray<FName> BusNames = 
    FAnimMixerBusUtils::GatherBusNamesFromSequence(RootSequence);

// 计算 Bus 求值顺序（拓扑排序）
TArray<FName> EvalOrder = 
    FAnimMixerBusUtils::ComputeBusEvaluationOrder(MixerTracks);

// 验证 Bus 拓扑
FAnimMixerBusValidationResult ValidationResult = 
    FAnimMixerBusUtils::ValidateBusTopology(MixerTracks);

if (ValidationResult.HasErrors())
{
    for (const FString& Error : ValidationResult.Errors)
    {
        UE_LOG(LogMovieSceneAnimMixer, Error, TEXT("%s"), *Error);
    }
}

// 检查添加 Bus Section 是否会创建循环依赖
bool bWouldCycle = FAnimMixerBusUtils::WouldBusSectionCreateCycle(
    BusName, TargetTrack, AllMixerTracks);
```

---

## Demo 示例

以下示例展示如何创建一个自定义的动画混合 Evaluation Task，并将其注册到混合器系统中。

```cpp
// MyAnimMixerTask.h
#pragma once

#include "CoreMinimal.h"
#include "EvaluationVM/Tasks/AnimNextEvaluationTask.h"
#include "MyAnimMixerTask.generated.h"

USTRUCT()
struct FMyCustomBlendTask : public FAnimNextEvaluationTask
{
    GENERATED_BODY()
    
    DECLARE_ANIM_EVALUATION_TASK(FMyCustomBlendTask)

    virtual void Execute(UE::UAF::FEvaluationVM& VM) const override;

    // 混合权重 0.0 = 原始姿态, 1.0 = 完全覆盖
    UPROPERTY()
    float BlendAlpha = 0.0f;
};
```

```cpp
// MyAnimMixerTask.cpp
#include "MyAnimMixerTask.h"

IMPLEMENT_ANIM_EVALUATION_TASK(FMyCustomBlendTask)

void FMyCustomBlendTask::Execute(UE::UAF::FEvaluationVM& VM) const
{
    // 在 VM 栈顶有两个姿态 keyframe:
    // Top = 目标覆盖姿态 (从后续任务推入)
    // Top-1 = 源姿态 (从之前任务推入)
    //
    // 按照混合权重进行插值
    // 实际实现需要调用 VM 的混合指令或直接操作 FLODPoseHeap
    
    // FMovieSceneAccumulateAbsoluteBlendTask 展示了类似的混合模式：
    // Top = (Top-1) + (Top * ScaleFactor)
    
    // 这里仅展示结构，实际实现需要访问 VM 的 pose stack
}
```

---

## 模块依赖

本插件依赖 AnimNext（UAF）系统作为底层混合框架，以及 Sequencer 的 ECS 实体系统。

| 模块 | 用途 |
|---|---|
| `AnimNextRuntime` | Evaluation Task 框架、Evaluation VM、求值程序 |
| `AnimNextEditor` | 编辑器集成 |
| `MovieSceneTools` | Sequencer 编辑器工具 |
| `MovieScene` | Sequencer 核心 ECS 系统 |
| `EntityCore` | 实体组件系统 |
| `Settings` | 开发者设置框架 |

> 注：本插件未启用（`EnabledByDefault=false`），需要在 Plugins 面板手动启用。同时需要 **AnimNext** 插件作为前置依赖。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `00f154d0` | Sequencer Anim Mixer: fix root motion pop at boundary between a KeepState section and an Accumulated | 修复 KeepState 和 Accumulated 段边界处的 Root Motion 跳变问题 |
| 2026-05-26 | `8905e197` | Sequencer: Fix Anim Mixer section gizmo freezing when dragged with AutoKey Off | 修复关闭自动关键帧时拖拽混合器 Section Gizmo 冻结的问题 |
| 2026-05-22 | `5f14e324` | Sequencer: Anim Mixer: force-link CachePreAnimatedStateSystem from AnimMixerSystem | 从混合器系统强制链接缓存预动画状态系统 |
| 2026-05-22 | `5515824d` | Sequencer: Anim mixer fix InitialRoot mismatch between cache and runtime that slid character across | 修复缓存与运行时初始根变换不匹配导致角色滑移的问题 |
| 2026-05-22 | `5c05fad6` | Sequencer: Anim mixer- fix issue where following a section with an anim with rotation in the offset | 修复包含旋转偏移动画的 Section 后续 Section 的问题 |

### 维护评价

**活跃维护中** 🟢

本插件创建于 2025 年 1 月，距今约 1.4 年，处于**快速迭代开发阶段**。最近的提交记录显示 2026 年 5 月仍有密集的功能修复和改进（仅 5 天内就有 5 次提交），涉及 Root Motion 边界处理、编辑器交互修复、缓存一致性等核心功能。

**注意事项**：
- **实验性标记**：`IsExperimentalVersion=true`，API 和功能可能在后续版本中发生重大变更
- **未默认启用**：需要手动在 Plugins 面板中启用，且依赖 AnimNext 插件
- **版本号 0.1**：明确表示为早期预览版本
- **首次提交的 TODO 列表**中提到了多项未完成的功能：零权重任务优化、源姿态混合、运动矢量模拟、镜像支持等
- 该插件正在积极开发中，是 Sequencer 动画系统的未来方向，但**不建议在生产环境中使用**

**推荐指数**：适合对 Sequencer 动画混合有前沿需求的开发者提前研究和预览，不建议用于生产项目。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieSceneAnimMixer)
- [官方文档](https://epicgames.com)（暂无独立文档）