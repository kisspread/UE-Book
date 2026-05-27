# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD资产缓存、场景管理蓝图资产等） |
| 模块 | `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageImporter` (Runtime), `USDExporter` (Runtime), `USDClassesEditor` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `GeometryCacheUSD` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

本插件为 Unreal Engine 提供了完整的 USD (Universal Scene Description) 工作流支持。其核心功能是将 USD 文件（如 `.usd`、`.usda`、`.usdc`）导入到引擎中，转换为 Unreal 的资产和场景表示。除了基础的静态网格、骨骼网格和材质导入外，它还包含一个完整的“USD Stage”概念，允许用户在编辑器内可视化地管理、预览和编辑 USD 场景图，并支持将 Unreal 内容导出回 USD 格式。该插件旨在解决复杂资产管线中，Unreal Engine 与 Maya、Houdini、Nuke 等使用 USD 的 DCC 工具之间的数据交换与协同问题。

## 使用场景

- 你的美术团队使用 Maya 或 Houdini 创建了复杂的 USD 场景，需要将其完整地导入到 Unreal 中进行关卡设计或实时渲染预览。
- 你需要在一个 Unreal 项目中同时管理多个 USD 文件（代表不同的资产或场景变体），并进行交互式的图层、变体和有效载荷切换。
- 你希望将 Unreal 中创建的资产或场景布局（例如用于虚拟制片）导出为 USD 格式，供其他管线环节使用。
- 你需要将 USD 动画曲线（如骨骼动画、变形目标）导入并用于驱动 Unreal 中的 Skeletal Mesh 或 Geometry Cache。

## 蓝图用法

USDImporter 插件的主要功能是通过编辑器 UI（如 USD Stage 面板）和资产导入/导出流程来操作。其 `USDClassesEditor` 和 `USDStageEditor` 等模块提供的核心类主要为编辑器扩展服务，未暴露通用的 `BlueprintCallable` 函数供游戏运行时蓝图使用。交互主要在编辑器内完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *无相关蓝图节点* | 本插件模块主要提供编辑器工具和资产类型，不直接提供运行时蓝图函数。 | - |

### 使用示例（蓝图描述）

在蓝图中通常不直接与 USD 文件交互。正确的使用流程是在编辑器中：
1.  通过 `File -> Import` 或 Content Browser 右键菜单导入 USD 文件。
2.  使用 `USD Stage` 编辑器面板（`Window -> USD Stage`）来管理导入的 USD 阶段。
3.  在 `USD Stage` 面板中调整图层、变体、有效载荷，并通过“Stage Actor”在场景中预览。
4.  导出时，通过 Content Browser 右键菜单或工具栏中的“USD Exporter”工具进行操作。

## C++ 用法

### 头文件引入

```cpp
#include "USDClassesEditorModule.h"
#include "USDAssetCacheAssetEditorToolkit.h"
#include "AssetDefinition_USDAssetCache.h"
#include "USDAssetCacheFactory.h"
```

### 基本用法

`USDClassesEditor` 模块主要为 `UUsdAssetCache3` 资产提供编辑器集成。你可以通过自定义资产定义来控制其在编辑器中的显示和行为。

**来源文件**: `Source/USDClassesEditor/Private/AssetDefinition_USDAssetCache.h`
```cpp
// 自定义 USD 资产缓存资产的显示名称、颜色和分类
UCLASS()
class UAssetDefinition_UsdAssetCache : public UAssetDefinitionDefault
{
    GENERATED_BODY()
public:
    virtual FText GetAssetDisplayName() const override;
    virtual FLinearColor GetAssetColor() const override;
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    virtual bool CanImport() const override;
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
};
```

### 进阶用法

你可以为 `UUsdAssetCache3` 创建一个自定义的资产编辑器（Toolkit），当用户双击该资产时弹出一个带属性面板的编辑器窗口。

