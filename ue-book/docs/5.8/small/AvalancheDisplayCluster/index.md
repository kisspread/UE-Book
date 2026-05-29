# Motion Design For nDisplay

> Motion Design Synchronization extensions for nDisplay clustering

| 属性 | 值 |
|---|---|
| 中文名 | Motion Design nDisplay同步 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheDisplayCluster` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-06-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AvalancheDisplayCluster) | |

## 用途

本插件为 Unreal Engine 的 Motion Design (Avalanche) 系统提供针对 **nDisplay** 集群渲染的同步扩展。它解决了在由多个物理节点（如 PC、工作站）组成的大型沉浸式显示环境（例如穹幕、CAVE）中，如何确保不同节点上的 Motion Design Playable（可播放对象）能够**精确、同步地**执行操作的问题。

核心思路是将事件的同步机制作为 Playable 框架中的“一等公民”。该插件实现了一种基于 nDisplay 集群事件（Cluster Events）的同步分发器，使得诸如“启动某个播放序列”、“切换场景”等关键事件，能够在所有集群节点上几乎同时触发，从而保证视觉呈现的一致性。

## 使用场景

- 你正在使用 **Motion Design (Avalanche)** 制作内容，并计划部署到由 **nDisplay** 驱动的多节点集群显示系统中。
- 你需要确保一个在主节点（Master）上发起的“播放/停止/切换”操作，能同时在所有从节点（Slaves）上执行，避免画面撕裂或序列不同步。
- 你的场景中使用了 **Level Streaming Playable**，并且需要所有集群节点同步加载和显示同一个关卡，即使它们的加载速度可能不同。

## 蓝图用法

本插件主要提供底层同步功能，未发现直接暴露的 `BlueprintCallable` 函数。同步逻辑通常由 Motion Design (Avalanche) 框架内部调用，用户一般通过配置 **Avalanche Settings** 来选择同步实现方式（例如，选择本插件提供的 `nDisplay` 实现）。

## C++ 用法

本插件的 API 主要面向高级用户和开发者，用于在自定义 Playable 或同步逻辑中集成集群事件。

### 头文件引入

```cpp
#include “SynchronizedEvents/AvaDisplayClusterSynchronizedEventsFeature.h”
#include “SynchronizedEvents/AvaDisplayClusterSynchronizedEventsDispatcher.h”
```

### 基本用法

**1. 创建同步事件分发器 (Dispatcher)**

这是使用同步功能的核心入口。你需要通过 `IAvaMediaSynchronizedEventsFeature` 接口来创建一个特定的调度器实例。

```cpp
// 假设你已经获取到了指向 IAvaMediaSynchronizedEventsFeature 的指针。
// 这通常由 Avalanche 系统在内部处理，但以下示例展示了原理。
// 来源: AvaDisplayClusterSynchronizedEventsFeature.h -> CreateDispatcher
if (TSharedPtr<IAvaMediaSynchronizedEventsFeature> SyncFeature = /* ... */)
{
    // 创建一个带有唯一签名的调度器，用于标识一类同步事件。
    TSharedPtr<IAvaMediaSynchronizedEventDispatcher> Dispatcher = SyncFeature->CreateDispatcher(“MyPlayableGroup_Sync”);
    // 保存 `Dispatcher` 以便后续使用。
}
```

**2. 推送同步事件**

创建好调度器后，你就可以向其中推送需要同步执行的函数。

```cpp
// 来源: AvaDisplayClusterSynchronizedEventsDispatcher.h -> PushEvent
if (Dispatcher.IsValid())
{
    // 推送一个事件，当集群中所有节点都准备好后，将执行 Lambda 中的代码。
    Dispatcher->PushEvent(“Event_01_StartSequence”, [this]()
    {
        // 这里是需要所有节点同步执行的逻辑，例如播放一段动画。
        StartMyAnimation();
    });
}
```

### 进阶用法

**监听和跟踪集群事件**

插件内部使用 `FAvaDisplayClusterSynchronizedEventsFeature` 来监听整个集群的二进制事件，并路由到对应的调度器。

```cpp
// 来源: AvaDisplayClusterSynchronizedEventsFeature.h -> OnBinaryClusterEventReceived
// 当收到一个二进制集群事件时，根据事件中的签名找到对应的调度器并处理。
void FAvaDisplayClusterSynchronizedEventsFeature::OnBinaryClusterEventReceived(const FDisplayClusterClusterEventBinary& InClusterEvent)
{
    // 解析事件载荷中的签名。
    FString EventSignature = /* ... */;
    
    // 在已创建的调度器中查找。
    if (TWeakPtr<FAvaDisplayClusterSynchronizedEventDispatcher> DispatcherWeak = DispatchersWeak.FindRef(EventSignature))
    {
        if (TSharedPtr<FAvaDisplayClusterSynchronizedEventDispatcher> Dispatcher = DispatcherWeak.Pin())
        {
            // 将集群事件传递给调度器处理。
            Dispatcher->OnClusterEventReceived(/* 解析后的载荷 */);
        }
    }
    // 如果调度器尚未创建（例如，对应的 Playable Group 还未初始化），
    // 事件会被缓存在 TrackingDispatchers 中，待调度器创建时处理。
}
```

## Demo 示例

以下是一个简化的、概念性的示例，展示如何在自定义的子系统或类中集成 nDisplay 同步事件。

**MySyncSubsystem.h**
```cpp
#pragma once
#include "Subsystems/GameInstanceSubsystem.h"
#include "Interfaces/AvaMediaSynchronizedEvents.h"
#include “MySyncSubsystem.generated.h”

