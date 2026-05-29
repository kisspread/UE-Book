# Capture Metadata Extraction

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 采集元数据提取 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式资产） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerCPSClient` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureMetadataExtraction` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

本文档聚焦 **CaptureMetadataExtraction** 模块（[源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureMetadataExtraction)），它是 CaptureManagerCore 插件中负责**从各种采集设备和媒体文件中提取 Take 元数据**的核心模块。

该模块解决的核心问题是：在虚拟制片工作流中，来自不同设备（iPhone Live Link Face、立体相机阵列、单目/立体视频录制）的采集数据有着完全不同的元数据格式。CaptureMetadataExtraction 提供统一的提取接口，将这些异构数据转换为统一的 `FTakeMetadata` 结构，供下游的 CaptureManagerEditor 和 CaptureManagerApp 消费。

**主要能力：**
- 解析 Live Link Face 应用导出的 `.cptake` 及旧版 JSON 元数据
- 解析立体相机系统（Stereo Camera）的采集数据
- 从单目/立体视频文件中提取时码、帧率、分辨率等信息
- 支持 FFProbe 或 UE 内置 ElectraPlayer 两种媒体探测后端
- 自动检测标定文件格式（OpenCV vs Unreal）
- 处理图像序列目录（jpg/jpeg/png）

## 使用场景

- 你从 iPhone Live Link Face 应用录制了一段面部表演数据，导入到 UE → 使用 `ExtractLiveLinkFaceMetadata` 自动解析 `.cptake` 元数据
- 你用立体相机阵列拍摄了一组标定和表演数据 → 使用 `ExtractStereoVideoMetadata` 或 `FStereoCameraSystemTakeParser` 解析
- 你有一段单目视频录制（mp4/mov），需要提取时码和帧率信息 → 使用 `ExtractMonoVideoMetadata`
- 你有一个 `.cptake` 归档文件 → 使用 `ExtractTakeArchiveMetadata`
- 你需要探测视频文件的时码、帧率、音频时长等技术信息 → 使用 `FCaptureExtractVideoInfo`

## 蓝图用法

本模块的绝大部分 API 为纯 C++ 接口（返回 `TValueOrError` 模板），不直接暴露给蓝图。唯一的 BlueprintType 类 `UDesiredPlayerMediaSource` 是内部使用的媒体源辅助类（仅编辑器环境下可用）。

### 核心类

| 类/结构 | 说明 | 所在文件 |
|---|---|---|
| `FCaptureExtractVideoInfo` | 视频文件信息探测器（帧率、时码、音频、方向） | `Private/Utils/CaptureExtractTimecode.h` |
| `FCaptureExtractAudioTimecode` | 音频文件时码提取器 | `Private/Utils/CaptureExtractTimecode.h` |
| `FStereoCameraSystemTakeParser` | 立体相机 Take 元数据解析器 | `Private/StereoCameraTakeMetadata.h` |
| `FResolutionResolver` | 立体相机分辨率一致性校验器 | `Private/ResolutionResolver.h` |
| `FExtractionConfig` | 提取配置（FFProbe 路径等） | `Internal/CaptureManagerExtractionConfig.h` |
| `UDesiredPlayerMediaSource` | 指定 ElectraPlayer 的媒体源（BlueprintType, EditorOnly） | `Private/Utils/CaptureExtractTimecode.h` |

## C++ 用法

### 头文件引入

```cpp
// 视频信息探测
#include "Utils/CaptureExtractTimecode.h"

// 单目视频元数据提取
#include "MonoVideoMetadataExtractor.h"

// 立体视频元数据提取
#include "StereoVideoMetadataExtractor.h"

// Live Link Face 元数据提取
#include "LiveLinkFaceMetadataExtractor.h"

// Take 归档元数据提取
#include "TakeArchiveMetadataExtractor.h"

// 立体相机元数据解析
#include "StereoCameraTakeMetadata.h"

// 标定格式检测
#include "CaptureManagerCalibrationUtils.h"

// 文件扩展名判断
#include "CaptureManagerFileExtensions.h"
```

### 基本用法：探测视频文件信息

```cpp
// 使用 FCaptureExtractVideoInfo 探测视频文件的基本技术信息
// 支持两种后端：ElectraPlayer（默认）或 FFProbe

using namespace UE::CaptureManager;

// 默认使用 ElectraPlayer 探测
auto VideoInfoResult = FCaptureExtractVideoInfo::Create(TEXT("/path/to/video.mp4"));
if (VideoInfoResult.HasValue())
{
    FCaptureExtractVideoInfo& VideoInfo = VideoInfoResult.GetValue();
    
    FFrameRate FrameRate = VideoInfo.GetFrameRate();
    FTimecode Timecode = VideoInfo.GetTimecode();
    bool bHasAudio = VideoInfo.ContainsAudio();
    float AudioDuration = VideoInfo.GetAudioDurationSeconds();
    EMediaOrientation Orientation = VideoInfo.GetVideoOrientation();
}

// 使用 FFProbe 探测（需要配置 FFmpeg 路径）
FExtractionConfig Config;
Config.bUseFFprobe = true;
Config.FFmpegPath = TEXT("/usr/local/bin/ffmpeg");

TOptional<Private::FFProbeCommand> ProbeCommand(Private::FFProbeCommand(Config.FFmpegPath));
auto VideoInfoWithProbe = FCaptureExtractVideoInfo::Create(
    TEXT("/path/to/video.mp4"), ProbeCommand);
```

