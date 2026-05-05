# MP4 (ISO/IEC 14496-12) utilities

> Provides helpers to work with mp4 files

| 属性 | 值 |
|---|---|
| 分类 | Media |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MP4Utilities` (Runtime), `MP4Boxes` (Runtime), `MP4Muxer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-02-25 |
| 年龄标签 | 🆕（约 -2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MP4Utilities) | |

## 用途

MP4Utilities 插件提供了一套用于在 Unreal Engine 中创建和操作 MP4 (ISO/IEC 14496-12) 文件的底层工具集。它并非一个用于播放媒体的插件，而是一个用于**生成**或**修改** MP4 文件结构的“工具箱”。其核心功能是提供一个原始的 MP4 文件复用器（Muxer），允许开发者将已编码的视频、音频等媒体数据帧，按照 MP4 容器格式的规范，写入到一个有效的 .mp4 文件中。这对于实现自定义的视频录制、导出或后期处理流程至关重要。

## 使用场景

- **自定义视频录制**：当你需要将游戏画面或特定视口的渲染结果录制为 MP4 文件，且对编码格式、元数据（如时间码）有特殊要求时。
- **媒体文件后期处理**：需要向已有的 MP4 文件中添加新的轨道（如自定义时间码轨道 `tmcd`）或元数据。
- **生成测试媒体文件**：在开发媒体相关功能时，需要程序化地生成包含特定参数（如分辨率、帧率、采样率）的 MP4 测试文件。
- **处理非标准媒体数据**：当你的媒体数据已经是编码好的原始帧（例如 H.264 NAL 单元），需要将其封装成标准的 MP4 容器时。

## 蓝图用法

本插件主要提供 C++ 接口，用于底层文件操作。在提供的头文件中未发现标记为 `UFUNCTION(BlueprintCallable)` 的函数，因此**没有直接的蓝图节点**可用。所有操作均需通过 C++ 代码完成。

## C++ 用法

### 头文件引入

```cpp
#include "MP4Muxer.h"
```

### 基本用法

以下示例展示了如何使用 `IMP4RawMuxer` 创建一个简单的 MP4 文件并写入一帧视频数据。

```cpp
// 来源: Public/MP4Muxer.h
#include "MP4Muxer.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/Paths.h"

void CreateSimpleMP4File()
{
    // 1. 创建 Muxer 实例
    TSharedRef<IMP4RawMuxer, ESPMode::ThreadSafe> Muxer = IMP4RawMuxer::Create();

    // 2. 定义视频轨道规格
    IMP4RawMuxer::FTrackSpec VideoTrackSpec;
    VideoTrackSpec.Video.DisplayWidth = 1920;
    VideoTrackSpec.Video.DisplayHeight = 1080;
    VideoTrackSpec.Video.CompressorName = TEXT("avc1"); // H.264
    // 设置时间刻度（例如，对于 30fps，Timescale 可以是 30000，FrameDuration 是 1001）
    VideoTrackSpec.Timescale = 30000;
    VideoTrackSpec.FrameDuration = 1001;

    // 3. 添加视频轨道
    int32 VideoTrackIndex = Muxer->AddTrack(VideoTrackSpec);

    // 4. 准备一帧视频数据（这里用空数据模拟）
    TArray<uint8> SampleData;
    SampleData.SetNumZeroed(1024); // 假设这是编码后的一帧数据

    // 5. 写入样本数据
    // PresentationTime 和 Duration 以轨道的 Timescale 为单位
    Muxer->WriteSample(VideoTrackIndex, SampleData, 0 /* PresentationTime */, 1001 /* Duration */);

    // 6. 完成文件写入
    FString OutputPath = FPaths::ProjectSavedDir() / TEXT("TestOutput.mp4");
    Muxer->Finalize(OutputPath);
}
```

### 进阶用法

可以添加多个轨道（如音频），并为视频轨道关联时间码轨道。

