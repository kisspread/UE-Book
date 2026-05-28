# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | 实验性声音插件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，节点定义） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

MetasoundExperimental 是 UE5 MetaSounds 音频框架的**实验性功能孵化器**。它存在的意义在于，在核心 MetaSound 插件 (`Metasound`) 稳定并达到生产就绪状态之前，为开发者提供一个安全的空间来试验和集成尚未完全成熟的新音频功能与节点。

**它解决的问题是：**
1.  **功能隔离：** 将未完全验证的新特性与核心、稳定的 MetaSound 运行时分离，避免实验性代码影响项目稳定性。
2.  **快速迭代：** 允许 Epic 的音频团队快速迭代新想法（如新的音频处理节点、新的数据类型），而无需等待完整的发布周期。
3.  **早期访问：** 为高级开发者提供对前沿音频工具的早期访问权限，以便在功能正式集成前提供反馈。

从源码分析来看，该插件主要包含：
*   **新的音频数据代理系统** (`TCatProxyView`)，用于在游戏线程和音频线程之间安全、高效地传递复杂数据（如音频波形容器）。
*   **新的 MetaSound 节点**，例如“CAT Wave Player”（通道无关波形播放器）和“Granulator”（粒子合成器），这些节点实现了新的音频处理逻辑。
*   **支持这些新节点和数据类型的基础设施**，包括自定义配置结构体、蓝图资产类型和编辑器扩展。

## 使用场景

*   你是一名音频程序员或技术美术，想要尝试使用**新的、实验性的 MetaSound 节点**（如粒子合成）来构建复杂音效，但这些节点尚未并入核心插件。
*   你需要在游戏线程与音频线程之间**安全地传递结构化音频资产数据**（例如一个包含多个音频波形及其权重的容器），并希望有一个无锁的、基于原子操作的高效解决方案。
*   你正在开发一个需要**通道无关（Channel Agnostic）音频处理**的功能，并希望使用为此专门设计的“CAT”节点和数据类型。
*   你愿意接受**实验性 API 可能发生变化**的风险，以换取对最新音频技术的早期使用权。

## 蓝图用法

此插件主要提供可配置的 **MetaSound 节点**和**资产类型**，而非大量供蓝图直接调用的函数。其用法主要体现在 MetaSound 图表的编辑器中。

### 核心资产与节点

| 资产/节点 | 说明 | 所在类/结构体 |
|---|---|---|
| `Audio Sound Wave Container` | 蓝图资产，用于定义和管理一个音频波形列表（支持标准顺序播放和加权随机播放模式）。 | `UCatSoundWaveContainer` |
| `CAT Wave Player` | MetaSound 节点。一个高级波形播放器，支持多声部、多种输出格式和播放模式。 | 节点配置由 `FMetasoundCatWavePlayerNodeConfiguration` 驱动 |
| `Granulator` | MetaSound 节点。实现粒子合成，可以将音频切割成微小的“粒子”并重新组合，创造独特的音效。 | 节点配置由 `FMetaSoundGranulatorNodeConfiguration` 驱动 |
| `Mapping Function` | MetaSound 节点。使用可配置的浮点曲线将输入值映射到输出值。 | 节点配置由 `FMetaSoundMappingFunctionNodeConfiguration` 驱动 |
| `Fade` | MetaSound 节点。生成淡入/淡出曲线，输出可以是浮点值或直接应用于音频缓冲区。 | 节点配置由 `FMetaSoundFadeNodeConfiguration` 驱动 |

### 使用示例（蓝图/MetaSound 编辑器描述）

1.  **创建音频资产容器：**
    *   在内容浏览器中，右键 → 音频 → `Audio Sound Wave Container` 创建资产。
    *   打开资产，设置 `Type` 为 `Standard`（顺序播放）或 `Random`（加权随机播放）。
    *   在 `Entries` 数组中添加条目，每个条目指向一个 `USoundWave` 资产并设置其 `Weight`（用于随机模式）。
2.  **在 MetaSound 中使用：**
    *   在 MetaSound 图表编辑器中，右键添加一个 `CAT Wave Player` 节点。
    *   在节点的细节面板中，可以配置 `MaxVoices`（最大同时发声数）、`Format`（输出格式，如自动、继承自源、或自定义）、`PlaybackType`（索引或顺序）和 `PlaybackMode`（标准或随机）。
    *   将之前创建的 `Audio Sound Wave Container` 资产引用连接到该节点的输入。
    *   添加触发、音高等控制信号来驱动播放。
