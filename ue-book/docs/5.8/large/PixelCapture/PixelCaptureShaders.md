# Pixel Capture

> Framework for capturing pixel buffers in other formats while allowing for disconnected produce/consume rates.

| 属性 | 值 |
|---|---|
| 中文名 | 像素捕获 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（着色器资源） |
| 模块 | `PixelCapture` (Runtime), `PixelCaptureShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelCapture) | |

## 用途

PixelCapture 是一个像素缓冲区捕获框架，专为需要从 GPU 读取像素数据并转换为不同格式的场景设计。其核心特性是**生产者/消费者速率解耦**——像素捕获（生产者）和像素处理（消费者）可以运行在不同的帧率上，互不阻塞。

该插件最初是为 **Pixel Streaming** 场景创建的，用于在流式传输过程中高效地捕获帧缓冲并编码为网络可传输的格式（如 YUV）。它通过 GPU 着色器完成色彩空间转换（RGB → YUV），避免了 CPU 端逐像素处理的性能瓶颈。

**为什么存在？** 像素流式传输、远程渲染、画面录制等场景都需要从 GPU 读取帧数据，但传统的 `ReadPixels` 操作既慢又会打断渲染管线。PixelCapture 提供了一套异步、解耦的框架，让捕获和编码可以各自以最优速率运行。

## 使用场景

- 你在做 **Pixel Streaming** → 用 PixelCapture 捕获渲染输出并编码为视频流
- 你需要将画面帧数据导出到 **WebRTC** 编码器 → 用 PixelCapture 提供的 YUV 转换着色器
- 你在做 **Remote Session** 或远程桌面功能 → 用 PixelCapture 异步捕获屏幕内容
- 你需要在 **不同帧率下** 采集和处理画面（如 60fps 捕获、30fps 编码）→ 利用解耦速率机制

## 蓝图用法

该插件主要面向 C++ 层面使用，未暴露蓝图节点。核心功能通过 Runtime 模块的 C++ API 和 Compute Shader 调度实现。

## C++ 用法

### 头文件引入

```cpp
#include "RGBToYUVShader.h"
```

### 基本用法 — RGB 到 YUV 着色器转换

该插件的核心着色器功能之一是将 RGB 纹理通过 GPU Compute Shader 高效转换为 YUV 格式的三个独立平面。以下展示如何调度 RGB → YUV 转换着色器：

```cpp
// 来源: Engine/Plugins/Media/PixelCapture/Source/PixelCaptureShaders/Public/RGBToYUVShader.h

// 1. 准备参数
FRGBToYUVShaderParameters ShaderParams;
ShaderParams.SourceTexture = SourceTextureRHI;              // 源 RGB 纹理
ShaderParams.DestPlaneYDimensions = FIntPoint(1920, 1080);  // Y 平面尺寸
ShaderParams.DestPlaneUVDimensions = FIntPoint(960, 540);   // UV 平面尺寸（通常为半分辨率）
ShaderParams.DestPlaneY = DestYUAV;                         // Y 平面 UAV
ShaderParams.DestPlaneU = DestUUAV;                         // U 平面 UAV
ShaderParams.DestPlaneV = DestVUAV;                         // V 平面 UAV

// 2. 在 RHI 命令列表上调度着色器
FRGBToYUVShader::Dispatch(RHICmdList, ShaderParams);
```

### 进阶用法 — 解耦速率捕获

PixelCapture 的设计核心是生产者/消费者速率解耦。典型使用模式如下：

```cpp
// 伪代码示意（基于框架设计理念）

// 生产者端：以渲染帧率捕获像素数据
// 每帧将捕获的帧缓冲推入环形缓冲区
void OnRenderFrame(FRHICommandListImmediate& RHICmdList, FTextureRHIRef BackBuffer)
{
    // 将当前帧加入捕获队列，立即返回，不阻塞渲染
    PixelCaptureProducer->EnqueueCapture(RHICmdList, BackBuffer);
}

// 消费者端：以独立速率（如编码器帧率）取出数据
// 例如每 33ms（30fps）处理一帧，即使渲染是 60fps
void OnEncodeTick()
{
    if (auto LatestFrame = PixelCaptureConsumer->DequeueLatest())
    {
        // 对 LatestFrame 进行编码处理
        // 框架自动处理时序对齐
    }
}
```

## Demo 示例

```cpp
// RGBToYUVCapture.h
#pragma once

#include "RGBToYUVShader.h"

class FRGBToYUVCaptureExample
{
public:
    void CaptureAndConvert(FRHICommandListImmediate& RHICmdList,
                           FTextureRHIRef InSourceTexture,
                           FUnorderedAccessViewRHIRef OutPlaneY,
                           FUnorderedAccessViewRHIRef OutPlaneU,
                           FUnorderedAccessViewRHIRef OutPlaneV,
                           FIntPoint InResolution);
};

// RGBToYUVCapture.cpp
#include "RGBToYUVCapture.h"

void FRGBToYUVCaptureExample::CaptureAndConvert(
    FRHICommandListImmediate& RHICmdList,
    FTextureRHIRef InSourceTexture,
    FUnorderedAccessViewRHIRef OutPlaneY,
    FUnorderedAccessViewRHIRef OutPlaneU,
    FUnorderedAccessViewRHIRef OutPlaneV,
    FIntPoint InResolution)
{
    FRGBToYUVShaderParameters Params;
    Params.SourceTexture = InSourceTexture;
    Params.DestPlaneYDimensions = InResolution;
    Params.DestPlaneUVDimensions = FIntPoint(InResolution.X / 2, InResolution.Y / 2);
    Params.DestPlaneY = OutPlaneY;
    Params.DestPlaneU = OutPlaneU;
    Params.DestPlaneV = OutPlaneV;

    FRGBToYUVShader::Dispatch(RHICmdList, Params);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 媒体 IO 框架，提供媒体捕获和输出基础设施 |
| `RenderCore` | 渲染核心，提供 RHI 命令列表和纹理类型定义 |
| `RHI` | 渲染硬件接口，提供底层 GPU 资源（UAV、纹理等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-03-16 | `d0c437a7` | [PixelCapture, PixelStreaming2] Fix: Multiple issues for RemoteSession on Android | 修复 Android 平台 RemoteSession 的多个问题 |
| 2026-03-12 | `225cb015` | [PixelCapture] Fix: Missing sRGB flag when required | 修复需要 sRGB 标记时缺失的问题 |
| 2026-02-06 | `f087dbb2` | [PixelCapture] Fix: Potential deadlock when pinning weak UObject ptr | 修复 pin 弱 UObject 指针时的潜在死锁 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2022 年 8 月，约 4 年历史，相对年轻
- **更新频率**：近 4 个月内有 5 次提交，维护节奏稳定
- **更新内容**：包含 Android 平台修复、sRGB 标记修复、死锁修复等实质性 bugfix，说明仍在被实际使用和维护
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，API 可能发生变化
- **平台支持**：支持 Win64/Linux/Mac/Android/iOS，排除 Server 目标，符合其像素捕获用途
- **注意**：该插件标记为 Beta，不建议在生产环境中作为核心依赖；如用于 Pixel Streaming 场景，推荐关注 PixelStreaming2 的更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelCapture)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)（Pixel Streaming 相关）
- [RGBToYUVShader 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Media/PixelCapture/Source/PixelCaptureShaders/Public/RGBToYUVShader.h)