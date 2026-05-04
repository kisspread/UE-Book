# Tiled Mipmap Video Player

> Framework for tiled-mipmap video (TMV) playback, includes transcoding tools.
Implemented using Advanced Professional Video (APV) codec.

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ApvMedia` (Runtime), `TmvMedia` (Runtime), `TmvMediaEditor` (Runtime), `TmvMediaMp4Utils` (Runtime), `TmvMediaShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TmvMedia) | |

## 用途

TmvMedia 是一个用于**分块 Mipmap 视频（Tiled-Mipmap Video, TMV）**播放和转码的完整框架。它基于 Epic 的 Advanced Professional Video (APV) 编解码器实现，解决的核心问题是：**如何高效地流式传输和解码超大分辨率视频，同时支持按需加载特定区域和 Mip 级别**。

传统视频解码需要将整帧解码到内存中，对于 8K+ 分辨率的视频来说内存开销巨大。TMV 通过将视频帧分割为小的 Tile 块，并为每个 Tile 生成多级 Mipmap，实现了：

- **按需解码**：只解码视口可见区域的 Tile，而非整帧
- **渐进式加载**：先加载低分辨率 Mip，再逐步加载高分辨率细节
- **GPU 友好**：支持 Tiled 内存布局，与 GPU 的 Tile-based 架构天然匹配
- **完整转码管线**：从任意视频源（媒体播放器、图片序列）转码为 TMV 格式

该插件默认禁用（`EnabledByDefault=false`），属于实验性功能，需要手动在插件设置中启用。

## 使用场景

- 你需要在虚拟制片（Virtual Production）场景中播放超大分辨率（8K+）的视频背景 → 使用 TMV 播放器按需加载可见区域
- 你需要将现有的视频素材转码为 TMV 格式以获得更好的流式播放性能 → 使用转码管线（Commandlet 或编辑器工具）
- 你需要将图片序列（EXR 等）转换为 TMV 容器格式 → 使用文件序列帧生产器
- 你需要在运行时通过 MediaPlayer 播放视频并逐帧捕获为 TMV → 使用 MediaPlayer 帧生产器
- 你需要自定义编解码器实现 → 通过工厂接口注册自定义的 Decoder/Encoder/Muxer/Demuxer

## 蓝图用法

TmvMedia 的核心功能主要面向 C++ 层，蓝图可访问的 API 有限。主要的蓝图暴露集中在转码任务管理方面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start` | 启动转码阶段 | `UTmvMediaTranscodeStage` |
| `RequestStop` | 请求停止转码阶段 | `UTmvMediaTranscodeStage` |
| `SetEncoderOptions` | 设置编码器选项 | `UTmvMediaFrameEncoder` |
| `ReceiveMips` | 接收 Mip 数据进行编码 | `UTmvMediaFrameEncoder` |
| `OpenStream` | 在 Muxer 中打开一个流 | `UTmvMediaContainerTranscodeMuxer` |
| `ReceiveAccessUnit` | 向 Muxer 发送编码后的访问单元 | `UTmvMediaContainerTranscodeMuxer` |
| `SetStreamTrackConfig` | 设置流的轨道配置 | `UTmvMediaContainerTranscodeMuxer` |

### 使用示例（蓝图描述）

TMV 的转码管线通过 `UTmvMediaTranscodeJob` 组织，典型的蓝图使用流程：

1. 创建一个 `UTmvMediaTranscodeJob` 对象
2. 配置 `FTmvMediaTranscodeJobSettings`（输入路径、输出路径、输出格式等）
3. 设置编码器选项（通过 `SetEncoderOptions`）
4. 调用 `Start` 启动转码
5. 通过 `ITmvMediaTranscodeJobManager` 监听任务状态变化（`OnTranscodeJobAdded` / `OnTranscodeJobRemoved` 委托）

对于播放端，TMV 通过标准的 UE Media Framework 集成，使用 `UMediaPlayer` + `UMediaTexture` 进行播放，内部通过 `FTmvMediaTextureSampleConverter` 处理分块 Mip 的转换。

## C++ 用法

### 头文件引入

```cpp
#include "ITmvMediaModule.h"
#include "TmvMediaFrameInfo.h"
#include "TmvMediaFrameColorInfo.h"
#include "Decoder/ITmvMediaDecoder.h"
#include "Encoder/ITmvMediaEncoder.h"
#include "Encoder/ITmvMediaMuxer.h"
#include "Decoder/ITmvMediaDemuxer.h"
#include "SampleConverter/TmvMediaTextureSampleConverter.h"
#include "SampleConverter/TmvMediaFrameMipBuffer.h"
#include "SampleConverter/TmvMediaFrameMipBufferPool.h"
```

### 基本用法 — 获取模块实例并注册工厂

```cpp
// 来源: Public/ITmvMediaModule.h

