# Geometry Dataflow Nodes

> Geometry Processing in Dataflow.

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流节点 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GeometryDataflowNodes` (Runtime), `DataflowMedialSkeleton` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-21 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow) | |

## 用途

该插件将几何处理（如网格布尔运算）功能引入到 Unreal Engine 的数据流（Dataflow）系统中。数据流是一种基于节点的可视化编程系统，允许用户通过连接节点来处理数据。`GeometryDataflow` 插件旨在将复杂的几何算法（如网格布尔运算）封装为易于使用的数据流节点，使艺术家和技术美术能够在不编写 C++ 代码的情况下，在数据流图表中执行几何操作。

该插件的核心价值在于将 `GeometryProcessing` 模块中的底层算法与 `Dataflow` 模块的可视化节点系统连接起来，创建了一个专注于几何处理的高阶工具集。

## 使用场景

-   **程序化建模**：在数据流中构建复杂的几何体，例如通过多个网格的布尔运算（并集、交集、差集）来创建新的几何形状。
-   **资产生成**：作为程序化内容生成（PCG）工作流的一部分，用于动态创建和修改网格资产。
-   **技术美术工具链**：技术美术可以创建自定义的数据流节点图，执行几何处理任务，而无需依赖传统的蓝图或 C++ 脚本。
-   **简化复杂操作**：将复杂的几何算法（如网格布尔运算）抽象为简单的节点，降低使用门槛。

## 蓝图用法

该插件主要通过数据流编辑器中的节点使用，而不是传统的蓝图节点。数据流节点在“数据流图表”编辑器中进行连接和配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mesh Boolean` | 对两个输入网格执行布尔运算（并集、交集、差集），并输出结果网格。 | `FMeshBooleanDataflowNode` |

### 使用示例（数据流图表描述）

1.  在数据流编辑器中，从节点面板的 `Mesh|Utilities` 分类下拖出一个 `Mesh Boolean` 节点。
2.  该节点有两个网格输入引脚 `Mesh1` 和 `Mesh2`。连接两个网格数据源（例如另外两个生成网格的节点）到这两个引脚。
3.  在节点细节面板中，配置布尔运算的属性：
    -   **Operation**：选择运算类型（并集、交集、差集）。
    -   **bWeldSharedEdges**：是否焊接公共边。
    -   **bSimplifyAlongNewEdges**：是否简化结果网格。
4.  节点将输出一个经过布尔运算处理的网格，可以连接到后续的节点（如材质应用、网格体生成节点等）。

## C++ 用法

该插件提供的主要功能是数据流节点，因此 C++ 用法通常涉及在自定义数据流节点中使用几何处理库，或者扩展该插件的节点集。

### 头文件引入

```cpp
#include "Dataflow/MeshBooleanNodes.h"
```

### 基本用法

虽然主要通过数据流节点使用，但了解其底层结构有助于扩展。以下是如何在 C++ 中声明一个网格布尔数据流节点的结构。

```cpp
// 引用自 Engine/Plugins/Experimental/GeometryDataflow/Source/GeometryDataflowNodes/Public/Dataflow/MeshBooleanNodes.h

// 1. 定义布尔运算枚举
UENUM(BlueprintType)
enum class EMeshBooleanOperationEnum : uint8
{
    Dataflow_MeshBoolean_Union,
    Dataflow_MeshBoolean_Intersect,
    Dataflow_MeshBoolean_Difference,
    Dataflow_Max
};

// 2. 定义网格布尔运算数据流节点
USTRUCT()
struct FMeshBooleanDataflowNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    // ... 属性和重写的 Evaluate 函数
};
```

### 进阶用法

`FMeshBooleanDataflowNode` 的 `Evaluate` 函数是执行实际布尔运算的地方。该函数的实现（未在提供的代码片段中展示）会调用 `GeometryProcessing` 模块中的算法。

```cpp
// 伪代码，展示 Evaluate 函数的可能实现逻辑
void FMeshBooleanDataflowNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 1. 从输入引脚获取两个网格
    UDynamicMesh* InputMesh1 = Context.GetValue<UDynamicMesh>(Mesh1);
    UDynamicMesh* InputMesh2 = Context.GetValue<UDynamicMesh>(Mesh2);
    
    // 2. 调用 GeometryProcessing 模块的网格布尔运算函数
    UDynamicMesh* ResultMesh = /* ... 调用如 UE::Geometry::MeshBoolean(...) 的函数 ... */;
    
    // 3. 将结果设置到输出引脚
    Context.SetValue<UDynamicMesh>(Mesh, ResultMesh);
}
```

## Demo 示例

由于 `GeometryDataflow` 是一个提供数据流节点的插件，其“Demo”主要是通过数据流图表来完成。一个最小的演示就是在数据流编辑器中创建一个简单的 `Mesh Boolean` 节点，并连接两个基础网格生成节点（如立方体、球体）来查看布尔运算效果。

从代码层面，一个最小的、可编译的扩展示例可能是创建一个新的数据流节点，该节点包装了另一个几何处理函数。由于示例较长且依赖于完整的几何处理库，此处不展开。但基本模式与 `FMeshBooleanDataflowNode` 类似：

1.  继承自 `FDataflowNode`。
2.  使用 `DATAFLOW_NODE_DEFINE_INTERNAL` 宏定义节点元数据。
3.  声明 `UPROPERTY` 作为输入、输出和可编辑参数。
4.  重写 `Evaluate` 函数实现逻辑。

## 模块依赖

该插件本身依赖于 `Dataflow` 和 `GeometryProcessing` 两个插件（在 `.uplugin` 中声明）。要在你自己的模块中使用该插件的节点或功能，需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `GeometryDataflowNodes` | 访问几何数据流节点（如 `FMeshBooleanDataflowNode`） |
| `GeometryProcessing` | 访问底层的几何处理算法（如网格布尔运算） |
| `Dataflow` | 数据流节点系统的基类和基础设施 |

在你的模块的 `.Build.cs` 文件中，需要添加对这些模块的依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "GeometryDataflowNodes",
    "GeometryProcessing",
    "Dataflow"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `da753042` | Dataflow geometry nodes plugin : remove beta status | 移除该插件的 beta 标记，表明其趋于稳定 |
| 2026-05-12 | `45745f54` | Dataflow: | (Commit message 过于简短，推测为通用性更新) |
| 2026-04-17 | `49f946b4` | [Dataflow] | (Commit message 过于简短，推测为通用性更新) |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 大量更新节点以使用新的渲染系统 |
| 2025-12-11 | `2c27a203` | Minor cleanup of dataflow mesh boolean options | 对网格布尔运算选项进行微小清理 |

### 维护评价

该插件创建于 2025 年初，目前处于**实验性阶段**（`EnabledByDefault: false`，路径在 `Experimental` 下）。从提交历史看，开发团队仍在积极维护和改进：

1.  **活跃度**：最近一次实质性更新是 2026 年 5 月移除 beta 状态，表明插件功能已相对成熟，并可能在未来从 Experimental 目录移出。
2.  **内容更新**：2025 年 12 月有多次提交，涉及节点渲染系统的更新和选项的清理，说明在持续优化。
3.  **风险**：作为实验性插件，其 API 和功能在未来版本中可能发生不兼容的变化。
4.  **推荐使用**：对于希望在数据流中进行几何处理的项目，特别是原型开发和工具链构建，可以谨慎使用。在生产环境中使用前，建议关注其从 Experimental 目录毕业的公告。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow/Tests)（如果存在）