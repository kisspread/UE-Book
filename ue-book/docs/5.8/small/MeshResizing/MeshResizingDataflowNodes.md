# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Dataflow 节点资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

MeshResizing 是一个基于 Dataflow 的网格变形与缩放系统，用于将一个网格的拓扑结构适配到不同形状的目标网格上。核心解决的问题是：**当你有一个源网格（如角色的基础骨骼网格体），需要生成与之拓扑相同但形状不同的变体时，如何保持顶点对应关系和动画兼容性**。

该插件提供了三种主要变形策略：

1. **Mesh Wrap（网格包裹）**：基于关键点（Landmarks）对应关系，将源拓扑网格包裹到目标形状上，使用拉普拉斯变形保持拓扑特征。
2. **RBF Interpolation（径向基函数插值）**：通过在源网格上采样插值点并计算 RBF 权重，然后应用到目标网格上实现平滑变形。
3. **Mesh Warp（网格扭曲）**：高层封装节点，封装了 Wrap Deform 和 RBF Interpolate 两种方法，通过 Alpha 参数控制源到目标的混合程度。

此外还包含 UV 操作节点（UV 展开、对齐、变换）和纹理处理节点，用于在网格变形后重新适配纹理坐标。

## 使用场景

- 你有一个基础角色骨骼网格体，需要为不同体型生成变体 → 用 RBF Interpolation 节点链
- 你需要将一个网格的拓扑结构"包裹"到另一个形状不同的网格上 → 用 Mesh Wrap 节点配合 Landmark 关键点
- 你需要在源形状和目标形状之间平滑插值生成中间状态 → 用 GenerateInterpolatedProxy 节点
- 网格变形后 UV 坐标需要重新适配 → 用 UV Unwrap / UV Mesh Transform / Align UV Mesh 节点
- 纹理需要在变形后的网格上重新平铺 → 用 Grow Tile Region 节点

## 蓝图用法