### 基本用法：提取单目视频元数据

```cpp
using namespace UE::CaptureManager;

// 构造单目视频描述符
FMonoVideoDescriptor Descriptor;
Descriptor.VideoFilePath = TEXT("/path/to/recorded.mp4");
Descriptor.AudioFilePaths = { TEXT("/path/to/audio.wav") };  // 可选外部音频
Descriptor.Slate = TEXT("Shot01");                            // 留空则从文件名推导
Descriptor.TakeNumber = 1;

FExtractionConfig Config;
auto Result = ExtractMonoVideoMetadata(MoveTemp(Descriptor), Config);

if (Result.HasValue())
{
    FTakeMetadata& Metadata = Result.GetValue();
    // 使用统一的 FTakeMetadata 结构...
}
else
{
    EMonoVideoExtractionError Error = Result.GetError();
    // VideoFileNotFound / UnsupportedVideoFormat / AudioFileNotFound
}
```

### 基本用法：提取 Live Link Face 元数据

```cpp
using namespace UE::CaptureManager;

FExtractionConfig Config;
auto Result = ExtractLiveLinkFaceMetadata(
    TEXT("/path/to/LiveLinkFaceCapture/Take001"), Config);

if (Result.HasValue())
{
    FTakeMetadata& Metadata = Result.GetValue();
    // Metadata 包含视频、音频、时码等统一结构
}
else
{
    ELiveLinkFaceExtractionError Error = Result.GetError();
    // DirectoryNotFound / MetadataFileNotFound / MetadataFormatNotRecognized / MultipleMetadataFilesFound
}
```

### 进阶用法：提取立体视频元数据

```cpp
using namespace UE::CaptureManager;

FStereoVideoDescriptor Descriptor;
Descriptor.VideoPathA = TEXT("/path/to/left_eye.mp4");     // 可以是视频文件
Descriptor.VideoPathB = TEXT("/path/to/right_eye.mp4");    // 或图像序列目录
Descriptor.AudioFilePaths = { TEXT("/path/to/audio.wav") };
Descriptor.CalibrationFilePath = TEXT("/path/to/calibration.json");  // 自动检测 OpenCV/Unreal 格式
Descriptor.Slate = TEXT("StereoShot01");
Descriptor.TakeNumber = 1;

FExtractionConfig Config;
auto Result = ExtractStereoVideoMetadata(MoveTemp(Descriptor), Config);

if (Result.HasValue())
{
    FTakeMetadata& Metadata = Result.GetValue();
    // 包含立体视频对的完整元数据
}
else
{
    EStereoVideoExtractionError Error = Result.GetError();
    // VideoANotFound / VideoBNotFound / UnsupportedVideoFormatA / UnsupportedVideoFormatB
    // VideoTypeMismatch / AudioFileNotFound / CalibrationFileNotFound / CalibrationFormatUnrecognized
}
```

### 进阶用法：检测标定格式

```cpp
using namespace UE::CaptureManager;

FString Format = DetectCalibrationFormat(TEXT("/path/to/calibration.json"));

if (Format == TEXT("opencv"))
{
    // 使用 OpenCV 标定解析器处理
}
else if (Format == TEXT("unreal"))
{
    // 使用 Unreal 标定解析器处理
}
else
{
    // 格式无法识别
}
```

### 进阶用法：文件类型判断工具

```cpp
using namespace UE::CaptureManager;

// 判断文件扩展名类型
bool bIsVideo = IsVideoExtension(TEXT("mp4"));     // true
bool bIsAudio = IsAudioExtension(TEXT("wav"));     // true
bool bIsImage = IsImageExtension(TEXT("png"));     // true
bool bIsUnknown = IsVideoExtension(TEXT("txt"));   // false

// 支持的视频格式: mp4, mov, avi, mkv, webm
// 支持的音频格式: wav, mp3, flac, m4a, aac
// 支持的图像格式: jpg, jpeg, png
```

### 进阶用法：从音频文件提取时码

```cpp
using namespace UE::CaptureManager;

FCaptureExtractAudioTimecode AudioExtractor(TEXT("/path/to/audio.wav"));

// 不指定帧率，自动检测
auto TimecodeResult = AudioExtractor.Extract();

// 指定帧率提取
FFrameRate TargetRate(30000, 1001);  // 29.97fps
auto TimecodeResultWithRate = AudioExtractor.Extract(TargetRate);

if (TimecodeResultWithRate.HasValue())
{
    FTimecodeInfo Info = TimecodeResultWithRate.GetValue();
    // 包含时码和时码率信息
}
```

