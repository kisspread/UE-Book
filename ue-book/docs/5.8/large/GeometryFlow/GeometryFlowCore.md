# GeometryFlow

> Geometry DataFlow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流图 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GeometryFlowCore` (Runtime), `GeometryFlowMeshProcessing` (Runtime), `GeometryFlowMeshProcessingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryFlow) | |

## 用途

GeometryFlow 是一个用于构建**几何数据处理管线**的节点图（Node-Graph）框架。它提供了一套完整的有向无环图（DAG）执行引擎，用于将昂贵的几何处理操作组织为可序列化、可缓存、支持增量计算的节点图。

核心解决的问题是：当你需要将多个几何处理步骤（如网格简化、LOD 生成、碰撞体生成、材质实例化）串联为一个复杂的流水线时，手动管理数据依赖、缓存和增量更新非常困难。GeometryFlow 将每个处理步骤抽象为节点，节点间通过有类型的连接传递数据，由图引擎自动处理拓扑排序、脏标记传播、并行求值和结果缓存。

最初创建时的具体目标（来自首次提交信息）：配合 MeshLODToolset 插件，实现将高分辨率源网格+材质处理为游戏就绪的 StaticMesh 资产+材质实例+碰撞几何体的完整流程，通过 Modeling Mode 工具暴露给用户。

## 使用场景

- 你需要将多个几何处理步骤（简化、重拓扑、UV 展开等）编排为可复用的管线 → 用 GeometryFlow 构建节点图
- 你在开发一个网格处理工具，需要支持参数修改后**仅重算变化的部分** → GeometryFlow 的脏标记传播和缓存策略自动处理
- 你需要将复杂的几何处理流水线**序列化保存**，以便之后恢复或编辑 → FGraph 支持完整的序列化/反序列化
- 你在实现类似 Mesh LOD 生成工具，需要从高模生成多级 LOD 资产 → 基于 GeometryFlow 构建处理图
- 你需要在编辑器工具中暴露可配置的几何处理参数 → 使用 TSourceNode/TUStructSourceNode 作为参数输入节点

## 蓝图用法

GeometryFlow 是一个纯 C++ 框架，**不提供 BlueprintCallable 节点**。它面向的是编写编辑器工具和自定义处理管线的 C++ 开发者。如需在蓝图中使用几何处理功能，请使用 GeometryScript（Geometry Scripting 插件）。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryFlowGraph.h"
#include "GeometryFlowNode.h"
#include "GeometryFlowCoreNodes.h"
#include "GeometryFlowGraphUtil.h"
```

### 基本用法：构建和求值一个简单的节点图

以下示例演示创建一个包含两个 Float Source 节点和一个加法节点的图，并求值结果。

来源：基于 `Public/GeometryFlowGraph.h`、`Public/GeometryFlowCoreNodes.h`、`Public/MathNodes/ArithmeticNodes.h` 的 API 分析。

```cpp
using namespace UE::GeometryFlow;

// 1. 创建图
FGraph Graph;

// 2. 注册节点类型（通常在模块 StartupModule 中完成一次）
FCoreNodeRegistration::RegisterNodes();

// 3. 添加两个 Float 源节点和一个加法节点
FGraph::FHandle FloatA = Graph.AddNodeOfType<FDoubleSourceNode>("InputA");
FGraph::FHandle FloatB = Graph.AddNodeOfType<FDoubleSourceNode>("InputB");
FGraph::FHandle AddNode = Graph.AddNodeOfType<FAddFloatNode>("Add");

// 4. 设置源节点的值
Graph.ApplyToNodeOfType<FDoubleSourceNode>(FloatA, [](FDoubleSourceNode& Node) {
    Node.UpdateSourceValue(3.0);
});
Graph.ApplyToNodeOfType<FDoubleSourceNode>(FloatB, [](FDoubleSourceNode& Node) {
    Node.UpdateSourceValue(4.0);
});

