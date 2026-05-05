# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 插件为 MetaHuman 数字人系统提供实时动画数据流传输能力。它基于 UE 的 Live Link 框架，实现了从外部设备（如 iPhone 的 ARKit 面部追踪）到 MetaHuman 角色的实时面部动画驱动。

该插件解决的核心问题是：**如何将实时捕捉的面部表情数据流式传输到 MetaHuman 角色上，实现数字人的实时动画驱动**。

插件包含以下关键功能模块：
- **设备发现**：自动发现网络上的 Live Link Face 应用设备
- **数据源连接**：建立与 Live Link Face 应用的连接，接收面部追踪数据
- **本地处理**：支持本地面部动画数据的处理和转换
- **编辑器集成**：提供编辑器工具用于配置和预览实时动画

## 使用场景

- 你正在使用 MetaHuman Creator 创建数字人角色，需要实时驱动面部动画 → 使用 MetaHumanLiveLink
- 你有一个 iPhone 设备运行 Live Link Face 应用，想要实时捕捉面部表情到 UE 中的 MetaHuman 角色 → 使用 LiveLinkFaceSource
- 你需要在多人场景中同时驱动多个 MetaHuman 角色的面部动画 → 使用 MetaHumanLiveLinkSource
- 你想要在本地处理面部动画数据，不依赖网络连接 → 使用 MetaHumanLocalLiveLinkSource
- 你正在开发虚拟直播或实时数字人应用 → 使用 MetaHumanLiveLink

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateLiveLinkFaceSource` | 创建 Live Link Face 数据源，连接 iPhone 设备 | `ULiveLinkFaceSourceFactory` |
| `CreateMetaHumanLiveLinkSource` | 创建 MetaHuman Live Link 数据源 | `UMetaHumanLiveLinkSourceFactory` |
| `CreateLocalLiveLinkSource` | 创建本地 Live Link 数据源 | `UMetaHumanLocalLiveLinkSourceFactory` |
| `GetDiscoveredDevices` | 获取已发现的设备列表 | `ULiveLinkFaceDiscovery` |
| `ConnectToDevice` | 连接到指定设备 | `ULiveLinkFaceSource` |
| `DisconnectFromDevice` | 断开与设备的连接 | `ULiveLinkFaceSource` |
| `IsConnected` | 检查是否已连接 | `ULiveLinkFaceSource` |
| `GetFaceTrackingData` | 获取面部追踪数据 | `ULiveLinkFaceSource` |

### 使用示例（蓝图描述）

**连接 iPhone 设备并驱动 MetaHuman 面部动画：**

1. 在蓝图中创建 `CreateLiveLinkFaceSource` 节点
2. 使用 `GetDiscoveredDevices` 节点获取可用设备列表
3. 选择目标设备，调用 `ConnectToDevice` 建立连接
4. 在 MetaHuman 角色的动画蓝图中，使用 Live Link 节点接收面部数据
5. 将 Live Link 数据连接到 MetaHuman 的面部动画控制器

**配置本地面部动画源：**

1. 创建 `CreateLocalLiveLinkSource` 节点
2. 设置本地数据源参数（如动画序列路径）
3. 将数据源连接到 MetaHuman 角色的 Live Link 组件

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkFaceSource.h"
#include "MetaHumanLiveLinkSource.h"
#include "MetaHumanLocalLiveLinkSource.h"
#include "LiveLinkFaceDiscovery.h"
```

### 基本用法

```cpp
// 创建 Live Link Face 数据源
// 来源: LiveLinkFaceSource 模块
ULiveLinkFaceSourceFactory* Factory = NewObject<ULiveLinkFaceSourceFactory>();
ILiveLinkSource* Source = Factory->CreateSource(FString("iPhone Device"));

// 连接到设备
ULiveLinkFaceSource* FaceSource = Cast<ULiveLinkFaceSource>(Source);
if (FaceSource)
{
    FaceSource->ConnectToDevice(FString("192.168.1.100"));
    
    // 检查连接状态
    if (FaceSource->IsConnected())
    {
        UE_LOG(LogTemp, Log, TEXT("Connected to Live Link Face device"));
    }
}

// 获取已发现的设备
// 来源: LiveLinkFaceDiscovery 模块
ULiveLinkFaceDiscovery* Discovery = NewObject<ULiveLinkFaceDiscovery>();
TArray<FDiscoveredDevice> Devices = Discovery->GetDiscoveredDevices();

for (const FDiscoveredDevice& Device : Devices)
{
    UE_LOG(LogTemp, Log, TEXT("Found device: %s at %s"), 
        *Device.Name, *Device.IPAddress);
}
```

### 进阶用法

