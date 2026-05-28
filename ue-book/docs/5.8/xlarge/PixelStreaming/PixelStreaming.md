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
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming) | |

## 用途

Pixel Streaming 插件的核心功能是将 Unreal Engine 应用程序的实时渲染画面和音频，通过 WebRTC 协议压缩并传输到支持 WebRTC 的客户端（例如网页浏览器）。它解决的核心问题是：**如何让远程用户无需在本地安装高性能客户端，仅通过浏览器就能低延迟地访问、查看甚至交互 UE 应用程序**。

该插件不仅仅是一个简单的视频流，它还是一个完整的交互式远程访问解决方案。它包括：
1.  **视频编码与传输**：捕获 UE 的渲染后缓冲区（BackBuffer），使用硬件或软件编码器（如 H.264, VP8, AV1）进行压缩，并通过 WebRTC 的 Data Channel 发送。
2.  **音频捕获与传输**：捕获 UE 的音频子系统（Submix）输出，并与浏览器客户端的麦克风输入（可选）进行混合后传输。
3.  **输入交互**：接收来自浏览器端的键盘、鼠标、触摸等输入事件，并将其转发给 UE 应用程序进行处理，实现远程操控。
4.  **信令服务**：通过 WebSocket 与外部的信令服务器（Signalling Server）通信，用于客户端与 UE 应用之间建立和管理 WebRTC 连接（如 SDP 交换、ICE 候选）。
5.  **流管理与控制**：支持同时管理多个“Streamer”（流实例）和“Player”（连接客户端），并提供质量控制、数据通道、冻结帧等高级功能。

其存在价值在于提供了一种轻量级、跨平台、低延迟的远程访问方案，广泛应用于云游戏、远程应用演示、虚拟桌面、建筑/工程可视化等领域。

## 使用场景

-   **云游戏服务**：你需要将完整的 UE 游戏体验通过浏览器提供给玩家 → 用 Pixel Streaming。
-   **远程应用演示**：你需要向客户展示一个交互式的 UE 应用（如产品配置器、建筑漫游），而客户无需安装 → 用 Pixel Streaming。
-   **虚拟制作协作**：导演或设计师需要远程查看并控制虚拟制片场景中的摄像机 → 用 Pixel Streaming。
-   **教学与培训**：你需要创建可远程交互的 UE 模拟培训程序 → 用 Pixel Streaming。
-   **轻量级客户端**：目标用户设备性能有限，无法运行 UE 原生客户端，但可以运行浏览器 → 用 Pixel Streaming。

## 蓝图用法

### 核心节点

以下节点主要来自 `UPixelStreamingBlueprints` 静态函数库，可直接在蓝图中调用。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Force Key Frame` | 强制所有流发送一个关键帧，用于快速解决画面花屏等问题。 | `UPixelStreamingBlueprints` |
| `Freeze Frame` | 冻结流画面。可传入一张纹理作为静态画面，否则使用当前后缓冲。常用于掩盖加载卡顿。 | `UPixelStreamingBlueprints` |
| `Unfreeze Frame` | 解除流画面的冻结状态。 | `UPixelStreamingBlueprints` |
| `Send File` | 通过数据通道向所有连接的客户端发送一个文件（基于文件路径）。 | `UPixelStreamingBlueprints` |
| `Send File As Byte Array` | 通过数据通道向所有连接的客户端发送一个字节数组（模拟文件）。 | `UPixelStreamingBlueprints` |
| `Kick Player` | 踢出一个指定的客户端连接。 | `UPixelStreamingBlueprints` |
| `Get Connected Players` | 获取当前连接到默认流的所有客户端 ID 列表。 | `UPixelStreamingBlueprints` |
| `Get Default Streamer ID` | 获取默认流的 ID。 | `UPixelStreamingBlueprints` |
| `Get Pixel Streaming Delegates` | 获取 `UPixelStreamingDelegates` 单例，用于监听像素流送的各类事件（如连接建立、断开、统计变化等）。 | `UPixelStreamingBlueprints` |

### 使用示例（蓝图描述）

1.  **监听新客户端连接**：
    *   调用 `Get Pixel Streaming Delegates` 节点获取委托对象。
    *   从委托对象拖出线，绑定到 `OnNewConnection` 事件。
    *   事件触发时，`StreamerId` 和 `PlayerId` 输出可以用来识别是哪个流和哪个玩家连接了。

2.  **向指定客户端发送消息**：
    *   先通过 `Get Connected Players` 或监听 `OnNewConnection` 获取到目标 `PlayerId`。
    *   调用一个自定义函数（如上文 C++ 中的 `SendPlayerMessage`），将 `PlayerId` 和自定义消息（如 JSON 字符串）传入，该消息会通过数据通道发送给浏览器端的 JavaScript 代码。

3.  **实现加载界面**：
    *   在关卡开始加载时，调用 `Freeze Frame`，并传入一张“加载中”的纹理。
    *   加载完成后，调用 `Unfreeze Frame` 恢复实时视频流。

## C++ 用法

### 头文件引入

```cpp
// 核心模块接口
#include "IPixelStreamingModule.h"
// 流接口
#include "IPixelStreamingStreamer.h"
// 蓝图函数库
#include "PixelStreamingBlueprints.h"
// 委托与事件
#include "PixelStreamingDelegates.h"
// 音频组件
#include "PixelStreamingAudioComponent.h"
// 输入组件
#include "PixelStreamingInputComponent.h"
```

### 基本用法

```cpp
// 来源: 测试用例或文档示例

