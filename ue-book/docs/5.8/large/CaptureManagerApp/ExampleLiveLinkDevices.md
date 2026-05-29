# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例设备、设置资产） |
| 模块 | `CaptureManagerEditor` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

CaptureManagerApp 是虚幻引擎虚拟制片工作流中的**捕获设备管理中枢**。它解决了从外部捕获设备（如动作捕捉、面部捕捉等）获取数据并导入引擎的完整管线问题。

核心职责包括：
- **设备发现与连接**：通过 LiveLink 设备框架发现、连接和监控捕获硬件设备
- **数据获取（Ingest）**：从设备获取原始捕获数据（Take），管理 Take 列表
- **转码处理**：将设备原始数据转码为引擎可导入的格式
- **上传与导入**：将处理后的数据上传至 Unreal 进行最终导入

该插件基于 LiveLink 设备能力接口体系（LiveLink Device Capabilities），通过组合 `Connection`、`Recording`、`Ingest` 等能力接口来定义不同类型的捕获设备。

## 使用场景

- 你在搭建虚拟制片管线，需要将动捕/面捕设备的数据导入 UE → 用 CaptureManagerApp
- 你需要自定义捕获设备适配器，支持特定厂商的硬件 → 参考 ExampleLiveLinkDevices 模块创建自己的设备类
- 你需要管理多台捕获设备的连接状态、录制状态和数据获取流程 → 用 CaptureManagerApp 的设备管理框架
- 你需要对捕获数据进行转码后批量导入引擎 → 用 CaptureManagerApp 的 Ingest 管线

## 蓝图用法

本插件以 C++ 框架为主，示例设备类不暴露 BlueprintCallable 函数。设备管理主要通过编辑器 UI 和 LiveLink 设备框架进行操作。

### 核心类

| 类 | 说明 |
|---|---|
| `UExampleNetworkIngestDevice` | 示例网络摄取设备，演示如何实现连接、录制和数据获取三大能力 |
| `UExampleNetworkIngestDeviceSettings` | 示例设备设置，包含 IP 地址和端口配置 |
| `UBaseIngestLiveLinkDevice` | 摄取设备基类，所有 Ingest 设备的父类 |

### 设备能力接口

| 接口 | 说明 |
|---|---|
| `ILiveLinkDeviceCapability_Connection` | 连接能力：管理设备的连接/断开和状态查询 |
| `ILiveLinkDeviceCapability_Recording` | 录制能力：控制设备的录制开始/停止 |
| Ingest（通过 `UBaseIngestLiveLinkDevice`） | 数据获取能力：获取 Take 列表、转码上传数据 |

## C++ 用法

### 头文件引入

```cpp
#include "ExampleNetworkIngestDevice.h"  // 示例设备
#include "LiveLinkDeviceSettings.h"       // 设备设置基类
#include "BaseIngestLiveLinkDevice.h"     // Ingest 设备基类
```

### 基本用法 —— 创建自定义捕获设备

参考 `ExampleLiveLinkDevices` 模块，创建自定义设备需要两步：定义设置类和设备类。

**来源**: `Source/ExampleLiveLinkDevices/Private/NetworkIngest/ExampleNetworkIngestDevice.h`

```cpp
// 1. 定义设备设置类
UCLASS()
class UMyCaptureDeviceSettings : public ULiveLinkDeviceSettings
{
    GENERATED_BODY()

public:
    UMyCaptureDeviceSettings()
    {
        DisplayName = TEXT("My Capture Device");
    }

    // 设备自定义属性
    UPROPERTY(EditAnywhere, Category = "My Capture Device")
    FString IpAddress;

    UPROPERTY(EditAnywhere, Category = "My Capture Device")
    uint16 Port = 14785;
};

// 2. 定义设备类，继承基类并实现所需能力接口
UCLASS()
class UMyCaptureDevice : public UBaseIngestLiveLinkDevice
    , public ILiveLinkDeviceCapability_Connection    // 连接能力
    , public ILiveLinkDeviceCapability_Recording     // 录制能力
{
    GENERATED_BODY()

public:
    // 获取设置类类型
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override;

    // 设备显示信息
    virtual FText GetDisplayName() const override;
    virtual EDeviceHealth GetDeviceHealth() const override;
    virtual FText GetHealthText() const override;

    // 设备生命周期
    virtual void OnDeviceAdded() override;
    virtual void OnDeviceRemoved() override;
    virtual void OnSettingChanged(const FPropertyChangedEvent& InPropertyChangedEvent) override;
};
```

