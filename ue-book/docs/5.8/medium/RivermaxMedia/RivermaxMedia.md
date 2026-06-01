# NVIDIA Rivermax Media Streaming

> Adding NVIDIA Rivermax capabilities for Media Captures and Media Players

| 属性 | 值 |
|---|---|
| 中文名 | Rivermax 媒体流 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxMedia` (Runtime), `RivermaxMediaEditor` (Runtime), `RivermaxMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia) | |

## 用途

本插件基于 NVIDIA Rivermax SDK，为 Unreal Engine 的 Media Framework 提供 **SMPTE ST 2110** 标准的 IP 视频收发能力。它解决的核心问题是：在虚拟制作（Virtual Production）场景中，需要通过专业 IP 网络（而非传统 SDI/HDMI）实时接收和发送广播级视频流。

具体来说，该插件包含两个主要功能方向：

1. **媒体播放器（Player）**：通过 Rivermax Input Stream 接收 ST 2110-20 视频流和 ST 2110-40 辅助数据（ANC，如时间码），在引擎中实时回放 IP 视频。
2. **媒体捕获（Capture）**：通过 Rivermax Output Stream 将引擎渲染画面通过 IP 网络发送出去，支持 GPUDirect 实现 GPU 到网卡的零拷贝传输。

此外还提供基于 PTP 时钟的 **Genlock**（同步锁相）和 **Timecode Provider**，确保引擎与外部设备精确同步。

## 使用场景

- 你在搭建 **nDisplay 多屏渲染** 或 **LED 虚拟墙** 系统，需要通过 ST 2110 IP 网络将多台渲染机器的画面同步输出到 LED 控制器
- 你在做 **现场直播制作（Live Production）**，需要从专业摄像机通过 IP 网络接收实时视频流到 Unreal Engine 中做实时合成
- 你需要从外部 **PTP 主时钟** 获取精确时间码，保持引擎与广播设备时间同步
- 你需要通过 **Genlock** 让引擎帧率与外部同步信号精确对齐

## 蓝图用法

### 核心资产类型

本插件通过 Media Framework 的资产驱动方式工作，主要涉及以下蓝图可见资产类：

| 资产类 | 说明 | 类型 |
|---|---|---|
| `URivermaxMediaSource` | 配置输入流参数（地址、端口、分辨率、像素格式等） | MediaSource |
| `URivermaxMediaOutput` | 配置输出流参数（对齐模式、连续输出、帧锁定等） | MediaOutput |
| `URivermaxTimecodeProvider` | 基于 Rivermax PTP 时钟的时间码提供器 | TimecodeProvider |
| `URivermaxCustomTimeStep` | 基于 Rivermax PTP 时钟的 Genlock 自定义时间步进 | CustomTimeStep |

### 核心属性 — 媒体源 (`URivermaxMediaSource`)

| 属性 | 说明 |
|---|---|
| `VideoStream` | 视频流配置结构体（接口地址、流地址、端口、帧率、分辨率、像素格式、GPUDirect） |
| `AncStreams` | ANC 辅助数据流数组（如 ST 2110-40 时间码） |

### 核心属性 — 媒体输出 (`URivermaxMediaOutput`)

| 属性 | 说明 |
|---|---|
| `AlignmentMode` | 对齐模式：`AlignmentPoint`（PTP 时钟对齐）或 `FrameCreation`（帧创建对齐） |
| `bDoContinuousOutput` | 是否在无新帧时重复发送最后一帧（仅 AlignmentPoint 模式） |
| `FrameLockingMode` | 帧锁定模式：`FreeRun`（无缓冲则跳过）或 `BlockOnReservation`（阻塞等待） |
| `bDoFrameCounterTimestamping` | 实验性：使用帧计数器替代 PTP 时钟时间戳（适用于 UE-UE 流，如 nDisplay） |
| `VideoStream` | 视频输出流配置 |
| `AncStreams` | ANC 辅助数据输出流 |

