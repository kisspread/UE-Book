# Mesh Painting

> System for painting data onto meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 网格绘制 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshPaintEditorMode` (Editor), `MeshPaintingToolset` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-12-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MeshPainting) | |

## 用途

MeshPainting 插件是一个编辑器工具集，用于在静态网格或骨骼网格体上进行交互式数据绘制。其核心功能是让美术和关卡设计师能够直接在网格的顶点上绘制颜色、纹理通道等数据。这些数据通常用于在运行时控制材质效果，例如：混合多个材质层、模拟风化或苔藓效果、控制光照贴图的接缝，或为特定区域设置材质属性权重。它解决了在 DCC 软件中预烘焙顶点数据后无法在引擎中实时修改和迭代的问题。

## 使用场景

*   **材质混合**：你需要为大型场景中的静态网格（如岩石、墙壁）绘制顶点颜色，以驱动材质中的混合因子，实现不同材质（如石头、泥土、青苔）的平滑过渡。
*   **视觉细节增强**：你希望在网格的特定区域（如角落、边缘）直接绘制磨损、污渍或颜色变化，而无需创建复杂的UV布局或额外贴图。
*   **LOD 或风化控制**：通过绘制数据来影响网格特定区域的 LOD 切换或风化材质的强度。

## 蓝图用法

此插件主要为编辑器工具，其运行时蓝图节点较少。其核心功能通过编辑器中的“网格绘制”模式（Mesh Paint Mode）进行交互，该模式由 `MeshPaintEditorMode` 模块提供。`MeshPaintingToolset` 模块则提供了底层的工具函数和数据结构。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPaintedData` | 获取指定网格体上已绘制的数据（如顶点颜色）。 | `UMeshPaintComponent` |
| `ApplyOrRemoveData` | 将绘制的数据应用到网格资产或从资产中移除。 | `UMeshPaintUtility` |

*注：具体可用的蓝图函数取决于插件版本和你的操作流程（是在组件上临时绘制，还是修改源资产）。*

## C++ 用法

### 头文件引入

```cpp
#include “MeshPaintEditorMode/MeshPaintEditorMode.h“
#include “MeshPaintingToolset/MeshPaintingToolset.h“
```

### 基本用法

此插件的 C++ 用法主要围绕工具集和编辑器模式扩展。通常不直接在游戏代码中调用，而是用于开发自定义的绘制工具或扩展绘制功能。

### 进阶用法

可以继承 `UMeshPaintAdapter` 来为自定义的网格类型（如程序化生成的网格）实现绘制支持。

## Demo 示例

此插件作为编辑器工具，没有独立的运行时 Demo。其使用演示集成在虚幻编辑器的工作流中：
1.  在内容浏览器中选择一个 **Static Mesh** 或 **Skeletal Mesh** 资产。
2.  在资产编辑器或关卡视口中，找到并启用工具栏上的 **“网格绘制”** 按钮。
3.  在出现的面板中选择绘制模式（如顶点颜色）、画笔设置（大小、强度）和目标通道。
4.  直接在视口中对网格模型进行绘制，更改将实时预览。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供几何体处理算法，可能用于绘制时的网格交互计算。 |
| `InterchangeEditor` | 支持资产数据交换，可能用于绘制数据的导入导出流程。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式。 |
| 2026-03-06 | `02b005a0` | make the mesh paint mode render geometry collections w/ the native render, so it does not show any p... | 修复几何体集合在网格绘制模式下的渲染显示问题。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了一次错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的某个提交。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist... | 修复了引擎初始化委托的注册问题，提升了稳定性。 |

### 维护评价

该插件创建于 2019 年，是一个成熟的编辑器工具。从近期的 Git 历史看，仍在进行**活跃维护**，最近的更新（2026年）主要集中在修复错误和适配引擎核心变更（如委托、日志系统）上，以确保其与最新版 UE5 的兼容性。虽然没有看到重大新功能，但持续的维护表明它是官方支持、稳定可用的工具。**推荐在需要顶点数据绘制的项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MeshPainting)
- 测试用例路径：`Engine/Tests/MeshPainting/` (如果存在)