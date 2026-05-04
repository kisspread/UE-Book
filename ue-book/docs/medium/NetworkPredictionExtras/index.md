# Network Prediction Extras

> Non essential classes for Network Prediction. Samples, test maps, etc intended to help developers start using the system. Not intended to be used directly in a shipping product.

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试地图、示例 Pawn/Character 蓝图） |
| 模块 | `NetworkPredictionExtras` (Runtime), `NetworkPredictionExtrasLatentLoad` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-27 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/NetworkPredictionExtras) | |

## 用途

NetworkPredictionExtras 是 UE5 **Network Prediction** 插件的配套示例和工具集。它不提供生产级代码，而是提供一系列**可参考的实现模式**，帮助开发者理解如何将自己的游戏系统接入 Network Prediction 框架。

插件的核心价值在于展示了以下 Network Prediction 的关键概念：

- **三种基本运动模拟**：Flying Movement（飞行）、Character Movement（角色行走+跳跃）、Parametric Movement（参数化运动）
- **模拟继承**：在基础运动之上叠加能力系统（Sprint/Dash/Blink）
- **物理集成**：NP 模拟与 Chaos 物理引擎的协作方式
- **Root Motion 原型**：网络预测的 Root Motion 系统雏形
- **NetSimCues**：从模拟中发出可预测/可回滚的事件（特效、音效等）
- **Mock 示例**：最简化的"Hello World"级别 NP 用法演示

## 使用场景

- **学习 Network Prediction 框架**：你刚接触 UE5 的 Network Prediction，需要看完整示例理解 InputCmd/SyncState/AuxState 三件套 → 打开这个插件，从 MockNetworkSimulation 开始
- **构建自定义网络同步运动**：你需要一个比 CharacterMovementComponent 更灵活的网络同步移动方案 → 参考 FlyingMovementComponent 或 CharacterMotionComponent
- **实现能力系统与移动的集成**：你想在网络游戏中实现 Sprint/Dash/Blink 等能力，并且需要客户端预测 → 参考 MockAbilitySimulation 的继承模式
- **测试 Network Prediction 功能**：你需要一个测试环境验证 NP 的预测/回滚/校正行为 → 使用插件自带的 TestMap 和 Pawn 类

## 蓝图用法

### 示例 Pawn 类

插件提供了多个可直接使用的 Pawn 类，可以放入测试地图中：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ANetworkPredictionExtrasFlyingPawn` | 使用 FlyingMovementComponent 的示例 Pawn | `ANetworkPredictionExtrasFlyingPawn` |
| `ANetworkPredictionExtrasFlyingPawn_MockAbility` | 带能力系统（Sprint/Dash/Blink）的飞行 Pawn | `ANetworkPredictionExtrasFlyingPawn_MockAbility` |
| `ANetworkPredictionExtrasCharacter` | 使用 CharacterMotionComponent 的示例角色 | `ANetworkPredictionExtrasCharacter` |
| `ANetworkPredictionExtrasCharacter_MockAbility` | 带能力系统（Sprint/Dash/Blink/Jump）的角色 | `ANetworkPredictionExtrasCharacter_MockAbility` |

### 运动组件（Blueprint Spawnable）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UFlyingMovementComponent` | 网络预测的飞行移动组件 | `UFlyingMovementComponent` |
| `UCharacterMotionComponent` | 网络预测的角色行走移动组件 | `UCharacterMotionComponent` |
| `UParametricMovementComponent` | 参数化运动组件（时间→变换） | `UParametricMovementComponent` |
| `UMockPhysicsComponent` | 物理模拟示例组件 | `UMockPhysicsComponent` |
| `UMockPhysicsGrenadeComponent` | 手榴弹物理示例组件 | `UMockPhysicsGrenadeComponent` |
| `UMockRootMotionComponent` | Root Motion 原型组件 | `UMockRootMotionComponent` |
| `UMockNetworkSimulationComponent` | 最简 NP 示例组件（累加器） | `UMockNetworkSimulationComponent` |

### 运动参数控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMaxMoveSpeed` | 获取最大移动速度 | `ANetworkPredictionExtrasFlyingPawn` / `ANetworkPredictionExtrasCharacter` |
| `SetMaxMoveSpeed` | 设置最大移动速度 | 同上 |
| `AddMaxMoveSpeed` | 叠加最大移动速度 | 同上 |

