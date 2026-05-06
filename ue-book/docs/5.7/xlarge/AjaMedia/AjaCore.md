# AJA Media Player

> Implements input and output using AJA Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | AJA 媒体播放器核心 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++ 模块、底层 AJA SDK 封装） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia) | |

## 用途

AjaCore 是 AJA Media Player 插件的核心运行时模块。它直接封装了 AJA SDK（`ajantv2`），提供了与 AJA 采集/输出卡进行底层通信的 C++ 接口。其主要功能包括：

- **设备管理与扫描**：枚举系统中的 AJA 设备，获取设备信息及支持的视频格式。
- **输入通道**：从指定设备接收视频、音频、辅助数据（ANC）及时间码。
- **输出通道**：向指定设备发送视频、音频、辅助数据，支持 GPU 直接纹理传输（`GPUTextureTransfer`）以降低延迟。
- **同步通道**：用于 Genlock 同步，等待垂直同步信号并获取同步计数。
- **时间码通道**：独立的时间码读取通道，支持 LTC、VITC 等源。
- **自动侦测通道**：自动检测通道上的视频格式、信号状态等。

本模块解决了 Unreal Engine 需要与专业广播级 AJA 硬件进行实时视频 I/O 的需求，是直播、虚拟制片、实时回放等应用的底层基础。

## 使用场景

- **虚拟制片（VP）**：将 UE 渲染画面通过 AJA 卡输出到 LED 墙或投影，同时接收摄像机信号作为合成源。
- **实时直播**：从 AJA 卡输入直播信号，叠加 UE 图形后再输出。
- **广播级回放**：精确控制帧率、时间码同步的媒体回放。
- **颜色校准与测试**：输出测试图案进行信号检测。
- **多通道同步**：使用 Genlock 信号同步多张 AJA 卡或与其他设备对时。

## 蓝图用法

AjaCore 是一个纯 C++ 模块，不暴露任何蓝图可调用函数。蓝图层面的媒体功能由 `AjaMedia` 模块（基于 `MediaIOCore`）提供，例如 `AjaMediaSource`、`AjaMediaOutput` 等。如果你需要直接通过蓝图控制 AJA 硬件，请参考 `AjaMedia` 或 `AjaMediaOutput` 模块的文档。

## C++ 用法

### 头文件引入

```cpp
#include "AJALib.h"       // 所有公有类型和接口
#include "AjaCoreModule.h" // 模块类及日志
```

### 基本用法

#### 1. 扫描设备并获取信息

```cpp
#include "AJALib.h"

AJA::AJADeviceScanner Scanner;
int32 NumDevices = Scanner.GetNumDevices();

for (int32 i = 0; i < NumDevices; ++i)
{
    AJA::AJADeviceScanner::DeviceInfo Info;
    if (Scanner.GetDeviceInfo(i, Info))
    {
        // Info.bIsSupported, Info.TextId, etc.
    }
}
```

#### 2. 创建并启动输入通道

```cpp
#include "AJALib.h"

// 设备选项
AJA::AJADeviceOptions DeviceOptions;
DeviceOptions.DeviceIndex = 0; // 使用第一个设备

// 通道选项
AJA::AJAInputOutputChannelOptions ChannelOptions;
ChannelOptions.bOutput = false;          // 输入模式
ChannelOptions.Channel = NTV2_CHANNEL1; // 物理通道
ChannelOptions.VideoFormatIndex = ...;   // 通过 VideoFormatsScanner 获取
ChannelOptions.PixelFormat = AJA::EPixelFormat::PF_10BIT_YCBCR;
ChannelOptions.bUseVideo = true;
ChannelOptions.bUseAudio = false;
ChannelOptions.TimecodeFormat = AJA::ETimecodeFormat::TCF_LTC;

// 创建通道对象
auto InputChannel = std::make_shared<AJA::Private::InputChannel>();
if (InputChannel->Initialize(DeviceOptions, ChannelOptions))
{
    // 通道已启动，可在回调中接收帧数据
    // ...
}
// 使用完毕后调用 InputChannel->Uninitialize();
```

