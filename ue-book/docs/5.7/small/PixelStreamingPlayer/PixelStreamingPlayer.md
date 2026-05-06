# Pixel Streaming Player

> Support for receiving a pixel streaming stream and displaying it in game.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流接收器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreamingPlayer` (Runtime), `PixelStreamingPlayerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PixelStreamingPlayer) | |

---

## 用途

Pixel Streaming Player 是一个实验性插件，用于**在游戏客户端中**接收并渲染来自 Pixel Streaming 发射器的视频流。

它提供了蓝图驱动的信令连接组件（`UPixelStreamingSignallingComponent`）和对等连接组件（`UPixelStreamingPeerComponent`），以及一个可动态更新的纹理对象（`UPixelStreamingMediaTexture`），让开发者无需编写 C++ 代码即可快速搭建 **WebRTC 的接收端**。简而言之，这是 Pixel Streaming 技术栈中的“观众”端实现。

---

## 使用场景

- 你想在游戏内观看另一个 UE 实例的实时画面（例如直播、监控、协作场景）。
- 需要为 Pixel Streaming 工作流创建自定义的客户端逻辑，但又不想深入 C++ 的 WebRTC 细节。
- 开发基于 UE 的远程桌面或远程协助应用，接收端使用本插件提供的组件。
- 在蓝图层快速原型化 Pixel Streaming 接收功能，然后迁移到 C++ 进行性能优化。

---

## 蓝图用法

所有核心功能均暴露为裸蓝图节点，无需 C++ 知识即可串联。

### 核心组件

| 组件 | 说明 |
|---|---|
| `PixelStreaming Signalling Component` | 管理与信令服务器的 WebSocket 连接，收发 SDP、ICE 候选等消息。 |
| `PixelStreaming Peer Component` | 管理 WebRTC 对等连接，创建/处理 Offer/Answer，接收视频流。 |
| `PixelStreaming Media Texture` | 动态纹理，自动接收对等连接传来的视频帧，可直接入材质。 |

### 主要节点

#### 信号连接组

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect` | 连接到指定 URL 的信令服务器。如果关联了 MediaSource，URL 将从那里读取。 | `UPixelStreamingSignallingComponent` |
| `Disconnect` | 断开与信令服务器的连接。 | 同上 |
| `Subscribe` | 向服务器订阅指定 ID 的发射器（Streamer）。 | 同上 |
| `Unsubscribe` | 取消订阅当前发射器。 | 同上 |
| `Send Offer` | 将对等连接生成的 Offer SDP 发送给信令服务器。 | 同上 |
| `Send Answer` | 将对等连接生成的 Answer SDP 发送给信令服务器。 | 同上 |
| `Send Ice Candidate` | 将对等连接生成的 ICE 候选发送给信令服务器。 | 同上 |

#### 对等连接组

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Config` | 设置 WebRTC 的 RTCConfiguration（通常来自信令服务器的 OnConfig 事件）。 | `UPixelStreamingPeerComponent` |
| `Create Offer` | 创建一个新的 SDP Offer 对象（返回给信号组件发送）。 | 同上 |
| `Create Answer` | 根据收到的 Offer 创建 Answer 对象。 | 同上 |
| `Receive Answer` | 收到信令服务器转发的 Answer 后，将其填入对等连接。 | 同上 |
| `Receive Ice Candidate` | 收到信令服务器转发的 ICE 候选后，填入对等连接。 | 同上 |

