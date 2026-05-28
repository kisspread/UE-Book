# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 是基于 Chaos 物理引擎的**程序化布料资产系统**。与传统的顶点绑定布料不同，它采用**基于布样（Pattern）的工作流**——先在 2D 空间定义布片形状和缝合关系，再映射到 3D 模型上进行物理模拟。

这个插件解决了以下问题：
- **布料数据结构化管理**：通过 `FManagedArrayCollection` 统一存储 2D/3D 模拟网格、渲染网格、材质、骨骼权重等所有布料数据
- **布样工作流**：支持多个 Sim Pattern 和 Render Pattern，每个 Pattern 独立管理顶点和面片
- **物理参数分组**：Fabric（面料）系统将弯曲刚度、拉伸刚度、密度等参数抽象为独立对象，多个 Pattern 可共享同一面料
- **缝合系统**：通过 Seam/Stitch 机制管理布片之间的缝合关系
- **代理变形器**：将模拟网格结果映射到渲染网格，支持多种变形影响权重

**注意**：此插件默认未启用（`EnabledByDefault=false`），且标记为实验性/Beta 版本。从 Experimental 文件夹迁移而来。

## 使用场景

- 你需要基于物理的衣物模拟，且希望用布样（Pattern）方式定义布料拓扑 → 用 ChaosClothAsset
- 你在开发角色换装系统，需要程序化生成或修改布料资产 → 用 ChaosClothAsset 的 Facade API
- 你需要自定义布料的物理参数（弯曲、拉伸、密度等）并通过 Dataflow 节点进行编辑 → 配合 Dataflow 插件使用
- 你需要将多种面料参数组合并分配给不同布片 → 用 Fabric 系统

## 蓝图用法

此插件为纯 C++ 数据层 API，**不包含 BlueprintCallable 函数**。所有操作均通过 C++ Facade 接口完成。编辑器端的蓝图资产操作由 ChaosClothAssetTools（Editor 模块）和 Dataflow 节点提供，但这些属于编辑器扩展，不暴露为运行时蓝图节点。

## C++ 用法

### 核心架构

插件采用 **Facade 模式** 封装 `FManagedArrayCollection`，提供类型安全的数据访问：

```
FConstClothCollection / FClothCollection     ← 底层数据容器
        ↑
FCollectionClothConstFacade / FCollectionClothFacade  ← 高层 Facade
        ├── FCollectionClothSimPatternFacade      ← 模拟 Pattern
        ├── FCollectionClothRenderPatternFacade    ← 渲染 Pattern
        ├── FCollectionClothFabricFacade           ← 面料参数
        ├── FCollectionClothSeamFacade             ← 缝合
        ├── FCollectionClothSimMorphTargetFacade   ← 变形目标
        └── FCollectionClothSimAccessoryMeshFacade ← 配饰网格
```

### 头文件引入

```cpp
#include "ChaosClothAsset/CollectionClothFacade.h"
#include "ChaosClothAsset/ClothGeometryTools.h"
#include "ChaosClothAsset/CollectionClothSelectionFacade.h"
```

### 基本用法：创建布料集合

```cpp
// 来源: CollectionClothFacade.h
using namespace UE::Chaos::ClothAsset;

// 创建底层集合
TSharedRef<FManagedArrayCollection> ClothCollection = MakeShared<FManagedArrayCollection>();

// 通过 Facade 定义 Schema 并设置数据
FCollectionClothFacade ClothFacade(ClothCollection);
ClothFacade.DefineSchema();

// 设置资产引用
ClothFacade.SetPhysicsAssetSoftObjectPathName(FSoftObjectPath(TEXT("/Game/Characters/PhysicsAsset")));
ClothFacade.SetSkeletalMeshSoftObjectPathName(FSoftObjectPath(TEXT("/Game/Characters/SkeletalMesh")));
ClothFacade.SetReferenceBoneName(FName(TEXT("pelvis")));
```

### 基本用法：设置模拟参数

