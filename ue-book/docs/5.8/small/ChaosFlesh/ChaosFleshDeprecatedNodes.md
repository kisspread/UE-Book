# Chaos Flesh (已废弃节点)

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 混沌软体（已废弃节点） |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点资产） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

`ChaosFleshDeprecatedNodes` 模块是 `ChaosFlesh` 插件的一个子模块，专门用于存放**已被标记为废弃（Deprecated）** 的数据流（Dataflow）节点。这些节点是早期版本（UE 5.4 之前）用于软体（Flesh）模拟工作流的一部分，现在已由新版本节点替代。

该模块存在的主要目的是**向后兼容**，确保在旧版本引擎中创建的、使用了这些节点的资产或数据流图，在新版本引擎中仍能被加载和识别，避免直接报错。但所有新项目和功能都应使用 `ChaosFleshNodes` 模块中的非废弃节点。

## 使用场景

1.  **维护旧项目**：当你在新版本 UE5 中打开一个使用了旧版 `ChaosFlesh` 数据流图的项目时，可能会遇到这些废弃节点。此模块确保它们能被识别和加载。
2.  **参考旧版工作流**：如果你需要了解或复现旧版教程或文档中描述的软体设置，可能会看到这些节点名称。

**重要提示**：在新项目中**不应**使用这些节点。请查找并使用它们的非废弃替代版本（通常位于 `ChaosFleshNodes` 模块）。

## 蓝图用法

本模块中的节点均为 `Dataflow` 节点，通常在 **Dataflow 编辑器**中使用，而非传统蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportGEO` | 从 `.geo` 文件导入数据，可提取四面体网格和变量。 | `FImportGEO` |
| `GenerateTetrahedralCollection` | 从静态或骨骼网格体生成四面体网格集合，支持 IsoStuffing 和 TetWild 算法。 | `FGenerateTetrahedralCollectionDataflowNodes` |
| `TetGrid` | 创建一个由四面体组成的规则网格。 | `FConstructTetGridNode` |
| `KinematicTetrahedralBindings` | 为骨骼网格体的骨骼创建运动学（Kinematic）的四面体绑定。 | `FKinematicTetrahedralBindingsDataflowNode` |
| `KinematicOriginInsertionInitialization` | 初始化软体模拟中的原点（Origin）和插入点（Insertion）选择集，用于定义附着点。 | `FKinematicOriginInsertionInitializationDataflowNode` |
| `ExtractGEOInt` | 从 `ImportGEO` 节点的输出中提取指定的整数变量。 | `FExtractGEOInt` |
| `ExtractGEOIntVector` | 从 `ImportGEO` 节点的输出中提取指定的整数数组变量。 | `FExtractGEOIntVector` |
| `ExtractGEOFloatVector` | 从 `ImportGEO` 节点的输出中提取指定的浮点数组变量。 | `FExtractGEOFloatVector` |

### 使用示例（数据流图描述）

假设你要复现一个旧版教程中导入 GEO 文件的工作流：

1.  在 Dataflow 编辑器中，创建一个新的数据流资产。
2.  添加一个 **`ImportGEO`** 节点。在它的 `Filename` 属性中，浏览并选择一个 `.geo` 文件。
3.  将 `ImportGEO` 节点的 `Collection` 输出连接到后续需要使用网格体数据的节点（如 `KinematicTetrahedralBindings`）。
4.  如果 `.geo` 文件中包含自定义变量，可以使用 **`ExtractGEOInt`**、**`ExtractGEOIntVector`** 或 **`ExtractGEOFloatVector`** 节点。将 `ImportGEO` 的相应输出（如 `IntVarsOutput`）连接到提取节点的输入，并在提取节点的 `VarName` 属性中填写要查询的变量名。

## C++ 用法

本模块中的类主要是数据流节点，在 C++ 中主要作为数据流图的一部分被实例化和评估，通常不直接进行函数调用。

### 头文件引入

```cpp
#include "ChaosFleshImportGEO.h"
#include "ChaosFleshCreateTetrahedralCollectionNode.h"
#include "ChaosFleshConstructTetGridNode.h"
// ... 根据需要包含其他废弃节点头文件
```

### 基本用法

这些节点作为 `FDataflowNode` 的子类，其生命周期和评估由 Dataflow 框架管理。在 C++ 中，你通常不会直接 `new` 这些节点，而是在构建数据流图资产时，通过编辑器或特定的数据流资产创建函数来添加它们。

例如，`FImportGEO` 节点的使用逻辑封装在其 `Evaluate` 函数中，该函数由 Dataflow 上下文调用：

```cpp
// FImportGEO::Evaluate 的简化逻辑示意 (来自节点定义)
virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
{
    // 1. 读取并解析 Filename 属性指向的 .geo 文件
    // 2. 根据 bImportTetrahedronMesh 标志，将网格数据写入 Collection 输出
    // 3. 将文件中的变量数据写入 IntVarsOutput, IntVectorVarsOutput, FloatVectorVarsOutput
}
```

### 进阶用法

在更复杂的场景下，数据流图引擎会按连接顺序依次评估节点。例如，一个典型的设置流程可能是：

1.  `FConstructTetGridNode` 或 `FGenerateTetrahedralCollectionDataflowNodes` 创建一个基础的 `FManagedArrayCollection` (Collection)。
2.  `FImportGEO` 可能将额外的几何或属性数据合并到同一个 `Collection` 中。
3.  `FKinematicTetrahedralBindingsDataflowNode` 根据传入的 `SkeletalMesh` 为 `Collection` 中的顶点添加骨骼绑定信息。
4.  最后，`FKinematicOriginInsertionInitializationDataflowNode` 使用用户指定的顶点索引集合来标记模拟的附着点。

所有这些操作都通过连接节点的输入/输出端口（`DataflowInput`/`DataflowOutput`）并共享同一个 `FManagedArrayCollection` 对象来完成。

## Demo 示例

由于这些节点已被废弃，不建议在新代码中使用。下面仅展示一个概念性的 C++ 代码片段，说明如何创建一个包含废弃节点的数据流图（通常由编辑器工具完成）：

```cpp
// 注意：此代码仅为说明数据流节点的连接方式，实际创建数据流资产通常通过编辑器或专用工厂类。
#include "Dataflow/DataflowGraph.h"
#include "Dataflow/DataflowNodeParameters.h"
#include "ChaosFleshImportGEO.h"
#include "ChaosFleshCreateTetrahedralCollectionNode.h"

