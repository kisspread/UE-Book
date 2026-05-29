# Soundscape Plugin

> A Dynamic Ambient Sound System（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 环境音景系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Soundscape` (Runtime), `SoundscapeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-27 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Soundscape) | |

## 用途

Soundscape 插件提供了一套数据驱动的动态环境音系统。其核心目的是让设计师能够通过蓝图和资产（Soundscape Palette）配置复杂的环境音层（如风声、鸟鸣、城市噪音），并通过“状态”（如时间、天气、区域）来动态混合这些音层，从而营造出沉浸、动态且响应游戏世界的音频环境。它解决了传统手动放置音源和触发器难以维护复杂动态音景的问题。

## 使用场景

- **开放世界游戏**：根据昼夜、天气（晴天、雨天）、玩家位置（森林、城市、室内）无缝切换和混合环境音层，提升世界沉浸感。
- **线性关卡/叙事游戏**：根据剧情进展、玩家行为或脚本事件（如进入战斗、发现秘密）触发特定的环境音氛围，强化叙事体验。
- **VR/虚拟现实应用**：提供高度沉浸式、空间感知的音景，其动态混合能力有助于维持场景的真实感和减少听觉疲劳。

## 蓝图用法

插件主要通过 `USoundscapeSubsystem` 进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Soundscape State` | 设置影响音景混合的全局或区域状态（如“时间=夜晚”、“天气=下雨”） | `USoundscapeSubsystem` |
| `Set Soundscape Palette` | 为指定区域或全局应用一套音景调色板（定义音层及其权重曲线） | `USoundscapeSubsystem` |
| `Clear Soundscape Palette` | 移除指定的音景调色板 | `USoundscapeSubsystem` |

### 使用示例（蓝图描述）

在关卡蓝图或角色蓝图中：
1. 获取 `Soundscape Subsystem`。
2. 使用 `Set Soundscape State` 节点，设置一个 `GameplayTag` 表示当前的“时间”状态（如 `State.Time.Night`）。
3. 使用 `Set Soundscape Palette` 节点，将预先创建好的 `SoundscapePalette` 资产应用到场景中。该资产内定义了“夜晚”状态下各音层的权重。
4. 随着游戏状态变化（如下雨了），再次调用 `Set Soundscape State` 添加 “天气=雨天” 标签，系统将自动根据新的状态组合更新音效混合。

## C++ 用法

### 头文件引入

```cpp
#include "SoundscapeSubsystem.h"
```

### 基本用法

```cpp
// 获取子系统
USoundscapeSubsystem* SoundscapeSubsystem = GetWorld()->GetSubsystem<USoundscapeSubsystem>();

// 定义并设置状态
FGameplayTagContainer NewStateTags;
NewStateTags.AddTag(FGameplayTag::RequestGameplayTag(FName("State.Time.Day")));
NewStateTags.AddTag(FGameplayTag::RequestGameplayTag(FName("State.Weather.Clear")));
SoundscapeSubsystem->SetSoundscapeState(NewStateTags);

// 应用音景调色板资产
USoundscapePalette* DaytimePalette = LoadObject<USoundscapePalette>(nullptr, TEXT("/Game/Audio/Soundscapes/SKP_Daytime"));
SoundscapeSubsystem->SetSoundscapePalette(DaytimePalette);
```

### 进阶用法

可以通过 `OnSoundscapePaletteChanged` 和 `OnSoundscapeStateChanged` 委托监听音景状态和调色板的变化，用于UI更新或游戏逻辑响应。

## Demo 示例

以下是一个最小化的组件设置示例，用于在蓝图之外的C++类中驱动音景。

**MyAudioComponent.h**
```cpp
#pragma once

#include "Components/ActorComponent.h"
#include "MyAudioComponent.generated.h"

class USoundscapeSubsystem;

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMyAudioComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    UPROPERTY(EditAnywhere, Category = "Soundscape")
    FGameplayTag DayNightStateTag;

    UPROPERTY(EditAnywhere, Category = "Soundscape")
    USoundscapePalette* SoundscapePaletteAsset;

private:
    UPROPERTY()
    USoundscapeSubsystem* SoundscapeSubsystem;
};
```

**MyAudioComponent.cpp**
```cpp
#include "MyAudioComponent.h"
#include "SoundscapeSubsystem.h"
#include "GameplayTagContainer.h"

void UMyAudioComponent::BeginPlay()
{
    Super::BeginPlay();
    SoundscapeSubsystem = GetWorld()->GetSubsystem<USoundscapeSubsystem>();
    if (SoundscapeSubsystem && SoundscapePaletteAsset)
    {
        // 初始设置调色板
        SoundscapeSubsystem->SetSoundscapePalette(SoundscapePaletteAsset);
    }
}

void UMyAudioComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    
    // 模拟状态变化（实际项目中由游戏逻辑驱动）
    if (SoundscapeSubsystem)
    {
        FGameplayTagContainer CurrentState;
        // 根据游戏时间或其他逻辑设置标签...
        if (bIsNightTime) CurrentState.AddTag(DayNightStateTag);
        SoundscapeSubsystem->SetSoundscapeState(CurrentState);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 底层音频混合引擎 |
| `SignalProcessing` | 音频信号处理功能 |
| `GameplayTags` | 用于定义和管理音景状态标签 |
| `Engine` | 基础引擎功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“添加”菜单中新增了音频相关选项，方便创建资产。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出从旧宏迁移到新的UE_LOGF格式，属于代码维护和现代化改进。 |
| 2025-10-01 | `714456fa` | [Soundscape] Fixes | 对Soundscape插件进行了错误修复，提升了稳定性。 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta... | 清理了同时标记为实验版和测试版的插件描述文件，Soundscape的测试版状态得以明确。 |
| 2024-08-05 | `fd4a6bf8` | [Soundscape] Adding Asynchronous Loading to Soundscape Palettes | 为音景调色板资产添加了异步加载功能，有助于减少加载时的卡顿。 |

### 维护评价

Soundscape 插件创建于 2022 年，虽然仍处于测试版（Beta），但持续有功能添加、问题修复和代码现代化更新。最近的更新（2026年4月）表明它仍在被 Epic Games 积极维护和改进。作为音频领域的专业化工具，它为处理复杂动态音景提供了强大的框架。推荐在需要数据驱动、动态混合环境音的项目中使用，但需注意其“测试版”状态，意味着API可能在未来发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Soundscape)
- [Soundscape 运行时模块文档](SoundScape.md)
- [Soundscape 编辑器模块文档](SoundScapeEditor.md)