# Network Prediction

> Generalized framework for writing network prediction friendly gameplay systems

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NetworkPrediction` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-27 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/NetworkPrediction) | |

## 用途

Network Prediction（NP）是 Epic 提供的一个**通用网络预测框架**，用于编写支持客户端预测、服务器权威、状态回滚（Rollback）和插值（Interpolation）的游戏逻辑系统。

传统做法中，每个网络同步系统都需要自行处理输入预测、状态校正、回滚重模拟等逻辑，导致大量重复代码。NP 的目标是将这些通用逻辑抽象为一个可复用的框架，让开发者只需定义「状态类型」和「模拟逻辑」，系统自动处理网络同步、预测、回滚和插值等复杂工作。

**核心设计理念**：
- **ModelDef**（模型定义）：声明式地定义一个模拟系统包含哪些状态类型、模拟类和驱动类
- **Service 架构**：内部功能被拆分为独立的服务（Ticking、Rollback、Interpolate 等），根据实例的网络角色和配置自动订阅
- **双 Ticking 模式**：支持 Fixed Tick（确定性固定步长，支持物理回滚）和 Independent Tick（各自帧率）
- **Cues 系统**：提供网络同步、回滚感知的事件系统

**注意**：此插件标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，需要手动在项目设置中启用。API 可能在未来版本中发生变化。

## 使用场景

- 你在做一个多人射击游戏，需要客户端预测角色移动和射击 → 使用 NP 的 Fixed Tick + ForwardPredict + Rollback
- 你在做一个赛车游戏，需要确定性物理回滚 → 使用 NP 的 PhysicsState + Fixed Tick
- 你需要一个网络同步的 kinematic 物体（如电梯、平台），不需要客户端预测 → 使用 `FGenericKinematicActorDef` 或 Independent Tick + Interpolate
- 你需要自定义复杂的游戏系统（如技能系统、载具系统）并要求网络预测支持 → 定义自己的 ModelDef，让 NP 处理同步和回滚
- 你想为已有的模拟系统添加网络同步事件（如爆炸特效、命中反馈）→ 使用 NP 的 Cue 系统

## 蓝图用法

此插件**没有暴露任何 BlueprintCallable / BlueprintReadWrite 接口**。Network Prediction 是一个纯 C++ 框架，所有使用都通过 C++ 代码完成。

不过，以下两个组件可以作为蓝图中可添加的 ActorComponent 使用：
- `UNetworkPredictionComponent` — 抽象基类，需要 C++ 子类化
- `UNetworkPredictionPhysicsComponent` — 蓝图可生成组件（`BlueprintSpawnableComponent`），用于独立物理对象

## C++ 用法

### 核心概念

NP 的使用围绕以下核心概念展开：

**1. State Types（状态类型）** — 三种用户定义的结构体：
- **InputCmd**：客户端输入命令（如移动方向、按键状态）
- **SyncState**：需要网络同步的核心模拟状态（如位置、速度、生命值）
- **AuxState**：辅助同步状态，非每帧必需（如装备信息、buff 列表）

**2. ModelDef（模型定义）** — 声明一个模拟系统的组成：
```cpp
struct FMyModelDef : FNetworkPredictionModelDef
{
    NP_MODEL_BODY(); // 声明 static FModelDefId ID

    using StateTypes = TNetworkPredictionStateTypes<FMyInputCmd, FMySyncState, FMyAuxState>;
    using Simulation = FMySimulation;  // 执行模拟的对象
    using Driver = AMyPawn;            // UE 侧驱动对象（Actor/Component）
    using PhysicsState = void;         // 或 FNetworkPredictionPhysicsState

