# UAF Layering

> Framework to define a layering setup in UAF（在 UAF 中定义层叠设置的框架）

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画层叠 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（层栈资产） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

`UAFLayering` 是 `Unreal Animation Framework (UAF)` 的一个实验性插件，它提供了一个框架，用于在 UAF 动画图系统之上构建和管理分层的动画混合。其核心目标是为动画师和开发者提供一个直观、可视化的方法来组合多个动画源，并通过图层混合（如叠加、混合权重、遮罩）来创建复杂的最终动画效果。

这个插件的存在是为了解决传统动画蓝图状态机在处理复杂、多层动画叠加时的复杂性问题。它将动画内容的“播放”（图层内容提供者）与“混合方式”（图层混合提供者）解耦，并通过一个可排序、可编辑的图层栈（Layer Stack）来管理这些图层，使得动画的混合逻辑更加清晰和易于维护。

## 使用场景

-   你需要为一个角色构建复杂的动画表现，例如在“跑步”基础动画上叠加“射击”上半身动画，再叠加“受伤”的面部表情和权重遮罩。
-   你需要一个可视化编辑器来管理动画的混合顺序和参数，而不是在动画蓝图节点中手动连接复杂的混合节点。
-   你正在使用 UAF 系统，并希望扩展其功能以支持类似于 Unity 中 Mecanim 层叠系统的概念。

## 蓝图用法

该插件主要通过其编辑器资产和运行时组件进行交互，直接暴露给蓝图的 UFUNCTION 较少，但通过编辑器操作创建的资产和组件可以在蓝图中使用。

### 核心节点（运行时）

由于插件主要面向编辑器和图编译，直接可用的运行时蓝图节点不多。核心交互发生在编辑器创建资产和图编译阶段。

| 节点 | 说明 | 所在类 |
|---|---|---|
| (通过层栈资产间接使用) | 在 UAF 控制器中评估编译好的图层栈，产生最终混合动画。 | `UUAFLayerStack` (资产) |

### 使用示例（蓝图描述）

1.  **创建层栈资产**：在内容浏览器中右键 -> Animation -> UAF Layer Stack。
2.  **编辑层栈**：双击资产打开专用编辑器。在此界面中：
    - 可以添加、删除、重排图层。
    - 为每个图层指定内容来源（如某个动画序列）。
    - 为每个图层配置混合模式、权重、遮罩、淡入淡出曲线等混合设置。
3.  **在 UAF 图中使用**：在 `AnimNext` 或 UAF 的动画图编辑器中，将编译好的“层栈”资产作为节点引入到动画图的执行流中。该节点会输出经过所有图层混合后的最终姿势。

## C++ 用法

该插件主要通过结构体继承和编辑器数据扩展进行集成，以下是关键的使用接口。

### 头文件引入

```cpp
#include “Layers/UAFLayer.h”
#include “Layers/UAFLayerStack_EditorData.h”
#include “LayeringUncookedOnlyTypes.h”
```

### 基本用法：理解图层创建上下文

在插件内部编译图层栈时，会创建一个 `FLayerCreationContext` 来传递图层创建所需的所有上下文信息。自定义内容/混合提供者需要使用此上下文。

*来源：`Public/LayeringUncookedOnlyTypes.h`*

```cpp
// 当实现自定义的图层内容或混合提供者时，您将接收到这个上下文结构体。
// 它包含了编译设置、图层栈、当前图层、图形控制器以及输入引脚等信息。
UE::UAF::Layering::FLayerCreationContext Context(CompileSettings);
Context.LayerStack = MyLayerStackAsset;
Context.Layer = CurrentLayerBeingProcessed;
Context.GraphController = MyAnimNextController;

// 上下文的 LayerInputs[0] 是前一个图层的输出姿势
// 上下文的 LayerInputs[1] 是当前图层内容的输出姿势
// 您需要将这些输入连接到您创建的节点上。
URigVMPin* PreviousLayerOutput = Context.LayerInputs[0];
```

### 进阶用法：创建自定义图层内容提供者

通过继承 `FUAFLayerContentProviderBase` 并实现其虚函数，可以创建全新的图层内容来源。

*来源：`Internal/Layers/UAFLayerContentProviderBase.h`*