#### 3. 输出通道发送视频帧

```cpp
#include "AJALib.h"
#include "GPUTextureTransferModule.h"

AJA::AJADeviceOptions DeviceOptions{0};
AJA::AJAInputOutputChannelOptions ChannelOptions;
ChannelOptions.bOutput = true;
ChannelOptions.Channel = NTV2_CHANNEL1;
ChannelOptions.PixelFormat = AJA::EPixelFormat::PF_10BIT_YCBCR;

auto OutputChannel = std::make_shared<AJA::Private::OutputChannel>();
if (OutputChannel->Initialize(DeviceOptions, ChannelOptions))
{
    // 从 UE 渲染线程获取 RHI 纹理
    FRHITexture* RenderTarget = ...;
    
    AJA::AJAOutputFrameBufferData FrameData;
    FrameData.FrameNumber = ...; // 帧序号
    FrameData.Timecode = ...;    // 可选时间码
    
    OutputChannel->SetVideoFrameData(FrameData, RenderTarget);
}
```

完整用例可参考 `Engine/Plugins/Media/AjaMedia/Source/AjaMedia/` 下的 `AjaMediaPlayer` 实现。

## Demo 示例

以下是一个最小可编译的 C++ 类，演示如何扫描 AJA 设备并打印设备信息。

```cpp
// MyAjaDeviceScanner.h
#pragma once
#include "CoreMinimal.h"
#include "AJALib.h"

class FMyAjaDeviceScanner
{
public:
    static void ScanAndPrint()
    {
        AJA::AJADeviceScanner Scanner;
        int32 NumDevices = Scanner.GetNumDevices();
        UE_LOG(LogTemp, Log, TEXT("Found %d AJA device(s)."), NumDevices);
        
        for (int32 i = 0; i < NumDevices; ++i)
        {
            AJA::AJADeviceScanner::DeviceInfo Info;
            if (Scanner.GetDeviceInfo(i, Info))
            {
                AJA::AJADeviceScanner::FormatedTextType TextId;
                Scanner.GetDeviceTextId(i, TextId);
                UE_LOG(LogTemp, Log, TEXT("  Device %d: %s (Supported=%d)"), i, TextId, Info.bIsSupported);
            }
        }
    }
};

// 在你的某个 GameInstance 或 Module 启动时调用
// FMyAjaDeviceScanner::ScanAndPrint();
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AjaCore` 自身 | 无特殊依赖（仅标准 Core/Engine/Slate 等） |

**说明**：AjaCore 是一个扁平化的底层模块，其依赖已在 `AjaCore.Build.cs` 中隐式链接 AJA SDK 和 GPU 纹理传输模块（`GPUTextureTransfer`），使用者不需要显式添加这些模块。在构建你的模块时，如果只需要 AJA 底层 API，将 `AjaCore` 加入 `PublicDependencyModuleNames` 即可。

## 维护状态

### 近期更新

- 2025-10-17 `ab15e769` Media IO - Fix crash when refreshing media properties for Aja source
- 2025-09-24 `5ef7a9a2` Aja - Add a new output mode that can reduce latency by up to 1 frame.
- 2025-09-24 `94f6a824` Aja - Add option to continue input, output and genlock when card timeouts
- 2025-08-20 `5f63edc0` Update Aja SDK to 17.5.0
- 2025-08-18 `5b28eda8` Aja - Add an option to discard interlace frames if they land on an odd frame.

### 维护评价

- **活跃维护**：最近 3 个月内有功能更新（低延迟模式、超时恢复）、Bug 修复及 SDK 升级。
- **年龄**：仅约 1 年（从首次提交算起），属于较新模块。
- **推荐**：强烈推荐用于需要 AJA 硬件交互的 UE5 项目。模块设计良好，充分利用 UE5 异步和线程模型，并支持现代特性（GPU 纹理传输、HDR 元数据等）。
- **已知限制**：仅支持 Windows 64 位平台；对非 AJA 硬件无替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/working-with-aja-media-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia/Tests)