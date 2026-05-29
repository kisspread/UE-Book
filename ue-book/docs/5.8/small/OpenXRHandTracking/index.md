# OpenXR Hand Tracking

> OpenXR Hand Tracking provides XR_EXT_hand_tracking support.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | OpenXR 手部追踪 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产类型待定） |
| 模块 | `OpenXRHandTracking` (Runtime), `OpenXRHandTrackingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRHandTracking) | |

## 用途

该插件是 Unreal Engine 对 OpenXR 扩展 `XR_EXT_hand_tracking` 的官方集成。它解决了在基于 OpenXR 的 VR/AR 项目中实现自然手势追踪的问题，让开发者能够直接访问用户双手的骨骼姿态数据，从而替代或补充传统的手柄控制器输入，用于实现更沉浸和自然的交互方式（例如，用裸手抓取物体、做手势命令、查看手部动画等）。

## 使用场景

- 你正在开发一个 VR 交互体验，希望用户能用自己的双手（而非手柄）与虚拟环境进行直接互动。
- 你需要为 VR 应用添加基于手势的用户界面控制（例如，捏合缩放、挥手切换）。
- 你想在 VR 中实现高质量的手部模型动画，使其精确反映用户的真实手部动作。
- 你的项目需要支持多种 VR 输入方式，希望在 OpenXR 平台上统一处理手部追踪数据。

## 蓝图用法

该插件主要通过增强 Unreal Engine 的输入子系统工作。以下是其核心蓝图功能节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `获取追踪状态 (Get Tracking State)` | 查询当前手部追踪功能是否可用、被跟踪。 | `UOpenXRHandTracking` |
| `获取手部骨骼变换 (Get Hand Skeletal Transforms)` | 获取指定骨骼（如手腕、手指关节）在世界或追踪空间中的变换（位置、旋转）。 | `UOpenXRHandTracking` |
| `设置手部追踪源 (Set Hand Tracking Source)` | 将 OpenXR 手部追踪数据关联到指定的 `UInputComponent` 或 `AMotionControllerComponent`，使其自动驱动组件的变换。 | `UOpenXRHandTracking` |

### 使用示例（蓝图描述）

1.  **获取手部数据**: 在角色蓝图中，通过 `Get Tracking State` 节点先检查 `Left` 或 `Right` 手是否被追踪。如果返回 `ETrackingStatus::Tracked`，则使用 `Get Hand Skeletal Transforms` 节点，输入 `EControllerHand::Left` 和目标骨骼名（如 `“index_01”`），即可获得该骨骼的世界空间变换，用于驱动场景中的手部模型。
2.  **驱动手部模型**: 将 `MotionController` 组件的输入源设置为 OpenXR Hand Tracking。这通常通过蓝图中的 `Set Hand Tracking Source` 节点完成，将其连接到 `MotionController` 组件，该组件的位置和旋转将自动跟随用户的物理手部。

## C++ 用法

### 头文件引入

```cpp
#include "OpenXRHandTracking.h"
```

### 基本用法

获取手部追踪状态和基础骨骼数据。

```cpp
// 来源：OpenXRHandTracking 模块测试用例推断
#include "OpenXRHandTracking.h"
#include "HeadMountedDisplayFunctionLibrary.h"

void AMyActor::CheckHandTracking()
{
    // 检查 OpenXR 运行时是否支持手部追踪扩展
    if (UOpenXRHandTracking* HandTracking = GEngine->GetEngineSubsystem<UOpenXRHandTracking>())
    {
        ETrackingStatus Status = HandTracking->GetTrackingStatus(EControllerHand::Right);
        if (Status == ETrackingStatus::Tracked)
        {
            // 获取右手腕的变换
            FTransform WristTransform;
            HandTracking->GetBoneTransform(EControllerHand::Right, FName("wrist"), WristTransform);
            // 使用 WristTransform...
        }
    }
}
```

### 进阶用法

将手部追踪数据深度集成到输入系统，并处理 LiveLink 数据流。

```cpp
// 来源：结合模块文档和 LiveLink 插件用法推断
#include "OpenXRHandTracking.h"
#include "Roles/LiveLinkAnimationRole.h"

