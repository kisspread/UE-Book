# Editor DataflowGraph

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 数据流图 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DataflowEditor` (Editor), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-04-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow) | |

## 用途

Dataflow 是 UE5 中一套**可视化的节点图数据处理框架**，提供基于节点连接的数据流编辑器。它解决的核心问题是：让开发者和美术在编辑器中通过拖拽节点、连接数据线的方式，以程序化的方式生成、变换、编辑几何数据，而无需编写代码。

该插件从 5.8 版本起从 Experimental 迁移为正式功能，说明 Epic 认为其 API 已趋于稳定。Dataflow 主要服务于以下高层系统：

- **GeometryCollection（Chaos 破碎系统）**：程序化生成、编辑破碎碎片的几何数据、蒙皮权重、选择集等
- **程序化网格生成**：在节点图中生成基础几何体（球、盒、圆柱等）并进行变换
- **属性传输**：在不同网格之间传输蒙皮权重、变形目标、多边形组等属性
- **采样器系统**：提供一套可组合的采样器，用于程序化生成标量/向量场（噪声、渐变、网格距离等），可驱动顶点属性或网格变形

简而言之，Dataflow 是 UE5 面向**程序化几何内容创作**的节点化工具平台。

## 使用场景

- 你在制作 Chaos 破碎特效，需要程序化编辑 GeometryCollection 的顶点属性 → 用 Dataflow 的 Collection 节点
- 你需要为破碎碎片程序化分配蒙皮权重 → 用 `EditSkinWeights` 节点在节点图中可视化编辑
- 你要生成基础网格（球体、盒子、楼梯等）并进行程序化变形 → 用 Generators|Mesh 类节点
- 你需要在两个网格之间迁移蒙皮权重/变形目标 → 用 `TransferMeshAttributes` 节点
- 你要基于噪声/渐变程序化生成顶点权重图 → 组合使用 Sampler 节点（Perlin、fBm、梯度等）+ `SamplerToAttribute` 节点
- 你需要交互式选择顶点/面并存为选择集 → 用 `DataflowSelectionToolNode`

## 蓝图用法

> 注意：Dataflow 主要是编辑器内节点图系统，大部分节点通过可视化节点图交互，不通过蓝图调用。以下列出的主要是 C++ 侧可编程的 API。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeSphereMesh` | 生成球体网格 | `FMakeSphereMeshDataflowNode_v2` |
| `MakeBoxMesh` | 生成盒子网格 | `FMakeBoxMeshDataflowNode_v2` |
| `MakeCapsuleMesh` | 生成胶囊体网格 | `FMakeCapsuleMeshDataflowNode_v2` |
| `MakeCylinderMesh` | 生成圆柱体网格 | `FMakeCylinderMeshDataflowNode_v2` |
| `MakeTorusMesh` | 生成圆环网格 | `FMakeTorusMeshDataflowNode_v2` |
| `MakeStairMesh` | 生成楼梯网格（直线/悬浮/弧形/螺旋） | `FMakeStairMeshDataflowNode_v2` |
| `MakeDiscMesh` | 生成圆盘网格 | `FMakeDiscMeshDataflowNode_v2` |
| `MakeRectangleMesh` | 生成矩形网格 | `FMakeRectangleMeshDataflowNode_v2` |
| `FilterPointsByAttribute` | 按属性值过滤点集 | `FFilterPointsByAttributeDataflowNode` |
| `EditSkinWeights` | 编辑网格蒙皮权重 | `FDataflowCollectionEditSkinWeightsNode` |
| `PaintWeightMap` | 绘制权重图到集合 | `FDataflowCollectionAddScalarVertexPropertyNode` |
| `TransferMeshAttributes` | 在网格间传输属性 | `FTransferMeshAttributesDataflowNode` |
| `SkeletalMesh` | 获取骨骼网格资产 | `FGetSkeletalMeshDataflowNode` |
| `Skeleton` | 获取骨架资产 | `FGetSkeletonDataflowNode` |
| `StaticMesh` | 获取静态网格资产 | `FGetStaticMeshDataflowNode_v2` |
| `SelectionSet` | 定义选择集 | `FSelectionSetDataflowNode` |
| `MakeSelectionSet` | 将选择集写入集合 | `FMakeSelectionSetDataflowNode` |
| `GetSelectionSet` | 从集合读取选择集 | `FGetSelectionSetDataflowNode` |
| `DataflowSelectionToolNode` | 交互式顶点/面选择工具 | `FDataflowSelectionToolNode` |
| `DisplaceDataflowMesh` | 用采样器位移网格顶点 | `FDisplaceDataflowMeshDataflowNode` |
| `TextureToAttribute` | 从纹理传输数据到顶点属性 | `FDataflowTextureToAttributeNode` |
| `SamplerToAttribute` | 用采样器设置顶点属性 | `FDataflowSamplerToAttributeNode` |
| `SamplerToImage` | 将采样器输出为 2D 图像 | `FDataflowSamplerToImageNode` |

