# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式资产、Take 元数据定义） |
| 模块 | `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

Capture Manager Core 是 Epic 虚拟制片（Virtual Production）工作流中 **Capture Manager** 系统的底层核心库。它不直接面向最终用户，而是为 **Capture Manager App**（运行在外部设备上的采集客户端）和 **Capture Manager Editor**（UE 编辑器内的采集管理面板）提供共享的基础设施。

该插件解决的核心问题是：在多设备、多协议的影视动捕/虚拟制片场景中，如何统一处理以下环节——

- **设备发现与连接管理**：通过消息总线（MessageBus）在局域网内发现 LiveLink Hub 设备，建立连接并维持心跳保活
- **Take 元数据管理**：标准化描述一次采集（Take）的元数据结构（Slate、Take Number、场景信息等）
- **数据上传协议**：通过 TCP 将采集数据（视频、音频、传感器数据）从客户端上传到服务器，支持分块传输和完整性校验（MD5 Hash）
- **采集协议栈**：实现 Capture Manager 与外部采集设备之间的通信协议
- **数据摄取核心**：处理采集数据的导入、解析和存储
- **编辑器样式**：为 Capture Manager 编辑器 UI 提供统一的视觉风格

## 使用场景

- 你正在搭建 **虚拟制片采集管线**，需要从多个外部设备（如 iPhone、iPad、专业动捕相机）同步采集数据 → 使用 Capture Manager App + Capture Manager Editor，底层依赖此插件
- 你需要在局域网内 **自动发现并连接** LiveLink Hub 设备，进行 Take 数据的上传和管理 → 使用 LiveLinkHubCaptureMessaging 模块
- 你需要自定义 **Take 元数据结构** 或扩展采集协议 → 使用 CaptureManagerTakeMetadata 和 CaptureProtocolStack 模块
- 你需要在编辑器中构建 **Capture Manager 相关 UI** → 使用 CaptureManagerStyle 模块获取统一视觉风格

## 模块概览

| 模块 | 类型 | 职责 |
|---|---|---|
| **CaptureManagerStyle** | Runtime | 编辑器 UI 样式定义（图标、颜色、字体等） |
| **CaptureManagerTakeMetadata** | Runtime | Take 元数据结构定义（Slate、Take Number、场景描述等） |
| **CaptureProtocolStack** | Runtime | 采集设备通信协议实现 |
| **CaptureUtils** | Runtime | 通用工具函数库 |
| **DataIngestCore** | Runtime | 采集数据的导入、解析和存储核心逻辑 |
| **LiveLinkHubCaptureMessaging** | Runtime | 基于 MessageBus 的设备发现、连接管理和数据上传消息协议 |

---

# LiveLinkHubCaptureMessaging 模块

> 基于 Unreal MessageBus 的 LiveLink Hub 采集消息通信模块，提供设备发现、连接管理、心跳保活和数据上传功能。

## 用途

LiveLinkHubCaptureMessaging 实现了 Capture Manager 系统中 **客户端与服务器之间的消息通信层**。它基于 Unreal Engine 的 MessageBus 框架，提供了一套完整的连接生命周期管理：

1. **设备发现**（Discovery）：在局域网内广播发现请求，获取可用的 LiveLink Hub 服务器
2. **连接建立**（Connect）：客户端发起连接请求，服务器接受或拒绝
3. **心跳保活**（Keep-Alive）：通过 Ping/Pong 机制维持连接活性，超时自动断开
4. **上传状态通知**（Upload State）：在 Take 数据上传过程中，实时报告进度和完成状态
5. **数据上传协议**（Upload Data）：通过 TCP 传输 Take 数据文件，支持分块传输和 MD5 校验

## 蓝图用法

本模块为纯 C++ 运行时模块，不暴露蓝图接口。所有 API 均为 C++ 类和函数。

## C++ 用法

### 头文件引入

```cpp
#include "Messenger.h"
#include "LiveLinkHubCaptureMessages.h"
#include "UploadDataMessage.h"
#include "Features/ConnectStarter.h"
#include "Features/ConnectAcceptor.h"
#include "Features/UploadStateSender.h"
#include "Features/UploadStateHandler.h"
```

### 核心架构：FMessenger 模板类

本模块的核心设计模式是 **Feature 组合**。`FMessenger` 是一个可变参数模板类，通过多重继承将多个 Feature 组合到一个消息端点中：

```cpp
// 创建一个同时具备连接发起和上传状态发送功能的 Messenger
using FMyMessenger = FMessenger<FConnectStarter, FUploadStateSender>;

// 实例化（自动初始化所有 Feature 并构建 MessageEndpoint）
TSharedRef<FMyMessenger> Messenger = MakeShared<FMyMessenger>();

// 设置目标地址（服务器的 MessageBus 地址）
Messenger->SetAddress(ServerAddress);
```

每个 Feature 继承自 `FFeatureBase`，通过 `Initialize(FMessageEndpointBuilder&)` 注册自己关心的消息类型。

### 连接管理：客户端发起连接

```cpp
#include "Features/ConnectStarter.h"
#include "Messenger.h"

