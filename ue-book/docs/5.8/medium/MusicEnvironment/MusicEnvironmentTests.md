# Music Environment

> A Project-Wide source of musical information (musically synchronized clocks, events, etc.)

| 属性 | 值 |
|---|---|
| 中文名 | 音乐环境 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MusicEnvironment` (Runtime), `MusicEnvironmentEditor` (Runtime), `MusicEnvironmentTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MusicEnvironment) | |

## 用途

MusicEnvironment 插件的核心功能是为整个游戏项目提供一个统一、全局的“音乐环境”管理器。它并非一个简单的音频播放组件，而是一个**基础设施**，旨在解决音乐与游戏逻辑精确同步的复杂问题。其存在意义是为音乐游戏(Music Game)、节奏动作游戏或其他需要基于音乐节拍进行交互的项目，提供一个权威且可预测的音乐时序信息源。通过该插件，游戏逻辑（如障碍物生成、玩家输入判定、环境变化）可以精确地与音乐的节拍、小节或自定义事件对齐，避免了不同系统各自计算音乐时间可能带来的漂移和不一致。

## 使用场景

- **音乐节奏游戏**：你需要在游戏中生成与音乐节拍精准同步的“音符”或障碍物，并精确判定玩家输入是否在节拍窗口内。
- **动态音乐交互**：你需要根据音乐的不同段落（如主歌、副歌）或特定的音乐事件（如鼓点、旋律变化）来改变游戏玩法、镜头或环境效果。
- **音乐可视化**：你需要将场景中的灯光、粒子效果或动画与音乐的特定频率或节拍同步。
- **影视化游戏**：你需要确保游戏内的叙事事件与背景音乐的特定时间点完全吻合。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMusicEnvironment` | 获取当前世界/游戏的全局 Music Environment 实例 | `UMusicEnvironmentSubsystem` |
| `GetSyncedClock` | 从 Music Environment 获取一个与音乐同步的时钟对象 | `UMusicEnvironmentSubsystem` |
| `GetSongLength` | 获取当前音乐的长度（以秒为单位） | `UMusicEnvironmentSubsystem` |
| `GetCurrentBeat` | 获取当前音乐的拍子位置（如 4/4 拍中的第几拍） | `UMusicEnvironmentSubsystem` |
| `RegisterForMusicEvent` | 注册一个委托，以监听特定的音乐事件（如“VerseStart”、“ChorusStart”） | `UMusicEnvironmentSubsystem` |
| `SetPlaybackSpeed` | 设置音乐环境的播放速度（影响同步时钟的速率） | `UMusicEnvironmentSubsystem` |

### 使用示例（蓝图描述）

1.  **获取同步时钟**：在任意需要音乐时间的游戏逻辑中，首先通过 `GetMusicEnvironment` 节点获取子系统，然后调用 `GetSyncedClock` 节点。将返回的 `UMusicSyncedClock` 对象引用存储为变量。
2.  **同步生成障碍物**：在一个定时器或 Tick 事件中，比较 `GetGameTimeInSeconds`（来自世界）和从 `UMusicSyncedClock` 获取的 `GetMusicalTimeInSeconds`。当两者差值在某个允许的误差范围内时，生成一个障碍物。
3.  **响应音乐事件**：在 BeginPlay 中，使用 `RegisterForMusicEvent` 节点，指定要监听的事件名称（例如 “ChorusStart”），并绑定一个自定义事件。当音乐播放到副歌部分时，你的自定义事件将被触发，从而可以执行改变场景灯光、加速游戏节奏等操作。

## C++ 用法

### 头文件引入

```cpp
#include "MusicEnvironmentSubsystem.h"
```

### 基本用法

以下代码展示了如何获取音乐环境子系统并使用其同步时钟。

```cpp
// 来自源码分析 (MusicEnvironmentTests)
// 首先，确保你的 Build.cs 依赖了 “MusicEnvironment” 模块。

// 在游戏逻辑类（如 Actor 或 Pawn）中
void AMyMusicSyncedActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取世界并访问子系统
    UWorld* World = GetWorld();
    if (World)
    {
        // 2. 获取全局的 MusicEnvironment 子系统
        UMusicEnvironmentSubsystem* MusicEnv = World->GetSubsystem<UMusicEnvironmentSubsystem>();
        if (MusicEnv)
        {
            // 3. 获取与音乐同步的时钟
            UMusicSyncedClock* SyncedClock = MusicEnv->GetSyncedClock();
            if (SyncedClock)
            {
                // 4. 将时钟用于后续逻辑
                // 例如，将当前音乐时间保存下来，用于与外部事件对比
                UE_LOG(LogTemp, Log, TEXT("Music Synced Time: %f"), SyncedClock->GetMusicalTimeInSeconds());
            }
        }
    }
}
```

### 进阶用法

以下代码结合了获取音乐信息和注册事件监听。

```cpp
// 头文件 (.h)
UPROPERTY()
UMusicSyncedClock* MySyncedClock;

