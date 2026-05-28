# Sequencer Anim Mixer

> System for mixing layered animation in sequences

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer动画混合器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Slate SVG图标资源） |
| 模块 | `MovieSceneAnimMixer` (Runtime), `MovieSceneAnimMixerEditor` (Runtime), `MovieSceneAnimMixerScripting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieSceneAnimMixer) | |

## 用途

这是一个 Sequencer 中的**分层动画混合系统**，提供了与传统骨骼动画轨道不同的处理路径。它将动画生产和混合过程模块化，核心设计理念包括：

- **多类型动画生产轨道**：支持动画序列（AnimSequence）、ControlRig，以及未来可能的空闲动画、面部动画、注视动画、动作匹配等
- **多类型动画目标（Animation Target）**：所有发送到同一目标的动画会被混合（未来支持遮罩混合）
- **基于 Evaluation Program 的执行**：使用 AnimNext 的"求值任务"系统，将求值任务列表编译为一个程序，共享 VM 内存执行，内存中维护一个"姿态关键帧栈"
- **根运动独立处理**：根运动可以作为属性单独提取和混合，确保 Sequencer 中时间跳转时的确定性

与传统 Sequencer 动画轨道相比，这个插件将动画混合逻辑从各个轨道中解耦，使得不同类型的动画源（序列、Rig、未来类型）可以通过统一的混合管线输出到不同类型的动画目标（自定义 AnimInstance、蓝图 Slot、AnimNext 注入点等）。

## 使用场景

- 你需要在 Sequencer 中同时混合多个不同来源的动画 → 用此插件的分层混合架构
- 你需要将骨骼动画、ControlRig、未来类型的动画统一混合 → 用 Animation Mixer Track 管理混合层
- 你需要在 Sequencer 中精确控制根运动 → 根运动可作为独立属性混合，支持骨骼匹配和偏移编辑
- 你需要将混合后的动画烘焙为 AnimSequence 或 ControlRig → 使用内置的烘焙系统
- 你需要在 Anim Blueprint 中接收 Sequencer 的混合动画 → 使用 `SequencerMixerTarget` 动画图节点

## 蓝图用法

此插件主要通过 Sequencer 编辑器 UI 操作，运行时部分通过动画图节点接入。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SequencerMixerTarget` | 动画图节点，用于在 Anim Blueprint 中定义 Sequencer 混合器的注入目标 | `UAnimGraphNode_SequencerMixerTarget` |

### Sequencer 工作流

1. **创建混合器轨道**：在对象绑定上右键 → Add Animation Track → 选择 Mixer Track，并指定目标类型（Automatic / Custom AnimInstance / Anim Blueprint / AnimNext Injection / Bus）
2. **管理混合层**：在 Mixer Track 内创建多个 Layer，每个 Layer 可包含多个动画片段或一个子轨道（如 ControlRig）
3. **配置根运动**：在片段的装饰（Decoration）中添加 Root Motion Settings，配置根运动目标和骨骼匹配
4. **添加遮罩**：通过 Decoration 菜单添加 Blend Mask，实现选择性骨骼混合
5. **烘焙动画**：右键 → Bake → 选择烘焙到 AnimSequence 或 ControlRig

### 动画目标类型

| 目标类型 | 说明 |
|---|---|
| Automatic | 自动选择合适的求值目标 |
| Custom Anim Instance | 使用自定义 AnimInstance 代理求值 |
| Anim Blueprint | 在 Anim Blueprint 中通过 `SequencerMixerTarget` 节点接收 |
| AnimNext Injection | 通过 AnimNext 组件的注入点接收 |
| Bus | 通过总线路由到其他混合器轨道 |

## C++ 用法

### 头文件引入

```cpp
#include "AnimMixerBakeHelper.h"
#include "AnimGraphNode_SequencerMixerTarget.h"
#include "AnimBlueprintExtension_SequencerMixerTarget.h"
```

### 烘焙混合动画到 AnimSequence

来自 `Public/AnimMixerBakeHelper.h`：

