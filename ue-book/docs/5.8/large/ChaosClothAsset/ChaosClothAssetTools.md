# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Chaos布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

`ChaosClothAsset` 插件是 Epic 为 Chaos 物理引擎提供的新一代布料资产系统。它旨在替代或补充传统的基于骨骼的布料模拟（`ClothAsset`），提供一个以 **2D 布料图案（Pattern）** 为核心、使用 **Chaos Cloth 物理模拟** 的完整工作流。

**核心解决的问题**：
1.  **更真实的物理模拟**：利用 Chaos 物理引擎，提供更高级的布料动力学模拟效果。
2.  **图案化工作流**：允许美术师从 2D 图案（如服装纸样）开始设计布料，然后自动转换为可模拟的 3D 网格，使服装设计更直观、更符合现实工艺。
3.  **节点图驱动**：深度集成了 `Dataflow` 插件，布料资产的创建、编辑和属性控制都通过可视化的节点图（Dataflow Graph）完成，提供了极高的灵活性和可定制性。

## 使用场景

*   **游戏开发**：为角色（无论是玩家角色还是 NPC）创建逼真的衣物、盔甲、旗帜等布料模拟。
*   **影视动画**：在过场动画或实时渲染中，需要高质量、可控的布料动态效果。
*   **虚拟时尚/试衣**：需要基于真实服装版型进行快速虚拟布料模拟和展示。

## 蓝图用法

此插件主要通过编辑器扩展和工厂类提供蓝图可用的创建与转换功能，其核心模拟逻辑更多在运行时 C++ 层面驱动。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Cloth Asset from Template` | 非模态创建布料资产，可指定 Dataflow 模板，用于脚本或自动化流程 | `UChaosClothAssetFactory` |
| `Export` | 将传统布料资产（`UClothingAssetCommon`）导出为 Chaos 布料资产 | `UClothingAssetToChaosClothAssetExporter` |

### 使用示例（蓝图描述）

1.  **在编辑器中创建**：通常，你会在内容浏览器右键 -> “材质与纹理” -> “Chaos 布料资产”来创建一个新的资产。这会调用 `UChaosClothAssetFactory` 并打开 Dataflow 节点编辑器。
2.  **自动化创建**：在编辑器工具蓝图或脚本中，你可以获取 `UChaosClothAssetFactory` 的类，然后调用其静态函数 `CreateClothAssetFromTemplate`，传入指定的模板路径，即可在后台创建资产，适用于批量处理。

## C++ 用法

### 头文件引入

```cpp
// 用于网格转换和映射支持
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"

// 用于资产工厂
#include "ChaosClothAsset/ClothAssetFactory.h"
```

### 基本用法

将布料资产或布料集合中的一个图案转换为 `FDynamicMesh3`，以便进行几何处理。

```cpp
// 来源：基于 Public/ChaosClothAsset/ClothPatternToDynamicMesh.h
#include "ChaosClothAsset/ClothPatternToDynamicMesh.h"

void ConvertClothPatternToDynamicMesh(UChaosClothAsset* ClothAsset)
{
    using namespace UE::Chaos::ClothAsset;
    FClothPatternToDynamicMesh Converter;

    // 转换整个布料资产的所有图案（LOD 0）为焊接的 3D 仿真网格
    UE::Geometry::FDynamicMesh3 MeshOut;
    Converter.Convert(
        ClothAsset,
        0, // LODIndex
        INDEX_NONE, // PatternIndex, INDEX_NONE 表示全部
        EClothPatternVertexType::Sim3D,
        MeshOut
    );

    // 现在可以使用 MeshOut 进行其他几何操作...
}
```

### 进阶用法

使用 `FClothPatternToDynamicMeshMappingSupport` 在处理后的 `FDynamicMesh3` 和原始布料数据之间建立 ID 映射关系，这对于将修改结果反馈回布料系统至关重要。

```cpp
// 来源：基于 Public/ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h
#include "ChaosClothAsset/ClothPatternToDynamicMeshMappingSupport.h"

