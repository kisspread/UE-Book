# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产文件） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

---

## 用途

CaptureManagerApp 是一个面向虚拟制片（Virtual Production）的**捕获设备管理与数据摄取平台**。它解决的核心问题是：在虚拟制片工作流中，如何统一管理多种捕获设备（如 iPhone 面部捕捉 LiveLink Face、立体相机阵列等），并将这些设备产生的原始数据（视频、音频、元数据）经过下载、转码、上传的完整流水线，最终导入到 Unreal Engine 中。

该插件基于 UE 的 **LiveLink** 体系构建，通过 Capability（能力）模式将设备抽象化——任何实现了 `ILiveLinkDeviceCapability_Ingest` 接口的 LiveLink 设备都可以参与 Capture Manager 的摄取工作流。整个数据流为：

```
捕获设备 → 列出 Takes → 下载原始数据 → 转码 → 上传至 UE/UEFN 客户端
```

**本文档聚焦于 `LiveLinkCapabilities` 模块**，该模块定义了摄取工作流的核心接口和数据结构。

---

## 使用场景

- 你在做虚拟制片，使用 iPhone + LiveLink Face 进行面部动作捕捉 → 用 CaptureManagerApp 管理和摄取捕获数据
- 你有立体相机阵列拍摄的多视角视频需要批量导入 UE → 用 CaptureManagerApp 的摄取流水线处理
- 你需要为自定义捕获设备接入 Capture Manager 工作流 → 实现 `ILiveLinkDeviceCapability_Ingest` 接口
- 你需要将捕获数据下载到本地后稍后再导入 → 使用 `Download` 模式（仅下载不转码上传）
- 你需要监控摄取进度和处理错误 → 使用 ProcessHandle 的进度回调和错误报告机制

---

## 模块总览

| 模块 | 类型 | 职责 |
|---|---|---|
| `LiveLinkCapabilities` | Runtime | **核心接口层**——定义摄取能力接口、Take 信息、摄取选项、事件系统 |
| `CaptureManagerPipeline` | Runtime | 摄取流水线的具体实现（下载、转码、上传步骤） |
| `CaptureDataConverter` | Runtime | 捕获数据格式转换（视频/音频转码） |
| `CaptureManagerMediaRW` | Runtime | 媒体文件读写操作 |
| `CaptureManagerUnrealEndpoint` | Runtime | 与 UE/UEFN 客户端的连接和数据上传 |
| `CaptureManagerSettings` | Runtime | 插件全局设置和配置 |
| `CaptureManagerEditor` | Runtime | 编辑器 UI（设备管理面板、Take 列表面板） |
| `IngestLiveLinkDevice` | Runtime | 基于摄取能力的 LiveLink 设备实现 |
| `ExampleLiveLinkDevices` | Runtime | 示例 LiveLink 设备实现（供开发者参考） |
| `LiveLinkFaceMetadata` | Runtime | LiveLink Face（iPhone 面部捕捉）的元数据解析 |
| `StereoCameraMetadata` | Runtime | 立体相机的元数据解析 |

---

## LiveLinkCapabilities 模块详解

该模块是整个 Capture Manager 的**接口契约层**，定义了所有摄取相关的能力接口、数据结构、事件和选项。设备厂商或开发者需要实现这些接口来接入 Capture Manager 工作流。

### 核心接口：ILiveLinkDeviceCapability_Ingest

这是摄取工作流的核心接口，所有支持数据摄取的 LiveLink 设备都必须实现此接口。

```
┌─────────────────────────────────────────────────┐
│         ILiveLinkDeviceCapability_Ingest         │
├─────────────────────────────────────────────────┤
│  UpdateTakeList()           ← 刷新设备上的 Take 列表  │
│  GetTakeIdentifiers()       ← 获取所有 Take ID       │
│  GetTakeInformation(id)     ← 获取 Take 元数据       │
│  CreateIngestProcess(id)    ← 创建摄取进程            │
│  RunIngestProcess(handle)   ← 执行摄取（下载+转码+上传）│
│  CancelIngestProcess(handle)← 取消摄取               │
└─────────────────────────────────────────────────┘
         │ 继承 FCaptureEventSource
         ▼
┌─────────────────────────────────────────────────┐
│              事件系统                              │
│  TakeAdded / TakeUpdated / TakeRemoved / Reset   │
└─────────────────────────────────────────────────┘
```

