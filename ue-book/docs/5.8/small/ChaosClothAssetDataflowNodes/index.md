# Chaos Cloth Asset Dataflow Nodes

> Dataflow node plugin required to edit a Cloth Asset.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产数据流节点 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流节点定义） |
| 模块 | `ChaosClothAssetDataflowNodes` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-12-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetDataflowNodes) | |

## 用途

本插件为 Chaos 布料资产（Cloth Asset）的编辑提供了一整套 **Dataflow 节点**。它是 ChaosClothAsset 布料系统在编辑器中的**可视化节点图工作流**的核心组件，通过 Dataflow 框架将布料的导入、网格处理、模拟参数配置、权重图绘制、选择集管理、代理变形器设置等操作全部封装为可连接的节点。

该插件从 ChaosClothAsset 中独立出来（原为 USD Dataflow 节点的一部分），专门负责所有与 Cloth Asset 编辑相关的 Dataflow 节点实现。它解决的核心问题是：**让用户通过可视化的节点图方式来构建和配置布料资产的完整工作流**，而不需要编写代码。

## 使用场景

- 你在做角色服装的布料模拟 → 使用 SkeletalMeshImport 节点导入骨骼网格，配置 Stretch/Bending/SelfCollision 等模拟参数
- 你需要从 USD 文件导入第三方服装软件（如 CLO3D、Marvelous Designer）的布料数据 → 使用 USDImport 节点
- 你需要对布料网格进行重新拓扑或简化 → 使用 Remesh 节点调整仿真网格和渲染网格的分辨率
- 你需要精确控制布料哪些区域受模拟驱动 vs 受蒙皮驱动 → 使用 ProxyDeformer 节点配合 Selection 节点
- 你需要将骨骼网格的蒙皮权重转移到布料网格上 → 使用 TransferSkinWeights 节点
- 你需要绘制或调整布料的权重图 → 使用 WeightMap 节点
- 你需要为布料创建自定义的弹簧约束或顶点-面约束 → 使用 ClothVertexSpring/ClothVertexFaceSpring 节点

## 蓝图用法

本插件的节点主要通过 Dataflow 编辑器的节点图界面使用，而非传统蓝图。以下是核心节点分类：

### 导入节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SkeletalMeshImport` | 从骨骼网格资产导入仿真/渲染网格 | `FChaosClothAssetSkeletalMeshImportNode_v2` |
| `StaticMeshImport` | 从静态网格资产导入仿真/渲染网格 | `FChaosClothAssetStaticMeshImportNode_v2` |
| `USDImport` | 从 USD 文件导入布料数据（已废弃） | `FChaosClothAssetUSDImportNode_v2` |

### 网格处理节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Remesh` | 对仿真/渲染网格进行重拓扑或简化 | `FChaosClothAssetRemeshNode_v2` |
| `TransferSkinWeights` | 从骨骼网格转移蒙皮权重到布料网格 | `FChaosClothAssetTransferSkinWeightsNode` |
| `ClothCollectionToDynamicMesh` | 将布料集合转换为动态网格（实验性） | `FChaosClothAssetCollectionToDynamicMeshNode` |
| `UpdateClothFromDynamicMesh` | 从动态网格更新布料集合属性（实验性） | `FChaosClothAssetUpdateClothFromDynamicMeshNode` |

### 模拟参数配置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SimulationStretchConfig` | 配置拉伸约束属性 | `FChaosClothAssetSimulationStretchConfigNode` |
| `SimulationBendingConfig` | 配置弯曲约束属性 | `FChaosClothAssetSimulationBendingConfigNode` |
| `SimulationAerodynamicsConfig` | 配置空气动力学属性（风、阻力、升力） | `FChaosClothAssetSimulationAerodynamicsConfigNode` |
| `SimulationSelfCollisionConfig` | 配置自碰撞属性 | `FChaosClothAssetSimulationSelfCollisionConfigNode_v2` |
| `SimulationCollisionConfig` | 配置碰撞属性（与物理资产交互） | `FChaosClothAssetSimulationCollisionConfigNode` |
| `SimulationLongRangeAttachmentConfig` | 配置长距离附着约束 | `FChaosClothAssetSimulationLongRangeAttachmentConfigNode_v2` |
| `SimulationVelocityScaleConfig` | 配置速度缩放属性 | `FChaosClothAssetSimulationVelocityScaleConfigNode` |

### 参数覆盖节点（实验性）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SimulationStretchOverrideConfig` | 覆盖拉伸约束参数 | `FChaosClothAssetSimulationStretchOverrideConfigNode` |
| `SimulationBendingOverrideConfig` | 覆盖弯曲约束参数 | `FChaosClothAssetSimulationBendingOverrideConfigNode` |

### 约束创建节点（实验性）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SimulationClothVertexSpringConfig` | 创建顶点-顶点弹簧约束 | `FChaosClothAssetSimulationClothVertexSpringConfigNode` |
| `SimulationClothVertexFaceSpringConfig` | 创建顶点-面弹簧约束 | `FChaosClothAssetSimulationClothVertexFaceSpringConfigNode` |

### 选择与权重图节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Selection` | 创建/编辑顶点选择集 | `FChaosClothAssetSelectionNode_v2` |
| `WeightMap` | 创建/编辑权重图 | `FChaosClothAssetWeightMapNode` |
| `Attribute` | 创建自定义属性（实验性） | `FChaosClothAssetAttributeNode_v2` |

### 变形器与终端节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ProxyDeformer` | 配置代理变形器数据 | `FChaosClothAssetProxyDeformerNode_v3` |
| `ClothAssetTerminal` | 将布料集合生成最终布料资产 | `FChaosClothAssetTerminalNode_v2` |

### 使用示例（节点图描述）

一个典型的布料资产构建流程：

1. **SkeletalMeshImport** 节点：连接一个 USkeletalMesh 资产输入，输出 ClothCollection
2. 连接到 **SimulationStretchConfig** 节点：配置拉伸刚度（如 StretchStiffness 设为 1.0）
3. 连接到 **SimulationBendingConfig** 节点：配置弯曲刚度
4. 连接到 **SimulationAerodynamicsConfig** 节点：配置风速和阻力系数
5. 连接到 **SimulationSelfCollisionConfig** 节点：启用自碰撞
6. 连接到 **ClothAssetTerminal** 节点：生成最终的 ClothAsset

所有配置节点均继承自 `FChaosClothAssetSimulationBaseConfigNode`，通过 `Collection` 输入/输出的 Passthrough 模式串行连接。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/SimulationBaseConfigNode.h"
#include "ChaosClothAsset/SimulationStretchConfigNode.h"
#include "ChaosClothAsset/SimulationBendingConfigNode.h"
#include "ChaosClothAsset/WeightedValue.h"
#include "ChaosClothAsset/SelectionNode.h"
#include "ChaosClothAsset/WeightMapNode.h"
```

### 基本用法 — 创建自定义模拟配置节点

从 `SimulationBaseConfigNode.h` 中可以看到，所有模拟配置节点都继承自 `FChaosClothAssetSimulationBaseConfigNode`。创建自定义配置节点需要重写 `AddProperties` 方法：

```cpp
// 头文件: MyCustomConfigNode.h
#pragma once
#include "ChaosClothAsset/SimulationBaseConfigNode.h"
#include "ChaosClothAsset/WeightedValue.h"
#include "MyCustomConfigNode.generated.h"

USTRUCT(Meta = (DataflowCloth))
struct FMyCustomConfigNode : public FChaosClothAssetSimulationBaseConfigNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomConfigNode, "MyCustomConfig", "Cloth", "My Custom Config")

public:
    FMyCustomConfigNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FChaosClothAssetSimulationBaseConfigNode(InParam, InGuid)
    {
        // 必须调用此方法注册 Collection 连接
        RegisterCollectionConnections();
    }

    /** 自定义拉伸刚度，支持权重图插值 */
    UPROPERTY(EditAnywhere, Category = "Custom Properties",
        Meta = (UIMin = "0", UIMax = "10000", ClampMin = "0", ClampMax = "10000000"))
    FChaosClothAssetWeightedValue CustomStiffness = { true, 1.f, 1.f, TEXT("CustomStiffness") };

    /** 自定义阻尼 */
    UPROPERTY(EditAnywhere, Category = "Custom Properties",
        Meta = (UIMin = "0", UIMax = "10", ClampMin = "0", ClampMax = "1000"))
    FChaosClothAssetWeightedValue CustomDamping = { true, 0.1f, 0.1f, TEXT("CustomDamping") };

private:
    virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
    {
        // 使用 PropertyHelper 设置带权重图的属性
        PropertyHelper.SetProperty(this, &CustomStiffness);
        PropertyHelper.SetProperty(this, &CustomDamping);
    }
};
```

### 进阶用法 — 使用 FPropertyHelper 管理属性

从 `SimulationBaseConfigNode.h` 中 `FPropertyHelper` 的定义可以看到，它提供了丰富的属性设置方法：

```cpp
// 在 AddProperties 中使用各种 PropertyHelper 方法

virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
{
    // 1. 设置浮点属性（带权重图插值）
    PropertyHelper.SetProperty(TEXT("Stiffness"), SomeWeightedValue);

    // 2. 设置布尔属性
    PropertyHelper.SetPropertyBool(TEXT("UseFeature"), bSomeFeature);

    // 3. 设置枚举属性
    PropertyHelper.SetPropertyEnum(TEXT("Method"), SomeMethodEnum);

    // 4. 设置字符串属性
    PropertyHelper.SetPropertyString(TEXT("MapName"), SomeStringValue);

    // 5. 设置带权重的属性（Low/High 范围 + 权重图）
    PropertyHelper.SetPropertyWeighted(TEXT("WeightedProp"), SomeWeightedValue);

    // 6. 通过成员变量指针设置属性（自动推导属性名）
    PropertyHelper.SetProperty(this, &MyStiffness);
    PropertyHelper.SetPropertyBool(this, &bMyBool);
    PropertyHelper.SetPropertyEnum(this, &MyEnum);

    // 7. 设置从 solver 导入的值
    PropertyHelper.SetSolverProperty(
        TEXT("SolverProp"),
        PropertyValue,
        [](FCollectionClothFacade& Facade) { return Facade.GetSomeValue(); },
        {}
    );

    // 8. 设置从 fabric 导入的值
    PropertyHelper.SetFabricProperty(
        TEXT("FabricProp"),
        PropertyValue,
        [](FCollectionClothFabricFacade& Facade) { return Facade.GetSomeFabricValue(); },
        {}
    );
}
```

## Demo 示例

以下是一个完整的自定义布料模拟配置节点示例：

**MyGravityConfigNode.h**

```cpp
#pragma once

#include "ChaosClothAsset/SimulationBaseConfigNode.h"
#include "ChaosClothAsset/WeightedValue.h"
#include "MyGravityConfigNode.generated.h"

/**
 * 自定义重力缩放配置节点，用于在特定区域控制重力的影响。
 */
USTRUCT(Meta = (DataflowCloth))
struct FMyGravityConfigNode : public FChaosClothAssetSimulationBaseConfigNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyGravityConfigNode, "MyGravityConfig", "Cloth", "Custom Gravity Config")

public:
    FMyGravityConfigNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

    /** 重力缩放系数，0 表示无重力，1 表示完全重力 */
    UPROPERTY(EditAnywhere, Category = "Gravity",
        Meta = (UIMin = "0", UIMax = "2", ClampMin = "0", ClampMax = "10"))
    FChaosClothAssetWeightedValue GravityScale = { true, 1.f, 1.f, TEXT("GravityScale") };

    /** 是否启用自定义重力方向 */
    UPROPERTY(EditAnywhere, Category = "Gravity")
    bool bUseCustomGravityDirection = false;

    /** 自定义重力方向（单位向量） */
    UPROPERTY(EditAnywhere, Category = "Gravity",
        Meta = (EditCondition = "bUseCustomGravityDirection"))
    FVector3f CustomGravityDirection = FVector3f(0.f, 0.f, -1.f);

private:
    virtual void AddProperties(FPropertyHelper& PropertyHelper) const override;
};
```

**MyGravityConfigNode.cpp**

```cpp
#include "MyGravityConfigNode.h"

FMyGravityConfigNode::FMyGravityConfigNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FChaosClothAssetSimulationBaseConfigNode(InParam, InGuid)
{
    // 注册 Collection 输入/输出连接
    RegisterCollectionConnections();
}

void FMyGravityConfigNode::AddProperties(FPropertyHelper& PropertyHelper) const
{
    // 设置重力缩放属性（带权重图插值）
    PropertyHelper.SetProperty(this, &GravityScale);

    // 设置布尔属性
    PropertyHelper.SetPropertyBool(this, &bUseCustomGravityDirection);

    // 设置向量属性
    if (bUseCustomGravityDirection)
    {
        PropertyHelper.SetProperty(
            TEXT("CustomGravityDirection"),
            CustomGravityDirection,
            {},
            ECollectionPropertyFlags::Animatable
        );
    }
}
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段提取：

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料物理模拟核心 |
| `ChaosClothAsset` | 布料资产数据结构和 Facade 接口 |
| `Dataflow` | Dataflow 节点图框架 |
| `GeometryProcessing` | 几何处理工具（重拓扑、网格操作） |
| `MeshResizing` | 网格尺寸调整 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-18 | `d4c2bb83` | Fix crash happening when regenerating or visualizing vertex and vertex face springs after the sim me | 修复仿真网格修改后重新生成/可视化顶点弹簧时的崩溃问题 |
| 2026-05-14 | `e9598355` | Chaos Cloth Asset toolset and updated converter from legacy SKM cloth to Chaos Cloth Asset. | 布料资产工具集更新，改进从旧版 SKM 布料到 Chaos 布料资产的转换器 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-12 | `7639ea3a` | Cloth weightmap node - add tranmsfer from render mesh option (on behalf of Tim Brakensiek) | 权重图节点新增从渲染网格转移的选项 |

### 维护评价

- **创建时间**：2025-12-05，非常新的插件
- **版本**：0.1，处于早期开发阶段
- **近期更新频率**：2026 年 5 月密集更新，非常活跃
- **维护状态**：**活跃维护中**。作为 Chaos 布料系统的核心编辑器组件，由 Epic Games 持续开发
- **已知限制**：
  - 大量节点标注为 `Deprecated`（v2/v3 版本迭代频繁），升级时需注意节点版本兼容
  - 部分功能标记为 `Experimental`（如 BendingOverride、StretchOverride、VertexSpring、VertexFaceSpring、Attribute、CollectionToDynamicMesh 等），可能在后续版本变更 API
  - 仅支持 Win64、Mac、Linux 平台
  - 版本号 0.1，API 稳定性不能保证
- **推荐使用**：✅ 推荐。这是 Chaos 布料资产工作流的必备插件，是 Epic 官方维护的布料编辑工具链的核心部分。虽然 API 还在快速迭代，但作为编辑器工具使用是稳定可靠的

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetDataflowNodes)
- 官方文档：无（.uplugin 中 DocsURL 为空）