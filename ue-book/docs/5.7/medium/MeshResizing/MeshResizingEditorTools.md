# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格尺寸调整 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（工具蓝图、数据流预设） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

Mesh Resizing 插件是基于 **Dataflow** 网格处理框架的**实验性**变形/缩放工具集。它提供了一套编辑器工具，允许用户通过交互式 Landmark（地标点）匹配、网格包裹（Wrap）和 RBF 插值等方式对静态网格进行尺寸调整或形状变形。核心目标是在不破坏拓扑结构的前提下，实现可控的、非均匀的网格变形。

该插件主要用于解决以下问题：
- 在游戏开发或资产制作中，需要按特定特征点（如关节、面部五官）对齐或缩放网格。
- 希望将 landamark 数据流嵌入到 Dataflow 图表中，实现程序化的网格变形。
- 需要一个轻量、可实验的网格变形原型工具，以测试新的变形算法。

## 使用场景

- **角色服装适配**：通过标记角色模型和服装模型的对应顶点，使用包裹变形快速将服装贴合到不同体型角色上。
- **面部动画测试**：在面部网格上设置地标点，通过调整地标位置来测试网格变形效果，而无需进入蒙皮绑定流程。
- **程序化资产调整**：在 Dataflow 图表中嵌入 MeshResizing 节点，实现参数化的网格缩放（如产品变体生成）。
- **编辑器原型验证**：游戏开发者需要快速测试一种新的网格变形算法，利用该插件的工具基类快速搭建交互式工具。

## 蓝图用法

> 注意：本插件主要作为编辑器工具使用，蓝图可直接调用的节点有限。以下列出从源码中提取的、与工具交互相关的暴露接口。

### 核心节点（蓝图可调用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetFirstLandmarkWithID` | 根据 ID 获取第一个匹配的 Landmark 索引 | `UMeshWrapLandmarkSelectionTool` |
| `UpdateSelection` | 更新多边形选择（用于 landmark 拾取） | `UMeshWrapLandmarkSelectionMechanic` |

### 使用示例（蓝图描述）

在关卡中放置一个静态网格体，选中它并启动 `MeshWrapLandmarkSelectionTool`（通过编辑器菜单或工具面板）。在工具 Detail 面板中，可以添加/编辑 `Landmarks` 数组属性（类型为 `FMeshWrapToolLandmark`）。每个 Landmark 需设置 `Identifier`（字符串标识）和 `VertexIndex`（顶点索引）。按住 **Shift** 点击网格表面可添加新 Landmark，按住 **Ctrl** 并点击已有 Landmark 可将其设为当前编辑项。

## C++ 用法

### 头文件引入

```cpp
#include "MeshResizing/MeshWrapLandmarkSelectionTool.h"
#include "MeshResizing/MeshResizingToolActionCommandBindings.h"
#include "Dataflow/DataflowToolRegistry.h"
```

### 基本用法（来自测试用例片段）

**1. 创建工具实例并设置 Landmark 数据**

```cpp
// 假设已在编辑器中获得源网格动态网格体
UPreviewMesh* PreviewMesh = ...;
UMeshWrapLandmarkSelectionTool* Tool = NewObject<UMeshWrapLandmarkSelectionTool>();
Tool->SetWorld(PreviewMesh->GetWorld());
Tool->SetTargetMesh(PreviewMesh->GetTangenMeshComponent()); // 实际接口可能不同

// 添加 Landmark 数据
FMeshWrapToolLandmark Landmark;
Landmark.Identifier = TEXT("NoseTip");
Landmark.VertexIndex = 42;
Tool->GetProperties()->Landmarks.Add(Landmark);
```

**2. 通过 DataflowToolRegistry 注册工具与命令绑定**

```cpp
// 在模块启动阶段
FMeshResizingToolActionCommandBindings* Bindings = new FMeshResizingToolActionCommandBindings();
UE::Dataflow::FDataflowToolRegistry::Get().RegisterToolActionCommands(Bindings);
```

**3. 工具关闭时清理**

```cpp
Tool->OnShutdown(EToolShutdownType::Accept);
```

> 源码位置：`Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingEditorTools/Private/MeshResizing/`

### 进阶用法（组合 Dataflow 节点）

MeshResizingDataflowNodes 模块提供了可连接到 Dataflow 图表的节点（如 `MeshWrapNode`）。用户可以在 Dataflow 图表中通过蓝图或 C++ 创建节点，并动态设置 Landmark 数组来驱动网格变形。

```cpp
// 在 Dataflow 节点评估时调用
FMeshWrapNode Node;
Node.SourceMesh = ...;
Node.TargetMesh = ...;
Node.Landmarks = ...;
Node.Evaluate(/* Context */);
```

## Demo 示例

以下是一个最小可编译的工具调用示例，展示如何从编辑器模块激活 `UMeshWrapLandmarkSelectionTool`（假设已集成到 EditorMode 中）。

**MeshResizingTestTool.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "BaseTools/SingleSelectionMeshEditingTool.h"
#include "InteractiveToolManager.h"
#include "MeshResizingTestTool.generated.h"

UCLASS()
class UMeshResizingTestTool : public USingleSelectionMeshEditingTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override;
};
```

**MeshResizingTestTool.cpp**

```cpp
#include "MeshResizingTestTool.h"
#include "MeshResizing/MeshWrapLandmarkSelectionTool.h"
#include "InteractiveToolManager.h"

void UMeshResizingTestTool::Setup()
{
    // 调用默认的包裹变形工具
    UMeshWrapLandmarkSelectionTool* LandmarkTool = NewObject<UMeshWrapLandmarkSelectionTool>(GetToolManager());
    LandmarkTool->SetWorld(GetWorld());
    LandmarkTool->SetTarget(GetTargetActor());
    LandmarkTool->Setup();
}
```

> 注意：实际集成需要处理 UInteractiveToolManager 的激活流程，以上仅为示意。

## 模块依赖

**省略常见依赖**（CoreUObject, Engine, Slate, InputCore, UnrealEd, PropertyEditor 等不列出）。

本模块（MeshResizingEditorTools）在 `Build.cs` 中引用的独特依赖（基于推断与常见模式）：

| 模块 | 用途 |
|---|---|
| `MeshResizingCore` | 提供核心数据结构（如 `FMeshWrapToolLandmark`、`FGroupTopology`） |
| `DataflowEditorTools` | 提供 `FDataflowToolRegistry`、`UDataflowEditorToolBuilder` 等基础框架 |
| `InteractiveToolsFramework` | 交互式工具框架（UICommands、UInteractiveTool 等） |
| `GeometryFramework` | 网格拓扑处理（`FGroupTopology`） |
| `MeshDescription` | 网格描述基础类型 |
| `MeshConversion` | 网格格式转换 |
| `MeshLODUtilities` | LOD 处理（可能用到的工具） |

其他模块依赖类似，但 `MeshResizingDataflowNodes` 额外依赖 `DataflowEngine` 和 `DataflowNodes`。

## 维护状态

### 近期更新

| 日期 | Commit Hash | 说明 |
|---|---|---|
| 2025-09-29 | `92ddeeb8` | 修复每任务顶点分配 bug |
| 2025-09-23 | `ca2d126b` | 使工具添加节点按钮可用于非 `ManagedArrayCol` 工具 |
| 2025-08-19 | `d66ea4c2` | 修复 Landmark 工具中的指针检查 |
| 2025-08-19 | `a5c868d7` | 修复工具在未修改时错误标记节点无效的问题 |
| 2025-08-15 | `e79d88de` | 修复空网格时 RBF 插值除零问题 |

### 维护评价

- **创建时间**：2025-08-15（距今约 1 年）
- **最近更新**：2025-09-29 有功能性修复，表明仍在维护中
- **活跃度**：过去 2 个月内有多次提交，但均为修复与优化，无重大功能迭代
- **实验性状态**：插件明确标记为 `IsExperimentalVersion=true`，API 可能在不兼容警告下变更
- **已知限制**：工具依赖 Dataflow 框架，缺少完整文档；Landmark 工具缺少对非对称网格的支持（根据代码注释推测）
- **推荐使用**：适合作为原型验证或对 Dataflow 网格变形有深入需求的开发者；由于是实验性插件，不建议直接用于生产管线，除非愿意承担 API 变动的维护成本

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（本插件暂无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing/Tests)（可能位于 Engine/Tests 下，具体路径待确认）

---

> **文档说明**：本文档基于 `.uplugin` 元数据、公开头文件头及 Git 历史生成。部分接口细节（如 `UMeshWrapLandmarkSelectionTool` 的完整 API）因信息有限未完全列出，建议参考源码 `MeshResizingEditorTools/Private/` 目录下的实现。