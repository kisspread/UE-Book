# RigLogic for UAF

> RigLogic for UAF

| 属性 | 值 |
|---|---|
| 中文名 | 角色逻辑UAF集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、骨骼网格体模板） |
| 模块 | `RigLogicUAF` (Runtime), `RigLogicUAFUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicUAF) | |

## 总体用途

**RigLogic for UAF** 是 UE5 实验性插件，将 **RigLogic**（肌肉/面部变形解算器）集成到 **UAF（Unreal Animation Framework）** 动画图中。它提供新的动画节点和编辑器工具，使动画师能够在 UAF 蓝图或动画图表中直接使用 RigLogic 的解算能力，实现更真实的面部动画及肢体扭曲变形。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [RigLogicUAF](RigLogicUAF.md) | Runtime | 提供在 UAF 动画图中使用的 RigLogic 节点和运行时逻辑 |
| [RigLogicUAFUncookedOnly](RigLogicUAFUncookedOnly.md) | UncookedOnly | 提供编辑器导入、缓存生成等未烹饪时所需的工具支持 |

## 使用场景

- **面部动画增强**：在 UAF 动画图表中插入 RigLogic 解算节点，驱动高精度面部变形。
- **角色自定义变形**：利用 RigLogic 对骨骼、肌肉进行实时调节，实现角色体型或表情的实时变化。
- **动画回放优化**：在动画蓝图中混合 RigLogic 解算结果与标准动画，提升最终输出质量。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicUAF)
- [UAF 概述（官方）](https://dev.epicgames.com/documentation/unreal-engine/unreal-animation-framework)