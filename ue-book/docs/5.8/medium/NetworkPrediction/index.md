# Network Prediction

> Generalized framework for writing network prediction friendly gameplay systems

| 属性 | 值 |
|---|---|
| 中文名 | 网络预测框架 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NetworkPrediction` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-27 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPrediction) | |

## 用途

NetworkPrediction 插件提供了一套**通用的网络预测框架**，用于编写对网络预测友好的游戏玩法系统。

它解决的核心问题是：在多人游戏中，客户端需要在本地预测游戏状态以获得流畅体验，同时又必须与服务端权威状态保持同步。当预测出错时，系统需要回滚并重新模拟（reconcile/rollback）。

该插件是一个**底层框架**，不提供现成的移动组件或战斗系统，而是提供：
- **状态管理**：Input（输入）、Sync（同步）、Aux（辅助）三类状态的缓冲与回滚
- **固定帧率/独立帧率**两种预测模式（Fixed Tick / Independent Tick）
- **网络序列化与复制代理**（Replication Proxy），处理客户端-服务端数据同步
- **Cue 事件系统**：网络感知的事件分发，支持回滚、重放、去重
- **插值/前向预测**等 NetworkLOD 级别控制

## 使用场景

- 你在编写自定义移动系统，需要客户端预测、服务端权威、回滚重模拟 → 使用此框架的 Fixed Tick 模式
- 你在实现一个需要网络同步的技能/战斗系统，要求输入在多个模拟帧内保持新鲜 → 使用 Independent Tick + `PollPerSimFrame` 输入策略
- 你需要网络感知的事件系统（如命中特效、爆炸通知），要求预测客户端和插值客户端行为不同 → 使用 NetSimCue 系统
- 你在实现服务端权威但需要极致客户端响应的游戏，需要自定义网络预测逻辑 → 使用此框架而非 UE 内置的 CharacterMovementComponent

## 蓝图用法

本插件**不包含任何蓝图可用的 API**。所有接口均为 C++ 模板类型，包括 `FNetworkPredictionProxy`、`FNetworkPredictionDriver<ModelDef>` 等。使用本插件需要完全在 C++ 层面工作。

## C++ 用法

### 头文件引入

```cpp
// 核心类型定义
#include "NetworkPredictionModelDef.h"
#include "NetworkPredictionStateTypes.h"
#include "NetworkPredictionDriver.h"
#include "NetworkPredictionSimulation.h"

// Proxy 初始化（仅在 .cpp 中 include）
#include "NetworkPredictionProxyInit.h"

// Cue 事件系统
#include "NetworkPredictionCues.h"
#include "NetworkPredictionCueTraits.h"

// 组件基类
#include "NetworkPredictionComponent.h"
```

### 基本用法

**1. 定义状态类型（Input/Sync/Aux）**

```cpp
// 来源: NetworkPredictionStateTypes.h
// 定义三种网络状态
struct FMyInputCmd
{
    float MoveForward;
    float MoveRight;
    
    void NetSerialize(FArchive& Ar) { Ar << MoveForward << MoveRight; }
    bool NetIdentical(const FMyInputCmd& Other) const
    {
        return MoveForward == Other.MoveForward && MoveRight == Other.MoveRight;
    }
};

struct FMySyncState
{
    FVector Location;
    FRotator Rotation;
    
    void NetSerialize(FArchive& Ar) { Ar << Location << Rotation; }
    bool NetIdentical(const FMySyncState& Other) const
    {
        return Location.Equals(Other.Location) && Rotation.Equals(Other.Rotation);
    }
    // 判断是否需要调和服务端状态
    bool ShouldReconcile(const FMySyncState& Authority) const
    {
        return !Location.Equals(Authority.Location, 1.0f);
    }
};

struct FMyAuxState
{
    // 辅助状态：不需要参与 reconcile 判断，但需要被预测和回滚
    float SomeVisualParam;
    void NetSerialize(FArchive& Ar) { Ar << SomeVisualParam; }
};
```

**2. 定义 ModelDef（模型定义）**

```cpp
// 来源: NetworkPredictionModelDef.h
// NP_MODEL_BODY() 声明静态 ID
struct FMyMovementDef : FNetworkPredictionModelDef
{
    NP_MODEL_BODY();
    
    using StateTypes = TNetworkPredictionStateTypes<FMyInputCmd, FMySyncState, FMyAuxState>;
    using Simulation = FMyMovementSimulation;  // 运行 SimulationTick 的对象类型
    using Driver = AMyPawn;                     // 接收预测输出的 Actor 类型
    
    static const TCHAR* GetName() { return TEXT("MyMovement"); }
    static constexpr int32 GetSortPriority()
    {
        return (int32)ENetworkPredictionSortPriority::KinematicMovers;
    }
};
// 在 .cpp 中注册
NP_MODEL_REGISTER(FMyMovementDef);
```

**3. 实现 Driver 接口**

```cpp
// 来源: NetworkPredictionDriver.h — FNetworkPredictionDriverBase 默认实现
// Driver 类需要实现以下成员函数：

