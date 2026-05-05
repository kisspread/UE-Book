# TCP Messaging

> Adds a TCP connection based transport layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | TcpMessaging (Runtime, PreDefault) |
| 创建时间 | 2016-07-19 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Messaging/TcpMessaging) | |

## 用途

TcpMessaging 为 UE5 的 **消息总线 (Message Bus)** 子系统提供基于 TCP 协议的传输层实现。

UE5 的 Messaging 系统是一套进程间/机器间的松耦合消息通信框架，它定义了 `IMessageTransport` 接口，不同的传输层可以插件式替换。TcpMessaging 就是其中一种传输实现——通过 TCP 连接在网络上的不同计算机和设备之间发送和接收消息。

与 UDP 版本的 Messaging 不同，TCP 提供**可靠的、有序的**消息传递，适合对消息丢失零容忍的场景。该 plugin 被限制在特定的工具程序（UnrealFrontend、UnrealInsights、UnrealPak）中使用，而非游戏运行时。

核心工作原理：
1. 模块启动时创建 `FTcpMessageTransport` 实例，配置监听端口和连接目标
2. 通过 `FMessageBridgeBuilder` 构建 `IMessageBridge`，将 TCP transport 注入消息总线
3. 运行一个独立线程 (`FRunnable`) 管理所有 TCP 连接的收发
4. 支持双向通信：既可作为服务端监听，也可作为客户端主动连接

## 使用场景

- **Unreal Insights 需要跨机器收集数据**：在远程设备上运行的游戏通过 TCP 将 Trace 数据发送到运行 Insights 的开发机
- **UnrealFrontend 管理远程设备**：前端工具通过 TCP 消息与远程设备上的 Agent 通信
- **UnrealPak 与其他工具通信**：打包工具通过消息总线与其他工具进程协调工作
- **自定义工具间的进程间通信**：如果你开发了自定义的 UE 工具程序，可以用 TCP Messaging 实现多机协作

> ⚠️ **注意**：该 plugin 的 `ProgramAllowList` 限制为 `UnrealFrontend`、`UnrealInsights`、`UnrealPak`。普通游戏项目**不会加载**此模块。游戏运行时使用需要添加 `-Messaging` 命令行参数。

## 蓝图用法

TcpMessaging **没有暴露任何蓝图接口**。它是一个纯 C++ 传输层实现，不包含 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。

配置通过编辑器的 **Project Settings → Plugins → TCP Messaging** 面板完成（编辑器环境下会自动注册设置面板）。

### 设置面板参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `EnableTransport` | bool | 是否启用 TCP 传输 |
| `ListenEndpoint` | string | 监听地址，格式 `IP:PORT`，留空则不监听 |
| `ConnectToEndpoints` | string[] | 要连接的远端地址列表，格式 `IP:PORT` |
| `ConnectionRetryDelay` | int32 | 断线重连延迟（秒），0 禁用重连 |
| `ConnectionRetryPeriod` | int32 | 重连尝试周期（秒），0 表示只重试一次 |
| `bStopServiceWhenAppDeactivates` | bool | 应用失活时停止服务（如 iOS 休眠） |

## C++ 用法

### 头文件引入

```cpp
#include "ITcpMessagingModule.h"
```

### 基本用法 — 动态添加/移除连接

通过模块接口可以在运行时动态管理出站连接：

```cpp
// 获取模块实例
ITcpMessagingModule* TcpMessaging = FModuleManager::GetModulePtr<ITcpMessagingModule>("TcpMessaging");

if (TcpMessaging)
{
    // 添加一个出站连接
    TcpMessaging->AddOutgoingConnection(TEXT("192.168.1.100:1988"));

    // 移除一个出站连接
    TcpMessaging->RemoveOutgoingConnection(TEXT("192.168.1.100:1988"));
}
```

来源：`Source/TcpMessaging/Public/ITcpMessagingModule.h` + `Source/TcpMessaging/Private/TcpMessagingModule.cpp`

### 控制台命令

模块注册了 `FSelfRegisteringExec`，可在控制台使用以下命令：

| 命令 | 说明 |
|---|---|
| `TCPMESSAGING STATUS` | 显示协议版本和 Message Bridge 状态 |
| `TCPMESSAGING RESTART` | 重启 Message Bridge |
| `TCPMESSAGING SHUTDOWN` | 关闭 Message Bridge |

### 命令行参数覆盖

配置可以通过命令行参数覆盖，优先级高于配置文件：

