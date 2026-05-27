# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 肌肉模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Dataflow 节点、蓝图资产） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 插件提供了一套基于 Chaos 物理引擎的软组织（肌肉、脂肪等）模拟框架。它通过 Dataflow 图系统，允许用户从网格数据（如静态网格、骨骼网格）生成可模拟的四面体（Tetrahedron）网格，并定义肌肉纤维方向、绑定约束、激活参数等，从而在运行时实现物理真实的肌肉收缩、膨胀和形变效果。核心目标是解决生物角色在动画驱动下，其内部软组织如何物理响应和形变的问题。

## 使用场景

- 你正在制作一个需要高度真实肌肉变形的生物角色（如怪物、动物） → 使用 ChaosFlesh 构建其内部四面体肌肉系统。
- 你需要模拟角色在运动时，皮肤与内部肌肉之间的绑定和碰撞效果 → 使用 `GenerateSurfaceBindings` 和 `SetVertexTrianglePositionTargetBinding` 等节点。
- 你想要控制特定肌肉群的收缩和激活效果（例如二头肌隆起） → 使用 `ComputeFiberField` 和 `SetMuscleActivationParameter` 节点。
- 你需要在 Dataflow 图中可视化肌肉纤维方向或绑定效果 → 使用 `VisualizeFiberField` 等可视化节点。

## 蓝图用法

ChaosFlesh 主要通过 Unreal Engine 的 Dataflow 系统使用，其提供的节点在编辑器中作为蓝图节点出现。这些节点通常用于构建 `Chaos Flesh Asset` 的几何数据和模拟参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateTetrahedron` | 从输入的表面网格（源集合）生成四面体网格。支持 IsoStuffing 和 TetWild 两种算法。 | `FCreateTetrahedronDataflowNode` |
| `ComputeFiberField` | 根据指定的肌肉起止点（Origin/Insertion），计算每个四面体的纤维方向。 | `FComputeFiberFieldNode` |
| `SetMuscleActivationParameter` | 设置肌肉收缩的全局或逐肌肉自定义参数，如收缩体积比、纤维长度比等。 | `FSetMuscleActivationParameterNode` |
| `GenerateSurfaceBindings` | 将四面体网格的顶点绑定到输入的渲染网格（静态/骨骼网格）表面。 | `FGenerateSurfaceBindings` |
| `SetFleshBonePositionTargetBinding` | 将四面体网格的顶点绑定到骨骼网格的骨头上（运动学或弱约束）。 | `FSetFleshBonePositionTargetBindingDataflowNode_v2` |
| `SetVertexTrianglePositionTargetBinding` | 在不同几何体表面之间创建点-三角形弱约束（弹簧），用于模拟肌肉间连接。 | `FSetVertexTrianglePositionTargetBindingDataflowNode` |
| `MakeFleshAsset` | 将一个或多个LOD的四面体网格数据打包成最终的 `FleshAsset`。 | `FMakeFleshAssetNode` |
| `VisualizeFiberField` | 可视化每个四面体的纤维方向向量。 | `FVisualizeFiberFieldNode` |

### 使用示例（蓝图描述）

典型的 ChaosFlesh Dataflow 图会遵循以下流程：
1.  **输入**：使用 `GetFleshAsset` 或其他节点获取或创建一个 `FManagedArrayCollection`（代表四面体网格数据）。
2.  **几何构建**：连接 `CreateTetrahedron` 节点，从一个源集合（如骨骼网格的几何数据）生成四面体。
3.  **参数设置**：连接 `ComputeFiberField` 节点计算纤维方向；连接 `SetFleshDefaultProperties` 或 `SetMuscleActivationParameter` 设置材料和激活参数。
4.  **绑定**：连接 `GenerateSurfaceBindings` 将四面体绑定到渲染网格；使用 `SetFleshBonePositionTargetBinding` 绑定到骨骼。
5.  **输出**：最后连接到 `FleshAssetTerminal` 或 `MakeFleshAsset` 节点，生成或更新 `FleshAsset`。

所有节点都通过 `Collection` 引脚进行串联和数据传递。

## C++ 用法

ChaosFlesh 的节点主要通过 Dataflow 宏系统进行注册和使用，开发者通常不需要直接继承这些节点，而是通过蓝图使用。但是，了解其 C++ 结构有助于扩展或调试。

### 头文件引入

```cpp
#include "ChaosFleshNodes.h"
// 或特定节点头文件
#include "Dataflow/ChaosFleshCreateTetrahedronNode.h"
#include "Dataflow/ChaosFleshComputeFiberFieldNode.h"
```

### 基本用法

以下是定义一个简单 Dataflow 节点的示例结构，类似于插件中的节点。
*来源: `ChaosFleshNodes` 模块中各节点定义文件。*

```cpp
// MyChaosFleshNode.h
#include "Dataflow/DataflowNode.h"
#include "ManagedArrayCollection.h"

USTRUCT(meta = (DataflowFlesh))
struct FMyCustomFleshNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomFleshNode, "MyCustomFlesh", "Flesh", "")

