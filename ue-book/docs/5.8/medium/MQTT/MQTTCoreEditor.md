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
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT) | |

## 用途

该插件为 Unreal Engine 应用程序提供了对 MQTT 协议的原生支持。MQTT 是一种轻量级的消息发布/订阅传输协议，专为低带宽、高延迟或不可靠的网络环境设计，是物联网 (IoT) 领域通信的标准之一。该插件的核心功能是实现一个 MQTT **客户端**，允许 UE 应用程序连接到外部的 MQTT 代理 (Broker)，订阅感兴趣的消息主题，并向其他客户端发布消息。其目的是将 Unreal Engine 的强大可视化和逻辑能力与现实世界中的传感器、设备及其他软件服务通过 MQTT 协议无缝连接起来。

## 使用场景

- **智能家居/楼宇自动化可视化**：连接家庭中的温度、湿度、灯光、安防传感器，实时在 UE 中反映其状态。
- **工业监控与数字孪生**：从工厂设备（如 PLC、机器人）收集运行数据，在 UE 中构建对应的数字孪生体并进行实时监控。
- **实时数据仪表盘**：订阅来自数据库、Web 服务或其他分析系统通过 MQTT 推送的实时指标数据，并以 3D 或 2D UI 形式展示。
- **多机协同仿真**：在分布式仿真系统中，作为不同 UE 实例或其他软件间通信的轻量级总线。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MQTTClient` | 创建一个 MQTT 客户端组件实例。 | `UMQTTClientComponent` |
| `Connect` | 使用提供的服务器地址、端口和客户端 ID 连接到 MQTT 代理。 | `UMQTTClientComponent` |
| `Disconnect` | 断开与 MQTT 代理的连接。 | `UMQTTClientComponent` |
| `Subscribe` | 订阅一个或多个主题，并指定消息到达时的回调事件。 | `UMQTTClientComponent` |
| `Unsubscribe` | 取消对一个或多个主题的订阅。 | `UMQTTClientComponent` |
| `Publish` | 向指定主题发布一条消息，可以是纯文本或 JSON 格式。 | `UMQTTClientComponent` |

### 使用示例（蓝图描述）

1.  **创建并连接**：在 Actor 蓝图中，添加 `MQTT Client Component`。在 `BeginPlay` 事件中，调用 `Connect` 节点，输入 MQTT 代理的 IP 地址、端口（默认 1883）和一个唯一的客户端标识符。
2.  **订阅与接收**：创建一个自定义事件（如 `OnMessageReceived`），并将其连接到 `Subscribe` 节点的 `Event` 引脚。在 `Topic` 引脚输入如 `home/temperature` 的主题。当该主题有消息时，`OnMessageReceived` 会被触发，消息内容（Payload）将以字符串形式传入。
3.  **处理与发布**：在 `OnMessageReceived` 事件内，可以解析收到的消息（例如使用 `Parse JSON` 节点），然后调用 `Publish` 节点，向另一个主题（如 `control/light`）发送控制指令。

## C++ 用法

### 头文件引入

```cpp
#include "MQTTClientComponent.h"
#include "MQTTClientInterface.h"
```

### 基本用法

以下代码展示了如何以编程方式创建并配置一个 MQTT 客户端。来源文件：`MQTTClientComponent.h`。

```cpp
// 在你的 Actor 头文件 (.h) 中声明组件
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MQTT")
UMQTTClientComponent* MQTTClient;

// 在你的 Actor 源文件 (.cpp) 中
// 1. 创建组件
MQTTClient = CreateDefaultSubobject<UMQTTClientComponent>(TEXT("MQTTClient"));

// 2. 在初始化后连接
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 绑定消息接收委托
    MQTTClient->OnMessageReceived.AddDynamic(this, &AMyActor::HandleMQTTMessage);

    // 连接到 Broker
    FText ErrorMsg;
    bool bSuccess = MQTTClient->Connect(
        TEXT("broker.example.com"), // 服务器地址
        1883,                       // 端口
        TEXT("UE5_Client_01"),       // 客户端ID
        ErrorMsg                    // 错误信息输出
    );

    if (bSuccess)
    {
        // 连接成功，订阅主题
        MQTTClient->Subscribe(TEXT("sensors/#"));
    }
}

// 3. 处理接收到的消息
UFUNCTION()
void AMyActor::HandleMQTTMessage(const FString& Topic, const FString& Message)
{
    UE_LOG(LogTemp, Log, TEXT("Received on [%s]: %s"), *Topic, *Message);
    // 在此处解析消息并更新游戏逻辑或UI
}
```

### 进阶用法

结合 `JsonBlueprintUtilities` 插件处理 JSON 消息，并实现自定义的代理（Delegate）来处理特定主题。

```cpp
// 定义一个更具体的委托
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTemperatureUpdate, float, Temperature);

