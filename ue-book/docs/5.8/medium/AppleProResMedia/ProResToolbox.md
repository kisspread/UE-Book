# Apple ProRes Media

> Implements video playback and the export of the Apple ProRes Codec.  Apple ProRes is a high quality, lossy video compression format.

| 属性 | 值 |
|---|---|
| 中文名 | ProRes 媒体编解码 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleProResMedia` (Runtime), `ProResToolbox` (External) |
| 实验性 | 否 |
| 创建时间 | 2019-08-16 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AppleProResMedia) | |

## 用途

此插件为 Unreal Engine 提供 **Apple ProRes 编解码器** 的运行时支持，实现两个核心功能：

1. **ProRes 视频文件播放**：通过 UE 的 Media Framework（MediaPlayer、MediaTexture）播放封装在 QuickTime (.mov) 容器中的 ProRes 视频，作为 WmfMedia 插件的编解码扩展。
2. **ProRes 视频导出**：配合 MovieRenderPipeline（影片渲染队列/Movie Graph），将渲染输出编码为 ProRes 格式的 .mov 文件。

底层依赖 Apple 提供的 **ProResToolbox** 外部 C 库，该库提供完整的 ProRes 文件读写 API（基于 QuickTime 文件格式规范），支持 ProRes 422 Proxy / LT / 标准 / HQ / 4444 / 4444 XQ 全系列编码。

**重要限制**：
- 仅支持 **Win64**（不支持 Win64:arm64）和 **Mac** 平台
- **不支持 Server** 目标平台
- 默认未启用（`EnabledByDefault: false`），需要在插件设置中手动启用
- 依赖 WmfMedia 插件（Windows 平台上使用 Windows Media Foundation 进行底层媒体框架集成）

## 使用场景

- 你在做影片渲染队列（Movie Render Queue）输出，需要将渲染结果导出为高质量的 ProRes 编码 .mov 文件
- 你的项目需要在运行时播放 ProRes 编码的过场动画或背景视频（Windows 平台）
- 你使用 Movie Graph Renderer 需要 ProRes 输出格式
- 你的后期制作管线要求 ProRes 中间编码格式

## 蓝图用法

此插件**不暴露任何蓝图 API**。它通过 UE 的 Media Framework 插件系统和 MovieRenderPipeline 管线系统被间接使用。

### 在 Media Player 中使用

ProRes 作为媒体格式注册后，可以通过标准的 Media Player 资产来播放 ProRes 编码的 .mov 文件。使用方式与播放其他媒体格式完全一致——在 MediaPlayer 资产中选择文件即可，引擎会自动通过 AppleProResMedia 插件进行解码。

### 在 Movie Render Pipeline 中使用

在影片渲染队列或 Movie Graph 的输出设置中，选择 ProRes 作为输出编解码器。输出配置出现在 MovieRenderPipeline 的导出设置中。

## C++ 用法

此插件主要通过 UE 的 Media Framework 接口系统工作，不直接暴露面向游戏代码的公共 C++ API。其内部通过 `IMediaPlayer` 和 `IMediaTextureSampleConverter` 等接口集成。

### 核心内部接口

插件实现了以下 Media Framework 接口：

```cpp
// 媒体播放器 - 负责 ProRes 文件的播放
class FAppleProResMediaPlayer : public IMediaPlayer

// 媒体纹理采样转换器 - 负责 ProRes 帧到 GPU 纹理的解码
class FAppleProResMediaTextureSampleConverter : public IMediaTextureSampleConverter

// 媒体工厂 - 创建 MediaPlayer 实例
class FAppleProResMediaFactory : public IMediaPlayerFactory

// ProRes 媒体纹理工厂
class FAppleProResMediaTextureSampleFactory : public IMediaTextureSampleFactory
```

### ProResToolbox C API（底层库）

如果需要直接操作 ProRes 文件读写，可以使用 ProResToolbox 的 C API：

```cpp
// ProResToolbox 头文件位于 Source/ThirdParty/ProResToolbox/include/
#include "ProResFileReader.h"
#include "ProResFileWriter.h"
#include "ProResTypes.h"
```

## ProResToolbox API 参考

ProResToolbox 是 Apple 提供的底层 C 库，提供完整的 ProRes 文件读写能力。以下为关键 API 概述：

### 文件读取（ProResFileReader）

```c
// 创建文件读取器
PRStatus ProResFileReaderCreate(const char *utf8Path, ProResFileReaderRef *fileReaderOut);

