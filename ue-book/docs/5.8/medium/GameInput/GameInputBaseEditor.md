# Game Input Base

> GameInput is a next-generation input API that exposes input devices of all kinds through a single consistent interface.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏输入基础 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameInputBase` (Runtime), `GameInputBaseEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-02-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameInput) | |

## 用途

GameInput 是微软推出的下一代输入 API，旨在为所有类型的输入设备（手柄、键鼠、方向盘等）提供一个统一且强大的接口。该插件为 Unreal Engine 集成了 GameInput API，允许开发者通过标准化的方式访问和控制各类输入设备，特别是针对 Xbox 生态系统进行了深度优化。它不仅支持基础的按键、摇杆输入，还提供了对高级特性的访问，例如针对 Xbox 无线手柄的**高级触觉反馈（HD Rumble）**和**触觉音频（Haptic Audio）**，以及精确的**设备功能码（Feature Code）**查询，解决了传统输入系统在功能丰富度和一致性上的限制。

## 使用场景

- 你正在开发一款面向 Xbox 平台（Windows）的游戏，希望充分利用 Xbox 无线手柄的高级功能，如精细的脉冲振动（Impulse Trigger）和振动马达控制。
- 你需要一个统一的抽象层来处理来自不同厂商、不同类型的游戏控制器（手柄、方向盘、飞行摇杆等）。
- 你的游戏需要实现与游戏音效同步的“触觉音频”体验，例如让爆炸声通过手柄的振动马达传达出更真实的冲击感。
- 你希望查询输入设备的详细功能信息（是否支持光追、振动电机数量等），以便动态适配游戏功能。

## 蓝图用法

由于 GameInput 主要用于底层的设备控制和状态查询，其核心 API 多为 C++ 接口。蓝图支持主要通过 `FGameInputDevice` 和相关的辅助结构体提供。以下是关键功能的概览。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Devices` | 获取当前所有连接的 GameInput 设备列表。 | `UGameInputSubsystem` |
| `Poll Input` | 为指定的设备和玩家启动输入轮询，获取当前帧的输入状态。 | `UGameInputSubsystem` |
| `Stop Polling` | 停止对指定设备和玩家的输入轮询。 | `UGameInputSubsystem` |
| `Set Device Haptics` | 设置设备振动马达的强度和频率。 | `FGameInputDevice` |
| `Set Rumble State` | （高级）设置 HD Rumble 或 Impulse Trigger 的精细振动状态。 | `FGameInputDevice` |
| `Get Device Info` | 查询设备的详细信息，如支持的按钮数量、摇杆数量、是否支持光追等。 | `FGameInputDevice` |

### 使用示例（蓝图描述）

1.  **枚举设备**：在 BeginPlay 节点后，调用 `Get Devices` 获取设备列表。可以遍历列表，根据 `DeviceInfo` 筛选特定类型的设备（如 Xbox 无线手柄）。
2.  **绑定输入**：为选定的设备调用 `Poll Input`，并设置回调事件。在回调事件中，通过 `FGameInputReading` 结构体获取按键状态、摇杆轴值等。
3.  **触觉反馈**：在游戏事件（如角色受伤、驾驶颠簸）发生时，调用 `Set Rumble State` 节点。可以通过插值节点平滑地改变振动强度，或使用 `Set Device Haptics` 设置更简单的左右马达振动。
4.  **设备功能适配**：在游戏设置中，使用 `Get Device Info` 查询设备是否支持“光追反馈”功能。如果支持，则在游戏中启用相关的视觉-触觉联动效果。

## C++ 用法

### 头文件引入

```cpp
#include "GameInputSubsystem.h"
#include "GameInputDevice.h"
#include "GameInputReading.h"
```

### 基本用法

以下示例展示了如何获取设备、开始输入轮询并处理输入数据。

```cpp
// 引擎初始化完成后，在游戏模块或子系统中
// 来源：引擎子系统典型用法
UGameInputSubsystem* GameInputSubsystem = UGameInputSubsystem::Get();

