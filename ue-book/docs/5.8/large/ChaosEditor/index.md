# ChaosEditor

> Destruction Tools

| 属性 | 值 |
|---|---|
| 中文名 | 破碎编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FractureEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-08 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosEditor) | |

## 用途

ChaosEditor 是 Unreal Engine 5 中用于创建和编辑 **几何集合 (Geometry Collection)** 的核心编辑器插件。它并非一个简单的破坏工具，而是为 Chaos 物理系统的实时破坏效果提供了完整的编辑器工作流。该插件通过一个专用的 **破碎编辑器模式 (Fracture Editor Mode)** 工作，允许用户将一个静态网格体 (Static Mesh) 或骨骼网格体 (Skeletal Mesh) **分割、组织和配置成** 一个层次化的、可用于实时物理模拟的几何集合。

其主要功能包括：
1.  **破碎操作**：使用多种算法（如 Voronoi、径向、砖块、网格切割等）将几何体分解为碎片。
2.  **层次管理**：创建和管理碎片的聚类（Cluster）层次，以控制大规模破坏时的行为。
3.  **属性编辑**：设置碎片的物理模拟属性，如初始动态状态、损坏阈值、断裂后移除时间等。
4.  **UV 与材质**：为碎片的内部面自动生成 UV 布局和纹理，模拟内部材质效果。
5.  **优化与清理**：生成凸包（用于碰撞）、修复微小几何体、检测邻近关系等。
6.  **可视化与选择**：在编辑器中交互式地选择、查看和操作几何集合的骨骼（Bone）层级。

简单来说，**ChaosEditor 解决了“如何在编辑器中可视化、直观地创建复杂物理破坏资产”的问题**。它是连接美术资产和 Chaos 物理模拟运行时的桥梁。

## 使用场景

-   你需要制作一栋可以实时倒塌的建筑 → 使用 **砖块 (Brick)** 或 **Voronoi 破碎工具** 进行破碎。
-   你需要一个破碎的汽车，引擎盖、车门等部件需要独立飞出 → 使用 **聚类 (Cluster)** 工具构建层次，然后为不同部件设置不同的 **初始动态状态 (Initial Dynamic State)**。
-   你需要制作一个破碎的雕像，并希望破碎面看起来有内部纹理（如石头或混凝土质感）→ 使用 **自动 UV (Auto UV)** 工具为内部面生成 UV 并烘焙纹理。
-   你需要精确控制碎片的大小和分布，例如制作碎裂的玻璃窗 → 使用 **自定义 Voronoi (Custom Voronoi)** 工具手动放置破碎点。
-   你需要优化破碎资产的性能，合并过小的碎片或调整碰撞凸包 → 使用 **几何体合并 (Fix Tiny Geo)** 和 **凸包 (Convex)** 工具。

## 蓝图用法

由于 ChaosEditor 主要是一个 **编辑器模式 (Editor Mode)**，其核心交互发生在编辑器界面中，而非通过蓝图节点直接调用。绝大多数功能都封装在 `FFractureEditorModeToolkit` 和各种 `UFractureTool*` 类中，用于驱动编辑器 UI。

