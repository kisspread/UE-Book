# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体读写器、协议栈、管线、工具类等运行时模块） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerCPSClient` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureMetadataExtraction` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

CaptureManagerCore 是 **虚拟制片中数字人/体积视频捕获工作流的基础设施层**。它本身不提供完整的捕获应用功能，而是被 `CaptureManagerApp`（独立应用程序端）和 `CaptureManagerEditor`（编辑器端插件）共同依赖的共享库。

核心解决的问题：
- **媒体格式读写的统一抽象**：封装了音频（WAV）、视频（WMV/图像序列/MHA深度）、相机标定（OpenCV/iPhone/MHA）等多种格式的读写能力，通过工厂模式按文件扩展名自动匹配读写器
- **像素格式转换**：提供 YUV→BGRA、YUV→Mono、NV12→BGRA 等专业视频格式转换，服务于深度图和视频帧的后续处理
- **坐标系统转换**：内置 OpenCV 和 Unreal 两套坐标系的定义与互转，解决不同设备/软件间的相机姿态数据对齐问题
- **捕获协议与管线**：提供与 CaptureManager 服务端通信的协议栈（CPS Client）、数据摄取流程编排（Pipeline）、Take 元数据解析等

**默认禁用**（`EnabledByDefault=false`），需要由 CaptureManagerApp 或 CaptureManagerEditor 插件间接启用。

---

## 模块总览

| 模块 | 类型 | 说明 |
|---|---|---|
| `CaptureManagerMediaRW` | Runtime | 媒体读写管理器，音频/视频/标定数据的格式工厂 |
| `CaptureProtocolStack` | Runtime | 与 CaptureManager 服务端的通信协议栈 |
| `CaptureManagerCPSClient` | Runtime | CPS（Capture Protocol Stack）客户端实现 |
| `CaptureManagerPipeline` | Runtime | 捕获数据处理管线编排 |
| `CaptureDataConverter` | Runtime | 捕获数据格式转换 |
| `CaptureManagerTakeMetadata` | Runtime | Take（拍摄条目）元数据定义与解析 |
| `CaptureMetadataExtraction` | Runtime | 从捕获文件中提取元数据 |
| `CaptureManagerStyle` | Runtime | UI 样式定义（供编辑器 UI 使用） |
| `CaptureUtils` | Runtime | 通用工具函数 |
| `DataIngestCore` | Runtime | 数据摄取核心逻辑 |
| `LiveLinkHubCaptureMessaging` | Runtime | LiveLink Hub 与捕获系统的消息通信 |

---

## 重点模块：CaptureManagerMediaRW

这是整个插件中最核心的模块，提供了一个 **可扩展的媒体读写框架**。下面详细说明其 API。

### 架构设计

```
FMediaRWManager（中央注册表）
├── 音频读取器 (IAudioReader)     ← Windows Media Foundation / 其他平台
├── 视频读取器 (IVideoReader)     ← WMV视频 / 图像序列 / MHA深度
├── 标定读取器 (ICalibrationReader) ← OpenCV JSON / iPhone / MHA
├── 音频写入器 (IAudioWriter)     ← WAV 文件
├── 图像写入器 (IImageWriter)     ← WIC 编码 / EXR 深度图
└── 标定写入器 (ICalibrationWriter) ← Unreal JSON 格式
```

采用 **工厂+注册表** 模式：各读写器通过 `Register*Reader/Writer` 注册到 `FMediaRWManager`，之后按文件格式字符串（扩展名）自动创建对应的读写器实例。

### 内置读写器一览

| 类型 | 读/写 | 实现类 | 支持格式 |
|---|---|---|---|
| 音频 | 读 | `FWindowsAudioReader` | WMV/支持的音频格式（Windows Media Foundation） |
| 视频 | 读 | `FWindowsVideoReader` | WMV/支持的视频格式（Windows Media Foundation） |
| 视频 | 读 | `FImageSequenceReader` | 图像序列目录（jpg/png 等） |
| 视频 | 读 | `FMHADepthVideoReader` | MHA 深度视频 |
| 标定 | 读 | `FOpenCvCalibrationReader` | OpenCV 标定 JSON |
| 标定 | 读 | `FMHAICalibrationReader` | MHA 标定 JSON |
| 音频 | 写 | `FAudioWaveWriter` | WAV |
| 图像 | 写 | `FWindowsImageWriter` | WIC 支持的图像格式（jpg/png 等，Windows） |
| 图像 | 写 | `FDepthExrImageWriter` | EXR 深度图 |
| 标定 | 写 | `FUnrealCalibrationWriter` | Unreal JSON 格式 |

