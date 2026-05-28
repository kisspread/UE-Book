# Hierarchy Table Animation

> Animation-specific type definitions for Hierarchy Tables

| 属性 | 值 |
|---|---|
| 中文名 | 层级表动画 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画节点，编辑器工具） |
| 模块 | `HierarchyTableAnimationRuntime` (Runtime), `HierarchyTableAnimationEditor` (Editor), `HierarchyTableAnimationUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation) | |

## 用途

`HierarchyTableAnimation` 插件为 `HierarchyTable` 核心插件提供了动画领域特定的类型定义和功能扩展。其主要目的是支持基于骨骼层次结构的复杂动画混合逻辑。

具体来说，该插件引入了一个关键的动画蓝图节点 `FAnimNode_BlendProfileLayeredBlend`。这个节点允许用户根据一个“混合配置文件”（Blend Profile）来控制不同骨骼（或骨骼组）的混合权重，从而实现分层的、基于骨骼层次的动画混合效果。例如，你可以定义角色的左臂和右腿使用不同的混合权重，从而实现非对称的动画混合，这在标准混合节点中难以实现。

该插件的存在是为了提供一种更精细、更直观的方式来控制复杂角色的动画混合，特别是当动画师需要根据角色的不同部位或骨骼层次来应用不同的混合参数时。

## 使用场景

- 你正在为一个拥有多段可独立动画的肢体（如机械臂、触手）的角色创建动画蓝图，并需要为每个段设置不同的混合强度。
- 你需要实现一个动画效果，其中角色的上半身和下半身对同一个混合输入（如移动速度）做出不同比例的反应。
- 动画师需要一个可视化工具来直观地查看和编辑每个骨骼节点在混合过程中的权重分布。

## 蓝图用法

该插件主要在动画蓝图编辑器中提供新的节点。核心功能通过 `UAnimGraphNode_BlendProfileLayeredBlend` 类暴露给蓝图编辑器。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FAnimNode_BlendProfileLayeredBlend` | 分层混合动画节点，根据混合配置文件对不同骨骼应用不同的混合权重。 | `UAnimGraphNode_BlendProfileLayeredBlend` |

### 使用示例（蓝图描述）

1.  在动画蓝图的 **AnimGraph** 中，右键点击并搜索 `Blend Profile Layered Blend` 节点。
2.  将此节点连接到 `Output Pose` 或其它节点。
3.  在节点的 **Details** 面板中，配置其属性：
    *   **Blend Profile**: 指定一个 `UHierarchyTable` 资产，该资产定义了骨骼到混合权重的映射关系。这是驱动分层混合的核心数据源。
    *   **Blend Time**: 设置混合过渡的时间。
    *   其它属性（如 `Blend Mode`）与标准的混合节点类似。
4.  为该节点的输入（Pose A, Pose B 等）连接不同的动画源。

## C++ 用法

### 头文件引入

```cpp
#include "AnimGraphNode_BlendProfileLayeredBlend.h"
```

### 基本用法

在C++中，你可以动态创建或修改 `UAnimGraphNode_BlendProfileLayeredBlend` 实例。以下是一个简化的示例，展示了如何获取动画蓝图中的该节点并修改其配置。

```cpp
// 假设 AnimBlueprintInstance 是一个有效的 UAnimInstance 指针
// 获取动画蓝图资产
UAnimBlueprint* AnimBlueprint = LoadObject<UAnimBlueprint>(nullptr, TEXT("/Game/ABP_MyCharacter"));
if (!AnimBlueprint) return;

// 获取 AnimGraph 并查找目标节点
UEdGraph* AnimGraph = AnimBlueprint->GetAnimGraph();
UAnimGraphNode_BlendProfileLayeredBlend* BlendNode = nullptr;
for (UEdGraphNode* Node : AnimGraph->Nodes)
{
    if (UAnimGraphNode_BlendProfileLayeredBlend* ProfileNode = Cast<UAnimGraphNode_BlendProfileLayeredBlend>(Node))
    {
        BlendNode = ProfileNode;
        break;
    }
}

if (BlendNode)
{
    // 修改节点属性 (示例)
    BlendNode->Node.BlendProfile = LoadObject<UHierarchyTable>(nullptr, TEXT("/Game/HT_MyBlendProfile"));
    BlendNode->Node.BlendTime = 0.2f;

    // 在编辑器环境下，可能需要通知节点属性已更改
    BlendNode->PostEditChange();
}
```

