# CelestialVault

> A DaySequence implementation of a Celestial Vault for Earth using ephemeris

| 属性 | 值 |
|---|---|
| 中文名 | 天体穹顶 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据表） |
| 模块 | `CelestialVault` (Runtime), `CelestialVaultEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CelestialVault) | |

## 用途

CelestialVault 是一个基于 DaySequence 的天文穹顶实现，利用**VSOP87**星历表精确计算太阳系行星的位置（包括地球、月球等），在 UE 场景中驱动天空大气、太阳光、月光、星光等组件，实现高精度的实时天文模拟。

**核心价值**：替代传统静态天空球或简单太阳方向算法，提供基于真实天文公式的日出日落、月相、行星位置、视星等计算，适用于天文教育、科学可视化、虚拟天文馆、游戏中的真实天空系统。

## 使用场景

- **天文模拟项目**：需要准确显示特定时间（过去/未来）的天空景象，如行星位置、月相。
- **开放世界游戏**：希望玩家的地理坐标、季节天气影响光照和天空外观，增强沉浸感。
- **虚拟天文馆/教育**：用户可自由调整时间、地点，观察天体运行规律。
- **科幻/奇幻**：可利用椭圆轨道参数自定义虚构行星，并复用本插件的天体计算能力。

## 蓝图用法

主要接口在 `UCelestialMaths` 蓝图函数库和 `ACelestialVaultDaySequenceActor` 类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetBodyLocation_FK5J2000_AU` | 获取指定行星在 FK5 J2000 坐标系下的位置（天文单位） | `UCelestialMaths` |
| `GetBodyLocation_FK5J2000_AU_Relativistic` | 考虑光行差的相对位置（从观察者位置看） | `UCelestialMaths` |
| `GetBodyCelestialCoordinatesAU` | 获取行星的赤经(RA)、赤纬(DEC)以及到地球、太阳的距离 | `UCelestialMaths` |
| `GetPlanetaryBodyMagnitude` | 计算行星的视星等 | `UCelestialMaths` |
| `GetMoonNormalizedAgeSimple` | 计算月球相位（归一化年龄 0~1） | `UCelestialMaths` |
| `GetIlluminationPercentage` | 根据归一化年龄获取光照百分比 | `UCelestialMaths` |
| `BVtoLinearColor` | 将恒星的 B-V 色指数转换为线性颜色 | `UCelestialMaths` |
| `LocalTimeToUTCTime` | 本地时间转 UTC 时间（考虑时区、夏令时） | `UCelestialMaths` |
| `CalendarDateToJulianDate` | 阳历日期转儒略日（UTC 或 Local） | `UCelestialMaths` |
| `JulianDateToCalendarDate` | 儒略日转阳历日期 | `UCelestialMaths` |
| `ComputeSunPositionFromCelestial` | 从天体坐标计算太阳实际方位（用于方向光） | `UCelestialMaths` |

**蓝图使用示例**：
1. 从 `CelestialVaultDaySequenceActor` 获取当前地球的 `JulianDate`（蓝图属性 `JulianDate`）。
2. 调用 `GetBodyCelestialCoordinatesAU`，传入 `FPlanetaryBodyInputData(Mars)` 和儒略日，输出火星的赤经/赤纬。
3. 使用输出的 RA/DEC 在场景中放置一个指示器，或驱动动态材质显示火星位置。

### 常用公共属性

| 属性（ACelestialVaultDaySequenceActor） | 说明 |
|---|---|
| `bUseCurrentDate` | 是否使用当前系统日期 |
| `Year / Month / Day` | 手动设定的日期 |
| `GMT_TimeZone` | 时区偏移（小时） |
| `bIsDST` | 是否夏令时 |
| `ObserverLatitude / ObserverLongitude` | 观察者地理坐标 |
| `CelestialVaultComponent` | 天体穹顶场景根组件 |
| `SunLightComponent` | 太阳方向光 |
| `MoonLightComponent` | 月球方向光 |
| `SkyAtmosphereComponent` | 天空大气组件 |
| `VolumetricCloudComponent` | 体积云组件 |
| `StarsComponent` | 恒星实例化静态网格体 |
| `PlanetsComponent` | 行星实例化静态网格体 |
| `MoonDiscComponent` | 月球圆盘网格体 |
| `JulianDate` | 当前计算使用的儒略日（实时更新） |