if (GameInputSubsystem)
{
    // 1. 枚举设备
    TArray<FGameInputDevice*> Devices = GameInputSubsystem->GetDevices();
    if (Devices.Num() > 0)
    {
        FGameInputDevice* MyDevice = Devices[0]; // 选择第一个设备

        // 2. 定义输入轮询回调
        FGameInputDevice::FOnInputCallback OnInputCallback;
        OnInputCallback.BindLambda([](const FGameInputReading* Reading)
        {
            if (Reading)
            {
                // 处理输入数据，例如获取按钮状态
                bool bIsAPressed = Reading->IsButtonPressed(EGameInputButton::A);
                // 获取左摇杆X轴值 (-1.0 到 1.0)
                float LeftStickX = Reading->GetAxis(EGameInputAxis::LeftStickX);
                UE_LOG(LogTemp, Log, TEXT("A Button Pressed: %s, Left Stick X: %f"), bIsAPressed ? TEXT("true") : TEXT("false"), LeftStickX);
            }
        });

        // 3. 开始轮询
        MyDevice->PollInput(OnInputCallback, FPlatformProcess::GetCurrentProcessId(), 0); // 0 为玩家索引
    }
}
```

### 进阶用法

使用设备功能码查询和高级触觉 API。

```cpp
// 假设已有一个有效的 FGameInputDevice* Device 指针
// 来源：Xbox 手柄高级功能用法
if (Device && Device->GetDeviceInfo().bSupportsImpulseTriggers)
{
    // 查询特定功能码 (示例：振动电机数量)
    uint32 VibrationMotorCount = 0;
    FGameInputDeviceInfo Info = Device->GetDeviceInfo();
    // 通常通过 Info 的成员变量直接获取，具体字段需参考头文件
    // VibrationMotorCount = Info.NumVibrationMotors;

    // 设置 Impulse Trigger (脉冲扳机) 的振动
    // 参数：频率 (Hz)，强度 (0.0-1.0)
    Device->SetRumbleState(EGameInputMotor::LeftTrigger, 160.0f, 0.5f); // 左扳机马达
    Device->SetRumbleState(EGameInputMotor::RightTrigger, 160.0f, 0.8f); // 右扳机马达

    // 启动触觉音频端点
    // 通常需要 XAudio2 源数据，此处为概念性代码
    // Device->StartHapticAudioEndpoint(MyXAudio2SourceVoice);
}

// 停止轮询
Device->StopPolling(FPlatformProcess::GetCurrentProcessId(), 0);
```

## Demo 示例

以下是一个简单的 Actor，用于连接第一个 GameInput 设备并打印其基本输入信息。

### MyGameInputActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameInputDevice.h"
#include "MyGameInputActor.generated.h"

UCLASS()
class MYPROJECT_API AMyGameInputActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGameInputActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UFUNCTION()
    void HandleDeviceInput(const FGameInputReading* Reading);

    UPROPERTY()
    UGameInputSubsystem* GameInputSubsystem;

    FGameInputDevice* ActiveDevice;
    FDelegateHandle InputCallbackHandle;
};
```

### MyGameInputActor.cpp

