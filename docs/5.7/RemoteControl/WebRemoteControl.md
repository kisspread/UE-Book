# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control API 是一个功能强大的远程控制框架，其核心目的是**通过标准的网络协议（HTTP 和 WebSocket）暴露 Unreal Engine 的内部状态和功能**，从而实现外部应用程序对引擎的远程操控。

它解决的核心问题是：如何让第三方应用（如自定义的 UI 工具、自动化脚本、移动设备 App、其他 DCC 软件）能够安全、高效地读取和修改运行中或编辑器中的 Unreal Engine 实例的数据和行为。这在虚拟制片、自动化测试、自定义编辑器工具链等场景中至关重要。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙拍摄现场，使用平板电脑或自定义控制台远程调整场景灯光、摄像机参数或 Actor 位置。
- **自动化测试与部署**：通过脚本（如 Python）向运行中的引擎实例发送 HTTP 请求，触发特定的游戏逻辑或收集性能数据，实现无人值守的自动化测试。
- **自定义编辑器工具**：开发一个独立的 Web 前端界面，用于批量管理资产、配置关卡或监控编辑器状态，而无需深入编写编辑器模块。
- **多用户协作**：结合 `RemoteControlMultiUser` 模块，在多人协同编辑时，通过网络同步对引擎对象的远程修改。

## 蓝图用法

本插件的核心功能主要通过 C++ 接口暴露。`IWebRemoteControlModule` 提供了管理服务器和注册路由的接口，而 `WebRemoteControlUtils` 提供了序列化工具。蓝图层面通常不直接操作这些底层网络细节，而是通过插件提供的更高层的 Remote Control Preset 和 Remote Control Panel 资产进行配置和使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Web Remote Control Module` | 获取 WebRemoteControl 模块的单例接口，用于管理 HTTP/WebSocket 服务器。 | `IWebRemoteControlModule` (通过模块系统获取) |

## C++ 用法

### 头文件引入

```cpp
#include "IWebRemoteControlModule.h"
#include "WebRemoteControlUtils.h"
```

### 基本用法

以下示例展示了如何获取模块接口并监听服务器事件。

```cpp
// 来源：基于 IWebRemoteControlModule.h 接口推断的典型用法
#include "IWebRemoteControlModule.h"

void SetupRemoteControl()
{
    // 1. 获取模块接口
    IWebRemoteControlModule& WebRCModule = FModuleManager::GetModuleChecked<IWebRemoteControlModule>(TEXT("WebRemoteControl"));

    // 2. 监听 HTTP 服务器启动事件
    WebRCModule.OnHttpServerStarted().AddLambda([](uint32 Port)
    {
        UE_LOG(LogTemp, Log, TEXT("Remote Control HTTP Server started on port: %d"), Port);
    });

    // 3. 监听 WebSocket 客户端连接
    WebRCModule.OnWebSocketConnectionOpened().AddLambda([](const FGuid& ClientId)
    {
        UE_LOG(LogTemp, Log, TEXT("WebSocket client connected: %s"), *ClientId.ToString());
    });

    // 4. 检查服务器状态
    if (WebRCModule.IsHttpServerRunning())
    {
        UE_LOG(LogTemp, Log, TEXT("HTTP Server is already running."));
    }
}
```

### 进阶用法

注册一个自定义的 WebSocket 路由来处理特定消息。

```cpp
// 来源：基于 RemoteControlWebsocketRoute.h 和 IWebRemoteControlModule.h 接口推断
#include "IWebRemoteControlModule.h"
#include "RemoteControlWebsocketRoute.h"

