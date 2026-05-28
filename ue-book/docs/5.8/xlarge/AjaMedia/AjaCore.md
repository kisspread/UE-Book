# AjaCore

> Implements input and output using AJA Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | AJA 底层核心模块 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（AJA 硬件抽象层、设备扫描、音视频 I/O 管道） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia) | |

---

## 文档结构

本文档聚焦于 **AjaCore** 模块（底层 C++ 硬件抽象层）。完整插件包含以下模块：

| 模块 | 类型 | 职责 | 文档 |
|---|---|---|---|
| **AjaCore** | Runtime | AJA 硬件抽象层：设备扫描、通道管理、音视频/时间码 I/O | 👈 当前文档 |
| AjaMedia | Runtime | UE Media Framework 集成：MediaSource、MediaPlayer | 待补充 |
| AjaMediaEditor | Runtime | 编辑器 UI：媒体源/输出资产自定义面板 | 待补充 |
| AjaMediaFactory | Runtime | 资产工厂：创建 AjaMediaSource 等资产 | 待补充 |
| AjaMediaOutput | Runtime | MediaOutput 实现：将引擎画面输出到 AJA 卡 | 待补充 |

---

## 用途

AjaCore 是 AJA Media Player 插件的底层核心模块，封装了 AJA（Advanced Joint Architecture）专业视频采集卡的原生 C++ SDK。它解决了 UE 与 AJA 硬件之间的桥接问题：

- **设备抽象**：扫描系统中所有 AJA 设备，管理设备连接的生命周期和线程安全
- **视频 I/O 管道**：提供输入通道（`AJAInputChannel`）和输出通道（`AJAOutputChannel`）的完整实现，支持 AutoCirculate 和 PingPong 两种采集/输出模式
- **同步机制**：`AJASyncChannel` 等待 AJA 卡的垂直中断信号，使引擎 Tick 与外部视频信号帧同步
- **时间码读取**：`AJATimecodeChannel` 从 LTC（Longitudinal Timecode）、VITC（Vertical Interval Timecode）或模拟 LTC 引脚读取时间码
- **格式转换**：在 UE 像素格式、AJA 帧缓冲格式、视频格式、帧率、HDR 元数据之间进行双向转换
- **通道自动检测**：扫描所有已连接设备的活跃输入/输出通道

> **注意**：此模块仅在 **Win64** 平台可用，且需要系统中安装 AJA 驱动和 SDK。

---

## 使用场景

- 你在做虚拟制片（Virtual Production）→ 需要从 AJA 采集卡捕获摄影机信号并同步到 UE 渲染循环
- 你在做广播级实时合成（Broadcast Compositing）→ 需要将 UE 画面实时输出到 AJA SDI/HDMI 接口
- 你需要精确的外部时间码同步（LTC/VITC）→ 用 AjaCore 的 TimecodeChannel 从硬件读取时间码
- 你在做 LED 墙（LED Volume）项目 → 需要引擎帧率与摄影机帧率严格同步

---

## C++ 用法

### 头文件引入

```cpp
#include "AJALib.h"          // 主公共头文件，包含所有公开 API
```

### 基本用法

#### 扫描 AJA 设备

```cpp
#include "AJALib.h"

// 扫描系统中所有 AJA 设备（来自 Public/AJALib.h: AJADeviceScanner 类）
AJA::AJADeviceScanner Scanner;
int32_t NumDevices = Scanner.GetNumDevices();

for (int32_t i = 0; i < NumDevices; ++i)
{
    AJA::AJADeviceScanner::FormatedTextType DeviceTextId;
    AJA::AJADeviceScanner::DeviceInfo DeviceInfo;
    
    Scanner.GetDeviceTextId(i, DeviceTextId);
    Scanner.GetDeviceInfo(i, DeviceInfo);
    
    UE_LOG(LogAjaCore, Log, TEXT("Device %d: %s, SDI In=%d Out=%d, HDMI In=%d Out=%d"),
        i, DeviceTextId,
        DeviceInfo.NumSdiInput, DeviceInfo.NumSdiOutput,
        DeviceInfo.NumHdmiInput, DeviceInfo.NumHdmiOutput);
    
    // 检查设备能力
    if (DeviceInfo.bCanDo4K)
    {
        UE_LOG(LogAjaCore, Log, TEXT("  Supports 4K"));
    }
    if (DeviceInfo.bSupportPixelFormat10bitRGB)
    {
        UE_LOG(LogAjaCore, Log, TEXT("  Supports 10-bit RGB"));
    }
}
```

