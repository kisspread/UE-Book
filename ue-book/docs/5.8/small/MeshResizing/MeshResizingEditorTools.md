# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

Mesh Resizing 是一个实验性的编辑器工具插件，其核心功能是提供一套基于 **Dataflow** 的节点和交互式工具，用于对网格（特别是动画角色的蒙皮网格）进行高质量的缩放和变形。

它解决的核心问题是：在动画制作流程中，当需要将动画应用到不同体型的角色上时，如何高效、精确地调整角色的网格（蒙皮）以适应新的骨骼比例，同时保持变形质量和美术效果。通过引入“地标点”（Landmarks）的约束机制，美术师可以在模型的关键位置（如关节、五官）设定控制点，引导网格在缩放或变形时遵循预期的形态，从而避免简单的全局缩放带来的不自然拉伸。

## 使用场景

- **动画角色体型适配**：当你有一套为标准体型角色制作的动画，现在需要将其应用到一个更高、更瘦或更胖的角色上时，可以使用此工具基于地标点精确调整角色的蒙皮网格，使其匹配新骨骼。
- **美术资源微调**：当美术师需要对角色模型的特定部位（如头部、手部）进行精细的比例调整，而非全局缩放时。
- **程序化内容生成**：结合 Dataflow 节点，可以创建可重用的网格缩放流程，批量处理多个模型。

## 蓝图用法

此插件的当前模块（`MeshResizingEditorTools`）主要提供交互式编辑器工具，蓝图用法集中在工具属性的控制上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetFirstLandmarkWithID` | 根据一个整数 ID 查找第一个匹配的地标的索引。 | `UMeshWrapLandmarkSelectionTool` |
| `Landmarks` (属性) | 可编辑的地标准标数组。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `CurrentEditableLandmark` (属性) | 当前正在编辑的地标准标索引。设置为 -1 或按住 Shift 键可添加新地标。按住 Ctrl 键选择已有地标可设置此值。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `bShowVertices` (属性) | 控制是否在视图中显示网格顶点。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `Show Edges` (属性) | 控制是否在视图中显示网格边。 | `UMeshWrapLandmarkSelectionToolProperties` |

### 使用示例（蓝图描述）

1.  在编辑器中激活“Mesh Wrap Landmark Selection”工具后，工具细节面板会显示上述属性。
2.  美术师可以在网格上点击添加地标（通过调整 `CurrentEditableLandmark` 或使用 Shift+点击）。
3.  每个地标都有一个唯一的 `Identifier` 字符串和对应的 `VertexIndex`。
4.  通过勾选 `Show Vertices` 和 `Show Edges` 来获得更好的视图辅助。
5.  工具本身（`UMeshWrapLandmarkSelectionTool`）负责处理视图交互和地标选择，其 `GetFirstLandmarkWithID` 节点可用于查询特定地标。

## C++ 用法

此模块主要是编辑器交互式工具，没有直接暴露给游戏运行时的 C++ API。其核心用法体现在编辑器扩展和工具开发中。

### 头文件引入

```cpp
#include "MeshResizingToolActionCommandBindings.h" // 用于工具命令绑定
#include "MeshWrapLandmarkSelectionTool.h"        // 用于地标选择工具
```

### 基本用法

以下是工具命令绑定的简化使用逻辑，来源于 `MeshResizingToolActionCommandBindings.h`。

```cpp
// 定义一个特定工具的命令类
class FMeshWrapLandmarkSelectionToolActionCommands : public FMeshResizingToolActionCommands<FMeshWrapLandmarkSelectionToolActionCommands, UMeshWrapLandmarkSelectionTool>
{
public:
    FMeshWrapLandmarkSelectionToolActionCommands();
    // 这个类继承了命令上下文名和工具类信息，用于将UI命令（快捷键等）与特定工具绑定。
};

// 注册并管理这些命令
class FMeshResizingToolActionCommandBindings : public UE::Dataflow::FDataflowToolRegistry::IDataflowToolActionCommands
{
public:
    // 构造函数中通常会注册命令。
    // BindCommandsForCurrentTool 在激活工具时被调用，将命令绑定到UI。
    virtual void BindCommandsForCurrentTool(const TSharedPtr<FUICommandList>& UICommandList, UInteractiveTool* Tool) const override;
    // UnbindActiveCommands 在工具停用时清理。
    virtual void UnbindActiveCommands(const TSharedPtr<FUICommandList>& UICommandList) const override;
};
```

### 进阶用法

要创建类似“地标选择工具”的自定义工具，可以参考 `UMeshWrapLandmarkSelectionTool` 的结构：

```cpp
// 1. 定义一个继承自 USingleSelectionMeshEditingTool 的工具类
UCLASS(MinimalAPI)
class UMyCustomResizingTool : public USingleSelectionMeshEditingTool
{
    GENERATED_BODY()
public:
    // 重写 Setup, Shutdown, Render 等函数来实现自定义逻辑。
    virtual void Setup() override;
    virtual void OnShutdown(EToolShutdownType ShutdownType) override;
    virtual void Render(IToolsContextRenderAPI* RenderAPI) override;
    // ... 其他工具生命周期函数。
private:
    // 工具特定的属性、预览网格、交互机制等。
    UPROPERTY()
    TObjectPtr<UMyToolProperties> Properties;
    UPROPERTY()
    TObjectPtr<UPreviewMesh> Preview;
};

