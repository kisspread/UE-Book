# OpenXR Hand Tracking

> OpenXR Hand Tracking provides XR_EXT_hand_tracking support.

| 属性 | 值 |
|---|---|
| 中文名 | OpenXR 手部追踪 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OpenXRHandTracking` (Runtime), `OpenXRHandTrackingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRHandTracking) | |

## 用途

该插件实现了 OpenXR 的 `XR_EXT_hand_tracking` 扩展，让支持手部追踪的 XR 设备（如 Meta Quest、HTC Vive 等）能够以 26 个关节点（Keypoint）的精度追踪双手姿态。

核心能力包括：

- **关节点追踪**：每只手 26 个关节点（掌心、手腕、拇指/食指/中指/无名指/小指各自的指骨关节和指尖）的实时位置、旋转、半径和速度
- **输入设备集成**：作为 `IInputDevice` 和 `FXRMotionControllerBase` 注册到引擎输入系统，每个关节点都可以作为 Motion Source 使用
- **LiveLink 集成**：作为 `ILiveLinkSource` 将手部骨骼数据推送到 LiveLink，支持动画蓝图直接消费手部追踪数据
- **IHandTracker 接口**：实现引擎的通用手部追踪抽象接口，与 OculusXR 等其他手部追踪实现互操作

该插件**默认禁用**（`EnabledByDefault=false`），需要在项目设置中手动启用，并且依赖 OpenXR 和 LiveLink 插件。

## 使用场景

- 你在做 VR 应用，需要无控制器的徒手交互（Hand Tracking）→ 用此插件获取手部关节数据驱动抓取、指向等交互
- 你需要在 VR 中实时驱动骨骼网格体的手部动画 → 用此插件通过 LiveLink 推送手部骨骼姿态
- 你需要获取特定手指指尖的位置做精确交互（如虚拟键盘打字）→ 用 Motion Source 或 `GetKeypointState()` 获取 `EHandKeypoint::IndexTip` 等精确位置
- 你需要跨 XR 平台的通用手部追踪能力 → 通过 OpenXR 抽象层，一次接入支持多种设备

## 蓝图用法

### 项目设置

在 **项目设置 → Input → OpenXR Hand Tracking** 中可配置：

| 设置 | 说明 |
|---|---|
| `bUseMoreSpecificMotionSourceNames` | 默认 `false`。若为 `true`，Motion Source 名称格式变为 `HandTrackingLeftPalm`（避免与其他输入设备冲突） |
| `bSupportLegacyControllerMotionSources` | 默认 `true`。是否支持 `Left`/`Right` 传统 Motion Source 名称 |

### Motion Source 命名

每个关节点都有对应的 Motion Source 名称：

| 格式 | 示例 |
|---|---|
| 默认格式 | `LeftPalm`、`RightIndexTip`、`LeftThumbProximal` |
| 更具体格式（开启后） | `HandTrackingLeftPalm`、`HandTrackingRightIndexTip` |

这些名称可在 Enhanced Input 的 Mapping Context 或 Motion Controller 组件中直接使用。

### LiveLink 重定向资产

`UOpenXRHandTrackingLiveLinkRemapAsset`（蓝图可继承）用于将 OpenXR 的手部骨骼数据重定向到目标骨架：

| 属性 | 说明 |
|---|---|
| `bHasMetacarpals` | 目标骨架是否包含掌骨关节（默认 `true`） |
| `bRetargetRotationOnly` | 仅应用旋转，不应用位移（默认 `false`） |
| `SwizzleX/Y/Z/W` | 四元数轴重映射，用于适配不同朝向约定的骨架 |
| `HandTrackingBoneNameMap` | 骨骼名称映射表（TMap），将 OpenXR 的骨骼名映射到目标骨架骨骼名 |

### 使用示例（蓝图描述）

**方式一：通过 Enhanced Input 使用手部追踪**

1. 启用 OpenXRHandTracking 插件
2. 在 Enhanced Input Mapping Context 中添加新的 Mapping
3. 将 Action 的 Motion Source 设置为 `LeftPalm` 或 `RightIndexTip` 等
4. 当手部被追踪时，输入值自动反映手部位置/旋转

**方式二：通过 LiveLink 使用手部骨骼**

1. 启用插件后，LiveLink 源列表中自动出现 `OpenXR Hand Tracking Left/Right`
2. 在动画蓝图中使用 LiveLink 节点连接对应的主题
3. 创建 `UOpenXRHandTrackingLiveLinkRemapAsset` 蓝图子类，配置骨骼名称映射
4. 在 LiveLink 组件上设置该 Retarget Asset

