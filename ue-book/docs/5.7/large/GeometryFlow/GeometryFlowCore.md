# GeometryFlow

> Geometry DataFlow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流图 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（源节点、设置结构体） |
| 模块 | `GeometryFlowCore` (Runtime), `GeometryFlowMeshProcessing` (Runtime), `GeometryFlowMeshProcessingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryFlow) | |

## 用途

GeometryFlow 是一个实验性的 **几何处理数据流图** 框架。它允许开发者通过构建有向无环图（DAG）来定义和执行复杂的几何数据处理管线，类似于 UE 的 Dataflow 蓝图系统，但专门针对几何数据类型（如网格、设置、数学值等）。核心思想是将几何操作（如变换、布尔运算、网格生成）拆分为独立的节点，通过数据流动驱动计算，支持缓存、惰性求值和分支控制。

GeometryFlow 提供了一套基础节点框架（`GeometryFlowCore`），包括源节点（Source Node）、传输节点（Transfer Node）、二元操作节点（Binary Op）、开关节点（Switch Node）和带设置的变换节点（Transformer with Settings）。基于此，`GeometryFlowMeshProcessing` 模块提供了网格处理相关的具体节点（如网格简化、法线计算等），而 `GeometryFlowMeshProcessingEditor` 模块则使这些节点可在编辑器中使用。

该插件解决了传统 C++ 几何处理流程中硬编码逻辑、难以组合和复用的问题，允许以声明式方式构建可序列化、可缓存的几何处理图。

## 使用场景

- **构建自定义几何处理管线**：例如从输入网格生成简化版本，同时计算法线和 UV，通过开关节点在多个结果中动态选择。
- **参数化几何生成**：将用户输入的参数（如半径、分段数）通过源节点注入图，驱动网格生成节点。
- **编辑器工具集成**：利用 `GeometryFlowMeshProcessingEditor` 模块将处理图暴露给 Slate UI 或细节面板，实现交互式调节。
- **并行/延迟计算**：通过图的依赖分析，实现部分节点的并行求值或按需计算。

## 蓝图用法

本插件目前**未暴露**任何蓝图可调用节点或函数。图构建、节点注册、数据传递均通过 C++ API 完成。

以下 C++ 定义的结构体可被蓝图用作属性（通过 UPROPERTY），但无直接蓝图节点：

| 结构体 | 说明 | 数据标识符 |
|---|---|---|
| `FInt32Setting` | 整数设置 | `EDataTypes::IntegerStruct` |
| `FFloatSetting` | 浮点数设置 | `EDataTypes::FloatStruct` |
| `FDoubleSetting` | 双精度浮点设置 | `EDataTypes::DoubleStruct` |
| `FVector3fSetting` | 3维浮点向量设置 | `EDataTypes::Vector3fStruct` |
| `FVector3dSetting` | 3维双精度向量设置 | `EDataTypes::Vector3dStruct` |
| `FNameSetting` | 名称设置 | `EDataTypes::NameStruct` |

这些结构体可直接用于 UPROPERTY 并在细节面板编辑，作为节点属性的输入数据。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryFlowGraph.h"
#include "GeometryFlowTSourceNode.h"
#include "GeometryFlowCoreNodes.h"
#include "BaseNodes/BinaryOpLambdaNode.h"
#include "MathNodes/ArithmeticNodes.h"
```

### 基本用法

以下示例创建了一个简单的算数执行图：两个浮点源节点输入数值，通过加法节点输出结果。

```cpp
// 源自 GeometryFlow 内部测试用例片段（路径：Engine/Plugins/Experimental/GeometryFlow/...）

using namespace UE::GeometryFlow;

// 1. 创建图
FGraph Graph;

// 2. 创建源节点：浮点源节点 (设置初始值为 3.0 和 4.0)
FGraph::FHandle SourceA = Graph.AddNode<TSourceNodeBase<float, (int)EDataTypes::Float>>();
FGraph::FHandle SourceB = Graph.AddNode<TSourceNodeBase<float, (int)EDataTypes::Float>>();
Graph.ApplyToNodeOfType<TSourceNodeBase<float, (int)EDataTypes::Float>>(SourceA, [](auto& Node) { Node.UpdateSourceValue(3.0f); });
Graph.ApplyToNodeOfType<TSourceNodeBase<float, (int)EDataTypes::Float>>(SourceB, [](auto& Node) { Node.UpdateSourceValue(4.0f); });

// 3. 创建加法节点
FGraph::FHandle AddNode = Graph.AddNode<FAddFloatNode>();

// 4. 建立连接
Graph.MakeConnection(SourceA, TSourceNodeBase<float, (int)EDataTypes::Float>::OutParamValue(),
                     AddNode, TBinaryOpAddNode<float, (int)EDataTypes::Float>::InParamArg1());
Graph.MakeConnection(SourceB, TSourceNodeBase<float, (int)EDataTypes::Float>::OutParamValue(),
                     AddNode, TBinaryOpAddNode<float, (int)EDataTypes::Float>::InParamArg2());

// 5. 添加输出节点（可选：直接获取加法节点的输出）
FGraph::FHandle Output = Graph.AddNode<TSourceNodeBase<float, (int)EDataTypes::Float>>(); // 仅作为输出占位
Graph.MakeConnection(AddNode, TBinaryOpAddNode<float, (int)EDataTypes::Float>::OutParamResult(),
                     Output, TSourceNodeBase<float, (int)EDataTypes::Float>::OutParamValue());

// 6. 评估图（自动按依赖顺序求值）
TUniquePtr<FEvaluationInfo> EvalInfo = MakeUnique<FEvaluationInfo>();
FNamedDataMap DummyInputs; // 无外部输入
FNamedDataMap Outputs;
Graph.Evaluate(DummyInputs, Outputs, EvalInfo);

// 7. 从输出节点提取结果
float Result;
TSafeSharedPtr<IData> OutputData = Outputs.GetData(TSourceNodeBase<float, (int)EDataTypes::Float>::OutParamValue());
OutputData->GetDataCopy(Result, (int)EDataTypes::Float);
// Result == 7.0
```

