# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Live Link 预设资产） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

---

## 用途

MetaHuman Live Link 插件提供了一套完整的实时面部捕捉数据流传输方案，将外部设备（如运行 Live Link Face 应用的 iPhone/iPad）的面部动画数据通过 Live Link 协议实时传输到 Unreal Engine 中的 MetaHuman 角色。

该插件解决的核心问题是：**如何将真实人脸的实时表情捕捉数据低延迟地映射到高保真 MetaHuman 面部模型上**。它包含设备发现、数据源连接、数据流处理和编辑器集成等完整链路，是 MetaHuman 实时驱动工作流的基础设施。

插件由 7 个模块组成，按职责可分为三层：

| 层级 | 模块 | 职责 |
|---|---|---|
| **发现层** | `LiveLinkFaceDiscovery` | 通过网络自动发现运行 Live Link Face 应用的设备 |
| **数据源层** | `LiveLinkFaceSource` | 连接 Live Link Face 应用，接收面部追踪数据 |
| | `MetaHumanLiveLinkSource` | 通用 MetaHuman Live Link 数据源 |
| | `MetaHumanLocalLiveLinkSource` | 本地 MetaHuman Live Link 数据源（无需外部设备） |
| **编辑器集成层** | `LiveLinkFaceSourceEditor` | Live Link Face 源的编辑器 UI 和设置面板 |
| | `MetaHumanLiveLinkSourceEditor` | MetaHuman Live Link 源的编辑器 UI |
| | `MetaHumanLocalLiveLinkSourceEditor` | 本地源的编辑器 UI |

## 使用场景

- **实时面部捕捉表演**：演员佩戴 iPhone（使用 Live Link Face 应用），其面部表情实时驱动场景中的 MetaHuman 角色，适用于虚拟制片和实时预览
- **直播/虚拟主播**：通过面部捕捉实时驱动 MetaHuman 虚拟形象进行直播
- **动画预览**：在最终渲染前快速预览面部动画效果，无需等待离线烘焙
- **本地测试**：使用 `MetaHumanLocalLiveLinkSource` 在没有外部捕捉设备的情况下进行开发和测试
- **多设备同时捕捉**：通过 `LiveLinkFaceDiscovery` 自动发现局域网内多个捕捉设备，支持多角色同时驱动

## 模块架构

### LiveLinkFaceDiscovery

负责网络设备发现。通过 mDNS/Bonjour 协议扫描局域网内运行 Live Link Face 应用的设备，提供设备列表和连接信息。支持周期性刷新和服务器过期检测。

### LiveLinkFaceSource

Live Link Face 应用的核心数据源模块。建立与 iOS 设备的连接，接收面部 Blendshape 数据并转换为 Live Link 帧数据。处理网络连接管理、数据解码和帧率同步。

### MetaHumanLiveLinkSource

通用的 MetaHuman Live Link 数据源。提供标准化的 MetaHuman 面部动画数据接口，支持从多种输入源接收数据并转换为 MetaHuman 兼容格式。

### MetaHumanLocalLiveLinkSource

本地数据源模块，允许在不连接外部设备的情况下创建 Live Link 源。适用于开发测试和离线预览场景。依赖 UnrealEd 模块。

### *Editor 模块

三个 Editor 模块分别对应三个数据源模块，提供：
- Live Link 面板中的自定义 UI
- 源配置的 Details 面板
- 设备发现结果的可视化展示
- 连接状态监控

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Live Link Face Source` | 创建 Live Link Face 数据源并连接到指定设备 | `ULiveLinkFaceSourceFactory` |
| `Get Discovered Devices` | 获取当前发现的所有 Live Link Face 设备列表 | `ULiveLinkFaceDiscovery` |
| `Connect to Device` | 连接到指定的发现设备 | `ULiveLinkFaceSource` |
| `Disconnect` | 断开当前 Live Link Face 连接 | `ULiveLinkFaceSource` |
| `Is Connected` | 查询当前连接状态 | `ULiveLinkFaceSource` |
| `Get Subject Names` | 获取可用的 Live Link 主题名称列表 | `UMetaHumanLiveLinkSource` |

### 使用示例

**基本连接流程（蓝图描述）**：

1. 在 BeginPlay 中，使用 `Get Discovered Devices` 节点获取可用设备列表
2. 将设备列表输出到 UI（如 ComboBox）供用户选择
3. 用户选择设备后，调用 `Create Live Link Face Source` 创建数据源
4. 在 Live Link 面板中确认 Subject 已出现并正在接收数据
5. 在 MetaHuman 角色的 AnimBP 中，使用 `Live Link Pose` 节点读取面部数据

**自动重连逻辑（蓝图描述）**：

1. 使用 Timer 每隔 N 秒调用 `Is Connected` 检查连接状态
2. 如果断开，调用 `Get Discovered Devices` 重新扫描
3. 如果之前连接的设备仍在列表中，自动调用 `Connect to Device` 重连

## C++ 用法

### 头文件引入

```cpp
// Live Link Face 发现
#include "LiveLinkFaceDiscovery.h"

