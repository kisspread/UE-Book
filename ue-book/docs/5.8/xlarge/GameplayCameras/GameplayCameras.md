# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏相机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Editor), `GameplayCamerasUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

---

## 用途

GameplayCameras 是 UE5 全新的模块化、数据驱动相机系统，用于替代和扩展传统的 `CameraShake`、`PlayerCameraManager` 以及硬编码相机方案。

**解决的核心问题：**

1. **相机行为可组合**：将相机逻辑拆分为独立的"相机节点"（`UCameraNode`），通过节点树组合出复杂相机行为，类似材质图的思路
2. **数据驱动**：相机配置存储在资产（`UCameraRigAsset`、`UCameraAsset`）中，设计师可在编辑器中调整，无需修改代码
3. **平滑过渡**：内置混合栈（Blend Stack），支持相机在不同状态间平滑切换
4. **参数化接口**：通过"接口参数"（Interface Parameters）暴露可配置项，支持蓝图和 C++ 侧覆盖
5. **Actions 系统**：运行时动态插入相机行为（如锁定瞄准目标），无需预配置

**与传统方案的区别：**

| 传统方案 | GameplayCameras |
|---|---|
| `PlayerCameraManager` + `CameraModifier` | 模块化节点树 + 资产驱动 |
| 硬编码相机逻辑 | 设计师可通过蓝图图编辑 |
| 无内置过渡系统 | 混合栈 + 过渡资产 |
| 难以组合 | 节点树 + 相机 Rig 组合 |
| 无 Sequencer 集成 | MovieScene 组件集成 |

---

## 使用场景

- **第三人称 / 第一人称游戏**：需要根据游戏状态（探索、战斗、过场）动态切换相机行为
- **锁敌系统**：运行时通过 `UAimAtActorCameraAction` 将相机对准目标
- **电影化过场**：通过 Sequencer 集成（MovieScene 组件）控制相机
- **多相机层**：Main 层处理基础行为，叠加层添加抖动、聚焦等效果
- **设计师友好**：希望在不修改 C++ 的情况下调整相机参数

---

## 核心概念

### 资产层次

```
UCameraAsset (相机资产)
├── UCameraDirector (导演) - 决定当前运行哪个相机 Rig
├── UCameraRigAsset[] (相机 Rig) - 一组相机节点
│   ├── UCameraNode[] (相机节点) - 最小执行单元
│   └── FCameraObjectInterface (接口) - 暴露的参数
└── UCameraRigTransition[] (过渡) - Rig 间的切换方式
```

### 运行时架构

```
FCameraSystemEvaluator (系统求值器)
└── FBlendStackCameraNodeEvaluator (混合栈)
    ├── FBlendStackRootCameraNodeEvaluator (条目 1) → UCameraRigAsset
    ├── FBlendStackRootCameraNodeEvaluator (条目 2) → UCameraRigAsset
    └── ...自动混合过渡
```

### 关键类

| 类 | 用途 |
|---|---|
| `UCameraAsset` | 顶层相机资产，包含导演 + Rig + 接口 |
| `UCameraRigAsset` | 一个可复用的相机节点树 |
| `UCameraDirector` | 决定哪个 Rig 在何时运行（子类实现） |
| `UCameraNode` | 节点树中的节点基类 |
| `FCameraSystemEvaluator` | 运行时求值入口 |
| `UBlendStackCameraNode` | 混合栈，管理 Rig 的叠加与过渡 |
| `UCameraAction` | 运行时可插入的相机行为 |

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TargetActor` | 锁定瞄准的目标 Actor | `UAimAtActorCameraAction` |
| `TargetSocketName` | 目标 Actor 的 Socket 名 | `UAimAtActorCameraAction` |
| `TargetBoneName` | 目标 Actor 的骨骼名 | `UAimAtActorCameraAction` |
| `TargetLocation` | 瞄准的世界坐标 | `UAimAtCameraAction` |
| `Interpolator` | 瞄准时使用的插值器 | `UBaseAimAtCameraAction` |
| `LockOnPolicy` | 锁定策略（锁定/脱锁） | `UBaseAimAtCameraAction` |
| `TargetFraming` | 屏幕空间的聚焦点（0-1） | `UBaseAimAtCameraAction` |

### 参数覆盖

通过 `FCameraAssetReference` 在蓝图中覆盖相机参数：

1. 持有 `FCameraAssetReference` 属性（BlueprintType 可序列化）
2. 设置相机资产引用
3. 通过 `Parameters` 的可覆盖属性袋覆盖接口参数
4. 系统在运行时自动应用覆盖值

---

## C++ 用法

### 头文件引入

```cpp
#include "Core/CameraAsset.h"
#include "Core/CameraRigAsset.h"
#include "Core/CameraDirector.h"
#include "Core/CameraSystemEvaluator.h"
#include "Core/BlendStackCameraNode.h"
#include "Actions/AimAtActorCameraAction.h"
```

### 基本用法：创建自定义相机导演

`UCameraDirector` 是决定相机行为的核心抽象。你需要子类化它来实现自定义逻辑。

```cpp
// MyGameCameraDirector.h
#pragma once