#### 流媒体列表获取

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Streamer Id List` | 异步获取当前信令服务器可用的发射器 ID 列表。需要先建立信号连接。 | `UAsyncAction_GetStreamers` |

### 事件绑定（蓝图可指派）

在信号组件上绑定以下事件：

- `On Connected` – 连接成功
- `On Connection Error` – 连接失败
- `On Disconnected` – 连接断开
- `On Config` – 收到 RTC 配置（在此事件中调用 Peer Component 的 SetConfig）
- `On Offer` – 收到远程 Offer（在此事件中调用 Peer Component 的 ReceiveAnswer / CreateAnswer）
- `On Answer` – 收到远程 Answer（在此事件中调用 Peer Component 的 CreateOffer / ReceiveAnswer）
- `On Ice Candidate` – 收到远程 ICE 候选（在此事件中调用 Peer Component 的 ReceiveIceCandidate）

在 Peer 组件上绑定：

- `On Ice Candidate` – 本地生成 ICE 候选（在此事件中调用信号组件的 SendIceCandidate）
- `On Ice Connection` – ICE 连接状态变更（可据此开启/关闭视频纹理）
- `On Ice Disconnection` – ICE 连接中断

---

## 使用示例（蓝图流程）

1. 创建一个 Actor，添加一个 `PixelStreaming Signalling Component` 和一个 `PixelStreaming Peer Component`。
2. 在信号组件的事件图中：
   - **On Config** → 调用 Peer Component 的 `Set Config`，传入收到的 Config 对象。
   - **On Offer** → 调用 Peer Component 的 `Create Answer`，然后将返回的 Answer 通过信号组件的 `Send Answer` 发送给服务器。
   - **On Answer** → 调用 Peer Component 的 `Receive Answer`。
   - **On Ice Candidate** → 调用 Peer Component 的 `Receive Ice Candidate`。
3. 在 Peer 组件的事件图中：
   - **On Ice Candidate** → 调用信号组件的 `Send Ice Candidate`。
   - **On Ice Connection** → 当值大于 0 时，表示连接建立，可以开始渲染视频。
4. 创建一个 `PixelStreaming Media Texture` 资源，并在 Peer 组件的 Details 面板中将其赋给 `Video Sink` 属性。
5. 将 Media Texture 直接拖入材质编辑器作为纹理，应用到某个材质上（例如 UI 或 3D 平面）。
6. 在 BeginPlay 中调用信号组件的 `Connect`，传入信令服务器地址。
7. 连接成功后，调用 `Get Streamer Id List`（异步节点）获取发射器列表，选择目标发射器后调用 `Subscribe`。

---

## C++ 用法

本插件设计为优先面向蓝图，但核心类均可通过 C++ 直接操作。

### 头文件引入

```cpp
#include "PixelStreamingSignallingComponent.h"
#include "PixelStreamingPeerComponent.h"
#include "PixelStreamingMediaTexture.h"
#include "PixelStreamingWebRTCWrappers.h"
#include "AsyncActionGetStreamers.h"
```

### 基本用法

以下示例创建一个 Actor 并手动建立连接（来源：`PixelStreamingPlayerEditor` 下的测试资源及头文件分析）。

```cpp
// 在某个 Actor 的头文件中
UPROPERTY(EditAnywhere, Category = "PixelStreaming")
UPixelStreamingSignallingComponent* SignallingComponent;

UPROPERTY(EditAnywhere, Category = "PixelStreaming")
UPixelStreamingPeerComponent* PeerComponent;

UPROPERTY(EditAnywhere, Category = "PixelStreaming")
UPixelStreamingMediaTexture* MediaTexture;   // 创建并赋给 PeerComponent 的 VideoSink

// 在 BeginPlay 中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建组件（如果未在蓝图中创建）
    if (!SignallingComponent)
        SignallingComponent = NewObject<UPixelStreamingSignallingComponent>(this);

    if (!PeerComponent)
        PeerComponent = NewObject<UPixelStreamingPeerComponent>(this);

    if (!MediaTexture)
        MediaTexture = NewObject<UPixelStreamingMediaTexture>(this);

    // 2. 绑定事件
    SignallingComponent->OnConfig.AddDynamic(this, &AMyActor::OnConfigReceived);
    SignallingComponent->OnOffer.AddDynamic(this, &AMyActor::OnOfferReceived);
    // ... 其他事件绑定

    PeerComponent->OnIceCandidate.AddDynamic(this, &AMyActor::OnLocalIceCandidate);
    PeerComponent->OnIceConnection.AddDynamic(this, &AMyActor::OnIceStateChanged);

    // 3. 连接服务器
    SignallingComponent->Connect(TEXT("ws://your-signalling-server:8888"));
}

