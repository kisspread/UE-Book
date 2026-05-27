# Pixel Streaming Player

> Support for receiving a pixel streaming stream and displaying it in game.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流播放器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体资产） |
| 模块 | `PixelStreamingPlayer` (Runtime), `PixelStreamingPlayerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer) | |

## 用途

这个插件为客户端（播放器）提供了从**像素流服务器**接收和渲染视频流的能力。它封装了信令连接（Signalling）和WebRTC对等连接（Peer Connection）的复杂性，将其转化为蓝图友好的组件，使得在游戏客户端中集成像素流播放功能变得简单。它解决的核心问题是：如何让一个运行在低性能设备（如移动设备、瘦客户端）上的游戏客户端，通过网络实时接收并播放由高性能服务器渲染并编码的视频画面。

## 使用场景

- 你的项目需要运行在性能受限的设备上（例如手机、平板、低端PC），但希望体验高画质的3A级游戏内容。→ 使用此插件在客户端接收并播放由远程服务器渲染的像素流。
- 你正在开发一个云游戏平台或类似的串流服务，需要一个轻量级的客户端模块来接入像素流服务。
- 你需要将另一个应用程序（如CAD查看器、数据分析工具）的实时画面嵌入到你的UE游戏或应用中。

## 蓝图用法

插件主要通过两个核心Actor组件提供功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect` | 连接到指定的信令服务器 | `UPixelStreamingSignallingComponent` |
| `Disconnect` | 断开与信令服务器的连接 | `UPixelStreamingSignallingComponent` |
| `Subscribe` | 向信令服务器发送订阅请求，以接收特定的视频流 | `UPixelStreamingSignallingComponent` |
| `Unsubscribe` | 取消订阅当前视频流 | `UPixelStreamingSignallingComponent` |
| `SetConfig` | 为对等连接设置RTC配置（通常从信令服务器的`OnConfig`事件获取） | `UPixelStreamingPeerComponent` |
| `CreateOffer` | 创建一个WebRTC Offer，用于向流媒体服务器请求媒体流 | `UPixelStreamingPeerComponent` |
| `CreateAnswer` | 基于收到的Offer创建WebRTC Answer | `UPixelStreamingPeerComponent` |
| `ReceiveAnswer` | 接收并处理来自流媒体服务器的Answer | `UPixelStreamingPeerComponent` |
| `GetStreamerIdList` | 异步获取当前信令服务器上可用的流媒体ID列表 | `UAsyncAction_GetStreamers` (蓝图异步节点) |

### 使用示例（蓝图描述）

1. **建立信令连接**：在你的Actor中添加 `UPixelStreamingSignallingComponent`。调用 `Connect` 节点，输入信令服务器的URL（如 `ws://127.0.0.1:80`）。绑定 `OnConnected` 事件。
2. **初始化对等连接**：在同一个Actor中添加 `UPixelStreamingPeerComponent`。在信令连接成功后（`OnConnected`事件），调用 `PeerComponent` 的 `SetConfig` 节点，传入信令服务器通过 `OnConfig` 事件发来的 `RTCConfig`。
3. **订阅并开始流传输**：调用信令组件的 `Subscribe` 节点，传入你想要订阅的 `StreamerId`。当收到信令服务器发来的 `OnOffer` 事件时，将Offer字符串传递给对等组件的 `CreateAnswer` 节点。然后，将生成的Answer通过信令组件的 `SendAnswer` 节点发回。同时，将对等组件的 `OnIceCandidate` 事件连接到信令组件的 `SendIceCandidate` 节点。
4. **渲染视频**：在对等组件上，设置 `VideoSink` 属性，指向一个 `UPixelStreamingMediaTexture` 资产。当对等连接建立（`OnIceConnection` 事件触发）后，该纹理将开始接收并渲染来自服务器的视频帧。你可以将此纹理用于UI的Image控件或3D物体的材质。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingSignallingComponent.h"
#include "PixelStreamingPeerComponent.h"
#include "PixelStreamingMediaTexture.h"
```

### 基本用法

基于头文件分析，以下是C++中创建和使用组件的基本流程。

```cpp
// MyStreamingActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyStreamingActor.generated.h"

