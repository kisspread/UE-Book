# Mobile Location Services - Android Implementation

> Android implementation for blueprint access for location data from mobile devices

| 属性 | 值 |
|---|---|
| 中文名 | 安卓定位服务 |
| 分类 | Mobile |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LocationServicesAndroidEditor` (Editor), `LocationServicesAndroidImpl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-12-09 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesAndroidImpl) | |

## 用途

本插件为 Android 平台提供了位置服务（GPS 和网络定位）的运行时实现。它不是独立的插件，而是作为 `LocationServicesBPLibrary` 插件在 Android 平台上的具体实现。

**解决的问题**：当开发者需要在 Unreal Engine 项目中获取 Android 设备的地理位置信息（经纬度、精度等）时，可以通过本插件提供的功能，结合 `LocationServicesBPLibrary` 的蓝图接口，轻松实现定位功能，而无需编写复杂的 Android 原生代码。

**存在原因**：Android 的位置服务 API 需要特定的权限和复杂的 Java/JNI 调用。本插件封装了这些平台特定的逻辑，提供了统一的蓝图和 C++ 接口，使得开发者可以跨平台（此处特指 Android）使用位置服务功能。

## 使用场景

- 你正在开发一款基于地理位置的增强现实（AR）游戏 → 用它来获取玩家的真实位置。
- 你需要为地图应用或导航应用提供实时位置数据 → 用它来集成设备的 GPS 和网络定位功能。
- 你的应用需要根据用户位置提供本地化服务（如附近商店）→ 用它来获取精确的经纬度信息。

## 蓝图用法

本插件本身不提供新的蓝图节点，它为 `LocationServicesBPLibrary` 插件中的蓝图节点提供了 Android 平台的实现。因此，蓝图用法与 `LocationServicesBPLibrary` 一致。

### 核心配置

在 Project Settings 中，可以找到 `Location Services - Android` 分类，其中包含以下配置项：

| 配置项 | 说明 |
|---|---|
| `bCoarseLocationEnabled` | 启用粗略定位精度（使用网络提供者） |
| `bFineLocationEnabled` | 启用精确定位精度（使用 GPS 提供者） |
| `bLocationUpdatesEnabled` | 启用位置更新 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Location Services` | 获取位置服务管理器实例 | `ULocationServices` |
| `Start Location Services` | 开始位置更新 | `ULocationServices` |
| `Stop Location Services` | 停止位置更新 | `ULocationServices` |
| `Get Last Known Location` | 获取最后已知的位置信息 | `ULocationServices` |
| `Is Location Accuracy Available` | 检查指定的定位精度是否可用 | `ULocationServices` |

### 使用示例（蓝图描述）

1.  在蓝图编辑器中，调用 `Get Location Services` 节点获取位置服务管理器。
2.  检查 `Is Location Accuracy Available` 来确认设备是否支持所需的定位精度（例如 `Fine`）。
3.  调用 `Start Location Services` 开始接收位置更新。
4.  在事件图表中，使用 `Event Tick` 或自定义事件，调用 `Get Last Known Location` 来获取最新的经纬度信息。
5.  当不再需要时，调用 `Stop Location Services` 停止更新。

## C++ 用法

本插件主要作为平台实现层，其公开的 C++ API 较少，主要通过 `LocationServicesBPLibrary` 模块进行交互。

### 头文件引入

```cpp
// 要使用位置服务，通常需要包含 LocationServicesBPLibrary 的头文件
#include "LocationServicesBPLibrary.h"
#include "LocationServicesComponent.h" // 如果使用组件
```

### 基本用法

从 `LocationServicesBPLibrary` 的 `ULocationServices` 类中调用函数。以下示例展示了如何启动和获取位置。

```cpp
// 获取位置服务管理器实例
ULocationServices* LocationServices = ULocationServices::GetLocationServices();

// 启动位置服务，传入所需的定位精度（如 Fine）
LocationServices->StartLocationServices(ELocationAccuracy::Fine);

// 获取最后已知的位置
FLocationServicesData LocationData = LocationServices->GetLastKnownLocation();
if (LocationData.bIsAvailable)
{
    FVector Location(LocationData.Longitude, LocationData.Latitude, LocationData.Altitude);
    // 处理位置数据...
}

// 停止位置服务
LocationServices->StopLocationServices();
```

### 进阶用法

可以结合 `ULocationServicesComponent` 组件使用，它封装了常用的生命周期管理逻辑。

```cpp
// 在角色或 Actor 中添加组件
// 在 .h 文件中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
ULocationServicesComponent* LocationServicesComponent;

