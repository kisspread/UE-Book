# Engine Asset Definitions

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 资产定义核心 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EngineAssetDefinitions` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-11-10 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EngineAssetDefinitions) | |

## 用途

Engine Asset Definitions 插件是虚幻引擎资产编辑系统的基石。它的核心功能是建立一个统一的、面向对象的框架，用于定义**各种资产类型在编辑器中的行为**，以取代旧的 `IAssetTypeActions` 接口。

它解决了旧系统（`IAssetTypeActions`）的几个关键问题：
1.  **功能耦合过重**：旧接口将显示、右键菜单、资产操作等功能杂糅在一起。
2.  **不必要的资产加载**：在打开资产右键上下文菜单时，可能被迫加载所有选中的资产，导致性能问题。
3.  **扩展性差**：旧接口难以在不破坏继承链的情况下进行修改和扩展。

通过 `UAssetDefinition` 基类及其众多子类（如 `UAssetDefinition_Blueprint`, `UAssetDefinition_StaticMesh`），该插件为每一种引擎原生资产类型（蓝图、静态网格体、材质、数据表等）提供了标准化的定义，包括显示名称、颜色、缩略图、分类以及差异比较、合并、打开等高级编辑操作。它是编辑器中资产浏览器、右键菜单、资产编辑器等所有与资产交互功能的底层驱动程序。

## 使用场景

- **你在开发一个自定义资产类型**：需要定义它在内容浏览器中的图标颜色、右键菜单选项和双击行为。你需要继承 `UAssetDefinitionDefault` 并创建你自己的 `UAssetDefinition_MyCustomAsset`。
- **你需要为现有引擎资产添加新的编辑操作**：例如，为所有数据资产添加一个“批量验证”选项，你可以扩展对应的 `UAssetDefinition` 子类。
- **你遇到了资产编辑器或内容浏览器的显示/行为问题**：修改或调试对应资产类型的 `UAssetDefinition` 子类是解决问题的标准路径。
- **你想要理解或定制蓝图、材质、网格体等核心资产的编辑器行为**：这个插件的源码是权威参考。

## 蓝图用法

此插件主要是 C++ 框架层，为引擎和项目插件提供基础，不直接暴露蓝图节点。其价值在于为各种资产类型的 `UAssetDefinition` 子类定义了可覆盖的虚函数（如 `OpenAssets`, `PerformAssetDiff`），这些函数最终决定了资产在编辑器中的交互行为。蓝图资产本身（`UAssetDefinition_Blueprint`）的定义也包含在此插件中。

## C++ 用法

### 头文件引入

```cpp
// 包含资产定义基类
#include "AssetDefinitionDefault.h"

// 如果需要处理特定资产类型，包含其对应的定义头文件，例如：
// #include "AssetDefinition_Blueprint.h"
```

### 基本用法

创建一个自定义资产类型的定义。这通常是创建新资产类型编辑器支持的第一步。

```cpp
// MyAssetDefinition.h
#pragma once

#include "AssetDefinitionDefault.h"
#include "MyAssetDefinition.generated.h"

UCLASS()
class UMyAssetDefinition : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    // 定义资产在内容浏览器中的显示名称
    virtual FText GetAssetDisplayName() const override
    {
        return NSLOCTEXT("MyModule", "MyAssetType", "My Custom Asset");
    }

    // 定义资产缩略图/图标的颜色
    virtual FLinearColor GetAssetColor() const override
    {
        return FLinearColor(FColor(255, 128, 0)); // 橙色
    }

    // 关联资产类，告诉编辑器这个定义对应哪个 C++ 类
    virtual TSoftClassPtr<UObject> GetAssetClass() const override
    {
        return UMyAsset::StaticClass();
    }

    // 定义资产在“新建资产”菜单中的分类路径
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override
    {
        static const auto Categories = { EAssetCategoryPaths::Misc };
        return Categories;
    }

    // （可选）覆盖双击或回车键打开资产时的行为
    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override
    {
        // 自定义打开逻辑，例如打开一个自定义编辑器
        // return OpenCustomEditor(OpenArgs);
        return EAssetCommandResult::Unhandled; // 使用默认行为
    }
};
```
*来源: 多个公开头文件的综合模式*

### 进阶用法

覆盖特定资产类型的差异比较 (`PerformAssetDiff`) 逻辑，以支持自定义的资产合并流程。

```cpp
// 在 MyAssetDefinition.h 或.cpp中
virtual EAssetCommandResult PerformAssetDiff(const FAssetDiffArgs& DiffArgs) const override
{
    // 获取要比较的资产对象
    UMyAsset* OldAsset = Cast<UMyAsset>(DiffArgs.OldAsset);
    UMyAsset* NewAsset = Cast<UMyAsset>(DiffArgs.NewAsset);

    if (OldAsset && NewAsset)
    {
        // 执行自定义差异计算和展示逻辑
        ShowMyCustomDiff(OldAsset, NewAsset);
        return EAssetCommandResult::Handled;
    }

    return EAssetCommandResult::Unhandled;
}

