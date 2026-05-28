# Chaos Rigid Asset

> Rigid Asset plugin for creating and utilising collections of rigid bodies（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 刚体资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosRigidAssetEditor` (Editor), `ChaosRigidAssetNodes` (Runtime), `ChaosRigidAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidAsset) | |

## 用途

ChaosRigidAsset 插件提供了一套基于 **Dataflow 节点图** 的工作流，用于程序化地创建和编辑物理资产（`UPhysicsAsset`）。传统方式下，物理资产的碰撞体和约束需要在 Physics Asset Editor 中手动逐一配置，而该插件将这一过程完全数据化——通过连接节点来选择骨骼、生成碰撞几何体（Box/Sphere/Capsule/Convex/凸包分解）、自动创建约束，并最终输出完整的物理资产。

核心设计理念是利用 Dataflow 图的**求值不变性**（const evaluation），通过 `TCopyOnWriteArray`（写时复制数组）实现轻量级状态传递，使得整个构建过程可以高效地进行回退、撤销和增量更新。此外，插件还提供了刚体模拟缓存功能，可以直接将物理模拟结果烘焙为动画序列资产。

## 使用场景

- 你的角色有复杂的骨骼结构，需要批量为所有骨骼自动生成碰撞体 → 使用骨骼选择 + 几何体生成器
- 你需要基于骨骼蒙皮网格的顶点数据，自动计算最紧凑的碰撞包络 → 使用 Sphere/Box/Capsule/Convex 生成器
- 你需要为大量骨骼自动创建摆动/扭转约束 → 使用 Swing/Twist 约束生成器
- 你想跳过手动编辑物理资产，直接通过节点图流程化生产 → 使用完整的 Dataflow 图
- 你需要快速预览刚体碰撞效果并导出为动画 → 使用 Rigid Simulation Caching 节点
- 你想在 GPU 实例化动画系统中使用物理模拟结果 → 使用 AnimBankTerminal 节点

## 蓝图用法

> **注意**：本插件的主要交互方式是通过 Dataflow 编辑器中的节点图，而非传统蓝图节点。以下列出的是在 Dataflow 图中可用的核心节点。

### 核心节点

**状态管理**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PhysicsAssetMakeState` | 创建物理资产构建的初始状态，可选输入骨骼网格体 | `FDataflowPhysicsAssetMakeState` |
| `PhysicsAssetTerminal` | 终端节点，将状态转换为最终的 UPhysicsAsset | `FDataflowPhysicsAssetTerminalNode` |
| `New Bone Selection` | 为指定骨架创建一个新的空骨骼选择集 | `FDataflowNewBoneSelection` |

**骨骼选择与操作**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Select Bones by Name` | 按名称模式（支持通配符 `*` 和 `?`）选择骨骼 | `FDataflowSelectBonesByName` |
| `Select Connected Bones` | 选择当前选择集中骨骼的上下游关联骨骼 | `FDataflowSelectConnectedBones` |
| `Append Selected Bones` | 合并两个骨骼选择集 | `FDataflowAppendBoneSelection` |
| `Merge Bones in Selection` | 根据合并策略合并选择集中的小骨骼 | `FDataflowMergeBoneSelection` |

**几何体生成**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Geometry for Bones` | 为选择的骨骼应用几何体生成器，创建碰撞体 | `FDataflowCreateGeometryForBones` |
| `Make Box Bone Geometry Builder` | 创建 Box 类型的骨骼几何体生成器 | `FMakeBoxBoneGeometryGenerator` |
| `Make Sphere Bone Geometry Builder` | 创建 Sphere 类型的骨骼几何体生成器 | `FMakeSphereBoneGeometryGenerator` |
| `Make Capsule Bone Geometry Builder` | 创建 Capsule 类型的骨骼几何体生成器 | `FMakeCapsuleBoneGeometryGenerator` |
| `Make Convex Bone Geometry Builder` | 创建凸包类型的骨骼几何体生成器 | `FMakeConvexBoneGeometryGenerator` |
| `Make Convex Decomposition Bone Geometry Builder` | 创建凸包分解类型的骨骼几何体生成器 | `FMakeConvexDecompBoneGeometryGenerator` |

**约束生成**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Constraints for Bones` | 为骨骼选择集自动创建约束 | `FDataflowAutoConstrainBodies` |
| `Make Swing/Twist Constraint Generator` | 创建摆动/扭转约束生成器 | `FMakeSwingTwistConstraintGenerator` |

**基础形状**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeBox` | 创建一个 Box 形状元素 | `FMakeBoxElemDataflowNode` |
| `MakeSphere` | 创建一个 Sphere 形状元素 | `FMakeSphereElemDataflowNode` |
| `MakeCapsule` | 创建一个 Capsule 形状元素 | `FMakeCapsuleElemDataflowNode` |

**物理操作**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PhysicsAssetAddBody` | 向资产状态中添加一个刚体 | `FDataflowPhysicsAssetAddBody` |
| `Make Body Setup` | 从模板创建一个刚体配置 | `FDataflowMakeBody` |
| `Make Joint` | 从模板创建一个关节配置 | `FDataflowMakeJoint` |
| `Set Body Geometry` | 替换刚体的聚合几何体 | `FDataflowSetBodyGeometry` |
| `AggGeomAddShape` | 向聚合几何体添加形状 | `FDataflowAggGeomAddShape` |

**模拟与动画**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Rigid Simulation Caching` | 运行刚体模拟并烘焙为动画序列 | `FDataflowRigidSimulationCachingNode` |
| `AccelerationAffector` | 为模拟添加恒定加速度（如重力） | `FDataflowSimulationAccelerationAffectorNode` |
| `WindAffector` | 为模拟添加风力效果 | `FDataflowSimulationWindAffectorNode` |
| `AnimSequenceTerminal` | 终端节点，将动画写入 AnimSequence 资产 | `FDataflowAnimSequenceAssetTerminalNode` |
| `AnimBankTerminal` | 终端节点，将多个动画序列写入 AnimBank 资产 | `FDataflowAnimBankAssetTerminalNode` |

### 使用示例（Dataflow 图描述）

**示例 1：自动为角色骨骼生成球形碰撞体**

1. 放置 `PhysicsAssetMakeState` 节点，连接目标骨骼网格体
2. 放置 `New Bone Selection` 节点，指定目标骨架
3. 放置 `Select Bones by Name` 节点，设置搜索模式如 `"*"` 选择所有骨骼
4. 放置 `Make Sphere Bone Geometry Builder` 节点，配置 Sphere 生成器参数
5. 放置 `Create Geometry for Bones` 节点，连接生成器、骨骼选择集和状态
6. 放置 `PhysicsAssetTerminal` 节点，连接最终状态
7. 执行图，物理资产将自动创建

**示例 2：带约束的完整物理资产生成**

1. 按示例 1 的步骤 1-5 创建几何体
2. 放置 `Make Swing/Twist Constraint Generator`，配置摆动/扭转角度限制
3. 放置 `Create Constraints for Bones` 节点，连接约束生成器和状态
4. 连接 `PhysicsAssetTerminal` 输出

**示例 3：物理模拟缓存为动画**

1. 通过上述流程构建物理资产状态
2. 放置 `AccelerationAffector` 节点，设置重力方向和大小
3. 放置 `Rigid Simulation Caching` 节点，连接状态和模拟器，配置持续时间和帧率
4. 放置 `AnimSequenceTerminal`，指定输出动画资产
5. 执行图，模拟结果将被烘焙到动画序列中

## C++ 用法

### 头文件引入

```cpp
#include "BoneSelection.h"
#include "PhysicsAssetDataflowState.h"
#include "BoneGeometryGenerators.h"
#include "ConstraintGenerators.h"
#include "PhysicsAssetBuilder.h"
```

### 基本用法

以下代码展示了如何通过 `FPhysicsAssetBuilder` 以编程方式构建物理资产：

```cpp
// 来源: Private/PhysicsAssetBuilder.h

#include "PhysicsAssetBuilder.h"
#include "BoneSelection.h"

using namespace UE::Chaos::RigidAsset;

// 创建一个骨骼选择集
FRigidAssetBoneSelection Selection;
Selection.Skeleton = MySkeleton;
Selection.Mesh = MySkeletalMesh;

// 选择特定骨骼
FRigidAssetBoneInfo BoneInfo(FName("spine_01"), 0, 0);
Selection.SelectedBones.Add(BoneInfo);

// 使用 Builder 构建物理资产
TObjectPtr<UPhysicsAsset> PhysicsAsset = FPhysicsAssetBuilder::Make(MySkeleton)
    .Body(MyBodySetup)
    .Joint(MyConstraintTemplate)
    .Path(MyDesiredPath)
    .Build();
```

### 进阶用法

以下代码展示了在运行时使用骨骼几何体生成器和物理模拟的组合用法：

```cpp
// 来源: Private/Generators/BoneGeometryGenerators.h

#include "BoneGeometryGenerators.h"
#include "BoneSelection.h"
#include "PhysicsAssetDataflowState.h"

// 配置基础生成设置
FBaseGenerationSettings Settings;
Settings.Operation = EMergeOperation::MergeSmall;
Settings.MinimumBoneSize = 20.0f;  // 厘米
Settings.SmallBoneOp = ESmallBoneOperation::Merge;
Settings.VertexMode = EVertexSelectMode::DominantOnly;
Settings.SourceLod = 0;
Settings.Thickness = 1.0f;

// 对骨骼选择集进行合并处理（小骨骼会根据策略被合并或跳过）
FRigidAssetBoneSelection MergedSelection = MergeSelection(Settings, SortedSelection);

// 使用 Sphere 生成器为合并后的骨骼创建几何体
UBoneGeometryGenerator_Sphere* SphereGenerator = NewObject<UBoneGeometryGenerator_Sphere>();
TArray<FRigidAssetBoneGeometry> Geometries = SphereGenerator->Build(MergedSelection);

