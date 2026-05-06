# Web Socket Messaging

> Adds a WebSocket based transport layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 中文名 | WebSocket 消息传输 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebSocketMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WebSocketMessaging) | |

---

## 用途

WebSocket Messaging 插件为 UE5 的 **消息总线 (Message Bus)** 子系统添加了一个基于 WebSocket 的传输层。它允许不同网络上的计算机或设备之间通过 WebSocket 协议发送和接收消息，从而使得跨平台、跨进程的通信更加灵活。

插件解决了以下问题：
- 原生消息总线（如 UDP）可能受到防火墙或网络拓扑限制。
- 需要与外部应用程序（如 Web 前端、移动应用、编辑器工具）通过标准 WebSocket 协议进行实时通信。
- 需要自动发现局域网内的其他 Unreal 实例（通过 Multicast Discovery Beacon）。

---

## 使用场景

- **远程控制编辑器**：在外部设备上运行一个 WebSocket 客户端，通过消息总线向 Unreal Editor 发送指令（如执行蓝图、切换关卡）。
- **多用户协作**：多个 Unreal 实例（如分离式 VR 渲染、多机推流）通过 WebSocket 交换同步数据。
- **与 Web 应用集成**：Web 前端通过 ws:// 连接发送 JSON 格式消息，Unreal 端解析并响应。
- **自建局域网发现**：利用内置的 Beacon 组件自动广播服务信息，免去手动配置 IP 地址。

---

## 蓝图用法

该插件没有公开任何蓝图可调用节点。它工作在底层传输层，通过 C++ 配置和启动。所有消息发送/接收仍通过引擎标准的 **Message Bus** API 完成（UObject 消息、结构体消息）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 插件不提供 BlueprintCallable 函数 | - |

---

## C++ 用法

### 头文件引入

```cpp
#include "IWebSocketMessagingModule.h"
#include "WebSocketMessagingSettings.h"
```

### 基本用法

以下示例展示了如何在模块启动时启用 WebSocket 消息传输，并连接到指定的 WebSocket 端点。

```cpp
// 在模块的 StartupModule() 中调用
void FMyModule::StartupModule()
{
    // 获取 WebSocket Messaging 模块
    IWebSocketMessagingModule* WSMessaging = FModuleManager::LoadModulePtr<IWebSocketMessagingModule>("WebSocketMessaging");
    if (WSMessaging)
    {
        // 检查传输是否已经在运行
        if (!WSMessaging->IsTransportRunning())
        {
            // 配置设置（可通过 Project Settings -> WebSocket Messaging 修改）
            UWebSocketMessagingSettings* Settings = GetMutableDefault<UWebSocketMessagingSettings>();
            Settings->EnableTransport = true;
            Settings->ServerPort = 8888;                    // 本地服务端口
            Settings->ConnectToEndpoints.Add(TEXT("ws://other-unreal-instance:8888")); // 连接到远程
            Settings->SaveConfig();

            // 模块初始化时会自动读取设置并启动传输
            // 如果需要在运行时手动重新初始化，调用 InitializeBridge()
        }

        int32 ServerPort = WSMessaging->GetServerPort();
        UE_LOG(LogTemp, Log, TEXT("WebSocket Messaging server on port %d"), ServerPort);
    }
}
```

### 进阶用法：自定义序列化格式与 Beacon 发现

```cpp
// 设置 JSON 序列化并使字段名首字母小写
UWebSocketMessagingSettings* Settings = GetMutableDefault<UWebSocketMessagingSettings>();
Settings->ServerTransportFormat = EWebSocketMessagingTransportFormat::Json;
Settings->bMessageSerializationStandardizeCase = true;

// 启用局域网发现 Beacon
Settings->bEnableDiscoveryListener = true;
Settings->DiscoveryEndpoint = TEXT("230.0.0.4");
Settings->DiscoveryPort = 12345;
Settings->BroadcastEndpoint = TEXT("230.0.0.4");
Settings->BroadcastPort = 12345;

// 添加自定义服务元数据（会被广播给发现者）
Settings->AdvertisedServices.Empty();
FWebSocketMessagingBeaconService Service;
Service.Name = "MyGameServer";
Service.Port = 8888;
Settings->AdvertisedServices.Add(Service);

Settings->SaveConfig();
```