// 创建仅包含 ConnectStarter 的 Messenger
using FConnectMessenger = FMessenger<FConnectStarter>;
TSharedRef<FConnectMessenger> Messenger = MakeShared<FConnectMessenger>();

// 设置服务器地址
Messenger->SetAddress(ServerMessageAddress);

// 发起连接
Messenger->Connect([](const FConnectResponse& InResponse)
{
    if (InResponse.Status == EStatus::Ok)
    {
        UE_LOG(LogTemp, Log, TEXT("连接成功"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("连接失败: %s"), *InResponse.Message);
    }
});

// 设置断开回调
Messenger->SetDisconnectHandler([]()
{
    UE_LOG(LogTemp, Warning, TEXT("连接已断开"));
});

// 检查连接状态
if (Messenger->IsConnected())
{
    // 执行需要连接的操作
}

// 主动断开
Messenger->Disconnect();
```

### 连接管理：服务器接受连接

```cpp
#include "Features/ConnectAcceptor.h"
#include "Messenger.h"

// 创建包含 ConnectAcceptor 的 Messenger
using FAcceptorMessenger = FMessenger<FConnectAcceptor>;
TSharedRef<FAcceptorMessenger> Messenger = MakeShared<FAcceptorMessenger>();

// 设置连接处理回调
Messenger->SetConnectionHandler(
    // 连接请求回调：决定是否接受连接
    [](const FConnectRequest& InRequest, const FMessageAddress& InAddress) -> FConnectResponse*
    {
        FConnectResponse* Response = new FConnectResponse();
        Response->Status = EStatus::Ok;
        Response->Message = TEXT("Welcome");
        return Response;
    },
    // 连接丢失回调
    [](const FMessageAddress& InAddress)
    {
        UE_LOG(LogTemp, Warning, TEXT("客户端断开: %s"), *InAddress.ToString());
    }
);

// 检查是否有客户端连接
if (Messenger->IsConnected())
{
    // 处理已连接的客户端
}

// 主动断开
Messenger->Disconnect();
```

`ConnectAcceptor` 内置了 **超时检测机制**：如果客户端在 20 秒内没有发送 Ping 消息，服务器将自动判定连接丢失并触发 `ConnectionLostHandler`。

### 上传状态通知

```cpp
#include "Features/UploadStateSender.h"
#include "Features/UploadStateHandler.h"
#include "Messenger.h"

// === 发送端（上传客户端）===
using FUploadSenderMessenger = FMessenger<FUploadStateSender>;
TSharedRef<FUploadSenderMessenger> Sender = MakeShared<FUploadSenderMessenger>();
Sender->SetAddress(ServerAddress);

FGuid CaptureSourceId = FGuid::NewGuid();
FGuid TakeUploadId = FGuid::NewGuid();

// 报告上传进度（0.0 ~ 1.0）
Sender->SendUploadStateMessage(CaptureSourceId, TakeUploadId, 0.75);

// 报告上传完成
Sender->SendUploadDoneMessage(CaptureSourceId, TakeUploadId, TEXT("Success"), 0);

// === 接收端（服务器）===
using FUploadHandlerMessenger = FMessenger<FUploadStateHandler>;
TSharedRef<FUploadHandlerMessenger> Handler = MakeShared<FUploadHandlerMessenger>();

Handler->SetUploadCallbacks(
    // 进度回调
    [](const FGuid& InCaptureSourceId, const FGuid& InTakeUploadId, double InProgress)
    {
        UE_LOG(LogTemp, Log, TEXT("上传进度: %.1f%%"), InProgress * 100.0);
    },
    // 完成回调
    [](const FGuid& InCaptureSourceId, const FGuid& InTakeUploadId, FString InMessage, int32 InCode)
    {
        if (InCode == 0)
        {
            UE_LOG(LogTemp, Log, TEXT("上传完成: %s"), *InMessage);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("上传失败 [%d]: %s"), InCode, *InMessage);
        }
    }
);
```

### 数据上传协议（TCP）

`FUploadDataMessage` 提供了通过 TCP 传输 Take 数据的序列化/反序列化接口：

```cpp
#include "UploadDataMessage.h"
#include "Network/TcpReaderWriter.h"

// 构建上传头部
FUploadDataHeader Header;
Header.ClientId = FGuid::NewGuid();
Header.CaptureSourceId = CaptureSourceId;
Header.TakeUploadId = TakeUploadId;
Header.CaptureSourceName = TEXT("iPhone_01");
Header.Slate = TEXT("Shot_001");
Header.TakeNumber = 3;
Header.TotalLength = 1024 * 1024 * 50; // 50MB

// 序列化头部到 TCP 连接
FUploadVoidResult Result = FUploadDataMessage::SerializeHeader(Header, *TcpWriter);
if (Result.HasError())
{
    UE_LOG(LogTemp, Error, TEXT("序列化失败: %s"), *Result.GetError().GetText().ToString());
}

