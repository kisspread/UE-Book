# Editor Performance

> Plugin that provides Editor Performance feedback to developers（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器性能监控 |
| 分类 | Performance |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorPerformance` (Editor), `StallLogSubsystem` (Editor), `CrashDiagnostics` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorPerformance) | |

## 用途

这个插件的核心目的是**监控和诊断 Unreal Editor 自身在运行时遇到的性能问题**，特别是卡顿（Stall）和崩溃（Crash），并为开发者提供相关的诊断信息反馈。它不是一个面向最终用户或游戏内容的功能插件，而是一个**面向引擎开发者和高级用户**的调试与分析工具。

插件由三个紧密协作的模块组成：
1.  **StallLogSubsystem**: 核心子系统，负责**检测、记录和展示编辑器卡顿事件**。当编辑器主线程因长时间计算或资源加载而无响应（卡顿）时，它会记录下这些事件，方便开发者事后分析卡顿原因和频率。
2.  **CrashDiagnostics**: 负责收集和展示**编辑器崩溃相关的诊断信息**。它可能在崩溃发生前后收集关键状态、堆栈信息或内存快照，帮助开发者定位导致编辑器崩溃的根本原因。
3.  **EditorPerformance**: 主模块，很可能负责协调上述功能，并将性能状态（如最近的卡顿、崩溃记录）集成到编辑器的状态栏（Status Bar）等可视化界面中，提供直观的反馈。

## 使用场景

-   你在使用 UE5 编辑器进行大型关卡编辑或蓝图编译时，频繁遇到编辑器界面**卡死或响应缓慢**，需要定位具体是哪个操作导致的卡顿。
-   你的编辑器在处理特定资产或执行某些操作时**意外崩溃**，需要查看崩溃前的性能状态和诊断日志来排查原因。
-   你是一个引擎工具开发者，需要**监控编辑器工具的性能影响**，确保它们不会引入严重的卡顿或不稳定。
-   你需要对编辑器的**长期运行稳定性**进行基准测试或压力测试，并收集性能数据。

## 蓝图用法

该插件的主要功能通过 `UStallLogSubsystem` 提供，这是一个 `UEditorSubsystem`。在编辑器蓝图（例如编辑器工具或窗口蓝图）中，你可以访问该子系统。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateStallLogPanel` | 创建并返回一个包含卡顿日志历史记录的 Slate Widget（面板），可用于嵌入自定义编辑器窗口。 | `UStallLogSubsystem` |

### 使用示例（蓝图描述）

1.  **获取子系统**：在编辑器工具蓝图的 `Event BeginPlay` 或相应初始化事件中，使用 “Get Editor Subsystem” 节点，类选择 `UStallLogSubsystem`。
2.  **创建日志面板**：调用子系统的 `Create Stall Log Panel` 节点，这会返回一个 `SWidget` 引用。
3.  **嵌入窗口**：将这个 `SWidget` 作为子项添加到你的自定义编辑器窗口（`SWindow`）的布局中，即可在窗口内实时显示编辑器的卡顿记录。

## C++ 用法

该插件主要面向 C++ 开发者，用于深度集成到编辑器工具链中。

### 头文件引入

```cpp
#include "StallLogSubsystem.h"
```

### 基本用法

以下示例展示如何在编辑器工具模块中获取 `UStallLogSubsystem` 并创建一个嵌入了卡顿日志的停靠式选项卡。

```cpp
// 在你的编辑器工具初始化代码中（例如 FXXXModule::StartupModule）
#include "StallLogSubsystem.h"
#include "Framework/Docking/TabManager.h"

void FMyEditorToolModule::RegisterTabSpawner(const TSharedPtr<FWorkspaceItem>& WorkspaceGroup)
{
    // 获取卡顿日志子系统
    UStallLogSubsystem* StallSubsystem = GEditor->GetEditorSubsystem<UStallLogSubsystem>();
    if (StallSubsystem)
    {
        // 注册一个名为“MyStallLogTab”的选项卡
        FGlobalTabmanager::Get()->RegisterNomadTabSpawner("MyStallLogTab", FOnSpawnTab::CreateLambda([StallSubsystem](const FSpawnTabArgs& Args)
        {
            // 使用子系统创建日志面板 Widget
            TSharedRef<SWidget> StallLogPanel = StallSubsystem->CreateStallLogPanel();

            // 创建一个包含该面板的停靠式选项卡
            return SNew(SDockTab)
                .TabRole(NomadTab)
                [
                    StallLogPanel
                ];
        }))
        .SetDisplayName(LOCTEXT("StallLogTabTitle", "Stall Log"))
        .SetMenuType(ETabSpawnerMenuType::Hidden) // 可根据需要设置菜单可见性
        .SetGroup(WorkspaceGroup.ToSharedRef());
    }
}
```

### 进阶用法

结合 `CrashDiagnostics` 模块，可以构建一个综合的“编辑器诊断”窗口。虽然本模块文档未提供 `CrashDiagnostics` 的详细头文件，但其用法应与 `StallLogSubsystem` 类似，可能提供创建崩溃诊断面板的方法。

