# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

Capture Manager App 是一个面向虚拟制作（Virtual Production）流程的综合性数据管理插件。它并非一个单一功能的组件，而是一个**应用程序框架**，旨在解决从物理世界捕获数据到在 Unreal Engine 中使用的完整工作流问题。

其核心功能是：
1.  **设备控制与监控**：连接并管理各种捕获设备（如 Live Link Face 应用、立体相机等）。
2.  **数据获取与转码**：从设备获取原始的视频、音频和元数据（如时间码、面部捕捉数据），并将其转码为 UE 可用的格式。
3.  **数据上传与导入**：将处理后的数据上传至 UE 项目，并触发导入流程，使其成为引擎内可用的资产。

该插件的存在是为了**标准化和自动化**虚拟制作中繁琐的数据采集和处理环节，让艺术家和技术人员能够更专注于创意工作，而不是手动处理文件格式转换和数据传输。

## 使用场景

-   你的团队使用 **Live Link Face** 应用进行面部动作捕捉，需要将录制的视频和音频数据自动导入到 UE 项目中。
-   你使用**立体相机**进行拍摄，需要将左右眼的视频流与时间码同步，并转换为 UE 可用的媒体资产。
-   你需要一个**统一的界面**来管理多个捕获设备，监控其状态，并批量处理录制的“Take”。
-   你的虚拟制作管线需要**自动化**从拍摄到引擎内预览的流程，减少人工干预和错误。

## 蓝图用法

本插件主要通过继承和实现接口来扩展，而非提供大量独立的蓝图节点。核心逻辑封装在 C++ 基类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnDeviceAdded` | 当设备被添加到管理器时调用。子类可重写此函数以初始化设备特定资源。 | `UBaseIngestLiveLinkDevice` |
| `OnDeviceRemoved` | 当设备从管理器移除时调用。子类可重写此函数以清理资源。 | `UBaseIngestLiveLinkDevice` |
| `IngestTake` | **核心函数**。启动一个 Take 的完整摄取流程（下载、转换、上传）。 | `UBaseIngestLiveLinkDevice` |
| `GetFullTakePath` | **必须实现**。返回指定 Take 在本地文件系统中的完整路径。 | `UBaseIngestLiveLinkDevice` |
| `RunDownloadTake` | **必须实现**。定义如何从设备下载 Take 数据。 | `UBaseIngestLiveLinkDevice` |
| `RunConvertAndUploadTake` | **必须实现**。定义如何将下载的数据转换并上传到 UE。 | `UBaseIngestLiveLinkDevice` |
| `CancelIngest` | 取消正在进行的 Take 摄取过程。 | `UBaseIngestLiveLinkDevice` |

### 使用示例（蓝图描述）

由于核心功能是通过 C++ 继承实现的，蓝图中主要作为配置和触发点：
1.  在项目中创建一个继承自 `UBaseIngestLiveLinkDevice` 的蓝图类（例如 `BP_MyCaptureDevice`）。
2.  在蓝图中重写 `GetFullTakePath`、`RunDownloadTake` 和 `RunConvertAndUploadTake` 函数，实现具体的设备通信和数据处理逻辑。
3.  在另一个管理器蓝图或 UI 中，实例化 `BP_MyCaptureDevice`，并调用其 `IngestTake` 函数来启动数据摄取流程。
4.  可以通过 `OnDeviceAdded` 和 `OnDeviceRemoved` 事件来管理设备连接状态。

## C++ 用法

### 头文件引入

```cpp
#include "BaseIngestLiveLinkDevice.h"
```

### 基本用法

创建一个自定义的 Live Link 设备类，继承自 `UBaseIngestLiveLinkDevice` 并实现必要的虚函数。

```cpp
// MyCaptureDevice.h
#pragma once

#include "BaseIngestLiveLinkDevice.h"
#include "MyCaptureDevice.generated.h"

UCLASS(BlueprintType)
class UMyCaptureDevice : public UBaseIngestLiveLinkDevice
{
    GENERATED_BODY()

public:
    // 设备添加/移除时的回调
    virtual void OnDeviceAdded() override;
    virtual void OnDeviceRemoved() override;

protected:
    // 必须实现：返回 Take 数据的本地路径
    virtual FString GetFullTakePath(UE::CaptureManager::FTakeId InTakeId) const override;

