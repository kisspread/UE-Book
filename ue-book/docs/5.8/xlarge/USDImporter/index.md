# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件为虚幻引擎提供了一个完整的 USD (Universal Scene Description) 工作流支持。USD 是由皮克斯开发的开放、可扩展的场景描述格式，广泛应用于电影、动画和游戏行业。此插件不仅仅是简单的文件导入，它旨在实现：
1.  **资产交换**：支持将 USD 文件（`.usd`, `.usda`, `.usdc`）作为资产导入到虚幻引擎中，包括几何体、材质、动画等。
2.  **实时编辑**：提供 USD Stage Actor 和编辑器工具，允许用户在虚幻引擎内以非破坏性的方式实时查看、编辑和组合多个 USD 图层。
3.  **工作流集成**：支持将虚幻引擎中的场景或资产导出为 USD 格式，便于与 Maya、Houdini 等 DCC 软件进行双向协作。
4.  **高级功能**：包括几何缓存导入、骨骼动画控制、材质映射以及针对 USD 动画轨道的烘焙等专业功能。

其核心价值在于为影视、动画和虚拟制片等高保真可视化领域提供标准化的资产交换管线。

## 使用场景

-   **影视与虚拟制片**：从 DCC 软件（如 Maya, Houdini）导出的 USD 场景或资产需要导入到虚幻引擎中进行实时渲染、预览或最终输出。
-   **资产管线管理**：使用 USD 的图层（Layer）和变体（Variant）系统来管理复杂场景的不同配置或细节层次。
-   **跨软件协作**：需要在虚幻引擎和多个 DCC 工具之间无损地交换动画、几何体和材质。
-   **几何缓存播放**：需要高效播放由 USD 格式存储的预计算几何体动画（如布料、流体模拟结果）。

## 模块列表

该插件由 9 个模块协同工作，构成完整的 USD 支持栈：

| 模块名 | 一句话说明 |
|---|---|
| `USDSchemas` | 核心模块，定义了 USD 类型（如 Prim、Attribute）在虚幻引擎中的表现形式。 |
| `USDStage` | 管理 USD Stage 的运行时表示，负责加载、更新和管理 USD 图层。 |
| `USDStageImporter` | 处理 USD 文件的导入逻辑，将 USD 数据转化为虚幻引擎资产。 |
| `USDStageEditor` | 提供编辑器 UI 工具（如 USD Stage 窗口），用于交互式查看和编辑 USD Stage。 |
| `USDStageEditorViewModels` | `USDStageEditor` 的 ViewModel 层，将 USD 数据与编辑器 UI 逻辑解耦。 |
| `USDClassesEditor` | 提供编辑器专用的蓝图节点和资产工厂，用于在蓝图或编辑器脚本中操作 USD。 |
| `USDExporter` | 实现将虚幻引擎场景（Level、Actor）导出为 USD 格式的功能。 |
| `GeometryCacheUSD` | 将 USD 格式的几何缓存（Alembic 风格）适配为虚幻引擎的 `UGeometryCache` 资产。 |
| `USDTests` | 包含自动化测试用例，验证 USD 导入、导出和编辑功能的正确性。 |

## 蓝图用法

`USDClassesEditor` 和 `USDStageEditor` 模块提供了大量可供蓝图调用的节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Usd Stage` | 从文件路径加载一个 USD Stage 资产。 | `UUsdAssetCache` |
| `Import All` | 将当前 USD Stage 中所有内容批量导入为虚幻资产。 | `UUsdStageImportOptions` |
| `Set Visibility` | 控制 USD Stage 中特定 Prim（对象）的可见性。 | `AUsdStageActor` |
| `Set Attribute Value` | 设置 USD Prim 上某个属性（Attribute）的值。 | `UUsdStage` |

### 使用示例

在蓝图中，典型的工作流是：
1.  使用“Load Usd Stage”节点加载一个 `.usd` 文件，获得一个 `UUsdStage` 对象引用。
2.  将该对象连接到一个 `AUsdStageActor` 或通过“Import All”节点进行批量导入。
3.  使用“Set Visibility”等节点在运行时动态控制 USD 场景中的元素。
4.  对于导入后的资产（如 Static Mesh, Skeletal Mesh），可以像使用普通虚幻资产一样在蓝图中进行实例化、放置和操控。

## C++ 用法

详细的 C++ 用法和 API 请参见各子模块文档。核心操作通常围绕 `UUsdStage` 和 `AUsdStageActor` 展开。

### 头文件引入

```cpp
#include “UsdStage.h”
// 根据需要引入其他模块头文件，如 USDClassesEditor
#include “UsdClassesEditor.h”
```

### 基本用法

**通过 C++ 加载并操作 USD Stage (来自 USDTests 模块示例)**：
```cpp
// 引用自 Engine/Plugins/Importers/USDImporter/Source/USDTests/Tests/USDStageTests.cpp

