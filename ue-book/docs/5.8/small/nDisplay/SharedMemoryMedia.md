# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、着色器、配置资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `SharedMemoryMedia` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMultiUser` (Runtime), `ScalableMPCDI` (External), + 18 more |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

---

## 用途

nDisplay 是 UE5 中用于 **多 PC 同步集群渲染** 的核心系统。它解决的核心问题是：当一台 PC 的 GPU 性能不足以驱动多通道/多屏幕的实时渲染（例如 LED 虚拟摄影棚、穹幕投影、CAVE 系统）时，如何将渲染任务分配到多台 PC 上，并保证所有节点的帧同步、投影校正和画面拼接。

该插件的核心设计目标包括：

1. **帧锁定渲染（Frame-locked）**：确保集群中所有渲染节点在完全相同的时刻输出画面，避免撕裂和延迟
2. **投影变形与融合（Warp & Blend）**：支持 MPCDI 标准的投影网格，处理多投影仪的几何校正和边缘融合
3. **跨 GPU 纹理共享**：通过 SharedMemoryMedia 模块实现进程间和跨 GPU 的像素数据传输，用于 nDisplay 渲染节点间的画面捕获与回放
4. **ICVFX（In-Camera VFX）**：完整的虚拟摄影棚支持，包括灯光卡片（Light Card）、色温校正、视锥体管理等
5. **多用户协作**：支持 nDisplay 集群环境下的多用户同步编辑

**默认未启用**：需要在插件管理器中手动启用，或通过项目配置启用。

---

## 模块架构

nDisplay 由 28+ 个模块组成，可按功能分为以下几组：

| 模块组 | 模块 | 用途 |
|---|---|---|
| **核心** | `DisplayCluster`, `DisplayClusterConfiguration` | 主运行时逻辑、配置系统 |
| **投影与变形** | `DisplayClusterProjection`, `DisplayClusterWarp`, `ScalableMPCDI` | 投影校正、MPCDI 支持 |
| **媒体捕获/回放** | `DisplayClusterMedia`, `SharedMemoryMedia` | 视频流捕获、跨进程纹理共享 |
| **渲染** | `DisplayClusterShaders`, `DisplayClusterColorGrading` | 着色器、色温/色彩校正 |
| **编辑器工具** | `DisplayClusterEditor`, `DisplayClusterConfigurator`, `DisplayClusterOperator`, `DisplayClusterLightCardEditor` | 配置编辑器、操作面板、灯光卡片编辑 |
| **录制** | `DisplayClusterMoviePipeline`, `DisplayClusterMoviePipelineEditor` | Sequencer/影片渲染队列集成 |
| **多用户** | `DisplayClusterMultiUser`, `DisplayClusterReplication` | 多用户同步、状态复制 |
| **监控** | `DisplayClusterMonitor`, `DisplayClusterStageMonitoring` | 节点监控、Stage 监控 |
| **远程控制** | `DisplayClusterRemoteControlInterceptor`, `DisplayClusterMessageInterception` | 远程控制协议拦截 |
| **工具** | `DisplayClusterFillDerivedDataCache`, `DisplayClusterScenePreview`, `DisplayClusterTests` | DDC 填充、场景预览、测试 |

---

## 使用场景

- **LED 虚拟摄影棚**：多台 PC 驱动 LED 墙的不同区域，实现 ICVFX 拍摄 → 使用 `DisplayProjection` + `DisplayClusterWarp`
- **穹幕/CAVE 系统**：多台投影仪拼接投射到弧形屏幕 → 使用 MPCDI 投影网格 + 边缘融合
- **多屏同步输出**：一台 PC 渲染多通道画面，另一台 PC 回放 → 使用 `SharedMemoryMedia`
- **演出控制**：虚拟制作中的灯光、摄像机、画面实时控制 → 使用 `DisplayClusterOperator`
- **影片渲染队列**：将 nDisplay 集群渲染结果录制为 EXR 序列帧 → 使用 `DisplayClusterMoviePipeline`

---

# SharedMemoryMedia 模块

