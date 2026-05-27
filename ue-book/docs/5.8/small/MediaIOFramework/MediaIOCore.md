# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 专业媒体 IO 框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOCore` (Runtime), `MediaIOEditor` (Editor), `GPUTextureTransfer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-10-02 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework) | |

## 用途

MediaIOFramework 是虚幻引擎中**专业视频采集与输出的核心基础设施**，专门为虚拟制片（Virtual Production）行业设计。它解决的核心问题是：**如何在引擎运行时，高效地将渲染画面捕获并发送到外部专业视频设备（如 AJA、Blackmagic 采集卡），同时也能从这些设备输入视频信号。**

该插件本身是一个**框架层**，不直接提供特定硬件的实现。它定义了：

- **媒体捕获管线**（`UMediaCapture` / `UMediaOutput`）：定义了从渲染目标、场景视口或 RHI 资源捕获画面的标准流程，包含颜色转换（OCIO）、裁剪、缩放、隔行扫描处理等渲染通道
- **媒体播放器基类**（`FMediaIOCorePlayerBase`）：实现 `IMediaPlayer` 接口，为采集卡视频输入提供 JITR（Just-In-Time Rendering）延迟采样、时间码同步、帧锁定等专业功能
- **帧管理与 GPU 回读**（`FFrameManager`）：管理 GPU 回读帧队列，支持异步采集管线
- **音频捕获与输出**（`FMediaIOAudioCapture` / `FMediaIOAudioOutput`）：从引擎音频混音器捕获音频，支持多通道上混和格式转换
- **专业信号定义**（`FMediaIOConfiguration`）：SDI 单链路/双链路/四链路、HDMI、时间码格式（LTC/VITC）、隔行扫描模式等完整的专业视频信号抽象

具体硬件支持由依赖此框架的其他插件实现（如 AJA Media、Blackmagic Media 等），它们通过 `IMediaIOCoreDeviceProvider` 接口注册自己的设备。

## 使用场景

- 你需要将引擎画面通过 SDI/HDMI 输出到 LED 墙或监视器 → 使用此框架的 `UMediaCapture` + `UMediaOutput` 子类实现
- 你需要从专业摄像机采集卡输入视频信号到引擎 → 继承 `FMediaIOCorePlayerBase` 实现具体的采集卡播放器
- 你正在构建虚拟制片系统，需要帧同步（Framelock）和时间码对齐 → 使用 `bFramelock`、`EvaluationType`（Timecode/PlatformTime）等同步机制
- 你需要高质量的隔行扫描视频去交织 → 使用 `UVideoDeinterlacer` 的 Bob/Blend/Discard 三种模式
- 你需要从引擎音频混音器捕获音频并发送到外部设备 → 使用 `FMediaIOAudioCapture` + `FMediaIOAudioOutput`
- 你需要将捕获画面保存为图片序列 → 使用 `UFileMediaOutput` / `UFileMediaCapture`
- 你需要在编辑器中预览采集卡输入 → 通过 `URenderTargetMediaOutput` 输出到 `UTextureRenderTarget2D`

## 蓝图用法

该插件主要是 C++ 框架层，但 `UMediaCapture` 和 `UMediaOutput` 暴露了蓝图接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CaptureActiveSceneViewport` | 捕获当前活动场景视口 | `UMediaCapture` |
| `CaptureTextureRenderTarget2D` | 捕获指定纹理渲染目标 | `UMediaCapture` |
| `CaptureMediaTexture` | 捕获 MediaTexture 并支持旋转缩放 | `UMediaCapture` |
| `CreateMediaCapture` | 创建媒体捕获实例 | `UMediaOutput` |
| `Validate` | 验证媒体输出配置是否有效 | `UMediaOutput` |

### 使用示例（蓝图描述）

**捕获渲染目标到文件序列**：

1. 创建一个 `UFileMediaOutput` 资产（在内容浏览器右键 → Media → File Media Output）
2. 设置文件路径、基础文件名、图片格式
3. 在蓝图中：
   - 从 `FileMediaOutput` 节点调用 `CreateMediaCapture` 获得 `UMediaCapture`
   - 从 `UMediaCapture` 调用 `CaptureTextureRenderTarget2D`，传入目标 RT 和捕获选项
   - `FMediaCaptureOptions` 可控制裁剪模式、颜色转换、是否自动停止等

**捕获场景视口**：

1. 调用 `CaptureActiveSceneViewport`（自动查找 Standalone 或 New Editor Window PIE 中的视口）
2. 通过 `FMediaCaptureOptions.CapturePhase` 控制捕获时机（如 AfterToneMap、EndFrame 等）

## C++ 用法

### 头文件引入

```cpp
#include "MediaCapture.h"
#include "MediaOutput.h"
#include "CaptureCardMediaSource.h"
#include "MediaIOCoreDefinitions.h"
#include "MediaIOCorePlayerBase.h"
#include "MediaIOCoreSubsystem.h"
```

### 基本用法 — 配置媒体 IO 连接

```cpp
#include "MediaIOCoreDefinitions.h"

