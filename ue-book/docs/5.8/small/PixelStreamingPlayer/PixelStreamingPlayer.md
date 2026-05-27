# Pixel Streaming Player

> Support for receiving a pixel streaming stream and displaying it in game.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流接收器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PixelStreamingPlayer` (Runtime), `PixelStreamingPlayerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer) | |

## 用途

该插件提供了一套蓝图友好的组件（ActorComponent），使一个UE应用程序能够作为“客户端”或“播放器”连接到另一个正在运行的像素流（Pixel Streaming）服务器，并接收其输出的视频流进行显示。它解决了在另一个UE实例中观看或控制远端像素流输出的需求，是标准像素流插件（通常作为流发送者）的对应补充。

## 使用场景

- **轻量级客户端**：在VR应用中，将高性能PC作为计算主机运行主场景，而用Quest设备作为轻量客户端接收并显示视频流。
- **多屏展示**：主屏幕运行复杂的渲染，多个副屏幕作为轻量客户端连接并显示相同的视频流。
- **自动化测试与监控**：在自动化测试中，可以启动一个独立的播放器实例来连接并监控正在运行的测试服务器。
- **混合现实应用**：接收来自另一个设备（如HoloLens）的像素流，并在其环境中叠加显示。

## 蓝图用法

该插件的核心功能通过两个ActorComponent提供，适合在蓝图中组合使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect` | 连接到指定的信令服务器 | `UPixelStreamingSignallingComponent` |
| `Disconnect` | 断开与信令服务器的连接 | `UPixelStreamingSignallingComponent` |
| `Subscribe` | 向信令服务器发送订阅特定流媒体源的消息 | `UPixelStreamingSignallingComponent` |
| `Unsubscribe` | 发送取消订阅的消息 | `UPixelStreamingSignallingComponent` |
| `SetConfig` | 设置WebRTC连接的RTC配置（通常从信令服务器的 `OnConfig` 事件获取） | `UPixelStreamingPeerComponent` |
| `CreateOffer` | 创建一个WebRTC Offer，用于开始连接协商 | `UPixelStreamingPeerComponent` |
| `CreateAnswer` | 根据收到的Offer创建WebRTC Answer | `UPixelStreamingPeerComponent` |
| `ReceiveAnswer` | 处理从流媒体源收到的Answer | `UPixelStreamingPeerComponent` |
| `ReceiveIceCandidate` | 处理ICE候选地址，用于建立P2P连接 | `UPixelStreamingPeerComponent` |

### 事件绑定

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnConnected` | 成功连接到信令服务器 | `UPixelStreamingSignallingComponent` |
| `OnConnectionError` | 连接失败或出错 | `UPixelStreamingSignallingComponent` |
| `OnDisconnected` | 连接已关闭 | `UPixelStreamingSignallingComponent` |
| `OnConfig` | 收到来自信令服务器的RTC配置（最早的初始化PeerConnection的时机） | `UPixelStreamingSignallingComponent` |
| `OnOffer` | 收到来自服务器的SDP Offer（意味着服务器有媒体要发送） | `UPixelStreamingSignallingComponent` |
| `OnAnswer` | 收到来自服务器对我们Offer的SDP Answer | `UPixelStreamingSignallingComponent` |
| `OnIceCandidate` | 收到来自服务器的ICE候选 | `UPixelStreamingSignallingComponent` |
| `OnIceConnection` | WebRTC ICE连接已建立，流媒体传输开始 | `UPixelStreamingPeerComponent` |
| `OnIceDisconnection` | ICE连接丢失 | `UPixelStreamingPeerComponent` |
| `OnIceCandidate` (Peer) | PeerConnection生成了本地ICE候选，需要发送给信令服务器 | `UPixelStreamingPeerComponent` |

### 使用示例（蓝图描述）

典型的连接流程如下：
1.  在一个Actor上添加 `UPixelStreamingSignallingComponent` 和 `UPixelStreamingPeerComponent`。
2.  调用 `SignallingComponent->Connect(Url)` 连接到信令服务器。
3.  在 `SignallingComponent->OnConfig` 事件中，将收到的 `RTCConfiguration` 传递给 `PeerComponent->SetConfig(Config)`。
4.  在 `SignallingComponent->OnOffer` 事件中，调用 `PeerComponent->CreateAnswer(OfferSdp)` 生成Answer，并通过 `SignallingComponent->SendAnswer(Answer)` 将其发送回服务器。
5.  将 `SignallingComponent` 的 `OnIceCandidate` 事件与 `PeerComponent->ReceiveIceCandidate` 节点连接。
6.  将 `PeerComponent` 的 `OnIceCandidate` 事件与 `SignallingComponent->SendIceCandidate` 节点连接。
7.  为 `PeerComponent` 指定一个 `PixelStreamingMediaTexture` 作为 `VideoSink`，该纹理可被材质使用以显示视频画面。

