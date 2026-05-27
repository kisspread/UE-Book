# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频技术工具 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、视图模型） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 插件旨在为 UE5 的音频系统，特别是 MetaSound，提供一套底层工具和抽象层。其核心解决的问题是：MetaSound 等音频系统内部通常使用线性、规格化的数值（如线性增益、频率倍率）进行计算，但用户界面（UI）上显示和编辑这些数值时，却需要使用更直观、人类可感知的单位（如分贝 dB、半音 Semitones）。这个插件提供了在“内部系统源”和“UI 显示”这两个不同值域之间进行转换、映射和格式化的统一框架，并为此提供了 MVVM（模型-视图-视图模型）模式支持，方便将音频组件状态绑定到 UI 控件。

简而言之，它是 MetaSound 与用户界面之间的“翻译官”和“适配器”。

## 使用场景

- 你正在为自定义的 MetaSound 或音频系统创建用户界面控件（如旋钮、滑块、数字显示框），并希望这些控件以分贝、半音等单位工作，而底层系统使用线性增益和频率倍率。
- 你需要一个标准化的方式来处理音频参数（如音量、音高、时间）在不同表示法（如 dB vs 线性，半音 vs 频率倍数）之间的转换。
- 你希望利用 MVVM 模式，将 `UAudioComponent` 的播放状态（播放中、停止、淡入淡出等）实时绑定到 UI 元素上。
- 你正在开发需要复杂音频参数处理的编辑器工具或运行时界面。

## 蓝图用法

插件的核心是一个参数映射系统和一个视图模型系统。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Audio Component` | 设置视图模型要绑定的音频组件 | `UAudioComponentViewModel` |
| `Source To Display` | 将内部系统的源值转换为 UI 显示值 | `UTechAudioToolsFloatMapping` |
| `Display To Source` | 将 UI 显示值转换回内部系统的源值 | `UTechAudioToolsFloatMapping` |
| `Get Source Min` | 获取映射后源范围的最小值 | `UTechAudioToolsFloatMapping` |
| `Get Display Max` | 获取映射后显示范围的最大值 | `UTechAudioToolsFloatMapping` |
| `Is Playing` | (来自 Viewmodel) 判断音频组件是否正在播放 | `UAudioComponentViewModel` |
| `Is Fading Out` | (来自 Viewmodel) 判断音频组件是否正在淡出 | `UAudioComponentViewModel` |

### 使用示例（蓝图描述）

**1. 音频参数映射（音量旋钮）：**
   - 创建一个 `UTechAudioToolsFloatMapping` 对象。
   - 设置 `MappingType` 为 `Volume`。
   - 配置 `SourceVolumeUnits` 为 `LinearGain`，`DisplayVolumeUnits` 为 `Decibels`。
   - 设置 `Display Range_Decibels` 为 (-60, 6)。
   - 当用户拖动一个滑块（值为 0.0 ~ 1.0）时，首先将其映射到显示范围 (-60, 6) 得到分贝值，然后调用 `Display To Source` 节点，将分贝值转换为线性增益，最后将该值设置给 MetaSound 参数或 `AudioComponent`。

**2. 音频状态绑定（播放按钮）：**
   - 创建一个 `UAudioComponentViewModel` 对象。
   - 调用 `Set Audio Component` 将其绑定到场景中的一个 `AudioComponent`。
   - 在 UI 按钮（如“播放/暂停”按钮）的绑定中，读取 `Is Playing` 属性来决定按钮图标。
   - 在按钮的点击事件中，直接控制对应的 `AudioComponent` 进行播放或停止。

## C++ 用法

### 头文件引入

```cpp
#include "TechAudioTools/TechAudioToolsFloatMapping.h"
#include "TechAudioTools/Viewmodels/AudioComponentViewModel.h"
```

### 基本用法

创建并配置一个浮点数映射对象，用于在源值和显示值之间转换。

```cpp
// 创建映射对象
UTechAudioToolsFloatMapping* VolumeMapping = NewObject<UTechAudioToolsFloatMapping>();

// 配置为音量映射模式，内部使用线性增益，UI显示为分贝
VolumeMapping->MappingType = ETechAudioToolsFloatMappingType::Volume;
VolumeMapping->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
VolumeMapping->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;
VolumeMapping->DisplayRange_Decibels = FFloatInterval(-60.f, 6.f);

// 将UI上的分贝值(-30 dB)转换为内部使用的线性增益值
float DisplayDbValue = -30.0f;
float SourceLinearGain = VolumeMapping->DisplayToSource(DisplayDbValue);
// 结果约等于 0.0316f

// 将内部线性增益值(1.0f)转换为UI显示的分贝值
float SourceLinearValue = 1.0f; // unity gain
float DisplayDbResult = VolumeMapping->SourceToDisplay(SourceLinearValue);
// 结果为 0.0f dB

