# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | 声音元实验 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（实验性音频节点、数据资产、配置） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

该插件是官方 `Metasound` 插件的实验性开发分支，旨在为新的、尚未完全成熟的音频功能提供一个隔离的测试和开发环境。它包含一系列实验性的 MetaSound 节点、数据结构和运行时支持，用于探索新的音频处理范式，例如通道无关音频（Channel Agnostic Types, CAT）技术、颗粒化合成等。开发者可以在此插件中安全地试用这些前沿功能，待其稳定后再迁移至主 `Metasound` 插件。

## 使用场景

-   你需要为 MetaSound 图使用更高级、实验性的音频处理节点（如颗粒化器、映射函数节点）。
-   你在开发需要支持通道无关（Channel Agnostic）音频处理的系统，特别是需要处理动态多通道音频容器。
-   你希望提前体验和测试 Epic 正在开发中的 MetaSound 新功能。
-   **注意**：由于此插件标记为实验性且默认禁用，功能接口和实现可能会在后续版本中发生重大变更，不建议在稳定发布的项目中作为核心依赖使用。

## 蓝图用法

实验性插件提供的核心功能主要在 C++ 运行时层面，但部分配置和数据资产可以在蓝图中使用。

### 核心节点/资产

| 节点/资产 | 说明 | 所在类 |
|---|---|---|
| `UCatSoundWaveContainer` | 可蓝图化的资产，用于管理一组 `USoundWave` 及其权重，支持顺序和随机播放。是实验性波形播放器的数据源。 | `UCatSoundWaveContainer` (UObject) |
| `FCatSoundWaveContainerEntry` | 用于配置 `UCatSoundWaveContainer` 中每个条目的结构体，包含声音资产引用和权重。 | 结构体 |
| `FMetasoundCatWavePlayerNodeConfiguration` | CAT 波形播放器节点的配置结构体，可在节点细节面板中设置最大声部数、输出格式、播放类型等。 | 结构体 |
| `FMetaSoundGranulatorNodeConfiguration` | 颗粒化节点的配置结构体，用于设置输出通道类型和颗粒包络类型。 | 结构体 |
| `FMetaSoundMappingFunctionNodeConfiguration` | 映射函数节点的配置结构体，可定义输入输出映射曲线和输入值包裹行为。 | 结构体 |

### 使用示例（蓝图描述）

1.  **创建声音波形容器**：
    *   在内容浏览器右键，创建 `Audio Sound Wave Container` 资产。
    *   打开该资产，在 `Type` 中选择播放模式（`Standard` 或 `Random`）。
    *   在 `Entries` 数组中添加条目，为每个条目指定一个 `SoundWave` 资产和 `Weight`。
    *   保存资产。此容器资产可作为实验性 `CAT Wave Player` 节点的输入。
2.  **使用实验性节点**：
    *   打开 MetaSound 编辑器。
    *   在节点库中搜索实验性节点（如 `CAT Wave Player`、`Granulator`）。
    *   将节点添加到图表中，通过节点的细节面板配置其特有的属性（如 `FMetasoundCatWavePlayerNodeConfiguration` 中的参数）。
    *   连接节点的输入输出引脚。

## C++ 用法

### 头文件引入

```cpp
// 包含核心实验性运行时模块（取决于具体使用的功能）
#include "MetasoundExperimentalEngineRuntime.h"

// 如果使用声音波形容器代理
#include "CatSoundWaveContainer.h"

// 如果使用无锁代理视图模式
#include "CatAudioProxyView.h"
```

### 基本用法 (创建并使用声音波形容器代理)

此示例展示了如何在代码中创建一个 `UCatSoundWaveContainer` 并发布其代理数据，以便在音频线程安全地访问。

```cpp
// 来源: CatSoundWaveContainer.h
// 创建一个容器 UObject
UCatSoundWaveContainer* Container = NewObject<UCatSoundWaveContainer>();

// 配置容器
Container->Type = ECatSoundWaveContainerType::Random;
Container->Entries.Add(FCatSoundWaveContainerEntry(MySoundWave1));
Container->Entries.Add(FCatSoundWaveContainerEntry(MySoundWave2));

// 手动触发代理重建（在非编辑器环境或手动创建容器后需要）
Container->RebuildProxy();

// 获取代理数据，用于传递给音频系统
TSharedPtr<Audio::IProxyData> ProxyData = Container->CreateProxyData(Audio::FProxyDataInitParams());
```

### 进阶用法 (实现自定义的无锁代理数据)

此模式源自 `FCatSoundWaveContainerProxy` 的实现，用于在游戏线程和音频线程之间安全地传递复杂数据。

