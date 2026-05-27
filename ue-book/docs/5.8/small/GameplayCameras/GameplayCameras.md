# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 模块化相机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是 UE5 全新的**数据驱动模块化相机系统**，旨在取代传统的 `APlayerCameraManager` + `UCameraComponent` + CameraModifier 的架构。

传统相机系统的核心问题：
- 相机行为用硬编码或蓝图混杂实现，难以复用和维护
- 不同相机状态之间的过渡逻辑散落各处，无法统一管理
- 没有标准化的相机参数数据化方案，各项目各自造轮子
- 相机混合（Blend）系统原始且不支持节点树级别的混合

GameplayCameras 通过以下核心设计解决这些问题：
- **Camera Rig**：相机行为的数据资产单元，由一棵 Camera Node 树驱动，可作为可复用的"相机预设"
- **Camera Asset**：管理多个 Camera Rig 的资产，包含 Camera Director 来决定每帧使用哪个 Rig
- **Blend Stack**：多层（Base/Global/Main/Visual）叠加栈，支持隔离式和叠加式两种混合模式
- **Camera Variables**：类型安全的变量表系统，支持预混合（Pre-blend）和参数覆盖
- **Camera Transitions**：条件驱动的过渡系统，支持中断、冻结、方向反转等高级过渡

## 使用场景

- 你在做第三人称动作游戏，需要肩越镜头 + 锁定目标镜头 + 战斗特写镜头之间平滑过渡 → 用 Camera Rig + Transitions
- 你需要相机震动、瞄准修正（Aim At）等临时叠加效果 → 用 Camera Actions 和 Camera Modifier Rigs
- 你的相机需要自动避障（环境碰撞） → 用 Collision Push Camera Node
- 你需要自定义构图逻辑（如三分法、死区） → 用 Framing Camera Nodes
- 你希望在蓝图中完全自定义相机导演逻辑 → 用 Blueprint Camera Director
- 你需要在多个对象之间切换相机焦点，带过渡混合 → 用 Camera Evaluation Context + Blend Stack
- 你希望相机行为完全由数据资产定义，程序员和策划可以分离工作 → 用 Camera Rig Assets

## 蓝图用法

### 核心组件节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActivateCameraForPlayerIndex` | 为指定玩家激活相机组件 | `UGameplayCameraComponentBase` |
| `ActivateCameraForPlayerController` | 为指定 PlayerController 激活相机组件 | `UGameplayCameraComponentBase` |
| `ActivatePersistentBaseCameraRig` | 在 Base 层激活持久化的 Camera Rig | `UGameplayCameraComponentBase` |
| `ActivatePersistentGlobalCameraRig` | 在 Global 层激活持久化的 Camera Rig | `UGameplayCameraComponentBase` |
| `ActivatePersistentVisualCameraRig` | 在 Visual 层激活持久化的 Camera Rig | `UGameplayCameraComponentBase` |
| `DeactivateCameraRig` | 停止一个 Camera Rig 实例 | `UGameplayCameraComponentBase` |
| `StartGlobalCameraModifierRig` | 在 Global 层启动 Camera Modifier Rig | `UGameplayCameraComponentBase` |
| `StopCameraModifierRig` | 停止 Camera Modifier Rig | `UGameplayCameraComponentBase` |
| `StartCameraShakeAsset` | 播放相机震动资产 | `UGameplayCameraComponentBase` |
| `StopCameraShakeAsset` | 停止相机震动 | `UGameplayCameraComponentBase` |
| `StartAction` | 启动一个 Camera Action（如瞄准修正） | `UGameplayCameraComponentBase` |
| `StopAction` | 停止一个 Camera Action | `UGameplayCameraComponentBase` |
| `GetInitialResult` | 获取共享相机评估数据 | `UGameplayCameraComponentBase` |
| `GetConditionalResult` | 获取特定条件下的相机评估数据 | `UGameplayCameraComponentBase` |
| `GetEvaluatedCameraRotation` | 获取最后一帧评估的相机旋转 | `UGameplayCameraComponentBase` |
| `GetOutputCameraComponent` | 获取输出相机组件（UCineCameraComponent） | `UGameplayCameraComponentBase` |

