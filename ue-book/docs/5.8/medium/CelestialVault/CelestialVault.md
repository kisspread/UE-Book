# Celestial Vault

> A DaySequence implementation of a Celestial Vault for Earth using ephemeris

| 属性 | 值 |
|---|---|
| 中文名 | 天穹系统 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质参数集合） |
| 模块 | `CelestialVault` (Runtime), `CelestialVaultEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CelestialVault) | |

## 用途

CelestialVault 基于天文学 VSOP87 行星星历算法，在 UE5 中实现了一个**精确的地球天穹模拟系统**。它将太阳、月球、八大行星及恒星按照真实的天体力学轨道放置在场景中，并与 DaySequence 系统集成实现昼夜更替。

核心解决的问题：
- **天文级精度的天体定位**：使用 VSOP87A 系数计算行星在 J2000 黄道坐标系中的精确位置，支持相对论光行时修正
- **完整的地球坐标系统**：WGS84 椭球体模型、大地坐标 ↔ ECEF 转换、岁差/章动矩阵
- **时间系统完整性**：儒略日、GMST/GAST 恒星时、闰秒、原子时（TAI/TT）、夏令时处理
- **与 DaySequence 的深度集成**：通过 `ACelestialVaultDaySequenceActor` 作为 DaySequence 的载体，自动驱动天空穹、日月光照方向、深空星场的旋转

## 使用场景

- 你在制作需要**真实天空**的模拟器（飞行模拟、航天仿真、天文教育软件）→ 用 CelestialVault
- 你需要在 UE 中**精确还原某一天某一地点的星空**（天文摄影、天文馆投影）→ 用 CelestialVault
- 你在做地球尺度的**建筑可视化/地理信息系统**，需要匹配真实太阳位置 → 用 CelestialVault
- 你需要一个自动随时间旋转的**天球穹顶**，包含真实行星和恒星 → 用 CelestialVault

## 蓝图用法

### 核心节点

**天体查询与计算**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ComputeCurrentSunInfo` | 获取当前时间的太阳天体信息（赤经/赤纬/距离） | `ACelestialVaultDaySequenceActor` |
| `ComputeCurrentMoonInfo` | 获取当前时间的月球天体信息（含相位、光照率） | `ACelestialVaultDaySequenceActor` |
| `ComputeSunInfo` | 在指定儒略日计算太阳信息 | `ACelestialVaultDaySequenceActor` |
| `ComputeMoonInfo` | 在指定儒略日计算月球信息 | `ACelestialVaultDaySequenceActor` |
| `GetClosestStar` | 查询指定方向最近的恒星 | `ACelestialVaultDaySequenceActor` |
| `GetClosestPlanetaryBody` | 查询指定方向最近的行星/卫星 | `ACelestialVaultDaySequenceActor` |
| `GetPlanetaryBodyByVSOP87Type` | 按 VSOP87 类型获取行星信息 | `ACelestialVaultDaySequenceActor` |

**日期时间与夏令时**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDate` | 获取当前日期（不含时间） | `ACelestialVaultDaySequenceActor` |
| `GetDateAndTime` | 获取当前日期和时间 | `ACelestialVaultDaySequenceActor` |
| `GetJulianDate` | 获取当前儒略日 | `ACelestialVaultDaySequenceActor` |
| `IsDaylightSavingsNow` | 当前是否处于夏令时 | `ACelestialVaultDaySequenceActor` |
| `GetCelestialVaultAngle` | 获取指定时刻的天穹旋转角（GMST） | `ACelestialVaultDaySequenceActor` |

**天文数学库（静态函数）**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UTCDateTimeToJulianDate` | UTC 日期时间转儒略日 | `UCelestialMaths` |
| `GetSunInformation` | 计算太阳完整属性 | `UCelestialMaths` |
| `GetBodyCelestialCoordinatesAU` | 计算行星在天球上的坐标 | `UCelestialMaths` |
| `GeodeticLatLonToECEFXYZAU` | 大地坐标转 ECEF（天文单位） | `UCelestialMaths` |
| `GetEarthCenterTransformUEFrame` | 获取地球原点在 UE 帧中的变换 | `UCelestialMaths` |
| `BVtoLinearColor` | 恒星 B-V 色指数转 RGB 颜色 | `UCelestialMaths` |

