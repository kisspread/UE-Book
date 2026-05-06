# AJA Media Player

> Implements input and output using AJA Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | AJA驱动媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图媒体源、时间码设置、自定义时间步配置） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia) | |

## 用途

该插件是 UE5 与 AJA 专业视频采集/输出卡之间的桥梁。它利用 AJA SDK 提供以下核心能力：

- **实时视频输入**：从 AJA SDI 或 HDMI 接口捕获视频帧、音频和辅助数据（Ancillary）。
- **精确同步**：通过 AJA 卡锁定引擎的渲染循环（自定义时间步）或为时间码提供器。
- **媒体播放器**：以 `IMediaPlayer` 接口封装，可无缝接入 UE 的媒体框架，配合 `MediaPlayer` 等资产使用。
- **HDR 支持**：支持 HLG 和 PQ 两种 HDR 传输函数，以及 Rec.709 / Rec.2020 色域。
- **输出**（通过 `AjaMediaOutput` 模块）：将 UE 渲染的帧输出到 AJA 卡。

解决了在 UE 中使用专业广播级视频设备进行实时画面采集、同步和监看的场景。

## 使用场景

- **虚拟制片**：将摄影机视频信号输入 UE，作为背景或合成元素。
- **演播室播出**：使用 AJA 卡生成参考时间码，同步多台机器。
- **后期预可视化**：实时回看 UE 渲染画面到 SDI 显示器。
- **混合现实直播**：低延迟捕获摄像机信号并叠加虚拟内容。

## 蓝图用法

插件暴露了多个可直接在蓝图中配置的类，主要属性以 `UPROPERTY(EditAnywhere, BlueprintReadOnly)` 暴露，无需调用额外函数。

### 核心可用类

| 类名 | 说明 | 蓝图处理 |
|---|---|---|
| `UAjaMediaSource` | 定义 AJA 输入源的配置（设备、端口、格式、音频/辅助选项） | 作为 `Media Source` 资产使用，可直接在 `MediaPlayer` 中指定 |
| `UAjaCustomTimeStep` | 锁定引擎时间步与 AJA 卡输入信号同步 | 在项目设置 → 自定义时间步中选择 |
| `UAjaTimecodeProvider` | 从 AJA 卡读取 LTC 时间码或 SDI 内嵌时间码 | 在项目设置 → 时间码提供器中选择 |
| `FAjaMediaHDROptions` | HDR 元数据结构体，用于配置 EOTF 和 Gamut | 在 `Aja Media Source` 的 HDR 选项中暴露 |

### 关键属性配置（以 `UAjaMediaSource` 为例）

- **MediaConfiguration**（FMediaIOConfiguration）：选择设备、端口、分辨率、帧率。
- **AutoDetectableTimecodeFormat**：自动或手动指定时间码格式。
- **bCaptureVideo / bCaptureAudio / bCaptureAncillary**：开启对应的数据捕获。
- **bUseSRGBInput**：是否将输入视为 sRGB 空间（影响颜色校正）。

> 无需编写蓝图节点，只需在项目设置或媒体源资产中设置这些属性即可。

## C++ 用法

### 头文件引入

```cpp
#include "IAjaMediaModule.h"
#include "AjaMediaSource.h"
#include "AjaCustomTimeStep.h"
#include "AjaTimecodeProvider.h"
```

### 基本用法

#### 创建媒体播放器并播放 AJA 输入流

```cpp
// 通过模块接口创建播放器
IAjaMediaModule& AjaMediaModule = IAjaMediaModule::Get();
TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = AjaMediaModule.CreatePlayer(EventSink);

// 创建媒体源对象（UMediaSource 子类）
UAjaMediaSource* MediaSource = NewObject<UAjaMediaSource>();
MediaSource->MediaConfiguration.Device.DeviceProvider = EMediaIODeviceProvider::AJA;
MediaSource->MediaConfiguration.MediaPort.Mode = EMediaIOMode::Input;
MediaSource->MediaConfiguration.MediaMode.Resolution = FIntPoint(1920, 1080);
MediaSource->MediaConfiguration.MediaMode.FrameRate = FFrameRate(30, 1);
// ... 其他配置

// 打开媒体播放器
Player->Open(MediaSource->GetUrl(), MediaSource);
```

*来源：`AjaMediaPlayer.cpp` 中 `Open` 方法分析*

#### 使用自定义时间步锁定引擎与 AJA 信号

```cpp
// 在项目设置或代码中创建 UAjaCustomTimeStep
UAjaCustomTimeStep* TimeStep = NewObject<UAjaCustomTimeStep>();
TimeStep->MediaConfiguration = ...; // 设置与输入流一致的配置
TimeStep->bUseReferenceIn = false;   // 使用输入视频信号锁定
TimeStep->bWaitForFrameToBeReady = true;

// 设置引擎时间步（通常在 UEngineSubsystem 或模块启动时）
GEngine->SetCustomTimeStep(TimeStep);
TimeStep->Initialize(GEngine);
```

*来源：`AjaCustomTimeStep.cpp`*

#### 使用时间码提供器

```cpp
UAjaTimecodeProvider* TimecodeProvider = NewObject<UAjaTimecodeProvider>();
TimecodeProvider->bUseDedicatedPin = false; // 从 SDI 输入读取
TimecodeProvider->VideoConfiguration.MediaConfiguration = ...;

// 应用为全局时间码提供器
GEngine->SetTimecodeProvider(TimecodeProvider);
TimecodeProvider->Initialize(GEngine);
```

