# Motion Design Scene State Integration

> （Description 字段为空）

| 属性 | 值 |
|---|---|
| 中文名 | 动效场景状态 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AvalancheSceneState` (Runtime), `AvalancheSceneStateBlueprint` (UncookedOnly), `AvalancheSceneStateEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheSceneState) | |

## 用途

AvalancheSceneState 是 **Motion Design（动态设计/Avalanche）与 Scene State（场景状态）系统之间的桥接插件**。它将通用的场景状态框架扩展为 Motion Design 专用的场景状态系统，提供以下核心能力：

- **播放动效序列**：在场景状态任务中播放 Avalanche Sequence，支持按名称或标签查询序列，并可控制等待方式
- **远程控制集成**：通过 Remote Control 系统，将场景状态中的属性值同步到 Remote Control 控制器，实现参数驱动的场景状态切换
- **Actor 生成与 Ticker 管理**：在场景状态任务中生成 Actor 并将其添加到 Motion Design 的 Ticker 系统中
- **Remote Control 事件触发**：通过 Remote Control 的 Behavior 系统触发场景状态事件，实现远程控制驱动的状态切换
- **Motion Design 专用 Schema**：定义哪些场景状态任务在 Motion Design 上下文中可用，限制任务类型以确保兼容性

简单来说：如果你在 Motion Design 工作流中需要基于事件、状态机来驱动序列播放和参数控制，这个插件就是连接两套系统的粘合层。

## 使用场景

- 你在 Motion Design 项目中，需要通过状态机来控制多个动效序列的播放顺序 → 使用 `Play Sequence` 任务
- 你需要根据场景状态变化自动更新 Remote Control 控制器的参数值 → 使用 `Set RC Controller Values` 任务
- 你需要在状态切换时动态生成 Actor 并纳入 Ticker 管理 → 使用 `Spawn Actor to Ticker` 任务
- 你需要通过 Remote Control 的外部信号触发场景状态事件 → 使用 `Scene State RC Event Behavior`
- 你正在为 Motion Design 构建复杂的交互式场景，需要状态机管理整体流程 → 使用 Motion Design Scene State Actor

## 蓝图用法

本插件的蓝图交互主要通过 **Scene State Graph（场景状态图）** 编辑器完成，而非传统的蓝图函数节点。以下为各任务节点在场景状态图中的使用方式。

### 核心任务节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Sequence` | 播放 Motion Design 序列，支持按名称或标签查询，可配置等待类型 | `FAvaSceneStatePlaySequenceTask` |
| `Set RC Controller Values` | 将场景状态属性值映射并写入 Remote Control 控制器 | `FAvaSceneStateRCTask` |
| `Spawn Actor to Ticker` | 生成 Actor 并添加到指定 Ticker Actor 的 Ticker 组件中 | `FAvaSceneStateSpawnerTickerTask` |

### 核心类型/Schema

| 类型 | 说明 | 所在类 |
|---|---|---|
| `Motion Design Scene State Schema` | 定义 Motion Design 场景状态中允许使用的任务类型 | `UAvaSceneStateSchema` |
| `Motion Design Scene State Actor` | 场景状态的宿主 Actor，关联 Scene State Blueprint | `AAvaSceneStateActor` |

### 使用示例（场景状态图描述）

**Play Sequence 任务配置**：
1. 在场景状态图中添加 `Play Sequence` 任务节点
2. 设置 `SequenceQueryType`：选择 `Name`（按名称）或 `Tag`（按标签）
3. 若选择 Name：填写 `SequenceName`（如 "IntroSequence"）
4. 若选择 Tag：填写 `SequenceTag`
5. 配置 `PlaySettings`（`FAvaSequencePlayParams`）：循环、播放速率等
6. 设置 `WaitType`：`WaitUntilStop`（等待序列播放完毕）或其他等待模式

**Set RC Controller Values 任务配置**：
1. 在场景状态图中添加 `Set RC Controller Values` 任务节点
2. 在 `ControllerValues` 中定义要设置的属性值（Property Bag）
3. 在 `ControllerMappings` 中添加映射：将每个 `SourcePropertyId`（属性包中的属性）映射到 `TargetController`（Remote Control 控制器 ID）
4. 任务执行时自动将属性值写入对应的 Remote Control 控制器

