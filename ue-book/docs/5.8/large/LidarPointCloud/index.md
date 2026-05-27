# LiDAR Point Cloud Support

> Adds support for importing, processing and rendering of LiDAR Point Clouds.

| 属性 | 值 |
|---|---|
| 中文名 | 激光雷达点云支持 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `LidarPointCloudRuntime` (Runtime), `LidarPointCloudEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud) | |

## 用途

本插件专为在 Unreal Engine 中处理和使用**激光雷达（LiDAR）扫描数据**而设计。它解决的核心问题是将海量的、非结构化的三维点云数据（通常由激光雷达设备采集）高效地导入引擎，并以交互式的方式进行渲染、编辑和集成到场景中。传统模型资产无法直接承载此类数据，因此本插件提供了专门的数据结构、渲染管线和编辑器工具链，使其成为建筑信息模型（BIM）、数字孪生、自动驾驶仿真、影视特效和地理空间应用中的关键技术组件。

## 使用场景

- **建筑与基础设施逆向建模**：将激光扫描得到的建筑、工厂或历史遗迹的点云数据导入 UE，用于测量、可视化或作为改造设计的参考底图。
- **自动驾驶仿真**：在虚拟环境中还原真实世界道路场景，用于测试自动驾驶算法对周围环境（如建筑物、树木、交通设施）的感知能力。
- **地理信息系统（GIS）集成**：导入地形、城市或林业的 LiDAR 数据，创建大规模的开放世界或用于景观规划分析。
- **影视与虚拟制片**：快速搭建基于真实环境扫描的虚拟场景，用于预演或实时合成。

## 蓝图用法

### 核心节点 (运行时)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPointAt` | 根据索引获取单个点云数据点 | `ULidarPointCloud` |
| `GetPointsInBox` | 获取包围盒内的所有点云数据 | `ULidarPointCloud` |
| `SetRenderType` | 设置点云的渲染模式（例如，根据高度或强度着色） | `ALidarPointCloudActor` |

### 核心节点 (编辑器)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportLidarPointCloud` | 通过文件路径导入一个点云文件并创建资产 | `ULidarPointCloudFactory` |
| `ReimportLidarPointCloud` | 重新导入一个已存在的点云资产 | `ULidarPointCloudFactory` |

### 使用示例（蓝图描述）
1.  **导入数据**：在内容浏览器右键，选择“Import”，选择支持的点云文件（如 .las, .laz）。`ULidarPointCloudFactory` 会自动创建 `ULidarPointCloud` 资产。
2.  **放置到场景**：将 `ULidarPointCloud` 资产从内容浏览器拖入视口，会自动生成一个 `ALidarPointCloudActor`。
3.  **控制显示**：在 Actor 的详情面板中，可以通过蓝图或直接设置其“渲染类型”、“点大小”、“颜色映射”等属性来改变点云的显示效果。

## C++ 用法

### 头文件引入

```cpp
#include "LidarPointCloud.h" // 核心数据结构
#include "LidarPointCloudActor.h" // 场景中的Actor
```

### 基本用法

核心数据结构 `FLidarPointCloudPoint` 代表一个点云数据点，通常通过 `ULidarPointCloud` 对象访问。
*(来源: LidarPointCloudRuntime/Public/LidarPointCloudPoint.h)*

```cpp
// 假设已有一个 ULidarPointCloud* PointCloudAsset
int32 NumPoints = PointCloudAsset->GetNumPoints();
for (int32 i = 0; i < NumPoints; ++i)
{
    const FLidarPointCloudPoint& Point = PointCloudAsset->GetPoint(i);
    FVector PointLocation = Point.Location; // 世界坐标
    FVector PointColor = Point.Color; // RGB颜色
    // ... 处理点数据
}
```

### 进阶用法

使用空间查询来筛选点云数据，这对于交互（如鼠标选取）或空间分析至关重要。
*(综合自运行时模块的空间查询接口)*

```cpp
// 在某个世界包围盒内查询点
FBox QueryBounds = FBox(FVector(-100, -100, -100), FVector(100, 100, 100));
TArray<FLidarPointCloudPoint> PointsInRegion;
PointCloudAsset->GetPointsInBox(QueryBounds, PointsInRegion);

// 根据结果进行高亮或分析
for (const FLidarPointCloudPoint& Point : PointsInRegion)
{
    // 执行高亮、统计或其他逻辑
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderingCore` | 提供底层渲染接口和资源管理 |
| `EditorFramework` | 为编辑器模块提供基础框架和视口交互支持 |
| `UnrealEd` | 提供资产工厂、编辑器工具和自定义资产类型的功能 |
| `PropertyEditor` | 用于在详情面板中自定义点云资产的属性编辑界面 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口代码重构：优化客户端关联/解关联通知逻辑 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了之前的变更 (CL53913857) |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口代码重构：与上一条相关，优化关联逻辑 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 硬件光线追踪支持：改进动态几何体更新参数中的网格批次管理 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中32位与64位格式说明符混用的问题 |

### 维护评价

该插件创建于2020年初，已有超过5年历史。从提交记录看，其维护**不规律但尚未停止**。最近的更新（2026年5月）主要围绕引擎底层的视口系统和硬件光线追踪（HWRT）接口进行适配和重构，这表明该插件仍在随着引擎主干同步更新，以确保兼容性和基础功能。然而，近年来没有看到显著的**功能增强**（如支持新格式、性能优化等）提交。考虑到其为企业级插件、相对稳定，且最近仍有维护迹象，**推荐在需要处理激光雷达数据的项目中使用**，但需注意它默认禁用，需手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud/Tests)