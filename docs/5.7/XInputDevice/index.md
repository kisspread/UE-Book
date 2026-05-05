# XInput Device

> XInput is a Game Controller API for Windows.

| 属性 | 值 |
|---|---|
| 分类 | Input Devices |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | XInputDevice (Runtime) |
| 平台限制 | Win64 |
| 支持程序 | LiveLinkHub |
| 创建时间 | 2023-08-22 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Windows/XInputDevice) | |

## 用途

XInputDevice 是 UE5 在 Windows 平台上接入 Xbox 兼容手柄的底层驱动插件。它封装了微软的 XInput API，将物理手柄的按键、摇杆、扳机等输入转化为 UE 统一的 `IInputDevice` 事件流，供引擎的输入系统消费。

**为什么存在？** XInput 是 Windows 上最广泛的手柄协议，覆盖 Xbox 360、Xbox One、Xbox Series 以及大量兼容手柄。引擎需要一个标准化的 Runtime 模块来将 XInput 硬件状态转化为引擎内部的 `FGamepadKeyNames` 事件，并通过 `FGenericApplicationMessageHandler` 分发给 Slate 和游戏逻辑。这个插件就是这个桥梁。

**核心能力：**
- 最多同时支持 **4 个** XInput 手柄
- 按键边沿检测（按下/抬起），支持按键重复事件
- 摇杆和扳机的模拟量输入（归一化到 [-1, 1]）
- **力反馈（振动）**：左右两个马达的独立控制
- 手柄热插拔检测与设备状态管理
- 动态扳机释放死区（Dynamic Trigger Release DeadZone）

## 使用场景

- 你在做 PC 端游戏，需要支持 Xbox 手柄 → 这个插件默认启用，无需额外配置
- 你需要力反馈/振动反馈 → 通过 `UInputDeviceSubsystem` 或 `FLatentActionInfo` 设置振动
- 你在做多人本地游戏，需要支持最多 4 个手柄同时输入 → XInput 天然支持 4 手柄
- 你在用 Enhanced Input 系统 → XInputDevice 作为底层设备驱动，自动与 Enhanced Input 配合

## 蓝图用法

XInputDevice 本身不暴露任何 `BlueprintCallable` 函数。它是一个底层设备驱动，输入事件通过引擎的输入系统（`UPlayerInput`、`UInputDeviceSubsystem`、Enhanced Input）传递到蓝图层面。

### 间接使用方式

| 功能 | 节点 | 所在类 |
|---|---|---|
| 查询手柄是否连接 | `Get Platform User` / `Is Gamepad Attached` | `UInputDeviceSubsystem` |
| 设置振动 | `Set Force Feedback Effect` / `Play Haptic Effect` | `APlayerController` / `UInputDeviceSubsystem` |
| 读取手柄输入 | Enhanced Input 的 `IA_Gamepad_*` Actions | Enhanced Input 系统 |

### 使用示例（蓝图描述）

**检测手柄连接：**
在 BeginPlay 中，使用 `Get Input Device Subsystem` → `Is Device Connected` 节点，传入 `Platform User ID 0` 检测第一个手柄是否已连接。

**设置振动：**
使用 `Play Force Feedback Effect` 节点（在 `APlayerController` 上），创建一个 `Force Feedback Effect` 资产，配置 Left Large / Left Small / Right Large / Right Small 四个通道的振动强度。

## C++ 用法

### 头文件引入

```cpp
// XInputInterface 是 Private 类，不能直接 include
// 通过引擎的输入系统间接使用
#include "GameFramework/InputDeviceSubsystem.h"
#include "IInputDevice.h"
```

### 基本用法

XInputDevice 作为 Runtime 插件自动注册，你不需要手动创建实例。引擎启动时 `FXInputDeviceModule::CreateInputDevice()` 会被调用，自动创建 `XInputInterface` 实例。

**通过 CVar 调试：**

