# Eye Tracker

> Eye Tracker provides a modular interface for eye tracking hardware, with OpenXR eye gaze interaction as the primary implementation.

| 属性 | 值 |
|---|---|
| 分类 | Runtime |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EyeTracker` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-05-10 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/EyeTracker) | |

## 用途

EyeTracker 是 UE5 的**眼动追踪抽象层**，它解决的核心问题是：为不同的眼动追踪硬件提供统一的接口。它本身不包含任何设备实现——而是定义了一套 `IEyeTracker` 接口和 `UEyeTrackerFunctionLibrary` 蓝图函数库，让具体的设备驱动（如 OpenXREyeTracker）通过 UE 的 Modular Feature 系统注册自己。

引擎通过 `GEngine->EyeTrackingDevice` 持有一个全局的 `IEyeTracker` 指针，蓝图函数库直接访问它来提供眼动数据。

这个系统的设计思路与 HMD（头戴显示器）系统类似：核心模块定义接口，插件提供实现，运行时按优先级选择最佳实现。

## 相关插件：OpenXR Eye Tracker

实际的 OpenXR 实现位于独立插件 `Engine/Plugins/Runtime/OpenXREyeTracker/`：

| 属性 | 值 |
|---|---|
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 模块 | `OpenXREyeTracker` (Runtime) |
| 依赖插件 | XRBase, OpenXR |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXREyeTracker) | |

该插件实现了 `XR_EXT_eye_gaze_interaction` 扩展，将 OpenXR 的眼动姿态数据转换为 UE5 的 `FEyeTrackerGazeData` 格式。

## 使用场景

- 你在做 VR 应用，需要检测用户正在看哪里 → 使用 EyeTracker 模块
- 你需要实现基于视线的交互（如 UI 选择、注意力分析） → 使用 EyeTracker
- 你有支持 OpenXR 眼动追踪扩展的 VR 头显 → 启用 OpenXREyeTracker 插件
- 你在做无障碍/辅助功能，需要替代传统输入 → EyeTracker 提供眨眼和瞳孔数据
- 你需要自定义眼动追踪硬件支持 → 实现 `IEyeTracker` 接口并注册为 Modular Feature

## 蓝图用法

EyeTracker 通过 `UEyeTrackerFunctionLibrary` 提供蓝图节点，所有节点都在 **Eye Tracking** 分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsEyeTrackerConnected` | 检查眼动追踪硬件是否已连接并就绪 | `UEyeTrackerFunctionLibrary` |
| `IsStereoGazeDataAvailable` | 检查当前设备是否支持逐眼注视数据 | `UEyeTrackerFunctionLibrary` |
| `GetGazeData` | 获取统一的注视数据（融合双眼的单一射线） | `UEyeTrackerFunctionLibrary` |
| `GetStereoGazeData` | 获取立体注视数据（左右眼各自的射线） | `UEyeTrackerFunctionLibrary` |
| `SetEyeTrackedPlayer` | 指定被追踪的玩家控制器（某些设备需要） | `UEyeTrackerFunctionLibrary` |

### 数据结构

**FEyeTrackerGazeData**（统一注视数据）：

| 属性 | 类型 | 说明 |
|---|---|---|
| `GazeOrigin` | `FVector` | 统一注视射线的起点 |
| `GazeDirection` | `FVector` | 统一注视射线的前方方向 |
| `FixationPoint` | `FVector` | 双眼汇聚点（用户正在看的 3D 位置） |
| `ConfidenceValue` | `float` | 置信度 [0..1]，稳定追踪时接近 1 |
| `bIsLeftEyeBlink` | `bool` | 左眼眨眼状态（true = 闭眼） |
| `bIsRightEyeBlink` | `bool` | 右眼眨眼状态（true = 闭眼） |
| `LeftPupilDiameter` | `float` | 左眼瞳孔直径 |
| `RightPupilDiameter` | `float` | 右眼瞳孔直径 |

**FEyeTrackerStereoGazeData**（立体注视数据）：

| 属性 | 类型 | 说明 |
|---|---|---|
| `LeftEyeOrigin` | `FVector` | 左眼注视射线起点 |
| `LeftEyeDirection` | `FVector` | 左眼注视射线方向 |
| `RightEyeOrigin` | `FVector` | 右眼注视射线起点 |
| `RightEyeDirection` | `FVector` | 右眼注视射线方向 |
| `FixationPoint` | `FVector` | 双眼汇聚点 |
| `ConfidenceValue` | `float` | 置信度 [0..1] |

**EEyeTrackerStatus**（设备状态枚举）：

| 值 | 说明 |
|---|---|
| `NotConnected` | 眼动追踪设备未连接 |
| `NotTracking` | 设备已连接但未在追踪眼睛 |
| `Tracking` | 设备正在追踪眼睛 |

