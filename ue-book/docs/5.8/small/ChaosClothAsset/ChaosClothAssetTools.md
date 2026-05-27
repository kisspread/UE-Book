# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | Chaos布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（布料资产模板、数据流节点、编辑器工具） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 插件旨在提供一个基于物理模拟、使用 Chaos 布料求解器的新一代布料资产工作流。它不仅仅是对传统 `UClothingAssetBase` 的简单替代，而是通过 **Dataflow** 技术提供了一个数据驱动、基于模式（Pattern）的布料创建与编辑流水线。

其核心解决的问题是：
1.  **取代传统的蒙皮权重工作流**：美术师不再需要在 Skeletal Mesh 上绘制复杂的蒙皮权重来定义布料。他们可以使用更直观的 2D 布片（Pattern）来设计布料，并自动转换为用于模拟的网格。
2.  **数据驱动与可扩展**：通过整合 Dataflow 插件，布料资产的创建过程被定义为一系列可定制的节点图（如切割、缝合、参数化）。这使得工作流高度可配置和可重用，并且更容易集成到自动化管线中。
3.  **提供完整的工具链**：该插件提供了从创建、编辑（在 ChaosClothAssetEditor 中）、转换（从传统布料资产）、到预览的全流程支持，是 Epic 官方力推的下一代布料解决方案。

## 使用场景

-   你需要为一个角色或物体创建动态、逼真的物理布料（如衣物、旗帜、窗帘、绳索）。
-   你希望使用直观的 2D 布片模式（Pattern）来设计布料，而不是在 3D 网格上绘制复杂的蒙皮权重。
-   你的项目需要将传统的布料资产（`UClothingAssetCommon`）迁移到新的 Chaos 布料资产系统。
-   你需要一个可扩展、数据驱动的布料创建流程，可以通过自定义 Dataflow 节点来满足特定的美术或技术需求。

## 蓝图用法

该插件的主要蓝图功能集成在编辑器工具中，用于资产创建和操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateClothAssetFromTemplate` | 从指定的 Dataflow 模板路径创建一个新的布料资产。适用于脚本化或自动化创建流程。 | `UChaosClothAssetFactory` |
| `GetClothComponent` | 用于在缩略图预览场景中获取关联的 `UChaosClothComponent`。 | `AChaosClothPreviewActor_Internal` (内部类) |

### 使用示例（蓝图描述）

1.  **从模板创建资产**：在蓝图函数库或编辑器 Utility Widget 中，可以调用 `UChaosClothAssetFactory::CreateClothAssetFromTemplate` 静态函数。你需要提供资产类（`UChaosClothAsset::StaticClass()`）、父包、名称以及一个指向 Dataflow 模板资产路径的指针。这可以绕过标准的资产创建对话框，实现程序化生成。
2.  **传统资产导出**：在内容浏览器中，对传统的 `UClothingAssetCommon` 资产右键，选择“Export to Chaos Cloth Asset”选项。这会触发 `UClothingAssetToChaosClothAssetExporter`，将旧资产转换为新的 `UChaosClothAsset`。

## C++ 用法

本模块提供了将布料资产数据转换为可编辑网格（`FDynamicMesh3`）以及维护两者之间映射关系的核心功能。

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"
```

### 基本用法

将布料资产或其子模式转换为用于编辑器显示和操作的 DynamicMesh。

*来源: Public/ChaosClothAsset/ClothPatternToDynamicMesh.h*

```cpp
// 假设你有一个指向 UChaosClothAsset 的指针 MyClothAsset
UChaosClothAsset* MyClothAsset = ...;

// 1. 准备一个空的 DynamicMesh
UE::Geometry::FDynamicMesh3 DynamicMesh;

// 2. 创建转换器
UE::Chaos::ClothAsset::FClothPatternToDynamicMesh Converter;

// 3. 执行转换：将指定 LOD 和整个布料资产（PatternIndex=INDEX_NONE）转换为 DynamicMesh
Converter.Convert(MyClothAsset, /*LODIndex*/0, /*PatternIndex*/INDEX_NONE,
                  UE::Chaos::ClothAsset::EClothPatternVertexType::Render,
                  DynamicMesh);

// 现在 DynamicMesh 包含了可用于预览或编辑的渲染网格数据
```

### 进阶用法

在进行网格编辑后，将修改映射回原始的布料数据。这需要结合 `FClothPatternToDynamicMeshMappingSupport`。

*来源: Public/ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h*

