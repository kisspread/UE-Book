# Geometry Dataflow Nodes

> Geometry Processing in Dataflow.

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流节点 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 |
| 模块 | `GeometryDataflowNodes` (Runtime), `DataflowMedialSkeleton` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow) | |

## 用途

这个插件的核心目的是将常见的几何处理功能（Geometry Processing）封装为可复用的 **Dataflow 节点**，从而让用户能够在可视化、基于节点的 **Dataflow 图**中执行复杂的网格操作。

与直接在蓝图中通过 C++ 调用几何处理库相比，此插件提供了一种更直观、更易于构建和调试的工作流程。它主要解决了在 Dataflow 环境中进行程序化几何编辑（如布尔运算）的需求，特别适用于需要将几何操作作为复杂程序化生成或动画流程一部分的场景。

## 使用场景

- 你需要在 Dataflow 图中执行两个网格的布尔运算（并集、差集、交集）来组合或修剪它们。
- 你在创建一个程序化角色生成系统，需要在生成过程中动态地合并或雕刻身体部件的网格。
- 你正在制作一个基于节点的几何编辑器，并希望将网格布尔操作作为其中一个可配置的步骤。

## 蓝图用法

此插件主要通过 Dataflow 系统提供节点，而非传统的蓝图节点。其核心功能体现在 Dataflow 图编辑器中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MeshBoolean` | 执行两个网格之间的布尔运算（并集、差集、交集）。 | `FMeshBooleanDataflowNode` |

### 使用示例（Dataflow 图描述）

在 Dataflow 图编辑器中，你可以找到“MeshBoolean”节点，它属于“Mesh|Utilities”类别。

1.  **连接输入**：将两个 `UDynamicMesh` 资产（或来自其他节点的网格输出）分别连接到节点的 `Mesh1` 和 `Mesh2` 输入引脚。
2.  **设置属性**：
    - 在节点的属性面板中，选择 `Operation`（运算类型），例如 `Union`（并集）。
    - 根据需要调整 `bSimplifyAlongNewEdges`（沿新边简化）等优化选项。
3.  **获取输出**：节点会输出一个经过布尔运算后的新 `UDynamicMesh`，你可以将它连接到后续节点或用于渲染。

## C++ 用法

此插件主要提供 Dataflow 节点定义，而非可直接在游戏逻辑中调用的库。其用法主要体现在对节点的扩展或作为 Dataflow 系统一部分的配置上。

### 头文件引入

```cpp
#include "Dataflow/MeshBooleanNodes.h"
```

### 基本用法

该插件的核心是定义了 `FMeshBooleanDataflowNode` 结构体，它继承自 `FDataflowNode`。虽然游戏代码通常不直接实例化此节点，但理解其结构有助于在 Dataflow 图中进行配置。

```cpp
// 以下代码展示了节点内部如何定义布尔运算类型枚举，这是你在Dataflow图节点属性中看到选项的来源。
// 该节点本身通过 UE::Dataflow 命名空间中的函数进行注册。
UENUM(BlueprintType)
enum class EMeshBooleanOperationEnum : uint8
{
    // A union of A + B includes everything inside either A or B
    Dataflow_MeshBoolean_Union UMETA(DisplayName = "Union"),
    // An intersection of A & B includes only the points inside both A and B, i.e. trimming A by B (and vice versa)
    Dataflow_MeshBoolean_Intersect UMETA(DisplayName = "Intersect"),
    // A difference of A - B includes only the points inside A that are outside of B, i.e. subtracting B from A
    Dataflow_MeshBoolean_Difference UMETA(DisplayName = "Difference"),
    //~~~
    //256th entry
    Dataflow_Max                UMETA(Hidden)
};
```

### 进阶用法

从代码注释和结构推断，`FMeshBooleanDataflowNode` 的 `Evaluate` 函数是实际执行布尔运算的地方。如果你想为自己的 Dataflow 节点集成几何处理功能，可以参考此节点的结构：
1.  使用 `DATAFLOW_NODE_DEFINE_INTERNAL` 宏定义节点。
2.  为节点属性（如 `EMeshBooleanOperationEnum Operation`）添加 `UPROPERTY` 宏，使其在 Dataflow 图的属性面板中可编辑。
3.  定义 `DataflowInput` 和 `DataflowOutput` 元数据的属性来连接数据。
4.  重写 `Evaluate` 函数以实现具体逻辑。

## Demo 示例

由于此插件主要提供 Dataflow 节点定义，一个完整的“Demo”更接近于一个包含此节点的 Dataflow 图资产。一个最小可运行的“示例”是在编辑器中创建一个新的 Dataflow 图资产，搜索并添加“MeshBoolean”节点，然后连接两个输入网格体来观察结果。

从 C++ 插件扩展的角度，这里是一个理论上如何基于此节点创建类似功能的示意性代码结构：

**MyCustomMeshNode.h**
```cpp
#pragma once
#include "Dataflow/DataflowNode.h"
#include "GeometryScript/Types.h"

