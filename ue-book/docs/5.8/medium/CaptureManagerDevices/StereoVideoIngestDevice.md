# Capture Manager Devices

> The Capture Manager Devices contains devices that can be used from the Capture Manager layout of the LiveLink Hub（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器设备 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Live Link设备资产） |
| 模块 | `CPSLiveLinkDevice` (Runtime), `MonoVideoIngestDevice` (Runtime), `StereoVideoIngestDevice` (Runtime), `TakeArchiveIngestDevice` (Runtime), `VideoLiveLinkDeviceCommon` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices) | |

## 用途

此插件为虚幻引擎的 **Live Link Hub** 中的 **Capture Manager（捕获管理器）** 布局提供具体的设备实现。它解决的核心问题是：在虚拟制作中，如何将不同格式的视频、音频和拍摄数据（Takes）作为标准化的 **Live Link 设备**，统一管理和集成到引擎的编辑与实时工作流中。

插件包含多个设备模块，用于连接或摄入（Ingest）来自不同来源的媒体数据：
- **CPSLiveLinkDevice**: 可能用于连接特定的硬件（如CPS设备）。
- **MonoVideoIngestDevice**: 处理单声道视频文件的摄入。
- **StereoVideoIngestDevice**: 处理立体声（左右眼）视频文件对的摄入。
- **TakeArchiveIngestDevice**: 处理存档形式的拍摄数据（Take）。
- **VideoLiveLinkDeviceCommon**: 包含视频设备共享的代码。

这些设备使得用户可以通过 Capture Manager 界面批量发现、解析文件系统中的媒体文件，并将其作为元数据导入到项目中，简化了大型虚拟制片项目中的资产管理工作流。

## 使用场景

- 你在使用 **Live Link Hub** 进行虚拟制片（Virtual Production）拍摄。
- 你需要将拍摄现场录制的 **立体视频**（例如用于3D重建的双机位）批量导入到引擎中进行后续处理（如重建、合成）。
- 你希望根据自定义的文件名规则（如 `<Slate>_<Name>_<Take>.mov`）自动从文件夹中发现和解析拍摄数据（Takes）。
- 你需要将视频、音频等媒体文件作为具有 Live Link 属性的设备连接到场景中，用于实时预览或后期同步。

## 蓝图用法

本插件主要提供设备类和设置类，用于在编辑器或运行时配置视频摄入行为。核心的可编程接口集中在设备设置上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Settings` | 获取当前立体视频摄入设备的配置设置对象。 | `UStereoVideoIngestDevice` |

### 使用示例（蓝图描述）

1.  **配置设备设置**：在“Capture Manager”布局中添加一个“Stereo Video Ingest”设备后，在其细节面板（Details）中配置：
    - **Take Directory**: 指向包含所有拍摄数据文件夹的根目录。
    - **Video Discovery Expression**: 设置视频文件的匹配模式。例如，选择 `<Auto>` 让系统自动推断，或自定义模式如 `<Slate>_<Name>_<Take>.mov`。
    - **Audio Discovery Expression**: 设置对应的音频文件匹配模式。
2.  **蓝图调用**：在蓝图中，可以通过一个 `UStereoVideoIngestDevice` 类型的对象变量（例如，从 Capture Manager 获取），调用 `Get Settings` 节点获取其 `UStereoVideoIngestDeviceSettings` 对象，从而在运行时读取或修改设置。

## C++ 用法

### 头文件引入

要使用立体视频摄入设备相关的类，需要引入其模块头文件。

```cpp
#include "StereoVideoIngestDevice.h"
```

### 基本用法

以下代码展示了如何在 C++ 中创建一个立体视频摄入设备实例并配置其发现规则。
*(来源：基于 `Private/StereoVideoIngestDevice.h` 中类的推断和常见用法)*

```cpp
#include "StereoVideoIngestDevice.h"
#include "LiveLinkDeviceSubsystem.h"

// 假设你有一个获取设备子系统的途径
ULiveLinkDeviceSubsystem* DeviceSubsystem = GEngine->GetEngineSubsystem<ULiveLinkDeviceSubsystem>();

if (DeviceSubsystem)
{
    // 创建一个新的立体视频摄入设备实例
    UStereoVideoIngestDevice* StereoDevice = NewObject<UStereoVideoIngestDevice>();

    // 获取并修改设备设置
    UStereoVideoIngestDeviceSettings* Settings = const_cast<UStereoVideoIngestDeviceSettings*>(StereoDevice->GetSettings());
    if (Settings)
    {
        // 设置拍摄数据根目录
        Settings->TakeDirectory.Path = TEXT("/Game/Captures/MyStereoShoot");

        // 设置视频文件名匹配模式
        Settings->VideoDiscoveryExpression = TEXT("<Slate>_<Name>_<Take>"); // 示例模式
        // 或使用自动模式：Settings->VideoDiscoveryExpression = TEXT("<Auto>");

        // 通知设备设置已更改，触发重新发现文件
        Settings->PostEditChange();
    }
}
```

### 进阶用法

该设备类继承自 `UBaseIngestLiveLinkDevice` 并实现了 `ILiveLinkDeviceCapability_Connection` 接口，这意味着你可以像管理一个网络连接设备一样管理它。

```cpp
#include "StereoVideoIngestDevice.h"