**来源**：`Public/AJALib.h` 中 `AJADeviceScanner` 类定义

---

#### 查询设备支持的视频格式

```cpp
// 查询指定设备支持的所有视频格式（来自 Public/AJALib.h: AJAVideoFormats 类）
AJA::AJAVideoFormats VideoFormats(0); // DeviceIndex = 0
int32_t NumFormats = VideoFormats.GetNumSupportedFormat();

for (int32_t i = 0; i < NumFormats; ++i)
{
    AJA::AJAVideoFormats::VideoFormatDescriptor Format = VideoFormats.GetSupportedFormat(i);
    
    if (Format.bIsValid)
    {
        UE_LOG(LogAjaCore, Log, TEXT("Format %u: %ux%u @ %u/%u fps %s"),
            Format.VideoFormatIndex,
            Format.ResolutionWidth, Format.ResolutionHeight,
            Format.FrameRateNumerator, Format.FrameRateDenominator,
            Format.bIsProgressiveStandard ? TEXT("Progressive") : TEXT("Interlaced"));
    }
}
```

**来源**：`Public/AJALib.h` 中 `AJAVideoFormats` 类定义

---

#### 初始化同步通道（等待外部信号）

```cpp
// 同步通道：使引擎 Tick 与 AJA 卡的垂直中断同步（来自 Public/AJALib.h: AJASyncChannel 类）
// 通常用于输出场景，确保 UE 帧与外部视频信号对齐

class FMySyncCallback : public AJA::IAJASyncChannelCallbackInterface
{
public:
    virtual void OnInitializationCompleted(bool bSucceed) override
    {
        if (bSucceed)
        {
            UE_LOG(LogAjaCore, Log, TEXT("Sync channel initialized successfully"));
        }
        else
        {
            UE_LOG(LogAjaCore, Error, TEXT("Sync channel initialization failed"));
        }
    }
};

// 使用示例
FMySyncCallback SyncCallback;

AJA::AJADeviceOptions DeviceOptions(0); // DeviceIndex = 0
AJA::AJASyncChannelOptions SyncOptions(TEXT("MySyncChannel"));
SyncOptions.CallbackInterface = &SyncCallback;
SyncOptions.TransportType = AJA::ETransportType::TT_SdiSingle;
SyncOptions.ChannelIndex = 1;
SyncOptions.VideoFormatIndex = /* format index */;
SyncOptions.bOutput = false;  // 输入同步
SyncOptions.bAutoDetectFormat = true;

AJA::AJASyncChannel SyncChannel;
if (SyncChannel.Initialize(DeviceOptions, SyncOptions))
{
    // 主循环中等待同步
    if (SyncChannel.WaitForSync())
    {
        AJA::FTimecode Timecode;
        SyncChannel.GetTimecode(Timecode);
        UE_LOG(LogAjaCore, Log, TEXT("Sync: %02d:%02d:%02d:%02d"),
            Timecode.Hours, Timecode.Minutes, Timecode.Seconds, Timecode.Frames);
    }
}
```

**来源**：`Public/AJALib.h` 中 `AJASyncChannel` 和 `AJASyncChannelOptions` 定义

---

#### 读取时间码

```cpp
// 时间码通道：从 AJA 卡读取 LTC 或 VITC 时间码（来自 Public/AJALib.h: AJATimecodeChannel 类）

class FMyTimecodeCallback : public AJA::IAJATimecodeChannelCallbackInterface
{
public:
    virtual void OnInitializationCompleted(bool bSucceed) override {}
};

FMyTimecodeCallback TCCallback;

AJA::AJADeviceOptions DeviceOptions(0);
AJA::AJATimecodeChannelOptions TCOptions(TEXT("MyTimecodeChannel"));
TCOptions.CallbackInterface = &TCCallback;
TCOptions.bUseDedicatedPin = false;       // 从视频流读取时间码
TCOptions.TransportType = AJA::ETransportType::TT_SdiSingle;
TCOptions.ChannelIndex = 1;
TCOptions.VideoFormatIndex = /* format index */;
TCOptions.TimecodeFormat = AJA::ETimecodeFormat::TCF_VITC1;
TCOptions.bAutoDetectFormat = true;

AJA::AJATimecodeChannel TimecodeChannel;
if (TimecodeChannel.Initialize(DeviceOptions, TCOptions))
{
    AJA::FTimecode Timecode;
    if (TimecodeChannel.GetTimecode(Timecode))
    {
        UE_LOG(LogAjaCore, Log, TEXT("Timecode: %02d:%02d:%02d:%02d (DropFrame=%s)"),
            Timecode.Hours, Timecode.Minutes, Timecode.Seconds, Timecode.Frames,
            Timecode.bDropFrame ? TEXT("true") : TEXT("false"));
    }
}
```

