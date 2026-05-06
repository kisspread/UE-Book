# Experimental WebSocket Networking Plugin

> WebSocket Networking - NOTE: MUST disable all other existing NetDriverDefinitions in order to use WebSocketNetDriver. ALSO: MUST disable all PackHandlerComponents not supported by HTML5/Websockets (e.g. SteamAuthComponentModuleInterface)

| 属性 | 值 |
|---|---|
| 中文名 | WebSocket网络插件 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebSocketNetworking` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WebSocketNetworking) | |

## 用途

该插件基于流行的 [libwebsockets](https://libwebsockets.org/) 库，为 Unreal Engine 提供了原生的 **WebSocket 网络驱动**。它实现了 `UNetDriver` 和 `UNetConnection` 的子类（`UWebSocketNetDriver` 和 `UWebSocketConnection`），从而允许你使用 WebSocket 协议作为 UE 的网络传输层。

**解决什么问题？**

UE 默认的网络驱动通常基于 UDP 或 TCP。但在以下场景中，WebSocket 是更好的选择：

- **HTML5/Web 客户端**：浏览器环境默认不支持原始 UDP/TCP 套接字，但 WebSocket 是标准协议。当你的 UE 游戏需要导出到 WebGL 并与专用服务器通信时，必须使用 WebSocket。
- **防火墙友好**：WebSocket 使用标准的 HTTP/S 端口（80/443），更容易穿透企业防火墙和 NAT 设备，而 UDP 经常被限制。
- **与 Web 服务集成**：如果你需要游戏客户端与现有的 Web 服务器、API 或第三方服务进行实时双向通信，WebSocket 是天然的选择。

> ⚠️ **重要限制**：此插件是**实验性**且默认禁用的。启用它需要修改 `DefaultEngine.ini`，禁用其他所有 NetDriver 定义，并移除所有不被 WebSocket 支持的包处理器（如 SteamAuth）。

## 使用场景

- **制作一个纯网页端（HTML5/WebGL）的游戏**：想要让游戏通过浏览器运行，并与后端服务器实时交互，必须使用此插件作为网络驱动。
- **需要一个可被任何 Web 客户端连接的 UE 服务器**：你的服务端（UE 服务器）需要接受来自 Unity、JavaScript、React Native 等非 UE 客户端的 WebSocket 连接。
- **实现游戏内嵌的 HTTP 服务器功能**：插件内部的 WebSocket 服务器支持绑定 HTTP 挂载点，可以静态文件服务器（如网页资源）。

## 蓝图用法

此插件**没有**暴露任何蓝图节点或蓝图可调用函数。所有的配置和操作都需要通过 C++ 或配置文件来完成。

### 如何配置

1. 在 `Project Settings` -> `Plugins` -> `WebSocket Networking` 中启用插件。
2. 在 `Config/DefaultEngine.ini` 中添加以下配置来替换默认的 NetDriver：

```ini
[/Script/Engine.Engine]
;! 注释掉或删除所有其他的 NetDriverDefinitions
;+NetDriverDefinitions=(DefName="GameNetDriver", DriverClassName="/Script/OnlineSubsystemUtils.IpNetDriver", DriverClassNameFallback="/Script/OnlineSubsystemUtils.IpNetDriver")

; 添加 WebSocket NetDriver
+NetDriverDefinitions=(DefName="WebSocketNetDriver", DriverClassName="/Script/WebSocketNetworking.WebSocketNetDriver", DriverClassNameFallback="/Script/WebSocketNetworking.WebSocketNetDriver")

; 设置默认网络驱动（可选，当地图没有指定时）
[/Script/Engine.GameEngine]
NetDriverDefinitions=$(NetDriverDefinitions)
```

## C++ 用法

### 头文件引入

```cpp
#include "IWebSocketNetworkingModule.h"
#include "INetworkingWebSocket.h"
#include "IWebSocketServer.h"

