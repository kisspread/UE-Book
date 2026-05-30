# OpenXR Msft Hand Interaction

> OpenXRMsftHandInteraction provides support for the XR_MSFT_hand_interaction OpenXR Extension. This allows hand tracking to act as a motion controller.

| 属性 | 值 |
|---|---|
| 中文名 | OpenXR 微软手势交互 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OpenXRMsftHandInteraction` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRMsftHandInteraction) | |

## 用途

本插件为 Unreal Engine 的 OpenXR 运行时添加对微软 `XR_MSFT_hand_interaction` 扩展的支持。该扩展的核心功能是**将手势追踪（Hand Tracking）的数据映射为标准的运动控制器输入**，使得用户无需物理控制器，仅凭双手即可与 VR/MR 场景进行交互。

与基础的手势追踪插件（仅提供骨骼关节数据）不同，本插件实现了 OpenXR 的 **Interaction Profile** 机制，将手势识别为具体的交互意图（如捏合、指向、抓握），从而让现有的 Motion Controller 输入系统能够直接处理手势输入。

主要支持以下 Interaction Profile：
- `XR_MSFT_hand_interaction` — 通用手势交互
- `XR_EXT_hand_interaction` — 扩展手势交互（Pinch、Grasp、Poke 等）

### 典型硬件

适用于支持手部追踪的 OpenXR 设备，例如：
- Microsoft HoloLens 2
- Meta Quest 3 / Quest Pro（需支持对应扩展）
- Windows Mixed Reality 头显（配合手部追踪）

## 使用场景

- 你正在为 HoloLens 2 开发 MR 应用，希望用户用双手直接操作 UI 和物体
- 你在做一个 VR 体验，希望同时支持物理控制器和裸手交互，无需分别处理两套输入
- 你使用了 Enhanced Input 系统并绑定到 Motion Controller 输入，想让手势自动兼容

## 蓝图用法

本插件为纯扩展注册插件，**不包含任何蓝图节点**。其功能通过向 OpenXR 运行时注册扩展和 Interaction Profile，使得手势输入自动出现在引擎的 Motion Controller 输入通道中。

### 工作方式

1. 启用插件后，引擎加载时会请求 `XR_MSFT_hand_interaction` 扩展
2. 注册相应的 Interaction Profile
3. 手势追踪数据被自动映射为 Motion Controller 轴和按键
4. 你在蓝图中使用标准的 Motion Controller 节点即可接收手势输入

### 手势映射参考

| 手势动作 | 对应控制器按键/轴 |
|---|---|
| 捏合（Pinch） | Trigger（触摸/按下） |
| 抓握（Grasp） | Grip（触摸/按下） |
| 指向方向 | 指针姿态（Aim Pose） |
| 手掌朝向 | 抓握姿态（Grip Pose） |

## C++ 用法

本插件不对外暴露可直接调用的 C++ API。其功能通过 OpenXR 扩展插件接口（`IOpenXRExtensionPlugin`）自动注册。

### 头文件引入

无需引入本插件头文件。通过依赖 OpenXR 模块即可访问手势数据：

```cpp
#include "IOpenXRHMDModule.h"
```

### 基本用法

本插件作为后台扩展运行，无需编写代码。启用插件后，标准的 Motion Controller 组件即可接收手势输入：

```cpp
// 在你的 Pawn 或 Actor 中获取 Motion Controller 的追踪数据
// 当手部追踪激活时，这些数据来自手势而非物理控制器
UMotionControllerComponent* MotionController = CreateDefaultSubobject<UMotionControllerComponent>(TEXT("MotionController"));
MotionController->SetTrackingMotionSource(FName("Right"));

