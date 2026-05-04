# Groom

> Rendering and simulation of grooms（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Groom资产、数据流图表等） |
| 模块 | `HairStrandsCore` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsSolver` (Runtime), `HairStrandsDeformer` (Runtime), `HairCardGeneratorFramework` (Runtime), `HairStrandsDataflow` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands（Groom）插件是 Unreal Engine 中用于处理**Groom资产**（如毛发、羽毛、皮毛等）的核心系统。它不仅仅是一个渲染组件，而是一个完整的解决方案，涵盖了从资产导入、编辑、物理模拟到最终渲染的整个管线。

该插件的核心功能包括：
1.  **Groom资产管理**：定义和存储毛发/曲线的几何数据（Strands用于渲染，Guides用于模拟）、LOD层级、蒙皮权重等。
2.  **物理模拟**：通过 `HairStrandsSolver` 模块，为Guides曲线提供基于物理的动态模拟，实现逼真的毛发飘动、碰撞和交互效果。
3.  **渲染**：`HairStrandsRuntime` 模块负责将Strands数据转换为GPU可高效渲染的格式（如发片、发束），并集成到UE的渲染管线中。
4.  **程序化处理**：`HairStrandsDataflow` 模块提供了一套基于节点的数据流（Dataflow）工具，允许用户在编辑器中以非破坏性的方式程序化生成、修改和优化Groom数据。
5.  **变形与蒙皮**：`HairStrandsDeformer` 模块处理毛发随角色骨骼动画的变形，支持线性蒙皮和样条蒙皮。

简单来说，这个插件解决了在游戏和实时应用中创建、驱动和渲染高质量、高性能毛发系统的问题。

## 使用场景

-   **游戏角色毛发**：为写实风格或风格化的角色创建头发、胡须、眉毛等，并需要随骨骼动画自然摆动。
-   **动物毛发/皮毛**：为动物角色创建全身皮毛，并需要物理模拟以增强真实感。
-   **羽毛与装饰**：为鸟类角色或服装装饰创建羽毛，并需要动态效果。
-   **开放世界优化**：利用Groom的LOD系统，在远距离使用简化的卡片网格（Hair Cards）或发片（Strands）进行渲染，以优化性能。
-   **程序化毛发工作流**：使用数据流节点从基础网格或其它Groom资产程序化生成新的毛发造型，或批量处理大量Groom资产。

## 蓝图用法

HairStrands插件主要通过**数据流（Dataflow）编辑器**提供可视化节点操作，而非传统的蓝图函数节点。这些节点用于在编辑器中构建Groom资产的处理图。

### 核心节点（数据流）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetGroomAsset` | 从资产引用中获取Groom数据，并输出为数据流集合（Collection）。 | `FGetGroomAssetDataflowNode_v2` |
| `GroomAssetToCollection` | 将Groom资产转换为数据流集合，可选择Strands或Guides类型。 | `FGroomAssetToCollectionDataflowNode` |
| `GroomAssetTerminal` | 数据流图的终端节点，将处理后的集合数据写回Groom资产。 | `FGroomAssetTerminalDataflowNode_v2` |
| `SmoothCurvePoints` | 对曲线点进行平滑处理，使模拟更稳定。 | `FSmoothCurvePointsDataflowNode` |
| `GenerateCurveGeometry` | 从源曲线集合生成新的曲线几何体。 | `FGenerateCurveGeometryDataflowNode` |
| `BuildCurveLODs` | 为曲线构建LOD层级。 | `FBuildCurveLODsDataflowNode` |
| `ResampleCurvePoints` | 对曲线进行重采样，统一控制点数量。 | `FResampleCurvePointsDataflowNode` |
| `AttachCurveRoots` | 将曲线根部设置为运动学权重1.0，使其固定。 | `FAttachCurveRootsDataflowNode` |
| `TransferLinearSkinWeights` | 从骨骼网格体将线性蒙皮权重传输到曲线。 | `FTransferGeometrySkinWeightsDataflowNode` |

### 使用示例（数据流图描述）

