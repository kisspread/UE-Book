# Electra Player

> Cross platform media player for local files and internet streaming. Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

ElectraPlayer 是 UE5 内置的跨平台自适应流媒体播放器，是 Epic Games 开发的完整媒体播放解决方案。它解决了以下核心问题：

- **自适应流媒体播放**：支持 HLS 和 DASH 两种主流自适应比特率流媒体协议，能根据网络状况自动切换视频/音频质量
- **本地文件播放**：支持 MP4 (ISO 14496-12)、MKV/WebM 和 MPEG Audio（如 MP3）等常见媒体容器格式
- **DRM 内容保护**：内置 DRM 管理器，支持通过 CDM（Content Decryption Module）播放加密内容
- **CDN 内容分发优化**：实现了 CTA-5004 (Common Media Client Data) 标准和 Content Steering，优化 CDN 选择策略
- **低延迟直播**：支持低延迟 DASH 和低延迟 HLS 直播场景
- **桌面优化播放**：ElectraProtron 子模块提供针对桌面平台优化的本地 MP4 专用播放器

与 UE5 媒体框架中其他播放器插件（如 WMF、AVFoundation）不同，ElectraPlayer 是一个完全跨平台的纯软件实现，不依赖任何平台特定的媒体 API。

## 使用场景

- 你需要在游戏内播放网络直播流（HLS/DASH）→ 使用 ElectraPlayer
- 你需要播放远程视频 URL 并根据带宽自适应切换画质 → 使用 ElectraPlayer
- 你需要播放本地 MP4 文件作为游戏内过场动画 → 使用 ElectraPlayer
- 你需要播放加密 DRM 视频内容 → 使用 ElectraPlayer
- 你需要播放 MPEG Audio（MP3）文件 → 使用 ElectraPlayer
- 你在桌面平台上需要高性能本地 MP4 播放 → 使用 ElectraProtron

## 蓝图用法

ElectraPlayer 通过 UE 标准 Media Framework 接口在蓝图中使用，不提供额外的 BlueprintCallable 函数。播放器通过 `UMediaPlayer` / `UMediaSource` / `UMediaTexture` 等标准媒体组件在蓝图中操作。

### 核心交互方式

| 组件 | 说明 | 用法 |
|---|---|---|
| `UMediaPlayer` | 媒体播放器组件 | 在蓝图中创建实例，使用 Open Source / Open URL 节点 |
| `UMediaSource` | 媒体源（URL 或文件） | 配置媒体地址，作为输入传给播放器 |
| `UMediaTexture` | 渲染媒体到纹理 | 将播放器输出绑定到 3D 物体或 UI |

### 使用示例（蓝图描述）

1. 在 Actor 中添加 `UMediaPlayer` 组件
2. 创建 `UFileMediaSource`（本地文件）或 `UStreamMediaSource`（网络 URL），设置路径
3. 调用 `MediaPlayer → Open Source` 打开媒体
4. 创建 `UMediaTexture`，设置其 MediaPlayer 为上一步的播放器
5. 在 Material 中使用 MediaTexture 节点将视频渲染到网格

> **注意**：ElectraPlayer 是默认禁用的媒体播放器插件，需要在项目设置中手动启用。在打包时，系统会自动选择 ElectraPlayer 作为媒体播放器后端。

## C++ 用法

### 头文件引入

```cpp
#include "IElectraPlayerInterface.h"
```

### 基本用法

ElectraPlayer 主要通过 UE 标准 Media Framework 接口使用。以下是通过工厂创建播放器实例的方式（来源：`Public/IElectraPlayerInterface.h`）：

```cpp
#include "IElectraPlayerInterface.h"

// 通过工厂创建 Electra 播放器实例
// 通常由 Media Framework 内部调用，但也可以直接使用
TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = FElectraPlayerRuntimeFactory::CreatePlayer(
    EventSink,                    // IMediaEventSink - 接收媒体事件
    AnalyticMetricsDelegate,      // 分析指标委托
    AnalyticMetricsPerMinuteDelegate, // 每分钟分析指标委托
    VideoStreamingErrorDelegate,  // 视频流错误委托
    SubtitlesMetricsDelegate      // 字幕指标委托
);

// 使用标准 IMediaPlayer 接口操作
Player->Open(URL, Options);
Player->GetControls().Seek(NewTime);
Player->GetControls().SetRate(1.0f);
```

### 安全媒体选项

