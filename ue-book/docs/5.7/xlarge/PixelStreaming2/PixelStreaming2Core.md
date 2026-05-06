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
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Unreal Engine 5.7 中第二代像素流送技术，用于将虚幻引擎的渲染画面和音频实时推送到 WebRTC 兼容的播放器（如网页浏览器）。与第一代相比，PS2 引入了更模块化的架构、统一的音视频生产-消费管道、以及更高效的编码和传输机制。`PixelStreaming2Core` 核心模块定义了整个系统的抽象接口，包括：

- **流媒体实例** (`IPixelStreaming2Streamer`)：管理整个流会话的生命周期（连接、帧率、编解码器、信令等）。
- **视频生产者** (`IPixelStreaming2VideoProducer`)：将视频帧（GPU 纹理或 CPU 帧）推入流管道。
- **视频消费者** (`IPixelStreaming2VideoConsumer`)：接收从浏览器传回的编码视频帧并消费（例如渲染到 RenderTarget）。
- **音视频管道**（生产者/消费者/接收器）提供灵活的解耦接入点。

解决的核心问题：**如何让任意 UE 应用实时、低延迟地、可交互地输出到浏览器**。适用于云游戏、远程培训、设计评审、数字孪生等场景。

## 使用场景

- **云游戏**：在服务器上运行 UE 游戏，将画面流式传输到网页浏览器，玩家直接在浏览器中操作。
- **建筑/工业可视化**：将高保真虚拟场景远程推送给客户，无需高端客户端硬件。
- **远程协作**：多位用户通过浏览器同时查看同一场景，并接收输入反馈。
- **直播/展示**：将 UE 实时渲染内容推流到 OBS 或浏览器直播平台。

## 蓝图用法

`PixelStreaming2Core` 模块主要提供 C++ 接口（UObject 接口类），蓝图无法直接调用 `IPixelStreaming2XX` 上的方法，但可以通过蓝图实现 UInterface 并绑定事件。例如 `IPixelStreaming2VideoProducer` 的 `OnFramePushed` 事件和 `IPixelStreaming2AudioProducer` 的 `OnAudioPushed` 事件可以在 C++ 中绑定，而蓝图中可以通过继承 `BlueprintImplementableEvent` 来响应，但当前接口未暴露。因此核心功能更偏向 C++ 使用。

不过，插件提供了 `PixelStreaming2` 模块中的一些蓝图可调用函数（如 `GetPixelStreaming2Module` 等），但不在本模块范围内。本文档仅描述 `PixelStreaming2Core` 的抽象接口。

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreaming2Streamer.h"
#include "IPixelStreaming2VideoProducer.h"
#include "IPixelStreaming2VideoConsumer.h"
#include "IPixelStreaming2AudioProducer.h"
#include "IPixelStreaming2AudioConsumer.h"
#include "IPixelStreaming2AudioSink.h"
#include "IPixelStreaming2VideoSink.h"
```

### 基本用法

#### 1. 创建自定义视频生产者

```cpp
// MyVideoProducer.h
#pragma once
#include "IPixelStreaming2VideoProducer.h"

class FMyVideoProducer : public IPixelStreaming2VideoProducer
{
public:
    virtual EVideoProducerCapabilities GetCapabilities() override { return EVideoProducerCapabilities::Default; }
    virtual FString ToString() override { return TEXT("MyCustomProducer"); }

    void PushMyFrame(const IPixelCaptureInputFrame& Frame)
    {
        PushFrame(Frame); // 触发 OnFramePushed
    }
};
```

#### 2. 实现视频消费者

```cpp
// MyVideoConsumer.h
#pragma once
#include "IPixelStreaming2VideoConsumer.h"

class FMyVideoConsumer : public IPixelStreaming2VideoConsumer
{
public:
    virtual void ConsumeFrame(FTextureRHIRef Frame) override
    {
        // 处理远端传来的视频帧（例如更新 UTexture2D）
        // Frame 是 GPU 纹理 RHI 句柄
    }
    virtual void OnVideoConsumerAdded() override { /* 消费者被添加到 sink 时回调 */ }
    virtual void OnVideoConsumerRemoved() override { /* 消费者被移除时回调 */ }
};
```

#### 3. 获取流媒体实例并配置

```cpp
#include "IPixelStreaming2Module.h" // 该头文件定义在 PixelStreaming2 模块中，但 Core 模块提供工厂方法

// 假设已获得 streamer 实例（例如通过 IPixelStreaming2Module::Get().CreateStreamer()）
TSharedPtr<IPixelStreaming2Streamer> MyStreamer = ...;

// 设置视频生产者
TSharedPtr<IPixelStreaming2VideoProducer> MyProducer = MakeShared<FMyVideoProducer>();
MyStreamer->SetVideoProducer(MyProducer);

// 设置帧率
MyStreamer->SetStreamFPS(60);

// 设置连接地址（信令服务器或直接 WebRTC 地址）
MyStreamer->SetConnectionURL(TEXT("ws://my-signaling-server.com/ws"));

// 开始流送
MyStreamer->StartStreaming();
```

#### 4. 添加音频消费者

```cpp
#include "IPixelStreaming2AudioSink.h"