### 进阶用法

#### 使用开关节点实现条件分支

`TSwitchNode` 可以从多个输入源中选择一个作为输出，只对选中的输入进行求值。

```cpp
using MySwitchNode = TSwitchNode<FDynamicMesh3, 3, (int)EMeshProcessingDataTypes::DynamicMesh>;

FGraph::FHandle SwitchNode = Graph.AddNode<MySwitchNode>();

// 创建三个网格源节点 (Mesh0, Mesh1, Mesh2)
FGraph::FHandle MeshSrc[3];
for (int i = 0; i < 3; ++i)
{
    MeshSrc[i] = Graph.AddNode<TSourceNodeBase<FDynamicMesh3, (int)EMeshProcessingDataTypes::DynamicMesh>>();
    // 设置初始网格...
}

// 连接所有输入到开关节点
for (int i = 0; i < 3; ++i)
{
    Graph.MakeConnection(MeshSrc[i],
        TSourceNodeBase<FDynamicMesh3, (int)EMeshProcessingDataTypes::DynamicMesh>::OutParamValue(),
        SwitchNode,
        MySwitchNode::InParamValue(i));
}

// 设置开关索引为 1，只求值第二个输入
UpdateSwitchNodeInputIndex<MySwitchNode>(Graph, SwitchNode, 1);

// 评估后，仅 MeshSrc[1] 被求值，其输出作为开关输出
```

#### 使用带设置的变换节点

`TTransformerWithSettingsNode` 接收输入数据、设置参数，执行变换后输出新数据。

```cpp
// 假设我们已经有一个 TExampleTransformNode（派生自 TTransformerWithSettingsNode）
// 该节点以 FDynamicMesh3 为输入和输出，以 FExampleSettings 为设置

FGraph::FHandle InputMesh = /* 网格源节点句柄 */;
FGraph::FHandle SettingsSource = Graph.AddNode<TSourceNodeBase<FExampleSettings, FExampleSettings::DataTypeIdentifier>>();
Graph.ApplyToNodeOfType<TSourceNodeBase<FExampleSettings, FExampleSettings::DataTypeIdentifier>>(
    SettingsSource, [](auto& Node) {
        FExampleSettings S;
        S.Scale = 2.0f;
        Node.UpdateSourceValue(S);
    });

FGraph::FHandle TransformNode = Graph.AddNode<TExampleTransformNode>();

Graph.MakeConnection(InputMesh, /* 输出名 */, TransformNode, TTransformerWithSettingsNode::InParamInput());
Graph.MakeConnection(SettingsSource, TSourceNodeBase::OutParamValue(), TransformNode, TTransformerWithSettingsNode::InParamSettings());

// 评估后 TransformNode 输出变换后的网格
```

### 进阶用法（图序列化）

`FGraph` 支持通过 `FArchive` 序列化/反序列化整个 DAG。这要求所有节点类型已在 `FNodeFactory` 中注册。

```cpp
FBufferArchive Ar;
FGraph::FHandle RootHandle = /* 某输出节点句柄 */;

// 序列化
Graph.Serialize(Ar); // 序列化全部图

// 反序列化到新图
FMemoryReader Reader(Ar);
FGraph NewGraph;
NewGraph.Serialize(Reader);
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示了创建、连接并求值一个简单的数学加法图。该示例不依赖其他模块（仅 GeometryFlowCore）。

```cpp
// GeometryFlowDemo.h
#pragma once

