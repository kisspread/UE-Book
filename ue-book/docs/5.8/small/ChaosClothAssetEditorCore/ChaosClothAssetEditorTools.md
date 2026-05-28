# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑核心 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

该插件是 Unreal Engine 5 中 Chaos 布料系统（Chaos Cloth）编辑工具的核心组件。它的主要作用是提供一个完整的编辑器工具集，允许美术和技术美术在编辑器环境中**交互式地创建、编辑和调试**基于 Dataflow（数据流）节点的布料资产。

它不是一个面向玩家的运行时功能，而是一套**专业的编辑器工具链**，旨在将布料属性的编辑（如蒙皮权重、模拟参数）从复杂的参数调整转变为可视化的、类似雕塑的直观操作。其核心功能包括：
- **布料权重图绘制**：使用笔刷、填充、梯度等工具，在网格体顶点上直接绘制或修改影响布料模拟（如拉伸、弯曲、重力）的权重。
- **网格体选择**：精确选择布料网格体的顶点、边或多边形，以便进行局部操作。
- **蒙皮权重转移**：从另一个骨骼网格体（Skeletal Mesh）将蒙皮权重（Skin Weights）转移到布料网格体上，快速完成绑定。
- **与 Dataflow 编辑器集成**：工具的输入输出与数据流图紧密配合，确保在非破坏性工作流中的实时反馈和一致性。

**为什么存在**：没有这个插件，调整布料模拟效果需要手动修改数据流节点中的数值参数，效率低下且不直观。此插件通过提供所见即所得的交互式工具，极大地提升了布料资产的创作和迭代效率。

## 使用场景

- **角色服装设计**：为游戏角色制作复杂的布料（如披风、裙摆、盔甲衬布），需要精确控制不同区域的布料硬度、飘动幅度。使用`权重图绘制工具`直接在网格体上“绘制”这些属性。
- **资产绑定与迁移**：将一套为普通骨骼网格体制作的布料属性，快速应用到另一个具有相似拓扑但不同骨骼的网格体上，使用`蒙皮权重转移工具`可以节省大量时间。
- **节点调试与优化**：在 Dataflow 节点图中调整了参数后，希望立即在视口中看到结果，并可能需要手动微调。本插件的工具视口与 Dataflow 视口实时同步。
- **布料模拟问题排查**：布料穿模或抖动通常源于权重或约束设置不当。使用`网格体选择工具`和`权重图绘制工具`可以隔离问题区域，进行定点修复。

## 蓝图用法

本插件的核心功能以编辑器工具（Editor Tools）的形式存在，而非运行时蓝图节点。其蓝图可访问性主要体现在工具的属性（Properties）和操作（Actions）上。

### 核心节点（工具属性）

这些是工具激活后，在编辑器细节面板（Details Panel）中可配置的蓝图属性。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BrushSize` | 控制绘制笔刷的相对大小。 | `UClothEditorWeightMapPaintBrushFilterProperties` |
| `Strength` | 控制笔刷绘制效果的强度。 | `UClothEditorWeightMapPaintBrushFilterProperties` |
| `AttributeValue` | 指定绘制到网格上的权重目标值（0-1）。 | `UClothEditorWeightMapPaintBrushFilterProperties` |
| `Falloff` | 控制笔刷中心到边缘的衰减比例。 | `UClothEditorWeightMapPaintBrushFilterProperties` |
| `AngleThreshold` | 将影响区域限制在特定边角度的阈值内。 | `UClothEditorWeightMapPaintBrushFilterProperties` |
| `SourceMesh` | 在蒙皮权重转移工具中指定源骨骼网格体。 | `UClothTransferSkinWeightsToolProperties` |
| `Name` | 指定当前操作关联的数据流节点名称。 | `UClothEditorUpdateWeightMapProperties`, `UClothMeshSelectionToolProperties` |

### 使用示例（蓝图描述）

1.  **激活权重绘制工具**：在编辑器工具栏中选择“布料”相关工具，选择“权重图绘制”。工具被激活后，细节面板会显示`UClothEditorWeightMapPaintBrushFilterProperties`的一系列属性。
2.  **配置并绘制**：在细节面板中，将`BrushSize`设为0.5，`AttributeValue`设为1.0。在视口中用鼠标左键拖拽，即可将受影响顶点的权重值向1.0平滑地绘制。
3.  **执行操作**：在细节面板的`Operations`分类下，点击`FloodFillCurrent`按钮（对应`UClothEditorMeshWeightMapPaintToolActions`的函数），可以将当前`AttributeValue`一次性填充到所有选中或可见的顶点上。
4.  **蒙皮权重转移**：激活“转移蒙皮权重”工具后，在细节面板中，为`SourceMesh`属性指定一个骨骼网格体资产。工具会计算并显示权重转移的预览。点击接受（Accept）后，权重即被应用到当前的布料网格体上。

## C++ 用法

### 头文件引入

```cpp
// 使用编辑器工具构建器和上下文
#include "ChaosClothAsset/ClothEditorToolBuilders.h"
#include "ChaosClothAsset/ClothEditorContextObject.h"
```

### 基本用法

以下示例展示了如何在 C++ 中实例化一个布料权重绘制工具构建器，并使用上下文对象。

**来源文件路径**：基于 `ClothEditorToolBuilders.h` 和 `ClothEditorContextObject.h` 中的类定义。

```cpp
// 假设在某个编辑器工具管理类或模块中
#include "ChaosClothAsset/ClothEditorToolBuilders.h"
#include "ChaosClothAsset/ClothEditorContextObject.h"

