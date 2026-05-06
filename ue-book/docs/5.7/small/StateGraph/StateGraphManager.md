# State Graph

> Generic state machine management class.

| 属性 | 值 |
|---|---|
| 中文名 | 状态图系统 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StateGraph` (Runtime), `StateGraphManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StateGraph) | |

> **注意**：该插件位于 `Experimental` 目录，API 和行为可能在未来版本中发生变化。

## 用途

`State Graph` 插件提供了一套轻量级的状态图运行时框架，并附带多个预构建的管理器（Manager），用于管理引擎和游戏中的复杂异步流程。

- **`StateGraph` 模块**：定义了核心数据结构 `FStateGraph`（状态图容器）、`FStateGraphNode`（状态节点基类）及其引用/指针类型。支持节点依赖、生命周期跟踪、超时处理等功能。
- **`StateGraphManager` 模块**：提供了管理器基类 `UE::FStateGraphManager` 和 `UE::FStateGraphManagerTracked`，允许其他模块通过注册委托的方式动态构建状态图实例。内置了三个使用场景的管理器：
  - `UClientJoinManager` - 客户端加入服务器流程的状态图管理
  - `UPreLoginAsyncManager` - 游戏模式预登录异步流程的管理
  - `URegisterServerManager` / `URestartServerManager` - 服务器注册/重启流程

该插件解决了传统上硬编码的异步逻辑难以扩展和复用的问题，允许不同子系统通过独立的委托来贡献状态图节点，实现面向切面的流程编排。

## 使用场景

- 需要管理多步骤、可配置的异步登录流程（客户端 → 服务器验证 → 创建玩家 → 进入世界）
- 在 `PreLogin` 阶段执行自定义检查（如反作弊、排队、数据下载），并支持动态扩展
- 游戏框架内任何需要按顺序/并行执行多个异步任务并统一完成回调的场景

## 蓝图用法

该插件目前**未公开任何蓝图可调用函数或可蓝图继承的类**。所有管理器子类和核心状态图类均为 C++ 类，推荐在 C++ 项目中使用。

如需在蓝图中使用，可以编写 C++ 包装函数，将其转化为蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "StateGraphManager.h"
#include "StateGraph.h"
#include "PreLoginAsyncManager.h" // 以预登录管理器为例
```

### 基本用法：使用 `FStateGraphManager` 创建未跟踪的状态图

```cpp
#include "StateGraphManager.h"

// 假设已经获取到某个管理器实例（例如 UPreLoginAsyncManager）
UPreLoginAsyncManager* Manager = ...;

// 创建一个未跟踪的状态图实例
UE::FStateGraphPtr Graph = Manager->Create(TEXT("MyCustomLogin"));

// 此时，Manager 中注册的所有创建委托都会被调用，
// 各个子系统可以向 Graph 中添加节点。
// 然后可以手动启动 Graph 中的节点处理流程。
```

### 进阶用法：使用 `FStateGraphManagerTracked` 跟踪并查找已创建的图

```cpp
// 假设有一个自定义管理器继承自 FStateGraphManagerTracked
class UMyCustomManager : public UWorldSubsystem, public UE::FStateGraphManagerTracked
{
public:
    virtual FName GetStateGraphName() const override
    {
        return FName(TEXT("MyCustomFlow"));
    }
};

// 创建并跟踪（上下文名为连接 ID 或用户 ID）
UMyCustomManager* MyManager = ...;
UE::FStateGraphPtr Graph = MyManager->Create(TEXT("Player_001"));

// 在其他地方查找该图
UE::FStateGraphPtr FoundGraph = MyManager->Find(TEXT("Player_001"));

// 移除该图并释放资源
MyManager->Remove(TEXT("Player_001"));
```

### 使用 `UPreLoginAsyncManager` 处理预登录异步

```cpp
// 在 GameMode 的 PreLoginAsync 实现中
void AMyGameMode::PreLoginAsync(const FString& Options, const FString& Address, const FUniqueNetIdRepl& UniqueId, const FOnPreLoginCompleteDelegate& OnComplete)
{
    // 获取 PreLoginAsyncManager
    UPreLoginAsyncManager* Manager = GetWorld()->GetSubsystem<UPreLoginAsyncManager>();
    if (ensure(Manager))
    {
        // 1. 创建一个空状态图（此时尚没有节点）
        UE::FStateGraphPtr Graph = Manager->Create(TEXT("MyPreLogin_") + UniqueId.ToString());
        // 2. 初始化状态图，将选项等信息存入 Options 节点，并开始跟踪
        Manager->InitializeStateGraph(*Graph, Options, Address, UniqueId, OnComplete);
        // 之后，其他注册的委托（如反作弊子系统）会自动向该图添加节点，
        // 并在这些节点完成后调用 CompleteLogin 完成流程。
    }
}