// 获取视频/音频 sink 通常通过 player 的接口获得
// 假设获得 audio sink: TSharedRef<IPixelStreaming2AudioSink> AudioSink = ...;
// 创建音频消费者
class FMyAudioConsumer : public IPixelStreaming2AudioConsumer
{
public:
    virtual void ConsumeRawPCM(const int16_t* AudioData, int InSampleRate, size_t NChannels, size_t NFrames) override
    {
        // 处理 PCM 音频数据
    }
    virtual void OnAudioConsumerAdded() override {}
    virtual void OnAudioConsumerRemoved() override {}
};

// 添加消费者
TWeakPtrVariant<IPixelStreaming2AudioConsumer> ConsumerPtr = MakeShareable(new FMyAudioConsumer);
AudioSink->AddAudioConsumer(ConsumerPtr);
```

### 进阶用法

#### 自定义视频生产者支持预处理帧

如果生产者已经对帧进行了预处理（如缩放、格式转换），则返回 `EVideoProducerCapabilities::ProducesPreprocessedFrames` 标志：

```cpp
virtual EVideoProducerCapabilities GetCapabilities() override 
{ 
    return EVideoProducerCapabilities::ProducesPreprocessedFrames; 
}
```

#### 多个音频生产者混合

```cpp
TSharedPtr<IPixelStreaming2AudioProducer> MicProducer = ...;
TSharedPtr<IPixelStreaming2AudioProducer> GameSoundProducer = ...;
MyStreamer->AddAudioProducer(MicProducer);
MyStreamer->AddAudioProducer(GameSoundProducer);
// 所有推入的音频将被混合后编码发送
```

## Demo 示例

以下是一个完整的 C++ 示例，创建一个简单的视频消费者将收到的帧输出到控制台（简化）。

**DemoVideoConsumer.h**
```cpp
#pragma once
#include "IPixelStreaming2VideoConsumer.h"
#include "Containers/Array.h"

class FDemoVideoConsumer : public IPixelStreaming2VideoConsumer
{
public:
    virtual void ConsumeFrame(FTextureRHIRef Frame) override
    {
        // 仅记录帧到达
        UE_LOG(LogTemp, Log, TEXT("Video frame consumed"));
        // 实际应用中可将 Frame 拷贝到 UTexture2D 或渲染到 Viewport
    }
    virtual void OnVideoConsumerAdded() override
    {
        UE_LOG(LogTemp, Log, TEXT("Video consumer added"));
    }
    virtual void OnVideoConsumerRemoved() override
    {
        UE_LOG(LogTemp, Log, TEXT("Video consumer removed"));
    }
};
```

**DemoStreamerSetup.h**
```cpp
#pragma once
#include "IPixelStreaming2Module.h"
#include "IPixelStreaming2Streamer.h"

void SetupPixelStreaming()
{
    // 获取 Pixel Streaming 2 模块
    IPixelStreaming2Module& PS2Module = IPixelStreaming2Module::Get();
    
    // 创建默认流媒体实例（ID 可自定义）
    TSharedPtr<IPixelStreaming2Streamer> Streamer = PS2Module.CreateStreamer(TEXT("DemoStreamer"));
    
    // 设置连接 URL
    Streamer->SetConnectionURL(TEXT("ws://localhost:8888"));

    // 设置帧率
    Streamer->SetStreamFPS(30);

    // 创建视频生产者（使用引擎默认的屏幕捕获生产者，假设已实现 FFallbackVideoProducer）
    // 实际生产环境中使用 PS2 自带的 FCaptureSource 等
    // Streamer->SetVideoProducer(SomeProducer);

    // 启动流送
    Streamer->StartStreaming();

    // 添加自定义视频消费者（如果接收到远端视频）
    // 通常通过 WebRTC player 获取视频 sink 后添加
}
```

## 模块依赖

`PixelStreaming2Core` 模块的 Build.cs 未提供（但可以推断依赖极少）。根据架构，它尽可能轻量。列出其他模块中的独特依赖（非标准核心模块）。

| 模块 | 用途 |
|---|---|
| `VulkanRHI`（通过 `PixelStreaming2` 模块间接） | 需要 Vulkan 支持以进行 GPU 帧编码 |
| `PixelCapture` | 提供 `IPixelCaptureInputFrame` 等捕获帧基础类型 |

> **注意**：`PixelStreaming2Core` 本身不直接依赖特定图形 API，只依赖 `PixelCapture`（RHI 基础类型）。实际 GPU 编码依赖在 `PixelStreaming2` 模块中。

## 维护状态

### 近期更新

- 2026-01-23 a9928676 — [NVCodecs, PixelStreaming2] Fixes: 修复多种编码器问题
- 2025-11-18 d7a4d160 — [AVCodecs, PixelStreaming2] Fixes: 修复 AV 编码器问题
- 2025-10-28 b1db9444 — [PixelStreaming2] Fix: Deadlocks in PixelStreaming2Thread
- 2025-10-17 5c2f039d — [PS2] Fix: Non-functional public API
- 2025-10-13 0de4d465 — [PS2] Bug Fixes for 5.7

### 维护评价

Pixel Streaming 2 是 UE 5.7 新引入的插件，目前处于活跃开发阶段。从创建日期（2025年10月）到最近提交（2026年1月）仅有 3 个月，但已有多项关键修复（死锁、API 功能问题）。虽然功能尚不完善，但官方投入明显，推荐在 5.7+ 中使用，但应注意可能仍有不稳定因素。**注意**：`IsEnabledByDefault` 为 `false`，需手动在项目设置中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2Core/Private/Tests)（若存在）