# Capture Manager Devices - Mono Video Ingest

> The Capture Manager Devices contains devices that can be used from the Capture Manager layout of the LiveLink Hub

| 属性 | 值 |
|---|---|
| 中文名 | 单视频导入设备 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（设备逻辑与默认设置） |
| 模块 | `MonoVideoIngestDevice` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices) | |

## 用途

该模块是 Capture Manager 系统的一部分，提供了一个 `MonoVideoIngestDevice` 设备。它的核心功能是在 LiveLink Hub 的“Capture Manager”布局中，将**单机位视频文件**批量导入（Ingest）到 Unreal Engine 中。

它解决的问题是：在虚拟制作或动作捕捉流程中，通常会获得大量以特定方式命名的视频文件。此设备能够解析预定义的文件名模式，自动提取拍摄场次（Slate）、机位（Name）和拍摄次数（Take）等元数据，并将视频文件及其元数据集成到引擎的拍摄数据管理系统中，为后续的编辑、播放和合成流程做准备。

## 使用场景

- 你有一批来自单机位摄影机的 `.mov`、`.mp4` 等视频文件，需要按照文件名中的信息（如“场次_机位_描述-次数”）快速导入到 UE 中。
- 你正在使用 Capture Manager 工作流，希望通过文件目录结构或命名规范，自动发现和识别视频拍摄内容。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Settings` | 获取当前设备的配置对象，用于读取或修改目录和文件名模式。 | `UMonoVideoIngestDevice` |

### 使用示例（蓝图描述）

1.  在 LiveLink Hub 的“Capture Manager”面板中，添加一个 `Mono Video Ingest` 类型的设备。
2.  在设备属性中，通过 `Take Directory` 属性指向包含视频文件的文件夹。
3.  设置 `Video Discovery Expression` 属性。可以使用 `<Auto>` 模式让系统自动识别，也可以手动指定模式如 `<Slate>_<Name>-<Take>`，以便从文件名中精确提取元数据。
4.  设备会根据设置扫描目录，识别出视频文件并显示在设备面板中，后续可进行导入操作。

## C++ 用法

### 头文件引入

```cpp
#include "MonoVideoIngestDevice.h"
```

### 基本用法

该设备主要用于系统流程，在蓝图中配置更为常见。在 C++ 中，你通常会通过 Capture Manager 或 Live Link 系统来创建和管理设备实例，而非直接 `new` 出来。

```cpp
// 获取设备配置类（用于理解结构）
TSubclassOf<ULiveLinkDeviceSettings> SettingsClass = UMonoVideoIngestDevice::StaticClass()->GetDefaultObject<UMonoVideoIngestDevice>()->GetSettingsClass();
```

### 进阶用法

你可以通过 C++ 代码监听设备的设置变更，或与其进行更底层的交互。

```cpp
// 假设你已经有了一个 UMonoVideoIngestDevice 指针
UMonoVideoIngestDevice* VideoDevice = ...;
if (VideoDevice)
{
    // 获取当前设置以查看路径和模式
    const UMonoVideoIngestDeviceSettings* Settings = VideoDevice->GetSettings();
    if (Settings)
    {
        UE_LOG(LogTemp, Log, TEXT("监控目录: %s"), *Settings->TakeDirectory.Path);
        UE_LOG(LogTemp, Log, TEXT("文件名模式: %s"), *Settings->VideoDiscoveryExpression.Expression);
    }
}
```

## Demo 示例

以下示例展示了如何通过 C++ 代码创建并配置一个 `UMonoVideoIngestDeviceSettings` 对象。

```cpp
// MonoVideoIngestDemo.h
#pragma once

#include "CoreMinimal.h"
#include "MonoVideoIngestDevice.h"

class FMonoVideoIngestDemo
{
public:
    void ConfigureDemoDevice();
};
```

```cpp
// MonoVideoIngestDemo.cpp
#include "MonoVideoIngestDemo.h"

void FMonoVideoIngestDemo::ConfigureDemoDevice()
{
    // 创建一个默认的设备设置对象
    UMonoVideoIngestDeviceSettings* DeviceSettings = NewObject<UMonoVideoIngestDeviceSettings>();

    // 配置要扫描的目录
    DeviceSettings->TakeDirectory.Path = TEXT("/Game/Captures/MyMonoVideos");

    // 配置文件名解析模式
    // 例如，文件名为 “SlateName_Camera01_SecondTake-002.mov”
    DeviceSettings->VideoDiscoveryExpression.Expression = TEXT("<Slate>_<Name>_<Any>-<Take>");

    UE_LOG(LogTemp, Warning, TEXT("Mono Video Ingest 设备已配置，监控目录: %s"), *DeviceSettings->TakeDirectory.Path);
    UE_LOG(LogTemp, Warning, TEXT("文件名解析模式: %s"), *DeviceSettings->VideoDiscoveryExpression.Expression);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLinkDevices` | 提供 Live Link 设备基类和接口 |
| `CaptureManagerCore` | 提供 Capture Manager 核心功能，如拍摄数据（Take）管理、元数据等 |
| `IngestCapability` | 提供文件导入（Ingest）能力的核心接口和类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `222ac128` | StereoVideoIngest: Fix component name consistency across ingest devices | 修复了不同导入设备间组件命名不一致的问题 |
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 向CaptureManagerCore中添加了CPS客户端模块 |
| 2026-04-27 | `778f07fc` | [CaptureManager] Fix log category ODR violations in video devices | 修复了视频设备中日志分类违反ODR（单定义规则）的问题 |
| 2026-04-27 | `334822cd` | Add ConfigureMediaSource virtual hook to ULiveLinkFaceDevice | 向LiveLinkFace设备添加了配置媒体源的虚函数钩子 |
| 2026-04-21 | `40065f3e` | Added connection indicator for Live Link Face devices | 为LiveLink Face设备添加了连接状态指示器 |

### 维护评价

该模块创建于2025年2月，目前处于**活跃维护**状态。从近期提交记录看，Epic Games 团队仍在对其进行持续的优化和bug修复，例如确保命名一致性、修复编译警告等。虽然它默认未启用（`EnabledByDefault: false`），但这是作为可选高级功能设计的，不影响其维护状态。该模块是 Capture Manager 工作流中的一个具体实现，随着虚拟制作功能的完善，预计会持续更新。**推荐在需要批量处理单机位视频文件的虚拟制作流程中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices)
- [官方文档]() (暂无)
- [测试用例]() (暂未在引擎测试目录中发现针对此特定插件的测试)