// 创建物理资产状态并添加刚体
FPhysicsAssetDataflowState State(MySkeleton, MySkeletalMesh);
for (const FRigidAssetBoneGeometry& Geom : Geometries)
{
    USkeletalBodySetup* Body = State.FindOrCreateBody(Geom.Bone.Name);
    // 将几何体设置到刚体上...
}
```

**凸包分解生成器**的 C++ 配置：

```cpp
// 来源: Private/Generators/BoneGeometryGenerators.h

UBoneGeometryGenerator_ConvexDecomposition* DecompGenerator = NewObject<UBoneGeometryGenerator_ConvexDecomposition>();

// 简单分解模式
DecompGenerator->Method = EDecompositionMethod::Simple;
DecompGenerator->NumHulls = 4;

// 或使用负空间保护模式
DecompGenerator->Method = EDecompositionMethod::NegativeSpace;
DecompGenerator->bOnlyConnectedToHull = true;
DecompGenerator->NegativeSpaceTolerance = 2.0f;
DecompGenerator->NegativeSpaceMinRadius = 10.0f;
DecompGenerator->NegativeSpaceMaxSplits = 0;  // 自动决定

// 可选：简化凸包
DecompGenerator->bSimplifyHulls = true;
DecompGenerator->SimplifyTargetMaxFaces = 128;

TArray<FRigidAssetBoneGeometry> Geometries = DecompGenerator->Build(MyBoneSelection);
```

## Demo 示例

以下是一个完整的最小示例，展示如何自定义一个骨骼几何体生成器并在 Dataflow 图中使用它：

```cpp
// MyBoneGeometryGenerator.h
#pragma once

#include "BoneGeometryGenerators.h"
#include "BoneSelection.h"

UCLASS()
class UMyBoneGeometryGenerator : public UBoneGeometryGenerator
{
    GENERATED_BODY()

public:
    virtual TArray<FRigidAssetBoneGeometry> Build(FRigidAssetBoneSelection Bones) override;

private:
    UPROPERTY(EditAnywhere, Category = "Settings")
    float InflationRadius = 5.0f;
};
```

```cpp
// MyBoneGeometryGenerator.cpp
#include "MyBoneGeometryGenerator.h"
#include "PhysicsAssetDataflowState.h"

TArray<FRigidAssetBoneGeometry> UMyBoneGeometryGenerator::Build(FRigidAssetBoneSelection Bones)
{
    TArray<FRigidAssetBoneGeometry> Results;

    // 遍历骨骼选择集
    for (const FRigidAssetBoneInfo& BoneInfo : Bones.SelectedBones)
    {
        FRigidAssetBoneGeometry Geom;
        Geom.Bone = BoneInfo;

        // 创建一个简单的球形几何体，半径为膨胀半径
        TSharedPtr<FKSphereElem> SphereElem = MakeShared<FKSphereElem>();
        SphereElem->Radius = InflationRadius;
        SphereElem->Center = FVector::ZeroVector;

        Geom.Geometry = UE::Chaos::RigidAsset::FSimpleGeometry(FTransform::Identity, SphereElem);

        Results.Add(MoveTemp(Geom));
    }

    return Results;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | 提供 Dataflow 节点图框架，所有节点的基类和求值系统 |
| `GeometryProcessing` | 几何处理算法，用于凸包分解和网格简化 |
| `PhysicsCore` | 物理核心模块，提供 `FKAggregateGeom`、`FKShapeElem` 等物理几何体类型 |
| `ImmediatePhysics` | 即时物理模拟，用于 `Rigid Simulation Caching` 节点中的运行时模拟 |
| `AnimationCore` | 动画核心模块，用于模拟结果烘焙为动画 |
| `AnimGraph` | 动画图模块，动画终端节点的依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `1a41cebd` | Dataflow : fix Dataflow nodes not properly referencing the node when outputing error messages causing | 修复 Dataflow 节点输出错误消息时引用不正确的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-04-10 | `36646cb9` | Rigid asset - Update rigid asset asset to use the unified dataflow menu command so that the user exp | 统一 Dataflow 菜单命令，改善用户体验 |
| 2026-04-10 | `5c4d7272` | Dataflow : added an API to dataflow attachment to get the preview actor path for the Dataflow Editor | 新增 API 获取 Dataflow 编辑器中的预览 Actor 路径 |
| 2026-04-07 | `b7596b26` | Fixup docs on rigid caching node | 修复刚体缓存节点的文档注释 |

### 维护评价

- **创建时间**：2025 年 8 月，非常年轻的插件
- **更新频率**：最近一个月内有 5 次提交，包括功能改进、Bug 修复和代码质量维护，属于**活跃开发**阶段
- **实验性状态**：标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 和功能可能随时发生变化
- **核心功能完整度**：已实现从骨骼选择到几何体生成、约束创建、物理模拟缓存的完整流程，但生成器类型（如 Convex）标注 "more to follow"，说明仍在扩展中
- **建议**：适合在实验性项目中尝试和评估，不建议用于生产环境。可关注后续版本的 API 稳定化进展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidAsset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidAsset/Tests)