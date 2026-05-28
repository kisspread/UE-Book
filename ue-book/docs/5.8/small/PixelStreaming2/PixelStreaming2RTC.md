# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Epic Games 对初代 Pixel Streaming 插件的完全重写版本。它实现了将 Unreal Engine 的渲染画面和音频通过 WebRTC 协议实时流送到浏览器等兼容客户端的能力，使得无需在用户端安装高性能硬件即可体验高质量的实时 3D 内容。

与初代相比，PS2 的核心架构变化在于引入了 **EpicRtc** 作为 WebRTC 的抽象层（替代直接绑定 libwebrtc），使得编解码器注册、会话管理、轨道回调等都通过 EpicRtc 接口完成。整个插件按职责拆分为 9 个模块：

- **PixelStreaming2Core** — 核心公共类型、接口定义、数据协议
- **PixelStreaming2RTC** — WebRTC 通信层（EpicRtc 集成、编解码器、流送器/播放器）
- **PixelStreaming2Input** — 远程输入处理（键盘、鼠标、手柄、XR）
- **PixelStreaming2Servers** — 内嵌信令/转发服务器管理
- **PixelStreaming2HMD** — VR/XR 头显支持
- **PixelStreaming2Settings** — 控制台变量与配置
- **PixelStreaming2Editor** — 编辑器工具与 UI
- **PixelStreaming2** — 顶层模块，整合所有子模块
- **EpicRtc** — 第三方 EpicRtc WebRTC 库封装

`PixelStreaming2EnabledByDefault` 为 `false`，需要在项目设置或命令行中手动启用。

## 使用场景

- 你需要将 UE 应用流送到浏览器，用户只需一个链接即可体验（云渲染、云游戏、数字孪生）
- 你需要多客户端同时观看同一份渲染流（一对多广播）
- 你需要从浏览器向 UE 发送输入（鼠标点击、键盘、手柄、XR 控制器）
- 你需要低延迟的实时音视频流（建筑可视化、汽车配置器、远程协作评审）
- 你需要在多个 UE 实例间复用同一个信令服务器进行切换流

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect` | 连接到指定的信令服务器，传入 URL 字符串 | `UPixelStreaming2Peer` |
| `Disconnect` | 断开与信令服务器的连接 | `UPixelStreaming2Peer` |
| `Subscribe` | 订阅指定 StreamerId 的流 | `UPixelStreaming2Peer` |

### 事件委托

| 委托 | 说明 | 所在类 |
|---|---|---|
| `OnStreamerList` | 当服务器返回可用流列表时触发 | `UPixelStreaming2Peer` |

### 属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `VideoConsumer` | `UPixelStreaming2MediaTexture*` | 视频数据接收纹理，流连接协商完成后自动填充 | `UPixelStreaming2Peer` |

### 使用示例（蓝图描述）

**作为观看者连接到流：**

1. 在 Actor 上添加 `PixelStreaming2PeerComponent`
2. 在 `BeginPlay` 中调用 `Connect("ws://your-signalling-server:80")`
3. 绑定 `OnStreamerList` 事件，从返回的流列表中选择一个 StreamerId
4. 调用 `Subscribe(StreamerId)` 订阅该流
5. 将 `VideoConsumer` 属性设置为一个 `MediaTexture`，流的视频画面将自动渲染到该纹理上

**在 Widget 中显示：**

1. 创建一个 UMG `Image` 控件
2. 创建一个 `MediaTexture` 资产并设为 Image 的 Brush
3. 将 `PixelStreaming2PeerComponent` 的 `VideoConsumer` 指向该 MediaTexture
4. 连接/订阅后，远程画面将自动显示在 UI 中

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreaming2RTCModule.h"   // RTC 模块接口
#include "IPixelStreaming2Stats.h"      // 统计信息接口
```

### 检查模块就绪状态

```cpp
// 来源: Public/IPixelStreaming2RTCModule.h
// 等待 PixelStreaming2RTC 模块初始化完成后再使用流送器
if (IPixelStreaming2RTCModule::IsAvailable())
{
    IPixelStreaming2RTCModule& RTCModule = IPixelStreaming2RTCModule::Get();
    RTCModule.OnReady().AddLambda([](IPixelStreaming2RTCModule& Module)
    {
        // 此时流送器已创建，可以安全使用
    });
}
```

### 使用统计信息 API

```cpp
// 来源: Public/IPixelStreaming2Stats.h
// 在自定义代码中向 Pixel Streaming 统计图表写入自定义值
IPixelStreaming2Stats& Stats = IPixelStreaming2Stats::Get();
Stats.GraphValue(TEXT("MyCustomMetric"), CurrentValue, 120, 0.0f, 100.0f, 50.0f);
// 参数: 名称, 值, 采样数, 最小范围, 最大范围, 参考线值
```

### 自定义流送器工厂

```cpp
// 来源: Private/EpicRtcStreamer.h (FRTCStreamerFactory)
// FRTCStreamerFactory 创建 FEpicRtcStreamer 实例
// 通过 GetStreamType() 返回 "DefaultRtc" 标识流类型
// 通过 CreateNewStreamer(StreamerId) 创建新的流送器实例
```

### 进阶用法

**实现自定义 Observer（观察者模式）：**

PS2 大量使用观察者模式。你可以实现 `IPixelStreaming2SessionObserver`、`IPixelStreaming2RoomObserver`、`IPixelStreaming2AudioTrackObserver`、`IPixelStreaming2VideoTrackObserver`、`IPixelStreaming2DataTrackObserver` 等接口来监听各种 WebRTC 事件。

