# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 中文名 | 采集管理器应用 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CaptureManagerEditor` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

Capture Manager Application 是一个完整的虚拟制作数据采集解决方案。它提供了一个框架，用于**管理、监控和自动化从物理采集设备（如摄像机、动作捕捉系统）获取数据的全过程**。其核心功能包括：

1.  **设备管理与监控**：通过扩展的 Live Link 设备系统，集中管理多个采集设备。
2.  **数据导入流水线**：提供了标准化的接口 (`ILiveLinkDeviceCapability_Ingest`) 来执行从设备下载数据、转码（如视频格式转换）并上传到 Unreal Engine 项目中的完整工作流。
3.  **实时流预览**：通过 `ILiveLinkDeviceCapability_Streaming` 接口，设备可以提供实时媒体流，方便在编辑器中预览。
4.  **事件系统**：内置事件系统（如 `FIngestCapability_TakeAddedEvent`）来通知导入流程的状态变化（Take 的添加、更新、移除）。

它解决了虚拟制片中手动处理多源采集数据、格式转换和资产导入的繁琐问题，将这一流程自动化并集成到引擎的编辑器和运行时环境中。

## 使用场景

-   **虚拟制片团队**：你需要从多个现场摄像机或动作捕捉设备采集数据，自动将原始数据转码为引擎友好的格式，并批量导入到项目中用于后期制作。
-   **技术美术或工具程序员**：你需要为新的采集设备类型开发支持插件，利用 `LiveLinkCapabilities` 模块提供的接口快速实现数据导入和流传输功能。
-   **项目管线集成**：你希望将数据采集环节直接集成到 UE 编辑器的工作流中，通过蓝图或 C++ 控制整个采集、转码和导入过程。

## 蓝图用法

本插件的功能主要通过实现和调用 `LiveLinkCapabilities` 模块中定义的蓝图接口和类来使用。

### 核心节点

#### 导入 (Ingest) 流程
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Ingest Process` | 为指定 Take ID 创建一个导入进程句柄。`InProcessConfig` 决定是仅下载还是完整导入。 | `ILiveLinkDeviceCapability_Ingest` |
| `Run Ingest Process` | 启动一个已创建的导入进程。需要传入选项 (`UIngestCapability_Options`)。 | `ILiveLinkDeviceCapability_Ingest` |
| `Cancel Ingest Process` | 取消正在运行的导入进程。 | `ILiveLinkDeviceCapability_Ingest` |
| `Update Take List` | 请求设备更新其可用 Take（拍摄片段）列表。 | `ILiveLinkDeviceCapability_Ingest` |
| `Get Take Identifiers` | 获取设备上所有可用 Take 的 ID 列表。 | `ILiveLinkDeviceCapability_Ingest` |
| `Get Take Information` | 获取指定 Take ID 的详细信息（如设备名、场次、镜头号）。 | `ILiveLinkDeviceCapability_Ingest` |
| `Is Done` | 查询进程句柄是否已完成。 | `UIngestCapability_ProcessHandle` |
| `On Process Finish Reporter` | 进程完成时的动态委托。 | `UIngestCapability_ProcessHandle` |
| `On Process Progress Reporter` | 进程进度更新的动态委托。 | `UIngestCapability_ProcessHandle` |

#### 流传输 (Streaming) 控制
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Streaming` | 开始设备的实时流传输。 | `ILiveLinkDeviceCapability_Streaming` |
| `Stop Streaming` | 停止设备的实时流传输。 | `ILiveLinkDeviceCapability_Streaming` |
| `Is Streaming` | 查询设备是否正在流传输。 | `ILiveLinkDeviceCapability_Streaming` |
| `Get Media Source` | 获取设备提供的用于流预览的媒体源对象。 | `ILiveLinkDeviceCapability_Streaming` |

