# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例设备实现） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

---

# ExampleLiveLinkDevices 模块文档

## 用途

ExampleLiveLinkDevices 是 CaptureManagerApp 插件中的**示例模块**，展示了如何为 LiveLink 系统实现自定义捕获设备。该模块提供了完整的设备实现模板，帮助开发者理解：

- 如何创建与 LiveLink 兼容的捕获设备
- 如何处理设备发现、连接和数据流
- 如何实现设备元数据和能力声明
- 如何集成到 CaptureManager 的工作流程中

该模块存在的目的是作为**参考实现**，让虚拟制片团队能够基于此模板快速开发支持新捕获硬件的 LiveLink 设备插件。

## 使用场景

- 你需要为新的动作捕捉设备创建 LiveLink 集成 → 参考 ExampleLiveLinkDevices 的实现模式
- 你在开发自定义相机追踪系统 → 基于此模块的设备发现和连接逻辑
- 你需要理解 CaptureManager 的设备抽象层 → 阅读此模块的接口实现
- 你想为虚拟制片流程添加新的数据源 → 使用此模块作为开发起点

## 蓝图用法

该模块主要作为 C++ 示例，不直接暴露蓝图节点。其设备实现会被 CaptureManagerEditor 模块通过 LiveLink 系统间接使用。

### 核心概念

| 概念 | 说明 |
|---|---|
| 设备发现 | 通过网络广播发现可用的捕获设备 |
| 设备连接 | 建立与捕获设备的通信连接 |
| 数据流 | 实时接收捕获数据（视频、音频、传感器） |
| 元数据 | 设备能力声明和配置信息 |

## C++ 用法

### 头文件引入

```cpp
#include "ExampleLiveLinkDevicesModule.h"
```

### 基本用法

该模块主要提供设备实现的参考代码，关键类包括：

```cpp
// 示例设备实现 - 展示如何创建 LiveLink 设备
// 参考: Source/ExampleLiveLinkDevices/ 目录下的实现

// 1. 设备发现接口实现
class FExampleNetworkDevice : public ILiveLinkDevice
{
    // 实现设备发现逻辑
    virtual void DiscoverDevices() override;
    
    // 设备连接管理
    virtual bool Connect(const FDeviceAddress& Address) override;
    
    // 数据流处理
    virtual void StartCapture() override;
    virtual void StopCapture() override;
};

// 2. 设备元数据定义
struct FExampleDeviceMetadata
{
    FString DeviceName;
    FString FirmwareVersion;
    TArray<FString> SupportedFormats;
    // ... 其他设备属性
};
```

### 进阶用法

结合 CaptureManagerPipeline 模块实现完整的捕获工作流：

```cpp
// 从 git history 可以看到，设备需要实现回调机制
// 参考 commit: 568b6321fb38 "Passing UpdateTakeList callback as a parameter"

// 设备实现需要支持 Take 列表更新回调
DECLARE_DELEGATE_OneParam(FOnTakeListUpdated, const TArray<FCaptureTake>&);

class FExampleLiveLinkDevice : public ILiveLinkDevice
{
public:
    // 设置 Take 列表更新回调
    void SetTakeListUpdateCallback(FOnTakeListUpdated Callback);
    
    // 当设备状态变化时通知上层
    void NotifyTakeListChanged();
    
    // 实现数据下载和转换的分离（参考 commit: 365fb2caa298）
    virtual void DownloadCaptureData(const FCaptureTake& Take) override;
    virtual void ConvertAndUpload(const FCaptureTake& Take) override;
};
```

## Demo 示例

### 最小设备实现示例

```cpp
// MyCaptureDevice.h
#pragma once

#include "CoreMinimal.h"
#include "LiveLinkDevice.h"
#include "MyCaptureDevice.generated.h"

UCLASS()
class MYPLUGIN_API UMyCaptureDevice : public ULiveLinkDevice
{
    GENERATED_BODY()

public:
    // 设备初始化
    virtual bool Initialize(const FDeviceSettings& Settings) override;
    
    // 设备发现
    virtual void DiscoverDevices() override;
    
    // 连接到设备
    virtual bool Connect(const FString& Address) override;
    
    // 断开连接
    virtual void Disconnect() override;
    
    // 获取设备状态
    virtual EDeviceState GetDeviceState() const override;
    
    // 获取设备元数据
    virtual FDeviceMetadata GetMetadata() const override;

private:
    // 设备连接句柄
    FDeviceConnectionHandle ConnectionHandle;
    
    // 设备配置
    FDeviceSettings CachedSettings;
};
```

