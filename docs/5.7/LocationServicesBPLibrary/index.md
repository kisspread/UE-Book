# Mobile Location Services Blueprints Library

> Common interface for blueprint access for location data from mobile devices

| 属性 | 值 |
|---|---|
| 分类 | Mobile |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | LocationServicesBPLibrary (Runtime) |
| 创建时间 | 2016-12-08 |
| 年龄标签 | 🏛️ 文物（>10年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/LocationServicesBPLibrary/) | |

## 用途

LocationServicesBPLibrary 是一个**抽象接口层**，为 UE5 提供统一的 GPS/定位服务蓝图访问接口。它本身不包含任何平台实现——实际的定位逻辑由两个独立的平台插件提供：

- **LocationServicesAndroidImpl** — Android 平台实现（通过 JNI 调用 Android LocationManager）
- **LocationServicesIOSImpl** — iOS 平台实现（通过 CLLocationManager）

本插件定义了抽象基类 `ULocationServicesImpl`，平台插件在启动时将自己的实现注入进来。蓝图开发者只需调用 `ULocationServices` 的静态函数，无需关心底层是哪个平台。

这种设计使得同一套蓝图/代码可以同时支持 Android 和 iOS 的定位功能。

## 使用场景

- 你在做一个 AR 手游，需要获取玩家的实时 GPS 坐标 → 用 LocationServicesBPLibrary
- 你需要基于地理位置触发游戏事件（如 Pokémon GO 风格的 LBS 玩法）→ 用 LocationServicesBPLibrary
- 你需要记录玩家的移动轨迹用于数据分析 → 用 LocationServicesBPLibrary

⚠️ **注意**：此插件仅在移动平台（Android/iOS）上有效。在桌面/主机平台上，所有函数会返回 `false` 或默认值，因为没有平台实现注入。

## 蓝图用法

所有蓝图节点位于 `Services > Mobile > Location` 分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitLocationServices` | 初始化定位服务，设置精度、更新频率和最小距离过滤器 | `ULocationServices` |
| `StartLocationServices` | 开始接收位置更新 | `ULocationServices` |
| `StopLocationServices` | 停止位置更新 | `ULocationServices` |
| `GetLastKnownLocation` | 获取最后一次已知位置数据 | `ULocationServices` |
| `AreLocationServicesEnabled` | 检查设备是否已为本应用启用定位服务 | `ULocationServices` |
| `IsLocationAccuracyAvailable` | 检查设备是否支持指定精度等级 | `ULocationServices` |
| `GetLocationServicesImpl` | 获取平台实现对象（用于绑定 OnLocationChanged 委托） | `ULocationServices` |

### 精度等级（ELocationAccuracy）

| 枚举值 | 显示名称 | 说明 |
|---|---|---|
| `LA_ThreeKilometers` | Three Kilometers | 最低精度，最省电 |
| `LA_OneKilometer` | One Kilometer | 低精度 |
| `LA_HundredMeters` | One Hundred Meters | 中等精度 |
| `LA_TenMeters` | Ten Meters | 高精度 |
| `LA_Best` | Best | 设备最高精度 |
| `LA_Navigation` | Best for Navigation | 导航级精度，最耗电 |

精度枚举基于 iOS 的 `kCLLocationAccuracy` 定义，因为 iOS 的限制更严格但命名更具描述性。

### 位置数据结构（FLocationServicesData）

| 属性 | 类型 | 说明 |
|---|---|---|
| `Timestamp` | float | UTC 时间戳（自 1970-01-01 起的毫秒数） |
| `Longitude` | float | 经度 |
| `Latitude` | float | 纬度 |
| `HorizontalAccuracy` | float | 水平精度估计（米）。Android 上为整体精度 |
| `VerticalAccuracy` | float | 垂直精度估计（米）。**仅 iOS 提供** |
| `Altitude` | float | 海拔高度（米），如果设备提供的话 |

### 事件委托

`ULocationServicesImpl` 上有一个 `BlueprintAssignable` 委托：

- **OnLocationChanged** (`FLocationServicesData_OnLocationChanged`) — 每次位置更新时触发，传递 `FLocationServicesData` 参数

### 使用示例（蓝图描述）

**基本定位流程：**

1. 调用 `AreLocationServicesEnabled` 检查定位是否可用
2. 调用 `InitLocationServices`，传入精度（如 `LA_HundredMeters`）、更新频率（如 5000ms）、最小距离过滤器（如 10 米）
3. 调用 `StartLocationServices` 开始接收更新
4. 通过 `GetLocationServicesImpl` 获取实现对象，绑定 `OnLocationChanged` 委托来实时接收位置变化
5. 游戏结束或不需要时，调用 `StopLocationServices` 停止

**轮询方式获取位置：**

也可以不绑定委托，通过定时调用 `GetLastKnownLocation` 来轮询获取最新位置。但这种方式不如委托方式高效。

## C++ 用法

### 头文件引入

```cpp
#include "LocationServicesBPLibrary.h"
#include "LocationServicesImpl.h"
```

### 基本用法

```cpp
// 检查定位服务是否可用
if (ULocationServices::AreLocationServicesEnabled())
{
    // 初始化：百米精度，每 5 秒更新，最小移动 10 米才触发
    if (ULocationServices::InitLocationServices(
        ELocationAccuracy::LA_HundredMeters,
        5000.0f,   // UpdateFrequency (ms, Android only)
        10.0f))    // MinDistanceFilter (meters)
    {
        // 启动定位
        ULocationServices::StartLocationServices();
    }
}