FDelegateHandle MusicEventHandle;
UPROPERTY()
UMusicEnvironmentSubsystem* CachedMusicEnv;

// 实现文件 (.cpp)
void AMyActor::SetupMusicBinding()
{
    UWorld* World = GetWorld();
    if (!World) return;

    CachedMusicEnv = World->GetSubsystem<UMusicEnvironmentSubsystem>();
    if (!CachedMusicEnv) return;

    // 获取时钟
    MySyncedClock = CachedMusicEnv->GetSyncedClock();

    // 注册一个音乐事件监听器
    // 假设有一个名为“Drop”的音乐事件标记在音乐数据中
    MusicEventHandle = CachedMusicEnv->RegisterForMusicEvent(
        TEXT(“Drop”),
        FOnMusicEvent::CreateUObject(this, &AMyActor::OnMusicDrop)
    );
}

void AMyActor::OnMusicDrop(const FMusicEventPayload& Payload)
{
    // 当“Drop”事件触发时执行的操作
    UE_LOG(LogTemp, Warning, TEXT(“Music Drop at time: %f!”), Payload.Timestamp);

    // 示例：激活一个爆炸特效或提升玩家速度
    ActivateExplosionEffect();
    if (MyPlayer)
    {
        MyPlayer->AddSpeedMultiplier(1.5f);
    }
}

void AMyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 重要：清理事件绑定，避免悬垂指针
    if (CachedMusicEnv && MusicEventHandle.IsValid())
    {
        CachedMusicEnv->UnregisterMusicEvent(MusicEventHandle);
        MusicEventHandle.Reset();
    }
    Super::EndPlay(EndPlayReason);
}
```

## Demo 示例

一个最小化的 Actor，用于在音乐的每个节拍上打印日志。

**MyBeatPrinter.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyBeatPrinter.generated.h"

class UMusicSyncedClock;

UCLASS()
class MYPROJECT_API AMyBeatPrinter : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    UMusicSyncedClock* SyncedClock = nullptr;
    float LastPrintedBeat = -1.0f;
};
```

**MyBeatPrinter.cpp**
```cpp
#include "MyBeatPrinter.h"
#include "MusicEnvironmentSubsystem.h"

void AMyBeatPrinter::BeginPlay()
{
    Super::BeginPlay();
    if (UWorld* World = GetWorld())
    {
        if (UMusicEnvironmentSubsystem* MusicEnv = World->GetSubsystem<UMusicEnvironmentSubsystem>())
        {
            SyncedClock = MusicEnv->GetSyncedClock();
        }
    }
}

void AMyBeatPrinter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (SyncedClock)
    {
        // 假设音乐是 4/4 拍，GetCurrentBeat 返回 1.0, 2.0, 3.0, 4.0...
        float CurrentBeat = SyncedClock->GetCurrentBeat();
        // 当拍子发生整数变化时打印
        if (FMath::FloorToInt(CurrentBeat) != FMath::FloorToInt(LastPrintedBeat))
        {
            UE_LOG(LogTemp, Display, TEXT(“Beat: %d”), FMath::FloorToInt(CurrentBeat));
            LastPrintedBeat = CurrentBeat;
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 核心逻辑不依赖特定音频或渲染模块，专注于提供时序框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG迁移至UE_LOGF，为模块化日志做准备。 |
| 2025-09-05 | `de978cf7` | Explicitly adding various missing headers to fix non-unity build errors after large CoreUObject chan | 显式添加缺失的头文件，修复大范围CoreUObject改动后的非统一构建错误。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied) | 为有对应.gen.cpp的源文件添加UE_INLINE_GENERATED_CPP_BY_NAME宏。 |
| 2025-06-23 | `d42c028c` | Music Map Song Length Data | 添加了音乐地图的歌曲长度数据支持。 |
| 2025-06-11 | `e0d87df8` | Replace some usages of FORCEINLINE with inline in Audio modules. | 在音频模块中将部分FORCEINLINE替换为inline。 |

### 维护评价

**状态：实验性且活跃维护中**。

- **年龄**：插件于2024年底创建，非常年轻。
- **更新频率**：近期（2025-2026）有多次更新，主要集中在编译修复、构建系统优化和功能添加（如歌曲长度数据），表明正在活跃开发和迭代。
- **实验性**：`.uplugin` 中 `IsBetaVersion` 和 `IsExperimentalVersion` 均为 `true`，且 `EnabledByDefault` 为 `false`。这明确表明该插件仍处于实验阶段，其API和功能在未来版本中可能发生**重大变更**，不建议用于追求稳定的商业项目。
- **推荐**：如果你正在开发一个对音乐同步有极高要求的原型或实验性项目，并且愿意接受未来可能的API变动和手动维护，可以谨慎使用。对于生产环境项目，建议等待其稳定或寻找替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MusicEnvironment)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MusicEnvironment/Source/MusicEnvironmentTests)