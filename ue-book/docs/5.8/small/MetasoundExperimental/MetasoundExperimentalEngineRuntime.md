# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音频元声音实验 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

本插件是 Unreal Engine Metasound 音频系统的实验性扩展。其主要用途是在将新功能（如 CAT（Channel Agnostic Types，通道无关类型）系统）集成到主插件之前，提供一个稳定、可独立迭代的开发和测试环境。从源码分析可见，它实现了一个线程安全的音频代理数据视图 (`TCatProxyView`)，以及基于此构建的声音波形容器 (`UCatSoundWaveContainer`) 和一系列实验性 Metasound 节点（如波形播放器、颗粒化器）。这些功能旨在提供更灵活、更高级的音频合成与处理能力，特别是与 CAT 相关的多通道音频处理。

## 使用场景

- 你是音频技术美术或程序员，需要为下一代游戏开发更强大、更灵活的音频合成与回放系统。
- 你想提前尝试或评估 Unreal Engine 未来可能引入的 Metasound 新功能，例如 CAT 系统。
- 你需要处理复杂的音频资产（如包含多个音效波形的容器），并希望以线程安全的方式将其与 Metasound 图形连接。
- 你正在开发需要自定义颗粒合成、高级淡入淡出或复杂映射函数的音频效果。

## 蓝图用法

本插件提供的核心蓝图功能围绕其新增的数据类型和节点配置。

### 核心资产与节点

| 节点/资产 | 说明 | 所在类/枚举 |
|---|---|---|
| `Audio Sound Wave Container` | 蓝图资产，用于打包和管理一组 SoundWave 资产及其权重，支持随机或顺序播放。 | `UCatSoundWaveContainer` |
| `CAT Wave Player` 配置 | Metasound 节点配置，用于控制波形播放器的格式、回放模式等。 | `FMetasoundCatWavePlayerNodeConfiguration` |
| `Granulator` 配置 | Metasound 节点配置，用于控制颗粒化合成器的输出通道格式和包络类型。 | `FMetaSoundGranulatorNodeConfiguration` |
| `Fade` 节点配置 | Metasound 节点配置，用于控制淡入淡出效果的输出类型（浮点数或音频缓冲区）。 | `FMetaSoundFadeNodeConfiguration` |
| `Mapping Function` 节点配置 | Metasound 节点配置，用于通过可编辑的曲线将输入值映射到输出值。 | `FMetaSoundMappingFunctionNodeConfiguration` |

### 使用示例（蓝图描述）

1.  **创建声音波形容器**:
    *   在内容浏览器右键 -> `Audio` -> `Audio Sound Wave Container`。
    *   打开资产，设置 `Type` 为 `Standard` 或 `Random`。
    *   在 `Entries` 数组中添加多个 `USoundWave` 条目，并为每项设置 `Weight`。
    *   此资产可作为输入连接到 Metasound 中的 `CAT Wave Player` 节点的 `Sound Wave Container` 引脚。

2.  **配置 CAT Wave Player 节点**:
    *   在 Metasound 编辑器中，添加一个 `CAT Wave Player` 节点。
    *   在节点细节面板中，配置 `MaxVoices`、`Format`（如 `SourceAuto` 或 `Custom`）、`PlaybackType` 和 `PlaybackMode`。
    *   当选择 `Custom` 格式时，需要指定具体的 `CustomFormat`（例如 `Cat:Stereo2Dot0`）。

## C++ 用法

### 头文件引入

```cpp
#include "CatAudioProxyView.h"
#include "CatSoundWaveContainer.h"
#include "CatSoundWaveContainerAsset.h"
// 以及其他需要的节点头文件，如 MetasoundCatWavePlayerNode.h
```

### 基本用法：使用 `TCatProxyView` 创建线程安全代理

`TCatProxyView` 提供了一种在游戏线程创建/更新数据，并安全地从音频线程读取最新版本的机制。

```cpp
// （概念性示例，基于 CatAudioProxyView.h 中的注释）
struct FMyAudioData
{
    float Frequency = 440.0f;
    // ... 其他数据
};

// 1. 定义你的代理类
class FMyProxy : public Audio::TCatProxyView<FMyProxy, FMyAudioData>
{
public:
    // 必须使用此宏
    IMPL_AUDIOPROXY_CLASS(FMyProxy);
};

// 2. 在游戏线程创建并发布初始数据
TSharedRef<FMyProxy> MyProxy = FMyProxy::Create(FMyAudioData{440.0f});

// 3. 在游戏线程更新数据（结构性变化，如增减数组元素）
MyProxy = MyProxy->New(FMyAudioData{880.0f}); // 发布新版本

// 4. 在音频线程安全读取最新数据
TSharedRef<const FMyProxy> LatestProxy = MyProxy->GetLatest();
float CurrentFreq = LatestProxy->GetData().Frequency;

// 注意：对于简单的标量更新（如修改 Frequency），可直接在 GetData() 引用上修改，无需调用 New()。
```

### 进阶用法：管理声音波形容器代理

`UCatSoundWaveContainer` 和 `FCatSoundWaveContainerProxy` 是 `TCatProxyView` 在实际资产上的应用。

