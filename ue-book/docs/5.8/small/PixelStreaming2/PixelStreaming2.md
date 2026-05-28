# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图组件、媒体纹理、功能类） |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Unreal Engine 的下一代像素流送技术。它通过 WebRTC 协议，将引擎的实时渲染画面和音频压缩并推送到兼容的客户端（如网页浏览器），同时能够接收来自客户端的输入（鼠标、键盘、触摸、手柄等）和自定义数据。其核心是管理一个或多个“Streamer”（流送器），每个 Streamer 负责一路独立的音视频流和与一个或多个“Player”（玩家/观众）的连接。

该插件解决了在无需本地安装 UE 应用的情况下，向海量用户提供低延迟、交互式实时 3D 体验的问题，并支持多路流、自定义视频源、双向数据通道等高级功能，是构建云游戏、远程演示、虚拟制作和协作应用的关键技术。

## 使用场景

-   **云游戏/云应用**：将 UE 应用部署在云端，用户通过浏览器即可畅玩，无需下载。
-   **远程演示与评审**：设计师或开发者可以实时分享应用运行状态给远端团队成员进行观看和交互。
-   **虚拟制作**：将 UE 的实时渲染画面流送到现场监视器、LED 墙或其他设备。
-   **交互式培训与教育**：创建可交互的 3D 培训模拟器或教育内容，并通过浏览器分发。
-   **多用户协作**：多个用户可以同时连接到同一个 Streamer，查看相同或不同的视图（通过 Simulcast）。

## 蓝图用法

以下节点主要来自 `UPixelStreaming2Blueprints` 类，可直接在蓝图中调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SendResponse` | 向默认 Streamer 的所有连接玩家发送一个 JSON 格式的响应字符串。 | `UPixelStreaming2Blueprints` |
| `StreamerSendResponse` | 向指定 Streamer 的所有连接玩家发送一个 JSON 格式的响应字符串。 | `UPixelStreaming2Blueprints` |
| `SendFile` | 通过默认 Streamer 的数据通道向所有玩家发送一个文件。 | `UPixelStreaming2Blueprints` |
| `SendFileAsByteArray` | 通过默认 Streamer 的数据通道向所有玩家发送一个字节数组文件。 | `UPixelStreaming2Blueprints` |
| `ForceKeyFrame` | 强制默认 Streamer 向所有玩家发送一个关键帧。 | `UPixelStreaming2Blueprints` |
| `FreezeFrame` | 冻结默认 Streamer 的视频流，并显示指定的纹理（可选）。 | `UPixelStreaming2Blueprints` |
| `UnfreezeFrame` | 解除默认 Streamer 视频流的冻结。 | `UPixelStreaming2Blueprints` |
| `KickPlayer` | 将指定 Player 从默认 Streamer 上踢出。 | `UPixelStreaming2Blueprints` |
| `GetConnectedPlayers` | 获取连接到默认 Streamer 的所有 Player ID 列表。 | `UPixelStreaming2Blueprints` |
| `GetDefaultStreamerID` | 获取默认 Streamer 的 ID。 | `UPixelStreaming2Blueprints` |
| `GetJsonStringValue` | 从一个 JSON 字符串中提取指定字段的字符串值。 | `UPixelStreaming2Blueprints` |
| `AddJsonStringValue` | 向一个 JSON 字符串中添加一个新的字符串字段。 | `UPixelStreaming2Blueprints` |
| `GetDelegates` | 获取 `UPixelStreaming2Delegates` 单例，用于绑定各种流送事件。 | `UPixelStreaming2Blueprints` |

### 蓝图组件

| 组件 | 说明 |
|---|---|
| `UPixelStreaming2StreamerComponent` | 可附加到 Actor 上，用于创建和管理一个 Streamer 实例，控制其开始/停止流送，并监听输入。 |
| `UPixelStreaming2Input` | 可附加到 Actor 上，用于监听并处理来自特定 Streamer 的 UI 交互事件（JSON 格式）。 |
| `UPixelStreaming2AudioComponent` | 可附加到 Actor 上，用于播放来自特定 Pixel Streaming 玩家麦克风的音频。 |
| `UPixelStreaming2VideoComponent` | 可附加到 Actor 上，用于显示来自特定 Pixel Streaming 玩家摄像头的视频。 |

### 使用示例（蓝图描述）

1.  **启动流送**：在任意 Actor 蓝图中添加 `UPixelStreaming2StreamerComponent`，设置 `StreamerId` 和 `SignallingServerURL`（默认为 `ws://127.0.0.1:8888`）。在 `BeginPlay` 事件后，调用其 `StartStreaming` 节点。
2.  **监听玩家事件**：在 `UPixelStreaming2Blueprints::GetDelegates` 返回的单例对象上，绑定 `OnNewConnection`、`OnClosedConnection` 等动态多播委托，以响应玩家连接和断开。
3.  **发送自定义数据**：当需要向网页端发送数据时，使用 `SendResponse` 节点。可以使用 `AddJsonStringValue` 节点逐步构建一个 JSON 字符串，然后通过 `SendResponse` 发送。
4.  **接收玩家输入**：添加 `UPixelStreaming2Input` 组件，并绑定其 `OnInputEvent` 委托。当玩家在网页端进行交互时，此委托将被触发，并传入一个 JSON 描述符。使用 `GetJsonStringValue` 可以从中解析出需要的信息。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreaming2Module.h"
#include "PixelStreaming2Streamer.h"
#include "PixelStreaming2VideoProducer.h"
#include "PixelStreaming2Delegates.h"
```

### 基本用法

以下代码演示如何获取模块、创建 Streamer 并开始流送。
*（来源：基于 `IPixelStreaming2Module` 接口设计）*

```cpp
// 获取 Pixel Streaming 2 模块实例
if (IPixelStreaming2Module::IsAvailable())
{
    IPixelStreaming2Module& PSModule = IPixelStreaming2Module::Get();
    
    // 等待模块就绪（例如在 BeginPlay 中）
    if (PSModule.IsReady())
    {
        // 创建一个新的 Streamer
        TSharedPtr<IPixelStreaming2Streamer> MyStreamer = PSModule.CreateStreamer(TEXT("MyGameStreamer"));
        
        if (MyStreamer.IsValid())
        {
            // 配置 Streamer（可选）
            // MyStreamer->SetSignallingServerURL(TEXT("ws://192.168.1.100:8888"));
            
            // 开始流送
            bool bSuccess = PSModule.StartStreaming();
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("Pixel Streaming started successfully."));
            }
        }
    }
    else
    {
        // 绑定模块就绪事件
        PSModule.OnReady().AddLambda([](IPixelStreaming2Module& Module)
        {
            // 模块已就绪，可以安全地创建 Streamer
            TSharedPtr<IPixelStreaming2Streamer> Streamer = Module.CreateStreamer(TEXT("DefaultStreamer"));
            Module.StartStreaming();
        });
    }
}
```

### 进阶用法

#### 1. 使用自定义视频生产者

你可以创建自己的视频生产者，将任意来源的帧（如渲染到特定 RenderTarget）推送到 Pixel Streaming。
*（来源：`FVideoProducerRenderTarget`, `FVideoProducerBackBuffer` 类）*

```cpp
#include "VideoProducerRenderTarget.h"
#include "IPixelStreaming2VideoProducer.h"

