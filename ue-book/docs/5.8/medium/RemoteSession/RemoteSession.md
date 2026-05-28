# Remote Session

> A plugin for Unreal that allows one instance to act as a thin-client (rendering and input) to a second instance

| 属性 | 值 |
|---|---|
| 中文名 | 远程会话 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例应用） |
| 模块 | `RemoteSession` (Runtime), `RemoteSessionEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-03-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteSession) | |

## 用途

Remote Session 插件实现了一种“瘦客户端”（Thin-Client）架构。它允许一个 Unreal Engine 实例（**Host**，主机）承担全部的游戏逻辑和渲染计算，并将渲染结果（屏幕画面）通过网络流式传输给一个或多个轻量级的引擎实例（**Client**，客户端）。客户端实例接收画面并显示，同时将本地的输入（如键盘、鼠标、触摸、手柄、XR 控制器）操作实时回传给主机，实现远程控制。这种模式常用于将资源密集的渲染任务卸载到高性能主机，而移动设备或低性能PC仅作为显示和输入终端。插件还支持转发 XR 追踪数据和 AR 系统信息，使其可用于远程 XR 设备调试或 MR（混合现实）应用。

## 使用场景

- **远程设备调试与测试**：在 PC 主机上运行 UE5 编辑器或游戏，通过手机或平板作为远程显示和触摸输入设备，快速测试移动端交互。
- **移动设备性能优化**：在 PC 主机上渲染高质量画面，将其流式传输到移动设备，用于展示或评估在低端设备上的实际观感。
- **多机协作演示**：一个主机实例驱动多个客户端实例，用于产品演示、多人评审或分布式显示墙。
- **自动化测试与录制**：通过客户端的输入通道，可以向主机发送预录制的输入事件，用于自动化测试或创建演示回放。
- **远程 XR 体验**：将 PC 主机的 XR 内容流式传输到独立的移动 XR 设备（如手机AR），或将移动端 AR 追踪数据回传给主机进行渲染。

## 蓝图用法

### 核心配置节点 (通过 `URemoteSessionSettings`)

| 属性 | 说明 |
|---|---|
| `HostPort` | 主机监听的 TCP 端口 (默认 2049) |
| `ConnectionTimeout` | 连接超时时间（秒） |
| `bAutoHostWithPIE` | 是否在编辑器中运行游戏时自动启动主机 |
| `bAutoHostWithGame` | 是否在独立游戏启动时自动启动主机 |
| `ImageQuality` | 传输图像质量 (1-100) |
| `FrameRate` | 主机发送图像的最大帧率 |
| `AllowedChannels` / `DeniedChannels` | 控制允许或禁止使用的数据通道 |

### 核心 API 节点 (通过 `IRemoteSessionModule`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitHost` | 在指定端口启动主机，开始监听连接 | `IRemoteSessionModule` |
| `StopHost` | 停止主机服务 | `IRemoteSessionModule` |
| `IsHostRunning` | 查询主机是否正在运行 | `IRemoteSessionModule` |
| `IsHostConnected` | 查询是否有客户端连接到主机 | `IRemoteSessionModule` |
| `CreateClient` | 创建一个客户端并连接到指定主机地址 | `IRemoteSessionModule` |
| `StopClient` | 断开并停止客户端 | `IRemoteSessionModule` |

### 使用示例（蓝图描述）

1.  **主机端蓝图**：
    - 获取 `RemoteSession` 模块引用。
    - 调用 `Init Host` 节点。
    - 通过 `Get Host` 获取主机角色，然后使用 `Get Channel` 节点（如 `Get Image Channel`）获取特定通道（如图像通道），并进行设置（例如设置压缩质量）。
    - 监听 `On Remote Session Connection Change` 委托来处理客户端连接/断开事件。

2.  **客户端端蓝图**：
    - 获取 `RemoteSession` 模块引用。
    - 调用 `Create Client` 节点，输入主机的 IP 地址。
    - 通过返回的客户端角色对象，获取 `Image Channel` 并调用 `Get Host Screen` 节点，将返回的 `UTexture2D` 连接到一个 `Image` 控件以显示远程画面。
    - 客户端会自动捕获本地输入并发送给主机。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteSession.h"
