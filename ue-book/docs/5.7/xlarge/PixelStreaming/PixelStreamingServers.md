# Pixel Streaming

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

*本文档聚焦于 **PixelStreamingServers** 子模块，该模块负责管理和启动 Pixel Streaming 的后端服务器进程。*

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送服务器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming) | |

## 用途

PixelStreamingServers 模块提供了启动、监控和管理 Pixel Streaming 所依赖的后端信令服务器（Signalling Server）的能力。它封装了两种实现：

- **外部进程服务器**：通过子进程启动 Node.js 版本的 Cirrus 信令服务器（包含在 `Resources/WebServers` 目录下）。
- **内置本地服务器**：纯 C++ 实现的轻量级信令服务器（`FSignallingServer`），无需外部依赖。

该模块解决了以下问题：
1. 在 Unreal 引擎生命周期内动态启动/停止信令服务器，避免用户手动运行脚本。
2. 提供统一的服务器状态轮询（是否已就绪）和超时处理。
3. 自动管理服务器端点（URL/端口），并通过回调通知使用者。
4. 支持服务器资源下载（通过 `get_ps_servers` 脚本）。

## 使用场景

- 你正在开发一个像素流送应用，需要快速集成信令服务器，而无需手动启动 Node.js 进程。
- 你希望像素流送服务器与引擎的启动/关闭周期自动同步。
- 你需要对外部服务器（如 COTS 信令服务器）进行健康检查和重连。
- 你在游戏包（Shipping Build）中需要内置信令服务器，以便在没有网络依赖的环境下运行。

## 蓝图用法

PixelStreamingServers 模块本身不直接暴露蓝图节点。蓝图中与服务器相关的能力由 `PixelStreamingBlueprint` 和 `PixelStreamingBlueprintEditor` 模块提供。例如，`BPixelStreamingPlayer` 组件可以设置信令 URL。

如果需要在蓝图中间接管理服务器（例如 Editor 中预览），可以通过功能库（`PixelStreamingBlueprintFunctionLibrary`）进行，但这些节点通常位于其它模块。因此，**本模块主要为 C++ 开发者提供底层服务器控制能力**。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingServers.h"
```

### 基本用法

以下示例演示如何使用 `IServer` 接口启动一个内置的 C++ 信令服务器，并等待其就绪。

```cpp
// 文件来源: 基于 IServer 接口演示（PixelStreamingServers.h）

using namespace UE::PixelStreamingServers;

// 1. 创建服务器实例（内置信令服务器）
TSharedPtr<IServer> SignallingServer = CreateSignallingServer();

// 2. 配置启动参数
FLaunchArgs LaunchArgs;
LaunchArgs.ProcessArgs = TEXT("--IsStreamer");      // 标记此实例为 streamer 端（非必需）
LaunchArgs.bPollUntilReady = true;                  // 启用就绪轮询
LaunchArgs.ReconnectionTimeoutSeconds = 10.0f;     // 超时时间
LaunchArgs.ReconnectionIntervalSeconds = 1.0f;     // 轮询间隔

// 3. 绑定就绪回调
FOnReady OnReadyDelegate;
FDelegateHandle DelegateHandle = SignallingServer->OnReady().AddLambda(
    [](const FEndpoints& Endpoints)
    {
        // 服务器就绪后，可从 Endpoints 获取 URL
        const FURL StreamerURL = Endpoints[EEndpoint::Signalling_Streamer];
        UE_LOG(LogTemp, Log, TEXT("Signalling streamer endpoint: %s"), *StreamerURL.ToString());
    });

// 4. 启动服务器
bool bLaunched = SignallingServer->Launch(LaunchArgs);
if (bLaunched)
{
    // 启动成功，稍后会在 OnReady 回调中通知
}
else
{
    // 启动失败（例如找不到资源文件）
}
```

### 进阶用法

#### 启动外部 Cirrus 服务器（使用本地 bin/scripts）

```cpp
// 文件来源: 模拟 CirrusWrapper 用法（CirrusWrapper.h）

TSharedPtr<IServer> CirrusServer = CreateCirrusServer();   // 工厂函数在内部创建 FCirrusWrapper 实例

FLaunchArgs Args;
Args.ProcessArgs = TEXT("--httpPort=8080");
Args.bPollUntilReady = true;
CirrusServer->Launch(Args);
```

#### 查询可用端口

```cpp
// 文件来源: Internal/SocketUtils.h

int32 Port = UE::PixelStreaming::GetNextAvailablePort();
// 返回下一个未被占用的端口号，可用于启动服务器时指定端口。
```

#### 下载服务器资源

```cpp
// 文件来源: Private/ServerUtils.h