void RegisterCustomWebSocketRoute()
{
    IWebRemoteControlModule& WebRCModule = FModuleManager::GetModuleChecked<IWebRemoteControlModule>(TEXT("WebRemoteControl"));

    // 定义消息处理委托
    FWebSocketMessageDelegate MessageHandler;
    MessageHandler.BindLambda([](const FRemoteControlWebSocketMessage& Message)
    {
        // 处理来自客户端的 “MyCustomMessage”
        UE_LOG(LogTemp, Log, TEXT("Received custom message from client %s"), *Message.ClientId.ToString());

        // 可以在此处解析 Message.RequestPayload 并执行相应逻辑
        // 例如，反序列化 JSON 负载
        // FMyCustomData Data;
        // if (WebRemoteControlUtils::DeserializeMessage(Message.RequestPayload, Data))
        // {
        //     // 处理数据...
        // }

        // 向客户端发送响应
        TArray<uint8> ResponsePayload;
        FString ResponseString = TEXT("{\"status\": \"ok\"}");
        WebRemoteControlUtils::ConvertToUTF8(ResponseString, ResponsePayload);
        WebRCModule.SendWebsocketMessage(Message.ClientId, ResponsePayload);
    });

    // 创建并注册路由
    FRemoteControlWebsocketRoute CustomRoute(
        TEXT("Handles custom application logic"),
        TEXT("MyCustomMessage"), // 客户端发送此消息名时触发
        MessageHandler
    );

    WebRCModule.RegisterWebsocketRoute(CustomRoute);

    // 记得在模块关闭或不再需要时注销路由
    // WebRCModule.UnregisterWebsocketRoute(CustomRoute);
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何创建一个自定义的 WebSocket 路由来响应 “Ping” 消息。

### MyRemoteControlModule.h
```cpp
// MyRemoteControlModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyRemoteControlModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FDelegateHandle PingRouteHandle;
};
```

### MyRemoteControlModule.cpp
```cpp
// MyRemoteControlModule.cpp
#include "MyRemoteControlModule.h"
#include "IWebRemoteControlModule.h"
#include "RemoteControlWebsocketRoute.h"
#include "WebRemoteControlUtils.h"

#define LOCTEXT_NAMESPACE "FMyRemoteControlModule"

void FMyRemoteControlModule::StartupModule()
{
    // 确保 WebRemoteControl 模块已加载
    if (FModuleManager::Get().IsModuleLoaded(TEXT("WebRemoteControl")))
    {
        IWebRemoteControlModule& WebRCModule = FModuleManager::GetModuleChecked<IWebRemoteControlModule>(TEXT("WebRemoteControl"));

        // 定义 Ping 消息处理器
        FWebSocketMessageDelegate PingHandler;
        PingHandler.BindLambda([&WebRCModule](const FRemoteControlWebSocketMessage& Message)
        {
            UE_LOG(LogTemp, Display, TEXT("Ping received from client: %s"), *Message.ClientId.ToString());

            // 构造 Pong 响应
            TArray<uint8> PongPayload;
            FString PongString = TEXT("{\"message\": \"Pong\"}");
            WebRemoteControlUtils::ConvertToUTF8(PongString, PongPayload);

            // 发送回客户端
            WebRCModule.SendWebsocketMessage(Message.ClientId, PongPayload);
        });

        // 注册路由
        FRemoteControlWebsocketRoute PingRoute(
            TEXT("Responds to Ping messages with Pong"),
            TEXT("Ping"),
            PingHandler
        );
        WebRCModule.RegisterWebsocketRoute(PingRoute);
        // 注意：这里为了示例简洁，没有保存用于注销的句柄。实际应用中应妥善管理。
    }
}

void FMyRemoteControlModule::ShutdownModule()
{
    // 在实际模块中，应在此处注销所有注册的路由
    // if (FModuleManager::Get().IsModuleLoaded(TEXT("WebRemoteControl")))
    // {
    //     IWebRemoteControlModule& WebRCModule = FModuleManager::GetModuleChecked<IWebRemoteControlModule>(TEXT("WebRemoteControl"));
    //     WebRCModule.UnregisterWebsocketRoute(...);
    // }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyRemoteControlModule, MyRemoteControl)
```

## 模块依赖

从模块名称和功能推断，使用 `WebRemoteControl` 模块通常需要依赖以下模块。**注意**：以下为根据功能推断的常见依赖，具体需以项目实际 `Build.cs` 为准。

| 模块 | 用途 |
|---|---|
| `HTTP` | 提供底层 HTTP 服务器和客户端功能。 |
| `WebSockets` | 提供 WebSocket 服务器和客户端功能。 |
| `Json` | 用于 JSON 数据的解析和生成，是序列化/反序列化的基础。 |
| `Serialization` | 提供 `FStructSerializer` 和 `FStructDeserializer` 等核心序列化框架。 |

## 维护状态

### 近期更新

- 2025-10-03 ce6ff39 修复了 `FTSTicker::RemoveTicker` 返回值被忽略的编译警告。
- 2025-09-15 2b1285e 允许在 HTTP 请求中指定字符集 (charset)。
- 2025-08-20 0c70681 修复了当单个布尔属性更改时，更新未通过 WebSocket 发送的问题 (UE-225092)。

### 维护评价

Remote Control API 是一个**成熟且处于活跃维护状态**的插件。它创建于 2019 年，是 Unreal Engine 虚拟制片工具链的核心组件之一。从近期的提交记录可以看出，Epic 团队仍在持续修复 bug、优化功能和提升稳定性（如修复特定属性类型的同步问题、改进 HTTP 处理）。作为 VirtualProduction 分类下的官方插件，其代码质量和长期支持有较高保障。**推荐在需要远程控制引擎的项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/remote-control-api-in-unreal-engine/) (通常位于 Virtual Production 章节下)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl/Tests) (如果存在)