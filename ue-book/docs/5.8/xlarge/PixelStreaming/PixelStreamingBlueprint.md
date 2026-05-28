# Pixel Streaming

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-31 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming) | |

## 用途

Pixel Streaming 插件实现了 Unreal Engine 的音视频流送功能，通过 WebRTC 协议将渲染画面和音频实时传输到兼容的播放器（主要是 Web 浏览器）。核心架构是：UE 引擎在服务端进行渲染和编码，生成 H.264/VP8 视频流和 Opus 音频流，然后通过 WebRTC 数据通道发送给远程客户端。客户端只需要一个支持 WebRTC 的浏览器即可接收并播放，无需安装任何本地应用或游戏客户端。

这解决了以下核心问题：
- **跨平台访问**：用户无需下载安装大型游戏/应用，浏览器即可体验
- **硬件要求转移**：客户端无需高性能 GPU，渲染压力完全在服务器端
- **即时访问**：通过 URL 即可立即进入体验
- **企业应用**：适用于数字孪生、远程监控、虚拟制片等需要远程可视化的大屏/客户端场景

## 使用场景

- 你做了一个 UE5 应用，想让用户通过浏览器直接访问 → 用 Pixel Streaming
- 你在做数字孪生/智慧工厂项目，需要在多台终端大屏上展示实时 3D 场景 → 用 Pixel Streaming
- 你在做虚拟制片项目，导演需要在 iPad/手机上预览实时渲染 → 用 Pixel Streaming
- 你需要将 UE5 的实时渲染能力嵌入到现有 Web 平台 → 用 Pixel Streaming
- 你在做云游戏服务，需要低延迟的远程游戏串流 → 用 Pixel Streaming
- 你在做 XR 串流，需要将 VR/AR 画面发送到 HMD 设备 → 用 Pixel Streaming + PixelStreamingHMD 模块

## 蓝图用法

Blueprint 模块提供了 `UPixelStreamingStreamerComponent`，这是一个可附加到任何 Actor 的组件，用于在蓝图中控制流送的生命周期。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartStreaming` | 启动流送，连接到信令服务器并开始编码推流 | `UPixelStreamingStreamerComponent` |
| `StopStreaming` | 停止流送，断开信令服务器连接 | `UPixelStreamingStreamerComponent` |
| `IsStreaming` | 检查当前是否正在流送 | `UPixelStreamingStreamerComponent` |
| `IsSignallingConnected` | 检查是否已连接到信令服务器 | `UPixelStreamingStreamerComponent` |
| `GetId` | 获取流送器 ID，用于区分多个流送实例 | `UPixelStreamingStreamerComponent` |
| `ForceKeyFrame` | 强制下一个编码帧为关键帧，可用于修复画面撕裂 | `UPixelStreamingStreamerComponent` |
| `FreezeStream` | 冻结流送画面，显示指定的纹理而不是实时画面 | `UPixelStreamingStreamerComponent` |
| `UnfreezeStream` | 解冻流送，恢复实时画面 | `UPixelStreamingStreamerComponent` |
| `SendPlayerMessage` | 向连接的播放器发送自定义消息（类型 + 描述符） | `UPixelStreamingStreamerComponent` |

### 视频输入选项

| 类 | 说明 |
|---|---|
| `UPixelStreamingStreamerVideoInputBackBuffer` | 从后缓冲区（BackBuffer）捕获画面，这是默认的输入方式 |
| `UPixelStreamingStreamerVideoInputRenderTarget` | 从指定的 `UTextureRenderTarget2D` 捕获画面，适用于自定义渲染管线 |
| `UPixelStreamingStreamerVideoInputMediaCapture` | 通过 Media Capture API 捕获画面，适用于特殊场景 |

### 组件属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `StreamerId` | String | 流送器唯一标识，默认为 "Streamer Component" |
| `SignallingServerURL` | String | 信令服务器地址，默认为 `ws://127.0.0.1:8888` |
| `UsePixelStreamingURL` | Bool | 是否使用 Pixel Streaming URL 配置 |
| `StreamFPS` | Int | 流送帧率，默认 60 FPS |
| `CoupleFramerate` | Bool | 是否耦合渲染帧率和流送帧率 |
| `VideoInput` | VideoInput Object | 视频输入源，可选 BackBuffer / RenderTarget / MediaCapture |