class AMyPawn : public APawn
{
    // ...
public:
    // 初始化模拟状态（从当前 Actor 状态播种）
    void InitializeSimulationState(FMySyncState* Sync, FMyAuxState* Aux)
    {
        Sync->Location = GetActorLocation();
        Sync->Rotation = GetActorRotation();
        Aux->SomeVisualParam = 0.f;
    }
    
    // 采集本地输入（在每次模拟帧前调用）
    void ProduceInput(int32 DeltaTimeMS, FMyInputCmd* InputCmd)
    {
        InputCmd->MoveForward = InputComponent->GetAxisValue("MoveForward");
        InputCmd->MoveRight = InputComponent->GetAxisValue("MoveRight");
    }
    
    // 每引擎帧将预测结果推送到 Actor
    void FinalizeFrame(const FMySyncState* Sync, const FMyAuxState* Aux)
    {
        SetActorLocationAndRotation(Sync->Location, Sync->Rotation);
    }
    
    // 回滚前准备（同步碰撞体等）
    void RestoreFrame(const FMySyncState* Sync, const FMyAuxState* Aux)
    {
        SetActorLocationAndRotation(Sync->Location, Sync->Rotation);
    }
};
```

**4. 实现 Simulation（模拟逻辑）**

```cpp
// 来源: NetworkPredictionSimulation.h — TNetSimInput / TNetSimOutput
struct FMyMovementSimulation
{
    static void SimulationTick(
        const FNetSimTimeStep& TimeStep,
        TNetSimInput<FMyMovementDef::StateTypes> Input,
        TNetSimOutput<FMyMovementDef::StateTypes> Output)
    {
        const FMyInputCmd* Cmd = Input.Cmd;
        FMySyncState* Sync = Output.Sync;
        
        if (Cmd && Sync)
        {
            FVector Movement(Cmd->MoveRight, Cmd->MoveForward, 0.f);
            Movement.Normalize();
            Sync->Location += Movement * TimeStep.StepMS * 0.1f;
        }
    }
};
```

**5. 初始化 Proxy 并注册到系统**

```cpp
// 来源: NetworkPredictionProxyInit.h — FNetworkPredictionProxy::Init
// 在 Component 或 Actor 中：
void UMyNetworkComponent::InitializeNetworkPredictionProxy()
{
    NetworkPredictionProxy.Init<FMyMovementDef>(
        GetWorld(),
        GetReplicationProxies(),
        /*Simulation=*/ nullptr,
        /*Driver=*/ GetOwner<AMyPawn>()
    );
}
```

### 进阶用法

**定义 NetSimCue 网络事件**

```cpp
// 来源: NetworkPredictionCueTraits.h — NetSimCueTraits 预设
// 来源: NetworkPredictionCues.h — TNetSimCueDispatcher::Invoke

// 1. 定义 Cue 类型
struct FHitImpactCue
{
    FVector Location;
    float Damage;
    
    // 使用 Strong 特性：所有人可触发、支持重模拟、复制到所有人
    using Traits = NetSimCueTraits::Strong;
    
    void NetSerialize(FArchive& Ar) { Ar << Location << Damage; }
    bool NetIdentical(const FHitImpactCue& Other) const
    {
        return Location.Equals(Other.Location) && Damage == Other.Damage;
    }
};

// 2. 定义 Handler 类
class FMyCueHandler
{
public:
    void HandleCue(const FHitImpactCue& Cue, const FNetSimCueSystemParamemters& Params)
    {
        // Params.TimeSinceInvocation: 距离触发时刻的仿真时间
        // Params.Callbacks: 回滚回调（非权威端可用）
        SpawnImpactEffect(Cue.Location, Cue.Damage);
        
        if (Params.Callbacks)
        {
            Params.Callbacks->OnRollback.AddLambda([this]() {
                // 撤销效果（如移除粒子）
                UndoLastImpact();
            });
        }
    }
};

// 3. 在 SimulationTick 中触发
Output.CueDispatch.Invoke<FHitImpactCue>(HitLocation, CalculatedDamage);

// 4. 在 Driver 初始化时注册 Handler
CueDispatcher->template RegisterHandler<FMyCueHandler>(MyHandlerInstance);
```

**Cue 特性预设选择指南**

| 预设 | 使用场景 |
|---|---|
| `Weak`（默认） | 脚步声、撞击特效等纯表现性事件，最轻量 |
| `WeakOwningClientOnly` | 仅控制客户端需要的 HUD 通知 |
| `WeakClientsOnly` | 纯客户端表现，服务端不运行 |
| `AuthorityOnly` | 仅服务端执行，不复制 |
| `ReplicatedNonPredicted` | 关键事件，由服务端触发并复制，但不预测 |
| `ReplicatedXOrPredicted` | 所有人可见，前向预测时轻量（无 NetIdentical 测试） |
| `Strong` | 最健壮：所有人可触发、复制、回滚、重模拟，带宽/CPU 成本最高 |

**切换网络 LOD**

```cpp
// 来源: NetworkPredictionConfig.h
// 在运行时切换实例的 NetworkLOD（如远距离降级为插值）
FNetworkPredictionInstanceConfig Config;
Config.NetworkLOD = ENetworkLOD::Interpolated;  // 降级为插值模式
NetworkPredictionProxy.Configure(Config);
```

## Demo 示例

**最小可编译的网络预测 Actor 组件示例**

```cpp
// MyNetworkMovement.h
#pragma once
#include "Components/ActorComponent.h"
#include "NetworkPredictionComponent.h"
#include "NetworkPredictionModelDef.h"
#include "NetworkPredictionStateTypes.h"
#include "NetworkPredictionSimulation.h"

// --- 状态定义 ---
struct FSimpleInput
{
    FVector_NetQuantize10 Direction;
    void NetSerialize(FArchive& Ar) { Ar << Direction; }
    bool NetIdentical(const FSimpleInput& O) const { return Direction == O.Direction; }
};

struct FSimpleSync
{
    FVector_NetQuantize100 Position;
    void NetSerialize(FArchive& Ar) { Ar << Position; }
    bool NetIdentical(const FSimpleSync& O) const { return Position == O.Position; }
    bool ShouldReconcile(const FSimpleSync& Auth) const
    {
        return !Position.Equals(Auth.Position, 1.f);
    }
};

// --- ModelDef ---
struct FSimpleMoveDef : FNetworkPredictionModelDef
{
    NP_MODEL_BODY();
    using StateTypes = TNetworkPredictionStateTypes<FSimpleInput, FSimpleSync, void>;
    using Simulation = FSimpleMoveSimulation;
    using Driver = AActor;
    static const TCHAR* GetName() { return TEXT("SimpleMove"); }
    static constexpr int32 GetSortPriority()
    {
        return (int32)ENetworkPredictionSortPriority::KinematicMovers;
    }
};

// --- Simulation ---
struct FSimpleMoveSimulation
{
    static void SimulationTick(
        const FNetSimTimeStep& TimeStep,
        TNetSimInput<FSimpleMoveDef::StateTypes> In,
        TNetSimOutput<FSimpleMoveDef::StateTypes> Out)
    {
        if (In.Cmd && Out.Sync)
        {
            Out.Sync->Position += In.Cmd->Direction * TimeStep.StepMS * 0.05f;
        }
    }
};

// --- Component ---
UCLASS()
class UMyNetMovementComponent : public UNetworkPredictionComponent
{
    GENERATED_BODY()
protected:
    virtual void InitializeNetworkPredictionProxy() override;
};
```

```cpp
// MyNetworkMovement.cpp
#include "MyNetworkMovement.h"
#include "NetworkPredictionProxyInit.h"

// 注册 ModelDef
NP_MODEL_REGISTER(FSimpleMoveDef);

// Driver 特化
template<>
struct FNetworkPredictionDriver<FSimpleMoveDef> : FNetworkPredictionDriverBase<FSimpleMoveDef>
{
    static void InitializeSimulationState(AActor* Driver, FSimpleSync* Sync, void*)
    {
        Sync->Position = Driver->GetActorLocation();
    }
};

// 初始化 Proxy
void UMyNetMovementComponent::InitializeNetworkPredictionProxy()
{
    NetworkPredictionProxy.Init<FSimpleMoveDef>(
        GetWorld(),
        GetReplicationProxies(),
        /*Simulation=*/ nullptr,
        /*Driver=*/ GetOwner()
    );
}
```

## 模块依赖

本插件仅依赖 UE 标准模块，无特殊依赖。

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `1b629845` | Restoring Network Prediction functionality during replays | 修复回放模式下网络预测功能恢复 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复枚举格式化输出乱码 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符匹配问题 |
| 2026-04-20 | `93873b9e` | Prevent Network Prediction from running when playing back a replay since it would negatively affect | 回放时禁用网络预测以避免负面影响 |
| 2026-04-18 | `3cbae1a3` | Network Prediction Plugin: downgrading Iris-related warning to verbose until it can be debugged | 将 Iris 相关警告降级为 verbose |

### 维护评价

- **年龄**：约 7 年，属于 `🏛️ 文物` 级别插件
- **实验性状态**：`IsBetaVersion=true`，`EnabledByDefault=false`，从创建至今一直是实验性插件
- **活跃程度**：最近 1 个月内有多次提交（2026-04/05），但主要是 **bug 修复和编译问题修复**，没有功能更新
- **已知限制**：
  - 纯 C++ 框架，无蓝图支持
  - 模板代码极其复杂，学习曲线陡峭
  - 仍标记为 Beta，API 可能在未来版本发生变化
  - `VersionName: 0.1`，暗示从未达到 1.0 正式发布
- **推荐程度**：适合需要自定义网络预测逻辑的高级项目。如果你只是需要网络同步的角色移动，CharacterMovementComponent 仍是更成熟的选择。此框架更适合需要完全控制预测、回滚、插值行为的场景（如自定义载具系统、战斗预测系统等）。

⚠️ **警告**：该插件长期处于 Beta 状态（7 年），commit 历史显示近期更新以编译修复为主而非功能迭代。使用前请评估稳定性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPrediction)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）