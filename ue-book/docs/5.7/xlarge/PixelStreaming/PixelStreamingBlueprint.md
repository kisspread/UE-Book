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
| 创建时间 | 2025-08-29（根据提供信息；实际引擎版本中此插件历史更久） |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming) | |

---

## 用途

PixelStreamingBlueprint 模块为 Pixel Streaming 插件提供蓝图可访问的接口。它封装了核心流送逻辑（`IPixelStreamingStreamer`），通过一个蓝图节点化的 Actor 组件（`UPixelStreamingStreamerComponent`）和多种视频输入类（如渲染目标、后缓冲、媒体捕获）让设计师和蓝图用户能够轻松在关卡中配置、启动/停止流送，而无需编写 C++ 代码。该模块解决了纯蓝图项目中接入 WebRTC 流送的高门槛问题，使得非程序员也能快速搭建像素流送功能。

## 使用场景

- **云游戏/远程渲染**：通过蓝图快速搭建游戏流送服务器，将 UE 画面实时编码并通过 WebRTC 推送到浏览器。
- **可视化协作**：在编辑器中预览流送效果，使用组件控制多路流送（多个摄像机视角）。
- **教育培训**：学生无需安装完整引擎即可通过浏览器体验 3D 场景，讲师可通过蓝图管理流送开关。
- **自定义视频源**：利用视频输入子类（渲染目标、后缓冲、媒体捕获）灵活选择流送内容。

## 蓝图用法

所有蓝图可调用函数和可绑定事件均定义在 `UPixelStreamingStreamerComponent` 中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Streaming` | 开始建立 WebRTC 连接并编码推流 | `UPixelStreamingStreamerComponent` |
| `Stop Streaming` | 断开所有客户端连接并停止流送 | `UPixelStreamingStreamerComponent` |
| `Is Streaming` | 返回当前是否正在流送 | `UPixelStreamingStreamerComponent` |
| `Is Signalling Connected` | 检查与信令服务器的连接状态 | `UPixelStreamingStreamerComponent` |
| `Force Key Frame` | 立即生成一个关键帧（用于低延迟场景） | `UPixelStreamingStreamerComponent` |
| `Freeze Stream` (Texture) | 冻结画面，显示指定静态纹理 | `UPixelStreamingStreamerComponent` |
| `Unfreeze Stream` | 恢复实时流送画面 | `UPixelStreamingStreamerComponent` |
| `Send Player Message` | 向所有连接的玩家发送自定义消息（Type + Descriptor） | `UPixelStreamingStreamerComponent` |
| `Get Id` | 返回当前流器 ID | `UPixelStreamingStreamerComponent` |

### 事件绑定

| 事件 | 说明 |
|---|---|
| `On Streaming Started` | 流送成功建立后触发（单播委托） |
| `On Streaming Stopped` | 流送停止后触发（单播委托） |
| `On Input Received` | 收到来自任何客户端的输入数据时触发（多播委托，提供 PlayerId、数据类型和原始数据） |

### 使用示例（蓝图描述）

1. **基本启动流程**：
   - 在关卡中放置一个 Actor 并挂载 `Pixel Streaming Streamer Component`（蓝图可创建）。
   - 在 Event BeginPlay 中调用 `Start Streaming`。
   - 绑定 `On Streaming Started` 事件以在控制台打印“流送已启动”。

2. **动态切换视频源**：
   - 组件暴露 `Video Input` 属性（`UPixelStreamingStreamerVideoInput` 派生类）。
   - 在细节面板中选择“Render Target Video Input”或“Back Buffer Video Input”。
   - 若选择“Render Target”，需指定渲染目标纹理。

3. **冻结/解冻画面**：
   - 调用 `Freeze Stream` 并传入一个 `Texture2D` 资产作为冻结画面。
   - 需要恢复时调用 `Unfreeze Stream`。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingStreamerComponent.h"
#include "PixelStreamingStreamerVideoInputRenderTarget.h" // 按需引入视频输入类
```

### 基本用法

以下代码演示如何在 C++ Actor 中创建并使用 `UPixelStreamingStreamerComponent`（来源：`Source/PixelStreamingBlueprint/Private/PixelStreamingStreamerComponent.h` 及实现）。

```cpp
// MyStreamingActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyStreamingActor.generated.h"

UCLASS()
class AMYSTREAMINGACTOR : public AActor
{
    GENERATED_BODY()
public:
    AMYSTREAMINGACTOR();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Streaming")
    class UPixelStreamingStreamerComponent* StreamerComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Streaming")
    class UTextureRenderTarget2D* RenderTarget;
};
```

