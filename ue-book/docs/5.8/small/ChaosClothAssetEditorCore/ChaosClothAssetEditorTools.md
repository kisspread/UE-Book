# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑器核心 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、蓝图资产） |
| 模块 | `ChaosClothAssetEditor` (Editor), `ChaosClothAssetEditorTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

本插件为 Unreal Engine 中基于 Dataflow 系统的布料（Cloth）资产提供了核心的编辑器内创作和编辑工具集。它解决了在引擎内部高效编辑、绘制权重和选择特定布料区域的需求，是布料美术和 Technical Artist 工作流程的核心组成部分。其主要功能包括对布料顶点权重图进行绘画、平滑、擦除等操作，对布料网格进行顶点/边/面选择，以及从其他骨骼网格体转移蒙皮权重。

## 使用场景

- 你是一名布料美术师或 Technical Artist，需要为角色服装或布料模拟精确调整参数（如风力影响、刚度等）的权重分布 → 使用 **权重绘制工具 (`UClothEditorWeightMapPaintTool`)**。
- 你需要快速、直观地选择布料资产的特定区域（如袖口、领口），以便后续进行材质分配或参数设置 → 使用 **网格选择工具 (`UClothMeshSelectionTool`)**。
- 你有一个带蒙皮权重的角色模型，希望快速将权重信息传递给新的布料资产，避免手动绘制 → 使用 **蒙皮权重转移工具 (`UClothTransferSkinWeightsTool`)**。

## 蓝图用法

本插件主要提供 **编辑器内交互式工具**，而非运行时的蓝图节点。这些工具通过 Unreal Editor 的“建模”工具面板或 Dataflow 编辑器的上下文菜单激活。

### 核心工具

| 工具 | 说明 | 对应的工具构建器类 |
|---|---|---|
| 重量绘制 | 在布料资产的顶点上绘制、平滑或擦除权重图。 | `UClothEditorWeightMapPaintToolBuilder` |
| 网格选择 | 通过点选、框选或套索选择布料网格的顶点、边或面。 | `UClothMeshSelectionToolBuilder` |
| 蒙皮权重转移 | 从一个骨骼网格体转移蒙皮权重到布料资产。 | `UClothTransferSkinWeightsToolBuilder` |

### 工具构建器接口

所有布料编辑工具都实现了 `IChaosClothAssetEditorToolBuilder` 接口，用于声明其支持的构造视图模式（如 2D 模拟视图、3D 模拟视图）。

```cpp
// 示例：获取工具支持的构造视图模式
TArray<UE::Chaos::ClothAsset::EClothPatternVertexType> SupportedModes;
if (IChaosClothAssetEditorToolBuilder* Builder = Cast<IChaosClothAssetEditorToolBuilder>(SomeToolBuilder))
{
    Builder->GetSupportedViewModes(DataflowContextObject, SupportedModes);
}
```

## C++ 用法

本插件提供编辑器工具集，其 C++ 接口主要涉及工具构建、上下文对象和命令绑定，用于扩展或集成到自定义的编辑器工作流中。

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothEditorToolBuilders.h"
#include "ChaosClothAsset/ClothEditorContextObject.h"
#include "ChaosClothAsset/ClothToolActionCommandBindings.h"
```

### 基本用法

**1. 使用上下文对象获取编辑器状态**
`UDataflowContextObject` (或已废弃的 `UClothEditorContextObject`) 用于获取当前 Dataflow 编辑器的状态，如选中的节点、活动的布料集合和构造视图模式。

```cpp
// 假设你已经获得了一个 UDataflowContextObject 指针
if (UDataflowContextObject* Context = GetContextObject())
{
    // 获取当前构造视图模式
    EClothPatternVertexType ViewMode = Context->GetConstructionViewMode();
    
    // 获取当前选中的布料集合
    TWeakPtr<const FManagedArrayCollection> SelectedCollection = Context->GetSelectedClothCollection();
    
    // 尝试获取选中的特定类型 Dataflow 节点
    auto* MyCustomNode = Context->GetSingleSelectedNodeOfType<FMyCustomClothNode>();
}
```
*(来源: `Public/ChaosClothAsset/ClothEditorContextObject.h`)*

