# Media Compositing

> Actors, components and Sequencer extensions for compositing media

| 属性 | 值 |
|---|---|
| 中文名 | 媒体合成 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Sequencer 轨道、片段资源） |
| 模块 | `MediaCompositing` (Runtime), `MediaCompositingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaCompositing) | |

## 用途

Media Compositing 插件为 Unreal Engine 的 Sequencer 提供了完整的媒体合成扩展。它允许你在 Sequencer 中添加媒体片段（如视频、图像序列），并控制其播放行为（循环、偏移、帧对齐等）。该插件解决了以下问题：

- **直接播放媒体**：无需手动创建 MediaPlayer / MediaTexture，即可将视频源拖入 Sequencer 轨道。
- **属性轨道播放**：支持在 MediaPlayer 属性轨道上直接播放媒体，简化动画录制流程。
- **播放器复用与优先级**：当多个媒体片段重叠时，自动管理 MediaPlayer 的分配与优先级，避免冲突。
- **帧精度控制**：提供帧对齐、手动帧率覆盖等高级选项，确保媒体与 CG 渲染同步。
- **代理对象支持**：可通过 MediaPlate 等代理对象访问纹理，实现分层合成与混合。

该插件是构建基于时间线的媒体合成工作流的核心组件，广泛应用于过场动画、虚拟制片、交互式媒体展示。

## 使用场景

- **创建电影级过场动画**：在 Sequencer 中混合 CG 内容与实拍视频，控制播放与混合。
- **虚拟制片**：在实时场景中回放视频背景，与摄像机运动同步。
- **交互式媒体播放器**：在 UI 或 3D 世界中嵌入视频，并由时间线控制播放进度。
- **动画录制**：将 MediaPlayer 属性绑定到动画轨道，实现自动录制/播放。

## 蓝图用法

Media Compositing 提供的核心 Sequencer 类可通过蓝图进行编辑（主要在细节面板），但 **没有公开的蓝图可调用函数**。所有交互均通过 Sequencer 编辑器完成。

### 核心片段属性

以下属性可在 `UMovieSceneMediaSection` 的细节面板中编辑（所有属性均为 `BlueprintReadWrite`）：

| 属性 | 类型 | 说明 |
|---|---|---|
| `MediaSource` | `UMediaSource*` | 要播放的媒体源（直接指定） |
| `MediaSourceProxyIndex` | `int32` | 当使用 MediaSourceProxy 时的索引 |
| `bLooping` | `bool` | 是否循环播放。仅影响内部缓存，不延长片段超出结束时间 |
| `StartFrameOffset` | `FFrameNumber` | 从媒体源的指定帧开始播放 |
| `MediaTexture` | `UMediaTexture*` | 接收视频输出的纹理 |
| `MediaSoundComponent` | `UMediaSoundComponent*` | 接收音频的声音组件 |
| `bUseExternalMediaPlayer` | `bool` | 是否使用外部已有的 MediaPlayer |
| `ExternalMediaPlayer` | `UMediaPlayer*` | 外部 MediaPlayer 引用 |
| `CacheSettings` | `FMediaSourceCacheSettings` | 缓存设置（仅在无代理时有效） |
| `TextureIndex` | `int32` | 代理对象中的纹理索引（用于交叉淡化） |
| `bManualFrameRateAlignment` | `bool` | 是否手动指定帧率对齐 |
| `FrameRateAlignment` | `FFrameRate` | 内部帧对齐使用的帧率 |

### 轨道属性

`UMovieSceneMediaTrack` 提供以下编辑属性：

| 属性 | 类型 | 说明 |
|---|---|---|
| `bSynchronousScrubbing` | `bool` | 在编辑器中手动擦除时强制同步帧请求，牺牲性能换取对齐 |

### 使用示例（蓝图描述）

在 Sequencer 中添加媒体轨道：

1. 在 Sequencer 面板中点击“添加轨道”，选择“Media Track”。
2. 右键媒体轨道，添加一个媒体片段。
3. 在片段细节面板中：
   - **Media Source**：选择一个已创建的 `MediaSource` 资产（如 `FileMediaSource`、`ImgMediaSource`）。
   - **Media Texture**：指定一个 `MediaTexture` 资产（通常提前创建）。
   - **Media Sound Component**：可选择对应的 `UMediaSoundComponent` 播放音频。
4. 调整片段的开始/结束时间，设置 `Looping`、`StartFrameOffset` 等参数。
5. 如果使用外部 MediaPlayer，勾选 `bUseExternalMediaPlayer` 并引用它。
6. 运行 Sequence，媒体将按配置播放。

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneMediaSection.h"
#include "MovieSceneMediaTrack.h"
#include "MovieSceneMediaData.h"
```

