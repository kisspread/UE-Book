# MIDI Device Support

> Allows you to send and receive MIDI events through a simple API in either C++ or Blueprints（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MIDI 设备支持 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MIDIDevice` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2016-09-21 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MIDIDevice) | |

## 用途

MIDIDevice 插件提供了一套简单的 API，让 UE 项目能够与计算机上连接的 MIDI 硬件设备进行双向通信。它封装了底层的 PortMidi 库，将 MIDI 协议的各种事件类型（Note On/Off、Pitch Bend、Control Change 等）转化为蓝图可绑定的事件委托和 C++ 可调用的方法。

**核心解决的问题**：UE 默认没有任何 MIDI 设备支持。如果你需要接收来自 MIDI 键盘、控制器或合成器的输入信号，或者需要向外部 MIDI 设备发送指令（如控制舞台灯光、驱动硬件乐器），就必须使用这个插件。

**存在的意义**：许多交互式艺术装置、音乐可视化项目、演出控制系统都需要实时的 MIDI 通信能力。这个插件让这些需求无需外部中间件即可在 UE 内完成。

**平台限制**：仅支持 **Win64** 和 **Mac**。

## 使用场景

- 你在做一个交互式音乐装置，用 MIDI 键盘控制 UE 中的粒子特效 → 用 MIDIDevice 的 Input Controller 接收按键事件
- 你在做一个灯光演出系统，需要通过 UE 向 MIDI 灯光控制器发送指令 → 用 Output Controller 发送 Control Change 事件
- 你在做一个音乐教学应用，需要检测用户在 MIDI 键盘上弹的音符是否正确 → 绑定 `OnMIDINoteOn` 事件进行判定
- 你需要同时处理多个 MIDI 设备（如键盘 + 推子控制器）→ 为每个设备创建独立的 Controller 实例

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindMIDIDevices` | 枚举所有已连接的 MIDI 设备，返回设备列表（含 ID、名称、能力信息） | `UMIDIDeviceManager` |
| `FindAllMIDIDeviceInfo` | 分别枚举 MIDI 输入和输出设备，返回详细信息 | `UMIDIDeviceManager` |
| `GetMIDIInputDeviceIDByName` | 根据设备名称查找输入设备 ID | `UMIDIDeviceManager` |
| `GetMIDIOutputDeviceIDByName` | 根据设备名称查找输出设备 ID | `UMIDIDeviceManager` |
| `GetDefaultMIDIInputDeviceID` | 获取系统默认 MIDI 输入设备 ID | `UMIDIDeviceManager` |
| `GetDefaultMIDIOutputDeviceID` | 获取系统默认 MIDI 输出设备 ID | `UMIDIDeviceManager` |
| `CreateMIDIDeviceController` | 创建通用 MIDI 设备控制器（输入+输出），旧版 API | `UMIDIDeviceManager` |
| `CreateMIDIDeviceInputController` | 创建专用 MIDI 输入控制器 | `UMIDIDeviceManager` |
| `CreateMIDIDeviceOutputController` | 创建专用 MIDI 输出控制器 | `UMIDIDeviceManager` |
| `ShutDownAllMIDIDevices` | 关闭所有已打开的 MIDI 设备 | `UMIDIDeviceManager` |
| `SendMIDIEvent` | 发送原始 MIDI 事件 | `UMIDIDeviceOutputController` |
| `SendMIDINoteOn` | 发送 Note On 事件 | `UMIDIDeviceOutputController` |
| `SendMIDINoteOff` | 发送 Note Off 事件 | `UMIDIDeviceOutputController` |
| `SendMIDIPitchBend` | 发送弯音轮事件 | `UMIDIDeviceOutputController` |
| `SendMIDIControlChange` | 发送控制变更事件（如旋钮、推子） | `UMIDIDeviceOutputController` |
| `SendMIDIProgramChange` | 发送音色切换事件 | `UMIDIDeviceOutputController` |
| `SendMIDINoteAftertouch` | 发送单音触后事件 | `UMIDIDeviceOutputController` |
| `SendMIDIChannelAftertouch` | 发送通道触后事件 | `UMIDIDeviceOutputController` |

### 输入事件委托（绑定在 Input Controller 上）

