# Chaos Rigid Asset

> Rigid Asset plugin for creating and utilising collections of rigid bodies

| 属性 | 值 |
|---|---|
| 中文名 | 混沌刚体资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点、资产编辑器） |
| 模块 | `ChaosRigidAssetEditor` (Editor), `ChaosRigidAssetNodes` (Runtime), `ChaosRigidAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidAsset) | |

## 用途

ChaosRigidAsset 插件的核心目的是为 Chaos 物理系统提供一套**基于数据流（Dataflow）的工作流**，用于程序化地创建、编辑和生成物理资产（`UPhysicAsset`）。它并非替代传统的物理资产编辑器，而是通过数据流图，将复杂的物理资产创建过程（如为骨骼网格体的骨骼生成碰撞体、关节等）自动化、模块化和参数化。这解决了在传统编辑器中手动设置复杂角色或对象物理资产时，过程繁琐、难以迭代和版本控制的问题。

## 使用场景

-   **程序化内容生成**：在大型开放世界或模拟中，需要为大量不同规格的 NPC 或生物自动生成物理资产。
-   **角色物理快速迭代**：角色动画师或技术美术师希望快速调整角色的碰撞体形状、约束范围等，无需在编辑器中逐一修改。
-   **将物理资产创建集成到流水线**：将物理资产的生成作为自动化构建或资产处理流水线的一部分，实现可重复的构建。
-   **替代传统物理资产编辑器**：当资产通过数据流生成时，系统可以自动打开数据流编辑器而非物理资产编辑器，提供更直观的节点化编辑体验。

## 蓝图用法

本插件的核心功能通过数据流节点（ChaosRigidAssetNodes）暴露，而非直接的蓝图函数节点。其主要交互发生在**数据流编辑器（Dataflow Editor）** 中，通过连接不同的节点图来实现物理资产的程序化构建。

### 核心数据流节点（概念性）

| 节点类型 | 说明 |
|---|---|
| **输入/终端节点** | 接收骨骼网格体等输入，并最终输出一个 `UPhysicAsset`。 |
| **几何体生成器** | 为指定的骨骼生成碰撞几何体（如球体生成器）。 |
| **约束生成器** | 为指定的骨骼创建关节约束（如简单的摆动/扭转生成器）。 |
| **选择操作节点** | 对骨骼、刚体、约束的选择集进行操作和过滤。 |

### 使用示例（蓝图描述）

1.  在内容浏览器中创建一个 **Dataflow Asset**。
2.  打开该资产，进入 **数据流编辑器**。
3.  从节点库中拖出 **`Rigid Asset Terminal`** 节点。
4.  拖入一个 **骨骼网格体输入** 节点，并将其连接到终端节点。
5.  添加 **几何体生成器节点**（例如 `Sphere Generator`），连接到终端节点的相关输入引脚，并配置其作用于哪些骨骼。
6.  添加 **约束生成器节点**（例如 `Simple Swing Twist Generator`），类似地进行连接和配置。
7.  通过 **选择节点** 来精细控制哪些骨骼会应用这些生成器。
8.  点击编译/预览，数据流图将计算并生成一个 `UPhysicAsset`。

## C++ 用法

### 头文件引入

主要在编辑器和数据流扩展模块中使用。
```cpp
#include "ChaosRigidAssetEditorModule.h"
#include "DataflowRendering.h" // 用于渲染相关的回调
```

### 基本用法

该插件的 C++ API 主要集中在数据流图节点的创建和注册，以及编辑器集成的扩展。典型的用法是在自定义的数据流节点中操作物理资产的数据。

```cpp
// 一个自定义的数据流节点可能需要继承自基础节点类
// 以下为概念性代码，具体基类需查看 ChaosRigidAssetNodes 模块
class FMyCustomRigidNode : public FDataflowNode
{
public:
    // ... 节点输入输出端口定义 ...

    // 节点评估函数，这是核心
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Output) const override
    {
        // 1. 从输入端口获取数据（如骨骼信息、选择集）
        // 2. 执行自定义逻辑（例如，基于特定算法生成碰撞体形状）
        // 3. 将结果设置到输出端口，供下游节点或终端节点使用
    }
};

// 在编辑器模块启动时注册自定义的渲染回调
void FChaosRigidAssetEditorModule::StartupModule()
{
    // EditorFeature = MakeUnique<FDataflowPhysicsAssetEditorOverride>(...);
    // 注册各种自定义的节点渲染器（如 FAgregateGeometryGeomRenderCallbacks）
}
```

**来源**: `ChaosRigidAssetEditorModule.h`, `DataflowRendering.h`

### 进阶用法

进阶用法涉及深度集成，例如创建自定义的几何体或约束生成器，并将它们注册到数据流系统中。这通常需要理解 `ChaosRigidAssetNodes` 模块中现有节点的实现模式，并依赖 `ChaosRigidAssetEngine` 模块提供的底层物理资产操作工具。

## Demo 示例

以下是一个最小化的自定义数据流节点示例框架，展示了如何接入该插件的系统。

```cpp
// MyRigidAssetNode.h
#pragma once

