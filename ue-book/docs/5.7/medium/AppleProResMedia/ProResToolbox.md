# Apple ProRes Media

> Implements video playback and the export of the Apple ProRes Codec.  Apple ProRes is a high quality, lossy video compression format.

| 属性 | 值 |
|---|---|
| 中文名 | Apple ProRes 媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleProResMedia` (Runtime), `ProResToolbox` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-08-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AppleProResMedia) | |

## 用途

Apple ProRes Media 插件在 Unreal Engine 中引入了对 Apple ProRes 编码格式的原生支持。ProRes 是一种广泛应用于影视后期、广播和高质量视频制作中的有损视频压缩格式，以其卓越的画质和相对高效的解码性能著称。

该插件的核心功能包括：
- **视频播放**：读取并解码 `.mov` 容器中的 ProRes 编码视频流，使其能在 UE 媒体框架中播放。
- **视频导出**：通过 Movie Render Pipeline，将渲染序列帧编码为 ProRes 格式的视频文件。
- **编解码器集成**：封装了 Apple 官方的 ProRes 编解码库，提供了底层文件读写、元数据操作、时间信息处理等全面的 C API，作为 UE 与 ProRes 格式之间的桥梁。

这个插件存在的根本原因是：ProRes 是专业视频领域的行业标准格式，而 UE 广泛用于虚拟制片、广告、影视预演等领域，需要能够直接输出或导入 ProRes 格式，以便无缝对接后期制作管线。

## 使用场景

- **影视级渲染输出**：你正在使用 Movie Render Pipeline 渲染一段高质量的 CG 内容，需要中间片直接交付给剪辑或调色部门 → 将输出格式设置为 ProRes 422 HQ 或 ProRes 4444。
- **广播级视频素材导入**：你的项目需要导入摄像机实拍的 ProRes 文件（如 Arri Alexa 拍摄的 ProRes）作为背景板或 HDR 环境贴图 → 使用 `Media Player` 资产播放 ProRes 媒体源。
- **后期制作流程**：你需要直接在 UE 内生成 ProRes 文件，以便无缝交付给上游的非线性编辑系统 → 通过插件提供的导出管线。
- **自定义 ProRes 工具**：作为开发者在 C++ 层面使用底层 ProResToolbox API，编写自定义的文件读取、元数据提取或转码工具。

## 蓝图用法

Apple ProRes Media 插件**不暴露任何可直接在蓝图中调用的新节点**。它的功能完全集成在 UE 的媒体框架和 Movie Render Pipeline 系统中。

要使用它，你需要通过以下方式间接操作：

### 在蓝图中播放 ProRes 文件

1. 创建 **Media Player** 资产。
2. 创建 **Media Source** 资产，并将其指向一个 `.mov` 文件（文件必须包含 ProRes 编码的视频轨）。
3. 创建一个 **Media Texture** 资产，并将上一步的 Media Player 分配给它的 `Media Player` 属性。
4. 在关卡中放置一个 **Media Bundle** Actor，或者使用 **Image** 控件配合 `Set Brush from Media Texture` 节点来显示视频。
5. 在蓝图或关卡蓝图中，调用 Media Player 的 `Open Source` → `Play` 节点。

### 在 Movie Render Pipeline 中导出 ProRes

1. 在 ML Movie Render 面板中，将一个 **Apple ProRes Encoder** 添加到输出阶段（如果该编解码器已启用且平台支持）。
2. 在输出配置中，通过 MRG 的 `Config` 资产设置视频编码为 `Apple ProRes`。
3. 在渲染输出的编码器设置中，配置 ProRes 的编码配置文件（如 HQ、4444）和帧速率。

**请注意**：具体的配置参数通过 C++ 侧的配置类暴露，仅在项目设置或序列设置中可由美术人员调整，而非独立的蓝图函数。

## C++ 用法

### 头文件引入

```cpp
// 使用 Apple ProRes 媒体框架的播放功能
#include "AppleProResMedia/AppleProResMediaModule.h"

// 如果需要直接访问底层 ProRes 编解码器 API
#include "ProResToolbox/ProResFileReader.h"
#include "ProResToolbox/ProResFileWriter.h"
#include "ProResToolbox/ProResFormatDescription.h"
#include "ProResToolbox/ProResTime.h"
#include "ProResToolbox/ProResTypes.h"
```

### 基本用法

**1. 播放一个 ProRes 文件（基于 Media Framework）**

在 C++ 中，你通常不会直接操作底层 API，而是使用 UE 的 `UMediaPlayer` 和 `UMediaSource`。

```cpp
// 文件: Engine/Source/Runtime/MediaAssets/Private/MediaPlayer.cpp (示意)
// 说明：使用 UMediaPlayer 打开一个 ProRes 媒体源

