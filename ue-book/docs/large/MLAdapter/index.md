# ML Adapter

> A framework for training and utilizing machine learning agents in games. Creates an RPC interface through which an external process can query game state and control in-game actors. Once trained, agents can be run in-engine via neural networks loaded from ONNX models.

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MLAdapter` (Runtime), `MLAdapterTestSuite` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-12 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MLAdapter) | |

## 用途

MLAdapter 是 UE5 的**机器学习代理框架**，解决的核心问题是：**如何在游戏引擎中训练和运行 ML 代理（Agent）**。

它的工作流程分为两个阶段：

1. **训练阶段**：通过 RPC（远程过程调用）接口，让外部 Python/C++ 训练脚本查询游戏状态（observations）、发送动作（actions）、获取奖励（rewards），实现类似 OpenAI Gym 的 `step` / `reset` 循环
2. **推理阶段**：将训练好的 ONNX 神经网络模型加载到引擎内，由 `UMLAdapterAgent_Inference` 直接在游戏线程中完成 Sense → Think → Act 循环，无需外部进程

插件的核心架构遵循经典的**感知-思考-行动**（Sense-Think-Act）模式：
- **Sensor**（传感器）：从游戏世界收集观测数据（位置、速度、图像、输入状态、AI 感知等）
- **Actuator**（执行器）：将 ML 模型的输出转化为游戏动作（按键注入、相机旋转、Enhanced Input 等）
- **Agent**（代理）：连接传感器和执行器，管理一个 Avatar（通常是 Pawn 或 Controller）
- **Session**（会话）：管理一组 Agent，负责 Avatar 分配和生命周期
- **Manager**（管理器）：全局单例，管理 RPC 服务器、会话和世界状态

**为什么存在这个插件？** UE5 有强大的 AI 系统（行为树、EQS 等），但那些是基于规则的。MLAdapter 为数据驱动的 ML 方法提供了原生集成，让游戏 AI 可以通过强化学习等技术从数据中学习行为策略。

**注意**：此插件标记为 `IsExperimentalVersion = true` 且 `EnabledByDefault = false`，需要手动启用。

## 使用场景

- **强化学习训练**：你正在用 Stable Baselines3 / RLlib 等框架训练游戏 AI → 用 MLAdapter 的 RPC 接口连接 Python 训练脚本和 UE5 游戏世界
- **ONNX 模型推理**：你已经训练好了一个 ONNX 模型，想在游戏内直接运行 → 用 `UMLAdapterAgent_Inference` 加载模型，无需外部进程
- **模仿学习数据采集**：你需要从人类玩家的操作中采集训练数据 → 用 `UMLAdapterLocalDataCollectionSession` 记录传感器数据到文件
- **多代理训练**：你需要同时训练多个 AI 代理 → MLAdapter 原生支持多 Agent，有 `batch_act` / `batch_get_observations` 等批量 RPC 函数
- **自定义传感器/执行器**：你需要观测游戏特定属性（如 GAS 属性集）→ 继承 `UMLAdapterSensor` / `UMLAdapterActuator` 创建自定义组件

## 蓝图用法

MLAdapter 的蓝图支持主要集中在**创建推理代理**和**本地数据采集**场景。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ModelData` (属性) | 引用 ONNX 神经网络资产 | `UMLAdapterAgent_Inference` |
| `Brain` (属性) | 加载后的神经网络实例 | `UMLAdapterAgent_Inference` |
| `TrackedActions` (属性) | 此传感器/执行器追踪的 InputAction 列表 | `UMLAdapterSensor_EnhancedInput` / `UMLAdapterActuator_EnhancedInput` |
| `FilePath` (属性) | 数据采集输出目录 | `UMLAdapterLocalDataCollectionSession` |
| `FileName` (属性) | 数据采集输出文件名 | `UMLAdapterLocalDataCollectionSession` |
| `bPrefixOutputFilenameWithTimestamp` (属性) | 是否用时间戳作为文件名前缀 | `UMLAdapterLocalDataCollectionSession` |
| `Width` / `Height` (属性) | 相机传感器的捕获分辨率 | `UMLAdapterSensor_Camera` |
| `Sensors` (属性) | Agent 的传感器列表（EditInlineNew） | `UMLAdapterAgent` |
| `Actuators` (属性) | Agent 的执行器列表（EditInlineNew） | `UMLAdapterAgent` |
| `bEnableActionDuration` (属性) | 是否启用动作持续时间限制 | `UMLAdapterAgent` |
| `ActionDurationSeconds` (属性) | 动作持续时间（秒） | `UMLAdapterAgent` |