    // 必须实现：定义下载逻辑
    virtual void RunDownloadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions) override;

    // 必须实现：定义转换和上传逻辑
    virtual void RunConvertAndUploadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions) override;
};
```

```cpp
// MyCaptureDevice.cpp
#include "MyCaptureDevice.h"

void UMyCaptureDevice::OnDeviceAdded()
{
    Super::OnDeviceAdded();
    // 初始化设备连接，例如：建立网络连接，初始化硬件驱动
    UE_LOG(LogTemp, Log, TEXT("MyCaptureDevice added. Initializing..."));
}

void UMyCaptureDevice::OnDeviceRemoved()
{
    Super::OnDeviceRemoved();
    // 清理设备连接
    UE_LOG(LogTemp, Log, TEXT("MyCaptureDevice removed. Cleaning up..."));
}

FString UMyCaptureDevice::GetFullTakePath(UE::CaptureManager::FTakeId InTakeId) const
{
    // 根据 TakeId 返回设备上或本地缓存中的文件路径
    // 例如：FString::Printf(TEXT("C:/Captures/Take_%d.mp4"), InTakeId);
    return TEXT("Path/To/Your/Take.mp4");
}

void UMyCaptureDevice::RunDownloadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions)
{
    // 实现从设备下载数据的逻辑
    // 可以调用基类的 IngestTake 来使用默认的转换上传流程，或者完全自定义
    // 例如：通过网络协议从设备拉取文件到本地缓存
    UE_LOG(LogTemp, Log, TEXT("Downloading take data..."));

    // 下载完成后，通常需要调用 IngestTake 来触发后续的转换和上传
    // IngestTake(InProcessHandle, InIngestOptions, TaskProgress);
}

void UMyCaptureDevice::RunConvertAndUploadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions)
{
    // 实现将下载的数据转换并上传到 UE 的逻辑
    // 这里可以调用 CaptureDataConverter 等模块的功能
    UE_LOG(LogTemp, Log, TEXT("Converting and uploading take data to UE..."));
}
```

### 进阶用法

结合 `FCaptureExtractVideoInfo` 工具类来提取视频文件的时间码和帧率信息，用于在转换流程中进行同步。

```cpp
#include "Utils/CaptureExtractTimecode.h"

void UMyCaptureDevice::RunConvertAndUploadTake(...)
{
    FString TakePath = GetFullTakePath(CurrentTakeId);
    
    // 使用工具类提取视频信息
    auto VideoInfoResult = FCaptureExtractVideoInfo::Create(TakePath);
    if (VideoInfoResult.HasValue())
    {
        const FCaptureExtractVideoInfo& VideoInfo = VideoInfoResult.GetValue();
        FFrameRate FrameRate = VideoInfo.GetFrameRate();
        FTimecode Timecode = VideoInfo.GetTimecode();
        
        // 使用提取到的帧率和时间码信息来指导后续的转换和同步过程
        UE_LOG(LogTemp, Log, TEXT("Extracted FrameRate: %s, Timecode: %s"), 
            *FrameRate.ToPrettyText().ToString(), 
            *Timecode.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to extract video info: %d"), 
            static_cast<int32>(VideoInfoResult.GetError()));
    }
    
    // ... 继续转换和上传逻辑
}
```

## Demo 示例

一个最小的自定义设备实现，仅打印日志以演示流程。

```cpp
// SimpleCaptureDevice.h
#pragma once

#include "BaseIngestLiveLinkDevice.h"
#include "SimpleCaptureDevice.generated.h"

UCLASS(BlueprintType, MinimalAPI)
class USimpleCaptureDevice : public UBaseIngestLiveLinkDevice
{
    GENERATED_BODY()

public:
    virtual void OnDeviceAdded() override;
    virtual void OnDeviceRemoved() override;

protected:
    virtual FString GetFullTakePath(UE::CaptureManager::FTakeId InTakeId) const override;
    virtual void RunDownloadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions) override;
    virtual void RunConvertAndUploadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions) override;
};
```

```cpp
// SimpleCaptureDevice.cpp
#include "SimpleCaptureDevice.h"