### 核心属性 — 时间码提供器 (`URivermaxTimecodeProvider`)

| 属性 | 说明 |
|---|---|
| `FrameRate` | 提供时间码的帧率 |
| `PTPToLTCTimecodeFrameOffset` | PTP 到 LTC 时间码的帧偏移补偿（默认 1） |
| `UTCSecondsOffset` | TAI 到 UTC 的秒偏移（默认 37 秒） |
| `DaylightSavingTimeHourOffset` | 夏令时偏移（小时） |

### 核心属性 — Genlock (`URivermaxCustomTimeStep`)

| 属性 | 说明 |
|---|---|
| `FrameRate` | 目标同步帧率，使用 ST 2059 标准将 PTP 时间对齐到标准 Genlock |
| `AlignmentPointDelayMS` | 从对齐点开始的延迟（毫秒） |
| `bEnableOverrunDetection` | 引擎太慢时是否警告丢帧 |

### 蓝图使用方式

本插件不暴露额外的 `BlueprintCallable` 节点。所有功能通过 Media Framework 的标准资产驱动方式使用：

1. **播放 IP 视频流**：在项目设置或场景中创建 `URivermaxMediaSource` 资产，配置网络参数，然后在 Media Player 组件中引用它
2. **捕获输出 IP 流**：创建 `URivermaxMediaOutput` 资产，配置输出参数，然后通过 `UMediaCapture` API 启动捕获
3. **Genlock 同步**：在项目设置 → Time & Synchronization 中选择 `URivermaxCustomTimeStep` 作为自定义时间步进
4. **时间码同步**：在项目设置中选择 `URivermaxTimecodeProvider` 作为时间码提供器

## C++ 用法

### 头文件引入

```cpp
#include "IRivermaxMediaModule.h"
#include "RivermaxMediaSource.h"
#include "RivermaxMediaOutput.h"
#include "RivermaxMediaCapture.h"
#include "RivermaxMediaTypes.h"
#include "RivermaxTimecodeProvider.h"
#include "RivermaxCustomTimeStep.h"
```

### 基本用法 — 创建媒体播放器

通过模块接口创建 Rivermax 媒体播放器：

```cpp
// 引自 Public/IRivermaxMediaModule.h
#include "IRivermaxMediaModule.h"

if (IRivermaxMediaModule::IsAvailable())
{
    // 通过模块接口创建播放器，接收媒体事件
    IMediaEventSink& EventSink = /* your event sink */;
    TSharedPtr<IMediaPlayer> Player = IRivermaxMediaModule::Get().CreatePlayer(EventSink);
}
```

### 基本用法 — 配置媒体源（输入）

```cpp
#include "RivermaxMediaSource.h"

// 创建 Rivermax 媒体源
URivermaxMediaSource* MediaSource = NewObject<URivermaxMediaSource>();

// 配置视频流
MediaSource->VideoStream.InterfaceAddress = TEXT("192.168.1.100");  // 网卡接口
MediaSource->VideoStream.StreamAddress = TEXT("239.1.1.1");         // 多播地址
MediaSource->VideoStream.Port = 50000;                               // UDP 端口
MediaSource->VideoStream.FrameRate = FFrameRate(24, 1);              // 帧率
MediaSource->VideoStream.Resolution = FIntPoint(1920, 1080);        // 分辨率
MediaSource->VideoStream.bOverrideResolution = true;
MediaSource->VideoStream.PixelFormat = ERivermaxPixelFormat::RGB_10bit;
MediaSource->VideoStream.bUseGPUDirect = true;                       // 启用 GPUDirect

// 配置 ANC 辅助数据流（接收时间码）
FRivermaxAncStream AncStream;
AncStream.StreamType = ERivermaxAncStreamType::ST2110_40_TC;
AncStream.InterfaceAddress = TEXT("192.168.1.100");
AncStream.StreamAddress = TEXT("239.1.1.1");
AncStream.Port = 50001;
MediaSource->AncStreams.Add(AncStream);
```

