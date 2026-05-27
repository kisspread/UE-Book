# TechAudioTools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频技术工具 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 插件提供了一套用于处理音频相关技术细节的工具集，主要解决音频参数在不同表示域（如内部计算域和用户界面显示域）之间的转换和映射问题。它不仅仅是一个简单的工具包，而是构建了一套机制，使得开发者能够轻松地在内部系统（如 MetaSound 图表中使用的线性增益或频率乘数）和用户界面（如使用分贝或半音显示的滑块、旋钮）之间同步和转换数值。此外，它还提供了基于 MVVM 模式的音频组件状态视图模型，便于构建响应式的音频用户界面。

## 使用场景

- **自定义音频参数UI控件**：你在开发音频预设编辑器或游戏内的音频设置界面，需要将一个0-1范围的滑块映射到内部MetaSound的-60dB到6dB的音量范围。
- **MetaSound参数驱动UI**：你希望在UI上显示当前音频参数（如音高、滤波器截止频率）的人类可读单位（如半音、赫兹），而底层MetaSound图表使用不同的内部单位。
- **构建响应式音频UI**：你需要创建一个能够实时显示音频组件播放状态（播放、停止、淡入、淡出）并绑定相关操作的控件。

## 蓝图用法

### 核心节点

**音频参数映射 (`UTechAudioToolsFloatMapping`)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Audio Component` | 设置视图模型要绑定的音频组件。 | `UAudioComponentViewModel` |
| `Get Source Min` | 获取源域（内部系统）范围的最小值。 | `UTechAudioToolsFloatMapping` |
| `Get Source Max` | 获取源域（内部系统）范围的最大值。 | `UTechAudioToolsFloatMapping` |
| `Get Display Min` | 获取显示域（用户界面）范围的最小值。 | `UTechAudioToolsFloatMapping` |
| `Get Display Max` | 获取显示域（用户界面）范围的最大值。 | `UTechAudioToolsFloatMapping` |
| `Source To Display` | 将源域值转换为显示域值。 | `UTechAudioToolsFloatMapping` |
| `Display To Source` | 将显示域值转换为源域值。 | `UTechAudioToolsFloatMapping` |
| `Get Units` | 获取源或显示端点的单位。 | `UTechAudioToolsFloatMapping` |

**音频组件视图模型 (`UAudioComponentViewModel`)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Playing` | (只读属性) 音频组件是否正在播放。 | `UAudioComponentViewModel` |
| `Is Stopped` | (只读属性) 音频组件是否已停止。 | `UAudioComponentViewModel` |
| `Is Fading In` | (只读属性) 音频组件是否正在淡入。 | `UAudioComponentViewModel` |
| `Is Fading Out` | (只读属性) 音频组件是否正在淡出。 | `UAudioComponentViewModel` |
| `Get Play State` | (只读属性) 获取音频组件的枚举播放状态。 | `UAudioComponentViewModel` |

### 使用示例（蓝图描述）

1.  **音量滑块映射**：
    *   创建一个 `UTechAudioToolsFloatMapping` 类的实例（例如作为 Widget 或 Actor 的子对象）。
    *   将其 `MappingType` 属性设置为 `Volume`。
    *   配置 `SourceVolumeUnits` (内部单位，如 `LinearGain`) 和 `DisplayVolumeUnits` (显示单位，如 `Decibels`)。
    *   设置 `DisplayRange_Decibels` (例如 `{-60, 6}`) 来定义UI滑块的范围。
    *   在滑块的 `OnValueChanged` 事件中，调用 `Display To Source` 节点，将滑块的当前值（分贝）转换为线性增益值，然后将其设置为目标 `Audio Component` 或 `MetaSound` 参数。

2.  **音频状态绑定**：
    *   在 Widget 蓝图中，创建一个 `UAudioComponentViewModel` 类型的变量。
    *   在初始化时，调用 `Set Audio Component` 节点，传入场景中的 `Audio Component` 引用。
    *   将 Widget 中的状态指示器（如图标或文本）绑定到视图模型的 `IsPlaying`、`IsStopped` 等属性上。这些属性使用了 `FieldNotify`，当音频组件状态改变时，UI会自动更新。

## C++ 用法

### 头文件引入

