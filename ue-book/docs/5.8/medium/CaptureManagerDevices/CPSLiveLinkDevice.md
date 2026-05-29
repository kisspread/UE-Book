# Capture Manager Devices

> The Capture Manager Devices contains devices that can be used from the Capture Manager layout of the Live Link Hub

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器设备 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（设备实现、自定义属性编辑器） |
| 模块 | `CPSLiveLinkDevice` (Runtime), `MonoVideoIngestDevice` (Runtime), `StereoVideoIngestDevice` (Runtime), `TakeArchiveIngestDevice` (Runtime), `VideoLiveLinkDeviceCommon` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices) | |

## 用途

本插件为 **Capture Manager**（虚拟制片捕获管理器）提供具体的硬件设备抽象实现。Capture Manager 是 Live Link Hub 中用于管理面部/身体捕获设备、采集拍摄数据（take）的核心布局模块。

本插件解决的核心问题是：**将不同类型的捕获设备（Live Link Face 应用、单目/双目视频、拍摄档案）统一抽象为可连接、可录制、可流式传输、可采集（ingest）的设备接口**。

包含 5 个子模块，分别对应不同设备类型：
- **CPSLiveLinkDevice** — Live Link Face 应用设备（通过 CPS 协议连接 iPhone/iPad 上的 Live Link Face 应用）
- **MonoVideoIngestDevice** — 单目视频采集设备
- **StereoVideoIngestDevice** — 双目视频采集设备
- **TakeArchiveIngestDevice** — 拍摄档案（已录制的 take）采集设备
- **VideoLiveLinkDeviceCommon** — 视频 Live Link 设备的通用共享逻辑

## 使用场景

- 你在做虚拟制片项目，需要用 iPhone 上的 **Live Link Face** 应用进行面部动捕 → 用 `CPSLiveLinkDevice`
- 你需要从单目/双目视频文件中采集面部数据到 Unreal → 用 `MonoVideoIngestDevice` / `StereoVideoIngestDevice`
- 你有一个已导出的 take 档案包，需要重新导入系统 → 用 `TakeArchiveIngestDevice`
- 你在 Live Link Hub 的 Capture Manager 面板中管理多台捕获设备 → 本插件提供所有设备实现

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSettings` | 获取 Live Link Face 设备设置 | `ULiveLinkFaceDevice` |
| `Connect` | 连接到 Live Link Face 设备 | `ULiveLinkFaceDevice`（通过 Capability 接口） |
| `Disconnect` | 断开与设备的连接 | `ULiveLinkFaceDevice`（通过 Capability 接口） |
| `StartRecording` | 开始远程录制 | `ULiveLinkFaceDevice`（通过 Capability 接口） |
| `StopRecording` | 停止远程录制 | `ULiveLinkFaceDevice`（通过 Capability 接口） |
| `IsRecording` | 查询当前是否正在录制 | `ULiveLinkFaceDevice`（通过 Capability 接口） |

### 设备设置（ULiveLinkFaceDeviceSettings）

在编辑器细节面板中可配置：

- **IpAddress** (`FDeviceIpAddress`) — 设备 IP 地址，支持自定义 UI 验证输入格式
- **Port** (`int32`, 默认 `14785`) — CPS 协议端口号
- **ConnectAction** (`FToggleConnectAction`) — 连接/断开按钮，带自定义属性编辑器

### 使用示例（蓝图描述）

1. 在 **Live Link Hub** 中打开 **Capture Manager** 面板
2. 添加设备，选择 **"Live Link Face Device"**
3. 在设备设置中填入 iPhone 的 IP 地址和端口（默认 14785）
4. 点击 **Connect** 按钮连接设备
5. 设备连接成功后，可在 take 列表中查看 iPhone 上的拍摄数据
6. 选择需要的 take，执行 Download 或 Convert & Upload 操作

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkFaceDevice.h"
```

### 基本用法 — 实现自定义 Live Link 设备

从 `ULiveLinkFaceDevice` 的实现模式可以学习如何创建自定义设备：

```cpp
// Source: CPSLiveLinkDevice/Public/LiveLinkFaceDevice.h

// 设备设置类 - 定义设备在编辑器中的可配置参数
UCLASS(BlueprintType)
class UMyCaptureDeviceSettings : public ULiveLinkDeviceSettings
{
    GENERATED_BODY()
public:
    UMyCaptureDeviceSettings()
    {
        DisplayName = TEXT("My Capture Device");
    }

    // 设备 IP 地址（使用自定义属性编辑器 FDeviceIpAddressCustomization）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "My Device")
    FDeviceIpAddress IpAddress;

    // 通信端口
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "My Device")
    int32 Port = 12345;
};

// 设备类 - 通过 Capability 接口声明设备支持的功能
UCLASS(BlueprintType, meta = (DisplayName = "My Capture Device"))
class UMyCaptureDevice : public UBaseIngestLiveLinkDevice
    , public ILiveLinkDeviceCapability_Connection   // 连接能力
    , public ILiveLinkDeviceCapability_Recording    // 录制能力
    , public ILiveLinkDeviceCapability_Streaming    // 流式传输能力
{
    GENERATED_BODY()

public:
    // 返回设备设置类型
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override;

    // 设备健康状态
    virtual EDeviceHealth GetDeviceHealth() const override;

    // 设备生命周期回调
    virtual void OnDeviceAdded() override;
    virtual void OnDeviceRemoved() override;
};
```

