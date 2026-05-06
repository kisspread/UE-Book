# Media Foundation Media Player

> Implements a media player using the Microsoft Media Foundation framework. Requires Xbox One or Windows 7 and higher.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体基础播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MfMedia` (RuntimeNoCommandlet), `MfMediaEditor` (Editor), `MfMediaFactory` (Editor), `MfMediaFactory` (RuntimeNoCommandlet with Win64) |
| 实验性 | 否 |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MfMedia) | |

## 用途

该插件通过 Windows Media Foundation (WMF) 原生框架实现媒体播放功能，是 UE 媒体框架（Media Framework）的播放器后端之一。它利用操作系统的硬件加速解码能力，高效播放视频和音频文件（如 MP4、WMV 等常见格式），并支持从文件、网络 URL 以及内存存档（`FArchive`）读取媒体数据。

插件解决的核心问题：
- 在 Windows 平台（Win7+）上提供原生级别的媒体播放性能和兼容性。
- 通过标准 `IMediaPlayer` 接口与 UE 媒体管道集成，可被 `MediaPlayer` 资产和 UMG 控件直接使用。
- 支持音频/视频轨道切换、播放控制（播放、暂停、跳转）、缓存控制等功能。

## 使用场景

- 你正在开发一个 Windows 游戏或应用，需要播放视频过场动画、菜单背景视频或 UI 动画。
- 你的项目需要从远程 URL 流式播放媒体内容，或者从内存中（如解包后的加密存档）播放媒体。
- 你希望利用系统底层的硬件解码器来降低 CPU 占用，并支持高分辨率/高码率视频。
- 你的目标平台不包括 Xbox One（插件名称虽提到 Xbox One，但当前源码主要面向 Windows 平台）。

## 蓝图用法

本插件不直接暴露蓝图可调用节点，但通过媒体框架的通用节点可完成所有操作。在蓝图编辑器中：

1. **创建 Media Player 资产**：在内容浏览器中选择“媒体播放器 (MediaPlayer)”资产类型，创建后在其属性面板的“播放器”部分将“媒体播放器覆盖”设置为 `Media Foundation Media Player`。
2. **创建 Media Source 资产**：选择“媒体源 (MediaSource)”资产，设置文件路径（支持相对路径、绝对路径或网络 URL）。
3. **连接播放**：使用蓝图节点 `Open Source`（打开媒体源）、`Play`（播放）、`Pause`（暂停）等标准媒体节点控制播放。
4. **显示视频**：将 `File Media Source` 或平台原生媒体纹理拖入材质，或使用 `Media Texture` 资产配合 `Image` / `Widget` 控件进行渲染。

由于 `MfMedia` 内部实现了 `IMediaPlayer`，所有标准媒体蓝图节点均自动支持该播放器。

## C++ 用法

### 头文件引入

```cpp
#include "IMfMediaModule.h"
#include "IMediaPlayer.h"
#include "IMediaEventSink.h"
```

### 基本用法

通过模块接口创建播放器实例，然后打开媒体源。以下示例展示了播放一个本地视频文件：

```cpp
// 获取 MfMedia 模块
IMfMediaModule* MediaModule = FModuleManager::LoadModulePtr<IMfMediaModule>("MfMedia");
if (!MediaModule)
{
    // 插件未启用或平台不支持
    return;
}

// 创建媒体事件接收器（简单示例：控制台输出）
class FSimpleEventSink : public IMediaEventSink
{
public:
    virtual void ReceiveMediaEvent(EMediaEvent Event) override
    {
        UE_LOG(LogTemp, Log, TEXT("Media Event: %d"), (int32)Event);
    }
};
FSimpleEventSink EventSink;

// 创建播放器
TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = MediaModule->CreatePlayer(EventSink);
if (!Player.IsValid())
{
    return;
}

// 打开媒体文件（绝对路径或相对路径）
FString FilePath = TEXT("C:\\Videos\\intro.mp4");
if (!Player->Open(FilePath, nullptr))
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open media file: %s"), *FilePath);
}
```

### 进阶用法

- **从内存存档播放**：可使用 `Open(const TSharedRef<FArchive, ESPMode::ThreadSafe>& Archive, const FString& OriginalUrl, const IMediaOptions* Options)` 方法，从 `FArchive` 读取加密或打包的媒体数据。
- **轨道选择**：通过 `GetTracks()` 获取 `IMediaTracks` 接口，主动选择音频/视频/字幕轨道。
- **缓存控制**：实现 `IMediaCache` 接口（本插件内建支持），可配置预加载策略和缓冲区大小。
- **播放选项**：传递 `FMediaPlayerOptions` 结构体，指定开始时间、循环模式等。

示例：从内存播放媒体（来自测试用例中的 `FMfMediaByteStream` 机制）：

```cpp
// 假设有一个 TArray<uint8> 内存数据
TSharedRef<FArchive, ESPMode::ThreadSafe> Archive = MakeShareable(new FMemoryReader(Buffer));
FString OriginalUrl = TEXT("memory://video.mp4");
if (!Player->Open(Archive, OriginalUrl, nullptr))
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open media from memory"));
}
```

## Demo 示例

一个完整的可编译最小示例，展示如何使用 MfMedia 播放视频文件（该代码应放置在一个独立模块中，并确保模块依赖了 `MfMedia` 和 `Media` 等模块）。

### MyMediaPlayerDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "IMediaEventSink.h"

class IMediaPlayer;

class FMyMediaPlayerDemo
{
public:
    void Run(const FString& MediaFilePath);
    
private:
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player;
    TSharedPtr<IMediaEventSink> EventSink;
};
```

