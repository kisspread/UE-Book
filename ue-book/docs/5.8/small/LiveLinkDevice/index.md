# Live Link Device Framework

> Provides interfaces and base classes for implementing Live Link Hub devices

| 属性 | 值 |
|---|---|
| 中文名 | 设备框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkDevice` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkDevice) | |

## 用途

该插件为 Live Link Hub 提供了一个统一的设备抽象层。它解决的核心问题是：在复杂的动捕或虚拟制作工作流中，需要集成、监控和自动化来自不同厂商的硬件设备与第三方软件。

它并非一个具体的功能实现，而是一个**框架**。开发者可以通过继承 `ULiveLinkDevice` 基类并实现不同的 `ILiveLinkDeviceCapability` 接口（如连接、录制）来创建标准化的设备驱动。这使得 Live Link Hub 能够以统一的方式管理（如显示、控制、持久化）所有接入的设备，类似于 Switchboard 的功能，但更侧重于通过可查询的“能力”接口提供灵活的扩展性。

## 使用场景

- 你正在开发一个定制的 Live Link Hub，需要统一管理来自 Vicon、OptiTrack、Noitom 等不同厂商的动捕设备 → 为每种设备实现一个 `ULiveLinkDevice` 子类。
- 你的设备具备网络连接功能，你希望在 Live Link Hub 中显示其连接状态、硬件ID并提供连接/断开操作 → 为你的设备实现 `ILiveLinkDeviceCapability_Connection` 接口。
- 你的设备支持数据录制，你希望在 Hub 中统一控制开始/停止录制，并显示录制状态 → 为你的设备实现 `ILiveLinkDeviceCapability_Recording` 接口。
- 你需要在 Live Link Hub 的设备列表中添加自定义的列和单元格控件，用于显示设备特有的信息 → 通过 `ULiveLinkDeviceCapability` 的 CDO 注册自定义表格列。

## 蓝图用法

该插件定义了多个 `BlueprintCallable` 函数，主要用于查询设备状态和与设备能力交互。以下是核心功能分组：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetConnectionStatus` | 获取设备的连接状态 | `ILiveLinkDeviceCapability_Connection` |
| `Connect` | 尝试建立连接 | `ILiveLinkDeviceCapability_Connection` |
| `Disconnect` | 尝试断开连接 | `ILiveLinkDeviceCapability_Connection` |
| `GetHardwareId` | 获取设备的硬件标识符（如序列号、IP） | `ILiveLinkDeviceCapability_Connection` |
| `SetHardwareId` | 设置设备的硬件标识符 | `ILiveLinkDeviceCapability_Connection` |
| `StartRecording` | 开始在设备上录制 | `ILiveLinkDeviceCapability_Recording` |
| `StopRecording` | 停止在设备上录制 | `ILiveLinkDeviceCapability_Recording` |
| `IsRecording` | 查询设备是否正在录制 | `ILiveLinkDeviceCapability_Recording` |
| `GetDeviceHealth` | 获取设备的运行健康状态 | `ULiveLinkDevice` |
| `GetDevicesByClass` | 按设备类获取所有设备实例 | `ULiveLinkDeviceSubsystem` |
| `GetDevicesByCapability` | 按能力类获取所有实现了该能力的设备 | `ULiveLinkDeviceSubsystem` |

### 使用示例（蓝图描述）

假设你有一个已经创建好的设备实例（变量 `MyDevice`），你想检查其连接状态并尝试连接：
1. 从 `MyDevice` 拉出引脚，搜索并添加 `Get Connection Status` 节点。其输出是一个 `ELiveLinkDeviceConnectionStatus` 枚举。
2. 将 `Get Connection Status` 节点的输出连接到一个 `Branch` 节点，检查状态是否为 `Disconnected`。
3. 如果分支为真，则从 `MyDevice` 拉出引脚，添加 `Connect` 节点来尝试连接。
4. 你可以通过 `Get Connection Delegate` 节点获取一个委托对象，用于在蓝图中监听连接状态变化的动态事件。

## C++ 用法

主要通过继承和实现接口来扩展框架。

### 头文件引入

```cpp
#include "LiveLinkDevice.h"
#include "LiveLinkDeviceSubsystem.h"
#include "LiveLinkDeviceCapability_Connection.h"
#include "LiveLinkDeviceCapability_Recording.h"
```

### 基本用法

以下代码演示了如何创建一个最简单的自定义设备，并实现连接能力。（参考 `Tests/LiveLinkDevice_BasicTest.h`）

```cpp
// MyLiveLinkDevice.h
#pragma once
#include "LiveLinkDevice.h"
#include "LiveLinkDeviceCapability_Connection.h" // 包含连接能力接口
#include "MyLiveLinkDevice.generated.h"

// 1. 定义设备设置类
UCLASS()
class UMyDeviceSettings : public ULiveLinkDeviceSettings
{
    GENERATED_BODY()
public:
    UMyDeviceSettings() { DisplayName = TEXT("My Custom Device"); }
};

// 2. 定义设备类，继承基类和需要实现的能力接口
UCLASS(NotPlaceable)
class UMyLiveLinkDevice : public ULiveLinkDevice
    , public ILiveLinkDeviceCapability_Connection // 实现连接能力
{
    GENERATED_BODY()

public:
    // 实现 ULiveLinkDevice 的纯虚函数
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override { return UMyDeviceSettings::StaticClass(); }
    virtual EDeviceHealth GetDeviceHealth() const override { return EDeviceHealth::Nominal; }
    virtual FText GetHealthText() const override { return FText::FromString(TEXT("OK")); }

    // 实现 ILiveLinkDeviceCapability_Connection 的纯虚函数
    virtual ELiveLinkDeviceConnectionStatus GetConnectionStatus_Implementation() const override { return CurrentStatus; }
    virtual FString GetHardwareId_Implementation() const override { return HardwareId; }
    virtual bool Connect_Implementation() override
    {
        // ... 你的连接逻辑 ...
        SetConnectionStatus(ELiveLinkDeviceConnectionStatus::Connected);
        return true;
    }
    virtual bool Disconnect_Implementation() override
    {
        // ... 你的断开逻辑 ...
        SetConnectionStatus(ELiveLinkDeviceConnectionStatus::Disconnected);
        return true;
    }

protected:
    ELiveLinkDeviceConnectionStatus CurrentStatus = ELiveLinkDeviceConnectionStatus::Disconnected;
    FString HardwareId = TEXT("192.168.1.100");
};
```

