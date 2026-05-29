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

MLAdapter 是 UE5 内置的 **强化学习/机器学习训练框架**，解决的核心问题是：**让外部 Python 训练脚本能通过 RPC 与游戏世界通信**。

具体来说，它实现了类似 OpenAI Gym 的模式：
1. **外部训练**：外部 Python 进程通过 RPC 获取游戏状态（observations），发送动作（actions）控制游戏内的角色，完成训练循环
2. **引擎内推理**：训练完成后，将 ONNX 模型加载到引擎中，让 AI Agent 完全在引擎内自主运行，无需外部连接

它不是一个"开箱即用的 AI"，而是一个 **基础设施层**，连接了游戏引擎和 ML 训练工具链（如 Stable Baselines、RLlib 等）。

## 使用场景

- 你在做游戏 AI，想用强化学习训练 NPC 行为 → 用 MLAdapter 搭建训练环境
- 你需要用 Python 脚本批量收集游戏状态数据用于离线学习 → 用 MLAdapter 的 RPC 接口
- 你已经训练好了 ONNX 模型，想直接在引擎内运行推理 → 用 `UMLAdapterAgent_Inference`
- 你只想在引擎内跑推理，不需要 RPC 通信 → 用 `UMLAdapterNoRPCManager`
- 你只做数据采集，不做训练 → 用 `UMLAdapterLocalDataCollectionSession`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Configure` | 使用配置对象设置 Agent 的头像、传感器和执行器 | `UMLAdapterAgent` |
| `SetAvatar` | 为 Agent 设置控制目标（Pawn/Controller） | `UMLAdapterAgent` |
| `EnableActionDuration` | 启用动作持续时间限制 | `UMLAdapterAgent` |
| `AddAgent` | 向 Session 添加一个新 Agent | `UMLAdapterSession` |
| `RemoveAgent` | 从 Session 移除指定 Agent | `UMLAdapterSession` |
| `EnableActionDuration` | 启用 Agent 的动作持续时间 | `UMLAdapterSession` |
| `SetManualWorldTickEnabled` | 设置世界由远程客户端手动推进 | `UMLAdapterSession` |
| `Open` / `Close` | 激活/关闭 Session | `UMLAdapterSession` |
| `StartServer` | 启动 RPC 服务器 | `UMLAdapterManager` |
| `StopServer` | 停止 RPC 服务器 | `UMLAdapterManager` |

### 使用示例（蓝图描述）

**场景一：纯引擎内推理（推荐入门方式）**

1. 在项目设置中将 `MLAdapter Settings → ManagerClass` 设为 `UMLAdapterNoRPCManager`
2. 创建 `UMLAdapterAgent_Inference` 的蓝图子类，设置 `ModelData` 为你的 ONNX 模型资产
3. 为 Agent 添加传感器（Camera、Movement 等）和执行器（EnhancedInput、Camera 等）
4. 运行游戏，Agent 会自动感知环境并执行动作

**场景二：外部 Python 训练**

1. 保持默认 `ManagerClass`（`UMLAdapterManager`）
2. 在 Python 端使用 rpclib 连接到默认端口 15151
3. 通过 RPC 调用 `request_observation` 获取状态、`send_action` 发送动作
4. 训练完成后导出 ONNX 模型，切换为推理模式

## C++ 用法

### 头文件引入

```cpp
#include "MLAdapterModule.h"
#include "Managers/MLAdapterManager.h"
#include "Sessions/MLAdapterSession.h"
#include "Agents/MLAdapterAgent.h"
#include "Agents/MLAdapterAgent_Inference.h"
```

### 基本用法

访问全局单例管理器并检查状态（来源：`Public/Managers/MLAdapterManager.h`）：

```cpp
// 检查管理器是否就绪
if (UMLAdapterManager::IsReady())
{
    UMLAdapterManager& Manager = UMLAdapterManager::Get();
    
    // 检查是否有活跃的 Session
    if (Manager.HasSession())
    {
        UMLAdapterSession& Session = Manager.GetSession();
        
        // 获取当前 Agent 数量
        int32 AgentCount = Session.GetAgentsCount();
    }
    
    // 手动启动 RPC 服务器（通常自动启动）
    Manager.StartServer(15151, EMLAdapterServerMode::AutoDetect, 4);
}
```

### 进阶用法

**创建自定义传感器**（来源：`Public/Sensors/MLAdapterSensor.h`）：

```cpp
UCLASS(Blueprintable)
class UMLAdapterSensor_Health : public UMLAdapterSensor
{
    GENERATED_BODY()
    
protected:
    virtual void Configure(const TMap<FName, FString>& Params) override
    {
        Super::Configure(Params);
    }
    
    // 定义观测空间形状
    virtual TSharedPtr<FMLAdapter::FSpace> ConstructSpaceDef() const override
    {
        // 返回一个 1 维连续空间（血量值）
        return MakeShareable(new FMLAdapter::FSpace_Box({ 1 }, 0.f, 1.f));
    }
    
    // 采集观测数据
    virtual void GetObservations(FMLAdapterMemoryWriter& Ar) override
    {
        float Health = 1.0f; // 从角色获取血量
        if (APawn* Pawn = GetPawnAvatar())
        {
            // 获取实际血量...
        }
        Ar << Health;
    }
    
    virtual void SenseImpl(const float DeltaTime) override
    {
        // 每帧更新内部状态
    }
};
```

**创建自定义执行器**（来源：`Public/Actuators/MLAdapterActuator.h`）：

```cpp
UCLASS(Blueprintable)
class UMLAdapterActuator_Movement : public UMLAdapterActuator
{
    GENERATED_BODY()
    
protected:
    virtual TSharedPtr<FMLAdapter::FSpace> ConstructSpaceDef() const override
    {
        // 2D 连续空间（X/Y 方向移动）
        return MakeShareable(new FMLAdapter::FSpace_Box({ 2 }, -1.f, 1.f));
    }
    
    virtual void DigestInputData(FMLAdapterMemoryReader& ValueStream) override
    {
        FScopeLock Lock(&ActionCS);
        ValueStream << MoveX;
        ValueStream << MoveY;
    }
    
    virtual void Act(const float DeltaTime) override
    {
        FScopeLock Lock(&ActionCS);
        if (APawn* Pawn = GetPawnAvatar())
        {
            FVector Direction(MoveX, MoveY, 0.f);
            Pawn->AddMovementInput(Direction.GetSafeNormal());
        }
    }
    
    float MoveX = 0.f;
    float MoveY = 0.f;
};
```

## Demo 示例

### 自定义推理 Agent

```cpp
// MyInferenceAgent.h
#pragma once
#include "Agents/MLAdapterAgent_Inference.h"
#include "MyInferenceAgent.generated.h"

UCLASS(Blueprintable)
class UMyInferenceAgent : public UMLAdapterAgent_Inference
{
    GENERATED_BODY()
public:
    // 构造函数中注册传感器和执行器
    UMyInferenceAgent(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());
};

// MyInferenceAgent.cpp
#include "MyInferenceAgent.h"
#include "Sensors/MLAdapterSensor_Movement.h"
#include "Sensors/MLAdapterSensor_Camera.h"
#include "Actuators/MLAdapterActuator_EnhancedInput.h"

UMyInferenceAgent::UMyInferenceAgent(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    // 可以在蓝图中配置，也可以在构造函数中添加默认组件
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RPCLib` | 第三方 RPC 库，用于与外部 Python 等进程通信 |
| `GameplayAbilities` | 插件依赖，用于属性传感器（Attribute）支持 |
| `EnhancedInput` | 插件依赖，用于增强输入传感器和执行器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前错误的查找替换后的第二轮修正 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的提交 CL51314860 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复委托访问方式，防止注册丢失 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复 printf 格式说明符错误 |

### 维护评价

MLAdapter 创建于 2021 年 4 月，由 UE4ML 更名而来（前身历史更久远）。标记为 **实验性**（IsExperimentalVersion=true）且 **默认不启用**（EnabledByDefault=false）。

近期（2026 年初）有少量维护性更新，主要是引擎全局 API 变更的适配（日志宏迁移、委托 API 变更），**不涉及功能改进或 bug 修复**。

**注意事项**：
- 该插件长期处于实验性状态，尚未正式发布
- 核心代码结构完整，但依赖的 RPCLib 是第三方库，可能存在兼容性风险
- 适合做原型验证和研究用途，不建议用于生产环境
- 如果只需要引擎内推理（不需要 RPC），可以用 `UMLAdapterNoRPCManager` 简化架构

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MLAdapter/Source/MLAdapterTestSuite)