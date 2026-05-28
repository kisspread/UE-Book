# TCP Messaging

> Adds a TCP connection based transport layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 中文名 | TCP 消息传输 |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `TcpMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-19 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Messaging/TcpMessaging) | |

## 用途

本插件为 UE 的消息总线（Message Bus）子系统提供基于 TCP 协议的传输层实现。UE 的消息总线默认使用 UDP 广播进行节点发现和消息传递，但在某些场景下 UDP 不可靠或不可用（如跨子网、防火墙限制、需要可靠传输等），此时需要 TCP 作为替代传输层。

本插件并非通用游戏网络插件，而是专为 UE **工具程序**（UnrealFrontend、UnrealInsights、UnrealPak）设计的。它解决了这些工具之间在不同机器上进行可靠消息通信的需求，例如 Unreal Insights 从远程机器收集性能分析数据时就需要稳定的连接。

## 使用场景

- **Unreal Insights 远程分析**：从另一台机器的 UnrealPak 或游戏实例收集性能数据
- **Unreal Frontend 多设备管理**：在编辑器前端中管理远程设备上的构建和部署任务
- **跨子网工具通信**：当 UDP 广播无法跨越网络边界时，使用 TCP 点对点连接
- **需要可靠消息传递**：确保消息不丢失、不乱序的场景

## 蓝图用法

本插件没有暴露任何蓝图接口。它是一个纯 Runtime 模块，仅支持通过 C++ 和配置文件使用，且限定为特定工具程序（UnrealFrontend、UnrealInsights、UnrealPak）。

## C++ 用法

### 头文件引入

```cpp
#include "ITcpMessagingModule.h"
```

### 基本用法

通过模块接口动态添加/移除 TCP 连接：

```cpp
// 获取 TcpMessaging 模块实例
ITcpMessagingModule* TcpMessaging = FModuleManager::GetModulePtr<ITcpMessagingModule>("TcpMessaging");
if (TcpMessaging)
{
    // 添加到远程节点的出站连接（格式：IP:端口）
    TcpMessaging->AddOutgoingConnection(TEXT("192.168.1.100:1987"));

    // 移除不再需要的连接
    TcpMessaging->RemoveOutgoingConnection(TEXT("192.168.1.100:1987"));
}
```

来源：`Source/TcpMessaging/Public/ITcpMessagingModule.h`

### 通过配置文件使用

更常见的方式是通过 `Engine.ini` 配置文件，无需编写代码：

```ini
[/Script/TcpMessaging.TcpMessagingSettings]
EnableTransport=true
ListenEndpoint=0.0.0.0:1987
+ConnectToEndpoints=192.168.1.100:1987
+ConnectToEndpoints=10.0.0.50:1987
ConnectionRetryDelay=5
ConnectionRetryPeriod=30
```

来源：`Source/TcpMessaging/Private/Settings/TcpMessagingSettings.h`

### 进阶用法

本插件使用的消息协议内部细节（供理解源码参考）：

```cpp
// 协议魔数，用于握手识别
#define TCP_MESSAGING_TRANSPORT_PROTOCOL_MAGIC 0x45504943  // ASCII "EPIC"

// 协议版本，支持向后兼容
namespace ETcpMessagingVersion
{
    enum Type
    {
        Initial,
        ChangedMessageLengthToInt32,
        ChangedMessageContext,
        LatestVersion = ChangedMessageContext,
        OldestSupportedVersion = ChangedMessageLengthToInt32
    };
}

// 缓冲区大小常量
#define TCP_MESSAGING_SEND_BUFFER_SIZE    (2 * 1024 * 1024)  // 2MB
#define TCP_MESSAGING_RECEIVE_BUFFER_SIZE (2 * 1024 * 1024)  // 2MB
#define TCP_MESSAGING_MAX_ANNOTATIONS     128
#define TCP_MESSAGING_MAX_RECIPIENTS      1024
```

## Demo 示例

一个最小的使用示例——通过 TCP 消息传输在两个节点之间建立连接：

```cpp
// MyTcpMessagingExample.h
#pragma once

