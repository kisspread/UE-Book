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
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途

该插件为 Unreal Engine 提供与 Blackmagic Design DeckLink 采集卡的硬件集成，实现高带宽、低延迟的视频与音频的实时捕获（输入）和输出功能。它解决了在虚拟制片、实时合成、广播和广播级监控等专业工作流中，需要将 UE 的渲染输出以广播级质量实时传输到外部设备（如切换器、监视器、投影仪）的需求。其核心是封装了 Blackmagic SDK，提供了与硬件交互的稳定接口，并管理复杂的视频音频同步、时间码处理和硬件缓冲区。

## 使用场景

- **虚拟制片 (Virtual Production)**：将 UE 的实时渲染画面通过 SDI/HDMI 输出到 LED 墙或摄影机监视器，实现摄像机内视觉特效 (In-Camera VFX)。
- **广播与实时图文包装 (Broadcast & Live Graphics)**：将 UE 生成的动态图形（如体育赛事数据、新闻包装）以 SDI 信号嵌入到传统广播流程中。
- **高端监控与质量控制 (High-End Monitoring & QC)**：使用支持专业色彩空间（如 HDR、10-bit 4:4:4）的 Blackmagic 卡，以最高质量监看 UE 输出，进行色彩校正或细节检查。
- **多路输出**：利用单卡或多卡，同时向多个显示设备或录制设备输出不同分辨率或格式的信号。

## 蓝图用法

该插件主要通过 Media Framework 体系集成，在蓝图中主要通过 `MediaPlayer`, `MediaSource` 和 `MediaCapture` 等通用媒体类操作。

### 核心节点

由于 Blackmagic 的具体控制大多封装在 C++ 层，蓝图主要通过通用的媒体框架节点间接使用。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开指定的 Blackmagic Media Source 开始捕获。 | `UMediaPlayer` |
| `Close` | 关闭当前媒体源，停止捕获。 | `UMediaPlayer` |
| `Play` | 开始或恢复捕获/播放。 | `UMediaPlayer` |
| `Pause` | 暂停捕获/播放。 | `UMediaPlayer` |
| `Start Capture` | 启动媒体捕获，将渲染输出发送到指定的 Blackmagic 设备。 | `UMediaCapture` |
| `Stop Capture` | 停止媒体捕获。 | `UMediaCapture` |

### 使用示例（蓝图描述）

1.  **视频捕获（输入）**：
    *   创建一个 `Media Player` 资产。
    *   创建一个 `Blackmagic Media Source` 资产，在其中配置输入设备、视频格式、音频通道等参数。
    *   在蓝图中，使用 `Create Media Player` 节点创建一个 `MediaPlayer` 组件或对象。
    *   调用 `Open Source` 节点，将 `Blackmagic Media Source` 连接到 `MediaPlayer`。
    *   调用 `Play` 节点开始捕获。捕获到的画面将作为 `MediaPlayer` 的输出纹理，可以应用到 Material 或 Media Texture 上。

2.  **视频输出（输出）**：
    *   创建一个 `Blackmagic Media Output` 资产，配置输出设备、分辨率、帧率、音频设置等。
    *   创建一个 `Media Capture` 组件，附加到场景中的 `SceneCaptureComponent2D` 或 `Viewport` 上。
    *   在 `Media Capture` 组件上设置 `Media Output` 为你创建的 `Blackmagic Media Output`。
    *   调用 `Start Capture` 节点，开始将指定视口或渲染目标的内容实时输出到 Blackmagic 硬件。

## C++ 用法

C++ 层面通过 `BlackmagicCore` 模块提供的底层 API 进行更精细的控制。

### 头文件引入

```cpp
#include "BlackmagicLib.h" // 核心公共接口
#include "BlackmagicCoreModule.h" // 模块状态查询
```

### 基本用法

以下是初始化和使用 Blackmagic 设备的基础流程。

