# Media Compositing

> Actors, components and Sequencer extensions for compositing media（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 媒体合成 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器UI、录制功能） |
| 模块 | `MediaCompositing` (Runtime), `MediaCompositingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaCompositing) | |

## 用途

MediaCompositing 插件的核心功能是扩展 Unreal Engine 的 **Sequencer** 系统，使其能够精确地控制和编辑媒体内容（视频、音频等）的播放与合成。它不是一个独立的媒体播放器，而是将媒体资产深度集成到 Sequencer 的动画时间线中。

**解决的问题**：在游戏或应用的过场动画、虚拟制作或建筑可视化中，经常需要将预先录制好的视频（如背景视频、角色动画、UI 动画）与场景中的其他动画（如摄像机运动、物体变换、灯光变化）进行精准的逐帧同步。原生 Sequencer 主要专注于控制 Actor 和组件的属性动画，对媒体播放的控制能力有限。

**存在原因**：MediaCompositing 插件填补了这一空白，提供了专门的媒体轨道（Media Track）和区段（Section），允许用户在 Sequencer 时间线上像编辑动画关键帧一样编辑媒体的开始时间、结束时间、播放速率、循环设置等。它还提供了丰富的编辑器 UI（如媒体缩略图预览、缓存状态可视化）和工具（如媒体事件录制），极大地提升了在 Sequencer 中进行媒体合成的工作流效率和可控性。

## 使用场景

- **过场动画制作**：你需要将一段预先渲染好的角色对话视频，精确地与场景中角色的口型动画、摄像机切换以及背景音乐对齐。使用 MediaCompositing 插件，你可以在 Sequencer 中直接控制视频的播放时间轴。
- **虚拟制作（Virtual Production）**：在 LED 墙虚拟拍摄现场，你需要实时预览并将虚拟场景中的媒体背景与演员表演在时间线上同步。
- **建筑/产品可视化**：你需要制作一个带有视频背景（如流动的云、变化的光线）的产品展示动画，并确保视频内容与摄像机运动完美契合。
- **复杂的媒体事件序列**：你需要编排一系列媒体事件（如启动视频A、在特定时间点触发字幕、切换到视频B），并可能希望将这个编排过程录制下来以便重用或编辑。

## 蓝图用法

该插件的蓝图功能主要通过 Sequencer 的 UI 和媒体相关资产暴露，直接在蓝图中调用节点较少。其核心价值体现在 Sequencer 编辑器中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShowMediaTexturePrompt` | 当媒体区段缺少 Media Texture 资产时，弹出创建/选择提示框。 | `FMovieSceneMediaSectionHelpers` (UE::MediaCompositingEditor::Private) |
| `FMediaTrackEditor::OnBuildOutlinerEditWidget` | 静态事件委托，可用于自定义 Sequencer 大纲中媒体轨道的编辑小部件。 | `FMediaTrackEditor` |

### 使用示例（蓝图描述）

1.  **在 Sequencer 中添加媒体轨道**：在 Sequencer 编辑器中，为需要播放媒体的 Actor（如 `MediaPlate` Actor）添加一个 “Media Track”。
2.  **拖入媒体资产**：从内容浏览器直接将媒体文件（如 `.mp4`, `.exr` 序列）拖放到该媒体轨道的时间线上，插件会自动创建对应的媒体区段。
3.  **编辑媒体区段**：选中时间线上的媒体区段，可以在细节面板中调整其属性，如开始偏移、播放速率、循环等。插件会自动在 Sequencer 的缩略图区显示视频帧预览。
4.  **播放与预览**：使用 Sequencer 的播放控件，时间线、媒体内容以及其他动画（摄像机、变换等）将同步播放，实现所见即所得的合成效果。

## C++ 用法

### 头文件引入

```cpp
// 核心 Sequencer 和媒体合成相关头文件
#include "Sequencer/MediaTrackEditor.h"
#include "Sequencer/MediaThumbnailSection.h"
#include "MovieSceneMediaSection.h"
```

### 基本用法

以下代码演示了如何在 C++ 中程序化地创建媒体轨道和区段，并将其与 `MediaPlayer` 关联。
（来源：基于 `FMediaTrackEditor` 和 `UMovieSceneMediaSection` 的接口分析）

