# Tiled Mipmap Video Player

> Framework for tiled-mipmap video (TMV) playback, includes transcoding tools.
> Implemented using Advanced Professional Video (APV) codec.

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ApvMedia` (Runtime), `TmvMedia` (Runtime), `TmvMediaEditor` (Runtime), `TmvMediaMp4Utils` (Runtime), `TmvMediaShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TmvMedia) | |

## 用途

TmvMedia 插件为 Unreal Engine 提供了一套用于播放和转码 **Tiled Mipmap Video (TMV)** 格式视频的框架。TMV 是一种特殊的视频格式，其核心特点是将视频帧数据组织成“分块”和“多级渐进纹理（Mipmap）”的结构。这种结构使得视频播放器可以按需加载和解码视频的特定区域或特定分辨率层级，从而在需要高质量局部细节（如虚拟制片中的 LED 墙面）或进行流式传输时，显著优化内存占用和带宽使用。

该插件的实现基于 **Advanced Professional Video (APV)** 编解码器，这是一种为专业视频工作流设计的高性能编解码器。插件不仅包含运行时播放器，还提供了用于将常规视频转码为 TMV 格式的工具链。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙面播放背景视频时，TMV 格式允许摄像机只解码当前视野所覆盖的视频区域，极大节省 GPU 内存和解码带宽。
- **高质量视频流式传输**：对于需要高分辨率但观看区域有限的应用（如全景视频中的焦点区域），TMV 可以实现高效的自适应码流。
- **视频资产预处理**：在项目打包前，使用插件提供的转码工具将标准视频（如 MP4）转换为优化的 TMV 格式，以提升运行时性能。
- **需要精确时间码同步的专业工作流**：插件支持在 MP4 容器中读取和写入起始时间码，满足影视后期制作的同步需求。

## 蓝图用法

由于提供的源码主要为底层解复用/复用器实现，蓝图接口通常封装在 `TmvMedia` 或 `TmvMediaEditor` 模块中。基于常见的媒体播放器模式，可能的蓝图节点包括：

### 核心节点（推测）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个媒体源（如文件路径或 URL） | `UMediaPlayer` |
| `Play` | 开始播放已打开的媒体 | `UMediaPlayer` |
| `Pause` | 暂停播放 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间点 | `UMediaPlayer` |
| `Get Duration` | 获取视频总时长 | `UMediaPlayer` |
| `Get Time` | 获取当前播放时间 | `UMediaPlayer` |

*注：具体节点名称和所属类需参考 `TmvMedia` 模块中封装的 `UMediaPlayer` 子类或相关蓝图函数库。*

### 使用示例（蓝图描述）

1.  **创建媒体播放器**：在蓝图中创建一个 `Media Player` 资产，其类型选择为 TmvMedia 提供的播放器。
2.  **打开视频文件**：使用 `Open Source` 节点，将一个 `.tmv` 或 `.mp4` 文件路径作为 `Media Source` 输入。
3.  **连接到媒体纹理**：将 `Media Player` 的输出连接到一个 `Media Texture` 资产，再将该纹理应用到材质或 UI 上。
4.  **控制播放**：通过 `Play`、`Pause`、`Seek` 等节点控制视频播放流程。

## C++ 用法

### 头文件引入

```cpp
// 使用 MP4 解复用器
#include "TmvMediaMp4Utils/TmvMediaMp4Demuxer.h"
// 使用 MP4 复用器
#include "TmvMediaMp4Utils/TmvMediaMp4Muxer.h"
```

### 基本用法

以下示例展示了如何使用 `FTmvMediaMp4Demuxer` 读取一个 MP4 文件的基本信息和样本。
（基于 `Private/TmvMediaMp4Demuxer.h` 接口推断）