    static const TCHAR* GetName() { return TEXT("MyModel"); }
    static constexpr int32 GetSortPriority() { return (int32)ENetworkPredictionSortPriority::KinematicMovers; }
};
```

**3. Driver（驱动类）** — UE 侧对象，负责产生输入和处理输出：
- `ProduceInput(DeltaTimeMS, InputCmd*)` — 采集本地输入
- `InitializeSimulationState(SyncState*, AuxState*)` — 初始化模拟状态
- `FinalizeFrame(SyncState*, AuxState*)` — 将模拟结果应用到 Actor
- `RestoreFrame(SyncState*, AuxState*)` — 回滚前恢复状态

**4. FNetworkPredictionProxy** — 连接驱动对象和 NP 系统的代理

### 头文件引入

```cpp
#include "NetworkPredictionModelDef.h"        // ModelDef 基类
#include "NetworkPredictionDriver.h"           // Driver 模板
#include "NetworkPredictionProxy.h"            // Proxy
#include "NetworkPredictionProxyInit.h"        // Proxy::Init 模板实现（仅在 .cpp 中 include）
#include "NetworkPredictionComponent.h"        // ActorComponent 基类
#include "NetworkPredictionPhysicsComponent.h" // 物理组件
#include "NetworkPredictionCues.h"             // Cue 系统
```

### 基本用法：定义一个简单的移动模型

**步骤 1：定义状态类型**

```cpp
// 来源: 类似 NetworkPredictionGenericKinematicActor.h 的模式
struct FMyInputCmd
{
    FVector MoveDir;
    uint8 bJump : 1;

    // 可选：定义 ShouldReconcile 来决定是否需要回滚
    bool ShouldReconcile(const FMyInputCmd& Other) const { return false; } // 输入不需要 reconcile
};

struct FMySyncState
{
    FVector Location;
    FRotator Rotation;
    float Health;

    // 当预测状态与权威状态差异超过阈值时触发回滚
    bool ShouldReconcile(const FMySyncState& Authority) const
    {
        return !Location.Equals(Authority.Location, 1.0f)
            || !FMath::IsNearlyEqual(Health, Authority.Health, 0.01f);
    }
};
```

**步骤 2：定义 Simulation 类**

```cpp
struct FMySimulation
{
    // 每个模拟帧调用，输入当前状态，输出新状态
    // 来源: NetworkPredictionSimulation.h 中 TNetSimInput/TNetSimOutput 模式
    void SimulationTick(const TNetSimInput<FMyStateTypes>& Input, TNetSimOutput<FMyStateTypes>& Output)
    {
        FMySyncState* Sync = Output.Sync;

        // 应用输入到状态
        Sync->Location += Input.Cmd->MoveDir * 10.0f;

        if (Input.Cmd->bJump)
        {
            Sync->Location.Z += 10.0f;
        }
    }

    // 本地预测帧数（用于 Independent Tick 模式下限制预测深度）
    static constexpr int32 GetMaxSupportedSimFrames() { return 10; }
};
```

**步骤 3：定义 ModelDef**

```cpp
struct FMyMoveModelDef : FNetworkPredictionModelDef
{
    NP_MODEL_BODY();

    using StateTypes = TNetworkPredictionStateTypes<FMyInputCmd, FMySyncState, void>;
    using Simulation = FMySimulation;
    using Driver = AMyPawn;

    static const TCHAR* GetName() { return TEXT("MyMoveModel"); }
    static constexpr int32 GetSortPriority() { return (int32)ENetworkPredictionSortPriority::KinematicMovers; }
};
```

**步骤 4：实现 Driver 函数**

```cpp
// 在 AMyPawn 中实现 Driver 接口
void AMyPawn::ProduceInput(int32 DeltaTimeMS, FMyInputCmd* InputCmd)
{
    // 从 PlayerController 采集输入
    InputCmd->MoveDir = GetLastMovementInputVector();
    InputCmd->bJump = bWantsToJump;
}

void AMyPawn::InitializeSimulationState(FMySyncState* Sync, void* Aux)
{
    Sync->Location = GetActorLocation();
    Sync->Rotation = GetActorRotation();
    Sync->Health = CurrentHealth;
}

void AMyPawn::FinalizeFrame(const FMySyncState* Sync, const void* Aux)
{
    SetActorLocation(Sync->Location);
    SetActorRotation(Sync->Rotation);
    CurrentHealth = Sync->Health;
}
```

**步骤 5：通过 Component 连接到系统**

```cpp
// UMyNetworkComponent 继承 UNetworkPredictionComponent
void UMyNetworkComponent::InitializeNetworkPredictionProxy()
{
    // 来源: NetworkPredictionComponent.h - InitializeNetworkPredictionProxy
    NetworkPredictionProxy.Init<FMyMoveModelDef>(
        GetWorld(),
        GetReplicationProxies(),
        nullptr,           // Simulation（由系统管理）
        GetOwner<AMyPawn>()  // Driver
    );
}
```

### 进阶用法：Physics State（物理回滚）

对于需要物理引擎参与的模拟，使用 `PhysicsState`：

```cpp
struct FMyPhysicsModelDef : FNetworkPredictionModelDef
{
    NP_MODEL_BODY();

    using StateTypes = TNetworkPredictionStateTypes<FMyInputCmd, FMySyncState, void>;
    using Simulation = FMyPhysicsSimulation;
    using Driver = AMyPawn;

    // 使用默认物理状态（同步 X, R, V, W）
    using PhysicsState = FNetworkPredictionPhysicsState;

    static const TCHAR* GetName() { return TEXT("MyPhysicsModel"); }
    // Physics 必须使用 Fixed Tick
};
```

Physics 模式下系统会自动：
- 记录物理状态用于回滚
- 在回滚时恢复物理组件状态（通过 `MarshalPhysicsToComponent`）
- 管理 Chaos 物理求解器的 rewind data

### 进阶用法：Cues（网络同步事件）

Cues 是模拟输出的瞬态事件，支持网络同步和回滚：

```cpp
// 定义 Cue 类型
struct FMyExplosionCue
{
    FVector Location;
    float Radius;

    // 注册时通过 NETSIM_CUE_TYPEID_TYPE 宏自动分配 ID
};

// 在 ModelDef 中声明 Cue Handler 类型
using CueHandler = FMyCueHandler;

// 在模拟中触发 Cue
void FMySimulation::SimulationTick(const TNetSimInput<...>& Input, TNetSimOutput<...>& Output)
{
    if (bExploded)
    {
        Output.CueDispatch.Invoke<FMyExplosionCue>(Location, Radius);
    }
}

// 实现 Handler
struct FMyCueHandler
{
    void HandleCue(const FMyExplosionCue& Cue, const FNetSimCueSystemParamemters& Params)
    {
        // 播放爆炸特效
        // Params.TimeSinceInvocation: 距触发的时间
        // Params.Callbacks->OnRollback: 回滚回调（如果支持）
    }
};
```

Cue 特性：
- **不可靠传输**：可能丢失，不要用于状态同步
- **回滚感知**：提供 `OnRollback` 回调用于撤销副作用
- **时间感知**：接收方知道距事件触发过了多久
- **不会在重模拟时重复播放**

## Demo 示例

### 最小可运行的 ModelDef

```cpp
// MyNetworkModel.h
#pragma once
#include "NetworkPredictionModelDef.h"
#include "NetworkPredictionSimulation.h"

// 状态定义
struct FSimpleInputCmd
{
    FVector Direction = FVector::ZeroVector;
};

struct FSimpleSyncState
{
    FVector Position = FVector::ZeroVector;

    bool ShouldReconcile(const FSimpleSyncState& Other) const
    {
        return !Position.Equals(Other.Position, 0.5f);
    }
};

using FSimpleStateTypes = TNetworkPredictionStateTypes<FSimpleInputCmd, FSimpleSyncState, void>;

// 模拟逻辑
struct FSimpleSimulation
{
    void SimulationTick(const TNetSimInput<FSimpleStateTypes>& Input,
                        TNetSimOutput<FSimpleStateTypes>& Output)
    {
        Output.Sync->Position = Input.Sync->Position + Input.Cmd->Direction * 5.0f;
    }

    static constexpr int32 GetMaxSupportedSimFrames() { return 10; }
};

// ModelDef
struct FSimpleModelDef : FNetworkPredictionModelDef
{
    NP_MODEL_BODY();
    using StateTypes = FSimpleStateTypes;
    using Simulation = FSimpleSimulation;
    using Driver = AActor;

    static const TCHAR* GetName() { return TEXT("SimpleModel"); }
    static constexpr int32 GetSortPriority() { return (int32)ENetworkPredictionSortPriority::KinematicMovers; }
};
```

```cpp
// MyNetworkModel.cpp
#include "MyNetworkModel.h"
#include "NetworkPredictionProxyInit.h"

// 注册 ModelDef（NP_MODEL_BODY 中的 ID 赋值）
FModelDefId FSimpleModelDef::ID = 0;

// 如果使用 Component 方式连接：
// 在你的 Component::InitializeNetworkPredictionProxy() 中调用
// NetworkPredictionProxy.Init<FSimpleModelDef>(GetWorld(), GetReplicationProxies(), nullptr, Driver);
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "NetworkPrediction",
    "Core",
    "CoreUObject",
    "Engine"
});
```

## 架构总览

### 服务（Services）架构

NP 内部将功能拆分为独立的服务，每个服务处理一类职责。实例根据网络角色和配置自动订阅所需的服务：

| 服务 | 说明 |
|---|---|
| `FixedTick` / `IndependentLocalTick` | 本地模拟帧推进 |
| `FixedRollback` / `IndependentRollback` | 检测分歧并回滚重模拟 |
| `FixedInterpolate` / `IndependentInterpolate` | 对 SimulatedProxy 进行状态插值 |
| `FixedInputLocal` / `IndependentLocalInput` | 采集本地输入 |
| `FixedInputRemote` | 服务器接收远程客户端输入 |
| `FixedFinalize` / `IndependentLocalFinalize` | 将模拟结果推送到驱动对象 |
| `FixedPhysics` | 物理引擎集成（Chaos 回滚） |
| `FixedSmoothing` | 平滑插值服务 |
| `ServerRPC` | 客户端→服务器的输入 RPC |

### Ticking 策略

| 策略 | 说明 | 适用场景 |
|---|---|---|
| `Fixed` | 所有端以相同固定帧率 tick | 需要确定性回滚、物理同步 |
| `Independent` | 各端以本地帧率 tick | 非确定性模拟、简单同步 |

### Network LOD

| LOD | 说明 |
|---|---|
| `Interpolated` | 插值模式，有内置延迟但永远正确 |
| `SimExtrapolate` | 外推模式（未实现，Hidden） |
| `ForwardPredict` | 前瞻预测，低延迟但可能需要回滚 |

## 模块依赖

从 `NetworkPrediction.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、数学库 |
| `CoreUObject` | UObject 系统、反射 |
| `NetCore` | 网络核心基础设施 |
| `Engine` | 引擎核心（World、Actor、Component） |
| `RenderCore` | 渲染核心 |
| `PhysicsCore` | 物理核心接口 |
| `Chaos` | Chaos 物理引擎（用于物理回滚） |
| `TraceLog` | 追踪日志（Insights 集成） |

## 维护状态

### 近期更新

- `ce3e3e5d8ec0` (2025-10-03): 回退了 Independent ticking 模式下 Interpolated SimProxy 的 input cmd 路由改动，原因是客户端→服务器→SimProxy 的延迟问题尚未解决
- `6025e7169d54` (2025-10-02): 尝试为 Independent ticking 模式下的 Interpolated SimProxy 路由 input cmd
- `2e995baebf56` (2025-09-23): 修复拼写错误（suppress misspellings）

### 维护评价

- **创建时间**：2019 年 7 月，已有约 7 年历史
- **维护状态**：**活跃维护中** — 2025 年 9-10 月仍有功能性更新
- **Beta 状态**：标记为 `IsBetaVersion=true`，API 可能变化
- **默认未启用**：`EnabledByDefault=false`，需手动启用
- **已知限制**：
  - `SimExtrapolate` LOD 尚未实现（代码中标记为 `// TODO`）
  - `IndependentSmoothingFinalize` 尚未实现
  - `FutureInputs` 和 `InputDecay` 等实验性功能状态不明
  - Independent Tick 下 Interpolated SimProxy 的 input cmd 路由存在延迟问题
- **推荐度**：如果你需要自定义网络预测逻辑且愿意接受 Beta 风险，这是一个强大的框架。对于简单的角色移动同步，Lyra 的 CMC 方案可能更稳定

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/NetworkPrediction)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）
- 测试用例：未在插件目录内找到独立测试文件；代码注释中引用了 `NetworkPredictionCueTests.cpp` 等测试，可能位于引擎内部测试目录
