# Audio Motor Sim

> Compositional method for simulating audio for vehicles.

| 属性 | 值 |
|---|---|
| 中文名 | 音频引擎模拟 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioMotorSim` (Runtime), `AudioMotorSimStandardComponents` (Runtime), `AudioMotorSimDebug` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioMotorSim) | |

## 用途

AudioMotorSim 插件旨在提供一种组合式、基于组件的方法来模拟车辆引擎的音频驱动状态。它并非直接生成音频，而是专注于计算并输出影响引擎音效的关键物理参数，如转速 (RPM)、速度、档位等。核心思想是将复杂的引擎物理模拟拆分成多个独立的、可组合的功能组件（如基础物理、转速限制器、助力等），通过组合这些组件来灵活、高效地模拟不同类型车辆的引擎特性。这种方法解决了传统单一模拟类参数臃肿、难以定制和维护的问题。

## 使用场景

- 你在制作一款赛车游戏，需要真实且可调的引擎音效 → 使用此插件计算车辆的RPM、档位等数据，再通过MetaSound或其他音频系统驱动音效。
- 你需要为不同车辆（如卡车、超跑、卡丁车）配置差异化的引擎响应 → 通过组合不同的组件（如`MotorPhysicsSimComponent`， `BoostMotorSimComponent`）并调整参数来实现。
- 你的车辆拥有复杂的动力总成特性，如助力系统、特殊的换挡逻辑、倒车限制等 → 使用专门的组件（`BoostMotorSimComponent`， `RevLimiterMotorSimComponent`， `ReverseMotorSimComponent`）来处理。

## 蓝图用法

插件的功能主要通过继承自`UAudioMotorSimComponent`的各类组件暴露给蓝图。每个组件都可以作为场景组件添加到Actor上，并拥有大量的可编辑属性和可绑定的事件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnGearChanged` | 档位改变时触发的委托事件 | `UMotorPhysicsSimComponent` |
| `OnUpShift` / `OnDownShift` | 升档/降档时触发的委托事件 | `URpmCurveMotorSimComponent` |
| `OnRevLimiterHit` / `OnRevLimiterStateChanged` | 触及转速限制器/限制器状态改变时触发的委托 | `URevLimiterMotorSimComponent` |
| `OnThrottleEngaged` / `OnThrottleReleased` | 油门踩下/松开时触发的委托 | `UThrottleStateMotorSimComponent` |
| `OnEngineBlowoff` | 油门释放时，根据保持油门的时长触发的“泄压”事件 | `UThrottleStateMotorSimComponent` |

### 使用示例（蓝图描述）

1.  **基础车辆设置**：在你的车辆Pawn/Actor中，添加一个`MotorPhysicsSimComponent`组件。在细节面板中，调整`Weight`、`EngineTorque`、`GearRatios`等参数以模拟车辆的物理特性。
2.  **添加转速限制**：在同一Actor上添加一个`RevLimiterMotorSimComponent`组件。设置`LimiterMaxRpm`（限制转速上限）和`LimitTime`（限制时长）。将该组件的`Update`顺序设置为在物理模拟组件之后。
3.  **监听事件**：在蓝图中，获取`OnGearChanged`事件的引用并绑定一个自定义事件。当档位变化时，该事件会触发，你可以在其中切换对应的档位音效。
4.  **组合使用**：你可以同时添加多个组件。例如，添加`BoostMotorSimComponent`来模拟氮气加速，并在`ConfigMotorSim`函数中通过`FInstancedStruct`动态配置`FMotorPhysicsSimConfigData`来调整参数。

## C++ 用法

### 头文件引入

```cpp
#include “AudioMotorSim/AudioMotorSimComponent.h”
#include “AudioMotorSimStandardComponents/MotorPhysicsSimComponent.h”
```

### 基本用法

核心是通过`UAudioMotorSimComponent`基类的`Update`函数来驱动模拟。你需要一个“驱动器”组件（如`UMotorPhysicsSimComponent`）来计算核心物理，并可能使用其他组件来修改其输出。

```cpp
// 在你的车辆类中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Motor Sim”)
TObjectPtr<UMotorPhysicsSimComponent> MotorPhysicsSim;

UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Motor Sim”)
TObjectPtr<URevLimiterMotorSimComponent> RevLimiterSim;

// 初始化时配置
void AMyVehicle::BeginPlay()
{
    Super::BeginPlay();
    
    if (MotorPhysicsSim && RevLimiterSim)
    {
        // 可以通过 FInstancedStruct 在运行时配置参数
        FMotorPhysicsSimConfigData ConfigData;
        ConfigData.Weight = 1200.0f;
        ConfigData.EngineTorque = 3000.0f;
        
        MotorPhysicsSim->ConfigMotorSim(FInstancedStruct::Make(ConfigData));
        
        // 设置模拟更新顺序，物理组件先更新
        MotorPhysicsSim->SetUpdateOrder(0);
        RevLimiterSim->SetUpdateOrder(1);
    }
}

// 在 Tick 或专门的更新函数中驱动模拟
void AMyVehicle::UpdateMotorSim()
{
    FAudioMotorSimInputContext Input;
    Input.Throttle = CurrentThrottle;
    Input.Brake = CurrentBrake;
    Input.Speed = GetSpeed();
    Input.bClutchEngaged = bIsClutched;
    // ... 其他输入
    
    FAudioMotorSimRuntimeContext Runtime;
    
    // 依次更新组件，它们会修改 Runtime 上下文
    if (MotorPhysicsSim) MotorPhysicsSim->Update(Input, Runtime);
    if (RevLimiterSim) RevLimiterSim->Update(Input, Runtime);
    
    // 此时 Runtime 中的 RPM, Gear, Velocity 等值可用于驱动音效
    float CurrentRPM = Runtime.RPM;
    int32 CurrentGear = Runtime.Gear;
}
```

