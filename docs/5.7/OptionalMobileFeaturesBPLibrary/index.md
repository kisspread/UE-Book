# Optional Mobile Features Blueprint Library

> Gives blueprint access to Sound Volume, Battery Charge Level, and System Temperature for Android and iOS devices

| 属性 | 值 |
|---|---|
| 分类 | Mobile |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | OptionalMobileFeaturesBPLibrary (Runtime) |
| 创建时间 | 2016-12-08 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OptionalMobileFeaturesBPLibrary) | |

## 用途

这个 plugin 是一个轻量级的蓝图函数库，将 Android 和 iOS 设备的硬件状态信息暴露给蓝图。它封装了平台原生 API，提供四个设备状态查询函数：音量、电量、电池温度和耳机插入状态。

在没有这个 plugin 的情况下，你需要编写 C++ 平台特定代码并手动绑定到蓝图。这个 plugin 提供了一个开箱即用的蓝图节点，省去了这些工作。

**注意**：该 plugin 默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你在做一个手机游戏，需要根据设备电量自动降低画质以延长续航
- 你需要在游戏中同步显示系统音量
- 你想检测耳机是否插入，以便切换音频输出方式
- 你需要监控设备温度，在过热时降低渲染质量

## 蓝图用法

所有节点都在 `Mobile` 分类下，均为静态函数，可直接拖入蓝图使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetVolumeState` | 返回设备当前音量，0-100（%） | `UOptionalMobileFeaturesBPLibrary` |
| `GetBatteryLevel` | 返回设备当前电量，0-100（%） | `UOptionalMobileFeaturesBPLibrary` |
| `GetBatteryTemperature` | 返回电池温度（摄氏度） | `UOptionalMobileFeaturesBPLibrary` |
| `AreHeadphonesPluggedIn` | 返回耳机是否已插入 | `UOptionalMobileFeaturesBPLibrary` |

### 使用示例（蓝图描述）

**低电量自动降低画质**：
1. 使用 `Event Tick` 或 `Timer` 周期性调用 `GetBatteryLevel`
2. 将返回值连接到 `Branch` 节点，判断是否低于阈值（如 20%）
3. 如果是，调用 `Scalability` 相关节点降低画质

**耳机检测自动切换音频**：
1. 使用 `Event Tick` 调用 `AreHeadphonesPluggedIn`
2. 根据返回值 `true/false` 切换音频输出路由

## C++ 用法

### 头文件引入

```cpp
#include "OptionalMobileFeaturesBPLibrary.h"
```

### 基本用法

所有函数都是 `static` 的，可以直接调用：

```cpp
// 获取当前音量（0-100）
int32 Volume = UOptionalMobileFeaturesBPLibrary::GetVolumeState();

// 获取电量（0-100）
int32 BatteryLevel = UOptionalMobileFeaturesBPLibrary::GetBatteryLevel();

// 获取电池温度（摄氏度），注意 iOS 不支持，始终返回 0.0f
float Temperature = UOptionalMobileFeaturesBPLibrary::GetBatteryTemperature();

// 检测耳机是否插入
bool bHeadphones = UOptionalMobileFeaturesBPLibrary::AreHeadphonesPluggedIn();
```

来源：`Source/OptionalMobileFeaturesBPLibrary/Classes/OptionalMobileFeaturesBPLibrary.h`、`Source/OptionalMobileFeaturesBPLibrary/Private/OptionalMobileFeaturesBPLibrary.cpp`

### 平台差异说明

- **Android**：所有函数均正常工作。音量从 Android 原生的 0-15 范围缩放到 0-100
- **iOS**：`GetBatteryTemperature` 不可用，始终返回 `0.0f`（Apple 无公开 API）
- **其他平台**（Editor / PC）：所有函数返回 `0` 或 `false`

## Demo 示例

### 电量监控组件

```cpp
// BatteryMonitor.h
#pragma once
#include "Components/ActorComponent.h"
#include "BatteryMonitor.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UBatteryMonitor : public UActorComponent
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Battery")
    float LowBatteryThreshold = 20.0f;

    UPROPERTY(BlueprintAssignable, Category="Battery")
    FSimpleDelegate OnLowBattery;

    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;
};
```

```cpp
// BatteryMonitor.cpp
#include "BatteryMonitor.h"
#include "OptionalMobileFeaturesBPLibrary.h"

void UBatteryMonitor::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    int32 Level = UOptionalMobileFeaturesBPLibrary::GetBatteryLevel();
    if (Level > 0 && Level <= LowBatteryThreshold)
    {
        OnLowBattery.Broadcast();
    }
}
```

Build.cs 依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "OptionalMobileFeaturesBPLibrary"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `ApplicationCore` | 平台抽象层（私有依赖，提供 FAndroidMisc / FIOSPlatformMisc） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2023-07-19 | `3686eae71ae1` | 添加 ShortName 以缩短构建路径长度 |
| 2023-04-12 | `bd466cf26ca6` | 移除模块对自身的循环依赖 |
| 2023-01-16 | `bbc37aa2f5e6` | IWYU 更新，减少头文件包含 |

三次更新均为构建系统维护，没有任何功能性改动。

### 维护评价

- **创建时间**：2016-12-08，已超过 9 年
- **最近实质性功能更新**：从未有过。所有 commit 都是构建系统/编译维护
- **维护状态**：⚠️ **可能废弃**。自创建以来从未增加新功能，最后的实质性代码改动在 2016 年
- **已知限制**：iOS 的 `GetBatteryTemperature` 始终返回 0；非移动平台所有函数返回默认值
- **是否推荐使用**：这个 plugin 功能极少且长期未更新，如果只需要这四个函数，直接在自己的项目中封装可能更好维护。但它仍然能正常工作，如果只是需要快速原型验证可以使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OptionalMobileFeaturesBPLibrary)
- [官方文档]()（无）
- [测试用例]()（无测试用例）
