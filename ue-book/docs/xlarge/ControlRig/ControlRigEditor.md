# Control Rig

> Framework for animation driven by user controls.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、形状资产） |
| 模块 | `ControlRig` (Runtime), `ControlRigDeveloper` (Runtime), `ControlRigEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-02-08 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig) | |

## 用途

ControlRig 是 UE5 中最核心的程序化动画框架，解决的核心问题是：**如何通过用户定义的控制器（Controls）来驱动骨骼动画**。

它不仅仅是一个简单的 FK/IK 解算器，而是一个完整的动画创作系统，包含：

- **RigVM 虚拟机驱动**：基于节点图的动画逻辑编排，支持运行时求值
- **层级式控制器系统**：通过 Rig Hierarchy 管理骨骼、控制器、Null 等元素的父子关系
- **Sequencer 深度集成**：在 Sequencer 中对控制器进行关键帧动画创作、空间切换、约束烘焙
- **蓝图编辑器**：可视化节点图编辑器，用于构建自定义 Rig 逻辑
- **模块化 Rig**：支持将多个 Rig 模块组合成复杂的动画系统
- **约束系统**：内置父子约束、目标约束、旋转约束等，支持烘焙到关键帧

ControlRig 存在的意义是替代传统的纯骨骼动画工作流，让动画师和程序员能够通过程序化方式创建、编辑和驱动动画，特别适合需要运行时动态调整的动画场景（如 IK、物理混合、程序化动画等）。

## 使用场景

- 你需要为角色创建自定义的 FK/IK 控制器 → 用 ControlRig 构建 Rig 蓝图
- 你需要在 Sequencer 中对动画进行精细的关键帧编辑 → 用 ControlRig 的 Sequencer 集成
- 你需要运行时动态驱动骨骼（如瞄准 IK、脚步 IK）→ 用 ControlRig 的运行时求值
- 你需要将多个动画模块组合成复杂系统 → 用 Modular Rig 功能
- 你需要在动画之间进行约束和空间切换 → 用 ControlRig 的约束和空间通道系统
- 你需要批量烘焙约束动画到关键帧 → 用 ConstraintBaker 工具

## 子模块文档

本插件规模为 xlarge（1240+ 源文件），按模块拆分如下：

| 子模块 | 类型 | 说明 |
|---|---|---|
| [ControlRig](ControlRig.md) | Runtime | 核心运行时模块：RigVM 求值、层级管理、控制器、约束 |
| [ControlRigDeveloper](ControlRigDeveloper.md) | Runtime | 开发者工具模块：蓝图编译、节点注册、资产工厂 |
| [ControlRigEditor](ControlRigEditor.md) | Runtime | 编辑器集成模块：Sequencer 工具、编辑模式、蓝图编辑器 |

## 蓝图用法

### 核心节点（编辑器蓝图库）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateNewControlRigAsset` | 在项目中创建新的 Control Rig 资产 | `UControlRigBlueprintFactory` |
| `CreateControlRigFromSkeletalMeshOrSkeleton` | 基于骨骼网格体或骨架创建 Control Rig | `UControlRigBlueprintFactory` |
| `CastToControlRigBlueprint` | 将对象安全转换为 ControlRigBlueprint | `UControlRigBlueprintEditorLibrary` |
| `SetPreviewMesh` | 设置 Control Rig 蓝图的预览网格体 | `UControlRigBlueprintEditorLibrary` |
| `GetPreviewMesh` | 获取 Control Rig 蓝图的预览网格体 | `UControlRigBlueprintEditorLibrary` |
| `GetHierarchy` | 获取 Control Rig 的层级对象 | `UControlRigBlueprintEditorLibrary` |
| `GetHierarchyController` | 获取层级控制器 | `UControlRigBlueprintEditorLibrary` |
| `GetAvailableRigUnits` | 获取所有可用的 Rig 单元结构体 | `UControlRigBlueprintEditorLibrary` |
| `GetAvailableRigModules` | 获取所有可用的 Rig 模块描述 | `UControlRigBlueprintEditorLibrary` |
| `GetCurrentlyOpenRigBlueprints` | 获取当前打开的所有 Rig 蓝图 | `UControlRigBlueprintEditorLibrary` |
| `RequestControlRigInit` | 请求重新初始化 Control Rig | `UControlRigBlueprintEditorLibrary` |

