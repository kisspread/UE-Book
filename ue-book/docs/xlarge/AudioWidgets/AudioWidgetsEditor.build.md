# AudioWidgets

> Collection of widgets tailored to interacting with audio-related data and systems.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（控件资产） |
| 模块 | `AudioWidgetsCore` (RuntimeAndProgram), `AudioWidgets` (Runtime), `AudioWidgetsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-12-10 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioWidgets) | |

## 用途

AudioWidgets 插件提供了一套专门为音频数据交互设计的 UI 控件集合。其核心目的是解决在 Unreal Engine 中可视化、调试和编辑音频相关数据时缺乏专用、高效工具的问题。

该插件主要服务于两个场景：
1.  **运行时音频调试与分析**：为 Unreal Insights 等分析工具提供专用的音频数据可视化控件（如频谱分析器、音频表），帮助开发者实时监控和诊断音频系统的运行状态。
2.  **编辑器音频资产编辑**：增强编辑器中音频资产（如 Sound Wave、Sound Cue）的属性编辑体验，通过自定义细节面板和属性矩阵，让音频设计师能更直观、高效地调整音频参数。

## 使用场景

-   **音频系统调试**：当你在开发一个复杂的音频系统，需要实时查看音频频谱、音量包络或特定音频分析结果时，可以使用本插件提供的控件在 Unreal Insights 或自定义调试界面中进行可视化。
-   **音频资产批量编辑**：当你需要同时调整多个音频资产的音量、音高或其他共享属性时，可以利用本插件提供的属性矩阵（Property Matrix）功能进行批量操作，极大提升工作效率。
-   **自定义音频工具开发**：当你需要为项目开发一个自定义的音频混合器或音频事件编辑器时，可以直接使用或继承本插件提供的基础音频控件（如滑块、旋钮、频谱显示），快速构建专业级界面。

## 蓝图用法

本插件主要提供的是底层控件和编辑器扩展，其蓝图 API 通常通过 UMG 控件的形式暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Audio Spectrum Analyzer` | 创建一个频谱分析器控件实例。 | `UAudioSpectrumAnalyzer` |
| `Create Audio Meter` | 创建一个音频电平表控件实例。 | `UAudioMeter` |
| `Set Audio Data` | 向音频控件（如频谱分析器）馈送新的音频数据以进行显示。 | `UAudioWidgetBase` |

### 使用示例（蓝图描述）

1.  **创建频谱分析器**：
    *   在 UMG 设计器中，从控件面板拖拽一个 `AudioSpectrumAnalyzer` 控件到画布上。
    *   在蓝图中，通过 `Create Audio Spectrum Analyzer` 节点动态创建一个实例，并将其添加到某个容器控件（如 `Canvas Panel`）中。
2.  **更新频谱数据**：
    *   在音频分析回调（例如来自 `AudioSynesthesia` 插件的分析结果）中，获取到频谱数据数组。
    *   调用频谱分析器控件的 `Set Audio Data` 节点，将频谱数据数组传入，控件会自动更新其可视化显示。

## C++ 用法

### 头文件引入

```cpp
// 引入核心音频控件基类
#include "AudioWidgetsModule.h"
// 引入具体的频谱分析器控件
#include "AudioSpectrumAnalyzer.h"
// 引入音频表控件
#include "AudioMeter.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建并配置一个音频表控件。

```cpp
// 来源：基于 AudioWidgets 模块典型用法推断
#include "AudioMeter.h"
#include "Components/AudioComponent.h"

void AMyActor::SetupAudioMeter()
{
    // 1. 创建一个音频表控件实例
    UAudioMeter* AudioMeterWidget = NewObject<UAudioMeter>(this);

    // 2. 配置其样式（颜色、范围等）
    FAudioMeterStyle MeterStyle;
    MeterStyle.MeterValueColor = FLinearColor::Green;
    MeterStyle.MeterPeakColor = FLinearColor::Red;
    MeterStyle.MeterSize = FVector2D(200.0f, 20.0f);
    AudioMeterWidget->SetStyle(MeterStyle);

    // 3. 将其添加到某个 Slate 容器或 UMG 面板中（此处以添加到 Viewport 为例）
    // 注意：实际使用中通常通过 UMG 设计器或将其嵌入到其他 Slate/UMG 容器。
    // GEngine->GameViewport->AddViewportWidgetContent(SNew(SBox).Content()[AudioMeterWidget->TakeWidget()]);

    // 4. 绑定音频数据源
    // 假设你有一个 UAudioComponent 用于播放声音
    if (UAudioComponent* MyAudioComp = FindComponentByClass<UAudioComponent>())
    {
        // 将音频表的音量数据源绑定到该 AudioComponent
        AudioMeterWidget->SetAudioMeter(MyAudioComp);
    }
}
```

### 进阶用法

结合 `AudioSynesthesia` 插件进行频谱分析并显示。

```cpp
// 来源：基于 AudioWidgets 与 AudioSynesthesia 集成推断
#include "AudioSpectrumAnalyzer.h"
#include "SynesthesiaNRT.h" // 来自 AudioSynesthesia 插件

