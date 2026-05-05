# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（配置资产、示例资源） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

CaptureManagerApp 是一个**虚拟制片数据采集与管理应用程序**，解决的核心问题是：在虚拟制片工作流中，如何高效地从各类采集设备（面部捕捉摄像头、立体相机、深度传感器等）获取原始数据，并将其转换、上传至 Unreal Engine 进行后续使用。

具体来说，它完成以下工作链：

1. **设备控制与监控** — 连接并管理 LiveLink 兼容的采集设备，实时监控采集状态
2. **数据获取** — 从设备读取视频、音频、深度图、标定数据等原始素材
3. **数据转码** — 通过可扩展的 Pipeline 架构，将原始采集数据转换为 UE 可用的格式（图像序列、WAV 音频等）
4. **数据上传** — 将处理后的数据上传至 Unreal Engine 进行导入

与简单的 LiveLink 流传输不同，CaptureManagerApp 专注于**离线采集工作流**：录制完整的 Take（一次拍摄），然后批量处理和导入。

## 使用场景

- 你在做**面部动作捕捉**，使用 LiveLink Face 或类似 App 录制了大量 Take → 用 CaptureManagerApp 批量转码视频帧、音频并上传到 UE
- 你有一套**立体相机采集系统**，需要处理双目视频和深度数据 → 用 StereoCameraMetadata 模块解析相机标定，CaptureDataConverter 转换图像序列
- 你需要将第三方采集设备的数据集成到虚拟制片管线中 → 通过 ExampleLiveLinkDevices 参考实现自定义设备驱动
- 你需要一个**统一的采集数据管理界面**，而不是手动处理文件 → 用 CaptureManagerEditor 提供的编辑器 UI

## 架构概览

本插件采用**模块化 Pipeline 架构**，共 11 个模块，各司其职：

```
┌─────────────────────────────────────────────────────────┐
│                  CaptureManagerEditor                    │
│              （编辑器 UI / 应用主界面）                    │
├──────────┬──────────┬──────────┬─────────────────────────┤
│ 设备层   │ 采集层   │ 转换层   │ 上传层                  │
│          │          │          │                         │
│ LiveLink │ Capture  │ Capture  │ CaptureManager          │
│ Capabil- │ Manager  │ Data     │ UnrealEndpoint          │
│ ities    │ MediaRW  │ Converter│                         │
│          │          │          │                         │
│ Example  │ Ingest   │ Capture  │                         │
│ LiveLink │ LiveLink │ Manager  │                         │
│ Devices  │ Device   │ Pipeline │                         │
├──────────┴──────────┴──────────┴─────────────────────────┤
│  LiveLinkFaceMetadata  │  StereoCameraMetadata          │
│  （元数据解析层）                                        │
├─────────────────────────────────────────────────────────┤
│              CaptureManagerSettings                      │
│              （全局配置）                                  │
└─────────────────────────────────────────────────────────┘
```

| 模块 | 职责 |
|---|---|
| **CaptureManagerEditor** | 编辑器 UI，提供 Capture Manager 应用主界面 |
| **CaptureManagerPipeline** | Pipeline 框架，定义节点接口和执行引擎 |
| **CaptureDataConverter** | 数据转码，将原始采集数据转换为目标格式 |
| **CaptureManagerMediaRW** | 媒体读写，从设备/文件读取原始数据 |
| **CaptureManagerSettings** | 全局设置和配置管理 |
| **CaptureManagerUnrealEndpoint** | UE 数据上传端点 |
| **LiveLinkCapabilities** | LiveLink 设备能力描述 |
| **ExampleLiveLinkDevices** | 示例 LiveLink 设备实现 |
| **IngestLiveLinkDevice** | LiveLink 数据摄入设备 |
| **LiveLinkFaceMetadata** | LiveLink Face App 元数据解析 |
| **StereoCameraMetadata** | 立体相机标定元数据解析 |

## CaptureDataConverter 模块详解

