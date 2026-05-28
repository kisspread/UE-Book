# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据存储功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（实验性UI功能模块） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

EditorDataStorageFeatures 是一个大型、实验性的插件集合，旨在为 Unreal Editor 构建基于 **TEDS (Editor Data Storage)** 的新一代编辑器 UI 和工作流程。TEDS 是 UE5 中引入的用于高效查询和操作海量编辑器数据（如资产、Actor、对象）的框架。

此插件的核心目标是将编辑器现有的各种功能（如场景大纲、属性编辑器、内容浏览器、修订控制等）**重构**到 TEDS 之上，以获得更好的性能、一致性和可扩展性。它不是提供给游戏运行时使用的功能，而是专门用于改造编辑器自身的 UI 和数据管理方式。

## 使用场景

- **性能优化**：你的编辑器场景包含成千上万的 Actor，使用传统场景大纲 (Outliner) 或资产浏览器会卡顿 → 启用 `TedsOutliner` 或 `TedsContentBrowser` 模块以获得基于 TEDS 的高性能替代方案。
- **统一数据查询**：你需要以灵活、高效的方式查询编辑器中的各类数据（资产、Actor、组件等） → 启用 `TedsQueryStack` 或相关模块，使用 TEDS 的统一查询接口。
- **实验新编辑器功能**：作为 UE5 开发者或技术美术，希望体验或参与 Epic 正在开发的下一代编辑器架构 → 启用此实验性插件。

## 蓝图用法

该插件主要提供 Slate 控件和 C++ 模块，蓝图层面的公开接口较少。其主要的可视化组件可在蓝图中作为 Slate Widget 使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SPropertyMenuTedsRowPicker` | 一个 Slate 控件，用于在属性编辑器中弹出一个基于 TEDS 的行选择器（类似 Actor 拾取器）。 | `SPropertyMenuTedsRowPicker` |
| `FTedsRowPickingMode` | 场景大纲 (Scene Outliner) 的一种特定模式，用于在拾取场景中元素时提供 TEDS 数据支持。 | `FTedsRowPickingMode` |

### 使用示例（蓝图描述）

由于这些是 Slate 控件，无法直接在蓝图中通过节点连线创建。它们通常在 C++ 中构造，然后作为 Slate Widget 被包含在其他 UI 元素中（如属性自定义界面）。在蓝图中，你可能会在自定义编辑器工具或扩展的上下文中通过代码引用这些控件。

## C++ 用法

### 头文件引入

```cpp
// 引入 TEDS 属性编辑器行拾取模式相关定义
#include "TedsRowPickingMode.h"
#include "Widgets/SPropertyMenuTedsRowPicker.h"

