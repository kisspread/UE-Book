# MassAI

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 中文名 | 大规模AI |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavMeshNavigation` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 插件是 Epic Games 为 Unreal Engine 的 `MassGameplay` 框架专门开发的 AI 扩展组件。`MassGameplay` 提供了基于大规模实体（Mass Entity）的高性能游戏框架基础，而 MassAI 则在此基础上，为这些实体添加了具体的 AI 行为能力、复杂的导航逻辑以及支持网络复制的系统。

简单来说，`MassGameplay` 定义了“实体是什么”，而 `MassAI` 定义了“实体要怎么想、怎么动、怎么同步”。它解决了在管理成百上千乃至上万个 AI 实体时，传统基于 Actor 的 AI 系统（如行为树）在性能和扩展性上遇到的瓶颈问题。

## 使用场景

- **大规模 NPC 模拟**：你在制作开放世界游戏、城市模拟或策略游戏，需要同时控制数百个以上 NPC 的移动、寻路和简单决策，追求极致的运行时性能。
- **高性能路径跟随**：你需要一个能处理海量实体并发路径请求、并且与 `ZoneGraph`（区域图导航系统）深度集成的移动解决方案。
- **联网游戏中的 AI 同步**：你在开发多人在线游戏，需要将大规模 AI 实体的状态（尤其是路径跟随状态）高效、准确地同步给所有客户端，避免客户端表现与服务器逻辑脱节。
- **AI 行为的模块化扩展**：你想利用 `MassGameplay` 的处理器（Processor）和片段（Fragment）架构，以声明式、可组合的方式为实体添加 AI 行为，而不是使用庞大的单体行为树。

## 蓝图用法

MassAI 插件的核心功能高度依赖 C++ 和数据驱动的处理器，直接暴露给蓝图的可调用函数（UFUNCTION）相对较少，主要集中在调试、数据设置和全局系统控制层面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginPlay` / `EndPlay` | MassAI 管理器的生命周期控制 | `UMassAIManager` (示例类，需验证) |
| `SetSimulationEnabled` | 全局启用/禁用 AI 模拟 | `UMassAIManager` (示例类，需验证) |
| `SpawnAIAgent` | 通过蓝图生成一个具有 AI 逻辑的 Mass 实体 | `UMassAISpawner` (示例类，需验证) |
| `DrawDebug` | 控制 AI 相关调试信息的绘制 | `UMassAIDebug` (示例类，需验证) |

**说明**：由于 MassAI 是运行时模块，其核心逻辑（如行为树评估、寻路计算）由 `UMassProcessor` 子类在幕后执行，不直接暴露为蓝图节点。蓝图主要负责触发和配置这些系统。

### 使用示例（蓝图描述）

1.  **启用 AI 模拟**：
    *   在关卡蓝图的 `BeginPlay` 事件中，获取 `MassAIManager` 的实例，并调用 `SetSimulationEnabled(true)`。
2.  **配置 AI 实体生成**：
    *   创建一个自定义的 `DataAsset`（如 `UMassAIAgentConfig`），在其中定义实体的 AI 片段组合（例如：`FMassZoneGraphPathRequestFragment`， `FMassMoveTargetFragment`）。
    *   在游戏逻辑中（如 NPC 管理器），使用 `SpawnAIAgent` 节点，传入之前创建的 `DataAsset` 来生成带有指定 AI 配置的实体。
3.  **调试与监控**：
    *   通过 `DrawDebug` 节点开关，可以在运行时显示实体的预期路径、碰撞检测射线等调试信息。

## C++ 用法

MassAI 的 C++ 用法紧密围绕 `MassGameplay` 的 ECS（实体组件系统）架构展开。核心是定义自己的 **处理器（Processor）** 和 **片段（Fragment）**。

### 头文件引入

```cpp
#include "MassAIReplication.h" // 引入复制模块核心类
#include "MassAIBehavior.h"   // 引入行为模块核心类
```

### 基本用法

以下示例展示了如何使用 `MassAIReplication` 模块来同步实体的路径跟随状态。

**1. 定义你自己的复制 Agent 类（继承自 `FReplicatedAgentBase`）**：
```cpp
// MyReplicatedAgent.h
#pragma once
#include "MassReplicatedAgent.h"
#include "MassReplicationPathHandlers.h" // 引入路径复制支持

USTRUCT()
struct FMyReplicatedAgent : public FReplicatedAgentBase
{
    GENERATED_BODY()

    // 包含路径跟随数据，这是网络同步的关键
    UPROPERTY(Transient)
    FReplicatedAgentPathData ReplicatedPathData;

    // 提供路径数据的可修改访问器，TMassClientBubblePathHandler 需要它
    FReplicatedAgentPathData& GetReplicatedPathDataMutable() { return ReplicatedPathData; }
};
```

