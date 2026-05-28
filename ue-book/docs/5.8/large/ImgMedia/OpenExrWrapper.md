# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（媒体源资产，编辑器工具） |
| 模块 | `ImgMedia` (Runtime), `ImgMediaFactory` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaEditor` (Runtime), `OpenExrWrapper` (Runtime), `ExrReaderGpu` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia) | |

## 用途

本插件提供了一个**媒体播放器**，其功能是将一系列静态图像文件（如 EXR、BMP、JPG、PNG 序列）当作“视频”来播放和控制。它解决的核心问题是**在 Unreal Engine 中高效、流畅地播放高动态范围（HDR）的图像序列**，特别是视觉特效（VFX）行业标准的 OpenEXR 格式。

**为什么存在：**
1.  **行业标准支持**：EXR 是视觉特效和电影制作中用于存储渲染帧、多通道 AOV（Arbitrary Output Variables，如深度、法线、ID 通道等）和 Alpha 通道的标准格式。本插件是连接离线渲染/合成流程与实时引擎的桥梁。
2.  **高质量与灵活性**：支持 EXR 的高精度颜色深度（半精度浮点）、多通道、平铺（Tiled）存储以及压缩选项，满足专业制作需求。
3.  **工作流程集成**：允许艺术家将渲染好的帧序列直接导入引擎进行预览、合成或作为背景元素，无需先转码成传统视频格式，保持了数据的原始质量和完整性。
4.  **可扩展架构**：通过 `ImgMediaFactory` 模块，可以轻松添加对其他图像格式的支持。

## 使用场景

-   **视觉特效与实拍合成**：将 Maya、Houdini、Nuke 等软件渲染出的 EXR 帧序列在 UE 中作为动态背景或前景元素进行实时预览和合成。
-   **材质与渲染调试**：播放多通道 EXR 文件（如 beauty、diffuse、specular、depth），在引擎内逐帧检查不同渲染通道的结果。
-   **过场动画与预渲染内容**：使用高分辨率的图像序列作为游戏中的预渲染过场动画。
-   **动态贴图与UI**：将一系列图片作为材质的动态纹理或 UI 元素的序列帧动画。
-   **摄影测量与扫描数据回放**：播放从照片序列重建的 3D 模型纹理或点云数据。

## 蓝图用法

本插件的核心播放控制功能集成在引擎标准的 `UMediaPlayer` 和 `UMediaSource` 蓝图接口中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个媒体源，开始播放图像序列。 | `UMediaPlayer` |
| `Play` | 开始或恢复播放当前媒体。 | `UMediaPlayer` |
| `Stop` | 停止播放并重置播放位置。 | `UMediaPlayer` |
| `Set Looping` | 设置媒体是否循环播放。 | `UMediaPlayer` |
| `Get Duration` | 获取序列总时长（由序列帧数和帧率决定）。 | `UMediaPlayer` |
| `Get Time` | 获取当前播放位置。 | `UMediaPlayer` |
| `Seek` | 将播放位置跳转到指定时间。 | `UMediaPlayer` |
| `Set Rate` | 设置播放速率（支持正向、反向和变速）。 | `UMediaPlayer` |
| `Media Event Dispatcher` (Event) | 媒体播放状态变更事件（如 Opened, Closed, PlaybackEndReached）。 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1.  **创建媒体资产**：
    *   在内容浏览器中右键，选择 `Media` -> `Media Source` -> `Img Media Source`，创建一个新的媒体源资产。
    *   在该资产的详情面板中，设置 `Sequence Path` 属性，指向存放图像序列的文件夹（例如 `C:\MySequence\Frame_`），插件会自动识别序列中的所有支持格式的图片。

2.  **搭建播放器**：
    *   将一个 `MediaPlayer` 资产拖拽到场景中，或通过蓝图动态创建。
    *   在其详情面板中，将 `Media Source` 设置为上一步创建的 `Img Media Source`。
    *   可以勾选 `Play on Open` 和 `Loop` 以实现自动循环播放。

3.  **蓝图控制**：
    *   使用 `Open Source` 节点，传入 `MediaPlayer` 和 `ImgMediaSource` 对象，即可开始播放。
    *   通过 `Media Event Dispatcher` 监听 `PlaybackEndReached` 事件，可以在序列播放完毕时触发特定逻辑。
    *   通过 `Seek` 节点和 `Get Duration`、`Get Time` 节点的配合，可以实现精确的帧定位或进度条拖动。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "ImgMediaSource.h" // 如果需要直接操作ImgMedia源资产
```

