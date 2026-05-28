# Movie Scene Pose Search Tracks

> Sequencer pose search tracks using the Anim Mixer

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer 姿态搜索轨道 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MovieScenePoseSearchTracks` (Runtime), `MovieScenePoseSearchTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieScenePoseSearchTracks) | |

## 用途

此插件用于在 **Sequencer** 中实现 **无缝动画过渡**。它通过 **Motion Matching (运动匹配)** 技术，在预设的动画数据库 (`PoseSearchDatabase`) 中查找一个最合适的动画片段，将角色当前的动画状态（姿态、轨迹历史）与目标动画姿态平滑连接，并支持带动画蓝图根运动播放。

**核心解决的问题**：在过场动画中，角色通常需要从游戏玩法（Gameplay）中的实时状态过渡到预设的动画序列。传统方法可能需要手动调整动画起始点来避免跳跃或滑步。此插件通过自动化方式查找连接动画，使过渡更自然、无缝，特别适用于从游戏玩法过渡到过场动画（Cutscene）的场景。

## 使用场景

- 你在制作过场动画，需要角色从一个游戏中的待机状态**无缝过渡**到一个预录的对话动画。
- 你需要为一段过场动画创建一个**动态的动画连接**，而不是使用固定的过渡动画剪辑。
- 你希望利用 **Motion Matching** 的技术优势，在 Sequencer 中实现更智能、更真实的动画混合。

## 蓝图用法

该插件主要通过 Sequencer 编辑器中的 UI 进行操作，而非传统的蓝图节点调用。其核心资产和属性在 Sequencer 编辑器中配置。

### 核心资产与属性

在 Sequencer 中为角色添加“Animation Stitch”轨道后，每个“Stitch”片段（Section）都包含以下可在蓝图编辑器中配置的属性：

| 属性 | 说明 | 所在类 |
|---|---|---|
| `StitchDatabase` | 用于 Motion Matching 搜索的动画数据库 (PoseSearchDatabase) 资产。 | `UMovieSceneStitchAnimSection` |
| `TargetPoseAsset` | 目标动画资产（如对话动画）。Motion Matching 将寻找连接当前状态到此资产特定时间点的动画。 | `UMovieSceneStitchAnimSection` |
| `TargetAnimationTimeSeconds` | 目标动画中要连接到的具体时间点（秒）。 | `UMovieSceneStitchAnimSection` |
| `TargetTransform` | 连接点的目标世界变换（位置、旋转）。 | `UMovieSceneStitchAnimSection` |
| `bAuthoritativeRootMotion` | 是否使用匹配到的动画中的根运动数据。 | `UMovieSceneStitchAnimSection` |

### 使用示例（蓝图描述）

在 Sequencer 编辑器中操作：
1.  为你的角色 Actor 添加一个 “Animation Stitch” 轨道。
2.  在时间轴上创建一个新的“Stitch”片段。
3.  在细节面板中，将你的 `PoseSearchDatabase` 资产拖拽到 `StitchDatabase` 属性上。
4.  将你的目标动画（如 “DialogueAnim”）拖拽到 `TargetPoseAsset` 属性。
5.  调整 `TargetAnimationTimeSeconds` 来选择对话动画的起始时刻。
6.  （可选）在视口中调整 `TargetTransform`，将角色最终放置到正确位置。
7.  播放 Sequencer。当片段激活时，插件会自动在数据库中搜索并播放过渡动画。

## C++ 用法

### 头文件引入

```cpp
#include "Sections/MovieSceneStitchAnimSection.h"
#include "Tracks/MovieSceneStitchAnimTrack.h"
```

### 基本用法

在 C++ 中，你可以动态创建和配置 “Stitch” 轨道与片段。这通常在编写 Sequencer 的扩展或自动生成脚本时使用。
（示例来源：基于 `MovieSceneStitchAnimTrack.h` 中 `AddNewAnimationOnRow` 函数的用法推断）

```cpp
// 获取或创建 Sequencer 的 MovieScene 对象
UMovieScene* MovieScene = /* ... */;

// 创建 Stitch 动画轨道
UMovieSceneStitchAnimTrack* StitchTrack = NewObject<UMovieSceneStitchAnimTrack>(MovieScene);
MovieScene->AddMasterTrack(StitchTrack);

// 在特定帧创建一个新的动画片段
FFrameNumber StartTime = /* ... */;
UPoseSearchDatabase* MyDatabase = /* ... */;
UMovieSceneSection* NewSection = StitchTrack->AddNewAnimationOnRow(StartTime, MyDatabase, 0 /* RowIndex */);

// 进一步配置片段（如果获得的是 UMovieSceneStitchAnimSection）
if (UMovieSceneStitchAnimSection* StitchSection = Cast<UMovieSceneStitchAnimSection>(NewSection))
{
    StitchSection->TargetPoseAsset = MyTargetAnimation;
    StitchSection->TargetAnimationTimeSeconds = 2.0f;
    StitchSection->bAuthoritativeRootMotion = true;
    // ... 设置其他属性
}
```

