# Sequencer Anim Tools

> Animation Tools For Sequencer and Control Rig

| 属性 | 值 |
|---|---|
| 中文名 | 序列器动画工具 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SequencerAnimTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-07-13 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/SequencerAnimTools) | |

## 用途

SequencerAnimTools 为 Unreal Sequencer 提供了两个核心的动画编辑工具：**Motion Trail（运动轨迹）** 和 **Edit Pivot（枢轴点编辑）**。

**Motion Trail** 解决的核心问题是：在 Sequencer 中编辑动画时，用户很难直观地看到对象在世界空间中的运动路径。该工具在视口中绘制对象随时间变化的运动轨迹线，用户可以直接在视口中点击轨迹上的关键帧进行选择、拖拽和删除，就像在曲线编辑器中操作一样，但更加直观。轨迹支持多种类型：Actor/组件的变换轨迹、Socket 轨迹、以及 Control Rig 控制点的轨迹。

**Edit Pivot** 解决的问题是：在 Sequencer 中同时选中多个对象（Actor 或 Control Rig 控制器）时，Gizmo 的枢轴点默认位于某个中心位置。该工具允许用户自由设置或切换枢轴点位置，以便在操作多个对象时以指定的点为中心进行变换。

这两个工具作为 **UInteractiveTool** 实现，通过 UE5 的编辑器模式（Editor Mode）系统集成到 Sequencer 的工作流中。

## 使用场景

- 你在 Sequencer 中编辑骨骼动画，想要直观地看到骨骼的运动轨迹 → 用 Motion Trail
- 你在 Sequencer 中使用 Control Rig 调节角色动画，需要在视口中直接拖拽关键帧 → 用 Motion Trail
- 你在 Sequencer 中同时选中了多个对象，需要自定义 Gizmo 枢轴点 → 用 Edit Pivot
- 你需要将运动轨迹固定（Pin）在视口中，方便对比不同帧之间的位置关系 → 用 Motion Trail 的 Pin 功能

## 蓝图用法

本插件的工具通过 Editor Mode 激活，不直接暴露蓝图节点给游戏逻辑。以下 API 通过编辑器扩展使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TranslateSelectedKeysLeft` | 将选中的关键帧向左移动一帧 | `UMotionTrailTool` |
| `TranslateSelectedKeysRight` | 将选中的关键帧向右移动一帧 | `UMotionTrailTool` |
| `FrameSelection` | 在视口中框选选中的关键帧 | `UMotionTrailTool` |
| `DeselectAll` | 取消所有关键帧选择 | `UMotionTrailTool` |
| `TogglePivotMode` | 切换枢轴点模式与自由模式 | `USequencerPivotTool` |
| `ResetPivot` | 重置枢轴点位置 | `USequencerPivotTool` |

### 命令绑定

两个工具分别注册了各自的命令集：

**Motion Trail 命令**（`FMotionTrailCommands`）：

| 命令 | 快捷键 | 说明 |
|---|---|---|
| `TranslateSelectedKeysLeft` | 自定义 | 选中关键帧左移一帧 |
| `TranslateSelectedKeysRight` | 自定义 | 选中关键帧右移一帧 |
| `FrameSelection` | 自定义 | 框选选中的关键帧 |
| `DeselectAll` | 自定义 | 取消全部选择 |

**Edit Pivot 命令**（`FEditPivotCommands`）：

| 命令 | 快捷键 | 说明 |
|---|---|---|
| `ResetPivot` | 自定义 | 重置枢轴点到原始位置 |
| `ToggleFreePivot` | 自定义 | 在自由模式和枢轴模式间切换 |

## C++ 用法

### 头文件引入

```cpp
#include "MotionTrailTool.h"
#include "SequencerAnimEditPivotTool.h"
#include "Trail.h"
#include "TrailHierarchy.h"
#include "BaseSequencerAnimTool.h"
```

### 基本用法

#### 创建自定义轨迹类型

继承 `FTrail` 实现自定义运动轨迹（来源：`Trail.h`）：

```cpp
#include "Trail.h"