```cpp
#include "TmvMediaMp4Utils/TmvMediaMp4Demuxer.h"

void ReadMp4File(const FString& FilePath)
{
    // 1. 创建解复用器实例
    TSharedPtr<UE::TmvMedia::FTmvMediaMp4Demuxer> Demuxer = MakeShared<UE::TmvMedia::FTmvMediaMp4Demuxer>();

    // 2. 打开文件
    UE::TmvMedia::ETmvMediaContainerResult Result = Demuxer->OpenFile(FilePath);
    if (Result != UE::TmvMedia::ETmvMediaContainerResult::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open MP4 file: %s"), *Demuxer->GetLastError());
        return;
    }

    // 3. 获取轨道信息
    int32 TrackCount = Demuxer->GetTrackCount();
    UE_LOG(LogTemp, Log, TEXT("Found %d tracks."), TrackCount);

    for (int32 i = 0; i < TrackCount; ++i)
    {
        UE::TmvMedia::FTmvMediaDemuxerTrackInfo TrackInfo;
        if (Demuxer->GetTrackInfo(i, TrackInfo) == UE::TmvMedia::ETmvMediaContainerResult::Success)
        {
            UE_LOG(LogTemp, Log, TEXT("Track %d: Type=%d, Codec=%s"), i, (int32)TrackInfo.TrackType, *TrackInfo.CodecName);
        }
    }

    // 4. 读取第一个视频轨道的第一个样本
    if (TrackCount > 0)
    {
        UE::TmvMedia::FTmvMediaDemuxerSample Sample;
        // 假设第一个轨道是视频轨道
        if (Demuxer->ReadSample(0, Sample) == UE::TmvMedia::ETmvMediaContainerResult::Success)
        {
            UE_LOG(LogTemp, Log, TEXT("Read sample: Size=%d, Time=%s"), Sample.Data.Num(), *Sample.Time.ToString());
            // Sample.Data 中包含了压缩的视频帧数据
        }
    }

    // 5. 关闭文件（析构函数也会自动调用）
    Demuxer->Close();
}
```

### 进阶用法

结合解复用器和复用器，可以实现视频流的转封装或简单处理。

```cpp
#include "TmvMediaMp4Utils/TmvMediaMp4Demuxer.h"
#include "TmvMediaMp4Utils/TmvMediaMp4Muxer.h"

void RemuxMp4(const FString& InputPath, const FString& OutputPath)
{
    // 创建解复用器和复用器
    auto Demuxer = MakeShared<UE::TmvMedia::FTmvMediaMp4Demuxer>();
    auto Muxer = MakeShared<UE::TmvMedia::FTmvMediaMp4Muxer>();

    // 打开输入文件
    if (Demuxer->OpenFile(InputPath) != UE::TmvMedia::ETmvMediaContainerResult::Success)
    {
        return;
    }

    // 配置复用器
    UE::TmvMedia::FTmvMediaMuxerConfig MuxerConfig;
    MuxerConfig.OutputPath = OutputPath;
    if (Muxer->Configure(MuxerConfig) != UE::TmvMedia::ETmvMediaContainerResult::Success)
    {
        return;
    }

    // 为输入文件的每个轨道在输出文件中添加对应轨道
    for (int32 i = 0; i < Demuxer->GetTrackCount(); ++i)
    {
        UE::TmvMedia::FTmvMediaDemuxerTrackInfo TrackInfo;
        Demuxer->GetTrackInfo(i, TrackInfo);

        UE::TmvMedia::FTmvMediaMuxerTrackConfig TrackConfig;
        TrackConfig.TrackType = TrackInfo.TrackType;
        TrackConfig.CodecName = TrackInfo.CodecName;
        // ... 设置其他轨道参数
        Muxer->AddTrack(TrackConfig);
    }

    // 启动复用器（需要提供样本请求回调）
    Muxer->Start(
        [&](int32 TrackIndex) -> TOptional<UE::TmvMedia::FTmvMediaMuxerSample>
        {
            // 从解复用器读取样本
            UE::TmvMedia::FTmvMediaDemuxerSample DemuxSample;
            if (Demuxer->ReadSample(TrackIndex, DemuxSample) == UE::TmvMedia::ETmvMediaContainerResult::Success)
            {
                UE::TmvMedia::FTmvMediaMuxerSample MuxSample;
                MuxSample.Data = DemuxSample.Data;
                MuxSample.Time = DemuxSample.Time;
                MuxSample.Duration = DemuxSample.Duration;
                return MuxSample;
            }
            return {}; // 没有更多样本
        },
        [](UE::TmvMedia::ETmvMediaContainerResult Status, const FString& Message)
        {
            UE_LOG(LogTemp, Warning, TEXT("Muxer status: %d - %s"), (int32)Status, *Message);
        }
    );

    // 等待完成或循环处理直到结束...
    // Muxer->Finalize();
}
```

## Demo 示例

一个最小的 MP4 文件信息读取示例。

**TmvMediaDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FTmvMediaDemo
{
public:
    static void PrintMp4Info(const FString& FilePath);
};
```

**TmvMediaDemo.cpp**
```cpp
#include "TmvMediaDemo.h"
#include "TmvMediaMp4Utils/TmvMediaMp4Demuxer.h"

void FTmvMediaDemo::PrintMp4Info(const FString& FilePath)
{
    using namespace UE::TmvMedia;

    TSharedPtr<FTmvMediaMp4Demuxer> Demuxer = MakeShared<FTmvMediaMp4Demuxer>();

    if (Demuxer->OpenFile(FilePath) != ETmvMediaContainerResult::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("无法打开文件: %s. 错误: %s"), *FilePath, *Demuxer->GetLastError());
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("=== MP4 文件信息: %s ==="), *FilePath);
    UE_LOG(LogTemp, Log, TEXT("轨道数量: %d"), Demuxer->GetTrackCount());

    for (int32 i = 0; i < Demuxer->GetTrackCount(); ++i)
    {
        FTmvMediaDemuxerTrackInfo Info;
        if (Demuxer->GetTrackInfo(i, Info) == ETmvMediaContainerResult::Success)
        {
            UE_LOG(LogTemp, Log, TEXT("  轨道 %d:"), i);
            UE_LOG(LogTemp, Log, TEXT("    类型: %s"), Info.TrackType == ETmvMediaTrackType::Video ? TEXT("视频") : TEXT("音频"));
            UE_LOG(LogTemp, Log, TEXT("    编解码器: %s"), *Info.CodecName);
            if (Info.TrackType == ETmvMediaTrackType::Video)
            {
                UE_LOG(LogTemp, Log, TEXT("    分辨率: %d x %d"), Info.VideoResolution.X, Info.VideoResolution.Y);
            }
        }
    }

    // 尝试获取起始时间码
    TOptional<FString> Timecode = Demuxer->GetStartTimecode();
    if (Timecode.IsSet())
    {
        UE_LOG(LogTemp, Log, TEXT("起始时间码: %s"), *Timecode.GetValue());
    }

    Demuxer->Close();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UEOpenAPV` | APV 编解码器的核心实现库，`ApvMedia` 模块依赖它进行视频编解码。 |
| `MP4Muxer` | 底层的 MP4 容器复用器库，`TmvMediaMp4Utils` 模块依赖它来封装 MP4 文件。 |
| `MediaUtils` | UE 内置的媒体工具模块，提供媒体框架的基础类。 |
| `RenderCore` | 用于与渲染线程交互和处理 GPU 资源，`TmvMediaShaders` 模块依赖它。 |

## 维护状态

### 近期更新

- 2026-04-24 `c7065a2f` [Tmv Media] Transcoding Commandlet
- 2026-04-23 `efcad028` HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the
- 2026-04-22 `323ab3ea` [TmvMediaUtils] Addressing Ux feedback for the MRG node
- 2026-04-20 `4677c750` [TmvMedia] Adding start timecode support to tmv container
- 2026-04-18 `1a28370d` [TmvMediaUtils] New version of the Movie Render Graph Tmv Encoder node.

### 维护评价

- **创建时间**：标记为 2026 年，这表明该插件可能是为未来引擎版本（如 UE 5.8 或 6.0）开发的新功能，目前处于**实验性或预发布阶段**。
- **启用状态**：`EnabledByDefault: false` 明确表示这是一个需要用户手动启用的实验性功能。
- **模块结构**：包含 5 个模块，结构清晰，涵盖了编解码器（ApvMedia）、核心播放框架（TmvMedia）、编辑器工具（TmvMediaEditor）、容器处理（TmvMediaMp4Utils）和着色器（TmvMediaShaders），表明这是一个功能完整但复杂的系统。
- **综合评价**：这是一个**前沿的、实验性的**媒体框架。由于其依赖于特定的 APV 编解码器和 TMV 格式，目前可能仅适用于特定的专业工作流（如 Epic 自己的虚拟制片项目）。对于普通开发者，建议等待其正式发布并拥有更完善的文档和示例后再考虑使用。在当前阶段，它主要面向引擎开发者和高级技术美术进行研究和集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TmvMedia)
- 官方文档：暂无
- 测试用例：未在提供的路径中发现，可能位于 `Engine/Tests/` 目录下或尚未公开。