void AMyCharacter::SetupHandInput()
{
    // 1. 在项目设置或运行时启用 OpenXR Hand Tracking 插件后，它会自动向引擎的输入设备注册。
    // 2. 为动画蓝图或角色蓝图中的 Mesh 组件创建 LiveLink Subject。
    UOpenXRHandTracking* HandTracking = GEngine->GetEngineSubsystem<UOpenXRHandTracking>();
    if (HandTracking)
    {
        // 设置 LiveLink 数据源，将手部追踪数据转换为动画蓝图可用的骨骼数据流
        FOpenXRHandTrackingLiveLinkData LiveLinkData;
        LiveLinkData.Role = ULiveLinkAnimationRole::StaticClass();
        LiveLinkData.SubjectName = FName("MyCharacter_LeftHand");
        HandTracking->SetLiveLinkSubjectForHand(EControllerHand::Left, LiveLinkData);
    }
}
```

## Demo 示例

一个可编译的最小 Actor，用于每帧打印左手食指指尖的 Z 坐标。

**OpenXRHandTrackingDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OpenXRHandTrackingDemo.generated.h"

UCLASS()
class AOpenXRHandTrackingDemo : public AActor
{
    GENERATED_BODY()

public:
    AOpenXRHandTrackingDemo();

protected:
    virtual void Tick(float DeltaTime) override;
};
```

**OpenXRHandTrackingDemo.cpp**
```cpp
#include "OpenXRHandTrackingDemo.h"
#include "OpenXRHandTracking.h"

AOpenXRHandTrackingDemo::AOpenXRHandTrackingDemo()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AOpenXRHandTrackingDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    UOpenXRHandTracking* HandTracking = GEngine->GetEngineSubsystem<UOpenXRHandTracking>();
    if (!HandTracking) return;

    if (HandTracking->GetTrackingStatus(EControllerHand::Left) == ETrackingStatus::Tracked)
    {
        FTransform FingertipTransform;
        // 骨骼名需根据实际 OpenXR 手部骨骼映射表确定，常见为 “index_tip”
        if (HandTracking->GetBoneTransform(EControllerHand::Left, FName("index_tip"), FingertipTransform))
        {
            UE_LOG(LogTemp, Log, TEXT("Left Index Fingertip Z: %.2f"), FingertipTransform.GetLocation().Z);
        }
    }
}
```

## 模块依赖

要使用此插件，你的项目或模块通常无需直接添加额外依赖，因为插件本身会将其功能集成到引擎的输入和 LiveLink 子系统中。但如果你需要在代码中直接访问其 `UOpenXRHandTracking` 子系统，需确保在 `Build.cs` 中依赖 `OpenXRHandTracking` 模块。

| 模块 | 用途 |
|---|---|
| `OpenXR` | 提供底层的 OpenXR API 和运行时支持，是本插件工作的基础。 |
| `LiveLink` | 用于将手部追踪数据实时流式传输到动画蓝图，实现高质量的动画驱动。 |

## 维护状态

该插件作为 Epic Games 的官方 VR 支持组件，保持了稳定的维护。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 `UE_LOGF` 格式化日志系统。 |
| 2025-09-16 | `308ebb2b` | OpenXR now building for all platforms. | 修复编译问题，确保 OpenXR 相关代码能在所有目标平台上构建。 |
| 2025-07-21 | `3b02ba19` | Added OnCreateHandTracker() IOpenXRExtensionPlugin hook for xrCreateHandTrackerEXT() OpenXR call | 新增一个扩展钩子，允许其他插件介入 OpenXR 手部追踪器的创建过程。 |
| 2025-06-19 | `6e6685c7` | Enabling LinuxArm64 support for OpenXR | 为 LinuxArm64 平台启用 OpenXR 支持，扩展了插件的跨平台能力。 |
| 2025-06-17 | `c938772e` | [Backout] - CL43548023 | 回退了一次之前的提交，通常是修复回归问题。 |

### 维护评价

- **维护状态**: 活跃维护中。最近一次更新在 2026 年 4 月，并且在过去一年内有多次功能性更新（如平台扩展、钩子API）。
- **稳定性**: 作为 Runtime 插件且默认关闭，表明它被视为一项需要用户显式启用的功能，但 Epic 持续投入维护。
- **推荐**: **推荐使用**。对于任何需要基于 OpenXR 平台实现高质量手部追踪功能的 UE5 项目，这是官方且首选的集成方案。启用时需注意项目已正确配置 OpenXR 运行时和硬件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRHandTracking)
- [官方文档](https://docs.unrealengine.com/)（请在官方文档站搜索“OpenXR Hand Tracking”）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRHandTracking/Tests)