**VSOP87 行星位置（直接访问）**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMercuryLocation` / `GetMercuryVelocity` | 水星位置/速度 | `UVSOP87` |
| `GetVenusLocation` / `GetVenusVelocity` | 金星位置/速度 | `UVSOP87` |
| `GetEarthLocation` / `GetEarthVelocity` | 地球位置/速度 | `UVSOP87` |
| `GetMarsLocation` ~ `GetNeptuneVelocity` | 其余行星 | `UVSOP87` |
| `GetMoonLocation` / `GetMoonVelocity` | 月球位置/速度 | `UVSOP87` |

### 使用示例（蓝图描述）

**基础用法：放置天穹 Actor**
1. 在关卡中放置 `ACelestialVaultDaySequenceActor`（搜索 "Celestial Vault Day Sequence Actor"）
2. 在细节面板中设置 **Location** 区域：
   - `Latitude` / `Longitude`：你希望的观测点地理坐标（如蒙特利尔：45.0, -73.0）
   - `GMT_TimeZone`：时区偏移（如 -5.0 表示 EST）
3. 设置 **Date** 区域：
   - `bUseCurrentDate = true` 自动使用系统日期，或手动指定 Year/Month/Day
4. 添加 DaySequence 资产控制一天的光照变化
5. 拖入 `CelestialStarCatalog` 和 `PlanetsCatalog` 数据表

**查询当前太阳位置**
1. 从 CelestialVaultDaySequenceActor 引脚拖出 → 调用 `ComputeCurrentSunInfo`
2. 返回 `FStellarBody` 结构体，包含 `RA`（赤经/时）、`DEC`（赤纬/度）、`DistanceInAU` 等
3. 可直接将 `RA`/`DEC` 显示为文字或用于调试

**查询指定日期的月球相位**
1. 获取当前 JulianDate：调用 `GetJulianDate`（从 Actor 引脚）
2. 调用 `UCelestialMaths::GetMoonNormalizedAgeSimple`（传入 JulianDate）
3. 返回值 0=新月，0.25=上弦月，0.5=满月，1=下一个新月

**在蓝图中获取行星星历位置**
1. 调用 `UCelestialMaths::UTCDateTimeToJulianDate` 将日期转为儒略日
2. 调用 `UCelestialMaths::JulianDateToVSOP87Time` 转为 VSOP87 专用时间
3. 调用 `UVSOP87::GetMarsLocation` 等获取行星在黄道坐标系中的 XYZ 位置（天文单位）

## C++ 用法

### 头文件引入

```cpp
#include "CelestialMaths.h"
#include "CelestialVaultDaySequenceActor.h"
#include "VSOP87.h"
#include "DaylightSavings.h"
#include "CelestialDataTypes.h"
```

### 基本用法

```cpp
// 计算 2026-06-21 12:00 UTC 太阳在蒙特利尔 (45°N, 73°W) 的位置
FDateTime UTCDate(2026, 6, 21, 12, 0, 0);
double JulianDate = UCelestialMaths::UTCDateTimeToJulianDate(UTCDate);

FStellarBody SunInfo = UCelestialMaths::GetSunInformation(
    JulianDate,
    45.0,   // ObserverLatitude
    -73.0,  // ObserverLongitude
    false   // bGeoCentric
);

UE_LOG(LogTemp, Log, TEXT("Sun RA: %.2f h, DEC: %.2f deg"),
    SunInfo.RA, SunInfo.DEC);
```

### 进阶用法

```cpp
// 1. 使用缓存加速多行星查询
FPlanetaryBodyKinematicState EarthState =
    UCelestialMaths::GetPlanetaryBodyKinematicState_AU(JulianDate, EVSOP87BodyType::Earth);

// 2. 计算多个行星坐标（复用 Earth 缓存）
double RA, DEC, RA2000, DEC2000, RAGeo, DECGeo, DistBody, DistSun, DistEarth;
UCelestialMaths::GetBodyCelestialCoordinatesAU_UsingKnownState(
    JulianDate, EVSOP87BodyType::Mars, EarthState,
    45.0, -73.0, false, false,
    RA2000, DEC2000, RA, DEC, RAGeo, DECGeo,
    DistBody, DistSun, DistEarth
);

// 3. 计算行星视星等
double PhaseAngle;
double Magnitude = UCelestialMaths::GetPlanetaryBodyMagnitude(
    EVSOP87BodyType::Mars, DistSun, DistBody, DistEarth, PhaseAngle);