当通过 Media Framework 传递 `IMediaOptions` 指针时（如 `UMediaSource`），由于 GC 可能回收底层对象，ElectraPlayer 提供了安全封装（来源：`Public/IElectraPlayerInterface.h`）：

```cpp
// 在自定义 MediaSource 中使用安全选项接口
class UMyMediaSource : public UMediaSource
{
    TSharedPtr<FElectraSafeMediaOptionInterface> SafeOptions;
    
    void Init()
    {
        // 创建安全包装
        SafeOptions = MakeShared<FElectraSafeMediaOptionInterface>(this);
    }
    
    // 通过 GetMediaOption("GetSafeMediaOptions") 查询安全接口
    // 使用时通过 FScopedLock 自动加锁
    {
        FElectraSafeMediaOptionInterface::FScopedLock Lock(SafeOptions);
        IMediaOptions* Opts = SafeOptions->GetMediaOptionInterface();
        if (Opts)
        {
            // 安全访问媒体选项
        }
    }
};
```

### 可检索位置数据

```cpp
#include "IElectraPlayerInterface.h"

// 传递可检索位置数据到播放器
TArray<FTimespan> Positions;
Positions.Add(FTimespan::FromSeconds(10.0));
Positions.Add(FTimespan::FromSeconds(30.0));
Positions.Add(FTimespan::FromSeconds(60.0));

// 通过 IMediaOptions 传递
TSharedPtr<FElectraSeekablePositions> SeekPositions = 
    MakeShared<FElectraSeekablePositions>(Positions);
```

## 内部架构概览

ElectraPlayer 内部是一个大型自适应流媒体播放框架，以下是核心子系统：

| 子系统 | 关键类 | 职责 |
|---|---|---|
| 自适应播放器核心 | `IAdaptiveStreamingPlayer`, `FAdaptiveStreamingPlayer` | 播放器状态机、播放控制、缓冲管理 |
| HLS 解析器 | `FPlaylistParserHLS`, `FMultiVariantPlaylistHLS` | Apple HLS 播放列表解析和管理 |
| DASH 解析器 | `FManifestDASHInternal`, `IDashMPDElement` | MPEG DASH MPD 解析和管理 |
| MP4 解析器 | `IParserISO14496_12` | ISO 基本媒体文件格式解析 |
| MKV 解析器 | `IParserMKV` | Matroska/WebM 容器解析 |
| MPEG 传输流 | `IParserISO13818_1` | MPEG-TS 流解析 |
| MPEG 音频 | `FManifestMPEGAudioInternal` | MP3/AAC 流解析 |
| ABR 策略 | `IAdaptiveStreamSelector`, `IABRRule` | 自适应比特率选择算法 |
| 内容分发 | `FContentSteeringHandler` | CDN 路径选择和内容导引 |
| CMCD | `FCMCDHandler` | CTA-5004 Common Media Client Data |
| DRM | `FDRMManager` | 数字版权管理 |
| HTTP 管理 | `IElectraHttpManager` | HTTP 请求和连接管理 |
| 解码器基础 | `IDecoderBase` | 解码器抽象层 |
| 输出处理 | `FOutputHandlerVideo`, `FOutputHandlerAudio` | 视频/音频采样输出 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DirectX` | Windows 平台 Direct3D 图形 API 支持 |
| `D3D12RHI` | DirectX 12 渲染硬件接口（ElectraProtron 依赖） |
| `ElectraBase` | Electra 基础工具库（工厂模块依赖） |

无特殊依赖（核心仅标准 Core/Engine/Slate 等，加上平台图形 API）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复 Protron 播放器在已播放视频后无法播放新视频的问题 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复流式播放中专辑元数据的显示问题 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 新增配置项和 CVar 控制播放期间解码器是否需要挂起 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam | 将断言改为条件判断以处理 .ts 内部时间戳异常情况 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece | 在预取字幕段时检查序列索引，减少不必要的预取 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

ElectraPlayer 处于非常活跃的维护状态。最近的提交记录显示持续有功能增强和 Bug 修复（2026 年 5 月有多次提交）。作为 Epic Games 官方维护的跨平台媒体播放器，它是 UE5 媒体框架的核心组件之一。

该插件规模庞大（约 175 个源文件），架构设计成熟，支持 HLS、DASH、MP4、MKV、MPEG Audio 等多种媒体格式，并包含完整的 ABR 自适应算法、DRM 支持和 CDN 内容导引等高级功能。

**推荐使用**：对于需要在 UE5 中进行视频播放的项目，ElectraPlayer 是官方推荐的跨平台解决方案，特别是涉及网络流媒体的场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)