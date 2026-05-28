# Bink Media

> Implements a media player using Bink.

| 属性 | 值 |
|---|---|
| 中文名 | Bink 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BinkMediaPlayer` (Runtime), `BinkMediaPlayerEditor` (Editor), `BinkMediaPlayerSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2021-06-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BinkMedia) | |

## 用途

此插件为 Unreal Engine 5 集成了 **Bink 视频解码库**，使引擎能够播放 Bink 格式（`.bik`）的视频文件。Bink 是一款广泛应用于游戏行业的高性能视频编解码器，以其高压缩率和低解码开销而闻名，特别适合在游戏运行时播放过场动画、开场视频等。

插件的核心价值在于提供了一个完整的媒体播放器后端，将 Bink 的解码能力与 UE 的媒体框架（`MediaAssets`）无缝对接，开发者可以通过标准的媒体纹理（Media Texture）和媒体播放器蓝图/代码来使用 Bink 视频。

## 使用场景

- **游戏开场与过场动画**：在游戏启动、场景转换或剧情节点播放预渲染的高质量 Bink 视频。
- **加载画面视频**：在加载关卡时，播放循环视频以丰富用户体验。
- **游戏内实时视频**：在游戏中通过电视、监视器等物体播放 Bink 格式的视频流。
- **需要高性能视频解码的场合**：当项目对视频播放的 CPU/GPU 开销和内存占用有严格要求时，Bink 是理想选择。

**注意**：该插件默认未启用（`EnabledByDefault: false`）。要使用它，必须在项目设置中手动启用 `BinkMedia` 插件，并可能需要安装对应的 Bink SDK 许可。

## 蓝图用法

该插件将 Bink 集成到 UE 的媒体资产系统中，因此主要通过媒体资产相关的蓝图类使用。

### 核心节点

以下节点基于 UE 媒体框架，并为 Bink 进行了适配。具体的可用节点取决于 `BinkMediaPlayer` 模块实现的 `IMediaPlayer` 接口。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` / `Open File` / `Open URL` | 用于加载并准备播放一个 Bink 媒体源。 | `UBinkMediaPlayer` (通过 `UMediaPlayer` 接口) |
| `Play` | 开始或恢复播放已打开的 Bink 视频。 | `UBinkMediaPlayer` (通过 `UMediaPlayer` 接口) |
| `Pause` | 暂停当前播放。 | `UBinkMediaPlayer` (通过 `UMediaPlayer` 接口) |
| `Close` | 关闭当前媒体源，释放资源。 | `UBinkMediaPlayer` (通过 `UMediaPlayer` 接口) |
| `Set Looping` | 设置视频是否循环播放。 | `UBinkMediaPlayer` (通过 `UMediaPlayer` 接口) |
| `Set Rate` | 设置播放速率（如快进、慢放）。 | `UBinkMediaPlayer` (通过 `UMediaPlayer` 接口) |

**使用方式**：
1.  在内容浏览器中创建或导入一个 `.bik` 格式的视频文件，它会自动成为一个 `Media Source` 资产。
2.  创建一个 `Media Player` 资产，并在详情面板中将其播放器类型指定为 `BinkMediaPlayer`。
3.  在蓝图中，获取该 `Media Player` 的引用，调用 `Open Source` 节点并传入 Bink 媒体源。
4.  将 `Media Player` 的输出链接到一个 `Media Texture`，再将 `Media Texture` 应用到材质或 UI 上。
5.  通过 `Play` 等节点控制播放。

## C++ 用法

通常，开发者通过 UE 的 `UMediaPlayer` 类来间接使用 Bink。以下示例展示了底层 SDK 的初始化流程，有助于理解其工作原理。

### 头文件引入

```cpp
// 主要使用 SDK 提供的类型和函数
#include "binktiny.h"

// 通常也包含媒体资产模块的头文件
#include "MediaPlayer.h"
#include "MediaTexture.h"
```

### 基本用法 (初始化与播放)

以下代码片段展示了如何使用 Bink SDK 进行最基本的初始化、打开文件和获取信息。此示例来源于对 `binktiny.h` 中 API 的推断。
```cpp
// 来源：基于 include/binktiny.h 的 API 分析

// 1. 初始化 Bink 的高层 (High-Level) 系统
// 参数：线程数，音频频率(0表示不初始化音频)，音频通道数
BinkHLInit(2, 0, 0);

// 2. 打开一个 Bink 文件
// 参数：文件名，音频轨道类型，音频轨道起始ID，缓冲策略，文件偏移量
HBINK bink_handle = BinkHLOpen("MyVideo.bik", BINKHLSNDLAYOUT_NONE, 0, BINKHLBUFFER_STREAM, 0);

if (bink_handle)
{
    // 3. 循环解码并处理帧
    BINKHLINFO info;
    while (bink_handle) // 或者检查 playback_state != 3 (停止)
    {
        // 解码一帧（并处理音频、移动到下一帧）
        BinkHLProcess();

        // 获取当前信息
        BinkHLGetInfo(bink_handle, &info);

        // info.PlaybackState: 0=播放, 1=暂停, 2=Gotoing, 3=停止(结束)
        if (info.PlaybackState == 3) // 视频播放完毕
        {
            break;
        }

        // 将解码后的帧数据复制到渲染目标或纹理缓冲区 (示例)
        // S32 result = BinkCopyToBuffer(bink_handle, dest_buffer, dest_pitch, dest_height, 0, 0, BINKSURFACE32RGBA);

        // 更新你的游戏循环...
    }

    // 4. 关闭视频
    BinkClose(bink_handle);
}

