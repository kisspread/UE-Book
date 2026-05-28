# ChaosVehiclesPlugin

> Chaos Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 载具插件 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ChaosVehicles` (Runtime), `ChaosVehiclesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosVehiclesPlugin) | |

## 用途

基于 Chaos 物理引擎的载具模拟系统，为 UE5 提供真实的车辆物理行为。该插件包含完整的车轮悬挂、引擎、变速箱、差速器等子系统模拟，支持蓝图和 C++ 两种方式驱动载具。与旧版 PhysX Vehicle 插件（`VehiclePlugin`）平行存在，是 Epic 迁移到 Chaos 物理引擎后的载具解决方案。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`ChaosVehicles`](ChaosVehicles.md) | Runtime | 核心载具物理模拟，包含引擎、变速箱、悬挂、车轮等子系统及动画组件 |
| [`ChaosVehiclesEditor`](ChaosVehiclesEditor.md) | UncookedOnly | 编辑器支持，提供载具相关资产的自定义编辑器和属性面板 |

## 使用场景

- 你在做一个赛车或竞速游戏 → 用此插件提供物理驱动的载具模拟
- 你需要真实的车辆悬挂、引擎扭矩、变速箱换挡逻辑 → 使用 `UChaosVehicleMovementComponent`
- 你需要基于物理的车轮动画驱动 → 使用 `UChaosVehicleAnimInstance`
- 你有自定义载具资产类型需要编辑器 UI → 依赖 `ChaosVehiclesEditor` 模块

## 蓝图用法

详见各模块文档中的蓝图 API 说明。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetThrottleInput` / `SetSteeringInput` / `SetBrakeInput` | 控制载具油门、转向、刹车输入 | `UChaosVehicleMovementComponent` |
| `SetHandbrakeInput` | 手刹控制 | `UChaosVehicleMovementComponent` |
| `GetEngineRPM` / `GetForwardSpeed` | 获取引擎转速和前进速度 | `UChaosVehicleMovementComponent` |
| `SetTransmissionType` | 切换手动/自动变速箱 | `UChaosVehicleMovementComponent` |

## C++ 用法

### 头文件引入

```cpp
#include "ChaosVehicles/ChaosVehicles.h"
```

### 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosVehicles` | 载具物理运行时核心，蓝图和 C++ 均需依赖 |
| `PhysicsCore` | Chaos 物理引擎底层支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `400ae955` | OG Vehicle Plugin - Fix automatic transmission stuck in neutral when RPM exceeds ChangeUpRPM | 修复自动变速箱在 RPM 超过换挡阈值时卡在空挡的问题 |
| 2026-05-12 | `6d7bcebe` | Fix UE-376288: Add HasEngine() checks before GetEngine() calls | 修复调用 GetEngine() 前缺少引擎存在性检查导致的崩溃 |
| 2026-04-30 | `194ad803` | Simple crash bug fix in original vehicle plugin | 修复旧版载具插件的一个简单崩溃 bug |
| 2026-04-23 | `97afe1bb` | [NetPhysics] Feature: Adaptive resim coalescing + MergeData semantics | 网络物理新增自适应重模拟合并及 MergeData 语义 |

### 维护评价

该插件自 2020 年创建以来持续维护，2026 年仍有活跃更新。近期提交集中在 **bug 修复**（变速箱逻辑、崩溃防护）和 **网络物理特性增强**。需要注意的是：

- **实验性状态**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，需在项目设置中手动启用
- **持续活跃**：最近 1 个月内有多次功能性修复，维护状态良好
- **与旧版并存**：部分 commit（`400ae955`、`194ad803`）涉及的是旧版 `VehiclePlugin` 的修复，说明两个插件共享部分底层逻辑
- **推荐使用**：适合需要 Chaos 物理载具的项目，但需注意实验性标签意味着 API 可能在未来版本变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosVehiclesPlugin)
- [ChaosVehicles 模块文档](ChaosVehicles.md)
- [ChaosVehiclesEditor 模块文档](ChaosVehiclesEditor.md)