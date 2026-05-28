# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、UI 资源） |
| 模块 | `GeometryProcessingAdapters` (Runtime), `MeshModelingToolsEditorOnlyExp` (Runtime), `MeshModelingToolsExp` (Runtime), `ModelingEditorUI` (Runtime), `ModelingUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

## 用途

这是 UE5 官方网格建模工具集的**实验性分支**。2021 年从稳定的 `MeshModelingToolset` 插件拆分而来（见首次 commit），专门承载尚在开发中的新功能。

该插件解决的核心问题是：在 UE5 编辑器内提供完整的 3D 网格创建与编辑能力，无需外部 DCC 工具即可完成建模工作流。具体包括：

- **网格近似（Mesh Approximation）**：将多个 Actor（含 Nanite 几何体）合并为简化的 Static Mesh，用于 LOD 生成或场景烘焙
- **自动 UV 展开**：基于几何分析自动生成 UV 坐标，省去手动拆 UV 的繁琐过程
- **顶点属性绘制**：在网格表面直接绘制自定义顶点属性（如皮肤权重）
- **交互式建模工具**：提供布尔运算、倒角、挤出、细分、重拓扑等完整的多边形建模工具链

此插件处于实验阶段（`IsExperimentalVersion=true`，`Hidden=true`），功能可能随时变更或移除。稳定版本请使用 `MeshModelingToolset`。

## 使用场景

- 你需要在编辑器内对 Static Mesh 做布尔运算、倒角、挤出等操作 → 用本插件的建模工具
- 你有一组 Nanite 高精度 Actor，需要生成简化的碰撞/LOD 版本 → 用 `ApproximateActors` 功能
- 你需要快速为网格自动展开 UV → 用 `MeshAutoUV` 功能
- 你需要在骨骼网格上绘制皮肤权重 → 用 `SkinWeightsPaintTool`
- 你在原型阶段需要快速建模，不想切换到 Blender/3ds Max → 用本插件的全套工具

> ⚠️ 本插件默认未启用。需要在编辑器的 Plugins 面板中手动启用。

## 蓝图用法

由于本插件的 Runtime 模块主要暴露的是 C++ 接口供编辑器工具框架调用，直接的蓝图节点有限。核心功能通过编辑器内的 Modeling Tools 操作面板使用。

### 核心节点

本插件的 GeometryProcessingAdapters 模块提供 C++ 接口（`IGeometryProcessing_ApproximateActors`、`IGeometryProcessing_MeshAutoUV`），这些接口的蓝图可用版本通常封装在 `MeshModelingToolsExp` 模块的工具类中。直接的 `BlueprintCallable` 节点较少，主要通过编辑器工具交互使用。

### 使用示例（编辑器操作）

1. 启用插件后，在编辑器工具栏找到 **Modeling** 模式
2. 选择网格对象，从工具列表中选择所需的建模工具（如 Extrude、Boolean、Bevel 等）
3. 在细节面板中调整参数，实时预览效果
4. 确认后生成修改后的网格

## C++ 用法

### 头文件引入

```cpp
// 使用几何处理适配器接口
#include "GeometryProcessingAdaptersModule.h"
#include "GeometryProcessing/ApproximateActorsImpl.h"
#include "GeometryProcessing/MeshAutoUVImpl.h"
```

### 基本用法 — 网格近似（ApproximateActors）

将多个 Actor 合并近似为简化的 Static Mesh。

```cpp
#include "GeometryProcessing/ApproximateActorsImpl.h"
#include "MeshApproximationSettings.h"

// 来源: Public/GeometryProcessing/ApproximateActorsImpl.h
void MyApproximateFunction()
{
    // 获取近似实现
    UE::Geometry::FApproximateActorsImpl Approximator;
    
    // 基于 MeshApproximationSettings 构建选项
    FMeshApproximationSettings Settings;
    // ... 配置 Settings（精度、法线策略等）
    
    UE::Geometry::FApproximateActorsImpl::FOptions Options = 
        Approximator.ConstructOptions(Settings);
    
    // 准备输入
    UE::Geometry::FApproximateActorsImpl::FInput Input;
    // ... 填充 Input（Actor 列表等）
    
    // 执行近似
    UE::Geometry::FApproximateActorsImpl::FResults Results;
    Approximator.ApproximateActors(Input, Options, Results);
    
    // Results 中包含生成的 StaticMesh 资产
}
```

### 基本用法 — 自动 UV 生成

```cpp
#include "GeometryProcessing/MeshAutoUVImpl.h"

