# Live Link Hub Example Device

> An example device implementation using the Live Link Hub device interface

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | LiveLinkExampleDevice (Editor) |
| 创建时间 | 2024-12-18 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkExampleDevice) | |

## 用途

这是一个 **教学示例插件**，演示如何为 Live Link Hub 创建自定义设备（Device）。它本身不提供实际的运动捕捉或动画数据采集功能，而是作为模板代码，帮助开发者理解 Live Link Device 框架的实现模式。

插件展示了设备的三个核心能力：
- **连接管理**（Connection）：IP 地址/端口配置、连接/断开流程
- **录制控制**（Recording）：与 Live Link 录制会话集成
- **设备生命周期**：设备添加/移除回调、设置变更响应

## 使用场景

- 你需要为自定义硬件（如动捕设备、传感器）开发 Live Link Hub 设备插件 → 参考此插件的实现模式
- 你想了解 Live Link Device 框架的能力接口（Capability）系统 → 这是最简单的完整示例
- 你要快速搭建一个 Live Link 设备的骨架代码 → 复制此插件并修改

## 蓝图用法

本插件是 **Editor 模块**，且所有类都在 `Private` 目录下，不暴露蓝图接口。

设备的创建和管理通过 **Live Link Hub** 面板完成，无需蓝图操作。

## C++ 用法

### 头文件引入

本插件的类位于 `Private` 目录，不作为公共 API。以下信息用于理解框架结构：

```cpp
#include "LiveLinkDevice.h"
#include "LiveLinkDeviceCapability_Connection.h"
#include "LiveLinkDeviceCapability_Recording.h"
```

### 架构解析

Live Link Device 框架采用 **Capability 接口** 模式。设备类继承 `ULiveLinkDevice`，然后通过实现不同的 Capability 接口来获得功能：

```
ULiveLinkExampleDevice
├── ULiveLinkDevice              ← 基类：设备生命周期、显示名、健康状态
├── ILiveLinkDeviceCapability_Connection  ← 连接能力：Connect/Disconnect/GetHardwareId
└── ILiveLinkDeviceCapability_Recording   ← 录制能力：StartRecording/StopRecording
```

### 设备设置类

每个设备需要一个 Settings 类继承 `ULiveLinkDeviceSettings`，用于在编辑器中配置：

```cpp
UCLASS()
class ULiveLinkExampleDeviceSettings : public ULiveLinkDeviceSettings
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category="Example Device")
    FString DisplayName = TEXT("Example Device");

    UPROPERTY(EditAnywhere, Category="Example Device")
    FString IpAddress = TEXT("127.0.0.1");

    UPROPERTY(EditAnywhere, Category="Example Device")
    uint16 Port = 12345;
};
```

设备类通过 `GetSettingsClass()` 关联设置类：

```cpp
virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override
{
    return ULiveLinkExampleDeviceSettings::StaticClass();
}
```

### 连接能力实现要点

`Connect_Implementation()` 中解析 IP 地址并设置连接状态：

```cpp
bool ULiveLinkExampleDevice::Connect_Implementation()
{
    // 1. 确保当前是断开状态
    if (!ensure(ConnectionStatus == ELiveLinkDeviceConnectionStatus::Disconnected))
        return false;

    // 2. 解析 IP 和端口
    FIPv4Endpoint Endpoint;
    if (!FIPv4Address::Parse(DeviceSettings->IpAddress, Endpoint.Address))
        return false;
    Endpoint.Port = DeviceSettings->Port;

    // 3. 更新状态（注意：实际连接逻辑需自行实现）
    ConnectionStatus = ELiveLinkDeviceConnectionStatus::Connecting;
    SetConnectionStatus(ConnectionStatus);
    return true;
}
```

`SetHardwareId_Implementation()` 支持解析 `IP:Port` 和纯 IP 两种格式：

