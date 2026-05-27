# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏相机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、数据资产、材质模板、测试资源） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是一个模块化、数据驱动的相机系统，用于替代传统的 `UCameraComponent` 和 `UCineCameraComponent`。它解决了传统相机系统扩展性差、逻辑与数据耦合紧密的问题。通过这个插件，开发者可以使用蓝图或数据资产（`UGameplayCameraAsset`）来定义复杂的相机行为、摇臂、景深等参数，实现高度自定义的电影级摄像机效果，同时保持良好的性能和模块化架构。

## 使用场景

- 你需要创建电影级或玩法复杂的相机系统，例如第三人称过肩视角、电影序列、动态景深等 → 用 GameplayCameras
- 你想要在不修改 C++ 代码的情况下，通过数据资产和蓝图快速迭代相机行为 → 用 GameplayCameras
- 你需要相机在不同游戏状态（如瞄准、驾驶、过场动画）之间平滑切换 → 用 GameplayCameras
- 你正在开发需要大量电影化镜头的游戏，如叙事驱动游戏或赛车游戏 → 用 GameplayCameras

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| `GameplayCameras` | Runtime | 核心运行时模块，包含所有相机逻辑、摇臂、数据资产和基础组件 |
| `GameplayCamerasEditor` | Runtime | 编辑器支持模块，提供自定义的编辑器工具、资产编辑器和属性自定义界面 |
| `GameplayCamerasUncookedOnly` | Runtime | 仅未打包模块，处理编辑器内的资产预处理、转换和蓝图分析 |

## 蓝图用法概述

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Camera Asset` | 为玩家控制器设置当前使用的 Gameplay Camera 数据资产 | `AGameplayCameraActor` |
| `Push Camera Mode` | 将一个新的相机模式压入栈，优先级高于当前模式 | `UGameplayCameraComponent` |
| `Pop Camera Mode` | 从栈中弹出当前相机模式 | `UGameplayCameraComponent` |
| `Blend To Camera` | 平滑混合到指定的相机资产或设置 | `UGameplayCameraComponent` |
| `Get Camera Settings` | 获取当前相机资产的特定参数（如视野、景深等） | `UGameplayCameraAsset` |

### 使用示例（蓝图描述）

1. **基础设置**：在场景中放置一个 `GameplayCameraActor`，并为它指定一个 `GameplayCameraAsset` 数据资产。在玩家控制器中获取该 Actor 的引用。
2. **动态切换**：当玩家按下某个键（如瞄准键），调用 `Push Camera Mode` 节点，传入一个代表“瞄准模式”的相机数据资产或配置。松开按键时，调用 `Pop Camera Mode`。
3. **参数驱动**：在蓝图中通过 `Get Camera Settings` 节点读取当前相机的 `Field of View`（视野）参数，用于驱动 HUD 上的准星缩放动画。

## C++ 用法概述

### 头文件引入

```cpp
#include "GameplayCameras.h"
```

### 基本用法

主要通过 `UGameplayCameraComponent` 控制相机行为。

```cpp
// 在角色类中创建并配置相机组件
UGameplayCameraComponent* CameraComponent = CreateDefaultSubobject<UGameplayCameraComponent>(TEXT("GameplayCamera"));
CameraComponent->SetCameraAsset(DefaultCameraAsset); // DefaultCameraAsset 是 UGameplayCameraAsset* 类型
CameraComponent->AttachToComponent(RootComponent, FAttachmentTransformRules::SnapToTargetNotIncludingScale);
```

### 进阶用法

动态管理相机栈，实现复杂的视角切换。

```cpp
// 压入一个新的相机模式（例如瞄准）
UObject* AimMode = LoadObject<UGameplayCameraAsset>(nullptr, TEXT("/Game/Cameras/AimMode"));
if (AimMode)
{
    CameraComponent->PushCameraMode(AimMode);
}

// 在某个时机弹出
CameraComponent->PopCameraMode();
```

## Demo 示例

一个最小化的、实现基础跟随和按键切换视野的示例。

**CameraPawn.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameplayCameras.h"
#include "CameraPawn.generated.h"

UCLASS()
class ACameraPawn : public APawn
{
    GENERATED_BODY()
public:
    ACameraPawn();
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
    UGameplayCameraComponent* CameraComponent;

    UPROPERTY(EditDefaultsOnly, Category = "Camera")
    UGameplayCameraAsset* DefaultCameraAsset;

    UPROPERTY(EditDefaultsOnly, Category = "Camera")
    UGameplayCameraAsset* ZoomedCameraAsset;

private:
    void ZoomIn();
    void ZoomOut();
    bool bIsZoomed = false;
};
```

**CameraPawn.cpp**
```cpp
#include "CameraPawn.h"
#include "Components/InputComponent.h"

ACameraPawn::ACameraPawn()
{
    CameraComponent = CreateDefaultSubobject<UGameplayCameraComponent>(TEXT("GameplayCamera"));
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    CameraComponent->AttachToComponent(RootComponent, FAttachmentTransformRules::SnapToTargetNotIncludingScale);
}

void ACameraPawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    PlayerInputComponent->BindAction("Zoom", IE_Pressed, this, &ACameraPawn::ZoomIn);
    PlayerInputComponent->BindAction("Zoom", IE_Released, this, &ACameraPawn::ZoomOut);
}

void ACameraPawn::ZoomIn()
{
    if (ZoomedCameraAsset && !bIsZoomed)
    {
        CameraComponent->PushCameraMode(ZoomedCameraAsset);
        bIsZoomed = true;
    }
}

void ACameraPawn::ZoomOut()
{
    if (bIsZoomed)
    {
        CameraComponent->PopCameraMode();
        bIsZoomed = false;
    }
}
```

## 模块依赖

此插件对以下非标准模块有依赖。你的项目如果要使用，需要在对应的 `.Build.cs` 中添加。

| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 核心相机运行时逻辑 |
| `GameplayCamerasEditor` | 编辑器内相机资产编辑和预览 |
| `GameplayCamerasUncookedOnly` | 资产预处理和蓝图分析 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复在 PIE 模式下相机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 为部分追踪通道添加或更新描述 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 通用提交（可能为内部代码整理或小修复） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF（更安全的日志宏） |

### 维护评价

- **创建时间**：2020 年创建，已有约 6 年历史。
- **近期活跃度**：**非常活跃**。最近一次更新在 2026 年 5 月，且过去 1 个月内有多次实质性功能修复和代码改进。
- **维护状态**：由 Epic Games 官方维护，作为 Unreal 引擎未来相机系统的基础，持续投入开发。
- **已知限制**：由于标记为 `IsExperimentalVersion`，其 API 和架构可能在后续版本中发生变化。
- **推荐使用**：**推荐**。尽管是实验性功能，但其强大的模块化、数据驱动特性和官方的积极维护，使其成为复杂相机需求的首选方案。建议在项目早期引入，并关注其 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档](https://docs.unrealengine.com/en-US/)（待补充，此插件文档尚在完善中）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras/Tests)