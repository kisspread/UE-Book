# Mobile Location Services - IOS Implementation

> IOS implementation for blueprint access for location data from mobile devices

| 属性 | 值 |
|---|---|
| 中文名 | iOS定位服务 |
| 分类 | Mobile |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LocationServicesIOSEditor` (Editor), `LocationServicesIOSImpl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-12-09 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesIOSImpl) | |

## 用途

此插件是 Epic Games 为 `LocationServicesBPLibrary` 插件提供的 **iOS 平台具体实现**。它的核心作用是将 iOS 系统的原生定位框架 (Core Location) 封装起来，以便通过引擎的蓝图和 C++ API 统一访问 GPS 和位置数据。它解决了在 iOS 设备上通过标准接口获取精确地理位置信息的需求。

## 使用场景

- 你正在为 iOS 平台开发一款需要**获取用户实时地理位置**的应用（如地图、导航、社交、LBS游戏）。
- 你需要通过蓝图或 C++ 跨平台地查询设备位置，此插件是 `LocationServicesBPLibrary` 在 iOS 平台背后的实现者。
- 当项目设置中启用了位置服务权限（`NSLocationWhenInUseUsageDescription`），并需要实际读取 GPS 坐标、速度、方向等数据时。

## 蓝图用法

蓝图功能主要通过 `LocationServicesBPLibrary` 这个插件暴露，本插件是其底层实现。开发者通常直接与 `LocationServicesBPLibrary` 提供的节点交互。

### 核心节点

以下节点在 `LocationServicesBPLibrary` 中定义，其功能由本插件在 iOS 上实现：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLocationServicesImpl` | 获取当前平台的位置服务实现接口（在 iOS 上返回本插件的实例） | `ULocationServicesBPLibrary` |
| `IsLocationAccuracyAvailable` | 检查设备是否支持指定精度的位置更新 | `ULocationServicesBPLibrary` |
| `GetLastKnownLocation` | 获取最后一次缓存的位置信息 | `ULocationServicesBPLibrary` |
| `StartLocationServices` | 启动位置更新服务，需指定精度和更新频率 | `ULocationServicesBPLibrary` |
| `StopLocationServices` | 停止位置更新服务 | `ULocationServicesBPLibrary` |
| `AreLocationServicesEnabled` | 查询设备或应用的位置服务权限是否已开启 | `ULocationServicesBPLibrary` |

### 使用示例（蓝图描述）

1.  首先，调用 `LocationServicesBPLibrary -> GetLocationServicesImpl` 节点，获取平台服务实例。
2.  调用 `AreLocationServicesEnabled` 检查权限。如果返回 `true`。
3.  调用 `StartLocationServices`，设置所需的位置精度（如 `HighAccuracy`）和更新间隔（如 1 秒）。
4.  在需要的时候，调用 `GetLastKnownLocation` 来获取最新的 `FLocationServicesData` 结构体，其中包含经纬度、水平精度、垂直精度、速度、方向等信息。
5.  应用退出或不再需要时，调用 `StopLocationServices`。

## C++ 用法

在 C++ 中，你将通过 `ILocationServices` 接口与底层实现交互。通常，你会直接使用 `LocationServicesBPLibrary` 模块中的类，该模块依赖于本插件。

### 头文件引入

```cpp
// 包含位置服务数据结构和接口定义
#include "LocationServicesBPLibrary/LocationServicesDelegates.h" // 主要包含 FLocationServicesData 和相关委托
#include "LocationServicesBPLibrary/LocationServicesBPLibrary.h" // 蓝图函数库

// 如果需要直接访问 iOS 实现（通常不需要）：
// #include "LocationServicesIOSImpl/LocationServicesIOSImpl.h"
```

### 基本用法

```cpp
// 来源: 基于 LocationServicesBPLibrary 模块的设计推断
#include "LocationServicesBPLibrary/LocationServicesBPLibrary.h"

void AMyActor::CheckAndStartLocation()
{
    // 1. 检查位置服务是否可用
    bool bIsAvailable = ULocationServicesBPLibrary::AreLocationServicesEnabled();
    
    if (bIsAvailable)
    {
        // 2. 启动高精度定位，每1秒更新一次
        FLocationServicesData LastLocation;
        ULocationServicesBPLibrary::StartLocationServices(ELocationAccuracy::HighAccuracy, 1.0f, true);
        
        // 3. （可选）绑定位置更新委托
        // ULocationServicesBPLibrary::GetLocationServicesImpl()->OnLocationChanged.AddDynamic(this, &AMyActor::OnLocationUpdated);
    }
}

