# Chaos Flesh（已弃用节点）

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 混沌肉体（已弃用节点） |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

**重要提示**: 本文档主要介绍 **`ChaosFleshDeprecatedNodes`** 模块。这是一个包含**已弃用** Dataflow 节点的模块，用于导入 GEO 文件并生成四面体网格集合。这些节点是 Chaos Flesh 早期工作流的一部分，从 UE 5.4 开始已被标记为弃用。**强烈建议新项目使用主模块 `ChaosFlesh` 或 `ChaosFleshNodes` 中的非弃用节点。**

## 用途

本模块（`ChaosFleshDeprecatedNodes`）提供了一套已弃用的 Dataflow 节点，其核心功能是：
1.  **数据导入**：从 SideFX Houdini 的 GEO 文件中导入几何体和属性数据。
2.  **网格生成**：将导入的或引擎内的静态/骨骼网格体转化为用于物理模拟的四面体（Tetrahedron）集合。
3.  **约束设置**：为四面体网格设置运动学约束的起始点和插入点。

这些节点是 Chaos Flesh 系统早期版本用于构建模拟资产的工具链的一部分，现已由更新、更稳定的节点所取代。

## 使用场景

-   **物理模拟与实时变形**：为角色或物体创建用于可变形（软体）物理模拟的底层四面体网格。
-   **Houdini 流水线集成**：需要从 Houdini 导出 GEO 格式的几何体（特别是四面体网格）并在 UE 中使用。
-   **构建复合物理资产**：结合骨骼网格体的动画驱动和肉体的物理变形。

**注意**：由于这些节点已弃用，对于新项目，应优先使用主 `ChaosFlesh` 或 `ChaosFleshNodes` 模块中提供的相应功能节点。

## 蓝图用法

**此模块中的所有节点都已在 UE 5.4 中弃用（`Deprecated = "5.4"`）。** 在蓝图编辑器中，它们可能默认隐藏或带有弃用警告。

### 核心节点（已弃用）

所有节点均属于 `Flesh` 分类，用于构建 Dataflow 图。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportGEO` | 从指定的 GEO 文件导入几何体和属性数据。输出包含四面体网格的 `Collection` 和多种类型的变量映射。 | `FImportGEO` |
| `ExtractGEOInt` | 从 `ImportGEO` 节点的整数变量输出中，按名称提取单个整数值。 | `FExtractGEOInt` |
| `ExtractGEOIntVector` | 从 `ImportGEO` 节点的整数数组变量输出中，按名称提取一个整数数组。 | `FExtractGEOIntVector` |
| `ExtractGEOFloatVector` | 从 `ImportGEO` 节点的浮点数组变量输出中，按名称提取一个浮点数数组。 | `FExtractGEOFloatVector` |
| `GenerateTetrahedralCollection` | 从一个静态或骨骼网格体生成四面体网格集合。支持 IsoStuffing 和 TetWild 两种算法。 | `FGenerateTetrahedralCollectionDataflowNodes` |
| `TetGrid` | 构建一个规整的四面体网格（Tet Grid），用于测试或作为基础形状。 | `FConstructTetGridNode` |
| `KinematicOriginInsertionInitialization` | 为四面体网格集合设置运动学约束的起始点和插入点的顶点索引。 | `FKinematicOriginInsertionInitializationDataflowNode` |
| `KinematicTetrahedralBindings` | 为骨骼网格体和四面体网格集合创建运动学绑定。 | `FKinematicTetrahedralBindingsDataflowNode` |

## C++ 用法

**不建议在新代码中使用此模块中的类，因为它们已被弃用。** 以下仅为历史参考。

### 头文件引入

```cpp
#include "ChaosFleshImportGEO.h" // 对于 ImportGEO 及相关提取节点
#include "ChaosFleshCreateTetrahedralCollectionNode.h" // 对于四面体网格生成节点
// 其他节点头文件类似
```

### 基本用法

以下代码展示了如何程序化地创建一个已弃用的 `ImportGEO` 节点。这通常在自定义的 Dataflow 工具中完成，而非直接在游戏逻辑中。

```cpp
// 来源：节点定义 (ChaosFleshImportGEO.h)
// 创建节点参数
UE::Dataflow::FNodeParameters Params;
FGuid NodeGuid = FGuid::NewGuid();

// 实例化节点（已弃用）
FImportGEO ImportGEONode(Params, NodeGuid);

// 设置属性
ImportGEONode.Filename.FilePath = TEXT("/Game/Path/To/YourMesh.geo");
ImportGEONode.bImportTetrahedronMesh = true;
ImportGEONode.bDiscardInteriorTriangles = true;

// 注意：节点的实际执行（Evaluate）通常由 Dataflow 图形引擎驱动，
// 而非直接调用。此示例仅为展示构造方式。
```

## Demo 示例

**由于所有节点均已弃用，不提供使用这些节点的完整示例。**

建议查看 **`ChaosFlesh`** 或 **`ChaosFleshNodes`** 模块的文档和测试用例，以获取当前推荐的、用于构建 Flesh 资产和工作流的示例。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosFlesh` | Chaos Flesh 核心运行时模块，提供 `FFleshCollection` 等基础数据结构。 |
| `ChaosFleshEngine` | Chaos Flesh 引擎集成模块。 |

## 维护状态

### 近期更新

从最近的 git 历史可以看出，整个 ChaosFlesh 插件仍在活跃维护中，但 `ChaosFleshDeprecatedNodes` 模块本身可能只接收兼容性修复。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-05-12 | `981bc9da` | Dataflow: | （提交信息不完整） |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理 Flesh 模块中的纤维场生成节点。 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复掩码缓冲区赋值逻辑错误。 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | **弃用 Flesh 资产中的 StaticMesh 属性。** |

### 维护评价

- **活跃维护**：从提交记录看，整个 ChaosFlesh 系统在 2026 年仍在频繁更新和优化，表明 Epic Games 持续投入。
- **模块状态**：`ChaosFleshDeprecatedNodes` 模块本身已确认为弃用状态，其功能正在被主模块的新节点替代。它很可能只接收必要的编译修复，而不会有新功能添加。
- **推荐使用**：**不推荐**在新项目中使用此模块。请使用主 `ChaosFlesh` 或 `ChaosFleshNodes` 模块提供的当前、受支持的工作流和节点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh/Tests)（需验证路径）