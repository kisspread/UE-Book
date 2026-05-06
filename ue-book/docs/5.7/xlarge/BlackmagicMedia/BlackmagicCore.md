# Blackmagic Media Player

> Implements input and output using Blackmagic Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | 黑魔法采集卡媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicCore` (Runtime), `BlackmagicMedia` (Runtime), `BlackmagicMediaEditor` (Runtime), `BlackmagicMediaFactory` (Runtime), `BlackmagicMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-06-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途

该插件提供了对 **Blackmagic Design 采集卡** 的底层硬件支持，实现高精度的**视频输入**（从采集卡获取帧）和**视频输出**（通过采集卡发送帧到显示器或录制设备）。

**为什么存在？**  
Unreal Engine 原生无法直接与专业广播级采集卡通信。BlackmagicMedia 封装了 DeckLink SDK，将复杂的硬件接口转换为 UE 可用的模块化架构，使开发者可以通过 `MediaPlayer`、`MediaSource`、`MediaOutput` 等标准媒体框架使用 Blackmagic 设备。它解决了广电、直播、虚拟制片等领域对超低延迟、高精确时间码、多路 SDI/HDMI 输入输出的需求。

## 使用场景

- **虚拟演播室 / 电视直播**：使用 Blackmagic 采集卡将摄像机信号实时传入 UE，驱动背景或虚拟摄像跟踪。
- **大屏 / LED 背景投射**：将 UE 渲染画面通过输出卡发送到 LED 屏幕，要求帧同步和 Genlock。
- **视频播放与录制**：在片场或演播室中使用 UE 播放预渲染内容，并同步录制带时间码的输出。
- **多机位切换**：同时从多张采集卡读取信号，支持不同视频格式（SD/HD/4K/8K）。
- **专业广播流程**：利用 SDI 嵌入音频、LTC 时间码、HDR 元数据等特性。

## 蓝图用法

本插件的核心功能（设备管理、输入输出通道）**未直接暴露蓝图函数**，所有底层操作需在 C++ 层完成。但是在更高层模块（如 `BlackmagicMediaSource`、`BlackmagicMediaOutput`）中，您可以通过标准的 `MediaPlayer`、`MediaSource`、`FileMediaOutput` 等蓝图节点间接使用，配置项通过细节面板设置。

**无需手动编写蓝图节点**，只需在内容浏览器中创建对应的资产即可使用：
- `BlackmagicMediaSource`（输入源）
- `BlackmagicMediaOutput`（输出目标）

配置完毕后，使用常规的 `Open Source`、`Play`、`Close` 等节点控制媒体流。

## C++ 用法

### 头文件引入

```cpp
#include "BlackmagicLib.h"
#include "BlackmagicCoreModule.h"
#include "Common.h"
```

### 基本用法

#### 1. 获取模块并检查硬件可用性

```cpp
// 检查 BlackmagicCore 模块是否初始化成功
FBlackmagicCoreModule& CoreModule = FModuleManager::LoadModuleChecked<FBlackmagicCoreModule>("BlackmagicCore");
if (!CoreModule.IsInitialized())
{
    UE_LOG(LogTemp, Error, TEXT("BlackmagicCore not initialized. Cannot use Blackmagic card."));
    return;
}

// 确保可以访问硬件（需要 CanEverRender 或强制启用）
if (!CoreModule.CanUseBlackmagicCard())
{
    UE_LOG(LogTemp, Warning, TEXT("Blackmagic card cannot be used in this context."));
}
```

#### 2. 扫描设备

```cpp
#include "BlackmagicDeviceScanner.h"

BlackmagicDesign::Private::DeviceScanner Scanner;
int32_t NumDevices = Scanner.GetNumDevices();
UE_LOG(LogTemp, Log, TEXT("Found %d Blackmagic device(s)."), NumDevices);

for (int32 i = 0; i < NumDevices; ++i)
{
    BlackmagicDesign::BlackmagicDeviceScanner::FormatedTextType TextId;
    BlackmagicDesign::BlackmagicDeviceScanner::DeviceInfo Info;
    Scanner.GetDeviceTextId(i, TextId);
    Scanner.GetDeviceInfo(i, Info);
    UE_LOG(LogTemp, Log, TEXT("Device %d: %s (identifier=%lld)"), i, TextId, Info.DeviceIdentifier);
}
```

#### 3. 注册输入通道并接收帧

