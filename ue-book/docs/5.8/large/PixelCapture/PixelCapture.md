# Pixel Capture

> Framework for capturing pixel buffers in other formats while allowing for disconnected produce/consume rates.

| 属性 | 值 |
|---|---|
| 中文名 | 像素捕获 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（缓冲区格式和捕获器实现） |
| 模块 | `PixelCapture` (Runtime), `PixelCaptureShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelCapture) | |

## 用途

PixelCapture 是一个用于捕获 GPU 像素数据（RHI 纹理）并将其转换为各种 CPU 可读缓冲区格式（如 I420, NV12）的 C++ 框架。其核心设计目标是支持**生产者和消费者以解耦的速率运行**。这意味着产生像素数据的帧源（如游戏渲染）可以独立于处理这些数据的消费者（如视频编码器）的速率工作，通过内部缓冲区环实现异步处理，避免阻塞。

该插件是 **Pixel Streaming** 功能的重要组成部分，负责从游戏画面中高效地抓取和转换视频帧，为后续的编码和网络传输做准备。它允许开发者实现自定义的捕获流程，并支持从 GPU 到 CPU 的异步数据回传。

## 使用场景

- 你正在使用或开发 **Pixel Streaming** 功能，需要一个可靠、高效且异步的视频帧捕获和转换管道。
- 你需要从 Unreal Engine 的渲染输出（GPU 纹理）中捕获画面，并将其转换为特定的 CPU 像素格式（如 I420, NV12）以便进行进一步处理（例如硬件编码、网络传输、图像分析）。
- 你的应用程序需要处理以不同帧率产生的像素数据和消费这些数据的系统，需要一个解耦的生产者-消费者模型。

## 蓝图用法

**该插件主要是一个 C++ 框架，其核心类和接口均未暴露蓝图（UFUNCTION）节点。** 使用它需要通过 C++ 代码创建捕获器、输入帧和管理输出帧。

## C++ 用法

### 头文件引入

```cpp
#include "PixelCaptureCapturer.h"
#include "PixelCaptureCapturerRHI.h"
#include "PixelCaptureInputFrameRHI.h"
#include "PixelCaptureOutputFrameRHI.h"
```

### 基本用法

以下代码展示了如何使用一个 RHI 复制捕获器来捕获一帧。

```cpp
// 来源文件: 基于 Public/PixelCaptureCapturerRHI.h 和 Public/PixelCaptureCapturer.h 的用法推断

// 1. 创建一个捕获器实例（例如 RHI 到 RHI 的拷贝）
FPixelCaptureCapturerConfig CapturerConfig;
CapturerConfig.OutputResolution = FIntPoint(1920, 1080);
TSharedPtr<FPixelCaptureCapturerRHI> MyCapturer = FPixelCaptureCapturerRHI::Create(CapturerConfig);

// 2. 准备输入帧（假设我们有一个 FTextureRHIRef CurrentFrameTexture）
TSharedPtr<FPixelCaptureInputFrameRHI> InputFrame = MakeShared<FPixelCaptureInputFrameRHI>(CurrentFrameTexture);

// 3. 开始捕获（异步）
MyCapturer->Capture(*InputFrame);

// 4. 检查并获取输出
// 通常在 OnComplete 委托中处理，或者定期轮询
if (MyCapturer->HasOutput())
{
    TSharedPtr<IPixelCaptureOutputFrame> OutputFrame = MyCapturer->ReadOutput();
    if (OutputFrame)
    {
        // 安全地将接口转换为具体的输出类型
        TSharedPtr<FPixelCaptureOutputFrameRHI> OutputFrameRHI = StaticCastSharedPtr<FPixelCaptureOutputFrameRHI>(OutputFrame);
        FTextureRHIRef OutputTexture = OutputFrameRHI->GetFrameTexture();
        // ... 使用输出纹理
    }
}
```

### 进阶用法

使用 `FPixelCaptureCapturerMultiFormat` 来管理多个格式的输出，并等待特定格式就绪。

```cpp
// 来源文件: Public/PixelCaptureCapturerMultiFormat.h

// 假设我们有一个实现了 IPixelCaptureCapturerSource 的类 `MyCapturerSource`
// MyCapturerSource::CreateCapturer 能够根据 FinalFormat 创建对应的捕获器。

// 1. 创建一个支持多格式的捕获器管理器
TArray<FIntPoint> OutputResolutions = { FIntPoint(1280, 720), FIntPoint(640, 360) };
TSharedPtr<FPixelCaptureCapturerMultiFormat> MultiCapturer = FPixelCaptureCapturerMultiFormat::Create(MyCapturerSource.Get(), OutputResolutions);

// 2. 添加期望的输出格式（例如 I420 格式）
MultiCapturer->AddOutputFormat(PixelCaptureBufferFormat::FORMAT_I420);

// 3. 输入一帧进行捕获
TSharedPtr<FPixelCaptureInputFrameRHI> InputFrame = MakeShared<FPixelCaptureInputFrameRHI>(GameFrameTexture);
MultiCapturer->Capture(*InputFrame);

