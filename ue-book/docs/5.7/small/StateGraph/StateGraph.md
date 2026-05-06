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
| 创建时间 | 2025-04-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StateGraph) | |

## 用途

State Graph 提供了一个通用的状态机管理框架。与传统的层级状态机不同，它采用**自由形式图结构**——节点不需要线性排列或强制继承关系，节点之间通过依赖关系连接。设计目标包括：

- **灵活的结构**：节点间依赖关系可任意定义，不受层级限制。
- **异步支持**：通过延迟完成函数（`Complete()`）处理异步任务（如等待外部事件、定时器、网络回调）。
- **运行时动态修改**：可以在执行过程中增加、删除、重命名或重置节点，无需暂停整个状态机。
- **每个节点都是独立对象**：节点封装自己的数据和逻辑，便于派生和嵌套。
- **委托节点**：提供 `FStateGraphNodeFunction` 支持直接绑定各种函数类型作为节点逻辑。
- **单线程执行深度**：一次只执行一个节点，避免并发状态混叠。
- **超时控制**：可以为整个状态图和单个节点设置超时，超时自动标记为 `TimedOut`。
- **可配置与热修复**：支持通过 ini 文件进行配置和运行时热修复。

## 使用场景

- **AI 行为状态**：当需要根据复杂条件（如感知、血量、距离）切换行为，且状态间依赖关系不是简单线性链时，用状态图可以清晰表达。
- **游戏流程管理**：加载流程、联机匹配、关卡切换等具有异步等待和条件分支的阶段。
- **UI 导航**：多步骤表单、向导、动画序列等依赖用户输入或后台数据的流程。
- **网络状态机**：连接、认证、同步等具有超时和重试逻辑的网络阶段。
- **任何需要“等待后继续”的异步逻辑**：状态图天然支持节点暂挂（Blocked）和延迟完成。

## 蓝图用法

**本插件目前**不暴露 `UFUNCTION(BlueprintCallable)` 接口，因此不直接支持蓝图使用。需要在 C++ 中创建封装，或者通过自定义蓝图节点（如 `UK2Node`）间接调用。

建议：在 C++ 项目中继承 `FStateGraphNode` 并添加 `UFUNCTION` 暴露，然后通过 `FStateGraph` 操作，再暴露给蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "StateGraph.h"               // 主模块头文件
#include "StateGraphFwd.h"            // 智能指针类型别名
```

建议在 Precompiled Header 或模块 PCH 中引入以提升编译速度。

### 基本用法

以下示例来自测试文件 `StateGraphTests.cpp` 的简化版，展示如何创建并运行一个简单的两节点状态图。

```cpp
// 创建状态图实例
TSharedRef<UE::FStateGraph> Graph = MakeShared<UE::FStateGraph, ESPMode::ThreadSafe>(TEXT("TestGraph"));

// 创建两个节点：InitNode 和 ProcessNode
TSharedRef<UE::FStateGraphNode> InitNode = MakeShared<UE::FStateGraphNode>(TEXT("Init"));
TSharedRef<UE::FStateGraphNode> ProcessNode = MakeShared<UE::FStateGraphNode>(TEXT("Process"));

// 添加依赖关系：ProcessNode 依赖于 InitNode 完成后才能启动
ProcessNode->AddDependency(InitNode);

// 将节点添加到图中
Graph->AddNode(InitNode);
Graph->AddNode(ProcessNode);

// 设置节点的启动逻辑（通过 SetUpdate 或使用 FStateGraphNodeFunction 委托节点）
// 这里演示直接使用 FStateGraphNode 并重写 Start() 函数（Base class 方式）
// 实际推荐使用 FStateGraphNodeFunction 实现简单逻辑。

// 启动状态图
Graph->Start();

// 模拟 Tick 更新（通常放在游戏循环或计时器里）
while (Graph->Update(DeltaTime) != UE::FStateGraph::EUpdateResult::Completed)
{
    // 处理其他逻辑
}
```

### 进阶用法：使用 `FStateGraphNodeFunction` 绑定委托

```cpp
// 使用 FStateGraphNodeFunction 快速创建带完成回调的节点
TSharedRef<UE::FStateGraphNodeFunction> Node = MakeShared<UE::FStateGraphNodeFunction>(TEXT("AsyncNode"));

// 设置启动函数：函数体执行异步操作，完成后调用 Complete()
Node->SetStartFunction([NodeRef = Node.ToWeakPtr()](UE::FStateGraphNodeFunctionComplete CompleteFn)
{
    // 模拟异步任务（例如等待 1 秒后完成）
    FTSTicker::GetCoreTicker().AddTimer(FTimerDelegate::CreateLambda([CompleteFn, NodeRef]()
    {
        UE_LOG(LogStateGraph, Log, TEXT("Async task done"));
        CompleteFn();
    }), 1.0f, false);
});