本插件的所有功能通过 **Dataflow 节点** 实现，不提供传统蓝图可调用函数。所有节点均注册在 `MeshResizing` 分类下，可在 Dataflow Editor 中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SkeletalMeshToMesh` | 将 SkeletalMesh 转换为 DataflowMesh，保留导入顶点映射信息 | `FSkeletalMeshToMeshDataflowNode_v2` |
| `GenerateResizableProxy` | 生成一对拓扑相同的代理网格，用于后续插值 | `FGenerateResizableProxyDataflowNode` |
| `GenerateInterpolatedProxy` | 在源和目标代理网格之间插值，Alpha 控制混合比例 | `FGenerateInterpolatedProxyDataflowNode` |
| `GenerateRBFResizingWeights` | 采样源网格并计算 RBF 插值权重数据 | `FGenerateRBFResizingWeightsNode` |
| `ApplyRBFResizing` | 应用预计算的 RBF 权重对网格进行缩放变形 | `FApplyRBFResizingNode` |
| `MeshWrapLandmarks` | 定义网格包裹操作的关键点（Landmarks），可通过选择工具生成 | `FMeshWrapLandmarksNode` |
| `MeshWrap` | 基于 Landmark 对应关系执行网格包裹，将源拓扑适配到目标形状 | `FMeshWrapNode` |
| `MeshWarp` | 高层网格扭曲节点，封装 WrapDeform 和 RBFInterpolate 两种方法 | `FMeshWarpNode` |
| `MeshConstrainedDeformationTestPlayground` | 受约束变形测试节点，支持剪切/弯曲/边缘约束 | `FMeshConstrainedDeformationNode` |
| `UVResizeController` | UV 缩放控制器，检测可缩放的 UV 通道 | `FUVResizeControllerNode` |
| `UVUnwrapNode` | UV 展开，支持指数映射、保角自由边界、谱保角三种算法 | `FUVUnwrapNode` |
| `AlignUVMeshNode` | 将缩放网格的 UV 与基础网格 UV 对齐 | `FAlignUVMeshNode` |
| `UVMeshTransformNode` | 对 UV 坐标进行缩放、旋转、平移变换 | `FUVMeshTransformNode` |
| `GrowTileRegion` | 在有效 UV 区域内查找方形纹理块并平铺整个图像 | `FMeshResizingGrowTileRegionNode` |

### 使用示例（Dataflow 图描述）

**基本 Mesh Wrap 工作流：**

1. 添加 `SkeletalMeshToMesh` 节点，将源 SkeletalMesh 转为 DataflowMesh
2. 添加另一个 `SkeletalMeshToMesh` 节点，将目标 SkeletalMesh 转为 DataflowMesh
3. 添加 `MeshWrapLandmarks` 节点（两个），分别为源和目标网格定义对应关键点
4. 添加 `MeshWrap` 节点：
   - 将源 DataflowMesh 连接到 `SourceTopologyMesh`
   - 将目标 DataflowMesh 连接到 `TargetShapeMesh`
   - 将两组 Landmarks 连接到 `SourceTopologyLandmarks` 和 `TargetShapeLandmarks`
5. `WrappedMesh` 输出即为拓扑来自源、形状匹配目标的变形结果

**RBF 缩放工作流：**

1. `SkeletalMeshToMesh` → 转换基础网格
2. `GenerateRBFResizingWeights` → 采样源网格生成插值数据
3. `ApplyRBFResizing` → 输入目标网格和插值数据，输出缩放后的网格

## C++ 用法

本插件的所有功能通过 Dataflow 节点的 USTRUCT 注册实现。使用者主要通过 Dataflow 图组合使用，而非直接 C++ 调用。

### 头文件引入

```cpp
#include "MeshResizing/BaseBodyDataflowNodes.h"
#include "MeshResizing/MeshWrapNode.h"
#include "MeshResizing/RBFInterpolationNodes.h"
#include "MeshResizing/MeshWarpNode.h"
```

### 基本用法

MeshResizingDataflowNodes 模块通过命名空间函数注册所有节点：

```cpp
// 注册所有 MeshResizing Dataflow 节点（通常在模块 StartupModule 中调用）
#include "MeshResizing/BaseBodyDataflowNodes.h"
#include "MeshResizing/MeshWrapNode.h"
#include "MeshResizing/RBFInterpolationNodes.h"
#include "MeshResizing/MeshConstraintNodes.h"
#include "MeshResizing/MeshWarpNode.h"
#include "MeshResizing/AlignUVMeshNode.h"
#include "MeshResizing/UVMeshTransformNode.h"
#include "MeshResizing/UVUnwrapNode.h"
#include "MeshResizing/MeshResizingTextureNodes.h"
#include "MeshResizing/UVResizeControllerNode.h"

// 各节点组通过命名空间函数注册
UE::MeshResizing::RegisterBaseBodyDataflowNodes();
UE::MeshResizing::RegisterMeshWrapNodes();
UE::MeshResizing::RegisterMeshConstraintDataflowNodes();
UE::MeshResizing::RegisterAlignUVMeshNodes();
UE::MeshResizing::RegisterUVMeshTransformNodes();
UE::MeshResizing::RegisterUVUnwrapNodes();
UE::MeshResizing::RegisterTextureNodes();
```

### 进阶用法

**Mesh Wrap 节点的关键参数（源码提取）：**

```cpp
// Mesh Wrap 使用内外循环迭代：
// 内循环（NumInnerIterations）：执行拉普拉斯变形
// 外循环（MaxNumOuterIterations）：每轮增加投影刚度（乘以 ProjectionStiffnessMultiplier）
// 收敛条件：当投影误差 < ProjectionTolerance 时提前终止

// 关键参数含义：
// LaplacianStiffness     - 保持源拓扑特征的权重
// InitialProjectionStiffness - 初始投影刚度，每外循环乘以倍增因子
// ProjectionStiffnessMultiplier - 投影刚度倍增因子（默认 10.0）
// CorrespondenceStiffness - Landmark 对应点匹配的权重
```

**RBF 节点的目标网格支持：**

```cpp
// ApplyRBFResizingNode 支持两种目标网格类型：
// 1. UDataflowMesh - 通用动态网格（默认）
// 2. USkeletalMesh - 骨骼网格体（需要设置 bUseSkeletalMeshTarget = true）
//    目标骨骼网格体的顶点必须与源网格匹配

// 注意：使用 SkeletalMesh 作为目标时，需要访问 MeshDescription（编辑器专用数据）
// 因此该功能仅在 WITH_EDITORONLY_DATA 下可用
```

**UV Unwrap 支持的算法：**

```cpp
// EUVUnwrapMethod 枚举：
// ExponentialMap        - 指数映射
// ConformalFreeBoundary - 保角自由边界
// SpectralConformal     - 谱保角（默认，质量通常最好）
```

## Demo 示例

以下展示如何在 C++ 中创建一个使用 Mesh Resizing 节点的 Dataflow 图：

```cpp
// MeshResizingDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Dataflow/DataflowGraph.h"
#include "MeshResizing/MeshWrapNode.h"
#include "MeshResizing/BaseBodyDataflowNodes.h"

class FMeshResizingDemo
{
public:
    /** 创建一个完整的 Mesh Wrap Dataflow 图示例 */
    static TSharedPtr<UE::Dataflow::FGraph> CreateMeshWrapGraph()
    {
        auto Graph = MakeShared<UE::Dataflow::FGraph>();

        // 1. 将源 SkeletalMesh 转换为 DataflowMesh
        auto* SourceConvertNode = Graph->AddNode(
            FSkeletalMeshToMeshDataflowNode_v2::StaticStruct(),
            UE::Dataflow::FNodeParameters()
        );

        // 2. 将目标 SkeletalMesh 转换为 DataflowMesh
        auto* TargetConvertNode = Graph->AddNode(
            FSkeletalMeshToMeshDataflowNode_v2::StaticStruct(),
            UE::Dataflow::FNodeParameters()
        );

        // 3. 添加 Mesh Wrap 节点
        auto* WrapNode = Graph->AddNode(
            FMeshWrapNode::StaticStruct(),
            UE::Dataflow::FNodeParameters()
        );

        // 连接节点（伪代码，实际连接方式取决于 Dataflow API）
        // SourceConvertNode.Mesh -> WrapNode.SourceTopologyMesh
        // TargetConvertNode.Mesh -> WrapNode.TargetShapeMesh

        return Graph;
    }
};
```

```cpp
// MeshResizingDemo.cpp
#include "MeshResizingDemo.h"
// 实现省略，主要展示节点的使用方式和连接关系
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | Dataflow 图引擎框架，所有节点的基类和运行时 |
| `DataflowEngine` | Dataflow 引擎运行时支持 |
| `GeometryCore` | 几何计算核心（DynamicMesh 等） |
| `DynamicMesh` | 动态网格资产类型 |
| `MeshConversion` | 网格格式转换（SkeletalMesh ↔ DynamicMesh） |
| `ModelingComponents` | 建模组件（用于编辑器工具集成） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `a7802337` | Dataflow: | Dataflow 相关更新（提交信息不完整） |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将到来的头文件清理前添加必要的 include |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | 为绘制工具添加套索支持，利用网格编辑新特性 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 更新大量节点以使用新渲染系统 |

### 维护评价

- **创建时间**：2024-12-09，非常年轻的插件
- **近期活跃度**：持续活跃，2025-12 至 2026-05 期间有多次功能性更新
- **维护状态**：**活跃维护中**，仍在持续开发新功能（套索支持、渲染系统迁移等）
- **已知限制**：
  - 标记为实验性（`IsExperimentalVersion=true`），API 可能发生破坏性变更
  - 默认未启用（`EnabledByDefault=false`），需手动在编辑器中启用
  - 部分已标记 `Deprecated = "5.8"` 的旧节点将在未来版本移除
- **推荐程度**：⚠️ 适合早期测试和实验，不建议在生产环境使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [Dataflow 节点源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingNodes)
- [Mesh Wrap 节点](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingNodes/Private/MeshResizing/MeshWrapNode.h)
- [RBF 插值节点](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingNodes/Private/MeshResizing/RBFInterpolationNodes.h)