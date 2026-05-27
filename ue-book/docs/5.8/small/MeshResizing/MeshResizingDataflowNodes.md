# Mesh Resizing

> Mesh Resizing（网格缩放）

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

MeshResizing 插件为 UE5 的 Dataflow 系统提供了一组实验性的节点，用于实现**形状保持的网格缩放与变形**。它解决的核心问题是：当一个网格（通常是骨骼网格体）的目标形状（Target Shape）与原始形状（Source Shape）不同时，如何在缩放或变形过程中保持其拓扑结构、UV 映射和纹理坐标的正确性。

插件通过以下方式实现这一目标：
1.  **网格转换与代理生成**：将骨骼网格体（Skeletal Mesh）转换为 Dataflow 可用的动态网格（Dynamic Mesh）或数据流网格（Dataflow Mesh），并为其生成可变形的“代理”网格。
2.  **RBF 插值**：使用径向基函数（Radial Basis Function）在源形状和目标形状之间进行插值，从而实现平滑、形状保持的变形。
3.  **网格包裹 (Mesh Wrap)**：通过定义地标点（Landmarks），将一个网格的拓扑“包裹”到另一个网格的形状上，这是实现高质量变形的关键。
4.  **UV 与纹理处理**：提供节点来自动调整 UV 布局、对齐 UV，甚至基于新网格形状生成平铺纹理，确保纹理在新形状下依然正确映射。

简单来说，这个插件让你可以在 Dataflow 图表中，用节点化的方式，将角色网格体从一种体型（如瘦）平滑、保真地变形为另一种体型（如胖），同时自动处理好所有相关的 UV 和材质问题。

## 使用场景

-   **角色自定义系统**：制作一个支持多种体型（高矮胖瘦）的角色创建器，共享同一套基础拓扑和 UV 的网格资产，通过该插件实时变形。
-   **角色成长或老化**：模拟角色随时间推移的体型变化，如从成年到老年。
-   **资产批量缩放**：需要将一批同拓扑但不同比例的网格资产（例如不同尺寸的桌椅）的 UV 和纹理进行批量适配。
-   **高级变形管线**：构建复杂的 Dataflow 变形管线，例如先进行网格包裹，再进行局部约束变形，最后调整纹理。

## 蓝图用法

