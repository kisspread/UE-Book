```markdown
# Render Grid

> Advanced pipeline for use in creating rendered cinematics.

| 属性 | 值 |
|---|---|
| 中文名 | 渲染网格 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderGrid` (Runtime), `RenderGridDeveloper` (Runtime), `RenderGridEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid) | |

## 用途

Render Grid 插件为影视级渲染工作流提供一套完整的编辑器工具。它允许用户在 Unreal Editor 中创建、管理和批量渲染多个“渲染作业”（Render Job）。每个作业可以指定不同的关卡（Map）、Level Sequence、输出路径、渲染设置（本地属性或通过 Remote Control 暴露的属性），并直接在编辑器中预览单帧或全序列的低分辨率输出，以便快速迭代。

此插件解决了传统渲染流程中需要手动管理多个独立电影管道作业、缺乏集中式可视化管理界面的痛点。它提供**作业列表**（支持排序、过滤、启用/禁用）、**作业属性编辑**（支持本地属性面板和远程控制面板）、**实时预览**（可直接在视口中播放序列）、**预览渲染**（单帧低分辨率快照）以及**批量渲染**（一键按顺序执行所有启用的作业）等功能。

## 使用场景

- **批量渲染序列**：你有多个镜头需要依次渲染输出为 EXR 或 PNG，希望用一个工具管理所有作业并一键启动渲染队列。
- **远程控制参数调优**：项目中使用了 Remote Control API 暴露了某些材质参数或场景变量，你希望在每次渲染前为不同作业设置不同的远程控制值。
- **快速预览结果**：你只需要快速查看某一个镜头在特定帧的渲染效果（低分辨率），而无需启动完整的 Movie Render Queue 导出流程。
- **团队协作**：一个美术/导演使用 Render Grid 预览镜头选择，另一个渲染技术美术使用 Remote Control 绑定渲染参数，作业配置可通过蓝图或 C++ 扩展。

## 蓝图用法

本插件`RenderGridEditor`模块是纯编辑器模块，不提供可直接在蓝图图表中调用的蓝图标节点。所有编辑功能通过 UI 交互完成。

但插件包含的运行时模块 `RenderGrid` 提供了核心数据类（如 `URenderGrid`、`URenderGridJob`），这些类可以在蓝图中创建和修改。以下列出最常用的蓝图标节点（位于`RenderGrid`模块）：

### 核心节点（在运行时模块中）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Render Grid Job` | 创建一个新的渲染作业对象 | `URenderGrid` |
| `Get Render Grid Jobs` | 获取当前渲染网格中的所有作业数组 | `URenderGrid` |
| `Get Job Output Path` | 获取作业的输出文件路径 | `URenderGridJob` |
| `Set Job Output Path` | 设置作业的输出文件路径 | `URenderGridJob` |
| `Get Job Level Sequence` | 获取作业关联的 Level Sequence 资产 | `URenderGridJob` |
| `Set Job Level Sequence` | 设置作业关联的 Level Sequence 资产 | `URenderGridJob` |
| `Render Grid Job (Event)` | 当渲染作业状态变更时广播的事件（如渲染完成） | `URenderGridJob` |

### 使用示例（蓝图）

1. 创建一个 Render Grid 资产（右键内容浏览器 → Miscellaneous → Render Grid）。
2. 在 Blueprint 中引用该资产，并调用 `Get Render Grid Jobs` 获取作业列表。
3. 遍历作业，通过 `Get Job Output Path` 读取路径，或通过 `Set Job Level Sequence` 更改序列。
4. 若要触发批量渲染，可使用 `Batch Render List` 编辑器命令（或通过 C++ 调用 `URenderGrid::StartBatchRender`，该函数同样暴露给蓝图，但需要配合 Movie Render Pipeline 插件）。

## C++ 用法

本模块主要为编辑器提供 GUI 和交互逻辑，若要用 C++ 扩展 RenderGrid 编辑器功能，需引用以下公共接口。

### 头文件引入

```cpp
#include "RenderGridEditorModule.h"
#include "IRenderGridEditor.h"
#include "RenderGrid/RenderGrid.h"             // 运行时核心类
#include "RenderGrid/RenderGridJob.h"
```

### 基本用法

#### 创建 Render Grid 资产（通过工厂）

