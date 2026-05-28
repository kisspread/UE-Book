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

Pixel Streaming 2 是 Epic 为 Unreal Engine 构建的第二代像素流送系统，用于将引擎的音频和视频渲染输出通过 WebRTC 协议实时传输到兼容的媒体播放器（主要是 Web 浏览器）。

与第一代 Pixel Streaming 相比，PS2 采用了全新的模块化架构（9 个独立模块），基于 EpicRtc（Epic 自研的 WebRTC 实现）替代了旧版的第三方 WebRTC 依赖，并引入了以下关键改进：

- **多 Streamer 支持**：可以在同一进程中运行多个独立的流送实例，每个 Streamer 有独立的 ID 和配置
- **Simulcast（联播）**：支持 3 层联播，根据客户端带宽自适应选择不同分辨率
- **多编解码器**：运行时检测硬件/软件编码器支持，自动选择 H264、AV1、VP8、VP9
- **MediaIO 捕获路径**：除传统的后缓冲区捕获外，还支持通过 MediaIO 框架捕获视频帧
- **自定义音视频生产者**：用户可以实现自己的 `IPixelStreaming2VideoProducer` 和 `IPixelStreaming2AudioProducer` 来推送自定义音视频源

**为什么存在**：第一代 Pixel Streaming 的架构过于单体化，WebRTC 依赖难以维护，且不支持多流送实例等现代需求。PS2 从底层完全重写，提供了更灵活、更可扩展的流送解决方案。

> ⚠️ **注意**：此插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用或通过命令行参数 `-PixelStreaming` 启用。

## 使用场景

- 你需要将 Unreal Engine 应用的画面实时传输到浏览器中查看和交互 → 使用默认后缓冲区流送
- 你在做一个云游戏/云渲染平台，需要支持多个玩家同时连接不同的游戏实例 → 使用多 Streamer 模式
- 你需要将特定的渲染目标（RenderTarget）而非整个后缓冲区传输到前端 → 使用 `FVideoProducerRenderTarget`
- 你需要在 PIE（Play In Editor）模式下测试像素流送 → 使用 `FVideoProducerPIEViewport`
- 你需要从前端浏览器接收玩家的摄像头画面并在引擎中展示 → 使用 `UPixelStreaming2VideoComponent`
- 你需要从前端浏览器接收玩家的麦克风音频并在引擎中播放 → 使用 `UPixelStreaming2AudioComponent`
- 你需要将自定义音频源（如语音聊天）混入流送音频 → 实现 `IPixelStreaming2AudioProducer`
- 你需要在 VR/HMD 设备上使用像素流送 → 启用 `PixelStreaming2HMD` 模块

## 蓝图用法

### 核心节点 — 全局操作（PixelStreaming2Blueprints）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SendResponse` | 向默认 Streamer 的连接客户端发送 JSON 响应 | `UPixelStreaming2Blueprints` |
| `StreamerSendResponse` | 向指定 Streamer 的客户端发送 JSON 响应 | `UPixelStreaming2Blueprints` |
| `SendFileAsByteArray` | 通过数据通道发送字节数组文件到默认 Streamer | `UPixelStreaming2Blueprints` |
| `StreamerSendFileAsByteArray` | 通过数据通道发送字节数组文件到指定 Streamer | `UPixelStreaming2Blueprints` |
| `SendFile` | 通过数据通道发送本地文件到默认 Streamer | `UPixelStreaming2Blueprints` |
| `StreamerSendFile` | 通过数据通道发送本地文件到指定 Streamer | `UPixelStreaming2Blueprints` |
| `ForceKeyFrame` | 强制默认 Streamer 发送关键帧 | `UPixelStreaming2Blueprints` |
| `StreamerForceKeyFrame` | 强制指定 Streamer 发送关键帧 | `UPixelStreaming2Blueprints` |
| `FreezeFrame` | 冻结默认 Streamer 的视频流，可选指定冻结画面 | `UPixelStreaming2Blueprints` |
| `UnfreezeFrame` | 解冻默认 Streamer 的视频流 | `UPixelStreaming2Blueprints` |
| `StreamerFreezeStream` | 冻结指定 Streamer 的视频流 | `UPixelStreaming2Blueprints` |
| `StreamerUnfreezeStream` | 解冻指定 Streamer 的视频流 | `UPixelStreaming2Blueprints` |
| `KickPlayer` | 从默认 Streamer 踢出指定玩家 | `UPixelStreaming2Blueprints` |
| `StreamerKickPlayer` | 从指定 Streamer 踢出指定玩家 | `UPixelStreaming2Blueprints` |
| `GetConnectedPlayers` | 获取默认 Streamer 的已连接玩家列表 | `UPixelStreaming2Blueprints` |
| `StreamerGetConnectedPlayers` | 获取指定 Streamer 的已连接玩家列表 | `UPixelStreaming2Blueprints` |
| `GetDefaultStreamerID` | 获取默认 Streamer 的 ID | `UPixelStreaming2Blueprints` |
| `GetJsonStringValue` | 从 JSON 描述符中提取字符串字段值 | `UPixelStreaming2Blueprints` |
| `AddJsonStringValue` | 向 JSON 描述符中添加字符串字段 | `UPixelStreaming2Blueprints` |
| `GetDelegates` | 获取委托单例，用于绑定像素流送事件 | `UPixelStreaming2Blueprints` |