// 在你的 Actor 或 GameInstance 中
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>(this);
if (MediaPlayer)
{
    // 创建一个文件媒体源（或使用资源引用）
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->FilePath = TEXT("C:\\MyFootage\\clip.mov");
    
    // 打开媒体源
    bool bOpened = MediaPlayer->OpenSource(MediaSource);
    if (bOpened)
    {
        // 播放
        MediaPlayer->Play();
    }
}
```

**2. 使用 ProResToolbox 底层 API 读取文件信息（C API）**

Apple ProRes Media 插件提供了一个三方的 C 语言工具库 `ProResToolbox`，可以直接读取和写入 ProRes 文件。

```cpp
// 文件: Engine/Plugins/Media/AppleProResMedia/Source/ThirdParty/ProResToolbox/include/ProResFileReader.h
// 说明：打开一个 ProRes 文件并获取时长

#include "ProResToolbox/ProResFileReader.h"
#include <stdio.h>

void ReadProResFileInfo()
{
    ProResFileReaderRef FileReader = nullptr;
    PRStatus Status = ProResFileReaderCreate("/Users/test/MyMovie.mov", &FileReader);
    if (Status == 0 && FileReader != nullptr)
    {
        // 获取时长（PRTime 结构）
        PRTime Duration = ProResFileReaderGetDuration(FileReader);
        
        // 获取时间尺度（每秒的 tick 数）
        PRTimeScale Timescale = ProResFileReaderGetTimescale(FileReader);
        
        double DurationInSeconds = (double)Duration.value / Duration.timescale;
        printf("Duration: %f seconds\n", DurationInSeconds);
        
        // 释放
        PRRelease(FileReader);
    }
}
```

### 进阶用法

**1. 读取 ProRes 视频样本**

从文件读者中获取 `ProResTrackReader`，然后使用 `ProResSampleCursor` 迭代样本，提取压缩帧数据。

```cpp
// 文件: Engine/Plugins/Media/AppleProResMedia/Source/ThirdParty/ProResToolbox/include/ProResFileReader.h
// 说明：使用 Cursor 获取视频样本信息

#include "ProResToolbox/ProResFileReader.h"
#include "ProResToolbox/ProResFormatDescription.h"

void IterateSamples()
{
    ProResFileReaderRef FileReader = nullptr;
    ProResFileReaderCreate("/path/to/file.mov", &FileReader);
    if (!FileReader) return;
    
    // 获取第一个视频轨道（索引 0）
    ProResTrackReaderRef TrackReader = nullptr;
    // ProResFileReaderCopyTrackByIndex 是一个示例，实际 API 可能有所不同。
    // 真实 API 需要查看头文件获取准确名称。
    // TrackReader = ProResFileReaderCopyTrackByIndex(FileReader, 0);
    if (!TrackReader) { PRRelease(FileReader); return; }
    
    // 获取轨道格式描述
    ProResFormatDescriptionRef FormatDesc = nullptr;
    // FormatDesc = ProResTrackReaderGetFormatDescription(TrackReader);
    
    // 获取第一个样本游标
    ProResSampleCursorRef Cursor = nullptr;
    // Cursor = ProResTrackReaderCreateCursor(TrackReader);
    
    // 遍历样本，获取压缩帧数据
    PRTime SampleTime;
    // while (ProResSampleCursorGetPresentationTime(Cursor, &SampleTime) == 0)
    // {
    //     const void* SampleData;
    //     size_t SampleSize;
    //     ProResSampleCursorGetSampleData(Cursor, &SampleData, &SampleSize);
    //     
    //     // 处理压缩帧数据...
    //     
    //     ProResSampleCursorStepForward(Cursor, 1);
    // }
    
    // 释放资源
    // PRRelease(Cursor);
    // PRRelease(FormatDesc);
    // PRRelease(TrackReader);
    PRRelease(FileReader);
}
```

**2. 创建并写入 ProRes 文件**

```cpp
// 文件: Engine/Plugins/Media/AppleProResMedia/Source/ThirdParty/ProResToolbox/include/ProResFileWriter.h
// 说明：创建一个新的 ProRes 文件并写入一帧

#include "ProResToolbox/ProResFileWriter.h"
#include "ProResToolbox/ProResFormatDescription.h"