### 进阶用法 —— 实现 Ingest（数据获取）流程

Ingest 流程是 CaptureManager 的核心功能，涉及获取 Take 列表和转码上传数据。

**来源**: `Source/ExampleLiveLinkDevices/Private/NetworkIngest/ExampleNetworkIngestDevice.h`

```cpp
// 实现 Take 列表获取
void UMyCaptureDevice::RunUpdateTakeList(UIngestCapability_UpdateTakeListCallback* InCallback)
{
    // 从设备获取可用的 Take 列表
    // 通过 InCallback 回调返回结果
    // 通常需要网络请求设备，异步返回
}

// 实现转码上传
void UMyCaptureDevice::RunConvertAndUploadTake(
    const UIngestCapability_ProcessHandle* InProcessHandle,
    const UIngestCapability_Options* InIngestOptions)
{
    // 1. 获取 Take 的原始数据
    // 2. 转码为目标格式
    // 3. 上传至 Unreal 导入管线
    // InProcessHandle 用于进度报告和取消支持
}

// 取消正在进行的 Ingest 流程
void UMyCaptureDevice::CancelIngestProcess_Implementation(
    const UIngestCapability_ProcessHandle* InProcessHandle)
{
    // 安全取消当前转码/上传操作
}

// 获取 Take 的完整文件路径
FString UMyCaptureDevice::GetFullTakePath(UE::CaptureManager::FTakeId InTakeId) const
{
    // 根据 TakeId 构建完整的本地/远程文件路径
    return FString();
}
```

### 进阶用法 —— 实现 Connection（连接）和 Recording（录制）

```cpp
// ---- 连接接口实现 ----

ELiveLinkDeviceConnectionStatus UMyCaptureDevice::GetConnectionStatus_Implementation() const
{
    // 返回当前连接状态：Connected / Disconnected / Connecting
    return ELiveLinkDeviceConnectionStatus::Disconnected;
}

bool UMyCaptureDevice::Connect_Implementation()
{
    // 使用设置中的 IpAddress 和 Port 建立连接
    const UMyCaptureDeviceSettings* Settings = GetSettings();
    // ... 网络连接逻辑
    return true;
}

bool UMyCaptureDevice::Disconnect_Implementation()
{
    // 断开与设备的连接
    return true;
}

FString UMyCaptureDevice::GetHardwareId_Implementation() const
{
    // 返回设备唯一标识符（如 MAC 地址或序列号）
    return TEXT("");
}

bool UMyCaptureDevice::SetHardwareId_Implementation(const FString& HardwareID)
{
    // 设置设备硬件标识
    return true;
}

// ---- 录制接口实现 ----

bool UMyCaptureDevice::StartRecording_Implementation()
{
    // 向设备发送开始录制指令
    return true;
}

bool UMyCaptureDevice::StopRecording_Implementation()
{
    // 向设备发送停止录制指令
    return true;
}

bool UMyCaptureDevice::IsRecording_Implementation() const
{
    // 查询设备当前录制状态
    return false;
}
```

## Demo 示例

以下是一个完整的最小自定义网络摄取设备实现。

**MyNetworkDevice.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "BaseIngestLiveLinkDevice.h"
#include "LiveLinkDeviceSettings.h"
#include "LiveLinkDeviceCapability_Connection.h"
#include "LiveLinkDeviceCapability_Recording.h"
#include "MyNetworkDevice.generated.h"

UCLASS()
class UMyNetworkDeviceSettings : public ULiveLinkDeviceSettings
{
    GENERATED_BODY()

public:
    UMyNetworkDeviceSettings()
    {
        DisplayName = TEXT("My Network Device");
    }

