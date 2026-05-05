# Capture Manager Media RW

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（示例设备实现） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

CaptureManagerMediaRW 是 Capture Manager 插件的**媒体读写抽象层**，为虚拟制片中的捕获数据处理提供统一的 I/O 接口。

该模块解决的核心问题：不同捕获设备（如 iPhone LiDAR、立体相机阵列等）输出的媒体数据格式各异（音频、视频、标定数据），需要一个统一的抽象层来：
- **读取**多种格式的音频、视频和相机标定文件
- **写入**转换后的媒体数据到指定格式
- **转换**像素格式（如 YUV → BGRA、YUV → Mono）
- 通过**工厂模式**支持按格式动态创建对应的 Reader/Writer

本模块是整个 Capture Manager 管线的数据 I/O 基础设施，被上游的 `CaptureDataConverter` 和 `CaptureManagerPipeline` 等模块依赖。

## 使用场景

- 你在构建虚拟制片管线，需要从 iPhone/专业相机读取捕获数据 → 用 MediaRWManager 创建对应的 Reader
- 你需要将捕获的视频帧从 YUV 格式转换为 BGRA 用于 UE 纹理 → 用 MediaPixelFormatConversions 工具函数
- 你要实现自定义的媒体格式支持 → 实现 IAudioReaderFactory/IVideoReaderFactory 接口并注册到 MediaRWManager
- 你需要将处理后的音频/图像/标定数据写入磁盘 → 用 MediaRWManager 创建对应的 Writer

## 蓝图用法

本模块为纯 C++ Runtime 模块，**不暴露 BlueprintCallable 接口**。所有 API 均为 C++ 接口，供其他模块在代码中调用。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManagerMediaRWModule.h"
#include "MediaRWManager.h"
#include "IMediaReader.h"
#include "IMediaWriter.h"
#include "MediaSample.h"
#include "Utils/MediaPixelFormatConversions.h"
```

### 基本用法 — 获取 MediaRWManager 并创建 Reader

```cpp
// 获取模块单例中的 MediaRWManager
FCaptureManagerMediaRWModule& MediaRWModule = FModuleManager::GetModuleChecked<FCaptureManagerMediaRWModule>("CaptureManagerMediaRW");
FMediaRWManager& RWManager = MediaRWModule.Get();

// 根据文件路径自动检测格式并创建视频 Reader
TValueOrError<TUniquePtr<IVideoReader>, FText> VideoReaderResult = RWManager.CreateVideoReader(TEXT("/path/to/video.mp4"));
if (VideoReaderResult.HasValue())
{
    TUniquePtr<IVideoReader> VideoReader = VideoReaderResult.GetValue();
    
    // 打开文件
    TOptional<FText> Error = VideoReader->Open(TEXT("/path/to/video.mp4"));
    if (!Error.IsSet())
    {
        // 逐帧读取
        while (true)
        {
            TValueOrError<TUniquePtr<UE::CaptureManager::FMediaTextureSample>, FText> SampleResult = VideoReader->Next();
            if (!SampleResult.HasValue())
                break; // 读取完毕或出错
            
            TUniquePtr<UE::CaptureManager::FMediaTextureSample> Sample = SampleResult.GetValue();
            // 处理 Sample->Buffer, Sample->Dimensions 等
        }
        
        VideoReader->Close();
    }
}
```

### 基本用法 — 创建 Writer 写入数据

```cpp
FMediaRWManager& RWManager = /* ... */;

// 创建图像 Writer（指定目录、文件名、格式）
TValueOrError<TUniquePtr<IImageWriter>, FText> WriterResult = RWManager.CreateImageWriter(
    TEXT("/output/dir"),
    TEXT("frame"),
    TEXT("png")
);

if (WriterResult.HasValue())
{
    TUniquePtr<IImageWriter> ImageWriter = WriterResult.GetValue();
    
    // 写入纹理样本
    UE::CaptureManager::FMediaTextureSample Sample;
    Sample.Buffer = /* ... */;
    Sample.Dimensions = FIntPoint(1920, 1080);
    Sample.CurrentFormat = UE::CaptureManager::EMediaTexturePixelFormat::U8_BGRA;
    
    ImageWriter->Append(&Sample);
    ImageWriter->Close();
}
```

### 基本用法 — 音频读写

```cpp
FMediaRWManager& RWManager = /* ... */;

