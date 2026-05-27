# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、资产缓存等） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USDImporter 是 Unreal Engine 的 Universal Scene Description (USD) 全流程支持插件，远超"导入"二字的含义。它提供了一套完整的 USD 生态集成方案，覆盖以下核心能力：

- **USD 资产导入**：将 `.usd`、`.usda`、`.usdc` 文件导入 UE，包括几何体、材质、动画、相机、灯光等
- **USD Stage 管理**：在编辑器中维护一个活动的 USD Stage，支持实时编辑 USD Prim 属性并回写到 USD 文件
- **USD 资产导出**：将 UE 内容导出为 USD 格式
- **GeometryCache USD 支持**：通过 USD 实现几何缓存的读写
- **资产缓存系统**：提供 `UUsdAssetCache3` 管理 USD 导入过程中生成的 UE 资产，避免重复生成

该插件在影视、建筑可视化、数字孪生等需要与 DCC 工具（Maya、Houdini、Blender）协作的场景中至关重要。

**注意**：此插件默认未启用且标记为实验性（Beta），需要在插件管理器中手动启用。它依赖 Epic 维护的 USD SDK，构建时需要额外配置。

## 使用场景

- 你在做建筑可视化，需要从 Revit/SketchUp 通过 USD 管线导入场景 → 用 USDImporter
- 你在做虚拟制片，需要实时从 USD Stage 拉取资产更新 → 用 USD Stage 功能
- 你需要将 UE 关卡导出为 USD 供 VFX 流水线使用 → 用 USDExporter 模块
- 你需要将 USD 中的骨骼动画导入并驱动 UE 骨骼网格体 → 用 USDImporter 的动画导入功能
- 你需要管理 USD 导入过程中大量生成的临时 UE 资产 → 用 USDAssetCache3

## 蓝图用法

由于此插件大量功能集中在编辑器工具和 C++ API 层面，蓝图直接可用的节点较少。核心的蓝图/编辑器交互通过 USD Stage Actor 和资产编辑器完成。

### 核心节点

USDImporter 的主要交互方式不是蓝图节点，而是通过以下编辑器资产和组件：

| 交互方式 | 说明 | 所在类 |
|---|---|---|
| USD Stage Actor | 在关卡中放置 USD Stage Actor 来加载和管理 USD 场景 | `AUsdStageActor` |
| USD Asset Cache | 资产缓存资产，管理 USD 导入生成的 UE 资产映射 | `UUsdAssetCache3` |
| 资产编辑器 | 双击 USDAssetCache 资产打开属性编辑器 | `FUsdAssetCacheAssetEditorToolkit` |
| USD Stage 编辑器 | 专用的 USD Stage 编辑器面板 | `USDStageEditor` 模块 |

### 使用示例

1. **启用插件**：编辑 → 插件 → 搜索 "USD Importer" → 启用 → 重启编辑器
2. **导入 USD 文件**：内容浏览器右键 → 导入 → 选择 `.usd` / `.usda` / `.usdc` 文件
3. **使用 USD Stage**：放置 → USD Stage Actor → 在细节面板中指定 USD 文件路径 → 场景自动加载
4. **编辑 USD 属性**：通过 USD Stage 编辑器面板查看和修改 Prim 属性

## C++ 用法

### 头文件引入

```cpp
// USD 核心类
#include "USDAssetCache3.h"
#include "USDClassesEditorModule.h"

// USD Stage 相关
#include "UsdStageActor.h"

// USD Schema
#include "USDSchemasModule.h"
```

### 基本用法 - 资产缓存系统

资产缓存 (`UUsdAssetCache3`) 是管理 USD 导入资产的核心组件，用于跟踪 USD Prim 与生成的 UE 资产之间的映射关系。

```cpp
// 创建或获取资产缓存
UUsdAssetCache3* AssetCache = NewObject<UUsdAssetCache3>();

// 在 USD 导入流程中，缓存会自动管理生成的 UStaticMesh、UMaterialInterface 等资产
// 避免重复导入相同的 USD Prim 时生成重复资产
```

### 基本用法 - 自定义资产编辑器

USDClassesEditor 模块提供了资产编辑器工具包，用于在编辑器中查看和编辑 USD Asset Cache：

