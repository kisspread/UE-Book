# OpenXRHandTracking

> OpenXR Hand Tracking provides XR_EXT_hand_tracking support.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | OpenXR手部追踪 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（初始化资产） |
| 模块 | `OpenXRHandTracking` (Runtime), `OpenXRHandTrackingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRHandTracking) | |

## 用途

此插件为 Unreal Engine 的 OpenXR 运行时添加了 **XR_EXT_hand_tracking** 扩展支持。它允许使用支持手部追踪的 XR 设备（如 Meta Quest Pro、Valve Index 控制器）来获取玩家手部的实时骨骼姿态和关节旋转数据。其主要目的是将底层 OpenXR 的手部追踪能力暴露给 UE 的开发框架，从而让开发者能够基于手势、手部动画或免控制器的交互来创建应用。它依赖于 `OpenXR` 插件，并通过 `LiveLink` 插件来流式传输追踪数据。

## 使用场景

- 你正在开发一个 VR 应用，目标设备支持手部追踪（如 Quest Pro），希望实现免控制器的交互。
- 你需要使用真实的手部动作来驱动虚拟角色的手部动画。
- 你希望识别简单的手势（如捏合、指向）来作为输入。
- 你已经在使用 OpenXR 作为 XR 运行时，并希望利用其附加的扩展功能。

## 蓝图用法

从 `OpenXRHandTracking.h` 中提取的关键蓝图接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsHandTrackingEnabled` | 检查当前 XR 会话是否已启用并正在运行手部追踪。 | `UOpenXRHandTracking` |
| `GetHandTrackingData` | 获取指定手（左手/右手）的最新追踪数据，包括每个关节的变换。 | `UOpenXRHandTracking` |
| `GetHandBoneRotation` | 获取指定手特定骨骼（关节）相对于手部根部（腕部）的旋转。 | `UOpenXRHandTracking` |
| `GetHandScale` | 获取指定手的整体缩放估计值。 | `UOpenXRHandTracking` |

### 使用示例（蓝图描述）

1.  **初始化与检查**：在 Actor 的 `BeginPlay` 或角色初始化逻辑中，调用 `IsHandTrackingEnabled` 节点。通常将其结果连接到一个 `Branch` 节点，以便在手部追踪可用时启用相关的交互逻辑。
2.  **获取持续数据**：在 `Event Tick` 或自定义的定时事件中，使用 `GetHandTrackingData` 节点（指定 `EControllerHand::Left` 或 `EControllerHand::Right`）来持续获取手部姿态数据。
3.  **提取特定信息**：将 `GetHandTrackingData` 的输出结构体连接到 `Break` 节点，以提取各个关节的 `Transform`。或者直接使用 `GetHandBoneRotation` 节点（例如获取 `EHandBone::Index_03` 的旋转）来驱动单个骨骼的动画。

## C++ 用法

### 头文件引入

```cpp
#include "OpenXRHandTracking.h"
#include "IOpenXRHandTrackingModule.h"
```

### 基本用法

以下代码片段展示了如何检查手部追踪状态并获取基础数据。

```cpp
// 获取手部追踪模块实例
IOpenXRHandTrackingModule* HandTrackingModule = FModuleManager::GetModulePtr<IOpenXRHandTrackingModule>(TEXT("OpenXRHandTracking"));
if (HandTrackingModule && HandTrackingModule->IsHandTrackingEnabled())
{
    // 模块存在且手部追踪已启用
    FOpenXRHandTrackingData LeftHandData;
    if (HandTrackingModule->GetHandTrackingData(EControllerHand::Left, LeftHandData))
    {
        // 成功获取左手数据
        // LeftHandData.JointTransforms 包含所有关节的变换信息
        FTransform WristTransform = LeftHandData.JointTransforms[static_cast<int32>(EOculusXrHandJoint::Wrist)];
        // 使用手腕位置等...
    }
}
```

*(基于对 `OpenXRHandTracking.h` 中接口声明和模块获取方式的分析)*

### 进阶用法

结合手势识别的简单逻辑示例。

