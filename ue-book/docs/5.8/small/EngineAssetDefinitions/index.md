# Engine Asset Definitions

> （Description 字段为空）

| 属性 | 值 |
|---|---|
| 中文名 | 引擎资产定义 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EngineAssetDefinitions` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-11-10 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EngineAssetDefinitions) | |

## 用途

EngineAssetDefinitions 是 UE5 引擎内置资产类型的定义集合，是 **AssetDefinition 框架的落地实现**。

该插件解决的核心问题：旧的 `IAssetTypeActions` 系统将资产的显示信息、右键菜单、打开方式、差异对比等所有功能塞进一个类里，导致每次打开上下文菜单都必须加载所有相关资产类。AssetDefinition 框架通过 UObject-based 设计，允许在不加载资产的情况下获取大部分元信息（显示名称、颜色、分类等）。

本插件为引擎自带的数十种资产类型（蓝图、静态网格、骨骼网格、材质、数据表、世界关卡等）各提供一个 `UAssetDefinition` 子类，定义它们在编辑器中的：
- **显示名称和颜色**（内容浏览器中的视觉表现）
- **资产分类**（右键创建菜单的归属）
- **打开行为**（双击资产时打开哪个编辑器）
- **差异对比/合并**（蓝图 Diff、材质 Diff 等）
- **缩略图覆盖**（如骨骼网格的蒙皮状态指示）
- **导入支持**（是否支持导入操作）

**简单来说**：你在内容浏览器中看到的每种资产的名称、颜色、图标、右键菜单、双击行为，都由这个插件中的对应 AssetDefinition 类控制。

## 使用场景

- **查看/理解引擎资产类型行为**：想知道为什么双击 `.uasset` 会打开某个编辑器？查看对应的 AssetDefinition 类
- **开发自定义资产类型插件**：参考本插件的实现模式，为自定义资产创建 AssetDefinition
- **自定义引擎资产行为**：通过创建子类或注册新的 AssetDefinition 来覆盖引擎资产的默认行为
- **编辑器工具开发**：需要查询资产的显示名称、颜色、分类等元信息时使用

## 蓝图用法

本插件不提供 BlueprintCallable 节点。它是一个纯编辑器框架，所有 API 均为 C++ 虚函数覆盖模式。

## C++ 用法

### 头文件引入

```cpp
#include "AssetDefinitionDefault.h"
```

核心基类 `UAssetDefinitionDefault` 位于独立的 AssetDefinition 模块中，本插件提供的是具体资产类型的定义实现。

### 基本用法：创建自定义资产的 AssetDefinition

参考本插件中最简单的实现模式（如 `AssetDefinition_Redirector`）：

```cpp
// MyAssetDefinition.h
#pragma once

#include "AssetDefinitionDefault.h"
#include "MyAssetDefinition.generated.h"

UCLASS(MinimalAPI)
class UAssetDefinition_MyAsset : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    // 资产在编辑器中显示的名称
    virtual FText GetAssetDisplayName() const override
    {
        return NSLOCTEXT("AssetDefinition", "MyAsset", "My Custom Asset");
    }

    // 内容浏览器中的图标颜色
    virtual FLinearColor GetAssetColor() const override
    {
        return FLinearColor(FColor(255, 128, 0));
    }

    // 关联的 UObject 类型
    virtual TSoftClassPtr<UObject> GetAssetClass() const override
    {
        return UMyAsset::StaticClass();
    }

    // 在"创建资产"菜单中的分类
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override
    {
        static const auto Categories = { EAssetCategoryPaths::Basic };
        return Categories;
    }

    // 双击资产时的打开行为
    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override;
};
```

### 进阶用法：支持差异对比和合并

参考 `AssetDefinition_Blueprint` 和 `AssetDefinition_DataAsset` 的实现：

```cpp
// 支持 Diff 和 Merge
virtual bool CanMerge() const override { return true; }

virtual EAssetCommandResult PerformAssetDiff(const FAssetDiffArgs& DiffArgs) const override
{
    // 自定义差异对比逻辑
    return EAssetCommandResult::Unhandled;
}

virtual EAssetCommandResult Merge(const FAssetManualMergeArgs& MergeArgs) const override
{
    // 自定义手动合并逻辑
    return EAssetCommandResult::Unhandled;
}
```

### 进阶用法：缩略图覆盖和状态信息

参考 `AssetDefinition_SkeletalMesh` 的缩略图覆盖实现：

```cpp
// 添加缩略图覆盖层（如状态图标）
virtual TSharedPtr<class SWidget> GetThumbnailOverlay(const FAssetData& AssetData) const override;

