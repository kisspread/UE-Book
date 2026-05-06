# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 学习智能体 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `Learning` (Runtime), `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime), `LearningTraining` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents) | |

## 总体用途

Learning Agents 是 Epic Games 开发的一套机器 学习插件，旨在让游戏开发者无需深厚的 ML 背景即可将强化学习和模仿学习集成到 Unreal 项目中。它提供了智能体环境交互、观测 / 动作抽象、训练调度、数据回放以及编辑器集成等功能，覆盖从训练到部署的全流程。插件设计为可扩展的模块化架构，核心 `Learning` 与 `LearningTraining` 提供底层算法和数值工具，而 `LearningAgents`、`LearningAgentsTraining` 等高层模块则封装了面向蓝图和 C++ 的易用接口。

## 模块列表

| 模块 | 类型 | 一句话说明 | 文档 |
|---|---|---|---|
| `Learning` | Runtime | 机器学习核心库，包含张量、优化器、网络等基础组件。 | [Learning](./Learning.md) |
| `LearningAgents` | Runtime | 智能体高层集成层，提供观测、动作、奖励等蓝图可调用功能。 | [LearningAgents](./LearningAgents.md) |
| `LearningAgentsReplay` | Runtime | 回放系统，用于离线记录和重放训练数据。 | [LearningAgentsReplay](./LearningAgentsReplay.md) |
| `LearningAgentsTraining` | Runtime | 训练调度和执行模块，管理训练循环、配置与结果。 | [LearningAgentsTraining](./LearningAgentsTraining.md) |
| `LearningAgentsTrainingEditor` | Runtime | 编辑器扩展，提供训练任务的可视化配置和调试工具。 | [LearningAgentsTrainingEditor](./LearningAgentsTrainingEditor.md) |
| `LearningTraining` | Runtime | 底层训练算法实现，包括策略梯度、PPO 等。 | [LearningTraining](./LearningTraining.md) |

## 使用场景

- **训练游戏 AI 智能体**：通过强化学习让角色自主学会走路、奔跑、躲避障碍等行为，无需手写复杂的行为树。
- **模仿学习**：录制人类玩家的操作数据（如控制角色行走），让 AI 学会模仿，实现更自然的动作。
- **在线 / 离线训练**：直接在编辑器内运行训练，或导出数据到外部环境进行大规模训练。
- **回放与调试**：使用 `LearningAgentsReplay` 观察历史训练过程，分析策略收敛情况。
- **自定义神经网络架构**：基于 `Learning` 模块的低级张量 API 构建自定义网络层。

## 模块依赖

插件不依赖除标准 Core/Engine 外的公共模块。各模块具体依赖请参考相应模块文档。

| 模块 | 独特依赖 | 说明 |
|---|---|---|
| `LearningAgentsTraining` | `UnrealEd` | 编辑器环境下启动训练需要编辑器功能支持 |

其余模块无特殊依赖（仅标准 Core、CoreUObject、Engine 等）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/learning-agents-in-unreal-engine/)（5.7 新版）
- 各模块文档：请见上述模块列表中的链接