// 处理配置
void AMyActor::OnConfigReceived(FPixelStreamingRTCConfigWrapper Config)
{
    PeerComponent->SetConfig(Config);
}

// 收到远程 Offer，创建 Answer 并发送
void AMyActor::OnOfferReceived(const FString& OfferSDP)
{
    FPixelStreamingSessionDescriptionWrapper Answer = PeerComponent->CreateAnswer(OfferSDP);
    SignallingComponent->SendAnswer(Answer);
}

// 本地候选发送
void AMyActor::OnLocalIceCandidate(const FPixelStreamingIceCandidateWrapper& Candidate)
{
    SignallingComponent->SendIceCandidate(Candidate);
}
```

### 进阶用法

- **异步获取发射器列表**：使用 `UAsyncAction_GetStreamers` 的节点化方式，C++ 中可监听其 `Completed` 委托获取结果。
- **自定义 WebRTC 配置**：`FPixelStreamingRTCConfigWrapper` 可直接操作底层的 `webrtc::PeerConnectionInterface::RTCConfiguration`，适用于高级用户。
- **视频纹理更新**：`UPixelStreamingMediaTexture` 实现了 `FPixelStreamingVideoSink` 接口，每当收到帧即触发纹理更新，不需要手动轮询。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreaming` (Runtime) | 提供底层 WebRTC 对等连接、信号连接、视频接收等核心基础设施。本插件的几乎所有功能都建立在此之上。 |

其余依赖均为标准 UE 模块（如 Core、Engine、RHI、MediaUtils 等），无需额外关注。

---

## 维护状态

### 近期更新

| 日期 | Hash | Commit 解读 |
|---|---|---|
| 2025-08-26 | `0a8b2cd9` | 弃用 `RHICreateTextureReference` 和 `RHIUpdateTextureReference`，强制调用迁移 |
| 2025-04-10 | `ea97db60` | Movie Render Queue 的 High-res tiling 支持（与本插件无关） |
| 2024-09-04 | `ffe80807` | [PixelStreaming] 取消弃用以支持 VCam（本插件依然依赖旧 API） |
| 2024-09-04 | `27591f5e` | 引入 PixelStreaming2（第二代像素流送），本插件可能与新架构共存或迁移中 |
| 2024-03-15 | `b630cc23` | 移除 Media 模块中 `FRHICommandListExecutor::GetImmediateCommandList()` 的使用（初始创建） |

### 维护评价

- **创建时间**：2024-03-15，距今约 1.5 年。
- **活跃度**：2025 年仍有编译修复（纹理引用弃用），但无功能性更新。2024 年 9 月引入 PixelStreaming2 后，本插件未跟进新架构，可能处于过渡期。
- **实验性状态**：`IsBetaVersion=true`，官方明确标记为实验性。
- **已知限制**：
  - 仅支持 Win64/Linux 平台，目标不能是 Server。
  - 依赖于旧的 `PixelStreaming` 插件，当 PixelStreaming2 成为默认后可能被废弃。
  - 蓝图节点较多，但缺少官方示例资源和文档。
- **推荐使用**：对于需要快速原型 Pixel Streaming 接收端的项目，这是一个便捷的蓝图化方案。但请注意其实验性质，建议在生产项目前评估长期维护成本。若使用 PixelStreaming2，请考虑直接使用其提供的原生 API。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PixelStreamingPlayer)
- [官方 Pixel Streaming 文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例（PixelStreamingPlayerEditor 模块下）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PixelStreamingPlayer/Source/PixelStreamingPlayerEditor)