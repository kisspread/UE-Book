# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 混沌肉体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，Dataflow节点） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是一个实验性的物理模拟插件，用于模拟具有体积和内部结构的“肉体”或软体物理效果。它扩展了 Unreal Engine 的 Chaos 物理系统，提供了基于四面体网格的有限元分析能力，用于模拟肌肉、脂肪、内脏等生物组织或橡胶、果冻等软材料的形变、撕裂和断裂效果。它解决了传统基于表面网格（如布料）无法模拟物体内部体积变化和复杂断裂行为的问题。

**核心价值**：该插件允许用户将静态或骨骼网格体转换为由四面体单元构成的体积网格，并应用基于物理的材料属性和力（如重力、肌肉收缩力）进行高保真的肉体模拟，适用于游戏、影视和仿真领域中需要高真实度生物/软体物理表现的场景。

## 使用场景

- **游戏开发**：制作角色受击时肉质抖动、模拟软体生物（如史莱姆、章鱼）的运动。
- **影视/虚拟制片**：创建用于特写镜头的超高精度物理模拟效果，如伤口、肌肉收缩。
- **医学仿真/科学研究**：作为有限元分析工具，模拟生物力学实验或手术规划。
- **物理研发**：测试新的材料模型、求解器算法或破坏系统。

## 蓝图用法

此插件的核心功能主要通过 **Dataflow（数据流）** 系统和 **GeometryCollection（几何体集合）** 资产实现，而非传统的蓝图函数节点。用户通常在 **Dataflow 编辑器** 中连接节点来创建和控制肉体模拟。

### 核心数据流节点（已废弃）

**重要提示**：以下列出的节点在 `ChaosFleshDeprecatedNodes` 模块中，并已在 UE 5.4 中被标记为 **Deprecated（废弃）**。新项目应寻找替代方案。这些节点曾用于构建从网格体导入、生成四面体并设置约束的工作流。

| 节点 | 说明 | 所在模块 |
|---|---|---|
| `ImportGEO` | 从 `.geo` 文件（Houdini 等 DCC 软件导出）导入四面体网格和自定义变量。 | `ChaosFleshDeprecatedNodes` |
| `GenerateTetrahedralCollection` | 从输入的 `StaticMesh` 或 `SkeletalMesh` 生成四面体网格。支持 `IsoStuffing` 和 `TetWild` 等算法。 | `ChaosFleshDeprecatedNodes` |
| `TetGrid` | 构建一个规则的四面体网格，用于简单测试或作为基础形状。 | `ChaosFleshDeprecatedNodes` |
| `KinematicTetrahedralBindings` | 将 `SkeletalMesh` 的骨骼动画绑定到四面体网格上，实现骨骼驱动的肉体动画或约束。 | `ChaosFleshDeprecatedNodes` |
| `KinematicOriginInsertionInitialization` | 初始化运动学约束的起点和插入点，用于模拟肌肉的收缩。 | `ChaosFleshDeprecatedNodes` |
| `ExtractGEOInt`, `ExtractGEOIntVector`, `ExtractGEOFloatVector` | 辅助节点，用于从 `ImportGEO` 节点的输出中提取特定名称的自定义变量。 | `ChaosFleshDeprecatedNodes` |

### 使用示例（数据流工作流描述）

一个典型（已废弃）的肉体模拟数据流图可能如下：
1.  **导入或生成**：使用 `ImportGEO` 节点导入外部四面体模型，或使用 `GenerateTetrahedralCollection` 节点从一个 `StaticMesh`（如一个立方体）生成。
2.  **设置约束**：使用 `KinematicTetrahedralBindings` 节点将四面体网格绑定到一个 `SkeletalMesh` 的骨骼上，以便用动画驱动。
3.  **输出**：将处理好的 `Collection`（几何体集合）输出给 **Flesh Actor** 或其他消耗实体。

## C++ 用法

**重要**：由于 `ChaosFleshDeprecatedNodes` 模块中的节点均被标记为废弃，以下示例仅用于说明其API结构和历史用法，**不推荐在新代码中使用**。

### 头文件引入

```cpp
#include "ChaosFleshDeprecatedNodes/ChaosFleshImportGEO.h"
#include "ChaosFleshDeprecatedNodes/ChaosFleshCreateTetrahedralCollectionNode.h"
```

### 基本用法：操作废弃的数据流节点

数据流节点通常是 `USTRUCT`，并继承自 `FDataflowNode`。它们通过 `Evaluate` 函数执行计算。以下代码展示了如何程序化地配置一个 `FImportGEO` 节点，但实际使用中通常在Dataflow编辑器里可视化地连接它们。

