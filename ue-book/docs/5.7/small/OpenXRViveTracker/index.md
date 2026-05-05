# OpenXRViveTracker

> OpenXR Vive Tracker provides XR_HTCX_vive_tracker_interaction.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Reality |
| 默认启用 | ❌ `EnabledByDefault: false`（需手动启用） |
| 包含内容 | ✅ `CanContainContent: true` |
| 模块 | `OpenXRViveTracker` (Runtime, LoadingPhase: PostConfigInit) |
| 创建时间 | 2022-11-07 |
| 年龄标签 | 🆕（~3.5 年） |
| 实验性 | ⚠️ `IsBetaVersion: true` |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXRViveTracker) | |

## 用途

这个 plugin 为 UE5 的 OpenXR 运行时添加了 **HTC Vive Tracker** 的追踪支持。它实现了 OpenXR 扩展 `XR_HTCX_vive_tracker_interaction`，让 UE5 能够读取 Vive Tracker（全身追踪器）的位置和旋转数据，并将其作为标准的 Motion Controller 输入设备暴露给引擎。

Vive Tracker 是 HTC 的外部追踪设备，通常用于全身动捕（Full Body Tracking）、道具追踪、外设追踪等场景。这个 plugin 将 Tracker 的物理位置映射为 UE5 的 `EControllerHand` 枚举值，使得蓝图和 C++ 代码可以通过统一的 Motion Controller 接口访问追踪数据。

### 核心机制

- 实现 `IOpenXRExtensionPlugin` 接口，作为 OpenXR 扩展注册
- 实现 `IMotionController` 接口，作为标准运动控制器输入设备
- 实现 `IHapticDevice` 接口，支持对 Tracker 发送触觉反馈（振动）
- 自动枚举并注册所有已连接的 Vive Tracker
- 为未分配角色的 Tracker 也创建追踪条目（通过 persistent path）

## 使用场景

- **全身动捕游戏**：将 Vive Tracker 绑定在腰部、膝盖、脚部，用于全身姿态追踪
- **VR 外设追踪**：追踪真实世界的道具（如枪械模型、相机等），映射到 VR 中的虚拟物体
- **混合现实（MR）**：将 Tracker 装在外部摄像头上，精确追踪现实摄像机位置
- **多人 VR 体验**：追踪多个用户的物理位置
- **体育/健身 VR 应用**：追踪肘部、肩膀等关节用于运动分析

## 支持的 Tracker 角色

Plugin 在创建 session 时注册以下 13 个标准 Tracker 角色：

| Motion Source 名称 | EControllerHand | OpenXR Role Path |
|---|---|---|
| `Pad` | Pad | `/user/vive_tracker_htcx/role/keyboard` |
| `ExternalCamera` | ExternalCamera | `/user/vive_tracker_htcx/role/camera` |
| `Gun` | Gun | `/user/vive_tracker_htcx/role/handheld_object` |
| `Chest` | Chest | `/user/vive_tracker_htcx/role/chest` |
| `LeftShoulder` | LeftShoulder | `/user/vive_tracker_htcx/role/left_shoulder` |
| `RightShoulder` | RightShoulder | `/user/vive_tracker_htcx/role/right_shoulder` |
| `LeftElbow` | LeftElbow | `/user/vive_tracker_htcx/role/left_elbow` |
| `RightElbow` | RightElbow | `/user/vive_tracker_htcx/role/right_elbow` |
| `Waist` | Waist | `/user/vive_tracker_htcx/role/waist` |
| `LeftKnee` | LeftKnee | `/user/vive_tracker_htcx/role/left_knee` |
| `RightKnee` | RightKnee | `/user/vive_tracker_htcx/role/right_knee` |
| `LeftFoot` | LeftFoot | `/user/vive_tracker_htcx/role/left_foot` |
| `RightFoot` | RightFoot | `/user/vive_tracker_htcx/role/right_foot` |

此外，未分配角色的 Tracker 会以 `persistent path` 的形式自动注册为 `UnassignedTrackers`。

## 蓝图用法

这个 plugin **没有暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性**。它的所有功能都是通过引擎内置的 Motion Controller 接口自动运行的。

### 通过标准蓝图节点访问 Tracker 数据

在蓝图中使用标准的 Motion Controller 节点即可获取 Vive Tracker 数据：

1. **获取 Tracker 位置和旋转**：
   - 使用 `Get Motion Controller Data` 节点
   - 将 `Motion Source` 设置为上表中的名称（如 `Waist`、`LeftFoot` 等）
   - `Hand` 参数设为对应的 `EControllerHand` 值

