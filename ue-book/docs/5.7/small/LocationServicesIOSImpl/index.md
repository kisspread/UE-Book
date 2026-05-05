# Mobile Location Services - IOS Implementation

> IOS implementation for blueprint access for location data from mobile devices

| 属性 | 值 |
|---|---|
| 分类 | Mobile |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | LocationServicesIOSEditor (Editor), LocationServicesIOSImpl (Runtime, 仅 IOS) |
| 创建时间 | 2016-12-08 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LocationServicesIOSImpl) | |

## 用途

LocationServicesIOSImpl 是 UE5 跨平台定位服务框架的 **iOS 平台具体实现**。它不是一个独立使用的插件，而是 `LocationServicesBPLibrary` 插件的 iOS 后端。

整个架构采用策略模式（Strategy Pattern）：
- `LocationServicesBPLibrary` 提供平台无关的蓝图接口（`ULocationServices` 静态函数库）
- `LocationServicesIOSImpl`（本插件）在 iOS 平台上注入 `ULocationServicesIOSImpl` 作为实际执行者
- 模块启动时自动注册，蓝图开发者无需关心平台差异

底层实现封装了 Apple 的 `CLLocationManager`（CoreLocation 框架），通过 Objective-C++ 混编实现。首次启动定位时会调用 `requestAlwaysAuthorization` 请求用户授权。

## 使用场景

- 你在开发 iOS 上的 LBS（基于位置的服务）游戏 → 启用此插件即可通过蓝图获取 GPS 定位
- 你需要实现 AR 导航或地理位置打卡功能 → 用此插件获取实时经纬度和精度信息
- 你已有 Android 定位实现，需要 iOS 端对应 → 启用本插件，蓝图逻辑无需修改
- **前提条件**：必须同时启用 `LocationServicesBPLibrary` 插件（已声明为依赖，会自动启用）

## 蓝图用法

所有蓝图节点来自父插件 `LocationServicesBPLibrary` 的 `ULocationServices` 类，本插件负责在 iOS 上提供底层实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitLocationServices` | 初始化定位服务，设置精度/更新频率/最小距离 | `ULocationServices` |
| `StartLocationServices` | 开始接收位置更新 | `ULocationServices` |
| `StopLocationServices` | 停止位置更新 | `ULocationServices` |
| `GetLastKnownLocation` | 获取最后一次已知位置数据 | `ULocationServices` |
| `AreLocationServicesEnabled` | 检查设备是否已启用定位服务 | `ULocationServices` |
| `IsLocationAccuracyAvailable` | 检查设备是否支持指定精度（iOS 始终返回 true） | `ULocationServices` |
| `GetLocationServicesImpl` | 获取平台实现对象，用于绑定 OnLocationChanged 委托 | `ULocationServices` |

### 精度等级 (ELocationAccuracy)

| 枚举值 | 显示名称 | iOS 对应常量 | 说明 |
|---|---|---|---|
| `LA_ThreeKilometers` | Three Kilometers | `kCLLocationAccuracyThreeKilometers` | 最低精度，最省电 |
| `LA_OneKilometer` | One Kilometer | `kCLLocationAccuracyKilometer` | 低精度 |
| `LA_HundredMeters` | One Hundred Meters | `kCLLocationAccuracyHundredMeters` | 中等精度（默认） |
| `LA_TenMeters` | Ten Meters | `kCLLocationAccuracyNearestTenMeters` | 高精度 |
| `LA_Best` | Best | `kCLLocationAccuracyBest` | 最高精度 |
| `LA_Navigation` | Best for Navigation | `kCLLocationAccuracyBestForNavigation` | 导航级精度，最耗电 |

### FLocationServicesData 结构体

| 字段 | 类型 | 说明 |
|---|---|---|
| `Timestamp` | float | UTC 时间戳（自 1970-01-01 的秒数） |
| `Longitude` | float | 经度 |
| `Latitude` | float | 纬度 |
| `HorizontalAccuracy` | float | 水平精度（米） |
| `VerticalAccuracy` | float | 垂直精度（米，iOS 特有） |
| `Altitude` | float | 海拔高度（米） |

### OnLocationChanged 委托

通过 `GetLocationServicesImpl` 节点获取实现对象后，可绑定其 `OnLocationChanged` 事件。每次位置更新时自动广播 `FLocationServicesData`。

### 使用示例（蓝图描述）

**基本定位流程：**

1. **Event BeginPlay** → **InitLocation Services**（Accuracy = One Hundred Meters, UpdateFrequency = 0, MinDistanceFilter = 10）→ 分支判断返回值
2. 若初始化成功 → **Start Location Services** → 分支判断返回值
3. 通过 **Get Location Services Impl** 获取实现对象 → 绑定 **OnLocationChanged** 事件
4. OnLocationChanged 回调中 → 从 LocationData 拆解 Latitude/Longitude/Altitude 等字段使用

**获取一次性位置：**

1. **InitLocationServices** → **StartLocationServices**
2. 等待片刻后调用 **Get Last Known Location** 获取 `FLocationServicesData`

## C++ 用法

### 头文件引入

```cpp
// 使用蓝图接口（推荐，跨平台）
#include "LocationServicesBPLibrary.h"

// 直接使用 iOS 实现类（仅限 iOS 平台特定逻辑）
#include "LocationServicesIOSImpl.h"
```

### 基本用法

基于 `LocationServicesBPLibrary.h` 中 `ULocationServices` 的静态接口：

```cpp
#include "LocationServicesBPLibrary.h"