```cpp
#include "MyGameInputActor.h"
#include "GameInputSubsystem.h"
#include "GameInputReading.h"

AMyGameInputActor::AMyGameInputActor()
{
    PrimaryActorTick.bCanEverTick = false;
    ActiveDevice = nullptr;
}

void AMyGameInputActor::BeginPlay()
{
    Super::BeginPlay();

    GameInputSubsystem = UGameInputSubsystem::Get();
    if (GameInputSubsystem)
    {
        TArray<FGameInputDevice*> Devices = GameInputSubsystem->GetDevices();
        if (Devices.Num() > 0)
        {
            ActiveDevice = Devices[0];
            UE_LOG(LogTemp, Log, TEXT("GameInput: Device '%s' connected."), *ActiveDevice->GetDeviceInfo().DisplayName);

            // 绑定输入回调
            FGameInputDevice::FOnInputCallback Callback;
            Callback.BindUObject(this, &AMyGameInputActor::HandleDeviceInput);
            InputCallbackHandle = ActiveDevice->PollInput(Callback, FPlatformProcess::GetCurrentProcessId(), 0);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("GameInput: No devices found."));
        }
    }
}

void AMyGameInputActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ActiveDevice && InputCallbackHandle.IsValid())
    {
        ActiveDevice->StopPolling(FPlatformProcess::GetCurrentProcessId(), 0);
    }
    Super::EndPlay(EndPlayReason);
}

void AMyGameInputActor::HandleDeviceInput(const FGameInputReading* Reading)
{
    if (!Reading || !ActiveDevice) return;

    // 检测 A 按钮按下
    if (Reading->IsButtonPressed(EGameInputButton::A))
    {
        UE_LOG(LogTemp, Log, TEXT("A Button Pressed!"));
        // 触发一个简单的振动反馈
        ActiveDevice->SetHapticsState(EGameInputMotor::LeftMotor, 1.0f, 0.5f); // 左马达，强度1.0，持续0.5秒
    }

    // 打印左摇杆值
    FVector2D LeftStick = FVector2D(
        Reading->GetAxis(EGameInputAxis::LeftStickX),
        Reading->GetAxis(EGameInputAxis::LeftStickY)
    );
    if (!LeftStick.IsNearlyZero())
    {
        UE_LOG(LogTemp, Verbose, TEXT("Left Stick: %s"), *LeftStick.ToString());
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下模块（这些是 GameInput 特有的或关键的依赖）：

| 模块 | 用途 |
|---|---|
| `GameInputBase` | 提供核心的 `FGameInputDevice`， `UGameInputSubsystem` 和轮询逻辑。 |
| `XAudio2` | 用于实现 `Haptic Audio` 功能，将音频流映射到手柄触觉反馈。 |

*注：项目通常还需要依赖 `InputCore`， `Core`， `Engine` 等基础模块，此处不重复列出。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复了跨编译器（MSVC和Clang）的函数类型转换警告，提升代码可移植性。 |
| 2026-05-01 | `1fbba943` | [GameInput] Add haptic audio endpoint support via XAudio2. | 通过集成XAudio2，新增了“触觉音频”端点支持，实现音频到手柄振动的映射。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧的 `UE_LOG` 迁移到新的、更安全的 `UE_LOGF` 宏。 |
| 2026-04-02 | `a4559861` | UE_LOG -> UE_LOGF macro conversion for Game Input modules | 为GameInput所有模块批量完成了UE_LOG到UE_LOGF的日志宏转换。 |
| 2026-04-01 | `1afb0871` | [Input] Add a thread affinitiy for input for IInputDevice so that we can specify which input modules run on which threads | 为输入设备接口添加了线程亲和性设置，允许指定输入模块运行的线程，优化多线程性能。 |

### 维护评价

**积极维护中**。该插件自2024年初创建以来，近6个月（截至分析时间点）保持了活跃且高质量的更新。更新内容不仅包括基础的代码质量维护（日志宏迁移、编译器警告修复），还包含了重要的**功能增强**（触觉音频支持）和**性能优化**（线程亲和性）。这表明 Epic Games 和微软团队正在持续投入开发，致力于将其打造为 Xbox 和 Windows 平台上功能完备的输入解决方案。对于面向 Xbox 生态或需要高级输入功能的 PC 游戏项目，这是一个**推荐使用**且处于快速发展期的插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameInput)
- [微软 GameInput 官方文档](https://learn.microsoft.com/en-us/gaming/gdk/_content/gc/input/overviews/input-overview)（参考）
- [相关测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameInput/Tests)（如果存在）