// Live Link Face 数据源
#include "LiveLinkFaceSource.h"

// MetaHuman Live Link 数据源
#include "MetaHumanLiveLinkSource.h"

// Live Link 核心接口
#include "ILiveLinkClient.h"
#include "LiveLinkTypes.h"
```

### 基本用法

创建并连接 Live Link Face 数据源：

```cpp
// 创建 Live Link Face 数据源
// 参考 LiveLinkFaceSource 模块的源码模式

#include "LiveLinkFaceSource.h"
#include "ILiveLinkClient.h"

void FMyClass::ConnectToFaceCaptureDevice(const FString& DeviceAddress, uint16 Port)
{
    // 通过 Live Link 客户端创建数据源
    ILiveLinkClient* LiveLinkClient = &IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);
    
    if (LiveLinkClient)
    {
        // 创建 Face Source 并注册到 Live Link 系统
        TSharedPtr<FLiveLinkFaceSource> FaceSource = MakeShared<FLiveLinkFaceSource>(DeviceAddress, Port);
        LiveLinkClient->AddSource(FaceSource);
    }
}
```

### 进阶用法

设备发现与自动连接：

```cpp
#include "LiveLinkFaceDiscovery.h"

void FMyClass::SetupAutoDiscovery()
{
    // 创建设备发现实例
    Discovery = MakeUnique<FLiveLinkFaceDiscovery>();
    
    // 设置发现回调
    Discovery->OnDeviceDiscovered.AddLambda([this](const FLiveLinkFaceDeviceInfo& DeviceInfo)
    {
        UE_LOG(LogTemp, Log, TEXT("发现设备: %s (%s:%d)"), 
            *DeviceInfo.Name, *DeviceInfo.Address, DeviceInfo.Port);
        
        // 自动连接第一个发现的设备
        if (!bIsConnected)
        {
            ConnectToFaceCaptureDevice(DeviceInfo.Address, DeviceInfo.Port);
            bIsConnected = true;
        }
    });
    
    Discovery->OnDeviceLost.AddLambda([this](const FLiveLinkFaceDeviceInfo& DeviceInfo)
    {
        UE_LOG(LogTemp, Warning, TEXT("设备丢失: %s"), *DeviceInfo.Name);
        bIsConnected = false;
    });
    
    // 开始周期性刷新发现
    Discovery->StartDiscovery();
}
```

Subject 名称验证（基于最近的 commit 改进）：

```cpp
// MetaHuman Live Link Source 现在将 Subject 名称视为 UObject 名称并进行验证
// 确保名称符合 UObject 命名规范，避免特殊字符导致的问题

FName ValidatedSubjectName = MakeObjectNameSafe(*RawSubjectName);
```

## Demo 示例

完整的 MetaHuman 实时面部捕捉集成示例：

```cpp
// MyFaceCaptureComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LiveLinkFaceDiscovery.h"
#include "MyFaceCaptureComponent.generated.h"

UCLASS(ClassGroup=(MetaHuman), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyFaceCaptureComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyFaceCaptureComponent();

    // 蓝图可调用：开始设备发现
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|FaceCapture")
    void StartDeviceDiscovery();

    // 蓝图可调用：连接到指定设备
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|FaceCapture")
    void ConnectToDevice(const FString& DeviceAddress, int32 Port);

    // 蓝图可调用：断开连接
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|FaceCapture")
    void Disconnect();

    // 蓝图可读：当前连接状态
    UPROPERTY(BlueprintReadOnly, Category = "MetaHuman|FaceCapture")
    bool bIsConnected = false;

    // 蓝图可读：已发现的设备列表
    UPROPERTY(BlueprintReadOnly, Category = "MetaHuman|FaceCapture")
    TArray<FString> DiscoveredDeviceNames;

    // 设备发现事件
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDeviceFound, const FString&, DeviceName);
    
    UPROPERTY(BlueprintAssignable, Category = "MetaHuman|FaceCapture")
    FOnDeviceFound OnDeviceFound;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TUniquePtr<FLiveLinkFaceDiscovery> DeviceDiscovery;
    
    UFUNCTION()
    void OnDeviceDiscovered(const FString& DeviceName, const FString& Address, int32 Port);
};
```

```cpp
// MyFaceCaptureComponent.cpp
#include "MyFaceCaptureComponent.h"
#include "ILiveLinkClient.h"
#include "LiveLinkFaceSource.h"