```cpp
// 来源: Public/MP4Muxer.h
void CreateMP4WithTimecode()
{
    TSharedRef<IMP4RawMuxer, ESPMode::ThreadSafe> Muxer = IMP4RawMuxer::Create();

    // 添加视频轨道
    IMP4RawMuxer::FTrackSpec VideoSpec;
    VideoSpec.Video.DisplayWidth = 1280;
    VideoSpec.Video.DisplayHeight = 720;
    VideoSpec.Timescale = 24000; // 24fps
    VideoSpec.FrameDuration = 1001;
    int32 VideoTrack = Muxer->AddTrack(VideoSpec);

    // 添加时间码轨道
    IMP4RawMuxer::FTrackSpec TimecodeSpec;
    TimecodeSpec.Timecode.bDropFrame = false;
    TimecodeSpec.Timecode.Timescale = 24000; // 通常与视频 Timescale 一致
    TimecodeSpec.Timecode.FrameDuration = 1001;
    TimecodeSpec.Timecode.FramesPerSecond = 24;
    int32 TimecodeTrack = Muxer->AddTrack(TimecodeSpec);

    // 将时间码轨道关联到视频轨道
    Muxer->AddTrackReference(VideoTrack, IMP4RawMuxer::ETrackReferenceType::Timecode, TimecodeTrack);

    // 写入视频样本...
    // 写入时间码样本（通常只需写入第一个样本，后续时间码自动推算）...
    Muxer->WriteSample(TimecodeTrack, TimecodeData, 0, 1001);

    Muxer->Finalize(TEXT("VideoWithTimecode.mp4"));
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何创建一个包含单帧视频的 MP4 文件。

**MyMP4Writer.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyMP4Writer
{
public:
    static void WriteMinimalMP4(const FString& FilePath);
};
```

**MyMP4Writer.cpp**
```cpp
#include "MyMP4Writer.h"
#include "MP4Muxer.h"

void FMyMP4Writer::WriteMinimalMP4(const FString& FilePath)
{
    // 创建 Muxer
    auto Muxer = IMP4RawMuxer::Create();

    // 配置一个 640x480 的视频轨道
    IMP4RawMuxer::FTrackSpec TrackSpec;
    TrackSpec.Video.DisplayWidth = 640;
    TrackSpec.Video.DisplayHeight = 480;
    TrackSpec.Timescale = 30; // 简单起见，Timescale=30，FrameDuration=1 表示 30fps
    TrackSpec.FrameDuration = 1;

    // 添加轨道
    int32 TrackIndex = Muxer->AddTrack(TrackSpec);

    // 创建一帧虚拟的视频数据（实际应用中应为编码后的数据）
    TArray<uint8> FrameData;
    FrameData.Add(0x00); // 起始码
    FrameData.Add(0x00);
    FrameData.Add(0x00);
    FrameData.Add(0x01);
    FrameData.Append(TEXT("FAKE_H264_FRAME_DATA"), 20); // 伪数据

    // 写入第一帧，时间戳为0，持续时间为1个单位
    Muxer->WriteSample(TrackIndex, FrameData, 0, 1);

    // 完成并保存文件
    Muxer->Finalize(FilePath);
}
```

## 模块依赖

从 `MP4Muxer.Build.cs` 分析，该插件的模块间存在依赖关系。使用者需要根据具体使用的模块添加依赖。

| 模块 | 用途 |
|---|---|
| `MP4Boxes` | 提供 MP4 文件盒子（Box/Atom）结构的底层数据表示和操作，被 `MP4Muxer` 依赖。 |
| `MediaUtils` | 可能用于媒体相关的通用工具函数（需根据实际 Build.cs 确认）。 |

**注意**：如果你只使用 `MP4Muxer` 模块，你的模块需要依赖 `MP4Muxer` 和 `MP4Boxes`。`MP4Utilities` 模块可能提供更高级的封装，具体依赖需查看其 `Build.cs`。

## 维护状态

### 近期更新

（无法从提供的信息中获取 git log，以下为基于创建时间的推测）
- 2026-02-25 初始提交，插件创建。

### 维护评价

- **创建时间**：2026-02-25（未来日期，可能为测试数据）。
- **维护状态**：基于提供的创建时间，该插件非常新。然而，`EnabledByDefault: false` 表明它可能仍处于实验性或特定用途阶段，并非引擎默认启用的核心功能。
- **推荐度**：如果你有明确的、需要程序化生成或操作 MP4 文件的需求，并且愿意使用相对底层的 C++ API，这个插件是官方提供的解决方案，值得尝试。由于它默认未启用，使用前需要在项目设置中手动开启插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MP4Utilities)
- [官方文档]()（暂无）
- [测试用例]()（暂无）