    UPROPERTY(EditAnywhere, Category = "Network")
    FString ServerAddress = TEXT("192.168.1.100");

    UPROPERTY(EditAnywhere, Category = "Network")
    uint16 ServerPort = 14785;
};

UCLASS()
class UMyNetworkDevice : public UBaseIngestLiveLinkDevice
    , public ILiveLinkDeviceCapability_Connection
    , public ILiveLinkDeviceCapability_Recording
{
    GENERATED_BODY()

public:
    const UMyNetworkDeviceSettings* GetSettings() const;

    // ULiveLinkDevice interface
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override;
    virtual FText GetDisplayName() const override;
    virtual EDeviceHealth GetDeviceHealth() const override;
    virtual FText GetHealthText() const override;
    virtual void OnDeviceAdded() override;
    virtual void OnDeviceRemoved() override;
    virtual void OnSettingChanged(const FPropertyChangedEvent& InPropertyChangedEvent) override;

protected:
    virtual FString GetFullTakePath(UE::CaptureManager::FTakeId InTakeId) const override;

    // Ingest
    virtual void RunUpdateTakeList(UIngestCapability_UpdateTakeListCallback* InCallback) override;
    virtual void RunConvertAndUploadTake(const UIngestCapability_ProcessHandle* InProcessHandle,
                                         const UIngestCapability_Options* InIngestOptions) override;
    virtual void CancelIngestProcess_Implementation(const UIngestCapability_ProcessHandle* InProcessHandle) override;

    // Connection
    virtual ELiveLinkDeviceConnectionStatus GetConnectionStatus_Implementation() const override;
    virtual FString GetHardwareId_Implementation() const override;
    virtual bool SetHardwareId_Implementation(const FString& HardwareID) override;
    virtual bool Connect_Implementation() override;
    virtual bool Disconnect_Implementation() override;

    // Recording
    virtual bool StartRecording_Implementation() override;
    virtual bool StopRecording_Implementation() override;
    virtual bool IsRecording_Implementation() const override;

private:
    ELiveLinkDeviceConnectionStatus ConnectionStatus = ELiveLinkDeviceConnectionStatus::Disconnected;
    bool bIsRecording = false;
};
```

**MyNetworkDevice.cpp**

```cpp
#include "MyNetworkDevice.h"

const UMyNetworkDeviceSettings* UMyNetworkDevice::GetSettings() const
{
    return Cast<UMyNetworkDeviceSettings>(Super::GetSettings());
}

TSubclassOf<ULiveLinkDeviceSettings> UMyNetworkDevice::GetSettingsClass() const
{
    return UMyNetworkDeviceSettings::StaticClass();
}

FText UMyNetworkDevice::GetDisplayName() const
{
    return FText::FromString(TEXT("My Network Device"));
}

EDeviceHealth UMyNetworkDevice::GetDeviceHealth() const
{
    if (ConnectionStatus == ELiveLinkDeviceConnectionStatus::Connected)
    {
        return EDeviceHealth::Nominal;
    }
    return EDeviceHealth::Error;
}

FText UMyNetworkDevice::GetHealthText() const
{
    if (ConnectionStatus == ELiveLinkDeviceConnectionStatus::Connected)
    {
        return FText::FromString(TEXT("Connected"));
    }
    return FText::FromString(TEXT("Disconnected"));
}

void UMyNetworkDevice::OnDeviceAdded()
{
    Super::OnDeviceAdded();
    // 设备添加时自动尝试连接
    Connect_Implementation();
}

void UMyNetworkDevice::OnDeviceRemoved()
{
    Disconnect_Implementation();
    Super::OnDeviceRemoved();
}

void UMyNetworkDevice::OnSettingChanged(const FPropertyChangedEvent& InPropertyChangedEvent)
{
    Super::OnSettingChanged(InPropertyChangedEvent);
    // IP 或端口变化时重新连接
    if (ConnectionStatus == ELiveLinkDeviceConnectionStatus::Connected)
    {
        Disconnect_Implementation();
        Connect_Implementation();
    }
}

