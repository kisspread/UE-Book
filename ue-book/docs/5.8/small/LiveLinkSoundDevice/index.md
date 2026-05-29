# Live Link Sound Device

> Sound Devices recorder support for Live Link Hub with recording and connection capabilities

| 属性 | 值 |
|---|---|
| 中文名 | 录音机设备链接器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产） |
| 模块 | `LiveLinkSoundDevice` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2026-03-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkSoundDevice) | |

## 用途

本插件为 Sound Devices 专业录音设备（如 MixPre、888、Scorpio 系列）提供与 Unreal Engine 的 Live Link 框架集成的能力。它解决了在虚拟制片（Virtual Production）流程中，需要通过网络（REST API）集中控制和监控远程录音设备状态（如连接、录制）的问题，实现了音频录制环节与视效管线的同步。

## 使用场景

- **影视拍摄现场**：在使用 Sound Devices 录音机进行现场同期录音时，通过 Live Link Hub 实时监控其连接状态、启停录制，并与场记信息（Slate/Take）同步。
- **虚拟制片集成**：在 LED Volume 拍摄中，需要将录音设备的开始/停止信号与摄影机、追踪系统联动，确保所有数据时间线对齐。
- **远程设备管理**：在多个录音机部署的片场，通过网络在中心控制台查看所有设备健康状况并控制录制。

## 蓝图用法

本插件作为 Live Link Device 框架的一部分，其蓝图接口主要通过 Live Link Hub 的标准设备管理流程暴露。核心功能通过实现 `ULiveLinkDevice` 及其能力接口（`ILiveLinkDeviceCapability_Connection`, `ILiveLinkDeviceCapability_Recording`）来提供。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect` | 尝试通过配置的 IP 和端口连接到 Sound Devices 录音机 | `ULiveLinkSoundDeviceBase` |
| `Disconnect` | 断开与录音机的连接 | `ULiveLinkSoundDeviceBase` |
| `StartRecording` | 向录音机发送开始录制的命令 | `ULiveLinkSoundDeviceBase` |
| `StopRecording` | 向录音机发送停止录制的命令 | `ULiveLinkSoundDeviceBase` |
| `IsRecording` | 查询录音机当前是否处于录制状态 | `ULiveLinkSoundDeviceBase` |
| `GetConnectionStatus` | 获取当前设备的连接状态（已连接/断开/连接中） | `ULiveLinkSoundDeviceBase` |

### 使用示例（蓝图描述）

1.  在 **Live Link Hub** 中，添加一个新的 `Sound Devices Recorder` 类型的设备。
2.  在设备设置面板中，输入录音机的 **IP Address** 和 **Port**。
3.  蓝图中，获取该设备的 `ULiveLinkSoundDeviceBase` 对象引用。
4.  调用 `Connect` 节点尝试建立连接。
5.  连接成功后，可以调用 `StartRecording` 和 `StopRecording` 来控制录制。
6.  使用 `IsRecording` 节点轮询或事件驱动来获取录制状态。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkSoundDeviceBase.h"
```

### 基本用法

本插件主要通过 Live Link Device 框架使用，开发者通常在 Live Link Hub 的设备管理器中操作。在 C++ 中，可以管理或扩展设备行为。

```cpp
// 假设已获取一个 ULiveLinkSoundDeviceBase* Device 实例
// 检查设备连接状态
ELiveLinkDeviceConnectionStatus Status = Device->GetConnectionStatus_Implementation();

// 尝试连接
if (Device->Connect_Implementation())
{
    UE_LOG(LogTemp, Log, TEXT("成功向录音机发送连接指令"));
}

// 开始录制
if (Device->StartRecording_Implementation())
{
    UE_LOG(LogTemp, Log, TEXT("成功向录音机发送开始录制指令"));
}
```

