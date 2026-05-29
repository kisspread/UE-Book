# OpenXREyeTracker

> OpenXR Eye Tracker provides XR_EXT_eye_gaze_interaction support.

| 属性 | 值 |
|---|---|
| 中文名 | OpenXR 眼动追踪 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OpenXREyeTracker` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXREyeTracker) | |

## 用途

此插件为 UE5 的通用眼动追踪系统（`EyeTracker` 模块）提供了基于 OpenXR 的具体实现。它通过集成 `XR_EXT_eye_gaze_interaction` 扩展，将支持该扩展的 VR/XR 头显的原始眼动数据，转化为 UE 标准的 `IEyeTracker` 接口数据。开发者可以通过引擎内置的眼动追踪 API（如 `GEngine->XRSystem->GetEyeTracker()`）访问这些数据，而无需关心底层 OpenXR 扩展的细节。

## 使用场景

- 你在开发一个支持眼神交互的 VR 应用，需要获取用户的注视点数据。
- 你希望利用眼动追踪数据优化注视点渲染（Foveated Rendering）以提升性能。
- 你需要在 VR 体验中实现基于注视的交互或研究用户注意力分布。

## 蓝图用法

此插件的核心功能通过 `IEyeTracker` 接口暴露给引擎。通常在蓝图中，你不会直接调用插件自身的函数，而是通过引擎提供的通用眼动追踪节点来访问数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Eye Tracker Gaze Data` | 获取单合一的眼动追踪数据（注视方向与原点）。 | `UEyeTrackerFunctionLibrary` |
| `Get Eye Tracker Stereo Gaze Data` | 获取分离的双眼注视数据（如果支持）。 | `UEyeTrackerFunctionLibrary` |
| `Get Eye Tracker Status` | 获取眼动追踪器的连接状态（未连接/追踪中/校准中等）。 | `UEyeTrackerFunctionLibrary` |

### 使用示例（蓝图描述）

在蓝图中，你可以使用 `Eye Tracker` 分类下的节点：
1.  使用 `Get Eye Tracker Status` 节点检查设备是否可用并正在追踪。
2.  使用 `Get Eye Tracker Gaze Data` 节点获取一个 `FEyeTrackerGazeData` 结构体。
3.  从该结构体中提取 `GazeDirection`（世界空间下的注视方向）和 `GazeOrigin`（双眼之间的估计原点），用于射线检测或确定用户正在看什么物体。

## C++ 用法

### 头文件引入

```cpp
#include “EyeTrackerTypes.h” // 用于 FEyeTrackerGazeData 等数据结构
#include “EyeTrackerModule.h” // 用于访问 IEyeTracker 和 IEyeTrackerModule
```

### 基本用法

通过引擎的 XR 系统获取眼动追踪器实例并查询数据。
（来源：引擎通用眼动追踪使用模式）

```cpp
// 获取眼动追踪器模块
if (IEyeTrackerModule* EyeTrackerModule = IEyeTrackerModule::GetModule())
{
    // 创建或获取追踪器实例
    TSharedPtr<IEyeTracker> EyeTracker = EyeTrackerModule->CreateEyeTracker();
    
    if (EyeTracker.IsValid())
    {
        FEyeTrackerGazeData GazeData;
        // 查询最新的注视数据
        if (EyeTracker->GetEyeTrackerGazeData(GazeData))
        {
            // 使用 GazeData.GazeDirection 和 GazeData.GazeOrigin
            FVector GazeDirection = GazeData.GazeDirection;
            FVector GazeOrigin = GazeData.GazeOrigin;
            // 执行射线检测等操作
        }
        
        // 查询状态
        EEyeTrackerStatus Status = EyeTracker->GetEyeTrackerStatus();
        if (Status == EEyeTrackerStatus::Tracking)
        {
            // 设备正在追踪中
        }
    }
}
```

### 进阶用法

结合 OpenXR 扩展的生命周期进行更细粒度的控制。
（来源：IOpenXRExtensionPlugin 接口）