class UPixelStreamingSignallingComponent;
class UPixelStreamingPeerComponent;
class UPixelStreamingMediaTexture;

UCLASS()
class AMyStreamingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyStreamingActor();

    UFUNCTION(BlueprintCallable)
    void StartStreaming(const FString& SignallingUrl, const FString& StreamerId);

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UPixelStreamingSignallingComponent> SignallingComp;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UPixelStreamingPeerComponent> PeerComp;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UPixelStreamingMediaTexture> MediaTexture;
};
```

```cpp
// MyStreamingActor.cpp
#include "MyStreamingActor.h"
#include "PixelStreamingSignallingComponent.h"
#include "PixelStreamingPeerComponent.h"
#include "PixelStreamingMediaTexture.h"

AMyStreamingActor::AMyStreamingActor()
{
    PrimaryActorTick.bCanEverTick = false;

    SignallingComp = CreateDefaultSubobject<UPixelStreamingSignallingComponent>(TEXT("Signalling"));
    PeerComp = CreateDefaultSubobject<UPixelStreamingPeerComponent>(TEXT("Peer"));
    // MediaTexture通常作为资产引用或动态创建，这里示意创建。
    MediaTexture = CreateDefaultSubobject<UPixelStreamingMediaTexture>(TEXT("MediaTexture"));

    // 关联视频接收器
    PeerComp->VideoSink = MediaTexture;
}

void AMyStreamingActor::StartStreaming(const FString& SignallingUrl, const FString& StreamerId)
{
    // 1. 绑定信令事件（示意，实际需绑定Delegates）
    SignallingComp->OnConnected.AddDynamic(this, &AMyStreamingActor::HandleSignallingConnected);
    SignallingComp->OnConfig.AddDynamic(this, &AMyStreamingActor::HandleSignallingConfig);
    SignallingComp->OnOffer.AddDynamic(this, &AMyStreamingActor::HandleSignallingOffer);
    SignallingComp->OnIceCandidate.AddDynamic(this, &AMyStreamingActor::HandleSignallingIceCandidate);

    // 2. 连接信令服务器
    SignallingComp->Connect(SignallingUrl);

    // 保存StreamerId供后续使用
    PendingStreamerId = StreamerId;
}

// 假设的事件处理函数
void AMyStreamingActor::HandleSignallingConnected()
{
    // 连接成功后订阅流
    SignallingComp->Subscribe(PendingStreamerId);
}

void AMyStreamingActor::HandleSignallingConfig(const FPixelStreamingRTCConfigWrapper& Config)
{
    // 收到服务器配置后，设置本地对等连接
    PeerComp->SetConfig(Config);
}

void AMyStreamingActor::HandleSignallingOffer(const FPixelStreamingSessionDescriptionWrapper& Offer)
{
    // 收到Offer后创建Answer并发送回去
    FPixelStreamingSessionDescriptionWrapper Answer = PeerComp->CreateAnswer(Offer.SDP);
    SignallingComp->SendAnswer(Answer);
}

void AMyStreamingActor::HandleSignallingIceCandidate(const FPixelStreamingIceCandidateWrapper& Candidate)
{
    // 收到远端ICE候选后，添加到本地对等连接
    PeerComp->ReceiveIceCandidate(Candidate);
}
```

## Demo 示例

一个最小化的C++ Actor示例，它完成了从信令连接到视频渲染的完整流程。

**MyPixelStreamingPlayer.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyPixelStreamingPlayer.generated.h"

class UPixelStreamingSignallingComponent;
class UPixelStreamingPeerComponent;

UCLASS(Blueprintable)
class AMyPixelStreamingPlayer : public AActor
{
    GENERATED_BODY()

public:
    AMyPixelStreamingPlayer();

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UPixelStreamingSignallingComponent> Signalling;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UPixelStreamingPeerComponent> Peer;

    UFUNCTION(BlueprintCallable)
    void JoinStream(const FString& ServerUrl, const FString& StreamId);

private:
    UFUNCTION()
    void OnSignallingConnected();

    UFUNCTION()
    void OnSignallingConfig(const FPixelStreamingRTCConfigWrapper& Config);

    UFUNCTION()
    void OnSignallingOffer(const FPixelStreamingSessionDescriptionWrapper& Offer);

    UFUNCTION()
    void OnPeerIceCandidate(const FPixelStreamingIceCandidateWrapper& Candidate);

    FString TargetStreamerId;
};
```