```cpp
// 控制台变量：强制每帧刷新手柄状态
// 默认为 0（仅在手柄已连接时轮询），设为 1 可强制每帧检测连接状态
// 来源: XInputInterface.cpp
XInput.ForceControllerStateUpdate 1
```

**通过 InputDeviceSubsystem 交互：**

```cpp
// 获取子系统
UInputDeviceSubsystem* Subsystem = UInputDeviceSubsystem::Get();

// 查询特定用户的最新手柄设备
FPlatformUserId UserId = /* ... */;
FInputDeviceId DeviceId = Subsystem->GetLatestDeviceOfType(UserId, EHardwareDevicePrimaryType::Gamepad);
```

### 进阶用法

**动态扳机释放死区（Dynamic Trigger Release DeadZone）：**

通过 `FInputDeviceTriggerDynamicReleaseDeadZoneProperty` 可以动态调整左右扳机的释放阈值，解决扳机回弹时的抖动问题。

```cpp
// 来源: XInputInterface.cpp - SetDeviceProperty()
FInputDeviceTriggerDynamicReleaseDeadZoneProperty TriggerProp;
TriggerProp.AffectedTriggers = EInputDeviceTriggerMask::All;
TriggerProp.DeadZone = 0.1f; // 自定义释放阈值

// 通过 InputDeviceSubsystem 发送到指定手柄
// 设备会调用 SetDynamicTriggerThreshold() 应用新阈值
```

**自定义手柄输入处理：**

```cpp
// 实现自定义 FGenericApplicationMessageHandler 来拦截手柄事件
// XInputInterface 会通过以下方法分发事件：
// - OnControllerButtonPressed / OnControllerButtonReleased  (按键)
// - OnControllerAnalog  (摇杆/扳机)
```

## 按键映射表

XInputDevice 将 XInput 按键映射到 UE 的 `FGamepadKeyNames`：

| XInput 按键 | UE 按键名 | 说明 |
|---|---|---|
| A | `FaceButtonBottom` | 面板底部按钮 |
| B | `FaceButtonRight` | 面板右侧按钮 |
| X | `FaceButtonLeft` | 面板左侧按钮 |
| Y | `FaceButtonTop` | 面板顶部按钮 |
| LB | `LeftShoulder` | 左肩键 |
| RB | `RightShoulder` | 右肩键 |
| Back | `SpecialRight` | 特殊右键 |
| Start | `SpecialLeft` | 特殊左键 |
| Left Thumb | `LeftThumb` | 左摇杆按下 |
| Right Thumb | `RightThumb` | 右摇杆按下 |
| LT | `LeftTriggerThreshold` | 左扳机阈值 |
| RT | `RightTriggerThreshold` | 右扳机阈值 |
| D-Pad Up/Down/Left/Right | `DPadUp`/`DPadDown`/`DPadLeft`/`DPadRight` | 方向键 |
| Left Stick Up/Down/Left/Right | `LeftStickUp`/`LeftStickDown`/`LeftStickLeft`/`LeftStickRight` | 左摇杆方向 |
| Right Stick Up/Down/Left/Right | `RightStickUp`/`RightStickDown`/`RightStickLeft`/`RightStickRight` | 右摇杆方向 |

**模拟量输入键名：**

| 轴 | UE 键名 | 值域 |
|---|---|---|
| 左摇杆 X | `LeftAnalogX` | [-1.0, 1.0] |
| 左摇杆 Y | `LeftAnalogY` | [-1.0, 1.0] |
| 右摇杆 X | `RightAnalogX` | [-1.0, 1.0] |
| 右摇杆 Y | `RightAnalogY` | [-1.0, 1.0] |
| 左扳机 | `LeftTriggerAnalog` | [0.0, 1.0] |
| 右扳机 | `RightTriggerAnalog` | [0.0, 1.0] |

## 配置

### Input.ini

插件自带 `Config/Input.ini`，注册了 Windows 平台的硬件设备映射：