### 相机管理器节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StealPlayerController` | 接管玩家控制器的相机管理器 | `AGameplayCamerasPlayerCameraManager` |
| `ReleasePlayerController` | 释放之前接管的相机管理器 | `AGameplayCamerasPlayerCameraManager` |
| `ActivateGameplayCamera` | 在管理器的相机系统中激活一个 Gameplay Camera 组件 | `AGameplayCamerasPlayerCameraManager` |
| `DeactivateGameplayCamera` | 停止一个之前激活的组件 | `AGameplayCamerasPlayerCameraManager` |
| `ActivatePersistentBaseCameraRig` | 在 Base 层激活 Camera Rig | `AGameplayCamerasPlayerCameraManager` |
| `ActivatePersistentGlobalCameraRig` | 在 Global 层激活 Camera Rig | `AGameplayCamerasPlayerCameraManager` |
| `ActivatePersistentVisualCameraRig` | 在 Visual 层激活 Camera Rig | `AGameplayCamerasPlayerCameraManager` |
| `DeactivateCameraRig` | 停止 Camera Rig | `AGameplayCamerasPlayerCameraManager` |
| `StartGlobalCameraModifierRig` | 启动 Global 层的 Modifier Rig | `AGameplayCamerasPlayerCameraManager` |
| `StartVisualCameraModifierRig` | 启动 Visual 层的 Modifier Rig | `AGameplayCamerasPlayerCameraManager` |
| `StopCameraModifierRig` | 停止 Modifier Rig | `AGameplayCamerasPlayerCameraManager` |
| `StartCameraShakeAsset` | 播放相机震动 | `AGameplayCamerasPlayerCameraManager` |
| `StopCameraShakeAsset` | 停止相机震动 | `AGameplayCamerasPlayerCameraManager` |

### 相机数据操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCameraPose` / `SetCameraPose` | 获取/设置相机姿态 | `UBlueprintCameraEvaluationDataFunctionLibrary` |
| `BlendCameraEvaluationData` | 在两个相机数据之间插值 | `UBlueprintCameraEvaluationDataFunctionLibrary` |
| `Get*CameraVariable` | 获取各类型相机变量值 | `UBlueprintCameraVariableTableFunctionLibrary` |
| `Set*CameraVariable` | 设置各类型相机变量值 | `UBlueprintCameraVariableTableFunctionLibrary` |
| `GetTransform` | 获取相机姿态变换矩阵 | `UBlueprintCameraPoseFunctionLibrary` |
| `GetEffectiveFieldOfView` | 获取有效视场角 | `UBlueprintCameraPoseFunctionLibrary` |
| `GetAimRay` | 获取相机瞄准射线 | `UBlueprintCameraPoseFunctionLibrary` |
| `GetTarget` | 获取相机目标点 | `UBlueprintCameraPoseFunctionLibrary` |

### 蓝图 Camera Director 节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RunCameraDirector` | 每帧执行的蓝图相机导演逻辑 | `UBlueprintCameraDirectorEvaluator` |
| `ActivateCameraDirector` | 激活回调 | `UBlueprintCameraDirectorEvaluator` |
| `DeactivateCameraDirector` | 停用回调 | `UBlueprintCameraDirectorEvaluator` |
| `ActivateCameraRig` | 指定一个 Camera Rig 本帧激活 | `UBlueprintCameraDirectorEvaluator` |
| `ActivateCameraRigViaProxy` | 通过代理指定 Camera Rig 激活 | `UBlueprintCameraDirectorEvaluator` |
| `ResolveCameraRigProxy` | 解析 Camera Rig 代理 | `UBlueprintCameraDirectorEvaluator` |
| `FindEvaluationContextOwnerActor` | 查找评估上下文的拥有 Actor | `UBlueprintCameraDirectorEvaluator` |

### 蓝图 Camera Node 节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeCameraNode` | 节点初始化回调 | `UBlueprintCameraNodeEvaluator` |
| `TickCameraNode` | 每帧执行的节点逻辑 | `UBlueprintCameraNodeEvaluator` |
| `GetCurrentCameraPose` | 获取当前相机姿态 | `UBlueprintCameraNodeEvaluator` |
| `SetCurrentCameraPose` | 设置当前相机姿态 | `UBlueprintCameraNodeEvaluator` |
| `SetDefaultOwningCameraRigParameters` | 设置所属 Camera Rig 的默认参数 | `UBlueprintCameraNodeEvaluator` |
| `GetPlayerController` | 获取关联的 PlayerController | `UBlueprintCameraNodeEvaluator` |

