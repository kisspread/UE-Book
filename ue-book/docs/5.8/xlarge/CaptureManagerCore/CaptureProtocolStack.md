# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（共享工具库） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerCPSClient` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureMetadataExtraction` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

此插件并非一个面向终端用户的独立功能插件，而是为 **Capture Manager** 生态系统提供底层核心框架和共享服务的**基础库**。它实现了虚拟制片（Virtual Production）工作流中，用于管理、控制和导入来自各种设备（如iPhone、专业摄像机）捕获数据（如视频、动画、音频）的核心通信协议、数据处理管线和元数据模型。

其主要目的是：
1.  **统一设备通信协议**：实现了 **Capture Protocol Stack (CPS)** 的客户端逻辑，用于与运行CPS服务端的捕获设备（如通过Live Link Hub应用运行在iOS设备上的App）进行控制、状态同步和数据导出。
2.  **标准化数据导入流程**：提供 `DataIngestCore` 和 `CaptureDataConverter` 等模块，定义了从设备接收原始数据、解析元数据、并将其转换为Unreal Engine可识别的资产（如动画、媒体文件）的标准化流程。
3.  **提供共享基础设施**：包含设备发现、任务队列、文件导出、样式定义等工具，供上层的 `CaptureManagerApp` 和 `CaptureManagerEditor` 插件复用，避免重复开发。

## 使用场景

-   **你在虚拟制片现场**，需要使用iPhone或专业设备录制表演捕捉（Performance Capture）数据。你的设备运行着支持CPS协议的App（如Live Link Hub）。你需要通过Unreal Engine实时连接、监控设备状态、控制录制开始/停止、并最终将录制好的Take（一条完整的录制数据）下载到编辑器中。 → **使用此插件提供的CPS客户端和发现服务**。
-   **你正在开发一个自定义的捕获设备管理工具**，需要将捕获设备的数据导入UE。你的设备遵循CPS协议。 → **可以依赖此插件的`CaptureProtocolStack`模块**作为通信基础。
-   **你在制作一个自动化的素材导入流水线**，需要根据拍摄时记录的元数据（Slate, Take Number, Tags）自动组织和处理导入的媒体文件。 → **使用`CaptureManagerTakeMetadata`和`DataIngestCore`模块**。

## 蓝图用法

**重要**：此插件（`CaptureManagerCore`）本身是一个**纯C++运行时库**，其主要模块（如`CaptureProtocolStack`）并未设计为直接在蓝图中使用。它主要为上层的编辑器插件（`CaptureManagerEditor`）和应用程序插件（`CaptureManagerApp`）提供API。

在蓝图中交互的功能，通常由上述上层插件封装并暴露。例如，设备发现、录制控制、数据导入等用户界面操作，其底层逻辑都依赖于本核心库。

## C++ 用法

此插件的核心在于`CaptureProtocolStack`模块，它提供了与CPS设备通信的完整客户端API。

### 头文件引入

```cpp
// 引入CPS核心消息和客户端
#include "Control/ControlMessenger.h"
#include "Control/Messages/ControlRequest.h"
#include "Control/Messages/ControlResponse.h"

// 引入设备发现
#include "Discovery/DiscoveryMessenger.h"

// 引入数据导出
#include "ExportClient/ExportClient.h"
```

### 基本用法

以下示例展示了如何使用`FControlMessenger`连接到CPS设备并发送一个获取服务器信息的请求。

```cpp
// 假设已经知道设备的IP和端口 (例如通过FDiscoveryMessenger发现)
FString DeviceIP = TEXT("192.168.1.100");
uint16 ControlPort = 32768;

// 创建并初始化控制信使
FControlMessenger Messenger;
Messenger.Start(DeviceIP, ControlPort);

// 发送“获取服务器信息”请求并同步等待响应
TProtocolResult<FGetServerInformationResponse> Result = Messenger.GetServerInformation();
if (Result.HasValue())
{
    FGetServerInformationResponse Response = Result.GetValue();
    UE_LOG(LogTemp, Log, TEXT("Connected to: %s, Model: %s"), *Response.GetName(), *Response.GetModel());
}
else
{
    FCaptureProtocolError Error = Result.GetError();
    UE_LOG(LogTemp, Error, TEXT("Failed to get server info: %s"), *Error.GetMessage());
}

// 完成后停止连接
Messenger.Stop();
```
*来源参考: `Public/Control/ControlMessenger.h` 中 `SendRequest` 模板函数的实现逻辑。*

