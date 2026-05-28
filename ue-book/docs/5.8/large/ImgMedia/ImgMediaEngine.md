# Img Media

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ExrReaderGpu` (Runtime), `ImgMedia` (Runtime), `ImgMediaEditor` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `OpenExrWrapper` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia) | |

## 用途

ImgMedia 是 UE 内置的**图像序列媒体播放器**插件，解决的核心问题是：**将一连串静态图片文件（如电影渲染输出的每一帧 EXR）当作视频来播放**。

与传统视频文件（MP4、MOV）不同，图像序列是影视和视觉特效行业的标准交付格式。每一帧都是独立的高精度图片文件（通常为 OpenEXR 格式，也支持 BMP/JPG/PNG），便于逐帧编辑和无损传输。ImgMedia 让引擎能像播放视频一样流畅地播放这些图像序列，并支持以下特性：

- **EXR 多线程解码**：通过 `OpenExrWrapper` 和 `ExrReaderGpu` 模块实现高性能 OpenEXR 解码
- **LRU 缓存帧加载**：`TLruCache` 模板管理帧数据，避免内存溢出
- **选择性 Mipmap 加载**：根据相机距离只加载需要的分辨率级别
- **正/反向播放**：支持倒放，适合配合 Sequencer 时间轴拖拽
- **异步初始化**：序列扫描在后台线程完成，不阻塞主线程
- **Tile 可见性流式加载**：大尺寸图像按瓦片按需加载（2026 年新增）

典型工作流：在外部 DCC（Nuke、Houdini、Blender）中渲染出一帧帧 EXR → 通过 ImgMedia 在引擎中实时预览 → 配合 Sequencer 做最终合成。

## 使用场景

- 你制作了影视级渲染输出（每帧为 EXR 文件），需要在引擎中实时预览 → 用 ImgMedia
- 你需要将 DCC 渲染的图像序列与场景灯光、特效同步播放 → ImgMedia + Sequencer
- 你需要对图像序列做选择性 Mipmap 加载以节省显存 → ImgMedia + ImgMediaPlaybackComponent（已废弃，建议迁移到 MediaPlate）
- 你处理超大分辨率图像序列，需要按瓦片按需加载 → ImgMedia 的 Tile 流式加载功能
- 你有 BMP/JPG/PNG 格式的逐帧图片序列需要当作视频播放 → ImgMedia（自 4.15 起支持）

## 模块架构

本插件由 6 个模块组成，各司其职：

```
┌─────────────────────────────────────────────────────┐
│                    ImgMedia (主模块)                    │
│  媒体播放器核心：帧加载、缓存、解码调度、播放控制       │
├──────────┬──────────┬───────────────┬───────────────┤
│ ImgMedia │ ImgMedia │ ImgMedia      │ ImgMedia      │
│ Factory  │ Engine   │ Editor        │ Factory       │
│ 媒体工厂 │ 引擎集成 │ 编辑器支持    │ 纹理工厂      │
├──────────┴──────────┴───────────────┴───────────────┤
│              OpenExrWrapper (EXR 底层封装)              │
│              ExrReaderGpu (GPU 加速 EXR 解码)           │
└─────────────────────────────────────────────────────┘
```

| 模块 | 职责 |
|---|---|
| `ImgMedia` | 核心播放逻辑：序列解析、帧缓存管理、线程调度、播放状态机 |
| `ImgMediaFactory` | `UImgMediaFactory`，负责根据文件扩展名创建合适的 Media Source |
| `ImgMediaEngine` | 引擎集成层：`ImgMediaPlaybackComponent`（已废弃）、Mipmap 信息注册 |
| `ImgMediaEditor` | 编辑器支持：资产缩略图、属性面板自定义 |
| `OpenExrWrapper` | OpenEXR 库的 C++ 封装，处理 EXR 文件的读取和解码 |
| `ExrReaderGpu` | GPU 加速的 EXR 帧读取器，用于大分辨率 EXR 的高性能解码 |

## 蓝图用法

> **注意**：`UImgMediaPlaybackComponent` 已在 UE 5.3 中废弃，建议迁移到 MediaPlate。以下为历史 API。

### 核心节点

由于 ImgMedia 主要通过 `UMediaPlayer` + `UMediaTexture` 标准 Media Framework 接口使用，其蓝图交互遵循通用媒体流程：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开图像序列的 Media Source | `UMediaPlayer` |
| `Play` | 开始播放图像序列 | `UMediaPlayer` |
| `Set Rate` | 设置播放速率（支持负值倒放） | `UMediaPlayer` |
| `Seek` | 跳转到指定时间位置 | `UMediaPlayer` |
| `Close` | 关闭当前媒体 | `UMediaPlayer` |

### 使用示例（蓝图描述）

**基本播放流程：**

1. 创建 `MediaPlayer` 资产（媒体类型选择 ImgMedia）
2. 创建 `MediaTexture` 资产，绑定到该 MediaPlayer
3. 创建 `FileMediaSource`，设置 SequencePath 指向图像序列文件夹
4. 在蓝图中：`MediaPlayer → Open Source (FileMediaSource)` → 图像序列开始加载
5. 将 `MediaTexture` 赋给材质的纹理采样节点 → 显示在场景中的物体上

**Sequencer 集成：**

1. 在 Sequencer 中添加 Media Track
2. 将 MediaPlayer 拖入 Media Track
3. 拖拽时间轴 → ImgMedia 自动按照帧时间戳显示对应图像帧
4. 支持正向和反向拖拽

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "FileMediaSource.h"
// 如需使用已废弃的 PlaybackComponent（不推荐）：
#include "Unreal/ImgMediaPlaybackComponent.h"
```

