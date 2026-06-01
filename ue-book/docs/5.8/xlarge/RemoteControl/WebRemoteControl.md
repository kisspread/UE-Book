# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制 API |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control API 是一套完整的远程控制引擎工具集，通过内置的 HTTP 服务器和 WebSocket 服务器，允许第三方应用程序和 Web 服务远程控制 Unreal Engine。

**核心解决的问题**：在虚拟制片（Virtual Production）、交互式装置、以及需要外部工具驱动引擎的场景中，开发者需要一种标准化的方式来远程读取和修改引擎中的属性、调用函数、监听变化。Remote Control API 提供了：

- **HTTP REST API**：通过标准 HTTP 请求远程访问引擎对象的属性和函数
- **WebSocket 实时通信**：支持双向实时通信，可监听属性变化、Actor 变动等事件
- **Remote Control Preset（预设）系统**：将需要暴露的属性、函数、Actor 组织成可管理的预设资产
- **Web 控制面板 UI**：提供浏览器端的可视化控制界面
- **安全机制**：支持密码验证、IP 白名单、CORS 策略等安全控制
- **多用户支持**：支持事务管理、序列号同步等多客户端协作机制

## 使用场景

- **虚拟制片现场**：灯光师、导演通过平板或手机远程调整灯光参数、摄像机位置
- **交互式装置**：使用 TouchDesigner、Processing 等外部工具实时驱动 Unreal 场景
- **自动化测试**：通过 HTTP 请求批量执行引擎操作
- **Web 管理面板**：构建基于浏览器的 Unreal Engine 远程管理界面
- **多机协同**：一台机器运行引擎，另一台机器通过网络控制
- **第三方工具集成**：Max、Maya、Blender 等 DCC 工具与 Unreal 的桥接

## 蓝图用法

Remote Control API 主要通过 C++ 接口和 HTTP/WebSocket 协议使用，蓝图层面的直接调用较少。核心交互通过 Remote Control Preset 资产完成。

### 核心概念

| 概念 | 说明 |
|---|---|
| Remote Control Preset | 资产类型，用于组织要暴露的属性、函数、Actor |
| Exposed Property | 暴露的属性，可通过 HTTP/WebSocket 远程读写 |
| Exposed Function | 暴露的函数，可通过 HTTP/WebSocket 远程调用 |
| Exposed Actor | 暴露的 Actor，可远程监听其属性变化 |
| Controller | 虚拟属性控制器，可映射到多个底层属性 |
| Layout Group | 预设中的分组，用于组织暴露的字段 |

### HTTP API 概览

插件在启动时会注册大量 HTTP 路由，主要包括：

| 路由 | 方法 | 说明 |
|---|---|---|
| `/remote/info` | GET | 获取 API 信息和可用路由列表 |
| `/remote/presets` | GET | 列出所有可用的 Remote Control Preset |
| `/remote/preset/:id` | GET | 获取指定预设的详细信息 |
| `/remote/preset/:id/property` | POST | 读取或设置预设中的属性 |
| `/remote/preset/:id/function` | POST | 调用预设中暴露的函数 |
| `/remote/object/call` | POST | 直接调用引擎对象的函数 |
| `/remote/object/property` | POST | 直接读取或设置对象属性 |
| `/remote/batch` | POST | 批量执行多个请求 |
| `/remote/search/asset` | GET | 搜索资产 |
| `/remote/search/actor` | GET | 搜索 Actor |

## C++ 用法

### 头文件引入

```cpp
#include "IWebRemoteControlModule.h"
```

### 基本用法 - 获取模块接口

```cpp
// 获取 WebRemoteControl 模块实例
IWebRemoteControlModule& WebRCModule = FModuleManager::LoadModuleChecked<IWebRemoteControlModule>("WebRemoteControl");

// 检查 HTTP 服务器是否运行
bool bHttpRunning = WebRCModule.IsHttpServerRunning();

// 检查 WebSocket 服务器是否运行
bool bWSRunning = WebRCModule.IsWebSocketServerRunning();
```

### 监听服务器事件

