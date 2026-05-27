# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模块与测试资源） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个实验性的高级音频创作和播放系统。它旨在为开发者提供一个比标准音频引擎更强大、更灵活的框架，用于构建复杂的音频体验，例如动态音乐系统、交互式环境音效或需要精细混音控制的应用。由于其处于实验阶段，API 和功能可能会发生变化。

## 使用场景

*   你正在开发一个开放世界游戏，需要根据玩家位置、天气和游戏事件动态混合和切换多个音乐层 → 使用 Subsonic 管理复杂的音频场景。
*   你正在制作一个音乐节奏游戏，需要精确到毫秒的音频播放控制和实时音频处理 → 利用 Subsonic 提供的创作工具和播放引擎。
*   你需要创建一个包含大量交互式音频元素（如脚步声、环境声、语音）并能实时调整其参数的体验 → 使用 Subsonic 作为统一的音频管理后台。

## 蓝图用法

> *注：由于 Subsonic 是实验性插件，具体的蓝图节点可能随版本更新。以下为基于模块功能的预期核心节点。*

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Sound Wave` | 创建一个可由 Subsonic 系统管理的音频源资产 | `USubsonicSoundWaveFactory` (推断) |
| `Play Audio Scene` | 根据场景资产播放和控制一组音频源 | `USubsonicAudioScenePlayer` (推断) |
| `Set Audio Parameter` | 实时修改正在播放的音频源的参数（如音量、音高、滤波器） | `USubsonicAudioParameterControl` (推断) |

### 使用示例（蓝图描述）

1.  **初始化**：在游戏开始时，使用 “Create Sound Wave” 节点为背景音乐和环境音效创建音频资产。
2.  **播放**：通过 “Play Audio Scene” 节点，将这些音频资产组织到一个“场景”中并开始播放。该节点会返回一个句柄用于后续控制。
3.  **动态控制**：在游戏过程中（如角色进入室内），使用 “Set Audio Parameter” 节点，通过句柄降低外部环境音效的音量，并调整其滤波器参数以模拟室内声音效果。

## C++ 用法

### 头文件引入

```cpp
// 核心音频系统
#include "SubsonicCoreModule.h"
// 引擎集成
#include "SubsonicEngineModule.h"
```

### 基本用法

*代码示例为基于模块结构的推断，具体API需查阅源码。*

```cpp
#include "SubsonicCore/AudioSceneAsset.h"
#include "SubsonicEngine/SubsonicAudioSubsystem.h"

void AMyActor::StartCustomAudioScene()
{
    // 1. 从资产中加载音频场景
    UAudioSceneAsset* SceneAsset = LoadObject<UAudioSceneAsset>(nullptr, TEXT("/Game/Audio/BattleScene"));
    if (SceneAsset)
    {
        // 2. 通过引擎子系统播放该场景
        USubsonicAudioSubsystem* AudioSubsystem = GetWorld()->GetSubsystem<USubsonicAudioSubsystem>();
        if (AudioSubsystem)
        {
            FAudioScenePlaybackHandle Handle = AudioSubsystem->PlayScene(SceneAsset, this->GetActorLocation());
            // 3. 保存句柄以便后续控制
            CurrentSceneHandle = Handle;
        }
    }
}

void AMyActor::MuffleAudio()
{
    // 4. 实时修改音频参数（示例：对主音频源施加低通滤波）
    USubsonicAudioSubsystem* AudioSubsystem = GetWorld()->GetSubsystem<USubsonicAudioSubsystem>();
    if (AudioSubsystem && CurrentSceneHandle.IsValid())
    {
        AudioSubsystem->SetSceneParameter(CurrentSceneHandle, TEXT("LPF_Cutoff"), 500.0f);
    }
}
```

### 进阶用法

结合多个子系统和资产，实现动态音乐层控制。

```cpp
// 可能涉及 SubsonicCore 中定义的更细粒度的音频图谱(Audio Graph)控制
#include "SubsonicCore/AudioGraphController.h"
#include "SubsonicEngine/DynamicMusicLayerManager.h"

void AMyGameMode::TransitionToCombatMusic()
{
    // 假设有一个管理动态音乐层的子系统
    if (UDynamicMusicLayerManager* MusicMgr = GetWorld()->GetSubsystem<UDynamicMusicLayerManager>())
    {
        // 淡出当前平和层，并淡入战斗层
        MusicMgr->CrossfadeToLayer(FName("Combat_Intense"), 2.0f);
    }
}
```

## Demo 示例

以下是一个创建并播放一个简单 Subsonic 音频场景的最小 C++ 示例。

### MyActor.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SubsonicCoreTypes.h" // 包含句柄等基础类型
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
    
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Audio")
    UAudioSceneAsset* TestSceneAsset; // 需要在编辑器中指定一个场景资产

    UFUNCTION(BlueprintCallable, Category="Audio")
    void PlaySubsonicScene();

    UFUNCTION(BlueprintCallable, Category="Audio")
    void StopSubsonicScene();

private:
    FAudioScenePlaybackHandle ActiveSceneHandle;
};
```

### MyActor.cpp

```cpp
#include "MyActor.h"
#include "SubsonicEngine/SubsonicAudioSubsystem.h"

void AMyActor::PlaySubsonicScene()
{
    if (!TestSceneAsset) return;

    USubsonicAudioSubsystem* AudioSub = GetWorld()->GetSubsystem<USubsonicAudioSubsystem>();
    if (AudioSub)
    {
        // 播放并存储句柄
        ActiveSceneHandle = AudioSub->PlayScene(TestSceneAsset, GetActorLocation());
        UE_LOG(LogTemp, Log, TEXT("Subsonic scene started with handle: %s"), *ActiveSceneHandle.ToString());
    }
}

void AMyActor::StopSubsonicScene()
{
    USubsonicAudioSubsystem* AudioSub = GetWorld()->GetSubsystem<USubsonicAudioSubsystem>();
    if (AudioSub && ActiveSceneHandle.IsValid())
    {
        AudioSub->StopScene(ActiveSceneHandle);
        ActiveSceneHandle.Invalidate();
        UE_LOG(LogTemp, Log, TEXT("Subsonic scene stopped."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | Subsonic 作为独立音频系统，其运行时模块主要依赖 UE 核心框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复一个糟糕的合并，恢复被意外覆盖的订阅者部分，并应用最小化的非废弃性修改。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃修复相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静默处理静态代码分析(PVS)产生的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“添加”菜单中新增了音频相关选项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |

### 维护评价

Subsonic 是一个创建于 2026 年初的**实验性**插件，当前仍处于**积极开发**阶段。从近期的 Git 提交历史来看，团队在持续进行代码维护（修复编译警告、解决合并冲突）和功能集成（编辑器内容浏览器集成），表明项目正在推进中。然而，由于其 `.uplugin` 明确标记为 `IsExperimentalVersion: true`，意味着 API 和架构可能发生重大变化，**不建议在需要稳定性的正式项目中全面依赖**。它适合用于技术预研、原型开发或对音频系统有前沿探索需求的项目。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
*   [官方文档](https://docs.unrealengine.com/) (暂无特定文档页)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)