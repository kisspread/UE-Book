# MfMedia

> Implements a media player using the Microsoft Media Foundation framework. Requires Xbox One or Windows 7 and higher.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体基础播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MfMedia` (RuntimeNoCommandlet), `MfMediaEditor` (Editor), `MfMediaFactory` (Editor), `MfMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2017-01-25 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MfMedia) | |

## 用途

MfMedia 是 Unreal Engine Media Framework 的一个**媒体播放器后端实现**，基于 Microsoft Media Foundation (MF) API 构建。它不是面向最终用户的插件，而是 Media Framework 插件化架构中的底层组件。

**解决的问题**：UE5 的 Media Framework 需要在不同平台上使用不同的原生媒体解码 API。MfMedia 负责在 **Windows 7+** 和 **Xbox One** 平台上，利用 Media Foundation 进行视频和音频的解码与播放。它是 WMFMedia（基于更老的 Windows Media Format SDK）的现代替代方案。

**核心职责**：
- 通过 `IMFSourceReader` 从本地文件、URL 或内存存档中读取媒体数据
- 将 Media Foundation 的音频/视频采样转换为 UE5 的 `IMediaAudioSample` / `IMediaTextureSample`
- 管理多音轨、多视频轨、字幕轨的选择与切换
- 支持可变帧率、循环播放、播放速率控制等媒体控制功能

**默认不启用**的原因：该插件仅适用于 Microsoft 平台（Windows/Xbox），其他平台使用对应的后端（如 AvfMedia 用于 macOS/iOS，AndroidMedia 用于 Android）。

## 使用场景

- 你需要在 **Windows** 或 **Xbox One** 项目中播放视频文件 → MfMedia 作为 Media Framework 后端自动被使用
- 你使用 `MediaPlayer` 蓝图组件或 `UMediaPlayer` C++ 类播放媒体内容 → 引擎会自动选择可用的媒体播放器后端
- 你需要播放 `.mp4`、`.wmv`、`.avi` 等 Windows 原生支持的媒体格式 → MfMedia 通过 Media Foundation 提供编解码器支持
- 你需要从内存中的 `FArchive` 数据流播放媒体（而非文件路径）→ MfMedia 的 `FMfMediaByteStream` 支持此功能

## 蓝图用法

MfMedia 是一个底层媒体播放器后端实现，**不暴露任何 BlueprintCallable 函数**。它通过 UE5 Media Framework 的标准接口（`IMediaPlayer`、`IMediaControls`、`IMediaTracks`、`IMediaView`）与上层交互。

**在蓝图中使用媒体播放的方式**：

1. 添加 `Media Player` 组件到 Actor
2. 设置 Media Source 资产（URL 或文件路径）
3. 调用 `Open Source` / `Open URL` 等标准媒体播放节点
4. 引擎自动选择 MfMedia 后端（在 Windows/Xbox 平台上）

> 如果你需要直接通过蓝图控制播放器后端，请参阅 Media Framework 通用文档，所有媒体播放器后端共享相同的蓝图 API。

## C++ 用法

MfMedia 的使用者通常是 Media Framework 内部框架代码。直接使用 MfMedia 的场景较少，以下内容主要面向需要理解或扩展该后端的开发者。

### 头文件引入

```cpp
// MfMedia 模块公共接口（唯一对外暴露的头文件）
#include "IMfMediaModule.h"
```

### 基本用法：创建媒体播放器

通过 `IMfMediaModule` 创建基于 Media Foundation 的播放器实例。以下代码展示了框架层面的典型调用方式：

```cpp
// 来源: Public/IMfMediaModule.h
#include "IMfMediaModule.h"

// 加载 MfMedia 模块
IMfMediaModule* MfMediaModule = FModuleManager::LoadModulePtr<IMfMediaModule>("MfMedia");

if (MfMediaModule != nullptr)
{
    // 创建媒体播放器（需要传入事件接收器）
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = MfMediaModule->CreatePlayer(EventSink);
    
    if (Player.IsValid())
    {
        // 打开媒体源
        Player->Open(TEXT("C:/Videos/test.mp4"), nullptr);
    }
}
```