### 核心节点 — Streamer 组件（UPixelStreaming2StreamerComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetId` | 获取当前 Streamer 的 ID | `UPixelStreaming2StreamerComponent` |
| `StartStreaming` | 开始流送 | `UPixelStreaming2StreamerComponent` |
| `StopStreaming` | 停止流送 | `UPixelStreaming2StreamerComponent` |
| `IsStreaming` | 检查是否正在流送 | `UPixelStreaming2StreamerComponent` |
| `ForceKeyFrame` | 强制发送关键帧 | `UPixelStreaming2StreamerComponent` |
| `FreezeStream` | 冻结视频流 | `UPixelStreaming2StreamerComponent` |
| `UnfreezeStream` | 解冻视频流 | `UPixelStreaming2StreamerComponent` |
| `SendAllPlayersMessage` | 向所有连接的玩家发送消息 | `UPixelStreaming2StreamerComponent` |
| `SendPlayerMessage` | 向指定玩家发送消息 | `UPixelStreaming2StreamerComponent` |

### 核心节点 — 音视频组件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListenTo` | 监听默认 Streamer 上指定玩家的音频 | `UPixelStreaming2AudioComponent` |
| `StreamerListenTo` | 监听指定 Streamer 上指定玩家的音频 | `UPixelStreaming2AudioComponent` |
| `IsListeningToPlayer` | 是否正在监听某个玩家 | `UPixelStreaming2AudioComponent` |
| `Reset` | 重置音频组件，停止监听并准备重新监听 | `UPixelStreaming2AudioComponent` |
| `Watch` | 观看默认 Streamer 上指定玩家的视频 | `UPixelStreaming2VideoComponent` |
| `StreamerWatch` | 观看指定 Streamer 上指定玩家的视频 | `UPixelStreaming2VideoComponent` |
| `IsWatchingPlayer` | 是否正在观看某个玩家 | `UPixelStreaming2VideoComponent` |
| `Reset` | 重置视频组件，停止观看并准备重新观看 | `UPixelStreaming2VideoComponent` |

### 核心节点 — 输入组件（UPixelStreaming2Input）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SendPixelStreaming2Response` | 向前端发送 UI 交互响应 | `UPixelStreaming2Input` |
| `GetJsonStringValue` | 从 JSON 描述符中提取字段值 | `UPixelStreaming2Input` |
| `AddJsonStringValue` | 向 JSON 描述符中添加字段 | `UPixelStreaming2Input` |

### 事件委托（UPixelStreaming2Delegates）

| 委托 | 说明 | 触发时机 |
|---|---|---|
| `OnConnectedToSignallingServer` | 已连接信令服务器 | Streamer 成功连接到信令服务器 |
| `OnDisconnectedFromSignallingServer` | 断开信令服务器连接 | Streamer 与信令服务器断开 |
| `OnNewConnection` | 新玩家连接 | 有新玩家/peer 建立 WebRTC 连接 |
| `OnClosedConnection` | 玩家断开连接 | 玩家/peer 断开连接 |
| `OnAllConnectionsClosed` | 所有连接已关闭 | 所有玩家都断开了，可重置应用 |
| `OnDataTrackOpen` | 数据通道打开 | 新的数据通道建立 |
| `OnDataTrackClosed` | 数据通道关闭 | 数据通道断开 |
| `OnStatChanged` | 统计数据变化 | 帧率、延迟等统计变化 |
| `OnFallbackToSoftwareEncoding` | 回退到软件编码 | GPU 硬件编码器不足时触发 |

