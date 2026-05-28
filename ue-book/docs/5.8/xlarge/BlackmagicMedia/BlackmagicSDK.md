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
| 创建时间 | 2018-09-04 |
| 年龄标签 | 🆕（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途

BlackmagicMedia 插件是 UE5 Media Framework 与 Blackmagic DeckLink 系列采集卡之间的桥接层。它解决了在 Unreal Engine 中通过专业 SDI/HDMI 硬件进行实时视频采集和输出的需求。

**核心能力**：
- **视频输入（Capture）**：从 DeckLink 采集卡接收 SDI/HDMI 视频信号，支持从 480i 到 8K DCI 120p 的全部专业视频格式
- **视频输出（Output）**：将 UE5 渲染画面通过 DeckLink 卡输出到外部设备（监视器、录机、LED 墙等）
- **音频输入/输出**：随视频流同步传输嵌入式音频或独立音频通道
- **Timecode 支持**：读取和写入 SMPTE RP188、VITC、LTC 等专业时间码格式
- **Media Framework 集成**：通过 UMediaSource / UMediaPlayer / UMediaCapture 等 UE 标准接口暴露功能

**为什么存在**：虚拟制片（Virtual Production）、直播（Live Broadcasting）、XR 拓展、广电级回放等场景需要与 Blackmagic 硬件直接交互，此插件封装了 Blackmagic DeckLink SDK 的底层 COM 接口，提供了 UE5 原生的媒体工作流集成。

## 使用场景

- 你在搭建虚拟制片 LED 墙 → 用 BlackmagicMediaOutput 将 nDisplay 画面通过 DeckLink SDI 输出到 LED 处理器
- 你需要从摄影机实时采集 SDI 信号到 UE5 场景中 → 用 BlackmagicMediaSource 作为媒体源
- 你需要将 UE5 渲染画面录到外部录机（如 HyperDeck）→ 用 DeckLink 输出功能
- 你需要同步多路视频输入的时间码 → 使用插件内置的 Timecode Provider
- 你在做实况转播需要画中画效果 → 采集多路 SDI 信号并在场景中合成
- 你需要通过 genlock 同步 UE5 渲染和外部信号 → DeckLink 参考输入 + 自定义时间步进

## 蓝图用法

由于此插件主要通过 UE5 Media Framework 的标准接口工作，蓝图交互主要通过 Media Source、Media Player 和 Media Capture 等通用蓝图资产实现，而非特定于 Blackmagic 的自定义蓝图节点。

### 核心资产类型

| 资产类型 | 说明 | 用途 |
|---|---|---|
| `UBlackmagicMediaSource` | 视频输入源配置 | 选择设备、端口、视频格式、像素格式等 |
| `UBlackmagicMediaOutput` | 视频输出目标配置 | 配置输出设备、分辨率、帧率 |
| `UMediaPlayer` | 媒体播放器 | 与 MediaSource 配合使用，控制采集的播放/停止 |
| `UMediaCapture` | 媒体捕获 | 将渲染输出发送到 MediaOutput |

### 使用示例（蓝图描述）

**采集 SDI 输入**：
1. 创建 `BlackmagicMediaSource` 资产，选择 DeckLink 设备和输入端口
2. 设置视频格式（如 `bmdModeHD1080p2997`）
3. 创建 `MediaPlayer` 资产，用 Open Source 节点打开 MediaSource
4. 在 Media Texture / Media Sound 中引用 MediaPlayer

**输出到 DeckLink**：
1. 创建 `BlackmagicMediaOutput` 资产，配置输出设备和格式
2. 创建 `MediaCapture` 资产，设置 Output 为 BlackmagicMediaOutput
3. 在 Viewport 或 Render Target 上调用 StartCapture

## C++ 用法

### 头文件引入