### 采样器节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Uniform Float/Vector Sampler` | 恒定值采样 | `FDataflowUniformFloatSamplerNode` |
| `Linear Gradient Sampler` | 线性渐变采样 | `FDataflowLinearGradientFloatSamplerNode` |
| `Linear Gradient From Box Sampler` | 包围盒轴向渐变采样 | `FDataflowLinearGradientFromBoxFloatSamplerNode` |
| `Radial Gradient Sampler` | 径向渐变采样 | `FDataflowRadialGradientFloatSamplerNode` |
| `Perlin Noise Float/Vector Sampler` | Perlin 噪声采样 | `FDataflowPerlinNoiseFloatSamplerNode` |
| `fBm Float/Vector Sampler` | 分形布朗运动噪声采样 | `FDataflowfBmFloatSamplerNode` |
| `Turbulence Float Sampler` | 湍流噪声采样 | `FDataflowTurbulenceFloatSamplerNode` |
| `Random Float/Vector Sampler` | 随机值采样 | `FDataflowRandomFloatSamplerNode` |
| `Mesh Float/Vector Sampler` | 基于网格的采样（距离、法线、UV等） | `FDataflowMeshFloatSamplerNode` |
| `ElectricField Vector Sampler` | 电场模拟向量采样 | `FDataflowElectricFieldVectorSamplerNode` |
| `SmoothStep Float/Vector Sampler` | 平滑阶梯采样 | `FDataflowSmoothStepFloatSamplerNode` |
| `Step Float/Vector Sampler` | 硬阶梯采样 | `FDataflowStepFloatSamplerNode` |
| `Modulo Float/Vector Sampler` | 取模采样 | `FDataflowModuloFloatSamplerNode` |
| `Lerp Sampler` | 线性插值混合采样 | `FDataflowLerpSamplerNode` |
| `SLerp Sampler` | 球面插值混合采样 | `FDataflowSLerpSamplerNode` |
| `Remap Float Sampler` | 值域重映射采样 | `FDataflowRemapFloatSamplerNode` |
| `ColorRamp Sampler` | 颜色渐变映射采样 | `FDataflowColorRampSamplerNode` |
| `Tiling Sampler` | 平铺采样 | `FDataflowTilingSamplerNode` |
| `Sign Sampler` | 符号函数采样 | `FDataflowSignSamplerNode` |
| `Abs Sampler` | 绝对值采样 | `FDataflowAbsSamplerNode` |
| `SamplerRange` | 计算采样器的值域范围 | `FSamplerRangeDataflowNode` |

### 使用示例（节点图描述）

**生成球体并用 Perlin 噪声位移表面**：
1. 创建 `MakeSphereMesh` 节点 → 输出 Mesh
2. 创建 `Perlin Noise Float Sampler` 节点 → 输出 FloatSampler
3. 创建 `DisplaceDataflowMesh` 节点
4. 将球体的 Mesh 输出连接到 Displace 的 Mesh 输入
5. 将 Perlin 的 FloatSampler 输出连接到 Displace 的 Sampler 输入
6. Displace 的 Mesh 输出即为带噪声位移的球体