**2. 注册和绑定工具命令**
`FClothToolActionCommandBindings` 负责将工具的键盘快捷键等命令绑定到特定的 UI 操作上。

```cpp
// 在插件启动时注册命令绑定
FClothToolActionCommandBindings* Bindings = new FClothToolActionCommandBindings();
UE::Dataflow::FDataflowToolRegistry::Get().RegisterToolActionCommands(MakeShareable(Bindings));
```
*(来源: `Private/ChaosClothAsset/ClothToolActionCommandBindings.h`)*

### 进阶用法

**扩展布料编辑工具**
你可以通过继承工具基类和构建器来创建自定义的布料编辑工具。
1.  创建一个新的工具类，继承自 `USingleSelectionMeshEditingTool` 或 `UMeshSurfacePointTool`。
2.  创建对应的工具构建器类，继承自相应的 `UXXXToolBuilder` 并实现 `IChaosClothAssetEditorToolBuilder` 接口。
3.  在构建器的 `CreateNewTool` 方法中实例化你的自定义工具。
4.  通过 `FClothToolActionCommands` 模板类为你的工具注册命令。

```cpp
// 自定义工具构建器示例
class UMyClothToolBuilder : public USingleSelectionMeshEditingToolBuilder,
                            public IChaosClothAssetEditorToolBuilder
{
    // ... 实现 IChaosClothAssetEditorToolBuilder 接口 ...
    UE_API virtual USingleSelectionMeshEditingTool* CreateNewTool(const FToolBuilderState& SceneState) const override;
};

// 注册自定义工具命令
class FMyClothToolActionCommands : public FClothToolActionCommands<FMyClothToolActionCommands, UMyClothTool>
{
public:
    FMyClothToolActionCommands();
};
```
*(概念基于 `Private/ChaosClothAsset/ClothToolActionCommandBindings.h` 和 `Public/ChaosClothAsset/ClothEditorToolBuilders.h`)*

## Demo 示例

本插件为编辑器工具，不包含运行时 C++ 代码示例。其使用演示主要通过 Unreal Editor 的“建模”模式或 Dataflow 编辑器进行。启动 Dataflow 编辑器并编辑一个布料资产后，上述工具将出现在工具栏中。

## 模块依赖

本插件的模块依赖主要是 Unreal Engine 的编辑器和几何处理相关模块。使用者如果需要基于本插件进行扩展开发，其模块需要依赖以下模块。

| 模块 | 用途 |
|---|---|
| `Dataflow` | Dataflow 节点系统的核心模块，是本插件所有功能的基础。 |
| `GeometryProcessing` | 提供动态网格 (`FDynamicMesh3`) 操作、空间查询 (`FDynamicMeshAABBTree3`) 等底层几何功能。 |
| `MeshModelingToolsetExp` | 提供交互式建模工具框架（如 `UMeshSculptToolBase`、`UPolygonSelectionMechanic`）及其相关属性集。 |
| `ToolWidgets` | 提供工具交互控件，如变换 Gizmo (`UCombinedTransformGizmo`)。 |
| `SkeletalMeshDescription` | 用于蒙皮权重转移工具，处理骨骼网格体数据。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为 Interchange 布料资产添加重新导入支持 |
| 2026-05-12 | `f1d5a018` | Dataflow : add HUD selection information to both Cloth and dataflow selection tool viewports | Dataflow：为布料和数据流选择工具视口都添加 HUD 选择信息 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复编译警告问题 |

### 维护评价

该插件创建于 **2026年1月**，是一个非常新的项目（约 0 年历史）。从 Git 提交历史看，它在创建后的几个月内持续有功能更新和缺陷修复，表明它**正处于活跃的早期开发阶段**。由于其专注于 Dataflow 布料资产编辑这一特定且前沿的领域，是 Epic Games 官方工作流的一部分，因此**推荐开发者关注和学习**，尤其是在需要使用 Chaos 布料系统的项目中。但需注意，作为新系统，其 API 和功能可能仍在快速迭代中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- 官方文档 (链接待补充)
- 测试用例 (位于插件源码的 `Tests/` 目录下)