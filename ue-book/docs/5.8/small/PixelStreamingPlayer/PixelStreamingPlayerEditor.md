# Pixel Streaming Player

> Support for receiving a pixel streaming stream and displaying it in game.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流播放器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体纹理工厂） |
| 模块 | `PixelStreamingPlayer` (Runtime), `PixelStreamingPlayerEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer) | |

## 用途
该插件为游戏客户端（Player）提供接收和显示像素流（Pixel Streaming）视频流的功能。它允许一个 UE 应用程序作为“接收端”，去播放由另一个 UE 应用程序（作为“发送端”或“流媒体服务器”）推送的实时视频流。这与官方 Pixel Streaming 插件主要用于将 UE 应用程序推流至浏览器的角色相反，实现了双向的像素流通信场景。

## 使用场景
- **跨平台游玩与演示**：在一台配置较低的设备（如移动设备、旧电脑）上，通过网络连接并操控运行在高端 PC 或服务器上的 UE 游戏。
- **远程监控与调试**：作为监控客户端，实时查看远程运行的 UE 应用程序画面，用于测试或演示。
- **混合架构应用**：在需要将渲染与逻辑分离的复杂应用架构中，作为接收渲染结果的客户端程序。
- **教育演示**：教师演示一个复杂的 UE 场景，学生客户端无需安装完整引擎即可实时观看和交互。

## 蓝图用法
从当前提供的源码片段（PixelStreamingMediaTextureFactory）来看，该插件主要通过编辑器工厂类集成，未发现直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。核心的流接收、解码和渲染逻辑很可能封装在 `PixelStreamingPlayer` 运行时模块的 C++ 层。

## C++ 用法

### 头文件引入
```cpp
#include "PixelStreamingPlayer.h"
```

### 基本用法
基于插件描述和模块结构，典型的用法是创建一个播放器组件或子系统来管理连接和显示。以下为概念性示例（需根据实际API调整）：
```cpp
// 假设存在一个播放器类，用于管理连接
#include "PixelStreamingPlayer.h"
// 通常还会包含用于显示纹理的MediaTexture或Slate Widget头文件

// 创建一个播放器实例
TSharedPtr<FPixelStreamingPlayer> Player = MakeShared<FPixelStreamingPlayer>();

// 配置流媒体服务器地址
FString SignallingServerURL = TEXT("ws://your-signalling-server:8888");

// 启动连接
Player->Connect(SignallingServerURL);

// 获取接收到的视频纹理用于显示
// UTexture2D* VideoTexture = Player->GetVideoTexture();
// ... 将纹理应用到材质或 UI 上
```

### 进阶用法
进阶用法可能涉及处理连接事件、设置解码参数、管理多个流等。由于没有详细的头文件，具体 API 需参考引擎源码中 `PixelStreamingPlayer` 模块的公共接口。

## Demo 示例

以下是一个最小化的 C++ Actor 示例，演示如何集成 `PixelStreamingPlayer`。请注意，此示例基于对插件结构的合理推断，具体类名和方法需以实际头文件为准。

**MyPixelStreamReceiver.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPixelStreamReceiver.generated.h"

// 前置声明
class FPixelStreamingPlayer;
class UMediaTexture;

UCLASS()
class AMyPixelStreamReceiver : public AActor
{
    GENERATED_BODY()

public:
    AMyPixelStreamReceiver();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, Category = "Pixel Streaming")
    FString SignallingServerURL = TEXT("ws://127.0.0.1:8888");

private:
    TSharedPtr<FPixelStreamingPlayer> StreamingPlayer;

    UPROPERTY()
    UMediaTexture* VideoOutputTexture;
};
```

**MyPixelStreamReceiver.cpp**
```cpp
#include "MyPixelStreamReceiver.h"
#include "PixelStreamingPlayer.h" // 关键头文件
// #include "MediaTexture.h" // 如果使用 UMediaTexture 进行输出

AMyPixelStreamReceiver::AMyPixelStreamReceiver()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyPixelStreamReceiver::BeginPlay()
{
    Super::BeginPlay();

    // 创建播放器实例
    StreamingPlayer = MakeShared<FPixelStreamingPlayer>();

    // 设置输出纹理（具体创建方式取决于插件提供的API）
    // VideoOutputTexture = NewObject<UMediaTexture>(this);
    // StreamingPlayer->SetVideoTexture(VideoOutputTexture);

    // 启动连接
    StreamingPlayer->Connect(SignallingServerURL);

    UE_LOG(LogTemp, Log, TEXT("Pixel Streaming Player: Connecting to %s"), *SignallingServerURL);
}

void AMyPixelStreamReceiver::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (StreamingPlayer.IsValid())
    {
        StreamingPlayer->Disconnect();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyPixelStreamReceiver::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (StreamingPlayer.IsValid())
    {
        // 可能需要每帧处理网络数据或更新纹理
        // StreamingPlayer->Tick();
    }
}
```

## 模块依赖
根据 `.uplugin` 的 `Plugins` 字段，该插件显式依赖：

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 核心依赖，提供了像素流的基础通信协议、信令和编解码框架。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于引擎级编译修复。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers... | 添加缺失的渲染相关头文件包含和前向声明，解决编译问题。 |
| 2025-08-26 | `0a8b2cd9` | Deprecating the functions RHICreateTextureReference and RHIUpdateTextureReference... | 废弃了RHI纹理引用函数，是底层渲染API的清理工作。 |
| 2025-04-10 | `ea97db60` | Movie Render Queue: High-res tiling support... | 非直接相关改动，属于电影渲染队列的更新。 |
| 2024-09-04 | `ffe80807` | [PixelStreaming] Fix: Undeprecate as VCam is still depending on it | 重新启用了一个被标记为废弃的函数，因为VCam模块仍在使用。 |

### 维护评价
- **状态**：实验性/Beta。创建于 2023 年初，标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`。
- **活跃度**：近半年的提交均为编译修复和底层API迁移，**没有实质性的功能更新或bug修复**。最后一次明确的功能性维护记录在 2024 年 9 月。
- **风险**：作为实验性功能，API 可能不稳定。由于长时间缺乏实质性更新，其与最新引擎版本的兼容性和新功能的支持度存疑。
- **建议**：**不推荐在生产项目中使用**。仅适用于研究、原型开发或对实验性功能有特定需求的场景。使用前务必在当前引擎版本中进行充分测试。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)