```cpp
// 检测一个简单的“捏合”手势（拇指尖和食指尖靠近）
void AMyHandInteractionActor::CheckPinchGesture()
{
    IOpenXRHandTrackingModule* HandTrackingModule = ...; // 获取模块
    if (!HandTrackingModule || !HandTrackingModule->IsHandTrackingEnabled()) return;

    FOpenXRHandTrackingData RightHandData;
    if (HandTrackingModule->GetHandTrackingData(EControllerHand::Right, RightHandData))
    {
        const FTransform& ThumbTip = RightHandData.JointTransforms[static_cast<int32>(EOculusXrHandJoint::Thumb_Tip)];
        const FTransform& IndexTip = RightHandData.JointTransforms[static_cast<int32>(EOculusXrHandJoint::Index_Tip)];

        float Distance = FVector::Dist(ThumbTip.GetLocation(), IndexTip.GetLocation());
        if (Distance < PinchThreshold) // PinchThreshold 是一个自定义的阈值（例如 2.0 cm）
        {
            // 执行捏合手势触发的动作
            OnPinchGestureDetected();
        }
    }
}
```

*(逻辑基于通用手部追踪 API 的典型用法和关节枚举)*

## Demo 示例

一个用于打印左手手腕位置的最小 Actor 示例。

**HandTrackerActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HandTrackerActor.generated.h"

class IOpenXRHandTrackingModule;

UCLASS()
class AHandTrackerActor : public AActor
{
    GENERATED_BODY()

public:
    AHandTrackerActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    IOpenXRHandTrackingModule* HandTrackingModule = nullptr;
};
```

**HandTrackerActor.cpp**
```cpp
#include "HandTrackerActor.h"
#include "IOpenXRHandTrackingModule.h"

AHandTrackerActor::AHandTrackerActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AHandTrackerActor::BeginPlay()
{
    Super::BeginPlay();
    HandTrackingModule = FModuleManager::GetModulePtr<IOpenXRHandTrackingModule>(TEXT("OpenXRHandTracking"));
}

void AHandTrackerActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (HandTrackingModule && HandTrackingModule->IsHandTrackingEnabled())
    {
        FOpenXRHandTrackingData LeftHandData;
        if (HandTrackingModule->GetHandTrackingData(EControllerHand::Left, LeftHandData))
        {
            const FTransform& WristTransform = LeftHandData.JointTransforms[static_cast<int32>(EOculusXrHandJoint::Wrist)];
            FVector WristLocation = WristTransform.GetLocation();
            UE_LOG(LogTemp, Log, TEXT("Left Hand Wrist Location: %s"), *WristLocation.ToString());
        }
    }
}
```

## 模块依赖

从 `OpenXRHandTracking.Build.cs` 分析得出，使用者需要依赖：

| 模块 | 用途 |
|---|---|
| `OpenXRHandTracking` | 提供手部追踪的核心运行时模块和 API。 |
| `OpenXR` | 提供底层的 OpenXR 运行时和扩展框架。 |
| `LiveLink` | 用于将手部追踪数据作为 LiveLink 源进行传输和同步。 |

**注意**：`OpenXRHandTracking` 模块自身依赖 `InputDevice`, `EditorFramework`, `UnrealEd`, `InputEditor`，但这些主要是为了集成编辑器支持。对于纯运行时使用，上表中的依赖是直接相关的。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 格式，属于代码现代化更新。 |
| 2025-09-16 | `308ebb2b` | OpenXR now building for all platforms. | 确保 OpenXR 相关插件能在所有支持的平台上编译，提升了兼容性。 |
| 2025-07-21 | `3b02ba19` | Added OnCreateHandTracker() IOpenXRExtensionPlugin hook for xrCreateHandTrackerEXT() OpenXR call | 添加了新的扩展插件钩子，允许其他模块在手部追踪器创建时进行干预或附加功能。 |
| 2025-06-19 | `6e6685c7` | Enabling LinuxArm64 support for OpenXR | 为 Linux ARM64 架构（如树莓派、Steam Deck 等）启用了 OpenXR 支持，扩大了平台覆盖范围。 |
| 2025-06-17 | `c938772e` | [Backout] - CL43548023 | 回退了之前的某次提交（CL43548023），可能是因为引入了编译或运行时问题。 |

### 维护评价

该插件自 2020 年创建，已有约 5.5 年历史。尽管默认未启用，但从 **近期提交记录** 来看，**维护非常活跃**。更新内容不仅包括平台扩展（LinuxArm64）、API 增强（新钩子），还有代码现代化和持续集成维护。它作为 Epic Games 官方维护的 OpenXR 生态重要组成部分，状态健康，**强烈推荐**有手部追踪需求的开发者使用。需要注意的是，它是一个 **运行时插件**，需要硬件支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRHandTracking)
- [官方文档]() （.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/OpenXRHandTracking) （假设测试位于此目录，常见模式）