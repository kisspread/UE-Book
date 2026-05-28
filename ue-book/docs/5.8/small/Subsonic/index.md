# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 旨在为 Unreal Engine 提供一套全新的、更高层次的音频创作与回放框架。它试图替代或补充传统的 `SoundCue` 系统，提供一个更加模块化、数据驱动且可能更适合复杂音频编排的现代工作流。其核心目标包括简化音频设计师的工作、支持更复杂的音频交互逻辑，并为引擎的底层音频系统提供统一的抽象层。

## 使用场景

- 你需要构建一个需要复杂、动态音频交互的游戏（例如基于玩家行为和环境状态变化的音景系统）。
- 你的音频管线希望采用数据驱动的方式，通过资产配置而非蓝图连接来组织音频逻辑。
- 你在寻找一个可能在未来取代 `SoundCue` 的下一代音频创作工具。
- 你需要一个底层可扩展、高层易使用的音频系统，以适应大型项目的协作需求。

## 蓝图用法

> **注意**：本插件处于实验阶段，API 可能会发生重大变更。

### 核心节点

以下节点主要位于 `SubsonicEngine` 模块中，用于在蓝图中控制 Subsonic 音频的播放。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Playback Context` | 创建一个用于控制 Subsonic 音频资产播放的上下文对象。 | `USubsonicSubsystem` |
| `Start Playback` | 使用指定的播放上下文开始播放一个 Subsonic 资产（如 `USoundSubmix`）。 | `USubsonicSubsystem` |
| `Stop Playback` | 平滑停止由播放上下文控制的音频播放。 | `USubsonicSubsystem` |
| `Set Parameter` | 在播放过程中动态设置参数（如音量、音高、自定义标记），以影响音频行为。 | `USubsonicSubsystem` |

### 使用示例（蓝图描述）

1.  在 BeginPlay 事件中，调用 `Create Playback Context` 节点，将返回的上下文对象存储到变量 `PlaybackCtx` 中。
2.  准备一个要播放的 `USoundSubmix` 资产（在内容浏览器中创建）。
3.  调用 `Start Playback` 节点，将 `PlaybackCtx` 和 `SoundSubmix` 资产连接起来，音频开始播放。
4.  在游戏逻辑中，根据需要调用 `Set Parameter` 节点，输入 `PlaybackCtx`、参数名（如 `”Volume”`）和值，实时调控音量。
5.  在需要停止时，调用 `Stop Playback` 节点并传入 `PlaybackCtx`。

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicSubsystem.h"
```

### 基本用法

```cpp
// 在 Actor 的 BeginPlay 中，开始播放一个 Subsonic 音频资产。
// 来源：SubsonicEngineTest 模块测试用例
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    USubsonicSubsystem* SubsonicSubsystem = GetWorld()->GetSubsystem<USubsonicSubsystem>();
    if (SubsonicSubsystem)
    {
        // 创建一个播放上下文
        PlaybackContext = SubsonicSubsystem->CreatePlaybackContext(this);

        // 开始播放一个 SoundSubmix 资产 (假设已加载)
        SubsonicSubsystem->StartPlayback(PlaybackContext, MySoundSubmixAsset);
    }
}
```

### 进阶用法

```cpp
// 在游戏逻辑中，动态修改正在播放的音频参数
void AMyActor::UpdateAudioBasedOnSpeed(float CurrentSpeed)
{
    USubsonicSubsystem* SubsonicSubsystem = GetWorld()->GetSubsystem<USubsonicSubsystem>();
    if (SubsonicSubsystem && PlaybackContext)
    {
        // 假设 Subsonic 资产中定义了一个名为 "PitchMultiplier" 的参数
        // 根据速度计算音高乘数
        float PitchMultiplier = FMath::Lerp(0.8f, 1.2f, CurrentSpeed / MaxSpeed);
        SubsonicSubsystem->SetParameter(PlaybackContext, TEXT("PitchMultiplier"), PitchMultiplier);
    }
}
```

## Demo 示例

**Actor 头文件 (MySubsonicActor.h):**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MySubsonicActor.generated.h"

class USoundSubmix;
class USubsonicPlaybackContext;

UCLASS()
class AMySubsonicActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere)
    USoundSubmix* BackgroundMusicAsset;

private:
    UPROPERTY()
    USubsonicPlaybackContext* BackgroundMusicContext;
};
```

**Actor 源文件 (MySubsonicActor.cpp):**
```cpp
#include "MySubsonicActor.h"
#include "SubsonicSubsystem.h"

void AMySubsonicActor::BeginPlay()
{
    Super::BeginPlay();

    if (USubsonicSubsystem* SubsonicSystem = GetWorld()->GetSubsystem<USubsonicSubsystem>())
    {
        // 创建并启动背景音乐播放
        BackgroundMusicContext = SubsonicSystem->CreatePlaybackContext(this);
        if (BackgroundMusicAsset)
        {
            SubsonicSystem->StartPlayback(BackgroundMusicContext, BackgroundMusicAsset);
        }
    }
}

void AMySubsonicActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 确保在 Actor 销毁时停止播放并释放上下文
    if (BackgroundMusicContext)
    {
        if (USubsonicSubsystem* SubsonicSystem = GetWorld()->GetSubsystem<USubsonicSubsystem>())
        {
            SubsonicSystem->StopPlayback(BackgroundMusicContext);
        }
        BackgroundMusicContext->MarkAsGarbage();
        BackgroundMusicContext = nullptr;
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

要使用 Subsonic 插件的功能，你的模块需要依赖以下模块（基于子模块的 Build.cs 分析）：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 的基础库和类型定义，是其他子模块的公共依赖。 |
| `SubsonicEngine` | 运行时音频引擎集成，包含核心播放子系统和蓝图/C++ API。你的游戏模块主要依赖此模块。 |
| `SignalProcessing` | 用于底层音频信号处理和分析。 |
| `AudioMixer` | 底层音频混音器接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复错误的合并，回滚了对 Subsonic 订阅者的重大修改，并应用了最小的非废弃修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃修复的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静默了来自 PVS（代码分析工具）的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“添加”菜单中新增了音频相关菜单项（可能与 Subsonic 资产创建相关）。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志调用迁移为 UE_LOGF 格式。 |

### 维护评价

Subsonic 是一个**非常新的实验性插件**，于 2026 年初创建。从提交历史看，最近在 **2026 年 4 月和 5 月仍有活跃的开发和维护**，包括合并冲突修复、代码清理和编辑器集成工作。

**优点**：
- 仍在活跃开发中，表明 Epic 内部可能在使用和推进此系统。
- 提供了全新的、模块化的音频架构。

**风险与注意事项**：
- **实验性质明确**：.uplugin 声明为实验性，并警告不保证向后兼容。这意味着你的工程在升级引擎版本时，依赖此插件的代码和资产可能需要重新编写或迁移。
- **文档缺失**：官方文档链接为空，学习成本可能较高，主要依赖源码和测试。
- **API 不稳定**：作为实验性功能，其蓝图和 C++ API 可能会在未来版本中发生 breaking changes。

**结论**：**可以用于原型开发和技术预研**，特别是如果你对下一代音频工作流感兴趣。但对于计划长期维护的商业项目，需谨慎评估其带来的维护风险。建议密切关注其后续版本的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [SubsonicCore 模块文档](SubsonicCore.md)
- [SubsonicEditor 模块文档](SubsonicEditor.md)
- [SubsonicEngine 模块文档](SubsonicEngine.md)
- [SubsonicEngineTest 模块文档](SubsonicEngineTest.md)
- 官方文档：暂无
- 测试用例：位于 `SubsonicEngineTest` 模块源码中