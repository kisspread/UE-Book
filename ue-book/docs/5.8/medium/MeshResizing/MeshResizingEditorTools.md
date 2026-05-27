# Mesh Resizing

> Mesh Resizing（网格调整）

| 属性 | 值 |
|---|---|
| 中文名 | 网格调整工具 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

该插件提供了一套基于地标的网格调整工具，主要用于在编辑器中通过交互式方式选择和操作网格上的关键点（地标），以实现网格的包裹或形状调整。其核心功能体现在 `UMeshWrapLandmarkSelectionTool` 上，它允许用户在目标网格上选择顶点作为“地标”，并利用这些地标来引导或控制另一个网格的变形过程（例如将基础网格适配到扫描数据）。这在数字人创建、虚拟角色定制或需要将通用网格适配到特定形状的场景中非常有用。

## 使用场景

- 你在创建数字人或虚拟角色，需要将一个基础面部或身体网格调整并适配到一套特定的扫描数据或手绘的目标形状。
- 你在进行虚拟试衣或角色装备制作，需要将服装网格紧密地包裹到角色身体网格上。
- 你需要一种直观的、基于关键点选择的方式来驱动网格的形状变化，而不是依赖复杂的参数化调整。

## 蓝图用法

该插件的工具类主要通过蓝图暴露其属性，供编辑器界面（如资产编辑器或自定义工具）交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Landmarks` | 获取或设置地标列表，包含标识符和对应的顶点索引。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `CurrentEditableLandmark` | 获取或设置当前正在编辑的地标的索引。值为 -1 或按住 Shift 键时为添加新地标状态。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `bShowVertices` | 控制在工具视图中是否显示网格顶点。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `bShowEdges` | 控制在工具视图中是否显示网格边。 | `UMeshWrapLandmarkSelectionToolProperties` |

### 使用示例（蓝图描述）

1.  **创建工具实例**：通过 `UMeshWrapLandmarkSelectionToolBuilder` 创建一个 `UMeshWrapLandmarkSelectionTool` 实例。这通常由编辑器的交互工具框架自动完成。
2.  **配置工具属性**：在工具激活后，获取其 `ToolProperties` 对象（类型为 `UMeshWrapLandmarkSelectionToolProperties`）。
3.  **设置地标数据**：在蓝图中，你可以修改 `Landmarks` 数组，添加或移除 `FMeshWrapToolLandmark` 结构体，为每个地标的 `Identifier` 赋值并关联一个 `VertexIndex`。
4.  **控制交互**：设置 `CurrentEditableLandmark` 来指定当前编辑的地标，或设置为 -1 进入添加模式。用户可以在视口中使用 Shift 和 Ctrl 键快速切换模式。
5.  **视图辅助**：根据需要切换 `bShowVertices` 和 `bShowEdges` 来优化视口中的网格显示。

## C++ 用法

### 头文件引入

```cpp
#include "MeshResizing/MeshWrapLandmarkSelectionTool.h"
#include "MeshResizing/MeshResizingToolActionCommandBindings.h"
```

### 基本用法

以下代码展示了如何以 C++ 方式与工具属性交互，这与蓝图中通过 `ToolProperties` 对象操作的逻辑一致。

```cpp
// 假设我们已经获得了一个有效的 UMeshWrapLandmarkSelectionTool* 实例指针 (例如通过工具管理器)
UMeshWrapLandmarkSelectionTool* LandmarkTool = ...;

// 获取其属性对象
UMeshWrapLandmarkSelectionToolProperties* ToolProps = LandmarkTool->GetToolProperties();

if (ToolProps)
{
    // 在地标的起始位置添加一个新地标
    FMeshWrapToolLandmark NewLandmark;
    NewLandmark.Identifier = TEXT("ChinTip");
    NewLandmark.VertexIndex = 1234; // 假设的顶点索引
    ToolProps->Landmarks.Add(NewLandmark);

    // 将当前编辑地标设置为刚刚添加的那个
    ToolProps->CurrentEditableLandmark = ToolProps->Landmarks.Num() - 1;

    // 启用顶点显示以便操作
    ToolProps->bShowVertices = true;

    // 标记属性为已修改，通知系统更新
    ToolProps->PostEditChange();
}
```
*来源：基于 `Private/MeshResizing/MeshWrapLandmarkSelectionTool.h` 中属性定义的推断。*

### 进阶用法

该插件通过 `FMeshResizingToolActionCommandBindings` 类将工具操作注册到全局的 Dataflow 工具注册表中。如果你需要在自己的编辑器模块中集成此工具，可能需要了解命令绑定机制。

```cpp
// 创建命令绑定对象并将其注册到 Dataflow 工具注册表
TUniquePtr<FMeshResizingToolActionCommandBindings> ActionBindings = MakeUnique<FMeshResizingToolActionCommandBindings>();

