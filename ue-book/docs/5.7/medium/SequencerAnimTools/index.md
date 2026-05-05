# Sequencer Anim Tools

> Animation Tools For Sequencer and Control Rig

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SequencerAnimTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-07-13 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/SequencerAnimTools) | |

## 用途

SequencerAnimTools 为 UE5 Sequencer 编辑器提供**运动轨迹（Motion Trail）可视化**和**枢轴点编辑（Edit Pivot）**工具。它解决了 Sequencer 中动画编辑缺乏空间参考的核心问题：当你在 Sequencer 里移动一个物体的关键帧时，很难直观地看到它在 3D 空间中的运动路径。这个 plugin 在视口中绘制运动轨迹曲线，让你可以直接在 3D 空间中选择、移动和删除关键帧，而不只是在 Sequencer 的时间轴上操作。

同时支持 **Control Rig** 的控制器轨迹，意味着你可以为骨骼动画的每个控制点单独查看和编辑运动轨迹。

## 使用场景

- 你在 Sequencer 中制作角色动画，需要可视化查看某个骨骼或物体的运动轨迹形状 → 启用 Motion Trail
- 你需要在 3D 视口中直接拖拽运动轨迹上的关键帧点来调整动画 → 使用 Motion Trail Tool
- 你使用 Control Rig 做面部动画或身体动画，需要查看某个控制器的运动路径 → 添加 Control Rig Trail
- 你需要自定义变换 Gizmo 的旋转/缩放枢轴点来编辑动画 → 使用 Edit Pivot Tool
- 你需要将某个 Socket（如武器挂点）的运动轨迹也显示出来 → Pin Socket Trail

## 蓝图用法

本 plugin 不暴露 BlueprintCallable 函数，它是一个纯编辑器交互工具，通过 Sequencer 面板和视口操作使用。

### 使用方式

Motion Trail 通过 Sequencer 编辑器中的 **Motion Trail** 按钮启用。进入 Motion Trail 编辑模式后：

1. 选择 Sequencer 中的绑定（Binding），对应的运动轨迹会自动出现在视口中
2. 轨迹上的点代表每个关键帧位置
3. 左键点击轨迹点选中关键帧
4. 使用 Transform Gizmo 拖拽移动选中的关键帧
5. 支持框选（Box Select）和锥形选择（Frustum Select）多个关键帧

### 快捷键命令

| 命令 | 说明 |
|---|---|
| TranslateSelectedKeysLeft | 将选中关键帧左移一帧 |
| TranslateSelectedKeysRight | 将选中关键帧右移一帧 |
| FrameSelection | 将视口聚焦到选中项 |
| DeselectAll | 取消所有选择 |

Edit Pivot Tool 的快捷键：

| 命令 | 说明 |
|---|---|
| ResetPivot | 重置枢轴点到原始位置 |
| ToggleFreePivot | 切换 Free/Pivot 模式 |

## C++ 用法

### 头文件引入

```cpp
#include "MotionTrailTool.h"
#include "BaseSequencerAnimTool.h"
#include "TrailHierarchy.h"
#include "Trail.h"
```

### 核心架构

整个 plugin 采用分层架构设计：

```
USequencerToolsEditMode (编辑模式)
  └── UMotionTrailTool (交互工具，管理所有 Trail Hierarchy)
        └── FSequencerTrailHierarchy (每个 Sequencer 实例对应一个)
              └── FMovieSceneTransformTrail (每条运动轨迹)
                    ├── FMovieSceneComponentTransformTrail (组件轨迹)
                    ├── FMovieSceneSocketTransformTrail (Socket 轨迹)
                    └── FMovieSceneControlRigTransformTrail (Control Rig 轨迹)
```

### IBaseSequencerAnimTool 接口

所有 Sequencer 动画工具都实现 `IBaseSequencerAnimTool` 接口：

```cpp
// BaseSequencerAnimTool.h
UINTERFACE(MinimalAPI)
class UBaseSequencerAnimTool : public UInterface {};

class IBaseSequencerAnimTool
{
    virtual bool ProcessCommandBindings(const FKey Key, const bool bRepeat) const { return false; }
};
```

### FTrail 抽象基类

所有轨迹都继承自 `FTrail`：

