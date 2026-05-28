# AJA Media Player

> Implements input and output using AJA Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | AJA 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体工厂资产、编辑器资产） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia) | |

## 用途

该插件将 AJA 公司的专业视频采集卡（如 Corvid、Kona 系列）集成到 UE5 的 Media Framework 中。AJA 是广播级和虚拟制片领域的主流硬件厂商，提供 SDI/HDMI 信号的输入输出能力。

该插件解决的核心问题：
- **视频输入**：从 AJA 采集卡实时捕获外部视频信号（如摄影机 SDI 输出、外部播放器），用于虚拟制片中的实时合成、色键抠像等场景
- **视频输出**：将 UE5 渲染画面通过 AJA 采集卡以 SDI/HDMI 信号发送到外部设备（如 LED 墙控制器、广播切换台、监视器），是虚拟制片中 nDisplay/LED Volume 工作流的关键环节
- **时间码同步**：通过 AJA 硬件提供专业级 LTC 时间码支持，确保视频信号与引擎时间同步

该插件默认未启用（`EnabledByDefault: false`），仅支持 Win64 平台，因为 AJA 官方 SDK 仅提供 Windows 驱动。使用前需安装 AJA 驱动和 NTV2 SDK。

## 使用场景

- 你在搭建虚拟制片 LED Volume → 使用 AJA 卡将引擎渲染内容实时输出到 LED 墙
- 你需要将摄影机 SDI 信号引入 UE5 进行实时合成 → 使用 AJA 输入捕获
- 你在做广播级实时图形输出 → 将 UE 画面通过 AJA SDI 输出到导播台
- 你需要多路 AJA 信号的同步输入输出 → 该插件支持多通道配置
- 你要录制来自 AJA 采集卡的视频素材 → 结合 Media Framework 的录制功能

## 蓝图用法

该插件主要通过 UE5 的 Media Framework 体系工作，其核心资产类型（MediaSource、MediaOutput）均可在蓝图中使用。

### 核心资产类型

| 资产类型 | 说明 | 创建位置 |
|---|---|---|
| `UAjaMediaSource` | 配置 AJA 视频输入源（通道、格式、帧率等） | Content Browser → Media → AJA Media Source |
| `UAjaMediaOutput` | 配置 AJA 视频输出目标（通道、格式、分辨率等） | Content Browser → Media → AJA Media Output |

### 典型蓝图工作流（输入）

1. 创建 **AJA Media Source** 资产，配置输入通道和视频格式
2. 创建 **Media Player** 资产，选择支持的格式
3. 在蓝图中使用 `Open Source` 节点打开 AJA 输入
4. 通过 **Media Texture** 获取输入画面，应用到材质或 UI

### 典型蓝图工作流（输出）

1. 创建 **AJA Media Output** 资产，配置输出通道和视频格式
2. 在蓝图中使用 `Capture Scene / Capture Texture` 将渲染内容输出到 AJA 卡
3. 可结合 nDisplay 实现多路输出

## C++ 用法

### 头文件引入

```cpp
#include "AjaMediaSource.h"
#include "AjaMediaOutput.h"
```

### 基本用法 — 编程创建 AJA 媒体源

```cpp
// 创建 AJA 媒体源对象并配置输入参数
// 来源: 基于 Media Framework 标准用法
UAjaMediaSource* MediaSource = NewObject<UAjaMediaSource>();
MediaSource->MediaConnection.Device.DeviceName = TEXT("Corvid88 0");
MediaSource->MediaConnection.Channel = EMediaIOChannelType::Channel1;
MediaSource->MediaConnection.VideoModeConfiguration.VideoMode = EMediaIOVideoMode::HD_1080p_2997;
```

### 基本用法 — 编程创建 AJA 媒体输出

```cpp
// 创建 AJA 媒体输出对象并配置输出参数
UAjaMediaOutput* MediaOutput = NewObject<UAjaMediaOutput>();
MediaOutput->MediaConnection.Device.DeviceName = TEXT("Corvid88 0");
MediaOutput->MediaConnection.Channel = EMediaIOChannelType::Channel1;
MediaOutput->MediaConnection.VideoModeConfiguration.VideoMode = EMediaIOVideoMode::HD_1080p_2997;
```

