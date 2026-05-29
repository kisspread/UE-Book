# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模块代码） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerCPSClient` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureMetadataExtraction` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

Capture Manager Core 是虚幻引擎虚拟制作流程中，用于统一管理外部捕获设备（如移动手机、摄像头阵列等）的核心功能库。它并非面向最终用户的独立插件，而是作为 `Capture Manager App` 和 `Capture Manager Editor` 插件的底层支撑。其主要解决以下问题：

1.  **设备通信**：通过实现 `CaptureProtocolStack` 和 `CaptureManagerCPSClient` 模块，封装了与捕获设备通信的协议（CPS - Capture Protocol Stack），提供了连接、状态监控、控制命令（如开始/停止录制）等标准化接口。
2.  **数据传输与处理**：负责管理捕获数据（Take）的元数据、媒体文件的读写（`CaptureManagerMediaRW`）、数据的导入与处理（`DataIngestCore`），以及格式转换（`CaptureDataConverter`）。
3.  **流程协调**：`CaptureManagerPipeline` 和 `CaptureUtils` 提供了数据处理的管道和通用工具，协调整个从设备捕获数据到引擎内可用的资产（如纹理、动画、音频）的完整流程。
4.  **共享逻辑**：将上述核心、通用的逻辑抽象出来，避免在 App（移动端）和 Editor（桌面端）插件中重复开发，确保功能一致性和可维护性。

## 使用场景

- 你正在开发或使用一个需要连接外部物理设备（如iPhone、专业相机）进行视频、深度或动作捕获的虚拟制片流程。
- 你需要在虚幻编辑器或自定义应用程序（如LiveLinkHub）中，统一管理这些捕获设备的连接、录制控制和数据回收。
- 你需要实现自定义的捕获数据导入管道，将设备捕获的原始数据转换为引擎可用的资产。

## 蓝图用法

该插件主要为C++层设计，提供核心服务。从提供的 `CaptureManagerCPSClient` 模块源码分析，其核心类 `FCPSDevice` 暴露了设备管理的完整生命周期API，这些函数通常会在编辑器或App的蓝图逻辑中被封装和调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeCPSDevice` | 静态工厂方法，创建一个连接指定IP和端口的设备实例。 | `FCPSDevice` |
| `InitiateConnect` | 异步发起与设备的连接。 | `FCPSDevice` |
| `Stop` | 停止设备连接并释放资源。 | `FCPSDevice` |
| `IsConnected` | 查询设备是否已连接。 | `FCPSDevice` |
| `StartRecording` | 发送指令，让连接的设备开始录制新的Take（可配置板岩名、Take编号等）。 | `FCPSDevice` |
| `StopRecording` | 发送指令，让设备停止当前录制。 | `FCPSDevice` |
| `FetchTakeList` | 从设备获取所有已录制的Take的元数据列表。 | `FCPSDevice` |
| `FetchTake` | 根据Take名称，从设备获取单个Take的详细元数据。 | `FCPSDevice` |
| `StartExport` | 开始将指定Take的数据从设备导出到本地流（文件或内存）。 | `FCPSDevice` |
| `CancelExport` | 取消正在进行的单个Take导出。 | `FCPSDevice` |
| `CancelAllExports` | 取消所有正在进行的导出任务。 | `FCPSDevice` |
| `FetchThumbnailForTake` | 获取单个Take的缩略图数据。 | `FCPSDevice` |

### 使用示例（蓝图描述）

在编辑器蓝图中，典型工作流如下：
1.  **创建设备**：使用 `MakeCPSDevice` 节点，输入设备的IP地址和控制端口（例如 `192.168.1.100`, `22222`），获得一个设备对象引用。
2.  **建立连接**：调用 `InitiateConnect`。连接状态变化会通过 `FConnectionStateChangedEvent` 事件通知。
3.  **设备控制**：连接成功后，调用 `StartRecording` 开始录制。录制完成后，调用 `StopRecording`。
4.  **获取数据**：调用 `FetchTakeList` 获取录制完成的Take列表。选择一个Take，使用 `StartExport` 并提供一个 `FCPSFileStream`（用于写入本地磁盘）或 `FCPSDataStream`（用于内存处理）来导出数据。
5.  **清理**：流程结束或关闭编辑器时，调用 `Stop` 断开连接并释放资源。

## C++ 用法

### 头文件引入

使用 `CaptureManagerCPSClient` 模块的核心功能：
```cpp
#include “CPSDevice.h”
#include “CPSFileStream.h” // 或 “CPSDataStream.h”
```

### 基本用法

以下代码演示了如何创建设备、连接并开始一个简单的录制流程。
```cpp
// 包含必要的头文件
#include “CPSDevice.h”
#include “CPSFileStream.h”