> 基于共享内存的跨进程/GPU 纹理传输模块

| 属性 | 值 |
|---|---|
| 中文名 | 共享内存媒体 |
| 分类 | Runtime |
| 模块 | `SharedMemoryMedia` (Runtime) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/SharedMemoryMedia) | |

## 用途

SharedMemoryMedia 是 nDisplay 的 **跨进程 GPU 纹理共享** 子系统。它基于 UE 的 Media Framework（媒体框架），实现了两个进程之间的像素数据零拷贝传输：

- **发送端（Sender）**：`USharedMemoryMediaCapture` — 将渲染画面写入共享的跨 GPU 纹理
- **接收端（Receiver）**：`FSharedMemoryMediaPlayer` — 从共享纹理中读取画面并作为媒体源播放

核心工作原理：
1. 发送端通过共享系统内存（Shared System Memory）分配 IPC 元数据区域
2. 像素数据存储在跨 GPU 纹理中，通过纹理的 GUID 进行标识和打开
3. 接收端通过 `UniqueName` 找到对应的共享内存区域，获取纹理 GUID 后打开纹理
4. 使用 KeepAlive 心跳机制检测接收端是否存活
5. 使用帧号确认（Ack）机制确保发送端不会覆盖接收端正在读取的纹理

**典型场景**：nDisplay 的渲染节点（Render Node）将渲染结果通过 SharedMemoryMedia 捕获，控制节点（Control Node）的播放器读取并显示。

## 接收模式

| 模式 | 说明 | 适用场景 |
|---|---|---|
| `Framelocked` | 匹配源帧号和本地帧号，严格帧同步 | **nDisplay 集群渲染（推荐）** |
| `Genlocked` | 不匹配帧号，但不跳帧，发送端被接收端节流 | Genlock 硬件同步 |
| `Freerun` | 始终抓取最新帧，可能跳帧 | 非同步场景、调试 |

---

## 蓝图用法

### 核心资产

SharedMemoryMedia 提供三个蓝图可用的类：

#### USharedMemoryMediaOutput（媒体输出）

创建共享内存输出，配置捕获参数。

| 属性 | 类型 | 说明 |
|---|---|---|
| `UniqueName` | `FString` | 共享内存唯一标识名，发送端和接收端必须匹配 |
| `bInvertAlpha` | `bool` | 是否反转 Alpha 通道（默认 true） |
| `bCrossGpu` | `bool` | 是否跨 GPU 共享纹理（默认 true，不需要时关闭可提升性能） |

#### USharedMemoryMediaSource（媒体源）

创建共享内存输入源，配置接收参数。

| 属性 | 类型 | 说明 |
|---|---|---|
| `UniqueName` | `FString` | 共享内存唯一标识名，必须与对应的 Media Output 匹配 |
| `Mode` | `ESharedMemoryMediaSourceMode` | 接收模式（Framelocked / Genlock / Freerun） |
| `bZeroLatency` | `bool` | 零延迟模式，等待同帧渲染的纹理（仅 Framelocked 模式有效） |

#### USharedMemoryMediaCapture（媒体捕获）

由 `USharedMemoryMediaOutput` 自动创建，不直接在蓝图中使用。

### 使用示例（蓝图描述）

**发送端设置**（渲染节点）：

1. 创建一个 `USharedMemoryMediaOutput` 资产
2. 设置 `UniqueName` 为 `"MyClusterOutput"`
3. 在 Media Bundle 或 MediaCapture 组件中引用该 Output
4. 捕获会自动启动，将渲染画面写入共享纹理

**接收端设置**（控制节点）：

1. 创建一个 `USharedMemoryMediaSource` 资产
2. 设置 `UniqueName` 为 `"MyClusterOutput"`（与发送端匹配）
3. 设置 `Mode` 为 `Framelocked`
4. 创建 `MediaPlayer`，使用 `Open Source` 节点打开该 Source
5. 在 `MediaTexture` 中引用播放器，再将其应用到材质/UI

---

## C++ 用法

### 头文件引入