```cpp
// Trail.h
namespace UE::SequencerAnimTools {

class FTrail
{
public:
    FTrail(UObject* InOwner);

    // 每帧更新轨迹数据
    virtual FTrailCurrentStatus UpdateTrail(const FNewSceneContext& NewSceneContext) = 0;

    // 在指定时间插值获取变换
    virtual void Interp(const FFrameNumber& Time, FTransform& OutTransform, FTransform& OutParentTransform);

    // 选中关键帧后的拖拽操作
    virtual bool StartTracking();
    virtual bool ApplyDelta(const FVector& Pos, const FRotator& Rot, const FVector& WidgetLocation, bool bApplyToOffset);
    virtual bool EndTracking();

    // 关键帧操作
    virtual void TranslateSelectedKeys(bool bRight);
    virtual void DeleteSelectedKeys();

    // 偏移模式（临时修改轨迹位置）
    virtual FTransform GetOffsetTransform() const;
    virtual void SetSpace(AActor* InActor, const FName& InComponentName);
};

} // namespace UE::SequencerAnimTools
```

### FTrailHierarchy

管理一组轨迹的容器类：

```cpp
// TrailHierarchy.h
namespace UE::SequencerAnimTools {

class FTrailHierarchy
{
public:
    // 轨迹管理
    virtual void AddTrail(const FGuid& Key, TUniquePtr<FTrail>&& TrailPtr);
    virtual void RemoveTrail(const FGuid& Key);

    // 选择操作
    virtual bool IsAnythingSelected(FVector& OutVectorPosition) const;
    virtual bool BoxSelect(FBox& InBox, bool InSelect = true);
    virtual bool FrustumSelect(const FConvexVolume& InFrustum, FEditorViewportClient* InViewportClient, bool InSelect = true);
    virtual void SelectNone();

    // 变换操作（通过 Gizmo）
    virtual bool StartTracking();
    virtual bool ApplyDelta(const FVector& Pos, const FRotator& Rot, const FVector& WidgetLocation, bool bApplyToOffset);
    virtual bool EndTracking();
};

} // namespace UE::SequencerAnimTools
```

### FSequencerTrailHierarchy

与 Sequencer 集成的具体实现：

```cpp
// SequencerTrailHierarchy.h
namespace UE::SequencerAnimTools {

class FSequencerTrailHierarchy : public FTrailHierarchy
{
public:
    FSequencerTrailHierarchy(TWeakPtr<ISequencer> InWeakSequencer);

    // 添加组件轨迹到层级
    FGuid AddComponentToHierarchy(const FGuid& InBindingGuid, USceneComponent* CompToAdd, UMovieScene3DTransformTrack* TransformTrack);

    // 添加 Control Rig 控制器轨迹
    FGuid AddControlRigTrail(USkeletalMeshComponent* Component, UControlRig* ControlRig,
        UMovieSceneControlRigParameterTrack* CRTrack, const FName& ControlName);

    // 固定 Socket 轨迹
    FGuid PinComponent(USceneComponent* InSceneComponent, FName InSocketName);
};

} // namespace UE::SequencerAnimTools
```

### Edit Pivot Tool

枢轴点编辑工具，用于临时修改变换 Gizmo 的枢轴位置：

```cpp
// SequencerAnimEditPivotTool.h
namespace UE::SequencerAnimTools {

class USequencerPivotTool : public UMultiSelectionTool, public IClickBehaviorTarget, public IBaseSequencerAnimTool
{
public:
    // Pivot 模式 vs Free 模式
    bool IsInPivotMode() const;
    void TogglePivotMode();
    void SetPivotMode(bool bVal);

    // 保存的枢轴位置（跨实例持久化）
    static FSavedMappings SavedPivotLocations;
    static FLastSelectedObjects LastSelectedObjects;
};

} // namespace UE::SequencerAnimTools
```

### 进阶：轨迹可见性管理

`FTrailVisibilityManager` 控制哪些轨迹可见：

```cpp
// TrailHierarchy.h
struct FTrailVisibilityManager
{
    // 轨迹是否可见（考虑选择状态、固定状态、遮罩等）
    bool IsTrailVisible(const FGuid& Guid, const FTrail* Trail, bool bShowSelected = true) const;

    // 固定/取消固定轨迹的始终显示
    void SetTrailAlwaysVisible(const FGuid& Guid, bool bSet);

    TSet<FGuid> InactiveMask;       // 缓存状态未更新的轨迹
    TSet<FGuid> VisibilityMask;     // 用户界面隐藏的轨迹
    TSet<FGuid> AlwaysVisible;      // 用户固定的轨迹
    TSet<FGuid> Selected;           // 选中的变换/骨骼轨迹
    TSet<FGuid> ControlSelected;    // 选中的 Control Rig 轨迹
};
```

### 进阶：关键帧工具

`FMotionTraiMovieScenelKeyTool` 处理轨迹上的关键帧选择和操作：