FString UMyNetworkDevice::GetFullTakePath(UE::CaptureManager::FTakeId InTakeId) const
{
    return FString::Printf(TEXT("/Captures/Take_%d"), InTakeId);
}

void UMyNetworkDevice::RunUpdateTakeList(UIngestCapability_UpdateTakeListCallback* InCallback)
{
    // 异步从设备获取 Take 列表
    // 调用 InCallback 完成后返回结果
}

void UMyNetworkDevice::RunConvertAndUploadTake(
    const UIngestCapability_ProcessHandle* InProcessHandle,
    const UIngestCapability_Options* InIngestOptions)
{
    // 获取原始数据 → 转码 → 上传
}

void UMyNetworkDevice::CancelIngestProcess_Implementation(
    const UIngestCapability_ProcessHandle* InProcessHandle)
{
    // 取消当前处理流程
}

ELiveLinkDeviceConnectionStatus UMyNetworkDevice::GetConnectionStatus_Implementation() const
{
    return ConnectionStatus;
}

FString UMyNetworkDevice::GetHardwareId_Implementation() const
{
    const UMyNetworkDeviceSettings* Settings = GetSettings();
    return Settings ? FString::Printf(TEXT("%s:%d"), *Settings->ServerAddress, Settings->ServerPort) : TEXT("");
}

bool UMyNetworkDevice::SetHardwareId_Implementation(const FString& HardwareID)
{
    // 解析 HardwareID 设置地址和端口
    return true;
}

bool UMyNetworkDevice::Connect_Implementation()
{
    ConnectionStatus = ELiveLinkDeviceConnectionStatus::Connected;
    // 实际连接逻辑...
    return true;
}

bool UMyNetworkDevice::Disconnect_Implementation()
{
    ConnectionStatus = ELiveLinkDeviceConnectionStatus::Disconnected;
    bIsRecording = false;
    return true;
}

bool UMyNetworkDevice::StartRecording_Implementation()
{
    bIsRecording = true;
    return true;
}

bool UMyNetworkDevice::StopRecording_Implementation()
{
    bIsRecording = false;
    return true;
}

bool UMyNetworkDevice::IsRecording_Implementation() const
{
    return bIsRecording;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLink 设备框架基础 |
| `LiveLinkDevice` | 设备基类 `ULiveLinkDevice` 和设备设置 |
| `CaptureManagerCore` | CaptureManager 核心数据类型（如 `FTakeId`、`UIngestCapability_*`） |
| `UnrealEd` | LiveLinkCapabilities 模块依赖（编辑器功能） |

无特殊依赖（除上述模块外，仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 向 CaptureManagerCore 添加 CPS 客户端模块 |
| 2026-04-28 | `6eba47f3` | [Capture Manager] Warn when Third Party Encoder is required for ingest | 数据获取需要第三方编码器时发出警告 |
| 2026-04-23 | `43d97726` | MediaProfile: Moved UMediaProfile and related entities to its own plugin to avoid dependency on Open | 将 MediaProfile 拆分为独立插件，减少 OpenEXR 依赖 |
| 2026-04-20 | `a8e2df25` | [CaptureManager] Add auto-rotation mode to ECaptureManagerRotation | 为旋转枚举添加自动旋转模式 |
| 2026-04-16 | `cf2dffa4` | [CaptureManager] Fix broken LLH encoder defaults. | 修复 LLH 编码器默认值错误 |

### 维护评价

- **创建时间**：2025-02-04，插件约 1 年历史
- **维护状态**：**活跃维护中** —— 最近一个月内有多次功能性更新和 bug 修复
- **更新频率**：高频更新，涵盖新功能（CPS 客户端、自动旋转）、改进（编码器警告）和修复（LLH 默认值）
- **已知问题**：LiveLinkCapabilities 模块依赖 UnrealEd，意味着该模块无法在打包版本中使用，属于编辑器专用功能
- **推荐度**：✅ 推荐使用 —— 作为 Epic 官方虚拟制片管线的核心组件，持续受到关注和维护。适合需要完整捕获设备管理流程的虚拟制片项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- 官方文档（无）