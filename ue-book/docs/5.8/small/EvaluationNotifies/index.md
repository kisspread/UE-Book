# Evaluation Notifies

> A system for animation notifies which have animation evaluation time code.

| 属性 | 值 |
|---|---|
| 中文名 | 求值通知 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画相关资产） |
| 模块 | `EvaluationNotifiesRuntime` (Runtime), `EvaluationNotifiesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EvaluationNotifies) | |

## 用途
为动画通知（Anim Notify）系统引入“动画求值时间码”机制。其核心目的是解决动画求值阶段与通知触发之间的时间对齐问题，允许通知精确响应动画曲线求值过程中的特定时间点或状态，而非仅在游戏线程的更新周期中触发。这使得动画驱动的逻辑（如特效、音效、游戏玩法事件）能够与动画数据的处理时机更加紧密地同步。

## 使用场景
- 你需要基于动画曲线求值过程中的精确时间点（而非帧更新点）来触发通知。
- 你的动画系统（如基于 `AnimWarping` 或 `RigVM`）需要通知与求值阶段紧密同步。
- 你正在开发实验性的高级动画功能，需要更细粒度的事件触发控制。

## 模块列表

| 模块 | 说明 |
|---|---|
| `EvaluationNotifiesRuntime` | 提供求值通知系统的核心运行时逻辑，包括通知定义、调度和求值时间码的集成。 |
| `EvaluationNotifiesEditor` | 提供用于在编辑器中配置和调试求值通知的工具与用户界面。 |

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EvaluationNotifies)
- [Runtime 模块文档](EvaluationNotifiesRuntime.md)
- [Editor 模块文档](EvaluationNotifiesEditor.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-24 | `42548e51` | Fix non-unity build: forward-declare UAnimationAsset in anim node headers | 修复非统一编译错误，在动画节点头文件中前向声明类。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新格式。 |
| 2026-04-10 | `8ce934ce` | MotionWarping - fix for FAlignmentNotifyInstance::GetWeight and URootMotionModifier_PrecomputedWarp: | 修复运动扭曲中相关通知实例和根运动修饰器的权重计算问题。 |
| 2026-02-09 | `1be7393a` | Gracefully handle notify dispatch failure when no animation sequence is playing | 当没有动画序列播放时，优雅地处理通知分发失败。 |
| 2025-11-24 | `1e8772b6` | UAF: Timelines can now fail state & delta queries | UAF 模块：时间线现在可以处理状态和增量查询失败。 |

### 维护评价
- **活跃维护**：创建于2024年底，且在最近6个月内有多次实质性代码更新，包括功能修复（运动扭曲、失败处理）和代码维护（编译修复、日志迁移），表明该实验性插件仍在积极开发中。
- **推荐使用**：作为实验性插件，适合在希望探索高级动画同步技术的新项目或实验性功能中采用。由于其依赖 `AnimationWarping`, `RigVM`, `UAF` 等模块，引入前需评估项目依赖的复杂性。目前版本为 0.1，API 和功能可能发生变化。