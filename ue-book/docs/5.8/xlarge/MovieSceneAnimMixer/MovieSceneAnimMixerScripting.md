# Sequencer Anim Mixer

> System for mixing layered animation in sequences

| 属性 | 值 |
|---|---|
| 中文名 | 序列器动画混合器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MovieSceneAnimMixer` (Runtime), `MovieSceneAnimMixerEditor` (Runtime), `MovieSceneAnimMixerScripting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieSceneAnimMixer) | |

## 用途

该插件为 Sequencer 中的骨骼动画处理提供了一条新的、模块化的路径。传统 Sequencer 的动画轨道将动画的生产（如播放动画序列）与混合（如在不同动画间过渡）紧密耦合，限制了灵活性。

**MovieSceneAnimMixer** 的核心目标是解耦这个过程，引入“动画生产者”（Animation Producer）和“动画目标”（Animation Target）的概念。它利用 Unreal 的 ECS（实体组件系统）和来自 **AnimNext** 的“评估任务”（Evaluation Task）系统来构建一个“评估程序”（Evaluation Program）。这个程序本质上是一个由多种动画源（如动画序列、Control Rig，未来可能还包括 Idle、表情、注视、动作匹配等）构建的、包含所有混合逻辑的指令列表。

该程序可以被发送到不同的“动画目标”去执行，例如一个自定义的 AnimInstance、蓝图中的动画槽位，或是 **AnimNext** 的注入点。这使得动画的生产、混合与最终应用变得高度模块化和可扩展。

**该插件解决了以下问题**：
- **僵化的动画处理流程**：允许在同一 Sequencer 轨道内混合来自不同类型生产者的动画。
- **动画目标限制**：支持将混合后的动画输出到多种目标，而不仅仅是标准的 SkeletalMeshComponent。
- **根运动处理**：通过评估程序，可以提前（在动画 Tick 之前）计算和混合根运动，确保确定性，尤其是在序列跳转时。

## 使用场景

- 你需要在 Sequencer 中组合来自不同来源的动画（例如，一个 AnimSequence + 一个 Control Rig 轨道）并希望它们在播放时自动混合。
- 你正在开发一个复杂的角色动画系统，需要将 Sequencer 产出的动画注入到自定义的 AnimInstance 或 **AnimNext** 的评估流中。
- 你需要更精确地控制动画之间的过渡（Transitions），并希望通过脚本（蓝图）程序化地创建和管理这些过渡。

## 蓝图用法

插件通过多个 `UBlueprintFunctionLibrary` 提供了丰富的蓝图函数，用于操作混合器轨道、层、过渡和装饰。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Layers` | 获取混合器轨道中的所有层 | `UMovieSceneAnimMixerTrackExtensions` |
| `Add Layer` | 在混合器轨道末尾添加一个新层 | `UMovieSceneAnimMixerTrackExtensions` |
| `Add Animation` | 向指定层的指定起始帧添加一个骨骼动画段 | `UMovieSceneAnimMixerTrackExtensions` |
| `Get Transition Between` | 获取两个特定动画段之间的过渡段 | `UMovieSceneAnimMixerTrackExtensions` |
| `Add Child Track To Layer` | 向一个空的混合器层添加子轨道（如 ControlRig 轨道） | `UMovieSceneAnimMixerTrackExtensions` |
| `Get Sections` | 获取一个层上的所有动画段 | `UMovieSceneAnimMixerLayerExtensions` |
| `Is Transition Valid` | 检查一个过渡段是否结构有效（两个段存在且在同一行） | `UMovieSceneAnimMixerTransitionExtensions` |
| `Change Transition Type` | 将一个过渡段更改为另一种类型，并尝试保留混合数据 | `UMovieSceneAnimMixerTransitionExtensions` |
| `Find Decoration` | 在一个容器对象上查找特定类型的装饰 | `UMovieSceneDecorationContainerExtensions` |

### 使用示例（蓝图描述）

1.  **动态构建动画混合轨道**：
    - 使用 `Sequencer` 蓝图库获取或创建一个 `UMovieSceneAnimationMixerTrack`。
    - 调用 `Add Layer` 创建两个层，分别得到 `Layer A` 和 `Layer B`。
    - 对 `Layer A` 调用 `Add Animation`，传入一个 `Walk` 动画序列。
    - 对 `Layer B` 调用 `Add Animation`，传入一个 `LookAround` 动画序列，时间上与 `Walk` 重叠。
    - 此时 Sequencer 播放时，两个动画将根据其权重进行混合。

2.  **查询和修改过渡**：
    - 假设已有两个动画段 `Section1` 和 `Section2`。
    - 调用 `Get Transition Between` 传入 `FromSection=Section1`, `ToSection=Section2` 来获取它们之间的过渡对象。
    - 如果返回的过渡对象有效，可以调用 `Is Transition Valid` 进行检查。
    - 或者调用 `Change TransitionType` 并指定一个新的过渡类，来改变混合效果。

## C++ 用法

### 头文件引入

```cpp
// 包含混合器轨道、层、过渡的扩展函数
#include "MovieSceneAnimMixerTrackExtensions.h"
#include "MovieSceneAnimMixerLayerExtensions.h"
#include "MovieSceneAnimMixerTransitionExtensions.h"
// 包含装饰容器操作函数
#include "MovieSceneDecorationContainerExtensions.h"
```

### 基本用法

以下代码展示了如何在 C++ 中程序化地向一个混合器轨道添加动画（来源: `Public/MovieSceneAnimMixerTrackExtensions.h` 中函数的典型使用逻辑）。

```cpp
// 假设我们有一个指向 Sequencer 资产或组件的指针
USequencer* Sequencer = ...;
// 获取或创建一个 AnimationMixerTrack
UMovieSceneAnimationMixerTrack* MixerTrack = /* 从 Sequencer 中获取或创建 */;

