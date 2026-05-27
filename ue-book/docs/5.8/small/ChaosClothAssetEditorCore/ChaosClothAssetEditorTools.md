# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑器核心 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

该插件提供基于 Dataflow 的布料资产（Cloth Asset）在编辑器中的核心交互式编辑功能。它是从原始 `ChaosClothEditor` 插件拆分而来的三个插件之一，目的是将 USD 相关代码从编辑器模块中移出，同时保持功能完整性。

该插件主要解决以下问题：

- **布料权重图绘制**：在布料网格上交互式绘制权重图（Weight Map），用于控制布料模拟的约束强度、风力影响等参数
- **布料网格选择**：在布料资产上进行精确的网格元素选择（顶点/边/面），用于后续操作的数据输入
- **蒙皮权重转移**：将骨骼网格体的蒙皮权重（Skin Weights）转移到布料资产上，使布料能正确跟随骨骼变形

核心架构基于 UE5 的 Dataflow（数据流图）系统，所有编辑工具都通过 `UDataflowContextObject` 与 Dataflow 图编辑器联动，实现非破坏性的参数化编辑流程。

## 使用场景

- 你在制作角色服装的布料模拟 → 用权重图绘制工具控制不同区域的布料约束强度
- 你需要为布料的不同部分设置不同的物理参数（如刚度、阻尼）→ 用权重图绘制精确控制影响范围
- 你有一个已绑定骨骼的角色模型，需要将蒙皮权重应用到布料上 → 用蒙皮权重转移工具
- 你需要在 Dataflow 图中选择特定的布料节点进行编辑 → 用网格选择工具进行精确选择
- 你正在使用 Chaos Cloth 的 Dataflow 工作流创建布料资产 → 该插件是编辑环节的核心依赖

## 蓝图用法

该插件的所有功能均为编辑器交互式工具（Interactive Tools），不提供传统的蓝图节点。工具通过编辑器工具栏和 Dataflow 图编辑器上下文启动。

### 工具列表

| 工具 | 说明 | 所在类 |
|---|---|---|
| 权重图绘制工具 | 在布料网格上绘制/平滑/擦除权重值 | `UClothEditorWeightMapPaintTool` |
| 网格选择工具 | 选择布料网格元素（顶点/边/面组） | `UClothMeshSelectionTool` |
| 蒙皮权重转移工具 | 从骨骼网格体转移蒙皮权重到布料 | `UClothTransferSkinWeightsTool` |

### 工具构建器

| 构建器 | 说明 | 所在类 |
|---|---|---|
| `UClothEditorWeightMapPaintToolBuilder` | 创建权重图绘制工具实例 | 继承自 `UMeshSurfacePointMeshEditingToolBuilder` |
| `UClothMeshSelectionToolBuilder` | 创建网格选择工具实例 | 继承自 `UInteractiveToolWithToolTargetsBuilder` |
| `UClothTransferSkinWeightsToolBuilder` | 创建蒙皮权重转移工具实例 | 继承自 `USingleSelectionMeshEditingToolBuilder` |

### 权重图绘制工具属性

权重图绘制工具通过 `UClothEditorWeightMapPaintBrushFilterProperties` 提供丰富的配置选项：

| 属性 | 类型 | 说明 |
|---|---|---|
| `ColorMap` | `EClothEditorWeightMapDisplayType` | 权重图显示模式（黑白/白红） |
| `SubToolType` | `EClothEditorWeightMapPaintInteractionType` | 交互模式：Brush（笔刷）、Fill（填充）、PolyLasso（多边形套索）、Gradient（渐变）、HideTriangles（隐藏三角面） |
| `PrimaryBrushType` | `EClothEditorWeightMapPaintBrushType` | 笔刷模式：Paint（绘制）、Smooth（平滑）、Erase（擦除） |
| `BrushSize` | `float` | 笔刷相对大小 (0.0–1.0) |
| `Falloff` | `float` | 笔刷衰减区域比例 |
| `AttributeValue` | `double` | 绘制的目标权重值 |
| `Strength` | `double` | 笔刷强度 |
| `AngleThreshold` | `float` | 角度阈值限制（0–180°） |
| `bUVSeams` | `bool` | 是否以 UV 接缝为边界 |
| `bNormalSeams` | `bool` | 是否以法线硬边为边界 |
| `VisibilityFilter` | `EClothEditorWeightMapPaintVisibilityType` | 可见性过滤模式 |

### 权重图批量操作