Graph->AddNode(Node);
```

### 超时设置

```cpp
// 设置整个状态图超时（5 秒）
Graph->SetTimeout(5.0);

// 为单个节点设置超时（3 秒）
Node->SetTimeout(3.0);
```

### 运行时修改

```cpp
// 在状态图运行过程中动态添加节点
Graph->AddNode(NewNode);

// 移除节点（如果该节点已有依赖者，会抛出断言或日志警告）
Graph->RemoveNode(OldNode);

// 重命名节点
OldNode->SetName(TEXT("RenamedNode"));

// 重置所有节点
Graph->Reset();
```

## Demo 示例

以下是一个完整的可编译 C++ 示例，展示如何使用 StateGraph 实现一个简单的**“等待初始化 → 处理 → 完成”**流程。

**StateGraphDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "StateGraph.h"

class FStateGraphDemo
{
public:
    void Run();
    
private:
    TSharedRef<UE::FStateGraphNode> InitNode;
    TSharedRef<UE::FStateGraphNodeFunction> ProcessNode;
    TSharedRef<UE::FStateGraph> Graph;

    void StartDemo();
};
```

**StateGraphDemo.cpp**
```cpp
#include "StateGraphDemo.h"
#include "StateGraphFwd.h"
#include "Misc/DateTime.h"

void FStateGraphDemo::Run()
{
    Graph = MakeShared<UE::FStateGraph, ESPMode::ThreadSafe>(TEXT("DemoGraph"));

    // 1. 初始化节点：立即完成
    InitNode = MakeShared<UE::FStateGraphNode>(TEXT("Init"));
    Graph->AddNode(InitNode);
    InitNode->SetTimeout(0.5); // 半秒未完成则超时
    // 手动设置为 Started 后立即 Complete（实际应用中可在 Start() 内调用 Complete()）
    InitNode->SetStatus(UE::FStateGraphNode::EStatus::Started);
    InitNode->Complete();

    // 2. 处理节点：等待 Init 完成后，延迟 2 秒完成
    ProcessNode = MakeShared<UE::FStateGraphNodeFunction>(TEXT("Process"));
    ProcessNode->AddDependency(InitNode);
    ProcessNode->SetStartFunction([WeakThis = TWeakPtr<FStateGraphDemo>(AsShared())]
        (UE::FStateGraphNodeFunctionComplete CompleteFn)
    {
        // 模拟异步操作
        FTSTicker::GetCoreTicker().AddTimer(FTimerDelegate::CreateLambda([CompleteFn]()
        {
            UE_LOG(LogTemp, Log, TEXT("Process completed!"));
            CompleteFn();
        }), 2.0f, false);
    });
    Graph->AddNode(ProcessNode);

    // 启动
    Graph->Start();

    // 模拟 Tick 更新（在实际项目中放在 Event Tick 或定时器）
    while (Graph->Update(0.016f) != UE::FStateGraph::EUpdateResult::Completed)
    {
        // 实际项目中不在此处忙等，而是每帧调用 Update
        FPlatformProcess::Sleep(0.01f);
    }

    UE_LOG(LogTemp, Log, TEXT("StateGraph completed!"));
}
```

## 模块依赖

**StateGraph** 模块本身的依赖已在 .Build.cs 中隐式包含，对于使用该插件的项目，只需在 `PublicDependencyModuleNames` 中添加 `"StateGraph"`（以及可能的 `"StateGraphManager"`）。

| 模块 | 用途 |
|---|---|
| `StateGraphManager`（可选） | 如需更高级的状态图管理功能，依赖此模块 |

无其他特殊依赖（仅标准 Core、CoreUObject、Engine 等）。

## 维护状态

### 近期更新

```
2025-08-11   58a4ffe6    Making FStateGraph and FStateGraphNode respect -NoTimeouts
2025-07-21   2415c7aa    Fix two types of nodiscard warnings seen when building with Clang 20
2025-06-26   ec900998    Added UE_INLINE_GENERATED_CPP_BY_NAME to source files with .gen.cpp
2025-04-23   939cc6e5    Used FortniteClient build target to convert files to have dllstorage
2025-04-08   0d2c9a0c    Update StateGraph to use FDateTime and UTC time tracking
```

### 维护评价

- **活跃维护**：从 Git 历史看，2025 年 4 月至今（2025 年 8 月）有多次实质性更新（功能增强、API 调整、编译修复）。
- **持续演进**：最近的提交涉及对 `-NoTimeouts` 的尊重，说明开发者正在考虑性能优化和禁用超时的场景。
- **无废弃迹象**：所有提交均为功能或修复性质，无 deprecation 标记。
- **推荐使用**：适合需要灵活状态机的新项目，但需注意该插件仍为 **Experimental**，未来 API 可能变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StateGraph)
- [官方文档](https://docs.unrealengine.com/en-US/)（搜索“StateGraph”可查看官方示例和说明）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/StateGraph/Tests/StateGraphTests.cpp)