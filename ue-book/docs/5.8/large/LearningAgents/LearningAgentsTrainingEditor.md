# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 智能体学习 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、录制数据） |
| 模块 | `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningAgents) | |

## 用途

Learning Agents 是 Epic Games 为 Unreal Engine 开发的机器学习框架，专注于游戏 AI 角色的行为控制。它解决的核心问题是：**如何让 AI 角色通过学习（而非硬编码规则）来获得智能行为**。

该插件封装了强化学习（Reinforcement Learning）和模仿学习（Imitation Learning）的完整流程，包括：
- **观察空间**：定义 AI 能感知到的信息（位置、速度、深度图等）
- **动作空间**：定义 AI 可以执行的动作（移动、转向等）
- **奖励机制**：定义什么行为是"好的"
- **训练流程**：在编辑器中或外部进程进行模型训练
- **推理部署**：将训练好的模型部署到运行时
- **录制回放**：记录人类玩家行为用于模仿学习

核心设计理念是将机器学习的复杂性隐藏在蓝图友好的接口后面，让游戏开发者无需深入了解 PyTorch 或 TensorFlow 就能使用 ML 技术来驱动 AI 行为。

## 使用场景

- 你正在开发一个赛车游戏，希望 AI 对手能像人类玩家一样驾驶 → 使用模仿学习（Imitation Learning），录制人类驾驶数据训练 AI
- 你在做一个 RTS 游戏，希望单位能学会复杂的战术决策 → 使用强化学习（Reinforcement Learning），通过奖励函数引导 AI 学习
- 你需要 AI 角色能适应动态环境（如地形变化）→ 使用感知组件（如深度图）作为观察输入
- 你想在编辑器中快速迭代训练过程 → 使用 LearningAgentsTrainingEditor 模块提供的编辑器集成工具
- 你需要将训练数据导出到外部 Python 环境进行高级训练 → 使用 File Communicator 导出训练材料

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetupTraining` | 初始化训练器，设置必要的组件（蓝图实现事件） | `ALearningAgentsTrainerEditorBase` |
| `StartTraining` | 开始训练过程 | `ALearningAgentsTrainerEditorBase` |
| `StopTraining` | 停止训练过程 | `ALearningAgentsTrainerEditorBase` |
| `IsTraining` | 查询是否正在训练 | `ALearningAgentsTrainerEditorBase` |
| `MakeFileCommunicator` | 创建文件通信器，用于导出训练材料到文件 | `ALearningAgentsTrainerEditorBase` |
| `StartExport` | 导出训练数据（网络、回放缓冲区、训练器配置等） | `ALearningAgentsTrainerEditorBase` |
| `SetDepthValues` | 设置深度图数据用于可视化 | `ULearningAgentsDepthMapWidget` |

### 训练器使用流程（蓝图描述）

**模仿学习训练流程：**

1. 在关卡中放置 `ALearningAgentsImitationTrainerEditor` Actor
2. 实现 `SetupTraining` 蓝图事件，创建并返回 `ULearningAgentsManagerListener` 组件
3. 设置 `LearningAgentsManager` 引用指向场景中的 Manager
4. 设置 `Recording` 引用指向已录制的学习数据资产
5. 配置 `ImitationTrainerSettings`（网络架构、学习率等）
6. 配置 `ImitationTrainerTrainingSettings`（训练轮次、批量大小等）
7. 点击 Details 面板上的 "Run" 按钮或调用 `StartTraining` 开始训练
8. 训练完成后可使用 `Export All` 导出训练好的模型

**Flow Matching 训练流程：**

1. 放置 `ALearningAgentsFlowMatchingTrainerEditor` Actor
2. 同样实现 `SetupTraining` 和配置参数
3. 设置 `FlowMatchingTrainerSettings` 和 `FlowMatchingTrainerTrainingSettings`
4. 启动训练并导出结果

**深度图可视化：**

1. 在 AI 角色上添加 `ULearningAgentsDepthMapVisualizerComponent` 组件
2. 设置 `RenderSize` 和 `RenderPosition` 控制显示位置和大小
3. 组件会自动连接到角色上的 `ULearningAgentsDepthMapComponent` 并实时显示深度信息

## C++ 用法

### 头文件引入

```cpp
#include "LearningAgentsTrainerEditorBase.h"
#include "LearningAgentsImitationTrainerEditor.h"
#include "LearningAgentsFlowMatchingTrainerEditor.h"
#include "LearningAgentsDepthMapVisualizer.h"
```

### 基本用法 - 创建自定义训练器

```cpp
// 来源: Public/LearningAgentsImitationTrainerEditor.h

// 创建自定义模仿学习训练器
UCLASS(BlueprintType, Blueprintable)
class AMyCustomTrainer : public ALearningAgentsImitationTrainerEditor
{
    GENERATED_BODY()

public:
    AMyCustomTrainer()
    {
        // 配置默认训练参数
        ImitationTrainerSettings.LearningRate = 0.001f;
        ImitationTrainerTrainingSettings.NumIterations = 1000;
    }

    // SetupTraining 在蓝图中实现
    // 返回配置好的 ULearningAgentsManagerListener

    virtual void StartTraining() override
    {
        Super::StartTraining();
        UE_LOG(LogLearningAgents, Log, TEXT("Custom training started"));
    }

    virtual void StopTraining() override
    {
        Super::StopTraining();
        UE_LOG(LogLearningAgents, Log, TEXT("Custom training stopped"));
    }
};
```

