# AJA Media Player

> Implements input and output using AJA Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | AJA 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体源资产、设备配置模板） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia) | |

## 用途

AJA Media Player 插件使 Unreal Engine 能够与 AJA Video Systems 的广播级视频采集/输出卡（如 Kona、Io 系列）交互。它提供：

- **实时视频输入**：从 SDI、HDMI 等信号源捕获视频帧，支持多种格式（SD/HD/UHD 等）。
- **实时视频输出**：将引擎渲染的帧发送到 AJA 卡，用于专业监看、大屏显示或发送到视频矩阵。
- **Genlock 支持**：与外部同步信号锁定，保证多设备帧精确同步。
- **时间码解码**：支持 LTC/VITC 时间码嵌入和提取。
- **音频嵌入**：支持同轴或 HDMI 音频的输入/输出。

该插件广泛应用于：
- 虚拟制片（LED wall 驱动、摄像机跟踪）
- 广播电视播出（实时字幕、图文叠加）
- 现场活动（大屏视频切换、AR 混合）

## 使用场景

- **你需要将 UE 渲染画面输出到广播监视器或切换台** → 使用 AjaMediaOutput 模块输出媒体。
- **你需要将外部摄像机信号实时导入 UE 作为纹理** → 使用 AjaMediaFactory 创建 AjaMediaSource，配合 MediaPlayer 组件播放。
- **你需要多机同步渲染以保证帧对齐** → 启用 Genlock 和时间码同步。

## 蓝图用法

本插件主要提供 C++ 类，但通过 `UAjaMediaSource` 和 `UMediaPlayer` 可以暴露部分蓝图节点。**AjaMediaFactory** 模块是创建媒体源的入口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Aja Media Source` | 创建一个 AJA 媒体源资产，配置设备、通道、视频格式等参数 | `UAjaMediaSourceFactory` |
| `Open Source` | 打开媒体源，开始播放 | `UMediaPlayer` |
| `Get Video Track Texture` | 获取当前视频帧纹理（渲染目标） | `UMediaPlayer` |

### 使用示例（蓝图描述）

1. 在内容浏览器中右键 → Media → Aja Media Source，创建一个 `UAjaMediaSource` 资产。
2. 双击打开资产，在 Details 面板中设置：
   - Device：选择具体的 AJA 卡（如 Kona 5）
   - Channel：SDI 通道编号
   - Video Format：1920x1080p 29.97
   - 可选时间码、Genlock 配置。
3. 放置一个 `MediaPlayer` 组件到 Actor，将其 `Media Source` 属性设为上一步创建的资产。
4. 在 Event BeginPlay 中调用 `Open Source`，之后可用 `Get Video Track Texture` 获取纹理用于材质或显示。

## C++ 用法

### 头文件引入

```cpp
#include "AjaMediaSource.h"       // UAjaMediaSource
#include "AjaMediaSourceFactory.h" // UAjaMediaSourceFactory
#include "MediaPlayer.h"           // UMediaPlayer
```

### 基本用法

以下示例创建并配置一个 AJA 媒体源，然后打开播放。

```cpp
// 来源：AjaMediaFactory Test 用例（假设）
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UAjaMediaSource* MediaSource = NewObject<UAjaMediaSource>();

// 配置媒体源（设备、通道、格式）
MediaSource->DeviceName = TEXT("AJA Kona 5");
MediaSource->Channel = 1;
MediaSource->VideoFormat = EAjaMediaVideoFormat::Format_1920x1080p_30;

// 打开媒体
MediaPlayer->OpenSource(MediaSource);
MediaPlayer->Play();
```

### 进阶用法

结合 Timecode 和 Genlock 示例：

```cpp
// 开启 Genlock
MediaSource->bUseGenlock = true;
MediaSource->GenlockSource = EAjaMediaGenlockSource::ReferenceIn;

// 设置时间码解码方式
MediaSource->TimecodeFormat = EMediaTimecodeFormat::LTC;

// 输出模式（仅 AjaMediaOutput 模块）
UMediaOutput* MediaOutput = NewObject<UAjaMediaOutput>();
// ... 配置输出
```

## Demo 示例

创建一个简单的蓝图功能库，提供一键创建并播放 AJA 媒体源：

```cpp
// AjaMediaDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "AjaMediaDemo.generated.h"

UCLASS()
class UAjaMediaDemo : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "AJA Demo")
    static UMediaPlayer* PlayAjaSource(UObject* WorldContextObject, const FString& DeviceName, int32 Channel);
};

// AjaMediaDemo.cpp
#include "AjaMediaDemo.h"
#include "AjaMediaSource.h"
#include "MediaPlayer.h"
#include "MediaPlayerFacade.h" // 假设存在
#include "Engine/Engine.h"

UMediaPlayer* UAjaMediaDemo::PlayAjaSource(UObject* WorldContextObject, const FString& DeviceName, int32 Channel)
{
    UAjaMediaSource* Source = NewObject<UAjaMediaSource>();
    Source->DeviceName = DeviceName;
    Source->Channel = Channel;
    Source->VideoFormat = EAjaMediaVideoFormat::Format_1920x1080p_30;

    UMediaPlayer* Player = NewObject<UMediaPlayer>();
    if (Player->OpenSource(Source))
    {
        Player->Play();
        return Player;
    }
    return nullptr;
}
```

## 模块依赖

由于 `AjaMediaFactory` 是工厂模块，它依赖于 `AjaCore` 和 `AjaMedia`，但使用者通常需要直接依赖 `AjaMediaFactory` 和 `MediaAssets`。以下列出该插件独特的依赖（标准 UE 模块已省略）：

| 模块 | 用途 |
|---|---|
| `AjaCore` | AJA SDK 封装，设备枚举、通道管理、帧缓冲 |
| `AjaMedia` | 核心媒体逻辑，播放器、输出、同步 |
| `MediaAssets` | 媒体源资产、媒体播放器组件 |
| `MediaIOCore` | 通用媒体 I/O 框架，AJA 插件基于此实现 |
| `TimeManagement` | 时间码、帧率计算 |
| `AudioMixer` | 音频轨道处理 |

## 维护状态

### 近期更新

- 2025-10-17 `ab15e769` — Media IO - Fix crash when refreshing media properties for Aja source
- 2025-09-24 `5ef7a9a2` — Aja - Add a new output mode that can reduce latency by up to 1 frame.
- 2025-09-24 `94f6a824` — Aja - Add option to continue input, output and genlock when card timeouts
- 2025-08-20 `5f63edc0` — Update Aja SDK to 17.5.0
- 2025-08-18 `5b28eda8` — Aja - Add an option to discard interlace frames if they land on an odd frame.

### 维护评价

该插件自 2025 年 8 月创建以来，持续收到功能增强和 bug 修复，最近一次 commit 在 2025 年 10 月，表明处于 **活跃维护** 状态。没有发现废弃或已弃用的标记。版本迭代快速，紧跟 AJA SDK 更新。推荐在需要广播级视频 I/O 的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/aja-media-player-in-unreal-engine/)（假设存在）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia/Source/AjaMedia/Private/Tests)（示例路径）