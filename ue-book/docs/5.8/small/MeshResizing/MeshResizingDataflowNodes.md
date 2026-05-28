# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放变形 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

MeshResizing 是一个基于 **Dataflow** 数据流图系统的网格变形与缩放工具集。它的核心目标是：**将一个网格的拓扑结构（骨架/顶点连接关系）"包裹"到另一个网格的形状上**，并在此过程中保持形状特征和顶点对应关系。

具体解决的问题包括：

- **骨骼网格到动态网格的转换**：将 SkeletalMesh 转换为带导入顶点映射信息的 DataflowMesh/ DynamicMesh，为后续变形操作提供基础
- **基于地标（Landmark）的网格包裹**：通过在源拓扑网格和目标形状网格上标记对应点，引导网格包裹算法将源网格的表面变形为目标形状
- **RBF 径向基函数插值变形**：基于采样点计算 RBF 权重，实现源网格到目标网格的高效变形
- **约束物理变形**：支持剪切约束、弯曲约束、边缘约束等物理模拟方式的网格变形
- **代理网格生成与插值**：生成拓扑一致的源/目标代理网格对，并支持在两者之间进行混合插值
- **UV 操作管线**：提供 UV 展开、UV 对齐、UV 变换等配套工具，确保变形后纹理仍然正确

该插件主要用于角色/生物的网格变形工作流——例如将一个体型的角色网格快速适配到另一个体型，同时保持拓扑、UV 和材质的一致性。

## 使用场景

- 你需要将一个角色的网格变形（wrap）到另一个角色的体型上 → 使用 **MeshWrap** 节点配合 Landmark 地标系统
- 你需要基于采样权重将源网格高效插值到目标形状 → 使用 **RBF Resizing** 节点（GenerateRBFResizingWeights + ApplyRBFResizing）
- 你需要在源形状和目标形状之间做平滑过渡动画 → 使用 **GenerateInterpolatedProxy** 节点控制 BlendAlpha
- 你需要在变形后重新生成 UV 映射 → 使用 **UVUnwrapNode**、**AlignUVMeshNode**、**UVMeshTransformNode** 组成 UV 处理管线
- 你需要基于物理约束（剪切/弯曲/边缘）的网格变形 → 使用 **MeshConstrainedDeformation** 节点

## Dataflow 节点用法

本插件不使用传统蓝图系统，而是通过 UE5 的 **Dataflow** 可视化数据流图来组织工作流。所有节点以 `USTRUCT` 形式定义，可在 Dataflow 编辑器中通过节点图连接使用。

> ⚠️ 本插件为实验性功能，API 随时可能变更。部分节点已标记 `Deprecated = "5.8"`。

### 核心节点

#### 网格转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SkeletalMeshToMesh` (v2) | 将 SkeletalMesh 转换为带导入顶点信息的 DataflowMesh | `FSkeletalMeshToMeshDataflowNode_v2` |
| `SkeletalMeshToMesh` (v1, 已废弃) | 旧版转换节点，输出 DynamicMesh，5.8 起已废弃 | `FSkeletalMeshToMeshDataflowNode` |

#### 代理网格与插值

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateResizableProxy` | 基于顶点映射数据生成拓扑一致的源/目标代理网格对 | `FGenerateResizableProxyDataflowNode` |
| `GenerateInterpolatedProxy` | 在源和目标代理网格之间做混合插值，Alpha=0 为源，Alpha=1 为目标 | `FGenerateInterpolatedProxyDataflowNode` |

#### 网格包裹

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MeshWrapLandmarks` | 定义网格包裹所需的地标点（可在编辑器中通过选择工具交互生成） | `FMeshWrapLandmarksNode` |
| `MeshWrap` | 将源拓扑网格包裹到目标形状网格上，使用地标对应关系引导 | `FMeshWrapNode` |

#### RBF 变形

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateRBFResizingWeights` | 对源网格采样并计算 RBF 插值权重数据 | `FGenerateRBFResizingWeightsNode` |
| `ApplyRBFResizing` | 将预计算的 RBF 权重应用到网格上进行变形，支持骨骼网格目标 | `FApplyRBFResizingNode` |

#### 网格包裹（综合）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MeshWarp` | 综合网格变形节点，支持 WrapDeform 和 RBFInterpolate 两种方法 | `FMeshWarpNode` |

