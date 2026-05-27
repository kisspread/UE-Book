# Control Rig

> Framework for animation driven by user controls.

| 属性 | 值 |
|---|---|
| 中文名 | 控制绑定 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `ControlRig` (Runtime), `ControlRigDeveloper` (Runtime), `ControlRigEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-14 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig) | |

## 用途

Control Rig 是 UE5 的核心动画驱动框架，解决的核心问题是：**让用户通过自定义控制（Controls）来驱动骨骼动画**。

传统骨骼动画依赖预烘焙的动画资产，而 Control Rig 提供了一套完整的工具链，让动画师能够：

1. **创建控制（Controls）**：在骨骼层级中添加浮点、变换、旋转等类型的控制器，取代直接操作骨骼节点
2. **构建程序化绑定（Procedural Rigging）**：通过可视化节点图（基于 RigVM）定义控制器之间的逻辑关系，实现 FK/IK 切换、空间切换等复杂动画行为
3. **在 Sequencer 中编辑动画**：将控制器参数暴露为 Sequencer 的关键帧通道，支持动画层、约束、混合等高级动画编辑功能
4. **模块化绑定（Modular Rig）**：将复杂绑定拆分为可复用的模块，通过连接器（Connector）系统组合，提高绑定的可维护性和复用性

Control Rig 从 5.0 版本从 Experimental 迁移到正式发布，目前已成为 UE5 动画系统的核心组件，被 MetaHuman、动画模式（Animation Mode）等 Epic 官方功能深度集成。

## 使用场景

- 你正在为角色创建动画绑定 → 使用 Control Rig 构建控制器和绑定逻辑
- 你需要在 Sequencer 中对动画进行分层编辑（基础层 + 叠加层 + 覆盖层）→ 使用动画层系统
- 你需要在动画编辑过程中实时切换控制器的空间（如从世界空间切换到父骨骼空间）→ 使用空间选择器（Space Picker）
- 你需要将约束烘焙为关键帧 → 使用约束管理器和烘焙工具
- 你想在两个关键帧之间进行插值混合（Tween）→ 使用 Tween 工具
- 你需要为多人动画团队创建可复用的绑定模块 → 使用模块化绑定系统
- 你想通过 Python/蓝图脚本批量处理 Sequencer 中的 Control Rig 动画 → 使用 `UControlRigSequencerEditorLibrary`
- 你需要可视化调试绑定的依赖关系 → 使用依赖图（Dependency Graph）

## 蓝图用法

### 核心节点

#### Sequencer 与 Control Rig 交互

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetVisibleControlRigs` | 获取当前可见的所有 Control Rig 实例 | `UControlRigSequencerEditorLibrary` |
| `GetControlRigs` | 获取 Level Sequence 中的所有 Control Rig 及其绑定 | `UControlRigSequencerEditorLibrary` |
| `FindOrCreateControlRigTrack` | 查找或创建指定绑定的 Control Rig 轨道 | `UControlRigSequencerEditorLibrary` |
| `BakeToControlRig` | 将当前动画烘焙到 Control Rig 轨道 | `UControlRigSequencerEditorLibrary` |
| `SmartReduce` | 对 Control Rig 区段执行智能关键帧精简 | `UControlRigSequencerEditorLibrary` |

#### 动画导入与导出

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadAnimSequenceIntoControlRigSectionWithRange` | 将动画序列加载到 Control Rig 区段（支持自定义范围） | `UControlRigSequencerEditorLibrary` |
| `ExportAnimSequenceFromSequencer` | 从 Sequencer 导出动画序列（支持 Spawnable） | `UControlRigSequencerEditorLibrary` |
| `ControlRigCopyVectorParameterCurvesToTransform` | 将向量类型的参数曲线转换为变换曲线 | `UControlRigSequencerEditorLibrary` |

#### 控制器操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetControlValues` | 批量获取指定帧的控制器值 | `UControlRigSequencerEditorLibrary` |
| `BatchGetControlTransforms` | 批量获取控制器变换（支持本地/世界空间） | `UControlRigSequencerEditorLibrary` |
| `TweenControlRig` | 对 Control Rig 执行 Tween 混合操作 | `UControlRigSequencerEditorLibrary` |
| `BlendValuesOnSelected` | 对选中的关键帧执行混合操作 | `UControlRigSequencerEditorLibrary` |
| `SnapControlRig` | 将子对象吸附到父对象并设置关键帧 | `UControlRigSequencerEditorLibrary` |

