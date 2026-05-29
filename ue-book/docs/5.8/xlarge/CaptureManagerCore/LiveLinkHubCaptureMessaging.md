# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 采集管理器核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（共享模块库） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerCPSClient` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureMetadataExtraction` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

CaptureManagerCore 是一个**共享基础库插件**，为 Epic 的“采集管理器”生态系统提供核心运行时功能。它的核心作用是：

1.  **定义通信协议**：特别是 `LiveLinkHubCaptureMessaging` 模块，它为 Unreal Engine 的 LiveLink Hub 与外部采集设备（如 iPhone、专业摄像机等）之间的实时通信建立了标准化框架，包括设备发现、连接管理、状态同步和数据上传。
2.  **封装核心数据处理**：`CaptureDataConverter`, `CaptureProtocolStack`, `DataIngestCore` 等模块处理从设备接收的原始数据（如元数据、媒体文件），并将其转换为引擎可用的格式。
3.  **提供通用工具**：`CaptureUtils` 等模块提供文件、网络、JSON 处理等通用功能，避免在上层插件中重复造轮子。

该插件本身不提供独立的编辑器界面或最终用户功能，而是作为 `CaptureManagerEditor` 和 `CaptureManagerApp` 的共同依赖，确保它们之间行为一致且代码复用。

## 使用场景

-   你在开发一个使用 **LiveLink Hub** 管理 iPhone 面部捕捉数据流的**虚拟制片**项目，需要设备与 PC 之间建立可靠的连接并监控上传进度。
-   你需要为**自定义采集硬件**编写一个与 LiveLink Hub 兼容的驱动程序或接口。
-   你在构建一个需要处理**多源采集数据**（如视频、音频、元数据）并将其同步到引擎时间线上的工具。

## 蓝图用法

`LiveLinkHubCaptureMessaging` 模块主要提供 C++ API 用于构建通信逻辑，其核心 `FMessenger` 模板类和 `Features` 系统为蓝图暴露有限。该模块侧重于底层通信，高级操作和 UI 通常由上层插件（如 `CaptureManagerEditor`）处理。

### 核心概念

该模块的核心是基于 **Unreal Message Bus (UBT)** 的通信框架。关键概念包括：
-   **Messenger**：通信端点的管理者，组合了多个“特性”（Feature）。
-   **Features**：可插拔的功能模块，如 `FConnectStarter` (发起连接)、`FConnectAcceptor` (接受连接)、`FUploadStateHandler` (处理上传状态)。

蓝图中可能通过上层插件间接使用此模块的数据结构（如 `FDiscoveryResponse`, `FUploadState`），但直接创建和操作 `FMessenger` 通常是 C++ 任务。

## C++ 用法

### 头文件引入

```cpp
#include "Messenger.h"
#include "LiveLinkHubCaptureMessages.h"
#include "Features/ConnectStarter.h"
#include "Features/UploadStateHandler.h"
```

### 基本用法：建立一个具有连接和状态处理功能的 Messenger

以下示例创建了一个 `FMessenger`，它同时具备发起连接（`FConnectStarter`）和处理上传状态（`FUploadStateHandler`）的能力。这模拟了一个客户端设备的角色。