### 进阶用法

结合 `HierarchyTable` 插件的功能，你可以通过代码动态创建或修改驱动混合的 `HierarchyTable` 资产。

```cpp
// 创建或修改 HierarchyTable 资产
UHierarchyTable* HierarchyTable = NewObject<UHierarchyTable>(GetTransientPackage(), TEXT("DynamicBlendProfile"));
// ... 使用 HierarchyTable 插件的 API 来填充层次和权重数据 ...
// 然后将此资产赋值给 BlendNode->Node.BlendProfile
```

## Demo 示例

以下是一个简单的 C++ 示例，演示了如何创建一个包含 `UAnimGraphNode_BlendProfileLayeredBlend` 的动画蓝图。

**文件： MyAnimBlueprint.h**
```cpp
#pragma once
#include "Animation/AnimBlueprint.h"
#include "MyAnimBlueprint.generated.h"

UCLASS()
class UMyAnimBlueprint : public UAnimBlueprint
{
    GENERATED_BODY()
public:
    // 可以在此声明一些辅助函数或成员，用于管理动画蓝图逻辑
};
```

**文件： MyAnimBlueprint.cpp**
```cpp
#include "MyAnimBlueprint.h"
#include "AnimGraphNode_BlendProfileLayeredBlend.h"

void UMyAnimBlueprint::CreateBasicAnimGraph(UEdGraph* InGraph)
{
    // 这是一个示意性函数，展示如何在代码中添加节点
    // 在实际编辑器扩展中，通常通过 GraphSchema 和工厂来完成

    UAnimGraphNode_BlendProfileLayeredBlend* NewNode = NewObject<UAnimGraphNode_BlendProfileLayeredBlend>(InGraph);
    NewNode->CreateNewGuid();
    NewNode->PostPlacedNewNode();

    // 配置节点属性
    // NewNode->Node.BlendProfile = ...;
    // NewNode->Node.BlendTime = 0.3f;

    // 将节点添加到图中
    InGraph->AddNode(NewNode, /*bSelectNewNode=*/ false);

    // 创建输入输出引脚连接... (省略具体连接逻辑)
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationBlueprintLibrary` | 提供动画蓝图操作的库函数。 |
| `AnimGraph` | 提供动画图（AnimGraph）节点、引脚和编译相关的基础框架。 |
| `BlueprintGraph` | 提供蓝图图表的节点和连接基础，是 `AnimGraphNode` 的基类所在。 |
| `HierarchyTable` | 核心依赖，提供 `HierarchyTable` 资产类型和数据操作API。 |
| `Persona` | 提供动画蓝图编辑器、节点工厂和属性自定义界面支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `711fdc2f` | Add root space support to profile blend | 为配置文件混合节点添加根骨骼空间支持 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新动画混合配置文件相关功能 |
| 2025-10-20 | `beb220c7` | Fix loaded blend profile assets not updating the hierarchy when its skeleton's hierarchy has changed | 修复已加载的混合配置文件资产在骨架层次改变后不更新层次结构的问题 |
| 2025-10-09 | `71d54d3d` | Fix profile blend node crash due to cached data not being generated in some cases | 修复由于在某些情况下缓存数据未生成而导致配置文件混合节点崩溃的问题 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件从 Base 前缀重命名为 Default 前缀 |

### 维护评价

该插件是一个较新的实验性插件，创建于2024年底。从提交历史来看，它在过去一年多的时间里持续获得更新，包括新功能添加（根空间支持）和重要的稳定性修复（崩溃修复、数据同步问题修复）。最近的活跃更新表明该插件处于积极开发和维护阶段。

由于插件仍处于实验性状态（`IsExperimentalVersion=true`）且默认未启用（`EnabledByDefault=false`），其API和功能在未来版本中仍有变更的可能。建议在项目中进行评估性使用，并关注官方更新日志。

**结论**：✅ **推荐关注和使用**，特别适合需要高级骨骼混合控制的动画项目，但需注意其“实验性”状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation/Tests) (如果存在)