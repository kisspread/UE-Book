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
| 创建时间 | 2025-10-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2（简称 PS2）是 UE5 中实现**实时像素流送**的核心插件。它将 UE 渲染的画面（包括音频）通过 WebRTC 协议实时编码并传输到浏览器等 WebRTC 兼容客户端，让用户无需高端硬件即可通过浏览器操控 UE 应用。与第一代相比，PS2 完全重构了内部架构，支持更灵活的编解码器选择（H.264/AV1/VP8/VP9）、多流（Simulcast）、自定义视频输入源（RenderTarget、后缓冲区、MediaIO 等），并提供了更完善的蓝图/C++ 接口。

## 使用场景

- **云游戏/云渲染**：将高保真渲染应用（如汽车配置器、建筑漫游）通过浏览器远程交付，用户只需一个 URL 即可体验。
- **远程协作**：多个用户同时观看/操作同一个 UE 场景，比如多人评审、协同设计。
- **数字孪生/工业可视化**：在低端设备上（如手机、平板）查看实时更新的 3D 数据，无需下载完整 UE 工程。
- **短视频/直播**：将 UE 内容作为直播视频源推送到流媒体平台。

## 蓝图用法

以下节点来自 `PixelStreaming2InputComponent`、`PixelStreaming2Blueprints`、`PixelStreaming2Delegates`、`PixelStreaming2StreamerComponent`、`PixelStreaming2AudioComponent`、`PixelStreaming2VideoComponent` 等类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SendPixelStreaming2Response` | 向触发 UI 交互的源发送响应（JSON 描述符） | `UPixelStreaming2Input` |
| `GetJsonStringValue` | 从 UI 交互的 JSON 描述符中提取指定字段的值 | `UPixelStreaming2Input` |
| `AddJsonStringValue` | 向 JSON 描述符中添加一个字符串字段 | `UPixelStreaming2Input` |
| `SendResponse` | 向连接到默认流送器的所有 WebRTC 对端发送响应 | `UPixelStreaming2Blueprints` |
| `StreamerSendResponse` | 向指定流送器的所有对端发送响应 | `UPixelStreaming2Blueprints` |
| `SendFile` | 通过数据通道向默认流送器发送文件（填入文件路径、MIME 类型、扩展名） | `UPixelStreaming2Blueprints` |
| `StreamerSendFile` | 通过数据通道向指定流送器发送文件 | `UPixelStreaming2Blueprints` |
| `SendFileAsByteArray` | 通过数据通道发送字节数组（如截图数据） | `UPixelStreaming2Blueprints` |
| `StreamerSendFileAsByteArray` | 通过数据通道向指定流送器发送字节数组 | `UPixelStreaming2Blueprints` |
| `ForceKeyFrame` | 强制默认流送器发送关键帧（用于视频质量恢复） | `UPixelStreaming2Blueprints` |
| `StreamerForceKeyFrame` | 强制指定流送器发送关键帧 | `UPixelStreaming2Blueprints` |
| `FreezeFrame` | 冻结默认流送器的视频输出，显示指定的 Texture2D（或最后一帧） | `UPixelStreaming2Blueprints` |
| `UnfreezeFrame` | 恢复默认流送器的视频输出 | `UPixelStreaming2Blueprints` |
| `StreamerFreezeStream` / `StreamerUnfreezeStream` | 对指定流送器冻结/解冻视频 | `UPixelStreaming2Blueprints` |
| `ListenTo` | 使音频组件开始监听指定 Player 的 WebRTC 音频 | `UPixelStreaming2AudioComponent` |
| `StreamerListenTo` | 使音频组件监听指定流送器下的指定 Player | `UPixelStreaming2AudioComponent` |
| `IsListeningToPlayer` | 音频组件是否正在监听某个 Player | `UPixelStreaming2AudioComponent` |
| `Reset` | 重置音频组件状态，停止监听并准备重新连接 | `UPixelStreaming2AudioComponent` |
| `Watch` | 使视频组件开始观看指定 Player 的 WebRTC 视频 | `UPixelStreaming2VideoComponent` |
| `StreamerWatch` | 使视频组件观看指定流送器下的指定 Player | `UPixelStreaming2VideoComponent` |
| `IsWatchingPlayer` | 视频组件是否正在观看某个 Player | `UPixelStreaming2VideoComponent` |
| `Reset` | 重置视频组件状态 | `UPixelStreaming2VideoComponent` |
| `StartStreaming` | 让流送器组件开始连接信号服务器并发送音视频 | `UPixelStreaming2StreamerComponent` |
| `StopStreaming` | 停止流送 | `UPixelStreaming2StreamerComponent` |
| `IsStreaming` | 是否正在流送 | `UPixelStreaming2StreamerComponent` |
| `ForceKeyFrame` (流送器组件) | 强制该组件对应的流送器发送关键帧 | `UPixelStreaming2StreamerComponent` |
| `FreezeStream` / `UnfreezeStream` | 对该组件对应的流送器冻结/解冻视频 | `UPixelStreaming2StreamerComponent` |
| `SendAllPlayersMessage` / `SendPlayerMessage` | 向所有 Player 或指定 Player 发送消息 | `UPixelStreaming2StreamerComponent` |

### 使用示例（蓝图描述）

**从浏览器接收 UI 交互并回应**：
1. 在玩家 Pawn 上挂载 `PixelStreaming2Input` 组件。
2. 在其 `OnInputEvent` 事件上绑定自定义事件。
3. 在事件中调用 `GetJsonStringValue` 提取 `"command"` 字段，根据命令执行相应操作（如显示计分板）。
4. 最后调用 `SendPixelStreaming2Response` 向浏览器返回 JSON 结果。

**在引擎内播放远程玩家音频**：
1. 在任意 Actor 添加 `PixelStreaming2AudioComponent`。
2. 设置 `PlayerToHear` 为空白（让组件自动监听第一个非监听 Player）。
3. 勾选 `bAutoFindPeer`。
4. 组件会像普通 SynthComponent 发出声音。

**显示远程玩家视频**：
1. 在场景中放置一个平面，材质中使用 `PixelStreaming2MediaTexture` 作为纹理源。
2. 添加 `PixelStreaming2VideoComponent`，设置其 `PlayerToWatch` 为空白，勾选 `bAutoFindPeer`。
3. 将 `VideoConsumer` 属性指向已创建的 `PixelStreaming2MediaTexture`，视频将实时显示在平面上。

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreaming2Module.h"
#include "IPixelStreaming2Streamer.h"
#include "PixelStreaming2Delegates.h"
#include "PixelStreaming2Blueprints.h" // 如使用蓝图库
// 各组件头文件
#include "PixelStreaming2InputComponent.h"
#include "PixelStreaming2AudioComponent.h"
#include "PixelStreaming2VideoComponent.h"
```