```cpp
// 来源：基于 LiveLinkHubCaptureMessaging/Public/Messenger.h 和 Features 头文件推断的用法。
// 定义一个同时包含连接发起者和上传状态处理器的 Messenger 类型
using FDeviceMessenger = UE::LiveLinkHubCaptureMessaging::FMessenger<
    UE::LiveLinkHubCaptureMessaging::FConnectStarter,
    UE::LiveLinkHubCaptureMessaging::FUploadStateHandler
>;

// 在类中持有 Messenger 实例
TUniquePtr<FDeviceMessenger> MyDeviceMessenger;

// 初始化 Messenger
void AMyCaptureDevice::InitializeMessenger()
{
    MyDeviceMessenger = MakeUnique<FDeviceMessenger>();

    // 设置连接目标地址 (从设备发现或配置获得)
    FMessageAddress TargetAddress; // ... 从某个地方获取
    MyDeviceMessenger->SetAddress(TargetAddress);

    // 设置连接回调
    MyDeviceMessenger->Connect(
        FDeviceMessenger::FConnectStarter::FConnectHandler::CreateUObject(this, &AMyCaptureDevice::OnConnectResponse)
    );

    // 设置上传状态回调
    MyDeviceMessenger->SetUploadCallbacks(
        FDeviceMessenger::FUploadStateHandler::FUploadStateCallback::CreateUObject(this, &AMyCaptureDevice::OnUploadProgress),
        FDeviceMessenger::FUploadStateHandler::FUploadFinishedCallback::CreateUObject(this, &AMyCaptureDevice::OnUploadFinished)
    );
}

// 回调实现
void AMyCaptureDevice::OnConnectResponse(const FConnectResponse& Response)
{
    if (Response.Status == EStatus::Ok)
    {
        UE_LOG(LogTemp, Log, TEXT("成功连接到 LiveLink Hub"));
    }
}

void AMyCaptureDevice::OnUploadProgress(const FGuid& CaptureSourceId, const FGuid& TakeUploadId, double Progress)
{
    // 更新 UI 上的进度条
    UpdateProgressBar(CaptureSourceId, TakeUploadId, Progress);
}

void AMyCaptureDevice::OnUploadFinished(const FGuid& CaptureSourceId, const FGuid& TakeUploadId, FString Message, int32 Code)
{
    if (Code == 0) // 0 通常代表成功
    {
        UE_LOG(LogTemp, Log, TEXT("Take %s 上传完成"), *TakeUploadId.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Take %s 上传失败: %s"), *TakeUploadId.ToString(), *Message);
    }
}
```

### 进阶用法：直接使用 UploadDataMessage 进行数据序列化

在某些需要直接控制网络数据包结构的场景下，可以直接使用 `FUploadDataMessage` 进行序列化/反序列化。

```cpp
#include "UploadDataMessage.h"
#include "Network/NetworkTcpSocket.h" // 假设的 TCP 套接字包装器

// 假设我们有一个向 Writer 写入数据的场景
void SerializeAndSendCaptureData(const FUploadDataHeader& Header, const TArray<uint8>& FileData, UE::CaptureManager::ITcpSocketWriter& Writer)
{
    // 序列化头信息
    FUploadVoidResult HeaderResult = FUploadDataMessage::SerializeHeader(Header, Writer);
    if (HeaderResult.HasError())
    {
        UE_LOG(LogTemp, Error, TEXT("序列化头信息失败: %s"), *HeaderResult.GetError().GetText().ToString());
        return;
    }

    // 序列化文件数据
    FUploadVoidResult DataResult = FUploadDataMessage::SerializeData(FileData, Writer);
    if (DataResult.HasError())
    {
        UE_LOG(LogTemp, Error, TEXT("序列化数据失败: %s"), *DataResult.GetError().GetText().ToString());
        return;
    }

    // (可选) 序列化校验哈希
    TStaticArray<uint8, FUploadDataMessage::HashSize> Hash = CalculateMD5(FileData);
    FUploadVoidResult HashResult = FUploadDataMessage::SerializeHash(Hash, Writer);
    if (HashResult.HasError())
    {
        UE_LOG(LogTemp, Warning, TEXT("序列化哈希失败: %s"), *HashResult.GetError().GetText().ToString());
    }
}
```

## Demo 示例

一个最小化的示例，演示如何接收设备发现请求并响应。

```cpp
// MyDiscoveryReceiver.h
#pragma once
#include "CoreMinimal.h"
#include "Features/ConnectAcceptor.h"
#include "LiveLinkHubCaptureMessages.h"

class FMyDiscoveryReceiver : public UE::LiveLinkHubCaptureMessaging::FConnectAcceptor
{
public:
    FMyDiscoveryReceiver();

private:
    // 覆盖 FConnectAcceptor 的连接处理，返回一个成功的响应
    UE::LiveLinkHubCaptureMessaging::FConnectResponse* OnConnectRequest(
        const FConnectRequest& Request,
        const FMessageAddress& ClientAddress);

    // 处理设备发现请求（通常由上层或另一个特性处理，此处为演示集成）
    void OnDiscoveryRequest(const FDiscoveryRequest& Request,
                            const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context);

    void SendDiscoveryResponse(const FDiscoveryResponse& Response, const FMessageAddress& ToAddress);
};
```

