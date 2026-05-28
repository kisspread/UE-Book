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

模板序列插件为虚幻引擎的序列器（Sequencer）提供了一种**可复用动画模板**的机制。它允许你创建一个预先定义了动画轨道（如变换、摄像机属性等）的“模板”序列资产，然后将这个模板快速应用到不同的对象或演员上。

这个插件解决了在项目中频繁创建结构相似但绑定对象不同的动画序列时，重复性劳动和容易出错的问题。例如，你可以创建一个标准的摄像机推进动画模板，然后将其快速应用到场景中的多个不同摄像机上，每个摄像机都会继承模板中的动画数据，但可以独立调整和播放。

该插件包含运行时和编辑器两部分：运行时部分负责模板序列的实例化和播放逻辑；编辑器部分则提供了在序列器中创建、编辑和应用模板序列的完整工具集。

## 使用场景

- **摄像机动画系统**：创建可复用的摄像机动画模板（如推拉、平移、环绕），快速应用到游戏或过场动画中的不同摄像机上。
- **标准化动画**：为项目中的某种特定类型的对象（如开门动画、宝箱打开动画）创建标准动画模板，确保动画风格的一致性。
- **快速原型设计**：在关卡设计中，通过拖放模板序列资产快速为场景中的物体添加复杂的动画行为。
- **过场动画制作**：在需要大量相似镜头运动的过场动画中，使用模板序列来提高制作效率。

## 蓝图用法

模板序列插件在蓝图中主要通过 `UTemplateSequenceFunctionLibrary` 提供核心功能，用于运行时创建和播放模板序列。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Template Sequence` | 在指定世界中实例化一个模板序列并开始播放，返回播放器对象。 | `UTemplateSequenceFunctionLibrary` |
| `Create Camera Animation` | 创建一个摄像机动画序列实例，用于控制摄像机。 | `UTemplateSequenceFunctionLibrary` |
| `Stop Camera Animation` | 停止一个正在播放的摄像机动画序列。 | `UTemplateSequenceFunctionLibrary` |

### 使用示例（蓝图描述）

**示例1：在关卡中播放模板动画**
1. 使用 `Spawn Template Sequence` 节点。
2. 将 `Sequence` 引脚连接到你的模板序列资产引用。
3. 将 `Outer` 引脚连接到 `World` 或一个场景中的对象（如场景中的一个 `SceneComponent`）。
4. 节点会返回一个 `UTemplateSequencePlayer` 对象，你可以通过它来控制播放（播放、暂停、跳转等）。

**示例2：应用摄像机动画**
1. 使用 `Create Camera Animation` 节点。
2. 将 `Sequence` 引脚连接到一个摄像机动画模板序列资产。
3. 将 `Camera Actor` 引脚连接到场景中你想要控制的 `ACameraActor` 或包含摄像机组件的演员。
4. 节点会返回一个 `UCameraAnimationSequencePlayer`，用于精细控制动画的混合权重、播放速率等。

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequence.h"
#include "TemplateSequenceFunctionLibrary.h"
#include "Sections/MovieSceneTemplateSequenceSection.h"
```

### 基本用法

创建并播放一个模板序列实例。

```cpp
// 假设在某个 Actor 的 BeginPlay 中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 加载你的模板序列资产 (UTemplateSequence*)
    UTemplateSequence* TemplateSequenceAsset = LoadObject<UTemplateSequence>(nullptr, TEXT("/Game/Path/To/Your_TemplateSeq"));

    if (TemplateSequenceAsset && GetWorld())
    {
        // 2. 使用函数库生成播放器
        UTemplateSequencePlayer* Player = UTemplateSequenceFunctionLibrary::SpawnTemplateSequence(
            GetWorld(),
            TemplateSequenceAsset,
            this // Outer，通常是当前 Actor 或 World
        );

        // 3. 播放序列
        if (Player)
        {
            Player->Play();
        }
    }
}
```

### 进阶用法

使用 C++ 在编辑器或运行时动态创建模板序列资产。这通常用于工具链或自动化流程。