void ProcessClothMeshAndMapBack(const TSharedRef<const FManagedArrayCollection> ClothCollection)
{
    using namespace UE::Chaos::ClothAsset;
    FClothPatternToDynamicMesh Converter;
    UE::Geometry::FDynamicMesh3 Mesh;

    // 1. 转换，并确保启用属性以存储映射信息
    Converter.Convert(ClothCollection, 0, EClothPatternVertexType::Sim3D, Mesh, false);

    // 2. 创建映射支持对象
    FClothPatternToDynamicMeshMappingSupport MappingSupport(Mesh);

    // 3. 检查数据是否有映射信息
    if (MappingSupport.IsMappedVertexInSource())
    {
        // 4. 对 DynamicMesh 进行一些处理（例如平滑、变形）
        // ...

        // 5. 使用映射获取原始布料数据中对应的顶点索引
        for (int32 DynamicMeshVertexID = 0; DynamicMeshVertexID < Mesh.VertexCount(); ++DynamicMeshVertexID)
        {
            int32 OriginalClothVertexID = MappingSupport.GetOriginalVertexID(DynamicMeshVertexID);
            // 使用 OriginalClothVertexID 来更新原始 ClothCollection 中对应顶点的位置或其他数据...
        }
    }
}
```

## Demo 示例

一个创建布料资产工厂并生成新资产的最小 C++ 示例。

```cpp
// ClothAssetDemo.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ClothAssetDemo.generated.h"

UCLASS()
class UClothAssetDemo : public UObject
{
    GENERATED_BODY()
public:
    /** 创建一个基础的 Chaos 布料资产 */
    UFUNCTION(BlueprintCallable, Category = "Cloth Demo")
    static UObject* CreateDemoClothAsset(UObject* InOuter, const FString& AssetName);
};

// ClothAssetDemo.cpp
#include "ClothAssetDemo.h"
#include "ChaosClothAsset/ClothAssetFactory.h" // 包含工厂头文件

UObject* UClothAssetDemo::CreateDemoClothAsset(UObject* InOuter, const FString& AssetName)
{
    // 获取布料资产工厂类
    UClass* FactoryClass = UChaosClothAssetFactory::StaticClass();
    UFactory* Factory = GetMutableDefault<UChaosClothAssetFactory>();

    if (Factory && InOuter)
    {
        // 调用工厂的创建方法
        return Factory->FactoryCreateNew(
            UChaosClothAsset::StaticClass(), // 通常工厂内部知道具体资产类，这里示意
            InOuter,
            FName(*AssetName),
            RF_Public | RF_Standalone,
            nullptr, // Context
            GWarn     // 警告反馈上下文
        );
    }
    return nullptr;
}
```

## 模块依赖

要使用 `ChaosClothAssetTools` 模块（或 `ChaosClothAsset` 模块）的功能，你的项目模块需要依赖以下独特的模块（基于插件声明的插件依赖推断）：

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料物理模拟的核心运行时库。 |
| `GeometryCache` | 几何缓存系统，布料资产可能用于缓存模拟结果。 |
| `Dataflow` | 可视化节点图编辑框架，布料资产的编辑器和资产逻辑严重依赖于此。 |

**注意**：对于编辑器工具功能（如资产工厂），你还需要依赖 `ChaosClothAssetTools` 模块。无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint | 在蓝图中编辑布料组件时，保留 `bSimulateInEditor` 和资产属性设置。 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 将并行布料模拟的等待任务从帧末移到 `TG_LastDemotable` 任务组，优化性能调度。 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为 `ClothAssetSKMClothingAsset` 实现了 `RefreshBoneMapping` 函数，修复骨骼映射问题。 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 在复制或粘贴带有布料资产的 Actor 后，刷新编辑器专用的资产别名。 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理 Chaos 布料资产转换器代码。 |

### 维护评价

**活跃维护**。该插件创建于 2024 年 3 月，虽然版本号仍为 0.1 且标记为实验性/Beta，但从近期的 git 记录来看，**维护非常活跃**。最近一次提交在 2026 年 5 月，且提交内容涉及功能完善（映射支持、编辑器工作流优化）、性能改进（模拟任务调度）和 Bug 修复。这表明 Epic 内部正在积极开发和打磨此系统。

**建议**：此插件代表 UE 布料系统的未来方向，技术先进且处于快速迭代中。它非常适合愿意投入学习新工作流并追求最高布料模拟质量的项目。但由于其“实验性”状态和复杂的节点图工作流，不建议在追求稳定性的生产项目中立即全面替换旧系统，可先用于原型或特定高需求角色。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- [官方文档]() （暂无）
- [测试用例]() （暂无明确路径，通常位于 `Engine/Plugins/ChaosClothAsset/Tests` 或 `Engine/Tests` 下）