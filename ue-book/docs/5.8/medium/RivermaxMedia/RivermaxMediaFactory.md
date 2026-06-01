# NVIDIA Rivermax Media Streaming

> Adding NVIDIA Rivermax capabilities for Media Captures and Media Players（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Rivermax 媒体流 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxMedia` (Runtime), `RivermaxMediaEditor` (Runtime), `RivermaxMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia) | |

## 用途

本插件将 NVIDIA Rivermax SDK 集成到 Unreal Engine 的 Media Framework 体系中，提供两个核心能力：

- **Rivermax Player**：通过 Rivermax Input Stream 实现 IP 视频播放，可用于接收来自专业 SDI-over-IP 设备、NDI 源或其他 Rivermax 兼容设备的实时视频流
- **Rivermax Capture**：通过 Rivermax Output Stream 实现 IP 视频采集输出，可将引擎画面通过 Rivermax 协议推送到外部显示设备或录制系统

该插件解决的核心问题是：在虚拟制片（Virtual Production）工作流中，需要在 UE 与专业广播级设备之间进行高带宽、低延迟的 IP 视频传输。Rivermax 基于 NVIDIA 网卡的 RDMA（远程直接内存访问）技术，可实现接近线速的无损视频流传输。

## 使用场景

- 你在搭建 LED Volume 虚拟制片棚，需要从 UE 向 LED 墙发送实时渲染画面 → 使用 Rivermax Capture（Output）
- 你需要从专业摄像机或 SDI 网关接收实时视频输入到 UE → 使用 Rivermax Player（Input）
- 你需要在多个节点之间同步传输未压缩的 4K/8K 视频 → Rivermax 的 RDMA 特性比传统 UDP 传输更高效
- 你已在使用 NVIDIA Rivermax 生态系统中的其他设备 → 本插件提供无缝集成

## 蓝图用法

本插件的蓝图接口通过 UE Media Framework 的标准接口暴露，主要体现在 MediaSource 和 MediaOutput 资产的创建与配置。

### 核心资产类型

| 资产类型 | 说明 | 所在模块 |
|---|---|---|
| `URivermaxMediaSource` | 配置 Rivermax 输入流参数（IP 地址、端口、视频格式等） | `RivermaxMedia` |
| `URivermaxMediaOutput` | 配置 Rivermax 输出流参数（目标地址、分辨率、像素格式等） | `RivermaxMedia` |

### 使用示例（蓝图描述）

**播放 IP 视频流：**
1. 在 Content Browser 中右键 → Media → Rivermax Media Source，创建输入源资产
2. 配置源资产的 IP 地址、端口号、视频分辨率等参数
3. 放置一个 Media Player Actor，在其 Media Player 资产中引用该 Rivermax Media Source
4. 调用 `Open Source` 节点开始接收视频流

**输出引擎画面到 IP 流：**
1. 创建 Rivermax Media Output 资产，配置目标地址和输出格式
2. 使用 Media Capture 功能，将 Viewport 或 SceneCapture 的画面推送到该 Output

## C++ 用法

### 头文件引入

```cpp
#include "RivermaxMediaSource.h"
#include "RivermaxMediaOutput.h"
```

### 基本用法

创建和配置 Rivermax Media Source 用于 IP 视频接收：

```cpp
// 创建 Rivermax 媒体源
URivermaxMediaSource* MediaSource = NewObject<URivermaxMediaSource>();
MediaSource->SetStreamAddress(TEXT("239.1.1.1"));  // 组播地址
MediaSource->SetStreamPort(5000);

// 通过标准 Media Framework 接口使用
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->OpenSource(MediaSource);
```

### 进阶用法

使用 Rivermax Media Output 进行视频采集输出：

```cpp
// 创建输出目标
URivermaxMediaOutput* MediaOutput = NewObject<URivermaxMediaOutput>();
MediaOutput->SetStreamAddress(TEXT("239.1.1.2"));
MediaOutput->SetResolution(FIntPoint(1920, 1080));

// 创建 Media Capture 实例并开始输出
UMediaCapture* Capture = NewObject<UMediaCapture>();
Capture->CaptureSceneViewport(MediaOutput);
```