```cpp
#include "SharedMemoryMediaCapture.h"
#include "SharedMemoryMediaOutput.h"
#include "SharedMemoryMediaSource.h"
```

### 基本用法：创建媒体输出并捕获

```cpp
// 创建 SharedMemory Media Output
USharedMemoryMediaOutput* MediaOutput = NewObject<USharedMemoryMediaOutput>();
MediaOutput->UniqueName = TEXT("RenderNode1_Output");
MediaOutput->bInvertAlpha = true;
MediaOutput->bCrossGpu = true;

// 创建 Media Capture 并启动捕获
UMediaCapture* MediaCapture = MediaOutput->CreateMediaCapture();
MediaCapture->CaptureTexture(/* 渲染目标纹理 */, /* 捕获区域 */);
```

### 基本用法：创建媒体源并播放

```cpp
// 创建 SharedMemory Media Source
USharedMemoryMediaSource* MediaSource = NewObject<USharedMemoryMediaSource>();
MediaSource->UniqueName = TEXT("RenderNode1_Output");  // 必须与发送端匹配
MediaSource->Mode = ESharedMemoryMediaSourceMode::Framelocked;
MediaSource->bZeroLatency = true;

// 打开 MediaPlayer
UMediaPlayer* MediaPlayer = /* 获取或创建 */;
MediaPlayer->OpenSource(MediaSource);
```

### 进阶用法：通过 URL 打开

SharedMemoryMedia 使用自定义 URI scheme，可以通过 URL 打开：

```cpp
// URL 格式: sharedmemorymedia://UniqueName
FString Url = TEXT("sharedmemorymedia://RenderNode1_Output");
MediaPlayer->OpenUrl(Url);
```

通过 MediaOptions 传递模式参数：

```cpp
UMediaSource* Source = /* 获取 */;
// 可以通过 IMediaOptions 接口设置参数
// 对应 SharedMemoryMediaOption 命名空间中的 FName:
//   "UniqueName" - 共享内存名称
//   "Mode"       - 接收模式 (0=Framelocked, 1=Genlock, 2=Freerun)
//   "ZeroLatency" - 零延迟开关
```

---

## Demo 示例

### 发送端：捕获渲染画面到共享内存

```cpp
// SharedMemoryMediaSender.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SharedMemoryMediaOutput.h"
#include "SharedMemoryMediaSender.generated.h"

UCLASS()
class ASharedMemoryMediaSender : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "SharedMemory")
    FString UniqueName = TEXT("DemoOutput");

    UPROPERTY(EditAnywhere, Category = "SharedMemory")
    bool bInvertAlpha = true;

    void StartCapture(UTextureRenderTarget2D* RenderTarget);
    void StopCapture();

private:
    UPROPERTY()
    USharedMemoryMediaOutput* MediaOutput = nullptr;

    UPROPERTY()
    UMediaCapture* MediaCapture = nullptr;
};
```

```cpp
// SharedMemoryMediaSender.cpp
#include "SharedMemoryMediaSender.h"
#include "MediaCapture.h"

void ASharedMemoryMediaSender::StartCapture(UTextureRenderTarget2D* RenderTarget)
{
    MediaOutput = NewObject<USharedMemoryMediaOutput>(this);
    MediaOutput->UniqueName = UniqueName;
    MediaOutput->bInvertAlpha = bInvertAlpha;
    MediaOutput->bCrossGpu = true;

    MediaCapture = MediaOutput->CreateMediaCapture();
    if (MediaCapture && RenderTarget)
    {
        MediaCapture->CaptureTexture(
            RenderTarget->GetResource(),
            FIntRect(0, 0, RenderTarget->SizeX, RenderTarget->SizeY),
            FMediaCaptureOptions()
        );
    }
}

void ASharedMemoryMediaSender::StopCapture()
{
    if (MediaCapture)
    {
        MediaCapture->StopCapture(true);
    }
}
```

### 接收端：从共享内存播放画面