### 进阶用法 - 导出训练材料到文件

```cpp
// 来源: Public/LearningAgentsTrainerEditorBase.h

// 在编辑器工具中导出训练数据用于外部 Python 训练
void ExportTrainingData(ALearningAgentsTrainerEditorBase* Trainer)
{
    // 创建文件通信器，指定导出目录
    FDirectoryPath ExportPath;
    ExportPath.Path = TEXT("/Game/LearningAgents/TrainingData");
    
    FLearningAgentsCommunicator Communicator = Trainer->MakeFileCommunicator(ExportPath);
    
    // 设置导出标志 - 选择要导出的内容
    Trainer->ExportFlags = UE::Learning::ETrainerExportFlags::All;
    
    // 开始导出（不启动训练循环）
    Trainer->StartExport(Trainer->ExportFlags);
    
    // 导出完成后，可以在外部使用 Python 脚本读取训练数据
    // 文件位于 ExportPath 指定的目录中
}
```

## Demo 示例

### 自定义模仿学习训练器（编辑器内训练）

```cpp
// MyImitationTrainer.h
#pragma once

#include "CoreMinimal.h"
#include "LearningAgentsImitationTrainerEditor.h"
#include "MyImitationTrainer.generated.h"

UCLASS(BlueprintType, Blueprintable)
class MYGAME_API AMyImitationTrainer : public ALearningAgentsImitationTrainerEditor
{
    GENERATED_BODY()

public:
    AMyImitationTrainer();

    // 蓝图中实现此事件，返回配置好的 Listener
    // UFUNCTION(BlueprintImplementableEvent)
    // ULearningAgentsManagerListener* SetupTraining();

    virtual void StartTraining() override;
    virtual void StopTraining() override;
    virtual bool IsTraining() const override;
};
```

```cpp
// MyImitationTrainer.cpp
#include "MyImitationTrainer.h"
#include "LearningAgentsManager.h"
#include "LearningAgentsRecording.h"

AMyImitationTrainer::AMyImitationTrainer()
{
    // 默认配置
    ImitationTrainerSettings.LearningRate = 0.001f;
    ImitationTrainerTrainingSettings.NumIterations = 500;
    ImitationTrainerTrainingSettings.BatchSize = 64;
}

void AMyImitationTrainer::StartTraining()
{
    // 调用父类开始训练
    ALearningAgentsImitationTrainerEditor::StartTraining();
    
    // 可以在这里添加自定义逻辑
    UE_LOG(LogTemp, Log, TEXT("模仿学习训练开始，迭代次数: %d"), 
           ImitationTrainerTrainingSettings.NumIterations);
}

void AMyImitationTrainer::StopTraining()
{
    ALearningAgentsImitationTrainerEditor::StopTraining();
    UE_LOG(LogTemp, Log, TEXT("模仿学习训练停止"));
}

bool AMyImitationTrainer::IsTraining() const
{
    return ALearningAgentsImitationTrainerEditor::IsTraining();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器集成（用于训练器 Details 面板自定义） |

说明：LearningAgentsTrainingEditor 模块依赖 UnrealEd 用于编辑器 UI 集成。其他模块（LearningAgents、LearningAgentsReplay、LearningAgentsTraining）主要依赖标准 Core/Engine 模块，无特殊依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0b2b6629` | [LearningAgents] Fix interactor SetActionVector | 修复交互器 SetActionVector 函数的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-24 | `553c9043` | [LearningAgents] Pass NNECpuPath to python directly | 将 NNE CPU 路径直接传递给 Python 进程 |
| 2026-04-20 | `305f49dd` | [LearningAgents] Improve reinitialize recording behavior to reset and add new schema (#14361) | 改进重新初始化录制行为，支持重置并添加新 schema |
| 2026-04-14 | `898b7c7c` | [LACombat] Replay Runtime Recording | 添加战斗系统的回放运行时录制功能 |

### 维护评价

**活跃维护中** ⚡

- **创建时间**：2023 年 3 月，作为实验性功能引入
- **更新频率**：最近一个月内有多次功能性更新（2026 年 4-5 月），表明该插件正在被积极开发
- **更新内容**：
  - Bug 修复（交互器函数、格式说明符）
  - 功能增强（Python 集成改进、录制 schema 改进）
  - 新功能（战斗系统回放录制）
- **状态**：虽然路径仍为 Experimental，但从更新频率看已接近成熟
- **推荐度**：✅ 推荐使用，特别是对于需要 AI 学习能力的项目

**注意事项**：
- 该插件默认未启用（EnabledByDefault: false），需要在项目设置中手动启用
- 路径仍为 Experimental，API 可能在未来版本中有变动
- 训练模块依赖 Python 环境和 PyTorch，需要额外配置

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningAgents)
- [官方文档]()（暂无）
- [测试用例]()（待确认）