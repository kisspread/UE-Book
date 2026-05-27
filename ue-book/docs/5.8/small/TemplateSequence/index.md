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

TemplateSequence 插件解决了在 Unreal Engine 的 Sequencer 中复用动画序列资产的核心问题。它允许你创建一个“模板序列”资产，并将其作为一个整体，实例化到场景中的不同角色（Actor）上。每个实例共享模板序列的动画数据（如关键帧），但可以拥有独立的属性覆盖（如播放速度、混合权重）。这使得在不复制序列数据的前提下，让多个角色播放相同动画序列并保持同步成为可能，尤其适用于群体动画或需要快速复用复杂动画剪辑的场景。

## 使用场景

- 你需要让场景中的大量角色（如NPC或人群）同步播放一段相同的动画序列。
- 你希望在 Sequencer 编辑器中快速为多个角色实例应用同一套复杂的动画剪辑，并允许微调每个实例的某些参数。
- 你在制作过场动画，需要多个角色执行相同的动作，但希望保持动画数据的单一来源以便于维护和更新。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Template Sequence` | 通过模板序列资产创建一个序列实例，可绑定到特定对象。 | `UTemplateSequenceSubsystem` |
| `Get Sequence Instance` | 获取已有的模板序列实例。 | `UTemplateSequenceSubsystem` |
| `Set Template` | 为序列实例设置要使用的模板序列资产。 | `UTemplateSequencePlayer` |
| `Get Template` | 获取序列实例当前使用的模板序列资产。 | `UTemplateSequencePlayer` |

### 使用示例（蓝图描述）

1.  首先，你需要在内容浏览器中创建一个“Template Sequence”资产。
2.  在 Sequencer 轨道中，为需要播放此模板动画的角色添加一个“Template Sequence Track”。
3.  从资产库中将你的模板序列资产拖拽到该轨道上，即可为该角色创建一个实例。
4.  在蓝图中，你可以通过 `Create Template Sequence` 节点动态地创建实例并将其绑定到角色。通过 `Set Template` 节点可以运行时更换模板资产。

## C++ 用法

### 头文件引入

```cpp
// 核心运行时模块
#include "TemplateSequence.h"
#include "TemplateSequencePlayer.h"
#include "TemplateSequenceSubsystem.h"
// 编辑器模块 (仅在编辑器代码中使用)
#include "TemplateSequenceEditor.h"
```

### 基本用法

以下代码演示如何在运行时创建一个模板序列播放器并播放。
*(来源：基于 `TemplateSequencePlayer` 和 `TemplateSequenceSubsystem` 的公开 API 设计)*

```cpp
// 假设你有一个模板序列资产 UTemplateSequenceAsset* MyTemplateAsset 和一个要绑定的目标 AActor* TargetActor
// 1. 获取子系统
UTemplateSequenceSubsystem* Subsystem = UWorld::GetSubsystem<UTemplateSequenceSubsystem>(GetWorld());
// 2. 创建一个播放器实例，并绑定到目标Actor
UTemplateSequencePlayer* Player = Subsystem->CreateSequencePlayer(MyTemplateAsset, TargetActor);
// 3. 设置播放参数并开始播放
Player->SetPlayRate(1.0f);
Player->Play();
```

### 进阶用法

你可以遍历并管理所有已创建的序列实例，或使用其事件进行精细控制。
*(来源：`UTemplateSequenceSubsystem` 管理多实例的设计)*

```cpp
// 获取子系统并遍历所有活动的序列实例
UTemplateSequenceSubsystem* Subsystem = World->GetSubsystem<UTemplateSequenceSubsystem>();
TArray<UTemplateSequencePlayer*> AllPlayers = Subsystem->GetAllPlayers();
for (UTemplateSequencePlayer* Player : AllPlayers)
{
    // 对每个实例进行操作，例如暂停、跳转或修改模板
    Player->Pause();
    Player->SetTemplate(NewTemplateAsset);
}
```

## Demo 示例

```cpp
// MyTemplateSequenceActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyTemplateSequenceActor.generated.h"

class UTemplateSequencePlayer;
class UTemplateSequenceAsset;

UCLASS()
class AMyTemplateSequenceActor : public AActor
{
    GENERATED_BODY()
public:
    AMyTemplateSequenceActor();

protected:
    virtual void BeginPlay() override;

public:
    // 在编辑器中指定的模板序列资产
    UPROPERTY(EditAnywhere, Category = "Template")
    UTemplateSequenceAsset* TemplateAsset;

private:
    UPROPERTY()
    UTemplateSequencePlayer* SequencePlayer;
};

// MyTemplateSequenceActor.cpp
#include "MyTemplateSequenceActor.h"
#include "TemplateSequence.h"
#include "TemplateSequencePlayer.h"
#include "TemplateSequenceSubsystem.h"

AMyTemplateSequenceActor::AMyTemplateSequenceActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTemplateSequenceActor::BeginPlay()
{
    Super::BeginPlay();
    if (TemplateAsset)
    {
        // 从世界获取子系统，并创建序列播放器绑定到自身
        if (UTemplateSequenceSubsystem* Subsystem = GetWorld()->GetSubsystem<UTemplateSequenceSubsystem>())
        {
            SequencePlayer = Subsystem->CreateSequencePlayer(TemplateAsset, this);
            if (SequencePlayer)
            {
                SequencePlayer->Play();
            }
        }
    }
}
```

## 模块依赖

要使用 `TemplateSequence` 插件，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 的核心序列与轨道系统 |
| `MovieSceneTracks` | Sequencer 的各种内置轨道实现 |
| `AnimationCore` | 动画核心基础类型与工具 |
| `LevelSequenceEditor` | **编辑器模块** 提供在 Sequencer 编辑器中操作模板序列的功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统的 UE_LOG 宏迁移到新的 UE_LOGF 宏。 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复了由于编辑器专用数据属性导致关卡序列播放器中复制布局不匹配的问题。 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | 在 Sequencer 的对象绑定菜单中添加了“烘焙变换”选项。 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除了 UObject 中的 7 个虚函数（已废弃或仅供工具使用）。 |

### 维护评价

TemplateSequence 插件创建于 **2019 年**，距今约 7 年。从最近的 Git 提交记录看，维护**较为活跃**。近期更新主要集中在修复编译警告、代码现代化迁移（如日志宏）、修复运行时数据同步的 Bug 以及为 Sequencer 编辑器增加功能（如烘焙变换）。

然而，该插件在 `.uplugin` 中明确标记为 **`IsBetaVersion: true`** 且 **`EnabledByDefault: false`**，这表明它仍处于**实验性阶段**，其 API 和功能在未来版本中可能发生不兼容的更改。

**总结**：这是一个功能成熟但官方定义为实验性的插件。如果你的项目核心功能依赖于它，需要做好未来 API 变更的准备，并自行启用该插件。对于人群动画或动画序列复用等场景，它是一个强大且活跃维护的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence/Tests)