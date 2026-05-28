# MQTT

> MQTT broker and client

| 属性 | 值 |
|---|---|
| 中文名 | 物联网通信协议 |
| 分类 | IOT |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MQTTCore` (Runtime), `MQTTCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-08 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT) | |

## 用途

MQTT 插件为 Unreal Engine 提供了完整的 MQTT 协议客户端和服务器实现。MQTT 是一种轻量级的、基于发布/订阅模式的消息传输协议，专为低带宽、高延迟或不可靠的网络环境（如物联网 IoT 场景）而设计。该插件让 UE 项目能够与任何符合标准的 MQTT 代理（Broker）进行通信，实现数据双向传输，是连接虚幻引擎与外部硬件设备、传感器网络或云服务的理想桥梁。

## 使用场景

*   **物联网设备集成**：你的游戏或应用需要实时读取物理传感器（如温度、湿度、GPS）的数据，或控制 LED 灯、电机等执行器。
*   **外部服务通信**：你需要与运行在其他设备或云上的服务（如 Node-RED、AWS IoT Core、Azure IoT Hub）进行简单的消息交换。
*   **设备监控与调试**：在游戏中实时监控和调试连接的物联网设备状态，或发送控制指令。
*   **简单的客户端/服务器原型**：快速搭建一个基于消息的、解耦的通信架构原型，用于验证想法。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Client (From Project URL)` | 使用项目设置中配置的默认URL创建或获取一个MQTT客户端。 | `UMQTTSubsystem` |
| `Create Client (From URL)` | 使用指定的URL创建或获取一个MQTT客户端。 | `UMQTTSubsystem` |
| `Connect` | 连接到MQTT代理服务器。 | `UMQTTClientObject` |
| `Disconnect` | 从MQTT代理服务器断开连接。 | `UMQTTClientObject` |
| `Publish` | 向指定的MQTT主题发布一条消息。 | `UMQTTClientObject` |
| `Subscribe` | 订阅一个或多个MQTT主题，并返回订阅对象。 | `UMQTTClientObject` |
| `Subscribe (Multiple Topics)` | 批量订阅多个MQTT主题。 | `UMQTTClientObject` |
| `Unsubscribe` | 取消订阅指定的MQTT主题。 | `UMQTTClientObject` |
| `Get Payload String` | 将MQTT消息的载荷（Payload）转换为字符串。 | `UMQTTSubsystem` |
| `Get Payload Json` | 将MQTT消息的载荷（Payload）解析为JSON对象。 | `UMQTTSubsystem` |

### 使用示例（蓝图描述）

1.  **创建客户端**：使用 `Create Client (From Project URL)` 节点获取一个持久化的客户端实例，或者使用 `Create Client (From URL)` 节点指定服务器地址创建新实例。
2.  **连接与订阅**：调用客户端的 `Connect` 节点，在成功回调后，使用 `Subscribe` 节点订阅感兴趣的主题（如 “sensors/temperature”），并绑定一个委托（Delegate）来接收消息。
3.  **发布消息**：调用 `Publish` 节点，指定主题（如 “actuators/light”）和载荷数据（如 `“ON”` 的字节数组），向该主题发布控制指令。
4.  **处理消息**：在订阅时绑定的回调函数中，可以通过 `Get Payload String` 或 `Get Payload Json` 节点，将接收到的 `FMQTTClientMessage` 载荷转换为蓝图可用的字符串或JSON对象进行处理。
5.  **断开连接**：游戏结束或需要时，调用 `Disconnect` 节点断开与代理服务器的连接。

## C++ 用法

### 头文件引入

```cpp
#include "MQTTClientObject.h"
#include "MQTTSubsystem.h"
#include "MQTTShared.h"
#include "MQTTClientMessage.h"
```

### 基本用法

以下代码展示了如何在C++中创建客户端、连接、订阅和发布消息。
*来源文件: `Public/MQTTClientObject.h`, `Public/MQTTSubsystem.h`*

```cpp
// 获取MQTT子系统
UMQTTSubsystem* MQTTSubsystem = GEngine->GetEngineSubsystem<UMQTTSubsystem>();

// 创建或获取一个客户端对象
FMQTTURL BrokerURL(TEXT("broker.example.com"), 1883, TEXT("user"), TEXT("password"));
UMQTTClientObject* Client = MQTTSubsystem->GetOrCreateClient(this, BrokerURL);

// 连接到代理
Client->Connect(FUMQTTClientObject::FOnConnectDelegate::CreateLambda([](EMQTTConnectReturnCode ReturnCode){
    if(ReturnCode == EMQTTConnectReturnCode::Accepted){
        UE_LOG(LogTemp, Log, TEXT("MQTT Connected Successfully!"));
    }
}));

// 订阅主题
UMQTTSubscriptionObject* Sub = Client->Subscribe(TEXT("sensors/#"), EMQTTQualityOfService::AtLeastOnce);
if(Sub){
    Sub->SetOnMessageHandler(FUMQTTSubscriptionObject::FOnMessageDelegate::CreateLambda([](const FMQTTClientMessage& Message){
        UE_LOG(LogTemp, Log, TEXT("Received on %s: %s"), *Message.Topic, *Message.GetPayloadAsString());
    }));
}

// 发布消息
TArray<uint8> Payload = {(uint8)'O', (uint8)'N'};
Client->Publish(TEXT("actuators/light"), Payload, EMQTTQualityOfService::Once, false);
```

### 进阶用法

使用 `IMQTTClient` 接口进行更底层的控制，例如直接使用 Future 模式和自定义订阅回调。
*来源文件: `Public/IMQTTClient.h`, `Private/MQTTClient.h`*

```cpp
// 直接通过模块接口获取底层客户端（C++底层使用）
IMQTTCoreModule& MQTTModule = IMQTTCoreModule::Get();
TSharedPtr<IMQTTClient, ESPMode::ThreadSafe> LowLevelClient = MQTTModule.GetOrCreateClient(FMQTTURL(TEXT("broker.example.com")));

// 使用Future模式进行连接
TFuture<EMQTTConnectReturnCode> ConnectFuture = LowLevelClient->Connect();
ConnectFuture.Next([](const EMQTTConnectReturnCode& Result){
    // 在连接完成的线程上执行
    UE_LOG(LogTemp, Log, TEXT("Connection result: %d"), static_cast<int32>(Result));
});

// 使用模板Subscribe直接绑定Lambda
LowLevelClient->Subscribe(
    TEXT("events/important"),
    [](const FMQTTClientMessage& Message){
        // 处理接收到的消息
    },
    EMQTTQualityOfService::ExactlyOnce
);

// 获取客户端状态
bool bIsConnected = LowLevelClient->IsConnected();
FGuid ClientId = LowLevelClient->GetClientId();
```

## Demo 示例

一个完整的最小示例，展示如何在 Actor 中使用 MQTT 客户端。
*来源文件: `Public/MQTTClientObject.h`, `Public/MQTTSubsystem.h`*

**MQTTDemoActor.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MQTTDemoActor.generated.h"

class UMQTTClientObject;
class UMQTTSubscriptionObject;

UCLASS()
class AMQTTDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION()
	void OnMQTTConnect(EMQTTConnectReturnCode ReturnCode);
	
	UFUNCTION()
	void OnMQTTMessage(const FMQTTClientMessage& Message);

private:
	UPROPERTY()
	TObjectPtr<UMQTTClientObject> MQTTClient;

	UPROPERTY()
	TObjectPtr<UMQTTSubscriptionObject> SensorSubscription;
};
```

**MQTTDemoActor.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MQTTDemoActor.h"
#include "MQTTSubsystem.h"
#include "MQTTClientObject.h"

void AMQTTDemoActor::BeginPlay()
{
	Super::BeginPlay();

	// 获取MQTT子系统并创建客户端
	UMQTTSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMQTTSubsystem>();
	if(Subsystem)
	{
		// 使用本地主机的默认端口
		FMQTTURL URL(TEXT("localhost"));
		MQTTClient = Subsystem->GetOrCreateClient(this, URL);

		if(MQTTClient)
		{
			// 绑定连接成功回调
			UMQTTClientObject::FOnConnectDelegate ConnectDelegate;
			ConnectDelegate.BindDynamic(this, &AMQTTDemoActor::OnMQTTConnect);
			MQTTClient->Connect(ConnectDelegate);
		}
	}
}

void AMQTTDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if(MQTTClient)
	{
		// 清理订阅和断开连接
		MQTTClient->Disconnect(UMQTTClientObject::FOnDisconnectDelegate());
		MQTTClient = nullptr;
		SensorSubscription = nullptr;
	}
	Super::EndPlay(EndPlayReason);
}

void AMQTTDemoActor::OnMQTTConnect(EMQTTConnectReturnCode ReturnCode)
{
	if(ReturnCode == EMQTTConnectReturnCode::Accepted && MQTTClient)
	{
		// 订阅传感器数据主题
		SensorSubscription = MQTTClient->Subscribe(TEXT("home/sensors/+"), EMQTTQualityOfService::AtLeastOnce);
		if(SensorSubscription)
		{
			UMQTTSubscriptionObject::FOnMessageDelegate MessageDelegate;
			MessageDelegate.BindDynamic(this, &AMQTTDemoActor::OnMQTTMessage);
			SensorSubscription->SetOnMessageHandler(MessageDelegate);
		}
	}
}

void AMQTTDemoActor::OnMQTTMessage(const FMQTTClientMessage& Message)
{
	// 将消息载荷转换为字符串
	UMQTTSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMQTTSubsystem>();
	if(Subsystem)
	{
		FString PayloadStr = Subsystem->GetPayloadString(Message);
		UE_LOG(LogTemp, Log, TEXT("MQTT [%s]: %s"), *Message.Topic, *PayloadStr);
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `JsonBlueprintUtilities` | 用于在蓝图中处理JSON数据，对应 `Get Payload Json` 节点 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新版的 `UE_LOGF`，属于代码维护和现代化更新。 |
| 2026-01-30 | `52a87df5` | Fixed a crash that occurred when receiving MQTT packets with payloads =128 bytes due to incorrect va | 修复了一个因变量长度解析错误导致接收特定长度(128字节)载荷数据包时崩溃的bug。 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 在在线相关模块中将一些 `FORCEINLINE` 用法替换为 `inline`，属于编译器优化调整。 |
| 2025-05-09 | `163c5cc4` | [MQTT] Removed platform restrictions | 移除了MQTT插件原先的平台限制，使其可在更多平台上使用。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 在引擎其他部分替换 `IsValid(this)` 用法，属于代码清理和规范统一。 |

### 维护评价

该插件创建于 **2022年8月**，至今约3年。从提交历史看，维护活动持续到 **2026年4月**，最近的一次提交是日志系统的现代化迁移，并且期间包含关键的Bug修复（如特定载荷长度崩溃问题）和平台兼容性改进。

**综合评价**：
*   **状态**：**实验性 (Experimental)**，但**持续维护中**。
*   **建议**：对于新项目或原型开发，可以尝试使用。由于是实验性功能，不建议直接用于需要极高稳定性的核心生产环节。它提供了一个完整的MQTT协议栈实现，是UE内嵌物联网通信能力的优秀起点。在使用时需注意其API可能在后续版本中发生变化。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
*   测试用例：暂无独立测试目录，测试代码可能嵌入在模块内部或引擎测试框架中。