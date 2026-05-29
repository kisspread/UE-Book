# Mobile Location Services - Android Implementation

> Android implementation for blueprint access for location data from mobile devices

| 属性 | 值 |
|---|---|
| 中文名 | Android 定位服务实现 |
| 分类 | Mobile |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LocationServicesAndroidEditor` (Editor), `LocationServicesAndroidImpl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-12-09 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesAndroidImpl) | |

## 用途

此插件是 `LocationServicesBPLibrary` 核心抽象插件在 Android 平台的具体实现。它负责将 Android 系统的 GPS/网络定位能力暴露给 UE 的蓝图系统，解决了在 Unreal Engine 中无法直接获取 Android 设备位置数据的问题。插件通过 JNI (Java Native Interface) 与 Android 系统的 `LocationManager` 服务进行交互。

## 使用场景

- 你在开发一款需要基于真实地理位置进行交互的移动端 AR 游戏。
- 你的应用需要根据用户所在位置展示不同的内容或触发特定事件。
- 你在构建一个导航或地理围栏相关的移动工具应用。

## 蓝图用法

此插件提供底层实现，具体的蓝图节点通常由上层插件 `LocationServicesBPLibrary` 定义。开发者应通过 `LocationServicesBPLibrary` 插件提供的统一蓝图接口进行调用。

### 核心节点 (通过 `LocationServicesBPLibrary`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Location Services` | 启动定位服务 | `ULocationServicesBPLibrary` |
| `Stop Location Services` | 停止定位服务 | `ULocationServicesBPLibrary` |
| `Get Location` | 获取最新位置数据 | `ULocationServicesBPLibrary` |
| `Check Location Permission` | 检查定位权限状态 | `UAndroidPermissionFunctionLibrary` |

### 使用示例 (蓝图描述)

在 `ULocationServicesBPLibrary` 中，`Start Location Services` 节点需要一个 `LocationAccuracy` 枚举和 `UpdateFrequency` 枚举作为输入。成功启动后，可以设置一个定时器，循环调用 `Get Location` 节点来获取最新的经纬度、精度等信息。使用前需通过 `UAndroidPermissionFunctionLibrary` 检查并请求必要的运行时权限。

## C++ 用法

### 头文件引入

```cpp
#include "LocationServicesAndroidImpl.h"
```

### 基本用法

由于该插件主要作为蓝图功能的底层实现，且被 `LocationServicesBPLibrary` 封装，直接在 C++ 中使用的情况较少。更常见的用法是通过蓝图接口或依赖 `LocationServicesBPLibrary` 模块。

## Demo 示例

以下是一个概念性的 C++ 代码示例，展示了如何通过依赖的 `LocationServicesBPLibrary` 模块间接触发定位服务。

```cpp
// MyLocationActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyLocationActor.generated.h"

UCLASS()
class AMyLocationActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLocationActor();

protected:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void StartTrackingLocation();

    UFUNCTION(BlueprintCallable)
    void StopTrackingLocation();

private:
    // 使用蓝图库中的函数
    // ULocationServicesBPLibrary::StartLocationServices 等
};
```

```cpp
// MyLocationActor.cpp
#include "MyLocationActor.h"
#include "LocationServicesBPLibrary.h"
#include "AndroidPermissionFunctionLibrary.h"

AMyLocationActor::AMyLocationActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyLocationActor::BeginPlay()
{
    Super::BeginPlay();

    // 检查并请求权限
    TArray<FString> Permissions;
    Permissions.Add(TEXT("android.permission.ACCESS_FINE_LOCATION"));
    UAndroidPermissionFunctionLibrary::AcquirePermissions(Permissions);
}

void AMyLocationActor::StartTrackingLocation()
{
    // 设置精度和频率
    ELocationAccuracy Accuracy = ELocationAccuracy::LA_Best;
    ELocationUpdateFrequency UpdateFrequency = ELocationUpdateFrequency::LUFT_Medium;
    ULocationServicesBPLibrary::StartLocationServices(Accuracy, UpdateFrequency);
}

void AMyLocationActor::StopTrackingLocation()
{
    ULocationServicesBPLibrary::StopLocationServices();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LocationServicesBPLibrary` | 提供统一的蓝图接口和抽象层 |
| `AndroidPermission` | 处理 Android 运行时权限（如位置权限）的请求与检查 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-02 | `7d7255e0` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. | 重构 JNI 交互，注册函数，添加线程安全环境，为未来调用做准备。 |
| 2023-12-15 | `3dcdaa23` | Fix usage of _activity errors | 修复了使用 `_activity` 时可能导致的错误。 |
| 2023-05-17 | `6cd02193` | non-unity fix for Android LocationServices | 修复了在非统一（Non-Unity）构建模式下的编译问题。 |
| 2023-05-16 | `70af860a` | Fix OnLocationChanged broadcast for Android to use game thread properly | 修复位置变化回调，确保其在游戏线程上正确执行。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 包含此插件的引擎插件批量提交。 |

### 维护评价

此插件是一个历史悠久的特定平台实现（Android）。虽然创建于 2016 年，但近期仍有实质性更新（2025 年的 JNI 重构），表明其仍在维护中，以适应新的引擎和平台环境变化。作为一个小型、专用的 Runtime 模块，它稳定地服务于 `LocationServicesBPLibrary` 的抽象层。**推荐使用**，但应注意其 `EnabledByDefault=false`，需要在插件管理器中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesAndroidImpl)
- [上层抽象插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/LocationServices/LocationServicesBPLibrary)
- [Android 权限插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidPermission)