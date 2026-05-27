# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产编辑器核心 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、资产、Dataflow 节点） |
| 模块 | `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

此插件是 Chaos 布料（Chaos Cloth）编辑系统的核心模块，为基于 **Dataflow 图**的布料资产提供编辑和创建功能。它不是一个独立的运行时物理模拟插件，而是布料资产在**编辑器环境**下的可视化编辑工具链核心。

主要解决的问题：
1. **布料权重图绘制**：允许美术师在网格表面直接绘制权重（例如，哪些顶点受布料模拟影响，影响强度如何）。
2. **网格选择工具**：提供精确的网格元素选择功能，用于定义布料模拟的区域。
3. **蒙皮权重传递**：从一个骨骼网格体将蒙皮权重信息传递给布料资产，简化绑定过程。
4. **Dataflow 集成**：所有工具都与 Dataflow 图系统深度集成，允许将编辑操作作为图节点输出。

它从原有的 `ChaosClothEditor` 插件拆分而来，目的是将与 USD 相关的代码移出编辑器模块，同时保持功能完整。

## 使用场景

-   **游戏美术师**：使用布料权重图绘制工具，为角色服装的物理模拟指定精确的权重区域（如，裙摆哪些部分摆动更剧烈，哪些部分相对固定）。
-   **技术美术/关卡设计师**：使用网格选择工具，在布料资产上定义特定的模式（Pattern），用于后续的模拟设置。
-   **绑定师/技术美术**：使用蒙皮权重传递工具，快速将已有人体骨骼的权重信息映射到服装布料资产上，避免手动重新绘制。
-   **所有用户**：通过 Dataflow 图的集成，将上述所有编辑操作记录为可重放、可调整参数的图节点，实现非破坏性工作流。

## 蓝图用法

本插件的蓝图用法主要体现在编辑器工具和属性设置上，而非运行时游戏逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ClearAll` | 清除当前工具的全部权重/选择 | `UClothEditorMeshWeightMapPaintToolActions`, `UClothMeshSelectionToolActions` |
| `FloodFillCurrent` | 用当前设置的权重值填充整个区域 | `UClothEditorMeshWeightMapPaintToolActions` |
| `Invert` | 反转当前选择的权重/选择 | `UClothEditorMeshWeightMapPaintToolActions`, `UClothMeshSelectionToolActions` |
| `GrowSelection` | 增长当前网格选择区域 | `UClothMeshSelectionToolActions` |
| `ShrinkSelection` | 收缩当前网格选择区域 | `UClothMeshSelectionToolActions` |
| `FloodSelection` | 全选所有网格元素 | `UClothMeshSelectionToolActions` |
| `ClearSelection` | 清除当前网格选择 | `UClothMeshSelectionToolActions` |
| `ShowAll` | 显示所有三角形（在隐藏三角形工具中） | `UClothEditorMeshWeightMapPaintToolShowHideProperties` |
| `Multiply` | 将当前权重乘以一个值 | `UClothEditorMeshWeightMapPaintToolActions` |

### 使用示例（蓝图描述）

1.  **在编辑器中启动工具**：当用户在布料资产编辑器中选择一个节点（如“布料绘制节点”或“选择节点”）时，Dataflow 图编辑器会触发对应的工具构建器（例如 `UClothEditorWeightMapPaintToolBuilder`），从而在视口界面激活相应的交互工具。
2.  **修改工具属性**：在工具激活后，细节面板（Details Panel）中会显示一组属性（例如 `UClothEditorWeightMapPaintBrushFilterProperties`）。这些属性通过 `UPROPERTY(EditAnywhere)` 暴露在蓝图编辑器中，允许用户在运行时调整。
3.  **触发操作按钮**：在细节面板中，一些属性集（如 `UClothEditorMeshWeightMapPaintToolActions`）包含了标记为 `CallInEditor` 的函数。这些函数会作为按钮出现在细节面板中，点击后会调用对应的操作（如“清除全部”、“反转”）。这些操作最终通过 `RequestAction` 函数传递给工具内部逻辑执行。

## C++ 用法

### 头文件引入

根据你要使用的具体工具类，引入对应的头文件。