// 假设你有一个 UTextureRenderTarget2D* MyRenderTarget;
TSharedPtr<IPixelStreaming2VideoProducer> CustomVideoProducer = 
    UE::PixelStreaming2::FVideoProducerRenderTarget::Create(MyRenderTarget);

// 在创建 Streamer 后，将其视频生产者替换为你自定义的生产者
TSharedPtr<IPixelStreaming2Streamer> Streamer = ...;
if (Streamer.IsValid() && CustomVideoProducer.IsValid())
{
    Streamer->SetVideoProducer(CustomVideoProducer);
}
```

#### 2. 监听并处理玩家事件

使用 `UPixelStreaming2Delegates` 来监听连接、断开、数据通道打开等事件。
*（来源：`PixelStreaming2Delegates.h`）*

```cpp
// 获取委托单例
UPixelStreaming2Delegates* Delegates = UPixelStreaming2Delegates::Get();
if (Delegates)
{
    // 绑定原生（C++）委托
    Delegates->OnNewConnectionNative.AddLambda([](const FString& StreamerId, const FString& PlayerId)
    {
        UE_LOG(LogTemp, Log, TEXT("New player connected to Streamer '%s': %s"), *StreamerId, *PlayerId);
    });
    
    Delegates->OnDataTrackOpenNative.AddLambda([](const FString& StreamerId, const FString& PlayerId)
    {
        UE_LOG(LogTemp, Log, TEXT("Data channel opened for player '%s' on Streamer '%s'."), *PlayerId, *StreamerId);
        // 此时可以向该玩家发送自定义数据
    });
    
    Delegates->OnAllConnectionsClosedNative.AddLambda([](const FString& StreamerId)
    {
        UE_LOG(LogTemp, Log, TEXT("All players disconnected from Streamer '%s'. Application can reset."), *StreamerId);
    });
}
```

#### 3. 向玩家发送数据

当数据通道打开后，可以通过 Streamer 向特定或所有玩家发送消息。
*（来源：基于 `IPixelStreaming2Streamer` 接口）*

```cpp
TSharedPtr<IPixelStreaming2Streamer> Streamer = ...;
if (Streamer.IsValid())
{
    // 发送一个 JSON 格式的字符串消息给所有玩家
    FString JsonMessage = TEXT("{\"command\": \"updateScore\", \"value\": 100}");
    Streamer->SendAllPlayersMessage(TEXT("CustomMessage"), JsonMessage);
    
    // 或者发送给特定玩家
    FString TargetPlayerId = TEXT("..."); // 从 OnNewConnection 获取
    Streamer->SendPlayerMessage(TargetPlayerId, TEXT("PrivateMessage"), TEXT("{\"data\": \"secret\"}"));
}
```

## Demo 示例

这是一个最小化的 C++ 示例，展示如何创建一个自定义的视频生产者并开始流送自定义内容。

**CustomPixelStreamingProducer.h**
```cpp
#pragma once