此插件主要提供 Dataflow 节点，这些节点可在 Dataflow 图表中使用，并通过 Dataflow 组件（如 Dataflow 节点组件）连接到 Actor 上。其核心功能并非直接暴露给传统的蓝图事件图表，而是通过 Dataflow 的节点化工作流实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SkeletalMeshToMesh` (v2) | 将骨骼网格体转换为数据流网格，保留导入的顶点信息用于映射。 | `FSkeletalMeshToMeshDataflowNode_v2` |
| `GenerateResizableProxy` | 基于源网格和目标网格，生成一对拓扑相同的代理网格，用于后续插值。 | `FGenerateResizableProxyDataflowNode` |
| `GenerateInterpolatedProxy` | 在源网格和目标网格之间进行混合，生成一个插值后的代理网格。 | `FGenerateInterpolatedProxyDataflowNode` |
| `MeshWrapLandmarks` | 定义用于网格包裹的地标点（顶点标识对）。通常配合编辑器中的地标选择工具使用。 | `FMeshWrapLandmarksNode` |
| `MeshWrap` | 执行网格包裹操作。将源拓扑网格的几何形状“包裹”到目标形状网格上，使用地标点进行引导。 | `FMeshWrapNode` |
| `GenerateRBFResizingWeights` | 对源网格进行采样，生成用于 RBF 插值的权重数据。 | `FGenerateRBFResizingWeightsNode` |
| `ApplyRBFResizing` | 应用预先计算的 RBF 权重数据，将一个网格变形为目标网格的形状。 | `FApplyRBFResizingNode` |
| `UVResizeController` | 分析网格的 UV 通道，确定哪些通道需要随网格变形进行调整。 | `FUVResizeControllerNode` |
| `AlignUVMesh` | 将一个网格的 UV 与另一个基准网格的 UV 进行对齐和缩放。 | `FAlignUVMeshNode` |
| `GrowTileRegion` | 在图像的有效区域（由 UV 网格定义）内查找并复制一个方块纹理瓦片。 | `FMeshResizingGrowTileRegionNode` |

### 使用示例（Dataflow 图表描述）

1.  **基础形状变形管线**:
    -   将 `SkeletalMeshToMesh` 节点连接到你的源角色骨骼网格体。
    -   将其输出的 `Mesh` 和 `MaterialArray` 连接到 `GenerateResizableProxy` 节点的 `SourceMesh` 和 `SourceMaterialArray` 输入。
    -   将你的目标形状网格（可以是另一个 `SkeletalMeshToMesh` 的输出或编辑好的动态网格）连接到 `TargetMesh` 输入。
    -   `GenerateResizableProxy` 将输出拓扑一致的 `SourceProxyMesh` 和 `TargetProxyMesh`。
    -   你可以将这两个代理网格连接到 `GenerateInterpolatedProxy`，通过 `BlendAlpha` (0-1) 来控制源形状和目标形状的混合比例，得到最终的变形网格。

2.  **使用网格包裹进行高级变形**:
    -   使用 `MeshWrapLandmarks` 节点（或通过编辑器工具在网格上选择）为源拓扑网格和目标形状网格定义匹配的地标点。
    -   将源拓扑网格、目标形状网格以及各自的地标点数组连接到 `MeshWrap` 节点。
    -   调整 `MaxNumOuterIterations`, `LaplacianStiffness` 等参数来优化包裹结果。`MeshWrap` 节点的 `WrappedMesh` 输出即为形状匹配目标网格但拓扑来自源网格的最终结果。

## C++ 用法

此插件的功能主要通过 Dataflow 节点在编辑器中以图形化方式使用，直接的 C++ 编程接口较少。开发者更可能继承或参考这些节点来创建自定义的变形逻辑。

### 头文件引入

```cpp
// 若要使用或引用其中的数据结构
#include "MeshResizing/MeshWrapNode.h" // FMeshWrapLandmark, FMeshWrapNode
#include "MeshResizing/RBFInterpolationNodes.h" // FMeshResizingRBFInterpolationData 等
```

### 基本用法

自定义 Dataflow 节点是此插件最核心的扩展方式。你可以继承 `FDataflowNode` 来创建自己的网格处理节点。

```cpp
// 示例：一个简单的自定义节点，用于对网格顶点进行缩放 (来自插件节点设计的简化)
USTRUCT(Meta = (MeshResizing, Experimental))
struct FMyScaleMeshNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyScaleMeshNode, "MyScaleMesh", "Custom|Mesh", "Scales mesh vertices")

    FMyScaleMeshNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        // 注册输入输出
        RegisterInputConnection(&Mesh);
        RegisterOutputConnection(&Mesh); // 输入和输出可以是同一个属性
    }

private:
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Mesh"))
    TObjectPtr<UDataflowMesh> Mesh;

    UPROPERTY(EditAnywhere, Category = "Scale", meta = (DataflowInput))
    FVector3d Scale = FVector3d(1.0);

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
    {
        // 获取输入网格（如果需要可修改副本）
        if (UDataflowMesh* InMesh = Context.GetValue(DataflowInput, &Mesh))
        {
            // 创建可编辑副本或在原网格上操作
            // ... 应用缩放变换到网格顶点 ...
            // 设置输出值
            Context.SetValue(DataflowOutput, &Mesh, InMesh);
        }
    }
};
```

### 进阶用法

结合多个节点构建复杂的变形效果。例如，在 C++ 层面，你可能需要编写一个函数来批量生成匹配的地标点，然后将其输入到 `FMeshWrapNode` 中进行处理。

## Demo 示例

以下是一个在 Dataflow 资产中可能使用的节点连接关系示例，展示了从骨骼网格体到最终变形结果的流程。请注意，这需要在 UE 编辑器中通过 Dataflow 图表界面实现。

```cpp
// 此示例描述了 Dataflow 节点图的连接逻辑，而非可直接编译的 C++ 代码。
// 假设我们有两个骨骼网格体：SourceSKM (瘦型) 和 TargetSKM (胖型)。
// 目标是生成一个介于两者之间的混合体，并确保其 UV 正确。