从源码中可以提取出一些与数据读写相关的属性和函数，可用于蓝图中查询或设置几何集合的状态，但破碎和编辑操作本身主要在模式面板中完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSelectedGeometryCollectionComponents` (静态) | 获取当前编辑器中选中的所有几何集合组件。 | `FFractureEditorModeToolkit` |
| `SetBoneSelection` | 设置几何集合组件上选中的骨骼索引列表。 | `FFractureEditorModeToolkit` |
| `GetStatisticsSummary` | 获取当前选择的几何集合的统计信息（如总顶点数、三角面数等）。 | `FFractureEditorModeToolkit` |
| `GetSelectionInfo` | 获取当前选择的描述信息文本。 | `FFractureEditorModeToolkit` |

### 使用示例（蓝图描述）

1.  **查询选中的几何集合**：在一个编辑器工具蓝图中，你可以调用 `FFractureEditorModeToolkit::GetSelectedGeometryCollectionComponents` 静态函数来获取当前用户在场景中选中的 `UGeometryCollectionComponent` 组件列表，然后遍历它们进行批处理或检查。
2.  **读取属性**：获取到组件后，你可以访问其关联的 `UGeometryCollection` 资产，读取其 `Damage`、`DynamicState` 等托管数组（TManagedArray）中的数据，这些数据与破碎编辑器中看到的状态一致。

## C++ 用法

### 头文件引入

```cpp
#include "FractureEditorMode.h"
#include "FractureEditorModeToolkit.h"
#include "FractureToolContext.h"
#include "GeometryCollection/GeometryCollection.h"
```

### 基本用法

以下代码展示了如何在 C++ 中获取破碎编辑器工具箱并操作骨骼选择。这些操作通常发生在编辑器扩展或自动化脚本中。
```cpp
// 假设我们已经进入了 Fracture Editor Mode
if (GEditor && GEditor->GetActiveViewport())
{
    // 获取当前的编辑模式实例
    FEditorModeTools& EditorModeTools = GLevelEditorModeTools();
    UFractureEditorMode* FractureMode = Cast<UFractureEditorMode>(EditorModeTools.GetActiveMode(UFractureEditorMode::EM_FractureEditorModeId));

    if (FractureMode)
    {
        // 获取工具箱（Toolkit），这是破碎编辑器的主要交互类
        TSharedPtr<FFractureEditorModeToolkit> Toolkit = FractureMode->GetToolkit().ToSharedRef();

        if (Toolkit.IsValid())
        {
            // 获取当前选中的几何集合组件
            TSet<UGeometryCollectionComponent*> SelectedComponents;
            FFractureEditorModeToolkit::GetSelectedGeometryCollectionComponents(SelectedComponents);

            // 对第一个选中的组件设置新的骨骼选择（索引1和2）
            if (UGeometryCollectionComponent* FirstComp = SelectedComponents.Array().Top())
            {
                TArray<int32> NewSelection = {1, 2};
                Toolkit->SetBoneSelection(FirstComp, NewSelection, /*bClearCurrentSelection=*/true);
            }
        }
    }
}
```
*（来源：参考 `FractureEditorModeToolkit.h` 中的 `GetSelectedGeometryCollectionComponents` 和 `SetBoneSelection` 函数声明）*

### 进阶用法

**使用 `FFractureToolContext` 执行破碎操作**：
破碎工具的核心执行逻辑围绕 `FFractureToolContext` 展开。以下是一个概念性示例，展示了如何为选中的组件创建上下文并模拟一个工具执行的流程。
```cpp
// 获取当前的破碎编辑器工具箱 (如上文所述)
TSharedPtr<FFractureEditorModeToolkit> Toolkit = ...;
if (!Toolkit.IsValid()) return;

// 获取选中的组件
TSet<UGeometryCollectionComponent*> SelectedComponents;
FFractureEditorModeToolkit::GetSelectedGeometryCollectionComponents(SelectedComponents);
if (SelectedComponents.Num() == 0) return;

// 为第一个组件创建工具上下文（包含选中的骨骼、几何集合、包围盒等信息）
UGeometryCollectionComponent* Component = *SelectedComponents.CreateConstIterator();
FFractureToolContext Context(Component);

// 清理选择（移除无效索引等）
Context.Sanitize();

// 此时，Context.GetSelection() 包含了经过清理的骨骼索引列表
// Context.GetGeometryCollection() 返回了底层的几何集合数据
// 接下来，理论上可以实例化一个具体的 UFractureTool（如 UFractureToolUniformVoronoi），
// 设置其参数，然后调用其 Execute 方法。但这需要深入了解工具内部实现。
```
*（来源：参考 `FractureToolContext.h` 中 `FFractureToolContext` 的构造和方法）*

**注意**：直接实例化和执行 `UFractureTool` 子类在 C++ 外部并不常见，因为这些工具的设计紧密依赖于破碎编辑器模式提供的 UI 状态、可视化系统和撤销/重做上下文。上述代码主要用于理解内部数据结构和流程。

## Demo 示例

由于 ChaosEditor 的核心是编辑器模式，一个“可运行的最小示例”通常是进入该模式并使用其 UI。以下是一个在 C++ 中 **激活破碎编辑器模式** 的示例，可以集成到编辑器工具菜单或按钮中。

### FractureEditorActivator.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "FractureEditorMode.h" // 包含模式ID定义

class FFractureEditorActivator
{
public:
    /** 切换破碎编辑器模式的开关 */
    static void ToggleFractureEditorMode()
    {
        if (GEditor)
        {
            FEditorModeTools& ModeTools = GLevelEditorModeTools();
            if (ModeTools.IsModeActive(UFractureEditorMode::EM_FractureEditorModeId))
            {
                // 如果已激活，则退出
                ModeTools.DeactivateMode(UFractureEditorMode::EM_FractureEditorModeId);
            }
            else
            {
                // 否则，激活该模式
                ModeTools.ActivateMode(UFractureEditorMode::EM_FractureEditorModeId);
            }
        }
    }
};
```

