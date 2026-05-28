# Pixel Streaming

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流传输 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming) | |

## 用途

Pixel Streaming 允许将 Unreal Engine 的渲染画面和音频通过 WebRTC 协议实时传输到支持 WebRTC 的播放端（如网页浏览器）。本文档聚焦的 **PixelStreamingServers** 模块负责管理信令服务器（Signalling Server）的生命周期——它是 Pixel Streaming 架构中的核心基础设施，负责在 UE 流式传输端（Streamer）与浏览器播放端（Player）之间协调 WebRTC 连接建立。

该模块解决的核心问题是：**如何在 UE 内部启动、管理和监控信令服务器**。它提供三种启动方式：
1. 以子进程方式启动 NodeJS 版 Cirrus 信令服务器
2. 以嵌入 UE 进程的方式启动原生 C++ 信令服务器（无外部依赖）
3. 兼容 UE 4.26/4.27 旧版信令协议的 Legacy 信令服务器

默认不启用（`EnabledByDefault=false`），需要手动在项目设置中启用。

## 使用场景

- 你需要将 UE 应用画面流式传输到远程浏览器 → 启用 Pixel Streaming 并使用信令服务器
- 你在开发云游戏、远程渲染、虚拟制片等需要低延迟串流的项目 → 使用此模块管理信令服务器
- 你想避免外部 NodeJS 依赖 → 使用 `MakeSignallingServer()` 创建纯 C++ 嵌入式信令服务器
- 你需要兼容旧版 Pixel Streaming 前端页面 → 使用 `MakeLegacySignallingServer()`
- 你希望服务器以独立子进程运行以隔离崩溃影响 → 使用 `MakeCirrusServer()`

## 蓝图用法

本模块（PixelStreamingServers）本身不提供蓝图节点，它是纯 C++ 模块。蓝图交互主要由 `PixelStreamingBlueprint` 模块提供。服务器的创建和管理在 C++ 层完成。

### C++ 核心 API

| 函数 | 说明 | 所在类 |
|---|---|---|
| `MakeCirrusServer()` | 创建 NodeJS Cirrus 信令服务器实例（子进程方式） | `UE::PixelStreamingServers` |
| `MakeSignallingServer()` | 创建原生 C++ 信令服务器实例（无外部依赖） | `UE::PixelStreamingServers` |
| `MakeLegacySignallingServer()` | 创建兼容旧版协议的 C++ 信令服务器 | `UE::PixelStreamingServers` |
| `DownloadPixelStreamingServers()` | 下载信令服务器文件到本地 | `UE::PixelStreamingServers` |

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingServers.h"
```

### 基本用法

创建并启动一个原生 C++ 信令服务器：

```cpp
#include "PixelStreamingServers.h"

using namespace UE::PixelStreamingServers;

// 创建信令服务器
TSharedPtr<IServer> Server = MakeSignallingServer();

// 绑定就绪回调
Server->OnReady.AddLambda([](const FEndpoints& Endpoints) {
    for (const auto& [Endpoint, Url] : Endpoints) {
        UE_LOG(LogTemp, Log, TEXT("Endpoint ready: %s"), *Url.ToString());
    }
});

// 绑定失败回调
Server->OnFailedToReady.AddLambda([]() {
    UE_LOG(LogTemp, Error, TEXT("Server failed to become ready"));
});

// 配置启动参数
FLaunchArgs LaunchArgs;
LaunchArgs.bPollUntilReady = true;
LaunchArgs.ReconnectionTimeoutSeconds = 30.0f;
LaunchArgs.ReconnectionIntervalSeconds = 2.0f;

// 启动服务器
if (Server->Launch(LaunchArgs))
{
    UE_LOG(LogTemp, Log, TEXT("Server launched successfully"));
}
```

### 进阶用法

使用 NodeJS Cirrus 服务器并自定义端口参数：

```cpp
#include "PixelStreamingServers.h"

using namespace UE::PixelStreamingServers;