## Demo 示例

```cpp
// RivermaxMediaDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RivermaxMediaSource.h"
#include "RivermaxMediaOutput.h"
#include "MediaPlayer.h"
#include "MediaCapture.h"
#include "RivermaxMediaDemo.generated.h"

UCLASS()
class ARivermaxMediaDemo : public AActor
{
    GENERATED_BODY()

public:
    ARivermaxMediaDemo();

    UPROPERTY(EditAnywhere, Category = "Rivermax")
    FString InputAddress = TEXT("239.1.1.1");

    UPROPERTY(EditAnywhere, Category = "Rivermax")
    int32 InputPort = 5000;

    UPROPERTY(EditAnywhere, Category = "Rivermax")
    FString OutputAddress = TEXT("239.1.1.2");

    UPROPERTY(EditAnywhere, Category = "Rivermax")
    int32 OutputPort = 5001;

    UFUNCTION(BlueprintCallable, Category = "Rivermax")
    void StartReceiving();

    UFUNCTION(BlueprintCallable, Category = "Rivermax")
    void StartCapturing();

private:
    UPROPERTY()
    URivermaxMediaSource* MediaSource = nullptr;

    UPROPERTY()
    URivermaxMediaOutput* MediaOutput = nullptr;

    UPROPERTY()
    UMediaPlayer* MediaPlayer = nullptr;

    UPROPERTY()
    UMediaCapture* MediaCapture = nullptr;
};
```

```cpp
// RivermaxMediaDemo.cpp
#include "RivermaxMediaDemo.h"

ARivermaxMediaDemo::ARivermaxMediaDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ARivermaxMediaDemo::StartReceiving()
{
    if (!MediaSource)
    {
        MediaSource = NewObject<URivermaxMediaSource>(this);
    }
    MediaSource->SetStreamAddress(InputAddress);
    MediaSource->SetStreamPort(InputPort);

    if (!MediaPlayer)
    {
        MediaPlayer = NewObject<UMediaPlayer>(this);
    }
    MediaPlayer->OpenSource(MediaSource);
}

void ARivermaxMediaDemo::StartCapturing()
{
    if (!MediaOutput)
    {
        MediaOutput = NewObject<URivermaxMediaOutput>(this);
    }
    MediaOutput->SetStreamAddress(OutputAddress);
    MediaOutput->SetStreamPort(OutputPort);

    if (!MediaCapture)
    {
        MediaCapture = NewObject<UMediaCapture>(this);
    }
    MediaCapture->CaptureSceneViewport(MediaOutput);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Rivermax` | NVIDIA Rivermax SDK 的 UE 封装层，提供底层流媒体 API |
| `MediaIOCore` | UE Media Framework 核心模块，提供 MediaSource/MediaOutput 基类 |
| `MediaUtils` | 媒体工具函数库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和采集添加引擎分析数据 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整虚拟制片相关资产的分类归属 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 补充 MediaSource/MediaOutput 子类的资产定义注册 |
| 2026-04-28 | `3348026a` | Rivermax: ANC timecode input, input stream base class refactor, and pixel format unification | 新增 ANC 时间码输入、重构输入流基类、统一像素格式 |

### 维护评价

- **创建时间**：2022 年 3 月，约 4 年历史
- **维护状态**：**活跃维护** — 最近一个月内有多次实质性更新，包括功能新增（ANC 时间码）、架构重构和代码质量改进
- **实验性标记**：仍标记为 Beta（`IsBetaVersion: true`），API 可能在未来版本发生变化
- **限制**：需要 NVIDIA Rivermax SDK 和支持 RDMA 的网卡硬件，非通用解决方案
- **推荐程度**：如果你的虚拟制片工作流依赖 NVIDIA Rivermax 生态系统，这是官方推荐的集成方案。注意 Beta 状态意味着可能存在未发现的问题，建议在生产环境中做好备份方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia)
- 官方文档：无
- [NVIDIA Rivermax SDK 文档](https://developer.nvidia.com/networking/rivermax)