```cpp
// 创建 MetaHuman Live Link 数据源
// 来源: MetaHumanLiveLinkSource 模块
UMetaHumanLiveLinkSourceFactory* MetaHumanFactory = NewObject<UMetaHumanLiveLinkSourceFactory>();
ILiveLinkSource* MetaHumanSource = MetaHumanFactory->CreateSource(FString("MetaHuman Source"));

// 创建本地 Live Link 数据源
// 来源: MetaHumanLocalLiveLinkSource 模块
UMetaHumanLocalLiveLinkSourceFactory* LocalFactory = NewObject<UMetaHumanLocalLiveLinkSourceFactory>();
ILiveLinkSource* LocalSource = LocalFactory->CreateSource(FString("Local Source"));

// 在动画蓝图中处理面部追踪数据
// 来源: LiveLinkFaceSource 模块
void UMyAnimInstance::ProcessFaceTrackingData(const FLiveLinkFaceFrameData& FrameData)
{
    // 获取面部混合形状数据
    const TMap<FName, float>& BlendShapes = FrameData.BlendShapes;
    
    // 应用到 MetaHuman 面部控制器
    for (const auto& Pair : BlendShapes)
    {
        // Pair.Key 是混合形状名称（如 "EyeBlinkLeft"）
        // Pair.Value 是权重值（0.0 - 1.0）
        SetBlendShapeWeight(Pair.Key, Pair.Value);
    }
    
    // 获取头部旋转数据
    FRotator HeadRotation = FrameData.HeadRotation;
    SetHeadRotation(HeadRotation);
}
```

## Demo 示例

### LiveLinkFaceConnection.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkFaceSource.h"
#include "LiveLinkFaceDiscovery.h"
#include "LiveLinkFaceConnection.generated.h"

UCLASS(BlueprintType, Blueprintable)
class ALiveLinkFaceConnection : public AActor
{
    GENERATED_BODY()

public:
    ALiveLinkFaceConnection();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    // 连接到 Live Link Face 设备
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|LiveLink")
    bool ConnectToDevice(const FString& DeviceIPAddress);

    // 断开连接
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|LiveLink")
    void Disconnect();

    // 检查连接状态
    UFUNCTION(BlueprintPure, Category = "MetaHuman|LiveLink")
    bool IsConnected() const;

    // 获取已发现的设备列表
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|LiveLink")
    TArray<FString> GetDiscoveredDevices() const;

    // 获取当前面部追踪数据
    UFUNCTION(BlueprintPure, Category = "MetaHuman|LiveLink")
    FFaceTrackingData GetCurrentFaceData() const;

protected:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    FString TargetDeviceIP;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    bool bAutoConnect = true;

private:
    UPROPERTY()
    ULiveLinkFaceSource* FaceSource;

    UPROPERTY()
    ULiveLinkFaceDiscovery* Discovery;

    FFaceTrackingData CurrentFaceData;
};
```

### LiveLinkFaceConnection.cpp

```cpp
#include "LiveLinkFaceConnection.h"
#include "LiveLinkFaceSource.h"
#include "LiveLinkFaceDiscovery.h"

ALiveLinkFaceConnection::ALiveLinkFaceConnection()
{
    PrimaryActorTick.bCanEverTick = true;
    FaceSource = nullptr;
    Discovery = nullptr;
}

void ALiveLinkFaceConnection::BeginPlay()
{
    Super::BeginPlay();

    // 创建设备发现对象
    Discovery = NewObject<ULiveLinkFaceDiscovery>(this);
    
    // 创建 Live Link Face 数据源
    FaceSource = NewObject<ULiveLinkFaceSource>(this);

    // 如果设置了自动连接，尝试连接到目标设备
    if (bAutoConnect && !TargetDeviceIP.IsEmpty())
    {
        ConnectToDevice(TargetDeviceIP);
    }
}

void ALiveLinkFaceConnection::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 如果已连接，获取最新的面部追踪数据
    if (FaceSource && FaceSource->IsConnected())
    {
        CurrentFaceData = FaceSource->GetFaceTrackingData();
        
        // 在这里处理面部数据，例如应用到 MetaHuman 角色
        // ProcessFaceData(CurrentFaceData);
    }
}

bool ALiveLinkFaceConnection::ConnectToDevice(const FString& DeviceIPAddress)
{
    if (!FaceSource)
    {
        UE_LOG(LogTemp, Error, TEXT("FaceSource is null"));
        return false;
    }

    bool bSuccess = FaceSource->ConnectToDevice(DeviceIPAddress);
    
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully connected to device: %s"), *DeviceIPAddress);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to connect to device: %s"), *DeviceIPAddress);
    }

    return bSuccess;
}

void ALiveLinkFaceConnection::Disconnect()
{
    if (FaceSource)
    {
        FaceSource->Disconnect();
        UE_LOG(LogTemp, Log, TEXT("Disconnected from Live Link Face device"));
    }
}

bool ALiveLinkFaceConnection::IsConnected() const
{
    return FaceSource && FaceSource->IsConnected();
}

TArray<FString> ALiveLinkFaceConnection::GetDiscoveredDevices() const
{
    TArray<FString> DeviceNames;
    
    if (Discovery)
    {
        TArray<FDiscoveredDevice> Devices = Discovery->GetDiscoveredDevices();
        for (const FDiscoveredDevice& Device : Devices)
        {
            DeviceNames.Add(Device.Name);
        }
    }

    return DeviceNames;
}

