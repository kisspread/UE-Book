# Editor DataflowGraph

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 数据流图编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资源） |
| 模块 | `DataflowAssetTools` (Runtime), `DataflowEditor` (Runtime), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow) | |

## 用途

Dataflow 插件提供了一套**可视化节点图编辑器**（Dataflow Graph），用于定义和执行**数据流工作流**。它允许用户通过拖拽节点、连接引脚的方式，将一组数据处理步骤（如几何体转换、属性计算、仿真输入）组合成一个可复用的图表。

核心机制是**构造（Construction）** 与**模拟（Simulation）** 两套视图：

- **构造视图**：在编辑器中实时预览数据流的静态输出（网格、碰撞体等）。
- **模拟视图**：与动画序列或物理模拟联动，预览动态效果。

该插件主要服务于需要**程序化几何内容**（如 Chaos 破碎、布料模拟、骨架编辑）的开发者，为高级用户提供了比蓝图更底层、更专注于数据流动的编辑环境。

## 使用场景

- 为角色创建**动态的碰撞体或布料几何体**，并与动画系统集成。
- 定义**复杂的网格处理流程**（如重新拓扑、属性映射），并实时预览每个步骤的输出。
- 制作**可复用的数据流模板**，在多个资产之间共享处理逻辑。
- 需要**精细控制网格顶点属性**（如权重、颜色）时，结合笔刷工具进行编辑。

## 蓝图用法

> 本模块为编辑器插件，不直接暴露蓝图可调用节点。蓝图层面主要通过 `DataflowEnginePlugin` 模块提供的 `UDataflow` 组件进行交互，例如在蓝图函数中执行已编译的 Dataflow 图。

### 核心节点（编辑器扩展）

插件为详情面板提供了多种**属性类型自定义**（PropertyCustomization），用于提升节点 UI 的编辑体验。这些自定义在编辑器内部自动应用，无需手动调用。

| 节点/自定义 | 说明 | 所在类 |
|---|---|---|
| `FAnyTypeCustomization` 系列 | 为 `FDataflow` 中的泛型属性（数字、布尔、字符串、向量等）提供专用编辑控件。 | `UE::Dataflow::FAnyTypeCustomizationBase` |
| `FFreezeActionsCustomization` | 为节点上的“冻结”操作添加按钮 UI。 | `UE::Dataflow::FFreezeActionsCustomization` |
| `FFunctionPropertyCustomization` | 为节点结构中的函数引脚生成调用按钮。 | `UE::Dataflow::FFunctionPropertyCustomization` |
| `FPropertyGroupCustomization` 系列 | 自动填充属性组名称（如标量顶点组），避免手动输入。 | `UE::Dataflow::FScalarVertexPropertyGroupCustomization` |

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/DataflowAssetEditUtils.h"
#include "Dataflow/DataflowObjectInterface.h"
#include "Dataflow/DataflowEditorUtil.h"
```

### 基本用法 – 程序化添加节点

在编辑器工具或自动测试中，可以使用 `UE::Dataflow::FEditAssetUtils` 静态方法操作 Dataflow 图。

```cpp
// 文件：Private/Dataflow/DataflowAssetEditUtils.h

// 获取目标图（假设已获得 UDataflow* MyDataflow 和 UEdGraph* EdGraph）
using namespace UE::Dataflow;

// 1. 在图的指定位置添加一个节点
const FVector2D Location(100, 200);
const FName NodeName("MyCustomNode");
const FName NodeTypeName("FMyDataflowNodeType");  // 需注册的节点类型
UDataflowEdNode* NewNode = FEditAssetUtils::AddNewNode(
    EdGraph,
    Location,
    NodeName,
    NodeTypeName,
    nullptr // FromPin：可自动连接源引脚
);

// 2. 删除一组节点
TArray<UEdGraphNode*> NodesToDelete = { SomeNode };
FEditAssetUtils::DeleteNodes(EdGraph, NodesToDelete);

// 3. 复制节点到剪贴板
int32 NumCopied = 0;
FEditAssetUtils::CopyNodesToClipboard(NodesToCopy, NumCopied);
```

### 基本用法 – 渲染节点输出

在构造视图中，可通过 `UE::Dataflow::RenderNodeOutput` 获取节点的渲染数据。

```cpp
// 文件：Private/Dataflow/DataflowEditorUtil.h

GeometryCollection::Facades::FRenderingFacade RenderingFacade(Collection);
const UDataflowEdNode& Node = ...;
const UDataflowBaseContent& Content = ...;
bool bEvaluateOutputs = true;