### 基本用法

**获取模块并创建流送器**（GameThread 或 Async 中）：
```cpp
using namespace UE::PixelStreaming2;

// 获取模块
IPixelStreaming2Module& PSModule = IPixelStreaming2Module::Get();

// 创建流送器
FString StreamerId = TEXT("MyStreamer");
TSharedPtr<IPixelStreaming2Streamer> Streamer = PSModule.CreateStreamer(StreamerId);
if (Streamer)
{
    Streamer->SetVideoProducer(...);   // 设置视频输入源
    Streamer->SetSignallingServerURL(TEXT("ws://127.0.0.1:8888"));
    Streamer->StartStreaming();
}
```

**监听全局事件**：
```cpp
UPixelStreaming2Delegates* Delegates = GetMutableDefault<UPixelStreaming2Delegates>();
Delegates->OnConnectedToSignallingServerNative.AddLambda([](const FString& StreamerId) {
    UE_LOG(LogTemp, Log, TEXT("Streamer %s connected to signalling server"), *StreamerId);
});
```

**自定义视频生产者**（将 RenderTarget 作为输入）：
```cpp
#include "VideoProducerRenderTarget.h"

void SetupCustomVideoSource(UTextureRenderTarget2D* RT)
{
    TSharedPtr<FVideoProducerRenderTarget> VP = FVideoProducerRenderTarget::Create(RT);
    // 将其绑定到某个流送器
    // Streamer->SetVideoProducer(VP);
}
```

**在应用内接收远程音频**（在 C++ Actor 中）：
```cpp
// 在 Actor 中创建 AudioComponent
UPixelStreaming2AudioComponent* AudioComp = NewObject<UPixelStreaming2AudioComponent>(this);
AudioComp->RegisterComponent();
AudioComp->PlayerToHear = TEXT(""); // 自动
AudioComp->bAutoFindPeer = true;
```

**通过数据通道发送消息**：
```cpp
#include "PixelStreaming2Blueprints.h"
// 向默认流送器的所有 Player 发送 JSON 消息
UPixelStreaming2Blueprints::SendResponse(TEXT("{\"type\":\"update\",\"data\":\"...\"}"));
```

### 进阶用法

**多流（Simulcast）配置**：通过控制台变量或设置 `CVarEncoderEnableSimulcast` 可启用 Simulcast，系统自动产生低、中、高三个分辨率层。每层的比特率分配见 `UtilsVideo.h` 中的 `GetSimulcastParameters()`。

**自定义硬件编解码器检测**：使用 `IsHardwareEncoderSupported<FVideoEncoderConfigAV1>()`、`IsSoftwareEncoderSupported<FVideoEncoderConfigH264>()` 等模板函数检查平台支持情况。

**自定义音频混合器**：实现 `IPixelStreaming2AudioProducer` 接口，通过 `FAudioCapturer::AddAudioProducer` 添加自定义音频源，音频将自动与引擎声音混合后发送。

