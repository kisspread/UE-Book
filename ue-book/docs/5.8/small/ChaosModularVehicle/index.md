# Chaos Modular Vehicle

> Modular Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | 模块化载具 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（载具相关资产） |
| 模块 | `ChaosModularVehicle` (Runtime), `ChaosModularVehicleEngine` (Runtime), `ChaosModularVehicleEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle) | |

## 用途
该插件提供了一个基于 Chaos 物理引擎的**模块化载具（Modular Vehicle）框架**。其核心目标是解耦传统载具系统的各个组件（如车身、悬挂、车轮、引擎），将它们设计为可独立配置、自由组合的“模块”。这允许开发者像搭积木一样构建高度自定义的车辆，而无需编写大量继承或硬编码逻辑。它解决了传统载具蓝图/类继承方式不够灵活、难以复用和修改的问题，特别适用于需要动态改装、部件可更换或拥有大量异构载具的游戏。

## 使用场景
- **赛车/竞速游戏**：为不同车辆品牌、级别或改装件创建差异巨大的物理表现，而无需为每辆车编写独立的载具蓝图。
- **载具模拟/改装游戏**：实现游戏中实时的部件更换（如更换轮胎、悬挂），并实时影响车辆的物理属性。
- **多人游戏开发**：插件内置了对网络同步的支持（从近期提交记录可见），非常适合开发需要精确同步的网络载具。

## 蓝图用法
作为实验性插件，其蓝图 API 主要服务于载具的组装和初始化。
**注意**：由于插件处于实验阶段，且 `Installed: false`，蓝图节点可能不在常规菜单中直接暴露，通常需要配合 C++ 使用或通过实验性窗口访问。

### 核心概念
- **模块化部件**：通过不同的 Actor Component 来表示车辆的各个部分（如底盘、轮组）。
- **组装与配置**：在载具生成或运行时，将各模块组件组合在一起，并由管理类协调它们的物理交互。

## C++ 用法
该插件的核心逻辑和物理模拟主要在 C++ 中实现。使用它通常涉及：
1.  **继承或集成**：继承或组合插件提供的基础模块类。
2.  **配置**：在代码或配置中定义各个模块的物理参数（如质量、悬挂刚度、引擎扭矩曲线）。
3.  **组装**：在运行时实例化这些模块并组装到一个载具实体上。
4.  **输入处理**：通常与 `EnhancedInput` 插件结合，将玩家输入映射到载具模块的控制接口。

## 模块依赖
| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 处理和映射载具相关的输入操作。 |
| `ChaosPhysics` / `ChaosVehicles` | 底层 Chaos 物理引擎及载具支持。 |
| `ControlRig` / `PhysicsControl` | 可能用于更高级的骨骼/物理控制。 |

## 维护状态
### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `cd96428a` | ChaosModularVehicle: Fix ShowDebug engine torque always reporting 0 | 修复调试显示中引擎扭矩始终显示为 0 的 bug。 |
| 2026-04-23 | `be90176f` | Modular Vehicle: Fix the vehicle setup for the simplified skeletal mesh case when running networked. | 修复网络模式下使用简化骨骼网格体时的载具初始化问题。 |
| 2026-04-16 | `4ea9aba8` | [NetPhysics] Fix IsLocallyControlled ensure on physics thread in ModularVehicle | 修复物理线程中“是否本地控制”判断的断言错误。 |
| 2026-04-14 | `bd0ef478` | [ModularVehicle] Rely on NetworkPhysicsComponent.IsLocallyControlled from the Modular Vehicle instea | 重构逻辑，使用统一的 `NetworkPhysicsComponent` 来判断本地控制。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出迁移到新的 UE_LOGF 宏。 |

### 维护评价
- **状态**：**活跃维护中**。插件创建于2023年底，近期（2026年4-5月）仍在持续进行重要的 bug 修复和功能优化，特别是围绕**网络同步**和**物理线程交互**的稳定性。
- **建议**：这是一个**实验性**插件（`IsExperimentalVersion: true`），且默认未安装。这意味着其 API 可能不稳定，随时可能变动。它非常适合愿意跟进实验性功能、有深度定制载具需求的项目。在生产环境中使用需要自行承担兼容性风险，并密切关注引擎更新。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosModularVehicle/Tests) (推测路径，可能位于引擎的通用测试目录中)