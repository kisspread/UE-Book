# Motion Design Scene State Data Link Bridge

> Scene State Tasks that execute Data Link Graphs

| 属性 | 值 |
|---|---|
| 中文名 | 场景状态数据链接桥 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图任务资产） |
| 模块 | `SceneStateDataLink` (Runtime), `SceneStateDataLinkEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneStateDataLink) | |

## 用途

本插件是 Motion Design（动态设计）工作流中，将 **Scene State（场景状态）** 系统与 **Data Link（数据链接）** 系统连接起来的桥梁。它解决的核心问题是：**如何让一个场景状态任务（Task）能够执行并驱动一个数据链接图（Data Link Graph）**。

**场景状态（Scene State）** 通常用于管理复杂的动画序列、交互状态机或场景中的数据流，它将一系列操作封装为可执行的任务。**数据链接（Data Link）** 则提供了一种在 UE 资产（如 Actor、组件）之间定义、获取和设置数据的强大框架，它以节点图的形式可视化数据的来源和去向。

本插件的作用就是创建一种特定的场景状态任务——“Data Link Request Task”。当场景状态系统执行到这个任务时，它会启动关联的数据链接图，从而实现了用场景状态的逻辑流来驱动数据链接的数据流。这为 Motion Design 用户提供了将复杂状态逻辑与灵活数据获取/设置相结合的能力。

## 使用场景

- 你正在使用 Motion Design 工作流构建一个动态场景，场景中的某个动画或交互逻辑（由 Scene State 管理）需要根据当前状态去获取一个外部数据源（如来自 C++ 对象、另一个蓝图 Actor 或文件的数据）。
- 你希望在状态机的某个状态中，自动触发一个数据链接图来为某个属性赋值或收集信息。
- 你需要在 Scene State 的任务列表中添加一个节点，该节点的执行会启动一个预配置好的 Data Link Graph，并可以向该图传递初始输入数据。

## 蓝图用法

由于插件提供的具体 `UFUNCTION(BlueprintCallable)` 节点未在给定文件中完整展示，蓝图层面的主要用法是通过编辑器创建和配置 **Data Link Request Task** 实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Data Link Request Task` | 这是一个场景状态任务类型。在场景状态图表或资产中使用时，可以为其指定一个 `Data Link Graph` 资产，并配置其输入参数。 | 任务实例类（具体类名未提供） |

### 使用示例（蓝图描述）

1.  **在场景状态资产中添加任务**：
    打开或创建一个场景状态资产（如 `Scene State Asset`）。在其任务列表中，添加一个新的任务节点，选择类型为 **“Data Link Request Task”**。
2.  **配置数据链接图**：
    在添加的任务节点的细节面板中，你会看到一个 **“Data Link Graph”** 属性。通过资产选择器（下拉菜单或资产浏览器），为你想要执行的 `UDataLinkGraph` 蓝图资产赋值。
3.  **配置输入数据**：
    如果选择的 `Data Link Graph` 有输入引脚（Inputs），细节面板中会自动更新 **“Input Data”** 数组。你需要为数组中的每个元素设置初始值。这些值会在任务执行时，作为输入参数传递给数据链接图。
4.  **执行与结果**：
    当场景状态机流转到包含此任务的状态并执行该任务时，关联的 `Data Link Graph` 将被启动。图中的数据流开始工作，最终输出的结果可用于后续的场景状态逻辑或驱动场景中的对象。

## C++ 用法

### 头文件引入

由于插件主要在编辑器层面进行细节定制，运行时使用通常通过配置资产完成。若需在 C++ 中进行更底层的操作或扩展，可能需要引入场景状态和数据链接的核心头文件。但本插件提供的具体公共头文件信息有限。

### 基本用法

从提供的代码中可以看出，插件的核心功能之一是为 `FSceneStateDataLinkRequestTaskInstance` 结构体提供 **细节面板定制（Detail Customization）**。

**示例：理解细节面板定制器（来自 `SceneStateDataLinkRequestTaskDetails.h`）**

```cpp
// 场景：编辑器中的细节面板正在显示一个 Data Link Request Task 实例的属性
// 定制器 FRequestTaskInstanceDetails 的作用是：

// 1. 当用户选择了不同的 DataLinkGraph 时，自动更新 InputData 数组
void UE::SceneStateDataLink::FRequestTaskInstanceDetails::OnGraphChanged()
{
    UpdateInputData();
}

// 2. 当某个 DataLinkGraph 被重新编译时，也更新 InputData，确保引脚定义同步
void UE::SceneStateDataLink::FRequestTaskInstanceDetails::OnGraphCompiled(UDataLinkGraph* InDataLinkGraph)
{
    UpdateInputData();
}

// 3. UpdateInputData 负责同步图引脚与输入数据结构
void UE::SceneStateDataLink::FRequestTaskInstanceDetails::UpdateInputData()
{
    // 此处逻辑会读取 DataLinkGraphHandle 指向的图资产，
    // 解析其输入引脚，并对比 InputDataHandle 指向的数组，
    // 进行添加、删除或更新操作，以保持两者一致。
}
```

这段代码展示了插件如何确保在编辑器中，任务配置面板的输入数据（`InputData`）与所选数据链接图（`DataLinkGraph`）的输入引脚始终保持同步。这是用户友好性的关键。

### 进阶用法

当前提供的源码片段主要涉及编辑器扩展，未展示运行时执行 Data Link Graph 的具体 C++ API。要实现类似运行时功能，通常需要研究其依赖的 `SceneState` 和 `DataLink` 模块的公共 API，例如：
- 创建或获取一个 `FDataLinkInstance`。
- 设置其图资产（`DataLinkGraph`）和输入数据。
- 执行图并获取结果。
本插件的任务类内部可能封装了这些逻辑。

## Demo 示例

以下是一个最小的 C++ 示例，演示了如何通过代码配置一个“数据链接请求任务”实例，类似于在编辑器细节面板中进行的操作。请注意，`FSceneStateDataLinkRequestTaskInstance` 的具体头文件和成员可能需要根据实际编译情况调整。

```cpp
// MySceneStateSetup.h
#pragma once
#include "CoreMinimal.h"
#include "SceneStateDataLinkRequestTaskInstance.h" // 假设的任务实例头文件，需根据实际路径调整

class FMySceneStateSetup
{
public:
    void SetupDataLinkTask();
};

// MySceneStateSetup.cpp
#include "MySceneStateSetup.h"
#include "DataLinkGraph.h"

void FMySceneStateSetup::SetupDataLinkTask()
{
    // 1. 假设我们已经有了一个任务实例
    FSceneStateDataLinkRequestTaskInstance MyTaskInstance;

    // 2. 设置要执行的数据链接图资产 (需要提前在编辑器中创建)
    // UDataLinkGraph* MyGraph = LoadObject<UDataLinkGraph>(nullptr, TEXT("/Game/DataLinks/MyGraph.MyGraph"));
    // MyTaskInstance.DataLinkGraph = MyGraph;

    // 3. 设置输入数据 (需要根据 MyGraph 的输入引脚定义来填充)
    // MyTaskInstance.InputData.Add(FDataLinkInputData(/*...*/));

    // 注意：在实际的场景状态资产编辑中，这些值是通过编辑器UI设置的。
    // 上述代码仅为展示数据结构的可能性，直接运行时创建任务并执行其Data Link部分
    // 通常由场景状态机内部调度完成。
}
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段和模块用途分析，使用此插件的核心依赖是：

| 模块 | 用途 |
|---|---|
| `SceneState` | 提供场景状态系统、任务定义与执行框架。本插件的任务在此框架内注册和运行。 |
| `DataLink` | 提供数据链接图的定义、编译与执行框架。本插件的任务负责启动和驱动这些图。 |
| `PropertyEditor` | (Editor模块依赖) 用于实现场景状态任务实例的细节面板定制，提供友好的输入数据配置界面。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `e7a6e476` | Motion Design: fixed Scene State Data Link task not appearing in MD Scene State, as it did not have... | 修复了数据链接任务在场景状态中不显示的注册问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏更新为新的日志宏格式，属于代码维护。 |
| 2025-08-27 | `f25e96ca` | Motion Design: set the scene state and data link plugins to beta | 将场景状态和数据链接插件标记为测试版。 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 插件从实验性目录迁移到VirtualProduction目录，标志着功能趋于稳定。 |

### 维护评价

- **创建时间**：2025年8月，至今约1年。
- **活跃度**：**活跃维护**。插件在创建后不久（2026年）仍有功能性Bug修复（任务显示问题）和代码质量改进（日志迁移），表明正在被积极使用和改进。
- **状态**：标记为 **Beta（测试版）**，说明功能可能尚未完全稳定，API 和实现未来可能会有变动。
- **推荐度**：**推荐在 Motion Design 项目中使用，但需留意其 Beta 状态**。如果你的工作流需要结合场景状态和数据链接，此插件是官方提供的桥梁方案，且维护活跃，值得一试。建议将其作为“实验性功能”纳入项目规划，并关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneStateDataLink)
- 官方文档：暂无 (`DocsURL` 为空)
- 测试用例：给定信息中未提及本插件目录下有独立测试文件。核心功能可能由 `SceneState` 或 `DataLink` 插件的测试覆盖，或依赖集成测试。