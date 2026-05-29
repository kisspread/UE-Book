# Mobile Location Services - Android Implementation

> Android implementation for blueprint access for location data from mobile devices

| 属性 | 值 |
|---|---|
| 中文名 | Android定位服务 |
| 分类 | Mobile |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LocationServicesAndroidImpl` (Runtime), `LocationServicesAndroidEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2016-12-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesAndroidImpl) | |

## 用途

此插件并非一个独立的功能蓝图库，而是为 Unreal Engine 的 **Location Services 蓝图功能库** (`LocationServicesBPLibrary`) 提供了 Android 平台下的具体实现。它通过 Java Native Interface (JNI) 调用 Android 系统的 `LocationManager` 服务，从而允许开发者在 Unreal 项目中访问 Android 设备的 GPS 或网络定位数据，用于实现基于地理位置的游戏玩法或应用功能。

## 使用场景

- **基于地理位置的游戏（LBS 游戏）**：例如，玩家需要移动到真实世界的特定地点才能解锁游戏内容或触发事件。
- **需要实时位置信息的应用**：例如，一个健身应用需要追踪玩家的移动路径和速度。
- **地图集成**：获取设备的当前位置，并将其映射到游戏世界的特定坐标。
- **地理围栏**：当玩家进入或离开某个预定义的物理区域时，触发游戏内的逻辑。

## 蓝图用法

核心的蓝图接口由 `LocationServicesBPLibrary` 提供，而本插件是其 Android 端的底层驱动。蓝图节点调用会通过接口调用到本插件的 `ULocationServicesAndroidImpl` 类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init Location Services` | 使用指定精度、更新频率和最小距离过滤器初始化定位服务。必须首先调用。 | `ULocationServicesImpl` (由 `ULocationServicesAndroidImpl` 实现) |
| `Start Location Service` | 开始接收位置更新。必须在初始化后调用。 | `ULocationServicesImpl` |
| `Stop Location Service` | 停止接收位置更新。 | `ULocationServicesImpl` |
| `Get Last Known Location` | 返回最后一次已知的位置信息，包含经纬度、高度、精度等数据。 | `ULocationServicesImpl` |
| `Is Location Service Enabled` | 检查设备上是否为该应用启用了定位服务。 | `ULocationServicesImpl` |
| `Is Location Accuracy Available` | 检查指定的定位精度（如高精度、省电模式等）在当前设备上是否可用。 | `ULocationServicesImpl` |

### 使用示例（蓝图描述）

1.  **请求权限（重要）**：在 Android 上，访问位置是敏感操作。需要先使用 **Android Permission** 插件请求 `ACCESS_FINE_LOCATION` 或 `ACCESS_COARSE_LOCATION` 权限。
2.  **初始化**：在权限授予后，调用 `Init Location Services` 节点。通常将 `Accuracy` 设为 `HighAccuracy`，`UpdateFrequency` 设为期望的毫秒值（例如 1000 表示每秒），`MinDistanceFilter` 设为 0 表示尽可能频繁更新。
3.  **启动服务**：调用 `Start Location Service` 节点开始获取位置。
4.  **获取位置**：在需要时（例如通过定时器或事件）调用 `Get Last Known Location` 节点。返回的 `FLocationServicesData` 结构体包含 `Longitude`（经度）、`Latitude`（纬度）、`Timestamp`（时间戳）等字段。
5.  **停止服务**：不再需要时，调用 `Stop Location Service` 节点以节省电量。

## C++ 用法

### 头文件引入

要使用 Location Services 的接口，需要引入公共头文件。实际的 Android 实现头文件通常无需直接包含。
```cpp
#include "Kismet/BlueprintPlatformLibrary.h" // 包含 FLocationServicesData 等
#include "LocationServicesBPLibrary.h"
```

### 基本用法

C++ 中通常通过蓝图库的静态函数或引擎的子系统进行调用。直接使用 Android 实现类进行开发的情况较少，更常见的是通过蓝图接口进行间接调用。

**示例：通过蓝图库函数检查定位服务状态**
```cpp
// 检查定位服务是否启用
bool bIsEnabled = ULocationServicesBPLibrary::IsLocationServiceEnabled();

if (bIsEnabled)
{
    // 初始化服务
    bool bInitSuccess = ULocationServicesBPLibrary::InitLocationServices(
        ELocationAccuracy::LA_HighAccuracy,
        1000.0f, // 每1000毫秒更新
        0.0f     // 最小距离过滤为0
    );
    
    if (bInitSuccess)
    {
        // 启动服务
        ULocationServicesBPLibrary::StartLocationService();
    }
}