2. **检测 Tracker 连接状态**：
   - 使用 `Get Motion Controller Tracking Status` 节点
   - 返回 `Tracked` 或 `NotTracked`

3. **发送触觉反馈**：
   - 使用标准的 Haptic Feedback 节点
   - Tracker 支持频率和振幅控制

### 使用示例（蓝图描述）

```
[Event Tick] → [Get Motion Controller Data]
                  Motion Source: "Waist"
                  → 输出 Orientation, Position
                  → 连接到场景中一个 Scene Component 的 Set World Location And Rotation
```

要获取全身追踪，可以创建 6 个 Get Motion Controller Data 调用，分别使用 `Waist`、`LeftFoot`、`RightFoot`、`LeftKnee`、`RightKnee`、`Chest` 作为 Motion Source。

## C++ 用法

### 头文件引入

```cpp
#include "IOpenXRViveTrackerModule.h"
#include "HeadMountedDisplayFunctionLibrary.h"
```

### 检查模块是否可用

```cpp
if (IOpenXRViveTrackerModule::IsAvailable())
{
    IOpenXRViveTrackerModule& ViveTrackerModule = IOpenXRViveTrackerModule::Get();
    TSharedPtr<IInputDevice> InputDevice = ViveTrackerModule.GetInputDevice();
}
```

### 通过 Motion Controller 接口获取 Tracker 位置

```cpp
// 获取 Vive Tracker 的位置和旋转
// MotionSource 对应角色名，如 "Waist"、"LeftFoot" 等
int32 ControllerIndex = 0;  // Tracker 使用的 DeviceIndex
FName MotionSource = FName(TEXT("Waist"));
FRotator Orientation;
FVector Position;
float WorldToMetersScale = 100.0f;

if (UHeadMountedDisplayFunctionLibrary::GetControllerOrientationAndPosition(
        ControllerIndex, MotionSource, Orientation, Position))
{
    // 使用 Orientation 和 Position
    UE_LOG(LogTemp, Log, TEXT("Waist Tracker Position: %s"), *Position.ToString());
}
```

### 获取带速度信息的 Tracker 数据

```cpp
FRotator Orientation;
FVector Position;
bool bHasLinearVelocity, bHasAngularVelocity, bHasLinearAcceleration;
FVector LinearVelocity, AngularVelocity, LinearAcceleration;
float WorldToMetersScale = 100.0f;
FTimespan Time;  // 默认 0 表示最新数据
bool bTimeWasUsed = false;

UHeadMountedDisplayFunctionLibrary::GetControllerOrientationAndPositionForTime(
    ControllerIndex, MotionSource, Time, bTimeWasUsed,
    Orientation, Position,
    bHasLinearVelocity, LinearVelocity,
    bHasAngularVelocity, AngularVelocity,
    bHasLinearAcceleration, LinearAcceleration,
    WorldToMetersScale);
```

### 检查追踪状态

```cpp
ETrackingStatus Status = UHeadMountedDisplayFunctionLibrary::GetControllerTrackingStatus(
    ControllerIndex, MotionSource);

if (Status == ETrackingStatus::Tracked)
{
    // Tracker 正在被追踪
}
```

## Demo 示例

### 全身追踪 Actor

以下是一个最小的全身追踪示例 Actor，将 6 个 Vive Tracker 的位置应用到骨骼网格体的骨骼上。

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "HeadMountedDisplay",
    "InputDevice"
});
```

**FullBodyTrackerActor.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FullBodyTrackerActor.generated.h"

UCLASS()
class AFullBodyTrackerActor : public AActor
{
    GENERATED_BODY()

public:
    AFullBodyTrackerActor();

    virtual void Tick(float DeltaTime) override;

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USceneComponent> Waist;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USceneComponent> LeftFoot;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USceneComponent> RightFoot;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USceneComponent> LeftKnee;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USceneComponent> RightKnee;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USceneComponent> Chest;

private:
    void UpdateTrackerComponent(USceneComponent* Component, const FName& MotionSource);
};
```

**FullBodyTrackerActor.cpp**：

