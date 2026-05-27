# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 媒体IO框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOCore` (Runtime), `MediaIOEditor` (Editor), `GPUTextureTransfer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-10-02 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework) | |

## 用途

MediaIOFramework 是虚拟制片工作流的核心基础设施，主要解决与专业媒体硬件（如 AJA、Blackmagic 等采集卡/输出卡）进行高质量、低延迟的实时视频输入输出（I/O）问题。它抽象了底层硬件差异，为 UE5 的虚拟制片、实时合成、广播等场景提供了统一的媒体帧捕获、传输和渲染接口。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在 LED 墙体上实时渲染并输出摄像机画面，或从外部摄像机实时捕获画面用于合成。
-   **实时合成 (Compositing)**：将外部视频源（如实拍素材）无缝集成到 UE 场景中。
-   **广播与直播 (Broadcasting & Live)**：将引擎渲染画面以专业 SDI/HDMI 信号输出到导播台或录制设备。
-   **监控与质量检查 (Monitoring & QC)**：使用专业监视器查看引擎输出的最终画面色彩和信号质量。

## 蓝图用法

*注意：此插件主要面向 C++ 开发和编辑器集成，蓝图 API 通常用于配置和触发。以下为核心概念节点。*

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Media Output` | 在指定的媒体配置下，查找可用的媒体输出设备 | `UMediaIOSubsystem` |
| `Get Media Configuration` | 获取当前的媒体输入/输出配置（分辨率、帧率等） | `UMediaIOSubsystem` |
| `Capture Texture` | 将引擎内指定的纹理（如场景捕获）捕获到媒体IO通道 | `UMediaIOSubsystem` |

### 使用示例（蓝图描述）

1.  **获取并配置媒体输出**：
    -   调用 `Find Media Output` 节点，传入所需的硬件接口（如 AJA）、输出端口等参数，获取一个 `FMediaOutputDevice` 对象。
    -   使用 `Get Media Configuration` 设置期望的分辨率（如 1080p）和帧率。
2.  **开始输出**：
    -   将配置好的 `FMediaOutputDevice` 对象传递给类似 `Start Output` 的函数。
    -   引擎中指定的渲染目标（Render Target）或场景捕获组件（Scene Capture Component）的画面将开始实时输出到该设备。

## C++ 用法

### 头文件引入

```cpp
#include "MediaIOCoreSubsystem.h"
#include "MediaOutput.h"
#include "MediaCapture.h"
```

### 基本用法

以下示例展示如何通过 C++ 查找设备并开始媒体输出。
*（来源：基于插件核心模块的功能设计）*

```cpp
// 获取媒体IO子系统
UMediaIOSubsystem* MediaIOSubsystem = GEngine->GetEngineSubsystem<UMediaIOSubsystem>();
if (MediaIOSubsystem)
{
    // 定义媒体输出设备配置
    FMediaOutputDevice DesiredOutput;
    DesiredOutput.MediaConnection.Device.deviceIdentifier = TEXT("AJA-1");
    DesiredOutput.MediaConnection.Port.PortIdentifier = TEXT("SDI1");
    DesiredOutput.VideoMode.Width = 1920;
    DesiredOutput.VideoMode.Height = 1080;
    DesiredOutput.VideoMode.FrameRate = FFrameRate(60, 1);

    // 查找匹配的媒体输出
    FMediaOutputDevice OutputDevice;
    if (MediaIOSubsystem->FindOutputDevice(DesiredOutput, OutputDevice))
    {
        // 创建并配置媒体捕获对象
        UMediaCapture* MediaCapture = NewObject<UMediaCapture>();
        MediaCapture->SetOutputDevice(OutputDevice);
        // 将一个渲染目标（RT）绑定到捕获对象
        MediaCapture->SetRenderTarget(MyRenderTarget);

        // 开始捕获/输出
        MediaCapture->StartCapture();
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，用于演示媒体输出的核心流程。
*（功能原理说明，非实际文件）*

```cpp
// MediaIOMinimalExample.h
#pragma once
#include "CoreMinimal.h"

class FMediaIOMinimalExample
{
public:
    void InitAndStartOutput();
    void StopOutput();

private:
    UPROPERTY()
    UMediaCapture* ActiveCapture = nullptr;
};
```

```cpp
// MediaIOMinimalExample.cpp
#include "MediaIOMinimalExample.h"
#include "MediaIOCoreSubsystem.h"
#include "MediaOutput.h"
#include "MediaCapture.h"

void FMediaIOMinimalExample::InitAndStartOutput()
{
    UMediaIOSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMediaIOSubsystem>();
    if (!Subsystem) return;

    // 配置一个 Blackmagic DeckLink 设备的输出
    FMediaOutputDevice OutputConfig;
    OutputConfig.MediaConnection.Device.deviceIdentifier = TEXT("Blackmagic DeckLink");
    OutputConfig.MediaConnection.Port.PortIdentifier = TEXT("Port 1");
    OutputConfig.VideoMode = FVideoModeInfo(FIntPoint(1280, 720), FFrameRate(30, 1));

    FMediaOutputDevice FoundDevice;
    if (Subsystem->FindOutputDevice(OutputConfig, FoundDevice))
    {
        ActiveCapture = NewObject<UMediaCapture>();
        ActiveCapture->SetOutputDevice(FoundDevice);
        // 假设已经有一个有效的渲染目标 'MyRT'
        // ActiveCapture->SetRenderTarget(MyRT);
        ActiveCapture->StartCapture();
    }
}

void FMediaIOMinimalExample::StopOutput()
{
    if (ActiveCapture && ActiveCapture->IsCapturing())
    {
        ActiveCapture->StopCapture();
    }
    ActiveCapture = nullptr;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | GPUTextureTransfer 模块用于实现高效的 GPU 纹理到媒体硬件缓冲区的拷贝 |
| `LevelEditor` | MediaIOCore 模块用于集成媒体IO配置到编辑器的视口和场景管理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为Blackmagic和AJA采集卡的自动配置模式填充媒体配置 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为多个媒体播放器和捕获类添加了额外的引擎分析信息 |
| 2026-05-14 | `a43a62b2` | Media Profile: Changed media texture capture behavior to always preserve aspect ratio of texture eve | 更改媒体纹理捕获行为，始终保留纹理的原始宽高比 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量被截断为浮点数并产生警告的代码 |
| 2026-05-12 | `a879de69` | Fix clang warnings when compiling MediaIODeinterlacerTests | 修复编译MediaIODeinterlacerTests时的clang编译器警告 |

### 维护评价

**活跃维护**。插件自 2018 年创建以来持续更新，是虚拟制片核心管线的一部分。近期的更新（2026年5月）主要集中在**功能增强**（如自动配置、宽高比保持、分析信息）和**代码质量**修复上，表明 Epic 仍在积极维护此插件，以适应专业媒体硬件的新特性和工作流优化需求。虽然需要手动启用 (`EnabledByDefault: false`)，但其在虚拟制片领域不可或缺。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework)
-   [官方文档](https://docs.unrealengine.com/) (搜索 “Media IO Framework” 或 “Virtual Production Media”)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework/Source/GPUTextureTransfer/Private/Tests) （示例路径，GPUTextureTransfer模块包含测试代码）