### 使用示例（蓝图描述）

**基本流送设置**：

1. 在场景中放置一个 `UPixelStreaming2StreamerComponent` 组件
2. 设置组件的 `SignallingServerURL`（默认 `ws://127.0.0.1:8888`）
3. 设置 `StreamerId` 为一个唯一标识符
4. 设置 `VideoProducer` 为需要的视频生产者类型（默认为后缓冲区）
5. 调用 `StartStreaming` 开始流送

**监听前端玩家音频**：

1. 在场景中放置一个 `UPixelStreaming2AudioComponent`
2. 设置 `PlayerToHear` 为目标玩家 ID（留空则自动监听第一个连接的玩家）
3. 设置 `bAutoFindPeer = true` 让组件自动寻找玩家
4. 组件会自动开始播放来自该玩家浏览器麦克风的音频

**接收前端 UI 交互并响应**：

1. 在 Actor 上添加 `UPixelStreaming2Input` 组件
2. 绑定 `OnInputEvent` 事件
3. 在事件回调中使用 `GetJsonStringValue` 解析前端发来的 JSON 数据
4. 使用 `AddJsonStringValue` 构建响应 JSON
5. 调用 `SendPixelStreaming2Response` 将响应发回前端

**使用全局委托监听连接事件**：

1. 调用 `UPixelStreaming2Blueprints::GetDelegates()` 获取委托单例
2. 绑定 `OnNewConnection`、`OnClosedConnection` 等委托
3. 在回调中根据 `StreamerId` 和 `PlayerId` 执行相应逻辑

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreaming2Module.h"
#include "IPixelStreaming2Streamer.h"
#include "PixelStreaming2Delegates.h"
#include "PixelStreaming2VideoProducers.h"
```

### 基本用法 — 获取模块并启动流送

```cpp
// 获取 PixelStreaming2 模块
IPixelStreaming2Module& PS2Module = IPixelStreaming2Module::Get();

// 等待模块就绪后操作
if (PS2Module.IsReady())
{
    // 获取或创建 Streamer
    TSharedPtr<IPixelStreaming2Streamer> Streamer = PS2Module.FindStreamer("MyStreamer");
    if (!Streamer.IsValid())
    {
        Streamer = PS2Module.CreateStreamer("MyStreamer");
    }

    // 启动所有 Streamer 的流送
    PS2Module.StartStreaming();
}
```

### 基本用法 — 使用 OnReady 事件

```cpp
// 监听模块就绪事件（推荐方式）
IPixelStreaming2Module::Get().OnReady().AddLambda([](IPixelStreaming2Module& Module)
{
    // 模块就绪，可以安全使用所有功能
    TSharedPtr<IPixelStreaming2Streamer> Streamer = Module.CreateStreamer("DefaultStreamer");
    Module.StartStreaming();
});
```

### 基本用法 — 监听连接委托

```cpp
// 获取委托单例
UPixelStreaming2Delegates* Delegates = UPixelStreaming2Delegates::Get();
if (Delegates)
{
    // 监听新连接
    Delegates->OnNewConnectionNative.AddLambda([](FString StreamerId, FString PlayerId)
    {
        UE_LOG(LogPixelStreaming2, Log, TEXT("Player %s connected to Streamer %s"), *PlayerId, *StreamerId);
    });

    // 监听连接断开
    Delegates->OnClosedConnectionNative.AddLambda([](FString StreamerId, FString PlayerId)
    {
        UE_LOG(LogPixelStreaming2, Log, TEXT("Player %s disconnected from Streamer %s"), *PlayerId, *StreamerId);
    });

    // 监听所有连接关闭（可用于重置应用状态）
    Delegates->OnAllConnectionsClosedNative.AddLambda([](FString StreamerId)
    {
        UE_LOG(LogPixelStreaming2, Log, TEXT("All connections closed on Streamer %s"), *StreamerId);
    });
}
```

### 基本用法 — 遍历所有 Streamer

```cpp
IPixelStreaming2Module::Get().ForEachStreamer([](TSharedPtr<IPixelStreaming2Streamer> Streamer)
{
    // 对每个 Streamer 执行操作
    // 注意：不要在回调内创建/删除 Streamer，避免死锁
});
```

### 进阶用法 — 自定义视频生产者

```cpp
#include "IPixelStreaming2VideoProducer.h"