void CreateDeprecatedChaosFleshDataflowExample()
{
    // 创建一个数据流图
    UDataflowGraph* Graph = NewObject<UDataflowGraph>();
    UE::Dataflow::FNodeParameters Params;

    // 1. 添加一个“生成四面体集合”节点
    FGenerateTetrahedralCollectionDataflowNodes* TetNode = Graph->AddNode<FGenerateTetrahedralCollectionDataflowNodes>(Params);

    // 2. 添加一个“导入GEO”节点
    FImportGEO* ImportNode = Graph->AddNode<FImportGEO>(Params);
    ImportNode->Filename.FilePath = TEXT("/Path/To/Your/file.geo");

    // 3. 连接节点 (概念性，实际连接通过图编辑器或连接API)
    // TetNode->Collection 输出 -> ImportNode->Collection 输入
    // ImportNode 评估后，其 IntVarsOutput 等端口将包含解析出的变量。

    // 4. 添加一个提取节点来获取特定变量
    FExtractGEOInt* ExtractNode = Graph->AddNode<FExtractGEOInt>(Params);
    ExtractNode->VarName = TEXT("SomeIntegerVariable");

    // 5. 连接: ImportNode->IntVarsOutput -> ExtractNode->IntVars 输入

    // 之后，当数据流图被评估时，所有这些节点的 Evaluate 函数将按拓扑顺序执行。
}
```

## 模块依赖

要使用此模块（即链接并使用其中的废弃节点类），你的项目模块需要在 `Build.cs` 文件中添加对 `ChaosFleshDeprecatedNodes` 的依赖。由于该模块包含数据流节点，很可能还需要依赖数据流框架。

| 模块 | 用途 |
|---|---|
| `ChaosFlesh` | ChaosFlesh 插件的核心运行时模块，提供 `FManagedArrayCollection`, `FFleshCollection` 等基础类型。 |
| `Dataflow` | Unreal Engine 的数据流框架，提供 `FDataflowNode`, `FDataflowGraph` 等基础设施。 |
| `Chaos` | Chaos 物理系统的公共接口，软体模拟基于此系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为单精度时产生的编译警告。 |
| 2026-05-12 | `981bc9da` | Dataflow: | (无详细信息，可能是对数据流框架的通用更改) |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理了软体模拟中用于生成纤维场的节点代码。 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复了掩码缓冲区赋值的一个问题。 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 将软体资产中的静态网格体属性标记为已弃用。 |

### 维护评价

- **创建时间**：2022年3月，作为 ChaosFlesh 插件的一部分引入。
- **最近更新**：近期（2026年5月）有多次提交，主要是**代码清理、修复编译警告和兼容性问题**，而非新功能开发。这表明该模块仍在被维护，但维护活动主要集中在保持代码健康和与引擎其他部分的同步上，**不再添加新功能**。
- **活跃状态**：**维护中**。虽然模块内容已过时，但 Epic 仍在对其进行必要的维护以保证引擎的稳定性和向后兼容性。
- **已知限制**：**模块内的所有节点和结构体均已明确标记为 `Deprecated = "5.4"`**。这意味着它们可能在未来的某个引擎版本中被完全移除。
- **推荐**：**仅用于兼容旧项目，不推荐在新项目中使用**。新项目应直接使用 `ChaosFleshNodes` 模块中的替代节点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 测试用例：未在提供的信息中明确标识，可能位于 `Engine/Tests/` 目录下或集成在 ChaosFlesh 的整体测试套件中。