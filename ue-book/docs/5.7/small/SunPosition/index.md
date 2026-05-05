# Sun Position Calculator

> Calculates the sun position based on latitude/longitude and date/time.

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | SunPosition (Runtime, PostEngineInit) |
| 创建时间 | 2018-10-01 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SunPosition) | |

## 用途

根据地球上任意经纬度坐标和日期时间，精确计算太阳的仰角（Elevation）、方位角（Azimuth）、日出/日落时间以及太阳正午时刻。算法基于 [NOAA Solar Calculator](https://www.esrl.noaa.gov/gmd/grad/solcalc/calcdetails.html) 的天文学公式，包含大气折射修正。

这个 plugin 解决的核心问题是：**在虚拟场景中还原真实世界的日照方向**。当你需要让场景光照与特定地理位置和时间的真实太阳位置一致时，就需要它。

## 使用场景

- 你在做建筑可视化，需要精确模拟某栋建筑在某城市某时间的日照情况
- 你在做虚拟制片（Virtual Production），需要与真实拍摄地点的日光方向同步
- 你在做城市规划模拟，需要展示不同季节/时间的建筑阴影变化
- 你需要一个基于真实天文数据的昼夜循环系统，而非简单的旋转方向光

## 蓝图用法

plugin 默认未启用，需要先在 **Edit → Plugins** 中搜索 "Sun Position Calculator" 并启用。

启用后，编辑器的 **放置面板（Place Actors）→ Lights** 分类下会出现 **Sun and Sky** 预制蓝图，可直接拖入场景使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Sun Position` | 根据经纬度、时区、日期时间计算太阳位置 | `USunPositionFunctionLibrary` |

### FSunPositionData 输出结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `Elevation` | float | 太阳仰角（已偏移 180° 适配 UE 坐标系） |
| `CorrectedElevation` | float | 经大气折射修正后的太阳仰角 |
| `Azimuth` | float | 太阳方位角（从正北顺时针，单位：度） |
| `SunriseTime` | FTimespan | 当日日出时间 |
| `SunsetTime` | FTimespan | 当日日落时间 |
| `SolarNoon` | FTimespan | 当日太阳正午时刻 |

### 使用示例（蓝图描述）

1. 新建蓝图，添加一个 **Directional Light** 组件
2. 添加一个自定义事件或 Tick 事件
3. 拖出 **Get Sun Position** 节点（在 Sun Position 分类下）
4. 填入目标城市的经纬度、时区、夏令时标志、以及当前日期时间
5. 从 **SunPositionData** 引脚拆分出 `Elevation` 和 `Azimuth`
6. 用 **Make Rotator** 将 Azimuth 作为 Yaw、Elevation 作为 Pitch，设置到 Directional Light 的旋转

**注意**：Elevation 已经偏移了 180°（即真实仰角 0° = 返回值 180°），这是为了适配 UE 的坐标系统，你可以直接将其用于 Rotator 的 Pitch。

## C++ 用法

### 头文件引入

```cpp
#include "SunPosition.h"
```

### 基本用法

```cpp
// 计算太阳位置
FSunPositionData SunData;
USunPositionFunctionLibrary::GetSunPosition(
    40.7128f,   // Latitude  (纬度，北正南负)
    -74.0060f,  // Longitude (经度，东正西负)
    -5.0f,      // TimeZone  (时区偏移，EST = -5)
    false,      // bIsDaylightSavingTime (是否夏令时)
    2024, 6, 21, // Year, Month, Day
    12, 0, 0,    // Hours, Minutes, Seconds
    SunData     // [out] 输出参数
);

// 使用结果
float Azimuth   = SunData.Azimuth;    // 方位角
float Elevation = SunData.Elevation;  // 仰角（偏移180°）
FTimespan Sunrise = SunData.SunriseTime;
FTimespan Sunset  = SunData.SunsetTime;
```

### 进阶用法

结合 Directional Light 驱动日照方向：

```cpp
// 在 Tick 或定时器中更新太阳方向
void AMySunActor::UpdateSunDirection()
{
    FSunPositionData SunData;
    USunPositionFunctionLibrary::GetSunPosition(
        Latitude, Longitude, TimeZone, bIsDST,
        CurrentYear, CurrentMonth, CurrentDay,
        CurrentHour, CurrentMinute, CurrentSecond,
        SunData
    );

    // 将方位角和仰角转换为旋转
    FRotator SunRotation;
    SunRotation.Pitch = SunData.Elevation;   // 已偏移180°
    SunRotation.Yaw   = SunData.Azimuth;
    SunRotation.Roll  = 0.0f;

    DirectionalLight->SetActorRotation(SunRotation);
}
```

## Demo 示例

### Build.cs 依赖

```csharp
// 在你的模块 .Build.cs 中添加（运行时使用不需要额外依赖，SunPosition 是 Runtime 模块）
PublicDependencyModuleNames.AddRange(new string[] {
    "SunPosition"
});
```

### 最小示例：太阳方向驱动器

```cpp
// MySunTracker.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SunPosition.h"
#include "MySunTracker.generated.h"

UCLASS()
class AMySunTracker : public AActor
{
    GENERATED_BODY()

public:
    AMySunTracker();

    UPROPERTY(EditAnywhere, Category = "Location")
    float Latitude = 40.7128f;  // New York

    UPROPERTY(EditAnywhere, Category = "Location")
    float Longitude = -74.0060f;

    UPROPERTY(EditAnywhere, Category = "Location")
    float TimeZone = -5.0f;

    UPROPERTY(EditAnywhere, Category = "Location")
    bool bIsDaylightSavingTime = false;

    UPROPERTY(EditAnywhere, Category = "Sun")
    float TimeSpeed = 60.0f;  // 时间流速倍率

    UPROPERTY(VisibleAnywhere)
    class UDirectionalLightComponent* SunLight;

    virtual void Tick(float DeltaSeconds) override;

private:
    double ElapsedSeconds = 43200.0;  // 从正午开始
};
```

```cpp
// MySunTracker.cpp
#include "MySunTracker.h"
#include "Components/DirectionalLightComponent.h"

AMySunTracker::AMySunTracker()
{
    PrimaryActorTick.bCanEverTick = true;
    SunLight = CreateDefaultSubobject<UDirectionalLightComponent>(TEXT("SunLight"));
    RootComponent = SunLight;
}

void AMySunTracker::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    ElapsedSeconds += DeltaSeconds * TimeSpeed;

    // 简化：用一天中的时间推进（实际项目应使用真实日期时间）
    int32 TotalSeconds = FMath::Fmod(ElapsedSeconds, 86400.0);
    int32 Hours   = TotalSeconds / 3600;
    int32 Minutes = (TotalSeconds % 3600) / 60;
    int32 Seconds = TotalSeconds % 60;

    FSunPositionData SunData;
    USunPositionFunctionLibrary::GetSunPosition(
        Latitude, Longitude, TimeZone, bIsDaylightSavingTime,
        2024, 6, 21,  // 固定日期，仅时间变化
        Hours, Minutes, Seconds,
        SunData
    );

    FRotator SunRotation(SunData.Elevation, SunData.Azimuth, 0.0f);
    SetActorRotation(SunRotation);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、Component 等） |
| `Projects` | 插件管理接口 |
| `Slate` | UI 框架（编辑器放置面板） |
| `SlateCore` | Slate 核心 |

编辑器额外依赖（仅编辑器构建）：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器功能 |
| `EditorFramework` | 编辑器框架 |
| `PlacementMode` | 放置面板注册 |

**使用者只需依赖 `SunPosition` 模块**即可，上述依赖由 plugin 自身处理。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2023-01-16 | `7ce67da71ab9` | IWYU 清理，减少不必要的 #include（编译优化，无功能变更） |
| 2022-11-07 | `0a10c21ff628` | Engine staging 更新（批量同步，非专门针对此 plugin） |
| 2022-11-03 | `049a3a702172` | 添加预留 #include（为未来变更做准备） |

### 维护评价

- **创建时间**：2018 年 10 月，至今约 7.6 年
- **最近更新**：2023 年 1 月，但均为编译层面的 IWYU 清理，**无实质性功能更新**
- **维护状态**：⚠️ **维护不活跃** — 超过 2 年没有功能性更新
- **稳定性**：算法成熟（基于 NOAA 天文公式），功能完整，不太需要更新
- **已知限制**：
  - Elevation 值偏移了 180°，需要开发者了解这一设计决策
  - 没有季节性日照时长变化的独立 API（但可通过 SunriseTime/SunsetTime 计算）
  - 内嵌的验证测试使用的是 2017-2018 年的数据
- **推荐**：✅ 功能稳定可用，适合需要真实太阳位置计算的项目。虽然不活跃维护，但天文算法本身不会变化，风险较低。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SunPosition)
- [NOAA Solar Calculator（算法参考）](https://www.esrl.noaa.gov/gmd/grad/solcalc/calcdetails.html)
