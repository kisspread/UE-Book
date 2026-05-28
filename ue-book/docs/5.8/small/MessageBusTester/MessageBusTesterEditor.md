# Message Bus Tester

> Plugin to test and monitor message bus reliability（照抄，不翻译）

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

MessageBus Tester 是一个专门用于测试和监控基于 UDP 的 UE 消息总线系统可靠性的开发工具。它并非为游戏逻辑或最终用户功能设计，而是一个内部测试和调试套件。

其核心目的是为开发者提供一组可执行的测试用例，用于：
1.  **压力与可靠性测试**：模拟真实场景下的消息发送，以验证 UDP 消息传输层在持续负载下的稳定性和数据完整性。
2.  **性能监控与分析**：提供实时的网络统计面板，用于可视化消息的往返时间（RTT）、窗口大小、分段状态、数据传输速率以及丢包情况，帮助分析性能瓶颈。
3.  **跨进程/跨机器测试**：设计用于发现连接在同一消息总线上的不同实例（可能运行在不同进程或机器上），并允许它们互相发送测试负载，以验证网络通信的连通性和效率。

简而言之，它是 UE 消息总线基础设施的“质量检测员”和“性能分析仪”，服务于引擎和网络功能的开发者。

## 使用场景

-   你正在开发或调试一个依赖 `UdpMessaging` 插件进行进程间通信（IPC）的自定义工具或系统。
-   你需要为 UE 的消息传输层编写或运行压力测试，以验证其在高负载或不稳定网络环境下的表现。
-   你需要一个可视化工具来实时监控多个测试客户端之间的网络统计信息，用于性能调优。
-   你需要诊断消息丢失、延迟过高或连接不稳定等与底层消息总线相关的问题。

## 蓝图用法

该插件主要是一个编辑器工具和独立测试应用，其核心交互通过专用 UI 面板（`SMessageBusTesterPanel`）进行，**没有公开的蓝图节点**。所有操作（如启动测试、配置负载、查看结果）都在其编辑器标签页中完成。

## C++ 用法

该插件的主要使用方式是通过其运行时模块的接口来控制测试流程，并通过编辑器模块来显示 UI。以下示例展示了如何从 C++ 代码中与测试器交互。

### 头文件引入

```cpp
// 要使用运行时测试逻辑
#include "MessageBusTester/IMessageBusTesterModule.h"

// 要使用编辑器 UI 面板
#include "MessageBusTesterEditor/IMessageBusTesterEditorModule.h"
```

### 基本用法

从 `IMessageBusTesterModule` 接口启动测试管理器。

```cpp
// 假设在某个编辑器工具或控制台命令的实现中
#include "MessageBusTester/IMessageBusTesterModule.h"

void FMyEditorCommands::RunMessageBusTest()
{
    // 获取运行时模块的实例
    if (IMessageBusTesterModule* TesterModule = FModuleManager::GetModulePtr<IMessageBusTesterModule>(TEXT("MessageBusTester")))
    {
        // 访问测试器的功能，例如启动一个测试会话
        // TesterModule->StartTesting(...); // 具体方法需查看 IModule 接口定义
    }
}
```

*注意：`IMessageBusTesterModule` 的具体 API 需查看其头文件。*

### 进阶用法

在编辑器模块中启动测试 UI 面板。

```cpp
// 在编辑器工具栏按钮的点击处理中
#include "MessageBusTesterEditor/IMessageBusTesterEditorModule.h"

void FMyEditorModule::OnOpenTesterButtonClicked()
{
    // 获取编辑器模块的实例
    if (IMessageBusTesterEditorModule* EditorModule = FModuleManager::GetModulePtr<IMessageBusTesterEditorModule>(TEXT("MessageBusTesterEditor")))
    {
        // 调用接口方法显示测试器标签页
        EditorModule->DisplayMessageBusTester();
    }
}
```

## Demo 示例

这是一个最小化的 C++ 代码片段，演示如何从一个编辑器模块中打开 MessageBus Tester 的 UI 面板。

```cpp
// MyEditorModule.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OpenMessageBusTester();
    TSharedPtr<FUICommandInfo> OpenTesterAction;
};

// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "MessageBusTesterEditor/IMessageBusTesterEditorModule.h" // 关键头文件

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 注册一个菜单项或工具栏按钮来触发 OpenMessageBusTester
}

void FMyEditorModule::ShutdownModule()
{
}

void FMyEditorModule::OpenMessageBusTester()
{
    // 安全地获取编辑器模块并调用显示函数
    if (IMessageBusTesterEditorModule* EditorModule = FModuleManager::GetModulePtr<IMessageBusTesterEditorModule>(TEXT("MessageBusTesterEditor")))
    {
        EditorModule->DisplayMessageBusTester();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("MessageBusTesterEditor module is not loaded. Ensure the plugin is enabled."));
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

从 `IMessageBusTesterModule` 的使用以及 `.uplugin` 中的 `Plugins` 字段可知，要使用此插件的功能，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `MessageBusTester` | 访问核心测试逻辑和接口 (`IMessageBusTesterModule`) |
| `UdpMessaging` | 插件本身依赖的 UDP 消息传输模块，这是测试的目标 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏升级为新的 `UE_LOGF` 格式。 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复了本地化相关的编译警告。 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修正了 API 导出宏。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 启用 Android NDK 29 并修复相关编译问题。 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复了当远程客户端重置其 UDP 消息设置时，统计面板不更新的问题。 |

### 维护评价

该插件创建于 **2025 年 10 月**，时间较新。从提交历史看，它一直处于维护中，最后一次功能性更新（修复统计面板）发生在 **2025 年 11 月**，距离当前时间不足一年。近期的提交主要是兼容性维护（如升级日志宏、修复编译问题）。

-   **状态**：实验性 (`IsBetaVersion: true`)，默认不启用。
-   **活跃度**：**维护中**，但更新频率不高，主要是编译和兼容性修复。
-   **已知限制**：仅用于测试和调试目的，其 API 和行为可能在后续版本中更改或移除。
-   **推荐使用**：推荐给**引擎开发者、网络功能贡献者或需要深度调试消息总线问题的团队**。不建议在最终产品中依赖此插件的功能或 API。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)
-   [官方文档]() (无)
-   [测试用例]() (未在提供的文件列表中发现明确的测试文件，测试逻辑可能集成在插件内部或通过其支持的 `MessageBusTesterApp` 程序运行)