**来源**：`Public/AJALib.h` 中 `AJATimecodeChannel` 和 `AJATimecodeChannelOptions` 定义

---

### 进阶用法

#### 初始化输入通道（捕获视频）

```cpp
// 输入通道回调接口（来自 Public/AJALib.h: IAJAInputOutputChannelCallbackInterface）
class FMyInputCallback : public AJA::IAJAInputOutputChannelCallbackInterface
{
public:
    virtual void OnInitializationCompleted(bool bSucceed) override
    {
        UE_LOG(LogAjaCore, Log, TEXT("Input channel init: %s"), bSucceed ? TEXT("OK") : TEXT("FAIL"));
    }
    
    // UE 请求输入缓冲区 — 你需要提供内存指针
    virtual bool OnRequestInputBuffer(
        const AJA::AJARequestInputBufferData& RequestBuffer,
        AJA::AJARequestedInputBufferData& OutRequestedBuffer) override
    {
        // 分配或提供预分配的缓冲区
        OutRequestedBuffer.VideoBuffer = /* your video buffer */;
        OutRequestedBuffer.AudioBuffer = /* your audio buffer (or nullptr) */;
        OutRequestedBuffer.AncBuffer   = /* your anc buffer (or nullptr) */;
        return true;
    }
    
    // 每帧输入回调 — 帧数据已到达
    virtual bool OnInputFrameReceived(
        const AJA::AJAInputFrameData& InFrameData,
        const AJA::AJAAncillaryFrameData& InAncillaryFrame,
        const AJA::AJAAudioFrameData& InAudioFrame,
        const AJA::AJAVideoFrameData& InVideoFrame) override
    {
        // InVideoFrame.VideoBuffer 中现在有原始像素数据
        // InVideoFrame.Width / Height / PixelFormat 描述了格式
        // InFrameData.Timecode 包含时间码
        // InFrameData.FramesDropped 告诉你 AJA 丢了多少帧
        
        UE_LOG(LogAjaCore, Log, TEXT("Frame received: %ux%u, Timecode=%02d:%02d:%02d:%02d, Dropped=%u"),
            InVideoFrame.Width, InVideoFrame.Height,
            InFrameData.Timecode.Hours, InFrameData.Timecode.Minutes,
            InFrameData.Timecode.Seconds, InFrameData.Timecode.Frames,
            InFrameData.FramesDropped);
        
        return true; // true = 继续接收
    }
    
    virtual void OnCompletion(bool bSucceed) override {}
    virtual bool OnOutputFrameCopied(const AJA::AJAOutputFrameData&) override { return true; }
};

// 初始化输入通道
FMyInputCallback InputCallback;

AJA::AJADeviceOptions DeviceOptions(0);
AJA::AJAInputOutputChannelOptions InputOptions(TEXT("MyInput"), 1); // ChannelIndex = 1
InputOptions.CallbackInterface = &InputCallback;
InputOptions.TransportType = AJA::ETransportType::TT_SdiSingle;
InputOptions.ChannelIndex = 1;
InputOptions.PixelFormat = AJA::EPixelFormat::PF_8BIT_ARGB;
InputOptions.TimecodeFormat = AJA::ETimecodeFormat::TCF_VITC1;
InputOptions.bOutput = false;
InputOptions.bUseVideo = true;
InputOptions.bUseAudio = true;
InputOptions.bUseAutoCirculating = true;
InputOptions.bAutoDetectFormat = true;
InputOptions.bStopOnTimeout = true;

AJA::AJAInputChannel InputChannel;
if (InputChannel.Initialize(DeviceOptions, InputOptions))
{
    // 输入通道现在在后台线程运行
    // 回调函数会在每帧被调用
    
    uint32_t DropCount = InputChannel.GetFrameDropCount();
    const AJA::AJAInputOutputChannelOptions& ActiveOptions = InputChannel.GetOptions();
}

// 不再需要时
InputChannel.Uninitialize();
```

**来源**：`Public/AJALib.h` 中 `AJAInputChannel`、`IAJAInputOutputChannelCallbackInterface`、`AJAInputOutputChannelOptions` 定义；`Private/InputChannel.h` 中 `InputChannelThread` 实现

---

## 内部架构

### 设备连接层

AjaCore 使用三层架构管理 AJA 硬件：