```cpp
// 假设你已经拥有一个有效的 ISequencer 实例 (TSharedPtr<ISequencer> Sequencer)
// 和一个指向目标 MovieScene 的指针 (UMovieScene* MyMovieScene)

// 1. 创建媒体轨道编辑器实例
TSharedPtr<FMediaTrackEditor> MediaTrackEditor = MakeShared<FMediaTrackEditor>(Sequencer.ToSharedRef());

// 2. 获取或创建一个媒体轨道
// 注意：通常轨道的创建由 Sequencer 自动处理，这里演示如何操作 UMovieSceneMediaTrack
UMovieSceneMediaTrack* MediaTrack = MyMovieScene->AddTrack<UMovieSceneMediaTrack>();
if (MediaTrack)
{
    // 3. 创建一个新的媒体区段
    UMovieSceneMediaSection* MediaSection = Cast<UMovieSceneMediaSection>(MediaTrack->CreateNewSection());
    if (MediaSection)
    {
        // 4. 设置区段时间范围（例如，从第0帧到第150帧）
        MediaSection->SetRange(TRange<FFrameNumber>(0, 150));
        
        // 5. 将媒体源资产链接到区段（需要事先拥有一个有效的 UMediaSource* Asset）
        MediaSection->SetMediaSource(YourMediaSourceAsset);
        
        // 6. 将区段添加到轨道
        MediaTrack->AddSection(*MediaSection);
        
        // 7. 可以进一步设置属性，如播放速率
        // MediaSection->SetPlaybackRate(1.0f);
    }
}
```

### 进阶用法

结合 `FMediaThumbnailSection` 来自定义 Sequencer 中媒体轨道的缩略图显示行为。
（来源：`FMediaThumbnailSection.h` 接口分析）

```cpp
// 假设你正在实现一个自定义的媒体区段视图，并想集成官方的媒体缩略图功能
// 在你自定义的 Sequencer Section 类中，可以创建一个 FMediaThumbnailSection 来管理缩略图

// 在你的 Section 类的成员中
TSharedPtr<FMediaThumbnailSection> MediaThumbnailSection;

// 在 Section 初始化时（例如在 MakeSectionInterface 的实现中）
void FMyCustomMediaSection::Initialize(...)
{
    // ...其他初始化...
    
    // 创建媒体缩略图区段实例
    MediaThumbnailSection = MakeShared<FMediaThumbnailSection>(
        *MovieSceneMediaSection, // UMovieSceneMediaSection&
        Sequencer->GetThumbnailPool(), // TSharedPtr<FTrackEditorThumbnailPool>
        Sequencer // TSharedPtr<ISequencer>
    );
}

// 在 Section 的 Tick 或 Paint 方法中，需要更新和绘制缩略图
void FMyCustomMediaSection::Tick(...)
{
    if (MediaThumbnailSection.IsValid())
    {
        MediaThumbnailSection->Tick(...); // 传递参数
    }
}

int32 FMyCustomMediaSection::OnPaintSection(...) const
{
    // 先调用父类或其他绘制逻辑
    int32 LayerId = ...;
    
    if (MediaThumbnailSection.IsValid())
    {
        // 让媒体缩略图区段绘制其内容（视频帧、缓存状态、警告等）
        LayerId = MediaThumbnailSection->OnPaintSection(InPainter);
    }
    
    return LayerId;
}
```

## Demo 示例

一个最小的、展示如何将媒体内容集成到 Sequencer 的 C++ 示例。
（注：此示例侧重于 Sequencer 侧，媒体播放器的实际设置需参照 MediaAssets 模块。）

```cpp
// MyMediaSequenceBuilder.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MovieSceneMediaSection.h" // 包含媒体区段头文件

class UMediaPlayer;
class UMediaSource;
class UMediaTexture;
class ULevelSequence;
class UMovieSceneMediaTrack;

UCLASS()
class UMyMediaSequenceBuilder : public UObject
{
    GENERATED_BODY()

public:
    /**
     * 在指定的关卡序列中创建一个简单的媒体动画段。
     * @param LevelSequence 要编辑的关卡序列资产。
     * @param MediaSource 要播放的媒体源资产。
     * @param MediaTexture 用于接收视频帧的媒体纹理资产。
     * @param StartFrame 动画的起始帧号。
     * @param EndFrame 动画的结束帧号。
     */
    UFUNCTION(BlueprintCallable, Category = "Media|Sequence")
    bool CreateMediaSequenceSegment(
        ULevelSequence* LevelSequence,
        UMediaSource* MediaSource,
        UMediaTexture* MediaTexture,
        int32 StartFrame = 0,
        int32 EndFrame = 150);
};
```