```cpp
// SharedMemoryMediaReceiver.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SharedMemoryMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "SharedMemoryMediaReceiver.generated.h"

UCLASS()
class ASharedMemoryMediaReceiver : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "SharedMemory")
    FString UniqueName = TEXT("DemoOutput");

    UPROPERTY(EditAnywhere, Category = "SharedMemory")
    ESharedMemoryMediaSourceMode Mode = ESharedMemoryMediaSourceMode::Framelocked;

    UPROPERTY(EditAnywhere, Category = "SharedMemory")
    bool bZeroLatency = true;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SharedMemory")
    UMediaPlayer* MediaPlayer = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SharedMemory")
    UMediaTexture* MediaTexture = nullptr;

    UFUNCTION(BlueprintCallable, Category = "SharedMemory")
    void StartPlayback();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};
```

```cpp
// SharedMemoryMediaReceiver.cpp
#include "SharedMemoryMediaReceiver.h"

void ASharedMemoryMediaReceiver::BeginPlay()
{
    Super::BeginPlay();

    MediaPlayer = NewObject<UMediaPlayer>(this);
    MediaTexture = NewObject<UMediaTexture>(this);
    MediaTexture->SetMediaPlayer(MediaPlayer);
    MediaTexture->UpdateResource();
}

void ASharedMemoryMediaReceiver::StartPlayback()
{
    USharedMemoryMediaSource* Source = NewObject<USharedMemoryMediaSource>(this);
    Source->UniqueName = UniqueName;
    Source->Mode = Mode;
    Source->bZeroLatency = bZeroLatency;

    MediaPlayer->OpenSource(Source);
}

void ASharedMemoryMediaReceiver::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer && MediaPlayer->IsPlaying())
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

---

## 内部架构

### 跨进程通信协议

SharedMemoryMedia 使用 `FSharedMemoryMediaFrameMetadata` 结构体作为 IPC 元数据，存储在共享系统内存中：

```
┌─────────────────────────────────────────────────┐
│           Shared System Memory (per buffer)      │
├─────────────────────────────────────────────────┤
│  Sender 数据:                                    │
│    - Magic (0x534D4D4D = "SMMM")                │
│    - TextureGuid (跨 GPU 纹理标识)               │
│    - FrameNumber (当前帧号)                      │
├─────────────────────────────────────────────────┤
│  Receiver 数据 (最多 4 个接收端):                 │
│    - FrameNumberAcked (已完成读取的帧号)          │
│    - KeepAliveCounter (心跳计数器)               │
│    - Id (接收端唯一标识)                          │
└─────────────────────────────────────────────────┘
```

### 纹理共享机制

- **Windows/D3D12**：使用 `ID3D12Resource` 创建可跨 GPU 共享的堆纹理，通过 Windows 共享句柄（Shared Handle）跨进程传递
- 纹理通过 `FGuid` 进行标识和匹配
- 支持多种像素格式，由发送端决定，接收端通过元数据获取描述

### 帧同步模式

| 模式 | 策略 | 说明 |
|---|---|---|
| Framelocked | `DetermineNextSourceFrameFramelockMode` | 本地帧号 = 源帧号，严格匹配 |
| Genlock | `DetermineNextSourceFrameGenlockMode` | 不匹配帧号，但连续不跳帧 |
| Freerun | `DetermineNextSourceFrameFreerunMode` | 始终取最新帧，允许跳帧 |

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口，用于跨 GPU 纹理共享（Windows 平台） |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 新增多层 EXR 支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 合并 Alpha 融合模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 摄像机命名和 MPCDI 着色器 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时正确处理非默认 Gamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口时的闪烁问题 |

### 维护评价

**活跃维护** ✅

- 创建于 2018 年（UE 4.20），已持续维护约 8 年
- 最近更新在 2026 年 5 月，更新频率高（每周多次提交）
- 持续进行功能增强（EXR 多层、MoviePipeline 集成）和 Bug 修复
- 作为 Epic 虚拟制作（Virtual Production）核心组件，是 **长期战略级插件**
- 默认未启用是因为需要特定硬件配置（多 PC 集群、LED 墙等），不是质量问题
- **强烈推荐**用于任何虚拟制作/ICVFX 项目

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)