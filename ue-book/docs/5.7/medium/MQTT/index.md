# MQTT

> MQTT broker and client

| 属性 | 值 |
|---|---|
| 分类 | IOT |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MQTTCore` (Runtime), `MQTTCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-07 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Protocols/MQTT) | |

## 用途

这是一个纯 C++ 实现的 MQTT 客户端 plugin，用于在 UE5 中直接连接 MQTT Broker（消息代理服务器），无需任何外部依赖。MQTT 是物联网（IoT）和消息系统中广泛使用的轻量级发布/订阅协议。

该 plugin 实现了 MQTT v3.1.1 协议的完整客户端功能：连接/断开、发布消息、订阅/取消订阅主题、QoS 0/1/2 保证级别、通配符主题匹配（`+` 单级、`#` 多级），以及 KeepAlive 心跳。它通过 TCP socket 在独立线程上运行连接循环，所有操作都是异步的（基于 `TFuture`）。

注意：.uplugin 的 Description 写的是 "MQTT broker and client"，但实际上**只有 client**，没有 broker/server 的实现。

## 使用场景

- 你在做一个 IoT/智能家居控制应用，需要从传感器接收实时数据（温度、湿度等） → 用 MQTT 订阅传感器 topic
- 你需要将 UE5 场景数据实时发布到外部系统（Node-RED、Home Assistant 等） → 用 MQTT 发布消息
- 你需要与 MQTT Broker（如 Mosquitto、EMQX）通信进行设备间的事件驱动通信 → 用 MQTT plugin
- 你需要在多个 UE5 实例之间做轻量级消息传递，不想搭建专用的网络层 → 用 MQTT

## 蓝图用法

该 plugin 提供完整的蓝图接口。通过 `UMQTTSubsystem`（引擎子系统）创建客户端，然后通过 `UMQTTClientObject` 执行 MQTT 操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Client (From Project URL)` | 使用项目设置中的默认 URL 创建 MQTT 客户端 | `UMQTTSubsystem` |
| `Create Client (From URL)` | 使用指定 URL 创建 MQTT 客户端 | `UMQTTSubsystem` |
| `Get Payload String` | 将 MQTT 消息的 payload 提取为字符串 | `UMQTTSubsystem` |
| `Get Payload Json` | 将 MQTT 消息的 payload 解析为 JSON 对象 | `UMQTTSubsystem` |
| `Connect` | 连接到 MQTT Broker，完成后回调 OnConnect | `UMQTTClientObject` |
| `Disconnect` | 断开连接，完成后回调 OnDisconnect | `UMQTTClientObject` |
| `Publish` | 发布消息到指定 topic，支持 QoS 和 Retain | `UMQTTClientObject` |
| `Subscribe` | 订阅单个 topic，返回 Subscription 对象用于接收消息 | `UMQTTClientObject` |
| `Subscribe (Multiple Topics)` | 批量订阅多个 topic | `UMQTTClientObject` |
| `Unsubscribe` | 取消订阅指定 topic | `UMQTTClientObject` |
| `Set On Message Handler` | 设置订阅的消息回调（委托） | `UMQTTSubscriptionObject` |
| `Get Client Id` | 获取客户端 ID（GUID 字符串） | `UMQTTClientObject` |
| `Get URL` | 获取客户端连接的 URL | `UMQTTClientObject` |

### 蓝图数据类型

| 类型 | 说明 |
|---|---|
| `FMQTTURL` | MQTT 连接地址，包含 Host、Port、Username、Password、Scheme |
| `FMQTTClientMessage` | MQTT 消息结构体，包含 TimeStamp、Topic、Payload、QoS、bRetain |
| `EMQTTQualityOfService` | QoS 枚举：Once (0)、AtLeastOnce (1)、ExactlyOnce (2) |
| `EMQTTScheme` | 协议方案：MQTT（明文）、MQTTS（加密） |
| `EMQTTConnectReturnCode` | 连接返回码：Accepted、RefusedProtocolVersion、RefusedBadUsernamePassword 等 |
| `EMQTTSubscribeReturnCode` | 订阅返回码：Success_QoS0/1/2、Failure |

### 使用示例（蓝图描述）

**基本发布/订阅流程：**

1. 在 BeginPlay 中，调用 `Create Client (From Project URL)` 节点（或 `Create Client (From URL)` 并设置 `FMQTTURL`），Parent 设为 self，获得 `UMQTTClientObject` 引用
2. 调用 `Connect` 节点，绑定 OnConnect 回调。在回调中检查 ReturnCode 是否为 Accepted
3. 调用 `Subscribe` 节点，Topic 设为如 `"sensor/temperature"`，QoS 设为 QoS 0。获得 `UMQTTSubscriptionObject` 引用
4. 对 `UMQTTSubscriptionObject` 调用 `Set On Message Handler`，绑定一个自定义事件。事件参数为 `FMQTTClientMessage`
5. 在事件中使用 `Get Payload String` 或 `Get Payload Json` 提取消息内容
6. 发布时调用 `Publish` 节点，Topic 设为 `"actuator/led"`，Payload 设为 `TArray<uint8>`（需要手动转换字符串到字节数组）

**JSON 消息处理：**

收到 `FMQTTClientMessage` 后，使用 `Get Payload Json` 节点可直接解析为 `FJsonObjectWrapper`，方便蓝图中读写 JSON 字段。

## C++ 用法

### 头文件引入

```cpp
#include "IMQTTClient.h"
#include "IMQTTCoreModule.h"
#include "MQTTClientMessage.h"
#include "MQTTShared.h"
#include "MQTTClientObject.h"
#include "MQTTSubsystem.h"
```

### 基本用法

以下是基于源码分析的核心 C++ API 用法：

**创建客户端（C++ API）：**

```cpp
// 通过模块接口创建客户端
IMQTTCoreModule& MQTTModule = IMQTTCoreModule::Get();

// 使用自定义 URL
FMQTTURL URL;
URL.Host = TEXT("broker.example.com");
URL.Port = 1883;
URL.Username = TEXT("user");
URL.Password = TEXT("pass");

TSharedPtr<IMQTTClient> Client = MQTTModule.GetOrCreateClient(URL);
```

*来源：`MQTTCoreModule.cpp` GetOrCreateClient 方法*

**连接：**

```cpp
Client->Connect(/*bCleanSession=*/true)
    .Next([](EMQTTConnectReturnCode ReturnCode)
    {
        if (ReturnCode == EMQTTConnectReturnCode::Accepted)
        {
            UE_LOG(LogTemp, Log, TEXT("Connected to MQTT broker!"));
        }
    });
```

*来源：`MQTTClient.cpp` Connect 方法*

**发布消息：**

```cpp
// 发布字符串
Client->Publish(TEXT("my/topic"), TEXT("hello world"), EMQTTQualityOfService::Once);

// 发布原始字节
TArray<uint8> Payload = {0x01, 0x02, 0x03};
Client->Publish(TEXT("my/topic"), Payload, EMQTTQualityOfService::AtLeastOnce, /*bRetain=*/false);
```

*来源：`MQTTClient.cpp` Publish 方法*

**订阅并接收消息：**

```cpp
Client->Subscribe(TEXT("sensor/+"),
    [](const FMQTTClientMessage& Message)
    {
        UE_LOG(LogTemp, Log, TEXT("Received on %s: %s"),
            *Message.Topic, *Message.GetPayloadAsString());
    },
    EMQTTQualityOfService::AtLeastOnce);
```

*来源：`IMQTTClient.h` Subscribe 模板方法*

**断开连接：**

```cpp
Client->Disconnect().Next([]()
{
    UE_LOG(LogTemp, Log, TEXT("Disconnected"));
});
```

*来源：`MQTTClient.cpp` Disconnect 方法*

### 进阶用法

**URL 解析：**

```cpp
// 从字符串解析 URL
FMQTTURL URL = FMQTTURL::FromString(TEXT("mqtt://user:pass@broker.example.com:1883"));

// URL 转字符串
FString URLString = URL.ToString(); // "mqtt://user:pass@broker.example.com:1883"

// 验证 URL 有效性
FText ErrorMessage;
if (!URL.IsValid(ErrorMessage))
{
    UE_LOG(LogTemp, Error, TEXT("Invalid URL: %s"), *ErrorMessage.ToString());
}
```

*来源：`MQTTShared.cpp` FMQTTURL::FromString / ToString / IsValid*

**Topic 通配符匹配：**

```cpp
// MQTT 支持两种通配符：
// '+' 匹配单级：  "sensor/+/temperature" 匹配 "sensor/kitchen/temperature"
// '#' 匹配多级：  "sensor/#" 匹配 "sensor/kitchen/temperature/humidity"

// 通配符匹配验证
bool bMatch = FMQTTSubscription::Matches(
    TEXT("sensor/kitchen/temperature"),
    TEXT("sensor/+/temperature")); // true
```

*来源：`MQTTShared.cpp` FMQTTSubscription::Matches*

**Blueprint API (UMQTTSubsystem)：**

```cpp
// 从 C++ 调用蓝图接口
UMQTTSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMQTTSubsystem>();
UMQTTClientObject* ClientObj = Subsystem->GetOrCreateClient_WithProjectURL(this);
```

*来源：`MQTTSubsystem.cpp`*

**Console 命令调试：**

运行时可用以下控制台命令快速测试：

```
MQTT.GetOrCreateClient localhost 1883
MQTT.ClientSubscribe <ClientId> <TopicFilter> <QoS>
MQTT.ClientPublish <ClientId> <Topic> <Payload> <QoS> <bRetain>
MQTT.ClientUnsubscribe <ClientId> <TopicFilter>
MQTT.DestroyClient <ClientId>
```

*来源：`MQTTCoreModule.cpp` RegisterConsoleCommands*

## Demo 示例

### Build.cs 依赖

```csharp
// MyModule.Build.cs
PublicDependencyModuleNames.AddRange(new[]
{
    "Core",
    "CoreUObject",
    "MQTTCore"  // 添加 MQTTCore 依赖
});
```

### .uplugin 插件依赖

确保在项目的 `.uplugin` 中启用 MQTT plugin：

```json
{
    "Plugins": [
        {
            "Name": "MQTT",
            "Enabled": true
        }
    ]
}
```

### 完整最小示例（.h + .cpp）

```cpp
// MyMQTTActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMQTTActor.generated.h"

class IMQTTClient;
struct FMQTTClientMessage;

UCLASS()
class AMyMQTTActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<IMQTTClient, ESPMode::ThreadSafe> MQTTClient;

    void OnMessageReceived(const FMQTTClientMessage& Message);
};
```

```cpp
// MyMQTTActor.cpp
#include "MyMQTTActor.h"

#include "IMQTTClient.h"
#include "IMQTTCoreModule.h"
#include "MQTTClientMessage.h"
#include "MQTTShared.h"

void AMyMQTTActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建客户端
    FMQTTURL URL;
    URL.Host = TEXT("localhost");
    URL.Port = 1883;

    MQTTClient = IMQTTCoreModule::Get().GetOrCreateClient(URL);
    if (!MQTTClient.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create MQTT client"));
        return;
    }

    // 连接
    MQTTClient->Connect(true).Next([this](EMQTTConnectReturnCode ReturnCode)
    {
        if (ReturnCode != EMQTTConnectReturnCode::Accepted)
        {
            UE_LOG(LogTemp, Error, TEXT("MQTT connect failed: %d"), (uint8)ReturnCode);
            return;
        }

        UE_LOG(LogTemp, Log, TEXT("MQTT connected!"));

        // 订阅
        MQTTClient->Subscribe(TEXT("game/events"),
            [this](const FMQTTClientMessage& Msg)
            {
                OnMessageReceived(Msg);
            },
            EMQTTQualityOfService::AtLeastOnce);

        // 发布
        MQTTClient->Publish(TEXT("game/status"), TEXT("hello from UE5"),
            EMQTTQualityOfService::Once);
    });
}

void AMyMQTTActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MQTTClient.IsValid())
    {
        MQTTClient->Disconnect();
        MQTTClient.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyMQTTActor::OnMessageReceived(const FMQTTClientMessage& Message)
{
    UE_LOG(LogTemp, Log, TEXT("Topic: %s, Payload: %s"),
        *Message.Topic, *Message.GetPayloadAsString());

    // 如果是 JSON，可以直接解析
    TSharedPtr<FJsonObject> Json;
    if (Message.GetPayloadAsJson(Json))
    {
        // 处理 JSON...
    }
}
```

## 模块依赖

从 `MQTTCore.Build.cs` 的依赖关系提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `JsonBlueprintUtilities` | 蓝图 JSON 工具（plugin 级依赖） |
| `JsonUtilities` | JSON 序列化/反序列化（payload 解析） |
| `Engine` | 引擎核心（Socket、Subsystem 等） |
| `Json` | JSON 解析库 |
| `Networking` | 网络功能 |
| `Sockets` | TCP Socket 接口 |
| `Projects` | 项目配置访问 |

你的模块要使用此 plugin，至少需要依赖：`MQTTCore`、`Core`、`CoreUObject`。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-11 | `afdf8d7` | Replace some usages of FORCEINLINE with inline in Online modules | 代码风格统一，非功能性修改 |
| 2025-05-09 | `163c5cc` | [MQTT] Removed platform restrictions | 移除了平台限制，意味着该 plugin 现在可在所有平台使用 |
| 2025-02-13 | `ec3fb59` | Replaced `IsValid(this)` under the rest of Engine/ | 代码清理，修复 UE5.6 的 API 变更 |

### 维护评价

- **创建时间**：2022 年 8 月，约 4 年前
- **实验性状态**：`IsExperimentalVersion = true`，`EnabledByDefault = false`——需要手动在项目设置中启用
- **更新频率**：近半年有 3 次更新，但都是编译修复和代码风格调整，无功能性新特性
- **代码质量**：实现完整（MQTT v3.1.1 客户端协议），使用独立线程处理 socket I/O，通过 `TFuture` 实现异步操作。有控制台命令方便调试
- **已知限制**：
  - 仅支持 MQTT v3.1.1，MQTT v5 的属性/原因码定义已存在但未实现
  - 没有 broker/server 实现（与 Description 不符）
  - 没有自动化测试文件
  - TLS/SSL（MQTTS scheme）支持在枚举中标记但实际实现可能不完整
  - 部分 delegate 绑定被注释掉（`MQTTClientObject.cpp` 中 InitDelegates 方法体为空）
- **是否推荐使用**：适合原型开发和非关键场景。生产环境需要自行验证稳定性，因为它是实验性 plugin 且无测试覆盖。如果有成熟的第三方 MQTT 库需求，可以考虑社区插件作为替代。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Protocols/MQTT)
- 官方文档（无）
