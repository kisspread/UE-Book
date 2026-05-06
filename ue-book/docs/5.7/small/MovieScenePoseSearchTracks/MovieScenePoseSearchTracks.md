# Movie Scene Pose Search Tracks

> Sequencer pose search tracks using the Anim Mixer

| 属性 | 值 |
|---|---|
| 中文名 | 姿态搜索轨道 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（序列器轨道资源/蓝图资源） |
| 模块 | `MovieScenePoseSearchTracks` (Runtime), `MovieScenePoseSearchTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieScenePoseSearchTracks) | |

---

## 用途

此插件为 **Unreal Engine 的 Sequencer** 提供一种特殊的轨道类型 —— **姿态搜索过渡轨道**（`MovieSceneStitchAnimTrack`），用于在动画混合器（Anim Mixer）中实现基于 **PoseSearch 数据库** 的自然动画过渡。

传统动画过渡通常需要手动定义 blend space 或过渡曲线，而此插件通过 **姿态搜索（PoseSearch）** 技术，从数据库中自动匹配最合适的过渡动画片段（stitch animation），从而生成更流畅、更真实的动画混合效果。

核心作用域：
- 将 `UPoseSearchDatabase`（姿态搜索数据库）与 Sequencer 内的动画片段关联
- 自动计算最佳过渡时间、目标姿态和根骨运动
- 支持多行轨道，可同时管理多个过渡段

---

## 使用场景

- **过场动画制作**：当角色从一个动作切换到另一个动作时，利用姿态搜索数据库生成自然过渡，避免硬切或不自然的 blend。
- **游戏内动画序列**：在 Sequencer 中驱动角色动画，需要根据上下文（如行走→奔跑、站立→跳跃）动态选择最优过渡。
- **Rig 与混合空间替代**：对于需要大量实际数据的复杂过渡，姿态搜索比手动调节混合空间更高效。

---

## 蓝图用法

此插件 **未暴露任何 BlueprintCallable 函数**。所有功能在 Sequencer 编辑器界面上通过拖拽轨道和设置参数完成。

**在 Sequencer 中使用步骤**：
1. 确保已启用插件并重启编辑器。
2. 在 Sequencer 中为动画骨骼添加一条 **“Stitch Anim Track”**（姿态搜索轨道）。
3. 在轨道的 Section 属性中指定一个 `UPoseSearchDatabase` 资源和目标动画资产。
4. 调节 Section 的时间范围和根骨空间等参数，播放预览过渡效果。

> 注意：由于插件仍处于实验阶段，部分编辑器界面可能位于 `MovieScenePoseSearchTracksEditor` 模块中，需要在编辑器模式下工作。

---

## C++ 用法

### 头文件引入

```cpp
#include "Tracks/MovieSceneStitchAnimTrack.h"
#include "PoseSearchDatabase.h"            // 来自 UAFPoseSearch 模块
#include "Sections/MovieSceneStitchAnimSection.h"
```

### 基本用法

创建一个姿态搜索轨道并添加一个动画 Section（基于源码 `UMovieSceneStitchAnimTrack::AddNewAnimationOnRow`）：

```cpp
// 假设你已有一个 UMovieSceneSequence* Sequence 及对应的 UMovieScene* MovieScene
UMovieScene* MovieScene = Sequence->GetMovieScene();

// 创建轨道
UMovieSceneStitchAnimTrack* StitchTrack = NewObject<UMovieSceneStitchAnimTrack>(MovieScene);
MovieScene->AddTrack(StitchTrack);  // 需自行实现添加逻辑

// 准备姿态搜索数据库和关键帧时间
UPoseSearchDatabase* PoseSearchDB = LoadObject<UPoseSearchDatabase>(nullptr, TEXT("/Game/MyDatabase.MyDatabase"));
FFrameNumber StartTime(0);

// 在第0行添加 Section
UMovieSceneSection* NewSection = StitchTrack->AddNewAnimationOnRow(StartTime, PoseSearchDB, 0);

// 设置 Section 的附加属性（例如目标动画资产）通过继承的 FMovieSceneStitchAnimComponentData
if (UMovieSceneStitchAnimSection* StitchSection = Cast<UMovieSceneStitchAnimSection>(NewSection))
{
    // 直接修改 UPROPERTY（需要 Section 内部有对应的成员）
    // 注意：以下属性可能需要在 UMovieSceneStitchAnimSection 中公开
    // FMovieSceneStitchAnimComponentData& CompData = StitchSection->StitchData;
    // CompData.TargetPoseAsset = ...;
    // CompData.TargetAnimationTimeSeconds = ...;
}
```

> 实际开发中，`AddNewAnimationOnRow` 会返回一个已经初始化好的 Section，并自动创建 MotionMatching 所需的组件数据。

### 进阶用法

结合 Anim Mixer 和 Evaluation Task 的流程（基于 `UMovieSceneStitchAnimSystem`）：

```cpp
// 在自定义动画系统或游戏模块中，你可以订阅 OnPreAnimated 等事件
// 但插件内部通过 Entity System 自动调度任务，无需用户手动触发

