# Game Input Base

> GameInput is a next-generation input API that exposes input devices of all kinds through a single consistent interface.

| 属性 | 值 |
|---|---|
| 分类 | Input Devices |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | GameInputBase (Runtime), GameInputBaseEditor (Editor) |
| 创建时间 | 2024-02-12 |
| 年龄标签 | 🆕(≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameInput) | |

## 用途

GameInput 是微软推出的下一代统一输入 API（属于 GDK / Windows.Gaming.Input 体系），UE5 通过此 plugin 将其集成到引擎的 `IInputDevice` 架构中。它的核心价值在于：

- **统一设备抽象**：手柄、键盘、鼠标、触摸屏、赛车方向盘、飞行摇杆、街机摇杆、以及任意 Raw HID 设备，全部通过同一个 `IGameInput` COM 接口枚举和读取，无需分别对接 XInput、DirectInput、WinRT 等多套 API。
- **原生支持 Xbox 生态**：Xbox 主机（GDK 平台）本身就使用 GameInput 作为首选输入 API，此 plugin 让 PC 和主机共享同一套输入管线。
- **支持"特殊"外设**：通过 `GameInputKindController` + `GameInputKindRawDeviceReport` 双机制，可以为吉他控制器的摇杆、赛车方向盘的自定义换挡器等非标准输入编写自定义映射，全部在 Project Settings 中配置，无需写代码。

### 与 XInput / Enhanced Input 的关系

| | GameInput | XInput | Enhanced Input |
|---|---|---|---|
| 层级 | 底层设备驱动接口 | 底层设备驱动接口 | 上层输入映射框架 |
| 设备范围 | 所有 HID 设备 | 仅 Xbox 兼容手柄 | 任意 IInputDevice 的输出 |
| 平台 | Win64 + Xbox GDK | 仅 Win64 | 全平台 |

三者并不冲突：GameInput/XInput 负责"从硬件读取原始状态"，Enhanced Input 负责"把按键映射为 Gameplay Action"。启用 GameInput 后，它会取代 XInput 成为手柄的底层驱动，Enhanced Input 照常工作。

## 使用场景

- 你在开发 Xbox + PC 跨平台游戏，需要统一输入管线 → 启用 GameInput，禁用 XInput
- 你的游戏需要支持赛车方向盘、飞行摇杆等"特殊"外设 → 使用 GameInput 的 Controller + Raw Report 配置
- 你需要为非标准 HID 设备（如自定义 MIDI 控制器）做按键映射 → 使用 `FGameInputDeviceConfiguration` + `RawReportMappingData`
- 你只需要标准手柄/键鼠，且仅发布 PC → 可以继续用 XInput，不必启用此 plugin

## 蓝图用法

此 plugin 没有暴露任何 `BlueprintCallable` 函数。它完全工作在底层 `IInputDevice` 层面，通过 UE 的标准输入系统（`FKey`、Enhanced Input 等）向上层传递事件。

所有配置均通过 **Project Settings → Input → Game Input Plugin Settings** 完成。

### 配置界面

在 Project Settings 中找到 **Game Input Plugin Settings**（即 `UGameInputDeveloperSettings`），可配置：

| 设置项 | 说明 |
|---|---|
| **DeviceConfigurations** | 为特定 VendorId/ProductId 设备配置按键映射 |
| **bDoNotProcessDuplicateCapabilitiesForSingleUser** | 同一用户的多个设备是否只处理一个（推荐开启） |

在 **Platform Options** 下（`UGameInputPlatformSettings`），按平台配置：

| 设置项 | 默认值 | 说明 |
|---|---|---|
| bProcessGamepad | true | 是否处理标准手柄 |
| bProcessKeyboard | true | 是否处理键盘（PC 上建议关闭，由 WindowsApplication 处理） |
| bProcessMouse | true | 是否处理鼠标（PC 上建议关闭） |
| bProcessController | false | 是否处理第三方控制器（需配置 DeviceConfigurations） |
| bProcessRawInput | false | 是否处理 Raw HID 报告（需配置 DeviceConfigurations） |
| bProcessRacingWheel | false | 是否处理赛车方向盘（实验性） |
| bProcessArcadeStick | false | 是否处理街机摇杆（实验性） |
| bProcessFlightStick | false | 是否处理飞行摇杆（实验性） |
| bSpecialDevicesRequireExplicitDeviceConfiguration | true | Controller/Raw 设备是否必须在 DeviceConfigurations 中注册 |

## C++ 用法

### 头文件引入

```cpp
#include "GameInputBaseModule.h"        // 模块入口
#include "GameInputDeveloperSettings.h" // 开发者设置
#include "GameInputUtils.h"             // 工具函数
```

### 基本用法：访问 IGameInput 实例

```cpp
// 来源: GameInputBaseModule.h
if (FGameInputBaseModule::IsAvailable())
{
    IGameInput* GameInput = FGameInputBaseModule::GetGameInput();
    // 可用于创建自己的 IGameInputReading 等
}
```

### 查询设备配置

```cpp
// 来源: GameInputDeveloperSettings.h
const UGameInputDeveloperSettings* Settings = GetDefault<UGameInputDeveloperSettings>();
const FGameInputDeviceIdentifier ID(VendorId, ProductId);
const FGameInputDeviceConfiguration* Config = Settings->FindDeviceConfiguration(ID);
if (Config)
{
    // 读取该设备的按键映射等
}
```

