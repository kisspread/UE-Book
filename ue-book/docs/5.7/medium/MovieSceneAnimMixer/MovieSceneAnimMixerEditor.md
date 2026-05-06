# Sequencer Anim Mixer

> System for mixing layered animation in sequences

| 属性 | 值 |
|---|---|
| 中文名 | 序列动画混合器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画蓝图节点、蓝图扩展、编辑器轨道） |
| 模块 | `MovieSceneAnimMixer` (Runtime), `MovieSceneAnimMixerEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneAnimMixer) | |

## 用途

**Sequencer Anim Mixer** 提供了一套在 Sequencer（过场动画）中混合分层动画的系统。它允许将多个动画序列或姿势以分层方式叠加在同一条轨道上，并配合动画蓝图（UAF 框架）驱动角色融合。该插件解决了传统 Sequencer 动画轨道只能播放单一动画序列的限制，支持更复杂的动画混合需求，例如：基础行走动画上叠加瞄准或受伤反应。

插件通过以下方式实现：
- 自定义的 `FAnimationMixerTrackEditor`，在 Sequencer 轨道面板中提供“动画混合”轨道类型。
- 动画蓝图扩展 `UAnimBlueprintExtension_SequencerMixerTarget`，桥接 Sequencer 和动画蓝图的数据。
- 动画蓝图节点 `UAnimGraphNode_SequencerMixerTarget`，允许在动画蓝图中声明一个混合目标，接收来自 Sequencer 的混合指令。

## 使用场景

- 当需要在 Sequencer 中对同一角色应用**多层动画**（例如：跑步 + 挥手）时，使用动画混合轨道替代传统单层动画轨道。
- 将 Sequencer 驱动的动画与动画蓝图中的状态机、蒙太奇等混合逻辑结合，实现过场动画与实时动画的平滑过渡。
- 在复杂的过场动画中，对角色肢体进行精细控制（例如：上半身播放开枪动画，下半身保持行走）。

## 蓝图用法

本插件为编辑器模块，主要提供 Sequencer 轨道和动画蓝图节点，未暴露直接的蓝图可调用函数。但在**动画蓝图**中可以通过 `SequencerMixerTarget` 节点接入混合数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Sequencer Mixer Target` | 声明一个动画混合目标，可接收外部（Sequencer）提供的动画姿势并叠加到最终姿态上。 | `UAnimGraphNode_SequencerMixerTarget` |

### 使用示例（蓝图描述）

1. 打开角色的动画蓝图，在事件图表中添加 **Sequencer Mixer Target** 节点（位于“AnimGraph”类别下）。
2. 将 **Final Animation Pose** 引脚连接到输出姿势针脚（如 `Result`）。
3. 在该节点的细节面板中，可以设置节点名称、混合权重等属性（具体属性取决于运行时的 `FAnimNode_SequencerMixerTarget` 结构，但该结构当前仅包含默认设置）。
4. 在 Sequencer 中为角色添加“Animation Mixer”轨道，并指定该节点名称以驱动混合。

> 注意：当前插件处于实验阶段，节点名称与 Sequencer 轨道的绑定机制尚未完全公开。

## C++ 用法

### 头文件引入

```cpp
#include "AnimBlueprintExtension_SequencerMixerTarget.h"
#include "AnimGraphNode_SequencerMixerTarget.h"
#include "MovieSceneAnimationMixerTrackEditor.h"
```

### 基本用法

**在 Sequencer 中注册自定义的混合动画段落**

```cpp
// 在模块启动时注册一个自定义段落创建委托
void FMyModule::StartupModule()
{
    using namespace UE::Sequencer;
    // 假设 MySectionClass 是 UMovieSceneSection 的子类
    FAnimationMixerTrackEditor::RegisterCustomMixerAnimSection(
        MySectionClass::StaticClass(),
        FOnMakeSectionInterfaceDelegate::CreateLambda([](UMovieSceneSection& Section, UMovieSceneTrack& Track, FGuid ObjectBinding) -> TSharedRef<ISequencerSection> {
            return MakeShared<FMySectionInterface>(Section, Track, ObjectBinding);
        })
    );
}

void FMyModule::ShutdownModule()
{
    UE::Sequencer::FAnimationMixerTrackEditor::UnregisterCustomMixerAnimSection(MySectionClass::StaticClass());
}
```

