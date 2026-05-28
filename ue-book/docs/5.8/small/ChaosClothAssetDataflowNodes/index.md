# Chaos Cloth Asset Dataflow Nodes

> Dataflow node plugin required to edit a Cloth Asset.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产数据流节点 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Dataflow 节点定义、模拟配置、网格导入、权重图） |
| 模块 | `ChaosClothAssetDataflowNodes` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-12-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetDataflowNodes) | |

## 用途

该插件提供了 Chaos Cloth Asset（布料资产）系统的 **Dataflow 节点**，用于在 Cloth Asset Editor 中通过节点图方式编辑布料模拟属性。它从 ChaosClothAsset 插件中拆分而来，专注于提供所有编辑布料资产所需的 Dataflow 节点。

该插件解决了以下核心问题：

- **模拟物理属性配置**：拉伸、弯曲、气动力、自碰撞、碰撞、速度缩放、远程附着等约束的参数配置
- **网格导入**：从静态网格、骨骼网格、USD 文件导入布料的模拟/渲染网格
- **网格处理**：重网格化（Remesh）、蒙皮权重转移、代理变形器（Proxy Deformer）
- **选择与权重**：权重图（Weight Map）绘制、选择集（Selection）管理、属性创建
- **约束生成**：顶点弹簧、顶点-面弹簧约束的程序化生成
- **终端输出**：将布料集合（Cloth Collection）转换为可运行时使用的 Cloth Asset

该插件默认不启用（`Installed: false`），需要在 ChaosClothAsset 和 Dataflow 插件的配合下使用。

## 使用场景

- 你在使用 Chaos 布料系统制作角色服装 → 用 Cloth Asset Editor 中的 Dataflow 节点图配置布料参数
- 你需要从第三方服装建模软件（如 Marvelous Designer）导入 USD 布料数据 → 用 USD Import 节点
- 你需要控制布料在不同区域的物理行为（如袖口更硬、裙摆更软）→ 用 Weight Map + 各模拟配置节点
- 你需要将骨骼网格的蒙皮权重转移到布料模拟网格 → 用 TransferSkinWeights 节点
- 你需要精细控制渲染网格与模拟网格的对应关系 → 用 Proxy Deformer + Selection 节点
- 你需要重网格化布料表面以优化模拟性能 → 用 Remesh 节点

## 蓝图用法

> **注意**：该插件的所有节点都是 **Dataflow 节点**（`USTRUCT` + `FDataflowNode`），不是传统的蓝图可调用函数。它们在 Cloth Asset Editor 的 Dataflow 图编辑器中使用，而非蓝图编辑器。

### 核心节点一览

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SkeletalMeshImport` | 从骨骼网格导入布料模拟/渲染网格 | `FChaosClothAssetSkeletalMeshImportNode_v2` |
| `StaticMeshImport` | 从静态网格导入布料模拟/渲染网格 | `FChaosClothAssetStaticMeshImportNode_v2` |
| `USDImport` | 从 USD 文件导入布料数据 | `FChaosClothAssetUSDImportNode_v3` |
| `TransferSkinWeights` | 将骨骼网格的蒙皮权重转移到布料网格 | `FChaosClothAssetTransferSkinWeightsNode` |
| `Remesh` | 重网格化布料表面以控制分辨率 | `FChaosClothAssetRemeshNode_v2` |
| `ProxyDeformer` | 设置渲染网格到模拟网格的代理变形关系 | `FChaosClothAssetProxyDeformerNode_v3` |
| `WeightMap` | 创建/编辑权重图属性 | `FChaosClothAssetWeightMapNode` |
| `Selection` | 创建/编辑选择集 | `FChaosClothAssetSelectionNode_v2` |
| `Attribute` | 创建新的自定义属性 | `FChaosClothAssetAttributeNode_v2` |
| `ClothAssetTerminal` | 终端节点，将布料集合输出为 Cloth Asset | `FChaosClothAssetTerminalNode_v2` |
| `ClothCollectionToDynamicMesh` | 将布料集合转换为动态网格 | `FChaosClothAssetCollectionToDynamicMeshNode` |

**模拟配置节点**（均继承自 `FChaosClothAssetSimulationBaseConfigNode`）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SimulationAerodynamicsConfig` | 风力/空气动力学参数 | `FChaosClothAssetSimulationAerodynamicsConfigNode` |
| `SimulationBendingConfig` | 弯曲约束参数 | `FChaosClothAssetSimulationBendingConfigNode` |
| `SimulationStretchConfig` | 拉伸约束参数 | `FChaosClothAssetSimulationStretchConfigNode` |
| `SimulationCollisionConfig` | 碰撞参数（碰撞体交互） | `FChaosClothAssetSimulationCollisionConfigNode` |
| `SimulationSelfCollisionConfig` | 自碰撞参数 | `FChaosClothAssetSimulationSelfCollisionConfigNode_v2` |
| `SimulationLongRangeAttachmentConfig` | 远程附着约束参数 | `FChaosClothAssetSimulationLongRangeAttachmentConfigNode_v2` |
| `SimulationVelocityScaleConfig` | 速度缩放参数 | `FChaosClothAssetSimulationVelocityScaleConfigNode` |
| `SimulationBendingOverrideConfig` | 弯曲约束覆盖参数 | `FChaosClothAssetSimulationBendingOverrideConfigNode` |
| `SimulationStretchOverrideConfig` | 拉伸约束覆盖参数 | `FChaosClothAssetSimulationStretchOverrideConfigNode` |
| `SimulationClothVertexSpringConfig` | 顶点-顶点弹簧约束 | `FChaosClothAssetSimulationClothVertexSpringConfigNode` |
| `SimulationClothVertexFaceSpringConfig` | 顶点-面弹簧约束 | `FChaosClothAssetSimulationClothVertexFaceSpringConfigNode` |

### 典型 Dataflow 图结构

一个基本的布料资产 Dataflow 图通常按以下顺序连接：

1. **导入节点**（SkeletalMeshImport / StaticMeshImport）→ 输出 `Collection`
2. **WeightMap 节点** → 定义区域权重（如 MaxDistance 权重图）
3. **Selection 节点** → 定义特定区域选择集
4. **模拟配置节点链**（StretchConfig → BendingConfig → AerodynamicsConfig → ...）→ 串联 `Collection`
5. **Remesh 节点**（可选）→ 调整网格分辨率
6. **ProxyDeformer 节点**（可选）→ 设置代理变形
7. **TransferSkinWeights 节点**（可选）→ 转移蒙皮权重
8. **Terminal 节点** → 输出最终 Cloth Asset

所有模拟配置节点通过 `Collection` 的 passthrough 连接串联，每个节点向 `Collection` 写入自己的属性。

## C++ 用法

### 头文件引入

```cpp
// 基础配置节点（如需自定义模拟配置节点）
#include "ChaosClothAsset/SimulationBaseConfigNode.h"

// 特定配置节点
#include "ChaosClothAsset/SimulationStretchConfigNode.h"
#include "ChaosClothAsset/SimulationBendingConfigNode.h"
#include "ChaosClothAsset/SimulationAerodynamicsConfigNode.h"

// 导入/工具节点
#include "ChaosClothAsset/SkeletalMeshImportNode.h"
#include "ChaosClothAsset/RemeshNode.h"
#include "ChaosClothAsset/ProxyDeformerNode.h"
#include "ChaosClothAsset/TransferSkinWeightsNode.h"

// 权重/选择/终端
#include "ChaosClothAsset/WeightMapNode.h"
#include "ChaosClothAsset/SelectionNode.h"
#include "ChaosClothAsset/TerminalNode.h"

// 权重值类型
#include "ChaosClothAsset/WeightedValue.h"
```

### 基本用法：自定义模拟配置节点

最核心的扩展点是继承 `FChaosClothAssetSimulationBaseConfigNode` 来创建自定义模拟配置节点：

```cpp
// 来源：SimulationBaseConfigNode.h - 演示如何继承基础配置节点

#include "ChaosClothAsset/SimulationBaseConfigNode.h"

// 自定义配置节点：必须标记为 DataflowCloth 以在 Cloth Asset Editor 中可见
USTRUCT(Meta = (DataflowCloth))
struct FMyCustomClothConfigNode : public FChaosClothAssetSimulationBaseConfigNode
{
    GENERATED_USTRUCT_BODY()
    // 定义节点名称、分类和描述
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomClothConfigNode, "MyCustomConfig", "Cloth", "My Custom Cloth Config")

public:
    // 自定义属性：使用 FChaosClothAssetWeightedValue 实现带权重图的参数
    // WeightedValue 支持 Low/High 范围 + 权重图名称，运行时按每粒子权重插值
    UPROPERTY(EditAnywhere, Category = "Custom Properties",
        Meta = (UIMin = "0", UIMax = "1000", ClampMin = "0", ClampMax = "10000000",
                InteractorName = "CustomStiffness"))
    FChaosClothAssetWeightedValue CustomStiffness = {
        true,       // bIsAnimatable - 是否支持实时动画
        100.f,      // Low - 权重为 0 时的值
        100.f,      // High - 权重为 1 时的值
        TEXT("CustomStiffness"),  // 权重图名称
        true        // bCouldUseFabrics - 是否支持从 USD fabric 导入
    };

    // 布尔属性
    UPROPERTY(EditAnywhere, Category = "Custom Properties",
        Meta = (InteractorName = "bUseCustomFeature"))
    bool bUseCustomFeature = true;

    FMyCustomClothConfigNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FChaosClothAssetSimulationBaseConfigNode(InParam, InGuid)
    {
    }

private:
    // 核心方法：通过 PropertyHelper 将属性写入布料集合
    // 这是配置节点必须实现的方法
    virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
    {
        // 设置权重值属性
        PropertyHelper.SetPropertyWeighted(
            this,               // this 指针用于自动查找 UPROPERTY 名称
            &CustomStiffness,   // 属性指针
            {},                 // SimilarPropertyNames - 同义属性名列表
            ECollectionPropertyFlags::Animatable  // 属性标志
        );

        // 设置布尔属性
        PropertyHelper.SetPropertyBool(
            this,
            &bUseCustomFeature,
            {},
            ECollectionPropertyFlags::Animatable
        );
    }
};
```

### 进阶用法：理解 PropertyHelper 内部机制

`FPropertyHelper` 是基础配置节点中用于将属性安全写入布料集合的核心工具类。以下演示其完整 API：

