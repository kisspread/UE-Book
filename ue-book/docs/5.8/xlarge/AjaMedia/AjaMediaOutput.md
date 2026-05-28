# AJA Media Player - AjaMediaOutput

> Implements input and output using AJA Capture cards.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | AJA 媒体输出 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体输出配置资产、蓝图资产） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia) | |

## 用途

AjaMediaOutput 模块负责将 Unreal Engine 的视频、音频和辅助数据（Ancillary Data）通过 AJA 专业视频采集卡输出到 SDI/HDMI 信号。它基于 MediaIOCore 框架实现，将引擎渲染内容实时传输到专业广播设备。

这个模块解决的核心问题是：在虚拟制片（Virtual Production）、实时广播、演播室合成等场景中，需要将 UE 的渲染画面通过专业视频接口实时输出到外部设备（如切换台、录制设备、监视器等）。AJA 采集卡是广播行业常用的硬件设备，支持多种专业视频格式（SDI、HDMI 等）。

**AjaMediaOutput 模块**是整个插件中专门处理**输出方向**的模块，与 AjaMedia（输入）模块互为补充。

## 使用场景

- 你在做虚拟制片项目，需要将 UE 画面通过 SDI 输出到 LED 墙或切换台 → 使用 AJA Media Output
- 你需要将引擎画面录制到专业录像设备 → 配置 AJA Media Output 的帧抓取协议
- 你需要在广播场景中实时输出带时间码的专业视频信号 → 使用支持 Timecode 输出的 AJA 配置
- 你需要同时输出视频和音频到外部设备 → 配置音频输出参数
- 你需要同步多路输出（Genlock）→ 启用同步事件等待

## 蓝图用法

### 核心配置类 - UAjaMediaOutput

| 属性 | 说明 | 类型 |
|---|---|---|
| `OutputConfiguration` | 设备、端口和视频设置配置 | `FMediaIOOutputConfiguration` |
| `bStopOutputOnCardTimeout` | 超时时是否停止输出 | `bool` |
| `bOutputWithAutoCirculating` | 是否使用自动循环模式同步输出音频、辅助数据和视频 | `bool` |
| `TimecodeFormat` | 输出帧是否嵌入引擎时间码 | `EMediaIOTimecodeFormat` |
| `PixelFormat` | 设备内部使用的原生像素格式（8bit YUV 或 10bit YUV） | `EAjaMediaOutputPixelFormat` |
| `bOutputIn3GLevelB` | 是否将 3G Level A 转换为 Level B 输出 | `bool` |
| `bInvertKeyOutput` | 是否反转键信号输出 | `bool` |
| `bOutputAudio` | 是否输出音频 | `bool` |
| `AudioBufferSize` | 音频缓冲区大小（越大越稳定但延迟越高） | `int32` |
| `NumOutputAudioChannels` | 输出音频通道数（6/8/16） | `EAjaMediaOutputChannelConfiguration` |
| `AudioSampleRate` | 音频采样率 | `EAjaMediaOutputAudioSampleRate` |
| `bWaitForSyncEvent` | 是否等待垂直同步信号以维持 Genlock | `bool` |
| `bLogDropFrame` | 是否在丢帧时记录警告 | `bool` |
| `bEncodeTimecodeInTexel` | 是否将时间码烧录到像素中 | `bool` |
| `HDROptions` | HDR 元数据设置 | `FAjaMediaHDROptions` |

### 枚举类型

| 枚举 | 说明 | 值 |
|---|---|---|
| `EAjaMediaOutputPixelFormat` | 原生像素格式 | `PF_8BIT_YUV` (8bit YUV), `PF_10BIT_YUV` (10bit YUV) |
| `EAjaMediaOutputAudioSampleRate` | 音频采样率 | `SR_48k` (48000 Hz) |
| `EAjaMediaOutputChannelConfiguration` | 音频通道配置 | `CH_6` (6), `CH_8` (8), `CH_16` (16) |

### 帧抓取协议 - UAjaFrameGrabberProtocol

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MediaOutput` | 引用的 AJA 输出配置资产 | `UAjaFrameGrabberProtocol` |

### 使用示例（蓝图描述）

**基本视频输出设置：**
1. 在内容浏览器中右键 → 创建 → Media → Aja Media Output
2. 在详情面板中配置 `OutputConfiguration`：选择 AJA 设备、端口和视频格式
3. 设置 `PixelFormat` 为所需格式（8bit YUV 或 10bit YUV）
4. 根据需要启用 `bOutputAudio` 配置音频输出
5. 将此 Media Output 赋给 Media Capture 组件或蓝图节点

**时间码输出：**
1. 在 Media Output 配置中设置 `TimecodeFormat` 为所需格式
2. 如需 Genlock 同步，启用 `bWaitForSyncEvent`
3. 如需调试，可启用 `bEncodeTimecodeInTexel` 在画面上烧录时间码

## C++ 用法

### 头文件引入

```cpp
#include "AjaMediaOutput.h"
#include "AjaMediaCapture.h"
#include "AjaMediaFrameGrabberProtocol.h"
```

### 基本用法 - 创建媒体输出

```cpp
// 创建 AJA Media Output 对象
UAjaMediaOutput* MediaOutput = NewObject<UAjaMediaOutput>();