virtual bool CanMerge() const override { return true; }

virtual EAssetCommandResult Merge(const FAssetManualMergeArgs& MergeArgs) const override
{
    // 实现自定义的手动合并逻辑
    // ...
    return EAssetCommandResult::Handled;
}
```
*来源: `AssetDefinition_DataAsset.h`, `AssetDefinition_Curve.h` 等*

## Demo 示例

一个定义了简单数据资产编辑器行为的 `UAssetDefinition` 最小示例。

```cpp
// SimpleDataAssetDefinition.h
#pragma once

#include "AssetDefinitionDefault.h"
#include "SimpleDataAssetDefinition.generated.h"

class USimpleDataAsset; // 前置声明你的自定义资产类

UCLASS()
class USimpleDataAssetDefinition : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    virtual FText GetAssetDisplayName() const override
    {
        return NSLOCTEXT("MyGame", "SimpleDataAsset", "Simple Data Asset");
    }

    virtual FLinearColor GetAssetColor() const override
    {
        return FLinearColor(FColor(150, 150, 255)); // 淡蓝色
    }

    virtual TSoftClassPtr<UObject> GetAssetClass() const override;

    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override
    {
        static const auto Categories = { EAssetCategoryPaths::Data };
        return Categories;
    }

    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override;
    virtual EAssetCommandResult PerformAssetDiff(const FAssetDiffArgs& DiffArgs) const override;
};
```

```cpp
// SimpleDataAssetDefinition.cpp
#include "SimpleDataAssetDefinition.h"
#include "SimpleDataAsset.h"
#include "SimpleDataAssetEditorModule.h"

TSoftClassPtr<UObject> USimpleDataAssetDefinition::GetAssetClass() const
{
    return USimpleDataAsset::StaticClass();
}

EAssetCommandResult USimpleDataAssetDefinition::OpenAssets(const FAssetOpenArgs& OpenArgs) const
{
    for (USimpleDataAsset* Asset : OpenArgs.LoadObjects<USimpleDataAsset>())
    {
        if (Asset)
        {
            // 调用你的自定义编辑器模块来打开资产
            FSimpleDataAssetEditorModule::Get().CreateEditor(EToolkitMode::Standalone, {}, Asset);
        }
    }
    return EAssetCommandResult::Handled;
}

EAssetCommandResult USimpleDataAssetDefinition::PerformAssetDiff(const FAssetDiffArgs& DiffArgs) const
{
    // 这里可以调用自定义的Diff工具，或使用引擎默认的Diff窗口
    // 例如：UEditorEngine::EditorAddWindow(...);
    return EAssetCommandResult::Unhandled;
}
```

## 模块依赖

该插件的 `Build.cs` 文件表明，它的依赖大多是标准编辑器模块。

| 模块 | 用途 |
|---|---|
| `AssetDefinition` | 提供 `UAssetDefinition` 基类框架 |
| 无特殊依赖（仅标准 Core/Engine/Slate/EditorStyle/PropertyEditor 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `c9ef5202` | Fix early check for derived anim blueprints causing crashes when parent class skeletons were deleted | 修复了当父类骨骼被删除时，对派生动画蓝图的早期检查导致的崩溃问题 |
| 2026-05-13 | `f933819f` | EditorUsability : Textures | 编辑器易用性改进：涉及纹理资产 |
| 2026-05-12 | `4c024ae7` | [Subsurface Profile] Add back the default toolbar for quick save and browse. | 为次表面配置文件资产重新添加了默认工具栏，支持快速保存和浏览 |
| 2026-04-24 | `12940ee6` | EditorUsability : AssetDefinitions | 编辑器易用性改进：针对资产定义系统的优化 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 为内容浏览器新增了“添加菜单”的数据菜单 |

### 维护评价

**活跃维护**。该插件创建于2022年底，属于较新的核心编辑器组件。从Git历史看，**最近6个月内有多次实质性更新**（2026年4月、5月），包括修复关键崩溃、改进编辑器易用性（如工具栏、新增菜单项），表明它正处于活跃开发和迭代中。作为引擎资产编辑系统的新基石，其稳定性和功能完善度对编辑器体验至关重要，Epic持续投入维护。可以放心依赖和使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EngineAssetDefinitions)
- [官方文档]()（暂无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Editor/AssetDefinitionTests)