using namespace UE::CaptureManager;

// 创建一个设备实例（在某个管理器或Actor中持有这个共享指针）
TSharedPtr<FCPSDevice> MyDevice = FCPSDevice::MakeCPSDevice(TEXT(“192.168.1.100”), 22222);

// 注册连接状态变化的回调（可选）
MyDevice->AddEventHandler<FConnectionStateChangedEvent>([](const FConnectionStateChangedEvent& Event) {
    if (Event.ConnectionState == FConnectionStateChangedEvent::EState::Connected)
    {
        UE_LOG(LogTemp, Log, TEXT(“设备已连接！”));
    }
});

// 发起连接
MyDevice->InitiateConnect();

// 在连接成功的回调或其他适当时机，开始录制
// 假设有一个函数确认连接已建立
void OnDeviceReady()
{
    if (MyDevice && MyDevice->IsConnected())
    {
        // 开始录制，板岩名为 “TestSlate”, Take编号 1
        auto Result = MyDevice->StartRecording(TEXT(“TestSlate”), 1);
        if (Result.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT(“录制指令发送成功”));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT(“开始录制失败: %s”), *Result.GetError());
        }
    }
}

// … 在一段时间后停止录制
void StopMyRecording()
{
    if (MyDevice)
    {
        MyDevice->StopRecording();
    }
}

// 清理（通常在对象销毁时）
void Cleanup()
{
    if (MyDevice)
    {
        MyDevice->Stop();
        MyDevice.Reset();
    }
}
```
*代码逻辑参考 `Public/CPSDevice.h` 中 `FCPSDevice` 类的公开接口。*

### 进阶用法：使用流式接口导出数据

`FCPSFileStream` 和 `FCPSDataStream` 是用于接收导出数据的两种流实现。`FCPSFileStream` 将数据直接写入磁盘文件，并提供进度和完成回调。
```cpp
#include “CPSDevice.h”
#include “CPSFileStream.h”

using namespace UE::CaptureManager;

TSharedPtr<FCPSDevice> Device; // 假设已连接
FTakeId TakeToExport = ...; // 通过 FetchTakeList 或 FetchTake 获取

// 创建一个文件流，指定输出目录和预期大小
FString ExportDir = FPaths::ProjectSavedDir() / TEXT(“Captures”);
uint64 ExpectedFileSize = 1024 * 1024 * 100; // 100 MB，示例值
auto FileStream = MakeUnique<FCPSFileStream>(ExportDir, ExpectedFileSize);

// 设置进度和完成回调
FileStream->SetProgressHandler([](float Progress) {
    UE_LOG(LogTemp, Log, TEXT(“导出进度: %.2f%%”), Progress * 100.0f);
});

FileStream->SetExportFinished([](TProtocolResult<void> Result) {
    if (Result.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT(“Take导出完成！”));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT(“Take导出失败: %s”), *Result.GetError());
    }
});

// 开始导出，将文件流所有权转移给设备
Device->StartExport(TakeToExport, std::move(FileStream));