#include "Core/CameraDirector.h"
#include "MyGameCameraDirector.generated.h"

UCLASS()
class UMyGameCameraDirector : public UCameraDirector
{
    GENERATED_BODY()

protected:
    virtual FCameraDirectorEvaluatorPtr OnBuildEvaluator(
        FCameraDirectorEvaluatorBuilder& Builder) const override;

    virtual void OnGatherRigUsageInfo(
        FCameraDirectorRigUsageInfo& UsageInfo) const override;

public:
    UPROPERTY(EditAnywhere, Category="Camera")
    TObjectPtr<UCameraRigAsset> ExploreRig;

    UPROPERTY(EditAnywhere, Category="Camera")
    TObjectPtr<UCameraRigAsset> CombatRig;
};
```

### 使用相机参数

相机参数通过 `FCameraVariableTable` 和 `FCameraContextDataTable` 在求值器间传递。

```cpp
// 读取双精度参数（如 Yaw, Pitch）
FDoubleCameraParameter YawParam;
double CurrentYaw = YawParam.GetDefault();  // 获取默认值
// 在求值器中通过变量表获取实际值

// 读取向量参数
FVector3dCameraParameter OffsetParam;
FVector3d CurrentOffset = OffsetParam.GetDefault();

// 内置变量定义
const FBuiltInCameraVariables& BuiltInVars = FBuiltInCameraVariables::Get();
const FCameraVariableDefinition& YawDef = BuiltInVars.YawDefinition;
const FCameraVariableDefinition& ControlRotationDef = BuiltInVars.ControlRotationDefinition;
```

### 使用相机 Actions（瞄准系统）

```cpp
// 在游戏代码中创建瞄准 Action
UAimAtActorCameraAction* AimAction = NewObject<UAimAtActorCameraAction>();
AimAction->TargetActor = SomeEnemyActor;
AimAction->TargetSocketName = FName("head");
AimAction->Interpolator = SomeInterpolator;
AimAction->LockOnPolicy = EAimAtCameraActionLockOnPolicy::KeepLock;
AimAction->TargetFraming = FVector2D(0.5, 0.3); // 屏幕上方 1/3 处
AimAction->LockOnAngleTolerance = 0.05f;

// 通过 FCameraSystemEvaluator 提交 Action（具体 API 见求值器文档）
```

### 应用相机参数覆盖

```cpp
// FCameraAssetReference 用法
FCameraAssetReference CameraRef(MyCameraAsset);
CameraRef.RebuildParametersIfNeeded();

// 覆盖特定参数
const FGuid& ParamGuid = /* 从接口参数获取 */;
CameraRef.SetParameterOverridden(ParamGuid, true);

// 在求值时应用
FCameraNodeEvaluationResult Result;
CameraRef.ApplyParameterOverrides(Result, /*bDrivenOnly=*/false);
```

### 构建相机资产（编辑器 / Cook）

```cpp
#include "Build/CameraAssetBuilder.h"
#include "Build/CameraBuildContext.h"
#include "Build/CameraBuildLog.h"

FCameraBuildLog BuildLog;
FCameraBuildContext BuildContext(BuildLog, ECameraBuildReason::UserAction);
FCameraAssetBuilder Builder(BuildContext);
Builder.BuildCamera(MyCameraAsset, /*bBuildReferencedAssets=*/true);

