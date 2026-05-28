# Audio Motor Sim

> Compositional method for simulating audio for vehicles.

| 属性 | 值 |
|---|---|
| 中文名 | 车辆音频模拟 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioMotorSim` (Runtime), `AudioMotorSimStandardComponents` (Runtime), `AudioMotorSimDebug` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioMotorSim) | |

## 用途

AudioMotorSim 插件并非一个简单的音频播放器，而是提供了一套用于**模拟车辆（尤其是引擎）物理状态**的框架。其核心设计思想是“组合式”（Compositional）：开发者可以将不同的模拟组件（如引擎模拟、变速箱模拟、轮胎摩擦模拟等）像乐高积木一样组合在一起，每个组件负责计算车辆状态的一个方面（如RPM、挡位），最终由一个主模型（`UAudioMotorModelComponent`）汇总这些状态，再驱动音频组件输出相应的声音。

这个插件解决了在游戏中创建逼真、动态且可高度定制的车辆音频系统的问题，避免了传统基于单一RPM曲线的僵硬声音设计。

## 使用场景

- 你正在开发一款赛车游戏，需要引擎声音能够平滑地响应油门、刹车、挡位切换和车辆滑行状态。
- 你的游戏中有多种车辆（如卡车、跑车），希望它们拥有独特且真实的发动机声浪，而不是简单的音调缩放。
- 你需要一个灵活的系统，允许设计师或程序员通过添加、移除或调整不同的物理模拟模块（如空气阻力、轮胎打滑）来微调声音表现。

## 蓝图用法

该插件的核心是组件化架构，所有操作都围绕着 `UAudioMotorModelComponent` 和实现 `IAudioMotorSim` 接口的组件进行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Motor Sim Component` | 向主模型添加一个物理模拟组件，并设置其更新优先级（SortOrder） | `UAudioMotorModelComponent` |
| `Add Motor Audio Component` | 向主模型添加一个音频输出组件，用于接收模拟结果并播放声音 | `UAudioMotorModelComponent` |
| `Update` | **核心驱动函数**。在每帧调用，传入当前车辆的输入信息（`FAudioMotorSimInputContext`），驱动所有模拟组件计算并更新运行时状态（`FAudioMotorSimRuntimeContext`） | `UAudioMotorModelComponent` |
| `Get Rpm` | 获取当前模拟计算出的归一化RPM值 (0-1) | `UAudioMotorModelComponent` |
| `Get Gear` | 获取当前模拟计算出的挡位 | `UAudioMotorModelComponent` |
| `Set Enabled` | 启用或禁用一个具体的模拟组件（例如，当车辆悬空时禁用轮胎模拟） | `UAudioMotorSimComponent` (及其子类) |
| `BP_Update` | **蓝图可实现事件**。用于在C++创建的 `UAudioMotorSimComponent` 子类中，或在蓝图中直接继承该组件时，实现自定义的模拟逻辑。 | `UAudioMotorSimComponent` |

### 使用示例（蓝图描述）

1.  **初始化设置**：在载具Actor的 `BeginPlay` 事件中：
    *   使用 `Add Motor Audio Component` 节点将负责播放引擎声音的音频组件连接到 `UAudioMotorModelComponent`。
    *   使用 `Add Motor Sim Component` 节点，按顺序添加多个模拟组件（例如：`UAudioMotorSimPhysicsComponent`，`UAudioMotorSimGearBoxComponent`）。**SortOrder** 值决定了组件的更新顺序。
2.  **每帧更新**：在载具Actor的 `Event Tick` 事件中：
    *   将当前的 `DeltaTime`、`Throttle`、`Brake`、`Speed` 等信息填入一个 `FAudioMotorSimInputContext` 结构体。
    *   调用 `Update` 节点，将该结构体传入 `UAudioMotorModelComponent`。
    *   `Update` 内部会按顺序调用每个 `IAudioMotorSim` 组件的 `Update` 函数，它们会读取输入并修改共同的 `FAudioMotorSimRuntimeContext`。
    *   最后，`UAudioMotorModelComponent` 会将更新后的 `RuntimeContext`（包含RPM、挡位等）传递给所有注册的 `IAudioMotorSimOutput` 音频组件，驱动声音变化。

## C++ 用法

### 头文件引入

```cpp
// 核心接口与类型
#include "AudioMotorSimModule.h"
#include "IAudioMotorSim.h"
#include "AudioMotorSimTypes.h"
#include "AudioMotorModelComponent.h"
```

### 基本用法

**创建自定义模拟组件（C++）**：你可以继承 `UAudioMotorSimComponent` 来创建自己的模拟逻辑。

*MyCustomSimComponent.h*
```cpp
#pragma once
#include "IAudioMotorSim.h"
#include "MyCustomSimComponent.generated.h"

UCLASS(ClassGroup = AudioMotorSim, meta = (BlueprintSpawnableComponent))
class MYGAME_API UMyCustomSimComponent : public UAudioMotorSimComponent
{
    GENERATED_BODY()

public:
    // 构造函数中设置默认值
    UMyCustomSimComponent();

protected:
    // 实现核心更新逻辑
    virtual void Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo) override;

private:
    UPROPERTY(EditAnywhere, Category = "Config")
    float CustomSensitivity = 1.0f;
};
```

*MyCustomSimComponent.cpp*
```cpp
#include "MyCustomSimComponent.h"

UMyCustomSimComponent::UMyCustomSimComponent()
{
    // 可以在构造函数中设置组件属性
}

void UMyCustomSimComponent::Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo)
{
    // 在这里编写自定义的模拟逻辑
    // 例如，根据油门和速度计算一个虚拟的“增压”值
    float CustomBoost = Input.Throttle * CustomSensitivity * (1.0f - (Input.Speed / 1000.0f));
    
    // 修改运行时上下文，供后续组件或音频输出使用
    // RuntimeInfo.Pitch += CustomBoost * 0.1f; // 可以微调音高
    // RuntimeInfo.Rpm = FMath::Clamp(RuntimeInfo.Rpm + CustomBoost * 0.01f, 0.f, 1.f); // 影响RPM
}
```

### 进阶用法

**配置模拟组件**：插件支持通过 `FInstancedStruct` 对组件进行运行时配置。

```cpp
// 假设你有一个用于配置齿轮比的结构体
USTRUCT(BlueprintType)
struct FMyGearboxConfig : public FAudioMotorSimConfigData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TArray<float> GearRatios = {3.0f, 2.0f, 1.5f, 1.0f, 0.8f};
};

// 在蓝图或代码中，你可以这样配置齿轮箱组件
FMyGearboxConfig Config;
Config.GearRatios = {3.5f, 2.2f, 1.6f, 1.1f, 0.9f, 0.75f};

// 将配置数据包装成 FInstancedStruct
FInstancedStruct ConfigStruct;
ConfigStruct.InitializeAs<FMyGearboxConfig>();
ConfigStruct.GetMutable<FMyGearboxConfig>() = Config;

// 获取齿轮箱组件并应用配置
if (TObjectPtr<UGearboxSimComponent> Gearbox = MotorModel->GetMotorSimOfType<UGearboxSimComponent>())
{
    Gearbox->ConfigMotorSim(ConfigStruct);
}
```

## Demo 示例

以下是一个最小化的自定义模拟组件示例。

**MyMinimalSimComponent.h**
```cpp
#pragma once
#include "IAudioMotorSim.h"
#include "MyMinimalSimComponent.generated.h"

UCLASS(ClassGroup = AudioMotorSim, meta = (BlueprintSpawnableComponent))
class UMyMinimalSimComponent : public UAudioMotorSimComponent
{
    GENERATED_BODY()

public:
    virtual void Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo) override;
    
private:
    UPROPERTY(EditAnywhere, Category = "Config")
    float VolumeScale = 1.0f;
};
```

**MyMinimalSimComponent.cpp**
```cpp
#include "MyMinimalSimComponent.h"

void UMyMinimalSimComponent::Update(FAudioMotorSimInputContext& Input, FAudioMotorSimRuntimeContext& RuntimeInfo)
{
    // 一个简单的模拟：根据速度线性调整音量
    float SpeedFactor = FMath::Clamp(Input.Speed / 500.0f, 0.f, 1.f);
    RuntimeInfo.Volume = FMath::Lerp(0.5f, 1.0f, SpeedFactor) * VolumeScale;
    
    // 可以设置引擎RPM随油门变化
    RuntimeInfo.Rpm = FMath::FInterpTo(RuntimeInfo.Rpm, Input.Throttle, Input.DeltaTime, 5.0f);
}
```

## 模块依赖

该插件自身的依赖已在其Build.cs中定义。要在你的项目中使用此插件，你的模块Build.cs通常需要依赖：

| 模块 | 用途 |
|---|---|
| `AudioMotorSim` | 核心接口、类型和基础组件 |
| `AudioMotorSimStandardComponents` | Epic提供的标准模拟组件（如齿轮箱、物理模拟等） |
| `AudioMotorSimDebug` | 用于在编辑器和开发构建中调试模拟状态（非Shipping构建） |

此外，根据你项目的配置，可能还需要依赖 `SlateIM`（如果使用了其调试UI）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF。 |
| 2026-01-17 | `302d1b88` | [Backout] - CL49913998 | 回滚了一个特定的更改（CL49913998）。 |
| 2026-01-17 | `622fab9f` | SlateIM: You can now create always on top windows. | （插件依赖的SlateIM）现在支持创建始终置顶的窗口。 |
| 2026-01-13 | `393bf787` | [Backout] - CL49749599 | 回滚了另一个更改（CL49749599）。 |
| 2026-01-12 | `1ed12928` | SlateIM: You can now create always on top windows. | （插件依赖的SlateIM）首次引入始终置顶窗口功能。 |

### 维护评价

- **创建时间**：约4年，相对较新。
- **最近更新**：最近一次更新在2026年4月，主要是内部优化（日志宏迁移）。更早的提交与插件依赖的 `SlateIM` 模块相关，并非对本插件功能的直接更新。
- **活跃程度**：维护**不活跃**。自插件创建以来，除了依赖模块的更新和内部重构外，没有看到新的功能提交或核心接口的增强。插件仍标记为 `IsExperimentalVersion` 且默认禁用。
- **已知问题**：作为实验性功能，其API和行为在未来版本中可能会发生变化。
- **推荐使用**：适用于愿意接受实验性功能、且需要高度可定制化车辆音频模拟的项目。在生产环境中使用需谨慎，需自行承担API可能变更的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioMotorSim)
- 官方文档：无