### 核心数据结构

| 类/结构体 | 说明 |
|---|---|
| `UIngestCapability_TakeInformation` | Take 元数据：设备名、Slate 名、Take 编号、时间戳 |
| `UIngestCapability_Options` | 摄取配置：工作目录、下载目录、视频/音频选项、上传目标 |
| `FIngestCapability_VideoOptions` | 视频选项：文件名前缀、格式、像素格式、旋转角度 |
| `FIngestCapability_AudioOptions` | 音频选项：文件名前缀、格式 |
| `UIngestCapability_ProcessHandle` | 摄取进程句柄，用于跟踪和控制摄取操作 |
| `UIngestCapability_ProcessResult` | 摄取结果：成功/失败状态、错误码、消息 |
| `UIngestCapability_UpdateTakeListCallback` | Take 列表更新回调 |

### 枚举类型

| 枚举 | 说明 |
|---|---|
| `EIngestCapability_ProcessConfig` | 摄取模式：`Download`（仅下载）/ `Ingest`（下载+转码+上传） |
| `EIngestCapability_ImagePixelFormat` | 像素格式：RGB/BGR/RGBA/BGRA/I444/I420/NV12/Mono 等 |
| `EIngestCapability_ImageRotation` | 图像旋转：None/CW_90/CW_180/CW_270 |

### 错误码

`FIngestCapability_Error::ECode` 定义了以下错误类型：

| 错误码 | 说明 |
|---|---|
| `Ok` | 成功 |
| `AbortedByUser` | 用户取消 |
| `InternalError` | 内部错误 |
| `InvalidArgument` | 无效参数 |
| `DownloaderError` | 下载器错误 |
| `UnrealEndpointNotFound` | 未找到 UE 端点 |
| `UnrealEndpointConnectionTimedOut` | UE 端点连接超时 |
| `UnrealEndpointUploadError` | 上传至 UE 端点失败 |
| `ConversionError` | 数据转换错误 |

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateTakeList` | 刷新设备上的 Take 列表，完成后通过回调返回 Take ID 列表 | `ILiveLinkDeviceCapability_Ingest` |
| `GetTakeIdentifiers` | 获取设备上所有 Take 的 ID 数组 | `ILiveLinkDeviceCapability_Ingest` |
| `GetTakeInformation` | 根据 Take ID 获取 Take 的元数据信息 | `ILiveLinkDeviceCapability_Ingest` |
| `CreateIngestProcess` | 为指定 Take 创建摄取进程句柄 | `ILiveLinkDeviceCapability_Ingest` |
| `RunIngestProcess` | 使用指定选项执行摄取进程 | `ILiveLinkDeviceCapability_Ingest` |
| `CancelIngestProcess` | 取消正在运行的摄取进程 | `ILiveLinkDeviceCapability_Ingest` |
| `GetDateTimeString` | 获取 Take 时间戳的 ISO8601 字符串 | `UIngestCapability_TakeInformation` |
| `IsValid` | 检查摄取结果是否有效（成功） | `UIngestCapability_ProcessResult` |
| `IsError` | 检查摄取结果是否为错误 | `UIngestCapability_ProcessResult` |

### 使用示例（蓝图描述）

**场景：从设备摄取一个 Take 到 UE**

1. **获取设备引用**：从 LiveLink 设备列表中获取目标设备（需实现 `ILiveLinkDeviceCapability_Ingest`）
2. **刷新 Take 列表**：调用 `UpdateTakeList`，传入 `FUpdateTakeListCallback` 委托
3. **在回调中**：获取返回的 Take ID 数组
4. **选择 Take**：调用 `GetTakeInformation(TakeId)` 获取 Take 详情，展示 Slate 名、Take 编号、时间等
5. **配置选项**：创建 `UIngestCapability_Options` 对象，设置：
   - `WorkingDirectory`：临时工作目录
   - `DownloadDirectory`：下载目录
   - `Video.PixelFormat`：选择 `U8_BGRA`（默认）
   - `Video.Rotation`：根据设备方向设置
   - `UploadHostName`：目标 UE 实例地址
6. **创建进程**：调用 `CreateIngestProcess(TakeId, EIngestCapability_ProcessConfig::Ingest)`
7. **绑定回调**：在 ProcessHandle 上绑定 `FProcessProgressReporter`（进度）和 `FProcessFinishReporter`（完成）
8. **执行**：调用 `RunIngestProcess(ProcessHandle, Options)`
9. **处理结果**：在完成回调中检查 `ProcessResult.IsValid()` 或 `ProcessResult.IsError()`

---

## C++ 用法

### 头文件引入

```cpp
#include "Ingest/LiveLinkDeviceCapability_Ingest.h"
#include "Ingest/IngestCapability_Options.h"
#include "Ingest/IngestCapability_TakeInformation.h"
#include "Ingest/IngestCapability_ProcessHandle.h"
#include "Ingest/IngestCapability_Events.h"
```

### 基本用法：实现摄取能力接口

以下展示如何为自定义 LiveLink 设备实现 `ILiveLinkDeviceCapability_Ingest` 接口。

```cpp
// MyCaptureDevice.h
#pragma once

