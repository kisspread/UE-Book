# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 插件用于将 Unreal Engine 的渲染画面和音频通过 WebRTC 协议实时流式传输到兼容的客户端，例如现代 Web 浏览器。它解决的核心问题是：允许用户无需在本地设备上运行 UE 引擎或打包的游戏/应用，即可在网页端获得高保真、低延迟的交互式 3D 体验。

与旧版 Pixel Streaming 相比，v2 版本旨在提供更模块化、更可扩展的架构，支持更丰富的输入处理和服务器管理能力。插件本身包含运行时核心、输入处理、服务器管理等多个模块，允许开发者按需组合。

## 使用场景

- **云端渲染与串流**：在云服务器上运行 UE 应用，并将画面通过网页串流给终端用户，适用于云游戏、云端设计评审等。
- **嵌入式 Web 预览**：在产品网页或企业门户中直接嵌入交互式的 3D 模型或应用程序预览。
- **远程协作与培训**：允许多用户通过浏览器同时查看并操控同一 UE 场景，用于远程培训、虚拟展示或协同设计。
- **轻量级客户端访问**：为硬件配置较低的终端设备提供访问高要求 UE 应用的能力。

## 蓝图用法

当前提供的 `PixelStreaming2Servers` 模块主要面向 C++ 开发，其核心类与接口未通过 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 直接暴露给蓝图。服务器的启动和管理主要通过 C++ 代码完成。流媒体的开启、设置等核心功能可能位于 `PixelStreaming2` 或 `PixelStreaming2Core` 等其他模块中。

## C++ 用法

### 头文件引入

要使用 `PixelStreaming2Servers` 模块提供的服务器管理功能，需要包含其公共头文件。

```cpp
#include "PixelStreaming2Servers.h"
```

### 基本用法：启动内嵌信令服务器

`PixelStreaming2Servers` 模块的核心功能是提供一个 C++ 原生的信令服务器实现，类似于 Node.js 版本的 Cirrus。以下示例展示了如何创建并启动这个内嵌信令服务器。

**来源文件：** `Public/PixelStreaming2Servers.h`

```cpp
using namespace UE::PixelStreaming2Servers;

// 1. 创建信令服务器实例（尚未启动）
TSharedPtr<IServer> SignallingServer = MakeSignallingServer();

// 2. 定义启动参数
FLaunchArgs LaunchArgs;
LaunchArgs.ProcessArgs = TEXT("--StreamerPort=8888 --PlayerPort=80"); // 可配置参数
LaunchArgs.bPollUntilReady = true; // 启动后轮询直到就绪

// 3. 绑定服务器就绪委托
SignallingServer->OnReady.AddLambda([](const FEndpoints& Endpoints) {
    // 服务器已就绪，可以从Endpoints map中获取各服务的URL
    if (const FURL* PlayerUrl = Endpoints.Find(EEndpoint::Signalling_Players))
    {
        UE_LOG(LogTemp, Log, TEXT("Players can connect at: %s"), *PlayerUrl->ToString());
    }
});

// 4. 绑定服务器启动失败委托（例如超时）
SignallingServer->OnFailedToReady.AddLambda([]() {
    UE_LOG(LogTemp, Error, TEXT("Signalling server failed to become ready!"));
});

// 5. 启动服务器
if (!SignallingServer->Launch(LaunchArgs))
{
    UE_LOG(LogTemp, Error, TEXT("Failed to launch signalling server."));
}
```

### 进阶用法：查询连接的流媒体数量

`IServer` 接口提供了异步查询当前连接到信令服务器的流媒体（Streamer）数量的方法。

```cpp
// 获取服务器实例后，查询连接数
SignallingServer->GetNumStreamers([](uint16 NumStreamers) {
    UE_LOG(LogTemp, Log, TEXT("Number of connected streamers: %u"), NumStreamers);
});
```

## Demo 示例

一个最小的可运行 C++ 示例，演示如何在自定义模块中启动 Pixel Streaming 内嵌信令服务器。

**MyPixelStreamingServer.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "PixelStreaming2Servers.h"

class FMyPixelStreamingServer
{
public:
    FMyPixelStreamingServer();
    ~FMyPixelStreamingServer();

    void StartServer();
    void StopServer();

private:
    TSharedPtr<UE::PixelStreaming2Servers::IServer> Server;
};
```

**MyPixelStreamingServer.cpp**
```cpp
#include "MyPixelStreamingServer.h"
#include "PixelStreaming2Servers.h"

using namespace UE::PixelStreaming2Servers;

FMyPixelStreamingServer::FMyPixelStreamingServer()
{
}

FMyPixelStreamingServer::~FMyPixelStreamingServer()
{
    StopServer();
}

void FMyPixelStreamingServer::StartServer()
{
    if (Server.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Server is already running."));
        return;
    }

    // 创建信令服务器
    Server = MakeSignallingServer();

    // 绑定就绪回调
    Server->OnReady.AddLambda([](const FEndpoints& Endpoints) {
        UE_LOG(LogTemp, Log, TEXT("Pixel Streaming Signalling Server is ready."));
        // 此处可以开始启动流媒体或通知其他系统
    });

    // 配置启动参数
    FLaunchArgs Args;
    Args.ProcessArgs = TEXT("--StreamerPort=8888 --PlayerPort=80");
    Args.bPollUntilReady = true;
    Args.ReconnectionTimeoutSeconds = 30.0f;

    // 启动服务器
    if (!Server->Launch(Args))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to launch Pixel Streaming signalling server."));
        Server.Reset();
    }
}

void FMyPixelStreamingServer::StopServer()
{
    if (Server.IsValid())
    {
        Server->Stop();
        Server.Reset();
        UE_LOG(LogTemp, Log, TEXT("Pixel Streaming Signalling Server stopped."));
    }
}
```

## 模块依赖

对于 `PixelStreaming2Servers` 模块，其 `Build.cs` 文件显示它依赖 `PixelStreaming2Core`。但这些是插件内部的模块依赖。

对于一个希望**使用** `PixelStreaming2Servers` 模块功能的游戏或编辑器插件项目，**无需**在 `Build.cs` 中添加任何不常见的依赖。只需确保 `PublicDependencyModuleNames` 中包含 `PixelStreaming2Servers` 即可。该模块自身没有依赖引擎外部或非常规的模块。

| 模块 | 用途 |
|---|---|
| （无特殊依赖） | 使用该插件无需引用除标准引擎模块外的其他特定模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器错误获取默认目标窗口的方法。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数导致的编译警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：将各种虚拟制片资产迁移至不同的资产分类。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中作用域枚举可能导致输出乱码的问题。 |

### 维护评价

- **创建时间**：插件于 2024 年 9 月创建，相对年轻。
- **活跃度**：最近一次提交在 2026 年 5 月，且近期有多次功能修复和优化，表明插件处于**活跃维护**状态。
- **功能状态**：`.uplugin` 中 `EnabledByDefault` 为 `false`，表明该插件可能仍处于**实验性或可选**阶段，但持续更新意味着其正在走向稳定。
- **推荐度**：**推荐使用**。对于需要在引擎进程内管理信令服务器或进行深度集成的场景，`PixelStreaming2Servers` 模块提供了强大且持续维护的底层支持。对于简单的串流需求，可以先使用插件默认的服务器管理方式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)