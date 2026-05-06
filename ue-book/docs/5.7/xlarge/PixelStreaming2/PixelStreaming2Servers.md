# Pixel Streaming 2 Servers

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送2服务器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

`PixelStreaming2Servers` 是 Pixel Streaming 2 插件中专门用于**启动、管理和探测**像素流送相关服务器的模块。它提供了统一接口来启动信令服务器（Signalling Server）、选择转发单元（SFU）服务器以及下载官方服务器脚本。该模块支持三种运行模式：
- **内嵌 C++ 信令服务器**：不依赖 Node.js，通过 WebSocket 直接在 UE 进程中实现信令交互。
- **本地进程服务器**：启动预编译的二进制文件或脚本（如 `cirrus.js`）。
- **远程服务器**：通过 WebSocket 探测已启动的外部服务器。

该模块解决了像素流送场景中服务器端的生命周期管理、端口分配、连接状态轮询等通用问题，使得 UE 流媒体端能与浏览器或 SFU 建立稳定可靠的 WebRTC 连接。

## 使用场景

- **单机游戏直播**：在编辑器或打包游戏中启动内置信令服务器，玩家通过浏览器连接 UE 渲染画面。
- **云端渲染集群**：自动下载并启动多个副本的信令服务器，与 SFU 配合实现弹性扩展。
- **自动化测试**：在 CI/CD 流程中通过代码控制服务器启停，验证像素流送完整性。
- **自定义信令逻辑**：基于 `FSignallingServer` 派生新类，扩展消息处理逻辑（如权限认证、房间管理）。

## 蓝图用法

本模块**未暴露任何蓝图可调用函数或属性**，所有服务器启动与管理均在 C++ 层完成。如需在蓝图中使用，需在 C++ 中包装为函数库，或通过 `FLaunchArgs` 等结构体参数间接控制。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreaming2Servers.h"
```

### 基本用法

#### 启动内置信令服务器（不依赖 Node.js）

使用 `IServer` 接口的派生类 `FSignallingServer`（位于私有源文件中，推荐通过工厂函数创建）。以下示例展示了基本启动流程：

```cpp
// 文件：Source/PixelStreaming2Servers/Private/SignallingServer.cpp
using namespace UE::PixelStreaming2Servers;

FLaunchArgs LaunchArgs;
LaunchArgs.ProcessArgs = TEXT("--HttpPort=8080 --StreamerPort=8888 --PlayerPort=80");
LaunchArgs.bPollUntilReady = true;
LaunchArgs.ReconnectionTimeoutSeconds = 30.0f;

// 创建内置信令服务器
TUniquePtr<IServer> SignallingServer = MakeUnique<FSignallingServer>();

// 绑定就绪回调
FOnReady OnReadyCallback;
OnReadyCallback.AddLambda([](const FEndpoints& Endpoints)
{
    UE_LOG(LogPixelStreaming2Servers, Log, TEXT("Server ready! Endpoints:"));
    for (const auto& [Key, URL] : Endpoints)
    {
        UE_LOG(LogPixelStreaming2Servers, Log, TEXT("  %s: %s"), *URL.ToString());
    }
});

// 启动（异步）
bool bLaunched = SignallingServer->Launch(LaunchArgs);

// 在 Tick 中轮询就绪状态（或绑定 OnReady 回调）
if (SignallingServer->IsReady())
{
    // 获取端点
    FURL StreamerWS = Endpoints[EEndpoint::Signalling_Streamer];
}
```

#### 通过进程启动外部服务器（如 cirrus.js）

使用 `Utils::LaunchChildProcess` 执行 Node.js 脚本：

```cpp
// 文件：Source/PixelStreaming2Servers/Private/ServerUtils.h
FString ResourcesDir;
Utils::GetResourcesDir(ResourcesDir);

FString ServerScript = FPaths::Combine(ResourcesDir, TEXT("cirrus.js"));
FString Args = TEXT("--HttpPort=8080 --StreamerPort=8888");

TSharedPtr<FMonitoredProcess> Process = Utils::LaunchChildProcess(
    ServerScript,
    Args,
    TEXT("[Cirrus]"),
    true // 作为脚本运行（通过 cmd/bash）
);

