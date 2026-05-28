# Audio Motor Sim Debug

> Compositional method for simulating audio for vehicles.

| 属性 | 值 |
|---|---|
| 中文名 | 音频电机模拟调试器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioMotorSimDebug` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioMotorSim/Source/AudioMotorSimDebug) | |

## 用途

这是一个面向开发者的调试工具模块，用于在游戏运行时实时可视化和调试 `AudioMotorSim` 插件中车辆音频模拟系统的参数变化。它提供了一个独立的调试窗口，能够动态显示模拟器（如 `UAudioMotorModelComponent`）及其各个组件（如 `IAudioMotorSim` 实现）的关键参数，例如引擎转速、负载等，并支持绘制这些参数随时间变化的波形图，是开发、测试和调优车辆音频效果的有力助手。

## 使用场景

- 你正在实现一个基于 `AudioMotorSim` 插件的车辆音频系统，需要实时查看引擎转速、油门开度等核心参数是否按预期变化。
- 你在调整音频混合逻辑（如淡入淡出、频率调制）时，需要观察多个参数的交互关系和动态波形。
- 你需要为一个新的 `IAudioMotorSim` 组件添加自定义调试数据，并希望将其可视化。
- 你希望在 Shipping 构建之外的开发版本中，拥有一个便捷的工具来监控和调试音频模拟逻辑。

## 蓝图用法

该模块主要为 C++ 开发者提供调试功能，未在提供的头文件中发现标记为 `BlueprintCallable` 或 `BlueprintReadWrite` 的公共 API。其使用主要在 C++ 层面。

## C++ 用法

### 头文件引入

```cpp
#include "AudioMotorSimDebug.h"
#include "IAudioMotorModelDebugger.h"
```

### 基本用法

调试器通过 `IAudioMotorModelDebugger` 接口进行注册和交互。在开发版本中，`AudioMotorSimDebug` 模块启动时会自动创建一个调试器实例。

```cpp
// 1. 注册一个 UAudioMotorModelComponent 到调试器进行监控
if (IAudioMotorModelDebugger* Debugger = IAudioMotorModelDebugger::Get())
{
    Debugger->RegisterComponentWithDebugger(MyMotorModelComponent);
}
```

### 进阶用法

除了监控 `UAudioMotorModelComponent` 的基本属性，你还可以为调试对象附加额外的结构化数据。

```cpp
// 定义一个自定义调试数据结构
USTRUCT()
struct FMyDebugData
{
    GENERATED_BODY()

    UPROPERTY()
    float CustomDebugValue = 0.f;

    UPROPERTY()
    bool bSomeState = false;
};

// 在游戏逻辑中，当需要发送额外调试信息时
if (IAudioMotorModelDebugger* Debugger = IAudioMotorModelDebugger::Get())
{
    FMyDebugData DebugData;
    DebugData.CustomDebugValue = SomeCalculatedValue;
    DebugData.bSomeState = IsInSpecialMode();
    Debugger->SendAdditionalDebugData(MyObject, DebugData);
}
```

此外，你也可以利用调试器内部的参数图工具来绘制自定义数据。

```cpp
// 假设你在组件中有一个 double 类型的参数
double* MyParameterPtr = &MyMotorSimComponent->CurrentLoad;

// 使用 FParamPtrGraph 创建一个波形图
AudioMotorModelDebug::FParamPtrGraph<double> LoadGraph(
    TEXT("Custom Load"),
    MyParameterPtr,
    AudioMotorModelDebug::FParamGraphSettings(FDoubleRange(0, 1.5), FLinearColor::Yellow)
);

// 在每帧更新中绘制
LoadGraph.Draw();
```

## Demo 示例

一个最小的 C++ 示例，展示如何在自定义组件中集成调试数据发送。

```cpp
// MyVehicleAudioComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "MyVehicleAudioComponent.generated.h"

class UAudioMotorModelComponent;

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyVehicleAudioComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
    // 引用场景中已有的电机模型组件
    UPROPERTY()
    TObjectPtr<UAudioMotorModelComponent> MotorModel;
};

// MyVehicleAudioComponent.cpp
#include "MyVehicleAudioComponent.h"
#include "IAudioMotorModelDebugger.h"

void UMyVehicleAudioComponent::BeginPlay()
{
    Super::BeginPlay();
    MotorModel = GetOwner()->FindComponentByClass<UAudioMotorModelComponent>();
}

void UMyVehicleAudioComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!MotorModel || !IAudioMotorModelDebugger::IsAvailable())
    {
        return;
    }

    // 获取调试器实例
    IAudioMotorModelDebugger* Debugger = IAudioMotorModelDebugger::Get();

    // 确保模型已注册（通常在 MotorModel 的 BeginPlay 或类似位置注册一次即可）
    // Debugger->RegisterComponentWithDebugger(MotorModel);

    // 发送自定义的调试数据
    struct FVehicleAudioDebugData
    {
        float GearShiftIntensity = 0.f;
        float WindNoiseFactor = 0.f;
    };
    FVehicleAudioDebugData DebugData;
    DebugData.GearShiftIntensity = CalculateGearShiftEffect(); // 假设的函数
    DebugData.WindNoiseFactor = GetWindNoiseFactor();
    Debugger->SendAdditionalDebugData(this, DebugData);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioMotorSim` | 提供被调试的核心接口和类型（如 `UAudioMotorModelComponent`, `IAudioMotorSim`）。 |
| `SlateIM` | 提供即时模式（IMGUI风格）的UI框架，用于绘制调试窗口和参数图表。 |

*注意：`SlateIM` 插件本身被标记为在 Shipping 构建中禁用，这与 `AudioMotorSimDebug` 模块的构建配置一致。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧版 `UE_LOG` 迁移到新版 `UE_LOGF`。 |
| 2026-01-17 | `302d1b88` | [Backout] - CL49913998 | 回滚了之前的提交 CL49913998。 |
| 2026-01-17 | `622fab9f` | SlateIM: You can now create always on top windows. | 为依赖的 SlateIM 框架增加了创建“始终置顶”窗口的功能。 |
| 2026-01-13 | `393bf787` | [Backout] - CL49749599 | 回滚了之前的提交 CL49749599。 |
| 2026-01-12 | `1ed12928` | SlateIM: You can now create always on top windows. | （同前）SlateIM 框架更新。 |

### 维护评价

**维护状态：** 维护中。
**推荐使用：** **谨慎使用**。
该模块自 2022 年创建以来一直存在，但最近的提交（截至 2026 年）主要围绕其依赖的 `SlateIM` 框架进行更新和回滚，以及对日志宏的现代化迁移，并没有针对 `AudioMotorSimDebug` 模块自身功能的增强或修复。这表明该模块处于一个基础维护状态，核心功能已稳定，但缺少活跃的功能开发。
**重要限制**：该模块标记为 **实验性** (`IsExperimentalVersion: true`)，且 **默认不启用** (`EnabledByDefault: false`)。它仅在非 Shipping 构建且非服务器目标下编译。这意味着：
1. 它不适合用于最终发行版本。
2. 它的API可能在未来版本中发生不兼容的变更。
3. 它是一个纯粹的开发者工具。

**结论**：对于需要在开发阶段深度调试 `AudioMotorSim` 车辆音频系统的开发者，此模块提供了有价值的可视化工具。但由于其实验性质和较低的更新频率，不建议在高度稳定的生产环境中依赖它，使用时需做好其API可能变动的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioMotorSim/Source/AudioMotorSimDebug)
- [官方文档]()（暂无）
- [测试用例]()（在提供的源码中未发现）