UPROPERTY(BlueprintAssignable, Category = "MQTT|Events")
FOnTemperatureUpdate OnTemperatureUpdate;

// 在消息处理函数中
void AMyActor::HandleMQTTMessage(const FString& Topic, const FString& Message)
{
    if (Topic == TEXT("sensors/temperature"))
    {
        // 使用 JsonUtilities 解析消息
        TSharedPtr<FJsonObject> JsonObject;
        TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Message);
        if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
        {
            float TempValue = JsonObject->GetNumberField(TEXT("value"));
            OnTemperatureUpdate.Broadcast(TempValue);
        }
    }
}
```

## Demo 示例

一个完整的最小 Actor 示例，演示连接、订阅和发布。

**MyMQTTActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMQTTActor.generated.h"

class UMQTTClientComponent;

UCLASS()
class AMyMQTTActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMQTTActor();

protected:
    virtual void BeginPlay() override;

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MQTT")
    UMQTTClientComponent* MQTTClient;

    UFUNCTION()
    void OnMQTTMessage(const FString& Topic, const FString& Message);
};
```

**MyMQTTActor.cpp**
```cpp
#include "MyMQTTActor.h"
#include "MQTTClientComponent.h"

AMyMQTTActor::AMyMQTTActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MQTTClient = CreateDefaultSubobject<UMQTTClientComponent>(TEXT("MQTTClient"));
}

void AMyMQTTActor::BeginPlay()
{
    Super::BeginPlay();

    MQTTClient->OnMessageReceived.AddDynamic(this, &AMyMQTTActor::OnMQTTMessage);

    FText Error;
    if (MQTTClient->Connect(TEXT("broker.hivemq.com"), 1883, TEXT("UE5_MyActor"), Error))
    {
        MQTTClient->Subscribe(TEXT("ue5/demo/incoming"));
        // 发布一条上线消息
        MQTTClient->Publish(TEXT("ue5/demo/status"), TEXT("{\"status\": \"online\"}"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MQTT Connection Failed: %s"), *Error.ToString());
    }
}

void AMyMQTTActor::OnMQTTMessage(const FString& Topic, const FString& Message)
{
    UE_LOG(LogTemp, Log, TEXT("Topic: %s, Message: %s"), *Topic, *Message);
    // 将收到的消息转发发布到另一个主题
    MQTTClient->Publish(TEXT("ue5/demo/echo"), Message);
}
```

## 模块依赖

从 `MQTTCoreEditor.Build.cs` 分析，使用者通常无需直接依赖 Editor 模块。使用 `MQTTCore` 功能的依赖如下：

| 模块 | 用途 |
|---|---|
| `JsonUtilities` | 用于解析和生成 JSON 格式的 MQTT 消息载荷，是 `JsonBlueprintUtilities` 插件的底层依赖。 |
| `Networking` | 提供底层的网络套接字（Socket）支持，MQTT 通信协议实现的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 UE_LOG 迁移至新宏 UE_LOGF，以提升日志系统的安全性和一致性。 |
| 2026-01-30 | `52a87df5` | Fixed a crash that occurred when receiving MQTT packets with payloads =128 bytes due to incorrect va | 修复了接收载荷为 128 字节的 MQTT 包时因缓冲区大小计算错误导致的崩溃问题。 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 将部分 Online 模块（可能包含本插件）中的 FORCEINLINE 替换为 inline，改善编译兼容性。 |
| 2025-05-09 | `163c5cc4` | [MQTT] Removed platform restrictions | 移除了插件原先可能存在的平台编译限制，使其可在更多目标平台上使用。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 在整个 Engine 范围内替换 `IsValid(this)`，统一代码风格。 |

### 维护评价

该插件创建于 2022 年，目前仍标记为**实验性 (IsExperimentalVersion=true)** 且**默认未启用**。从 Git 历史看，它仍处于**活跃维护**中，最近一次更新（2026年）修复了一个可能导致崩溃的关键问题。过去一年内有多次相关提交，包括功能增强（平台限制移除）和代码现代化（日志迁移）。

**综合评价**：作为一个实验性插件，其核心 MQTT 客户端功能已基本稳定，并持续得到修复和优化。对于需要在 UE 项目中集成物联网数据的开发者来说，它是一个**值得尝试和评估**的现成方案。但鉴于其“实验性”标签，在生产环境中使用时应进行充分测试，并关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [官方文档]()（暂无公开文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Protocols/MQTT/Tests) (如果存在)