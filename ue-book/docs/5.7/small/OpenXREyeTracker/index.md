# OpenXREyeTracker

> OpenXR Eye Tracker provides XR_EXT_eye_gaze_interaction support.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Reality |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | OpenXREyeTracker (Runtime, LoadingPhase: PostConfigInit) |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXREyeTracker) | |

## 用途

这个 plugin 为 UE5 的 Eye Tracking 系统提供 OpenXR 后端实现。它通过 OpenXR 的 `XR_EXT_eye_gaze_interaction` 扩展，将 VR/XR 头显的眼球追踪硬件接入到 Unreal 的统一 `IEyeTracker` 接口中。

简单来说：如果你的 VR 头显支持 OpenXR 眼球追踪（如 HTC VIVE Pro Eye、Meta Quest Pro 等），这个 plugin 就是让 UE5 能读取眼球注视数据的桥梁。它注册为 OpenXR 的扩展插件，在 XR Session 生命周期中管理 Eye Gaze Action Set，每帧同步并缓存眼球姿态数据，然后通过 `FEyeTrackerGazeData` 结构体暴露给游戏逻辑。

## 使用场景

- **VR 应用需要视线交互**：你在做 VR 体验，想让玩家通过"看"来选中物体（gaze-based interaction）
- **注视点渲染（Foveated Rendering）**：需要知道玩家在看哪里来优化渲染性能
- **用户行为分析**：记录玩家在 VR 场景中的注视热力图
- **辅助功能**：为无法使用手柄的用户提供视线控制方案
- **XR 研究/原型**：快速接入 OpenXR 眼球追踪数据进行实验

## 蓝图用法

OpenXREyeTracker plugin 本身不直接暴露蓝图节点。它通过 UE 内置的 `EyeTracker` 模块的蓝图函数库（`UEyeTrackerFunctionLibrary`）间接提供访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Gaze Data` | 获取统一的双眼融合注视射线数据（原点、方向、置信度） | `UEyeTrackerFunctionLibrary` |
| `Get Stereo Gaze Data` | 获取左右眼各自的注视射线数据（此 plugin 不支持，始终返回 false） | `UEyeTrackerFunctionLibrary` |
| `Is Eye Tracker Connected` | 检查眼球追踪硬件是否已连接并可用 | `UEyeTrackerFunctionLibrary` |
| `Is Stereo Gaze Data Available` | 检查设备是否支持逐眼数据（此 plugin 返回 false） | `UEyeTrackerFunctionLibrary` |
| `Set Eye Tracked Player` | 指定被追踪的玩家控制器 | `UEyeTrackerFunctionLibrary` |

### 使用示例（蓝图描述）

**获取注视点数据：**

1. 在任意 Blueprint 的 Event Tick 中，添加 `Get Gaze Data` 节点
2. 检查返回的布尔值（true = 数据有效）
3. 从 OutGazeData 中读取 `GazeOrigin`（射线起点）和 `GazeDirection`（射线方向）
4. 用 `Line Trace By Channel` 做射线检测，找到玩家正在看的物体

**检查设备状态：**

1. 在 BeginPlay 中调用 `Is Eye Tracker Connected`
2. 如果返回 false，可以禁用视线交互相关的 UI 提示

## C++ 用法

### 头文件引入

```cpp
#include "EyeTrackerFunctionLibrary.h"
#include "EyeTrackerTypes.h"
```

### 基本用法

通过 `UEyeTrackerFunctionLibrary` 的静态函数获取注视数据：

```cpp
// 检查眼球追踪器是否已连接
if (UEyeTrackerFunctionLibrary::IsEyeTrackerConnected())
{
    FEyeTrackerGazeData GazeData;
    if (UEyeTrackerFunctionLibrary::GetGazeData(GazeData))
    {
        // 有效的注视数据
        FVector RayOrigin = GazeData.GazeOrigin;
        FVector RayDirection = GazeData.GazeDirection;
        float Confidence = GazeData.ConfidenceValue;
        
        // 做射线检测
        FHitResult HitResult;
        FVector RayEnd = RayOrigin + RayDirection * 10000.0f;
        if (GetWorld()->LineTraceSingleByChannel(HitResult, RayOrigin, RayEnd, ECC_Visibility))
        {
            AActor* LookedAtActor = HitResult.GetActor();
            // 处理注视命中...
        }
    }
}
```

### 进阶用法

直接通过 `GEngine->EyeTrackingDevice` 访问底层接口，获取更详细的状态信息：

```cpp
if (GEngine && GEngine->EyeTrackingDevice.IsValid())
{
    const TSharedPtr<IEyeTracker>& EyeTracker = GEngine->EyeTrackingDevice;
    
    // 获取详细的追踪状态
    EEyeTrackerStatus Status = EyeTracker->GetEyeTrackerStatus();
    switch (Status)
    {
    case EEyeTrackerStatus::Tracking:
        // 正在追踪中
        break;
    case EEyeTrackerStatus::NotTracking:
        // 设备在线但未检测到眼睛
        break;
    case EEyeTrackerStatus::NotConnected:
        // 设备未连接
        break;
    }
    
    // 检查置信度，过滤低质量数据
    FEyeTrackerGazeData GazeData;
    if (EyeTracker->GetEyeTrackerGazeData(GazeData) && GazeData.ConfidenceValue > 0.5f)
    {
        // 高置信度的注视数据，可用于精确交互
    }
}
```

## Demo 示例

### 最小可用示例

一个简单的 Actor，检测玩家正在注视的物体并高亮显示。

**GazeInteractionActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EyeTrackerTypes.h"
#include "GazeInteractionActor.generated.h"

UCLASS()
class AGazeInteractionActor : public AActor
{
    GENERATED_BODY()

public:
    AGazeInteractionActor();

    virtual void Tick(float DeltaTime) override;

protected:
    virtual void BeginPlay() override;

    // 注视射线的最大距离
    UPROPERTY(EditAnywhere, Category = "Gaze")
    float TraceDistance = 10000.0f;

    // 当前注视命中的 Actor
    UPROPERTY(VisibleAnywhere, Category = "Gaze")
    AActor* CurrentGazeTarget = nullptr;

    // 上一帧注视的 Actor（用于检测注视进入/离开）
    AActor* PreviousGazeTarget = nullptr;
};
```

