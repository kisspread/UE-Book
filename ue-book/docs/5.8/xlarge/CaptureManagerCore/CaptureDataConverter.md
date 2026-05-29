# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（工具库） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerCPSClient` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureMetadataExtraction` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

Capture Manager Core 是一个底层工具库集合，为虚拟制片中的数据捕获与处理提供核心支持。它不是一个独立应用，而是为 `CaptureManagerApp` 和 `CaptureManagerEditor` 提供共享的基础设施。

其核心功能是处理捕获（Capture）得到的原始数据。这包括：
1.  **数据转换**：将捕获的视频、音频、深度图等原始文件，转换成UE引擎或下游工具可直接使用的格式（如将 `.png` 序列帧转换为特定的图像格式，或转码音频）。
2.  **流程管理**：通过 `CaptureManagerPipeline` 模块，将转换、验证、拷贝等操作组织成一个可管理、可取消的管道（Pipeline）。
3.  **元数据处理**：解析和管理捕获会话的“Take”（一次拍摄/录制）元数据，这是理解捕获内容上下文的关键。
4.  **设备与协议通信**：提供与外部设备（如多摄像机系统、动作捕捉设备）通信的客户端和协议栈。
5.  **集成与扩展**：支持通过第三方编码器（如FFmpeg）扩展处理能力，并利用命名令牌（Naming Tokens）系统实现灵活的文件命名和命令参数化。

本质上，它是整个 Capture Manager 工作流的“发动机”和“工具箱”，确保原始捕获数据能够被可靠、高效、可定制地处理并注入到UE5的内容管线中。

## 使用场景

- **处理nDisplay摄像机阵列的捕获**：你从一套复杂的摄像机设置中获得了大量未处理的视频片段，需要批量将它们转换并同步输出为UE可用的图像序列。
- **处理MetaHuman Animator的面部数据**：录制了演员的面部表演，需要将数据（如高精度网格序列、校准信息）转换并存储为项目可引用的资产。
- **开发自定义捕获设备插件**：你需要实现与一个新型摄像机的通信协议，并利用 `CaptureProtocolStack` 和 `CaptureManagerCPSClient` 模块来集成。
- **在LiveLink Hub中监控捕获会话**：利用 `LiveLinkHubCaptureMessaging` 模块在远程编辑会话中查看设备状态和捕获进度。
- **构建自动化数据处理管线**：你希望将捕获数据的导入、验证、转换过程脚本化，以加速虚拟制片流程。

## 蓝图用法

该插件的模块主要为C++运行时库，公共API中暴露给蓝图的类和函数有限。核心操作如数据转换主要通过C++接口完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ECaptureManagerPixelFormat` | 枚举，定义支持的像素格式（RGB, BGR, YUV, 单色等）。 | `ECaptureManagerPixelFormat` |
| `ECaptureManagerRotation` | 枚举，定义图像旋转角度。 | `ECaptureManagerRotation` |

**注意**：主要的转换管理类 `FCaptureDataConverter` 和配置结构 `FCaptureManagerEncoderConfig` 等均为C++类，未暴露为蓝图节点。蓝图更可能用于选择参数（如像素格式枚举），然后传递给C++层执行。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureDataConverter.h" // 核心转换器
#include "CaptureDataConverterNodeParams.h" // 转换参数定义
#include "CaptureManagerEncoderConfig.h" // 编码器配置
```

### 基本用法（创建和运行一个转换任务）

`FCaptureDataConverter` 是数据转换的核心类。你需要配置参数，然后调用其 `Run` 方法。这个过程通常是异步或同步的，取决于是否提供了 `FProgressReporter`。

```cpp
// 来源: Public/CaptureDataConverter.h
// 1. 准备转换参数
FCaptureDataConverterParams ConvertParams;
ConvertParams.TakeMetadata = LoadedTakeMetadata; // 从某处加载的Take元数据
ConvertParams.TakeName = TEXT("Take_001");
ConvertParams.TakeOriginDirectory = TEXT("/Path/To/Captured/RawFiles");
ConvertParams.TakeOutputDirectory = TEXT("/Path/To/Save/ProcessedFiles");

// 可选：配置视频输出参数
FCaptureConvertVideoOutputParams VideoOutput;
VideoOutput.Format = TEXT("png");
VideoOutput.OutputPixelFormat = UE::CaptureManager::EMediaTexturePixelFormat::U8_RGB;
ConvertParams.VideoOutputParams = VideoOutput;

// 可选：配置第三方编码器（如FFmpeg）
FCaptureManagerEncoderConfig VideoEncoderConfig;
VideoEncoderConfig.EncoderPath = TEXT("/Path/To/ffmpeg");
VideoEncoderConfig.EncoderArgs = TEXT("-i {input} -vf scale=1920:1080 {output}"); // 使用命名令牌
ConvertParams.VideoEncoderConfig = VideoEncoderConfig;

// 2. 创建转换器实例
FCaptureDataConverter DataConverter;

// 3. （可选）添加自定义处理节点
// auto MyCustomNode = MakeShared<FCaptureConvertCustomData>();
// MyCustomNode->SetParams(/*...*/);
// DataConverter.AddCustomNode(MyCustomNode);

// 4. 运行转换
FCaptureDataConverter::FProgressReporter ProgressReporter;
ProgressReporter.BindLambda([](double InProgress) {
    UE_LOG(LogTemp, Log, TEXT("Conversion Progress: %.2f%%"), InProgress * 100.0);
});

FCaptureDataConverter::FCaptureDataConverterResult<void> Result = DataConverter.Run(ConvertParams, ProgressReporter);

// 5. 检查结果
if (Result.HasValue()) {
    UE_LOG(LogTemp, Log, TEXT("Conversion completed successfully!"));
} else {
    FCaptureDataConverterError Error = Result.StealError();
    TArray<FText> ErrorMessages = Error.GetErrors();
    for (const FText& Msg : ErrorMessages) {
        UE_LOG(LogTemp, Error, TEXT("Conversion Error: %s"), *Msg.ToString());
    }
}
```

### 进阶用法（使用取消令牌实现可中断任务）

长时间运行的转换任务（如转码高分辨率视频）应该支持取消。你可以通过提供外部停止令牌来实现。

```cpp
// 来源: 公共头文件（概念）及 Private/Nodes 中的实现
#include "StopToken.h" // 假设来自 CaptureUtils 或相关模块

// 创建一个外部停止令牌
UE::CaptureManager::FStopRequester StopRequester;
UE::CaptureManager::FStopToken StopToken = StopRequester.GetToken();

FCaptureDataConverterParams ConvertParams = /* ... 如前所述 ... */;
ConvertParams.ExternalStopToken = StopToken; // 将外部令牌传递给转换参数

FCaptureDataConverter DataConverter;

// 在另一个线程或某个事件（如UI按钮点击）中触发取消
// 例如：在某个超时后取消
FTimerHandle CancelTimer;
GetWorldTimerManager().SetTimer(CancelTimer, [&StopRequester]() {
    StopRequester.RequestStop();
    UE_LOG(LogTemp, Warning, TEXT("Conversion cancellation requested!"));
}, 5.0f, false); // 5秒后取消

// 启动转换（可以是同步或异步的）
FCaptureDataConverter::FCaptureDataConverterResult<void> Result = DataConverter.Run(ConvertParams, nullptr);

// 转换可能因停止令牌被触发而提前结束，返回带有错误的结果
```

## Demo 示例

以下示例展示了一个完整的、可编译的转换任务设置与执行。

### `MyCaptureProcessor.h`
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "CaptureDataConverter.h" // 核心头文件
#include "MyCaptureProcessor.generated.h"

UCLASS(BlueprintType)
class UMyCaptureProcessor : public UObject
{
    GENERATED_BODY()

public:
    // 启动一个转换任务
    UFUNCTION(BlueprintCallable, Category = "Capture Processing")
    bool ProcessCaptureTake(const FString& TakeName,
                            const FString& SourceDir,
                            const FString& DestDir,
                            const FTakeMetadata& TakeMetadata);

    // 请求取消当前任务（如果正在运行）
    UFUNCTION(BlueprintCallable, Category = "Capture Processing")
    void CancelCurrentTask();

private:
    TUniquePtr<FCaptureDataConverter> CurrentConverter;
    UE::CaptureManager::FStopRequester StopRequester;
};
```

### `MyCaptureProcessor.cpp`
```cpp
#include "MyCaptureProcessor.h"

bool UMyCaptureProcessor::ProcessCaptureTake(const FString& TakeName,
                                              const FString& SourceDir,
                                              const FString& DestDir,
                                              const FTakeMetadata& TakeMetadata)
{
    // 清理旧的转换器
    CurrentConverter.Reset();
    StopRequester.Reset();

    // 配置转换参数
    FCaptureDataConverterParams ConvertParams;
    ConvertParams.TakeMetadata = TakeMetadata;
    ConvertParams.TakeName = TakeName;
    ConvertParams.TakeOriginDirectory = SourceDir;
    ConvertParams.TakeOutputDirectory = DestDir;
    ConvertParams.ExternalStopToken = StopRequester.GetToken();

    // 配置视频输出为PNG序列
    FCaptureConvertVideoOutputParams VideoOutput;
    VideoOutput.Format = TEXT("png");
    ConvertParams.VideoOutputParams = VideoOutput;

    // 创建新的转换器
    CurrentConverter = MakeUnique<FCaptureDataConverter>();

    // 设置进度回调（这里简化为日志输出）
    FCaptureDataConverter::FProgressReporter ProgressDelegate;
    ProgressDelegate.BindLambda([TakeName](double Progress) {
        UE_LOG(LogTemp, Display, TEXT("[%s] Progress: %0.1f%%"), *TakeName, Progress * 100.0);
    });

    // 运行转换（同步模式，实际项目中可能需要在后台线程运行）
    auto Result = CurrentConverter->Run(MoveTemp(ConvertParams), ProgressDelegate);

    if (Result.HasValue()) {
        UE_LOG(LogTemp, Log, TEXT("Take '%s' processed successfully."), *TakeName);
        CurrentConverter.Reset();
        return true;
    }
    else {
        const auto& Errors = Result.StealError().GetErrors();
        for (const auto& Err : Errors) {
            UE_LOG(LogTemp, Error, TEXT("Processing Take '%s' failed: %s"), *TakeName, *Err.ToString());
        }
        CurrentConverter.Reset();
        return false;
    }
}

void UMyCaptureProcessor::CancelCurrentTask()
{
    if (CurrentConverter.IsValid())
    {
        StopRequester.RequestStop();
        UE_LOG(LogTemp, Warning, TEXT("Cancellation requested for capture processing."));
        // 注意：同步Run模式下，这里可能不会立即生效，
        // 转换节点内部需要检查停止令牌才能提前退出。
    }
}
```

## 模块依赖

使用 `CaptureManagerCore` 插件时，你的 `Build.cs` 文件通常需要依赖其中特定的子模块，而非整个插件。常见的依赖模式如下：

```csharp
// 在你的模块的 .Build.cs 文件中
PublicDependencyModuleNames.AddRange(new string[] {
    "Core", "CoreUObject", "Engine", // ... 其他基础模块
    "CaptureManagerTakeMetadata",   // 需要访问Take元数据结构
    "CaptureUtils",                 // 使用通用工具类（如任务进度、停止令牌）
    "CaptureDataConverter"          // 如果直接进行数据转换
});

// 如果涉及媒体读写
PrivateDependencyModuleNames.Add("MediaUtils");
PrivateDependencyModuleNames.Add("ImageWriteQueue"); // 用于写入图像序列
```

| 模块 | 用途 |
|---|---|
| `CaptureManagerTakeMetadata` | 定义 `FTakeMetadata` 等核心数据结构，用于描述一次捕获会话。 |
| `CaptureUtils` | 提供任务进度跟踪 (`FTaskProgress`)、停止令牌 (`FStopToken`) 等基础工具。 |
| `CaptureDataConverter` | 提供数据转换的主动作 `FCaptureDataConverter`。 |
| `MediaUtils`, `MediaAssets` | 底层媒体框架，用于读取和处理音频/视频样本。 |
| `ImageWriteQueue` | 用于将媒体样本高效地写入磁盘文件（如PNG、EXR序列）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelle | 将停止令牌传递给第三方编码器命令，使音视频转换任务可被取消。 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 补充了在之前模块迁移过程中丢失的一个修复。 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复了交易ID的数据竞争问题，该问题会导致间歇性下载失败。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了FJsonObject以支持FString和UE::FSharedString两种类型。 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增了 `CaptureManagerDeviceBlueprint` 模块。 |

### 维护评价

- **创建时间**：约1年半前（2025年初）。
- **更新频率**：**非常活跃**。最近一次更新在2026年5月，且近期有多次功能性提交（如改进取消功能、修复数据竞争、新增模块）。
- **维护状态**：**积极维护中**。作为虚拟制片管线的核心组件，Epic Games持续对其进行功能增强和稳定性修复。
- **已知限制**：`EnabledByDefault: false` 表明该插件处于实验性或开发阶段，API和功能在未来版本中可能发生破坏性变更。
- **推荐使用**：**适合在虚拟制片项目中使用，特别是需要处理复杂捕获数据流程时。** 但由于其活跃开发和实验性状态，建议在项目早期进行集成，并密切关注版本更新日志。对于生产环境关键任务，应进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [测试用例] (未在分析路径中发现独立的测试文件，测试可能位于 `Engine/Tests/` 目录下)