### 基本用法

以下代码演示了如何通过 C++ 加载并播放一个图像序列。

```cpp
// 来源：基于标准 MediaPlayer 用法及 ImgMediaSource 资产接口
// 1. 创建或获取 MediaPlayer 对象
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
// 或者从某个组件获取: MediaPlayerComponent->GetMediaPlayer();

// 2. 创建 ImgMediaSource 对象并设置路径
UImgMediaSource* MediaSource = NewObject<UImgMediaSource>();
MediaSource->SequencePath = FDirectoryPath();
MediaSource->SequencePath.Path = TEXT("C:/RenderOutput/Shot01_");
// 可选：设置帧率
// MediaSource->FrameRateOverride = FFrameRate(24, 1); // 24fps

// 3. 打开媒体源并播放
if (MediaPlayer->OpenSource(MediaSource))
{
    MediaPlayer->Play();
    // 设置循环
    MediaPlayer->SetLooping(true);
}

// 4. 在 Tick 或定时器中检查状态
// MediaPlayer->GetState() 可以返回 EMediaPlayerState::Playing 等状态。
```

### 进阶用法

进阶用法涉及多通道 EXR 读取、缓存管理和 GPU 加速。

```cpp
// 来源：结合 FOpenExrHeaderReader, FRgbaInputFile, FExrInputFile 及缓存管理
// 1. 使用 FOpenExrHeaderReader 探查 EXR 文件信息（无需完整读取）
FOpenExrHeaderReader HeaderReader(TEXT("C:/MySequence/frame_0010.exr"));
if (HeaderReader.HasInputFile())
{
    FIntPoint Dimensions = HeaderReader.GetDataWindow();
    FFrameRate FrameRate = HeaderReader.GetFrameRate(FFrameRate(24, 1));
    TArray<FString> ChannelNames;
    HeaderReader.GetChannelNames(ChannelNames); // 获取所有通道名，如 “R”, “G”, “B”, “A”, “Depth.Z”

    // 判断是否适合 GPU 加速
    bool bUseGpu = HeaderReader.IsOptimizedForGpu();
}

// 2. 使用 FRgbaInputFile 读取整个 RGBA 图像数据
TArray<uint16> PixelData; // 存储半精度浮点 RGBA 数据
FRgbaInputFile RgbaReader(TEXT("C:/MySequence/frame_0010.exr"));
if (RgbaReader.HasInputFile())
{
    FIntPoint Size = RgbaReader.GetDataWindow();
    PixelData.SetNumZeroed(Size.X * Size.Y * 4); // RGBA
    RgbaReader.SetFrameBuffer(PixelData.GetData(), FIntPoint(4, Size.X * 4)); // 设置交错存储的缓冲区
    RgbaReader.ReadPixels(0, Size.Y - 1); // 读取所有行
}

// 3. 使用 FExrInputFile 选择特定通道读取（用于 AOV 管线）
TArray<uint16> BeautyData;
TArray<uint16> DepthData;
// ... 初始化缓冲区大小
FExrInputFile ChannelReader(TEXT("C:/MySequence/frame_0010.exr"), 0); // 0 表示自动线程数
if (ChannelReader.HasInputFile())
{
    FIntPoint Size = ChannelReader.GetDataWindow();
    // 将 “beauty.R”, “beauty.G”, “beauty.B” 通道读入 BeautyData 的 R, G, B 插槽
    ChannelReader.ReadPixels(BeautyData.GetData(), Size,
        TEXT("beauty.R"), TEXT("beauty.G"), TEXT("beauty.B"), TEXT("A"), // 通道映射
        0, Size.Y - 1);
    // 将 “Zdepth.Z” 通道读入 DepthData 的所有插槽（灰度图）
    ChannelReader.ReadPixels(DepthData.GetData(), Size,
        TEXT("Zdepth.Z"), TEXT("Zdepth.Z"), TEXT("Zdepth.Z"), TEXT(""), // 空字符串填 0
        0, Size.Y - 1);
}
```