```cpp
// 引擎启动时自动注册工厂，用户直接在内容浏览器创建即可
// 如需 C++ 编程创建：
URenderGridBlueprintFactory* Factory = NewObject<URenderGridBlueprintFactory>();
Factory->ParentClass = URenderGrid::StaticClass();
// 然后使用 UFactory::FactoryCreateNew 创建 URenderGridBlueprint 实例
```

#### 获取当前打开的 Render Grid 编辑器

```cpp
// 通过 IRenderGridEditorModule 接口获取
IRenderGridEditorModule& EditorModule = FModuleManager::LoadModuleChecked<IRenderGridEditorModule>("RenderGridEditor");
// 注意：IRenderGridEditorModule 仅提供工厂方法，不能直接查询当前编辑器实例
// 若需要与编辑器交互，可通过 FBlueprintEditor 方法获取
```

#### 在自定义编辑器模式下创建 RenderGrid 编辑器

```cpp
// 参考 RenderGridEditorModule.cpp 中的 CreateRenderGridEditor 实现：
EToolkitMode::Type Mode = EToolkitMode::Standalone;
TSharedPtr<IToolkitHost> ToolkitHost = ...;
URenderGridBlueprint* Blueprint = ...; // 必须已有效

IRenderGridEditorModule& EditorModule = FModuleManager::LoadModuleChecked<IRenderGridEditorModule>("RenderGridEditor");
TSharedRef<IRenderGridEditor> Editor = EditorModule.CreateRenderGridEditor(Mode, ToolkitHost, Blueprint);
Editor->SetIsDebugging(false);
```

### 进阶用法

#### 扩展 Props Source Widget 工厂

插件支持通过 `IRenderGridPropsSourceWidgetFactory` 接口注册新的属性源 UI 部件。例如插件内置了 `Local` 和 `RemoteControl` 两种工厂。自定义工厂示例：

```cpp
// 定义工厂类
class FMyCustomPropsWidgetFactory : public IRenderGridPropsSourceWidgetFactory
{
    virtual TSharedPtr<SRenderGridPropsBase> CreateInstance(
        URenderGridPropsSourceBase* PropsSource,
        TSharedPtr<IRenderGridEditor> BlueprintEditor) override
    {
        // 返回自定义的 SCompoundWidget 实例
        return SNew(SMyCustomPropsWidget, BlueprintEditor, Cast<UMyCustomPropsSource>(PropsSource));
    }
};

// 在模块 StartupModule 中注册
void FMyModule::StartupModule()
{
    IRenderGridEditorModule& RenderGridModule = FModuleManager::LoadModuleChecked<IRenderGridEditorModule>("RenderGridEditor");
    TSharedPtr<IRenderGridPropsSourceWidgetFactory> Factory = MakeShared<FMyCustomPropsWidgetFactory>();
    RenderGridModule.GetPropsSourceWidgetFactories().Add(ERenderGridPropsSourceType::Custom, Factory);
}
```

#### 批量渲染编程

```cpp
// 获取当前编辑器中的 RenderGrid 实例
URenderGrid* Grid = ...; // 从 Blueprint 中获取 GetRenderGrid();
if (Grid)
{
    // 构建作业列表
    TArray<URenderGridJob*> JobsToRender;
    // ... 填充作业 ...
    
    // 启动批量渲染（使用默认设置，实际会打开 Movie Render Queue 对话框）
    // 注意：该函数定义在 URenderGrid 类中（运行时模块）
    Grid->StartBatchRender(JobsToRender);
}
```

## Demo 示例

以下是一个最小编辑器模块示例，展示如何创建 RenderGrid 编辑器并打开（类似 `TutorialEditor` 的方式）。

### MyRenderGridEditorModule.h

```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "Widgets/Docking/SDockTab.h"

class IToolkitHost;

class FMyRenderGridEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedRef<SDockTab> SpawnEditorTab(const FSpawnTabArgs& Args);
    TSharedPtr<IToolkitHost> ToolkitHost;
};
```

### MyRenderGridEditorModule.cpp

