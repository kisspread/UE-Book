# Lidar Point Cloud Support

> Adds support for importing, processing and rendering of LiDAR Point Clouds.

| 属性 | 值 |
|---|---|
| 中文名 | 激光雷达点云 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义、样式资源） |
| 模块 | `LidarPointCloudRuntime` (Runtime), `LidarPointCloudEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud) | |

## 用途

该插件为 UE5 提供完整的 LiDAR 点云数据工作流支持，覆盖从**导入原始数据**、**编辑处理**到**实时渲染**的全流程。LiDAR（激光雷达）扫描产生的点云数据通常包含数百万至数十亿个 3D 点，广泛用于建筑测量、自动驾驶仿真、数字孪生等领域。此插件解决了 UE5 中高效加载、显示和编辑海量点云数据的问题。

具体功能包括：
- **导入**：支持常见的 LiDAR 文件格式导入（通过 UFactory 体系），带导入选项对话框，支持重新导入（Reimport）
- **渲染**：运行时高效渲染海量点云，支持节点可视化（ToggleShowNodes）
- **编辑**：提供专用编辑器模式（EditorMode），包含完整的交互工具集——选择、对齐、合并、碰撞生成、网格化、法线计算等
- **资产化**：将点云数据封装为 `ULidarPointCloud` 资产，可在内容浏览器中管理

## 使用场景

- 你正在制作**自动驾驶仿真**项目，需要导入真实道路扫描的 LiDAR 点云数据 → 用此插件
- 你需要在 UE5 中创建**数字孪生**，将建筑工地的 3D 扫描点云可视化 → 用此插件
- 你有一个大型点云文件，需要从中**提取感兴趣区域**、计算法线、生成静态网格体 → 用此插件的编辑工具
- 你需要将点云数据**转换为碰撞体**用于物理模拟 → 用此插件的碰撞构建功能

## 蓝图用法

此插件的大部分 API 通过编辑器工具（Editor Tools）以按钮形式暴露，而非标准的蓝图节点。以下是可从蓝图和编辑器面板调用的核心功能。

### 编辑器工具动作

这些函数标记为 `CallInEditor`，在 LiDAR 编辑模式的工具面板中以按钮形式出现：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AlignAroundWorldOrigin` | 将选中点云对齐到世界原点 | `ULidarToolActionsAlign` |
| `AlignAroundOriginalCoordinates` | 按原始坐标对齐点云 | `ULidarToolActionsAlign` |
| `ResetAlignment` | 重置对齐变换 | `ULidarToolActionsAlign` |
| `MergeActors` | 将多个 LiDAR Actor 合并为一个 | `ULidarToolActionsMerge` |
| `MergeData` | 在数据层面合并多个点云资产 | `ULidarToolActionsMerge` |
| `BuildCollision` | 为选中点云构建碰撞体 | `ULidarToolActionsCollision` |
| `RemoveCollision` | 移除选中点云的碰撞体 | `ULidarToolActionsCollision` |
| `BuildStaticMesh` | 将点云转换为静态网格体 | `ULidarToolActionsMeshing` |
| `CalculateNormals` | 计算点云法线（支持质量/噪声容差参数） | `ULidarToolActionsNormals` |
| `ClearSelection` | 清除当前选择 | `ULidarToolActionsSelection` |
| `InvertSelection` | 反选点 | `ULidarToolActionsSelection` |
| `DeleteSelected` | 删除选中的点 | `ULidarToolActionsSelection` |
| `DeleteHidden` | 删除隐藏的点 | `ULidarToolActionsSelection` |
| `HideSelected` | 隐藏选中的点 | `ULidarToolActionsSelection` |
| `ResetVisibility` | 重置所有点的可见性 | `ULidarToolActionsSelection` |
| `Extract` | 提取选中区域到新资产 | `ULidarToolActionsSelection` |
| `ExtractAsCopy` | 提取选中区域为副本 | `ULidarToolActionsSelection` |

### 选择工具

| 工具 | 说明 | 所在类 |
|---|---|---|
| Box Selection | 框选模式 | `ULidarEditorToolBoxSelection` |
| Polygonal Selection | 多边形套索选择 | `ULidarEditorToolPolygonalSelection` |
| Lasso Selection | 自由套索选择 | `ULidarEditorToolLassoSelection` |
| Paint Selection | 画笔选择（可调半径） | `ULidarEditorToolPaintSelection` |

### 使用示例（编辑器操作）