void ActivateWeightPaintTool()
{
    // 1. 获取上下文对象 (通常由编辑器框架或 Dataflow 编辑器提供)
    // UDataflowContextObject* ContextObject = GetOrCreateContextObject();

    // 2. 创建工具构建器实例
    UClothEditorWeightMapPaintToolBuilder* ToolBuilder = NewObject<UClothEditorWeightMapPaintToolBuilder>();

    // 3. 检查是否可以构建工具 (基于当前编辑器状态和选择)
    FToolBuilderState SceneState = GetEditorSceneState(); // 需要实现获取当前状态的函数
    if (ToolBuilder->CanBuildTool(SceneState))
    {
        // 4. 构建并启动工具
        // 注意：工具的生命周期通常由框架管理，此处仅为逻辑演示
        UMeshSurfacePointTool* NewTool = ToolBuilder->CreateNewTool(SceneState);
        if (NewTool)
        {
            // 工具已创建并设置，框架会接管它的更新和渲染
            // 可能还需要设置 DataflowContextObject
            // Cast<UClothEditorWeightMapPaintTool>(NewTool)->SetDataflowContextObject(ContextObject);
        }
    }
}
```

### 进阶用法

以下示例结合了工具构建器和上下文对象，演示了在 Dataflow 编辑器工具栏中注册和使用布料工具的基本逻辑。

**来源文件路径**：综合 `ClothEditorToolBuilders.h`、`ClothEditorContextObject.h` 和 `ClothToolActionCommandBindings.h` 的逻辑。

```cpp
// 在模块的 StartupModule 中注册工具和命令
void FChaosClothAssetEditorToolsModule::StartupModule()
{
    // 注册工具的操作命令绑定
    FClothToolActionCommandBindings* ActionBindings = new FClothToolActionCommandBindings();
    UE::Dataflow::FDataflowToolRegistry::Get().RegisterToolActionCommands(MakeShareable(ActionBindings));

    // 获取工具的 CDO（类默认对象）列表用于命令注册
    TArray<UInteractiveTool*> ToolCDOs;
    UE::Chaos::ClothAsset::GetClothEditorToolDefaultObjectList(ToolCDOs);

    // 对每个工具的 CDO，可以注册菜单命令或快捷键
    for (UInteractiveTool* ToolCDO : ToolCDOs)
    {
        // 注册逻辑... 例如 TInteractiveToolCommands::RegisterCommands()
    }
}

// 在 Dataflow 编辑器中响应工具切换
void HandleToolActivation(UInteractiveTool* NewTool, const UDataflowContextObject& Context)
{
    // 检查新激活的工具是否是布料工具
    if (IChaosClothAssetEditorToolBuilder* ClothToolBuilder = Cast<IChaosClothAssetEditorToolBuilder>(NewTool->GetBuilder()))
    {
        // 查询该工具支持的布料视图模式
        TArray<UE::Chaos::ClothAsset::EClothPatternVertexType> SupportedModes;
        ClothToolBuilder->GetSupportedViewModes(Context, SupportedModes);

        if (SupportedModes.Num() > 0)
        {
            // 自动切换到该工具的首选视图模式
            EClothPatternVertexType PreferredMode = SupportedModes[0];
            SetClothConstructionViewMode(PreferredMode);
        }

        // 查询该工具是否允许在构建视图中显示线框
        bool bWireframeAllowed = ClothToolBuilder->CanSetConstructionViewWireframeActive();
        SetWireframeButtonState(bWireframeAllowed);
    }
}
```

## Demo 示例

一个最小化的示例，展示如何在插件或模块中访问布料编辑工具的上下文。

**ClothToolDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ChaosClothAsset/ClothEditorContextObject.h"

class FClothToolDemo
{
public:
    FClothToolDemo();
    ~FClothToolDemo();

    /** 模拟从外部（如自定义编辑器面板）启动权重绘制工具 */
    void SimulateWeightPaintToolActivation();

private:
    /** 创建并初始化一个用于演示的上下文对象 */
    UDataflowContextObject* CreateDemoContextObject();
};
```