// 序列化文件头部
FUploadFileDataHeader FileHeader;
FileHeader.FileName = TEXT("video.mp4");
FileHeader.Length = 1024 * 1024 * 50;
FUploadDataMessage::SerializeFileHeader(FileHeader, *TcpWriter);

// 分块发送数据
TArray<uint8> ChunkData;
// ... 填充数据块 ...
FUploadDataMessage::SerializeData(MoveTemp(ChunkData), *TcpWriter);

// 发送 MD5 校验和
TStaticArray<uint8, 16> Hash;
// ... 计算 MD5 ...
FUploadDataMessage::SerializeHash(Hash, *TcpWriter);
```

### 消息结构

本模块定义了以下消息类型（均继承自 `FBaseMessage`）：

| 消息类型 | 用途 |
|---|---|
| `FConnectRequest` | 客户端发起连接请求 |
| `FConnectResponse` | 服务器连接响应（含状态码和消息） |
| `FCaptureManagerHangUp` | 断开连接通知 |
| `FDiscoveryRequest` | 局域网设备发现请求（含主机名） |
| `FDiscoveryResponse` | 设备发现响应（含主机名、IP、导出端口） |
| `FPingMessage` | 心跳 Ping |
| `FPongMessage` | 心跳 Pong |
| `FUploadState` | 上传进度通知 |
| `FUploadFinished` | 上传完成通知 |

所有消息都包含版本号（当前为 `Version = 1`）和 GUID，用于消息路由和去重。

## Demo 示例

### 完整的客户端-服务器连接示例

**MyCaptureServer.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Messenger.h"
#include "Features/ConnectAcceptor.h"
#include "Features/UploadStateHandler.h"

class FMyCaptureServer
{
public:
    using FServerMessenger = FMessenger<FConnectAcceptor, FUploadStateHandler>;

    FMyCaptureServer();
    ~FMyCaptureServer();

    bool IsClientConnected() const;

private:
    TSharedRef<FServerMessenger> Messenger;
};
```

**MyCaptureServer.cpp**

```cpp
#include "MyCaptureServer.h"

FMyCaptureServer::FMyCaptureServer()
    : Messenger(MakeShared<FServerMessenger>())
{
    // 设置连接处理
    Messenger->SetConnectionHandler(
        [](const FConnectRequest& InRequest, const FMessageAddress& InAddress) -> FConnectResponse*
        {
            FConnectResponse* Response = new FConnectResponse();
            Response->Status = EStatus::Ok;
            return Response;
        },
        [](const FMessageAddress& InAddress)
        {
            UE_LOG(LogTemp, Warning, TEXT("Client disconnected"));
        }
    );

    // 设置上传回调
    Messenger->SetUploadCallbacks(
        [](const FGuid& SourceId, const FGuid& UploadId, double Progress)
        {
            UE_LOG(LogTemp, Log, TEXT("Upload progress: %.1f%%"), Progress * 100.0);
        },
        [](const FGuid& SourceId, const FGuid& UploadId, FString Msg, int32 Code)
        {
            UE_LOG(LogTemp, Log, TEXT("Upload finished: %s (code: %d)"), *Msg, Code);
        }
    );
}

FMyCaptureServer::~FMyCaptureServer()
{
    Messenger->Disconnect();
}

bool FMyCaptureServer::IsClientConnected() const
{
    return Messenger->IsConnected();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CaptureUtils` | 通用工具函数（TCP 读写接口 `ITcpSocketReader`/`ITcpSocketWriter`、定时器管理 `FCaptureTimerManager`） |
| `Messaging` | Unreal MessageBus 消息通信框架 |

## 维护状态

### 近期更新

```
- fdaf85b60939 [Capture Manager] Fixed several crashes while aborting take upload.
- 7e2449cb2cbb Unshelved from pending changelist '46101232':
- 3cb1199596ff Fixing Python issues:
```

最近的提交修复了中止 Take 上传时的多个崩溃问题，表明该模块仍在积极开发和修复中。

### 维护评价

- **创建时间**：2025 年 2 月，非常新的模块
- **维护状态**：活跃开发中，最近有实质性 bug 修复
- **实验性标记**：`EnabledByDefault = false`，标记为实验性功能
- **已知限制**：
  - 作为实验性功能，API 可能在后续版本中发生变化
  - `FFeatureBase` 中的 `Endpoint` 和 `Address` 成员已在 5.7 中标记为 deprecated，建议使用 `SendMessage()` 和 `Set/GetAddress()` 替代
  - 心跳超时默认 20 秒，上传不活动超时 15 秒，均为硬编码值
- **推荐程度**：如果你正在使用 Capture Manager 虚拟制片管线，此模块是必需的基础设施。但作为独立使用者，需要理解它是一个内部共享库，API 不保证向后兼容。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [CaptureManagerCore 汇总页](./index.md)