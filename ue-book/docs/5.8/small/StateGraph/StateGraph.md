# State Graph

> Generic state machine management class.

| 属性 | 值 |
|---|---|
| 中文名 | 状态图 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StateGraph` (Runtime), `StateGraphManager` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph) | |

## 用途

该插件提供了一个基于**有向图**的状态机框架。它并非简单的线性状态机，而是将状态抽象为图的**节点 (Node)**，节点之间可以通过依赖关系构建出复杂的执行流（例如分支、并行、顺序执行）。每个节点代表一个异步或同步的操作/状态，框架负责管理节点的生命周期（启动、完成、超时）、依赖检查、超时处理以及整个状态图的运行控制（启动、暂停、重置）。其主要解决的是**复杂异步流程的管理**问题，为游戏逻辑（如网络连接、加载流程、任务链）提供了一种更灵活、可维护性更高的状态管理范式。

## 使用场景

- **网络连接状态管理**：将连接过程的各个步骤（握手、认证、加载地图、同步数据等）建模为节点，利用依赖关系确保步骤按顺序执行，并通过超时和错误状态处理异常流程。
- **游戏流程控制**：管理从菜单、加载、游戏进行到暂停、结束等整个游戏生命周期的复杂状态转换。
- **批处理或任务队列**：当一系列任务存在复杂的先后依赖或可并行关系时，可以将其抽象为图节点，由状态图自动调度执行。

## 蓝图用法

**不支持蓝图**。此插件为纯C++实现，所有API均在`UE`命名空间下的C++类中，没有暴露任何`BlueprintCallable`或`BlueprintReadWrite`功能。

## C++ 用法

该插件的核心是`UE::FStateGraph`和`UE::FStateGraphNode`两个类。

### 头文件引入

```cpp
#include "StateGraph.h"
#include "StateGraphFwd.h"
```

### 基本用法

**1. 定义一个自定义节点**

自定义节点需要继承自`UE::FStateGraphNode`并实现纯虚函数`Start()`。

```cpp
// 自定义节点：模拟一个异步加载任务
class FMyLoadAssetNode : public UE::FStateGraphNode
{
public:
    FMyLoadAssetNode(FName InName) : UE::FStateGraphNode(InName) {}

protected:
    virtual void Start() override
    {
        UE_LOGF(LogStateGraph, Log, TEXT("[%s] Asset load started."), *GetLogName());

        // 模拟异步操作，完成后调用 Complete()
        FGraphEventRef Task = FFunctionGraphTask::CreateAndDispatchWhenReady([this]()
        {
            // ... 执行实际的异步加载逻辑 ...
            // 假设加载完成
            Complete();
        }, TStatId(), nullptr, ENamedThreads::AnyBackgroundThreadNormalTask);
    }
};
```

**2. 创建状态图并管理节点**

```cpp
// 创建状态图
UE::FStateGraphRef StateGraph = MakeShared<UE::FStateGraph>(FName("MyLoadGraph"));
StateGraph->Initialize();

// 创建节点
UE::FStateGraphNodeRef LoadNode = StateGraph->CreateNode<FMyLoadAssetNode>(FName("LoadData"));
UE::FStateGraphNodeRef ProcessNode = StateGraph->CreateNode<FMyProcessDataNode>(FName("ProcessData"));

// 设置依赖：ProcessNode 依赖于 LoadNode 完成
StateGraph->AddDependencies(FName("ProcessData"), { FName("LoadData") });

// 启动状态图
StateGraph->Run();
```

**3. 使用函数节点快速链式调用**

对于简单的逻辑，可以直接使用Lambda或成员函数创建函数节点，并链式设置依赖。

```cpp
StateGraph->CreateNode(FName("Step1"), [](UE::FStateGraph& StateGraph, UE::FStateGraphNodeFunctionComplete Complete)
{
    UE_LOGF(LogStateGraph, Log, TEXT("Step 1 is running..."));
    // ... 做一些事情 ...
    Complete(); // 标记完成，触发下一步
})->Next(FName("Step2"), [this](UE::FStateGraph& StateGraph, UE::FStateGraphNodeFunctionComplete Complete)
{
    UE_LOGF(LogStateGraph, Log, TEXT("Step 2 is running..."));
    // ... 做更多事情 ...
    Complete();
});
```

### 进阶用法

**超时处理**
可以为单个节点或整个状态图设置超时。

```cpp
// 为节点设置超时
LoadNode->SetTimeout(5.0f); // 5秒后若未完成则触发 TimedOut

// 为整个状态图设置超时
StateGraph->SetTimeout(10.0f);