1. **启用插件**：在 Plugins 面板搜索 "LiDAR Point Cloud Support"，启用后重启编辑器
2. **导入点云**：将 .las/.laz/.pts 等文件拖入内容浏览器，会弹出导入选项对话框
3. **放置到场景**：从内容浏览器拖拽 `ULidarPointCloud` 资产到视口，自动生成 `ALidarPointCloudActor`
4. **进入编辑模式**：选择 LiDAR Actor 后，进入 LiDAR 编辑模式，工具栏中出现各类编辑工具
5. **选择 & 处理**：使用框选/画笔选择目标点区域，然后执行删除、隐藏、提取、网格化等操作

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块
#include "ILidarPointCloudEditorModule.h"
#include "LidarPointCloudEditorHelper.h"

// 运行时（需查看 Runtime 模块头文件）
#include "LidarPointCloud.h"
```

### 基本用法

通过 `FLidarPointCloudEditorHelper` 静态函数执行点云操作：

```cpp
// 来源: LidarPointCloudEditorHelper.h

// 创建新的点云资产
ULidarPointCloud* NewCloud = FLidarPointCloudEditorHelper::CreateNewAsset();

// 对齐选中的点云到世界原点
FLidarPointCloudEditorHelper::AlignSelectionAroundWorldOrigin();

// 设置选中点云的原始坐标
FLidarPointCloudEditorHelper::SetOriginalCoordinateForSelection();

// 居中选中的点云
FLidarPointCloudEditorHelper::CenterSelection();
```

### 进阶用法

合并、碰撞、网格化、法线等操作：

```cpp
// 来源: LidarPointCloudEditorHelper.h

// 合并多个点云资产到目标资产
ULidarPointCloud* Target = ...;
TArray<ULidarPointCloud*> Sources = { Cloud1, Cloud2, Cloud3 };
FLidarPointCloudEditorHelper::MergeLidar(Target, Sources);

// 以组件方式合并选中的 Actor（可选替换源 Actor）
FLidarPointCloudEditorHelper::MergeSelectionByComponent(true);

// 为选中点云构建碰撞体
FLidarPointCloudEditorHelper::BuildCollisionForSelection();

// 设置碰撞误差精度
FLidarPointCloudEditorHelper::SetCollisionErrorForSelection(100.0f);

// 将点云网格化为静态网格体
// 参数: bMeshByPoints, CellSize, bMergeMeshes, bRetainTransform
FLidarPointCloudEditorHelper::MeshSelected(false, 0.0f, true, true);

// 设置法线计算参数并计算
FLidarPointCloudEditorHelper::SetNormalsQuality(40, 1.0f);
FLidarPointCloudEditorHelper::CalculateNormalsForSelection();

// 通过凸体积选择点
FConvexVolume Volume = FLidarPointCloudEditorHelper::BuildConvexVolumeFromCoordinates(
    Start2D, End2D, ViewportClient);
FLidarPointCloudEditorHelper::SelectPointsByConvexVolume(
    Volume, ELidarPointCloudSelectionMode::Add);

// 通过球体选择点
FSphere SelectionSphere(FVector::ZeroVector, 500.0f);
FLidarPointCloudEditorHelper::SelectPointsBySphere(
    SelectionSphere, ELidarPointCloudSelectionMode::Add);

// 提取选中区域为新资产
FLidarPointCloudEditorHelper::ExtractAsCopy();

// 从屏幕坐标发射射线并检测点云
FVector3f HitLocation;
FLidarPointCloudRay Ray = FLidarPointCloudEditorHelper::MakeRayFromScreenPosition(
    ScreenPos, ViewportClient);
bool bHit = FLidarPointCloudEditorHelper::RayTracePointClouds(Ray, 1.0f, HitLocation);
```

### 编辑器模块扩展

```cpp
// 来源: ILidarPointCloudEditorModule.h

// 获取模块实例
ILidarPointCloudEditorModule& Module = ILidarPointCloudEditorModule::Get();

// 检查模块是否可用
if (ILidarPointCloudEditorModule::IsAvailable())
{
    // 获取菜单扩展管理器
    TSharedPtr<FExtensibilityManager> MenuManager = Module.GetMenuExtensibilityManager();
    
    // 获取工具栏扩展管理器
    TSharedPtr<FExtensibilityManager> ToolbarManager = Module.GetToolBarExtensibilityManager();
}
```

## Demo 示例

以下演示如何在编辑器插件中以编程方式创建点云资产并执行操作：

```cpp
// LidarPointCloudDemo.h
#pragma once