### 使用示例（蓝图描述）
1.  **获取设备并执行导入**：
    *   从 Live Link 设备列表中获取一个实现了 `ILiveLinkDeviceCapability_Ingest` 接口的设备引用。
    *   调用 `Create Ingest Process` 节点，传入 `Take ID` 和配置（如 `EIngestCapability_ProcessConfig::Ingest`），获得一个 `Process Handle`。
    *   创建一个 `UIngestCapability_Options` 对象，设置 `Working Directory`、`Download Directory` 等。
    *   连接 `Process Handle` 的 `On Process Progress Reporter` 和 `On Process Finish Reporter` 委托到自定义事件，以监控进度和结果。
    *   调用 `Run Ingest Process`，传入 `Process Handle` 和 `Options` 对象，启动导入。
2.  **管理实时流**：
    *   获取一个实现了 `ILiveLinkDeviceCapability_Streaming` 接口的设备引用。
    *   调用 `Start Streaming` 开始接收实时画面。
    *   调用 `Get Media Source` 获取媒体源，将其连接到一个 `Media Player` 或 `Media Texture` 节点以在 UI 上预览。
    *   在不需要时调用 `Stop Streaming` 释放资源。

## C++ 用法

### 头文件引入
```cpp
#include "LiveLinkCapabilitiesModule.h"
// 根据具体功能引入
#include "Ingest/LiveLinkDeviceCapability_Ingest.h"
#include "Streaming/LiveLinkDeviceCapability_Streaming.h"
#include "Ingest/IngestCapability_ProcessHandle.h"
#include "Ingest/IngestCapability_Options.h"
```

### 基本用法

以下示例展示了如何为一个自定义采集设备实现 `Ingest` 能力接口。*（基于接口定义推断）*

```cpp
// MyCaptureDevice.h
#pragma once

#include "CoreMinimal.h"
#include "LiveLinkDevice.h"
#include "Ingest/LiveLinkDeviceCapability_Ingest.h"
#include "MyCaptureDevice.generated.h"

UCLASS()
class MYMODULE_API UMyCaptureDevice : public ULiveLinkDevice, public ILiveLinkDeviceCapability_Ingest
{
	GENERATED_BODY()

public:
    // ... 其他 LiveLinkDevice 必须实现的方法 ...

    // --- 实现 ILiveLinkDeviceCapability_Ingest 接口 ---
    virtual UIngestCapability_ProcessHandle* CreateIngestProcess_Implementation(int32 InTakeId, EIngestCapability_ProcessConfig InProcessConfig) override;
    virtual void RunIngestProcess_Implementation(UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InOptions) override;
    virtual void CancelIngestProcess_Implementation(const UIngestCapability_ProcessHandle* InProcessHandle) override;
    virtual void UpdateTakeList_Implementation(UIngestCapability_UpdateTakeListCallback* InCallback) override;
    virtual void RequestAbortUpdateTakeList_Implementation() override;
    virtual UIngestCapability_TakeInformation* GetTakeInformation_Implementation(int32 InTakeId) const override;
    virtual TArray<int32> GetTakeIdentifiers_Implementation() const override;

protected:
    // 需要子类实现的核心逻辑
    virtual void RunDownloadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions) override;
    virtual void RunConvertAndUploadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions) override;
    virtual void RunUpdateTakeList(UIngestCapability_UpdateTakeListCallback* InCallback) override;
};
```

```cpp
// MyCaptureDevice.cpp
#include "MyCaptureDevice.h"
#include "Ingest/IngestCapability_ProcessHandle.h"

UIngestCapability_ProcessHandle* UMyCaptureDevice::CreateIngestProcess_Implementation(int32 InTakeId, EIngestCapability_ProcessConfig InProcessConfig)
{
    // 创建一个进程上下文，并返回由框架管理的句柄
    TUniquePtr<FIngestCapability_ProcessContext> Context = MakeUnique<FIngestCapability_ProcessContext>(InTakeId, InProcessConfig, this, FIngestCapability_ProcessContext::FPrivateToken());
    UIngestCapability_ProcessHandle* Handle = NewObject<UIngestCapability_ProcessHandle>();
    Handle->Initialize(MoveTemp(Context));
    return Handle;
}

void UMyCaptureDevice::RunDownloadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions)
{
    int32 TakeId = InProcessHandle->GetTakeId();
    FString DownloadDir = InIngestOptions->DownloadDirectory;

    // 模拟从设备下载数据的耗时操作
    // ... 使用网络或文件接口下载 TakeId 对应的数据到 DownloadDir ...

    // 下载完成后，通过 Handle 报告进度和完成状态
    InProcessHandle->OnProcessProgressReporter().ExecuteIfBound(InProcessHandle, 1.0); // 100%
    ExecuteProcessFinishedReporter(InProcessHandle, TValueOrError<void, FIngestCapability_Error>(MakeValue()));
}

// ... 其他接口方法的实现 ...
```