### 核心数据结构

| 结构体 | 说明 |
|---|---|
| `FMediaAudioSample` | 音频采样数据：Buffer、采样率、通道数、格式、时间戳 |
| `FMediaTextureSample` | 视频/图像采样：Buffer、尺寸、像素格式、方向、旋转 |
| `FMediaCalibrationSample` | 相机标定：焦距、主点、畸变模型、变换矩阵、坐标系 |
| `FOpenCVDistortionModel` | OpenCV 径向+切向畸变参数（K1-K3, P1-P2） |
| `FIphoneDistortionModel` | iPhone 镜头畸变查找表 |
| `FCoordinateSystem` | 三维坐标系定义（6 个方向轴的映射） |

### 像素格式枚举

`EMediaTexturePixelFormat` 支持以下格式：

| 枚举值 | 说明 |
|---|---|
| `U8_RGB` / `U8_BGR` | 8位 RGB/BGR |
| `U8_RGBA` / `U8_BGRA` | 8位 RGBA/BGRA |
| `U8_I444` / `U8_I420` | YUV 4:4:4 / 4:2:0 |
| `U8_YUY2` | YUY2 交错格式 |
| `U8_NV12` | NV12 半平面格式 |
| `U8_Mono` / `U16_Mono` / `F_Mono` | 8位/16位/浮点单通道（深度图） |

---

## 蓝图用法

该插件以纯 C++ Runtime 模块为主，**未暴露 BlueprintCallable 接口**。需要在 C++ 中直接使用。

---

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManagerMediaRWModule.h"
#include "MediaRWManager.h"
#include "IMediaReader.h"
#include "IMediaWriter.h"
#include "MediaSample.h"
```

### 基本用法：获取 MediaRWManager 并创建读取器

```cpp
// 获取模块单例
FCaptureManagerMediaRWModule& MediaRWModule = FModuleManager::LoadModuleChecked<FCaptureManagerMediaRWModule>("CaptureManagerMediaRW");
FMediaRWManager& MediaRWManager = MediaRWModule.Get();

// 根据文件路径自动匹配读取器
{
    // 读取音频文件
    TValueOrError<TUniquePtr<IAudioReader>, FText> AudioResult = 
        MediaRWManager.CreateAudioReader(TEXT("C:/Capture/audio.wav"));
    
    if (AudioResult.HasValue())
    {
        TUniquePtr<IAudioReader> Reader = AudioResult.GetValue();
        TOptional<FText> OpenResult = Reader->Open(TEXT("C:/Capture/audio.wav"));
        
        if (!OpenResult.IsSet())  // 打开成功
        {
            // 逐帧读取
            while (true)
            {
                TValueOrError<TUniquePtr<FMediaAudioSample>, FText> SampleResult = Reader->Next();
                if (SampleResult.HasError())
                    break;  // 读取完毕或出错
                
                TUniquePtr<FMediaAudioSample> Sample = SampleResult.GetValue();
                // 处理 Sample->Buffer, Sample->SampleRate 等
            }
        }
        Reader->Close();
    }
    else
    {
        // AudioResult.GetError() 包含错误信息
    }
}

// 读取视频/图像序列
{
    // CreateVideoReader 支持 .wmv 视频文件或包含图像序列的目录路径
    TValueOrError<TUniquePtr<IVideoReader>, FText> VideoResult = 
        MediaRWManager.CreateVideoReader(TEXT("C:/Capture/frame_sequence/"));
    
    if (VideoResult.HasValue())
    {
        TUniquePtr<IVideoReader> Reader = VideoResult.GetValue();
        TOptional<FText> OpenResult = Reader->Open(TEXT("C:/Capture/frame_sequence/"));
        
        if (!OpenResult.IsSet())
        {
            FIntPoint Dimensions = Reader->GetDimensions();
            FFrameRate FrameRate = Reader->GetFrameRate();
            
            while (true)
            {
                TValueOrError<TUniquePtr<FMediaTextureSample>, FText> SampleResult = Reader->Next();
                if (SampleResult.HasError())
                    break;
                
                TUniquePtr<FMediaTextureSample> Frame = SampleResult.GetValue();
                // Frame->Buffer 包含像素数据
                // Frame->Dimensions 包含宽高
                // Frame->CurrentFormat 包含像素格式
            }
        }
        Reader->Close();
    }
}
```

*来源：Public/MediaRWManager.h、Public/IMediaReader.h*

### 基本用法：创建写入器

```cpp
FMediaRWManager& MediaRWManager = ...;