```cpp
// 来源：SimulationBaseConfigNode.h - PropertyHelper 各种属性设置方法

virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
{
    // === 基本类型设置 ===
    
    // 通过名称设置浮点属性
    PropertyHelper.SetProperty<float>(TEXT("SomeProperty"), 42.0f, {}, ECollectionPropertyFlags::Animatable);
    
    // 通过名称 + 字符串值设置属性（支持字符串显示）
    PropertyHelper.SetPropertyAndString<float>(TEXT("SomeProperty"), 42.0f, TEXT("42.0"));

    // 通过结构体指针自动推断属性名称（推荐方式）
    PropertyHelper.SetProperty(this, &MyFloatProperty);

    // === 布尔属性 ===
    PropertyHelper.SetPropertyBool(TEXT("UseFeature"), true);  // 注意：名称不含 'b' 前缀
    PropertyHelper.SetPropertyBool(this, &bMyBool);  // 自动去除 'b' 前缀

    // === 枚举属性 ===
    PropertyHelper.SetPropertyEnum(TEXT("ConstraintType"), EMyConstraintType::HingeAngles);
    PropertyHelper.SetPropertyEnum(this, &MyEnumProperty);

    // === 字符串属性 ===
    PropertyHelper.SetPropertyString(TEXT("MapName"), TEXT("MyWeightMap"));
    PropertyHelper.SetPropertyString(this, &MyStringProperty);

    // === 加权值属性（支持权重图） ===
    // 基本加权值
    PropertyHelper.SetPropertyWeighted(TEXT("Stiffness"), FChaosClothAssetWeightedValue{true, 100.f, 100.f, TEXT("StiffnessMap")});
    // 非动画加权值
    PropertyHelper.SetPropertyWeighted(TEXT("RestAngle"), FChaosClothAssetWeightedValueNonAnimatable{0.f, 0.f, TEXT("RestAngleMap")});

    // === 从 Fabric 导入的属性 ===
    // 设置从 Fabric（USD 导入的面料数据）导入的属性
    PropertyHelper.SetFabricProperty(
        TEXT("CollisionThickness"),
        CollisionThicknessImported,
        [](UE::Chaos::ClothAsset::FCollectionClothFabricFacade& FabricFacade) -> float
        {
            return FabricFacade.GetCollisionThickness();
        },
        {}
    );

    // 从 Solver（模拟器配置）导入的属性
    PropertyHelper.SetSolverProperty(
        TEXT("SolverProperty"),
        SolverPropertyValue,
        [](UE::Chaos::ClothAsset::FCollectionClothFacade& ClothFacade) -> float
        {
            return ClothFacade.GetSolverValue();
        },
        {}
    );

    // === 覆盖其他节点的属性 ===
    // 覆盖布尔属性
    PropertyHelper.OverridePropertiesBool({TEXT("Property1"), TEXT("Property2")}, true);
    
    // 覆盖浮点属性
    PropertyHelper.OverridePropertiesFloat(
        {TEXT("Stiffness")},
        EChaosClothAssetConstraintOverrideType::Multiply,
        0.5f
    );
    
    // 覆盖加权值属性
    PropertyHelper.OverridePropertiesWeighted(
        {TEXT("StretchStiffness")},
        EChaosClothAssetConstraintOverrideType::Add,
        FChaosClothAssetWeightedValueOverride{10.f, 10.f}
    );
}
```

### 进阶用法：重写 Evaluate 以扩展节点行为

```cpp
// 来源：SimulationBaseConfigNode.h - 钩子方法

// 在 AddProperties 被调用之后，可以对布料集合执行额外操作
virtual void EvaluateClothCollection(UE::Dataflow::FContext& Context,
    const TSharedRef<FManagedArrayCollection>& ClothCollection) const override
{
    // 在这里可以对布料集合执行节点特定的后处理
    // 例如：创建约束、修改拓扑、生成附加数据等
    
    // 获取布料 Facade 进行操作
    UE::Chaos::ClothAsset::FCollectionClothFacade ClothFacade(ClothCollection);
    // ... 执行自定义逻辑
}
```

## Demo 示例

以下是一个完整的自定义模拟配置节点示例，创建一个控制布料"弹性"的简单节点：

```cpp
// MyClothElasticityConfigNode.h
#pragma once

#include "ChaosClothAsset/SimulationBaseConfigNode.h"
#include "ChaosClothAsset/WeightedValue.h"
#include "MyClothElasticityConfigNode.generated.h"

USTRUCT(Meta = (DataflowCloth))
struct FMyClothElasticityConfigNode final : public FChaosClothAssetSimulationBaseConfigNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyClothElasticityConfigNode,
        "MyElasticityConfig", "Cloth", "Cloth Elasticity Config")

public:
    FMyClothElasticityConfigNode(
        const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

    /** 弹性刚度，可通过权重图在不同区域设置不同值 */
    UPROPERTY(EditAnywhere, Category = "Elasticity",
        Meta = (UIMin = "0", UIMax = "10000", ClampMin = "0", ClampMax = "10000000",
                InteractorName = "ElasticityStiffness"))
    FChaosClothAssetWeightedValue ElasticityStiffness = {
        true, 100.f, 100.f, TEXT("ElasticityStiffness") };

    /** 阻尼比，相对于临界阻尼 */
    UPROPERTY(EditAnywhere, Category = "Elasticity",
        Meta = (UIMin = "0", UIMax = "1", ClampMin = "0", ClampMax = "1000",
                InteractorName = "ElasticityDamping"))
    FChaosClothAssetWeightedValue ElasticityDamping = {
        true, 0.1f, 0.1f, TEXT("ElasticityDamping") };

private:
    virtual void AddProperties(FPropertyHelper& PropertyHelper) const override;
};
```

```cpp
// MyClothElasticityConfigNode.cpp
#include "MyClothElasticityConfigNode.h"

FMyClothElasticityConfigNode::FMyClothElasticityConfigNode(
    const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FChaosClothAssetSimulationBaseConfigNode(InParam, InGuid)
{
}

void FMyClothElasticityConfigNode::AddProperties(FPropertyHelper& PropertyHelper) const
{
    // 将弹性刚度写入布料集合的属性中
    // this 指针使 PropertyHelper 能自动从 UPROPERTY 定义获取属性名
    PropertyHelper.SetPropertyWeighted(this, &ElasticityStiffness);
    PropertyHelper.SetPropertyWeighted(this, &ElasticityDamping);
}
```

## 模块依赖

该插件的依赖信息来自 `.uplugin` 的 `Plugins` 字段：

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料运行时模拟核心 |
| `ChaosClothAsset` | 布料资产数据结构（ClothCollection、Facade 等） |
| `Dataflow` | Dataflow 节点图框架 |
| `GeometryProcessing` | 几何处理（重网格化、蒙皮权重转移等） |
| `MeshResizing` | 网格缩放/调整 |

无特殊运行时模块依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-18 | `d4c2bb83` | Fix crash happening when regenerating or visualizing vertex and vertex face springs after the sim mesh | 修复重新生成或可视化顶点弹簧后崩溃的问题 |
| 2026-05-14 | `e9598355` | Chaos Cloth Asset toolset and updated converter from legacy SKM cloth to Chaos Cloth Asset | 更新布料工具集和旧版 SKM 布料到 Chaos Cloth Asset 的转换器 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode | 修复严格浮点模式下 double 截断为 float 的警告 |
| 2026-05-12 | `7639ea3a` | Cloth weightmap node - add transfer from render mesh option | 权重图节点新增从渲染网格转移选项 |

### 维护评价

- **活跃维护**：最近 1 周内有多次实质性更新（bug 修复、功能增强）
- **创建时间**：2025-12-05，约 6 个月前，属于较新的插件
- **代码质量**：从 ChaosClothAsset 插件拆分而来，继承了成熟的代码基础；源码中有大量已废弃（Deprecated）节点的版本迭代记录，说明 API 在持续演进
- **实验性功能**：部分节点标记为 `Experimental`（如 BendingOverrideConfig、VertexSpringConfig、VertexFaceSpringConfig、DynamicMesh 转换节点等），这些功能可能在后续版本中有变动
- **已知限制**：该插件仅支持 Win64、Mac、Linux 平台；需配合 ChaosClothAsset 和 Dataflow 插件使用
- **推荐使用**：✅ 强烈推荐 — 这是 Chaos 布料系统编辑 Cloth Asset 的唯一官方 Dataflow 节点插件，处于活跃开发中，bug 修复及时

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetDataflowNodes)
- [ChaosClothAsset 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) — 布料资产核心模块
- [ChaosCloth 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) — 布料运行时模拟
- [Dataflow 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow) — Dataflow 节点图框架
- [GeometryProcessing 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/GeometryProcessing) — 几何处理