# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（可能包含蓝图资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途
`MeshResizing` 是一个实验性插件，提供了一套网格包裹（Mesh Wrapping）和形变的工作流工具。它允许用户在源网格和目标网格上标记对应的“地标点”（Landmarks），并基于这些对应关系，在 Dataflow 图表中驱动网格形变节点，从而将一个网格的形状适配到另一个相似的拓扑结构上。其核心解决的问题是：当需要将一个网格（如角色服装、部件）适配到另一个形状略有不同的网格（如不同体型的角色）时，进行快速、可控的形变和适配。

## 使用场景
- **角色换装系统**：将同一套服装网格适配到不同体型或姿态的角色身体网格上。
- **部件复用**：将一个经过雕刻或建模的网格部件（如肩甲、头盔）适配到相似但尺寸、角度略有不同的基础模型上。
- **程序化资产适配**：在 Dataflow 程序化建模流程中，使用节点对网格进行基于地标点的非刚性形变。

## 蓝图用法

### 核心节点

此插件的功能主要通过 **编辑器工具（Editor Tool）** 和 **Dataflow 节点** 体现，而非暴露给游戏运行时（Runtime）的蓝图节点。其蓝图交互主要体现在编辑器工具属性面板的配置上。

| 节点/属性 | 说明 | 所在类 |
|---|---|---|
| `Landmarks` 属性 | 一个地标点列表，每个点包含一个字符串标识符 `Identifier` 和一个顶点索引 `VertexIndex`。用于标记源和目标网格上的对应关系。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `CurrentEditableLandmark` 属性 | 当前正在编辑的地标索引。设置为 `-1` 或按住 Shift 键可新增地标，按住 Ctrl 键选择已有地标可修改此值。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `bShowVertices` 属性 | 在视口中是否显示网格的顶点。 | `UMeshWrapLandmarkSelectionToolProperties` |
| `bShowEdges` 属性 | 在视口中是否显示网格的边。 | `UMeshWrapLandmarkSelectionToolProperties` |

### 使用示例（编辑器内操作）

1.  **启动工具**：在编辑器模式下，通过特定的 Dataflow 图表面板或上下文菜单，找到并启动 “Mesh Wrap Landmark Selection Tool”。
2.  **选择网格**：工具会要求你选择一个网格物体（Target）进行操作。
3.  **标记地标**：
    - 在视口中，直接点击网格顶点或边来创建新的地标点（按住 Shift 键添加）。
    - 在属性面板的 `Landmarks` 数组中，手动为每个地标点填写唯一的字符串标识符（如 “Head”, “LeftShoulder”），以便与另一网格上的对应点匹配。
    - 可以通过按住 Ctrl 键点击视口中已有的地标点来在 `CurrentEditableLandmark` 中快速定位和编辑它。
4.  **配置显示**：通过勾选 `Show Vertices` 和 `Show Edges` 来控制视口中辅助几何体的显示，帮助更精确地选点。
5.  **完成与取消**：编辑完地标后，点击工具栏上的“接受”（绿勾）应用更改，或“取消”（红叉）放弃。

## C++ 用法

### 头文件引入

根据具体使用的模块，引入相应的头文件。例如，使用编辑器工具功能：
```cpp
#include "MeshResizing/MeshWrapLandmarkSelectionTool.h"
```

### 基本用法（工具与地标数据）

`MeshResizing` 的核心 C++ 交互发生在编辑器工具和其内部数据结构中。

**定义和检查地标（Landmark）：**
```cpp
// 定义一个地标点结构体，来自 MeshWrapLandmarkSelectionTool.h
FMeshWrapToolLandmark Landmark;
Landmark.Identifier = TEXT("ShoulderRight");
Landmark.VertexIndex = 1234; // 目标网格上的顶点索引

// 两个地标点通过 Identifier 和 VertexIndex 进行相等性比较
bool bAreSame = (Landmark == OtherLandmark);
```

**访问工具属性（通过 CDO）：**
```cpp
// 获取工具属性的默认对象（CDO），用于查询或设置属性
UMeshWrapLandmarkSelectionToolProperties* ToolPropsCDO = GetMutableDefault<UMeshWrapLandmarkSelectionToolProperties>();

// 获取当前地标列表的引用
TArray<FMeshWrapToolLandmark>& Landmarks = ToolPropsCDO->Landmarks;

// 设置当前编辑的地标索引（例如，在代码中自动聚焦到第一个地标）
if (Landmarks.Num() > 0)
{
    ToolPropsCDO->CurrentEditableLandmark = 0;
}
```