// 向轨道添加一个新层
UMovieSceneAnimationMixerLayer* NewLayer = UMovieSceneAnimMixerTrackExtensions::AddLayer(MixerTrack);
if (NewLayer)
{
    // 在第 0 帧，向该层添加一个动画
    UAnimSequence* MyAnimSequence = LoadObject<UAnimSequence>(nullptr, TEXT("/Game/Anims/Idle"));
    UMovieSceneSection* AnimSection = UMovieSceneAnimMixerTrackExtensions::AddAnimation(
        MixerTrack,
        NewLayer->GetLayerIndex(), // 或者直接传 0
        FFrameNumber(0),
        MyAnimSequence
    );
}
```

### 进阶用法

结合使用多个扩展函数来管理一个复杂的混合轨道（综合自多个头文件的功能）。

```cpp
// 1. 获取混合器轨道
UMovieSceneAnimationMixerTrack* Track = ...;

// 2. 在第 1 层（索引 0）添加一个动画段
UMovieSceneSection* Section1 = UMovieSceneAnimMixerTrackExtensions::AddAnimation(Track, 0, FFrameNumber(0), AnimSeq1);

// 3. 在同一层，稍后位置添加另一个动画段，创建一个过渡关系
UMovieSceneSection* Section2 = UMovieSceneAnimMixerTrackExtensions::AddAnimation(Track, 0, FFrameNumber(300), AnimSeq2);

// 4. 查询这两个段之间可能自动生成的过渡
UMovieSceneAnimTransitionSectionBase* Transition = UMovieSceneAnimMixerTrackExtensions::GetTransitionBetween(Track, Section1, Section2);
if (Transition)
{
    // 检查过渡是否有效
    bool bValid = UMovieSceneAnimMixerTransitionExtensions::IsTransitionValid(Transition);
    
    // 更改过渡类型（例如从线性混合改为缓动函数混合）
    TSubclassOf<UMovieSceneAnimTransitionSectionBase> NewTransitionClass = UMyEasingTransition::StaticClass();
    UMovieSceneAnimTransitionSectionBase* NewTransition = UMovieSceneAnimMixerTransitionExtensions::ChangeTransitionType(Transition, NewTransitionClass);
}

// 5. 在第 2 层（索引 1）添加一个子轨道（如 ControlRig 轨道）
TSubclassOf<UMovieSceneTrack> ControlRigTrackClass = UMovieSceneControlRigParameterTrack::StaticClass();
UMovieSceneTrack* ChildTrack = UMovieSceneAnimMixerTrackExtensions::AddChildTrackToLayer(Track, ObjectBindingGuid, ControlRigTrackClass, 1);
```

## Demo 示例

一个最小化的示例，展示如何在 C++ 中创建一个简单的混合器轨道并打印其层信息。

```cpp
// MyAnimMixerTest.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "MyAnimMixerTest.generated.h"

UCLASS()
class UMyAnimMixerTestSubsystem : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UFUNCTION(BlueprintCallable)
    void CreateTestMixerTrack();

private:
    void LogLayerInfo(UMovieSceneAnimationMixerTrack* Track);
};
```

```cpp
// MyAnimMixerTest.cpp
#include "MyAnimMixerTest.h"
#include "MovieSceneAnimMixerTrackExtensions.h"
#include "MovieSceneAnimMixerLayerExtensions.h"
#include "Tracks/MovieSceneAnimationMixerTrack.h"
#include "Sections/MovieSceneAnimationMixerLayer.h"

void UMyAnimMixerTestSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    UE_LOG(LogTemp, Log, TEXT("MyAnimMixerTestSubsystem Initialized"));
}

