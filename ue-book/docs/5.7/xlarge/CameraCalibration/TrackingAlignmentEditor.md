# Camera Calibration - TrackingAlignmentEditor 模块

> Framework to support lens distortion and camera calibration in engine.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（镜头校准数据资产、预设） |
| 模块 | `CameraCalibrationEditor` (Runtime), `TrackingAlignment` (Runtime), `TrackingAlignmentEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration) | |

---

## 模块概述

**TrackingAlignmentEditor** 是 CameraCalibration 插件中的一个编辑器模块，专门用于追踪数据与镜头校准之间的对齐工具。该模块为虚拟制片工作流提供追踪系统（如 MoCap、光学追踪）与摄像机校准数据之间的精确对齐能力。

### 在插件中的位置

```
CameraCalibration/
├── CameraCalibrationEditor/    ← 主编辑器模块（镜头畸变校准 UI）
├── TrackingAlignment/          ← 运行时追踪对齐核心逻辑
└── TrackingAlignmentEditor/    ← 本模块（追踪对齐编辑器工具）
```

---

## 用途

该模块解决虚拟制片中的一个关键问题：**如何将外部追踪系统的数据与 Unreal Engine 中的摄像机校准精确对齐**。

在虚拟制片场景中，通常需要：
1. 使用物理摄像机拍摄真实场景
2. 使用追踪系统记录摄像机的运动轨迹
3. 在 UE 中使用校准后的虚拟摄像机渲染 CG 内容
4. **将追踪数据与校准后的虚拟摄像机精确对齐** ← 本模块解决的问题

追踪数据和镜头校准数据来自不同的系统，可能存在坐标系差异、偏移、旋转误差等问题。TrackingAlignmentEditor 提供工具来可视化和修正这些对齐误差。

---

## 使用场景

- **LED 虚拟制片**：将摄像机追踪系统（如 OptiTrack、Vicon）的数据与 nDisplay 集群中的虚拟摄像机对齐
- **绿幕合成**：确保追踪摄像机的运动与 CG 场景的镜头畸变校准一致
- **混合现实拍摄**：实时对齐真实摄像机追踪与虚拟场景渲染
- **镜头校准验证**：在实际拍摄环境中验证镜头校准参数的准确性

---

## 蓝图用法

由于该模块主要面向编辑器工具，蓝图 API 较少。核心功能通过编辑器 UI 面板暴露。

### 核心功能

| 功能 | 说明 | 访问方式 |
|---|---|---|
| 追踪对齐工具 | 可视化追踪数据与校准数据的对齐状态 | 编辑器面板 |
| 对齐参数调整 | 调整偏移、旋转等对齐参数 | 编辑器面板 |
| 对齐数据保存 | 将对齐结果保存为资产 | 编辑器面板 |

---

## C++ 用法

### 头文件引入

```cpp
#include "TrackingAlignmentEditor.h"
```

### 模块依赖

在你的 `.Build.cs` 文件中添加：

```cpp
PublicDependencyModuleNames.AddRange(new string[]
{
    "TrackingAlignment",
    "TrackingAlignmentEditor"
});
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TrackingAlignment` | 追踪对齐的核心运行时逻辑 |
| `CameraCalibrationCore` | 镜头校准核心数据结构 |
| `LensComponent` | 镜头组件，提供校准数据接口 |

---

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2021-04-29 | `fcf82a98f07f` | 初始提交：将 TrackingAlignment 工具添加到 CameraCalibration 插件 |

### 维护评价

- **创建时间**：2021-04-29（约 4 年前）
- **更新频率**：仅有一次初始提交，无后续更新记录
- **状态**：⚠️ **可能不活跃**
- **实验性**：是（IsBetaVersion=true）

**警告**：该模块自创建以来仅有一次提交，且标记为 Beta 版本。在生产环境中使用前请充分测试，并关注 Epic 的更新计划。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/camera-calibration-in-unreal-engine/)（虚拟制片镜头校准）

---

## 插件汇总页导航

本文档是 CameraCalibration 插件的子模块文档。该插件包含以下模块：

| 模块 | 说明 | 文档 |
|---|---|---|
| CameraCalibrationEditor | 主编辑器模块，镜头畸变校准 UI 和工具 | [待生成] |
| TrackingAlignment | 追踪对齐运行时核心逻辑 | [待生成] |
| TrackingAlignmentEditor | 追踪对齐编辑器工具 | **本文档** |