```cpp
// 来源: CollectionClothFacade.h, CollectionClothFabricFacade.h

// 设置求解器参数
ClothFacade.SetSolverGravity(FVector3f(0.0f, 0.0f, -980.665f));
ClothFacade.SetSolverAirDamping(0.035f);
ClothFacade.SetSolverSubSteps(1);
ClothFacade.SetSolverTimeStep(0.033f);

// 添加面料并设置物理参数
int32 FabricIndex = ClothFacade.AddFabric();
FCollectionClothFabricFacade FabricFacade = ClothFacade.GetFabric(FabricIndex);
FabricFacade.Initialize(
    FCollectionClothFabricConstFacade::FAnisotropicData(100.0f, 100.0f, 100.0f),  // BendingStiffness
    0.5f,     // BucklingRatio
    FCollectionClothFabricConstFacade::FAnisotropicData(50.0f, 50.0f, 50.0f),     // BucklingStiffness
    FCollectionClothFabricConstFacade::FAnisotropicData(100.0f, 100.0f, 100.0f),  // StretchStiffness
    0.35f,    // Density
    0.8f,     // Friction
    0.1f,     // Damping
    0.0f,     // Pressure
    INDEX_NONE, // Layer
    1.0f      // CollisionThickness
);
```

### 进阶用法：构建模拟网格

```cpp
// 来源: CollectionClothSimPatternFacade.h, CollectionClothSeamFacade.h
using namespace UE::Chaos::ClothAsset;

// 创建模拟 Pattern
FCollectionClothFacade ClothFacade(ClothCollection);
int32 PatternIndex = ClothFacade.AddSimPattern();
FCollectionClothSimPatternFacade SimPattern = ClothFacade.GetSimPattern(PatternIndex);

// 使用 2D/3D 位置和索引初始化 Pattern
TArray<FVector2f> Positions2D = { FVector2f(0,0), FVector2f(1,0), FVector2f(0,1) };
TArray<FVector3f> Positions3D = { FVector3f(0,0,0), FVector3f(10,0,0), FVector3f(0,10,0) };
TArray<FIntVector3> Indices = { FIntVector3(0, 1, 2) };
SimPattern.Initialize(Positions2D, Positions3D, Indices, FabricIndex);

// 添加缝合
int32 SeamIndex = ClothFacade.AddSeam();
FCollectionClothSeamFacade SeamFacade = ClothFacade.GetSeam(SeamIndex);
TArray<FIntVector2> Stitches = { FIntVector2(0, 3), FIntVector2(1, 4) }; // 2D顶点对
SeamFacade.Initialize(Stitches);
```

### 进阶用法：使用几何工具

```cpp
// 来源: ClothGeometryTools.h
using namespace UE::Chaos::ClothAsset;

// 从 DynamicMesh 构建模拟网格
TSharedRef<FManagedArrayCollection> ClothCollection = MakeShared<FManagedArrayCollection>();
UE::Geometry::FDynamicMesh3 DynamicMesh;
// ... 加载或构建 DynamicMesh ...

TMap<int, int32> VertexMap;
FClothGeometryTools::BuildSimMeshFromDynamicMeshes(
    ClothCollection,
    DynamicMesh2D, DynamicMesh3D,
    PatternIndexLayerId,    // PolyGroup 层 ID
    true,                   // 传输权重贴图
    true,                   // 传输蒙皮数据
    false,                  // 追加模式
    VertexMap
);

// 检查并清理网格
FClothGeometryTools::CleanupAndCompactMesh(ClothCollection);

// 将模拟网格复制为渲染网格
FClothGeometryTools::CopySimMeshToRenderMesh(
    ClothCollection,
    FSoftObjectPath(TEXT("/Game/Materials/ClothMaterial")),
    true  // 单一渲染 Pattern
);

// 应用代理变形器
FClothGeometryTools::ApplyProxyDeformer(ClothCollection, false);
```

## Demo 示例

### 最小示例：创建带单个 Pattern 的布料资产

```cpp
// ChaosClothExample.h
#pragma once

#include "CoreMinimal.h"
#include "ChaosClothAsset/CollectionClothFacade.h"

class FChaosClothExample
{
public:
    /** 创建一个包含单个模拟 Pattern 和面料的布料集合 */
    static TSharedRef<FManagedArrayCollection> CreateSimpleClothCollection();
};
```

