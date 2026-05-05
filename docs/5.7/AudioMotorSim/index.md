# Audio Motor Sim

> Compositional method for simulating audio for vehicles.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioMotorSim` (Runtime), `AudioMotorSimStandardComponents` (Runtime), `AudioMotorSimDebug` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioMotorSim) | |

## 用途

AudioMotorSim 是一个**组合式车辆音频模拟框架**，用于根据车辆的物理状态（速度、油门、刹车、档位等）实时计算引擎音效参数（RPM、音量、音调）。

它解决的核心问题是：**如何用可组合的模块化方式，将车辆物理状态映射到音频输出参数**。传统的做法是把所有逻辑写在一个大函数里，而 AudioMotorSim 把不同的行为拆分成独立的"模拟组件"（`IAudioMotorSim`），每个组件负责一小块逻辑（如物理模拟、转速限制、增压效果等），通过链式执行组合起来。

这个插件最初为 Fortnite 的载具音频系统开发（从 CVar `Fort.VehicleAudio.DebugMotorModel` 可以看出），但设计上是通用的。

**注意**：这是一个实验性插件（`IsExperimentalVersion=true`），默认不启用（`EnabledByDefault=false`）。需要在项目的 `.uproject` 中手动启用。

## 使用场景

- 你在做一个赛车游戏，需要引擎声音随速度和档位自然变化 → 用 `MotorPhysicsSimComponent` + `AudioMotorModelComponent`
- 你需要自定义 RPM 曲线而非物理模拟 → 用 `RpmCurveMotorSimComponent` 替代 `MotorPhysicsSimComponent`
- 你的载具有氮气加速功能，需要音效配合 → 加入 `BoostMotorSimComponent`
- 你需要漂移时的断油回火效果 → 加入 `RevLimiterMotorSimComponent`
- 你想检测油门状态变化来触发涡轮泄压阀音效 → 用 `ThrottleStateMotorSimComponent` 的事件

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Update` | 每帧调用，传入输入上下文，驱动整个模拟链 | `UAudioMotorModelComponent` |
| `Reset` | 重置所有模拟组件状态 | `UAudioMotorModelComponent` |
| `StartOutput` | 启动音频输出组件 | `UAudioMotorModelComponent` |
| `StopOutput` | 停止音频输出组件 | `UAudioMotorModelComponent` |
| `AddMotorSimComponent` | 添加一个模拟组件到链中（可指定排序顺序） | `UAudioMotorModelComponent` |
| `RemoveMotorSimComponent` | 从链中移除一个模拟组件 | `UAudioMotorModelComponent` |
| `RemoveAllMotorSimComponents` | 移除所有模拟组件并停止输出 | `UAudioMotorModelComponent` |
| `AddMotorAudioComponent` | 添加音频输出组件 | `UAudioMotorModelComponent` |
| `RemoveMotorAudioComponent` | 移除音频输出组件 | `UAudioMotorModelComponent` |
| `ConfigureMotorSimComponents` | 批量配置模拟组件参数 | `UAudioMotorModelComponent` |
| `GetRpm` | 获取当前归一化 RPM [0-1] | `UAudioMotorModelComponent` |
| `GetGear` | 获取当前档位 | `UAudioMotorModelComponent` |
| `GetRuntimeInfo` | 获取完整运行时上下文 | `UAudioMotorModelComponent` |
| `SetEnabled` | 启用/禁用某个模拟组件 | `UAudioMotorSimComponent` |
| `OnUpdate` (蓝图事件) | 在蓝图子类中实现自定义模拟逻辑 | `UAudioMotorSimComponent` |
| `OnReset` (蓝图事件) | 在蓝图子类中实现自定义重置逻辑 | `UAudioMotorSimComponent` |

### 委托事件

| 事件 | 参数 | 所在类 |
|---|---|---|
| `OnGearChangedEvent` | `int32 NewGear` | `UMotorPhysicsSimComponent` |
| `OnUpShift` | `int32 NewGear` | `URpmCurveMotorSimComponent` |
| `OnDownShift` | `int32 NewGear` | `URpmCurveMotorSimComponent` |
| `OnRevLimiterHit` | 无 | `URevLimiterMotorSimComponent` |
| `OnRevLimiterStateChanged` | `bool bNewState` | `URevLimiterMotorSimComponent` |
| `OnThrottleEngaged` | 无 | `UThrottleStateMotorSimComponent` |
| `OnThrottleReleased` | 无 | `UThrottleStateMotorSimComponent` |
| `OnEngineBlowoff` | `float BlowoffStrength` | `UThrottleStateMotorSimComponent` |