### 进阶用法

创建自定义的`UAudioMotorSimComponent`子类，实现特定的模拟逻辑，然后与其他组件组合。

```cpp
// MyCustomAirResistanceComponent.h
UCLASS(ClassGroup = “AudioMotorSim”, meta = (BlueprintSpawnableComponent))
class UMyCustomAirResistanceComponent : public UAudioMotorSimComponent
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “Resistance”)
    float AirDensity = 1.225f; // kg/m^3
    
    virtual void Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo) override;
};

// MyCustomAirResistanceComponent.cpp
void UMyCustomAirResistanceComponent::Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo)
{
    // 基于速度增加额外的阻力，影响 RuntimeInfo 中的计算
    if (RuntimeInfo.Velocity > 0.f)
    {
        float DragForce = 0.5f * AirDensity * FMath::Square(RuntimeInfo.Velocity) * DragCoefficient;
        // 应用此力到模拟中，可能需要修改 RuntimeInfo 的某个字段或通过其他方式影响下游组件
    }
}
```

## Demo 示例

以下是一个自定义“阻力组件”的示例，展示了如何扩展插件。

```cpp
// MyCustomAirResistanceComponent.h
#pragma once

#include “CoreMinimal.h”
#include “AudioMotorSim/AudioMotorSimComponent.h”
#include “MyCustomAirResistanceComponent.generated.h”

UCLASS(ClassGroup = “AudioMotorSim”, meta = (BlueprintSpawnableComponent))
class YOURPROJECT_API UMyCustomAirResistanceComponent : public UAudioMotorSimComponent
{
    GENERATED_BODY()

public:
    // 空气密度 (kg/m³)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “AirResistance”, meta=(ClampMin=“0.0”))
    float AirDensity = 1.225f;

    // 风阻系数 (无量纲)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “AirResistance”, meta=(ClampMin=“0.0”))
    float DragCoefficient = 0.3f;

    // 迎风面积 (m²)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “AirResistance”, meta=(ClampMin=“0.0”))
    float FrontalArea = 2.0f;

    virtual void Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo) override;

private:
    // 辅助函数：计算风阻力
    float CalculateAirResistanceForce(float Velocity) const;
};
```

```cpp
// MyCustomAirResistanceComponent.cpp
#include “MyCustomAirResistanceComponent.h”

void UMyCustomAirResistanceComponent::Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo)
{
    Super::Update(Input, RuntimeInfo);

    // 计算当前速度下的空气阻力
    const float AirResistanceForce = CalculateAirResistanceForce(RuntimeInfo.Velocity);

    // 将空气阻力作为“摩擦力”或“阻力”的一部分，施加到模拟中。
    // 这里假设 RuntimeInfo 或其依赖的输入中有一个表示外部阻力的字段。
    // 具体实现取决于插件核心模块如何处理此类力。
    // 示例：RuntimeInfo.AdditionalFriction += AirResistanceForce;
}

float UMyCustomAirResistanceComponent::CalculateAirResistanceForce(float Velocity) const
{
    // 空气阻力公式：F = 0.5 * ρ * v² * Cd * A
    return 0.5f * AirDensity * FMath::Square(Velocity) * DragCoefficient * FrontalArea;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioMotorSim` | 提供核心接口、基类和数据类型 |
| `SlateIM` | 用于 `AudioMotorSimDebug` 模块的调试界面，在 Shipping 和 Server 构建中禁用 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-01-17 | `302d1b88` | [Backout] - CL49913998 | 回滚了某个更改（CL49913998）。 |
| 2026-01-17 | `622fab9f` | SlateIM: You can now create always on top windows. | SlateIM 功能更新：支持创建置顶窗口。 |
| 2026-01-13 | `393bf787` | [Backout] - CL49749599 | 回滚了某个更改（CL49749599）。 |
| 2026-01-12 | `1ed12928` | SlateIM: You can now create always on top windows. | SlateIM 功能更新：支持创建置顶窗口。 |

### 维护评价

**维护中**。插件自2022年创建以来，近期（2026年）仍有活动，主要集中在日志宏迁移和对依赖模块 `SlateIM` 的更新。尽管该插件被标记为实验性（`IsExperimentalVersion=true`）且默认未启用（`EnabledByDefault=false`），但其最近的提交并非bug修复或功能增强，更多是引擎层面的基础设施维护。这表明插件的功能可能已趋于稳定，但尚未被提升为正式功能。对于需要车辆引擎音效模拟的项目，它仍然是一个有价值且可用的起点，但需要接受其“实验性”状态，意味着未来API或行为可能会发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioMotorSim)