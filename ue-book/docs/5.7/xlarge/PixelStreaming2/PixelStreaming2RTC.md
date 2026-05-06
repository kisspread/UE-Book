# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图组件、媒体纹理资产、材质模板） |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Epic Games 开发的下一代像素流送解决方案，基于 **EpicRtc** 实时通信引擎（取代了第一代使用的 WebRTC C++ API）。它允许将 Unreal Engine 的渲染帧和音频实时编码、打包并通过 WebSocket 信令服务器分发给任意 WebRTC 兼容的浏览器或客户端。

与第一代相比，PixelStreaming2 拥有更清晰的模块划分、更健壮的错误处理、更低的延迟以及对硬件编码器的更佳集成。它同时支持**推流（Streaming）**和**拉流（Subscribing）**——即 UE 既可以作为流媒体服务器向客户端推流，也可以作为客户端订阅另一个 Streamer 的流（多用户协作、远程渲染）。

## 使用场景

- **远程实时协作**：多位设计师或开发者在不同地点同时查看同一场景的高质量渲染。
- **云游戏 / 交互式展示**：在无法本地运行 UE 的设备（如手机、平板、低压笔记本）上通过浏览器低延迟操控高保真应用。
- **XR 远程渲染**：将 VR/AR 渲染卸载到服务器，头显仅负责解码显示。
- **直播 / 教学演示**：将 UE 内容实时推送到直播平台或内部工具。

## 蓝图用法

本插件基于 PixelStreaming2RTC 模块暴露了许多可直接在蓝图中使用的组件和接口。核心可编程组件为 **UPixelStreaming2Peer**，它是一个音频合成组件（USynthComponent），可以附加到 Actor 上，负责连接信令服务器、订阅流并渲染音频/视频。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect (Url)` | 连接到指定的信令服务器 URL | `UPixelStreaming2Peer` |
| `Disconnect` | 断开当前连接 | `UPixelStreaming2Peer` |
| `Subscribe (StreamerId)` | 订阅指定 Streamer 的音频/视频流 | `UPixelStreaming2Peer` |
| `On Streamer List` (委托) | 当服务器返回可用 Streamer 列表时触发，传出 `TArray<FString>` Streamer 名称 | `UPixelStreaming2Peer` |

### 使用示例

1. **获取可用流列表**：在关卡蓝图中拖入 `BeginPlay`，连接到自行部署的信令服务器（如 `ws://your-signal-server:8888`）。连接成功后，服务器会发出 `On Streamer List` 事件，你可以从中选择一个 Streamer 名称（例如 `"MyUEStreamer"`）。
2. **订阅流**：从 `On Streamer List` 获取的数组中选择一项，调用 `Subscribe`。该组件会自动向该 Streamer 请求视频/音频轨道。
3. **显示视频**：在组件属性中设置 `Video Consumer` 为任意 `UPixelStreaming2MediaTexture` 资产，视频帧将自动送入该纹理。您可以将该纹理用于 UMG 或 3D 材质。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreaming2RTC.h"              // 模块入口
#include "PixelStreaming2/EpicRtcStreamer.h" // 核心 Streamer 类
#include "PixelStreaming2/Blueprints/PixelStreaming2Peer.h" // 蓝图组件 C++ 访问
```

### 基本用法

**创建并启动 Streamer 推流**（来自 `EpicRtcStreamer` 的典型流程）

```cpp
// 在自定义的 Module/Singleton 中
#include "IPixelStreaming2RTCModule.h"
#include "PixelStreaming2EpicRtcStreamer.h"

void MyClass::StartStreaming()
{
    // 获取 RTC 模块
    IPixelStreaming2RTCModule* RTCModule = FModuleManager::Get().LoadModulePtr<IPixelStreaming2RTCModule>("PixelStreaming2RTC");
    if (!RTCModule) return;

    // 创建一个 Streamer（ID 任意，需唯一）
    TSharedPtr<UE::PixelStreaming2::FEpicRtcStreamer> Streamer = RTCModule->CreateStreamer(TEXT("MyStreamer"));

    // 设置视频源（可以是场景捕获、视图端口等）
    auto VideoProducer = MakeShared<FMyVideoProducer>();
    Streamer->SetVideoProducer(VideoProducer);

    // 连接信令服务器并开始推流
    Streamer->SetConnectionURL(TEXT("ws://signalling-host:8888"));
    Streamer->StartStreaming();
}
```

**作为客户端订阅流**（参考 `UPixelStreaming2Peer` 的实现）

```cpp
// 创建一个 UPixelStreaming2Peer 对象（需要附加到 Actor）
UPixelStreaming2Peer* Peer = NewObject<UPixelStreaming2Peer>(GetOwner());
Peer->RegisterComponent(); // 如果作为组件

// 设置视频输出纹理
UPixelStreaming2MediaTexture* Texture = NewObject<UPixelStreaming2MediaTexture>();
Peer->VideoConsumer = Texture;

// 连接并订阅
if (Peer->Connect(TEXT("ws://signalling-host:8888")))
{
    // 等待 OnStreamerList 事件触发，然后调用
    Peer->Subscribe(TEXT("RemoteStreamerName"));
}
```

### 进阶用法

**手动创建音频/视频轨道观察者**（用于自定义处理入站数据）

```cpp
#include "EpicRtcAudioTrackObserver.h"
#include "EpicRtcVideoTrackObserver.h"
#include "EpicRtcAudioTrackObserverFactory.h"