// … 在某个时刻（如UI取消按钮），可以取消导出
void CancelMyExport()
{
    if (Device)
    {
        Device->CancelExport(TakeToExport);
    }
}
```
*代码逻辑参考 `Public/CPSFileStream.h` 和 `Public/CPSDevice.h` 中导出相关的方法。*

## Demo 示例

一个最小化的示例，展示如何创建设备对象、连接并打印状态。
**MyCaptureManagerActor.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “CPSDevice.h”
#include “MyCaptureManagerActor.generated.h”

UCLASS()
class MYPROJECT_API AMyCaptureManagerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCaptureManagerActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void OnConnectionStateChanged(const UE::CaptureManager::FConnectionStateChangedEvent& Event);

    TSharedPtr<UE::CaptureManager::FCPSDevice> CaptureDevice;
};
```
**MyCaptureManagerActor.cpp**
```cpp
#include “MyCaptureManagerActor.h”

using namespace UE::CaptureManager;

AMyCaptureManagerActor::AMyCaptureManagerActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCaptureManagerActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建设备实例
    CaptureDevice = FCPSDevice::MakeCPSDevice(TEXT(“127.0.0.1”), 22222);

    // 注册状态变化回调
    CaptureDevice->AddEventHandler<FConnectionStateChangedEvent>(
        FConnectionStateChangedEvent::FDelegate::CreateUObject(this, &AMyCaptureManagerActor::OnConnectionStateChanged)
    );

    // 发起连接
    UE_LOG(LogTemp, Log, TEXT(“正在尝试连接捕获设备…”));
    CaptureDevice->InitiateConnect();
}

void AMyCaptureManagerActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (CaptureDevice)
    {
        CaptureDevice->Stop();
        CaptureDevice.Reset();
    }

    Super::EndPlay(EndPlayReason);
}

void AMyCaptureManagerActor::OnConnectionStateChanged(const FConnectionStateChangedEvent& Event)
{
    switch (Event.ConnectionState)
    {
    case FConnectionStateChangedEvent::EState::Connecting:
        UE_LOG(LogTemp, Log, TEXT(“设备状态: 正在连接”));
        break;
    case FConnectionStateChangedEvent::EState::Connected:
        UE_LOG(LogTemp, Log, TEXT(“设备状态: 已连接”));
        // 连接成功后可以进行其他操作，如查询Take列表
        break;
    case FConnectionStateChangedEvent::EState::Disconnected:
        UE_LOG(LogTemp, Warning, TEXT(“设备状态: 已断开”));
        break;
    default:
        break;
    }
}
```
*将此类放入场景中运行，即可在输出日志中观察到设备连接状态的变化。*

## 模块依赖

使用 `CaptureManagerCPSClient` 或其他核心模块时，你的项目模块 `Build.cs` 文件需要添加以下依赖（根据你实际使用的子模块选择）：

| 模块 | 用途 |
|---|---|
| `CaptureManagerCPSClient` | 提供与CPS设备通信的客户端实现 |
| `CaptureProtocolStack` | 提供CPS协议的基础定义、序列化和解析 |
| `CaptureManagerTakeMetadata` | 定义Take的元数据结构体 |
| `CaptureUtils` | 提供捕获流程中的通用工具和辅助函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelle | 支持取消第三方编码器（音视频转换）任务 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 补充模块迁移时遗漏的一个修复 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复事务ID数据竞争导致的瞬时下载失败 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构JSON对象以支持两种字符串类型 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 添加设备蓝图模块 |

### 维护评价

- **创建时间**：该插件创建于 2025 年 2 月，相对**较新**。
- **更新频率**：最近一次更新在 2026 年 5 月，距今约一年。从提交记录看，更新内容包含功能增强（取消支持）、错误修复（数据竞争、遗漏修复）和重构，表明插件仍在被积极维护和完善。
- **活跃度**：属于**活跃维护**状态。作为Virtual Production（虚拟制片）关键流程的共享核心，其稳定性对上层应用（App和Editor插件）至关重要，因此有持续的维护需求。
- **已知问题**：源码中包含 `IsBetaVersion` 标记，说明该插件或其部分功能仍处于**测试阶段**，在生产环境中使用需谨慎，并关注后续的稳定性更新。
- **推荐使用**：如果你正在开发或集成基于UE的虚拟制片捕获解决方案，且需要与运行Capture Manager App的设备通信，那么这个插件是必须的基础依赖。由于仍为Beta版本，建议在实际项目中充分测试后再用于关键任务。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Tests)