## C++ 用法

### 头文件引入

```cpp
#include "CelestialMaths.h"
#include "CelestialDataTypes.h"
#include "CelestialVaultDaySequenceActor.h"
```

### 基本用法

获取行星在指定儒略日的位置（FK5 J2000 坐标系）：

```cpp
#include "CelestialMaths.h"
#include "CelestialDataTypes.h"

// 在任意函数中
FPlanetaryBodyInputData MarsData;
MarsData.Name = TEXT("Mars");
MarsData.OrbitType = EOrbitType::Mars;
MarsData.Radius = 3390.0; // km

// 当前儒略日（例如从 ACelestialVaultDaySequenceActor 获取）
double JulianDay = 2460840.5; // 2025-04-22 00:00 UTC

FVector MarsLocationAU = UCelestialMaths::GetBodyLocation_FK5J2000_AU(MarsData, JulianDay);
// 结果单位：天文单位（AU）
UE_LOG(LogTemp, Log, TEXT("Mars location in AU: %s"), *MarsLocationAU.ToString());
```

**来源**：`Engine/Plugins/Experimental/CelestialVault/Source/CelestialVault/Public/CelestialMaths.h`

### 进阶用法

自定义椭圆轨道行星 + 视星等计算：

```cpp
#include "CelestialMaths.h"
#include "CelestialDataTypes.h"

// 创建虚构行星
FPlanetaryBodyInputData MyPlanet;
MyPlanet.Name = TEXT("Proxima");
MyPlanet.OrbitType = EOrbitType::Elliptic; // 椭圆轨道（当前仅占位，星历计算仅支持预设行星）
MyPlanet.Radius = 5000.0;

// 预设行星的星等计算需要距离参数
double DistanceToSunAU = 0.723; // 例如金星
double DistanceToEarthAU = 0.52;
double DistanceEarthToSunAU = 1.0;
double PhaseAngle = 0.0;

double Magnitude = UCelestialMaths::GetPlanetaryBodyMagnitude(
    MercuryData, // 以水银为例
    DistanceToSunAU,
    DistanceToEarthAU,
    DistanceEarthToSunAU,
    PhaseAngle
);
UE_LOG(LogTemp, Log, TEXT("Magnitude: %f"), Magnitude);
```

从 `ACelestialVaultDaySequenceActor` 获取天体坐标并驱动太阳方向光：

```cpp
// 在 Actor 生命周期内
ACelestialVaultDaySequenceActor* VaultActor = Cast<ACelestialVaultDaySequenceActor>(MyDaySequenceActor);
if (VaultActor)
{
    double RA, DEC, DistBodyEarth, DistBodySun, DistEarthSun;
    FPlanetaryBodyInputData SunData;
    SunData.OrbitType = EOrbitType::Earth; // 太阳相对地球的位置通过地球反向计算，此处作简化
    // 注意：实际太阳位置由内部计算，SunLightComponent 会自动更新
    UCelestialMaths::GetBodyCelestialCoordinatesAU(
        VaultActor->JulianDate,
        SunData,
        VaultActor->ObserverLatitude,
        VaultActor->ObserverLongitude,
        RA, DEC, DistBodyEarth, DistBodySun, DistEarthSun
    );
    // 将 RA/DEC 转为 UE 场景方向（引擎内部提供了辅助函数 ComputeSunPositionFromCelestial）
    // ...
}
```

## Demo 示例

**完整 .h + .cpp** 展示如何使用 CelestialVault 计算火星位置并打印。

### MyCelestialDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCelestialDemo.generated.h"

UCLASS()
class AMyCelestialDemo : public AActor
{
    GENERATED_BODY()

public:
    // 在 Tick 中更新
    virtual void Tick(float DeltaTime) override;

    // 火星的输入数据
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Celestial")
    class FPlanetaryBodyInputData MarsData;