UCLASS()
class UMySyncSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    // 模拟一个需要同步执行的动作
    UFUNCTION(BlueprintCallable)
    void RequestSynchronizedAction();

private:
    // 持有同步事件调度器
    TSharedPtr<IAvaMediaSynchronizedEventDispatcher> ActionDispatcher;
};
```

**MySyncSubsystem.cpp**
```cpp
#include “MySyncSubsystem.h”

void UMySyncSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 获取 Motion Design 同步特性（假设通过某种服务定位机制）
    // 在实际插件中，这由 Avalanche 管理。
    if (IAvaMediaSynchronizedEventsFeature* SyncFeature = /* 获取 IAvaMediaSynchronizedEventsFeature 的实现 */)
    {
        // 为“主操作”创建一个同步调度器
        ActionDispatcher = SyncFeature->CreateDispatcher(“GlobalActionDispatcher”);
    }
}

void UMySyncSubsystem::Deinitialize()
{
    ActionDispatcher.Reset();
    Super::Deinitialize();
}

void UMySyncSubsystem::RequestSynchronizedAction()
{
    if (!ActionDispatcher.IsValid()) return;

    // 将具体的业务逻辑封装成一个同步事件，并推送。
    // 此 Lambda 将在集群所有节点都收到信号后，于各自的本地线程执行。
    ActionDispatcher->PushEvent(“Action_PressedButton”, [WeakThis = TWeakObjectPtr<UMySyncSubsystem>(this)]()
    {
        if (UMySyncSubsystem* Subsystem = WeakThis.Get())
        {
            // 执行真正的同步操作，例如播放全局特效、触发过场等。
            UE_LOG(LogTemp, Log, TEXT(“Synchronized action executed on node: %s”), *FGenericPlatformMisc::GetEnvironmentVariable(TEXT(“nDisplayNodeID”)));
            Subsystem->DoActualSynchronizedEffect();
        }
    });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Avalanche` | Motion Design 核心框架插件。本插件为其提供 nDisplay 同步扩展。 |
| `nDisplay` | Unreal Engine 的官方集群渲染框架。本插件依赖其提供的集群事件系统。 |
| `AvaMedia` | Avalanche 的媒体同步抽象层。本插件实现了其中的 `IAvaMediaSynchronizedEventsFeature` 接口。 |
| `DisplayCluster` | nDisplay 的核心运行时模块，用于访问集群管理器和通信功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移为 `UE_LOGF`，属于引擎日志系统标准化的维护性更新。 |
| 2024-11-05 | `56aadf00` | [Motion Design] Fix Installed Build generation failure cause by AvalancheDisplayCluster | 修复了由于本插件导致的“安装构建”生成失败问题。 |
| 2024-06-15 | `3d842152` | [Motion Design] Fix CIS 498201 - nDisplay not supported on Mac | 修复了 macOS 平台不支持 nDisplay 的编译/集成问题。 |
| 2024-06-15 | `2f604ce4` | [Motion Design] Display Cluster synchronization support for Level Streaming Playable. | **初始提交**。实现了基于 nDisplay 集群事件的 Level Streaming Playable 同步支持，包含完整的调度器和事件跟踪系统。 |

### 维护评价

该插件创建于 2024 年 6 月，是一个相对年轻的实验性插件。从提交历史看，初始功能提交后，后续更新主要集中在**修复构建问题和平台兼容性**上（如修复安装构建失败、适配 macOS），而非添加新功能或优化核心逻辑。最后一次实质性更新停留在 **2024 年 11 月**，距今已超过 **1 年半**。

**综合评价**：
- **功能状态**：实现了其核心描述的 nDisplay 同步功能，但作为 `Experimental` 且 `EnabledByDefault=false` 的插件，表明其稳定性和 API 可能未定型。
- **维护活跃度**：**不活跃**。超过一年没有针对同步功能本身（如性能优化、新同步模式、错误恢复）的更新。最近的维护性更新（日志宏迁移）由引擎全局变更驱动。
- **已知限制**：作为实验性功能，可能存在未发现的边界条件问题。其稳定性和可靠性在长期运行的复杂集群场景下需要进一步验证。
- **推荐使用**：如果你的项目**强依赖** Motion Design (Avalanche) 在 nDisplay 集群上的同步，并且是 **Win64/Linux** 平台，可以尝试使用。但需做好心理准备，它可能不会得到频繁更新，并且需要深入理解其原理以解决可能出现的问题。对于新项目，建议评估是否有更稳定或官方推荐的集群同步方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AvalancheDisplayCluster)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AvalancheDisplayCluster/Tests) (如有)