3.  **配置粒子合成：**
    *   在 MetaSound 图表中添加 `Granulator` 节点。
    *   在细节面板中选择 `OutputAudioTypeName`（输出音频格式，如立体声）和 `GranularEnvelope`（粒子包络形状，如汉宁窗、指数衰减等）。
    *   连接一个音频缓冲区输入到节点，调整参数以获得所需效果。

## C++ 用法

### 头文件引入

```cpp
// 核心代理视图系统
#include "CatAudioProxyView.h"

// 声音波形容器及其代理
#include "CATSoundWaveContainer.h"
#include "CATSoundWaveContainerAsset.h"

// 新的 MetaSound 节点（用于配置）
#include "MetasoundCATWavePlayerNode.h"
```

### 基本用法：TCatProxyView（代理视图）

`TCatProxyView` 是此插件实现线程安全数据传输的核心。以下是一个自定义数据代理的最小用法，源自源码注释。

**来源**: `Engine/Plugins/Experimental/MetasoundExperimental/Source/MetasoundExperimentalEngineRuntime/Public/CatAudioProxyView.h`

```cpp
// 1. 定义你的数据结构
struct FMyAudioSettings
{
    float Volume = 1.0f;
    int32 ChannelCount = 2;
    // ... 其他需要跨线程传递的数据
};

// 2. 定义你的代理类，继承自 TCatProxyView
class FMyAudioSettingsProxy : public Audio::TCatProxyView<FMyAudioSettingsProxy, FMyAudioSettings>
{
public:
    // 必须使用此宏来实现必要的静态方法和静态断言
    IMPL_AUDIOPROXY_CLASS(FMyAudioSettingsProxy);
};

// 3. 使用代理（例如在 UObject 子类中）
// 头文件
UPROPERTY()
TSharedPtr<FMyAudioSettingsProxy> SettingsProxy;

// 创建和发布初始数据
void InitializeSettings()
{
    FMyAudioSettings InitialData;
    InitialData.Volume = 0.8f;
    SettingsProxy = FMyAudioSettingsProxy::Create(MoveTemp(InitialData));
}

// 更新数据（必须从单个线程，通常是游戏线程调用）
void UpdateVolume(float NewVolume)
{
    if (SettingsProxy)
    {
        // 方法 A：对于简单标量更新，可以直接修改数据，无需创建新节点
        // SettingsProxy->GetData().Volume = NewVolume;

        // 方法 B：对于结构性变更（如改变数组大小），或者为了确保读取端获得一致性快照，使用 New()
        FMyAudioSettings UpdatedData = SettingsProxy->GetData();
        UpdatedData.Volume = NewVolume;
        SettingsProxy = SettingsProxy->New(MoveTemp(UpdatedData));
    }
}

// 在音频线程安全地读取数据
void AudioThreadFunction()
{
    if (SettingsProxy)
    {
        // 获取最新的数据版本（遍历原子链表头部）
        TSharedRef<const FMyAudioSettingsProxy> LatestProxy = SettingsProxy->GetLatest();
        const FMyAudioSettings& CurrentData = LatestProxy->GetData();

        // 使用 CurrentData.Volume, CurrentData.ChannelCount 等进行音频处理
        ApplyVolume(CurrentData.Volume);
    }
}
```

### 进阶用法：与 MetaSound 系统集成

要将你的自定义代理数据暴露给 MetaSound 图表，你需要像插件中 `UCatSoundWaveContainer` 和 `FCatSoundWaveContainerProxy` 那样，实现 `IAudioProxyDataFactory` 接口并定义对应的数据引用类型。

**简化概念流程**：
1.  实现一个 `UObject` 子类，并实现 `IAudioProxyDataFactory::CreateProxyData` 接口。在此方法中创建你的代理实例。
2.  定义一个类似于 `FCatSoundWaveContainerData` 的数据类，用于封装你的代理数据。
3.  定义一个类似于 `FCatSoundWaveContainerProxy` 的代理类，继承自 `TCatProxyView`，并可能需要重写 `QueryInterface` 以支持多个接口。
4.  使用 `DECLARE_METASOUND_DATA_REFERENCE_TYPES` 等宏将你的数据类型注册到 MetaSound 前端系统。
5.  创建 MetaSound 节点操作符 (`Metasound::FOperator`)，在其中声明并读取你的数据引用 (`ReadRef`)。

## Demo 示例

一个演示 `TCatProxyView` 基本用法的最小 C++ 类。

**PlayerSettingsProxy.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "CATAudioProxyView.h" // 引入代理视图基类