```cpp
// 定义一个自定义内容提供者，例如用于程序化生成的动画
USTRUCT()
struct FMyProceduralContentProvider : public FUAFLayerContentProviderBase
{
    GENERATED_BODY()

    // 必须重写：在此函数中创建代表该图层内容的 RigVM 节点/特征。
    virtual URigVMPin* CreateLayerContentTrait(UE::UAF::Layering::FLayerCreationContext& LayerCreationContext) override
    {
        // 使用 LayerCreationContext.GraphController 添加节点
        // 例如，添加一个“程序化波形生成器”节点
        URigVMNode* ProceduralNode = LayerCreationContext.GraphController->AddUnitNode(/*...*/);
        
        // 连接该节点的输出到上下文中的层输入（通常连接到 LayerInputs[1]）
        URigVMPin* OutputPin = ProceduralNode->FindPin(TEXT(“Output”));
        LayerCreationContext.GraphController->AddLink(OutputPin, LayerCreationContext.LayerInputs[1]);
        
        // 返回该节点的最终输出引脚
        return OutputPin;
    }

    // 可选：为编辑器中的该图层提供自定义UI控件
    virtual TSharedRef<SWidget> CreateLayerContentWidget(UUAFLayer* InLayer) override
    {
        // 返回一个显示程序化参数（如频率、振幅）的Slate控件
        return SNew(STextBlock).Text(FText::FromString(“Procedural Settings”));
    }
};
```

## Demo 示例

以下示例展示了如何在 C++ 中定义一个简单的自定义混合提供者，该提供者修改图层的混合权重。

```cpp
// MyCustomBlendProvider.h
#pragma once

#include “Layers/UAFLayerBlendProviderBase.h”
#include “LayeringUncookedOnlyTypes.h”

USTRUCT()
struct FMyCustomWeightMultiplierBlend : public FUAFLayerBlendProviderBase
{
    GENERATED_BODY()

    virtual URigVMPin* CreateBlendGraphTrait(UE::UAF::Layering::FLayerCreationContext& LayerCreationContext) override
    {
        // 假设我们添加一个“乘法”节点来动态缩放图层权重
        if (LayerCreationContext.GraphController)
        {
            // 添加一个乘法节点
            URigVMNode* MultiplyNode = LayerCreationContext.GraphController->AddUnitNode(/*...*/);
            URigVMPin* MultiplyInputA = MultiplyNode->FindPin(TEXT(“A”));
            URigVMPin* MultiplyInputB = MultiplyNode->FindPin(TEXT(“B”));
            URigVMPin* MultiplyOutput = MultiplyNode->FindPin(TEXT(“Result”));

            // 将“前一个图层输出”（索引0）连接到乘法节点的A输入
            LayerCreationContext.GraphController->AddLink(LayerCreationContext.LayerInputs[0], MultiplyInputA);
            // 将“本层内容输出”（索引1）连接到乘法节点的B输入
            LayerCreationContext.GraphController->AddLink(LayerCreationContext.LayerInputs[1], MultiplyInputB);
            
            // 返回乘法节点的输出作为本层的最终输出
            return MultiplyOutput;
        }
        return nullptr;
    }

    virtual TSharedRef<SWidget> CreateLayerBlendWidget(UUAFLayer* OuterLayer) override
    {
        // 简单的文本标识
        return SNew(STextBlock).Text(FText::FromString(“Custom Weight Multiplier”));
    }

    // 公开的权重倍率参数
    UPROPERTY(EditAnywhere, Category = “Layer”)
    float WeightMultiplier = 1.0f;
};
```

## 模块依赖

该插件依赖于 UAF 和 Workspace 等特定模块，使用者需要在自己的模块构建文件中添加相应依赖。

| 模块 | 用途 |
|---|---|
| `Workspace` | 提供工作区编辑器集成和资产视图功能。 |
| `AnimNext` | UAF 的核心动画图框架，提供图控制器、编译环境等基础功能。 |
| `RigVM` | 提供 RigVM 图、节点、引脚等底层图形编程系统。 |
| `PropertyEditor` | 用于在自定义控件中显示和编辑属性。 |
| `InputCore` | 处理编辑器中的输入事件（如拖放）。 |
| `Slate` | 构建自定义编辑器UI（图层列表、控件等）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统迁移至新的 UE_LOGF 宏。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 重命名 GetComponent 为 GetOrAddComponent 以更准确描述其功能。 |
| 2026-03-05 | `dd5531fb` | UAF Layering: | UAF Layering 插件相关的提交（信息不完整）。 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新了 UAF 混合配置文件。 |
| 2026-03-04 | `95766f52` | UAF Layering: Expand outliner items per default | UAF Layering：默认展开大纲视图中的条目。 |

### 维护评价

`UAFLayering` 是一个非常新的实验性插件，创建于 2026 年初。从近期提交记录来看，它处于**活跃开发**状态，最近几个月持续有功能迭代（如大纲UI改进）、API清理（重命名、迁移日志）和系统更新（混合配置文件）。这表明 Epic 正在积极开发和测试该功能。

由于其 **`IsExperimentalVersion: true`** 和 **`EnabledByDefault: false`** 的状态，它目前还不适合用于生产环境，仅推荐用于原型开发、学习或实验性项目。API 可能会发生 breaking changes。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering/Tests)