// 在反作弊子系统（或其他子系统）中注册委托
void UMyAntiCheatSystem::Initialize(FSubsystemCollectionBase& Collection)
{
    if (UPreLoginAsyncManager* Manager = Collection.GetSubsystem<UPreLoginAsyncManager>())
    {
        Manager->AddCreateDelegate(FStateGraphManagerCreateDelegate::CreateUObject(this, &UMyAntiCheatSystem::OnCreatePreLoginGraph));
    }
}

bool UMyAntiCheatSystem::OnCreatePreLoginGraph(UE::FStateGraph& StateGraph)
{
    using namespace UE::PreLoginAsync;
    // 读取选项
    FOptionsPtr Options = FOptions::Get(StateGraph);
    if (!Options)
    {
        return false;
    }
    // 创建自定义节点进行反作弊检查，完成后调用 CompleteLogin
    // 可以创建继承自 FStateGraphNode 的节点并添加到 StateGraph
    return true;
}
```

## Demo 示例

以下展示一个自定义管理器，用于模拟异步资源加载流程。

### MyAsyncFlowManager.h

```cpp
#pragma once

#include "StateGraphManager.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyAsyncFlowManager.generated.h"

UCLASS()
class UMyAsyncFlowManager : public UGameInstanceSubsystem, public UE::FStateGraphManagerTracked
{
    GENERATED_BODY()

public:
    virtual FName GetStateGraphName() const override
    {
        return FName(TEXT("AsyncResourceFlow"));
    }

    void AddLoadStep(const FString& StepName);
};
```

### MyAsyncFlowManager.cpp

```cpp
#include "MyAsyncFlowManager.h"
#include "StateGraph.h"

// 自定义节点：加载一个资源，完成后标记完成
class FLoadAssetNode : public UE::FStateGraphNode
{
public:
    FLoadAssetNode(const FString& InAssetPath)
        : UE::FStateGraphNode(FName(*InAssetPath))
        , AssetPath(InAssetPath)
    {}

    virtual void Start() override
    {
        // 模拟异步加载
        Async(EAsyncExecution::ThreadPool, [this]()
        {
            // 加载完成
            Async(EAsyncExecution::GameThread, [this]()
            {
                Complete();
            });
        });
    }

private:
    FString AssetPath;
};

void UMyAsyncFlowManager::AddLoadStep(const FString& StepName)
{
    AddCreateDelegate(FStateGraphManagerCreateDelegate::CreateLambda([StepName](UE::FStateGraph& Graph) -> bool
    {
        Graph.AddNode<FLoadAssetNode>(StepName);
        return true;
    }));
}

// 使用示例
void UMyAsyncFlowManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    AddLoadStep(TEXT("Texture_Pack"));
    AddLoadStep(TEXT("Audio_Pack"));

    // 实际使用
    UE::FStateGraphPtr Graph = Create(TEXT("LoadSession_001"));
    // Graph 自动开始执行节点...
}
```

## 模块依赖

使用 `StateGraphManager` 模块时，你的模块需要在 `Build.cs` 中添加以下依赖（省略标准 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `StateGraph` | 依赖核心状态图数据结构 |
| `GameplayTags` | 可选，如果使用标签系统（示例中未体现，但部分内部实现可能依赖） |

> 实际依赖可从 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 中提取。当前已知 `PreLoginAsyncManager` 依赖于 `OnlineSubsystemUtils`（通过 `FUniqueNetIdRepl`），建议一并包含。

## 维护状态

### 近期更新

```
2025-08-11 58a4ffe6 修复 FStateGraph 和 FStateGraphNode 对 -NoTimeouts 的兼容性
2025-07-21 2415c7aa 修复 Clang 20 编译时的 nodiscard 警告
2025-06-26 ec900998 为对应 .gen.cpp 的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏
2025-04-23 939cc6e5 为所有方法/静态变量添加 DLL 导出存储（Fortnite 客户端构建目标）
2025-04-08 0d2c9a0c 更新 StateGraph 使用 FDateTime 和 UTC 时间追踪
```

### 维护评价

- **创建时间**：2025-04-08，距今约 4 个月（文档撰写时）。
- **活跃度**：持续有功能性更新和修复（最近为 2025-08-11），属于活跃维护。
- **稳定性**：该插件仍处于实验阶段，API 可能变化，但核心概念已基本稳定。
- **建议**：适合愿意接受 API 变动的项目提前适配。如果追求稳定，建议等待正式版。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StateGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StateGraph/Tests)