### 用法（例如，在某个菜单命令的回调中）：
```cpp
#include "FractureEditorActivator.h"

// ... 在某个 UFUNCTION(CallInEditor) 或 FUICommandInfo 的 Execute 中
FFractureEditorActivator::ToggleFractureEditorMode();
```

这个示例仅演示了如何开关编辑器模式。破碎操作本身需要用户在模式面板中手动选择工具并配置参数。

## 模块依赖

从插件的 `.uplugin` 文件 `Plugins` 数组可以看出，ChaosEditor 依赖于以下关键插件（模块），使用前需确保它们已启用：

| 模块 | 用途 |
|---|---|
| `PlanarCut` | 提供基于平面的切割算法，是 Voronoi 破碎等工具的底层实现。 |
| `GeometryCollectionPlugin` | 定义了几何集合（GeometryCollection）的核心运行时数据和组件。 |
| `MeshModelingToolsetExp` | 提供网格建模工具集，可能被用于某些编辑操作（如 UV 生成）。 |
| `EditorScriptingUtilities` | 提供编辑器脚本工具函数。 |
| `Fracture` | 可能包含破碎相关的底层库或运行时支持。 |

**特殊依赖**：插件本身是 `Editor` 类型，因此你的模块如果要在打包后（Runtime）使用几何集合，需要依赖 `GeometryCollectionPlugin` 等运行时模块。但 `ChaosEditor` 自身只在编辑器中工作。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断到浮点数的警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化字符串中，32位与64位格式说明符与参数类型不匹配的问题。 |
| 2026-04-14 | `eaf81cf6` | Add new fracture mode utility to split islands | 在破碎编辑器模式中新增了拆分岛屿（Split Islands）的工具。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 日志宏迁移至新的 UE_LOGF 宏。 |
| 2026-04-06 | `3e98cc7e` | TLazyObjectPtr Deprecation pt 3: | 继续进行对废弃指针类型 TLazyObjectPtr 的清理工作。 |

### 维护评价

ChaosEditor 是一个 **老资格但仍在维护中** 的核心插件。它创建于 2019 年，是 Unreal Engine Chaos 物理系统破坏编辑的基石。从近期的提交记录来看，Epic Games 的团队仍在持续对它进行 **编译兼容性修复**（如浮点、格式化宏、指针类型迁移）和 **功能增强**（新增工具如 Split Islands）。这表明它并非处于废弃状态，而是作为**生产就绪**的工具在持续迭代。

-   **活跃度**：中等。近期更新主要是内部维护和小型功能添加，大型特性更新不频繁。
-   **稳定性**：高。作为引擎内置且默认启用的插件，经过了充分的测试。
-   **推荐**：**强烈推荐** 任何需要使用 Unreal Engine 5 实现实时物理破坏效果的项目使用此插件。它是官方推荐的工作流。

> **注意**：尽管 `.uplugin` 中 `IsBetaVersion = true`，但这更多是 Epic 内部对“实验性”功能（相对于最终稳定版）的标记。该插件在实际项目中已被广泛使用和验证。鉴于其 7 年以上的年龄和持续的维护，它完全可用于生产环境。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosEditor)
-   [官方文档]() (此插件暂无独立的官方文档页面，主要参考 Chaos Destruction 的整体文档和引擎内的编辑器模式说明)
-   [测试用例]() (此插件的自动化测试用例通常位于引擎测试目录下，而非插件自身目录内)