**为集合顶点绘制程序化权重图**：
1. 创建 `Linear Gradient Sampler` 节点，配置起止点和值
2. 创建 `SamplerToAttribute` 节点
3. 将 Gradient 的 Sampler 输出连接到 SamplerToAttribute 的 Sampler 输入
4. 配置属性名和顶点组
5. 连接集合的 Collection 输入/输出

## C++ 用法

### 头文件引入

```cpp
// 网格生成节点
#include "Dataflow/DataflowMeshMakeNodes.h"

// 点集操作节点
#include "Dataflow/DataflowPointsNodes.h"

// 属性传输节点
#include "Dataflow/Transfer/DataflowMeshAttributesTransferNodes.h"
#include "Dataflow/Transfer/TransferAttributes.h"

// 骨骼网格节点
#include "Dataflow/DataflowSkeletalMeshNodes.h"

// 蒙皮权重编辑
#include "Dataflow/DataflowCollectionEditSkinWeightsNode.h"

// 权重图绘制
#include "Dataflow/DataflowCollectionAddScalarVertexPropertyNode.h"

// 采样器类型与节点
#include "Dataflow/SamplerNodes/DataflowSamplerTypes.h"
#include "Private/Dataflow/SamplerNodes/DataflowGradientSamplerNode.h"

// 选择集节点
#include "Dataflow/DataflowSelectionNodes.h"

// 工具节点基类
#include "Dataflow/DataflowToolNode.h"

// 静态网格节点
#include "Dataflow/DataflowStaticMeshNodes.h"

// 骨骼编辑节点
#include "Dataflow/DataflowCollectionEditSkeletonBonesNode.h"
```

### 基本用法

Dataflow 节点以 `USTRUCT` 形式定义，每个节点继承 `FDataflowNode`（或其子类如 `FDataflowPrimitiveNode`、`FDataflowToolNode`）。

**定义一个简单的自定义节点**：

```cpp
// 来源: 模式参考 DataflowMeshMakeNodes.h
USTRUCT()
struct FMyCustomDataflowNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomDataflowNode, "MyNode", "MyCategory|SubCategory", "")

    // 输入：通过 DataflowInput 元数据标记
    UPROPERTY(EditAnywhere, Category = "Input", meta = (DataflowInput))
    float Value = 1.0f;

    // 输出：通过 DataflowOutput 元数据标记
    UPROPERTY(meta = (DataflowOutput))
    float Result = 0.0f;

    FMyCustomDataflowNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Value);
        RegisterOutputConnection(&Result);
    }

    // 核心求值函数
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
    {
        // 从 Context 读取输入值
        const float InValue = Context.GetValue(DataflowInput, Value);
        // 计算并设置输出
        Context.SetValue(DataflowOutput, Result, InValue * 2.0f);
    }
};
```

**使用传递（Passthrough）属性**——让数据直接穿过节点不修改：

```cpp
// 来源: DataflowPointsNodes.h - FFilterPointsByAttributeDataflowNode
UPROPERTY(EditAnywhere, Category = "Filter", meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Attribute"))
FString Attribute = FString("Dummy");
```

`DataflowPassthrough` 使得连接到输入的数据自动出现在输出上，无需在 Evaluate 中手动传递。

### 进阶用法

**使用属性传输代理系统**（TransferAttributes）：

```cpp
// 来源: DataflowMeshAttributesTransferNodes.h + TransferAttributes.h
#include "Dataflow/Transfer/TransferAttributes.h"

// 创建传输操作器
UE::Geometry::FTransferAttributes TransferOp(SourceMesh, &SourceBVH);

// 添加蒙皮权重代理
TransferOp.AddVertexProxy<UE::Geometry::FSkinWeightsProxy>(
    SourceSkinAttribute,
    FName("DestinationSkinWeights"),
    FSkinWeightsProxy::FSkinWeightsProxyOptions()
);

// 添加变形目标代理
TransferOp.AddVertexProxy<UE::Geometry::FMorphTargetProxy>(
    SourceMorphAttribute,
    FName("DestinationMorphTarget")
);

// 添加多边形组代理
TransferOp.AddTriangleProxy<UE::Geometry::FPolygroupProxy>(
    SourcePolygroupAttribute,
    FName("DestinationPolygroup")
);

// 执行传输
TransferOp.TransferAttributesToMesh(TargetDynamicMesh);
```

