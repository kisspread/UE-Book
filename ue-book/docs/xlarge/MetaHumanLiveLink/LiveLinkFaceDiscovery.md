# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 插件的核心目的是为 MetaHuman 角色提供实时的面部动画数据流式传输能力。它解决了将来自外部设备（如 iPhone 上的 Live Link Face 应用）或本地处理管线的实时面部捕捉数据，高效、低延迟地驱动 UE 中 MetaHuman 角色面部动画的问题。该插件是 MetaHuman 实时工作流的关键组成部分，使得在虚拟制片、实时预览和游戏开发中驱动高保真数字人成为可能。

## 使用场景

- **虚拟制片**：在 LED 墙或绿幕前，演员佩戴面部捕捉设备，其表演需要实时驱动场景中的 MetaHuman 角色。
- **实时预览与评审**：在动画或视觉特效制作中，导演或动画师希望立即看到面部动画调整的效果，而无需等待离线渲染。
- **游戏开发与测试**：在开发需要复杂面部动画的游戏时，用于快速原型设计和测试对话、表情系统。
- **直播与虚拟主播**：驱动虚拟形象进行实时直播互动。

## 蓝图用法

该插件主要通过其提供的 Live Link Source 和发现机制在蓝图中工作。核心交互通常发生在 Live Link 面板和蓝图中的 Live Link 节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start` | 启动设备发现过程，开始监听网络上的 Live Link Face 应用。 | `FLiveLinkFaceDiscovery` |
| `Stop` | 停止设备发现过程。 | `FLiveLinkFaceDiscovery` |
| `OnServersUpdated` | 委托。当发现的设备列表更新时触发，提供当前所有可用设备的集合。 | `FLiveLinkFaceDiscovery` |

### 使用示例（蓝图描述）

1.  **发现设备**：在蓝图中，创建一个 `FLiveLinkFaceDiscovery` 对象（通常通过 C++ 暴露的函数或特定蓝图节点）。调用 `Start` 节点开始扫描网络。绑定 `OnServersUpdated` 委托到自定义事件，该事件会接收一个 `TSet<FServer>`，其中包含所有发现的设备信息（ID、名称、IP地址、控制端口）。
2.  **建立连接**：从 `FServer` 结构中获取目标设备的 `Address` 和 `ControlPort`。使用这些信息，通过 Live Link 面板或蓝图中的 `Create Live Link Source` 节点，手动或自动创建一个指向该设备的 Live Link 源。
3.  **驱动角色**：一旦 Live Link 源建立连接并开始接收数据，就可以在角色蓝图中使用 `Live Link` 节点（如 `Get Live Link Subject Data`）来获取面部骨骼变换数据，并将其应用到 MetaHuman 角色的 Control Rig 或 AnimBP 上。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkFaceDiscovery.h"
```

### 基本用法

以下代码展示了如何创建一个设备发现器并监听设备更新。

```cpp
// 创建发现器实例，设置刷新间隔为3秒，设备过期时间为6秒
TSharedRef<FLiveLinkFaceDiscovery> Discovery = MakeShared<FLiveLinkFaceDiscovery>(3.0, 6.0);

// 绑定设备更新委托
Discovery->OnServersUpdated.BindLambda([](const TSet<FLiveLinkFaceDiscovery::FServer>& Servers)
{
    UE_LOG(LogTemp, Log, TEXT("发现 %d 个设备:"), Servers.Num());
    for (const FLiveLinkFaceDiscovery::FServer& Server : Servers)
    {
        UE_LOG(LogTemp, Log, TEXT("  - %s (%s)"), *Server.Name, *Server.Address);
    }
});

// 开始发现
Discovery->Start();

// ... 在某个时刻停止发现
// Discovery->Stop();
```

### 进阶用法

结合 Live Link 框架，根据发现的设备信息动态创建 Live Link 源。