1.  **创建基础数据流图**：在Groom资产编辑器中，打开“Dataflow”选项卡。
2.  **添加输入节点**：拖入一个 `GetGroomAsset` 节点，并指定一个现有的Groom资产作为输入。
3.  **处理数据**：连接一个 `SmoothCurvePoints` 节点来平滑Guides，或连接一个 `BuildCurveLODs` 节点来生成LOD。
4.  **输出结果**：将处理链的末端连接到 `GroomAssetTerminal` 节点。在终端节点的属性中，可以添加额外的属性键（Attribute Keys）来保存自定义数据。
5.  **应用**：点击“Apply”按钮，数据流图将被评估，结果将写回Groom资产。

## C++ 用法

### 头文件引入

```cpp
#include "HairStrandsDataflowModule.h"
#include "GetGroomAssetNode.h"
#include "SmoothGuidesCurvesNode.h"
// 根据需要引入其他节点头文件
```

### 基本用法

以下示例展示了如何在C++中创建一个简单的数据流节点。数据流节点是USTRUCT，继承自`FDataflowNode`。

```cpp
// MyCustomGroomNode.h
#pragma once

#include "CoreMinimal.h"
#include "Dataflow/DataflowCore.h"
#include "MyCustomGroomNode.generated.h"

USTRUCT(meta = (Experimental, DataflowGroom))
struct FMyCustomGroomNode : public FDataflowNode
{
    GENERATED_BODY()

    // 定义节点名称、分类和描述
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomGroomNode, "MyCustomGroomOp", "Groom", "A custom operation on groom data")

public:
    FMyCustomGroomNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        // 注册输入和输出连接
        RegisterInputConnection(&InputCollection);
        RegisterOutputConnection(&OutputCollection, &InputCollection); // 输出直通输入
    }

private:
    // 节点评估函数，核心逻辑在此
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
    {
        // 从输入获取数据
        const FManagedArrayCollection& InData = Context.GetValue(InputCollection);
        // ... 对InData进行处理 ...
        // 将结果设置到输出
        Context.SetValue(OutputCollection, ProcessedData);
    }

public:
    // 输入属性，标记为DataflowInput
    UPROPERTY(meta = (DataflowInput, DisplayName = "Input Groom"))
    FManagedArrayCollection InputCollection;

    // 输出属性，标记为DataflowOutput，并设置为直通输入
    UPROPERTY(meta = (DataflowOutput, DisplayName = "Output Groom", DataflowPassthrough = "InputCollection"))
    FManagedArrayCollection OutputCollection;

    // 用户可编辑的参数
    UPROPERTY(EditAnywhere, Category = "Settings")
    float SomeParameter = 1.0f;
};
```

### 进阶用法

结合多个节点构建处理链。以下代码片段展示了如何在代码中实例化节点并连接它们（通常在编辑器工具或自动化流程中）。

```cpp
// 假设我们有一个Dataflow资产 (UDataflow* DataflowAsset)
// 1. 创建节点实例
FGetGroomAssetDataflowNode_v2* GetAssetNode = DataflowAsset->AddNode<FGetGroomAssetDataflowNode_v2>();
FSmoothCurvePointsDataflowNode* SmoothNode = DataflowAsset->AddNode<FSmoothCurvePointsDataflowNode>();
FGroomAssetTerminalDataflowNode_v2* TerminalNode = DataflowAsset->AddNode<FGroomAssetTerminalDataflowNode_v2>();

// 2. 配置节点参数
GetAssetNode->GroomAsset = MyGroomAsset;
SmoothNode->SmoothingFactor = 0.5f;

// 3. 连接节点 (通过引脚名称)
DataflowAsset->Connect(GetAssetNode->GetOutputConnection(TEXT("GroomAsset")), 
                       SmoothNode->GetInputConnection(TEXT("Collection")));
DataflowAsset->Connect(SmoothNode->GetOutputConnection(TEXT("Collection")),
                       TerminalNode->GetInputConnection(TEXT("StrandsCollection")));

// 4. 评估整个图
DataflowAsset->Evaluate();
```

## Demo 示例

一个最小的自定义数据流节点，用于将Groom集合中所有曲线的点数加倍（通过简单的线性插值）。

**DoubleCurvePointsNode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Dataflow/DataflowCore.h"
#include "DoubleCurvePointsNode.generated.h"