// 需要 FModuleManager 来获取模块
#include "Modules/ModuleManager.h"
#include "WebSocketNetworkingDelegates.h"
```

### 基本用法

#### 获取模块接口

```cpp
IWebSocketNetworkingModule& WsModule = FModuleManager::LoadModuleChecked<IWebSocketNetworkingModule>("WebSocketNetworking");
```

#### 创建 WebSocket 服务器（C++）

以下示例展示了如何在 UE 服务器中创建并启动一个 WebSocket 服务器。

```cpp
// 来自: Engine/Plugins/Experimental/WebSocketNetworking/Source/WebSocketNetworking/Private/WebSocketServer.h

// 1. 获取模块接口
IWebSocketNetworkingModule& WsModule = FModuleManager::LoadModuleChecked<IWebSocketNetworkingModule>("WebSocketNetworking");

// 2. 创建服务器实例（返回 TUniquePtr<IWebSocketServer>）
TUniquePtr<IWebSocketServer> Server = WsModule.CreateServer();

// 3. 设置新客户端连接的回调
FWebSocketClientConnectedCallBack OnClientConnected;
OnClientConnected.BindLambda([](INetworkingWebSocket* Socket)
{
    UE_LOG(LogTemp, Warning, TEXT("New WebSocket client connected! Remote: %s"), *Socket->RemoteEndPoint(true));

    // 设置接收数据回调
    FWebSocketPacketReceivedCallBack OnData;
    OnData.BindLambda([](void* Data, int32 DataSize)
    {
        UE_LOG(LogTemp, Warning, TEXT("Received %d bytes"), DataSize);
        FString Message(DataSize, (const char*)Data);
        UE_LOG(LogTemp, Warning, TEXT("Message: %s"), *Message);
    });
    Socket->SetReceiveCallBack(OnData);

    // 设置连接关闭回调
    FWebSocketInfoCallBack OnClose;
    OnClose.BindLambda([]()
    {
        UE_LOG(LogTemp, Warning, TEXT("WebSocket client disconnected."));
    });
    Socket->SetSocketClosedCallBack(OnClose);
});

// 4. 初始化服务器（端口 8888）
if (Server->Init(8888, OnClientConnected))
{
    UE_LOG(LogTemp, Log, TEXT("WebSocket server started on port 8888: %s"), *Server->Info());
}
else
{
    UE_LOG(LogTemp, Error, TEXT("Failed to start WebSocket server!"));
}
```

#### 创建 WebSocket 客户端连接

```cpp
// 来自: Engine/Plugins/Experimental/WebSocketNetworking/Source/WebSocketNetworking/Public/IWebSocketNetworkingModule.h

// 1. 获取模块接口
IWebSocketNetworkingModule& WsModule = FModuleManager::LoadModuleChecked<IWebSocketNetworkingModule>("WebSocketNetworking");

// 2. 构造服务器地址（假设服务器在 ws://localhost:8888）
FInternetAddr ServerAddr;
ServerAddr.SetPort(8888);

// 3. 创建客户端连接
TSharedPtr<INetworkingWebSocket> Connection = WsModule.CreateConnection(ServerAddr);
if (Connection.IsValid())
{
    // 4. 设置连接成功回调
    FWebSocketInfoCallBack OnConnected;
    OnConnected.BindLambda([]()
    {
        UE_LOG(LogTemp, Warning, TEXT("Connected to WebSocket server!"));
    });
    Connection->SetConnectedCallBack(OnConnected);

    // 5. 设置接收数据回调
    FWebSocketPacketReceivedCallBack OnData;
    OnData.BindLambda([](void* Data, int32 DataSize)
    {
        // 处理接收到的数据
    });
    Connection->SetReceiveCallBack(OnData);

    // 6. 发送数据（字符串）
    FString TestMessage = TEXT("Hello, WebSocket!");
    uint8* Data = (uint8*)TCHAR_TO_UTF8(*TestMessage);
    int32 Size = TestMessage.Len();
    Connection->Send(Data, Size, true); // bPrependSize = true 表示在数据前添加长度前缀

    // 7. 在 Tick 中处理连接
    Connection->Tick();
}
```

### 进阶用法

#### 启用 HTTP 文件服务

WebSocket 服务器可以同时作为 HTTP 服务器，提供静态文件服务。

```cpp
// 来自: Engine/Plugins/Experimental/WebSocketNetworking/Source/WebSocketNetworking/Public/IWebSocketServer.h

