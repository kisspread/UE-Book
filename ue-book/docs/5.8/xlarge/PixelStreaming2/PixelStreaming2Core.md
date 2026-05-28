# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流式传输 2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Epic Games 推出的下一代像素流式传输插件，用于将 Unreal Engine 的实时渲染画面和音频通过 WebRTC 协议流式传输到远程客户端（如网页浏览器）。它是原版 Pixel Streaming 插件的重构和现代化版本，旨在提供更清晰、更模块化、更易于扩展的架构。其核心解决的问题是实现“所见即所得”的远程应用访问，使用户无需在本地安装或运行引擎，即可通过网络浏览器实时交互体验高品质的 3D 内容、应用程序或游戏。

## 使用场景

- **云游戏与云应用**：将游戏或复杂的 3D 应用程序（如设计工具、仿真软件）部署在云端服务器，用户通过浏览器即可即点即玩/即用。
- **远程协作与评审**：在建筑、汽车设计等领域，团队成员可通过浏览器远程查看并操控同一份实时渲染的 3D 模型进行评审。
- **虚拟展览与零售**：创建高保真的线上虚拟展厅或产品配置器，供客户在线沉浸式体验。
- **实时数据可视化**：将引擎内的实时数据可视化场景（如城市信息模型、科学计算结果）流式传输给决策者。
- **XR 云串流**：通过 `PixelStreaming2HMD` 模块，可支持将 VR/XR 体验流式传输到头显设备。

## 蓝图用法

Pixel Streaming 2 的核心蓝图功能主要通过 `IPixelStreaming2Module` 和 `IPixelStreaming2Streamer` 接口暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Streamer` | 根据 ID 查找一个已创建的流媒体实例。 | `UPixelStreaming2Module` |
| `Create Streamer` | 创建一个新的流媒体实例。 | `UPixelStreaming2Module` |
| `Remove Streamer` | 移除一个流媒体实例。 | `UPixelStreaming2Module` |
| `Set Connection URL` | 设置流媒体要连接的信令服务器地址（如 WebSocket URL）。 | `IPixelStreaming2Streamer` |
| `Start Streaming` | 启动流式传输。 | `IPixelStreaming2Streamer` |
| `Stop Streaming` | 停止流式传输。 | `IPixelStreaming2Streamer` |
| `Set Video Producer` | 设置视频源（画面生产者），决定引擎的哪个画面将被编码并传输。 | `IPixelStreaming2Streamer` |
| `Add Audio Producer` | 添加一个额外的音频源（音频生产者），其音频将与引擎音频混合后传输。 | `IPixelStreaming2Streamer` |
| `Send All Players Message` | 向所有连接的浏览器客户端广播一条自定义消息。 | `IPixelStreaming2Streamer` |
| `Send Player Message` | 向指定 ID 的浏览器客户端发送一条自定义消息。 | `IPixelStreaming2Streamer` |
| `Kick Player` | 踢出指定 ID 的浏览器客户端。 | `IPixelStreaming2Streamer` |
| `Get Connected Players` | 获取当前所有连接的浏览器客户端 ID 列表。 | `IPixelStreaming2Streamer` |
| `Freeze Stream` | 冻结当前画面，可以捕获当前帧或指定纹理作为冻结画面。 | `IPixelStreaming2Streamer` |
| `Unfreeze Stream` | 解除画面冻结。 | `IPixelStreaming2Streamer` |
| `Force Key Frame` | 强制编码器发送一个关键帧，用于快速修复画面质量。 | `IPixelStreaming2Streamer` |

### 使用示例（蓝图描述）

1.  **初始化流媒体**：
    - 在需要开始流式传输的 Actor 的 `BeginPlay` 事件中，调用 `Create Streamer` 节点创建一个新的流媒体实例，并保存其返回的 `IPixelStreaming2Streamer` 对象引用。
    - 调用 `Set Connection URL` 节点，填入你的信令服务器地址（例如 `ws://your-server:8888`）。