| 事件 | 说明 |
|---|---|
| `OnMIDINoteOn` | 按键按下，参数包含 Channel、Note、Velocity |
| `OnMIDINoteOff` | 按键释放，参数包含 Channel、Note、Velocity |
| `OnMIDIPitchBend` | 弯音轮变化，参数包含 Channel、Pitch (0-16383) |
| `OnMIDIControlChange` | 控制器值变化（旋钮/推子/踏板），参数包含 Channel、Type、Value |
| `OnMIDIProgramChange` | 音色/程序切换，参数包含 Channel、ProgramNumber |
| `OnMIDIAftertouch` | 单键触后压力，参数包含 Channel、Note、Amount |
| `OnMIDIChannelAftertouch` | 通道触后压力，参数包含 Channel、Amount |

### 使用示例（蓝图描述）

**接收 MIDI 输入**：

1. 在 BeginPlay 中调用 `FindMIDIDevices`，将返回的 `FoundMIDIDevices` 数组遍历
2. 挑选目标设备（通过 `DeviceName` 或 `bIsDefaultInputDevice` 判断）
3. 调用 `CreateMIDIDeviceInputController`，传入 `DeviceID` 和 `MIDIBufferSize`（默认 1024）
4. 将返回的 Controller 存储到变量
5. 在 Controller 上绑定 `OnMIDINoteOn` 事件，在事件中读取 Note 和 Velocity 参数

**发送 MIDI 输出**：

1. 枚举设备后，用 `CreateMIDIDeviceOutputController` 创建输出控制器
2. 调用 `SendMIDINoteOn(Channel=0, Note=60, Velocity=127)` 发送中央 C
3. 延时后调用 `SendMIDINoteOff(Channel=0, Note=60, Velocity=0)` 释放

## C++ 用法

### 头文件引入

```cpp
#include "MIDIDeviceManager.h"
#include "MIDIDeviceInputController.h"
#include "MIDIDeviceOutputController.h"
#include "MIDIDeviceController.h"
```

### 基本用法

```cpp
// 枚举所有 MIDI 设备
TArray<FFoundMIDIDevice> Devices;
UMIDIDeviceManager::FindMIDIDevices(Devices);

for (const FFoundMIDIDevice& Device : Devices)
{
    UE_LOG(LogTemp, Log, TEXT("MIDI Device: %s (ID: %d), Input: %s, Output: %s"),
        *Device.DeviceName, Device.DeviceID,
        Device.bCanReceiveFrom ? TEXT("Yes") : TEXT("No"),
        Device.bCanSendTo ? TEXT("Yes") : TEXT("No"));
}
```

### 进阶用法

```cpp
// 创建输入控制器并绑定事件
UMIDIDeviceInputController* InputController = UMIDIDeviceManager::CreateMIDIDeviceInputController(DeviceID, 1024);
if (InputController)
{
    InputController->OnMIDINoteOn.AddDynamic(this, &AMyActor::HandleNoteOn);
}

// 事件处理函数
void AMyActor::HandleNoteOn(UMIDIDeviceInputController* Controller, int32 Timestamp, int32 Channel, int32 Note, int32 Velocity)
{
    UE_LOG(LogTemp, Log, TEXT("Note On: Channel=%d, Note=%d, Velocity=%d"), Channel, Note, Velocity);
}

// 创建输出控制器并发送事件
UMIDIDeviceOutputController* OutputController = UMIDIDeviceManager::CreateMIDIDeviceOutputController(DeviceID);
if (OutputController)
{
    OutputController->SendMIDINoteOn(0, 60, 127);  // Channel 0, Middle C, Max velocity
    OutputController->SendMIDIControlChange(0, 7, 100);  // Channel 0, Volume (CC7), Value 100
    OutputController->SendMIDIProgramChange(0, 48);  // Channel 0, 切换到音色 #48
}
```

## Demo 示例

**MyMIDIActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MIDIDeviceInputController.h"
#include "MIDIDeviceOutputController.h"
#include "MyMIDIActor.generated.h"

UCLASS()
class AMyMIDIActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void OnNoteOn(UMIDIDeviceInputController* Controller, int32 Timestamp, int32 Channel, int32 Note, int32 Velocity);

    UFUNCTION()
    void OnControlChange(UMIDIDeviceInputController* Controller, int32 Timestamp, int32 Channel, int32 ControlID, int32 Value);