## C++ 用法

### 头文件引入

```cpp
#include "IOpenXRHandTrackingModule.h"        // 模块接口
#include "IHandTracker.h"                     // 手部追踪抽象接口
#include "IOpenXRExtensionPlugin.h"           // OpenXR 扩展接口（仅开发扩展时需要）
#include "OpenXRHandTrackingSettings.h"       // 设置访问
#include "OpenXRHandTrackingLiveLinkRemapAsset.h"  // LiveLink 重定向资产
```

### 基本用法：通过 IHandTracker 获取手部关节数据

`IHandTracker` 是引擎标准的手部追踪抽象接口，不直接依赖 OpenXR 细节。

```cpp
#include "IHandTracker.h"

void AMyActor::ReadHandTracking()
{
    // IHandTracker 是引擎全局单例
    IHandTracker& HandTracker = IHandTracker::Get();

    if (!HandTracker.IsHandTrackingStateValid())
    {
        return; // 手部追踪不可用
    }

    // 获取单个关节
    FTransform PalmTransform;
    float PalmRadius;
    if (HandTracker.GetKeypointState(EControllerHand::Left, EHandKeypoint::Palm, PalmTransform, PalmRadius))
    {
        FVector PalmLocation = PalmTransform.GetLocation();
        FRotator PalmRotation = PalmTransform.GetRotation().Rotator();
        // 使用掌心位置和旋转...
    }

    // 获取所有关节（适合驱动骨骼网格体）
    TArray<FVector> Positions;
    TArray<FQuat> Rotations;
    TArray<float> Radii;
    bool bIsTracked = false;
    if (HandTracker.GetAllKeypointStates(EControllerHand::Right, Positions, Rotations, Radii, bIsTracked))
    {
        for (int32 i = 0; i < Positions.Num(); ++i)
        {
            EHandKeypoint Keypoint = static_cast<EHandKeypoint>(i);
            // Keypoint 0 = Palm, 1 = Wrist, 2-5 = Thumb joints, ...
            // Positions[i] 是该关节在世界空间的位置
        }
    }
}
```

### 基本用法：通过 Motion Source 接口获取手部数据

```cpp
#include "IOpenXRHandTrackingModule.h"
#include "IXRTrackingSystem.h"

void AMyActor::GetHandMotionSourceData()
{
    if (!IOpenXRHandTrackingModule::IsAvailable())
    {
        return;
    }

    auto& Module = IOpenXRHandTrackingModule::Get();
    TSharedPtr<IInputDevice> InputDevice = Module.GetInputDevice();
    if (!InputDevice.IsValid())
    {
        return;
    }

    // 通过 Motion Controller 接口获取特定关节
    TSharedPtr<IMotionController> MotionController = StaticCastSharedPtr<IMotionController>(InputDevice);
    if (MotionController.IsValid())
    {
        FRotator Orientation;
        FVector Position;
        float WorldToMeters = 100.0f;

        // Motion Source 名称格式：Left[Keypoint] 或 Right[Keypoint]
        FName MotionSource("LeftPalm");
        ETrackingStatus Status = MotionController->GetControllerTrackingStatus(0, MotionSource);

        if (Status == ETrackingStatus::Tracked)
        {
            MotionController->GetControllerOrientationAndPosition(
                0, MotionSource, Orientation, Position, WorldToMeters);
        }
    }
}
```

### 进阶用法：手动管理 LiveLink 源

```cpp
#include "IOpenXRHandTrackingModule.h"
#include "ILiveLinkSource.h"

void AMyActor::SetupLiveLink()
{
    if (!IOpenXRHandTrackingModule::IsAvailable())
    {
        return;
    }

    auto& Module = IOpenXRHandTrackingModule::Get();

    // 检查并添加 LiveLink 源
    if (!Module.IsLiveLinkSourceValid())
    {
        Module.AddLiveLinkSource();
    }

    // 获取 LiveLink 源指针
    TSharedPtr<ILiveLinkSource> Source = Module.GetLiveLinkSource();
    if (Source.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("LiveLink Source: %s"), *Source->GetSourceType().ToString());
    }

    // 移除 LiveLink 源（不再需要时）
    // Module.RemoveLiveLinkSource();
}
```

## Demo 示例

以下示例展示一个 Actor 组件，实时读取双手关节数据并驱动对应的骨骼网格体：

