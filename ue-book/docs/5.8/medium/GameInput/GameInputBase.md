# Game Input Base

> GameInput is a next-generation input API that exposes input devices of all kinds through a single consistent interface.

| 属性 | 值 |
|---|---|
| 中文名 | 新一代输入接口 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameInputBase` (Runtime), `GameInputBaseEditor` (Editor), `GameInputWindowsLibrary` (External) |
| 实验性 | 否 |
| 创建时间 | 2024-02-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameInput) | |

## 用途

GameInput 是微软推出的下一代统一输入 API，通过单一接口暴露所有类型的输入设备。本插件将 GameInput SDK 集成到 UE5 中，替代或补充原有的 XInput、WinDualShock 等平台特定输入模块。

**解决的问题**：不同类型的输入设备（手柄、方向盘、飞行摇杆、街机摇杆、原始 HID 设备等）各自有独立的驱动和 API。GameInput 提供统一抽象层，让开发者无需关心底层硬件差异，同时支持传感器、触控和原始设备报告等高级功能。

**为什么存在**：微软在 GDK（Game Development Kit）中引入 GameInput 作为标准输入接口，本插件是 Epic 为 UE5 提供的官方集成。它仅支持 Win64 平台，需要系统安装 GameInput Redistributable。

## 使用场景

- 你需要支持多种不同类型的游戏外设（手柄、方向盘、飞行摇杆）且不想分别处理每个平台的输入 API → 用 GameInput
- 你需要读取原始 HID 设备报告数据（如吉他控制器的摇杆、特殊设备的自定义轴）→ 配置 `RawDeviceReport` 处理器
- 你需要通过音频驱动控制器的触觉反馈（振动）→ 启用 Haptic Sensor Support
- 你在开发 Xbox/Windows 交叉平台游戏，希望使用微软官方推荐的输入方案 → 用 GameInput 替代 XInput
- 你需要精确控制哪些厂商/型号的设备被处理，以及各自的按键映射 → 通过 `UGameInputDeveloperSettings` 配置

## 蓝图用法

本插件**没有暴露蓝图 API**。GameInput 完全在引擎底层运行时工作，通过 `IInputDevice` 接口和 `FGenericApplicationMessageHandler` 将输入事件注入引擎输入系统。所有配置通过 `Project Settings → Input → Game Input Plugin Settings` 的编辑器 UI 完成。

### 编辑器配置项

在 **Project Settings → Input → Game Input Plugin Settings** 中可配置：

| 设置项 | 说明 |
|---|---|
| `bProcessGamepad` | 启用标准游戏手柄处理（默认开启） |
| `bProcessKeyboard` | 启用键盘处理（Windows 上建议关闭，避免与 WindowsApplication 重复） |
| `bProcessMouse` | 启用鼠标处理（Windows 上建议关闭） |
| `bProcessController` | 启用通用控制器处理（需要显式设备配置） |
| `bProcessRawInput` | 启用原始设备报告处理（需要显式设备配置） |
| `bProcessRacingWheel` | 启用方向盘处理（实验性） |
| `bProcessFlightStick` | 启用飞行摇杆处理（实验性） |
| `bProcessArcadeStick` | 启用街机摇杆处理（实验性） |
| `bProcessSensors` | 启用传感器处理（实验性） |
| `DeviceConfigurations` | 自定义设备配置数组（按 VendorId/ProductId 匹配） |
| `DevicesToIgnore` | 完全忽略的设备列表 |

## C++ 用法

### 头文件引入

```cpp
#include "IGameInputDeviceInterface.h"
#include "GameInputBaseModule.h"
#include "GameInputDeveloperSettings.h"
#include "GameInputDeviceContainer.h"
#include "GameInputKeyTypes.h"
#include "GameInputUtils.h"
```

### 基本用法：获取 GameInput 实例

```cpp
// Source/Engine/Plugins/Runtime/GameInput/Source/GameInputBase/Public/GameInputBaseModule.h

#include "GameInputBaseModule.h"

if (FGameInputBaseModule::IsAvailable())
{
    // 获取模块引用
    FGameInputBaseModule& GameInputModule = FGameInputBaseModule::Get();
    
    // 获取底层 IGameInput 接口（需要 #if GAME_INPUT_SUPPORT）
    IGameInput* GameInput = FGameInputBaseModule::GetGameInput();
    
    // 监听 GameInput 对象创建
    GameInputModule.OnGameInputCreation.AddLambda([](IGameInput* InGameInput)
    {
        // GameInput 已初始化，可以开始使用
    });
}
```

### 基本用法：自定义设备处理器

```cpp
// 基于 Source/.../Public/Processors/IGameInputDeviceProcessor.h

#include "Processors/IGameInputDeviceProcessor.h"

class FMyCustomDeviceProcessor : public IGameInputDeviceProcessor
{
protected:
    // 声明支持的输入类型
    virtual GameInputKind GetSupportedReadingKind() const override
    {
        return GameInputKindController;
    }
    