```cpp
// 创建 USD Asset Cache 编辑器
#include "USDAssetCacheAssetEditorToolkit.h"

// FUsdAssetCacheAssetEditorToolkit 继承自 FAssetEditorToolkit
// 当用户双击 UUsdAssetCache3 资产时，系统自动创建此编辑器
// 它会打开一个 DetailsView 面板，展示 AssetCache 的所有可编辑属性
```

### 进阶用法 - 自定义资产定义

通过 `UAssetDefinition_UsdAssetCache` 自定义 USD Asset Cache 在内容浏览器中的显示：

```cpp
// USDAssetCache 在内容浏览器中的自定义表现
// - 显示名称: GetAssetDisplayName()
// - 图标颜色: GetAssetColor()
// - 资产类别: GetAssetCategories()
// - 支持导入: CanImport()
```

### 工厂类

`UUsdAssetCacheFactory` 允许通过"新建资产"菜单创建 USD Asset Cache 资产：

```cpp
#include "USDAssetCacheFactory.h"

// UUsdAssetCacheFactory 继承自 UFactory
// FactoryCreateNew() 创建新的 UUsdAssetCache3 实例
// ShouldShowInNewMenu() 控制是否在内容浏览器的"新建"菜单中显示
```

## Demo 示例

以下示例演示如何在编辑器工具中集成 USD Asset Cache 编辑器：

```cpp
// MyUSDTool.h
#pragma once

#include "CoreMinimal.h"

class UUsdAssetCache3;

class FMyUSDTool
{
public:
    void OpenAssetCacheEditor(UUsdAssetCache3* AssetCache);
};
```

```cpp
// MyUSDTool.cpp
#include "MyUSDTool.h"
#include "USDAssetCacheAssetEditorToolkit.h"
#include "USDAssetCache3.h"

void FMyUSDTool::OpenAssetCacheEditor(UUsdAssetCache3* AssetCache)
{
    if (!AssetCache)
    {
        return;
    }

    // 创建编辑器工具包实例并打开编辑器
    TSharedRef<FUsdAssetCacheAssetEditorToolkit> EditorToolkit =
        MakeShared<FUsdAssetCacheAssetEditorToolkit>();

    EditorToolkit->Initialize(
        EToolkitMode::Standalone,
        nullptr,
        AssetCache
    );
}
```

## 模块依赖

USDImporter 包含 9 个模块，各模块承担不同职责：

| 模块 | 用途 |
|---|---|
| `USDSchemas` | USD Schema 定义，提供 USD Prim 与 UE 类型之间的映射 |
| `USDStage` | USD Stage 运行时管理，加载和维护 USD 场景 |
| `USDStageImporter` | USD Stage 导入逻辑，将 USD Stage 内容转换为 UE 资产 |
| `USDStageEditor` | USD Stage 编辑器 UI，提供可视化 Stage 编辑面板 |
| `USDStageEditorViewModels` | USD Stage 编辑器的 MVVM 视图模型层 |
| `USDClassesEditor` | USD 相关资产的编辑器支持（资产缓存编辑器、工厂类、资产定义） |
| `USDExporter` | USD 导出功能，将 UE 内容写入 USD 格式 |
| `GeometryCacheUSD` | GeometryCache 的 USD 读写支持 |
| `USDTests` | USD 功能的自动化测试 |

**特殊构建依赖**：此插件依赖 Epic 的 USD SDK（通常位于 `Engine/Source/ThirdParty/OpenUSD/`），构建前需确保 USD SDK 已正确配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 支持分配不依赖蓝图的 Control Rig |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | 解决 USD 26.03 更新导致 LOD 变化时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位与 64 位格式说明符不匹配的问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 烘焙曝光动画轨道的所有帧 |

### 维护评价

- **活跃维护**：最近提交密度高（2026 年 4-5 月有多次实质性更新），涵盖动画、Control Rig 集成、浮点精度修复等
- **仍标记为实验性**：尽管已维护 7 年，`IsBetaVersion` 仍为 true，说明 Epic 认为 API 尚未完全稳定
- **功能持续扩展**：近期更新涵盖动画烘焙、Control Rig、LOD 兼容性等，表明仍在积极增加新特性
- **模块化架构**：9 个模块分工明确，架构成熟
- **推荐使用**：虽然标记为实验性，但此插件功能完整且持续维护，是 UE 中使用 USD 的唯一官方途径，在影视和建筑可视化项目中被广泛使用。注意默认未启用，需手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [USD 官方文档](https://openusd.org/release/index.html)（Pixar USD 项目文档）