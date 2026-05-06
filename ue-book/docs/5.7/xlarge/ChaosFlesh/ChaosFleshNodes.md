# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 肉体物理模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Dataflow节点资产） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh) | |

---

## 用途

ChaosFlesh 是 UE5 Chaos 物理系统的一个扩展模块，专注于**软体/肉体物理模拟**。它允许艺术家和开发者通过 Dataflow 编辑图来定义肉体变形体（Flesh Asset），包括：

- 从输入几何体（静态网格、骨骼网格）生成**四面体网格**（Tetrahedral Mesh）
- 计算**肌肉纤维方向场**（Fiber Field）用于各向异性形变
- 创建**运动学约束**（Kinematic Constraints）、**位置目标绑定**（Position Target Binding）等
- 生成**骨骼绑定**（Skeletal Bindings）以使肉体跟随骨架动画
- 集成 **Chaos 求解器**进行实时或离线物理模拟

该模块解决的核心问题：**为角色肉体变形、内脏模拟、肌肉驱动等需要复杂软组织物理的场景提供一套完整的资产管线**。

---

## 使用场景

- **角色肌肉变形**：在 Dataflow 中连接网格→生成四面体→计算纤维方向→设置运动学约束→输出 FleshAsset，让骨架驱动肉体形变。
- **模拟肌肉收缩**：使用 `ComputeMuscleActivation` 节点从动画曲线驱动肌肉激活，模拟真实的肌肉隆起。
- **碰撞自交互**：通过 `AuthorSceneCollisionCandidates` 配置顶点与环境碰撞候选，或通过 `SetVertexTrianglePositionTargetBinding` 创建几何体之间的弱约束（如内脏挤压）。

---

## Dataflow 节点蓝图用法

所有节点均为 Dataflow 编辑器中的蓝图中结构体（`USTRUCT`），通过拖拽连接线工作。以下按功能分组列出核心节点。

### 四面体生成

| 节点 | 说明 | 所属结构 |
|------|------|----------|
| `CreateTetrahedron` | 从三角形网格生成四面体网格（支持 IsoStuffing / TetWild 两种方法） | `FCreateTetrahedronDataflowNode` |
| `RadialTetrahedron` | 生成径向四面体（如圆柱体内部四面体化） | `FRadialTetrahedronDataflowNodes` |
| `AppendTetrahedralCollection` (v2) | 将两个四面体集合合并成一个 | `FAppendTetrahedralCollectionDataflowNode_v2` |

### 肌肉纤维

| 节点 | 说明 | 所属结构 |
|------|------|----------|
| `ComputeFiberField` | 根据起止顶点计算每个四面体的纤维方向（用于肌肉收缩） | `FComputeFiberFieldNode` |
| `ComputeFiberStreamline` | 生成从起点到终点的纤维流线（可视化用） | `FComputeFiberStreamlineNode` |
| `VisualizeFiberField` | 将纤维方向以向量场形式输出 | `FVisualizeFiberFieldNode` |

### 约束与绑定

| 节点 | 说明 | 所属结构 |
|------|------|----------|
| `KinematicInitialization` | 将指定顶点设为运动学（位置由外部驱动） | `FKinematicInitializationDataflowNode` |
| `KinematicBodySetupInitialization` | 根据骨骼网格初始化碰撞体约束 | `FKinematicBodySetupInitializationDataflowNode` |
| `KinematicSkeletonConstraint` | 将骨架绑定到四面体网格上 | `FKinematicSkeletonConstraintDataflowNode` |
| `SetFleshBonePositionTargetBinding` (v2) | 将四面体顶点绑定到骨骼网格表面（运动学或弱约束） | `FSetFleshBonePositionTargetBindingDataflowNode_v2` |
| `SetVertexTrianglePositionTargetBinding` | 创建顶点到三角形的弱约束（弹簧），用于几何体之间交互 | `FSetVertexTrianglePositionTargetBindingDataflowNode` |
| `SetVertexVertexPositionTargetBinding` | 创建顶点到顶点的弱约束 | `FSetVertexVertexPositionTargetBindingDataflowNode` |
| `DeleteVertexTrianglePositionTargetBinding` | 删除已创建的顶点-三角形约束 | `FDeleteVertexTrianglePositionTargetBindingDataflowNode` |

### 绑定生成

| 节点 | 说明 | 所属结构 |
|------|------|----------|
| `GenerateSkeletalBindings` | 为骨骼网格的渲染表面生成到四面体的重心绑定（用于 FleshDeformer） | `FGenerateSkeletalBindings` |
| `GenerateSurfaceBindings` | 为静态/骨骼网格的渲染表面生成到四面体的绑定（用于 Geometry Cache 或形变器） | `FGenerateSurfaceBindings` |

### 属性设置与计算