// 配置一个 SDI 单链路 1080p30 输出
FMediaIOConnection Connection;
Connection.Device.DeviceName = TEXT("AJA Corvid88");
Connection.Device.DeviceIdentifier = 0;
Connection.Protocol = TEXT("AJA");
Connection.TransportType = EMediaIOTransportType::SingleLink;
Connection.PortIdentifier = 1;

FMediaIOMode Mode;
Mode.FrameRate = FFrameRate(30000, 1001);  // 29.97fps
Mode.Resolution = FIntPoint(1920, 1080);
Mode.Standard = EMediaIOStandardType::Progressive;

FMediaIOOutputConfiguration OutputConfig;
OutputConfig.MediaConfiguration.bIsInput = false;
OutputConfig.MediaConfiguration.MediaConnection = Connection;
OutputConfig.MediaConfiguration.MediaMode = Mode;
OutputConfig.OutputType = EMediaIOOutputType::Fill;
OutputConfig.OutputReference = EMediaIOReferenceType::FreeRun;
```

**来源**: `MediaIOCoreDefinitions.h` 中的 `FMediaIOConnection`、`FMediaIOMode`、`FMediaIOOutputConfiguration` 结构体定义。

### 基本用法 — 程序化创建文件捕获

```cpp
#include "FileMediaOutput.h"
#include "FileMediaCapture.h"

// 创建文件媒体输出
UFileMediaOutput* FileOutput = NewObject<UFileMediaOutput>();
FileOutput->FilePath.Path = TEXT("/Game/Captures");
FileOutput->BaseFileName = TEXT("Frame_");
FileOutput->WriteOptions.Format = EImageFormat::PNG;

// 创建捕获并启动
UMediaCapture* Capture = FileOutput->CreateMediaCapture();

FMediaCaptureOptions Options;
Options.bAutoRestartOnSourceSizeChange = true;
Options.Crop = EMediaCaptureCroppingType::None;
Options.CapturePhase = EMediaCapturePhase::EndFrame;

// 捕获场景视口
Capture->CaptureActiveSceneViewport(Options);
```

**来源**: `FileMediaOutput.h` 和 `MediaCapture.h`。

### 进阶用法 — 使用音频子系统

```cpp
#include "MediaIOCoreSubsystem.h"

// 获取音频子系统
UMediaIOCoreSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMediaIOCoreSubsystem>();

// 创建音频输出
UMediaIOCoreSubsystem::FCreateAudioOutputArgs AudioArgs;
AudioArgs.NumOutputChannels = 2;
AudioArgs.TargetFrameRate = FFrameRate(30000, 1001);
AudioArgs.MaxSampleLatency = 4800;  // 0.1秒 @ 48kHz
AudioArgs.OutputSampleRate = 48000;

TSharedPtr<FMediaIOAudioOutput> AudioOutput = Subsystem->CreateAudioOutput(AudioArgs);

// 在每帧获取音频样本
TArray<int16> Samples = AudioOutput->GetAudioSamples<int16>();

// 订阅原始音频缓冲区回调（音频线程）
Subsystem->OnBufferReceived_AudioThread().AddLambda(
    [](Audio::FDeviceId DeviceId, float* Data, int32 NumSamples) {
        // 处理原始浮点音频数据
    });
```

**来源**: `MediaIOCoreSubsystem.h` 和 `MediaIOCoreAudioOutput.h`。

### 进阶用法 — 继承实现自定义播放器

```cpp
#include "MediaIOCorePlayerBase.h"

class FMyCaptureCardPlayer : public FMediaIOCorePlayerBase
{
public:
    FMyCaptureCardPlayer(IMediaEventSink& InEventSink)
        : FMediaIOCorePlayerBase(InEventSink) {}
    
protected:
    // 实现硬件就绪检查
    virtual bool IsHardwareReady() const override { return bHardwareInitialized; }
    
    // 设置采样通道
    virtual void SetupSampleChannels() override { /* 初始化视频/音频通道 */ }
    
