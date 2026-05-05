# Chaos Cloth Asset Editor

> Editor for modifying cloth assets（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、数据流节点） |
| 模块 | `ChaosClothAssetDataflowNodes` (Runtime), `ChaosClothAssetEditor` (Editor), `ChaosClothAssetEditorTools` (Runtime), `ChaosClothAssetTools` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor) | |

## 用途

ChaosClothAssetEditor 是一个用于创建和编辑基于 Chaos 物理系统的布料资产的完整编辑器插件。它解决的核心问题是：为美术和技术美术提供一个可视化的、基于节点的工具集，用于定义布料的模拟网格（Simulation Mesh）、渲染网格（Render Mesh）以及它们之间的映射关系，并最终生成可用于运行时布料模拟的资产。

该插件不仅仅是一个简单的编辑器，它包含了一个完整的数据流（Dataflow）系统，允许用户通过连接节点来构建布料资产的生成逻辑，类似于材质编辑器或蓝图。这使得布料资产的创建过程更加灵活、可复用和可调试。

## 使用场景

- **角色服装设计**：为游戏角色创建复杂的布料（如长袍、披风、裙子），需要精确控制哪些区域参与物理模拟，哪些区域仅作为渲染网格。
- **布料模拟调试**：在编辑器中实时预览和调整布料的模拟参数（如刚度、阻尼），并立即看到效果，无需进入游戏运行时。
- **程序化布料生成**：利用数据流节点，通过程序化方式生成或修改布料资产，适用于需要大量变体或动态生成布料的场景。
- **资产迁移与优化**：将传统的布料资产转换为基于 Chaos 的新格式，并利用工具进行优化和清理。

## 蓝图用法

该插件主要通过编辑器界面和数据流图表进行交互，直接暴露给蓝图的节点较少。其核心功能集成在编辑器工具和资产工厂中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create New Cloth Asset` | 在编辑器内容浏览器中通过右键菜单创建新的 `UChaosClothAsset` 资产。 | `UChaosClothAssetFactory` |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中右键 -> `Animation` -> `Chaos Cloth Asset`，即可创建一个新的布料资产。
2.  **编辑资产**：双击创建的资产，将打开专用的布料资产编辑器。在该编辑器中，用户通过连接数据流节点（如 `ClothAssetImportNode`, `ClothAssetSewingNode` 等）来定义布料的几何形状、属性和模拟设置。
3.  **应用资产**：将编辑好的 `UChaosClothAsset` 拖拽到场景中的 `SkeletalMeshComponent` 上，并在组件的 `Cloth` 部分进行配置，即可启用布料模拟。

## C++ 用法

该插件的 C++ API 主要面向工具开发和数据处理，核心是网格数据转换。

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "ChaosClothAsset/ClothAssetFactory.h"
```

### 基本用法

将布料资产中的一个模拟模式（Pattern）转换为动态网格，用于编辑器工具处理或可视化。

```cpp
// 来源: Engine/Plugins/ChaosClothAssetEditor/Source/ChaosClothAssetTools/Public/ChaosClothAsset/ClothPatternToDynamicMesh.h
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "ChaosClothAsset/ClothAsset.h"

void ConvertClothPatternToMesh(const UChaosClothAsset* ClothAsset, int32 LODIndex, int32 PatternIndex)
{
    using namespace UE::Chaos::ClothAsset;
    
    FClothPatternToDynamicMesh Converter;
    UE::Geometry::FDynamicMesh3 DynamicMesh;
    
    // 将指定LOD和Pattern的3D模拟顶点转换为动态网格
    Converter.Convert(
        ClothAsset,
        LODIndex,
        PatternIndex,
        EClothPatternVertexType::Sim3D, // 使用3D模拟顶点
        DynamicMesh
    );
    
    // 现在可以对 DynamicMesh 进行各种几何操作
    // 例如：计算包围盒、应用修改器等
}
```

### 进阶用法

处理网格映射关系，这对于在编辑器中进行精确的顶点选择和属性传递至关重要。

