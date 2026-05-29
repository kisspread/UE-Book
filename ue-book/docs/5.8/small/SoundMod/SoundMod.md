# Sound Module Plugin

> 支持播放 ProTracker (MOD)、Scream Tracker 3 (S3M)、Fast Tracker II (XM) 和 Impulse Tracker (IT) 格式的音乐文件。

| 属性 | 值 |
|---|---|
| 中文名 | 音乐模块插件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SoundMod` (Runtime), `SoundModImporter` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-06-13 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundMod) | |

## 用途

该插件的核心功能是将老式音乐跟踪器（Tracker）格式的音乐文件集成到 Unreal Engine 的音频系统中。它不是一个简单的播放器，而是通过提供自定义的 `USoundMod` 资产类型和 `USoundNodeModPlayer` 声音节点，让开发者能够像使用普通声音波形（WAV）或声音提示（Sound Cue）一样，在游戏内播放和控制 MOD、S3M、XM、IT 这些在 90 年代流行的模块化音乐格式。它解决了在 Unreal Engine 中无缝使用这类特定格式背景音乐或音效的需求。

## 使用场景

-   你正在开发一个独立游戏，希望使用经典 8-bit 或 16-bit 风格的 MOD 音乐作为背景音轨。
-   你的游戏项目中已有一批从旧项目或特定社区获取的 MOD 格式音乐文件，需要直接集成到 UE 项目中播放。
-   你需要在 Unreal 引擎中对 MOD 音乐进行播放、循环、空间化等标准音频操作，而不是依赖外部播放库。

## 蓝图用法

该插件提供的核心蓝图功能通过 `USoundNodeModPlayer` 声音节点实现，通常在声音提示（Sound Cue）编辑器中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSoundMod` | 获取此声音节点当前引用的 `USoundMod` 资产。 | `USoundNodeModPlayer` |
| `SetSoundMod` | 设置此声音节点要引用的 `USoundMod` 资产。 | `USoundNodeModPlayer` |

### 使用示例（蓝图描述）

1.  **资产导入**：首先需要将 MOD 文件通过 `SoundModImporter` 导入为 `USoundMod` 资产。
2.  **声音提示 (Sound Cue) 制作**：
    *   打开或创建一个 `Sound Cue` 资产。
    *   在节点图中右键点击，搜索并添加 “Mod Player” 节点。
    *   在“细节”面板中，将“Sound Mod”属性指向你导入的 `USoundMod` 资产。
    *   勾选“Looping”以启用循环播放。
    *   将此节点的输出连接到 `Sound Cue` 的 `Output` 节点。
3.  **在游戏逻辑中使用**：将制作好的 `Sound Cue` 资产像普通声音一样，用于 `Play Sound At Location`、`Play Sound 2D` 等蓝图节点进行播放。

## C++ 用法

### 头文件引入

```cpp
#include "SoundMod.h"
#include "SoundModWave.h"
#include "SoundNodeModPlayer.h"
```

### 基本用法

该插件主要通过资产和声音节点在编辑器中使用，C++ 端更侧重于底层播放控制。以下是一个程序化创建和播放 MOD 声音的示例：

```cpp
// 假设已经有一个加载好的 USoundMod* SoundModAsset
// SoundModAsset 通常通过资产系统异步加载或硬路径引用获得

if (SoundModAsset)
{
    // 创建一个过程化声音波形，用于播放 MOD 数据
    USoundModWave* ModWave = NewObject<USoundModWave>(GetTransientPackage());
    ModWave->SoundMod = SoundModAsset;
    
    // 设置循环属性
    ModWave->bLooping = true;
    
    // 使用标准的 UGameplayStatics 接口播放此过程化声音
    UGameplayStatics::PlaySound2D(GetWorld(), ModWave, 1.0f, 1.0f);
}
```

**注意**：`USoundModWave` 内部使用 `xmp_context` 库来解码 MOD 数据并生成 PCM 数据，这些过程对用户是透明的。

## Demo 示例

以下是一个可编译的最小示例，演示如何在 C++ 中引用并准备播放一个 `USoundMod` 资产。

**MySoundModActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SoundMod.h"
#include "MySoundModActor.generated.h"

UCLASS()
class AMySoundModActor : public AActor
{
    GENERATED_BODY()
    
public:    
    AMySoundModActor();

protected:
    virtual void BeginPlay() override;

public:    
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, Category = "Sound")
    TSoftObjectPtr<USoundMod> ModMusicAsset;
    
    UPROPERTY(EditAnywhere, Category = "Sound")
    bool bPlayOnStart = true;

private:
    UPROPERTY()
    TObjectPtr<USoundModWave> PlayingModWave;
};
```

**MySoundModActor.cpp**
```cpp
#include "MySoundModActor.h"
#include "SoundModWave.h"
#include "Kismet/GameplayStatics.h"

AMySoundModActor::AMySoundModActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMySoundModActor::BeginPlay()
{
    Super::BeginPlay();

    if (bPlayOnStart && !ModMusicAsset.IsNull())
    {
        // 异步加载 MOD 资产（简化示例，实际应使用异步加载代理）
        USoundMod* LoadedMod = ModMusicAsset.LoadSynchronous();
        if (LoadedMod)
        {
            // 创建并播放过程化波形
            PlayingModWave = NewObject<USoundModWave>(this);
            PlayingModWave->SoundMod = LoadedMod;
            PlayingModWave->bLooping = true;
            
            UGameplayStatics::PlaySound2D(GetWorld(), PlayingModWave);
        }
    }
}

void AMySoundModActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}
```

## 模块依赖

从源码结构和常见实践推断，使用者需要依赖：

| 模块 | 用途 |
|---|---|
| `CoreUObject` | 基础对象系统、资产引用。 |
| `Engine` | 声音系统基类 (`USoundBase`, `USoundNode`)、音频设备。 |
| `AudioMixer` | 现代音频混音系统（可能被底层使用）。 |

**注意**：`SoundModImporter` 编辑器模块仅用于资产导入，运行时游戏模块无需依赖它。无其他特殊依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and sub | 修复了静态分析警告 V623，优化了条件运算符可能产生的临时对象。 |
| 2025-05-27 | `5961ff5b` | Fix for loctext collision | 修复了本地化文本冲突问题。 |
| 2023-05-16 | `381f77ac` | Optimized include module name dependencies. | 优化了头文件中的模块依赖包含关系。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 一批插件相关的通用引擎更新（可能是编译或接口适配）。 |
| 2022-12-14 | `96ab5837` | Deprecate use of TUniquePtr in Audio::IProxyData | 标记废弃了音频代理数据接口中 `TUniquePtr` 的使用。 |

### 维护评价

**维护评价：维护中，但功能稳定**

该插件创建于 2014 年，是一个历史悠久的模块。尽管它支持的音乐格式在现代游戏中已不常见，但引擎团队仍在持续进行维护。最近的更新集中在 **代码质量修复（静态分析警告）和本地化冲突修复**，而非新功能开发，这表明它已被视为**功能完善且稳定的遗产代码**。最后一次功能性改动追溯到 2022 年底的音频接口更新。

-   **优点**：代码仍被维护以兼容新引擎版本，没有明显的废弃标记。
-   **缺点**：功能长期未增长，目标用户群非常小众。
-   **推荐**：如果你的项目**必须使用** MOD、S3M、XM、IT 格式的音乐，此插件是官方支持的直接解决方案。否则，对于新的音乐项目，建议使用现代音频格式或 FMOD/Wwise 等中间件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundMod)
-   官方文档（无）
-   测试用例（无）