    // 处理输入读数
    virtual bool ProcessInput(const FGameInputEventParams& Params) override
    {
        if (!Params.Reading)
        {
            return false;
        }
        
        // 获取设备信息
        const GameInputDeviceInfo* Info = Params.GetDeviceInfo();
        
        // 读取控制器状态
        GameInputGamepadState GamepadState;
        if (Params.Reading->GetGamepadState(&GamepadState))
        {
            // 处理按钮状态...
            return true;
        }
        return false;
    }
    
    // 每帧结束时调用一次，适合处理模拟轴（避免多读数累积）
    virtual bool PostProcessInput(const FGameInputEventParams& Params) override
    {
        // 处理模拟输入，确保值在 [-1.0, +1.0] 范围内
        return false;
    }
    
    // 清除输入状态
    virtual void ClearState(const FGameInputEventParams& Params) override
    {
        // 将所有相关 FKey 值重置为 0
    }
};
```

### 进阶用法：配置自定义设备

```cpp
// 基于 Source/.../Public/GameInputDeveloperSettings.h

#include "GameInputDeveloperSettings.h"

// 1. 查询设备配置
const UGameInputDeveloperSettings* Settings = GetDefault<UGameInputDeveloperSettings>();

// 2. 根据设备信息查找配置
const GameInputDeviceInfo* Info = GetDeviceInfo(Device);
const FGameInputDeviceConfiguration* Config = Settings->FindDeviceConfiguration(Info);

if (Config)
{
    // 配置中定义了按键映射、轴映射、原始报告映射等
    bool bProcessButtons = Config->bProcessControllerButtons;
    const TMap<uint32, FName>& ButtonMap = Config->ControllerButtonMappingData;
    const TMap<uint32, FGameInputControllerAxisData>& AxisMap = Config->ControllerAxisMappingData;
}

// 3. 创建自定义设备标识符
FGameInputDeviceIdentifier MyDeviceId;
MyDeviceId.VendorId = 0x045E;  // Microsoft
MyDeviceId.ProductId = 0x028E; // Xbox 360 Controller
```

### 进阶用法：平台设置与设备族过滤

```cpp
// 基于 Source/.../Public/GameInputDeveloperSettings.h

// 获取平台特定设置
UGameInputPlatformSettings* PlatformSettings = UGameInputPlatformSettings::Get();

bool bShouldProcessGamepad = PlatformSettings->bProcessGamepad;
bool bShouldProcessRawInput = PlatformSettings->bProcessRawInput;
bool bRequireExplicitConfig = PlatformSettings->bSpecialDevicesRequireExplicitDeviceConfiguration;

// 设备族过滤（位掩码）
uint32 SupportedFamilies = Settings->SupportedDeviceFamilies;
bool bSupportHID = (SupportedFamilies & static_cast<uint32>(EGameInputDeviceFamily::Hid)) != 0;
bool bSupportXboxOne = (SupportedFamilies & static_cast<uint32>(EGameInputDeviceFamily::XboxOne)) != 0;
```

## Demo 示例

### 最小自定义设备处理器

```cpp
// MyGameInputProcessor.h
#pragma once

#include "Processors/IGameInputDeviceProcessor.h"
#include "GameInputBaseIncludes.h"

#if GAME_INPUT_SUPPORT

class FMyFlightControllerProcessor : public IGameInputDeviceProcessor
{
public:
    FMyFlightControllerProcessor();

protected:
    virtual bool ProcessInput(const FGameInputEventParams& Params) override;
    virtual bool PostProcessInput(const FGameInputEventParams& Params) override;
    virtual void ClearState(const FGameInputEventParams& Params) override;
    virtual GameInputKind GetSupportedReadingKind() const override;

private:
    GameInputFlightStickState PreviousState = {};
    int32 NumReadingsProcessedThisFrame = 0;
    static constexpr uint32 MaxSupportedButtons = 32;
    double RepeatTime[MaxSupportedButtons] = {};
};

#endif // GAME_INPUT_SUPPORT
```

```cpp
// MyGameInputProcessor.cpp
#include "MyGameInputProcessor.h"

#if GAME_INPUT_SUPPORT

FMyFlightControllerProcessor::FMyFlightControllerProcessor()
{
    for (uint32 i = 0; i < MaxSupportedButtons; ++i)
    {
        RepeatTime[i] = 0.0;
    }
}

GameInputKind FMyFlightControllerProcessor::GetSupportedReadingKind() const
{
    return GameInputKindFlightStick;
}

bool FMyFlightControllerProcessor::ProcessInput(const FGameInputEventParams& Params)
{
    if (!Params.Reading)
    {
        return false;
    }

    GameInputFlightStickState CurrentState;
    if (!Params.Reading->GetFlightStickState(&CurrentState))
    {
        return false;
    }

    // 处理按钮
    EvaluateButtonStates(
        Params,
        CurrentState.buttons,
        PreviousState.buttons,
        RepeatTime,
        /* UnrealButtonNameMap - 自定义映射 */ {},
        MaxSupportedButtons
    );

    // 处理摇杆轴（在 PostProcessInput 中统一处理模拟值）
    ++NumReadingsProcessedThisFrame;
    PreviousState = CurrentState;
    return true;
}