USTRUCT(meta = (Experimental, DataflowGroom))
struct FDoubleCurvePointsNode : public FDataflowNode
{
    GENERATED_BODY()

    DATAFLOW_NODE_DEFINE_INTERNAL(FDoubleCurvePointsNode, "DoubleCurvePoints", "Groom", "Doubles the number of points on each curve via linear interpolation")

public:
    FDoubleCurvePointsNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

private:
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;

public:
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DisplayName = "Collection", DataflowPassthrough = "Collection", DataflowRenderGroups = "Surface"))
    FManagedArrayCollection Collection;
};
```

**DoubleCurvePointsNode.cpp**
```cpp
#include "DoubleCurvePointsNode.h"
#include "GroomCollectionFacades.h"

FDoubleCurvePointsNode::FDoubleCurvePointsNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FDataflowNode(InParam, InGuid)
{
    RegisterInputConnection(&Collection);
    RegisterOutputConnection(&Collection, &Collection);
}

void FDoubleCurvePointsNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 获取输入的集合
    FManagedArrayCollection& OutCollection = Context.GetMutableValue(Collection);
    
    // 使用Groom Facade访问曲线数据
    UE::Groom::FCurvesFacade CurvesFacade(OutCollection);
    if (!CurvesFacade.IsValid())
    {
        return;
    }

    // 遍历每条曲线
    const int32 NumCurves = CurvesFacade.GetNumCurves();
    for (int32 CurveIndex = 0; CurveIndex < NumCurves; ++CurveIndex)
    {
        const int32 OldNumPoints = CurvesFacade.GetNumPoints(CurveIndex);
        const int32 NewNumPoints = OldNumPoints * 2 - 1; // 例如，3个点 -> 5个点

        // 此处省略了实际的插值和数组重分配逻辑
        // 核心是：读取旧点位置，计算新点位置，更新集合中的点数据
        // ...
    }
    
    // 输出修改后的集合（由于设置了Passthrough，通常不需要显式设置，但确保逻辑正确）
    // Context.SetValue(Collection, OutCollection);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | 提供数据流图的核心框架、节点、连接和评估系统。 |
| `GroomAsset` | 定义Groom资产（`UGroomAsset`）的核心数据结构。 |
| `GeometryCollection` | 提供`FManagedArrayCollection`等底层几何数据容器，是Groom数据流的基础。 |
| `Chaos` | 物理模拟框架，`HairStrandsSolver`模块依赖它进行毛发物理计算。 |
| `MeshDescription` | 用于处理网格体描述，可能在生成发片网格（Hair Cards）时使用。 |

## 维护状态

### 近期更新

```
- cb28d8f41d3d Bending model for groom + geometric collision+ guides solver
- 71e223a60f6c Dataflow: - Tidied up the private deprecations in FDataflowNode. - Fixed typo on OutputArrayProperties. - Prepared the override color properties for a move to the private section.
- 4ca6edca226e Optional simulation visualisation for strands / Fix bad indexing for custom attributes / update simulation view when asset is changing / Relative offsets for guides LODs
```

**解读**：
1.  `cb28d8f41d3d`：为Groom添加了弯曲模型、几何碰撞和新的Guides求解器，这是核心物理模拟功能的重大更新。
2.  `71e223a60f6c`：对数据流节点框架进行了内部清理和修复，属于代码质量改进。
3.  `4ca6edca226e`：增加了模拟可视化选项，修复了自定义属性索引错误，并改进了LOD的相对偏移，属于功能增强和Bug修复。

### 维护评价

**活跃维护**。该插件创建于约6年前，属于UE中较成熟的毛发系统。从近期提交记录看，Epic仍在积极开发和优化其核心功能（如物理模拟、数据流工具链）。最近的提交集中在提升模拟真实感、改善编辑器工作流和修复问题上，表明它仍然是UE毛发技术的重点发展方向。虽然默认未启用（`EnabledByDefault: false`），但这通常是因为它需要特定的资产和设置，并非废弃标志。**推荐使用**，特别是对于需要高质量、可定制毛发系统的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands)
- [官方文档]()（暂无）
- [测试用例]()（暂未提供具体路径）