# Windows RawInput

> RawInput provides an interface to receive input from Flight Sticks, Steering Wheels, and other non-XInput supported devices in Windows.

| 属性 | 值 |
|---|---|
| 中文名 | 原始输入 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RawInput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-07-05 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RawInput) | |

## 用途

RawInput 插件是 UE5 在 **Windows 平台**上接收非 XInput 标准游戏控制器（如飞行摇杆、方向盘、节流阀、脚踏板等）输入的官方解决方案。它绕过 XInput 框架，直接使用 Windows Raw Input API 读取 HID 设备数据，并提供统一的设备注册、按钮/轴绑定、轴反转与偏移等功能，同时暴露蓝图的 `GetRegisteredDevices` 节点便于运行时设备枚举。

该插件解决了标准 Gamepad 接口无法支持大量专业 HID 外设的问题，是模拟飞行、赛车、专业控制台等场景的必备组件。

## 使用场景

- 制作 **模拟飞行** 游戏 → 通过 RawInput 读取油门、方向舵、各种开关按钮
- 需要 **赛车方向盘** 支持 → 直接读取方向盘力反馈和 900° 旋转角度
- 连接 **工业控制杆** 或 **自定义 USB 控制器** → 利用 RawInput 兼容任意符合 HID 标准的设备
- 开箱不支持的手柄 → 有些手柄使用私有协议，XInput 无法识别，RawInput 可捕获原始 HID 报告

## 蓝图用法

### 核心节点

通过 `RawInputFunctionLibrary` 提供以下蓝图可调用函数：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Registered Devices` | 返回当前系统上已连接的所有 RawInput 设备信息（包括供应商 ID、产品 ID、物理设备句柄等） | `URawInputFunctionLibrary` |

**注意**：该节点为静态函数，直接由蓝图表调用，无需特定 Actor 组件。

### 使用示例（蓝图）

1. 在蓝图中拖入 **Get Registered Devices** 节点，得到 `FRawInputDeviceEntry` 数组。
2. 遍历数组，读取每个设备的 `VendorID` / `ProductID`，与实际设备匹配。
3. 根据匹配结果在 **Project Settings → RawInput** 中配置该设备的轴和按钮属性（映射到引擎标准按键）。
4. 运行时设备会自动将 HID 报告转换为对应的 `FKey` 输入，可以直接在事件图表中使用（如通过 Enhanced Input 或传统绑定）。

> 提示：必须先启用插件（Edit → Plugins → 搜 RawInput → 勾选启用）并在项目设置中配置设备映射。

## C++ 用法

### 头文件引入

```cpp
#include "RawInput.h"
#include "Windows/RawInputWindows.h"     // Windows 平台特有接口
#include "RawInputFunctionLibrary.h"     // 蓝图函数库（可选）
```

### 基本用法

在自定义模块（如 GameModule）或 PlayerController 中获取 RawInput 模块并注册设备。

```cpp
// 获取 RawInput 插件实例（IInputDeviceModule 子类）
IRawInput* RawInput = static_cast<IRawInput*>(FModuleManager::Get().GetModuleChecked<IInputDeviceModule>("RawInput")->CreateInputDevice(MessageHandler).Get());
```

或者更常用的方式是通过 **IInputDeviceModule** 的静态方法：

```cpp
// 在 .h 中定义
TSharedPtr<IRawInput> RawInputDevice;

// 在 .cpp 的 Initialize 中
RawInputDevice = StaticCastSharedPtr<IRawInput>(FModuleManager::LoadModuleChecked<IInputDeviceModule>("RawInput").CreateInputDevice(MessageHandler));
```

注册设备示例（来自 `FRawInputWindows` 的用法）：

```cpp
// 查询当前连接的所有 RawInput 设备
RawInputDevice->QueryConnectedDevices();

// 假设我们想要注册第一个设备（设备类型、标志、设备 ID、用途页、句柄）
// 实际应用中可从 QueryConnectedDevices 结果中获取这些值
int32 DeviceHandle = RawInputDevice->RegisterInputDevice(RIM_TYPEHID, 0, 0x046D, 1, nullptr);

// 绑定按钮 1～4 到自定义按键名称
RawInputDevice->BindButtonForDevice(DeviceHandle, "MyButton_1", 0);
RawInputDevice->BindButtonForDevice(DeviceHandle, "MyButton_2", 1);
RawInputDevice->BindButtonForDevice(DeviceHandle, "MyButton_3", 2);
RawInputDevice->BindButtonForDevice(DeviceHandle, "MyButton_4", 3);

// 绑定轴 1（模拟油门） 到自定义轴
RawInputDevice->BindAnalogForDevice(DeviceHandle, "MyAxis_Throttle", 0);

// 设置轴反转（如油门反向）
RawInputDevice->SetAnalogAxisIsInverted(DeviceHandle, 0, true);

// 设置轴偏移（使 0～1 范围变为 -0.5～0.5）
RawInputDevice->SetAnalogAxisOffset(DeviceHandle, 0, -0.5f);
```

### 进阶用法

通过 `FRawInputDataDelegate` 处理原始 HID 数据包：

```cpp
// 在您的类中声明委托处理函数
bool OnRawInputData(int32 DataSize, const struct tagRAWINPUT* Data);

// 绑定委托
RawInputDevice->GetDataReceivedHandler().BindRaw(this, &YourClass::OnRawInputData);