2.  **配置与启动**：
    - 调用 `Set Video Producer` 节点，通常保持默认（使用引擎的最终渲染结果）。
    - 调用 `Start Streaming` 节点开始流式传输。
    - （可选）监听 `On Streaming Started` 事件以确认流已成功启动。
3.  **交互控制**：
    - 在需要向客户端发送数据时，使用 `Send All Players Message` 或 `Send Player Message` 节点。
    - 在需要管理客户端连接时，使用 `Get Connected Players` 和 `Kick Player` 节点。

## C++ 用法

核心用法围绕 `IPixelStreaming2Streamer` 和 `IPixelStreaming2Module` 展开。

### 头文件引入

```cpp
#include "IPixelStreaming2Module.h"
#include "IPixelStreaming2Streamer.h"
```

### 基本用法

以下代码展示了如何通过 C++ 创建和配置一个像素流媒体实例。
(来源：基于 `IPixelStreaming2Module` 和 `IPixelStreaming2Streamer` 接口定义)

```cpp
// 获取 Pixel Streaming 2 模块单例
UE::PixelStreaming2::IPixelStreaming2Module& PS2Module = UE::PixelStreaming2::IPixelStreaming2Module::Get();

// 创建一个新的流媒体实例，需要一个唯一的 ID
FString StreamerId = TEXT("MyCStreamer");
TSharedPtr<UE::PixelStreaming2::IPixelStreaming2Streamer> Streamer = PS2Module.CreateStreamer(StreamerId);
if (Streamer.IsValid())
{
    // 设置连接地址
    Streamer->SetConnectionURL(TEXT("ws://localhost:8888"));
    
    // 设置流媒体帧率
    Streamer->SetStreamFPS(60);
    
    // 绑定事件
    Streamer->OnStreamingStarted().AddLambda([](UE::PixelStreaming2::IPixelStreaming2Streamer* InStreamer) {
        UE_LOG(LogTemp, Log, TEXT("Streamer %s has started streaming."), *InStreamer->GetId());
    });
    
    // 启动流媒体
    Streamer->StartStreaming();
}
```

### 进阶用法

1.  **自定义视频生产者 (Video Producer)**：实现 `IPixelStreaming2VideoProducer` 接口，可以推送非引擎默认的渲染画面（如特定视口、UI 元素或外部图像源）。

    ```cpp
    // 自定义视频生产者
    class FMyVideoProducer : public UE::PixelStreaming2::IPixelStreaming2VideoProducer
    {
    public:
        virtual UE::PixelStreaming2::EVideoProducerCapabilities GetCapabilities() override
        {
            return UE::PixelStreaming2::EVideoProducerCapabilities::Default;
        }
        
        virtual FString ToString() override
        {
            return TEXT("My Custom Video Producer");
        }
        
        // 在你的逻辑中调用此方法来推送帧
        void ProduceFrame(const UE::PixelStreaming2::IPixelCaptureInputFrame& InputFrame)
        {
            // PushFrame 是基类 final 方法，会广播 OnFramePushed 事件
            PushFrame(InputFrame);
        }
    };
    
    // 使用
    auto MyProducer = MakeShared<FMyVideoProducer>();
    Streamer->SetVideoProducer(MyProducer);
    ```

2.  **自定义音频/视频消费者 (Consumer)**：实现 `IPixelStreaming2AudioConsumer` 和 `IPixelStreaming2VideoConsumer` 接口，可以处理来自浏览器端推回的音频和视频数据（例如用于本地录制、转发）。

    ```cpp
    // 自定义视频消费者
    class FMyVideoConsumer : public UE::PixelStreaming2::IPixelStreaming2VideoConsumer
    {
    public:
        virtual void ConsumeFrame(FTextureRHIRef Frame) override
        {
            // 在这里处理从浏览器接收到的视频纹理，例如渲染到一个小窗口
        }
        
        virtual void OnVideoConsumerAdded() override {}
        virtual void OnVideoConsumerRemoved() override {}
    };
    
    // 使用（需要先获取到某个玩家的 Video Sink）
    auto MyConsumer = MakeShared<FMyVideoConsumer>();
    TWeakPtr<UE::PixelStreaming2::IPixelStreaming2VideoSink> PlayerVideoSink = Streamer->GetPeerVideoSink(PlayerId);
    if (PlayerVideoSink.IsValid())
    {
        PlayerVideoSink.Pin()->AddVideoConsumer(MyConsumer);
    }
    ```