#include "CoreMinimal.h"
#include "LidarPointCloud.h"
#include "LidarPointCloudEditorHelper.h"

class FLidarPointCloudDemo
{
public:
    /** 创建点云资产并执行基本操作 */
    static void RunDemo()
    {
        // 1. 创建新的点云资产
        ULidarPointCloud* PointCloud = FLidarPointCloudEditorHelper::CreateNewAsset();
        if (!PointCloud)
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to create point cloud asset"));
            return;
        }

        UE_LOG(LogTemp, Log, TEXT("Created point cloud asset: %s"), *PointCloud->GetName());

        // 2. 假设已导入点云数据到 PointCloud 中
        // （通常通过内容浏览器拖入文件触发导入流程）

        // 3. 设置法线计算参数
        FLidarPointCloudEditorHelper::SetNormalsQuality(60, 1.5f);

        // 4. 执行射线检测（从屏幕位置）
        FVector3f HitLocation;
        FVector2d ScreenPosition(960.0, 540.0); // 屏幕中心
        FLidarPointCloudRay Ray = FLidarPointCloudEditorHelper::MakeRayFromScreenPosition(
            ScreenPosition, nullptr);
        
        if (FLidarPointCloudEditorHelper::RayTracePointClouds(Ray, 1.0f, HitLocation))
        {
            UE_LOG(LogTemp, Log, TEXT("Hit point cloud at: %s"), *FString(HitLocation.ToString()));
        }
    }

    /** 演示选择和编辑操作 */
    static void SelectionDemo()
    {
        // 框选区域（从屏幕左上到右下）
        FVector2d Start(100.0, 100.0);
        FVector2d End(500.0, 500.0);
        FConvexVolume Volume = FLidarPointCloudEditorHelper::BuildConvexVolumeFromCoordinates(
            Start, End, nullptr);

        // 添加选择
        FLidarPointCloudEditorHelper::SelectPointsByConvexVolume(
            Volume, ELidarPointCloudSelectionMode::Add);

        // 隐藏选中点
        FLidarPointCloudEditorHelper::HideSelected();

        // 重置可见性
        FLidarPointCloudEditorHelper::ResetVisibility();

        // 检查是否有选中的点
        if (FLidarPointCloudEditorHelper::AreLidarPointsSelected())
        {
            // 提取为副本
            FLidarPointCloudEditorHelper::ExtractAsCopy();
        }
    }

    /** 演示合并和网格化操作 */
    static void MergeAndMeshDemo()
    {
        // 合并选中的 LiDAR Actor（以数据方式，替换源 Actor）
        FLidarPointCloudEditorHelper::MergeSelectionByData(true);

        // 为选中点云构建碰撞（误差 100）
        FLidarPointCloudEditorHelper::SetCollisionErrorForSelection(100.0f);
        FLidarPointCloudEditorHelper::BuildCollisionForSelection();

        // 生成静态网格体（按体素大小网格化，合并网格，保留变换）
        FLidarPointCloudEditorHelper::MeshSelected(false, 0.0f, true, true);
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 编辑器交互工具框架（UInteractiveTool、行为目标等） |

> 注：运行时模块的依赖信息未在提供的 Build.cs 中给出。从编辑器代码可推断还可能依赖 `GeometryFramework`（选择框架）和 `ToolMenus`（工具菜单扩展）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退之前的某个改动 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联通知的重构（被回退后重新提交） |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 硬件光线追踪中统一网格批次所有权管理 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

**维护状态：活跃维护**

- 插件创建于 2020 年 1 月，已有约 6 年历史，属于较成熟的插件
- 近期（2026 年 5 月）仍有持续更新，主要为引擎级重构（视口框架统一、硬件光线追踪改进、格式化修复等）
- 更新内容多为引擎底层代码的统一重构，说明该插件已随引擎同步维护，功能上趋于稳定
- `EnabledByDefault=false` 需手动启用，但 `IsBetaVersion=false` 说明已非实验性产品
- 作为 Enterprise 类别插件（路径 `Engine/Plugins/Enterprise/`），由 Epic Games 官方维护，可靠性有保障
- **推荐使用**：对于需要在 UE5 中处理 LiDAR 点云数据的项目，这是官方提供的标准解决方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud)
- 官方文档：无
- 测试用例：未在插件目录中发现自动化测试用例