// 写入音频
{
    // CreateAudioWriter(输出目录, 文件名（不含扩展名）, 格式扩展名)
    TValueOrError<TUniquePtr<IAudioWriter>, FText> WriterResult = 
        MediaRWManager.CreateAudioWriter(TEXT("C:/Output/"), TEXT("capture_audio"), TEXT("wav"));
    
    if (WriterResult.HasValue())
    {
        TUniquePtr<IAudioWriter> Writer = WriterResult.GetValue();
        
        // 配置音频参数
        Writer->Configure(ESampleRate::SR_48000Hz, 2, EMediaAudioSampleFormat::Int16);
        
        TOptional<FText> OpenResult = Writer->Open(TEXT("C:/Output/"), TEXT("capture_audio"), TEXT("wav"));
        if (!OpenResult.IsSet())
        {
            // 写入音频采样
            FMediaAudioSample Sample;
            Sample.SampleRate = ESampleRate::SR_48000Hz;
            Sample.Channels = 2;
            // ... 填充 Sample.Buffer ...
            Writer->Append(&Sample);
        }
        Writer->Close();
    }
}

// 写入图像序列
{
    TValueOrError<TUniquePtr<IImageWriter>, FText> WriterResult = 
        MediaRWManager.CreateImageWriter(TEXT("C:/Output/frames/"), TEXT("frame"), TEXT("png"));
    
    if (WriterResult.HasValue())
    {
        TUniquePtr<IImageWriter> Writer = WriterResult.GetValue();
        Writer->Open(TEXT("C:/Output/frames/"), TEXT("frame"), TEXT("png"));
        
        FMediaTextureSample Frame;
        Frame.Dimensions = FIntPoint(1920, 1080);
        // ... 填充 Frame.Buffer ...
        Writer->Append(&Frame);
        
        Writer->Close();
    }
}

// 写入标定数据
{
    TValueOrError<TUniquePtr<ICalibrationWriter>, FText> WriterResult = 
        MediaRWManager.CreateCalibrationWriter(TEXT("C:/Output/"), TEXT("calibration"), TEXT("json"));
    
    if (WriterResult.HasValue())
    {
        TUniquePtr<ICalibrationWriter> Writer = WriterResult.GetValue();
        Writer->Open(TEXT("C:/Output/"), TEXT("calibration"), TEXT("json"));
        
        FMediaCalibrationSample Calib;
        Calib.CameraId = TEXT("camera_0");
        Calib.CameraType = FMediaCalibrationSample::Video;
        Calib.FocalLength = FVector2D(1000.0, 1000.0);
        Calib.PrincipalPoint = FVector2D(960.0, 540.0);
        Calib.Dimensions = FIntPoint(1920, 1080);
        // ... 设置 Transform, DistortionModel 等 ...
        Writer->Append(&Calib);
        
        Writer->Close();
    }
}
```

*来源：Public/MediaRWManager.h、Public/IMediaWriter.h*

### 进阶用法：按格式指定读写器索引

当同一格式注册了多个读写器时，可通过 `InIndex` 参数选择：

```cpp
// 第二个注册的音频读取器（InIndex=1）
TUniquePtr<IAudioReader> Reader = MediaRWManager.CreateAudioReaderByFormat(TEXT("wav"), 1);

// 按格式字符串直接创建（不依赖文件路径推断）
TUniquePtr<IVideoReader> VideoReader = MediaRWManager.CreateVideoReaderByFormat(TEXT("mha"));
```

*来源：Public/MediaRWManager.h*

### 进阶用法：像素格式转换

```cpp
#include "Utils/MediaPixelFormatConversions.h"

// 将 YUV 图像序列样本转为 BGRA
TArray<uint8> BGRAData = UE::CaptureManager::ConvertI420ToBGRA(TextureSample.Get());

// 转为 Unreal 的 FColor 数组（方便 UTexture 更新）
TArray<FColor> ColorData = UE::CaptureManager::UEConvertNV12ToBGRA(TextureSample.Get());

// 深度图 YUV 转 Mono（单通道）
TArray<uint8> MonoData = UE::CaptureManager::ConvertYUVToMono(TextureSample.Get(), true);
```

*来源：Public/Utils/MediaPixelFormatConversions.h*

### 进阶用法：坐标系转换

```cpp
#include "MediaSample.h"