### MyMediaPlayerDemo.cpp

```cpp
#include "MyMediaPlayerDemo.h"
#include "IMfMediaModule.h"
#include "Modules/ModuleManager.h"
#include "IMediaPlayer.h"

// 简单事件接收器：打印事件到日志
class FMyEventSink : public IMediaEventSink
{
public:
    virtual void ReceiveMediaEvent(EMediaEvent Event) override
    {
        const TCHAR* EventNames[] = {
            TEXT("MediaOpened"),
            TEXT("MediaClosed"),
            TEXT("MediaFailed"),
            TEXT("PlaybackSuspended"),
            TEXT("PlaybackResumed"),
            // ... 其他事件
        };
        if ((int32)Event < UE_ARRAY_COUNT(EventNames))
        {
            UE_LOG(LogTemp, Log, TEXT("Media Event: %s"), EventNames[(int32)Event]);
        }
    }
};

void FMyMediaPlayerDemo::Run(const FString& MediaFilePath)
{
    IMfMediaModule* MediaModule = FModuleManager::LoadModulePtr<IMfMediaModule>("MfMedia");
    if (!MediaModule)
    {
        UE_LOG(LogTemp, Error, TEXT("MfMedia module not available!"));
        return;
    }

    EventSink = MakeShareable(new FMyEventSink);
    Player = MediaModule->CreatePlayer(*EventSink);
    if (!Player.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create MfMedia player!"));
        return;
    }

    if (!Player->Open(MediaFilePath, nullptr))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open media: %s"), *MediaFilePath);
    }
    
    // 后续可以使用 Player->GetControls()->Play() 等
}
```

## 模块依赖

若要使用 `MfMedia` 插件，你的模块的 `Build.cs` 需要添加以下独特依赖（标准 Core/Engine 等已省略）：

| 模块 | 用途 |
|---|---|
| `Media` | 提供 `IMediaPlayer`, `IMediaControls`, `IMediaSamples` 等核心接口 |
| `MediaUtils` | 提供媒体样本队列、对象池等工具类 |
| `MediaAssets` | 若要在蓝图中通过资产使用，需要此模块（通常由编辑器自动处理） |

注意：`MfMedia` 本身依赖 Windows SDK 的 Media Foundation 组件（`mfapi.dll`, `mferror.dll` 等），这些属于系统库，无需额外 UE 模块。

## 维护状态

### 近期更新

- 2025-06-20 `642aa84c` — Fix PVS warnings（修复 PVS 静态分析警告）
- 2025-02-18 `0ecd6846` — Media: reworking the timestamp associated sequence index（重构时间戳关联的序列索引）
- 2025-02-06 `81c434be` — Media: Added a new "MediaBufferingComplete" event（添加新事件 MediaBufferingComplete）
- 2024-12-18 `6ed576ac` — [FormatStringSan] disallow printing TCHAR*'s via %d (and fix all occurrences)（修复格式字符串安全问题）
- 2024-05-06 `1d0682a5` — Media: Changed CanPlayUrl() to return a value indicating the confidence that the media can be played（修改 CanPlayUrl 返回值以表示可信度）

### 维护评价

- **创建时间**：2024 年 5 月，距今约 1 年（2025 年 7 月）。
- **更新频率**：最近 6 个月内有 2 次功能性更新（媒体事件和时序重构），维护活跃度尚可。
- **功能完整性**：该插件已稳定运行，覆盖常见使用场景，支持文件/URL/内存播放。
- **已知限制**：
  - 只支持 Windows 平台（且排除 UE Server 编译）。
  - 默认不启用，需要手动在插件管理器中激活 `Media Foundation Media Player`。
  - 部分高级特性（如字幕、HDR）可能未完全实现。
- **推荐度**：推荐在 Windows 项目中使用，作为替代内置 Windows Media Player 后端的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MfMedia)
- [官方文档（UE 论坛）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MfMedia/Source)（插件的测试逻辑集成在 `Private/Player/MfMediaPlayer.cpp` 等源文件中，暂无独立测试文件）