// 创建 HTTP 挂载点
FWebSocketHttpMount Mount;
Mount.SetPathOnDisk(TEXT("C:/MyWebFiles"));   // 要服务的目录
Mount.SetWebPath(TEXT("/"));                  // URL 路径映射
Mount.SetDefaultFile(TEXT("index.html"));     // 根路径默认文件

TArray<FWebSocketHttpMount> Mounts = { Mount };

// 启用 HTTP 服务（bSecure = false 为 HTTP, true 为 HTTPS）
FWebSocketServerCertificates Certs;  // HTTPS 时需要设置证书路径
Server->EnableHTTPServer(Mounts, false, Certs);
```

#### 使用 SSL/TLS（HTTPS / WSS）

```cpp
FWebSocketServerCertificates Certs;
Certs.SetCertificateFilePath(TEXT("/path/to/cert.pem"));
Certs.SetPrivateKeyFilePath(TEXT("/path/to/privkey.pem"));

// 启用安全模式
TArray<FWebSocketHttpMount> Mounts;
Server->EnableHTTPServer(Mounts, true, Certs);
```

#### 连接过滤

```cpp
// 来自: Engine/Plugins/Experimental/WebSocketNetworking/Source/WebSocketNetworking/Public/WebSocketNetworkingDelegates.h

FWebSocketFilterConnectionCallback FilterCallback;
FilterCallback.BindLambda([](FString Origin, FString ClientIP) -> EWebsocketConnectionFilterResult
{
    UE_LOG(LogTemp, Warning, TEXT("Connection attempt from: %s, Origin: %s"), *ClientIP, *Origin);
    
    if (Origin.Contains(TEXT("allowed-domain.com")))
    {
        return EWebsocketConnectionFilterResult::ConnectionAccepted;
    }
    
    return EWebsocketConnectionFilterResult::ConnectionRefused;
});

Server->SetFilterConnectionCallback(FilterCallback);
```

#### 获取连接 URL 参数

当客户端通过 WebSocket URL（如 `ws://localhost:8888?token=abc&room=42`）连接时，可以获取查询参数：

```cpp
// 来自: Engine/Plugins/Experimental/WebSocketNetworking/Source/WebSocketNetworking/Public/INetworkingWebSocket.h

// 在 OnClientConnected 回调中
void OnClientConnected(INetworkingWebSocket* Socket)
{
    // 获取所有 URL 参数
    TArray<FString> Args = Socket->GetUrlArgs();
    for (const FString& Arg : Args)
    {
        UE_LOG(LogTemp, Log, TEXT("URL Arg: %s"), *Arg);
    }
    
    // 获取指定参数
    FString Token = Socket->GetUrlArgByName(TEXT("token"));
    FString Room = Socket->GetUrlArgByName(TEXT("room"));
}
```

## Demo 示例

以下是一个完整的、可编译的示例，展示了如何启动 WebSocket 服务器并接受客户端连接，同时响应数据。

```cpp
// MyWebSocketServer.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "IWebSocketNetworkingModule.h"
#include "IWebSocketServer.h"
#include "INetworkingWebSocket.h"
#include "MyWebSocketServer.generated.h"

UCLASS()
class AMyWebSocketServer : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void StartPlay() override;
    virtual void Tick(float DeltaSeconds) override;

private:
    TUniquePtr<IWebSocketServer> ServerInstance;
};
```

