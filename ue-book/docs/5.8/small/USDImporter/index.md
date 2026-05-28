# USD Importer

> Adds support for importing the USD file format into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、蓝图资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件提供了在虚幻引擎中处理 **Universal Scene Description (USD)** 文件格式的全面支持。USD 是 Pixar 开发的开源场景描述框架，广泛应用于电影、动画和视觉特效行业，用于高效地交换和组合复杂的 3D 场景数据。

USDImporter 不仅限于“导入”，它是一个完整的 USD 工作流解决方案，包括：
- **导入**：将 USD 文件（`.usd`, `.usda`, `.usdc`）导入为虚幻引擎资产。
- **导出**：将虚幻引擎场景或资产导出为 USD 格式。
- **编辑**：提供专门的 USD Stage 编辑器，允许在虚幻引擎中直接查看和编辑 USD 场景图层、属性和 prim。
- **实时同步**：支持将 USD Stage 作为代理资产（Stage Actor）放入关卡，并实现实时或按需的双向同步。
- **动画支持**：处理 USD 的动画和变形数据（如骨骼网格体、变形目标、几何体缓存）。
- **架构支持**：将 USD 的 prim 和属性映射到虚幻引擎的类型系统（USchemas）。

## 使用场景

- **跨部门/跨软件协作**：你的团队使用 Maya、Houdini、Blender 等 DCC 工具制作资产，需要将它们无缝导入虚幻引擎，同时保留完整的场景层次和材质信息。
- **大型虚拟制片项目**：需要实时同步虚拟场景，并在虚幻引擎中直接编辑灯光、摄像机、几何体等 USD prim。
- **程序化内容生成**：通过脚本或蓝图生成或修改 USD Stage，然后将其导入引擎，用于建筑可视化或大规模场景。
- **资产管线集成**：将 USD 作为资产管线中的中间格式，实现自动化资产导入、验证和部署。
- **几何体缓存播放**：使用 `GeometryCacheUSD` 模块导入预计算的顶点动画序列，用于角色动画或特效。

## 蓝图用法

由于 USDImporter 是一个大型、复杂的插件，其蓝图 API 分布在多个模块中。核心交互通常通过 USD Stage Actor 和专门的编辑器工具完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Usd Stage` | 加载一个 USD 文件并创建一个 Stage 对象。 | `UUsdStageActor` |
| `Save Stage` | 将当前 USD Stage 保存到文件。 | `UUsdStageActor` |
| `Import USD Stage` | 将 USD Stage 的内容作为蓝图资产导入到内容浏览器。 | `UUsdStageImportLibrary` |
| `Set Time` | 设置 USD Stage 的当前时间，用于播放动画。 | `UUsdStageActor` |

### 使用示例（蓝图描述）

1.  **在关卡中放置 USD Stage**：
    *   从放置 Actor 面板中拖放 `Usd Stage Actor` 到关卡。
    *   在细节面板中，为其指定一个 `.usd` 文件。
    *   勾选 “Realtime Sync” 可实现与外部 DCC 工具的实时同步。

2.  **通过蓝图导入 USD 资产**：
    *   使用 `Load Usd Stage` 节点加载 USD 文件。
    *   使用 `Import USD Stage` 节点，可以配置导入选项（如网格体合并、材质创建规则）。
    *   导入的资产会出现在指定的内容浏览器路径下。

3.  **控制 USD 动画**：
    *   通过 `Set Time` 节点驱动 Stage Actor 的时间轴。
    *   可以配合 Sequencer 创建轨道来控制 USD 动画的播放。

> **注意**：高级 USD 编辑和 Prim 属性修改主要通过 `USD Stage Editor` 编辑器窗口进行，蓝图更多用于流程控制和自动化导入。

## C++ 用法

C++ 用法主要涉及直接操作 USD 的 C++ API（pxr 库）和虚幻引擎的封装类。

### 头文件引入

```cpp
#include "USDStageActor.h"
#include "USDStageImportContext.h"
#include "UsdWrappers/UsdStage.h"
```

### 基本用法

以下示例展示如何在 C++ 中加载一个 USD Stage 并遍历其 Prim。

```cpp
// 来自 Source/USDStage/Private/USDStageActor.cpp 的思路示例
FUsdStage UsdStage = FUsdStage::Open(TEXT("D:/MyScene.usda"));
if (UsdStage)
{
    UsdStage.Traverse([&](const FUsdPrim& Prim)
    {
        UE_LOG(LogTemp, Log, TEXT("Found Prim: %s, Type: %s"),
            *Prim.GetPrimPath().GetString(),
            *Prim.GetPrimTypeName().GetString());
        return true; // 继续遍历
    });
}
```

### 进阶用法

使用 `UUsdStageImportContext` 进行可控的资产导入，这比蓝图节点更灵活。

```cpp
// 来自 Source/USDStageImporter/Private/USDStageImporter.cpp 的思路示例
UUsdStageImportContext* ImportContext = NewObject<UUsdStageImportContext>();
ImportContext->OriginalFilePath = TEXT("D:/Asset.usd");
ImportContext->RenderContext = EUsdRenderContext::Unreal;
ImportContext->bImportGeometry = true;
ImportContext->bImportMaterials = true;
ImportContext->bImportAnimations = true;

