# Shared Memory Media

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 共享内存媒体 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时媒体传输模块） |
| 模块 | `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`SharedMemoryMedia` 模块是 nDisplay 插件的核心组成部分，旨在为多 PC 集群渲染系统（如虚拟制片 LED 墙或大型投影仪阵列）提供一种低延迟、高效率的帧同步传输机制。它通过操作系统级别的共享内存和跨 GPU 纹理（Cross-GPU Textures）实现进程间通信（IPC），从而避免传统网络传输带来的延迟和开销，确保所有渲染节点能够严格同步地输出画面。

这个模块解决的核心问题是：在 nDisplay 的分布式渲染架构中，如何让不同 PC 上的渲染进程能够快速、可靠地共享渲染结果（GPU 纹理），并实现帧锁定（Framelock）或生成锁（Genlock），以满足视觉上无撕裂、无卡顿的沉浸式体验要求。

## 使用场景

- **虚拟制片（Virtual Production）**：使用多台 PC 驱动大型 LED 墙时，需要所有屏幕像素严格同步更新。
- **多投影仪投影映射（Projection Mapping）**：多个投影仪覆盖一个不规则表面时，需要边缘融合和内容同步。
- **集群渲染（Clustered Rendering）**：需要将一个高分辨率视图分割给多台机器渲染并拼接时。
- **任何需要多 PC 间零延迟、帧锁定视频流传输的场景**。

## 蓝图用法

该模块主要提供配置类，用于定义媒体传输的源和输出。实际的传输逻辑由 C++ 运行时处理。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UniqueName` (属性) | 输入/输出的唯一标识符，发送端和接收端必须匹配才能通信。 | `USharedMemoryMediaSource`, `USharedMemoryMediaOutput` |
| `Mode` (属性) | 接收模式：`Framelocked` (帧锁定，nDisplay标准)、`Genlocked` (生成锁)、`Freerun` (自由运行)。 | `USharedMemoryMediaSource` |
| `bZeroLatency` (属性) | 是否启用零延迟模式，等待同帧渲染的纹理。 | `USharedMemoryMediaSource` |
| `bInvertAlpha` (属性) | 是否反转输出纹理的 Alpha 通道。 | `USharedMemoryMediaOutput` |
| `bCrossGpu` (属性) | 是否启用跨 GPU 共享纹理，对于多 GPU 系统必需。 | `USharedMemoryMediaOutput` |

### 使用示例（蓝图描述）

1.  **发送端（Media Output）**：
    *   在场景中放置一个 `MediaOutputActor` 或任何使用 `MediaCapture` 的组件。
    *   在其属性中，将 `Media Output` 设置为一个 `USharedMemoryMediaOutput` 资产。
    *   配置该资产的 `UniqueName`（例如 “LedWall_Output”），并根据需要设置 `bCrossGpu` 和 `bInvertAlpha`。

2.  **接收端（Media Source）**：
    *   在另一个 PC 的场景中，使用 `MediaPlayer` 组件播放视频。
    *   将 `MediaPlayer` 的 `Media Source` 设置为一个 `USharedMemoryMediaSource` 资产。
    *   配置该资产，将其 `UniqueName` 设置为与发送端相同的名称（“LedWall_Output”），并选择合适的 `Mode`（通常为 `Framelocked`）。

## C++ 用法

### 头文件引入

```cpp
// 核心类型和捕获类
#include "SharedMemoryMediaOutput.h"
#include "SharedMemoryMediaCapture.h"
#include "SharedMemoryMediaSource.h"

// 播放器和样本相关（用于自定义集成）
#include "SharedMemoryMediaPlayer.h"
#include "SharedMemoryMediaSample.h"
```

### 基本用法

基于源码中类的设计，实现一个基本的发送端和接收端连接。

