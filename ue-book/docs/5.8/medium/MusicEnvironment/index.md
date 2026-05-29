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

`MusicEnvironment` 插件旨在为整个游戏项目提供一个统一、全局的音乐信息中心。它不是一个具体的音效播放器，而是一个基础设施层，用于管理和广播与音乐节奏相关的核心数据，例如精确的音乐时钟（Musically Synchronized Clocks）、节拍事件、小节信息等。其核心目的是解决在音游、音乐可视化或任何需要游戏逻辑与音乐节奏严格同步的场景中，时钟源不统一和同步精度不足的问题。通过此插件，游戏中的不同系统（如动画、特效、玩法逻辑）可以订阅同一个权威的音乐时间线，从而实现精准的协同。

## 使用场景

- 你正在开发一款音乐节奏游戏（音游），需要让玩家的输入判定、视觉特效与音乐节拍严格同步。
- 你的游戏中有大量随音乐节奏变化的灯光、场景或角色动画，需要一个全局的“节拍发生器”来驱动它们。
- 你需要创建一个复杂的音乐可视化程序，需要从游戏音频流中提取实时的节奏和节拍信息。
- 你在实现一个“音乐驱动”（Music-driven）的玩法机制，例如只有在特定节拍点击才有效的互动。

## 蓝图用法

该插件的核心是提供音乐环境信息。由于是底层设施，其蓝图暴露主要通过子模块中的工具类完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `获取音乐时钟` | 获取当前项目中全局唯一的音乐同步时钟实例。 | `UMusicEnvironmentSubsystem` |
| `绑定节拍事件` | 将一个自定义事件绑定到音乐时钟的节拍回调上。 | `UMusicEnvironmentSubsystem` |

### 使用示例（蓝图描述）

1.  **获取时钟**：在任何需要音乐时间的蓝图中，首先通过 `Get Music Clock` 节点获取全局音乐时钟。
2.  **监听节拍**：使用 `Bind to Beat` 节点，将一个自定义事件（例如 `On Beat Hit`）绑定到时钟上。当音乐播放到每个节拍点时，系统会自动调用你的事件。
3.  **使用时间数据**：在你的自定义事件中，你可以使用时钟提供的时间数据（如当前拍子位置、BPM等）来驱动其他逻辑，例如播放粒子特效或改变材质参数。

## C++ 用法

C++ 端的使用主要围绕获取和监听全局音乐环境子系统。

### 头文件引入

```cpp
#include "MusicEnvironmentSubsystem.h"
```

### 基本用法

从子系统获取音乐时钟并监听基本事件。

```cpp
// 获取游戏世界的音乐环境子系统
UMusicEnvironmentSubsystem* MusicEnvSubsystem = GetWorld()->GetSubsystem<UMusicEnvironmentSubsystem>();
if (MusicEnvSubsystem)
{
    // 获取音乐时钟
    UMusicClock* MusicClock = MusicEnvSubsystem->GetMusicClock();
    if (MusicClock)
    {
        // 使用时钟的当前时间（例如，设置一个动画的起始时间）
        float CurrentSongBeat = MusicClock->GetCurrentSongBeat();
        // ... 进行与节拍相关的逻辑
    }
}
```

### 进阶用法

注册委托以监听节拍变化等事件。

```cpp
// 在某个 Actor 的 BeginPlay 中
if (UMusicEnvironmentSubsystem* MusicEnvSubsystem = GetWorld()->GetSubsystem<UMusicEnvironmentSubsystem>())
{
    // 绑定一个成员函数到节拍事件
    MusicEnvSubsystem->GetMusicClock()->OnBeat.AddUObject(this, &AMyActor::HandleBeatEvent);
}

// 对应的回调函数
void AMyActor::HandleBeatEvent(float BeatNumber)
{
    // 在每个节拍触发时执行的操作
    UE_LOG(LogTemp, Log, TEXT("Beat! %f"), BeatNumber);
    // 例如：播放一个音效，或触发一个粒子效果
}
```

## Demo 示例

由于该插件是底层设施，完整的演示通常需要结合具体音频播放器（如 `Metasound`）和音频分析系统。一个最小的 C++ 使用模式如下：

**MyMusicDrivenActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMusicDrivenActor.generated.h"

class UMusicClock;

UCLASS()
class AMyMusicDrivenActor : public AActor
{
    GENERATED_BODY()
    
public:
    virtual void BeginPlay() override;

private:
    UFUNCTION()
    void OnMusicBeat(float BeatNumber);

    UPROPERTY()
    TObjectPtr<UMusicClock> CachedMusicClock;
};
```

**MyMusicDrivenActor.cpp**
```cpp
#include "MyMusicDrivenActor.h"
#include "MusicEnvironmentSubsystem.h"
#include "MusicClock.h"

void AMyMusicDrivenActor::BeginPlay()
{
    Super::BeginPlay();
    
    if (UMusicEnvironmentSubsystem* MusicEnv = GetWorld()->GetSubsystem<UMusicEnvironmentSubsystem>())
    {
        CachedMusicClock = MusicEnv->GetMusicClock();
        if (CachedMusicClock)
        {
            CachedMusicClock->OnBeat.AddDynamic(this, &AMyMusicDrivenActor::OnMusicBeat);
        }
    }
}

void AMyMusicDrivenActor::OnMusicBeat(float BeatNumber)
{
    // 在此处实现与节拍同步的逻辑
    // 例如，让 Actor 跳跃
    UE_LOG(LogTemp, Warning, TEXT("Jumping on beat %f!"), BeatNumber);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏至新标准。 |
| 2025-09-05 | `de978cf7` | Explicitly adding various missing headers to fix non-unity build errors after large CoreUObject chan | 补充缺失的头文件以修复非统一构建错误。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联生成宏，优化编译。 |
| 2025-06-23 | `d42c028c` | Music Map Song Length Data | 新增音乐地图歌曲时长数据功能。 |
| 2025-06-11 | `e0d87df8` | Replace some usages of FORCEINLINE with inline in Audio modules. | 将音频模块中部分 FORCEINLINE 替换为 inline。 |

### 维护评价

`MusicEnvironment` 是一个于2024年底创建的实验性插件（Beta/Experimental），目前处于早期开发阶段。从最近的提交记录看，插件仍在维护中，最近的更新主要是底层代码维护、编译修复以及功能补充（如歌曲长度数据）。由于它是项目级的基础设施，且标记为实验性，其API和功能可能在未来版本中发生变化。**推荐在需要高精度音乐同步的音游或相关项目中谨慎评估和使用，并做好应对API变动的准备。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MusicEnvironment)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MusicEnvironment/Source/MusicEnvironmentTests)