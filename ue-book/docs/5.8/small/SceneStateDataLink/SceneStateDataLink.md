# Motion Design Scene State Data Link Bridge

> Scene State Tasks that execute Data Link Graphs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 场景状态数据链接桥 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `SceneStateDataLink` (Runtime), `SceneStateDataLinkEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneStateDataLink) | |

## 用途

这是一个**桥接插件**，用于连接 Unreal Motion Design (UMD) 的两个核心系统：**Scene State（场景状态）** 和 **Data Link（数据链接）**。它解决的核心问题是：如何让场景状态机中的任务能够触发并执行复杂的、基于图表的 Data Link 数据流。

简单来说，它让设计师能够在 Scene State 的流程中，通过一个专门的任务节点（`FSceneStateRunDataLinkTask`）去执行一个 `DataLinkGraph`，获取数据处理结果，并将结果写回到场景状态系统的属性中。这在需要根据场景状态变化动态获取、处理或转换数据的虚拟制片工作流中至关重要。

## 使用场景

- 你在使用 Motion Design 工具构建一个复杂的虚拟制片场景，其中场景对象的属性（如位置、材质参数、灯光强度）需要通过一个数据处理管道（DataLink Graph）来计算。
- 你需要在某个场景状态（如“演出开始”、“摄像机切换”）被激活时，自动触发一个数据链接图，来生成驱动其他资产或效果的数据。
- 你希望将外部数据源（如通过网络、文件）经过 DataLink 图处理后的结果，无缝地集成到场景状态机的工作流中。

## 蓝图用法

该插件主要通过结构体（`USTRUCT`）和任务（`Task`）工作，其蓝图交互主要体现在 Scene State 编辑器中配置任务实例属性。

### 核心结构体

| 结构体 | 说明 | 用途 |
|---|---|---|
| `FSceneStateRunDataLinkTask` | 一个 Scene State 任务，其作用是运行一个 DataLink 图。 | 在 Scene State 图中作为任务节点使用。 |
| `FSceneStateDataLinkRequestTaskInstance` | `FSceneStateRunDataLinkTask` 任务的具体实例数据。 | 存储该任务执行时所需的所有配置和状态。 |

### 核心属性（在 `FSceneStateDataLinkRequestTaskInstance` 中配置）

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `DataLinkGraph` | `UDataLinkGraph*` | **要执行的 DataLink 图表资产**。这是任务的核心输入。 | `FSceneStateDataLinkRequestTaskInstance` |
| `InputData` | `TArray<FDataLinkInputData>` | DataLink 图所需的输入数据数组。其类型由关联的 `DataLinkGraph` 决定。 | `FSceneStateDataLinkRequestTaskInstance` |
| `OutputTarget` | `FSceneStatePropertyReference` | **用于接收 DataLink 图执行结果的属性引用**。必须与 DataLink 图的输出结构体类型匹配。 | `FSceneStateDataLinkRequestTaskInstance` |

### 使用示例（蓝图描述）

1.  **在 Scene State 编辑器中**：在场景状态图（Scene State Graph）中添加一个任务节点。
2.  **选择任务类型**：在节点的细节面板中，从任务类型列表里选择 **`Run Data Link`**。
3.  **配置任务实例**：
    - **Data Link Graph**：指定一个你创建好的 `UDataLinkGraph` 蓝图资产。
    - **Input Data**：根据 `DataLinkGraph` 的定义，为其添加所需的输入数据项。这些数据可以来自场景中的其他属性引用。
    - **Output Target**：选择一个场景状态机中定义的结构体属性（`FSceneStatePropertyReference`），该属性的类型必须与 `DataLinkGraph` 的最终输出类型一致。
4.  **运行时**：当场景状态机执行到该任务节点时，会自动创建 `FDataLinkInstance`，使用配置的 `InputData` 执行 `DataLinkGraph`，并将计算结果写入到 `OutputTarget` 指向的属性中。

## C++ 用法

该插件的核心是定义了一个新的 Scene State 任务类型。开发者可以基于此进行扩展或理解其工作原理。

### 头文件引入

```cpp
#include "Tasks/SceneStateRunDataLinkTask.h"
```

### 基本用法

任务 `FSceneStateRunDataLinkTask` 在引擎内部由 Scene State 系统管理，通常通过编辑器配置。以下是其核心机制的代码层面描述（源自 `SceneStateRunDataLinkTask.h`）：

```cpp
// 来源：Engine/Plugins/VirtualProduction/SceneStateDataLink/Source/SceneStateDataLink/Public/SceneStateRunDataLinkTask.h