### 基本用法：打开并播放图像序列

```cpp
// 创建 MediaPlayer 并打开图像序列
void AMyActor::PlayImageSequence()
{
    // MediaPlayer 已通过 UPROPERTY 或 CreateDefaultSubobject 创建
    UFileMediaSource* Source = NewObject<UFileMediaSource>();
    Source->SetFilePath(TEXT("/Game/RenderOutput/sequence.####.exr"));
    
    MediaPlayer->OpenSource(Source);
    MediaPlayer->Play();
}
```

### 进阶用法：配置帧缓存和 Mipmap

```cpp
// ImgMedia 内部使用 LRU 缓存管理帧数据
// 通过引擎的 Media Framework 配置缓存行为
void AMyActor::ConfigureImageSequencePlayback()
{
    // 设置 MediaTexture 的 LOD 偏移（已废弃组件方式）
    // 现代方式：使用 MediaPlate 组件
    
    // 设置播放速率（负值为倒放）
    MediaPlayer->SetRate(-1.0f);
    
    // 跳转到指定时间
    FTimespan Duration = MediaPlayer->GetDuration();
    MediaPlayer->Seek(Duration / 2); // 跳到中间
}
```

## Demo 示例

```cpp
// MyImageSequencePlayer.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "FileMediaSource.h"
#include "MyImageSequencePlayer.generated.h"

UCLASS()
class AMyImageSequencePlayer : public AActor
{
    GENERATED_BODY()

public:
    AMyImageSequencePlayer();

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, Category = "Media")
    UFileMediaSource* MediaSource;

    UPROPERTY(EditAnywhere, Category = "Media")
    float PlayRate = 1.0f;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StartPlayback();

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopPlayback();

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyImageSequencePlayer.cpp
#include "MyImageSequencePlayer.h"
#include "MediaSoundComponent.h"

AMyImageSequencePlayer::AMyImageSequencePlayer()
{
    PrimaryActorTick.bCanEverTick = false;
    
    // 创建静态网格组件用于显示
    UStaticMeshComponent* Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Display"));
    RootComponent = Mesh;
}

void AMyImageSequencePlayer::BeginPlay()
{
    Super::BeginPlay();

    if (MediaPlayer && MediaSource)
    {
        // 打开图像序列
        bool bOpened = MediaPlayer->OpenSource(MediaSource);
        
        if (bOpened)
        {
            // 设置播放速率并开始播放
            MediaPlayer->SetRate(PlayRate);
            UE_LOG(LogTemp, Log, TEXT("Image sequence playback started"));
        }
    }
}

void AMyImageSequencePlayer::StartPlayback()
{
    if (MediaPlayer)
    {
        MediaPlayer->SetRate(FMath::Abs(PlayRate));
    }
}

void AMyImageSequencePlayer::StopPlayback()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenExrWrapper` | OpenEXR 库封装，提供 EXR 文件读写能力 |
| `ExrReaderGpu` | GPU 加速 EXR 解码，依赖 `OpenExrWrapper` |
| `UnrealEd` | 编辑器集成（仅 ImgMedia 主模块依赖） |
| `MediaAssets` | UE 媒体框架资产类（MediaPlayer、MediaTexture 等） |
| `MediaUtils` | 媒体框架工具类（采样队列、时间源等） |

> ImgMedia 的核心依赖是 `OpenExrWrapper` 和 `MediaAssets`，这些是其区别于其他 Media Player 插件的关键模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `edcd0d53` | [ImgMedia] refresh single-frame sequences on tile visibility changes | 单帧序列在瓦片可见性变化时自动刷新 |
| 2026-05-26 | `cf292c45` | [ImgMedia] Use AR-constrained view rect for tile mip selection | 使用 AR 约束的视口矩形来选择瓦片 Mipmap 级别 |
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened ana | 修复 ImgMedia 和 NDI 播放器发出错误的 SourceOpened 分析事件 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和捕获设备添加额外的引擎分析信息 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 在关卡编辑器窗口菜单中添加共享 Media 分类 |

### 维护评价

**✅ 活跃维护中**

- **创建时间**：2017 年，是 UE 媒体框架的核心组成部分
- **最近更新**：2026 年 5 月仍有功能性更新（Tile 流式加载、AR 支持），说明仍在积极开发
- **维护特征**：
  - 作为 Media Framework 的一部分，随引擎版本持续演进
  - 近期重点转向 Tile 可见性流式加载和 Mipmap 优化，适用于大分辨率图像序列
  - `ImgMediaPlaybackComponent` 已在 5.3 废弃，功能迁移到 MediaPlate
- **推荐使用**：✅ 强烈推荐。这是 UE 唯一的原生图像序列播放方案，且持续获得新功能。对于影视渲染预览和 Sequencer 集成场景是必需品。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)