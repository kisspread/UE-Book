# Interchange OpenUSD Chaos Cloth Asset

> Allows translation of OpenUSD files with Chaos Cloth Asset schemas via Interchange（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD布料资产导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质引用） |
| 模块 | `InterchangeOpenUSDChaosClothAssetImport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSDChaosClothAsset) | |

## 用途

此插件是 Epic 官方 Interchange 框架的一个扩展，其核心作用是为 Unreal Engine 的 **Chaos Cloth 资产**（即物理驱动的布料系统资产）提供从 **OpenUSD** 格式的导入支持。

它解决的问题是：当用户从其他 DCC 工具（如 Marvelous Designer、CLO3D）或自定义工具中，以 OpenUSD 文件格式导出包含布料模拟数据（如模拟网格、织物属性、缝合信息、弹簧、求解器参数等）的资产时，UE 的 Interchange 导入管线能够识别这些数据，并将其正确地转换、组装为 UE 内部可用的 `UChaosClothAsset` 及其相关组件，从而实现完整的布料模拟工作流。

插件通过注册一个自定义的 USD Schema Handler (`FInterchangeOpenUSDChaosClothAssetRootSchemaHandler`) 来拦截和处理带有特定布料相关 API 模式（如 `ClothRootAPI`, `SimMeshDataAPI`, `CloFabricAPI` 等）的 USD Prim，并在 Interchange 的节点图中生成对应的中间节点，最终由布料资产管线 (`UInterchangeOpenUSDChaosClothAssetPipeline`) 处理这些节点以创建最终资产。

## 使用场景

- 你正在使用 Marvelous Designer、CLO3D 或其他支持 OpenUSD 导出的布料设计软件，需要将设计好的、包含物理属性的布料模型导入 UE5 进行实时模拟 → **使用此插件**。
- 你的美术团队交付的资产是 USD 格式，并且其中包含了为 Chaos Cloth 准备的自定义模式数据 → **使用此插件**。
- 你需要通过 Interchange 管线自动化导入流程，并且源文件是带有布料数据的 USD → **使用此插件**。

## 蓝图用法

此插件的蓝图可交互性主要体现在其**导入管线**的配置上。当通过 Interchange 对话框导入 USD 文件时，此插件会提供一个可配置的管线。

### 核心节点与属性

该插件提供了一个蓝图类型的管线类 `UInterchangeOpenUSDChaosClothAssetPipeline`，其属性可在导入对话框中编辑。

| 节点/属性 | 说明 | 所在类 |
|---|---|---|
| `PipelineDisplayName` | 在导入对话框中显示的管线名称。 | `UInterchangeOpenUSDChaosClothAssetPipeline` |
| `PreviewSurfaceMaterialReplacement` | 用于替换导入的 USD 预览表面材质的 UE 材质资产路径。 | `UInterchangeOpenUSDChaosClothAssetPipeline` |
| `PreviewSurfaceTranslucentMaterialReplacement` | 用于替换导入的 USD 半透明预览表面材质的 UE 材质资产路径。 | `UInterchangeOpenUSDChaosClothAssetPipeline` |
| `PreviewSurfaceTwoSidedMaterialReplacement` | 用于替换导入的 USD 双面预览表面材质的 UE 材质资产路径。 | `UInterchangeOpenUSDChaosClothAssetPipeline` |
| `DisplayColorMaterialReplacement` | 用于替换导入的 USD 显示颜色材质的 UE 材质资产路径。 | `UInterchangeOpenUSDChaosClothAssetPipeline` |

### 使用示例（蓝图描述）

1.  在编辑器中，通过 **内容浏览器** 右键 → **Import** 导入一个包含布料数据的 USD 文件。
2.  在弹出的 **Interchange Import** 对话框中，找到 **Pipelines** 部分。
3.  你应该能看到一个名为 “Interchange OpenUSD Chaos Cloth Asset”（或你自定义的 `PipelineDisplayName`）的管线选项。
4.  点击该管线选项，下方会显示其属性（即上述表格中的属性）。
5.  你可以根据需要修改 `PreviewSurfaceMaterialReplacement` 等材质替换路径，指向项目中合适的材质资产。
6.  配置完成后，点击 **Import**。Interchange 会使用此管线处理 USD 文件中的布料数据，最终在内容浏览器中生成 `UChaosClothAsset`。

## C++ 用法

此插件主要作为 Interchange 框架的内部扩展，直接 C++ 交互较少，核心是提供常量定义和 Schema Handler。

### 头文件引入

```cpp
// 要使用插件中定义的 USD Schema 名称和属性常量
#include "InterchangeOpenUSDChaosClothAssetDefinitions.h"
```

### 基本用法

以下示例展示了如何使用插件提供的常量来检查或解析 USD Prim 的属性名称。这在自定义 Schema Handler 或数据处理逻辑中可能会用到。

```cpp
#include "InterchangeOpenUSDChaosClothAssetDefinitions.h"