### 使用示例（蓝图描述）

**创建一个 ONNX 推理代理（蓝图）**：

1. 创建 `UMLAdapterAgent_Inference` 的蓝图子类
2. 在蓝图的 `Sensors` 数组中添加所需的传感器（如 `MLAdapterSensor_Movement`、`MLAdapterSensor_Camera`）
3. 在 `Actuators` 数组中添加所需的执行器（如 `MLAdapterActuator_EnhancedInput`）
4. 设置 `ModelData` 属性指向你的 ONNX 模型资产（`UNNEModelData`）
5. 设置 `AvatarClass` 指定代理控制的 Actor 类型
6. 在 Project Settings → MLAdapter 中将 `DefaultAgentClass` 设置为你的蓝图类
7. 将 `ManagerClass` 设置为 `MLAdapterNoRPCManager`（纯推理模式，不启动 RPC 服务器）

**配置 Enhanced Input 传感器**：

1. 在 `UMLAdapterSensor_EnhancedInput` 蓝图实例的 `TrActions` 属性中添加要追踪的 `UInputAction` 资产
2. 传感器会自动绑定到 Avatar 的 `UEnhancedInputComponent`，实时记录输入状态
3. 输入数据以 float 数组形式输出，与 `TrackedActions` 数组一一对应

## C++ 用法

### 头文件引入

```cpp
#include "Agents/MLAdapterAgent.h"
#include "Agents/MLAdapterAgent_Inference.h"
#include "Sensors/MLAdapterSensor.h"
#include "Sensors/MLAdapterSensor_Movement.h"
#include "Sensors/MLAdapterSensor_Camera.h"
#include "Sensors/MLAdapterSensor_AIPerception.h"
#include "Actuators/MLAdapterActuator.h"
#include "Actuators/MLAdapterActuator_InputKey.h"
#include "Actuators/MLAdapterActuator_Camera.h"
#include "Actuators/MLAdapterActuator_EnhancedInput.h"
#include "Sessions/MLAdapterSession.h"
#include "Managers/MLAdapterManager.h"
#include "MLAdapterSettings.h"
```

### 基本用法：创建和配置 Agent

来自 `AgentTest.cpp` 和 `SessionTest.cpp` 的测试用例：

```cpp
// 获取 Manager 单例（引擎启动后自动创建）
UMLAdapterManager& Manager = UMLAdapterManager::Get();

// 获取或创建 Session
UMLAdapterSession& Session = Manager.GetSession();
Session.SetWorld(GetWorld());

// 用默认配置添加 Agent
FMLAdapter::FAgentID AgentID = Session.AddAgent();
UMLAdapterAgent* Agent = Session.GetAgent(AgentID);

// 设置 Avatar（Agent 将控制此 Actor）
Agent->SetAvatar(MyPawn);

// 或者用自定义配置添加 Agent
FMLAdapterAgentConfig Config;
Config.AvatarClassName = APawn::StaticClass()->GetFName();
Config.bAvatarClassExact = false;
Config.bAutoRequestNewAvatarUponClearingPrev = true;
FMLAdapter::FAgentID AgentID2 = Session.AddAgent(Config);
```

来源：`Source/MLAdapterTestSuite/Private/AgentTest.cpp`

### 基本用法：RPC 服务器

