# OpenXRHandTracking

> OpenXR Hand Tracking provides XR_EXT_hand_tracking support.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Reality |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | OpenXRHandTracking (Runtime), OpenXRHandTrackingEditor (Editor) |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXRHandTracking) | |

## 用途

该插件实现了 OpenXR 的 `XR_EXT_hand_tracking` 扩展，将 XR 头显的手部追踪数据接入 UE5 的输入系统和 LiveLink 系统。它将 OpenXR 的 26 个手部关节（`EHandKeypoint`，包括 Palm、Wrist、五指各 5 个关节）的位姿数据映射为 UE5 的 Motion Controller 源和 IHandTracker 接口，使蓝图和 C++ 代码可以通过标准的 Motion Source 名称（如 `LeftPalm`、`RightIndexTip`）获取手部追踪数据。

核心功能包括：
- 通过 OpenXR 扩展获取双手 26 个关节的位置、旋转和半径
- 注册为 `IMotionController`、`IHandTracker`、`IOpenXRExtensionPlugin` 三个模块化特性
- 作为 LiveLink Source 推送左右手骨骼动画数据（Subject: `LeftHand` / `RightHand`）
- 提供可配置的 Motion Source 命名策略，避免与控制器输入冲突

## 使用场景

- 你在做一个 VR 应用，需要用手势（捏、抓、指等）进行交互 → 启用此插件，通过 Motion Source 或 IHandTracker 获取手部关键点位姿
- 你需要将手部追踪数据驱动骨骼动画（如虚拟手模型） → 通过 LiveLink 接收手部骨骼数据，配合 `UOpenXRHandTrackingLiveLinkRemapAsset` 做骨骼重定向
- 你的项目同时使用手柄和手部追踪 → 将 `bUseMoreSpecificMotionSourceNames` 设为 `true`，使手部追踪源使用 `HandTrackingLeft*` / `HandTrackingRight*` 前缀，避免与手柄的 `Left` / `Right` 冲突

## 蓝图用法

该插件本身不暴露额外的 BlueprintCallable 函数，而是通过 UE5 标准的 Motion Controller 和 Hand Tracker 接口工作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Motion Controller Data` (EnhancedInput) | 通过 Motion Source 名称获取手部关节位姿 | 标准引擎节点 |
| `Get Keypoint State` | 通过 IHandTracker 接口获取单个关节的 Transform 和 Radius | `IHandTracker` |
| `Get All Keypoint States` | 获取一只手的所有关节位置、旋转、半径 | `IHandTracker` |
| LiveLink Subject 数据 | 通过 LiveLink 面板查看 `LeftHand` / `RightHand` 的骨骼动画数据 | LiveLink 系统 |

### Motion Source 命名规则

默认模式（`bUseMoreSpecificMotionSourceNames = false`）：
- `LeftPalm`、`LeftWrist`、`LeftThumbTip`、`RightIndexTip` 等

特定前缀模式（`bUseMoreSpecificMotionSourceNames = true`）：
- `HandTrackingLeftPalm`、`HandTrackingRightIndexTip` 等

若 `bSupportLegacyControllerMotionSources = true`（默认），还支持简写的 `Left` / `Right`（映射到 Palm 关节）。

### 使用示例（蓝图描述）

1. 在 Motion Controller 组件上设置 Motion Source 为 `LeftPalm` 或 `RightPalm`，即可让该组件跟随手掌位置
2. 在 LiveLink 面板中找到 `OpenXR Hand Tracking` 源，可以看到 `LeftHand` 和 `RightHand` 两个 Subject
3. 在动画蓝图中使用 LiveLink 节点接收手部骨骼数据，配合 `UOpenXRHandTrackingLiveLinkRemapAsset` 进行骨骼重定向

## C++ 用法

### 头文件引入

```cpp
#include "IOpenXRHandTrackingModule.h"
#include "IHandTracker.h"
```

### 基本用法

通过 IHandTracker 接口获取手部关节数据：

```cpp
// 获取 HandTracker 模块化特性
IHandTracker* HandTracker = IHandTracker::Get();
if (HandTracker && HandTracker->IsHandTrackingStateValid())
{
    FTransform OutTransform;
    float OutRadius;

    // 获取左手食指尖的位姿
    if (HandTracker->GetKeypointState(EControllerHand::Left, EHandKeypoint::IndexTip, OutTransform, OutRadius))
    {
        FVector Position = OutTransform.GetLocation();
        FRotator Rotation = OutTransform.GetRotation().Rotator();
        // 使用 Position 和 Rotation ...
    }
}
```

### 获取所有关节

```cpp
TArray<FVector> Positions;
TArray<FQuat> Rotations;
TArray<float> Radii;
bool bIsTracked = false;

