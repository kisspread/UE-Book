# Chaos Vehicles Plugin

> Chaos Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | 混沌车辆 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时逻辑、编辑器工具） |
| 模块 | `ChaosVehicles` (Runtime), `ChaosVehiclesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosVehiclesPlugin) | |

## 总体用途

Chaos Vehicles Plugin 是 UE5 基于 Chaos 物理引擎的车辆模拟插件。它提供了完整的车辆动力学模拟框架，包括车轮、悬挂、发动机、变速箱、差速器等核心部件，支持轮式车辆的物理驱动，并提供了编辑器工具用于配置车辆参数和调试。该插件旨在替代旧的 PhysX 车辆系统，充分利用 Chaos 的高性能物理计算能力。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `ChaosVehicles` | Runtime | 核心车辆模拟运行时模块，实现车辆动力学、车轮模型、物理交互等逻辑。 |
| `ChaosVehiclesEditor` | UncookedOnly | 编辑器支持模块，提供车辆数据资产自定义、调试可视化、物理参数编辑等工具。 |

## 使用场景

- **制作赛车游戏或载具模拟游戏**：需要真实物理反馈的车辆操控，如漂移、悬挂动态、轮胎抓地力模拟。
- **开放世界载具系统**：支持多种车辆类型（轿车、卡车、越野车）的物理属性配置，适用大规模场景。
- **需要自定义车辆物理行为的项目**：通过可配置的部件参数（发动机扭矩、齿轮比、悬挂刚度等）实现差异化驾驶体验。
- **从 PhysX 迁移到 Chaos 物理的项目**：官方推荐的 Chaos 车辆集成方案，与 Chaos 碰撞、布料、破坏等系统协同工作。

## 进阶参考

- 各模块详细 API 和蓝图节点请参阅：
  - [ChaosVehicles 模块文档](./ChaosVehicles.md)
  - [ChaosVehiclesEditor 模块文档](./ChaosVehiclesEditor.md)
- 完整测试用例位于 `Engine/Plugins/Experimental/ChaosVehiclesPlugin/Tests/` 目录。

## 维护状态

### 近期更新（来自 git log）

- **2025-07-28** `b8b21b7a` — 修复物理求解器时间缓存为 32 位浮点数导致精度丢失的若干问题
- **2025-06-09** `87ed9fc8` — 消除 `UChaosWheeledVehicleMovementComponent::DrawDebug` 中的除零编译器 SA 警告
- **2025-06-09** `4e0b9b90` — 修复关闭时崩溃的 bug
- **2025-06-05** `0500d1c4` — 修复慢速行驶时因小台阶阻挡车辆的 bug（修正了错误的法线）
- **2025-05-22** `39d3ddff` — 将一条日志警告改为低优先级日志

### 维护评价

- **创建时间**：2025-05-22（约 2 个月前）
- **近期更新**：连续 4 次功能性修复和优化，针对精度、崩溃、行为错误均有处理
- **活跃度**：高频维护（月均 2-3 次 commit），开发者持续跟进反馈
- **已知问题**：实验性插件，可能存在未发现或性能瓶颈，建议在项目早期集成测试
- **推荐度**：✅ 推荐使用，尤其是基于 Chaos 物理的新项目；生产环境需充分验证

## 相关链接

- [源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosVehiclesPlugin)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/chaos-vehicles-in-unreal-engine/)（UE 官方 Chaos Vehicles 概述，非插件专属）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosVehiclesPlugin/Tests)