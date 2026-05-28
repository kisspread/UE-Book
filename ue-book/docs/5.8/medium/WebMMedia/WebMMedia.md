# WebM Video Player

> A simulated cable component.

| 属性 | 值 |
|---|---|
| 中文名 | WebM视频播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebMMedia` (RuntimeNoCommandlet), `WebMMediaEditor` (Runtime), `WebMMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-12 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia) | |

## 用途

WebMMedia 是一个用于播放 WebM 格式媒体文件的插件。WebM 是一种开放的媒体文件格式，使用 VP8 或 VP9 视频编码和 Vorbis 或 Opus 音频编码。该插件为 Unreal Engine 的媒体框架（Media Framework）提供了 WebM 格式的解码和播放支持，使开发者能够在 Windows 和 Linux 平台上播放 WebM 视频文件。

该插件的存在解决了在 Unreal Engine 项目中播放 WebM 格式视频的需求。WebM 格式因其开放性和高效的压缩而被广泛应用于网络视频，特别是在需要避免专利限制或使用开源技术栈的场景下。

## 使用场景

- 你需要播放来自网络或本地的 WebM 格式视频文件。
- 你的项目需要支持开放、免版税的视频格式。
- 你在开发 Linux 平台项目，需要一种可靠的视频播放方案。
- 你需要播放 VP8/VP9 编码的视频，特别是 10-bit VP9 视频。

## 蓝图用法

该插件主要通过 Unreal Engine 的媒体框架（Media Framework）进行集成，不直接暴露蓝图节点。播放 WebM 视频的标准方法是使用 `MediaPlayer` 和 `MediaTexture` 资产。

### 核心节点

由于该插件是媒体播放器的后端实现，其主要通过 Media Framework 的标准接口工作，没有直接暴露独特的蓝图节点。开发者使用 `MediaPlayer` 蓝图类来控制播放。

### 使用示例（蓝图描述）

1.  **创建资产**:
    *   在内容浏览器中右键，创建 `Media` -> `MediaPlayer` 资产。
    *   在内容浏览器中右键，创建 `Media` -> `MediaTexture` 资产。
    *   在内容浏览器中右键，创建 `Material` 资产，并将 `MediaTexture` 作为纹理输入。

2.  **配置播放器**:
    *   双击打开 `MediaPlayer` 资产。
    *   确保 `Media Player Class` 设置为 `WebMMediaPlayer` (通过 `WebMMediaFactory` 自动选择)。
    *   将 `Media Texture` 属性设置为上一步创建的 `MediaTexture`。

3.  **在蓝图中控制播放**:
    *   在蓝图中，添加一个 `MediaPlayer` 变量，并指向您创建的资产。
    *   使用 `Open Source` 或 `Open URL` 节点打开一个 `.webm` 文件。
    *   使用 `Play`、`Pause`、`Seek` 等节点控制播放。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
#include "MediaPlaylist.h"
```

### 基本用法

以下示例展示了如何在 C++ 中播放一个本地 WebM 文件。

```cpp
// 假设您已经通过编辑器创建了 UMediaPlayer 和 UMediaTexture 资产。
// 在代码中引用它们。

UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
UMediaPlayer* MyMediaPlayer;

UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
UMediaTexture* MyMediaTexture;

void AMyActor::PlayWebMVideo()
{
    if (MyMediaPlayer && MyMediaPlayer->OpenUrl(TEXT("file:///C:/Videos/MyVideo.webm")))
    {
        // 设置媒体纹理到材质（假设您有一个动态材质实例）
        UMaterialInstanceDynamic* DynMaterial = UMaterialInstanceDynamic::Create(MyMaterial, this);
        DynMaterial->SetTextureParameterValue(TEXT("VideoTexture"), MyMediaTexture);
        MyMeshComponent->SetMaterial(0, DynMaterial);

        // 开始播放
        MyMediaPlayer->Play();
    }
}
```

### 进阶用法

使用 `FWebMContainer` 类直接解析 WebM 容器，获取更底层的控制。

```cpp
#include "WebMContainer.h"
#include "WebMMediaFrame.h"