UMyFaceCaptureComponent::UMyFaceCaptureComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyFaceCaptureComponent::BeginPlay()
{
    Super::BeginPlay();
    StartDeviceDiscovery();
}

void UMyFaceCaptureComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Disconnect();
    if (DeviceDiscovery)
    {
        DeviceDiscovery.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

void UMyFaceCaptureComponent::StartDeviceDiscovery()
{
    DeviceDiscovery = MakeUnique<FLiveLinkFaceDiscovery>();
    
    DeviceDiscovery->OnDeviceDiscovered.AddUObject(this, &UMyFaceCaptureComponent::OnDeviceDiscovered);
    DeviceDiscovery->StartDiscovery();
}

void UMyFaceCaptureComponent::OnDeviceDiscovered(const FString& DeviceName, const FString& Address, int32 Port)
{
    DiscoveredDeviceNames.AddUnique(DeviceName);
    OnDeviceFound.Broadcast(DeviceName);
    
    UE_LOG(LogTemp, Log, TEXT("MetaHuman Face Capture: 发现设备 %s at %s:%d"), 
        *DeviceName, *Address, Port);
}

void UMyFaceCaptureComponent::ConnectToDevice(const FString& DeviceAddress, int32 Port)
{
    ILiveLinkClient* LiveLinkClient = &IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(
        ILiveLinkClient::ModularFeatureName);
    
    if (LiveLinkClient)
    {
        auto FaceSource = MakeShared<FLiveLinkFaceSource>(DeviceAddress, Port);
        LiveLinkClient->AddSource(FaceSource);
        bIsConnected = true;
        
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Face Capture: 已连接到 %s:%d"), 
            *DeviceAddress, Port);
    }
}

void UMyFaceCaptureComponent::Disconnect()
{
    bIsConnected = false;
    DiscoveredDeviceNames.Empty();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心框架，提供数据传输和源管理 |
| `LiveLinkInterface` | Live Link 接口定义，Subject 和帧数据类型 |
| `LiveLinkComponents` | Live Link 组件，用于在 Actor 上接收数据 |
| `MetaHumanCore` | MetaHuman 核心库，面部骨骼和 Blendshape 定义 |
| `UnrealEd` | 编辑器框架（MetaHumanLocalLiveLinkSource 依赖） |

## 维护状态

### 近期更新

```
- 0b432ee8a8cd Treat subject names as UObject names and validate as such in the MetaHuman Live Link Sources
  → 修复 Subject 名称验证，确保符合 UObject 命名规范，避免特殊字符问题
- 43a7589ac777 Prevent intermittent editor crash when double clicking on a discovered device
  → 修复双击已发现设备时的偶发编辑器崩溃
- be9e554712ac Add periodic refresh and server expiry to LiveLinkFaceDiscovery
  → 为设备发现添加周期性刷新和服务器过期机制，改善发现可靠性
```

### 维护评价

**活跃维护** ✅

- **创建时间**：2025 年 2 月，是一个相对较新的插件
- **更新频率**：近期有多次实质性更新，包括功能改进（周期性刷新）和稳定性修复（崩溃修复、名称验证）
- **开发状态**：处于积极开发阶段，持续修复问题和完善功能
- **已知限制**：
  - 所有模块均标记为 Runtime 类型，包括 Editor 模块，这可能在纯 Runtime 构建中引入不必要的依赖
  - 依赖 iOS 端 Live Link Face 应用，跨平台支持有限
  - Subject 名称验证最近才修复，早期版本可能存在命名问题
- **推荐程度**：强烈推荐用于 MetaHuman 实时面部捕捉工作流。作为 Epic 官方维护的插件，与 MetaHuman 生态深度集成，是虚拟制片和实时表演的标准方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-in-unreal-engine/)
- [Live Link 官方文档](https://docs.unrealengine.com/5.7/en-US/live-link-in-unreal-engine/)
- [Live Link Face App (iOS)](https://apps.apple.com/app/live-link-face/id1495892446)