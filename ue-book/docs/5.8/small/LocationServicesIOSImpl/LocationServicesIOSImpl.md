# Mobile Location Services - IOS Implementation

> IOS implementation for blueprint access for location data from mobile devices

| 属性 | 值 |
|---|---|
| 中文名 | iOS 位置服务 |
| 分类 | Mobile |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LocationServicesIOSEditor` (Editor), `LocationServicesIOSImpl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-12-09 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesIOSImpl) | |

## 用途

这个插件是 UE 跨平台位置服务框架在 iOS 平台的具体实现。它封装了 iOS 的 Core Location 框架，为 Unreal 项目提供了在 iOS 设备上通过蓝图访问设备 GPS、基站、Wi-Fi 等位置传感器数据的标准化接口。其核心目的是将 iOS 平台特定的位置 API 适配到 UE 通用的 `ULocationServicesImpl` 抽象层中，使开发者无需直接处理原生 Objective-C 代码即可获取设备位置。

## 使用场景

- 你在开发一个面向 iOS 平台的游戏或应用，需要利用设备的真实地理位置信息。
- 你正在构建一个基于位置的 AR 体验或 LBS（基于位置的服务）应用，如导航、打卡或地点相关的游戏玩法。
- 你的项目已经使用了 `LocationServicesBPLibrary` 插件提供的通用蓝图节点，并需要在 iOS 设备上运行和获取位置数据。

## 蓝图用法

此插件本身不提供新的蓝图节点，而是作为 `LocationServicesBPLibrary` 插件的 iOS 平台后端实现。当 `LocationServicesBPLibrary` 的蓝图函数（如 `Start Location Service`）在 iOS 设备上被调用时，它们将通过此插件提供的具体实现来访问 iOS 原生位置服务。

### 核心节点

由依赖的 `LocationServicesBPLibrary` 插件提供蓝图节点，此插件提供其底层实现：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Location Service` | 启动 iOS 设备的位置服务 | `ULocationServicesIOSImpl` |
| `Stop Location Service` | 停止 iOS 设备的位置服务 | `ULocationServicesIOSImpl` |
| `Get Last Known Location` | 获取最后一次获取到的位置信息 | `ULocationServicesIOSImpl` |

### 使用示例（蓝图描述）

在蓝图中，你将使用 `LocationServicesBPLibrary` 提供的节点：
1.  使用 **Init Location Service** 节点配置所需的精度和更新频率。
2.  使用 **Start Location Service** 节点开始接收位置更新。
3.  可以使用 **Get Last Known Location** 节点随时获取最新的经纬度、速度等数据。
4.  在不需要时，调用 **Stop Location Service** 节点停止服务以节省电量。
当项目打包部署到 iOS 设备时，这些蓝图节点将自动调用本插件（`LocationServicesIOSImpl`）提供的功能。

## C++ 用法

直接使用 C++ 访问此插件较为少见，通常是引擎或上层 `LocationServicesBPLibrary` 模块在内部调用。主要交互对象是其核心类 `ULocationServicesIOSImpl`。

### 头文件引入

```cpp
#include "LocationServicesIOSImpl.h"
```

### 基本用法

此插件的类 `ULocationServicesIOSImpl` 继承自 `ULocationServicesImpl`，实现了 iOS 平台的位置服务逻辑。以下代码展示了其核心接口的调用方式，但通常这些调用由 `LocationServicesBPLibrary` 封装。

```cpp
// 通常需要先获取 LocationServicesBPLibrary 提供的服务实例
ULocationServicesImpl* LocationService = GetLocationServicesImpl(); // 假设的获取方法

