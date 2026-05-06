# Pixel Capture

> Framework for capturing pixel buffers in other formats while allowing for disconnected produce/consume rates.

| 属性 | 值 |
|---|---|
| 中文名 | 像素捕获框架 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UObject 类、蓝图节点、着色器资源） |
| 模块 | `PixelCapture` (Runtime), `PixelCaptureShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelCapture) | |

## 用途

Pixel Capture 是一个通用像素捕获框架，用于将渲染帧（如 RHI 纹理、I420/NV12 缓冲区）转换为其他格式的缓冲区，同时支持 **生产者与消费者速率解耦**。它适用于需要从渲染管线中异步获取像素数据的场景，如像素流送（Pixel Streaming）、实时编码、屏幕截图等。

主要设计特点：
- **单一生产者，多个消费者**：通过 `FOutputFrameBuffer`（SPMC 环形缓冲区）实现，捕获端仅生产最新帧，消费端可独立读取。
- **分层分辨率**：`FPixelCaptureCapturerLayered` 可对同一帧生成多个分辨率层，每层独立捕获。
- **多格式输出**：`FPixelCaptureCapturerMultiFormat` 管理多个格式（如 I420、NV12、RHI 纹理）的捕获管道，按需请求特定格式。
- **异步处理**：每个捕获器单独处理一帧，支持 CPU/GPU 时间标记，便于性能分析。

## 使用场景

- **像素流送（Pixel Streaming）**：将游戏画面转换为 I420/NV12 帧供 WebRTC 编码器使用。
- **远程桌面/串流**：需要以不同分辨率和格式捕获渲染目标。
- **视频录制/截图**：在后台异步捕获帧，不影响主渲染线程。
- **自定义渲染管道**：当你需要从渲染纹理中提取数据并进行格式转换时。

## 蓝图用法

由于核心捕获类是纯 C++ 类（`IPixelCaptureBuffer`, `FPixelCaptureCapturer` 等），Blueprint 中直接可用的节点有限。插件提供了两个 UObject 类用于与 `Media Framework` 集成：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Pixel Capture Media Output` | 创建自定义媒体输出，用于配置捕获尺寸 | `UPixelCaptureMediaOuput` |
| `Start Media Capture` | 启动媒体捕获（继承自 `UMediaCapture`） | `UPixelCaptureMediaCapture` |
| `Create Media Output` | 创建标准媒体输出对象（标准蓝图节点） | `UMediaOutput` |

使用示例（蓝图）：
1. 创建一个 `UPixelCaptureMediaOuput`，设置 `RequestedSize`（目标分辨率）。
2. 调用 `Start Media Capture` 并传入该 Media Output，指定捕获源（如 Scene Viewport）。
3. 捕获后的帧可通过 `OnCaptureComplete` 事件获取（需绑定到 `UPixelCaptureMediaCapture` 的自定义事件）。

## C++ 用法

### 头文件引入

```cpp
#include "PixelCaptureCapturerMultiFormat.h"
#include "PixelCaptureInputFrameRHI.h"
#include "PixelCaptureOutputFrameI420.h"
```

### 基本用法

从 RHI 纹理捕获到 I420 格式（使用 Compute Shader 版本）：

```cpp
// 创建多格式捕获器（假设已经有一个 IPixelCaptureCapturerSource 实现）
TSharedPtr<FPixelCaptureCapturerMultiFormat> Capturer = 
    FPixelCaptureCapturerMultiFormat::Create(MyCapturerSource, /*可选输出分辨率*/ {});

// 注册需要输出的格式
Capturer->AddOutputFormat(PixelCaptureBufferFormat::FORMAT_I420);

// 创建输入帧（从渲染线程获取的纹理）
FTextureRHIRef RenderTexture = /* 从 RHI 获取 */;
TSharedPtr<IPixelCaptureInputFrame> InputFrame = 
    MakeShared<FPixelCaptureInputFrameRHI>(RenderTexture);

// 启动捕获
Capturer->Capture(*InputFrame);

// 当捕获完成（通常通过回调或定时查询），请求输出
TSharedPtr<IPixelCaptureOutputFrame> OutputFrame = 
    Capturer->RequestFormat(PixelCaptureBufferFormat::FORMAT_I420, FIntPoint(1920, 1080));

if (OutputFrame)
{
    TSharedPtr<FPixelCaptureOutputFrameI420> I420Frame = StaticCastSharedPtr<FPixelCaptureOutputFrameI420>(OutputFrame);
    TSharedPtr<FPixelCaptureBufferI420> I420Buffer = I420Frame->GetI420Buffer();
    // 使用 I420Buffer->GetDataY(), GetDataU(), GetDataV() 访问平面数据
}
```

### 进阶用法

**使用分层捕获器**（多分辨率）：

```cpp
// 创建分层捕获器的源（例如返回 RHI 拷贝、RHI->I420 等 Capturer）
class FMyCapturerSource : public IPixelCaptureCapturerSource
{
public:
    virtual TSharedPtr<FPixelCaptureCapturer> CreateCapturer(int32 FinalFormat, FIntPoint OutputResolution) override
    {
        if (FinalFormat == PixelCaptureBufferFormat::FORMAT_RHI)
            return FPixelCaptureCapturerRHI::Create( { OutputResolution } );
        if (FinalFormat == PixelCaptureBufferFormat::FORMAT_I420)
            return FPixelCaptureCapturerRHIToI420Compute::Create( { OutputResolution } );
        return nullptr;
    }
};

// 手动添加输出分辨率
TArray<FIntPoint> Resolutions = { FIntPoint(1920,1080), FIntPoint(1280,720), FIntPoint(640,360) };
TSharedPtr<FPixelCaptureCapturerMultiFormat> MultiCapturer = 
    FPixelCaptureCapturerMultiFormat::Create(&MySource, Resolutions);
MultiCapturer->AddOutputFormat(PixelCaptureBufferFormat::FORMAT_I420);
```