// 创建设备并尝试连接
UStereoVideoIngestDevice* Device = NewObject<UStereoVideoIngestDevice>();

// 1. 设置硬件ID（如果适用）
bool bHardwareSet = Device->SetHardwareId(TEXT("VIRTUAL_DEVICE_001"));

// 2. 尝试连接
if (bHardwareSet)
{
    bool bConnected = Device->Connect_Implementation(); // 通常，对于文件设备，“连接”意味着验证路径有效性
    if (bConnected)
    {
        // 3. 检查设备健康状态和连接状态
        EDeviceHealth Health = Device->GetDeviceHealth();
        ELiveLinkDeviceConnectionStatus Status = Device->GetConnectionStatus_Implementation();

        // 4. 触发拍摄列表更新（发现文件）
        // 注意：这是一个异步过程，需要回调
        // UIngestCapability_UpdateTakeListCallback* Callback = ...;
        // Device->RunUpdateTakeList(Callback);
    }
}
```

## Demo 示例

一个可编译的最小示例，展示如何创建和配置一个立体视频摄入设备。

```cpp
// MyStereoDeviceDemo.h
#pragma once

#include "CoreMinimal.h"
#include "StereoVideoIngestDevice.h"

class FMyStereoDeviceDemo
{
public:
    void InitDemo();
    void PrintDeviceInfo();

private:
    UPROPERTY()
    UStereoVideoIngestDevice* DeviceInstance = nullptr;
};
```

```cpp
// MyStereoDeviceDemo.cpp
#include "MyStereoDeviceDemo.h"
#include "StereoVideoIngestDevice.h"

void FMyStereoDeviceDemo::InitDemo()
{
    // 创建设备实例
    DeviceInstance = NewObject<UStereoVideoIngestDevice>();

    // 配置设置
    UStereoVideoIngestDeviceSettings* Settings = const_cast<UStereoVideoIngestDeviceSettings*>(DeviceInstance->GetSettings());
    if (Settings)
    {
        Settings->TakeDirectory.Path = TEXT("D:/VirtualProduction/Shoot_2025");
        Settings->VideoDiscoveryExpression = TEXT("<Slate>/<Name>_<Take>");
        Settings->AudioDiscoveryExpression = TEXT("<Auto>");
        UE_LOG(LogTemp, Log, TEXT("Stereo Video Ingest Device configured."));
    }
}

void FMyStereoDeviceDemo::PrintDeviceInfo()
{
    if (DeviceInstance)
    {
        FText HealthText = DeviceInstance->GetHealthText();
        UE_LOG(LogTemp, Log, TEXT("Device Health: %s"), *HealthText.ToString());
    }
}
```

## 模块依赖

要使用 `CaptureManagerDevices` 插件，你的项目模块需要依赖以下模块。已省略标准 Core/Engine/Slate 等常见依赖。

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 框架的核心模块，设备基类和接口所在。 |
| `LiveLinkInterface` | Live Link 的接口定义，用于实现设备能力和属性。 |
| `CaptureManagerCore` | Capture Manager 的核心功能，提供摄入（Ingest）能力基础和 Take 数据结构。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `222ac128` | StereoVideoIngest: Fix component name consistency across ingest devices | 修复了立体视频摄入设备中组件名称不一致的问题，提升跨设备数据一致性。 |
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 在CaptureManagerCore中添加了CPS客户端模块，可能用于支持新硬件连接。 |
| 2026-04-27 | `778f07fc` | [CaptureManager] Fix log category ODR violations in video devices | 修复了视频设备中的日志类别违反“一次定义规则”（ODR）的编译问题。 |
| 2026-04-27 | `334822cd` | Add ConfigureMediaSource virtual hook to ULiveLinkFaceDevice | 为LiveLinkFaceDevice添加了ConfigureMediaSource虚函数钩子，增强扩展性。 |
| 2026-04-21 | `40065f3e` | Added connection indicator for Live Link Face devices | 为Live Link Face设备添加了连接状态指示器。 |

### 维护评价

- **创建时间**：插件于2025年2月创建，非常新（约1年）。
- **活跃度**：根据git记录，插件在创建后持续有功能性更新和错误修复，最近一次更新在2026年5月，**处于活跃维护状态**。
- **状态**：这是一个 **启用的、活跃维护中** 的插件。它不是一个实验性功能，但默认未启用，需要用户在项目中手动启用。
- **已知限制**：文档尚不完善（`DocsURL`为空），主要依赖源码和引擎内置的“Capture Manager”UI进行使用。
- **推荐**：**强烈推荐**给所有进行虚拟制片，并使用 Live Link Hub 的团队。它是连接拍摄素材和引擎的关键工具之一，维护积极。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices)
- [官方文档]() （暂无，请参考引擎内置的 Capture Manager 文档）