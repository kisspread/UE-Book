# Electra Player

> Cross platform media player for local files and internet streaming.
> Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 电子播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源、配置资产） |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

ElectraPlayer 是 Unreal Engine 5 内置的、高性能的跨平台媒体播放器插件。其核心目的是解决游戏和应用程序中播放本地媒体文件（如 MP4）以及进行实时网络流媒体播放（如 DASH、HLS 协议）的需求。

与旧有的媒体播放器框架相比，ElectraPlayer 提供了更强大、更现代的功能：
1.  **跨平台支持**：为 PC、主机等主流平台提供统一的播放体验。
2.  **流媒体支持**：原生支持 DASH 和 HLS 这两种主流的自适应比特率流媒体协议，能够根据网络状况动态调整视频质量。
3.  **优化播放器 (Protron)**：针对桌面平台，提供了一个名为“Protron”的优化播放器，专注于高效播放本地 MP4 文件，性能更优。
4.  **模块化架构**：插件由多个模块组成，职责分离清晰，便于维护和扩展。

## 使用场景

-   你需要在游戏内播放过场动画、背景视频或教学视频（本地或网络 URL）。
-   你的应用需要接入一个实时视频流服务（例如体育直播、新闻直播）。
-   你正在开发一个媒体中心或视频点播应用，需要支持自适应码率切换。
-   在桌面平台上快速、高效地播放本地 MP4 文件，对 CPU/GPU 负载有要求。

## 蓝图用法

ElectraPlayer 作为 UE 标准媒体框架的一个实现，其核心蓝图节点与通用的 `Media Player` 资产使用方法一致。创建和使用播放器的流程如下：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Media Player` | 创建一个新的 Electra 媒体播放器实例。这是获取播放器的主要蓝图节点。 | `UMediaPlayer` |
| `Open URL` | 通过播放器实例打开一个本地文件路径或网络 URL 地址。 | `UMediaPlayer` |
| `Play` | 开始播放已打开的媒体。 | `UMediaPlayer` |
| `Pause` | 暂停当前播放。 | `UMediaPlayer` |
| `Close` | 关闭当前媒体并释放相关资源。 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1.  **创建播放器**：在蓝图中，使用 `Create Media Player` 节点，指定 `Media Source`（如 `File Media Source` 或 `Stream Media Source`）来创建一个 Electra 播放器。这个节点返回一个 `UMediaPlayer` 对象。
2.  **打开媒体**：将 `UMediaPlayer` 对象的 `Open URL` 节点，连接一个 `Make Literal String` 节点，输入媒体文件的本地路径（如 `D:/video.mp4`）或网络地址。
3.  **连接输出**：将 `UMediaPlayer` 对象的 `Video Texture` 输出（一个 `UTexture2D`）连接到 `Image` 控件或 `Media Texture`，以显示视频画面。
4.  **控制播放**：通过 `UMediaPlayer` 对象的 `Play`, `Pause`, `Stop` 等节点来控制播放状态。
5.  **事件处理**：监听 `On Media Opened`, `On Media Closed`, `On Playback Resumed` 等委托来响应播放状态变化。

## C++ 用法

在 C++ 中，ElectraPlayer 通过标准的 `IMediaPlayer` 接口进行集成。

### 头文件引入

```cpp
// 需要包含媒体模块和 Electra 插件模块接口
#include "MediaPlayer.h"
#include "IElectraPlayerPluginModule.h"
```

### 基本用法

以下代码展示了如何通过 C++ 创建和操作 Electra 播放器（来源：基于 `IElectraPlayerPluginModule` 接口分析）。

```cpp
// 获取 ElectraPlayerPlugin 模块
IElectraPlayerPluginModule* ElectraModule = FModuleManager::GetModulePtr<IElectraPlayerPluginModule>(TEXT("ElectraPlayerPlugin"));

if (ElectraModule && ElectraModule->IsInitialized())
{
    // 创建媒体事件接收器（通常由媒体框架内部管理）
    // IMediaEventSink* EventSink = ...;
    
    // 通过模块接口创建播放器实例
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = ElectraModule->CreatePlayer(*EventSink);
    
    if (Player.IsValid())
    {
        // 打开一个媒体源
        FMediaSourceCacheSettings CacheSettings; // 可选配置
        Player->OpenUrl(TEXT("http://example.com/stream.mpd"), &CacheSettings);
        
        // 控制播放
        Player->Play();
        
        // 获取渲染目标（Texture），用于绑定到 UMG 或其他渲染器
        // FTextureResource* TextureResource = Player->GetVideoTexture(); // 伪代码，具体接口需参考最新API
    }
}
```

### 进阶用法

对于流媒体，你可以利用 `UStreamMediaSource` 来提供 DASH 或 HLS 播放列表地址。

```cpp
// 创建流媒体源
UStreamMediaSource* StreamSource = NewObject<UStreamMediaSource>();
StreamSource->StreamUrl = TEXT("https://cdn.example.com/live/stream.m3u8");

// 在 MediaPlayer 资产或蓝图节点中使用此 Source，或通过 OpenSource 方法
// Player->OpenSource(StreamSource);
```

## Demo 示例

一个最小化的 C++ 示例，演示如何使用 Electra 插件模块播放本地视频。

### MyVideoPlayer.h
```cpp
// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyVideoPlayer.generated.h"