### 进阶用法

插件的核心逻辑在于 `UMovieSceneStitchAnimEvaluationTask`。这是一个评估任务，当 Sequencer 片段激活时被调度执行。其 `Execute` 方法是运动匹配计算的入口点。开发者可以继承或修改此任务以实现自定义的过渡逻辑，但这属于深度引擎开发范畴。

```cpp
// 核心执行逻辑框架 (概念性，源自 MovieSceneStitchAnimSection.h)
void FMovieSceneStitchAnimEvaluationTask::Execute(UE::UAF::FEvaluationVM& VM) const
{
    // 1. 检查是否需要运行 Motion Matching 计算（例如，首次评估时）
    if (ShouldRunMotionMatching())
    {
        // 2. 使用 StitchData.StitchDatabase 和当前角色状态（来自 VM）进行搜索
        // 3. 找到最佳匹配的动画和时间点，存储到 MatchedAsset 和 MatchedAssetTime
        FindBestMatch(VM);
    }

    // 4. 根据当前时间（CurrentTime）、匹配到的动画和时间点，计算动画混合权重并输出到 VM
    EvaluateMatchedAnimation(VM);
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何在代码中创建一个 “Animation Stitch” 轨道。

```cpp
// MySequencerScript.h
#pragma once
#include "CoreMinimal.h"
#include "MovieScene.h"

class UMovieSceneStitchAnimTrack;

class FMySequencerScript
{
public:
    static UMovieSceneStitchAnimTrack* CreateStitchTrackInSequence(UMovieScene* InMovieScene);
};
```

```cpp
// MySequencerScript.cpp
#include "MySequencerScript.h"
#include "Tracks/MovieSceneStitchAnimTrack.h"

UMovieSceneStitchAnimTrack* FMySequencerScript::CreateStitchTrackInSequence(UMovieScene* InMovieScene)
{
    if (!InMovieScene)
    {
        return nullptr;
    }

    // 创建轨道对象
    UMovieSceneStitchAnimTrack* StitchTrack = NewObject<UMovieSceneStitchAnimTrack>(InMovieScene, NAME_None, RF_Transactional);

    // 将轨道添加到序列（作为主轨道）
    InMovieScene->AddMasterTrack(StitchTrack);

    // 创建一个初始片段（可选）
    StitchTrack->CreateNewSection();

    return StitchTrack;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieSceneAnimMixer` | 动画混合器核心，提供 Sequencer 中动画混合的基础架构。 |
| `PoseSearch` | 姿态搜索（Motion Matching）运行时，用于执行动画数据库搜索。 |
| `AnimNextRuntime` | 提供评估任务（`FAnimNextEvaluationTask`）基类和动画求值框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `68f769e6` | Sequencer: Stitch track section was defaulting weight to 0 | 修复 Stitch 片段权重默认为 0 的 Bug，确保动画能正常播放。 |
| 2026-05-22 | `2ad26ca4` | Sequencer: Anim Mixer: Stitch section root motion fix for offset-mesh actors | 修复针对网格原点偏移的角色，根运动应用不正确的问题。 |
| 2026-04-17 | `8bcded9c` | Sequencer: Per Anim Track and Row Iconography | 为动画轨道和行添加了图标，提升 Sequencer 编辑器的视觉辨识度。 |
| 2026-04-07 | `6ab9300d` | Sequencer: Fix default AddSection path for Animation Mixer to properly assign sections to layers | 修复通过代码添加片段时，未能正确分配到混合层的问题。 |
| 2026-04-07 | `8bf4fb4b` | Sequencer: Restructure mixer evaluation around layers; new mask blend system | 重构混合器评估层结构并引入新的遮罩混合系统。 |

### 维护评价

**活跃维护**。该插件作为实验性功能，正处于积极开发和调试阶段。从近期（2026年4月-5月）的更新记录看，维护非常活跃，主要集中在**修复关键功能缺陷**（如权重、根运动）和**提升编辑器体验**。尽管标记为实验性 (`IsExperimentalVersion=true`)，但其依赖的 `PoseSearch` 和 `AnimMixer` 是 Epic 重点推进的动画技术方向。目前不建议在生产环境中直接使用，但非常适合用于原型开发和技术预研。预计随着核心模块成熟，此插件也将逐步稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieScenePoseSearchTracks)
- [官方文档]() (暂无)
- [测试用例]() (源码分析中未发现独立测试用例)