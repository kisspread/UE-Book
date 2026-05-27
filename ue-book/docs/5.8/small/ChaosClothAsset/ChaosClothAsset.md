# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 插件提供了一套完整的、基于数据驱动（Dataflow）的框架，用于创建、编辑和管理使用 Chaos 物理引擎进行模拟的布料资产。其核心思想是**基于图案（Pattern）的工作流**：设计师可以在 2D 空间中绘制布料裁片（模拟网格），然后将其映射到 3D 骨骼网格体上进行模拟和渲染。这比传统的直接蒙皮方式能产生更真实、交互性更强的布料动态效果。

该插件解决的是角色服装、披风、旗帜等需要高级布料物理模拟的创作需求。它整合了资产创建、物理属性设置、模拟与渲染管线，并通过 Dataflow 图表系统提供了灵活的非破坏性编辑能力。

## 使用场景

- 你需要为游戏角色创建逼真飘动的披风、斗篷或裙摆。
- 你需要模拟旗帜、窗帘等布料物体，并希望它们能与风或其他物理对象互动。
- 你的布料需要复杂的物理属性（如各向异性的拉伸和弯曲刚度）和高级功能（如基于图案的裁剪、缝合、形态目标）。
- 你希望使用可视化节点图（Dataflow）来程序化地构建和调整布料资产，而非纯粹的手工建模。

## 蓝图用法

此插件主要为 C++ 和 Dataflow 图表系统设计，**未发现可直接用于蓝图的 `BlueprintCallable` 或 `BlueprintReadWrite` 函数**。布料资产的创建和配置主要通过编辑器内的布料资产编辑器和 Dataflow 图表完成，其运行时数据通常由 `UChaosClothComponent` 在模拟过程中内部使用。

## C++ 用法

该插件的核心是通过 Facade（门面）模式操作 `FManagedArrayCollection` 中存储的布料数据。`FCollectionClothFacade` 是最核心的读写接口。

### 头文件引入

```cpp
#include "ChaosClothAsset/CollectionClothFacade.h"
#include "ChaosClothAsset/CollectionClothSimPatternFacade.h"
#include "ChaosClothAsset/CollectionClothFabricFacade.h"
#include "ChaosClothAsset/ClothGeometryTools.h"
```

### 基本用法：创建和初始化布料集合

以下示例演示了如何创建一个空的布料集合，并为其添加一个模拟图案和一个织物。

```cpp
// 来源：基于 CollectionClothFacade.h 和 CollectionClothSimPatternFacade.h 的 API 逻辑推断
TSharedRef<FManagedArrayCollection> ClothCollection = MakeShared<FManagedArrayCollection>();
FCollectionClothFacade ClothFacade(ClothCollection);

// 1. 初始化布料集合的 Schema（数据结构定义）
ClothFacade.DefineSchema();

// 2. 设置一些全局的模拟参数（可选）
ClothFacade.SetSolverGravity(FVector3f(0.f, 0.f, -980.f));
ClothFacade.SetSolverSubSteps(4);

// 3. 添加一个织物（Fabric），定义布料材质属性
int32 FabricIndex = ClothFacade.AddFabric();
FCollectionClothFabricFacade FabricFacade = ClothFacade.GetFabric(FabricIndex);
FabricFacade.Initialize(
    FCollectionClothFabricConstFacade::FAnisotropicData(100.f, 100.f, 100.f), // 弯曲刚度
    0.5f, // 屈曲比
    FCollectionClothFabricConstFacade::FAnisotropicData(50.f, 50.f, 50.f),   // 屈曲刚度
    FCollectionClothFabricConstFacade::FAnisotropicData(100.f, 100.f, 100.f),// 拉伸刚度
    0.35f, // 密度
    0.8f,  // 摩擦系数
    0.1f,  // 阻尼
    0.f,   // 压力
    0,     // 层级
    1.0f   // 碰撞厚度
);

// 4. 添加一个模拟图案（Sim Pattern）
int32 PatternIndex = ClothFacade.AddSimPattern();
FCollectionClothSimPatternFacade PatternFacade = ClothFacade.GetSimPattern(PatternIndex);

// 5. 为该图案设置模拟网格数据（2D 展开图和 3D 位置）
TArray<FVector2f> SimPositions2D = { FVector2f(0,0), FVector2f(1,0), FVector2f(0,1) }; // 2D 三角形
TArray<FVector3f> SimPositions3D = { FVector3f(0,0,0), FVector3f(10,0,0), FVector3f(0,10,0) }; // 3D 空间位置
TArray<FIntVector3> SimIndices = { FIntVector3(0, 1, 2) }; // 三角形索引

PatternFacade.Initialize(SimPositions2D, SimPositions3D, SimIndices, FabricIndex);

// 6. （可选）将模拟网格设置为渲染网格
FClothGeometryTools::CopySimMeshToRenderMesh(ClothCollection, /* 材质路径 */, true);
```

### 进阶用法：操作布料几何数据与权重图

`FClothGeometryTools` 提供了操作布料网格的静态工具函数。

