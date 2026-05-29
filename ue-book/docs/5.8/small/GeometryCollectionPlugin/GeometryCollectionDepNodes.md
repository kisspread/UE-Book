# Geometry Collection Dep Nodes

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何集合数据流节点 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点） |
| 模块 | `GeometryCollectionDepNodes` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

该插件提供了一系列 **数据流（Dataflow）节点**，用于在运行时或编辑器中操作 `GeometryCollection` 资产。这些节点并非独立的蓝图或C++ API，而是作为更大型的 **Chaos 破坏系统（Chaos Destruction）** 及 **程序化破坏工作流** 中的构建块。它们的核心功能是实现 **几何集合之间的数据传输和属性操作**，例如：
1.  从一个几何集合（`GeometryCollection`）的源三角形网格向另一个目标集合传输顶点标量属性（如权重、温度等）。
2.  根据顶点选择集或浮点数组设置几何集合的顶点颜色，用于可视化调试。

这些节点是 UE5 早期 Chaos 破坏系统数据流架构的一部分，旨在提供比蓝图脚本更高效、更灵活的几何数据操作方式。

## 使用场景

-   **程序化破坏工作流**：在 Dataflow 编辑器中构建复杂的破坏资产准备和预处理流程。例如，在程序化生成大量破碎网格后，将损伤权重从一个“烘焙”好的集合传输到新生成的集合上。
-   **几何集合属性操作**：需要批量修改或传递几何集合的顶点属性（如颜色、自定义 float 属性）时，使用这些 Dataflow 节点进行处理。
-   **可视化调试**：将复杂的数值数据（如选择集、计算出的标量场）转换为顶点颜色，以便在编辑器视口中直观地检查几何集合的状态。

## 蓝图用法

该插件的功能主要通过 **Dataflow 图** 暴露，而非传统的蓝图函数。这些 `USTRUCT` 定义的节点会在 Dataflow 编辑器中显示为可用节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TransferVertexScalarAttribute` | 将源集合的指定标量属性（`AttributeKey`）传输到目标集合的对应顶点。支持配置采样距离、衰减方式等。 | `FGeometryCollectionTransferVertexScalarAttributeNode` |
| `SetVertexColorInCollectionFromVertexSelection` | 根据输入的顶点选择集（`VertexSelection`），将集合的顶点颜色设置为“选中”或“未选中”颜色。 | `FSetVertexColorInCollectionFromVertexSelectionDataflowNode` |
| `SetVertexColorInCollectionFromFloatArray` | 根据输入的浮点数组（`FloatArray`）和缩放因子（`Scale`），设置集合的顶点颜色（通常将 float 值映射为颜色梯度）。 | `FSetVertexColorInCollectionFromFloatArrayDataflowNode` |

### 使用示例（Dataflow 图描述）

1.  在 **Dataflow 编辑器**中创建一个新的图表。
2.  从节点面板拖入 `TransferVertexScalarAttribute` 节点。
3.  将源 `GeometryCollection` 资产连接到节点的 `FromCollection` 输入引脚。
4.  将目标 `GeometryCollection` 资产连接到节点的 `Collection` 输入引脚。
5.  指定要传输的属性名称（`AttributeKey`），例如 “Damage”。
6.  根据需要调整 `Falloff`（衰减类型）、`SampleScale`（采样半径计算方式）和 `FalloffThreshold`（衰减阈值）等参数。
7.  将节点的 `Collection` 输出引脚连接到后续的保存或输出节点。

**注意**：所有列出的节点在代码中均被标记为 `Deprecated = "5.5"`，表示在 UE 5.5 版本后已被废弃。在新版本中，类似功能可能已迁移到 `GeometryCollectionNodes` 模块或其他更稳定的实现中。

## C++ 用法

虽然这些节点设计为通过 Dataflow 图使用，但其本质是 `USTRUCT`。以下是如何在 C++ 代码中声明和注册此类节点的基本结构。

### 头文件引入

```cpp
// 引入节点定义所需的头文件
#include "Dataflow/DataflowNode.h"
// 对于 GeometryCollection 相关类型
#include "GeometryCollection/ManagedArray.h"
#include "GeometryCollection/ManagedArrayCollection.h"
```

### 基本用法

以下示例展示了自定义一个简单 Dataflow 节点的框架，该框架与插件中节点的实现方式类似。
（来源：插件源码中各个节点的 `.h` 文件结构）

```cpp
// MyDataflowNode.h
#pragma once
#include "Dataflow/DataflowNode.h"
#include "GeometryCollection/ManagedArrayCollection.h"

/**
 * 一个简单的示例 Dataflow 节点，用于处理 GeometryCollection。
 */