// 创建一个临时的 USD Stage
FScopedUsdStage UsdStage(TEXT(“MyTempStage.usda”));
if (UsdStage.GetStage())
{
    // 创建一个默认的 Cube Prim
    UsdStage.GetStage()->DefinePrim(SdfPath(“/MyCube”), TfToken(“Cube”));
    
    // 获取并设置 Cube 的大小属性
    UsdAttribute SizeAttr = UsdStage.GetStage()->GetPrimAtPath(SdfPath(“/MyCube”)).GetAttribute(TfToken(“size”));
    SizeAttr.Set(2.0); // 将大小设置为 2.0
    
    // 保存修改
    UsdStage.GetStage()->Save();
}
```

### 进阶用法

**监听 USD Stage 的变更 (来自 USDStage 模块示例)**：
```cpp
// 引用自 Engine/Plugins/Importers/USDImporter/Source/USDStage/Private/UsdStage.cpp

// 获取一个已加载的 USD Stage
UUsdStage* UsdStage = ...;
// 注册一个回调函数，当 Stage 中的对象发生变更时触发
UsdStage->OnStageObjectChanged.AddLambda([](const UsdObjectChangedData& Data)
{
    UE_LOG(LogTemp, Log, TEXT(“USD Object changed: %s”), *Data.PrimPath);
});
```

## Demo 示例

本插件本身包含丰富的示例资产和测试，位于 `Engine/Plugins/Importers/USDImporter/Content/` 和 `Source/USDTests/` 目录中。一个最小的功能演示通常涉及：
1.  在项目设置中启用 `USDImporter` 插件。
2.  在内容浏览器中右键，选择“导入”，然后选择一个 `.usd` 文件。
3.  或者在编辑器中放置一个 `USD Stage Actor`，然后在细节面板中指定一个 USD 文件路径。
4.  使用“USD Stage”窗口（通过“窗口 -> 虚拟制片 -> USD Stage”打开）来查看和交互编辑导入的场景。

## 模块依赖

要使用此插件，你的项目或模块需要链接以下核心模块（常见依赖如 Core, Engine 等已省略）：

| 模块 | 用途 |
|---|---|
| `USDCore` | Epic 内部封装的 USD 库核心绑定，提供基础类型和函数。 |
| `USDConverter` | 负责 USD 数据类型与虚幻引擎数据类型之间的转换。 |
| `USDUtilities` | 提供操作 USD 数据的便捷工具函数库。 |
| `USDClasses` | 定义了与 USD 相关的虚幻资产类和数据结构。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：新增对分配独立于蓝图的控制装配的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | USD：解决升级到 26.03 版本导致在 LOD 变化时 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式说明符与参数位宽不匹配（32/64位）的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙曝光动画轨道的所有帧。 |

### 维护评价

**活跃维护中**。
-   **创建于 2018 年**，是一个成熟且历史悠久的插件。
-   **最近更新非常频繁**（截至 2026 年 5 月仍有功能性提交和 Bug 修复），表明 Epic 持续投入开发，是 USD 工作流的核心支持部分。
-   **实验性标记 (`IsBetaVersion: true`)**：尽管维护活跃，但插件仍被标记为 Beta 版。这可能意味着其 API 或功能在未来版本中仍有变动可能，或者某些高级特性（如特定的材质转换或复杂动画）尚未完全稳定。建议在生产环境中谨慎使用，并密切关注版本更新日志。
-   **结论**：对于需要 USD 支持的项目，尤其是虚拟制片和影视级内容创作，**推荐使用**，但应做好应对 API 变化的准备，并充分利用 `USDTests` 模块验证工作流的稳定性。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/working-with-usd-in-unreal-engine/)（虚幻引擎官方 USD 工作流指南）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)