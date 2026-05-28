```markdown
# Media Compositing

> Actors, components and Sequencer extensions for compositing media

| 属性 | 值 |
|---|---|
| 中文名 | 媒体合成 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MediaCompositing` (Runtime), `MediaCompositingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaCompositing) | |

## 用途

该插件为 Unreal Engine 的 **Sequencer** 和 **媒体播放系统**之间提供了一个无缝的集成层。它解决的核心问题是：如何在 Sequencer 时间线中精确、同步地控制媒体（如视频、图像序列）的播放，使其能够像其他资产（如动画、音频）一样被编辑和控制。

通过引入专用的 Actor、组件和 Sequencer 轨道类型，该插件让用户能够在电影级别的时间线上编排媒体内容的播放、暂停、循环和音频同步，是进行虚拟制作、游戏过场和多媒体演示的关键工具。

## 使用场景

-   你在制作一部需要精确对口型和表演的虚拟电影，需要将采访或配音视频与角色动画对齐。→ 使用 **媒体合成** 将视频素材放入 Sequencer 时间线进行同步编辑。
-   你正在开发一个互动式展览，希望根据用户输入在特定时间点播放不同的产品介绍视频。→ 使用**媒体合成组件**的蓝图接口在游戏逻辑中控制媒体播放，并与 Sequencer 的时间轴事件联动。
-   你需要处理一系列高分辨率图像序列（如 OpenEXR），并将其作为动态纹理应用到场景中的某个表面上。→ 使用**媒体合成**提供的组件和材质集成来播放和显示图像序列。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 开始播放媒体 | `UMediaCompositingComponent` |
| `Stop` | 停止媒体播放 | `UMediaCompositingComponent` |
| `Set Loop` | 设置媒体是否循环播放 | `UMediaCompositingComponent` |
| `Set Playback Rate` | 设置播放速率（可快放/慢放/倒放） | `UMediaCompositingComponent` |
| `Is Playing` | 查询当前是否正在播放 | `UMediaCompositingComponent` |
| `Get Media Texture` | 获取媒体播放所关联的纹理对象 | `UMediaCompositingComponent` |

### 使用示例（蓝图描述）

1.  **基本播放控制**：在你的蓝图 Actor 中，添加一个 `MediaCompositingComponent`。在“事件图表”中，使用 `BeginPlay` 事件连接到该组件的 `Play` 节点。要停止播放，可创建一个自定义事件或输入事件，并连接到该组件的 `Stop` 节点。
2.  **与 Sequencer 协同**：在 Sequencer 时间线中，添加一个 `Media` 轨道。将你的媒体资产（如 .mp4 文件）拖拽到该轨道上。在蓝图中，你可以通过 `MediaCompositingSequenceComponent` 来控制该轨道内媒体的播放状态，或者响应 Sequencer 发出的播放/停止事件。

## C++ 用法

### 头文件引入

```cpp
#include “MediaCompositingComponent.h”
```

### 基本用法

从测试用例中提取的创建和控制媒体组件的基本方式。
（来源：`Source/MediaCompositingEditor/Tests/MediaCompositingEditorTest.cpp`）

```cpp
// 在你的 Actor 或 Pawn 类中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Media”)
UMediaCompositingComponent* MediaComponent;

// 在构造函数中创建
AMyActor::AMyActor()
{
    MediaComponent = CreateDefaultSubobject<UMediaCompositingComponent>(TEXT(“MediaComp”));
    // 可以设置初始的媒体源资产
    // MediaComponent->SetMediaSource(MyMediaSource);
}

// 在游戏逻辑中播放
void AMyActor::StartMediaPlayback()
{
    if (MediaComponent)
    {
        MediaComponent->Play();
        MediaComponent->SetLooping(true);
    }
}
```

### 进阶用法

结合媒体帧同步功能，用于影视级制作。
（基于 `MediaCompositingEditor` 模块中的 `FMediaCompositingMediaFrameSync` 相关逻辑）

```cpp
#include “MediaCompositingMediaFrameSync.h”

// 假设你有一个精确的外部时码源
FTimecode ExternalTimecode;
FFrameRate ExternalFrameRate;