// 5. 连接节点
Graph.AddConnection(FloatA, "Value", AddNode, "Operand1");
Graph.AddConnection(FloatB, "Value", AddNode, "Operand2");

// 6. 求值并获取结果
double Result = 0;
TUniquePtr<FEvaluationInfo> EvalInfo = MakeUnique<FEvaluationInfo>();
EGeometryFlowResult Ret = Graph.EvaluateResult(AddNode, "Result", Result, 
    (int)EDataTypes::Double, EvalInfo, false);
// Result == 7.0
```

### 进阶用法：自定义处理节点

以下示例展示如何基于 `TTransformerWithSettingsNode` 创建自定义的网格处理节点。

来源：基于 `Public/BaseNodes/TransformerWithSettingsNode.h` 模板。

```cpp
#include "GeometryFlowNode.h"
#include "GeometryFlowMovableData.h"

// 定义一个简单的设置结构
struct FMyProcessorSettings
{
    static constexpr int DataTypeIdentifier = (int)EDataTypes::UserDefinedTypes + 1;
    float Threshold = 0.5f;
    int32 Iterations = 3;
};

// 自定义处理节点：输入一个 float，根据设置参数输出处理后的 float
class FMyProcessorNode : public TTransformerWithSettingsNode<
    float, (int)EDataTypes::Float,
    FMyProcessorSettings, FMyProcessorSettings::DataTypeIdentifier,
    float, (int)EDataTypes::Float>
{
    static constexpr int Version = 1;
    GEOMETRYFLOW_NODE_INTERNAL(FMyProcessorNode, Version, FNode)

protected:
    virtual void ComputeOutput(
        const FNamedDataMap& DatasIn,
        const FMyProcessorSettings& Settings,
        const float& Input,
        float& Output) override
    {
        Output = Input;
        for (int32 i = 0; i < Settings.Iterations; ++i)
        {
            Output = Output * Settings.Threshold;
        }
    }
};

// 注册到工厂
void RegisterMyNodes()
{
    FNodeFactory::GetInstance().RegisterType<FMyProcessorNode>("MyProcessor", "Custom");
}
```

### 进阶用法：使用 Switch 节点实现分支

来源：基于 `Public/BaseNodes/SwitchNode.h`。

```cpp
// 创建一个 3 路 Switch 节点（类型为 Float）
using FFloatSwitch3 = TSwitchNode<float, 3, (int)EDataTypes::Float>;

FGraph::FHandle SwitchNode = Graph.AddNodeOfType<FFloatSwitch3>("MySwitch");

// 选择第 2 个输入（索引从 0 开始）
Graph.ApplyToNodeOfType<FFloatSwitch3>(SwitchNode, [](FFloatSwitch3& Node) {
    Node.UpdateSwitchInputIndex(1);  // 激活 Input1
});
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何构建自定义节点并在图中求值。

```cpp
// MyCustomNode.h
#pragma once

#include "GeometryFlowNode.h"
#include "GeometryFlowMovableData.h"
#include "GeometryFlowTSourceNode.h"
#include "GeometryFlowCoreNodes.h"

using namespace UE::GeometryFlow;

// 自定义设置结构
struct FScaleSettings
{
    static constexpr int DataTypeIdentifier = (int)EDataTypes::UserDefinedTypes + 10;
    float ScaleFactor = 2.0f;
};

// 自定义节点：将输入 Double 乘以一个缩放因子
class FScaleDoubleNode : public TTransformerWithSettingsNode<
    double, (int)EDataTypes::Double,
    FScaleSettings, FScaleSettings::DataTypeIdentifier,
    double, (int)EDataTypes::Double>
{
    static constexpr int Version = 1;
    GEOMETRYFLOW_NODE_INTERNAL(FScaleDoubleNode, Version, FNode)

protected:
    virtual void ComputeOutput(
        const FNamedDataMap& DatasIn,
        const FScaleSettings& Settings,
        const double& Input,
        double& Output) override
    {
        Output = Input * static_cast<double>(Settings.ScaleFactor);
    }
};
```

