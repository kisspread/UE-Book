# Mesh Resizing - Dataflow Nodes

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格调整尺寸节点 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Dataflow节点） |
| 模块 | `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingNodes) | |

## 用途

Mesh Resizing 插件提供了一套基于 Dataflow 的网格尺寸调整流水线。本模块 `MeshResizingDataflowNodes` 提供了所有用于网格变形、UV 重映射、纹理平铺及 RBF 插值等操作的 Dataflow 节点。这些节点允许用户在 Dataflow 编辑器中以节点图形式组合出复杂的网格适配与变形逻辑，而无需编写 C++ 代码。

核心功能包括：
- **网格变形与包裹**：通过源网格和目标网格的顶点映射，将源网格变形至目标形状。
- **UV 操作**：对 UV 通道进行缩放、旋转、平移、重新映射以及自动展开。
- **纹理区域扩展**：根据 UV 三角形边界自动识别并扩展纹理中的重复平铺区域。
- **RBF 插值**：采样源网格顶点并计算径向基函数权重，然后应用于目标网格实现变形。
- **约束变形**：通过可配置的惯性、弯曲、剪切和边缘约束模拟物理变形。

## 使用场景

- 需要将一个角色的身体部分的网格形状适配到另一个不同体型的目标网格（例如服装适配）。
- 在纹理制作中，需要将贴图从一个 UV 布局自动平铺到另一个更小的 UV 区域。
- 需要根据已有骨骼网格的变形结果驱动动态网格的顶点位置（RBF 插值）。
- 在程序化建模流程中，将高模细节通过变形转移到低模上（结合 Wrap 与 UV 工具）。

## 蓝图用法

本模块的节点并非标准的蓝图可调用函数，而是 **Dataflow 节点**。在 **Dataflow 编辑器**（位于 Geometry 或 Scripting 菜单下）中，这些节点会出现在节点面板的 `MeshResizing` 分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AlignUVMeshNode` | 将输入网格的 UV 对齐到目标网格的 UV，可选缩放 | `FAlignUVMeshNode` |
| `SkeletalMeshToMesh` | 将骨骼网格转换为动态网格，保留顶点顺序与材质 | `FSkeletalMeshToMeshDataflowNode` |
| `GenerateResizableProxy` | 生成具有相同拓扑结构的源代理网格和目标代理网格，可用于插值 | `FGenerateResizableProxyDataflowNode` |
| `MeshConstrainedDeformationTestPlayground` | 对网格施加可配置的约束变形（弯曲、剪切、边缘） | `FMeshConstrainedDeformationNode` |
| `GrowTile` | 在纹理中搜索位于 UV 三角形内的方形瓦片，并将其复制扩展到整个图像 | `FMeshResizingGrowTileRegionNode` |
| `MeshWarp` | 通过包裹变形或 RBF 插值将输入网格变形至目标形状 | `FMeshWarpNode` |
| `GenerateRBFResizingWeights` | 对源网格采样，生成 RBF 插值所需的权重数据 | `FGenerateRBFResizingWeightsNode` |
| `ApplyRBFResizing` | 应用之前生成的 RBF 权重将网格变形到目标形状 | `FApplyRBFResizingNode` |
| `UVMeshTransform` | 对指定 UV 通道进行平移、旋转、缩放 | `FUVMeshTransformNode` |
| `UVResizeController` | 分析网格材质参数名称，确定需要重映射的 UV 通道 | `FUVResizeControllerNode` |
| `UV Unwrap` | 对指定 UV 通道进行展开（支持指数映射、保角自由边界、谱保角三种方法） | `FUVUnwrapNode` |
| `MeshWrapLandmarks` | 定义用于指导 Mesh Wrap 操作的顶点标记（地标），支持调试显示 | `FMeshWrapLandmarksNode` |
| `Mesh Wrap` | 使用地标配准对源拓扑网格进行包裹变形到目标形状 | `FMeshWrapNode` |

### 使用示例

在 Dataflow 编辑器中创建一个图，包含以下节点：
1. `SkeletalMeshToMesh`：将骨骼网格转换为动态网格，输出材质数组。
2. `GenerateResizableProxy`：将源动态网格和目标动态网格输入，计算具有相同拓扑的代理网格。
3. `ApplyRBFResizing`（可选）：或使用 `MeshWarp` 将源网格变形到目标形状。
4. `AlignUVMeshNode`：将变形后的网格 UV 对齐到目标网格 UV。
5. `UV Unwrap`：对最终网格的 UV 通道重新展开。