---

## Demo 示例

一个完整的最小示例：在自定义 GameInstance 中启用 WebSocket Messaging。

### MyGameInstance.h

```cpp
#pragma once

#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
};
```

### MyGameInstance.cpp

```cpp
#include "MyGameInstance.h"
#include "IWebSocketMessagingModule.h"
#include "WebSocketMessagingSettings.h"
#include "Modules/ModuleManager.h"

void UMyGameInstance::Init()
{
    Super::Init();

    // 加载 WebSocket Messaging 模块
    IWebSocketMessagingModule* WSMessaging = FModuleManager::LoadModulePtr<IWebSocketMessagingModule>("WebSocketMessaging");
    if (WSMessaging)
    {
        // 设置配置（建议在 Project Settings 中预先设置，此处仅演示）
        UWebSocketMessagingSettings* Settings = GetMutableDefault<UWebSocketMessagingSettings>();
        Settings->EnableTransport = true;
        Settings->ServerPort = 0;                // 0 表示不启动服务端，仅作为客户端
        Settings->ConnectToEndpoints.Add(TEXT("ws://localhost:8888"));
        Settings->SaveConfig();

        // 如果需要，手动重新初始化消息桥
        // 注意：通常模块在 StartupModule 时已初始化，此处仅展示获取
        UE_LOG(LogTemp, Log, TEXT("WebSocket Messaging transport running: %s"), WSMessaging->IsTransportRunning() ? TEXT("Yes") : TEXT("No"));
    }
}
```

---

## 模块依赖

**虽然本插件是一个单独的插件，但其功能依赖于以下其他插件和引擎模块**：

| 模块 / 插件 | 用途 |
|---|---|
| `WebSocketNetworking` | 提供底层的 WebSocket 客户端与服务器实现 |
| `DiscoveryBeaconReceiver` | 提供局域网多播服务发现机制 |
| `Messaging` (引擎模块) | UE 消息总线框架（标准依赖，不单独列出） |

在您的 `.Build.cs` 中，如果要在自己的模块中引用该插件的接口，需要添加以下依赖（仅包含非标准依赖）：

```cpp
PublicDependencyModuleNames.AddRange(new string[] {
    "WebSocketMessaging",
    "WebSocketNetworking",
    "DiscoveryBeaconReceiver"
});
```

---

## 维护状态

### 近期更新

- 2025-09-12 `ce6ff392` — 修复 `nodiscard` 属性忽略返回值的问题
- 2025-08-21 `dfe86da3` — 将默认服务器传输格式改为 JSON
- 2024-07-24 `0954dcc2` — 添加描述使插件更易通过“websocket”关键词搜索
- 2024-06-26 `0aaf98a1` — 修复弃用的 `FString` 用法
- 2024-05-14 `6eb2d723` — 代码风格清理（初始版本）

### 维护评价

- **创建时间**：2024-05-14（约 1 年）
- **近期更新**：2025 年 9 月仍有修复和功能调整，显示活跃维护。
- **内容**：插件为实验性，但已具备完整功能（序列化、发现、多客户端）。默认格式已改为更通用的 JSON。
- **推荐使用**：✅ 推荐。对于需要 WebSocket 消息传输的场景，该插件是官方解决方案。已知限制：仅支持 Windows/Mac/Linux，不支持主机平台（如 Console）。实验性标签意味着 API 后续可能变动，但目前稳定。

---

## 相关链接

- [源码（GitHub）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WebSocketMessaging)
- [官方文档](https://docs.unrealengine.com/5.5/en-US/messaging-system-in-unreal-engine/)（消息总线系统概念）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WebSocketMessaging/Source)（暂无独立测试文件夹，但可通过插件源码中的示例了解用法）