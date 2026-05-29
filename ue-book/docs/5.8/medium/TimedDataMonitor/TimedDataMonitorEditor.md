# Timed Data Monitor

> Utilities to monitor inputs that can be time synchronized.

| 属性 | 值 |
|---|---|
| 中文名 | 时间同步数据监控器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TimedDataMonitor` (UncookedOnly), `TimedDataMonitorEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-01-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TimedDataMonitor) | |

## 用途

该插件的核心功能是提供一个**集中式监控面板**，用于实时诊断和调试与时间同步相关的输入数据源。它解决了虚拟制片和多设备同步场景中，各种数据输入（如LiveLink、时间码提供器、自定义时间步进器）的同步状态和数据流健康度难以直观查看的问题。

插件通过一个编辑器窗口，汇总显示：
- **全局评估状态**：引擎是否因性能问题而节流。
- **时间码提供器状态**：当前时间码、系统时间、同步状态。
- **Genlock/自定义时间步进器状态**：帧率、同步状态、调试信息。
- **监控输入列表**：显示所有已注册的LiveLink主题或其他可监控输入源。
- **每个输入源的详细信息**：包括启用状态、评估偏移（秒或帧）、缓冲区大小、当前样本计数，以及**下溢、溢出、丢帧计数**等关键诊断指标。
- **时序图**：可视化数据到达的时间点与预期时间点的偏差。
- **缓冲区可视化**：图形化显示输入缓冲区的填充状态。

**为什么存在？** 在虚拟制片、广播或现场活动等实时性要求极高的场景中，数据同步的细微偏差可能导致画面撕裂、数据丢失或动作不流畅。此插件提供了必要的工具，让技术人员能够快速定位是哪个数据源、在哪个环节（如缓冲区满/空、评估偏移错误）出现了问题，从而进行调整。

## 使用场景

- 你正在搭建一个**虚拟制片现场**，使用多个摄像机追踪系统、LED屏幕控制器和音频设备，它们都通过LiveLink或时间码协议与引擎同步 → 用此插件监控所有数据源的同步健康度。
- 你的项目**实时合成**了摄像机画面和CG元素，需要确保CG元素的运动数据与真实摄像机的运动数据在时间上完全对齐 → 使用时序图和评估偏移功能进行校准。
- 在**现场直播或广播**工作流中，需要确保来自不同设备的视频、音频、元数据流在引擎中被正确处理和按时消费 → 查看缓冲区溢出/下溢计数。
- 你正在调试一个**自定义时间步进器**或**时间码提供器**插件，需要验证其同步状态和输出值 → 在此面板中查看其状态和输出。

## 蓝图用法

该插件主要提供**编辑器面板和工具**，而非暴露给蓝图的运行时功能。其公共API主要面向C++模块，用于在编辑器中管理和显示监控面板。源码中未发现 `UFUNCTION(BlueprintCallable)` 标记的函数。

### 核心节点

*此插件不提供蓝图可调用的节点。*

## C++ 用法

### 头文件引入

```cpp
#include "TimedDataMonitorEditorModule.h"
```

### 基本用法

**显示监控面板**

此插件的功能主要通过其编辑器面板访问。C++ 代码可以用于程序化地打开这个面板。

```cpp
// 获取TimedDataMonitor编辑器模块
FTimedDataMonitorEditorModule& TimedDataMonitorModule = FModuleManager::LoadModuleChecked<FTimedDataMonitorEditorModule>(TEXT("TimedDataMonitorEditor"));

// 获取当前的标签页管理器（通常在编辑器中）
TSharedPtr<FTabManager> TabManager = FGlobalTabmanager::Get();

// 尝试激活（如果未打开则打开）TimedDataMonitor面板
TimedDataMonitorModule.DisplayTimedDataMonitorPanel(TabManager);
```
*（代码逻辑推断自 `Public/TimedDataMonitorEditorModule.h` 和 `Private/STimedDataMonitorPanel.h` 中 `DisplayTimedDataMonitorPanel` 的声明与 `RegisterNomadTabSpawner` 的用法。）*

### 进阶用法

**注册/注销标签页生成器**

在自定义编辑器或需要集成此面板的模块中，你可以管理其标签页的注册。

