# Live Link Device Framework

> Provides interfaces and base classes for implementing Live Link Hub devices

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | 否 |
| 模块 | LiveLinkDevice (Editor) |
| 创建时间 | 2024-12-18 |
| 年龄标签 | 🆕 (~1.4年) |
| 实验性 | ✅ `IsExperimentalVersion: true` |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkDevice) | |

## 用途

LiveLinkDevice 是一个 **框架级插件**，为 Live Link Hub 应用提供设备管理的抽象层。它本身不包含任何具体的设备实现，而是定义了：

1. **设备基类** (`ULiveLinkDevice`) — 所有 Live Link 设备的抽象基类
2. **能力系统** (`ULiveLinkDeviceCapability`) — 基于 UInterface 的能力接口，允许设备声明式地组合功能
3. **设备子系统** (`ULiveLinkDeviceSubsystem`) — 统一的设备注册、创建、查询和生命周期管理
4. **UI 框架** — 为 Live Link Hub 提供设备列表和详情面板的 Tab 注册

这个插件解决的核心问题是：Live Link Hub 需要管理多种不同类型的硬件/软件设备（动作捕捉、面部追踪等），每种设备有不同的能力和配置。LiveLinkDevice 提供了统一的接口和管理机制，使得具体的设备实现（如 LiveLinkFace、LiveLinkOpenXR 等）可以以插件的形式接入。

## 使用场景

- 你正在开发一个 Live Link 设备插件（如自定义动作捕捉设备驱动）→ 继承 `ULiveLinkDevice` + 组合所需 Capability 接口
- 你需要管理多个 Live Link 设备的连接和录制状态 → 使用 `ULiveLinkDeviceSubsystem` 统一管理
- 你在开发 Live Link Hub 的自定义 UI 扩展 → 通过设备表和能力系统获取设备信息
- 你需要在会话间持久化设备配置 → 通过 Session ExtraData 机制自动保存/恢复

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDisplayName` | 获取设备的人类可读名称 | `ULiveLinkDevice` |
| `GetDeviceHealth` | 获取设备健康状态（Nominal/Good/Info/Warning/Error） | `ULiveLinkDevice` |
| `GetHealthText` | 获取健康状态的说明文字 | `ULiveLinkDevice` |
| `GetConnectionStatus` | 获取连接状态（Disconnected/Connecting/Connected/Disconnecting） | `ILiveLinkDeviceCapability_Connection` |
| `GetHardwareId` | 获取硬件标识（序列号、网络端点等） | `ILiveLinkDeviceCapability_Connection` |
| `Connect` | 尝试建立连接 | `ILiveLinkDeviceCapability_Connection` |
| `Disconnect` | 尝试断开连接 | `ILiveLinkDeviceCapability_Connection` |
| `SetHardwareId` | 设置硬件标识 | `ILiveLinkDeviceCapability_Connection` |
| `StartRecording` | 开始录制 | `ILiveLinkDeviceCapability_Recording` |
| `StopRecording` | 停止录制 | `ILiveLinkDeviceCapability_Recording` |
| `IsRecording` | 查询是否正在录制 | `ILiveLinkDeviceCapability_Recording` |
| `GetDevicesByClass` | 按设备类获取已注册设备列表 | `ULiveLinkDeviceSubsystem` |
| `GetDevicesByCapability` | 按能力接口获取已注册设备列表 | `ULiveLinkDeviceSubsystem` |

### 连接状态委托

| 委托 | 说明 | 所在类 |
|---|---|---|
| `ConnectionChangedDynamic` | 连接状态变化时触发（蓝图可用，仅游戏线程） | `UConnectionDelegate` |
| `GetConnectionDelegate` | 获取连接委托对象 | `ILiveLinkDeviceCapability_Connection` |

### 使用示例（蓝图描述）

**查询所有支持连接的设备并断开：**
1. 调用 `ULiveLinkDeviceSubsystem::GetDevicesByCapability`（传入 `ULiveLinkDeviceCapability_Connection` 类），获取设备数组
2. For Each 遍历，Cast 到 `ILiveLinkDeviceCapability_Connection`
3. 调用 `Disconnect` 节点

**监听连接状态变化：**
1. 获取设备后，调用 `GetConnectionDelegate` 获取 `UConnectionDelegate` 对象
2. 绑定 `ConnectionChangedDynamic` 委托，在回调中根据 `ELiveLinkDeviceConnectionStatus` 更新 UI

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkDevice.h"
#include "LiveLinkDeviceCapability.h"
#include "LiveLinkDeviceCapability_Connection.h"
#include "LiveLinkDeviceCapability_Recording.h"
#include "LiveLinkDeviceSubsystem.h"
```