### Sequencer 编辑器库

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetVisibleControlRigs` | 获取场景中所有可见的 Control Rig | `UControlRigSequencerEditorLibrary` |
| `GetControlRigs` | 获取关卡序列中的所有 Control Rig 及其绑定 | `UControlRigSequencerEditorLibrary` |

### 使用示例（蓝图描述）

**创建 Control Rig 资产**：
1. 使用 `CreateNewControlRigAsset` 节点，传入目标包路径
2. 可选设置 `bModularRig=true` 创建模块化 Rig
3. 返回的 `UControlRigBlueprint` 可直接在编辑器中打开编辑

**从骨骼创建 Control Rig**：
1. 选中一个 SkeletalMesh 或 Skeleton 资产
2. 使用 `CreateControlRigFromSkeletalMeshOrSkeleton` 节点传入选中对象
3. 系统自动基于骨骼层级创建对应的控制器

## C++ 用法

### 头文件引入

```cpp
// 核心运行时
#include "ControlRig.h"
#include "Rigs/RigHierarchy.h"

// 编辑器工具
#include "ControlRigBlueprintFactory.h"
#include "ControlRigBlueprintEditorLibrary.h"
#include "ControlRigSequencerEditorLibrary.h"

// Sequencer 集成
#include "Sequencer/EditModeAnimationUtil.h"
#include "Tools/ControlRigSnapper.h"
#include "Tools/ConstraintBaker.h"
```

### 基本用法：创建 Control Rig 资产

```cpp
// 通过工厂创建新的 Control Rig 资产
// 来源: ControlRigBlueprintFactory.h
UControlRigBlueprint* RigBlueprint = UControlRigBlueprintFactory::CreateNewControlRigAsset(
    TEXT("/Game/Characters/MyRig"),  // 包路径
    false                             // bModularRig
);

// 基于现有骨骼网格体创建
UControlRigBlueprint* RigFromMesh = UControlRigBlueprintFactory::CreateControlRigFromSkeletalMeshOrSkeleton(
    MySkeletalMesh,  // USkeletalMesh* 或 USkeleton*
    false             // bModularRig
);
```

### 基本用法：访问 Control Rig 蓝图属性

```cpp
// 来源: ControlRigBlueprintEditorLibrary.h
// 设置预览网格体
UControlRigBlueprintEditorLibrary::SetPreviewMesh(RigBlueprint, PreviewSkeletalMesh);

// 获取层级
URigHierarchy* Hierarchy = UControlRigBlueprintEditorLibrary::GetHierarchy(RigBlueprint);
URigHierarchyController* Controller = UControlRigBlueprintEditorLibrary::GetHierarchyController(RigBlueprint);

// 获取所有可用的 Rig 单元
TArray<UStruct*> AvailableUnits = UControlRigBlueprintEditorLibrary::GetAvailableRigUnits();
```

### 进阶用法：约束烘焙

```cpp
// 来源: ConstraintBaker.h
// 烘焙单个约束
FConstraintBaker::Bake(
    World,
    TransformConstraint,        // UTickableTransformConstraint*
    Sequencer,                  // TSharedPtr<ISequencer>
    BakeSettings,               // TOptional<FBakingAnimationKeySettings>
    Frames                      // TOptional<TArray<FFrameNumber>>
);

// 批量烘焙多个约束
TArray<UTickableTransformConstraint*> Constraints;
FBakingAnimationKeySettings Settings;
FConstraintBaker::BakeMultiple(World, Constraints, Sequencer, Settings);
```

### 进阶用法：Snapping 工具

```cpp
// 来源: ControlRigSnapper.h
FControlRigSnapper Snapper;

// 配置子对象（要被 snap 的）
FControlRigSnapperSelection Children;
FControlRigForWorldTransforms ChildRig;
ChildRig.ControlRig = MyControlRig;
ChildRig.ControlNames.Add(TEXT("LeftHand"));
Children.ControlRigs.Add(ChildRig);

// 配置父对象（snap 目标）
FControlRigSnapperSelection Parent;
FActorForWorldTransforms ParentActor;
ParentActor.Actor = TargetActor;
Parent.Actors.Add(ParentActor);

// 执行 snap
Snapper.SnapIt(StartFrame, EndFrame, Children, Parent, SnapSettings);
```

### 进阶用法：空间通道操作

```cpp
// 来源: ControlRigSpaceChannelEditors.h
// 在空间通道中添加关键帧
FKeyHandle Handle = FControlRigSpaceChannelHelpers::SequencerKeyControlRigSpaceChannel(
    ControlRig, Sequencer, SpaceChannel, Section, Time, RigHierarchy, ControlKey, SpaceKey
);

