# MessageBus Tester

> Plugin to test and monitor message bus reliability

| 属性 | 值 |
|---|---|
| 中文名 | 消息总线测试器 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessageBusTester` (Runtime), `MessageBusTesterEditor` (UncookedOnly) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-10-24 |
| 年龄标签 | 🆕（约 0.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester) | |

## 用途

该插件是一个专门用于**测试和调试 Unreal Engine 底层 UDP 消息传输系统（Message Bus）** 的开发者工具。它并非一个面向最终用户的功能插件，而是一个为 UE5 网络消息系统开发团队（或高级用户）设计的“诊断套件”。其核心目的是提供一系列测试用例和监控工具，用于：

1.  **压力测试**：通过定义测试计划（如定时发送不同大小的数据包）来主动“压测” UDP 消息通道。
2.  **可靠性监控**：实时监控消息传输的统计数据，如往返时间（RTT）、丢包率、滑动窗口大小、分段传输状态等，帮助分析底层传输代码的健壮性和性能瓶颈。
3.  **多实例发现与交互**：能够自动发现网络上运行的其他测试实例，并与之建立连接进行测试，模拟真实的分布式消息传递场景。

## 使用场景

-   **UE5 网络引擎开发人员**：用于验证和优化 UDP 消息传输协议、流量控制、拥塞避免等底层逻辑的实现。
-   **需要深度调试网络消息的高级开发者**：当你的游戏或应用依赖 UE 的 Message Bus 或 UDP Messaging 插件进行自定义网络通信，并且遇到了难以复现的网络性能或稳定性问题时，可以使用此插件来创建标准化的测试环境，量化分析问题。
-   **性能基准测试**：在不同的网络环境（局域网、模拟延迟/丢包网络）下，对消息总线的吞吐量和延迟进行基准测试。

## 蓝图用法

该插件主要提供编辑器 UI 和运行时测试逻辑，**没有暴露可用于蓝图的 `BlueprintCallable` 函数**。其核心功能通过编辑器标签页和运行时逻辑实现，主要供 C++ 代码和编辑器 UI 调用。

## C++ 用法

该插件主要提供一个编辑器面板和运行时测试模块，其核心使用方式是**通过编辑器界面操作**，或者在其测试框架内添加自定义测试。直接在项目 C++ 代码中调用其 API 的场景较少。

### 头文件引入

```cpp
// 引入编辑器模块接口
#include "IMessageBusTesterEditorModule.h"
```

### 基本用法（在编辑器工具中）

插件注册了一个编辑器标签页，可以通过代码或菜单打开。

```cpp
// 检查编辑器模块是否可用
if (FModuleManager::Get().IsModuleLoaded(TEXT("MessageBusTesterEditor")))
{
    // 获取模块接口
    IMessageBusTesterEditorModule& EditorModule = FModuleManager::GetModuleChecked<IMessageBusTesterEditorModule>(TEXT("MessageBusTesterEditor"));
    
    // 显示（或切换到）Message Bus Tester 面板
    EditorModule.DisplayMessageBusTester();
}
```
*（思路来源：`MessageBusTesterEditorModule.h` 中的 `DisplayMessageBusTester` 接口定义）*

## Demo 示例

一个最小的集成示例，展示如何在项目中启用该插件并尝试打开其面板。假设插件已通过 .uplugin 文件或项目设置启用。

```cpp
// MyTestGameMode.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyTestGameMode.generated.h"

UCLASS()
class AMyTestGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    // 在游戏开始后的一段时间，尝试打开消息总线测试面板（仅编辑器下有效）
    virtual void BeginPlay() override;
};
```

```cpp
// MyTestGameMode.cpp
#include "MyTestGameMode.h"
#include "IMessageBusTesterEditorModule.h"
#include "Modules/ModuleManager.h"

void AMyTestGameMode::BeginPlay()
{
    Super::BeginPlay();

#if WITH_EDITOR
    // 在游戏开始后5秒，如果编辑器模块已加载，则显示测试面板
    FTimerHandle UnusedHandle;
    GetWorldTimerManager().SetTimer(UnusedHandle, [this]()
    {
        if (FModuleManager::Get().IsModuleLoaded(TEXT("MessageBusTesterEditor")))
        {
            IMessageBusTesterEditorModule& TesterModule = FModuleManager::GetModuleChecked<IMessageBusTesterEditorModule>(TEXT("MessageBusTesterEditor"));
            TesterModule.DisplayMessageBusTester();
            UE_LOG(LogTemp, Log, TEXT("MessageBus Tester Panel Opened."));
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("MessageBusTesterEditor module not loaded. Ensure the plugin is enabled for editor."));
        }
    }, 5.0f, false);
#endif
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UdpMessaging` | 插件测试的目标传输层，提供 UDP 消息传输实现。插件依赖它来建立实际的网络连接和发送测试数据。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统的 UE_LOG 宏迁移至新的 UE_LOGF 宏，属于引擎日志系统升级的适配性改动。 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复本地化相关的编译警告。 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修正 API 相关的宏定义，确保跨模块调用的兼容性。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 为 Android 平台启用 NDK 29 并修复由此引起的编译问题。 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复当远程客户端重置其 UDP 消息设置时，统计面板无法更新的 bug。 |

### 维护评价

该插件创建于 2025 年 10 月，历史较短，仍处于**实验性阶段**（`IsBetaVersion=true`）。从提交历史看，初期有功能性提交（如修复统计面板更新），近期（2026 年）的更新主要集中在**维护和适配**上（修复警告、宏迁移、平台编译修复），没有新的核心功能开发。

由于是 `Experimental` 插件且默认未启用，它更可能作为 Epic 内部或特定项目的测试工具存在。对于大多数项目而言，它不具备直接的生产使用价值，而是作为网络底层开发的辅助工具。

**综合评价**：这是一个功能明确、设计完整的**实验性开发者工具**，适合在开发或深度调试 UE5 UDP 消息系统时使用。它并非一个需要集成到最终产品中的插件。如果你的工作不涉及 UE 消息总线底层开发，则无需关注。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)
-   测试用例：该插件本身即为测试工具，其源码可视为 UE5 消息系统测试用例的参考。核心逻辑和 UI 位于 `Source/MessageBusTesterEditor/` 目录下。