```cpp
#include "TechAudioToolsFloatMapping.h"
#include "TechAudioToolsTypes.h"
#include "Viewmodels/AudioComponentViewModel.h"
```

### 基本用法

1.  **创建并配置浮点映射对象** (参考 `UTechAudioToolsFloatMapping.h` 逻辑):
    ```cpp
    // 创建一个音量映射对象实例
    UTechAudioToolsFloatMapping* VolumeMapping = NewObject<UTechAudioToolsFloatMapping>();
    
    // 配置为音量映射模式
    VolumeMapping->MappingType = ETechAudioToolsFloatMappingType::Volume;
    VolumeMapping->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
    VolumeMapping->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;
    VolumeMapping->DisplayRange_Decibels = FFloatInterval(-60.0f, 6.0f);
    
    // 使用映射进行转换
    float InternalGain = 0.5f; // 内部系统使用的线性增益
    float DisplayDB = VolumeMapping->SourceToDisplay(InternalGain); // 转换为分贝值用于UI显示
    
    float UserDB = -12.0f; // 用户通过UI滑块输入的分贝值
    float GainForSystem = VolumeMapping->DisplayToSource(UserDB); // 转换回线性增益用于内部系统
    ```

2.  **绑定音频组件到视图模型** (参考 `UAudioComponentViewModel.h`):
    ```cpp
    // 创建一个音频组件视图模型实例
    UAudioComponentViewModel* AudioVM = NewObject<UAudioComponentViewModel>();
    
    // 绑定到场景中的一个 AudioComponent
    UAudioComponent* MyAudioComp = /* 从 Actor 获取 */;
    AudioVM->SetAudioComponent(MyAudioComp);
    
    // 现在可以通过 AudioVM 查询状态
    if (AudioVM->IsPlaying())
    {
        UE_LOG(LogTemp, Log, TEXT("音频正在播放"));
    }
    ```

### 进阶用法

结合映射和视图模型，构建一个完整的音频参数编辑器控件逻辑：

```cpp
// 假设我们正在为一个音频参数（如音高）构建一个自定义编辑器控件
UTechAudioToolsFloatMapping* PitchMapping = NewObject<UTechAudioToolsFloatMapping>();
PitchMapping->MappingType = ETechAudioToolsFloatMappingType::Pitch;
PitchMapping->SourcePitchUnits = ETechAudioToolsPitchUnit::FrequencyMultiplier;
PitchMapping->DisplayPitchUnits = ETechAudioToolsPitchUnit::Semitones;
PitchMapping->DisplayRange_Semitones = FFloatInterval(-24.0f, 24.0f);

// 同时，我们有一个视图模型来跟踪音频组件的状态，以便在UI上显示播放/停止状态
UAudioComponentViewModel* StateVM = NewObject<UAudioComponentViewModel>();
StateVM->SetAudioComponent(TargetAudioComponent);

// 在UI更新逻辑中
void SMyAudioParamWidget::UpdateUI()
{
    // 从模型获取内部值 (例如从 MetaSound 节点)
    float CurrentFrequencyMultiplier = GetParameterValueFromModel();
    
    // 转换为UI显示值
    float DisplaySemitones = PitchMapping->SourceToDisplay(CurrentFrequencyMultiplier);
    // 更新 UI 滑块的显示值为 DisplaySemitones
    
    // 同时，根据视图模型状态更新播放/停止按钮的图标
    PlayStopButton->SetIsEnabled(!StateVM->IsStopped());
}
```

## Demo 示例

一个展示音量映射和状态绑定的最小示例组件。

### MyAudioParamWidget.h
```cpp
// MyAudioParamWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Components/Widget.h"
#include "TechAudioToolsFloatMapping.h"
#include "Viewmodels/AudioComponentViewModel.h"
#include "MyAudioParamWidget.generated.h"

class UAudioComponent;
class UTextBlock;
class UButton;

UCLASS()
class UMyAudioParamWidget : public UWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category="Audio")
    TWeakObjectPtr<UAudioComponent> AudioComponent;

protected:
    UPROPERTY()
    TObjectPtr<UTechAudioToolsFloatMapping> VolumeMapping;
    
    UPROPERTY()
    TObjectPtr<UAudioComponentViewModel> AudioViewModel;

    virtual void NativeConstruct() override;
    
    UFUNCTION()
    void OnVolumeSliderChanged(float Value);
    
    UFUNCTION()
    void OnPlayStopButtonClicked();
};
```