| 参数 | 说明 |
|---|---|
| `-Messaging` | 在游戏进程中启用消息传输（默认仅工具程序可用） |
| `-TcpMessagingListen=IP:PORT` | 覆盖监听端点 |
| `-TcpMessagingConnect=IP1:PORT1,IP2:PORT2` | 覆盖连接目标（逗号分隔） |

来源：`Source/TcpMessaging/Private/TcpMessagingModule.cpp` 中的 `SupportsNetworkedTransport()` 和 `UTcpMessagingSettings` 方法

## 内部架构

### 协议细节

- **Magic Number**: `0x45504943` (ASCII: "EPIC")
- **协议版本**: `ETcpMessagingVersion::LatestVersion` (当前为 2)
- **最老支持版本**: `ChangedMessageLengthToInt32` (版本 1)
- **Socket 缓冲区**: 发送 2MB / 接收 2MB
- **最大消息注解数**: 128
- **最大接收者数**: 1024

来源：`Source/TcpMessaging/Private/TcpMessagingPrivate.h`

### 连接状态机

每个 `FTcpMessageTransportConnection` 有以下状态：

| 状态 | 说明 |
|---|---|
| `STATE_Connecting` | 正在连接，尚未获得远端 NodeId |
| `STATE_Connected` | 已连接，NodeId 有效 |
| `STATE_DisconnectReconnectPending` | 已断开，等待重连 |
| `STATE_Disconnected` | 已断开（最终状态） |

### 线程模型

- `FTcpMessageTransport` 运行在独立线程，循环处理：新连接 → 移除连接 → 检查状态 → 收取消息
- 每个 `FTcpMessageTransportConnection` 也有独立收发线程
- 消息序列化通过 `FTcpSerializeMessageTask` 异步图任务完成
- 使用无锁 MPSC 队列进行线程间通信

## Demo 示例

由于 TcpMessaging 是一个底层传输层，没有对外暴露直接使用的 API 示例。以下展示如何在自定义工具程序中启用和配置它：

### 在自定义工具程序中启用

1. 在 `.Target.cs` 中确保加载该模块（或通过 `ProgramAllowList` 添加你的程序名）
2. 在项目配置 `DefaultEngine.ini` 中配置：

```ini
[/Script/TcpMessaging.TcpMessagingSettings]
EnableTransport=True
ListenEndpoint=0.0.0.0:1988
ConnectToEndpoints=192.168.1.100:1988
ConnectionRetryDelay=1
ConnectionRetryPeriod=0
```

3. 启动时添加 `-Messaging` 参数（游戏程序场景下）：

```bash
UnrealEditor.exe MyProject -Messaging
```

## 模块依赖

从 `TcpMessaging.Build.cs` 提取：

| 模块 | 类型 | 用途 |
|---|---|---|
| `Core` | Public | 基础核心库 |
| `CoreUObject` | Private | UObject 系统（设置类支持） |
| `Networking` | Private | 网络基础设施（Socket、TCP 监听器） |
| `Serialization` | Private | 消息序列化/反序列化 |
| `Sockets` | Private | Socket 抽象层 |
| `Messaging` | Dynamic / IncludePath | UE 消息总线系统（动态加载） |
| `MessagingCommon` | IncludePath | 消息系统公共定义 |
| `Settings` | Dynamic / IncludePath | 编辑器设置面板（仅编辑器） |

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-05-21 | `9a46e4c4` | UnrealPak references TcpMessaging module | 将 UnrealPak 加入 ProgramAllowList，扩展了支持的程序范围 |
| 2024-11-09 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 代码清理，移除 5.2 版本的废弃 include 顺序兼容宏 |
| 2024-04-04 | `a8878bd1` | [Insights] Enable Session Frontend in Insights Session Browser | Insights 集成相关改动，非 TcpMessaging 核心功能更新 |

### 维护评价

- **创建时间**：2016 年，已存在约 10 年
- **活跃度**：**低**。最近 3 次提交均为周边维护（宏清理、工具列表扩展），没有核心功能更新
- **稳定性**：高。这是一个成熟的传输层实现，协议版本已稳定在 v2
- **限制**：
  - 仅支持 IPv4（使用 `FIPv4Endpoint`）
  - Shipping 构建默认禁用（需定义 `ALLOW_TCP_MESSAGING_SHIPPING`）
  - 不支持单线程平台
  - `ProgramAllowList` 限制了使用范围
- **推荐**：如果你在开发 UE 工具程序需要跨机器通信，这是一个开箱即用的方案。对于游戏项目，建议使用 UDP Messaging 或自建网络层。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Messaging/TcpMessaging)
- [官方文档]()（无）
- [UDP Messaging 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Messaging/UdpMessaging)（姊妹实现）