**Remote Control Event Behavior 触发**：
1. 在 Remote Control Behavior 中添加 `Scene State RC Event Behavior`
2. 配置 `Event`（`FSceneStateEventTemplate`）模板
3. 当 Behavior 执行通过时，自动向场景状态发送事件触发状态切换

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "AvaSceneStatePlaySequenceTask.h"
#include "AvaSceneStateRCTask.h"
#include "AvaSceneStateSpawnerTickerTask.h"
#include "AvaSceneStateActor.h"
#include "AvaSceneStateComponent.h"
#include "AvaSceneStateSchema.h"

// Remote Control 集成
#include "AvaSceneStateRCEventBehaviorNode.h"
#include "AvaSceneStateRCTaskBinding.h"
```

### 基本用法

**查询场景状态中的场景接口**（来自 `Private/AvaSceneStateUtils.h`）：

```cpp
#include "AvaSceneStateUtils.h"

void MyFunction(const FSceneStateExecutionContext& InContext)
{
    // 在任务执行上下文中查找 Motion Design 场景接口
    IAvaSceneInterface* SceneInterface = UE::AvaSceneState::FindSceneInterface(InContext);
    if (SceneInterface)
    {
        // 使用场景接口访问 Motion Design 场景功能
        // 例如获取序列管理器、Ticker 管理器等
    }
}
```

### 进阶用法

**自定义 Motion Design 场景状态任务**：

```cpp
// MyCustomTask.h
#pragma once

#include "SceneStateTask.h"
#include "SceneStateTaskInstance.h"
#include "MyCustomTask.generated.h"

USTRUCT()
struct FMyCustomTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category="Custom")
    float Duration = 1.0f;

    UPROPERTY(EditAnywhere, Category="Custom")
    FString Message;
};

// meta 中的 MotionDesignTask 使其被 Motion Design Schema 允许
// RequiresContextWorld 表示需要有效的 World 上下文
USTRUCT(DisplayName="My Custom Task", Category="Motion Design",
    meta=(MotionDesignTask, RequiresContextWorld))
struct FMyCustomTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FMyCustomTaskInstance;

protected:
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetTaskInstanceType() const override
    {
        return FMyCustomTaskInstance::StaticStruct();
    }
#endif

    virtual void OnStart(
        const FSceneStateExecutionContext& InContext,
        FStructView InTaskInstance) const override
    {
        // 访问实例数据
        FMyCustomTaskInstance& Instance = InTaskInstance.Get<FMyCustomTaskInstance>();
        
        // 查找 Motion Design 场景接口
        IAvaSceneInterface* SceneInterface = 
            UE::AvaSceneState::FindSceneInterface(InContext);
        
        if (SceneInterface)
        {
            UE_LOG(LogAvaSceneState, Log, TEXT("Custom task started: %s"), 
                *Instance.Message);
        }
    }

    virtual void OnStop(
        const FSceneStateExecutionContext& InContext,
        FStructView InTaskInstance,
        ESceneStateTaskStopReason InStopReason) const override
    {
        // 清理资源
    }
};
```

## Demo 示例

以下展示如何创建一个最小的自定义 Motion Design 场景状态任务，该任务在执行时通过场景接口查找序列播放器并播放指定序列。

**AvaSceneStateDemoTask.h**

```cpp
#pragma once

#include "SceneStateTask.h"
#include "SceneStateTaskInstance.h"
#include "SceneStateExecutionContext.h"
#include "AvaSceneStateDemoTask.generated.h"

USTRUCT()
struct FAvaSceneStateDemoTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    /** 要播放的序列名称 */
    UPROPERTY(EditAnywhere, Category="Demo")
    FName TargetSequenceName;

    /** 播放速率 */
    UPROPERTY(EditAnywhere, Category="Demo", meta=(ClampMin="0.1", ClampMax="10.0"))
    float PlaybackRate = 1.0f;
};

USTRUCT(DisplayName="Demo: Play Named Sequence", Category="Motion Design",
    meta=(MotionDesignTask, RequiresContextWorld))
struct FAvaSceneStateDemoTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FAvaSceneStateDemoTaskInstance;

