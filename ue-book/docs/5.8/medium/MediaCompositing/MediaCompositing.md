# Media Compositing

> Actors, components and Sequencer extensions for compositing media（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 媒体合成 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `MediaCompositing` (Runtime), `MediaCompositingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaCompositing) | |

## 用途

该插件的核心功能是将媒体播放（视频、图像序列）无缝集成到 **Sequencer** 中。它不仅仅是一个媒体播放器，而是一个完整的 **Sequencer 驱动的媒体控制与合成** 解决方案。

它解决了以下具体问题：
1.  **时间线精确控制**：允许在 Sequencer 的时间线上像控制摄像机动画、Actor 属性一样，精确控制媒体片段的开始、结束、循环和播放速度。
2.  **媒体与场景同步**：确保媒体播放（视频/音频）与场景中的其他动画（如角色动画、粒子效果）严格同步，这对于过场动画（Cutscene）、虚拟制作（Virtual Production）和预渲染背景合成至关重要。
3.  **资源管理与复用**：提供了 `MediaPlayerStore` 等机制，在 Sequencer 评估过程中智能管理和复用 `UMediaPlayer` 对象，避免频繁创建和销毁，提升性能和稳定性。
4.  **代理与图层支持**：支持通过 `IMediaPlayerProxyInterface` 代理来管理媒体源，这使得像 `MediaPlate` 这样的高级 Actor 可以管理多个媒体图层（用于画中画、合成），并由 Sequencer 统一控制。
5.  **编辑器集成**：提供了编辑器扩展（`MediaCompositingEditor`），用于在 Sequencer 界面中直观地添加、编辑媒体轨道和属性。

简而言之，**它让媒体成为 Sequencer 中的一等公民，实现了“基于时间线的媒体驱动”工作流**，而非简单的“在场景中放置一个媒体播放器”。

## 使用场景

- **游戏过场动画（Cutscene）**：你正在制作一段过场动画，需要同步播放一段预渲染的视频作为背景，同时前景中的角色动画、镜头移动和对话由 Sequencer 控制。**→ 使用 `UMovieSceneMediaTrack` 将视频片段添加到 Sequencer 时间线。**
- **虚拟制作（Virtual Production）**：在 LED 墙上显示实时背景视频，该视频的播放进度需要与摄影机运动在 Sequencer 中严格同步。**→ 使用媒体轨道控制背景视频的播放，确保视觉同步。**
- **动画预览与合成**：在制作动画时，你需要将一段实拍的参考视频或图像序列（如 EXR 序列）叠加在 3D 场景上，作为对位或风格参考。**→ 使用媒体轨道控制参考视频的播放和循环。**
- **交互式媒体墙/广告牌**：在游戏世界中，你需要一个动态的广告牌，其显示内容由 Sequencer 驱动，可以是一段视频或一个图片序列。**→ 使用 `UMovieSceneMediaPlayerPropertyTrack` 来控制一个 `UMediaPlayer` Actor 的媒体源属性。**

## 蓝图用法

该插件的蓝图功能主要通过 **属性** 和 **Sequencer 轨道** 暴露，直接用于 Sequencer 编辑器中配置媒体行为。

### 核心节点 (属性与配置)

| 节点/属性 | 说明 | 所在类 |
|---|---|---|
| `MediaSource` (属性) | 指定此媒体片段使用的媒体源资产 (如文件媒体源、流媒体源)。 | `UMovieSceneMediaSection` |
| `bLooping` (属性) | 设置媒体片段是否循环。这有助于某些格式（如 EXR 序列）在播放接近结束时预缓存开头数据。 | `UMovieSceneMediaSection` |
| `MediaTexture` (属性) | 指定接收视频输出的 `UMediaTexture`。该纹理随后可用于材质。 | `UMovieSceneMediaSection` |
| `MediaSoundComponent` (属性) | 指定接收音频输出的 `UMediaSoundComponent`。 | `UMovieSceneMediaSection` |
| `StartFrameOffset` (属性) | 设置媒体源内部的起始偏移帧，用于从媒体的中间开始播放。 | `UMovieSceneMediaSection` |
| `bSynchronousScrubbing` (属性) (在轨道上) | 勾选后，在 Sequencer 中手动拖动时间轴时，将强制媒体同步更新帧，代价是编辑器可能卡顿，但能保证媒体与场景动画的实时对齐。 | `UMovieSceneMediaTrack` |

### 使用示例 (蓝图描述)

1.  **添加媒体轨道**：
    *   在 Sequencer 编辑器中，选中一个 Actor（或创建一个新的空 Actor）。
    *   点击 “+ Track” 按钮，在搜索栏输入 “Media”。
    *   选择 “Media Track”。这将创建一个 `UMovieSceneMediaTrack`。

2.  **添加媒体片段**：
    *   在 Media Track 上右键，选择 “Add Media Source…”。
    *   浏览并选择一个 `UMediaSource` 资产（例如一个指向视频文件的 `FileMediaSource`）。
    *   Sequencer 会自动创建一个 `UMovieSceneMediaSection`（媒体片段），其长度默认为媒体源的总时长。

3.  **配置媒体属性**：
    *   在 Sequencer 中选中该媒体片段。
    *   在细节面板（Details）中，你可以配置：
        *   `Media Texture`：分配一个 `MediaTexture` 资产。之后你可以在任何材质中使用该纹理来显示视频。
        *   `Media Sound Component`：分配一个场景中存在的 `MediaSoundComponent` 组件以播放音频。
        *   `Looping`：根据需要开启循环。
        *   `Start Frame Offset`：如果想跳过片头，可以设置一个偏移。

4.  **（高级）使用代理**：
    *   你需要一个实现了 `IMediaPlayerProxyInterface` 的 Actor（如 `AMediaPlate`）。
    *   在媒体片段的细节面板中，勾选 `Use External Media Player`。
    *   将 `External MediaPlayer` 属性设置为那个 Actor。
    *   该媒体片段现在将控制代理 Actor 内部的媒体播放器，而不是自己创建播放器。

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneMediaSection.h"
#include "MovieSceneMediaTrack.h"
#include "MediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
```

