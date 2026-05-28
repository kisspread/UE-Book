# HAP Media

> Implements video playback of the HAP Codec. HAP is a high performance, high resolution codec that runs on the GPU.

| 属性 | 值 |
|---|---|
| 中文名 | HAP解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HAPMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-20 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HAPMedia) | |

## 用途

该插件为虚幻引擎的媒体播放器框架提供了 HAP 视频编解码器的解码支持。HAP（High Performance）是一种高性能、高分辨率的视频编解码器，其核心特点是利用 GPU 进行解码，从而减轻 CPU 的负担。此插件通过 Windows Media Foundation (WMF) 框架集成，使得 UE5 能够播放使用 HAP 编码的视频文件，特别适用于需要实时播放超高分辨率或大量视频墙的媒体装置、展览或演出场景。

## 使用场景

- 你正在制作一个多媒体装置、沉浸式空间或现场演出，需要同时播放多个高分辨率（如 4K/8K）的视频。
- 你的视频源采用了 HAP 编码（通常使用 HAP Alpha 或 HAP Q 格式），以确保在实时播放时获得最佳性能和最低延迟。
- 你的目标平台是 Windows (Win64)，并且正在使用 WmfMedia 作为基础媒体播放器。

## 蓝图用法

该插件没有提供额外的蓝图节点。它的作用是扩展底层 WmfMedia 播放器的能力，使引擎能够识别并播放 HAP 编码的视频文件。因此，在蓝图中，你仍然使用标准的 `Media Player` 资产和 `Open Source` 等节点来播放 HAP 视频，引擎会自动调用此插件进行解码。

## C++ 用法

此插件没有提供面向用户的公开 C++ API。它的主要实现是 `WmfMediaHAPDecoder` 类，该类作为 WMF Media Foundation Transform (MFT) 与 UE 的 WmfMedia 模块之间的桥梁，在内部被自动调用。

### 头文件引入

```cpp
// 通常不需要直接引入此插件的头文件。
// 使用媒体播放器相关的标准头文件即可。
#include "MediaPlayer.h"
#include "MediaSource.h"
```

### 基本用法

该插件的使用完全是透明的。开发者只需通过标准的媒体播放器接口加载并播放 HAP 视频文件。解码过程由插件在后台完成。

```cpp
// 假设你已经有一个 UMediaPlayer* MediaPlayer 和一个指向 HAP 视频文件的 FMediaSource* HAPMediaSource

// 在 C++ 中播放 HAP 视频
if (MediaPlayer && HAPMediaSource)
{
    // 打开源，引擎会自动选择合适的解码器（对于 HAP 文件，会使用此插件的解码器）
    MediaPlayer->OpenSource(HAPMediaSource);
    MediaPlayer->Play();
}
```
*注：此示例展示了标准的媒体播放器用法，HAP 解码器将在后台被 WmfMedia 模块自动加载和使用。*

### 进阶用法

由于该插件没有暴露高级 API，进阶用法主要涉及对媒体播放过程的监控和事件处理，这同样使用标准的 `UMediaPlayer` 委托。

```cpp
// 绑定媒体打开完成的事件
MediaPlayer->OnMediaOpened.AddDynamic(this, &UMyClass::HandleMediaOpened);
MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &UMyClass::HandleMediaOpenFailed);

void UMyClass::HandleMediaOpened(const FString& OpenedUrl)
{
    // HAP 视频已成功用正确的解码器打开
    UE_LOG(LogTemp, Log, TEXT("HAP Media opened successfully: %s"), *OpenedUrl);
    // 可以在此处获取视频尺寸、时长等信息
}

void UMyClass::HandleMediaOpenFailed(const FString& FailedUrl)
{
    // 可能由于解码器不支持或文件损坏而失败
    UE_LOG(LogTemp, Error, TEXT("Failed to open HAP Media: %s"), *FailedUrl);
}
```

## Demo 示例

该插件通常不被单独使用，而是作为 `WmfMedia` 插件功能的一部分。以下是一个概念性的使用示例。

```cpp
// MyMediaPlayerComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MyMediaPlayerComponent.generated.h"

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class UMyMediaPlayerComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UMyMediaPlayerComponent();

    // 要播放的 HAP 视频源资产
    UPROPERTY(EditAnywhere, Category="Media")
    UMediaSource* HAPVideoSource;

    // 媒体播放器实例
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Media")
    UMediaPlayer* MediaPlayer;

    UFUNCTION(BlueprintCallable, Category="Media")
    void PlayHAPVideo();

protected:
    virtual void BeginPlay() override;

private:
    UFUNCTION()
    void OnVideoOpened(const FString& URL);
};

// MyMediaPlayerComponent.cpp
#include "MyMediaPlayerComponent.h"
#include "MediaPlayer.h"

UMyMediaPlayerComponent::UMyMediaPlayerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
}

void UMyMediaPlayerComponent::BeginPlay()
{
    Super::BeginPlay();
    if (MediaPlayer)
    {
        MediaPlayer->OnMediaOpened.AddDynamic(this, &UMyMediaPlayerComponent::OnVideoOpened);
    }
}

void UMyMediaPlayerComponent::PlayHAPVideo()
{
    if (MediaPlayer && HAPVideoSource)
    {
        MediaPlayer->OpenSource(HAPVideoSource);
    }
}

void UMyMediaPlayerComponent::OnVideoOpened(const FString& URL)
{
    // 视频已打开，如果设置了自动播放，它会开始播放。
    // MediaPlayer->Play(); // 根据需要调用
    UE_LOG(LogTemp, Display, TEXT("HAP Video Playback Started: %s"), *URL);
}
```

## 模块依赖

该插件自身没有公开的模块依赖供你的项目直接引用。但它的正常工作依赖于 `WmfMedia` 插件（已在 .uplugin 中声明）。

| 模块 | 用途 |
|---|---|
| `WmfMedia` | 提供基于 Windows Media Foundation 的媒体播放器框架，HAPMedia 是此框架的一个编解码器插件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式的日志宏迁移至新格式，属于代码现代化维护。 |
| 2023-04-03 | `ebabab67` | Electra: Copy-up from codec refactor task stream | 从 Electra 播放器重构任务中同步代码，可能涉及底层媒体框架调整。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件的外部链接至HTTPS协议。 |
| 2022-08-15 | `a2d38616` | Fixing up DX12 playback with WMFmediaPlayer (H264/5, HAP, ProRes) | 修复在 DX12 下使用 WMF 播放器播放 HAP 等视频的问题。 |
| 2021-11-29 | `9e51a331` | WmfMedia: HAP now uses external buffers. | 优化 HAP 解码器，改为使用外部缓冲区以提升性能。 |

### 维护评价

该插件自2019年创建以来，持续得到维护。最近的更新（2026年）主要是代码清理和现代化，说明它仍被纳入引擎的更新周期中。实质性功能更新（如性能优化、平台兼容性修复）集中在2021-2023年。作为一个依赖特定平台（Win64）和外部框架（WMF）的专用解码器插件，其更新频率符合预期。**目前处于“维护中”状态，推荐在需要 GPU 解码 HAP 视频的 Win64 项目中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HAPMedia)
- [官方文档](https://epicgames.com)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HAPMedia) (无公开的独立测试用例)