# MessageBus Tester

> Plugin to test and monitor message bus reliability

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessageBusTester` (Runtime), `MessageBusTesterEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester) | |

## 用途

该插件提供了一个完整的测试和监控框架，用于验证 Unreal Engine 消息总线（Message Bus）的可靠性。它不仅仅是一个简单的测试工具，而是一个集成了网络监控、测试计划管理、日志记录和可视化面板的综合性诊断工具。其核心目的是帮助开发者系统化地测试消息总线在各种条件下的表现，例如消息传输的可靠性、网络性能、以及在多实例（Tester）环境下的交互情况。它通过一个独立的编辑器面板来呈现所有测试数据和控制选项。

## 使用场景

- 你正在开发一个依赖于 `UdpMessaging` 或其他消息总线进行进程间或网络通信的分布式系统，需要验证其稳定性和性能。
- 你需要模拟多个消息发送/接收实例，并监控它们之间的通信状态、传输速率和错误率。
- 你需要一个可视化的界面来启动、停止测试，定义测试负载（Payload），并实时查看测试日志和网络统计信息。
- 你正在调试消息总线相关的问题，需要一个工具来集中观察消息的流向、分段传输状态和确认（ACK）情况。

## 蓝图用法

该插件主要提供编辑器工具和 C++ 接口，未暴露 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。其主要功能通过编辑器 UI 和 C++ 模块接口访问。

## C++ 用法

### 头文件引入

```cpp
#include "IMessageBusTesterEditorModule.h"
```

### 基本用法

通过模块接口打开消息总线测试器面板。

```cpp
// 获取编辑器模块并显示测试器面板
IMessageBusTesterEditorModule& EditorModule = FModuleManager::LoadModuleChecked<IMessageBusTesterEditorModule>(TEXT("MessageBusTesterEditor"));
EditorModule.DisplayMessageBusTester();
```

### 进阶用法

该插件通过 `INetworkMessagingExtension` 模块化特性接口暴露网络统计信息。你可以获取此接口来查询当前的网络消息传输状态。

```cpp
#include "INetworkMessagingExtension.h"
#include "Features/IModularFeatures.h"

// 获取网络消息统计扩展接口
INetworkMessagingExtension* GetNetworkStats()
{
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    const FName FeatureName = INetworkMessagingExtension::ModularFeatureName;

    // 确保在游戏线程调用，或正确加锁
    if (IsInGameThread())
    {
        if (ModularFeatures.IsModularFeatureAvailable(FeatureName))
        {
            return &ModularFeatures.GetModularFeature<INetworkMessagingExtension>(FeatureName);
        }
    }
    else
    {
        // 非游戏线程需要加锁访问
        ModularFeatures.LockModularFeatureList();
        ON_SCOPE_EXIT { ModularFeatures.UnlockModularFeatureList(); };
        if (ModularFeatures.IsModularFeatureAvailable(FeatureName))
        {
            return &ModularFeatures.GetModularFeature<INetworkMessagingExtension>(FeatureName);
        }
    }
    return nullptr;
}

// 使用示例
void PrintNetworkStats()
{
    INetworkMessagingExtension* NetStats = GetNetworkStats();
    if (NetStats)
    {
        // 此处可以调用 NetStats 提供的方法来获取具体的统计数据
        // 具体方法需参考 INetworkMessagingExtension 接口定义
    }
}
```

## Demo 示例

一个最小化的示例，展示如何在编辑器工具中触发消息总线测试器面板的显示。

**MessageBusTesterDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MessageBusTesterDemoActor.generated.h"

UCLASS()
class AMessageBusTesterDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMessageBusTesterDemoActor();

    // 一个蓝图可调用的函数，用于打开测试器面板
    UFUNCTION(BlueprintCallable, Category = "MessageBusTester")
    void OpenMessageBusTesterPanel();
};
```

**MessageBusTesterDemoActor.cpp**
```cpp
#include "MessageBusTesterDemoActor.h"
#include "IMessageBusTesterEditorModule.h"
#include "Modules/ModuleManager.h"

AMessageBusTesterDemoActor::AMessageBusTesterDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMessageBusTesterDemoActor::OpenMessageBusTesterPanel()
{
    // 检查编辑器模块是否可用
    if (FModuleManager::Get().IsModuleLoaded(TEXT("MessageBusTesterEditor")))
    {
        IMessageBusTesterEditorModule& EditorModule = FModuleManager::GetModuleChecked<IMessageBusTesterEditorModule>(TEXT("MessageBusTesterEditor"));
        EditorModule.DisplayMessageBusTester();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("MessageBusTesterEditor module is not loaded."));
    }
}
```

## 模块依赖

该插件依赖于 `UdpMessaging` 插件（在 `.uplugin` 中声明）。对于使用该插件功能的模块，通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `UdpMessaging` | 提供底层的 UDP 消息传输实现，是本插件测试的核心对象 |
| `MessageBusTester` | 提供核心的测试逻辑和数据结构 |
| `MessageBusTesterEditor` | 提供编辑器 UI、面板和样式 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-01-15 `738ab46a` Fixed localization warnings
- 2025-11-27 `29081f24` Fixup API macros
- 2025-11-20 `f8d6103d` Enable NDK 29 for Android, fix compilation issues
- 2025-11-10 `248fda82` Fix the statistics panel not updating with a remote client resets its UDP Messaging settings.

### 维护评价

- **创建时间**：2025-11-10，非常新。
- **实验性状态**：`.uplugin` 中 `IsBetaVersion: true`，明确标记为实验性。
- **程序限制**：`SupportedPrograms` 和模块的 `AllowlistPrograms` 均限定为 `MessageBusTesterApp`，表明它可能是一个专用的测试应用程序，而非通用编辑器插件。
- **综合评价**：这是一个**全新的、实验性的专用测试工具**。它目前可能仅用于 Epic 内部或特定项目的测试流程中。由于其高度专用性和实验性，**不建议在生产项目中依赖它**。它更适合作为学习消息总线测试方法的参考，或在开发类似专用测试工具时借鉴其架构。使用前请确认其是否适用于你的目标程序（`MessageBusTesterApp`）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)