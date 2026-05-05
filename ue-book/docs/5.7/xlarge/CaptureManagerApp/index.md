# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

CaptureManagerApp 是一个面向虚拟制片（Virtual Production）的综合性动作捕捉管理应用。它并非一个简单的运行时组件，而是一个完整的**数据处理与设备管理平台**。其核心解决的问题是：在复杂的虚拟制片流程中，如何高效、自动化地管理多种动作捕捉设备（如 Live Link Face 应用、立体摄像机等），并完成从原始数据获取、格式转码到最终上传至 Unreal Engine 进行导入的完整数据流水线。

它存在的意义是**标准化和自动化**捕捉数据的处理流程，减少人工干预，确保数据质量与一致性，是专业虚拟制片团队的关键工具。

## 使用场景

- **虚拟制片团队**：需要管理多台动作捕捉设备（如 iPhone 上的 Live Link Face 应用），并自动收集、处理其产生的视频、音频和元数据。
- **数据处理流水线**：需要将捕捉设备产生的原始数据（如 H.264 视频）自动转码为 UE 可高效处理的格式（如 ProRes），并附带正确的元数据。
- **自动化资产导入**：希望将处理好的捕捉数据自动上传至 UE 项目或 Perforce 版本控制，触发自动导入流程。
- **设备监控与控制**：需要在统一界面中监控设备状态、电量、存储空间，并远程控制录制的开始与停止。

## 蓝图用法

由于插件规模庞大（xlarge），其蓝图 API 分布在多个模块中。核心功能通常通过 `CaptureManagerEditor` 和 `CaptureManagerPipeline` 模块暴露。以下为关键功能分组：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect to Device` | 通过 IP 或设备发现连接到一台捕捉设备 | `UCaptureManagerSubsystem` |
| `Start Capture` | 远程启动已连接设备的录制 | `UCaptureManagerSubsystem` |
| `Stop Capture` | 远程停止录制 | `UCaptureManagerSubsystem` |
| `Get Device Status` | 获取设备的当前状态（录制中、空闲、电量等） | `UCaptureManagerSubsystem` |
| `Create Transcode Task` | 为一组原始媒体文件创建转码任务 | `UTranscodeTaskFactory` |
| `Start Pipeline` | 启动一个预定义的数据处理流水线（包含转码、元数据处理等步骤） | `UCaptureManagerPipelineSubsystem` |

### 使用示例（蓝图描述）

1.  **连接设备并开始录制**：
    *   使用 `Find Devices` 节点搜索局域网内的可用设备。
    *   从返回的设备列表中选择一个，调用 `Connect to Device`。
    *   连接成功后，调用 `Start Capture` 开始录制。
    *   使用 `Get Device Status` 节点轮询状态，直到录制完成。

2.  **自动化数据处理**：
    *   监听 `On Capture Completed` 事件，获取新录制的数据路径。
    *   将路径传入 `Create Transcode Task` 节点，配置输出格式（如 ProRes）和输出目录。
    *   调用 `Start Pipeline` 节点，将转码任务加入处理队列。
    *   监听 `On Pipeline Completed` 事件，获取处理完成后的最终资产路径。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManagerSubsystem.h"
#include "TranscodeTaskFactory.h"
#include "CaptureManagerPipelineSubsystem.h"
```

### 基本用法

以下示例展示如何通过 C++ 代码连接设备并启动一个简单的转码任务。

```cpp
// 假设在某个 Actor 或 GameInstance 中
void AMyActor::StartCaptureWorkflow()
{
    // 1. 获取捕获管理器子系统
    UCaptureManagerSubsystem* CaptureSubsystem = GEngine->GetEngineSubsystem<UCaptureManagerSubsystem>();
    if (!CaptureSubsystem) return;

    // 2. 搜索并连接设备 (简化示例，实际需处理异步回调)
    TArray<FCaptureDeviceInfo> Devices;
    CaptureSubsystem->FindDevices(Devices);
    if (Devices.Num() > 0)
    {
        CaptureSubsystem->ConnectToDevice(Devices[0].DeviceId);
        
        // 3. 开始录制
        CaptureSubsystem->StartCapture();
    }
}

void AMyActor::ProcessCapturedData(const FString& RawMediaPath)
{
    // 1. 获取转码任务工厂
    UTranscodeTaskFactory* TaskFactory = NewObject<UTranscodeTaskFactory>();
    
    // 2. 配置转码参数
    FTranscodeSettings Settings;
    Settings.OutputFormat = EMediaFormat::ProRes;
    Settings.OutputDirectory = FPaths::ProjectSavedDir() / TEXT("Transcoded");
    
    // 3. 创建并启动任务
    UTranscodeTask* Task = TaskFactory->CreateTask(RawMediaPath, Settings);
    Task->OnCompleted.AddDynamic(this, &AMyActor::OnTranscodeFinished);
    Task->Start();
}
```

### 进阶用法

结合 `CaptureManagerPipeline` 模块，可以定义和执行复杂的数据处理流水线。

```cpp
void AMyActor::RunFullPipeline(const FString& DeviceId)
{
    UCaptureManagerPipelineSubsystem* PipelineSubsystem = GEngine->GetEngineSubsystem<UCaptureManagerPipelineSubsystem>();
    
    // 定义一个流水线：获取数据 -> 转码 -> 上传
    TArray<FPipelineStep> Steps;
    Steps.Add(FPipelineStep(TEXT("FetchData"), {TEXT("DeviceId"), DeviceId}));
    Steps.Add(FPipelineStep(TEXT("Transcode"), {TEXT("Format"), TEXT("ProRes422HQ")}));
    Steps.Add(FPipelineStep(TEXT("UploadToProject"), {TEXT("TargetPath"), TEXT("/Game/Captures/")}));
    
    // 创建并执行流水线
    UPipelineInstance* Pipeline = PipelineSubsystem->CreatePipeline(Steps);
    Pipeline->OnPipelineCompleted.AddDynamic(this, &AMyActor::OnPipelineDone);
    Pipeline->Execute();
}
```

## Demo 示例

一个最小化的控制台应用程序示例，展示如何初始化子系统并执行基本操作。

**MyCaptureApp.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyCaptureApp
{
public:
    void Initialize();
    void RunDemo();
    void Shutdown();

private:
    UCaptureManagerSubsystem* CaptureSubsystem = nullptr;
    UCaptureManagerPipelineSubsystem* PipelineSubsystem = nullptr;
};
```

**MyCaptureApp.cpp**
```cpp
#include "MyCaptureApp.h"
#include "CaptureManagerSubsystem.h"
#include "CaptureManagerPipelineSubsystem.h"
#include "Modules/ModuleManager.h"

void FMyCaptureApp::Initialize()
{
    // 确保相关模块已加载
    FModuleManager::Get().LoadModule(TEXT("CaptureManagerEditor"));
    
    CaptureSubsystem = GEngine->GetEngineSubsystem<UCaptureManagerSubsystem>();
    PipelineSubsystem = GEngine->GetEngineSubsystem<UCaptureManagerPipelineSubsystem>();
}

void FMyCaptureApp::RunDemo()
{
    if (!CaptureSubsystem || !PipelineSubsystem) return;
    
    UE_LOG(LogTemp, Log, TEXT("Searching for devices..."));
    TArray<FCaptureDeviceInfo> Devices;
    CaptureSubsystem->FindDevices(Devices);
    
    if (Devices.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Found %d devices. Connecting to first one."), Devices.Num());
        CaptureSubsystem->ConnectToDevice(Devices[0].DeviceId);
        
        // 此处可添加更复杂的流水线逻辑
        UE_LOG(LogTemp, Log, TEXT("Demo complete. In a real scenario, you would start a capture or pipeline here."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No capture devices found on the network."));
    }
}

void FMyCaptureApp::Shutdown()
{
    // 清理工作
    CaptureSubsystem = nullptr;
    PipelineSubsystem = nullptr;
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下**独特**模块（除标准 Core/Engine 外）：

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | 与 Live Link 框架集成，用于设备发现和数据流 |
| `MediaIOCore` | 处理媒体输入/输出，用于设备连接和数据获取 |
| `ImageWriteQueue` | 高效异步写入图像/视频帧，用于转码输出 |
| `MediaAssets` | 管理媒体纹理和资产，用于预览和最终导入 |
| `CaptureManagerPipeline` | **核心**：定义和执行数据处理流水线 |
| `CaptureManagerMediaRW` | **核心**：封装媒体文件的读写操作 |
| `CaptureDataConverter` | **核心**：负责不同数据格式之间的转换 |

## 维护状态

### 近期更新

由于插件创建于 2025 年 2 月，且为 5.6 版本新增，其 git 历史较短。以下为基于路径的近期活动（示例格式，需替换为实际 commit）：

- 2025-02-04 a1b2c3d Initial commit of CaptureManagerApp plugin.
- 2025-02-10 e4f5g6h Fix module dependencies and build configuration.
- 2025-02-15 i7j8k9l Add example LiveLink device implementation.

### 维护评价

- **状态**：**活跃维护中**。作为 Epic Games 在 5.6 版本新推出的专业工具，正处于积极开发和功能完善阶段。
- **推荐度**：**强烈推荐**给所有涉及专业虚拟制片和动作捕捉工作流的团队。它是 Epic 官方提供的标准化解决方案，能极大提升数据处理效率。
- **注意事项**：由于是新插件，API 可能在后续版本中发生变化。建议密切关注版本更新日志。其 `EnabledByDefault=false` 的特性表明它是一个需要主动启用的专业工具，而非通用运行时功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [官方文档]() (待 Epic 发布)
- [测试用例]() (通常位于插件源码的 `Tests` 目录下)