```cpp
#include "FullBodyTrackerActor.h"
#include "HeadMountedDisplayFunctionLibrary.h"

AFullBodyTrackerActor::AFullBodyTrackerActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建各身体部位的 Scene Component
    Waist = CreateDefaultSubobject<USceneComponent>(TEXT("Waist"));
    SetRootComponent(Waist);

    LeftFoot = CreateDefaultSubobject<USceneComponent>(TEXT("LeftFoot"));
    LeftFoot->SetupAttachment(RootComponent);

    RightFoot = CreateDefaultSubobject<USceneComponent>(TEXT("RightFoot"));
    RightFoot->SetupAttachment(RootComponent);

    LeftKnee = CreateDefaultSubobject<USceneComponent>(TEXT("LeftKnee"));
    LeftKnee->SetupAttachment(RootComponent);

    RightKnee = CreateDefaultSubobject<USceneComponent>(TEXT("RightKnee"));
    RightKnee->SetupAttachment(RootComponent);

    Chest = CreateDefaultSubobject<USceneComponent>(TEXT("Chest"));
    Chest->SetupAttachment(RootComponent);
}

void AFullBodyTrackerActor::BeginPlay()
{
    Super::BeginPlay();
}

void AFullBodyTrackerActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    UpdateTrackerComponent(Waist, FName(TEXT("Waist")));
    UpdateTrackerComponent(LeftFoot, FName(TEXT("LeftFoot")));
    UpdateTrackerComponent(RightFoot, FName(TEXT("RightFoot")));
    UpdateTrackerComponent(LeftKnee, FName(TEXT("LeftKnee")));
    UpdateTrackerComponent(RightKnee, FName(TEXT("RightKnee")));
    UpdateTrackerComponent(Chest, FName(TEXT("Chest")));
}

void AFullBodyTrackerActor::UpdateTrackerComponent(USceneComponent* Component, const FName& MotionSource)
{
    FRotator Orientation;
    FVector Position;

    if (UHeadMountedDisplayFunctionLibrary::GetControllerOrientationAndPosition(
            0, MotionSource, Orientation, Position))
    {
        Component->SetWorldLocationAndRotation(Position, Orientation);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InputDevice` | 输入设备框架（PublicDependency） |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `HeadMountedDisplay` | HMD/VR 抽象层，Motion Controller 接口 |
| `XRBase` | XR 基础设施 |
| `InputCore` | 输入系统核心类型（EControllerHand 等） |
| `OpenXRHMD` | OpenXR HMD 实现，提供 IOpenXRHMD 接口 |
| `OpenXRInput` | OpenXR 输入系统 |
| `Slate` / `SlateCore` | UI 框架（用于 Application Message Handler） |
| `ApplicationCore` | 应用程序核心 |

### 插件依赖

| 插件 | 说明 |
|---|---|
| `OpenXR` | 必须启用，提供 OpenXR 运行时 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-03-13 | `b059f7b` | Fix trivial unreachable code warnings | 编译警告修复，无功能变更 |
| 2025-01-28 | `22b7270` | FPlatformString/FCString deprecation: Strcpy/Strcat/Strncat API 变更 | 适配引擎底层字符串 API 的弃用变更，将 `Strncpy`/`Strncat` 调用迁移到新 API |
| 2024-01-12 | `56a32fe` | Silence false V621, V654, and V1078 warnings | 静态分析工具（PVS-Studio）警告抑制，无功能变更 |

### 维护评价

- **年龄**：~3.5 年，属于较新的 plugin
- **维护状态**：**维护不活跃**。最近 3 次提交全部是编译器警告修复和 API 迁移，没有任何功能性更新。自 2022 年创建以来，核心功能从未修改过。
- **实验性标记**：`IsBetaVersion: true`，`EnabledByDefault: false`——Epic 将此 plugin 标记为实验性质，尚未正式支持。
- **代码质量**：代码结构清晰，但存在一些 TODO 注释（如 `// TODO: Refactor API to change the Hand type to EControllerHand`），说明 API 设计尚不完善。
- **平台支持**：Win64、Linux、Android
- **是否推荐使用**：如果你的项目依赖 HTC Vive Tracker 的全身追踪功能，这是唯一的选择（UE5 内置方案）。但需注意它是实验性 plugin，且上游 OpenXR 的 `XR_HTCX_vive_tracker_interaction` 扩展本身也处于草案阶段。建议在使用前充分测试，并准备好备用方案。

⚠️ **警告**：此 plugin 自创建以来没有实质性功能更新（超过 3 年），核心追踪逻辑未发生任何变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXRViveTracker)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）
- [OpenXR XR_HTCX_vive_tracker_interaction 扩展规范](https://www.khronos.org/registry/OpenXR/specs/1.0/html/xrspec.html#XR_HTCX_vive_tracker_interaction)