```cpp
#include "BlackmagicInputChannel.h"
#include "BlackmagicDevice.h"

using namespace BlackmagicDesign;
using namespace BlackmagicDesign::Private;

// 定义回调类
class FMyInputCallback : public IInputEventCallback
{
public:
    FMyInputCallback() : RefCount(1) {}

    // IUnknown 必须实现
    ULONG STDMETHODCALLTYPE AddRef() override { return ++RefCount; }
    ULONG STDMETHODCALLTYPE Release() override { if (--RefCount == 0) delete this; return 0; }
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID, LPVOID*) override { return E_NOINTERFACE; }

    virtual void OnFrameReceived(const FFrameReceivedInfo& Info) override
    {
        // 处理视频帧（Info.VideoBuffer 包含像素数据）
        UE_LOG(LogTemp, Log, TEXT("Frame received: width=%d, height=%d, timecode=%s"),
               Info.VideoWidth, Info.VideoHeight, *Info.Timecode.ToString());
    }

    virtual void OnVideoFormatChanged(const FVideoFormatChangedInfo& Info) override
    {
        UE_LOG(LogTemp, Log, TEXT("Video format changed: %dx%d, framerate=%d/%d"),
               Info.VideoWidth, Info.VideoHeight, Info.FrameRateNumerator, Info.FrameRateDenominator);
    }

    virtual void OnInputConnectionLost() override
    {
        UE_LOG(LogTemp, Log, TEXT("Input connection lost."));
    }

    virtual void OnInputConnectionRecovered() override
    {
        UE_LOG(LogTemp, Log, TEXT("Input connection recovered."));
    }

    std::atomic<ULONG> RefCount;
};

// 在函数中注册通道
void StartInput()
{
    FChannelInfo ChannelInfo;
    ChannelInfo.DeviceIndex = 0;  // 设备索引
    // 填写其他信息（如视频模式、像素格式等）

    FInputChannelOptions Options;
    Options.FormatInfo.DisplayMode = bmdModeHD1080p30;  // 来自 DeckLinkAPI 枚举
    Options.PixelFormat = EPixelFormat::pf_8Bits;
    Options.bUseVideo = true;
    Options.bUseAudio = false;

    ReferencePtr<FMyInputCallback> Callback(new FMyInputCallback());
    FUniqueIdentifier Id = FDevice::GetDevice()->RegisterChannel(ChannelInfo, Options, Callback);
    if (Id.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Input channel registered with id=%d"), Id.GetId());
    }
}
```

#### 4. 发送视频帧到输出通道

```cpp
#include "BlackmagicOutputChannel.h"

void SendOutputFrame()
{
    FChannelInfo ChannelInfo;
    ChannelInfo.DeviceIndex = 0;

    FOutputChannelOptions Options;
    Options.FormatInfo.DisplayMode = bmdModeHD1080p30;
    Options.PixelFormat = EPixelFormat::pf_8Bits;
    Options.OutputFrameType = EOutputFrameType::Progressive;
    Options.OutputAudioSampleRate = EAudioSampleRate::SR_48kHz;
    Options.OutputAudioBitDepth = EAudioBitDepth::Signed_16Bits;

    // 注册输出通道
    ReferencePtr<IOutputEventCallback> EmptyCallback; // 通常可以传递 nullptr
    FUniqueIdentifier Id = FDevice::GetDevice()->RegisterOutputChannel(ChannelInfo, Options, EmptyCallback);

    // 创建帧描述符（示例：填充纯色）
    const int32 Width = 1920;
    const int32 Height = 1080;
    const int32 Stride = Width * 4; // 假设 32bit BGRA
    FFrameDescriptor Frame;
    Frame.Width = Width;
    Frame.Height = Height;
    Frame.Stride = Stride;
    Frame.VideoBuffer = new uint8[Height * Stride];
    memset(Frame.VideoBuffer, 0xFF, Height * Stride); // 白色

    // 发送帧
    bool bSent = FDevice::GetDevice()->SendVideoFrameData(ChannelInfo, Frame);
    if (bSent)
    {
        UE_LOG(LogTemp, Log, TEXT("Frame sent successfully."));
    }

    delete[] Frame.VideoBuffer;
    FDevice::GetDevice()->UnregisterOutputChannel(ChannelInfo, Id);
}
```

### 进阶用法

#### GPU DMA 直接传输

使用 `SendVideoFrameData(const FChannelInfo&, FFrameDescriptor_GPUDMA&)` 直接从 GPU 纹理传输，避免 CPU 拷贝：

```cpp
FRHITexture* RHITexture = /* 你的渲染纹理 */;
FFrameDescriptor_GPUDMA GpuFrame;
GpuFrame.RHITexture = RHITexture;
GpuFrame.Stride = 0; // 将由 RHI 自动计算
GpuFrame.bUseGPUDMA = true;

// 前提：已在插件配置中启用了 GPUDMA 并初始化了 ITextureTransfer
bool bSent = FDevice::GetDevice()->SendVideoFrameData(ChannelInfo, GpuFrame);
```

## Demo 示例

完整的最小示例（在 GameInstance 或自定义 Actor 中调用）：

```cpp
// MyBlackmagicDemo.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "BlackmagicLib.h"
#include "MyBlackmagicDemo.generated.h"

UCLASS()
class UMyBlackmagicDemo : public UObject
{
    GENERATED_BODY()

public:
    void StartDeviceScan();
    void RegisterInput();
    void UnregisterInput();

private:
    BlackmagicDesign::FUniqueIdentifier InputId;
    BlackmagicDesign::FChannelInfo ChannelInfo;
};
```