### 进阶用法（工具与 Dataflow 集成）

该插件的工具深度集成了 Dataflow 系统，工具本身可以读取和更新 Dataflow 图表中的节点。

```cpp
// 工具类内部持有 Dataflow 上下文和需要更新的节点指针（来自 MeshWrapLandmarkSelectionTool.h）
// UDataflowContextObject* DataflowContextObject;
// FMeshWrapLandmarksNode* SelectionNodeToUpdate;

// 当用户在工具中修改了地标后，工具会调用类似以下的方法将更改同步到 Dataflow 节点
void UpdateSelectedNode()
{
    if (SelectionNodeToUpdate && ToolProperties)
    {
        // 将工具属性中编辑好的地标列表，设置到对应的 Dataflow 节点属性上
        SelectionNodeToUpdate->Landmarks = ToolProperties->Landmarks;
        // 通知 Dataflow 图表，该节点属性已变化，可能需要重新计算
        // ... (触发图更新逻辑)
    }
}
```

## Demo 示例

由于此插件为编辑器工具且实验性，没有简单的独立运行时 Demo。其用法主要通过在编辑器中启动工具并交互来演示。一个极简的 C++ 框架示例如下：

**MyMeshResizingTest.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "MeshResizing/MeshWrapLandmarkSelectionTool.h" // 包含地标结构体
#include "MyMeshResizingTest.generated.h"

UCLASS()
class UMyMeshResizingTestSubsystem : public UEngineSubsystem
{
    GENERATED_BODY()
public:
    // 一个示例函数，演示如何操作地标数据
    void CreateSampleLandmarks();
};
```

**MyMeshResizingTest.cpp**
```cpp
#include "MyMeshResizingTest.h"

void UMyMeshResizingTestSubsystem::CreateSampleLandmarks()
{
    // 此函数仅为演示数据操作，实际应用中这些数据会由编辑器工具管理
    TArray<FMeshWrapToolLandmark> SampleLandmarks;

    FMeshWrapToolLandmark HeadLandmark;
    HeadLandmark.Identifier = TEXT("Head_Top");
    HeadLandmark.VertexIndex = 0;
    SampleLandmarks.Add(HeadLandmark);

    FMeshWrapToolLandmark SpineLandmark;
    SpineLandmark.Identifier = TEXT("Spine_Base");
    SpineLandmark.VertexIndex = 100;
    SampleLandmarks.Add(SpineLandmark);

    UE_LOG(LogTemp, Log, TEXT("Created %d sample landmarks for Mesh Resizing demo."), SampleLandmarks.Num());
}
```

## 模块依赖

从模块名称和插件性质推断，使用者通常需要依赖以下模块（具体以实际 `Build.cs` 文件为准）：

| 模块 | 用途 |
|---|---|
| `Dataflow` | 核心的 Dataflow 图表框架，用于创建和执行节点 |
| `GeometryProcessing` | 提供网格处理、拓扑分析（如 `FGroupTopology`）等底层几何操作 |
| `InteractiveToolsFramework` | 构建编辑器交互工具的基础框架 |
| `MeshResizingCore` | 插件的核心类型和工具定义 |
| `MeshResizingEngine` | 插件的引擎层面逻辑和形变算法 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数导致的编译警告。 |
| 2026-05-12 | `a7802337` | Dataflow: ... | 对 Dataflow 相关功能进行了更新。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将进行的头文件清理前，预先添加了必要的包含声明。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh ... | Dataflow：利用网格处理中新增的功能，为绘制工具添加了套索选择支持。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | Dataflow：将许多节点更新为使用新的渲染系统。 |

### 维护评价

`MeshResizing` 是一个**创建时间很近（2024年底）且目前仍在活跃维护**的实验性插件。从最近一年的提交记录看，它持续获得功能更新（如集成 Dataflow、改进工具交互）和质量优化（如修复编译警告），表明 Epic Games 内部有项目在使用或积极开发此功能。然而，其 `IsExperimentalVersion=true` 和 `EnabledByDefault=false` 的状态明确表示这是一个**实验性功能**，API 和工作流在未来版本中可能发生重大变化，甚至可能被移除。**不建议在需要长期稳定性的正式项目中将其作为核心依赖**，但非常适合在研发或实验项目中探索网格包裹和程序化形变的最新能力。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [官方文档]()（暂无）
- [测试用例]()（暂未在提供的上下文中发现公开的测试文件路径）