```cpp
// MyMediaSequenceBuilder.cpp
#include "MyMediaSequenceBuilder.h"
#include "LevelSequence.h"
#include "MovieScene.h"
#include "MovieSceneMediaTrack.h"
#include "MovieSceneMediaSection.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MediaTexture.h"

bool UMyMediaSequenceBuilder::CreateMediaSequenceSegment(
    ULevelSequence* LevelSequence,
    UMediaSource* MediaSource,
    UMediaTexture* MediaTexture,
    int32 StartFrame,
    int32 EndFrame)
{
    if (!LevelSequence || !MediaSource || !MediaTexture)
    {
        UE_LOG(LogTemp, Error, TEXT("CreateMediaSequenceSegment: 无效输入。"));
        return false;
    }

    UMovieScene* MovieScene = LevelSequence->GetMovieScene();
    if (!MovieScene)
    {
        return false;
    }

    // 1. 创建媒体轨道
    UMovieSceneMediaTrack* MediaTrack = MovieScene->AddTrack<UMovieSceneMediaTrack>();
    if (!MediaTrack)
    {
        return false;
    }

    // 2. 创建媒体区段
    UMovieSceneMediaSection* MediaSection = Cast<UMovieSceneMediaSection>(MediaTrack->CreateNewSection());
    if (!MediaSection)
    {
        // 创建失败则移除刚添加的轨道
        MovieScene->RemoveTrack(*MediaTrack);
        return false;
    }

    // 3. 配置区段属性
    FFrameNumber Start(StartFrame);
    FFrameNumber End(EndFrame);
    MediaSection->SetRange(TRange<FFrameNumber>(Start, End));
    MediaSection->SetMediaSource(MediaSource);
    // 设置媒体纹理（这通常会触发编辑器的提示流程，但程序化设置会跳过）
    MediaSection->SetMediaTexture(MediaTexture);
    
    // 可选：设置循环
    // MediaSection->SetLooping(true);
    // 可选：设置播放速率
    // MediaSection->SetPlaybackRate(1.0f);

    // 4. 将区段添加到轨道
    MediaTrack->AddSection(*MediaSection);

    // 5. 通知序列有改动（关键步骤）
    MovieScene->MarkAsDirty();

    UE_LOG(LogTemp, Log, TEXT("成功在帧 %d 到 %d 之间创建媒体动画段。"), StartFrame, EndFrame);
    return true;
}
```

## 模块依赖

要使用此插件的功能，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Media` | 媒体框架核心接口 |
| `MediaAssets` | 提供 `UMediaPlayer`, `UMediaSource`, `UMediaTexture` 等资产类 |
| `MediaUtils` | 媒体工具函数和类，如 `FMediaRecorder` |
| `SequencerCore` | Sequencer 核心系统 |
| `MovieScene` | Sequencer 场景和轨道的基础类 |
| `MovieSceneTools` | Sequencer 编辑器工具集 |

**注意**：`MediaCompositingEditor` 模块本身还依赖于 `EditorWidgets`, `PropertyEditor`, `LevelEditor`, `SequencerWidgets` 等编辑器模块，但这些通常由引擎自动包含。如果你的模块也需要直接访问编辑器 UI 功能（如提示窗口），则需要添加对 `MediaCompositingEditor` 模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-05-12 | `5aa3e62a` | Media: Sequencer media track shows a yellow warning when the level sequence display rate differs from the media source rate. | Sequencer中的媒体轨道现在会在关卡序列显示速率与媒体源帧率不匹配时显示黄色警告。 |
| 2026-03-20 | `3fae06d2` | [MediaCompositing] Build Media Source Thumbnail on demand from Asset Thumbnail when requested for the first time. | 改为首次请求时按需从资产缩略图构建媒体源缩略图，优化性能。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 为多个文件补充了缺失的渲染相关头文件包含和前向声明，提高编译兼容性。 |
| 2026-02-16 | `cd1d14de` | [MediaCompositing] Fix Media Texture not updating when created through the media track creation prompt. | 修复了通过媒体轨道创建提示框创建媒体纹理后，纹理未能及时更新的Bug。 |

### 维护评价

- **活跃度**：该插件处于**活跃维护**状态。最近一次代码提交距今不足一个月（2026年5月），且近期更新集中在功能优化（速率不匹配警告）、性能改进（按需构建缩略图）和 Bug 修复（媒体纹理更新）上。
- **年龄与状态**：虽然插件创建于约8年前（2017年），属于“老古董”级别，但鉴于其在 Sequencer 工作流中的核心地位，Epic Games 持续为其投入维护资源。
- **已知问题/限制**：从提交记录看，开发团队正在积极解决已知问题。潜在限制可能包括对某些特定媒体格式或硬件加速功能的支持程度，这取决于底层的 `MediaPlayer` 实现。
- **推荐使用**：**强烈推荐**。对于任何需要在 Sequencer 时间线中精确控制媒体播放的项目（如过场动画、虚拟制作），MediaCompositing 是官方提供的标准且强大的解决方案。其持续维护保证了与最新引擎版本的兼容性和稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaCompositing)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/media-framework-in-unreal-engine/)（媒体框架整体文档，涵盖本插件使用场景）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaCompositing/Tests)（如果存在）