```cpp
// 假设已经通过 Converter.Convert() 得到了一个 DynamicMesh
UE::Geometry::FDynamicMesh3 EditedMesh = ...;

// 1. 创建映射支持对象，初始化时关联到包含映射属性的 DynamicMesh
UE::Chaos::ClothAsset::FClothPatternToDynamicMeshMappingSupport MappingSupport(EditedMesh);

// 2. 检查映射关系是否存在
if (MappingSupport.IsMappedVertexInSource())
{
    // 3. 遍历 EditedMesh 的顶点
    for (int32 VertexID = 0; VertexID < EditedMesh.MaxVertexID(); ++VertexID)
    {
        if (!EditedMesh.IsVertex(VertexID)) continue;

        // 4. 获取该编辑后顶点在原始布料数据中的对应顶点ID
        int32 OriginalVertexID = MappingSupport.GetOriginalVertexID(VertexID);

        // 5. 使用 OriginalVertexID 去访问或修改原始的布料集合数据 (FManagedArrayCollection)
        //    例如，获取原始位置、修改模拟权重等。
        //    FVector OriginalPosition = ClothCollection->GetPositions()[OriginalVertexID];
    }
}
```

## Demo 示例

一个最小示例，展示如何在 Actor 的 BeginPlay 中将布料资产的一个模拟模式转换为 DynamicMesh。

### MyClothAssetActor.h
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "ChaosClothAsset/ClothPatternVertexType.h"
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "GeometryScript/SceneUtilityFunctions.h"
#include "MyClothAssetActor.generated.h"

class UChaosClothAsset;

UCLASS()
class AMyClothAssetActor : public AActor
{
    GENERATED_BODY()

public:
    AMyClothAssetActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Cloth")
    TObjectPtr<UChaosClothAsset> ClothAsset;

protected:
    virtual void BeginPlay() override;

private:
    UE::Geometry::FDynamicMesh3 SimMesh;
    UE::Chaos::ClothAsset::FClothPatternToDynamicMesh MeshConverter;
};
```

### MyClothAssetActor.cpp
```cpp
#include "MyClothAssetActor.h"
#include "ChaosClothAsset/ClothAssetBase.h"

AMyClothAssetActor::AMyClothAssetActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyClothAssetActor::BeginPlay()
{
    Super::BeginPlay();

    if (ClothAsset && ClothAsset->GetNumLODs() > 0)
    {
        // 转换第一个LOD的第一个Sim模式（索引0）为3D模拟网格
        MeshConverter.Convert(
            ClothAsset,
            /*LODIndex*/0,
            /*PatternIndex*/0, // 指定模式索引，而非INDEX_NONE
            UE::Chaos::ClothAsset::EClothPatternVertexType::Sim3D,
            SimMesh
        );

        // 在此可以对 SimMesh 进行操作，例如打印顶点数
        UE_LOG(LogTemp, Log, TEXT("Converted Cloth Sim Mesh has %d vertices"), SimMesh.VertexCount());
    }
}
```

## 模块依赖

要使用 `ChaosClothAssetTools` 模块（特别是其转换和映射功能），你的模块需要链接以下库：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 提供布料资产核心类 (`UChaosClothAsset`) 和数据集合定义。 |
| `DynamicMesh` | 提供 `FDynamicMesh3` 等几何处理核心类。 |
| `GeometryScriptCore` | 提供几何脚本的基础设施，`ChaosClothAssetTools` 的转换逻辑与其深度集成。 |
| `ChaosCloth` | Chaos 布料模拟引擎，依赖的基础。 |
| `ClothingSystemRuntimeCommon` | 提供传统布料资产 (`UClothingAssetCommon`) 的类定义，用于迁移功能。 |

## 维护状态

该插件自 2024 年 3 月从实验性文件夹移出并标记为 Beta 版以来，正处于**非常活跃的开发和维护阶段**。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint reinstancing | 在蓝图重新实例化时保留布料组件的编辑器内模拟和资产属性。 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 优化并行布料模拟的等待点，从帧末尾移至可降级的任务组，提升性能。 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为布料资产实现骨骼映射刷新功能。 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 在复制或粘贴 Actor 后，刷新其编辑器内的资产别名引用。 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器的代码。 |

### 维护评价

-   **活跃度**：极高。Git 记录显示在最近一周内有密集的提交，内容涵盖功能增强（如属性保留、骨骼映射）、性能优化（模拟等待点调整）和代码清理。这表明插件正在快速迭代和完善中。
-   **稳定性**：作为“Beta”版本，可能仍存在边界情况或接口变动，但核心功能已相当稳固并被官方积极维护。
-   **推荐程度**：**强烈推荐**。对于新项目或希望采用最新布料工作流的项目，这是官方推荐的首选方案。对于现有项目，建议评估迁移传统布料资产的成本和收益。
-   **注意事项**：由于是较新的技术栈（Dataflow, DynamicMesh），学习曲线可能比传统蒙皮权重方式更陡峭。建议结合 ChaosClothAssetEditor 插件进行使用和学习。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
-   [官方文档] (暂无链接，可关注 Epic Games 官方文档和引擎更新说明)
-   [测试用例] (插件内部测试通常位于 `Engine/Plugins/ChaosClothAsset/Source/ChaosClothAssetTools/Tests/`，但需确认具体路径)