TSharedPtr<IServer> Server = MakeCirrusServer();

FLaunchArgs LaunchArgs;
// 通过 --key=value 格式传递参数给 Cirrus 进程
LaunchArgs.ProcessArgs = TEXT("--SignallingPort=8888 --HttpPort=80");
LaunchArgs.bPollUntilReady = true;
LaunchArgs.ReconnectionTimeoutSeconds = 60.0f;

Server->OnReady.AddLambda([WeakServer = TWeakPtr<IServer>(Server)](const FEndpoints& Endpoints) {
    // 获取 Streamer 信令端点
    if (const FURL* StreamerUrl = Endpoints.Find(EEndpoint::Signalling_Streamer))
    {
        UE_LOG(LogTemp, Log, TEXT("Streamer signalling: %s"), *StreamerUrl->ToString());
    }
    // 获取 Player 信令端点
    if (const FURL* PlayerUrl = Endpoints.Find(EEndpoint::Signalling_Players))
    {
        UE_LOG(LogTemp, Log, TEXT("Player signalling: %s"), *PlayerUrl->ToString());
    }
});

Server->OnFailedToReady.AddLambda([]() {
    UE_LOG(LogTemp, Error, TEXT("Cirrus server failed"));
});

Server->Launch(LaunchArgs);

// 查询连接的 Streamer 数量
Server->GetNumStreamers([](uint16 NumStreamers) {
    UE_LOG(LogTemp, Log, TEXT("Connected streamers: %d"), NumStreamers);
});

// 停止服务器
Server->Stop();
```

## Demo 示例

一个完整的最小示例：在游戏启动时启动信令服务器，在关闭时停止。

```cpp
// MyGameMode.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "PixelStreamingServers.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<UE::PixelStreamingServers::IServer> SignallingServer;
};
```

```cpp
// MyGameMode.cpp
#include "MyGameMode.h"

using namespace UE::PixelStreamingServers;

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 创建嵌入式 C++ 信令服务器
    SignallingServer = MakeSignallingServer();

    // 监听就绪事件
    SignallingServer->OnReady.AddLambda([](const FEndpoints& Endpoints) {
        if (const FURL* Url = Endpoints.Find(EEndpoint::Signalling_Streamer))
        {
            UE_LOG(LogTemp, Log, TEXT("Pixel Streaming 信令服务器已就绪: %s"), *Url->ToString());
        }
    });

    // 启动服务器
    FLaunchArgs LaunchArgs;
    LaunchArgs.bPollUntilReady = true;
    LaunchArgs.ReconnectionTimeoutSeconds = 30.0f;
    SignallingServer->Launch(LaunchArgs);
}

void AMyGameMode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (SignallingServer.IsValid())
    {
        SignallingServer->Stop();
        SignallingServer.Reset();
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 `PixelStreamingServers.Build.cs` 分析，该模块的依赖为标准基础依赖，无特殊外部依赖。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复 PIE/模拟模式下的崩溃问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片相关资产分类调整和迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString 双模式 |

### 维护评价

Pixel Streaming 插件整体处于**活跃维护**状态：

- **创建时间**：2019 年 10 月，从 Experimental 文件夹迁移到 Media 分类，已脱离实验阶段
- **更新频率**：近期（2026 年 5 月）有密集更新，包括 bug 修复、编译警告修复和代码重构
- **活跃度**：作为 Epic Games 的核心流媒体解决方案，持续获得官方维护
- **架构演进**：近期 commit 中出现了 "PixelStreaming2" 标记，表明 Epic 正在进行新一代架构的开发
- **注意事项**：插件默认不启用（`EnabledByDefault=false`），需要手动启用；原生 C++ 信令服务器不支持 SFU、Matchmaker 和内嵌 Webserver，如需这些功能需使用 Cirrus 子进程方案

**推荐使用**。作为 UE 官方的流媒体解决方案，适用于云游戏、远程渲染、虚拟制片等场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)