# LidarPointCloud

> Adds support for importing, processing and rendering of LiDAR Point Clouds.

| 属性 | 值 |
|---|---|
| 中文名 | 激光雷达点云 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（点云材质、渲染资源） |
| 模块 | `LidarPointCloudRuntime` (Runtime), `LidarPointCloudEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud) | |

## 用途

为 Unreal Engine 提供完整的 LiDAR 点云数据支持管线。LiDAR（激光雷达）扫描产生的点云数据通常包含数百万甚至数十亿个三维点，每个点带有位置、颜色、强度等属性。本插件解决的核心问题是：如何高效地将这些海量点云数据导入引擎，并在运行时和编辑器中进行可视化渲染。

插件的典型数据源包括：机载/车载 LiDAR 扫描、建筑 BIM 扫描、地形测绘等场景产生的 `.las`、`.laz` 等标准点云格式文件。Runtime 模块负责点云数据的加载、LOD 管理和渲染；Editor 模块提供导入向导、编辑器内预览和点云资产的管理工作流。

**注意**：此插件默认未启用，需在 Plugins 面板手动启用或通过项目配置启用。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `LidarPointCloudRuntime` | Runtime | 点云数据的核心运行时支持，包含点云资产类型、LOD 系统、渲染管线集成和数据加载 |
| `LidarPointCloudEditor` | Editor | 编辑器专用功能，提供点云文件导入、资产编辑器、编辑器内视口预览和属性面板 |

## 使用场景

- 你在做建筑/基建项目的数字孪生可视化 → 导入 LiDAR 扫描数据作为场景参考
- 你在做自动驾驶仿真 → 加载车载 LiDAR 扫描的道路环境点云
- 你在做影视/虚拟制片 → 使用 LiDAR 扫描的真实场景重建数字资产
- 你在做地形测绘/GIS 应用 → 导入大规模地形点云数据进行可视化分析
- 你需要在 UE 中预览和检查点云数据质量 → 使用编辑器导入和查看功能

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud)
- Runtime 模块文档: LidarPointCloudRuntime.md
- Editor 模块文档: LidarPointCloudEditor.md

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联/解除关联的通知机制重构 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了某个提交，修复引入的问题 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联通知重构（被回退后重新提交） |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 硬件光线追踪动态几何更新参数中添加 MeshBatchesView |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符不匹配问题 |

### 维护评价

- **活跃维护**：最近 1 个月内有多次更新（2026-04 至 2026-05），且涉及核心渲染管线改动
- 更新内容偏向引擎底层框架适配（视口重构、硬件光线追踪支持、编译警告修复），说明该插件仍在跟随引擎主版本演进
- 作为 Enterprise 类插件，由 Epic 官方维护，质量有保障
- 默认未启用（`EnabledByDefault=false`），属于按需使用的专业功能模块
- **推荐使用**：如果项目需要处理 LiDAR 点云数据，这是引擎内置的官方解决方案，维护状态良好