    // 创建纹理采样（工厂方法）
    virtual TSharedPtr<FMediaIOCoreTextureSampleBase> AcquireTextureSample_AnyThread() const override
    {
        return MakeShared<FMyCaptureCardTextureSample>();
    }
    
    // 可选：自定义颜色格式
    virtual EMediaIOCoreColorFormat GetColorFormat() const override
    {
        return EMediaIOCoreColorFormat::YUV10;  // 10bit YUV
    }
    
    // 可选：自定义帧缓冲数量
    virtual uint32 GetNumVideoFrameBuffers() const override { return 3; }

private:
    bool bHardwareInitialized = false;
};
```

**来源**: `MediaIOCorePlayerBase.h` 中的纯虚函数定义。

## Demo 示例

**自定义渲染目标捕获实现** — 展示如何继承 `UMediaOutput` 和 `UMediaCapture` 创建自定义输出：

```cpp
// MyCustomMediaOutput.h
#pragma once
#include "MediaOutput.h"
#include "MyCustomMediaOutput.generated.h"

UCLASS(BlueprintType)
class UMyCustomMediaOutput : public UMediaOutput
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Output")
    FIntPoint OutputSize = FIntPoint(1920, 1080);

    UPROPERTY(EditAnywhere, Category = "Output")
    EPixelFormat OutputFormat = PF_B8G8R8A8;

    virtual FIntPoint GetRequestedSize() const override { return OutputSize; }
    virtual EPixelFormat GetRequestedPixelFormat() const override { return OutputFormat; }

protected:
    virtual UMediaCapture* CreateMediaCaptureImpl() override;
};
```

```cpp
// MyCustomMediaOutput.cpp
#include "MyCustomMediaOutput.h"

class UMyCustomMediaCapture : public UMediaCapture
{
    GENERATED_BODY()

protected:
    virtual bool InitializeCapture() override
    {
        // 初始化自定义硬件 SDK
        UE_LOG(LogMediaIOCore, Log, TEXT("Custom capture initialized."));
        return true;
    }

    virtual void OnFrameCaptured_RenderingThread(
        FRHICommandListImmediate& RHICmdList,
        const FCaptureBaseData& InBaseData,
        TSharedPtr<FMediaCaptureUserData, ESPMode::ThreadSafe> InUserData,
        void* InBuffer,
        int32 Width, int32 Height, int32 BytesPerRow) override
    {
        // 将帧数据发送到自定义硬件
        // InBuffer 包含像素数据
        // Width/Height 是分辨率
        // BytesPerRow 是行步长
    }

    virtual void StopCaptureImpl(bool bAllowPendingFrameToBeProcess) override
    {
        // 清理硬件资源
    }
};

UMediaCapture* UMyCustomMediaOutput::CreateMediaCaptureImpl()
{
    return NewObject<UMyCustomMediaCapture>(this);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenColorIO` | OCIO 颜色空间转换（插件级依赖） |
| `VulkanRHI` | GPU 纹理传输（GPUTextureTransfer 模块） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：MediaIOCore 和 MediaIOEditor 模块依赖了 EditorFramework、UnrealEd、LevelEditor，但这些属于标准编辑器模块，无需额外引用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为 Blackmagic/AJA 自动模式填充媒体配置信息 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和捕获添加引擎分析埋点信息 |
| 2026-05-14 | `a43a62b2` | Media Profile: Changed media texture capture behavior to always preserve aspect ratio of texture eve | 媒体纹理捕获始终保持纹理宽高比 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-12 | `a879de69` | Fix clang warnings when compiling MediaIODeinterlacerTests | 修复 MediaIODeinterlacerTests 的 clang 编译警告 |

### 维护评价

**活跃维护**。该插件在最近几周内持续收到功能性更新和修复，说明 Epic 仍在积极维护。作为虚拟制片管线的核心基础设施，它对 Blackmagic/AJA 等采集卡的支持不断改进，颜色管理（OCIO）和分析埋点等功能也在持续增强。

虽然创建于 2018 年（约 8 年前），但作为 UE 虚拟制片战略的关键组件，该插件有稳定的维护周期。需要注意的是：
- `EnabledByDefault=false`，需要手动在插件列表中启用
- 多处 API 在 5.8 中标记为 `UE_DEPRECATED`（如旧的颜色格式参数 `FColorFormatArgs`），建议使用新的 `FNativeMediaSourceColorSettings`
- GPUTextureTransfer 模块不支持 Win64:arm64 架构

**推荐使用**：如果你在做虚拟制片相关的媒体 IO 开发，这是必经的框架层。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework)
- [官方文档]() （无官方文档链接）