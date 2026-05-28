# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 数据驱动摄像机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、摄像机节点） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Editor), `GameplayCamerasUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是 Epic 为 UE5 开发的**模块化、数据驱动的摄像机系统**，旨在替代引擎传统的摄像机管理方式。它解决的核心问题是：传统 UE 摄像机系统（基于 `APlayerCameraManager` + `UCameraComponent`）在复杂游戏场景下难以扩展和维护——摄像机行为逻辑散落在各种 Actor/Component 中，难以复用和调试。

GameplayCameras 通过以下设计解决这些问题：

- **节点图驱动的摄像机资产**（`UCameraRigAsset`）：摄像机行为以可视化节点图定义，每个节点负责摄像机的一个方面（变换、取景、碰撞、混合等），可组合、可复用
- **分层混合栈**（Blend Stack）：摄像机 rig 按层（Base/Global/Visual/Main）管理，支持独立评估后再混合，或叠加式评估
- **类型安全的摄像机变量**（Camera Variables）：所有摄像机参数通过统一的变量表管理，支持混合、覆盖和自动重置
- **蓝图可扩展性**：摄像机节点、摄像机导演（Director）、摄像机动作（Action）都支持蓝图自定义
- **摄像机动作/抖动/修改器系统**：运行时动态叠加摄像机效果
- **自动取景/碰撞处理**：内置取景节点和碰撞推进节点

本质上，它是一个**摄像机领域的 ECS-like 系统**：数据资产定义行为（CameraRigAsset），评估器执行行为（Evaluators），变量表存储状态（VariableTable），混合器管理过渡（BlendStack/Transitions）。

## 使用场景

- 你在做一个需要复杂摄像机逻辑的动作游戏（如跑酷、战斗、过场）→ 用 CameraRigAsset 定义不同场景的摄像机行为，用 CameraDirector 切换
- 你需要摄像机自动取景目标（如赛车游戏中车辆始终在画面合适位置）→ 用 BaseFramingCameraNode
- 你需要摄像机碰撞检测和安全位置推进 → 用 CollisionPushCameraNode
- 你需要在蓝图中完全自定义摄像机逻辑 → 用 BlueprintCameraNode 或 BlueprintCameraDirector
- 你需要运行时叠加摄像机效果（如受击抖动、瞄准特写）→ 用 CameraShakeAsset / CameraAction
- 你需要多个摄像机 rig 平滑过渡 → 用 CameraRigTransition + BlendCameraNode
- 你需要把摄像机逻辑做成可配置的数据资产供设计师调整 → 整个系统就是为此设计的

## 蓝图用法

### 核心节点

#### 摄像机组件（GameplayCameraComponentBase）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActivateCameraForPlayerIndex` | 为指定玩家索引激活摄像机 | `UGameplayCameraComponentBase` |
| `ActivateCameraForPlayerController` | 为指定玩家控制器激活摄像机 | `UGameplayCameraComponentBase` |
| `ActivatePersistentBaseCameraRig` | 在基础层激活持久摄像机 rig | `UGameplayCameraComponentBase` |
| `ActivatePersistentGlobalCameraRig` | 在全局层激活持久摄像机 rig | `UGameplayCameraComponentBase` |
| `ActivatePersistentVisualCameraRig` | 在视觉层激活持久摄像机 rig | `UGameplayCameraComponentBase` |
| `DeactivateCameraRig` | 停用已激活的摄像机 rig | `UGameplayCameraComponentBase` |
| `StartGlobalCameraModifierRig` | 启动全局层摄像机修改器 rig | `UGameplayCameraComponentBase` |
| `StartVisualCameraModifierRig` | 启动视觉层摄像机修改器 rig | `UGameplayCameraComponentBase` |
| `StopCameraModifierRig` | 停止摄像机修改器 rig | `UGameplayCameraComponentBase` |
| `StartCameraShakeAsset` | 启动摄像机抖动 | `UGameplayCameraComponentBase` |
| `StopCameraShakeAsset` | 停止摄像机抖动 | `UGameplayCameraComponentBase` |
| `StartAction` | 启动摄像机动作 | `UGameplayCameraComponentBase` |
| `StopAction` | 停止摄像机动作 | `UGameplayCameraComponentBase` |
| `GetEvaluatedCameraRotation` | 获取当前评估的摄像机旋转 | `UGameplayCameraComponentBase` |
| `GetOutputCameraComponent` | 获取输出的 CineCameraComponent | `UGameplayCameraComponentBase` |

