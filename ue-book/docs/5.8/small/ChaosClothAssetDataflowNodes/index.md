# Chaos Cloth Asset Dataflow Nodes

> Dataflow node plugin required to edit a Cloth Asset.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产数据流节点 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosClothAssetDataflowNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-12-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetDataflowNodes) | |

## 用途

该插件为 Chaos 布料资产系统提供了一整套 **Dataflow 节点**，用于在 Dataflow 图中构建、配置和编辑布料资产。它解决了 Chaos 布料模拟中需要通过可视化数据流图来完成的所有资产创建工作流程，包括：

- **网格导入**：从 Skeletal Mesh 或 Static Mesh 导入模拟/渲染网格
- **模拟配置**：配置拉伸、弯曲、气动、碰撞、自碰撞、速度缩放等物理参数
- **网格操作**：重拓扑（Remesh）、代理变形（Proxy Deformer）、蒙皮权重转移
- **选择与权重图**：管理顶点选择集和权重图的绘制与传输
- **USD 导入**：从第三方服装构造软件（如 CLO、Marvelous Designer）的 USD 文件导入布料数据
- **资产终端**：将布料集合输出为可用的布料资产

该插件从 `ChaosClothAsset` 插件中拆分出来，专门负责 Dataflow 节点的定义，使得布料资产编辑的可视化工作流模块化。

## 使用场景

- 你在使用 Chaos 布料系统为角色制作衣服 → 用此插件中的 Dataflow 节点构建布料资产
- 你需要从 CLO/Marvelous Designer 导入 USD 格式的布料模型 → 用 USDImport 节点
- 你需要为布料模拟调整弯曲、拉伸、空气阻力等物理参数 → 用对应的 SimulationXxxConfig 节点
- 你需要将骨骼网格的蒙皮权重转移到布料网格 → 用 TransferSkinWeights 节点
- 你需要对布料网格进行重拓扑以优化模拟性能 → 用 Remesh 节点
- 你需要在布料上绘制选择集或权重图 → 用 Selection/WeightMap 节点

## 蓝图用法

本插件主要通过 **Dataflow 编辑器**使用，而非传统蓝图。所有节点均为 `USTRUCT` 且标注了 `DataflowCloth` 元数据，在 Dataflow 图编辑器中可用。

### 核心数据流节点

#### 网格导入节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SkeletalMeshImport` | 从骨骼网格导入模拟/渲染网格 | `FChaosClothAssetSkeletalMeshImportNode_v2` |
| `StaticMeshImport` | 从静态网格导入模拟/渲染网格 | `FChaosClothAssetStaticMeshImportNode_v2` |
| `USDImport` | 从 USD 文件导入布料数据 | `FChaosClothAssetUSDImportNode_v2` |

#### 模拟配置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SimulationStretchConfig` | 配置拉伸约束（各向同性/各向异性） | `FChaosClothAssetSimulationStretchConfigNode` |
| `SimulationBendingConfig` | 配置弯曲约束（铰链角/弯曲元素） | `FChaosClothAssetSimulationBendingConfigNode` |
| `SimulationAerodynamicsConfig` | 配置气动力学（风、阻力、升力、水体交互） | `FChaosClothAssetSimulationAerodynamicsConfigNode` |
| `SimulationCollisionConfig` | 配置碰撞属性（碰撞厚度、摩擦系数、CCD） | `FChaosClothAssetSimulationCollisionConfigNode` |
| `SimulationSelfCollisionConfig` | 配置自碰撞（点面排斥力、交集解析） | `FChaosClothAssetSimulationSelfCollisionConfigNode_v2` |
| `SimulationLongRangeAttachmentConfig` | 配置长程附着约束（系绳刚度、测地距离） | `FChaosClothAssetSimulationLongRangeAttachmentConfigNode_v2` |
| `SimulationVelocityScaleConfig` | 配置速度缩放（线性/角速度、假想力模型） | `FChaosClothAssetSimulationVelocityScaleConfigNode` |

#### 实验性模拟配置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SimulationBendingOverrideConfig` | 覆盖弯曲约束参数 | `FChaosClothAssetSimulationBendingOverrideConfigNode` |
| `SimulationStretchOverrideConfig` | 覆盖拉伸约束参数 | `FChaosClothAssetSimulationStretchOverrideConfigNode` |
| `SimulationClothVertexFaceSpringConfig` | 顶点-面弹簧约束 | `FChaosClothAssetSimulationClothVertexFaceSpringConfigNode` |
| `SimulationClothVertexSpringConfig` | 顶点-顶点弹簧约束 | `FChaosClothAssetSimulationClothVertexSpringConfigNode` |

#### 网格操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Remesh` | 重拓扑布料网格 | `FChaosClothAssetRemeshNode_v2` |
| `ProxyDeformer` | 配置代理变形器（蒙皮/变形过渡） | `FChaosClothAssetProxyDeformerNode_v3` |
| `TransferSkinWeights` | 将蒙皮权重从骨骼网格转移到布料 | `FChaosClothAssetTransferSkinWeightsNode` |

#### 选择与权重图节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Selection` | 管理顶点选择集 | `FChaosClothAssetSelectionNode_v2` |
| `WeightMap` | 管理权重图属性 | `FChaosClothAssetWeightMapNode` |
| `Attribute` | 创建自定义属性 | `FChaosClothAssetAttributeNode_v2` |

#### 终端节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ClothAssetTerminal` | 将布料集合输出为布料资产（支持多 LOD） | `FChaosClothAssetTerminalNode_v2` |

### 使用示例（Dataflow 图描述）

典型的布料资产构建 Dataflow 图流程：

1. **导入网格**：添加 `SkeletalMeshImport` 节点，指定骨骼网格资产和 LOD 索引，输出 `Collection`
2. **配置模拟参数**：依次连接 `SimulationStretchConfig`、`SimulationBendingConfig`、`SimulationAerodynamicsConfig`、`SimulationCollisionConfig`、`SimulationSelfCollisionConfig` 等配置节点，每个节点的 `Collection` 输入连接前一个节点的 `Collection` 输出
3. **绘制权重图**：添加 `WeightMap` 节点，在编辑器中使用权重图绘制工具绘制权重值（如 MaxDistance、TetherStiffness 等）
4. **配置代理变形器**（可选）：添加 `ProxyDeformer` 节点，定义选择滤波器集来指定哪些渲染顶点由哪些模拟面变形
5. **输出资产**：将最终 `Collection` 连接到 `ClothAssetTerminal` 节点，该节点会将数据写入布料资产

所有配置节点都通过 `Collection` 管线串联（DataflowPassthrough），每个节点仅修改自己关心的属性。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/SimulationBaseConfigNode.h"
#include "ChaosClothAsset/SimulationStretchConfigNode.h"
#include "ChaosClothAsset/SimulationBendingConfigNode.h"
#include "ChaosClothAsset/SimulationAerodynamicsConfigNode.h"
#include "ChaosClothAsset/SimulationCollisionConfigNode.h"
```

### 基本用法 - 自定义模拟配置节点

所有模拟配置节点继承自 `FChaosClothAssetSimulationBaseConfigNode`，需要实现 `AddProperties` 方法来注册属性。

**头文件**：`Source/ChaosClothAssetDataflowNodes/Public/ChaosClothAsset/SimulationBaseConfigNode.h`

```cpp
// 创建自定义配置节点
USTRUCT(Meta = (DataflowCloth))
struct FMyClothConfigNode : public FChaosClothAssetSimulationBaseConfigNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyClothConfigNode, "MyConfig", "Cloth", "My Cloth Config")

public:
    // 可加权属性：支持 Low/High 范围和权重图插值
    UPROPERTY(EditAnywhere, Category = "My Properties",
        Meta = (InteractorName = "MyStiffness"))
    FChaosClothAssetWeightedValue MyStiffness = { true, 1.f, 1.f, TEXT("MyStiffness") };

    FMyClothConfigNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

private:
    // 必须实现：使用 FPropertyHelper 注册所有属性到布料集合
    virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
    {
        // 设置可加权浮点属性
        PropertyHelper.SetProperty(this, &MyStiffness);
    }
};
```

### 进阶用法 - FPropertyHelper 属性系统

`FPropertyHelper` 是基类提供的核心工具，用于将节点属性写入 `FCollectionPropertyMutableFacade`：

**来源**：`SimulationBaseConfigNode.h`

```cpp
virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
{
    // 设置可加权浮点属性（带 Low/High 值和权重图名称）
    PropertyHelper.SetProperty(this, &StretchStiffness);
    
    // 设置布尔属性
    PropertyHelper.SetPropertyBool(this, &bUseGeodesicTethers);
    
    // 设置枚举属性
    PropertyHelper.SetPropertyEnum(this, &SolverType);
    
    // 设置字符串属性
    PropertyHelper.SetPropertyString(this, &SomeStringProperty);
    
    // 设置从 USD/导入值获取的属性（带 solver 值函数）
    PropertyHelper.SetSolverProperty(
        TEXT("PropertyName"), PropertyValue,
        [](FCollectionClothFacade& Facade) { return Facade.GetSomeValue(); },
        SimilarPropertyNames);
    
    // 设置从 fabric 数据获取的加权属性
    PropertyHelper.SetFabricPropertyWeighted(
        TEXT("PropertyName"), PropertyValue,
        [](FCollectionClothFabricFacade& Fabric) { return Fabric.GetSomeValue(); },
        SimilarPropertyNames);
}
```

### 进阶用法 - 可加权值（Weighted Value）系统

**来源**：`WeightedValue.h`

```cpp
// FChaosClothAssetWeightedValue 支持基于权重图的插值
struct FChaosClothAssetWeightedValue
{
    bool bIsAnimatable;  // 是否可在运行时动画化
    float Low;           // 权重 0 对应的值
    float High;          // 权重 1 对应的值
    FString WeightMap;   // 权重图名称
};

// 用法示例：设置拉伸刚度的加权值
FChaosClothAssetWeightedValue StretchStiffness = {
    true,      // bIsAnimatable
    1.f,       // Low（权重为 0 的顶点使用此值）
    1.f,       // High（权重为 1 的顶点使用此值）
    TEXT("StretchStiffness")  // 权重图名称
};
```

## Demo 示例

一个自定义模拟配置节点的完整实现：

```cpp
// MyClothDampingConfigNode.h
#pragma once

#include "ChaosClothAsset/SimulationBaseConfigNode.h"
#include "ChaosClothAsset/WeightedValue.h"
#include "MyClothDampingConfigNode.generated.h"

USTRUCT(Meta = (DataflowCloth))
struct FMyClothDampingConfigNode : public FChaosClothAssetSimulationBaseConfigNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(
        FMyClothDampingConfigNode,
        "MyDampingConfig", "Cloth", "My Cloth Damping Config")

public:
    /** 全局阻尼系数，控制布料运动的衰减 */
    UPROPERTY(EditAnywhere, Category = "Damping",
        Meta = (UIMin = "0", UIMax = "1", ClampMin = "0", ClampMax = "1",
                InteractorName = "GlobalDamping"))
    FChaosClothAssetWeightedValue GlobalDamping = {
        true, 0.1f, 0.5f, TEXT("GlobalDamping") };

    /** 是否启用局部阻尼 */
    UPROPERTY(EditAnywhere, Category = "Damping",
        Meta = (InteractorName = "UseLocalDamping"))
    bool bUseLocalDamping = false;

    FMyClothDampingConfigNode() = default;
    FMyClothDampingConfigNode(
        const UE::Dataflow::FNodeParameters& InParam,
        FGuid InGuid = FGuid::NewGuid())
        : FChaosClothAssetSimulationBaseConfigNode(InParam, InGuid) {}

private:
    virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
    {
        // 注册可加权浮点属性
        PropertyHelper.SetProperty(this, &GlobalDamping);

        // 注册布尔属性
        PropertyHelper.SetPropertyBool(this, &bUseLocalDamping);
    }
};
```

```cpp
// MyClothDampingConfigNode.cpp
#include "MyClothDampingConfigNode.h"

// 节点注册由 DATAFLOW_NODE_DEFINE_INTERNAL 宏自动完成
// 无需额外代码
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段提取：

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料运行时模拟核心 |
| `ChaosClothAsset` | 布料资产定义和布料集合数据结构 |
| `Dataflow` | Dataflow 图框架（节点、上下文、求值） |
| `GeometryProcessing` | 几何处理工具（网格重拓扑、蒙皮权重转移） |
| `MeshResizing` | 网格尺寸调整工具 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-18 | `d4c2bb83` | Fix crash happening when regenerating or visualizing vertex and vertex face springs after the sim me | 修复重新生成或可视化顶点弹簧时的崩溃问题 |
| 2026-05-14 | `e9598355` | Chaos Cloth Asset toolset and updated converter from legacy SKM cloth to Chaos Cloth Asset. | 更新布料资产工具集及旧版 SKM 布料到 Chaos 布料资产的转换器 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `7639ea3a` | Cloth weightmap node - add tranmsfer from render mesh option (on behalf of Tim Brakensiek) | 权重图节点新增从渲染网格传输选项 |

### 维护评价

- **创建时间**：2025-12-05，插件较新（约 1 年），但其代码历史可追溯至更早（从 ChaosClothAsset 拆分）
- **更新频率**：非常活跃，最近一周内有多次提交，包含功能增强、bug 修复和代码清理
- **版本状态**：VersionName 为 `0.1`，仍处于早期版本，API 可能频繁变动
- **废弃标记**：源码中存在大量 `Deprecated = "5.4"` / `5.5` / `5.6"` / `5.7"` / `5.8"` 标记，表明节点 API 在持续演进和重构
- **实验性节点**：部分节点标记为 `Experimental`（如 `SimulationBendingOverrideConfig`、`SimulationClothVertexFaceSpringConfig` 等）
- **推荐程度**：✅ **推荐使用** — 作为 Chaos 布料资产编辑的核心插件，活跃维护且是官方工作流的一部分。但需注意 API 仍在快速迭代，使用实验性节点时需做好适配准备

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetDataflowNodes)
- [官方文档]()（无官方文档链接）
- [测试用例]()（测试文件位于 Engine 测试目录中）