using namespace UE::PixelStreaming2;

// 自定义观察者实现
class FMyAudioObserver : public IPixelStreaming2AudioTrackObserver
{
    void OnAudioTrackMuted(EpicRtcAudioTrackInterface*, EpicRtcBool) override {}
    void OnAudioTrackFrame(EpicRtcAudioTrackInterface*, const EpicRtcAudioFrame& Frame) override
    {
        // 处理音频帧
    }
    void OnAudioTrackState(EpicRtcAudioTrackInterface*, const EpicRtcTrackState) override {}
};

// 创建工厂并传递给 FEpicRtcAudioTrackObserverFactory
TSharedPtr<FMyAudioObserver> Observer = MakeShared<FMyAudioObserver>();
TObserverVariant<IPixelStreaming2AudioTrackObserver> Variant = TObserver(TWeakPtr<IPixelStreaming2AudioTrackObserver>(Observer));
FEpicRtcAudioTrackObserverFactory Factory(Variant);

// 将工厂注册到 RTC 模块
RTCModule->SetAudioTrackObserverFactory(&Factory);
```

**自定义 WebSocket 连接**（使用 EpicRtcWebsocket 工厂）

```cpp
#include "EpicRtcWebsocketFactory.h"

FEpicRtcWebsocketFactory WebsocketFactory(/*bSendKeepAlive=*/true);
EpicRtcWebsocketInterface* WebSocket = nullptr;
WebsocketFactory.CreateWebsocket(&WebSocket);
// WebSocket 现在可以连接任意 URL
```

## Demo 示例

一个最小化的独立 C++ 类，演示作为客户端连接并订阅流：

**PixelStreaming2Subscriber.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PixelStreaming2Subscriber.generated.h"

UCLASS(ClassGroup=(PixelStreaming2), meta=(BlueprintSpawnableComponent))
class UPixelStreaming2Subscriber : public UActorComponent
{
    GENERATED_BODY()

public:
    // 要连接的信令服务器 URL
    UPROPERTY(EditAnywhere, Category="Pixel Streaming 2")
    FString SignallingURL = TEXT("ws://localhost:8888");

    // 要订阅的 Streamer 名称
    UPROPERTY(EditAnywhere, Category="Pixel Streaming 2")
    FString StreamerName = TEXT("DefaultStreamer");

    // 视频输出纹理（可选）
    UPROPERTY(EditAnywhere, Category="Pixel Streaming 2")
    TObjectPtr<class UPixelStreaming2MediaTexture> VideoTexture;

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TObjectPtr<class UPixelStreaming2Peer> Peer;
};
```

**PixelStreaming2Subscriber.cpp**
```cpp
#include "PixelStreaming2Subscriber.h"
#include "PixelStreaming2/Blueprints/PixelStreaming2Peer.h"
#include "PixelStreaming2/Blueprints/PixelStreaming2MediaTexture.h"

void UPixelStreaming2Subscriber::BeginPlay()
{
    Super::BeginPlay();

    if (!Peer)
    {
        Peer = NewObject<UPixelStreaming2Peer>(GetOwner());
        Peer->RegisterComponent();
    }

    Peer->VideoConsumer = VideoTexture;

    // 绑定流列表更新事件
    Peer->OnStreamerList.AddDynamic(this, &UPixelStreaming2Subscriber::OnStreamerList);

    Peer->Connect(SignallingURL);
}

void UPixelStreaming2Subscriber::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Peer)
    {
        Peer->Disconnect();
        Peer = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}

void UPixelStreaming2Subscriber::OnStreamerList(const TArray<FString>& StreamerList)
{
    if (StreamerList.Contains(StreamerName))
    {
        Peer->Subscribe(StreamerName);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EpicRtc` | 底层实时通信引擎，提供 Conference/Session/Room 等核心接口 |
| `VulkanRHI` (仅 PixelStreaming2 模块) | 用于 Vulkan 平台下的视频捕获与编码 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, Projects, DeveloperSettings 等未列出。

其他模块（PixelStreaming2Core, PixelStreaming2Input, PixelStreaming2Servers, PixelStreaming2Settings）属于插件内部依赖，无需使用者显式引用。

## 维护状态

### 近期更新

- 2026-01-23 `a9928676` [NVCodecs, PixelStreaming2] Fixes: 修复 NVidia 编码器兼容性问题
- 2025-11-18 `d7a4d160` [AVCodecs, PixelStreaming2] Fixes: 修复音视频同步和编解码器初始化问题
- 2025-10-28 `b1db9444` [PixelStreaming2] Fix: Deadlocks in PixelStreaming2Thread
- 2025-10-17 `5c2f039d` [PS2] Fix: Non-functional public API
- 2025-10-13 `0de4d465` [PS2] Bug Fixes for 5.7

### 维护评价

- **创建时间**：2025-10-13，距今约半年。
- **更新频率**：非常活跃，几乎每月都有多次提交，且包含功能修复和性能改进。
- **活跃维护**：最近一次 commit 为 2026-01-23，仍在迭代中。
- **已知问题**：早期版本存在死锁、公共 API 失效等问题，但均已快速修复。
- **推荐使用**：作为 PixelStreaming 的下一代方案，功能完善、API 清晰，推荐在新项目中采用。需要注意它是实验性插件（默认未启用），且需要额外部署信令服务器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2RTC/Private/Tests)