```cpp
// 使用 Blackmagic DeckLink SDK 原生接口
#include "DeckLinkAPI.h"
#include "DeckLinkAPIModes.h"
#include "DeckLinkAPITypes.h"
#include "DeckLinkAPIConfiguration.h"

// 使用 UE5 媒体框架封装
#include "BlackmagicMediaSource.h"
#include "BlackmagicMediaOutput.h"
```

### 基本用法 — DeckLink 设备枚举

通过 DeckLink SDK 原生接口枚举系统中的 Blackmagic 设备：

```cpp
#include "DeckLinkAPI.h"

// 创建设备迭代器
IDeckLinkIterator* DeckLinkIterator = nullptr;
HRESULT Result = GetDeckLinkIteratorInstance(&DeckLinkIterator);
if (Result != S_OK || !DeckLinkIterator)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create DeckLink iterator. Is Desktop Video installed?"));
    return;
}

// 遍历所有 DeckLink 设备
IDeckLink* DeckLink = nullptr;
while (DeckLinkIterator->Next(&DeckLink) == S_OK)
{
    // 获取设备名称
    CFStringRef DeviceName = nullptr;
    DeckLink->GetDisplayName(&DeviceName);
    
    // 获取视频输出接口
    IDeckLinkOutput* DeckLinkOutput = nullptr;
    DeckLink->QueryInterface(IID_IDeckLinkOutput, (void**)&DeckLinkOutput);
    
    if (DeckLinkOutput)
    {
        // 枚举支持的显示模式
        IDeckLinkDisplayModeIterator* ModeIterator = nullptr;
        DeckLinkOutput->GetDisplayModeIterator(&ModeIterator);
        
        IDeckLinkDisplayMode* DisplayMode = nullptr;
        while (ModeIterator->Next(&DisplayMode) == S_OK)
        {
            BMDDisplayMode Mode = DisplayMode->GetDisplayMode();
            long Width = DisplayMode->GetWidth();
            long Height = DisplayMode->GetHeight();
            BMDTimeValue FrameDuration;
            BMDTimeScale TimeScale;
            DisplayMode->GetFrameRate(&FrameDuration, &TimeScale);
            
            DisplayMode->Release();
        }
        ModeIterator->Release();
        DeckLinkOutput->Release();
    }
    
    DeckLink->Release();
}
DeckLinkIterator->Release();
```

*（来源：DeckLinkAPI.h 中 IID_IDeckLinkIterator、IID_IDeckLinkOutput 等接口定义）*

### 基本用法 — 查询设备能力

```cpp
#include "DeckLinkAPI.h"

IDeckLink* DeckLink = GetFirstDeckLinkDevice(); // 自行实现的获取设备函数
if (!DeckLink) return;

// 查询设备属性
IDeckLinkAttributes* Attributes = nullptr;
DeckLink->QueryInterface(IID_IDeckLinkProfileAttributes, (void**)&Attributes);

if (Attributes)
{
    // 是否支持内部抠像
    bool SupportsInternalKeying = false;
    Attributes->GetFlag(BMDDeckLinkSupportsInternalKeying, &SupportsInternalKeying);
    
    // 最大音频通道数
    int64_t MaxAudioChannels = 0;
    Attributes->GetInt(BMDDeckLinkMaximumAudioChannels, &MaxAudioChannels);
    
    // 视频输出连接类型（SDI/HDMI/模拟等）
    int64_t VideoOutputConnections = 0;
    Attributes->GetInt(BMDDeckLinkVideoOutputConnections, &VideoOutputConnections);
    
    // 检查是否有 HDMI 输出
    bool HasHDMI = (VideoOutputConnections & bmdVideoConnectionHDMI) != 0;
    
    // 设备名称
    CFStringRef DeviceName = nullptr;
    Attributes->GetString(BMDDeckLinkDisplayName, &DeviceName);
    
    Attributes->Release();
}
DeckLink->Release();
```

*（来源：DeckLinkAPI.h 中 BMDDeckLinkAttributeID 枚举定义）*

