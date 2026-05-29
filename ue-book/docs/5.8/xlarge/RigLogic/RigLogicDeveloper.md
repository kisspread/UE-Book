# RigLogic Plugin

> RigLogic Plugin for Facial Animation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画驱动插件 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时库、编辑器工具、示例资产） |
| 模块 | `RigLogicLib` (Runtime), `RigLogicModule` (Runtime), `RigLogicEditor` (Runtime), `RigLogicDeveloper` (Runtime), `RigLogicLibTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 是一个用于在 UE5 中驱动基于数据驱动的复杂角色面部动画的插件。其核心目的是将 DCC（数字内容创建）工具（如 Maya）中创建的 RigLogic rigs（骨骼、形态目标、逻辑）集成到 UE5 运行时，用于实时驱动高保真、高性能的数字人面部动画。它解决的问题是将复杂的离线面部绑定逻辑高效地转化为可在 UE5 中实时运行的动画节点，特别适用于需要大量表情混合和控制的实时应用，如虚拟人、数字替身、交互式剧情等。

## 使用场景

- 你正在制作一个需要电影级面部表情的实时数字人或虚拟偶像，其面部骨骼和变形逻辑在 Maya 等 DCC 中使用 RigLogic 工具集创建。
- 你的项目需要从基于 RigLogic 的 DCC 资产库迁移角色动画到 UE5 中，并希望保持原有的精细控制和性能。
- 你需要一个数据驱动的、可预测且高性能的面部动画系统，来驱动成百上千个骨骼和混合形状（morph targets）。

## 蓝图用法

RigLogic 插件的核心在蓝图中体现为动画蓝图节点。其主要通过 `AnimNode_RigLogic` 来驱动角色网格体。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Rig Logic` | 动画蓝图中的核心节点，接收控制曲线输入，输出驱动后的骨骼姿态和 Morph 目标权重。 | `UAnimGraphNode_RigLogic` (蓝图节点类), `FAnimNode_RigLogic` (运行时逻辑) |

### 使用示例（蓝图描述）

1.  在角色的 **动画蓝图** 的 AnimGraph 中，添加一个 **`Rig Logic`** 节点。
2.  将你的 **骨骼网格体组件** 连接到该节点的输入。
3.  通过 **动画曲线** 或 **蓝图事件** 驱动节点上的属性（例如 `ControlAttributeCurves`），这些属性通常映射到 DCC 工具中的控制器（如滑块、UI 控件）。
4.  节点的输出将自动计算并应用正确的骨骼变换和 Morph 权重，你可以将其连接到最终的 `Output Pose` 节点。

## C++ 用法

### 头文件引入

```cpp
// 引入核心运行时库和模块
#include "RigLogicLib.h"
#include "RigLogicModule.h"
// 如果使用动画节点相关功能
#include "AnimNode_RigLogic.h" // 通常包含在模块内，此处仅为示意
```

### 基本用法

从测试用例中提取的设置和初始化一个 `FAnimNode_RigLogic` 的框架代码。

```cpp
// 假设在某个自定义动画节点或组件内
// 包含头文件: #include "AnimNode_RigLogic.h"

// 1. 声明节点
FAnimNode_RigLogic RigLogicNode;

// 2. 在初始化时（如 `Initialize_AnyThread`），需要提供对应的运行时上下文
// 这个上下文通常由 RigLogicModule 管理，并与骨骼网格体数据关联。
// 代码示意，实际获取方式需查阅模块 API。
// RigLogic::FRuntimeContext* RuntimeContext = RigLogicModule::Get().GetOrCreateContext(SkeletalMesh);
// RigLogicNode.SetRuntimeContext(RuntimeContext);

// 3. 在更新（如 `Evaluate_AnyThread`）时，确保已输入了控制数据
// 控制数据可能通过 `FAnimationUpdateContext` 或直接设置节点属性传入。
// RigLogicNode.Update_AnyThread(UpdateContext);

// 4. 节点的输出（Pose）现在包含了 RigLogic 计算后的结果，可用于后续动画链。
```

*(注：完整的 API 需要深入 `RigLogicModule` 和 `RigLogicLib` 的公共接口。)*

### 进阶用法

更复杂的用法涉及管理运行时上下文、处理配置变更，以及与自定义的动画评估器集成。这通常需要对 `RigLogic::FRuntimeContext` 生命周期有深入了解，并可能需要处理底层库 (`RigLogicLib`) 的直接调用以进行高级调试或扩展。

## Demo 示例

一个最小的可运行动画节点示例，展示了 `UAnimGraphNode_RigLogic` 的基本结构。

