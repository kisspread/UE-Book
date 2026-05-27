# LiDAR Point Cloud Support

> Adds support for importing, processing and rendering of LiDAR Point Clouds.

| 属性 | 值 |
|---|---|
| 中文名 | 激光雷达点云 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、资产定义等） |
| 模块 | `LidarPointCloudRuntime` (Runtime), `LidarPointCloudEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud) | |

## 用途

本插件为 Unreal Engine 提供完整的 LiDAR（激光雷达）点云数据工作流支持。LiDAR 扫描产生的点云数据通常包含数百万到数十亿个三维点，每个点带有位置、颜色、法线等属性。该插件解决了以下核心问题：

- **导入**：支持 `.las`、`.laz` 等标准 LiDAR 格式的文件导入，带导入选项对话框
- **处理**：在编辑器中对点云进行对齐、合并、法线计算、碰撞体生成、网格化（Meshing）等操作
- **渲染**：高效渲染大规模点云数据，支持视锥体剔除等优化
- **编辑**：通过框选、多边形选择、套索选择、画刷选择等多种方式选择并编辑点云中的点

该插件默认关闭（`EnabledByDefault: false`），需要在项目设置中手动启用。属于企业级（Enterprise）插件，主要面向建筑、工程、测绘、影视虚拟制片等需要处理现实世界扫描数据的行业用户。

## 使用场景

- 你从激光雷达扫描仪获得了建筑物/地形的 `.las` 点云文件 → 用本插件导入并在场景中可视化
- 你需要将扫描的点云数据转换为可碰撞的静态网格体用于碰撞检测 → 使用编辑器工具中的 Meshing 和 Collision 功能
- 你需要从多个扫描站点合并点云数据并对齐坐标 → 使用 Merge 和 Align 工具
- 你需要在虚拟制片中使用 LiDAR 扫描的实景环境作为背景参考 → 导入点云并渲染

## 蓝图用法

本插件的核心功能主要通过编辑器工具（Interactive Tools）提供，而非运行时蓝图节点。编辑器工具中的操作通过 `UFUNCTION(CallInEditor)` 暴露，在编辑器 Mode 面板中直接使用。

### 编辑器工具操作

以下操作在 LiDAR 编辑模式（Lidar Editor Mode）的工具面板中可用：

| 操作类别 | 功能 | 说明 |
|---|---|---|
| 对齐（Align） | `AlignAroundWorldOrigin` | 将点云对齐到世界原点 |
| 对齐（Align） | `AlignAroundOriginalCoordinates` | 将点云对齐到原始坐标 |
| 对齐（Align） | `ResetAlignment` | 重置对齐 |
| 合并（Merge） | `MergeActors` | 按组件合并选中的点云 Actor |
| 合并（Merge） | `MergeData` | 按数据合并选中的点云资产 |
| 碰撞（Collision） | `BuildCollision` | 为点云生成碰撞体 |
| 碰撞（Collision） | `RemoveCollision` | 移除点云碰撞体 |
| 网格化（Meshing） | `BuildStaticMesh` | 将点云转换为静态网格体 |
| 法线（Normals） | `CalculateNormals` | 计算点云法线 |
| 选择（Selection） | `ClearSelection` / `InvertSelection` / `DeleteSelected` / `HideSelected` 等 | 点云点的选取与清理操作 |
| 选择（Selection） | `Extract` / `ExtractAsCopy` | 提取选中点为新资产 |
| 画刷（Brush） | 可调 `BrushRadius`（0-8196） | 画刷半径控制 |

### 选择模式

| 模式 | 说明 |
|---|---|
| 框选（Box Selection） | 矩形区域选择 |
| 多边形选择（Polygonal Selection） | 多边形顶点定义选择区域 |
| 套索选择（Lasso Selection） | 自由绘制选择区域 |
| 画刷选择（Paint Selection） | 画刷半径内选点 |

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块
#include "LidarPointCloudEditorHelper.h"

// 模块接口
#include "ILidarPointCloudEditorModule.h"
```

### 基本用法

以下示例展示如何在 C++ 中操作点云资产，基于 `FLidarPointCloudEditorHelper` 静态工具类：

```cpp
// 来源: LidarPointCloudEditorHelper.h

// 创建新的点云资产
ULidarPointCloud* NewCloud = FLidarPointCloudEditorHelper::CreateNewAsset();

// 将选中的点云对齐到世界原点
FLidarPointCloudEditorHelper::AlignSelectionAroundWorldOrigin();

// 设置选中点云的原始坐标
FLidarPointCloudEditorHelper::SetOriginalCoordinateForSelection();

// 居中选中的点云
FLidarPointCloudEditorHelper::CenterSelection();
```

### 进阶用法