// 在构造函数中
LocationServicesComponent = CreateDefaultSubobject<ULocationServicesComponent>(TEXT("LocationServices"));
LocationServicesComponent->LocationAccuracy = ELocationAccuracy::Fine;
LocationServicesComponent->UpdateInterval = 1.0f; // 每秒更新一次

// 绑定位置更新事件
LocationServicesComponent->OnLocationChanged.AddDynamic(this, &AMyCharacter::OnLocationUpdated);
```

## Demo 示例

以下是一个最小的 Actor 示例，展示了如何使用位置服务组件来持续获取位置。

### MyLocationActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LocationServicesComponent.h"
#include "MyLocationActor.generated.h"

UCLASS()
class AMyLocationActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLocationActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta = (AllowPrivateAccess = "true"))
    ULocationServicesComponent* LocationServicesComponent;

    UFUNCTION()
    void OnLocationUpdated(const FLocationServicesData& LocationData);
};
```

### MyLocationActor.cpp

```cpp
#include "MyLocationActor.h"
#include "Kismet/GameplayStatics.h"

AMyLocationActor::AMyLocationActor()
{
    PrimaryActorTick.bCanEverTick = false;

    LocationServicesComponent = CreateDefaultSubobject<ULocationServicesComponent>(TEXT("LocationServices"));
    LocationServicesComponent->LocationAccuracy = ELocationAccuracy::Fine;
    LocationServicesComponent->UpdateInterval = 2.0f;
}

void AMyLocationActor::BeginPlay()
{
    Super::BeginPlay();

    // 绑定位置更新事件
    LocationServicesComponent->OnLocationChanged.AddDynamic(this, &AMyLocationActor::OnLocationUpdated);

    // 启动位置服务
    LocationServicesComponent->StartLocationServices();

    UE_LOG(LogTemp, Warning, TEXT("Location services started."));
}

void AMyLocationActor::OnLocationUpdated(const FLocationServicesData& LocationData)
{
    if (LocationData.bIsAvailable)
    {
        FString LocationString = FString::Printf(TEXT("Lat: %f, Lon: %f, Alt: %f, Accuracy: %f"),
            LocationData.Latitude, LocationData.Longitude, LocationData.Altitude, LocationData.HorizontalAccuracy);
        UE_LOG(LogTemp, Log, TEXT("Location Updated: %s"), *LocationString);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Location data unavailable."));
    }
}
```

## 模块依赖

要使用本插件的功能，你的模块需要依赖以下模块（通过 `Build.cs` 文件）：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "LocationServicesBPLibrary", // 核心位置服务接口
    "LocationServicesAndroidImpl" // Android 实现（如果需要直接访问实现）
});
```

**重要提示**：`LocationServicesAndroidImpl` 模块仅适用于 Android 平台。在打包或运行于其他平台时，需要确保代码的平台兼容性。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-02 | `7d7255e0` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. | 注册 JNI 函数，创建 Java 类的 JNI 封装类，添加了线程局部的 UE::Jni::Env 全局变量。这是 JNI 接口的重大重构和现代化。 |
| 2023-12-15 | `3dcdaa23` | Fix usage of _activity errors | 修复使用 `_activity` 时出现的错误。 |
| 2023-05-17 | `6cd02193` | non-unity fix for Android LocationServices | 修复非 Unity 构建模式下 Android 定位服务的问题。 |
| 2023-05-16 | `70af860a` | Fix OnLocationChanged broadcast for Android to use game thread properly | 修复 Android 上 `OnLocationChanged` 事件广播，确保正确使用游戏线程。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录结构的常规维护提交。 |

### 维护评价

- **活跃维护**：最近一次实质性更新（JNI 重构）发生在 2025 年 9 月，表明 Epic 仍在积极维护此插件，尤其是在 Android 环境和 JNI 层面的现代化改进。
- **平台特定**：作为 Android 平台专有的实现，其更新往往与 Android 平台工具链、API 变化以及引擎的 JNI 框架演进相关。
- **推荐使用**：对于需要在 Android 上使用位置服务功能的 UE5 项目，这是一个官方支持的、维护中的解决方案。建议配合 `LocationServicesBPLibrary` 插件一起使用。
- **注意事项**：由于是平台特定插件，代码移植到其他平台（如 iOS）需要使用对应的实现插件（如 `LocationServicesIOSImpl`）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesAndroidImpl)
- [官方文档]() （暂无官方文档链接）
- [测试用例]() （未在插件目录内发现明显测试用例，可能位于引擎测试套件中）