```ini
[InputPlatformSettings_Windows InputPlatformSettings]
+HardwareDevices=(InputClassName="XInputInterface",HardwareDeviceIdentifier="XInputController",PrimaryDeviceType=Gamepad,SupportedFeaturesMask=260)
```

`SupportedFeaturesMask=260`（0x104）表示支持 Left/Right Large Motor 和 Left/Right Small Motor 的力反馈通道。

### 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `XInput.ForceControllerStateUpdate` | 0 | 设为 1 强制每帧检测手柄连接状态（默认仅在已连接时轮询） |

### 按键重复延迟

通过 `Input.ini` 中的 `/Script/Engine.InputSettings` 配置：

```ini
[/Script/Engine.InputSettings]
InitialButtonRepeatDelay=0.2
ButtonRepeatDelay=0.1
```

## Demo 示例

XInputDevice 是纯 Runtime 设备驱动，没有独立的测试用例或可运行 Demo。以下是一个使用力反馈的最小 C++ 示例：

### MyHapticActor.h

```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyHapticActor.generated.h"

UCLASS()
class AMyHapticActor : public AActor
{
    GENERATED_BODY()
public:
    // 蓝图可调用：在指定手柄上触发振动
    UFUNCTION(BlueprintCallable, Category = "Haptic")
    void TriggerVibration(int32 ControllerId, float LargeMotor, float SmallMotor);
};
```

### MyHapticActor.cpp

```cpp
#include "MyHapticActor.h"
#include "GameFramework/InputDeviceSubsystem.h"

void AMyHapticActor::TriggerVibration(int32 ControllerId, float LargeMotor, float SmallMotor)
{
    // 通过引擎的力反馈系统，XInputDevice 会自动接收并应用到手柄马达
    // Force Feedback 使用 FForceFeedbackChannelType 通道：
    //   LEFT_LARGE, LEFT_SMALL, RIGHT_LARGE, RIGHT_SMALL
    // XInputDevice 在 XInputInterface::SetChannelValue() 中将值映射到
    // XINPUT_VIBRATION 的 wLeftMotorSpeed 和 wRightMotorSpeed
}
```

### Build.cs 依赖

```csharp
// 如果需要直接访问 InputDeviceSubsystem
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "Engine",
    "InputDevice"  // 提供 IInputDevice 接口
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、日志、容器 |
| `ApplicationCore` | 平台应用抽象层 |
| `Engine` | 游戏框架（InputDeviceSubsystem） |
| `InputDevice` | `IInputDevice` / `IInputDeviceModule` 接口定义 |
| `XInput` (ThirdParty) | 微软 XInput SDK（仅 Windows 平台链接） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-05-09 | `235cfcb4` | Simple IsPressed function in GamepadUtils for dynamic trigger release deadzone | 为动态扳机释放死区添加了 `IsPressed()` 辅助函数，改善扳机回弹抖动问题 |
| 2025-05-08 | `2e79cc3f` | Dynamic Trigger Release support on main analog trigger platforms (disabled by default) | 引入动态扳机释放死区机制，默认禁用。解决了扳机键在释放瞬间的误触发问题 |
| 2025-01-14 | `22edfd32` | Add a "Get input device for force feedback" function on the input device subsystem | 在 InputDeviceSubsystem 中新增力反馈设备查询函数，XInputDevice 相应适配 |

### 维护评价

- **创建时间**：2023-08-22，约 2.7 年前
- **最近更新**：2025-05-09，约 3 个月前有功能性更新
- **维护状态**：✅ **活跃维护** — 2025 年有多次实质性功能更新（动态扳机死区、力反馈改进）
- **平台限制**：仅 Windows (Win64)，这是 XInput API 的固有限制
- **已知限制**：最多 4 个手柄（XInput API 限制），无法区分 Xbox 360 和 Xbox One 手柄
- **推荐使用**：✅ 推荐。作为默认启用的 Runtime 插件，PC 端游戏开箱即用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Windows/XInputDevice)
- [微软 XInput 文档](https://learn.microsoft.com/en-us/windows/win32/xinput/)
