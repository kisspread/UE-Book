# Electra Player

> Cross platform media player for local files and internet streaming. Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

---

## 用途

ElectraPlayer 是 UE5 内置的**跨平台自适应流媒体播放器**，用于播放本地文件和互联网流媒体内容。它是 UE Media Framework 的底层实现之一，当通过 `UMediaPlayer` 播放 HLS、DASH 等自适应流媒体 URL 时，底层实际上由 ElectraPlayer 负责网络请求、流解析、自适应码率切换、DRM 解密、音视频解码调度等全部流程。

ElectraPlayer 解决的核心问题：
- **自适应流媒体播放**：自动解析 HLS（.m3u8）和 DASH（.mpd）清单文件，根据网络带宽动态切换码率
- **跨格式支持**：统一处理 MP4、MKV/WebM、MPEG Audio（.mp3）、MPEG-TS 等多种容器格式
- **DRM 支持**：通过 CDM 接口支持加密内容播放
- **内容导向分发（CDN）切换**：支持 DASH Content Steering 和 HLS Content Steering，实现多 CDN 自动选择
- **低延迟直播**：支持 DASH-LL 和 LL-HLS 低延迟流
- **桌面优化**：Protron 子模块针对桌面平台提供本地 MP4 文件的优化播放路径

## 使用场景

- 你需要在游戏内播放来自 CDN 的 HLS 或 DASH 自适应直播流 → 使用 ElectraPlayer（通过 `UMediaPlayer` + `UMediaSource`）
- 你需要播放远程服务器上的 .mp4/.mkv/.mp3 文件 → 使用 ElectraPlayer
- 你需要支持加密（DRM）媒体内容 → ElectraPlayer 内置 CDM 集成
- 你需要低延迟直播（如电竞赛事直播） → 支持 DASH-LL / LL-HLS
- 你只需要在桌面端快速播放本地 MP4 → 使用 Protron 优化路径

## 蓝图用法

ElectraPlayerRuntime 模块本身是纯运行时 C++ 模块，不暴露 `UFUNCTION(BlueprintCallable)` API。播放功能通过 UE 标准的 Media Framework 蓝图接口使用：

- `Open Source` 节点（`UMediaPlayer::OpenSource`）
- `Play` / `Pause` / `Stop` 节点
- `Seek` 节点
- 事件委托 `OnMediaOpened` / `OnMediaOpenFailed` / `OnPlaybackResumed` 等

### 核心节点（通过 Media Framework 间接使用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 使用 UMediaSource 打开媒体 URL | `UMediaPlayer` |
| `Play` / `Pause` / `Stop` | 播放控制 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间 | `UMediaPlayer` |
| `Set Rate` | 设置播放速率（快进/慢放） | `UMediaPlayer` |
| `Set Looping` | 设置循环播放 | `UMediaPlayer` |
| `Select Track` | 选择音轨/字幕轨 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1. 在场景中放置一个 `Media Player` 资产和 `File Media Source` / `Stream Media Source`
2. 设置 Media Source 的 URL 为 HLS/DASH 流地址（如 `https://example.com/live/stream.m3u8`）
3. 使用 `Open Source` 节点打开媒体
4. 监听 `OnMediaOpened` 事件确认加载成功
5. 使用 `Play` 节点开始播放
6. 可选：使用 `Select Track` 切换音轨或字幕

## C++ 用法

### 头文件引入

```cpp
// 核心播放器接口
#include "IElectraPlayerInterface.h"

// 如果需要访问运行时模块
#include "IElectraPlayerRuntimeModule.h"
```

### 基本用法：创建播放器实例

ElectraPlayer 通过工厂方法创建，返回标准的 `IMediaPlayer` 接口指针。源码来自 `IElectraPlayerInterface.h`。

```cpp
#include "IElectraPlayerInterface.h"

// 通过工厂创建 Electra 播放器
TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = FElectraPlayerRuntimeFactory::CreatePlayer(
    InEventSink,
    SendAnalyticMetricsDelegate,
    SendAnalyticMetricsPerMinuteDelegate,
    ReportVideoStreamingErrorDelegate,
    ReportSubtitlesFileMetricsDelegate
);

// 使用标准 IMediaPlayer 接口操作
if (Player.IsValid())
{
    Player->Open(URL, Options);
}
```

**来源**: `Source/ElectraPlayerRuntime/Private/ElectraPlayer.h` — `FElectraPlayer` 类实现 `IMediaPlayer`, `IMediaCache`, `IMediaControls`, `IMediaTracks`, `IMediaView` 全部接口。

### 基本用法：Safe Media Options 传递