```cpp
// 来源: Engine/Plugins/ChaosClothAssetEditor/Source/ChaosClothAssetTools/Public/ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"
#include "DynamicMesh/DynamicMesh3.h"

void WorkWithMeshMapping(const UE::Geometry::FDynamicMesh3& ConvertedMesh)
{
    using namespace UE::Chaos::ClothAsset;
    
    // 创建映射支持对象
    FClothPatternToDynamicMeshMappingSupport MappingSupport(ConvertedMesh);
    
    // 检查源数据是否包含映射顶点（例如，来自UV岛的重叠顶点）
    if (MappingSupport.IsMappedVertexInSource())
    {
        // 遍历网格中的每个顶点
        for (int32 VertexID : ConvertedMesh.VertexIndicesItr())
        {
            // 检查该顶点是否是映射产生的（即，是否对应源数据中的多个顶点）
            if (MappingSupport.IsMappedVertexID(VertexID))
            {
                // 获取该顶点在原始布料数据中的ID
                int32 OriginalVertexID = MappingSupport.GetOriginalVertexID(VertexID);
                // 可以基于 OriginalVertexID 进行进一步处理，如查询原始UV或属性
            }
        }
    }
    
    // 类似地，可以处理三角形映射
    if (MappingSupport.IsMappedTriangleInSource())
    {
        for (int32 TriangleID : ConvertedMesh.TriangleIndicesItr())
        {
            if (MappingSupport.IsMappedTriangleID(TriangleID))
            {
                int32 OriginalTriangleID = MappingSupport.GetOriginalTriangleID(TriangleID);
                // ...
            }
        }
    }
}
```

## Demo 示例

一个最小的示例，展示如何通过 C++ 代码创建一个布料资产工厂实例并生成新资产。

```cpp
// MyClothAssetCreator.h
#pragma once

#include "CoreMinimal.h"

class UChaosClothAsset;

class FMyClothAssetCreator
{
public:
    static UChaosClothAsset* CreateNewClothAsset(UObject* InParent, const FName& InName);
};
```

```cpp
// MyClothAssetCreator.cpp
#include "MyClothAssetCreator.h"
#include "ChaosClothAsset/ClothAssetFactory.h"
#include "ChaosClothAsset/ClothAsset.h"

UChaosClothAsset* FMyClothAssetCreator::CreateNewClothAsset(UObject* InParent, const FName& InName)
{
    // 获取布料资产工厂类
    UClass* FactoryClass = UChaosClothAssetFactory::StaticClass();
    UChaosClothAssetFactory* Factory = NewObject<UChaosClothAssetFactory>(GetTransientPackage(), FactoryClass);
    
    if (Factory)
    {
        // 使用工厂创建资产
        UObject* NewAsset = Factory->FactoryCreateNew(
            UChaosClothAsset::StaticClass(),
            InParent,
            InName,
            RF_Public | RF_Standalone,
            nullptr, // Context
            GWarn     // FeedbackContext
        );
        
        return Cast<UChaosClothAsset>(NewAsset);
    }
    
    return nullptr;
}
```

## 模块依赖

从 Build.cs 分析，该插件依赖于以下非标准模块：

| 模块 | 用途 |
|---|---|
| `GeometryFramework` | 提供 `FDynamicMesh3` 等动态网格基础设施，是网格转换的核心。 |
| `Chaos` | Chaos 物理系统的核心模块，布料模拟的基础。 |
| `Cloth` | 旧的布料系统接口（可能用于兼容性）。 |
| `Dataflow` | 提供数据流图表框架，是布料资产编辑器节点系统的基础。 |
| `MeshConversion` | 网格格式转换工具。 |
| `ModelingComponents` | 提供建模工具组件，用于编辑器中的交互式网格编辑。 |
| `MeshModelingTools` | 提供具体的网格建模工具（如平滑、简化等）。 |

## 维护状态

### 近期更新

```
- 98d9917351a2 Cloth - Deprecated the old Clothing Simulation Interface and added a new updated class to replace it.
- e22e50aacc4e [Backout] - CL46169203 [FYI] kriss.gossart #rnx Original CL Desc ----------------------------------------------------------------- Cloth - Deprecated the old Clothing Simulation Interface and added a new updated class to replace it.
- 2c5b623c1f18 Cloth - Deprecated the old Clothing Simulation Interface and added a new updated class to replace it.
```

### 维护评价

- **活跃维护**：插件创建于 2022 年，属于较新的功能。最近的提交（2024年）集中在废弃旧的服装模拟接口并引入新的替代类，表明 Epic 正在积极重构和改进布料系统。
- **实验性状态**：`.uplugin` 中明确标记为 `IsBetaVersion: true`，且 `EnabledByDefault: false`，说明该插件仍处于实验阶段，API 和功能可能会发生变化。
- **推荐使用**：对于需要使用 Chaos 布料系统的新项目，**推荐使用**此插件，它是官方提供的标准工作流。但需注意其“实验性”标签，意味着在生产环境中使用需要做好应对未来变更的准备。对于维护旧的布料系统，应关注其废弃警告并计划迁移。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor)
- [官方文档]() (暂无)
- [测试用例]() (暂未在提供的信息中发现)