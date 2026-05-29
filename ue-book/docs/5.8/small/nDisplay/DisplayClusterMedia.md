# Display Cluster Media

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群媒体模块 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，配置数据） |
| 模块 | `DisplayClusterMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterMedia) | |

## 用途

`DisplayClusterMedia` 模块是 nDisplay 插件的核心子模块之一，专门负责管理 nDisplay 集群中所有与 **媒体输入、输出及同步** 相关的逻辑。它解决的核心问题是：在由多台 PC 组成的 nDisplay 集群中，如何高效、精确地在各个节点（PC）之间捕获、传输和同步渲染画面。

具体来说，该模块提供了以下关键能力：
1.  **媒体捕获**：将 nDisplay 中单个或多个视口（Viewport）的渲染画面，或者整个后缓冲（Backbuffer）的画面，通过 UE 的 Media Output 框架捕获并输出到外部设备（如采集卡、编码器）。
2.  **媒体输入**：接收来自外部设备（如摄像机、视频流）的媒体源，并将其作为纹理输入到 nDisplay 的视口或虚拟制片（ICVFX）相机中，实现外部视频合成。
3.  **帧同步**：通过可配置的同步策略（如 Ethernet Barrier 或 V-blank），确保集群中所有节点的媒体输出在精确的时间点对齐，避免画面撕裂或延迟不一致。
4.  **延迟队列**：实现可控的渲染延迟，用于补偿网络传输或实现特定的视觉效果。
5.  **OCIO 支持**：在媒体输入/输出路径上集成 OpenColorIO 颜色管理。

该模块的存在使得 nDisplay 能够无缝接入影视级虚拟制片（VP）、大型 LED 墙、多投影仪融合等专业工作流，这些场景对画面同步性和媒体集成有着极高要求。

## 使用场景

-   **虚拟制片（In-Camera VFX）**：将 Unreal Engine 的实时渲染画面作为背景，通过采集卡输出到 LED 墙或给后期使用。同时，可以将真实摄像机的视频流输入回引擎，用于实时合成。
-   **大型 LED 墙系统**：由多台 PC 分别驱动 LED 墙的不同区域（Tile），该模块负责将每台 PC 捕获的对应区域画面准确输出，并保持全局同步。
-   **多通道投影融合**：类似 LED 墙，但输出端是投影仪。模块捕获每个视口画面并输出到对应的投影仪，同步策略确保融合区无撕裂。
-   **实时视频合成与监看**：在集群渲染的同时，将特定视口或相机的画面通过 SDI、NDI 等协议输出给现场监视器或导播系统。
-   **电影渲染队列集成**：与 `DisplayClusterMoviePipeline` 模块配合，在离线渲染时精确捕获和同步多机位画面。

## 蓝图用法

该模块的蓝图接口主要集中在**同步策略**的配置上。这些策略是 `UObject`，可以在 nDisplay 配置资产或通过蓝图动态创建和分配。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Barrier Timeout` | 设置以太网屏障（Ethernet Barrier）同步策略的等待超时时间（毫秒）。 | `UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrierBase` |
| `Set Margin` | 设置基于阈值（Threshold）同步策略（如 V-blank）的时间裕量（毫秒）。 | `UDisplayClusterMediaOutputSynchronizationPolicyThresholdBase` |
| `Get Handler` | 获取同步策略对应的具体处理程序实例。 | `UDisplayClusterMediaOutputSynchronizationPolicy` |
| `Create Ethernet Barrier Policy` | 创建一个基于以太网屏障的同步策略实例。 | `UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier` |
| `Create V-blank Policy` | 创建一个基于垂直同步（V-blank）的同步策略实例。 | `UDisplayClusterMediaOutputSynchronizationPolicyVblank` |

### 使用示例（蓝图描述）

假设你需要为 nDisplay 集群配置一个使用以太网同步、超时为 5 秒的媒体输出策略：

1.  在 nDisplay 根 Actor 的配置中，找到 `Media` 相关部分。
2.  为 `MediaOutputSyncPolicy` 属性创建一个新的 `UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier` 对象。
3.  在该策略对象的细节面板中，将 `BarrierTimeoutMs` 设置为 `5000`。
4.  这个策略对象将被 nDisplay 系统自动用于同步所有关联的媒体输出设备。

## C++ 用法

### 头文件引入

