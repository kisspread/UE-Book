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

StateGraph 提供了一个轻量、高效的状态机管理框架，核心是 `FStateGraph` 和 `FStateGraphNode` 两个运行时结构。它解决了 Unreal Engine 中缺乏通用、低开销状态机基础设施的问题，允许开发者以纯 C++ 的方式构建、运行和追踪有限状态机（FSM），无需依赖重量级的 UObject 或 Blueprint 系统。适用于需要高性能状态转换逻辑的场景，如 AI 决策、动画状态混合、游戏流程控制等。

## 使用场景

- 实现角色 AI 的有限状态机（巡逻、警戒、战斗状态切换）
- 管理 UI 导航状态（菜单、设置、游戏界面）
- 控制动画层状态（空闲、行走、跑步、跳跃）
- 需要可复用的、无蓝图的纯 C++ 状态机时

## 蓝图用法

> 注意：StateGraph 目前处于实验阶段，蓝图接口尚未公开。所有 API 均为 C++ 原生类型，暂不提供蓝图可调用节点。若需蓝图集成，建议手动封装为 UObject 子系统。

### 核心节点

暂无公开的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 成员。计划未来版本可能通过 `UStateGraph` 提供蓝图包装。

## C++ 用法

### 头文件引入

```cpp
#include "StateGraph.h"        // 核心 FStateGraph
#include "StateGraphNode.h"    // 节点类型定义
```

### 基本用法

通过 `FStateGraph` 创建并驱动状态机。以下示例构建一个简单的三状态机（空闲 → 行走 → 奔跑）。

```cpp
// 来源：Tests/StateGraphTests/Private/StateGraphTests.cpp（简化）
#include "StateGraph.h"
#include "StateGraphNode.h"

void SampleStateMachine()
{
    // 创建状态图实例
    FStateGraph Graph;

    // 定义状态节点（使用整型 ID 标识）
    uint32 IdleNode = Graph.AddNode(0);
    uint32 WalkNode = Graph.AddNode(1);
    uint32 RunNode  = Graph.AddNode(2);

    // 配置节点属性（可附加任意用户数据）
    Graph.GetNode(IdleNode).SetUserData<int32>(100);
    Graph.GetNode(WalkNode).SetUserData<int32>(200);
    Graph.GetNode(RunNode).SetUserData<int32>(300);

    // 设置初始状态
    Graph.SetActiveNode(IdleNode);

    // 执行状态转换（例如从空闲切换到行走）
    Graph.SetActiveNode(WalkNode);

    // 获取当前状态
    uint32 CurrentNodeId = Graph.GetActiveNode();
    int32  UserData = Graph.GetNode(CurrentNodeId).GetUserData<int32>();
    // UserData == 200

    // 重置状态机
    Graph.ResetActiveNode();
}
```

### 进阶用法

`FStateGraphNode` 支持泛型用户数据存储，可附加任意 `TSharedPtr` 或 POD 类型的数据。结合 `FDateTime` 时间追踪，可实现超时自动转换。

```cpp
// 来源：Tests/StateGraphTests/Private/StateGraphTests.cpp（组合示例）
#include "StateGraph.h"
#include "StateGraphNode.h"
#include "Misc/DateTime.h"

void TimedStateMachine()
{
    FStateGraph Graph;
    uint32 A = Graph.AddNode(10);
    uint32 B = Graph.AddNode(20);

    // 为节点 A 设置超时阈值（300 秒后自动切换）
    Graph.GetNode(A).SetTimeout(FTimespan::FromSeconds(300.0));
    Graph.SetActiveNode(A);

    // 模拟时间流逝
    FDateTime StartTime = FDateTime::UtcNow();

    // 检查是否超时
    if (Graph.GetNode(A).GetElapsedTime() > Graph.GetNode(A).GetTimeout())
    {
        Graph.SetActiveNode(B);
    }
}
```

> 注意：`FStateGraph` 支持 `-NoTimeouts` 编译选项（见 git 历史），在无超时需求的编译配置下可跳过时间计算以提升性能。

## Demo 示例

以下是一个完整的、可编译的 C++ 示例，演示使用 StateGraph 实现一个简单的 AI 巡逻/追击状态机。

### StateGraphDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "StateGraph.h"
#include "StateGraphNode.h"

enum class EAIState : uint8
{
    Patrol,
    Chase,
    Attack
};

class FAIStateMachine
{
public:
    FAIStateMachine();
    void Update(float DeltaTime);
    void SetState(EAIState NewState);
    EAIState GetCurrentState() const;

private:
    FStateGraph Graph;
    uint32 PatrolNodeId;
    uint32 ChaseNodeId;
    uint32 AttackNodeId;
};
```

### StateGraphDemo.cpp

```cpp
#include "StateGraphDemo.h"

FAIStateMachine::FAIStateMachine()
{
    PatrolNodeId = Graph.AddNode(static_cast<uint32>(EAIState::Patrol));
    ChaseNodeId  = Graph.AddNode(static_cast<uint32>(EAIState::Chase));
    AttackNodeId = Graph.AddNode(static_cast<uint32>(EAIState::Attack));

    // 设置初始状态
    Graph.SetActiveNode(PatrolNodeId);
}

void FAIStateMachine::Update(float DeltaTime)
{
    // 你可以在此处根据游戏逻辑触发状态切换
    // 例如检测到敌人时：SetState(EAIState::Chase);
}

void FAIStateMachine::SetState(EAIState NewState)
{
    uint32 TargetId;
    switch (NewState)
    {
    case EAIState::Patrol:  TargetId = PatrolNodeId; break;
    case EAIState::Chase:   TargetId = ChaseNodeId;  break;
    case EAIState::Attack:  TargetId = AttackNodeId; break;
    default:                return;
    }
    Graph.SetActiveNode(TargetId);
}

EAIState FAIStateMachine::GetCurrentState() const
{
    uint32 ActiveId = Graph.GetActiveNode();
    if (ActiveId == PatrolNodeId) return EAIState::Patrol;
    if (ActiveId == ChaseNodeId)  return EAIState::Chase;
    if (ActiveId == AttackNodeId) return EAIState::Attack;
    return EAIState::Patrol; // fallback
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | StateGraph 及其测试模块仅依赖 Core、CoreUObject 等引擎核心模块，无第三方或特殊依赖。 |

> 说明：`StateGraphManager` 模块是对 `StateGraph` 的进一步封装，提供管理器级别的功能，但其依赖同样仅限于引擎基础模块。

## 维护状态

### 近期更新

- 2025-08-11 `58a4ffe` — 让 `FStateGraph` 和 `FStateGraphNode` 尊重 `-NoTimeouts` 编译选项
- 2025-07-21 `2415c7a` — 修复 Clang 20 编译时因 `nodiscard` 引发的两处警告
- 2025-06-26 `ec90099` — 为包含 `.gen.cpp` 的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏
- 2025-04-23 `939cc6e` — 使用 FortniteClient 构建目标进行 `dllstorage` 属性转换
- 2025-04-08 `0d2c9a0` — 让 StateGraph 改用 `FDateTime` 和 UTC 时间追踪

### 维护评价

StateGraph 是一个全新的实验性插件（2025年4月创建），截至最近更新仅4个月，仍处于早期活跃开发阶段。更新内容集中在编译修复、时间追踪优化和构建系统适配，尚未暴露出完整的蓝图集成或大规模功能迭代。由于插件位于 `Experimental` 目录且默认未启用，API 和设计可能在未来发生变化。**建议在原型阶段或测试项目中使用，谨慎用于生产环境。** 如果没有明确的成本收益，建议暂缓采用，等待其进入正式版。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StateGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StateGraph/Tests/StateGraphTests)
- 官方文档：暂无（插件过于早期）