IHandTracker* HandTracker = IHandTracker::Get();
if (HandTracker && HandTracker->GetAllKeypointStates(EControllerHand::Right, Positions, Rotations, Radii, bIsTracked))
{
    // Positions.Num() == EHandKeypointCount (26)
    for (int32 i = 0; i < Positions.Num(); ++i)
    {
        // 处理每个关节的位置 Positions[i]、旋转 Rotations[i]、半径 Radii[i]
    }
}
```

### 检测设备是否支持手部追踪

```cpp
// 通过模块接口检测
if (IOpenXRHandTrackingModule::IsAvailable())
{
    IOpenXRHandTrackingModule& Module = IOpenXRHandTrackingModule::Get();
    TSharedPtr<IInputDevice> InputDevice = Module.GetInputDevice();
    // 手部追踪设备已就绪
}
```

## Demo 示例

### 最小可用示例：读取手掌位置

```cpp
// MyHandTrackingComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "IHandTracker.h"
#include "MyHandTrackingComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyHandTrackingComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override
    {
        Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

        IHandTracker* HandTracker = IHandTracker::Get();
        if (!HandTracker || !HandTracker->IsHandTrackingStateValid())
        {
            return;
        }

        FTransform LeftPalmTransform;
        float LeftPalmRadius;
        if (HandTracker->GetKeypointState(EControllerHand::Left, EHandKeypoint::Palm, LeftPalmTransform, LeftPalmRadius))
        {
            // 左手掌位姿可用
            GetOwner()->SetActorLocation(LeftPalmTransform.GetLocation());
        }
    }
};
```

Build.cs 依赖（如需直接引用 HandTracker 接口）：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "HeadMountedDisplay" });
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InputDevice` | 输入设备基础接口（公共依赖） |
| `Core` / `CoreUObject` / `Engine` | UE 核心模块 |
| `HeadMountedDisplay` | HMD 和手部追踪接口定义（EHandKeypoint、IHandTracker） |
| `XRBase` | XR 基础设施 |
| `InputCore` | 输入核心 |
| `LiveLinkAnimationCore` / `LiveLinkInterface` | LiveLink 骨骼动画数据推送 |
| `OpenXRHMD` | OpenXR HMD 主模块 |
| `OpenXRInput` | OpenXR 输入模块 |
| `Slate` / `SlateCore` / `ApplicationCore` | UI 和应用框架 |
| `OpenXR` (ThirdParty) | OpenXR SDK 静态库 |

插件依赖（.uplugin Plugins 字段）：
- **OpenXR** — 必须启用
- **LiveLink** — 必须启用

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-23 | `000fbe45cd22` | OpenXR 改为全平台构建，移除平台限制以支持跨平台项目 |
| 2025-07-21 | `3b02ba195022` | 新增 `OnCreateHandTracker()` 扩展钩子，支持其他 OpenXR 扩展插件注入自定义数据到 `xrCreateHandTrackerEXT` 调用 |
| 2025-06-19 | `6e6685c775a4` | 启用 LinuxArm64 平台支持（不提供 OpenXR loader） |

### 维护评价

- **创建时间**：2020-09-24，已超过 5 年
- **维护状态**：**活跃维护** — 2025 年有多次功能性更新，包括平台扩展和新 API 钩子
- **稳定性**：成熟稳定，代码逻辑简洁，无 Beta 标记
- **注意事项**：`EnabledByDefault = false`，需要手动在项目设置中启用
- **推荐**：推荐使用。这是 Epic 官方维护的 OpenXR 手部追踪实现，是 UE5 中获取 XR 手部追踪数据的标准方式。如果你的项目需要手部追踪功能，这是首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXRHandTracking)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [OpenXR EXT_hand_tracking 规范](https://www.khronos.org/registry/OpenXR/specs/1.0/html/xrspec.html#XR_EXT_hand_tracking)