通过 `UClothEditorMeshWeightMapPaintToolActions` 提供批量操作节点：

| 操作 | 说明 |
|---|---|
| `ClearAll()` | 清除所有权重值为零 |
| `FloodFillCurrent()` | 用当前属性值填充整个权重图 |
| `Invert()` | 反转所有权重值 |
| `Multiply()` | 乘以一个系数 |

### 网格选择工具操作

通过 `UClothMeshSelectionToolActions` 提供选择操作：

| 操作 | 说明 |
|---|---|
| `GrowSelection()` | 扩展当前选择 |
| `ShrinkSelection()` | 收缩当前选择 |
| `FloodSelection()` | 洪水填充选择 |
| `ClearSelection()` | 清除选择 |

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothEditorToolBuilders.h"
#include "ChaosClothAsset/ClothWeightMapPaintTool.h"
#include "ChaosClothAsset/ClothMeshSelectionTool.h"
#include "ChaosClothAsset/ClothTransferSkinWeightsTool.h"
#include "ChaosClothAsset/ClothEditorContextObject.h"
```

### 基本用法 — 获取工具默认对象列表

工具注册系统通过 `GetClothEditorToolDefaultObjectList` 获取所有可用工具的 CDO 列表：

```cpp
// 来源: ClothEditorToolBuilders.h
TArray<UInteractiveTool*> ToolCDOs;
UE::Chaos::ClothAsset::GetClothEditorToolDefaultObjectList(ToolCDOs);

// 每个 CDO 对应一个可用的布料编辑工具
for (UInteractiveTool* ToolCDO : ToolCDOs)
{
    // 注册到 Dataflow 工具注册表等
}
```

### 基本用法 — 视图模式转换

在 Dataflow 视图模式和布料视图模式之间转换：

```cpp
// 来源: ClothEditorToolBuilders.h
// 从 Dataflow 视图模式转为布料视图模式
const UE::Dataflow::IDataflowConstructionViewMode* DataflowMode = /* ... */;
EClothPatternVertexType ClothMode = UE::Chaos::ClothAsset::DataflowViewModeToClothViewMode(DataflowMode);

// 从布料视图模式获取对应的 Dataflow 视图模式名称
FName DataflowModeName = UE::Chaos::ClothAsset::ClothViewModeToDataflowViewModeName(ClothMode);
// 返回值为 "Cloth2DSimView"、"Cloth3DSimView" 或 "ClothRenderView"
```

### 进阶用法 — 权重图绘制工具的编程式操作

可以直接调用权重图绘制工具的 API 进行编程式权重设置：

```cpp
// 来源: ClothWeightMapPaintTool.h
// 假设已获取到 UClothEditorWeightMapPaintTool* Tool 实例

// 设置指定顶点集合的权重值
TSet<int32> Vertices;
Vertices.Add(0);
Vertices.Add(1);
Vertices.Add(2);
double WeightValue = 0.75;
bool bIsErase = false;
Tool->SetVerticesToWeightMap(Vertices, WeightValue, bIsErase);

// 请求批量操作
Tool->RequestAction(EClothEditorWeightMapPaintToolActions::ClearAll);
Tool->RequestAction(EClothEditorWeightMapPaintToolActions::FloodFillCurrent);
Tool->RequestAction(EClothEditorWeightMapPaintToolActions::Invert);
```

### 进阶用法 — 上下文对象与 Dataflow 联动

```cpp
// 来源: ClothEditorContextObject.h (UClothEditorContextObject 已废弃，使用 UDataflowContextObject)
// 注意: UClothEditorContextObject 在 5.6 中已被标记为废弃，应使用 UDataflowContextObject

// 通过上下文对象获取 Dataflow 资产
UDataflow* DataflowAsset = ContextObject->GetDataflowAsset();

// 获取当前选中的布料集合
TWeakPtr<const FManagedArrayCollection> ClothCollection = ContextObject->GetSelectedClothCollection();

// 获取当前施工视图模式
EClothPatternVertexType ViewMode = ContextObject->GetConstructionViewMode();

// 设置布料集合（切换视图模式时）
ContextObject->SetClothCollection(ViewMode, NewClothCollection, bUsingInputCollection);
```

### 进阶用法 — 蒙皮权重转移

```cpp
// 来源: ClothTransferSkinWeightsTool.h
// UClothTransferSkinWeightsTool 通过 ToolProperties 配置源网格体：

