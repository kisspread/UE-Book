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
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming) | |

## 用途

像素流送插件将虚幻引擎的渲染输出和音频实时编码为视频流，通过 WebRTC 协议传输到浏览器或其他支持 WebRTC 的客户端。它实现了从 UE 应用到远程设备的高效、低延迟音视频传输，并支持双向交互（键盘、鼠标、触摸）和自定义数据通道。

该插件解决的核心问题：
- **远程渲染**：在服务器上运行 UE 应用，将画面流式传输到任何 WebRTC 兼容的终端（PC、手机、平板、智能电视），无需安装 UE 运行时。
- **云游戏/实时交互**：结合信令服务器和 ICE/STUN/TURN，可实现跨网络的高质量、低延迟交互体验。
- **虚拟桌面/远程控制**：可用于数字孪生、建筑可视化、工业模拟等场景的远程操控。

## 使用场景

- **云游戏平台**：将 UE 渲染的游戏画面实时推送到浏览器，用户通过浏览器进行游戏。
- **远程协作**：多个用户同时观看同一 UE 场景，通过数据通道交换控制命令。
- **产品展示/虚拟展厅**：用户通过 URL 即可访问精美的 UE 渲染 3D 场景并进行交互。
- **数字孪生远程监控**：实时推送建筑、工厂、设备的 UE 可视化画面，并通过浏览器进行远程操控。
- **教育/培训模拟**：将复杂模拟画面推送到学生设备，无需高性能本地硬件。

## 蓝图用法

以下功能通过 `UPixelStreamingBlueprints` 蓝图函数库暴露，可在任何蓝图中调用。

### 文件传输

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SendFileAsByteArray` | 将字节数组作为文件通过数据通道发送到浏览器（需指定文件 MIME 类型和扩展名） | `UPixelStreamingBlueprints` |
| `StreamerSendFileAsByteArray` | 向指定流送器的所有连接客户端发送字节数组文件 | `UPixelStreamingBlueprints` |
| `SendFile` | 从磁盘路径加载文件并通过数据通道发送 | `UPixelStreamingBlueprints` |
| `StreamerSendFile` | 向指定流送器的客户端发送文件 | `UPixelStreamingBlueprints` |

### 流控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ForceKeyFrame` | 强制视频编码器立即生成关键帧，可用于快速恢复因网络丢包导致的画面质量问题 | `UPixelStreamingBlueprints` |
| `FreezeFrame` | 冻结像素流送画面，显示一张静态纹理（可指定 `UTexture2D`，为 `null` 时冻结当前帧） | `UPixelStreamingBlueprints` |
| `UnfreezeFrame` | 解除冻结，恢复实时视频流 | `UPixelStreamingBlueprints` |
| `StreamerFreezeStream` / `StreamerUnfreezeStream` | 同上，但针对指定 ID 的流送器 | `UPixelStreamingBlueprints` |

### 输入与连接

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddInputComponent` / `RemoveInputComponent` | 管理输入组件（`UPixelStreamingInput`），用于处理来自浏览器的输入 | `FPixelStreamingModule`（通过 `IPixelStreamingModule` 蓝图 API） |
| `GetInputComponents` | 获取所有注册的输入组件 | `IPixelStreamingModule` |
| `CreateStreamer` / `DeleteStreamer` | 创建/销毁一个流送器实例，每个流送器独立管理一个信令连接 | `IPixelStreamingModule` |
| `StartStreaming` / `StopStreaming` | 启动/停止指定流送器的流送 | `IPixelStreamingStreamer` |

### 使用示例（蓝图描述）

1. **发送文件到浏览器**：从蓝图节点调用 `SendFileAsByteArray`，连接 `ByteArray`（`TArray<uint8>`），`MimeType`（如 `"image/png"`），`FileExtension`（如 `".png"`）。浏览器端会收到数据通道消息并自动重建文件。
2. **显示加载画面冻结帧**：在切换关卡前调用 `FreezeFrame`，传入一张 `UTexture2D` 作为加载画面。关卡加载完成后调用 `UnfreezeFrame` 恢复流。
3. **强制关键帧**：当检测到网络质量下降或客户端请求时，调用 `ForceKeyFrame` 帮助解码器恢复。

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreamingModule.h"
#include "IPixelStreamingStreamer.h"
#include "PixelStreamingVideoInputI420.h"   // 如果使用 I420 视频输入
#include "PixelStreamingServers.h"           // 如果使用内置信令服务器
```

### 基本用法

从自动化测试（`Source/Private/Tests/TestUtils.h`、`CodecUtils.h`）提取的典型用法：

```cpp
// 1. 获取像素流送模块并创建流送器
TSharedPtr<IPixelStreamingStreamer> Streamer = FPixelStreamingModule::Get().CreateStreamer(TEXT("MyStreamer"));

// 2. 设置视频输入（此处使用 I420 纯色帧视频输入，生产环境通常使用后缓冲输入）
TSharedPtr<FPixelStreamingVideoInputI420> VideoInput = MakeShared<FPixelStreamingVideoInputI420>();
Streamer->SetVideoInput(VideoInput);

// 3. 创建并连接信令服务器（内置简单服务器示例）
TSharedPtr<UE::PixelStreamingServers::IServer> SignallingServer = CreateSignallingServer(StreamerPort, PlayerPort);
Streamer->SetSignallingServerURL(FString::Printf(TEXT("ws://127.0.0.1:%d"), StreamerPort));

// 4. 开始流送
Streamer->StartStreaming();

// 5. 向视频输入推入帧（测试中发送纯色帧）
FMockVideoFrameConfig FrameConfig = { 128, 128, 255, 137, 216 }; // 宽度、高度、Y、U、V
// 实际使用时应通过视频捕获管线获取帧
VideoInput->OnFrame(CreateI420Frame(FrameConfig));

// 6. 停止流送
Streamer->StopStreaming();
```

*源码路径：`Engine/Plugins/Media/PixelStreaming/Source/PixelStreaming/Private/Tests/CodecUtils.h`*

### 进阶用法

**自定义音频输入**：创建 `FAudioInputMixer` 并注入外部音频源。

```cpp
// 创建音频混合器
TSharedPtr<UE::PixelStreaming::FAudioInputMixer> AudioMixer = MakeShared<UE::PixelStreaming::FAudioInputMixer>();

// 创建自定义音频输入（48kHz 立体声）
TSharedPtr<UE::PixelStreaming::FAudioInput> MyAudioInput = AudioMixer->CreateInput();
MyAudioInput->PushAudio(MyBuffer, NumSamples, 2, 48000);

// 使用此混合器创建音频设备模块
TSharedPtr<webrtc::AudioDeviceModule> ADM = MakeShared<UE::PixelStreaming::FAudioDeviceModule>(AudioMixer);
```

**配置编码器参数**：通过控制台变量或代码设置。

```cpp
// 通过 CVar 设置编码器代码为 H.264
UE::PixelStreaming::Settings::SetCodec(EPixelStreamingCodec::H264);

// 设置目标码率（bps）
UE::PixelStreaming::Settings::CVarPixelStreamingEncoderTargetBitrate->Set(5000000, ECVF_SetByCode);
```

**处理浏览器输入**：注册输入组件并处理消息。

```cpp
// 创建输入组件（通常在 Pawn 或 HUD 中）
UPixelStreamingInput* InputComponent = NewObject<UPixelStreamingInput>(this);
InputComponent->RegisterComponent();

// 在模块中注册
IPixelStreamingModule& Module = IPixelStreamingModule::Get();
Module.AddInputComponent(InputComponent);

// 通过输入组件的委托监听消息
InputComponent->OnInputReceived.AddLambda([](const FString& Descriptor) {
    UE_LOG(LogTemp, Log, TEXT("Received input: %s"), *Descriptor);
});
```

## Demo 示例

以下是一个最小可编译的 C++ 示例，展示如何创建流送器并开始流送。