```cpp
// MotionTrailMovieSceneKey.h
namespace UE::SequencerAnimTools {

// 关键帧信息
struct FTrailKeyInfo
{
    FTransform Transform;
    FTransform ParentTransform;
    TMap<ETransformChannel, FKeyHandle> IdxMap;  // 9 个变换通道的 KeyHandle
    FFrameNumber FrameNumber;
};

// 关键帧管理工具
class FMotionTraiMovieScenelKeyTool
{
public:
    void UpdateKeys();
    void ClearSelection();
    void TranslateSelectedKeys(bool bRight);
    void DeleteSelectedKeys();

    FTrailKeyInfo* FindKey(const FFrameNumber& FrameNumber) const;
    TArray<FFrameNumber> SelectedKeyTimes() const;
    FTransform GetSelectedKeysTransform() const;
};

} // namespace UE::SequencerAnimTools
```

## Demo 示例

### 自定义 Trail 实现

如果需要为自定义对象创建运动轨迹，可以继承 `FTrail`：

```cpp
// MyCustomTrail.h
#pragma once
#include "Trail.h"

class FMyCustomTrail : public UE::SequencerAnimTools::FTrail
{
public:
    FMyCustomTrail(UObject* InOwner) : FTrail(InOwner) {}

    virtual FTrailCurrentStatus UpdateTrail(const FNewSceneContext& NewSceneContext) override
    {
        FTrailCurrentStatus Status;
        // 计算轨迹点...
        Status.CacheState = ETrailCacheState::UpToDate;
        return Status;
    }

    virtual FText GetName() const override
    {
        return FText::FromString(TEXT("Custom Trail"));
    }

    virtual void Interp(const FFrameNumber& Time, FTransform& OutTransform, FTransform& OutParentTransform) override
    {
        // 在指定时间插值...
        OutTransform = FTransform::Identity;
        OutParentTransform = FTransform::Identity;
    }
};
```

### 依赖 Build.cs

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "Slate",
    "SlateCore",
});

PrivateDependencyModuleNames.AddRange(new string[]
{
    "CoreUObject",
    "Engine",
    "InputCore",
    "UnrealEd",
    "SequencerAnimTools",  // 你的模块需要依赖此模块
    "InteractiveToolsFramework",
    "EditorInteractiveToolsFramework",
    "MovieScene",
    "ControlRig",
});
```

> 注意：由于本 plugin 是 Editor 类型，你的模块也必须是 Editor 或 UncookedOnly 类型才能依赖它。

## 模块依赖

从 Build.cs 的 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `CoreUObject` | UObject 系统基础 |
| `Engine` | 引擎核心（World、Actor、Component） |
| `InputCore` | 输入系统（按键定义） |
| `UnrealEd` | 编辑器框架（EdMode、HitProxy） |
| `LevelEditor` | 关卡编辑器集成 |
| `EditorFramework` | 编辑器框架基础 |
| `EditorInteractiveToolsFramework` | 编辑器交互工具框架（Gizmo、行为系统） |
| `InteractiveToolsFramework` | 交互工具框架核心 |
| `MovieScene` | MovieScene 数据结构 |
| `MovieSceneTracks` | MovieScene Track 类型 |
| `MovieSceneTools` | MovieScene 工具集 |
| `Sequencer` | Sequencer 编辑器核心 |
| `LevelSequence` | LevelSequence 资产类型 |
| `LevelSequenceEditor` | LevelSequence 编辑器 UI |
| `ControlRig` | Control Rig 运行时 |
| `ControlRigEditor` | Control Rig 编辑器集成 |

Plugin 依赖：

| Plugin | 用途 |
|---|---|
| `ControlRig` | Control Rig 控制器轨迹支持 |
| `LevelSequenceEditor` | Sequencer 编辑器集成 |
| `SequencerScripting` | Sequencer 脚本接口 |

## 维护状态

### 近期更新

1. **2025-11-18** `504e6237e477` — Fix actor motion trails not working (UE-349680)
   - 修复了 Actor 运动轨迹不工作的 bug，属于关键功能修复。

2. **2025-10-17** `b5076111aebf` — Added support for multiple rigs; fixed SpawnableRestore issue
   - 新增多 Control Rig 支持，修复 Spawnable 恢复时层级可能为空的问题。

3. **2025-10-01** `063444dfe1f8` — Register Motion Trail Commands early (UE-346120)
   - 提前注册 Motion Trail 命令，修复启动时序问题。

### 维护评价

- **活跃维护** ✅ — 最近一次更新在 2025 年 11 月，约 5 个月前
- 从 2021 年 7 月创建至今持续更新，功能不断完善（新增 Control Rig 支持、多 Rig 支持等）
- 近期更新集中在 bug 修复和功能扩展，说明 Epic 内部有实际使用
- 作为 Editor 工具，依赖 Sequencer 和 ControlRig 等核心模块，Epic 有维护动力
- **推荐使用** — 这是 Sequencer 动画编辑的核心工具集，几乎是高级 Sequencer 用户的必备功能

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/SequencerAnimTools)
- 官方文档（无）