## Demo 示例

以下是一个最小化的 C++ 示例，创建一个流媒体并启动流式传输。
(注意：需要先在项目模块的 `.Build.cs` 文件中添加对 `PixelStreaming2` 和 `PixelStreaming2Core` 模块的依赖)

```cpp
// MyPS2Actor.h
#pragma once
#include "GameFramework/Actor.h"
#include "IPixelStreaming2Streamer.h"
#include "MyPS2Actor.generated.h"

UCLASS()
class AMyPS2Actor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<UE::PixelStreaming2::IPixelStreaming2Streamer> MyStreamer;
};
```

```cpp
// MyPS2Actor.cpp
#include "MyPS2Actor.h"
#include "IPixelStreaming2Module.h"

void AMyPS2Actor::BeginPlay()
{
    Super::BeginPlay();
    
    // 获取模块并创建流媒体
    if (UE::PixelStreaming2::IPixelStreaming2Module::IsAvailable())
    {
        UE::PixelStreaming2::IPixelStreaming2Module& PS2Module = UE::PixelStreaming2::IPixelStreaming2Module::Get();
        MyStreamer = PS2Module.CreateStreamer(TEXT("DemoStreamer"));
        
        if (MyStreamer)
        {
            MyStreamer->SetConnectionURL(TEXT("ws://localhost:8888"));
            MyStreamer->SetStreamFPS(30);
            MyStreamer->StartStreaming();
        }
    }
}

void AMyPS2Actor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MyStreamer)
    {
        MyStreamer->StopStreaming();
        MyStreamer.Reset();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

Pixel Streaming 2 插件由多个模块组成，它们之间存在依赖关系。对于使用者而言，**通常只需依赖主模块 `PixelStreaming2`**，它会传递性地引入其他必要的核心模块。在 `.Build.cs` 文件中添加如下依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "PixelStreaming2" });
```

插件内部的模块依赖关系如下（对使用者透明）：

| 模块 | 用途 |
|---|---|
| `PixelStreaming2` | 主模块，提供核心框架和集成。 |
| `PixelStreaming2Core` | 核心接口和类型定义（如 `IPixelStreaming2Streamer`）。 |
| `PixelStreaming2RTC` | WebRTC 通信层封装。 |
| `PixelStreaming2Input` | 处理来自浏览器的输入（鼠标、键盘、触摸、手柄）。 |
| `PixelStreaming2Servers` | 内置信令和 Web 服务器的实现。 |
| `PixelStreaming2Settings` | 插件的设置和配置资产。 |
| `EpicRtc` | Epic 定制的 WebRTC 依赖库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量转换为浮点数产生警告的代码。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the … | 虚拟制作：将相关资产迁移至新分类，属于引擎级资产整理。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString，属于底层 JSON 库改进。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中可能导致乱码输出的问题。 |

### 维护评价

**活跃维护**。Pixel Streaming 2 于 2024 年 9 月作为全新插件引入，旨在替代旧的 Pixel Streaming 插件。尽管创建时间不长（约 2 年），但从近期（2026 年 4-5 月）的提交记录可以看出，它仍在**持续进行功能完善和 bug 修复**（如输入处理、编译警告修复）。其模块化设计也表明了长期维护的意图。该插件是 Epic 官方主推的云渲染/流式传输解决方案，**推荐在新项目中使用**，以取代旧版 Pixel Streaming 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)