// OpenCV 坐标系 → Unreal 坐标系
FTransform OpenCVTransform = /* 从标定数据获取 */;
FTransform UnrealTransform = UE::CaptureManager::ConvertToCoordinateSystem(
    OpenCVTransform,
    UE::CaptureManager::OpenCvCS,   // 输入：OpenCV 坐标系
    UE::CaptureManager::UnrealCS    // 输出：Unreal 坐标系
);

// 向量也可以转换
FVector OpenCVPos(1.0, 2.0, 3.0);
FVector UnrealPos = UE::CaptureManager::ConvertToCoordinateSystem(
    OpenCVPos,
    UE::CaptureManager::OpenCvCS,
    UE::CaptureManager::UnrealCS
);

// 自定义坐标系
FCoordinateSystem CustomCS(
    FCoordinateSystem::Right,   // X 轴朝右
    FCoordinateSystem::Up,      // Y 轴朝上
    FCoordinateSystem::Forward  // Z 轴朝前
);
```

*来源：Public/MediaSample.h*

### 进阶用法：自定义读写器扩展

```cpp
#include "IMediaRWFactory.h"
#include "IMediaReader.h"
#include "MediaSample.h"

// 实现自定义视频读取器
class FMyCustomVideoReader final : public IVideoReader
{
public:
    virtual TOptional<FText> Open(const FString& InFileName) override
    {
        // 打开自定义格式文件...
        return {};  // 返回空表示成功
    }
    
    virtual TOptional<FText> Close() override { return {}; }
    
    virtual TValueOrError<TUniquePtr<FMediaTextureSample>, FText> Next() override
    {
        // 返回下一帧...
        auto Sample = MakeUnique<FMediaTextureSample>();
        Sample->Dimensions = FIntPoint(1920, 1080);
        Sample->CurrentFormat = EMediaTexturePixelFormat::U8_BGRA;
        // ... 填充 Sample->Buffer ...
        return MakeValue(MoveTemp(Sample));
    }
    
    virtual FTimespan GetDuration() const override { return FTimespan::FromSeconds(10.0); }
    virtual FIntPoint GetDimensions() const override { return FIntPoint(1920, 1080); }
    virtual FFrameRate GetFrameRate() const override { return FFrameRate(30, 1); }
};

// 实现工厂
class FMyCustomVideoReaderFactory final : public IVideoReaderFactory
{
public:
    virtual TUniquePtr<IVideoReader> CreateVideoReader() override
    {
        return MakeUnique<FMyCustomVideoReader>();
    }
};

// 注册到 MediaRWManager
FMediaRWManager& Manager = FModuleManager::LoadModuleChecked<FCaptureManagerMediaRWModule>("CaptureManagerMediaRW").Get();
Manager.RegisterVideoReader(
    {TEXT("myformat"), TEXT("mfmt")},  // 支持的扩展名列表
    MakeUnique<FMyCustomVideoReaderFactory>()
);
```

*来源：Public/IMediaRWFactory.h、Public/IMediaReader.h*

---

## Demo 示例

以下示例展示如何读取一组图像序列并将其写入为 WAV 音频 + EXR 深度图：

```cpp
// CaptureMediaRWDemo.h
#pragma once

#include "CoreMinimal.h"

class FCaptureMediaRWDemo
{
public:
    static void RunDemo();
};
```

```cpp
// CaptureMediaRWDemo.cpp
#include "CaptureMediaRWDemo.h"

#include "CaptureManagerMediaRWModule.h"
#include "MediaRWManager.h"
#include "IMediaReader.h"
#include "IMediaWriter.h"
#include "MediaSample.h"

