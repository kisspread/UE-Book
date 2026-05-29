# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是 Epic Games 为虚拟制作工作流（特别是 Motion Design）开发的资产依赖同步插件。它提供了一套完整的解决方案，用于在网络上发现其他设备、管理连接状态、并高效地传输资产包（`spak`）。其核心设计目标是简化分布式环境下的资产依赖同步，确保不同工作站（如设计师的电脑、渲染农场节点）能快速获取所需的资产，支持“推”（Push）和“拉”（Pull）两种操作模式，是 Motion Design 工作流中不可或缺的一部分。

## 使用场景

- **多机协作**：在一个分布式 Motion Design 工作室中，多个艺术家和渲染节点需要共享和同步资产。
- **大型资产传输**：需要在网络中传输包含复杂依赖关系的资产包（`spak`）。
- **自动发现**：在局域网内自动发现并连接到其他 Storm Sync 实例，无需手动配置 IP 地址。
- **状态监控**：实时监控网络中其他设备的连接状态和服务器运行状态。

## C++ 用法

由于 StormSync 主要是一个网络同步框架，其核心用法涉及模块的初始化和管理。

### 头文件引入

```cpp
#include "IStormSyncTransportServerModule.h"
```

### 基本用法

启动并管理 Storm Sync 传输服务器。来源文件：`Private/StormSyncTransportServerModule.h`

```cpp
// 获取 Storm Sync Transport Server 模块的单例引用
IStormSyncTransportServerModule& StormSyncServer = IStormSyncTransportServerModule::Get();

// 启动发现管理器（用于在网络上发现其他 Storm Sync 实例）
StormSyncServer.StartDiscoveryManager();

// 启动一个本地服务器端点（监听传入的资产传输请求）
FString EndpointName = TEXT("MyRenderNode");
StormSyncServer.StartServerEndpoint(EndpointName);

// 检查服务器是否正在运行
bool bIsRunning = StormSyncServer.IsRunning();
if (bIsRunning)
{
    UE_LOG(LogTemp, Log, TEXT("Storm Sync 服务器已启动并运行。"));
}
```

### 进阶用法

自定义 TCP 服务器端点，并监听连接事件。来源文件：`Private/Socket/StormSyncTransportTcpServer.h`

```cpp
// 创建一个自定义的 TCP 服务器
FIPv4Address LocalAddress(127, 0, 0, 1);
uint16 Port = 12345;
uint32 InactiveTimeoutSeconds = 30;

TUniquePtr<FStormSyncTransportTcpServer> TcpServer = MakeUnique<FStormSyncTransportTcpServer>(
    LocalAddress, Port, InactiveTimeoutSeconds);

// 绑定缓冲区接收事件，当一个完整的资产包被接收时触发
TcpServer->OnReceivedBuffer().AddLambda([](const FIPv4Endpoint& Endpoint, const TSharedPtr<FSocket>& Socket, const FStormSyncBufferPtr& Buffer)
{
    UE_LOG(LogTemp, Log, TEXT("从 %s 接收到一个大小为 %llu 字节的资产包。"), *Endpoint.ToString(), Buffer->Num());
    // 处理接收到的缓冲区（资产包）
});

// 开始监听传入的连接
if (TcpServer->StartListening())
{
    UE_LOG(LogTemp, Log, TEXT("TCP 服务器正在监听 %s。"), *TcpServer->GetEndpointAddress());
}
```

## 模块依赖

StormSync 依赖于 Unreal Engine 的网络和消息传递框架。

| 模块 | 用途 |
|---|---|
| `Messaging` | 核心消息总线系统，用于在实例间发送发现、心跳和控制消息 |
| `Sockets` | 底层网络套接字支持，用于 TCP 数据传输 |
| `Json` | 用于序列化和反序列化控制消息（如连接信息） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复了安全漏洞，防止恶意构造的资产包利用包名进行攻击 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复了资产导出向导在更改设置时错误创建大量嵌套文件夹的 UI 问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了日志中 32 位和 64 位格式说明符不匹配的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为新的 UE_LOGF 宏 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正了之前一次错误的查找替换操作 |

### 维护评价

**活跃维护**。该插件虽然创建时间不长（约1年），但近期更新频繁（最近一次更新在数天前），内容涵盖重要的安全修复、功能改进和代码质量优化。从更新记录看，Epic Games 正在积极维护此插件，以将其整合到正式的虚拟制作工作流中。推荐在需要资产同步的 Motion Design 项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [官方文档]() (无)
- [测试用例]() (无)