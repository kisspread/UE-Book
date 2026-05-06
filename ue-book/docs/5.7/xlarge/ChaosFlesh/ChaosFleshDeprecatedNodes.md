# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 肉体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Editor), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

该插件是 Chaos 物理系统中用于 **肉体模拟（flesh simulation）** 的实验性模块。它提供了一组数据流（Dataflow）节点，用于生成和处理基于四面体网格的变形体数据，支持导入自定义几何文件（.geo）、构建四面体网格、定义运动学约束等。

**本模块 `ChaosFleshDeprecatedNodes`** 包含已在 UE 5.4 版本中弃用的旧版数据流节点，仅用于向后兼容旧项目。新项目应使用 `ChaosFleshNodes` 模块中的对应节点。

> ⚠️ 注意：该模块的所有节点均标记 `Deprecated = "5.4"`，后续版本可能移除。

## 使用场景

- 你正在维护一个在 UE 5.4 之前使用 Chaos Flesh 旧版节点的项目，需要保持兼容。
- 你需要临时使用旧版 API（如 `FConstructTetGridNode`、`FGenerateTetrahedralCollectionDataflowNodes`）进行快速原型验证。
- 你希望学习 Chaos Flesh 历史实现，但**不建议**在新项目中直接使用本模块。

## 蓝图用法

本模块中的所有节点均为 Dataflow 节点，**不提供直接可在蓝图图表中调用的函数（UFUNCTION）**。它们只能在 **Dataflow 编辑器** 中作为节点使用，或通过 C++ 驱动。

### 核心数据流节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FConstructTetGridNode` | 构建一个简单的均匀四面体网格（四叉网格） | `ChaosFlesh/TetGrid` |
| `FGenerateTetrahedralCollectionDataflowNodes` | 从静态网格或骨骼网格生成四面体集合，支持 IsoStuffing 和 TetWild 两种方法 | `Flesh/GenerateTetrahedralCollection` |
| `FExtractGEOInt` / `FExtractGEOIntVector` / `FExtractGEOFloatVector` | 从 `ImportGEO` 节点的输出中提取指定名称的标量/向量数据 | `Flesh/ExtractGEO*` |
| `FKinematicOriginInsertionInitializationDataflowNode` | 初始化运动学原点插入约束，将指定的顶点对绑定到骨骼 | `Flesh/KinematicOriginInsertionInitialization` |
| `FKinematicTetrahedralBindingsDataflowNode` | 为四面体网格创建运动学约束绑定，支持排除列表 | `Flesh/KinematicTetrahedralBindings` |

以上节点均在 **Dataflow** → **Flesh** 分类下，可在 Dataflow 图表中拖拽使用。

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/ChaosFleshConstructTetGridNode.h"
#include "Dataflow/ChaosFleshCreateTetrahedralCollectionNode.h"
#include "Dataflow/ChaosFleshImportGEO.h"
#include "Dataflow/ChaosFleshKinematicOriginInsertionInitializationNode.h"
#include "Dataflow/ChaosFleshKinematicTetrahedralConstraintNode.h"
```

### 基本用法

以下示例演示如何创建一个 `FConstructTetGridNode` 并执行评估，生成一个四面体网格集合（来自旧版 API，仅供兼容参考）：

```cpp
// Source: Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFleshDeprecatedNodes/Private/Dataflow/ChaosFleshConstructTetGridNode.cpp
#include "Dataflow/ChaosFleshConstructTetGridNode.h"

// 创建节点实例
UE::Dataflow::FNodeParameters Params;
FConstructTetGridNode Node(Params);

// 设置输入参数
Node.GridCellCount = FIntVector(8, 8, 8);
Node.GridDomain = FVector(5.0, 5.0, 5.0);
Node.bDiscardInteriorTriangles = true;

// 准备 Dataflow 上下文
UE::Dataflow::FContext Context;
Node.RegisterInputConnection(&Node.Collection);
Node.RegisterOutputConnection(&Node.Collection);

// 执行评估（需要 Dataflow 引擎驱动，此处为简化调用）
// 注意：实际使用时需通过 Dataflow 求解器（如 FDataflowSolver）调度
// Node.Evaluate(Context, &Node.Collection);
```

### 进阶用法

使用 `FGenerateTetrahedralCollectionDataflowNodes` 从静态网格生成四面体集合（TetWild 方法）：

```cpp
// Source: Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFleshDeprecatedNodes/Private/Dataflow/ChaosFleshCreateTetrahedralCollectionNode.cpp
#include "Dataflow/ChaosFleshCreateTetrahedralCollectionNode.h"

FGenerateTetrahedralCollectionDataflowNodes Node(Params);
Node.StaticMesh = MyStaticMesh; // 输入静态网格
Node.Method = TetMeshingMethod::TetWild;
Node.IdealEdgeLengthRel = 0.1;
Node.MaxIterations = 80;
Node.bCoarsen = false;

// ... 连接输入输出并执行
```

> 注意：这些已弃用节点不再建议使用，推荐使用 `ChaosFleshNodes` 模块中的 `FGenerateTetrahedralCollectionDataflowNodes`（非弃用版本）。

## Demo 示例

由于本模块仅包含已弃用节点，强烈建议**不要**在新项目中使用。若需学习 Chaos Flesh 模拟，请参阅 `ChaosFleshNodes` 模块的示例。

因此，此处**不提供完整代码示例**。读者可参考 `ChaosFleshNodes` 模块的文档获取最新用法。

## 模块依赖

`ChaosFleshDeprecatedNodes` 的依赖信息来自其 `Build.cs`。常见 Dataflow 相关模块已自动链接。

| 模块 | 用途 |
|---|---|
| `DataflowCore` | Dataflow 框架核心 |
| `DataflowEngine` | Dataflow 引擎集成 |
| `GeometryCollection` | 几何集合数据结构 |
| `ChaosFlesh` | 父模块（包含基础集合类型如 `FFleshCollection`） |

无其他特殊依赖。

## 维护状态

### 近期更新

| 日期 | Hash | Commit | 解读 |
|---|---|---|---|
| 2025-10-22 | `a1039b21` | USD: Disabled UE allocator in USD for Windows. | 仅与外插件构建相关，非本模块修改 |
| 2025-10-17 | `be609b71` | [Backout] - CL47041219 | 回滚无关改动 |
| 2025-10-17 | `7ab79237` | USD: Disabled UE allocator in USD for Windows. | 同上 |
| 2025-10-03 | `71e223a6` | Dataflow: | 可能涉及 Dataflow 框架调整，但不针对本模块 |
| 2025-10-01 | `dca9c2ee` | Add a way fro each dataflow editors to hide geometry cache properties... | 初始化 commit |

### 维护评价

- **创建时间**：2025-10-01（距今约 0 年）
- **近期更新**：最近 commit 均非针对本模块功能的更新，而是全局构建或 Dataflow 框架修改。
- **是否活跃维护**：否。该模块所有节点均标记为 `Deprecated = "5.4"`，官方已明确弃用，后续版本（5.5+）中此模块可能被移除。
- **是否推荐使用**：**强烈不推荐**。仅用于临时兼容旧项目，新项目应使用 `ChaosFleshNodes` 模块中的非弃用节点。

⚠️ **警告**：本模块自 UE 5.4 起弃用，超过 1 年未获得实质性更新，建议尽快迁移。

## 相关链接

- [源码 (Plugin 根目录)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh)
- [本模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFleshDeprecatedNodes/Public)
- [官方文档](https://docs.unrealengine.com/)（Chaos 物理文档，不专门针对此 Deprecated 模块）