// 检查构建结果
if (BuildLog.HasErrors()) {
    for (const FCameraBuildLogMessage& Msg : BuildLog.GetMessages()) {
        UE_LOG(LogCameraSystem, Error, TEXT("%s"), *Msg.ToString());
    }
}
```

来源：`Public/Build/CameraAssetBuilder.h`

### 使用 Camera Context Data

上下文数据用于非混合类型的数据传递（Name、String、Enum、Struct、Object 等）。

```cpp
// 在求值器中读取上下文数据
FCameraContextDataTable ContextData;
// 初始化后...
const FName& SomeName = ContextData.GetNameData(DataID);
UObject* SomeObject = ContextData.GetObjectData(DataID);

// 使用类型安全的读取器
TCameraContextDataReader<FName> NameReader;
NameReader.Initialize(SomeNameParameter);
FName Value = NameReader.Get(ContextDataTable);
```

来源：`Public/Core/CameraContextDataReader.h`

---

## 模块依赖

从 `Public/Core/*.h` 和 `Build.cs` 分析：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 输入轴绑定（相机节点中使用增强输入 Action） |
| `StructUtils` | 属性袋（`FInstancedPropertyBag`、`FInstancedOverridablePropertyBag`），用于相机参数系统 |
| `MovieScene` / `MovieSceneEntitySystem` | Sequencer 集成，相机参数在动画中的驱动 |

> 注意：`EnhancedInput` 是通过 `.uplugin` 的 `Plugins` 依赖声明的（而非模块依赖）。

---

## 子模块文档

本插件为 xlarge 规模（729 源文件），按功能拆分如下：

| 子模块 | 说明 | 核心类 |
|---|---|---|
| [Build 系统](Build.md) | 相机资产的构建、验证、日志 | `FCameraAssetBuilder`, `FCameraRigAssetBuilder`, `FCameraBuildLog` |
| [Blend Stack](BlendStack.md) | 混合栈管理相机 Rig 的叠加与过渡 | `UBlendStackCameraNode`, `FBlendStackCameraNodeEvaluator` |
| [Camera Assets](CameraAssets.md) | 相机资产、Rig 资产、引用与接口 | `UCameraAsset`, `UCameraRigAsset`, `FCameraAssetReference` |
| [Camera Variables](CameraVariables.md) | 变量表与上下文数据表 | `FCameraVariableTable`, `FCameraContextDataTable`, `FBuiltInCameraVariables` |
| [Camera Actions](CameraActions.md) | 运行时相机行为（瞄准、自定义） | `UAimAtActorCameraAction`, `UAimAtCameraAction`, `UCameraAction` |
| [Camera Directors](CameraDirectors.md) | 相机导演与求值器 | `UCameraDirector`, `FCameraDirectorEvaluator`, `FCameraSystemEvaluator` |

---

## 维护状态

### 近期更新

```
- 2026-04-14 35e60df1 Migrate UE_LOG to UE_LOGF — 例行日志宏迁移
- 2026-04-13 6f1ea925 State Tree: Updated state tree reference struct details — 非本插件直接改动
- 2026-04-08 81eea83d [ContentBrowser] New Add Menu Gameplay Menu — 非本插件直接改动
- 2026-03-03 76a32825 [PostProcessing] Replace FilmGrainTexelSize with float2 FilmGrainScale — 非本插件直接改动
- 2026-03-03 ea1a72ff Cameras: make playback mode only affect whether a GPC component writes to the output — 相机系统功能调整
```

### 维护评价

- **创建时间**：2026-03-03，极其年轻（约 0 年）
- **版本号**：0.1（VersionName），处于早期开发阶段
- **实验性标记**：`IsExperimentalVersion = true`，尚未稳定
- **更新频率**：创建后有少量更新，主要是编译兼容性修复和跨插件调整
- **代码规模**：729 个源文件，架构完整，表明是 Epic 重点投入的新系统
- **推荐程度**：⚠️ **谨慎使用**。作为实验性插件，API 可能在后续版本中发生重大变化。适合早期探索和实验性项目，不建议用于需要长期稳定的商业项目。关注 UE5 后续版本的移除实验性标记。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- 官方文档（暂无，DocsURL 为空）