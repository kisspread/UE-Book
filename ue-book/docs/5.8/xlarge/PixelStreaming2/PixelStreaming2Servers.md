# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

PixelStreaming2 是 Unreal Engine 第二代像素流送方案，替代了原有的 Pixel Streaming 插件。它通过 WebRTC 协议将 UE 的实时渲染画面和音频流式传输到浏览器等 WebRTC 兼容客户端，实现无需安装客户端即可在远程设备上体验 UE 应用。

与第一代相比，PixelStreaming2 采用了模块化架构（拆分为 9 个独立模块），并引入了 EpicRtc 作为自研 WebRTC 实现，不再直接依赖第三方 WebRTC 库。`PixelStreaming2Servers` 模块提供了一个**原生 C++ 信令服务器**（对标 Node.js 的 cirrus.js），可以在 UE 进程内直接运行信令服务器，消除了外部 Node.js 依赖。

**核心解决的问题：**
- 远程渲染：在云端 GPU 服务器运行 UE，用户通过浏览器访问
- 跨平台：无需客户端安装，支持任意 WebRTC 兼容浏览器
- 降低部署门槛：内置信令服务器，无需额外部署 Node.js 环境

## 使用场景

- **云游戏/云应用**：将 UE 游戏部署在云端 GPU 服务器上，玩家通过浏览器即点即玩
- **数字孪生/可视化**：企业级 3D 可视化应用，用户通过网页浏览器访问高保真 UE 场景
- **建筑/汽车展厅**：在展会上用平板电脑展示 UE 渲染的实时交互场景
- **VR 远程体验**：通过 PixelStreaming2HMD 模块支持 VR 头显的远程流送
- **快速原型验证**：无需配置外部信令服务器，使用内置 `MakeSignallingServer()` 即可在编辑器内快速测试流送功能

## 蓝图用法

PixelStreaming2Servers 模块的公共 API 以 C++ 为主，未暴露蓝图可调用节点。蓝图集成主要通过 `PixelStreaming2` 和 `PixelStreaming2Input` 模块提供。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreaming2Servers.h"
```

### 基本用法：启动内置信令服务器

无需依赖外部 Node.js 的 cirrus.js，直接在 UE 进程内启动原生信令服务器。

```cpp
// 来源: Public/PixelStreaming2Servers.h
#include "PixelStreaming2Servers.h"

using namespace UE::PixelStreaming2Servers;

// 创建内置信令服务器（类似 cirrus.js，但运行在 UE 进程内）
TSharedPtr<IServer> SignallingServer = MakeSignallingServer();

// 绑定就绪回调 —— 服务器启动完成并可接受连接时触发
SignallingServer->OnReady.AddLambda([](const FEndpoints& Endpoints)
{
    // 从 Endpoints 获取各个 URL
    if (const FURL* StreamerUrl = Endpoints.Find(EEndpoint::Signalling_Streamer))
    {
        UE_LOG(LogTemp, Log, TEXT("Streamer 信令端点: %s"), *StreamerUrl->ToString());
    }
    if (const FURL* PlayerUrl = Endpoints.Find(EEndpoint::Signalling_Players))
    {
        UE_LOG(LogTemp, Log, TEXT("Player 信令端点: %s"), *PlayerUrl->ToString());
    }
});

// 绑定失败回调
SignallingServer->OnFailedToReady.AddLambda([]()
{
    UE_LOG(LogTemp, Error, TEXT("信令服务器启动失败！"));
});

// 配置启动参数
FLaunchArgs LaunchArgs;
LaunchArgs.ProcessArgs = TEXT("--SignallingPort=8888 --HttpPort=80");
LaunchArgs.bPollUntilReady = true;
LaunchArgs.ReconnectionTimeoutSeconds = 30.0f;
LaunchArgs.ReconnectionIntervalSeconds = 2.0f;

// 启动服务器
bool bLaunched = SignallingServer->Launch(LaunchArgs);
```

### 进阶用法：下载外部服务器并查询流送器数量

```cpp
// 来源: Public/PixelStreaming2Servers.h + Private/ServerUtils.h
#include "PixelStreaming2Servers.h"

using namespace UE::PixelStreaming2Servers;

// 步骤 1: 下载 Pixel Streaming 服务器二进制文件（如果尚未存在）
TSharedPtr<FMonitoredProcess> DownloadProcess = DownloadPixelStreaming2Servers(/* bSkipIfPresent */ true);

// 步骤 2: 等待下载完成后，创建并启动信令服务器
TSharedPtr<IServer> Server = MakeSignallingServer();

Server->OnReady.AddLambda([ServerWeak = TWeakPtr<IServer>(Server)](const FEndpoints& Endpoints)
{
    // 步骤 3: 异步查询当前连接的流送器数量
    if (TSharedPtr<IServer> ServerPin = ServerWeak.Pin())
    {
        ServerPin->GetNumStreamers([](uint16 NumStreamers)
        {
            UE_LOG(LogTemp, Log, TEXT("当前连接了 %d 个流送器"), NumStreamers);
        });
    }
});