### 进阶用法 — 视频输出与帧调度

```cpp
#include "DeckLinkAPI.h"
#include "DeckLinkAPIModes.h"

// 配置视频输出
IDeckLinkOutput* DeckLinkOutput = nullptr; // 从设备获取

// 启用 1080p29.97 视频输出
BMDDisplayMode OutputMode = bmdModeHD1080p2997;
BMDPixelFormat PixelFormat = bmdFormat8BitBGRA;  // 使用 BGRA 像素格式
BMDVideoOutputFlags OutputFlags = bmdVideoOutputFlagDefault;

HRESULT Hr = DeckLinkOutput->EnableVideoOutput(OutputMode, OutputFlags);
if (Hr != S_OK) return;

// 创建视频帧（假设宽度1920、高度1080）
const int32_t Width = 1920;
const int32_t Height = 1080;
const int32_t RowBytes = Width * 4;  // 4 bytes per pixel for BGRA
IDeckLinkMutableVideoFrame* VideoFrame = nullptr;

Hr = DeckLinkOutput->CreateVideoFrame(
    Width, Height, RowBytes,
    PixelFormat, bmdFrameFlagDefault,
    &VideoFrame
);

// 填充帧数据
void* FrameBuffer = nullptr;
VideoFrame->GetBytes(&FrameBuffer);
// ... 填充像素数据到 FrameBuffer ...

// 设置时间码
VideoFrame->SetTimecodeFromComponents(
    bmdTimecodeRP188VITC1,
    10, 30, 0, 0,  // 10:30:00:00
    bmdTimecodeFlagDefault
);

// 调度帧显示
BMDTimeValue DisplayTime = 0;
BMDTimeValue DisplayDuration = 1001;  // 29.97fps: 1001/30000
BMDTimeScale TimeScale = 30000;

DeckLinkOutput->ScheduleVideoFrame(VideoFrame, DisplayTime, DisplayDuration, TimeScale);
DeckLinkOutput->StartScheduledPlayback(0, TimeScale, 1.0);

// ... 清理 ...
DeckLinkOutput->DisableVideoOutput();
VideoFrame->Release();
DeckLinkOutput->Release();
```

*（来源：DeckLinkAPI.h 中 IDeckLinkOutput 接口、BMDDisplayMode 枚举、BMDPixelFormat 枚举定义）*

### 进阶用法 — 视频输入采集

```cpp
#include "DeckLinkAPI.h"
#include "DeckLinkAPIModes.h"

// 设置输入回调
class FMyDeckLinkInputCallback : public IDeckLinkInputCallback
{
public:
    virtual HRESULT VideoInputFormatChanged(
        BMDVideoInputFormatChangedEvents Events,
        IDeckLinkDisplayMode* NewMode,
        BMDDetectedVideoInputFormatFlags Flags) override
    {
        // 信号格式变化时重新配置
        BMDDisplayMode NewDisplayMode = NewMode->GetDisplayMode();
        // ... 重新启用输入 ...
        return S_OK;
    }
    
    virtual HRESULT VideoInputFrameArrived(
        IDeckLinkVideoInputFrame* VideoFrame,
        IDeckLinkAudioInputPacket* AudioPacket) override
    {
        if (VideoFrame)
        {
            // 检查是否有信号输入
            BMDFrameFlags Flags = VideoFrame->GetFlags();
            if (Flags & bmdFrameHasNoInputSource)
            {
                return S_OK;  // 无信号
            }
            
            // 获取帧数据
            void* Buffer = nullptr;
            VideoFrame->GetBytes(&Buffer);
            long Width = VideoFrame->GetWidth();
            long Height = VideoFrame->GetHeight();
            BMDPixelFormat Format = VideoFrame->GetPixelFormat();
            
            // 获取流时间
            BMDTimeValue FrameTime, FrameDuration;
            VideoFrame->GetStreamTime(&FrameTime, &FrameDuration, 30000);
            
            // 读取时间码
            IDeckLinkTimecode* Timecode = nullptr;
            VideoFrame->GetTimecode(bmdTimecodeRP188Any, &Timecode);
            if (Timecode)
            {
                BMDTimecodeBCD TimecodeBCD = Timecode->GetBCD();
                Timecode->Release();
            }
        }
        return S_OK;
    }
    
    virtual HRESULT QueryInterface(REFIID iid, void** ppv) override { /* ... */ }
    virtual ULONG AddRef() override { /* ... */ }
    virtual ULONG Release() override { /* ... */ }
};

// 启用输入
IDeckLinkInput* DeckLinkInput = nullptr; // 从设备获取
FMyDeckLinkInputCallback* Callback = new FMyDeckLinkInputCallback();

DeckLinkInput->SetCallback(Callback);
DeckLinkInput->EnableVideoInput(
    bmdModeHD1080p2997,     // 显示模式
    bmdFormat8BitYUV,       // 像素格式
    bmdVideoInputFlagDefault // 启用格式检测
);
DeckLinkInput->EnableAudioInput(bmdAudioSampleRate48kHz, bmdAudioSampleType16bitInteger, 2);
DeckLinkInput->StartStreams();

// ... 等待帧到达 ...
DeckLinkInput->StopStreams();
DeckLinkInput->DisableVideoInput();
DeckLinkInput->DisableAudioInput();
```