### 基本用法 — 配置媒体输出（捕获）

```cpp
#include "RivermaxMediaOutput.h"

// 创建 Rivermax 媒体输出
URivermaxMediaOutput* MediaOutput = NewObject<URivermaxMediaOutput>();

// 配置输出模式
MediaOutput->AlignmentMode = ERivermaxMediaAlignmentMode::AlignmentPoint;
MediaOutput->bDoContinuousOutput = true;
MediaOutput->FrameLockingMode = ERivermaxFrameLockingMode::BlockOnReservation;

// 配置视频流
MediaOutput->VideoStream.InterfaceAddress = TEXT("192.168.1.100");
MediaOutput->VideoStream.StreamAddress = TEXT("239.1.1.2");
MediaOutput->VideoStream.Port = 50000;
MediaOutput->VideoStream.FrameRate = FFrameRate(60, 1);
MediaOutput->VideoStream.PixelFormat = ERivermaxPixelFormat::RGB_10bit;
MediaOutput->VideoStream.bUseGPUDirect = true;
```

### 进阶用法 — 获取捕获的流信息和 SDP

```cpp
#include "RivermaxMediaCapture.h"

// 假设已有捕获实例
URivermaxMediaCapture* Capture = /* your capture */;

// 获取输出选项
FRivermaxOutputOptions Options = Capture->GetOutputOptions();

// 获取最后呈现的帧信息
FPresentedFrameInfo FrameInfo;
Capture->GetLastPresentedFrameInformation(FrameInfo);

// 导出 SDP 文件（用于与其他 ST 2110 设备互操作）
MediaOutput->ExportSDP(TEXT("/path/to/output.sdp"));
```

### 进阶用法 — 像素格式转换工具

```cpp
#include "RivermaxMediaUtils.h"

// 在 Rivermax 像素格式和引擎采样类型之间转换
ESamplingType SamplingType = UE::RivermaxMediaUtils::Private::PixelFormatToRivermaxSamplingType(
    ERivermaxPixelFormat::YUV422_10bit
);

// 获取对齐后的分辨率（满足 ST 2110-20 像素组对齐要求）
FVideoFormatInfo FormatInfo = /* format info */;
FIntPoint AlignedRes = UE::RivermaxMediaUtils::Private::GetAlignedResolution(
    FormatInfo, FIntPoint(1920, 1080)
);

// 计算最优 UDP 载荷大小
FPayloadSizeInformation PayloadInfo;
UE::RivermaxMediaUtils::Private::FindPayloadSize(BytesPerLine, PixelGroupSize, PayloadInfo);
```

## Demo 示例

### Genlock + Timecode Provider 配置示例

```cpp
// MyVirtualProductionGame.h
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyVirtualProductionGame.generated.h"

UCLASS()
class AMyVirtualProductionGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};
```