```cpp
#include "CatSoundWaveContainer.h"

// 1. 获取或创建容器资产
UCatSoundWaveContainer* MyContainer = NewObject<UCatSoundWaveContainer>();

// 2. 设置容器类型和条目（通常在编辑器或蓝图中完成）
MyContainer->Type = ECatSoundWaveContainerType::Random;
FCatSoundWaveContainerEntry Entry;
Entry.SoundWave = LoadObject<USoundWave>(nullptr, TEXT("/Game/Audio/MyWave"));
Entry.Weight = 1.0f;
MyContainer->Entries.Add(Entry);

// 3. 从容器创建音频代理数据（用于连接到 Metasound）
Audio::FProxyDataInitParams InitParams;
TSharedPtr<Audio::IProxyData> ProxyData = MyContainer->CreateProxyData(InitParams);
// 返回的 ProxyData 实际是 FCatSoundWaveContainerProxy，可安全转换
TSharedPtr<FCatSoundWaveContainerProxy> WaveProxy = StaticCastSharedPtr<FCatSoundWaveContainerProxy>(ProxyData);

// 4. 在 Metasound 节点操作符中使用代理数据包装器
MetasoundCatExperimental::FSoundWaveContainerAsset ContainerAsset(ProxyData);
// 在音频线程安全获取最新容器数据
TSharedPtr<const FCatSoundWaveContainerProxy> LatestContainer = ContainerAsset.GetLatest();
if (LatestContainer.IsValid())
{
    // 获取容器内的波形代理列表
    TArray<FSoundWaveProxyPtr> Waves = LatestContainer->GetData().GetContainedWaveProxies();
    // ... 使用波形进行播放
}
```

## Demo 示例

一个最小化示例，展示如何创建并使用 `UCatSoundWaveContainer`。

**MyAudioComponent.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CatSoundWaveContainer.h"
#include "MyAudioComponent.generated.h"

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMyAudioComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Audio")
    TObjectPtr<UCatSoundWaveContainer> WaveContainerAsset;

    UFUNCTION(BlueprintCallable, Category = "Audio")
    void UpdateAndPlayContainer();

private:
    UPROPERTY()
    TObjectPtr<UCatSoundWaveContainer> RuntimeContainer;
    TSharedPtr<FCatSoundWaveContainerProxy> ContainerProxy;
};
```

**MyAudioComponent.cpp**
```cpp
#include "MyAudioComponent.h"
#include "Engine/Engine.h" // 用于 GEngine 输出

void UMyAudioComponent::UpdateAndPlayContainer()
{
    if (!WaveContainerAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("WaveContainerAsset is not set!"));
        return;
    }

    // 1. 创建运行时容器（或在构造函数中创建）
    if (!RuntimeContainer)
    {
        RuntimeContainer = NewObject<UCatSoundWaveContainer>(this);
    }

    // 2. 复制资产设置到运行时容器
    RuntimeContainer->Type = WaveContainerAsset->Type;
    RuntimeContainer->Entries = WaveContainerAsset->Entries;

    // 3. 手动触发代理重建（模拟属性变更或用于初始化）
    RuntimeContainer->RebuildProxy();

    // 4. 获取生成的代理（通常在 `CreateProxyData` 之后自动存储）
    // 注意：实际生产中，代理生命周期由 Metasound 图管理，此示例仅为演示数据流。
    Audio::FProxyDataInitParams InitParams;
    TSharedPtr<Audio::IProxyData> ProxyData = RuntimeContainer->CreateProxyData(InitParams);
    ContainerProxy = StaticCastSharedPtr<FCatSoundWaveContainerProxy>(ProxyData);

    if (ContainerProxy.IsValid())
    {
        TSharedRef<const FCatSoundWaveContainerProxy> Latest = ContainerProxy->GetLatest();
        TArray<FSoundWaveProxyPtr> Waves = Latest->GetData().GetContainedWaveProxies();
        UE_LOG(LogTemp, Log, TEXT("Container published with %d wave entries."), Waves.Num());
        // 在此将 ContainerProxy 连接到实际的 Metasound 播放图中...
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | `MetasoundExperimentalEngineRuntime` 及其兄弟模块的 Build.cs 主要依赖 `CoreUObject`，这是基础依赖。插件本身依赖 `Metasound` 插件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 添加了实验性的元声音通道无关类型(CAT)波形功能。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃相关的合并冲突。 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 添加了 [CAT] 乘法节点。 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 添加了 [CAT] 梯形滤波器节点。 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': | 从待处理变更列表中取消搁置。 |

### 维护评价

- **活跃维护**: 该插件处于非常活跃的开发状态。从 Git 历史看，最近（2026年5月）有密集的提交，主要围绕 **CAT（通道无关类型）** 功能的开发和集成，包括新的节点（乘法、滤波器）和波形系统。这表明 Epic 的音频团队正在积极地向此插件添加新功能。
- **实验性质**: 插件本身标记为 `IsExperimentalVersion: true`，且 `EnabledByDefault: false`。这意味着其中的 API 和功能在未来的引擎版本中可能发生重大变更或被移除。它主要用于内部开发和测试新想法。
- **潜在问题**: 由于是实验性代码，可能存在未完全优化、接口不稳定或文档缺失的情况。部分注释提到与其他模块（如 `MetasoundPolyphonyInternal`）存在功能重叠或需要整合。
- **推荐使用**: **不推荐用于正式生产项目**。如果你是研究或学习引擎内部音频系统、或者愿意承担 API 变更的风险来尝试最前沿功能，可以启用此插件。对于生产项目，应等待功能成熟并合并到主 `Metasound` 插件中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- 官方文档：无
- 测试用例：未在提供的路径中找到（可能位于 Engine/Tests/ 或其他位置，需进一步查找）