// 步骤 4: 检查服务器状态
if (Server->HasLaunched() && Server->IsReady())
{
    UE_LOG(LogTemp, Log, TEXT("服务器已就绪"));
}

// 步骤 5: 停止服务器（程序退出或不再需要时）
Server->Stop();
```

### 进阶用法：自定义 WebSocket 服务器

```cpp
// 来源: Private/WebSocketServerWrapper.h
#include "WebSocketServerWrapper.h"

using namespace UE::PixelStreaming2Servers;

// 创建 WebSocket 服务器包装器
TUniquePtr<FWebSocketServerWrapper> WSServer = MakeUnique<FWebSocketServerWrapper>();

// 可选：启用内置 Web 服务器（用于提供 HTML/JS 客户端页面）
FWebSocketServerCertificates Certs;
// ... 配置证书 ...
WSServer->EnableWebServer(DirectoriesToServe, /* bServeHttps */ false, Certs);

// 绑定新连接事件
WSServer->OnOpenConnection.AddLambda([](uint16 ConnectionId)
{
    UE_LOG(LogTemp, Log, TEXT("新 WebSocket 连接: %d"), ConnectionId);
});

// 绑定消息事件
WSServer->OnMessage.AddLambda([](uint16 ConnectionId, TArrayView<uint8> Message)
{
    FString MsgString = FString(UTF8_TO_TCHAR(Message.GetData()));
    UE_LOG(LogTemp, Log, TEXT("收到消息 [%d]: %s"), ConnectionId, *MsgString);
});

// 绑定断开事件
WSServer->OnClosedConnection.AddLambda([](uint16 ConnectionId)
{
    UE_LOG(LogTemp, Log, TEXT("连接断开: %d"), ConnectionId);
});

// 启动监听
WSServer->Launch(8888);

// 发送消息给特定连接
WSServer->Send(ConnectionId, TEXT("{\"type\": \"ping\"}"));

// 命名连接以便后续引用
WSServer->NameConnection(ConnectionId, TEXT("MainPlayer"));
uint16 FoundId;
if (WSServer->GetNamedConnection(TEXT("MainPlayer"), FoundId))
{
    WSServer->Send(FoundId, TEXT("{\"type\": \"hello\"}"));
}
```

## Demo 示例

一个完整的最小示例：在游戏启动时自动启动内置信令服务器。

```cpp
// MyGameMode.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "PixelStreaming2Servers.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<UE::PixelStreaming2Servers::IServer> SignallingServer;
};
```

```cpp
// MyGameMode.cpp
#include "MyGameMode.h"
#include "PixelStreaming2Servers.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    using namespace UE::PixelStreaming2Servers;

    // 创建内置信令服务器
    SignallingServer = MakeSignallingServer();
    if (!SignallingServer.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("无法创建信令服务器"));
        return;
    }

    // 绑定就绪回调
    SignallingServer->OnReady.AddLambda([](const FEndpoints& Endpoints)
    {
        UE_LOG(LogTemp, Log, TEXT("信令服务器已就绪"));
        for (const auto& Pair : Endpoints)
        {
            UE_LOG(LogTemp, Log, TEXT("  端点: %s"), *Pair.Value.ToString());
        }
    });

    // 绑定失败回调
    SignallingServer->OnFailedToReady.AddLambda([]()
    {
        UE_LOG(LogTemp, Warning, TEXT("信令服务器启动超时或连接失败"));
    });

    // 配置并启动
    FLaunchArgs Args;
    Args.ProcessArgs = TEXT("--SignallingPort=9999");
    Args.bPollUntilReady = true;
    Args.ReconnectionTimeoutSeconds = 15.0f;

    if (!SignallingServer->Launch(Args))
    {
        UE_LOG(LogTemp, Error, TEXT("信令服务器启动失败"));
    }
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

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | PixelStreaming2 主模块的渲染抓取依赖（PixelStreaming2Servers 无特殊依赖） |
| `WebSockets` | WebSocket 服务器/客户端实现（由 PixelStreaming2Servers 使用） |
| `Json` | 信令消息的 JSON 解析与构建 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器获取默认目标窗口的方法错误 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 虚拟制片资产分类调整及迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |

### 维护评价

PixelStreaming2 是 Epic Games **官方重点维护**的插件，作为 Pixel Streaming 的第二代实现，持续获得功能性更新和 Bug 修复。

- **创建时间**：2024 年 9 月，相对较新
- **活跃度**：2026 年 4-5 月仍有多个实质性的 Bug 修复和重构提交，**维护非常活跃**
- **模块化程度**：拆分为 9 个模块，架构清晰，各司其职
- **稳定性**：仍标记为 `EnabledByDefault: false`，表明 Epic 可能认为尚未完全替代第一代 Pixel Streaming，但代码质量持续提升
- **推荐度**：✅ **强烈推荐**。如果你在新项目中需要像素流送功能，应优先选择 PixelStreaming2 而非旧版。内置信令服务器（`MakeSignallingServer`）极大简化了部署流程

> ⚠️ 注意：该插件默认未启用（`EnabledByDefault: false`），需在项目设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [PixelStreaming2Servers 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2Servers)