// 方式1：使用预设的视频生产者
TSharedPtr<IPixelStreaming2VideoProducer> BackBufferProducer = 
    UE::PixelStreaming2::CreateVideoProducerBackBuffer();

TSharedPtr<IPixelStreaming2VideoProducer> RenderTargetProducer = 
    UE::PixelStreaming2::CreateVideoProducerRenderTarget(MyRenderTarget);

TSharedPtr<IPixelStreaming2VideoProducer> PIEViewportProducer = 
    UE::PixelStreaming2::CreateVideoProducerPIEViewport();

// 方式2：实现自定义视频生产者（继承 IPixelStreaming2VideoProducer）
// 实现 PushFrame 方法来推送自定义视频帧
```

### 进阶用法 — 自定义音频生产者

```cpp
#include "IPixelStreaming2AudioProducer.h"

// 继承 IPixelStreaming2AudioProducer 并实现 PushAudio 方法
// 推送的音频会与引擎音频混合后统一编码传输
```

### 进阶用法 — 发送数据到前端

```cpp
// 向默认 Streamer 发送 JSON 响应
FString Response = TEXT("{\"type\":\"customEvent\",\"data\":\"hello\"}");
IPixelStreaming2Module::Get().FindStreamer("Default")->SendResponse(Response);

// 向指定玩家发送消息
TSharedPtr<IPixelStreaming2Streamer> Streamer = IPixelStreaming2Module::Get().FindStreamer("MyStreamer");
if (Streamer.IsValid())
{
    Streamer->SendPlayerMessage(PlayerId, "CustomMessage", Descriptor);
}
```

### 进阶用法 — JSON 工具函数

```cpp
#include "PixelStreaming2Utils.h"

// 扩展 JSON 字符串
FString OriginalJson = TEXT("{}");
FString NewJson;
bool bSuccess;
UE::PixelStreaming2::ExtendJsonWithField(OriginalJson, "Resolution.Width", "1920", NewJson, bSuccess);

// 从 JSON 提取字段值
FString Value;
UE::PixelStreaming2::ExtractJsonFromDescriptor(NewJson, "Resolution.Width", Value, bSuccess);
```

### 进阶用法 — Simulcast 与编解码器

```cpp
// 运行时检测编解码器支持
#include "UtilsCoder.h"

bool bH264Supported = UE::PixelStreaming2::IsEncoderSupported<FVideoEncoderConfigH264>();
bool bAV1Supported  = UE::PixelStreaming2::IsEncoderSupported<FVideoEncoderConfigAV1>();
bool bVP8Supported  = UE::PixelStreaming2::IsEncoderSupported<FVideoEncoderConfigVP8>();
bool bVP9Supported  = UE::PixelStreaming2::IsEncoderSupported<FVideoEncoderConfigVP9>();

// Simulcast 参数（3 层联播，缩放因子为 2）
// 可通过 CVar UPixelStreaming2PluginSettings::CVarEncoderEnableSimulcast 启用
```

## Demo 示例

### 最小流送示例

```cpp
// MyStreamActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IPixelStreaming2Module.h"
#include "IPixelStreaming2Streamer.h"
#include "PixelStreaming2Delegates.h"
#include "MyStreamActor.generated.h"

UCLASS()
class AMyStreamActor : public AActor
{
    GENERATED_BODY()

public:
    AMyStreamActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void OnPS2Ready(IPixelStreaming2Module& Module);
    void OnPlayerConnected(FString StreamerId, FString PlayerId);
    void OnPlayerDisconnected(FString StreamerId, FString PlayerId);

    TSharedPtr<IPixelStreaming2Streamer> Streamer;
    FDelegateHandle ReadyHandle;
};
```

```cpp
// MyStreamActor.cpp
#include "MyStreamActor.h"
#include "PixelStreaming2VideoProducers.h"