来源：`MovieSceneAnimationMixerTrackEditor.h` 中的 `RegisterCustomMixerAnimSection` / `UnregisterCustomMixerAnimSection` 静态方法。

**在动画蓝图中获取扩展**

```cpp
// 在动画蓝图编译时获取扩展
const UAnimBlueprintExtension_SequencerMixerTarget* Extension = Cast<UAnimBlueprintExtension_SequencerMixerTarget>(AnimBlueprint->GetExtension());
if (Extension)
{
    const FAnimSubsystem_SequencerMixer& Subsystem = Extension->Subsystem;
    // 使用子系统数据...
}
```

来源：`AnimBlueprintExtension_SequencerMixerTarget.h`。

### 进阶用法

**创建自定义动画混合轨道编辑器**

继承 `UE::Sequencer::FAnimationMixerTrackEditor` 或直接使用其静态方法创建轨道编辑器实例：

```cpp
TSharedRef<ISequencerTrackEditor> MyTrackEditor = UE::Sequencer::FAnimationMixerTrackEditor::CreateTrackEditor(SequencerPtr.ToSharedRef());
```

来源：`MovieSceneAnimationMixerTrackEditor.h`。

## Demo 示例

以下是一个最小化的 C++ 模块示例，展示如何在插件中注册自定义轨道编辑器并添加自定义段落类型。

```cpp
// MyModule.h
#pragma once
#include "Modules/ModuleInterface.h"

class FMyAnimMixerModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyModule.cpp
#include "MyModule.h"
#include "MovieSceneAnimationMixerTrackEditor.h"
#include "ISequencerModule.h"
#include "ISequencer.h"

IMPLEMENT_MODULE(FMyAnimMixerModule, MyAnimMixerModule);

void FMyAnimMixerModule::StartupModule()
{
    // 获取 Sequencer 模块并注册轨道编辑器
    ISequencerModule& SequencerModule = FModuleManager::LoadModuleChecked<ISequencerModule>("Sequencer");
    SequencerModule.RegisterTrackEditor(
        FOnCreateTrackEditor::CreateStatic(&UE::Sequencer::FAnimationMixerTrackEditor::CreateTrackEditor)
    );
}

void FMyAnimMixerModule::ShutdownModule()
{
    // 清理注册（可选）
}
```

你的模块 `.Build.cs` 需要添加依赖项（见下一节）。

## 模块依赖

由于该插件直接依赖了 `UAF` 和 `UAFAnimGraph`（Unreal Animation Framework），使用本插件的模块必须添加这些依赖。同时，编辑器模块需要 `Sequencer`、`MovieScene` 等常见依赖（已省略）。

| 模块 | 用途 |
|---|---|
| `UAF` | Unreal Animation Framework 运行时模块 |
| `UAFAnimGraph` | 动画蓝图编译所需的扩展图功能 |

> 如果你的模块只需使用运行时功能（无编辑器），则只需要依赖 `MovieSceneAnimMixer` 和 `UAF`，不需要 `UAFAnimGraph` 和 `MovieSceneAnimMixerEditor`。

## 维护状态

### 近期更新

- 2025-10-01 142f8a80 Sequencer: Partial back out of 42444020 and 42182253 which added UnbindFromSkeletalMeshComponent in
- 2025-09-03 83133567 Sequencer: Fix issue where when changing shots we could sometimes get one frame of t-pose on a character
- 2025-09-03 072d3134 Sequencer: Minor Stitch Track UX fixes.
- 2025-09-02 78089693 Add scoped named event for UAF pose evaluation
- 2025-08-20 8dd5bb75 Sequencer: Improved property traits variants, added type-erased property values, and unified many property...

### 维护评价

属于 **🆕 新插件**，2025-08 创建，至今每月都有实质性更新，包括功能改进和 Bug 修复。目前处于**实验性**阶段（`IsExperimentalVersion: true`），API 可能发生变化。Epic 正在积极开发，推荐在原型或实验项目中使用，但谨慎用于正式发布产品。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneAnimMixer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneAnimMixer/Tests)（若存在）