using namespace UE::SequencerAnimTools;

class FMyCustomTrail : public FTrail
{
public:
    FMyCustomTrail(UObject* InOwner)
        : FTrail(InOwner)
    {}

    virtual FText GetName() const override
    {
        return FText::FromString(TEXT("My Custom Trail"));
    }

    // 每帧更新轨迹数据
    virtual FTrailCurrentStatus UpdateTrail(const FNewSceneContext& NewSceneContext) override
    {
        FTrailCurrentStatus Status;
        Status.CacheState = ETrailCacheState::UpToDate;
        // ... 计算轨迹点 ...
        return Status;
    }

    // 在指定时间获取变换
    virtual void Interp(const FFrameNumber& Time, FTransform& OutTransform,
                        FTransform& OutParentTransform) override
    {
        // 根据时间插值获取变换
        OutTransform = FTransform::Identity;
        OutParentTransform = FTransform::Identity;
    }

    // 支持框选
    virtual bool BoxSelect(FBox& InBox, bool InSelect = true) override
    {
        // 检查轨迹上的点是否在选择框内
        return false;
    }

    // 支持键盘操作
    virtual void TranslateSelectedKeys(bool bRight) override
    {
        // 将选中的关键帧左右移动
    }

    virtual void DeleteSelectedKeys() override
    {
        // 删除选中的关键帧
    }
};
```

#### 使用 FTrailHierarchy 管理轨迹

```cpp
#include "TrailHierarchy.h"

using namespace UE::SequencerAnimTools;

// 假设已有一个 FTrailHierarchy 的实例
FTrailHierarchy* Hierarchy = /* 获取层次结构 */;

// 添加轨迹
FGuid TrailKey = FGuid::NewGuid();
TUniquePtr<FTrail> MyTrail = MakeUnique<FMyCustomTrail>(OwnerObject);
Hierarchy->AddTrail(TrailKey, MoveTemp(MyTrail));

// 检查轨迹可见性
bool bVisible = Hierarchy->IsVisible(TrailKey);

// 查询是否有选中的轨迹
bool bHasSelection = Hierarchy->IsAnythingSelected();
FVector SelectedPos;
FQuat SelectedRot;
Hierarchy->IsAnythingSelected(SelectedPos, SelectedRot);

// 移动选中的关键帧
Hierarchy->TranslateSelectedKeys(true); // 向右移动
Hierarchy->TranslateSelectedKeys(false); // 向左移动
```

#### 通过委托注册自定义轨迹层次结构

```cpp
#include "MotionTrailTool.h"

// 在模块的 StartupModule 中注册回调
void FMyModule::StartupModule()
{
    UMotionTrailTool::OnCreateAdditionalTrailHierarchies.AddLambda(
        [](UMotionTrailTool* Tool)
        {
            // 创建并注册自定义的轨迹层次结构
            auto MyHierarchy = MakeShared<FMyTrailHierarchy>();
            Tool->AddTrailHierarchy(MyHierarchy);
        }
    );
}
```

### 进阶用法

#### 注册自定义 Gizmo

```cpp
#include "BaseSequencerAnimTool.h"

using namespace UE::SequencerAnimTools;

// 使用辅助函数创建 Gizmo
FSequencerAnimToolHelpers::FGizmoData GizmoData;
GizmoData.Owner = this;
GizmoData.ToolManager = ToolManager;
GizmoData.TransformProxy = MyTransformProxy;
GizmoData.GizmoManager = GizmoManager;
GizmoData.InstanceIdentifier = TEXT("MyCustomGizmo");

TObjectPtr<UCombinedTransformGizmo> CombinedGizmo;
TObjectPtr<UTransformGizmo> TRSGizmo;
FSequencerAnimToolHelpers::CreateGizmo(GizmoData, CombinedGizmo, TRSGizmo);
```

#### FTrailVisibilityManager 控制可见性

```cpp
#include "TrailHierarchy.h"

