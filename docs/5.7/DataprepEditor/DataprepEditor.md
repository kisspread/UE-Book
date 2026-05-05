# Dataprep Editor

> A tool to simplify creation and execution of data preparation pipelines from within the Unreal Editor.

| 属性 | 值 |
|---|---|
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `DataprepCore` (Runtime), `DataprepEditor` (Runtime), `DataprepEditorScriptingUtilities` (Runtime), `DataprepLibraries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-11-22 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor) | |

## 用途

Dataprep Editor 是一个用于在 Unreal Editor 内部创建、管理和执行数据准备（Data Preparation）管道的集成工具集。它解决的核心问题是：在将外部资产（如 CAD、BIM 模型）导入到 Unreal Engine 用于建筑可视化、工业仿真等场景时，原始数据往往包含大量冗余信息、不规范的命名、复杂的层级结构或不兼容的材质。手动清理和优化这些资产既繁琐又容易出错。

该插件通过提供一个可视化的、基于节点的编辑器界面，允许用户定义一系列自动化的“操作”（Actions），如重命名、合并网格体、简化几何体、转换材质等，并将这些操作组合成可重复使用的“管道”（Pipeline）。用户可以将这些管道应用到资产上，实现一键式批量处理，从而极大地提升资产准备的工作流效率和一致性。

## 使用场景

- **建筑可视化（ArchViz）**：你从 Revit 或 SketchUp 导入了一个完整的建筑模型，但发现它包含成千上万个独立的构件、复杂的材质名称和过高的多边形数量。你可以创建一个 Dataprep 管道，自动合并相似构件、重命名资产、优化几何体并替换为 Unreal 原生材质。
- **工业数字孪生**：你需要将来自不同 CAD 软件（如 CATIA, NX）的机械零件模型导入到 Unreal 中进行实时可视化。每个模型的结构和材质命名都不同。你可以为每种来源创建特定的 Dataprep 管道，将它们标准化为统一的命名规范和材质体系。
- **游戏资产批处理**：虽然主要用于企业领域，但其批处理逻辑同样适用于游戏开发。例如，你可以创建一个管道来批量为导入的静态网格体设置碰撞、生成 LOD 或调整光照贴图分辨率。

## 蓝图用法

当前 `DataprepEditor` 模块主要提供编辑器集成和 UI 扩展，其核心的蓝图可调用 API 分布在 `DataprepCore` 和 `DataprepLibraries` 模块中。本模块提供的主要是编辑器上下文和扩展点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SelectedObjects` | 获取在 Dataprep 编辑器中当前选中的对象数组。 | `UDataprepEditorContextMenuContext` |
| `DataprepAsset` | 获取当前正在编辑的 Dataprep 资产接口。 | `UDataprepEditorContextMenuContext` |

### 使用示例（蓝图描述）

