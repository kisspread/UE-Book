# Chaos Modular Vehicle

> Modular Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | 混沌模块化载具 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle) | |

## 用途

ChaosModularVehicle 是基于 Chaos 物理引擎的模块化载具系统。与传统载具系统将所有部件耦合不同，该插件将载具拆分为可独立配置的模块（底盘、发动机、传动系统等），每个模块拥有独立的物理模拟和网络同步逻辑。

该插件存在的原因是为了解决复杂载具系统的模块化需求——允许开发者在运行时动态组合载具部件，实现高度可定制的载具行为，同时保持与 Chaos 物理系统和 UE5 网络预测框架的深度集成。

## 使用场景

- 你需要一个可以动态组装/拆卸部件的载具系统（如赛车改装、机甲组装）
- 你的游戏需要多个独立可配置的载具模块（独立的引擎、变速箱、悬挂）
- 你需要在网络多人游戏中实现载具物理同步
- 你希望在编辑器中可视化配置模块化载具参数

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `ChaosModularVehicle` | Runtime | 核心运行时模块，提供模块化载具的基础框架、物理模拟和网络同步 |
| `ChaosModularVehicleEngine` | Runtime | 发动机模拟模块，处理引擎扭矩、转速和传动系统逻辑 |
| `ChaosModularVehicleEditor` | UncookedOnly | 编辑器工具模块，提供载具模块的可视化配置和调试界面 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle)
- [模块详情：ChaosModularVehicle](ChaosModularVehicle.md)
- [模块详情：ChaosModularVehicleEngine](ChaosModularVehicleEngine.md)
- [模块详情：ChaosModularVehicleEditor](ChaosModularVehicleEditor.md)