### 使用示例（蓝图描述）

**基本设置**：
1. 在载具 Actor 上添加 `UAudioMotorModelComponent`
2. 添加子组件 `UMotorPhysicsSimComponent`（物理驱动 RPM）+ `UBoostMotorSimComponent`（氮气加速）
3. 每 Tick 调用 `UAudioMotorModelComponent::Update`，传入填好的 `FAudioMotorSimInputContext`
4. 调用 `StartOutput` 开始音频输出

**自定义蓝图模拟组件**：
1. 创建 `UAudioMotorSimComponent` 的蓝图子类
2. 实现 `OnUpdate` 事件，使用 "Set Members in Struct" 修改 `FAudioMotorSimInputContext` 或 `FAudioMotorSimRuntimeContext`
3. 将该蓝图组件添加到 `UAudioMotorModelComponent` 的 `SimComponents` 数组中

## C++ 用法

### 头文件引入

```cpp
#include "AudioMotorModelComponent.h"
#include "AudioMotorSimTypes.h"
#include "MotorPhysicsSimComponent.h"
```

### 基本用法

`UAudioMotorModelComponent` 是整个系统的核心，负责管理模拟组件链和音频输出组件。

```cpp
// 获取 MotorModelComponent
UAudioMotorModelComponent* MotorModel = /* ... */;

// 构造输入上下文
FAudioMotorSimInputContext Input;
Input.DeltaTime = GetWorld()->GetDeltaSeconds();
Input.Speed = VehicleSpeed;          // 任意方向的速度 (cm/s)
Input.ForwardSpeed = ForwardSpeed;   // 前向速度 (cm/s)
Input.Throttle = ThrottleInput;      // [-1, 1]
Input.Brake = BrakeInput;            // [0, 1]
Input.bDriving = true;
Input.bGrounded = bOnGround;

// 每帧调用 Update
MotorModel->Update(Input);

// 读取输出
float Rpm = MotorModel->GetRpm();       // 归一化 [0-1]
int32 Gear = MotorModel->GetGear();
FAudioMotorSimRuntimeContext Runtime = MotorModel->GetRuntimeInfo();
```

*来源: `AudioMotorModelComponent.cpp` — `Update` 方法*

### 进阶用法

**动态添加/移除模拟组件**：

```cpp
// 添加物理模拟组件，排序值越小越先执行
UMotorPhysicsSimComponent* PhysicsSim = NewObject<UMotorPhysicsSimComponent>(this);
MotorModel->AddMotorSimComponent(PhysicsSim, /*SortOrder=*/0);

// 添加增压组件，排在物理模拟之后
UBoostMotorSimComponent* BoostSim = NewObject<UBoostMotorSimComponent>(this);
MotorModel->AddMotorSimComponent(BoostSim, /*SortOrder=*/10);

// 运行时配置
TArray<FInstancedStruct> ConfigData;
FInstancedStruct& Config = ConfigData.AddDefaulted_GetRef();
Config.InitializeAs<FMotorPhysicsSimConfigData>();
Config.GetMutablePtr<FMotorPhysicsSimConfigData>()->Weight = 1200.f;
MotorModel->ConfigureMotorSimComponents(ConfigData);
```

*来源: `AudioMotorModelComponent.cpp` — `AddMotorSimComponent`, `ConfigureMotorSimComponents`*

**实现自定义模拟组件（C++）**：

```cpp
UCLASS()
class UMyCustomMotorSim : public UAudioMotorSimComponent
{
    GENERATED_BODY()
public:
    virtual void Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo) override
    {
        // 自定义逻辑：修改 Input 或 RuntimeInfo
        // 注意调用 Super::Update() 来触发蓝图 OnUpdate 事件
        Super::Update(Input, RuntimeInfo);
    }
};
```

**实现音频输出接口**：

```cpp
UCLASS()
class UMyAudioOutput : public UActorComponent, public IAudioMotorSimOutput
{
    GENERATED_BODY()
public:
    virtual void Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo) override
    {
        // 根据 RuntimeInfo.Rpm, RuntimeInfo.Volume, RuntimeInfo.Pitch 设置音效参数
    }
    virtual void StartOutput() override { /* 开始播放 */ }
    virtual void StopOutput() override { /* 停止播放 */ }
};

// 注册输出组件
MotorModel->AddMotorAudioComponent(MyAudioOutput);
```

## Demo 示例

### 最小可用示例

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "AudioMotorSim",           // 核心接口和 MotorModel
    "AudioMotorSimStandardComponents"  // 标准模拟组件
});
```

**MyVehicle.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioMotorSimTypes.h"
#include "MyVehicle.generated.h"

class UAudioMotorModelComponent;
class UMotorPhysicsSimComponent;
class URevLimiterMotorSimComponent;

UCLASS()
class AMyVehicle : public AActor
{
    GENERATED_BODY()

public:
    AMyVehicle();

    virtual void Tick(float DeltaTime) override;

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    UAudioMotorModelComponent* MotorModel;

    UPROPERTY(VisibleAnywhere)
    UMotorPhysicsSimComponent* PhysicsSim;

    UPROPERTY(VisibleAnywhere)
    URevLimiterMotorSimComponent* RevLimiter;

    // 你的载具物理数据
    float CurrentSpeed = 0.f;
    float ThrottleInput = 0.f;
    bool bOnGround = true;
};
```

**MyVehicle.cpp**：

```cpp
#include "MyVehicle.h"
#include "AudioMotorModelComponent.h"
#include "MotorPhysicsSimComponent.h"
#include "RevLimiterMotorSimComponent.h"
#include "AudioMotorSimTypes.h"

AMyVehicle::AMyVehicle()
{
    PrimaryActorTick.bCanEverTick = true;

    MotorModel = CreateDefaultSubobject<UAudioMotorModelComponent>(TEXT("MotorModel"));

    PhysicsSim = CreateDefaultSubobject<UMotorPhysicsSimComponent>(TEXT("PhysicsSim"));
    PhysicsSim->Weight = 1000.f;
    PhysicsSim->EngineTorque = 3000.f;

    RevLimiter = CreateDefaultSubobject<URevLimiterMotorSimComponent>(TEXT("RevLimiter"));
    RevLimiter->LimiterMaxRpm = 0.95f;
    RevLimiter->LimitTime = 0.1f;
}

void AMyVehicle::BeginPlay()
{
    Super::BeginPlay();

    // 按 SortOrder 添加模拟组件
    MotorModel->AddMotorSimComponent(PhysicsSim, 0);
    MotorModel->AddMotorSimComponent(RevLimiter, 10);

    MotorModel->StartOutput();
}

void AMyVehicle::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    FAudioMotorSimInputContext Input;
    Input.DeltaTime = DeltaTime;
    Input.Speed = FMath::Abs(CurrentSpeed);
    Input.ForwardSpeed = CurrentSpeed;
    Input.Throttle = ThrottleInput;
    Input.bDriving = true;
    Input.bGrounded = bOnGround;

    MotorModel->Update(Input);

    // 读取结果用于你的音频系统
    float Rpm = MotorModel->GetRpm();
    int32 Gear = MotorModel->GetGear();
}
```

## 模块依赖

### 使用 AudioMotorSim（核心模块）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | ActorComponent 基础 |

### 使用 AudioMotorSimStandardComponents

| 模块 | 用途 |
|---|---|
| `AudioMotorSim` | 核心接口和类型定义 |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | ActorComponent 基础 |

### 使用 AudioMotorSimDebug

| 模块 | 用途 |
|---|---|
| `AudioMotorSim` | 核心接口 |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | ActorComponent 基础 |
| `SlateCore` | 调试 UI |
| `SlateIM` | 即时模式调试窗口（插件依赖） |
| `UnrealEd` | 编辑器功能（仅 Editor 构建） |

## 维护状态

### 近期更新

1. `89a6c233` | 2025-08-13 | Fix for motor sim component reverse hold ignoring physics sim
   - 修复了倒车时 RevLimiter 组件在 hold 模式下忽略物理模拟的问题
2. `01dedb50` | 2025-08-12 | enable motor model debug on client only
   - 将 MotorModel 的调试输出限制为仅客户端，避免服务器端无意义的打印
3. `e41bb224` | 2025-08-08 | make it so coronado vehicle does not shift when locked into place
   - 修复特定载具锁定时不换挡的行为

### 维护评价

- **创建时间**：2022-06-06，约 4 年历史
- **最近更新**：2025 年 8 月，有实质性功能修复和改进
- **维护状态**：**活跃维护** — 最近 1 年内有多次功能性更新
- **已知限制**：实验性插件，默认不启用；无公开测试用例；Debug 模块依赖 SlateIM 插件
- **推荐程度**：如果你需要模块化的载具音频模拟系统，可以使用。但请注意其**实验性**状态，API 可能在未来版本中变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioMotorSim)
- 官方文档（无）
