# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟捕获管理器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产，UI 界面） |
| 模块 | `CaptureManagerEditor` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

CaptureManagerApp 是虚幻引擎虚拟制片管线中的核心采集与管理工具。它提供了一个完整的图形化界面（集成在 LiveLinkHub 中），用于集中控制各类动作捕捉设备、管理采集到的数据（Takes）、并自动化处理数据转码、上传和导入虚幻引擎的流程。

**核心问题解决**：在虚拟制片中，需要从多个不同的捕获设备（如头戴式摄像头、表演捕捉系统）中同步采集数据，然后经过一系列复杂的处理（如视频转码、音频提取）才能导入引擎使用。这个插件通过统一的界面和自动化流程，大大简化了这一繁琐的工作。

## 使用场景

- 你是虚拟制片团队的技术美术或管线开发人员 → 需要一个统一的工具来管理多个捕捉设备的数据采集和处理流程。
- 你的制作需要使用动作捕捉数据（如 LiveLink Face、面部捕捉头盔） → 用 CaptureManagerApp 来接收、查看和管理这些设备的采集数据。
- 你需要将采集到的视频、音频数据自动转换成虚幻引擎可用的格式（如将 MOV 转为 PNG 序列和 WAV 音频），并自动上传到虚幻引擎的 Media Pipeline 中进行导入 → 使用此插件的 Ingest 管理功能。
- 你需要同时管理多个捕获设备的连接状态、开始/停止采集、查看采集队列 → 使用此插件的设备管理和队列视图。

## 蓝图用法

此插件的核心 UI 逻辑主要封装在 `FCaptureManagerPanelController` 和相关的 Slate Widget 中，直接暴露给蓝图的公开节点相对较少。其主要蓝图接口是通过 `ULiveLinkHubCaptureDevice` 和 `ULiveLinkHubCaptureDeviceFactory` 提供的，用于通过蓝图脚本化地控制捕获设备。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateDeviceByClass` | 根据指定的设备类创建一个捕获设备实例 | `ULiveLinkHubCaptureDeviceFactory` |
| `Start` | 启动指定捕获设备的采集会话 | `ULiveLinkHubCaptureDevice` |
| `Stop` | 停止指定捕获设备的采集会话 | `ULiveLinkHubCaptureDevice` |
| `FetchTakes` | 从指定捕获设备获取可采集的 Take 列表及其元数据 | `ULiveLinkHubCaptureDevice` |
| `DownloadTake` | 从设备下载指定的 Take 到本地目录 | `ULiveLinkHubCaptureDevice` |
| `IngestTake` | 将指定的 Take 根据选项进行转码处理 | `ULiveLinkHubCaptureDevice` |

### 使用示例（蓝图描述）

1.  **创建设备并开始采集**：
    *   从 `ULiveLinkHubCaptureDeviceFactory` 的 `CreateDeviceByClass` 节点创建一个设备对象。
    *   调用该设备对象的 `Start` 节点（可设置超时时间），启动采集。
2.  **获取 Take 列表并导入**：
    *   在设备对象上调用 `FetchTakes`，返回一个 `FLiveLinkHubFetchTakesResult` 结构，其中包含状态和 Take 元数据数组。
    *   遍历 Take 数组，为每个 Take 调用 `IngestTake` 节点，并传入一个 `UIngestCapability_Options` 对象来指定转码设置（如输出图片格式、音频格式）。
3.  **管理 Ingest 设置**：
    *   可以创建 `UIngestJobSettings` 对象，并修改其 `ImageFormat`、`AudioFormat`、`UploadHostName` 等属性。
    *   通过 `SIngestJobProcessor` 的蓝图可访问接口（但通常其核心操作是 C++ 层面的队列管理）来添加或管理作业。

## C++ 用法

插件的 C++ 接口主要分为两层：**管理控制器层**（`FCaptureManagerPanelController`）和**底层 Ingest 管线层**（`FIngestJobProcessor`、`FIngestPipelineManager` 等）。

### 头文件引入

```cpp
// 访问核心控制器
#include "UI/CaptureManagerPanelController.h"
// 访问 Ingest 作业和处理器
#include "IngestManagement/IngestJob.h"
#include "IngestManagement/IngestJobProcessor.h"
// 访问蓝图设备接口
#include "Scripting/ULiveLinkHubCaptureDevice.h"
```

### �本用法

以下示例展示了如何通过 C++ 代码使用插件的核心管理类来添加作业到处理队列。

**来源文件路径**：`Private/UI/CaptureManagerPanelController.cpp`, `Private/IngestManagement/IngestJobProcessor.h`

```cpp
// 假设已经通过某种方式获取到捕获设备和 Take 信息
FGuid CaptureDeviceId = ...;
UE::CaptureManager::FTakeId TakeId = ...;
FTakeMetadata TakeMetadata = ...;