### 进阶用法
组合使用 `Ingest` 和 `Streaming` 能力，实现一个既能采集又能实时预览的设备。

```cpp
// MyAdvancedDevice.h
UCLASS()
class UMyAdvancedDevice : public ULiveLinkDevice, 
                          public ILiveLinkDeviceCapability_Ingest,
                          public ILiveLinkDeviceCapability_Streaming
{
    GENERATED_BODY()
    // ... 同时实现两个接口的所有纯虚函数 ...
};

// 在初始化时，可以分别调用 Init() 来初始化流能力
void UMyAdvancedDevice::Initialize(const FObjectInitializer& ObjectInitializer)
{
    Super::Initialize(ObjectInitializer);
    // 初始化流能力（由基类 ULiveLinkDeviceCapability_Streaming 提供）
    ILiveLinkDeviceCapability_Streaming::Init();
}
```

## Demo 示例

一个最小化的自定义设备实现，展示了如何集成 `Ingest` 能力。

```cpp
// MyDemoDevice.h
#pragma once

#include "LiveLinkDevice.h"
#include "Ingest/LiveLinkDeviceCapability_Ingest.h"
#include "MyDemoDevice.generated.h"

UCLASS()
class UMyDemoDevice : public ULiveLinkDevice, public ILiveLinkDeviceCapability_Ingest
{
	GENERATED_BODY()

public:
    // 必须重写的 LiveLinkDevice 虚函数（示例）
    virtual FText GetDisplayName() const override { return NSLOCTEXT("MyDevice", "DisplayName", "Demo Ingest Device"); }
    virtual void OnDeviceAdded() override {}
    virtual void OnDeviceRemoved() override {}

    // 实现 ILiveLinkDeviceCapability_Ingest 接口
    virtual UIngestCapability_ProcessHandle* CreateIngestProcess_Implementation(int32 InTakeId, EIngestCapability_ProcessConfig InProcessConfig) override;
    virtual void RunIngestProcess_Implementation(UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InOptions) override;
    virtual void CancelIngestProcess_Implementation(const UIngestCapability_ProcessHandle* InProcessHandle) override;
    virtual void UpdateTakeList_Implementation(UIngestCapability_UpdateTakeListCallback* InCallback) override;
    virtual void RequestAbortUpdateTakeList_Implementation() override;
    virtual UIngestCapability_TakeInformation* GetTakeInformation_Implementation(int32 InTakeId) const override;
    virtual TArray<int32> GetTakeIdentifiers_Implementation() const override;

protected:
    virtual void RunDownloadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions) override;
    virtual void RunConvertAndUploadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions) override;
    virtual void RunUpdateTakeList(UIngestCapability_UpdateTakeListCallback* InCallback) override;

private:
    TArray<int32> AvailableTakes = {101, 102, 103}; // 模拟可用的 Take 列表
};
```