**2. 在你的复制处理器中集成路径处理**：
```cpp
// MyReplicationProcessor.h
#pragma once
#include "MassReplicationProcessor.h" // 假设的基类
#include "MassReplicationPathHandlers.h"

UCLASS()
class UMyReplicationProcessor : public UMassReplicationProcessorBase
{
    GENERATED_BODY()

protected:
    // 持有路径处理器实例，用于处理路径数据的复制逻辑
    FMassReplicationProcessorPathHandler PathHandler;

    virtual void Initialize(UObject& Owner) override
    {
        Super::Initialize(Owner);
        // 为你的实体查询添加路径相关片段的要求
        FMassEntityQuery& Query = /* ... */;
        PathHandler.AddRequirements(Query);
        // ... 其他初始化
    }

    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override
    {
        // 在遍历实体前，缓存路径片段视图
        PathHandler.CacheFragmentViews(Context);

        // ... 你的主循环 ...
        for (int32 EntityIdx = 0; EntityIdx < NumEntities; ++EntityIdx)
        {
            // 当需要向客户端气泡添加实体时
            if (/* 需要添加实体 */)
            {
                FReplicatedAgentPathData PathData;
                // 从当前实体获取路径数据填入 PathData
                // ...
                PathHandler.AddEntity(EntityIdx, PathData);
            }

            // 当需要修改已有实体时
            if (/* 需要修改实体 */)
            {
                // 假设你有一个指向客户端气泡处理器的指针
                // TMassClientBubbleHandler<AgentArrayItem>* BubbleHandler = ...;
                // PathHandler.ModifyEntity(Handle, EntityIdx, BubbleHandler->GetPathHandler(), bIsLastClient);
            }
        }
    }
};
```
*来源文件：`Public/MassReplicationPathHandlers.h`*

### 进阶用法

结合 `MassZoneGraphNavigation` 和 `MassAIReplication`，实现一个完整的、可复制的 NPC 行走循环。

1.  **定义行为处理器**：继承 `UMassProcessor`，评估 `FMassZoneGraphPathRequestFragment`，并生成 `FMassZoneGraphPathResultFragment`。
2.  **定义移动处理器**：继承 `UMassProcessor`，读取 `FMassZoneGraphPathResultFragment`，更新 `FMassMoveTargetFragment`。
3.  **集成复制**：在你的网络复制处理器中（如上例），使用 `FMassReplicationProcessorPathHandler` 来确保 `FMassMoveTargetFragment` 和 `FMassZoneGraphLaneLocationFragment` 的变化能被正确复制。
4.  **在客户端处理接收**：使用 `TMassClientBubblePathHandler` 在客户端为新生成的实体正确设置路径数据，或在实体状态更新时应用新的路径数据。

## Demo 示例

一个最小化的演示，展示如何定义支持网络路径复制的 AI Agent 片段。

**MyAIPathAgent.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "MassReplicatedAgent.h"
#include "MassReplicationPathHandlers.h"
#include "MyAIPathAgent.generated.h"

USTRUCT()
struct FMyAIPathAgent : public FReplicatedAgentBase
{
    GENERATED_BODY()

    UPROPERTY(Transient)
    FReplicatedAgentPathData ReplicatedPathData;

    FReplicatedAgentPathData& GetReplicatedPathDataMutable() { return ReplicatedPathData; }
};
```

**MyAIPathBubbleHandler.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "ClientBubbleHandler.h" // 假设的基类头文件
#include "MassReplicationPathHandlers.h"
#include "MyAIPathAgent.h"

// 自定义气泡项
struct FMyAIPathBubbleItem : public FMassClientBubbleItem
{
    FMyAIPathAgent Agent;
};

// 自定义气泡处理器
class FMyAIPathBubbleHandler : public TClientBubbleHandlerBase<FMyAIPathBubbleItem>
{
public:
    FMyAIPathBubbleHandler()
        : PathHandler(*this) // 初始化路径处理器，并将自身作为友元传入
    {}

    // 获取路径处理器
    TMassClientBubblePathHandler<FMyAIPathBubbleItem>& GetPathHandler() { return PathHandler; }

protected:
    // 路径跟随复制处理器，作为成员变量
    TMassClientBubblePathHandler<FMyAIPathBubbleItem> PathHandler;
};
```
*这个示例定义了网络复制系统需要的数据结构和处理器骨架。*

## 模块依赖

MassAI 插件的各个模块依赖于标准的 UE 核心和编辑器模块。其中 `MassAIReplication` 模块有一个特殊的依赖，用于其调试和编辑器集成。

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 用于集成编辑器框架，可能用于自定义面板或资产编辑器。 |
| `UnrealEd` | 提供编辑器工具和命令，用于 AI 行为、导航和调试的开发时支持。 |
| `MassEntityEditor` | 为 Mass 实体系统提供编辑器支持，MassAI 的调试模块依赖它。 |

**注意**：上述模块主要用于**开发、调试和编辑器工具**。对于纯运行时的游戏逻辑，你的 `Build.cs` 可能只需要依赖 `MassAI` 插件的运行时模块（如 `MassAIBehavior`, `MassNavigation`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 移除INFINITY宏以修复新版Windows SDK的编译错误 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | 修复Mass调试器对无效实体的处理 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中可能导致错误输出的问题 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | （相关于回放调试器的改动） |

### 维护评价

MassAI 是一个相对较新（约4年）且持续维护的插件。从提交历史看，其更新**非常活跃**，最近几个月（2026年4-5月）有多次提交，主要集中在：
1.  **编译器和平台兼容性修复**（如处理最新的Windows SDK和严格浮点模式），表明它跟随着引擎的构建基础设施更新。
2.  **Bug修复和稳定性改进**（如修复调试器对无效实体的处理），体现了对运行时质量的关注。
3.  与其他系统（如RewindDebugger）的集成更新。

尽管标记为 **实验性（IsExperimentalVersion=true）** 且 **默认未启用（EnabledByDefault=false）**，但从其活跃的维护状态来看，它是一个**正在积极开发和迭代**的核心 AI 框架组件。Epic Games 在其官方项目中（如《堡垒之夜》的AI）很可能大量使用了 MassAI 的理念或早期版本。**推荐在需要高性能大规模AI的项目中试用和评估**，但需注意其 API 和功能在正式版中可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)
- [测试用例]（路径未在提供信息中明确，通常位于 `Engine/Plugins/AI/MassAI/Source/MassAITestSuite/` 或引擎测试目录中）