### 使用示例（蓝图描述）

**基本流送设置：**

1. 创建一个新 Actor，添加 `PixelStreamingStreamerComponent` 组件
2. 在 Details 面板中设置 `SignallingServerURL` 为你的信令服务器地址（如 `ws://192.168.1.100:8888`）
3. 设置 `StreamerId` 为唯一标识（如 "MainStreamer"）
4. 在 BeginPlay 中调用 `StartStreaming` 节点
5. 在 EndPlay 中调用 `StopStreaming` 节点

**自定义渲染目标流送：**

1. 创建一个 `Render Target 2D` 资产
2. 创建 `UPixelStreamingStreamerVideoInputRenderTarget` 对象，将其 `Target` 属性设置为你的 RenderTarget
3. 将 Streamer Component 的 `VideoInput` 设置为该 VideoInput 对象
4. 你的场景渲染逻辑将画面输出到该 RenderTarget，Pixel Streaming 将捕获并流送

**向客户端发送自定义消息：**

1. 调用 `SendPlayerMessage`，`Type` 参数传入消息类型（0-255 的数字标识符）
2. `Descriptor` 参数传入 JSON 格式的消息内容
3. 客户端 JavaScript 端通过 `UE5.js` 的 `addResponseEventListener` 接收

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingStreamerComponent.h"
```

### 基本用法

在 C++ 中获取并控制 Streamer 组件：

```cpp
// 在 Actor 中获取已附加的 Streamer 组件
UPixelStreamingStreamerComponent* StreamerComp = FindComponentByClass<UPixelStreamingStreamerComponent>();
if (StreamerComp)
{
    // 启动流送
    StreamerComp->StartStreaming();
    
    // 检查连接状态
    if (StreamerComp->IsSignallingConnected())
    {
        UE_LOG(LogTemp, Log, TEXT("Connected to signalling server"));
    }
    
    // 获取流送 ID
    FString StreamerId = StreamerComp->GetId();
}
```

### 进阶用法

监听流送事件和处理客户端输入：

```cpp
// 监听流送开始事件
StreamerComp->OnStreamingStarted.AddUObject(this, &AMyActor::OnStreamStarted);

// 监听流送停止事件
StreamerComp->OnStreamingStopped.AddUObject(this, &AMyActor::OnStreamStopped);

// 监听来自客户端的输入数据
StreamerComp->OnInputReceived.AddUObject(this, &AMyActor::OnPlayerInput);

// 回调函数
void AMyActor::OnStreamStarted()
{
    UE_LOG(LogTemp, Log, TEXT("Streaming started"));
}

void AMyActor::OnStreamStopped()
{
    UE_LOG(LogTemp, Log, TEXT("Streaming stopped"));
}

void AMyActor::OnPlayerInput(FPixelStreamingPlayerId PlayerId, uint8 Type, TArray<uint8> Data)
{
    // 处理客户端发送的自定义输入数据
    // Type 为消息类型标识符
    // Data 为消息负载数据
}

// 发送消息给客户端
StreamerComp->SendPlayerMessage(1, TEXT("{\"action\":\"update\",\"value\":42}"));

// 冻结流送画面（例如暂停时）
StreamerComp->FreezeStream(PauseScreenTexture);

// 解冻恢复实时画面
StreamerComp->UnfreezeStream();
```

## Demo 示例

一个完整的最小可编译示例，演示如何通过 C++ 组件控制 Pixel Streaming：

**MyStreamingActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyStreamingActor.generated.h"

class UPixelStreamingStreamerComponent;

UCLASS()
class AMyStreamingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyStreamingActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "PixelStreaming")
    UPixelStreamingStreamerComponent* StreamerComponent;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void HandleStreamingStarted();
    UFUNCTION()
    void HandleStreamingStopped();

    UFUNCTION(BlueprintCallable, Category = "PixelStreaming")
    void SendCustomMessageToClient(const FString& Message);

    UFUNCTION(BlueprintCallable, Category = "PixelStreaming")
    void ToggleFreeze(bool bFreeze, UTexture2D* FreezeTexture = nullptr);
};
```

