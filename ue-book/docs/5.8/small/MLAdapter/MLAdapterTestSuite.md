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
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter) | |

## 用途
MLAdapter 为在虚幻引擎中集成机器学习代理提供了一个框架。它解决了将外部机器学习训练环境（如 Python 脚本、强化学习框架）与引擎内游戏世界连接的核心问题。该插件通过创建一个 RPC（远程过程调用）服务器，允许外部进程实时查询游戏状态（如观察空间）并执行动作（如控制游戏内角色），从而支持代理的训练。训练完成后，可以将训练好的神经网络以 ONNX 格式加载回引擎，使代理能够在游戏内独立运行，无需持续连接外部进程。

## 使用场景
- 你正在使用强化学习（如 PPO、DQN）训练游戏中的 AI 代理（例如 NPC 行为、游戏角色控制）。
- 你需要一个桥梁，让你的 Python 训练脚本能够与虚幻引擎中的游戏实例进行双向通信。
- 你希望将训练好的 AI 模型（ONNX 格式）集成到游戏中，使其作为游戏逻辑的一部分直接运行。
- 你需要在引擎内运行标准化的、与机器学习环境类似的接口，以便使用 Gym-like 的 API 进行交互。

## 蓝图用法
由于该插件主要通过 C++ 模块和 RPC 接口与外部环境交互，其核心功能并非为蓝图可视化脚本设计。然而，插件可能会暴露一些用于配置或状态查询的蓝图函数。基于其设计目标，主要的蓝图交互点可能在于配置观察、动作空间或监控代理状态。

### 核心节点
（根据当前模块（测试套件）的代码分析，未发现直接的 `BlueprintCallable` 函数。其主要接口是 C++ 层面的 RPC 绑定和管理。）

## C++ 用法

### 头文件引入
```cpp
// 引入 MLAdapter 核心模块
#include "MLAdapter.h"
// 引入 RPC 服务器相关接口
#include "RPCServer.h"
```

### 基本用法
以下示例展示了如何创建一个用于测试的 RPC 客户端与 MLAdapter 服务器交互的基类。
*来源：`Source/MLAdapterTestSuite/Private/RPCTestBase.h`*

```cpp
// 前置声明
namespace rpc { class client; }

// 定义一个用于 RPC 测试的基类
struct FRPCTestBase : public FAITestBase
{
    enum 
    {
        DefaultServerPort = 10101
    }; 

    EMLAdapterServerMode Mode = EMLAdapterServerMode::Client;
    FDelegateHandle BindClientHandle;
    FDelegateHandle BindServerHandle;
    rpc::client* RPCClient = nullptr;

    FRPCTestBase()
    {
        // 绑定事件：当 MLAdapter 添加客户端函数时，调用 SetUpClientBinds 进行设置
        BindClientHandle = UMLAdapterManager::Get().GetOnAddClientFunctions().AddLambda([this](FRPCServer& Server)
        {
            SetUpClientBinds(Server);
        });
        // 绑定事件：当 MLAdapter 添加服务器函数时，调用 SetUpServerBinds 进行设置
        BindServerHandle = UMLAdapterManager::Get().GetOnAddServerFunctions().AddLambda([this](FRPCServer& Server)
        {
            SetUpServerBinds(Server);
        });
    }

    // 派生类可重写此函数以绑定需要由外部客户端调用的函数
    virtual void SetUpClientBinds(FRPCServer& Server) {}
    // 派生类可重写此函数以绑定服务器可调用的函数
    virtual void SetUpServerBinds(FRPCServer& Server) {}
    
    virtual void TearDown() override;
};
```

### 进阶用法
要创建一个完整的、可被外部训练脚本控制的游戏代理，通常需要：
1.  **实现 `FMLAdapterAgent` 或类似基类**：定义代理的状态观察空间和可用动作空间。
2.  **配置 RPC 函数**：在 `SetUpClientBinds` 中注册 `GetObservation` 等函数，允许外部进程获取游戏状态；在 `SetUpServerBinds` 中注册 `ApplyAction` 函数，允许外部进程执行动作。
3.  **与游戏循环集成**：将代理的步骤循环与游戏的 `Tick` 同步，通常通过 `FMLAdapterManager` 管理的服务器请求处理来驱动。

## Demo 示例
一个最小化的 C++ 示例，演示如何创建一个继承自 MLAdapter 接口的代理类框架。
```cpp
// MyAgent.h
#pragma once

#include "MLAdapterTypes.h" // 假设包含基础类型
#include "MyAgent.generated.h"

UCLASS()
class UMyMLAgent : public UObject // 或继承自 FMLAdapterAgent 等适当基类
{
    GENERATED_BODY()

public:
    // 注册到 MLAdapter 系统
    void Register();

    // 获取当前观测值，供外部 RPC 调用
    UFUNCTION()
    TArray<float> GetObservation() const;

    // 接收并应用来自外部的动作
    UFUNCTION()
    void ApplyAction(const TArray<float>& Action);

private:
    // 代理内部状态
    FVector Position;
};
```
```cpp
// MyAgent.cpp
#include "MyAgent.h"
#include "MLAdapter.h" // 插件主头文件
#include "RPCServer.h"

void UMyMLAgent::Register()
{
    // 此处应有逻辑将 GetObservation 和 ApplyAction 绑定到 RPC 服务器
    // 具体绑定方式取决于 MLAdapterManager 提供的接口
    // 例如，在某个 OnAddClientFunctions 的委托中绑定:
    // Server.AddMethod(TEXT("my_agent.get_observation"), rpc::bind(&UMyMLAgent::GetObservation, this));
}

TArray<float> UMyMLAgent::GetObservation() const
{
    // 将游戏状态转换为浮点数组
    return { Position.X, Position.Y, Position.Z };
}

void UMyMLAgent::ApplyAction(const TArray<float>& Action)
{
    if (Action.Num() > 0)
    {
        // 根据动作数组更新代理状态，例如移动方向
        Position += FVector(Action[0], Action[1], 0.0f) * 10.0f;
    }
}
```

## 模块依赖
| 模块 | 用途 |
|---|---|
| `RPCLib` | 提供 RPC (远程过程调用) 的底层网络通信功能。 |
| `GameplayAbilities` | 插件依赖的外部插件，可能用于代理技能系统交互。 |
| `EnhancedInput` | 插件依赖的外部插件，可能用于将动作映射到增强输入系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新版UE_LOGF。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复前次提交中错误的查找替换。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了一次有问题的提交。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing registration. | 迁移引擎初始化委托以修复注册丢失问题。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符。 |

### 维护评价
- **创建时间**：该插件于2021年创建，已有约5年历史。
- **活跃度**：近期（2026年2月至4月）有多次提交，主要是针对引擎API变更（如委托函数签名、日志宏）的适配性修改和编译错误修复，表明其处于**活跃维护**状态。
- **状态**：插件被标记为实验性 (`IsExperimentalVersion: true`) 且默认未启用 (`EnabledByDefault: false`)，这意味着Epic官方可能认为其API或功能尚未完全稳定，不建议在生产环境中直接依赖。
- **推荐**：对于研究和实验机器学习与UE集成的开发者，这是一个官方提供的、值得关注的参考框架。但因其实验性状态，直接用于正式项目需谨慎，并做好应对API变更的准备。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter/Source/MLAdapterTestSuite)