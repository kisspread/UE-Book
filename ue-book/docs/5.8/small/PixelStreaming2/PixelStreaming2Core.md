# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模块化架构） |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Epic Games 为 Unreal Engine 5.6 及更高版本全新重构的像素流送解决方案。它解决了原版 Pixel Streaming 在架构扩展性、跨平台支持和 WebRTC 集成方面的局限性。其核心目的是将 Unreal Engine 应用程序的实时视频和音频流（包括渲染画面和引擎音效）通过 WebRTC 协议，低延迟地推送到任何兼容的 WebRTC 终端（主要是现代网页浏览器），从而实现无需在客户端安装高性能显卡的云游戏、远程应用预览、实时协作和分布式渲染等场景。

**与旧版的核心区别**：
1.  **模块化架构**：拆分为多个独立模块（Core, RTC, Input, Servers等），便于扩展和维护。
2.  **EpicRtc**：集成了 Epic 自己的、经过优化的 WebRTC 实现，减少了对第三方库的依赖。
3.  **更清晰的抽象**：通过 `IPixelStreaming2Streamer`, `IPixelStreaming2VideoProducer` 等接口，将流送控制、视频/音频生产与消费解耦，开发者可以更灵活地定制数据源和输出目标。
4.  **改进的输入处理**：专门的 `PixelStreaming2Input` 模块，更好地处理来自浏览器的键盘、鼠标、游戏手柄输入。

## 使用场景

-   **云游戏/应用串流**：用户无需在本地设备安装庞大的客户端，通过浏览器即可体验高质量的 UE 应用。
-   **实时演示与评审**：设计师、开发者可以将编辑器或应用画面实时分享给远端团队成员或客户，进行实时讨论和反馈。
-   **数字孪生与远程控制**：将工厂、城市等数字孪生体的实时渲染画面推送给监控中心，并接收远程控制指令。
-   **互动直播与教育**：结合输入反馈，实现观众可参与互动的直播内容或虚拟实验室。
-   **多平台分发**：一套 UE 应用同时为 PC、移动设备和 VR/AR 头显提供服务。

## 蓝图用法

**重要说明**：`PixelStreaming2Core` 模块主要定义了核心接口（Interface），这些接口本身没有暴露蓝图节点。真正的蓝图可调用函数和属性通常位于更高级的、实现这些接口的模块中（例如 `PixelStreaming2` 模块）。根据提供的核心模块头文件分析，没有发现 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。要使用蓝图控制像素流送，需要查找其他模块（如 `PixelStreaming2`）的蓝图支持类。一个典型的蓝图工作流可能如下：

1.  获取或创建一个 Streamer 对象。
2.  设置视频源（Video Producer）。
3.  设置连接信令服务器的 URL。
4.  开始流送。

**示例逻辑（概念性描述）**：
1.  使用 `Get Pixel Streaming Module` 节点获取模块接口。
2.  调用 `Create Streamer` 或 `Find Streamer` 节点。
3.  通过 `Set Video Producer` 节点绑定一个视频输出源（例如一个 `MediaTexture` 或自定义的生产者）。
4.  使用 `Set Connection URL` 节点设置信令服务器地址（如 `ws://localhost:80`）。
5.  调用 `Start Streaming` 节点启动流送。

## C++ 用法

核心用法围绕 `IPixelStreaming2Streamer` 接口展开。

### 头文件引入

```cpp
#include "PixelStreaming2Core.h"
#include "IPixelStreaming2Module.h"
#include "IPixelStreaming2Streamer.h"
#include "IPixelStreaming2VideoProducer.h"
```

### 基本用法

以下代码展示了如何通过模块接口创建 Streamer 并启动流送。

*来源：基于 `IPixelStreaming2Streamer.h` 接口设计*

```cpp
// 1. 获取模块接口
UE::PixelStreaming2::IPixelStreaming2Module& PSModule = UE::PixelStreaming2::IPixelStreaming2Module::Get();

// 2. 创建一个默认的 Streamer（例如，用于视频流）
TSharedPtr<UE::PixelStreaming2::IPixelStreaming2Streamer> MyStreamer = PSModule.CreateStreamer(TEXT("MyGameStreamer"));
if (MyStreamer.IsValid())
{
    // 3. 初始化 Streamer
    MyStreamer->Initialize();

    // 4. 设置信令服务器 URL
    MyStreamer->SetConnectionURL(TEXT("ws://signalling-server.example.com:80"));

    // 5. （可选）设置视频生产者，例如将引擎的后缓冲帧推送出去
    // TSharedPtr<IPixelStreaming2VideoProducer> VideoProducer = ...;
    // MyStreamer->SetVideoProducer(VideoProducer);

    // 6. 开始流送
    MyStreamer->StartStreaming();

    // 监听流送状态变化事件
    MyStreamer->OnStreamingStarted().AddLambda([](IPixelStreaming2Streamer* Streamer)
    {
        UE_LOG(LogTemp, Log, TEXT("Pixel Streaming started for %s"), *Streamer->GetId());
    });

    MyStreamer->OnStreamingStopped().AddLambda([](IPixelStreaming2Streamer* Streamer)
    {
        UE_LOG(LogTemp, Log, TEXT("Pixel Streaming stopped for %s"), *Streamer->GetId());
    });
}
```

### 进阶用法

**自定义视频生产者与事件监听**：

你可以实现 `IPixelStreaming2VideoProducer` 接口来提供自定义的视频帧。