protected:
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetTaskInstanceType() const override;
#endif
    virtual void OnStart(
        const FSceneStateExecutionContext& InContext,
        FStructView InTaskInstance) const override;
    virtual void OnStop(
        const FSceneStateExecutionContext& InContext,
        FStructView InTaskInstance,
        ESceneStateTaskStopReason InStopReason) const override;
};
```

**AvaSceneStateDemoTask.cpp**

```cpp
#include "AvaSceneStateDemoTask.h"
#include "AvaSceneStateLog.h"
#include "AvaSceneStateUtils.h"

#define LOCTEXT_NAMESPACE "AvaSceneStateDemoTask"

#if WITH_EDITOR
const UScriptStruct* FAvaSceneStateDemoTask::OnGetTaskInstanceType() const
{
    return FAvaSceneStateDemoTaskInstance::StaticStruct();
}
#endif

void FAvaSceneStateDemoTask::OnStart(
    const FSceneStateExecutionContext& InContext,
    FStructView InTaskInstance) const
{
    FAvaSceneStateDemoTaskInstance& Instance = 
        InTaskInstance.Get<FAvaSceneStateDemoTaskInstance>();

    UE_LOG(LogAvaSceneState, Log, 
        TEXT("Demo task started: playing sequence '%s' at rate %.1f"),
        *Instance.TargetSequenceName.ToString(), 
        Instance.PlaybackRate);

    // 查找 Motion Design 场景接口以访问序列系统
    IAvaSceneInterface* SceneInterface = 
        UE::AvaSceneState::FindSceneInterface(InContext);

    if (!SceneInterface)
    {
        UE_LOG(LogAvaSceneState, Warning, 
            TEXT("Demo task: could not find scene interface"));
        return;
    }

    // 在此处使用 SceneInterface 获取序列管理器并播放序列
    // 具体 API 取决于 IAvaSceneInterface 的实现
}

void FAvaSceneStateDemoTask::OnStop(
    const FSceneStateExecutionContext& InContext,
    FStructView InTaskInstance,
    ESceneStateTaskStopReason InStopReason) const
{
    UE_LOG(LogAvaSceneState, Log, TEXT("Demo task stopped (reason: %d)"), 
        static_cast<int32>(InStopReason));
}

#undef LOCTEXT_NAMESPACE
```

> **注意**：由于 `UAvaSceneStateSchema::OnIsTaskStructAllowed` 会检查任务上的 `MotionDesignTask` 元数据，自定义任务必须在 `USTRUCT` 的 `meta` 中包含 `MotionDesignTask` 才会被 Motion Design Schema 允许使用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心场景状态框架（任务基类、Schema、Actor、Component 等） |
| `AvaSequencer` / `Avalanche` | Motion Design 序列器系统（序列播放、序列名称、标签等） |
| `AvaTransition` | Motion Design 过渡系统（序列查询类型、等待类型等枚举） |
| `RemoteControl` / `RemoteControlAPI` | 远程控制系统（控制器、Behavior、Preset 等） |
| `PropertyBag` | 属性包系统（用于 RC 任务的属性值存储） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-02-22 | `977f0c20` | Motion Design Scene State: added an extra 'utility task' metadata + updating from deprecated api | 新增 utility task 元数据，更新已废弃 API |
| 2026-02-16 | `22f3bb17` | Motion Design Scene State: changed schema to only check for task type metadata in the task itself, n | Schema 改为仅检查任务自身的类型元数据 |
| 2026-02-15 | `5c9f991d` | Motion Design Scene State: made some schema functions editor-only, and added metadata to tasks to ea | 部分 Schema 函数改为编辑器专用，新增任务元数据 |
| 2026-02-03 | `d2e06058` | Motion Design Scene State: added schema to set the rules of which tasks are allowed. | 新增 Schema 规则，限制允许使用的任务类型 |

### 维护评价

**活跃维护** ✅

- 创建于 2025-08-27，不足 1 年，属于较新的插件
- 2026 年 2-4 月持续有功能性更新，包括 Schema 机制完善、元数据扩展、API 迁移
- 近期更新集中在任务类型管理和 Schema 规则优化，表明该系统仍在积极迭代
- 标记为 `IsBetaVersion: true`，API 可能仍有变动
- 作为 Motion Design 与 Scene State 的桥接层，依赖两个活跃系统（Avalanche + Scene State），长期可维护性有保障
- **推荐使用**：适合 Motion Design 项目中需要状态机驱动的场景管理工作流，但注意 Beta 阶段 API 可能变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheSceneState)
- 官方文档（无）
- 测试用例（未发现）