```cpp
// MyStreamingActor.cpp
#include "MyStreamingActor.h"
#include "PixelStreamingStreamerComponent.h"
#include "PixelStreamingStreamerVideoInputRenderTarget.h"

AMYSTREAMINGACTOR::AMYSTREAMINGACTOR()
{
    // 创建组件
    StreamerComponent = CreateDefaultSubobject<UPixelStreamingStreamerComponent>(TEXT("StreamerComponent"));
}

void AMYSTREAMINGACTOR::BeginPlay()
{
    Super::BeginPlay();

    // 设置视频输入为渲染目标（需确保事先创建 RenderTarget）
    if (RenderTarget)
    {
        UPixelStreamingStreamerVideoInputRenderTarget* VideoInput = NewObject<UPixelStreamingStreamerVideoInputRenderTarget>(this);
        VideoInput->Target = RenderTarget;
        StreamerComponent->VideoInput = VideoInput;
    }

    // 绑定事件
    StreamerComponent->OnStreamingStarted.AddLambda([this]()
    {
        UE_LOG(LogTemp, Log, TEXT("Streaming started!"));
    });

    // 启动流送
    StreamerComponent->StartStreaming();
}

void AMYSTREAMINGACTOR::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 停止流送
    if (StreamerComponent)
    {
        StreamerComponent->StopStreaming();
    }
    Super::EndPlay(EndPlayReason);
}
```

### 进阶用法

结合 `OnInputReceived` 多播委托处理自定义玩家输入（来自 `PixelStreamingInput` 模块）：

```cpp
// 在初始化时绑定
StreamerComponent->OnInputReceived.AddLambda([](FPixelStreamingPlayerId PlayerId, uint8 Type, TArray<uint8> Data)
{
    // Type 0x01 表示键盘输入，0x02 表示鼠标等，按需求解析 Data
    UE_LOG(LogTemp, Log, TEXT("Player %s sent input type %d, size %d"), *PlayerId, Type, Data.Num());
});
```

## Demo 示例

以下是一个最小可编译的 Actor 类，演示如何通过 C++ 使用 `UPixelStreamingStreamerComponent` 启动渲染目标流送。请将代码放入您的项目中并添加对 `PixelStreamingBlueprint` 模块的依赖。

### MyStreamingActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyStreamingActor.generated.h"

UCLASS()
class MYPIXELSTREAMING_API AMyStreamingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyStreamingActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

protected:
    UPROPERTY(VisibleAnywhere, Category = "Streaming")
    class UPixelStreamingStreamerComponent* StreamerComponent;

    UPROPERTY(EditAnywhere, Category = "Streaming")
    class UTextureRenderTarget2D* RenderTarget;
};
```

### MyStreamingActor.cpp

```cpp
#include "MyStreamingActor.h"
#include "PixelStreamingStreamerComponent.h"
#include "PixelStreamingStreamerVideoInputRenderTarget.h"

AMyStreamingActor::AMyStreamingActor()
{
    PrimaryActorTick.bCanEverTick = false;
    StreamerComponent = CreateDefaultSubobject<UPixelStreamingStreamerComponent>(TEXT("StreamerComponent"));
}

void AMyStreamingActor::BeginPlay()
{
    Super::BeginPlay();

    if (RenderTarget)
    {
        UPixelStreamingStreamerVideoInputRenderTarget* VideoInput = NewObject<UPixelStreamingStreamerVideoInputRenderTarget>(this);
        VideoInput->Target = RenderTarget;
        StreamerComponent->VideoInput = VideoInput;
    }

    StreamerComponent->StartStreaming();
}

void AMyStreamingActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (StreamerComponent)
    {
        StreamerComponent->StopStreaming();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

在您自己的模块的 `Build.cs` 中，请添加以下独特依赖（标准 Core/Engine/Slate 等已省略）：

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 核心流送逻辑、视频编码、WebRTC 连接管理 |
| `PixelStreamingInput` | 输入接收与转发、`FPixelStreamingPlayerId` 类型 |
| `PixelStreamingServers` | 信令服务器（内嵌或外部）启动管理 |

**注意**：使用本模块时，您的项目或插件需要公开依赖 `PixelStreamingBlueprint`，并确保运行时环境中已加载上述依赖模块。

## 维护状态

### 近期更新

- 2025-09-30 `4bfe7f55` Updating infra scripts to point to new release branch（未涉及代码逻辑）
- 2025-09-25 `1fdac7d5` [PixelCapture, PS, PS2] Fix: MediaCapture could get into a bad state due to use of queues and praying（修复媒体捕获状态问题）
- 2025-09-23 `30db91bd` [PS1, PS2] Fix: Internal signalling server hitting an ensure during creation due FTickableGameObject（修复信令服务器创建时断言）
- 2025-09-23 `cc062cea` [PS1, PS2] Fix a crash in editor when setting the streamID on the command line（修复命令行设置 streamID 时编辑器崩溃）
- 2025-08-29 `32884de4` Changing more uses of RHICreateTexture to RHICmdList.CreateTexture（兼容性更新）

### 维护评价

PixelStreaming 插件是 Epic 官方维护的核心 Media 插件之一，近期提交显示团队持续修复 Bug 并进行底层适配。用户可通过蓝图组件快速部署流送功能，无需深入 C++ 细节。由于该插件依赖 WebRTC 和硬件编码器，某些边缘情况（如非 NVIDIA GPU / 移动平台）可能有限制，但官方文档和社区资源丰富。**推荐使用**，尤其适合需要蓝图驱动的流送项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming/Tests)（部分测试可能位于引擎 Tests 目录）