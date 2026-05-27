# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体IO框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOCore` (Runtime), `MediaIOEditor` (Editor), `GPUTextureTransfer` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-10-02 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework) | |

## 用途

MediaIOFramework 为虚拟制作行业提供了一套核心框架，用于处理专业级媒体输入/输出（IO）操作。它并非一个面向最终用户的插件，而是作为底层基石，支持诸如 AJA、Blackmagic Design 等专业视频采集卡与 Unreal Engine 之间的集成。该插件解决了将引擎实时渲染画面（如场景视口、渲染目标）无损、低延迟地输出到外部专业设备（如 LED 墙、监视器）的核心问题，同时也支持从这些设备捕获视频和音频信号作为引擎内的源。它是构建高质量、帧同步的虚拟制作管线的基础。

## 使用场景

- 你需要将 Unreal Engine 实时渲染的画面发送到现场的 LED 墙幕或广播级监视器。
- 你需要在多机位虚拟制作环境中，同步多个采集卡输入的视频和音频信号。
- 你正在开发一个基于 AJA、Blackmagic 等硬件的媒体源或媒体输出插件，并需要一个稳定的底层数据传输和帧管理框架。
- 你需要精确的帧锁定（Frame Lock）和时间码同步，以确保渲染输出与外部设备的时间线对齐。

## 蓝图用法

本插件的核心功能通常通过其子类实现（如具体的媒体输出、媒体捕获类）来使用，但基类提供了关键蓝图可调用方法。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Capture Active Scene Viewport` | 捕获当前活动的场景视口。在独立窗口PIE或独立运行时可用。 | `UMediaCapture` |
| `Capture Texture Render Target 2D` | 捕获一个 `UTextureRenderTarget2D` 的内容。 | `UMediaCapture` |
| `Capture Media Texture` | 捕获一个 `UMediaTexture` 的内容。 | `UMediaCapture` |
| `Stop Capture` | 停止当前的捕获操作。 | `UMediaCapture` |
| `Get State` | 获取媒体捕获的当前状态（如 `Capturing`， `Stopped`）。 | `UMediaCapture` |
| `Create Media Capture` | 根据媒体输出设置创建一个对应的媒体捕获实例。 | `UMediaOutput` |

### 使用示例（蓝图描述）

1. **捕获视口输出到文件**：
   - 创建一个 `UFileMediaOutput` 资产并设置输出路径和格式。
   - 使用 `Create Media Capture` 节点从该输出创建捕获实例。
   - 调用 `Capture Active Scene Viewport` 启动捕获。
   - 通过 `Get State` 节点监控捕获状态，在适当时候调用 `Stop Capture`。

2. **将渲染目标输出到外部设备**：
   - 假设你有一个实现了具体输出逻辑的 `UMediaOutput` 子类。
   - 在该子类的蓝图实例中调用 `Create Media Capture`。
   - 对你的 `UTextureRenderTarget2D` 调用 `Capture Texture Render Target 2D`。

## C++ 用法

### 头文件引入

```cpp
#include "MediaCapture.h"
#include "MediaOutput.h"
#include "CaptureCardMediaSource.h" // 如果你需要创建基于采集卡的媒体源
```

### 基本用法

此框架通常不直接使用，而是被具体的插件（如 AJAMedia 插件）继承和实现。基本流程如下：
1.  **创建媒体输出配置**：定义输出目标（如具体的 AJA 设备连接）。
2.  **创建媒体捕获**：通过 `UMediaOutput::CreateMediaCapture()` 创建捕获实例。
3.  **启动捕获**：调用 `CaptureSceneViewport` 或 `CaptureTextureRenderTarget2D`。
4.  **处理回调**：在子类中重写 `OnFrameCaptured_RenderingThread` 或 `OnRHIResourceCaptured_RenderingThread` 来处理被捕获的帧数据。
5.  **停止捕获**：调用 `StopCapture`。

### 进阶用法

高级用法涉及实现 `IMediaIOCoreDeviceProvider` 接口以向系统注册新的设备类型，并管理帧同步、音频捕获（`FMediaIOAudioCapture`）和去隔行（`UVideoDeinterlacer`）等复杂功能。`FMediaIOCorePlayerBase` 是媒体播放器的核心基类，处理样本管理、时间评估和 GPU 纹理传输。

## Demo 示例

以下是一个极简的示例，演示如何创建一个自定义的媒体捕获，并开始捕获一个渲染目标。

**MyMediaCapture.h**
```cpp
#pragma once

