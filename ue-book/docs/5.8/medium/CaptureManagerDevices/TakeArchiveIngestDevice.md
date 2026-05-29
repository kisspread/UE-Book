# Capture Manager Devices

> The Capture Manager Devices contains devices that can be used from the Capture Manager layout of the LiveLink Hub

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理设备集 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CPSLiveLinkDevice` (Runtime), `MonoVideoIngestDevice` (Runtime), `StereoVideoIngestDevice` (Runtime), `TakeArchiveIngestDevice` (Runtime), `VideoLiveLinkDeviceCommon` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices) | |

## 用途

Capture Manager Devices 是 LiveLink Hub 中 Capture Manager 布局的核心设备插件，提供了一系列用于虚拟制片中数据采集的 Live Link 设备类型。它解决了以下问题：

- **视频采集**：支持单目（Mono）和双目（Stereo）视频数据的实时采集与 Live Link 传输
- **Take 归档管理**：解析和摄取 `.cptake` 格式的 take 归档文件以及旧版 Capture Manager 的 take 数据
- **CPS 设备集成**：提供与 CPS（Camera Positioning System）设备的 Live Link 连接

这些设备统一基于 Live Link 框架，实现了连接管理（Connection）和数据摄取（Ingest）两种能力接口，可在 LiveLink Hub 的 Capture Manager 面板中集中管理。

## 使用场景

- 你在使用 LiveLink Hub 进行虚拟制片的面部/动作捕捉录制 → 通过 MonoVideoIngestDevice 实时接收单路视频流
- 你需要将录制的 take 数据（`.cptake` 文件）批量导入到项目中 → 使用 TakeArchiveIngestDevice 配置目录路径后一键摄取
- 你使用双目立体相机进行深度/立体视频采集 → 使用 StereoVideoIngestDevice 处理双路视频输入
- 你需要连接 Camera Positioning System 设备进行摄像机追踪 → 通过 CPSLiveLinkDevice 建立 Live Link 连接
- 你正在搭建 Capture Manager 的自定义设备扩展 → 基于 VideoLiveLinkDeviceCommon 的通用功能进行开发

**注意**：此插件默认未启用（`EnabledByDefault: false`），需要在 Plugins 面板或项目配置中手动启用。

## 蓝图用法

此插件通过 Live Link 设备系统与蓝图交互，主要暴露设备设置和连接管理能力。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSettings` | 获取 Take Archive Ingest 设备的配置参数（包含 TakeDirectory 路径） | `UTakeArchiveIngestDevice` |
| `GetDeviceHealth` | 查询设备当前健康状态 | `UTakeArchiveIngestDevice` |
| `GetHealthText` | 获取设备健康状态的文本描述 | `UTakeArchiveIngestDevice` |
| `Connect` | 建立设备连接 | `UTakeArchiveIngestDevice` |
| `Disconnect` | 断开设备连接 | `UTakeArchiveIngestDevice` |
| `RunUpdateTakeList` | 更新可用的 take 列表 | `UTakeArchiveIngestDevice` |
| `RunConvertAndUploadTake` | 执行 take 数据的转换和上传 | `UTakeArchiveIngestDevice` |

### 使用示例（蓝图描述）

**配置 Take 目录并摄取**：
1. 在 LiveLink Hub 的 Capture Manager 面板中，添加一个 "Take Archive Ingest" 设备
2. 在设备设置中，设置 `TakeDirectory` 指向包含 `.cptake` 文件的目录路径
3. 设备会自动扫描目录，通过 `RunUpdateTakeList` 刷新可用的 take 列表
4. 选择目标 take，调用 `RunConvertAndUploadTake` 将数据转换并上传到项目中

**连接状态监控**：
1. 使用 `GetDeviceHealth` 节点定期检查设备健康状态
2. 根据返回的 `EDeviceHealth` 枚举值在 UI 上显示连接状态指示器
3. 使用 `GetHealthText` 获取可读的状态文本用于界面展示

## C++ 用法

### 头文件引入

```cpp
#include "TakeArchiveIngestDevice.h"
#include "TakeArchiveIngestDeviceLog.h"
```

### 基本用法

基于源码中 `UTakeArchiveIngestDeviceSettings` 和 `UTakeArchiveIngestDevice` 的实现：

```cpp
// 来源: Private/TakeArchiveIngestDevice.h

// 获取设备设置
const UTakeArchiveIngestDeviceSettings* Settings = TakeArchiveDevice->GetSettings();
FString DirectoryPath = Settings->TakeDirectory.Path;

// 检查设备健康状态
EDeviceHealth Health = TakeArchiveDevice->GetDeviceHealth();
FText HealthText = TakeArchiveDevice->GetHealthText();

// 连接管理
bool bConnected = TakeArchiveDevice->Connect();
// ... 使用设备 ...
bool bDisconnected = TakeArchiveDevice->Disconnect();
```

### 进阶用法

继承并实现自定义 ingest 设备，参考 TakeArchiveIngestDevice 的接口实现模式：

