# Chaos Cloth Asset Editor

> Editor for modifying cloth assets（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ChaosClothAssetEditor` (Editor), `ChaosClothAssetEditorTools` (Runtime), `ChaosClothAssetTools` (Runtime), `ChaosClothAssetDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor) | |

## 用途

ChaosClothAssetEditor 是一个基于 Dataflow 框架的布料资产编辑器插件。它解决的核心问题是：为 UE5 的 Chaos 布料系统提供一个可视化、节点化的资产编辑工作流。传统的布料资产编辑可能依赖于复杂的参数面板或外部工具，而此插件将布料模拟的构建、修改和调试过程集成到一个基于节点的图（Dataflow Graph）中。用户可以通过连接不同的节点来定义布料的几何形状、物理属性、约束和动画驱动，从而直观地创建和迭代复杂的布料效果。它本质上是一个面向技术美术师和动画师的专用内容创作工具。

## 使用场景

- 你正在为游戏角色制作复杂的服装（如长袍、披风、裙子），需要精细控制布料的褶皱、飘动和碰撞效果。
- 你需要为场景中的旗帜、窗帘、帐篷等物体创建逼真的布料模拟。
- 你希望以非破坏性、可复用的方式定义布料资产，通过节点图清晰地管理各个属性（如刚度、阻尼、重力影响）。
- 你需要在编辑器中实时预览和调试布料模拟的结果，并快速调整参数。

## 蓝图用法

此插件主要提供编辑器工具和上下文对象，其核心功能通过编辑器工具（Editor Tools）和 Dataflow 节点图暴露，而非传统的蓝图函数库。以下是从源码中提取的关键可交互对象。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSingleSelectedNodeOfType<T>` | 获取当前在 Dataflow 图编辑器中选中的、指定类型的单个节点。如果未选中或选中多个则返回空。 | `UClothEditorContextObject` |
| `SetClothCollection` | 设置当前编辑器上下文中关联的布料集合数据（`FManagedArrayCollection`）及其视图模式。 | `UClothEditorContextObject` |
| `GetSelectedClothCollection` | 获取当前选中的布料集合数据。 | `UClothEditorContextObject` |
| `GetDataflowAsset` | 获取当前正在编辑的 Dataflow 资产。 | `UClothEditorContextObject` |
| `GetSupportedViewModes` | （工具构建器接口）查询特定编辑工具支持哪些布料构造视图模式（如顶点、边、面）。 | `IChaosClothAssetEditorToolBuilder` |

### 使用示例（蓝图描述）

由于此插件主要服务于编辑器扩展，其“蓝图用法”更侧重于在编辑器工具蓝图（Editor Utility Blueprint）或自定义编辑器模块中与上下文对象交互。典型流程如下：
1.  在编辑器工具或自定义面板中，获取当前 `UClothEditorContextObject` 实例。
2.  调用 `GetSingleSelectedNodeOfType` 并传入具体的节点类型（如 `FChaosClothAssetWeightMapNode`），以检查用户是否选中了某个权重绘制节点。
3.  根据返回的节点信息，更新UI或执行特定操作。
4.  使用 `SetClothCollection` 来响应用户在不同视图模式（如顶点选择模式、边选择模式）间的切换，更新编辑器的显示数据。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothEditorContextObject.h"
#include "ChaosClothAsset/ClothEditorToolBuilders.h"
```

### 基本用法

以下示例展示了如何在编辑器扩展代码中使用 `UClothEditorContextObject` 来查询当前选中的 Dataflow 节点。
*（来源：`ClothEditorContextObject.h`）*

```cpp
// 假设你已经获取了当前活动的 UClothEditorContextObject 指针 ContextObject
if (UClothEditorContextObject* ContextObject = GetActiveClothEditorContext())
{
    // 尝试获取用户选中的单个 FChaosClothAssetWeightMapNode 节点
    // 这是一个模板函数，可以传入任何 FDataflowNode 的子类
    if (FChaosClothAssetWeightMapNode* WeightMapNode = ContextObject->GetSingleSelectedNodeOfType<FChaosClothAssetWeightMapNode>())
    {
        // 成功获取到选中的权重绘制节点，可以读取其属性
        UE_LOG(LogTemp, Log, TEXT("Selected Weight Map Node: %s"), *WeightMapNode->GetName());
        // ... 进行后续操作，例如获取其权重图数据
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No single Weight Map node selected."));
    }
}
```

### 进阶用法

结合工具构建器接口 `IChaosClothAssetEditorToolBuilder`，可以创建自定义的布料编辑工具。以下是一个简化的自定义工具构建器示例。
*（来源：`ClothEditorToolBuilders.h`）*

```cpp
// MyClothToolBuilder.h
#pragma once
#include "ChaosClothAsset/ClothEditorToolBuilders.h"
#include "MyClothToolBuilder.generated.h"

UCLASS()
class UMyClothToolBuilder : public UInteractiveToolBuilder, public IChaosClothAssetEditorToolBuilder
{
    GENERATED_BODY()

public:
    // 实现 IChaosClothAssetEditorToolBuilder 接口
    virtual void GetSupportedViewModes(const UDataflowContextObject& ContextObject, TArray<UE::Chaos::ClothAsset::EClothPatternVertexType>& Modes) const override
    {
        // 声明此工具支持在“顶点”和“边”模式下工作
        Modes.Add(UE::Chaos::ClothAsset::EClothPatternVertexType::ClothVertex);
        Modes.Add(UE::Chaos::ClothAsset::EClothPatternVertexType::ClothEdge);
    }

    virtual bool CanSetConstructionViewWireframeActive() const override { return true; }

    // 实现 UInteractiveToolBuilder 接口
    virtual bool CanBuildTool(const FToolBuilderState& SceneState) const override
    {
        // 检查场景状态是否满足构建此工具的条件
        return true;
    }

    virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override
    {
        // 创建并返回你的自定义工具实例
        return NewObject<UMyClothTool>(SceneState.ToolManager);
    }
};
```

