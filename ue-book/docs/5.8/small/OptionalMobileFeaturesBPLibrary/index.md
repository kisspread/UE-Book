# Optional Mobile Features Blueprint Library

> Gives blueprint access to Sound Volume, Battery Charge Level, and System Temperature for Android and iOS devices

| 属性 | 值 |
|---|---|
| 中文名 | 移动设备可选功能库 |
| 分类 | Mobile |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OptionalMobileFeaturesBPLibrary` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-12-09 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OptionalMobileFeaturesBPLibrary) | |

## 用途

该插件为 Android 和 iOS 移动设备提供了硬件状态的蓝图查询接口。它封装了操作系统层面的 API，使蓝图无需编写 C++ 即可获取以下设备信息：

- **音量状态**：当前系统媒体音量百分比
- **电池电量**：当前电池剩余百分比
- **设备温度**：电池温度（摄氏度）
- **耳机状态**：是否插入有线耳机

这些信息在桌面平台（Windows/Mac/Linux）上通常无效或返回默认值，插件主要面向移动部署场景。

## 使用场景

- 你需要根据设备电量动态降低画质或关闭特效 → 用 `GetBatteryLevel()`
- 你需要根据设备温度触发过热保护机制 → 用 `GetBatteryTemperature()`
- 你需要在蓝图中同步游戏音量与系统音量 → 用 `GetVolumeState()`
- 你需要检测耳机插拔来切换音频输出方式 → 用 `AreHeadphonesPluggedIn()`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetVolumeState` | 返回设备当前音量（0-100%） | `UOptionalMobileFeaturesBPLibrary` |
| `GetBatteryLevel` | 返回设备当前电池电量（0-100） | `UOptionalMobileFeaturesBPLibrary` |
| `GetBatteryTemperature` | 返回设备电池温度（摄氏度） | `UOptionalMobileFeaturesBPLibrary` |
| `AreHeadphonesPluggedIn` | 返回是否插入耳机 | `UOptionalMobileFeaturesBPLibrary` |

所有节点位于 **Mobile** 分类下，均为 `BlueprintCallable` 静态函数。

### 使用示例（蓝图描述）

**电量监控与画质自适应：**

1. 使用 `Event Tick` 定时调用 `GetBatteryLevel`
2. 将返回值连接到 `Branch` 节点，判断 `<= 20`
3. 若为 True，通过 `Execute Console Command` 执行 `sg.PostProcessQuality 0` 降低画质
4. 同时使用 `GetBatteryTemperature` 检测温度是否超过 40°C，触发额外保护逻辑

**耳机检测音频切换：**

1. 调用 `AreHeadphonesPluggedIn` 获取返回的 Boolean
2. 通过 `Branch` 节点分流
3. 耳机插入时设置背景音乐为立体声，拔出时切换为单声道或降低音量

## C++ 用法

### 头文件引入

```cpp
#include "OptionalMobileFeaturesBPLibrary.h"
```

### 基本用法

所有函数均为静态方法，可直接调用：

```cpp
// 获取设备音量（0-100%）
int32 Volume = UOptionalMobileFeaturesBPLibrary::GetVolumeState();

// 获取电池电量（0-100）
int32 Battery = UOptionalMobileFeaturesBPLibrary::GetBatteryLevel();

// 获取电池温度（摄氏度）
float Temperature = UOptionalMobileFeaturesBPLibrary::GetBatteryTemperature();

// 检测耳机是否插入
bool bHasHeadphones = UOptionalMobileFeaturesBPLibrary::AreHeadphonesPluggedIn();
```

### 进阶用法

结合定时器实现周期性设备状态监控：

```cpp
// 在 BeginPlay 中启动定时器
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    FTimerHandle MonitorHandle;
    GetWorldTimerManager().SetTimer(
        MonitorHandle, this, &AMyActor::CheckDeviceStatus, 5.0f, true);
}

// 定期检查设备状态并执行相应逻辑
void AMyActor::CheckDeviceStatus()
{
    int32 BatteryLevel = UOptionalMobileFeaturesBPLibrary::GetBatteryLevel();
    float Temperature = UOptionalMobileFeaturesBPLibrary::GetBatteryTemperature();

    // 低电量保护
    if (BatteryLevel <= 15)
    {
        // 降低渲染质量、关闭非必要特效
        GEngine->Exec(GetWorld(), TEXT("sg.PostProcessQuality 0"));
        GEngine->Exec(GetWorld(), TEXT("sg.EffectsQuality 0"));
    }

    // 过热保护
    if (Temperature >= 42.0f)
    {
        // 降低帧率限制
        GEngine->Exec(GetWorld(), TEXT("t.MaxFPS 30"));
    }
}
```

## Demo 示例

```cpp
// DeviceMonitorComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "DeviceMonitorComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UDeviceMonitorComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UDeviceMonitorComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Monitor")
    float CheckInterval = 5.0f;

    UPROPERTY(BlueprintReadOnly, Category="Monitor")
    int32 CurrentBatteryLevel;

    UPROPERTY(BlueprintReadOnly, Category="Monitor")
    float CurrentTemperature;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnLowBattery, int32, Level);

    UPROPERTY(BlueprintAssignable, Category="Monitor")
    FOnLowBattery OnLowBattery;

protected:
    virtual void BeginPlay() override;

private:
    FTimerHandle MonitorTimerHandle;

    UFUNCTION()
    void UpdateDeviceStatus();
};
```

```cpp
// DeviceMonitorComponent.cpp
#include "DeviceMonitorComponent.h"
#include "OptionalMobileFeaturesBPLibrary.h"

UDeviceMonitorComponent::UDeviceMonitorComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UDeviceMonitorComponent::BeginPlay()
{
    Super::BeginPlay();
    GetWorld()->GetTimerManager().SetTimer(
        MonitorTimerHandle, this,
        &UDeviceMonitorComponent::UpdateDeviceStatus,
        CheckInterval, true);
}

void UDeviceMonitorComponent::UpdateDeviceStatus()
{
    CurrentBatteryLevel = UOptionalMobileFeaturesBPLibrary::GetBatteryLevel();
    CurrentTemperature = UOptionalMobileFeaturesBPLibrary::GetBatteryTemperature();

    if (CurrentBatteryLevel <= 20)
    {
        OnLowBattery.Broadcast(CurrentBatteryLevel);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-07-19 | `574e8e6e` | Add a ShortName to modules that generated paths over the 200 chars limit and a few modules that were | 为路径过长的模块添加 ShortName，属于基础设施维护 |
| 2023-04-12 | `bd466cf2` | Updated modules to not dependency on itself. | 移除模块对自身的循环依赖，属于构建系统修复 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件批量更新，无具体说明 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的供应商链接更新为 HTTPS 协议 |
| 2021-02-11 | `9756461b` | Quick pass at some plugin category clean up | 插件分类信息清理 |

### 维护评价

⚠️ **该插件实质上已停止维护。**

- 自 2016 年 12 月创建以来，从未有过功能性更新
- 所有近期 commit 均为全局性基础设施调整（路径修复、依赖清理、链接更新），不涉及插件本身的功能改动
- `EnabledByDefault: false` 表明 Epic 将其视为可选/边缘功能
- 插件功能极为简单（仅 4 个函数），API 稳定但可能未适配最新平台 API 特性
- 没有对应的测试用例

**建议**：如果项目仅需基本的设备信息查询，该插件仍可使用；但对于生产项目，建议自行封装原生平台接口以获得更完善的控制和兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OptionalMobileFeaturesBPLibrary)
- [测试用例] 无