### 使用示例（蓝图描述）

**基本视线检测**：

1. 在 Tick 事件中，拖出引线搜索 `Get Gaze Data`
2. 将返回值连接到 Branch 节点（bool）
3. 如果为 true，使用 `OutGazeData` 的 `GazeOrigin` + `GazeDirection` 做射线检测（Line Trace）
4. 检测命中的 Actor 即为用户正在看的物体

**眨眼检测**：

1. 调用 `Get Gaze Data` 获取 `FEyeTrackerGazeData`
2. 检查 `bIsLeftEyeBlink` 和 `bIsRightEyeBlink`
3. 可用于触发"眨眼选择"交互

## C++ 用法

### 头文件引入

```cpp
#include "EyeTrackerFunctionLibrary.h"
#include "EyeTrackerTypes.h"
#include "IEyeTracker.h"
```

### 基本用法

通过蓝图函数库的静态方法获取眼动数据：

```cpp
// 检查设备连接状态
bool bConnected = UEyeTrackerFunctionLibrary::IsEyeTrackerConnected();

// 获取统一注视数据
FEyeTrackerGazeData GazeData;
if (UEyeTrackerFunctionLibrary::GetGazeData(GazeData))
{
    // GazeData.GazeOrigin     - 注视射线起点（世界空间）
    // GazeData.GazeDirection   - 注视射线方向（世界空间）
    // GazeData.FixationPoint   - 双眼汇聚点
    // GazeData.ConfidenceValue - 置信度 0-1
    // GazeData.bIsLeftEyeBlink - 左眼是否闭合
    
    FVector TraceEnd = GazeData.GazeOrigin + GazeData.GazeDirection * 10000.0f;
    // 用于射线检测...
}
```

### 进阶用法

直接访问引擎的 EyeTrackingDevice 指针（绕过蓝图函数库）：

```cpp
#include "Engine/Engine.h"
#include "IEyeTracker.h"

// 直接获取设备接口
if (GEngine && GEngine->EyeTrackingDevice.IsValid())
{
    IEyeTracker* EyeTracker = GEngine->EyeTrackingDevice.Get();
    
    // 检查设备状态
    EEyeTrackerStatus Status = EyeTracker->GetEyeTrackerStatus();
    if (Status == EEyeTrackerStatus::Tracking)
    {
        // 获取立体数据（需要设备支持）
        if (EyeTracker->IsStereoGazeDataAvailable())
        {
            FEyeTrackerStereoGazeData StereoData;
            if (EyeTracker->GetEyeTrackerStereoGazeData(StereoData))
            {
                // 分别访问左右眼数据
                FVector LeftGazeEnd = StereoData.LeftEyeOrigin + StereoData.LeftEyeDirection * 10000.0f;
                FVector RightGazeEnd = StereoData.RightEyeOrigin + StereoData.RightEyeDirection * 10000.0f;
            }
        }
        
        // 或者使用统一数据
        FEyeTrackerGazeData GazeData;
        EyeTracker->GetEyeTrackerGazeData(GazeData);
    }
    
    // 指定被追踪的玩家（某些设备需要）
    EyeTracker->SetEyeTrackedPlayer(GetWorld()->GetFirstPlayerController());
}
```

### 实现自定义眼动追踪设备

如果你有自定义的眼动追踪硬件，可以实现 `IEyeTracker` 接口：

```cpp
#include "IEyeTracker.h"
#include "IEyeTrackerModule.h"

// 实现眼动追踪器接口
class FMyCustomEyeTracker : public IEyeTracker
{
public:
    virtual void SetEyeTrackedPlayer(APlayerController* PlayerController) override
    {
        // 缓存 PlayerController 以获取视口信息
    }
    
    virtual bool GetEyeTrackerGazeData(FEyeTrackerGazeData& OutGazeData) const override
    {
        // 从你的硬件 SDK 获取数据，填充 OutGazeData
        // 返回 true 表示数据有效
        return false;
    }
    
    virtual bool GetEyeTrackerStereoGazeData(FEyeTrackerStereoGazeData& OutGazeData) const override
    {
        // 如果你的硬件支持逐眼数据，填充并返回 true
        return false;
    }
    
    virtual EEyeTrackerStatus GetEyeTrackerStatus() const override
    {
        return EEyeTrackerStatus::NotConnected;
    }
    
    virtual bool IsStereoGazeDataAvailable() const override
    {
        return false;
    }
};

// 实现模块接口，注册为 Modular Feature
class FMyEyeTrackerModule : public IEyeTrackerModule
{
public:
    virtual void StartupModule() override
    {
        IEyeTrackerModule::StartupModule(); // 注册 Modular Feature
        EyeTracker = MakeShared<FMyCustomEyeTracker, ESPMode::ThreadSafe>();
    }
    
    virtual FString GetModuleKeyName() const override
    {
        return TEXT("MyCustomEyeTracker");
    }
    
    virtual bool IsEyeTrackerConnected() const override
    {
        return EyeTracker.IsValid() && 
               EyeTracker->GetEyeTrackerStatus() != EEyeTrackerStatus::NotConnected;
    }
    
    virtual TSharedPtr<IEyeTracker, ESPMode::ThreadSafe> CreateEyeTracker() override
    {
        return EyeTracker;
    }
    
private:
    TSharedPtr<FMyCustomEyeTracker, ESPMode::ThreadSafe> EyeTracker;
};
```