```cpp
// 继承 UBaseIngestLiveLinkDevice 并实现连接能力接口
UCLASS(BlueprintType, meta = (DisplayName = "Custom Ingest Device"))
class UCustomIngestDevice final : public UBaseIngestLiveLinkDevice
    , public ILiveLinkDeviceCapability_Connection
{
    GENERATED_BODY()

public:
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override;
    virtual EDeviceHealth GetDeviceHealth() const override;
    virtual FText GetHealthText() const override;

private:
    // 实现 Ingest 能力接口
    virtual void RunConvertAndUploadTake(const UIngestCapability_ProcessHandle* InProcessHandle,
                                         const UIngestCapability_Options* InIngestOptions) override;
    virtual void RunUpdateTakeList(UIngestCapability_UpdateTakeListCallback* InCallback) override;

    // 实现 Connection 能力接口
    virtual ELiveLinkDeviceConnectionStatus GetConnectionStatus_Implementation() const override;
    virtual FString GetHardwareId_Implementation() const override;
    virtual bool SetHardwareId_Implementation(const FString& HardwareID) override;
    virtual bool Connect_Implementation() override;
    virtual bool Disconnect_Implementation() override;
};
```

## Demo 示例

```cpp
// TakeArchiveDemoDevice.h
#pragma once

#include "CoreMinimal.h"
#include "TakeArchiveIngestDevice.h"

// 演示如何查询 Take Archive Ingest 设备的状态
UCLASS(BlueprintType)
class UTakeArchiveDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    // 通过蓝图设置设备引用
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Capture")
    UTakeArchiveIngestDevice* TakeArchiveDevice;

    UFUNCTION(BlueprintCallable, Category = "Capture")
    void QueryDeviceStatus();

    UFUNCTION(BlueprintCallable, Category = "Capture")
    void ListAvailableTakes();
};
```

```cpp
// TakeArchiveDemoDevice.cpp
#include "TakeArchiveDemoDevice.h"

void UTakeArchiveDemoComponent::QueryDeviceStatus()
{
    if (!TakeArchiveDevice)
    {
        UE_LOG(LogTakeArchiveIngestDevice, Warning, TEXT("TakeArchiveDevice is null"));
        return;
    }

    // 检查连接状态
    ELiveLinkDeviceConnectionStatus Status = TakeArchiveDevice->GetConnectionStatus();
    UE_LOG(LogTakeArchiveIngestDevice, Log, TEXT("Connection Status: %d"), static_cast<int32>(Status));

    // 获取健康状态
    EDeviceHealth Health = TakeArchiveDevice->GetDeviceHealth();
    FText HealthText = TakeArchiveDevice->GetHealthText();
    UE_LOG(LogTakeArchiveIngestDevice, Log, TEXT("Device Health: %s"), *HealthText.ToString());

    // 读取配置
    const UTakeArchiveIngestDeviceSettings* Settings = TakeArchiveDevice->GetSettings();
    if (Settings)
    {
        UE_LOG(LogTakeArchiveIngestDevice, Log, TEXT("Take Directory: %s"), *Settings->TakeDirectory.Path);
    }
}

void UTakeArchiveDemoComponent::ListAvailableTakes()
{
    if (!TakeArchiveDevice)
    {
        return;
    }

    // 触发 take 列表更新
    TakeArchiveDevice->RunUpdateTakeList(nullptr);
}
```

## 模块依赖

此插件包含 5 个 Runtime 模块，各模块之间存在层级关系：

| 模块 | 用途 |
|---|---|
| `VideoLiveLinkDeviceCommon` | 视频 Live Link 设备的公共基础功能（被其他视频设备模块依赖） |
| `CaptureManagerCore` | Capture Manager 核心框架，提供 take 管理和摄取基础设施 |
| `LiveLinkInterface` | Live Link 设备接口定义 |
| `LiveLinkHubMessaging` | LiveLink Hub 通信协议支持 |

> 各子模块的具体依赖关系详见各自的 Build.cs。使用者需注意：此插件依赖 Capture Manager 生态中的多个核心模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `222ac128` | StereoVideoIngest: Fix component name consistency across ingest devices | 修复双目视频摄取设备的组件名称一致性问题 |
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore | 在 CaptureManagerCore 中添加 CPS 客户端模块 |
| 2026-04-27 | `778f07fc` | [CaptureManager] Fix log category ODR violations in video devices | 修复视频设备中日志分类的 ODR 违规问题 |
| 2026-04-27 | `334822cd` | Add ConfigureMediaSource virtual hook to ULiveLinkFaceDevice | 为 LiveLink Face 设备添加 ConfigureMediaSource 虚函数钩子 |
| 2026-04-21 | `40065f3e` | Added connection indicator for Live Link Face devices | 为 Live Link Face 设备添加连接状态指示器 |

### 维护评价

- **活跃维护**：插件创建于 2025 年 2 月，至今约 1 年，最近 1 个月内有多次实质性更新
- **开发状态**：持续添加新功能（CPS 客户端模块、连接指示器）并修复问题（组件命名、ODR 违规）
- **成熟度**：已非实验性状态（`IsBetaVersion: false`），但默认未启用（`EnabledByDefault: false`），表明可能仍在逐步稳定中
- **推荐程度**：✅ 推荐用于使用 Capture Manager / LiveLink Hub 进行虚拟制片数据采集的项目。默认未启用，需手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices)
- 官方文档：暂无
- 测试用例：暂未发现独立测试文件