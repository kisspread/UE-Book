# Blackmagic Media Player

> Implements input and output using Blackmagic Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | Blackmagic 采集卡媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicCore` (Runtime), `BlackmagicMedia` (Runtime), `BlackmagicMediaEditor` (Runtime), `BlackmagicMediaFactory` (Runtime), `BlackmagicMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-06-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途

该插件封装了 Blackmagic Design 采集卡（如 DeckLink 系列）的 SDK，使 Unreal Engine 能够通过 SDI/HDMI 接口**实时输入和输出视频、音频以及时间码**。它提供了与 UE 媒体框架（Media Framework）、Genlock 同步系统、时间码系统的深度集成，是广播级虚拟制片、现场制作、实时演播室等场景的核心组件。

## 使用场景

- **虚拟制片**：将外部摄影机信号（如 ARRI、RED 等）通过 Blackmagic 卡输入到 UE，实现实时合成与渲染。
- **广播输出**：将 UE 渲染的画面（含音轨和时间码）通过 Blackmagic 卡输出到切换台、监视器或录机。
- **Genlock 同步**：使用 Blackmagic 卡的参考信号同步引擎的帧率，确保多机位或外部设备严格对齐。
- **时间码嵌入/读取**：从 SDI 信号中提取 LTC/VITC 时间码，驱动引擎时间码提供者，或向输出流写入时间码。
- **HDR 工作流**：支持 PQ/HLG 等 HDR 传输函数，满足高端影视制作需求。

## 蓝图用法

以下类可在蓝图中直接使用（放置于蓝图类或关卡蓝图）：

### 媒体源配置（UBlackmagicMediaSource）

| 属性 | 说明 |
|---|---|
| `MediaConfiguration` | 选择捕获设备、端口及视频格式 |
| `AutoDetectableTimecodeFormat` | 时间码格式（自动/None/LTC/VITC） |
| `bCaptureAudio` / `bCaptureVideo` | 是否捕获音频/视频 |
| `AudioChannels` | 声道数（立体声/环绕8声道） |
| `ColorFormat` | 视频像素格式（8bit YUV / 10bit YUV） |
| `MaxNumAudioFrameBuffer` / `MaxNumVideoFrameBuffer` | 缓冲区最大帧数 |
| `bLogDropFrame` | 丢帧时输出日志警告 |
| `bEncodeTimecodeInTexel` | 将时间码编码到纹素中 |
| `HDRMetadata` | HDR 元数据（EOTF 和 Gamut） |

### 自定义时间步（UBlackmagicCustomTimeStep）

| 属性 | 说明 |
|---|---|
| `MediaConfiguration` | 选择参考信号来源（设备、端口、格式） |
| `bEnableOverrunDetection` | 引擎循环是否超出发送端速率的警告检测 |

### 时间码提供者（UBlackmagicTimecodeProvider）

| 属性 | 说明 |
|---|---|
| `TimecodeConfiguration` | 设备、端口、时间码格式 |
| `bAutoDetectTimecode` | 是否自动检测时间码格式（默认开启） |

## C++ 用法

### 头文件引入

```cpp
#include "IBlackmagicMediaModule.h"
#include "BlackmagicMediaSource.h"
#include "BlackmagicCustomTimeStep.h"
#include "BlackmagicTimecodeProvider.h"
#include "BlackmagicDeviceProvider.h"
```

### 基本用法

```cpp
// 1. 获取模块并创建播放器
IBlackmagicMediaModule& Module = IBlackmagicMediaModule::Get();
if (Module.IsInitialized() && Module.CanBeUsed())
{
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = Module.CreatePlayer(EventSink);
    // 将 Player 传递给媒体播放器管理器...
}

// 2. 枚举设备（通过 FBlackmagicDeviceProvider）
FBlackmagicDeviceProvider Provider;
TArray<FMediaIODevice> Devices = Provider.GetDevices();
for (const FMediaIODevice& Device : Devices)
{
    UE_LOG(LogTemp, Log, TEXT("Device: %s"), *Device.DeviceName);
}

// 3. 创建并配置媒体源（UBlackmagicMediaSource）
UBlackmagicMediaSource* MediaSource = NewObject<UBlackmagicMediaSource>();
MediaSource->MediaConfiguration = Provider.GetDefaultConfiguration();
MediaSource->bCaptureVideo = true;
MediaSource->bCaptureAudio = true;
MediaSource->ColorFormat = EBlackmagicMediaSourceColorFormat::YUV10;
// 设置后传递给媒体播放器...

// 4. 自定义时间步
UBlackmagicCustomTimeStep* CustomTimeStep = NewObject<UBlackmagicCustomTimeStep>();
CustomTimeStep->MediaConfiguration = SomeConfiguration;
if (CustomTimeStep->Initialize(GEngine))
{
    // 引擎将使用此时间步同步
}
```

