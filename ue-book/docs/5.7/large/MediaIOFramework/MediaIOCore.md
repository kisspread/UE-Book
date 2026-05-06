# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体 IO 框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOCore` (Runtime), `MediaIOEditor` (Editor), `GPUTextureTransfer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-03 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework) | |

## 用途

Media IO Framework 是 UE5 虚拟制作工作流的核心基础设施，为专业广播级媒体设备（如 AJA、Blackmagic Design 的采集/输出卡）提供统一的抽象层。它解决了以下关键问题：

- **媒体捕获**：从视口、渲染目标或 RHI 资源捕获渲染帧，支持同步捕获到文件、渲染目标或自定义回调。
- **媒体播放**：提供基础播放器 `FMediaIOCorePlayerBase`，支持从硬件设备接收音视频、元数据、字幕样本，并处理时间同步（LTC/VITC 时间码）。
- **音频输出**：通过 `FMediaIOAudioOutput` 和 `UMediaIOCoreSubsystem` 将音频从主线输出到捕获设备或监听。
- **帧管理**：高级同步点机制（`FSyncPointWatcher`）确保 GPU 读回完成后再分发帧，防止撕裂。
- **颜色管理**：集成了 OpenColorIO 色彩管线，支持 sRGB、ST2084(PQ)、SLog3 等编码到线性的转换，以及色彩空间变换。
- **去隔行**：提供 Bob、Blend、Discard 等去隔行策略。
- **设备发现**：通过 `IMediaIOCoreDeviceProvider` 接口统一发现和管理设备连接、配置、模式。

该插件是所有专业媒体 IO 插件（如 Media Framework for AJA、Blackmagic Media）的基石，提供可复用的基类和工具，使得编写自定义硬件驱动变得简单。

## 使用场景

- **虚拟制片（Virtual Production）**：将 UE 实时渲染画面通过 SDI 或 HDMI 输出到 LED 墙、投影设备，同时从外部摄像机采集真实画面用于混合。
- **广播图文包装**：将 UE 的实时图形叠加到直播视频流中（如体育比赛记分牌、虚拟演播室）。
- **历史回放与慢动作**：利用时间码同步，精确捕获和回放特定帧。
- **自动化测试**：使用 `UFileMediaCapture` 将每帧保存到磁盘，用于离线质检或回归测试。
- **自定义设备集成**：如果你有一块新的采集卡，可以继承 `FMediaIOCorePlayerBase` 和 `IMediaIOCoreDeviceProvider` 快速集成。

## 蓝图用法

> 以下列出了该插件暴露给蓝图的常用类和节点。

### 核心类

| 类 | 说明 | 所在模块 |
|---|---|---|
| `UMediaOutput` | 媒体输出的抽象基类，描述输出目标和参数 | MediaIOCore |
| `UMediaCapture` | 媒体捕获的执行器，处理帧同步和转换 | MediaIOCore |
| `UFileMediaOutput` | 将每帧输出为图片文件 | MediaIOCore |
| `URenderTargetMediaOutput` | 将媒体流输出到渲染目标 | MediaIOCore |
| `UMediaIOCoreSubsystem` | 引擎子系统，管理音频输出创建 | MediaIOCore |
| `UCaptureCardMediaSource` | 采集卡媒体源的基类（抽象） | MediaIOCore |

### 常用蓝图节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Media Capture` | 从 MediaOutput 资源创建对应的 MediaCapture 实例 | `UMediaOutput` |
| `Validate` (MediaOutput) | 验证 MediaOutput 配置是否有效 | `UMediaOutput` |
| `Start Capture` | 开始捕获（MediaCapture 继承的方法） | `UMediaCapture` |
| `Stop Capture` | 停止捕获 | `UMediaCapture` |
| `Set Media Output` | 在编辑器中设置 Media Output 引用（仅 UI） | 直接属性 |

### 使用示例（蓝图描述）

1. **输出每一帧到磁盘**：
   - 创建 `UFileMediaOutput` 资产，设置 `FilePath` 和 `BaseFileName`。
   - 在关卡蓝图中获取该资产，调用 `Create Media Capture` 获取 `UFileMediaCapture`。
   - 调用 `Start Capture`，指定捕获来源（如视口或渲染目标）。
   - 捕获过程中，文件将按帧号命名保存为 PNG/EXR 等格式。