## Demo 示例

以下 C++ 示例演示如何在关卡 Blueprint 中通过 C++ 创建并启动一个简单的像素流送（假设已运行 Signal Server）。

**PixelStreaming2Demo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PixelStreaming2Demo.generated.h"

class UPixelStreaming2AudioComponent;
class UPixelStreaming2VideoComponent;

UCLASS()
class APixelStreaming2Demo : public AActor
{
    GENERATED_BODY()

public:
    APixelStreaming2Demo();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void OnNewConnection(FString StreamerId, FString PlayerId);

    TSharedPtr<class IPixelStreaming2Streamer> Streamer;
    UPROPERTY() UPixelStreaming2AudioComponent* AudioComp;
};
```

**PixelStreaming2Demo.cpp**
```cpp
#include "PixelStreaming2Demo.h"
#include "IPixelStreaming2Module.h"
#include "PixelStreaming2Delegates.h"
#include "PixelStreaming2AudioComponent.h"
#include "PixelStreaming2Blueprints.h" // for SendResponse
#include "Kismet/GameplayStatics.h"

APixelStreaming2Demo::APixelStreaming2Demo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void APixelStreaming2Demo::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建音频组件，用于播放远程用户的麦克风音频
    AudioComp = NewObject<UPixelStreaming2AudioComponent>(this);
    AudioComp->RegisterComponent();
    AudioComp->bAutoFindPeer = true;
    AudioComp->PlayerToHear = TEXT("");

    // 2. 等待 PixelStreaming2 模块就绪
    IPixelStreaming2Module& PSModule = IPixelStreaming2Module::Get();
    PSModule.OnReady().AddLambda([this](IPixelStreaming2Module& Module) {
        // 3. 创建默认流送器
        Streamer = Module.CreateStreamer(TEXT("DemoStreamer"));
        if (!Streamer)
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to create streamer"));
            return;
        }
        // 4. 连接到本地信号服务器（端口 8888）
        Streamer->SetSignallingServerURL(TEXT("ws://127.0.0.1:8888"));
        Streamer->StartStreaming();

        // 5. 监听新连接事件，当有 Player 连接时向浏览器发送欢迎消息
        UPixelStreaming2Delegates* Delegates = GetMutableDefault<UPixelStreaming2Delegates>();
        Delegates->OnNewConnectionNative.AddRaw(this, &APixelStreaming2Demo::OnNewConnection);
    });
}

void APixelStreaming2Demo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);
    if (Streamer)
    {
        Streamer->StopStreaming();
        Streamer.Reset();
    }
}

void APixelStreaming2Demo::OnNewConnection(FString StreamerId, FString PlayerId)
{
    // 向新连接的 Player 发送一条 JSON 消息
    FString Response = TEXT("{\"type\":\"welcome\", \"message\":\"Hello from Unreal Engine!\"}");
    UPixelStreaming2Blueprints::StreamerSendResponse(StreamerId, Response);
    UE_LOG(LogTemp, Log, TEXT("Player %s connected, sent welcome"), *PlayerId);
}
```

**说明**：此示例演示了最小化启动流送、监听远程音频、以及通过数据通道响应新连接。实际部署时需要启动独立的 Signal Server（例如官方提供的 Node.js 服务器）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | 用于 Vulkan 后端视频资源的创建和管理（PixelStreaming2 模块特有） |

其他模块如 `PixelStreaming2RTC`、`PixelStreaming2Servers` 等内部依赖已在插件内部自动处理，用户模块无需显式依赖。若用户需要使用插件蓝图或组件，只需在项目 `.Build.cs` 中添加 `"PixelStreaming2"` 到 `PublicDependencyModuleNames` 即可。

## 维护状态

### 近期更新

- 2026-01-23 `a9928676` — [NVCodecs, PixelStreaming2] Fixes:
- 2025-11-18 `d7a4d160` — [AVCodecs, PixelStreaming2] Fixes:
- 2025-10-28 `b1db9444` — [PixelStreaming2] Fix: Deadlocks in PixelStreaming2Thread
- 2025-10-17 `5c2f039d` — [PS2] Fix: Non-functional public API
- 2025-10-13 `0de4d465` — [PS2] Bug Fixes for 5.7

### 维护评价

- **创建时间**：2025-10-13（约 1 年前）
- **近期更新活跃度**：来自最近 3 个月的多次修复（死锁、API 修复等），且仍在持续修复。
- **维护状态**：**活跃维护**。Epic 持续投入修复和优化，无废弃迹象。
- **推荐使用**：✅ 强烈推荐。作为 UE 官方下一代像素流送方案，PS2 已在多个实际项目中使用，且 API 稳定、功能丰富。建议新项目直接使用 PS2 而非第一代版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2/Private/Tests)