```cpp
// 在启动你的自定义编辑器模块时
void FMyCustomEditorModule::StartupModule()
{
    // ... 其他初始化
    if (FTimedDataMonitorEditorModule* TimedDataMonitorModule = FModuleManager::GetModulePtr<FTimedDataMonitorEditorModule>(TEXT("TimedDataMonitorEditor")))
    {
        // 获取或创建你的标签页管理器
        TSharedPtr<FTabManager> MyTabManager = ...;
        TimedDataMonitorModule->RegisterNomadTabSpawner(MyTabManager);
    }
}

// 在关闭时
void FMyCustomEditorModule::ShutdownModule()
{
    // ... 其他清理
    if (FTimedDataMonitorEditorModule* TimedDataMonitorModule = FModuleManager::GetModulePtr<FTimedDataMonitorEditorModule>(TEXT("TimedDataMonitorEditor")))
    {
        TSharedPtr<FTabManager> MyTabManager = ...;
        TimedDataMonitorModule->UnregisterNomadTabSpawner(MyTabManager);
    }
}
```
*（示例基于 `Public/TimedDataMonitorEditorModule.h` 中 `RegisterNomadTabSpawner` 和 `UnregisterNomadTabSpawner` 的公共API。）*

## Demo 示例

以下是一个最小的 C++ 示例，展示如何在你的编辑器工具中集成并打开“时间同步数据监控器”面板。

```cpp
// MyEditorTool.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    /** 打开时间同步数据监控面板 */
    void OpenTimedDataMonitor();

private:
    /** 用于打开面板的UICommand */
    TSharedPtr<FUICommandInfo> OpenMonitorCommand;
};

// MyEditorTool.cpp
#include "MyEditorTool.h"
#include "TimedDataMonitorEditorModule.h"
#include "Framework/Docking/TabManager.h"
#include "Framework/Commands/UICommandList.h"

#define LOCTEXT_NAMESPACE "FMyEditorToolModule"

void FMyEditorToolModule::StartupModule()
{
    // 创建一个命令来打开面板
    FUICommandInfo::MakeCommandInfo(
        this->AsShared(),
        OpenMonitorCommand,
        FName("OpenTimedDataMonitor"),
        LOCTEXT("OpenTimedDataMonitor", "Time Sync Monitor"),
        LOCTEXT("OpenTimedDataMonitorTooltip", "Opens the Timed Data Monitor panel"),
        EUserInterfaceActionType::Button,
        FInputChord()
    );

    // 你可以将此命令绑定到菜单或工具栏
}

void FMyEditorToolModule::ShutdownModule()
{
    OpenMonitorCommand.Reset();
}

void FMyEditorToolModule::OpenTimedDataMonitor()
{
    FTimedDataMonitorEditorModule& TimedDataMonitorModule =
        FModuleManager::LoadModuleChecked<FTimedDataMonitorEditorModule>(TEXT("TimedDataMonitorEditor"));

    // 使用全局标签页管理器
    TimedDataMonitorModule.DisplayTimedDataMonitorPanel(FGlobalTabmanager::Get());
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorToolModule, MyEditorTool)
```

## 模块依赖

该插件依赖 **LiveLink** 插件来获取其监控的数据源。在你的项目 `.uproject` 文件中启用此插件时，LiveLink 插件会自动启用。

对于 **使用此插件API的C++模块**，其依赖关系如下：

| 模块 | 用途 |
|---|---|
| `LiveLink` | 提供LiveLink客户端和主题访问，是插件监控的主要数据来源。 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-21 | `251322d6` | LiveLink and TDM: Option to save settings. | 为LiveLink和TDM添加了保存设置的功能。 |
| 2026-02-21 | `58f7b461` | [Backout] - CL51083024 | 回退了某个变更（可能是临时性问题修复）。 |
| 2026-02-21 | `c8c1981c` | LiveLink and TDM: Option to save settings. | 再次提交“保存设置”功能（可能与回退相关）。 |
| 2026-01-08 | `2906cc5f` | LiveLinkHub - Disable Timed Data Monitor temporarily to work around crash | 在LiveLinkHub中临时禁用TDM以解决崩溃问题。 |
| 2026-01-07 | `0c117b61` | LiveLinkHub - Enable Timed Data Monitor | 在LiveLinkHub中启用TDM。 |

### 维护评价

- **年龄**：插件创建于2020年，约5年历史。
- **活跃度**：从最近提交记录看（2026年2月、1月），插件仍在**积极维护**中，最近的更新集中在功能完善（添加保存设置）和稳定性修复（解决崩溃问题）。
- **状态**：标记为 `IsBetaVersion=true`，属于实验性插件，但并未废弃。
- **推荐度**：**推荐在需要的场景中使用**。它是虚拟制片工具链中一个专业的诊断工具，虽然处于Beta阶段，但功能明确且维护活跃。由于默认未启用 (`EnabledByDefault: false`)，用户需要手动在插件管理器中启用它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TimedDataMonitor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TimedDataMonitor/Tests) *(路径推断，可能存在)*