// 5. 关闭 Bink 系统
BinkHLShutdown();
```

### 进阶用法 (预加载与字幕)

利用 SDK 的预加载和字幕功能可以优化加载时间和实现本地化。
```cpp
// 1. 预加载视频文件到内存
BINKHLPRELOADED* preloaded = BinkHLPreload("MyVideo.bik", 0);

if (preloaded)
{
    // 2. 从预加载数据中打开（更快）
    HBINK bink_handle = BinkHLOpenPreload(preloaded, BINKHLSNDLAYOUT_NONE, 0);

    // 3. 加载 SRT 字幕文件
    BinkLoadSubtitles(bink_handle, "Subtitles_EN.srt");

    // 在播放循环中，获取当前时间对应的字幕文本
    U32 iterate = 0;
    const char* subtitle_text = BinkCurrentSubtitle(bink_handle, &iterate, nullptr, nullptr);
    // 可以将 subtitle_text 显示在 UI 上

    // ... 使用 bink_handle ...

    // 4. 清理
    BinkClose(bink_handle);
    BinkHLUnpreload(preloaded); // 释放预加载的内存
}
```

## Demo 示例

一个最小化的控制台程序示例，演示如何初始化并获取一个 Bink 文件的基本信息。

```cpp
// BinkDemo.h
#pragma once
#include "CoreMinimal.h"

// 主要包含 Bink SDK 头文件
#include "binktiny.h"
```

```cpp
// BinkDemo.cpp
#include "BinkDemo.h"
#include "HAL/PlatformProcess.h"

void RunBinkDemo(const FString& VideoPath)
{
    // 1. 初始化
    BinkHLInit(1, 0, 0); // 1个线程，不初始化音频

    // 2. 打开文件
    // 注意：需要将 FString 转换为 char*
    FTCHARToUTF8 Converter(*VideoPath);
    HBINK handle = BinkHLOpen(Converter.Get(), BINKHLSNDLAYOUT_NONE, 0, BINKHLBUFFER_LOADALL, 0);

    if (!handle)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Bink file: %s. Error: %s"), *VideoPath, ANSI_TO_TCHAR(BinkGetError()));
        BinkHLShutdown();
        return;
    }

    // 3. 获取并打印信息
    BINKHLINFO Info;
    BinkHLGetInfo(handle, &Info);

    UE_LOG(LogTemp, Log, TEXT("Bink File Info:"));
    UE_LOG(LogTemp, Log, TEXT("  Dimensions: %u x %u"), Info.Width, Info.Height);
    UE_LOG(LogTemp, Log, TEXT("  Total Frames: %u"), Info.Frames);
    UE_LOG(LogTemp, Log, TEXT("  Frame Rate: %u / %u"), Info.FrameRate, Info.FrameRateDiv);
    UE_LOG(LogTemp, Log, TEXT("  Has Alpha: %s"), Info.NeedAlpha ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogTemp, Log, TEXT("  Has HDR: %s"), Info.NeedHDR ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogTemp, Log, TEXT("  Texture Luma Size: %u x %u"), Info.TextureBufferYAWidth, Info.TextureBufferYAHeight);

    // 4. 模拟处理一帧
    BinkHLProcess();
    UE_LOG(LogTemp, Log, TEXT("  Current Frame: %u (State: %u)"), Info.FrameNum, Info.PlaybackState);

    // 5. 清理
    BinkClose(handle);
    BinkHLShutdown();
}
```

**调用方式**：
```cpp
RunBinkDemo(FPaths::ProjectContentDir() + TEXT("Movies/MyTestVideo.bik"));
```

## 模块依赖

你的项目模块（通常是 `YourGameModule`）需要依赖以下模块才能使用 Bink 媒体播放器功能：

| 模块 | 用途 |
|---|---|
| `BinkMediaPlayerSDK` | 核心的 Bink 解码库和外部 SDK 头文件。这是必须链接的底层库。 |
| `MediaAssets` | 提供 UE 的媒体框架，包括 `UMediaPlayer`, `UMediaTexture` 等，是集成 Bink 到引擎的桥梁。 |
| `MoviePlayer` | 用于控制游戏内的全屏电影播放功能，Bink 媒体播放器需要与此模块协作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式，属于内部现代化重构。 |
| 2026-04-01 | `2f26bbfa` | Bink: Fixed BinkTestBed | 修复了 Bink 测试床的错误，属于测试和开发工具维护。 |
| 2026-04-01 | `8a338576` | Bink: Fixed foward def mismatch, just include PixelFormat.h | 修复了前向声明不匹配的编译问题，直接包含正确的头文件。 |
| 2026-04-01 | `9f45180e` | Bink: update for new BinkHL interface | 根据新版 Bink 高层（HL）接口更新了插件代码，这是一个功能性适配。 |
| 2026-02-19 | `3e97632c` | Refactored FSceneViewport / FViewport to remove the ViewportRHI field | 重构了视口相关类，移除了 ViewportRHI 字段。插件需要适配此引擎核心变更。 |

### 维护评价

- **活跃程度**：插件仍在维护中。最近的提交（2026年4月）包含了功能更新（适配新 BinkHL 接口）和编译修复，表明 Epic Games 和 Bink 团队（RAD Game Tools）仍在协作维护。
- **年龄**：创建于 2021 年，已有约 5 年历史，属于老古董级别，但鉴于 Bink 在行业的成熟地位，其稳定性很高。
- **状态**：该插件非实验性，但由于 `EnabledByDefault: false`，需要用户主动启用。它是一个功能完整、经过时间考验的第三方集成模块。
- **推荐度**：**推荐使用**。如果你的项目需要播放 Bink 格式的视频，这是一个官方支持的、可靠的集成方案。需注意它需要商业授权。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BinkMedia)
- [RAD Game Tools Bink 官方网站](https://www.radgametools.com/bink.htm) (获取 SDK 和授权)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BinkMedia/Tests) (如果存在)