## Demo 示例

以下是一个最小的 C++ 示例，展示如何在 Actor 中集成 ImgMedia 播放器。

```cpp
// AImgMediaDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "AImgMediaDemoActor.generated.h"

UCLASS()
class YOURPROJECT_API AImgMediaDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AImgMediaDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaSource* MediaSource;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayMediaSequence();
};
```

```cpp
// AImgMediaDemoActor.cpp
#include "AImgMediaDemoActor.h"

AImgMediaDemoActor::AImgMediaDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
    // 可以在构造函数或蓝图中创建并设置 MediaPlayer 和 MediaSource 资产。
}

void AImgMediaDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (MediaSource && MediaPlayer)
    {
        // 连接播放完成事件（可选）
        MediaPlayer->OnEndReached.AddDynamic(this, &AImgMediaDemoActor::PlayMediaSequence); // 循环播放
        PlayMediaSequence();
    }
}

void AImgMediaDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}

void AImgMediaDemoActor::PlayMediaSequence()
{
    if (MediaPlayer && MediaSource)
    {
        MediaPlayer->OpenSource(MediaSource);
        MediaPlayer->SetLooping(false); // 因为我们用事件手动循环
        MediaPlayer->Play();
    }
}
```

## 模块依赖

从 `Build.cs` 文件分析，使用本插件时，你的模块通常不需要直接依赖这些底层模块，因为功能已封装在 `MediaPlayer` 等核心类中。但若需进行底层开发，以下是关键依赖：

| 模块 | 用途 |
|---|---|
| `OpenEXRWrapper` | 提供对 OpenEXR 库的封装，用于读写 `.exr` 文件。 |
| `ImageWrapper` | 通用图像格式（如 BMP, JPG, PNG）的解码封装。 |
| `MediaUtils` | 提供媒体播放器、样本处理、缓存管理等工具类。 |
| `MediaAssets` | 提供 `UMediaPlayer`, `UMediaSource`, `UMediaTexture` 等资产类。 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, EditorStyle, PropertyEditor, Projects, DeveloperSettings 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `edcd0d53` | [ImgMedia] refresh single-frame sequences on tile visibility changes | 修复单帧图像序列在平铺（Tile）可见性变化时的刷新问题。 |
| 2026-05-26 | `cf292c45` | [ImgMedia] Use AR-constrained view rect for tile mip selection | 改进平铺Mip选择策略，使用宽高比约束的视图矩形。 |
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened analytics. | 修复最近一个提交导致ImgMedia和NDI播放器触发错误的媒体源打开分析事件。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro. | 为多种媒体播放器及捕获处理添加了额外的引擎分析信息。 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 在关卡编辑器窗口菜单中添加了共享的“媒体”分类。 |

### 维护评价

-   **创建时间**：2017年8月创建，至今已近9年。
-   **近期活跃度**：**非常活跃**。尽管插件本身历史悠久，但从Git日志可见，在2026年5月仍有密集的功能改进和bug修复提交，主要涉及平铺渲染（Tiling）、Mip选择、分析事件和编辑器集成。这表明插件仍在Epic的积极维护和功能增强列表中。
-   **已知问题/限制**：作为核心媒体框架的一部分，其稳定性较高。主要限制在于对巨大图像序列的内存管理，需要合理配置缓存。
-   **推荐使用**：**强烈推荐**。如果你的工作流涉及EXR或其他静态图像序列，这是官方提供的、功能完备且持续更新的解决方案。虽然年龄较老，但其核心架构已被验证并不断现代化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview) (Media Framework 通用文档，较早但仍有参考价值)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia/Tests) (位于插件目录下的Tests文件夹)