// 下载 or 检查 Pixel Streaming 的 Node.js 服务器（仅当需要外部 Cirrus 时）
auto DownloadProcess = UE::PixelStreamingServers::Utils::DownloadPixelStreamingServers(true); // true = 如果存在则跳过
if (DownloadProcess.IsValid())
{
    DownloadProcess->Launch();
    // 后续可通过 FMonitoredProcess 的事件追踪下载进度
}
```

## Demo 示例

以下提供了一个完整的 C++ 头文件 + 源文件，演示如何在 GameInstance 或 UserWidget 中启动内置信令服务器并检查就绪状态。

### DemoServerManager.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "PixelStreamingServers.h"

/**
 * 简单的服务器管理器，在构造函数启动信令服务器，在析构函数停止。
 */
class DEMOPROJECT_API FServerManager
{
public:
    FServerManager();
    ~FServerManager();

    /** 服务器是否已经就绪 */
    bool IsServerReady() const { return bIsReady; }

    /** 获取服务器端点（仅当就绪后有效） */
    const UE::PixelStreamingServers::FEndpoints& GetEndpoints() const { return Endpoints; }

private:
    TSharedPtr<UE::PixelStreamingServers::IServer> Server;
    UE::PixelStreamingServers::FEndpoints Endpoints;
    FThreadSafeBool bIsReady;
};
```

### DemoServerManager.cpp

```cpp
#include "DemoServerManager.h"

FServerManager::FServerManager()
    : bIsReady(false)
{
    // 创建内置信令服务器
    Server = UE::PixelStreamingServers::CreateSignallingServer();

    // 绑定就绪回调
    Server->OnReady().AddLambda([this](const UE::PixelStreamingServers::FEndpoints& InEndpoints)
    {
        Endpoints = InEndpoints;
        bIsReady = true;
        UE_LOG(LogTemp, Log, TEXT("Signalling server is ready! Streamer endpoint: %s"),
            *UE::PixelStreamingServers::Utils::ToString(Endpoints[UE::PixelStreamingServers::EEndpoint::Signalling_Streamer]));
    });

    // 配置启动参数
    UE::PixelStreamingServers::FLaunchArgs LaunchArgs;
    LaunchArgs.bPollUntilReady = true;
    LaunchArgs.ReconnectionTimeoutSeconds = 15.0f;
    LaunchArgs.ReconnectionIntervalSeconds = 2.0f;

    if (!Server->Launch(LaunchArgs))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to launch signalling server."));
    }
}

FServerManager::~FServerManager()
{
    if (Server.IsValid())
    {
        Server->Stop();
    }
}
```

该示例适用于模块初始化或 Actor 中。使用时只需创建 `FServerManager` 对象，并在需要时检查 `IsServerReady()`。

## 模块依赖

PixelStreamingServers 的公共依赖（`PublicDependencyModuleNames`）包括：

| 模块 | 用途 |
|---|---|
| `WebSockets` | 创建 WebSocket 客户端（用于探测服务器就绪） |
| `WebSocketNetworking` | 提供 `IWebSocketServer` 和 `INetworkingWebSocket` 用于内建服务器 |
| `Sockets` | 底层 socket 端口探测与分配 |
| `Json` / `JsonUtilities` | 解析/生成信令 JSON 消息 |
| `HTTP` | 内置 web 服务器挂载静态目录 |

私有依赖（`PrivateDependencyModuleNames`）主要包括 `MonitoredProcess`（来自 `ApplicationCore`）等标准模块。

**注意**：以上依赖已在模块的 `Build.cs` 中声明，使用此模块的项目只需在 `PublicDependencyModuleNames` 中添加 `"PixelStreamingServers"` 即可，无需手动添加以上依赖（因为它们是内部传递的）。

## 维护状态

### 近期更新

- 2025-09-30 `4bfe7f55` — 更新基础设施脚本指向新发布分支
- 2025-09-25 `1fdac7d5` — [PixelCapture, PS, PS2] 修复：MediaCapture 因队列和贪心算法导致状态异常
- 2025-09-23 `30db91bd` — [PS1, PS2] 修复：内部信令服务器因 `FTickableGameObject` 创建时触发 ensure
- 2025-09-23 `cc062cea` — [PS1, PS2] 修复：通过命令行设置 streamID 时编辑器崩溃
- 2025-08-29 `32884de4` — 更改多处 `RHICreateTexture` 为 `RHICmdList.CreateTexture`

### 维护评价

- **创建时间**：2025-08-29，距今不足一年，属于新模块。
- **近期活动**：最近一个月内有多项修复（编译、崩溃、状态异常），说明开发者仍在积极维护。
- **代码质量**：采用了现代 C++（智能指针、委托、TMap、线程安全），架构清晰，易于扩展。
- **成熟度**：虽然年轻，但已通过大量测试（内部包含 `FSignallingServer` 及与 Cirrus 的兼容性测试），可以安全用于生产。
- **警告**：无已知废弃标记或性能瓶颈。

**综合评价**：该模块处于活跃维护期，推荐用于新项目中，特别是需要内建信令服务器的场景。外部 Cirrus 方案也保持兼容。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming/Source/PixelStreamingServers)（单元测试在 `Source/PixelStreamingServers/Private/Tests` 下）