### 基本用法：通过 C++ 创建媒体轨道与片段

以下代码展示了如何以编程方式为一个 Level Sequence 添加媒体轨道并添加一个媒体片段。

```cpp
// 假设 LevelSequence 已加载
ULevelSequence* LevelSequence = ...;
UMovieScene* MovieScene = LevelSequence->GetMovieScene();

// 1. 创建媒体轨道
UMovieSceneMediaTrack* MediaTrack = Cast<UMovieSceneMediaTrack>(MovieScene->AddTrack(UMovieSceneMediaTrack::StaticClass()));

// 2. 创建媒体片段并添加到轨道
UMovieSceneMediaSection* MediaSection = Cast<UMovieSceneMediaSection>(MediaTrack->CreateNewSection());
// 设置片段的起始和结束时间（以序列的帧率为准）
MediaSection->SetRange(TRange<FFrameNumber>(FFrameNumber(0), FFrameNumber(150))); // 播放 150 帧
MediaTrack->AddSection(*MediaSection);

// 3. 配置媒体片段属性
// 获取或创建一个媒体源资产
UMediaSource* MyMediaSource = LoadObject<UMediaSource>(nullptr, TEXT("/Game/Movies/MyVideo.FileMediaSource"));
MediaSection->SetMediaSource(MyMediaSource);

// 设置接收视频的纹理
UMediaTexture* MyMediaTexture = LoadObject<UMediaTexture>(nullptr, TEXT("/Game/Media/VideoTexture.MediaTexture"));
MediaSection->MediaTexture = MyMediaTexture;

// 启用循环
MediaSection->bLooping = true;

// 4. 标记序列资产为已修改，以便保存
LevelSequence->Modify();
```

### 进阶用法：自定义媒体播放参数与缓存

通过修改 `FMovieSceneMediaPlaybackParams` 和 `FMediaSourceCacheSettings`，可以精细控制播放行为。

```cpp
// 在自定义的序列评估逻辑中（例如自定义的Template或Node），你可能会操作媒体数据
// 获取序列片段的持久化数据
FMovieSceneMediaData& MediaData = PersistentData.GetSectionData<FMovieSceneMediaData>();

// 设置播放参数（例如，当需要精确控制播放范围时）
FMovieSceneMediaPlaybackParams PlaybackParams;
PlaybackParams.bIsLooping = false;
PlaybackParams.SectionTimeRange = TRange<FTimespan>(FTimespan::FromSeconds(2.0), FTimespan::FromSeconds(10.0));
PlaybackParams.FrameDuration = FTimespan::FromSeconds(1.0 / 30.0); // 假设序列是30fps

// 配置媒体源的缓存设置
FMediaSourceCacheSettings CacheSettings;
CacheSettings.bOverride = true;
CacheSettings.DurationSeconds = FTimespan::FromSeconds(5.0); // 预缓存5秒内容

// 你可以将这些设置应用到媒体片段或通过代理传递
// ... (具体实现取决于你的扩展方式)
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个自定义的 Actor，该 Actor 包含一个由 Sequencer 驱动的媒体播放器。

```cpp
// DrivenMediaActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "Components/StaticMeshComponent.h"
#include "DrivenMediaActor.generated.h"

UCLASS()
class ADrivenMediaActor : public AActor
{
    GENERATED_BODY()

public:
    ADrivenMediaActor();

    // 被 Sequencer 通过代理接口控制的媒体播放器
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    TObjectPtr<UMediaPlayer> MediaPlayer;