// 1. 检查模块是否可用并获取模块接口
if (IPixelStreamingModule::IsAvailable())
{
    IPixelStreamingModule& PSModule = IPixelStreamingModule::Get();
    
    // 2. 等待模块就绪（流初始化完成）
    if (PSModule.IsReady())
    {
        // 模块就绪，可以安全使用
        PSModule.StartStreaming(); // 启动所有流
    }
    else
    {
        // 绑定就绪事件
        PSModule.OnReady().AddLambda([](IPixelStreamingModule& Module) {
            Module.StartStreaming();
        });
    }
}
```

### 进阶用法

```cpp
// 来源: 基于 IPixelStreamingStreamer 接口的典型用法

// 1. 创建并配置一个自定义的流实例
FString StreamerId = TEXT("MyCustomStreamer");
TSharedPtr<IPixelStreamingStreamer> MyStreamer = IPixelStreamingModule::Get().CreateStreamer(StreamerId);

if (MyStreamer.IsValid())
{
    // 2. 设置信令服务器 URL（通常从配置读取）
    MyStreamer->SetSignallingServerURL(TEXT("ws://localhost:8888"));
    
    // 3. 配置流属性
    MyStreamer->SetStreamFPS(60); // 设置流帧率
    
    // 4. 设置视频输入源（通常使用默认的后缓冲，但可自定义）
    // MyStreamer->SetVideoInput(MyCustomVideoInput);
    
    // 5. 绑定流事件
    MyStreamer->OnPreConnection().AddLambda([](IPixelStreamingStreamer* Streamer) {
        UE_LOG(LogTemp, Log, TEXT("Streamer %s: 准备连接信令服务器..."), *Streamer->GetId());
    });
    
    MyStreamer->OnStreamingStarted().AddLambda([](IPixelStreamingStreamer* Streamer) {
        UE_LOG(LogTemp, Log, TEXT("Streamer %s: 流已开始，等待客户端连接。"), *Streamer->GetId());
    });
    
    // 6. 启动此流
    MyStreamer->StartStreaming();
    
    // 7. 在运行时向所有连接的客户端发送消息
    MyStreamer->SendPlayerMessage(0 /* Type */, TEXT("{\"message\": \"Hello from UE!\"}"));
    
    // 8. 监听来自客户端的数据通道消息
    MyStreamer->OnInputReceived.AddLambda([](FPixelStreamingPlayerId PlayerId, uint8 Type, const TArray<uint8>& Data) {
        // 处理来自特定玩家的自定义数据
        FString DataStr = FBase64::Encode(Data);
        UE_LOG(LogTemp, Log, TEXT("Received data from player %s: %s"), *PlayerId, *DataStr);
    });
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何初始化 Pixel Streaming 并监听连接事件。

**MyPixelStreamingActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IPixelStreamingModule.h"
#include "MyPixelStreamingActor.generated.h"

UCLASS()
class AMyPixelStreamingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPixelStreamingActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void OnPixelStreamingReady();
    void OnNewConnection(FString StreamerId, FString PlayerId, bool bQualityController);

    FDelegateHandle ReadyDelegateHandle;
    FDelegateHandle ConnectionDelegateHandle;
};
```

**MyPixelStreamingActor.cpp**
```cpp
#include "MyPixelStreamingActor.h"
#include "IPixelStreamingModule.h"
#include "PixelStreamingDelegates.h"

AMyPixelStreamingActor::AMyPixelStreamingActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyPixelStreamingActor::BeginPlay()
{
    Super::BeginPlay();

    if (IPixelStreamingModule::IsAvailable())
    {
        IPixelStreamingModule& PSModule = IPixelStreamingModule::Get();

        // 绑定就绪事件
        ReadyDelegateHandle = PSModule.OnReady().AddUObject(this, &AMyPixelStreamingActor::OnPixelStreamingReady);

        // 如果已经就绪，直接调用
        if (PSModule.IsReady())
        {
            OnPixelStreamingReady();
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("PixelStreaming plugin is not available!"));
    }
}

void AMyPixelStreamingActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理委托
    if (IPixelStreamingModule::IsAvailable())
    {
        IPixelStreamingModule& PSModule = IPixelStreamingModule::Get();
        PSModule.OnReady().Remove(ReadyDelegateHandle);

        UPixelStreamingDelegates* Delegates = PSModule.IsReady() ? UPixelStreamingDelegates::GetPixelStreamingDelegates() : nullptr;
        if (Delegates)
        {
            Delegates->OnNewConnectionNative.Remove(ConnectionDelegateHandle);
        }
    }

    Super::EndPlay(EndPlayReason);
}

void AMyPixelStreamingActor::OnPixelStreamingReady()
{
    UE_LOG(LogTemp, Log, TEXT("Pixel Streaming Module is ready!"));
    
    // 模块就绪后，监听客户端连接事件
    UPixelStreamingDelegates* Delegates = UPixelStreamingDelegates::GetPixelStreamingDelegates();
    if (Delegates)
    {
        // 使用 C++ 原生委托（性能更好）
        ConnectionDelegateHandle = Delegates->OnNewConnectionNative.AddUObject(this, &AMyPixelStreamingActor::OnNewConnection);
    }
}

void AMyPixelStreamingActor::OnNewConnection(FString StreamerId, FString PlayerId, bool bQualityController)
{
    UE_LOG(LogTemp, Log, TEXT("New client connected via streamer '%s'! Player ID: %s. Is Quality Controller: %s"),
        *StreamerId, *PlayerId, bQualityController ? TEXT("True") : TEXT("False"));

    // 你可以在这里向新连接的客户端发送欢迎消息
    if (IPixelStreamingModule::IsAvailable())
    {
        TSharedPtr<IPixelStreamingStreamer> Streamer = IPixelStreamingModule::Get().FindStreamer(StreamerId);
        if (Streamer.IsValid())
        {
            Streamer->SendPlayerMessage(PlayerId, 0 /* 自定义消息类型 */, TEXT("{\"status\": \"welcome\"}"));
        }
    }
}
```

## 模块依赖

使用 Pixel Streaming 插件时，你的项目模块通常无需额外依赖，因为该插件的设计是自包含的。但是，如果你需要在自己的 C++ 模块中深度集成（例如使用 `FPixelStreamingPeerConnection` 进行高级控制），可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `WebRTC` | 提供核心的 WebRTC 协议栈，Peer Connection，SDP，ICE 等功能。Pixel Streaming 的所有网络通信基于此模块。 |
| `PixelCapture` | 提供用于捕获和转换渲染帧（如 RHI 纹理到编码器输入）的框架。Pixel Streaming 的视频输入处理依赖此模块。 |
| `AVCodecsCore` | 提供视频/音频编码器的抽象层。Pixel Streaming 通过它支持不同的硬件和软件编解码器（H264， VP8， AV1 等）。 |
| `MediaUtils` | 提供媒体工具函数。 |

**注意**：`Core`, `CoreUObject`, `Engine`, `Slate`, `UMG` 等常见模块依赖已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复了输入处理器从错误方法获取默认目标窗口的问题，提升了输入处理的准确性。 |
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复了在 PIE（在编辑器中运行）或模拟模式下发生的崩溃问题，增强了稳定性。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数时产生编译警告的代码。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 对虚拟制作资产进行了分类和迁移整理，属于项目组织层面的优化。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了 FJsonObject 以同时支持 FString 和 UE::FSharedString，提升了 JSON 处理的灵活性和性能。 |

### 维护评价

Pixel Streaming 插件自 2019 年从实验文件夹迁移至正式目录后，已成为 Unreal Engine 中一个**成熟且活跃维护**的核心功能。

*   **创建时间**：约 6 年历史，已脱离“实验性”阶段。
*   **最近更新频率**：近期（2026年4-5月）有持续的提交，内容集中在 **Bug 修复**（如崩溃、输入处理错误）和 **代码质量改进**（消除警告、重构）。这表明 Epic 团队仍在持续维护和优化该插件。
*   **维护状态**：**活跃维护中**。尽管近期没有大规模的新功能提交，但对稳定性和兼容性的修复保证了其在生产环境中的可靠性。
*   **已知限制**：
    1.  默认不启用（`EnabledByDefault = false`），需要手动在项目中启用。
    2.  对网络延迟和带宽敏感，用户体验高度依赖于网络条件。
    3.  信令服务器需要用户自行部署或使用 Epic 提供的示例服务器。
    4.  某些高级功能（如 SFU， Simulcast）的配置和使用有一定复杂度。
*   **推荐使用**：**强烈推荐**。对于任何需要远程流式访问 UE 应用场景的项目，Pixel Streaming 都是官方提供且经过大量生产验证的首选方案。其持续的维护也保障了长期使用的可行性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming/Source/PixelStreaming/Private/Tests) (内部测试代码可能未公开)