### 创建自定义设备

以下示例展示如何创建一个实现连接能力的自定义设备：

```cpp
// MyDevice.h
#pragma once

#include "LiveLinkDevice.h"
#include "LiveLinkDeviceCapability_Connection.h"
#include "MyDevice.generated.h"

// 自定义设备设置
UCLASS()
class MYMODULE_API UMyDeviceSettings : public ULiveLinkDeviceSettings
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Connection")
    FString HostAddress = TEXT("127.0.0.1");

    UPROPERTY(EditAnywhere, Category = "Connection")
    int32 Port = 12345;
};

// 自定义设备，实现连接能力
UCLASS(Blueprintable)
class MYMODULE_API UMyDevice : public ULiveLinkDevice
    , public ILiveLinkDeviceCapability_Connection
{
    GENERATED_BODY()

public:
    // ULiveLinkDevice 接口
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override
    {
        return UMyDeviceSettings::StaticClass();
    }

    virtual FText GetDisplayName() const override
    {
        return FText::FromString(TEXT("My Custom Device"));
    }

    virtual EDeviceHealth GetDeviceHealth() const override
    {
        return EDeviceHealth::Nominal;
    }

    virtual FText GetHealthText() const override
    {
        return FText::FromString(TEXT("OK"));
    }

    // ILiveLinkDeviceCapability_Connection 接口
    virtual ELiveLinkDeviceConnectionStatus GetConnectionStatus_Implementation() const override
    {
        return CurrentStatus;
    }

    virtual FString GetHardwareId_Implementation() const override
    {
        return HardwareId;
    }

    virtual bool Connect_Implementation() override
    {
        // 实现连接逻辑
        SetConnectionStatus(ELiveLinkDeviceConnectionStatus::Connecting);
        // ... 连接代码 ...
        SetConnectionStatus(ELiveLinkDeviceConnectionStatus::Connected);
        return true;
    }

    virtual bool Disconnect_Implementation() override
    {
        SetConnectionStatus(ELiveLinkDeviceConnectionStatus::Disconnecting);
        // ... 断开代码 ...
        SetConnectionStatus(ELiveLinkDeviceConnectionStatus::Disconnected);
        return true;
    }

protected:
    ELiveLinkDeviceConnectionStatus CurrentStatus = ELiveLinkDeviceConnectionStatus::Disconnected;
    FString HardwareId;
};
```

### 注册和查询设备（来源: `LiveLinkDevice.spec.cpp`）

```cpp
// 获取设备子系统
ULiveLinkDeviceSubsystem* Subsystem = GEngine->GetEngineSubsystem<ULiveLinkDeviceSubsystem>();

// 创建设备（返回 TValueOrError）
ULiveLinkDeviceSubsystem::FCreateResult CreateResult =
    Subsystem->CreateDeviceOfClass(UMyDevice::StaticClass());

if (CreateResult.HasValue())
{
    FGuid DeviceId = CreateResult.GetValue().DeviceId;
    UMyDevice* Device = CastChecked<UMyDevice>(CreateResult.GetValue().Device);

    // 通过基类指针查询能力
    ULiveLinkDevice* BaseDevice = Device;
    if (BaseDevice->Implements<ULiveLinkDeviceCapability_Connection>())
    {
        TScriptInterface<ILiveLinkDeviceCapability_Connection> ConnectionCap(BaseDevice);
        // 使用能力...
    }
}

// 移除设备
Subsystem->RemoveDevice(Device);
```

### 通过能力查询设备

```cpp
ULiveLinkDeviceSubsystem* Subsystem = GEngine->GetEngineSubsystem<ULiveLinkDeviceSubsystem>();

// 获取所有支持录制的设备
TArray<ULiveLinkDevice*> RecordingDevices;
Subsystem->GetDevicesByCapability(ULiveLinkDeviceCapability_Recording::StaticClass(), RecordingDevices);

for (ULiveLinkDevice* Device : RecordingDevices)
{
    if (Device->Implements<ULiveLinkDeviceCapability_Recording>())
    {
        ILiveLinkDeviceCapability_Recording::Execute_StartRecording(Device);
    }
}
```