#include "Dataflow/DataflowNode.h"
// 可能需要包含 ChaosRigidAssetNodes 或 ChaosRigidAssetEngine 中的相关头文件

/**
 * 一个示例数据流节点，用于简单演示。
 */
class FMySimpleBodyGeneratorNode : public FDataflowNode
{
public:
    FMySimpleBodyGeneratorNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());
    virtual ~FMySimpleBodyGeneratorNode() override = default;

    // 定义输入：一个骨骼名称列表
    UE::Dataflow::TConnection<FName> BoneNamesInput;

    // 定义输出：一组生成的物理体定义
    UE::Dataflow::TConnection<TArray<FPhysicsBodyData*>> BodyDataOutput;

    // 节点评估
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Output) const override;
};
```

```cpp
// MyRigidAssetNode.cpp
#include "MyRigidAssetNode.h"

FMySimpleBodyGeneratorNode::FMySimpleBodyGeneratorNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FDataflowNode(InParam, InGuid)
    , BoneNamesInput(this)
    , BodyDataOutput(this)
{
    // 注册端口
    RegisterInputConnection(&BoneNamesInput);
    RegisterOutputConnection(&BodyDataOutput);
}

void FMySimpleBodyGeneratorNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Output) const
{
    if (Output->IsA(&BodyDataOutput))
    {
        // 1. 从输入获取骨骼名列表
        const TArray<FName>& Bones = Context.GetValue(BoneNamesInput);

        // 2. 简单逻辑：为每个骨骼创建一个默认的球体物理体数据
        TArray<FPhysicsBodyData*> Bodies;
        for (const FName& Bone : Bones)
        {
            // 这里需要调用 ChaosRigidAssetEngine 中的函数来创建 FPhysicsBodyData
            // FPhysicsBodyData* BodyData = UPhysicsAssetFactory::CreateSphereBodyData(Bone, Radius);
            // Bodies.Add(BodyData);
        }

        // 3. 设置输出
        Context.SetValue(BodyDataOutput, Bodies);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | 插件的核心依赖，提供数据流图框架、节点和编辑器。 |
| `GeometryProcessing` | 用于处理和生成几何体数据，可能在生成碰撞体形状时使用。 |
| `Chaos` (Chaos Solver) | 底层的 Chaos 物理系统，被 `ChaosRigidAssetEngine` 调用以操作物理资产。 |
| `PhysicsCore` | 提供 `UPhysicAsset` 等核心物理资产类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `1a41cebd` | Dataflow : fix Dataflow nodes not properly referencing the node when outputing error messages causing | 修复了数据流节点在输出错误信息时，未能正确引用节点本身，导致错误报告不准确的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件中的日志输出宏从 UE_LOG 迁移到 UE_LOGF，以遵循新的日志规范。 |
| 2026-04-10 | `36646cb9` | Rigid asset - Update rigid asset asset to use the unified dataflow menu command so that the user exp | 更新了刚体资产，使其使用统一的数据流菜单命令，改善用户体验，使打开数据流编辑器的流程更一致。 |
| 2026-04-10 | `5c4d7272` | Dataflow : added an API to dataflow attachment to get the preview actor path for the Dataflow Editor | 为数据流附件添加了新API，用于获取数据流编辑器的预览Actor路径，便于扩展编辑器功能。 |
| 2026-04-07 | `b7596b26` | Fixup docs on rigid caching node | 修复了关于刚体缓存节点的文档。 |

### 维护评价

- **活跃维护**：插件创建于 **2025年8月**，距今约1年。从最近的提交记录（2026年4月）看，**维护非常活跃**。
- **近期更新内容**：最近的更新集中在**错误修复、API改进、用户体验优化（统一菜单）和代码规范化（日志迁移）**，表明插件处于快速开发和打磨阶段。
- **实验性状态**：插件标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，说明其API和功能可能尚未稳定，不建议在生产环境中直接使用。
- **推荐度**：**推荐尝试**。对于希望探索 **程序化物理资产创建工作流** 的项目或研究用途，这是一个非常前沿和有潜力的工具。但应做好应对API变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidAsset)
- [官方文档]() (暂无)
- [测试用例]() (需在引擎测试目录或插件内部搜索)