## Demo 示例

以下示例演示如何提取单目视频的完整元数据信息，包括视频探测和音频时码提取：

**CaptureMetadataDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FCaptureMetadataDemo
{
public:
    /** 演示完整的视频元数据提取流程 */
    static void RunDemo(const FString& InVideoPath, const FString& InFFmpegPath = TEXT(""));
};
```

**CaptureMetadataDemo.cpp**
```cpp
#include "CaptureMetadataDemo.h"

#include "MonoVideoMetadataExtractor.h"
#include "CaptureManagerExtractionConfig.h"
#include "Utils/CaptureExtractTimecode.h"
#include "CaptureManagerFileExtensions.h"

void FCaptureMetadataDemo::RunDemo(const FString& InVideoPath, const FString& InFFmpegPath)
{
    using namespace UE::CaptureManager;

    // Step 1: 检查文件类型
    FString Extension = FPaths::GetExtension(InVideoPath);
    if (!IsVideoExtension(Extension))
    {
        UE_LOG(LogTemp, Error, TEXT("不支持的视频格式: %s"), *Extension);
        return;
    }

    // Step 2: 配置提取选项
    FExtractionConfig Config;
    if (!InFFmpegPath.IsEmpty())
    {
        Config.bUseFFprobe = true;
        Config.FFmpegPath = InFFmpegPath;
    }

    // Step 3: 探测视频技术信息
    TOptional<Private::FFProbeCommand> ProbeCommand;
    if (Config.bUseFFprobe)
    {
        ProbeCommand.Emplace(Config.FFmpegPath);
    }

    auto VideoInfoResult = FCaptureExtractVideoInfo::Create(InVideoPath, ProbeCommand);
    if (VideoInfoResult.HasValue())
    {
        const FCaptureExtractVideoInfo& Info = VideoInfoResult.GetValue();
        UE_LOG(LogTemp, Log, TEXT("帧率: %s"), *Info.GetFrameRate().ToString());
        UE_LOG(LogTemp, Log, TEXT("时码: %s"), *Info.GetTimecode().ToString());
        UE_LOG(LogTemp, Log, TEXT("包含音频: %s"), Info.ContainsAudio() ? TEXT("是") : TEXT("否"));
        
        if (Info.ContainsAudio())
        {
            UE_LOG(LogTemp, Log, TEXT("音频时长: %.2f 秒"), Info.GetAudioDurationSeconds());
        }
    }

    // Step 4: 提取完整 Take 元数据
    FMonoVideoDescriptor Descriptor;
    Descriptor.VideoFilePath = InVideoPath;
    Descriptor.Slate = FPaths::GetBaseFilename(InVideoPath);
    Descriptor.TakeNumber = 1;

    auto MetadataResult = ExtractMonoVideoMetadata(MoveTemp(Descriptor), Config);
    if (MetadataResult.HasValue())
    {
        const FTakeMetadata& Metadata = MetadataResult.GetValue();
        UE_LOG(LogTemp, Log, TEXT("Take 元数据提取成功"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Take 元数据提取失败"));
    }
}
```

## 模块依赖

由于未提供 Build.cs 完整内容，以下基于头文件中的类型引用推断：

| 模块 | 用途 |
|---|---|
| `CaptureManagerTakeMetadata` | 提供 `FTakeMetadata` 统一数据结构 |
| `MediaUtils` | 提供 `FFrameRate`、`FTimecode`、`EMediaOrientation` 等媒体类型 |
| `MediaAssets` | 提供 `UFileMediaSource` 基类 |
| `RenderCore` | 提供 `FImageWrapper` 相关图像处理能力 |
| `Json` | JSON 元数据文件解析 |

> 注：Core、CoreUObject、Engine 等标准依赖已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelled | 支持取消第三方编码器命令（音视频转换可中断） |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 补充模块迁移时遗漏的修复 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复事务 ID 数据竞争导致的偶发下载失败 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 SharedString |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增设备蓝图模块 |

### 维护评价

- **活跃维护**：插件创建于 2025 年 2 月，至今约 15 个月，最近一次更新在 2026 年 5 月 13 日（约 11 天前）
- 近期更新频率高（2 周内 5 次提交），包含功能增强（取消支持）、bug 修复（数据竞争）和重构
- 作为 Epic 虚拟制片工具链的核心组件，与 CaptureManagerEditor 和 CaptureManagerApp 紧密关联，将持续维护
- `EnabledByDefault=false` 表明这是一个按需加载的模块，需要在项目设置中手动启用
- ⚠️ **未发现单元测试文件**，建议在使用前充分验证
- **推荐使用**：作为 Epic 官方虚拟制片管线的标准组件，适合需要从多种采集设备导入 Take 数据的项目

## 相关链接

- [插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [CaptureMetadataExtraction 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureMetadataExtraction)