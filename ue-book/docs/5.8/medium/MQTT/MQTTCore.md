# MQTT

> MQTT broker and client

| 属性 | 值 |
|---|---|
| 中文名 | 物联网通信 |
| 分类 | IOT |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MQTTCore` (Runtime), `MQTTCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT) | |

## 用途

该插件为 Unreal Engine 提供了 MQTT v3.1.1 协议的完整客户端实现，用于与 MQTT Broker（消息代理服务器）进行双向通信。MQTT 是物联网（IoT）领域最广泛使用的轻量级消息传输协议，特别适合带宽有限、网络不稳定的场景。

插件实现了：
- **完整的 MQTT v3.1.1 协议栈**：包括 Connect、Publish、Subscribe、Unsubscribe、Ping、Disconnect 等所有标准报文类型
- **多级服务质量（QoS 0/1/2）**：支持"至多一次"、"至少一次"、"恰好一次"三种投递保证
- **异步操作模型**：所有网络操作基于 `TFuture`/`TPromise`，不阻塞游戏线程
- **线程安全的连接管理**：通过 `FRunnable` 在独立线程处理 Socket I/O 和报文解析
- **蓝图友好的封装**：提供 `UMQTTClientObject` 和 `UMQTTSubsystem`，蓝图可直接创建客户端、订阅主题、发布消息

> ⚠️ 代码中存在 MQTT v5 的部分枚举定义（如 `EMQTTReasonCode`、`FMQTT5Property`），但协议实现仅支持 v3.1.1。

## 使用场景

- 你需要从 IoT 传感器（温度、湿度、运动检测等）实时接收数据 → 用 MQTT Subscribe
- 你需要向智能设备发送控制指令（开灯、调节温度等） → 用 MQTT Publish
- 你在做一个数字孪生项目，需要与物理世界的设备保持双向通信 → 用 MQTT Client
- 你需要将游戏内的事件发送到外部系统（如监控面板、数据分析平台） → 用 MQTT Publish
- 你需要与 Home Assistant、Mosquitto 等 MQTT Broker 交互 → 直接连接

## 蓝图用法

### 核心节点

#### 子系统（创建客户端）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Client (From Project URL)` | 使用项目配置的默认 URL 创建/获取 MQTT 客户端 | `UMQTTSubsystem` |
| `Create Client (From URL)` | 使用指定 URL 创建/获取 MQTT 客户端 | `UMQTTSubsystem` |
| `Get Payload String` | 将客户端消息的 Payload 转为字符串 | `UMQTTSubsystem` |
| `Get Payload Json` | 将客户端消息的 Payload 解析为 JSON 对象 | `UMQTTSubsystem` |

#### 客户端操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect` | 连接到 MQTT Broker，连接结果通过委托回调 | `UMQTTClientObject` |
| `Disconnect` | 断开与 Broker 的连接 | `UMQTTClientObject` |
| `Publish` | 向指定主题发布消息（支持 QoS 和 Retain 标志） | `UMQTTClientObject` |
| `Subscribe` | 订阅单个主题，返回订阅对象用于监听消息 | `UMQTTClientObject` |
| `Subscribe (Multiple Topics)` | 一次性订阅多个主题 | `UMQTTClientObject` |
| `Unsubscribe` | 取消订阅指定主题 | `UMQTTClientObject` |
| `Get Client Id` | 获取客户端唯一标识 | `UMQTTClientObject` |
| `Get URL` | 获取客户端连接的 Broker URL | `UMQTTClientObject` |