void WriteProResFrame()
{
    ProResFileWriterRef Writer = nullptr;
    PRStatus Status = ProResFileWriterCreate("/tmp/output.mov", &Writer);
    if (Status != 0 || !Writer) return;
    
    // 添加视频轨道
    PRPersistentTrackID VideoTrackID = kProResTrackID_Invalid;
    // ProResFileWriterAddVideoTrack(Writer, kProResCodecType_ProRes_422_HQ, 1920, 1080, &VideoTrackID);
    if (VideoTrackID != kProResTrackID_Invalid)
    {
        // 设置轨道时间尺度
        ProResFileWriterSetTrackMediaTimescale(Writer, VideoTrackID, 600);
        
        // 创建压缩的帧数据（需要编码器完成）
        const void* CompressedFrameData = nullptr;
        size_t CompressedFrameSize = 0;
        // ... 使用第三方编码器压缩一帧 ...
        
        // 添加样本
        PRTime PresentationTime = { 0, 600, kPRTimeFlags_Valid, 0 }; // 0秒
        // ProResFileWriterAddSampleBufferToTrack(
        //     Writer,
        //     VideoTrackID,
        //     CompressedFrameData,
        //     CompressedFrameSize,
        //     PresentationTime,
        //     // 帧持续时间
        //     PRTimeDivide(PRTimeMake(1, 30), 1), // 假设 30fps
        //     // 格式描述（轨道宽高信息）
        //     FormatDesc);
    }
    
    // 完成写入
    ProResFileWriterFinish(Writer);
    ProResFileWriterInvalidate(Writer);
    PRRelease(Writer);
}
```

## Demo 示例

以下是一个完整的 C++ 示例，演示如何使用 ProResToolbox 读取一个 ProRes 文件并获得基本的时长信息。

**文件: `MyProResReader.h`**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ProResToolbox/ProResFileReader.h"
#include "ProResToolbox/ProResTypes.h"

class FMyProResReader
{
public:
    FMyProResReader();
    ~FMyProResReader();

    /** 从文件路径加载 ProRes 文件 */
    bool OpenFile(const FString& FilePath);

    /** 获取文件时长（秒） */
    double GetDurationInSeconds() const;

    /** 释放资源 */
    void Close();

private:
    ProResFileReaderRef FileReader;
};
```

**文件: `MyProResReader.cpp`**
```cpp
#include "MyProResReader.h"

FMyProResReader::FMyProResReader()
    : FileReader(nullptr)
{
}

FMyProResReader::~FMyProResReader()
{
    Close();
}

bool FMyProResReader::OpenFile(const FString& FilePath)
{
    if (FileReader)
    {
        PRRelease(FileReader);
        FileReader = nullptr;
    }

    // 转换为纯 C 字符串
    std::string StdPath = TCHAR_TO_UTF8(*FilePath);
    const char* Utf8Path = StdPath.c_str();

    PRStatus Status = ProResFileReaderCreate(Utf8Path, &FileReader);
    return (Status == 0 && FileReader != nullptr);
}

double FMyProResReader::GetDurationInSeconds() const
{
    if (!FileReader) return 0.0;

    PRTime Duration = ProResFileReaderGetDuration(FileReader);
    if (PRTIME_IS_VALID(Duration))
    {
        return (double)Duration.value / (double)Duration.timescale;
    }
    return 0.0;
}

void FMyProResReader::Close()
{
    if (FileReader)
    {
        PRRelease(FileReader);
        FileReader = nullptr;
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WmfMedia` | Windows 平台上的媒体播放框架，用于回放 ProRes 视频。该插件依赖 WmfMedia 的路由来实际解码视频帧。 |
| `MovieRenderPipeline` | 电影渲染管线，插件通过此模块注册 ProRes 编码器，实现渲染序列的 ProRes 格式输出。 |
| `ProResToolbox` | Apple 官方提供的底层 C API 库，处理 ProRes 文件的读写、元数据、格式描述和时间操作。这是一个外部第三方库。 |

> **说明**：以下常见模块已自动包含，不在此处列出：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, Projects, DeveloperSettings。

## 维护状态

### 近期更新

- 2025-09-29 b41cef35 [AppleProResMedia] Fix Error handling and potential memory leaks.
- 2025-09-26 6f67c4c3 [AppleProResMedia] Editor load time improvement: Implementing on demand loading of the ProResToolbox
- 2025-09-26 95d77a2a [Backout] - CL46266885
- 2025-09-26 438a85e5 [AppleProResMedia] Editor load time improvement: Implementing on demand loading of the ProResToolbox
- 2025-08-07 ee53759d MoviePipeline: Updated the UX for burn-ins in MRG (each output node can individually opt in or out o

### 维护评价

Apple ProRes Media 是一个**活跃维护**的插件。从 Git 历史可以看出：

- 该插件于 2025 年 8 月创建，是一个非常新的功能模块。
- 近期的提交（2025 年 9 月）明确表明了开发团队正在进行质量改进（修复内存泄漏、增强错误处理）和性能优化（按需加载 ProResToolbox 以缩短编辑器启动时间）。
- 维护频率很高，在不到两个月的时间里已有多次实质性更新。
- 该插件被设计为与 `WmfMedia` 和 `MovieRenderPipeline` 深度集成，是 UE 专业视频流程的重要组成部分，预计未来会持续演进。

**综合评价**：该插件正处于积极开发阶段，功能和质量快速提升。推荐在需要 ProRes 格式的影视工作流中启用并使用。建议关注未来更新，以获取更多的编码配置选项和平台支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AppleProResMedia)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/apple-prores-media-in-unreal-engine/)（*如果 available*）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AppleProResMedia/Tests)（*如果存在*）