```cpp
// 支持 "192.168.1.1:54321" 或 "192.168.1.1"（使用默认端口）
FIPv4Endpoint Endpoint;
if (FIPv4Endpoint::Parse(InHardwareID, Endpoint))
{
    // 完整 endpoint
}
else if (FIPv4Address::Parse(InHardwareID, Endpoint.Address))
{
    // 仅 IP，使用默认端口
    Endpoint.Port = SettingsCDO->Port;
}
```

### 设备创建（来自测试用例）

通过 `ULiveLinkDeviceSubsystem` 创建设备实例：

```cpp
ULiveLinkDeviceSubsystem* DeviceSubsystem = GEngine->GetEngineSubsystem<ULiveLinkDeviceSubsystem>();

// 1. 准备设置
ULiveLinkExampleDeviceSettings* DeviceSettingsTemplate = NewObject<ULiveLinkExampleDeviceSettings>();
DeviceSettingsTemplate->IpAddress = FString(TEXT("127.1.2.3"));
DeviceSettingsTemplate->DisplayName = FString(TEXT("Test Device"));

// 2. 创建设备
ULiveLinkDeviceSubsystem::FCreateResult CreateResult =
    DeviceSubsystem->CreateDeviceOfClass(ULiveLinkExampleDevice::StaticClass(), DeviceSettingsTemplate);

if (CreateResult.HasValue())
{
    const FGuid DeviceId = CreateResult.GetValue().DeviceId;
    ULiveLinkDevice* NewDevice = CreateResult.GetValue().Device;
}
```

来源：`Source/LiveLinkExampleDevice/Private/Tests/LiveLinkExampleDeviceTests.cpp`

## Demo 示例

如要基于此插件创建自己的 Live Link 设备：

1. 复制整个 `LiveLinkExampleDevice` 目录，重命名
2. 修改 `.uplugin` 中的 `FriendlyName` 和模块名
3. 自定义 Settings 类的属性（如添加串口号、协议类型等）
4. 在 `Connect_Implementation()` 中实现实际的设备连接逻辑
5. 在 `StartRecording_Implementation()` 中实现数据采集逻辑
6. 根据需要添加新的 Capability 接口

## 模块依赖

所有依赖均为 `PrivateDependencyModuleNames`，说明此插件是自包含的，不暴露公共 API。

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、日志 |
| `CoreUObject` | UCLASS/UPROPERTY 反射系统 |
| `Engine` | 引擎核心（GEngine、子系统） |
| `InputCore` | 输入核心类型 |
| `LiveLinkDevice` | Device 框架基类和 Capability 接口 |
| `LiveLinkHub` | Live Link Hub 会话信息（录制会话） |
| `Networking` | IPv4 地址/端口解析 |
| `Projects` | 项目/插件系统 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |

另外，`.uplugin` 声明了插件依赖 `LiveLinkDevice`。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-05-22 | `7e73442` | Don't enable LiveLinkExampleDevice by default | 将 `EnabledByDefault` 改为 false，表明作为示例不应默认启用 |
| 2025-03-31 | `065f738` | Device session serialization, capability UI improvements, code cleanup | 设备会话序列化能力增强，Capability UI 改进，代码清理 |
| 2024-12-18 | `05339a5` | Introduce a new Live Link "Device" framework | 初始提交，引入 Device 框架时同时创建了此示例插件 |

### 维护评价

- **创建时间**：2024-12-18，约 1.4 年历史，属于较新的插件
- **更新频率**：3 次提交，平均约 4 个月一次，与框架同步更新
- **维护状态**：活跃维护中，随 Live Link Device 框架一起演进
- **性质**：`IsExperimentalVersion = true`，`EnabledByDefault = false`，这是 Epic 的官方教学示例
- **推荐程度**：如果你要开发自定义 Live Link 设备，这是必读的参考代码。作为功能插件不推荐直接使用（它本身不提供实际功能）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkExampleDevice)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/LiveLinkExampleDevice/Source/LiveLinkExampleDevice/Private/Tests/LiveLinkExampleDeviceTests.cpp)
