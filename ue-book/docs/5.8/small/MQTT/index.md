# MQTT

> MQTT broker and client（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 物联网协议 |
| 分类 | IOT |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MQTTCore` (Runtime), `MQTTCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT) | |

## 用途

该插件为 Unreal Engine 提供了完整的 MQTT 协议实现，包括 Broker（代理服务器）和 Client（客户端）功能。它解决了在游戏或实时应用中集成物联网 (IoT) 设备通信、实现进程间消息发布/订阅以及连接外部 MQTT 服务的需求。不同于简单的网络消息，MQTT 协议专为低带宽、高延迟或不稳定的网络环境设计，非常适合用于控制物理设备、同步多客户端状态或接收传感器数据等场景。

## 使用场景

*   你需要在游戏内实时接收来自 IoT 传感器（如温度、湿度、运动传感器）的数据，并根据数据改变游戏世界状态。
*   你需要为多人游戏或模拟应用构建一个轻量级、基于主题的消息总线，实现解耦的客户端间通信。
*   你需要将游戏客户端与外部的 MQTT Broker（如 Mosquitto, HiveMQ）连接，发布游戏事件或订阅外部控制指令。
*   你需要在编辑器工具或运行时服务中内嵌一个简单的 MQTT Broker，用于本地调试或小规模部署。

## 蓝图用法

（基于插件结构与常见 MQTT 操作推断的核心功能节点）

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect` | 连接到指定的 MQTT Broker | `UMQTTClient` |
| `Disconnect` | 断开与 Broker 的连接 | `UMQTTClient` |
| `Subscribe` | 订阅一个或多个主题 | `UMQTTClient` |
| `Unsubscribe` | 取消订阅一个或多个主题 | `UMQTTClient` |
| `Publish` | 向指定主题发布消息 | `UMQTTClient` |
| `OnMessageReceived` | 当订阅的主题收到消息时的委托 | `UMQTTClient` |

### 使用示例（蓝图描述）

1.  **连接与订阅**：在 BeginPlay 事件中，首先使用 `Connect` 节点连接到指定的 Broker 地址和端口。连接成功后，立即调用 `Subscribe` 节点订阅你关心的主题（如 `"game/control/#"`）。
2.  **处理消息**：绑定 `OnMessageReceived` 委托到一个自定义事件。在该事件中，你可以解析传入的消息主题和负载（Payload），并根据内容执行游戏逻辑。
3.  **发布消息**：当游戏内发生特定事件（如玩家得分），使用 `Publish` 节点将事件信息（如 `{"player": "A", "score": 100}`）发布到一个主题（如 `"game/events"`）。

## C++ 用法

### 头文件引入

```cpp
#include "MQTTClient.h"
```

### 基本用法

```cpp
// 创建客户端并连接
UMQTTClient* Client = NewObject<UMQTTClient>(this);
Client->Connect(TEXT("broker.example.com"), 1883);

// 订阅主题
Client->Subscribe(TEXT("my/topic"), EMQTTQualityOfService::AtLeastOnce);

// 绑定消息回调
Client->OnMessageReceived.AddDynamic(this, &AMyActor::HandleMQTTMessage);

// 发布消息
Client->Publish(TEXT("my/topic"), TEXT("{\"key\":\"value\"}"), EMQTTQualityOfService::AtLeastOnce, false);
```

### 进阶用法

```cpp
// 实现自定义认证（需参考 UMQTTClient 的相关属性）
Client->SetCredentials(TEXT("username"), TEXT("password"));

// 设置遗嘱消息（LWT），当客户端异常断开时由 Broker 发布
Client->SetLastWillMessage(TEXT("status/offline"), TEXT("Client disconnected unexpectedly"), EMQTTQualityOfService::AtLeastOnce, true);

// 使用自定义连接选项
FMQTTConnectionOptions Options;
Options.bCleanSession = false;
Options.KeepAliveInterval = 60;
Client->ConnectWithOptions(TEXT("broker.example.com"), 1883, Options);
```

## Demo 示例

```cpp
// MyMQTTActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MQTTClient.h"
#include "MyMQTTActor.generated.h"

UCLASS()
class AMyMQTTActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMQTTActor();

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void HandleMQTTMessage(const FMQTTMessage& Message);

private:
    UPROPERTY()
    UMQTTClient* MQTTClient;
};

// MyMQTTActor.cpp
#include "MyMQTTActor.h"

AMyMQTTActor::AMyMQTTActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMQTTActor::BeginPlay()
{
    Super::BeginPlay();

    MQTTClient = NewObject<UMQTTClient>(this);
    // 连接到公共测试 Broker
    MQTTClient->Connect(TEXT("test.mosquitto.org"), 1883);
    // 订阅测试主题
    MQTTClient->Subscribe(TEXT("ue5/mqtt/test"), EMQTTQualityOfService::AtMostOnce);
    // 绑定回调
    MQTTClient->OnMessageReceived.AddDynamic(this, &AMyMQTTActor::HandleMQTTMessage);
    // 发布一条测试消息
    MQTTClient->Publish(TEXT("ue5/mqtt/test"), TEXT("Hello from UE5!"), EMQTTQualityOfService::AtMostOnce, false);
}

void AMyMQTTActor::HandleMQTTMessage(const FMQTTMessage& Message)
{
    UE_LOG(LogTemp, Log, TEXT("Received on topic '%s': %s"), *Message.Topic, *Message.Payload);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `JsonBlueprintUtilities` | 用于在蓝图中方便地序列化与反序列化 JSON 数据（MQTT 负载的常用格式） |
| `MQTTCore` | （使用者必须依赖）提供了 MQTT 协议的核心运行时功能和客户端 API |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2026-01-30 | `52a87df5` | Fixed a crash that occurred when receiving MQTT packets with payloads =128 bytes due to incorrect va | 修复了接收特定长度（128字节）MQTT数据包时因长度计算错误导致的崩溃。 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 在在线模块中，将部分 FORCEINLINE 用法替换为标准的 inline。 |
| 2025-05-09 | `163c5cc4` | [MQTT] Removed platform restrictions | 移除了 MQTT 模块对特定平台的限制，提高了跨平台兼容性。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 在引擎范围内，将 `IsValid(this)` 调用替换为更规范的检查。 |

### 维护评价

*   **活跃维护**：该插件创建于2022年，截至2026年仍有规律的提交，最近一次更新（2026年4月）是例行代码维护。在2025-2026年间有多次针对稳定性（修复崩溃）、兼容性（移除平台限制）和代码质量的改进，表明该插件处于积极维护状态。
*   **实验性状态**：`.uplugin` 明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着该插件API可能不稳定，功能尚未最终确定，不建议在正式生产项目中未经充分测试就直接使用。它更适合作为原型开发、内部工具或研究学习用途。
*   **推荐度**：对于需要MQTT协议且能接受其“实验性”标签和潜在API变更的开发者（如IoT游戏原型、技术Demo），这是一个直接来自Epic的官方实现，值得考虑。对于追求稳定性的生产项目，建议观望或评估第三方成熟插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT/Tests) （如果存在）