使用该模块的核心功能，通常需要引入以下头文件：
```cpp
// 媒体模块入口
#include "DisplayClusterMediaModule.h"

// 同步策略基类与具体实现
#include "DisplayClusterMediaOutputSynchronizationPolicy.h"
#include "DisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier.h"
#include "DisplayClusterMediaOutputSynchronizationPolicyVblank.h"

// 媒体输入/输出基类（用于理解架构）
#include "DisplayClusterMediaCaptureBase.h"
#include "DisplayClusterMediaInputBase.h"
```

### 基本用法

从架构看，开发者通常不直接实例化 `FDisplayClusterMediaCaptureViewportFull` 等类，而是通过 **nDisplay 配置系统** 或 **模块内部逻辑** 来驱动它们。配置示例（代码风格）：
```cpp
// 通常通过 UDisplayClusterConfigurationViewport 或 UDisplayClusterConfigurationClusterNode 配置媒体
// 以下为概念性代码，展示配置如何映射到内部对象
UDisplayClusterConfigurationViewport* ViewportConfig = GetMyViewportConfig();

// 设置该视口的媒体输出源为 “MediaOutput_1”，这是一个 UMediaOutput 资产
ViewportConfig->MediaOutput.MediaOutputId = TEXT("MediaOutput_1");

// 设置该视口的媒体输出同步策略为一个以太网屏障策略
ViewportConfig->MediaOutput.SyncPolicy = NewObject<UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier>(ViewportConfig);
Cast<UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier>(ViewportConfig->MediaOutput.SyncPolicy)->BarrierTimeoutMs = 3000;

// nDisplay 的 DisplayClusterMediaModule 会在初始化时根据这些配置，创建相应的
// FDisplayClusterMediaCaptureViewportFull 和 FDisplayClusterMediaOutputSynchronizationPolicyHandler
```

### 进阶用法

**动态更改同步策略**：
```cpp
#include "DisplayClusterMediaModule.h"

// 获取媒体模块实例
FDisplayClusterMediaModule* MediaModule = FModuleManager::GetModulePtr<FDisplayClusterMediaModule>(TEXT("DisplayClusterMedia"));
if (MediaModule)
{
    // 假设我们知道某个媒体输出设备的ID
    const FString MediaOutputDeviceId = TEXT("ViewportOut_MyViewport");

    // 创建一个新的V-blank策略，设置2ms的裕量
    UDisplayClusterMediaOutputSynchronizationPolicyVblank* NewVblankPolicy = NewObject<UDisplayClusterMediaOutputSynchronizationPolicyVblank>();
    NewVblankPolicy->MarginMs = 2;

    // 通过模块接口更新特定设备的同步策略（具体API需查阅模块公开接口）
    // MediaModule->UpdateMediaOutputSyncPolicy(MediaOutputDeviceId, NewVblankPolicy);
}
```

**理解延迟队列**：
延迟队列 (`FDisplayClusterFrameQueue`) 用于在渲染管线中插入可控延迟。它缓存每一帧所有视口的纹理和着色器参数。当 `nDisplay` 的 `FrameLatency` 属性被设置时，该队列生效。
```cpp
// 队列内部逻辑（简化）
void FDisplayClusterFrameQueue::HandleEndDraw()
{
    // 当前帧数据进入队列头部
    FDisplayClusterFrameQueueItem& HeadItem = Frames[IdxHead];
    // ... 保存当前所有视口的纹理和数据到 HeadItem

    // 队列尾部的数据被用于最终输出
    const FDisplayClusterFrameQueueItem& TailItem = Frames[IdxTail];
    // ... 从 TailItem 加载数据用于合成输出

    // 移动队列索引
    StepQueueIndices_RenderThread();
}
```

## Demo 示例

以下是一个最小示例，展示如何创建一个使用以太网同步策略的媒体输出设备，并将其绑定到一个视口配置上。**注意**：实际使用中，这些配置通常通过 nDisplay 的配置资产完成，此代码仅为演示底层对象关系。

**MediaDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MediaDemo.generated.h"

class UMediaOutput;
class UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier;