```cpp
// 来源: Internal/EpicRtcSessionObserver.h
// 会话状态观察者
class FMySessionObserver : public IPixelStreaming2SessionObserver
{
public:
    virtual void OnSessionStateUpdate(const EpicRtcSessionState State) override
    {
        // 处理会话状态变化: Disconnected -> Connecting -> Connected
    }
    virtual void OnSessionErrorUpdate(const EpicRtcErrorCode Error) override
    {
        // 处理会话错误
    }
    virtual void OnSessionRoomsAvailableUpdate(EpicRtcStringArrayInterface* RoomsList) override
    {
        // 获取可用房间列表
    }
};
```

```cpp
// 来源: Internal/EpicRtcVideoTrackObserver.h
// 视频轨道观察者 - 接收远程视频帧
class FMyVideoObserver : public IPixelStreaming2VideoTrackObserver
{
public:
    virtual void OnVideoTrackFrame(EpicRtcVideoTrackInterface* Track, const EpicRtcVideoFrame& Frame) override
    {
        // 收到原始视频帧
    }
    virtual void OnVideoTrackEncodedFrame(EpicRtcStringView ParticipantId,
        EpicRtcVideoTrackInterface* Track, const EpicRtcEncodedVideoFrame& EncodedFrame) override
    {
        // 收到编码后的视频帧
    }
    virtual void OnVideoTrackMuted(EpicRtcVideoTrackInterface* Track, EpicRtcBool bIsMuted) override {}
    virtual void OnVideoTrackState(EpicRtcVideoTrackInterface* Track, const EpicRtcTrackState State) override {}
    virtual EpicRtcBool Enabled() const override { return true; }
};
```

**使用数据通道发送自定义消息：**

```cpp
// 来源: Internal/EpicRtcDataTrack.h
// FEpicRtcDataTrack::SendMessage 使用协议注册的消息名称发送结构化数据
// 需要先在 IPixelStreaming2InputHandler::GetFromStreamerProtocol() 中注册消息
DataTrack->SendMessage(TEXT("MyCustomMessage"), SomeIntValue, SomeStringValue);
```

## Demo 示例

```cpp
// MyPixelStreamingPeer.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PixelStreaming2RTCModule.h"
#include "IPixelStreaming2Stats.h"
#include "MyPixelStreamingPeer.generated.h"

UCLASS()
class AMyPixelStreamingPeer : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override
    {
        Super::BeginPlay();

        // 等待 RTC 模块就绪
        if (IPixelStreaming2RTCModule::IsAvailable())
        {
            IPixelStreaming2RTCModule::Get().OnReady().AddUObject(
                this, &AMyPixelStreamingPeer::OnRTCModuleReady);
        }
    }

    virtual void Tick(float DeltaTime) override
    {
        Super::Tick(DeltaTime);

        // 自定义统计信息示例
        if (IPixelStreaming2Stats* Stats = &IPixelStreaming2Stats::Get())
        {
            Stats->GraphValue(TEXT("MyMetric"), FMath::Sin(GetWorld()->GetTimeSeconds()),
                60, -1.0f, 1.0f);
        }
    }

private:
    void OnRTCModuleReady(IPixelStreaming2RTCModule& Module)
    {
        // RTC 模块就绪，可以创建流送器或连接信令服务器
        UE_LOG(LogTemp, Log, TEXT("PixelStreaming2RTC module is ready"));
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VulkanRPI` | Vulkan RHI 后端，用于 GPU 编码器的硬件加速 |
| `PixelCapture` | 帧捕获与格式转换（I420/RHI 等） |
| `AVCodecsCore` / `AVCodecsCoreRHI` | 编解码器核心框架（H.264/VP8/VP9/AV1） |
| `PixelStreaming2Core` | PS2 核心接口与类型定义 |
| `PixelStreaming2Input` | 远程输入处理 |
| `EpicRtc` | EpicRtc WebRTC 抽象层 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器获取默认目标窗口的方法错误 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double 截断为 float 的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the... | 虚拟制片资产分类重组，PS2 相关资产随项目调整 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象支持 FString 和 SharedString 双模式 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的输出错误 |

### 维护评价

Pixel Streaming 2 是 Epic Games 的**旗舰级活跃维护项目**，作为初代 Pixel Streaming 的继任者，于 2024 年 9 月正式引入。插件创建至今约 2 年，但最近 1 个月内仍有持续的功能修复和代码质量改进。

**优势：**
- 来自 Epic Games 官方维护，与 UE 主线同步更新
- 架构清晰，模块化设计（9 个独立模块）
- 基于 EpicRtc 抽象层，不再直接依赖 libwebrtc，维护和升级更灵活
- 支持 H.264/VP8/VP9/AV1 多种编码器，支持 SVC 可伸缩编码
- 内置完整的统计信息收集与显示系统
- 提供 Media Framework 集成（IMediaPlayerFactory），可用标准 MediaTexture 显示流

**注意事项：**
- `EnabledByDefault=false`，需要手动启用插件
- 需要配套的信令服务器和 TURN/STUN 服务器
- 依赖 VulkanRHI 等特定 RHI 后端
- 当前仍为 v1.0 版本，API 可能随版本迭代调整

**推荐程度：** ⭐⭐⭐⭐⭐ 强烈推荐。这是 Epic Games 官方的云渲染/远程流送方案，是初代 Pixel Streaming 的全面升级版。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)