### 进阶用法 — 采集（Ingest）流程实现

`ULiveLinkFaceDevice` 展示了完整的 take 采集流程：

```cpp
// Source: CPSLiveLinkDevice/Public/LiveLinkFaceDevice.h

// 1. 获取 take 完整路径
virtual FString GetFullTakePath(UE::CaptureManager::FTakeId InTakeId) const override;

// 2. 更新 take 列表（从设备获取所有可用拍摄）
virtual void RunUpdateTakeList(UIngestCapability_UpdateTakeListCallback* InCallback) override;

// 3. 下载 take 数据
virtual void RunDownloadTake(
    const UIngestCapability_ProcessHandle* InProcessHandle,
    const UIngestCapability_Options* InIngestOptions) override;

// 4. 转换并上传 take
virtual void RunConvertAndUploadTake(
    const UIngestCapability_ProcessHandle* InProcessHandle,
    const UIngestCapability_Options* InIngestOptions) override;

// 5. 取消采集流程
virtual void CancelIngestProcess_Implementation(
    const UIngestCapability_ProcessHandle* InProcessHandle) override;
```

## Demo 示例

基于 `ULiveLinkFaceDeviceSettings` 的最小设置类示例：

```cpp
// MyCaptureDeviceSettings.h
#pragma once

#include "LiveLinkDeviceSettings.h"
#include "LiveLinkFaceDevice.h"
#include "MyCaptureDeviceSettings.generated.h"

UCLASS(BlueprintType)
class MYCAPTUREMODULE_API UMyDeviceSettings : public ULiveLinkDeviceSettings
{
    GENERATED_BODY()

public:
    UMyDeviceSettings()
    {
        DisplayName = TEXT("My Custom Device");
    }

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    FDeviceIpAddress IpAddress;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    int32 Port = 8080;
};
```

```cpp
// MyCaptureDevice.cpp
#include "MyCaptureDevice.h"
#include "MyCaptureDeviceSettings.h"

TSubclassOf<ULiveLinkDeviceSettings> UMyCaptureDevice::GetSettingsClass() const
{
    return UMyDeviceSettings::StaticClass();
}

EDeviceHealth UMyCaptureDevice::GetDeviceHealth() const
{
    // 根据连接状态返回健康状态
    if (GetConnectionStatus_Implementation() == ELiveLinkDeviceConnectionStatus::Connected)
    {
        return EDeviceHealth::Nominal;
    }
    return EDeviceHealth::Error;
}

FText UMyCaptureDevice::GetHealthText() const
{
    return FText::FromString(TEXT("My Custom Device Status"));
}

void UMyCaptureDevice::OnDeviceAdded()
{
    Super::OnDeviceAdded();
    // 设备添加时的初始化逻辑
}

void UMyCaptureDevice::OnDeviceRemoved()
{
    Super::OnDeviceRemoved();
    // 设备移除时的清理逻辑
}

bool UMyCaptureDevice::Connect_Implementation()
{
    // 建立与物理设备的连接
    return true;
}

bool UMyCaptureDevice::Disconnect_Implementation()
{
    // 断开连接
    return true;
}

ELiveLinkDeviceConnectionStatus UMyCaptureDevice::GetConnectionStatus_Implementation() const
{
    // 返回当前连接状态
    return ELiveLinkDeviceConnectionStatus::Disconnected;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 框架核心 |
| `LiveLinkHub` | Live Link Hub 应用框架 |
| `LiveLinkDevice` | 设备抽象基类和 Capability 接口 |
| `CaptureManagerCore` | Capture Manager 核心功能（take 管理、采集流程） |
| `CaptureManagerCPSClient` | CPS 协议客户端（与 Live Link Face 应用通信） |
| `RtspMedia` | RTSP 流媒体支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `222ac128` | StereoVideoIngest: Fix component name consistency across ingest devices | 修复双目视频采集设备中组件名称一致性问题 |
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 将 CPS 客户端模块迁移到 CaptureManagerCore 下 |
| 2026-04-27 | `778f07fc` | [CaptureManager] Fix log category ODR violations in video devices | 修复视频设备模块中日志分类的 ODR 违规问题 |
| 2026-04-27 | `334822cd` | Add ConfigureMediaSource virtual hook to ULiveLinkFaceDevice | 为 LiveLinkFaceDevice 添加 ConfigureMediaSource 虚函数钩子 |
| 2026-04-21 | `40065f3e` | Added connection indicator for Live Link Face devices | 为 Live Link Face 设备添加连接状态指示器 |

### 维护评价

- **创建时间**: 2025-02-14，非常新的插件（约 0 年）
- **活跃度**: 活跃维护中，最近数月持续有功能性更新和 bug 修复
- **注意事项**:
  - `EnabledByDefault=false`，需要在插件管理器中手动启用
  - 部分 Protocol 头文件已迁移到 `CaptureManagerCPSClient` 模块（`CPSDevice.h`、`CPSDataStream.h`、`CPSFileStream.h`），旧头文件保留为 deprecated 重定向
  - 属于 Live Link Hub / Virtual Production 工作流的一部分，需要配合 Live Link Hub 使用
- **推荐度**: ⭐ 推荐使用。作为 Epic 官方维护的虚拟制片设备插件，代码质量有保障，且仍在活跃迭代

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices/Tests)