**MyPixelStreamer.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "IPixelStreamingModule.h"
#include "IPixelStreamingStreamer.h"

class FMyPixelStreamer
{
public:
    void StartStreaming(const FString& SignallingURL);
    void StopStreaming();

private:
    TSharedPtr<IPixelStreamingStreamer> Streamer;
};
```

**MyPixelStreamer.cpp**
```cpp
#include "MyPixelStreamer.h"
#include "PixelStreamingVideoInputBackBuffer.h" // 发送后缓冲画面
#include "PixelStreamingServers.h"

void FMyPixelStreamer::StartStreaming(const FString& SignallingURL)
{
    // 获取模块
    IPixelStreamingModule& Module = IPixelStreamingModule::Get();

    // 创建流送器
    Streamer = Module.CreateStreamer(TEXT("MyStreamer"));

    // 设置视频输入（默认为后缓冲）
    Streamer->SetVideoInput(FPixelStreamingVideoInputBackBuffer::Create());

    // 设置信令服务器 URL
    Streamer->SetSignallingServerURL(SignallingURL);

    // 可选：注册事件回调
    Streamer->OnStreamingStarted().AddLambda([]() {
        UE_LOG(LogTemp, Log, TEXT("Streaming started"));
    });

    // 开始流送
    Streamer->StartStreaming();
}

void FMyPixelStreamer::StopStreaming()
{
    if (Streamer.IsValid())
    {
        Streamer->StopStreaming();
        IPixelStreamingModule::Get().DeleteStreamer(Streamer);
        Streamer.Reset();
    }
}
```

**注意**：此示例假设已有一个运行中的信令服务器（如 Node.js 官方的 `cirrus` 或内置的 `PixelStreamingServers` 模块）。实际部署时需先启动信令服务器。

## 模块依赖

PixelStreaming 主模块依赖以下独特模块（省略标准 Core/Engine/Slate/UMG 等）：

| 模块 | 用途 |
|---|---|
| `WebRTC` | 提供 WebRTC 核心功能（PeerConnection、音频/视频轨道、数据通道、STUN/TURN） |
| `AVEncoder` | 硬件/软件视频编码器基础架构（H.264、H.265、AV1、VPX） |
| `PixelCapture` | 帧捕获管线，提供多格式缓冲和适配器 |
| `PixelStreamingServers` | 内置信令服务器（简化开发测试） |
| `PixelStreamingInput` | 浏览器输入处理（键盘、鼠标、触摸、自定义消息） |
| `DeveloperSettings` | 读取像素流送配置（`/Script/PixelStreaming.PixelStreamingSettings`） |

## 维护状态

### 近期更新

- 2025-09-30 `4bfe7f55` 更新基础架构脚本指向新发布分支
- 2025-09-25 `1fdac7d5` 修复 MediaCapture 因队列和概率轮询导致的错误状态
- 2025-09-23 `30db91bd` 修复内部信令服务器因 `FTickableGameObject` 布局引起的 ensure 崩溃
- 2025-09-23 `cc062cea` 修复在命令行设置 streamID 时编辑器中的崩溃
- 2025-08-29 `32884de4` 迁移 `RHICreateTexture` 为 `RHICmdList.CreateTexture`

### 维护评价

PixelStreaming 是 UE5 的核心插件之一，由 Epic Games 官方维护。最近 1 个月内有多项关键修复，包括 MediaCapture 状态错误和编辑器崩溃，表明团队正在积极维护。

虽然插件非常新（2025 年 8 月创建），但代码成熟度较高，集成了 WebRTC 的最新版本，并提供了丰富的可配置选项。当前版本已支持 H.264、AV1、VP8/VP9 等多种编码，以及无界面模式、多窗口捕获等高级特性。

**建议**：对于需要远程渲染的 UE 项目，强烈推荐使用此插件。由于还在活跃迭代，建议关注官方发布日志和 GitHub 更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming/Source/PixelStreaming/Private/Tests)