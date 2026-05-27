# MessageBus Tester

> Plugin to test and monitor message bus reliability

| 属性 | 值 |
|---|---|
| 中文名 | 消息总线测试器 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessageBusTester` (Runtime), `MessageBusTesterEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester) | |

## 用途

MessageBus Tester 是一个专用于开发和测试阶段的实验性插件。它的核心功能并非作为通用的消息总线监控工具，而是为 `MessageBusTesterApp` 这个特定的应用程序提供一套完整的测试用例和调试界面。其目的是通过模拟各种场景（如不同的负载大小、发送间隔），系统性地验证 Unreal Engine 底层 UDP 消息传输（由 `UdpMessaging` 插件提供）的可靠性、稳定性和性能。它帮助开发者分析消息总线的用例，并确保底层网络代码在最优状态下运行。此插件**不适合用于生产环境的实时监控**。

## 使用场景

- 你正在开发或维护 Unreal Engine 的底层消息系统或网络传输层，需要进行压力测试和回归测试。
- 你需要为 `MessageBusTesterApp` 这个独立工具提供测试界面和用例，以评估 UDP 消息传输在各种条件下的表现。
- 你怀疑 UDP 消息传输存在丢包、延迟或性能问题，需要一个工具来系统性地复现和诊断问题。

## 蓝图用法

经过源码分析，该插件主要提供编辑器 UI 和应用程序逻辑，**未发现面向蓝图公开的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口**。它的所有功能都通过其配套的 `MessageBusTesterApp` 程序和编辑器标签页 `SMessageBusTesterPanel` 来操作，无法在游戏逻辑或通用蓝图中直接调用。

## C++ 用法

**重要提示：** 此插件的模块 (`MessageBusTester`, `MessageBusTesterEditor`) 的 `AllowlistPrograms` 设置为 `["MessageBusTesterApp"]`。这意味着这些模块**只会在 `MessageBusTesterApp` 这个程序中加载**，在编辑器、独立运行或打包的游戏程序中不会加载。因此，其 C++ API 主要供插件内部和 `MessageBusTesterApp` 使用，普通项目无法直接调用。

### 头文件引入

如果需要在 `MessageBusTesterApp` 的开发中引用，可使用：
```cpp
#include "MessageBusTesterEditorModule.h"
```

### 基本用法（内部/调试）

一个典型的内部用法是获取当前的网络消息统计信息扩展。以下示例展示了如何通过 `FMessageBusTesterEditorModule` 的静态方法安全地获取该接口：

```cpp
// 来源: Private/MessageBusTesterEditorModule.h
// 用途：获取用于监控消息统计的 INetworkMessagingExtension 接口
if (INetworkMessagingExtension* StatsProvider = FMessageBusTesterEditorModule::GetMessagingStatistics())
{
    // 使用 StatsProvider 查询网络传输统计信息
    // 例如：RTT, 窗口大小, 已发送/丢失分段等
}
else
{
    // 特征不可用，可能在非测试上下文或模块未加载时
    UE_LOG(LogMessageBusTesterEditor, Warning, TEXT("Network Messaging Extension is not available."));
}
```

### 进阶用法

更高级的用法涉及启动该插件的编辑器模块并显示其测试面板，但这通常由 `MessageBusTesterApp` 的入口点自动完成。

## Demo 示例

由于插件的特殊性，下面提供一个最小的示例，展示如何在另一个编辑器模块中（假设上下文允许）引用并调用 `MessageBusTester` 的辅助函数。这仅用于说明原理，实际中很少这样使用。

**MessageBusTestConsumer.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

// 前置声明，避免不必要的头文件包含
class INetworkMessagingExtension;

class FMessageBusTestConsumerModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // 示例函数：尝试获取并使用消息统计接口
    void QueryNetworkStats();

private:
    // 缓存接口指针，避免频繁查询
    INetworkMessagingExtension* CachedStatsProvider = nullptr;
};
```

**MessageBusTestConsumer.cpp**
```cpp
#include "MessageBusTestConsumerModule.h"
#include "MessageBusTesterEditorModule.h" // 引入插件模块
#include "INetworkMessagingExtension.h" // 引入统计接口类型

#define LOCTEXT_NAMESPACE "FMessageBusTestConsumerModule"

void FMessageBusTestConsumerModule::StartupModule()
{
    // 模块启动时尝试缓存接口
    CachedStatsProvider = FMessageBusTesterEditorModule::GetMessagingStatistics();
}

void FMessageBusTestConsumerModule::ShutdownModule()
{
    CachedStatsProvider = nullptr;
}

void FMessageBusTestConsumerModule::QueryNetworkStats()
{
    if (CachedStatsProvider)
    {
        // 此处可以使用 CachedStatsProvider 调用其方法，获取统计数据
        // 例如：FMessageTransportStatistics Stats = CachedStatsProvider->GetTransportStatistics(...);
        UE_LOG(LogTemp, Log, TEXT("Successfully queried network messaging stats via MessageBusTester helper."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("MessageBusTester network stats interface is not available in this context."));
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMessageBusTestConsumerModule, MessageBusTestConsumer)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UdpMessaging` | 提供底层的 UDP 消息传输实现，是此插件测试的核心对象。 |
| `INetworkMessagingExtension` | (通过 `INetworkMessagingExtension.h`) 提供网络消息统计的抽象接口，插件通过 `IModularFeatures` 获取具体实现。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏以使用新的格式化功能。 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复了本地化相关的编译警告。 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修正了 API 导出宏的使用。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 启用 Android NDK 29 并修复相关编译问题。 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复了当远程客户端重置其 UDP 消息设置时，统计面板未更新的问题。 |

### 维护评价

该插件创建于 2025 年 10 月，相对“年轻”。从提交历史看，它处于**活跃维护**中，近期的更新包括编译修复、平台兼容性改进（Android NDK 29）和 bug 修复（统计面板更新）。作为实验性 (`IsBetaVersion=true`) 和特定工具 (`MessageBusTesterApp`) 的插件，其核心功能稳定，但 API 和设计未来可能会有变动。**仅推荐在开发 `MessageBusTesterApp` 或对 UE 消息总线进行深度调试时使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester/Tests) (如果存在)