## Demo 示例

以下是一个最小的编辑器工具模块示例，它注册了一个选项卡来显示由 `EditorPerformance` 插件提供的卡顿日志。

```cpp
// MyStallLogViewer.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyStallLogViewerModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterTabSpawner();
    void UnregisterTabSpawner();
};
```

```cpp
// MyStallLogViewer.cpp
#include "MyStallLogViewer.h"
#include "StallLogSubsystem.h"
#include "Framework/Docking/TabManager.h"
#include "WorkspaceMenuStructure.h"
#include "WorkspaceMenuStructureModule.h"

#define LOCTEXT_NAMESPACE "FMyStallLogViewerModule"

void FMyStallLogViewerModule::StartupModule()
{
    RegisterTabSpawner();
}

void FMyStallLogViewerModule::ShutdownModule()
{
    UnregisterTabSpawner();
}

void FMyStallLogViewerModule::RegisterTabSpawner()
{
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner("MyStallLogViewer", FOnSpawnTab::CreateRaw(this, &FMyStallLogViewerModule::SpawnTab))
        .SetDisplayName(LOCTEXT("TabTitle", "My Stall Log"))
        .SetTooltipText(LOCTEXT("TooltipText", "Open a tab showing editor stall logs."))
        .SetGroup(WorkspaceMenu::GetMenuStructure().GetToolsCategory())
        .SetIcon(FSlateIcon(FAppStyle::GetAppStyleSetName(), "Icons.Bug"));
}

void FMyStallLogViewerModule::UnregisterTabSpawner()
{
    FGlobalTabmanager::Get()->UnregisterNomadTabSpawner("MyStallLogViewer");
}

TSharedRef<SDockTab> FMyStallLogViewerModule::SpawnTab(const FSpawnTabArgs& Args)
{
    // 获取卡顿日志子系统
    UStallLogSubsystem* StallSubsystem = GEditor->GetEditorSubsystem<UStallLogSubsystem>();
    TSharedPtr<SWidget> ContentWidget;

    if (StallSubsystem)
    {
        ContentWidget = StallSubsystem->CreateStallLogPanel();
    }
    else
    {
        ContentWidget = SNew(STextBlock).Text(LOCTEXT("SubsystemNotFound", "StallLogSubsystem not found. Is the EditorPerformance plugin enabled?"));
    }

    return SNew(SDockTab)
        .TabRole(NomadTab)
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot()
            .AutoHeight()
            [
                SNew(STextBlock)
                .Text(LOCTEXT("PanelHeader", "Editor Stall History"))
                .Font(FCoreStyle::GetDefaultFontStyle("Bold", 14))
                .Margin(FMargin(5, 5))
            ]
            + SVerticalBox::Slot()
            .FillHeight(1.0f)
            [
                ContentWidget.ToSharedRef()
            ]
        ];
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyStallLogViewerModule, MyStallLogViewer)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorDataStorageFeatures` | 插件显式依赖的插件，很可能为性能数据的存储（如 TEDS，Editor Data Storage）提供底层支持。 |
| `StallDetection` (推测) | 可能用于检测编辑器主线程卡顿的核心功能模块。 |
| `PerformanceMonitoring` (推测) | 可能用于收集更广泛的编辑器性能指标。 |

*注：具体依赖需查看各模块的 Build.cs 文件。此列表基于插件功能推断。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `e9acc6db` | EditorPerformance: TEDS-based diagnostic signaling for the status bar | 基于 TEDS 改进状态栏诊断信号 |
| 2026-04-13 | `f5d68e93` | [Crash Diagnostics] Add Crash Diagnostics panel to the Editor Diagnostics window | 添加崩溃诊断面板 |
| 2026-03-30 | `e0fedb7b` | Editor Diagnostics | 编辑器诊断功能更新 |
| 2026-03-30 | `dc530088` | Editor Diagnostics | 编辑器诊断功能更新 |
| 2025-12-19 | `ff7b39f1` | Added Free Disk Space KPIs and removed the free disk space check on editor startup | 新增磁盘空间指标，移除启动检查 |

### 维护评价

-   **创建时间**: 2024年3月创建，插件历史较短。
-   **更新频率**: 非常活跃。近期（2026年3-4月）有多次连续的功能性更新，特别是关于 TEDS 集成和新面板的添加。
-   **维护状态**: **活跃维护中**。作为 Epic Games 官方开发的实验性（从首次提交信息看）性能工具，其开发非常积极。
-   **已知限制**: 插件最初是“实验性且默认不启用”，虽然当前版本的 `.uplugin` 显示为默认启用且非 Beta 版，但其从 `Experimental` 文件夹发布表明它可能仍处于功能完善和测试阶段。
-   **推荐使用**: **推荐**。对于遇到编辑器性能问题并希望获得官方级诊断工具的开发者，这是一个非常有价值且正在持续改进的插件。建议在开发环境或需要诊断编辑器问题时启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorPerformance)
- 官方文档 (暂无)
- 测试用例 (暂未发现公开的测试文件)