```cpp
// 引用来自 `Private/Factories/TemplateSequenceFactoryUtil.h` 的内部逻辑
#include "AssetToolsModule.h"
#include "IAssetTools.h"
#include "TemplateSequenceFactoryNew.h"

void CreateNewTemplateSequenceAsset()
{
    // 获取资产创建工具
    FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools");

    // 创建工厂实例
    UTemplateSequenceFactoryNew* Factory = NewObject<UTemplateSequenceFactoryNew>();
    Factory->BoundActorClass = AMyCustomActor::StaticClass(); // 设置模板要绑定的默认类型

    // 使用工厂创建资产
    UObject* NewAsset = AssetToolsModule.Get().CreateAsset(
        TEXT("NewTemplateSeq"),       // 资产名称
        TEXT("/Game/Sequences"),       // 路径
        UTemplateSequence::StaticClass(),
        Factory
    );

    if (UTemplateSequence* NewSequence = Cast<UTemplateSequence>(NewAsset))
    {
        // 资产创建成功，可以在这里进一步编辑轨道
        UE_LOG(LogTemp, Log, TEXT("Created new Template Sequence: %s"), *NewSequence->GetName());
    }
}
```

## Demo 示例

一个简单的 Actor，在开始游戏时播放一个指定的模板序列。

**MyTemplateSequencePlayerActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTemplateSequencePlayerActor.generated.h"

class UTemplateSequence;
class UTemplateSequencePlayer;

UCLASS()
class AMyTemplateSequencePlayerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTemplateSequencePlayerActor();

protected:
    virtual void BeginPlay() override;

    // 在编辑器中指定要播放的模板序列资产
    UPROPERTY(EditAnywhere, Category="Animation")
    TSoftObjectPtr<UTemplateSequence> TemplateSequenceAsset;

private:
    UPROPERTY()
    TObjectPtr<UTemplateSequencePlayer> SequencePlayer;
};
```

**MyTemplateSequencePlayerActor.cpp**
```cpp
#include "MyTemplateSequencePlayerActor.h"
#include "TemplateSequence.h"
#include "TemplateSequenceFunctionLibrary.h"

AMyTemplateSequencePlayerActor::AMyTemplateSequencePlayerActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTemplateSequencePlayerActor::BeginPlay()
{
    Super::BeginPlay();

    // 加载资产
    UTemplateSequence* Sequence = TemplateSequenceAsset.LoadSynchronous();

    if (Sequence && GetWorld())
    {
        // 创建并开始播放
        SequencePlayer = UTemplateSequenceFunctionLibrary::SpawnTemplateSequence(GetWorld(), Sequence, this);
        if (SequencePlayer)
        {
            SequencePlayer->Play();
            UE_LOG(LogTemp, Log, TEXT("Playing template sequence: %s"), *Sequence->GetName());
        }
    }
}
```

## 模块依赖

从插件模块的依赖关系推断，使用者需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `TemplateSequence` | 核心运行时，提供模板序列资产类型和播放逻辑。 |
| `MovieScene` | 虚幻序列器基础框架。 |
| `MovieSceneTracks` | 包含标准轨道类型（变换、属性等），模板序列可能依赖这些轨道。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量转为浮点数时产生警告的代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 UE_LOG 迁移为新的 UE_LOGF。 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复因仅编辑器数据属性导致关卡序列播放器复制布局不匹配的问题。 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | 序列器：为对象绑定菜单添加“烘焙变换”功能。 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除 UObject 中的 7 个虚函数（已弃用或仅供工具使用）。 |

### 维护评价

- **创建时间**：该插件创建于 2019 年 10 月，已有约 7 年历史。
- **近期活动**：最近的提交集中在 2026 年初，主要是**维护性更新**，如修复编译警告、迁移日志宏、修复边缘情况 bug 等，没有重大的新功能引入。
- **活跃度**：**维护中，但不活跃**。插件仍能与当前引擎版本（5.8）兼容，并接受必要的错误修复，但功能上已趋于稳定，长期没有实质性功能更新。
- **已知问题/限制**：`.uplugin` 中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明该插件仍被官方标记为**实验性**，可能在未来的引擎版本中有不兼容的更改或限制。
- **推荐使用**：适合需要**可复用动画模板**的项目，特别是摄像机动画。但由于其“实验性”状态，不建议在追求极高稳定性的核心生产管线中完全依赖它，使用时需注意版本升级可能带来的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- 官方文档 (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence/Tests) (如果存在)