private:
    UPROPERTY()
    TObjectPtr<UMIDIDeviceInputController> InputController;

    UPROPERTY()
    TObjectPtr<UMIDIDeviceOutputController> OutputController;
};
```

**MyMIDIActor.cpp**

```cpp
#include "MyMIDIActor.h"
#include "MIDIDeviceManager.h"

void AMyMIDIActor::BeginPlay()
{
    Super::BeginPlay();

    // 枚举设备
    TArray<FFoundMIDIDevice> Devices;
    UMIDIDeviceManager::FindMIDIDevices(Devices);

    if (Devices.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No MIDI devices found!"));
        return;
    }

    // 使用第一个可用的输入设备
    for (const FFoundMIDIDevice& Device : Devices)
    {
        if (Device.bCanReceiveFrom && !InputController)
        {
            InputController = UMIDIDeviceManager::CreateMIDIDeviceInputController(Device.DeviceID, 1024);
            if (InputController)
            {
                InputController->OnMIDINoteOn.AddDynamic(this, &AMyMIDIActor::OnNoteOn);
                InputController->OnMIDIControlChange.AddDynamic(this, &AMyMIDIActor::OnControlChange);
                UE_LOG(LogTemp, Log, TEXT("MIDI Input: %s"), *Device.DeviceName);
            }
        }

        if (Device.bCanSendTo && !OutputController)
        {
            OutputController = UMIDIDeviceManager::CreateMIDIDeviceOutputController(Device.DeviceID);
            if (OutputController)
            {
                UE_LOG(LogTemp, Log, TEXT("MIDI Output: %s"), *Device.DeviceName);
            }
        }
    }
}

void AMyMIDIActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UMIDIDeviceManager::ShutDownAllMIDIDevices();
    Super::EndPlay(EndPlayReason);
}

void AMyMIDIActor::OnNoteOn(UMIDIDeviceInputController* Controller, int32 Timestamp, int32 Channel, int32 Note, int32 Velocity)
{
    // 收到按键后，将音符回显到输出设备（回放测试）
    if (OutputController)
    {
        OutputController->SendMIDINoteOn(Channel, Note, Velocity);
    }
}

void AMyMIDIActor::OnControlChange(UMIDIDeviceInputController* Controller, int32 Timestamp, int32 Channel, int32 ControlID, int32 Value)
{
    UE_LOG(LogTemp, Log, TEXT("CC: Ch=%d, Type=%d, Value=%d"), Channel, ControlID, Value);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。内部使用 PortMidi 第三方库（已随 UE 源码提供，位于 `Engine/Source/ThirdParty/`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新 API |
| 2025-05-19 | `a60b2b5c` | Fixup API macros for merged modules, PURE_VIRTUAL does not need API export | 修复模块合并后的 API 导出宏问题 |
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 为所有方法添加 DLL 导出标记 |
| 2024-01-23 | `fde2961f` | Fixed up a lot of bool-taking container resize functions to take EAllowShrinking instead. | 适配容器 API 变更 |
| 2023-05-26 | `b6ee3a6c` | Fix UE_LOG callsites that have format string-related UB | 修复日志格式字符串未定义行为 |

### 维护评价

MIDIDevice 插件创建于 2016 年，至今约 9 年。**该插件从未脱离 Beta 状态**（`IsBetaVersion=true`），且默认不启用（`EnabledByDefault=false`）。

从 git 历史来看，近年来的更新全部是**编译适配和全局重构**（API 宏修复、日志迁移、容器 API 适配等），**没有任何功能性更新或 Bug 修复**。这说明该插件处于"能用就不管"的状态。

**已知限制**：
- 仅支持 Win64 和 Mac，无 Linux/移动端/主机支持
- 从未添加过 MIDI 输出功能的进一步完善（如 SysEx 支持）
- `OnMIDIRawEvent` 仅在 C++ 中可用，蓝图无法绑定
- 始终标记为实验性，可能在未来版本中被移除

**推荐**：如果你的项目只需要基本的 MIDI 输入输出，且目标平台为 Windows/Mac，这个插件可以直接使用。但对于需要跨平台 MIDI 支持的项目，建议考虑第三方 MIDI 库（如 RtMidi）的自定义集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MIDIDevice)
- 官方文档：无
- 测试用例：未找到专门的自动化测试