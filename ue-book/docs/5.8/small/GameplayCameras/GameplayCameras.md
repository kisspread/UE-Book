# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是一个基于节点图（Node Graph）的数据驱动摄像机系统，旨在替代 Unreal 传统的 `APlayerCameraManager` 硬编码摄像机逻辑方式。它解决了以下核心问题：

1. **可组合性**：传统摄像机系统将行为硬编码在 C++ 中，难以复用和组合。GameplayCameras 通过"摄像机资产（Camera Asset）→ 摄像机配置（Camera Rig）→ 摄像机节点（Camera Node）"的层级结构，让摄像机行为像蓝图一样可视化编辑和复用。
2. **混合栈（Blend Stack）**：内置多层混合栈架构（Base/Global/Visual/Main），支持多个摄像机配置同时运行并通过混合过渡实现平滑切换，无需手写混合逻辑。
3. **参数化**：摄像机配置暴露参数接口（Interface Parameters），支持通过蓝图变量和上下文数据动态驱动摄像机行为，实现运行时灵活调整。
4. **独立运行**：`UGameplayCameraComponentBase` 可以作为独立组件运行摄像机系统，也可与 `AGameplayCamerasPlayerCameraManager` 集成作为全局摄像机管理器。

插件标记为 **实验性**（`IsExperimentalVersion=true`），版本号 0.1，API 可能在未来版本中发生变化。

## 使用场景

- 你在做第三人称动作游戏，需要根据战斗/探索/过场等状态切换不同摄像机行为 → 用 Camera Asset + Camera Director 组织不同场景的摄像机配置
- 你需要摄像机在碰撞墙体时自动拉近，避免穿模 → 用 `UCollisionPushCameraNode`
- 你需要精确控制目标在屏幕上的构图（如电影般的"死区"和"软区"） → 用 `UBaseFramingCameraNode` 系列节点
- 你需要在蓝图中自定义摄像机逻辑，但不想写 C++ → 用 `UBlueprintCameraNode` 或 `UBlueprintCameraDirector`
- 你需要摄像机震动效果 → 用 `UCameraShakeAsset` + `StartCameraShakeAsset` 节点
- 你需要摄像机在场景切换时平滑过渡 → 用 `UCameraRigTransition` 定义过渡条件和混合方式

## 蓝图用法

### 核心节点：摄像机组件

以下节点位于 `UGameplayCameraComponentBase`，是蓝图中控制摄像机的主要入口：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActivateCameraForPlayerIndex` | 为指定玩家索引激活摄像机 | `UGameplayCameraComponentBase` |
| `ActivateCameraForPlayerController` | 为指定玩家控制器激活摄像机 | `UGameplayCameraComponentBase` |
| `GetOutputCameraComponent` | 获取输出摄像机组件（UCineCameraComponent） | `UGameplayCameraComponentBase` |
| `GetInitialResult` | 获取共享的摄像机评估数据 | `UGameplayCameraComponentBase` |
| `GetConditionalResult` | 获取条件摄像机数据（如当前激活的摄像机配置） | `UGameplayCameraComponentBase` |
| `GetEvaluatedCameraRotation` | 获取最后评估的摄像机朝向 | `UGameplayCameraComponentBase` |

### 核心节点：持久层摄像机配置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActivatePersistentBaseCameraRig` | 在基础层激活持久摄像机配置 | `UGameplayCameraComponentBase` / `AGameplayCamerasPlayerCameraManager` |
| `ActivatePersistentGlobalCameraRig` | 在全局层激活持久摄像机配置 | 同上 |
| `ActivatePersistentVisualCameraRig` | 在视觉层激活持久摄像机配置 | 同上 |
| `DeactivateCameraRig` | 停用之前激活的摄像机配置 | 同上 |

### 核心节点：摄像机修改器与震动

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartGlobalCameraModifierRig` | 在全局层启动摄像机修改器 | `UGameplayCameraComponentBase` / `AGameplayCamerasPlayerCameraManager` |
| `StartVisualCameraModifierRig` | 在视觉层启动摄像机修改器 | 同上 |
| `StopCameraModifierRig` | 停止摄像机修改器 | 同上 |
| `StartCameraShakeAsset` | 启动摄像机震动 | 同上 |
| `IsCameraShakeAssetPlaying` | 检查震动是否正在播放 | 同上 |
| `StopCameraShakeAsset` | 停止摄像机震动 | 同上 |

### 核心节点：摄像机动作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartAction` | 启动摄像机动作（如瞄准） | `UGameplayCameraComponentBase` |
| `IsActionRunning` | 检查动作是否运行中 | 同上 |
| `StopAction` | 停止指定动作实例 | 同上 |
| `StopAllActionsOfClass` | 停止某类型的所有动作 | 同上 |

