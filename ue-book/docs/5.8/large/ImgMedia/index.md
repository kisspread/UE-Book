# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `ExrReaderGpu` (Runtime), `ImgMedia` (Runtime), `ImgMediaEditor` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `OpenExrWrapper` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia) | |

## 用途
`ImgMedia` 插件是一个专为专业影视、动画和视觉特效工作流程设计的媒体播放器。它并非播放传统的视频文件（如 .mp4, .mov），而是直接从一系列单独的图片文件（图像序列）中读取数据并将其作为视频播放。其核心价值在于支持**高动态范围（HDR）的EXR格式**，并提供了**GPU加速解码**能力，使得在UE5中预览和回放渲染农场输出的最终图像序列变得高效可行。它解决了将分帧渲染结果集成到实时引擎中进行可视化、编辑和最终合成预览的关键需求。

## 使用场景
- **影视后期与合成预览**：在UE5中直接加载和播放由Maya、Blender或Nuke等DCC工具渲染输出的EXR序列，实时检查最终渲染效果、动画节奏和特效合成。
- **建筑/产品可视化**：使用高质量的图像序列（如来自渲染器的8K图）作为动态天空盒、背景板或虚拟LED墙的内容源。
- **虚拟制片**：为LED Volume屏幕准备和预览预先渲染好的背景视频内容。
- **游戏内过场动画**：当需要使用预先渲染的高质量过场动画视频时，可以用图像序列替代，方便艺术家在UE编辑器中预览和调整。

## 蓝图用法
该插件的蓝图接口主要通过媒体资产（Media Assets）和媒体播放器（Media Player）组件暴露，核心是创建和配置一个图像序列媒体源。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Sequence Path` | 设置图像序列的文件夹路径（支持本地路径和打包后的虚拟路径）。 | `UImgMediaSource` |
| `Open Source` | 使用指定的媒体源（如`UImgMediaSource`）打开媒体。 | `UMediaPlayer` |
| `Play` | 开始播放已打开的媒体。 | `UMediaPlayer` |
| `Seek` | 跳转到媒体的特定时间点（帧）。 | `UMediaPlayer` |
| `Is Looping` / `Set Looping` | 获取或设置媒体是否循环播放。 | `UMediaPlayer` |

### 使用示例（蓝图描述）
1. 在内容浏览器中，创建一个新的 `ImgMediaSource` 资产。
2. 在该资产的详情面板中，设置 `Sequence Path` 属性，指向存放序列图片的文件夹（例如：`/Game/Media/MyRenderSeq`）。
3. 在场景中放置一个 `MediaPlayer` 资产和一个 `MediaTexture` 资产，并将 MediaTexture 的 `MediaPlayer` 属性指向刚才的 MediaPlayer。
4. 在 `MediaPlayer` 资产的详情面板中，将 `Media Source` 属性设置为步骤2创建的 `ImgMediaSource` 资产。
5. 通过蓝图（例如在 `BeginPlay` 事件中）获取 `MediaPlayer` 对象的引用，并调用 `Open Source` 节点（传入`ImgMediaSource`引用），然后调用 `Play` 节点。
6. 将 `MediaTexture` 应用到场景中任何使用该材质的物体上（如静态网格、UI图像），即可看到序列播放。

## C++ 用法

### 头文件引入
```cpp
#include "ImgMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
```

### 基本用法
从模块文档和通用媒体框架用法推断。
```cpp
// 创建或获取一个已有的 UImgMediaSource 对象
UImgMediaSource* ImgMediaSource = NewObject<UImgMediaSource>();
FString SequenceFolder = FPaths::ProjectContentDir() / TEXT("Media/RenderOutput");
ImgMediaSource->SetSequencePath(SequenceFolder);

// 获取或创建一个 UMediaPlayer
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();

// 打开源
if (MediaPlayer->OpenSource(ImgMediaSource))
{
    // 可选：设置循环
    MediaPlayer->SetLooping(true);
    // 开始播放
    MediaPlayer->Play();
}
```
*(来源：基于UE媒体框架通用模式及`ImgMediaSource`类头文件推断)*

### 进阶用法
结合MediaTexture在材质中采样。
```cpp
// 假设已有 MediaPlayer 和 MediaTexture 成员变量
UImgMediaSource* ImgSource = ...; // 同上创建
UMediaPlayer* Player = ...; // 同上创建

// 通过Player打开源
Player->OpenSource(ImgSource);

// 将Player连接到MediaTexture
if (MediaTexture)
{
    MediaTexture->SetMediaPlayer(Player);
}