```cpp
// 工具构建器
#include "ChaosClothAsset/ClothEditorToolBuilders.h"

// 绘制工具
#include "ChaosClothAsset/ClothWeightMapPaintTool.h"

// 选择工具
#include "ChaosClothAsset/ClothMeshSelectionTool.h"

// 蒙皮权重传递工具
#include "ChaosClothAsset/ClothTransferSkinWeightsTool.h"

// 编辑器上下文对象 (已弃用，推荐使用 UDataflowContextObject)
#include "ChaosClothAsset/ClothEditorContextObject.h"
```

### 基本用法

**获取工具的 CDO（类默认对象）并注册命令**

这是一个典型的编辑器工具注册流程，来自 `ClothEditorToolBuilders.cpp` 的模式：

```cpp
#include "ClothEditorToolBuilders.h"

// 在某个注册函数中
void RegisterClothEditorTools()
{
    TArray<UInteractiveTool*> ToolCDOs;
    // 该函数由插件提供，用于获取所有工具的CDO，以便注册命令
    UE::Chaos::ClothAsset::GetClothEditorToolDefaultObjectList(ToolCDOs);
    
    // 然后可以将这些CDO用于命令注册或其他编辑器集成
    for (UInteractiveTool* ToolCDO : ToolCDOs)
    {
        // ... 注册逻辑
    }
}
```

**查询工具支持的视图模式**

在 Dataflow 图编辑器中切换视图模式时，工具构建器需要报告其支持哪些模式：

```cpp
// 假设你有一个工具构建器实例
UClothEditorWeightMapPaintToolBuilder* ToolBuilder = ...;
TArray<UE::Chaos::ClothAsset::EClothPatternVertexType> SupportedModes;
TObjectPtr<UDataflowContextObject> ContextObject = ...;

// 调用接口方法，获取该工具支持的视图模式
ToolBuilder->GetSupportedViewModes(*ContextObject, SupportedModes);
```

### 进阶用法

**从权重图绘制工具中获取当前绘制的权重值**

在工具运行时，可能需要查询当前画笔下的权重值：

```cpp
// 假设你已经有一个 UClothEditorWeightMapPaintTool 的实例 (ToolInstance)
if (UClothEditorWeightMapPaintTool* PaintTool = Cast<UClothEditorWeightMapPaintTool>(ToolInstance))
{
    // 获取当前画笔下最近顶点的权重值
    double CurrentWeight = PaintTool->GetCurrentWeightValueUnderBrush();
    UE_LOG(LogTemp, Log, TEXT("Current weight under brush: %f"), CurrentWeight);
}
```

**程序化地设置顶点权重**

你也可以不通过画笔交互，直接设置一组顶点的权重值：

```cpp
// 设置顶点索引集合为 1.0 的权重，且不是擦除模式
TSet<int32> VerticesToSet = {100, 101, 105, 200};
PaintTool->SetVerticesToWeightMap(VerticesToSet, 1.0, false /* bIsErase */);
```

## Demo 示例

以下是一个最小的示例，展示如何在一个自定义编辑器模块中，通过代码启动布料权重绘制工具。这通常用于插件集成或测试。

**MyClothToolIntegration.h**
```cpp
// MyClothToolIntegration.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ChaosClothAsset/ClothEditorToolBuilders.h" // 包含工具构建器
#include "MyClothToolIntegration.generated.h"

UCLASS()
class UMyClothToolIntegration : public UObject
{
    GENERATED_BODY()

public:
    /** 程序化地启动布料权重绘制工具 */
    UFUNCTION(BlueprintCallable, Category="ClothTools")
    void StartWeightPaintTool(UDataflowContextObject* ContextObject);

private:
    // 持有当前活跃的工具实例，防止被垃圾回收
    UPROPERTY()
    TObjectPtr<UInteractiveTool> ActiveClothTool;
};
```