// 注册命令绑定。这通常在模块 StartupModule 中完成。
// FDataflowToolRegistry::Get().RegisterToolActionCommands(MoveTemp(ActionBindings));

// 当工具激活时，注册特定的键盘快捷键
// ActionBindings->BindCommandsForCurrentTool(UICommandList, LandmarkTool);

// 工具关闭时解绑
// ActionBindings->UnbindActiveCommands(UICommandList);
```
*来源：`Private/MeshResizing/MeshResizingToolActionCommandBindings.h`。*

## Demo 示例

一个最小的示例，展示如何创建自定义的工具构建器，该构建器可以实例化带有预设配置的 `UMeshWrapLandmarkSelectionTool`。

```cpp
// MyLandmarkToolBuilder.h
#pragma once
#include "InteractiveToolBuilder.h"
#include "MeshResizing/MeshWrapLandmarkSelectionTool.h"

class UMyLandmarkToolBuilder : public UMeshWrapLandmarkSelectionToolBuilder
{
	GENERATED_BODY()

public:
	virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override
	{
		UMeshWrapLandmarkSelectionTool* Tool = Cast<UMeshWrapLandmarkSelectionTool>(UMeshWrapLandmarkSelectionToolBuilder::BuildTool(SceneState));
		if (Tool)
		{
			// 在工具创建后进行自定义配置（示例）
			UMeshWrapLandmarkSelectionToolProperties* Props = Tool->GetToolProperties();
			if (Props)
			{
				// 可以在此预设一些默认地标或显示选项
				Props->bShowVertices = true;
				Props->bShowEdges = true;
			}
		}
		return Tool;
	}
};
```

```cpp
// MyLandmarkToolBuilder.cpp
#include "MyLandmarkToolBuilder.h"
// 注意：需要确保你的模块 Build.cs 依赖 MeshResizingEditorTools
```

## 模块依赖

从源码分析，要使用 `MeshResizingEditorTools` 模块，你的项目模块需要依赖以下**特有**模块：

| 模块 | 用途 |
|---|---|
| `Dataflow` | 提供 Dataflow 上下文、节点和编辑器工具集成框架，这是插件工具与 Dataflow 图交互的基础。 |
| `InteractiveToolsFramework` | 提供交互式工具的构建、属性集和命令绑定框架，是 `UMeshWrapLandmarkSelectionTool` 的基类所在。 |
| `ModelingComponents` | 提供 `UPreviewMesh`、`FGroupTopology` 等几何和预览相关的组件，用于网格操作和可视化。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数引发的编译警告。 |
| 2026-05-12 | `a7802337` | Dataflow: | Dataflow 相关更新（提交信息不完整，可能为子提交或合并）。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理工作预先添加必要的包含文件。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | Dataflow：利用网格中的新增功能，为绘画工具添加了套索支持。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | Dataflow：更新了大量节点以使用新的渲染系统。 |

### 维护评价

该插件自 2024 年 12 月创建，距今约 1.5 年，属于较新的实验性插件。从近期的提交记录（截至 2026 年 5 月）来看，它仍在**活跃维护**中。提交内容主要围绕 Dataflow 框架的集成、编译警告修复和新功能（如套索支持）的添加，表明其功能正在逐步完善和与 UE5 的新特性（如新渲染系统）保持同步。

**注意事项**：
1.  **实验性标记**：插件在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true`，且默认不启用。这意味着其 API 可能会发生变化，不建议在稳定的产品管线中深度依赖。
2.  **文档缺失**：官方文档链接 (`DocsURL`) 为空，说明该插件尚无官方使用指南，社区文档和经验也较少。
3.  **集成度**：插件深度绑定 Dataflow 和交互式工具框架，适合用于构建复杂的编辑器工具链，但学习曲线较陡。

**结论**：这是一个处于**活跃开发早期阶段**的实验性插件。如果你正在构建基于 Dataflow 的、需要网格地标编辑功能的定制化编辑器工具，可以尝试使用和跟踪其进展。对于一般性项目，建议等待其进一步成熟。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing/Tests)