if (Process.IsValid())
{
    Process->Launch();
}
```

#### 获取可用端口

```cpp
// 文件：Source/PixelStreaming2Servers/Internal/SocketUtils.h
TOptional<int> StartingPort(0);
int Port = UE::PixelStreaming2::GetNextAvailablePort(StartingPort);
// 返回第一个可用端口，从 StartingPort 开始尝试
```

### 进阶用法

#### 自定义信令消息处理

继承 `FSignallingServer` 并重写事件处理器：

```cpp
// 文件：Source/PixelStreaming2Servers/Private/SignallingServer.h
class FMySignallingServer : public FSignallingServer
{
protected:
    virtual void OnStreamerConnected(uint16 ConnectionId) override
    {
        UE_LOG(LogTemp, Log, TEXT("Custom streamer connected: %d"), ConnectionId);
        // 添加自定义逻辑，如验证 token
        FServerBase::OnStreamerConnected(ConnectionId);
    }
    virtual void OnPlayerMessage(uint16 ConnectionId, TArrayView<uint8> Message) override
    {
        FString MsgStr = Utils::ToString(Message);
        // 拦截并处理自定义消息
        UE_LOG(LogTemp, Log, TEXT("Player message: %s"), *MsgStr);
    }
};
```

#### 下载官方服务器脚本

```cpp
// 使用 Utils::DownloadPixelStreaming2Servers 下载最新服务器
TSharedPtr<FMonitoredProcess> DownloadProcess = Utils::DownloadPixelStreaming2Servers(true); // 若已存在则跳过
if (DownloadProcess.IsValid())
{
    DownloadProcess->Launch();
    // 等待下载完成...
}
```

## Demo 示例

以下为一个独立的 C++ 类，演示如何启动内置信令服务器并建立基本信令交互：

```cpp
// PS2ServerDemo.h
#pragma once
#include "CoreMinimal.h"
#include "PixelStreaming2Servers.h"

class FPS2ServerDemo
{
public:
    FPS2ServerDemo();
    ~FPS2ServerDemo();
    void Start();
    void Stop();
private:
    TUniquePtr<UE::PixelStreaming2Servers::IServer> SignallingServer;
};

// PS2ServerDemo.cpp
#include "PS2ServerDemo.h"
#include "PixelStreaming2Servers.h"

using namespace UE::PixelStreaming2Servers;

FPS2ServerDemo::FPS2ServerDemo()
{
    // 工厂：实际应通过模块暴露的创建函数获取，这里直接使用内建类（私有头文件）
    // 此示例假设已有导出类，仅演示概念
    // SignallingServer = MakeUnique<...>();
}

void FPS2ServerDemo::Start()
{
    FLaunchArgs LaunchArgs;
    LaunchArgs.ProcessArgs = TEXT("--HttpPort=0 --StreamerPort=8888 --PlayerPort=80");
    LaunchArgs.bPollUntilReady = true;
    LaunchArgs.ReconnectionTimeoutSeconds = 30.0f;

    // 绑定就绪回调
    FOnReady OnReady;
    OnReady.AddLambda([this](const FEndpoints& Endpoints)
    {
        UE_LOG(LogTemp, Log, TEXT("Signalling server ready!"));
        for (const auto& [Key, URL] : Endpoints)
        {
            UE_LOG(LogTemp, Log, TEXT("  %s -> %s"), *URL.ToString());
        }
    });

    if (SignallingServer->Launch(LaunchArgs))
    {
        UE_LOG(LogTemp, Log, TEXT("Server launching..."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to launch server."));
    }
}

void FPS2ServerDemo::Stop()
{
    if (SignallingServer.IsValid())
    {
        SignallingServer->Stop();
    }
}
```

## 模块依赖

根据 `Build.cs` 分析（本模块 `PixelStreaming2Servers`）：

| 模块 | 用途 |
|---|---|
| `WebSockets` | 提供 `FWebSocketsModule` 用于客户端 WebSocket 探测 |
| `WebSocketNetworking` | 提供 `IWebSocketServer` 和 `INetworkingWebSocket` 实现服务器端 WebSocket |
| `JsonUtilities` | 解析/序列化 JSON 配置与信令消息 |
| `Projects` | 访问插件资源目录（`FPaths::PluginDir`） |

> **注意**：`PixelStreaming2Servers` 还间接依赖 `PixelStreaming2Core`（公共类型和日志），但 Build.cs 中通常将 `PixelStreaming2Core` 列为 `PrivateDependencyModuleNames`。若使用此模块，需在自己的 `Build.cs` 中添加 `"PixelStreaming2Servers"` 模块依赖，其余传递依赖自动解析。

```cpp
// YourProject.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "PixelStreaming2Servers",
    // 无需手动添加 WebSockets、WebSocketNetworking，会自动传递
});
```

## 维护状态

### 近期更新

- 2026-01-23 `a9928676` [NVCodecs, PixelStreaming2] Fixes: 修复编解码器和像素流送相关问题
- 2025-11-18 `d7a4d160` [AVCodecs, PixelStreaming2] Fixes: 修复音视频编解码器兼容性
- 2025-10-28 `b1db9444` [PixelStreaming2] Fix: Deadlocks in PixelStreaming2Thread 修复线程死锁
- 2025-10-17 `5c2f039d` [PS2] Fix: Non-functional public API 修复无效的公有 API
- 2025-10-13 `0de4d465` [PS2] Bug Fixes for 5.7 针对 UE5.7 的 Bug 修复

### 维护评价

- **创建时间**：2025-10-13，距今约 6 个月（相对于当前 2026-03 推测）。
- **更新频率**：高，平均每月有 2-3 次功能性修复/更新。
- **活跃度**：非常活跃，持续有新功能和修复合并。
- **已知问题**：早期版本存在死锁（已修复），非功能性 API（已修复）。
- **推荐度**：强烈推荐用于 UE5.7 及以上版本的像素流送项目。该模块提供了稳定的服务器管理方案，且内置信令服务器无需额外 Node.js 环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2Servers)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2Servers/Private)（与源码同目录，包含单元测试）