```cpp
// 来源：基于 ClothGeometryTools.h 的 API 推断
TSharedRef<FManagedArrayCollection> ClothCollection = /* ... 已有布料集合 ... */;

// 1. 检查网格数据
bool bHasSim = FClothGeometryTools::HasSimMesh(ClothCollection);
bool bHasRender = FClothGeometryTools::HasRenderMesh(ClothCollection);

// 2. 翻转网格法线
FClothGeometryTools::ReverseMesh(ClothCollection, true, true, true, true, {}, {});

// 3. 重新计算渲染网格法线
FClothGeometryTools::RecalculateRenderMeshNormals(ClothCollection);

// 4. 生成运动学顶点集（例如，将最大距离权重小于阈值的顶点标记为静态）
TSet<int32> KinematicVertices = FClothGeometryTools::GenerateKinematicVertices3D(
    ClothCollection,
    FName(“MaxDistance”), // 权重图名称
    FVector2f(0.0f, 1.0f), // MaxDistance 值范围 [Min, Max]
    NAME_None, // 已有的运动学顶点集
    0.1f // 阈值
);

// 5. 清理并压缩网格（移除退化三角形等）
FClothGeometryTools::CleanupAndCompactMesh(ClothCollection);

// 6. 使用 FCollectionClothFacade 管理权重图
FCollectionClothFacade Facade(ClothCollection);
if (!Facade.HasWeightMap(FName(“Drag”)))
{
    Facade.AddWeightMap(FName(“Drag”));
}
TArrayView<float> DragWeights = Facade.GetWeightMap(FName(“Drag”));
// ... 填充 DragWeights 数据 ...
```

## Demo 示例

下面是一个最小化的示例，展示如何在 C++ 中创建一个简单的布料资产并设置其基本属性。

**ClothAssetDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ChaosClothAsset/CollectionClothFacade.h"

class FClothAssetDemo
{
public:
    void CreateSimpleClothAsset();
    
private:
    TSharedPtr<FManagedArrayCollection> ClothCollection;
    TUniquePtr<UE::Chaos::ClothAsset::FCollectionClothFacade> ClothFacade;
};
```

**ClothAssetDemo.cpp**
```cpp
#include "ClothAssetDemo.h"
#include "ChaosClothAsset/CollectionClothSimPatternFacade.h"
#include "ChaosClothAsset/CollectionClothFabricFacade.h"

using namespace UE::Chaos::ClothAsset;

void FClothAssetDemo::CreateSimpleClothAsset()
{
    // 1. 创建底层集合和门面
    ClothCollection = MakeShared<FManagedArrayCollection>();
    ClothFacade = MakeUnique<FCollectionClothFacade>(ClothCollection.ToSharedRef());
    ClothFacade->DefineSchema();

    // 2. 添加一个织物
    const int32 FabricIndex = ClothFacade->AddFabric();
    auto Fabric = ClothFacade->GetFabric(FabricIndex);
    Fabric.Initialize(
        FCollectionClothFabricConstFacade::FAnisotropicData(50.f),
        0.5f,
        FCollectionClothFabricConstFacade::FAnisotropicData(25.f),
        FCollectionClothFabricConstFacade::FAnisotropicData(80.f),
        0.3f, 0.9f, 0.05f, 0.f, 0, 0.8f
    );

    // 3. 添加一个模拟图案（一个简单的矩形）
    const int32 PatternIndex = ClothFacade->AddSimPattern();
    auto SimPattern = ClothFacade->GetSimPattern(PatternIndex);

    TArray<FVector2f> Positions2D;
    TArray<FVector3f> Positions3D;
    TArray<FIntVector3> Indices;

    // 创建四个顶点（两个三角形构成一个矩形）
    Positions2D.Append({FVector2f(0,0), FVector2f(1,0), FVector2f(1,1), FVector2f(0,1)});
    Positions3D.Append({FVector3f(0,0,10), FVector3f(10,0,10), FVector3f(10,10,0), FVector3f(0,10,0)});
    Indices.Append({FIntVector3(0,1,2), FIntVector3(0,2,3)});

    SimPattern.Initialize(Positions2D, Positions3D, Indices, FabricIndex);

    UE_LOG(LogTemp, Log, TEXT(“Simple cloth asset created with %d sim vertices and %d sim faces.”),
        ClothFacade->GetNumSimVertices3D(),
        ClothFacade->GetNumSimFaces());
}
```

## 模块依赖

使用 `ChaosClothAsset` 插件时，你的模块需要依赖以下独特的插件/模块。

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | 底层的 Chaos 布料物理模拟引擎，是此插件的核心依赖 |
| `GeometryCache` | 可能用于存储和回放缓布几何动画数据 |
| `Dataflow` | 提供节点图表系统，用于非破坏性地构建布料资产创建流程 |
| `ChaosClothAssetEngine` | （插件内部模块）包含布料资产的核心运行时类，如 `UChaosClothAsset` |

**无特殊依赖（仅标准 Core/Engine/Slate 等）**。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint | 修复了蓝图复制时布料组件属性丢失的问题 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 优化了并行布料模拟的同步点，提升性能 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为布料资产实现了骨骼映射刷新功能 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 改进了编辑器中复制粘贴Actor后资产别名的刷新逻辑 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理了布料资产转换器的代码 |

### 维护评价

该插件自2024年3月创建，至今约2年，属于较新的功能。从近期的Git提交记录来看，**维护非常活跃**，最近一个月内有多次功能性更新和优化（如模拟性能、编辑器工作流、资产管理）。提交内容聚焦于核心功能的完善和用户体验的提升，未见废弃标记。

- **优点**：更新频繁，Epic 官方维护，功能完整且深度集成 Dataflow 系统，代表了 UE 布料模拟的未来方向。
- **注意**：该插件默认未启用 (`EnabledByDefault=false`)，表明它可能仍处于 Beta 或快速迭代阶段，API 和数据结构可能存在变化。
- **推荐使用**：对于新项目中需要高级布料模拟的需求，**强烈推荐**使用此插件。它比旧的 Cloth 插件功能更强大、工作流更先进。使用时建议密切关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- 官方文档 (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset/Tests)