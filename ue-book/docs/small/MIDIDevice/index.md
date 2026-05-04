# MIDI Device Support

> Allows you to send and receive MIDI events through a simple API in either C++ or Blueprints

| 属性 | 值 |
|---|---|
| 分类 | Input Devices |
| 默认启用 | ❌ 否（需要手动启用） |
| 包含内容 | 否 |
| 模块 | MIDIDevice (Runtime) |
| 平台 | Win64, Mac |
| 创建时间 | 2016-09-21 |
| 年龄标签 | 👴 老古董（约 9.6 年） |
| Beta | ⚠️ 是（IsBetaVersion=true） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MIDIDevice) | |

## 用途

MIDIDevice plugin 封装了 [PortMidi](http://portmedia.sourceforge.net/portmidi/) 库，为 UE5 提供 MIDI 设备的输入/输出能力。它解决了以下问题：

- **设备发现**：枚举系统上所有已连接的 MIDI 输入/输出设备
- **MIDI 输入**：从 MIDI 键盘、控制器等硬件接收 MIDI 事件（音符开/关、弯音、控制变更等）
- **MIDI 输出**：向 MIDI 设备发送事件，用于控制外部合成器、灯光设备等
- **蓝图友好**：所有核心功能都暴露为蓝图节点，事件通过 Delegate 广播

底层依赖 PortMidi 这个跨平台 MIDI 库，plugin 在每个 Tick 时轮询所有已打开的 MIDI 设备，读取新事件并广播给订阅者。

> ⚠️ **注意**：此 plugin 标记为 Beta（`IsBetaVersion=true`），且默认未启用。需要在项目设置中手动启用。

## 使用场景

- 你正在做一个 **音乐可视化项目**，需要用 MIDI 键盘实时控制视觉效果 → 用 MIDIDevice 接收 NoteOn/ControlChange 事件
- 你要做一个 **互动装置**，通过 MIDI 控制灯光/音效 → 用 MIDIDeviceOutputController 发送 MIDI 消息
- 你正在开发 **节奏游戏**，需要精确捕获 MIDI 输入的时序和力度 → 用 MIDIDeviceInputController 的 OnMIDINoteOn 委托
- 你需要用 **MIDI 控制器** 作为游戏输入设备（如 DJ 类游戏）→ 枚举设备后创建 Controller 绑定

## 蓝图用法

### 核心节点

**设备管理（`UMIDIDeviceManager`）**

| 节点 | 说明 |
|---|---|
| `Find All MIDI Device Info` | 枚举所有 MIDI 输入/输出设备，返回设备 ID、名称、是否默认设备等信息 |
| `Find MIDI Devices` | 枚举所有 MIDI 设备（旧版接口，返回 `FFoundMIDIDevice` 列表） |
| `Get Default MIDI Input Device ID` | 获取系统默认 MIDI 输入设备的 ID |
| `Get Default MIDI Output Device ID` | 获取系统默认 MIDI 输出设备的 ID |
| `Get MIDI Input Device ID By Name` | 通过设备名称查找输入设备 ID |
| `Get MIDI Output Device ID By Name` | 通过设备名称查找输出设备 ID |
| `Create MIDI Device Controller` | 创建一个双向 MIDI 控制器（输入+输出），返回 `UMIDIDeviceController` |
| `Create MIDI Device Input Controller` | 创建一个仅输入的 MIDI 控制器，返回 `UMIDIDeviceInputController` |
| `Create MIDI Device Output Controller` | 创建一个仅输出的 MIDI 控制器，返回 `UMIDIDeviceOutputController` |
| `Shut Down All MIDI Devices` | 关闭所有已打开的 MIDI 设备连接 |

**输入控制器事件（`UMIDIDeviceInputController`）**

| 委托 | 说明 | 参数 |
|---|---|---|
| `OnMIDINoteOn` | 音符按下 | Controller, Timestamp, Channel, Note, Velocity |
| `OnMIDINoteOff` | 音符释放 | Controller, Timestamp, Channel, Note, Velocity |
| `OnMIDIPitchBend` | 弯音轮变化 | Controller, Timestamp, Channel, Pitch (0-16383) |
| `OnMIDIAftertouch` | 触后压力（单音） | Controller, Timestamp, Channel, Note, Amount |
| `OnMIDIControlChange` | 控制器变化（踏板、旋钮等） | Controller, Timestamp, Channel, Type, Value |
| `OnMIDIProgramChange` | 音色切换 | Controller, Timestamp, Channel, ControlID, Velocity |
| `OnMIDIChannelAftertouch` | 通道触后压力 | Controller, Timestamp, Channel, Amount |

**旧版控制器事件（`UMIDIDeviceController`）**

| 委托 | 说明 |
|---|---|
| `OnMIDIEvent` | 所有 MIDI 事件的统一回调（Controller, Timestamp, EventType, Channel, ControlID, Velocity, RawEventType） |

**输出控制器（`UMIDIDeviceOutputController`）**

| 节点 | 说明 |
|---|---|
| `Send MIDI Event` | 发送原始 MIDI 事件（EventType, Channel, Data1, Data2） |
| `Send MIDI Note On` | 发送音符开（Channel, Note, Velocity） |
| `Send MIDI Note Off` | 发送音符关（Channel, Note, Velocity） |
| `Send MIDI Pitch Bend` | 发送弯音（Channel, Pitch 0-16383） |
| `Send MIDI Note Aftertouch` | 发送触后（Channel, Note, Amount） |
| `Send MIDI Control Change` | 发送控制变更（Channel, Type, Value） |
| `Send MIDI Program Change` | 发送音色切换（Channel, ProgramNumber） |
| `Send MIDI Channel Aftertouch` | 发送通道触后（Channel, Amount） |

### 使用示例（蓝图描述）

**接收 MIDI 键盘输入并打印音符：**

1. 在 BeginPlay 中，调用 `Find All MIDI Device Info` 获取设备列表
2. 调用 `Get Default MIDI Input Device ID` 获取默认输入设备 ID
3. 调用 `Create MIDI Device Input Controller`（传入 DeviceID）创建输入控制器，存为变量
4. 从控制器变量拖出，绑定 `OnMIDINoteOn` 事件
5. 在事件回调中，用 `Print String` 打印 Channel、Note、Velocity

**发送 MIDI Note On 到外部设备：**

1. 在 BeginPlay 中，调用 `Find All MIDI Device Info`
2. 调用 `Create MIDI Device Output Controller` 创建输出控制器
3. 需要发声时，调用控制器的 `Send MIDI Note On`（Channel=1, Note=60, Velocity=100）
4. 停止时调用 `Send MIDI Note Off`（Channel=1, Note=60, Velocity=0）

## C++ 用法

### 头文件引入

```cpp
#include "MIDIDeviceManager.h"
#include "MIDIDeviceInputController.h"
#include "MIDIDeviceOutputController.h"
#include "MIDIDeviceController.h"  // 旧版双向控制器
```

### 基本用法 —— 枚举设备并创建输入控制器

```cpp
// 枚举所有 MIDI 设备
TArray<FMIDIDeviceInfo> InputDevices;
TArray<FMIDIDeviceInfo> OutputDevices;
UMIDIDeviceManager::FindAllMIDIDeviceInfo(InputDevices, OutputDevices);

for (const FMIDIDeviceInfo& Device : InputDevices)
{
    UE_LOG(LogTemp, Log, TEXT("Input Device: ID=%d, Name=%s, Default=%s"),
        Device.DeviceID, *Device.DeviceName,
        Device.bIsDefaultDevice ? TEXT("Yes") : TEXT("No"));
}

// 获取默认输入设备 ID
int32 DeviceID = -1;
UMIDIDeviceManager::GetDefaultMIDIInputDeviceID(DeviceID);

// 创建输入控制器（buffer size 1024）
UMIDIDeviceInputController* InputController =
    UMIDIDeviceManager::CreateMIDIDeviceInputController(DeviceID, 1024);

if (InputController)
{
    // 绑定 Note On 事件
    InputController->OnMIDINoteOn.AddDynamic(this, &AMyActor::HandleNoteOn);
}
```

### 基本用法 —— 发送 MIDI 输出

```cpp
// 获取默认输出设备
int32 OutputDeviceID = -1;
UMIDIDeviceManager::GetDefaultMIDIOutputDeviceID(OutputDeviceID);

UMIDIDeviceOutputController* OutputController =
    UMIDIDeviceManager::CreateMIDIDeviceOutputController(OutputDeviceID);

if (OutputController)
{
    // 发送 Note On: Channel 1, Note 60 (Middle C), Velocity 100
    OutputController->SendMIDINoteOn(1, 60, 100);

    // 稍后发送 Note Off
    OutputController->SendMIDINoteOff(1, 60, 0);

    // 发送 Control Change (例如 sustain pedal)
    OutputController->SendMIDIControlChange(1, 64, 127);

    // 发送弯音
    OutputController->SendMIDIPitchBend(1, 8192);  // 中间值 = 无弯音
}
```

### 进阶用法 —— 使用旧版双向控制器

旧版 `UMIDIDeviceController` 将所有事件统一为一个 `OnMIDIEvent` 委托，需要自行判断事件类型：

```cpp
UMIDIDeviceController* Controller =
    UMIDIDeviceManager::CreateMIDIDeviceController(DeviceID, 1024);

if (Controller)
{
    Controller->OnMIDIEvent.AddDynamic(this, &AMyActor::HandleMIDIEvent);
}

// 回调处理
void AMyActor::HandleMIDIEvent(UMIDIDeviceController* MIDIDeviceController,
    int32 Timestamp, EMIDIEventType EventType, int32 Channel,
    int32 ControlID, int32 Velocity, int32 RawEventType)
{
    switch (EventType)
    {
    case EMIDIEventType::NoteOn:
        UE_LOG(LogTemp, Log, TEXT("Note On: Ch=%d Note=%d Vel=%d"),
            Channel, ControlID, Velocity);
        break;
    case EMIDIEventType::ControlChange:
        UE_LOG(LogTemp, Log, TEXT("CC: Ch=%d Type=%d Val=%d"),
            Channel, ControlID, Velocity);
        break;
    // ...
    }
}
```

### 进阶用法 —— 使用 C++ 原始事件委托

`UMIDIDeviceInputController` 还提供了一个 C++ 专用的 `OnMIDIRawEvent` 委托（非蓝图），参数更原始：

```cpp
// 这是一个普通 multicast delegate，不是 dynamic 的
InputController->OnMIDIRawEvent.AddRaw(this, &AMyActor::HandleRawMIDI);

void AMyActor::HandleRawMIDI(UMIDIDeviceInputController* Controller,
    int32 Timestamp, int32 Type, int32 Channel,
    int32 MessageData1, int32 MessageData2)
{
    // Type: 0xF0 >> 4 后的值，直接对应 MIDI status 的高 4 位
    // Channel: 1-16
    // MessageData1/MessageData2: 原始 MIDI 数据字节
}
```

## Demo 示例

### 最小完整示例：MIDI 音符可视化

```cpp
// MyMIDIActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MIDIDeviceInputController.h"
#include "MyMIDIActor.generated.h"

UCLASS()
class AMyMIDIActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void OnNoteOn(UMIDIDeviceInputController* Controller, int32 Timestamp,
                  int32 Channel, int32 Note, int32 Velocity);

    UFUNCTION()
    void OnNoteOff(UMIDIDeviceInputController* Controller, int32 Timestamp,
                   int32 Channel, int32 Note, int32 Velocity);

private:
    UPROPERTY()
    UMIDIDeviceInputController* MIDIInput = nullptr;
};
```

```cpp
// MyMIDIActor.cpp
#include "MyMIDIActor.h"
#include "MIDIDeviceManager.h"

void AMyMIDIActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取默认输入设备
    int32 DeviceID = -1;
    UMIDIDeviceManager::GetDefaultMIDIInputDeviceID(DeviceID);

    if (DeviceID >= 0)
    {
        MIDIInput = UMIDIDeviceManager::CreateMIDIDeviceInputController(DeviceID, 1024);
        if (MIDIInput)
        {
            MIDIInput->OnMIDINoteOn.AddDynamic(this, &AMyMIDIActor::OnNoteOn);
            MIDIInput->OnMIDINoteOff.AddDynamic(this, &AMyMIDIActor::OnNoteOff);
        }
    }
}

void AMyMIDIActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UMIDIDeviceManager::ShutDownAllMIDIDevices();
    Super::EndPlay(EndPlayReason);
}

void AMyMIDIActor::OnNoteOn(UMIDIDeviceInputController* Controller,
    int32 Timestamp, int32 Channel, int32 Note, int32 Velocity)
{
    UE_LOG(LogTemp, Log, TEXT("♪ Note ON  - Ch:%d Note:%d Vel:%d"),
        Channel, Note, Velocity);
}

void AMyMIDIActor::OnNoteOff(UMIDIDeviceInputController* Controller,
    int32 Timestamp, int32 Channel, int32 Note, int32 Velocity)
{
    UE_LOG(LogTemp, Log, TEXT("♪ Note OFF - Ch:%d Note:%d"), Channel, Note);
}
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "MIDIDevice"
});
```

## 模块依赖

MIDIDevice 模块自身的依赖（你的项目不需要直接依赖这些）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、日志、TArray 等 |
| `CoreUObject` | UObject 系统、反射 |
| `Engine` | FTickableGameObject、模块管理 |
| `portmidi`（第三方静态库） | 底层 MIDI I/O，跨平台 MIDI 通信 |

**你的项目只需要依赖 `MIDIDevice` 模块即可。**

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-05-19 | `a60b2b5` | Fixup API macros for merged modules, PURE_VIRTUAL does not need API export | API 导出宏修复，适配 UE5 模块合并改动 |
| 2025-04-23 | `939cc6e` | Used FortniteClient build target to find and convert all files to have dllstorage | 批量添加 DLL 导出标记，构建系统维护 |
| 2024-01-23 | `fde2961` | Fixed up a lot of bool-taking container resize functions to take EAllowShrinking instead | UE5 API 变更适配（EAllowShrinking 替换 bool） |

### 维护评价

- **创建时间**：2016 年 9 月，已存在近 10 年
- **最近更新**：最近 3 次提交全部是构建系统/API 宏维护性修复，**无任何功能性更新**
- **Beta 状态**：自创建以来一直标记为 `IsBetaVersion=true`，从未毕业为正式版
- **默认未启用**：`EnabledByDefault=false`，需要手动在项目设置中启用
- **平台限制**：仅支持 Win64 和 Mac，不支持 Linux/主机平台
- **架构陈旧**：旧版 `UMIDIDeviceController` 仍保留在代码中，与新版 Input/Output Controller 共存，显得冗余
- **性能注意**：每帧通过 `TObjectIterator` 遍历所有 UObject 查找控制器实例，代码中有 `@todo midi perf` 注释承认这不是最优方案

**综合评价**：这是一个功能完整但处于维护停滞状态的 plugin。核心功能（设备枚举、MIDI 输入输出）可以正常使用，但不要期待新功能或架构改进。如果你的项目需要更高级的 MIDI 功能（如 MPE、MIDI 2.0、虚拟 MIDI 端口），可能需要自行扩展或使用第三方方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MIDIDevice)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [PortMidi 官网](http://portmedia.sourceforge.net/portmidi/)