```cpp
#include "IPixelStreaming2VideoProducer.h"

// 自定义视频生产者类
class FMyGameVideoProducer : public IPixelStreaming2VideoProducer
{
public:
    virtual EVideoProducerCapabilities GetCapabilities() override
    {
        return EVideoProducerCapabilities::Default; // 或者 ProducePreprocessedFrames，如果帧已预处理
    }

    virtual FString ToString() override
    {
        return TEXT("MyGameSceneCapture");
    }

    // 当有新帧时调用此方法
    void CaptureAndPushFrame()
    {
        // ... 获取或生成一帧数据 (IPixelCaptureInputFrame) ...
        // IPixelCaptureInputFrame* NewFrame = ...;
        // PushFrame(*NewFrame);
    }
};

// 使用自定义生产者
TSharedPtr<FMyGameVideoProducer> MyProducer = MakeShared<FMyGameVideoProducer>();
MyStreamer->SetVideoProducer(MyProducer);
```

**向连接的玩家发送消息**：

```cpp
// 向所有玩家发送消息
FString MessageType = TEXT("GameEvent");
FString Payload = TEXT("{\"score\": 100}");
MyStreamer->SendAllPlayersMessage(MessageType, Payload);

// 向特定玩家发送消息
TArray<FString> Players = MyStreamer->GetConnectedPlayers();
if (Players.Num() > 0)
{
    MyStreamer->SendPlayerMessage(Players[0], TEXT("PrivateMessage"), TEXT("Hello Player 1!"));
}
```

**处理来自浏览器的输入**：

输入处理通常由 `PixelStreaming2Input` 模块和 Streamer 的输入处理器（`IPixelStreaming2InputHandler`）共同完成。你可能需要设置自定义的输入处理器来映射浏览器事件。

```cpp
// 获取并设置自定义输入处理器
TSharedPtr<IPixelStreaming2InputHandler> MyInputHandler = /* ... */;
MyStreamer->SetInputHandler(MyInputHandler);

// 从 Streamer 获取输入处理器
TWeakPtr<IPixelStreaming2InputHandler> CurrentHandler = MyStreamer->GetInputHandler();
```

## Demo 示例

一个最小的、可运行的 C++ 示例，用于在 `BeginPlay` 时启动像素流送。

**MyPixelStreamingActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IPixelStreaming2Streamer.h"
#include "MyPixelStreamingActor.generated.h"

UCLASS()
class MYPROJECT_API AMyPixelStreamingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPixelStreamingActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<UE::PixelStreaming2::IPixelStreaming2Streamer> Streamer;
    FDelegateHandle StreamingStartedHandle;
};
```

**MyPixelStreamingActor.cpp**
```cpp
#include "MyPixelStreamingActor.h"
#include "PixelStreaming2Core.h"
#include "IPixelStreaming2Module.h"

AMyPixelStreamingActor::AMyPixelStreamingActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyPixelStreamingActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取像素流送模块
    UE::PixelStreaming2::IPixelStreaming2Module& PSModule = UE::PixelStreaming2::IPixelStreaming2Module::Get();

    // 创建并初始化 Streamer
    Streamer = PSModule.CreateStreamer(TEXT("DemoStreamer"));
    if (Streamer.IsValid())
    {
        Streamer->Initialize();

        // 监听流送开始事件
        StreamingStartedHandle = Streamer->OnStreamingStarted().AddLambda([](IPixelStreaming2Streamer* S)
        {
            UE_LOG(LogTemp, Display, TEXT("Pixel Streaming started! ID: %s"), *S->GetId());
        });

        // 设置连接地址（默认使用本地信令服务器）
        Streamer->SetConnectionURL(TEXT("ws://localhost:80"));

        // 启动流送
        Streamer->StartStreaming();
        UE_LOG(LogTemp, Display, TEXT("Attempting to start Pixel Stream..."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Pixel Streaming Streamer."));
    }
}

void AMyPixelStreamingActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Streamer.IsValid())
    {
        // 移除事件委托
        if (StreamingStartedHandle.IsValid())
        {
            Streamer->OnStreamingStarted().Remove(StreamingStartedHandle);
        }
        // 停止并销毁流送器
        Streamer->StopStreaming();
        Streamer.Reset();
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

`PixelStreaming2Core` 模块是核心接口层，本身依赖较少。但要构建完整的像素流送功能，你的项目或模块通常需要依赖以下（根据 `PixelStreaming2` 主模块推断）：

| 模块 | 用途 |
|---|---|
| `PixelStreaming2` | 主模块，集成核心、信令、编码等功能 |
| `PixelStreaming2Core` | 核心接口定义（`IPixelStreaming2Streamer` 等） |
| `PixelStreaming2RTC` | WebRTC 通信层实现 |
| `PixelStreaming2Input` | 浏览器输入事件处理 |
| `PixelStreaming2Servers` | 信令服务器等服务器端逻辑 |
| `EpicRtc` | Epic 自己的 WebRTC 实现 |

**典型项目依赖**：
在你的模块 `.Build.cs` 文件中，至少需要添加：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "PixelStreaming2Core", "PixelStreaming2" });
// 如果涉及输入，可能还需要 "PixelStreaming2Input"
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器获取默认目标窗口的方法错误 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：将多项虚拟制片资产移至不同分类并进行迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中可能导致输出乱码的问题 |

### 维护评价

- **活跃度**：**活跃维护中**。插件创建于 2024 年 9 月，非常年轻。从 git 历史看，直到 2026 年 5 月仍有持续的功能性更新和 Bug 修复，表明 Epic Games 将其作为重点模块在积极开发和维护。
- **成熟度**：作为 UE 5.6+ 的新特性，它正在快速迭代以完善功能和提升稳定性。代码中存在一些已废弃（`DEPRECATED`）的接口，说明 API 尚在演进中。
- **推荐程度**：**强烈推荐**用于新的、需要像素流送功能的 UE 项目。它代表了 UE 官方对这一技术的未来方向，相较于旧版具有更好的架构和扩展性。对于正在使用旧版 Pixel Streaming 的项目，建议规划迁移至新版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)