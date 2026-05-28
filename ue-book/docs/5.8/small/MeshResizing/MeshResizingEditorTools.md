# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

Mesh Resizing 插件提供了一套实验性的工具，用于对静态网格（Static Mesh）进行“调整大小”操作。其核心并非简单的等比例缩放，而是基于用户在源网格和目标网格上设置的一系列对应“地标”（Landmarks），通过网格变形算法来重新拓扑网格，使其适配新的尺寸，同时尽可能保留表面细节和拓扑结构。该插件与 Unreal Engine 的 Dataflow 框架深度集成，提供了可视化的节点来操作网格变形过程。

## 使用场景

- 你有一个角色模型和一套为其精确制作的盔甲，现在需要为另一个体型不同的角色复用这套盔甲。你可以使用 Mesh Resizing，在新旧角色的身体关键部位（如肩膀、肘部、膝盖）设置地标，引导盔甲网格安全地变形以适配新体型，避免穿模和拉伸。
- 你在 Dataflow 中构建了一个程序化网格生成流程，其中一个步骤需要将一个基础网格动态调整到不同的尺寸。你可以使用 `MeshResizingDataflowNodes` 提供的节点来实现这个调整，并在编辑器中通过可视化工具精确控制变形区域。

## 蓝图用法

该插件的编辑器工具主要通过 C++ 和交互式工具框架使用，但提供了配置类供蓝图或编辑器细节面板交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Landmarks` | 可在编辑器属性面板中编辑的地标数组，每个地标包含一个标识符和对应的顶点索引。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `CurrentEditableLandmark` | 设置或获取当前正在编辑的地标索引。设置为 -1 或按住 Shift 键可添加新地标。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `Show Vertices` / `Show Edges` | 控制是否在编辑器中显示网格的顶点和边缘以辅助地标选择。 | `UMeshWrapLandmarkSelectionToolProperties` |

### 使用示例（蓝图描述）

在编辑器中激活 Mesh Wrap Landmark Selection Tool 后，你会在工具属性面板（Details Panel）中看到 `Landmarks` 数组和 `CurrentEditableLandmark` 属性。
1.  将 `CurrentEditableLandmark` 设置为 -1（或按住 Shift 键）。
2.  在视口中的源网格上点击，即可添加一个新的地标。该点的顶点索引会被自动记录。
3.  为该地标输入一个唯一的 `Identifier`（如 “left_shoulder”）。
4.  在目标网格上同样设置一个具有相同 `Identifier` 的地标。
5.  通过调整 `CurrentEditableLandmark` 索引并按住 Ctrl 键在视口中选择，可以修改已有地标的顶点位置。
6.  确认地标匹配无误后，执行工具操作，插件将根据这些对应点对网格进行变形调整。

## C++ 用法

### 头文件引入

```cpp
#include "MeshResizing/MeshWrapLandmarkSelectionTool.h"
#include "MeshResizing/MeshResizingToolActionCommandBindings.h"
```

### 基本用法

`MeshResizingEditorTools` 模块的核心是 `UMeshWrapLandmarkSelectionTool`，它通常由 `UMeshWrapLandmarkSelectionToolBuilder` 构建。
**来源文件**: `Private/MeshResizing/MeshWrapLandmarkSelectionTool.h`

```cpp
// 获取工具构建器
UInteractiveToolManager* ToolManager = GetToolManager();
UMeshWrapLandmarkSelectionToolBuilder* ToolBuilder = NewObject<UMeshWrapLandmarkSelectionToolBuilder>();
ToolManager->RegisterToolBuilder(UMeshWrapLandmarkSelectionTool::StaticClass(), ToolBuilder);