#### 摄像机管理器（GameplayCamerasPlayerCameraManager）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StealPlayerController` | 替换玩家控制器的摄像机管理器为本管理器 | `AGameplayCamerasPlayerCameraManager` |
| `ReleasePlayerController` | 恢复原始摄像机管理器 | `AGameplayCamerasPlayerCameraManager` |
| `ActivateGameplayCamera` | 在管理器的摄像机系统中激活组件 | `AGameplayCamerasPlayerCameraManager` |
| `DeactivateGameplayCamera` | 停用已激活的组件 | `AGameplayCamerasPlayerCameraManager` |
| `ActivatePersistentBaseCameraRig` | 在基础层激活持久摄像机 rig | `AGameplayCamerasPlayerCameraManager` |
| `StartCameraShakeAsset` | 启动摄像机抖动 | `AGameplayCamerasPlayerCameraManager` |

#### 蓝图摄像机数据访问

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeCameraEvaluationData` | 创建摄像机评估数据 | `UBlueprintCameraEvaluationDataFunctionLibrary` |
| `GetCameraPose` / `SetCameraPose` | 获取/设置摄像机位姿 | `UBlueprintCameraEvaluationDataFunctionLibrary` |
| `BlendCameraEvaluationData` | 混合两个摄像机数据 | `UBlueprintCameraEvaluationDataFunctionLibrary` |
| `GetFloatCameraVariable` | 从数据表获取浮点变量 | `UBlueprintCameraVariableTableFunctionLibrary` |
| `SetFloatCameraVariable` | 在数据表中设置浮点变量 | `UBlueprintCameraVariableTableFunctionLibrary` |

#### 蓝图摄像机位姿

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTransform` | 获取摄像机位姿的变换 | `UBlueprintCameraPoseFunctionLibrary` |
| `GetEffectiveFieldOfView` | 获取有效视场角 | `UBlueprintCameraPoseFunctionLibrary` |
| `GetSensorAspectRatio` | 获取传感器宽高比 | `UBlueprintCameraPoseFunctionLibrary` |
| `GetAimRay` / `GetAimDir` / `GetTarget` | 获取瞄准射线/方向/目标 | `UBlueprintCameraPoseFunctionLibrary` |
| `MakeCameraPoseFromCineCameraComponent` | 从 CineCamera 创建位姿 | `UBlueprintCameraPoseFunctionLibrary` |

### 使用示例（蓝图描述）

**基本用法 — 激活摄像机组件：**

1. 在角色 Actor 上添加 `GameplayCameraComponentBase` 子类组件
2. 设置组件的 `DefaultPlayer` 为对应玩家索引
3. 设置 `bRunStandaloneCameraSystem = true`（独立运行摄像机系统）
4. 在 BeginPlay 或需要时调用 `ActivateCameraForPlayerController`，传入玩家控制器

**运行时叠加摄像机效果：**

1. 通过组件的 `StartCameraShakeAsset` 节点传入 `UCameraShakeAsset` 资产
2. 返回一个 `FCameraShakeInstanceID`，用于后续停止
3. 需要停止时调用 `StopCameraShakeAsset`，传入实例 ID

**蓝图摄像机节点自定义：**

1. 创建 `UBlueprintCameraNodeEvaluator` 的蓝图子类
2. 重写 `TickCameraNode` 事件，在其中通过 `SetCurrentCameraPose` 修改摄像机位姿
3. 可通过 `GetCurrentCameraPose` 获取当前位姿进行计算
4. 将该蓝图评估器类分配给 `UBlueprintCameraNode` 资产

## C++ 用法

### 头文件引入

```cpp
#include "GameFramework/GameplayCameraComponentBase.h"
#include "GameFramework/GameplayCamerasPlayerCameraManager.h"
#include "Core/CameraAsset.h"
#include "Core/CameraRigAsset.h"
#include "Core/CameraSystemEvaluator.h"
#include "Core/CameraEvaluationContext.h"
#include "BlueprintCameraEvaluationDataRef.h"
#include "BlueprintCameraPose.h"
```

### 基本用法 — 创建摄像机评估上下文并激活

```cpp
// 在组件中创建评估上下文并绑定到玩家控制器
// 来源: Public/GameFramework/GameplayCameraComponentBase.h

// 假设 MyCameraComponent 继承自 UGameplayCameraComponentBase
void AMyActor::SetupCamera()
{
    UGameplayCameraComponentBase* CameraComp = FindComponentByClass<UGameplayCameraComponentBase>();
    if (CameraComp)
    {
        // 为指定玩家控制器激活摄像机
        CameraComp->ActivateCameraForPlayerController(GetController<APlayerController>(), true);
    }
}
```

### 进阶用法 — 摄像机系统评估器