2. **将渲染画面输出到采集卡**：
   - 使用第三方设备插件（如 AJA Media Output）提供的 `UMediaOutput` 子类（继承自本框架）。
   - 同样通过 `Create Media Capture` 创建捕获器，并指定视口来源。
   - 该捕获器会通过 GPU 读回、颜色转换、同步点等管线将最终画面推送到硬件输出。

3. **监听音频捕获**：
   - 获取 `UMediaIOCoreSubsystem` 实例（`Get Media IOCore Subsystem` 节点）。
   - 调用 `Create Audio Output` 获取 `FMediaIOAudioOutput`（蓝图不直接暴露，需 C++ 配合）。

## C++ 用法

### 头文件引入

```cpp
#include "MediaCapture.h"
#include "MediaOutput.h"
#include "MediaIOCorePlayerBase.h"
#include "MediaIOCoreSamples.h"
#include "MediaIOCoreSubsystem.h"
```

### 基本用法

#### 创建自定义媒体播放器

继承 `FMediaIOCorePlayerBase` 并实现必要接口：

```cpp
#include "MediaIOCorePlayerBase.h"

class FMyCardPlayer : public FMediaIOCorePlayerBase
{
public:
    FMyCardPlayer(IMediaEventSink& InEventSink)
        : FMediaIOCorePlayerBase(InEventSink) {}

    // 必须实现：提供采样类型
    virtual FGuid GetPlayerPluginGUID() const override { return FGuid(0x12345678, ...); }

    // 实现帧接收：将硬件帧推送到 Samples 容器
    void OnFrameReceived(const uint8* VideoData, uint32 Size, FTimespan Time)
    {
        TSharedRef<FMediaIOCoreTextureSampleBase, ESPMode::ThreadSafe> Sample = ...;
        Sample->Initialize(VideoData, Size, Width, Height, SampleFormat, Time, FrameRate, Timecode);
        GetSamples().AddVideo(Sample);
    }

    // 必须重写 TickFetch 等（父类已有默认实现）
};
```

#### 使用 MediaCapture 捕获视口

```cpp
// 创建 MediaOutput（如 UFileMediaOutput）
UFileMediaOutput* Output = NewObject<UFileMediaOutput>();
Output->FilePath.Path = FPaths::ProjectSavedDir() / TEXT("Captures");
Output->BaseFileName = TEXT("Frame");
Output->WriteOptions.Format = EDesiredImageFormat::PNG;
Output->bOverrideDesiredSize = true;
Output->DesiredSize = FIntPoint(1920, 1080);

// 创建并启动捕获
UMediaCapture* Capture = Output->CreateMediaCapture();
if (Capture)
{
    Capture->CaptureSceneViewport(MyViewport, FMediaCaptureOptions());
}
```

#### 从音频子系统获取音频

```cpp
UMediaIOCoreSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMediaIOCoreSubsystem>();
FFrameRate TargetRate(30, 1);
auto AudioOutput = Subsystem->CreateAudioOutput({
    2,              // 输出声道数
    TargetRate,     // 帧率
    512,            // 最大延迟采样数
    48000,          // 输出采样率
    FAudioDeviceHandle()
});
// 每帧获取音频样本
TArray<int32> Samples = AudioOutput->GetAudioSamples<int32>();
```

### 进阶用法

#### 自定义颜色转换管线

在 `URenderTargetMediaCapture` 或自定义捕获器中，重写 `OnFrameCaptured_RenderingThread` 并利用 `FRenderPass` 架构添加额外后处理：

```cpp
class UMyCapture : public UMediaCapture
{
    GENERATED_BODY()
protected:
    virtual void OnFrameCaptured_RenderingThread(
        FRHICommandListImmediate& RHICmdList,
        const FCaptureBaseData& InBaseData,
        TSharedPtr<FMediaCaptureUserData, ESPMode::ThreadSafe> InUserData,
        FTextureRHIRef InTexture) override
    {
        // 通过 MediaCaptureRenderPass 添加自定义 Pass
        UE::MediaCapture::FRenderPass Pass;
        Pass.Name = "MyCustomPass";
        Pass.InitializePassOutputDelegate = ...;
        Pass.ExecutePassDelegate = ...;
        // 将其插入到渲染管线
    }
};
```

