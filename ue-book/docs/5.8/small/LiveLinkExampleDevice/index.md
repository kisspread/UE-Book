# Live Link Hub Example Device

> An example device implementation using the Live Link Hub device interface

| 属性 | 值 |
|---|---|
| 中文名 | 示例设备 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例代码） |
| 模块 | `LiveLinkExampleDevice` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkExampleDevice) | |

## 用途

本插件是 **Live Link 设备框架**的一个**示例实现**，并非一个具备实际功能的设备。它的存在是为了演示如何基于 `ULiveLinkDevice` 基类和“能力”接口（`ILiveLinkDeviceCapability`）来构建一个自定义的 Live Link 设备插件。

通过分析此插件的源码，开发者可以学习到：
1.  如何定义一个设备类（继承 `ULiveLinkDevice`）。
2.  如何通过实现特定的“能力”接口（如 `ILiveLinkDeviceCapability_Connection` 和 `ILiveLinkDeviceCapability_Recording`）来为设备赋予连接、录制等标准功能。
3.  如何创建对应的设备设置类（继承 `ULiveLinkDeviceSettings`）以支持在编辑器中进行配置。

简而言之，它是学习 Live Link 设备开发的**官方起点和代码模板**。

## 使用场景

-   当你需要为 **Live Link Hub** 开发一个自定义设备插件时，应首先参考本示例的结构。
-   当你需要将一种新的第三方动捕硬件、面部捕捉软件或任何数据源集成到 UE 的 Live Link 工作流中时，可以此为基础进行开发。

## 蓝图用法

本插件主要作为 C++ 开发参考，但其定义的设备能力和设置在蓝图中同样可用（例如，通过 Python 脚本或设备管理 UI 的蓝图扩展）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Connection Status` | 获取设备的连接状态（已连接/已断开等） | `ULiveLinkExampleDevice` (via `ILiveLinkDeviceCapability_Connection`) |
| `Get Hardware ID` | 获取设备的硬件标识符 | `ULiveLinkExampleDevice` (via `ILiveLinkDeviceCapability_Connection`) |
| `Connect` | 尝试连接到设备 | `ULiveLinkExampleDevice` (via `ILiveLinkDeviceCapability_Connection`) |
| `Disconnect` | 断开与设备的连接 | `ULiveLinkExampleDevice` (via `ILiveLinkDeviceCapability_Connection`) |
| `Start Recording` | 开始在设备上录制数据 | `ULiveLinkExampleDevice` (via `ILiveLinkDeviceCapability_Recording`) |
| `Stop Recording` | 停止在设备上的录制 | `ULiveLinkExampleDevice` (via `ILiveLinkDeviceCapability_Recording`) |
| `Is Recording` | 查询设备是否正在录制 | `ULiveLinkExampleDevice` (via `ILiveLinkDeviceCapability_Recording`) |

### 使用示例（蓝图描述）

1.  在 **Live Link Hub** 的设备管理界面中，你可以添加一个 “Example Device”。
2.  在其属性面板中，你可以修改 `IpAddress` 和 `Port` 属性（来自 `ULiveLinkExampleDeviceSettings`）。
3.  通过界面按钮或自动化脚本，可以调用 `Connect`、`Start Recording` 等节点来控制这个虚拟设备的状态。
4.  设备的健康状态文本（`Get Health Text`）会反映当前的操作状态或错误信息。

## C++ 用法

### 头文件引入

```cpp
#include "Devices/LiveLinkExampleDevice.h"
```

### 基本用法

本插件的核心是定义两个类：设备类和其设置类。创建一个自定义设备的最小步骤如下：

```cpp
// MyLiveLinkDevice.h
#pragma once

#include "Devices/LiveLinkDevice.h"
#include "Capabilities/ILiveLinkDeviceCapability_Connection.h"
#include "MyLiveLinkDevice.generated.h"

UCLASS()
class UMyLiveLinkDeviceSettings : public ULiveLinkDeviceSettings
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category="My Device")
    FString DeviceName = TEXT("MyCustomDevice");
};

UCLASS()
class UMyLiveLinkDevice : public ULiveLinkDevice
    , public ILiveLinkDeviceCapability_Connection // 添加你需要的能力接口
{
    GENERATED_BODY()

public:
    // 1. 指定设备设置类
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override
    {
        return UMyLiveLinkDeviceSettings::StaticClass();
    }

    // 2. 实现设备基础接口
    virtual EDeviceHealth GetDeviceHealth() const override { /* ... */ }
    virtual FText GetHealthText() const override { /* ... */ }
    virtual void OnDeviceAdded() override { /* ... */ }
    virtual void OnDeviceRemoved() override { /* ... */ }
    virtual void OnSettingChanged(const FPropertyChangedEvent& InPropertyChangedEvent) override { /* ... */ }

    // 3. 实现你选择的能力接口
    virtual ELiveLinkDeviceConnectionStatus GetConnectionStatus_Implementation() const override { /* ... */ }
    virtual FString GetHardwareId_Implementation() const override { /* ... */ }
    virtual bool Connect_Implementation() override { /* ... */ }
    // ... 实现其他接口方法
};
```
*代码逻辑参考 `ULiveLinkExampleDevice` 和 `ULiveLinkExampleDeviceSettings` 的结构。*

### 进阶用法

结合多个能力接口来构建设备。例如，同时实现 `ILiveLinkDeviceCapability_Connection` 和 `ILiveLinkDeviceCapability_Recording` 将使你的设备同时具备连接和录制控制功能。

```cpp
UCLASS()
class UMyFullFeatureDevice : public ULiveLinkDevice
    , public ILiveLinkDeviceCapability_Connection
    , public ILiveLinkDeviceCapability_Recording // 同时拥有录制能力
{
    GENERATED_BODY()
    // ... 实现所有来自两个接口的纯虚函数
};
```

## Demo 示例

以下是基于 `LiveLinkExampleDevice` 简化的最小可运行设备示例头文件和实现框架。

### MyMinimalDevice.h

```cpp
// MyMinimalDevice.h
#pragma once