### 使用示例（蓝图描述）

**场景1：在第三人称角色上使用 Gameplay Camera Component**

1. 在角色 Actor 上添加 `UGameplayCameraComponentBase` 的子类组件
2. 组件属性面板中：
   - `DefaultPlayer` 设为 Player0
   - `bRunStandaloneCameraSystem` 设为 true（独立运行相机系统）
   - `bSetControlRotationWhenViewTarget` 设为 true（将相机旋转同步到控制器旋转）
3. 在 EventGraph 中，BeginPlay 后调用 `ActivateCameraForPlayerIndex(0, true)`
4. 如果需要运行时切换不同的 Camera Rig，调用 `ActivatePersistentMainCameraRig(MyCameraRigAsset)`

**场景2：使用 Blueprint Camera Director 自定义相机逻辑**

1. 创建 `UBlueprintCameraDirector` 子类（蓝图类）
2. 设置 `CameraDirectorEvaluatorClass` 为你创建的 `UBlueprintCameraDirectorEvaluator` 蓝图子类
3. 在该蓝图子类的 `RunCameraDirector` 事件中实现自定义逻辑：
   - 调用 `ActivateCameraRig(MyCameraRig)` 指定本帧使用的 Camera Rig
   - 调用 `ActivatePersistentBaseCameraRig` 设置底层始终运行的 Rig
4. 在 Camera Asset 资产中将该 Director 设为 `CameraDirector`

**场景3：在蓝图中修改相机变量数据**

1. 从 Camera Component 或 Camera Director 获取 `FBlueprintCameraEvaluationDataRef`
2. 调用 `GetFloatCameraVariable` 读取变量值
3. 调用 `SetFloatCameraVariable` 写入新值
4. 变量会自动在 Camera Rig 的节点树中被读取

## C++ 用法

### 头文件引入

```cpp
#include "GameFramework/GameplayCameraComponentBase.h"
#include "GameFramework/GameplayCamerasPlayerCameraManager.h"
#include "Core/CameraSystemEvaluator.h"
#include "Core/CameraRigAsset.h"
#include "Core/CameraAsset.h"
#include "Core/CameraVariableTable.h"
#include "Core/CameraContextDataTable.h"
#include "Core/CameraNodeEvaluator.h"
#include "BlueprintCameraDirector.h"
```

### 基本用法：创建独立相机系统评估器

基于 `FCameraSystemEvaluator` 的 API 摘自源码中 `CameraSystemEvaluator.h`。

```cpp
#include "Core/CameraSystemEvaluator.h"
#include "Core/CameraEvaluationContext.h"
#include "Core/CameraAsset.h"

using namespace UE::Cameras;

// 创建相机系统评估器
TSharedPtr<FCameraSystemEvaluator> CameraSystem = MakeShared<FCameraSystemEvaluator>();
CameraSystem->Initialize(MyOwnerObject);

// 创建评估上下文并推入相机系统
FCameraEvaluationContextInitializeParams ContextParams;
ContextParams.Owner = MyActor;
ContextParams.CameraAsset = MyCameraAsset;
ContextParams.PlayerController = MyPlayerController;

TSharedRef<FCameraEvaluationContext> Context = MakeShared<FCameraEvaluationContext>(ContextParams);
CameraSystem->PushEvaluationContext(Context);

// 每帧更新相机系统
FCameraSystemEvaluationParams EvalParams;
EvalParams.DeltaTime = DeltaTime;

FCameraSystemEvaluationResult EvalResult;
CameraSystem->Evaluate(EvalParams, EvalResult);

// 从结果中获取 FMinimalViewInfo 应用到相机
FMinimalViewInfo ViewInfo;
EvalResult.CameraPose.GetViewInfo(ViewInfo);
```

### 基本用法：使用 Gameplay Camera Component

基于 `UGameplayCameraComponentBase` 的 API 摘自 `GameplayCameraComponentBase.h`。