在编辑器工具栏或资产右键菜单中扩展 Dataprep 功能时，可以获取 `UDataprepEditorContextMenuContext` 对象。通过该对象，你可以访问用户当前选中的资产（`SelectedObjects`）以及正在操作的 Dataprep 资产（`DataprepAsset`），从而在自定义的编辑器扩展中执行相关逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "DataprepEditorModule.h"
```

### 基本用法

获取 Dataprep 编辑器模块的单例接口，用于检查模块状态或访问其提供的工厂方法。

```cpp
// 检查模块是否可用
if (IDataprepEditorModule::IsAvailable())
{
    // 获取模块接口
    IDataprepEditorModule& DataprepEditorModule = IDataprepEditorModule::Get();

    // 使用模块接口创建自定义的 Dataprep 生产者 Widget 或详情面板
    // TSharedRef<SWidget> ProducersWidget = DataprepEditorModule.CreateDataprepProducersWidget(MyAssetProducers);
    // TSharedRef<SWidget> DetailsView = DataprepEditorModule.CreateDataprepDetailsView(MyObject);
}
```

### 进阶用法

通过 `IHasMenuExtensibility` 和 `IHasToolBarExtensibility` 接口，你可以为 Dataprep 编辑器添加自定义的菜单项和工具栏按钮。

```cpp
// 在模块启动时（如 StartupModule）扩展 Dataprep 编辑器
if (IDataprepEditorModule::IsAvailable())
{
    IDataprepEditorModule& DataprepEditorModule = IDataprepEditorModule::Get();

    // 添加菜单扩展
    TSharedPtr<FExtensibilityManager> MenuExtensibility = DataprepEditorModule.GetMenuExtensibilityManager();
    if (MenuExtensibility.IsValid())
    {
        // ... 创建并注册 FExtender
    }

    // 添加工具栏扩展
    TSharedPtr<FExtensibilityManager> ToolBarExtensibility = DataprepEditorModule.GetToolBarExtensibilityManager();
    if (ToolBarExtensibility.IsValid())
    {
        // ... 创建并注册 FExtender
    }
}
```

## Demo 示例

一个最小化的示例，展示如何在自己的编辑器模块中与 Dataprep 编辑器模块交互。

**MyEditorModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterDataprepExtensions();
    void UnregisterDataprepExtensions();
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "DataprepEditorModule.h"

void FMyEditorModule::StartupModule()
{
    RegisterDataprepExtensions();
}

void FMyEditorModule::ShutdownModule()
{
    UnregisterDataprepExtensions();
}

void FMyEditorModule::RegisterDataprepExtensions()
{
    if (IDataprepEditorModule::IsAvailable())
    {
        IDataprepEditorModule& DataprepEditorModule = IDataprepEditorModule::Get();
        // 在此处添加你的菜单或工具栏扩展逻辑
        UE_LOG(LogTemp, Log, TEXT("Dataprep Editor module is available. Ready to extend."));
    }
}

void FMyEditorModule::UnregisterDataprepExtensions()
{
    // 清理扩展
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

从 `DataprepEditor.Build.cs` 分析，本模块依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `DataprepCore` | Dataprep 的核心运行时逻辑，包括资产、操作和管道的定义。 |
| `AssetTools` | 用于注册自定义资产类型和资产编辑器。 |
| `WorkspaceMenuStructure` | 用于在编辑器工作区（如选项卡）中注册自定义面板。 |
| `GraphEditor` | 用于创建和编辑基于节点的图表（Dataprep 管道的可视化界面）。 |
| `KismetWidgets` | 提供蓝图编辑器相关的 UI 控件，可能用于图表节点。 |
| `PropertyEditor` | 用于创建和自定义属性（Details）面板。 |
| `ToolMenus` | 用于扩展编辑器菜单和工具栏。 |
| `Slate`, `SlateCore`, `EditorStyle` | UI 框架和编辑器样式。 |

## 维护状态

### 近期更新

```
- 6f23619b61a2 Moved UEdGraphSchema asset reference filtering for drag and drop operations to their various implementations...
- 36bf499a13b6 Slate Dynamic Invalidation - ExpanderArrow
- 2c158c4d0766 Change GetUsedTextures MaterialInterface to use TOptional parameters instead of Enum+bool pairs...
```

**解读**：最近的提交主要是底层引擎和框架的改进（如图表拖放逻辑、Slate UI 性能优化、材质接口重构），而非 Dataprep 插件本身的功能更新。这表明该插件处于一个相对稳定的状态，其更新主要跟随引擎核心的演进。

### 维护评价

Dataprep Editor 是一个创建于 2019 年的企业级插件，已有约 5 年历史。从最近的提交记录看，它没有频繁的功能迭代，但持续跟随引擎版本进行兼容性维护。作为 Epic Games 官方维护的企业工具，其稳定性和可靠性有保障。由于其 `EnabledByDefault` 为 `false`，它主要面向有明确数据准备需求的专业用户（如建筑、工业领域）。对于需要处理大量外部资产导入和优化的工作流，这是一个成熟且推荐使用的工具。如果超过一年没有看到针对该插件特定功能的更新，通常意味着其核心功能已经稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/dataprep-editor-in-unreal-engine/) (Unreal Engine 官方文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DataprepEditor/Tests)