*（来源：DeckLinkAPI.h 中 IDeckLinkInputCallback、IDeckLinkInput 接口定义）*

## Demo 示例

### DeckLink 设备信息查询器

一个最小可编译示例，遍历系统中所有 DeckLink 设备并打印信息：

```cpp
// DeckLinkInfo.h
#pragma once

#include "CoreMinimal.h"

class FDeckLinkInfo
{
public:
    static void PrintAllDeviceInfo();
};
```

```cpp
// DeckLinkInfo.cpp
#include "DeckLinkInfo.h"
#include "DeckLinkAPI.h"
#include "DeckLinkAPIModes.h"
#include "HAL/Platform.h"

DEFINE_LOG_CATEGORY_STATIC(LogDeckLinkInfo, Log, All);

void FDeckLinkInfo::PrintAllDeviceInfo()
{
#if PLATFORM_WINDOWS || PLATFORM_LINUX
    IDeckLinkIterator* Iterator = nullptr;
    HRESULT Hr = GetDeckLinkIteratorInstance(&Iterator);
    
    if (Hr != S_OK || !Iterator)
    {
        UE_LOG(LogDeckLinkInfo, Error,
            TEXT("Failed to create DeckLink iterator. "
                 "Ensure Blackmagic Desktop Video software is installed."));
        return;
    }

    int32_t DeviceIndex = 0;
    IDeckLink* Device = nullptr;

    while (Iterator->Next(&Device) == S_OK)
    {
        UE_LOG(LogDeckLinkInfo, Display, TEXT("=== DeckLink Device %d ==="), DeviceIndex);

        // 设备名称
        CFStringRef Name = nullptr;
        Device->GetDisplayName(&Name);
        if (Name)
        {
            char NameBuffer[256] = {};
            CFStringGetCString(Name, NameBuffer, sizeof(NameBuffer), kCFStringEncodingUTF8);
            UE_LOG(LogDeckLinkInfo, Display, TEXT("  Name: %hs"), NameBuffer);
            CFRelease(Name);
        }

        // 枚举输出支持的显示模式
        IDeckLinkOutput* Output = nullptr;
        if (Device->QueryInterface(IID_IDeckLinkOutput, (void**)&Output) == S_OK)
        {
            IDeckLinkDisplayModeIterator* ModeIter = nullptr;
            Output->GetDisplayModeIterator(&ModeIter);

            if (ModeIter)
            {
                int32_t ModeCount = 0;
                IDeckLinkDisplayMode* Mode = nullptr;
                while (ModeIter->Next(&Mode) == S_OK)
                {
                    long W = Mode->GetWidth();
                    long H = Mode->GetHeight();
                    BMDTimeValue Dur;
                    BMDTimeScale Scale;
                    Mode->GetFrameRate(&Dur, &Scale);
                    BMDFieldDominance Field = Mode->GetFieldDominance();

                    const TCHAR* FieldStr = Field == bmdProgressiveFrame
                        ? TEXT("Progressive")
                        : (Field == bmdLowerFieldFirst ? TEXT("Interlaced LFF") : TEXT("Interlaced UFF"));

                    UE_LOG(LogDeckLinkInfo, Display,
                        TEXT("  Mode: %ldx%ld @ %.2f fps %s"),
                        W, H, (double)Scale / Dur, FieldStr);

                    Mode->Release();
                    ModeCount++;
                }
                UE_LOG(LogDeckLinkInfo, Display, TEXT("  Total output modes: %d"), ModeCount);
                ModeIter->Release();
            }
            Output->Release();
        }

        Device->Release();
        DeviceIndex++;
    }

    if (DeviceIndex == 0)
    {
        UE_LOG(LogDeckLinkInfo, Warning, TEXT("No DeckLink devices found."));
    }

    Iterator->Release();
#endif
}
```

