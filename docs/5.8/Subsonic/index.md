# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、蓝图） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个实验性的高级音频创作与播放系统。它旨在提供一个比传统 Sound Cue 和 MetaSound 更直观、更强大的音频工作流，用于创建复杂的交互式音频体验。该插件的核心目标是解决音频设计师在 UE 中面临的工作流复杂、实时迭代困难以及性能优化门槛高等问题。它通过提供一套集成的编辑器工具、高性能的运行时引擎和清晰的 API，让音频创作更接近视觉化编程和实时反馈。

## 使用场景

- **音乐游戏 (Rhythm Game)**：你需要根据玩家输入和游戏状态，实时、精确地触发和混合大量音效与音乐片段。
- **开放世界游戏**：你需要一个强大且易于管理的环境音效系统，能够根据地理位置、天气和时间动态变化。
- **影视与虚拟制片**：你需要精确控制音频的同步、空间化和动态混音，以匹配复杂的镜头和叙事。
- **交互式艺术装置**：你需要创建由用户行为或传感器数据驱动的复杂音频景观。

## 蓝图用法

*（注：以下为基于模块功能推断的核心节点，具体函数名需查阅各模块文档。）*

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Subsonic Asset` | 创建一个新的 Subsonic 音频资产 | `USubsonicFactory` |
| `Play Subsonic Sound` | 在指定位置或组件上播放一个 Subsonic 音频资产 | `USubsonicComponent` |
| `Set Audio Parameter` | 运行时修改音频参数（如音高、滤波器截止频率） | `USubsonicComponent` |
| `Stop All Sounds` | 停止所有由该组件播放的 Subsonic 音频 | `USubsonicComponent` |

### 使用示例（蓝图描述）

1.  在你的 Actor 蓝图中，添加一个 `SubsonicComponent`。
2.  在事件图表中，使用 `Create Subsonic Asset` 节点创建或引用一个已有的音频资产。
3.  将资产连接到 `SubsonicComponent` 的 `Play Subsonic Sound` 节点，并设置播放位置（如 Actor 位置）。
4.  使用 `Set Audio Parameter` 节点，根据游戏逻辑（如玩家速度）动态调整音频参数。

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicCore.h"
#include "SubsonicEngine.h"
```

### 基本用法

```cpp
// 假设在某个 Actor 或 Component 中
#include "SubsonicComponent.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 获取或创建 Subsonic 组件
    USubsonicComponent* AudioComp = FindComponentByClass<USubsonicComponent>();
    if (!AudioComp)
    {
        AudioComp = NewObject<USubsonicComponent>(this);
        AudioComp->RegisterComponent();
    }
    
    // 加载一个 Subsonic 资产
    USubsonicAsset* MySound = LoadObject<USubsonicAsset>(nullptr, TEXT("/Game/Audio/MySubsonicSound"));
    
    // 播放
    if (MySound)
    {
        AudioComp->Play(MySound);
    }
}
```

### 进阶用法

```cpp
// 动态控制音频参数
void AMyActor::UpdateAudioBasedOnSpeed(float Speed)
{
    USubsonicComponent* AudioComp = FindComponentByClass<USubsonicComponent>();
    if (AudioComp && AudioComp->IsPlaying())
    {
        // 将速度映射到音高参数
        float Pitch = FMath::GetMappedRangeValueClamped(
            FVector2D(0.f, 1000.f), // 速度范围
            FVector2D(0.8f, 1.5f),  // 音高范围
            Speed
        );
        AudioComp->SetParameter(FName("Pitch"), Pitch);
    }
}
```

## Demo 示例

**MySubsonicActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MySubsonicActor.generated.h"

class USubsonicComponent;
class USubsonicAsset;

UCLASS()
class AMySubsonicActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMySubsonicActor();
    
    virtual void BeginPlay() override;
    
    UFUNCTION(BlueprintCallable)
    void TriggerSound();
    
private:
    UPROPERTY(VisibleAnywhere)
    USubsonicComponent* SubsonicComponent;
    
    UPROPERTY(EditAnywhere, Category = "Audio")
    USubsonicAsset* SoundToPlay;
};
```

**MySubsonicActor.cpp**
```cpp
#include "MySubsonicActor.h"
#include "SubsonicComponent.h"
#include "SubsonicAsset.h"

AMySubsonicActor::AMySubsonicActor()
{
    PrimaryActorTick.bCanEverTick = false;
    SubsonicComponent = CreateDefaultSubobject<USubsonicComponent>(TEXT("SubsonicAudio"));
    RootComponent = SubsonicComponent;
}

void AMySubsonicActor::BeginPlay()
{
    Super::BeginPlay();
    // 可以在此预加载或做其他初始化
}

void AMySubsonicActor::TriggerSound()
{
    if (SoundToPlay && SubsonicComponent)
    {
        SubsonicComponent->Play(SoundToPlay);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | 核心数据类型、资产和基础接口 |
| `SubsonicEditor` | 编辑器自定义资产编辑器、节点和工具 |
| `SubsonicEngine` | 运行时音频播放、混音和空间化引擎 |
| `SubsonicEngineTest` | 引擎功能的自动化测试 |

## 维护状态

### 近期更新

*（注：由于插件为实验性且创建日期较新，暂无公开的 git 历史记录可供分析。以下为基于实验性状态的推断。）*

- 2026-04-02 `Initial commit` 插件首次引入实验性版本。

### 维护评价

- **状态**：**实验性 (Experimental)**
- **分析**：该插件明确标记为实验性 (`IsExperimentalVersion: true`)，且未默认启用。这意味着 Epic Games 正在积极开发和测试此功能，但 API 和功能集在未来版本中可能发生重大变更，且不保证向后兼容。
- **建议**：可以用于原型开发和内部测试，以探索其工作流优势。**不建议**在需要长期稳定维护的正式项目中作为核心依赖使用。请密切关注后续版本的更新日志和迁移指南。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]() (暂无)
- [测试用例]() (位于 `SubsonicEngineTest` 模块内)