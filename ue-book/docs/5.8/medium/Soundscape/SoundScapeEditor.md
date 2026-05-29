# Soundscape Plugin

> A Dynamic Ambient Sound System（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动态环境音景系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，材质模板） |
| 模块 | `Soundscape` (Runtime), `SoundscapeEditor` (Editor) |
| 实验性 | ⚚ 是 |
| 创建时间 | 2022-05-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Soundscape) | |

## 用途

Soundscape 插件是一个数据驱动的动态环境音景系统。它解决的核心问题是：如何根据游戏世界中的不同状态（如位置、时间、天气、事件等）实时、平滑地混合环境声音，创造出一个动态且沉浸式的音景，而不是简单地播放循环的背景音轨。它允许开发者将环境声音抽象为可编辑的“调色板”（Palette）和“颜色”（Color），通过系统的混合逻辑来管理声音的过渡和叠加，实现更高级的音频设计。

## 使用场景

- 你正在制作一个开放世界游戏，需要根据玩家所处的地形（森林、沙漠、城市）和天气（雨天、晴天）动态切换环境声音层。
- 你希望在游戏中，随着时间（白天/夜晚）或游戏内事件（如战斗开始）自动调整环境音的氛围。
- 你需要一个可复用、可配置的音频系统，让音效设计师能够通过蓝图或数据资产来调整音景，而无需程序员频繁修改代码。

## 蓝图用法

由于 `Soundscape` 运行时模块未提供详细头文件，以下蓝图节点基于 `SoundscapeEditor` 模块提供的资产类型和编辑器集成推断。

### 核心资产

| 资产类型 | 说明 | 所在类 |
|---|---|---|
| `Soundscape Palette` | 用于定义一个环境音景状态的资产，包含多个声音层（Layers）及其混合参数。 | `USoundscapePalette` |
| `Soundscape Color` | 用于定义声音层（Layer）的资产，通常对应一个具体的声音或一组声音。 | `USoundscapeColor` |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中，右键选择“Audio -> Advanced -> SoundScape”创建 `Soundscape Palette` 和 `Soundscape Color` 资产。
2.  **配置调色板**：编辑 `Soundscape Palette` 资产，添加多个声音层（Layer）。每一层可以关联一个 `Soundscape Color` 资产，并设置其基础音量、音高、淡入淡出时间等混合参数。
3.  **在关卡中使用**：虽然运行时蓝图节点未在提供的代码中明确显示，但通常会在关卡中放置一个音效管理器（如 `SoundscapeSubsystem`）或特定组件，并将配置好的 `Palette` 资产指派给它，以驱动当前音景。

## C++ 用法

由于运行时模块 (`Soundscape`) 的具体 API 未在提供的代码中展示，以下用法基于系统架构和编辑器模块进行推断。

### 头文件引入

```cpp
#include "SoundscapeSubsystem.h" // 假设的子系统头文件
#include "SoundscapePalette.h"
#include "SoundscapeColor.h"
```

### 基本用法（推测）

```cpp
// 假设在某个管理类中获取Soundscape子系统
void AMyGameAudioManager::UpdateSoundscape()
{
    if (UGameInstance* GameInstance = GetGameInstance())
    {
        USoundscapeSubsystem* SoundscapeSubsystem = GameInstance->GetSubsystem<USoundscapeSubsystem>();
        if (SoundscapeSubsystem)
        {
            // 加载一个Palette资产
            USoundscapePalette* ForestPalette = LoadObject<USoundscapePalette>(nullptr, TEXT("/Game/Audio/Soundscape/ForestPalette.ForestPalette"));
            // 请求播放该Palette
            SoundscapeSubsystem->RequestPalette(ForestPalette);
        }
    }
}
```

### 进阶用法（推测）

```cpp
// 动态混合两个Palette
void AMyGameAudioManager::TransitionBetweenStates()
{
    USoundscapeSubsystem* SoundscapeSubsystem = GetGameInstance()->GetSubsystem<USoundscapeSubsystem>();
    USoundscapePalette* CurrentPalette = SoundscapeSubsystem->GetCurrentPalette();
    USoundscapePalette* NextPalette = ...; // 下一个状态的Palette

    // 使用子系统提供的混合功能，平滑过渡
    float BlendTime = 5.0f;
    SoundscapeSubsystem->BlendToPalette(NextPalette, BlendTime);
}
```

## Demo 示例

由于运行时模块的核心类未在提供的代码中展示，无法提供完整的可编译示例。以下是一个概念性的片段，展示如何通过子系统与Soundscape交互。

**MySoundscapeManager.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySoundscapeManager.generated.h"

class USoundscapePalette;

UCLASS()
class AMySoundscapeManager : public AActor
{
    GENERATED_BODY()

public:
    AMySoundscapeManager();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Soundscape")
    USoundscapePalette* InitialPalette;

private:
    void InitializeSoundscape();
};
```

**MySoundscapeManager.cpp**
```cpp
#include "MySoundscapeManager.h"
#include "SoundscapeSubsystem.h"

AMySoundscapeManager::AMySoundscapeManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMySoundscapeManager::BeginPlay()
{
    Super::BeginPlay();
    InitializeSoundscape();
}

void AMySoundscapeManager::InitializeSoundscape()
{
    if (UWorld* World = GetWorld())
    {
        UGameInstance* GameInstance = World->GetGameInstance();
        if (GameInstance)
        {
            if (USoundscapeSubsystem* SoundscapeSubsystem = GameInstance->GetSubsystem<USoundscapeSubsystem>())
            {
                if (InitialPalette)
                {
                    SoundscapeSubsystem->RequestPalette(InitialPalette);
                }
            }
        }
    }
}
```

## 模块依赖

从 `SoundscapeEditor.Build.cs` 文件推断，编辑器模块依赖于运行时模块。
运行时模块的具体依赖未提供，但根据功能推断，除了标准依赖外，可能还需要 `AudioMixer` 等音频相关模块。

| 模块 | 用途 |
|---|---|
| `Soundscape` | Soundscape运行时核心逻辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 更新内容浏览器，为音频资产添加新的菜单项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF（可能为新的日志格式）。 |
| 2025-10-01 | `714456fa` | [Soundscape] Fixes | 修复Soundscape系统中的错误。 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th | 更新了同时标记为实验性和Beta的插件描述文件。 |
| 2024-08-05 | `fd4a6bf8` | [Soundscape] Adding Asynchronous Loading to Soundscape Palettes | 为Soundscape调色板资产添加异步加载功能。 |

### 维护评价

- **创建时间**：约4年历史。
- **最近更新**：近期（2026年）仍有更新，内容涉及编辑器集成和代码现代化，表明仍在积极维护。
- **活跃程度**：活跃维护中。最近一年内有功能更新和修复。
- **已知问题**：由于插件仍标记为 **Beta** (`IsBetaVersion: true`)，其API和功能可能还不稳定，未来版本可能发生变更。
- **推荐使用**：推荐用于需要动态环境音景的项目，但需注意其Beta状态，做好应对未来变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Soundscape)
- 官方文档：未提供
- 测试用例：未在提供的信息中明确指定，可尝试在 `Engine/Plugins/Runtime/Soundscape/` 或 `Engine/Tests/` 目录下查找。