// 实现（可手动解析 HID 报告，绕过预设绑定）
bool YourClass::OnRawInputData(int32 DataSize, const struct tagRAWINPUT* Data)
{
    // 检查 Data->header.dwType 等字段
    // 可从 Data->data.hid.bRawData 中读取原始字节
    return false;  // 返回 false 让系统继续按已有绑定处理；返回 true 则消耗该包
}
```

> 注意：`FRawInputDataDelegate` 定义在 `RawInput.h` 中，签名 `DECLARE_DELEGATE_RetVal_TwoParams(bool, FRawInputDataDelegate, int32, const struct tagRAWINPUT*)`。

## Demo 示例

以下是一个完整的、可编译的最小 C++ 示例，展示如何在自定义 GameInstance 中启用 RawInput 并打印设备信息。

### RawInputDeviceTester.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "RawInput.h"
#include "RawInputDeviceTester.generated.h"

UCLASS()
class URawInputDeviceTester : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void Shutdown() override;

private:
    TSharedPtr<IRawInput> RawInputDevice;
};
```

### RawInputDeviceTester.cpp

```cpp
#include "RawInputDeviceTester.h"
#include "RawInputFunctionLibrary.h"
#include "GenericPlatform/GenericApplicationMessageHandler.h"

void URawInputDeviceTester::Init()
{
    Super::Init();

    // 1. 创建消息处理器（用于接收输入事件）
    TSharedRef<FGenericApplicationMessageHandler> MessageHandler = MakeShared<FGenericApplicationMessageHandler>();

    // 2. 加载 RawInput 模块并创建设备
    IInputDeviceModule* RawInputModule = FModuleManager::LoadModulePtr<IInputDeviceModule>("RawInput");
    if (RawInputModule)
    {
        RawInputDevice = StaticCastSharedPtr<IRawInput>(RawInputModule->CreateInputDevice(MessageHandler));
        if (RawInputDevice.IsValid())
        {
            // 3. 查询已连接设备
            RawInputDevice->QueryConnectedDevices();

            // 4. 枚举已注册设备（实际可从 FRawInputWindows 内部获取，此处仅演示蓝图函数库）
            TArray<FRawInputDeviceEntry> Devices;
            URawInputFunctionLibrary::GetRegisteredDevices(Devices);

            UE_LOG(LogTemp, Log, TEXT("RawInput Device Tester: Found %d devices."), Devices.Num());
            for (const FRawInputDeviceEntry& Device : Devices)
            {
                UE_LOG(LogTemp, Log, TEXT("  Device: VendorID=0x%X, ProductID=0x%X, DeviceName=%s"),
                    Device.VendorID, Device.ProductID, *Device.DeviceName);
            }

            // 5. 注册第一个设备（实际应检查 VendorID/ProductID 匹配）
            if (Devices.Num() > 0)
            {
                int32 Handle = RawInputDevice->RegisterInputDevice(RIM_TYPEHID, 0, Devices[0].VendorID, 1, nullptr);
                RawInputDevice->BindButtonForDevice(Handle, "MyCustomBtn", 0);
                RawInputDevice->BindAnalogForDevice(Handle, "MyCustomAxis", 0);
            }
        }
    }
}

void URawInputDeviceTester::Shutdown()
{
    RawInputDevice.Reset();
    Super::Shutdown();
}
```

> **注意**：此示例假设 `URawInputFunctionLibrary::GetRegisteredDevices` 在 UE5.7 中可用。该函数已在 RawInputFunctionLibrary.h 中声明为静态蓝图可调用函数。实际使用时请确保已将该 GameInstance 设为项目默认。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InputDevice` | 提供 `IInputDeviceModule` 和 `IInputDevice` 基类，RawInput 计划派生自它们 |

其他均为标准模块（Core, CoreUObject, Engine, ApplicationCore, InputCore 等），已省略。

> 若要在您自己的模块中使用 RawInput 插件，请将 `RawInput` 添加到 `PublicDependencyModuleNames` 中，并将插件启用。

## 维护状态

### 近期更新

- 2024-01-25 f43fc1d 修复更多将 bool 参数改为 `EAllowShrinking` 的调用
- 2023-07-26 0ea286e [RawInput] 修复在 offscreen 模式下以 -game 启动时启用 RawInput 导致的崩溃
- 2022-11-10 db9d155 添加每平台输入设置，允许指定各平台可用的硬件输入设备
- 2022-10-21 610c467 更新内置插件的供应商链接为安全协议
- 2022-07-05 47968b5 更新 RawInput 使用新的 OnController 函数替代即将废弃的旧版本

### 维护评价

RawInput 插件于 UE5.0 早期（2022-07）创建，至今约 3 年。最近一年内（2024-01）仅有一次针对编译参数类型变更的小修复，功能性更新停留在 2022 年底。插件仍可正常工作于 UE5.7，且 Windows 平台 Raw Input API 本身稳定，无需频繁改动。但请注意：

- 插件默认**未启用**，需手动开启
- 仅支持 Windows 平台（Win64）
- 无官方文档，社区使用依赖于源码和少量示例
- 没有公开的专用测试用例（引擎内部有非公开测试）

**综合评价**：适合需要非 XInput 设备支持的专业项目，功能稳定，文档较少但 API 清晰。若项目长期维护且可能依赖该插件，建议确认后续引擎版本兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RawInput)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/raw-input-in-unreal-engine/)（UE5.7 官方文档 – RawInput）
- [蓝图函数库头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/RawInput/Source/RawInput/Public/RawInputFunctionLibrary.h)
- [Windows 实现](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/RawInput/Source/RawInput/Public/Windows/RawInputWindows.h)