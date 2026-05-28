# ML Adapter

> A framework for training and utilizing machine learning agents in games. Creates an RPC interface through which an external process can query game state and control in-game actors. Once trained, agents can be run in-engine via neural networks loaded from ONNX models.

| 属性 | 值 |
|---|---|
| 中文名 | 机器学习适配器 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MLAdapter` (Runtime), `MLAdapterTestSuite` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-12 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter) | |

## 用途

MLAdapter 为 UE5 游戏提供了一个**机器学习训练与推理框架**。它解决的核心问题是：如何让外部的 ML 训练进程（通常是 Python 环境中的强化学习库）与游戏世界进行双向通信。

具体来说，它做了三件事：

1. **RPC 桥梁**：通过 rpclib 建立一个 RPC 服务器，允许外部进程以远程调用的方式查询游戏状态（观测值/Observations）和控制游戏内 Actor（动作/Actions）
2. **Agent 管理**：在引擎内管理多个 ML Agent，为每个 Agent 提供观测空间（Observation Space）和动作空间（Action Space）的抽象
3. **ONNX 推理**：训练完成后，可以将神经网络模型以 ONNX 格式加载到引擎内，脱离外部训练进程直接运行 Agent

这个插件的前身是 UE4ML，在 UE5 早期开发时重命名为 MLAdapter。它依赖 **GameplayAbilities** 和 **EnhancedInput** 插件，说明它可以将游戏技能系统和增强输入系统作为 Agent 的观测和动作接口。

## 使用场景

- 你在训练游戏 AI 替代传统行为树 → 使用 MLAdapter 作为 RL 训练环境
- 你需要用强化学习训练 NPC 寻路、战斗等复杂行为 → 外部 Python 进程通过 RPC 与游戏交互
- 你已经训练好了 ML 模型，想直接在引擎中部署 → 用 ONNX 模式运行，无需外部进程
- 你需要批量运行游戏模拟来收集训练数据 → 利用 RPC 接口自动化控制游戏流程

## 蓝图用法

由于该插件的 RPC 和 Agent 管理主要在 C++ 层实现，蓝图暴露的 API 主要集中在 Agent 配置和管理层面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UMLAdapterManager::Get()` | 获取 ML 适配器管理器单例 | `UMLAdapterManager` |
| `GetOnAddClientFunctions` | 绑定 RPC 客户端函数的委托 | `UMLAdapterManager` |
| `GetOnAddServerFunctions` | 绑定 RPC 服务端函数的委托 | `UMLAdapterManager` |

> **注意**：该插件的核心交互逻辑依赖 C++ 的 RPC 绑定机制，蓝图层面主要用于配置。详细的 Agent 注册和观测/动作空间定义需要在 C++ 中完成。

## C++ 用法

### 头文件引入

```cpp
#include "MLAdapterModule.h"
```

### 基本用法

**RPC 客户端与服务端绑定**（来源：`Source/MLAdapterTestSuite/Private/RPCTestBase.h`）：

```cpp
#include "MLAdapterManager.h"
#include "RPCServer.h"

// 创建一个测试基类，绑定 RPC 客户端和服务端函数
struct FRPCTestBase : public FAITestBase
{
    enum { DefaultServerPort = 10101 };

    EMLAdapterServerMode Mode = EMLAdapterServerMode::Client;
    rpc::client* RPCClient = nullptr;

    FRPCTestBase()
    {
        // 绑定 RPC 客户端函数 —— 当客户端连接时调用
        BindClientHandle = UMLAdapterManager::Get().GetOnAddClientFunctions().AddLambda(
            [this](FRPCServer& Server)
            {
                SetUpClientBinds(Server);
            });

        // 绑定 RPC 服务端函数 —— 暴露给外部进程的函数
        BindServerHandle = UMLAdapterManager::Get().GetOnAddServerFunctions().AddLambda(
            [this](FRPCServer& Server)
            {
                SetUpServerBinds(Server);
            });
    }

    virtual void SetUpClientBinds(FRPCServer& Server) {}
    virtual void SetUpServerBinds(FRPCServer& Server) {}
};
```

### 进阶用法

**自定义 RPC 服务端函数**：你可以通过 `GetOnAddServerFunctions` 委托向 RPC 服务器注册自定义函数，让外部 Python 进程能够调用：

```cpp
UMLAdapterManager::Get().GetOnAddServerFunctions().AddLambda(
    [](FRPCServer& Server)
    {
        // 注册一个自定义函数，外部进程可通过 rpc.call("my_custom_function") 调用
        Server.Bind("my_custom_function", [](int32 Param) -> int32
        {
            // 处理来自外部进程的调用
            return ProcessCustomFunction(Param);
        });
    });
```

## Demo 示例

```cpp
// MyMLAgent.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMLAgent.generated.h"

UCLASS()
class MYGAME_API AMyMLAgent : public AActor
{
    GENERATED_BODY()

public:
    AMyMLAgent();

    virtual void BeginPlay() override;

    // 执行由 ML 推理得出的动作
    void ExecuteAction(const TArray<float>& ActionValues);

    // 获取当前观测值
    TArray<float> GetObservations() const;

private:
    FVector InitialPosition;
};
```

```cpp
// MyMLAgent.cpp
#include "MyMLAgent.h"
#include "MLAdapterManager.h"

AMyMLAgent::AMyMLAgent()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyMLAgent::BeginPlay()
{
    Super::BeginPlay();
    InitialPosition = GetActorLocation();
}

TArray<float> AMyMLAgent::GetObservations() const
{
    TArray<float> Observations;
    FVector Pos = GetActorLocation() - InitialPosition;
    Observations.Add(Pos.X / 1000.0f);  // 归一化位置
    Observations.Add(Pos.Y / 1000.0f);
    Observations.Add(Pos.Z / 1000.0f);
    return Observations;
}

void AMyMLAgent::ExecuteAction(const TArray<float>& ActionValues)
{
    if (ActionValues.Num() >= 2)
    {
        FVector Movement(ActionValues[0] * 100.0f, ActionValues[1] * 100.0f, 0.0f);
        AddActorWorldOffset(Movement, true);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RPCLib` | 底层 RPC 通信库（rpclib），用于与外部 ML 训练进程通信 |
| `GameplayAbilities` | 插件依赖，可将 GAS 技能系统暴露为 Agent 的动作空间 |
| `EnhancedInput` | 插件依赖，可将增强输入系统暴露为 Agent 的动作接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 宏到新的 UE_LOGF 格式 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换，第二次提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的改动 CL51314860 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist... | 将引擎初始化委托迁移为 Get 方法以修复注册缺失问题 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复 printf 格式化说明符 |

### 维护评价

- **实验性状态**：该插件从创建起就标记为 `IsExperimentalVersion = true`，且默认未启用，说明 Epic 将其定位为实验性功能
- **活跃维护中**：最近的提交（2026-04-14）距离当前很近，说明仍在跟随 UE5 引擎更新进行维护
- **更新类型**：近期提交主要是引擎 API 迁移（UE_LOGF、委托 API 变更）和编译修复，而非功能性更新
- **历史背景**：由 Nick Whiting 和 Mikko Mononen 在 UE5 早期开发时从 UE4ML 重命名而来，是 Epic 内部 ML 训练基础设施的一部分
- **注意事项**：该插件需要 rpclib 外部依赖，且实验性标记意味着 API 可能发生破坏性变更
- **推荐**：适合对 ML 训练游戏 AI 有明确需求的开发者，但不建议用于生产环境的核心系统

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter)
- 测试用例位于 `Source/MLAdapterTestSuite/` 模块内