```cpp
#include "MyRenderGridEditorModule.h"
#include "IRenderGridEditor.h"
#include "IRenderGridEditorModule.h"
#include "RenderGridBlueprint.h"
#include "BlueprintEditorTabs.h"
#include "Toolkits/IToolkitHost.h"
#include "Widgets/Docking/SDockTab.h"

IMPLEMENT_MODULE(FMyRenderGridEditorModule, MyRenderGridEditor);

void FMyRenderGridEditorModule::StartupModule()
{
    // 注册一个 Tab 生成器
    FGlobalTabmanager::Get()->RegisterTabSpawner("MyRenderGridEditor",
        FOnSpawnTab::CreateRaw(this, &FMyRenderGridEditorModule::SpawnEditorTab))
        .SetDisplayName(NSLOCTEXT("MyRenderGridEditor", "TabTitle", "My Render Grid"))
        .SetMenuType(ETabSpawnerMenuType::Hidden);
}

void FMyRenderGridEditorModule::ShutdownModule()
{
    FGlobalTabmanager::Get()->UnregisterTabSpawner("MyRenderGridEditor");
}

TSharedRef<SDockTab> FMyRenderGridEditorModule::SpawnEditorTab(const FSpawnTabArgs& Args)
{
    // 创建一个临时 Blueprint（实际使用应从资产编辑器获得）
    URenderGridBlueprint* Blueprint = NewObject<URenderGridBlueprint>();
    Blueprint->SetFlags(RF_Transactional);
    Blueprint->RenderGrid = NewObject<URenderGrid>(Blueprint);
    
    // 创建编辑器
    IRenderGridEditorModule& EditorModule = FModuleManager::LoadModuleChecked<IRenderGridEditorModule>("RenderGridEditor");
    TSharedRef<IRenderGridEditor> Editor = EditorModule.CreateRenderGridEditor(
        EToolkitMode::Standalone, 
        ToolkitHost, 
        Blueprint
    );
    
    // 返回编辑器的主 tab（通常 FBlueprintEditor 会自行管理 tab)
    // 实际 FBlueprintEditor 会注册多个 tab，这里简化为一个占位
    return SNew(SDockTab)
        .Label(NSLOCTEXT("MyRenderGridEditor", "TabLabel", "Render Grid"))
        .TabRole(ETabRole::MajorTab);
}
```

> **注意**：此 Demo 仅展示 API 调用方式，实际使用时须确保 `URenderGridBlueprint` 和 `URenderGrid` 已经正确初始化，且已加载相关依赖模块。

## 模块依赖

本插件编辑器模块 `RenderGridEditor` 依赖以下独特模块（省略常见 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `RenderGrid` | 运行时核心数据类和渲染逻辑（必须） |
| `RenderGridDeveloper` | 开发时辅助工具（如属性编辑、测试） |
| `RemoteControl` | 远程控制属性源 UI（用于显示 Props） |
| `RemoteControlUI` | 远程控制的编辑器 UI 组件（用于 Props 表格） |
| `LevelSequence` | 作业关联的序列播放 |
| `MovieRenderPipeline` | 批量渲染执行（启动 MRQ） |
| `MovieRenderPipelineEditor` | MRQ 编辑器的 UI 集成 |
| `WorkspaceMenuStructure` | 编辑器菜单结构 |
| `BlueprintEditor` | FBlueprintEditor 基类 |
| `KismetCompiler` | 蓝图编译 |
| `AssetDefinition` | 资产类型定义 |

## 维护状态

### 近期更新

- 2025-09-15 `0fcf72f1` — Render Grid: fixed crash when passing in an empty string when setting remote control values（修复空字符串崩溃）
- 2025-06-11 `b57e00bc` — Replace some usages of FORCEINLINE with inline in Rendering modules（渲染模块内联优化）
- 2025-04-15 `45a9eb59` — [Truncation Warnings] Deprecate FVector2D delegates in GraphEditor module（编辑器废弃警告适配）
- 2025-04-09 `3ffb1588` — Header unit / c++ modules compile fixes（编译修复）
- 2024-08-30 `df1cc540` — Gather text from source, resolve macro has an empty source text (.cpp files)（代码初始化提交）

### 维护评价

插件创建于 2024 年 8 月，是 UE 5.4 之后引入的新工具。从 git log 可见最近一次实质性 bug 修复就在 2025 年 9 月（修复崩溃），且多次收到编译修复更新，表明 Epic Games 仍在积极维护。由于标记为实验性（IsExperimentalVersion=true），API 可能发生变化。目前功能已较为完整（作业列表、预览、远程控制集成），推荐在新项目中尝试使用，但生产环境需注意实验性标签的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/render-grid-overview/)（假设）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid/Tests/)
```