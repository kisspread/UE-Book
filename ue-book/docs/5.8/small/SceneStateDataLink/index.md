# Motion Design Scene State Data Link Bridge

> Scene State Tasks that execute Data Link Graphs

| 属性 | 值 |
|---|---|
| 中文名 | 场景状态数据链接桥接 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SceneStateDataLink` (Runtime), `SceneStateDataLinkEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneStateDataLink) | |

## 用途

此插件是 **Scene State（场景状态）** 和 **Data Link（数据链接）** 两个系统之间的**桥接器**。它的核心功能是允许通过 **Data Link Graphs（数据链接图）** 来驱动场景状态中的任务（Task）。

具体来说，它解决了在 **Motion Design（动态设计）** 工作流中，如何将外部或复杂的数据源（通过 Data Link 系统获取）接入到场景状态动画系统的问题。Data Link 负责从各种来源（如蓝图、C++ 代码、其他插件）拉取数据，而本插件的 Task 会执行对应的 Data Link Graph，并将结果暴露给场景状态，从而实现数据驱动的动画控制。

## 使用场景

- 你在使用 **Motion Design** 模块制作虚拟生产（VP）或广播图形动画。
- 你的动画效果需要根据外部数据源（如 Excel 表格、数据库、游戏逻辑、其他蓝图）的动态变化来更新。
- 你希望使用 Data Link 系统来集中管理和抽象数据源，并通过图形化的方式配置数据获取逻辑。

## 蓝图用法

本插件提供的核心蓝图功能是创建和配置一个执行 Data Link Graph 的场景状态任务。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Scene State Task` | 创建一个 `USceneStateTask_DataLinkGraph` 实例，用于后续配置和添加到场景状态。 | `USceneStateTaskLibrary` |
| `Set Data Link Graph` | 为指定的任务对象设置要执行的 `UDataLinkGraph` 资产。 | `USceneStateTaskLibrary` |

### 使用示例（蓝图描述）

1.  在场景状态蓝图中，使用 `Create Scene State Task` 节点，Class 参数选择 `Scene State Task Data Link Graph`。
2.  将返回的任务对象（Object）连接到 `Set Data Link Graph` 节点。
3.  在 `Set Data Link Graph` 节点的 `Graph` 引脚上，指定你事先编辑好的 `UDataLinkGraph` 资产。
4.  最后，将配置好的任务对象添加到场景状态的任务列表中。

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateTask_DataLinkGraph.h"
```

### 基本用法

```cpp
// 创建一个数据链接图任务实例
USceneStateTask_DataLinkGraph* DataLinkTask = NewObject<USceneStateTask_DataLinkGraph>(Owner);

// 设置要执行的数据链接图
UDataLinkGraph* MyGraph = LoadObject<UDataLinkGraph>(nullptr, TEXT("/Game/MyDataLinkGraph"));
DataLinkTask->SetDataLinkGraph(MyGraph);

// 将任务添加到场景状态实例中（假设你有SceneStateInstance）
SceneStateInstance->AddTask(DataLinkTask);
```
*代码示例来源于模块 `SceneStateDataLink` 的公共 API 设计。*

## Demo 示例

以下是一个最小化的自定义场景状态任务示例，演示如何通过 C++ 使用数据链接图任务。

**MyCustomSceneState.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "SceneStateTask.h"
#include "MyCustomSceneState.generated.h"

UCLASS()
class UMyCustomSceneStateTask : public USceneStateTask
{
    GENERATED_BODY()

public:
    virtual void OnTaskActivated() override;
    virtual void OnTaskDeactivated() override;

private:
    UPROPERTY()
    TObjectPtr<USceneStateTask_DataLinkGraph> DataLinkGraphTask;
};
```

**MyCustomSceneState.cpp**
```cpp
#include "MyCustomSceneState.h"
#include "SceneStateTask_DataLinkGraph.h"

void UMyCustomSceneStateTask::OnTaskActivated()
{
    Super::OnTaskActivated();

    // 创建并配置数据链接图任务
    DataLinkGraphTask = NewObject<USceneStateTask_DataLinkGraph>(this);
    DataLinkGraphTask->SetDataLinkGraph(MyLoadedGraph);

    // 激活子任务（这里仅为示例，实际集成方式可能不同）
    DataLinkGraphTask->ActivateTask(/* ... */);
}

void UMyCustomSceneStateTask::OnTaskDeactivated()
{
    if (DataLinkGraphTask)
    {
        DataLinkGraphTask->DeactivateTask();
    }
    Super::OnTaskDeactivated();
}
```

## 模块依赖

使用此插件的运行时功能，你的模块需要链接 `SceneState` 和 `DataLink` 模块。编辑器功能则需要链接 `SceneStateDataLinkEditor`。

| 模块 | 用途 |
|---|---|
| `SceneState` | 提供场景状态系统的基础框架和任务接口。 |
| `DataLink` | 提供数据链接图系统，用于定义和执行数据获取逻辑。 |
| `SceneStateDataLinkEditor` | 提供编辑器支持，包括任务资产的自定义编辑器和 UI。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `e7a6e476` | Motion Design: fixed Scene State Data Link task not appearing in MD Scene State, as it did not have | 修复了数据链接任务在Motion Design场景状态中不显示的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移到 `UE_LOGF`，属于代码维护性更新。 |
| 2025-08-27 | `f25e96ca` | Motion Design: set the scene state and data link plugins to beta | 将插件正式标记为 Beta 版本。 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 插件从实验性目录迁移至正式的虚拟生产目录。 |

### 维护评价

该插件创建时间较新（2025年8月），且在创建后近10个月内仍有功能性更新（2026年5月修复显示问题），表明它处于**活跃维护**状态。作为 **Beta** 版本，其 API 和功能可能在未来版本中发生变化。目前功能聚焦，依赖关系清晰，是 Motion Design 数据驱动动画流程中的关键组件，**推荐在受控的测试或生产环境中使用**，并关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneStateDataLink)
- [SceneState 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)（相关系统）
- [DataLink 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink)（相关系统）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneStateDataLink/Tests)（如果存在）