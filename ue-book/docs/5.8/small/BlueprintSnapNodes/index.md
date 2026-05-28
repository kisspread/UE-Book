# Blueprint Snap Nodes Prototype

> Prototype of an alternative way to lay out Blueprint nodes in a more compact manner（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图吸附节点 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlueprintSnapNodes` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-04-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintSnapNodes) | |

## 用途

这个插件是 Epic Games 内部的一个实验性原型，旨在探索一种在蓝图编辑器中更紧凑地排列节点的方式。它不是一个生产就绪的系统，而是用于研究和开发新的蓝图用户体验。其核心思想是通过一个特殊的“容器”节点（`UK2Node_SnapContainer`）来封装和压缩一系列相关的蓝图节点，从而减少蓝图图表所占用的视觉空间，提高复杂蓝图的可读性和组织性。这个容器节点内部使用自定义的 Slate 控件（`SGraphSnapContainerEntry`、`SGraphNodeSnapContainer`）来以不同于传统节点引脚连接的方式显示内部结构和数据流。

## 使用场景

- 你正在开发一个大型蓝图，其中包含大量用于初始化或执行特定子任务的节点序列，导致图表非常冗长和杂乱 → 可以使用这个原型容器节点将这些节点组“吸附”在一起，形成一个更紧凑的区块。
- 你希望在不创建新的蓝图函数库的情况下，对蓝图逻辑进行视觉上的分组和封装，以提高可读性。
- **重要提示**：这是一个**原型**插件，其界面和功能可能会发生剧烈变化，且主要用于引擎内部开发和测试，不建议在正式项目中使用。

## 蓝图用法

该插件主要通过其定义的自定义蓝图节点在蓝图编辑器中交互，没有提供额外的、可在蓝图图表中直接调用的公开蓝图函数节点。其核心交互是创建和使用 `UK2Node_SnapContainer` 节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Snap Container` | 一个特殊的组合节点，用于将其他节点紧凑地吸附在一起。可以通过其右上角的“+”按钮或上下文菜单添加要吸附的节点。 | `UK2Node_SnapContainer` |

### 使用示例（蓝图描述）

1.  在蓝图编辑器中，右键打开节点创建菜单。
2.  搜索 “Snap Container” 或查找 “Blueprint Snap Nodes” 分类。
3.  放置一个 `Snap Container` 节点到图表中。
4.  点击容器节点右上角的 **“+”** 按钮，或者从容器节点的上下文菜单中选择，将其他现有的节点（如函数调用、变量设置等）“吸附”或移入到该容器中。
5.  被吸附的节点会显示在容器节点的内部区域，并以一种压缩的布局呈现。容器节点会自动生成必要的输入输出引脚，以连接外部逻辑。

## C++ 用法

该插件的公共 API 主要用于编辑器扩展和自定义节点行为，不直接暴露游戏运行时逻辑。

### 头文件引入

```cpp
#include “BlueprintSnapNodes/BlueprintSnapNodes.h”
// 以及用于节点定义的头文件，如果需要在自定义代码中操作该节点类型
#include “K2Node_SnapContainer.h”
```

### 基本用法

该插件在启动时会注册一个自定义的节点小部件工厂（`FBlueprintSnapNodeWidgetFactory`），以便蓝图编辑器能够正确地渲染 `UK2Node_SnapContainer`。

`UK2Node_SnapContainer` 是一个继承自 `UK2Node_Composite` 的蓝图节点。它重写了诸如 `AllocateDefaultPins`、`GetNodeTitle`、`UpdateGraphNode` 等方法，以定义其独特的外观和行为。它内部持有一个 `RootNode`（`UK2Node*`），作为被吸附节点图的起点。

一个典型的、用于创建这种自定义容器节点的结构如下（基于头文件分析）：

```cpp
// K2Node_SnapContainer.h
UCLASS()
class UK2Node_SnapContainer : public UK2Node_Composite
{
    GENERATED_BODY()
public:
    UPROPERTY()
    TObjectPtr<UK2Node> RootNode; // 内部图的根节点

    UK2Node_SnapContainer(const FObjectInitializer& ObjectInitializer);

    // 重写的蓝图节点核心接口
    virtual void AllocateDefaultPins() override;
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
    virtual void ReconstructNode() override;
    virtual void GetMenuActions(FBlueprintActionDatabaseRegistrar& ActionRegistrar) const override;
    // ... 其他重写方法
};
```

### 进阶用法

插件中的 Slate 控件负责将内部图以紧凑形式绘制出来。

- `FGraphSnapContainerBuilder`：这是一个工具类，通过 `CreateSnapContainerWidgets` 静态方法，为 `UK2Node_SnapContainer` 内部的每个节点和引脚创建对应的 Slate 小部件（`SGraphSnapContainerEntry`），这些小部件会以更节省空间的方式排列。
- `SGraphNodeSnapContainer`：这是 `UK2Node_SnapContainer` 在蓝图编辑器中的视觉表示。它重写了 `UpdateGraphNode()` 来创建自定义的节点主体（`CreateNodeBody()`），而不是使用标准的节点布局。

自定义节点容器的绘制逻辑大致如下：

