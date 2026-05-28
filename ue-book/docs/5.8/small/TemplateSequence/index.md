# Template Sequence

> Runtime for template sequences（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 模板序列 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TemplateSequence` (Runtime), `TemplateSequenceEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

Template Sequence 插件为 Unreal Engine 的 Sequencer 系统提供了一种创建和实例化“模板序列”的能力。其核心解决的问题是动画片段的**高效复用和版本控制**。

在游戏开发中，常常需要让多个不同的角色或对象执行相同或类似的动画序列（如通用的待机、受击、死亡动画）。传统方法是复制整个 Level Sequence 资产，但这会导致资产冗余且难以统一修改。Template Sequence 允许你创建一个主模板（Template Sequence），然后在具体的 Level Sequence 中创建它的**实例（Instance）**。对主模板的修改会自动传播到所有实例，极大地提升了动画资产的维护效率。

## 使用场景

-   **角色动画复用**：你正在开发一个有数十种敌人的游戏，其中大部分敌人共享相同的“死亡”动画。使用 Template Sequence 创建一个“通用死亡”模板，为每个敌人的 Level Sequence 引用它，实现统一管理。
-   **复杂过场动画同步**：在一个多人过场动画中，多名NPC需要同时做出相似但略有差异的动作。你可以创建一个基础动作模板，然后在不同NPC的序列中实例化并微调。
-   **动态动画组装**：在游戏运行时，需要根据条件为某个对象动态切换不同的动画序列。使用 Template Sequence 可以方便地管理这些动画模板。

## 蓝图用法

Template Sequence 在蓝图中主要通过 `UTemplateSequence` 和相关的 Actor/Component 类进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Template Sequence` | 创建一个新的模板序列资产 | `UTemplateSequence` |
| `Get Template Sequence` | 从实例获取其引用的主模板序列 | `UTemplateSequenceInstance` |
| `Set Template Sequence` | 为一个模板序列实例设置新的主模板 | `UTemplateSequenceInstance` |
| `Create Template Sequence Player` | 创建一个用于播放模板序列的播放器 | `UTemplateSequencePlayer` |

### 使用示例（蓝图描述）

1.  **创建与使用模板**：使用 `Create Template Sequence` 节点在蓝图中创建一个模板序列。然后，通过 `Create Level Sequence Player` 节点创建一个播放器，将模板序列作为资产传入，即可播放。
2.  **在场景中放置**：从放置面板拖入一个 `Template Sequence Actor` 到场景。在其细节面板中指定一个模板序列资产，即可在场景中预览和播放该模板序列动画。

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequence.h"
// 对于编辑器功能
#include "ITemplateSequenceModule.h"
```

### 基本用法

以下代码演示了如何在 C++ 中创建和播放一个模板序列。此示例逻辑源于引擎测试用例 `TemplateSequenceTest.cpp`。

```cpp
// 来源于测试用例：TemplateSequenceTest.cpp
void CreateAndPlayTemplateSequence()
{
    // 1. 创建模板序列资产
    UTemplateSequence* TemplateSeq = NewObject<UTemplateSequence>();
    TemplateSeq->Initialize();

    // 2. 为模板序列创建一个播放器
    UTemplateSequencePlayer* Player = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
        TemplateSeq,
        FTemplateSequencePlayerSettings(), // 播放设置
        /*InOwnerObject*/ this // 播放器的所有者，通常是当前 Actor 或组件
    );

    // 3. 开始播放
    if (Player)
    {
        Player->Play();
    }
}
```

### 进阶用法

结合 `UTemplateSequenceActor`，可以在世界中方便地放置和管理模板序列实例。以下代码展示了如何动态生成一个 Template Sequence Actor 并绑定模板序列。

```cpp
// 来源于测试用例：TemplateSequenceActorTest.cpp
void SpawnTemplateSequenceActor()
{
    UWorld* World = GetWorld();
    if (!World) return;

    // 1. 生成一个 Template Sequence Actor
    ATemplateSequenceActor* Actor = World->SpawnActor<ATemplateSequenceActor>(
        ATemplateSequenceActor::StaticClass(),
        FVector::ZeroVector,
        FRotator::ZeroRotator
    );

    // 2. 假设我们已经有一个创建好的模板序列资产
    UTemplateSequence* MyTemplate = /* ... 获取或创建模板序列 ... */;

    // 3. 将模板序列赋值给 Actor
    if (Actor && MyTemplate)
    {
        Actor->SetSequence(MyTemplate);
        // 可以进一步设置播放策略，如是否循环、自动播放等
        Actor->SetPlaybackSettings(FTemplateSequencePlaybackSettings(/*bLoop=*/true));
        Actor->PlaySequence();
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在 Actor 的 `BeginPlay` 中播放一个模板序列。

**MyActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TemplateSequencePlayer.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UTemplateSequencePlayer* TemplatePlayer;

    UPROPERTY(EditAnywhere, Category = "Animation")
    UTemplateSequence* TemplateSequenceToPlay;
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "TemplateSequencePlayer.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    if (TemplateSequenceToPlay)
    {
        // 创建播放器并开始播放
        TemplatePlayer = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
            TemplateSequenceToPlay,
            FTemplateSequencePlayerSettings(),
            this
        );

        if (TemplatePlayer)
        {
            TemplatePlayer->Play();
        }
    }
}
```

## 模块依赖

本插件的模块依赖 Sequencer 核心与 Level Sequence 系统。在你的项目 `.Build.cs` 文件中，需要添加对 `LevelSequence` 的依赖。

| 模块 | 用途 |
|---|---|
| `LevelSequence` | 核心依赖，提供 Level Sequence 的基础框架和运行时 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移为更安全的 `UE_LOGF`。 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复因只在编辑器存在的属性导致的网络同步布局不匹配问题。 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | 在 Sequencer 对象绑定菜单中添加“烘焙变换”选项。 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除 UObject 中的 7 个虚函数（已废弃或仅工具使用）。 |

### 维护评价

Template Sequence 插件创建于 2019 年，已有约 7 年历史。尽管它标记为 **实验性 (IsBetaVersion=true)** 且**默认未启用**，但从近期的 Git 历史来看，它仍然在**活跃维护**中。近期更新包含了编译修复、日志改进、网络同步修复以及 Sequencer 功能集成（如烘焙变换），表明 Epic 仍在使用和改进它。

**主要限制与注意事项**：
1.  **实验性状态**：作为实验性功能，其 API 和功能在未来版本中可能发生 breaking changes。
2.  **默认禁用**：需要手动在插件管理器中启用，或在 `.uproject` 文件中添加依赖。

**推荐度**：对于有复杂动画复用需求且能接受实验性功能的项目，**推荐尝试使用**。它能显著提升动画资产的管理效率。对于追求稳定性的项目，建议持续关注其状态，并在启用前进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- [测试用例 (Runtime)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence/Source/TemplateSequence/Private/Tests)
- [测试用例 (Editor)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence/Source/TemplateSequenceEditor/Private/Tests)