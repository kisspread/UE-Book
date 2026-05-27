# Blend Stack

> Blend Stack API

| 属性 | 值 |
|---|---|
| 中文名 | 混合堆栈 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlendStack` (Runtime), `BlendStackEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/BlendStack) | |

## 用途

此插件提供了一套用于动画蓝图（Animation Blueprint）的高级混合系统。它引入了“混合堆栈”的概念，允许开发者在动画图中创建可嵌套、可复用的混合逻辑片段（Graphs）。这解决了在复杂动画状态机（Animation State Machine）中维护大量、重复性混合逻辑的难题，通过封装和复用混合图来提高动画蓝图的可读性和可维护性。

## 使用场景

- 你正在制作一个ARPG游戏，角色根据不同武器类型需要截然不同的攻击动画混合逻辑。你可以将每种武器的攻击动画混合逻辑封装为一个“混合堆栈”图，并在主状态机中根据装备状态动态切换。
- 你正在构建一个模块化的动画系统，希望将“移动”、“跳跃”、“受击”等常见动画混合逻辑提取出来，在不同角色或不同动画蓝图间共享。
- 你的动画状态机变得过于庞大和复杂，多个状态共享相似的混合逻辑，希望通过“混合堆栈”进行逻辑抽象和复用。

## 蓝图用法

本插件主要在**动画蓝图编辑器**中以节点形式使用。你需要手动启用此插件（`EnabledByDefault: false`）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Blend Stack` | 混合堆栈节点，是混合逻辑的载体。它内部包含一个独立的动画子图，该图通过“输入”节点接收外部动画数据，并输出混合结果。 | `UAnimGraphNode_BlendStack` |
| `Blend Stack Input` | 混合堆栈输入节点，定义在混合堆栈子图内部。用于将外部（如主状态机）的动画数据（如资产播放器的输出）接入到当前混合堆栈的逻辑中。 | `UAnimGraphNode_BlendStackInput` |

### 使用示例（蓝图描述）

1.  **创建混合堆栈图**：在动画蓝图的“我的蓝图”面板中，新建一个“混合堆栈图”（Blend Stack Graph）。这是一个独立的图资源。
2.  **编辑混合逻辑**：在新建的混合堆栈图中，你会看到一个`Blend Stack Input`节点和一个`Result`节点。你可以在这两个节点之间连接任意的动画逻辑（如蓝图混合节点、状态机等）。
3.  **使用混合堆栈**：返回主动画蓝图图表，在状态机内（或任何可以放置动画节点的地方），右键添加一个`Blend Stack`节点。
4.  **连接与配置**：在`Blend Stack`节点的细节面板中，选择你之前创建的混合堆栈图资产。然后将主图中其他动画节点（如序列播放器）的输出引脚连接到该节点的`输入`引脚。该节点的输出即为经过其内部逻辑混合后的动画。

## C++ 用法

本插件的C++ API主要面向编辑器扩展（`BlendStackEditor`模块），运行时部分（`BlendStack`模块）的节点结构由引擎动画系统内部处理。

### 头文件引入

```cpp
#include "AnimGraphNode_BlendStack.h"
```

### 基本用法

此插件提供的主要是UObject派生类，用于在动画蓝图编辑器中注册和操作节点。以下是如何在自定义编辑器代码中引用这些类的示例。

```cpp
// 来自: Engine/Plugins/Animation/BlendStack/Source/Editor/BlendStackEditor/Public/AnimGraphNode_BlendStack.h
// 引用一个混合堆栈节点实例
if (UAnimGraphNode_BlendStack* BlendStackNode = Cast<UAnimGraphNode_BlendStack>(AnimGraphNode))
{
    // 可以获取其内部定义的动画节点，进行运行时数据检查
    FAnimNode_BlendStack* RuntimeNode = &BlendStackNode->Node;
    // ... 进行一些操作
}