```cpp
// 来源: CatAudioProxyView.h, CatSoundWaveContainer.h

// 1. 定义你的数据结构
struct FMyAudioConfigData
{
    float Volume;
    TArray<float> CustomCurve;
    // ... 其他音频相关配置
};

// 2. 定义你的代理类，继承 TCatProxyView
class FMyAudioConfigProxy : public Audio::TCatProxyView<FMyAudioConfigProxy, FMyAudioConfigData>
{
public:
    // 使用父类的构造函数
    using Audio::TCatProxyView<FMyAudioConfigProxy, FMyAudioConfigData>::TCatProxyView;

    // 必须实现静态方法
    static FName GetAudioProxyTypeName()
    {
        static FName Name = TEXT("FMyAudioConfigProxy");
        return Name;
    }
    static constexpr bool bWasAudioProxyClassImplemented = true;

    // 实现 QueryInterface，以便通过 IProxyData 接口查询
    virtual void* QueryInterface(const FName InInterfaceId) override
    {
        if (InInterfaceId == GetAudioProxyTypeName())
        {
            return this;
        }
        return IProxyData::QueryInterface(InInterfaceId);
    }
};

// 3. 在拥有数据的游戏线程对象中使用
// 游戏线程：创建并更新代理
TSharedRef<FMyAudioConfigProxy> Proxy = FMyAudioConfigProxy::Create(FMyAudioConfigData{1.0f, {}});
// ... 稍后数据变化时
FMyAudioConfigData NewData{0.5f, {0.0f, 1.0f}};
Proxy = Proxy->New(MoveTemp(NewData));

// 4. 在音频线程安全地读取最新数据
TSharedRef<const FMyAudioConfigProxy> LatestProxy = Proxy->GetLatest();
const FMyAudioConfigData& CurrentData = LatestProxy->GetData();
// 使用 CurrentData.Volume, CurrentData.CustomCurve 等
```

## Demo 示例

一个最小的 C++ 示例，演示如何使用 `UCatSoundWaveContainer`。

**MyWaveContainerDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyWaveContainerDemo.generated.h"

class USoundWave;
class UCatSoundWaveContainer;

UCLASS()
class UMyWaveContainerDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UPROPERTY(BlueprintReadOnly, Category="Demo")
    TObjectPtr<UCatSoundWaveContainer> DemoContainer;
};
```

**MyWaveContainerDemo.cpp**
```cpp
#include "MyWaveContainerDemo.h"
#include "CatSoundWaveContainer.h" // 包含实验性插件的头文件

void UMyWaveContainerDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 创建一个容器对象
    DemoContainer = NewObject<UCatSoundWaveContainer>(this);

    // 假设我们有一个加载好的 USoundWave 指针
    USoundWave* LoadedWave1 = LoadObject<USoundWave>(nullptr, TEXT("/Game/Sounds/Hit01.Hit01"));
    USoundWave* LoadedWave2 = LoadObject<USoundWave>(nullptr, TEXT("/Game/Sounds/Hit02.Hit02"));

    if (LoadedWave1 && LoadedWave2)
    {
        // 配置为随机模式
        DemoContainer->Type = ECatSoundWaveContainerType::Random;
        // 添加两个声音，权重相同
        DemoContainer->Entries.Add(FCatSoundWaveContainerEntry(LoadedWave1));
        DemoContainer->Entries.Add(FCatSoundWaveContainerEntry(LoadedWave2));
        // 重要：手动触发代理重建，使其对音频线程可见
        DemoContainer->RebuildProxy();

        UE_LOG(LogTemp, Log, TEXT("Created a CatSoundWaveContainer with 2 random entries."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。所有列出的模块（`AudioExperimentalRuntime`, `MetasoundExperimentalRuntime`, `MetasoundExperimentalEngineRuntime`, `MetasoundExperimentalEditor`）在其各自的 `.Build.cs` 中仅声明了对 `CoreUObject` 的依赖。但此插件运行依赖于 `Metasound` 插件，使用者的项目需要启用 `Metasound`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 添加实验性通道无关类型（CAT）波形相关功能。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 废弃相关的合并冲突。 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | 添加 CAT 乘法节点。 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | 添加 CAT 阶梯滤波器节点。 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': | 从待处理更改列表中恢复了一组更改。 |

### 维护评价

该插件创建于 2025 年 4 月，距今约 1 年。从 Git 历史看，**维护非常活跃**。在 2026 年 4 月和 5 月有多次密集提交，主要致力于添加“通道无关类型（CAT）”相关的新节点（波形播放器、乘法、滤波器）并进行 API 适配。这表明 Epic 正在积极开发此实验性分支。

- **优点**：功能更新频繁，紧跟 MetaSound 最新研发方向。
- **风险与限制**：
    1.  **实验性**：`IsExperimentalVersion=true`，`EnabledByDefault=false`。API 和功能极不稳定，可能在版本更新中被删除、重命名或彻底改变。
    2.  **依赖项**：依赖主 `Metasound` 插件，两者版本需兼容。
    3.  **文档缺失**：`.uplugin` 中 `DocsURL` 为空，无官方文档。
- **推荐**：仅推荐用于**研究、原型开发或内部工具**。绝对不建议在面向用户的稳定产品中作为核心功能依赖。开发者应有心理准备，此插件中的功能可能会在未来某个引擎版本中被移除或整合进主插件并发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- [官方文档]() (无)
- [测试用例]() (当前分析的模块路径中未发现独立测试文件，测试可能位于主 `Metasound` 插件或 `Engine/Tests` 目录)