### MyAudioParamWidget.cpp
```cpp
// MyAudioParamWidget.cpp
#include "MyAudioParamWidget.h"
#include "Components/AudioComponent.h"
#include "Components/TextBlock.h"
#include "Components/Button.h"

void UMyAudioParamWidget::NativeConstruct()
{
    Super::NativeConstruct();
    
    // 初始化映射对象 (假设在蓝图中已配置)
    if (!VolumeMapping)
    {
        VolumeMapping = NewObject<UTechAudioToolsFloatMapping>(this);
        VolumeMapping->MappingType = ETechAudioToolsFloatMappingType::Volume;
        VolumeMapping->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
        VolumeMapping->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;
        VolumeMapping->DisplayRange_Decibels = FFloatInterval(-60.0f, 6.0f);
    }
    
    // 初始化视图模型
    AudioViewModel = NewObject<UAudioComponentViewModel>(this);
    if (AudioComponent.IsValid())
    {
        AudioViewModel->SetAudioComponent(AudioComponent.Get());
    }
    
    // 绑定滑块和按钮事件 (假设这些控件在蓝图中已创建并引用)
    // VolumeSlider->OnValueChanged.AddDynamic(this, &UMyAudioParamWidget::OnVolumeSliderChanged);
    // PlayStopButton->OnClicked.AddDynamic(this, &UMyAudioParamWidget::OnPlayStopButtonClicked);
    
    // 初始更新UI状态
    // StatusText->SetText(AudioViewModel->IsPlaying() ? FText::FromString("Playing") : FText::FromString("Stopped"));
}

void UMyAudioParamWidget::OnVolumeSliderChanged(float Value)
{
    // Value 是滑块当前值 (例如范围 0-1 或映射后的分贝值)
    // 将其转换为内部线性增益
    float LinearGain = VolumeMapping->DisplayToSource(Value);
    
    // 应用到音频组件
    if (AudioComponent.IsValid())
    {
        AudioComponent->SetVolumeMultiplier(LinearGain);
    }
}

void UMyAudioParamWidget::OnPlayStopButtonClicked()
{
    if (AudioComponent.IsValid())
    {
        if (AudioViewModel->IsPlaying())
        {
            AudioComponent->Stop();
        }
        else
        {
            AudioComponent->Play();
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Metasound` | 核心插件依赖，用于 MetaSound 框架集成和功能。 |
| `ModelViewViewModel` | 核心插件依赖，提供 MVVM 框架（`UMVVMViewModelBase`），用于 `AudioComponentViewModel`。 |
| `TechAudioToolsMetaSound` | 本插件的子模块，提供与 MetaSound 相关的特定工具和类型。 |
| `TechAudioToolsMetaSoundEditor` | 本插件的子模块，提供 MetaSound 编辑器扩展（仅在编辑器中可用）。 |

**注意**：使用 `TechAudioTools` 基础模块时，你需要确保你的 `Build.cs` 文件依赖于 `TechAudioTools` 和 `ModelViewViewModel`。如果使用 MetaSound 相关功能，则需要额外依赖 `Metasound` 和相应的 `TechAudioToolsMetaSound*` 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合了MetaSound引脚类型注册及相关的编辑器行为。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退了导致CIS编译错误的更改。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合了MetaSound引脚类型注册及相关的编辑器行为。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为MetaSound Literal视图模型添加了事务支持。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将“DocumentConfiguration”重命名为“MetaSound(Document)Template”。 |

### 维护评价

该插件创建于 2025 年 4 月，年龄约 1 年，属于较新的插件。
从最近的 git 历史来看，**维护非常活跃**。最近几个月的更新集中在 MetaSound 引脚集成、编辑器行为优化和功能增强（如事务支持）上，表明 Epic 正在持续开发和改进此插件。
由于它被标记为 **实验性** (`IsExperimentalVersion=true`) 和 **测试版** (`IsBetaVersion=true`)，API 和功能在未来可能会发生变化。
总体而言，**推荐关注和试用**，尤其适合需要处理复杂音频参数映射和构建音频相关 UI 的项目。但请注意其实验性状态，不建议在生产关键项目中未经充分测试就深度依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools/Tests) (如果存在)