#include "MediaCapture.h"
#include "MyMediaCapture.generated.h"

UCLASS()
class UMyMediaCapture : public UMediaCapture
{
    GENERATED_BODY()

protected:
    // 当一帧被捕获到系统内存时回调
    virtual void OnFrameCaptured_RenderingThread(
        const FCaptureBaseData& InBaseData,
        TSharedPtr<FMediaCaptureUserData, ESPMode::ThreadSafe> InUserData,
        void* InBuffer,
        int32 Width,
        int32 Height,
        int32 BytesPerRow) override
    {
        // 在这里处理捕获到的像素数据 (InBuffer)
        // 例如：发送到外部设备、进行额外处理等。
        // 此时图像数据位于CPU内存，格式由 UMediaOutput::GetRequestedPixelFormat() 决定。
    }

    virtual bool InitializeCapture() override
    {
        // 初始化资源，例如分配内存缓冲区。
        return true;
    }

    // 其他必要的重写方法...
};
```

**MyMediaOutput.h**
```cpp
#pragma once

#include "MediaOutput.h"
#include "MyMediaOutput.generated.h"

UCLASS()
class UMyMediaOutput : public UMediaOutput
{
    GENERATED_BODY()

public:
    virtual FIntPoint GetRequestedSize() const override
    {
        // 请求与源相同大小，或指定一个固定大小
        return UMediaOutput::RequestCaptureSourceSize;
    }

    virtual EPixelFormat GetRequestedPixelFormat() const override
    {
        // 例如，请求 8 位 RGBA 格式
        return EPixelFormat::PF_B8G8R8A8;
    }

protected:
    virtual UMediaCapture* CreateMediaCaptureImpl() override
    {
        return NewObject<UMyMediaCapture>(this);
    }
};
```

## 模块依赖

从 Build.cs 的依赖分析，以下是该插件独特且关键的依赖。多数核心模块（Core， Engine等）已被省略。

| 模块 | 用途 |
|---|---|
| `OpenColorIO` | 提供 OpenColorIO (OCIO) 颜色空间转换功能，用于媒体捕获和播放时的颜色管理。 |
| `VulkanRHI` | `GPUTextureTransfer` 模块依赖，用于通过 Vulkan 实现高性能的 GPU 直接内存访问（GPUDirect）纹理传输。 |
| `LevelEditor` | `MediaIOCore` 模块依赖，用于访问编辑器关卡视图等特定功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为Blackmagic和AJA卡的自动检测模式填充媒体配置。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和捕获等添加了额外的引擎分析信息。 |
| 2026-05-14 | `a43a62b2` | Media Profile: Changed media texture capture behavior to always preserve aspect ratio of texture even | 改变了媒体纹理捕获行为，即使在...情况下也始终保留纹理宽高比。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下产生双精度常量截断为浮点数警告的代码。 |
| 2026-05-12 | `a879de69` | Fix clang warnings when compiling MediaIODeinterlacerTests | 修复编译MediaIODeinterlacerTests时的clang警告。 |

### 维护评价

MediaIOFramework 是一个核心框架插件，创建于 2018 年，拥有较长的历史。**从近期（2026年5月）密集的提交记录来看，该插件仍在被 Epic Games 积极维护和更新**。近期的更新集中在功能增强（如自动配置填充、分析数据）、行为优化（宽高比保留）和编译警告修复上，表明其与最新的引擎特性（如编辑器分析）保持同步。作为虚拟制作的基础设施，它相对稳定，是开发专业媒体IO插件的可靠基础。虽然默认禁用（需要特定硬件插件启用），但其代码库活跃，推荐在相关的专业领域内使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework)
- 官方文档：此插件本身通常不单独列出文档，其功能通过具体硬件插件（如 AJA， Blackmagic）的文档体现。
- 测试用例：未在提供的路径中发现明确的测试文件。