**手动使用 SPMC 缓冲区**：

```cpp
UE::PixelCapture::FOutputFrameBuffer Buffer;
Buffer.Reset(/*初始大小*/3, /*最大大小*/5, 
    []() { return MakeShared<FPixelCaptureOutputFrameRHI>(nullptr); });

TSharedPtr<IPixelCaptureOutputFrame> ProduceBuffer = Buffer.LockProduceBuffer();
// 填充 ProduceBuffer...
bool bReleased = Buffer.ReleaseProduceBuffer(ProduceBuffer);

TSharedPtr<IPixelCaptureOutputFrame> ConsumeBuffer = Buffer.GetConsumeBuffer();
```

## Demo 示例

以下是一个完整的最小 C++ 控制台命令示例，演示如何从 RenderTarget 纹理捕获到 I420 格式并输出信息。

**PixelCaptureDemo.h**:
```cpp
#pragma once
#include "CoreMinimal.h"
#include "PixelCaptureCapturerMultiFormat.h"
#include "PixelCaptureInputFrameRHI.h"
#include "PixelCaptureOutputFrameI420.h"

DECLARE_LOG_CATEGORY_EXTERN(LogPixelCaptureDemo, Log, All);

class FPixelCaptureDemo
{
public:
    static void RunDemo(FTextureRHIRef SourceTexture);
};
```

**PixelCaptureDemo.cpp**:
```cpp
#include "PixelCaptureDemo.h"
#include "RenderingThread.h"

DEFINE_LOG_CATEGORY(LogPixelCaptureDemo);

void FPixelCaptureDemo::RunDemo(FTextureRHIRef SourceTexture)
{
    // 创建多格式捕获器（使用内部统一的 CapturerSource）
    // 这里假设有默认实现，实际项目中需提供 IPixelCaptureCapturerSource
    TSharedPtr<FPixelCaptureCapturerMultiFormat> Capturer = 
        FPixelCaptureCapturerMultiFormat::Create(nullptr, { SourceTexture->GetDesc().Extent });

    Capturer->AddOutputFormat(PixelCaptureBufferFormat::FORMAT_I420);

    // 必须等捕获器初始化
    ENQUEUE_RENDER_COMMAND(CaptureFrame)(
        [Capturer, SourceTexture](FRHICommandListImmediate& RHICmdList)
        {
            TSharedPtr<IPixelCaptureInputFrame> InputFrame = 
                MakeShared<FPixelCaptureInputFrameRHI>(SourceTexture);
            Capturer->Capture(*InputFrame);
        });

    // 延迟读取结果（实际项目中应在捕获完成后或定时查询）
    FTimerHandle TimerHandle;
    GWorld->GetTimerManager().SetTimer(TimerHandle, 
        [Capturer]()
        {
            FIntPoint Size = SourceTexture->GetDesc().Extent;
            TSharedPtr<IPixelCaptureOutputFrame> Output = 
                Capturer->RequestFormat(PixelCaptureBufferFormat::FORMAT_I420, Size);
            if (Output)
            {
                TSharedPtr<FPixelCaptureOutputFrameI420> I420 = 
                    StaticCastSharedPtr<FPixelCaptureOutputFrameI420>(Output);
                UE_LOG(LogPixelCaptureDemo, Log, TEXT("Captured I420 frame: %dx%d"), 
                    I420->GetWidth(), I420->GetHeight());
            }
        },
        1.0f, false);
}
```

## 模块依赖

**PixelCapture 模块**的依赖（来源于源码分析）：

| 模块 | 用途 |
|---|---|
| `RHI` | 纹理资源接口 |
| `RenderCore` | 渲染图、着色器管理 |
| `MediaIOFramework` | MediaShaders、屏幕渲染辅助 |
| `WebRTC` (通过 PixelStreaming) | rtc_base/time_utils.h 中的时间戳 |

在您项目的 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { 
    "PixelCapture", 
    "PixelCaptureShaders" 
});
// 如果使用 PixelCapture 的 Media Capture 集成，还需添加：
PublicDependencyModuleNames.Add("MediaIOFramework");
```

## 维护状态

### 近期更新

- 2025-09-29 `9308001e` [PixelCapture] Fix: Remove call to StopCapture as it can cause deadlocks
- 2025-09-25 `1fdac7d5` [PixelCapture, PS, PS2] Fix: MediaCapture could get into a bad state due to use of queues and praying
- 2025-09-23 `20ee5e0e` The source files included were modified by the UnrealCodeFixup tool (merge fix)
- 2025-09-23 `5a037905` [PS2] Fix: Hang during first decoded frame
- 2025-06-23 `fb7a5db5` [PixelCapture] Fix Pixel Capture incorrectly incrementing loop in FOutputFrameBuffer::LockProduceBu

### 维护评价

Pixel Capture 插件创建于 2025 年 6 月，是一个相对较新的插件。近期更新集中在 Bug 修复（死锁、死循环、MediaCapture 状态问题），表明正在积极维护中。由于仍标记为 Beta 版本，API 可能出现不兼容变化（如 5.7 中废弃了基于 scale 的参数，改为 FIntPoint 分辨率）。推荐在新项目中使用，但建议关注 UE 官方更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelCapture)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelCapture/Source/PixelCapture/Tests)