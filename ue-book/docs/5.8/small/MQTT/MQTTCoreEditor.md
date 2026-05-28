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

MQTT 是一种轻量级的 IoT（物联网）消息传输协议，采用发布/订阅模式在设备之间传递消息。本插件为 Unreal Engine 提供了内置的 MQTT Broker（代理服务器）和 Client（客户端）实现，使引擎能够直接接入 IoT 生态系统。

该插件解决的核心问题是：让 UE5 应用程序能够无需外部依赖即可连接、订阅和发布 MQTT 消息，典型用途包括与 IoT 传感器、智能家居设备、工业控制器等进行实时双向通信。插件内部依赖 `JsonBlueprintUtilities` 进行 JSON 数据的序列化/反序列化，方便以结构化格式交换消息载荷。

**注意**：此插件当前标记为**实验性**（`IsExperimentalVersion=true`）且**默认不启用**（`EnabledByDefault=false`），API 可能会在未来版本中发生变化。

## 使用场景

- 你正在开发一个数字孪生应用，需要实时读取工厂 IoT 传感器数据 → 使用 MQTT 客户端订阅传感器 Topic
- 你需要在 UE5 场景中实时控制智能家居设备（灯光、温度等）→ 通过 MQTT 客户端发布控制指令
- 你想要在 UE5 中构建一个内嵌的 MQTT Broker，让多个外部设备直接连接 → 使用 MQTT Broker 功能
- 你需要将 UE5 中的模拟数据推送到 IoT 平台（如 AWS IoT、Azure IoT Hub）→ 通过 MQTT 发布消息
- 你在做汽车 HMI 或工业 HMI 项目，设备间通信基于 MQTT 协议 → 直接集成本插件

## 蓝图用法

由于本插件当前标记为实验性且提供的源码分析仅覆盖了 `MQTTCoreEditor`（编辑器辅助模块），核心运行时模块 `MQTTCore` 的详细蓝图 API 需要参阅源码中的 `Public/` 头文件。基于插件的整体架构，可预期的核心功能分组如下：

### 核心功能分组

| 功能 | 说明 |
|---|---|
| **Broker 管理** | 启动、停止内嵌 MQTT Broker，配置监听端口和连接参数 |
| **Client 连接** | 创建 MQTT 客户端实例，连接到外部 Broker（支持 TCP/TLS） |
| **订阅与发布** | 订阅 Topic 并接收消息、向指定 Topic 发布消息 |
| **消息处理** | 处理接收到的 MQTT 消息，支持 QoS 等级配置 |
| **JSON 载荷** | 结合 JsonBlueprintUtilities 进行消息载荷的 JSON 序列化 |

> **提示**：使用前需在项目的 `.uproject` 文件或编辑器插件设置中手动启用此插件（`EnabledByDefault=false`）。

### 使用示例（蓝图描述）

典型的蓝图工作流程：

1. **创建客户端**：实例化 MQTT 客户端对象，配置 Broker 地址、端口、Client ID
2. **连接 Broker**：调用连接函数，设置连接/断开的回调事件
3. **订阅 Topic**：连接成功后，调用 Subscribe 并指定 Topic 字符串和 QoS 等级
4. **接收消息**：在消息回调事件中处理收到的 Payload（可使用 JSON 工具解析）
5. **发布消息**：调用 Publish 函数向指定 Topic 发送 Payload
6. **断开连接**：不再需要时调用断开连接并释放资源

## C++ 用法

### 头文件引入

```cpp
// MQTTCore 运行时模块
#include "MQTTCore.h"

// MQTTCoreEditor 编辑器模块（仅在编辑器环境下使用）
#include "IMQTTCoreEditorModule.h"
```

### 基本用法

由于提供的源码分析主要覆盖了编辑器辅助模块，以下展示了编辑器模块的基本访问方式。MQTT 核心功能（Broker/Client API）位于 `MQTTCore` 运行时模块中，需参考该模块的 `Public/` 头文件获取完整 API。

```cpp
// 检查 MQTTCoreEditor 模块是否已加载
if (FModuleManager::Get().IsModuleLoaded("MQTTCoreEditor"))
{
    IMQTTCoreEditorModuleInterface& EditorModule = 
        FModuleManager::GetModuleChecked<IMQTTCoreEditorModuleInterface>("MQTTCoreEditor");
    // 使用编辑器扩展功能...
}
```

### 模块日志

插件内部定义了专用日志类别，可用于调试：

```cpp
// 使用 MQTT 日志类别（定义在 MQTTCore 模块中）
UE_LOG(LogMQTT, Log, TEXT("MQTT connection established to broker"));

// MQTTCoreEditor 模块的日志类别
UE_LOG(LogMQTTCoreEditor, Verbose, TEXT("Editor module initialized"));
```

