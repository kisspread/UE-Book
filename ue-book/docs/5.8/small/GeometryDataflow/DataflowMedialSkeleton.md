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
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow) | |

## 用途

该插件是 Unreal Engine 数据流 (Dataflow) 框架的一个扩展，旨在将几何处理 (Geometry Processing) 的功能封装为一系列可视化节点。它解决的核心问题是：让开发者或技术美术能够在数据流编辑器中，通过连接节点的方式直观地构建复杂的几何处理流程（如网格布尔运算、修改等），而无需编写底层 C++ 代码。其存在是为了将强大的几何处理算法（来自 `GeometryProcessing` 插件）无缝集成到数据流的工作流中，提升程序化资产创建和几何修改的效率与灵活性。

## 使用场景

- **程序化资产创建管线**：你需要构建一个可复用的、可视化的管线来生成或修改静态网格体（Static Mesh），例如从基础几何体通过一系列布尔、细分、减面操作生成复杂模型。
- **数据驱动的几何修改**：你希望基于场景中的数据（如物理模拟结果、传感器数据）动态地、实时地调整几何体的形状。
- **封装复杂几何操作**：你需要将一些高级的几何处理算法（如网格简化、布尔运算）封装成简单易用的节点，提供给团队中的其他成员或用于构建用户可编辑的工具。

## 蓝图用法

该插件主要通过向数据流系统注册自定义节点来实现功能，这些节点可在“Dataflow”蓝图图表中使用。其提供的功能以 **数据流节点 (Dataflow Nodes)** 的形式存在。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BakeRenderCaptureOutputs` | 将渲染捕获（Render Capture）的输出（如法线、深度）烘焙到网格体上，用于生成纹理或其他数据。 | `UBakeRenderCaptureOutputs` (来自关联模块) |

### 使用示例（蓝图描述）

1.  在蓝图编辑器中打开或创建一个数据流图表。
2.  在节点列表中搜索“Geometry”或“Mesh Boolean”，你将找到由该插件注册的几何处理节点。
3.  例如，将一个 **“网格体布尔 (Mesh Boolean)”** 节点拖入图表。该节点通常有两个输入（A 和 B）和一个输出（结果网格体）。
4.  将代表两个源网格体的节点输出（可能来自加载静态网格体节点或其他几何数据源）分别连接到布尔节点的 A 和 B 输入端。
5.  配置布尔节点的操作类型（如并集、交集、差集）。
6.  将布尔节点的输出连接到后续节点，如保存网格体节点或渲染节点。

## C++ 用法

该插件的 C++ 用法主要集中在为其数据流系统扩展自定义节点，或在 C++ 中调用其提供的实用函数。

### 头文件引入

```cpp
// 引入数据流节点的基类或特定功能类
#include "Dataflow/DataflowNode.h"
#include "Dataflow/DataflowMedialSkeleton.h" // 如果使用骨架数据
```

### 基本用法（来自测试用例）

以下代码展示了如何在数据流节点内部调用几何处理功能。此模式常用于创建自定义数据流节点。

```cpp
// 假设在一个自定义数据流节点类的求值函数中
// (来源: 基于 Dataflow 节点开发的通用模式)

// 1. 获取输入的几何数据（例如，从一个输入引脚）
const FDataflowMesh& InMesh = GetValue<FDataflowMesh>(...); // 从输入端获取

// 2. 准备几何处理所需的参数（例如，使用插件提供的选项结构体）
FDataflowMeshBooleanOptions BooleanOptions;
BooleanOptions.Operation = EDataflowMeshBooleanOps::Difference; // 设置操作为差集
// ... 设置其他参数

// 3. 调用几何处理函数（这些函数封装自 GeometryProcessing 插件）
// 注意：具体的函数调用依赖于插件内部的实现
// FDataflowMesh OutMesh = DataflowMeshBoolean(InMesh, InOtherMesh, BooleanOptions);