public:
    // 输入/输出的四面体网格数据（通常作为Passthrough）
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    // 一个可编辑的参数
    UPROPERTY(EditAnywhere, Category = "MyNode")
    float MyParameter = 1.0f;

    FMyCustomFleshNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        // 注册引脚
        RegisterInputConnection(&Collection);
        RegisterOutputConnection(&Collection, &Collection);
    }

    // 核心计算逻辑
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
    {
        if (Out == &Collection)
        {
            // 获取输入集合
            FManagedArrayCollection& InCollection = Context.GetValue(Collection);
            // ... 在 InCollection 上进行操作 ...
            // 设置输出（由于是 Passthrough，通常直接赋值）
            Context.SetValue(Collection, InCollection);
        }
    }
};
```

### 进阶用法

结合多个节点进行复杂数据流处理。
*来源: 结合 `FCreateTetrahedronDataflowNode` 和 `FComputeFiberFieldNode` 的逻辑。*

```cpp
// 伪代码：在某个自定义节点的Evaluate中模拟串联操作
virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
{
    // 1. 先处理输入集合，获取几何数据
    FManagedArrayCollection& GeometryCollection = Context.GetValue(InputCollection);
    
    // 2. 假设我们内部调用了类似 CreateTetrahedron 的逻辑，生成四面体
    // FFleshCollection& FleshCollection = ... (从GeometryCollection转换或新建)
    // EvaluateIsoStuffing(...) 或 EvaluateTetWild(...)
    
    // 3. 然后可以类似调用 Fiber Field 的计算逻辑
    // ComputeFiberField(FleshCollection.GetElements(), ..., Origins, Insertions, FiberDirections);
    
    // 4. 将结果存入输出集合
    FManagedArrayCollection& OutputCollection = Context.GetValue(OutputCollection);
    // ... 将计算结果写入 OutputCollection ...
}
```

## Demo 示例

以下是一个最小的 ChaosFlesh Dataflow 节头文件和实现示例，该节点仅将输入的集合传递到输出，并添加一个简单的日志。
*注意：Build.cs 中的模块依赖已在相关章节说明。*

**MyChaosFleshDemoNode.h**
```cpp
// Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFleshNodes/Public/MyChaosFleshDemoNode.h
#pragma once

#include "Dataflow/DataflowNode.h"
#include "ManagedArrayCollection.h"

USTRUCT(meta = (DataflowFlesh))
struct FMyChaosFleshDemoNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyChaosFleshDemoNode, "MyDemoNode", "Flesh", "Demo")

public:
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DisplayName = "Collection", DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    UPROPERTY(EditAnywhere, Category = "Demo")
    bool bLogMessage = true;

    FMyChaosFleshDemoNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

**MyChaosFleshDemoNode.cpp**
```cpp
// Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFleshNodes/Private/MyChaosFleshDemoNode.cpp
#include "MyChaosFleshDemoNode.h"
#include "Dataflow/DataflowCore.h"

FMyChaosFleshDemoNode::FMyChaosFleshDemoNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FDataflowNode(InParam, InGuid)
{
    RegisterInputConnection(&Collection);
    RegisterOutputConnection(&Collection, &Collection);
}

void FMyChaosFleshDemoNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    if (Out == &Collection)
    {
        FManagedArrayCollection InCollection = Context.GetValue(Collection);
        if (bLogMessage)
        {
            UE_LOG(LogTemp, Log, TEXT("FMyChaosFleshDemoNode: Processing Collection with %d vertices."), 
                InCollection.NumElements(FName("Vertices")));
        }
        Context.SetValue(Collection, InCollection);
    }
}
```

## 模块依赖

要使用 `ChaosFleshNodes` 模块，你的模块（如编辑器工具或运行时组件）通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ChaosFleshEngine` | 提供 `FFleshCollection`、`UFleshAsset` 等核心数据类型和资产类。 |
| `GeometryCollectionNodes` | 提供 `FManagedArrayCollection`、`FDataflowVertexSelection` 等基础几何数据流类型。 |
| `Dataflow` | Dataflow 框架核心模块，提供 `FDataflowNode` 基类。 |
| `GeometryCollectionEngine` | 可能与几何体运行时数据处理相关。 |
| `Chaos` | Chaos 物理引擎底层库。 |

*常见依赖如 Core, CoreUObject, Engine 等已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 产生警告的代码。 |
| 2026-05-12 | `981bc9da` | Dataflow: | （简短提交信息，可能与 Dataflow 框架更新相关） |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理肌肉纤维场生成节点的代码。 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复掩码缓冲区赋值错误。 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 弃用 Flesh Asset 中的 StaticMesh 属性。 |

### 维护评价

**活跃维护中**。该插件创建于 2022 年，是一个相对较新的实验性插件。从近期（2026年5月）的提交记录来看，开发团队仍在积极进行代码清理、bug 修复和 API 迭代（如弃用旧属性）。虽然标记为实验性且默认未启用，但它显然是 Epic 在物理角色模拟领域的一项重要投入。

**推荐使用**：对于需要生物力学模拟的高级项目（尤其是结合 Chaos 物理和几何体集合的项目），ChaosFlesh 是目前 UE 官方提供的主要解决方案。但由于其**实验性状态**和**默认禁用**的特性，使用者需要自行承担 API 可能发生变化的风险，并准备好进行适配工作。它不适合寻求开箱即用、稳定功能的入门级项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- [官方文档]() (当前为空，可关注 Epic 官方文档或开发者社区更新)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh/Tests) (可能存在)