```cpp
// 获取组件上的评估上下文
auto EvalContext = MyCameraComponent->GetEvaluationContext();

// 激活相机给指定玩家
MyCameraComponent->ActivateCameraForPlayerController(MyPlayerController, true);

// 在不同层激活 Camera Rig
FCameraRigInstanceID RigInstance = MyCameraComponent->ActivatePersistentMainCameraRig(MyCameraRigAsset);

// 停止一个 Camera Rig
MyCameraComponent->DeactivateCameraRig(RigInstance, /*bImmediately=*/false);

// 播放相机震动
FCameraShakeInstanceID ShakeID = MyCameraComponent->StartCameraShakeAsset(
    MyCameraShakeAsset, 
    1.0f,  // ShakeScale
    ECameraShakePlaySpace::CameraLocal
);

// 检查震动是否仍在播放
bool bPlaying = MyCameraComponent->IsCameraShakeAssetPlaying(ShakeID);

// 启动 Camera Action
FCameraActionInstanceID ActionID = MyCameraComponent->StartAction(MyCameraAction);
bool bRunning = MyCameraComponent->IsActionRunning(ActionID);
MyCameraComponent->StopAction(ActionID);
```

### 基本用法：使用 Player Camera Manager

基于 `AGameplayCamerasPlayerCameraManager` 的 API 摘自 `GameplayCamerasPlayerCameraManager.h`。

```cpp
// 接管玩家控制器
MyCameraManager->StealPlayerController(MyPlayerController);

// 激活一个 Gameplay Camera 组件
MyCameraManager->ActivateGameplayCamera(MyCameraComponent, EGameplayCameraComponentActivationMode::Push);

// 停用 Gameplay Camera 组件
MyCameraManager->DeactivateGameplayCamera(MyCameraComponent, true);

// 在管理层激活 Camera Rig
FCameraRigInstanceID RigID = MyCameraManager->ActivatePersistentBaseCameraRig(MyRig);

// 用完后释放玩家控制器
MyCameraManager->ReleasePlayerController();
```

### 进阶用法：操作相机变量表

基于 `FCameraVariableTable` 的 API 摘自 `CameraVariableTable.h`。

```cpp
#include "Core/CameraVariableTable.h"
#include "Core/CameraVariableAssets.h"

using namespace UE::Cameras;

// 从评估上下文获取初始结果中的变量表
FCameraNodeEvaluationResult& InitialResult = EvalContext->GetInitialResult();
FCameraVariableTable& VarTable = InitialResult.VariableTable;

// 设置一个浮点变量
UFloatCameraVariable* SpeedVariable; // 资产引用
VarTable.SetValue<float>(SpeedVariable->GetVariableID(), 1500.0f);

// 读取变量
float Speed = VarTable.GetValue<float>(SpeedVariable->GetVariableID(), 1000.0f);

// 检查变量是否被写入
bool bWritten = VarTable.ContainsValue(SpeedVariable->GetVariableID());

// 变量表支持混合：OverrideChanged 只覆盖已改变的变量
FCameraVariableTable TargetTable;
TargetTable.OverrideChanged(VarTable, ECameraVariableTableFilter::ChangedOnly);
```

### 进阶用法：操作上下文数据表

基于 `FCameraContextDataTable` 的 API 摘自 `CameraContextDataTable.h`。

```cpp
#include "Core/CameraContextDataTable.h"

using namespace UE::Cameras;

FCameraContextDataTable& DataTable = InitialResult.ContextDataTable;

// 设置/获取命名数据
FCameraContextDataID TargetNameID; // 由构建过程生成
DataTable.SetNameData(TargetNameID, FName("EnemyBoss"));
FName TargetName = DataTable.GetNameData(TargetNameID);

// 设置/获取对象引用
DataTable.SetObjectData(TargetActorID, MyTargetActor);
UObject* TargetObj = DataTable.GetObjectData(TargetActorID);

// 模板化的类型安全访问
TConstArrayView<FName> NamesArray = DataTable.TryGetArrayData<FName>(ArrayDataID);

// 检查是否本帧被写入
bool bWrittenThisFrame = DataTable.IsValueWrittenThisFrame(TargetNameID);
```

## Demo 示例

一个完整的最小示例：创建一个自定义 Camera Rig，在 C++ 中运行并输出最终相机姿态。

### CustomCameraRigDemo.h