void CheckUsdPrimAttributes(const UE::FUsdPrim& Prim)
{
    // 检查 Prim 是否应用了 “ClothRootAPI” 模式
    // 伪代码，具体 USD API 调用需参考 USD SDK
    bool bHasClothRootAPI = Prim.HasAPI(UE::Interchange::USD::ChaosCloth::ClothRootAPI);
    if (bHasClothRootAPI)
    {
        // 获取一个属于 “CloFabricAPI” 模式的属性，例如 “density”
        // UE::Interchange::USD::ChaosCloth::CloFabricDensity 的值是 “primvars:clo:density”
        FString DensityAttributeName = UE::Interchange::USD::ChaosCloth::CloFabricDensity;
        // ... 从 Prim 的属性中获取该属性值
    }
}
```
*(此代码为示意性伪代码，展示常量用法)*

### 进阶用法

对于高级用户，如果需要扩展或理解此插件的工作流程，可以查看 `FInterchangeOpenUSDChaosClothAssetRootSchemaHandler` 的实现。该类继承自 `FSchemaHandler`，负责：
1.  通过 `GetTargetSchemaName` 返回 `ClothRootAPI`，表明它处理带有此模式的 Prim。
2.  在 `CanHandlePrim` 中进一步判断 Prim 的有效性。
3.  在 `OnTranslate` 中，将包含布料模式的 USD Prim 转换为 Interchange 节点，这些节点随后会被 `UInterchangeOpenUSDChaosClothAssetPipeline` 处理。
*(由于源码未提供完整实现，此处为基于头文件的逻辑推断)*

## Demo 示例

由于此插件是底层框架扩展，没有独立的、可运行的 Actor 或组件 Demo。一个最小的“使用”示例是在你的项目模块中声明对本插件模块的依赖，并确保导入管线可用。

```cpp
// YourModule.h (在你的项目模块中)
#pragma once

#include "Modules/ModuleManager.h"

class FYourGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        // 模块启动时，可以确保 Interchange 和此插件的模块已加载
        FModuleManager::Get().LoadModule(TEXT("Interchange"));
        FModuleManager::Get().LoadModule(TEXT("InterchangeOpenUSDChaosClothAssetImport"));
    }
};
```

## 模块依赖

要使用此插件，你的项目或插件模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `Interchange` | 核心的资产交换框架。 |
| `UsdCore` 或 `USD` 相关模块 | 提供 USD SDK 的 UE 封装，用于访问和解析 USD 数据。 |
| `ChaosClothAssetEngine` | 提供 `UChaosClothAsset` 等布料资产类型和引擎集成。 |

## 维护状态

### 近期更新

```
- 2026-05-14 561d9c2d USD Pregen: Fix materials inside instances not being deduplicated; (修复实例内材质未被去重的问题)
- 2026-04-27 665076e6 USD Interchange: Add support for ChaosCloth asset. (USD Interchange：添加对 ChaosCloth 资产的支持)
```

### 维护评价

- **创建时间**：2026年4月27日（基于提供的数据）。
- **活跃度**：该插件非常新，最近的提交（2026年5月14日）是对材质处理的bug修复，表明它正在被**积极使用和维护**。
- **稳定性**：作为一个新增不久的插件，可能仍在快速迭代中，但作为 Epic 官方 Interchange 扩展的一部分，其稳定性和兼容性有基本保障。
- **推荐使用**：**推荐**。如果你的工作流涉及通过 USD 导入 Chaos Cloth 资产，这是官方提供的唯一标准途径。虽然 `EnabledByDefault` 为 `false`（需要手动启用），但这通常是为了避免在不需要的项目中增加模块开销。请确保你的项目依赖链中包含了 `ChaosClothAsset` 模块（在项目设置或 .Build.cs 中）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSDChaosClothAsset)
- [官方文档]( ) (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSDChaosClothAsset/Tests) (如果存在)