// 执行导入
bool bSuccess = UsdStageImporterModule.ImportUsdStage(ImportContext);
```

## 模块列表

以下是组成 USDImporter 插件的各个子模块及其核心职责：

| 模块 | 说明 |
|---|---|
| **USDSchemas** | 核心运行时模块。将 USD 的 Prim 类型（如 Mesh, Light, Camera）和属性映射到虚幻引擎的类型系统（UStructs, UClasses）。 |
| **USDStage** | 提供 USD Stage Actor、USD Stage 逻辑以及与 Unreal 的 USD 编辑器（USD Stage Editor）通信的桥梁。 |
| **USDStageImporter** | 负责将 USD Stage 中的数据转换为虚幻引擎资产（如 Static Mesh, Skeletal Mesh, Material）的导入流程核心逻辑。 |
| **USDStageEditor** | 编辑器模块。提供 USD Stage Editor 窗口，允许用户交互式地浏览、选择和编辑 USD Stage 中的 Prim 及其属性。 |
| **USDStageEditorViewModels** | USD Stage Editor 的视图模型层，负责管理 UI 状态、选择和编辑操作的数据。 |
| **USDClassesEditor** | 编辑器模块。扩展虚幻引擎的编辑器功能，以更好地显示和编辑 USD 类型。 |
| **USDExporter** | 负责将虚幻引擎资产（关卡、网格体、材质等）导出为 USD 格式的模块。 |
| **GeometryCacheUSD** | 支持导入和播放基于 USD 的几何体缓存（Geometry Cache）动画序列。 |
| **USDTests** | 包含针对 USDImporter 插件功能的自动化测试用例。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为单精度时产生的编译警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：新增对分配不依赖特定蓝图的控制绑定的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | USD：解决升级到 26.03 版本后，LOD 变化时导致 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串中 32 位与 64 位格式说明符不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙曝光动画轨道的所有帧。 |

### 维护评价

- **活跃维护**：从近期提交记录来看，USDImporter 插件仍在**积极维护和更新**。最近的提交集中在**Bug修复**、**动画系统增强**（如控制绑定支持）和**性能/兼容性改进**（如浮点精度问题）。
- **实验性状态**：尽管 `.uplugin` 中标记为 `IsBetaVersion: true` 和 `EnabledByDefault: false`，但这通常意味着它是一个功能强大但仍在快速迭代的高级特性，可能包含未完全稳定或文档不完整的接口。
- **推荐使用**：对于需要在虚幻引擎中深度集成 USD 工作流的项目（特别是影视、动画和高级可视化），该插件是**官方推荐且持续维护的解决方案**。由于其复杂性，建议在使用前充分了解 USD 概念，并关注其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/working-with-universal-scene-description-usd-in-unreal-engine/) (无链接字段，提供常见文档入口)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests/)