// 引用一个混合堆栈输入节点
if (UAnimGraphNode_BlendStackInput* InputNode = Cast<UAnimGraphNode_BlendStackInput>(AnimGraphNode))
{
    // 输入节点主要用于定义图内的数据接入点
    FAnimNode_BlendStackInput* RuntimeInputNode = &InputNode->Node;
}
```

### 进阶用法

如果你需要创建自定义的、类似于`Blend Stack`的动画图节点，可以继承自`UAnimGraphNode_BlendStack_Base`基类。

```cpp
UCLASS(MinimalAPI)
class UAnimGraphNode_MyCustomBlendStack : public UAnimGraphNode_BlendStack_Base
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = Settings)
    FAnimNode_MyCustomBlendStack Node; // 你需要定义对应的运行时动画节点

    // 必须实现基类的纯虚函数，返回你的运行时节点
    virtual FAnimNode_BlendStack_Standalone* GetBlendStackNode() const override
    {
        return (FAnimNode_BlendStack_Standalone*)(&Node);
    }

    // 重写其他虚函数以提供自定义行为，例如标题颜色、提示文本等
    virtual FLinearColor GetNodeTitleColor() const override { return FLinearColor::Red; }
    virtual FText GetTooltipText() const override { return NSLOCTEXT("MyBlendStack", "Tooltip", "My Custom Blend Stack"); }
    // ... 其他必要的重写
};
```

## Demo 示例

以下是一个最小化、可编译的自定义混合堆栈动画图节点示例。它演示了如何从基类派生。

**AnimGraphNode_MyCustomBlendStack.h**
```cpp
#pragma once

#include "AnimGraphNode_BlendStack.h"
#include "AnimNode_MyCustomBlendStack.h" // 假设你已定义运行时节点
#include "AnimGraphNode_MyCustomBlendStack.generated.h"

UCLASS(MinimalAPI)
class UAnimGraphNode_MyCustomBlendStack : public UAnimGraphNode_BlendStack_Base
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, Category = Settings)
	FAnimNode_MyCustomBlendStack Node;

	//~ Begin UAnimGraphNode_BlendStack_Base Interface
	virtual FAnimNode_BlendStack_Standalone* GetBlendStackNode() const override
	{
		return (FAnimNode_BlendStack_Standalone*)(&Node);
	}
	//~ End UAnimGraphNode_BlendStack_Base Interface

	//~ Begin UAnimGraphNode_AssetPlayerBase Interface
	virtual FLinearColor GetNodeTitleColor() const override { return FLinearColor::Green; }
	virtual FText GetTooltipText() const override
	{
		return NSLOCTEXT("AnimNode_MyCustomBlendStack", "Tooltip", "This is my custom blend stack node.");
	}
	virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override
	{
		return NSLOCTEXT("AnimNode_MyCustomBlendStack", "Title", "My Custom Blend Stack");
	}
	virtual FText GetMenuCategory() const override
	{
		return NSLOCTEXT("AnimNode_MyCustomBlendStack", "Category", "Custom Nodes");
	}
	//~ End UAnimGraphNode_AssetPlayerBase Interface
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimGraph` | 动画蓝图图表和节点的基础框架 |
| `BlueprintGraph` | 蓝图和动画图的编辑器图表逻辑支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF，属于代码规范化重构。 |
| 2026-01-27 | `62ce2078` | BlendStack - logging errors in FAnimNode_BlendStack_Standalone::InternalBlendTo if inconsistent an E | 在混合切换逻辑中添加错误日志，提升问题诊断能力。 |
| 2026-01-22 | `1d9e2356` | BlendStack - sync group support for follower blendstacks | 为跟随者混合堆栈添加同步组支持，增强功能。 |
| 2026-01-09 | `520bb55e` | PoseSearch - fix for misspelled words | 修复拼写错误，可能涉及相关注释或标识符。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件模板从Base重命名为Default，符合UE5新规范。 |

### 维护评价

该插件创建于2024年初，至今约一年多。从最近的提交记录看，它仍处于**活跃维护**状态。更新内容包括功能增强（如添加同步组支持）、错误修复和代码质量改进。虽然默认未启用，但这更可能是由于其专业性和对特定工作流的支持，并不代表项目被废弃。它作为动画蓝图功能的一部分，持续得到更新。推荐有复杂动画混合需求的项目评估并使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/BlendStack)