```cpp
// 假设已经通过 Discovery 获取到目标服务器信息
const FLiveLinkFaceDiscovery::FServer* TargetServer = /* ... */;

if (TargetServer)
{
    // 使用 Live Link 框架创建源 (需要包含 LiveLinkInterface 模块)
    // FCreateLiveLinkSourceArgs Args;
    // Args.Type = /* MetaHumanLiveLinkSource 的类型名 */;
    // Args.ConnectionString = FString::Printf(TEXT("%s:%d"), *TargetServer->Address, TargetServer->ControlPort);
    // ILiveLinkModule& LiveLinkModule = FModuleManager::Get().LoadModuleChecked<ILiveLinkModule>("LiveLink");
    // LiveLinkModule.CreateSource(Args);
}
```

## Demo 示例

一个最小化的 C++ 示例，演示如何集成设备发现功能。

```cpp
// MyActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkFaceDiscovery.h"
#include "MyActor.generated.h"

UCLASS()
class MYPROJECT_API AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<FLiveLinkFaceDiscovery> DeviceDiscovery;

    UFUNCTION()
    void OnDevicesUpdated(const TSet<FLiveLinkFaceDiscovery::FServer>& Servers);
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "LiveLinkFaceDiscovery.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建设备发现器
    DeviceDiscovery = MakeShared<FLiveLinkFaceDiscovery>();

    // 绑定更新回调
    DeviceDiscovery->OnServersUpdated.BindUObject(this, &AMyActor::OnDevicesUpdated);

    // 开始发现
    DeviceDiscovery->Start();
    UE_LOG(LogTemp, Log, TEXT("已开始搜索 Live Link Face 设备..."));
}

void AMyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (DeviceDiscovery.IsValid())
    {
        DeviceDiscovery->Stop();
        DeviceDiscovery.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyActor::OnDevicesUpdated(const TSet<FLiveLinkFaceDiscovery::FServer>& Servers)
{
    UE_LOG(LogTemp, Log, TEXT("设备列表更新，共 %d 个设备:"), Servers.Num());
    for (const auto& ServerPair : Servers)
    {
        const FLiveLinkFaceDiscovery::FServer& Server = ServerPair;
        UE_LOG(LogTemp, Log, TEXT("  名称: %s, IP: %s, 端口: %d"), *Server.Name, *Server.Address, Server.ControlPort);
        // 在此处可以添加逻辑，例如自动连接到第一个发现的设备
    }
}
```

## 模块依赖

该插件由多个模块组成，每个模块有其特定的依赖。以下是各模块的关键依赖（已省略 Core, CoreUObject, Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 框架的核心接口，所有 Live Link 源和主题都依赖于此。 |
| `LiveLink` | Live Link 的运行时模块，用于管理和评估 Live Link 数据。 |
| `LiveLinkComponents` | 提供用于在 Actor 中消费 Live Link 数据的组件（如 LiveLinkTransformController）。 |
| `CaptureManagerCore` | 提供底层的网络发现和通信协议（如 `FDiscoveryMessenger`）。 |
| `MetaHumanCore` | MetaHuman 的核心运行时模块，包含面部骨骼定义、控制绑定等。 |
| `UnrealEd` | 编辑器模块，用于 `LiveLinkFaceSourceEditor` 和 `MetaHumanLiveLinkSourceEditor` 模块，提供编辑器内源配置UI。 |

## 维护状态

### 近期更新

- 2025-10-03 ce6ff392ddca Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage.
  *解读：修复了编译器警告，提升了代码质量。*
- 2025-09-15 be9e554712ac Add periodic refresh and server expiry to LiveLinkFaceDiscovery
  *解读：为设备发现功能增加了周期性刷新和设备过期机制，提升了网络发现的健壮性。*
- 2025-08-20 0382f1a4d183 Fix compile error in LiveLinkFaceSourceEditor module on Mac Fix compile error in LiveLinkFaceDiscovery on Android
  *解读：修复了在 Mac 和 Android 平台上的编译错误，改善了跨平台兼容性。*

### 维护评价

MetaHuman Live Link 是一个**活跃维护**的插件。它创建于2025年初，属于较新的功能模块。从近期提交记录看，Epic 团队在持续进行功能增强（如改进发现机制）和跨平台兼容性修复。作为 MetaHuman 实时工作流的核心组件，预计会随着 MetaHuman 技术栈的更新而持续迭代。目前没有发现已知的重大限制或废弃标记，**推荐在需要实时驱动 MetaHuman 角色的项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink/Tests)