## C++ 用法

虽然该插件主要面向蓝图，但也提供了C++ API。

### 头文件引入

```cpp
#include "PixelStreamingSignallingComponent.h"
#include "PixelStreamingPeerComponent.h"
```

### 基本用法

在C++中动态创建和配置组件。

```cpp
// 假设在某个Actor的BeginPlay中
UPixelStreamingSignallingComponent* SignallingComp = NewObject<UPixelStreamingSignallingComponent>(this);
SignallingComp->RegisterComponent();

UPixelStreamingPeerComponent* PeerComp = NewObject<UPixelStreamingPeerComponent>(this);
PeerComp->RegisterComponent();

// 连接到信令服务器
SignallingComp->Connect(TEXT("ws://127.0.0.1:8888"));

// 绑定事件
SignallingComp->OnConfig.AddDynamic(this, &AMyActor::OnSignallingConfig);
SignallingComp->OnOffer.AddDynamic(this, &AMyActor::OnSignallingOffer);

// ...

void AMyActor::OnSignallingConfig(const FPixelStreamingRTCConfigWrapper& Config)
{
    if (PeerComp)
    {
        PeerComp->SetConfig(Config);
    }
}

void AMyActor::OnSignallingOffer(const FPixelStreamingSessionDescriptionWrapper& Offer)
{
    if (PeerComp && SignallingComp)
    {
        FPixelStreamingSessionDescriptionWrapper Answer = PeerComp->CreateAnswer(/* Offer的SDP字符串 */);
        SignallingComp->SendAnswer(Answer);
    }
}
```

### 进阶用法

异步获取可用的流媒体列表。

```cpp
#include "AsyncActionGetStreamers.h"

// 创建异步动作
UAsyncAction_GetStreamers* GetStreamersAction = UAsyncAction_GetStreamers::GetStreamerIdList(SignallingComponent);
GetStreamersAction->Completed.AddDynamic(this, &AMyActor::OnStreamerListReceived);
GetStreamersAction->Activate();

void AMyActor::OnStreamerListReceived(const TArray<FString>& StreamerIds)
{
    UE_LOG(LogTemp, Log, TEXT("Available streamers: %s"), *FString::Join(StreamerIds, TEXT(", ")));
    if (StreamerIds.Num() > 0)
    {
        SignallingComponent->Subscribe(StreamerIds[0]);
    }
}
```

## Demo 示例

一个最小的可编译的Actor，用于连接并接收像素流。

**MyPixelStreamingReceiverActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPixelStreamingReceiverActor.generated.h"

class UPixelStreamingSignallingComponent;
class UPixelStreamingPeerComponent;
class UPixelStreamingMediaTexture;
struct FPixelStreamingRTCConfigWrapper;
struct FPixelStreamingSessionDescriptionWrapper;

UCLASS()
class AMyPixelStreamingReceiverActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPixelStreamingReceiverActor();

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnSignallingConnected();

    UFUNCTION()
    void OnSignallingConfig(const FPixelStreamingRTCConfigWrapper& Config);

    UFUNCTION()
    void OnSignallingOffer(const FPixelStreamingSessionDescriptionWrapper& Offer);

    UFUNCTION()
    void OnSignallingIceCandidate(const FPixelStreamingIceCandidateWrapper& Candidate);

    UFUNCTION()
    void OnPeerIceCandidate(const FPixelStreamingIceCandidateWrapper& Candidate);

private:
    UPROPERTY(VisibleAnywhere)
    UPixelStreamingSignallingComponent* SignallingComponent;

    UPROPERTY(VisibleAnywhere)
    UPixelStreamingPeerComponent* PeerComponent;

    UPROPERTY(EditAnywhere, Category = "Config")
    FString SignallingServerURL = TEXT("ws://127.0.0.1:8888");
};
```

**MyPixelStreamingReceiverActor.cpp**
```cpp
#include "MyPixelStreamingReceiverActor.h"
#include "PixelStreamingSignallingComponent.h"
#include "PixelStreamingPeerComponent.h"
#include "PixelStreamingMediaTexture.h"

AMyPixelStreamingReceiverActor::AMyPixelStreamingReceiverActor()
{
    PrimaryActorTick.bCanEverTick = false;

    SignallingComponent = CreateDefaultSubobject<UPixelStreamingSignallingComponent>(TEXT("Signalling"));
    PeerComponent = CreateDefaultSubobject<UPixelStreamingPeerComponent>(TEXT("Peer"));
}