#include "GeometryFlowGraph.h"
#include "GeometryFlowTSourceNode.h"
#include "GeometryFlowCoreNodes.h"
#include "BaseNodes/BinaryOpLambdaNode.h"
#include "MathNodes/ArithmeticNodes.h"

class FGeometryFlowDemo
{
public:
    static float RunAdditionGraph(float A, float B);
};
```

```cpp
// GeometryFlowDemo.cpp
#include "GeometryFlowDemo.h"

float FGeometryFlowDemo::RunAdditionGraph(float A, float B)
{
    using namespace UE::GeometryFlow;

    FGraph Graph;

    // 创建源节点 (浮点)
    FGraph::FHandle SrcA = Graph.AddNode<TSourceNodeBase<float, (int)EDataTypes::Float>>();
    FGraph::FHandle SrcB = Graph.AddNode<TSourceNodeBase<float, (int)EDataTypes::Float>>();

    Graph.ApplyToNodeOfType<TSourceNodeBase<float, (int)EDataTypes::Float>>(SrcA, [A](auto& Node) { Node.UpdateSourceValue(A); });
    Graph.ApplyToNodeOfType<TSourceNodeBase<float, (int)EDataTypes::Float>>(SrcB, [B](auto& Node) { Node.UpdateSourceValue(B); });

    // 创建加法节点
    FGraph::FHandle Add = Graph.AddNode<FAddFloatNode>();

    Graph.MakeConnection(SrcA, TSourceNodeBase<float, (int)EDataTypes::Float>::OutParamValue(),
                         Add, TBinaryOpAddNode<float, (int)EDataTypes::Float>::InParamArg1());
    Graph.MakeConnection(SrcB, TSourceNodeBase<float, (int)EDataTypes::Float>::OutParamValue(),
                         Add, TBinaryOpAddNode<float, (int)EDataTypes::Float>::InParamArg2());

    // 评估
    TUniquePtr<FEvaluationInfo> EvalInfo = MakeUnique<FEvaluationInfo>();
    FNamedDataMap Outputs;
    Outputs.Add(TSourceNodeBase<float, (int)EDataTypes::Float>::OutParamValue(), nullptr); // 占位
    Graph.Evaluate(FNamedDataMap(), Outputs, EvalInfo);

    // 获取加法节点输出（直接从图内部节点输出的数据缓存）
    float Result = 0.0f;
    TArray<FGraph::FConnection> Connections;
    // 简单做法：直接通过输出节点获取，但此处我们假设图已缓存结果，直接读取 Add 节点的输出
    TSafeSharedPtr<IData> OutputData = Graph.GetNodeOutput(Add, TBinaryOpAddNode<float, (int)EDataTypes::Float>::OutParamResult());
    if (OutputData)
    {
        OutputData->GetDataCopy(Result, (int)EDataTypes::Float);
    }
    return Result;
}
```

## 模块依赖

**省略常见依赖**（Core, CoreUObject, Engine 等已自动包含）。以下列出本插件特有的、非标准依赖：

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供网格处理核心类型（如 `FDynamicMesh3`）和算法 |
| `MeshModelingToolsetExp` | 提供实验性建模工具集，用于网格操作节点 |

如果需要使用 `GeometryFlowCore`，你的模块的 `Build.cs` 中需添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "GeometryFlowCore",
    // 如果使用 MeshProcessing 节点，还需：
    // "GeometryFlowMeshProcessing",
    // "GeometryProcessing"
});
```

## 维护状态

### 近期更新

- 2025-07-10 `9803c443` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files.
- 2025-05-31 `52e3dac1` Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types.
- 2024-12-16 `dbb51bc5` GeometryFlow: clean-up node registration.
- 2024-12-13 `1d69cf7b` Geometry Processing Unit Tests: eliminate warnings and other problems in preparation for enabling tests.
- 2024-11-10 `66e9bb39` Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base.

### 维护评价

- **创建时间**：2024年11月，至今约 1 年。
- **近期更新**：最近 6 个月内有两次代码风格/修复更新（2025-07 和 2025-05），但无功能上的新增。
- **活跃度**：维护频率中等，主要停留在清理和修复阶段，未出现大规模新功能迭代。
- **已知限制**：该插件标记为 **实验性**（`IsExperimentalVersion=true`），API 可能发生破坏性变更；缺少蓝图支持，仅适用于 C++ 集成；节点注册机制依赖单例 `FNodeFactory`，在多图或动态卸载场景下需注意生命周期。
- **推荐使用**：适合需要自定义几何处理管线的 C++ 开发者，但不适合生产环境中的高稳定性需求。建议在非核心或原型项目中使用。长期未更新可能意味着处于维护不活跃状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryFlow)
- [官方文档] 无（未提供 DocsURL）
- [测试用例示例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryFlow/Source/GeometryFlowMeshProcessing/Tests)（需确认路径是否存在，当前仅有模块头文件）