// 1. 数据结构：存储玩家音频设置
struct FPlayerAudioSettings
{
    float MusicVolume = 0.7f;
    float SFXVolume = 1.0f;
    bool bEnableSurround = false;
};

// 2. 代理类
class FPlayerAudioSettingsProxy : public Audio::TProxyData<FPlayerAudioSettingsProxy>
{
public:
    // 使用宏实现必要的接口
    IMPL_AUDIOPROXY_CLASS(FPlayerAudioSettingsProxy);

    // 构造函数
    using Audio::TProxyData<FPlayerAudioSettingsProxy>::TProxyData;

    // 便捷的访问方法（可选）
    float GetMusicVolume() const { return GetData().MusicVolume; }
};
```

**MyAudioManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "PlayerSettingsProxy.h" // 包含我们的代理定义
#include "MyAudioManager.generated.h"

UCLASS()
class MYPROJECT_API UMyAudioManager : public UObject
{
    GENERATED_BODY()

public:
    // 初始化设置
    void Initialize();

    // 从游戏线程更新设置
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void SetMusicVolume(float NewVolume);

    // 模拟在音频线程消费数据
    void SimulateAudioThreadRead();

private:
    // 持有代理的共享指针
    TSharedPtr<FPlayerAudioSettingsProxy> SettingsProxy;
};
```

**MyAudioManager.cpp**
```cpp
#include "MyAudioManager.h"

void UMyAudioManager::Initialize()
{
    // 创建初始代理数据
    FPlayerAudioSettings InitialSettings;
    SettingsProxy = FPlayerAudioSettingsProxy::Create(MoveTemp(InitialSettings));
    UE_LOG(LogTemp, Log, TEXT("AudioManager Initialized. Music Volume: %f"), SettingsProxy->GetMusicVolume());
}

void UMyAudioManager::SetMusicVolume(float NewVolume)
{
    if (!SettingsProxy.IsValid()) return;

    // 从当前版本获取数据，创建修改后的副本，并发布新版本
    FPlayerAudioSettings UpdatedSettings = SettingsProxy->GetData();
    UpdatedSettings.MusicVolume = FMath::Clamp(NewVolume, 0.0f, 1.0f);
    SettingsProxy = SettingsProxy->New(MoveTemp(UpdatedSettings));

    UE_LOG(LogTemp, Log, TEXT("Music Volume Updated. New Version Created."));
}

void UMyAudioManager::SimulateAudioThreadRead()
{
    if (!SettingsProxy.IsValid()) return;

    // 在音频线程（或模拟它的线程）安全地获取最新数据
    TSharedRef<const FPlayerAudioSettingsProxy> LatestSettings = SettingsProxy->GetLatest();
    const FPlayerAudioSettings& Data = LatestSettings->GetData();

    UE_LOG(LogTemp, Log, TEXT("Audio Thread Read: Music=%.2f, SFX=%.2f, Surround=%s"),
        Data.MusicVolume, Data.SFXVolume, Data.bEnableSurround ? TEXT("ON") : TEXT("OFF"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Metasound` | 基础 MetaSound 框架，提供节点、操作符、前端类型系统等。此插件是其扩展。 |

**注意**：尽管各个 `.Build.cs` 文件仅声明依赖 `CoreUObject`，但作为 MetaSound 的实验性扩展，**运行此插件必须先启用并正确配置核心 `Metasound` 插件**。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 新增实验性通道无关（CAT）波形相关节点和数据类型。 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 新增 CAT 乘法节点。 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 新增 CAT 梯形滤波器节点。 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': | 从待定的更改列表中恢复内容。 |

### 维护评价

*   **创建时间**：创建于 2025 年 4 月，是一个相对年轻的插件。
*   **更新频率**：近期（2026 年 5 月）有密集的功能性更新，新增了多个 “CAT” 系列的实验性节点，表明该项目处于**活跃的开发状态**。
*   **状态**：✅ **活跃维护中**。这是一个由 Epic 官方维护的实验性前沿功能开发库。
*   **已知限制**：
    1.  **实验性**：标记为实验性 (`IsExperimentalVersion=true`)，API 和功能可能在不预告的情况下发生破坏性变更。
    2.  **默认未启用**：需要手动在项目设置中启用，表明其并非面向所有用户。
    3.  **依赖核心插件**：其功能建立在核心 `Metasound` 插件之上。
*   **推荐使用**：**仅推荐给希望探索 MetaSound 最新实验性功能、并能接受潜在 API 变更和不稳定风险的高级用户和技术美术/音频程序员**。不建议在追求稳定性的生产项目中作为核心依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- [官方文档]()（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental/Tests) (如果存在)