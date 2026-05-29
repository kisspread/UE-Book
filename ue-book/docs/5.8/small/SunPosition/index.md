# Sun Position Calculator

> Calculates the sun position based on latitude/longitude and date/time.

| 属性 | 值 |
|---|---|
| 中文名 | 太阳位置计算器 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质/纹理资产） |
| 模块 | `SunPosition` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-10-01 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SunPosition) | |

## 用途

这个插件为 Unreal Engine 提供了一个**基于真实世界天文学模型的太阳位置计算工具**。它通过输入地理位置（经纬度）、日期和时间，能够精确计算出该时刻太阳在天空中的**高度角**和**方位角**，以及当日的**日出、日落和正午时间**。

它解决的问题是：在影视制作、建筑可视化、游戏开发等需要真实世界光照环境的场景中，为方向光（Directional Light）或其他需要模拟太阳运动的物体提供精确的天文数据，确保光影角度和时间的准确性，比手动调整关键帧更科学、高效。

## 使用场景

- **建筑可视化（Arch Viz）**：你需要根据特定城市（如北京、纽约）的特定日期（如夏至、冬至）来展示建筑在一天中不同时段的真实光影效果。
- **影视预览（Previs）**：在虚拟拍摄前，你需要根据拍摄地点和日期规划日出/日落时间及光线角度。
- **开放世界游戏**：你的游戏世界基于真实地理位置，需要动态、准确的昼夜循环和日照角度。
- **动态天气/环境系统**：与时间系统结合，自动控制场景中方向光的旋转，模拟真实日月升落。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Sun Position` | 根据给定的经纬度、时区和日期时间，计算并返回太阳位置数据 | `USunPositionFunctionLibrary` |
| `SunPositionData` (结构体) | 存储太阳位置计算结果的结构体，包含高度角、方位角等 | `FSunPositionData` |

### 使用示例（蓝图描述）

1.  **准备数据**：在你的蓝图中，准备好代表**经度（Longitude）**、**纬度（Latitude）**、**时区（TimeZone）**、**是否夏令时（bIsDaylightSavingTime）** 以及具体**年、月、日、时、分、秒**的变量。
2.  **调用计算**：使用 `Get Sun Position` 节点。将上一步的变量连接到对应的输入引脚。
3.  **获取结果**：执行节点后，从 `SunPositionData` 输出引脚拖线，可以 break 结构体获取 `Elevation` (高度角)、`Azimuth` (方位角) 等字段。
4.  **应用结果**：将 `Azimuth` 值通过数学运算转换为旋转值（Pitch/Yaw），然后通过 `Set World Rotation` 节点应用到场景中的**方向光（Directional Light）** 上。可以用 `Elevation` 来微调光源的俯仰角。
5.  **结合时间系统**：将你的游戏时间系统（小时、分钟等）连接到该节点，即可实现随游戏时间动态变化的、真实的日照系统。

## C++ 用法

### 头文件引入

```cpp
#include "SunPosition.h"
```

### 基本用法

获取特定地点和时间的太阳位置数据。
```cpp
// 准备输入参数
float Latitude = 39.9042f; // 纬度 (例如：北京)
float Longitude = 116.4074f; // 经度
float TimeZone = 8.0f; // 时区 (东八区)
bool bIsDaylightSavingTime = false; // 是否夏令时
int32 Year = 2023;
int32 Month = 6;
int32 Day = 21; // 夏至
int32 Hours = 12;
int32 Minutes = 0;
int32 Seconds = 0;

// 用于存储结果的结构体
FSunPositionData SunData;

// 调用静态函数计算
USunPositionFunctionLibrary::GetSunPosition(
    Latitude, Longitude, TimeZone, bIsDaylightSavingTime,
    Year, Month, Day, Hours, Minutes, Seconds,
    SunData
);