// 引入 TEDS 核心类型（通常需要）
#include "Elements/Framework/TypedElementDataStorage.h"
```

### 基本用法

1.  **创建 TEDS 行选择器菜单 (SPropertyMenuTedsRowPicker)**
    这通常在为自定义属性类型创建自定义属性编辑器时使用。来源文件: `Source/TedsPropertyEditor/Public/Widgets/SPropertyMenuTedsRowPicker.h`

    ```cpp
    // 在创建属性自定义界面的代码中
    TSharedRef<SWidget> CreateMyCustomPropertyEditor(const TSharedRef<IPropertyHandle>& PropertyHandle)
    {
        // 定义一个查询描述，用于从 TEDS 中筛选要显示的行（例如，筛选特定类型的资产）
        UE::Editor::DataStorage::FQueryDescription MyQueryFilter;
        // ... 配置查询过滤器 ...

        // 定义行选择回调
        FOnTedsRowSelected OnRowSelectedDelegate;
        OnRowSelectedDelegate.BindLambda([PropertyHandle](UE::Editor::DataStorage::RowHandle RowHandle)
        {
            // 处理用户选中的 TEDS 行，例如将其关联的值设置到属性句柄
            // PropertyHandle->SetValue(...);
        });

        // 创建并返回拾取器 Widget
        return SNew(SPropertyMenuTedsRowPicker)
            .AllowClear(true)
            .QueryFilter(MyQueryFilter)
            .OnSet(OnRowSelectedDelegate);
    }
    ```

2.  **设置场景大纲为 TEDS 行拾取模式**
    这通常在自定义编辑器模块中，创建一个用于拾取特定 TEDS 数据行的场景大纲窗口。来源文件: `Source/TedsPropertyEditor/Public/TedsRowPickingMode.h`

    ```cpp
    #include "SceneOutliner/Public/SceneOutlinerFwd.h"
    #include "TedsOutlinerModule.h" // 假设通过 TedsOutliner 模块创建大纲实例

    void OpenTedsRowPickerDialog()
    {
        // 定义当用户选择项目时的回调
        FOnSceneOutlinerItemPicked OnItemPickedDelegate;
        OnItemPickedDelegate.BindLambda([](TSharedRef<ISceneOutlinerTreeItem> Item)
        {
            // 处理从 TEDS 大纲中拾取到的项目
            // 通常可以将其转换为 FTypedElementHandle 并获取 RowHandle
        });

        // 创建参数
        UE::Editor::Outliner::FTedsOutlinerParams Params;
        // ... 配置大纲参数，如初始列、过滤器等 ...

        // 使用 TedsRowPickingMode 初始化场景大纲
        // 具体的创建方式取决于 TedsOutliner 模块提供的工厂函数
        TSharedRef<FTedsRowPickingMode> PickingMode = MakeShareable(new FTedsRowPickingMode(Params, OnItemPickedDelegate));

        // 创建并显示包含此模式的场景大纲窗口
        // ...
    }
    ```

## Demo 示例

一个最小的示例，展示如何在自定义编辑器模块中包含 TEDS 属性编辑器行拾取功能。

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
    void RegisterCustomPropertyTypeLayout();
    void UnregisterCustomPropertyTypeLayout();
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "PropertyEditorModule.h"
#include "Widgets/SPropertyMenuTedsRowPicker.h"
#include "Elements/Framework/TypedElementDataStorage.h"

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    RegisterCustomPropertyTypeLayout();
}

void FMyEditorModule::ShutdownModule()
{
    UnregisterCustomPropertyTypeLayout();
}

void FMyEditorModule::RegisterCustomPropertyTypeLayout()
{
    // 获取属性编辑器模块
    FPropertyEditorModule& PropertyModule = FModuleManager::GetModuleChecked<FPropertyEditorModule>("PropertyEditor");

    // 为某个自定义属性结构（例如 FMyTedsReference）注册自定义界面
    PropertyModule.RegisterCustomPropertyTypeLayout(
        FMyTedsReference::StaticStruct()->GetFName(),
        FOnGetPropertyTypeCustomizationInstance::CreateLambda([]()
        {
            // 这里返回一个自定义的 FPropertyTypeLayout 实例
            // 在该实例的 `CustomizeHeader` 函数中，可以创建 SPropertyMenuTedsRowPicker
            return MakeShareable(new FMyTedsReferenceCustomization);
        })
    );
}

// 在 FMyTedsReferenceCustomization::CustomizeHeader 中，创建选择器控件的示例代码：
/*
TSharedRef<SWidget> FMyTedsReferenceCustomization::CreateCustomWidget()
{
    UE::Editor::DataStorage::FQueryDescription Filter;
    // ... 配置 Filter 以筛选特定类型的 TEDS 行 ...

    return SNew(SPropertyMenuTedsRowPicker)
        .QueryFilter(Filter)
        .OnSet(FOnTedsRowSelected::CreateSP(this, &FMyTedsReferenceCustomization::OnRowSelected));
}
*/

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

## 模块依赖

要使用此插件（特别是 `TedsPropertyEditor` 模块），你的模块通常需要依赖以下 TEDS 核心模块。其他子模块（如 `TedsOutliner`, `TedsContentBrowser`）依赖关系类似。

| 模块 | 用途 |
|---|---|
| `TypedElementFramework` | TEDS 和类型化元素的核心框架 |
| `TypedElementRuntime` | 运行时类型化元素数据存储和查询 |
| `TedsOutliner` | 提供基于 TEDS 的场景大纲功能，`TedsRowPickingMode` 基于此 |
| `SceneOutliner` | 标准的场景大纲模块，`FTedsOutlinerMode` 基于此 |

**注意**：由于这是一个包含17个模块的大型插件，具体依赖关系取决于你实际使用的子模块。使用前需要在你的 `.Build.cs` 文件中添加相应模块名到 `PublicDependencyModuleNames` 或 `PrivateDependencyModuleNames`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限的 UEFN（虚幻编辑器 For Next）中启用 TEDS 场景大纲。 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从 TEDS 场景大纲中隐藏非编辑关卡实例内的未加载 Actor 行。 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复 TEDS 场景大纲中无效的跨关卡拖放操作。 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退了之前的更改 CL53940377。 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从 TEDS 场景大纲中隐藏非编辑关卡实例内的未加载 Actor 行。 |

### 维护评价

- **创建时间**：2024年7月创建，至今约2年。
- **近期活跃度**：**高度活跃**。在 2026 年 5 月仍有密集的提交，且内容集中在功能启用（如 UEFN 支持）、Bug 修复和用户体验优化上。
- **维护状态**：**活跃开发中**。这是一个由 Epic 主导的实验性大型重构项目，旨在为未来编辑器架构奠定基础。近期的提交表明核心功能（如 TEDS Outliner）正在积极开发和集成到不同的编辑器上下文（如 UEFN）中。
- **已知限制**：作为实验性插件 (`IsExperimentalVersion=true`)，其 API 和功能在版本间可能会发生不兼容的更改。`Installed: false` 表示默认不启用，需要手动打开。
- **使用推荐**：**仅推荐用于研究、实验或参与 UE5 前沿开发**。不推荐在已上线的商业项目中依赖此插件，因为其稳定性无法保证且未来可能发生破坏性变更。对于希望了解 UE5 编辑器未来发展方向的开发者，这是一个极佳的学习和研究对象。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档]() (暂无)
- [测试用例]() (暂未在提供的信息中找到明确路径)