# AJA Media Player

> Implements input and output using AJA Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | AJA媒体源 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体资产模板） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia) | |

## 用途

该插件的核心目的是在 Unreal Engine 中集成 AJA 专业视频采集卡硬件。它提供了一个完整的媒体框架，用于通过 AJA 卡进行高质量的**视频输入（采集）**和**视频输出（播放）**。这使得 UE 项目能够直接与外部视频设备（如摄像机、监视器、视频墙、直播推流设备）进行实时、低延迟的数据交换，是虚拟制作、广播、仿真和直播等专业领域的基石。

## 使用场景

-   **虚拟制作与实时合成**：在 LED 墙（Volume）或绿幕场景中，将 UE 的渲染画面实时输出到监视器，或将摄像机信号实时输入 UE 作为背景或前景图层。
-   **广播级视频输出**：将 UE 中的游戏画面、UI 界面或特效，通过 AJA 卡以专业广播格式（如 SDI）输出到播出设备。
-   **直播推流**：结合直播软件，将 UE 画面作为高质量的视频源进行推流。
-   **视频墙与多屏输出**：驱动由多个显示器或投影仪组成的大型视觉系统。
-   **视频分析与处理**：采集外部视频源，并在 UE 内部进行实时分析或后期处理。

## 蓝图用法

蓝图接口主要提供创建和配置媒体资产的节点，以及对媒体输出的控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Aja Media Source` | 创建一个新的 AJA 媒体源资产，用于配置输入采集。 | `UAjaMediaFactory` |
| `Create Aja Media Output` | 创建一个新的 AJA 媒体输出资产，用于配置输出播放。 | `UAjaMediaFactory` |
| `Create Aja Media Player` | 创建一个媒体播放器实例，用于播放 AJA 媒体源。 | `UAjaMediaFactory` |

### 使用示例（蓝图描述）

1.  **输入采集**：在蓝图中使用 `Create Aja Media Source` 节点创建源资产，在其细节面板中配置 AJA 设备、输入端口和格式。然后，创建一个 `MediaPlayer` 和 `MediaTexture`，将 Media Source 关联到 MediaPlayer，再将 MediaTexture 赋予一个 `Image` 控件，即可在 UI 中显示采集到的视频画面。
2.  **视频输出**：使用 `Create Aja Media Output` 创建输出资产，配置目标 AJA 设备和输出参数。在场景中放置一个 `SceneCaptureComponent2D`，通过其 `Capture Scene` 功能获取渲染结果，最后通过蓝图或 C++ 代码将渲染结果发送给 Media Output，实现画面外输。

## C++ 用法

### 头文件引入

```cpp
#include "AjaMedia.h"
```

### 基本用法

创建并配置一个 AJA 媒体源。
```cpp
// 创建 Media Source
UAjaMediaSource* AjaSource = NewObject<UAjaMediaSource>();
// 配置设备和输入端口 (假设已知设备ID和端口)
AjaSource->DeviceIdentifier = TEXT("AJA Device Name");
AjaSource->PortIdentifier = TEXT("SDI 1");
// 配置视频格式
AjaSource->VideoConfiguration.bAuto = false;
AjaSource->VideoConfiguration.Width = 1920;
AjaSource->VideoConfiguration.Height = 1080;
AjaSource->VideoConfiguration.FrameRate = FFrameRate(24, 1);
```
*(基于 AjaMediaSource 的属性推断)*

### 进阶用法

创建一个媒体播放器并关联源。
```cpp
// 创建 Media Player
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
// 打开源
MediaPlayer->OpenSource(AjaSource);
// 等待 Media Player 就绪，然后关联到 MediaTexture 进行渲染显示
```
*(结合 UMediaPlayer 和 MediaFramework 使用模式)*

## Demo 示例

一个最小化的 C++ 示例，展示如何初始化 AJA 媒体源并打开播放器。
```cpp
// MyAjaMediaActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AjaMediaSource.h"
#include "MediaPlayer.h"
#include "MyAjaMediaActor.generated.h"

UCLASS()
class AMyAjaMediaActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAjaMediaActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UAjaMediaSource* MediaSource;

    UPROPERTY()
    UMediaPlayer* MediaPlayer;
};

// MyAjaMediaActor.cpp
#include "MyAjaMediaActor.h"

AMyAjaMediaActor::AMyAjaMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyAjaMediaActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建媒体源和播放器
    MediaSource = NewObject<UAjaMediaSource>(this);
    MediaPlayer = NewObject<UMediaPlayer>(this);

    // 简单配置（实际使用需根据硬件设置正确参数）
    MediaSource->DeviceIdentifier = TEXT("Default AJA Device");

    // 尝试打开源
    if (MediaSource && MediaPlayer)
    {
        bool bOpened = MediaPlayer->OpenSource(MediaSource);
        if (bOpened)
        {
            UE_LOG(LogTemp, Log, TEXT("AJA Media Source opened successfully."));
        }
    }
}
```

## 模块依赖

要使用此插件的功能，你的模块可能需要依赖以下核心模块：
*(基于典型的媒体插件架构推断，具体依赖需查阅各模块的 Build.cs)*

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 提供媒体框架的核心工具类和接口。 |
| `MediaIOCore` | 提供与硬件采集卡交互的通用核心逻辑，AJA 插件在此基础上构建。 |
| `RenderCore` | 用于处理与渲染相关的资源，如纹理的读写。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为 Blackmagic 和 AJA 卡自动填充媒体配置。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为多种媒体播放器和采集/处理组件添加了额外的引擎分析信息。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作：将多项 VP 资产移至不同的资产分类并进行迁移。 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | [媒体] 为具体的 UMediaSource 和 UMediaOutput 子类添加了缺失的 UAssetDefinition 条目。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了当参数为64位时，32位格式说明符未能相应转换为64位的问题，反之亦然。 |

### 维护评价

**活跃维护**。该插件创建于2018年，历史悠久，但近期（2026年）仍有持续的、功能性更新，主要集中在增强与 MediaIOCore 的集成、改进虚拟制作工作流、修复兼容性问题以及完善资产管理。尽管插件默认未启用，但其作为专业视频硬件支持的关键组件，维护状态良好，是虚拟制作和广播领域项目的**推荐使用**选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia/Tests) *(如果存在)*
- [官方文档](https://docs.unrealengine.com/) *(需在官方文档站内搜索 “AJA” 或 “Media IO”)*