# Live Link Graph Node

> LiveLink allows streaming of animated data into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkGraphNode` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-03-24 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink/Source/LiveLinkGraphNode) | |

## 用途

`LiveLinkGraphNode` 模块是 Live Link 插件的核心组成部分，它**为动画蓝图（Animation Blueprint）和标准蓝图（Blueprint）提供了直接集成 Live Link 实时数据流的专用节点**。该模块解决的核心问题是：如何让设计师和开发者能够在可视化脚本环境中，方便地接收、评估和更新来自外部设备（如动作捕捉系统、虚拟摄像机等）的实时动画数据，并将其应用于角色或场景中。

它通过提供两种关键类型的节点来实现这一目标：
1.  **动画蓝图节点 (`UAnimGraphNode_LiveLinkPose`)**：允许在动画蓝图的动画图表中直接使用 Live Link 主题（Subject）的姿势数据来驱动角色动画。
2.  **蓝图节点 (`UK2Node_EvaluateLiveLinkFrame`, `UK2Node_UpdateVirtualSubjectDataBase`)**：允许在标准蓝图中评估 Live Link 帧数据或更新虚拟主题的数据，用于更通用的数据处理和逻辑控制。

## 使用场景

-   **实时动捕驱动角色动画**：你在使用 OptiTrack、Vicon 等动捕系统，希望将演员的实时表演直接映射到游戏中的角色模型上 → 在角色的动画蓝图中使用 `Live Link Pose` 节点。
-   **蓝图中获取实时数据**：你需要在游戏逻辑中根据来自外部设备（如面部捕捉头盔、数据手套）的实时数据来触发事件或改变物体状态 → 在蓝图中使用 `Evaluate Live Link Frame` 节点。
-   **创建和更新虚拟主题**：你正在开发一个需要聚合或处理多个 Live Link 数据源的系统，或者需要从蓝图动态设置虚拟主题的数据 → 使用 `Update Virtual Subject Data` 相关的蓝图节点。

## 蓝图用法

本模块提供的节点主要在动画蓝图和蓝图编辑器中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Live Link Pose` | 动画蓝图节点，使用指定 Live Link 主题的姿势数据驱动角色骨骼。 | `UAnimGraphNode_LiveLinkPose` |
| `Evaluate Live Link Frame` | 蓝图节点，评估指定角色和主题的 Live Link 帧数据，并输出对应的结构体。 | `UK2Node_EvaluateLiveLinkFrame` |
| `Update Virtual Subject Static Data` | 蓝图节点，用于更新虚拟主题的静态数据。 | `UK2Node_UpdateVirtualSubjectDataBase` (子类) |
| `Update Virtual Subject Frame Data` | 蓝图节点，用于更新虚拟主题的帧数据。 | `UK2Node_UpdateVirtualSubjectDataBase` (子类) |

### 使用示例（蓝图描述）

**动画蓝图中使用 Live Link Pose：**
1.  打开角色的动画蓝图，进入动画图表（AnimGraph）。
2.  从右键菜单搜索并添加 `Live Link Pose` 节点。
3.  在节点的细节面板中，设置 `Live Link Subject`（例如，选择你的动捕系统创建的主题）。
4.  将该节点的输出姿势连接到动画蓝图的最终姿势节点（如 `Output Pose`）。

**蓝图中评估 Live Link 数据：**
1.  在任意蓝图（如 Actor 蓝图）的事件图表中，右键搜索 `Evaluate Live Link Frame`。
2.  选择与你数据角色（如 `LiveLinkBasicRole`）对应的节点。
3.  连接 `Subject Name` 引脚（可以硬编码或从变量传入）。
4.  节点的 `Data` 输出引脚将包含该主题最新的帧数据结构体，你可以将其 Break 开来使用具体字段（如变换、缩放等）。
5.  使用 `Frame Not Available` 执行引脚处理数据不可用的情况。

## C++ 用法

本模块主要提供蓝图节点类，其 C++ 用法通常涉及在自定义动画节点或蓝图节点中继承和扩展这些基类。

### 头文件引入

```cpp
#include “AnimGraphNode_LiveLinkPose.h”
#include “K2Node_EvaluateLiveLinkFrame.h”
#include “K2Node_UpdateVirtualSubjectDataBase.h”
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个自定义的动画蓝图节点，该节点内部使用 `FAnimNode_LiveLinkPose`。

```cpp
// MyCustomAnimGraphNode.h
#pragma once

#include “AnimGraphNode_Base.h”
#include “AnimNode_LiveLinkPose.h” // 包含 Live Link 动画节点
#include “MyCustomAnimGraphNode.generated.h”