### 核心节点：Player Camera Manager

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StealPlayerController` | 接管玩家控制器的摄像机管理 | `AGameplayCamerasPlayerCameraManager` |
| `ReleasePlayerController` | 恢复原始摄像机管理器 | 同上 |
| `ActivateGameplayCamera` | 在管理器中激活摄像机组件 | 同上 |
| `DeactivateGameplayCamera` | 在管理器中停用摄像机组件 | 同上 |

### 核心节点：蓝图摄像机节点/导演

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TickCameraNode` | 蓝图摄像机节点的主执行回调（覆盖实现） | `UBlueprintCameraNodeEvaluator` |
| `InitializeCameraNode` | 蓝图摄像机节点初始化回调 | 同上 |
| `GetCurrentCameraPose` | 获取当前摄像机姿态 | 同上 |
| `SetCurrentCameraPose` | 设置当前摄像机姿态 | 同上 |
| `RunCameraDirector` | 蓝图摄像机导演的主逻辑（覆盖实现） | `UBlueprintCameraDirectorEvaluator` |
| `ActivateCameraRig` | 在导演中指定本帧激活的摄像机配置 | 同上 |
| `ActivateCameraRigViaProxy` | 通过代理指定摄像机配置 | 同上 |
| `FindEvaluationContextOwnerActor` | 查找评估上下文的所有者 Actor | `UBlueprintCameraDirectorEvaluator` / `UBlueprintCameraNodeEvaluator` |

### 核心节点：摄像机变量操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetBooleanCameraVariable` | 从评估数据中获取布尔变量 | `UBlueprintCameraVariableTableFunctionLibrary` |
| `SetBooleanCameraVariable` | 在评估数据中设置布尔变量 | 同上 |
| `GetFloatCameraVariable` | 获取浮点变量 | 同上 |
| `SetFloatCameraVariable` | 设置浮点变量 | 同上 |
| `GetVector3CameraVariable` | 获取三维向量变量 | 同上 |
| `SetVector3CameraVariable` | 设置三维向量变量 | 同上 |
| `BlendCameraEvaluationData` | 混合两个摄像机评估数据 | `UBlueprintCameraEvaluationDataFunctionLibrary` |

### 使用示例（蓝图描述）

**场景：使用组件运行摄像机配置**

1. 在 Actor 上添加 `UGameplayCameraComponent`（继承自 `UGameplayCameraComponentBase`）
2. 在组件属性中设置 `CameraAsset` 为一个已创建的 Camera Asset
3. 设置 `DefaultPlayer` 为 Player0
4. 设置 `bRunStandaloneCameraSystem = true`
5. 在 BeginPlay 中调用 `ActivateCameraForPlayerIndex(0, true)` 激活摄像机

**场景：使用 Player Camera Manager 切换摄像机**

1. 将游戏的 Player Camera Manager 替换为 `AGameplayCamerasPlayerCameraManager`（通过 `StealPlayerController` 或项目设置）
2. 创建多个包含不同 Camera Rig 的 Actor（每个带 `UGameplayCameraComponent`）
3. 需要切换时调用 `ActivateGameplayCamera(NewCameraComponent, Push)` 实现平滑混合过渡

**场景：蓝图自定义摄像机逻辑**

1. 创建 `UBlueprintCameraNode` 的子蓝图资产
2. 在 `TickCameraNode` 事件中实现自定义逻辑
3. 使用 `GetCurrentCameraPose` 读取当前姿态，自定义计算后用 `SetCurrentCameraPose` 写入
4. 在 Camera Rig 的节点图中引用该蓝图节点

## C++ 用法

### 头文件引入

```cpp
#include "GameFramework/GameplayCameraComponentBase.h"
#include "GameFramework/GameplayCamerasPlayerCameraManager.h"
#include "Core/CameraAsset.h"
#include "Core/CameraRigAsset.h"
#include "Core/CameraNodeEvaluator.h"
#include "Core/CameraEvaluationContext.h"
#include "Core/CameraSystemEvaluator.h"
#include "Directors/BlueprintCameraDirector.h"
```

### 基本用法：创建自定义摄像机组件

```cpp
// 来源: Public/GameFramework/GameplayCameraComponentBase.h
// 自定义摄像机组件，继承 UGameplayCameraComponentBase 并实现 OnCreateEvaluationContext

UCLASS(Blueprintable, ClassGroup=Camera)
class UMyGameplayCameraComponent : public UGameplayCameraComponentBase
{
    GENERATED_BODY()

public:
    UMyGameplayCameraComponent(const FObjectInitializer& ObjectInit)
        : Super(ObjectInit)
    {}

protected:
    // 返回要运行的 Camera Asset
    virtual UCameraAsset* OnCreateEvaluationContext() override
    {
        return MyCameraAsset;
    }

public:
    UPROPERTY(EditAnywhere, Category="Camera")
    TObjectPtr<UCameraAsset> MyCameraAsset;
};

// 使用时：
void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 获取组件并激活
    UMyGameplayCameraComponent* CamComp = FindComponentByClass<UMyGameplayCameraComponent>();
    if (CamComp)
    {
        CamComp->ActivateCameraForPlayerIndex(0, true);
    }
    
    // 运行时激活摄像机震动
    FCameraShakeInstanceID ShakeID = CamComp->StartCameraShakeAsset(
        MyCameraShake, 1.0f, ECameraShakePlaySpace::CameraLocal);
    
    // 激活持久的摄像机配置
    FCameraRigInstanceID RigID = CamComp->ActivatePersistentGlobalCameraRig(MyGlobalCameraRig);
}
```

### 进阶用法：自定义摄像机节点求值器

```cpp
// 来源: Public/Core/CameraNodeEvaluator.h + Public/Nodes/CameraNode.h
// 创建自定义 C++ 摄像机节点

// 节点资产类（数据定义）
UCLASS(meta=(CameraNodeCategories="Transform"))
class UMyFollowCameraNode : public UCameraNode
{
    GENERATED_BODY()

public:
    /** 目标偏移 */
    UPROPERTY(EditAnywhere, Category="Follow")
    FVector3dCameraParameter TargetOffset;

    /** 跟随距离 */
    UPROPERTY(EditAnywhere, Category="Follow")
    FFloatCameraParameter FollowDistance;

protected:
    virtual FCameraNodeEvaluatorPtr OnBuildEvaluator(FCameraNodeEvaluatorBuilder& Builder) const override;
};

// 节点求值器类（执行逻辑）
class FMyFollowCameraNodeEvaluator : public TCameraNodeEvaluator<UMyFollowCameraNode>
{
    UE_DECLARE_CAMERA_NODE_EVALUATOR(GAMEPLAYCAMERAS_API, FMyFollowCameraNodeEvaluator)

protected:
    virtual void OnInitialize(const FCameraNodeEvaluatorInitializeParams& Params, 
                               FCameraNodeEvaluationResult& OutResult) override;
    virtual void OnRun(const FCameraNodeEvaluationParams& Params, 
                        FCameraNodeEvaluationResult& OutResult) override;

private:
    TCameraParameterReader<FVector3d> TargetOffsetReader;
    TCameraParameterReader<float> FollowDistanceReader;
};

void FMyFollowCameraNodeEvaluator::OnInitialize(
    const FCameraNodeEvaluatorInitializeParams& Params, 
    FCameraNodeEvaluationResult& OutResult)
{
    const UMyFollowCameraNode* MyNode = GetCameraNode();
    TargetOffsetReader.Initialize(MyNode->TargetOffset);
    FollowDistanceReader.Initialize(MyNode->FollowDistance);
}

void FMyFollowCameraNodeEvaluator::OnRun(
    const FCameraNodeEvaluationParams& Params, 
    FCameraNodeEvaluationResult& OutResult)
{
    const FVector3d Offset = TargetOffsetReader.GetCurrentValue(OutResult.VariableTable);
    const float Distance = FollowDistanceReader.GetCurrentValue(OutResult.VariableTable);
    
    // 获取上下文中的目标位置
    FVector3d TargetLocation = /* 从评估上下文获取 */;
    
    // 计算并设置摄像机位置
    FVector3d CameraLocation = TargetLocation + Offset - 
        OutResult.CameraPose.GetAimDir() * Distance;
    OutResult.CameraPose.SetLocation(CameraLocation);
    OutResult.CameraPose.SetTargetDistance(Distance);
}
```

### 进阶用法：运行时操作变量表

```cpp
// 来源: Public/Core/CameraVariableTable.h, Public/GameFramework/BlueprintCameraEvaluationDataRef.h
// 通过 C++ 读写摄像机变量

void AMyActor::UpdateCameraData(
    UE::Cameras::FCameraNodeEvaluationResult& Result)
{
    using namespace UE::Cameras;
    
    // 读取变量
    FCameraVariableTable& VarTable = Result.VariableTable;
    
    // 通过变量资产指针读取
    float CurrentFOV = VarTable.GetValue<float>(MyFOVVariable->GetVariableID());
    
    // 通过变量资产对象读取
    FVector3d LookTarget = VarTable.GetValue(MyLookTargetVariable);
    
    // 尝试读取（如果变量不存在返回 false）
    bool bIsAiming = false;
    bool bFound = VarTable.TryGetValue<bool>(MyIsAimingVariable->GetVariableID(), bIsAiming);
    
    // 设置变量值
    VarTable.SetValue<float>(MyFOVVariable->GetVariableID(), 90.0f);
    VarTable.SetValue(MyLookTargetVariable, NewLookTarget);
}
```

## Demo 示例

```cpp
// MyCustomCameraComponent.h
#pragma once

#include "GameFramework/GameplayCameraComponentBase.h"
#include "MyCustomCameraComponent.generated.h"

UCLASS(Blueprintable, ClassGroup=Camera, meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyCustomCameraComponent : public UGameplayCameraComponentBase
{
    GENERATED_BODY()

public:
    UMyCustomCameraComponent(const FObjectInitializer& ObjectInit);

    /** 要运行的摄像机资产 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Camera")
    TObjectPtr<UCameraAsset> CameraAsset;

    /** 是否自动激活 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Camera")
    bool bAutoActivateCamera = true;

protected:
    virtual UCameraAsset* OnCreateEvaluationContext() override;
    virtual void BeginPlay() override;
};
```

```cpp
// MyCustomCameraComponent.cpp
#include "MyCustomCameraComponent.h"

UMyCustomCameraComponent::UMyCustomCameraComponent(const FObjectInitializer& ObjectInit)
    : Super(ObjectInit)
{
    // 使用独立摄像机系统，不依赖外部 Player Camera Manager
    bRunStandaloneCameraSystem = true;
    bAutoActivate = false; // 我们手动控制激活
}

UCameraAsset* UMyCustomCameraComponent::OnCreateEvaluationContext()
{
    return CameraAsset;
}

void UMyCustomCameraComponent::BeginPlay()
{
    Super::BeginPlay();

    if (bAutoActivateCamera && CameraAsset)
    {
        // 为默认玩家激活摄像机
        ActivateCameraForPlayerIndex(
            static_cast<int32>(DefaultPlayer) - static_cast<int32>(EAutoReceiveInput::Player0),
            true);
    }
}
```

## 模块依赖

从 Build.cs 的依赖列表中，去除常见依赖后的独特依赖：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 插件级依赖，支持摄像机节点中的输入处理 |
| `GameplayTags` | 摄像机配置通过 GameplayTag 进行分类和匹配 |
| `GameplayCameras` | 核心 Runtime 模块，包含所有摄像机系统运行时逻辑 |

*注：Editor 模块（`GameplayCamerasEditor`）和 UncookedOnly 模块（`GameplayCamerasUncookedOnly`）为编辑器扩展，包含图表编辑器、资产工厂等。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 模式下摄像机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 添加或更新部分 Trace Channel 的描述 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 插件主体提交（未提供详细说明） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF |

### 维护评价

- **活跃维护**：最近 6 个月内有多次实质性更新（bug 修复、API 改进）
- **实验性状态**：插件标记为 `IsExperimentalVersion=true`，版本号 0.1，API 不保证稳定
- **创建时间**：2020 年 10 月创建，已有约 5 年历史，但一直处于活跃开发中
- **更新频率**：近几个月保持稳定更新节奏，从 commit 内容看主要在修 bug 和优化
- **代码规模**：729 个源文件，属于大型插件，架构复杂且完善
- **推荐使用**：适合项目早期采用（可接受 API 变动），不建议在即将发布的项目中作为核心摄像机系统使用（因实验性标签）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]()（暂无公开文档）
- [测试用例]()（测试文件未在插件目录内找到公开路径）