```cpp
// 来源于 Public/BlackmagicLib.h 和 Public/BlackmagicCoreModule.h 的接口定义
#include "BlackmagicLib.h"

// 1. 检查模块是否可用
FBlackmagicCoreModule* CoreModule = FModuleManager::GetModulePtr<FBlackmagicCoreModule>("BlackmagicCore");
if (CoreModule && CoreModule->IsInitialized() && CoreModule->CanUseBlackmagicCard())
{
    UE_LOG(LogTemp, Log, TEXT("Blackmagic Core 模块已初始化且可用。"));
}

// 2. 初始化 Blackmagic API
bool bSuccess = BlackmagicDesign::ApiInitialization();
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Blackmagic API 初始化成功。"));
}

// 3. 扫描可用设备
BlackmagicDesign::BlackmagicDeviceScanner DeviceScanner;
int32_t NumDevices = DeviceScanner.GetNumDevices();
UE_LOG(LogTemp, Log, TEXT("找到 %d 个 Blackmagic 设备。"), NumDevices);

for (int32 i = 0; i < NumDevices; ++i)
{
    BlackmagicDesign::BlackmagicDeviceScanner::FormatedTextType DeviceTextId;
    if (DeviceScanner.GetDeviceTextId(i, DeviceTextId))
    {
        UE_LOG(LogTemp, Log, TEXT("设备 %d: %s"), i, DeviceTextId);
    }
    
    BlackmagicDesign::BlackmagicDeviceScanner::DeviceInfo Info;
    if (DeviceScanner.GetDeviceInfo(i, Info))
    {
        UE_LOG(LogTemp, Log, TEXT("  - 支持捕获: %s, 支持播放: %s"), Info.bCanDoCapture ? TEXT("是") : TEXT("否"), Info.bCanDoPlayback ? TEXT("是") : TEXT("否"));
    }
}

// ... 后续使用完成后调用 ApiUninitialization()。
```

### 进阶用法

以下示例展示了如何注册回调以接收输入帧，以及如何输出一帧视频数据。

```cpp
// 来源于 Public/BlackmagicLib.h 中的回调接口定义和函数
#include "BlackmagicLib.h"

// 定义一个实现 IInputEventCallback 的类来接收输入帧
class FMyBlackmagicInputCallback : public BlackmagicDesign::IInputEventCallback
{
public:
    // ... 实现 AddRef, Release 等虚函数 ...

    virtual void OnInitializationCompleted(bool bSuccess) override
    {
        UE_LOG(LogTemp, Log, TEXT("输入通道初始化完成，状态: %s"), bSuccess ? TEXT("成功") : TEXT("失败"));
    }

    virtual void OnShutdownCompleted() override {}

    virtual void OnFrameReceived(const FFrameReceivedInfo& FrameInfo) override
    {
        // 在此处理接收到的视频帧 (FrameInfo.VideoBuffer) 和音频帧 (FrameInfo.AudioBuffer)
        // 注意：此回调可能在非游戏线程触发，注意线程安全
        UE_LOG(LogTemp, Verbose, TEXT("接收到帧 #%lld"), FrameInfo.FrameNumber);
    }

    virtual void OnFrameFormatChanged(const FFormatInfo& NewFormat) override
    {
        UE_LOG(LogTemp, Log, TEXT("输入格式变化: %dx%d @ %d/%d fps"), NewFormat.Width, NewFormat.Height, NewFormat.FrameRateNumerator, NewFormat.FrameRateDenominator);
    }
};

// 注册输入通道
BlackmagicDesign::FChannelInfo InputChannelInfo;
InputChannelInfo.DeviceIndex = 0; // 使用第一个设备

BlackmagicDesign::FInputChannelOptions InputOptions;
InputOptions.bReadVideo = true;
InputOptions.bReadAudio = true;
// ... 配置其他选项 ...

TSharedPtr<FMyBlackmagicInputCallback> InputCallback = MakeShared<FMyBlackmagicInputCallback>();
BlackmagicDesign::FUniqueIdentifier InputCallbackId = BlackmagicDesign::RegisterCallbackForChannel(InputChannelInfo, InputOptions, InputCallback.Get());

// ... 当不再需要输入时，注销回调 ...
// BlackmagicDesign::UnregisterCallbackForChannel(InputChannelInfo, InputCallbackId);

// 输出示例
BlackmagicDesign::FChannelInfo OutputChannelInfo;
OutputChannelInfo.DeviceIndex = 0;

BlackmagicDesign::FOutputChannelOptions OutputOptions;
OutputOptions.bOutputVideo = true;
OutputOptions.bOutputAudio = false; // 假设只输出视频
// ... 配置格式、缓冲区数量等 ...

// 假设有一个实现 IOutputEventCallback 的类 MyOutputCallback
TSharedPtr<IMyOutputCallback> OutputCallback = MakeShared<MyOutputCallback>();
BlackmagicDesign::FUniqueIdentifier OutputCallbackId = BlackmagicDesign::RegisterOutputChannel(OutputChannelInfo, OutputOptions, OutputCallback.Get());

// 准备一帧数据 (例如从 RHITexture 复制)
BlackmagicDesign::FFrameDescriptor FrameDesc;
// ... 填充 FrameDesc 的视频缓冲区、宽、高、时间码等信息 ...
bool bSent = BlackmagicDesign::SendVideoFrameData(OutputChannelInfo, FrameDesc);

// ... 当不再需要输出时，注销通道 ...
// BlackmagicDesign::UnregisterOutputChannel(OutputChannelInfo, OutputCallbackId, true);
```