// 使用结果
float CurrentElevation = SunData.Elevation;
float CurrentAzimuth = SunData.Azimuth;
FTimespan TodaySunrise = SunData.SunriseTime;
```

### 进阶用法

将计算逻辑封装到自定义组件中，与游戏时间系统集成。
```cpp
// 在自定义Actor组件的TickComponent中
void USunPositionComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 假设 GetGameTimeOfDay() 返回一个包含当前游戏内年月日时分秒的结构体
    FGameDateTime CurrentTime = GetGameTimeOfDay();

    FSunPositionData SunData;
    USunPositionFunctionLibrary::GetSunPosition(
        TargetLatitude, TargetLongitude, TimeZone, false,
        CurrentTime.Year, CurrentTime.Month, CurrentTime.Day,
        CurrentTime.Hours, CurrentTime.Minutes, CurrentTime.Seconds,
        SunData
    );

    // 将方位角转换为方向光的旋转
    FRotator LightRotation(0.0f, SunData.Azimuth, 0.0f); // Azimuth 映射到 Yaw
    // 可以进一步用 CorrectedElevation 调整俯仰角
    LightRotation.Pitch = -SunData.CorrectedElevation; // 负值使光向下

    if (DirectionalLightActor)
    {
        DirectionalLightActor->SetActorRotation(LightRotation);
    }
}
```

## Demo 示例

### SunPositionDemo.h
```cpp
// SunPositionDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SunPosition.h"
#include "SunPositionDemo.generated.h"

UCLASS()
class ASunPositionDemo : public AActor
{
    GENERATED_BODY()

public:
    ASunPositionDemo();

    virtual void BeginPlay() override;

    // 用于存储计算结果并显示在编辑器中
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Sun Demo")
    FSunPositionData LastCalculatedSunData;

    // 要查询的位置（可在编辑器中调整）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sun Demo")
    float QueryLatitude = 39.9042f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sun Demo")
    float QueryLongitude = 116.4074f;

    // 执行一次计算并更新数据
    UFUNCTION(BlueprintCallable, Category = "Sun Demo")
    void CalculateSunPositionForNow();

    // 指向场景中方向光的指针（可在编辑器中指定）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sun Demo")
    AActor* SunLightActor;
};
```

### SunPositionDemo.cpp
```cpp
// SunPositionDemo.cpp
#include "SunPositionDemo.h"
#include "Engine/DirectionalLight.h"

ASunPositionDemo::ASunPositionDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ASunPositionDemo::BeginPlay()
{
    Super::BeginPlay();
    // 游戏开始时计算一次
    CalculateSunPositionForNow();
}

void ASunPositionDemo::CalculateSunPositionForNow()
{
    // 获取当前系统时间
    FDateTime Now = FDateTime::Now();

    // 调用SunPosition插件的核心函数
    USunPositionFunctionLibrary::GetSunPosition(
        QueryLatitude,
        QueryLongitude,
        8.0f, // 假设东八区
        false, // 假设非夏令时
        Now.GetYear(),
        Now.GetMonth(),
        Now.GetDay(),
        Now.GetHour(),
        Now.GetMinute(),
        Now.GetSecond(),
        LastCalculatedSunData
    );

    // 如果指定了太阳光源，就应用结果
    if (SunLightActor)
    {
        // 将方位角(Azimuth)转换为Yaw旋转
        FRotator NewRotation(0.0f, LastCalculatedSunData.Azimuth, 0.0f);
        SunLightActor->SetActorRotation(NewRotation);

        UE_LOG(LogTemp, Log, TEXT("Sun Position Calculated - Azimuth: %.2f, Elevation: %.2f"),
            LastCalculatedSunData.Azimuth, LastCalculatedSunData.Elevation);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧版 `UE_LOG` 迁移至新版 `UE_LOGF`，属于引擎日志系统升级适配。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 批量插件提交，无具体功能改动描述。 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 为未来功能添加头文件包含，属于代码准备性提交，无功能影响。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件描述中的链接从 HTTP 更新为 HTTPS，属安全协议升级。 |
| 2022-02-03 | `338109ae` | fix FDateTime::GetJulianDay() | 修复了引擎 `FDateTime::GetJulianDay()` 函数的问题，该函数被本插件用于天文计算，此修复直接影响本插件准确性。 |

### 维护评价

SunPosition 插件自2018年创建以来，已存在约8年，属于一个**稳定但更新不频繁的实用工具**。

- **优点**：功能明确、单一，API设计简单（一个静态函数和一个结构体），易于集成和使用。作为官方内置插件，其天文算法的可靠性有保障。
- **维护状况**：最近一次功能性更新（修复 `GetJulianDay`）停留在2022年初，此后主要是编译兼容性修复（如日志宏迁移）。**在最近1年内没有实质性功能新增或重大优化**。
- **推荐度**：如果你需要**基于真实世界数据的、开箱即用的太阳位置计算功能**，它仍然是**推荐使用**的首选方案。虽然它可能未采用最新的引擎特性（如 `UE_LOGF` 是后来迁移的），但其核心算法稳定。对于要求极致性能或需要深度定制天文算法的项目，可能需要考虑自行实现或寻找第三方库。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SunPosition)
- 官方文档链接为空。