// 1. 获取 Ingest 管线管理器和作业处理器（通常从 Panel Controller 获取）
TSharedRef<UE::CaptureManager::FIngestPipelineManager> PipelineManager = PanelController->GetIngestPipelineManager();
TSharedRef<UE::CaptureManager::SIngestJobProcessor> JobProcessorWidget = PanelController->GetIngestJobProcessorWidget();
TSharedRef<UE::CaptureManager::FIngestJobProcessor> JobProcessor = JobProcessorWidget->GetIngestJobProcessor(); // 假设有此访问方法

// 2. 配置一个作业设置
UE::CaptureManager::FIngestJob::FSettings JobSettings;
JobSettings.VideoSettings.Format = EOutputImageFormat::PNG;
JobSettings.AudioSettings.Format = EAudioFormat::WAV;
JobSettings.WorkingDirectory = FPaths::ProjectSavedDir() / TEXT("CaptureManager_Temp");

// 3. 创建一个 Ingest 作业
TSharedRef<UE::CaptureManager::FIngestJob> NewJob = MakeShared<UE::CaptureManager::FIngestJob>(
    CaptureDeviceId,
    TakeId,
    TakeMetadata,
    EIngestCapability_ProcessConfig::Default, // 使用默认管线
    JobSettings
);

// 4. 将作业添加到处理器队列
TArray<TSharedRef<UE::CaptureManager::FIngestJob>> JobsToAdd;
JobsToAdd.Add(NewJob);
int32 NumAdded = JobProcessor->AddJobs(JobsToAdd);

// 5. 如果处理器未运行，启动处理
if (!JobProcessor->IsProcessing())
{
    JobProcessor->StartProcessing();
}

// 监听作业状态变化
JobProcessor->OnJobProcessingStateChanged().BindLambda([](FGuid JobGuid, UE::CaptureManager::FIngestJob::EProcessingState State) {
    UE_LOG(LogCaptureManager, Log, TEXT("Job %s State Changed to: %s"), *JobGuid.ToString(), LexToString(State));
});
```

### 进阶用法

以下示例展示了如何通过 `ULiveLinkHubCaptureDevice` 蓝图 API 的 C++ 对等方法来控制设备和处理 Take。

**来源文件路径**：`Private/Scripting/ULiveLinkHubCaptureDevice.h`, `Private/Scripting/ULiveLinkHubCaptureDevice.cpp`

```cpp
// 创建设备工厂和设备实例
ULiveLinkHubCaptureDeviceFactory* DeviceFactory = NewObject<ULiveLinkHubCaptureDeviceFactory>();
ULiveLinkHubCaptureDevice* CaptureDevice = DeviceFactory->CreateDeviceByClass(
    TEXT("MyCaptureDevice"),
    USomeLiveLinkCaptureDevice::StaticClass(),
    nullptr
);

// 启动设备采集
UIngestCapability_ProcessResult* StartResult = CaptureDevice->Start(10); // 10秒超时
if (StartResult && StartResult->IsSuccess())
{
    // 获取可用的 Take 列表
    FLiveLinkHubFetchTakesResult FetchResult = CaptureDevice->FetchTakes();
    if (FetchResult.Status && FetchResult.Status->IsSuccess())
    {
        for (const FLiveLinkHubTakeMetadata& TakeInfo : FetchResult.Takes)
        {
            // 为每个 Take 创建转码选项
            UIngestCapability_Options* ConversionSettings = NewObject<UIngestCapability_Options>();
            ConversionSettings->ImageFormat = EOutputImageFormat::JPEG;

            // 执行 Take 的转码（Ingest）
            UIngestCapability_ProcessResult* IngestResult = CaptureDevice->IngestTake(TakeInfo, ConversionSettings);
            if (IngestResult && IngestResult->IsSuccess())
            {
                UE_LOG(LogCaptureManager, Log, TEXT("Take %d ingested successfully."), TakeInfo.TakeId);
            }
        }
    }
}

// 停止设备采集
CaptureDevice->Stop();
```

## Demo 示例

以下是一个最小的 C++ 示例，演示如何实例化 `FCaptureManagerPanelController` 并获取其核心组件，用于集成到自定义工具或扩展中。

```cpp
// MyCaptureManagerTool.h
#pragma once

#include "CoreMinimal.h"

class FCaptureManagerPanelController;

class FMyCaptureManagerTool
{
public:
    FMyCaptureManagerTool();
    ~FMyCaptureManagerTool();