```cpp
// 启动 RPC 服务器（默认端口 15151）
uint16 Port = 15151;
Manager.StartServer(Port, EMLAdapterServerMode::Standalone, /*ServerThreads=*/1);

// 检查服务器是否运行
bool bRunning = Manager.IsRunning(); // true

// 停止服务器
Manager.StopServer();
```

来源：`Source/MLAdapterTestSuite/Private/RPCServerTest.cpp`

### 基本用法：手动世界 Tick

```cpp
// 启用手动 Tick 模式（外部客户端控制世界推进）
Manager.SetManualWorldTickEnabled(true);

// 请求 N 帧世界 Tick
// 通过 RPC: request_world_tick(TickCount, bWaitForWorldTick)
```

### 进阶用法：自定义 Sensor

```cpp
UCLASS(Blueprintable)
class UMLAdapterSensor_Health : public UMLAdapterSensor
{
    GENERATED_BODY()

public:
    virtual bool ConfigureForAgent(UMLAdapterAgent& Agent) override
    {
        // 验证 Avatar 有你需要的组件
        return Agent.GetAvatar() != nullptr;
    }

    virtual void Configure(const TMap<FName, FString>& Params) override
    {
        // 从参数映射中读取配置
        if (const FString* Threshold = Params.Find(TEXT("Threshold")))
        {
            AlertThreshold = FCString::Atof(**Threshold);
        }
    }

    virtual TSharedPtr<FMLAdapter::FSpace> ConstructSpaceDef() const override
    {
        // 定义观测空间：1 个连续值 [0, 1]
        return MakeShareable(new FMLAdapter::FSpace_Box({1}, 0.f, 1.f));
    }

protected:
    virtual void SenseImpl(const float DeltaTime) override
    {
        // 在这里更新观测数据
        AActor* Avatar = GetAvatar();
        if (Avatar)
        {
            // 收集你想要的数据
            CurrentHealth = /* ... */;
        }
    }

    virtual void GetObservations(FMLAdapterMemoryWriter& Ar) override
    {
        // 将观测数据写入流
        FScopeLock Lock(&ObservationCS);
        Ar << CurrentHealth;
    }

private:
    float CurrentHealth = 1.f;
    float AlertThreshold = 0.2f;
};
```

### 进阶用法：自定义 Actuator

```cpp
UCLASS(Blueprintable, EditInlineNew)
class UMLAdapterActuator_Move : public UMLAdapterActuator
{
    GENERATED_BODY()

public:
    virtual TSharedPtr<FMLAdapter::FSpace> ConstructSpaceDef() const override
    {
        // 动作空间：2D 连续向量 [-1, 1]
        return FMLAdapter::FSpace_Box::Vector2D();
    }

    virtual void DigestInputData(FMLAdapterMemoryReader& ValueStream) override
    {
        FScopeLock Lock(&ActionCS);
        ValueStream << MoveDirection.X;
        ValueStream << MoveDirection.Y;
    }

    virtual void Act(const float DeltaTime) override
    {
        FScopeLock Lock(&ActionCS);
        APawn* Pawn = GetPawnAvatar();
        if (Pawn)
        {
            Pawn->AddMovementInput(FVector(MoveDirection.X, MoveDirection.Y, 0.f));
        }
    }

private:
    FVector2D MoveDirection = FVector2D::ZeroVector;
};
```

### 进阶用法：本地数据采集

```cpp
// 使用 UMLAdapterLocalDataCollectionSession 录制人类玩家的传感器数据
// 配置 SessionClass 为 UMLAdapterLocalDataCollectionSession
// 在 Project Settings → MLAdapter 中设置 SessionClass

// 或者在代码中创建：
UMLAdapterLocalDataCollectionSession* DataSession = 
    NewObject<UMLAdapterLocalDataCollectionSession>();
DataSession->FilePath.Path = TEXT("D:/MLData");
DataSession->FileName = TEXT("training_data.bin");
DataSession->bPrefixOutputFilenameWithTimestamp = true;
Manager.SetSession(DataSession);
```

## Demo 示例

以下是一个完整的最小推理代理示例：创建一个使用移动传感器和键盘执行器的 ONNX 推理 Agent。