**发送端 (Media Output)**
```cpp
// 创建 SharedMemoryMedia 输出资产
USharedMemoryMediaOutput* MediaOutput = NewObject<USharedMemoryMediaOutput>();
MediaOutput->UniqueName = TEXT("RenderNode_01");
MediaOutput->bCrossGpu = true; // 如果涉及多GPU

// 将 MediaOutput 赋值给场景捕获组件的输出
USceneCaptureComponent2D* CaptureComp = ...;
CaptureComp->TextureTarget = ...; // 一个 RenderTarget
CaptureComp->CaptureSource = ESceneCaptureSource::SCS_FinalColorLDR;

// 创建并启动 MediaCapture
UMediaCapture* MediaCapture = MediaOutput->CreateMediaCapture();
MediaCapture->CaptureTextureRenderTarget2D(CaptureComp->TextureTarget, ...);
```

**接收端 (Media Source & Player)**
```cpp
// 创建 SharedMemoryMedia 源资产
USharedMemoryMediaSource* MediaSource = NewObject<USharedMemoryMediaSource>();
MediaSource->UniqueName = TEXT("RenderNode_01"); // 必须与输出端匹配
MediaSource->Mode = ESharedMemoryMediaSourceMode::Framelocked;
MediaSource->bZeroLatency = true;

// 使用 MediaPlayer 打开源
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->OpenSource(MediaSource);

// 获取 MediaTexture 用于渲染
UMediaTexture* MediaTexture = MediaPlayer->GetVideoTexture();
// 将 MediaTexture 应用到材质或直接作为纹理资源
```

### 进阶用法

理解底层同步机制和模式选择。

```cpp
// 1. 理解模式行为
// ESharedMemoryMediaSourceMode::Framelocked:
//   - 严格匹配发送端和接收端的帧号。
//   - 如果接收端落后，会等待；如果领先，会停滞。确保视觉同步。
//   - 在 nDisplay 环境下**必须使用**此模式。

// ESharedMemoryMediaSourceMode::Genlocked:
//   - 不直接匹配帧号，但保证不跳过任何帧。
//   - 如果发送端快于接收端，发送端会被“拖慢”。

// ESharedMemoryMediaSourceMode::Freerun:
//   - 总是抓取最新的可用帧。
//   - 可能跳过帧。适用于不需要严格同步的场景。

// 2. 零延迟 (bZeroLatency) 的影响
// 当设置为 true 且在 Framelocked 模式下，接收端会等待同帧渲染的纹理，这可能增加少许 GPU 延迟，但能减少感知延迟。
// 如果设置为 false，接收端可能显示比当前渲染帧稍早一帧的内容。

// 3. 直接操作 FSharedMemoryMediaPlayer (高级/调试)
// 通常不直接使用，但可用于性能分析或自定义集成。
// FSharedMemoryMediaPlayer 内部管理共享内存句柄、GPU 栅栏和样本转换。
// 其核心逻辑在 `DetermineNextSourceFrame` 方法中实现，根据不同模式选择下一帧。
```

## Demo 示例

一个最小的 C++ 示例，展示如何配置发送端和接收端。

**SharedMemoryMediaDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class USharedMemoryMediaOutput;
class USharedMemoryMediaSource;
class UMediaCapture;
class UMediaPlayer;
class USceneCaptureComponent2D;
class UMediaTexture;

class FSharedMemoryMediaDemo
{
public:
    /** 初始化发送端（输出） */
    void InitializeSender(USceneCaptureComponent2D* CaptureComponent);

    /** 初始化接收端（源） */
    void InitializeReceiver();

    /** 获取接收端的媒体纹理，用于渲染 */
    UMediaTexture* GetReceiverMediaTexture() const;

    /** 清理资源 */
    void Shutdown();

private:
    UPROPERTY()
    USharedMemoryMediaOutput* SenderOutput = nullptr;

    UPROPERTY()
    UMediaCapture* SenderCapture = nullptr;

    UPROPERTY()
    USharedMemoryMediaSource* ReceiverSource = nullptr;

    UPROPERTY()
    UMediaPlayer* ReceiverPlayer = nullptr;

    UPROPERTY()
    UMediaTexture* ReceiverTexture = nullptr;