**注意**：`_Implementation` 后缀是 Unreal Engine 中用于接口实现函数的命名约定。在蓝图或通过基类指针调用时，应使用不带后缀的函数名（如 `Connect()`），引擎会自动路由到正确的实现。

## Demo 示例

以下是一个最小示例，展示如何在 C++ 中配置并使用 Live Link Sound Device。

**头文件 (MySoundDeviceManager.h)**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "LiveLinkSoundDeviceBase.h"
#include "MySoundDeviceManager.generated.h"

UCLASS()
class UMySoundDeviceManager : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY()
    TObjectPtr<ULiveLinkSoundDeviceBase> SoundDevice;

    /** 初始化并配置一个录音机设备实例 */
    void InitializeDevice(const FString& InIpAddress, uint16 InPort, const FString& InUsername, const FString& InPassword);

    /** 尝试连接设备 */
    bool ConnectToDevice();
};
```

**实现文件 (MySoundDeviceManager.cpp)**

```cpp
#include "MySoundDeviceManager.h"
#include "LiveLinkSoundDeviceSettings.h"

void UMySoundDeviceManager::InitializeDevice(const FString& InIpAddress, uint16 InPort, const FString& InUsername, const FString& InPassword)
{
    // 创建设备实例
    SoundDevice = NewObject<ULiveLinkSoundDeviceBase>();

    // 获取并配置设置对象
    if (ULiveLinkSoundDeviceSettings* Settings = Cast<ULiveLinkSoundDeviceSettings>(SoundDevice->GetSettingsClass().GetDefaultObject()))
    {
        Settings->IpAddress = InIpAddress;
        Settings->Port = InPort;
        Settings->Username = InUsername;
        Settings->Password = InPassword;
    }

    // 模拟设备被添加到系统，触发初始化
    SoundDevice->OnDeviceAdded();
}

bool UMySoundDeviceManager::ConnectToDevice()
{
    if (!SoundDevice)
    {
        return false;
    }

    // 调用设备的连接实现
    return SoundDevice->Connect_Implementation();
}
```

## 模块依赖

本插件的 `Build.cs` 文件未在提供信息中，但根据其功能和 `.uplugin` 依赖分析，以下是使用者可能需要的关键模块。

| 模块 | 用途 |
|---|---|
| `LiveLinkDevice` | 插件的核心依赖，提供 `ULiveLinkDevice` 基类和设备能力接口 |
| `LiveLinkInterface` | Live Link 的基础数据接口，设备可能需要向 Live Link Hub 发送状态或元数据 |
| `HTTP` | 用于实现与录音机 REST API 通信的 HTTP 请求功能 |
| `Json` | 解析来自设备 REST API 的 JSON 格式响应 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `f6a8065d` | Matching device name with media source name | 确保设备名称与媒体源名称匹配，提升工作流一致性 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏迁移到新的 UE_LOGF 宏，可能是结构化日志改进 |
| 2026-03-10 | `2f602b1c` | Live Link Sound Devices Plugin - Port from Switchboard to Live Link Device framework | 插件的初始提交，将原有 Switchboard 集成功能移植到 Live Link Device 新框架 |

### 维护评价

该插件处于 **活跃维护** 状态。
- **创建时间**：2026年3月，非常新的插件。
- **近期更新**：最近一次更新在2026年4月，包含功能匹配改进和代码维护（日志宏迁移），表明开发团队仍在积极开发和维护。
- **实验性状态**：插件标记为 `IsExperimentalVersion: true`，且默认不安装 (`Installed: false`)，说明这是一个实验性功能，API和功能未来可能会发生变化。
- **推荐使用**：推荐在需要集成 Sound Devices 专业录音机到 Live Link 工作流的 **实验性** 项目中使用。由于是实验性插件，建议密切关注其更新日志和已知问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkSoundDevice)
- [官方文档](https://docs.unrealengine.com) (通用 UE 文档，目前无此插件专门页面)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/LiveLinkSoundDevice/Tests) (如果存在)