注意：`GetModulePriority()` 从 `Engine.ini` 的 `[EyeTrackerPluginPriority]` 段读取优先级，数值越大优先级越高。引擎会选择优先级最高的模块作为 `GEngine->EyeTrackingDevice`。

## Demo 示例

完整的最小示例——在 Actor 中使用眼动追踪进行射线检测：

```cpp
// GazeInteractor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EyeTrackerTypes.h"
#include "GazeInteractor.generated.h"

UCLASS()
class AGazeInteractor : public AActor
{
    GENERATED_BODY()

public:
    AGazeInteractor();

protected:
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, Category = "Gaze")
    float TraceDistance = 10000.0f;

    UPROPERTY(VisibleAnywhere, Category = "Gaze|Debug")
    AActor* LookedAtActor = nullptr;
};
```

```cpp
// GazeInteractor.cpp
#include "GazeInteractor.h"
#include "EyeTrackerFunctionLibrary.h"
#include "DrawDebugHelpers.h"

AGazeInteractor::AGazeInteractor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AGazeInteractor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    FEyeTrackerGazeData GazeData;
    if (UEyeTrackerFunctionLibrary::GetGazeData(GazeData))
    {
        FVector Start = GazeData.GazeOrigin;
        FVector End = Start + GazeData.GazeDirection * TraceDistance;

        FHitResult Hit;
        FCollisionQueryParams Params;
        Params.AddIgnoredActor(this);

        if (GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params))
        {
            LookedAtActor = Hit.GetActor();
            DrawDebugSphere(GetWorld(), Hit.ImpactPoint, 5.0f, 8, FColor::Green);
        }
        else
        {
            LookedAtActor = nullptr;
        }
    }
}
```

Build.cs 依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "EyeTracker"
});
```

## 模块依赖

EyeTracker 核心模块的依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、字符串 |
| `CoreUObject` | UObject 系统、反射 |
| `Engine` | GEngine、APlayerController |
| `InputCore` | 输入类型定义 |

OpenXREyeTracker 插件额外依赖：

| 模块 | 用途 |
|---|---|
| `EyeTracker` | 核心眼动追踪接口 |
| `OpenXRHMD` | OpenXR 头显模块 |
| `OpenXRInput` | OpenXR 输入系统 |
| `XRBase` | XR 基础设施 |
| `HeadMountedDisplay` | HMD 抽象层 |

## 维护状态

### 近期更新

1. **e25d843** (2025-07-28) — `[EyeTracker] * Dll exported IEyeTrackerModule::GetModularFeatureName()`
   - 修复蓝图函数不显示的问题。原因与 EyeTrackerModule 被子类化、两个模块实例使用相同名称调用 RegisterModularFeature 有关。

2. **89df8c1** (2025-04-23) — `Used UnrealGame build target to find and convert all files to have dllstorage`
   - 批量修改 DLL 导出声明，从类型级改为方法/静态变量级。

3. **d5a5a35** (2023-02-20) — `Remove unnecessary Public and Private entries for the current module`
   - 清理 Build.cs 中不必要的 include path 条目。

### 维护评价

- **创建时间**：2018 年 5 月，约 8 年历史
- **最后功能性更新**：2025 年 7 月（DLL 导出修复），属于构建系统维护
- **维护状态**：**维护中** — 模块稳定，近年只有构建系统层面的修复，无功能性变更
- **已知限制**：
  - 核心模块只提供接口，不包含任何设备实现
  - OpenXR 实现不支持立体注视数据（`IsStereoGazeDataAvailable()` 始终返回 false）
  - OpenXR 实现不支持 `FixationPoint`（硬编码为零向量）
  - OpenXR 实现的 `SetEyeTrackedPlayer` 是空实现
- **推荐使用**：✅ 推荐 — 这是 UE5 眼动追踪的标准接口，虽然更新不多但架构稳定

## 相关链接

- [EyeTracker 核心模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/EyeTracker)
- [OpenXREyeTracker 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXREyeTracker)
- 测试用例：无独立测试文件
