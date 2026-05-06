# Electra Player Runtime

> Cross platform media player for local files and internet streaming.  
> Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 播放器运行时 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++ 源代码） |
| 模块 | `ElectraPlayerRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer/Source/ElectraPlayerRuntime) | |

## 用途

`ElectraPlayerRuntime` 是 Electra Player 插件的核心运行时库。它提供完整的跨平台媒体播放能力，包括：

- 流媒体协议支持：HLS（HTTP Live Streaming）、DASH（Dynamic Adaptive Streaming over HTTP）、MPEG Transport Stream（ISO 13818-1）、ISO Base Media File Format（mp4）、Matroska/WebM（MKV）
- 自适应比特率（ABR）选择：支持 VoD、Live、Low Latency 等多种场景的比特率自适应规则
- 解复用（Demuxing）与解码：视频、音频、字幕的解析、解码及输出管理
- 渲染时钟同步：协调视频、音频、字幕的播放时间
- 网络请求与缓存：HTTP 请求管理、响应缓存，支持 Common Media Client Data (CMCD) 内容感知数据上报
- 内容导向（Content Steering）：根据服务器指示切换 CDN/路径
- 事件与元数据处理：Application Event Stream (AEMS) 事件、时间元数据、字幕

该模块不直接暴露蓝图接口，而是作为底层引擎供给 `ElectraPlayerPlugin`、`ElectraPlayerFactory` 等上层模块使用。开发者通常通过 `UMediaPlayer` 组件或 C++ API 与 Electra Player 交互。

## 使用场景

- 需要播放本地 mp4 文件或远程流媒体（HLS、DASH）的游戏或应用
- 对低延迟直播、高码率 VoD 有需求的场景
- 需要精确控制音视频同步、字幕显示、自适应码率切换的应用
- 在桌面平台（Windows、Mac、Linux）使用 Protron 优化本地 mp4 播放

## 蓝图用法

`ElectraPlayerRuntime` 模块本身不提供蓝图可调用函数。所有媒体播放的蓝图节点位于 `Media Player` 资产及蓝图函数库中，由 `ElectraPlayerPlugin` 桥接。例如：

- 通过 `Open Source` 节点播放媒体文件
- 通过 `Media Player` 资产设置播放源

如需在 C++ 中调用，请参考下方 C++ 用法。

## C++ 用法

### 头文件引入

```cpp
#include "Player/AdaptiveStreamingPlayer.h"
#include "Player/AdaptiveStreamingPlayerInternal.h"
```

### 基本用法

以下示例展示如何创建并初始化一个自适应流播放器，播放 HLS VoD 流。

```cpp
// Source: Engine/Plugins/Media/ElectraPlayer/Source/ElectraPlayerRuntime/Private/Player/AdaptiveStreamingPlayer.h

// 1. 创建视频和音频输出处理器（需提供纹理池等）
TSharedPtr<FOutputHandlerVideo, ESPMode::ThreadSafe> VideoOutput = MakeShared<FOutputHandlerVideo, ESPMode::ThreadSafe>();
TSharedPtr<FOutputHandlerAudio, ESPMode::ThreadSafe> AudioOutput = MakeShared<FOutputHandlerAudio, ESPMode::ThreadSafe>();

// 2. 设置播放器创建参数
IAdaptiveStreamingPlayer::FCreateParam CreateParams;
CreateParams.VideoOutputHandler = VideoOutput;
CreateParams.AudioOutputHandler = AudioOutput;
CreateParams.ExternalPlayerGUID = FGuid::NewGuid();
CreateParams.WorkerThreads = IAdaptiveStreamingPlayer::FCreateParam::EWorkerThreads::Shared;

// 3. 创建播放器实例
TSharedPtr<IAdaptiveStreamingPlayer, ESPMode::ThreadSafe> Player = IAdaptiveStreamingPlayer::Create(CreateParams);

// 4. 初始化播放器选项（可选）
FParamDict Options;
Options.Set(OptionKeyInitialBitrate, FVariantValue(int64(2000000)));   // 初始码率 2Mbps
Options.Set(OptionKeyMaxVerticalResolution, FVariantValue(int64(1080))); // 最大分辨率 1080p

Player->Initialize(Options);

// 5. 设置流媒体的初始属性（可选）
FStreamSelectionAttributes Attr;
Attr.CodecName = TEXT("h264");
Attr.Resolution = FStreamCodecInformation::FResolution(1920, 1080);
Player->SetInitialStreamAttributes(EStreamType::Video, Attr);

// 6. 开始加载并播放（URL 可以是 HLS、DASH 或文件路径）
Player->LoadManifest(TEXT("https://example.com/path/to/playlist.m3u8"));

// 7. 播放控制
Player->Play();         // 开始播放
Player->Pause();        // 暂停
Player->SeekTo(FTimeValue(30.0));  // 跳转到 30 秒处
```

### 进阶用法

**1. 监听度量事件（Metrics）**

```cpp
// 定义一个度量接收器
class FMyMetricsReceiver : public IAdaptiveStreamingPlayerMetrics
{
public:
    virtual void ReportDownloadEnd(const Metrics::FSegmentDownloadStats& SegmentDownloadStats) override
    {
        UE_LOG(LogTemp, Log, TEXT("Segment downloaded: %s, HTTP status: %d"), 
            *SegmentDownloadStats.URL, SegmentDownloadStats.HTTPStatusCode);
    }
    // ... 其他虚函数
};

