# Mobile Location Services - Android Implementation

> Android implementation for blueprint access for location data from mobile devices

| 属性 | 值 |
|---|---|
| 分类 | Mobile |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | LocationServicesAndroidEditor (Editor), LocationServicesAndroidImpl (Runtime) |
| 创建时间 | 2016-12-08 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LocationServicesAndroidImpl) | |

## 用途

这是 UE5 Location Services 的 **Android 平台实现**。UE5 的定位服务采用插件化架构：`LocationServicesBPLibrary` 提供统一的蓝图接口和抽象基类 `ULocationServicesImpl`，而 `LocationServicesAndroidImpl` 和 `LocationServicesIOSImpl` 分别提供 Android 和 iOS 的具体实现。

这个 plugin 通过 JNI 调用 Android 系统的 `LocationManager` API，将 GPS/网络定位数据桥接到 UE5 的蓝图和 C++ 层。它的核心价值在于：**你不需要写任何 Java 代码就能在 Android 上获取设备位置**。

工作原理：
1. 模块启动时自动创建 `ULocationServicesAndroidImpl` 实例并注册到 `ULocationServices`
2. 蓝图调用 `ULocationServices` 的静态函数 → 委托到已注册的平台实现
3. 实现类通过 JNI 调用 GameActivity 中注入的 Java 方法
4. Java 层使用 Android `LocationManager` 获取位置，通过 JNI 回调通知 UE5
5. 位置变更事件在 GameThread 上广播

## 使用场景

- **LBS 游戏**：基于真实地理位置的游戏机制（类似 Pokémon GO）
- **AR 应用**：需要知道用户真实位置的增强现实体验
- **位置感知内容**：根据用户所在城市/地区切换游戏内容
- **运动/健身应用**：追踪用户移动轨迹
- **地图集成**：在游戏内显示用户在真实地图上的位置

## 蓝图用法

### 核心节点

所有蓝图节点来自 `LocationServicesBPLibrary` 的 `ULocationServices` 类，本 plugin 作为 Android 平台的后端自动生效。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitLocationServices` | 初始化定位服务，设置精度、更新频率和最小距离 | `ULocationServices` |
| `StartLocationServices` | 开始接收位置更新 | `ULocationServices` |
| `StopLocationServices` | 停止位置更新 | `ULocationServices` |
| `GetLastKnownLocation` | 获取最后一次已知位置，返回 `FLocationServicesData` | `ULocationServices` |
| `AreLocationServicesEnabled` | 检查设备是否启用了定位服务 | `ULocationServices` |
| `IsLocationAccuracyAvailable` | 检查设备是否支持指定精度 | `ULocationServices` |
| `GetLocationServicesImpl` | 获取平台实现对象，用于绑定 `OnLocationChanged` 委托 | `ULocationServices` |

### 精度枚举 (ELocationAccuracy)

| 枚举值 | 显示名 | Android 精度 | Android 功耗 |
|---|---|---|---|
| `LA_ThreeKilometers` | Three Kilometers | LOW | LOW |
| `LA_OneKilometer` | One Kilometer | LOW | MEDIUM |
| `LA_HundredMeters` | One Hundred Meters | MEDIUM | MEDIUM |
| `LA_TenMeters` | Ten Meters | HIGH | MEDIUM |
| `LA_Best` | Best | HIGH | HIGH |
| `LA_Navigation` | Best for Navigation | HIGH | HIGH |

### FLocationServicesData 结构体

| 字段 | 类型 | 说明 |
|---|---|---|
| `Timestamp` | float | UTC 时间戳（毫秒，自 1970-01-01） |
| `Longitude` | float | 经度 |
| `Latitude` | float | 纬度 |
| `HorizontalAccuracy` | float | 水平精度（米），Android 上为整体精度 |
| `VerticalAccuracy` | float | 垂直精度（米），Android 上始终为 0 |
| `Altitude` | float | 海拔高度（米） |

### 使用示例（蓝图描述）

**基本位置获取：**
1. BeginPlay → `InitLocationServices`（Accuracy: LA_HundredMeters, UpdateFrequency: 5000, MinDistance: 10）→ `StartLocationServices`
2. 使用 `GetLastKnownLocation` 节点拉取位置数据
3. EndPlay → `StopLocationServices`

**实时位置监听：**
1. BeginPlay → `GetLocationServicesImpl` → 拉引脚获取返回对象
2. 在返回对象上绑定 `OnLocationChanged` 事件（类型为 `FLocationServicesData_OnLocationChanged`）
3. 在事件回调中处理每次位置更新
4. EndPlay → `StopLocationServices`

## C++ 用法

### 头文件引入

```cpp
#include "LocationServicesBPLibrary.h"  // 用于 ULocationServices 静态函数和类型定义
#include "LocationServicesImpl.h"       // 用于 ULocationServicesImpl 和 OnLocationChanged 委托
```

### 基本用法

```cpp
// 初始化并启动定位服务
// 来源: LocationServicesBPLibrary.h + LocationServicesAndroidImpl.cpp
if (ULocationServices::InitLocationServices(ELocationAccuracy::LA_HundredMeters, 5000.0f, 10.0f))
{
    ULocationServices::StartLocationServices();
}

