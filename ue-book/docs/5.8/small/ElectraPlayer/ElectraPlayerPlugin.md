# Electra Player

> Cross platform media player for local files and internet streaming. Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 电子媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

ElectraPlayer 是 UE5 的**跨平台媒体播放器**，用于播放本地文件和网络流媒体。它替代了早期的媒体播放方案，提供更现代的架构和更好的性能。

核心功能包括：

1. **跨平台媒体播放** - 支持本地文件和互联网流媒体（HLS、DASH 等协议）
2. **Protron 优化播放器** - 专门针对桌面平台优化的 MP4 本地文件播放器，使用 DirectX 12 硬件解码
3. **媒体框架集成** - 作为 Media Framework 的 Player 实现，与 MediaPlayer、MediaTexture 等组件无缝协作
4. **流媒体分析** - 内置分析和指标上报功能，用于监控播放质量

## 使用场景

- 你需要播放在线视频流（直播、点播）→ 用 ElectraPlayer 的流媒体功能
- 你需要在桌面平台高效播放本地 MP4 文件 → 用 Protron 优化播放器
- 你需要跨平台的媒体播放方案（Windows、Mac、Linux、主机）→ 用 ElectraPlayer
- 你需要播放 HLS 或 DASH 自适应流 → ElectraPlayer 原生支持

## 模块架构

```
ElectraPlayerPlugin/
├── ElectraPlayerFactory      ← 工厂：创建 Electra 播放器实例
├── ElectraPlayerPlugin       ← 插件入口：模块接口定义
├── ElectraPlayerPluginHandler← 处理器：协调播放器生命周期
├── ElectraPlayerRuntime      ← 核心运行时：解码、渲染、流媒体处理
├── ElectraProtron            ← Protron：桌面平台 MP4 硬件加速播放
└── ElectraProtronFactory     ← Protron 工厂：创建 Protron 播放器实例
```

## 蓝图用法

ElectraPlayer 通过 UE5 Media Framework 的标准蓝图接口使用：

### 核心组件

| 组件 | 说明 |
|---|---|
| `MediaPlayer` | 媒体播放器资产，配置播放源和选项 |
| `MediaTexture` | 媒体纹理，将视频帧渲染到材质 |
| `MediaSoundWave` | 媒体音频波形，播放音频 |
| `MediaSource` | 媒体源（FileMediaSource / StreamMediaSource） |

### 使用示例（蓝图描述）

**播放本地视频：**

1. 创建 `MediaPlayer` 资产，Player 实现选择 "Electra Player"
2. 创建 `MediaTexture` 资产，关联 MediaPlayer
3. 创建 `FileMediaSource` 资产，设置文件路径
4. 蓝图中调用 `MediaPlayer → OpenSource(MediaSource)`
5. 将 MediaTexture 连接到材质的纹理节点

**播放网络流：**

1. 创建 `StreamMediaSource` 资产，设置流媒体 URL
2. 蓝图中调用 `MediaPlayer → OpenSource(StreamMediaSource)`
3. 监听 `OnMediaOpened` / `OnMediaOpenFailed` 事件

## C++ 用法

### 头文件引入

```cpp
#include "IElectraPlayerPluginModule.h"
```

### 基本用法

```cpp
// 获取 ElectraPlayer 模块
IElectraPlayerPluginModule& ElectraModule = FModuleManager::LoadModuleChecked<IElectraPlayerPluginModule>("ElectraPlayerPlugin");

// 检查模块是否初始化
if (ElectraModule.IsInitialized())
{
    // 创建媒体事件接收器
    IMediaEventSink* EventSink = /* ... */;
    
    // 创建播放器实例
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = ElectraModule.CreatePlayer(*EventSink);
    
    if (Player.IsValid())
    {
        // 打开媒体源
        Player->OpenUrl(TEXT("https://example.com/stream.m3u8"));
        // 或打开本地文件
        // Player->OpenUrl(TEXT("file:///C:/video.mp4"));
    }
}
```