using namespace UE::SequencerAnimTools;

FTrailHierarchy* Hierarchy = /* ... */;
FTrailVisibilityManager& VisManager = Hierarchy->GetVisibilityManager();

// 设置轨迹始终可见（固定/钉住）
VisManager.SetTrailAlwaysVisible(TrailGuid, true);

// 检查轨迹是否始终可见
bool bPinned = VisManager.IsTrailAlwaysVisible(TrailGuid);

// 将轨迹标记为不活跃（隐藏）
VisManager.InactiveMask.Add(TrailGuid);

// 将轨迹标记为用户隐藏
VisManager.VisibilityMask.Add(TrailGuid);

// 重置所有可见性状态
VisManager.Reset();
```

#### 轨迹颜色和样式

```cpp
#include "Trail.h"

using namespace UE::SequencerAnimTools;

// 使用 FColorState 计算轨迹颜色
FColorState ColorState;
ColorState.Setup(TrailHierarchy);
ColorState.ReadyForTrail(bIsPinned, EMotionTrailTrailStyle::Solid);

EMotionTrailTrailStyle Style = ColorState.GetStyle();
```

## Demo 示例

### 最小 Motion Trail 实现

```cpp
// MyCustomTrail.h
#pragma once

#include "Trail.h"
#include "TrailHierarchy.h"

using namespace UE::SequencerAnimTools;

class FSimpleTrail : public FTrail
{
public:
    FSimpleTrail(UObject* InOwner, const TArray<FTransform>& InKeyframes)
        : FTrail(InOwner)
        , Keyframes(InKeyframes)
    {
        DrawInfo = MakeUnique<FTrajectoryDrawInfo>(
            EMotionTrailTrailStyle::Solid,
            FLinearColor::Green,
            CachedTransforms,
            CachedParentTransforms
        );
    }

    virtual FText GetName() const override
    {
        return FText::FromString(TEXT("Simple Trail"));
    }

    virtual FTrailCurrentStatus UpdateTrail(const FNewSceneContext& NewSceneContext) override
    {
        // 简单场景：直接使用预设的关键帧数据
        CachedTransforms = MakeShared<FArrayOfTransforms>();
        CachedTransforms->Transforms.SetNum(Keyframes.Num());

        for (int32 i = 0; i < Keyframes.Num(); ++i)
        {
            CachedTransforms->Transforms[i] = Keyframes[i];
        }

        DrawInfo = MakeUnique<FTrajectoryDrawInfo>(
            EMotionTrailTrailStyle::Solid,
            FLinearColor::Green,
            CachedTransforms,
            CachedParentTransforms
        );

        FTrailCurrentStatus Status;
        Status.CacheState = ETrailCacheState::UpToDate;
        return Status;
    }

    virtual void Interp(const FFrameNumber& Time, FTransform& OutTransform,
                        FTransform& OutParentTransform) override
    {
        // 简单的线性插值
        if (Keyframes.Num() == 0)
        {
            OutTransform = FTransform::Identity;
        }
        else
        {
            int32 Index = FMath::Clamp(Time.Value, 0, Keyframes.Num() - 1);
            OutTransform = Keyframes[Index];
        }
        OutParentTransform = FTransform::Identity;
    }

    virtual bool IsAnythingSelected() const override
    {
        return bIsSelected;
    }

    virtual bool IsAnythingSelected(FVector& OutVectorPosition, FQuat& OutRotation) const override
    {
        if (bIsSelected && SelectedKeyIndex >= 0 && SelectedKeyIndex < Keyframes.Num())
        {
            OutVectorPosition = Keyframes[SelectedKeyIndex].GetLocation();
            OutRotation = Keyframes[SelectedKeyIndex].GetRotation();
            return true;
        }
        return false;
    }

    virtual void SelectNone() override
    {
        bIsSelected = false;
        SelectedKeyIndex = -1;
    }

