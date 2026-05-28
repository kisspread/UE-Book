# WebSocket Networking

> WebSocket Networking - NOTE: MUST disable all other existing NetDriverDefinitions in order to use WebSocketNetDriver. ALSO: MUST disable all PackHandlerComponents not supported by HTML5/Websockets (e.g. SteamAuthComponentModuleInterface)

| 属性 | 值 |
|---|---|
| 中文名 | WebSocket 网络 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebSocketNetworking` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-15 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WebSocketNetworking) | |

## 用途

这是一个为 UE5 提供基于 WebSocket 协议的网络驱动（NetDriver）的实验性插件。它专门设计用于 **HTML5 平台** 或其他需要通过 WebSocket 进行网络通信的环境（如浏览器），因为在这些环境中，传统的 TCP/UDP 套接字无法直接使用。

该插件解决了在浏览器中运行 UE 游戏或应用时，如何进行实时网络通信的问题。它通过实现 `UWebSocketNetDriver` 来替换默认的网络驱动，使得 UE 的网络复制、RPC 调用等功能能够基于 WebSocket 协议工作。此外，它还内置了一个 HTTP/HTTPS 服务器功能，可以在 WebSocket 监听端口上同时提供静态文件服务，这非常方便为 Web 客户端提供资产文件。

## 使用场景

*   **部署 HTML5 版本的多人游戏或应用**：当你需要将 UE 项目编译为 HTML5 并部署到 Web 服务器上时，此插件是实现客户端与服务器（或另一个客户端）之间网络通信的必需品。
*   **在浏览器中进行网络测试**：开发过程中，可以直接在浏览器里测试游戏的网络功能，无需原生客户端。
*   **需要为 Web 客户端提供静态资源**：利用其内置的 HTTP 服务器功能，可以在同一个端口上同时提供 WebSocket 服务和静态文件（如 HTML、JS、图片）服务。

## 蓝图用法

此插件主要在底层网络层工作，公开的蓝图节点较少。主要通过 C++ 进行配置和使用。核心的蓝图交互点在于获取连接和处理连接事件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetServerConnection` | 获取到服务器的 WebSocket 连接对象 | `UWebSocketNetDriver` |
| `OnWebSocketClientConnected` | 服务器端：当有新客户端通过 WebSocket 连接成功时的回调 | `UWebSocketNetDriver` |
| `OnWebSocketServerConnected` | 客户端端：当此客户端成功连接到服务器时的回调 | `UWebSocketNetDriver` |
| `Tick` | 驱动连接的数据处理 | `UWebSocketConnection` |
| `ReceivedRawPacket` | 接收到原始网络包数据 | `UWebSocketConnection` |

### 使用示例（蓝图描述）

由于该插件面向底层，典型用法不在蓝图层面直接调用节点，而是通过配置使用。要使用 WebSocket 网络，你需要：
1.  在项目的 `DefaultEngine.ini` 配置文件中，禁用其他 `NetDriverDefinitions`，并添加一个使用 `WebSocketNetDriver` 的定义。
2.  在游戏逻辑中，你可能通过 `GetServerConnection` 获取连接状态，或者监听连接/断开事件。数据收发主要由引擎网络层自动处理。

## C++ 用法

该插件的核心是提供一组接口来创建和管理 WebSocket 服务器与客户端连接。

### 头文件引入

```cpp
#include "IWebSocketNetworkingModule.h"
#include "IWebSocketServer.h"
#include "INetworkingWebSocket.h"
#include "WebSocketNetworkingDelegates.h"
```

### 基本用法

以下代码展示了如何通过模块接口创建 WebSocket 服务器并初始化。
（来源：`IWebSocketNetworkingModule.h`, `IWebSocketServer.h`）

```cpp
// 获取 WebSocketNetworking 模块
IWebSocketNetworkingModule& WebSocketModule = FModuleManager::LoadModuleChecked<IWebSocketNetworkingModule>(TEXT("WebSocketNetworking"));

// 创建 WebSocket 服务器实例
TUniquePtr<IWebSocketServer> Server = WebSocketModule.CreateServer();
if (Server.IsValid())
{
    // 设置客户端连接回调
    FWebSocketClientConnectedCallBack ConnectedCallback;
    ConnectedCallback.BindLambda([](INetworkingWebSocket* ClientSocket)
    {
        // 新客户端连接，可以在这里设置接收回调等
        UE_LOG(LogTemp, Log, TEXT("New WebSocket Client Connected"));
    });

    // 初始化服务器，监听8080端口
    bool bSuccess = Server->Init(8080, ConnectedCallback, TEXT("0.0.0.0"));
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("WebSocket Server started on port 8080"));
    }

    // 在游戏循环中调用 Tick 以处理网络事件
    // Server->Tick();
}
```

### 进阶用法

启用 HTTP 服务器功能，并配置 SSL 证书以支持 HTTPS。
（来源：`IWebSocketServer.h`）

```cpp
// 假设已经创建了 Server (TUniquePtr<IWebSocketServer>)

// 配置要提供的静态文件目录
TArray<FWebSocketHttpMount> HttpMounts;
FWebSocketHttpMount Mount;
Mount.SetPathOnDisk(TEXT("/path/to/your/web/content"));
Mount.SetWebPath(TEXT("/"));
Mount.SetDefaultFile(TEXT("index.html"));
HttpMounts.Add(Mount);

// 配置 SSL 证书（用于 HTTPS）
FWebSocketServerCertificates Certificates;
Certificates.SetCertificateFilePath(TEXT("/path/to/server.crt"));
Certificates.SetPrivateKeyFilePath(TEXT("/path/to/server.key"));

// 启用 HTTPS 服务器
Server->EnableHTTPServer(HttpMounts, true, Certificates); // true 表示启用安全连接 (HTTPS)

// 设置网络协议（可选，默认为 IPv4）
Server->SetNetworkProtocol(IWebSocketServer::ENetworkProtocol::IPv4 | IWebSocketServer::ENetworkProtocol::IPv6);

// 然后调用 Init，HTTP/HTTPS 服务将与 WebSocket 使用同一端口
// Server->Init(8080, ...);
```

