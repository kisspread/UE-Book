# MotoSynth

> An experimental granular vehicle engine. Intended to explore and demonstrate potential capabilities. Not supported.

| 属性 | 值 |
|---|---|
| 中文名 | 摩托合成 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产类型、编辑器扩展） |
| 模块 | `MotoSynth` (Runtime), `MotoSynthEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MotoSynth) | |

## 用途

MotoSynth 是一个用于实时生成和合成车辆（特别是摩托车）引擎声音的实验性插件。它并非基于录制的音频片段进行播放，而是通过“粒化合成”技术，将极短的音频颗粒（Grains）根据模拟的发动机转速、负载等参数进行动态混合与播放，从而实时生成连续、平滑且可高度定制的引擎音效。

它解决的核心问题是：开发者无需为每个转速、负载组合录制独立的音频文件，也无需依赖复杂的音频映射表，即可在运行时动态生成逼真、可交互的引擎声音。这特别适用于对音效动态范围和响应性要求高的赛车或模拟游戏。

## 使用场景

- 你在开发一款赛车或摩托车模拟游戏，需要引擎声音能够根据玩家的油门输入、转速、档位等参数实时、平滑地变化。
- 你希望引擎声音具有高度的可定制性，能够通过调整合成参数（如颗粒大小、混合比例）来创造不同风格的引擎声，而不是受限于固定的录音素材。
- 你需要一个轻量级的引擎音效解决方案，避免打包大量高保真的音频资源文件。
- 你正在探索游戏音频的程序化生成技术。

## 蓝图用法

`MotoSynth` 运行时模块应提供用于控制引擎音效合成的核心蓝图 API。基于 `MotoSynthEditor` 模块的代码，我们可以推断相关的资产操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMotoSynthSource` | 根据提供的 `USoundWave` 创建一个 `UMotoSynthSource` 资产。 | `FMotoSynthExtension` (Editor) |

### 使用示例（蓝图描述）

1.  **在内容浏览器中创建资产**：在内容浏览器右键，进入 `Sounds > Legacy` 子菜单，选择 `Moto Synth Source` 或 `Moto Synth Preset` 来创建新的合成音源或预设资产。
2.  **从SoundWave创建音源**：选中一个 `SoundWave` 资产，在资产操作菜单或右键菜单中，应能找到由 `FMotoSynthExtension` 注册的扩展选项，用于快速基于该音频文件创建对应的 `MotoSynthSource`。

## C++ 用法

**注意**：以下用法基于提供的编辑器模块代码推断。核心的音频合成功能和蓝图API需要查看 `MotoSynth` 运行时模块的头文件（如 `MotoSynthSource.h`, `MotoSynthPreset.h` 等）。

### 头文件引入

```cpp
// 引入资产定义相关头文件
#include "MotoSynthSourceFactory.h"
// 如果需要操作或创建MotoSynth源资产
#include "MotoSynthSource.h"
```

### 基本用法 (资产工厂与定义)

MotoSynth提供了自定义的资产工厂(`UFactory`)和资产定义(`UAssetDefinition`)，用于在编辑器中创建和管理其特殊资产。
*来源文件: `Private/MotoSynthSourceFactory.h`*

```cpp
// 1. 通过工厂创建新的 MotoSynthSource 资产 (通常由编辑器自动调用)
UFactory* Factory = NewObject<UMotoSynthSourceFactory>();
Factory->StagedSoundWave = SomeSoundWaveAsset; // 可预先关联一个SoundWave
UObject* NewMotoSynthSource = Factory->FactoryCreateNew(
    UMotoSynthSource::StaticClass(),
    InParent,
    TEXT("NewMotoSynthSource"),
    RF_Public | RF_Standalone,
    nullptr,
    GWarn
);

// 2. 通过资产定义获取显示信息
UAssetDefinition_MotoSynthPreset* AssetDef = GetDefault<UAssetDefinition_MotoSynthPreset>();
FText DisplayName = AssetDef->GetAssetDisplayName(); // 返回“Moto Synth Preset”
TSoftClassPtr<UObject> AssetClass = AssetDef->GetAssetClass(); // 返回 UMotoSynthPreset
```

### 进阶用法 (编辑器菜单扩展)

MotoSynth向内容浏览器的右键菜单扩展了功能，允许从SoundWave直接创建音源资产。
*来源文件: `Public/SoundWaveAssetActionExtenderMotoSynth.h`*

