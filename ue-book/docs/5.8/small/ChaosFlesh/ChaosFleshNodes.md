# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 布料肉身模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是基于 Chaos 物理引擎的**软体（四面体体素）模拟**系统，用于在 UE5 中实现高质量的**肌肉、脂肪、内脏**等生物组织的物理表现。

该插件的核心能力包括：

- **四面体网格生成**：将表面三角网格（StaticMesh/SkeletalMesh）转换为体积四面体网格，支持 IsoStuffing 和 TetWild 两种算法
- **肌肉纤维场计算**：根据肌肉的起止点（Origin/Insertion）计算每个四面体单元的纤维方向，实现方向性收缩
- **肌肉激活模拟**：支持基于肌肉长度的激活曲线控制，可从动画资产导入最低肌肉长度数据
- **骨骼绑定**：将肉体的四面体网格绑定到骨骼网格体，支持运动学（Kinematic）和弱约束（Position Target）两种模式
- **表面约束**：在不同几何体表面之间创建点-三角形弱约束、气密性四面体约束、体积约束等
- **碰撞处理**：支持场景碰撞射线检测候选点、可碰撞顶点设置等
- **LOD 支持**：通过 `MakeFleshAsset` 节点支持多 LOD 级别

该插件通过 UE5 的 **Dataflow** 节点图系统进行资产创作，用户在 Dataflow Editor 中搭建节点图来定义肉体模拟管线。

## 使用场景

- 你在制作高品质的拟人角色动画，需要真实表现**肌肉收缩、膨胀、皮肤滑动**效果 → 使用 ChaosFlesh 搭建肉体模拟
- 你需要在角色蒙皮网格体下方创建**体积化的四面体网格**，作为物理模拟基础 → 使用 `CreateTetrahedron` 节点
- 你想让角色的**肌肉根据动画骨骼运动自动激活收缩** → 使用 `ComputeMuscleActivationData` + `SetMuscleActivationParameter` 节点
- 你需要将**多个肉体部件组合**（例如躯干、四肢独立生成后合并）→ 使用 `AppendTetrahedralCollection` 节点
- 你想让肉体几何体与外部网格体之间产生**软接触约束**（如器官之间、器官与骨骼之间）→ 使用 `SetVertexTrianglePositionTargetBinding` 或 `CreateAirTetrahedralConstraint` 节点
- 你需要为机器学习训练生成**肌肉激活采样动画** → 使用 `CurveSamplingAnimationAssetTerminal` 节点

## 蓝图用法

ChaosFlesh 主要通过 **Dataflow 节点图**（非传统蓝图）进行使用。以下为在 Dataflow Editor 中可用的核心节点。

### 四面体网格生成节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateTetrahedron` | 从封闭表面网格生成四面体体积网格（支持 IsoStuffing 和 TetWild 算法） | `FCreateTetrahedronDataflowNode` |
| `RadialTetrahedron` | 生成径向对称的圆柱/管状四面体网格 | `FRadialTetrahedronDataflowNodes` |

### 肌肉模拟节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ComputeMuscleActivationData` | 计算肌肉激活数据，确定哪些肌肉可激活并计算激活参数 | `FComputeMuscleActivationDataNode_v2` |
| `SetMuscleActivationParameter` | 设置每块肌肉的收缩参数（体积缩放、纤维长度比、激活阈值等），支持全局和自定义模式 | `FSetMuscleActivationParameterNode` |
| `ComputeFiberField` | 从起止点计算每四面体的肌肉纤维方向场 | `FComputeFiberFieldNode` |
| `ComputeFiberStreamline` | 在纤维场中计算从起点到止点的流线 | `FComputeFiberStreamlineNode` |
| `GenerateOriginInsertion` | 生成肌肉的起始点和插入点（通过半径搜索扩展） | `FGenerateOriginInsertionNode` |
| `KinematicMuscleAttachments` | 创建肌肉起止点的运动学附着约束 | `FKinematicMuscleAttachmentsDataflowNode` |