```cpp
// 来源: LidarPointCloudEditorHelper.h

// 合并多个点云资产
TArray<ULidarPointCloud*> Sources;
Sources.Add(CloudA);
Sources.Add(CloudB);
FLidarPointCloudEditorHelper::MergeLidar(TargetAsset, Sources);

// 按组件合并（保留组件结构）
FLidarPointCloudEditorHelper::MergeSelectionByComponent(/* bReplaceSource */ true);

// 按数据合并（合并为单个资产）
FLidarPointCloudEditorHelper::MergeSelectionByData(/* bReplaceSource */ false);

// 为选中点云生成碰撞体
FLidarPointCloudEditorHelper::BuildCollisionForSelection();

// 设置碰撞误差精度
FLidarPointCloudEditorHelper::SetCollisionErrorForSelection(100.0f);

// 计算法线（需要设置质量和噪声容差）
FLidarPointCloudEditorHelper::SetNormalsQuality(40, 1.0f);
FLidarPointCloudEditorHelper::CalculateNormalsForSelection();

// 将点云转换为静态网格体
// bMeshByPoints: true=按点, CellSize: 体素大小, bMergeMeshes: 是否合并, bRetainTransform: 保留变换
FLidarPointCloudEditorHelper::MeshSelected(true, 100.0f, true, true);

// 射线检测点云
FVector2d ScreenPos(512, 384);
FLidarPointCloudRay Ray = FLidarPointCloudEditorHelper::MakeRayFromScreenPosition(ScreenPos);
FVector3f HitLocation;
bool bHit = FLidarPointCloudEditorHelper::RayTracePointClouds(Ray, 1.0f, HitLocation);

// 通过凸体选择点
FConvexVolume Volume = FLidarPointCloudEditorHelper::BuildConvexVolumeFromCoordinates(StartPos, EndPos);
FLidarPointCloudEditorHelper::SelectPointsByConvexVolume(Volume, ELidarPointCloudSelectionMode::Add);

// 通过球体选择点
FSphere SelectionSphere(FVector::ZeroVector, 500.0f);
FLidarPointCloudEditorHelper::SelectPointsBySphere(SelectionSphere, ELidarPointCloudSelectionMode::Add);

// 选择模式枚举
// ELidarPointCloudSelectionMode::None      - 无操作
// ELidarPointCloudSelectionMode::Add        - 添加选择
// ELidarPointCloudSelectionMode::Subtract   - 减去选择
```

### 模块接口访问

```cpp
// 来源: ILidarPointCloudEditorModule.h

// 检查编辑器模块是否可用
if (ILidarPointCloudEditorModule::IsAvailable())
{
    // 获取模块实例
    ILidarPointCloudEditorModule& Module = ILidarPointCloudEditorModule::Get();
    
    // 获取菜单扩展管理器（用于扩展编辑器菜单）
    TSharedPtr<FExtensibilityManager> MenuManager = Module.GetMenuExtensibilityManager();
    
    // 获取工具栏扩展管理器
    TSharedPtr<FExtensibilityManager> ToolBarManager = Module.GetToolBarExtensibilityManager();
}
```

## Demo 示例

### 在编辑器中以编程方式操作点云资产

```cpp
// LidarPointCloudDemo.h
#pragma once

#include "CoreMinimal.h"

class ULidarPointCloud;

class FLidarPointCloudDemo
{
public:
    /** 演示完整的点云处理流程 */
    static void RunDemo();
};
```

```cpp
// LidarPointCloudDemo.cpp
#include "LidarPointCloudDemo.h"
#include "LidarPointCloudEditorHelper.h"

void FLidarPointCloudDemo::RunDemo()
{
    // 1. 创建新的点云资产
    ULidarPointCloud* Cloud = FLidarPointCloudEditorHelper::CreateNewAsset();
    if (!Cloud)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create point cloud asset"));
        return;
    }

    // 2. 假设已有多个点云资产需要合并
    TArray<ULidarPointCloud*> Sources;
    // Sources.Add(OtherCloud1);
    // Sources.Add(OtherCloud2);

    if (Sources.Num() > 0)
    {
        // 3. 合并点云数据
        FLidarPointCloudEditorHelper::MergeLidar(Cloud, Sources);
    }

    // 4. 计算法线
    FLidarPointCloudEditorHelper::SetNormalsQuality(40, 1.0f);
    FLidarPointCloudEditorHelper::CalculateNormalsForSelection();

    // 5. 生成碰撞体（误差 100 单位）
    FLidarPointCloudEditorHelper::SetCollisionErrorForSelection(100.0f);
    FLidarPointCloudEditorHelper::BuildCollisionForSelection();

    // 6. 转换为静态网格体
    FLidarPointCloudEditorHelper::MeshSelected(
        true,     // bMeshByPoints
        100.0f,   // CellSize
        true,     // bMergeMeshes
        true      // bRetainTransform
    );
}
```

## 模块依赖

由于 Build.cs 具体依赖项未在提供的信息中展示完整，基于插件功能推断，除了常见依赖外，可能需要以下模块：

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 编辑器交互工具框架（选择、画刷等工具依赖） |
| `LidarPointCloudRuntime` | 运行时模块（编辑器模块依赖此模块处理核心数据） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退 CL53913857 的改动 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 硬件光线追踪：统一网格批次所有权参数 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配的问题 |

### 维护评价

- **创建时间**：2020 年 1 月，已存在约 6 年
- **维护频率**：近期更新以引擎级重构为主（视口通知机制、光线追踪框架适配），非插件功能层面的更新，说明该插件功能已趋于稳定
- **状态**：维护中，但以跟随引擎架构调整为主，无新功能添加迹象
- **默认关闭**：`EnabledByDefault: false`，需要手动启用
- **已知限制**：仅支持 Win64、Mac、Linux 平台；无官方文档链接
- **推荐**：适合需要处理 LiDAR 点云数据的企业用户使用，功能完善且稳定。但作为企业级插件，社区资源相对较少。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud)
- [官方文档]()（无）