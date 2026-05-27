# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流模板） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 是 UE5 新一代布料系统的核心插件，基于 **Chaos 物理引擎**和 **模式（Pattern）驱动**的布料资产架构。它解决了传统布料系统（基于 APEX/NVIDIA Cloth）的几个核心痛点：

1. **模式化布料资产**：传统布料系统将布料数据绑定在骨骼网格体的 LOD 上，难以独立编辑和复用。ChaosClothAsset 引入独立的 `UChaosClothAsset` 资产，支持通过 Dataflow（数据流图）进行可视化编辑。
2. **从旧格式迁移**：提供从传统 `UClothingAssetCommon` 到 `UChaosClothAsset` 的完整迁移路径，包括右键导出和工厂转换。
3. **DynamicMesh 互转**：支持将布料 Pattern 转换为 Geometry 模块的 `FDynamicMesh3`，用于编辑器预览、缩略图渲染和几何操作。
4. **模拟与渲染分离**：通过 `EClothPatternVertexType`（Sim2D/Sim3D/Render）明确区分模拟顶点和渲染顶点的数据类型。

插件默认**未启用**，需要在项目设置中手动开启。它依赖 `ChaosCloth`（底层模拟引擎）、`GeometryCache` 和 `Dataflow`（数据流图编辑框架）三个前置插件。

## 使用场景

- 你在制作角色服装、旗帜、窗帘等柔性物体的物理模拟 → 用 ChaosClothAsset 创建独立的布料资产
- 你有旧版 APEX Cloth 或 UE 传统布料资产需要迁移到 Chaos 系统 → 右键旧资产 → "Export to Chaos Cloth Asset"
- 你需要通过数据流图（Dataflow）可视化编辑布料的约束、碰撞、风力等参数 → 配合 Dataflow 插件使用
- 你需要将布料 Pattern 导出为 DynamicMesh 进行几何分析或编辑 → 使用 `FClothPatternToDynamicMesh`

## 蓝图用法

本插件的 ChaosClothAssetTools 模块以 C++ 编辑器工具为主，不暴露蓝图节点。布料资产的蓝图交互（模拟控制、组件设置等）主要在 `ChaosCloth` 底层插件和 `ChaosClothAssetEngine` 模块中实现。

## C++ 用法

### 头文件引入

```cpp
// Tools 模块 - 转换与编辑器工具
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"
#include "ChaosClothAsset/ClothAssetFactory.h"
#include "ChaosClothAsset/LegacyClothingConverterProvider.h"
#include "ChaosClothAsset/ClothPatternVertexType.h"
```

### 基本用法 — 将布料 Pattern 转换为 DynamicMesh

```cpp
// 来源: Public/ChaosClothAsset/ClothPatternToDynamicMesh.h
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "ChaosClothAsset/ClothPatternVertexType.h"
#include "DynamicMesh/DynamicMesh3.h"

using namespace UE::Chaos::ClothAsset;

void ConvertClothPatternToMesh(const UChaosClothAsset* ClothAsset)
{
    UE::Geometry::FDynamicMesh3 DynamicMesh;
    FClothPatternToDynamicMesh Converter;

    // 转换整个布料资产的所有 Pattern 为焊接的 3D 模拟网格
    Converter.Convert(
        ClothAsset,
        /*LODIndex=*/ 0,
        /*PatternIndex=*/ INDEX_NONE,       // INDEX_NONE = 转换全部 Pattern
        EClothPatternVertexType::Sim3D,      // 3D 模拟顶点（焊接）
        DynamicMesh
    );

    // DynamicMesh 现在包含布料的几何数据，可用于预览、分析等
    UE_LOG(LogTemp, Log, TEXT("布料网格顶点数: %d, 三角面数: %d"),
        DynamicMesh.VertexCount(), DynamicMesh.TriangleCount());
}
```

### 基本用法 — 转换单个 Pattern

```cpp
// 来源: Public/ChaosClothAsset/ClothPatternToDynamicMesh.h
void ConvertSinglePattern(const UChaosClothAsset* ClothAsset, int32 PatternIndex)
{
    UE::Geometry::FDynamicMesh3 DynamicMesh;
    FClothPatternToDynamicMesh Converter;

    // 转换单个 Pattern 为非焊接的 2D 模拟网格
    Converter.Convert(
        ClothAsset,
        /*LODIndex=*/ 0,
        PatternIndex,
        EClothPatternVertexType::Sim2D,      // 2D 模拟顶点（非焊接）
        DynamicMesh,
        /*MaterialOffset=*/ INDEX_NONE,
        /*bFlip2DSimFaces=*/ false,
        /*bConvertWeightMaps=*/ true          // 将权重图转为 DynamicMesh 属性
    );
}
```

