# Pixel Capture

> Framework for capturing pixel buffers in other formats while allowing for disconnected produce/consume rates.

| 属性 | 值 |
|---|---|
| 中文名 | 像素捕获 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelCapture` (Runtime), `PixelCaptureShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelCapture) | |

## 用途

该插件提供了一个用于捕获和处理像素数据的高性能框架。其核心设计目标是解耦像素数据的**生产者**（如游戏渲染帧）和**消费者**（如编码器或流送），允许它们以独立的帧率运行。此外，它还封装了在GPU上高效转换像素格式（如RGBA到NV12）的能力，是实现高质量、低延迟像素流送（Pixel Streaming）的关键底层基础设施。

## 使用场景

- **像素流送（Pixel Streaming）**：将游戏或应用画面实时编码并流送至远程设备。本插件管理从游戏帧到编码器输入的复杂流水线。
- **独立帧率捕获与编码**：当游戏运行在120fps，但流送或录像仅需30fps时，本插件可以安全地丢弃多余帧，避免资源浪费。
- **跨平台像素处理**：在Windows、Linux、Mac、Android和iOS上提供统一的像素捕获与格式转换接口。
- **需要GPU加速格式转换的场景**：例如，将引擎默认的BGRA格式转换为视频编码器常用的YUV格式。

## 蓝图用法

本插件主要为C++层设计，蓝图API有限，核心捕获器通过 `UPixelCaptureCapturer` 类暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Capturer` | 静态方法，创建一个像素捕获器实例。需要指定源和目标格式。 | `UPixelCaptureCapturer` |
| `Start` | 启动捕获器，开始处理输入帧。 | `UPixelCaptureCapturer` |
| `Stop` | 停止捕获器。 | `UPixelCaptureCapturer` |
| `Capture` | 手动触发捕获当前帧。 | `UPixelCaptureCapturer` |
| `Get Output` | 获取处理后的输出纹理（RHI纹理）。 | `UPixelCaptureCapturer` |

### 使用示例（蓝图描述）

1.  使用 `Create Capturer` 节点，选择源纹理（如游戏视口输出）和目标格式（如 `EPixelCaptureFormat::NV12`）。
2.  调用 `Start` 启动捕获。
3.  在 Tick 事件或需要帧的时刻调用 `Capture`。
4.  通过 `Get Output` 获取结果纹理，可将其传递给后续的媒体输出或编码器节点。

## C++ 用法

### 头文件引入

```cpp
#include "PixelCapture.h"
#include "PixelCaptureCapturer.h"
```

### 基本用法

```cpp
// 来源: 概念来自 Source/PixelCapture/Private/PixelCaptureCapturer.cpp
// 创建一个从BGRA8到I420格式的捕获器链
TSharedPtr<FPixelCaptureCapturer> Capturer = FPixelCaptureCapturer::CreateCapturerChain(
    SourceRHI, // FTextureRHIRef，源纹理
    EPixelFormat::PF_B8G8R8A8, // 源格式
    EPixelFormat::PF_R8G8B8A8_UINT, // 目标格式 (I420的表示)
    FPixelCaptureCapturerArgs()
);

// 在渲染线程上执行捕获
Capturer->Capture();
// 等待捕获完成（可能涉及GPU同步）
Capturer->WaitForCapture();

// 获取结果
TArray<FColor> ResultPixels;
Capturer->GetOutput().ReadPixels(ResultPixels);
```

### 进阶用法

```cpp
// 来源: 概念来自 Source/PixelCapture/Private/PixelCaptureSubsystem.cpp
// 使用管理器来创建和管理捕获器链，更适合生产环境
UPixelCaptureSubsystem* CaptureSubsystem = GEngine->GetEngineSubsystem<UPixelCaptureSubsystem>();
if (CaptureSubsystem)
{
    // 注册一个捕获需求
    FPixelCaptureHandle CaptureHandle = CaptureSubsystem->RequestCapture(
        SourceTexture,
        TargetFormat,
        [WeakThis = MakeWeakObjectPtr(this)](FPixelCaptureHandle Handle, const FPixelCaptureOutput& Output)
        {
            // 异步回调：在捕获完成后被调用
            if (UYourClass* This = WeakThis.Get())
            {
                This->OnFrameCaptured(Output.GetTextureRHI());
            }
        });
    
    // 后续可以使用Handle暂停/恢复/取消捕获
}
```

## Demo 示例

**PixelCaptureDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PixelCaptureCapturer.h"
#include "PixelCaptureDemo.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UPixelCaptureDemo : public UActorComponent
{
    GENERATED_BODY()

public:
    // 开始捕获
    UFUNCTION(BlueprintCallable)
    void StartCapture(UTexture* SourceTexture);

    // 停止捕获
    UFUNCTION(BlueprintCallable)
    void StopCapture();

private:
    TSharedPtr<FPixelCaptureCapturer> Capturer;
    FTextureRHIRef OutputTexture;
};
```

**PixelCaptureDemo.cpp**
```cpp
#include "PixelCaptureDemo.h"
#include "PixelCapture.h"

void UPixelCaptureDemo::StartCapture(UTexture* SourceTexture)
{
    if (!SourceTexture || !SourceTexture->GetResource()) return;

    FTextureRHIRef SourceRHI = SourceTexture->GetResource()->GetTexture2DRHI();
    if (!SourceRHI) return;

    // 创建一个捕获链，将BGRA转为I420（常用于H.264编码）
    Capturer = FPixelCaptureCapturer::CreateCapturerChain(
        SourceRHI,
        EPixelFormat::PF_B8G8R8A8,
        EPixelFormat::PF_R8G8B8A8_UINT, // 代表I420
        FPixelCaptureCapturerArgs()
    );

    if (Capturer)
    {
        // 简单演示：在下一帧执行捕获
        ENQUEUE_RENDER_COMMAND(CaptureFrameCmd)(
            [WeakCapturer = MakeWeakPtr(Capturer)](FRHICommandListImmediate& RHICmdList)
            {
                if (TSharedPtr<FPixelCaptureCapturer> CapturerPin = WeakCapturer.Pin())
                {
                    CapturerPin->Capture();
                    // 注意：实际使用中，获取输出需要同步或异步等待
                }
            });
    }
}

void UPixelCaptureDemo::StopCapture()
{
    Capturer.Reset();
}
```

## 模块依赖

本插件依赖于MediaIOFramework插件，用于标准化的媒体I/O集成。

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 提供与媒体捕获和输出设备集成的框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统从 UE_LOG 迁移至 UE_LOGF |
| 2026-03-16 | `d0c437a7` | [PixelCapture, PixelStreaming2] Fix: Multiple issues for RemoteSession on Android | 修复 Android 平台上 RemoteSession 的多个问题 |
| 2026-03-12 | `225cb015` | [PixelCapture] Fix: Missing sRGB flag when required | 修复在需要时缺少 sRGB 标志的问题 |
| 2026-02-06 | `f087dbb2` | [PixelCapture] Fix: Potential deadlock when pinning weak UObject ptr | 修复引用弱 UObject 指针时潜在的死锁 |

### 维护评价

该插件处于 **Beta 实验性阶段**，创建于2022年8月。从近期提交历史看，维护**非常活跃**，近几个月持续有功能增强、平台兼容性修复和稳定性改进（如Android支持、死锁修复）。虽然默认未启用，但它是官方 Pixel Streaming 功能链的关键组成部分，有持续的工程投入。**推荐关注并用于相关项目**，但需注意其 Beta 状态可能带来 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelCapture)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/PixelCapture)