    virtual TArray<FFrameNumber> GetKeyTimes() const override
    {
        TArray<FFrameNumber> Times;
        for (int32 i = 0; i < Keyframes.Num(); ++i)
        {
            Times.Add(FFrameNumber(i));
        }
        return Times;
    }

private:
    TArray<FTransform> Keyframes;
    bool bIsSelected = false;
    int32 SelectedKeyIndex = -1;

    TSharedPtr<FArrayOfTransforms> CachedTransforms = MakeShared<FArrayOfTransforms>();
    TSharedPtr<FArrayOfTransforms> CachedParentTransforms = MakeShared<FArrayOfTransforms>();
};
```

```cpp
// MyTrailSetup.cpp
#include "MyCustomTrail.h"
#include "TrailHierarchy.h"
#include "MotionTrailTool.h"

using namespace UE::SequencerAnimTools;

void RegisterMyTrail()
{
    // 注册回调，在 Motion Trail 工具启动时创建自定义轨迹
    UMotionTrailTool::OnCreateAdditionalTrailHierarchies.AddLambda(
        [](UMotionTrailTool* Tool)
        {
            // 此处可以添加自定义的 FTrailHierarchy 实现
            // 并通过 Tool->AddTrailHierarchy() 注册
        }
    );
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | Control Rig 控制器轨迹支持 |
| `LevelSequenceEditor` | Sequencer 编辑器集成 |
| `SequencerScripting` | Sequencer 脚本接口 |
| `InteractiveToolsFramework` | 交互式工具框架（UInteractiveTool 基类） |
| `AnimationEditMode` | 动画编辑模式，提供关键帧和编辑模式支持 |
| `TransformConstraintUtil` | 变换约束工具，枢轴点编辑时的约束处理 |
| `ToolWidgets` | 工具 UI 组件（枢轴模式覆盖层等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `1df3a6bd` | Motion Trails: Remove Alt modifier so it can be used to move camera, at some point it was to be used | 移除 Motion Trail 的 Alt 修饰键，恢复 Alt 键用于相机移动的默认行为 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移为 UE_LOGF 格式化版本 |
| 2026-03-19 | `048033f8` | Silence false positive PVS. | 修复 PVS 静态分析工具的误报警告 |
| 2026-03-19 | `eeaee5eb` | Attempt to fix PVS static analysis warning with explicit lambda capture. | 通过显式 Lambda 捕获修复 PVS 静态分析警告 |
| 2026-03-19 | `66538387` | Sequencer: Add animation mixer edit mode with per-section skeleton visualization, motion trail infra | 为 Sequencer 添加动画混合器编辑模式，支持逐 Section 骨骼可视化，扩展运动轨迹基础设施 |

### 维护评价

- **活跃维护**：最近 6 个月内有多次实质性更新，包括功能扩展（动画混合器编辑模式）和交互改进（Alt 键行为调整）
- 创建于 2021 年，约 4 年历史，处于稳定期
- 代码持续优化（静态分析修复、日志宏迁移），表明维护质量良好
- 2026-03-19 的更新增加了动画混合器编辑模式，说明该插件仍在积极扩展功能
- **推荐使用**：作为 Epic 官方维护的 Sequencer 动画工具，与 Control Rig 紧密集成，适合动画工作流

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/SequencerAnimTools)
- [官方文档]()（暂无）
- [MotionTrailTool 源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Editor/SequencerAnimTools/Source/SequencerAnimTools/Public/MotionTrailTool.h)
- [SequencerAnimEditPivotTool 源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Editor/SequencerAnimTools/Source/SequencerAnimTools/Public/SequencerAnimEditPivotTool.h)
- [Trail 基类源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Editor/SequencerAnimTools/Source/SequencerAnimTools/Public/Trail.h)
- [TrailHierarchy 源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Editor/SequencerAnimTools/Source/SequencerAnimTools/Public/TrailHierarchy.h)