// 初始化定位服务：精度100米，更新频率由系统决定，最小移动距离10米
bool bSuccess = ULocationServices::InitLocationServices(
    ELocationAccuracy::LA_HundredMeters,
    0.0f,   // UpdateFrequency (iOS 忽略此参数)
    10.0f   // MinDistanceFilter (米)
);

if (bSuccess)
{
    // 开始接收位置更新
    ULocationServices::StartLocationServices();
}

// 获取当前位置
FLocationServicesData Location = ULocationServices::GetLastKnownLocation();
UE_LOG(LogTemp, Log, TEXT("Lat: %f, Lon: %f, Alt: %f"),
    Location.Latitude, Location.Longitude, Location.Altitude);

// 检查定位服务是否可用
if (ULocationServices::AreLocationServicesEnabled())
{
    UE_LOG(LogTemp, Log, TEXT("Location services are enabled"));
}
```

### 进阶用法 — 绑定位置更新委托

```cpp
#include "LocationServicesBPLibrary.h"

// 获取平台实现对象并绑定委托
ULocationServicesImpl* Impl = ULocationServices::GetLocationServicesImpl();
if (Impl)
{
    Impl->OnLocationChanged.AddDynamic(this, &AMyActor::HandleLocationChanged);
}

// 回调函数
void AMyActor::HandleLocationChanged(FLocationServicesData LocationData)
{
    UE_LOG(LogTemp, Log, TEXT("Location updated: (%f, %f) at %f"),
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
};
```

**MyLocationActor.cpp**
```cpp
#include "MyLocationActor.h"
#include "LocationServicesBPLibrary.h"

void AMyLocationActor::BeginPlay()
{
    Super::BeginPlay();

    // 检查并初始化
    if (ULocationServices::AreLocationServicesEnabled())
    {
        if (ULocationServices::InitLocationServices(
                ELocationAccuracy::LA_TenMeters, 0.0f, 5.0f))
        {
            ULocationServices::StartLocationServices();

            // 绑定位置更新事件
            ULocationServicesImpl* Impl = ULocationServices::GetLocationServicesImpl();
            if (Impl)
            {
                Impl->OnLocationChanged.AddDynamic(
                    this, &AMyLocationActor::OnLocationUpdated);
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
    UE_LOG(LogTemp, Log, TEXT("Position: (%.6f, %.6f), Alt: %.1fm, Accuracy: %.1fm"),
        LocationData.Latitude, LocationData.Longitude,
        LocationData.Altitude, LocationData.HorizontalAccuracy);
}
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "LocationServicesBPLibrary"
});
```

## 编辑器设置

启用插件后，在 **Project Settings → Plugins → Location Services IOS** 中可配置 iOS 权限弹窗文案：

| 设置项 | 说明 | Info.plist 键 |
|---|---|---|
| Location Services Always Use Permission Text | "始终使用"权限的说明文字 | `NSLocationAlwaysUsageDescription` |
| Location Services In-Use Permission Text | "使用期间"权限的说明文字 | `NSLocationWhenInUseUsageDescription` |

这两个字段会写入 iOS 打包的 Info.plist，App Store 审核要求必须填写。

## 模块依赖

### LocationServicesIOSImpl 模块（Runtime，仅 IOS）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `LocationServicesBPLibrary` | 跨平台蓝图接口层 |
| `Launch` | 启动模块（私有依赖） |

**iOS Framework 依赖：** `CoreLocation`

### LocationServicesIOSEditor 模块（Editor）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Settings` | 编辑器设置面板（动态加载） |

## 已知问题

- `IsLocationServiceEnabled()` 中的授权状态判断存在逻辑 bug：`kCLAuthorizationStatusDenied` 表示被拒绝，但代码将 `!bAuthorized` 用于日志提示（变量名 `bAuthorized` 实际存储的是"是否被拒绝"的含义），导致返回值语义不直观
- `UpdateFrequency` 参数在 iOS 实现中被忽略（iOS 的 `CLLocationManager` 不支持按频率更新，而是按距离和精度自动调度）
- `IsLocationAccuracyAvailable()` 在 iOS 上始终返回 `true`，因为 iOS 支持所有精度等级
- 使用手动内存管理（`retain`/`release`），非 ARC 风格

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da7` | [Engine/Plugins] * Another batch iwyu updates to reduce number of includes used in files | IWYU（Include What You Use）批量重构，减少头文件包含，无功能性变更 |
| 2022-11-07 | `0a10c21f` | Update Release-Engine-Staging from UE5/Main | 分支同步合并，非针对性更新 |
| 2022-09-15 | `7af5c760` | Fix static analyser report of missing dealloc in LocationServicesIOSImpl | 修复静态分析器报告的 `dealloc` 缺失问题，添加了 `~ULocationServicesIOSImpl` 析构函数 |

### 维护评价

- **创建时间**：2016-12-08（约 9 年前），最初为 UE4 编写
- **最近功能性更新**：2022 年 9 月的 dealloc 修复，此后仅有编译维护性提交
- **维护状态**：**维护不活跃** — 超过 2.5 年无实质性功能更新
- **成熟度**：功能稳定，代码量小（~240 行实现），不太需要频繁更新
- **推荐**：iOS 定位需求的**唯一选择**。虽然更新不活跃，但 CoreLocation API 稳定，插件功能完整。生产可用，但建议关注 iOS 新版本的权限变化（如 iOS 14+ 引入的精确定位/模糊定位选择）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LocationServicesIOSImpl)
- [父插件 LocationServicesBPLibrary 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LocationServicesBPLibrary)
- 官方文档：无（.uplugin 中 DocsURL 为空）