```cpp
// 插件本身作为 OpenXR 扩展被管理。
// 对于普通应用开发者，通常不需要直接调用这些方法，
// 它们在 OpenXR 会话生命周期中被引擎自动调用。
// 但了解其流程有助于调试。

// 插件注册了 `XR_EXT_eye_gaze_interaction` 扩展 (GetRequiredExtensions)。
// 在 OpenXR 会话创建时，它会创建对应的眼动追踪动作 (EyeTrackerAction) 和空间。
// 在每一帧，它会同步动作集并更新空间位置，将数据缓存供 IEyeTracker 接口查询。
```

## Demo 示例

一个演示如何查询 OpenXR 眼动追踪数据的最小 Actor 类。
```cpp
// MyEyeTrackingActor.h
#pragma once
#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “EyeTrackerTypes.h”
#include “MyEyeTrackingActor.generated.h”

UCLASS()
class MYPROJECT_API AMyEyeTrackingActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyEyeTrackingActor();

protected:
    virtual void Tick(float DeltaTime) override;
    
    // 用于在编辑器中显示当前注视点
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “EyeTracking”)
    FVector CurrentGazeOrigin;
    
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “EyeTracking”)
    FVector CurrentGazeDirection;
    
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “EyeTracking”)
    EEyeTrackerStatus CurrentStatus;
};
```

```cpp
// MyEyeTrackingActor.cpp
#include “MyEyeTrackingActor.h”
#include “EyeTrackerModule.h”
#include “Engine/Engine.h”

AMyEyeTrackingActor::AMyEyeTrackingActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyEyeTrackingActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    if (IEyeTrackerModule* EyeTrackerModule = IEyeTrackerModule::GetModule())
    {
        TSharedPtr<IEyeTracker> EyeTracker = EyeTrackerModule->CreateEyeTracker();
        if (EyeTracker.IsValid())
        {
            CurrentStatus = EyeTracker->GetEyeTrackerStatus();
            
            FEyeTrackerGazeData GazeData;
            if (EyeTracker->GetEyeTrackerGazeData(GazeData))
            {
                CurrentGazeOrigin = GazeData.GazeOrigin;
                CurrentGazeDirection = GazeData.GazeDirection;
                
                // 示例：打印到屏幕
                if (GEngine)
                {
                    GEngine->AddOnScreenDebugMessage(-1, 0.f, FColor::Yellow,
                        FString::Printf(TEXT(“Gaze Direction: %s”), *CurrentGazeDirection.ToString()));
                }
            }
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EyeTracker` | UE 引擎的核心眼动追踪接口和类型定义。 |
| `UnrealEd` | 提供 `IOpenXREyeTrackerModule` 所继承的编辑器/工具相关接口，以及用于调试显示。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-16 | `308ebb2b` | OpenXR now building for all platforms. | 使 OpenXR 插件能在所有平台编译，包括此插件。 |
| 2025-07-21 | `82674f19` | OpenXR extension names: use openxr.h define rather than hard coding the names. | 重构代码，使用 openxr.h 中的宏定义扩展名称，避免硬编码。 |
| 2025-06-19 | `6e6685c7` | Enabling LinuxArm64 support for OpenXR | 为 OpenXR 及其子插件（包括此插件）添加 LinuxArm64 平台支持。 |
| 2025-06-17 | `c938772e` | [Backout] - CL43548023 | 回退了之前的某次提交（与 LinuxArm64 支持相关）。 |
| 2025-06-16 | `5e391eec` | Enabling LinuxArm64 support for OpenXR | 启用 LinuxArm64 支持（后被回退）。 |

### 维护评价

- **维护状态**：**活跃维护中**。插件作为 OpenXR 生态系统的一部分，仍在持续更新以支持新平台（如 LinuxArm64）和进行代码质量改进。
- **注意事项**：该插件**默认未启用**，需要在项目设置中手动启用，并确保底层 OpenXR 运行时和头显驱动支持 `XR_EXT_eye_gaze_interaction` 扩展。
- **推荐**：**推荐使用**。对于需要在 Unreal Engine 项目中通过 OpenXR 标准获取眼动追踪数据的开发者，这是官方的、持续维护的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXREyeTracker)
- [官方文档](https://docs.unrealengine.com) (OpenXR 眼动追踪部分通常整合在引擎通用眼动追踪文档中)