### 基本用法

#### 创建媒体轨道并添加片段

```cpp
// 获取 MovieScene
UMovieScene* MovieScene = ...;

// 创建媒体轨道
UMovieSceneMediaTrack* MediaTrack = MovieScene->AddTrack<UMovieSceneMediaTrack>(ObjectBinding);

// 创建媒体源资产
UMediaSource* MediaSource = NewObject<UMediaSource>(GetTransientPackage(), ...);

// 添加新片段到轨道
FFrameNumber StartTime(0);
UMovieSceneSection* NewSection = MediaTrack->AddNewMediaSource(*MediaSource, StartTime);
```

#### 使用代理源添加片段

```cpp
FMovieSceneObjectBindingID ObjectBinding = ...;
UMovieSceneSection* Section = MediaTrack->AddNewMediaSourceProxy(MediaSource, ObjectBinding, 0, StartTime);
```

#### 访问媒体播放器数据

```cpp
// 在 Evaluate 上下文中获取持久数据
FMovieSceneMediaData* MediaData = PersistentData.FindSectionData<FMovieSceneMediaData>();
if (MediaData)
{
    UMediaPlayer* Player = MediaData->GetMediaPlayer();
    if (Player)
    {
        // 控制播放器...
    }
}
```

### 进阶用法

#### 设置媒体片段属性（C++ 代码创建）

```cpp
UMovieSceneMediaSection* MediaSection = Cast<UMovieSceneMediaSection>(NewSection);
if (MediaSection)
{
    MediaSection->MediaSource = MyMediaSource;
    MediaSection->MediaTexture = MyMediaTexture;
    MediaSection->MediaSoundComponent = MySoundComponent;
    MediaSection->bLooping = true;
    MediaSection->StartFrameOffset = FFrameNumber(10);
    MediaSection->bUseExternalMediaPlayer = false;
}
```

#### 自定义媒体播放器复用策略

`FMovieSceneMediaPlayerStore` 负责管理播放器的复用。你可以实现自定义存储逻辑，但通常使用默认行为即可。

```cpp
// 获取 MediaPlayerStore（通常由 System 自动管理）
TSharedPtr<FMovieSceneMediaPlayerStore> PlayerStore = ...;

// 手动调度播放器释放（很少需要手动调用）
PlayerStore->ScheduleMediaPlayerForRelease(FObjectKey(Section), MyMediaPlayer);

// 尝试获取复用播放器
UMediaPlayer* ReusedPlayer = PlayerStore->TryAcquireMediaPlayer(FObjectKey(Section));
```

#### 调整播放时间范围

```cpp
using namespace UE::MovieSceneMediaPlayerUtils;

TRange<FTimespan> SectionRange(FTimespan::FromSeconds(0), FTimespan::FromSeconds(10));
TRange<FTimespan> AdjustedRange = AdjustPlaybackTimeRange(SectionRange, MediaPlayer, FrameDuration);
SetPlayerPlaybackTimeRange(MediaPlayer, AdjustedRange);
```

#### 属性轨道媒体播放

```cpp
// 创建 MediaPlayer 属性轨道
UMovieSceneMediaPlayerPropertyTrack* PropertyTrack = ...;
UMovieSceneMediaPlayerPropertySection* PropSection = Cast<UMovieSceneMediaPlayerPropertySection>(PropertyTrack->CreateNewSection());
PropSection->MediaSource = MyMediaSource;
PropSection->bLoop = true;
PropertyTrack->AddSection(*PropSection);
```

## Demo 示例

以下是一个完整的 C++ 示例，展示如何在运行时使用 Sequencer 播放媒体片段（假设已有 `UMediaSource` 资产）。

### MyMediaActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LevelSequence.h"
#include "MyMediaActor.generated.h"

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaActor();

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaSource* MediaSource;

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaSoundComponent* MediaSoundComponent;

    UFUNCTION(BlueprintCallable, Category = "Sequencer")
    void PlayMediaSequence();

private:
    UPROPERTY()
    ULevelSequence* TempSequence;
};
```

### MyMediaActor.cpp

```cpp
#include "MyMediaActor.h"
#include "MovieScene.h"
#include "MovieSceneMediaTrack.h"
#include "MovieSceneMediaSection.h"
#include "LevelSequenceActor.h"
#include "LevelSequencePlayer.h"

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMediaActor::PlayMediaSequence()
{
    if (!MediaSource || !MediaTexture) return;

    // 创建一个临时 Sequence
    TempSequence = NewObject<ULevelSequence>(GetTransientPackage(), "TempMediaSeq");
    TempSequence->Initialize();
    UMovieScene* MovieScene = TempSequence->MovieScene;
    MovieScene->SetEvaluationType(EMovieSceneEvaluationType::WithSubFrames);

    // 添加绑定到无对象（不需要绑定具体 Actor）
    FGuid ObjectBinding = MovieScene->AddPossessable("MediaDummy", UObject::StaticClass());

    // 创建媒体轨道
    UMovieSceneMediaTrack* MediaTrack = MovieScene->AddTrack<UMovieSceneMediaTrack>(ObjectBinding);
    UMovieSceneMediaSection* MediaSection = Cast<UMovieSceneMediaSection>(MediaTrack->CreateNewSection());
    if (MediaSection)
    {
        MediaSection->MediaSource = MediaSource;
        MediaSection->MediaTexture = MediaTexture;
        MediaSection->MediaSoundComponent = MediaSoundComponent;
        MediaSection->bLooping = false;
        MediaSection->SetRange(TRange<FFrameNumber>(0, 300)); // 10 秒 @30fps
        MediaTrack->AddSection(*MediaSection);
    }

    // 播放 Sequence
    ALevelSequenceActor* SequenceActor;
    ULevelSequencePlayer* Player = ULevelSequencePlayer::CreateLevelSequencePlayer(
        GetWorld(),
        TempSequence,
        FMovieSceneSequencePlaybackSettings(),
        SequenceActor
    );
    if (Player)
    {
        Player->Play();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 提供编辑器相关基础设施（尽管是 Runtime 模块，仍依赖该模块） |

注意：MediaCompositing 模块本身依赖 `UnrealEd`，可能用于某些编辑器功能。使用本插件时，你的模块需要添加 `"MediaCompositing"` 到 `PublicDependencyModuleNames`。如果仅使用运行时播放，无需额外依赖。

## 维护状态

### 近期更新

- 2025-10-16 `45eb317d` — [MediaCompositing] Sequencer Media Track: Fix crash on exit when running a sequencer in game mode.
- 2025-10-08 `c039eab2` — [MediaCompositing] Sequencer Media Track: Revisiting the frame alignment for frame accuracy.
- 2025-10-03 `1d7d0e17` — [MediaCompositing] Frame Accuracy Fix
- 2025-09-29 `63374779` — [Media Track] Fixing inconsistent behavior - take 2.
- 2025-09-24 `689c7036` — [Media Track] Fix "missing media texture" message mistakenly appearing on sections under a media pla

### 维护评价

- **创建时间**：2025-09-24（约 1 年前）
- **更新频率**：近期频繁更新，平均每 1-2 周有修复或改进
- **活跃程度**：目前处于**活跃维护**状态，持续修复崩溃、帧精度和不一致性问题
- **已知问题**：已修复了退出游戏模式时的崩溃和帧对齐问题，稳定性逐步提升
- **推荐使用**：✅ 推荐用于需要媒体合成的 Sequencer 工作流，尤其在虚拟制片和过场动画场景下表现出色。作为较新的插件，API 可能仍有微调，但核心功能已稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaCompositing)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/media-compositing-in-unreal-engine/)（推测路径，实际可能需确认）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaCompositing/Source/MediaCompositing/Private)（私有头文件含核心逻辑）