// 来源: Public/GeometryProcessing/MeshAutoUVImpl.h
void MyAutoUVFunction(FMeshDescription& Mesh)
{
    UE::Geometry::FMeshAutoUVImpl AutoUV;
    
    // 使用默认选项
    UE::Geometry::FMeshAutoUVImpl::FOptions Options = 
        AutoUV.ConstructDefaultOptions();
    
    // 对 MeshDescription 执行自动 UV 展开
    UE::Geometry::FMeshAutoUVImpl::FResults Results;
    AutoUV.GenerateUVs(Mesh, Options, Results);
    
    // Mesh 中的 UV 数据已被更新
}
```

## Demo 示例

以下示例展示如何使用 GeometryProcessingAdapters 模块进行网格自动 UV 生成。

```cpp
// MyAutoUVHelper.h
#pragma once

#include "CoreMinimal.h"
#include "MeshDescription.h"

class FMyAutoUVHelper
{
public:
    /** 对给定的 MeshDescription 执行自动 UV 展开 */
    static bool GenerateAutomaticUVs(FMeshDescription& InOutMesh);
};
```

```cpp
// MyAutoUVHelper.cpp
#include "MyAutoUVHelper.h"
#include "GeometryProcessingAdaptersModule.h"
#include "GeometryProcessing/MeshAutoUVImpl.h"

bool FMyAutoUVHelper::GenerateAutomaticUVs(FMeshDescription& InOutMesh)
{
    UE::Geometry::FMeshAutoUVImpl AutoUV;
    
    // 构建默认选项
    UE::Geometry::FMeshAutoUVImpl::FOptions Options = 
        AutoUV.ConstructDefaultOptions();
    
    // 执行 UV 生成
    UE::Geometry::FMeshAutoUVImpl::FResults Results;
    AutoUV.GenerateUVs(InOutMesh, Options, Results);
    
    // 检查结果是否成功
    return Results.bSuccess;
}
```

## 模块依赖

由于本插件有 5 个模块，依赖关系分散在各自的 Build.cs 中。以下是使用者需要关注的关键依赖：

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 底层几何处理算法（网格简化、UV 生成等） |
| `ModelingTools` | 交互式建模工具框架基础 |
| `DynamicMesh` | 动态网格数据结构 |
| `MeshDescription` | 网格描述数据格式 |
| `MeshConversion` | 网格格式转换工具 |
| `InteractiveToolsFramework` | 交互式工具框架 |

> 注：`GeometryProcessingAdapters` 模块作为适配层，桥接 `GeometryProcessing` 库与 UE5 资产系统。

## 子模块概览

本插件为大型插件（163 个源文件），包含以下子模块：

| 模块 | 类型 | 职责 |
|---|---|---|
| `GeometryProcessingAdapters` | Runtime | 几何处理算法的适配器层（网格近似、自动 UV） |
| `MeshModelingToolsExp` | Runtime | 实验性建模工具的 Runtime 部分（工具逻辑、操作） |
| `MeshModelingToolsEditorOnlyExp` | Runtime | 仅编辑器环境下使用的工具功能 |
| `ModelingEditorUI` | Runtime | 建模工具的编辑器 UI 组件 |
| `ModelingUI` | Runtime | 建模工具的通用 UI 组件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 顶点属性绘制和皮肤权重绘制工具新增跨模式同步笔刷半径功能 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构顶点绘制的笔画累加器以支持松弛笔刷 |
| 2026-05-22 | `4938c498` | [SkeletalMeshModelingTools] Set AutoCalculated tangents mode on preview/sculpt meshes that lack valid tangents | 骨骼网格建模工具修复缺少有效切线的预览网格自动计算切线 |
| 2026-05-19 | `12cf9c64` | [SkeletalMeshModelingTools] Fixed polygroup edge visualizer not updated after mesh deformation | 修复骨骼网格建模中网格变形后多边形组边缘可视化未更新的问题 |
| 2026-05-14 | `f6425490` | [ModelingTools] Add UMeshElementsVisualizer to skin-weights tool; default group-boundary settings ON | 皮肤权重工具新增网格元素可视化器，默认开启组边界显示 |

### 维护评价

**活跃维护中** ✅

- 创建于 2021 年 7 月，从稳定的 `MeshModelingToolset` 拆分而来
- 近期（2026 年 5 月）有密集的功能性更新，主要集中在顶点属性绘制、皮肤权重工具和骨骼网格建模方面
- 虽然标记为实验性，但功能持续迭代，说明 Epic 正在积极将新功能推向稳定版本
- 随着功能成熟，部分功能可能会迁移到正式的 `MeshModelingToolset` 插件中

**注意**：本插件为实验性版本，默认未启用且对用户隐藏。生产环境建议使用稳定的 `MeshModelingToolset`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- [稳定版插件 MeshModelingToolset](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MeshModelingToolset)