#include "Devices/LiveLinkDevice.h"
#include "Capabilities/ILiveLinkDeviceCapability_Connection.h"
#include "MyMinimalDevice.generated.h"

UCLASS()
class UMyMinimalDevice : public ULiveLinkDevice
    , public ILiveLinkDeviceCapability_Connection
{
    GENERATED_BODY()

public:
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override;

    // ULiveDevice Interface
    virtual EDeviceHealth GetDeviceHealth() const override;
    virtual FText GetHealthText() const override;
    virtual void OnDeviceAdded() override;
    virtual void OnDeviceRemoved() override;
    virtual void OnSettingChanged(const FPropertyChangedEvent& InPropertyChangedEvent) override;

    // ILiveLinkDeviceCapability_Connection Interface
    virtual ELiveLinkDeviceConnectionStatus GetConnectionStatus_Implementation() const override;
    virtual FString GetHardwareId_Implementation() const override;
    virtual bool SetHardwareId_Implementation(const FString& HardwareID) override;
    virtual bool Connect_Implementation() override;
    virtual bool Disconnect_Implementation() override;

private:
    ELiveLinkDeviceConnectionStatus CurrentStatus = ELiveLinkDeviceConnectionStatus::Disconnected;
};
```

### MyMinimalDevice.cpp (示例实现)

```cpp
// MyMinimalDevice.cpp
#include "MyMinimalDevice.h"

TSubclassOf<ULiveLinkDeviceSettings> UMyMinimalDevice::GetSettingsClass() const
{
    // 返回一个基础设置类，或你自定义的设置类
    return ULiveLinkDeviceSettings::StaticClass();
}

EDeviceHealth UMyMinimalDevice::GetDeviceHealth() const
{
    return EDeviceHealth::Nominal; // 示例，根据实际逻辑返回
}

FText UMyMinimalDevice::GetHealthText() const
{
    return FText::FromString(TEXT("Example Device is healthy."));
}

void UMyMinimalDevice::OnDeviceAdded()
{
    // 设备被添加到管理器时调用
    UE_LOG(LogTemp, Log, TEXT("My Minimal Device added."));
}

void UMyMinimalDevice::OnDeviceRemoved()
{
    // 设备从管理器移除时调用
    UE_LOG(LogTemp, Log, TEXT("My Minimal Device removed."));
}

void UMyMinimalDevice::OnSettingChanged(const FPropertyChangedEvent& InPropertyChangedEvent)
{
    // 当设置（如IpAddress）在编辑器UI中改变时调用
    UE_LOG(LogTemp, Log, TEXT("Device setting changed."));
}

// Connection Capability Implementation
ELiveLinkDeviceConnectionStatus UMyMinimalDevice::GetConnectionStatus_Implementation() const
{
    return CurrentStatus;
}

FString UMyMinimalDevice::GetHardwareId_Implementation() const
{
    return TEXT("MY_MINIMAL_DEVICE_001");
}

bool UMyMinimalDevice::SetHardwareId_Implementation(const FString& HardwareID)
{
    // 在此存储HardwareID，或进行验证
    return true;
}

bool UMyMinimalDevice::Connect_Implementation()
{
    // 模拟连接逻辑
    CurrentStatus = ELiveLinkDeviceConnectionStatus::Connected;
    return true;
}

bool UMyMinimalDevice::Disconnect_Implementation()
{
    // 模拟断开逻辑
    CurrentStatus = ELiveLinkDeviceConnectionStatus::Disconnected;
    return true;
}
```

## 模块依赖

根据 `.uplugin` 文件，本插件依赖另一个插件：

| 模块 | 用途 |
|---|---|
| `LiveLinkDevice` | 提供设备基类 `ULiveLinkDevice` 和设备设置类 `ULiveLinkDeviceSettings`，以及设备管理的核心框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `f6a8065d` | Matching device name with media source name | 更新示例设备名称，使其与媒体源名称保持一致。 |
| 2025-11-26 | `7daa31a9` | LiveLink - Remove LiveLinkHub plugin dependency from LiveLinkDevice to allow LiveLink to depend on L... | 解耦插件依赖，使LiveLinkDevice不再强制依赖LiveLinkHub插件。 |
| 2025-05-22 | `bbe0a573` | Live Link Hub: Don't enable LiveLinkExampleDevice by default. | 明确将示例设备设为默认禁用，仅作为参考使用。 |
| 2025-03-31 | `065f738c` | Live Link device framework: Device session serialization, capability UI improvements, code cleanup. | 设备框架更新：增加了设备会话序列化功能，改进了能力UI，并进行了代码清理。 |
| 2024-12-18 | `05339a50` | Live Link Hub: Introduce a new Live Link "Device" framework. | 初始提交，引入Live Link设备框架及此示例设备插件。 |

### 维护评价

-   **活跃维护**：该插件虽为示例，但自创建（2024-12-18）以来有持续更新，最近一次功能性更新（设备名称匹配）发生在2026年4月，表明其随着底层框架的演进而同步维护。
-   **实验性**：在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，这与其作为学习示例和框架演示的定位相符。
-   **推荐使用**：**强烈推荐**给所有需要开发自定义 Live Link 设备插件的开发者作为首要参考。它是理解框架设计、接口契约和最佳实践的官方蓝图。不应用于实际生产环境。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkExampleDevice)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkExampleDevice/Source/LiveLinkExampleDevice/Tests) (如果存在)