### 进阶用法

创建设备实例并管理其生命周期。

```cpp
// 在某个管理类中，例如你的编辑器模块或子系统
#include "LiveLinkDeviceSubsystem.h"

void CreateAndManageMyDevice()
{
    // 1. 获取设备子系统
    ULiveLinkDeviceSubsystem* DeviceSubsystem = GEngine->GetEngineSubsystem<ULiveLinkDeviceSubsystem>();
    if (!DeviceSubsystem) return;

    // 2. 创建设备实例
    auto CreateResult = DeviceSubsystem->CreateDeviceOfClass(UMyLiveLinkDevice::StaticClass());
    if (CreateResult.HasValue())
    {
        FGuid NewDeviceId = CreateResult.GetValue().DeviceId;
        UMyLiveLinkDevice* NewDevice = Cast<UMyLiveLinkDevice>(CreateResult.GetValue().Device);

        // 3. 通过能力接口操作设备
        ILiveLinkDeviceCapability_Connection* ConnectionCap = Cast<ILiveLinkDeviceCapability_Connection>(NewDevice);
        if (ConnectionCap)
        {
            ConnectionCap->Execute_Connect(NewDevice);
        }

        // 4. 监听设备事件
        DeviceSubsystem->OnDeviceAdded().AddLambda([NewDeviceId](FGuid Id, ULiveLinkDevice* Dev) {
            if (Id == NewDeviceId) { /* 设备已添加 */ }
        });
    }

    // 5. 稍后，移除设备
    // DeviceSubsystem->RemoveDevice(NewDeviceId);
}
```

## Demo 示例

一个最小化的自定义设备和连接能力实现。

```cpp
// SimpleDevice.h
#pragma once
#include "LiveLinkDevice.h"
#include "LiveLinkDeviceCapability_Connection.h"
#include "SimpleDevice.generated.h"

UCLASS()
class USimpleDeviceSettings : public ULiveLinkDeviceSettings { GENERATED_BODY() };

UCLASS(NotPlaceable)
class USimpleDevice : public ULiveLinkDevice, public ILiveLinkDeviceCapability_Connection
{
    GENERATED_BODY()
public:
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override { return USimpleDeviceSettings::StaticClass(); }
    virtual EDeviceHealth GetDeviceHealth() const override { return EDeviceHealth::Nominal; }
    virtual FText GetHealthText() const override { return FText::FromString(TEXT("Simple")); }

    virtual ELiveLinkDeviceConnectionStatus GetConnectionStatus_Implementation() const override { return bConnected ? ELiveLinkDeviceConnectionStatus::Connected : ELiveLinkDeviceConnectionStatus::Disconnected; }
    virtual FString GetHardwareId_Implementation() const override { return TEXT("SIMPLE-001"); }
    virtual bool Connect_Implementation() override { bConnected = true; SetConnectionStatus(ELiveLinkDeviceConnectionStatus::Connected); return true; }
    virtual bool Disconnect_Implementation() override { bConnected = false; SetConnectionStatus(ELiveLinkDeviceConnectionStatus::Disconnected); return true; }

private:
    bool bConnected = false;
};
```

```cpp
// SimpleDevice.cpp (仅需包含头文件即可，功能实现均在头文件的内联函数中完成)
#include "SimpleDevice.h"
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | 提供核心的 Live Link 框架和客户端/服务器功能 |
| `LiveLinkHub` | 提供 Hub 会话管理和数据处理器基础类 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `bebf80da` | Porting CL 52732989 from Main stream | 从主线移植变更，可能包含功能同步或修复 |
| 2026-04-14 | `f6a8065d` | Matching device name with media source name | 将设备名称与媒体源名称匹配，可能改善显示一致性 |
| 2026-03-23 | `fd8c50d3` | Persisting media sources created by LiveLinkDevices | 持久化由 LiveLink 设备创建的媒体源，改善状态保存 |
| 2026-03-06 | `42cc20c7` | Adding interfaces from super classes as well | 同时添加来自父类的接口，改进能力查询逻辑 |
| 2026-03-05 | `146ad3d3` | Integrate Capture Manager with the Data Devices panel and deprecate the now redundant Devices panel | 将捕获管理器集成到数据设备面板，并废弃冗余的设备面板 |

### 维护评价

该插件创建于 2024 年底，是一个相对较新的**实验性**框架（`IsExperimentalVersion: true`，且默认禁用）。从 Git 历史看，它在 2026 年初仍保持着**活跃的开发和维护**，近期更新主要集中在功能完善（如媒体源持久化、UI 集成）和内部重构（接口查询优化）上。

**推荐使用**：如果你需要为 Live Link Hub 开发自定义设备驱动，这个框架是 Epic Games 官方提供的标准化解决方案。尽管它处于实验阶段且 API 可能发生变化，但其架构设计合理，且持续获得更新支持。建议密切关注其 API 变更，并将其作为未来 Live Link 设备开发的首选基础。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkDevice)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkDevice/Private/Tests)