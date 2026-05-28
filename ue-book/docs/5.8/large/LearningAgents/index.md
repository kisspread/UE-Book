# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 学习代理 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例资产） |
| 模块 | `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningAgents) | |

## 用途

Learning Agents 是一个为游戏 AI 角色控制设计的机器学习库。它封装了强化学习（Reinforcement Learning）和模仿学习（Imitation Learning）的核心流程，将复杂的机器学习算法与 UE5 的游戏世界无缝集成。开发者无需深入了解底层 ML 框架的细节，即可通过蓝图或 C++ 快速训练 AI 代理在游戏环境中执行任务。

该插件的核心价值在于提供了一套结构化的工作流，包括观察（Observation）、动作（Action）、奖励（Reward）和网络（Neural Network）的定义，以及回放数据收集、模型训练和推理部署的全流程支持。

## 使用场景

- **训练游戏 AI**：你需要训练一个 NPC 或敌人执行复杂的、难以用传统状态机实现的 AI 行为，例如动态寻径、战斗策略、资源管理等。
- **自动化测试**：利用 AI 代理自动进行游戏测试，探索游戏地图的边界情况或模拟玩家行为。
- **原型开发**：快速验证一个 AI 行为概念，无需编写繁琐的逻辑代码，通过定义观察和奖励函数来“教”AI 如何行动。
- **模仿学习**：你希望 AI 学习并模仿人类玩家的操作（例如驾驶、格斗），可以使用回放数据（Replay）进行训练。

## 模块概览

插件由四个模块组成，分别负责运行时核心、数据回放、训练执行和编辑器工具。

| 模块 | 类型 | 说明 |
|---|---|---|
| **[LearningAgents](LearningAgents.md)** | Runtime | 核心运行时模块。定义了代理（Agent）、观察（Observation）、动作（Action）、奖励（Reward）等基础框架和网络架构。是所有功能的基础。 |
| **[LearningAgentsReplay](LearningAgentsReplay.md)** | Runtime | 回放模块。负责在运行时录制代理的观察、动作、奖励等数据，用于后续的模仿学习训练或行为分析。 |
| **[LearningAgentsTraining](LearningAgentsTraining.md)** | Runtime | 训练模块。包含驱动训练进程的逻辑，调用 Python 脚本或 NNE (Neural Network Engine) 进行模型训练、评估和更新。此模块依赖 UnrealEd，因此主要用于编辑器内训练。 |
| **[LearningAgentsTrainingEditor](LearningAgentsTrainingEditor.md)** | Runtime | 训练编辑器模块。为编辑器提供训练相关的工具面板、资产类型和蓝图节点，方便开发者在编辑器中配置和启动训练任务。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningAgents)
- [官方文档]()（暂无）
- [测试用例]()（暂无）