```cpp
// 注意：以下代码仅作历史参考，这些节点已被废弃。
#include "Dataflow/DataflowNode.h"

// 创建一个 ImportGEO 节点实例
FImportGEO ImportNode(UE::Dataflow::FNodeParameters());
ImportNode.Filename.FilePath = TEXT("D:/assets/muscle.geo");
ImportNode.bImportTetrahedronMesh = true;
ImportNode.bDiscardInteriorTriangles = false;

// 手动触发计算（在Dataflow上下文中通常由图自动管理）
// UE::Dataflow::FContext Context;
// ImportNode.Evaluate(Context, nullptr);

// 访问输出
const FGEOMapStringInt& IntVars = ImportNode.IntVarsOutput;
TArray<float> FloatArray;
if (const TArray<float>* Found = ImportNode.FloatVectorVarsOutput.FloatVectorVars.Find(TEXT("density")))
{
    FloatArray = *Found;
}
```

### 进阶用法：集成到几何体处理流水线

此插件的核心类之一是 `FFleshCollection`（继承自 `FManagedArrayCollection`），它是存储四面体网格、顶点位置、约束等所有模拟数据的容器。下面的伪代码展示了如何在C++中直接创建和操作一个简单的肉体几何体。

```cpp
// 包含肉体核心类型
#include "ChaosFlesh/ChaosFleshCollection.h"

// 假设有一个转换函数从StaticMesh生成FDynamicMesh3
TUniquePtr<FFleshCollection> CreateFleshFromDynamicMesh(const UE::Geometry::FDynamicMesh3& DynamicMesh)
{
    // 创建肉体集合
    TUniquePtr<FFleshCollection> FleshCollection = MakeUnique<FFleshCollection>();

    // 此处为简化。实际流程复杂，通常调用如 GeometryCollectionToDynamicMesh 等工具函数，
    // 或使用 TetWild 等库进行四面体化。
    // 例如：
    // Chaos::Flesh::GenerateTetrahedralMesh(DynamicMesh, *FleshCollection, TetMeshingMethod::TetWild);

    // 设置材料属性（例如杨氏模量、泊松比）
    // FleshCollection->SetAttribute(TEXT("YoungsModulus"), 1e5);
    // FleshCollection->SetAttribute(TEXT("PoissonsRatio"), 0.45);

    return FleshCollection;
}
```

## 模块依赖

从 `Build.cs` 文件分析，该插件的依赖关系如下。为了清晰，已省略常见的Core、Engine等基础模块。

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理系统核心，提供底层物理求解器和约束系统。 |
| `ChaosSolverEngine` | Chaos 求解器运行时引擎。 |
| `GeometryFramework` | 提供动态网格体（`UDynamicMesh`）等几何处理框架。 |
| `GeometryProcessing` | 提供网格体处理、布尔运算、四面体化（Tetrahedralization）等算法。 |
| `Dataflow` | 核心数据流执行框架，所有 `FDataflowNode` 的基础。 |
| `DataflowEngine` | 数据流与引擎资产（如 `UDataflowAsset`）的集成。 |
| `MeshConversion` | 在不同网格体格式（如 `UDynamicMesh`, `FMeshDescription`, `FStaticMeshLODResources`）之间转换。 |
| `ModelingComponents` | 提供交互式建模组件，可能用于编辑器中的肉体网格预览和交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-12 | `981bc9da` | Dataflow: | 对数据流功能进行了修改。 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理了肉体纤维场生成节点的代码。 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复了MaskBuffer从OffsetsBuffer赋值NumMaskBuffer的错误。 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 从肉体资产中废弃了StaticMesh属性。 |

### 维护评价

**活跃维护，但功能定位已变**。该插件仍在被Epic Games积极维护和迭代，从近期密集的提交记录（尤其集中在2026年5月）可以看出，团队仍在投入开发。

然而，必须注意两个关键点：
1.  **核心模块已废弃**：`ChaosFleshDeprecatedNodes` 模块中的旧版数据流工作流节点在 UE 5.4 中已被废弃。这表明 Epic 可能正在将功能整合到 `ChaosFleshNodes` 和 `ChaosFleshEngine` 等新模块中，或引入了全新的API。
2.  **默认禁用**：插件默认不启用，且标记为 **实验性**，说明其API和功能仍可能不稳定，未来会有重大变更。

**建议**：对于新项目，**不应依赖** `ChaosFleshDeprecatedNodes` 模块中的任何节点。应关注 `ChaosFleshNodes` 和 `ChaosFleshEngine` 中的最新功能。密切关注官方更新日志，以了解肉体模拟工作流的最新官方推荐路径。此插件适合对前沿物理技术进行原型验证和研究，但用于生产项目需谨慎评估其稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh/Tests) (如果存在)
- [官方文档]() (暂无)