// 4. 获取地球变换矩阵用于场景放置
FTransform EarthTransform = UCelestialMaths::GetEarthCenterTransformUEFrame(
    45.0, -73.0, 0.0, false);
```

## Demo 示例

```cpp
// MySkyController.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CelestialMaths.h"
#include "CelestialVaultDaySequenceActor.h"
#include "MySkyController.generated.h"

UCLASS()
class AMySkyController : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Observer")
    double Latitude = 48.8566;  // Paris

    UPROPERTY(EditAnywhere, Category = "Observer")
    double Longitude = 2.3522;

    UPROPERTY(EditAnywhere, Category = "Observer")
    double TimeZoneOffset = 1.0;

    UPROPERTY(Transient, BlueprintReadOnly, Category = "Results")
    FStellarBody CurrentSunInfo;

    UPROPERTY(Transient, BlueprintReadOnly, Category = "Results")
    FPlanetaryBody CurrentMoonInfo;

    UPROPERTY(Transient, BlueprintReadOnly, Category = "Results")
    double MoonPhaseAge = 0.0;

    virtual void Tick(float DeltaTime) override
    {
        Super::Tick(DeltaTime);

        double JD = UCelestialMaths::UTCDateTimeToJulianDate(FDateTime::UtcNow());

        CurrentSunInfo = UCelestialMaths::GetSunInformation(
            JD, Latitude, Longitude, false);

        // 月球位置需要先获取地球运动状态以复用缓存
        FPlanetaryBodyKinematicState EarthState =
            UCelestialMaths::GetPlanetaryBodyKinematicState_AU(
                JD, EVSOP87BodyType::Earth);

        double RA2000, DEC2000, RA, DEC, RAGeo, DECGeo;
        double DistBody, DistSun, DistEarth;
        UCelestialMaths::GetBodyCelestialCoordinatesAU_UsingKnownState(
            JD, EVSOP87BodyType::Moon, EarthState,
            Latitude, Longitude, false, false,
            RA2000, DEC2000, RA, DEC, RAGeo, DECGeo,
            DistBody, DistSun, DistEarth);
        CurrentMoonInfo.DistanceInAU = DistBody;
        CurrentMoonInfo.RA = RA;
        CurrentMoonInfo.DEC = DEC;

        MoonPhaseAge = UCelestialMaths::GetMoonNormalizedAgeSimple(JD);
    }
};
```

## 模块依赖

`CelestialVault.Build.cs` 使用的依赖：

| 模块 | 用途 |
|---|---|
| `DaySequence` | 驱动天空昼夜变化的核心系统（DaySequence 播放器/子系统） |
| `DaySequenceEditor` | 编辑器中的 DaySequence 编辑支持 |
| `Niagara` | 恒星/行星粒子渲染（星空实例化） |

无特殊依赖（仅标准 Core/Engine/Slate 等）之外，以上三个是该插件独特的依赖项。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-30 | `8701bcf1` | Fix TopocentricVaultComponent attachment to use NorthOffsetComponent as parent | 修复地心视差穹组件的父级附着关系 |
| 2026-04-29 | `b69b383a` | Fixed: The DeepSky now follows the observer to remove the parallax effect on Stars | 深空天球现在跟随观察者移动，消除恒星视差 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到 UE_LOGF |
| 2026-04-10 | `8130162b` | Switched the Celestial Vault Plugin to Beta | 将插件切换为 Beta 版本并调整高动态范围曝光参数 |

### 维护评价

- **创建时间**：2026-04-10，非常新的插件（约 1 个月）
- **Beta 状态**：`IsBetaVersion=true`，API 尚未稳定，后续可能有破坏性变更
- **活跃度**：创建后持续有 bug 修复和优化更新，最近一次距今约 1 周
- **代码质量**：源码注释极为详尽（天文学公式、单位约定、坐标系说明），由 Epic 内部天文爱好者 albán bergeret 开发
- **已知限制**：月球相位近似计算精度限于 2025 年前后约 100 年；秋令时切换小时（`DaylightSavingsSwitchHour`）目前限制在 0-23
- **推荐状态**：适合需要精确天空的项目进行实验性集成，但不建议在生产环境中依赖此 Beta API

> ⚠️ **Beta 警告**：此插件处于 Beta 阶段，API 和功能可能在后续版本中发生重大变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CelestialVault)
- 官方文档（无）