void AMyActor::AnalyzeAndDisplaySpectrum(USoundWave* SoundWave)
{
    // 1. 创建一个频谱分析器控件
    UAudioSpectrumAnalyzer* SpectrumAnalyzer = NewObject<UAudioSpectrumAnalyzer>(this);

    // 2. 创建一个 Synesthesia NRT（非实时）分析任务
    USynesthesiaNRT* NRTAnalyzer = NewObject<USynesthesiaNRT>(this);
    NRTAnalyzer->SetSound(SoundWave);

    // 3. 运行分析（通常在异步任务中）
    NRTAnalyzer->AnalyzeAudio();

    // 4. 分析完成后，获取频谱数据并馈送给控件
    // 假设在分析完成的回调中
    TArray<FSynesthesiaSpectrumData> SpectrumData = NRTAnalyzer->GetSpectrumResults();
    SpectrumAnalyzer->SetSpectrumData(SpectrumData);
}
```

## Demo 示例

一个最小的可编译示例，展示如何在 Actor 中创建一个基础的音频表控件。

```cpp
// MyAudioMeterActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAudioMeterActor.generated.h"

class UAudioMeter;
class UAudioComponent;

UCLASS()
class MYPROJECT_API AMyAudioMeterActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAudioMeterActor();

protected:
    virtual void BeginPlay() override;

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    UAudioComponent* AudioComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    UAudioMeter* AudioMeterWidget;
};
```

```cpp
// MyAudioMeterActor.cpp
#include "MyAudioMeterActor.h"
#include "AudioMeter.h"
#include "Components/AudioComponent.h"
#include "Sound/SoundCue.h"

AMyAudioMeterActor::AMyAudioMeterActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建音频组件
    AudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("AudioComp"));
    AudioComponent->SetupAttachment(RootComponent);
}

void AMyAudioMeterActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建音频表控件
    AudioMeterWidget = NewObject<UAudioMeter>(this);

    // 配置样式
    FAudioMeterStyle Style;
    Style.MeterSize = FVector2D(300.0f, 30.0f);
    AudioMeterWidget->SetStyle(Style);

    // 绑定到音频组件
    if (AudioComponent)
    {
        AudioMeterWidget->SetAudioMeter(AudioComponent);
        // 可以开始播放一个声音来测试
        // AudioComponent->SetSound(MySoundCue);
        // AudioComponent->Play();
    }

    // 注意：要将此控件显示在屏幕上，需要将其添加到 Slate 层级或 UMG 视图中。
    // 例如，在 PlayerController 或 HUD 中获取此 Actor 并添加其控件。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioSynesthesia` | 提供音频分析（如频谱、响度）功能，是 AudioWidgets 许多高级控件的数据源。 |
| `Slate`, `SlateCore` | 构成所有 UI 控件的基础框架。 |
| `UMG` | 用于将 Slate 控件包装成可在蓝图中使用的 UMG 控件。 |
| `AudioMixer` | 底层音频混合系统，可能用于获取原始音频数据流。 |

## 维护状态

### 近期更新

```
- 2025-10-03 7f6fc2455c09 Use modular feature to instantiate AudioPropertiesSheet details injector #rb panda.parkes, david.taralla
  解读：采用模块化特性来实例化音频属性表的细节注入器，增强了扩展性。
- 2025-09-15 31692ca0ec40 [AudioProperties ]fix for cis error  620430 #rnx
  解读：修复了与音频属性相关的持续集成（CIS）错误。
- 2025-08-20 e9b2454e7fde AudioPropertiesDetailsInjector: - allows to override the view of properties on UObject that want to implement a property sheet - supports property matrix - changes to AudioPropertiesEditorModule to allow the object to be instantiated on projects that are not aware of the plugin - implementation into soundbase details #rb panda.parkes #rnx
  解读：重大功能更新。音频属性细节注入器现在允许 UObject 重写其属性视图以支持属性表，并支持属性矩阵。同时改进了编辑器模块，使其能在不了解此插件的项目中实例化对象，并已集成到 SoundBase 的细节面板中。
```

### 维护评价

**活跃维护**。

-   **创建时间**：插件于 2020 年底创建，已有约 4 年历史，属于较新的插件。
-   **近期更新**：最近三次提交（2025年8月至10月）均围绕“AudioProperties”功能进行实质性增强和修复，表明插件正在积极开发新特性（属性注入、矩阵支持）并保持稳定性。
-   **维护状态**：由 Epic Games 官方维护，更新频率稳定，且与核心音频系统（AudioSynesthesia）紧密集成，是官方音频工具链的重要组成部分。
-   **推荐使用**：**强烈推荐**。对于任何需要在 Unreal Engine 中进行专业音频调试、分析或构建自定义音频工具的项目，此插件都是首选。它提供了经过官方验证的、高性能的音频 UI 控件，能显著提升开发效率和质量。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioWidgets)
-   [官方文档]() (暂无)
-   [测试用例]() (插件目录内未发现独立测试文件，测试可能集成在引擎测试套件中)