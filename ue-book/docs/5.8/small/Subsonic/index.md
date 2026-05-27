# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是 Unreal Engine 的一个**实验性高级音频创作与回放系统**。它旨在解决 UE 原生音频系统在处理复杂、动态、程序化音频场景时的局限性，为开发者提供一个更强大、更灵活的音频工作流。该系统可能包含对动态音乐系统、高级空间音频、音频事件、程序化音效生成等高级功能的支持，是对 UE 核心音频引擎的重大扩展。

## 使用场景

-   你需要为开放世界游戏创建一个完全动态、根据玩家行为实时变化的**音乐系统**。
-   你在开发一个 VR 或沉浸式体验，需要极其精确和复杂的 **3D 空间音频**效果。
-   你的游戏玩法机制高度依赖于**程序化生成的音效**，例如基于物理碰撞的实时音效合成。
-   你需要一个统一的、可视化的**音频事件和逻辑编辑器**，来替代在蓝图中分散的音频逻辑。
-   你希望使用下一代音频技术来构建游戏的听觉体验，并愿意接受实验性 API 带来的变化风险。

## 蓝图用法

作为实验性系统，其蓝图 API 可能会快速演变。核心功能通常围绕音频资产的创建、触发和控制。

### 核心节点（示例性分组）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Subsonic Sound` | 触发一个 Subsonic 音频事件或资产 | `USubsonicSubsystem` 或类似管理类 |
| `Set Audio Parameter` | 动态调整正在播放的音频的参数（如音量、音高、滤波器） | `USubsonicComponent` 或类似运行时对象 |
| `Create Audio Event` | 动态创建一个音频事件实例 | 工厂类或子系统 |

*（注：具体函数名需查阅最新的 `SubsonicCore` 模块头文件，上述为基于音频系统常见模式的推断。）*

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicCoreModule.h"
// 根据需要，可能还需引入 SubsonicEngine 或特定子系统头文件
```

### 基本用法

从模块设计推断，通常会通过一个子系统或管理器类来使用核心功能。

```cpp
// 假设的示例，基于音频系统常见模式
void AMyActor::SetupDynamicMusic()
{
    // 1. 获取 Subsonic 子系统
    if (UGameInstance* GameInstance = GetGameInstance())
    {
        USubsonicSubsystem* SubsonicSubsystem = GameInstance->GetSubsystem<USubsonicSubsystem>();
        if (SubsonicSubsystem)
        {
            // 2. 创建一个动态音乐上下文
            FSubsonicMusicContext MusicContext;
            MusicContext.MusicAsset = MyDynamicMusicAsset;
            MusicContext.LayerNames = {TEXT("Base"), TEXT("Intensity"), TEXT("Tension")};

            // 3. 播放并获取句柄以便后续控制
            FSubsonicMusicHandle MusicHandle = SubsonicSubsystem->PlayDynamicMusic(MusicContext);

            // 4. 在后续逻辑中根据游戏状态改变音乐层强度
            SubsonicSubsystem->SetMusicLayerIntensity(MusicHandle, TEXT("Tension"), CurrentTensionValue);
        }
    }
}
```

### 进阶用法

结合多个子系统和自定义逻辑，构建复杂的音频体验。

```cpp
// 在 AI 感知系统中集成 3D 空间音频反馈
void UEnemyAIPerceptionComponent::OnTargetPerceptionUpdated(AActor* Actor, FAIStimulus Stimulus)
{
    if (SubsonicSubsystem && Stimulus.WasSuccessfullySensed())
    {
        // 根据威胁程度和距离，播放一个动态混合的音频提示
        FSubsonicSpatialSoundParams SpatialParams;
        SpatialParams.SourceActor = Actor;
        SpatialParams.BaseSound = ThreatDetectionSound;
        SpatialParams.Parameters.Add(TEXT("ThreatLevel"), GetThreatLevel(Actor));
        SpatialParams.Parameters.Add(TEXT("Distance"), FVector::Dist(GetOwner()->GetActorLocation(), Actor->GetActorLocation()));

        SubsonicSubsystem->PlaySpatialSound(SpatialParams);
    }
}
```

## Demo 示例

一个最小化的、展示基本初始化和播放的 C++ 示例。

**SubsonicDemoActor.h**
```cpp
// SubsonicDemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "SubsonicDemoActor.generated.h"

class USubsonicSubsystem;
class USoundBase; // 假设 Subsonic 音频资产继承自或类似此类

UCLASS()
class ASubsonicDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ASubsonicDemoActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Subsonic Demo")
    void TriggerDemoSound();

private:
    UPROPERTY(EditAnywhere, Category = "Subsonic Demo")
    USoundBase* DemoSoundAsset;

    UPROPERTY()
    USubsonicSubsystem* CachedSubsystem;
};
```

**SubsonicDemoActor.cpp**
```cpp
// SubsonicDemoActor.cpp
#include "SubsonicDemoActor.h"
#include "SubsonicSubsystem.h" // 假设的子系统头文件
#include "GameFramework/GameInstance.h"

ASubsonicDemoActor::ASubsonicDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ASubsonicDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 在 BeginPlay 中缓存子系统引用以提高性能
    if (UGameInstance* GI = GetGameInstance())
    {
        CachedSubsystem = GI->GetSubsystem<USubsonicSubsystem>();
    }
}

void ASubsonicDemoActor::TriggerDemoSound()
{
    if (CachedSubsystem && DemoSoundAsset)
    {
        // 使用子系统播放声音，可能支持更多参数
        CachedSubsystem->PlaySoundAtLocation(DemoSoundAsset, GetActorLocation());
        UE_LOG(LogTemp, Log, TEXT("Subsonic demo sound triggered."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Subsonic demo sound failed: Subsystem or Asset not available."));
    }
}
```

## 模块依赖

要使用 Subsonic 插件，你的项目模块需要依赖其核心模块。

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | 提供核心的音频数据类型、接口和子系统基类。**这是使用 Subsonic 功能的主要依赖。** |
| `SubsonicEngine` | 包含引擎集成层，将 Subsonic 与 UE 的渲染、物理、游戏逻辑等系统连接。通常由插件内部使用，高级用户可能直接依赖。 |
| `SubsonicEditor` | 提供编辑器专用工具、资产编辑器、自定义细节面板等。仅在开发编辑器功能或工具时依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并错误，回滚了对订阅系统的破坏性改动，应用了最小化的非废弃性修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 `FSoundWaveData` API 废弃相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或消除了 PVS（代码静态分析）警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“添加”菜单中新增了音频相关菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF`。 |

### 维护评价

Subsonic 是一个**全新且活跃开发中的实验性插件**。从创建时间（2026年1月）和最近的提交记录（2026年5月）来看，它正处于**初期快速开发和迭代阶段**。近期的提交主要是**合并修复、API 适配和代码清理**，而非重大新功能，这表明代码正在趋于稳定，为后续功能扩展打基础。

**主要提示**：
1.  **实验性**：文档明确指出其 API 不保证向后兼容，意味着在升级引擎版本时可能会有破坏性更改。
2.  **活跃但风险高**：推荐给勇于尝试新技术、且项目周期能承担 API 变更风险的开发者。不建议用于需要长期稳定维护的已上线项目。
3.  **文档缺乏**：作为实验性功能，官方文档 (`DocsURL`) 为空，使用时需要更多地依赖源码、测试用例和社区探索。

**结论**：**目前不推荐用于生产环境**，但适合用于原型验证、技术预研或对音频系统有前沿需求的独立实验项目。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest) （`SubsonicEngineTest` 模块通常包含自动化测试和用法示例）