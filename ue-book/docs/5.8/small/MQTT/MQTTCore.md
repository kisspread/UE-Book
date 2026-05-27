# MQTT

> MQTT broker and client

| 属性 | 值 |
|---|---|
| 中文名 | MQTT 协议 |
| 分类 | IOT |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MQTTCore` (Runtime), `MQTTCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT) | |

## 用途

该插件实现了完整的 MQTT v3.1.1 客户端协议，用于 UE5 项目与 MQTT Broker 之间的消息发布与订阅。MQTT 是物联网（IoT）领域最广泛使用的轻量级消息传输协议，适合在低带宽、高延迟的网络环境下进行设备间通信。

插件解决了以下核心问题：
- **异步 MQTT 连接管理**：基于 `FRunnable` 独立线程管理 socket 连接，不阻塞游戏线程
- **多级 QoS 支持**：完整实现 QoS 0（最多一次）、QoS 1（至少一次）、QoS 2（恰好一次）三种服务质量等级，涵盖完整的 MQTT 消息流（Publish → PUBACK/PUBREC/PUBREL/PUBCOMP）
- **蓝图友好的封装**：通过 `UMQTTClientObject` 和 `UMQTTSubsystem` 提供完整的蓝图 API，无需 C++ 即可使用
- **项目级配置**：通过 `UMQTTClientSettings`（Config 类）可在项目设置中配置默认 Broker URL

> **注意**：该插件默认未启用且标记为实验性，虽然已持续维护 4 年，但尚未正式发布。部分 MQTT v5 的枚举和属性定义已存在于头文件中，但协议实现仍为 v3.1.1。

## 使用场景

- 你需要将 UE5 应用连接到物联网设备（传感器、执行器等）→ 使用 MQTT 订阅设备状态、发布控制命令
- 你在做数字孪生或工业仿真，需要实时接收传感器数据流 → 用 MQTT 客户端订阅 Broker 上的主题
- 你需要将游戏或应用中的事件推送到外部监控系统 → 用 MQTT 发布消息到指定主题
- 你需要多客户端管理，每个客户端连接不同的 Broker → 通过 `UMQTTSubsystem` 按 URL 创建和复用客户端

## 蓝图用法

### 核心节点

**子系统（创建客户端）**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Client (From Project URL)` | 使用项目配置中的默认 URL 创建或获取 MQTT 客户端 | `UMQTTSubsystem` |
| `Create Client (From URL)` | 从指定 URL 创建或获取 MQTT 客户端，相同 URL 会复用已有客户端 | `UMQTTSubsystem` |
| `Get Payload String` | 将客户端消息的 payload 解码为字符串 | `UMQTTSubsystem` |
| `Get Payload Json` | 将客户端消息的 payload 解码为 JSON 对象 | `UMQTTSubsystem` |

**客户端对象**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect` | 连接到 Broker，通过回调返回连接结果码 | `UMQTTClientObject` |
| `Disconnect` | 断开连接 | `UMQTTClientObject` |
| `Publish` | 发布消息到指定主题，可设置 QoS 和 Retain 标志 | `UMQTTClientObject` |
| `Subscribe` | 订阅单个主题，返回订阅对象用于接收消息 | `UMQTTClientObject` |
| `Subscribe (Multiple Topics)` | 批量订阅多个主题 | `UMQTTClientObject` |
| `Unsubscribe` | 取消订阅指定主题 | `UMQTTClientObject` |
| `Get Client Id` | 获取客户端唯一标识 | `UMQTTClientObject` |
| `Get URL` | 获取客户端连接的 Broker URL | `UMQTTClientObject` |

**订阅对象**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set On Message Handler` | 设置消息到达回调 | `UMQTTSubscriptionObject` |
| `IsValid` | 检查订阅是否有效 | `UMQTTSubscriptionObject` |

### 使用示例（蓝图描述）

**基本发布/订阅流程：**

1. 在 BeginPlay 中，使用 **Create Client (From Project URL)** 节点获取一个 `UMQTTClientObject` 引用
2. 调用 **Connect** 节点，将返回的 **OnConnect** 委托连接到一个自定义事件
3. 在 OnConnect 回调中，检查 `ReturnCode` 是否为 `Accepted`（值为 0）
4. 连接成功后，调用 **Subscribe** 节点，传入主题字符串（如 `"sensors/temperature"`），获取 `UMQTTSubscriptionObject`
5. 在返回的订阅对象上调用 **Set On Message Handler**，将回调连接到自定义事件
6. 在自定义事件中，使用 **Get Payload String** 节点获取消息内容
7. 要发送消息时，调用 **Publish** 节点，传入主题和 payload（`TArray<uint8>`）

**多主题订阅：**

1. 准备一个 `TArray<FString>` 包含所有要订阅的主题
2. 准备一个 `TArray<EMQTTQualityOfService>` 包含每个主题对应的 QoS 等级
3. 调用 **Subscribe (Multiple Topics)** 节点
4. 对返回的每个 `UMQTTSubscriptionObject` 分别设置消息处理回调

## C++ 用法

### 头文件引入

```cpp
#include "MQTTClientObject.h"      // UMQTTClientObject, UMQTTSubscriptionObject
#include "MQTTSubsystem.h"         // UMQTTSubsystem
#include "IMQTTClient.h"           // IMQTTClient 接口
#include "IMQTTCoreModule.h"       // IMQTTCoreModule 模块接口
#include "MQTTShared.h"            // FMQTTURL, FMQTTTopic, FMQTTClientMessage 等
#include "MQTTClientSettings.h"    // UMQTTClientSettings
```

### 基本用法

通过模块接口获取 C++ 客户端并订阅消息（来源：`Public/IMQTTClient.h`、`Public/IMQTTCoreModule.h`）：

```cpp
// 获取模块接口，创建或复用客户端
FMQTTURL URL(TEXT("broker.example.com"), 1883, TEXT("user"), TEXT("pass"));
TSharedPtr<IMQTTClient, ESPMode::ThreadSafe> Client = 
    IMQTTCoreModule::Get().GetOrCreateClient(URL);

// 连接到 Broker
Client->Connect(/*bCleanSession=*/true).Next([](EMQTTConnectReturnCode ReturnCode)
{
    if (ReturnCode == EMQTTConnectReturnCode::Accepted)
    {
        UE_LOG(LogTemp, Log, TEXT("MQTT 连接成功"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MQTT 连接失败: %d"), static_cast<uint8>(ReturnCode));
    }
});

// 订阅主题并注册消息回调
Client->Subscribe(TEXT("sensors/#"), 
    [](const FMQTTClientMessage& Message)
    {
        UE_LOG(LogTemp, Log, TEXT("收到消息 [%s]: %s"), 
            *Message.Topic, *Message.GetPayloadAsString());
    },
    EMQTTQualityOfService::AtLeastOnce);

// 发布消息
TArray<uint8> Payload;
const FString Data = TEXT("{\"temperature\": 23.5}");
Payload.Append((uint8*)TCHAR_TO_UTF8(*Data), Data.Len());

Client->Publish(TEXT("sensors/temperature"), Payload, EMQTTQualityOfService::Once);
```

### 进阶用法

通过蓝图子系统管理多个客户端，并处理带 JSON payload 的消息（来源：`Public/MQTTSubsystem.h`、`Public/MQTTClientObject.h`、`Public/MQTTClientMessage.h`）：

```cpp
// 通过子系统创建蓝图兼容的客户端对象
UMQTTSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMQTTSubsystem>();

FMQTTURL URL;
URL.Host = TEXT("broker.example.com");
URL.Port = 1883;
URL.Username = TEXT("device01");
URL.Password = TEXT("secret");
URL.Scheme = EMQTTScheme::MQTTS; // 使用 TLS 加密

UMQTTClientObject* ClientObj = Subsystem->GetOrCreateClient(this, URL);

// 设置连接回调
UMQTTClientObject::FOnConnectDelegate OnConnect;
OnConnect.BindDynamic(this, &AMyActor::HandleConnect);
ClientObj->Connect(OnConnect);

// 订阅并设置消息处理
UMQTTSubscriptionObject* Sub = ClientObj->Subscribe(
    TEXT("devices/+/status"), EMQTTQualityOfService::AtLeastOnce);

UMQTTSubscriptionObject::FOnMessageDelegate OnMessage;
OnMessage.BindDynamic(this, &AMyActor::HandleMessage);
Sub->SetOnMessageHandler(OnMessage);

// 在消息处理函数中解析 JSON
void AMyActor::HandleMessage(const FMQTTClientMessage& Message)
{
    TSharedPtr<FJsonObject> Json;
    if (Message.GetPayloadAsJson(Json))
    {
        FString Status = Json->GetStringField(TEXT("status"));
        UE_LOG(LogTemp, Log, TEXT("设备状态: %s"), *Status);
    }
}

// 断开连接
ClientObj->Disconnect();
```

### 关键类型说明

| 类型 | 说明 |
|---|---|
| `FMQTTURL` | Broker 地址结构体，支持 `mqtt://` 和 `mqtts://` 协议 |
| `FMQTTTopic` | MQTT 主题路径，支持 `/` 分隔符 |
| `FMQTTTopicFilter` | 主题过滤器，支持 `+`（单级通配符）和 `#`（多级通配符） |
| `FMQTTClientMessage` | 收到的消息，包含 Topic、Payload（二进制）、QoS、Retain 标志 |
| `EMQTTQualityOfService` | QoS 等级：`Once`(0)、`AtLeastOnce`(1)、`ExactlyOnce`(2) |
| `EMQTTConnectReturnCode` | 连接结果码：`Accepted`、`RefusedProtocolVersion`、`RefusedNotAuthorized` 等 |
| `EMQTTScheme` | 连接协议：`MQTT`（明文，默认端口 1883）或 `MQTTS`（加密，默认端口 8883） |

## Demo 示例

### MyMQTTActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MQTTClientObject.h"
#include "MyMQTTActor.generated.h"

UCLASS()
class MYPROJECT_API AMyMQTTActor : public AActor
{
	GENERATED_BODY()

public:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION()
	void OnMqttConnected(EMQTTConnectReturnCode ReturnCode);

	UFUNCTION()
	void OnMqttMessage(const FMQTTClientMessage& Message);

	void PublishSensorData(float Temperature);

private:
	UPROPERTY()
	TObjectPtr<UMQTTClientObject> MQTTClient;

	UPROPERTY()
	TObjectPtr<UMQTTSubscriptionObject> MQTTSubscription;
};
```

### MyMQTTActor.cpp

```cpp
#include "MyMQTTActor.h"
#include "MQTTSubsystem.h"

void AMyMQTTActor::BeginPlay()
{
	Super::BeginPlay();

	// 通过子系统创建客户端
	UMQTTSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMQTTSubsystem>();

	FMQTTURL URL;
	URL.Host = TEXT("broker.example.com");
	URL.Port = 1883;

	MQTTClient = Subsystem->GetOrCreateClient(this, URL);
	if (!MQTTClient)
	{
		UE_LOG(LogTemp, Error, TEXT("无法创建 MQTT 客户端"));
		return;
	}

	// 连接
	UMQTTClientObject::FOnConnectDelegate OnConnect;
	OnConnect.BindDynamic(this, &AMyMQTTActor::OnMqttConnected);
	MQTTClient->Connect(OnConnect);
}

void AMyMQTTActor::OnMqttConnected(EMQTTConnectReturnCode ReturnCode)
{
	if (ReturnCode != EMQTTConnectReturnCode::Accepted)
	{
		UE_LOG(LogTemp, Error, TEXT("MQTT 连接失败: %d"), static_cast<uint8>(ReturnCode));
		return;
	}

	// 订阅控制主题
	MQTTSubscription = MQTTClient->Subscribe(
		TEXT("commands/mydevice"), EMQTTQualityOfService::AtLeastOnce);

	UMQTTSubscriptionObject::FOnMessageDelegate OnMessage;
	OnMessage.BindDynamic(this, &AMyMQTTActor::OnMqttMessage);
	MQTTSubscription->SetOnMessageHandler(OnMessage);

	UE_LOG(LogTemp, Log, TEXT("MQTT 已连接并订阅"));
}

void AMyMQTTActor::OnMqttMessage(const FMQTTClientMessage& Message)
{
	UE_LOG(LogTemp, Log, TEXT("收到 [%s]: %s"), *Message.Topic, *Message.GetPayloadAsString());
}

void AMyMQTTActor::PublishSensorData(float Temperature)
{
	if (!MQTTClient) return;

	const FString Json = FString::Printf(TEXT("{\"temp\":%.1f}"), Temperature);
	FTCHARToUTF8 Converter(*Json);
	TArray<uint8> Payload;
	Payload.Append((const uint8*)Converter.Get(), Converter.Length());

	MQTTClient->Publish(TEXT("sensors/temperature"), Payload, EMQTTQualityOfService::Once);
}

void AMyMQTTActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (MQTTClient)
	{
		MQTTClient->Disconnect();
	}

	Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sockets` | 底层 Socket 通信（FSocket、FInternetAddr） |
| `Json` | JSON 解析与序列化（FJsonObject） |

插件依赖：`JsonBlueprintUtilities`（用于蓝图 JSON 操作）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 统一将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-01-30 | `52a87df5` | Fixed a crash that occurred when receiving MQTT packets with payloads =128 bytes due to incorrect va | 修复接收 128 字节 payload 的 MQTT 数据包时的崩溃问题 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 将部分 FORCEINLINE 替换为 inline |
| 2025-05-09 | `163c5cc4` | [MQTT] Removed platform restrictions | 移除平台限制，支持更多平台 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 统一替换 IsValid(this) 调用 |

### 维护评价

- **仍为实验性**：插件创建于 2022 年 8 月，至今约 4 年仍标记为 `IsExperimentalVersion`，且 `EnabledByDefault=false`
- **持续维护**：最近一次更新在 2026 年 4 月，维护频率约每 2-4 个月一次，主要为 bug 修复和代码规范化
- **协议完成度**：MQTT v3.1.1 核心协议实现完整（Connect、Publish、Subscribe 及 QoS 0/1/2 完整消息流），MQTT v5 部分枚举已定义但未实现
- **已知问题**：2026 年 1 月修复了 128 字节 payload 的崩溃问题，说明协议序列化部分曾存在边界条件 bug
- **推荐程度**：适合原型开发和 IoT 项目评估，生产环境使用需充分测试。如果项目需要稳定的 MQTT 支持，建议评估第三方库（如 Mosquitto 绑定）作为替代方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [官方文档]()（无）