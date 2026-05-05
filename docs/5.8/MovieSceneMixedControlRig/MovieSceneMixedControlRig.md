# Sequencer Mixed Control Rig

> System for using the Anim Mixer to mix control rig tracks

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画混合器相关资产） |
| 模块 | `MovieSceneMixedControlRig` (Runtime), `MovieSceneMixedControlRigEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneMixedControlRig) | |

## 用途

该插件为 Unreal Engine 的 Sequencer（定序器）提供了一套系统，用于将 Control Rig（控制绑定）轨道与动画混合器（Anim Mixer）集成。其核心目的是解决在 Sequencer 时间轴上混合多个 Control Rig 动画轨道的问题。通过此系统，用户可以在 Sequencer 中利用动画混合器的强大功能，对 Control Rig 驱动的动画进行分层、混合和过渡，从而实现更复杂、更平滑的动画效果，而无需编写复杂的蓝图或 C++ 逻辑来手动处理混合。

## 使用场景

- 你在制作一个过场动画，需要让角色从一个基于 Control Rig 的姿势（如持枪瞄准）平滑过渡到另一个姿势（如挥手），并且希望这个过渡过程在 Sequencer 时间轴上可控。
- 你正在为角色创建复杂的动画状态机，其中多个 Control Rig 轨道（如面部表情、身体 IK）需要根据游戏逻辑或时间轴进行动态混合。
- 你需要将传统的骨骼动画序列与 Control Rig 生成的程序化动画在 Sequencer 中进行无缝融合。

## 蓝图用法

该插件主要提供底层的运行时系统，其功能通常通过 Sequencer 编辑器界面和动画混合器进行操作，而非直接暴露蓝图节点。其核心价值在于扩展 Sequencer 的能力，而非提供新的蓝图 API。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接公开蓝图节点） | 该插件的功能通过 Sequencer 的动画混合器界面和 Control Rig 轨道进行交互。 | - |

### 使用示例（蓝图描述）

1.  在 Sequencer 中为你的角色 Actor 添加一个 Control Rig 轨道。
2.  在该轨道上添加多个 Control Rig 动画片段（Clips）。
3.  打开动画混合器面板（通常在 Sequencer 窗口的底部或侧边）。
4.  你会看到 Control Rig 轨道的动画片段出现在混合器中，可以像混合普通动画序列一样，通过调整权重、添加过渡曲线等方式来混合它们。

## C++ 用法

该插件的核心是一个运行时系统，负责在 Sequencer 评估过程中为动画混合器创建和管理 Control Rig 的评估任务。

### 头文件引入

```cpp
#include "Systems/MovieSceneMixedControlRigSystem.h"
```

### 基本用法

该插件主要通过其注册的系统自动工作。开发者通常不需要直接实例化或调用 `UMovieSceneMixedControlRigSystem`。它的生命周期由 Sequencer 的实体系统管理。

```cpp
// 该系统由 Sequencer 的实体系统自动创建和调度。
// 以下代码仅为演示其存在形式，实际使用中无需手动操作。
// 来源: Public/Systems/MovieSceneMixedControlRigSystem.h

// 系统类声明
UCLASS(MinimalAPI)
class UMovieSceneMixedControlRigSystem : public UMovieSceneEntityInstantiatorSystem
{
    GENERATED_BODY()
    // ...
};
```

### 进阶用法

对于需要扩展或调试此系统的开发者，可以关注其重写的虚函数 `OnRun` 和 `OnSchedulePersistentTasks`。这些函数定义了系统如何参与 Sequencer 的评估任务调度。

```cpp
// 系统的核心调度逻辑（概念性代码，非直接调用）
// 来源: Public/Systems/MovieSceneMixedControlRigSystem.h

void UMovieSceneMixedControlRigSystem::OnRun(FSystemTaskPrerequisites& InPrerequisites, FSystemSubsequentTasks& Subsequents)
{
    // 在此处，系统会为动画混合器中混合的 Control Rig 轨道创建具体的评估任务。
    // 这些任务负责计算最终的 Control Rig 输出。
}

void UMovieSceneMixedControlRigSystem::OnSchedulePersistentTasks(UE::MovieScene::IEntitySystemScheduler* TaskScheduler)
{
    // 注册需要持续存在的任务，这些任务可能在整个 Sequencer 评估周期内保持活动。
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在自己的模块中依赖并使用此插件提供的系统。请注意，这主要用于扩展或集成目的。

**MyAnimModule.Build.cs (片段)**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "MovieScene",
    "MovieSceneMixedControlRig" // 依赖此插件模块
});
```

**MyCustomAnimProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "MyCustomAnimProcessor.generated.h"

// 一个假设的自定义动画处理器，可能需要与混合后的 Control Rig 数据交互。
UCLASS()
class UMyCustomAnimProcessor : public UObject
{
    GENERATED_BODY()

public:
    // 此函数可能在 Sequencer 评估后被调用，以处理混合后的 Control Rig 结果。
    // 具体的交互方式取决于插件未来暴露的接口。
    void ProcessMixedControlRigOutput(/* 参数待定 */);
};
```

**MyCustomAnimProcessor.cpp**
```cpp
#include "MyCustomAnimProcessor.h"
// 可能需要包含插件的特定头文件来访问混合后的数据结构
// #include "Systems/MovieSceneMixedControlRigSystem.h"

void UMyCustomAnimProcessor::ProcessMixedControlRigOutput(/* 参数待定 */)
{
    // 在这里处理来自动画混合器的、经过混合的 Control Rig 数据。
    // 例如，将结果应用到额外的骨骼网格体或驱动其他游戏逻辑。
}
```

## 模块依赖

从模块名称和功能推断，该插件依赖于 Sequencer 和 Control Rig 的核心模块。

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 的核心运行时模块，提供实体系统和评估框架。 |
| `ControlRig` | Control Rig 运行时模块，提供控制绑定的创建和评估功能。 |
| `AnimationCore` | 提供动画系统所需的核心数据结构和算法。 |

## 维护状态

### 近期更新

- 2026-04-21 `eb0331ca` Anim Mixer: Bake To Control Rig and Anim Sequence support for anim mixer for binding, mixer track an
- 2026-04-17 `62f614c6` Sequencer: Fix Control Rig gizmo drawing offset in Animation Mixer with multi-layer root motion
- 2026-04-07 `8bf4fb4b` Sequencer: Restructure mixer evaluation around layers; new mask blend system
- 2026-03-31 `b48e7f74` Fix shutdown issue with MovieScene
- 2026-03-31 `c7aaaa03` Sequencer: Enable root motion extraction for control rig in Animation Mixer.

### 维护评价

- **创建时间**：非常新（2026年创建），属于前沿实验性功能。
- **最近更新频率**：未知，但作为实验性插件，更新可能不频繁且专注于功能验证。
- **活跃维护**：状态未知。实验性插件可能随时被修改、合并到主分支或废弃。
- **已知问题或限制**：作为实验性功能，可能存在稳定性问题、API 不完整或与特定 Control Rig 设置不兼容的情况。
- **推荐使用**：**谨慎使用**。仅推荐用于原型开发、技术预研或对动画混合有高级需求的项目。不建议在需要长期稳定维护的生产项目中作为核心功能依赖。使用前请务必在项目中进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneMixedControlRig)
- 官方文档：暂无
- 测试用例：暂无公开的测试用例路径。