**来源文件**: `Source/USDClassesEditor/Private/USDAssetCacheAssetEditorToolkit.h`
```cpp
// 自定义 USD 资产缓存的编辑器窗口
class FUsdAssetCacheAssetEditorToolkit : public FAssetEditorToolkit, public FGCObject
{
public:
    void Initialize(const EToolkitMode::Type Mode, const TSharedPtr<IToolkitHost>& InitToolkitHost, UUsdAssetCache3* InAssetCache);

    // ... 重写 FAssetEditorToolkit 的函数以定义窗口名称、标签页等
    virtual void RegisterTabSpawners(const TSharedRef<FTabManager>& InTabManager) override;
    // ...
private:
    TSharedRef<SDockTab> SpawnTab(const FSpawnTabArgs& Args);
    TObjectPtr<UUsdAssetCache3> AssetCache;
    TSharedPtr<class IDetailsView> AssetCacheEditorWidget;
};
```

## Demo 示例

以下是一个最小化的示例，展示如何创建并注册一个用于 `UUsdAssetCache3` 的自定义资产编辑器。

**USDAssetCacheEditorApp.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/StrongObjectPtr.h"

class UUsdAssetCache3;
class FUsdAssetCacheAssetEditorToolkit;

class FUSDAssetCacheEditorApp
{
public:
    /** 打开一个已有的 USD 资产缓存进行编辑 */
    static void OpenEditor(UUsdAssetCache3* AssetToEdit);
    
    /** 创建一个新的 USD 资产缓存并打开编辑器 */
    static void CreateAndOpenEditor();

private:
    static TSharedPtr<FUsdAssetCacheAssetEditorToolkit> EditorToolkit;
};
```

**USDAssetCacheEditorApp.cpp**
```cpp
#include "USDAssetCacheEditorApp.h"
#include "USDAssetCacheAssetEditorToolkit.h"
#include "USDAssetCache3.h" // 假设存在此类

TSharedPtr<FUsdAssetCacheAssetEditorToolkit> FUSDAssetCacheEditorApp::EditorToolkit = nullptr;

void FUSDAssetCacheEditorApp::OpenEditor(UUsdAssetCache3* AssetToEdit)
{
    if (!AssetToEdit)
    {
        return;
    }

    if (!EditorToolkit.IsValid())
    {
        EditorToolkit = MakeShared<FUsdAssetCacheAssetEditorToolkit>();
    }
    // 初始化并打开编辑器
    EditorToolkit->Initialize(EToolkitMode::Standalone, TSharedPtr<IToolkitHost>(), AssetToEdit);
}

void FUSDAssetCacheEditorApp::CreateAndOpenEditor()
{
    // 通过工厂创建新资产，然后打开编辑器
    UUsdAssetCacheFactory* Factory = NewObject<UUsdAssetCacheFactory>();
    UObject* NewAsset = Factory->FactoryCreateNew(UUsdAssetCache3::StaticClass(), GetTransientPackage(), NAME_None, RF_Transient, nullptr, GWarn);
    if (UUsdAssetCache3* NewCache = Cast<UUsdAssetCache3>(NewAsset))
    {
        OpenEditor(NewCache);
    }
}
```

## 模块依赖

`USDClassesEditor` 模块是 USDImporter 插件内部的编辑器支持模块，其对外部模块的依赖已在插件的构建系统中处理。对于使用此插件的项目或模块，无需额外依赖 `USDClassesEditor`。要使用整个插件的功能，通常只需在 `.uproject` 文件或目标 `.Build.cs` 中启用 `USDImporter` 插件即可。本模块具体依赖（通常为插件内部模块）需查阅其 `USDClassesEditor.Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量被截断为浮点数而产生的编译警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 新增支持分配独立于蓝图的 Control Rig（控制绑定）。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD varies. | USD: 修复了 SDK 更新到 26.03 后，当LOD变化时导致 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化字符串中，32位与64位参数说明符不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 现在烘焙所有曝光动画轨迹的帧。 |

### 维护评价

该插件自2018年创建以来持续活跃维护。从近期提交历史看（最新提交在2026年5月），开发团队仍在积极添加新功能（如支持独立 Control Rig）和修复问题（SDK兼容性、编译警告）。提交信息专业且具体，表明维护质量较高。尽管`.uplugin`中标记为 `IsBetaVersion=true`，但考虑到其成熟度和持续的活跃开发，可以认为它是一个**稳定且活跃维护**的实验性/测试版插件。

**推荐使用**：对于任何需要在 Unreal Engine 项目中集成 USD 工作流（特别是来自 Maya、Houdini 等DCC工具）的团队，强烈推荐启用此插件。虽然标记为实验性，但其功能完整且有持续支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)