// 创建音频 Reader
TValueOrError<TUniquePtr<IAudioReader>, FText> AudioReaderResult = RWManager.CreateAudioReader(TEXT("/path/to/audio.wav"));
if (AudioReaderResult.HasValue())
{
    TUniquePtr<IAudioReader> AudioReader = AudioReaderResult.GetValue();
    AudioReader->Open(TEXT("/path/to/audio.wav"));
    
    // 查询音频属性
    FTimespan Duration = AudioReader->GetDuration();
    EMediaAudioSampleFormat Format = AudioReader->GetSampleFormat();
    UE::CaptureManager::ESampleRate Rate = AudioReader->GetSampleRate();
    uint32 Channels = AudioReader->GetNumChannels();
    
    // 逐块读取
    TValueOrError<TUniquePtr<UE::CaptureManager::FMediaAudioSample>, FText> SampleResult = AudioReader->Next();
    if (SampleResult.HasValue())
    {
        UE::CaptureManager::FMediaAudioSample* AudioSample = SampleResult.GetValue().Get();
        // 处理 AudioSample->Buffer, AudioSample->Frames 等
    }
    
    AudioReader->Close();
}

// 创建音频 Writer
TValueOrError<TUniquePtr<IAudioWriter>, FText> AudioWriterResult = RWManager.CreateAudioWriter(
    TEXT("/output/dir"),
    TEXT("output"),
    TEXT("wav")
);

if (AudioWriterResult.HasValue())
{
    TUniquePtr<IAudioWriter> AudioWriter = AudioWriterResult.GetValue();
    
    // 配置音频参数
    AudioWriter->Configure(
        UE::CaptureManager::ESampleRate::SR_48000Hz,
        2,  // 双声道
        EMediaAudioSampleFormat::Int16
    );
    
    // 写入音频样本
    UE::CaptureManager::FMediaAudioSample AudioSample;
    AudioSample.Buffer = /* ... */;
    AudioSample.SampleRate = UE::CaptureManager::ESampleRate::SR_48000Hz;
    AudioSample.Channels = 2;
    
    AudioWriter->Append(&AudioSample);
    AudioWriter->Close();
}
```

### 进阶用法 — 像素格式转换

```cpp
#include "Utils/MediaPixelFormatConversions.h"

// 假设从 Reader 获取了一个 YUV 格式的纹理样本
TUniquePtr<UE::CaptureManager::FMediaTextureSample> YUVSample = /* ... */;

// YUV 转 BGRA（返回 uint8 数组）
TArray<uint8> BGRAData = UE::CaptureManager::ConvertI420ToBGRA(YUVSample.Get());

// YUV 转 Mono（灰度）
TArray<uint8> MonoData = UE::CaptureManager::ConvertYUVToMono(YUVSample.Get(), /* bScaleRange */ true);

// NV12 转 BGRA
TArray<uint8> NV12ToBGRA = UE::CaptureManager::ConvertNV12ToBGRA(YUVSample.Get());

// YUY2 转 BGRA
TArray<uint8> YUY2ToBGRA = UE::CaptureManager::ConvertYUY2ToBGRA(YUVSample.Get());

// 如果需要 FColor 格式（用于 UE 纹理）
TArray<FColor> BGRAColors = UE::CaptureManager::UEConvertI420ToBGRA(YUVSample.Get());
```

### 进阶用法 — 按格式指定创建 Reader/Writer

```cpp
FMediaRWManager& RWManager = /* ... */;

// 明确指定格式创建（不依赖文件扩展名推断）
TUniquePtr<IVideoReader> VideoReader = RWManager.CreateVideoReaderByFormat(TEXT("mp4"));
TUniquePtr<IAudioReader> AudioReader = RWManager.CreateAudioReaderByFormat(TEXT("wav"));
TUniquePtr<ICalibrationReader> CalibReader = RWManager.CreateCalibrationReaderByFormat(TEXT("json"));

// Writer 同理
TUniquePtr<IImageWriter> ImageWriter = RWManager.CreateImageWriterByFormat(TEXT("png"));
TUniquePtr<IAudioWriter> AudioWriter = RWManager.CreateAudioWriterByFormat(TEXT("wav"));
TUniquePtr<ICalibrationWriter> CalibWriter = RWManager.CreateCalibrationWriterByFormat(TEXT("json"));
```

### 进阶用法 — 注册自定义 Reader/Writer

```cpp
// 实现自定义视频 Reader 工厂
class FMyCustomVideoReaderFactory : public IVideoReaderFactory
{
public:
    virtual TUniquePtr<IVideoReader> CreateVideoReader() override
    {
        return MakeUnique<FMyCustomVideoReader>();
    }
};