void AMyActor::OnLocationUpdated(FLocationServicesData LocationData)
{
    // 接收位置更新
    UE_LOG(LogTemp, Log, TEXT("New Location: %f, %f, Accuracy: %f m"), 
        LocationData.Latitude, LocationData.Longitude, LocationData.HorizontalAccuracy);
}
```

### 进阶用法

结合委托进行监听：

```cpp
// 来源: 基于 LocationServicesDelegates.h 中的声明
#include "LocationServicesBPLibrary/LocationServicesDelegates.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnLocationChanged, const FLocationServicesData&, LocationData);

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 获取服务接口
    ILocationServices* LocationServices = ULocationServicesBPLibrary::GetLocationServicesImpl();
    if (LocationServices)
    {
        // 绑定更新事件
        LocationServices->OnLocationChanged.AddDynamic(this, &AMyActor::HandleLocationUpdate);
        
        // 启动服务
        LocationServices->StartLocationServices(ELocationAccuracy::BestForNavigation, 0.5f, false);
    }
}

void AMyActor::HandleLocationUpdate(const FLocationServicesData& NewLocation)
{
    // 处理新的位置数据
    FVector ActorLocation = FVector(NewLocation.Longitude, NewLocation.Latitude, 0.0f); // 简化示例
    // ... 执行移动逻辑或其他操作
}
```

## Demo 示例

一个最小的 Actor 类，用于在 iOS 上启动并接收位置更新。

**MyLocationActor.h**
```cpp
// MyLocationActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LocationServicesBPLibrary/LocationServicesDelegates.h" // 包含 FLocationServicesData
#include "MyLocationActor.generated.h"

UCLASS()
class MYPROJECT_API AMyLocationActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyLocationActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UFUNCTION()
    void OnLocationUpdated(const FLocationServicesData& LocationData);
};
```

**MyLocationActor.cpp**
```cpp
// MyLocationActor.cpp
#include "MyLocationActor.h"
#include "LocationServicesBPLibrary/LocationServicesBPLibrary.h"

AMyLocationActor::AMyLocationActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyLocationActor::BeginPlay()
{
    Super::BeginPlay();

    // 尝试启动位置服务
    if (ULocationServicesBPLibrary::AreLocationServicesEnabled())
    {
        ULocationServicesBPLibrary::StartLocationServices(ELocationAccuracy::HighAccuracy, 2.0f, true);
        
        // 获取服务实例并绑定委托
        ILocationServices* Services = ULocationServicesBPLibrary::GetLocationServicesImpl();
        if (Services)
        {
            Services->OnLocationChanged.AddDynamic(this, &AMyLocationActor::OnLocationUpdated);
            UE_LOG(LogTemp, Log, TEXT("Location service started and bound."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Location services are not enabled on this device."));
    }
}

void AMyLocationActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 停止服务并解绑
    ILocationServices* Services = ULocationServicesBPLibrary::GetLocationServicesImpl();
    if (Services)
    {
        Services->OnLocationChanged.RemoveDynamic(this, &AMyLocationActor::OnLocationUpdated);
    }
    ULocationServicesBPLibrary::StopLocationServices();
    
    Super::EndPlay(EndPlayReason);
}

void AMyLocationActor::OnLocationUpdated(const FLocationServicesData& LocationData)
{
    UE_LOG(LogTemp, Log, TEXT("Location Update - Lat: %f, Lon: %f, Acc: %f"),
        LocationData.Latitude, LocationData.Longitude, LocationData.HorizontalAccuracy);
}
```

## 模块依赖

要使用此插件的功能，你的项目或模块通常需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `LocationServicesBPLibrary` | **核心依赖**。提供跨平台的位置服务蓝图接口和数据结构，本插件是其 iOS 实现。 |
| `IOS` | iOS 平台核心模块，提供与 iOS 系统框架的交互支持。 |

**标准依赖（已省略）**: Core, CoreUObject, Engine, IOS 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将遗留的 UE_LOG 迁移为更现代的 UE_LOGF 宏。 |
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复了在区分大小写的文件系统上编译 iOS 时出现的头文件包含大小写错误。 |
| 2026-01-14 | `1a097717` | Fix IOS CIS Issues. | 修复持续集成系统 (CIS) 中与 iOS 相关的构建问题。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | (批量更新) 可能涉及插件目录结构或元数据的整理。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为安全协议 (https)。 |

### 维护评价

该插件自 **2016 年底** 创建，已有近 9 年历史，属于**文物**级别的模块。虽然最近仍有零星更新（主要集中在编译兼容性、构建系统和代码规范上），但**核心功能自创建以来未见重大变化或增强**。它处于一种**低频率维护**的状态，主要应对平台 SDK 升级和引擎编译系统变化带来的问题。

作为一项成熟且功能范围明确的 iOS 平台实现，它目前**可以正常使用**，但因其年代久远，与现代 iOS 开发框架（如 SwiftUI、新的隐私策略）的深度集成可能有限。对于需要在 iOS 上获取基础位置数据的项目，它仍然是可行的官方方案。

**建议**：可安全使用，但预期不会有新功能。若对定位功能有更复杂或更新的需求（如后台持续定位、地理围栏、融合其他传感器），可能需要评估其能力是否满足，或寻找第三方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesIOSImpl)
- [官方文档]() （无）
- [测试用例]() (未在插件目录内发现专用测试)