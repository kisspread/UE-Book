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
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkHub) | |

## 用途

LiveLinkHub 并非一个简单的 UE 插件，而是一个**独立的桌面应用程序**（通常通过 Epic Games Launcher 安装）。它的核心作用是充当 **LiveLink 数据的中央枢纽（Hub）**。

在复杂的动画制作流程中，可能有多个动捕设备、动画软件（如 MotionBuilder）或其它数据源需要将 LiveLink 数据发送到多个 Unreal Engine 实例（或 UEFN 项目）。LiveLinkHub 解决了这个问题：
1.  **集中连接**：所有数据源连接到 Hub，而不是直接连接到各个 UE 编辑器。
2.  **数据路由与分发**：Hub 可以将来自不同源的数据路由到一个或多个目标 UE 实例。
3.  **数据预览与过滤**：可以在数据到达 UE 之前，在 Hub 中进行预览、过滤或混合。
4.  **简化工作流**：避免了在每个 UE 编辑器中重复配置相同的 LiveLink 源，提高了大型团队协作的效率。

`LiveLinkHubEditor` 模块是 UE 编辑器侧的配套工具，主要用于**检测和启动**已安装的 LiveLinkHub 应用程序。

## 使用场景

-   **多源多目标动捕**：你有一个动捕工作室，使用了 OptiTrack、Vicon 等多个系统，需要同时为 3 个不同的 UE 项目提供实时动画数据。使用 LiveLinkHub 集中管理所有数据流。
-   **动画数据预处理**：你希望在将动捕数据发送到 UE 之前，先在 Hub 中进行平滑、重定向或混合操作。
-   **团队协作**：动画师使用 Maya 或 MotionBuilder 工作，需要将他们的工作实时推送给关卡设计师和程序员查看。Hub 作为中间层，确保所有人都能稳定接收数据。
-   **UEFN 内容创作**：为 Unreal Editor for Fortnite (UEFN) 提供实时动画数据流。

## 蓝图用法

`LiveLinkHubEditor` 模块主要提供 C++ 工具函数，用于在编辑器中集成 LiveLinkHub 的启动功能，**没有直接暴露给蓝图的节点**。其功能通常通过编辑器扩展（如工具栏按钮、菜单项）来调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 该模块功能通过 C++ API 调用，用于编辑器工具开发 | `UE::LiveLinkHubLauncherUtils` |

### 使用示例（蓝图描述）

由于没有直接的蓝图节点，典型的用法是在 C++ 编辑器模块中创建一个自定义的工具栏按钮或菜单项。当用户点击时，调用 `UE::LiveLinkHubLauncherUtils::OpenLiveLinkHub()` 来启动外部的 LiveLinkHub 应用程序。

## C++ 用法

`LiveLinkHubEditor` 模块提供了在编辑器中查找和启动 LiveLinkHub 应用程序的工具函数。

### 头文件引入

```cpp
#include "LiveLinkHubLauncherUtils.h"
```

### 基本用法

查找并启动已安装的 LiveLinkHub 应用程序。

```cpp
// 来源: Engine/Plugins/Animation/LiveLinkHub/Source/LiveLinkHubEditor/Public/LiveLinkHubLauncherUtils.h
#include "LiveLinkHubLauncherUtils.h"

void LaunchLiveLinkHubApp()
{
    UE::LiveLinkHubLauncherUtils::FInstalledApp LiveLinkHubInfo;
    
    // 1. 尝试查找已安装的 LiveLinkHub
    if (UE::LiveLinkHubLauncherUtils::FindLiveLinkHubInstallation(LiveLinkHubInfo))
    {
        UE_LOG(LogTemp, Log, TEXT("找到 LiveLinkHub 安装于: %s"), *LiveLinkHubInfo.InstallLocation);
        
        // 2. 启动应用程序
        UE::LiveLinkHubLauncherUtils::OpenLiveLinkHub();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("未找到 LiveLinkHub 的安装。请通过 Epic Games Launcher 安装。"));
    }
}
```

### 进阶用法

在编辑器工具栏中集成一个启动按钮。这通常在一个 `FExtender` 或 `FToolBarBuilder` 中完成。