#include "CoreMinimal.h"

class FMyTcpMessagingExample
{
public:
    /** 初始化并添加 TCP 连接 */
    static void Init();

    /** 清理并移除 TCP 连接 */
    static void Shutdown();

private:
    static FString ConnectionEndpoint;
};
```

```cpp
// MyTcpMessagingExample.cpp
#include "MyTcpMessagingExample.h"
#include "ITcpMessagingModule.h"
#include "Modules/ModuleManager.h"

FString FMyTcpMessagingExample::ConnectionEndpoint = TEXT("127.0.0.1:1987");

void FMyTcpMessagingExample::Init()
{
    ITcpMessagingModule* TcpMessaging = FModuleManager::GetModulePtr<ITcpMessagingModule>("TcpMessaging");
    if (TcpMessaging)
    {
        // 建立到目标地址的 TCP 消息连接
        TcpMessaging->AddOutgoingConnection(ConnectionEndpoint);
        UE_LOG(LogTemp, Log, TEXT("TCP Messaging: 连接到 %s"), *ConnectionEndpoint);
    }
}

void FMyTcpMessagingExample::Shutdown()
{
    ITcpMessagingModule* TcpMessaging = FModuleManager::GetModulePtr<ITcpMessagingModule>("TcpMessaging");
    if (TcpMessaging)
    {
        // 移除连接
        TcpMessaging->RemoveOutgoingConnection(ConnectionEndpoint);
        UE_LOG(LogTemp, Log, TEXT("TCP Messaging: 断开连接 %s"), *ConnectionEndpoint);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等，以及 Messaging、Sockets、Networking 模块）。

## 配置参数

本插件通过 `UTcpMessagingSettings` 提供以下可配置参数（可在 `Engine.ini` 中设置）：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `EnableTransport` | bool | — | 是否启用 TCP 传输通道 |
| `ListenEndpoint` | FString | — | 监听地址，格式 `IP:端口`，留空则禁用监听 |
| `ConnectToEndpoints` | TArray\<FString\> | — | 要连接的远程端点列表，格式 `IP:端口` |
| `ConnectionRetryDelay` | int32 | — | 断开后重连前的延迟时间（秒），0 禁用重连 |
| `ConnectionRetryPeriod` | int32 | — | 重连尝试的持续时间（秒），0 表示仅重试一次 |
| `bStopServiceWhenAppDeactivates` | bool | true | 应用失焦时是否停止传输服务 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2025-10-17 | `1e874547` | Remove EStructSerializerBackendFlags::Legacy | 移除废弃的序列化标志 |
| 2025-05-21 | `9a46e4c4` | UnrealPak references TcpMessaging module | UnrealPak 添加对本模块的引用依赖 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理 5.2 版本废弃的头文件包含顺序兼容代码 |
| 2024-04-04 | `a8878bd1` | [Insights] Enable Session Frontend in Insights Session Browser | 在 Insights 会话浏览器中启用 Session Frontend |

### 维护评价

**稳定维护中**。本插件自 2016 年创建以来，功能上已趋于成熟稳定。近期的提交均为编译迁移（`UE_LOG` → `UE_LOGF`）、废弃代码清理和跨模块依赖更新，没有功能性变更。最近一次实质性功能相关改动是 2024 年为 Unreal Insights 启用会话前端。

该插件作为 Unreal 工具链（Insights、Frontend、Pak）的基础设施组件，虽然不常更新，但持续保持与引擎版本的兼容性。对于需要在工具程序之间进行 TCP 消息通信的场景，本插件是唯一选择且完全可用。

**推荐使用**：如果你在使用 Unreal Insights、Unreal Frontend 等工具并需要跨机器通信，本插件已默认启用且稳定可靠。普通游戏项目通常不需要直接使用本插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Messaging/TcpMessaging)
- [ITcpMessagingModule 接口](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Messaging/TcpMessaging/Public/ITcpMessagingModule.h)
- [配置类](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Messaging/TcpMessaging/Private/Settings/TcpMessagingSettings.h)