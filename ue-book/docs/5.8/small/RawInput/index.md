# Windows RawInput

> RawInput provides an interface to receive input from Flight Sticks, Steering Wheels, and other non-XInput supported devices in Windows.

| 属性 | 值 |
|---|---|
| 中文名 | 原始输入 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RawInput` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RawInput) | |

## 用途

RawInput 插件为 UE 提供了 Windows 原始输入（Raw Input）API 的封装，用于接收 XInput 不支持的 HID 设备输入数据。典型场景包括飞行摇杆、方向盘、专业控制器等非标准游戏手柄设备。

该插件通过 Windows 的 `RegisterRawInputDevices` 和 `GetRawInputData` API 直接与 HID（Human Interface Device）驱动层交互，绕过 XInput 的限制。插件动态加载 `hid.dll`，读取设备的按钮（Buttons）和模拟轴（Analog Axes）数据，并将其映射为 UE 的输入系统事件（FKey）。

**注意**：此插件已在 5.8 版本标记为废弃（`DeprecatedEngineVersion: "5.8"`），官方推荐使用更新的 Game Input 实验性插件替代。

## 使用场景

- 你在开发赛车/飞行模拟游戏，需要支持罗技 G920 方向盘或飞行摇杆等专业外设
- 你的设备不被 XInput 识别（XInput 仅支持标准 Xbox 兼容手柄）
- 你需要读取 HID 设备的原始按钮和轴数据并映射到自定义输入事件
- 仅支持 Windows 平台（Win64）

## 蓝图用法

插件提供一个蓝图函数库和一组通过 Settings 配置的设备绑定机制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetRegisteredDevices` | 获取所有已注册的原始输入设备信息（Handle、VendorID、ProductID、DeviceName） | `URawInputFunctionLibrary` |

### 设备配置（项目设置）

设备绑定不通过蓝图节点动态设置，而是通过 **项目设置 → Input → RawInput** 中的 `DeviceConfigurations` 数组进行配置。每个配置项包含：

- **VendorID**：十六进制厂商 ID（如 `0x046D`），留空则匹配所有厂商
- **ProductID**：十六进制产品 ID（如 `0xC262`），留空则匹配所有产品
- **AxisProperties**：轴配置数组，每项可设置映射的 FKey、是否反转、是否为游戏摇杆轴（-1 到 1）、偏移量
- **ButtonProperties**：按钮配置数组，每项可设置映射的 FKey

### 使用示例（蓝图描述）

1. 在 `项目设置 → Input → RawInput` 中添加一条 `DeviceConfiguration`
2. 设置 `VendorID` 和 `ProductID` 匹配你的设备
3. 在 `AxisProperties` 中为每个轴指定要映射的输入键（如 `GenericUSBController_Axis1`）
4. 在 `ButtonProperties` 中为每个按钮指定要映射的输入键（如 `GenericUSBController_Button1`）
5. 在 Input Action/Axis 映射中使用这些键名即可接收输入
6. 蓝图中调用 `GetRegisteredDevices` 节点可查询当前已连接并注册的设备列表

## C++ 用法

### 头文件引入

```cpp
#include "RawInput.h"
#include "RawInputFunctionLibrary.h"
#include "RawInputSettings.h"
```

### 基本用法

通过模块获取 RawInput 设备实例并注册设备：

```cpp
#include "RawInput.h"

// 获取 RawInput 模块实例
FRawInputPlugin& RawInputPlugin = FRawInputPlugin::Get();

// 检查模块是否可用
if (FRawInputPlugin::IsAvailable())
{
    TSharedPtr<IRawInput>& RawInputDevice = RawInputPlugin.GetRawInputDevice();
    
    // 注册一个 HID 设备（通常由系统自动完成）
    // DeviceType: 设备类型, Flags: 标志位
    // DeviceID: HID Usage ID, PageID: HID Usage Page
    int32 Handle = RawInputDevice->RegisterInputDevice(DeviceType, Flags, DeviceID, PageID, nullptr);
}
```

### 进阶用法

绑定设备的按钮和轴到自定义输入事件，并设置轴属性：

```cpp
// 来源: Source/RawInput/Public/RawInput.h - IRawInput 接口
#include "RawInput.h"

FRawInputPlugin& RawInputPlugin = FRawInputPlugin::Get();
TSharedPtr<IRawInput>& Device = RawInputPlugin.GetRawInputDevice();

int32 DeviceHandle = /* 已注册设备的 Handle */;

// 绑定按钮 0 到自定义事件名
Device->BindButtonForDevice(DeviceHandle, FName("MyFlightStick_Trigger"), 0);

// 绑定轴 0 到自定义事件名
Device->BindAnalogForDevice(DeviceHandle, FName("MyFlightStick_XAxis"), 0);

// 设置轴反转
Device->SetAnalogAxisIsInverted(DeviceHandle, 0, true);

// 设置轴偏移量
Device->SetAnalogAxisOffset(DeviceHandle, 0, 0.1f);
```

查询已注册设备信息（蓝图/函数库方式）：

```cpp
#include "RawInputFunctionLibrary.h"

// 获取所有已注册设备
TArray<FRegisteredDeviceInfo> Devices = URawInputFunctionLibrary::GetRegisteredDevices();

for (const FRegisteredDeviceInfo& Device : Devices)
{
    UE_LOG(LogTemp, Log, TEXT("Device: %s, Vendor: 0x%X, Product: 0x%X, Handle: %d"),
        *Device.DeviceName, Device.VendorID, Device.ProductID, Device.Handle);
}
```

## Demo 示例

一个最小的自定义输入处理示例，使用 RawInput 数据委托直接解析 HID 数据：

```cpp
// MyRawInputHandler.h
#pragma once

#include "CoreMinimal.h"
#include "RawInput.h"

class FMyRawInputHandler
{
public:
    void Setup();
    bool OnRawInputData(int32 DataSize, const tagRAWINPUT* Data);

private:
    FDelegateHandle DelegateHandle;
};
```

```cpp
// MyRawInputHandler.cpp
#include "MyRawInputHandler.h"
#include "RawInput.h"

void FMyRawInputHandler::Setup()
{
    if (!FRawInputPlugin::IsAvailable())
    {
        return;
    }

    TSharedPtr<IRawInput>& RawInputDevice = FRawInputPlugin::Get().GetRawInputDevice();

    // 绑定原始数据接收委托，用于手动解析 HID 数据
    DelegateHandle = RawInputDevice->GetDataReceivedHandler().BindRaw(
        this, &FMyRawInputHandler::OnRawInputData);
}

bool FMyRawInputHandler::OnRawInputData(int32 DataSize, const tagRAWINPUT* Data)
{
    // 返回 true 表示已处理该数据，阻止默认解析
    // 返回 false 则继续走默认的按键/轴映射逻辑
    if (Data && DataSize > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Received raw input data, size: %d"), DataSize);
        return false; // 让默认逻辑继续处理
    }
    return false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RawInput` | 无特殊依赖（仅标准 Core/Engine/Slate 等） |

插件仅在 Win64 平台编译，通过运行时动态加载 `hid.dll` 访问 HID API，无需额外模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |
| 2026-03-26 | `2cdca0c0` | [Input] FInputDeviceScope refactor and deprecation. | 输入设备作用域重构和废弃 |
| 2025-11-13 | `815ba42a` | Deprecate the Raw Input plugin in favor of the newer Game Input experimental plugin. | 正式废弃 Raw Input 插件，推荐使用 Game Input |
| 2025-11-13 | `fb8702ba` | [Backout] - CL47956511 | 回退一次变更 |

### 维护评价

**⚠️ 已废弃 — 不推荐新项目使用。**

该插件自 2016 年创建以来功能基本稳定，但在 2025-11-13 的提交中已被正式标记为废弃（`815ba42a`），官方推荐使用更新的 **Game Input** 实验性插件（Windows.Gaming.Input API）替代。`.uplugin` 中的 `DeprecatedEngineVersion: "5.8"` 也确认了这一点。

近期提交仅涉及日志宏迁移和格式修复等维护性改动，无功能性更新。虽然仍可使用，但预计将在未来版本中被移除。如果你正在开始新项目，应直接使用 Game Input 插件；如果已有项目依赖此插件，建议尽快迁移。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RawInput)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/raw-input-plugin-in-unreal-engine)