// 添加到播放器
TSharedPtr<FMyMetricsReceiver, ESPMode::ThreadSafe> MetricsReceiver = MakeShared<FMyMetricsReceiver, ESPMode::ThreadSafe>();
Player->AddMetricsReceiver(MetricsReceiver.Get());
```

**2. 配置 ABR 规则**

```cpp
// ElectraPlayerRuntime 内置多种 ABR 规则（固定码率直播、VoD+ 等）
// 通过选项键可以调整行为，例如设置 CDN 拒绝的 HTTP 状态码
Options.Set(ABR::OptionKeyABR_CDNSegmentDenyHTTPStatus, FVariantValue(int64(403)));
Player->ModifyOptions(Options, FParamDict());
```

**3. 使用 HTTP 响应缓存**

```cpp
// 设置 HTTP 响应缓存（可外部提供）
TSharedPtr<IElectraPlayerDataCache, ESPMode::ThreadSafe> ExternalCache = ...;
TSharedPtrTS<IHTTPResponseCache> Cache = IHTTPResponseCache::Create(10 * 1024 * 1024, 500, ExternalCache);
// Cache 需要与 Player 的 HTTP 管理器关联，具体通过 PlayerSessionServices 中的 GetHTTPResponseCache()
```

## Demo 示例

以下是一个最小可编译的 C++ 示例，展示如何初始化播放器并播放本地文件。

**PlayerDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Player/AdaptiveStreamingPlayer.h"
#include "OutputHandler.h"
#include "ElectraTextureSample.h"
#include "IElectraAudioSample.h"

class FPlayerDemo
{
public:
    FPlayerDemo();
    ~FPlayerDemo();

    void PlayLocalFile(const FString& InFilePath);
    void Stop();
    void Pause();
    void Resume();
    void SeekTo(float InSeconds);

private:
    TSharedPtr<IAdaptiveStreamingPlayer, ESPMode::ThreadSafe> Player;
    TSharedPtr<FOutputHandlerVideo, ESPMode::ThreadSafe> VideoOutput;
    TSharedPtr<FOutputHandlerAudio, ESPMode::ThreadSafe> AudioOutput;
};
```

**PlayerDemo.cpp**

```cpp
#include "PlayerDemo.h"
#include "Containers/UnrealString.h"
#include "Misc/Paths.h"
#include "GenericPlatform/GenericPlatformProcess.h"

FPlayerDemo::FPlayerDemo()
{
    VideoOutput = MakeShared<FOutputHandlerVideo, ESPMode::ThreadSafe>();
    AudioOutput = MakeShared<FOutputHandlerAudio, ESPMode::ThreadSafe>();

    // 创建播放器
    IAdaptiveStreamingPlayer::FCreateParam CreateParams;
    CreateParams.VideoOutputHandler = VideoOutput;
    CreateParams.AudioOutputHandler = AudioOutput;
    CreateParams.ExternalPlayerGUID = FGuid::NewGuid();
    CreateParams.WorkerThreads = IAdaptiveStreamingPlayer::FCreateParam::EWorkerThreads::Shared;

    Player = IAdaptiveStreamingPlayer::Create(CreateParams);
}

FPlayerDemo::~FPlayerDemo()
{
    Stop();
    Player.Reset();
}

void FPlayerDemo::PlayLocalFile(const FString& InFilePath)
{
    if (!Player)
        return;

    // 初始化选项
    FParamDict Options;
    Options.Set(OptionKeyMaxVerticalResolution, FVariantValue(int64(1080)));
    Player->Initialize(Options);

    // 加载并播放（Electra 支持本地文件路径）
    Player->LoadManifest(InFilePath);
    Player->Play();
}

void FPlayerDemo::Stop()
{
    if (Player)
        Player->Stop();
}

void FPlayerDemo::Pause()
{
    if (Player)
        Player->Pause();
}

void FPlayerDemo::Resume()
{
    if (Player)
        Player->Resume();
}

void FPlayerDemo::SeekTo(float InSeconds)
{
    if (Player)
        Player->SeekTo(FTimeValue(InSeconds));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Engine` | 引擎核心功能，包括 `IMediaPlayer` 等媒体接口 |
| `DirectX` | 使用 DirectX 纹理池进行 GPU 视频渲染（Windows 平台） |

> 提示：实际构建时，`ElectraPlayerRuntime` 会通过 `PrivateDependencyModuleNames` 使用 `DirectX`，使用者无需额外链接。`Engine` 是公开依赖。

## 维护状态

### 近期更新

- 2025-10-01 `31d4710d` — ElectraPlayer: Improved support for replay events; added ability to turn a HLS VoD stream into a replay
- 2025-09-29 `d34a730c` — ElectraPlayer: Emit warning about mismatched media segment duration only when the duration check was performed
- 2025-09-29 `49fa2b76` — ElectraPlayer: Adjusting the maximum Live edge latency in case the media segments have a larger duration
- 2025-09-23 `0dc995dc` — ElectraPlayer: Using a VoD asset for a synchronized event now allows it to loop when provided via DASH
- 2025-09-11 `d9f531d6` — Electra: combined multiline raw string into a single line

### 维护评价

- **创建时间**：2025-09-11，距今不足 1 个月，属于全新模块。
- **更新频率**：从 git 历史看，从 9 月 11 日到 10 月 1 日有 5 次提交，更新非常活跃，包含功能增强、警告调整、事件改进等。
- **活跃程度**：当前处于高度活跃维护状态，社区和 Epic 持续改进。
- **已知问题**：无公开严重问题。
- **推荐度**：强烈推荐使用。该模块是 UE5 默认流媒体播放器核心，提供跨平台、多协议、高性能播放能力。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer/Source/ElectraPlayerRuntime)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer/Tests)