**MyStreamingActor.cpp**

```cpp
#include "MyStreamingActor.h"
#include "PixelStreamingStreamerComponent.h"

AMyStreamingActor::AMyStreamingActor()
{
    PrimaryActorTick.bCanEverTick = false;

    StreamerComponent = CreateDefaultSubobject<UPixelStreamingStreamerComponent>(TEXT("PixelStreamer"));
    StreamerComponent->StreamerId = TEXT("MyCustomStreamer");
    StreamerComponent->SignallingServerURL = TEXT("ws://127.0.0.1:8888");
    StreamerComponent->StreamFPS = 60;
}

void AMyStreamingActor::BeginPlay()
{
    Super::BeginPlay();

    if (StreamerComponent)
    {
        StreamerComponent->OnStreamingStarted.AddUObject(this, &AMyStreamingActor::HandleStreamingStarted);
        StreamerComponent->OnStreamingStopped.AddUObject(this, &AMyStreamingActor::HandleStreamingStopped);
        StreamerComponent->StartStreaming();
    }
}

void AMyStreamingActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (StreamerComponent)
    {
        StreamerComponent->StopStreaming();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyStreamingActor::HandleStreamingStarted()
{
    UE_LOG(LogTemp, Log, TEXT("Pixel Streaming started for %s"), *StreamerComponent->GetId());
}

void AMyStreamingActor::HandleStreamingStopped()
{
    UE_LOG(LogTemp, Log, TEXT("Pixel Streaming stopped"));
}

void AMyStreamingActor::SendCustomMessageToClient(const FString& Message)
{
    if (StreamerComponent)
    {
        // Type 1 = 自定义应用消息
        StreamerComponent->SendPlayerMessage(1, Message);
    }
}

void AMyStreamingActor::ToggleFreeze(bool bFreeze, UTexture2D* FreezeTexture)
{
    if (!StreamerComponent) return;

    if (bFreeze && FreezeTexture)
    {
        StreamerComponent->FreezeStream(FreezeTexture);
    }
    else
    {
        StreamerComponent->UnfreezeStream();
    }
}
```

## 模块依赖

本插件包含 7 个模块，依赖关系如下：

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 核心 WebRTC 集成和流送引擎 |
| `MediaUtils` | 媒体工具函数，用于视频编码处理 |
| `RenderCore` | 渲染核心，用于获取后缓冲区和渲染目标 |
| `RHI` | 渲染硬件接口，用于 GPU 资源操作 |
| `Sockets` | 网络套接字，用于信令服务器通信 |
| `Networking` | 网络模块 |
| `WebRTC` | WebRTC 协议实现 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复 PIE/模拟模式下的崩溃问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：将 VP 资产移动到不同资产分类并迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString |

### 维护评价

**活跃维护** — Pixel Streaming 插件持续获得积极维护和更新：

- **最近更新频率**：近 1 个月内有多次功能性更新和 bug 修复，更新频率很高
- **功能完善度**：从 2019 年从 Experimental 迁移至今，功能已经非常成熟，涵盖多模块架构（核心流送、蓝图接口、HMD 支持、输入处理、独立服务器等）
- **仍在活跃维护**：最近的 commit 显示 Epic 仍在持续修复兼容性问题、优化性能，并且有 PixelStreaming2 相关的重构工作
- **注意事项**：
  - `EnabledByDefault` 为 `false`，使用前需要在项目设置中手动启用
  - 需要额外部署信令服务器（Signalling Server），UE5 提供了对应的工具
  - H.264 编码需要 GPU 硬件支持（通常需要 NVIDIA GPU 或 Intel Quick Sync）
- **推荐使用**：✅ 强烈推荐。这是 Epic 官方的远程串流方案，广泛应用于数字孪生、虚拟制片、云游戏等场景，社区生态成熟

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming/Tests)