// 获取文件时长
PRTime ProResFileReaderGetDuration(ProResFileReaderRef fileReader);

// 获取轨道数量
PRStatus ProResFileReaderGetTrackCount(ProResFileReaderRef fileReader, PRIndex *trackCountOut);

// 按索引获取轨道
PRStatus ProResFileReaderCopyTrackByIndex(
    ProResFileReaderRef fileReader, PRIndex trackIndex,
    ProResTrackReaderRef *retainedTrackOut,
    PRMediaType *mediaTypeOut,
    PRPersistentTrackID *persistentTrackIDOut);

// 获取轨道尺寸（视频宽高）
PRSize ProResTrackReaderGetDimensions(ProResTrackReaderRef trackReader);

// 创建样本游标用于逐帧读取
PRStatus ProResTrackReaderCreateCursorAtFirstSample(
    ProResTrackReaderRef trackReader, ProResSampleCursorRef *newCursorOut);
```

### 文件写入（ProResFileWriter）

```c
// 创建文件写入器
PRStatus ProResFileWriterCreate(const char *destUTF8Path, ProResFileWriterRef *newAssetWriterOut);

// 添加轨道
PRStatus ProResFileWriterAddTrack(
    ProResFileWriterRef writer, PRMediaType mediaType,
    PRPersistentTrackID *writerTrackIDOut);

// 开始写入会话
PRStatus ProResFileWriterBeginSession(ProResFileWriterRef writer, PRTime sessionStartTime);

// 添加样本数据
PRStatus ProResFileWriterAddSampleBufferToTrack(
    ProResFileWriterRef writer, PRPersistentTrackID writerTrackID,
    void *dataBuffer, size_t dataBufferLength,
    const PRSampleBufferDeallocator *deallocator,
    ProResFormatDescriptionRef formatDescription,
    int64_t numSamples, int64_t numSampleTimingEntries,
    const PRSampleTimingInfo *sampleTimingArray,
    int64_t numSampleSizeEntries, const size_t *sampleSizeArray);

// 结束会话并完成写入
PRStatus ProResFileWriterEndSession(ProResFileWriterRef writer, PRTime sessionEndTime);
PRStatus ProResFileWriterFinish(ProResFileWriterRef writer);
```

### 支持的编解码类型

| 编解码器 | 四字符码 | 说明 |
|---|---|---|
| ProRes 4444 XQ | `ap4x` | 最高质量，支持 4:4:4 + Alpha |
| ProRes 4444 | `ap4h` | 高质量 4:4:4，支持 Alpha |
| ProRes 422 HQ | `apch` | 高质量 4:2:2 |
| ProRes 422 | `apcn` | 标准质量 4:2:2 |
| ProRes 422 LT | `apcs` | 轻量级 4:2:2 |
| ProRes 422 Proxy | `apco` | 代理质量，用于离线编辑 |

## Demo 示例

以下示例演示如何使用 ProResToolbox API 读取 ProRes 文件的基本信息：

```cpp
// ProResReaderDemo.h
#pragma once

#include "CoreMinimal.h"

class FProResReaderDemo
{
public:
    static void ReadProResFileInfo(const FString& FilePath);
};
```

```cpp
// ProResReaderDemo.cpp
#include "ProResReaderDemo.h"

// ProResToolbox 头文件
#include "ProResFileReader.h"
#include "ProResFormatDescription.h"
#include "ProResTypes.h"
#include "ProResTime.h"