### 进阶用法 — 顶点/三角面 ID 映射追踪

```cpp
// 来源: Public/ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"

void TraceMappingIds(const UE::Geometry::FDynamicMesh3& DynamicMesh)
{
    // 创建映射支持对象
    FClothPatternToDynamicMeshMappingSupport MappingSupport(DynamicMesh);

    // 检查源数据是否包含映射顶点
    if (MappingSupport.IsMappedVertexInSource())
    {
        for (int32 Vid : DynamicMesh.VertexIndicesItr())
        {
            if (MappingSupport.IsMappedVertexID(Vid))
            {
                // 该顶点是从原始布料数据重映射而来的
                int32 OriginalVid = MappingSupport.GetOriginalVertexID(Vid);
                UE_LOG(LogTemp, Log, TEXT("DynamicMesh 顶点 %d -> 原始顶点 %d"), Vid, OriginalVid);
            }
        }
    }

    // 同样可以追踪三角面映射
    if (MappingSupport.IsMappedTriangleInSource())
    {
        for (int32 Tid : DynamicMesh.TriangleIndicesItr())
        {
            if (MappingSupport.IsMappedTriangleID(Tid))
            {
                int32 OriginalTid = MappingSupport.GetOriginalTriangleID(Tid);
                UE_LOG(LogTemp, Log, TEXT("DynamicMesh 三角面 %d -> 原始三角面 %d"), Tid, OriginalTid);
            }
        }
    }
}
```

### 进阶用法 — 附加自定义映射数据到 DynamicMesh

```cpp
// 来源: Public/ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h
void AttachCustomMappingData(UE::Geometry::FDynamicMesh3& Mesh)
{
    // 构建顶点映射数组：DynamicMesh VertexID -> 原始布料 VertexID
    TArray<int32> VertexToOriginalVertexIDMap;
    VertexToOriginalVertexIDMap.SetNum(Mesh.MaxVertexID());
    // ... 填充映射数据 ...

    // 附加顶点映射数据（要求 Mesh 已启用属性）
    bool bSuccess = FClothPatternToDynamicMeshMappingSupport::AttachVertexMappingData(
        VertexToOriginalVertexIDMap, Mesh);

    // 附加三角面映射数据
    TArray<int32> TriangleToOriginalTriangleIDMap;
    TriangleToOriginalTriangleIDMap.SetNum(Mesh.MaxTriangleID());
    // ... 填充映射数据 ...

    bSuccess = FClothPatternToDynamicMeshMappingSupport::AttachTriangleMappingData(
        TriangleToOriginalTriangleIDMap, Mesh);

    // 清理映射数据
    FClothPatternToDynamicMeshMappingSupport::RemoveAllMappingData(Mesh);
}
```

### 进阶用法 — 通过工厂创建布料资产

```cpp
// 来源: Public/ChaosClothAsset/ClothAssetFactory.h
#include "ChaosClothAsset/ClothAssetFactory.h"

UObject* CreateNewClothAsset(UObject* ParentPackage)
{
    // 方式 1：使用 Dataflow 模板创建（非模态，适合脚本/自动化流程）
    FString TemplatePath = TEXT("/Game/DataflowTemplates/MyClothTemplate");
    UObject* NewAsset = UChaosClothAssetFactory::CreateClothAssetFromTemplate(
        UChaosClothAsset::StaticClass(),
        ParentPackage,
        FName(TEXT("NewClothAsset")),
        RF_Public | RF_Standalone,
        &TemplatePath,
        /*bEmbedDataflow=*/ true   // 将数据流图嵌入资产
    );

    // 方式 2：不使用模板（无 Dataflow）
    UObject* SimpleAsset = UChaosClothAssetFactory::CreateClothAssetFromTemplate(
        UChaosClothAsset::StaticClass(),
        ParentPackage,
        FName(TEXT("SimpleClothAsset")),
        RF_Public | RF_Standalone,
        nullptr,                   // TemplatePath = nullptr 表示无模板
        false
    );

    return NewAsset;
}
```

### 进阶用法 — 旧版布料资产迁移（IModularFeature 接口）

```cpp
// 来源: Public/ChaosClothAsset/LegacyClothingConverterProvider.h
// 此接口由 ChaosClothAssetEditor 模块注册实现，ChaosClothAssetTools 通过 IModularFeatures 查找

#include "ChaosClothAsset/LegacyClothingConverterProvider.h"

bool MigrateLegacyClothing(const UClothingAssetCommon* LegacyAsset, UChaosClothAsset* TargetAsset)
{
    using namespace UE::Chaos::ClothAsset;

    // 查找已注册的转换器
    if (IModularFeatures::Get().IsModularFeatureImplemented(ILegacyClothingConverterProvider::FeatureName))
    {
        auto& Provider = static_cast<ILegacyClothingConverterProvider&>(
            IModularFeatures::Get().GetModularFeature(ILegacyClothingConverterProvider::FeatureName));
        return Provider.ConvertInto(LegacyAsset, TargetAsset);
    }

    // 无注册实现时回退到旧版导出逻辑
    return false;
}
```