具体流程取决于需求，所有节点通过 Dataflow 数据流连接，最终输出变形后的网格和材质。

## C++ 用法

### 头文件引入

```cpp
#include "MeshResizing/AlignUVMeshNode.h"
#include "MeshResizing/BaseBodyDataflowNodes.h"
#include "MeshResizing/MeshConstraintNodes.h"
#include "MeshResizing/MeshResizingTextureNodes.h"
#include "MeshResizing/MeshWarpNode.h"
#include "MeshResizing/RBFInterpolationNodes.h"
#include "MeshResizing/UVMeshTransformNode.h"
#include "MeshResizing/UVResizeControllerNode.h"
#include "MeshResizing/UVUnwrapNode.h"
#include "MeshResizing/MeshWrapNode.h"
```

### 基本用法

以下代码演示如何在 Dataflow 图中编程创建并使用 `FAlignUVMeshNode`。出自 `Source/MeshResizingNodes/Private/MeshResizing/AlignUVMeshNode.cpp`（示例）。

```cpp
// 创建节点实例
UE::Dataflow::FNodeParameters Params;
FGuid NodeGuid = FGuid::NewGuid();
FAlignUVMeshNode* AlignNode = new FAlignUVMeshNode(Params, NodeGuid);

// 设置输入参数
UDataflowMesh* ResizingMesh = ...;  // 待对齐的网格
UDataflowMesh* BaseMesh = ...;      // 目标网格（UV 参考）
int32 UVChannel = 0;
int32 BaseUVChannel = -1;           // -1 表示使用同一通道
bool bScale = true;                 // 是否缩放 UV

Nodes::SetInputValue(*AlignNode, "ResizingMesh", ResizingMesh);
Nodes::SetInputValue(*AlignNode, "BaseMesh", BaseMesh);
Nodes::SetInputValue(*AlignNode, "UVChannelIndex", UVChannel);
Nodes::SetInputValue(*AlignNode, "BaseUVChannelIndex", BaseUVChannel);
// bScale 仅通过 EditAnywhere 编辑，无 DataflowInput，需直接设置
AlignNode->bScale = bScale;

// 触发评估
UE::Dataflow::FContext Context;
AlignNode->Evaluate(Context, nullptr);
```

### 进阶用法

结合 RBF 插值节点实现复杂变形流程（源自 `Source/MeshResizingNodes/Private/MeshResizing/RBFInterpolationNodes.h`）。

```cpp
// 1. 生成 RBF 权重
FGenerateRBFResizingWeightsNode* GenRBF = new FGenerateRBFResizingWeightsNode(Params);
Nodes::SetInputValue(*GenRBF, "SourceMesh", SourceMesh);
Nodes::SetInputValue(*GenRBF, "NumInterpolationPoints", 1500);
GenRBF->Evaluate(Context, nullptr);
FMeshResizingRBFInterpolationData InterpData = Nodes::GetOutputValue<FMeshResizingRBFInterpolationData>(*GenRBF, "InterpolationData");

// 2. 应用 RBF 变形到目标网格
FApplyRBFResizingNode* ApplyRBF = new FApplyRBFResizingNode(Params);
Nodes::SetInputValue(*ApplyRBF, "MeshToResize", InputMesh);
Nodes::SetInputValue(*ApplyRBF, "TargetMesh", TargetMesh);
Nodes::SetInputValue(*ApplyRBF, "InterpolationData", InterpData);
ApplyRBF->Evaluate(Context, nullptr);
UDataflowMesh* ResizedMesh = Nodes::GetOutputValue<UDataflowMesh*>(*ApplyRBF, "ResizedMesh");
```

RBF 节点还支持将变形结果映射到骨骼网格（`bUseSkeletalMeshTarget` = true），此时需提供 `TargetSkeletalMesh` 和 `TargetSkeletalMeshLODIndex`。

## Demo 示例

以下是一个完整的程序化网格变形示例（C++），使用 RBF 插值将动态网格变形至目标形状。

