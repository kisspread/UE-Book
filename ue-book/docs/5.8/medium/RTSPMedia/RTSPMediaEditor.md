# RTSP Media

> Real-time media streaming via the RTSP protocol

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体源资产） |
| 模块 | `RTSPMedia` (Runtime), `RTSPMediaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/RTSPMedia) | |

## 用途

该插件为 Unreal Engine 5 提供了基于 RTSP (Real Time Streaming Protocol) 协议的媒体播放能力。它实现了一个 `URtspMediaSource` 资产，用于配置 RTSP 流地址（URL），并配合引擎内置的媒体播放器框架，使开发者能够在项目中接收和播放来自网络摄像头、监控系统或其他支持 RTSP 协议的设备的实时视频流。其核心价值在于将外部实时视频源无缝集成到 UE5 的渲染管线和媒体框架中。

## 使用场景

- **安防监控系统**：在虚拟场景中实时显示来自实体监控摄像头的画面。
- **直播与远程呈现**：接入外部直播源或远程设备的视频流，用于虚拟制作或远程协作。
- **工业仿真与数字孪生**：将工厂、设备等现场的实时视频画面集成到数字孪生模型中。
- **媒体播放器应用**：构建能够播放网络实时流媒体的应用程序。

## 蓝图用法

该插件主要通过创建和配置 `URtspMediaSource` 资产来使用，其本身不暴露额外的蓝图节点。核心操作是在编辑器中完成资产创建和参数设置。

### 核心资产

| 资产类型 | 说明 | 创建方式 |
|---|---|---|
| `RtspMediaSource` | RTSP 媒体源资产，用于存储 RTSP 流地址。 | 内容浏览器 -> 右键 -> Media -> RTSP Media Source |

### 使用示例（蓝图描述）

1.  **创建媒体源**：在内容浏览器中右键，选择 `Media` -> `RTsp Media Source`，创建一个新的资产（例如 `RTSP_MyCamera`）。
2.  **配置 URL**：选中创建的 `RTSP_MyCamera` 资产，在细节面板中设置 `Url` 属性为你的 RTSP 流地址（例如 `rtsp://192.168.1.100:554/stream`）。
3.  **在媒体播放器中使用**：创建一个 `MediaPlayer` 资产，在其“源”设置中，将“媒体源”指定为上一步创建的 `RTSP_MyCamera`。
4.  **在场景中显示**：将 `MediaPlayer` 应用到 `MediaTexture`，再将 `MediaTexture` 作为材质的纹理采样器，最终应用到场景中的网格体或 UI 控件上。

## C++ 用法

### 头文件引入

```cpp
#include "RtspMediaSource.h"
```

### 基本用法

在 C++ 中，你可以动态创建和配置 `URtspMediaSource` 对象。

```cpp
// 假设在某个 Actor 或 Subsystem 中
#include "RtspMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"

// 创建 RTSP 媒体源
URtspMediaSource* RtspSource = NewObject<URtspMediaSource>(GetTransientPackage(), TEXT("MyRTSPSource"));
RtspSource->SetUrl(TEXT("rtsp://your.camera.ip:port/path"));

// 创建媒体播放器并打开源
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>(GetTransientPackage(), TEXT("MyMediaPlayer"));
if (MediaPlayer->OpenSource(RtspSource))
{
    // 媒体源已成功打开，可以开始播放
    MediaPlayer->Play();
}

// （可选）将 MediaPlayer 关联到 MediaTexture 以用于渲染
UMediaTexture* MediaTexture = NewObject<UMediaTexture>(GetTransientPackage(), TEXT("MyMediaTexture"));
MediaTexture->SetMediaPlayer(MediaPlayer);
```

### 进阶用法

结合媒体播放器的事件委托来处理播放状态变化。

```cpp
// 绑定媒体打开完成事件
MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyActor::HandleMediaOpened);
MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &AMyActor::HandleMediaOpenFailed);

void AMyActor::HandleMediaOpened(const FString& OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("RTSP stream opened: %s"), *OpenedUrl);
    // 可以在此处安全地获取视频尺寸等信息
    FIntPoint VideoSize = MediaPlayer->GetVideoTrackDimensions(0, 0);
}

void AMyActor::HandleMediaOpenFailed(const FString& FailedUrl)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open RTSP stream: %s"), *FailedUrl);
    // 处理连接失败，例如重试或提示用户
}
```

## Demo 示例

一个最小的 Actor 示例，用于在 BeginPlay 时打开一个 RTSP 流。

**MyRtspPlayerActor.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyRtspPlayerActor.generated.h"

class UMediaPlayer;
class UMediaTexture;
class URtspMediaSource;

UCLASS()
class AMyRtspPlayerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRtspPlayerActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(Transient)
    TObjectPtr<URtspMediaSource> RtspSource;

    UPROPERTY(Transient)
    TObjectPtr<UMediaPlayer> MediaPlayer;

    UPROPERTY(Transient)
    TObjectPtr<UMediaTexture> MediaTexture;

    UPROPERTY(EditAnywhere, Category = "RTSP")
    FString StreamUrl = TEXT("rtsp://example.com/live/stream");
};
```

**MyRtspPlayerActor.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyRtspPlayerActor.h"
#include "RtspMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"

AMyRtspPlayerActor::AMyRtspPlayerActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyRtspPlayerActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建媒体资产
    RtspSource = NewObject<URtspMediaSource>(this, TEXT("RTSPSource"));
    RtspSource->SetUrl(StreamUrl);

    MediaPlayer = NewObject<UMediaPlayer>(this, TEXT("MediaPlayer"));
    MediaTexture = NewObject<UMediaTexture>(this, TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);

    // 打开流
    if (MediaPlayer->OpenSource(RtspSource))
    {
        UE_LOG(LogTemp, Log, TEXT("Attempting to open RTSP stream: %s"), *StreamUrl);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initiate RTSP stream open."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | 提供底层的媒体解码能力，用于解码 RTSP 流中的音视频数据。 |
| `MediaIOFramework` | 提供媒体输入/输出的基础框架和接口。 |
| `MediaPlayerEditor` | 提供编辑器内媒体播放器资产的编辑功能。 |

## 维护状态

### 近期更新

由于插件创建时间非常近（2026-03-20），且未提供具体的 Git 提交历史，无法列出近期更新记录。可以推断该插件处于初始发布阶段。

### 维护评价

- **创建时间**：2026年3月，是一个非常新的插件。
- **实验性状态**：`.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明这是一个实验性功能，API 和功能可能不稳定，未来版本可能发生重大变更。
- **维护活跃度**：作为新发布的实验性插件，预计会由 Epic Games 进行初期维护和迭代，但长期稳定性未知。
- **推荐使用**：**谨慎使用**。适用于原型开发、内部测试或对稳定性要求不高的项目。不建议在需要长期稳定支持的生产项目中作为核心功能依赖。使用前请评估其与目标平台和 UE 版本的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/RTSPMedia)
- 官方文档：暂无（`.uplugin` 中未提供 `DocsURL`）