void AMyActor::AnalyzeWebMFile(const FString& FilePath)
{
    FWebMContainer Container;
    if (Container.Open(FilePath))
    {
        // 获取视频和音频轨道信息
        FWebMVideoTrackInfo VideoInfo = Container.GetCurrentVideoTrackInfo();
        FWebMAudioTrackInfo AudioInfo = Container.GetCurrentAudioTrackInfo();

        if (VideoInfo.bIsValid)
        {
            UE_LOG(LogTemp, Log, TEXT("Video Codec: %s"), ANSI_TO_TCHAR(VideoInfo.CodecName));
        }
        if (AudioInfo.bIsValid)
        {
            UE_LOG(LogTemp, Log, TEXT("Audio Codec: %s, Sample Rate: %d, Channels: %d"),
                   ANSI_TO_TCHAR(AudioInfo.CodecName), AudioInfo.SampleRate, AudioInfo.NumOfChannels);
        }

        // 读取前 5 秒的帧数据
        TArray<TSharedPtr<FWebMFrame, ESPMode::ThreadSafe>> AudioFrames;
        TArray<TSharedPtr<FWebMFrame, ESPMode::ThreadSafe>> VideoFrames;
        Container.ReadFrames(FTimespan::FromSeconds(5.0), AudioFrames, VideoFrames);

        UE_LOG(LogTemp, Log, TEXT("Read %d video frames and %d audio frames."), VideoFrames.Num(), AudioFrames.Num());
    }
}
```

## Demo 示例

一个最小的 Actor，用于在场景中播放 WebM 视频到一个平面网格上。

**WebMPlayerActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WebMPlayerActor.generated.h"

class UMediaPlayer;
class UMediaTexture;
class UMaterialInterface;
class UMaterialInstanceDynamic;
class UStaticMeshComponent;

UCLASS()
class MYPROJECT_API AWebMPlayerActor : public AActor
{
    GENERATED_BODY()

public:
    AWebMPlayerActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:
    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaSource* MediaSource;

    UPROPERTY(EditAnywhere, Category = "Media")
    UMaterialInterface* BaseMaterial;

private:
    UPROPERTY()
    UMaterialInstanceDynamic* DynamicMaterial;

    UPROPERTY()
    UStaticMeshComponent* ScreenMesh;
};
```

**WebMPlayerActor.cpp**
```cpp
#include "WebMPlayerActor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

AWebMPlayerActor::AWebMPlayerActor()
{
    PrimaryActorTick.bCanEverTick = false;

    ScreenMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Screen"));
    RootComponent = ScreenMesh;
    // 确保你的项目中有一个平面网格体（例如 Engine/Content/BasicShapes/Plane）
    static ConstructorHelpers::FObjectFinder<UStaticMesh> PlaneMesh(TEXT("/Engine/BasicShapes/Plane"));
    if (PlaneMesh.Succeeded())
    {
        ScreenMesh->SetStaticMesh(PlaneMesh.Object);
    }
}

void AWebMPlayerActor::BeginPlay()
{
    Super::BeginPlay();

    if (BaseMaterial)
    {
        DynamicMaterial = UMaterialInstanceDynamic::Create(BaseMaterial, this);
        if (DynamicMaterial && MediaTexture)
        {
            DynamicMaterial->SetTextureParameterValue(TEXT("VideoTexture"), MediaTexture);
            ScreenMesh->SetMaterial(0, DynamicMaterial);
        }
    }

    if (MediaPlayer && MediaSource)
    {
        // 绑定播放状态变化事件
        MediaPlayer->OnMediaEvent.AddDynamic(this, &AWebMPlayerActor::OnMediaEvent);
        MediaPlayer->OpenSource(MediaSource);
    }
}

void AWebMPlayerActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
        MediaPlayer->OnMediaEvent.RemoveDynamic(this, &AWebMPlayerActor::OnMediaEvent);
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LibVpx` | VP8/VP9 视频编解码库，是解码视频流的核心依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `6fa2f4c5` | WebMMedia: Fixed video full range yuv offsets | 修复了 WebM 视频在满幅度 YUV 模式下的偏移量问题 |
| 2026-04-21 | `f9163c8f` | WebMMedia: Added support for 10 bit VP9 files; fixed an issue where images were overwritten before t | 新增 10-bit VP9 文件支持；修复图像在解码完成前被覆盖的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF |
| 2026-02-11 | `2639e40b` | Updated libvpx to 1.15.1, did not copy the duplicated headers layout from 1.14.1 | 将 libvpx 库更新至 1.15.1 版本 |
| 2026-01-22 | `0bfe789b` | WebMMedia: Rewrite of the plugin | WebMMedia 插件进行了重写 |

### 维护评价

该插件创建于 2018 年，已有约 8 年历史。从最近的 Git 提交历史来看，**在 2026 年初进行了大规模重写**，并在之后持续修复 bug 和增加新功能（如 10-bit VP9 支持）。这表明该插件**仍在积极维护**，并且是 Epic Games 官方维护的模块。

尽管它被标记为实验性（`IsBetaVersion=true`）且默认未启用（`EnabledByDefault=false`），但其近期的活跃更新表明它是一个稳定且不断改进的功能。对于需要在 Windows 或 Linux 平台播放 WebM 视频的项目，这是一个可靠的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/media-framework-in-unreal-engine/)（Media Framework 通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia/Tests)