#include "LiveLinkDevice.h"
#include "Ingest/LiveLinkDeviceCapability_Ingest.h"
#include "MyCaptureDevice.generated.h"

UCLASS()
class UMyCaptureDevice : public ULiveLinkDevice, public ILiveLinkDeviceCapability_Ingest
{
    GENERATED_BODY()

public:
    // 刷新设备上的 Take 列表
    virtual void UpdateTakeList_Implementation(
        UIngestCapability_UpdateTakeListCallback* InCallback) override
    {
        // 从设备获取 Take 列表...
        TArray<int32> TakeIds = { 1, 2, 3 };
        
        // 为每个 Take 添加元数据
        for (int32 Id : TakeIds)
        {
            FTakeMetadata Metadata;
            Metadata.DeviceName = TEXT("MyDevice");
            Metadata.SlateName = TEXT("Shot01");
            Metadata.TakeNumber = Id;
            AddTake(Metadata);
        }
        
        // 通过回调通知完成
        ExecuteUpdateTakeListCallback(InCallback, GetTakeIdentifiers());
    }

    // 下载 Take 数据
    virtual void RunDownloadTake(
        const UIngestCapability_ProcessHandle* InProcessHandle,
        const UIngestCapability_Options* InIngestOptions) override
    {
        // 实现从设备下载数据到 InIngestOptions->DownloadDirectory...
        // 完成后报告进度
        ExecuteProcessProgressReporter(InProcessHandle, 1.0);
    }