void UMyAnimMixerTestSubsystem::CreateTestMixerTrack()
{
    // 在 Sequencer 中创建一个混合器轨道（此处在内存中临时创建演示）
    UMovieSceneAnimationMixerTrack* TestTrack = NewObject<UMovieSceneAnimationMixerTrack>();
    if (!TestTrack)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create AnimationMixerTrack"));
        return;
    }

    // 添加两个层
    UMovieSceneAnimationMixerLayer* Layer0 = UMovieSceneAnimMixerTrackExtensions::AddLayer(TestTrack);
    UMovieSceneAnimationMixerLayer* Layer1 = UMovieSceneAnimMixerTrackExtensions::AddLayer(TestTrack);

    // 设置层名称
    if (Layer0) UMovieSceneAnimMixerLayerExtensions::SetDisplayName(Layer0, FText::FromString(TEXT("Base Layer")));
    if (Layer1) UMovieSceneAnimMixerLayerExtensions::SetDisplayName(Layer1, FText::FromString(TEXT("Additive Layer")));

    // 记录信息
    LogLayerInfo(TestTrack);
}

void UMyAnimMixerTestSubsystem::LogLayerInfo(UMovieSceneAnimationMixerTrack* Track)
{
    int32 Count = UMovieSceneAnimMixerTrackExtensions::GetLayerCount(Track);
    UE_LOG(LogTemp, Log, TEXT("MixerTrack has %d layers:"), Count);

    TArray<UMovieSceneAnimationMixerLayer*> Layers = UMovieSceneAnimMixerTrackExtensions::GetLayers(Track);
    for (UMovieSceneAnimationMixerLayer* Layer : Layers)
    {
        if (Layer)
        {
            FText Name = UMovieSceneAnimMixerLayerExtensions::GetDisplayName(Layer);
            int32 Index = UMovieSceneAnimMixerLayerExtensions::GetLayerIndex(Layer);
            bool bEmpty = UMovieSceneAnimMixerLayerExtensions::IsEmpty(Layer);
            UE_LOG(LogTemp, Log, TEXT("  Layer %d: '%s', Empty: %s"), Index, *Name.ToString(), bEmpty ? TEXT("true") : TEXT("false"));
        }
    }
}
```

## 模块依赖

从 `MovieSceneAnimMixerScripting` 模块的 `Build.cs` 文件分析，该脚本模块对核心库没有特殊依赖，主要依赖引擎常见模块。

| 模块 | 用途 |
|---|---|
| `Settings` | 访问项目或编辑器设置，可能用于配置混合器行为或实验性功能开关 |

**核心模块 `MovieSceneAnimMixer`** 的依赖（从首次提交信息推断）必然包含：
- `Engine` (Runtime)
- `Core` (Runtime)
- `CoreUObject` (Runtime)
- `MovieScene` (Runtime) – Sequencer 核心
- `SequencerCore` (Runtime)
- `AnimNext` 或相关模块 – 评估任务系统

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `00f154d0` | Sequencer Anim Mixer: fix root motion pop at boundary between a KeepState section and an Accumulated | 修复了在“保持状态”和“累积”动画段边界处根运动跳变的 BUG。 |
| 2026-05-26 | `8905e197` | Sequencer: Fix Anim Mixer section gizmo freezing when dragged with AutoKey Off | 修复了在关闭自动关键帧时，拖动混合器段 Gizmo 会卡住的编辑器交互问题。 |
| 2026-05-22 | `5f14e324` | Sequencer: Anim Mixer: force-link CachePreAnimatedStateSystem from AnimMixerSystem | 强制从混合器系统链接动画状态缓存系统，解决初始化依赖问题。 |
| 2026-05-22 | `5515824d` | Sequencer: Anim mixer fix InitialRoot mismatch between cache and runtime that slid character across | 修复了缓存与运行时初始根骨骼不匹配导致角色滑移的 BUG。 |
| 2026-05-22 | `5c05fad6` | Sequencer: Anim mixer- fix issue where following a section with an anim with rotation in the offset | 修复了当后续动画段包含旋转偏移时的混合问题。 |

### 维护评价

- **状态**：**活跃维护中**。该插件创建于 2025 年初，非常“年轻”。从提交记录看，开发团队在近期（2026年5月）集中修复了多个关键的运行时和编辑器BUG，表明它正处于积极开发和打磨阶段。
- **实验性**：`.uplugin` 明确标记为 `IsExperimentalVersion: true`，且默认禁用。这意味着它功能、API 和工作流程都可能发生不兼容的变更。
- **已知限制**：
    - 不支持运动矢量模拟和旧动画轨道的“镜像”功能。
    - 混合优化（如剔除零权重任务）尚未实现。
    - UX 待完善，例如用于组织子轨道的“Mixer Track”计划还未实现。
- **推荐使用**：
    - **推荐用于评估和原型开发**：如果你正在为项目规划下一代动画系统，或者对 Sequencer 的动画混合能力有更高要求，这是值得关注和试验的前沿方向。
    - **不推荐用于生产环境**：鉴于其“实验性”标签、频繁的修复以及明确的不完整功能列表，目前不建议在需要稳定性的商业项目中作为核心依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieSceneAnimMixer)
- [官方文档]( ) （.uplugin 中 DocsURL 为空，暂无官方文档）
- [测试用例]( ) （未在提供的文件中发现显式测试用例路径）