### 能力系统查询（BlueprintCallable）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsSprinting` | 是否正在冲刺 | `UMockFlyingAbilityComponent` / `UMockCharacterAbilityComponent` |
| `IsDashing` | 是否正在冲刺突进 | 同上 |
| `IsBlinking` | 是否正在闪现准备 | 同上 |
| `IsJumping` | 是否正在跳跃 | `UMockCharacterAbilityComponent` |
| `GetStamina` | 获取当前耐力值 | `UMockFlyingAbilityComponent` / `UMockCharacterAbilityComponent` |
| `GetMaxStamina` | 获取最大耐力值 | 同上 |
| `GetBlinkWarmupTimeSeconds` | 获取闪现准备时间（秒） | 同上 |

### 能力状态变化事件（BlueprintAssignable）

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnSprintStateChange` | 冲刺状态变化通知 | `UMockFlyingAbilityComponent` / `UMockCharacterAbilityComponent` |
| `OnDashStateChange` | 突进状态变化通知 | 同上 |
| `OnBlinkStateChange` | 闪现状态变化通知 | 同上 |
| `OnJumpStateChange` | 跳跃状态变化通知 | `UMockCharacterAbilityComponent` |
| `OnBlinkActivateEvent` | 闪现激活事件（含目标位置） | 同上 |
| `OnBlinkActivateEventRollback` | 闪现回滚事件 | 同上 |

### 物理模拟事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnJumpActivatedEvent` | 跳跃 Cue 事件（物理版本） | `UMockPhysicsComponent` |
| `OnChargeActivatedEvent` | 蓄力 Cue 事件 | `UMockPhysicsComponent` |
| `OnChargeStateChange` | 蓄力状态变化通知 | `UMockPhysicsComponent` |
| `OnExplode` | 手榴弹爆炸事件 | `UMockPhysicsGrenadeComponent` |

### Root Motion

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateRootMotionSource` | 创建 Root Motion 源 | `UMockRootMotionComponent` |
| `Input_PlayRootMotionSource` | 通过 Input 预测性播放 Root Motion | `UMockRootMotionComponent` |
| `Input_PlayRootMotionSourceByClass` | 通过类预测性播放 Root Motion | `UMockRootMotionComponent` |
| `PlayRootMotionSource` | 权威端直接播放 Root Motion（OOB） | `UMockRootMotionComponent` |
| `PlayRootMotionSourceByClass` | 权威端通过类播放 Root Motion（OOB） | `UMockRootMotionComponent` |

### Root Motion 源类型

| 类 | 说明 |
|---|---|
| `UMockRootMotionSource_Montage` | 基于动画蒙太奇的 Root Motion 源（Blueprintable） |
| `UMockRootMotionSource_Curve` | 基于曲线的 Root Motion 源（Blueprintable） |
| `UMockRootMotionSource_MoveToLocation` | 移动到目标位置的 Root Motion 源（Blueprintable） |

### 使用示例（蓝图描述）

**快速测试飞行移动：**
1. 创建新关卡或加载 `NetworkPredictionExtras/Content/TestMap.umap`
2. 将 GameMode 设置为 `ANetworkPredictionExtrasGameMode`
3. 将默认 Pawn 设置为 `ANetworkPredictionExtrasFlyingPawn`
4. 运行游戏，使用 WASD + 鼠标控制飞行移动
5. 控制台输入 `nms.Debug.LocallyControlledPawn 1` 查看调试 HUD

**测试能力系统：**
1. 将默认 Pawn 设置为 `ANetworkPredictionExtrasFlyingPawn_MockAbility`
2. 绑定 Sprint/Dash/Blink 输入事件
3. 在蓝图中监听 `OnSprintStateChange` / `OnDashStateChange` / `OnBlinkStateChange` 事件

## C++ 用法

### Network Prediction 状态三件套

Network Prediction 的核心设计模式是定义三种状态结构体：

```cpp
// 1. InputCmd - 客户端每帧生成的输入
struct FCharacterMotionInputCmd
{
    FRotator RotationInput;
    FVector MovementInput;
    void NetSerialize(const FNetSerializeParams& P);
};

// 2. SyncState - 每帧进化并保持同步的状态
struct FCharacterMotionSyncState
{
    ECharacterMovementMode MovementMode;
    FVector Location;
    FVector Velocity;
    FRotator Rotation;
    bool ShouldReconcile(const FCharacterMotionSyncState& AuthorityState) const;
    void Interpolate(const FCharacterMotionSyncState* From, const FCharacterMotionSyncState* To, float PCT);
};

// 3. AuxState - 不频繁变化的辅助参数
struct FCharacterMotionAuxState
{
    float MaxSpeed = 1200.f;
    float Acceleration = 4000.f;
    float Deceleration = 8000.f;
    // ...
};
```

用 `TNetworkPredictionStateTypes` 将它们绑定为类型包：
```cpp
using CharacterMotionStateTypes = TNetworkPredictionStateTypes<
    FCharacterMotionInputCmd, 
    FCharacterMotionSyncState, 
    FCharacterMotionAuxState>;
