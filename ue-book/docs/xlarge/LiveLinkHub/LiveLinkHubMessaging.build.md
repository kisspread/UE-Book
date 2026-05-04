# Live Link Hub

> LiveLink Hub allows streaming of animated data into Unreal Engine or UEFN

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkHub` (Runtime), `LiveLinkHubEditor` (Runtime), `LiveLinkHubMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkHub) | |

## 用途

LiveLinkHub 是一个中心化的 Live Link 数据路由和管理节点。它解决了在复杂的虚拟制作或多设备动画工作流中，多个 Live Link 源（如动作捕捉设备、动画软件）和多个 Unreal Engine 客户端（如主渲染机、UEFN 实例、监视器）之间数据同步和分发的问题。它充当一个“枢纽”，可以接收来自各种源的数据，并根据配置将其转发给一个或多个客户端，从而简化网络拓扑并提供集中控制。

## 使用场景

- **虚拟制作**：在 LED 墙拍摄中，将动作捕捉数据通过 LiveLinkHub 分发给渲染引擎、实时合成软件和监视器。
- **多客户端同步**：需要将同一动画数据流同时发送给多个运行在不同机器上的 Unreal Engine 实例（例如，一个用于最终渲染，一个用于实时预览）。
- **数据路由与过滤**：希望根据客户端需求，有选择地转发特定的 Live Link 主题（Subject），而不是广播所有数据。
- **集中管理**：希望在一个中心点监控所有 Live Link 连接状态，而不是在每个客户端上单独配置。

## 蓝图用法

LiveLinkHub 主要通过其消息传递模块 (`LiveLinkHubMessaging`) 提供配置和管理接口。核心蓝图可访问功能集中在设置和连接管理上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bAllowReceivingFromUnreal` | 布尔属性，控制是否允许 Hub 从其他 Unreal 实例接收 Live Link 数据。 | `ULiveLinkHubMessagingSettings` |
| `SetHostTopologyMode` | 设置当前主机的拓扑模式（如 Hub, Spoke, UnrealClient），决定其连接权限。 | `ILiveLinkHubMessagingModule` |
| `GetHostTopologyMode` | 获取当前主机的拓扑模式。 | `ILiveLinkHubMessagingModule` |
| `SetInstanceId` | 为当前实例设置唯一标识符，用于防止自连接。 | `ILiveLinkHubMessagingModule` |
| `GetInstanceId` | 获取当前实例的唯一标识符。 | `ILiveLinkHubMessagingModule` |
| `OnConnectionEstablished` | 多播委托，当与一个 Live Link Hub 建立连接时触发。 | `ILiveLinkHubMessagingModule` |

### 使用示例（蓝图描述）

1.  **配置 Hub 行为**：在项目设置中找到 `LiveLinkHubMessaging` 分类，可以设置 `Allow Receiving From Unreal` 来决定是否接受来自其他 UE 实例的广播。
2.  **在 C++ 中初始化 Hub**：在游戏模块或编辑器模块的初始化代码中，获取 `ILiveLinkHubMessagingModule` 接口，调用 `SetHostTopologyMode(ELiveLinkTopologyMode::Hub)` 将当前实例配置为 Hub 模式。
3.  **监听连接**：绑定到 `OnConnectionEstablished` 委托，当有新的客户端（如另一个 UE 实例）连接到此 Hub 时，可以执行相应逻辑（如记录日志、更新 UI）。

## C++ 用法

LiveLinkHub 的核心功能通过 `LiveLinkHubMessaging` 模块的接口暴露。以下示例展示了如何以编程方式配置和使用 Hub。

### 头文件引入

```cpp
#include "ILiveLinkHubMessagingModule.h"
#include "LiveLinkHubMessages.h"
```

### 基本用法

配置当前实例为 LiveLinkHub 并设置其拓扑模式。

```cpp
// 来源：基于 ILiveLinkHubMessagingModule.h 和 LiveLinkHubMessages.h 推断
#include "ILiveLinkHubMessagingModule.h"
#include "Modules/ModuleManager.h"

void InitializeAsLiveLinkHub()
{
    // 获取 LiveLinkHub 消息传递模块接口
    ILiveLinkHubMessagingModule* MessagingModule = FModuleManager::GetModulePtr<ILiveLinkHubMessagingModule>("LiveLinkHubMessaging");
    if (MessagingModule)
    {
        // 将当前实例设置为 Hub 模式，使其能够接收来自 Spoke (外部源) 和 UnrealClient 的数据，并向 UnrealClient 发送数据
        MessagingModule->SetHostTopologyMode(ELiveLinkTopologyMode::Hub);

        // 设置一个唯一的实例 ID，用于网络标识和防止自连接
        FGuid MyInstanceId = FGuid::NewGuid();
        MessagingModule->SetInstanceId(FLiveLinkHubInstanceId(MyInstanceId));

        UE_LOG(LogTemp, Log, TEXT("Initialized as LiveLinkHub with ID: %s"), *MyInstanceId.ToString());
    }
}
```

### 进阶用法

注册一个自定义的辅助通道请求处理器，用于处理特定的 LiveLinkHub 扩展消息。

```cpp
// 来源：基于 ILiveLinkHubMessagingModule.h 中的模板函数推断
#include "ILiveLinkHubMessagingModule.h"

