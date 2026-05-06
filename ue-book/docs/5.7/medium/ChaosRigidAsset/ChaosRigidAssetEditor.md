# Chaos Rigid Asset

> Rigid Asset plugin for creating and utilising collections of rigid bodies

| 属性 | 值 |
|---|---|
| 中文名 | 刚体资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点、物理碰撞几何体资产定义） |
| 模块 | `ChaosRigidAssetEditor` (Editor), `ChaosRigidAssetNodes` (Runtime), `ChaosRigidAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset) | |

---

## 用途

Chaos Rigid Asset 插件是 **Dataflow 流程的一部分**，用于在数据可视化编程环境中**定义和生成物理刚体集合（Rigid Bodies）**。它提供了一组 Dataflow 节点，允许用户以程序化的方式创建简单碰撞几何体（盒体、胶囊体、凸包），并将它们组合成可用于物理模拟的刚体资产（例如物理资产 Physics Asset 或碰撞体集合）。

**为什么存在？**

- 传统上，物理碰撞体需要手动在编辑器里放置、调整形状，或者通过导入网格自动生成。该插件将这一过程**流程化、无编程化**，让技术美术和程序员可以在 Dataflow 图中直观地定义物理体形状、位置、材质等属性。
- 特别适用于程序化生成场景、布料/刚体模拟、布娃娃系统，以及需要批量创建物理碰撞体的工作流。

---

## 使用场景

- **程序化布娃娃系统**：在 Dataflow 中定义每个骨头的碰撞体（盒体、胶囊体），自动生成 Physics Asset。
- **动态刚体集合**：为动态物体（如碎片、道具）生成统一的碰撞几何体集合。
- **数据驱动物理资产**：无需手动编辑，通过 Dataflow 节点配置、调整，快速迭代物理效果。
- **与 Chaos 物理系统集成**：生成的结构可直接用于 Chaos 的刚体、布料等模拟。

---

## 蓝图用法

本插件**不直接暴露**蓝图可调用的函数或节点。其功能完全通过 **Dataflow 资产** 中的 **Dataflow 节点** 使用，这些节点只能在 Dataflow 编辑器里连接和配置。

### 核心节点

| 节点（示例名称） | 说明 | 所在类（推测） |
|---|---|---|
| `Make Box Geometry` | 创建一个盒体碰撞几何体，可设置尺寸、位置、旋转 | `FMakeBoxGeometryDataflowNode` |
| `Make Capsule Geometry` | 创建一个胶囊体碰撞几何体，可设置半径、半高、位置、旋转 | `FMakeCapsuleGeometryDataflowNode` |
| `Make Convex Geometry` | 由一个静态网格体生成凸包碰撞几何体 | `FMakeConvexGeometryDataflowNode` |
| `Aggregate Geometry` | 将多个几何体合并为一个刚体集合 | `FAggregateGeometryDataflowNode` |
| `Create Physics Asset` | 根据刚体集合生成物理资产（UPhysicsAsset） | `FCreatePhysicsAssetDataflowNode` |

> 以上节点名称基于 git log 和插件功能推断，实际名称可能略有差异。这些节点存在于 `ChaosRigidAssetNodes` 模块中，未提供源码，因此无法列出精确签名。

---

## C++ 用法

### 头文件引入

```cpp
#include "ChaosRigidAssetEditorModule.h"
#include "DataflowRendering.h"
```

### 基本用法

**1. 注册模块（通常在模块 Startup 时自动完成）**

插件启动时，`FChaosRigidAssetEditorModule::StartupModule()` 会注册编辑器扩展（如资产菜单扩展）和渲染回调。

**2. 在自定义渲染中注册回调（用于 Dataflow 视图）**

如果你要在 Dataflow 视图中可视化自定义的刚体几何体，可以实现 `UE::Dataflow::FRenderingFactory::ICallbackInterface`：

```cpp
// 摘自引擎源码：DataflowRendering.h
class FAggregateGeometryGeomRenderCallbacks : public UE::Dataflow::FRenderingFactory::ICallbackInterface
{
public:
    static UE::Dataflow::FRenderKey StaticGetRenderKey();
    UE::Dataflow::FRenderKey GetRenderKey() const override;
    bool CanRender(const UE::Dataflow::IDataflowConstructionViewMode& ViewMode) const override;
    void Render(GeometryCollection::Facades::FRenderingFacade& RenderingFacade, 
                const UE::Dataflow::FGraphRenderingState& State) override;
};
```

使用时只需在 `StartupModule` 中向 `FRenderingFactory` 注册：

```cpp
#include "Dataflow/DataflowRenderingFactory.h"