```cpp
// SGraphNodeSnapContainer.h
class SGraphNodeSnapContainer : public SGraphNodeK2Base
{
public:
    void Construct(const FArguments& InArgs, UK2Node_SnapContainer* InNode);

    // 重写以自定义外观
    virtual void UpdateGraphNode() override;
    virtual TSharedPtr<SToolTip> GetComplexTooltip() override;

protected:
    virtual UEdGraph* GetInnerGraph() const;

private:
    // 创建压缩形式的节点主体
    TSharedRef<SWidget> CreateNodeBody();
};
```

## Demo 示例

以下示例展示如何在 C++ 中定义一个自定义节点，它使用类似 `SnapContainer` 的概念来管理其内部子图。这需要你创建自己的模块并注册节点。

**MySnapNode.h**
```cpp
#pragma once
#include "K2Node.h"
#include "MySnapNode.generated.h"

UCLASS()
class UMySnapNode : public UK2Node
{
    GENERATED_BODY()
public:
    // 存储要“吸附”的内部节点列表
    UPROPERTY()
    TArray<TObjectPtr<UK2Node>> SnapNodes;

    virtual void AllocateDefaultPins() override;
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
    virtual void GetMenuActions(FBlueprintActionDatabaseRegistrar& ActionRegistrar) const override;
    virtual FText GetMenuCategory() const override;

    // 添加一个节点到吸附列表
    UFUNCTION(BlueprintCallable, Category=“SnapNode”)
    void AddSnapNode(UK2Node* NodeToAdd);
};
```

**MySnapNode.cpp**
```cpp
#include “MySnapNode.h”

#define LOCTEXT_NAMESPACE “UMySnapNode”

void UMySnapNode::AllocateDefaultPins()
{
    // 根据吸附的节点和它们的引脚，动态创建容器节点的输入输出引脚
    // 这是一个复杂的逻辑，需要遍历所有 SnapNodes 并分析其引脚
    // 简化示例：创建一个执行引脚和一个数据引脚
    CreatePin(EGPD_Input, UEdGraphSchema_K2::PC_Exec, TEXT(“In”));
    CreatePin(EGPD_Output, UEdGraphSchema_K2::PC_Exec, TEXT(“Out”));
}

FText UMySnapNode::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
    return LOCTEXT(“MySnapNode”, “My Custom Snap Node”);
}

void UMySnapNode::GetMenuActions(FBlueprintActionDatabaseRegistrar& ActionRegistrar) const
{
    UClass* ActionKey = GetClass();
    if (ActionRegistrar.IsOpenForRegistration(ActionKey))
    {
        UBlueprintActionDatabaseRegistrar::FMakeActionDelegate Delegate;
        Delegate.BindLambda([]() -> UEdGraphNode* { return NewObject<UMySnapNode>(); });
        ActionRegistrar.AddBlueprintAction(ActionKey, Delegate);
    }
}

FText UMySnapNode::GetMenuCategory() const
{
    return LOCTEXT(“SnapCategory”, “Custom Snap Nodes”);
}

void UMySnapNode::AddSnapNode(UK2Node* NodeToAdd)
{
    if (NodeToAdd && !SnapNodes.Contains(NodeToAdd))
    {
        SnapNodes.Add(NodeToAdd);
        // 触发重建，以更新容器节点的引脚
        ReconstructNode();
    }
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

该插件作为编辑器原型，依赖于蓝图编辑和图表相关的模块。

| 模块 | 用途 |
|---|---|
| `KismetCompiler` | 蓝图编译器，用于处理自定义的 `UK2Node_SnapContainer` 节点的编译逻辑。 |
| `GraphEditor` | 图表编辑器框架，用于集成自定义的 Slate 节点控件（`SGraphNodeSnapContainer`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-12-17 | `8a277ed0` | Removing `SNodePanel`'s unused attributes | 引擎级图表面板代码清理，移除无用属性 |
| 2025-10-07 | `bafb0226` | Fixed non unity/pch by adding includes | 修复非统一头文件构建问题，添加缺失的include |
| 2025-04-09 | `e973f7aa` | [Truncation Warnings] Update GraphEditor Drag Drop Actions API to use FVector2f | 更新图表编辑器拖放接口，使用 FVector2f 消除类型转换警告 |
| 2025-03-31 | `515ec7cd` | [Truncation Warnings] Update SNodePanel, SGraphPanel and dependent classes to use FVector2f | 更新图表面板核心类，使用 FVector2f 消除类型转换警告 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的通用提交，无具体信息 |

### 维护评价

**BlueprintSnapNodes** 是一个典型的 Epic Games 内部实验性原型。它自 2022 年创建后，除了最初的迁移到实验性目录外，没有针对其自身功能的实质性更新。近期的提交全部是引擎级别的维护性更改（如解决编译警告、修复构建问题），并非该插件的功能迭代或 bug 修复。

- **年龄**：约 3 年，属于较新的实验。
- **更新频率**：非常低，仅有引擎级的间接维护。
- **维护状态**：**不活跃**。该插件作为原型，其开发很可能已经停滞，或者已被内部其他方案（如可能的未来版本）所取代。
- **已知限制**：代码标注为“Prototype”，接口和实现可能不稳定，缺乏文档和示例，且默认未启用。
- **推荐使用**：**不推荐在正式项目中使用**。仅适用于对 UE 蓝图编辑器内部工作机制感兴趣，或希望研究自定义节点布局技术的开发者学习和参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintSnapNodes)
- [官方文档]()（无）
- [测试用例]()（无）