#### 约束操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddConstraint` | 添加变换约束（父子、目标、旋转等） | `UControlRigSequencerEditorLibrary` |
| `BakeConstraint` | 将约束烘焙为关键帧 | `UControlRigSequencerEditorLibrary` |
| `SetConstraintActiveKey` | 设置约束的激活关键帧 | `UControlRigSequencerEditorLibrary` |
| `Compensate` | 在指定时间对约束执行补偿 | `UControlRigSequencerEditorLibrary` |
| `GetConstraintsForHandle` | 获取指定变换句柄的所有约束 | `UControlRigSequencerEditorLibrary` |

#### 动画层操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAnimLayers` | 获取动画层对象列表 | `UControlRigSequencerEditorLibrary` |
| `AddAnimLayerFromSelection` | 从当前选择创建动画层 | `UControlRigSequencerEditorLibrary` |
| `DuplicateAnimLayer` | 复制指定索引的动画层 | `UControlRigSequencerEditorLibrary` |
| `DeleteAnimLayer` | 删除指定索引的动画层 | `UControlRigSequencerEditorLibrary` |
| `MergeAnimLayersWithSettings` | 合并指定的动画层 | `UControlRigSequencerEditorLibrary` |
| `ReorderAnimLayers` | 重新排列动画层顺序 | `UControlRigSequencerEditorLibrary` |

#### 蓝图编辑器工具

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CastToControlRigBlueprint` | 将对象转换为 Control Rig Blueprint | `UControlRigBlueprintEditorLibrary` |
| `SetPreviewMesh` | 设置 Control Rig Blueprint 的预览网格体 | `UControlRigBlueprintEditorLibrary` |
| `GetPreviewMesh` | 获取 Control Rig Blueprint 的预览网格体 | `UControlRigBlueprintEditorLibrary` |
| `GetHierarchy` | 获取 Control Rig 的层级对象 | `UControlRigBlueprintEditorLibrary` |
| `GetHierarchyController` | 获取层级控制器 | `UControlRigBlueprintEditorLibrary` |
| `GetAvailableRigModules` | 获取可用的绑定模块描述列表 | `UControlRigBlueprintEditorLibrary` |
| `CreateControlRigAssetFromBlueprint` | 从蓝图创建 Control Rig 资产 | `UControlRigBlueprintEditorLibrary` |

#### 选择集操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateSetItemFromSelection` | 从当前选择创建选择集 | `UAIESelectionSets` |
| `CreateMirror` | 创建选择集的镜像副本 | `UAIESelectionSets` |
| `SelectItem` | 从选择集中选择控制器 | `UAIESelectionSets` |
| `KeyAll` | 对选择集中的所有项目设置关键帧 | `UAIESelectionSets` |
| `ShowOrHideControls` | 显示/隐藏选择集中的控制器 | `UAIESelectionSets` |
| `IsolateControls` | 隔离显示选择集中的控制器 | `UAIESelectionSets` |
| `LoadFromJsonFile` / `ExportAsJsonFile` | JSON 格式的导入/导出 | `UAIESelectionSets` |

### 使用示例（蓝图描述）

**示例 1：在 Sequencer 中为绑定对象添加 Control Rig 轨道**

1. 调用 `GetControlRigs(LevelSequence)` 获取当前序列中的 Control Rig
2. 如果目标绑定上没有 Control Rig，调用 `FindOrCreateControlRigTrack` 创建
3. 使用 `BakeToControlRig` 将已有动画烘焙到 Control Rig 轨道

**示例 2：批量获取控制器变换数据**

1. 准备控制器名称数组（如 `["Hand_L", "Hand_R", "Spine"]`）
2. 准备帧号数组（如 `[0, 10, 20, 30]`）
3. 调用 `BatchGetControlTransforms`，指定空间类型（Local/Global）
4. 返回的 `FArrayOfRigControlTransforms` 数组中包含每个控制器在各帧的变换值

**示例 3：创建并烘焙约束**

1. 获取目标绑定的 `UTransformableHandle`
2. 调用 `AddConstraint(ETransformConstraintType::Parent, ChildHandle, ParentHandle, true)` 创建约束
3. 指定需要烘焙的帧范围
4. 调用 `BakeConstraints` 执行烘焙，约束将在烘焙后自动设为非激活状态

## C++ 用法

### 头文件引入

```cpp
// Runtime 核心
#include "ControlRig.h"
#include "Rigs/ControlRig.h"

// 编辑器脚本库
#include "ControlRigSequencerEditorLibrary.h"
#include "ControlRigBlueprintEditorLibrary.h"

// 蓝图编辑器库
#include "ControlRigBlueprintEditorLibrary.h"

// 动画层
#include "AnimLayers.h"

// 选择集
#include "SelectionSets.h"

// 编辑模式
#include "EditMode/ControlRigEditMode.h"
```

### 基本用法