// 属性设置示例（通过 ToolProperties 面板）：
// - SourceMesh: 目标 USkeletalMesh 资产
// - SourceMeshTranslation: 源网格体位移偏移
// - SourceMeshRotation: 源网格体旋转
// - SourceMeshScale: 源网格体缩放
// - bHideSourceMesh: 是否隐藏源网格体预览
```

## Demo 示例

以下示例展示如何在自定义编辑器扩展中注册和使用布料编辑工具的命令绑定：

### ClothToolExample.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "ChaosClothAsset/ClothToolActionCommandBindings.h"

class FClothToolExample
{
public:
    /** 初始化所有布料编辑工具的命令绑定 */
    void RegisterToolCommands(const TSharedPtr<FUICommandList>& UICommandList);

    /** 为当前活动工具绑定命令 */
    void BindCommandsForTool(const TSharedPtr<FUICommandList>& UICommandList, UInteractiveTool* ActiveTool);

    /** 解除当前绑定 */
    void UnbindCommands(const TSharedPtr<FUICommandList>& UICommandList);
};
```

### ClothToolExample.cpp

```cpp
#include "ClothToolExample.h"
#include "ChaosClothAsset/ClothToolActionCommandBindings.h"

void FClothToolExample::RegisterToolCommands(const TSharedPtr<FUICommandList>& UICommandList)
{
    // 创建命令绑定管理器
    // FClothToolActionCommandBindings 内部注册了以下工具的快捷键：
    // - FClothEditorWeightMapPaintToolActionCommands (权重图绘制)
    // - FClothMeshSelectionToolActionCommands (网格选择)
    // - FClothTransferSkinWeightsToolActionCommands (蒙皮权重转移)
    
    FClothToolActionCommandBindings Bindings;
    // 将命令绑定到 UICommandList（具体实现在 BindCommandsForCurrentTool 中根据活动工具动态绑定）
}

void FClothToolExample::BindCommandsForTool(
    const TSharedPtr<FUICommandList>& UICommandList, 
    UInteractiveTool* ActiveTool)
{
    FClothToolActionCommandBindings Bindings;
    Bindings.BindCommandsForCurrentTool(UICommandList, ActiveTool);
}

void FClothToolExample::UnbindCommands(const TSharedPtr<FUICommandList>& UICommandList)
{
    FClothToolActionCommandBindings Bindings;
    Bindings.UnbindActiveCommands(UICommandList);
}
```

## 模块依赖

从源码中引用的类型推断，以下为该插件的特殊依赖：

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 交互式工具基础框架（UInteractiveTool、UInteractiveToolPropertySet） |
| `MeshModelingTools` | 网格雕刻工具基类（UMeshSculptToolBase、BrushOp） |
| `ModelingComponents` | 建模组件（UDynamicMeshComponent、UPreviewMesh） |
| `Dataflow` | Dataflow 数据流图框架（UDataflowContextObject、IDataflowEditorToolBuilder） |
| `DataflowEditor` | Dataflow 图编辑器集成（SDataflowGraphEditor） |
| `GeometryFramework` | 几何体框架（FDynamicMesh3、FTriangleGroupTopology） |
| `ChaosClothAsset` | 布料资产核心模块（布料专用数据类型） |
| `GeometryScriptingCore` | 几何脚本核心（网格操作） |
| `SkeletalMeshDescription` | 骨骼网格描述（蒙皮权重转移） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为布料资产添加重新导入支持 |
| 2026-05-12 | `f1d5a018` | Daaflow : add HUD selection information to both Cloth and dataflow selection tool viewports | 在布料和 Dataflow 选择工具视口中添加 HUD 选择信息显示 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复编译警告问题 |

### 维护评价

- **活跃维护中**：插件创建于 2026 年 1 月，至今约 4 个月，属于全新插件
- **更新频率高**：最近 1 个月内有多次功能性更新和修复，包括代码清理、编译警告修复、功能增强（重新导入支持、HUD 信息显示）
- **与 Chaos 布料系统同步发展**：作为布料资产 Dataflow 工作流的编辑器核心，随 UE5 Chaos 布料系统持续迭代
- **代码质量良好**：注意到了浮点精度警告等细节问题并修复
- **推荐使用**：如果你正在使用 Chaos Cloth 的 Dataflow 工作流创建布料资产，该插件是编辑环节的核心依赖，且处于活跃开发中

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- 官方文档（暂无）
- [Dataflow 工具注册表接口](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/ChaosClothAssetEditorCore/Source/ChaosClothAssetEditorTools/Private/ChaosClothAsset/ClothToolActionCommandBindings.h)