#include "IPixelStreaming2VideoProducer.h"
#include "VideoProducerBase.h"

class FCustomPixelStreamingProducer : public UE::PixelStreaming2::FVideoProducerBase
{
public:
    static TSharedPtr<FCustomPixelStreamingProducer> Create();
    virtual ~FCustomPixelStreamingProducer() = default;

    virtual FString ToString() override;
    virtual EVideoProducerCapabilities GetCapabilities() override;

    // 模拟推送一帧，实际应用中由渲染管线调用
    void SimulateFramePush(FTextureRHIRef Texture);

private:
    FCustomPixelStreamingProducer() = default;
};
```

**CustomPixelStreamingProducer.cpp**
```cpp
#include "CustomPixelStreamingProducer.h"

TSharedPtr<FCustomPixelStreamingProducer> FCustomPixelStreamingProducer::Create()
{
    TSharedPtr<FCustomPixelStreamingProducer> Producer(new FCustomPixelStreamingProducer());
    return Producer;
}

FString FCustomPixelStreamingProducer::ToString()
{
    return TEXT("CustomPixelStreamingProducer");
}

UE::PixelStreaming2::EVideoProducerCapabilities FCustomPixelStreamingProducer::GetCapabilities()
{
    // 表示这个生产者产生的帧可能已经过预处理
    return UE::PixelStreaming2::EVideoProducerCapabilities::ProducesPreprocessedFrames;
}

void FCustomPixelStreamingProducer::SimulateFramePush(FTextureRHIRef Texture)
{
    // 调用基类的 PushFrame 方法，将纹理推入像素流送管线
    // 注意：实际实现可能需要处理格式转换、分辨率等
    PushFrame(Texture);
}

// 在某个 Actor 或游戏模式中使用
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    if (IPixelStreaming2Module::IsAvailable())
    {
        IPixelStreaming2Module& PSModule = IPixelStreaming2Module::Get();
        if (PSModule.IsReady())
        {
            // 创建 Streamer
            TSharedPtr<IPixelStreaming2Streamer> Streamer = PSModule.CreateStreamer(TEXT("CustomStreamer"));
            
            // 创建并设置自定义视频生产者
            TSharedPtr<FCustomPixelStreamingProducer> CustomProducer = FCustomPixelStreamingProducer::Create();
            if (Streamer.IsValid() && CustomProducer.IsValid())
            {
                Streamer->SetVideoProducer(CustomProducer);
                PSModule.StartStreaming();
            }
        }
    }
}
```

## 模块依赖

要使用此插件，你的项目模块需要依赖以下 **独特** 的模块（常见依赖如 Core, Engine 等已省略）：

| 模块 | 用途 |
|---|---|
| `PixelStreaming2` | 主模块，提供核心的 `IPixelStreaming2Module` 接口和基本功能。 |
| `PixelStreaming2Input` | 处理来自 WebRTC 数据通道的输入事件。 |
| `PixelStreaming2Settings` | 管理插件相关的设置和配置变量（CVar）。 |
| `VulkanRHI` | 用于支持 Vulkan 图形 API 下的硬件编码，是硬件加速流送的依赖项之一。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复了输入处理器从错误方法获取默认目标窗口的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数引发的警告代码。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 虚拟制作：将各种 VP 资产移至不同的资产类别，并进行了迁移。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了 FJsonObject 以同时支持 FString 和 UE::FSharedString。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致垃圾输出的问题。 |

### 维护评价

-   **活跃维护**：该插件创建于 2024 年 9 月，至今约 2 年，属于较新的功能。从近期 commit 记录看，修复和优化仍在积极进行，频率较高。
-   **内容健康**：最近的更新主要是 bug 修复和代码重构，没有出现废弃（deprecated）或移除核心功能的标记。插件结构清晰，模块划分合理。
-   **推荐使用**：作为 Epic Games 官方推出的下一代像素流送解决方案，它旨在替代旧版 Pixel Streaming，拥有更好的架构和扩展性。对于新的云应用、流媒体项目，**强烈推荐使用 Pixel Streaming 2**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
-   [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)（注意：此链接指向旧版文档，Pixel Streaming 2 的官方文档链接可能尚未单独列出，但核心概念相通）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2/Tests)（如果存在，路径可能为 `Tests/` 或 `Source/.../Tests/`）