### 约束与绑定节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetFleshBonePositionTargetBinding` | 将肉体顶点绑定到骨骼网格体表面（运动学或弱约束模式） | `FSetFleshBonePositionTargetBindingDataflowNode_v2` |
| `SetVertexTrianglePositionTargetBinding` | 在不同几何体表面之间创建点-三角形弱约束 | `FSetVertexTrianglePositionTargetBindingDataflowNode` |
| `DeleteVertexTrianglePositionTargetBinding` | 删除两点集之间的弱约束 | `FDeleteVertexTrianglePositionTargetBindingDataflowNode` |
| `SetVertexTetrahedraPositionTargetBinding` | 将顶点绑定到目标四面体单元 | `FSetVertexTetrahedraPositionTargetBindingDataflowNode` |
| `SetVertexVertexPositionTargetBinding` | 将顶点绑定到目标顶点（基于搜索半径） | `FSetVertexVertexPositionTargetBindingDataflowNode` |
| `SetCollidableVertices` | 设置可碰撞顶点子集，未选中的顶点之间不会碰撞 | `FSetCollidableVerticesDataflowNode` |
| `CreateAirTetrahedralConstraint` | 在不同几何体表面之间创建空气四面体约束以维持间距 | `FCreateAirTetrahedralConstraintDataflowNode` |
| `CreateAirVolumeConstraint` | 创建基于四面体体积的约束，允许沿三角形平面滑动 | `FCreateAirVolumeConstraintDataflowNode` |
| `KinematicSkeletonConstraint` | 将四面体网格约束到骨架 | `FKinematicSkeletonConstraintDataflowNode` |
| `KinematicInitialization` | 初始化运动学约束（将指定顶点设为运动学状态） | `FKinematicInitializationDataflowNode` |

### 网格操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AppendTetrahedralCollection` | 将另一个四面体集合追加到当前集合，支持变换合并 | `FAppendTetrahedralCollectionDataflowNode_v2` |
| `DeleteFleshVertices` | 根据选择集删除肉体顶点及其关联元素 | `FDeleteFleshVerticesDataflowNode` |
| `IsolateComponent` | 隔离指定几何体索引的组件 | `FIsolateComponentNode` |
| `ComputeIslands` | 计算四面体网格中的连通岛 | `FComputeIslandsNode` |
| `GetSurfaceIndices` | 获取指定几何组的表面顶点选择集 | `FGetSurfaceIndicesNode` |
| `GenerateSurfaceBindings` | 将渲染网格体表面绑定到四面体网格表面 | `FGenerateSurfaceBindings` |
| `GenerateSkeletalBindings` | 生成骨骼网格体与肉体之间的绑定 | `FGenerateSkeletalBindings` |
| `AuthorTetMetrics` | 计算四面体网格的质量指标 | `FCalculateTetMetrics` |

### 属性与资产节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetFleshDefaultProperties` | 设置肉体默认物理属性（密度、刚度、阻尼、不可压缩性、膨胀） | `FSetFleshDefaultPropertiesNode` |
| `SkinSimulationProperties` | 设置蒙皮模拟属性（是否启用蒙皮约束） | `FSkinSimulationPropertiesDataflowNodes` |
| `TriangleMeshSimulationProperties` | 设置三角网格模拟属性（密度、刚度、阻尼） | `FTriangleMeshSimulationPropertiesDataflowNodes` |
| `MakeFleshAsset` | 将 FManagedArrayCollection 转换为 FleshAsset 资产，支持多 LOD 输入 | `FMakeFleshAssetNode` |
| `FleshAssetTerminal` | Dataflow 终端节点，将模拟结果输出到 FleshAsset | `FFleshAssetTerminalDataflowNode` |
| `GetFleshAsset` | 从 FleshAsset 资产读取集合数据 | `FGetFleshAssetDataflowNode` |
| `AppendToCollectionTransformAttribute` | 向集合追加变换属性 | `FAppendToCollectionTransformAttributeDataflowNode` |
| `AddKinematicParticles` | 向集合添加运动学粒子 | `FAddKinematicParticlesDataflowNode` |
| `AuthorSceneCollisionCandidates` | 标记顶点为场景碰撞射线检测候选 | `FAuthorSceneCollisionCandidates` |

### 可视化节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `VisualizeFiberField` | 可视化每四面体的肌肉纤维方向 | `FVisualizeFiberFieldNode` |
| `VisualizePositionTargets` | 可视化位置目标向量 | `FVisualizePositionTargetsNode` |
| `VisualizeKinematicFaces` | 可视化运动学面 | `FVisualizeKinematicFacesNode` |

### 专用终端节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CurveSamplingAnimationAssetTerminal` | 生成用于肌肉激活 ML 训练的动画资产（逐肌肉脉冲激活曲线） | `FCurveSamplingAnimationAssetTerminalNode` |
| `ReadSkeletalMeshCurves` | 从骨骼网格体读取曲线数据并关联到肌肉名称 | `FReadSkeletalMeshCurvesDataflowNode` |

### 使用示例（Dataflow 节点图描述）

**基本肉体模拟管线**：

1. 使用 `CreateTetrahedron` 从封闭的三角网格生成四面体体积网格
2. 使用 `SetFleshDefaultProperties` 设置物理属性（密度、刚度、阻尼、不可压缩性）
3. 使用 `SetFleshBonePositionTargetBinding` 将肉体绑定到骨骼网格体
4. 使用 `MakeFleshAsset` 或 `FleshAssetTerminal` 将结果输出为资产

**肌肉模拟管线**（在基本管线基础上增加）：

1. 使用 `GenerateOriginInsertion` 定义肌肉的起始点和插入点
2. 使用 `ComputeFiberField` 计算肌肉纤维方向场
3. 使用 `ComputeMuscleActivationData` 计算肌肉激活数据
4. 使用 `SetMuscleActivationParameter` 配置肌肉收缩参数（全局或逐肌肉自定义）
5. 使用 `FleshAssetTerminal` 输出最终资产

**多部件合并管线**：

1. 对每个肉体部件分别生成四面体网格（步骤同上）
2. 使用 `AppendTetrahedralCollection` 将多个部件合并为一个集合
3. 使用 `SetVertexTrianglePositionTargetBinding` 在部件之间创建软约束
4. 使用 `CreateAirTetrahedralConstraint` 或 `CreateAirVolumeConstraint` 维持部件间距

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFleshNodes/ChaosFleshNodesPlugin.h"
// 具体节点头文件位于 Public/Dataflow/ 目录下
#include "ChaosFleshNodes/Public/Dataflow/ChaosFleshCreateTetrahedronNode.h"
```

### 基本用法

ChaosFlesh 的节点基于 UE5 Dataflow 框架，每个节点是继承自 `FDataflowNode` 的 USTRUCT。以下为节点的核心结构模式：

```cpp
// 所有 ChaosFlesh Dataflow 节点遵循以下模式
// 1. 继承 FDataflowNode
// 2. 使用 DATAFLOW_NODE_DEFINE_INTERNAL 宏定义节点名称和分类
// 3. 通过 UPROPERTY + DataflowInput/DataflowOutput 元数据声明引脚
// 4. 在构造函数中注册连接
// 5. 实现 Evaluate() 方法处理逻辑

// 示例：SetFleshDefaultProperties 节点
USTRUCT(meta = (DataflowFlesh))
struct FSetFleshDefaultPropertiesNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FSetFleshDefaultPropertiesNode, "SetFleshDefaultProperties", "Flesh", "")

public:
    // 输入/输出通过同一属性的 Passthrough 连接
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DisplayName = "Collection", DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    // 可编辑的物理参数
    UPROPERTY(EditAnywhere, Category = "Dataflow")
    float Density = 1.f;

    UPROPERTY(EditAnywhere, Category = "Dataflow")
    float VertexStiffness = 1e6;

    UPROPERTY(EditAnywhere, Category = "Dataflow", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float VertexDamping = 0.f;

    // 构造函数中注册连接
    FSetFleshDefaultPropertiesNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterOutputConnection(&Collection, &Collection);
    }

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

### 进阶用法

**自定义 Dataflow 节点注册**：

插件通过命名空间函数注册特定类别的节点到 Dataflow 系统：

```cpp
// 位置目标绑定节点注册
namespace UE::Dataflow
{
    void RegisterChaosFleshPositionTargetInitializationNodes();
}

// 运动学初始化节点注册
namespace UE::Dataflow
{
    void RegisterChaosFleshKinematicInitializationNodes();
}

// 引擎资产节点注册
namespace UE::Dataflow
{
    void RegisterChaosFleshEngineAssetNodes();
}
```

**网格四面体化**：`CreateTetrahedron` 节点支持两种算法，通过枚举选择：

```cpp
// 两种四面体化方法
UENUM()
enum TetMeshingMethod : int
{
    IsoStuffing UMETA(DisplayName = "IsoStuffing"),  // 规则化细分，参数简单
    TetWild     UMETA(DisplayName = "TetWild"),       // 优化质量，参数丰富
};
```

**肌肉激活参数系统**支持全局和逐肌肉自定义两种模式：

```cpp
UENUM()
enum EParameterMethod : int
{
    Global  UMETA(DisplayName = "Use global parameters"),
    Custom  UMETA(DisplayName = "Override with custom parameters"),
};

// 逐肌肉参数结构
USTRUCT()
struct FPerMuscleParameter
{
    GENERATED_USTRUCT_BODY()

    // 是否编辑特定肌肉名称
    UPROPERTY(EditAnywhere, meta = (InlineEditConditionToggle))
    bool bCanEditMuscleName = false;

    UPROPERTY(EditAnywhere, meta = (EditCondition = "bCanEditMuscleName"))
    FString MuscleName;

    // 收缩体积缩放（>1 膨胀，=1 体积守恒）
    UPROPERTY(EditAnywhere, meta = (ClampMin = "0"))
    float ContractionVolumeScale = 1.f;

    // 最大激活时纤维长度比（越小收缩越强）
    UPROPERTY(EditAnywhere, meta = (ClampMin = "0", ClampMax = "1"))
    float FiberLengthRatioAtMaxActivation = 0.5f;

    // 达到最大激活的肌肉长度比阈值
    UPROPERTY(EditAnywhere, meta = (ClampMin = "0", ClampMax = "1"))
    float MuscleLengthRatioThresholdForMaxActivation = 0.75f;

    // 膨胀体积缩放
    UPROPERTY(EditAnywhere, meta = (ClampMin = "0"))
    float InflationVolumeScale = 1.f;

    // 自定义长度-激活曲线
    UPROPERTY(EditAnywhere, meta = (EditCondition = "bUseLengthActivationCurve"))
    FRuntimeFloatCurve LengthActivationCurve;
};
```

**骨骼绑定模式**：

```cpp
UENUM(BlueprintType)
enum class ESkeletalBindingMode : uint8
{
    Dataflow_SkeletalBinding_Kinematic        UMETA(DisplayName = "Kinematic"),
    Dataflow_SkeletalBinding_PositionTarget   UMETA(DisplayName = "Position Target"),
};
```

**辅助工具函数**：

```cpp
namespace UE::Dataflow
{
    // 获取四面体网格的表面三角形
    TArray<FIntVector3> CHAOSFLESHNODES_API GetSurfaceTriangles(
        const TArray<FIntVector4>& Tets, const bool bKeepInterior);

    // 在集合中查找匹配的几何体索引
    TArray<int32> CHAOSFLESHNODES_API GetMatchingMeshIndices(
        const TArray<FString>& MeshNames, const FManagedArrayCollection* InCollection);
}
```

## Demo 示例

以下为创建一个自定义 ChaosFlesh Dataflow 节点的最小示例：

```cpp
// MyCustomFleshNode.h
#pragma once

#include "Dataflow/DataflowNode.h"
#include "ManagedArrayCollection/ManagedArrayCollection.h"
#include "MyCustomFleshNode.generated.h"

USTRUCT(meta = (DataflowFlesh))
struct FMyCustomFleshNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomFleshNode, "MyCustomFlesh", "Flesh", "")

public:
    // 带 Passthrough 的集合输入/输出
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DisplayName = "Collection", DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    // 可编辑参数
    UPROPERTY(EditAnywhere, Category = "Dataflow", meta = (ClampMin = "0.0"))
    float MyStiffness = 1.f;

    FMyCustomFleshNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterOutputConnection(&Collection, &Collection);
    }

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

```cpp
// MyCustomFleshNode.cpp
#include "MyCustomFleshNode.h"

void FMyCustomFleshNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 从 Context 获取集合数据
    FManagedArrayCollection& InCollection = Context.GetPassthroughValue<FManagedArrayCollection>(
        FManagedArrayCollection(), &Collection);

    // 在此处对 Collection 进行自定义处理
    // 例如：遍历四面体单元，应用自定义刚度等

    // 输出结果
    Context.SetPassthroughValue<FManagedArrayCollection>(&Collection, InCollection);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心 |
| `ChaosSolverEngine` | Chaos 求解器 |
| `GeometryCollectionEngine` | GeometryCollection 引擎层（四面体运行时模拟） |
| `Dataflow` | UE5 Dataflow 节点图框架 |
| `GeometryFramework` | 动态网格体（UDynamicMesh）支持 |
| `MeshConversion` | 网格格式转换 |
| `ModelingComponents` | 建模组件（用于可视化输出） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `981bc9da` | Dataflow: | Dataflow 相关更新 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理纤维场生成节点代码 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复掩码缓冲区数量赋值错误 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃肉体资产中的 StaticMesh 属性 |

### 维护评价

**活跃维护中**。ChaosFlesh 自 2022 年 3 月创建以来持续更新，最近一次提交在 2026 年 5 月 13 日，保持非常高的更新频率。

从源码可以看出该插件仍在**快速迭代**：
- 多个节点标记了 `Deprecated = "5.6"` 或 `Deprecated = "5.7"`，说明持续在重构 API
- 不断有 `_v2` 版本节点替代旧版本，改进绑定方法和搜索半径等核心功能
- 最近清理了纤维场生成节点代码，废弃了 StaticMesh 属性

**注意事项**：
- 该插件标记为 **IsExperimentalVersion = true** 且 **EnabledByDefault = false**，需手动在 Plugins 面板中启用
- 由于实验性状态，API 随 UE 版本可能有 breaking changes
- 使用的是 UE5 Dataflow 框架，需要在 Dataflow Editor 中操作
- 部分节点已标记为 Deprecated，建议使用最新版本的节点（如 `_v2` 后缀版本）

**推荐使用**：如果你需要高品质的肌肉/肉体物理模拟，ChaosFlesh 是目前 UE5 官方提供的唯一解决方案。尽管仍为实验性功能，但已有丰富的节点集和活跃的维护，适合在生产环境中谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- 官方文档（无）
- 测试用例（当前模块内未发现测试文件）