    // 当前儒略日（可从外部传递或手动设置）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Celestial")
    double JulianDate = 2460840.5; // 2025-04-22 UTC
};
```

### MyCelestialDemo.cpp

```cpp
#include "MyCelestialDemo.h"
#include "CelestialMaths.h"
#include "CelestialDataTypes.h"

AMyCelestialDemo::AMyCelestialDemo()
{
    PrimaryActorTick.bCanEverTick = true;

    // 初始化火星数据
    MarsData.Name = TEXT("Mars");
    MarsData.OrbitType = EOrbitType::Mars;
    MarsData.Radius = 3390.0;
}

void AMyCelestialDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 获取火星在 J2000 坐标系的位置
    FVector LocationAU = UCelestialMaths::GetBodyLocation_FK5J2000_AU(MarsData, JulianDate);
    UE_LOG(LogTemp, Log, TEXT("Mars location (AU): X=%f, Y=%f, Z=%f"), LocationAU.X, LocationAU.Y, LocationAU.Z);

    // 获取火星的赤经/赤纬（相对于地球）
    double RAHours, DECDegrees, DistEarth, DistSun, DistEarthSun;
    UCelestialMaths::GetBodyCelestialCoordinatesAU(
        JulianDate,
        MarsData,
        48.8566,  // 巴黎纬度
        2.3522,   // 巴黎经度
        RAHours, DECDegrees, DistEarth, DistSun, DistEarthSun
    );
    UE_LOG(LogTemp, Log, TEXT("Mars RA: %f h, DEC: %f deg, Distance to Earth: %f AU"), RAHours, DECDegrees, DistEarth);
}
```

将上述 Actor 放置到场景中，确保项目已启用 CelestialVault 和 DaySequence 插件，运行即可看到控制台输出火星位置。

## 模块依赖

**注意**：请确保在项目的 `.Build.cs` 中添加以下依赖（仅列出独特模块）：

| 模块 | 用途 |
|---|---|
| `DaySequence` | 核心时间序列框架，提供 `ADaySequenceActor` 基类 |
| `ProceduralDaySequence` | `FCelestialVaultSequence` 的基类，用于构建程序化日序列 |
| `RHI` | 用于 GPU 相关的天空大气渲染（间接依赖） |
| `Renderer` | 渲染模块（间接依赖） |

**常见依赖**（已省略 Core/Engine/UMG 等）：
- 实际运行时，CelestialVault 内部会链接 `DaySequence`、`ProceduralDaySequence`、`Engine`、`CoreUObject` 等，用户模块只需声明 `CelestialVault` 即可自动获取传递依赖。

## 维护状态

### 近期更新

```
- 2025-11-18 e7eba216 修复了太阳光线方向的计算错误（尽管天体坐标正确）
- 2025-05-09 160c826c 向 CelestialVaultDaySequenceActor 添加了指数高度雾和全局后处理体积组件
- 2025-04-28 492e16e9 添加了月相计算
- 2025-04-22 e3039c5e 添加缺失的版权头
- 2025-04-22 c8d1177f 首次提交（Celestial Vault DaySequence 插件第一版）
```

### 维护评价

- **创建时间**：2025年4月（约半年）。
- **近期更新**：2025年11月仍有功能性修复（太阳光方向），表明仍在积极开发。
- **现状**：实验性插件，功能基本可用（支持太阳、月球、八大行星位置计算、月相、视星等、时间转换）。已知限制：椭圆轨道参数尚未实现（源码注释 `TODO_Beta`），自定义虚构行星暂不支持星历计算，仅预设太阳系行星可用。
- **推荐度**：对于需要高精度天文模拟的项目，非常推荐使用（即使处于实验阶段，核心算法来自 VSOP87 已很成熟）。但需注意该插件依赖 `DaySequence` 插件，可能对其他系统有额外要求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CelestialVault)
- [官方文档](https://docs.unrealengine.com/)（搜索 "CelestialVault" 暂无专门文档）
- [VSOP87 算法参考](http://www.celestialprogramming.com/)（插件使用的星历算法来源）