```cpp
// MyBlackmagicDemo.cpp
#include "MyBlackmagicDemo.h"
#include "BlackmagicCoreModule.h"
#include "BlackmagicDeviceScanner.h"
#include "BlackmagicDevice.h"
#include "BlackmagicInputChannel.h"
#include "BlackmagicOutputChannel.h"

class FSimpleInputCallback : public BlackmagicDesign::IInputEventCallback
{
public:
    FSimpleInputCallback() : RefCount(1) {}
    ULONG STDMETHODCALLTYPE AddRef() override { return ++RefCount; }
    ULONG STDMETHODCALLTYPE Release() override { if (--RefCount == 0) delete this; return 0; }
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID, LPVOID*) override { return E_NOINTERFACE; }

    virtual void OnFrameReceived(const BlackmagicDesign::FFrameReceivedInfo& Info) override
    {
        UE_LOG(LogTemp, Log, TEXT("Demo Frame: %dx%d, timecode=%s"),
               Info.VideoWidth, Info.VideoHeight, *Info.Timecode.ToString());
    }
    virtual void OnVideoFormatChanged(const BlackmagicDesign::FVideoFormatChangedInfo&) override {}
    virtual void OnInputConnectionLost() override {}
    virtual void OnInputConnectionRecovered() override {}

    std::atomic<ULONG> RefCount;
};

void UMyBlackmagicDemo::StartDeviceScan()
{
    FBlackmagicCoreModule& CoreModule = FModuleManager::LoadModuleChecked<FBlackmagicCoreModule>("BlackmagicCore");
    if (!CoreModule.IsInitialized()) return;

    BlackmagicDesign::Private::DeviceScanner Scanner;
    int32_t Num = Scanner.GetNumDevices();
    UE_LOG(LogTemp, Log, TEXT("Found %d Blackmagic devices"), Num);
}

void UMyBlackmagicDemo::RegisterInput()
{
    ChannelInfo.DeviceIndex = 0;
    BlackmagicDesign::FInputChannelOptions Options;
    Options.FormatInfo.DisplayMode = bmdModeHD1080p30;
    Options.PixelFormat = BlackmagicDesign::EPixelFormat::pf_8Bits;
    Options.bUseVideo = true;
    Options.bUseAudio = false;

    BlackmagicDesign::ReferencePtr<FSimpleInputCallback> Callback(new FSimpleInputCallback());
    InputId = BlackmagicDesign::Private::FDevice::GetDevice()->RegisterChannel(
        ChannelInfo, Options, Callback);
    UE_LOG(LogTemp, Log, TEXT("Registered input id=%d"), InputId.GetId());
}

void UMyBlackmagicDemo::UnregisterInput()
{
    if (InputId.IsValid())
    {
        BlackmagicDesign::Private::FDevice::GetDevice()->UnregisterCallbackForChannel(
            ChannelInfo, InputId);
        InputId = BlackmagicDesign::FUniqueIdentifier();
    }
}
```

## 模块依赖

本插件独特的依赖如下（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `BlackmagicSDK` | Blackmagic DeckLink API，外部 SDK（非 UE 模块），由 `ThirdParty/BlackmagicLib` 提供。 |
| `GPUTextureTransfer` | 支持将帧直接通过 GPU 内存传输，避免 CPU 拷贝（可选）。 |

**使用注意**：使用前需确保系统安装了 **Blackmagic Desktop Video** 驱动及 SDK 库（`DeckLinkAPi.h`），并正确配置平台支持（Win64/Linux）。不依赖其他额外 UE 模块。

## 维护状态

### 近期更新

```
- 2025-09-23 9d85dc0e — Blackmagic - Fix Blackmagic source assigning default configuration despite having a valid one.
- 2025-08-21 8143139e — Add missing #include
- 2025-08-20 2f0476a2 — Add missing include
- 2025-07-22 d0ba5722 — Media Profile: Specified category display order for AJA, Blackmagic, and NDI media sources and outputs.
- 2025-06-18 60a45027 — Disable BlackmagicMedia plugin on Windows Arm64
```

### 维护评价

- **创建时间**：2025年6月（约4个月）
- **近期更新**：积极修复 bug（配置默认值、缺少头文件）和功能优化（媒体类别排序）
- **活跃度**：高，最近 1 个月内仍有 commit。
- **已知限制**：当前不支持 Windows ARM64 平台（已被显式禁用）；仅支持 Win64 和 Linux。部分功能（如 GPU DMA）需要额外初始化。
- **推荐使用**：✅ 推荐用于任何需要 Blackmagic 采集卡输入/输出的项目，特别是虚拟制片、直播和专业广电流程。插件较为年轻，但维护活跃，API 设计稳健。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia)
- [测试用例（输入/输出通道）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia/Source/BlackmagicMedia/Tests)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/blackmagic-media-player-for-unreal-engine/)（如有）