```cpp
// HandTrackingComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "IHandTracker.h"
#include "HandTrackingComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UHandTrackingComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UHandTrackingComponent();

    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

    /** 手部关节位置（蓝图可读，用于调试） */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Hand Tracking")
    TArray<FTransform> LeftHandTransforms;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Hand Tracking")
    TArray<FTransform> RightHandTransforms;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Hand Tracking")
    bool bLeftHandTracked = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Hand Tracking")
    bool bRightHandTracked = false;

protected:
    virtual void BeginPlay() override;

private:
    void UpdateHandData(EControllerHand Hand, TArray<FTransform>& OutTransforms, bool& OutTracked);
    void ApplyToSkeletalMesh(USkeletalMeshComponent* Mesh, const TArray<FTransform>& Transforms);
};
```

```cpp
// HandTrackingComponent.cpp
#include "HandTrackingComponent.h"
#include "Components/SkeletalMeshComponent.h"

UHandTrackingComponent::UHandTrackingComponent()
{
    PrimaryComponentTick.bCanEverTick = true;

    LeftHandTransforms.SetNum(EHandKeypointCount);
    RightHandTransforms.SetNum(EHandKeypointCount);
}

void UHandTrackingComponent::BeginPlay()
{
    Super::BeginPlay();
}

void UHandTrackingComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    IHandTracker& HandTracker = IHandTracker::Get();
    if (!HandTracker.IsHandTrackingStateValid())
    {
        bLeftHandTracked = false;
        bRightHandTracked = false;
        return;
    }

    UpdateHandData(EControllerHand::Left, LeftHandTransforms, bLeftHandTracked);
    UpdateHandData(EControllerHand::Right, RightHandTransforms, bRightHandTracked);
}

void UHandTrackingComponent::UpdateHandData(EControllerHand Hand,
    TArray<FTransform>& OutTransforms, bool& OutTracked)
{
    IHandTracker& HandTracker = IHandTracker::Get();

    TArray<FVector> Positions;
    TArray<FQuat> Rotations;
    TArray<float> Radii;
    bool bIsTracked = false;

    if (HandTracker.GetAllKeypointStates(Hand, Positions, Rotations, Radii, bIsTracked))
    {
        OutTracked = bIsTracked;
        for (int32 i = 0; i < Positions.Num() && i < OutTransforms.Num(); ++i)
        {
            OutTransforms[i] = FTransform(Rotations[i], Positions[i]);
        }
    }
    else
    {
        OutTracked = false;
    }
}
```

## 模块依赖

Runtime 模块的依赖（从 Build.cs 提取）：

| 模块 | 用途 |
|---|---|
| `InputDevice` | 输入设备框架，提供 `IInputDevice` 基础接口 |

无其他特殊依赖（编辑器侧依赖 UnrealEd、EditorFramework、InputEditor 为常见编辑器模块）。

此外，该插件**隐式依赖**以下 UE5 插件（在 .uplugin 中声明）：

| 插件 | 用途 |
|---|---|
| `OpenXR` | OpenXR 运行时和扩展框架 |
| `LiveLink` | LiveLink 实时数据传输框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2025-09-16 | `308ebb2b` | OpenXR now building for all platforms. | OpenXR 扩展至全平台编译支持 |
| 2025-07-21 | `3b02ba19` | Added OnCreateHandTracker() IOpenXRExtensionPlugin hook for xrCreateHandTrackerEXT() OpenXR call | 新增手部追踪器创建钩子，支持自定义扩展 |
| 2025-06-19 | `6e6685c7` | Enabling LinuxArm64 support for OpenXR | 启用 Linux ARM64 平台的 OpenXR 支持 |
| 2025-06-17 | `c938772e` | [Backout] - CL43548023 | 回退某个变更 |

### 维护评价

**活跃维护中** ✅

- 插件创建于 2020 年，已有约 6 年历史，但持续有实质性更新
- 2025 年有多次功能性更新（LinuxArm64 支持、全平台编译、手部追踪器钩子扩展）
- 作为 OpenXR 生态的核心手部追踪组件，跟随 OpenXR 标准演进
- 默认禁用状态说明 Epic 将其定位为可选功能，而非核心依赖
- **推荐使用**：如果你的 VR 项目需要手部追踪功能，这是 UE5 官方提供的标准方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRHandTracking)
- OpenXR 手部追踪扩展规范：[XR_EXT_hand_tracking](https://www.khronos.org/registry/OpenXR/specs/1.0/html/xrspec.html#XR_EXT_hand_tracking)