### Build.cs

```csharp
using UnrealBuildTool;

public class MyMLProject : ModuleRules
{
    public MyMLProject(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "MLAdapter",          // MLAdapter 模块
            "EnhancedInput",      // 如果使用 Enhanced Input
            "NNE"                 // 如果使用推理 Agent
        });
    }
}
```

### MyInferenceAgent.h

```cpp
#pragma once

#include "Agents/MLAdapterAgent_Inference.h"
#include "MyInferenceAgent.generated.h"

/**
 * 一个使用移动传感器和键盘执行器的推理代理。
 * 在 Project Settings → MLAdapter → DefaultAgentClass 中设置此类。
 */
UCLASS(Blueprintable)
class UMyInferenceAgent : public UMLAdapterAgent_Inference
{
    GENERATED_BODY()

public:
    UMyInferenceAgent(const FObjectInitializer& ObjectInitializer);

    // 在 PostInitProperties 中，父类会自动加载 ModelData 中的 ONNX 模型
    // 你需要确保 Sensors 和 Actuators 的空间维度与模型输入/输出匹配
};
```

### MyInferenceAgent.cpp

```cpp
#include "MyInferenceAgent.h"
#include "Sensors/MLAdapterSensor_Movement.h"
#include "Sensors/MLAdapterSensor_AIPerception.h"
#include "Actuators/MLAdapterActuator_InputKey.h"

UMyInferenceAgent::UMyInferenceAgent(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    // 注册传感器：移动信息（位置 + 速度）
    UMLAdapterSensor_Movement* MovementSensor = ObjectInitializer.CreateDefaultSubobject<UMLAdapterSensor_Movement>(this, TEXT("MovementSensor"));
    Sensors.Add(MovementSensor);

    // 注册执行器：键盘输入
    UMLAdapterActuator_InputKey* InputKeyActuator = ObjectInitializer.CreateDefaultSubobject<UMLAdapterActuator_InputKey>(this, TEXT("InputKeyActuator"));
    Actuators.Add(InputKeyActuator);

    // 设置 Avatar 类型
    AvatarClass = APawn::StaticClass();
}
```

### 配置步骤

1. 编译上述代码
2. 在 **Project Settings → Plugins → MLAdapter** 中：
   - `ManagerClass` → `MLAdapterNoRPCManager`（纯推理，不启动 RPC）
   - `SessionClass` → `MLAdapterSession`
   - `DefaultAgentClass` → `MyInferenceAgent`
3. 导入你的 ONNX 模型为 `UNNEModelData` 资产
4. 创建 `UMyInferenceAgent` 蓝图子类，在 `ModelData` 属性中引用 ONNX 资产
5. 运行游戏，Agent 会自动 Spawn 并开始 Sense → Think → Act 循环

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `EnhancedInput` | 增强输入系统（用于 `MLAdapterSensor_EnhancedInput` 和 `MLAdapterActuator_EnhancedInput`） |
| `GameplayTags` | Gameplay Tag 系统 |
| `AIModule` | AI 框架（Controller、AIController 等） |
| `InputCore` | 输入核心类型（FKey 等） |
| `Json` | JSON 解析 |
| `JsonUtilities` | JSON 序列化/反序列化工具 |
| `GameplayAbilities` | GAS 系统（用于 `MLAdapterSensor_Attribute`） |
| `NNE` | Neural Network Engine（ONNX 模型加载和推理） |
| `RPCLib` | RPC 通信库（仅 Win64/Mac/Linux，通过 `WITH_RPCLIB` 宏控制） |
| `DeveloperSettings` | 开发者设置（`UMLAdapterSettings`） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator | 静态分析警告修复，非功能性改动 |
| 2025-06-10 | `004ad9ae` | Replace some usages of FORCEINLINE with inline in ML modules | 代码规范化，将 `FORCEINLINE` 替换为 `inline`，影响编译行为 |
| 2025-05-21 | `f6bd3c8f` | fix msgpack-c not detecting byte order on Windows Arm64 | 平台兼容性修复，修复 ARM64 Windows 上 msgpack 字节序检测问题 |

### 维护评价

- **创建时间**：2021-04-12，约 5 年前
- **实验性状态**：标记为 `IsExperimentalVersion = true`，从未正式毕业为稳定版本
- **最近更新**：最近 3 次提交都是编译/平台修复，无功能性更新
- **活跃度**：维护不活跃。最近的功能性更新需要追溯到更早的提交。近期工作集中在编译警告修复和平台兼容性
- **已知限制**：
  - RPC 仅支持 Win64、Mac、Linux（其他平台 `WITH_RPCLIB=0`）
  - 推理 Agent 仅支持单张量输入/输出的 ONNX 模型
  - 相机传感器使用 `SceneCaptureComponent2D`，性能开销较大
  - `UMLAdapterAgent_Inference` 硬编码使用 `NNERuntimeORTCpu`（ONNX Runtime CPU）
- **推荐程度**：**谨慎使用**。适合原型开发和研究用途。生产环境需要自行验证稳定性和性能。作为实验性插件，API 可能在未来版本中发生变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MLAdapter)
- 官方文档（无，.uplugin 的 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MLAdapter/Source/MLAdapterTestSuite)

## 架构总览

```
UMLAdapterManager (全局单例, TickableGameObject)
├── FRPCServer (rpclib, 异步运行)
├── FMLAdapterLibrarian (类注册表)
└── UMLAdapterSession
    ├── UMLAdapterAgent × N
    │   ├── UMLAdapterSensor × N
    │   │   ├── UMLAdapterSensor_Camera
    │   │   ├── UMLAdapterSensor_Movement
    │   │   ├── UMLAdapterSensor_Input
    │   │   ├── UMLAdapterSensor_EnhancedInput
    │   │   ├── UMLAdapterSensor_Attribute
    │   │   └── UMLAdapterSensor_AIPerception
    │   └── UMLAdapterActuator × N
    │       ├── UMLAdapterActuator_Camera
    │       ├── UMLAdapterActuator_InputKey
    │       └── UMLAdapterActuator_EnhancedInput
    └── AwaitingAvatar (等待 Avatar 分配的 Agent 列表)
```

### 关键类说明

| 类 | 文件 | 说明 |
|---|---|---|
| `UMLAdapterManager` | `Managers/MLAdapterManager.h` | 全局单例。管理 RPC 服务器、Session 生命周期。自动在 `OnPostEngineInit` 时创建 |
| `UMLAdapterNoRPCManager` | `Managers/MLAdapterNoRPCManager.h` | 不启动 RPC 服务器的 Manager，用于纯推理场景 |
| `UMLAdapterSession` | `Sessions/MLAdapterSession.h` | Agent 容器。Tick 所有 Agent 的 Sense/Think/Act。管理 Avatar 分配 |
| `UMLAdapterLocalDataCollectionSession` | `Sessions/MLAdapterLocalDataCollectionSession.h` | 数据采集 Session，将传感器数据写入文件 |
| `UMLAdapterAgent` | `Agents/MLAdapterAgent.h` | 基础 Agent。持有 Sensors 和 Actuators，控制一个 Avatar |
| `UMLAdapterAgent_Inference` | `Agents/MLAdapterAgent_Inference.h` | 推理 Agent。加载 ONNX 模型，在 Think() 中执行推理 |
| `UMLAdapterSensor` | `Sensors/MLAdapterSensor.h` | 传感器基类。支持 TickPolicy（每帧/每N帧/每N秒/从不） |
| `UMLAdapterActuator` | `Actuators/MLAdapterActuator.h` | 执行器基类。DigestInputData() 接收数据，Act() 执行动作 |
| `UMLAdapterAgentElement` | `Agents/MLAdapterAgentElement.h` | Sensor 和 Actuator 的公共基类 |
| `FMLAdapterLibrarian` | `MLAdapterLibrarian.h` | 类注册表。发现所有 Sensor/Actuator/Agent 子类，支持按名称查找 |
| `UMLAdapterSettings` | `MLAdapterSettings.h` | 插件设置（Manager/Session/Agent 类、RPC 端口） |
| `FMLAdapterSpace` / 子类 | `MLAdapterSpace.h` | 空间描述（类似 OpenAI Gym spaces）：Discrete、MultiDiscrete、Box、Tuple |

### RPC 接口一览

**通用函数**（Client + Server 模式均可用）：

| RPC 函数 | 说明 |
|---|---|
| `ping()` | 检查 RPC 服务器是否存活 |
| `get_name()` | 获取环境名称 |
| `list_functions()` | 列出所有可用 RPC 函数 |
| `list_sensor_types()` | 列出所有传感器类型 |
| `list_actuator_types()` | 列出所有执行器类型 |
| `get_description(element_name)` | 获取元素描述 |
| `is_finished(agent_id)` | 检查 Agent 的 episode 是否结束 |
| `batch_is_finished(agent_ids)` | 批量检查 |
| `exit()` | 关闭 UE 引擎 |

**Client 函数**（远程客户端调用，控制 Agent）：

| RPC 函数 | 说明 |
|---|---|
| `add_agent()` | 添加默认 Agent，返回 AgentID |
| `create_agent(json_config)` | 用 JSON 配置创建 Agent |
| `configure_agent(agent_id, json_config)` | 配置已有 Agent |
| `get_agent_config(agent_id)` | 获取 Agent 配置（JSON） |
| `get_observations(agent_id)` | 获取传感器数据（float 数组） |
| `batch_get_observations(agent_ids)` | 批量获取传感器数据 |
| `act(agent_id, actions)` | 发送动作数据到执行器 |
| `batch_act(agent_ids, actions_list)` | 批量发送动作 |
| `get_reward(agent_id)` | 获取奖励值 |
| `batch_get_rewards(agent_ids)` | 批量获取奖励 |
| `desc_action_space(agent_id)` | 获取动作空间描述 |
| `desc_observation_space(agent_id)` | 获取观测空间描述 |
| `reset()` | 重置世界 |
| `disconnect(agent_id)` | 断开 Agent |
| `is_agent_ready(agent_id)` | 检查 Agent 是否就绪 |
| `is_ready()` | 检查 Session 是否就绪 |
| `get_recent_agent()` | 获取最近创建的 AgentID |

**Server 函数**（服务器端控制）：

| RPC 函数 | 说明 |
|---|---|
| `enable_manual_world_tick(bEnable)` | 启用/禁用手动世界 Tick |
| `request_world_tick(count, bWait)` | 请求 N 帧世界 Tick |
| `enable_action_duration(agent_id, bEnable, seconds)` | 启用动作持续时间 |
| `wait_for_action_duration(agent_id)` | 等待动作持续时间结束 |
| `close_session()` | 关闭当前 Session |

### 控制台命令

| 命令 | 说明 |
|---|---|
| `mladapter.session.stop` | 停止当前 Session |
| `mladapter.server.restart [port]` | 重启 RPC 服务器（可选新端口） |

### 空间类型（类似 OpenAI Gym）

| 类型 | 说明 | 示例 |
|---|---|---|
| `FSpace_Discrete` | 离散空间，N 个可选值 | 按键选择（WASD = 5 个选项） |
| `FSpace_MultiDiscrete` | 多维离散空间 | 多个独立的离散选择 |
| `FSpace_Box` | 连续空间，Shape + Low/High 范围 | 位置向量 [3] ∈ [-1, 1] |
| `FSpace_Tuple` | 子空间组合 | 复杂的混合空间 |

### 内部对象生命周期管理

MLAdapter 使用 `FMLAdapter::NewObject<T>()` 创建对象，通过设置 `EInternalObjectFlags::Async` 标记防止 GC 回收。这是因为 RPC 服务器在独立线程运行，需要跨线程访问这些对象。关闭 Session 时会清除该标记，允许 GC 回收。
