# Web Socket Messaging

> Adds a WebSocket based transport layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 中文名 | WebSocket消息传输 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebSocketMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WebSocketMessaging) | |

## 用途

此插件为 Unreal Engine 的 **Message Bus** 消息系统增加了一个基于 **WebSocket 协议**的传输层实现。它的核心目标是让 UE 内部的进程间通信（IPC）能够跨越网络边界，通过标准的 WebSocket 进行。这使得运行在不同机器（例如，编辑器和独立进程）或设备（例如，UE 和外部 Web 应用）上的 UE 实例或外部应用程序，能够以统一的消息格式进行双向通信。它解决了 UE 内置消息总线在默认情况下局限于单个进程内部的问题，将其能力扩展到整个局域网。

## 使用场景

- 你需要将外部开发的移动端应用、Web 应用或桌面工具连接到正在运行的 UE 编辑器或游戏实例，以发送控制指令或接收状态更新。
- 你需要在局域网内运行多个 UE 实例（例如，用于分布式渲染或压力测试），并让它们之间能够相互发现和通信。
- 你需要在运行时动态发现网络上可用的、启用了此插件的 UE 服务，并获取其连接信息（如端口）。

## 蓝图用法

此插件主要提供底层的传输层实现，其主要 API 为 C++ 接口。在蓝图层面，没有直接暴露给设计师的函数或属性节点。其行为通过**项目设置**中的 `UWebSocketMessagingSettings` 进行配置（例如，启用传输、设置服务器端口、添加连接端点等）。

### 核心配置（项目设置）

| 设置项 | 说明 |
|---|---|
| `EnableTransport` | 启用/禁用 WebSocket 传输层 |
| `ServerPort` | 服务器监听的端口（0 禁用） |
| `ConnectToEndpoints` | 需要主动连接的 WebSocket URL 列表 |
| `bEnableDiscoveryListener` | 启用多播发现服务，以应答外部应用的探测 |

## C++ 用法

### 头文件引入

要访问此插件的核心模块接口，需要包含：
```cpp
#include "IWebSocketMessagingModule.h"
```

### 基本用法（查询传输状态）

通过插件模块接口，可以查询传输层是否正在运行以及使用的端口。这对于需要知道通信状态的游戏逻辑或工具代码很有用。
```cpp
// 获取 WebSocket Messaging 模块实例
IWebSocketMessagingModule& WebSocketModule = FModuleManager::GetModuleChecked<IWebSocketMessagingModule>(TEXT("WebSocketMessaging"));

// 检查传输层是否正在运行（服务器已启动或客户端已连接）
bool bIsRunning = WebSocketModule.IsTransportRunning();

// 获取当前使用的服务器端口（可能是配置端口或命令行指定的端口）
int32 CurrentPort = WebSocketModule.GetServerPort();
```
*（来源：分析 `IWebSocketMessagingModule.h` 及 `FWebSocketMessagingModule` 的实现推断）*

### 进阶用法（配置与自定义）

实际的启动和停止由模块在 `StartupModule()` 和 `ShutdownModule()` 中根据 `UWebSocketMessagingSettings` 的设置自动完成。开发者主要通过修改项目设置来控制其行为。对于需要更深度控制的场景，可以参考 `FWebSocketMessageTransport` 类，它实现了 `IMessageTransport` 接口，是整个功能的基石。

## Demo 示例

由于此插件主要通过配置驱动，且其核心功能是作为内部系统服务运行，因此没有独立的游戏逻辑 Demo。以下是一个如何在代码中查询插件状态的最小示例：

```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "WebSocket")
    void LogWebSocketStatus() const;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "IWebSocketMessagingModule.h"

void AMyActor::LogWebSocketStatus() const
{
    // 检查模块是否已加载
    if (FModuleManager::Get().IsModuleLoaded("WebSocketMessaging"))
    {
        IWebSocketMessagingModule& WSModule = FModuleManager::GetModuleChecked<IWebSocketMessagingModule>("WebSocketMessaging");
        
        UE_LOG(LogTemp, Display, TEXT("WebSocket Transport Running: %s"), WSModule.IsTransportRunning() ? TEXT("Yes") : TEXT("No"));
        UE_LOG(LogTemp, Display, TEXT("Server Port: %d"), WSModule.GetServerPort());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("WebSocketMessaging plugin is not loaded."));
    }
}
```

## 模块依赖

此插件对其他两个 UE 插件有直接依赖，这些依赖会在 `.uplugin` 中声明并自动启用。

| 模块 | 用途 |
|---|---|
| `WebSocketNetworking` | 提供底层的 WebSocket 客户端和服务器网络功能实现 |
| `DiscoveryBeaconReceiver` | 提供多播服务发现的基础框架，此插件的信标接收器继承自它 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持 FString 和共享字符串，提升内存效率 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF，统一日志输出方式 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 JSON 对象中的字符串重复，释放内存 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回滚了之前的更改 |
| 2026-02-25 | `af0dfacf` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 JSON 对象中的字符串重复，释放内存（初始提交） |

### 维护评价

该插件仍处于 **实验性** 阶段，且默认未启用。从 Git 历史看，自创建以来（2024年）一直有持续的、小范围的维护和优化工作，主要集中在内存管理、代码重构和日志系统迁移上。这些更新表明 Epic 对该功能仍有关注，但尚无重大新功能的引入。由于其处于实验状态，**不建议在生产环境中直接依赖**，但非常适合用于技术预研、原型开发和内部工具链。对于需要网络化消息总线的特定项目，这是一个有价值的参考和起点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WebSocketMessaging)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WebSocketMessaging)（插件目录内未发现独立测试文件）