```cpp
// 监听 HTTP 服务器启动（获取端口号）
WebRCModule.OnHttpServerStarted().AddLambda([](uint32 Port) {
    UE_LOG(LogTemp, Log, TEXT("Remote Control HTTP Server started on port %d"), Port);
});

// 监听 HTTP 服务器停止
WebRCModule.OnHttpServerStopped().AddLambda([]() {
    UE_LOG(LogTemp, Log, TEXT("Remote Control HTTP Server stopped"));
});

// 监听 WebSocket 连接打开
WebRCModule.OnWebSocketConnectionOpened().AddLambda([](FGuid ClientId) {
    UE_LOG(LogTemp, Log, TEXT("WebSocket client connected: %s"), *ClientId.ToString());
});

// 监听 WebSocket 连接关闭
WebRCModule.OnWebSocketConnectionClosed().AddLambda([](FGuid ClientId) {
    UE_LOG(LogTemp, Log, TEXT("WebSocket client disconnected: %s"), *ClientId.ToString());
});
```

### 注册请求预处理器

```cpp
// 注册一个请求预处理器，可以在请求被处理之前拦截或修改
FDelegateHandle Handle = WebRCModule.RegisterRequestPreprocessor(
    [](const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete) -> bool
    {
        // 返回 true 表示已处理（请求不会继续传递）
        // 返回 false 表示放行（请求继续传递给默认处理器）
        
        // 示例：拒绝来自特定 IP 的请求
        FString ClientIP = Request.Headers.Contains("x-forwarded-for") 
            ? Request.Headers["x-forwarded-for"] 
            : TEXT("unknown");
        
        if (ClientIP == TEXT("192.168.1.100"))
        {
            auto Response = MakeUnique<FHttpServerResponse>();
            Response->Code = EHttpServerResponseCodes::Denied;
            Response->Body = { 'A', 'c', 'c', 'e', 's', 's', ' ', 'D', 'e', 'n', 'i', 'e', 'd' };
            OnComplete(MoveTemp(Response));
            return true; // 已处理
        }
        
        return false; // 放行
    }
);

// 取消注册
WebRCModule.UnregisterRequestPreprocessor(Handle);
```

### 发送 WebSocket 消息

```cpp
// 向特定客户端发送 WebSocket 消息
FGuid TargetClientId = /* ... */;
TArray<uint8> Payload;
WebRemoteControlUtils::ConvertToUTF8(TEXT("{\"type\":\"Hello\"}"), Payload);
WebRCModule.SendWebsocketMessage(TargetClientId, Payload);
```

### 注册自定义 WebSocket 路由

```cpp
FRemoteControlWebsocketRoute Route;
Route.MessageName = TEXT("MyCustomMessage");
Route.Handler = [](const FRemoteControlWebSocketMessage& Message) {
    // 处理自定义 WebSocket 消息
    UE_LOG(LogTemp, Log, TEXT("Received custom message"));
};

WebRCModule.RegisterWebsocketRoute(Route);

// 取消注册
WebRCModule.UnregisterWebsocketRoute(Route);
```

### JSON 序列化工具

```cpp
// 序列化 UStruct 到 UTF-8 JSON
FMyStruct Data;
TArray<uint8> Payload;
WebRemoteControlUtils::SerializeMessage(Data, Payload);

// 反序列化 UTF-8 JSON 到 UStruct
TArray<uint8> JsonPayload = /* ... */;
FMyStruct DeserializedData;
bool bSuccess = WebRemoteControlUtils::DeserializeMessage(JsonPayload, DeserializedData);

// UTF-8 和 TCHAR 之间的转换
TArray<uint8> UTF8Payload;
TArray<uint8> TCHARPayload;
WebRemoteControlUtils::ConvertToTCHAR(UTF8Payload, TCHARPayload);
WebRemoteControlUtils::ConvertToUTF8(TCHARPayload, UTF8Payload);
```

### 进阶用法 - 自定义预处理器链

```cpp
// 使用 WebsocketMessageRouter 添加预处理器
// 在模块内部，FWebsocketMessageRouter 支持消息预分发检查
// 预处理器返回 false 可阻止消息被实际处理

// IP 验证预处理器（由模块内部注册）
// 密码验证预处理器（由模块内部注册）
// 用户可注册自定义预处理器实现额外安全策略
```

## Demo 示例

### 最小示例 - 读取和监听 Remote Control 模块状态

```cpp
// MyRemoteControlListener.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyRemoteControlListener.generated.h"

UCLASS()
class UMyRemoteControlListener : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    FDelegateHandle HttpStartHandle;
    FDelegateHandle WSConnectionHandle;
    FDelegateHandle WSDisconnectHandle;
};
```

```cpp
// MyRemoteControlListener.cpp
#include "MyRemoteControlListener.h"
#include "IWebRemoteControlModule.h"

void UMyRemoteControlListener::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    if (IWebRemoteControlModule* WebRCModule = FModuleManager::GetModulePtr<IWebRemoteControlModule>("WebRemoteControl"))
    {
        // 监听 HTTP 服务器启动
        HttpStartHandle = WebRCModule->OnHttpServerStarted().AddLambda(
            [](uint32 Port) {
                UE_LOG(LogTemp, Log, TEXT("[RemoteControl] HTTP Server started on port %u"), Port);
            }
        );

        // 监听 WebSocket 客户端连接
        WSConnectionHandle = WebRCModule->OnWebSocketConnectionOpened().AddLambda(
            [](FGuid ClientId) {
                UE_LOG(LogTemp, Log, TEXT("[RemoteControl] Client connected: %s"), *ClientId.ToString());
            }
        );

        // 监听 WebSocket 客户端断开
        WSDisconnectHandle = WebRCModule->OnWebSocketConnectionClosed().AddLambda(
            [](FGuid ClientId) {
                UE_LOG(LogTemp, Log, TEXT("[RemoteControl] Client disconnected: %s"), *ClientId.ToString());
            }
        );
    }
}

void UMyRemoteControlListener::Deinitialize()
{
    if (IWebRemoteControlModule* WebRCModule = FModuleManager::GetModulePtr<IWebRemoteControlModule>("WebRemoteControl"))
    {
        WebRCModule->OnHttpServerStarted().Remove(HttpStartHandle);
        WebRCModule->OnWebSocketConnectionOpened().Remove(WSConnectionHandle);
        WebRCModule->OnWebSocketConnectionClosed().Remove(WSDisconnectHandle);
    }

    Super::Deinitialize();
}
```

## 模块依赖

本插件包含 8 个 Runtime 模块，各模块之间存在依赖关系。以下列出使用者需要注意的**特殊依赖**：

| 模块 | 用途 |
|---|---|
| `HTTPServer` | 内置 HTTP 服务器，提供 REST API 能力 |
| `WebSocketNetworking` | WebSocket 服务器底层实现 |
| `JsonUtilities` | JSON 序列化/反序列化支持 |
| `StructUtils` | 结构体序列化和反射工具 |
| `RemoteControl` | 核心模块，管理暴露的属性/函数/Actor |
| `RemoteControlLogic` | 虚拟属性控制器逻辑 |
| `RemoteControlProtocol` | 协议抽象层 |
| `RemoteControlCommon` | 公共类型定义和工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1716f2e0` | Remote Control: added missing ApplyColorWheelDelta and ApplyColorGradingWheelDelta to the built-in a | 新增内置函数支持色彩轮和色彩校正轮增量操作 |
| 2026-05-20 | `d724bb52` | Remote Control: fixed uninitialized ObjectClass in FRCRemoteFunctionCallParams, sometimes causing a | 修复远程函数调用参数中 ObjectClass 未初始化导致的崩溃 |
| 2026-05-20 | `12d5ae7f` | Remote Control: added allow list for remote function calls, and specifying built-in functions to all | 新增远程函数调用白名单机制，指定内置允许的函数列表 |
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | Motion Design 相关的 UI 调整（非直接 RC 改动） |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double 转 float 警告 |

### 维护评价

Remote Control API 是一个**活跃维护中**的成熟插件：

- **创建于 2019 年**，至今已有约 7 年历史，属于虚拟制片工作流的核心组件
- **近期更新频繁**：2026 年 5 月有多次功能性更新，包括安全增强（函数调用白名单）和 bug 修复
- **持续演进**：不断添加新的内置函数支持，安全机制也在持续完善
- **推荐使用**：作为 Epic 官方维护的虚拟制片核心工具，稳定性有保障，API 设计成熟

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/remote-control-api-in-unreal-engine/)