// 示例：从 Section 中获取运动匹配专用数据结构
FMovieSceneStitchAnimComponentData Data;
Data.StitchDatabase = PoseSearchDB;
Data.StartFrame = StartTime;
Data.EndFrame = EndTime;
// ... 设置其他字段
```

该数据结构被用于 `FMovieSceneStitchAnimEvaluationTask` 在执行 `Execute` 时驱动实际过渡。

---

## Demo 示例

以下为一个完整的最小示例，演示在运行时（或编辑器工具）向现有 Sequence 添加姿态搜索轨道。

### StitchTrackDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MovieSceneSequencePlayer.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "StitchTrackDemo.generated.h"

UCLASS()
class UStitchTrackDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void AddStitchTrackToSequence(UMovieSceneSequence* InSequence, UPoseSearchDatabase* InDatabase);
};
```

### StitchTrackDemo.cpp

```cpp
#include "StitchTrackDemo.h"
#include "Tracks/MovieSceneStitchAnimTrack.h"
#include "PoseSearchDatabase.h"

void UStitchTrackDemoSubsystem::AddStitchTrackToSequence(UMovieSceneSequence* InSequence, UPoseSearchDatabase* InDatabase)
{
    if (!InSequence || !InDatabase)
    {
        return;
    }

    UMovieScene* MovieScene = InSequence->GetMovieScene();
    if (!MovieScene)
    {
        return;
    }

    // 创建姿态搜索轨道
    UMovieSceneStitchAnimTrack* NewTrack = NewObject<UMovieSceneStitchAnimTrack>(MovieScene, NAME_None, RF_Transactional);
    if (!NewTrack)
    {
        return;
    }

    // 将轨道添加到 MovieScene（并选择绑定的对象绑定 ID）
    FGuid ObjectBinding = MovieScene->AddPossessable(InSequence->GetName(), nullptr); // 简化，实际应绑定动画骨架
    NewTrack->SetObjectBindingID(ObjectBinding);
    MovieScene->AddTrack(NewTrack);

    // 在第0帧添加一个 Section
    FFrameNumber StartTime(0);
    int32 RowIndex = 0;
    UMovieSceneSection* Section = NewTrack->AddNewAnimationOnRow(StartTime, InDatabase, RowIndex);
    if (Section)
    {
        // 设置 Section 的持续时间（例如 2 秒）
        FFrameRate FrameRate = MovieScene->GetTickResolution();
        Section->SetEndTime(StartTime + (FrameRate.AsFrameNumber(2.0)));
    }

    // 通知 Sequencer 刷新
    if (GEditor)
    {
        GEditor->GetTimerManager()->SetTimerForNextTick([MovieScene]()
        {
            MovieScene->MarkAsChanged();
        });
    }
}
```

> 此示例需要 `MovieScene`, `MovieSceneSequence`, `PoseSearchDatabase` 等模块及 `Editor` 宏进行构建。实际项目中建议放入 `Editor` 模块或使用 `DeveloperTool` 模式。

---

## 模块依赖

使用时，你的模块 `.Build.cs` 中需添加以下依赖（除标准依赖外）：

| 模块 | 用途 |
|---|---|
| `MovieSceneAnimMixer` | 提供 Anim Mixer 轨道基础框架与评估任务 |
| `UAFPoseSearch` | 提供姿态搜索数据库 `UPoseSearchDatabase` 及其核心算法 |

> 无需额外依赖常见模块（Core, Engine, MovieScene 等）。

---

## 维护状态

### 近期更新

| 日期 | Hash | Commit 信息 |
|---|---|---|
| 2025-09-03 | 072d3134 | Sequencer: Minor Stitch Track UX fixes. |
| 2025-07-31 | bdedc2af | PoseSearch - support for PSD search returning multiple results |
| 2025-07-24 | 4d8395fa | PoseSearch - deprecating pose search database TArray\<FInstancedStruct\> AnimationAssets in favor of T... |
| 2025-06-27 | ee0441e9 | UAF: Rename/move plugins |
| 2025-06-26 | effdabd2 | UAF: Moved/renamed AnimNext and AnimNextAnimGraph plugins |

### 维护评价

- **创建时间**：2025-06-26，距今约 3 个月。
- **活跃度**：近 3 个月内有多次提交，包括 UX 修复和依赖更新，属于 **活跃开发** 中。
- **质量**：插件显式标记为 `Experimental`，版本号 0.1，API 可能随时变动。
- **稳定性**：未观察到废弃标记，但缺少正式文档，仅适合试验性项目或开发期使用。
- **推荐**：如果你的项目需要基于 PoseSearch 的序列器过渡动画，且能接受实验性质，可以试用。不建议用于交付级别的内容。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieScenePoseSearchTracks)
- 官方文档：无（实验性插件）
- 测试用例：未在插件目录中找到，可参考 `Engine/Plugins/Experimental/UAFPoseSearch/Tests` 中的 PoseSearch 单元测试以了解数据库使用方式。