UCLASS(ClassGroup=(nDisplay), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMediaDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMediaDemoComponent();

    virtual void BeginPlay() override;

    // 在蓝图中可设置的媒体输出资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "nDisplay Media Demo")
    TObjectPtr<UMediaOutput> DemoMediaOutput;

    // 创建并应用同步策略
    UFUNCTION(BlueprintCallable, Category = "nDisplay Media Demo")
    void ApplyEthernetSyncPolicy(int32 TimeoutMs = 3000);

private:
    // 内部使用的同步策略实例
    UPROPERTY()
    TObjectPtr<UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier> SyncPolicy;
};
```

**MediaDemo.cpp**
```cpp
#include "MediaDemo.h"
#include "DisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier.h"
#include "MediaOutput.h"

UMediaDemoComponent::UMediaDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMediaDemoComponent::BeginPlay()
{
    Super::BeginPlay();
    if (!SyncPolicy)
    {
        ApplyEthernetSyncPolicy();
    }
}

void UMediaDemoComponent::ApplyEthernetSyncPolicy(int32 TimeoutMs)
{
    if (!DemoMediaOutput)
    {
        UE_LOG(LogTemp, Warning, TEXT("MediaDemoComponent: DemoMediaOutput is not set."));
        return;
    }

    // 创建一个以太网屏障同步策略
    SyncPolicy = NewObject<UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier>(this);
    SyncPolicy->BarrierTimeoutMs = TimeoutMs;

    UE_LOG(LogTemp, Log, TEXT("MediaDemoComponent: Created Ethernet Barrier Sync Policy with Timeout: %d ms."), TimeoutMs);

    // 在实际的 nDisplay 系统中，你需要将这个 SyncPolicy 和 MediaOutput
    // 通过配置关联到一个具体的 nDisplay 视口。
    // 例如，你可以将其保存到某个 UDisplayClusterConfigurationViewport 资产中。
    // 此处仅为演示对象的创建。
}
```

## 模块依赖

从 `DisplayClusterMedia.Build.cs` 分析，该模块有以下关键依赖：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | 提供 DirectX 12 底层渲染硬件接口支持。媒体捕获和输入操作，特别是跨 GPU 传输和纹理操作，深度依赖于图形 API。 |
| `UnrealEd` | 提供编辑器相关功能。虽然标记为 Runtime，但模块内可能包含用于在编辑器中配置和预览 nDisplay 媒体设置的工具代码。 |

**注意**：该模块是 `nDisplay` 插件的一部分，因此也隐式依赖于 `DisplayCluster` 核心模块以及 `MediaFrameworkUtilities`、`MediaUtils` 等 UE 标准媒体模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影渲染图（MovieGraph）的 nDisplay 输出添加了 EXR 多图层支持。 |
| 2025-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将电影管线中的 WarpBlendAlpha 模式合并到 WarpBlend 功能中，简化了配置。 |
| 2025-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了在媒体渲染图（MRG）中拓扑感知相机命名问题，以及 MPCDI/ICVFX 着色器中不透明度（Alpha）的问题。 |
| 2025-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在输出帧编码回退路径中，未能正确遵循非默认 DisplayGamma 设置的问题。 |
| 2025-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时导致的画面闪烁问题。 |

### 维护评价

`DisplayClusterMedia` 模块作为 nDisplay 的核心媒体管线，**维护状态非常活跃**。
1.  **创建时间**：模块起源于 2018 年的 UE 4.20 企业版，历经多年发展。
2.  **近期更新**：从 git 历史看，2025 年内有多次实质性功能更新和关键 Bug 修复（如 EXR 多图层、着色器修复、Gamma 处理等），表明 Epic 对其在虚拟制片和电影渲染领域的持续投入。
3.  **功能复杂度**：模块包含 29 个头文件，涉及捕获、输入、同步、延迟、颜色管理等多个子系统，是 nDisplay 中较为复杂的模块之一。
4.  **平台支持**：明确支持 Win64 和 Linux，这是专业制作环境的基本要求。
5.  **推荐度**：**强烈推荐使用**。对于任何需要在多机 nDisplay 集群中进行专业媒体集成和同步输出的项目（尤其是虚拟制片），该模块是必不可少的。虽然功能复杂，但作为官方支持的核心组件，其稳定性和兼容性有保障。对于初学者，建议先理解 nDisplay 的基本配置，再深入该模块的高级功能。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterMedia)
-   官方文档: 通常包含在 [nDisplay 官方文档](https://docs.unrealengine.com/en-US/Engine/Rendering/nDisplay/index.html) 的媒体与同步章节中。
-   测试用例: 测试代码通常位于 `Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/` 目录下，具体媒体相关测试需在该目录内查找。