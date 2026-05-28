# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素串流2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Epic Games 全新构建的像素串流框架，用以替代旧版 Pixel Streaming 插件。它将 Unreal Engine 的音频和视频渲染输出通过 **EpicRtc**（Epic 自研的 WebRTC 抽象层）编码为 H264/VP8/VP9/AV1 格式，经 WebRTC 协议实时传输至浏览器或其他兼容播放器。

与旧版相比，Pixel Streaming 2 的核心架构变化包括：
- **EpicRtc 层**：用 Epic 自有的 WebRTC 抽象库替代直接依赖 webrtc 源码，提升可维护性和跨平台一致性
- **模块化设计**：将 RTC 通信、输入处理、服务器管理、编辑器工具等拆分为独立模块（9 个），降低耦合
- **Consumer/Producer 模型**：音视频数据采用标准化的 Producer→Sink→Consumer 管道，支持自定义音视频源接入
- **Media Framework 集成**：内置 `IMediaPlayerFactory`，支持通过 UE Media Framework 的 Media Source / Media Texture 播放远端流

## 使用场景

- 你需要将 UE5 云渲染结果实时传输到网页浏览器 → 启用 Pixel Streaming 2
- 你在做云游戏 / 云应用平台，需要低延迟音视频串流 → 用 Pixel Streaming 2 的 Streamer 端
- 你需要在 UE 内部作为客户端接收另一个 UE 实例或信令服务器的串流 → 用 `UPixelStreaming2Peer` 或 Media Player
- 你需要在 XR 设备上接收云渲染输出 → 用 `PixelStreaming2HMD` 模块
- 你需要在浏览器与 UE 之间双向传递数据通道消息 → 用 Data Track 的 `SendMessage` API
- 你需要自定义视频编码器（硬件加速）→ 实现 `EpicRtcVideoEncoderInitializerInterface`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect` | 连接到信令服务器，参数为服务器 URL | `UPixelStreaming2Peer` |
| `Disconnect` | 断开与信令服务器的连接 | `UPixelStreaming2Peer` |
| `Subscribe` | 订阅指定 Streamer 的音视频流 | `UPixelStreaming2Peer` |

### 属性与事件

| 属性/事件 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `OnStreamerList` | `BlueprintAssignable` 事件 | 服务器返回可用流列表时触发 | `UPixelStreaming2Peer` |
| `VideoConsumer` | `UPixelStreaming2MediaTexture*` | 远端视频画面输出目标材质纹理 | `UPixelStreaming2Peer` |

### 使用示例（蓝图描述）

**作为 Peer 端接收串流：**

1. 在 Actor 上添加 `PixelStreaming2PeerComponent`（`UPixelStreaming2Peer` 是 `USynthComponent`，可在蓝图中拖放添加）
2. 在组件属性中设置 `VideoConsumer` 为一个 `MediaTexture` 资产
3. 在 BeginPlay 中调用 `Connect("ws://your-signalling-server:80")` 连接信令服务器
4. 监听 `OnStreamerList` 事件，从返回的流 ID 列表中选取目标 Streamer
5. 调用 `Subscribe(StreamerId)` 订阅该流，远端视频将输出到 `VideoConsumer` 指定的纹理

## C++ 用法

### 头文件引入

```cpp
// Streamer 端（发送端）
#include "IPixelStreaming2Module.h"
#include "IPixelStreaming2Streamer.h"

// RTC 模块接口
#include "IPixelStreaming2RTCModule.h"

// Peer 端（接收端，蓝图组件）
#include "PixelStreaming2Peer.h"

// Media Player（Media Framework 集成）
#include "MediaSource.h"

// 统计
#include "IPixelStreaming2Stats.h"
```

### 基本用法 - Streamer 端创建与发送

从源码中 `FEpicRtcStreamer` 的接口推断的标准用法：

```cpp
// 获取 Streamer 实例（StreamId 为自定义标识符）
// 来源: Private/EpicRtcStreamer.h - FEpicRtcStreamer::GetId()
IPixelStreaming2Module& PSModule = IPixelStreaming2Module::Get();
if (PSModule.IsReady())
{
    // 获取或创建 streamer
    TSharedPtr<IPixelStreaming2Streamer> Streamer = PSModule.FindStreamer(TEXT("MyStreamer"));
    
    if (!Streamer.IsValid())
    {
        Streamer = PSModule.CreateStreamer(TEXT("MyStreamer"));
    }
    
    // 设置信令服务器 URL
    // 来源: Private/EpicRtcStreamer.h - SetConnectionURL()
    Streamer->SetConnectionURL(TEXT("ws://localhost:80"));
    
    // 设置帧率
    // 来源: Private/EpicRtcStreamer.h - SetStreamFPS()
    Streamer->SetStreamFPS(60);
    
    // 开始串流
    // 来源: Private/EpicRtcStreamer.h - StartStreaming()
    Streamer->StartStreaming();
    
    // 绑定事件
    // 来源: Private/EpicRtcStreamer.h - OnStreamingStarted()
    Streamer->OnStreamingStarted().AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("Streaming started!"));
    });
}
```

### 基本用法 - RTC 模块就绪检测

```cpp
// 来源: Public/IPixelStreaming2RTCModule.h
IPixelStreaming2RTCModule& RTCModule = IPixelStreaming2RTCModule::Get();

// 方式1：轮询就绪状态
if (RTCModule.IsReady())
{
    // 模块已初始化，可以使用
}

// 方式2：绑定就绪事件（推荐）
RTCModule.OnReady().AddLambda([](IPixelStreaming2RTCModule& Module)
{
    UE_LOG(LogTemp, Log, TEXT("PixelStreaming2RTC module is ready"));
});
```

### 进阶用法 - 自定义视频源

```cpp
// 来源: Private/EpicRtcStreamer.h - SetVideoProducer()
// 创建自定义视频生产者，替代默认的 BackBuffer 捕获
class FMyVideoProducer : public IPixelStreaming2VideoProducer
{
public:
    virtual FIntPoint GetFrameSize() const override { return FIntPoint(1920, 1080); }
    virtual int32 GetFrameBufferMemorySize() const override { return 1920 * 1080 * 4; }
    virtual void OnFrameReady(const FPixelCaptureOutputFrame& Frame) override { /* ... */ }
};

// 设置到 Streamer
TSharedPtr<IPixelStreaming2VideoProducer> MyProducer = MakeShared<FMyVideoProducer>();
Streamer->SetVideoProducer(MyProducer);
```

### 进阶用法 - 发送自定义消息

```cpp
// 来源: Private/EpicRtcStreamer.h - SendAllPlayersMessage() / SendPlayerMessage()
// 向所有连接的玩家发送自定义消息
FString Descriptor = TEXT("{\"action\":\"update\",\"value\":42}");
Streamer->SendAllPlayersMessage(TEXT("CustomMessage"), Descriptor);

// 向特定玩家发送
Streamer->SendPlayerMessage(TEXT("PlayerId123"), TEXT("CustomMessage"), Descriptor);
```

### 进阶用法 - 自定义音频源

```cpp
// 来源: Private/EpicRtcStreamer.h - AddAudioProducer() / RemoveAudioProducer()
// 添加自定义音频生产者
TSharedPtr<IPixelStreaming2AudioProducer> MyAudioProducer = /* ... */;
Streamer->AddAudioProducer(MyAudioProducer);

// 不再需要时移除
Streamer->RemoveAudioProducer(MyAudioProducer);
```

### 进阶用法 - 自定义数据统计

```cpp
// 来源: Public/IPixelStreaming2Stats.h - GraphValue()
// 在运行时图表中绘制自定义指标
IPixelStreaming2Stats::Get().GraphValue(
    TEXT("MyCustomMetric"),   // 图表名称
    CurrentValue,             // 当前值
    100,                      // 样本数（X 轴宽度）
    0.0f,                     // 最小范围
    1000.0f,                  // 最大范围
    500.0f                    // 参考线值
);
```

## Demo 示例

### 最小 Streamer 端示例（.h + .cpp）

```cpp
// MyPixelStreamingActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IPixelStreaming2Streamer.h"
#include "MyPixelStreamingActor.generated.h"