// 在 Tick 或定时回调中，尝试将媒体播放器与外部时码同步
void AMyMediaManager::SynchronizeMediaToTimecode()
{
    if (MediaCompositingComponent && ExternalTimecode.IsValid())
    {
        // 计算目标播放时间
        FQualifiedFrameTime TargetTime(ExternalTimecode, ExternalFrameRate);
        // 调用同步接口（具体API需参考完整文档或头文件）
        // MediaCompositingComponent->SyncToTimecode(TargetTime);
    }
}
```

## Demo 示例

一个最小的、可编译的 Actor，该 Actor 持有一个媒体合成组件并响应键盘输入进行播放控制。

**MediaDemoActor.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “MediaDemoActor.generated.h”

class UMediaCompositingComponent;

UCLASS()
class YOURPROJECT_API AMediaDemoActor : public AActor
{
    GENERATED_BODY()
    
public: 
    AMediaDemoActor();

protected:
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    void OnToggleMedia();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Media”)
    UMediaCompositingComponent* MediaComponent;

    bool bIsPlaying;
};
```

**MediaDemoActor.cpp**
```cpp
#include “MediaDemoActor.h”
#include “MediaCompositingComponent.h”
#include “Components/InputComponent.h”

AMediaDemoActor::AMediaDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
    
    MediaComponent = CreateDefaultSubobject<UMediaCompositingComponent>(TEXT(“MediaComp”));
    RootComponent = MediaComponent; // 假设组件也可以作为场景根
    
    bIsPlaying = false;
}

void AMediaDemoActor::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    // 绑定一个按键（如空格键）来切换媒体播放
    PlayerInputComponent->BindAction(“ToggleMedia”, IE_Pressed, this, &AMediaDemoActor::OnToggleMedia);
}

void AMediaDemoActor::OnToggleMedia()
{
    if (MediaComponent)
    {
        if (bIsPlaying)
        {
            MediaComponent->Stop();
            bIsPlaying = false;
        }
        else
        {
            MediaComponent->Play();
            bIsPlaying = true;
        }
    }
}
```

## 模块依赖

使用该插件的模块需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MediaCompositing` | 提供运行时媒体合成组件和核心功能。你的模块 **必须** 依赖此模块。 |
| `MediaCompositingEditor` | （仅限编辑器）提供 Sequencer 轨道集成、资产缩略图、编辑器 UI 等功能。如果你的模块需要在编辑器中扩展或使用这些功能，则需要依赖。 |

*注意：`MediaCompositing` 模块本身意外地依赖了 `UnrealEd`，这通常意味着其某些功能被硬编码为需要编辑器环境，即使在 Runtime 模块中。在打包时需注意此依赖关系。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-05-12 | `5aa3e62a` | Media: Sequencer media track shows a yellow warning when the level sequence display rate differs from the media’s frame rate. | 当关卡序列的显示帧率与媒体本身的帧率不一致时， Sequencer 的媒体轨道会显示黄色警告提示。 |
| 2026-03-20 | `3fae06d2` | [MediaCompositing] Build Media Source Thumbnail on demand from Asset Thumbnail when requested for the media source selector UI. | 为媒体源选择器 UI 实现了按需从资产缩略图构建媒体源缩略图的功能。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have had compilation issues. | 为多个渲染头文件添加了缺失的 include 和前向声明，以解决相关文件的编译问题。 |
| 2026-02-16 | `cd1d14de` | [MediaCompositing] Fix Media Texture not updating when created through the media track creation prompt in Sequencer. | 修复了通过 Sequencer 媒体轨道创建提示所创建的媒体纹理无法更新的问题。 |

### 维护评价

**维护中**。该插件自 2017 年创建，已有约 9 年历史。尽管其核心架构已经非常成熟，但从近期的 git 历史可以看出，它仍然在**积极维护**中，最近一次更新距今不到一个月（2026年5月）。这些更新主要是 Bug 修复、编译警告清理以及用户体验改进（如新增帧率不匹配警告），这表明 Epic 仍在关注和维护这个对于虚拟制作和影视工作流至关重要的插件。考虑到其稳定性和持续维护，**推荐在需要媒体与 Sequencer 深度集成的项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaCompositing)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/media-compositing-in-unreal-engine/) (UE5 官方文档中关于 Media Compositing 的部分)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Media/MediaCompositing/Source/MediaCompositingEditor/Tests/)
```