// 程序化设置工具属性（通常在工具内部完成）
UMeshWrapLandmarkSelectionToolProperties* Properties = Tool->ToolProperties;
Properties->Landmarks.Add(FMeshWrapToolLandmark{ TEXT("point_a"), 105 });
Properties->bShowVertices = true;
```

### 进阶用法

工具通过 `IDataflowEditorToolBuilder` 接口与 Dataflow 系统集成，可以注册自定义的工具动作命令。
**来源文件**: `Private/MeshResizing/MeshResizingToolActionCommandBindings.h`

```cpp
// 定义工具动作命令
class FMyCustomToolActionCommands : public FMeshResizingToolActionCommands<FMyCustomToolActionCommands, UMyCustomTool>
{
public:
    FMyCustomToolActionCommands()
        : FMeshResizingToolActionCommands(TEXT("MyToolContext"), LOCTEXT("MyToolContext", "My Custom Tool"))
    {
        // 定义具体的UI命令（如快捷键）
    }
};

// 在插件启动时，将命令注册到 Dataflow 工具注册表
FMeshResizingToolActionCommandBindings* ActionBindings = new FMeshResizingToolActionCommandBindings();
UE::Dataflow::FDataflowToolRegistry::Get().RegisterToolActionCommands(MakeShareable(ActionBindings));
```

## Demo 示例

以下示例展示了如何在一个编辑器模式（Mode）或交互式工具上下文中，程序化地创建并使用 Mesh Wrap Landmark Selection Tool 的属性。

```cpp
// MyMeshResizingHelper.h
#pragma once
#include "CoreMinimal.h"
#include "MeshResizing/MeshWrapLandmarkSelectionTool.h"

class FMyMeshResizingHelper
{
public:
    static void ConfigureLandmarkTool(UMeshWrapLandmarkSelectionTool* Tool);
};

// MyMeshResizingHelper.cpp
#include "MyMeshResizingHelper.h"
#include "UObject/ConstructorHelpers.h"

void FMyMeshResizingHelper::ConfigureLandmarkTool(UMeshWrapLandmarkSelectionTool* Tool)
{
    if (!Tool || !Tool->ToolProperties) return;

    UMeshWrapLandmarkSelectionToolProperties* Props = Tool->ToolProperties;

    // 清除现有地标
    Props->Landmarks.Reset();

    // 添加新的地标对应关系
    Props->Landmarks.Add({ TEXT("head_top"), 128 });
    Props->Landmarks.Add({ TEXT("left_elbow"), 256 });
    Props->Landmarks.Add({ TEXT("right_knee"), 312 });

    // 设置当前编辑第一个地标
    Props->CurrentEditableLandmark = 0;

    // 开启顶点显示以辅助调试
    Props->bShowVertices = true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 提供交互式工具框架（UInteractiveTool, UInteractiveToolBuilder 等基类） |
| `Dataflow` | 提供与 Dataflow 节点图编辑器集成的基础设施（IDataflowEditorToolBuilder, UDataflowContextObject） |
| `GeometryCore` | 提供几何处理核心功能（如 FGroupTopology） |
| `ModelingComponents` | 提供网格编辑、预览和选择机制（如 UPolygonSelectionMechanic） |
| `MeshResizingCore` | 本插件的核心数据类型和接口定义 |
| `MeshResizingEngine` | 包含实际的网格调整算法和引擎集成代码 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数产生的编译器警告。 |
| 2026-05-12 | `a7802337` | Dataflow: | 对 Dataflow 相关功能进行了更新（具体信息未在消息中给出）。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理提前添加必要的包含。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | 为 Dataflow 中的绘制工具添加了套索支持，利用了网格模块的新功能。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 更新了大量 Dataflow 节点以使用新的渲染系统。 |

### 维护评价

**状态**：**实验性，活跃维护中**。
- **创建时间**：该插件创建于2024年底，非常年轻。
- **活跃度**：从 git log 看，截止2026年5月仍有实质性功能更新和优化提交（如引入套索功能、适配新渲染系统、修复编译警告），表明 Epic 的开发团队仍在积极投入。
- **稳定性**：标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，说明它尚未成熟，API 和功能可能发生变更，不建议在生产项目中依赖。
- **建议**：适用于对网格变形工作流有前沿需求的开发者进行**原型验证和技术调研**。在生产环境中使用前，需充分评估其稳定性和未来支持情况。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [官方文档]( ) （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingEditorTools/Tests) （注：测试用例路径基于模块结构推断，可能位于插件内或 Engine/Tests 下）