    // 转码并上传 Take 数据
    virtual void RunConvertAndUploadTake(
        const UIngestCapability_ProcessHandle* InProcessHandle,
        const UIngestCapability_Options* InIngestOptions) override
    {
        // 实现转码和上传逻辑...
        TValueOrError<void, FIngestCapability_Error> Result = 
            MakeValue(); // 成功
        ExecuteProcessFinishedReporter(InProcessHandle, MoveTemp(Result));
    }
};
```

### 进阶用法：使用事件系统监听 Take 变化

```cpp
// 监听 Take 生命周期事件
void SetupEventListeners(ILiveLinkDeviceCapability_Ingest* IngestCapability)
{
    // 监听 Take 添加事件
    IngestCapability->AddEventHandler<FIngestCapability_TakeAddedEvent>(
        [](const FIngestCapability_TakeAddedEvent& Event)
        {
            UE_LOG(LogTemp, Log, TEXT("Take %d added"), Event.TakeId);
        });

    // 监听 Take 更新事件
    IngestCapability->AddEventHandler<FIngestCapability_TakeUpdatedEvent>(
        [](const FIngestCapability_TakeUpdatedEvent& Event)
        {
            UE_LOG(LogTemp, Log, TEXT("Take %d updated"), Event.TakeId);
        });

    // 监听 Take 移除事件
    IngestCapability->AddEventHandler<FIngestCapability_TakeRemovedEvent>(
        [](const FIngestCapability_TakeRemovedEvent& Event)
        {
            UE_LOG(LogTemp, Log, TEXT("Take %d removed"), Event.TakeId);
        });

    // 监听 Take 列表重置事件
    IngestCapability->AddEventHandler<FIngestCapability_TakeListResetEvent>(
        [](const FIngestCapability_TakeListResetEvent& Event)
        {
            UE_LOG(LogTemp, Log, TEXT("Take list reset"));
        });
}
```

### 进阶用法：仅下载模式（延迟摄取）

```cpp
// 使用 Download 模式：仅下载数据，不转码上传
void DownloadOnly(ILiveLinkDeviceCapability_Ingest* Device, int32 TakeId)
{
    // 创建仅下载的进程
    UIngestCapability_ProcessHandle* Handle = Device->CreateIngestProcess(
        TakeId, EIngestCapability_ProcessConfig::Download);

    // 配置选项
    UIngestCapability_Options* Options = NewObject<UIngestCapability_Options>();
    Options->DownloadDirectory = TEXT("/Users/Captures/MyTake");
    Options->WorkingDirectory = TEXT("/tmp/capture_work");

    // 绑定完成回调
    Handle->OnProcessFinished.AddDynamic(
        [](const UIngestCapability_ProcessHandle* InHandle,
           UIngestCapability_ProcessResult* InResult)
        {
            if (InResult->IsValid())
            {
                UE_LOG(LogTemp, Log, TEXT("Download completed successfully"));
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Download failed: %s (%d)"),
                    *InResult->Message.ToString(), InResult->Code);
            }
        });

    // 执行
    Device->RunIngestProcess(Handle, Options);
}
```

---

## Demo 示例

以下是一个完整的最小示例，展示如何实现一个支持摄取能力的 LiveLink 设备。

### MyCaptureDevice.h

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "LiveLinkDevice.h"
#include "Ingest/LiveLinkDeviceCapability_Ingest.h"
#include "MyCaptureDevice.generated.h"

/**
 * 示例捕获设备：实现 ILiveLinkDeviceCapability_Ingest 接口
 * 演示如何接入 Capture Manager 的摄取工作流
 */
UCLASS(BlueprintType)
class UMyCaptureDevice : public ULiveLinkDevice, public ILiveLinkDeviceCapability_Ingest
{
    GENERATED_BODY()

public:
    UMyCaptureDevice();

    // -- ILiveLinkDeviceCapability_Ingest 接口实现 --

    virtual void UpdateTakeList_Implementation(
        UIngestCapability_UpdateTakeListCallback* InCallback) override;

    virtual void CancelIngestProcess_Implementation(
        const UIngestCapability_ProcessHandle* InProcessHandle) override;

protected:
    virtual void RunDownloadTake(
        const UIngestCapability_ProcessHandle* InProcessHandle,
        const UIngestCapability_Options* InIngestOptions) override;

    virtual void RunConvertAndUploadTake(
        const UIngestCapability_ProcessHandle* InProcessHandle,
        const UIngestCapability_Options* InIngestOptions) override;

private:
    // 模拟设备上的 Take 数据
    TMap<int32, FString> LocalTakeFiles;
};
```

### MyCaptureDevice.cpp

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyCaptureDevice.h"

UMyCaptureDevice::UMyCaptureDevice()
{
    // 模拟设备上有 3 个 Take
    LocalTakeFiles.Add(1, TEXT("/device/captures/take_001.mov"));
    LocalTakeFiles.Add(2, TEXT("/device/captures/take_002.mov"));
    LocalTakeFiles.Add(3, TEXT("/device/captures/take_003.mov"));
}

void UMyCaptureDevice::UpdateTakeList_Implementation(
    UIngestCapability_UpdateTakeListCallback* InCallback)
{
    // 清除旧数据
    RemoveAllTakes();

    // 注册所有 Take
    for (const auto& Pair : LocalTakeFiles)
    {
        FTakeMetadata Metadata;
        Metadata.DeviceName = TEXT("MyCaptureDevice");
        Metadata.SlateName = FString::Printf(TEXT("Slate_%03d"), Pair.Key);
        Metadata.TakeNumber = Pair.Key;
        AddTake(Metadata);
    }

    // 通知回调
    ExecuteUpdateTakeListCallback(InCallback, GetTakeIdentifiers());
}