#### 约束变形

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MeshConstrainedDeformationTestPlayground` | 基于物理约束的网格变形（剪切/弯曲/边缘约束） | `FMeshConstrainedDeformationNode` |

#### UV 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UVUnwrapNode` | UV 展开，支持 ExponentialMap、ConformalFreeBoundary、SpectralConformal 三种算法 | `FUVUnwrapNode` |
| `AlignUVMeshNode` | 将变形网格的 UV 与基准网格对齐 | `FAlignUVMeshNode` |
| `UVMeshTransformNode` | 对 UV 进行缩放、旋转、平移变换 | `FUVMeshTransformNode` |
| `UVResizeController` | UV 缩放控制器，判断网格是否适合 UV 缩放并输出可用 UV 通道 | `FUVResizeControllerNode` |

#### 纹理操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GrowTileRegion` | 在图像指定 UV 区域内找到方形瓦片并平铺到整张图像 | `FMeshResizingGrowTileRegionNode` |

### 典型工作流

**网格包裹（Mesh Wrap）工作流**：

1. 使用 `SkeletalMeshToMesh` (v2) 将源骨骼网格和目标骨骼网格分别转为 DataflowMesh
2. 使用 `MeshWrapLandmarks` 节点分别为源拓扑网格和目标形状网格定义地标点
3. 连接两个 Landmarks 节点和两个网格到 `MeshWrap` 节点
4. `MeshWrap` 根据 Identifier 匹配对应地标，执行包裹计算
5. 输出的 WrappedMesh 即为目标形状上的源拓扑网格

**RBF 变形工作流**：

1. 使用 `SkeletalMeshToMesh` 将源网格和目标网格转为 DataflowMesh
2. `GenerateRBFResizingWeights` 节点以源网格为输入，采样计算 RBF 权重
3. `ApplyRBFResizing` 节点以待变形网格、目标网格和预计算权重为输入，输出变形后的网格

**UV 处理管线**：

1. 变形后的网格通过 `UVResizeController` 检测可用 UV 通道
2. 使用 `AlignUVMeshNode` 将变形网格的 UV 与基准网格对齐
3. 使用 `UVMeshTransformNode` 对 UV 做最终的缩放/旋转/平移调整
4. 如需要，使用 `UVUnwrapNode` 重新展开 UV

## C++ 用法

本插件的 C++ API 主要面向 Dataflow 节点注册和自定义扩展。

### 头文件引入

```cpp
#include "MeshResizing/MeshWrapNode.h"
```

```cpp
#include "MeshResizing/BaseBodyDataflowNodes.h"
```

### 基本用法：注册 Dataflow 节点

各子模块提供注册函数，需在使用前调用以将节点注册到 Dataflow 系统中。

```cpp
// 来源: Private/MeshResizing/BaseBodyDataflowNodes.h
namespace UE::MeshResizing
{
    void RegisterBaseBodyDataflowNodes();
}

// 来源: Public/MeshResizing/MeshWrapNode.h
namespace UE::MeshResizing
{
    void RegisterMeshWrapNodes();
}

// 来源: Private/MeshResizing/MeshConstraintNodes.h
namespace UE::MeshResizing
{
    void RegisterMeshConstraintDataflowNodes();
}

// 来源: Private/MeshResizing/AlignUVMeshNode.h
namespace UE::MeshResizing
{
    void RegisterAlignUVMeshNodes();
}

// 来源: Private/MeshResizing/UVMeshTransformNode.h
namespace UE::MeshResizing
{
    void RegisterUVMeshTransformNodes();
}

// 来源: Private/MeshResizing/UVUnwrapNode.h
namespace UE::MeshResizing
{
    void RegisterUVUnwrapNodes();
}

// 来源: Private/MeshResizing/MeshResizingTextureNodes.h
namespace UE::MeshResizing
{
    void RegisterTextureNodes();
}
```

### 基本用法：定义 MeshWrap 地标

```cpp
// 来源: Public/MeshResizing/MeshWrapNode.h
// 定义单个地标：包含标识符和顶点索引
FMeshWrapLandmark Landmark;
Landmark.Identifier = TEXT("LeftShoulder");
Landmark.VertexIndex = 42;

// 定义地标对应关系
FMeshWrapCorrespondence Correspondence;
Correspondence.Identifier = TEXT("LeftShoulder");
Correspondence.SourceVertexIndex = 42;
Correspondence.TargetVertexIndex = 108;
```

### 进阶用法：自定义 MeshWrap 参数

```cpp
// 来源: Public/MeshResizing/MeshWrapNode.h
// FMeshWrapNode 的关键参数说明：

// 迭代控制
int32 MaxNumOuterIterations = 10;     // 外循环最大次数
int32 NumInnerIterations = 20;        // 内循环次数
float ProjectionTolerance = 1e-4f;    // 提前终止阈值

// 刚度权重
float LaplacianStiffness = 1.f;              // 保持源拓扑特征的拉普拉斯刚度
float InitialProjectionStiffness = 0.1f;     // 初始投影刚度（匹配目标形状）
float ProjectionStiffnessMuliplier = 10.f;   // 每次外循环投影刚度的倍增系数
float CorrespondenceStiffness = 1.f;         // 地标对应匹配刚度
```

## Demo 示例

### 自定义 Dataflow 节点扩展示例

本插件的核心是 Dataflow 节点系统。以下展示如何创建使用 MeshResizing 功能的自定义节点。

```cpp
// MyMeshResizeNode.h
#pragma once

#include "CoreMinimal.h"
#include "Dataflow/DataflowNode.h"
#include "MeshResizing/MeshWrapNode.h"

// 继承 FMeshWrapNode 创建自定义变体
USTRUCT(Meta = (MeshResizing, Experimental))
struct FMyCustomWrapNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomWrapNode, "MyCustomWrap", "Custom", "Custom Mesh Wrap")

public:
    FMyCustomWrapNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&SourceMesh);
        RegisterInputConnection(&TargetMesh);
        RegisterOutputConnection(&OutputMesh, &SourceMesh);
    }

private:
    UPROPERTY(meta = (DataflowInput))
    TObjectPtr<UDataflowMesh> SourceMesh;

    UPROPERTY(meta = (DataflowInput))
    TObjectPtr<UDataflowMesh> TargetMesh;

    UPROPERTY(meta = (DataflowOutput, DataflowPassthrough = "SourceMesh"))
    TObjectPtr<UDataflowMesh> OutputMesh;

    UPROPERTY(EditAnywhere, Category = "Custom", meta = (ClampMin = "0"))
    float CustomStiffness = 1.f;

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

```cpp
// MyMeshResizeNode.cpp
#include "MyMeshResizeNode.h"

void FMyCustomWrapNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 从输入端获取数据
    const UDataflowMesh* Source = GetValue(Context, SourceMesh);
    const UDataflowMesh* Target = GetValue(Context, TargetMesh);

    if (!Source || !Target)
    {
        return;
    }

    // 在此实现自定义的包裹逻辑
    // 可以调用 MeshResizingCore / MeshResizingEngine 模块中的底层函数
    // ...

    // 设置输出
    SetValue(Context, OutputMesh, /* result mesh */);
}
```

## 模块依赖

由于本插件为实验性 Dataflow 节点集合，主要依赖 Dataflow 框架和几何处理模块。

| 模块 | 用途 |
|---|---|
| `Dataflow` | Dataflow 节点框架，所有节点的基类 `FDataflowNode` 所在模块 |
| `DataflowEngine` | Dataflow 运行时引擎 |
| `GeometryFramework` | 动态网格 `UDynamicMesh`、`UDataflowMesh` 等几何体类型 |
| `GeometryCore` | 底层几何计算库（顶点映射、网格拓扑操作等） |
| `MeshResizingCore` | MeshResizing 内部核心类型（如 `FMeshResizingRBFInterpolationData`） |
| `MeshResizingEngine` | MeshResizing 内部引擎逻辑 |
| `MeshDescriptionEditor` | 编辑器专用，处理 MeshDescription 相关操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `a7802337` | Dataflow: | Dataflow 相关更新（commit message 未提供详情） |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将到来的头文件清理前补充必要的 #include |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | Dataflow 画笔工具新增套索选择功能 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 大量节点迁移到新的渲染系统 |

### 维护评价

- **创建时间**：2024 年 12 月，至今约 1 年半
- **最近更新频率**：约 1-2 个月一次功能性更新，保持活跃
- **活跃度**：近期更新包括编译修复、新功能（套索工具）、渲染系统迁移和头文件清理，说明仍在积极开发中
- **状态**：实验性插件（`IsExperimentalVersion=true`），默认未启用，API 不稳定
- **已知限制**：
  - 部分节点标记为 `Deprecated = "5.8"`，说明 API 仍在快速迭代
  - 顶点映射数据选项有限（源码注释提到 "only have two choices that work currently"）
  - RBF 插值中待变形网格输入 "currently unused"，功能尚未完整
  - 约束变形节点命名为 "TestPlayground"，尚处于测试阶段

**总体评价**：这是一个处于**早期活跃开发**阶段的实验性插件。Dataflow 节点覆盖了从网格转换、包裹、RBF 变形到 UV 处理的完整管线，但多个节点明确标记为实验性和已废弃状态。建议关注但**暂不用于生产环境**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [官方文档]()（无）