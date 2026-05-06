# Sequencer Anim Mixer

> System for mixing layered animation in sequences

| 属性 | 值 |
|---|---|
| 中文名 | 序列动画混合器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、蓝图节点） |
| 模块 | `MovieSceneAnimMixer` (Runtime), `MovieSceneAnimMixerEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneAnimMixer) | |

## 用途

Sequencer Anim Mixer 是一个实验性插件，为 UE5 的关卡序列（Level Sequencer）提供**分层动画混合**能力。它基于 Unreal Animation Framework（UAF）和 AnimNext 技术栈，允许在单个序列中混合多个独立的动画输入（例如全身动画、面部动画、根运动偏移），并通过优先级、加法/绝对模式、目标选择等机制灵活控制最终姿态。

该插件解决了传统 Sequencer 动画轨道混叠时缺乏层叠混合、根运动控制困难的问题。它提供了多种目标注入方式（Anim Blueprint 节点、自定义 Anim Instance、UAF 模块注入），使得动画师可以在序列中精细控制角色动画的混合层级。

## 使用场景

- 制作电影级过场动画，需要将多个动画层（如运动、表情、手部）按照优先级和权重混合。
- 在序列中同时控制角色的根运动和骨骼动画，并决定根运动是累加还是覆盖。
- 创建一个自定义动画蓝图，使用 "Sequencer Mixer Target" 节点接收来自序列的混合结果。
- 将序列动画注入到现有的 AnimNext 模块中，实现模块化动画组合。

## 蓝图用法

插件的核心蓝图节点是动画蓝图中的 **Sequencer Mixer Target** 节点（对应 `FAnimNode_SequencerMixerTarget`）。此外，序列编辑器中的动画混合器轨道（MovieSceneAnimationMixerTrack）和根运动节（Root Motion Section）也提供了可视化配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Sequencer Mixer Target` | 在 Anim Blueprint 中定义接收序列混合结果的目标点，通过 `TargetName` 匹配序列中的动画目标 | `FAnimNode_SequencerMixerTarget` |
| `Root Motion` 节 | 用于声明根运动的目的地（丢弃、留在骨骼、应用到组件或 Actor、输出到属性） | `UMovieSceneRootMotionSection` |
| `Anim Blueprint Target`（结构） | 声明一个匹配 Anim Blueprint 混合节点名称的目标，用于注入序列动画 | `FMovieSceneAnimBlueprintTarget` |
| `UAF Module Injection`（结构） | 声明一个匹配 UAF 模块注入点的目标，使用 `InjectionSite` 指定注入位置 | `FMovieSceneAnimNextInjectionTarget` |
| `Custom Anim Instance`（结构） | 声明一个使用自定义动画实例的目标，由系统自动创建 `USequencerMixedAnimInstance` | `FMovieSceneAnimInstanceTarget` |

### 使用示例（蓝图描述）

1. **创建 Anim Blueprint 混合**：在动画蓝图（AnimBP）中，将 `Sequencer Mixer Target` 节点连接到输出姿势（Output Pose）。设置 `Target Name` 为唯一标识（如 "MainBody"）。将基础动画（如混合空间）输入到 `Source Pose` 引脚。
2. **序列中配置混合**：在序列中添加 `Animation Mixer` 轨道，并创建子轨道（如普通动画节、根运动节）。每个子轨道可通过细节面板指定目标名称（例如 "MainBody"）和优先级。
3. **运行序列**：序列播放时，系统将各子轨道的动画逐个混合到对应的 `Sequencer Mixer Target` 节点上，按照优先级和加法模式叠加，最终输出到角色。

## C++ 用法

### 头文件引入

```cpp
#include "AnimMixerComponentTypes.h"
#include "Systems/MovieSceneAnimMixerSystem.h"
#include "Systems/MovieSceneAnimBlueprintTargetSystem.h"
#include "Systems/MovieSceneAnimNextTargetSystem.h"
#include "Systems/MovieSceneAnimInstanceTargetSystem.h"
#include "Systems/MovieSceneMixedSkeletalAnimationSystem.h"
#include "Systems/MovieSceneRootMotionSystem.h"
#include "MovieSceneAnimationMixerTrack.h"
#include "MovieSceneRootMotionSection.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个自定义动画节，并通过实体系统向混合器注册条目（来自 `MovieSceneAnimationMixerTrack.cpp` 的简化逻辑）：

```cpp
// 头文件：MyCustomAnimationSection.h
#include "MovieSceneSection.h"
#include "EntitySystem/IMovieSceneEntityProvider.h"
#include "MovieSceneAnimationMixerTrack.h"

