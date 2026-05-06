# MotionJPEG Decoder for Electra

> Implements video playback of MotionJPEG encoded video files

| 属性 | 值 |
|---|---|
| 中文名 | MJPEG 解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MJPEGDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MJPEGDecoderElectra) | |

## 用途

该插件为 **Electra 媒体框架** 添加了 MotionJPEG（MJPEG）视频编解码支持。MJPEG 是一种将视频帧以独立 JPEG 图像进行压缩的格式，常用于监控摄像头、医学影像、老旧视频编辑软件等场景。

Electra 是 UE5 的现代媒体播放系统（替代 MediaFramework 中的 FMediaPlayer），通过注册编解码器来播放不同格式。此插件在 Electra 内部注册了一个 MJPEG 解码器，使 `MediaPlayer` 能够直接播放 `.avi`、`.mov` 等容器中的 MJPEG 视频流，无需额外转码。

## 使用场景

- **监控回放**：接入 IP 摄像头生成的 MJPEG 流或录制文件。
- **医学影像播放**：DICOM 格式常使用 MJPEG 压缩，可在引擎内直接渲染。
- **兼容旧素材**：处理早期摄像机或视频采集卡输出的 MJPEG 文件。
- **低延迟流媒体**：某些直播推流采用 MJPEG（帧独立解码，丢帧不影响后续帧）。

## 蓝图用法

该插件**不暴露**任何蓝图可调用函数或可配置属性。它作为 Electra 的底层解码器自动注册。

### 使用方式（蓝图）

1. 在项目设置中**启用**此插件（默认禁用）。
2. 创建一个 `MediaPlayer` 和 `MediaTexture` / `FileMediaSource` 资源。
3. 将 `MediaPlayer` 的 Source 设置为待播放的 MJPEG 文件（如 `.avi`、`.mov`）。
4. 使用 `MediaPlayer->Open Source` 节点打开文件，若文件内视频编码为 MotionJPEG 且容器受支持（如 AVI），解码将自动使用此插件。

## C++ 用法

### 头文件引入

```cpp
#include "MJPEGDecoder/ElectraMediaMJPEGDecoder.h"
```

### 基本用法

通常情况下，插件会在引擎启动时自动完成注册（`StartupModule` 中调用 `FElectraMediaMJPEGDecoder::Startup()`），开发者无需手动调用。

**手动初始化与关闭**（仅在需要精确控制生命周期时使用）：

```cpp
// 注册解码器
FElectraMediaMJPEGDecoder::Startup();

// ... 播放 MJPEG 视频 ...

// 注销解码器（通常在模块关闭时自动调用）
FElectraMediaMJPEGDecoder::Shutdown();
```

### 进阶用法

与 Electra 媒体框架配合，创建并播放 MJPEG 媒体源：

```cpp
// 文件路径
FString FilePath = FPaths::ProjectContentDir() / TEXT("Videos/MyMJPEGFile.avi");

// 创建 MediaPlayer（建议从 Asset 加载，此处为运行时创建示例）
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->SetFilePath(FilePath);

// 打开媒体源
MediaPlayer->OpenSource(MediaSource);

// 播放
MediaPlayer->Play();
```

此代码将自动触发 Electra 内部的解码器选择，MJPEG 解码由本插件提供。

## Demo 示例

一个最小的 C++ 示例，在关卡中加载并播放 MotionJPEG 视频。

**MyVideoActor.h**:

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "FileMediaSource.h"
#include "MyVideoActor.generated.h"

UCLASS()
class AMyVideoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyVideoActor();

    UFUNCTION(BlueprintCallable, Category = "Video")
    void PlayMJPEG(const FString& FilePath);

protected:
    UPROPERTY(VisibleAnywhere, Category = "Media")
    UMediaPlayer* MediaPlayer;
};
```

**MyVideoActor.cpp**:

```cpp
#include "MyVideoActor.h"

AMyVideoActor::AMyVideoActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
}

void AMyVideoActor::PlayMJPEG(const FString& FilePath)
{
    // 创建文件媒体源（也可用蓝图路径直接引用）
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->FilePath = FilePath;

    // 仅支持 MJPEG 编码的 AVI/MOV 文件
    MediaPlayer->OpenSource(MediaSource);
    MediaPlayer->Play();
}
```

使用时，在蓝图或 C++ 中调用 `PlayMJPEG("/Game/Videos/MyClip.avi")` 即可播放。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | 必须依赖的编解码器基础框架，此插件向其注册 MJPEG 解码器 |

**其他注意**：插件仅支持 **Win64** 平台（`.uplugin` 中 `SupportedTargetPlatforms` 配置），且不可用于 Dedicated Server。

## 维护状态

### 近期更新

- **2025-08-07** `a0902b75` — ElectraDecoders: Added an MJPEG decoder for Electra (初始提交)

### 维护评价

- **创建时间**：2025-08-07（距今约 2 个月）
- **活跃度**：初始可用版本，暂未发现后续功能更新或修复
- **推荐使用**：插件处于早期阶段，功能单一，且仅限 Win64 平台。如果项目确实需要 Electra 播放 MJPEG 视频，可以启用；否则建议使用传统 Media Framework + WmfMedia（支持 MJPEG 解码）。由于该插件依赖 ElectraCodecs 且较新，可能在未来 UE 版本中持续迭代，目前可正常使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MJPEGDecoderElectra)