### 进阶用法：异步请求与更新处理

更常见的用法是使用异步请求，并注册处理器以接收设备主动发送的更新（如录制状态变化）。

```cpp
// 创建控制信使
FControlMessenger Messenger;

// 注册更新处理器：当设备录制状态改变时收到通知
Messenger.RegisterUpdateHandler(CPS::AddressPaths::GRecordingStatus,
    FControlUpdate::FOnUpdateMessage::CreateLambda([](TSharedPtr<FControlUpdate> InUpdate)
    {
        if (auto* StatusUpdate = static_cast<FRecordingStatusUpdate*>(InUpdate.Get()))
        {
            UE_LOG(LogTemp, Log, TEXT("Device recording status changed to: %s"),
                StatusUpdate->IsRecording() ? TEXT("Recording") : TEXT("Stopped"));
        }
    })
);

// 注册断开连接处理器
Messenger.RegisterDisconnectHandler(FControlMessenger::FOnDisconnect::CreateLambda([](const FString& InCause)
{
    UE_LOG(LogTemp, Warning, TEXT("Connection lost: %s"), *InCause);
}));

// 启动连接
Messenger.Start(DeviceIP, ControlPort);
Messenger.StartSession(); // 建立会话

// 异步发送请求：开始录制一个Take
FStartRecordingTakeRequest StartRequest(
    TEXT("MySlate"),
    1,
    TOptional<FString>(),
    TOptional<FString>(),
    TOptional<TArray<FString>>()
);

Messenger.SendAsyncRequest(StartRequest,
    FControlMessenger::FOnControlResponse<FStartRecordingTakeRequest>::CreateLambda(
        [](TProtocolResult<FStartRecordingTakeResponse> InResult)
        {
            if (InResult.HasValue())
            {
                UE_LOG(LogTemp, Log, TEXT("Recording started successfully."));
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Failed to start recording: %s"),
                    *InResult.GetError().GetMessage());
            }
        })
    );

// ... 应用程序主循环 ...

// 退出前清理
Messenger.Stop();
```
*来源参考: `Public/Control/ControlMessenger.h` 中的 `RegisterUpdateHandler` 和 `SendAsyncRequest` 方法。*

## Demo 示例

一个完整的、可编译的最小示例，演示设备发现、连接和获取Take列表。

**MyCaptureDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Discovery/DiscoveryMessenger.h"
#include "Control/ControlMessenger.h"
#include "MyCaptureDemo.generated.h"

UCLASS()
class AMyCaptureDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyCaptureDemo();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void OnDeviceDiscovered(FString InServerIp, FDiscoveryResponse InResponse);
    void OnDeviceNotify(FString InServerIp, FDiscoveryNotify InNotify);
    void OnTakeListReceived(TProtocolResult<FGetTakeListResponse> InResult);

    FDiscoveryMessenger DiscoveryMessenger;
    TUniquePtr<FControlMessenger> ControlMessenger;

    FString DiscoveredDeviceIp;
    uint16 DiscoveredControlPort;
};
```

**MyCaptureDemo.cpp**
```cpp
#include "MyCaptureDemo.h"
#include "Control/Messages/ControlRequest.h"

AMyCaptureDemo::AMyCaptureDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCaptureDemo::BeginPlay()
{
    Super::BeginPlay();

    // 1. 设置并启动设备发现
    DiscoveryMessenger.SetResponseHandler(FDiscoveryMessenger::FOnResponseArrived::CreateUObject(this, &AMyCaptureDemo::OnDeviceDiscovered));
    DiscoveryMessenger.SetNotifyHandler(FDiscoveryMessenger::FOnNotifyArrived::CreateUObject(this, &AMyCaptureDemo::OnDeviceNotify));
    DiscoveryMessenger.Start();
    DiscoveryMessenger.SendRequest(); // 发送发现广播

    UE_LOG(LogTemp, Log, TEXT("Discovery request sent. Waiting for devices..."));
}

void AMyCaptureDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ControlMessenger.IsValid())
    {
        ControlMessenger->Stop();
        ControlMessenger.Reset();
    }
    DiscoveryMessenger.Stop();
    Super::EndPlay(EndPlayReason);
}