### 监听 GameInput 创建

```cpp
// 来源: GameInputBaseModule.h
FGameInputBaseModule& Module = FGameInputBaseModule::Get();
Module.OnGameInputCreation.AddLambda([](IGameInput* GameInput)
{
    // GameInput COM 对象已创建，可在此注册自定义回调
});
```

### 继承 IGameInputDeviceInterface（平台扩展）

```cpp
// 来源: IGameInputDeviceInterface.h
// 如果你需要为新平台实现 GameInput，继承此类：
class FMyPlatformGameInputDevice : public IGameInputDeviceInterface
{
public:
    using IGameInputDeviceInterface::IGameInputDeviceInterface;

protected:
    virtual void HandleDeviceConnected(IGameInputDevice* Device, uint64 Timestamp) override;
    virtual void HandleDeviceDisconnected(IGameInputDevice* Device, uint64 Timestamp) override;
    virtual FGameInputDeviceContainer* CreateDeviceData(IGameInputDevice* InDevice) override;
};
```

### 自定义设备处理器

```cpp
// 来源: GameInputDeviceProcessor.h
// 如果需要处理新的 GameInputKind，继承 IGameInputDeviceProcessor：
class FMyCustomProcessor : public IGameInputDeviceProcessor
{
protected:
    virtual bool ProcessInput(const FGameInputEventParams& Params) override;
    virtual void ClearState(const FGameInputEventParams& Params) override;
    virtual GameInputKind GetSupportedReadingKind() const override;
};
```

## Demo 示例

### 最小集成示例：启用 GameInput 并读取手柄

```cpp
// MyGame.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "GameInputBase",
    "InputCore",
    "Engine"
});

// MyInputListener.h
#pragma once
#include "GameInputBaseModule.h"
#include "GameInputDeveloperSettings.h"

class FMyInputListener
{
public:
    void Init()
    {
        if (!FGameInputBaseModule::IsAvailable()) return;

        IGameInput* GI = FGameInputBaseModule::GetGameInput();
        if (!GI) return;

        // 注册设备连接回调
        GI->RegisterDeviceCallback(
            nullptr,  // 所有设备
            GameInputKindGamepad,
            GameInputDeviceStatusAny,
            OnDeviceStatusChanged,
            this,
            &CallbackToken
        );
    }

    static void CALLBACK OnDeviceStatusChanged(
        GameInputCallbackToken Token,
        IGameInput* GameInput,
        IGameInputDevice* Device,
        uint64 Timestamp,
        GameInputDeviceStatus CurrentStatus,
        GameInputDeviceStatus PreviousStatus)
    {
        // 处理设备连接/断开
    }

private:
    GameInputCallbackToken CallbackToken = 0;
};
```

> **注意**：此 plugin 没有官方测试用例。使用时需注意 `GAME_INPUT_SUPPORT` 宏仅在 Win64 x64 平台为 1。

## 模块依赖

从 `GameInputBase.build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `ApplicationCore` | 平台应用抽象层 |
| `SlateCore` | Slate UI 核心（输入事件分发） |
| `Slate` | Slate UI 框架 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统核心（FKey、FInputDeviceId 等） |
| `InputDevice` | IInputDevice 接口定义 |
| `CoreUObject` | UObject 系统 |
| `DeveloperSettings` | UDeveloperSettings 基类 |
| `GameInputWindowsLibrary` | 微软 GameInput SDK 静态库（仅 Win64 x64） |

你的模块要使用此 plugin，至少需要依赖 `GameInputBase`。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-07 | `f44fbf45dc71` | Add cvar for enabling touch input correction in FGameInputTouchDeviceProcessor | 新增 CVar 控制触摸输入修正，表明触摸功能仍在活跃迭代 |
| 2025-07-16 | `3619277a7899` | Make sure Application correctly has key modifier state updated before OnKeyDown/OnKeyUp | 修复键盘修饰键（Shift/Ctrl/Alt）状态同步问题 |
| 2025-07-12 | `c025768499a7` | Run UnrealCodeFixup to add #include UE_INLINE_GENERATED_CPP_BY_NAME | 批量代码现代化，非功能性改动 |

### 维护评价

- **创建时间**：2024-02-12，约 2 年历史，属于较新的 plugin
- **更新频率**：2025 年 7-8 月连续有功能性更新，处于**活跃维护**状态
- **平台限制**：仅 Win64 x64（主机平台通过各自的 GDK 子模块支持）
- **EnabledByDefault=false**：需要手动在 Plugins 面板中启用
- **实验性功能**：赛车方向盘、街机摇杆、飞行摇杆标记为 Experimental
- **API 版本**：支持 GameInput v0（GDK）和 v1，v1 不支持 Raw/Touch/DeviceStatus
- **推荐**：如果你的目标平台包含 Xbox 或需要支持非标准外设，推荐启用；纯 PC 标准手柄场景可继续用 XInput

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameInput)
- [官方文档](https://learn.microsoft.com/en-us/gaming/gdk/_content/gc/input/overviews/input-overview)（微软 GameInput 文档）
- 测试用例：此 plugin 无独立测试用例