UCLASS()
class UMyCustomAnimationSection
    : public UMovieSceneSection
    , public IMovieSceneEntityProvider
{
    GENERATED_BODY()

public:
    virtual void ImportEntityImpl(UMovieSceneEntitySystemLinker* EntityLinker,
                                  const FEntityImportParams& Params,
                                  FImportedEntity* OutImportedEntity) override
    {
        using namespace UE::MovieScene;

        // 创建一个混合器条目，包含优先级、权重和目标任务信息
        FMovieSceneAnimMixerEntry MixerEntry;
        MixerEntry.Priority = 1;
        MixerEntry.PoseWeight = 1.0f;
        MixerEntry.bAdditive = false;
        MixerEntry.bRequiresBlend = true;

        // 设置目标任务（此处示例为目标动画蓝图）
        TInstancedStruct<FMovieSceneMixedAnimationTarget> Target;
        FMovieSceneAnimBlueprintTarget ABPTarget;
        ABPTarget.BlueprintNodeName = TEXT("MainBody");
        Target.InitializeAs<FMovieSceneAnimBlueprintTarget>(MoveTemp(ABPTarget));

        // 生成评估任务
        TSharedPtr<FAnimNextEvaluationTask> EvalTask = ...; // 自行创建

        MixerEntry.EvalTask = EvalTask;

        // 通过 FAnimMixerComponentTypes 注册到系统
        const FAnimMixerComponentTypes& ComponentTypes = *FAnimMixerComponentTypes::Get();
        OutImportedEntity->AddComponent(ComponentTypes.Target, Target);
        OutImportedEntity->AddComponent(ComponentTypes.Priority, MixerEntry.Priority);
        OutImportedEntity->AddComponent(ComponentTypes.MixerEntry, MakeShared<FMovieSceneAnimMixerEntry>(MoveTemp(MixerEntry)));
        // ... 添加其他组件
    }
};
```

### 进阶用法

**创建根运动节并设置目的地**：

```cpp
// 根运动节的创建（通常在 UMovieSceneRootMotionSection::ImportEntityImpl 中）
UMovieSceneRootMotionSection* RootMotionSection = ...;
RootMotionSection->RootDestinationChannel.SetDefault(static_cast<uint8>(EMovieSceneRootMotionDestination::Component));

// 通过实体系统附加根运动设置
FMovieSceneRootMotionSettings RootMotionSettings;
RootMotionSettings.RootMotionSpace = EMovieSceneRootMotionSpace::AnimationSpace;
RootMotionSettings.TransformMode = EMovieSceneRootMotionTransformMode::Offset;
// 注册到系统（通过 FAnimMixerComponentTypes::Get().RootMotionSettings）
```

**自定义目标系统**：如果需要扩展混合逻辑，可以继承 `UMovieSceneAnimBlueprintTargetSystem` 或 `UMovieSceneAnimNextTargetSystem`，重写 `OnSchedulePersistentTasks` 方法实现自定义调度。

## Demo 示例

以下是一个最小化的 C++ Actor，展示如何在运行时创建并使用 Anim Mixer 目标系统（假设你在编辑器中有一个骨骼网格体 actor）。

```cpp
// MyAnimMixerActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAnimMixerActor.generated.h"

UCLASS()
class AMyAnimMixerActor : public AActor
{
    GENERATED_BODY()
public:
    AMyAnimMixerActor();

    UPROPERTY(VisibleAnywhere)
    class USkeletalMeshComponent* SkeletalMesh;

    void RegisterMixerTarget();
};
```

```cpp
// MyAnimMixerActor.cpp
#include "MyAnimMixerActor.h"
#include "Systems/MovieSceneAnimBlueprintTargetSystem.h"
#include "AnimMixerComponentTypes.h"
#include "MovieSceneMixedAnimationTarget.h"

AMyAnimMixerActor::AMyAnimMixerActor()
{
    PrimaryActorTick.bCanEverTick = false;
    SkeletalMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkeletalMesh"));
    RootComponent = SkeletalMesh;
}

void AMyAnimMixerActor::RegisterMixerTarget()
{
    // 初始化目标结构（匹配 AnimBP 中的节点名称）
    FMovieSceneAnimBlueprintTarget Target;
    Target.BlueprintNodeName = FAnimNode_SequencerMixerTarget::DefaultTargetName;

    // 通过 FAnimMixerComponentTypes 获取组件类型
    const UE::MovieScene::FAnimMixerComponentTypes& Types = *UE::MovieScene::FAnimMixerComponentTypes::Get();
    // 实际使用中，这些组件会在序列的实体系统中被添加
    // 此处仅演示如何准备目标数据
    TInstancedStruct<FMovieSceneMixedAnimationTarget> TargetInst;
    TargetInst.InitializeAs<FMovieSceneAnimBlueprintTarget>(MoveTemp(Target));
}
```

**注意**：示例仅为概念展示，实际运行时需要结合序列轨道、实体系统和评估管线。你可参考插件源码中的 `MovieSceneAnimationMixerTrack.h` 和 `MovieSceneAnimMixerSystem.cpp` 中的实现。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | 核心序列框架 |
| `MovieSceneTracks` | 标准轨道类型（动画、变换等） |
| `Sequencer` | 编辑器集成和运行时评估 |
| `UAF` | Unreal Animation Framework 基础 |
| `UAFAnimGraph` | UAF 的动画图运行时 |
| `AnimNext` | AnimNext 评估系统 |
| `AnimNextSystem` | AnimNext 实体系统组件类型 |
| `StructUtils` | 结构化类型支持（`TInstancedStruct`） |

其余依赖（Core, Engine, Slate 等）为标准常见依赖，不赘述。

## 维护状态

### 近期更新

- 2025-10-01 `142f8a80` — Sequencer: Partial back out of 42444020 and 42182253 which added UnbindFromSkeletalMeshComponent in
- 2025-09-03 `83133567` — Sequencer: Fix issue where when changing shots we could sometimes get one frame of t-pose
- 2025-09-03 `072d3134` — Sequencer: Minor Stitch Track UX fixes
- 2025-09-02 `78089693` — Add scoped named event for UAF pose evaluation
- 2025-08-20 `8dd5bb75` — Sequencer: Improved property traits variants, added type-erased property values...

### 维护评价

该插件创建于 2025 年 8 月，属于实验性新特性，仍在快速迭代中（最近一个月内有多次功能性提交和 bug 修复）。虽然是实验性插件，但更新频繁，说明 Epic 团队在积极开发。当前版本为 0.1，API 可能随版本变动。推荐在非生产项目中尝鲜使用，生产项目请谨慎评估稳定性。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneAnimMixer)
- [官方文档](https://docs.unrealengine.com/5.7/)（当前无专有文档，可参考 Sequencer 动画混合文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneAnimMixer/Tests)（若存在）