### 进阶用法：理解媒体播放器生命周期

MfMedia 的核心类 `FMfMediaPlayer` 实现了 `IMediaPlayer` 接口的完整生命周期。以下是关键调用流程：

```cpp
// 1. 播放器创建后，调用 Open 打开媒体源
// 来源: Private/Player/MfMediaPlayer.h
Player->Open(Url, Options);

// 2. 引擎每帧调用三个 Tick 函数（分别处理不同线程）
Player->TickFetch(DeltaTime, Timecode);  // 获取线程：更新状态、处理特征
Player->TickInput(DeltaTime, Timecode);  // 输入线程：处理视频/字幕采样
Player->TickAudio();                      // 音频线程：处理音频采样

// 3. 通过 IMediaControls 控制播放
IMediaControls& Controls = Player->GetControls();
Controls.SetRate(1.0f);          // 正常速度播放
Controls.SetRate(2.0f);          // 2倍速播放
Controls.Seek(FTimespan::FromSeconds(30.0));  // 跳转到30秒
Controls.SetLooping(true);       // 设置循环播放

// 4. 通过 IMediaTracks 查询/选择轨道
IMediaTracks& Tracks = Player->GetTracks();
int32 VideoTrackCount = Tracks.GetNumTracks(EMediaTrackType::Video);
int32 AudioTrackCount = Tracks.GetNumTracks(EMediaTrackType::Audio);

// 获取视频轨道格式信息
FMediaVideoTrackFormat VideoFormat;
Tracks.GetVideoTrackFormat(0, 0, VideoFormat);
// VideoFormat.Dim 包含分辨率, VideoFormat.FrameRate 包含帧率
```

### 进阶用法：从内存存档播放媒体

MfMedia 支持从内存中的 `FArchive` 数据流播放媒体，通过 `FMfMediaByteStream` 实现：

```cpp
// 来源: Private/Mf/MfMediaByteStream.h
// FMfMediaByteStream 将 FArchive 包装为 IMFByteStream，
// 使 Media Foundation 能从内存数据源读取

// 使用 IMediaPlayer::Open 的 Archive 重载版本
TSharedRef<FArchive, ESPMode::ThreadSafe> Archive = /* ... */;
FString OriginalUrl = TEXT("file:///C:/Videos/test.mp4");  // 原始 URL（用于格式检测）

Player->Open(Archive, OriginalUrl, Options);
```

## Demo 示例

以下示例展示了如何在 C++ 中使用 Media Framework API（由 MfMedia 后端在 Windows 上实现）来播放媒体：

```cpp
// MyMediaPlayer.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
#include "MyMediaPlayerComponent.generated.h"

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class UMyMediaPlayerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMediaPlayerComponent();

    /** 媒体播放器对象 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    TObjectPtr<UMediaPlayer> MediaPlayer;

    /** 媒体纹理（用于渲染到材质） */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    TObjectPtr<UMediaTexture> MediaTexture;

    /** 要播放的媒体 URL */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    FString MediaUrl;

    /** 开始播放 */
    UFUNCTION(BlueprintCallable, Category = "Media")
    bool StartPlayback();

    /** 停止播放 */
    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopPlayback();

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);

    UFUNCTION()
    void OnMediaOpenFailed(FString FailedUrl);
};
```