| 节点 | 说明 | 所属结构 |
|------|------|----------|
| `SetFleshDefaultProperties` | 设置密度、刚度、阻尼、不可压缩性、膨胀等物理属性 | `FSetFleshDefaultPropertiesNode` |
| `SetVertexTetrahedraPositionTargetBinding` | 指定定点到四面体的位置目标绑定 | `FSetVertexTetrahedraPositionTargetBindingDataflowNode` |
| `CalculateTetMetrics` | 计算四面体质量指标（如最小二面角等） | `FCalculateTetMetrics` |
| `ComputeIslands` | 计算四面体网格的连通区域 | `FComputeIslandsNode` |
| `GenerateOriginInsertion` | 从两组顶点在距离半径内生成肌肉起止点 | `FGenerateOriginInsertionNode` |
| `GetSurfaceIndices` | 获取指定几何组的表面顶点索引 | `FGetSurfaceIndicesNode` |
| `IsolateComponent` | 分离指定几何组件（可选删除内部面） | `FIsolateComponentNode` |
| `AddKinematicParticles` | 根据骨骼网格添加运动学粒子 | `FAddKinematicParticlesDataflowNode` |

### 终端节点

| 节点 | 说明 | 所属结构 |
|------|------|----------|
| `FleshAssetTerminal` | 将 Dataflow 图输出为 `UFleshAsset` 资产（终端节点） | `FFleshAssetTerminalDataflowNode` |
| `CurveSamplingAnimationAssetTerminal` | 生成用于 MLD 训练的动画资产（肌肉激活采样） | `FCurveSamplingAnimationAssetTerminalNode` |

### 可视化

| 节点 | 说明 | 所属结构 |
|------|------|----------|
| `VisualizePositionTargets` | 可视化位置目标向量场 | `FVisualizePositionTargetsNode` |
| `VisualizeKinematicFaces` | 可视化运动学控制的面 | `FVisualizeKinematicFacesNode` |

---

## C++ 用法

所有节点均继承自 `FDataflowNode`，可以直接在 C++ 中构造并添加到 Dataflow 图中，但更常见的是在 Dataflow 编辑器中通过蓝图工作。以下展示如何以 C++ 方式使用节点。

### 头文件引入

```cpp
#include "Dataflow/ChaosFleshCreateTetrahedronNode.h"
#include "Dataflow/ChaosFleshComputeFiberFieldNode.h"
#include "Dataflow/ChaosFleshFleshAssetTerminalNode.h"
```

### 基本用法：构建一个末端节点并获取 FleshAsset

```cpp
// 创建一个 FleshAssetTerminalNode 实例
UE::Dataflow::FNodeParameters NodeParams;
FGuid NodeGuid = FGuid::NewGuid();
FFleshAssetTerminalDataflowNode TerminalNode(NodeParams, NodeGuid);
TerminalNode.FleshAsset = NewObject<UFleshAsset>();

// 设置输入集合（假设已有集合）
FManagedArrayCollection InputCollection;
// ...填充集合...
TerminalNode.Collection = InputCollection;

// 评估节点
UE::Dataflow::FContext Context;
TerminalNode.Evaluate(Context, nullptr);

// 输出已存储在 TerminalNode.Collection 中，并写回 FleshAsset
// TerminalNode.SetAssetValue() 会将集合写入资产
```

来源：`Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFleshNodes/Public/Dataflow/ChaosFleshFleshAssetTerminalNode.h`

### 进阶用法：完整的肉体资产管线

```cpp
// 1. 从静态网格生成四面体
FCreateTetrahedronDataflowNode CreateNode(...);
CreateNode.Collection = InitialCollection;
CreateNode.Method = TetMeshingMethod::TetWild;
CreateNode.IdealEdgeLengthRel = 0.05;
CreateNode.Evaluate(Context, &CreateNode.Collection);

// 2. 设置默认物理属性
FSetFleshDefaultPropertiesNode PropNode(...);
PropNode.Collection = CreateNode.Collection;
PropNode.Density = 1.0f;
PropNode.VertexStiffness = 1e6f;
PropNode.Evaluate(Context, &PropNode.Collection);

// 3. 生成骨骼绑定（假设有骨骼网格）
FGenerateSkeletalBindings BindNode(...);
BindNode.Collection = PropNode.Collection;
BindNode.SkeletalMeshIn = MySkeletalMesh;
BindNode.Evaluate(Context, &BindNode.Collection);

// 4. 连接到终端节点输出资产
FFleshAssetTerminalDataflowNode Terminal(...);
Terminal.Collection = BindNode.Collection;
Terminal.FleshAsset = MyFleshAsset;
Terminal.Evaluate(Context, nullptr);
Terminal.SetAssetValue(MyFleshAsset, Context);
```

来源：组合多个节点头文件定义，模拟 Dataflow 图执行流程。

---