// 在播放器状态改变的回调中，可以处理暂停、结束等事件
Player->OnMediaEvent().AddLambda([](EMediaEvent Event)
{
    if (Event == EMediaEvent::PlaybackEndReached)
    {
        // 序列播放完毕
    }
});
```

## Demo 示例
一个最小的可运行示例，用于在关卡开始时播放一个图像序列。

**ImgMediaDemoComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ImgMediaDemoComponent.generated.h"

class UImgMediaSource;
class UMediaPlayer;
class UMediaTexture;

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UImgMediaDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    // 在编辑器中设置的序列文件夹路径
    UPROPERTY(EditAnywhere, Category = "Media")
    FString SequencePath;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UImgMediaSource* ImgMediaSource;

    UPROPERTY()
    UMediaPlayer* MediaPlayer;

    // 注意：MediaTexture通常需要在材质中使用，这里仅为演示而持有引用
    // 实际使用时，应在材质编辑器中创建MediaTexture资产并拖拽到材质节点上
    // UPROPERTY()
    // UMediaTexture* MediaTexture;
};
```

**ImgMediaDemoComponent.cpp**
```cpp
#include "ImgMediaDemoComponent.h"
#include "ImgMediaSource.h"
#include "MediaPlayer.h"
// #include "MediaTexture.h" // 如果需要

void UImgMediaDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    if (SequencePath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("ImgMediaDemoComponent: SequencePath is not set."));
        return;
    }

    // 创建媒体源
    ImgMediaSource = NewObject<UImgMediaSource>(GetTransientPackage());
    ImgMediaSource->SetSequencePath(SequencePath);

    // 创建媒体播放器
    MediaPlayer = NewObject<UMediaPlayer>(GetTransientPackage());

    // 打开源并播放
    if (MediaPlayer->OpenSource(ImgMediaSource))
    {
        MediaPlayer->SetLooping(true); // 可选：循环播放
        MediaPlayer->Play();
        UE_LOG(LogTemp, Log, TEXT("Started playing image sequence: %s"), *SequencePath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open image sequence source."));
    }

    // 实际项目中，需要将MediaPlayer关联到MediaTexture，并将该MediaTexture用于材质。
    // 步骤：
    // 1. 在内容浏览器创建MediaTexture资产。
    // 2. 通过C++或蓝图将其MediaPlayer属性设置为这里的MediaPlayer。
    // 3. 在材质编辑器中使用该MediaTexture采样节点。
    // 4. 将该材质应用到场景中的物体上。
}
```

## 模块依赖
要使用 `ImgMedia` 插件，你的模块通常不需要直接依赖其子模块。插件的核心功能通过UE的媒体框架接口（`MediaPlayer`, `MediaTexture`）和资产（`ImgMediaSource`）提供。如果你需要在C++中直接操作其特有类型，可能需要添加依赖。

| 模块 | 用途 |
|---|---|
| `OpenExrWrapper` | 封装OpenEXR库，提供EXR图像格式的读写能力。 |
| `ExrReaderGpu` | 提供基于GPU的EXR文件读取加速。 |
| `ImgMediaEngine` | 媒体播放器引擎核心，负责线程管理、样本缓存和解码调度。 |
| `ImgMediaFactory` | 负责识别和创建图像序列媒体源（`ImgMediaSource`）资产。 |
| `ImgMediaEditor` | 提供编辑器中的资产工厂、自定义面板和路径浏览功能。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `edcd0d53` | [ImgMedia] refresh single-frame sequences on tile visibility changes | 优化了当Tile可见性变化时刷新单帧序列的逻辑。 |
| 2026-05-26 | `cf292c45` | [ImgMedia] Use AR-constrained view rect for tile mip selection | 在进行Tile Mip选择时，使用了受宽高比约束的视图矩形。 |
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened ana | 修复了ImgMedia和NDI播放器发出错误的`SourceOpened`分析事件的问题。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为多个媒体播放器和捕获/处理组件添加了额外的引擎分析信息。 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 在关卡编辑器窗口菜单中添加了共享的“媒体”类别。 |

### 维护评价
`ImgMedia` 插件自2017年创建以来已有约9年历史，属于成熟组件。从最近的提交记录（2026年5月）可以看出，它仍在**活跃维护**中。近期更新主要集中在：
1.  **性能与显示优化**：如针对Tile系统的刷新和Mip选择优化。
2.  **框架集成**：修复分析事件，并加强与其他媒体源（如NDI）的兼容性。
3.  **编辑器体验**：改善菜单组织。

该插件功能稳定，是UE5处理专业图像序列工作流的核心且必要的组件，**推荐使用**。虽然它“老”，但仍在持续适应引擎的新特性（如Nanite的虚拟几何体Tile系统）。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)