**GazeInteractionActor.cpp**

```cpp
#include "GazeInteractionActor.h"
#include "EyeTrackerFunctionLibrary.h"
#include "DrawDebugHelpers.h"

AGazeInteractionActor::AGazeInteractionActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AGazeInteractionActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 确认设备已连接
    if (!UEyeTrackerFunctionLibrary::IsEyeTrackerConnected())
    {
        UE_LOG(LogTemp, Warning, TEXT("Eye tracker not connected!"));
    }
}

void AGazeInteractionActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    PreviousGazeTarget = CurrentGazeTarget;
    CurrentGazeTarget = nullptr;

    FEyeTrackerGazeData GazeData;
    if (UEyeTrackerFunctionLibrary::GetGazeData(GazeData))
    {
        FVector RayEnd = GazeData.GazeOrigin + GazeData.GazeDirection * TraceDistance;
        FHitResult HitResult;
        
        if (GetWorld()->LineTraceSingleByChannel(
            HitResult, GazeData.GazeOrigin, RayEnd, ECC_Visibility))
        {
            CurrentGazeTarget = HitResult.GetActor();
            
            // 调试：绘制注视射线
            DrawDebugLine(GetWorld(), GazeData.GazeOrigin, HitResult.ImpactPoint,
                FColor::Green, false, -1.0f, 0, 1.0f);
        }
    }
}
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "EyeTracker"   // 使用 Eye Tracking 蓝图/函数库
});
```

## 模块依赖

从 `OpenXREyeTracker.Build.cs` 提取。如果你的项目只是通过蓝图函数库使用 Eye Tracking，你不需要直接依赖这些模块——只需启用此 plugin 并依赖 `EyeTracker` 模块即可。

| 模块 | 用途 |
|---|---|
| `EyeTracker` | 公共依赖，提供 `IEyeTracker` 接口和蓝图函数库 |
| `Core` | UE 核心模块 |
| `CoreUObject` | UObject 系统 |
| `ApplicationCore` | 应用程序核心功能 |
| `Engine` | 引擎核心 |
| `InputDevice` | 输入设备抽象层 |
| `InputCore` | 输入核心类型 |
| `HeadMountedDisplay` | HMD 抽象层 |
| `OpenXRHMD` | OpenXR HMD 实现 |
| `OpenXRInput` | OpenXR 输入系统 |
| `XRBase` | XR 基础模块 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-23 | `000fbe45cd22` | OpenXR 现在支持所有平台构建。之前 OpenXR 插件的平台限制导致跨平台项目无法在非 XR 平台上加载相关内容。现在 plugin 默认仍禁用，但不再有平台限制。 |
| 2025-07-21 | `82674f19240b` | 将 OpenXR 扩展名称改为使用 openxr.h 中的宏定义，而不是硬编码字符串。代码质量改进。 |
| 2025-06-19 | `6e6685c775a4` | 为 OpenXR 插件添加 LinuxArm64 平台支持。注意：这不提供 linuxarm64 的 OpenXR loader，需要通过自定义 loader 功能来暴露。 |

### 维护评价

- **创建时间**：2020 年 9 月，已有约 5.6 年历史
- **最近更新**：2025 年 9 月，最近 6 个月内有更新（主要是平台兼容性改进，非功能性更新）
- **维护状态**：**维护中** — 虽然近期更新主要是平台适配和代码规范化，但说明 Epic 仍在维护此 plugin
- **已知限制**：
  - `EnabledByDefault: false` — 需要手动在项目设置中启用
  - 不支持立体双眼数据（`GetStereoGazeData` 始终返回 false）
  - 不支持注视点（`FixationPoint` 始终为零向量）
  - 不支持瞳孔直径和眨眼检测（这些字段在返回的 `GazeData` 中始终为默认值）
  - 存在 HTC VIVE eye tracking API layer 版本兼容性检查（版本 ≤1 时禁用扩展以避免崩溃）
- **推荐程度**：如果你的 VR 项目需要通过 OpenXR 接入眼球追踪，这是唯一的官方实现，推荐使用。注意它只提供合并的注视射线，不支持逐眼数据。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXREyeTracker)
- [EyeTracker 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/EyeTracker)
- [OpenXR Eye Gaze Interaction 扩展规范](https://www.khronos.org/registry/OpenXR/specs/1.0/html/xrspec.html#XR_EXT_eye_gaze_interaction)