```cpp
// CustomCameraRigDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Core/CameraSystemEvaluator.h"
#include "Core/CameraEvaluationContext.h"
#include "Core/CameraAsset.h"
#include "Core/CameraRigAsset.h"
#include "ACustomCameraDemoActor.generated.h"

UCLASS()
class ACustomCameraDemoActor : public AActor
{
	GENERATED_BODY()

public:
	ACustomCameraDemoActor();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

	/** 要运行的相机资产 */
	UPROPERTY(EditAnywhere, Category="Camera")
	TObjectPtr<UCameraAsset> CameraAsset;

	/** 要运行的独立相机 Rig */
	UPROPERTY(EditAnywhere, Category="Camera")
	TObjectPtr<UCameraRigAsset> CameraRig;

private:
	/** 相机系统评估器 */
	TSharedPtr<UE::Cameras::FCameraSystemEvaluator> CameraSystem;

	/** 评估上下文 */
	TSharedPtr<UE::Cameras::FCameraEvaluationContext> EvalContext;
};
```

### CustomCameraRigDemo.cpp

```cpp
// CustomCameraRigDemo.cpp
#include "CustomCameraRigDemo.h"

#include "Core/CameraSystemEvaluator.h"
#include "Core/CameraEvaluationContext.h"
#include "Core/CameraAsset.h"
#include "Core/CameraRigAsset.h"
#include "Core/CameraNodeEvaluator.h"

using namespace UE::Cameras;

ACustomCameraDemoActor::ACustomCameraDemoActor()
{
	PrimaryActorTick.bCanEverTick = true;
}

void ACustomCameraDemoActor::BeginPlay()
{
	Super::BeginPlay();

	// 1. 创建相机系统评估器
	CameraSystem = MakeShared<FCameraSystemEvaluator>();
	CameraSystem->Initialize(this);

	// 2. 创建评估上下文
	FCameraEvaluationContextInitializeParams ContextParams;
	ContextParams.Owner = this;
	ContextParams.CameraAsset = CameraAsset;
	// ContextParams.PlayerController = GetWorld()->GetFirstPlayerController(); // 如有需要

	EvalContext = MakeShared<FCameraEvaluationContext>(ContextParams);

	// 3. 将上下文推入相机系统
	CameraSystem->PushEvaluationContext(EvalContext.ToSharedRef());
}

void ACustomCameraDemoActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (!CameraSystem.IsValid())
	{
		return;
	}

	// 4. 每帧评估相机系统
	FCameraSystemEvaluationParams EvalParams;
	EvalParams.DeltaTime = DeltaTime;

	FCameraSystemEvaluationResult EvalResult;
	CameraSystem->Evaluate(EvalParams, EvalResult);

	// 5. 使用评估结果
	if (EvalResult.bIsValid)
	{
		FMinimalViewInfo ViewInfo;
		EvalResult.CameraPose.GetViewInfo(ViewInfo);

		// 可以将 ViewInfo 应用到场景视图或进行其他处理
		UE_LOG(LogTemp, Log, TEXT("Camera Location: %s, Rotation: %s, FOV: %.2f"),
			*ViewInfo.Location.ToString(),
			*ViewInfo.Rotation.ToString(),
			ViewInfo.FOV);
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 增强输入系统（.uplugin 中声明为插件依赖） |
| `GameplayTags` | Gameplay Tags 标签系统（Camera Rig 支持标签） |
| `GameplayAbilities` | （可选）与 GAS 集成相关 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 中相机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 添加或更新部分 Trace Channel 的描述 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | GameplayCameras 通用改动（commit message 过于简短） |
| 2026-04-14 | `35e06df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |

### 维护评价

GameplayCameras 是一个**活跃维护中的实验性插件**，最近数月（2026年4-5月）仍有持续的功能修复和代码质量改进。该插件自 2020 年创建以来持续开发，是 Epic 对 UE 相机系统现代化重构的核心项目。

**优势**：
- 源码规模庞大（729 个源文件），架构成熟
- 提供完整的蓝图和 C++ 双向接口
- 层级化相机管理（Base/Global/Main/Visual 层）设计精良
- 支持运行时热编辑（Live Edit）

**注意事项**：
- 标记为 `IsExperimentalVersion=true`，API 可能在未来版本中发生变化
- `Installed=false` 且 `EnabledByDefault=true`，说明它是引擎内置但非正式发布的状态
- 存在大量 `_DEPRECATED` 后缀的属性和方法，表明 API 正在迭代优化
- 依赖 `EnhancedInput` 插件

**推荐程度**：如果你的项目需要复杂的相机系统且能接受实验性 API 变动，强烈推荐使用。它是 UE 相机系统的未来方向。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]()（.uplugin 中 DocsURL 为空，暂无官方文档）