UCLASS()
class AMyPixelStreamingActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<IPixelStreaming2Streamer> Streamer;

    UFUNCTION()
    void OnStreamingStarted();

    UFUNCTION()
    void OnStreamingStopped();

    UFUNCTION()
    void OnPlayerConnected(const FString& PlayerId);
};
```

```cpp
// MyPixelStreamingActor.cpp
#include "MyPixelStreamingActor.h"
#include "IPixelStreaming2Module.h"

void AMyPixelStreamingActor::BeginPlay()
{
    Super::BeginPlay();

    IPixelStreaming2Module& PSModule = IPixelStreaming2Module::Get();
    if (!PSModule.IsReady())
    {
        UE_LOG(LogTemp, Warning, TEXT("PixelStreaming2 not ready yet"));
        return;
    }

    // 创建 streamer
    Streamer = PSModule.CreateStreamer(TEXT("GameStreamer"));
    if (!Streamer.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create streamer"));
        return;
    }

    // 配置
    Streamer->SetConnectionURL(TEXT("ws://localhost:8888"));
    Streamer->SetStreamFPS(60);

    // 绑定事件
    Streamer->OnStreamingStarted().AddUObject(this, &AMyPixelStreamingActor::OnStreamingStarted);
    Streamer->OnStreamingStopped().AddUObject(this, &AMyPixelStreamingActor::OnStreamingStopped);

    // 开始
    Streamer->StartStreaming();
}

void AMyPixelStreamingActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Streamer.IsValid())
    {
        Streamer->StopStreaming();
        Streamer.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyPixelStreamingActor::OnStreamingStarted()
{
    UE_LOG(LogTemp, Log, TEXT("Pixel Streaming started, waiting for players..."));
}

void AMyPixelStreamingActor::OnStreamingStopped()
{
    UE_LOG(LogTemp, Log, TEXT("Pixel Streaming stopped"));
}

void AMyPixelStreamingActor::OnPlayerConnected(const FString& PlayerId)
{
    UE_LOG(LogTemp, Log, TEXT("Player connected: %s"), *PlayerId);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | 视频编码所需的 Vulkan 图形 API 支持（PixelStreaming2 模块依赖） |
| `PixelCapture` | 帧捕获管道，用于从 GPU 读取渲染帧（推断自 `PixelCaptureBufferFormat`、`FVideoCapturer`、`FPixelCaptureOutputFrame` 等类） |
| `AVCodecsCore` | 音视频编解码核心，提供 H264/VP9 编码器配置（推断自 `UE::AVCodecCore::H264`、`UE::AVCodecCore::VP9` 命名空间） |

> **注**：EpicRtc 库以源码形式包含在 `Source/ThirdParty/EpicRtc/` 中（`EpicRtc` 模块），无需额外安装。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器获取默认目标窗口的方法错误 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产归类调整（非 PixelStreaming2 直接改动） |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持 FString 和 FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的输出异常 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2024 年 9 月，是 UE5 中较新的大型插件
- **更新频率**：近 1 个月内有多次提交（5 次 / 月），且包含实质性修复而非仅编译兼容
- **维护团队**：由 Epic Games 核心团队（Eden Harris、William Belcher 等）维护，与旧版 Pixel Streaming 为不同团队
- **架构状态**：作为旧版 Pixel Streaming 的替代品设计，模块化程度高（9 个模块），代码质量规范
- **已知限制**：
  - `EnabledByDefault=false`，需要手动在插件设置中启用
  - 依赖 VulkanRHI，在非 Vulkan 平台上可能需要额外配置
  - EpicRtc 为 Epic 自有库，第三方文档有限
- **推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐。作为 Epic 官方的新一代像素串流方案，活跃维护且架构先进，适合新项目直接采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)