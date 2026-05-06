# CelestialVault

> A DaySequence implementation of a Celestial Vault for Earth using ephemeris

| 属性 | 值 |
|---|---|
| 中文名 | 天体穹顶 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、模板 Actor） |
| 模块 | `CelestialVault` (Runtime), `CelestialVaultEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CelestialVault) | |

## 用途

在 Unreal Engine 中基于真实星历模拟地球的昼夜循环与天体运动。该插件利用 `DaySequence` 框架（实验性）驱动：

- **太阳位置**：根据时间、地理经纬度实时计算太阳的方向与颜色，自动调节场景主光源。
- **月相变化**：按照实际月相周期显示月球的形状与亮度。
- **大气效果**：自动添加指数高度雾（`ExponentialHeightFog`）与全局后处理体积（`GlobalPostProcessVolume`），模拟真实的大气散射。
- **光照修正**：通过精确算法保证太阳光方向与世界坐标对齐，避免视觉偏差。

> 解决“需要快速搭建真实动态户外天空”的问题，无需手动调整动画曲线或光照数值。

## 使用场景

- 你在制作开放世界游戏，需要真实可靠的昼夜交替，且希望不同日期、时间、地理位置的光照效果自动变化。
- 你在开发模拟/驾驶/风景类应用，需要基于真实星历的太阳和月亮运动（如天文馆、飞行模拟）。
- 你希望将游戏内时间与现实时间同步，或快速测试不同季节/时区的光照。

## 蓝图用法

以下节点在 `CelestialVaultDaySequenceActor` 上暴露，可直接在蓝图图表中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Current Sun Direction` | 返回当前模拟时间下的太阳方向向量（世界坐标） | `UCelestialVaultDaySequenceActor` |
| `Set Latitude / Longitude` | 设置观测点的地理纬度（-90~90）和经度（-180~180） | 同上 |
| `Set Time of Day (Hours)` | 设置当前时间（0~24），驱动太阳和月亮位置 | 同上 |
| `Set Date (Year, Month, Day)` | 设置当前日期，影响太阳赤纬、月相等 | 同上 |
| `Get Moon Phase` | 返回当前月相（New, FirstQuarter, Full, LastQuarter 等枚举） | 同上 |
| `Get Moon Visibility` | 返回月球的可见性系数（0~1） | 同上 |
| `Enable Exponential Height Fog` | 启用/禁用自动指数高度雾控制 | 同上 |
| `Enable Global Post Process` | 启用/禁用自动全局后处理（色调、曝光等） | 同上 |

### 使用示例（蓝图描述）

1. **动态昼夜循环**：在关卡蓝图中，通过事件“Tick”循环调用 `Set Time of Day`，传入 `(Get World Elapsed Seconds * SpeedMultiplier) % 24`，即可驱动太阳和月亮运动。
2. **月相展示**：在 UI 中调用 `Get Moon Phase`，将返回的枚举值转换为字符串显示给玩家。
3. **真实地理位置**：在关卡开始时根据玩家选择的城市预设（如东京、巴黎），调用 `Set Latitude/Set Longitude` 和 `Set Date` 即可立即让光照变成该地真实效果。

## C++ 用法

### 头文件引入

```cpp
#include "CelestialVaultDaySequenceActor.h"
#include "CelestialVaultModule.h"   // 若需要访问模块接口
```

### 基本用法

从插件测试用例（`Engine/Plugins/Experimental/CelestialVault/Source/CelestialVault/Private/Tests`）提取的标准用法：

```cpp
// 创建并初始化天体穹顶 Actor
ACelestialVaultDaySequenceActor* Vault = World->SpawnActor<ACelestialVaultDaySequenceActor>(ACelestialVaultDaySequenceActor::StaticClass());
if (Vault)
{
    // 设置地点（北京，约北纬39.9°，东经116.4°）
    Vault->SetLatitude(39.9f);
    Vault->SetLongitude(116.4f);
    
    // 设置日期和时间（2025年6月21日中午12:00）
    Vault->SetDate(2025, 6, 21);
    Vault->SetTimeOfDay(12.0f);
    
    // 获取太阳方向
    FVector SunDir = Vault->GetSunDirection();
    // 在此应用定向光源方向：DirectionalLight->SetWorldRotation(SunDir.Rotation());
}
```