```cpp
// MyDemoDevice.cpp
#include "MyDemoDevice.h"
#include "Ingest/IngestCapability_ProcessHandle.h"

UIngestCapability_ProcessHandle* UMyDemoDevice::CreateIngestProcess_Implementation(int32 InTakeId, EIngestCapability_ProcessConfig InProcessConfig)
{
    // 创建上下文和句柄
    auto Context = MakeUnique<FIngestCapability_ProcessContext>(InTakeId, InProcessConfig, this, FIngestCapability_ProcessContext::FPrivateToken());
    auto* Handle = NewObject<UIngestCapability_ProcessHandle>();
    Handle->Initialize(MoveTemp(Context));
    return Handle;
}

void UMyDemoDevice::RunIngestProcess_Implementation(UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InOptions)
{
    // 根据配置决定运行哪个步骤
    FIngestCapability_ProcessContext* Context = InProcessHandle->GetContext(); // 假设有获取方法
    if (Context->GetProcessConfig() & EIngestCapability_ProcessConfig::DownloadStep)
    {
        RunDownloadTake(InProcessHandle, InOptions);
    }
    // ... 后续步骤处理
}

void UMyDemoDevice::RunDownloadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions)
{
    UE_LOG(LogTemp, Warning, TEXT("DemoDevice: Starting download for Take %d to %s"), InProcessHandle->GetTakeId(), *InIngestOptions->DownloadDirectory);
    
    // 模拟下载耗时
    FPlatformProcess::Sleep(2.0f);
    
    // 报告完成
    ExecuteProcessFinishedReporter(InProcessHandle, TValueOrError<void, FIngestCapability_Error>(MakeValue()));
}

void UMyDemoDevice::RunConvertAndUploadTake(const UIngestCapability_ProcessHandle* InProcessHandle, const UIngestCapability_Options* InIngestOptions)
{
    UE_LOG(LogTemp, Warning, TEXT("DemoDevice: Converting and uploading Take %d"), InProcessHandle->GetTakeId());
    // 模拟转码上传
    FPlatformProcess::Sleep(1.5f);
    ExecuteProcessFinishedReporter(InProcessHandle, TValueOrError<void, FIngestCapability_Error>(MakeValue()));
}

void UMyDemoDevice::UpdateTakeList_Implementation(UIngestCapability_UpdateTakeListCallback* InCallback)
{
    // 模拟从设备获取列表
    FPlatformProcess::Sleep(0.5f);
    ExecuteUpdateTakeListCallback(InCallback, AvailableTakes);
    // 也可以通过 AddTake, RemoveTake 等方法增量更新
}

// ... 其他接口方法的简单实现 ...
```

## 模块依赖

本插件主要依赖于 Unreal Engine 的核心系统和 Live Link 框架。使用者的模块（例如实现自定义设备的模块）通常需要依赖 `LiveLinkCapabilities` 模块。

| 模块 | 用途 |
|---|---|
| `LiveLinkCapabilities` | 提供设备能力接口（Ingest, Streaming）和相关数据结构。**是自定义采集设备必须依赖的核心模块**。 |
| `LiveLink` | Live Link 基础框架，提供设备管理和数据交互的底层支持。 |
| `MediaUtils` | 处理媒体源（`UMediaSource`），用于流传输功能。 |
| `UnrealEd` | 提供编辑器集成相关的功能（LiveLinkCapabilities模块的依赖）。 |
| `CaptureManagerCore` | 提供底层捕获管理工具，如任务进度、停止请求器、编码器管理等。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 在CaptureManagerCore中新增了CPS客户端模块，用于与采集设备通信。 |
| 2026-04-28 | `6eba47f3` | [Capture Manager] Warn when Third Party Encoder is required for ingest | 当导入流程需要第三方编码器时现在会发出警告。 |
| 2026-04-23 | `43d97726` | MediaProfile: Moved UMediaProfile and related entities to its own plugin to avoid dependency on Open | 将媒体配置文件（MediaProfile）功能剥离为独立插件，减少耦合。 |
| 2026-04-20 | `a8e2df25` | [CaptureManager] Add auto-rotation mode to ECaptureManagerRotation | 为采集管理器的旋转枚举添加了自动旋转模式。 |
| 2026-04-16 | `cf2dffa4` | [CaptureManager] Fix broken LLH encoder defaults. | 修复了LLH编码器默认设置损坏的问题。 |

### 维护评价
- **活跃维护**：插件非常新（2025年2月创建），且在2026年4月仍有连续的功能更新和问题修复。
- **核心功能稳定**：近期的提交主要集中在功能增强（新增模块、新旋转模式）和特定问题修复（编码器默认值、依赖剥离），表明基础架构已稳定，正在进行迭代优化。
- **推荐使用**：作为 Epic Games 官方维护的虚拟制片工具链核心部分，适合在新项目或需要强大、标准化数据采集管线的项目中采用。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Tests) (推测路径)