**跨骨架蒙皮权重传输**（不同骨骼索引映射）：

```cpp
// 来源: TransferAttributes.h - FSkinWeightsProxy
UE::Geometry::FSkinWeightsProxy::FSkinWeightsProxyOptions Options;
Options.SourceIndexToBone = SourceBoneNames;  // 源骨骼索引→名称映射
Options.TargetBoneToIndex = TargetBoneMap;    // 目标骨骼名称→索引映射
Options.bNormalizeToOne = true;

TransferOp.AddVertexProxy<UE::Geometry::FSkinWeightsProxy>(
    SourceSkinAttribute, FName("SkinWeights"), Options);
```

**创建自定义采样器**：

```cpp
// 来源: DataflowSamplerTypes.h
// 继承 FDataflowFloatSamplerBase 实现自定义采样逻辑
USTRUCT()
struct FMyCustomFloatSampler : public FDataflowFloatSamplerBase
{
    GENERATED_BODY();

    virtual ~FMyCustomFloatSampler() override = default;

    // 批量采样：为一组 3D 位置返回 float 值
    virtual void Sample(TArrayView<const FVector3f> Positions, TArrayView<float> OutValues) const override
    {
        for (int32 i = 0; i < Positions.Num(); ++i)
        {
            OutValues[i] = FVector3f::DotProduct(Positions[i], FVector3f::UpVector);
        }
    }

    virtual FBox GetRenderBounds() const override
    {
        return FBox(FVector(-100.0), FVector(100.0));
    }
};
```

**使用快照系统进行撤销/重做**：

```cpp
// 来源: DataflowToolNode.h
// FDataflowToolNode 子类自动支持快照
// 添加快照
FDataflowToolNodeSnapshot& Snapshot = AddSnapshot();

// 获取当前活跃快照
const FDataflowToolNodeSnapshot* Active = GetActiveSnapshot();

// 获取所有快照列表
TConstArrayView<FDataflowToolNodeSnapshot> AllSnapshots = GetSnapshots();
```

## Demo 示例

### 自定义 Dataflow 节点：网格顶点统计

```cpp
// MyDataflowNodes.h
#pragma once

#include "Dataflow/DataflowNode.h"
#include "GeometryCollection/ManagedArrayCollection.h"

USTRUCT()
struct FCountVerticesDataflowNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FCountVerticesDataflowNode, "CountVertices", "Collection|Utility", "统计集合中的顶点数量")

public:
    FCountVerticesDataflowNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

    /** 输入集合 */
    UPROPERTY(Meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection", DataflowIntrinsic))
    FManagedArrayCollection Collection;

    /** 选择集（可选） */
    UPROPERTY(meta = (DataflowInput))
    FDataflowVertexSelection Selection;

    /** 总顶点数 */
    UPROPERTY(meta = (DataflowOutput))
    int32 TotalVertices = 0;

    /** 选中顶点数 */
    UPROPERTY(meta = (DataflowOutput))
    int32 SelectedVertices = 0;

    /** 选中比例 */
    UPROPERTY(meta = (DataflowOutput))
    float SelectionRatio = 0.0f;

private:
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

```cpp
// MyDataflowNodes.cpp
#include "MyDataflowNodes.h"
#include "Dataflow/DataflowNodeColorsRegistry.h"