// 提供资产状态信息
virtual void GetAssetStatusInfo(
    const TSharedPtr<IAssetStatusInfoProvider>& InAssetStatusInfoProvider,
    TArray<FAssetDisplayInfo>& OutStatusInfo) const override;
```

### 进阶用法：类类型资产（ClassTypeBase 模式）

用于 C++ 类和蓝图类等"类类型"资产，通过 `IClassTypeActions` 接口提供额外功能：

```cpp
// 参考 AssetDefinition_ClassTypeBase.h
virtual TWeakPtr<IClassTypeActions> GetClassTypeActions(const FAssetData& AssetData) const;
```

## 模块分类总览

本插件包含一个 UE 模块 `EngineAssetDefinitions`（Editor 类型），内部按功能域组织为以下子文件夹，定义了引擎全部内置资产类型：

### 脚本/蓝图类（Script/）

| 资产类型类 | 资产类型 | 显示名称 |
|---|---|---|
| `UAssetDefinition_Blueprint` | `UBlueprint` | Blueprint Class |
| `UAssetDefinition_AnimBlueprint` | `UAnimBlueprint` | Animation Blueprint |
| `UAssetDefinition_BlueprintGeneratedClass` | `UBlueprintGeneratedClass` | Compiled Blueprint Class |
| `UAssetDefinition_Class` | `UClass` | C++ Class |
| `UAssetDefinition_ClassTypeBase` | — | 抽象基类（类类型资产） |

### 动画类（Animation/）

| 资产类型类 | 资产类型 | 显示名称 |
|---|---|---|
| `UAssetDefinition_SkeletalMesh` | `USkeletalMesh` | Skeletal Mesh |
| `UAssetDefinition_AnimBank` | `UAnimBank` | Animation Bank |
| `UAssetDefinition_AnimBankData` | `UAnimBankData` | Animation Bank Data |

### 材质类（Material/）

| 资产类型类 | 资产类型 | 显示名称 |
|---|---|---|
| `UAssetDefinition_MaterialInterface` | `UMaterialInterface` | Material Interface |
| `UAssetDefinition_MaterialInstanceConstant` | `UMaterialInstanceConstant` | Material Instance |
| `UAssetDefinition_MaterialFunction` | `UMaterialFunction` | Material Function |
| `UAssetDefinition_MaterialFunctionInstance` | `UMaterialFunctionInstance` | Material Function Instance |
| `UAssetDefinition_MaterialFunctionMaterialLayer` | `UMaterialFunctionMaterialLayer` | Material Layer |
| `UAssetDefinition_MaterialFunctionLayerBlend` | `UMaterialFunctionMaterialLayerBlend` | Material Layer Blend |
| `UAssetDefinition_MaterialFunctionLayerInstance` | `UMaterialFunctionMaterialLayerInstance` | Material Layer Instance |
| `UAssetDefinition_MaterialFunctionLayerBlendInstance` | `UMaterialFunctionMaterialLayerBlendInstance` | Material Layer Blend Instance |

### 数据表类（Table/）

| 资产类型类 | 资产类型 | 显示名称 |
|---|---|---|
| `UAssetDefinition_DataTable` | `UDataTable` | Data Table |
| `UAssetDefinition_CurveTable` | `UCurveTable` | Curve Table |

### 通用资产（根目录）

| 资产类型类 | 资产类型 | 显示名称 |
|---|---|---|
| `UAssetDefinition_World` | `UWorld` | Level |
| `UAssetDefinition_StaticMesh` | `UStaticMesh` | Static Mesh |
| `UAssetDefinition_DataAsset` | `UDataAsset` | Data Asset |
| `UAssetDefinition_Curve` | `UCurveBase` | Curve |
| `UAssetDefinition_Redirector` | `UObjectRedirector` | Redirector |
| `UAssetDefinition_UserDefinedStruct` | `UUserDefinedStruct` | Structure |
| `UAssetDefinition_UserDefinedEnum` | `UUserDefinedEnum` | Enumeration |
| `UAssetDefinition_PhysicsAsset` | `UPhysicsAsset` | Physics Asset |
| `UAssetDefinition_PhysicalMaterialMask` | `UPhysicalMaterialMask` | Physical Material Mask |
| `UAssetDefinition_ForceFeedbackEffect` | `UForceFeedbackEffect` | Force Feedback Effect |
| `UAssetDefinition_FontFace` | `UFontFace` | Font Face |
| `UAssetDefinition_DataLayer` | `UDataLayerAsset` | Data Layer |
| `UAssetDefinition_DataLayerInstance` | `UDataLayerInstance` | Data Layer Instance |
| `UAssetDefinition_ObjectLibrary` | `UObjectLibrary` | Object Library |
| `UAssetDefinition_TouchInterface` | `UTouchInterface` | Touch Interface Setup |
| `UAssetDefinition_SparseVolumeTexture` | `USparseVolumeTexture` | Sparse Volume Texture 系列 |
| `UDEPRECATED_AssetDefinition_LightWeightInstance` | — | Light Weight Instance（已废弃） |

## Demo 示例

以下是一个完整的自定义资产 AssetDefinition 示例，展示如何为自定义资产类型定义编辑器行为：

```cpp
// MyGameAssetDefinition.h
#pragma once

