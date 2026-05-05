# StateTree

> General purpose hierarchical state machine

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（状态树资产、任务节点、评估器等） |
| 模块 | `StateTreeModule` (Runtime), `StateTreeEditorModule` (Runtime), `StateTreeDeveloper` (Runtime), `StateTreeTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree) | |

## 用途

StateTree 是一个通用的、层次化的状态机框架，旨在为游戏逻辑（特别是 AI 行为）提供强大且灵活的组织方式。它超越了简单的状态切换，支持层次结构、并行状态、数据绑定和可扩展的任务节点，允许开发者以可视化的方式构建和调试复杂的行为逻辑。

## 使用场景

- **AI 行为设计**：为 NPC 或敌人设计复杂的决策树，如巡逻、追击、攻击、掩护等行为的切换与组合。
- **游戏流程控制**：管理游戏关卡流程、任务系统、过场动画序列等具有明确状态和转换条件的逻辑。
- **角色能力系统**：组织角色的不同能力（如冲刺、格挡、施法）及其激活、冷却和中断逻辑。
- **任何需要清晰状态管理的系统**：适用于任何需要将复杂逻辑分解为可管理状态和转换的场景。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `StateTreeModule` | Runtime | 核心运行时模块，包含状态机引擎、任务、评估器和数据绑定等核心逻辑。 |
| `StateTreeEditorModule` | Runtime | 编辑器支持模块，提供状态树资产的编辑器界面、自定义节点开发框架和调试工具。 |
| `StateTreeDeveloper` | Runtime | 开发者工具模块，提供用于开发和测试 StateTree 节点的辅助功能。 |
| `StateTreeTestSuite` | Runtime | 测试套件模块，包含针对 StateTree 核心功能的自动化测试用例。 |

## 蓝图用法

StateTree 的主要蓝图交互通过 **状态树资产** 和 **状态树组件** 完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartLogic` | 启动状态树逻辑。 | `UStateTreeComponent` |
| `StopLogic` | 停止状态树逻辑。 | `UStateTreeComponent` |
| `RestartLogic` | 重启状态树逻辑。 | `UStateTreeComponent` |
| `SetContextData` | 为状态树设置外部上下文数据（如角色引用）。 | `UStateTreeComponent` |

### 使用示例（蓝图描述）

1.  在角色蓝图中添加 `UStateTreeComponent`。
2.  在组件详情面板中，指定一个已创建的 `UStateTree` 资产。
3.  通过蓝图调用 `StartLogic` 节点来启动状态机。
4.  状态树资产内部通过可视化编辑器定义状态、转换和任务，无需额外蓝图节点。

## C++ 用法

StateTree 的 C++ 用法主要集中在创建自定义任务节点和评估器。

### 头文件引入

```cpp
#include "StateTreeTaskBase.h"
#include "StateTreeEvaluatorBase.h"
```

### 基本用法：创建自定义任务

```cpp
// 来源：Engine/Plugins/Runtime/StateTree/Source/StateTreeModule/Public/Tasks/StateTreeTask.h
UCLASS()
class UMyCustomTask : public UStateTreeTaskBase
{
    GENERATED_BODY()

public:
    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override;
    virtual void ExitState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override;
    // ... 其他重写方法
};
```

### 进阶用法：使用执行上下文

```cpp
// 在任务或评估器中，通过上下文访问和修改状态树数据
EStateTreeRunStatus UMyCustomTask::EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const
{
    // 从上下文中获取数据
    FMyCustomData* Data = Context.GetInstanceDataPtr<FMyCustomData>(DataHandle);
    if (Data)
    {
        Data->bIsActive = true;
    }
    // 返回运行状态
    return EStateTreeRunStatus::Running;
}
```

## Demo 示例

一个最小的自定义任务示例，仅打印日志。

**MySimpleTask.h**
```cpp
#pragma once
#include "StateTreeTaskBase.h"
#include "MySimpleTask.generated.h"

UCLASS()
class UMySimpleTask : public UStateTreeTaskBase
{
    GENERATED_BODY()

public:
    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override;
};
```

**MySimpleTask.cpp**
```cpp
#include "MySimpleTask.h"

EStateTreeRunStatus UMySimpleTask::EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const
{
    UE_LOG(LogTemp, Warning, TEXT("MySimpleTask: Entered State!"));
    return EStateTreeRunStatus::Succeeded;
}
```

## 模块依赖

对于使用 StateTree 的项目，主要依赖其核心运行时模块。

| 模块 | 用途 |
|---|---|
| `StateTreeModule` | 核心运行时功能，必须依赖。 |
| `StateTreeEditorModule` | 仅在编辑器环境下需要，用于资产编辑和调试。 |

## 维护状态

### 近期更新

（注：由于未提供具体 git log，以下为基于插件活跃状态的通用描述）
- StateTree 作为 UE5 的核心 AI/逻辑框架，处于持续开发和维护中。
- 更新通常包含新功能（如新的内置任务节点）、性能优化、Bug 修复以及与引擎其他系统（如 Mass AI）的集成改进。

### 维护评价

- **活跃维护**：作为 Epic Games 官方主推的下一代 AI/逻辑解决方案，StateTree 在 UE5 中持续获得更新和增强。
- **推荐使用**：对于新项目，尤其是需要复杂 AI 或游戏逻辑的项目，强烈推荐使用 StateTree 替代旧版行为树或自行实现的状态机。它提供了更好的可视化、可扩展性和调试能力。
- **注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree/Source/StateTreeTestSuite)