// 获取最新位置
FLocationServicesData Location = ULocationServices::GetLastKnownLocation();
UE_LOG(LogTemp, Log, TEXT("Lat: %f, Lon: %f, Alt: %f"),
    Location.Latitude, Location.Longitude, Location.Altitude);
```

### 监听位置变更事件

```cpp
// 来源: LocationServicesImpl.h (OnLocationChanged 声明)
ULocationServicesImpl* Impl = ULocationServices::GetLocationServicesImpl();
if (Impl)
{
    Impl->OnLocationChanged.AddDynamic(this, &AMyActor::OnLocationChanged);
}

// 回调函数
void AMyActor::OnLocationChanged(FLocationServicesData LocationData)
{
    UE_LOG(LogTemp, Log, TEXT("New location: %f, %f"), LocationData.Latitude, LocationData.Longitude);
}
```

### 进阶用法

```cpp
// 检查设备能力后再初始化
if (ULocationServices::AreLocationServicesEnabled())
{
    ELocationAccuracy DesiredAccuracy = ELocationAccuracy::LA_TenMeters;

    if (!ULocationServices::IsLocationAccuracyAvailable(DesiredAccuracy))
    {
        DesiredAccuracy = ELocationAccuracy::LA_HundredMeters;
        UE_LOG(LogTemp, Warning, TEXT("Falling back to HundredMeters accuracy"));
    }

    ULocationServices::InitLocationServices(DesiredAccuracy, 3000.0f, 5.0f);
    ULocationServices::StartLocationServices();
}
```

## Demo 示例

以下是一个完整的最小 Actor，每 5 秒打印一次设备位置：

**LocationTracker.Build.cs**（你的模块 Build.cs）：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "LocationServicesBPLibrary"  // 需要依赖此模块
});
```

**LocationTracker.h**：
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LocationServicesImpl.h"
#include "LocationTracker.generated.h"

UCLASS()
class ALocationTracker : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void OnLocationChanged(FLocationServicesData LocationData);

    FTimerHandle PollTimerHandle;
};
```

**LocationTracker.cpp**：
```cpp
#include "LocationTracker.h"
#include "LocationServicesBPLibrary.h"

void ALocationTracker::BeginPlay()
{
    Super::BeginPlay();

    // 初始化: 百米精度, 每3秒更新, 最小移动5米
    if (ULocationServices::AreLocationServicesEnabled() &&
        ULocationServices::InitLocationServices(ELocationAccuracy::LA_HundredMeters, 3000.0f, 5.0f))
    {
        ULocationServices::StartLocationServices();

        // 绑定实时更新事件
        ULocationServicesImpl* Impl = ULocationServices::GetLocationServicesImpl();
        if (Impl)
        {
            Impl->OnLocationChanged.AddDynamic(this, &ALocationTracker::OnLocationChanged);
        }
    }
}