#include "AssetDefinitionDefault.h"
#include "MyGameAsset.h"
#include "MyGameAssetDefinition.generated.h"

UCLASS(MinimalAPI)
class UAssetDefinition_MyGameAsset : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    virtual FText GetAssetDisplayName() const override
    {
        return NSLOCTEXT("MyGame", "MyGameAsset", "Game Config Asset");
    }

    virtual FText GetAssetDisplayName(const FAssetData& AssetData) const override
    {
        // 可根据具体资产数据返回更详细的名称
        return GetAssetDisplayName();
    }

    virtual FLinearColor GetAssetColor() const override
    {
        return FLinearColor(FColor(100, 200, 255));
    }

    virtual TSoftClassPtr<UObject> GetAssetClass() const override
    {
        return UMyGameAsset::StaticClass();
    }

    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override
    {
        static const auto Categories = { EAssetCategoryPaths::Basic };
        return Categories;
    }

    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override
    {
        // 双击时在属性编辑器中打开
        for (UMyGameAsset* Asset : OpenArgs.LoadObjects<UMyGameAsset>())
        {
            FPropertyEditorModule& PropertyModule =
                FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
            // 自定义打开逻辑
        }
        return EAssetCommandResult::Handled;
    }

    virtual bool CanImport() const override { return false; }

    virtual FAssetSupportResponse CanLocalize(const FAssetData& InAsset) const override
    {
        return FAssetSupportResponse::NotSupported();
    }
};
```

```cpp
// MyGameAssetDefinition.cpp
#include "MyGameAssetDefinition.h"
// 如有需要可在此实现更复杂的逻辑
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetDefinition` | 提供 `UAssetDefinitionDefault` 等基类框架 |
| `UnrestrictedAssetEditor` | 资产编辑器的无限制打开支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `c9ef5202` | Fix early check for derived anim blueprints causing crashes when parent class skeletons were deleted | 修复动画蓝图父类骨骼被删除时的崩溃问题 |
| 2026-05-13 | `f933819f` | EditorUsability : Textures | 编辑器易用性改进：纹理相关 |
| 2026-05-12 | `4c024ae7` | [Subsurface Profile] Add back the default toolbar for quick save and browse. | 恢复次表面配置的默认工具栏快速保存和浏览功能 |
| 2026-04-24 | `12940ee6` | EditorUsability : AssetDefinitions | 编辑器易用性改进：资产定义相关 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 内容浏览器新增"添加菜单数据"菜单 |

### 维护评价

**活跃维护**。本插件创建于 2022 年 11 月，是 Epic 替代旧 `IAssetTypeActions` 系统的长期工程。近期（2026 年 4-5 月）仍有频繁的功能更新和 Bug 修复，说明该系统正在持续完善中。

**注意事项**：
- 本插件默认启用（`EnabledByDefault: true`），所有 UE5 项目自动加载
- 已废弃的资产类型（如 `LightWeightInstance`）标注了 `UCLASS(Deprecated)`
- 作为编辑器框架插件，不包含任何运行时功能或内容资产
- 如果你需要为自定义资产定义编辑器行为，应直接创建 `UAssetDefinitionDefault` 子类，而非依赖本插件

**推荐使用**：✅ 是（所有 UE5 项目默认包含，了解其结构有助于自定义资产开发）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EngineAssetDefinitions)
- [创建时的提交说明](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Editor/EngineAssetDefinitions/EngineAssetDefinitions.uplugin)（首次提交 `fd6f4a2` 详细说明了设计动机）