    void Initialize();

private:
    TSharedPtr<FCaptureManagerPanelController> PanelController;
};
```

```cpp
// MyCaptureManagerTool.cpp
#include "MyCaptureManagerTool.h"
#include "UI/CaptureManagerPanelController.h"
#include "IngestManagement/IngestPipelineManager.h"

FMyCaptureManagerTool::FMyCaptureManagerTool() = default;

FMyCaptureManagerTool::~FMyCaptureManagerTool()
{
    PanelController.Reset();
}

void FMyCaptureManagerTool::Initialize()
{
    // 创建插件的核心面板控制器单例
    PanelController = FCaptureManagerPanelController::MakeInstance();

    // 获取管线管理器，可用于查询可用的处理管线
    TSharedRef<UE::CaptureManager::FIngestPipelineManager> PipelineManager = PanelController->GetIngestPipelineManager();
    const TArray<UE::CaptureManager::FPipelineDetails>& Pipelines = PipelineManager->GetPipelines();
    for (const auto& Pipeline : Pipelines)
    {
        UE_LOG(LogTemp, Log, TEXT("Available Pipeline: %s"), *Pipeline.DisplayName.ToString());
    }

    // 获取作业处理器控件，可用于嵌入到自定义UI
    TSharedRef<SIngestJobProcessor> ProcessorWidget = PanelController->GetIngestJobProcessorWidget();
    // 此时 ProcessorWidget 是一个有效的 Slate Widget，可以嵌入到你的工具窗口中
}
```

## 模块依赖

此插件包含多个模块，各模块的依赖关系已在各自的 `Build.cs` 中定义。对于使用者（希望在其他插件或模块中引用此插件功能）而言，需要根据你要使用的功能来添加依赖。

| 模块 | 用途 |
|---|---|
| `CaptureManagerEditor` | 主要编辑器和 UI 模块，包含 `FCaptureManagerPanelController` 和所有 Slate UI 代码。依赖 `LiveLinkCapabilities`。 |
| `LiveLinkCapabilities` | 提供与 LiveLink Hub 应用程序集成的模式工厂（`ILiveLinkHubApplicationModeFactory`）。**注意：此模块依赖 `UnrealEd`**。 |
| `CaptureManagerUnrealEndpoint` | 管理 Unreal Engine 端点（用于数据上传）。 |
| `IngestLiveLinkDevice` | 实现基于 LiveLink 的捕获设备，可能包含具体设备的实现逻辑。 |
| `CaptureManagerSettings` | 管理插件的全局设置。 |

**使用建议**：
*   如果你只是想**扩展或集成此插件的 UI**，依赖 `CaptureManagerEditor`。
*   如果你想**使用其蓝图脚本 API**，确保你的项目启用了此插件即可，蓝图节点会自动出现。
*   如果你想在 C++ 中**使用其底层管线类**（如 `FIngestJobProcessor`），你需要直接包含对应的头文件，并在你的模块 `Build.cs` 中添加对 `CaptureManagerEditor` 或相关模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 为核心模块添加了 CaptureManagerCPSClient 子模块。 |
| 2026-04-28 | `6eba47f3` | [Capture Manager] Warn when Third Party Encoder is required for ingest | 当 Ingest 过程需要第三方编码器时，现在会向用户发出警告。 |
| 2026-04-23 | `43d97726` | MediaProfile: Moved UMediaProfile and related entities to its own plugin to avoid dependency on Open | 将 UMediaProfile 相关实体迁移至独立插件，解除了对 Open 模块的依赖。 |
| 2026-04-20 | `a8e2df25` | [CaptureManager] Add auto-rotation mode to ECaptureManagerRotation | 为 `ECaptureManagerRotation` 枚举添加了自动旋转模式。 |
| 2026-04-16 | `cf2dffa4` | [CaptureManager] Fix broken LLH encoder defaults. | 修复了 LiveLink Hub 编码器默认值损坏的问题。 |

### 维护评价

*   **活跃维护**：插件于 2025 年 2 月创建，在最近的 2026 年 4 月仍有**频繁且实质性**的功能更新和 bug 修复，表明该插件处于**积极开发和维护**中。
*   **功能成熟度**：作为一个虚拟制片工作流的核心组件，其架构清晰（分层设计，模块化），近期更新集中在功能增强（如自动旋转、编码器管理）和架构优化（解耦 MediaProfile），说明功能在不断迭代和完善。
*   **已知问题**：从 commit 记录看，曾有编码器默认值损坏的问题，但已被修复。没有发现废弃或停止维护的迹象。
*   **推荐使用**：**强烈推荐**在涉及虚拟制片数据采集的 UE5 项目中使用。它是 Epic Games 官方提供的标准化解决方案，能有效提升管线效率。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [官方文档]( "") （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Tests) (如果存在)