bool bShouldDirectlyRender = UE::Dataflow::RenderNodeOutput(
    RenderingFacade,
    Node,
    Content,
    bEvaluateOutputs
);
// 如果返回 true，则 RenderingFacade 可直接用于绘制
```

### 进阶用法 – 自定义选项卡与子图

`FDataflowEditorSubGraphTabSummoner` 用于为每个子图（`UDataflowSubGraph`）生成独立的文档标签页。

```cpp
// 文件：Private/Dataflow/DataflowEditorSubGraphTabSummoner.h

// 在 FDataflowEditorToolkit 中创建
TSharedRef<FDataflowEditorSubGraphTabSummoner> SubGraphSummoner =
    MakeShared<FDataflowEditorSubGraphTabSummoner>(
        SharedThis(this),
        FDataflowEditorSubGraphTabSummoner::FOnCreateGraphEditorWidget::CreateLambda(
            [this](TSharedRef<FTabInfo>, UDataflowSubGraph* SubGraph) -> TSharedRef<SGraphEditor>
            {
                return CreateGraphEditorForSubGraph(SubGraph);
            }
        )
    );
```

## Demo 示例

以下最小示例演示如何通过 C++ 创建一个 `UDataflow` 资产并添加一个节点。需要在编辑器模块中运行。

### DataflowAssetExample.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Dataflow/DataflowAssetEditUtils.h"
#include "Dataflow/DataflowObject.h"

class FDataflowAssetExample
{
public:
    static void CreateAndEditDataflow(UObject* Outer, FName AssetName);
};
```

### DataflowAssetExample.cpp

```cpp
#include "DataflowAssetExample.h"
#include "Dataflow/DataflowEdNode.h"
#include "EdGraph/EdGraph.h"

void FDataflowAssetExample::CreateAndEditDataflow(UObject* Outer, FName AssetName)
{
    // 1. 通过工厂创建 Dataflow 资产
    UDataflow* Dataflow = NewObject<UDataflow>(Outer,AssetName, RF_Public | RF_Standalone);
    Dataflow->AddToRoot(); // 避免 GC

    // 2. 获取默认的主图（UEdGraph）
    UEdGraph* MainGraph = Dataflow->GetMainGraph();

    // 3. 添加一个节点（假设已注册类型 "FMyTestNode"）
    const FVector2D Location(0, 0);
    UDataflowEdNode* NewNode = UE::Dataflow::FEditAssetUtils::AddNewNode(
        MainGraph,
        Location,
        FName("TestNode"),
        FName("FMyTestNode"),
        nullptr
    );

    // 4. 标记资产已修改
    Dataflow->MarkPackageDirty();
}
```

**注意**：此示例需要 `Dataflow` 模块（核心）以及 `DataflowNodes` 模块已注册节点类型。

## 模块依赖

> 以下依赖基于代码中的 `#include` 引用和标准编辑器插件结构推断。未提供 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `DataflowEnginePlugin` | 提供运行时 `UDataflow` 组件及蓝图交互支持 |
| `DataflowNodes` | 定义可用的节点类型（如几何体运算、属性操作） |
| `AdvancedPreviewScene` | 构造/模拟视口中的预览场景（光照、环境） |
| `PropertyEditor` | 用于节点属性面板的自定义化（FDataflowAssetViewerSettingsCustomization 等） |
| `GeometryCollection` | 渲染节点输出时使用的几何体集合数据结构 |
| `DynamicMesh` | 动态网格组件 (`UDataflowEditorCollectionComponent`) 的渲染 |
| `UnrealEd` | 编辑器通用功能（资产定义、工厂、事务） |
| `SceneOutliner` | 数据流大纲视图 (`FDataflowOutlinerMode`) |
| `SequencerWidgets` | 模拟时间轴控件 (`SDataflowSimulationTimeline`) |

**无特殊依赖（仅标准 Core/Engine/Slate 等）**：已省略。

## 维护状态

### 近期更新

- 2025-11-18 `296af658` 确保数据流工具提交值时标记包脏
- 2025-10-16 `8b858c13` 取消搁置待处理更改
- 2025-10-03 `7f04ddbd` 修复取消关闭请求导致预览 Actor 被删除的问题
- 2025-10-03 `71e223a6` Dataflow 杂项更新
- 2025-10-02 `aba7c452` 临时禁用慢速任务进度通知（避免焦点问题）

### 维护评价

该插件创建于 **2025-10-02**，距今不足 3 个月，属于全新的实验性功能。近期更新频率较高（几乎每月都有提交），且修复了明显的关闭崩溃和 UI 焦点问题，表明团队正在积极迭代。尽管版本号为 0.1（预发布状态），但已有较完整的编辑器功能（构造/模拟视图、节点编辑、时间线、笔刷工具）。**推荐有 C++ 编辑器扩展需求的开发者试用**，但需注意其 API 可能在未来版本中变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/dataflow-in-unreal-engine/)（如已发布）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow/Tests)（假设存在）