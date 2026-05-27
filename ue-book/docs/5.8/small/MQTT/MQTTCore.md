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

该插件为 Unreal Engine 5 提供了完整的 MQTT 客户端实现，旨在让开发者能够轻松地将 UE 应用程序连接到任何标准的 MQTT 代理（Broker），实现物联网（IoT）设备通信、实时数据同步、远程监控和控制等功能。它解决了在游戏引擎中集成轻量级、低延迟的发布/订阅消息传输协议的需求。

## 使用场景

- **物联网与智能家居**：你需要将 UE 项目（如数字孪生或可视化界面）连接到物联网设备（如传感器、开关），通过 MQTT 发布指令并订阅设备状态更新。
- **实时数据可视化**：从外部数据源（如金融市场数据、服务器状态）接收实时数据流，并在 UE 界面中动态展示。
- **多设备同步与控制**：在多人交互式体验或模拟训练系统中，使用 MQTT 作为中央消息总线，协调多个客户端之间的状态同步。
- **移动应用与后端通信**：在 UE 开发的移动应用中，使用 MQTT 与后端服务器进行高效、可靠的通信。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Client (From Project URL)` | 使用项目设置中配置的默认 URL 创建一个 MQTT 客户端实例。 | `UMQTTSubsystem` |
| `Create Client (From URL)` | 根据指定的 URL 结构体创建一个 MQTT 客户端实例。 | `UMQTTSubsystem` |
| `Connect` | 连接到 MQTT 代理服务器。可绑定 `OnConnect` 委托获取连接结果。 | `UMQTTClientObject` |
| `Disconnect` | 从 MQTT 代理服务器断开连接。 | `UMQTTClientObject` |
| `Publish` | 向指定的 Topic 发布消息。可设置 QoS 和 Retain 标志。 | `UMQTTClientObject` |
| `Subscribe` | 订阅单个 Topic。返回一个 `UMQTTSubscriptionObject`，用于绑定消息回调。 | `UMQTTClientObject` |
| `Subscribe (Multiple Topics)` | 同时订阅多个 Topic。返回订阅对象的数组。 | `UMQTTClientObject` |
| `Unsubscribe` | 取消订阅指定的 Topic。 | `UMQTTClientObject` |
| `Set On Message Handler` | 为一个订阅对象绑定消息接收回调函数。 | `UMQTTSubscriptionObject` |
| `Get Payload String` | 从接收到的消息 (`FMQTTClientMessage`) 中提取字符串格式的负载。 | `UMQTTSubsystem` |
| `Get Payload Json` | 将接收到的消息负载解析为 JSON 对象。 | `UMQTTSubsystem` |

### 使用示例（蓝图描述）

1.  **获取/创建客户端**：在需要通信的蓝图（例如 `GameMode` 或 `PlayerController`）中，使用 `Create Client (From Project URL)` 节点获取一个客户端实例。该节点基于项目设置中的 `UMQTTClientSettings` 配置。
2.  **连接服务器**：调用客户端的 `Connect` 节点。你可以将一个自定义事件（如 `On Connected`）绑定到 `OnConnect` 委托，以便在连接成功或失败后执行逻辑。
3.  **订阅主题**：连接成功后，使用 `Subscribe` 节点订阅你感兴趣的主题（如 `"home/temperature"`）。该节点返回一个 `MQTT Subscription` 对象。
4.  **处理收到的消息**：将返回的 `MQTT Subscription` 对象连接到一个 `Set On Message Handler` 节点。为该节点创建一个自定义事件（如 `On Temperature Update`），该事件会自动接收 `FMQTTClientMessage` 参数。在此事件中，使用 `Get Payload String` 或 `Get Payload Json` 提取数据并更新UI。
5.  **发布消息**：当需要发送指令时（如用户点击按钮），使用客户端的 `Publish` 节点，指定主题（如 `"home/lamp/control"`）和负载（如 `""` 或 JSON 字符串）。

## C++ 用法

### 头文件引入

```cpp
#include "MQTTClientObject.h"
#include "MQTTSubsystem.h"
#include "MQTTShared.h"
#include "MQTTClientMessage.h"
```

### 基本用法

通过子系统创建和管理 MQTT 客户端。

```cpp
// 在需要的地方（如 GameMode 初始化）获取 MQTT 子系统
UMQTTSubsystem* MQTTSubsystem = GEngine->GetEngineSubsystem<UMQTTSubsystem>();
if (MQTTSubsystem)
{
    // 使用项目设置中的默认 URL 创建客户端
    UMQTTClientObject* Client = MQTTSubsystem->GetOrCreateClient_WithProjectURL(this);
    
    // 或者，创建一个指向特定服务器的客户端
    FMQTTURL CustomURL;
    CustomURL.Host = TEXT("mqtt.example.com");
    CustomURL.Port = 1883;
    CustomURL.Username = TEXT("user");
    CustomURL.Password = TEXT("password");
    UMQTTClientObject* CustomClient = MQTTSubsystem->GetOrCreateClient(this, CustomURL);
}
```
**来源**：基于 `Public/MQTTSubsystem.h` 和 `Public/MQTTClientObject.h` 中的 `UFUNCTION` 推断。

### 进阶用法

在 C++ 中使用客户端接口进行异步连接、发布和订阅。

```cpp
// 假设你已经通过 UMQTTSubsystem 获取了一个 UMQTTClientObject* ClientObject