#### 订阅对象

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set On Message Handler` | 设置消息到达时的回调委托 | `UMQTTSubscriptionObject` |
| `Is Valid` | 检查订阅是否仍然有效 | `UMQTTSubscriptionObject` |

### 使用示例（蓝图描述）

**建立连接并订阅主题：**

1. 调用 `Create Client (From URL)` 节点，传入 Broker 地址（如 `FMQTTURL("broker.hivemq.com", 1883)`），获取 `UMQTTClientObject`
2. 调用 `Connect` 节点，绑定 `OnConnect` 委托处理连接结果
3. 在 `OnConnect` 回调中，检查 `ReturnCode == Accepted` 后，调用 `Subscribe` 节点订阅 `"sensor/temperature"` 主题
4. 对返回的 `UMQTTSubscriptionObject` 调用 `Set On Message Handler`，绑定消息处理委托

**发布消息：**

1. 在已连接的客户端上，调用 `Publish` 节点
2. 填入 Topic（如 `"device/light/set"`）、Payload（`TArray<uint8>`）、QoS（默认 Once）
3. 无需等待回调，QoS 0 为即发即忘；QoS 1/2 会自动处理确认

## C++ 用法

### 头文件引入

```cpp
#include "MQTTClientObject.h"    // 蓝图友好的客户端封装
#include "MQTTSubsystem.h"       // 引擎子系统
#include "MQTTShared.h"          // URL、Topic、QoS 等共享类型
#include "MQTTClientMessage.h"   // 消息结构
#include "IMQTTClient.h"         // C++ 客户端接口
#include "IMQTTCoreModule.h"     // 模块接口
```

### 基本用法

通过模块接口创建客户端并连接：

```cpp
// 获取 MQTT 模块接口
IMQTTCoreModule& MQTTModule = IMQTTCoreModule::Get();

// 使用默认 URL 创建客户端
TSharedPtr<IMQTTClient, ESPMode::ThreadSafe> Client = MQTTModule.GetOrCreateClient();

// 或使用自定义 URL 创建客户端
FMQTTURL URL(TEXT("broker.hivemq.com"), 1883);
TSharedPtr<IMQTTClient, ESPMode::ThreadSafe> Client2 = MQTTModule.GetOrCreateClient(URL);

// 连接到 Broker（Clean Session = true）
Client->Connect(true).Next([Client](EMQTTConnectReturnCode ReturnCode)
{
    if (ReturnCode == EMQTTConnectReturnCode::Accepted)
    {
        UE_LOG(LogTemp, Log, TEXT("MQTT 连接成功，Client ID: %s"), *Client->GetClientId().ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MQTT 连接失败: %d"), static_cast<uint8>(ReturnCode));
    }
});

// 发布消息
TArray<uint8> Payload;
FString Message = TEXT("{\"temperature\": 23.5}");
Payload.Append(reinterpret_cast<const uint8*>(TCHAR_TO_UTF8(*Message)), Message.Len());

Client->Publish(TEXT("sensor/temperature"), Payload, EMQTTQualityOfService::AtLeastOnce)
    .Next([](bool bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("发布结果: %s"), bSuccess ? TEXT("成功") : TEXT("失败"));
    });

// 断开连接
Client->Disconnect();
```

### 进阶用法

使用带消息回调的 Subscribe 模板方法：

```cpp
// 订阅主题并绑定消息处理 Lambda
Client->Subscribe(TEXT("sensor/#"),
    [](const FMQTTClientMessage& Message)
    {
        // 解析消息内容
        FString PayloadStr = Message.GetPayloadAsString();
        UE_LOG(LogTemp, Log, TEXT("收到消息 - 主题: %s, 内容: %s, QoS: %d"),
            *Message.Topic, *PayloadStr, static_cast<uint8>(Message.QoS));
    },
    EMQTTQualityOfService::AtLeastOnce
).Next([](const FMQTTSubscribeResult& Result)
{
    if (Result.ReturnCode == EMQTTSubscribeReturnCode::Failure)
    {
        UE_LOG(LogTemp, Error, TEXT("订阅失败"));
        return;
    }
    UE_LOG(LogTemp, Log, TEXT("订阅成功，授予 QoS: %d"),
        static_cast<uint8>(Result.Subscription->GetGrantedQoS()));
});

// 批量订阅多个主题
TArray<TPair<FString, EMQTTQualityOfService>> Topics;
Topics.Add(MakeTuple(TEXT("sensor/temperature"), EMQTTQualityOfService::AtLeastOnce));
Topics.Add(MakeTuple(TEXT("sensor/humidity"), EMQTTQualityOfService::Once));
Topics.Add(MakeTuple(TEXT("actuator/#"), EMQTTQualityOfService::ExactlyOnce));