bool FMyFlightControllerProcessor::PostProcessInput(const FGameInputEventParams& Params)
{
    if (NumReadingsProcessedThisFrame <= 0)
    {
        return false;
    }

    // 使用最后一帧的读数处理模拟轴，避免多读数导致值累积超过 ±1.0
    const float Pitch = static_cast<float>(PreviousState.pitch) / 32767.0f;
    const float Roll = static_cast<float>(PreviousState.roll) / 32767.0f;
    const float Yaw = static_cast<float>(PreviousState.yaw) / 32767.0f;
    const float Throttle = static_cast<float>(PreviousState.throttle) / 32767.0f;

    // OnControllerAnalog 会自动处理死区和设备作用域
    // 调用方式参见 IGameInputDeviceProcessor 基类

    NumReadingsProcessedThisFrame = 0;
    return true;
}

void FMyFlightControllerProcessor::ClearState(const FGameInputEventParams& Params)
{
    FMemory::Memzero(RepeatTime, sizeof(RepeatTime));
    FMemory::Memzero(&PreviousState, sizeof(PreviousState));
    NumReadingsProcessedThisFrame = 0;
}

#endif // GAME_INPUT_SUPPORT
```

### 设备配置结构体定义

```cpp
// 基于 Source/.../Public/GameInputDeveloperSettings.h

// 配置一个自定义赛车方向盘的按键映射
FGameInputDeviceConfiguration WheelConfig;
WheelConfig.DeviceIdentifier.VendorId = 0x046D;   // Logitech
WheelConfig.DeviceIdentifier.ProductId = 0xC24F;   // G920
WheelConfig.bProcessControllerButtons = true;
WheelConfig.bProcessControllerAxis = true;

// 配置方向盘轴（死区、缩放、正负值打包）
FGameInputControllerAxisData SteerAxis;
SteerAxis.KeyName = "RacingWheel_Wheel";
SteerAxis.DeadZone = 7849.0f / 32768.0f;
SteerAxis.Scalar = 1.0f;
SteerAxis.bIsPackedPositveAndNegative = true; // 方向盘轴从 -1.0 到 +1.0
WheelConfig.ControllerAxisMappingData.Add(0, SteerAxis);

// 配置油门踏板
FGameInputControllerAxisData ThrottleAxis;
ThrottleAxis.KeyName = "RacingWheel_Throttle";
ThrottleAxis.DeadZone = 0.0f;
ThrottleAxis.Scalar = 1.0f;
ThrottleAxis.bIsPackedPositveAndNegative = false; // 踏板从 0.0 到 1.0
WheelConfig.ControllerAxisMappingData.Add(1, ThrottleAxis);
```

## 模块依赖

从 Build.cs 分析，使用者通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GameInputBase` | 核心运行时模块，包含所有设备接口和处理器 |
| `GameInputBaseEditor` | 编辑器模块，提供 Project Settings UI 和设备配置面板 |

**注意**：本插件默认禁用（`EnabledByDefault: false`），需要在 Plugins 面板手动启用或通过 `DefaultEngine.ini` 启用：

```ini
[/Script/Plugins.PluginManager]
GameInput=true
```

**系统依赖**：需要安装 [Microsoft GameInput Redistributable](https://aka.ms/gameinput)，仅支持 Win64 平台。插件内含 `GameInputWindowsLibrary` 外部模块包装 GameInput SDK 的 `GameInput.h`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器类型转换警告 |
| 2026-05-01 | `1fbba943` | [GameInput] Add haptic audio endpoint support via XAudio2. | 新增通过 WASAPI/XAudio2 驱动控制器触觉音频振动 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 格式 |
| 2026-04-02 | `a4559861` | UE_LOG -> UE_LOGF macro conversion for Game Input modules | GameInput 模块日志宏转换 |
| 2026-04-01 | `1afb0871` | [Input] Add a thread affinitiy for input for IInputDevice so that we can specify which input modules | 为 IInputDevice 添加线程亲和性支持 |

### 维护评价

- **活跃维护中**：最近 6 个月内有多次功能性更新（触觉音频支持、线程亲和性改进）
- **持续演进**：从创建至今约 1.5 年，仍在积极开发新功能
- **实验性功能**：传感器、方向盘、飞行摇杆、街机摇杆处理器仍标记为实验性
- **已知限制**：仅支持 Win64；Haptic 支持同时只追踪一个控制器的音频端点；需要外部安装 GameInput Redistributable
- **推荐使用**：如果你的项目面向 Windows/Xbox 平台且需要统一输入管理，推荐使用。注意需手动启用，且与 XInput/WinDualShock 等模块存在功能重叠，启用前应禁用其他输入插件以避免重复事件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameInput)
- [Microsoft GameInput 文档](https://learn.microsoft.com/en-us/gaming/gdk/_content/gc/input/overviews/input-overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameInput/Tests)