这是数据转码的核心模块，负责将采集到的原始数据（视频帧、音频、深度图、标定文件）转换为 UE 可用的格式。

### 核心类

| 类 | 说明 |
|---|---|
| `FCaptureDataConverter` | 转换器主类，管理 Pipeline 执行、进度报告和取消 |
| `FCaptureConvertParams` | 转换节点参数基类 |
| `FCaptureConvertCustomData` | 自定义转换节点，可插入 Pipeline |
| `FCaptureDataConverterError` | 错误收集器，聚合多条错误信息 |
| `FCaptureDataConverterParams` | 转换任务的完整参数集 |

### 数据流

```
原始 Take 数据（视频/音频/深度/标定）
        │
        ▼
  FCaptureDataConverterParams（配置输入输出路径、格式参数）
        │
        ▼
  FCaptureDataConverter::Run()
        │
        ├── Pipeline Node: 视频帧转码（图像序列）
        ├── Pipeline Node: 音频转码（WAV）
        ├── Pipeline Node: 深度图处理
        ├── Pipeline Node: 标定数据提取
        └── Custom Nodes（用户自定义）
        │
        ▼
  输出目录中的转码后文件
```

### 输出参数结构

| 结构体 | 默认文件名 | 关键字段 |
|---|---|---|
| `FCaptureConvertVideoOutputParams` | `frame` | Format, OutputPixelFormat, Rotation |
| `FCaptureConvertAudioOutputParams` | `audio` | Format（默认 wav） |
| `FCaptureConvertDepthOutputParams` | `depth` | bShouldCompressFiles, Rotation |
| `FCaptureConvertCalibrationOutputParams` | `calibration` | FileName |

## 蓝图用法

CaptureDataConverter 模块是纯 C++ 实现，**不包含 BlueprintCallable 函数**。数据转换逻辑通过 C++ API 调用。

其他模块（如 CaptureManagerEditor）可能提供蓝图接口，但不在本文档覆盖范围内。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureDataConverter.h"
#include "CaptureDataConverterNodeParams.h"
```

### 基本用法 — 执行一次 Take 转换

```cpp
#include "CaptureDataConverter.h"

void ConvertTake()
{
    // 1. 创建转换器实例
    FCaptureDataConverter Converter;

    // 2. 配置转换参数
    FCaptureDataConverterParams Params;
    Params.TakeName = TEXT("Take_001");
    Params.TakeOriginDirectory = TEXT("/Captures/Raw/Take_001");
    Params.TakeOutputDirectory = TEXT("/Captures/Converted/Take_001");

    // 3. 配置视频输出（图像序列）
    FCaptureConvertVideoOutputParams VideoParams;
    VideoParams.Format = TEXT("png");
    VideoParams.OutputPixelFormat = UE::CaptureManager::EMediaTexturePixelFormat::U8;
    VideoParams.Rotation = EMediaOrientation::Original;
    Params.VideoOutputParams = VideoParams;

    // 4. 配置音频输出
    FCaptureConvertAudioOutputParams AudioParams;
    AudioParams.Format = TEXT("wav");
    Params.AudioOutputParams = AudioParams;

    // 5. 执行转换，带进度回调
    auto Result = Converter.Run(MoveTemp(Params),
        FCaptureDataConverter::FProgressReporter::CreateLambda(
            [](double InProgress)
            {
                UE_LOG(LogTemp, Log, TEXT("转换进度: %.1f%%"), InProgress * 100.0);
            }
        )
    );

    // 6. 处理结果
    if (Result.HasValue())
    {
        UE_LOG(LogTemp, Log, TEXT("转换完成"));
    }
    else
    {
        for (const FText& Error : Result.GetError().GetErrors())
        {
            UE_LOG(LogTemp, Error, TEXT("转换错误: %s"), *Error.ToString());
        }
    }
}
```

### 进阶用法 — 自定义 Pipeline 节点与取消

```cpp
#include "CaptureDataConverter.h"
#include "Nodes/CaptureConvertCustomData.h"

// 自定义转换节点：在标准转换后执行额外处理
class FMyCustomPostProcessNode : public FCaptureConvertCustomData
{
public:
    using FCaptureConvertCustomData::FCaptureConvertCustomData;

    // 重写 Pipeline 节点的执行逻辑
    // （具体虚函数取决于 FCaptureManagerPipelineNode 的接口）
};

void AdvancedConvertTake()
{
    FCaptureDataConverter Converter;

    // 添加自定义节点到 Pipeline
    auto CustomNode = MakeShared<FMyCustomPostProcessNode>();
    Converter.AddCustomNode(CustomNode);

    // 添加同步节点（确保在所有异步节点完成后执行）
    auto SyncNode = MakeShared<FCaptureConvertCustomData>();
    Converter.AddSyncNode(SyncNode);

    // 配置参数（含深度和标定）
    FCaptureDataConverterParams Params;
    Params.TakeName = TEXT("StereoTake_001");
    Params.TakeOriginDirectory = TEXT("/Captures/Raw/StereoTake_001");
    Params.TakeOutputDirectory = TEXT("/Captures/Converted/StereoTake_001");

    // 深度图输出
    FCaptureConvertDepthOutputParams DepthParams;
    DepthParams.bShouldCompressFiles = true;
    DepthParams.Rotation = EMediaOrientation::Original;
    Params.DepthOutputParams = DepthParams;

    // 标定数据输出
    FCaptureConvertCalibrationOutputParams CalibParams;
    Params.CalibrationOutputParams = CalibParams;

    // 异步执行，支持取消
    auto Result = Converter.Run(MoveTemp(Params),
        FCaptureDataConverter::FProgressReporter::CreateLambda(
            [&Converter](double InProgress)
            {
                // 某种条件下取消转换
                if (ShouldCancel())
                {
                    Converter.Cancel();
                }
            }
        )
    );
}
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何使用 CaptureDataConverter 模块进行 Take 数据转换。

### CaptureDataConverterExample.h

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

class FCaptureDataConverterExample
{
public:
    /** 执行一次完整的 Take 转换示例 */
    static bool RunConversionExample();