**获取 Level Sequence 中的 Control Rig（来自 `UControlRigSequencerEditorLibrary`）：**

```cpp
// 来源: Public/ControlRigSequencerEditorLibrary.h

// 获取所有可见的 Control Rig
TArray<UControlRig*> VisibleRigs = UControlRigSequencerEditorLibrary::GetVisibleControlRigs();

// 获取 Level Sequence 中的 Control Rig 及其绑定
TArray<FControlRigSequencerBindingProxy> Proxies = 
    UControlRigSequencerEditorLibrary::GetControlRigs(MyLevelSequence);

for (const FControlRigSequencerBindingProxy& Proxy : Proxies)
{
    UControlRig* Rig = Proxy.ControlRig;
    UMovieSceneControlRigParameterTrack* Track = Proxy.Track;
    FMovieSceneBindingProxy Binding = Proxy.Proxy;
    // ...
}
```

**批量获取控制器值（来自 `UControlRigSequencerEditorLibrary`）：**

```cpp
// 来源: Public/ControlRigSequencerEditorLibrary.h

TArray<FName> ControlNames = {TEXT("Hand_L"), TEXT("Hand_R")};
TArray<FFrameNumber> Frames = {FFrameNumber(0), FFrameNumber(30), FFrameNumber(60)};

TArray<FArrayOfRigControlValues> Results = 
    UControlRigSequencerEditorLibrary::GetControlValues(
        LevelSequence, ControlRig, ControlNames, Frames, 
        EMovieSceneTimeUnit::DisplayRate);

for (const FArrayOfRigControlValues& ControlValues : Results)
{
    FName ControlName = ControlValues.ControlName;
    for (const FRigControlValue& Value : ControlValues.Values)
    {
        // 使用 URigHierarchy 的静态方法转换值
        // 例如: float FloatVal = URigHierarchy::GetFloatFromControlValue(Value);
    }
}
```

### 进阶用法

**批量操作控制器变换 + 约束管理：**

```cpp
// 来源: Public/ControlRigSequencerEditorLibrary.h

// 1. 批量获取控制器变换（世界空间）
TArray<FArrayOfRigControlTransforms> Transforms = 
    UControlRigSequencerEditorLibrary::BatchGetControlTransforms(
        LevelSequence, ControlRig, ControlNames, Frames,
        EControlRigTransformSpace::Global);

// 2. 创建约束
UTransformableControlHandle* ChildHandle = /* ... */;
UTransformableControlHandle* ParentHandle = /* ... */;
UTickableConstraint* Constraint = 
    UControlRigSequencerEditorLibrary::AddConstraint(
        World, ETransformConstraintType::Parent, 
        ChildHandle, ParentHandle, true);

// 3. 设置约束激活关键帧
FFrameNumber KeyFrame(60);
UControlRigSequencerEditorLibrary::SetConstraintActiveKey(
    Constraint, false, KeyFrame);  // false = 非激活

// 4. 烘焙约束为关键帧
TArray<FFrameNumber> BakeFrames;
for (int32 i = 0; i <= 120; i += 1)
{
    BakeFrames.Add(FFrameNumber(i));
}
UControlRigSequencerEditorLibrary::BakeConstraint(
    World, Constraint, BakeFrames);

// 5. 执行 Tween 混合
UControlRigSequencerEditorLibrary::TweenControlRig(
    LevelSequence, ControlRig, 0.5f);  // 0.5 = 中间值
```

## Demo 示例

以下展示如何通过 C++ 代码在 Sequencer 中与 Control Rig 交互：

```cpp
// MyControlRigScript.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "ControlRigSequencerEditorLibrary.h"
#include "MyControlRigScript.generated.h"

UCLASS()
class UMyControlRigScript : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    /** 演示：批量读取并设置控制器值 */
    UFUNCTION(BlueprintCallable)
    void DemoBatchControlOperations(ULevelSequence* InSequence);

    /** 演示：添加约束并烘焙 */
    UFUNCTION(BlueprintCallable)
    void DemoAddConstraintAndBake(
        ULevelSequence* InSequence,
        UTransformableHandle* InChild,
        UTransformableHandle* InParent);
};
```