// 烘焙控制器到指定空间
FRigSpacePickerBakeSettings BakeSettings;
BakeSettings.TargetSpace = FRigElementKey(TEXT("Spine"), ERigElementType::Bone);
FControlRigSpaceChannelHelpers::SequencerBakeControlInSpace(
    ControlRig, Sequencer, Channel, Section, RigHierarchy, ControlKey, BakeSettings
);
```

## Demo 示例

### 最小示例：创建并初始化 Control Rig

```cpp
// MyRigActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ControlRig.h"
#include "MyRigActor.generated.h"

UCLASS()
class AMyRigActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRigActor();

    UPROPERTY(EditAnywhere, Category = "Control Rig")
    TSubclassOf<UControlRig> RigClass;

    UPROPERTY()
    TObjectPtr<UControlRig> ControlRig;

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** 获取控制器的世界变换 */
    UFUNCTION(BlueprintCallable)
    FTransform GetControlTransform(FName ControlName) const;

    /** 设置控制器的本地变换 */
    UFUNCTION(BlueprintCallable)
    void SetControlTransform(FName ControlName, const FTransform& Transform);
};
```

```cpp
// MyRigActor.cpp
#include "MyRigActor.h"
#include "Rigs/RigHierarchy.h"

AMyRigActor::AMyRigActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyRigActor::BeginPlay()
{
    Super::BeginPlay();

    if (RigClass)
    {
        ControlRig = NewObject<UControlRig>(this, RigClass);
        if (ControlRig)
        {
            // 初始化 Rig，绑定到当前 Actor
            ControlRig->Initialize();
            ControlRig->SetObjectBinding(this);
        }
    }
}

void AMyRigActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (ControlRig)
    {
        // 每帧求值 Rig
        ControlRig->Evaluate(DeltaTime);
    }
}

FTransform AMyRigActor::GetControlTransform(FName ControlName) const
{
    if (ControlRig && ControlRig->GetHierarchy())
    {
        FRigElementKey Key(ControlName, ERigElementType::Control);
        return ControlRig->GetHierarchy()->GetGlobalTransform(Key);
    }
    return FTransform::Identity;
}

void AMyRigActor::SetControlTransform(FName ControlName, const FTransform& Transform)
{
    if (ControlRig && ControlRig->GetHierarchy())
    {
        FRigElementKey Key(ControlName, ERigElementType::Control);
        ControlRig->GetHierarchy()->SetGlobalTransform(Key, Transform);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigVM` | RigVM 虚拟机，ControlRig 的节点图求值引擎 |
| `PythonScript` | Python 脚本支持，用于编辑器自动化 |
| `MovieScene` | Sequencer 核心，动画序列管理 |
| `LevelSequence` | 关卡序列，Sequencer 的关卡集成 |
| `Constraints` | 变换约束系统 |
| `SequencerCore` | Sequencer 核心框架 |

## 维护状态

### 近期更新

```
- b901655f231e [Backout] - CL48394959 Control Rig: Multiple Control Rig tests are being skipped due to an assertion error
- 3e0533f2db94 Control Rig: Multiple Control Rig tests are being skipped due to an assertion error
- aa2fdb9b676e Constraints: baking with new evaluation & physics - ensure that the animation is updated with the proper delta time when baking
```

### 维护评价

ControlRig 是 UE5 动画系统的核心组件，由 Epic Games 官方持续维护。

- **创建时间**：2017 年，已有 8 年历史
- **维护状态**：🟢 **活跃维护** — 作为 UE5 动画管线的核心，持续有功能更新和 bug 修复
- **近期活动**：最近的提交涉及测试修复和约束烘焙改进，表明仍在积极开发
- **成熟度**：经过多个 UE 版本迭代，API 已趋于稳定，但仍在持续演进（如 Modular Rig 等新特性）
- **推荐使用**：✅ **强烈推荐** — 这是 UE5 官方推荐的程序化动画方案，文档和社区支持完善

**注意**：由于模块规模极大（1240+ 文件），建议从蓝图编辑器入手学习，逐步深入 C++ API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig)
- [官方文档](https://docs.unrealengine.com/en-US/animation-rigging/control-rig/)（UE 官方文档）