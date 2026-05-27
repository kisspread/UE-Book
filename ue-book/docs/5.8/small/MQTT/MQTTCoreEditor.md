# MQTT

> MQTT broker and client

| 属性 | 值 |
|---|---|
| 中文名 | 消息队列遥测传输 |
| 分类 | IOT |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MQTTCore` (Runtime), `MQTTCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT) | |

## 用途
该插件为 Unreal Engine 提供了 MQTT 协议的客户端和 Broker（代理服务器）实现。MQTT 是一种轻量级的、基于发布/订阅模式的消息传输协议，专为物联网 (IoT)、移动应用和低带宽、高延迟或不可靠的网络环境设计。此插件使 UE5 项目能够与其他 MQTT 设备或服务进行通信，实现状态同步、数据上报、远程控制等功能。

## 使用场景
- 你需要在游戏中实时接收来自 IoT 传感器（如温度、湿度、运动传感器）的数据。
- 你正在开发一个智能家居或智能建筑模拟器，需要与真实的智能设备（如灯、空调）进行交互。
- 你需要将游戏中的事件（如玩家操作、游戏状态变化）发布到 MQTT Broker，供其他应用（如仪表盘、监控系统）订阅和消费。
- 你需要在多个 UE 应用实例之间，通过一个中心 Broker 进行轻量级的状态同步。
- 你希望快速原型化或测试基于 MQTT 的通信逻辑。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Client` | 创建并返回一个 MQTT 客户端实例。 | `UMQTTClient` |
| `Connect` | 连接到指定的 MQTT Broker。 | `UMQTTClient` |
| `Subscribe` | 订阅一个或多个主题，并设置回调函数来处理收到的消息。 | `UMQTTClient` |
| `Publish` | 向指定主题发布一条消息。 | `UMQTTClient` |
| `Unsubscribe` | 取消订阅一个或多个主题。 | `UMQTTClient` |
| `Disconnect` | 断开与 Broker 的连接。 | `UMQTTClient` |
| `On Message Received` | 当订阅的主题收到新消息时触发的回调委托。 | `UMQTTClient` |

### 使用示例（蓝图描述）
1.  **创建并连接**：在蓝图中，使用 `Create Client` 节点创建一个客户端对象。然后，调用其 `Connect` 函数，填入 Broker 的地址（Host）和端口（Port）。可以为 `On Connected` 和 `On Connection Failure` 绑定事件以处理连接结果。
2.  **订阅主题**：连接成功后，使用 `Subscribe` 函数，填入想要监听的主题字符串（如 `home/sensor/temperature`）。为 `On Message Received` 事件创建一个自定义事件，该事件会接收 `Payload`（负载数据）等参数。
3.  **发布消息**：当需要发送数据时，使用 `Publish` 函数，填入目标主题和要发送的消息负载（通常是 JSON 格式的字符串）。
4.  **断开连接**：在不再需要时，调用 `Disconnect` 函数。

## C++ 用法

### 头文件引入
```cpp
#include “MQTTCore.h”
```

### 基本用法
基于典型的 MQTT 客户端使用模式。

```cpp
// 假设在某个 Actor 或 Subsystem 中
#include “MQTTClient.h” // 具体类名需根据源码确认

void AMQTTExampleActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建客户端实例
    MQTTClient = NewObject<UMQTTClient>(this);

    // 绑定连接状态回调
    MQTTClient->OnConnected.AddDynamic(this, &AMQTTExampleActor::HandleConnected);
    MQTTClient->OnConnectionError.AddDynamic(this, &AMQTTExampleActor::HandleConnectionError);

    // 发起连接
    MQTTClient->Connect(“broker.example.com”, 1883);
}

void AMQTTExampleActor::HandleConnected()
{
    UE_LOG(LogTemp, Log, TEXT(“MQTT 连接成功”));

    // 订阅主题
    MQTTClient->Subscribe(“game/player/status”);

    // 绑定消息接收回调
    MQTTClient->OnMessageReceived.AddDynamic(this, &AMQTTExampleActor::HandleMessage);
}

void AMQTTExampleActor::HandleMessage(const FString& Topic, const FString& Payload)
{
    UE_LOG(LogTemp, Log, TEXT(“收到来自 %s 的消息: %s”), *Topic, *Payload);
    // 在这里解析 Payload（如 JSON）并执行游戏逻辑
}
```

### 进阶用法
结合 JSON 序列化/反序列化处理结构化数据。

```cpp
// 发送一个包含 JSON 数据的消息
void AMQTTExampleActor::SendPlayerUpdate(int32 Score, const FVector& Location)
{
    // 创建 JSON 对象
    TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject);
    JsonObject->SetNumberField(TEXT(“score”), Score);
    JsonObject->SetStringField(TEXT(“location”), Location.ToString());

    // 序列化为字符串
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);

    // 发布消息
    if (MQTTClient && MQTTClient->IsConnected())
    {
        MQTTClient->Publish(“game/player/update”, OutputString);
    }
}
```

## Demo 示例

```cpp
// MQTTDemoActor.h
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “MQTTClient.h”
#include “MQTTDemoActor.generated.h”

UCLASS()
class AMQTTDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMQTTDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void OnMQTTConnected();

    UFUNCTION()
    void OnMQTTMessageReceived(const FString& Topic, const FString& Payload);

    UFUNCTION()
    void OnMQTTConnectionError(const FString& ErrorMessage);

private:
    UPROPERTY()
    TObjectPtr<UMQTTClient> MQTTClient;

    void PublishHeartbeat();
};
```

```cpp
// MQTTDemoActor.cpp
#include “MQTTDemoActor.h”
#include “JsonObjectConverter.h”

AMQTTDemoActor::AMQTTDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMQTTDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建并配置客户端
    MQTTClient = NewObject<UMQTTClient>(this);
    MQTTClient->OnConnected.AddDynamic(this, &AMQTTDemoActor::OnMQTTConnected);
    MQTTClient->OnConnectionError.AddDynamic(this, &AMQTTDemoActor::OnMQTTConnectionError);
    MQTTClient->OnMessageReceived.AddDynamic(this, &AMQTTDemoActor::OnMQTTMessageReceived);

    // 连接到公共测试 Broker
    MQTTClient->Connect(“test.mosquitto.org”, 1883);
}

void AMQTTDemoActor::OnMQTTConnected()
{
    UE_LOG(LogTemp, Warning, TEXT(“MQTTDemo: 连接成功！”));

    // 订阅一个测试主题
    MQTTClient->Subscribe(“ue5/mqtt/demo/request”);

    // 发布一条初始消息
    PublishHeartbeat();
}

void AMQTTDemoActor::OnMQTTMessageReceived(const FString& Topic, const FString& Payload)
{
    UE_LOG(LogTemp, Warning, TEXT(“MQTTDemo 收到消息 [%s]: %s”), *Topic, *Payload);
    // 可以在这里回复一个 pong
    MQTTClient->Publish(“ue5/mqtt/demo/response”, “Pong from UE5！”);
}

void AMQTTDemoActor::OnMQTTConnectionError(const FString& ErrorMessage)
{
    UE_LOG(LogTemp, Error, TEXT(“MQTTDemo 连接失败: %s”), *ErrorMessage);
}

void AMQTTDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MQTTClient && MQTTClient->IsConnected())
    {
        MQTTClient->Disconnect();
    }
    Super::EndPlay(EndPlayReason);
}

void AMQTTDemoActor::PublishHeartbeat()
{
    TSharedPtr<FJsonObject> Heartbeat = MakeShareable(new FJsonObject);
    Heartbeat->SetStringField(TEXT(“actor”), GetName());
    Heartbeat->SetNumberField(TEXT(“timestamp”), FPlatformTime::Seconds());

    FString HeartbeatJson;
    FJsonObjectConverter::JsonObjectToUStruct(Heartbeat.ToSharedRef(), &HeartbeatJson);
    MQTTClient->Publish(“ue5/mqtt/demo/heartbeat”, HeartbeatJson);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `JsonBlueprintUtilities` | 提供 JSON 与 UObject/UStruct 之间的序列化与反序列化功能，便于处理 MQTT 消息负载。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF 格式，属于维护性改进。 |
| 2026-01-30 | `52a87df5` | Fixed a crash that occurred when receiving MQTT packets with payloads >=128 bytes due to incorrect va | 修复了接收大于等于128字节负载的MQTT数据包时，因缓冲区计算错误导致的崩溃。 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 将部分 `FORCEINLINE` 替换为 `inline`，代码风格统一。 |
| 2025-05-09 | `163c5cc4` | [MQTT] Removed platform restrictions | 移除了 MQTT 模块的平台编译限制，使其能在所有平台上构建。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 替换了 `IsValid(this)` 的检查方式，属于引擎范围内的代码重构。 |

### 维护评价
该插件创建于 2022 年，约 4 年历史。从 git 历史看，**2025-2026 年期间仍有功能性更新和关键 bug 修复**（如修复大数据包崩溃），表明它目前仍处于**维护中**状态。插件被标记为 `IsExperimentalVersion` 且 `EnabledByDefault=false`，说明它尚未达到正式发布状态，API 和功能可能变动。它解决了 UE5 原生不支持的物联网通信需求，对于有明确 MQTT 通信需求的 IoT 项目或原型开发是**推荐使用**的，但需注意其“实验性”标签，并做好未来接口变更的准备。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT/Tests) (路径推断)