    // 视频输出纹理
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    TObjectPtr<UMediaTexture> MediaTexture;

    // 用于显示视频的网格体
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    TObjectPtr<UStaticMeshComponent> DisplayMesh;

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// DrivenMediaActor.cpp
#include "DrivenMediaActor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "Materials/MaterialInstanceDynamic.h"

ADrivenMediaActor::ADrivenMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建并配置静态网格体组件，用于显示视频
    DisplayMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DisplayMesh"));
    RootComponent = DisplayMesh;
    // (在构造函数中设置网格体，例如一个平面)

    // 创建媒体播放器和纹理
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    // 将播放器绑定到纹理，以便纹理接收视频帧
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void ADrivenMediaActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建一个动态材质实例，使用媒体纹理作为参数
    UMaterialInterface* BaseMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_VideoScreen"));
    if (BaseMat && DisplayMesh)
    {
        UMaterialInstanceDynamic* DynamicMat = DisplayMesh->CreateAndSetMaterialInstanceDynamicFromMaterial(0, BaseMat);
        if (DynamicMat)
        {
            DynamicMat->SetTextureParameterValue("VideoTexture", MediaTexture);
        }
    }

    // 注意：此 Actor 的 MediaPlayer 并不在 BeginPlay 中打开任何源。
    // 它将由 Sequencer 中的一个 `UMovieSceneMediaPlayerPropertyTrack` 通过设置 `MediaSource` 属性来驱动。
}
```

**使用步骤**：
1.  编译上述代码。
2.  在编辑器中，将 `ADrivenMediaActor` 拖入场景。
3.  打开一个 Level Sequence。
4.  在 Sequencer 中，为该 Actor 添加一个 `MediaPlayer Property Track`。
5.  在该轨道上右键添加一个片段，在细节面板中设置 `Media Source` 和 `Loop`。
6.  播放 Sequence，你会看到 `ADrivenMediaActor` 上的网格体开始播放指定的视频。

## 模块依赖

你的模块需要依赖以下**非标准**模块来使用 MediaCompositing 的功能（尤其是 C++ 扩展）：

| 模块 | 用途 |
|---|---|
| `MediaCompositing` | Runtime 模块，包含核心的媒体合成逻辑、轨道和片段类。 |
| `MediaCompositingEditor` | Editor 模块，提供 Sequencer 编辑器扩展，仅在编辑器环境下需要。 |
| `MediaAssets` | 提供 `UMediaSource`， `UMediaPlayer`， `UMediaTexture` 等基础媒体资产类。 |
| `MovieScene` | Sequencer 的核心模块，提供 `UMovieSceneTrack`， `UMovieSceneSection` 等基础类。 |
| `MovieSceneTools` | Sequencer 的工具模块，提供编辑器 UI 和交互支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量转换为浮点数时产生的编译器警告。 |
| 2026-05-12 | `5aa3e62a` | Media: Sequencer media track shows a yellow warning when the level sequence display rate differs fro | Sequencer 媒体现在会在关卡序列显示率与媒体帧率不匹配时显示黄色警告。 |
| 2026-03-20 | `3fae06d2` | [MediaCompositing] Build Media Source Thumbnail on demand from Asset Thumbnail when requested for th | 现在按需从资产缩略图构建媒体源缩略图，优化了编辑器资源管理。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 为多个文件添加了缺失的渲染头文件包含和前置声明，提升编译兼容性。 |
| 2026-02-16 | `cd1d14de` | [MediaCompositing] Fix Media Texture not updating when created through the media track creation prom | 修复了通过媒体轨道创建提示框创建媒体纹理时纹理不更新的问题。 |

### 维护评价

- **维护活跃**：该插件在 **2026 年** 仍有频繁且实质性的更新，包括功能增强（帧率不匹配警告、缩略图构建）、错误修复（纹理更新问题）和编译兼容性改进。
- **核心组件**：作为 UE 媒体框架（Media Framework）与 Sequencer 集成的关键组件，它随着引擎核心功能一起迭代，维护状态稳定。
- **实验性与风险**：虽然 `.uplugin` 标记为非实验性，但鉴于其功能涉及复杂的媒体解码、同步和内存管理，在极端使用场景（如超长时间线、极高分辨率媒体、快速擦洗）下仍可能遇到边缘情况或性能问题。
- **推荐**：**强烈推荐使用**。对于任何需要在 Sequencer 中精确、同步控制媒体播放的工作流程（如过场动画、虚拟制作、动画合成），此插件是官方提供的标准且功能完整的解决方案。其活跃的维护也保证了与最新引擎版本的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaCompositing)
- 官方文档：Unreal Engine 官方文档通常在其 **媒体框架（Media Framework）** 和 **Sequencer** 章节中涉及此插件的使用，没有单独的专属页面。
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaCompositing/Tests) (如果存在)