**头文件 (DemoResize.h)**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Dataflow/DataflowData.h"
#include "Dataflow/DataflowNode.h"
#include "MeshResizing/RBFInterpolationNodes.h"
#include "MeshResizing/MeshWarpNode.h"

class DEMO_API DemoResize
{
public:
    static UDataflowMesh* ResizeMesh(UDataflowMesh* InSource, UDataflowMesh* InTarget);
};
```

**实现文件 (DemoResize.cpp)**
```cpp
#include "DemoResize.h"
#include "Dataflow/DataflowContext.h"
#include "Dataflow/DataflowNode.h"

UDataflowMesh* DemoResize::ResizeMesh(UDataflowMesh* InSource, UDataflowMesh* InTarget)
{
    using namespace UE::Dataflow;
    
    // 创建上下文
    FContext Context;
    
    // 设置节点参数（此处简单创建）
    FNodeParameters Params;
    
    // 1. 生成 RBF 权重
    FGenerateRBFResizingWeightsNode* GenRBF = new FGenerateRBFResizingWeightsNode(Params);
    Nodes::SetInputValue(*GenRBF, "SourceMesh", InSource);
    Nodes::SetInputValue(*GenRBF, "NumInterpolationPoints", 1500);
    GenRBF->Evaluate(Context, nullptr);
    
    FMeshResizingRBFInterpolationData InterpData;
    if (!Context.GetOutput(*GenRBF, "InterpolationData", InterpData)) return nullptr;
    
    // 2. 应用 RBF 变形到目标网格
    FApplyRBFResizingNode* ApplyRBF = new FApplyRBFResizingNode(Params);
    Nodes::SetInputValue(*ApplyRBF, "MeshToResize", InSource);
    Nodes::SetInputValue(*ApplyRBF, "TargetMesh", InTarget);
    Nodes::SetInputValue(*ApplyRBF, "InterpolationData", InterpData);
    ApplyRBF->Evaluate(Context, nullptr);
    
    UDataflowMesh* ResizedMesh = nullptr;
    Context.GetOutput(*ApplyRBF, "ResizedMesh", ResizedMesh);
    
    // 清理（实际项目中需使用智能指针管理）
    delete GenRBF;
    delete ApplyRBF;
    
    return ResizedMesh;
}
```

## 模块依赖

根据模块功能推断，`MeshResizingDataflowNodes` 的独特依赖如下（省略 Core/Engine/Dataflow 等标准模块）：

| 模块 | 用途 |
|---|---|
| `MeshResizingCore` | 提供核心网格数据结构（如 `UDataflowMesh`） |
| `MeshResizingEngine` | 提供计算引擎支持（RBF、Wrap 等算法） |
| `Dataflow` | Dataflow 框架基础（节点、上下文、渲染类型） |
| `GeometryCore` | 动态网格（`FDynamicMesh3`）操作、Wrap 操作、UV 展开算法 |
| `GeometryCollection` | `ManagedArrayCollection` 数据结构 |
| `MeshDescription` | 骨骼网格转换时需要（Editor 下） |
| `RHI` | 纹理处理节点需要图像数据 |

**注意**：本模块为 Runtime 类型，但部分功能（如骨骼网格转换、纹理处理）依赖 Editor-only 数据，仅可在 Editor 环境下正常工作。

## 维护状态

### 近期更新

- 2025-09-29 92ddeeb8 修复顶点分配 bug  
- 2025-09-23 ca2d126b Dataflow 编辑器：使工具添加节点按钮适用于非 ManagedArrayCollection 的工具  
- 2025-08-19 d66ea4c2 Dataflow 地标工具：修复一些指针检查  
- 2025-08-19 a5c868d7 Dataflow 地标工具：修复未修改时标记节点无效的问题  
- 2025-08-15 e79d88de 修复空网格时 RBF 插值除零错误  

### 维护评价

该模块创建于 2025-08-15，距今不到一年，目前处于活跃开发阶段。最近的更新（2025-09-29）为功能性修复，且持续有内容追加。由于其标记为实验性（`IsExperimentalVersion=true`），API 可能不稳定，功能可能未完全成熟，但基本核心流程已经可用。推荐在实验性项目中使用，并关注后续版本变更。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing)
- [本模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingNodes)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing/Tests)（假设存在）