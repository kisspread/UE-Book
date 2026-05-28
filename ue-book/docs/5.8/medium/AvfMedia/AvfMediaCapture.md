# AVF Media Player

> Implements a media player using Apple AV Foundation.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | AVF 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvfMedia` (Runtime), `AvfMediaCapture` (Runtime), `AvfMediaEditor` (Editor), `AvfMediaFactory` (Editor/Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia) | |

## 用途

AvfMedia 是 Unreal Engine 媒体框架（Media Framework）在 Apple 平台上的底层实现插件，基于 Apple AV Foundation 框架提供音视频播放和采集能力。

该插件解决的核心问题是：**让 UE5 在 macOS、iOS 和 tvOS 上能够播放和采集媒体内容**。它封装了 AVFoundation 的 `AVPlayer`、`AVCaptureSession` 等原生 API，以 UE 媒体框架标准接口（`IMediaPlayer`、`IMediaTracks`、`IMediaControls` 等）暴露给引擎上层。

插件由四个模块组成：

- **AvfMedia**：核心播放器实现，基于 AVPlayer 处理文件播放和流媒体
- **AvfMediaCapture**：摄像头/麦克风采集，基于 AVCaptureSession 处理实时视频/音频捕获
- **AvfMediaEditor**：编辑器内的媒体资产预览支持
- **AvfMediaFactory**：媒体播放器工厂，负责根据 URL 协议和文件格式自动选择 AVF 播放器

## 使用场景

- 你需要在 **iOS / macOS / tvOS** 上播放视频文件（MP4、MOV 等） → 引擎会自动使用 AvfMedia
- 你需要在 iOS / macOS 上通过 **摄像头采集** 实时画面 → 使用 AvfMediaCapture 提供的 capture 协议
- 你需要在编辑器中 **预览** Apple 平台的媒体资产 → AvfMediaEditor 处理编辑器集成
- 你使用标准的 `UMediaPlayer` / `UMediaTexture` 蓝图工作流 → 底层自动路由到此插件

> **注意**：此插件默认启用，但仅在 Apple 平台（Mac/iOS/tvOS）上激活。Windows/Linux 上不生效。

## 蓝图用法

AvfMedia 是底层媒体播放器实现，不直接暴露自定义蓝图节点。所有交互通过 UE 媒体框架的标准蓝图 API 完成：

### 核心节点（标准媒体框架）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` / `Open Url` | 打开媒体源 | `UMediaPlayer` |
| `Play` / `Pause` / `Stop` | 播放控制 | `UMediaPlayer` |
| `Set Rate` | 设置播放速率 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间 | `UMediaPlayer` |
| `Set Looping` | 设置循环播放 | `UMediaPlayer` |
| `Get Duration` | 获取总时长 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1. 在场景中放置 `MediaSoundComponent` 和 `MediaTexture`
2. 创建 `MediaPlayer` 资产，格式选择支持 AVFoundation 的格式
3. 在蓝图中调用 `OpenUrl`，传入文件路径（如 `file:///path/to/video.mp4`）
4. 连接 `OnMediaOpened` 事件后调用 `Play`
5. 将 `MediaTexture` 赋给材质，将 `MediaPlayer` 赋给 `MediaSoundComponent`

引擎会自动使用 AvfMedia 播放器处理 Apple 平台的媒体内容。

## C++ 用法

AvfMediaCapture 模块通过媒体框架的自定义 URL 协议提供摄像头采集能力。

### 头文件引入

```cpp
#include "IMediaPlayer.h"
#include "IMediaTracks.h"
#include "IMediaControls.h"
#include "IMediaCache.h"
#include "IMediaView.h"
```

### 基本用法 — 通过媒体框架访问采集设备

AvfMediaCapture 注册了自定义的 capture 协议（如 `capture://`），可以通过标准媒体播放器接口打开：

```cpp
// 通过 UMediaPlayer 打开摄像头采集（底层会创建 FAvfMediaCapturePlayer）
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();

// 使用 capture:// 协议 + 设备 ID 打开采集会话
FString CaptureUrl = TEXT("capture://摄像头设备ID");
if (MediaPlayer->OpenUrl(CaptureUrl))
{
    UE_LOG(LogTemp, Log, TEXT("Capture session started"));
}
```

