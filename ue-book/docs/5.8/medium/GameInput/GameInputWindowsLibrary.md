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

该插件集成了微软的 GameInput API，为 Windows 平台提供了一套统一的、高性能的输入系统接口。它旨在解决传统输入系统（如 XInput、Raw Input、DirectInput）碎片化的问题，为所有输入设备（包括 Xbox 手柄、键盘、鼠标、赛车方向盘、飞行摇杆等）提供单一、一致的访问方式。其核心价值在于简化了对多种输入设备的处理逻辑，并支持最新一代设备的高级特性（如触觉反馈、精确摇杆死区）。

## 使用场景

-   你正在开发一款 Windows 平台游戏，并希望获得对 Xbox 手柄和其他现代输入设备的最佳支持。
-   你需要统一处理来自键盘、鼠标和各种游戏手柄的输入，而不希望为每种设备编写不同的代码路径。
-   你希望使用比标准 XInput 更精确的摇杆输入数据（例如，更精细的死区控制）。
-   你的游戏需要支持像赛车方向盘、飞行摇杆这类专业输入设备的高级轴和按钮映射。

## 蓝图用法

从提供的源码分析看，核心功能主要由 C++ 层实现。插件提供了对底层 GameInput API 类型的封装，这些类型主要在 C++ 中使用。目前没有从该插件的源码中找到直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 节点。蓝图层面的使用可能需要通过其他插件（如 Enhanced Input）或自定义的蓝图函数库进行桥接。

## C++ 用法

### 头文件引入

```cpp
#include "GameInput.h"
```

### 基本用法

GameInput API 的核心是识别和获取不同类型的输入设备及其数据。`GameInput.h` 中定义了大量枚举和常量，用于描述设备类型、能力、按钮和轴。

```cpp
// 判断一个设备是否是游戏手柄 (来源: ThirdParty/GameInput.h)
GameInput::v3::GameInputKind DeviceKind = GameInput::v3::GameInputKindGamepad;

// 检查游戏手柄是否支持标准布局 (包含 A, B, X, Y, 十字键, 肩键, 扳机, 摇杆)
GameInput::v3::GameInputGamepadButtons RequiredButtons = GameInput::v3::GameInputGamepadLayoutStandard;

// 使用标志位枚举检查设备是否支持特定轴（例如左侧扳机）
bool bHasLeftTrigger = (DeviceKind & GameInput::v3::GameInputKindController) != 0;
bool bHasLeftTriggerAxis = (GameInput::v3::GameInputGamepadAxesNone & GameInput::v3::GameInputGamepadLeftTrigger) != 0;
```

### 进阶用法

可以组合使用枚举和常量来精确描述设备需求或查询设备能力。

```cpp
// 描述一个需要标准摇杆和方向键，但不一定有背板的设备
GameInput::v3::GameInputGamepadButtons DesiredCapabilities = 
    GameInput::v3::GameInputGamepadModuleDpad |
    GameInput::v3::GameInputGamepadModuleThumbsticks;

// 检查一个设备是否属于‘精英’手柄布局（包含4个背板）
GameInput::v3::GameInputGamepadButtons DeviceButtons = ...; // 从设备获取
bool bIsEliteController = (DeviceButtons & GameInput::v3::GameInputGamepadLayoutElite) == GameInput::v3::GameInputGamepadLayoutElite;

// 处理设备连接状态变化
GameInput::v3::GameInputDeviceStatus StatusFlags = GameInput::v3::GameInputDeviceConnected;
```

## Demo 示例

以下是一个简单的设备管理器类头文件，展示了如何使用 GameInput 头文件中定义的类型进行设备查询。

```cpp
// GameInputDeviceManager.h
#pragma once
#include "CoreMinimal.h"
#include "GameInput.h"

class FGameInputDeviceManager
{
public:
    /** 检查给定的设备能力是否支持标准游戏手柄布局 */
    bool SupportsStandardGamepad(GameInput::v3::GameInputGamepadButtons InButtons) const
    {
        return (InButtons & GameInput::v3::GameInputGamepadLayoutStandard) == GameInput::v3::GameInputGamepadLayoutStandard;
    }

    /** 获取设备类型的字符串描述 */
    FString GetDeviceKindString(GameInput::v3::GameInputKind InKind) const
    {
        if (InKind & GameInput::v3::GameInputKindGamepad)
        {
            return TEXT("Gamepad");
        }
        else if (InKind & GameInput::v3::GameInputKindKeyboard)
        {
            return TEXT("Keyboard");
        }
        else if (InKind & GameInput::v3::GameInputKindMouse)
        {
            return TEXT("Mouse");
        }
        // ... 其他设备类型判断
        return TEXT("Unknown");
    }
};
```

```cpp
// GameInputDeviceManager.cpp
#include "GameInputDeviceManager.h"

// 示例：在某个地方使用设备管理器
void ExampleUsage()
{
    FGameInputDeviceManager DeviceManager;
    
    // 模拟从一个设备获取到的按钮能力
    GameInput::v3::GameInputGamepadButtons SomeControllerButtons = 
        GameInput::v3::GameInputGamepadA | 
        GameInput::v3::GameInputGamepadB | 
        GameInput::v3::GameInputGamepadModuleThumbsticks;

    if (DeviceManager.SupportsStandardGamepad(SomeControllerButtons))
    {
        UE_LOG(LogTemp, Log, TEXT("This controller supports the standard gamepad layout."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Controller does not support standard layout."));
    }
}
```

## 模块依赖

该插件本身是对平台底层 API 的封装，没有特殊的运行时模块依赖。

| 模块 | 用途 |
|---|---|
| `InputCore` | 引擎核心输入系统模块，用于与引擎输入抽象层集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 解决编译器兼容性问题，消除类型转换警告。 |
| 2026-05-01 | `1fbba943` | [GameInput] Add haptic audio endpoint support via XAudio2. | 新增通过 XAudio2 实现触觉音频端点的功能支持。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移为 UE_LOGF。 |
| 2026-04-02 | `a4559861` | UE_LOG -> UE_LOGF macro conversion for Game Input modules | 继续将 Game Input 模块中的日志宏转换为 UE_LOGF。 |
| 2026-04-01 | `1afb0871` | [Input] Add a thread affinitiy for input for IInputDevice so that we can specify which input modules | 为 IInputDevice 接口添加线程亲和性，允许指定输入模块的处理线程。 |

### 维护评价

**活跃维护**。该插件创建于 2024 年初，至今仍在持续更新。最近的提交（2026年5月）显示其正在积极添加新功能（如触觉音频支持）并进行代码现代化（迁移到 UE_LOGF）。它解决了特定平台（Windows）的输入需求，且由 Epic 和微软合作支持，预计会持续维护。**推荐**给需要在 Windows 平台上为 Xbox 生态系统优化输入体验的开发者使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameInput)
-   [官方文档](https://learn.microsoft.com/en-us/gaming/gdk/_content/gc/input/overviews/input-overview) (微软 GameInput API 概述)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/GameInput) (引擎内置测试，如有)