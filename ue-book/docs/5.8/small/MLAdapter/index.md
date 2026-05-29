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
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter) | |

## 用途
MLAdapter 是一个在虚幻引擎内为游戏训练和运行机器学习代理的框架。它解决了传统 AI 无法利用强化学习等方法进行自适应训练的问题。其核心是通过 RPC（远程过程调用）库建立一个双向通信接口，允许外部进程（如 Python 训练脚本）实时查询游戏状态（如角色位置、速度、生命值）并向游戏内的 Actor 发送控制指令。训练完成后，可以将训练好的神经网络模型（ONNX 格式）加载到引擎中，让代理独立运行。

## 使用场景
- **强化学习训练**：你在为游戏中的一个 NPC 或玩家角色训练复杂的决策行为（如格斗、寻路、策略）。你需要通过 Python 脚本循环获取游戏状态、计算奖励并发送动作，用于训练模型。
- **部署已训练的代理**：你已经通过其他框架（如 PyTorch）训练好了一个 ONNX 格式的神经网络模型，希望将其快速集成到游戏逻辑中，让 NPC 基于该模型做出决策。
- **机器学习研究与原型开发**：你需要在虚幻引擎这个高保真环境中快速搭建、测试和可视化机器学习算法在游戏场景中的表现。

## 蓝图用法
作为框架性插件，MLAdapter 的核心功能主要通过 C++ API 暴露，用于与外部训练脚本通信和管理代理。蓝图层面更多是配置和管理代理的入口点，而非直接的数据流控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAgentConfig` | 为 ML 代理设置配置参数 | `UMLAdapterComponent` |
| `GetAgentState` | 获取代理当前的状态信息 | `UMLAdapterComponent` |
| `StartSession` | 启动一个 ML 交互会话 | `UMLAdapterSubsystem` |

## C++ 用法
### 头文件引入
```cpp
#include "MLAdapterComponent.h"
#include "MLAdapterSubsystem.h"
```

### 基本用法
核心流程包括：获取子系统、启动会话、以及通过代理组件与外部进程交互。
```cpp
// 获取全局的 MLAdapter 子系统
UMLAdapterSubsystem* MLSubsystem = GEngine->GetEngineSubsystem<UMLAdapterSubsystem>();

// 启动一个用于监听外部连接的会话
MLSubsystem->StartSession();

// 在你的 Pawn 或 Actor 中，通常会添加一个 UMLAdapterComponent
// 该组件会自动将该 Actor 注册为可被外部控制的“代理”。
// 你可以在组件中重写如 GetAgentState 等方法来定义向外部发送的状态数据。
```

### 进阶用法
实际使用中，你通常需要：
1.  **定义 Agent**：创建包含 `UMLAdapterComponent` 的 Actor。
2.  **实现状态/动作**：重写组件方法来定义哪些游戏数据作为状态发送，以及如何解析接收到的动作指令。
3.  **通信**：使用插件提供的 RPC 接口库（RPCLib）与外部 Python 进程建立连接并进行数据交换。
（注：具体 RPC 调用细节封装在 `MLAdapter` 模块内部，通常使用者无需直接调用 RPCLib）。

## Demo 示例
由于此插件主要用于构建训练和通信框架，完整的演示通常涉及引擎外的 Python 脚本。一个最小可运行示例的骨架如下：
```cpp
// MyMLCharacter.h
#pragma once
#include "GameFramework/Character.h"
#include "MLAdapterComponent.h"
#include "MyMLCharacter.generated.h"

UCLASS()
class AMyMLCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AMyMLCharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UMLAdapterComponent* MLAdapterComponent;

    // 重写以定义发送给外部代理的状态
    virtual TMap<FName, FMLAdapterFloatArray> GetAgentState_Implementation();
};
```
```cpp
// MyMLCharacter.cpp
#include "MyMLCharacter.h"

AMyMLCharacter::AMyMLCharacter()
{
    MLAdapterComponent = CreateDefaultSubobject<UMLAdapterComponent>(TEXT("MLAdapter"));
}

TMap<FName, FMLAdapterFloatArray> AMyMLCharacter::GetAgentState_Implementation()
{
    TMap<FName, FMLAdapterFloatArray> StateMap;
    // 例如，将位置信息打包到状态中
    FVector Location = GetActorLocation();
    StateMap.Add(TEXT("Position"), FMLAdapterFloatArray({Location.X, Location.Y, Location.Z}));
    return StateMap;
}
```

## 模块依赖
从 Build.cs 分析，使用此插件需要依赖以下特有模块：

| 模块 | 用途 |
|---|---|
| `RPCLib` | 提供底层的远程过程调用通信能力，是 MLAdapter 与外部进程通信的基石 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，无功能变化。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次提交中错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的某次更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复了引擎初始化委托的注册问题。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了打印格式说明符的小问题。 |

### 维护评价
- **创建时间**：2021 年，属于较新的插件。
- **维护频率**：最近更新集中在 2026 年初，主要为维护性更新（API 迁移、错误修复）。在创建后的几年间应有持续更新以适配引擎版本。
- **活跃度**：插件状态为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明它仍处于实验性阶段，未被官方推荐广泛用于生产环境。功能基本稳定，但API可能仍有变化。
- **推荐**：适合希望在虚幻引擎中进行机器学习研究和实验的开发者。由于其通信架构设计，它可以无缝集成标准的Python ML训练流程（如使用 Stable Baselines3）。在生产环境中使用前需充分测试其稳定性和性能。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter)
- 官方文档链接未提供。
- 测试用例：`Engine/Plugins/AI/MLAdapter/Source/MLAdapterTestSuite/` (位于 `MLAdapterTestSuite` 模块内)