if (LocationService)
{
    // 1. 初始化服务，设置精度、更新频率（iOS 中可能被忽略）、最小移动距离
    bool bInitialized = LocationService->InitLocationServices(
        ELocationAccuracy::LA_Best, // 使用最高精度
        1000.0f,                    // 更新频率（毫秒），iOS实现中可能不使用此参数
        10.0f                       // 移动10米后才触发更新
    );

    if (bInitialized)
    {
        // 2. 启动位置服务
        bool bStarted = LocationService->StartLocationService();
        
        // 3. 在游戏循环中（例如 Tick），或通过回调/轮询获取位置
        FLocationServicesData LocationData = LocationService->GetLastKnownLocation();
        UE_LOG(LogTemp, Log, TEXT("当前位置: %f, %f"), LocationData.Latitude, LocationData.Longitude);

        // 4. 游戏结束或不再需要时停止服务
        LocationService->StopLocationService();
    }
}
```
*（逻辑基于公共接口 `ULocationServicesImpl` 推断，具体调用方式请参考 `LocationServicesBPLibrary` 插件源码）*

### 进阶用法

可以检查设备是否支持特定的精度等级，并在初始化前进行判断。

```cpp
ULocationServicesImpl* LocationService = GetLocationServicesImpl();
if (LocationService)
{
    // 检查设备是否支持最高精度
    if (LocationService->IsLocationAccuracyAvailable(ELocationAccuracy::LA_Best))
    {
        // 使用最高精度初始化并启动服务
        LocationService->InitLocationServices(ELocationAccuracy::LA_Best, 0, 0);
        LocationService->StartLocationService();
    }
    else
    {
        // 回退到其他精度
        LocationService->InitLocationServices(ELocationAccuracy::LA_Medium, 0, 0);
        LocationService->StartLocationService();
    }

    // 检查系统级的位置服务是否对此应用开启
    bool bSystemEnabled = LocationService->IsLocationServiceEnabled();
    UE_LOG(LogTemp, Log, TEXT("系统位置服务已为此应用启用: %s"), bSystemEnabled ? TEXT("是") : TEXT("否"));
}
```

## Demo 示例

一个最小的 C++ Actor 示例，用于在 iOS 设备上启动位置服务并输出日志。

```cpp
// LocationDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LocationServicesImpl.h"
#include "LocationDemoActor.generated.h"

UCLASS()
class ALocationDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    ALocationDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    ULocationServicesImpl* LocationService;
    float TimeSinceLastCheck;
};
```

```cpp
// LocationDemoActor.cpp
#include "LocationDemoActor.h"
#include "LocationServicesBPLibrary.h" // 用于获取服务实例

ALocationDemoActor::ALocationDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
    TimeSinceLastCheck = 0.0f;
}

void ALocationDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 通过 BPLibrary 获取 iOS 平台的位置服务实现
    LocationService = ULocationServicesBPLibrary::GetLocationServicesImpl();
    if (LocationService)
    {
        // 初始化并启动
        if (LocationService->InitLocationServices(ELocationAccuracy::LA_Best, 0, 5.0f))
        {
            LocationService->StartLocationService();
            UE_LOG(LogTemp, Log, TEXT("位置服务已启动"));
        }
    }
}

void ALocationDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (LocationService)
    {
        TimeSinceLastCheck += DeltaTime;
        // 每2秒获取一次位置
        if (TimeSinceLastCheck > 2.0f)
        {
            TimeSinceLastCheck = 0.0f;
            FLocationServicesData LocData = LocationService->GetLastKnownLocation();
            UE_LOG(LogTemp, Log, TEXT("位置更新 - 纬度: %f, 经度: %f, 精度: %f米"),
                LocData.Latitude, LocData.Longitude, LocData.HorizontalAccuracy);
        }
    }
}

void ALocationDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (LocationService)
    {
        LocationService->StopLocationService();
        UE_LOG(LogTemp, Log, TEXT("位置服务已停止"));
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。此插件的运行时模块 `LocationServicesIOSImpl` 依赖其功能性的兄弟插件 `LocationServicesBPLibrary`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到更现代的 UE_LOGF 格式。 |
| 2026-01-27 | `113268fe` | Fixed include casing mismatch when compiling ios with case sensitive on | 修复了在启用大小写敏感的 iOS 编译环境中头文件包含大小写不匹配的问题。 |
| 2026-01-14 | `1a097717` | Fix IOS CIS Issues. | 修复 iOS 持续集成 (CIS) 的问题。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | （大型引擎提交的一部分，内容不明确） |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接以使用安全协议。 |

### 维护评价

- **活跃度**：**维护不活跃**。此插件自 2016 年创建以来，核心功能代码未发生实质性更新。近期的提交（2026 年）均为工程维护性改动（宏迁移、编译修复、CI 修复），并未增加新功能或修复位置服务相关的功能缺陷。
- **稳定性**：作为一个轻量级、封装特定平台 API 的插件，在 iOS 平台稳定运行多年，核心代码结构已趋于稳定。
- **推荐度**：**仅在 iOS 平台有明确需求时使用**。该插件实现了其设计目的，但属于“维护中”而非“活跃开发”的状态。请注意，它高度依赖于 `LocationServicesBPLibrary` 插件的框架。
- **警告**：虽然近期有编译相关的维护提交，但插件的功能性部分已超过 **10 年**没有更新。使用时需留意其与最新 iOS SDK 版本的兼容性，以及是否有更现代的引擎位置服务解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesIOSImpl)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LocationServicesIOSImpl/Tests)