# Blueprint Snap Nodes Prototype

> Prototype of an alternative way to lay out Blueprint nodes in a more compact manner

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图吸附节点原型 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlueprintSnapNodes` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintSnapNodes) | |

## 用途

Blueprint Snap Nodes 是 UE5 的一个实验性插件，旨在提供一种全新的、更紧凑的蓝图节点布局方式。传统的蓝图节点以自由放置、连线拖拽的方式工作，节点之间留有大量空白。该插件通过将节点“吸附”在一起，形成类似块状或行的紧凑排列，减少视觉混乱，提升编辑效率。它引入了一个新的节点类型 `UK2Node_SnapContainer`，作为容纳多个子节点的容器，并在编辑器中以特殊的小部件（`SGraphNodeSnapContainer`、`SGraphSnapContainerRow`）呈现。

该插件目前处于原型阶段，主要探索替代布局方案，并非生产就绪。

## 使用场景

- 当你希望将多个功能相关的蓝图节点组合成一个紧凑的“单元”，并整体进行拖拽、复制。
- 在复杂蓝图中，通过吸附减少节点间的空白区域，提高屏幕空间利用率。
- 用于实验性项目或引擎二次开发，探索蓝图的视觉编辑方式。

## 蓝图用法

该插件目前没有公开可直接在蓝图中调用的自定义函数或事件。所有节点类型均为编辑器专用节点，通过蓝图编辑器右键菜单创建。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Snap Container` | 创建一个吸附容器节点，内部可容纳多个子节点，并以紧凑布局显示 | `UK2Node_SnapContainer` |

#### 注意事项
- 该节点仅在编辑器蓝图菜单中可见，需要手动启用插件（`Edit > Plugins > Experimental > Blueprint Snap Nodes Prototype`）。
- 节点内部会自动组织子节点的排列方式，不支持用户自定义引脚的添加（`CanCreateUserDefinedPin` 返回 false）。

## C++ 用法

由于插件是实验性且主要面向编辑器，未提供直接供游戏逻辑引用的 API。以下为插件内部结构和扩展点。

### 头文件引入

```cpp
#include "BlueprintSnapNodes.h"
#include "K2Node_SnapContainer.h"
#include "SGraphNodeSnapContainer.h"
#include "SGraphSnapContainerRow.h"
```

### 基本用法（创建吸附节点）

插件通过 `UK2Node_SnapContainer::GetMenuActions` 在蓝图编辑器中注册了菜单项。若需在 C++ 中动态创建，需借助 `UBlueprint` 的节点创建接口：

```cpp
// 假设 MyBlueprint 是目标蓝图
UK2Node_SnapContainer* SnapNode = NewObject<UK2Node_SnapContainer>(MyBlueprint);
SnapNode->CreateNewGuid();
SnapNode->PostPlacedNewNode();
MyBlueprint->Graphs[0]->AddNode(SnapNode);
```

但更常见的方式是在编辑器布局中手动添加。

### 构建吸附容器 UI

`FGraphSnapContainerBuilder::CreateSnapContainerWidgets` 内部递归遍历节点连线，生成紧凑的 SWidget 布局：

```cpp
UEdGraph* Graph = /* 获取蓝图编译后的图表 */;
UEdGraphNode* RootNode = /* 容器内的根节点 */;
TSharedRef<SWidget> Widget = FGraphSnapContainerBuilder::CreateSnapContainerWidgets(Graph, RootNode);
```

### 自定义 Slate 小部件

`SGraphSnapContainerEntry` 负责处理拖拽、放置和工具提示，若需扩展吸附行为，可继承此类。

## Demo 示例

以下是一个 C++ 控制台模块的最小示例，演示如何通过代码创建吸附容器节点（需在编辑器环境下运行）。

### SnapNodeDemo.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FSnapNodeDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### SnapNodeDemo.cpp

```cpp
#include "SnapNodeDemo.h"
#include "K2Node_SnapContainer.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphSchema.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Engine/Blueprint.h"

IMPLEMENT_MODULE(FSnapNodeDemoModule, SnapNodeDemo)

void FSnapNodeDemoModule::StartupModule()
{
    // 注意：该示例只能在编辑器模块中运行，且需要有效的蓝图对象
    if (UBlueprint* Blueprint = Cast<UBlueprint>(StaticLoadObject(UBlueprint::StaticClass(), nullptr, TEXT("/Game/MyBlueprint"))))
    {
        UEdGraph* Graph = Blueprint->EventGraph;
        if (Graph)
        {
            UK2Node_SnapContainer* SnapNode = NewObject<UK2Node_SnapContainer>(Graph);
            SnapNode->SetFlags(RF_Transactional);
            SnapNode->CreateNewGuid();
            SnapNode->PostPlacedNewNode();
            SnapNode->AllocateDefaultPins();
            Graph->AddNode(SnapNode, true, true);

            // 将容器标记为根节点
            SnapNode->RootNode = SnapNode; // 示例中将容器自身作为根节点（通常应指定内部子节点）

            // 刷新蓝图编辑器
            FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
        }
    }
}

void FSnapNodeDemoModule::ShutdownModule()
{
}
```

## 模块依赖

使用本插件时，你的模块需在 `PublicDependencyModuleNames` 中添加以下独特依赖（标准 Core/Engine/Slate 等依赖已省略）：

| 模块 | 用途 |
|---|---|
| `BlueprintGraph` | 提供蓝图节点基类 `UK2Node` 和复合节点 `UK2Node_Composite` |
| `KismetCompiler` | 支持蓝图编译和节点重构 |
| `GraphEditor` | 提供 `SGraphNodeK2Base` 等编辑器 Slate 组件 |
| `KismetWidgets` | 提供 `SGraphPin` 等通用小部件 |

### 完整 Build.cs 示例

```cpp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "Slate",
    "SlateCore",
    "UnrealEd",
    "BlueprintGraph",
    "KismetCompiler",
    "GraphEditor",
    "KismetWidgets"
});
```

## 维护状态

### 近期更新

| 日期 | Commit | 解读 |
|---|---|---|
| 2025-12-17 | `8a277ed0` | 移除 `SNodePanel` 未使用的属性（编译清理） |
| 2025-10-07 | `bafb0226` | 修复非 Unity/PCH 编译缺少包含的问题 |
| 2025-04-09 | `e973f7aa` | 更新 GraphEditor 拖拽 API 使用 `FVector2f`（适配引擎升级） |
| 2025-03-31 | `515ec7cd` | 更新 `SNodePanel` 等类使用 `FVector2f`（适配引擎升级） |
| 2023-01-16 | `bbc37aa2` | 首次提交：添加 BlueprintSnapNodes 插件原型 |

### 维护评价

- **创建时间**：2023年1月（约3年）
- **最近更新**：2025年12月有编译清理，2025年10月/4月/3月有引擎 API 适配。
- **活跃度**：近一年内有更新，但均为配合引擎升级的被动修改，无功能性改进。插件本身仍是原型（IsExperimentalVersion=true），且默认不启用。
- **风险**：作为实验性功能，API 不稳定，可能在未来引擎版本中被移除或大幅改动。
- **推荐度**：**不推荐**用于生产项目。适合对蓝图编辑器扩展感兴趣的开发者进行研究和实验。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintSnapNodes)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Experimental/BlueprintSnapNodes)（可能不存在，插件未公开测试）