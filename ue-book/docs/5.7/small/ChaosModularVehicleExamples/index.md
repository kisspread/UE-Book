# Chaos Modular Vehicle Examples

> Modular Vehicle Example Assets

| 属性 | 值 |
|---|---|
| 中文名 | 模块化车辆示例 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例关卡、蓝图、静态网格体、材质） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicleExamples) | |

## 用途

本插件是 Chaos Modular Vehicle 系统的配套示例资产包。它提供了一组开箱即用的模块化车辆实例（如轿车、卡车等），展示了如何通过部件拼接（底盘、驾驶室、车轮、货斗等）构建设计可变的车辆。用户可以直接在关卡中部署这些车辆，或将其作为模板加速自己的车辆原型的制作。插件本身不包含任何 C++ 代码，所有功能依赖 ChaosModularVehicle 运行时模块。

## 使用场景

- 快速搭建含可动态组合车身的物理车辆，用于原型验证或展示。
- 学习模块化车辆的设计思路——将车体拆解为独立子部件，每个部件拥有独立的物理碰撞和挂点逻辑。
- 需要直接在关卡中放置多个不同样式的测试车辆，无需手动组装。

## 蓝图用法

本插件为纯内容插件，不暴露自定义蓝图函数或节点。所有可交互内容均存在于 `/Game/ChaosModularVehicleExamples/` 目录下，主要包括：

- **示例关卡**：`Example_ModularVehicle` —— 展示了不同车型在简单地面上行驶的效果。
- **车辆蓝图**：`BP_ModularCar`、`BP_ModularTruck` —— 继承自 `ModularVehicleBase`，已配置好部件挂接。
- **部件蓝图**：如 `BP_Wheel_Sedan`、`BP_Cab_Pickup` 等单一部件，可在蓝图编辑器中替换。

用户应在关卡中拖放上述蓝图，并调整参数（如 `VehicleConfig`）来体验。

## C++ 用法

无。本插件不含任何 C++ 源文件，所有行为由基类（`ChaosModularVehicle` 模块）提供。

## Demo 示例

不适用。插件本身即是一个可运行的示例，直接启用后将包含可在关卡中放置的车辆蓝图。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosModularVehicle` | 提供模块化车辆的核心运行时逻辑、部件挂载与物理模拟 |
| `ChaosVehiclesCore` | 基础车辆物理引擎（被 `ChaosModularVehicle` 引用） |

> 其他依赖（如 `Engine`、`CoreUObject` 等）均为标准模块，此处省略。

## 维护状态

### 近期更新

- 2024-02-06 `c28bbea` 原始提交：新增模块化车辆示例资产插件

### 维护评价

该插件自创建以来（约 1 年）未有更新。由于是实验性示例资产，且代码层由主模块 `ChaosModularVehicle` 维护，本身属于静态内容包，不活跃是正常的。其资产质量稳定，适用于快速原型和教学。**建议启用前先确认主模块 `ChaosModularVehicle` 已启用并处于可用状态。**

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicleExamples)
- [ChaosModularVehicle 主模块文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-modular-vehicle-overview)（官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosModularVehicleExamples/Content)（即插件自身的内容目录）