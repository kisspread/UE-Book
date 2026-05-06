# Chaos Modular Vehicle

> Modular Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | 模块化车辆 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle) | |

## 总体用途

Chaos Modular Vehicle 插件提供了一套基于 Chaos 物理引擎的模块化车辆系统。与传统的单一车辆体不同，该插件允许将车辆分解为多个独立模拟的部件（如底盘、车轮、悬架、发动机等），每个部件作为独立的物理体进行交互，并通过约束和连接器组合成完整的车辆。这种方式支持更精细的损伤、部件脱落、可替换组件等动态效果，适合需要高物理真实感的车辆模拟场景（如赛车游戏、载具破坏系统）。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [ChaosModularVehicle](ChaosModularVehicle.md) | Runtime | 核心运行时模块，定义车辆部件框架、物理约束及模拟逻辑 |
| [ChaosModularVehicleEngine](ChaosModularVehicleEngine.md) | Runtime | 车辆动力系统模块，处理引擎、传动、变速等力学计算 |
| [ChaosModularVehicleEditor](ChaosModularVehicleEditor.md) | UncookedOnly | 编辑器工具模块，提供车辆蓝图创建、部件装配及调试界面 |

## 使用场景

- 需要高度可破坏/可交互的车辆系统，每个部件可独立受影响
- 模块化车辆组装：允许玩家或设计师自由组合底盘、车轮、武器等部件
- 赛车模拟中，单个部件损坏影响行驶性能（如爆胎、引擎故障）
- 基于 Chaos 物理的载具需要更高灵活性的物理耦合方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicle)
- [ChaosModularVehicle 模块文档](ChaosModularVehicle.md)
- [ChaosModularVehicleEngine 模块文档](ChaosModularVehicleEngine.md)
- [ChaosModularVehicleEditor 模块文档](ChaosModularVehicleEditor.md)