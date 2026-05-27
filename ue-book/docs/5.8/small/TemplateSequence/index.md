# Template Sequence

> Runtime for template sequences

| 属性 | 值 |
|---|---|
| 中文名 | 模板序列 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TemplateSequence` (Runtime), `TemplateSequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

TemplateSequence 插件是 **Unreal Engine 中 Sequencer（定序器）系统的高级扩展**。它解决的核心问题是**动画序列的复用与模板化**。

-   **核心概念**：它引入了“模板序列”的概念，即一个预录制的、包含复杂对象变换、属性动画、事件等内容的序列。这个序列可以作为一个**模板**，被快速应用到其他场景中的同类对象上。
-   **解决的问题**：传统的 Level Sequence 与场景对象绑定较死。如果需要为多个相似角色（如同类型敌人）创建复杂但模式相同的动画（如一套攻击动画），手动为每个角色创建独立序列效率低下且难以维护。TemplateSequence 允许你创建一套“标准”的动画模板，然后通过简单的配置或代码驱动，将其应用到多个目标对象上，实现了动画逻辑与具体对象的**解耦**和**复用**。
-   **存在价值**：它是为需要**批量化、可配置化管理复杂动画**的项目准备的工具，尤其适用于有大量行为相似的 AI 角色或可交互物体的游戏项目。它将 Sequencer 的动画能力从“场景录制”提升到了“可编程的动画资产”层面。

## 使用场景

-   你在为大量同类型敌人（如小兵、动物）创建复杂的攻击、受击、死亡动画序列 → 用 TemplateSequence 创建一个动画模板，然后应用到所有敌人上。
-   你需要制作一个可交互的物体（如机关门、移动平台），其动画逻辑在不同关卡或实例中需要微调（如移动速度、延迟） → 用 TemplateSequence 作为基础模板，通过参数化覆盖来定制。
-   你在开发过程中需要快速预览和迭代角色动画，而不希望每次都重新绑定到具体场景模型 → 使用 TemplateSequence 脱离具体场景对象进行动画编辑和测试。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `TemplateSequence` | Runtime | 提供模板序列的核心运行时数据结构、播放器和组件，用于在运行时加载和应用模板序列。 |
| `TemplateSequenceEditor` | Editor | 提供在编辑器中创建、编辑和预览模板序列的工具、资产类型和自定义界面。 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Template Sequence Player` | 创建一个用于播放模板序列的播放器实例。 | `UTemplateSequenceSubsystem` |
| `Play` / `Stop` / `Pause` | 控制模板序列的播放状态。 | `UTemplateSequencePlayer` |
| `Set Sequence` | 为播放器设置要播放的模板序列资产。 | `UTemplateSequencePlayer` |
| `Set Bound Actor` | 将播放器绑定到一个场景中的 Actor，模板序列将驱动该 Actor 的属性和变换。 | `UTemplateSequencePlayer` |
| `Add to Player` / `Remove from Player` | 将模板序列组件（作为子序列）添加或移除自一个父序列播放器。 | `UTemplateSequenceComponent` |

### 使用示例（蓝图描述）

1.  **在角色蓝图中播放**：
    - 在角色蓝图中添加一个 `Template Sequence Component`。
    - 在 BeginPlay 事件中，使用 `Set Sequence` 节点为该组件指定一个 `UTemplateSequence` 资产。
    - 调用组件的 `Play` 节点开始播放，角色将按照模板序列中的设定进行动画。

2.  **动态控制多个实例**：
    - 使用 `Create Template Sequence Player` 节点（通常在一个管理器 Actor 或 Subsystem 中）创建多个播放器实例。
    - 通过循环和 `Set Bound Actor` 节点，将每个播放器实例分别绑定到场景中不同的敌人 Actor 上。
    - 然后分别调用 `Play`，即可让所有敌人播放同一套模板动画，但绑定在各自不同的目标上。

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequenceSubsystem.h"
#include "TemplateSequencePlayer.h"
#include "Sections/MovieSceneTemplateSequenceSection.h"
```

### 基本用法

```cpp
// 获取模板序列子系统（需在运行时）
UTemplateSequenceSubsystem* TemplateSeqSubsystem = GetWorld()->GetSubsystem<UTemplateSequenceSubsystem>();
if (TemplateSeqSubsystem)
{
    // 创建一个播放器
    UTemplateSequencePlayer* Player = TemplateSeqSubsystem->CreateTemplateSequencePlayer(TemplateSequenceAsset, FMovieSceneSequencePlaybackSettings(), TemplateSequencePlayerOut);
    if (Player)
    {
        // 绑定到目标 Actor
        Player->SetBoundActor(TargetActor);
        // 开始播放
        Player->Play();
    }
}
```

### 进阶用法

结合模板序列组件，在 Actor 中直接管理和播放：

```cpp
// MyCharacter.h
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
UTemplateSequenceComponent* AttackAnimationComponent;

// MyCharacter.cpp (BeginPlay)
if (AttackTemplateSequenceAsset)
{
    AttackAnimationComponent->SetSequence(AttackTemplateSequenceAsset);
    // 可以订阅播放完成事件
    FMovieSceneSequenceDelegate& OnFinished = AttackAnimationComponent->GetSequencePlayer()->OnFinished;
    OnFinished.AddDynamic(this, &AMyCharacter::OnAttackAnimationFinished);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequence` | 核心的定序器播放和数据结构支持。 |
| `LevelSequenceEditor` | 提供基础的定序器编辑器框架。 |
| `MovieScene` | Sequencer 的底层场景和轨道系统。 |
| `MovieSceneTools` | 编辑器中的 Sequencer 工具和编辑功能。 |
| `TemplateSequence` (Runtime) | 本插件的核心运行时模块。 |
| `TemplateSequenceEditor` (Editor) | 本插件的编辑器模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 宏，属于日志系统更新。 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复了由于包含仅编辑器数据属性而导致的 Level Sequence Player 网络复制布局不匹配问题。 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | 在 Sequencer 的对象绑定菜单中添加了“烘焙变换”功能。 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 从 UObject 中移除了7个虚拟函数（已弃用或仅用于工具），属于底层重构。 |

### 维护评价

-   **状态**：**维护中**。插件在2019年创建，至今已有约7年历史。虽然状态标记为实验性且默认未启用，但从近一年的提交记录看，仍有持续的维护活动，包括编译问题修复、网络同步Bug修复以及跟随引擎核心（如日志、UObject）的更新。
-   **活跃度**：近期（6个月内）有实质性更新，主要围绕**稳定性**（修复警告、网络复制）和**功能增强**（添加烘焙变换）。
-   **建议**：该插件功能专一且强大，适用于需要深度使用 Sequencer 进行动画模板化管理的项目。由于其**实验性**和**默认禁用**的特性，建议在决定采用前，先在测试项目中充分评估其稳定性和与现有工作流的契合度。它并非一个“即插即用”的通用动画系统，而是面向特定高级需求的工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
-   官方文档：无 (`.uplugin` 中 `DocsURL` 为空)
-   测试用例：通常位于 `Engine/Plugins/MovieScene/TemplateSequence/Tests/` 目录下。