class IElectraPlayerPluginModule;
class IMediaPlayer;
class IMediaEventSink;
class UTexture2D;

UCLASS()
class MYPROJECT_API AMyVideoPlayer : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyVideoPlayer();

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:	
	virtual void Tick(float DeltaTime) override;

private:
	/** Electra播放器模块接口 */
	IElectraPlayerPluginModule* ElectraModule = nullptr;

	/** 媒体播放器实例 */
	TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> MediaPlayer;

	/** 媒体事件接收器 */
	TSharedPtr<IMediaEventSink, ESPMode::ThreadSafe> MediaEventSink;

	/** 视频纹理输出 */
	UPROPERTY(Transient)
	UTexture2D* VideoTexture = nullptr;

	/** 要播放的视频文件路径 */
	UPROPERTY(EditAnywhere, Category = "Video")
	FString VideoFilePath = TEXT("D:/MyVideo.mp4");
};
```

### MyVideoPlayer.cpp
```cpp
// Fill out your copyright notice in the Description page of Project Settings.

#include "MyVideoPlayer.h"
#include "IElectraPlayerPluginModule.h"
#include "MediaPlayer.h"
#include "MediaEventSink.h"
#include "Engine/Texture2D.h"
#include "UObject/ConstructorHelpers.h"

// 注意：需要在项目的 .Build.cs 中添加对 “ElectraPlayerPlugin” 和 “MediaAssets” 模块的依赖

AMyVideoPlayer::AMyVideoPlayer()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AMyVideoPlayer::BeginPlay()
{
	Super::BeginPlay();

	// 1. 获取 Electra 播放器模块
	ElectraModule = FModuleManager::GetModulePtr<IElectraPlayerPluginModule>(TEXT("ElectraPlayerPlugin"));
	if (!ElectraModule || !ElectraModule->IsInitialized())
	{
		UE_LOG(LogTemp, Error, TEXT("ElectraPlayerPlugin module not found or not initialized!"));
		return;
	}

	// 2. 创建媒体事件接收器 (简单实现)
	MediaEventSink = MakeShared<FMediaEventSink, ESPMode::ThreadSafe>();

	// 3. 创建播放器
	MediaPlayer = ElectraModule->CreatePlayer(*MediaEventSink);
	if (!MediaPlayer.IsValid())
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to create Electra Media Player."));
		return;
	}

	// 4. 打开视频文件
	if (MediaPlayer->OpenUrl(VideoFilePath))
	{
		UE_LOG(LogTemp, Log, TEXT("Opening video: %s"), *VideoFilePath);
		// 打开成功后，通常会通过 EventSink 的 OnMediaOpened 回调，在那里开始播放
		// 为简化，这里假设立即播放
		MediaPlayer->Play();
	}
}

void AMyVideoPlayer::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (MediaPlayer.IsValid())
	{
		MediaPlayer->Close();
		MediaPlayer.Reset();
	}
	MediaEventSink.Reset();
	Super::EndPlay(EndPlayReason);
}

void AMyVideoPlayer::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 在实际项目中，你需要将 MediaPlayer->GetVideoTexture() 返回的纹理资源
	// 绑定到你的 UI Widget (Image 控件) 或者使用一个动态材质实例来显示。
	// 此示例省略了具体的渲染绑定代码。
}
```

## 模块依赖

要使用 ElectraPlayer 插件，你的项目模块通常需要依赖以下模块（基于提供的 Build.cs 分析）：

| 模块 | 用途 |
|---|---|
| `ElectraPlayerPlugin` | 核心插件模块，提供 `IElectraPlayerPluginModule` 接口用于创建播放器。 |
| `MediaAssets` | UE 的媒体资产框架，提供 `UMediaPlayer`, `UMediaSource` 等蓝图和资产支持。 |
| `ElectraPlayerRuntime` | Electra 播放器的运行时核心库，处理解码、流媒体协议等底层功能。 |
| `ElectraProtron` | （可选）仅当你明确需要使用优化的 Protron 桌面播放器功能时才需依赖。 |

**说明**：`Core`, `Engine`, `Slate`, `UMG` 等基础模块是常见依赖，未列出。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复了 Protron 播放器在播放完一个视频后无法播放新视频的 Bug。 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复了流媒体专辑元数据解析问题。 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 新增配置项，允许控制播放期间是否暂停解码器。 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam | 将断言改为条件判断，以处理 TS 流内部时间戳异常的情况。 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece | 在预加载字幕片段时检查序列索引，减少不必要的请求。 |

### 维护评价

ElectraPlayer 是 Unreal Engine 5 的官方核心媒体播放器解决方案。
- **活跃维护**：从近期提交记录看（2026年5月有多次提交），该插件仍在被 Epic Games 的工程师持续维护和更新，不断修复 Bug 并增加新功能。
- **技术成熟**：作为从内部项目（NFL）迁移过来的成熟产品，经过了大规模应用验证。
- **推荐使用**：对于 UE5 项目中的视频播放需求，特别是涉及网络流媒体和跨平台播放时，**强烈推荐使用 ElectraPlayer**。它是当前 UE 媒体框架中功能最全面、性能最优的选择。
- **已知限制**：Protron 优化播放器主要面向桌面平台，其他平台的本地文件播放使用标准 Electra 播放器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer/Tests)