# Blackmagic Media Player

> Implements input and output using Blackmagic Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | 黑魔法媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicCore` (Runtime), `BlackmagicMedia` (Runtime), `BlackmagicMediaEditor` (Runtime), `BlackmagicMediaFactory` (Runtime), `BlackmagicMediaOutput` (Runtime), `BlackmagicSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-06-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途

基于 Blackmagic Design 采集卡实现实时的视频/音频输入输出功能。`BlackmagicMediaOutput` 模块专注于**输出**方向，允许将 Unreal Engine 的渲染画面（视口/材质目标）和同步音频通过 SDI/HDMI 接口发送到广播级监视器、录机或播出系统。解决在虚拟制片、现场包装、演播室环境下对高质量、低延迟、帧同步的外部视频输出的需求。

## 使用场景

- 你在做一个实时虚拟制片系统，需要将引擎画面同步输出到 LED 大屏或视频切换台
- 你需要在演播室中将 UE 渲染的内容以广播标准格式（如 1080p50/59.94）输出到录像机
- 你需要输出带嵌入时间码和高质量音频的 SDI 信号用于后期制作
- 你希望通过 Blackmagic 输出卡获得精确的帧级同步和色彩精度

## 蓝图用法

`BlackmagicMediaOutput` 模块公开了可编辑的 `UBlackmagicMediaOutput` 配置资产，以及自动关联的 `UBlackmagicMediaCapture` 捕获实例。在蓝图中，你可以直接创建 `MediaOutput` 对象，设置属性后调用 `MediaCapture` 提供的通用节点。

### 配置资产（UBlackmagicMediaOutput）

在内容浏览器中右键创建「媒体->Blackmagic Media Output」，或在细节面板中直接配置以下核心属性：

| 属性 | 说明 | 蓝图可读写 |
|---|---|---|
| `OutputConfiguration` | 选择输出设备、端口、视频格式（如 1080p60） | 否（编辑器编辑） |
| `PixelFormat` | 像素格式：8bit YUV 或 10bit YUV | 是 |
| `TimecodeFormat` | 是否嵌入引擎时间码（LTC/VITC） | 是 |
| `AudioBufferSize` | 音频缓冲大小（采样数），越大延迟越高但更稳定 | 是 |
| `AudioSampleRate` | 音频采样率（当前固定 48kHz） | 是 |
| `OutputChannelCount` | 输出声道数（2/8/16） | 是 |
| `AudioBitDepth` | 音频位深度（16/32 位有符号） | 是 |
| `bOutputAudio` | 是否同时捕获音频 | 是 |
| `bInvertKeyOutput` | 反转键控输出（用于 alpha 通道反转） | 是 |
| `NumberOfBlackmagicBuffers` | 系统内存与设备间的缓冲帧数（3-4） | 否（编辑） |

### 核心节点（继承自 UMediaCapture）

在蓝图里使用 `Media Capture` 对象的通用节点，例如：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CaptureActiveSceneViewport` | 立即开始捕获当前活动视口 | `UMediaCapture`（全局静态函数）|
| `CaptureTextureRenderTarget2D` | 捕获指定 Render Target 2D | `UMediaCapture` |
| `StartCapture` | 从 UMediaOutput 对象启动捕获 | `UMediaCapture` |
| `StopCapture` | 停止当前捕获过程 | `UMediaCapture` |
| `OnMediaCaptureStateChanged` | 捕获状态改变时的事件 | `UMediaCapture` |

**典型蓝图流程**：
1. 创建一个 `UBlackmagicMediaOutput` 资产（或构造）
2. 设置 `OutputConfiguration`、`PixelFormat`、音频参数等
3. 调用 `CaptureActiveSceneViewport` 或 `StartCapture`，传入该 MediaOutput
4. 监听 `OnMediaCaptureStateChanged` 事件以处理同步/错误

## C++ 用法

### 头文件引入

```cpp
#include "BlackmagicMediaOutput.h"
#include "BlackmagicMediaCapture.h"
```

### 基本用法

创建输出配置并启动捕获（从视口或 RenderTarget）：

```cpp
// 创建一个指向 Blackmagic 输出的媒体输出对象
UBlackmagicMediaOutput* MediaOutput = NewObject<UBlackmagicMediaOutput>();
MediaOutput->OutputConfiguration = /* 从设备枚举获得的 FMediaIOOutputConfiguration */;
MediaOutput->PixelFormat = EBlackmagicMediaOutputPixelFormat::PF_10BIT_YUV;
MediaOutput->bOutputAudio = true;
MediaOutput->AudioSampleRate = EBlackmagicMediaOutputAudioSampleRate::SR_48k;

// 获取媒体捕获管理器（单例）
UMediaCapture* MediaCapture = UMediaCapture::CreateMediaCapture(MediaOutput);
if (MediaCapture)
{
    // 启动捕获当前活动视口
    MediaCapture->CaptureActiveSceneViewport(
        FMediaCaptureOptions::Default
    );
}
```

*来源：基于 `UBlackmagicMediaCapture::InitBlackmagic` 和基类 `UMediaCapture` 的典型用法推断。*

### 进阶用法

**输出带嵌入时间码的 10bit YUV 信号**：

```cpp
// 配置时间码格式
MediaOutput->TimecodeFormat = EMediaIOTimecodeFormat::LTC;