USTRUCT()
struct FMySimpleDataflowNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()

    // 定义节点在编辑器中的名称、分类和提示
    DATAFLOW_NODE_DEFINE_INTERNAL(FMySimpleDataflowNode, "MySimpleNode", "MyCategory", "A simple example node")

    // 输入/输出引脚：集合数据（可作为输入和输出/透传）
    UPROPERTY(Meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    // 一个可编辑的输入参数
    UPROPERTY(EditAnywhere, Category = "Settings")
    float Strength = 1.0f;

    // 构造函数：注册输入和输出连接
    FMySimpleDataflowNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterInputConnection(&Strength);
        RegisterOutputConnection(&Collection, &Collection); // 通常输出修改后的同一集合
    }

    // 核心评估函数，在节点被执行时调用
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
    {
        // 获取输入数据
        const FManagedArrayCollection& InCollection = GetValue(Context, &Collection);
        const float InStrength = GetValue(Context, &Strength);

        // 在此进行实际的数据处理...
        // 例如，遍历 InCollection 的顶点数组并修改它们...
        // FManagedArrayCollection ModifiedCollection = InCollection;
        // ...

        // 设置输出
        SetValue(Context, &Collection, InCollection /* 或 ModifiedCollection */);
    }
};
```

## Demo 示例

以下是一个最小可编译的自定义 Dataflow 节点示例，该节点将输入的 `GeometryCollection` 中所有顶点的颜色设置为纯红色。

### MyRedColorNode.h
```cpp
// MyRedColorNode.h
#pragma once
#include "Dataflow/DataflowNode.h"
#include "GeometryCollection/ManagedArrayCollection.h"

/**
 * 将集合所有顶点颜色设置为红色的简单节点。
 */
USTRUCT()
struct FMyRedColorNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyRedColorNode, "SetAllVerticesRed", "MyUtilities", "Sets all vertex colors to red")

    UPROPERTY(Meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    FMyRedColorNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterOutputConnection(&Collection, &Collection);
    }

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

### MyRedColorNode.cpp
```cpp
// MyRedColorNode.cpp
#include "MyRedColorNode.h"
#include "GeometryCollection/ManagedArray.h"

void FMyRedColorNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    FManagedArrayCollection& CollectionRef = GetValue(Context, &Collection);

    // 尝试获取或创建“Color”属性数组
    TManagedArray<FLinearColor>* ColorArray = CollectionRef.FindAttributeTyped<FLinearColor>(FName("Color"), FGeometryCollection::VerticesGroup);
    if (!ColorArray)
    {
        // 如果不存在，则创建（这里简化处理，实际应考虑数组大小）
        CollectionRef.AddAttribute<FLinearColor>(FName("Color"), FGeometryCollection::VerticesGroup);
        ColorArray = CollectionRef.FindAttributeTyped<FLinearColor>(FName("Color"), FGeometryCollection::VerticesGroup);
        if (!ColorArray) return; // 创建失败
    }

    // 将所有顶点颜色设置为红色
    const int32 NumVertices = ColorArray->Num();
    for (int32 i = 0; i < NumVertices; ++i)
    {
        (*ColorArray)[i] = FLinearColor::Red;
    }

    // 输出修改后的集合
    SetValue(Context, &Collection, CollectionRef);
}
```

## 模块依赖

根据 `GeometryCollectionDepNodes` 模块的 Build.cs 以及此类 Dataflow 节点的典型依赖，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GeometryCollectionCore` | 提供 `GeometryCollection`、`ManagedArrayCollection` 等核心数据结构。 |
| `DataflowCore` | 提供 `FDataflowNode`、`FContext` 等数据流框架基础类。 |
| `Chaos` | 可能依赖于 Chaos 物理系统的基础数学和几何类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复了面向 UE 5.8 的本地化编译警告。 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | 对 Dataflow 节点进行更新（具体信息不完整）。 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 回退了之前编号为 53945814 的提交。 |
| 2026-05-14 | `88fb5004` | Dataflow: | 对 Dataflow 节点进行更新（具体信息不完整）。 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | 新增一个节点，用于在几何集合上创建外部碰撞体。 |

### 维护评价

**综合评价：维护中但核心功能已废弃**

-   **年龄**：创建于 2018 年，已有约 7 年历史。
-   **活跃度**：最近仍有提交，主要集中在修复兼容性警告和添加新节点。然而，从源码看，该模块下的主要节点（如 `TransferVertexScalarAttribute`）已被标记为 `Deprecated`。
-   **状态**：这是一个**实验性**插件（`IsBetaVersion=true`，且 `EnabledByDefault=false`）。其核心功能（几何集合间的属性传输）在 UE 5.5+ 版本中很可能已被整合到主 `GeometryCollection` 模块或替代方案中。
-   **推荐**：**不推荐新项目直接使用此模块**。对于新项目，应查阅最新的 Chaos 破坏系统文档，寻找官方推荐的、非废弃的几何集合操作方法。仅当维护遗留的、基于旧版 Chaos 数据流架构的项目时，才可能需要参考或直接使用此模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [官方文档]() (空)
- [测试用例]() (此插件目录下无独立测试文件，测试可能位于主 Chaos/GeometryCollection 模块内)