```cpp
#include "AnimMixerBakeHelper.h"

// 将 Animation Mixer 轨道的求值结果烘焙到 AnimSequence
void BakeMixerToAnimSequence(TSharedPtr<ISequencer> Sequencer, UMovieSceneAnimationMixerTrack* MixerTrack)
{
    UAnimSequence* AnimSequence = /* 创建或获取目标动画序列 */;
    UAnimSeqExportOption* ExportOptions = GetDefault<UAnimSeqExportOption>();
    USkeletalMeshComponent* SkelMeshComp = /* 获取骨骼网格组件 */;
    
    // 使用空 Filter 烘焙整个轨道
    bool bSuccess = UE::Sequencer::AnimMixerBake::ExportMixerToAnimSequence(
        Sequencer,
        AnimSequence,
        ExportOptions,
        SkelMeshComp,
        MixerTrack
    );
    
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Bake to AnimSequence completed successfully"));
    }
}
```

### 构建烘焙菜单

来自 `Public/AnimMixerBakeHelper.h`：

```cpp
// 在自定义编辑器中构建完整的烘焙菜单
void BuildBakeMenu(FMenuBuilder& MenuBuilder, TSharedPtr<ISequencer> Sequencer,
    UMovieSceneAnimationMixerTrack* MixerTrack, USkeletalMeshComponent* SkelMeshComp,
    USkeleton* Skeleton, FGuid ObjectBinding, UObject* BoundObject)
{
    bool bFilterAssetBySkeleton = true;
    
    UE::Sequencer::AnimMixerBake::BuildBakeMenuSection(
        MenuBuilder,
        Sequencer,
        MixerTrack,
        SkelMeshComp,
        Skeleton,
        ObjectBinding,
        BoundObject,
        bFilterAssetBySkeleton,
        /* Filter */ {},                    // 空 = 烘焙整个轨道
        /* ChildTrackFactory */ nullptr,     // 用于创建子轨道的工厂
        /* OnComplete */ nullptr,            // 烘焙后回调
        FText::FromString(TEXT("Bake"))
    );
}
```

### 注册自定义 Mixer 轨道编辑器

来自 `Private/MovieSceneAnimationMixerTrackEditor.h`：

```cpp
#include "MovieSceneAnimationMixerTrackEditor.h"

// 注册自定义 section 界面的回调
static FOnMakeSectionInterfaceDelegate MakeInterfaceDelegate;
MakeInterfaceDelegate.BindLambda([](UMovieSceneSection& Section, UMovieSceneTrack& Track, FGUID ObjectBinding) -> TSharedRef<ISequencerSection>
{
    return MakeShared<FMyCustomSection>(Section, Track, ObjectBinding);
});

UE::Sequencer::FAnimationMixerTrackEditor::RegisterCustomMixerAnimSection(
    UMyCustomSection::StaticClass(),
    MakeInterfaceDelegate
);
```

### 注册自定义动画目标菜单提供者

```cpp
#include "IMovieSceneAnimMixerTargetMenuProvider.h"

// 实现自定义目标菜单提供者
class FMyCustomTargetMenuProvider : public IMovieSceneAnimMixerTargetMenuProvider
{
public:
    virtual UScriptStruct* GetHandledTargetStructType() const override
    {
        return FMyCustomAnimationTarget::StaticStruct();
    }
    
    virtual void PopulateTargetMenu(
        FMenuBuilder& MenuBuilder,
        TObjectPtr<UObject> BoundObject,
        TFunction<void(TInstancedStruct<FMovieSceneMixedAnimationTarget>)> OnTargetSelected) override
    {
        MenuBuilder.AddMenuEntry(
            FText::FromString(TEXT("My Custom Target")),
            FText::GetEmpty(),
            FSlateIcon(),
            FUIAction(FExecuteAction::CreateLambda([=]()
            {
                TInstancedStruct<FMovieSceneMixedAnimationTarget> Target;
                // 配置 Target ...
                OnTargetSelected(Target);
            }))
        );
    }
    
    virtual int32 GetTargetMenuPriority() const override { return 100; }
};
```

## Demo 示例

### 动画图节点集成

在 Anim Blueprint 中使用 `SequencerMixerTarget` 节点接收 Sequencer 混合动画：