```cpp
// 注册扩展菜单项 (通常在模块Startup时自动完成)
FMotoSynthExtension::RegisterMenus();

// 模拟执行“从SoundWave创建MotoSynthSource”的命令
FToolMenuContext Context; // 此Context通常由UI系统填充，包含选中的资产等信息
// 假设Context中包含了我们选中的USoundWave资产
FMotoSynthExtension::ExecuteCreateMotoSynthSource(Context);
```

## Demo 示例

这是一个演示如何在C++中定义一个使用MotoSynth音效组件的Actor的最小示例。
**假设**：`MotoSynth` 运行时模块中提供了 `UMotoSynthAudioComponent` 组件类（需根据实际头文件调整）。

```cpp
// MyMotoSynthActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
// 假设MotoSynth组件头文件路径
#include "MotoSynthAudioComponent.h"
#include "MyMotoSynthActor.generated.h"

UCLASS()
class AMyMotoSynthActor : public AActor
{
    GENERATED_BODY()
    
public:	
    AMyMotoSynthActor();

protected:
    virtual void BeginPlay() override;

public:	
    virtual void Tick(float DeltaTime) override;

    // MotoSynth音频组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    UMotoSynthAudioComponent* MotoSynthAudioComp;

    // 控制油门输入的变量
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio Control")
    float ThrottleInput;
};
```

```cpp
// MyMotoSynthActor.cpp
#include "MyMotoSynthActor.h"

AMyMotoSynthActor::AMyMotoSynthActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建根组件
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));

    // 创建并附加MotoSynth音频组件
    MotoSynthAudioComp = CreateDefaultSubobject<UMotoSynthAudioComponent>(TEXT("MotoSynthAudio"));
    MotoSynthAudioComp->SetupAttachment(RootComponent);

    ThrottleInput = 0.0f;
}

void AMyMotoSynthActor::BeginPlay()
{
    Super::BeginPlay();
    // 启动合成引擎声音
    if (MotoSynthAudioComp)
    {
        MotoSynthAudioComp->Start();
    }
}

void AMyMotoSynthActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 将油门输入映射到音效参数（示例逻辑）
    // 实际参数名和范围取决于MotoSynth组件的API
    if (MotoSynthAudioComp)
    {
        // 假设组件有一个名为SetRPM的蓝图可调用函数
        float SimulatedRPM = FMath::Lerp(800.0f, 12000.0f, ThrottleInput);
        MotoSynthAudioComp->SetRPM(SimulatedRPM);
    }
}
```

## 模块依赖

从 `MotoSynthEditor` 模块的功能（资产工厂、操作扩展）推断其依赖。`MotoSynth` 运行时模块的依赖未在提供信息中，但通常会依赖音频引擎相关模块。

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 为运行时音频合成提供底层支持（推测） |
| `UnrealEd` | 提供编辑器模块基础设施（如资产注册、菜单扩展） |
| `ContentBrowser` | 集成到内容浏览器的资产菜单和操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数导致的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | [内容浏览器] 更新“添加”菜单的音频分类。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 宏迁移至新版 UE_LOGF。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件的 `Base<Plugin>.ini` 配置文件重命名为 `Default<Plugin>.ini`。 |
| 2025-08-28 | `08e89bc9` | fixup ISoundGenerator::GetNextBuffer() implementers (don’t assume zero’d buffer) | 修复 `ISoundGenerator::GetNextBuffer()` 实现中的问题（不再假设传入缓冲区已清零）。 |

### 维护评价

MotoSynth 是一个处于**实验性阶段**的插件，由 Epic Games 创建。从提交历史看，直到 2026 年 5 月仍有维护性更新（如修复警告、适配新的日志系统和文件命名规范），表明其代码仍在 UE 的主分支中被同步和维护。

然而，需要注意：
1.  **实验性状态**：插件明确标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，这意味着它不是官方支持的功能，API 和功能可能在未来版本中发生重大变更或被移除。
2.  **功能范围**：作为实验性插件，其功能可能不完善，文档和支持有限。
3.  **适用性**：适合用于原型开发、技术探索或对引擎声音合成有特定需求的项目。不推荐用于需要高度稳定性和长期支持的正式商业项目中。

**建议**：可以尝试使用和学习其技术思路，但在项目规划中应将其视为“技术验证”而非“生产工具”，并准备好应对潜在的破坏性更新或替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MotoSynth)
- [官方文档]() (无)
- [测试用例]() (未在提供信息中找到，需检查 `Engine/Tests` 目录或插件内是否有 `Tests` 子目录)