// 监听节点状态变化，处理超时
StateGraph->OnNodeStatusChanged.AddLambda([](UE::FStateGraphNode& Node, UE::FStateGraphNode::EStatus OldStatus, UE::FStateGraphNode::EStatus NewStatus)
{
    if (NewStatus == UE::FStateGraphNode::EStatus::TimedOut)
    {
        UE_LOGF(LogStateGraph, Warning, TEXT("Node [%s] timed out!"), *Node.GetLogName());
    }
});
```

**动态修改图**
可以在运行时向状态图添加或移除节点。

```cpp
// 在某个节点完成的回调中，动态添加新节点
StateGraph->OnNodeStatusChanged.AddLambda([StateGraph](UE::FStateGraphNode& Node, ...)
{
    if (Node.GetName() == FName("CheckCondition") && Node.GetStatus() == UE::FStateGraphNode::EStatus::Completed)
    {
        // 根据条件动态添加后续节点
        StateGraph->CreateNode(FName("DynamicStep"), [](UE::FStateGraph&, UE::FStateGraphNodeFunctionComplete Complete)
        {
            // ... 动态任务逻辑 ...
            Complete();
        });
        // 可能需要重新 Run() 状态图
        StateGraph->Run();
    }
});
```

**暂停与重置**
```cpp
// 暂停状态图，阻止新节点启动
StateGraph->Pause();

// 停止并重置所有节点，状态图可重新 Run()
StateGraph->Reset();
```

## Demo 示例

一个完整的、可编译的示例，展示如何创建状态图、定义节点、设置依赖并处理完成和超时。

```cpp
// MyStateGraphDemo.h
#pragma once
#include "CoreMinimal.h"
#include "StateGraph.h"
#include "StateGraphFwd.h"

class FAsyncDownloadNode : public UE::FStateGraphNode
{
public:
    FAsyncDownloadNode(FName InName) : UE::FStateGraphNode(InName) {}

protected:
    virtual void Start() override
    {
        UE_LOGF(LogTemp, Log, TEXT("[%s] Download started..."), *GetLogName());
        // 模拟下载，3秒后完成
        FTimerHandle Handle;
        GetWorld()->GetTimerManager().SetTimer(Handle, [WeakThis = MakeWeakObjectPtr(this)]()
        {
            if (TSharedPtr<FAsyncDownloadNode> SharedThis = WeakThis.Pin())
            {
                UE_LOGF(LogTemp, Log, TEXT("[%s] Download completed."), *SharedThis->GetLogName());
                SharedThis->Complete();
            }
        }, 3.0f, false);
    }
};

class FProcessFileNode : public UE::FStateGraphNode
{
public:
    FProcessFileNode(FName InName) : UE::FStateGraphNode(InName) {}

protected:
    virtual void Start() override
    {
        UE_LOGF(LogTemp, Log, TEXT("[%s] Processing file..."), *GetLogName());
        // 处理完成后立即完成
        Complete();
    }
};

// 演示如何使用
void RunStateGraphDemo(UWorld* World)
{
    // 1. 创建状态图
    UE::FStateGraphRef DemoGraph = MakeShared<UE::FStateGraph>(FName("DemoGraph"));
    DemoGraph->Initialize();

    // 2. 创建节点
    UE::FStateGraphNodeRef DownloadNode = DemoGraph->CreateNode<FAsyncDownloadNode>(FName("DownloadFile"));
    UE::FStateGraphNodeRef ProcessNode = DemoGraph->CreateNode<FProcessFileNode>(FName("ProcessFile"));

    // 3. 设置依赖：处理文件依赖于下载完成
    DemoGraph->AddDependencies(FName("ProcessFile"), { FName("DownloadFile") });

    // 4. 监听状态变化
    DemoGraph->OnStatusChanged.AddLambda([](UE::FStateGraph& Graph, UE::FStateGraph::EStatus Old, UE::FStateGraph::EStatus New)
    {
        UE_LOGF(LogTemp, Log, TEXT("Graph [%s] status changed: %s -> %s"), *Graph.GetLogName(), *Graph.GetStatusName(Old), *Graph.GetStatusName(New));
    });

    // 5. 启动状态图
    DemoGraph->Run();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/CoreUObject/Engine 等） | 该插件自身的依赖非常基础，主要包含标准引擎模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5b01134f` | Remove matchmaking attempt when CreateClientJoinStateGraph fails in TryMatchmaking. | 在匹配失败时移除了创建客户端加入状态图的尝试。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 宏迁移至新版 UE_LOGF 宏。 |
| 2026-02-10 | `0e0a7b5f` | UE: StateGraph remove timeout ticker when needed. | 修复了在需要时未能移除超时计时器的问题。 |
| 2025-12-09 | `bc24ccfb` | Complete PreLoginAsync stategraph with error if user disconnects before reaching PostLogin | 如果用户在完成登录前断开连接，则以错误状态完成异步登录状态图。 |
| 2025-12-09 | `7a456323` | [Backout] - CL49078828 | 回退了某个变更列表（CL49078828）。 |

### 维护评价

- **活跃度**：维护非常活跃，最近的提交集中在 2025-2026 年，且包含功能修复（如超时计时器）和实际业务逻辑集成（如登录、匹配）。
- **状态**：该插件仍标记为 **实验性** (`EnabledByDefault: false`)，说明 Epic 官方可能还在评估其稳定性和通用性，或将其作为内部使用的高级框架。
- **推荐度**：鉴于其清晰的设计和近期活跃的维护，**推荐**有复杂状态管理需求的项目（尤其是那些已经使用类似模式或感到传统状态机不够灵活的项目）评估并谨慎使用。需要注意其实验性标签，意味着API可能在未来的引擎版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StateGraph)
- [官方文档] (无)