```

### 模拟类实现

模拟类是纯粹的 C++ 类（不继承 UObject），包含核心的 `SimulationTick` 方法：

```cpp
// 来源: CharacterMotionSimulation.h
class FCharacterMotionSimulation : public FBaseMovementSimulation
{
public:
    // 核心更新函数 - 每个模拟 tick 调用
    void SimulationTick(
        const FNetSimTimeStep& TimeStep, 
        const TNetSimInput<CharacterMotionStateTypes>& Input, 
        const TNetSimOutput<CharacterMotionStateTypes>& Output);

protected:
    // 可重写的子功能
    virtual void PerformMovement(float DeltaSeconds, ...);
    virtual void Movement_Walking(float DeltaSeconds, ...);
    virtual void Movement_Falling(float DeltaSeconds, ...);
    virtual FVector ComputeVelocity(float DeltaSeconds, const FVector& InitialVelocity, ...);
    virtual void FindFloor(...);
};
```

### 驱动组件

驱动组件继承 `UNetworkPredictionComponent`，负责桥接 UE 组件系统和模拟类：

```cpp
// 来源: CharacterMotionComponent.h
UCLASS(BlueprintType, meta = (BlueprintSpawnableComponent))
class UCharacterMotionComponent : public UBaseMovementComponent
{
    // 输入委托 - 绑定到 Actor 以产生输入
    FProduceCharacterInput ProduceInputDelegate;

    // NP Driver 回调
    void ProduceInput(const int32 DeltaTimeMS, FCharacterMotionInputCmd* Cmd);
    void RestoreFrame(const FCharacterMotionSyncState* SyncState, const FCharacterMotionAuxState* AuxState);
    void FinalizeFrame(const FCharacterMotionSyncState* SyncState, const FCharacterMotionAuxState* AuxState);
    void InitializeSimulationState(FCharacterMotionSyncState* Sync, FCharacterMotionAuxState* Aux);
};
```

### 模拟继承（能力叠加）

MockAbility 演示了如何在基础运动上叠加能力系统——通过继承状态结构体和模拟类：

```cpp
// 来源: MockAbilitySimulation.h
// 1. 继承 InputCmd，增加能力输入
struct FMockAbilityInputCmd : public FFlyingMovementInputCmd
{
    bool bSprintPressed = false;
    bool bDashPressed = false;
    bool bBlinkPressed = false;
};

// 2. 继承 SyncState，增加能力状态
struct FMockAbilitySyncState : public FFlyingMovementSyncState
{
    float Stamina = 0.f;
};

// 3. 继承 AuxState，增加能力参数
struct FMockAbilityAuxState : public FFlyingMovementAuxState
{
    float MaxStamina = 100.f;
    float StaminaRegenRate = 20.f;
    int16 DashTimeLeft = 0;
    bool bIsSprinting = false;
};

// 4. 继承模拟类
class FMockAbilitySimulation : public FFlyingMovementSimulation
{
    void SimulationTick(const FNetSimTimeStep& TimeStep, 
        const TNetSimInput<TMockAbilityBufferTypes>& Input, 
        const TNetSimOutput<TMockAbilityBufferTypes>& Output);
};
```

### NetSimCues（网络模拟事件）

NetSimCues 是从模拟中发出的事件，支持预测和回滚：

```cpp
// 来源: MockPhysicsSimulation.h
// 定义 Cue 结构
struct FMockPhysicsJumpCue
{
    NETSIMCUE_BODY();
    using Traits = NetSimCueTraits::ReplicatedXOrPredicted;
    
    FVector_NetQuantize100 Start;
    void NetSerialize(FArchive& Ar);
    bool NetIdentical(const FMockPhysicsJumpCue& Other) const;
};

// 注册 Cue 集合
struct FMockPhysicsCueSet
{
    template<typename TDispatchTable>
    static void RegisterNetSimCueTypes(TDispatchTable& DispatchTable)
    {
        DispatchTable.template RegisterType<FMockPhysicsJumpCue>();
        DispatchTable.template RegisterType<FMockPhysicsChargeCue>();
    }
};

// 在组件中处理 Cue
void UMockPhysicsComponent::HandleCue(
    const FMockPhysicsJumpCue& JumpCue, 
    const FNetSimCueSystemParamemters& SystemParameters);
```

**Cue Traits 类型：**
- `NetSimCueTraits::Weak` - 弱：可能丢失
- `NetSimCueTraits::Strong` - 强：保证播放，有回滚支持
- `NetSimCueTraits::ReplicatedNonPredicted` - 仅复制，不预测
- `NetSimCueTraits::ReplicatedXOrPredicted` - 复制或预测（互斥）

### 物理集成

MockPhysicsSimulation 展示了 NP 与 Chaos 物理的集成方式——注意 SyncState 使用 `void`：

```cpp
// 来源: MockPhysicsSimulation.h
// SyncState 为 void 表示物理引擎自己管理位置同步
using MockPhysicsStateTypes = TNetworkPredictionStateTypes<
    FMockPhysicsInputCmd, 
    void,  // 无 SyncState！物理体自己管理状态
    FMockPhysicsAuxState>;
```

### Root Motion 原型

Root Motion 系统使用 UObject 派生的 Source 对象：

```cpp
// 来源: MockRootMotionSourceObject.h
UCLASS(Blueprintable)
class UMockRootMotionSource_Montage : public UMockRootMotionSource
{
    UPROPERTY(EditAnywhere, Category=RootMotion)
    TObjectPtr<UAnimMontage> Montage;

    UPROPERTY(EditAnywhere, Category=RootMotion)
    float PlayRate = 1.f;

    virtual FMockRootMotionReturnValue Step(const FMockRootMotionStepParameters& Parameters) override;
    virtual void FinalizePose(int32 ElapsedMS, UAnimInstance* AnimInstance) const override;
};
```

## Demo 示例

### 最小 NP 示例：MockNetworkSimulation

最简化的 Network Prediction 示例——一个累加器，接收随机输入并累加：

**状态定义** (`MockNetworkSimulation.h`)：
```cpp
struct FMockInputCmd {
    float InputValue = 0;
    void NetSerialize(const FNetSerializeParams& P);
};

struct FMockSyncState {
    float Total = 0;
    bool ShouldReconcile(const FMockSyncState& AuthorityState) const;
    void Interpolate(const FMockSyncState* From, const FMockSyncState* To, float PCT);
};

struct FMockAuxState {
    float Multiplier = 1;
};

using TMockNetworkSimulationBufferTypes = TNetworkPredictionStateTypes<
    FMockInputCmd, FMockSyncState, FMockAuxState>;
```

**模拟类**：
```cpp
class FMockNetworkSimulation
{
public:
    void SimulationTick(
        const FNetSimTimeStep& TimeStep, 
        const TNetSimInput<TMockNetworkSimulationBufferTypes>& Input, 
        const TNetSimOutput<TMockNetworkSimulationBufferTypes>& Output);
};
```

**组件驱动**：
```cpp
UCLASS(BlueprintType, meta=(BlueprintSpawnableComponent))
class UMockNetworkSimulationComponent : public UNetworkPredictionComponent
{
    virtual void InitializeNetworkPredictionProxy() override;
    void InitializeSimulationState(FMockSyncState* Sync, FMockAuxState* Aux);
    void ProduceInput(const int32 DeltaTimeMS, FMockInputCmd* Cmd);
    void FinalizeFrame(const FMockSyncState* Sync, const FMockAuxState* Aux);
    
    // NetSimCue 处理
    void HandleCue(const FMockCue& MockCue, const FNetSimCueSystemParamemters& SystemParameters);
};
```

**使用方式**：将 `UMockNetworkSimulationComponent` 添加到任何 `ROLE_AutonomousProxy` 的 Actor 上。控制台命令：
- `mns.DoLocalInput 1` - 提交随机输入
- `mns.RequestMispredict 1` - 强制预测错误（测试校正流程）
- `mns.Spawn` - 在所有 Pawn 上动态生成组件

### Build.cs 依赖

```csharp
// NetworkPredictionExtras.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "NetworkPrediction",  // 核心 NP 框架
    "Core",
    "CoreUObject",
    "Engine",
    "RenderCore",
    "InputCore",
    "PhysicsCore",
    "Chaos",              // 物理引擎
});

PrivateDependencyModuleNames.AddRange(new string[] {
    "NetCore",
    "TraceLog",
});

// 编辑器专属
if (Target.Type == TargetType.Editor) {
    PrivateDependencyModuleNames.Add("UnrealEd");
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NetworkPrediction` | Network Prediction 核心框架（必须） |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `RenderCore` | 渲染核心 |
| `InputCore` | 输入系统 |
| `PhysicsCore` | 物理核心接口 |
| `Chaos` | Chaos 物理引擎 |
| `NetCore` | 网络核心（私有依赖） |
| `TraceLog` | 追踪日志（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-03-06 | `d6a12ef6` | Making UClass::ClassDefaultObject private | 引擎级 API 重构，插件被动适配 |
| 2025-03-04 | `3ee47591` | [Backout] - CL40449780 | 回退后重新提交同一改动 |
| 2025-01-27 | `22599ad7` | Change to updated FBodyInstance ActorHandle API | 物理 API 适配 |

### 维护评价

- **创建时间**：2019 年 7 月，已存在约 7 年
- **更新频率**：最近的更新（2025-03）都是**被动适配引擎 API 变更**，而非功能性更新
- **维护状态**：**维护不活跃** — 插件本身已基本定型，近期无实质性功能迭代
- **实验性标记**：`.uplugin` 中 `IsBetaVersion: true`，且 `EnabledByDefault: false`
- **版本号**：`0.1`，从未正式发布

**⚠️ 重要警告**：
- 此插件的代码是**示例和原型**，Epic 官方明确声明"Not intended to be used directly in a shipping product"
- Root Motion 系统是原型设计，代码注释明确表示"We do not expect the code here in NetworkPredictionExtras to be used directly in shipping systems"
- NetworkPredictionExtrasLatentLoad 模块仅用于压力测试 NP 的类型系统，不包含功能代码

**推荐**：作为**学习资源**非常有价值，但不要直接在生产项目中使用。应该参考其模式后在自己的项目中重新实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/NetworkPredictionExtras)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [Network Prediction 核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/NetworkPrediction)

## 架构总览

```
NetworkPredictionExtras
├── 基础层 (Base Movement)
│   ├── FBaseMovementSimulation          ← 移动模拟基类（碰撞检测、穿透解决）
│   ├── UBaseMovementComponent           ← 移动组件基类（UpdatedComponent 管理）
│   ├── FSpring                          ← 弹簧物理结构体
│   └── FSimpleParametricMotion          ← 参数化运动定义
│
├── 飞行移动 (Flying Movement)
│   ├── FFlyingMovementSimulation        ← 飞行移动模拟
│   ├── UFlyingMovementComponent         ← 飞行移动组件
│   └── ANetworkPredictionExtrasFlyingPawn ← 示例飞行 Pawn
│
├── 角色移动 (Character Motion)
│   ├── FCharacterMotionSimulation       ← 角色移动模拟（Walk/Fall/Gravity/FindFloor）
│   ├── UCharacterMotionComponent        ← 角色移动组件
│   └── ANetworkPredictionExtrasCharacter ← 示例角色 Pawn
│
├── 参数化移动 (Parametric Movement)
│   ├── FParametricMovementSimulation    ← 参数化移动模拟
│   └── UParametricMovementComponent     ← 参数化移动组件
│
├── Mock 能力系统 (Mock Abilities)
│   ├── FMockAbilitySimulation           ← 飞行版能力模拟（继承 FlyingMovement）
│   ├── UMockFlyingAbilityComponent      ← 飞行能力组件
│   ├── FMockCharacterAbilitySimulation  ← 角色版能力模拟（继承 CharacterMotion）
│   ├── UMockCharacterAbilityComponent   ← 角色能力组件
│   └── ANetworkPredictionExtrasFlyingPawn_MockAbility / _Character_MockAbility
│
├── Mock 物理模拟 (Mock Physics)
│   ├── FMockPhysicsSimulation           ← 物理模拟（NP + Chaos 集成示例）
│   ├── UMockPhysicsComponent            ← 物理模拟组件
│   ├── UMockPhysicsGrenadeComponent     ← 手榴弹物理组件
│   └── FSpring                          ← 弹簧定义
│
├── Mock Root Motion (原型)
│   ├── FMockRootMotionSimulation        ← Root Motion 模拟
│   ├── UMockRootMotionComponent         ← Root Motion 组件
│   ├── UMockRootMotionSource            ← Root Motion 源基类
│   ├── UMockRootMotionSource_Montage    ← 蒙太奇 Root Motion
│   ├── UMockRootMotionSource_Curve      ← 曲线 Root Motion
│   └── UMockRootMotionSource_MoveToLocation ← 目标位置 Root Motion
│
├── Mock 网络模拟 (最简示例)
│   ├── FMockNetworkSimulation           ← 累加器模拟
│   └── UMockNetworkSimulationComponent  ← 示例组件
│
├── 框架支持
│   ├── ANetworkPredictionExtrasGameMode ← 允许作弊的 GameMode
│   ├── ANetworkPredictionExtrasGameState ← 自动启用 np2.DevMenu 的 GameState
│   └── INetworkPredictionExtrasModule   ← 模块接口
│
└── 压力测试模块
    └── NetworkPredictionExtrasLatentLoad ← 动态加载/卸载测试用空模块
```