// 注册到 MediaRWManager
FMediaRWManager& RWManager = /* ... */;
TArray<FString> Formats = { TEXT("myformat"), TEXT("mfmt") };
RWManager.RegisterVideoReader(Formats, MakeUnique<FMyCustomVideoReaderFactory>());
```

## Demo 示例

### 自定义视频 Reader 实现

```cpp
// MyCustomVideoReader.h
#pragma once

#include "IMediaReader.h"

class FMyCustomVideoReader : public IVideoReader
{
public:
    virtual TOptional<FText> Open(const FString& InFileName) override;
    virtual TOptional<FText> Close() override;
    virtual TValueOrError<TUniquePtr<UE::CaptureManager::FMediaTextureSample>, FText> Next() override;
    virtual FTimespan GetDuration() const override;
    virtual FIntPoint GetDimensions() const override;
    virtual FFrameRate GetFrameRate() const override;

private:
    FString FileName;
    int32 CurrentFrame = 0;
    int32 TotalFrames = 0;
    FIntPoint Dimensions = FIntPoint(1920, 1080);
};
```

```cpp
// MyCustomVideoReader.cpp
#include "MyCustomVideoReader.h"

TOptional<FText> FMyCustomVideoReader::Open(const FString& InFileName)
{
    FileName = InFileName;
    CurrentFrame = 0;
    // 打开文件、解析头部信息...
    TotalFrames = 300; // 示例值
    return {}; // 无错误
}

TOptional<FText> FMyCustomVideoReader::Close()
{
    FileName.Empty();
    CurrentFrame = 0;
    return {};
}

TValueOrError<TUniquePtr<UE::CaptureManager::FMediaTextureSample>, FText> FMyCustomVideoReader::Next()
{
    if (CurrentFrame >= TotalFrames)
    {
        return MakeError(FText::FromString(TEXT("No more frames")));
    }

    auto Sample = MakeUnique<UE::CaptureManager::FMediaTextureSample>();
    Sample->Dimensions = Dimensions;
    Sample->CurrentFormat = UE::CaptureManager::EMediaTexturePixelFormat::U8_BGRA;
    Sample->Time = FTimespan::FromSeconds(CurrentFrame / 30.0);
    Sample->Duration = FTimespan::FromSeconds(1.0 / 30.0);
    
    // 填充 Sample->Buffer...
    Sample->Buffer.SetNumUninitialized(Dimensions.X * Dimensions.Y * 4);
    
    CurrentFrame++;
    return MakeValue(MoveTemp(Sample));
}

FTimespan FMyCustomVideoReader::GetDuration() const
{
    return FTimespan::FromSeconds(TotalFrames / 30.0);
}

FIntPoint FMyCustomVideoReader::GetDimensions() const
{
    return Dimensions;
}

FFrameRate FMyCustomVideoReader::GetFrameRate() const
{
    return FFrameRate(30, 1);
}
```

## 模块依赖

从 Build.cs 分析，本模块依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 提供 IMediaAudioSample、IMediaTextureSample 等基础媒体样本接口 |

无其他特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

```
- a7fe5bca1c4b [CaptureManager] Add camera id to ingested asset metadata
- ca98474c4257 Rotation when ingesting image sequence using third party encoder
- d25c68ed2fe6 Image Sequence reader implementation
```

- `a7fe5bca1c4b`：为摄取的资产元数据添加了相机 ID，增强设备追踪能力
- `ca98474c4257`：修复了使用第三方编码器摄取图像序列时的旋转问题
- `d25c68ed2fe6`：实现了图像序列 Reader，扩展了支持的媒体格式

### 维护评价

- **创建时间**：2025-02-04，非常新的插件
- **活跃度**：活跃开发中，近期有功能性更新（图像序列 Reader、元数据增强）
- **稳定性**：作为 Virtual Production 管线的核心 I/O 层，接口设计成熟（工厂模式 + 抽象接口）
- **推荐度**：✅ 推荐使用。这是 Epic 官方 Virtual Production 工具链的一部分，接口清晰，扩展性好。如果你在构建自定义捕获管线或需要统一的媒体读写抽象，这是理想的基础模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/CaptureManagerMediaRW)
- [插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)