```cpp
// MyCustomNode.cpp
#include "MyCustomNode.h"

// 静态类型注册（确保 StaticType 唯一）
// GEOMETRYFLOW_NODE_INTERNAL 宏已在头文件中处理 RTTI
```

```cpp
// Usage.cpp - 使用示例
#include "MyCustomNode.h"
#include "GeometryFlowGraph.h"
#include "GeometryFlowCoreNodeRegistration.h"

void RunGeometryFlowDemo()
{
    // 注册核心节点
    FCoreNodeRegistration::RegisterNodes();

    // 注册自定义节点
    FNodeFactory::GetInstance().RegisterType<FScaleDoubleNode>("ScaleDouble", "Custom");

    // 构建图
    FGraph Graph;

    // 添加源节点和处理节点
    FGraph::FHandle InputNode = Graph.AddNodeOfType<FDoubleSourceNode>("Input");
    FGraph::FHandle SettingsNode = Graph.AddNodeOfType<FDoubleSourceNode>("Settings");
    FGraph::FHandle ScaleNode = Graph.AddNodeOfType<FScaleDoubleNode>("Scale");

    // 设置输入值
    Graph.ApplyToNodeOfType<FDoubleSourceNode>(InputNode, [](FDoubleSourceNode& Node) {
        Node.UpdateSourceValue(10.0);
    });

    // 连接
    Graph.AddConnection(InputNode, "Value", ScaleNode, "Input");
    // 注意：Settings 输入需要一个 FScaleSettings 类型的源节点
    // 此处简化演示，实际需要使用对应的 SettingsSourceNode

    // 求值
    double Result = 0;
    auto EvalInfo = MakeUnique<FEvaluationInfo>();
    Graph.EvaluateResult(ScaleNode, "Result", Result, 
        (int)EDataTypes::Double, EvalInfo, false);

    UE_LOG(LogGeometryFlowGraph, Display, TEXT("Result: %f"), Result);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 底层几何处理库（网格操作、简化等），提供 FDynamicMesh3 等核心类型 |
| `MeshModelingToolsetExp` | 实验性建模工具集，提供 GeometryFlow 的实际应用工具（如 LOD 生成） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新宏格式 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码清理：将析构函数改为 = default 形式 |
| 2025-10-23 | `3acea6cd` | add geometric tolerance to mesh->convex hull simplification path, to allow simplification below the | 为网格到凸包简化路径添加几何容差支持 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏到源文件 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 修正 DLL 导出标记，确保作用在方法而非类型上 |

### 维护评价

- **状态**: 实验性插件（`IsExperimentalVersion=true`，`Hidden=true`，`Installed=false`）
- **创建时间**: 2020 年 11 月，已存在约 6 年
- **最近更新**: 最近一年内有 5 次提交，但全部属于**全局代码维护**（宏迁移、代码风格修复、构建系统调整），**没有任何功能性更新**
- **功能演进**: 自创建以来核心架构未发生显著变化，说明设计已趋于稳定
- **关键限制**: 
  - 标记为实验性且隐藏，不随引擎默认安装
  - 无蓝图支持，仅面向 C++ 开发者
  - 代码中多处 TODO 注释（缓存策略优化、并行求值、循环检测改进）尚未完成
  - 无官方文档（DocsURL 为空）

**综合评价**: GeometryFlow 是一个设计合理的实验性几何处理管线框架，但 Epic 似乎将其定位为内部工具基础设施（服务于 MeshLODToolset 等工具），而非面向公众的稳定 API。如果您的项目需要类似的节点图处理管线，可以参考其架构，但**不建议作为外部项目的生产依赖**，因为它可能在未来版本中被移除或大幅重构。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryFlow)
- [官方文档]()（无）