void AMyPixelStreamingReceiverActor::BeginPlay()
{
    Super::BeginPlay();

    // 绑定事件
    SignallingComponent->OnConnected.AddDynamic(this, &AMyPixelStreamingReceiverActor::OnSignallingConnected);
    SignallingComponent->OnConfig.AddDynamic(this, &AMyPixelStreamingReceiverActor::OnSignallingConfig);
    SignallingComponent->OnOffer.AddDynamic(this, &AMyPixelStreamingReceiverActor::OnSignallingOffer);
    SignallingComponent->OnIceCandidate.AddDynamic(this, &AMyPixelStreamingReceiverActor::OnSignallingIceCandidate);
    PeerComponent->OnIceCandidate.AddDynamic(this, &AMyPixelStreamingReceiverActor::OnPeerIceCandidate);

    // 连接到信令服务器
    SignallingComponent->Connect(SignallingServerURL);
}

void AMyPixelStreamingReceiverActor::OnSignallingConnected()
{
    UE_LOG(LogTemp, Log, TEXT("Connected to signalling server, subscribing to first available stream."));
    // 通常连接后，服务器会推送流列表或直接发送Offer。这里假设有默认流。
    // 实际项目中，可能需要使用 UAsyncAction_GetStreamers 来获取列表。
    SignallingComponent->Subscribe(TEXT("DefaultStreamer"));
}

void AMyPixelStreamingReceiverActor::OnSignallingConfig(const FPixelStreamingRTCConfigWrapper& Config)
{
    UE_LOG(LogTemp, Log, TEXT("Received RTC configuration."));
    PeerComponent->SetConfig(Config);
}

void AMyPixelStreamingReceiverActor::OnSignallingOffer(const FPixelStreamingSessionDescriptionWrapper& Offer)
{
    UE_LOG(LogTemp, Log, TEXT("Received Offer, creating Answer."));
    // 注意：示例中省略了从Offer中提取SDP字符串的步骤，实际实现需要处理。
    // FPixelStreamingSessionDescriptionWrapper Answer = PeerComponent->CreateAnswer(OfferSDP);
    // SignallingComponent->SendAnswer(Answer);
}

void AMyPixelStreamingReceiverActor::OnSignallingIceCandidate(const FPixelStreamingIceCandidateWrapper& Candidate)
{
    PeerComponent->ReceiveIceCandidate(Candidate);
}

void AMyPixelStreamingReceiverActor::OnPeerIceCandidate(const FPixelStreamingIceCandidateWrapper& Candidate)
{
    SignallingComponent->SendIceCandidate(Candidate);
}
```

## 模块依赖

该插件依赖于以下核心模块，你的项目模块需要相应地依赖它们才能使用此插件的API。

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 提供像素流的核心功能、信令连接和WebRTC接口定义 |
| `MediaUtils` | 提供媒体工具类，可能用于纹理和媒体处理 |
| `MediaAssets` | 提供媒体相关资产类型（如 `UStreamMediaSource`） |
| `WebRTC` | 提供底层的WebRTC协议实现 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到新的UE_LOGF格式。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers... | 补充渲染相关头文件缺失的包含和前向声明，以修复编译问题。 |
| 2025-08-26 | `0a8b2cd9` | Deprecating the functions RHICreateTextureReference and RHIUpdateTextureReference... | 废弃了两个RHI纹理引用函数，强制调用方更新代码。 |
| 2025-04-10 | `ea97db60` | Movie Render Queue: High-res tiling support for paging scene view state persistent data to system m... | 此插件未受影响，为其他渲染模块的功能更新。 |
| 2024-09-04 | `ffe80807` | [PixelStreaming] Fix: Undeprecate as VCam is still depending on it | 修复：撤销了某个函数的废弃标记，因为虚拟摄像机功能仍在依赖它。 |

### 维护评价

- **状态**：**维护中**。该插件创建于2023年初，处于实验阶段（IsBetaVersion: true）。从提交记录看，截至2026年4月仍有编译和API适配性维护，但无新功能开发。
- **活跃度**：更新频率较低，且多为底层引擎渲染API变更后的适配性修改，表明其核心功能已稳定。
- **限制与风险**：
    1.  **实验性**：官方标记为实验性，未来API可能发生重大变更或被移除。
    2.  **强依赖**：核心依赖于 `PixelStreaming` 插件，其稳定性直接影响本插件。
    3.  **平台限制**：目前仅支持Win64和Linux，且不支持服务器目标。
- **建议**：可以用于原型开发和特定场景验证。在生产环境中使用前，需要充分测试其稳定性，并做好应对未来API变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html) (通用像素流文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/PixelStreaming)