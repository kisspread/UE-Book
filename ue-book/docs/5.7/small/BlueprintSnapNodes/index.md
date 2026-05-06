# Blueprint Snap Nodes Prototype

> Prototype of an alternative way to lay out Blueprint nodes in a more compact manner

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图快照节点 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlueprintSnapNodes` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-10 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BlueprintSnapNodes) | |

## 用途

Blueprint Snap Nodes 是一个**实验性的编辑器插件**，提供一种**更紧凑的蓝图节点布局方式**。它通过一个特殊的 `UK2Node_SnapContainer`（快照容器节点）将多个节点折叠为一个“快照”容器，在容器内部以紧凑的卡片式布局显示所有子节点的输入/输出引脚以及功能调用，从而有效减少蓝图编辑器的视觉混乱。该插件主要面向蓝图节点密集的复杂逻辑场景，作为传统平铺布局的替代方案。

## 使用场景

- 你需要整理一个**包含大量节点**的复杂蓝图函数/宏，希望**减少节点之间的空白**和滚动需求。
- 你想将一组逻辑上相关的节点**分组为一个可折叠的单元**，并在编辑器中以简洁的方式预览其内部逻辑。
- 你正在**创建自定义蓝图节点**，希望提供一种不同于默认布局的紧凑显示形式。

## 蓝图用法

该插件**不提供任何蓝图可调用的函数或可编辑属性**，它完全通过编辑器菜单和节点交互方式工作。你需要在“蓝图编辑器”中手动创建并使用 `Snap Container` 节点。

### 添加 Snap Container 节点

1. 在任何一个蓝图类的**事件图表**（Event Graph）或**函数图表**（Function Graph）中，**右键**打开上下文菜单。
2. 在搜索框中输入 `Snap Container`（或 `Snap`），选择出现的 **Snap Container** 节点。
3. 放置节点后，双击该节点（或从右键菜单中选择“编辑”），即可进入其内部子图（Sub-Graph）。子图默认是空的，你可以将其他蓝图节点粘贴或拖入其中。
4. 容器节点会自动以紧凑的卡片样式显示内部的所有引脚和节点标题。

### 节点交互

- **拖拽引脚**：从容器节点的输入/输出引脚拖拽连线，行为与普通节点一致。
- **工具提示**：鼠标悬停在容器节点上时，会显示内部子图的结构摘要。
- **重建**：当内部子图发生变化时（例如添加/删除节点），容器节点会自动刷新显示。

## C++ 用法

该插件本身以编辑器模块运行，开发者可以通过 C++ 在自定义的蓝图节点中启用类似的紧凑布局功能，或者直接内嵌 `FGraphSnapContainerBuilder` 构建自定义的紧凑控件。

### 头文件引入

```cpp
#include "K2Node_SnapContainer.h"
#include "SGraphSnapContainerRow.h"
```

### 基本用法：创建 Snap Container 节点

```cpp
// 在某个蓝图节点工厂或菜单动作中创建节点
UK2Node_SnapContainer* NewSnapNode = NewObject<UK2Node_SnapContainer>(Blueprint, UK2Node_SnapContainer::StaticClass());
NewSnapNode->CreateNewGuid();
NewSnapNode->PostPlacedNewNode();
// 设置根节点（可选）
NewSnapNode->RootNode = SomeRootNode;
```

### 进阶用法：使用 FGraphSnapContainerBuilder 展示子图

该构建器可以用于在**自定义的 Slate 控件**中渲染一个子图的紧凑卡片：

```cpp
// 假设你有 UEdGraph* SubGraph 和其中的某个节点作为根节点
UEdGraphNode* Root = ...;
TSharedRef<SWidget> CompactWidget = FGraphSnapContainerBuilder::CreateSnapContainerWidgets(SubGraph, Root);
// 将 CompactWidget 放置到你的自定义节点界面中
```

该构建器会递归地遍历子图节点，为每个节点生成一个紧凑的引脚块（`SGraphSnapContainerEntry`），从而形成一张完整的紧凑卡片。

## Demo 示例

以下是一个最小示例，展示如何在自定义模块的 `StartupModule` 中注册一个新的 `Snap Container` 类型节点（供蓝图使用）。

### .h

```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FMyCustomSnapExampleModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### .cpp

```cpp
#include "MyCustomSnapExampleModule.h"
#include "K2Node_SnapContainer.h"
#include "BlueprintActionDatabaseRegistrar.h"
#include "BlueprintNodeSpawner.h"

IMPLEMENT_MODULE(FMyCustomSnapExampleModule, MyCustomSnapExample);

void FMyCustomSnapExampleModule::StartupModule()
{
    // 注册自定义的快照节点（扩展默认的 SnapContainer 可能还需要继承 UK2Node_SnapContainer）
    // 这里仅作为示例，实际使用时建议继承 UK2Node_SnapContainer 并重写 GetMenuActions
}

void FMyCustomSnapExampleModule::ShutdownModule()
{
}
```

实际使用中，更常见的做法是**继承 `UK2Node_SnapContainer`**，然后在 `GetMenuActions` 中提供自定义的菜单项，以创建特定逻辑的快照节点。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `BlueprintGraph` | 提供 `UK2Node_Composite` 基类及相关蓝图图框架 |
| `KismetCompiler` | 用于编译快照节点内部子图 |
| `GraphEditor` | 提供 `SGraphNodeK2Base` 等编辑器 UI 组件 |
| ... | 其余依赖均为标准编辑器插件依赖（`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore` 等） |

**说明**：该插件依赖的模块均为蓝图编辑器中的常见模块，没有特殊的外部依赖。

## 维护状态

### 近期更新

- 2025-04-09 `e973f7aa` [Truncation Warnings] Update GraphEditor Drag Drop Actions API to use FVector2f
- 2025-03-31 `515ec7cd` [Truncation Warnings] Update SNodePanel, SGraphPanel and dependent classes to use FVector2f
- 2023-01-16 `bbc37aa2` [Engine/Plugins]  (大型目录整理)
- 2022-10-21 `610c4676` Update vendor links for built-in plugins to use secure protocol.
- 2022-09-10 `0eeac455` Pass 3 on cleaning up build.cs files.

### 维护评价

该插件自 2022 年 9 月创建以来，仅在 2023 年 1 月和 2025 年 Q1 有少量非功能性更新（主要是大型API重构适配）。**没有针对插件自身逻辑的新功能或 Bug 修复**。鉴于其标记为“实验性”且长时间处于低维护状态，该插件目前更倾向于一个**概念验证原型**，不建议在生产项目中直接依赖。如果你需要紧凑布局，可以考虑基于此代码自行扩展，或等待官方正式支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BlueprintSnapNodes)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/)（不包含本插件专门文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BlueprintSnapNodes/Source/BlueprintSnapNodes)（源码即测试）