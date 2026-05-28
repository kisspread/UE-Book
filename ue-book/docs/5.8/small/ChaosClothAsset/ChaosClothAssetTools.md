# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、工具类） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

该插件为 Unreal Engine 引入了基于图案（Pattern）的、新一代的布料资产系统，旨在替代和扩展现有的服装（Clothing）资产框架。其核心价值在于：

1.  **现代化架构**：它基于 UE 的 Chaos 物理引擎布料模拟系统，提供了更强大、更灵活的布料模拟能力。
2.  **资产导向**：将布料数据定义为独立的资产（`UChaosClothAsset`），便于在项目中管理、复用和版本控制，而不是作为骨骼网格体的一个附属部分。
3.  **工具集成**：提供了丰富的编辑器工具和转换器，支持从旧版服装资产（`UClothingAssetCommon`）迁移数据，并将布料资产导出为常规的骨骼网格体服装。
4.  **Dataflow 集成**：支持通过 Dataflow 节点图（Node Graph）来定义和编辑布料资产的几何与属性，实现程序化和非破坏性工作流。

简单来说，这个插件为美术师和开发者提供了一个更专业、可扩展性更强的布料制作与模拟工作流。

## 使用场景

-   你需要为角色制作复杂的、基于物理模拟的服装（如斗篷、长裙、飘带）。
-   你希望将布料数据与角色骨骼网格体分离，作为独立的资产进行管理，以便在不同角色间复用。
-   你的项目从传统的 `UClothingAsset` 迁移到基于 Chaos 物理的新系统。
-   你希望使用 Dataflow 节点图来程序化地定义或修改布料的模拟属性和形状。
-   你需要在编辑器中预览布料资产的缩略图，并快速将其转换为可预览的骨骼网格体。

## 蓝图用法

该插件的核心功能主要在 C++ 层实现，蓝图可调用的公开函数较少，主要集中在资产创建和转换工具中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Cloth Asset From Template` | 根据指定的 Dataflow 模板路径，以非模态方式创建一个新的布料资产。适用于脚本化流程。 | `UChaosClothAssetFactory` |

### 使用示例（蓝图描述）

在蓝图中，你无法直接操作底层的 `FClothPatternToDynamicMesh` 或 `FClothPatternToDynamicMeshMappingSupport`，因为这些是用于编辑器工具和资产导入导出的 C++ 类。蓝图层面的主要交互是通过资产和组件进行的。

1.  **创建资产**：通过编辑器内容浏览器右键菜单或调用 `UChaosClothAssetFactory` 的静态函数来创建新的布料资产。
2.  **编辑资产**：双击创建的布料资产，会打开基于 Dataflow 的专用编辑器，在其中通过节点图定义图案和模拟参数。
3.  **应用资产**：将编辑好的布料资产拖拽到角色的 `UChaosClothComponent` 上。

## C++ 用法

该插件的 C++ API 主要面向编辑器工具开发和资产流水线集成。

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"
```

### 基本用法

将单个布料图案（Pattern）转换为 `FDynamicMesh3`，用于后续的几何处理或预览。

```cpp
// 来源: Public/ChaosClothAsset/ClothPatternToDynamicMesh.h
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "ChaosClothAsset/ClothPatternVertexType.h"
#include "DynamicMesh/DynamicMesh3.h"

void ConvertSinglePatternToMesh(const UChaosClothAsset* ClothAsset, int32 LODIndex, int32 PatternIndex)
{
    using namespace UE::Chaos::ClothAsset;
    UE::Geometry::FDynamicMesh3 DynamicMesh;

    // 创建转换器
    FClothPatternToDynamicMesh Converter;
    // 将指定 LOD 和图案索引的模拟网格转换为动态网格
    // VertexDataType 选择 EClothPatternVertexType::Sim3D 表示3D模拟空间
    Converter.Convert(ClothAsset, LODIndex, PatternIndex, EClothPatternVertexType::Sim3D, DynamicMesh);

    // 现在 DynamicMesh 包含了该图案的几何数据，可以进行后续处理（如细分、布尔运算等）
}
```

### 进阶用法

处理从非流形（Non-Manifold）网格（如布料）转换而来的 `FDynamicMesh3` 时，使用映射支持类来跟踪原始顶点和三角形索引。