void UMyCaptureDevice::RunDownloadTake(
    const UIngestCapability_ProcessHandle* InProcessHandle,
    const UIngestCapability_Options* InIngestOptions)
{
    const int32 TakeId = InProcessHandle->GetTakeId();
    const FString* SourceFile = LocalTakeFiles.Find(TakeId);

    if (!SourceFile)
    {
        ExecuteProcessFinishedReporter(InProcessHandle,
            MakeError(FIngestCapability_Error(
                FIngestCapability_Error::InvalidArgument,
                FString::Printf(TEXT("Take %d not found"), TakeId))));
        return;
    }

    // 模拟下载进度
    for (int32 i = 1; i <= 10; ++i)
    {
        ExecuteProcessProgressReporter(InProcessHandle, i / 10.0);
        FPlatformProcess::Sleep(0.1f); // 模拟耗时
    }

    // 报告完成
    ExecuteProcessFinishedReporter(InProcessHandle, MakeValue());
}

void UMyCaptureDevice::RunConvertAndUploadTake(
    const UIngestCapability_ProcessHandle* InProcessHandle,
    const UIngestCapability_Options* InIngestOptions)
{
    // 模拟转码和上传
    ExecuteProcessProgressReporter(InProcessHandle, 0.5);
    FPlatformProcess::Sleep(0.5f);
    ExecuteProcessProgressReporter(InProcessHandle, 1.0);

    ExecuteProcessFinishedReporter(InProcessHandle, MakeValue());
}

void UMyCaptureDevice::CancelIngestProcess_Implementation(
    const UIngestCapability_ProcessHandle* InProcessHandle)
{
    // 实现取消逻辑（设置取消标志等）
    ExecuteProcessFinishedReporter(InProcessHandle,
        MakeError(FIngestCapability_Error(
            FIngestCapability_Error::AbortedByUser,
            TEXT("Cancelled by user"))));
}
```

---

## 模块依赖

`LiveLinkCapabilities` 模块的依赖关系（从头文件 include 推断）：

| 模块 | 用途 |
|---|---|
| `LiveLink` | 提供 `ULiveLinkDevice` 和 `ULiveLinkDeviceCapability` 基类 |
| `CaptureManagerTakeMetadata` | 提供 `FTakeMetadata` 结构体（来自 `CaptureManagerPipeline` 或同级模块） |
| `Async` | 提供 `TManagedDelegate`、`FCaptureEvent`、`FTaskProgress` 等异步工具 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

---

## 维护状态

### 近期更新

```
- f89d77efed22 Additional non-unity fixes from removing GCObject.h from StrongObjectPtr.h
- 641e6080b809 Make parts of CPSLiveLinkDevice public
- ed9a1bc76105 Proper handling of the enum class for Ingest Capability
```

- `f89d77efed22`：修复非 Unity 构建问题，涉及 GCObject.h 的头文件依赖清理
- `641e6080b809`：将 CPSLiveLinkDevice 的部分接口公开化，扩展 API 可用性
- `ed9a1bc76105`：修复 Ingest Capability 中枚举类的正确处理方式

### 维护评价

- **创建时间**：2025-02-04，插件非常新（约 1 年）
- **活跃度**：**活跃维护中**——近期有功能性更新和 API 调整
- **代码质量**：接口设计清晰，采用 Capability 模式解耦设备与工作流，事件系统完善
- **已知限制**：
  - 插件较新，API 可能仍在演进中（从近期 commit 可见接口调整）
  - 文档和示例相对有限，需要参考 `ExampleLiveLinkDevices` 模块
- **推荐程度**：✅ **推荐使用**——如果你在做虚拟制片且需要管理捕获设备数据摄取，这是 Epic 官方的标准解决方案。注意关注 API 变化。

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [LiveLinkCapabilities 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/LiveLinkCapabilities)
- [ExampleLiveLinkDevices 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/ExampleLiveLinkDevices)（示例设备实现，推荐参考）