// 配置输出参数
MediaOutput->OutputConfiguration.MediaConnection.Device.DeviceName = TEXT("Corvid88");
MediaOutput->OutputConfiguration.MediaConnection.Port.PortIdentifier = 1;
MediaOutput->OutputConfiguration.MediaMode.VideoMode = EMediaIOVideoMode::Progressive_1080;
MediaOutput->PixelFormat = EAjaMediaOutputPixelFormat::PF_8BIT_YUV;
MediaOutput->bOutputAudio = true;
MediaOutput->bWaitForSyncEvent = true;
```

### 基本用法 - 创建媒体捕获

```cpp
// 创建媒体捕获实例
UMediaCapture* MediaCapture = MediaOutput->CreateMediaCapture();

// 开始捕获视口
FMediaCaptureOptions CaptureOptions;
MediaCapture->CaptureSceneViewport(FIntPoint(1920, 1080), CaptureOptions);

// 或捕获渲染目标
MediaCapture->CaptureTextureRenderTarget2D(RenderTarget, CaptureOptions);

// 停止捕获
MediaCapture->StopCapture(true);
```

### 进阶用法 - 自定义音频输出

```cpp
// 配置音频输出参数
MediaOutput->bOutputAudio = true;
MediaOutput->AudioBufferSize = 1024 * 10;  // 较大缓冲区，更稳定
MediaOutput->NumOutputAudioChannels = EAjaMediaOutputChannelConfiguration::CH_16;
MediaOutput->AudioSampleRate = EAjaMediaOutputAudioSampleRate::SR_48k;

// 创建捕获并关联音频设备
FAudioDeviceHandle AudioDevice = GEngine->GetMainAudioDevice();
MediaCapture->UpdateAudioDevice(AudioDevice);
```

## Demo 示例

### 基本 AJA 输出 Actor

```cpp
// AjaOutputActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AjaMediaOutput.h"
#include "AjaMediaCapture.h"
#include "AjaOutputActor.generated.h"

UCLASS(BlueprintType, Blueprintable)
class MYPROJECT_API AAjaOutputActor : public AActor
{
    GENERATED_BODY()

public:
    AAjaOutputActor();

    UPROPERTY(EditAnywhere, Category = "AJA Output")
    TObjectPtr<UAjaMediaOutput> MediaOutput;

    UFUNCTION(BlueprintCallable, Category = "AJA Output")
    void StartOutput();

    UFUNCTION(BlueprintCallable, Category = "AJA Output")
    void StopOutput();

private:
    UPROPERTY()
    TObjectPtr<UAjaMediaCapture> MediaCapture;
};
```

```cpp
// AjaOutputActor.cpp
#include "AjaOutputActor.h"

AAjaOutputActor::AAjaOutputActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MediaOutput = nullptr;
    MediaCapture = nullptr;
}

void AAjaOutputActor::StartOutput()
{
    if (!MediaOutput)
    {
        UE_LOG(LogTemp, Warning, TEXT("AJA Media Output is not configured"));
        return;
    }

    // 创建媒体捕获实例
    MediaCapture = Cast<UAjaMediaCapture>(MediaOutput->CreateMediaCapture());
    if (!MediaCapture)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create AJA Media Capture"));
        return;
    }

    // 获取主视口并开始捕获
    FMediaCaptureOptions Options;
    if (GEngine && GEngine->GameViewport)
    {
        TSharedPtr<FSceneViewport> Viewport = GEngine->GameViewport->GetGameViewport();
        MediaCapture->CaptureSceneViewport(Viewport, Options);
        UE_LOG(LogTemp, Log, TEXT("AJA Output started"));
    }
}

void AAjaOutputActor::StopOutput()
{
    if (MediaCapture && MediaCapture->IsCapturing())
    {
        MediaCapture->StopCapture(true);
        MediaCapture = nullptr;
        UE_LOG(LogTemp, Log, TEXT("AJA Output stopped"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 媒体 IO 核心框架，提供 MediaOutput/MediaCapture 基类 |
| `AjaCore` | AJA 设备底层 API 封装 |
| `MediaUtils` | 媒体工具函数 |
| `AudioMixer` | 音频混音器，用于音频输出捕获 |
| `GPUTextureTransfer` | GPU 纹理传输支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为 AJA 和 Blackmagic 卡的自动配置填充媒体配置信息 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和捕获添加额外的引擎分析信息 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 将虚拟制片资产迁移至不同资产分类 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 为具体的 UMediaSource 和 UMediaOutput 子类添加缺失的资产定义 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位格式说明符与 64 位参数不匹配的问题 |

### 维护评价

**活跃维护** - AJA Media Player 是一个成熟的专业广播/虚拟制片插件，由 Epic Games 官方维护。该插件自 2018 年创建以来持续更新，近期（2026 年）仍有频繁的功能性更新和 Bug 修复。插件专注于 Win64 平台的专业广播场景，与 Blackmagic Media 插件并列为 UE5 中两大专业视频采集卡支持方案。

**注意事项：**
- 仅支持 Win64 平台
- 默认未启用（`EnabledByDefault: false`），需要在插件设置中手动启用
- 需要安装 AJA 驱动程序和 AJA SDK
- 非实验性功能，可用于生产环境

**推荐使用：** 如果你的项目需要通过 AJA 采集卡进行专业视频输出，这是一个成熟可靠的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia)
- [AJA 官方文档](https://www.aja.com/)
- [UE 官方文档 - Media IO](https://docs.unrealengine.com/5.0/en-US/media-io-in-unreal-engine/)