void AMyCaptureDemo::OnDeviceDiscovered(FString InServerIp, FDiscoveryResponse InResponse)
{
    UE_LOG(LogTemp, Log, TEXT("Discovered Device: %s (IP: %s, ControlPort: %d)"),
        *InResponse.GetServerName(), *InServerIp, InResponse.GetControlPort());

    // 选择第一个发现的设备进行连接（示例）
    if (!ControlMessenger.IsValid())
    {
        DiscoveredDeviceIp = InServerIp;
        DiscoveredControlPort = InResponse.GetControlPort();

        // 2. 创建并连接控制信使
        ControlMessenger = MakeUnique<FControlMessenger>();
        if (ControlMessenger->Start(DiscoveredDeviceIp, DiscoveredControlPort).HasError())
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to connect to device control port."));
            return;
        }

        // 3. 发送同步请求获取Take列表
        FGetTakeListRequest TakeListRequest;
        ControlMessenger->SendAsyncRequest(TakeListRequest,
            FControlMessenger::FOnControlResponse<FGetTakeListRequest>::CreateUObject(this, &AMyCaptureDemo::OnTakeListReceived));
    }
}

void AMyCaptureDemo::OnDeviceNotify(FString InServerIp, FDiscoveryNotify InNotify)
{
    // 可以处理设备状态变化通知，例如上下线
    UE_LOG(LogTemp, Log, TEXT("Device %s status: %s"),
        *InServerIp,
        InNotify.GetConnectionState() == FDiscoveryNotify::EConnectionState::Online ? TEXT("Online") : TEXT("Offline"));
}

void AMyCaptureDemo::OnTakeListReceived(TProtocolResult<FGetTakeListResponse> InResult)
{
    if (InResult.HasValue())
    {
        FGetTakeListResponse Response = InResult.GetValue();
        UE_LOG(LogTemp, Log, TEXT("--- Take List on Device ---"));
        for (const FString& TakeName : Response.GetNames())
        {
            UE_LOG(LogTemp, Log, TEXT("  * %s"), *TakeName);
        }
        UE_LOG(LogTemp, Log, TEXT("---------------------------"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get take list: %s"), *InResult.GetError().GetMessage());
    }
}
```

## 模块依赖

此插件本身是一个纯内容/工具库插件，其模块依赖已在各子模块的`Build.cs`中定义。作为使用者，如果你需要在自己的模块中引用`CaptureManagerCore`中的特定模块（例如`CaptureProtocolStack`），你需要在你的模块的`Build.cs`中添加对这些模块的依赖。

| 模块 | 用途 |
|---|---|
| `CaptureProtocolStack` | CPS协议客户端实现，用于设备通信 |
| `DataIngestCore` | 定义捕获数据导入的核心接口和流程 |
| `CaptureManagerTakeMetadata` | 解析和管理Take的元数据（Slate, Take Number等） |
| `CaptureUtils` | 通用工具函数 |

*注意：依赖通常还包括网络通信、JSON解析等基础库，具体请参考目标模块的`Build.cs`文件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelled | 将停止令牌转发给第三方编码器命令，使音视频转换可被取消 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 补回在模块迁移过程中丢失的修复(51621159) |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复事务ID数据竞争导致的瞬时下载失败问题 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构FJsonObject以支持FString和UE::FSharedString |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 添加CaptureManagerDeviceBlueprint模块 |

### 维护评价

-   **创建时间**：插件创建于2025年初，是一个相对较新的组件。
-   **更新频率**：从Git历史看，近半年内有多次实质性更新，包括**功能改进**（如传递停止令牌）、**重要Bug修复**（数据竞争、丢失的修复）和**重构**。更新频率较高，说明处于**积极开发和维护**阶段。
-   **已知问题**：近期的提交记录表明存在一些并发和数据处理方面的边界情况问题（如数据竞争），但都已得到修复。
-   **推荐使用**：**推荐在虚拟制片工作流中使用**。虽然插件默认未启用（`EnabledByDefault: false`），且标记为实验性（`IsBetaVersion: true`），但其功能完整，更新活跃，是构建基于CPS的捕获管理流程的基石。对于需要集成自定义捕获设备的开发者，这是一个重要的参考和依赖库。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureProtocolStack/Tests)