#include "RemoteSessionTypes.h"
```

### 基本用法

以下是启动一个 Remote Session 主机并获取图像通道的示例。

```cpp
// 假设在某个UObject或Actor中
void AMyActor::StartRemoteHost()
{
    // 获取RemoteSession模块
    IRemoteSessionModule& RemoteSessionModule = FModuleManager::GetModuleChecked<IRemoteSessionModule>(TEXT("RemoteSession"));
    
    // 启动主机，默认端口
    RemoteSessionModule.InitHost();
    
    // 获取主机角色
    TSharedPtr<IRemoteSessionRole> HostRole = RemoteSessionModule.GetHost();
    if (HostRole.IsValid())
    {
        // 监听连接变化
        HostRole->RegisterConnectionChangeDelegate(
            FOnRemoteSessionConnectionChange::FDelegate::CreateUObject(this, &AMyActor::OnHostConnectionChanged)
        );
        
        // 获取图像通道
        TSharedPtr<FRemoteSessionImageChannel> ImageChannel = HostRole->GetChannel<FRemoteSessionImageChannel>();
        if (ImageChannel.IsValid())
        {
            // 设置图像质量
            ImageChannel->SetCompressQuality(70);
            
            // 可以设置自定义的图像提供者，或使用默认的帧缓冲区抓取
            // ImageChannel->SetImageProvider(MyCustomProvider);
            ImageChannel->SetFramebufferAsImageProvider(); // 使用默认方式捕获主机屏幕
        }
    }
}

void AMyActor::OnHostConnectionChanged(IRemoteSessionRole* Role, ERemoteSessionConnectionChange Change)
{
    if (Change == ERemoteSessionConnectionChange::Connected)
    {
        UE_LOG(LogTemp, Log, TEXT("Remote Session client connected."));
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Remote Session client disconnected."));
    }
}
```

### 进阶用法

1.  **自定义通道**：可以继承 `IRemoteSessionChannel` 和 `IRemoteSessionChannelFactoryWorker`，使用 `REGISTER_CHANNEL_FACTORY` 宏注册自定义的数据传输通道。
2.  **获取XR追踪数据**：在客户端，可以通过 `FXRTrackingProxy` 获取从主机端传来的XR设备姿态数据，用于驱动本地的相机或模型。
3.  **处理AR数据**：`FARSystemProxy` 允许客户端作为AR数据代理，接收并模拟来自主机的AR追踪信息（如平面检测、特征点）。

## Demo 示例

以下是一个最小化的主机端 Actor 示例，用于启动服务并等待连接。

```cpp
// MyRemoteHostActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IRemoteSessionRole.h"
#include "MyRemoteHostActor.generated.h"

UCLASS()
class MYPROJECT_API AMyRemoteHostActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyRemoteHostActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable, Category = "RemoteSession")
    void StartRemoteSession();

    UFUNCTION(BlueprintCallable, Category = "RemoteSession")
    void StopRemoteSession();

private:
    void OnConnectionChanged(IRemoteSessionRole* Role, ERemoteSessionConnectionChange Change);

    TSharedPtr<IRemoteSessionRole> HostRole;
};
```

```cpp
// MyRemoteHostActor.cpp
#include "MyRemoteHostActor.h"
#include "RemoteSession.h"
#include "Channels/RemoteSessionImageChannel.h"
#include "ImageProviders/RemoteSessionFrameBufferImageProvider.h"

AMyRemoteHostActor::AMyRemoteHostActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyRemoteHostActor::BeginPlay()
{
    Super::BeginPlay();
    // 可以选择在BeginPlay时自动启动
    // StartRemoteSession();
}

void AMyRemoteHostActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopRemoteSession();
    Super::EndPlay(EndPlayReason);
}