void USimpleCaptureDevice::OnDeviceAdded()
{
    Super::OnDeviceAdded();
    UE_LOG(LogTemp, Display, TEXT("[SimpleCaptureDevice] Device Added."));
}

void USimpleCaptureDevice::OnDeviceRemoved()
{
    Super::OnDeviceRemoved();
    UE_LOG(LogTemp, Display, TEXT("[SimpleCaptureDevice] Device Removed."));
}

FString USimpleCaptureDevice::GetFullTakePath(UE::CaptureManager::FTakeId InTakeId) const
{
    // 返回一个示例路径
    return FString::Printf(TEXT("/Game/Captures/Take_%d"), InTakeId);
}

void USimpleCaptureDevice::RunDownloadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions)
{
    UE_LOG(LogTemp, Display, TEXT("[SimpleCaptureDevice] Simulating download for take..."));
    // 模拟下载完成，直接调用基类的 IngestTake 进行后续处理
    // 注意：实际使用中，这里需要确保数据已下载到 GetFullTakePath 返回的路径
    // IngestTake(InProcessHandle, InIngestOptions, MakeShared<UE::CaptureManager::FTaskProgress>());
}

void USimpleCaptureDevice::RunConvertAndUploadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions)
{
    UE_LOG(LogTemp, Display, TEXT("[SimpleCaptureDevice] Simulating conversion and upload..."));
    // 这里应调用 CaptureDataConverter 等模块的功能进行实际转换
}
```

## 模块依赖

本插件模块众多，依赖关系复杂。以下是 `IngestLiveLinkDevice` 模块的关键依赖（基于头文件推断）：

| 模块 | 用途 |
|---|---|
| `LiveLinkDevice` | 提供 `ULiveLinkDevice` 基类，是所有 Live Link 设备的根基。 |
| `LiveLinkCapabilities` | 提供设备能力接口，如 `ILiveLinkDeviceCapability_Ingest`。 |
| `CaptureManagerPipeline` | 提供摄取流程管理、任务进度跟踪（`FTaskProgress`）等核心管道功能。 |
| `CaptureManagerTakeMetadata` | 提供 Take 元数据解析相关的结构体和错误类型。 |
| `MediaUtils` | 提供媒体相关的工具类，如 `EMediaTexturePixelFormat`。 |

**注意**：完整的插件功能还需要其他模块（如 `CaptureDataConverter` 用于格式转换，`CaptureManagerUnrealEndpoint` 用于与 UE 通信）协同工作。

## 维护状态

### 近期更新

```
- 869b68f6ef3d Assumption that ensure will most likely never happen was wrong which is why it is promoted to user error.
- fdaf85b60939 [Capture Manager] Fixed several crashes while aborting take upload.
- 363783e2d023 Put quotes around file paths passed to ffmpeg and ffprobe
```

*   `869b68f6ef3d`: 将一个原本认为不太可能发生的 `ensure` 断言提升为用户可见的错误，提高了稳定性。
*   `fdaf85b60939`: 修复了在中止 Take 上传过程中发生的多个崩溃问题，增强了流程的健壮性。
*   `363783e2d023`: 修复了传递给外部工具（ffmpeg/ffprobe）的文件路径未加引号的问题，避免了路径中包含空格时的错误。

### 维护评价

-   **创建时间**：插件非常新（约1年），属于 UE 5.6 周期引入的功能。
-   **更新频率**：近期有更新，但主要集中在**错误修复和稳定性改进**，尚未看到重大新功能提交。
-   **活跃度**：处于**维护中**状态，开发团队在持续修复问题。
-   **已知问题**：从 commit 历史看，上传中止流程曾存在稳定性问题，现已修复。作为新功能，可能还有其他边界情况未被发现。
-   **推荐使用**：**推荐**。这是 Epic 官方为虚拟制作流程提供的标准化解决方案。虽然较新，但它是解决特定工作流（设备数据摄取）的权威方案。对于需要此功能的团队，建议采用并关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [官方文档]() (暂无)
- [测试用例]() (暂未在插件目录内发现标准测试文件)