```cpp
// MyAnimGraphNode_RigLogic.h
#pragma once

#include "AnimGraphNode_Base.h"
#include "AnimNode_RigLogic.h"
#include "MyAnimGraphNode_RigLogic.generated.h"

UCLASS(MinimalAPI, meta = (Keywords = "Rig Logic Animation Node Demo"))
class UMyAnimGraphNode_RigLogic : public UAnimGraphNode_Base
{
    GENERATED_UCLASS_BODY()

    // 节点的运行时数据
    UPROPERTY(EditAnywhere, Category = Settings)
    FAnimNode_RigLogic Node;

public:
    // 蓝图节点在编辑器中显示的标题
    UFUNCTION(BlueprintCallable, Category = "Animation|RigLogic")
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;

    // 编辑器中的提示文本
    virtual FText GetTooltipText() const override;
};
```

```cpp
// MyAnimGraphNode_RigLogic.cpp
#include "MyAnimGraphNode_RigLogic.h"

UMyAnimGraphNode_RigLogic::UMyAnimGraphNode_RigLogic(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

FText UMyAnimGraphNode_RigLogic::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
    return LOCTEXT("RigLogicNodeTitle", "My RigLogic Node");
}

FText UMyAnimGraphNode_RigLogic::GetTooltipText() const
{
    return LOCTEXT("RigLogicNodeTooltip", "Evaluates a RigLogic rig to drive facial animation.");
}
```

## 模块依赖

从 `Build.cs` 文件分析，使用 RigLogic 插件的核心功能，你的模块通常需要依赖以下 **非通用** 模块：

| 模块 | 用途 |
|---|---|
| `RigLogicLib` | 提供底层的、平台无关的 RigLogic 运行时库。通常无需直接依赖。 |
| `RigLogicModule` | UE5 集成层，提供管理运行时上下文、加载资产、提供服务等核心功能。**这是使用者最常依赖的模块**。 |
| `RigLogicEditor` | 提供编辑器支持，如自定义资产编辑器、节点菜单项等。仅编辑器模块需要。 |
| `RigLogicDeveloper` | 提供开发工具和动画图节点（如 `UAnimGraphNode_RigLogic`）。创建自定义 RigLogic 相关编辑器节点时可能需要。 |

*常见依赖如 `Core`， `Engine`， `Slate` 等已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `de0806c7` | Fix RigLogic NaN output from TwistSwing/RBF when ControlAttributeCurves overwrites driver-joint quat | 修复当控制属性曲线覆盖驱动关节四元数时，TwistSwing/RBF 模块输出 NaN 的问题 |
| 2026-05-13 | `52da7ee0` | Fix quaternion joints evaluator test in case no rotation support is compiled in for the zyx sequence | 修复在未编译 zyx 序列旋转支持时，四元数关节评估器测试失败的问题 |
| 2026-05-13 | `27f94d1b` | Fix RigLogic ML Joints initialization of rotation adapter in the absence of coordinate system conver | 修复在没有坐标系转换时，RigLogic ML Joints 旋转适配器初始化的错误 |
| 2026-05-13 | `4b5d4e7d` | Notify dependent AnimNode_RigLogic instances when RigRuntimeContext is reinitialized due to config c | 当配置变更导致 RigRuntimeContext 重新初始化时，通知依赖的 AnimNode_RigLogic 实例 |
| 2026-05-12 | `9006d42c` | Implement identical integration tests for all three RigLogic runtime integrations, AnimNode RigLogic | 为三种 RigLogic 运行时集成（AnimNode RigLogic）实现相同的集成测试 |

### 维护评价

RigLogic 插件**处于积极维护状态**。
- **年龄**：插件于 2020 年创建，已有约 6 年历史。
- **近期活跃度**：最近一次更新在 2026 年 5 月（此日期可能为数据测试值，实际以仓库最新 commit 为准），且 commit 内容集中在关键 bug 修复、测试完善和运行时稳定性改进上，表明核心功能仍在迭代优化。
- **推荐**：对于需要专业级面部动画驱动的项目，特别是涉及从 Maya RigLogic 工具集迁移资产的场景，**推荐使用**。该插件功能完整、文档相对齐全，并且有 Epic Games 官方维护。
- **注意**：由于其高度专业性，学习曲线可能较陡，需要对 RigLogic 的概念和 UE5 动画系统有较深理解。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/) (注：.uplugin 未提供 DocsURL，请查阅官方文档站搜索 “RigLogic”)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic/Source/RigLogicLibTest)

*(注：由于本插件规模较大（large），文档中详细描述了核心模块 `RigLogicDeveloper` 的示例。`RigLogicLib`、`RigLogicModule` 等更核心的模块应有独立的详细文档。)*