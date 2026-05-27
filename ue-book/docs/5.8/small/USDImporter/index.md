# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD (Universal Scene Description) 是皮克斯开发的通用场景描述格式，在影视、动画和虚拟制片领域被广泛用作资产交换标准。此插件为 Unreal Engine 提供了导入、编辑、管理和导出 USD 文件的能力，解决了 USD 资产与 Unreal Engine 工作流的集成问题。它允许艺术家和开发者直接在引擎中操作复杂的 USD 场景层次结构、绑定、动画和材质，而无需通过中间格式进行转换。

## 使用场景

-   **影视动画制作**：电影或动画团队使用 USD 在不同 DCC 软件（如 Maya, Houdini, Katana）间交换复杂的场景和资产，并在 UE 中进行实时预览、渲染或虚拟制片。
-   **虚拟制片**：将完整的 USD 虚拟场景（包含几何、灯光、材质、绑定）导入 UE，用于 LED 墙实时渲染。
-   **资产管线集成**：作为大型资产管线的一部分，自动或手动导入由其他软件导出的 USD 资产。
-   **跨软件协作**：游戏开发团队与负责过场动画或影视内容的外部团队协作时，使用 USD 作为交换格式。

## 模块职责概览

本插件由多个模块协同工作，以下是各模块的核心职责：

| 模块 | 核心职责 |
|---|---|
| `USDSchemas` | 核心模块。定义 USD 与 UE 类型之间的映射规则（Schemas）和转换基础架构。 |
| `USDStage` | 管理 USD Stage（场景）的运行时表示，负责加载、遍历、监听 USD Prim 的变化。 |
| `USDStageImporter` | 处理从 USD Stage 中提取数据并创建对应 UE 资产（如 StaticMesh, SkeletalMesh, Material）的逻辑。 |
| `USDStageEditor` | 提供编辑器 UI（如 USD Stage 窗口），用于可视化、交互和编辑 USD Stage。 |
| `USDStageEditorViewModels` | 为 `USDStageEditor` 的 UI 提供数据模型（ViewModel）和业务逻辑。 |
| `USDClassesEditor` | 提供编辑器专用的 USD 相关类和工具，例如资产操作和细节面板自定义。 |
| `USDExporter` | 提供从 UE 向 USD 格式导出资产和场景的功能。 |
| `GeometryCacheUSD` | 专门为 USD 动画曲线和几何体缓存提供支持。 |
| `USDTests` | 包含该插件的自动化测试用例。 |

## 蓝图用法

主要通过 `USDStage` 和 `USDExporter` 模块暴露蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Stage` | 引擎核心导入函数，通过 `FUSDImporter` 实现 | `UUSDStageImportFactory` |
| `Export To USD` | 将 UE 资产导出为 USD 文件 | `UUSDExporter` |
| 与 `UsdStageActor` 相关的节点 | 在场景中放置并驱动一个 USD Stage | `AUsdStageActor` |

### 使用示例（蓝图描述）
1.  **导入 USD**：通常通过内容浏览器右键 -> Import Asset，或在蓝图中通过 `FAssetTools::Get().ImportAssets()` 触发，最终调用 `USDStageImporter` 模块。
2.  **在场景中使用**：将 `UsdStageActor` 拖入场景，然后在其 Details 面板中指定 USD 文件路径。通过蓝图可以动态修改其属性。
3.  **导出**：通过 `UUSDExporter` 的蓝图节点，指定要导出的 UE 对象或文件列表以及输出路径。

## C++ 用法

C++ 接口更为强大和灵活，适合进行深度集成和自定义处理。

### 头文件引入

```cpp
#include “USDStage.h” // 包含核心 Stage 管理和 Prims
#include “USDTypes.h” // 包含 USD 与 UE 类型转换工具
// 根据功能需求引入其他模块头文件，如 USDExporter.h
```

### 基本用法

```cpp
// 创建并加载一个 USD Stage
TSharedRef<UE::USDStage::FUsdStage> UsdStage = UE::USDStage::FUsdStage::Create(“/Path/To/Scene.usd”);
if (UsdStage->IsValid())
{
    // 遍历 Stage 下的 Prim
    for (const UE::USDStage::FUsdPrim& Prim : UsdStage->GetRootPrims())
    {
        UE_LOG(LogTemp, Log, TEXT(“Prim: %s, Type: %s”), *Prim.GetPrimPath(), *Prim.GetPrimTypeName());
    }
}
```

*（示例基于模块 `USDStage` 和 `USDSchemas` 的通用模式推断）*

## Demo 示例

由于此插件功能庞大，一个完整的最小示例会非常复杂。建议从官方的 `USDTests` 模块中学习如何加载、遍历和提取 USD 数据。一个极简的“读取并打印 Prim 名称”示例已在上方的 **C++ 用法** 部分展示。

## 模块依赖

要使用此插件的功能，你的模块通常需要依赖 `USDStage` 或 `USDStageImporter` 等特定模块。这些模块又会依赖底层的 `USDSchemas` 和 USD 库。

| 模块 | 用途 |
|---|---|
| `USD` (第三方) | OpenUSD 核心运行时库，由 UE 集成并提供。 |
| `USDStage` | 访问和管理 USD Stage 的核心接口。 |
| `USDStageImporter` | 进行资产导入时需要依赖。 |
| `USDExporter` | 进行资产导出时需要依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增功能：支持分配不依赖于蓝图的控制绑定（Control Rigs）。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | 解决更新至 USD 26.03 后，LOD 变化导致 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串中 32 位与 64 位参数的匹配错误。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 功能改进：支持烘焙曝光动画轨道的所有帧。 |

### 维护评价

**活跃维护**。该插件创建于约 8 年前，属于 Epic 的核心内容创作工具链。从近期提交记录看，它仍在持续接收功能性更新、兼容性修复（如跟踪新版 USD）和 bug 修复，维护非常活跃。需要特别注意的是，该插件目前处于 **实验性（Beta）** 状态且**默认未启用**，意味着其 API 可能会变更，稳定性尚未得到全面保证。对于需要在生产中使用 USD 的影视动画和虚拟制片项目，这是目前 Unreal Engine 官方提供的最重要且持续更新的集成方案，推荐评估使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]()
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)