AMyStreamActor::AMyStreamActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyStreamActor::BeginPlay()
{
    Super::BeginPlay();

    IPixelStreaming2Module& PS2Module = IPixelStreaming2Module::Get();

    if (PS2Module.IsReady())
    {
        OnPS2Ready(PS2Module);
    }
    else
    {
        ReadyHandle = PS2Module.OnReady().AddUObject(this, &AMyStreamActor::OnPS2Ready);
    }

    // 绑定连接事件
    if (UPixelStreaming2Delegates* Delegates = UPixelStreaming2Delegates::Get())
    {
        Delegates->OnNewConnectionNative.AddUObject(this, &AMyStreamActor::OnPlayerConnected);
        Delegates->OnClosedConnectionNative.AddUObject(this, &AMyStreamActor::OnPlayerDisconnected);
    }
}

void AMyStreamActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Streamer.IsValid())
    {
        IPixelStreaming2Module::Get().DeleteStreamer(Streamer);
        Streamer.Reset();
    }

    IPixelStreaming2Module::Get().OnReady().Remove(ReadyHandle);

    Super::EndPlay(EndPlayReason);
}

void AMyStreamActor::OnPS2Ready(IPixelStreaming2Module& Module)
{
    // 创建一个使用后缓冲区的 Streamer
    Streamer = Module.CreateStreamer(TEXT("MyGameStreamer"));

    if (Streamer.IsValid())
    {
        // 设置视频生产者为后缓冲区
        TSharedPtr<IPixelStreaming2VideoProducer> VideoProducer = 
            UE::PixelStreaming2::CreateVideoProducerBackBuffer();
        Streamer->SetVideoProducer(VideoProducer);

        // 启动流送
        Module.StartStreaming();
    }
}

void AMyStreamActor::OnPlayerConnected(FString StreamerId, FString PlayerId)
{
    UE_LOG(LogTemp, Log, TEXT("Player [%s] connected to streamer [%s]"), *PlayerId, *StreamerId);
}

void AMyStreamActor::OnPlayerDisconnected(FString StreamerId, FString PlayerId)
{
    UE_LOG(LogTemp, Log, TEXT("Player [%s] disconnected from streamer [%s]"), *PlayerId, *StreamerId);
}
```

## 模块依赖

从 Build.cs 依赖分析，使用者需要关注以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | Vulkan 渲染硬件接口，用于视频帧捕获和编码（PixelStreaming2 模块直接依赖） |
| `PixelStreaming2Core` | 核心基础模块，提供共享类型和基础设施 |
| `PixelStreaming2RTC` | WebRTC 通信层，基于 EpicRtc 封装 |
| `PixelStreaming2Input` | 输入处理模块，管理前端到引擎的输入映射 |
| `PixelStreaming2Settings` | 设置模块，提供所有 CVar 和配置项 |
| `PixelStreaming2Servers` | 信令服务器和 Web 服务器管理 |
| `PixelStreaming2HMD` | VR/HMD 专用流送支持 |
| `PixelStreaming2Editor` | 编辑器集成支持 |
| `EpicRtc` | Epic 自研的 WebRTC 实现（第三方封装） |

> 如果仅通过蓝图使用（组件和蓝图节点），无需手动添加模块依赖。若需在 C++ 中直接访问 `IPixelStreaming2Module`，需在你的模块的 `Build.cs` 中添加 `PixelStreaming2Core` 依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：移动 VP 资产到不同分类（涉及 PS2 相关资源） |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 支持 FString 和 UE::FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的垃圾输出问题 |

### 维护评价

- **创建时间**：2024 年 9 月，作为 UE5 的新一代像素流送方案，是较新的插件
- **维护活跃度**：非常活跃，2026 年 4-5 月持续有实质性更新（bug 修复、重构）
- **代码规模**：347 个源文件，9 个模块，架构复杂但模块化清晰
- **默认未启用**：`EnabledByDefault: false`，表明仍处于可选采用阶段，但功能已完整
- **API 稳定性**：部分早期 API 已标记 `UE_DEPRECATED`（如 `CreateVideoProducer`、`GetDefaultSignallingURL`），说明 API 仍在演进中
- **推荐程度**：✅ 推荐使用。这是 Epic 官方维护的第二代像素流送方案，相比旧版 Pixel Streaming 有显著的架构改进和功能增强。如果你的项目需要像素流送功能，应优先选择 PS2 而非旧版。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [IPixelStreaming2Module 接口](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2/Public/IPixelStreaming2Module.h)
- [委托定义](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2/Public/PixelStreaming2Delegates.h)
- [蓝图库](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2/Private/Blueprints/PixelStreaming2Blueprints.h)