**MyPixelStreamingPlayer.cpp**
```cpp
#include "MyPixelStreamingPlayer.h"
#include "PixelStreamingSignallingComponent.h"
#include "PixelStreamingPeerComponent.h"
#include "PixelStreamingMediaTexture.h"

AMyPixelStreamingPlayer::AMyPixelStreamingPlayer()
{
    PrimaryActorTick.bCanEverTick = false;

    Signalling = CreateDefaultSubobject<UPixelStreamingSignallingComponent>(TEXT("Signalling"));
    Peer = CreateDefaultSubobject<UPixelStreamingPeerComponent>(TEXT("Peer"));
}

void AMyPixelStreamingPlayer::JoinStream(const FString& ServerUrl, const FString& StreamId)
{
    TargetStreamerId = StreamId;

    // 绑定关键事件
    Signalling->OnConnected.AddDynamic(this, &AMyPixelStreamingPlayer::OnSignallingConnected);
    Signalling->OnConfig.AddDynamic(this, &AMyPixelStreamingPlayer::OnSignallingConfig);
    Signalling->OnOffer.AddDynamic(this, &AMyPixelStreamingPlayer::OnSignallingOffer);
    Peer->OnIceCandidate.AddDynamic(this, &AMyPixelStreamingPlayer::OnPeerIceCandidate);

    // 发起连接
    Signalling->Connect(ServerUrl);
}

void AMyPixelStreamingPlayer::OnSignallingConnected()
{
    // 连接建立后立即订阅目标流
    Signalling->Subscribe(TargetStreamerId);
}

void AMyPixelStreamingPlayer::OnSignallingConfig(const FPixelStreamingRTCConfigWrapper& Config)
{
    // 使用服务器提供的配置初始化对等连接
    Peer->SetConfig(Config);
}

void AMyPixelStreamingPlayer::OnSignallingOffer(const FPixelStreamingSessionDescriptionWrapper& Offer)
{
    // 为收到的Offer生成Answer
    FPixelStreamingSessionDescriptionWrapper Answer = Peer->CreateAnswer(Offer.SDP);
    Signalling->SendAnswer(Answer);
}

void AMyPixelStreamingPlayer::OnPeerIceCandidate(const FPixelStreamingIceCandidateWrapper& Candidate)
{
    // 将本地生成的ICE候选发送给信令服务器
    Signalling->SendIceCandidate(Candidate);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 插件的核心依赖，提供了WebRTC通信、信令协议等底层实现 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 为多个渲染相关的头文件补充了缺失的包含和前置声明。 |
| 2025-08-26 | `0a8b2cd9` | Deprecating the functions RHICreateTextureReference and RHIUpdateTextureReference to force callers t | 废弃了RHI纹理引用相关函数，推动调用方转向新接口。 |
| 2025-04-10 | `ea97db60` | Movie Render Queue: High-res tiling support for paging scene view state persistent data to system m | 为高分辨率分块渲染添加了系统内存分页支持。 |
| 2024-09-04 | `ffe80807` | [PixelStreaming] Fix: Undeprecate as VCam is still depending on it | 撤销了一个API的废弃标记，因为虚拟摄像机（VCam）仍在依赖它。 |

### 维护评价

该插件创建于2023年初，仍处于**实验性阶段**（`IsBetaVersion=true`）且默认禁用。从Git历史看，最近的更新集中在底层的渲染和编译兼容性修复（如处理废弃API、补充头文件），而非功能性增强。这表明它**仍处于维护状态**，但开发重心可能在于保持其在新引擎版本中的可编译性，而非积极添加新功能。鉴于其“实验性”状态和有限的更新，**建议谨慎用于生产环境**。它更适合作为概念验证或内部研究项目中的快速集成方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)