## Demo 示例

### 布料资产转换工具类

```cpp
// ClothAssetToolExample.h
#pragma once

#include "CoreMinimal.h"
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"
#include "ChaosClothAsset/ClothPatternVertexType.h"
#include "DynamicMesh/DynamicMesh3.h"

class UChaosClothAsset;

class FClothAssetToolExample
{
public:
    /** 将布料资产的指定 LOD 和 Pattern 转换为 DynamicMesh，并打印映射信息 */
    static void ConvertAndLog(const UChaosClothAsset* ClothAsset, int32 LODIndex, int32 PatternIndex);
};
```

```cpp
// ClothAssetToolExample.cpp
#include "ClothAssetToolExample.h"
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"

using namespace UE::Chaos::ClothAsset;

void FClothAssetToolExample::ConvertAndLog(
    const UChaosClothAsset* ClothAsset, int32 LODIndex, int32 PatternIndex)
{
    if (!ClothAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("无效的布料资产"));
        return;
    }

    // 1. 转换布料为 DynamicMesh
    UE::Geometry::FDynamicMesh3 DynamicMesh;
    FClothPatternToDynamicMesh Converter;
    Converter.Convert(
        ClothAsset,
        LODIndex,
        PatternIndex,
        EClothPatternVertexType::Sim3D,
        DynamicMesh,
        /*MaterialOffset=*/ INDEX_NONE,
        /*bFlip2DSimFaces=*/ false,
        /*bConvertWeightMaps=*/ true
    );

    UE_LOG(LogTemp, Log, TEXT("转换完成: %d 顶点, %d 三角面"),
        DynamicMesh.VertexCount(), DynamicMesh.TriangleCount());

    // 2. 检查顶点映射
    FClothPatternToDynamicMeshMappingSupport MappingSupport(DynamicMesh);
    if (MappingSupport.IsMappedVertexInSource())
    {
        int32 MappedVertexCount = 0;
        for (int32 Vid : DynamicMesh.VertexIndicesItr())
        {
            if (MappingSupport.IsMappedVertexID(Vid))
            {
                MappedVertexCount++;
            }
        }
        UE_LOG(LogTemp, Log, TEXT("映射顶点数: %d / %d"),
            MappedVertexCount, DynamicMesh.VertexCount());
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("源数据未包含映射顶点信息"));
    }
}
```

## 模块依赖

从插件的 .uplugin 和模块结构推断，以下是该插件**独特**的依赖：

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 物理引擎的布料模拟核心 |
| `GeometryCache` | 几何缓存支持，用于存储布料模拟的中间结果 |
| `Dataflow` | 数据流图框架，用于可视化编辑布料参数 |
| `GeometryFramework` | DynamicMesh 相关几何操作（FClothPatternToDynamicMesh 依赖） |
| `MeshConversion` | 网格格式转换工具 |
| `SkeletalMeshDescription` | 骨骼网格描述，用于布料与骨骼网格体的互转 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint | 修复蓝图中布料组件的模拟状态和资产属性跨操作丢失的问题 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable | 优化并行布料模拟的等待时机，提升性能 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset | 实现 ClothAssetSKMClothingAsset 的骨骼映射刷新功能 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor | 修复复制/粘贴 Actor 后编辑器资产别名未刷新的问题 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |

### 维护评价

**活跃维护中**。

该插件创建于 2024 年 3 月，从 Experimental 文件夹迁出并标记为 Beta 状态。截至 2026 年 5 月仍有**持续且高频率**的更新（最近一周内有 5 次提交），内容涵盖功能实现（骨骼映射刷新）、Bug 修复（蓝图属性保持、编辑器别名刷新）和性能优化（并行模拟调度）。

注意事项：
- 插件仍处于 **Beta/实验性** 阶段（UChaosClothAssetFactory 标记为 Experimental）
- 默认**未启用**，需要在项目设置中手动开启
- 工厂类中部分功能（如 `CreateFromSkeletalMesh`、`CreateFromExistingCloth`）仍标记为 TODO
- 该插件是 UE5 Chaos 物理布料系统的**未来方向**，取代传统的 APEX Cloth 方案

**推荐使用**：如果你的新项目需要布料物理模拟，建议直接使用 ChaosClothAsset 而非旧版系统。如果是已有项目迁移，插件提供了完整的迁移工具链。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- 官方文档（暂无）