    FString UniqueName = TEXT("MyDemoSharedMedia");
};
```

**SharedMemoryMediaDemo.cpp**
```cpp
#include "SharedMemoryMediaDemo.h"
#include "SharedMemoryMediaOutput.h"
#include "SharedMemoryMediaCapture.h"
#include "SharedMemoryMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "Components/SceneCaptureComponent2D.h"

void FSharedMemoryMediaDemo::InitializeSender(USceneCaptureComponent2D* CaptureComponent)
{
    // 创建媒体输出
    SenderOutput = NewObject<USharedMemoryMediaOutput>();
    SenderOutput->UniqueName = UniqueName;
    SenderOutput->bCrossGpu = false; // 单GPU演示可关闭
    SenderOutput->bInvertAlpha = false;

    // 创建并启动捕获
    if (SenderOutput && CaptureComponent && CaptureComponent->TextureTarget)
    {
        SenderCapture = SenderOutput->CreateMediaCapture();
        if (SenderCapture)
        {
            SenderCapture->CaptureTextureRenderTarget2D(CaptureComponent->TextureTarget, FMediaCaptureOptions());
        }
    }
}

void FSharedMemoryMediaDemo::InitializeReceiver()
{
    // 创建媒体源
    ReceiverSource = NewObject<USharedMemoryMediaSource>();
    ReceiverSource->UniqueName = UniqueName;
    ReceiverSource->Mode = ESharedMemoryMediaSourceMode::Framelocked;
    ReceiverSource->bZeroLatency = true;

    // 创建播放器并打开源
    ReceiverPlayer = NewObject<UMediaPlayer>();
    if (ReceiverPlayer->OpenSource(ReceiverSource))
    {
        // 获取用于显示的 MediaTexture
        ReceiverTexture = ReceiverPlayer->GetVideoTexture();
    }
}

UMediaTexture* FSharedMemoryMediaDemo::GetReceiverMediaTexture() const
{
    return ReceiverTexture;
}

void FSharedMemoryMediaDemo::Shutdown()
{
    if (SenderCapture)
    {
        SenderCapture->StopCapture(true);
        SenderCapture = nullptr;
    }
    SenderOutput = nullptr;

    if (ReceiverPlayer)
    {
        ReceiverPlayer->Close();
        ReceiverPlayer = nullptr;
    }
    ReceiverSource = nullptr;
    ReceiverTexture = nullptr;
}
```

## 模块依赖

`SharedMemoryMedia` 模块直接依赖以下非标准模块，用于实现跨 GPU 纹理共享：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | 提供 Direct3D 12 渲染硬件接口，用于创建和管理跨 GPU 共享纹理句柄。这是 Windows 平台跨 GPU 共享的必需依赖。 |

其他依赖（如 `Core`, `Engine`, `MediaUtils` 等）均为常见基础模块，无需特别说明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 增加了 EXR 多层渲染支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 在 MoviePipeline 中合并了 WarpBlendAlpha 模式到 WarpBlend。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知相机的命名问题以及 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码回退时遵循非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

**活跃维护**。

- **创建时间**：2018年，作为 nDisplay 的一部分，已有约 8 年历史，是虚幻引擎中处理复杂多屏渲染的关键基础设施。
- **更新频率**：非常活跃，最近的提交记录（2026年5月）显示持续有功能增强和 bug 修复。这表明它仍在积极开发中，以满足不断发展的虚拟制片和沉浸式体验需求。
- **维护重点**：近期更新集中在提升渲染质量（如 Alpha 通道处理、Gamma 一致性）、增强与 MovieRenderQueue 的集成（多层 EXR）以及修复特定硬件配置下的显示问题。
- **推荐使用**：是的。对于任何需要构建基于 UE5 的 nDisplay 集群渲染系统的项目，`SharedMemoryMedia` 模块是实现高性能帧同步的**标准且受支持**的解决方案。虽然初始版本较早，但其持续的维护和更新保证了其与新引擎版本的兼容性和性能优化。默认启用为 `false` 是合理的，因为它是一个高度专业化的模块，仅在用户明确配置 nDisplay 系统时才需要激活。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay)（nDisplay 整体文档，包含 SharedMemoryMedia 的使用）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)（nDisplay 统一测试模块）