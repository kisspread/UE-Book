# Chaos Cloth Asset Dataflow Nodes

> Dataflow node plugin required to edit a Cloth Asset.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产数据流节点 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosClothAssetDataflowNodes` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-12-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetDataflowNodes) | |

## 用途

该插件提供了一套完整的 **Dataflow 节点集合**，用于在 UE5 编辑器中通过可视化数据流图（Dataflow Graph）构建和编辑 **Cloth Asset**（布料资产）。

它是 Chaos 布料系统与 Dataflow 工具链之间的桥梁。每个节点都是一个 `FDataflowNode` 子类，通过 `FManagedArrayCollection`（布料集合）在节点之间传递数据。用户在 Dataflow 编辑器中连接这些节点，即可完成从网格导入、模拟参数配置、权重图绘制、选择集管理到最终资产生成的完整布料创作工作流。

核心功能包括：
- **网格导入**：从 SkeletalMesh、StaticMesh 或 USD 文件导入模拟/渲染网格
- **模拟配置**：弯曲、拉伸、碰撞、自碰撞、气动、速度缩放等全部模拟参数
- **网格处理**：Remesh（重新网格化）、Proxy Deformer（代理变形器）
- **数据编辑**：权重图绘制、选择集管理、属性创建、蒙皮权重传输
- **资产生成**：终端节点将布料集合导出为可运行时使用的 Cloth Asset

## 使用场景

- 你在制作角色服装的布料模拟 → 用 SkeletalMeshImport 导入网格，通过各种 SimulationXxxConfig 节点调参
- 你需要为布料不同区域设置不同的物理属性 → 用 WeightMap 节点绘制权重图，再连接到配置节点
- 你需要将布料分成蒙皮区域和模拟区域 → 用 ProxyDeformer 节点配合选择集
- 你需要从 Marvelous Designer 等第三方软件导入布料 → 用 USDImport 节点
- 你需要优化布料网格分辨率 → 用 Remesh 节点调整拓扑
- 你需要将一个网格的蒙皮权重转移到布料网格 → 用 TransferSkinWeights 节点

## 蓝图用法

该插件是纯 Editor Dataflow 节点插件，**不提供蓝图可调用的函数**。所有功能通过 Dataflow 编辑器中的节点交互使用。

### 核心节点

#### 网格导入节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SkeletalMeshImport` | 从骨骼网格导入模拟/渲染网格 | `FChaosClothAssetSkeletalMeshImportNode_v2` |
| `StaticMeshImport` | 从静态网格导入模拟/渲染网格 | `FChaosClothAssetStaticMeshImportNode_v2` |
| `USDImport` | 从 USD 文件导入布料数据 | `FChaosClothAssetUSDImportNode_v3` |

#### 模拟配置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SimulationAerodynamicsConfig` | 配置气动属性（风、阻力、升力、水体交互） | `FChaosClothAssetSimulationAerodynamicsConfigNode` |
| `SimulationBendingConfig` | 配置弯曲约束（刚度、阻尼、屈曲） | `FChaosClothAssetSimulationBendingConfigNode` |
| `SimulationStretchConfig` | 配置拉伸约束（经纬方向、面积约束） | `FChaosClothAssetSimulationStretchConfigNode` |
| `SimulationCollisionConfig` | 配置碰撞属性（厚度、摩擦、CCD） | `FChaosClothAssetSimulationCollisionConfigNode` |
| `SimulationSelfCollisionConfig` | 配置自碰撞（厚度、摩擦、层、相交解析） | `FChaosClothAssetSimulationSelfCollisionConfigNode_v2` |
| `SimulationLongRangeAttachmentConfig` | 配置长距离附着约束（Tether） | `FChaosClothAssetSimulationLongRangeAttachmentConfigNode_v2` |
| `SimulationVelocityScaleConfig` | 配置速度缩放（线性/角速度、离心力） | `FChaosClothAssetSimulationVelocityScaleConfigNode` |

#### 实验性配置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SimulationBendingOverrideConfig` | 弯曲约束覆盖（覆盖已有配置） | `FChaosClothAssetSimulationBendingOverrideConfigNode` |
| `SimulationStretchOverrideConfig` | 拉伸约束覆盖 | `FChaosClothAssetSimulationStretchOverrideConfigNode` |
| `SimulationClothVertexFaceSpringConfig` | 顶点-面弹簧约束 | `FChaosClothAssetSimulationClothVertexFaceSpringConfigNode` |
| `SimulationClothVertexSpringConfig` | 顶点-顶点弹簧约束 | `FChaosClothAssetSimulationClothVertexSpringConfigNode` |

#### 网格处理节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Remesh` | 重新网格化模拟/渲染网格 | `FChaosClothAssetRemeshNode_v2` |
| `ProxyDeformer` | 配置代理变形器数据 | `FChaosClothAssetProxyDeformerNode_v3` |
| `TransferSkinWeights` | 从骨骼网格传输蒙皮权重 | `FChaosClothAssetTransferSkinWeightsNode` |

#### 数据编辑节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WeightMap` | 创建/编辑权重图 | `FChaosClothAssetWeightMapNode` |
| `Selection` | 创建/编辑选择集 | `FChaosClothAssetSelectionNode_v2` |
| `Attribute` | 创建自定义属性 | `FChaosClothAssetAttributeNode_v2` |

#### 转换节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ClothCollectionToDynamicMesh` | 布料集合转动态网格 | `FChaosClothAssetCollectionToDynamicMeshNode` |
| `UpdateClothFromDynamicMesh` | 动态网格更新布料集合 | `FChaosClothAssetUpdateClothFromDynamicMeshNode` |
| `ExtractClothWeightMap` | 提取布料权重图 | `FChaosClothAssetExtractWeightMapNode` |
| `ExtractClothSelectionSet` | 提取布料选择集 | `FChaosClothAssetExtractSelectionSetNode` |

#### 终端节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ClothAssetTerminal` | 生成 Cloth Asset（多 LOD） | `FChaosClothAssetTerminalNode_v2` |

### 使用示例（Dataflow 图描述）

**基本布料设置流程：**

1. 添加 `SkeletalMeshImport` 节点，选择角色骨骼网格，指定 LOD 和 UV 通道
2. 连接到 `SimulationBendingConfig` 节点，调整弯曲刚度为 1.0，勾选使用屈曲
3. 连接到 `SimulationStretchConfig` 节点，拉伸刚度设为 1.0
4. 连接到 `SimulationCollisionConfig` 节点，设置碰撞厚度和摩擦
5. 连接到 `SimulationSelfCollisionConfig` 节点，启用自碰撞
6. 连接到 `ClothAssetTerminal` 终端节点，生成最终 Cloth Asset

**选择性模拟区域流程：**

1. 从 `SkeletalMeshImport` 输出布料集合
2. 添加 `WeightMap` 节点，绘制 `MaxDistance` 权重图（0=固定，1=自由模拟）
3. 通过 `Selection` 节点创建渲染顶点和模拟面的选择集
4. 添加 `ProxyDeformer` 节点，连接选择集作为过滤器
5. 添加 `SkinningBlend` 节点创建蒙皮/模拟之间的平滑过渡

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/SimulationBaseConfigNode.h"
#include "ChaosClothAsset/SelectionNode.h"
#include "ChaosClothAsset/WeightMapNode.h"
```

### 基本用法

所有模拟配置节点都继承自 `FChaosClothAssetSimulationBaseConfigNode`。该基类提供了 `FPropertyHelper` 工具类来设置布料属性：

```cpp
// 继承基类实现自定义配置节点
USTRUCT(Meta = (DataflowCloth))
struct FMyCustomConfigNode : public FChaosClothAssetSimulationBaseConfigNode
{
    GENERATED_USTRUCT_BODY()

    UPROPERTY(EditAnywhere, Category = "My Config")
    FChaosClothAssetWeightedValue MyStiffness = { true, 1.0f, 1.0f, TEXT("MyStiffness") };

    UPROPERTY(EditAnywhere, Category = "My Config")
    bool bEnableMyFeature = true;

private:
    virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
    {
        // 使用模板函数按地址自动查找属性名
        PropertyHelper.SetProperty(this, &MyStiffness);
        PropertyHelper.SetPropertyBool(this, &bEnableMyFeature);
    }
};
```

> 来源：`SimulationBaseConfigNode.h` 中 `FPropertyHelper` 的设计模式

### 进阶用法

使用 `SetProperty` 系列函数可直接按名称设置属性，并支持权重图插值：

```cpp
virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
{
    // 按名称设置（需要手动指定名称）
    PropertyHelper.SetProperty(TEXT("MyStiffness"), MyStiffness);

    // 设置布尔属性（自动去掉 'b' 前缀）
    PropertyHelper.SetPropertyBool(this, &bEnableFeature);

    // 设置枚举属性
    PropertyHelper.SetPropertyEnum(TEXT("ConstraintType"), ConstraintType);

    // 设置加权值属性（支持 Low/High + 权重图插值）
    PropertyHelper.SetPropertyWeighted(TEXT("Damping"), Damping);

    // 设置字符串属性
    PropertyHelper.SetPropertyString(TEXT("WeightMapName"), WeightMap);
}

// 覆盖已有布料集合中的属性
virtual void EvaluateClothCollection(FContext& Context,
    const TSharedRef<FManagedArrayCollection>& ClothCollection) const override
{
    // 在属性设置完成后执行额外的布料集合操作
}
```

> 来源：各 `SimulationXxxConfigNode.h` 文件中的 `AddProperties` 实现

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料运行时模拟核心 |
| `ChaosClothAsset` | 布料资产数据结构和 Facade |
| `Dataflow` | Dataflow 框架（节点、图、求值） |
| `GeometryProcessing` | 几何处理（Remesh、TransferBoneWeights 等） |
| `MeshResizing` | 网格重缩放 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-18 | `d4c2bb83` | Fix crash happening when regenerating or visualizing vertex and vertex face springs after the sim me | 修复重新生成/可视化顶点和顶点面弹簧后的崩溃 |
| 2026-05-14 | `e9598355` | Chaos Cloth Asset toolset and updated converter from legacy SKM cloth to Chaos Cloth Asset. | 更新布料资产工具集及从旧版 SKM 布料的转换器 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double 截断为 float 警告 |
| 2026-05-12 | `7639ea3a` | Cloth weightmap node - add tranmsfer from render mesh option (on behalf of Tim Brakensiek) | 权重图节点增加从渲染网格传输选项 |

### 维护评价

该插件处于**活跃维护**状态。自 2025 年 12 月创建以来，持续有功能性更新，最近 1 个月内有多次提交，涵盖：
- Bug 修复（崩溃修复、编译警告修复）
- 新功能（渲染网格权重传输、工具集更新）
- 代码清理和重构

该插件是 Chaos 布料资产编辑流程的核心组件，预计将持续积极维护。多个节点存在版本迭代（v1→v2→v3），旧版标记为 `Deprecated`，说明 Epic 正在持续优化 API。

**注意**：该插件默认不启用（`Installed: false`），需要在项目设置中手动启用，或通过依赖它的插件间接启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetDataflowNodes)
- [官方文档]()（无）