// 在某个时刻获取位置
FLocationServicesData CurrentLocation = ULocationServicesBPLibrary::GetLastKnownLocation();
UE_LOG(LogTemp, Log, TEXT("Current Location: Lat=%f, Lon=%f"), CurrentLocation.Latitude, CurrentLocation.Longitude);
```

### 进阶用法

更底层的交互涉及 JNI。本插件的 `FLocationServices` 结构体在 `AndroidJniLocationServices.h` 中定义了 JNI 原生方法，用于处理从 Java 层（`GameActivity`）回调的位置更新事件。
```cpp
// 此为引擎内部代码示例，展示JNI回调如何将位置数据从Java层传递到UE
// 开发者通常不需要直接处理此回调
static void JNICALL FLocationServices::nativeHandleLocationChanged(
    JNIEnv* env, jobject thiz, jlong time, jdouble longitude, jdouble latitude, jfloat accuracy, jdouble altitude)
{
    // 在此处将Android的位置更新数据封装成FLocationServicesData
    // 并通过蓝图广播（Multicast Delegate）通知所有监听者
    // ULocationServicesSubsystem::Get()->BroadcastLocationChanged(FLocationServicesData(...));
}
```

## Demo 示例

**最小功能示例（游戏模式）**

```cpp
// MyLocationTestGameMode.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyLocationTestGameMode.generated.h"

UCLASS()
class AMyLocationTestGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AMyLocationTestGameMode();
    virtual void StartPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Location Test")
    void RequestAndStartLocationService();

    UFUNCTION(BlueprintCallable, Category = "Location Test")
    FLocationServicesData FetchCurrentLocation();

private:
    bool bLocationServiceInitialized = false;
};
```

```cpp
// MyLocationTestGameMode.cpp
#include "MyLocationTestGameMode.h"
#include "LocationServicesBPLibrary.h"
#include "AndroidPermissionCallbackProxy.h"
#include "AndroidPermissionFunctionLibrary.h"

AMyLocationTestGameMode::AMyLocationTestGameMode()
{
}

void AMyLocationTestGameMode::StartPlay()
{
    Super::StartPlay();
    // 启动后立即请求权限
    RequestAndStartLocationService();
}

void AMyLocationTestGameMode::RequestAndStartLocationService()
{
    // 请求位置权限
    TArray<FString> Permissions;
    Permissions.Add(TEXT("android.permission.ACCESS_FINE_LOCATION"));
    Permissions.Add(TEXT("android.permission.ACCESS_COARSE_LOCATION"));

    UAndroidPermissionCallbackProxy* Proxy = UAndroidPermissionFunctionLibrary::AcquirePermissions(Permissions);
    if (Proxy)
    {
        Proxy->OnPermissionsGrantedDynamic.AddDynamic(this, &AMyLocationTestGameMode::OnPermissionsGranted);
    }
}

// 权限授予后回调
void OnPermissionsGranted(bool bSuccess, const TArray<FString>& GrantedPermissions)
{
    if (bSuccess)
    {
        // 初始化并启动位置服务
        bLocationServiceInitialized = ULocationServicesBPLibrary::InitLocationServices(
            ELocationAccuracy::LA_HighAccuracy, 1000.0f, 0.0f);
        if (bLocationServiceInitialized)
        {
            ULocationServicesBPLibrary::StartLocationService();
            UE_LOG(LogTemp, Log, TEXT("Location service started after permission grant."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Location permissions were denied."));
    }
}

FLocationServicesData AMyLocationTestGameMode::FetchCurrentLocation()
{
    return ULocationServicesBPLibrary::GetLastKnownLocation();
}
```

## 模块依赖

从插件的 `.uplugin` 文件及通用实践推断，使用此插件时，你的项目需要依赖以下关键模块：

| 模块 | 用途 |
|---|---|
| `LocationServicesBPLibrary` | 提供位置服务的基础蓝图函数库接口，是必须依赖项。 |
| `AndroidPermission` | 用于在 Android 运行时动态请求位置等敏感权限，是必须依赖项。 |
| `AndroidRuntimeSettings` | 用于配置 Android 平台的特定设置（通常项目已默认包含）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-02 | `7d7255e0` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. | 重构 JNI 代码，适配新的 JDK 环境，注册原生函数并更新环境上下文管理。 |
| 2023-12-15 | `3dcdaa23` | Fix usage of _activity errors | 修复访问 `_activity` 成员变量时可能出现的错误。 |
| 2023-05-17 | `6cd02193` | non-unity fix for Android LocationServices | 修复在非 Unity 构建模式下 Android 定位服务模块的编译问题。 |
| 2023-05-16 | `70af860a` | Fix OnLocationChanged broadcast for Android to use game thread properly | 修复 `OnLocationChanged` 广播未能正确同步到游戏线程的问题。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 常规的引擎插件批量更新或调整。 |

### 维护评价

- **年龄**：创建于 2016 年，属于 UE4 早期插件。
- **维护频率**：**低频但持续维护**。最近几年的更新主要是为了兼容新的引擎版本和 Android SDK/JDK 的变化，进行必要的编译修复和 API 调整。
- **功能状态**：核心功能（位置获取）稳定，近期的更新（如 JNI 重构）表明 Epic 仍在维护其与 Android 新工具链的兼容性。
- **限制**：仅适用于 Android 平台，且定位功能的可用性和精度依赖于设备硬件及用户授权。
- **推荐**：**推荐用于需要 Android 位置服务的 UE5 项目**。它是一个官方维护的、久经考验的实现。虽然更新不频繁，但必要的兼容性修复会及时跟进。使用时需注意遵循 Android 的权限管理要求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesAndroidImpl)
- 官方文档链接未提供。
- 测试用例链接未提供。