void ALocationTracker::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    ULocationServices::StopLocationServices();
    Super::EndPlay(EndPlayReason);
}

void ALocationTracker::OnLocationChanged(FLocationServicesData LocationData)
{
    UE_LOG(LogTemp, Log, TEXT("Location: Lat=%f Lon=%f Alt=%f Accuracy=%f"),
        LocationData.Latitude, LocationData.Longitude,
        LocationData.Altitude, LocationData.HorizontalAccuracy);
}
```

## 编辑器设置

启用插件后，在 **Project Settings → Plugins → Location Services - Android** 中可以配置：

| 设置项 | 默认值 | 说明 |
|---|---|---|
| Enable Coarse Location Accuracy (Network Provider) | true | 向 AndroidManifest 添加 `ACCESS_COARSE_LOCATION` 权限和网络定位硬件特性 |
| Enable Fine Location Accuracy (GPS Provider) | true | 向 AndroidManifest 添加 `ACCESS_FINE_LOCATION` 权限和 GPS 硬件特性 |
| Enable Location Updates | true | 向 AndroidManifest 添加 `CONTROL_LOCATION_UPDATES` 权限 |

这些设置通过 UPL（Unreal Plugin Language）XML 自动注入到打包后的 AndroidManifest.xml 中。

## 模块依赖

### LocationServicesAndroidImpl（Runtime，仅 Android）

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `LocationServicesBPLibrary` | 定位服务抽象层和蓝图接口 |
| `Launch` | 启动模块（私有依赖） |
| `AndroidPermission` | Android 运行时权限请求 |

### LocationServicesAndroidEditor（Editor，全平台）

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `AndroidPermission` | Android 权限相关 |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `LocationServicesBPLibrary` | 提供 `ULocationServices` 蓝图函数库和 `ULocationServicesImpl` 基类 |
| `AndroidPermission` | 提供运行时 Android 权限请求能力 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-02 | `5a48f72` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local UE::Jni::Env global. Various JNI bug fixes and cleanup | JNI 架构重构：将旧式 JNI 调用迁移到 UE5 新的 JNI 类系统（`UE::Jni::FLocationServices`），改用 `FNativeMethod` 注册机制 |
| 2023-12-14 | `3dcdaa2` | Fix usage of _activity errors | 修复 Android Activity 引用问题 |
| 2023-05-16 | `6cd0219` | non-unity fix for Android LocationServices | 修复非 Unity Build 模式下的编译问题 |

### 维护评价

- **年龄**：约 9 年（2016-12 创建），属于 👴 老古董 级别
- **更新频率**：最近一次实质性更新在 2025 年 9 月（JNI 重构），之前 2023 年有两次小修复，整体更新非常稀疏
- **状态**：维护不活跃，但 2025 年的 JNI 重构表明 Epic 仍在维护此 plugin，未标记为废弃
- **限制**：
  - `VerticalAccuracy` 在 Android 上始终返回 0（Android `LocationManager` 不提供此值）
  - 所有位置数据通过 `float` 传递，经纬度精度受限（float 只有约 7 位有效数字）
  - 仅支持 Android 平台，iOS 需要使用 `LocationServicesIOSImpl`
  - `EnabledByDefault=false`，需要手动启用
  - `requestLocationUpdates` 在主线程执行，可能影响性能
- **推荐**：如果你的目标平台包含 Android 且需要定位功能，这是官方推荐的方案。虽然更新不频繁，但功能完整稳定。注意配合 `AndroidPermission` plugin 处理运行时权限请求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LocationServicesAndroidImpl)
- [LocationServicesBPLibrary 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LocationServicesBPLibrary)
- [LocationServicesIOSImpl 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LocationServicesIOSImpl)