```cpp
// MyDiscoveryReceiver.cpp
#include "MyDiscoveryReceiver.h"
#include "Messenger.h"

FMyDiscoveryReceiver::FMyDiscoveryReceiver()
{
    // 设置连接处理器
    SetConnectionHandler(
        FConnectAccepted::CreateRaw(this, &FMyDiscoveryReceiver::OnConnectRequest),
        FConnectionLostHandler() // 可留空
    );
}

FConnectResponse* FMyDiscoveryReceiver::OnConnectRequest(const FConnectRequest& Request, const FMessageAddress& ClientAddress)
{
    // 可以在此验证请求，例如检查 Guid 有效性
    FConnectResponse* Response = new FConnectResponse();
    Response->Status = EStatus::Ok;
    Response->Message = TEXT("Connection accepted.");
    Response->RequestGuid = Request.Guid;
    return Response;
}

void FMyDiscoveryReceiver::OnDiscoveryRequest(const FDiscoveryRequest& Request, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context)
{
    // 构造响应
    FDiscoveryResponse Response;
    Response.HostName = FPlatformProcess::ComputerName();
    Response.IPAddress = TEXT("192.168.1.100"); // 应该从配置或运行时获取
    Response.ExportPort = 12345; // 同上

    // 通过 Messenger 发送响应给请求方
    SendDiscoveryResponse(&Response, Context->GetSender());
}

// 注意：要在主程序中创建并使用此类，需要将其组装到一个 FMessenger 中。
// 例如：using FMyServer = UE::LiveLinkHubCaptureMessaging::FMessenger<FMyDiscoveryReceiver>;
// FMyServer Server;
// Server.SetAddress(ListenAddress);
```

## 模块依赖

从 `LiveLinkHubCaptureMessaging` 模块的 `Build.cs` 分析，它依赖以下非通用模块：

| 模块 | 用途 |
|---|---|
| `CaptureProtocolStack` | 提供底层协议和数据结构定义 |
| `CaptureUtils` | 提供通用的工具函数，如定时器管理、JSON 处理 |
| `Json` | 用于消息内容的序列化与反序列化 |
| `Serialization` | 用于二进制数据的序列化/反序列化（如`TValueOrError`） |

使用本模块（`LiveLinkHubCaptureMessaging`）时，你的模块需要在 `Build.cs` 中添加对 `LiveLinkHubCaptureMessaging` 的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelled | 为第三方编码器命令传递停止令牌，使音视频转换支持取消 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 补充了在模块迁移过程中丢失的修复 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复了导致间歇性下载失败的事务 ID 数据竞争问题 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 CaptureManagerDeviceBlueprint 模块 |

### 维护评价

-   **创建时间**：插件创建于 2025 年 2 月，是一个相对较新的项目。
-   **维护频率**：从 git 历史看，近期（2026 年 4 月、5 月）有**活跃的维护和开发**。提交内容包括新功能添加（如新模块）、重要的 Bug 修复（数据竞争、序列化问题）和重构。
-   **状态**：**活跃维护中**。属于 Epic Games Virtual Production 套件的一部分，有持续的投入。
-   **已知问题**：从更新日志看，历史上存在数据竞争和序列化相关问题，但均已被修复。
-   **推荐使用**：如果你正在开发与 Unreal Engine LiveLink 生态集成的采集工具，此插件提供了官方、标准化的基础通信层，**推荐作为依赖**。但需注意它**默认未启用**，需要在你的 `.uplugin` 文件或项目设置中明确启用 `CaptureManagerCore` 及其子模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [官方文档]() （未提供）
- [测试用例]() （未在当前信息中提供具体路径）