// 设置音频参数
MediaOutput->bOutputAudio = true;
MediaOutput->OutputChannelCount = EBlackmagicMediaAudioOutputChannelCount::CH_8;
MediaOutput->AudioBitDepth = EBlackmagicMediaOutputAudioBitDepth::Signed_24Bits; // 注意枚举值变化

// 启动捕获自定义 RenderTarget（假设已有 RT）
UTextureRenderTarget2D* OutputRT = /* ... */;
MediaCapture->CaptureTextureRenderTarget2D(
    OutputRT,
    FMediaCaptureOptions::Default
);

// 监控帧丢失
if (UBlackmagicMediaCapture* BmcCapture = Cast<UBlackmagicMediaCapture>(MediaCapture))
{
    // 可以在 UBlackmagicMediaCapture 子类中扩展丢失帧回调（当前基类未暴露）
}
```

**等待同步事件**：如果需要与外部同步信号对齐，在 `UBlackmagicMediaOutput` 中设置 `bWaitForSyncEvent` 为 true（高级选项），捕获线程将等待 Genlock 信号到达后再提交帧。

## Demo 示例

以下是一个最小可行的 C++ Actor 组件，演示从游戏视口输出到 Blackmagic 设备：

**Header (BlackmagicOutputActor.h)**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "BlackmagicMediaOutput.generated.h"

class UBlackmagicMediaOutput;
class UMediaCapture;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UBlackmagicOutputActor : public UActorComponent
{
    GENERATED_BODY()

public:
    UBlackmagicOutputActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

protected:
    UPROPERTY(EditAnywhere, Category = "Blackmagic Output")
    FMediaIOOutputConfiguration OutputConfiguration;

    UPROPERTY(EditAnywhere, Category = "Blackmagic Output")
    EBlackmagicMediaOutputPixelFormat PixelFormat = EBlackmagicMediaOutputPixelFormat::PF_10BIT_YUV;

    UPROPERTY(EditAnywhere, Category = "Blackmagic Output")
    bool bOutputAudio = true;

private:
    UPROPERTY()
    UBlackmagicMediaOutput* MediaOutput;

    UPROPERTY()
    UMediaCapture* MediaCapture;
};
```

**Source (BlackmagicOutputActor.cpp)**

```cpp
#include "BlackmagicOutputActor.h"
#include "BlackmagicMediaOutput.h"
#include "MediaCapture.h"
#include "MediaIOCoreDefinitions.h"

UBlackmagicOutputActor::UBlackmagicOutputActor()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UBlackmagicOutputActor::BeginPlay()
{
    Super::BeginPlay();

    MediaOutput = NewObject<UBlackmagicMediaOutput>(this);
    MediaOutput->OutputConfiguration = OutputConfiguration;
    MediaOutput->PixelFormat = PixelFormat;
    MediaOutput->bOutputAudio = bOutputAudio;

    MediaCapture = UMediaCapture::CreateMediaCapture(MediaOutput);
    if (MediaCapture)
    {
        MediaCapture->CaptureActiveSceneViewport(FMediaCaptureOptions::Default);
    }
}

void UBlackmagicOutputActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaCapture && MediaCapture->IsCapturing())
    {
        MediaCapture->StopCapture(false);
    }
    Super::EndPlay(EndPlayReason);
}
```

*注意：`FMediaIOOutputConfiguration` 需要从设备枚举或编辑器配置中获取，此处仅为演示。*

## 模块依赖

该插件（BlackmagicMediaOutput 子模块）的构建依赖：

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 提供时间码、帧率、格式定义等媒体核心类型 |
| `BlackmagicCore` | 底层 Blackmagic SDK 封装 |
| `MediaUtils` | 媒体捕获管理器与通用媒体输出接口 |
| `AudioExtensions` | 音频捕获与输出支持 |
| `RHI` / `RenderCore` | GPU 纹理/缓冲区操作 |

无其他特殊依赖（标准 Core/Engine/Slate 等已省略）。

## 维护状态

### 近期更新

- 2025-09-23 `9d85dc0e` Blackmagic - Fix Blackmagic source assigning default configuration despite having a valid one.
- 2025-08-21 `8143139e` Add missing #include
- 2025-08-20 `2f0476a2` Add missing include
- 2025-07-22 `d0ba5722` Media Profile: Specified category display order for AJA, Blackmagic, and NDI media sources and outputs
- 2025-06-18 `60a45027` Disable BlackmagicMedia plugin on Windows Arm64

### 维护评价

- **年龄**: 2025 年 6 月创建，距今约 4 个月（🆕）
- **更新频率**: 最近 3 个月内有多次提交，包含功能修复、构建修复和配置优化，属于**活跃维护**
- **稳定性**: 作为新插件，尚未发现已知重大问题；但 Blackmagic SDK 外部依赖可能导致跨平台支持受限
- **推荐度**: 强烈推荐，如果项目需要 Blackmagic 输出，这是官方唯一接口

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia)
- [Blackmagic Design Developer](https://www.blackmagicdesign.com/developer)
- [UE 官方文档 - Media Capture](https://docs.unrealengine.com/5.3/en-US/media-framework-in-unreal-engine/)（通用，具体 Blackmagic 部分参考插件源码）