```
┌─────────────────────────────────────────────┐
│  Public API (AJALib.h)                      │
│  AJAInputChannel / AJASyncChannel / ...     │
├─────────────────────────────────────────────┤
│  Private Channels (ChannelThreadBase)       │
│  InputChannelThread / OutputChannelThread   │
├─────────────────────────────────────────────┤
│  DeviceConnection + DeviceCache             │
│  (管理 CNTV2Card 实例、命令队列、同步)       │
└─────────────────────────────────────────────┘
```

| 类 | 职责 |
|---|---|
| `DeviceCache` | 缓存最多 8 个 `DeviceConnection` 实例，避免重复初始化硬件 |
| `DeviceConnection` | 封装 `CNTV2Card`（AJA 原生卡对象），管理通道注册/注销、帧缓冲分配、垂直中断等待 |
| `DeviceCommand` | 命令模式：所有硬件操作通过命令队列发送到设备线程执行，保证线程安全 |
| `ChannelThreadBase` | 所有 I/O 通道线程的基类，管理 AutoCirculate/PingPong 循环、时间码烧录 |
| `Helpers` | 静态工具函数：像素格式转换、视频格式检测、SDI/HDMI 信号路由、HDR 元数据转换 |

### 传输类型

```cpp
enum class ETransportType  // 来自 Public/AJALib.h
{
    TT_SdiSingle,        // 单链路 SDI (最高 1080p60)
    TT_SdiSingle4kTSI,   // 单链路 SDI 4K TSI
    TT_SdiDual,          // 双链路 SDI
    TT_SdiQuadSQ,        // 四链路 SDI Square Division
    TT_SdiQuadTSI,       // 四链路 SDI TSI (2SI)
    TT_Hdmi,             // HDMI
    TT_Hdmi4kTSI,        // HDMI 4K TSI
};
```

### 像素格式

```cpp
enum struct EPixelFormat  // 来自 Public/AJALib.h
{
    PF_8BIT_YCBCR,    // 8-bit YCbCr 4:2:2
    PF_8BIT_ARGB,     // 8-bit ARGB
    PF_10BIT_RGB,     // 10-bit RGB (RGB 10-bit packed)
    PF_10BIT_YCBCR,   // 10-bit YCbCr 4:2:2
};
```

### HDR 元数据支持

```cpp
// 来自 Public/AJALib.h
struct FAjaHDROptions
{
    EAjaHDRMetadataEOTF EOTF = EAjaHDRMetadataEOTF::SDR;        // 传递函数: SDR/HLG/PQ
    EAjaHDRMetadataGamut Gamut = EAjaHDRMetadataGamut::Rec709;   // 色域: Rec709/Rec2020
    EAjaHDRMetadataLuminance Luminance = EAjaHDRMetadataLuminance::YCbCr; // 亮度格式
};
```

HDR 元数据从 AJA 卡的 VPID 寄存器自动读取（参见 `Helpers::GetInputHDRMetadata`）。

---

## 模块依赖

AjaCore 的 Build.cs 依赖：

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | Media IO 基础设施（视频格式描述、传输类型通用定义） |

无特殊依赖（仅标准 Core/Engine/Slate 等 + MediaIOCore）。AJA 原生 SDK 以第三方库方式通过 `THIRD_PARTY_INCLUDES_START` / `END` 包含。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 自动检测时正确填充媒体配置信息 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和采集卡添加引擎分析数据 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类调整和迁移 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 补充媒体源/输出子类的资产定义 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配 |

### 维护评价

- **活跃维护** ✅：最近 6 个月内有多次实质性更新，且 Epic 在持续投入
- **创建时间**：2018 年，是 UE4 时代的专业视频 I/O 解决方案
- **重要性**：虚拟制片（Virtual Production）工作流的核心基础设施之一，与 Blackmagic Media 并列为 UE 支持的两大专业视频卡插件
- **限制**：仅支持 Win64 平台；需要安装 AJA 驱动和 SDK；`EnabledByDefault=false`，需手动在项目设置中启用
- **推荐使用**：如果你在使用 AJA 硬件做虚拟制片或广播级视频 I/O，这是官方唯一支持的解决方案，强烈推荐使用

> ⚠️ 此插件需要物理 AJA 采集卡才能运行。无卡环境下的开发和测试可能需要 mock 层。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia)
- [官方文档](https://docs.unrealengine.com/en-US/working-with-media/media-integrations/aja/)
- [AJA 官方网站](https://www.aja.com/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia/Tests)