### 进阶用法 - 分析指标

```cpp
// 发送播放分析指标
FGuid PlayerGuid = FGuid::NewGuid();
TSharedPtr<IAnalyticsProviderET> AnalyticsProvider = /* ... */;

ElectraModule.SendAnalyticMetrics(AnalyticsProvider, PlayerGuid);
ElectraModule.SendAnalyticMetricsPerMinute(AnalyticsProvider);

// 报告播放错误
ElectraModule.ReportVideoStreamingError(PlayerGuid, TEXT("Connection timeout"));

// 报告字幕相关指标
ElectraModule.ReportSubtitlesMetrics(
    PlayerGuid, 
    TEXT("https://example.com/subtitles.vtt"), 
    0.5,  // 响应时间（秒）
    TEXT("")  // 无错误
);
```

## Demo 示例

### 简单媒体播放器

```cpp
// SimpleMediaPlayer.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
#include "SimpleMediaPlayer.generated.h"

UCLASS(BlueprintType, Blueprintable)
class ASimpleMediaPlayer : public AActor
{
    GENERATED_BODY()

public:
    ASimpleMediaPlayer();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaSource* MediaSource;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StartPlayback();

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopPlayback();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);

    UFUNCTION()
    void OnMediaOpenFailed(FString FailedUrl);
};
```

```cpp
// SimpleMediaPlayer.cpp
#include "SimpleMediaPlayer.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
#include "FileMediaSource.h"
#include "StreamMediaSource.h"

ASimpleMediaPlayer::ASimpleMediaPlayer()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ASimpleMediaPlayer::BeginPlay()
{
    Super::BeginPlay();

    if (MediaPlayer)
    {
        // 绑定事件
        MediaPlayer->OnMediaOpened.AddDynamic(this, &ASimpleMediaPlayer::OnMediaOpened);
        MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &ASimpleMediaPlayer::OnMediaOpenFailed);
    }
}

void ASimpleMediaPlayer::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}

void ASimpleMediaPlayer::StartPlayback()
{
    if (!MediaPlayer || !MediaSource)
    {
        UE_LOG(LogTemp, Warning, TEXT("MediaPlayer or MediaSource is null"));
        return;
    }

    // 打开媒体源
    if (MediaPlayer->OpenSource(MediaSource))
    {
        UE_LOG(LogTemp, Log, TEXT("Opening media source..."));
    }
}

void ASimpleMediaPlayer::StopPlayback()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}

void ASimpleMediaPlayer::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Media opened: %s"), *OpenedUrl);
    
    // 开始播放
    if (MediaPlayer)
    {
        MediaPlayer->Play();
    }
}

void ASimpleMediaPlayer::OnMediaOpenFailed(FString FailedUrl)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open media: %s"), *FailedUrl);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraBase` | Electra 基础库（共享类型和工具） |
| `DirectX` | DirectX 数学库支持 |
| `D3D12RHI` | DirectX 12 渲染硬件接口（Protron 硬件解码） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复 Protron 无法播放新视频的问题 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复流媒体专辑元数据问题 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 添加配置项控制播放时是否挂起解码器 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam | 改进 .ts 文件内部时间戳处理逻辑 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece | 优化字幕预加载时的序列索引检查 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **创建时间**: 2021-01-06，约 5 年历史
- **最近更新**: 2026-05-21，**5 天前**有更新
- **维护状态**: **非常活跃** - Epic Games 持续维护，近期内有多次功能更新和 bug 修复
- **核心地位**: 作为 UE5 的默认媒体播放器，是 Media Framework 的核心组件
- **推荐使用**: ✅ **强烈推荐** - 这是 Epic 官方推荐的媒体播放方案，跨平台支持完善，持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [IElectraPlayerPluginModule.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Media/ElectraPlayer/Source/ElectraPlayerPlugin/Public/IElectraPlayerPluginModule.h)