```cpp
// MyAnimInstance.h
#pragma once
#include "Animation/AnimInstance.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 在 Anim Blueprint 编辑器中添加 SequencerMixerTarget 节点
    // 该节点会自动从 Sequencer 接收混合后的动画程序并应用到姿态
    
    // 可选：通过扩展注册确保 Sequencer 可以找到注入目标
    // GetRequiredExtensions 会自动添加 UAnimBlueprintExtension_SequencerMixerTarget
};
```

对应的 Anim Blueprint 中：
1. 在动画图中添加 `SequencerMixerTarget` 节点
2. 节点会自动注册为 Sequencer 混合器的目标
3. Sequencer 播放时，混合后的求值程序会注入到该节点

### 根运动设置装饰

```cpp
// 在 Sequencer 中配置根运动时，可以通过代码操作 Root Motion Settings Decoration
#include "RootMotionSettingsDecorationEditor.h"

// 编辑器模块自动处理以下工作：
// - 根运动轨迹可视化（Trail）
// - 根运动偏移关键帧编辑
// - 骨骼匹配对话框
// - 根运动重中心化
// 这些功能通过 Decoration Editor 系统自动集成到 Sequencer UI
```

## 模块依赖

从 Build.cs 分析，`MovieSceneAnimMixer` 核心模块依赖 `Settings`。编辑器模块和脚本模块的具体依赖未在提供信息中展示。

| 模块 | 用途 |
|---|---|
| `Settings` | 项目/插件配置设置支持 |

编辑器模块 (`MovieSceneAnimMixerEditor`) 隐含依赖以下 UE 标准动画/Sequencer 模块（基于头文件引用推断）：

| 模块 | 用途 |
|---|---|
| `AnimGraph` | 动画蓝图图编辑器支持 |
| `SequencerAnimTools` | Sequencer 动画轨迹可视化工具 |
| `AnimationCore` | 动画核心数据结构（根骨骼变换等） |

> 由于三个模块均标记为 Runtime 类型，无特殊依赖限制。使用烘焙功能和编辑器 UI 时需确保编辑器环境可用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `00f154d0` | Sequencer Anim Mixer: fix root motion pop at boundary between a KeepState section and an Accumulated | 修复 KeepState 与 Accumulate 段边界处根运动跳变问题 |
| 2026-05-26 | `8905e197` | Sequencer: Fix Anim Mixer section gizmo freezing when dragged with AutoKey Off | 修复关闭自动关键帧时拖拽 Gizmo 冻结的问题 |
| 2026-05-22 | `5f14e324` | Sequencer: Anim Mixer: force-link CachePreAnimatedStateSystem from AnimMixerSystem | 强制链接动画混合系统的预动画状态缓存系统 |
| 2026-05-22 | `5515824d` | Sequencer: Anim mixer fix InitialRoot mismatch between cache and runtime that slid character across | 修复缓存与运行时初始根骨骼不匹配导致角色滑动的问题 |
| 2026-05-22 | `5c05fad6` | Sequencer: Anim mixer- fix issue where following a section with an anim with rotation in the offset | 修复动画片段偏移中存在旋转时的跟随问题 |

### 维护评价

- **创建时间**：2025-01-14，约 1 年前
- **最近更新频率**：非常活跃，最近一周内（2026-05-22 至 2026-05-26）有 5 次提交，集中修复根运动和混合相关 bug
- **维护状态**：🔴 **活跃开发中** — 这是一个正在进行中的实验性系统，近期修复集中在根运动混合的边界情况和编辑器交互稳定性
- **已知限制**：
  - 尚未支持运动矢量模拟和镜像功能
  - 零权重任务尚未被优化剔除
  - 尚未利用"源姿态"作为可混合的基础姿态
  - UX 方面还需要改进（计划中的 Mixer Track 可以将旧轨道作为子轨道）
- **推荐程度**：⚠️ **仅供实验使用** — 标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，需要手动启用。API 和功能可能在后续版本中发生重大变更。适合对 Sequencer 动画管线有深入了解的开发者提前探索，不建议在生产项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieSceneAnimMixer)
- [官方文档]()（暂无）