// 获取 TMV 模块实例
ITmvMediaModule* TmvModule = ITmvMediaModule::Get();
if (TmvModule)
{
    // 注册自定义的解码器工厂
    TSharedPtr<ITmvMediaDecoderFactory> MyDecoderFactory = MakeShared<FMyDecoderFactory>();
    TmvModule->RegisterDecoderFactory(MyDecoderFactory);

    // 注册自定义的编码器工厂
    TSharedPtr<ITmvMediaEncoderFactory> MyEncoderFactory = MakeShared<FMyEncoderFactory>();
    TmvModule->RegisterEncoderFactory(MyEncoderFactory);

    // 注册自定义的 Muxer 工厂
    TSharedPtr<ITmvMediaMuxerFactory> MyMuxerFactory = MakeShared<FMyMuxerFactory>();
    TmvModule->RegisterMuxerFactory(MyMuxerFactory);

    // 注册自定义的 Demuxer 工厂
    TSharedPtr<ITmvMediaDemuxerFactory> MyDemuxerFactory = MakeShared<FMyDemuxerFactory>();
    TmvModule->RegisterDemuxerFactory(MyDemuxerFactory);
}
```

### 基本用法 — 帧信息与颜色管理

```cpp
// 来源: Public/TmvMediaFrameInfo.h, Public/TmvMediaFrameColorInfo.h

// 构造帧 Mip 信息
FTmvMediaFrameMipInfo MipInfo;
MipInfo.Width = 3840;
MipInfo.Height = 2160;
MipInfo.NumMips = 1;
MipInfo.BufferLayout = ETmvMediaFrameBufferLayout::Tiled;
MipInfo.ColorModel = ETmvMediaFrameColorModel::YUV;

// 配置平面信息（例如 YUV 4:2:0 的 Y 平面）
FTmvMediaFramePlaneInfo YPlane;
YPlane.NumComponents = 1;
YPlane.BitDepth = 8;
YPlane.Type = ETmvMediaFrameComponentType::Int;
YPlane.Width = 3840;
YPlane.Height = 2160;
YPlane.ComponentLayout = ETmvMediaFrameComponentLayout::Packed;
YPlane.Stride = 3840;
MipInfo.Planes.Add(YPlane);

// 配置颜色信息
FTmvMediaFrameColorInfo ColorInfo;
ColorInfo.Encoding = UE::Color::EEncoding::sRGB;
ColorInfo.ColorSpace = UE::Color::EColorSpace::Rec709;
ColorInfo.YuvMatrix = ETmvMediaFrameColorMatrix::Rec709;
ColorInfo.YuvMatrixRange = ETmvMediaFrameColorMatrixRange::Limited;
```

### 基本用法 — 使用 Mip Buffer 池

```cpp
// 来源: Public/SampleConverter/TmvMediaFrameMipBufferPool.h

// 创建缓冲池
TSharedPtr<FTmvMediaFrameMipBufferPool> BufferPool = MakeShared<FTmvMediaFrameMipBufferPool>();

// 从池中获取适合指定 Mip 信息的缓冲区
FTmvMediaFrameMipBufferHandle MipBuffer = BufferPool->AcquireBuffer(MipInfo);