```cpp
// 在某个编辑器模块的 StartupModule 中
#include "LiveLinkHubLauncherUtils.h"
#include "ToolMenus.h"

void FMyEditorModule::RegisterMenus()
{
    // ... 其他菜单注册代码
    
    UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Tools");
    FToolMenuSection& Section = Menu->AddSection("LiveLinkHubSection", LOCTEXT("LiveLinkHubHeading", "Live Link"));
    
    Section.AddMenuEntry(
        "OpenLiveLinkHub",
        LOCTEXT("OpenLiveLinkHub", "Open Live Link Hub"),
        LOCTEXT("OpenLiveLinkHubTooltip", "Launch the standalone Live Link Hub application"),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateStatic(&UE::LiveLinkHubLauncherUtils::OpenLiveLinkHub))
    );
}
```

## Demo 示例

以下示例展示如何在编辑器模块中注册一个菜单项来启动 LiveLinkHub。

**MyLiveLinkHubEditorModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyLiveLinkHubEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterMenus();
    TSharedPtr<FUICommandList> PluginCommands;
};
```

**MyLiveLinkHubEditorModule.cpp**
```cpp
#include "MyLiveLinkHubEditorModule.h"
#include "LiveLinkHubLauncherUtils.h"
#include "ToolMenus.h"
#include "Framework/Commands/UICommandList.h"
#include "Framework/Commands/UICommandInfo.h"

#define LOCTEXT_NAMESPACE "FMyLiveLinkHubEditorModule"

void FMyLiveLinkHubEditorModule::StartupModule()
{
    PluginCommands = MakeShareable(new FUICommandList);
    RegisterMenus();
}

void FMyLiveLinkHubEditorModule::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
}

void FMyLiveLinkHubEditorModule::RegisterMenus()
{
    UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Tools");
    FToolMenuSection& Section = Menu->FindOrAddSection("LiveLinkHubSection");
    
    Section.AddMenuEntry(
        "OpenLiveLinkHub",
        LOCTEXT("OpenLiveLinkHub_Label", "Open Live Link Hub"),
        LOCTEXT("OpenLiveLinkHub_Tooltip", "Launch the standalone Live Link Hub application for central LiveLink data routing."),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateStatic(&UE::LiveLinkHubLauncherUtils::OpenLiveLinkHub))
    );
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyLiveLinkHubEditorModule, MyLiveLinkHubEditor)
```

## 模块依赖

`LiveLinkHubEditor` 模块的依赖关系未在提供的 Build.cs 中明确列出。根据其功能（查找已安装应用、启动进程）推断，它可能依赖于标准的编辑器和系统交互模块。

| 模块 | 用途 |
|---|---|
| （无特殊依赖） | 该模块功能相对独立，主要依赖 Core、CoreUObject 等基础模块进行字符串处理和模块管理。 |

## 维护状态

### 近期更新

```
- b21ff31031fe Live Link Hub: Add "auxiliary channel" endpoint negotiation.
- 2057280165b3 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n
- 459b8b7c26ea LiveLinkHub - Fix UE only keeping track of a single LLH instance and displaying an invalid LLH status even if there is an active connection
```

-   `b21ff31031fe` (2025-10-03): 为 LiveLinkHub 添加了“辅助通道”端点协商功能，属于功能性更新。
-   `2057280165b3` (2025-09-15): 代码维护，修正了 DLL 导出标记，属于编译兼容性修复。
-   `459b8b7c26ea` (2025-08-20): 修复了一个重要的状态显示 Bug，属于稳定性修复。

### 维护评价

**活跃维护**。LiveLinkHub 是 Epic Games 在动画和虚拟制片领域的重要工具，处于积极开发中。从提交记录看，最近三个月内有功能性更新（辅助通道）和关键 Bug 修复，表明项目仍在迭代。作为 `IsBetaVersion: true` 的插件，其 API 和功能可能会发生变化，但核心架构稳定。**推荐在需要复杂 LiveLink 数据管理的项目中使用**，但需注意其 Beta 状态。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkHub)
-   [官方文档]() (暂无)
-   [测试用例]() (未在提供的路径中发现独立测试文件，测试可能集成在 LiveLink 主模块或引擎测试中)