// 手势追踪激活时，MotionController 会自动更新位置和旋转
// Trigger/Grip 等按键通过 Input Action 系统获取
```

### 扩展插件注册机制（内部原理）

本插件的核心实现在模块启动时通过 `IOpenXRExtensionPlugin` 接口注册：

```cpp
// 注册所需的 OpenXR 扩展
bool FOpenXRMsftHandInteraction::GetRequiredExtensions(TArray<const ANSICHAR*>& OutExtensions)
{
    OutExtensions.Add(XR_MSFT_HAND_INTERACTION_EXTENSION_NAME);
    return true;
}

// 注册 Interaction Profile，使引擎识别手势输入
bool FOpenXRMsftHandInteraction::GetInteractionProfiles(XrInstance InInstance, ...)
{
    // 添加 XR_MSFT_hand_interaction 和 XR_EXT_hand_interaction 的 Profile
    // 每个 Profile 对应一种手势→控制器的映射
}
```

## Demo 示例

本插件不包含可运行的 Demo。以下是一个最小的 Actor 示例，展示启用插件后如何接收手势输入：

```cpp
// HandInteractionActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/MotionControllerComponent.h"
#include "HandInteractionActor.generated.h"

UCLASS()
class AHandInteractionActor : public AActor
{
    GENERATED_BODY()

public:
    AHandInteractionActor();

    UPROPERTY(VisibleAnywhere)
    UMotionControllerComponent* RightHand;

    virtual void Tick(float DeltaTime) override;
};
```

```cpp
// HandInteractionActor.cpp
#include "HandInteractionActor.h"
#include "HeadMountedDisplayFunctionLibrary.h"

AHandInteractionActor::AHandInteractionActor()
{
    PrimaryActorTick.bCanEverTick = true;

    RightHand = CreateDefaultSubobject<UMotionControllerComponent>(TEXT("RightHand"));
    RootComponent = RightHand;

    // 使用 "Right" Motion Source
    // 当手部追踪激活时，此组件将追踪右手位置
    RightHand->SetTrackingMotionSource(FName("Right"));
}

void AHandInteractionActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 检查手势追踪是否有效
    if (RightHand->IsTracked())
    {
        FVector HandLocation = RightHand->GetComponentLocation();
        FRotator HandRotation = RightHand->GetComponentRotation();

        // 捏合手势通过 Enhanced Input 的 Trigger Action 获取
        // 无需特殊处理，与物理控制器完全一致
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenXR` | 核心 OpenXR 运行时，提供 `IOpenXRExtensionPlugin` 接口和 XR 实例管理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-09 | `0c8ae810` | OpenXR all platform cleanup. | 全平台 OpenXR 插件清理整合 |
| 2025-07-21 | `82674f19` | OpenXR extension names: use openxr.h define rather than hard coding the names. | 使用 openxr.h 宏定义替代硬编码扩展名 |
| 2024-08-01 | `0ba65eae` | [OpenXR]One extension plugin adds multiple interaction profiles | 支持单个扩展插件注册多个交互配置 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件链接为 HTTPS 协议 |
| 2022-08-12 | `685ff1f9` | OpenXRMsftHandInteraction plugin, remove beta tag | 移除 Beta 标记，正式发布 |

### 维护评价

**活跃维护** — 该插件虽然代码量极小（仅 2 个源文件），但持续获得更新以保持与 OpenXR 规范的兼容性。最近一次更新在 2026 年 2 月，说明仍在活跃维护。

- ✅ 代码精简，职责单一，维护风险低
- ✅ 2022 年移除 Beta 标签，已是正式功能
- ✅ 持续跟进 OpenXR 规范变更（如多 Profile 支持、宏定义规范化）
- ⚠️ 需要手动启用（`EnabledByDefault: false`）
- ✅ 推荐使用：如需支持手部追踪作为控制器输入，这是官方推荐方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRMsftHandInteraction)
- [OpenXR Msft Hand Interaction 扩展规范](https://www.khronos.org/registry/OpenXR/specs/1.0/html/xrspec.html#XR_MSFT_hand_interaction)
- [OpenXR 插件文档](https://docs.unrealengine.com/en-US/SharingAndReleasing/XRDevelopment/OpenXR/)