// 假设你想创建一个类似的节点用于自己的几何操作
USTRUCT()
struct FMyCustomMeshNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomMeshNode, "MyCustomNode", "MyCategory", "My custom node description")

public:
    FMyCustomMeshNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

private:
    // 定义输入网格
    UPROPERTY(meta = (DataflowInput, DataflowIntrinsic))
    TObjectPtr<UDynamicMesh> InputMesh;

    // 定义输出网格
    UPROPERTY(meta = (DataflowOutput))
    TObjectPtr<UDynamicMesh> OutputMesh;

    // 自定义参数
    UPROPERTY(EditAnywhere, Category = "Settings")
    float MyCustomParam = 1.0f;

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

**注意**：以上代码为结构示意，实际的 `Evaluate` 实现需要调用具体的几何处理函数，这正是 `GeometryDataflowNodes` 插件为 `MeshBoolean` 所封装的内容。

## 模块依赖

基于插件的 `.uplugin` 配置，它显式依赖以下插件。因此，使用此插件的模块通常也需要依赖这些模块或其提供的接口。

| 模块 | 用途 |
|---|---|
| `Dataflow` | 提供 Dataflow 节点系统的核心框架。 |
| `GeometryProcessing` | 提供底层的几何处理算法（如网格布尔运算的核心库）。 |

**注意**：插件自身有两个模块 `GeometryDataflowNodes` 和 `DataflowMedialSkeleton`。要使用 `MeshBoolean` 节点，你的项目需要启用此插件，其依赖项（`Dataflow` 和 `GeometryProcessing` 插件）会自动启用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `da753042` | Dataflow geometry nodes plugin : remove beta status | 此插件已正式移除beta版本标记，表明其趋于稳定。 |
| 2026-05-12 | `45745f54` | Dataflow: | 对Dataflow相关节点进行了更新或调整。 |
| 2026-04-17 | `49f946b4` | [Dataflow] | 针对Dataflow系统进行了维护性更新。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 更新了大量Dataflow节点以使用新的渲染系统，是一次重要的兼容性改进。 |
| 2025-12-11 | `2c27a203` | Minor cleanup of dataflow mesh boolean options | 对Dataflow网格布尔选项进行了小范围的清理和优化。 |

### 维护评价

**综合评价：积极维护的实验性功能。**

- **创建时间**：插件创建于2025年初，相对年轻。
- **更新频率**：从提交历史看，在2025年底和2026年初有持续的功能性更新和优化，并且在最近移除了beta标记，表明开发团队正在积极维护并认为其已达到一定稳定度。
- **维护状态**：**活跃维护中**。最近一次提交在2026年5月，且提交信息显示完成了从实验性到稳定化的转变。
- **已知限制**：作为实验性插件（尽管已移除beta标签），其API和功能在未来版本中仍可能发生变化。目前提供的节点数量有限（从代码分析看主要是网格布尔节点）。
- **推荐使用**：**推荐在实验性项目或接受API变化的项目中使用**。如果你需要在Dataflow图中执行网格布尔运算，并且项目可以接受使用实验性插件，那么这个插件是合适的选择。它正在走向稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow)
- [官方文档]()（暂无）
- [测试用例]()（在提供的信息中未明确，通常这类测试可能在引擎测试目录下）