### 进阶用法 — 直接操作采集播放器

`FAvfMediaCapturePlayer` 实现了完整的媒体接口族，可以直接控制采集参数：

```cpp
// 获取采集播放器的轨道信息（来源: AvfMediaCapturePlayer.h）
IMediaTracks& Tracks = CapturePlayer->GetTracks();

// 查询音频轨道数量
int32 NumAudioTracks = Tracks.GetNumTracks(EMediaTrackType::Audio);
int32 NumVideoTracks = Tracks.GetNumTracks(EMediaTrackType::Video);

// 获取视频格式信息
FMediaVideoTrackFormat VideoFormat;
if (Tracks.GetVideoTrackFormat(0, 0, VideoFormat))
{
    UE_LOG(LogTemp, Log, TEXT("Resolution: %dx%d"), 
           VideoFormat.Dimensions.X, VideoFormat.Dimensions.Y);
}

// 控制采集状态
IMediaControls& Controls = CapturePlayer->GetControls();
EMediaState State = Controls.GetState();  // Playing/Paused/Stopped
```

## Demo 示例

一个最小的摄像头采集访问示例：

```cpp
// MyCaptureActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MyCaptureActor.generated.h"

UCLASS()
class AMyCaptureActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCaptureActor();

    UPROPERTY(EditAnywhere, Category = "Capture")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = "Capture")
    UMediaTexture* MediaTexture;

    UFUNCTION(BlueprintCallable, Category = "Capture")
    void StartCapture(const FString& DeviceUrl);

    UFUNCTION(BlueprintCallable, Category = "Capture")  
    void StopCapture();

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);
};
```

```cpp
// MyCaptureActor.cpp
#include "MyCaptureActor.h"

AMyCaptureActor::AMyCaptureActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MediaPlayer = nullptr;
    MediaTexture = nullptr;
}

void AMyCaptureActor::BeginPlay()
{
    Super::BeginPlay();
    
    if (MediaPlayer)
    {
        MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyCaptureActor::OnMediaOpened);
    }
}

void AMyCaptureActor::StartCapture(const FString& DeviceUrl)
{
    if (!MediaPlayer) return;
    
    // 使用 capture:// 协议打开设备
    // 底层由 AvfMediaCapturePlayer 创建 AVCaptureSession
    MediaPlayer->OpenUrl(DeviceUrl);
}

void AMyCaptureActor::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Capture started: %s"), *OpenedUrl);
    
    // 绑定 MediaTexture 到播放器以显示采集画面
    if (MediaTexture)
    {
        MediaTexture->SetMediaPlayer(MediaPlayer);
    }
}

void AMyCaptureActor::StopCapture()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}
```

## 模块依赖

由于未提供 Build.cs 完整内容，基于插件性质推断，典型依赖如下：

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 媒体框架工具类（FMediaSamples、采样池等） |
| `MediaAssets` | UMediaPlayer/UMediaTexture 等资产类型 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> AvfMediaCapture 模块额外依赖 Apple 原生框架：`AVFoundation`、`CoreMedia`、`CoreVideo`、`Metal`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `1951db93` | [AvfMedia] Default H.264 file playback to BGRA decode and provide CPU accessible buffer for media fi | H.264 播放默认使用 BGRA 解码，提供 CPU 可访问缓冲区 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复不可达代码警告 |
| 2026-04-01 | `39223292` | [AvfMedia] Provide CPU buffer alongside GPU texture when using FAvfMediaCapturePlayer | 采集播放器同时提供 CPU 缓冲区和 GPU 纹理 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复打印语句 |

### 维护评价

- **创建时间**：2014 年，是 UE4 早期 Media Framework 的一部分，已有约 12 年历史
- **活跃程度**：近期更新频繁（2026 年 2-5 月有多次提交），仍在积极维护中
- **更新方向**：主要集中在性能优化（CPU/GPU 缓冲区改进、BGRA 解码默认值）和代码质量（警告修复、日志迁移）
- **平台限制**：仅 Apple 平台可用（Mac/iOS/tvOS），采集功能仅限 Mac/iOS
- **推荐度**：✅ **推荐使用**。作为 Apple 平台唯一可用的原生媒体后端，在 Mac/iOS 开发中是必不可少的。维护状态良好，近期有实质性功能改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)