// 1. 定义回调
UMQTTClientObject::FOnConnectDelegate OnConnectDelegate;
OnConnectDelegate.BindDynamic(this, &AMyActor::OnMQTTConnect); // 绑定成员函数

// 2. 发起连接
ClientObject->Connect(OnConnectDelegate);

// 3. 连接成功回调中，进行订阅
void AMyActor::OnMQTTConnect(EMQTTConnectReturnCode ReturnCode)
{
    if (ReturnCode == EMQTTConnectReturnCode::Accepted)
    {
        UMQTTSubscriptionObject* Subscription = ClientObject->Subscribe("device/+/status");
        if (Subscription)
        {
            UMQTTSubscriptionObject::FOnMessageDelegate OnMsgDelegate;
            OnMsgDelegate.BindDynamic(this, &AMyActor::OnDeviceStatusMessage);
            Subscription->SetOnMessageHandler(OnMsgDelegate);
        }
    }
}

// 4. 收到消息回调
void AMyActor::OnDeviceStatusMessage(const FMQTTClientMessage& Message)
{
    // 使用内置方法解析 JSON 负载
    TSharedPtr<FJsonObject> JsonObject;
    if (Message.GetPayloadAsJson(JsonObject))
    {
        bool bIsOnline = JsonObject->GetBoolField("online");
        // ... 更新逻辑
    }
}
```
**来源**：基于 `Public/MQTTClientObject.h` 和 `Public/MQTTClientMessage.h` 中的类定义。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建客户端、连接并发布一条消息。

```cpp
// MyMQTTActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMQTTActor.generated.h"

class UMQTTClientObject;

UCLASS()
class AMyMQTTActor : public AActor
{
    GENERATED_BODY()
public:
    AMyMQTTActor();

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnConnected(EMQTTConnectReturnCode ReturnCode);

private:
    UPROPERTY()
    UMQTTClientObject* MQTTClient;
};

// MyMQTTActor.cpp
#include "MyMQTTActor.h"
#include "MQTTSubsystem.h"
#include "MQTTClientObject.h"

AMyMQTTActor::AMyMQTTActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMQTTActor::BeginPlay()
{
    Super::BeginPlay();

    UMQTTSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMQTTSubsystem>();
    if (Subsystem)
    {
        MQTTClient = Subsystem->GetOrCreateClient(this);
        if (MQTTClient)
        {
            UMQTTClientObject::FOnConnectDelegate ConnectDelegate;
            ConnectDelegate.BindDynamic(this, &AMyMQTTActor::OnConnected);
            MQTTClient->Connect(ConnectDelegate);
        }
    }
}

void AMyMQTTActor::OnConnected(EMQTTConnectReturnCode ReturnCode)
{
    if (ReturnCode == EMQTTConnectReturnCode::Accepted && MQTTClient)
    {
        // 发布一条测试消息
        const FString Payload = TEXT("{\"action\":\"test\", \"value\":42}");
        MQTTClient->Publish("ue5/test", TArray<uint8>((uint8*)*Payload, Payload.Len()));
        UE_LOG(LogTemp, Log, TEXT("MQTT: 发布测试消息成功。"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("MQTT: 连接失败，返回码: %s"), *UEnum::GetValueAsString(ReturnCode));
    }
}
```

## 模块依赖

要使用此插件的 `MQTTCore` 模块，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `JsonBlueprintUtilities` | 插件依赖项，用于处理 JSON 负载的解析和序列化（如 `GetPayloadJson` 功能）。 |

**无其他特殊依赖**（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，属于日志系统更新。 |
| 2026-01-30 | `52a87df5` | Fixed a crash that occurred when receiving MQTT packets with payloads =128 bytes due to incorrect va | 修复了因错误的数组大小导致接收特定负载大小（128字节）的MQTT包时发生的崩溃。 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 在在线相关模块中，将部分 `FORCEINLINE` 宏替换为 `inline` 关键字，属于代码风格/兼容性调整。 |
| 2025-05-09 | `163c5cc4` | [MQTT] Removed platform restrictions | 移除了 MQTT 模块的平台限制，使其能在更多平台上使用。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 在引擎其他部分替换了 `IsValid(this)` 的用法，属于引擎范围内的代码清理。 |

### 维护评价

**状态**：**维护中**。

- **创建时间**：约 4 年前，相对较新。
- **更新频率**：最近一次更新在 2026 年 4 月，之前也有间断性的更新（2025 年有多次）。
- **维护质量**：更新内容包括关键 Bug 修复（如崩溃修复）、平台兼容性改进和代码现代化（日志系统、内联关键字），表明仍在积极维护以保障稳定性和兼容性。
- **实验性警告**：插件本身标记为**实验性**（`IsExperimentalVersion=true`）且默认未启用。这意味着其 API 可能尚未完全稳定，未来版本可能有重大变更。
- **推荐度**：适用于当前 UE 5.x 版本的实验性项目或需要快速集成 MQTT 的原型开发。在生产环境中使用需谨慎，建议关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [官方文档](https://mqtt.org/) (MQTT 协议官方网站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT/Tests) (位于插件目录的 Tests 文件夹下)