// 任务开始时被调用
virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override
{
    // 1. 从 InTaskInstance 获取配置数据
    FSceneStateDataLinkRequestTaskInstance* Instance = InTaskInstance.GetPtr<FSceneStateDataLinkRequestTaskInstance>();
    
    // 2. 使用配置创建一个 DataLink 执行器实例
    Instance->Executor = MakeShared<FDataLinkExecutor>(Instance->CreateDataLinkInstance());
    
    // 3. 启动执行，并绑定回调
    Instance->Executor->Execute(
        FDataLinkExecutor::FOnOutputData::CreateStatic(&FSceneStateRunDataLinkTask::OnOutputData, InContext),
        FDataLinkExecutor::FOnFinished::CreateStatic(&FSceneStateRunDataLinkTask::OnFinished, InContext)
    );
}

// 任务结束时被调用，用于清理
virtual void OnStop(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, ESceneStateTaskStopReason InStopReason) const override
{
    FSceneStateDataLinkRequestTaskInstance* Instance = InTaskInstance.GetPtr<FSceneStateDataLinkRequestTaskInstance>();
    // 确保停止执行器
    if (Instance->Executor)
    {
        Instance->Executor->Stop();
        Instance->Executor.Reset();
    }
}
```

### 进阶用法

要创建一个自定义的、类似 `FSceneStateRunDataLinkTask` 的任务，你需要：
1.  继承 `FSceneStateTask`。
2.  定义一个继承自 `FSceneStateTaskInstance` 的 `USTRUCT` 作为你的任务实例数据。
3.  重写 `OnStart`、`OnStop` 等虚函数来实现你的任务逻辑。
4.  使用 `USTRUCT` 宏的 `meta=(UtilityTask)` 标记使其出现在 Scene State 编辑器的任务列表中。

## Demo 示例

一个最小的、概念性的自定义任务实现示例：

```cpp
// MyCustomDataLinkTask.h
#pragma once

#include "SceneStateTask.h"
#include "SceneStateTaskInstance.h"
#include "MyCustomDataLinkTask.generated.h"

// 任务实例数据
USTRUCT()
struct FMyCustomTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    /** 我要执行的图表 */
    UPROPERTY(EditAnywhere, Category="Custom")
    TObjectPtr<UDataLinkGraph> MyGraph;
};

// 任务本身
USTRUCT(DisplayName="Run My Custom Logic", Category="Custom", meta=(UtilityTask))
struct FMyCustomDataLinkTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FMyCustomTaskInstance;

protected:
    virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override
    {
        // 获取实例数据
        FMyCustomTaskInstance* Instance = InTaskInstance.GetPtr<FMyCustomTaskInstance>();
        
        // 此处应有使用 Instance->MyGraph 创建并执行 DataLink 的逻辑
        // 类似于 FSceneStateRunDataLinkTask 中的实现
        UE_LOG(LogTemp, Log, TEXT("Custom task started with graph: %s"), *GetNameSafe(Instance->MyGraph));
        
        // 标记任务立即完成（仅为示例）
        FinishTask(InContext);
    }

    virtual void OnStop(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, ESceneStateTaskStopReason InStopReason) const override
    {
        // 清理资源
    }
};
```

## 模块依赖

该插件明确依赖于以下两个插件（见 `.uplugin` 中的 `Plugins` 字段）：

| 模块/插件 | 用途 |
|---|---|
| `SceneState` | 提供场景状态机的核心框架和任务系统。 |
| `DataLink` | 提供数据链接图表（Graph）的执行引擎和相关数据结构。 |

**注意**：使用此插件前，必须先启用 `SceneState` 和 `DataLink` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `e7a6e476` | Motion Design: fixed Scene State Data Link task not appearing in MD Scene State, as it did not have | 修复了“运行数据链接”任务在 Motion Design 场景状态编辑器中不显示的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏从 `UE_LOG` 迁移至 `UE_LOGF`，统一日志格式。 |
| 2025-08-27 | `f25e96ca` | Motion Design: set the scene state and data link plugins to beta | 将场景状态和数据链接插件标记为 Beta 版本。 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 将插件从实验性目录移动到虚拟制片正式目录。 |

### 维护评价

- **状态**：**活跃维护中**。插件创建于 2025 年 8 月，最近一次实质性功能修复（任务显示问题）发生在 2026 年 5 月，表明仍在积极开发和维护。
- **成熟度**：**Beta**。官方明确标记为 `IsBetaVersion: true`，意味着功能基本完成但可能还有不稳定或不完整的部分，API 可能在未来版本中发生变化。
- **推荐**：**推荐在 Motion Design 相关项目中使用**。它是连接场景状态与数据流的关键组件，对于需要构建复杂、数据驱动虚拟制片场景的用户来说是必需品。由于是 Beta 版，建议在测试环境中充分验证其稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneStateDataLink)
- [官方文档]() (暂无)
- [测试用例]() (在提供的代码片段中未发现测试文件，可能位于更上层模块或单独测试项目中)