### 进阶用法

```cpp
// 结合时间码提供者实现帧精确同步
UBlackmagicTimecodeProvider* TimecodeProvider = NewObject<UBlackmagicTimecodeProvider>();
TimecodeProvider->TimecodeConfiguration = SomeTimecodeConfig;
TimecodeProvider->bAutoDetectTimecode = true;

if (TimecodeProvider->Initialize(GEngine))
{
    // 引擎将使用该时间码提供者
    // 每帧可通过 UTimecodeProvider 获取 QualifiedFrameTime
}
```

## Demo 示例

以下是一个最小 C++ 示例，展示如何在 GameInstance 中创建 Blackmagic 播放器并打开媒体源。

```cpp
// MyGameInstance.h
#pragma once

#include "Engine/GameInstance.h"
#include "MediaPlayer.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void Shutdown() override;

private:
    UPROPERTY()
    UMediaPlayer* MediaPlayer;

    UPROPERTY()
    UBlackmagicMediaSource* MediaSource;
};
```

```cpp
// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "IBlackmagicMediaModule.h"
#include "BlackmagicMediaSource.h"
#include "BlackmagicDeviceProvider.h"

void UMyGameInstance::Init()
{
    Super::Init();

    // 仅在 Blackmagic 模块可用时初始化
    if (IBlackmagicMediaModule::Get().IsInitialized())
    {
        MediaPlayer = NewObject<UMediaPlayer>(this);
        MediaSource = NewObject<UBlackmagicMediaSource>(this);

        FBlackmagicDeviceProvider DeviceProvider;
        MediaSource->MediaConfiguration = DeviceProvider.GetDefaultConfiguration();
        MediaSource->bCaptureVideo = true;
        MediaSource->bCaptureAudio = true;

        // 打开媒体源
        if (!MediaPlayer->OpenSource(MediaSource))
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to open Blackmagic media source."));
        }
    }
}

void UMyGameInstance::Shutdown()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::Shutdown();
}
```

## 模块依赖

当你的模块要使用 `BlackmagicMedia` 时，需要在 `Build.cs` 中添加以下依赖（省略常见 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `BlackmagicCore` | Blackmagic SDK 的底层 C++ 封装 |
| `MediaIOCore` | UE 媒体 I/O 核心框架（播放器基类、管道、同步等） |
| `MediaAssets` | 媒体资产类（UMediaPlayer、UMediaSource 等） |
| `MediaUtils` | 媒体实用工具（可选，部分功能依赖） |

## 维护状态

### 近期更新

- 2025-09-23 `9d85dc0e` 修复 Blackmagic 源在已有有效配置时错误分配默认配置的问题
- 2025-08-21 `8143139e` 添加缺失的 #include
- 2025-08-20 `2f0476a2` 添加缺失的 #include
- 2025-07-22 `d0ba5722` 为 AJA、Blackmagic、NDI 媒体源和输出指定分类显示顺序
- 2025-06-18 `60a45027` 在 Windows Arm64 上禁用此插件

### 维护评价

该插件创建约4个月（2025-06-18），仍处于早期开发阶段，但最近3个月内有多次功能性修复和工程改进（修复配置错误、补充头文件、禁用不支持平台）。从 commit 内容看，开发团队正积极处理边界情况和兼容性问题，未发现废弃标记。推荐在新项目中使用，但需注意它仍属于“实验性”插件的后期（IsBetaVersion=false，但默认不启用，需手动开启）。对于追求稳定的长时间运行项目，建议在测试环境中充分验证。

## 相关链接

- [源码（主目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia)
- [Blackmagic 自定义时间步头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/BlackmagicMedia/Source/BlackmagicMedia/Public/BlackmagicCustomTimeStep.h)
- [Blackmagic 设备提供者头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/BlackmagicMedia/Source/BlackmagicMedia/Public/BlackmagicDeviceProvider.h)
- [Blackmagic 媒体源头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/BlackmagicMedia/Source/BlackmagicMedia/Public/BlackmagicMediaSource.h)