## Demo 示例

以下是一个最小化的自定义布料编辑工具构建器的头文件和实现文件示例。该工具仅用于演示如何集成到 ChaosClothAssetEditor 框架中。

**MySimpleClothToolBuilder.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "InteractiveToolBuilder.h"
#include "ChaosClothAsset/ClothEditorToolBuilders.h"
#include "MySimpleClothToolBuilder.generated.h"

UCLASS()
class UMySimpleClothToolBuilder : public UInteractiveToolBuilder, public IChaosClothAssetEditorToolBuilder
{
	GENERATED_BODY()

public:
	// IChaosClothAssetEditorToolBuilder Interface
	virtual void GetSupportedViewModes(const UDataflowContextObject& ContextObject, TArray<UE::Chaos::ClothAsset::EClothPatternVertexType>& Modes) const override;
	virtual bool CanSetConstructionViewWireframeActive() const override;

	// UInteractiveToolBuilder Interface
	virtual bool CanBuildTool(const FToolBuilderState& SceneState) const override;
	virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override;
};
```

**MySimpleClothToolBuilder.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MySimpleClothToolBuilder.h"
#include "MySimpleClothTool.h" // 假设你有一个对应的工具类

void UMySimpleClothToolBuilder::GetSupportedViewModes(const UDataflowContextObject& ContextObject, TArray<UE::Chaos::ClothAsset::EClothPatternVertexType>& Modes) const
{
	// 此简单工具仅支持在“顶点”视图模式下操作
	Modes.Add(UE::Chaos::ClothAsset::EClothPatternVertexType::ClothVertex);
}

bool UMySimpleClothToolBuilder::CanSetConstructionViewWireframeActive() const
{
	// 允许在工具激活时切换线框显示
	return true;
}

bool UMySimpleClothToolBuilder::CanBuildTool(const FToolBuilderState& SceneState) const
{
	// 在此添加你的工具是否可以构建的逻辑，例如检查是否有选中的布料资产
	return true;
}

UInteractiveTool* UMySimpleClothToolBuilder::BuildTool(const FToolBuilderState& SceneState) const
{
	UMySimpleClothTool* NewTool = NewObject<UMySimpleClothTool>(SceneState.ToolManager);
	// 在此初始化工具，例如传递场景状态或上下文对象
	return NewTool;
}
```

## 模块依赖

从模块名称和典型的 Chaos/Dataflow 工作流推断，使用此插件需要以下独特依赖。请在你的模块 `.Build.cs` 文件中添加。

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 提供布料资产的核心数据结构（如 `FManagedArrayCollection`）和运行时模拟逻辑。 |
| `Dataflow` | 提供 Dataflow 节点图框架、节点基类和图编辑器支持。 |
| `DataflowEditorTools` | 提供 Dataflow 编辑器工具的基础类和接口（如 `IDataflowEditorToolBuilder`）。 |
| `ChaosClothAssetEditorTools` | 本插件提供的编辑器工具和上下文对象模块。 |
| `ChaosClothAssetTools` | 提供布料资产相关的工具函数和操作。 |
| `ChaosClothAssetDataflowNodes` | 提供用于构建布料资产的 Dataflow 节点库。 |
| `ModelingToolsEditorMode` | （可能依赖）用于集成基于网格表面的交互式工具（如权重绘制）。 |

## 维护状态

### 近期更新

```
- 296af6582777 Dataflow : make sure we mark the dataflow package dirty when the tools are commiting their values - before this change editing a map without doing anything in the dataflow woudl not mark the package dirty and only modify the asset in memory but not on disk after saving
- 405ec08267b4 Dataflow : fix cloth transfer tool to better select the view mode based on the node parameters
- 1b857f7e5cd8 Cloth tool builder : fix assert when opening a selection tool in Dataflow - this is a side effect of a recent change
```

### 维护评价

- **创建时间**：2022年10月，相对较新的插件。
- **最近更新**：最近的提交（2025年）集中在修复 Dataflow 工具的脏标记、视图模式选择逻辑和断言错误，表明插件仍在积极维护和修复问题。
- **活跃状态**：**活跃维护中**。作为 Chaos 布料系统的重要编辑器组件，随着 UE5 Chaos 布料功能的迭代，此插件预计会持续更新。
- **已知限制**：`.uplugin` 中 `IsBetaVersion: true`，表明该插件仍处于 **Beta 测试阶段**，API 和功能可能发生变化，不建议在需要高度稳定的生产环境中直接依赖其内部实现。
- **推荐使用**：**推荐用于实验和内容创作**。对于需要使用 Chaos 布料系统并希望通过可视化节点图进行高效编辑的项目，此插件是官方提供的核心工具。但由于其 Beta 状态，使用者应关注版本更新日志，并准备好应对可能的接口变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor)
- [官方文档]() （暂无）
- [测试用例]() （测试用例可能位于 `Engine/Tests/` 目录下，具体路径需在源码仓库中查找）