### 进阶用法 — 结合 MediaPlayer 完整播放

```cpp
// 完整的 AJA 输入捕获流程
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);

UAjaMediaSource* MediaSource = NewObject<UAjaMediaSource>();
MediaSource->MediaConnection.Device.DeviceName = TEXT("Corvid88 0");

// 打开媒体源开始捕获
MediaPlayer->OpenSource(MediaSource);

// MediaTexture 可用于材质或渲染目标
```

## Demo 示例

```cpp
// AjaMediaDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AjaMediaDemo.generated.h"

class UMediaPlayer;
class UMediaTexture;
class UAjaMediaSource;
class UStaticMeshComponent;

UCLASS()
class AAjaMediaDemo : public AActor
{
    GENERATED_BODY()

public:
    AAjaMediaDemo();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 开始 AJA 视频输入捕获 */
    UFUNCTION(BlueprintCallable, Category = "AJA Demo")
    void StartCapture();

    /** 停止捕获 */
    UFUNCTION(BlueprintCallable, Category = "AJA Demo")
    void StopCapture();

private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* DisplayMesh;

    UPROPERTY()
    UMediaPlayer* MediaPlayer;

    UPROPERTY()
    UMediaTexture* MediaTexture;

    UPROPERTY()
    UAjaMediaSource* MediaSource;
};
```

```cpp
// AjaMediaDemo.cpp
#include "AjaMediaDemo.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
#include "AjaMediaSource.h"
#include "Components/StaticMeshComponent.h"

AAjaMediaDemo::AAjaMediaDemo()
{
    PrimaryActorTick.bCanEverTick = false;

    DisplayMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DisplayMesh"));
    RootComponent = DisplayMesh;
}

void AAjaMediaDemo::BeginPlay()
{
    Super::BeginPlay();

    MediaSource = NewObject<UAjaMediaSource>(this, TEXT("AjaInput"));
    MediaPlayer = NewObject<UMediaPlayer>(this, TEXT("AjaPlayer"));
    MediaTexture = NewObject<UMediaTexture>(this, TEXT("AjaTexture"));

    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void AAjaMediaDemo::StartCapture()
{
    if (MediaSource && MediaPlayer)
    {
        // 配置 AJA 设备（实际设备名需根据硬件调整）
        MediaSource->MediaConnection.Device.DeviceName = TEXT("Corvid88 0");
        MediaPlayer->OpenSource(MediaSource);
    }
}

void AAjaMediaDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopCapture();
    Super::EndPlay(EndPlayReason);
}

void AAjaMediaDemo::StopCapture()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 媒体 I/O 核心框架，提供通用的设备连接和视频模式抽象 |
| `MediaAssets` | 媒体资产类型（MediaPlayer、MediaTexture、MediaSource 等） |
| `MediaUtils` | 媒体工具函数 |
| `TimeManagement` | 时间码管理和同步支持 |
| `RenderCore` | 渲染核心，用于输出帧缓冲到 AJA 硬件 |
| `RHI` | 渲染硬件接口，用于 GPU 帧数据读回 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | AJA 和 Blackmagic 自动模式下填充媒体配置 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 媒体播放器和采集增加引擎分析信息 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类调整和迁移 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 补充 MediaSource 和 MediaOutput 子类的资产定义注册 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

- **创建时间**：2018 年 5 月，已存在约 8 年
- **最近更新**：2026 年 5 月仍有活跃更新，最近一次更新距文档编写时不到 2 周
- **维护状态**：**活跃维护** — 持续有功能增强和 bug 修复，与 MediaIOCore、Blackmagic 等模块同步迭代
- **虚拟制片核心**：作为 UE5 虚拟制片工具链的核心组件之一，AJA 插件受到 Epic 的持续关注
- **限制**：仅支持 Win64 平台；需要安装 AJA 驱动和 SDK；默认未启用需手动开启
- **推荐度**：如果使用 AJA 硬件，强烈推荐使用，这是 Epic 官方维护的集成方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia)
- [AJA 官方网站](https://www.aja.com/)
- [UE5 Media Framework 文档](https://docs.unrealengine.com/5.8/en-US/media-framework-in-unreal-engine/)