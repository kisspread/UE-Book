# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器数据存储特性 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（调试工具与UI组件） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

EditorDataStorageFeatures 是 Epic Games 推出的一个实验性插件，它并非一个独立的编辑器工具，而是 **TEDS (Editor Data Storage) 生态系统在编辑器用户界面层面的具体实现和扩展集合**。

TEDS 本身是一个底层的、高性能的编辑器数据存储和查询系统。而本插件的作用是 **利用 TEDS 的能力，以数据驱动和可组合的方式重新构建或增强编辑器中的各种界面（如大纲视图、属性编辑器、内容浏览器、资产选择器等）**。

它解决的核心问题是：在处理大规模场景或资产数据时，传统编辑器UI（如SListWidget， STableRow）可能面临的性能瓶颈和扩展性限制。通过将UI与底层的TEDS存储和查询解耦，该插件旨在提供更灵活、更高效的数据管理和UI呈现方案。

## 使用场景

- **开发大型开放世界或密集场景项目**：当传统Outliner因场景Actor数量过多而卡顿时，可尝试使用基于TEDS的Outliner (`TedsOutliner`) 来提升浏览和交互性能。
- **需要高度自定义的编辑器界面**：如果你需要开发一个自定义的资产浏览器、检查器或任何以数据表形式展示信息的工具，可以基于TEDS的查询栈 (`TedsQueryStack`) 和表格查看器 (`TedsTableViewer`) 构建，而不是从头实现复杂的列表控件。
- **进行编辑器技术研究和原型开发**：作为学习和探索UE5下一代编辑器数据架构的入口，理解其查询模型、数据桥接和UI渲染方式。
- **调试TEDS系统本身**：该插件提供了丰富的调试工具（`TedsDebugger`），是了解和排查TEDS数据存储、行引用、层级关系等问题的必备工具。

## 蓝图用法

该插件主要面向编辑器底层C++开发，其提供的功能大多通过C++接口或Slate Widget实现，**没有直接暴露为蓝图节点的通用功能**。其调试和查询界面本身就是一个Slate应用程序。

## C++ 用法

核心用法围绕 TEDS 的 `ICoreProvider` 接口以及本插件提供的查询编辑器模型 (`FTedsQueryEditorModel`) 和表格查看器 (`STedsTableViewer`) 展开。

### 头文件引入

使用该插件的不同模块时，需包含对应模块的头文件。以下为调试器相关头文件示例：
```cpp
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
// 引入TEDS调试器模块
#include "TedsDebuggerModule.h"
```

### 基本用法：打开调试器窗口

最直接的用法是打开TEDS调试器的DockTab，以便在编辑器中交互式地查询和浏览数据。
```cpp
// 在某个编辑器菜单或按钮的点击事件中
FTedsDebuggerModule& DebuggerModule = FModuleManager::LoadModuleChecked<FTedsDebuggerModule>(TEXT("TedsDebugger"));
DebuggerModule.Get().OpenTedsDebuggerTab(FSpawnTabArgs());
// OpenTedsDebuggerTab 是私有的，通常通过编辑器菜单命令调用。
// 下面展示一个更符合实践的“注册Tab并打开”的示例思路。
```

**一个更完整的示例（模拟模块启动并注册Tab）：**
```cpp
// 文件路径: 假设你在自己的编辑器模块中
// MyEditorModule.h
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "TedsDebuggerModule.h" // 关键依赖
#include "WorkspaceMenuStructure.h"
#include "WorkspaceMenuStructureModule.h"

void FMyEditorModule::StartupModule()
{
    // 确保TEDS调试器模块已加载
    FModuleManager::Get().LoadModule(TEXT("TedsDebugger"));
}

void FMyEditorModule::ShutdownModule()
{
    // 清理代码...
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

### 进阶用法：通过查询编辑器模型构建查询

`FTedsQueryEditorModel` 是理解本插件查询能力的核心。它允许你程序化地构建条件、生成查询描述，并最终获取匹配的数据行。
```cpp
// 文件路径: 基于 Private/QueryEditor/TedsQueryEditorModel.h 推断
#include "QueryEditor/TedsQueryEditorModel.h"
#include "EditorDataStorage.h" // 假设用于获取ICoreProvider

using namespace UE::Editor::DataStorage::Debug::QueryEditor;