### 统计计数器

`MQTTCoreEditor` 模块注册了统计组，可在控制台中通过 `stat MQTTCoreEditor` 查看编辑器侧性能数据。

## Demo 示例

以下是一个最小化的 MQTT 客户端使用示例（基于插件架构推断）：

### MyMQTTActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMQTTActor.generated.h"

UCLASS()
class AMyMQTTActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMQTTActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 连接到 MQTT Broker */
    UFUNCTION(BlueprintCallable, Category = "MQTT")
    void ConnectToBroker(const FString& Host, int32 Port, const FString& ClientId);

    /** 发布消息到指定 Topic */
    UFUNCTION(BlueprintCallable, Category = "MQTT")
    void PublishMessage(const FString& Topic, const FString& Payload);

    /** 订阅指定 Topic */
    UFUNCTION(BlueprintCallable, Category = "MQTT")
    void SubscribeTopic(const FString& Topic);

private:
    /** Broker 连接地址 */
    UPROPERTY(EditAnywhere, Category = "MQTT")
    FString BrokerHost = TEXT("localhost");

    /** Broker 端口 */
    UPROPERTY(EditAnywhere, Category = "MQTT")
    int32 BrokerPort = 1883;
};
```

### MyMQTTActor.cpp

```cpp
#include "MyMQTTActor.h"
#include "MQTTCore.h" // MQTTCore 运行时模块

AMyMQTTActor::AMyMQTTActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMQTTActor::BeginPlay()
{
    Super::BeginPlay();

    // 自动连接到配置的 Broker
    ConnectToBroker(BrokerHost, BrokerPort, TEXT("UE5_Client_01"));
}

void AMyMQTTActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理 MQTT 连接
    Super::EndPlay(EndPlayReason);
}

void AMyMQTTActor::ConnectToBroker(const FString& Host, int32 Port, const FString& ClientId)
{
    // 根据 MQTTCore 模块提供的 API 建立连接
    // 具体 API 参见 MQTTCore/Public/ 下的头文件
    UE_LOG(LogTemp, Log, TEXT("Connecting to MQTT Broker at %s:%d with ID: %s"), 
        *Host, Port, *ClientId);
}

void AMyMQTTActor::PublishMessage(const FString& Topic, const FString& Payload)
{
    UE_LOG(LogTemp, Log, TEXT("Publishing to [%s]: %s"), *Topic, *Payload);
}

void AMyMQTTActor::SubscribeTopic(const FString& Topic)
{
    UE_LOG(LogTemp, Log, TEXT("Subscribing to topic: %s"), *Topic);
}
```

> **注意**：以上示例为基于插件架构的框架代码，具体的 Broker/Client API 调用方法需要参考 `MQTTCore` 模块 `Public/` 目录下的实际头文件声明。

## 模块依赖

从 Build.cs 分析，本插件具有以下依赖关系：

| 模块 | 用途 |
|---|---|
| `JsonBlueprintUtilities` | JSON 数据处理（插件级依赖，用于 MQTT 消息载荷的序列化） |

无特殊模块依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新的 UE_LOGF 格式 |
| 2026-01-30 | `52a87df5` | Fixed a crash that occurred when receiving MQTT packets with payloads =128 bytes due to incorrect va | 修复接收 128 字节载荷的 MQTT 数据包时的崩溃问题 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 将部分 FORCEINLINE 替换为 inline，代码规范调整 |
| 2025-05-09 | `163c5cc4` | [MQTT] Removed platform restrictions | 移除平台限制，扩展跨平台支持 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 替换 IsValid(this) 调用，引擎范围代码规范修复 |

### 维护评价

- **创建时间**：2022 年 8 月，约 4 年前由 Epic Games 工程师引入（关联 Jira UE-155100）
- **更新频率**：持续有更新，最近一次为 2026 年 4 月，维护频率约为每 2-3 个月一次
- **维护状态**：**活跃维护中** — 近一年内有实质性 bug 修复（128 字节载荷崩溃修复）和平台扩展
- **实验性状态**：该插件仍标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明 Epic 尚未将其视为稳定 API
- **已知风险**：
  - 实验性标记意味着 API 可能在未来版本中发生变化或被移除
  - 默认不启用，需要手动在项目设置中开启
  - 最近修复的 128 字节载荷崩溃说明底层协议实现仍在迭代中

**推荐程度**：⚠️ 谨慎使用。适合 IoT 原型开发和内部项目，但不建议在需要长期稳定性的生产环境中依赖此插件。若用于生产环境，建议密切关注引擎版本更新中的变更日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [官方文档]()（暂无）