```cpp
// MyVirtualProductionGame.cpp
#include "MyVirtualProductionGame.h"
#include "RivermaxMediaSource.h"
#include "RivermaxMediaOutput.h"
#include "RivermaxMediaCapture.h"
#include "IRivermaxMediaModule.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MediaCapture.h"

void AMyVirtualProductionGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 1. 配置视频输入源
    URivermaxMediaSource* InputSource = NewObject<URivermaxMediaSource>();
    InputSource->VideoStream.InterfaceAddress = TEXT("*.*.*.*");
    InputSource->VideoStream.StreamAddress = TEXT("239.1.1.1");
    InputSource->VideoStream.Port = 50000;
    InputSource->VideoStream.FrameRate = FFrameRate(24, 1);
    InputSource->VideoStream.bOverrideResolution = true;
    InputSource->VideoStream.Resolution = FIntPoint(1920, 1080);
    InputSource->VideoStream.PixelFormat = ERivermaxPixelFormat::RGB_10bit;
    InputSource->VideoStream.bUseGPUDirect = true;

    // 2. 配置 ANC 时间码输入
    FRivermaxAncStream TimecodeStream;
    TimecodeStream.StreamType = ERivermaxAncStreamType::ST2110_40_TC;
    TimecodeStream.InterfaceAddress = TEXT("*.*.*.*");
    TimecodeStream.StreamAddress = TEXT("239.1.1.1");
    TimecodeStream.Port = 50001;
    InputSource->AncStreams.Add(TimecodeStream);

    // 3. 创建播放器并通过 Media Framework 打开
    if (IRivermaxMediaModule::IsAvailable())
    {
        // 播放器通常通过 UMediaPlayer 打开 UMediaSource 来间接创建
        // IMediaEventSink 由 UMediaPlayer 内部管理
        UE_LOG(LogTemp, Log, TEXT("Rivermax Media module is available, media source configured."));
    }

    // 4. 配置输出捕获
    URivermaxMediaOutput* Output = NewObject<URivermaxMediaOutput>();
    Output->AlignmentMode = ERivermaxMediaAlignmentMode::AlignmentPoint;
    Output->bDoContinuousOutput = true;
    Output->FrameLockingMode = ERivermaxFrameLockingMode::FreeRun;
    Output->VideoStream.InterfaceAddress = TEXT("192.168.1.100");
    Output->VideoStream.StreamAddress = TEXT("239.1.1.2");
    Output->VideoStream.Port = 50000;
    Output->VideoStream.FrameRate = FFrameRate(60, 1);
    Output->VideoStream.PixelFormat = ERivermaxPixelFormat::RGB_10bit;
    Output->VideoStream.bUseGPUDirect = true;

    // 通过 Media Capture 启动捕获
    UMediaCapture* Capture = Output->CreateMediaCapture();
    if (Capture)
    {
        // Capture->CaptureSceneViewport(); 或 Capture->CaptureRenderTarget(RenderTarget);
        UE_LOG(LogTemp, Log, TEXT("Rivermax media capture created successfully."));
    }
}
```

## 模块依赖

本插件依赖 NVIDIA Rivermax Core 插件和 Media Framework 基础模块。仅列出独特依赖：

| 模块 | 用途 |
|---|---|
| `RivermaxCore` | NVIDIA Rivermax SDK 的核心封装层，提供输入/输出流和 Rivermax 管理器 |
| `MediaIOCore` | Media Framework 的 IO 核心模块，提供 `FMediaIOCorePlayerBase` 和 `UMediaCapture` 基类 |
| `RenderCore` | GPU 渲染核心（RDG、GPU Fence 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为多个媒体播放器和捕获添加了分析数据追踪 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double-to-float 截断警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整虚拟制作资产的分类归属 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 补充 MediaSource 和 MediaOutput 子类的资产定义注册 |
| 2026-04-28 | `3348026a` | Rivermax: ANC timecode input, input stream base class refactor, and pixel format unification | 新增 ANC 时间码输入、重构输入流基类、统一像素格式枚举 |

### 维护评价

- **活跃维护**：最近 1 个月内有多次功能性更新（ANC 时间码输入、像素格式统一、分析数据等），持续迭代中
- **仍在演进**：从 5.7 到 5.8 版本经历了大量 API 重构（废弃了旧的扁平属性，迁移到 `FRivermaxVideoStream` 结构体），说明接口仍在趋于稳定
- **实验性状态**：标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，API 可能在未来版本继续变化
- **建议**：适合在受控的虚拟制作项目中使用，但需要注意升级时可能的 API 变更。大量 `UE_DEPRECATED` 标记表明接口正在积极整理中，建议使用最新的结构化配置方式（`FRivermaxVideoStream` / `FRivermaxAncStream`）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia/Tests)（如有）