```cpp
// MyControlRigScript.cpp
#include "MyControlRigScript.h"
#include "LevelSequence.h"
#include "MovieSceneControlRigParameterTrack.h"

void UMyControlRigScript::DemoBatchControlOperations(ULevelSequence* InSequence)
{
    if (!InSequence) return;

    // 1. 获取序列中的 Control Rig
    TArray<FControlRigSequencerBindingProxy> Proxies = 
        UControlRigSequencerEditorLibrary::GetControlRigs(InSequence);
    
    if (Proxies.IsEmpty()) return;
    
    UControlRig* Rig = Proxies[0].ControlRig;
    if (!Rig) return;

    // 2. 批量获取控制器变换
    TArray<FName> Names = {TEXT("LeftHand"), TEXT("RightHand")};
    TArray<FFrameNumber> Frames;
    for (int32 f = 0; f <= 60; f += 10)
    {
        Frames.Add(FFrameNumber(f));
    }
    
    TArray<FArrayOfRigControlTransforms> Results = 
        UControlRigSequencerEditorLibrary::BatchGetControlTransforms(
            InSequence, Rig, Names, Frames,
            EControlRigTransformSpace::Global);

    // 3. 执行 Tween
    UControlRigSequencerEditorLibrary::TweenControlRig(InSequence, Rig, 0.5f);

    // 4. 智能精简关键帧
    UMovieSceneControlRigParameterTrack* Track = Proxies[0].Track;
    if (Track)
    {
        TArray<UMovieSceneSection*> Sections = Track->GetAllSections();
        for (UMovieSceneSection* Section : Sections)
        {
            FSmartReduceParams ReduceParams;
            UControlRigSequencerEditorLibrary::SmartReduce(ReduceParams, Section);
        }
    }
}

void UMyControlRigScript::DemoAddConstraintAndBake(
    ULevelSequence* InSequence,
    UTransformableHandle* InChild,
    UTransformableHandle* InParent)
{
    if (!InChild || !InParent) return;

    UWorld* World = GEditor->GetEditorWorldContext().World();

    // 1. 创建父子约束
    UTickableConstraint* Constraint = 
        UControlRigSequencerEditorLibrary::AddConstraint(
            World, ETransformConstraintType::Parent, 
            InChild, InParent, true);

    if (!Constraint) return;

    // 2. 设置关键帧范围
    TArray<FFrameNumber> Frames;
    for (int32 f = 0; f <= 120; f++)
    {
        Frames.Add(FFrameNumber(f));
    }

    // 3. 烘焙约束
    UControlRigSequencerEditorLibrary::BakeConstraint(
        World, Constraint, Frames);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigVM` | Control Rig 底层的虚拟机执行框架，节点图编译与执行 |
| `RigVMEditor` | RigVM 的编辑器基础设施，节点图编辑、属性面板等 |
| `Sequencer` | Sequencer 集成，关键帧编辑、轨道管理 |
| `AnimationBlueprintLibrary` | 动画蓝图工具库 |
| `ActorModifierCore` | Actor 修改器核心（用于约束等功能） |
| `PropertyEditor` | 属性自定义面板（控制元素详情、模块实例详情等） |
| `ControlRig` | 运行时核心模块，控制器、层级、RigVM 主机 |

> **注意**：由于此插件规模极大（xlarge），依赖项众多。使用时建议在 Build.cs 中至少添加 `ControlRig`、`ControlRigEditor`（编辑器功能）、`Sequencer`（动画编辑功能）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7fc008ea` | AutoBake: Fix crash with using Shim track editor, need to get real one in order to cast to shared po | 修复 AutoBake 中使用 Shim 轨道编辑器时的崩溃问题 |
| 2026-05-26 | `0f35dc86` | Animating in Engine: Marquee selection in Animation Mode picks controls by pivot in addition to mesh | 动画模式下框选控件时，除网格体外还通过轴心点拾取控制器 |
| 2026-05-22 | `c09576c8` | Control Rig: Fix older rigs not creating gizmos when controls are selected | 修复旧版本绑定在选择控制器时不创建 Gizmo 的问题 |
| 2026-05-22 | `4eed6d63` | Control Rig: Guard against invalid instance proxy. | 防御无效实例代理导致的问题 |
| 2026-05-20 | `818e65b0` | Control Rig Nullptr check for static analyzer | 添加空指针检查以满足静态分析器要求 |

### 维护评价

**🟢 活跃维护**

- **创建时间**：2021 年 6 月（从 Experimental 迁移到正式发布）
- **近期活跃度**：最近一周内有多次功能性更新和 Bug 修复，更新频率非常高
- **代码规模**：861 个源文件（xlarge），属于 UE5 最庞大的插件之一
- **维护团队**：Epic Games 核心动画团队持续投入
- **集成程度**：深度集成到 MetaHuman、动画模式、Sequencer 等核心系统中，是 Epic 重点维护的旗舰插件

Control Rig 是 UE5 动画系统的核心组件，处于持续活跃开发状态。每个 UE 版本都有大量新功能和改进。**强烈推荐使用**——如果你的角色动画需要任何程度的程序化控制或高级编辑功能，Control Rig 几乎是唯一的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/control-rig-in-unreal-engine/)