// 等待 GPU 分配完成
MipBuffer->WaitAllocation();

// 获取映射的 CPU 缓冲区指针
void* MappedData = MipBuffer->GetMappedBuffer();

// 获取特定组件的平面缓冲区
void* YPlaneBuffer = MipBuffer->GetPlaneBufferForComponent(0);

// 获取 Shader Resource View（用于 GPU 渲染）
FShaderResourceViewRHIRef SRV = MipBuffer->GetShaderResourceView(0);
```

### 进阶用法 — Demuxer 工作流

```cpp
// 来源: Public/Decoder/ITmvMediaDemuxer.h, Public/Decoder/ITmvMediaDemuxerFactory.h

// 从模块获取 Demuxer 工厂并创建实例
ITmvMediaModule* TmvModule = ITmvMediaModule::Get();
TArray<TWeakPtr<ITmvMediaDemuxerFactory>> DemuxerFactories;
TmvModule->GetDemuxerFactories(DemuxerFactories);

TSharedPtr<ITmvMediaDemuxer> Demuxer;
for (auto& FactoryWeak : DemuxerFactories)
{
    if (TSharedPtr<ITmvMediaDemuxerFactory> Factory = FactoryWeak.Pin())
    {
        TArray<FString> Formats = Factory->GetSupportedContainerFormats();
        if (Formats.Contains(TEXT("mp4")))
        {
            Demuxer = Factory->CreateDemuxer();
            break;
        }
    }
}

if (Demuxer)
{
    // 打开容器文件
    ETmvMediaContainerResult Result = Demuxer->OpenFile(TEXT("/Game/Videos/input.mp4"));
    
    if (Result == ETmvMediaContainerResult::Success)
    {
        // 枚举轨道
        int32 TrackCount = Demuxer->GetTrackCount();
        for (int32 i = 0; i < TrackCount; ++i)
        {
            FTmvMediaDemuxerTrackInfo TrackInfo;
            Demuxer->GetTrackInfo(i, TrackInfo);
            
            if (TrackInfo.TrackType == ETmvMediaTrackType::Video)
            {
                // 逐个读取样本
                FTmvMediaDemuxerSample Sample;
                while (Demuxer->ReadSample(i, Sample) == ETmvMediaContainerResult::Success)
                {
                    // Sample.Data 包含编码后的访问单元
                    // Sample.PTS / Sample.DTS 包含时间戳
                    // 处理样本...
                }
            }
        }
    }
}
```

### 进阶用法 — Muxer 工作流

```cpp
// 来源: Public/Encoder/ITmvMediaMuxer.h, Public/Encoder/ITmvMediaMuxerFactory.h

// 创建 Muxer
ITmvMediaModule* TmvModule = ITmvMediaModule::Get();
TArray<TWeakPtr<ITmvMediaMuxerFactory>> MuxerFactories;
TmvModule->GetMuxerFactories(MuxerFactories);

TSharedPtr<ITmvMediaMuxer> Muxer;
for (auto& FactoryWeak : MuxerFactories)
{
    if (TSharedPtr<ITmvMediaMuxerFactory> Factory = FactoryWeak.Pin())
    {
        if (Factory->GetSupportedContainerFormats().Contains(TEXT("tmv")))
        {
            Muxer = Factory->CreateMuxer();
            break;
        }
    }
}