// 4. 获取特定分辨率和格式的输出
// 非阻塞获取
TSharedPtr<IPixelCaptureOutputFrame> I420Frame_720p = MultiCapturer->RequestFormat(PixelCaptureBufferFormat::FORMAT_I420, FIntPoint(1280, 720));
if (I420Frame_720p)
{
    // 已经就绪，可以使用
}

// 或者阻塞等待（注意线程安全，避免在捕获线程调用）
TSharedPtr<IPixelCaptureOutputFrame> I420Frame_360p = MultiCapturer->WaitForFormat(PixelCaptureBufferFormat::FORMAT_I420, FIntPoint(640, 360), 5000); // 等待5秒
if (I420Frame_360p)
{
    // 获取到了 360p 的 I420 帧
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何创建一个 RHI 捕获器并处理一帧。

**PixelCaptureDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "PixelCaptureCapturerRHI.h"
#include "PixelCaptureInputFrameRHI.h"
#include "PixelCaptureDemo.generated.h"

UCLASS()
class UPixelCaptureDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    void CaptureCurrentFrame(FTextureRHIRef SourceTexture);

private:
    TSharedPtr<FPixelCaptureCapturerRHI> Capturer;

    void OnCaptureComplete();
};
```

**PixelCaptureDemo.cpp**
```cpp
#include "PixelCaptureDemo.h"
#include "PixelCaptureOutputFrameRHI.h"
#include "Engine/TextureRenderTarget2D.h"

void UPixelCaptureDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 创建一个 RHI 复制捕获器，输出分辨率为 1280x720
    FPixelCaptureCapturerConfig Config;
    Config.OutputResolution = FIntPoint(1280, 720);
    Capturer = FPixelCaptureCapturerRHI::Create(Config);

    if (Capturer.IsValid())
    {
        // 绑定捕获完成回调
        Capturer->OnComplete.AddUObject(this, &UPixelCaptureDemoSubsystem::OnCaptureComplete);
    }
}

void UPixelCaptureDemoSubsystem::Deinitialize()
{
    Capturer.Reset();
    Super::Deinitialize();
}

void UPixelCaptureDemoSubsystem::CaptureCurrentFrame(FTextureRHIRef SourceTexture)
{
    if (!Capturer.IsValid() || Capturer->IsBusy())
    {
        UE_LOG(LogTemp, Warning, TEXT("Capturer is not ready or busy."));
        return;
    }

    // 创建输入帧
    TSharedPtr<FPixelCaptureInputFrameRHI> InputFrame = MakeShared<FPixelCaptureInputFrameRHI>(SourceTexture);
    // 开始异步捕获
    Capturer->Capture(*InputFrame);
}

void UPixelCaptureDemoSubsystem::OnCaptureComplete()
{
    // 此回调在捕获完成后可能触发在任何线程，注意线程安全
    TSharedPtr<IPixelCaptureOutputFrame> OutputFrame = Capturer->ReadOutput();
    if (OutputFrame.IsValid())
    {
        TSharedPtr<FPixelCaptureOutputFrameRHI> OutputFrameRHI = StaticCastSharedPtr<FPixelCaptureOutputFrameRHI>(OutputFrame);
        if (OutputFrameRHI.IsValid())
        {
            FTextureRHIRef CapturedTexture = OutputFrameRHI->GetFrameTexture();
            UE_LOG(LogTemp, Log, TEXT("Frame captured successfully! Texture: %s, Size: %dx%d"),
                *CapturedTexture->GetName().ToString(),
                OutputFrameRHI->GetWidth(),
                OutputFrameRHI->GetHeight());
            // 在此处使用 CapturedTexture，例如进行后续处理或显示
        }
    }
}
```

## 模块依赖

从 `.uplugin` 文件和代码依赖关系推断。

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 媒体 I/O 框架，是该插件的硬依赖。 |
| `MediaUtils` | 可能用于媒体相关的工具函数。 |
| `RenderCore` | 核心渲染功能，包含 RHI 命令列表、纹理等。 |
| `RHI` | 渲染硬件接口，用于底层图形 API 交互。 |
| `Renderer` | 用于执行图形渲染操作（如绘制矩形）。 |

*注意：许多常见模块（如 Core, CoreUObject, Engine）已被省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量到单精度的截断警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-16 | `d0c437a7` | [PixelCapture, PixelStreaming2] Fix: Multiple issues for RemoteSession on Android | 修复了 Android 上 RemoteSession 的多个问题。 |
| 2026-03-12 | `225cb015` | [PixelCapture] Fix: Missing sRGB flag when required | 修复了需要 sRGB 标志时缺失的问题。 |
| 2026-02-06 | `f087dbb2` | [PixelCapture] Fix: Potential deadlock when pinning weak UObject ptr | 修复了当固定弱 UObject 指针时可能出现的死锁问题。 |

### 维护评价

**活跃维护**。该插件创建于 2022 年，虽然仍标记为 `IsBetaVersion: true`，但从 Git 历史看，自 2026 年初以来有多次针对功能、平台兼容性（Android）和底层问题的修复，表明其仍在积极维护和改进中。它是 Pixel Streaming 技术栈的关键组件，因此预计会持续更新。作为 Beta 版本，其 API 可能在未来版本中发生变化，但当前状态稳定可用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelCapture)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/PixelCapture)