## Demo 示例

以下是一个完整的 C++ 函数，用于从静态网格生成带默认属性的 FleshAsset：

**ChaosFleshDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "ChaosFlesh/FleshAsset.h"
#include "Dataflow/DataflowCore.h"

class FChaosFleshDemo
{
public:
	static UFleshAsset* GenerateFleshFromStaticMesh(UStaticMesh* StaticMesh, UObject* Outer);
};
```

**ChaosFleshDemo.cpp**
```cpp
#include "ChaosFleshDemo.h"
#include "Dataflow/ChaosFleshCreateTetrahedronNode.h"
#include "Dataflow/ChaosFleshSetFleshDefaultPropertiesNode.h"
#include "Dataflow/ChaosFleshFleshAssetTerminalNode.h"
#include "GeometryCollection/GeometryCollection.h"
#include "GeometryCollection/ManagedArrayCollection.h"

UFleshAsset* FChaosFleshDemo::GenerateFleshFromStaticMesh(UStaticMesh* StaticMesh, UObject* Outer)
{
	// 初始集合：包含网格几何体
	FManagedArrayCollection Collection;
	// 实际项目需从 StaticMesh 生成 FGeometryCollection 填充 Collection
	// 这里省略转换细节

	// 创建 Dataflow 上下文和节点参数
	UE::Dataflow::FNodeParameters Params;
	FGuid Guid = FGuid::NewGuid();

	// 步骤1：生成四面体
	FCreateTetrahedronDataflowNode TetNode(Params, Guid);
	TetNode.Collection = Collection;
	TetNode.Method = TetMeshingMethod::IsoStuffing;
	TetNode.NumCells = 32;
	TetNode.Evaluate(nullptr, &TetNode.Collection);

	// 步骤2：设置默认属性
	FSetFleshDefaultPropertiesNode PropNode(Params, Guid);
	PropNode.Collection = TetNode.Collection;
	PropNode.Density = 1.0f;
	PropNode.VertexStiffness = 1e6f;
	PropNode.Evaluate(nullptr, &PropNode.Collection);

	// 步骤3：输出到 FleshAsset
	UFleshAsset* FleshAsset = NewObject<UFleshAsset>(Outer);
	FFleshAssetTerminalDataflowNode TerminalNode(Params, Guid);
	TerminalNode.Collection = PropNode.Collection;
	TerminalNode.FleshAsset = FleshAsset;
	TerminalNode.Evaluate(nullptr, nullptr);
	TerminalNode.SetAssetValue(FleshAsset, *new UE::Dataflow::FContext());

	return FleshAsset;
}
```

---

## 模块依赖

`ChaosFleshNodes` 模块的 `Build.cs` 中需要以下独特依赖（省略标准 Core/Engine 等）：

| 模块 | 用途 |
|------|------|
| `DataflowCore` | Dataflow 图框架核心 |
| `DataflowEngine` | Dataflow 引擎集成（节点注册、渲染类型等） |
| `GeometryCollection` | 几何集合数据结构（`FManagedArrayCollection`、`FGeometryCollection`） |
| `ChaosFleshEngine` | 肉体物理引擎模块（提供 `UFleshAsset` 定义） |
| `ChaosFlesh` | 肉体物理运行时模块（提供物理求解器集成） |
| `FieldSystemCore` | 场系统支持（可视化向量场） |
| `Projects` | 模块初始化（`IModuleInterface`） |

**注意**：若你的模块需要使用此处 Dataflow 节点，需在 `PublicDependencyModuleNames` 中添加以上模块（除 `ChaosFlesh`、`ChaosFleshEngine` 作为运行时依赖，可放在 `PrivateDependencyModuleNames` 中）。

---

## 维护状态

### 近期更新

- 2025-10-03 `71e223a6` Dataflow: 修复 API 更新导致的重命名（`FAppendTetrahedralCollection` 变体）
- 2025-10-01 `dca9c2ee` Add a way for each dataflow editor to hide geometry cache properties in the preview menu based on terminal node type.
- 2025-09-28 (推测) 实验性节点属性调整
- 2025-08-20 (推测) 修复骨骼绑定搜索半径问题

### 维护评价

- **活跃度**：该模块处于**活跃开发**阶段，几乎每月都有功能性更新（新节点、API 优化）。
- **已知限制**：节点版本化处理较为复杂（多版本共存，例如 v2 节点与废弃节点）。`IdealEdgeLength` 已弃用，需使用 `IdealEdgeLengthRel`。
- **推荐度**：仅推荐用于**实验性项目**或愿意接受 API 不稳定的开发者。对于正式产品，建议等待模块脱离实验状态（`IsExperimentalVersion=true`）。

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh)
- [当前模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFleshNodes/Public/Dataflow)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-flesh-overview)（实时更新链接可能变化）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh/Tests)