## Demo 示例

一个最小的、可编译的 C++ 示例，演示如何初始化 Blackmagic API 并列出设备。

```cpp
// MyBlackmagicDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyBlackmagicDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyBlackmagicDemo.cpp
#include "MyBlackmagicDemo.h"
#include "BlackmagicLib.h"
#include "BlackmagicCoreModule.h"

void FMyBlackmagicDemoModule::StartupModule()
{
    // 检查并初始化核心模块
    FBlackmagicCoreModule* CoreModule = FModuleManager::GetModulePtr<FBlackmagicCoreModule>("BlackmagicCore");
    if (!CoreModule || !CoreModule->IsInitialized())
    {
        UE_LOG(LogTemp, Error, TEXT("BlackmagicCore 模块未加载或未初始化。"));
        return;
    }

    // 初始化 Blackmagic API
    if (!BlackmagicDesign::ApiInitialization())
    {
        UE_LOG(LogTemp, Error, TEXT("Blackmagic API 初始化失败。"));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Blackmagic API 初始化成功。正在扫描设备..."));

    // 扫描设备
    BlackmagicDesign::BlackmagicDeviceScanner Scanner;
    int32 NumDevices = Scanner.GetNumDevices();
    UE_LOG(LogTemp, Log, TEXT("发现 %d 个 Blackmagic 设备。"), NumDevices);

    for (int32 i = 0; i < NumDevices; ++i)
    {
        BlackmagicDesign::BlackmagicDeviceScanner::FormatedTextType TextId;
        if (Scanner.GetDeviceTextId(i, TextId))
        {
            UE_LOG(LogTemp, Log, TEXT("  设备 %d: %s"), i, TextId);
        }
    }
}

void FMyBlackmagicDemoModule::ShutdownModule()
{
    // 清理 API
    BlackmagicDesign::ApiUninitialization();
    UE_LOG(LogTemp, Log, TEXT("Blackmagic API 已释放。"));
}

IMPLEMENT_MODULE(FMyBlackmagicDemoModule, MyBlackmagicDemo)
```

## 模块依赖

要使用 `BlackmagicCore` 模块（或整个 BlackmagicMedia 插件），你的模块需要依赖以下内容。

| 模块 | 用途 |
|---|---|
| `BlackmagicCore` | 核心封装层，提供与 Blackmagic SDK 交互的 API 和设备管理。 |
| `MediaUtils` | 通用媒体框架工具，与 UE 的媒体系统集成所需。 |
| `RenderCore` | 访问渲染硬件接口 (RHI)，用于 GPU-DMA 等高级视频数据传输。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `fe681f84` | MediaIO: Fix Blackmagic auto-detect misinterpreting interlaced signals as progressive. | 修复了黑魔法卡自动检测将隔行信号误判为逐行的问题。 |
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为黑魔法和AJA卡的自动模式填充了媒体配置。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro... | 为多个媒体播放器和捕获功能添加了引擎分析信息。 |
| 2026-05-12 | `b7bb4354` | Media IO - Fix bob deinterlacer field samples sharing source-frame timestamp | 修复了 bob 去隔行器中字段采样共享源帧时间戳的问题。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 将虚拟制片相关资产移动到了不同的资产类别。 |

### 维护评价

该插件作为虚拟制片和广播领域的关键硬件接口，**处于活跃维护状态**。最近（2026年5月）有多次针对自动检测、信号处理和去隔行算法的修复与增强，表明 Epic Games 持续投入资源解决专业用户的实际问题。

*   **优点**：功能稳定，深度集成硬件，支持高级特性如 HDR、10-bit、Timecode、GPU-DMA。
*   **注意**：由于依赖特定硬件和第三方 SDK (`BlackmagicSDK`)，跨平台移植性受限（目前支持 Win64 和 Linux）。启用此插件需要用户自行安装 Blackmagic Desktop Video 驱动程序。
*   **推荐**：对于需要 Blackmagic 硬件集成的虚拟制片、广播或监控项目，**强烈推荐使用**。对于没有此类需求的项目，则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/media-framework-in-unreal-engine/) （注：此为通用 Media Framework 文档，无专门的 Blackmagic 插件页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Plugins/Media/BlackmagicMedia) （注：根据插件规模，测试代码可能位于 Engine/Tests 目录下）