## 模块依赖

此插件的使用者通常不需要直接依赖 BlackmagicSDK 模块，而是通过标准的 Media Framework 路径工作。如果需要直接使用 DeckLink SDK 原生接口：

| 模块 | 用途 |
|---|---|
| `BlackmagicSDK` | DeckLink SDK 原生头文件和库（仅在需要直接调用 DeckLink API 时） |
| `MediaIOCore` | Media Framework 基础设施（通过 BlackmagicMedia 模块间接依赖） |
| `MediaAssets` | UMediaPlayer / UMediaSource / UMediaCapture 等媒体资产类 |

> **注意**：系统必须安装 **Blackmagic Desktop Video** 驱动/软件包才能使用此插件。DeckLink SDK 库随 Desktop Video 安装提供。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `fe681f84` | MediaIO: Fix Blackmagic auto-detect misinterpreting interlaced signals as progressive. | 修复自动检测将隔行信号误判为逐行的问题 |
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 使用 auto 模式时自动填充媒体配置信息 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和采集添加引擎分析信息 |
| 2026-05-12 | `b7bb4354` | Media IO - Fix bob deinterlacer field samples sharing source-frame timestamp | 修复 Bob 反交错器字段样本共享源帧时间戳 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the... | 虚拟制片相关资产迁移至新分类 |

### 维护评价

- **活跃维护**：最近 6 个月内有多次功能性更新，包括 bug 修复和新功能
- **创建时间**：2018 年 9 月创建，属于 UE4 时期的专业媒体插件
- **维护频率**：持续活跃更新，最近的 commit 集中在信号检测、反交错、analytics 等方面
- **成熟度**：经过 8 年迭代，已是非常成熟的生产级插件
- **硬件依赖**：需要 Blackmagic Desktop Video 驱动，插件版本需与 SDK 版本匹配
- **已知限制**：`EnabledByDefault=false`，需手动在插件设置中启用；仅支持 Win64 和 Linux 平台