void FProResReaderDemo::ReadProResFileInfo(const FString& FilePath)
{
    // 将 UE 字符串转为 UTF-8 路径
    FTCHARToUTF8 Utf8Path(*FilePath);

    // 创建文件读取器
    ProResFileReaderRef FileReader = nullptr;
    PRStatus Status = ProResFileReaderCreate(Utf8Path.Get(), &FileReader);
    if (Status != 0 || !FileReader)
    {
        UE_LOG(LogTemp, Error, TEXT("无法打开 ProRes 文件: %s"), *FilePath);
        return;
    }

    // 获取文件时长（转换为秒）
    PRTime Duration = ProResFileReaderGetDuration(FileReader);
    double DurationSecs = PRTimeGetSeconds(Duration);
    UE_LOG(LogTemp, Log, TEXT("文件时长: %.2f 秒"), DurationSecs);

    // 获取时基
    PRTimeScale Timescale = ProResFileReaderGetTimescale(FileReader);
    UE_LOG(LogTemp, Log, TEXT("时基: %d"), Timescale);

    // 获取轨道数量
    PRIndex TrackCount = 0;
    ProResFileReaderGetTrackCount(FileReader, &TrackCount);
    UE_LOG(LogTemp, Log, TEXT("轨道数量: %d"), TrackCount);

    // 遍历轨道
    for (PRIndex i = 0; i < TrackCount; ++i)
    {
        ProResTrackReaderRef TrackReader = nullptr;
        PRMediaType MediaType = 0;
        PRPersistentTrackID TrackID = 0;

        Status = ProResFileReaderCopyTrackByIndex(
            FileReader, i, &TrackReader, &MediaType, &TrackID);

        if (Status == 0 && TrackReader)
        {
            if (MediaType == kPRMediaType_Video)
            {
                PRSize Dimensions = ProResTrackReaderGetDimensions(TrackReader);
                UE_LOG(LogTemp, Log,
                    TEXT("视频轨道 %d: %.0f x %.0f"), TrackID, Dimensions.width, Dimensions.height);

                // 获取格式描述（编码类型等）
                ProResFormatDescriptionRef FormatDesc =
                    ProResTrackReaderCopyFormatDescription(TrackReader);
                if (FormatDesc)
                {
                    uint32_t SubType = ProResFormatDescriptionGetMediaSubType(FormatDesc);
                    UE_LOG(LogTemp, Log, TEXT("  编码: 0x%08X"), SubType);
                    PRRelease(FormatDesc);
                }
            }
            else if (MediaType == kPRMediaType_Audio)
            {
                UE_LOG(LogTemp, Log, TEXT("音频轨道: %d"), TrackID);
            }

            PRRelease(TrackReader);
        }
    }

    // 释放文件读取器
    PRRelease(FileReader);
}
```

> **注意**：直接使用 ProResToolbox 属于底层 API 操作。在大多数场景下，应通过 UE 的 Media Framework（MediaPlayer 资产）或 MovieRenderPipeline 间接使用 ProRes 功能，而非直接调用此 C 库。

## 模块依赖

从 Build.cs 提取的依赖：

| 模块 | 用途 |
|---|---|
| `WmfMedia` | Windows Media Foundation 媒体框架集成，提供 IMediaPlayer 等基础设施 |
| `MediaUtils` | 媒体工具库（Media Framework 基础类） |
| `MediaAssets` | 媒体资产类型（MediaPlayer、MediaTexture） |
| `RenderCore` | 渲染核心（纹理采样转换） |
| `RHI` | 渲染硬件接口（GPU 纹理操作） |

插件级依赖（在 .uplugin 中声明）：
- **WmfMedia**：Windows 平台的媒体框架基础
- **MovieRenderPipeline**：影片渲染导出管线

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |

> 注：最近的 commit 主要涉及 MovieRenderPipeline 模块的改动，这些改动虽然提交在插件目录下，但实质是 MovieRenderPipeline 的功能更新，并非直接针对 ProRes 编解码核心逻辑的修改。上表仅列出与本插件直接相关的提交。

### 维护评价

- **创建时间**：2019 年 8 月（UE 4.23 时期），由 Epic Games 的 Patrick Boutot 从 Release-4.23 分支合并
- **维护模式**：被动维护——主要随 MovieRenderPipeline 和 UE 核心框架的更新而被动更新
- **核心稳定性**：ProResToolbox 是 Apple 提供的预编译 C 库，极少需要修改；插件适配层代码稳定
- **活跃度**：虽然最近有 commit 涉及此目录，但均为编译修复和 MovieRenderPipeline 功能更新，ProRes 核心逻辑长期未变
- **推荐程度**：**推荐使用**。作为 Epic Games 官方支持的 ProRes 编解码插件，功能成熟稳定。需要注意的是默认未启用，需手动开启。仅支持 Win64/Mac 平台。

⚠️ 该插件默认未启用（`EnabledByDefault: false`），使用前需在项目设置的插件页面手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AppleProResMedia)
- [WmfMedia 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia)
- [MovieRenderPipeline 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline)