# Chaos Cloth Asset Dataflow Nodes

> Dataflow node plugin required to edit a Cloth Asset.

| 属性 | 值 |
|---|---|
| 中文名 | 布料数据流节点 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosClothAssetDataflowNodes` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-12-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetDataflowNodes) | |

## 用途

该插件为 Chaos Cloth Asset 系统提供 **Dataflow 可视化节点编辑能力**。它是布料资产编辑管线的核心组件——没有这些节点，用户无法在 Dataflow 图中构建、配置或调试布料模拟。

插件包含 80+ 个 Dataflow 节点，覆盖布料资产创建的完整流程：

1. **网格导入**：从 SkeletalMesh、StaticMesh 或 USD 文件导入仿真网格和渲染网格
2. **拓扑操作**：重网格化（Remesh）、选择集管理、权重图编辑
3. **蒙皮权重转移**：从骨骼网格转移蒙皮权重到布料网格
4. **物理约束配置**：拉伸（Stretch）、弯曲（Bending）、长距离附着（Long Range Attachment）、顶点弹簧（Vertex Spring）、顶点-面弹簧（VertexFace Spring）
5. **仿真环境配置**：空气动力学（Aerodynamics）、碰撞（Collision）、自碰撞（Self-Collision）、速度缩放（Velocity Scale）
6. **代理变形器**：控制渲染网格与仿真网格之间的变形映射
7. **资产输出**：终端节点将处理结果打包为 Cloth Asset

该插件从 `ChaosClothAsset` 的 USD Dataflow 节点独立而来（见首次提交信息），专门负责节点定义，与核心运行时逻辑分离。

## 使用场景

- 你在制作角色服装、旗帜、披风等布料效果 → 在 Dataflow 图中使用这些节点构建布料资产
- 你需要精细控制布料的拉伸、弯曲、风力等物理行为 → 使用各 SimulationXxxConfig 节点
- 你从第三方 DCC 工具（如 Marvelous Designer）导出了 USD 文件 → 使用 USDImport 节点导入
- 你需要对布料网格进行重网格化以调整分辨率 → 使用 Remesh 节点
- 你需要将骨骼网格的蒙皮权重转移到布料网格 → 使用 TransferSkinWeights 节点
- 你只想让渲染网格的特定区域参与布料仿真 → 使用 ProxyDeformer 节点配合选择集

**典型工作流**：

```
网格导入 → 选择/权重编辑 → 物理约束配置 → 仿真环境设置 → 代理变形器 → 终端输出
```

## 蓝图用法

本插件不提供蓝图节点。所有功能通过 **Dataflow 图编辑器**（Cloth Editor 内）以节点图形式使用。Dataflow 节点在编辑器中以可视化节点形式呈现，用户通过连接节点端口来构建布料资产处理管线。

### 核心节点分类

#### 导入节点

| 节点 | 说明 | 状态 |
|---|---|---|
| `SkeletalMeshImport` | 从骨骼网格导入仿真/渲染网格 | ✅ 活跃 |
| `StaticMeshImport` | 从静态网格导入仿真/渲染网格 | ✅ 活跃 |
| `USDImport` | 从 USD 文件导入（第三方 DCC 工具） | ⚠️ 已弃用 |

#### 物理约束配置节点

| 节点 | 说明 | 状态 |
|---|---|---|
| `SimulationStretchConfig` | 拉伸约束（刚度、阻尼、各向异性） | ✅ 活跃 |
| `SimulationBendingConfig` | 弯曲约束（铰链角、刚度、屈曲） | ✅ 活跃 |
| `SimulationLongRangeAttachmentConfig` | 长距离附着约束（防止过度拉伸） | ✅ 活跃 |
| `SimulationAerodynamicsConfig` | 空气动力学（风力、阻力、升力、水体交互） | ✅ 活跃 |
| `SimulationCollisionConfig` | 碰撞配置（碰撞厚度、摩擦力、CCD） | ✅ 活跃 |
| `SimulationSelfCollisionConfig` | 自碰撞配置（厚度、摩擦力、分层） | ✅ 活跃 |
| `SimulationVelocityScaleConfig` | 速度缩放（线性/角速度限制、离心力） | ✅ 活跃 |
| `SimulationClothVertexSpringConfig` | 顶点-顶点弹簧约束 | 🧪 实验性 |
| `SimulationClothVertexFaceSpringConfig` | 顶点-面弹簧约束 | 🧪 实验性 |

#### 覆盖配置节点

| 节点 | 说明 | 状态 |
|---|---|---|
| `SimulationBendingOverrideConfig` | 弯曲约束覆盖 | 🧪 实验性 |
| `SimulationStretchOverrideConfig` | 拉伸约束覆盖 | 🧪 实验性 |

#### 网格操作节点

| 节点 | 说明 | 状态 |
|---|---|---|
| `Remesh` | 重网格化（调整分辨率） | ✅ 活跃 |
| `TransferSkinWeights` | 转移蒙皮权重 | ✅ 活跃 |
| `ClothCollectionToDynamicMesh` | 布料集合转动态网格 | 🧪 实验性 |

#### 选择与权重节点

| 节点 | 说明 | 状态 |
|---|---|---|
| `Selection` | 顶点/面选择集 | ✅ 活跃 |
| `WeightMap` | 权重图编辑与绘制 | ✅ 活跃 |
| `Attribute` | 创建自定义属性 | 🧪 实验性 |

#### 变形与输出节点

| 节点 | 说明 | 状态 |
|---|---|---|
| `ProxyDeformer` | 代理变形器（渲染-仿真映射） | ✅ 活跃 |
| `ClothAssetTerminal` | 终端节点，生成 Cloth Asset | ✅ 活跃 |

### 使用示例（Dataflow 图描述）

**基础布料资产创建流程**：

1. 创建 `SkeletalMeshImport` 节点，连接骨骼网格资产，设置 LOD 和 UV 通道
2. 将其输出连接到 `SimulationStretchConfig`，配置拉伸刚度（如 Low=0.8, High=1.0）和权重图
3. 连接 `SimulationBendingConfig`，设置弯曲刚度和约束类型
4. 连接 `SimulationCollisionConfig`，设置碰撞厚度和摩擦系数
5. 连接 `SimulationAerodynamicsConfig`，设置风速和阻力系数
6. 将最终集合输出连接到 `ClothAssetTerminal` 节点
7. Dataflow 图自动将配置序列化为 Cloth Asset

**自定义代理变形器**：

1. 在 `SkeletalMeshImport` 后连接 `Selection` 节点，选择需要参与仿真的网格区域
2. 连接 `ProxyDeformer` 节点，将选择集作为输入
3. 无选择集输入时 → 完全蒙皮；有选择集时 → 选择区域参与布料变形

## C++ 用法

本插件的节点是 USTRUCT 数据流节点（继承自 `FDataflowNode`），不是传统蓝图函数。主要的 C++ 使用场景是**扩展自定义节点**。

### 头文件引入

```cpp
#include "ChaosClothAsset/SimulationBaseConfigNode.h"
```

### 基本用法：继承基础配置节点创建自定义仿真参数节点

所有仿真配置节点的基类是 `FChaosClothAssetSimulationBaseConfigNode`。自定义仿真参数时，继承此类并实现 `AddProperties` 方法。

```cpp
// 来源: Source/ChaosClothAssetDataflowNodes/Public/ChaosClothAsset/SimulationBaseConfigNode.h