void AMyRemoteHostActor::StartRemoteSession()
{
    if (HostRole.IsValid())
    {
        return; // 已经启动
    }

    IRemoteSessionModule& RemoteSessionModule = FModuleManager::GetModuleChecked<IRemoteSessionModule>(TEXT("RemoteSession"));
    
    // 配置支持的通道，这里至少需要图像通道
    TArray<FRemoteSessionChannelInfo> Channels;
    Channels.Add(FRemoteSessionChannelInfo(FRemoteSessionImageChannel::StaticType(), ERemoteSessionChannelMode::Write));
    // Channels.Add(FRemoteSessionChannelInfo(FRemoteSessionInputChannel::StaticType(), ERemoteSessionChannelMode::Read)); // 如需输入
    // Channels.Add(FRemoteSessionChannelInfo(FRemoteSessionXRTrackingChannel::StaticType(), ERemoteSessionChannelMode::Write)); // 如需XR追踪

    // 创建不受模块自动管理的主机，以便我们可以控制其生命周期
    HostRole = RemoteSessionModule.CreateHost(Channels, 2049); // 使用默认端口
    if (HostRole.IsValid())
    {
        HostRole->RegisterConnectionChangeDelegate(
            FOnRemoteSessionConnectionChange::FDelegate::CreateUObject(this, &AMyRemoteHostActor::OnConnectionChanged)
        );
        
        // 获取图像通道并设置提供者
        TSharedPtr<FRemoteSessionImageChannel> ImageChannel = HostRole->GetChannel<FRemoteSessionImageChannel>();
        if (ImageChannel.IsValid())
        {
            // 创建一个基于当前场景视口的图像提供者
            TSharedPtr<FRemoteSessionFrameBufferImageProvider> Provider = MakeShareable(new FRemoteSessionFrameBufferImageProvider(ImageChannel->GetImageSender()));
            ImageChannel->SetImageProvider(Provider);
            // 注意：实际使用中，需要将Provider与正确的ViewPort关联（例如通过FViewportClient）
        }
        
        UE_LOG(LogTemp, Log, TEXT("Remote Session Host started. Waiting for connections..."));
    }
}

void AMyRemoteHostActor::StopRemoteSession()
{
    if (HostRole.IsValid())
    {
        HostRole->Close(TEXT("Actor Destroyed"));
        HostRole.Reset();
    }
}

void AMyRemoteHostActor::OnConnectionChanged(IRemoteSessionRole* Role, ERemoteSessionConnectionChange Change)
{
    switch (Change)
    {
    case ERemoteSessionConnectionChange::Connected:
        UE_LOG(LogTemp, Warning, TEXT("A remote client has connected!"));
        break;
    case ERemoteSessionConnectionChange::Disconnected:
        UE_LOG(LogTemp, Warning, TEXT("The remote client has disconnected."));
        break;
    }
}
```

## 模块依赖

你的项目模块（Build.cs）需要依赖以下模块才能使用 Remote Session：

| 模块 | 用途 |
|---|---|
| `RemoteSession` | 核心远程会话功能，主机、客户端、通道管理 |
| `BackChannel` | Remote Session 底层使用的网络通信库，负责连接、路由和消息序列化 |
| `Networking` | UE 网络库，提供 Socket 支持 |
| `Media` | 可选，用于通过 `URemoteSessionMediaOutput` 接入媒体框架 |
| `LiveLink` | 可选，用于与 LiveLink 通道交互 |
| `HeadMountedDisplay` | 可选，用于处理 XR 追踪通道 |

**依赖示例 (YourModule.Build.cs)**:
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "InputCore",
    "RemoteSession", // 必需
    "BackChannel",   // 必需
    // "Media",       // 按需添加
    // "HeadMountedDisplay" // 按需添加
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `92167537` | Support other analytics providers for RemoteSession | 支持除FEngineAnalytics外的其他分析提供商 |
| 2026-05-12 | `1af5af49` | RemoteSession analytics | 添加了连接建立时的分析事件上报功能 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将模块内的日志宏迁移到新的UE_LOGF格式 |
| 2026-04-13 | `fb2897b0` | IPv6 support for RemoteSession client and server | 为客户端和服务器添加了IPv6网络支持 |
| 2026-04-13 | `015f61a1` | Fixed a bunch of unreachable code warnings causing errors on some targets | 修复了在某些平台上导致编译错误的不可达代码警告 |

### 维护评价

Remote Session 插件自 2018 年创建以来，一直处于**实验性**状态（`EnabledByDefault=false`，且未升级到正式版）。最近的提交（2026年4-5月）显示它仍在进行维护和功能增强，例如添加 IPv6 支持和新的分析功能，表明其开发并未停滞。

然而，由于其长期处于实验阶段，且文档和测试用例相对稀缺，它可能并不适合用于生产环境。**建议**将其视为一个**研究性或原型开发工具**，用于快速搭建远程控制、流式传输的原型，或作为学习 Unreal Engine 网络架构的参考。在生产项目中，应谨慎评估其稳定性和性能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteSession)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteSession/Tests)