// 获取显示范围的边界
float MinDisplay = VolumeMapping->GetDisplayMin(); // -60.0f
float MaxDisplay = VolumeMapping->GetDisplayMax(); // 6.0f
```
*(示例基于对 `UTechAudioToolsFloatMapping` 类方法的理解)*

### 进阶用法

使用视图模型监听音频组件状态变化。

```cpp
// 假设我们拥有一个 UAudioComponent 指针 AudioComp
UAudioComponentViewModel* AudioVM = NewObject<UAudioComponentViewModel>();
AudioVM->SetAudioComponent(AudioComp);

// 在某个地方监听状态变化（例如绑定到FieldNotify）
// 通常在UMG Widget的蓝图中通过绑定更简单，C++中可使用 FPropertyDelegate 等机制
// 这里仅展示如何查询状态
if (AudioVM->IsPlaying())
{
    UE_LOG(LogTemp, Log, TEXT("Audio is playing!"));
}
if (AudioVM->IsFadingOut())
{
    UE_LOG(LogTemp, Log, TEXT("Audio is fading out."));
}
```

## Demo 示例

一个最小的 C++ 示例，演示如何使用音频浮点映射。

```cpp
// MyAudioWidget.h
#pragma once
#include "CoreMinimal.h"
#include "TechAudioTools/TechAudioToolsFloatMapping.h"
#include "MyAudioWidget.generated.h"

UCLASS()
class UMyAudioWidget : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Instanced)
    UTechAudioToolsFloatMapping* VolumeMapping;

    UPROPERTY()
    float CurrentDisplayVolumeDb;

    UFUNCTION(BlueprintCallable)
    void Initialize();

    UFUNCTION(BlueprintCallable)
    void OnVolumeSliderChanged(float NewSliderValue); // Slider Value 通常 0-1
};
```

```cpp
// MyAudioWidget.cpp
#include "MyAudioWidget.h"

void UMyAudioWidget::Initialize()
{
    if (!VolumeMapping)
    {
        VolumeMapping = NewObject<UTechAudioToolsFloatMapping>(this);
        VolumeMapping->MappingType = ETechAudioToolsFloatMappingType::Volume;
        VolumeMapping->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
        VolumeMapping->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;
        VolumeMapping->DisplayRange_Decibels = FFloatInterval(-60.f, 6.f);
    }
}

void UMyAudioWidget::OnVolumeSliderChanged(float NewSliderValue)
{
    if (VolumeMapping)
    {
        // 1. 将0-1的滑块值映射到显示范围（-60到6 dB）
        CurrentDisplayVolumeDb = FMath::Lerp(VolumeMapping->GetDisplayMin(), VolumeMapping->GetDisplayMax(), NewSliderValue);

        // 2. 将显示的分贝值转换为源线性增益值
        float LinearGain = VolumeMapping->DisplayToSource(CurrentDisplayVolumeDb);

        // 3. 使用这个线性增益值设置音频参数 (此处为伪代码)
        // SetAudioParameter(LinearGain);

        UE_LOG(LogTemp, Log, TEXT("Slider: %.2f -> dB: %.2f -> Linear: %.4f"), NewSliderValue, CurrentDisplayVolumeDb, LinearGain);
    }
}
```

## 模块依赖

你的项目模块需要添加以下依赖项才能使用此插件的功能。

| 模块 | 用途 |
|---|---|
| `TechAudioTools` | 提供核心的浮点映射 (`UTechAudioToolsFloatMapping`) 和视图模型基类 |
| `Metasound` | 插件声明的硬依赖，用于与 MetaSound 系统集成 |
| `ModelViewViewModel` | 插件声明的硬依赖，用于 `UAudioComponentViewModel` 等 MVVM 功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 MetaSound 引脚类型注册及相关编辑器行为 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回滚导致 CIS 编译错误的提交 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 再次尝试整合 MetaSound 引脚类型注册及编辑器行为 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound 字面量视图模型添加事务支持 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将 DocumentConfiguration 重命名为 MetaSound(Document)Template |

### 维护评价

- **实验性插件**：根据 `.uplugin` 设置（`IsBetaVersion=true`），此插件仍处于实验阶段。
- **活跃开发**：从 git 记录看，在 2026 年 3 月至 4 月期间有密集的更新，主要围绕 MetaSound 集成、编辑器行为优化和新功能（如事务支持）展开，表明其仍在被**积极开发和迭代**。
- **功能演进**：更新内容涉及核心功能重构和编辑器集成，说明 Epic 团队仍在投入资源完善此工具链。
- **推荐使用**：对于需要深度集成 MetaSound 并构建专业音频工具的项目，此插件是官方提供的有价值工具。但由于其**实验性**状态，建议在**测试环境或能够接受 API 变动**的项目中使用，不建议直接用于需要长期稳定的核心生产代码中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [官方文档]() (暂无)
- [测试用例]() (暂未在插件目录内发现明显测试文件)