// 2. 定义一个对应的工具构建器
UCLASS(MinimalAPI)
class UMyCustomResizingToolBuilder : public UInteractiveToolWithToolTargetsBuilder, public IDataflowEditorToolBuilder
{
    GENERATED_BODY()
    // 实现 CanBuildTool, BuildTool 等函数。
};
```

## Demo 示例

以下是一个极简的工具扩展示例框架，展示了如何基于现有结构创建一个自定义的网格缩放相关工具。

**MySimpleMeshResizeTool.h**
```cpp
#pragma once

#include "InteractiveTool.h"
#include "MySimpleMeshResizeTool.generated.h"

UCLASS()
class UMySimpleMeshResizeTool : public UInteractiveTool
{
    GENERATED_BODY()

public:
    virtual void Setup() override;
    virtual void OnShutdown(EToolShutdownType ShutdownType) override;
    virtual void Render(IToolsContextRenderAPI* RenderAPI) override;

    // 在此添加你的工具核心逻辑函数
    void ApplySimpleResize(float ScaleFactor);
};
```

**MySimpleMeshResizeTool.cpp**
```cpp
#include "MySimpleMeshResizeTool.h"
#include "ToolContextInterfaces.h" // IToolsContextRenderAPI

void UMySimpleMeshResizeTool::Setup()
{
    UInteractiveTool::Setup();
    // 初始化工具状态，例如获取当前选中的网格。
}

void UMySimpleMeshResizeTool::OnShutdown(EToolShutdownType ShutdownType)
{
    // 清理资源。
    UInteractiveTool::OnShutdown(ShutdownType);
}

void UMySimpleMeshResizeTool::Render(IToolsContextRenderAPI* RenderAPI)
{
    // 在视口中绘制辅助信息，例如边界框、控制点等。
}

void UMySimpleMeshResizeTool::ApplySimpleResize(float ScaleFactor)
{
    // 此处实现具体的网格缩放算法。
    // 可以调用 MeshResizingEngine 模块中的功能（如果需要）。
}
```

*注意：此示例仅为代码结构演示。要让它在编辑器中工作并处理实际网格数据，需要集成工具构建器（Builder）、工具目标（Target）以及可能的 Dataflow 节点，这超出了简单示例的范围。*

## 模块依赖

从 `MeshResizingEditorTools.Build.cs` 分析，使用此工具模块需要依赖：

| 模块 | 用途 |
|---|---|
| `DataflowEditor` | 提供 Dataflow 编辑器集成、工具构建器接口 (`IDataflowEditorToolBuilder`) 和上下文对象 (`UDataflowContextObject`)。 |
| `DataflowNodes` | 提供核心的 Dataflow 节点定义和执行框架。 |
| `InteractiveToolsFramework` | 提供交互式工具的框架 (`UInteractiveTool`, `UPolygonSelectionMechanic` 等)。 |
| `GeometryFramework` | 提供几何处理相关的类，如 `FGroupTopology`、`UPreviewMesh` 和 `FToolDataVisualizer`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数导致编译警告的代码。 |
| 2026-05-12 | `a7802337` | Dataflow: | Dataflow 相关的更新（具体信息未在提交消息中展开）。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将进行的头文件清理前，预先添加必要的头文件包含。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | Dataflow：通过利用网格模块中新添加的功能，为绘制工具增加了套索选择的支持。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | Dataflow：将大量节点更新为使用新的渲染系统。 |

### 维护评价

**维护状态：活跃开发中**

- **创建时间**：插件创建于 2024 年底，非常年轻（约 1 年）。
- **更新频率**：从 Git 历史看，更新非常频繁（最近一次在 2026 年 5 月），表明 Epic 的开发团队正在持续投入。
- **内容性质**：近期更新主要集中在 **Dataflow 集成**（添加套索支持、更新渲染系统）和 **代码质量优化**（修复警告、头文件清理），这证实了插件的核心架构（Dataflow 管线）正在被积极地构建和打磨。
- **已知限制**：`.uplugin` 中 `EnabledByDefault: false` 和 `IsExperimentalVersion: true` 明确标识其为**实验性功能**，API 和功能在未来版本中可能发生重大变更。
- **推荐使用**：**仅推荐用于实验和原型开发**。如果你对利用 Dataflow 进行程序化网格变形感兴趣，可以关注此插件的进展。目前不适合用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [官方文档]()（暂无）
- [测试用例]()（未在提供的路径中找到独立测试用例，通常集成在模块内部或上游模块中）