### 进阶：通过 TScriptInterface 调用能力方法（来源: `LiveLinkDevice.spec.cpp`）

```cpp
// 已知设备类型时直接调用能力接口
ULiveLinkDevice* UnknownDevice = TestDevice;

// 方法 1: 通过 Execute_ 静态函数调用（推荐用于 BlueprintNativeEvent）
int32 Value = ILiveLinkDeviceCapability_BasicTest::Execute_GetValue(UnknownDevice);
ILiveLinkDeviceCapability_BasicTest::Execute_SetValue(UnknownDevice, 42);

// 方法 2: 通过 TScriptInterface 获取接口指针
TScriptInterface<ILiveLinkDeviceCapability_BasicTest> Capability(UnknownDevice);
if (Capability.GetInterface())
{
    // 直接调用接口方法
}
```

## Demo 示例

### 最小自定义设备实现

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "LiveLinkDevice"
});
```

**MySimpleDevice.h + MySimpleDevice.cpp：**

```cpp
// MySimpleDevice.h
#pragma once
#include "LiveLinkDevice.h"
#include "MySimpleDevice.generated.h"

UCLASS()
class UMySimpleDeviceSettings : public ULiveLinkDeviceSettings
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "Config")
    FString DeviceName = TEXT("Simple Device");
};

UCLASS(Blueprintable)
class UMySimpleDevice : public ULiveLinkDevice
{
    GENERATED_BODY()
public:
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override
    {
        return UMySimpleDeviceSettings::StaticClass();
    }
    virtual FText GetDisplayName() const override
    {
        return FText::FromString(GetDeviceSettings<UMySimpleDeviceSettings>()->DeviceName);
    }
    virtual EDeviceHealth GetDeviceHealth() const override { return EDeviceHealth::Nominal; }
    virtual FText GetHealthText() const override { return FText::FromString(TEXT("OK")); }
};
```

## 模块依赖

LiveLinkDevice 的 Build.cs 中全部为 **PrivateDependencyModuleNames**（不对外暴露）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（GEngine 等） |
| `InputCore` | 输入系统 |
| `JsonUtilities` | JSON 序列化（设备会话数据） |
| `LiveLinkHub` | Live Link Hub 应用框架 |
| `Projects` | 项目/插件元数据 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `ToolWidgets` | 工具窗口组件 |

> **注意**: 作为插件使用者，你只需在 Build.cs 中依赖 `LiveLinkDevice` 模块即可。插件内部的所有依赖会被自动链接。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-30 | `84c9c5c4` | [MH-16397] Resolving crash when broadcasting a dynamic delegate from multiple threads | 修复多线程广播动态委托导致的崩溃，说明该框架在实际生产中遇到了线程安全问题并已修复 |
| 2025-09-03 | `94dadceb` | Live Link device framework: Add Unreal (Take Recorder) device | 新增 Unreal（Take Recorder）设备实现，表明框架已有具体设备接入，功能在持续扩展 |
| 2025-04-22 | `ac9d4dcc` | [CaptureManager] Added tooltips to add live link device list | UI 改进：为设备列表添加 tooltip，说明与 CaptureManager 的集成 |

### 维护评价

- **状态**: 🧪 实验性，活跃维护中
- 插件标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，属于实验性功能
- 依赖 LiveLinkHub 插件，仅在 LiveLinkHub 应用模式下激活（`bCreateLiveLinkHubInstance`）
- 最近 6 个月内有实质性功能更新（新增 Take Recorder 设备）和 bug 修复
- 模块类型为 Editor，仅在编辑器环境可用
- **推荐使用**: 如果你在开发 Live Link Hub 设备插件，这是必须的基础框架。但请注意其实验性状态，API 可能在未来版本中发生变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkDevice)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/LiveLinkDevice/Source/LiveLinkDevice/Private/Tests/LiveLinkDevice.spec.cpp)
- [测试用设备实现](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/LiveLinkDevice/Source/LiveLinkDevice/Private/Tests/LiveLinkDevice_BasicTest.h)