// 假设我们定义了一个自定义的请求消息结构体
USTRUCT()
struct FMyCustomAuxChannelRequest : public FLiveLinkHubAuxChannelRequestMessage
{
    GENERATED_BODY()
    // 自定义字段...
};

void RegisterCustomAuxHandler()
{
    ILiveLinkHubMessagingModule* MessagingModule = FModuleManager::GetModulePtr<ILiveLinkHubMessagingModule>("LiveLinkHubMessaging");
    if (MessagingModule)
    {
        // 使用模板函数注册处理器，类型安全
        MessagingModule->RegisterAuxChannelRequestHandler<FMyCustomAuxChannelRequest>(
            [](const FMyCustomAuxChannelRequest& Request, const TSharedRef<IMessageContext>& Context)
            {
                // 处理来自对等端的自定义辅助通道请求
                UE_LOG(LogTemp, Log, TEXT("Received custom aux channel request."));
                // ... 执行业务逻辑，例如建立额外的数据通道
            }
        );
    }
}
```

## Demo 示例

一个最小化的 LiveLinkHub 管理器类，演示了如何初始化和监听连接。

**LiveLinkHubManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ILiveLinkHubMessagingModule.h"

class FLiveLinkHubManager
{
public:
    void Initialize();
    void Shutdown();

private:
    void OnHubConnectionEstablished(FGuid SourceId);

    FDelegateHandle ConnectionDelegateHandle;
};
```

**LiveLinkHubManager.cpp**
```cpp
#include "LiveLinkHubManager.h"
#include "ILiveLinkHubMessagingModule.h"
#include "Modules/ModuleManager.h"

void FLiveLinkHubManager::Initialize()
{
    ILiveLinkHubMessagingModule* MessagingModule = FModuleManager::GetModulePtr<ILiveLinkHubMessagingModule>("LiveLinkHubMessaging");
    if (MessagingModule)
    {
        // 配置为 Hub
        MessagingModule->SetHostTopologyMode(ELiveLinkTopologyMode::Hub);
        MessagingModule->SetInstanceId(FLiveLinkHubInstanceId(FGuid::NewGuid()));

        // 绑定连接事件
        ConnectionDelegateHandle = MessagingModule->OnConnectionEstablished().AddRaw(this, &FLiveLinkHubManager::OnHubConnectionEstablished);

        UE_LOG(LogTemp, Log, TEXT("LiveLinkHub Manager Initialized."));
    }
}

void FLiveLinkHubManager::Shutdown()
{
    ILiveLinkHubMessagingModule* MessagingModule = FModuleManager::GetModulePtr<ILiveLinkHubMessagingModule>("LiveLinkHubMessaging");
    if (MessagingModule)
    {
        MessagingModule->OnConnectionEstablished().Remove(ConnectionDelegateHandle);
    }
}

void FLiveLinkHubManager::OnHubConnectionEstablished(FGuid SourceId)
{
    UE_LOG(LogTemp, Log, TEXT("New client connected to Hub. Source ID: %s"), *SourceId.ToString());
    // 在此处更新连接列表 UI 或执行其他逻辑
}
```

## 模块依赖

从模块名称和头文件依赖关系推断，`LiveLinkHubMessaging` 模块依赖于 Live Link 核心模块。使用者无需直接依赖此插件的其他模块。

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心运行时，提供基础类型、客户端/提供者接口。 |
| `LiveLinkMessageBus` | 基于 MessageBus 的 Live Link 传输实现，是 Hub 网络通信的基础。 |

## 维护状态

### 近期更新

```
- 1a789fbeca7d LiveLinkHub - Disable timecode lerp interpolation when in playback
- 6314042d54bd LiveLinkHub - Fix discovered clients list not showing any information about client other than IP
- 8c20efeb0f5c LiveLinkHub - Various bug fixes for Client Filter Presets - Deleting current Filter preset will now clear it - Adding filter will no longer create a duplicated LiveLinkHub entry - Accessing the client filters no longer blocks accessing the hub - Renamed Disabled AutoConnect to Filters Only
```

**解读**：最近的提交集中在修复客户端过滤预设的 UI 和逻辑问题，以及改进播放时的时间码处理。这表明插件处于积极的 bug 修复和功能完善阶段。

### 维护评价

- **创建时间**：2024 年 2 月，是一个相对较新的插件。
- **最近更新**：最近的提交（基于提供的信息）都是功能修复和改进，表明仍在活跃开发。
- **状态**：`.uplugin` 中标记为 `IsBetaVersion: true`，且 `EnabledByDefault: false`，说明它仍处于测试阶段，需要用户手动启用。
- **推荐**：**推荐在需要中心化 Live Link 管理的虚拟制作或多客户端项目中试用**。由于是 Beta 版本，建议在生产环境中谨慎使用，并关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkHub)
- [官方文档]() (暂无)
- [测试用例]() (路径待确认，可能位于 `Engine/Tests/LiveLinkHub` 或插件内部的 `Tests` 目录)