if (Muxer)
{
    // 配置输出
    FTmvMediaMuxerConfig Config;
    Config.OutputFilename = TEXT("/Game/Videos/output.tmv");
    Config.OutputMode = FTmvMediaMuxerConfig::EOutputMode::WebOptimized;
    Config.InterleaveDuration = FTimespan::FromMilliseconds(500);
    Muxer->Configure(Config);

    // 添加视频轨道
    FTmvMediaMuxerTrackConfig TrackConfig;
    TrackConfig.TrackType = ETmvMediaTrackType::Video;
    TrackConfig.SampleEntryFormat = 'apv1';  // APV codec FourCC
    TrackConfig.Timescale = 30000;
    TrackConfig.ConstantSampleDuration = 1001;  // ~29.97fps
    TrackConfig.DisplayWidth = 3840;
    TrackConfig.DisplayHeight = 2160;
    TrackConfig.bIsAllKeyframes = true;
    
    int32 TrackIndex = Muxer->AddTrack(TrackConfig);

    // 写入样本
    FTmvMediaMuxerSample Sample;
    Sample.Data = EncodedData;  // 编码后的访问单元数据
    Sample.Duration = 1001;
    Sample.DTS = FrameIndex * 1001;
    Sample.PTS = FrameIndex * 1001;
    Sample.SampleNumber = FrameIndex;
    Sample.bIsKeyframe = true;
    
    Muxer->WriteSample(TrackIndex, Sample);

    // 完成后关闭
    Muxer->Close();
}
```

### 进阶用法 — 使用 Commandlet 进行无头转码

```cpp
// 来源: Private/Commandlets/TmvMediaTranscodeCommandlet.h
// 通过命令行调用，无需编写 C++ 代码

// 基本用法：从命令行参数构建单个转码任务
// UnrealEditor.exe MyProject.uproject -run=TmvMediaTranscode -AllowCommandletRendering ^
//   -Encoder=apv ^
//   -InputPath=/Game/Videos/input.mp4 ^
//   -OutputPath=/Game/Videos/output.tmv ^
//   -OutputFormat=Container

// 使用预定义的任务列表
// UnrealEditor.exe MyProject.uproject -run=TmvMediaTranscode -AllowCommandletRendering ^
//   -JobList=/path/to/joblist.json

// 带超时和调试选项
// UnrealEditor.exe MyProject.uproject -run=TmvMediaTranscode -AllowCommandletRendering ^
//   -Encoder=apv ^
//   -InputPath=/Game/Videos/input.mp4 ^
//   -OutputPath=/Game/Videos/output ^
//   -OutputFormat=FileSequence ^
//   -JobTimeoutSeconds=300 ^
//   -Debug ^
//   -LoadModule="ApvMedia,TmvMediaMp4Utils"
```

## Demo 示例

以下示例展示如何创建一个自定义的 TMV 解码器工厂并注册到模块中：

### MyTmvDecoderFactory.h

```cpp
#pragma once

#include "Decoder/ITmvMediaDecoderFactory.h"
#include "Decoder/ITmvMediaDecoder.h"
#include "Decoder/ITmvMediaDemuxer.h"

class FMyTmvDecoder : public ITmvMediaDecoder
{
public:
    // 实现解码接口
    virtual ETmvMediaDecoderResult DecodeMip(
        const FTmvMediaDecoderMipRequest& InRequest) override
    {
        // 从访问单元读取数据并解码到 MipBuffer
        // InRequest.MipInfo - 目标 Mip 的内存布局信息
        // InRequest.TileRegions - 需要解码的 Tile 区域
        // InRequest.MipBuffer - 目标缓冲区句柄
        
        // ... 解码逻辑 ...
        
        InRequest.OutResult = ETmvMediaDecoderResult::Success;
        InRequest.OutNumTilesDecoded = InRequest.TileRegions.Num();
        return ETmvMediaDecoderResult::Success;
    }
};

class FMyTmvDecoderFactory : public ITmvMediaDecoderFactory
{
public:
    virtual const FString& GetName() const override
    {
        static FString Name = TEXT("MyCustomDecoder");
        return Name;
    }

    virtual TArray<FString> GetSupportedFileExtensions() const override
    {
        return { TEXT("tmv") };
    }

    virtual int32 SupportsFormat(
        const FString& InCodecFormat,
        const TMap<FString, FVariant>& InOptions) const override
    {
        // 返回优先级，0 表示不支持
        if (InCodecFormat == TEXT("mycv"))
        {
            return 10; // 优先级
        }
        return 0;
    }

    virtual void GetParserOptions(TMap<FString, FVariant>& OutOptions) const override {}
    