UCLASS()
class UMyCustomAnimGraphNode : public UAnimGraphNode_Base
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = Settings)
    FAnimNode_LiveLinkPose LiveLinkNode; // 内嵌一个 Live Link 动画节点

    //~ Begin UEdGraphNode Interface
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
    virtual FText GetTooltipText() const override;
    //~ End UEdGraphNode Interface

    //~ Begin UAnimGraphNode_Base Interface
    virtual FAnimNode_Base* GetTemplateNode() const override { return const_cast<FAnimNode_LiveLinkPose*>(&LiveLinkNode); }
    //~ End UAnimGraphNode_Base Interface
};
```
*（来源：基于 `UAnimGraphNode_LiveLinkPose` 的结构推断）*

### 进阶用法

要创建一个全新的、用于评估特定 Live Link 角色的蓝图节点，通常需要继承 `UK2Node_EvaluateLiveLinkFrame` 并实现其纯虚函数。

```cpp
// K2Node_EvaluateLiveLinkTransform.h
#pragma once

#include “K2Node_EvaluateLiveLinkFrame.h”
#include “K2Node_EvaluateLiveLinkTransform.generated.h”

UCLASS()
class UK2Node_EvaluateLiveLinkTransform : public UK2Node_EvaluateLiveLinkFrame
{
    GENERATED_BODY()

protected:
    // 指定此节点调用的底层评估函数
    virtual FName GetEvaluateFunctionName() const override;

    // 根据角色类型，添加额外的输出引脚（例如，单独输出旋转和位移）
    virtual void AddPins(FKismetCompilerContext& CompilerContext, UK2Node_CallFunction* EvaluateLiveLinkFrameFunction) override;
};
```
*（来源：基于 `UK2Node_EvaluateLiveLinkFrame` 的接口推断）*

## Demo 示例

一个最小化的、使用 `UAnimGraphNode_LiveLinkPose` 的动画节点示例。

```cpp
// SimpleLiveLinkAnimNode.h
#pragma once

#include “AnimGraphNode_LiveLinkPose.h”
#include “SimpleLiveLinkAnimNode.generated.h”

// 这是一个简单的包装节点，仅用于演示如何在动画蓝图中暴露 Live Link Pose
UCLASS(MinimalAPI)
class USimpleLiveLinkAnimNode : public UAnimGraphNode_LiveLinkPose
{
    GENERATED_BODY()

public:
    USimpleLiveLinkAnimNode()
    {
        // 可以在这里设置一些默认值
        Node.LiveLinkSubjectName = FName(“MyMocapSubject”);
    }

    //~ Begin UEdGraphNode Interface
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override
    {
        return FText::FromString(TEXT(“Simple Live Link Pose”));
    }

    virtual FText GetTooltipText() const override
    {
        return FText::FromString(TEXT(“A simple node that applies a Live Link pose.”));
    }
    //~ End UEdGraphNode Interface
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 Live Link 框架，提供主题、角色、连接器等基础类。 |
| `AnimGraph` | 动画蓝图图表和节点的基础框架。 |
| `BlueprintGraph` | 蓝图图表和 K2 节点的基础框架。 |
| `KismetCompiler` | 用于编译蓝图节点的扩展逻辑。 |

## 维护状态

### 近期更新

```
- 2057280165b3 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n
- c1d4eecb59dc Replaced bool arguments with EFindObjectFlags.
- 98a8e0e0df23 Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes
```
这三次提交均为代码维护性更新：修正 DLL 导出标记、替换过时的布尔参数、清理废弃的头文件包含宏。没有功能性新增或重大修复。

### 维护评价

`LiveLinkGraphNode` 模块自 2017 年随 Live Link 插件一同创建，已有约 8 年历史，属于“老古董”级别。作为 Live Link 生态系统的**核心蓝图集成层**，它依然被广泛使用且是必需的。

**评价**：
- **状态**：**维护中，但非活跃开发**。最近的提交（2025年）都是底层代码质量维护，表明 Epic 仍在确保其与新版引擎的兼容性，但没有新功能添加。
- **稳定性**：作为基础节点模块，其接口已非常稳定，是构建 Live Link 工作流的可靠基石。
- **推荐**：**强烈推荐使用**。如果你需要在动画蓝图或蓝图中使用 Live Link 数据，这是官方提供的标准且唯一的方式。尽管模块本身不常更新，但其依赖的 `LiveLink` 核心模块仍在持续演进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink/Source/LiveLinkGraphNode)
- [官方文档]()（.uplugin 中未提供 DocsURL）
- [测试用例]()（未在提供的路径中发现测试文件）