void FMyModule::StartupModule()
{
    // 注册刚体集合渲染回调
    UE::Dataflow::FRenderingFactory::RegisterRenderCallback(
        MakeShared<UE::Chaos::RigidAsset::FAggregateGeometryGeomRenderCallbacks>()
    );
}
```

### 进阶用法

由于插件仍处于实验阶段，其高级用法集中于 Dataflow 节点组合。以下是一个在 C++ 中手动调用 Dataflow 节点创建物理资产的示例（伪代码）：

```cpp
// 假设已有 Dataflow 图和输入几何体
TSharedPtr<FDataflowNode> BoxNode = DataflowGraph->AddNode(FName("MakeBoxGeometry"));
BoxNode->SetInput("Dimensions", FVector(100, 50, 30));

TSharedPtr<FDataflowNode> AggregateNode = DataflowGraph->AddNode(FName("AggregateGeometry"));
AggregateNode->ConnectInput("Geometries", BoxNode->GetOutput("Geometry"));

TSharedPtr<FDataflowNode> CreatePhysicsAssetNode = DataflowGraph->AddNode(FName("CreatePhysicsAsset"));
CreatePhysicsAssetNode->ConnectInput("AggregateGeometry", AggregateNode->GetOutput("Result"));

// 执行图并获取输出物理资产
DataflowGraph->Evaluate();
UPhysicsAsset* NewAsset = CreatePhysicsAssetNode->GetOutput<UPhysicsAsset*>("PhysicsAsset");
```

> 实际 API 取决于 `ChaosRigidAssetNodes` 模块的实现，此示例仅演示概念。

---

## Demo 示例

由于该插件主要依赖 Dataflow 编辑器交互，以下提供一个 C++ 最小示例，创建一个 `UPhysicsAsset` 并通过刚体资产插件功能生成盒体碰撞。

**MyPhysicsAssetGenerator.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "PhysicsEngine/PhysicsAsset.h"

/**
 * 生成一个包含单个盒体刚体的物理资产
 */
class MYGAME_API FPhysicsAssetGenerator
{
public:
    static UPhysicsAsset* GenerateBoxPhysicsAsset(UObject* Outer, float HalfX, float HalfY, float HalfZ);
};
```

**MyPhysicsAssetGenerator.cpp**

```cpp
#include "MyPhysicsAssetGenerator.h"

// 需要包含刚体资产模块的头文件（若有暴露公共API）
// #include "ChaosRigidAssetNodes/Public/MakeBoxGeometryNode.h"  // 假想头文件

UPhysicsAsset* FPhysicsAssetGenerator::GenerateBoxPhysicsAsset(UObject* Outer, float HalfX, float HalfY, float HalfZ)
{
    // 由于运行时 API 尚未公开，此示例仅为概念演示
    // 实际可直接使用 UPhysicsAsset 的 API 创建，或通过 Dataflow 图执行
    UPhysicsAsset* Asset = NewObject<UPhysicsAsset>(Outer);
    // ... 填充碰撞体 ...
    return Asset;
}
```

> 注意：当前插件版本（2025-09）未提供稳定公共 API。推荐在 Dataflow 编辑器中直接操作。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | 提供 Dataflow 图框架和节点基础类 |

其他依赖均为标准 Core/Engine/Slate 模块，未列出。

---

## 维护状态

### 近期更新

- 2025-09-30 `5c0a4ef4` — [Dataflow] Added Box, Capsule and Convex simple builders as geometry generators for dataflow physics
- 2025-09-29 `6813b43d` — [Dataflow] Fixed physics asset generation not correctly setting base joint names on constraints
- 2025-09-26 `d83fb5ae` — [Backout] - CL46264036
- 2025-09-26 `3f07f94a` — [Dataflow] Added Box, Capsule and Convex simple builders as geometry generators for dataflow physics
- 2025-08-15 `4499bef8` — Fix warning due to passing derived member to multi-pin constructor

### 维护评价

- **创建时间**：2025年8月15日，至今约2个月
- **更新频率**：最近一个月内有多次功能性更新（添加构建器、修复约束命名）
- **活跃度**：处于积极开发阶段，Epic Games 正在完善 Dataflow 与物理资产的集成
- **实验性标志**：已标记为实验性，表示 API 可能变动，不建议直接依赖
- **推荐使用**：**谨慎使用**。适合探索和原型开发，但尚未稳定，已有功能（Box/Capsule/Convex）基本可用。如果生产项目需要，建议等官方正式版或自行封装。

---

## 相关链接

- [源码（插件目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/dataflow)（Dataflow 概览）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset/Tests)（若有）