FCountVerticesDataflowNode::FCountVerticesDataflowNode(
    const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FDataflowNode(InParam, InGuid)
{
    RegisterInputConnection(&Collection);
    RegisterOutputConnection(&Collection);
    RegisterInputConnection(&Selection);
    RegisterOutputConnection(&TotalVertices);
    RegisterOutputConnection(&SelectedVertices);
    RegisterOutputConnection(&SelectionRatio);
}

void FCountVerticesDataflowNode::Evaluate(
    UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 获取集合数据
    const FManagedArrayCollection& InCollection = 
        Context.GetValue<FManagedArrayCollection>(this, Collection);
    
    // 获取顶点数量（假设 Vertices 组）
    const int32 NumVerts = InCollection.NumElements(FGeometryCollection::VerticesGroup);
    Context.SetValue(Out, TotalVertices, NumVerts);

    // 计算选中数量
    if (Selection.Num() > 0)
    {
        int32 Count = 0;
        for (int32 i = 0; i < Selection.Num(); ++i)
        {
            if (Selection[i])
            {
                ++Count;
            }
        }
        Context.SetValue(Out, SelectedVertices, Count);
        Context.SetValue(Out, SelectionRatio, 
            NumVerts > 0 ? static_cast<float>(Count) / NumVerts : 0.0f);
    }
    else
    {
        Context.SetValue(Out, SelectedVertices, NumVerts);
        Context.SetValue(Out, SelectionRatio, 1.0f);
    }
}
```

## 模块依赖

基于源码分析，Dataflow 插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `GeometryCollectionCore` | ManagedArrayCollection、GeometryCollection 数据结构 |
| `GeometryCollectionEngine` | GeometryCollection 运行时支持 |
| `GeometryFramework` | UDynamicMesh 动态网格资产 |
| `GeometryScriptingCore` | 几何脚本工具函数 |
| `ModelingComponents` | 网格建模组件 |
| `AnimationCore` | FBoneWeights 骨骼权重类型 |
| `MeshConversion` | FDynamicMeshToMeshDescription 网格格式转换 |
| `StaticMeshDescription` | 静态网格描述 |
| `SkeletalMeshDescription` | 骨骼网格描述 |
| `DataflowCore` | Dataflow 节点图核心框架 |
| `DataflowEngine` | Dataflow 运行时引擎 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee85ff45` | Dataflow : remove sections from rendering settings since they are half broken | 移除渲染设置中损坏的部分配置 |
| 2026-05-25 | `25af8e6f` | Dataflow : add extra checks on the edit skin weight tool to inform user about why the node may not work | 为蒙皮权重编辑工具添加额外检查，提示节点不可用原因 |
| 2026-05-22 | `9a062c29` | [Dataflow Editor] Fixed container mutation during tick evaluation. | 修复编辑器中 Tick 求值期间容器突变的问题 |
| 2026-05-22 | `8dc486bc` | Dataflow Editor : Fix crash happening when using a tool with another Dataflow editor opened | 修复多个 Dataflow 编辑器同时打开时使用工具导致的崩溃 |
| 2026-05-22 | `8cfadbd3` | Dataflow Editor : fix Undo / redo issues with comment nodes | 修复注释节点的撤销/重做问题 |

### 维护评价

- **活跃维护中**：插件刚从 Experimental 迁移为正式功能（2026-04-17），最近一周内仍有密集的 bug 修复提交
- **API 趋于稳定**：大量节点已从 v1 版本（使用 `UDynamicMesh`）升级到 v2（使用 `UDataflowMesh`），v1 节点标记为 `Deprecated = "5.8"`
- **快速迭代期**：作为刚发布的正式功能，处于密集修复和打磨阶段，接口可能仍有小幅调整
- **部分 API 标记为实验性**：`FTransferMeshAttributesDataflowNode`、`FDataflowCollectionEditSkinWeightsNode`、`FDataflowCollectionEditSkeletonBonesNode` 仍标记 `Experimental`
- **推荐使用**：适合在 5.8 及以上版本中使用，尤其适合 GeometryCollection 和程序化几何内容创作工作流。但需注意实验性 API 的接口可能变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow)
- [官方文档]()（暂无）