// 4. 将处理结果设置到输出引脚
// SetValue<FDataflowMesh>(OutMesh, ...);
```

### 进阶用法

结合多个节点构建处理链。例如，一个节点生成基础几何体，另一个节点应用布尔运算，第三个节点进行减面。

```cpp
// 在数据流图表中，这些节点被连接起来，形成管线
// 代码层面，每个节点独立运行，通过数据流的边传递数据
// 进阶用法更多体现在设计数据流图表本身，而非编写额外的 C++ 代码。
// 若需创建全新的、复合功能的节点，则是 C++ 进阶用法的典型场景。
```

## Demo 示例

以下是一个假设的、简单的自定义数据流节点头文件示例，它演示了如何集成几何处理功能。

```cpp
// MyCustomGeometryNode.h
#pragma once

#include "Dataflow/DataflowNode.h"
#include "GeometryProcessing.h" // 假设使用了某个几何处理函数

USTRUCT()
struct FMyCustomGeometryData
{
    GENERATED_USTRUCT_BODY()

    UPROPERTY()
    TArray<FVector> Vertices;

    UPROPERTY()
    TArray<int32> Triangles;
};

UCLASS()
class UMyCustomGeometryNode : public UDataflowNode
{
    GENERATED_BODY()

public:
    UMyCustomGeometryNode();

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Output) const override;

    // 输入引脚
    UPROPERTY(EditAnywhere, Category = "Input")
    FMyCustomGeometryData InputGeometry;

    // 输出引脚
    UPROPERTY(VisibleAnywhere, Category = "Output")
    FMyCustomGeometryData OutputGeometry;

    // 用户参数
    UPROPERTY(EditAnywhere, Category = "Options")
    float ScaleFactor = 1.0f;
};
```

```cpp
// MyCustomGeometryNode.cpp
#include "MyCustomGeometryNode.h"
// 假设的几何处理函数
// #include "MyGeometryOperations.h"

UMyCustomGeometryNode::UMyCustomGeometryNode()
{
    // 注册输入输出引脚
    RegisterInputConnection(&InputGeometry);
    RegisterOutputConnection(&OutputGeometry);
}

void UMyCustomGeometryNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Output) const
{
    // 获取输入数据
    const FMyCustomGeometryData& InData = Context.GetValue(InputGeometry);

    // 执行几何处理（此处为示例）
    FMyCustomGeometryData ProcessedData = InData; // 复制一份
    // MyGeometryOperations::ScaleMesh(ProcessedData.Vertices, ScaleFactor); // 示例操作

    // 设置输出数据
    Context.SetValue(OutputGeometry, ProcessedData);
}
```

## 模块依赖

从 `Build.cs` 分析，要使用此插件的功能，你的模块需要依赖以下特定模块：

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供核心的几何处理算法，如网格布尔、简化、细分等。 |
| `MeshConversion` | 处理不同网格体格式（如渲染网格体、动态网格体、静态网格体）之间的数据转换。 |
| `Dataflow` | 基础数据流框架模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `da753042` | Dataflow geometry nodes plugin : remove beta status | 移除了几何数据流节点插件的测试版状态标记 |
| 2026-05-12 | `45745f54` | Dataflow: | （提交信息不完整，推测为数据流相关的更新） |
| 2026-04-17 | `49f946b4` | [Dataflow] | （提交信息不完整，推测为数据流相关的更新） |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 更新了大量数据流节点以使用新的渲染系统 |
| 2025-12-11 | `2c27a203` | Minor cleanup of dataflow mesh boolean options | 对数据流网格体布尔选项进行了小清理 |

### 维护评价

该插件创建于 2025 年 1 月，相对年轻。从 Git 历史看，它处于 **活跃维护** 状态。最近的重大更新（2026 年 5 月）移除了其“测试版”标签，表明 Epic 认为其已具备一定的稳定性和功能完整性。更新内容包括功能扩展（集成新渲染系统）和优化（清理选项）。鉴于其来自 Epic 官方且持续更新，**推荐关注和评估使用**。但需注意，它位于 `Experimental` 目录下，API 和功能在未来版本中仍可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryDataflow)
- [官方文档]()（暂无）
- [测试用例]()（插件目录内未发现测试文件，测试可能位于 `Engine/Tests` 或通过其他插件集成测试）