// 获取最新位置
FLocationServicesData Location = ULocationServices::GetLastKnownLocation();
UE_LOG(LogTemp, Log, TEXT("Lat: %f, Lon: %f, Alt: %f"),
    Location.Latitude, Location.Longitude, Location.Altitude);

// 停止定位
ULocationServices::StopLocationServices();
```

### 进阶用法

通过 C++ 绑定 `OnLocationChanged` 委托来实时接收位置更新：

```cpp
// 获取平台实现对象
ULocationServicesImpl* Impl = ULocationServices::GetLocationServicesImpl();
if (Impl)
{
    // 绑定位置变化委托
    Impl->OnLocationChanged.AddDynamic(this, &AMyActor::HandleLocationChanged);
}
```

```cpp
UFUNCTION()
void AMyActor::HandleLocationChanged(FLocationServicesData LocationData)
{
    UE_LOG(LogTemp, Log, TEXT("Location updated - Lat: %f, Lon: %f, Time: %f"),
        LocationData.Latitude, LocationData.Longitude, LocationData.Timestamp);
}
```

## Demo 示例

### 最小可编译示例

**MyLocationActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LocationServicesBPLibrary.h"
#include "LocationServicesImpl.h"
#include "MyLocationActor.generated.h"

UCLASS()
class AMyLocationActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void OnLocationUpdated(FLocationServicesData LocationData);

    UPROPERTY(BlueprintReadOnly)
    float CurrentLatitude = 0.0f;

    UPROPERTY(BlueprintReadOnly)
    float CurrentLongitude = 0.0f;
};
```

**MyLocationActor.cpp**

```cpp
#include "MyLocationActor.h"
#include "LocationServicesBPLibrary.h"

void AMyLocationActor::BeginPlay()
{
    Super::BeginPlay();

    if (ULocationServices::AreLocationServicesEnabled())
    {
        if (ULocationServices::InitLocationServices(
            ELocationAccuracy::LA_HundredMeters, 3000.0f, 5.0f))
        {
            ULocationServices::StartLocationServices();

            // 绑定委托
            ULocationServicesImpl* Impl = ULocationServices::GetLocationServicesImpl();
            if (Impl)
            {
                Impl->OnLocationChanged.AddDynamic(this, &AMyLocationActor::OnLocationUpdated);
            }
        }
    }
}

void AMyLocationActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    ULocationServices::StopLocationServices();
    Super::EndPlay(EndPlayReason);
}

void AMyLocationActor::OnLocationUpdated(FLocationServicesData LocationData)
{
    CurrentLatitude = LocationData.Latitude;
    CurrentLongitude = LocationData.Longitude;
}
```

**Build.cs 依赖**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "LocationServicesBPLibrary"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心模块 |

## 架构说明

本插件采用**策略模式**，将接口与实现分离：

```
LocationServicesBPLibrary (本插件)
├── ULocationServices        ← 蓝图函数库（静态函数入口）
├── ULocationServicesImpl    ← 抽象基类（平台插件需继承此类）
└── FLocationServicesData    ← 位置数据结构

LocationServicesAndroidImpl (独立插件)
└── 继承 ULocationServicesImpl，通过 JNI 调用 Android LocationManager

LocationServicesIOSImpl (独立插件)
└── 继承 ULocationServicesImpl，通过 CLLocationManager 获取 iOS 定位
```

平台插件在各自的 `StartupModule()` 中调用 `ULocationServices::SetLocationServicesImpl()` 注入实现。在 `ShutdownModule()` 中调用 `ClearLocationServicesImpl()` 清理。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-06-26 | `a2e75189887d` | 添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏到源文件，减少编译时间 |
| 2025-04-23 | `6ae573356bbf` | 将所有文件的 DLL 导出从类型级别改为方法/静态变量级别 |
| 2023-04-12 | `bd466cf26ca6` | 修复模块不正确的自依赖问题 |

### 维护评价

- **创建时间**：2016 年 12 月，已有超过 9 年历史（🏛️ 文物级别）
- **最近更新**：2025 年 6 月有更新，但均为编译/构建系统层面的维护性修改，无功能性变更
- **最后实质性更新**：功能层面的最后有意义更新可能在更早之前
- **维护状态**：**维护不活跃** — 近几年的提交都是自动化的构建系统迁移（如 DLL export 方式变更、inline generated 宏添加），没有人主动改进功能
- **是否推荐使用**：✅ **推荐**。虽然功能上不活跃，但作为抽象接口层，它足够稳定和成熟。API 简洁清晰，满足移动定位需求没有问题。实际的平台适配工作由 iOS/Android 实现插件承担。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/LocationServicesBPLibrary/)
- [Android 实现插件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/LocationServicesAndroidImpl/)
- [iOS 实现插件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/LocationServicesIOSImpl/)