void FCaptureMediaRWDemo::RunDemo()
{
    // 获取 MediaRWManager
    FCaptureManagerMediaRWModule& Module = 
        FModuleManager::LoadModuleChecked<FCaptureManagerMediaRWModule>("CaptureManagerMediaRW");
    FMediaRWManager& Manager = Module.Get();

    // === 读取图像序列 ===
    FString SequenceDir = TEXT("C:/Capture/frames/");
    auto VideoResult = Manager.CreateVideoReader(SequenceDir);
    
    if (!VideoResult.HasValue())
    {
        UE_LOG(LogTemp, Error, TEXT("无法创建视频读取器: %s"), *VideoResult.GetError().ToString());
        return;
    }
    
    TUniquePtr<IVideoReader> VideoReader = VideoResult.GetValue();
    if (auto Err = VideoReader->Open(SequenceDir))
    {
        UE_LOG(LogTemp, Error, TEXT("无法打开序列: %s"), *Err.GetValue().ToString());
        return;
    }
    
    // 创建 EXR 深度图写入器
    auto DepthWriterResult = Manager.CreateImageWriter(
        TEXT("C:/Output/depth/"), TEXT("depth"), TEXT("exr"));
    
    if (!DepthWriterResult.HasValue())
    {
        UE_LOG(LogTemp, Error, TEXT("无法创建深度写入器: %s"), *DepthWriterResult.GetError().ToString());
        VideoReader->Close();
        return;
    }
    
    TUniquePtr<IImageWriter> DepthWriter = DepthWriterResult.GetValue();
    DepthWriter->Open(TEXT("C:/Output/depth/"), TEXT("depth"), TEXT("exr"));
    
    // 逐帧处理
    int32 FrameCount = 0;
    while (true)
    {
        auto FrameResult = VideoReader->Next();
        if (FrameResult.HasError())
            break;
        
        TUniquePtr<FMediaTextureSample> Frame = FrameResult.GetValue();
        
        // 写入深度帧
        DepthWriter->Append(Frame.Get());
        ++FrameCount;
    }
    
    DepthWriter->Close();
    VideoReader->Close();
    
    UE_LOG(LogTemp, Log, TEXT("处理完成，共 %d 帧"), FrameCount);
    
    // === 读取标定数据并转换坐标系 ===
    auto CalibResult = Manager.CreateCalibrationReader(TEXT("C:/Capture/calibration.json"));
    if (CalibResult.HasValue())
    {
        TUniquePtr<ICalibrationReader> CalibReader = CalibResult.GetValue();
        CalibReader->Open(TEXT("C:/Capture/calibration.json"));
        
        while (true)
        {
            auto SampleResult = CalibReader->Next();
            if (SampleResult.HasError())
                break;
            
            TUniquePtr<FMediaCalibrationSample> Calib = SampleResult.GetValue();
            
            // 从 OpenCV 坐标系转换到 Unreal 坐标系
            FTransform UnrealTransform = UE::CaptureManager::ConvertToCoordinateSystem(
                Calib->Transform,
                Calib->InputCoordinateSystem,
                UE::CaptureManager::UnrealCS
            );
            
            UE_LOG(LogTemp, Log, TEXT("相机 %s: 焦距=(%.1f, %.1f), 位置=%s"),
                *Calib->CameraId,
                Calib->FocalLength.X, Calib->FocalLength.Y,
                *UnrealTransform.GetLocation().ToString());
        }
        
        CalibReader->Close();
    }
}
```

---

## 模块依赖

以下列出 CaptureManagerMediaRW 模块的非标准依赖（基于头文件 include 推断）：

| 模块 | 用途 |
|---|---|
| `ImageWrapper` | EXR 深度图写入（FDepthExrImageWriter） |
| `Json` | 标定数据的 JSON 读写（OpenCV/MHA/Unreal 格式） |
| `MediaUtils` | EMediaAudioSampleFormat、EMediaOrientation 等媒体类型定义 |
| `RenderCore` | FColor 类型（像素格式转换） |

> 注：Build.cs 原文未提供，以上依赖从源码头文件 include 推断。Windows 平台特有依赖（Media Foundation、WIC）通过平台宏 `PLATFORM_WINDOWS` 控制。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelle | 转发停止信号到第三方编码器，支持音频/视频转换的取消操作 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 补回在模块迁移过程中丢失的修复 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复事务 ID 数据竞争导致的偶发下载失败 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 FSharedString |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 CaptureManagerDeviceBlueprint 模块 |

### 维护评价

- **创建时间**：2025-02-04，约 1 年前，较新的插件
- **更新频率**：2026 年 4-5 月持续有实质性更新（数据竞争修复、新模块、取消机制），说明**活跃维护中**
- **状态**：该插件为 Virtual Production 工作流的核心基础设施，正在被 Epic 持续开发和迭代
- **实验性**：`EnabledByDefault=false`，仍处于实验/内部阶段
- **已知限制**：读写器的 Windows 实现依赖 Media Foundation 和 WIC，跨平台支持可能不完整；仅 Runtime 模块，无蓝图暴露
- **推荐**：✅ 推荐在虚拟制片/数字人捕获项目中作为底层媒体 I/O 基础设施使用，但注意该插件设计为被 CaptureManagerApp/CaptureManagerEditor 间接使用，而非直接面向最终用户

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [CaptureManagerCore.uplugin](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/CaptureManagerCore.uplugin)