    virtual TSharedPtr<ITmvMediaParser, ESPMode::ThreadSafe> CreateParser(
        const FString& InCodecFormat,
        const TMap<FString, FVariant>& InOptions) override
    {
        // 创建对应的解析器
        return nullptr;
    }

    virtual void GetDecoderOptions(TMap<FString, FVariant>& OutOptions) const override {}

    virtual TSharedPtr<ITmvMediaDecoder, ESPMode::ThreadSafe> CreateDecoder(
        const FString& InCodecFormat,
        const TMap<FString, FVariant>& InOptions) override
    {
        return MakeShared<FMyTmvDecoder>();
    }
};
```

### MyTmvDecoderFactory.cpp

```cpp
#include "MyTmvDecoderFactory.h"
#include "ITmvMediaModule.h"

void RegisterMyDecoderFactory()
{
    ITmvMediaModule* TmvModule = ITmvMediaModule::Get();
    if (TmvModule)
    {
        auto Factory = MakeShared<FMyTmvDecoderFactory>();
        TmvModule->RegisterDecoderFactory(Factory);
    }
}

void UnregisterMyDecoderFactory()
{
    ITmvMediaModule* TmvModule = ITmvMediaModule::Get();
    if (TmvModule)
    {
        auto Factory = MakeShared<FMyTmvDecoderFactory>();
        TmvModule->UnregisterDecoderFactory(Factory);
    }
}
```

## 模块依赖

TmvMedia 模块本身的 Build.cs 依赖信息未完整提供，但从插件整体结构可以推断以下独特依赖：

| 模块 | 用途 |
|---|---|
| `UEOpenAPV` | APV 编解码器的底层实现（ApvMedia 模块依赖） |
| `ImageCore` | 图片文件序列的读取（用于文件序列帧生产器） |
| `MediaAssets` | UMediaPlayer / UMediaTexture / UMediaSource 等媒体资产类 |
| `MediaUtils` | 媒体工具函数 |
| `RenderCore` | RDG 渲染管线、GPU 读回等 |
| `RHI` | RHI 资源管理（纹理、缓冲区、SRV） |
| `ColorManagement` | 颜色空间转换（sRGB、Rec709、Rec2020、PQ/HLG） |
| `StructUtils` | TInstancedStruct 支持（编码器选项的多态） |

## 维护状态

### 近期更新

- 2026-04-24 `c7065a2f` [Tmv Media] Transcoding Commandlet
- 2026-04-23 `efcad028` HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the
- 2026-04-22 `323ab3ea` [TmvMediaUtils] Addressing Ux feedback for the MRG node
- 2026-04-20 `4677c750` [TmvMedia] Adding start timecode support to tmv container
- 2026-04-18 `1a28370d` [TmvMediaUtils] New version of the Movie Render Graph Tmv Encoder node.

> 注：该插件创建于 2026-04-18，属于全新提交的实验性插件，尚无历史更新记录。

### 维护评价

- **创建时间**：2026-04-18，全新插件
- **实验性状态**：`EnabledByDefault=false`，需要手动启用
- **代码规模**：152 个源文件，5 个模块，架构完整且设计成熟
- **架构质量**：采用工厂模式实现高度可扩展的编解码器管线，支持自定义 Decoder/Encoder/Muxer/Demuxer
- **已知限制**：
  - 默认禁用，属于实验性功能
  - 主要面向 APV 编解码器，其他编解码器需要自行实现工厂
  - `FTmvMediaFrameMipImageBuffer` 不支持 R8/R16 格式（注释中明确说明）
  - 部分功能标记为 TMP（临时实现），如 `GetFilename()` 和 `GetUnderlyingArchive()`
- **推荐程度**：如果你需要处理超大分辨率视频的流式播放或转码，这是官方提供的实验性解决方案。但由于是实验性插件，API 可能在后续版本中发生变化。建议在虚拟制片或影视级渲染管线中评估使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TmvMedia)
- [官方文档]()（暂无）