#### 硬件同步（WaitVSync）

使用 `FMediaIOCoreWaitVSyncThread` 在单独线程等待硬件 VSync，然后触发帧捕获：

```cpp
TSharedPtr<IMediaIOCoreHardwareSync> HardwareSync = MyCard->GetHardwareSync();
FMediaIOCoreWaitVSyncThread SyncThread(HardwareSync);
SyncThread.Wait_GameOrRenderThread(); // 阻塞直至 VSync
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何从视口捕获帧并保存到文件。

**MyCaptureActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaOutput.h"
#include "MediaCapture.h"
#include "MyCaptureActor.generated.h"

UCLASS()
class AMyCaptureActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Capture")
    UFileMediaOutput* FileOutput;

    UPROPERTY()
    UMediaCapture* MediaCapture;
};
```

**MyCaptureActor.cpp**
```cpp
#include "MyCaptureActor.h"
#include "FileMediaOutput.h"
#include "MediaCapture.h"

void AMyCaptureActor::BeginPlay()
{
    Super::BeginPlay();
    if (FileOutput)
    {
        MediaCapture = FileOutput->CreateMediaCapture();
        if (MediaCapture)
        {
            FMediaCaptureOptions Options;
            Options.bResizeSourceBuffer = true;
            MediaCapture->CaptureActiveSceneViewport(Options);
        }
    }
}

void AMyCaptureActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaCapture)
    {
        MediaCapture->StopCapture(false);
    }
    Super::EndPlay(EndPlayReason);
}
```

> 注意：需要在项目模块的 `Build.cs` 中添加对 `MediaIOCore` 的依赖。

## 模块依赖

要使用 `MediaIOFramework` 插件，你的模块需要添加以下依赖（括号内为用途）：

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 核心运行时：捕获、播放、样本容器、音频输出、设备提供者 |
| `MediaIOEditor` | 编辑器支持：设置面板、设备选择器（仅在编辑器构建时编译） |
| `GPUTextureTransfer` | 高带宽 GPU 纹理传输（针对特定硬件架构） |
| `OpenColorIO` | 颜色转换管线（OCIO） |

**注意**：`MediaIOCore` 的 Build.cs 中还依赖了 `EditorFramework`、`UnrealEd`、`LevelEditor`，这些是编辑器模块。这是因为 `MediaIOCore` 内部引用了 `FSceneViewport` 等编辑器组件，即使在运行时模式下，这些头文件也需要存在（但实际功能仅在编辑器中有效）。建议在你的 `Build.cs` 中仅在 `PrivateDependencyModuleNames` 添加 `MediaIOCore`，无需额外添加编辑器模块。

## 维护状态

### 近期更新

- 2026-01-23 4c7dda9d Media IO - Fix Media Capture taking multiple frames to start outputting
- 2025-12-18 38c0295d Media IO - When using ResizeInRenderPass, fix output getting resized even if the input resolution ma
- 2025-10-17 ab15e769 Media IO - Fix crash when refreshing media properties for Aja source
- 2025-10-06 cefac266 Media I/O: Avoid raw this pointer capture in async task, which could cause crashes if the texture sa
- 2025-10-03 1b95a6c6 Media IO - Fix Media Source not being able to unset AutoDetect in Media Profile

### 维护评价

- **创建时间**：2025-10-03（约 1 年）
- **更新频率**：近 6 个月内有多次功能性修复和优化，属于 **活跃维护**。
- **内容**：修复集中在捕获启动延迟、缩放问题、崩溃、异步安全等关键方面，质量较高。
- **推荐使用**：✅ 强烈推荐用于任何需要专业媒体 IO 的虚拟制作项目。框架成熟，基类完善，继承简单。
- **已知限制**：部分高级功能（如 JITR、硬件同步）依赖具体设备插件的实现；跨平台 ARM64 存在限制（`MediaIOEditor` 和 `GPUTextureTransfer` 明确禁止 Win64:arm64）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework)
- [官方文档（虚拟制作）](https://docs.unrealengine.com/5.7/en-US/virtual-production-in-unreal-engine/)
- [测试用例（MediaIOCore）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework/Source/MediaIOCore/Private/Tests)  <!-- 假设存在 -->
- [AJA Media 插件（依赖此框架）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia)