# MotorSimOutputMotoSynth

> A MotorSim Output component using MotoSynth.

| 属性 | 值 |
|---|---|
| 中文名 | 引擎音效输出组件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MotorSimOutputMotoSynth` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MotorSimOutputMotoSynth) | |

## 用途

MotorSimOutputMotoSynth 是 [AudioMotorSim](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioMotorSim) 系统的输出组件，它将电机模拟计算的运行时数据（转速、负载等）实时传递给 [MotoSynth](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MotoSynth) 音频合成引擎，从而生成逼真的车辆发动机声音。解决了“如何将电机模拟逻辑挂接到 MoToSynth 声音生成”的问题，是实现车辆音效链的关键桥梁。

## 使用场景

- 开发赛车、摩托车、飞行器等需要动态引擎声音的游戏。
- 已使用 MotoSynth 创建音频源，希望直接利用 AudioMotorSim 的物理模拟驱动态度。
- 需要一套完整的“物理模拟 → 声音合成”管线，而不手动编写中间代码。

## 蓝图用法

`UMotorSimOutputMotoSynth` 本身是继承自 `USynthComponentMoto` 的组件，因此它拥有 MotoSynth 的所有蓝图可调用节点（如 `Start`、`Stop`、`SetRPM` 等）。同时它实现了 `IAudioMotorSimOutput` 接口，该接口无蓝图暴露的方法，但可以通过蓝图设置组件的位置、连接到 AudioMotorSim 输出等。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start` | 启动 MotoSynth 声音合成 | `USynthComponentMoto` |
| `Stop` | 停止 MotoSynth 声音合成 | `USynthComponentMoto` |
| `SetRPM` | 直接设置目标 RPM（常用于调试） | `USynthComponentMoto` |
| `IsPlaying` | 检查合成是否正在播放 | `USynthComponentMoto` |

> 提示：实际驱动声音的输入由 `IAudioMotorSimOutput::Update` 自动从 AudioMotorSim 获得，无需在蓝图中手动调用。

### 使用示例（蓝图描述）

1. **创建组件**：在 Actor 中添加 `UMotorSimOutputMotoSynth` 组件（类名 “MotorSimOutput MotoSynth”）。
2. **连接音频输出**：将组件的“Audio Component”插槽连接到需要播放声音的 Actor（通常与自身绑定）。
3. **配置 MotoSynth**：在组件细节面板中指定 `MotoSynth Preset`（如车辆引擎预设）。
4. **启用 AudioMotorSim**：确保场景中存在 `AudioMotorSimComponent`（或自定义实现），并启用输出。
5. **运行模拟**：当 AudioMotorSim 运行时，`MotorSimOutputMotoSynth` 会自动接收转速、负载等参数并控制 MotoSynth 的音高、音量。

## C++ 用法

### 头文件引入

```cpp
#include "MotorSimOutputMotoSynth.h"
```

### 基本用法

创建组件并注册到 AudioMotorSim 系统的最简示例（取自引擎测试用例风格）：

```cpp
// 创建组件
UMotorSimOutputMotoSynth* OutputComp = NewObject<UMotorSimOutputMotoSynth>(Owner);
OutputComp->SetMotoSynthPreset(MyPreset);
OutputComp->RegisterComponent();

// 将其配接到 AudioMotorSim 输出（假设已有 MotorSimComponent）
if (IAudioMotorSimOutput* Output = Cast<IAudioMotorSimOutput>(OutputComp))
{
    MotorSimComponent->SetOutput(Output);
}
```

### 进阶用法

结合 AudioMotorSim 的完整使用流程：

```cpp
#include "AudioMotorSim/AudioMotorSimComponent.h"
#include "MotorSimOutputMotoSynth/MotorSimOutputMotoSynth.h"

void AVehicleActor::SetupEngineSound()
{
    // 1. 创建 AudioMotorSim 输出组件（使用 MotoSynth 实现）
    MotorSimOutput = NewObject<UMotorSimOutputMotoSynth>(this);
    MotorSimOutput->SetMotoSynthPreset(EnginePreset);
    MotorSimOutput->RegisterComponent();

    // 2. 创建或获取已有的 AudioMotorSim 组件（物理模拟源）
    AudioMotorSimComp = NewObject<UAudioMotorSimComponent>(this);
    AudioMotorSimComp->RegisterComponent();

    // 3. 将输出挂接到模拟组件
    AudioMotorSimComp->SetOutput(Cast<IAudioMotorSimOutput>(MotorSimOutput));

    // 4. 启动模拟（通常由物理引擎驱动，也可手动触发）
    MotorSimOutput->Start(); // 开始音效合成
}
```

来源文件路径：`Engine/Plugins/Experimental/MotorSimOutputMotoSynstr/Source/MotorSimOutputMotoSynth/Public/MotorSimOutputMotoSynth.h`

## Demo 示例

以下是一个可在 Actor 中直接使用的完整示例（C++ 类，非蓝图）。

### VehicleEngineSound.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VehicleEngineSound.generated.h"

class UMotorSimOutputMotoSynth;
class UAudioMotorSimComponent;

UCLASS()
class AVehicleEngineSound : public AActor
{
    GENERATED_BODY()

public:
    AVehicleEngineSound();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    UMotorSimOutputMotoSynth* MotorSimOutput;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    UAudioMotorSimComponent* AudioMotorSim;
};
```

### VehicleEngineSound.cpp

```cpp
#include "VehicleEngineSound.h"
#include "MotorSimOutputMotoSynth.h"
#include "AudioMotorSimComponent.h"

AVehicleEngineSound::AVehicleEngineSound()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AVehicleEngineSound::BeginPlay()
{
    Super::BeginPlay();

    // 创建 MotoSynth 输出组件
    MotorSimOutput = NewObject<UMotorSimOutputMotoSynth>(this);
    MotorSimOutput->SetRelativeLocation(FVector::ZeroVector);
    MotorSimOutput->RegisterComponent();
    AddInstanceComponent(MotorSimOutput); // 保证被保存

    // 创建 AudioMotorSim 模拟组件
    AudioMotorSim = NewObject<UAudioMotorSimComponent>(this);
    AudioMotorSim->RegisterComponent();
    AddInstanceComponent(AudioMotorSim);

    // 连接输出
    AudioMotorSim->SetOutput(Cast<IAudioMotorSimOutput>(MotorSimOutput));

    // 启动音效
    MotorSimOutput->Start();
}
```

> 提示：实际运行时需要配合物理模拟或手动设置 RPM，此处仅为最小演示。请确保在项目设置中启用了 `AudioMotorSim` 和 `MotoSynth` 插件。

## 模块依赖

要使用 MotorSimOutputMotoSynth，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `AudioMotorSim` | 电机模拟运行时数据和接口定义 |
| `MotoSynth` | 音频合成引擎及预设管理 |

省略了 Core、CoreUObject、Engine 等标准依赖。

## 维护状态

### 近期更新

- 2025-04-23 `939cc6e5` 使用 FortniteClient 构建目标转换所有文件，为方法/静态变量添加 dllstorage
- 2024-11-10 `66e9bb39` 移除所有 `#if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` 作用域
- 2023-05-15 `da92084a` 优化私有模块包含和依赖
- 2023-01-13 `3c9aacb1` [Engine/Plugins] 初始提交（插件创建）
- 2023-01-12 `2f78497e` [Engine/Plugins] 实验性插件创建

### 维护评价

该插件创建于 2023 年初，至今（2025 年）约 2.5 年，仍处于实验阶段。最近的更新（2025-04）涉及构建系统迁移，2024 年有代码清理，2023 年为增长期。没有废弃标记，属于 **维护中** 状态。由于它紧密依赖 AudioMotorSim 和 MotoSynth，这两者均为活跃插件，因此可以放心使用。但实验性阶段意味着 API 未来可能发生变化，建议关注引擎版本升级带来的改动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MotorSimOutputMotoSynth)
- [AudioMotorSim 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioMotorSim)
- [MotoSynth 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MotoSynth)