```cpp
// 综合自: Public/ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h 和 ClothPatternToDynamicMesh.h
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"
#include "DynamicMesh/DynamicMesh3.h"

void ProcessClothMeshWithMapping(UE::Geometry::FDynamicMesh3& Mesh)
{
    using namespace UE::Chaos::ClothAsset;

    // 1. 初始化映射支持对象，它会读取 Mesh 上可能存在的映射属性
    FClothPatternToDynamicMeshMappingSupport MappingSupport(Mesh);

    // 2. 检查网格是否包含来自原始布料数据的映射
    if (MappingSupport.IsMappedVertexInSource())
    {
        // 3. 遍历网格的每个顶点，获取其在原始布料图案中的ID
        for (int32 Vid : Mesh.VertexIndicesItr())
        {
            int32 OriginalVid = MappingSupport.GetOriginalVertexID(Vid);
            // 可以用 OriginalVid 从原始布料数据中查询权重、UV等附加信息
        }
    }

    // 4. （可选）在网格上附加或更新自定义映射数据
    TArray<int32> NewMappingData;
    // ... 填充 NewMappingData ...
    FClothPatternToDynamicMeshMappingSupport::AttachVertexMappingData(NewMappingData, Mesh);
}
```

## Demo 示例

一个最小的示例，展示如何在编辑器工具代码中，将布料资产转换为动态网格并检查其映射关系。

```cpp
// MyClothTool.h
#pragma once
#include "CoreMinimal.h"

class UChaosClothAsset;
namespace UE::Geometry { class FDynamicMesh3; }

class FMyClothTool
{
public:
    static void ConvertAndAnalyze(const UChaosClothAsset* ClothAsset);
};

// MyClothTool.cpp
#include "MyClothTool.h"
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"
#include "ChaosClothAsset/ClothPatternVertexType.h"
#include "DynamicMesh/DynamicMesh3.h"

void FMyClothTool::ConvertAndAnalyze(const UChaosClothAsset* ClothAsset)
{
    using namespace UE::Chaos::ClothAsset;
    if (!ClothAsset) return;

    UE::Geometry::FDynamicMesh3 DynamicMesh;

    // 步骤1: 转换整个LOD0的模拟网格
    FClothPatternToDynamicMesh Converter;
    Converter.Convert(ClothAsset, /*LODIndex=*/0, /*PatternIndex=*/INDEX_NONE, EClothPatternVertexType::Sim3D, DynamicMesh);

    // 步骤2: 分析转换后的网格，查看原始数据映射
    FClothPatternToDynamicMeshMappingSupport MappingSupport(DynamicMesh);
    if (MappingSupport.IsMappedVertexInSource())
    {
        UE_LOG(LogTemp, Log, TEXT("布料网格已转换，顶点与原始图案索引相关联。"));
        // 示例：获取第一个顶点的原始索引
        if (DynamicMesh.VertexCount() > 0)
        {
            int32 FirstOriginalVID = MappingSupport.GetOriginalVertexID(0);
            UE_LOG(LogTemp, Log, TEXT("动态网格顶点 0 对应原始索引: %d"), FirstOriginalVID);
        }
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("布料网格已转换，但未保留原始索引映射。"));
    }
}
```

## 模块依赖

你的项目模块若要使用此插件，需要根据功能依赖以下模块（已省略 Core、Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `GeometryFramework` | 使用 `FDynamicMesh3` 及相关动态网格组件。 |
| `MeshConversion` | 进行网格格式转换（如与 Static Mesh 交互）。 |
| `ModelingComponents` | 使用建模工具相关的组件和函数库。 |
| `Chaos` | 使用 Chaos 物理引擎的布料模拟核心。 |
| `Dataflow` | 与 Dataflow 节点图系统交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint | 修复蓝图中复制布料组件时丢失“在编辑器中模拟”设置的问题 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 优化并行布料模拟的性能，调整等待点位置 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为基于SKM的布料服装资产实现了骨骼映射刷新功能 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 修复了复制或粘贴带有布料资产的Actor后，编辑器资产别名未更新的问题 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器的代码 |

### 维护评价

-   **活跃维护**：从最近的提交记录看，该插件在过去一周内有多次实质性更新（功能修复、优化、清理），开发非常活跃。
-   **状态**：虽然从实验性文件夹移出并标记为 Beta，但仍处于功能完善和问题修复阶段。其模块类型和大量编辑器工具表明它专注于提供完整的制作流程。
-   **注意事项**：作为 Beta 版本，API 和功能未来可能发生变化。默认未启用，需要在项目中手动激活，并确保所有依赖的插件（ChaosCloth, Dataflow等）也已启用。
-   **推荐使用**：**推荐**用于新项目中需要复杂布料模拟的角色资产制作。对于希望从旧版服装系统迁移或追求更专业布料工作流的团队，这是一个值得采用的、现代化的解决方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
-   （暂无官方独立文档，相关功能说明可参考 UE 官方文档中关于 Chaos Cloth 和 Dataflow 的部分）