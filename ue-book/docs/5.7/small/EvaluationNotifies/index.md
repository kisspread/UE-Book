# Evaluation Notifies

> A system for animation notifies which have animation evaluation time code.

| 属性 | 值 |
|---|---|
| 中文名 | 评估通知 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `EvaluationNotifiesRuntime` (Runtime), `EvaluationNotifiesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EvaluationNotifies) | |

## 总体用途

该插件提供了一种**与动画评估时间线紧密绑定的通知系统**。传统动画通知仅在动画播放的“帧”级别触发；而本插件允许在动画评估过程中的任意**时间代码（Evaluation Time Code）** 点触发逻辑，从而在程序化动画、动画蓝图或 Motion Matching 等场景中实现更精确、可量化的交互反馈。它是实验性功能，为未来更高级的动画控制打下基础。

## 子模块总览

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `EvaluationNotifiesRuntime` | Runtime | 运行时核心，定义通知数据结构、评估时间代码的处理逻辑，以及在动画实例中触发通知的机制。 |
| `EvaluationNotifiesEditor` | UncookedOnly | 编辑器扩展，提供可视化创建、编辑和管理评估通知的工具，包括自定义细节面板和动画图表集成。 |

详细 API 与用法请参阅：
- [EvaluationNotifiesRuntime 文档](EvaluationNotifiesRuntime.md)
- [EvaluationNotifiesEditor 文档](EvaluationNotifiesEditor.md)

## 使用场景

- **精准打击帧**：在动作游戏中，需要精确控制拳/脚在动画时间轴中的命中判定，使用评估时间代码（如 `TimeCode(1.23s)`）而非帧号。
- **程序化动画反馈**：结合 `AnimationWarping` 或 `RigVM` 插件，在动画解算的特定时间点触发 IK 校正或风效果。
- **运动匹配（Motion Matching）**：当动画片段被动态混合时，需要按时间代码触发声音、粒子或输入响应，而非固定通知。
- **动画测试与调试**：在开发阶段，对每个评估时间点设置断点或日志，验证动画逻辑是否正确。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EvaluationNotifies)
- [官方文档](https://docs.unrealengine.com/)（暂无单独页面，可在 Animation 系统搜索“Evaluation Notifies”）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EvaluationNotifies/Tests)（如存在）