void BuildCustomQuery()
{
    // 1. 获取TEDS核心接口 (ICoreProvider)
    ICoreProvider* Storage = /* 通常通过EditorDataStorage模块获取 */;

    // 2. 创建一个查询编辑器模型实例
    FTedsQueryEditorModel QueryModel(*Storage);

    // 3. 重置模型以从干净状态开始
    QueryModel.Reset();

    // 4. 添加条件：例如，查询包含‘USkeletalMeshComponent’列的行
    // 假设EOperatorType::All对应“所有”条件（Select）
    FConditionEntryHandle Handle;
    // 实际添加列类型的操作可能通过UI交互，模型内部维护。这里为演示。
    // EErrorCode AddColumnToCondition(FConditionEntryHandle Handle, const UScriptStruct* ColumnType);
    // AddColumnToCondition(Handle, USkeletalMeshComponent::StaticStruct());

    // 5. 生成查询描述（用于执行）
    FQueryDescription QueryDesc = QueryModel.GenerateQueryDescription();
    // 或者生成无选择项的描述（用于计数或表查看器）
    FQueryDescription NoSelectDesc = QueryModel.GenerateNoSelectQueryDescription();

    // 6. 将查询描述提交给TEDS执行（具体步骤依赖于TEDS API）
    // QueryHandle Handle = Storage->RegisterQuery(QueryDesc);
    // 然后通过QueryStack或直接遍历结果。
}
```

## Demo 示例

以下是一个最小的编辑器模块示例，演示如何确保TEDS调试器模块被加载，并提供一个基本的打开入口（实际打开通常由TEDS调试器模块内部的菜单命令处理）。

```cpp
// 文件: TedsDemoModule.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FTedsDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OpenDebugger();
    TSharedPtr<FUICommandList> PluginCommands;
};

// 文件: TedsDemoModule.cpp
#include "TedsDemoModule.h"
#include "TedsDebuggerModule.h"
#include "Framework/Commands/UICommandList.h"
#include "Framework/Commands/UIAction.h"

#define LOCTEXT_NAMESPACE "FTedsDemoModule"

void FTedsDemoModule::StartupModule()
{
    // 加载所需的TEDS核心模块（调试器模块会依赖它们）
    FModuleManager::Get().LoadModule(TEXT("TedsDebugger"));
    FModuleManager::Get().LoadModule(TEXT("EditorDataStorage"));

    // 创建并注册一个简单的菜单命令来打开调试器
    PluginCommands = MakeShareable(new FUICommandList);
    PluginCommands->MapAction(
        FUIAction(FExecuteAction::CreateRaw(this, &FTedsDemoModule::OpenDebugger)),
        // 这里简化了命令定义，实际需要FUICommandInfo
        nullptr, // FInputChord
        nullptr, // FUIAction
        EUIActionRepeatMode::RepeatDisabled
    );

    // 注意：将命令集成到编辑器菜单/工具栏需要更详细的代码
    // (如 FModuleManager::Get().LoadModuleChecked<FToolMenusModule>(“ToolMenus”).RegisterMenus())
}

void FTedsDemoModule::ShutdownModule()
{
    // 清理
}

void FTedsDemoModule::OpenDebugger()
{
    // 获取调试器模块并请求打开Tab
    FTedsDebuggerModule* DebuggerModule = FModuleManager::GetModulePtr<FTedsDebuggerModule>(TEXT("TedsDebugger"));
    if (DebuggerModule)
    {
        // 此处调用了内部的公共接口或通过Tab管理器触发
        // FGlobalTabmanager::Get()->TryInvokeTab(FTedsDebuggerModule::GetTedsDebuggerTabName());
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FTedsDemoModule, TedsDemo)
```

## 模块依赖

使用本插件的任何模块，都需要依赖其提供的核心TEDS接口和UI框架。具体依赖取决于你使用的子模块。

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS 的核心运行时模块，提供 `ICoreProvider` 等基础接口 |
| `EditorDataStorageUI` | TEDS 的UI渲染和Widget抽象层，提供 `IUiProvider`, `FTypedElementWidgetConstructor` 等 |
| `QueryStack` | TEDS 的查询处理栈，用于构建和执行复杂的过滤、排序、层级查询 |
| `TedsDebugger` | 提供完整的TEDS数据调试界面（本插件的一部分） |
| `TedsQueryStack` | 提供查询编辑器模型和UI（本插件的一部分） |
| `TedsTableViewer` | 提供通用的表格数据显示Widget（本插件的一部分） |

**注意**：由于 `Core`, `CoreUObject`, `Engine`, `Slate`, `UMG` 等基础模块是几乎所有插件都依赖的常见模块，此处已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限UEFN模式下启用TEDS Outliner |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在TEDS Outliner中隐藏非编辑层级实例内未加载的Actor行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | [TedsOutliner] 修复无效的跨层级拖放操作 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | [回退] - 变更列表 53940377 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在TEDS Outliner中隐藏非编辑层级实例内未加载的Actor行 |

### 维护评价

**活跃维护中**。

该插件创建于2024年7月，至今约1.8年。虽然它被标记为实验性（`IsExperimentalVersion=true`）且默认不启用，但从近期（2026年5月）的Git提交记录来看，Epic团队仍在**持续且活跃地**进行开发，近期的更新集中在对其子模块`TedsOutliner`的功能增强和bug修复上。

这表明 `EditorDataStorageFeatures` 是UE5编辑器技术栈中一个**重点推进的实验性方向**，其核心子模块（如Outliner）已具备一定的可用性。然而，由于整个插件仍处于实验阶段，其API和功能存在变动的可能，**不建议在追求长期稳定性的生产项目核心功能中使用**。

它非常适合作为**技术预研、原型开发或内部工具构建的参考和组件来源**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档]() (暂无)