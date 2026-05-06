# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容模板、蓝图资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件为 Unreal Engine 提供导入 USD（通用场景描述）文件格式的能力。插件的 **USDClassesEditor** 模块专注于编辑器侧对 USD 资产缓存（`UUsdAssetCache3`）的管理，包括：

- 资产缓存资源的资产定义和图标
- 在编辑器中创建/编辑资产缓存实例
- 当项目缺少默认资产缓存时，弹出对话框引导用户创建或选择
- 提供资产编辑器标签页（`FUsdAssetCacheAssetEditorToolkit`）用于查看缓存内容

> ⚠️ **实验性插件**：当前标记为 Beta 版本，API 可能随时间发生破坏性变更。

## 使用场景

- **导入 USD 文件时自动管理资产缓存**：导入流程需要将 USD 中的网格、材质等转换为 UE 资产并缓存起来，避免重复转换。该模块确保用户在编辑器中拥有合适的缓存对象。
- **手动管理缓存**：在内容浏览器中创建新的 `UsdAssetCache` 资产，并通过编辑器工具查看缓存中的资产引用情况。
- **项目设置中的缓存默认值**：通过模块提供的对话框，用户可以指定或创建项目级别的默认资产缓存。

## 蓝图用法

本模块未暴露任何蓝图可调用函数或可读写属性。USD 相关的蓝图功能主要集中在 `USDStage` 模块中（如加载/卸载舞台、获取资产等）。  
如需在蓝图中与资产缓存交互，可直接使用 `UUsdAssetCache2`（或 `UUsdAssetCache3`）对象，通过常规的资产操作节点（如 `Create Asset` 等）进行。

## C++ 用法

### 头文件引入

```cpp
#include "USDClassesEditorModule.h"
#include "USDAssetCacheFactory.h"
#include "AssetDefinition_USDAssetCache.h"
```

### 基本用法

#### 创建新的资产缓存实例（通过工厂）

```cpp
// 在内容浏览器的目标目录中创建资产
UUsdAssetCacheFactory* Factory = NewObject<UUsdAssetCacheFactory>();
UObject* NewCache = Factory->FactoryCreateNew(
    UUsdAssetCache3::StaticClass(),
    InParent,
    NAME_None,
    RF_Transactional | RF_Public,
    nullptr,
    GWarn
);
// 可进一步配置缓存设置
```

#### 显示缺失默认缓存对话框（已弃用）

```cpp
// 5.3 之前的签名
UUsdAssetCache2* Cache = IUsdClassesEditorModule::ShowMissingDefaultAssetCacheDialog();

// 5.4 签名（推荐）
UUsdAssetCache2* OutCache;
bool bAccepted;
IUsdClassesEditorModule::ShowMissingDefaultAssetCacheDialog(OutCache, bAccepted);
```

> 该对话框已在 5.5 中弃用，资产缓存会在需要时自动创建。

### 进阶用法

#### 注册自定义资产缓存编辑器

```cpp
// 在自定义模块的 StartupModule 中
if (FModuleManager::Get().IsModuleLoaded("AssetTools"))
{
    IAssetTools& AssetTools = FModuleManager::GetModuleChecked<FAssetToolsModule>("AssetTools").Get();
    AssetTools.RegisterAssetTypeActions(MakeShared<FAssetTypeActions_UsdAssetCache>());
}
```

#### 使用资产定义类（`UAssetDefinition_UsdAssetCache`）

该类定义了资产在内容浏览器中的显示名称、颜色、排序等。若需自定义资产行为，可继承该类并重写相关虚函数。

## Demo 示例

以下是一个最小化的编辑器模块，演示如何创建资产缓存并注册资产类型操作：

**MyUsdModule.h**

```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FMyUsdModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyUsdModule.cpp**

```cpp
#include "MyUsdModule.h"
#include "AssetToolsModule.h"
#include "AssetTypeActions_Base.h"
#include "USDAssetCacheFactory.h"
#include "USDClassesEditorModule.h"

class FAssetTypeActions_UsdCache : public FAssetTypeActions_Base
{
public:
    virtual FText GetName() const override { return NSLOCTEXT("AssetTypeActions", "UsdCache", "USD Asset Cache"); }
    virtual FColor GetTypeColor() const override { return FColor::Emerald; }
    virtual UClass* GetSupportedClass() const override { return UUsdAssetCache3::StaticClass(); }
    virtual uint32 GetCategories() override { return EAssetTypeCategories::Misc; }
    virtual bool HasActions(const TArray<UObject*>& InObjects) const override { return false; }
};

void FMyUsdModule::StartupModule()
{
    // 注册资产类型操作
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
    AssetTools.RegisterAssetTypeActions(MakeShareable(new FAssetTypeActions_UsdCache));
}

void FMyUsdModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded("AssetTools"))
    {
        IAssetTools& AssetTools = FModuleManager::GetModuleChecked<FAssetToolsModule>("AssetTools").Get();
        AssetTools.UnregisterAssetTypeActions(MakeShareable(new FAssetTypeActions_UsdCache));
    }
}

IMPLEMENT_MODULE(FMyUsdModule, MyUsdModule);
```

## 模块依赖

由于未提供 `USDClassesEditor.Build.cs` 全文，以下列表根据常见 USD 模块依赖整理：

| 模块 | 用途 |
|---|---|
| `USDStage` | USD 舞台核心功能（加载、解析、导出） |
| `USDSchemas` | 渲染模式（Schema）处理 |
| `USDClasses` | 资产缓存、资产工厂等基础类 |
| `Slate` | 编辑器 UI（对话框、标签页） |
| `UnrealEd` | 编辑器基础功能（Factories、AssetTools） |

> **注意**：上述依赖并不完整，实际编译可能需要根据 Build.cs 调整。建议在 `.Build.cs` 中添加：
> ```csharp
> PublicDependencyModuleNames.AddRange(new string[] { "USDStage", "USDSchemas", "USDClasses", "UnrealEd" });
> ```

## 维护状态

### 近期更新

- 2025-10-22 — USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 — USD: Disabled UE allocator in USD for Windows. (回退尝试)
- 2025-10-03 — USD: Use the default collision profile for generated static meshes.
- 2025-10-01 — Anim In Engine: Fix broken linked anim sequences.

### 维护评价

| 维度 | 评估 |
|---|---|
| 创建时间 | 2025-10-01（模块初次提交） |
| 最近更新 | 2025-10-22（约 4 周前） |
| 更新内容 | 修复 Windows 平台内存分配、碰撞配置、动画序列 |
| 活跃度 | 中等活跃，每月有实质性功能/修复提交 |
| 稳定性 | 标记为 Beta，API 仍在变动（如缓存对话框弃用） |
| 推荐使用 | ✅ 推荐，但留意 API 变更日志 |

> ⚠️ **警告**：该插件仍处于 Beta 阶段，部分 API 已弃用（如对话框），建议始终使用最新签名。如果项目需长期稳定，可考虑锁定特定 UE 版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter)
- [USD 官方文档](https://graphics.pixar.com/usd/release/index.html)（外部）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter/Source/USDTests)