在 Media Framework 中传递 `IMediaOptions` 指针存在 GC 安全问题。ElectraPlayer 提供了安全包装类：

```cpp
#include "IElectraPlayerInterface.h"

// 在 UMediaSource 派生类中创建安全选项接口
class UMyMediaSource : public UMediaSource
{
    TSharedPtr<FElectraSafeMediaOptionInterface> SafeOptions;
    
    void Init()
    {
        // 将自身包装为安全的 MediaOptions
        SafeOptions = MakeShared<FElectraSafeMediaOptionInterface>(this);
    }
};

// 使用时，通过 FScopedLock 安全访问
{
    FElectraSafeMediaOptionInterface::FScopedLock Lock(SafeOptions);
    IMediaOptions* Options = SafeOptions->GetMediaOptionInterface();
    if (Options)
    {
        // 安全使用 Options...
    }
}
```

**来源**: `Source/ElectraPlayerRuntime/Public/IElectraPlayerInterface.h`

### 进阶用法：模块初始化检查

```cpp
#include "IElectraPlayerRuntimeModule.h"

// 检查 Electra 运行时模块是否已初始化
IElectraPlayerRuntimeModule* Module = FModuleManager::GetModulePtr<IElectraPlayerRuntimeModule>("ElectraPlayerRuntime");
if (Module && Module->IsInitialized())
{
    // 模块已就绪，可以创建播放器
}
```

**来源**: `Source/ElectraPlayerRuntime/Public/IElectraPlayerRuntimeModule.h`

## Demo 示例

一个完整的最小示例，展示如何通过 Media Framework 间接使用 ElectraPlayer 播放 HLS 流：

```cpp
// MyMediaComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MediaTexture.h"
#include "MyMediaComponent.generated.h"

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class UMyMediaComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMediaComponent();

    UFUNCTION(BlueprintCallable, Category = "Media")
    bool OpenAndPlayStream(const FString& URL);

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopPlayback();

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaTexture* MediaTexture;

private:
    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);
    
    UFUNCTION()
    void OnMediaOpenFailed(FString FailedUrl);
};
```

```cpp
// MyMediaComponent.cpp
#include "MyMediaComponent.h"
#include "MediaSource.h"

UMyMediaComponent::UMyMediaComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UMyMediaComponent::OpenAndPlayStream(const FString& URL)
{
    if (!MediaPlayer)
    {
        UE_LOG(LogTemp, Error, TEXT("MediaPlayer is null"));
        return false;
    }

    // 绑定事件
    MediaPlayer->OnMediaOpened.AddDynamic(this, &UMyMediaComponent::OnMediaOpened);
    MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &UMyMediaComponent::OnMediaOpenFailed);

    // 创建 Stream Media Source 并打开 URL
    // ElectraPlayer 将自动检测 HLS/DASH 并处理
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->SetFilePath(URL);

    return MediaPlayer->OpenSource(MediaSource);
}

void UMyMediaComponent::StopPlayback()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}

void UMyMediaComponent::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Media opened: %s"), *OpenedUrl);
    MediaPlayer->Play();
}

void UMyMediaComponent::OnMediaOpenFailed(FString FailedUrl)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open media: %s"), *FailedUrl);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DirectX` | Direct3D 相关图形接口，用于视频帧渲染（ElectraPlayerRuntime） |
| `D3D12RHI` | D3D12 渲染硬件接口，用于 Protron 桌面优化路径（ElectraProtron） |
| `ElectraBase` | Electra 基础库，提供共享工具类（ElectraPlayerFactory, ElectraProtronFactory） |

> 注：`Engine` 依赖已省略（常见依赖）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had already played one | 修复 Protron 播放第二个视频失败的问题 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复流式传输时专辑元数据解析问题 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 新增配置项控制播放期间是否暂停解码器 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestamp | 将断言改为条件判断以处理 .ts 内部时间戳异常 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnecessary downloads | 预取字幕时检查序列索引以减少不必要下载 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **创建时间**：2021年1月，从 Epic 内部 NFL 项目迁移至公开源码（首次 commit 说明："Moved from NFL to public"）
- **近期更新**：最近一次更新在 2026年5月，过去一周内有多次功能性修复和改进，维护非常活跃
- **维护频率**：持续有 bug 修复、性能优化和功能增强
- **活跃维护者**：Epic Games 官方团队（commit 中可见 Thomas Engel、Jens Petersam 等核心开发者）
- **已知特点**：这是 UE5 自适应流媒体播放的核心实现，随着 UE5 版本迭代持续更新
- **推荐使用**：强烈推荐。这是 UE5 中播放 HLS/DASH 流媒体的标准且唯一的内置方案，且仍在积极维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/MediaFrameworkTests)