**推荐使用**：如果你的虚拟制片或广播工作流需要 Blackmagic DeckLink 硬件支持，这是官方推荐的集成方案，维护状态良好，推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia)
- [Blackmagic DeckLink SDK 文档](https://www.blackmagicdesign.com/developer)
- [UE5 Media Framework 官方文档](https://docs.unrealengine.com/5.8/en-US/media-framework-in-unreal-engine/)
- [Blackmagic Desktop Video 下载](https://www.blackmagicdesign.com/desktopvideo)

---

# BlackmagicSDK 模块

BlackmagicSDK 是一个 **External** 类型模块，封装了 Blackmagic 官方的 **DeckLink SDK** 头文件。它不包含 UE5 自身的运行时代码，而是为其他模块（如 BlackmagicMedia）提供访问 DeckLink 硬件 API 的能力。

## 模块说明

此模块包含 Blackmagic DeckLink SDK 的平台特定头文件（Windows/macOS/Linux），定义了与 DeckLink 硬件交互所需的所有 COM 接口、枚举类型和数据结构。

### 包含的 API 版本

模块包含从 **v7.1** 到 **v11.5.1** 的多个 API 版本头文件，以支持不同代次的 DeckLink 硬件：

| 版本范围 | 主要特性 |
|---|---|
| v7.1 - v7.9 | 基础视频/音频输入输出、显示模式枚举 |
| v8.1 | VTR 控制、Deck Control 接口改进 |
| v9.2 - v9.9 | 视频输出接口增强、参考信号状态查询 |
| v10.11 | Duplex 模式配置、属性查询接口、通知接口 |
| v11.4 | 视频输入/输出接口统一化、连接类型查询增强 |
| v11.5 | Cintel 胶片扫描仪元数据、HDR 元数据扩展 |
| v11.5.1 | 输入回调和输入接口最终版 |

### 核心 COM 接口

| 接口 | 说明 |
|---|---|
| `IDeckLink` | 设备根接口，通过 QueryInterface 获取其他接口 |
| `IDeckLinkOutput` | 视频/音频输出、帧调度、硬件时钟 |
| `IDeckLinkInput` | 视频/音频输入、流控制 |
| `IDeckLinkConfiguration` | 设备配置（连接类型、转换模式、音频设置等） |
| `IDeckLinkDisplayMode` | 显示模式（分辨率、帧率、场序） |
| `IDeckLinkVideoFrame` | 视频帧数据封装 |
| `IDeckLinkMutableVideoFrame` | 可写视频帧（用于输出） |
| `IDeckLinkVideoInputFrame` | 输入帧（含流时间和硬件时间戳） |
| `IDeckLinkAudioInputPacket` | 输入音频包 |
| `IDeckLinkTimecode` | 时间码表示（BCD、组件、字符串） |
| `IDeckLinkAttributes` | 设备属性查询（能力标志、连接类型等） |
| `IDeckLinkStatus` | 设备运行状态查询 |
| `IDeckLinkConfiguration` | 设备参数配置 |
| `IDeckLinkDeckControl` | VTR/磁带机控制（播放、录制、搜索等） |

### 关键枚举类型

| 枚举 | 说明 |
|---|---|
| `BMDDisplayMode` | 所有支持的视频模式（NTSC/PAL/HD/2K/4K/8K/PC 各分辨率和帧率） |
| `BMDPixelFormat` | 像素格式（8bit/10bit/12bit YUV、RGB、H.265、DNxHR） |
| `BMDVideoConnection` | 视频连接类型（SDI/HDMI/Optical/Component/Composite/SVideo） |
| `BMDAudioConnection` | 音频连接类型（Embedded/AES-EBU/Analog/Mic/Headphone） |
| `BMDTimecodeFormat` | 时间码格式（RP188 VITC1/VITC2/LTC/HFRTC、VITC、Serial） |
| `BMDFieldDominance` | 场序（逐行、上场优先、下场优先、PsF） |
| `BMDFrameFlags` | 帧标志（垂直翻转、HDR 元数据、无信号源等） |

## 模块依赖

BlackmagicSDK 是纯头文件外部模块，无运行时依赖。它通过 `Build.cs` 提供包含路径和预处理器定义，供 `BlackmagicMedia` 等模块链接时使用。

## 维护状态

作为第三方 SDK 封装层，BlackmagicSDK 的更新随 Epic 的 DeckLink SDK 版本升级而进行。当前包含的 SDK 版本已覆盖至 v11.5.1，支持最新的 DeckLink 硬件特性。