*来源：`AjaTimecodeProvider.cpp`*

### 进阶用法

#### 手动获取视频帧数据（通过回调）

在自定义媒体接收器中实现 `IMediaTextureSample` 处理：

```cpp
class FMyAJAReceiver : public IMediaTextureSampleRenderer
{
    void ProcessVideoFrame(const FAjaMediaTextureSample& Sample) override
    {
        // 获取像素数据
        const void* Buffer = Sample.GetBuffer();
        int32 Width = Sample.GetWidth();
        int32 Height = Sample.GetHeight();
        EMediaTextureSampleFormat Format = Sample.GetFormat();

        // 复制到纹理或 CPU 内存
    }
};
```

*来源：`AjaMediaTextureSample.h`*

#### 检测并处理输入格式变化

`FAjaMediaPlayer::OnFormatChange` 会在输入视频格式改变时触发（如切换分辨率）。可通过重写 `IAJAInputOutputChannelCallbackInterface` 处理。

## Demo 示例

以下是一个最小 C++ 示例，展示如何在模块启动时创建 AJA 媒体播放器并播放输入流。

**MyAjaDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"
#include "IMediaEventSink.h"
#include "IMediaPlayer.h"

class FMyAjaDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> MediaPlayer;
    class IMediaEventSink* EventSink;
};
```

**MyAjaDemo.cpp**
```cpp
#include "MyAjaDemo.h"
#include "IAjaMediaModule.h"
#include "AjaMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"

class FSimpleEventSink : public IMediaEventSink
{
public:
    virtual void ReceiveMediaEvent(EMediaEvent Event) override
    {
        UE_LOG(LogTemp, Log, TEXT("Media Event: %d"), (int32)Event);
    }
};

void FMyAjaDemoModule::StartupModule()
{
    // 1. 获取 AJA 模块
    IAjaMediaModule& AjaModule = IAjaMediaModule::Get();
    if (!AjaModule.IsInitialized())
    {
        UE_LOG(LogTemp, Error, TEXT("AJA module not initialized."));
        return;
    }

    // 2. 创建事件接收器
    EventSink = new FSimpleEventSink();

    // 3. 创建媒体播放器
    MediaPlayer = AjaModule.CreatePlayer(*EventSink);

    // 4. 构造媒体源
    UAjaMediaSource* MediaSource = NewObject<UAjaMediaSource>();
    MediaSource->MediaConfiguration.Device.DeviceProvider = EMediaIODeviceProvider::AJA;
    MediaSource->MediaConfiguration.MediaPort.Mode = EMediaIOMode::Input;
    MediaSource->MediaConfiguration.MediaMode.Resolution = FIntPoint(1920, 1080);
    MediaSource->MediaConfiguration.MediaMode.FrameRate = FFrameRate(30, 1);
    MediaSource->bCaptureVideo = true;
    MediaSource->bCaptureAudio = false;

    // 5. 打开播放
    bool bOpened = MediaPlayer->Open(MediaSource->GetUrl(), MediaSource);
    if (!bOpened)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open AJA media stream."));
    }
}

void FMyAjaDemoModule::ShutdownModule()
{
    if (MediaPlayer.IsValid())
    {
        MediaPlayer->Close();
        MediaPlayer.Reset();
    }
    delete EventSink;
}

IMPLEMENT_MODULE(FMyAjaDemoModule, MyAjaDemo);
```

## 模块依赖

以下模块是使用该插件时需要在项目 `.Build.cs` 的 `PublicDependencyModuleNames` 中添加的（省略标准核心依赖）：

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 媒体 IO 框架，提供基类（播放器、纹理样本等） |
| `MediaAssets` | 媒体资产（媒体玩家、媒体源等） |
| `AjaCore` | 包含 AJA SDK C++ 封装和原生回调 |
| `RHI` | 渲染硬件接口，用于纹理上传 |
| `Slate` / `SlateCore` | 编辑器图标等 UI 元素 |
| `Projects` | 模块加载回调 |
| `DeveloperSettings` | 全局设置类（`UAjaMediaSettings`） |

> 对于编辑器工具，还需依赖 `AjaMediaEditor` 和 `AjaMediaFactory`。

## 维护状态

### 近期更新

| 日期 | Hash | Commit 解读 |
|---|---|---|
| 2025-10-17 | `ab15e769` | 修复刷新 AJA 源媒体属性时的崩溃 |
| 2025-09-24 | `5ef7a9a2` | 新增一种输出模式，最多可减少 1 帧延迟 |
| 2025-09-24 | `94f6a824` | 为输入、输出和 Genlock 添加了超时后继续工作的选项 |
| 2025-08-20 | `5f63edc0` | 更新 AJA SDK 至 17.5.0 |
| 2025-08-18 | `5b28eda8` | 新增丢弃奇数帧隔行画面的选项 |

### 维护评价

- **创建时间**：2025年8月，非常新。
- **近期更新频率**：2025年9-10月仍有功能改进和 bug 修复，非常活跃。
- **活跃度**：目前处于积极开发阶段，修复和增强不断。
- **建议**：适合在最新的 UE5（如 5.5+）中使用。由于依赖于 AJA SDK 硬件，部署前需确认硬件兼容性。建议保持插件更新以获取最新功能和修复。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia)
- [官方文档（AJA 集成）](https://docs.unrealengine.com/5.5/en-US/aja-card-support-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia/Source/AjaMedia/Private/Player)（核心播放器源码）