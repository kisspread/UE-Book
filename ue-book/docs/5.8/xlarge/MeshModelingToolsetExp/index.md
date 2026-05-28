# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（实验性建模工具、编辑器UI框架、几何处理适配器） |
| 模块 | `GeometryProcessingAdapters` (Runtime), `MeshModelingToolsEditorOnlyExp` (Runtime), `MeshModelingToolsExp` (Runtime), `ModelingEditorUI` (Runtime), `ModelingUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

## 用途

本插件是 `MeshModelingToolset` 的**实验性分支**。它包含 Epic Games 正在开发、测试但尚未稳定或正式发布的新版网格建模工具。这些工具基于交互式工具框架构建，用于进行复杂的 3D 网格创建、编辑、绘制（如顶点颜色、蒙皮权重）等操作。将实验功能独立成插件有助于隔离风险，不影响主工具集的稳定性，并允许开发者和用户提前体验和反馈。

## 使用场景

- 你是**技术美术或工具开发者**，希望提前试用或集成 Epic 正在测试的最新网格编辑工具。
- 你需要使用**尚未在稳定版工具集中发布**的特定建模功能，例如新的细分曲面工具或高级绘制工具。
- 你正在**开发基于交互式工具框架的自定义工具**，并需要参考或复用实验性工具的UI和适配器代码。

## 蓝图用法

由于本插件为实验性且其模块（如 `ModelingUI`， `ModelingEditorUI`）主要提供 C++ 框架，蓝图公开接口相对有限。核心蓝图用法集中于通过交互式工具框架（Interactive Tools Framework）触发和控制这些实验性工具，但工具的具体逻辑和节点通常在子模块文档中定义。建议查看具体工具模块（如 `MeshModelingToolsExp`）的文档以获取可蓝图调用的函数。

### 核心节点

（具体可用蓝图节点取决于子模块 `MeshModelingToolsExp` 和 `ModelingUI` 中的 `UFUNCTION(BlueprintCallable)` 定义，详见子模块文档。）

## C++ 用法

使用本插件主要是在 C++ 层面，特别是进行工具开发或深度集成时。

### 头文件引入

根据所需功能引入对应模块的头文件，例如：
```cpp
#include "MeshModelingToolsExp.h"
#include "ModelingUI/ModelingToolWidgets.h"
```

### 基本用法

本插件的C++用法主要是通过交互式工具框架实例化和操作实验性工具。工具类通常位于 `MeshModelingToolsExp` 模块中，而UI部件位于 `ModelingUI` 或 `ModelingEditorUI` 模块中。

### 进阶用法

进阶用法涉及继承或组合这些实验性工具模块中的基础类（如 `UMeshVertexAttributePaintTool`）来创建自定义的网格编辑工具，或者利用 `GeometryProcessingAdapters` 模块适配不同的几何处理库。

## Demo 示例

由于本插件为实验性工具集，其示例代码通常与具体的实验工具绑定。最直接的“示例”是查看 `Engine/Tests/` 目录下与本插件相关的自动化测试用例，它们展示了工具的创建和基本操作流程。一个完整的、可编译的最小示例需要依赖多个子模块，结构复杂，通常作为插件的一部分进行测试。

## 模块依赖

要在你的项目或插件中使用本实验性工具集的特定功能，你需要依赖相应的子模块。常见依赖如下（具体依赖关系请查阅各子模块的 `Build.cs` 文件）：

| 模块 | 用途 |
|---|---|
| `MeshModelingToolsExp` | 核心实验性建模工具实现 |
| `ModelingUI` | 建模工具的通用 UI 框架 |
| `ModelingEditorUI` | 建模工具在编辑器中的特定 UI 组件 |
| `GeometryProcessingAdapters` | 为不同几何处理库提供统一接口 |
| `InteractiveToolsFramework` | 交互式工具框架（通常为引擎内置） |
| `ModelingTools` | 稳定版建模工具集（可能提供基类或共享功能） |

**注意**: 由于是实验性插件，其依赖关系可能比稳定版更复杂或不稳定。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 为顶点属性绘制和蒙皮权重绘制工具添加了跨模式同步画笔半径的功能 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构顶点属性绘制工具的笔画累加器以支持松弛笔刷，并修复了相关问题 |
| 2026-05-22 | `4938c498` | [SkeletalMeshModelingTools] Set AutoCalculated tangents mode on preview/sculpt meshes that lack vali | 在骨骼网格建模工具中，为缺少有效切线的预览/雕刻网格设置自动计算切线模式 |
| 2026-05-19 | `12cf9c64` | [SkeletalMeshModelingTools] Fixed polygroup edge visualizer not updated after mesh deformation | 修复了骨骼网格建模工具中多边形组边界可视化器在网格变形后不更新的问题 |
| 2026-05-14 | `f6425490` | [ModelingTools] Add UMeshElementsVisualizer to skin-weights tool; default group-boundary settings ON | 在蒙皮权重工具中添加网格元素可视化器，并将组边界设置默认为开启 |

### 维护评价

本插件处于**活跃的实验性开发**中。虽然创建于约5年前，但**近期（2026年5月）仍有频繁的功能性更新和Bug修复**，尤其集中在**骨骼网格建模工具**和**绘制类工具（如顶点属性、蒙皮权重）** 上。这表明 Epic 仍在积极探索和完善这些新功能。

**主要结论**：
- **推荐使用**：如果你是 UE5 工具链的早期使用者、技术美术或开发者，希望跟踪和测试最新的网格编辑功能，本插件是重要入口。
- **注意风险**：作为实验性插件，其API和功能可能在后续版本中发生重大变更甚至被移除。**不建议在正式生产项目的主线上深度依赖**。
- **适用对象**：主要用于开发、测试和原型验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Editor/MeshModelingTools) (通常位于引擎测试目录下)