```cpp
// MyWebSocketServer.cpp
#include "MyWebSocketServer.h"
#include "Modules/ModuleManager.h"

void AMyWebSocketServer::StartPlay()
{
    Super::StartPlay();

    // 1. 获取 WebSocket 模块
    IWebSocketNetworkingModule& WsModule = FModuleManager::LoadModuleChecked<IWebSocketNetworkingModule>("WebSocketNetworking");

    // 2. 创建服务器
    ServerInstance = WsModule.CreateServer();
    if (!ServerInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create WebSocket server!"));
        return;
    }

    // 3. 设置新连接回调
    FWebSocketClientConnectedCallBack OnConnected;
    OnConnected.BindLambda([this](INetworkingWebSocket* Socket)
    {
        FString Endpoint = Socket->RemoteEndPoint(true);
        UE_LOG(LogTemp, Log, TEXT("Client connected from: %s"), *Endpoint);

        // 设置接收回调：回显收到的消息
        FWebSocketPacketReceivedCallBack OnData;
        OnData.BindLambda([Socket](void* Data, int32 Size)
        {
            FString Message(Size, static_cast<const char*>(Data));
            UE_LOG(LogTemp, Log, TEXT("Echoing: %s"), *Message);
            Socket->Send(static_cast<uint8*>(Data), Size, true);
        });
        Socket->SetReceiveCallBack(OnData);

        // 设置关闭回调
        FWebSocketInfoCallBack OnClose;
        OnClose.BindLambda([Endpoint]()
        {
            UE_LOG(LogTemp, Log, TEXT("Client disconnected: %s"), *Endpoint);
        });
        Socket->SetSocketClosedCallBack(OnClose);
    });

    // 4. 初始化（端口 7777）
    if (!ServerInstance->Init(7777, OnConnected))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to start WebSocket server on port 7777!"));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("WebSocket server running on port 7777: %s"), *ServerInstance->Info());
}

void AMyWebSocketServer::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    // 5. 每帧服务 WebSocket 连接
    if (ServerInstance.IsValid())
    {
        ServerInstance->Tick();
    }
}
```

## 模块依赖

在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "WebSocketNetworking",
    "Networking",   // 使用 FInternetAddr 等
});
```

| 模块 | 用途 |
|---|---|
| `Networking` | 提供 `FInternetAddr` 等网络地址类型 |
| `Sockets` | 底层套接字抽象（未直接暴露，但 WebSocketNetworking 内部依赖） |
| `libwebsockets` | 内部使用的第三方 WebSocket 库（自动集成，无需额外配置） |

> 💡 **注意**：`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UMG`, `InputCore` 等常见依赖无需额外指定。

## 维护状态

### 近期更新

来源：git log for `Engine/Plugins/Experimental/WebSocketNetworking/`

- 2025-09-23 `20ee5e0e` — UnrealCodeFixup 工具修改源文件以通过 -merge 编译
- 2025-04-03 `c6441b11` — 修复 Xcode 16.3 编译问题
- 2025-03-13 `b059f7b4` — 修复无脑不可达代码警告
- 2025-02-26 `a057fe70` — [PS2] 新增：配置嵌入式信令服务器以通过 HTTPS 提供内容服务
- 2024-01-09 `20dc6bf0` — QOL：为从 websocket 连接检索 URL 参数添加了辅助方法

### 维护评价

- **创建时间**：2024-01-09（约 2 年）
- **近期更新**：整体活跃度中等。更新以编译修复和代码质量改进为主，但 2025-02-26 的 commit 添加了 HTTPS 服务功能，说明有功能性更新。
- **当前状态**：维护中。最近 6 个月内仍有提交（2025-09-23）。
- **已知限制**：
  - **高度实验性**：必须在配置中禁用所有其他 NetDriver。
  - **无法使用包处理器**：如 SteamAuth 等需要自定义包处理器的功能不兼容。
  - **平台限制**：仅支持 Mac, Win64, Linux（.uplugin 中指定）。
  - **没有蓝图节点**：完全依赖 C++ 或配置文件。
- **推荐度**：**谨慎推荐**。对于需要 WebSocket 网络驱动的项目非常有用，尤其是 HTML5 导出场景。但考虑到其实验性质和严格的配置要求，不适合大型项目或对稳定性要求高的场景，除非你有明确的 WebSocket 需求。

## 相关链接

- [源码（plugin 根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WebSocketNetworking)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/WebSocket-Networking/) *(注：5.7 版本文档可能未完全更新)*
- [libwebsockets 官网](https://libwebsockets.org/)