```cpp
// MyMediaPlayerComponent.cpp
#include "MyMediaPlayerComponent.h"
#include "IMfMediaModule.h"  // 验证 MfMedia 模块是否可用

UMyMediaPlayerComponent::UMyMediaPlayerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyMediaPlayerComponent::BeginPlay()
{
    Super::BeginPlay();

    // 检查 MfMedia 后端是否可用
    IModuleInterface* MfMediaModule = FModuleManager::Get().LoadModule(TEXT("MfMedia"));
    if (MfMediaModule == nullptr)
    {
        UE_LOG(LogTemp, Warning, TEXT("MfMedia module not available. "
               "Media playback will use another backend or fail."));
    }
}

bool UMyMediaPlayerComponent::StartPlayback()
{
    if (MediaPlayer == nullptr || MediaUrl.IsEmpty())
    {
        return false;
    }

    // 绑定回调
    MediaPlayer->OnMediaOpened.AddDynamic(this, &UMyMediaPlayerComponent::OnMediaOpened);
    MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &UMyMediaPlayerComponent::OnMediaOpenFailed);

    // 打开媒体（在 Windows 上，引擎会自动使用 MfMedia 后端）
    FMediaSourceCacheSettings CacheSettings;
    CacheSettings.bOverride = false;
    return MediaPlayer->OpenUrl(MediaUrl);
}

void UMyMediaPlayerComponent::StopPlayback()
{
    if (MediaPlayer != nullptr)
    {
        MediaPlayer->Close();
    }
}

void UMyMediaPlayerComponent::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Media opened: %s"), *OpenedUrl);
    
    // 设置循环播放
    MediaPlayer->SetLooping(true);
    
    // 输出媒体信息
    IMediaTracks& Tracks = MediaPlayer->GetTracks();
    UE_LOG(LogTemp, Log, TEXT("  Video tracks: %d"), 
           Tracks.GetNumTracks(EMediaTrackType::Video));
    UE_LOG(LogTemp, Log, TEXT("  Audio tracks: %d"), 
           Tracks.GetNumTracks(EMediaTrackType::Audio));
}

void UMyMediaPlayerComponent::OnMediaOpenFailed(FString FailedUrl)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open media: %s"), *FailedUrl);
}
```

## 模块依赖

从源码分析，MfMedia 依赖以下系统级组件：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | Media Framework 上层资产类型（MediaPlayer、MediaTexture 等） |
| `MediaUtils` | Media Framework 工具类（采样池、采样格式等） |
| `Media` | Media Framework 核心接口定义（IMediaPlayer、IMediaTracks 等） |
| Media Foundation SDK (mfapi.h, mfidl.h, mfreadwrite.h) | Windows 原生媒体框架 API（系统依赖，非引擎模块） |
| `Microsoft/COMPointer.h` | UE5 COM 智能指针封装（TComPtr） |

> 无特殊模块依赖（核心依赖为标准 Media Framework 模块链 + Windows Media Foundation SDK）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 全引擎日志宏迁移，非功能性改动 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 全引擎析构函数规范化，非功能性改动 |
| 2025-09-25 | `94af5100` | Replaced PREPROCESSOR_TO_STRING with UE_STRINGIZE. | 全引擎宏替换，非功能性改动 |
| 2025-06-20 | `642aa84c` | Fix PVS warnings | 修复 PVS-Studio 静态分析警告 |
| 2025-02-18 | `0ecd6846` | Media: reworking the timestamp associated sequence index | 重构时间戳关联的序列索引（功能性更新） |

### 维护评价

- **年龄**：创建于 2017 年 1 月（UE 4.15 时期），已存在约 9 年
- **最近更新**：近期更新均为全引擎级别的自动化代码维护（日志宏迁移、析构函数规范化等），仅有 `0ecd6846`（2025-02）是 Media Framework 相关的功能性改动
- **活跃程度**：**维护不活跃**。自 2017 年创建以来，大部分更新为引擎范围的批量重构。最近一次 MfMedia 专属功能性更新追溯到数年前
- **状态**：**稳定但不活跃**。作为底层平台媒体播放器后端，功能已基本完善，不需要频繁更新。Media Foundation API 本身变化不大
- **推荐使用**：**推荐**。在 Windows 和 Xbox 平台上，MfMedia 是 Media Framework 的标准后端之一。虽然不活跃维护，但作为引擎内置组件仍然可靠。注意该插件**默认不启用**，需要在项目设置中手动启用

> ⚠️ 该插件 `EnabledByDefault=false`，如需使用需在 Project Settings → Plugins 中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media)（无独立测试目录，测试位于 Media Framework 通用测试中）