```cpp
// ChaosClothExample.cpp
#include "ChaosClothExample.h"

using namespace UE::Chaos::ClothAsset;

TSharedRef<FManagedArrayCollection> FChaosClothExample::CreateSimpleClothCollection()
{
    TSharedRef<FManagedArrayCollection> Collection = MakeShared<FManagedArrayCollection>();

    // 1. 初始化 Facade 并定义 Schema
    FCollectionClothFacade ClothFacade(Collection);
    ClothFacade.DefineSchema();

    // 2. 设置资产引用
    ClothFacade.SetPhysicsAssetSoftObjectPathName(FSoftObjectPath(TEXT("/Game/Char/PhysAsset")));
    ClothFacade.SetSkeletalMeshSoftObjectPathName(FSoftObjectPath(TEXT("/Game/Char/SK")));
    ClothFacade.SetReferenceBoneName(FName(TEXT("root")));

    // 3. 创建面料
    const int32 FabricIdx = ClothFacade.AddFabric();
    auto Fabric = ClothFacade.GetFabric(FabricIdx);
    Fabric.Initialize(
        FCollectionClothFabricConstFacade::FAnisotropicData(100.0f, 100.0f, 100.0f),
        0.5f,   // BucklingRatio
        FCollectionClothFabricConstFacade::FAnisotropicData(50.0f),
        FCollectionClothFabricConstFacade::FAnisotropicData(100.0f),
        0.35f, 0.8f, 0.1f, 0.0f, INDEX_NONE, 1.0f
    );

    // 4. 创建模拟 Pattern（一个三角形）
    const int32 PatternIdx = ClothFacade.AddSimPattern();
    auto SimPattern = ClothFacade.GetSimPattern(PatternIdx);

    TArray<FVector2f> Positions2D = {
        FVector2f(0.0f, 0.0f),
        FVector2f(50.0f, 0.0f),
        FVector2f(0.0f, 50.0f)
    };
    TArray<FVector3f> Positions3D = {
        FVector3f(0.0f, 0.0f, 0.0f),
        FVector3f(50.0f, 0.0f, 0.0f),
        FVector3f(0.0f, 50.0f, 0.0f)
    };
    TArray<FIntVector3> Indices = { FIntVector3(0, 1, 2) };

    SimPattern.Initialize(Positions2D, Positions3D, Indices, FabricIdx);

    return Collection;
}
```

## 模块依赖

### ChaosClothAsset (Runtime)

从 `ChaosClothAsset.Build.cs` 分析，此模块为纯数据层，无特殊依赖（仅标准 Core/Engine/Slate 等）。

### ChaosClothAssetEngine (Runtime)

依赖 Chaos 物理引擎相关模块。

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料物理模拟核心 |
| `ChaosSolverEngine` | Chaos 物理求解器 |
| `Chaos` | Chaos 物理引擎基础 |
| `Dataflow` | Dataflow 节点图系统 |

### ChaosClothAssetTools (Editor)

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 网格几何处理工具 |
| `MeshDescription` | MeshDescription 网格格式支持 |
| `DynamicMesh` | 动态网格操作 |
| `ChaosClothAsset` | 本插件的运行时数据层 |
| `ChaosClothAssetEngine` | 本插件的引擎层 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Bluepri | 蓝图中保留布料组件的模拟编辑器开关和资产属性 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 优化并行布料模拟的同步等待时机 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 实现布料资产的骨骼映射刷新功能 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 复制/粘贴 Actor 后刷新编辑器资产别名 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |

### 维护评价

- **创建时间**：2024-03-22，约 2 年前，属于较新的插件
- **近期活跃度**：最近一周内有多次提交，维护非常活跃
- **版本状态**：Beta 版本（从 Experimental 迁移），默认未启用
- **API 稳定性**：存在多处 `UE_DEPRECATED` 标记（如 5.4、5.5、5.6、5.7 各版本），说明 API 仍在快速迭代
- **代码质量**：Facade 模式设计清晰，数据与行为分离良好

**综合评价**：这是一个**活跃开发中的 Beta 阶段插件**。API 在持续演化，适合跟进最新 UE 版本的项目使用，但生产环境需谨慎——未来版本可能继续调整接口。推荐在需要程序化布料数据处理的场景下使用，传统的顶点绑定布料工作流仍建议使用标准 Cloth 模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- [官方文档](https://docs.unrealengine.com/)（无专门文档页）