    /** 执行带自定义节点的转换示例 */
    static bool RunAdvancedConversionExample();
};
```

### CaptureDataConverterExample.cpp

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "CaptureDataConverterExample.h"

#include "CaptureDataConverter.h"
#include "CaptureDataConverterNodeParams.h"
#include "Nodes/CaptureConvertCustomData.h"

bool FCaptureDataConverterExample::RunConversionExample()
{
    FCaptureDataConverter Converter;

    // 配置转换参数
    FCaptureDataConverterParams Params;
    Params.TakeName = TEXT("DemoTake");
    Params.TakeOriginDirectory = TEXT("/Game/Captures/Raw/DemoTake");
    Params.TakeOutputDirectory = TEXT("/Game/Captures/Converted/DemoTake");

    // 视频：输出 PNG 图像序列
    FCaptureConvertVideoOutputParams VideoParams;
    VideoParams.Format = TEXT("png");
    VideoParams.OutputPixelFormat = UE::CaptureManager::EMediaTexturePixelFormat::U8;
    VideoParams.Rotation = EMediaOrientation::Original;
    Params.VideoOutputParams = VideoParams;

    // 音频：输出 WAV
    FCaptureConvertAudioOutputParams AudioParams;
    AudioParams.Format = TEXT("wav");
    Params.AudioOutputParams = AudioParams;

    // 执行转换
    auto Result = Converter.Run(MoveTemp(Params),
        FCaptureDataConverter::FProgressReporter::CreateLambda(
            [](double InProgress)
            {
                UE_LOG(LogTemp, Display, TEXT("[CaptureDataConverter] Progress: %.1f%%"),
                    InProgress * 100.0);
            }
        )
    );

    if (!Result.HasValue())
    {
        for (const FText& Error : Result.GetError().GetErrors())
        {
            UE_LOG(LogTemp, Error, TEXT("[CaptureDataConverter] %s"), *Error.ToString());
        }
        return false;
    }

    UE_LOG(LogTemp, Display, TEXT("[CaptureDataConverter] Conversion completed successfully"));
    return true;
}

bool FCaptureDataConverterExample::RunAdvancedConversionExample()
{
    FCaptureDataConverter Converter;

    // 添加自定义处理节点
    auto CustomNode = MakeShared<FCaptureConvertCustomData>();
    Converter.AddCustomNode(CustomNode);

    // 添加同步节点（在所有异步处理完成后执行）
    auto SyncNode = MakeShared<FCaptureConvertCustomData>();
    Converter.AddSyncNode(SyncNode);

    // 配置完整参数（含深度和标定）
    FCaptureDataConverterParams Params;
    Params.TakeName = TEXT("StereoDemoTake");
    Params.TakeOriginDirectory = TEXT("/Game/Captures/Raw/StereoDemoTake");
    Params.TakeOutputDirectory = TEXT("/Game/Captures/Converted/StereoDemoTake");

    FCaptureConvertVideoOutputParams VideoParams;
    VideoParams.Format = TEXT("exr");
    Params.VideoOutputParams = VideoParams;

    FCaptureConvertDepthOutputParams DepthParams;
    DepthParams.bShouldCompressFiles = true;
    DepthParams.Rotation = EMediaOrientation::Original;
    Params.DepthOutputParams = DepthParams;

    FCaptureConvertCalibrationOutputParams CalibParams;
    Params.CalibrationOutputParams = CalibParams;

    auto Result = Converter.Run(MoveTemp(Params),
        FCaptureDataConverter::FProgressReporter::CreateLambda(
            [](double InProgress)
            {
                UE_LOG(LogTemp, Display, TEXT("[CaptureDataConverter] Advanced progress: %.1f%%"),
                    InProgress * 100.0);
            }
        )
    );

    return Result.HasValue();
}
```

## 模块依赖

以下为 CaptureDataConverter 模块的独特依赖（从头文件推断）：

| 模块 | 用途 |
|---|---|
| `CaptureManagerPipeline` | Pipeline 框架，提供 `FCaptureManagerPipelineNode` 基类和执行引擎 |
| `Media` | 媒体基础类型，提供 `EMediaOrientation`、`EMediaTexturePixelFormat` 等 |

无其他特殊依赖（仅标准 Core/Engine 等）。

> **注意**：完整插件的其他模块可能有更多依赖（如 LiveLink、MediaFramework 等），此处仅列出 CaptureDataConverter 模块的依赖。

## 维护状态

### 近期更新

```
- b5b6ce302bb9 Text conflict from LOCTEXT macro for namespace 'CaptureConvertVideoDataTP'
- ca98474c4257 Rotation when ingesting image sequence using third party encoder
- d25c68ed2fe6 Image Sequence reader implementation
```

- `b5b6ce3` — 修复 LOCTEXT 宏命名空间冲突，属于本地化文本修正
- `ca98474` — 新增图像序列摄入时的旋转支持（第三方编码器），功能增强
- `d25c68e` — 实现图像序列读取器，核心功能新增

### 维护评价

- **创建时间**：2025 年 2 月，非常新的插件
- **版本**：1.0.0，首个正式版本
- **更新频率**：近期有活跃的功能开发（图像序列读取、旋转支持等）
- **维护状态**：🟢 **活跃维护中** — 作为 Virtual Production 工具链的核心组件，由 Epic Games 持续开发
- **已知限制**：作为 1.0 版本，API 可能随版本迭代发生变化；部分模块（如 CaptureManagerEditor）的具体 UI 交互需参考编辑器内实际界面
- **推荐程度**：⭐⭐⭐⭐ 如果你的虚拟制片工作流涉及批量采集数据处理，这是 Epic 官方推荐的工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [CaptureDataConverter 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/CaptureDataConverter)
- [CaptureManagerPipeline 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/CaptureManagerPipeline)