**MyClothToolIntegration.cpp**
```cpp
// MyClothToolIntegration.cpp
#include "MyClothToolIntegration.h"
#include "InteractiveToolManager.h"
#include "ToolContextInterfaces.h"
#include "ChaosClothAsset/ClothEditorToolBuilders.h"

void UMyClothToolIntegration::StartWeightPaintTool(UDataflowContextObject* ContextObject)
{
    if (!ContextObject)
    {
        UE_LOG(LogTemp, Warning, TEXT("ContextObject is null."));
        return;
    }

    // 1. 获取工具管理器 (在编辑器上下文中)
    FToolContextScopedQueryScope QueryScope(TEXT("StartWeightPaintTool"));
    IToolsContextQueries* ContextQueries = GetToolManagerContextQueries();
    if (!ContextQueries) return;

    UInteractiveToolManager* ToolManager = ContextQueries->GetToolManager();
    if (!ToolManager) return;

    // 2. 创建一个工具构建器状态
    FToolBuilderState BuilderState;
    // 在真实的编辑器环境中，BuilderState 需要从当前场景和选择状态中填充。
    // 这里为了示例，我们假设已经正确设置。
    // ... BuilderState 需要被正确初始化 ...

    // 3. 创建并启动工具
    // 注意：直接创建工具构建器并调用 BuildTool 是非标准方式，通常由编辑器框架在用户点击图标时触发。
    // 这里仅为演示底层API。
    UClothEditorWeightMapPaintToolBuilder* WeightPaintBuilder = GetMutableDefault<UClothEditorWeightMapPaintToolBuilder>();
    if (WeightPaintBuilder && WeightPaintBuilder->CanBuildTool(BuilderState))
    {
        UMeshSurfacePointTool* NewTool = WeightPaintBuilder->CreateNewTool(BuilderState);
        if (NewTool)
        {
            // 将上下文对象传递给工具 (通过工具自身的接口，此处简化)
            // 在实际实现中，工具的 Setup() 会从 BuilderState 中获取上下文。
            ToolManager->StartTool(NewTool);
            ActiveClothTool = NewTool;
            UE_LOG(LogTemp, Log, TEXT("Cloth Weight Paint Tool Started."));
        }
    }
}
```

**注意**：上述代码仅为概念演示。在真实的 UE5 编辑器中启动交互式工具，通常需要更完整的上下文设置（如有效的编辑器模式、工具目标等），并遵循 `UInteractiveToolManager` 的标准流程。

## 模块依赖

从 `ChaosClothAssetEditorTools.Build.cs` 分析，该插件依赖于多个 UE 核心和几何处理模块。

| 模块 | 用途 |
|---|---|
| `ChaosClothAssetEditor` | 同插件的另一个核心模块，包含 Dataflow 编辑器集成 |
| `Dataflow` | Dataflow 图框架，用于构建和执行布料处理图 |
| `DataflowEditor` | Dataflow 图的编辑器框架和 UI |
| `DynamicMesh` | 动态网格体库，用于工具操作的网格数据结构 |
| `GeometryProcessing` | 几何处理算法，用于权重计算、网格操作等 |
| `ModelingTools` | 建模工具框架，提供交互式工具基础（如 `UMeshSculptToolBase`） |
| `MeshConversion` | 网格体转换工具，用于在不同网格表示间转换 |
| `GeometryCore` | 几何核心库，提供向量、矩阵、边界框等基础几何类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为 Interchange 布料资产添加重新导入支持 |
| 2026-05-12 | `f1d5a018` | Daaflow : add HUD selection information to both Cloth and dataflow selection tool viewports | 在布料和数据流选择工具视口都增加 HUD 选择信息显示 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复 ChaosClothAssetEditor 模块的编译警告 |

### 维护评价

-   **活跃维护**：该项目创建于 **2026年1月**，至今约 **1年**，但最近一次更新在 **2026年5月20日**，表明仍在**积极维护**中。
-   **更新频率高**：近期更新频繁（2026年5月有多次提交），主要集中在**功能添加**（如重新导入支持）、**UI改进**（HUD信息）、**代码清理**和**编译警告修复**上。
-   **实验性状态**：`.uplugin` 中 `IsExperimentalVersion` 未明确标记为 `true`，但插件 `EnabledByDefault=false` 且版本号仅为 `0.1`，结合其处于活跃的重构期（从旧插件拆分而来），可以认为其**仍处于实验性阶段**。
-   **推荐使用**：对于需要基于 Dataflow 工作流来创建和编辑布料资产的**技术美术师和高级用户**，此插件是核心且推荐使用的。但对于纯运行时物理模拟，不需要此插件。由于它仍在演进，使用时应注意未来API可能发生变动。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
-   [官方文档]() (无)
-   [测试用例]() (未在插件目录内发现显式测试用例，可能集成在 `Engine/Tests` 下)