**ClothToolDemo.cpp**
```cpp
#include "ClothToolDemo.h"
#include "ChaosClothAsset/ClothEditorToolBuilders.h"

FClothToolDemo::FClothToolDemo()
{
}

FClothToolDemo::~FClothToolDemo()
{
}

void FClothToolDemo::SimulateWeightPaintToolActivation()
{
    // 创建上下文对象
    UDataflowContextObject* ContextObj = CreateDemoContextObject();
    if (!ContextObj) return;

    // 创建权重绘制工具的构建器
    UClothEditorWeightMapPaintToolBuilder* Builder = NewObject<UClothEditorWeightMapPaintToolBuilder>();
    if (!Builder) return;

    // 模拟一个构建状态（实际需要从编辑器获取）
    FToolBuilderState MockState;
    // ... 填充 MockState 的上下文信息 ...

    // 尝试构建工具
    if (Builder->CanBuildTool(MockState))
    {
        UMeshSurfacePointTool* Tool = Builder->CreateNewTool(MockState);
        if (Tool)
        {
            // 设置上下文对象
            if (UClothEditorWeightMapPaintTool* WeightTool = Cast<UClothEditorWeightMapPaintTool>(Tool))
            {
                WeightTool->SetDataflowContextObject(ContextObj);
                UE_LOG(LogTemp, Log, TEXT("Successfully created and configured Cloth Weight Map Paint Tool."));
            }
        }
    }
}

UDataflowContextObject* FClothToolDemo::CreateDemoContextObject()
{
    UDataflowContextObject* ContextObj = NewObject<UDataflowContextObject>();
    // 在此可以配置 ContextObj 的成员，例如指向一个虚拟的 Dataflow 图
    // 实际使用中，这通常由编辑器框架自动提供
    return ContextObj;
}
```

## 模块依赖

你的模块如果要使用此插件提供的编辑器工具功能（例如构建自定义布料工具或与现有工具交互），需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 布料资产的核心运行时数据结构（如 `FManagedArrayCollection`、节点定义）。 |
| `Dataflow` | 数据流框架的核心运行时模块，提供上下文（`UDataflowContextObject`）、节点基础类等。 |
| `DataflowEditor` | 数据流编辑器框架，提供工具集成接口（如 `IDataflowEditorToolBuilder`）。 |
| `InteractiveToolsFramework` | UE5 的交互式工具框架基础，提供 `UInteractiveTool`, `UInteractiveToolBuilder` 等基类。 |
| `GeometryFramework` | 几何框架，提供 `UDynamicMeshComponent`, `FDynamicMesh3` 等用于工具预览和操作的类。 |
| `ModelingComponents` | 建模组件，提供许多可复用的工具部件（Mechanics）、操作（Brush Ops）等。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理了布料资产转换器的代码。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量转换为浮点数时产生警告的代码。 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为 Interchange 布料资产添加了重新导入的支持。 |
| 2026-05-12 | `f1d5a018` | Dataflow : add HUD selection information to both Cloth and dataflow selection tool viewports | 在布料工具和数据流选择工具的视口中添加了 HUD 选择信息显示。 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复了 `ChaosClothAssetEditor` 模块的编译警告问题。 |

### 维护评价

- **活跃维护**：该插件创建于 2026 年 1 月，是一个非常新的插件。最近的提交记录（截至 2026 年 5 月）显示它仍在被积极开发和维护中，包括功能添加（重新导入支持）、代码清理和编译警告修复。
- **核心编辑器功能**：作为布料系统编辑工作流的核心，它不太可能被快速废弃，而是会随着 Chaos Cloth 系统的成熟而持续迭代。
- **推荐使用**：对于任何需要进行精细布料资产创作的项目，**强烈推荐使用**此插件。它是 Unreal Engine 官方布料编辑工作流的标准组成部分，能够显著提升效率。
- **已知状态**：作为新插件，API 可能还在演进中（例如 `UClothEditorContextObject` 已标记为废弃，推荐使用 `UDataflowContextObject`）。使用时应关注引擎的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- 官方文档链接暂无。