Client->Subscribe(Topics).Next([](const TArray<FMQTTSubscribeResult>& Results)
{
    for (const auto& Result : Results)
    {
        UE_LOG(LogTemp, Log, TEXT("订阅主题: %s, 返回码: %d, 授予QoS: %d"),
            *Result.Subscription->GetTopic().ToString(),
            static_cast<uint8>(Result.ReturnCode),
            static_cast<uint8>(Result.Subscription->GetGrantedQoS()));
    }
});

// 取消订阅
TSet<FString> UnsubTopics;
UnsubTopics.Add(TEXT("sensor/humidity"));
Client->Unsubscribe(UnsubTopics);

// 心跳检测（2 秒超时）
Client->Ping(2.0f).Next([](bool bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Ping 结果: %s"), bSuccess ? TEXT("正常") : TEXT("超时"));
});

// 监听全局消息事件
Client->OnMessage().AddLambda([](const FMQTTClientMessage& Message)
{
    // 处理所有未被 Subscription 独占处理的消息
});
```

使用蓝图封装对象（适合蓝图/C++ 混合项目）：

```cpp
// 通过子系统创建蓝图客户端
UMQTTSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMQTTSubsystem>();
FMQTTURL URL(TEXT("localhost"), 1883, TEXT("user"), TEXT("pass"));
UMQTTClientObject* ClientObj = Subsystem->GetOrCreateClient(this, URL);

// 使用委托连接
UMQTTClientObject::FOnConnectDelegate OnConnect;
OnConnect.BindLambda([](EMQTTConnectReturnCode ReturnCode)
{
    UE_LOG(LogTemp, Log, TEXT("连接结果: %d"), static_cast<uint8>(ReturnCode));
});
ClientObj->Connect(OnConnect);

// 发布消息
TArray<uint8> Payload;
FString Msg = TEXT("{\"state\": \"on\"}");
Payload.Append(reinterpret_cast<const uint8*>(TCHAR_TO_UTF8(*Msg)), Msg.Len());
ClientObj->Publish(TEXT("device/light"), Payload, EMQTTQualityOfService::Once, false);
```

## Demo 示例

**MyMQTTComponent.h**

```cpp
// MyMQTTComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "MQTTClientMessage.h"
#include "MyMQTTComponent.generated.h"

class IMQTTClient;

UCLASS(ClassGroup=(MQTT), meta=(BlueprintSpawnableComponent))
class UMyMQTTComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMQTTComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "MQTT")
    FString BrokerHost = TEXT("localhost");

    UPROPERTY(EditAnywhere, Category = "MQTT")
    int32 BrokerPort = 1883;

    UPROPERTY(EditAnywhere, Category = "MQTT")
    FString SubscribeTopic = TEXT("sensor/#");

    UPROPERTY(BlueprintAssignable, Category = "MQTT")
    FSimpleMulticastDelegate OnConnected;

    UFUNCTION(BlueprintCallable, Category = "MQTT")
    void PublishMessage(const FString& Topic, const FString& Message);

private:
    void HandleConnect(EMQTTConnectReturnCode ReturnCode);
    void HandleMessage(const FMQTTClientMessage& Message);

    TSharedPtr<IMQTTClient, ESPMode::ThreadSafe> MqttClient;
};
```

**MyMQTTComponent.cpp**

```cpp
// MyMQTTComponent.cpp
#include "MyMQTTComponent.h"
#include "IMQTTCoreModule.h"
#include "MQTTShared.h"
#include "MQTTClientMessage.h"

UMyMQTTComponent::UMyMQTTComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyMQTTComponent::BeginPlay()
{
    Super::BeginPlay();

    // 创建 MQTT 客户端
    FMQTTURL URL(BrokerHost, BrokerPort);
    MqttClient = IMQTTCoreModule::Get().GetOrCreateClient(URL);

    if (!MqttClient.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("无法创建 MQTT 客户端"));
        return;
    }

    // 监听连接事件
    MqttClient->OnConnect().AddUObject(this, &UMyMQTTComponent::HandleConnect);

    // 连接到 Broker
    MqttClient->Connect(true);
}

void UMyMQTTComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MqttClient.IsValid())
    {
        MqttClient->Disconnect();
        MqttClient.Reset();
    }

    Super::EndPlay(EndPlayReason);
}

void UMyMQTTComponent::HandleConnect(EMQTTConnectReturnCode ReturnCode)
{
    if (ReturnCode != EMQTTConnectReturnCode::Accepted)
    {
        UE_LOG(LogTemp, Error, TEXT("MQTT 连接失败: %d"), static_cast<uint8>(ReturnCode));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("MQTT 已连接"));

    // 连接成功后订阅主题
    MqttClient->Subscribe(SubscribeTopic,
        [this](const FMQTTClientMessage& Message) { HandleMessage(Message); },
        EMQTTQualityOfService::AtLeastOnce
    ).Next([this](const FMQTTSubscribeResult& Result)
    {
        if (Result.ReturnCode != EMQTTSubscribeReturnCode::Failure)
        {
            UE_LOG(LogTemp, Log, TEXT("已订阅: %s"), *SubscribeTopic);
            OnConnected.Broadcast();
        }
    });
}

void UMyMQTTComponent::HandleMessage(const FMQTTClientMessage& Message)
{
    UE_LOG(LogTemp, Log, TEXT("[%s] %s"),
        *Message.Topic, *Message.GetPayloadAsString());
}

void UMyMQTTComponent::PublishMessage(const FString& Topic, const FString& Message)
{
    if (!MqttClient.IsValid() || !MqttClient->IsConnected())
    {
        UE_LOG(LogTemp, Warning, TEXT("MQTT 未连接，无法发布"));
        return;
    }

    MqttClient->Publish(Topic, Message, EMQTTQualityOfService::Once);
}
```

## 模块依赖

从源码分析，使用该插件需要以下非标准模块依赖：

| 模块 | 用途 |
|---|---|
| `Sockets` | TCP Socket 通信（FSocket, FInternetAddr） |
| `Networking` | 网络地址解析（ISocketSubsystem） |
| `Json` | JSON 负载解析（FJsonObject） |
| `JsonUtilities` | JSON 工具封装（FJsonObjectWrapper） |

插件级别依赖：`JsonBlueprintUtilities`（已通过 .uplugin 声明自动启用）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-01-30 | `52a87df` | Fixed a crash that occurred when receiving MQTT packets with payloads =128 bytes due to incorrect va | 修复接收 128 字节负载的 MQTT 报文时导致的崩溃 |
| 2025-06-11 | `afdf8d7` | Replace some usages of FORCEINLINE with inline in Online modules. | 将部分 FORCEINLINE 替换为 inline（跨模块兼容性修复） |
| 2025-05-09 | `163c5cc` | [MQTT] Removed platform restrictions | 移除平台限制，使插件可在更多平台上使用 |
| 2025-02-13 | `ec3fb59` | Replaced `IsValid(this)` under the rest of Engine/. | 修复 IsValid(this) 调用方式（全局重构） |

### 维护评价

该插件创建于 2022 年 8 月，至今约 4 年。从提交记录看：

- **仍处于实验阶段**：`.uplugin` 标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，需要手动启用
- **维护频率较低**：最近一年仅有 3 次提交，且多为编译修复和重构，无实质性功能更新
- **存在已知限制**：仅实现 MQTT v3.1.1，v5 仅有枚举定义；2026 年 1 月的崩溃修复暗示报文解析可能存在更多边界问题
- **协议实现基本完整**：覆盖了 Connect/Publish/Subscribe/Unsubscribe/Ping/Disconnect 全流程，支持 QoS 0/1/2

**⚠️ 警告**：该插件仍标记为实验性，不建议在生产环境中使用。适合作为原型验证或内部工具使用。如果需要生产级 MQTT 支持，建议评估第三方方案（如 [UnrealCLR](https://github.com/nxrighthere/UnrealCLR) 或通过 WebSocket 桥接）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [MQTT v3.1.1 规范](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)（协议参考）
- [MQTT Core 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT/Source/MQTTCore)
- [MQTT Core Editor 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT/Source/MQTTCoreEditor)