> 来源：`Engine/Plugins/Experimental/CelestialVault/Source/CelestialVault/Private/Tests/CelestialVaultTest.cpp`

### 进阶用法

从多个 test case 组合出的高级配置：

```cpp
// 开启自动大气设置
Vault->SetEnableExponentialHeightFog(true);
Vault->SetEnableGlobalPostProcess(true);

// 手动驱动时间（在 Tick 中调用）
float HoursPerSecond = 2.0f;  // 1现实秒 = 2游戏小时
CurrentTime += HoursPerSecond * DeltaTime;
if (CurrentTime >= 24.0f)
{
    CurrentTime -= 24.0f;
    // 可选：递增日期
}
Vault->SetTimeOfDay(CurrentTime);
```

## Demo 示例

以下是一个最小 C++ Actor，在关卡中自动创建并驱动天体穹顶循环。

### .h

```cpp
// MySkyActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySkyActor.generated.h"

class ACelestialVaultDaySequenceActor;

UCLASS()
class AMySkyActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void Tick(float DeltaSeconds) override;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    ACelestialVaultDaySequenceActor* Vault = nullptr;

    float CurrentHours = 6.0f;  // 从早晨6点开始
    float Speed = 0.5f;         // 每小时/每秒
};
```

### .cpp

```cpp
// MySkyActor.cpp
#include "MySkyActor.h"
#include "CelestialVaultDaySequenceActor.h"
#include "Engine/World.h"

void AMySkyActor::BeginPlay()
{
    Super::BeginPlay();

    if (UWorld* World = GetWorld())
    {
        FActorSpawnParameters Params;
        Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        Vault = World->SpawnActor<ACelestialVaultDaySequenceActor>(ACelestialVaultDaySequenceActor::StaticClass(), Params);
        if (Vault)
        {
            // 设定默认位置（英国格林威治皇家天文台）
            Vault->SetLatitude(51.5f);
            Vault->SetLongitude(-0.0f);
            Vault->SetDate(2025, 12, 21); // 冬至
            Vault->SetTimeOfDay(CurrentHours);
            
            // 启用自动大气和后期
            Vault->SetEnableExponentialHeightFog(true);
            Vault->SetEnableGlobalPostProcess(true);
        }
    }
}

void AMySkyActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (Vault)
    {
        CurrentHours += DeltaSeconds * Speed;
        if (CurrentHours >= 24.0f) CurrentHours -= 24.0f;
        Vault->SetTimeOfDay(CurrentHours);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DaySequence` | 提供时间轴与时间驱动的核心框架，CelestialVault 的主体逻辑构建于此之上 |
| `ExponentialHeightFog` | 引擎内置模块，用于模拟指数高度雾（非特殊依赖，但由插件自动控制） |
| `PostProcessVolume` | 引擎内置模块，插件控制全局后处理（同上） |

> 插件自身模块（`CelestialVault`, `CelestialVaultEditor`）已在属性表列出，此处省略。  
> 标准引擎模块（Core, CoreUObject, Engine 等）未列出。

## 维护状态

### 近期更新

- 2025-11-18 `e7eba216` 修复了太阳光方向的计算错误（尽管之前的天体计算已是正确的）
- 2025-05-09 `160c826c` 在 CelestialVaultDaySequence Actor 中添加了指数高度雾和全局后处理体积
- 2025-04-28 `492e16e9` 添加了月相功能
- 2025-04-22 `e3039c5e` 添加缺失的版权声明
- 2025-04-22 `c8d1177f` 插件首个版本提交

### 维护评价

- **创建时间**：2025-04-22，至今约 8 个月（截至 2025-12 月）。
- **活跃度**：持续有功能性更新（修复、新增雾/月相），最近更新在 2025-11-18，属于活跃维护状态。
- **实验性**：`.uplugin` 标记为 `IsExperimentalVersion=true`，表明 API 或不稳定，可能未来有变动。
- **推荐度**：适合需要真实地球天空且愿意跟随 UE 实验性插件更新的项目。适合原型和正式产品，但应留意后续版本变更。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CelestialVault)
- [官方文档](https://docs.unrealengine.com/5.5/en-US/)（DaySequence 相关章节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CelestialVault/Source/CelestialVault/Private/Tests)