## Demo 示例

一个完整的、可编译的最小 WebSocket 服务器示例。

```cpp
// WebSocketDemo.h
#pragma once

#include "CoreMinimal.h"
#include "IWebSocketNetworkingModule.h"
#include "IWebSocketServer.h"
#include "INetworkingWebSocket.h"

class FWebSocketDemoServer
{
public:
    void StartServer(uint32 Port);
    void Tick();

private:
    TUniquePtr<IWebSocketServer> Server;
    TArray<INetworkingWebSocket*> ConnectedClients;

    void OnClientConnected(INetworkingWebSocket* NewClient);
    void OnClientDataReceived(void* Data, int32 DataSize, INetworkingWebSocket* Client);
    void OnClientDisconnected(INetworkingWebSocket* Client);
};

// WebSocketDemo.cpp
#include "WebSocketDemo.h"
#include "WebSocketNetworkingDelegates.h"

void FWebSocketDemoServer::StartServer(uint32 Port)
{
    IWebSocketNetworkingModule& WebSocketModule = FModuleManager::LoadModuleChecked<IWebSocketNetworkingModule>(TEXT("WebSocketNetworking"));
    Server = WebSocketModule.CreateServer();

    if (!Server.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create WebSocket Server"));
        return;
    }

    // 设置连接回调
    FWebSocketClientConnectedCallBack ConnectedCallback;
    ConnectedCallback.BindRaw(this, &FWebSocketDemoServer::OnClientConnected);

    if (Server->Init(Port, ConnectedCallback))
    {
        UE_LOG(LogTemp, Log, TEXT("Demo WebSocket Server started on port %d"), Port);
    }
}

void FWebSocketDemoServer::Tick()
{
    if (Server.IsValid())
    {
        Server->Tick();
    }
}

void FWebSocketDemoServer::OnClientConnected(INetworkingWebSocket* NewClient)
{
    UE_LOG(LogTemp, Log, TEXT("Demo Server: Client Connected"));
    ConnectedClients.Add(NewClient);

    // 为这个新客户端设置数据接收和断开回调
    FWebSocketPacketReceivedCallBack ReceivedCallback;
    ReceivedCallback.BindRaw(this, &FWebSocketDemoServer::OnClientDataReceived, NewClient); // 使用 BindRaw 绑定额外参数

    FWebSocketInfoCallBack ClosedCallback;
    ClosedCallback.BindRaw(this, &FWebSocketDemoServer::OnClientDisconnected, NewClient);

    NewClient->SetReceiveCallBack(ReceivedCallback);
    NewClient->SetSocketClosedCallBack(ClosedCallback);

    // 发送欢迎消息
    FString WelcomeMsg = TEXT("Welcome to the UE WebSocket Server!");
    NewClient->Send((uint8*)TCHAR_TO_UTF8(*WelcomeMsg), WelcomeMsg.Len());
}

void FWebSocketDemoServer::OnClientDataReceived(void* Data, int32 DataSize, INetworkingWebSocket* Client)
{
    FString ReceivedString = FString(UTF8_TO_TCHAR(static_cast<const char*>(Data)));
    UE_LOG(LogTemp, Log, TEXT("Demo Server received: %s"), *ReceivedString);
}

void FWebSocketDemoServer::OnClientDisconnected(INetworkingWebSocket* Client)
{
    UE_LOG(LogTemp, Log, TEXT("Demo Server: Client Disconnected"));
    ConnectedClients.Remove(Client);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 UE_LOG 迁移为新格式 UE_LOGF。 |
| 2026-04-13 | `ae217cfd` | IPv6 Support for PixelStreaming2 signaling server | 为 PixelStreaming2 信令服务器添加了 IPv6 支持，与本插件网络协议配置相关。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 执行引擎代码修复，将所有空析构函数改为 = default 声明。 |
| 2025-10-07 | `dcc26116` | Fixed up plugins that have both Base and Default ini files, and one plugin (WebSocketNetworking) t | 修复了同时拥有 Base 和 Default ini 文件的插件，包括本插件。 |
| 2025-09-18 | `49fd637a` | The source files included were modified by the UnrealCodeFixup tool so that they can pass the -merge | 源代码文件被 UnrealCodeFixup 工具修改以通过合并检查。 |

### 维护评价

该插件创建于 2019 年，属于 **实验性** 插件（`EnabledByDefault=false`）。从最近的 git 历史看，它仍在被持续维护和更新（2026 年仍有功能性提交，如 IPv6 支持）。更新内容主要涉及引擎级别的代码现代化、构建修复和平台支持增强。

**建议**：对于需要在 HTML5/浏览器环境中部署并使用 UE 网络功能的项目，此插件是 **可用且仍在维护** 的选择。但由于其“实验性”标签和对传统 NetDriver 的替换要求，在正式项目中使用时需充分测试，并注意其与第三方服务（如 Steam）组件的兼容性问题。对于非浏览器环境，通常无需使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WebSocketNetworking)