// 1. 转换源网格体
FDataflowNode& SourceConverter = DataflowGraph->AddNode(FSkeletalMeshToMeshDataflowNode_v2::StaticStruct());
SourceConverter.SetPropertyValue(TEXT("SkeletalMesh"), SourceSKM);

// 2. 转换目标网格体
FDataflowNode& TargetConverter = DataflowGraph->AddNode(FSkeletalMeshToMeshDataflowNode_v2::StaticStruct());
TargetConverter.SetPropertyValue(TEXT("SkeletalMesh"), TargetSKM);

// 3. 生成可变形代理（可选，用于平滑插值）
FDataflowNode& ProxyGenerator = DataflowGraph->AddNode(FGenerateResizableProxyDataflowNode::StaticStruct());
// 连接源转换器的输出到代理生成器的源输入
DataflowGraph->Connect(SourceConverter.GetOutput(TEXT("Mesh")), ProxyGenerator.GetInput(TEXT("SourceMesh")));
DataflowGraph->Connect(TargetConverter.GetOutput(TEXT("Mesh")), ProxyGenerator.GetInput(TEXT("TargetMesh")));

// 4. 进行插值混合
FDataflowNode& BlendingNode = DataflowGraph->AddNode(FGenerateInterpolatedProxyDataflowNode::StaticStruct());
DataflowGraph->Connect(SourceConverter.GetOutput(TEXT("Mesh")), BlendingNode.GetInput(TEXT("SourceMesh")));
DataflowGraph->Connect(TargetConverter.GetOutput(TEXT("Mesh")), BlendingNode.GetInput(TEXT("TargetMesh")));
BlendingNode.SetPropertyValue(TEXT("BlendAlpha"), 0.7f); // 70% 胖型

// 5. 对混合结果进行 UV 对齐
FDataflowNode& UVAligner = DataflowGraph->AddNode(FAlignUVMeshNode::StaticStruct());
DataflowGraph->Connect(BlendingNode.GetOutput(TEXT("ProxyMesh")), UVAligner.GetInput(TEXT("ResizingMesh")));
DataflowGraph->Connect(SourceConverter.GetOutput(TEXT("Mesh")), UVAligner.GetInput(TEXT("BaseMesh"))); // 以原始瘦型网格UV为基准
```

## 模块依赖

此插件的模块依赖主要围绕数据流、几何网格处理和渲染。使用者需要确保其项目模块包含了对核心模块的依赖。

| 模块 | 用途 |
|---|---|
| `DataflowCore`, `DataflowEngine` | Dataflow 框架的核心和运行时引擎，是使用所有节点的基础。 |
| `DynamicMesh`, `GeometryCore`, `MeshResizingCore` | 几何处理、动态网格操作和网格缩放核心算法。 |
| `DataflowNodes`, `MeshDescription` | 提供 Dataflow 节点基础结构和网格描述转换功能。 |
| `RenderCore`, `RHI` | 与渲染系统集成，用于节点的调试绘制和预览。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为单精度浮点数时产生的警告代码。 |
| 2026-05-12 | `a7802337` | Dataflow: | 数据流相关更新（具体信息未在摘录中显示）。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将到来的头文件清理之前，预先添加必要的头文件包含。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | 数据流：为绘图工具添加了套索选择支持，利用了网格中新添加的功能。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 数据流：更新了大量节点以使用新的渲染系统。 |

### 维护评价

MeshResizing 是一个**创建时间较新、处于活跃开发中的实验性插件**。

-   **创建时间**：2024年12月，至今约1年。
-   **近期更新**：最近一次提交在 2026 年 5 月，且在过去一年内有多次功能性更新（如节点渲染系统更新、工具增强），表明 Epic 工程师正在持续迭代。
-   **实验性**：插件明确标记为实验性 (`IsExperimentalVersion: true`)，且默认未启用。这意味着 API 和功能在未来版本中可能会发生**重大更改或被移除**。
-   **推荐使用**：适合在**原型开发、技术预览或内部工具**中探索 Dataflow 驱动的网格变形工作流。**不建议**直接用于生产环境的项目，除非你准备好应对其可能的不兼容变更。作为学习 Dataflow 和几何处理技术的范例非常有价值。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [官方文档]：暂无（.uplugin 中 DocsURL 为空）