// 自定义一个简单的风力配置节点
USTRUCT(Meta = (DataflowCloth))
struct FMyCustomWindConfigNode : public FChaosClothAssetSimulationBaseConfigNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomWindConfigNode, "MyWindConfig", "Cloth", "Custom Wind Config")

public:
    // 自定义的风力方向（可动画化）
    UPROPERTY(EditAnywhere, Category = "Wind", Meta = (InteractorName = "WindDirection"))
    FVector3f WindDirection = { 1.f, 0.f, 0.f };

    // 风力强度（带权重图支持的范围值）
    UPROPERTY(EditAnywhere, Category = "Wind", Meta = (UIMin = "0", UIMax = "100"))
    FChaosClothAssetWeightedValue WindStrength = { true, 10.f, 10.f, TEXT("WindStrength") };

    FMyCustomWindConfigNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FChaosClothAssetSimulationBaseConfigNode(InParam, InGuid)
    {
    }

private:
    // 实现属性注册——这是基类的纯虚函数，必须实现
    virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
    {
        // 通过 FPropertyHelper 将属性写入布料集合
        PropertyHelper.SetProperty(TEXT("WindDirection"), WindDirection);
        PropertyHelper.SetPropertyWeighted(TEXT("WindStrength"), WindStrength);
    }
};
```

### 进阶用法：使用 FPropertyHelper 管理属性

`FPropertyHelper` 是属性注册的核心辅助类，提供多种类型的安全属性设置方法。

```cpp
// 来源: Source/ChaosClothAssetDataflowNodes/Public/ChaosClothAsset/SimulationBaseConfigNode.h

virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
{
    // 1. 设置浮点属性
    PropertyHelper.SetProperty(TEXT("MyFloat"), MyFloatValue);
    
    // 2. 设置布尔属性
    PropertyHelper.SetPropertyBool(TEXT("bMyBool"), bMyFlag);
    
    // 3. 设置枚举属性
    PropertyHelper.SetPropertyEnum(TEXT("MyEnum"), MyEnumValue);
    
    // 4. 设置字符串属性
    PropertyHelper.SetPropertyString(TEXT("MyString"), MyStringValue);
    
    // 5. 设置带权重图的属性（最常用）
    PropertyHelper.SetPropertyWeighted(TEXT("Stiffness"), StiffnessWeighted);
    
    // 6. 设置带导入器数据的属性
    PropertyHelper.SetSolverProperty(TEXT("SolverProp"), SolverPropValue,
        [](auto& ClothFacade) -> auto { return ClothFacade.GetSomeValue(); },
        {});
    
    // 7. 设置织物属性
    PropertyHelper.SetFabricProperty(TEXT("FabricProp"), FabricPropValue,
        [](auto& FabricFacade) -> auto { return FabricFacade.GetSomeValue(); },
        {});
    
    // 8. 布尔属性名必须以 'b' 开头
    PropertyHelper.SetPropertyBool(TEXT("bUseGravity"), true);
}
```

### 自动属性名推导（推荐方式）

通过结构体指针和成员指针自动获取 UPROPERTY 名称，无需硬编码字符串：

```cpp
virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
{
    // 使用结构体指针 + 成员地址自动推导属性名
    // 布尔属性会自动移除 'b' 前缀
    PropertyHelper.SetPropertyBool(this, &FMyNode::bUseGravity);
    PropertyHelper.SetProperty(this, &FMyNode::Stiffness);
    PropertyHelper.SetPropertyEnum(this, &FMyNode::SolverType);
    PropertyHelper.SetPropertyWeighted(this, &FMyNode::DragCoefficient);
}
```

## Demo 示例

以下展示一个自定义仿真约束配置节点的完整实现：

```cpp
// MyClothTurbulenceConfigNode.h
#pragma once

#include "ChaosClothAsset/SimulationBaseConfigNode.h"
#include "MyClothTurbulenceConfigNode.generated.h"

/** 湍流扰动约束配置节点 */
USTRUCT(Meta = (DataflowCloth))
struct FMyClothTurbulenceConfigNode final : public FChaosClothAssetSimulationBaseConfigNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(
        FMyClothTurbulenceConfigNode,
        "MyTurbulenceConfig", "Cloth", "Custom Turbulence Config")

public:
    /** 湍流强度，支持权重图插值 */
    UPROPERTY(EditAnywhere, Category = "Turbulence", Meta = (UIMin = "0", UIMax = "100"))
    FChaosClothAssetWeightedValue TurbulenceStrength = { true, 5.f, 5.f, TEXT("Turbulence") };

    /** 湍流频率 (Hz) */
    UPROPERTY(EditAnywhere, Category = "Turbulence", Meta = (UIMin = "0", UIMax = "10"))
    float Frequency = 1.0f;

    /** 是否随时间衰减 */
    UPROPERTY(EditAnywhere, Category = "Turbulence")
    bool bDecayOverTime = true;

    FMyClothTurbulenceConfigNode() = default;
    FMyClothTurbulenceConfigNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FChaosClothAssetSimulationBaseConfigNode(InParam, InGuid)
    {
    }

private:
    virtual void AddProperties(FPropertyHelper& PropertyHelper) const override
    {
        // 使用指针方式自动获取属性名
        PropertyHelper.SetPropertyWeighted(this, &FMyClothTurbulenceConfigNode::TurbulenceStrength);
        PropertyHelper.SetProperty(this, &FMyClothTurbulenceConfigNode::Frequency);
        PropertyHelper.SetPropertyBool(this, &FMyClothTurbulenceConfigNode::bDecayOverTime);
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料物理引擎核心 |
| `ChaosClothAsset` | 布料资产数据结构（Collection、Facade 等） |
| `Dataflow` | Dataflow 图编辑框架（节点基类、连接、上下文） |
| `GeometryProcessing` | 几何处理算法（重网格化、蒙皮权重转移） |
| `MeshResizing` | 网格尺寸调整 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-18 | `d4c2bb83` | Fix crash happening when regenerating or visualizing vertex and vertex face springs after the sim me | 修复仿真网格重新生成后顶点弹簧可视化崩溃问题 |
| 2026-05-14 | `e9598355` | Chaos Cloth Asset toolset and updated converter from legacy SKM cloth to Chaos Cloth Asset. | 更新从旧版骨骼网格布料到 Chaos Cloth Asset 的转换工具 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-12 | `7639ea3a` | Cloth weightmap node - add tranmsfer from render mesh option | 权重图节点新增从渲染网格转移的选项 |

### 维护评价

- **活跃维护**：最近更新日期为 2026-05-20，更新非常频繁（几乎每天都有提交）
- **持续演进**：节点版本迭代活跃（v2、v3 后缀节点），旧节点标记为 `Deprecated`，说明 API 在持续改进
- **API 稳定性**：部分实验性节点（标记 `Experimental`）可能在未来版本变更
- **建议使用最新版本**：多个节点（ProxyDeformer、Remesh、Selection、TerminalNode 等）存在已弃用的旧版本，使用时应选择无 `Deprecated` 标记的最新版本

**推荐使用**：该插件处于活跃开发阶段，是 Chaos Cloth Asset 工作流的核心组成部分，推荐使用最新版本的节点以获得最佳兼容性和功能支持。