```cpp
// MyCaptureDevice.cpp
#include "MyCaptureDevice.h"

bool UMyCaptureDevice::Initialize(const FDeviceSettings& Settings)
{
    CachedSettings = Settings;
    
    // 初始化设备通信
    // ...
    
    return true;
}

void UMyCaptureDevice::DiscoverDevices()
{
    // 实现网络广播发现
    // 或扫描已知设备列表
}

bool UMyCaptureDevice::Connect(const FString& Address)
{
    // 建立 TCP/UDP 连接
    ConnectionHandle = FDeviceConnection::Create(Address);
    
    if (ConnectionHandle.IsValid())
    {
        // 注册数据接收回调
        ConnectionHandle->OnDataReceived.AddUObject(
            this, &UMyCaptureDevice::HandleIncomingData);
        return true;
    }
    
    return false;
}

void UMyCaptureDevice::Disconnect()
{
    if (ConnectionHandle.IsValid())
    {
        ConnectionHandle->Close();
        ConnectionHandle.Reset();
    }
}

EDeviceState UMyCaptureDevice::GetDeviceState() const
{
    if (!ConnectionHandle.IsValid())
        return EDeviceState::Disconnected;
    
    return ConnectionHandle->IsConnected() 
        ? EDeviceState::Connected 
        : EDeviceState::Connecting;
}

FDeviceMetadata UMyCaptureDevice::GetMetadata() const
{
    FDeviceMetadata Metadata;
    Metadata.DeviceName = TEXT("My Custom Capture Device");
    Metadata.FirmwareVersion = TEXT("1.0.0");
    Metadata.SupportedFormats = { TEXT("H264"), TEXT("ProRes") };
    return Metadata;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLink 核心框架，提供设备接口和数据流 |
| `LiveLinkInterface` | LiveLink 接口定义 |
| `CaptureManagerPipeline` | 捕获管理器管道，处理数据转换和上传 |
| `LiveLinkCapabilities` | 设备能力声明系统 |

## 维护状态

### 近期更新

```
- 530bb4d3588a [CaptureManager] Fixed build breaks in ExampleNetworkIngestDevice
  修复了示例网络摄取设备的编译错误
- 365fb2caa298 Splitting the download from the convert/upload
  将下载逻辑与转换/上传逻辑分离，优化工作流
- 568b6321fb38 Passing UpdateTakeList callback as a parameter
  将 Take 列表更新回调作为参数传递，提高灵活性
```

### 维护评价

- **创建时间**: 2025-02-04，非常新的模块
- **维护状态**: 活跃维护中，近期有多次功能性更新
- **代码质量**: 作为示例模块，代码结构清晰，注释完善
- **推荐程度**: ⭐⭐⭐⭐⭐ 强烈推荐作为开发自定义 LiveLink 设备的起点

该模块是 CaptureManagerApp 的核心示例组件，展示了 Epic Games 推荐的设备集成模式。由于是示例代码，更新频率适中，主要用于反映框架接口的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/ExampleLiveLinkDevices)
- [CaptureManagerApp 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [LiveLink 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink)

---

## 子模块索引

由于 CaptureManagerApp 是 xlarge 规模插件（258 个源文件），包含 11 个模块，建议按需查阅各子模块文档：

| 模块 | 类型 | 用途 |
|---|---|---|
| [CaptureDataConverter](CaptureDataConverter.md) | Runtime | 捕获数据格式转换 |
| [CaptureManagerEditor](CaptureManagerEditor.md) | Runtime | 编辑器 UI 和工作流管理 |
| [CaptureManagerMediaRW](CaptureManagerMediaRW.md) | Runtime | 媒体读写操作 |
| [CaptureManagerPipeline](CaptureManagerPipeline.md) | Runtime | 捕获处理管道 |
| [CaptureManagerSettings](CaptureManagerSettings.md) | Runtime | 插件配置设置 |
| [CaptureManagerUnrealEndpoint](CaptureManagerUnrealEndpoint.md) | Runtime | Unreal 端点集成 |
| [ExampleLiveLinkDevices](ExampleLiveLinkDevices.md) | Runtime | 示例设备实现（本文档） |
| [IngestLiveLinkDevice](IngestLiveLinkDevice.md) | Runtime | 数据摄取设备 |
| [LiveLinkCapabilities](LiveLinkCapabilities.md) | Runtime | 设备能力声明 |
| [LiveLinkFaceMetadata](LiveLinkFaceMetadata.md) | Runtime | LiveLink Face 元数据 |
| [StereoCameraMetadata](StereoCameraMetadata.md) | Runtime | 立体相机元数据 |