```cpp
// 手动创建和管理摄像机系统评估器
// 来源: Public/Core/CameraSystemEvaluator.h, Public/Core/CameraEvaluationContext.h

using namespace UE::Cameras;

// 创建摄像机系统
FCameraSystemEvaluatorCreateParams CreateParams;
CreateParams.Owner = MyActor;
CreateParams.Role = ECameraSystemEvaluatorRole::Game;

TSharedPtr<FCameraSystemEvaluator> CameraSystem = MakeShared<FCameraSystemEvaluator>();
CameraSystem->Initialize(CreateParams);

// 创建评估上下文
FCameraEvaluationContextInitializeParams ContextParams;
ContextParams.Owner = MyActor;
ContextParams.CameraAsset = MyCameraAsset;  // UCameraAsset*
ContextParams.PlayerController = MyPlayerController;

TSharedRef<FCameraEvaluationContext> EvalContext = MakeShared<FCameraEvaluationContext>();
EvalContext->Initialize(ContextParams);

// 推入上下文栈
CameraSystem->PushEvaluationContext(EvalContext);

// 每帧更新（通常在 Tick 中）
FCameraSystemEvaluationParams EvalParams;
EvalParams.DeltaTime = DeltaTime;

FCameraSystemEvaluationResult EvalResult;
CameraSystem->UpdateCamera(EvalParams, EvalResult);

if (EvalResult.bIsValid)
{
    // 应用摄像机结果
    FMinimalViewInfo ViewInfo;
    EvalResult.CameraPose.GetViewInfo(ViewInfo);
}
```

### 进阶用法 — 蓝图摄像机导演

```cpp
// 在蓝图中实现摄像机导演逻辑
// 来源: Public/Directors/BlueprintCameraDirector.h

// 创建 UBlueprintCameraDirectorEvaluator 的 C++ 子类
UCLASS()
class UMyCameraDirectorEvaluator : public UBlueprintCameraDirectorEvaluator
{
    GENERATED_BODY()

public:
    virtual void ActivateCameraDirector_Implementation(UObject* EvaluationContextOwner, 
        const FBlueprintCameraDirectorActivateParams& Params) override
    {
        // 初始化逻辑
    }

    virtual void RunCameraDirector_Implementation(float DeltaTime, UObject* EvaluationContextOwner,
        const FBlueprintCameraDirectorEvaluationParams& Params) override
    {
        // 每帧决定使用哪个摄像机 rig
        UCameraRigAsset* DesiredRig = DetermineDesiredRig(EvaluationContextOwner);
        if (DesiredRig)
        {
            ActivateCameraRig(DesiredRig);
        }
    }
};
```

## Demo 示例

### 蓝图可摄像机组件

```cpp
// MyGameplayCameraComponent.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameplayCameraComponentBase.h"
#include "MyGameplayCameraComponent.generated.h"

class UCameraAsset;

UCLASS(ClassGroup=Camera, meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyGameplayCameraComponent : public UGameplayCameraComponentBase
{
    GENERATED_BODY()

public:
    UMyGameplayCameraComponent(const FObjectInitializer& ObjectInit);

    /** 要运行的摄像机资产 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category=Camera)
    TObjectPtr<UCameraAsset> CameraAsset;

protected:
    // 重写以提供摄像机资产
    virtual UCameraAsset* OnCreateEvaluationContext() override;
};
```

```cpp
// MyGameplayCameraComponent.cpp
#include "MyGameplayCameraComponent.h"
#include "Core/CameraAsset.h"

UMyGameplayCameraComponent::UMyGameplayCameraComponent(const FObjectInitializer& ObjectInit)
    : Super(ObjectInit)
{
    // 默认独立运行摄像机系统
    bRunStandaloneCameraSystem = true;
}

UCameraAsset* UMyGameplayCameraComponent::OnCreateEvaluationContext()
{
    return CameraAsset;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 摄像机 rig 的标签系统 |
| `EnhancedInput` | 集成增强输入系统 |
| `ObjectTreeGraph` | 编辑器中的节点图可视化 |
| `GameplayCamerasUncookedOnly` | 仅编辑器/未打包时的功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 模式下摄像机变量覆盖失效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 补充和更新部分追踪通道的描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 通用更新（提交信息简短，可能是合并或常规维护） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 格式化日志宏 |

### 维护评价

**活跃维护中。** GameplayCameras 作为 Epic 为 UE5 打造的下一代摄像机系统，持续获得实质性更新和 Bug 修复（最近一次更新在 2026 年 5 月）。近期更新涵盖了 PIE 兼容性修复、编译器警告清理、日志系统迁移等，表明该插件处于积极迭代状态。

需要注意的是：
- **标记为实验性**（`IsExperimentalVersion = true`），API 可能在未来版本发生变化
- 源码规模庞大（729 个文件），属于大型插件，学习曲线较陡
- 创建至今约 6 年，已从实验阶段逐步走向成熟
- 某些 API 存在 `DEPRECATED` 标记（如 `BlueprintCameraDirectorEvaluationParams` 已废弃），说明 API 仍在演进

**推荐使用**：对于需要复杂摄像机逻辑的新项目，强烈推荐使用此系统。对于已有的使用传统 `APlayerCameraManager` 的项目，可以逐步迁移，因为两者可以共存（通过 `GameplayCamerasPlayerCameraManager.StealPlayerController`）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)