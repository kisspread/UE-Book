# AudioGameplay

> Core plugin for audio gameplay

| 属性 | 值 |
|---|---|
| 中文名 | 音频游戏核心 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `AudioGameplay` (Runtime), `AudioGameplayTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-10-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplay) | |

## 用途

AudioGameplay 插件为游戏中的音频交互提供了一套运行时框架。它并非一个具体的音频播放器或效果，而是一个核心系统，用于管理和查询音频相关的游戏逻辑。其主要功能包括：
1.  **音频资产标签查询**：允许游戏逻辑（如蓝图）根据标签（Tags）查询和筛选音频资产，使音频管理与游戏内容（如角色、物品、环境）解耦。
2.  **环境音频管理**：提供用于管理环境音量、音频混合等高级游戏音频概念的运行时支持。
3.  **测试支持**：附带专用的测试模块，用于验证音频游戏逻辑的正确性。

该插件存在的目的是为需要在运行时动态控制或查询音频信息的游戏提供标准化的基础设施。

## 使用场景

-   你正在开发一个大型开放世界游戏，需要根据玩家所在区域（如森林、城镇、室内）动态切换和管理复杂的环境音效组合 → 使用 `AudioGameplay` 的环境音频管理功能。
-   你的游戏中有大量可交互的音频资产（不同材质的脚步声、不同武器的音效），你希望通过游戏逻辑（如材质标签、物品类型标签）灵活地选择对应音效 → 使用音频资产标签查询功能。
-   你正在开发一套音频中间件或自定义音频系统，需要一个稳定的核心运行时模块来处理音频与游戏状态的交互 → 可以依赖或集成 `AudioGameplay` 模块。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All Audio Assets With Tags` | 根据一组标签查询所有匹配的音频资产。 | `UAudioAssetUserData` |
| `Get Audio Asset With Tag` | 根据单个标签查询一个匹配的音频资产。 | `UAudioAssetUserData` |
| `Set Submix Volume` | 设置指定音频子混音（Submix）的音量。 | `UAudioGameplaySubsystem` |
| `Get Submix Volume` | 获取指定音频子混音的当前音量。 | `UAudioGameplaySubsystem` |

*（注：基于 `AudioGameplayTests` 模块中测试用例的功能推断）*

### 使用示例（蓝图描述）

1.  **查询特定标签的音效**：
    *   节点：`Get Audio Asset With Tag`
    *   输入：一个 `FName` 类型的标签，例如 `"Footstep.Concrete"`。
    *   输出：返回一个 `USoundBase*` 音频资产引用。你可以将其连接到 “Play Sound” 节点来播放。

2.  **控制环境音乐音量**：
    *   节点：`Set Submix Volume`
    *   输入：指定用于背景音乐的 `Sound Submix` 资产引用，以及一个 `0.0` 到 `1.0` 的浮点数音量值。
    *   应用：在游戏菜单中调整“音乐音量”滑块时，调用此节点来实时更改音量。

## C++ 用法

### 头文件引入

```cpp
#include "AudioGameplaySubsystem.h" // 用于访问子系统功能
#include "AudioAssetUserData.h"     // 用于音频资产标签查询
```

### 基本用法

以下代码展示了如何查询带有特定标签的音频资产。
（来源：`AudioGameplayTests` 模块测试用例推断）

```cpp
// 假设你有一个 USoundBase* AssetToQuery
if (UAudioAssetUserData* AudioAssetUserData = AssetToQuery->FindComponent<UAudioAssetUserData>())
{
    // 查询带有 “Character.Player.Voice” 标签的所有音效
    TArray<FName> TagsToFind = { FName("Character.Player.Voice") };
    TArray<USoundBase*> FoundSounds;
    AudioAssetUserData->GetAllAudioAssetsWithTags(TagsToFind, FoundSounds);
    
    if (FoundSounds.Num() > 0)
    {
        // 使用查询到的第一个音效
        USoundBase* SoundToPlay = FoundSounds[0];
        // ... 播放声音逻辑
    }
}
```

### 进阶用法

结合子系统管理环境音频。
（来源：`AudioGameplayTests` 模块测试用例推断）

```cpp
// 获取音频游戏子系统实例
if (UAudioGameplaySubsystem* AudioSubsystem = GetWorld()->GetSubsystem<UAudioGameplaySubsystem>())
{
    // 假设你有一个 USoundSubmix* MusicSubmix 引用
    // 将背景音乐子混音的音量淡入到 80%
    AudioSubsystem->SetSubmixVolume(MusicSubmix, 0.8f);
    
    // 在某个时刻（如进入室内），降低环境音子混音的音量
    if (USoundSubmix* AmbientSubmix = GetAmbientSoundSubmix())
    {
        AudioSubsystem->SetSubmixVolume(AmbientSubmix, 0.3f);
    }
}
```

## Demo 示例

以下是一个最小化的使用示例，演示如何从音频资产获取数据并在编辑器中测试。

**MyAudioHelper.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "MyAudioHelper.generated.h"

UCLASS()
class UMyAudioHelper : public UWorldSubsystem
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "AudioHelper")
    USoundBase* FindSoundByTag(USoundBase* InAsset, FName Tag);
};
```

**MyAudioHelper.cpp**
```cpp
#include "MyAudioHelper.h"
#include "AudioAssetUserData.h"

USoundBase* UMyAudioHelper::FindSoundByTag(USoundBase* InAsset, FName Tag)
{
    if (!InAsset) return nullptr;
    
    if (UAudioAssetUserData* UserData = InAsset->FindComponent<UAudioAssetUserData>())
    {
        TArray<USoundBase*> Results;
        UserData->GetAllAudioAssetsWithTags({Tag}, Results);
        return Results.IsValidIndex(0) ? Results[0] : nullptr;
    }
    return nullptr;
}
```

## 模块依赖

从模块名称和用途推断，使用此插件通常需要依赖以下核心音频模块（非标准通用模块）：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 底层音频混音器，此插件的子混音管理功能很可能依赖它。 |
| `SoundFields` | 用于支持高级音频场（如 Ambisonics）。 |
| `SignalProcessing` | 可能用于音频信号处理相关的底层功能。 |

*（注：精确依赖关系需查阅 `AudioGameplay.Build.cs`，但以上为音频插件常见关键依赖。）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF格式。 |
| 2025-09-09 | `723f87e6` | Added missing include. | 补充了一个缺失的头文件包含。 |
| 2025-08-20 | `1746b743` | AGV Updates / Glow up | 对AudioGameplay进行了功能更新和优化。 |
| 2025-07-29 | `a6ddb9ae` | AudioMixerCore put string definitions for Insights events into .cpp file | 将Insights事件的字符串定义移至源文件，优化编译。 |
| 2025-07-25 | `5d147547` | [Audio] Add BP utility functions to AudioAssetUserData for interacting with audio asset tags | 为AudioAssetUserData添加了蓝图工具函数，用于交互音频资产标签。 |

### 维护评价

**状态：实验性且活跃维护中**

该插件自2021年创建以来，近期内（2025-2026年）有持续的更新，包括功能增强、代码优化和缺陷修复，表明它处于**活跃维护**状态。然而，`.uplugin` 文件中 `IsBetaVersion: true` 明确指出这是一个**实验性**插件，意味着其API和功能未来可能发生重大变化，不建议在需要长期稳定性的核心项目中直接使用。

尽管是实验性模块，但其持续的更新记录显示它仍在Epic的开发视野内，是探索和实现高级音频游戏逻辑的**有价值参考和工具**。建议关注其后续版本，或在独立、可更新的项目模块中谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplay/Source/AudioGameplayTests)