FFaceTrackingData ALiveLinkFaceConnection::GetCurrentFaceData() const
{
    return CurrentFaceData;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | UE Live Link 框架核心模块 |
| `LiveLinkInterface` | Live Link 接口定义 |
| `MetaHumanCore` | MetaHuman 核心功能模块 |
| `MetaHumanSDK` | MetaHuman SDK，提供面部动画数据结构 |
| `Networking` | 网络通信支持 |
| `Sockets` | Socket 通信支持 |
| `Json` | JSON 数据解析 |
| `MediaUtils` | 媒体工具函数 |
| `MediaAssets` | 媒体资产支持 |

## 维护状态

### 近期更新

```
- 09c462fbc626 GUI pass #rb robert.hillary
- fb15849136ed Audio solver mood refactoring
- 71c0fdfd700c [Backout] - CL46056783 [FYI] jon.cook #rnx Original CL Desc ----------------------------------------------------------------- Audio solver mood refactoring #rb jack.taylor
```

- GUI pass：对用户界面进行了优化和调整
- Audio solver mood refactoring：重构了音频求解器的情绪处理逻辑
- Backout：回退了之前的音频求解器重构更改

### 维护评价

**活跃维护** ✅

- **创建时间**：2025-02-05，非常新的插件
- **最近更新**：近期有 GUI 优化和功能重构，表明正在积极开发
- **维护状态**：活跃维护中，Epic Games 持续投入开发资源
- **已知问题**：作为新插件，可能存在一些边缘情况的 bug
- **推荐使用**：✅ 强烈推荐，这是 MetaHuman 生态系统的核心组件，对于需要实时驱动 MetaHuman 面部动画的项目是必需的

**注意事项**：
- 该插件依赖于 MetaHuman Creator 创建的角色资产
- 需要 iPhone 设备运行 Live Link Face 应用（或兼容的面部追踪设备）
- 网络连接质量会影响实时动画的流畅度

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-in-unreal-engine/)
- [Live Link 官方文档](https://docs.unrealengine.com/5.7/en-US/live-link-in-unreal-engine/)
- [Live Link Face 应用](https://apps.apple.com/app/live-link-face/id1495370836)

---

## 子模块文档

由于 MetaHumanLiveLink 是 xlarge 级别的插件（189 个源文件），以下是各子模块的详细说明：

### LiveLinkFaceDiscovery

**用途**：自动发现网络上的 Live Link Face 应用设备

**关键类**：
- `ULiveLinkFaceDiscovery`：设备发现管理器
- `FDiscoveredDevice`：已发现设备的数据结构

**功能**：
- 扫描本地网络上的 iOS 设备
- 提供设备列表和连接信息
- 支持设备状态监控

### LiveLinkFaceSource

**用途**：连接 iPhone 设备并接收面部追踪数据

**关键类**：
- `ULiveLinkFaceSource`：Live Link Face 数据源
- `ULiveLinkFaceSourceFactory`：数据源工厂类
- `FFaceTrackingData`：面部追踪数据结构

**功能**：
- 建立与 Live Link Face 应用的网络连接
- 接收实时面部混合形状数据
- 接收头部旋转和位置数据
- 数据格式转换和标准化

### LiveLinkFaceSourceEditor

**用途**：Live Link Face 数据源的编辑器工具

**关键类**：
- `ULiveLinkFaceSourceEditorSettings`：编辑器设置
- `SLiveLinkFaceSourceEditorWidget`：编辑器 UI 控件

**功能**：
- 提供设备连接配置界面
- 显示实时面部追踪预览
- 支持数据源参数调整

### MetaHumanLiveLinkSource

**用途**：MetaHuman 专用的 Live Link 数据源

**关键类**：
- `UMetaHumanLiveLinkSource`：MetaHuman Live Link 数据源
- `UMetaHumanLiveLinkSourceFactory`：数据源工厂类

**功能**：
- 处理 MetaHuman 特有的面部动画数据
- 支持 MetaHuman 面部骨骼映射
- 提供 MetaHuman 优化的数据传输

### MetaHumanLiveLinkSourceEditor

**用途**：MetaHuman Live Link 数据源的编辑器工具

**关键类**：
- `UMetaHumanLiveLinkSourceEditorSettings`：编辑器设置
- `SMetaHumanLiveLinkSourceEditorWidget`：编辑器 UI 控件

**功能**：
- MetaHuman 专用的配置界面
- 面部动画预览和调试工具
- MetaHuman 角色绑定配置

### MetaHumanLocalLiveLinkSource

**用途**：本地 MetaHuman 面部动画数据源

**关键类**：
- `UMetaHumanLocalLiveLinkSource`：本地数据源
- `UMetaHumanLocalLiveLinkSourceFactory`：数据源工厂类

**功能**：
- 从本地文件加载面部动画数据
- 支持离线预览和测试
- 不依赖网络连接的本地处理

### MetaHumanLocalLiveLinkSourceEditor

**用途**：本地 MetaHuman Live Link 数据源的编辑器工具

**关键类**：
- `UMetaHumanLocalLiveLinkSourceEditorSettings`：编辑器设置
- `SMetaHumanLocalLiveLinkSourceEditorWidget`：编辑器 UI 控件

**功能**：
- 本地数据源配置界面
- 动画文件选择和预览
- 本地数据源参数调整