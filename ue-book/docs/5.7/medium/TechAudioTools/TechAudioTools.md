# TechAudioTools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、音频工具内容） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 提供了一套用于音频参数转换和界面绑定的基础设施。它主要解决两个问题：

1. **音频浮点映射**：在内部系统（如 MetaSound）使用的线性/物理值与用户界面（UI）显示的直观单位（如分贝、半音、赫兹、百分比等）之间进行自动转换和线性映射。避免手动编写转换逻辑。
2. **音频组件状态绑定**：提供了一个基于 MVVM（Model-View-ViewModel）模式的 ViewModel，方便在 UMG 或 Slate 中实时监听 AudioComponent 的播放状态（播放/停止/淡化/虚拟化等），无需手动轮询。

该插件目前处于实验性阶段，主要面向音频工具开发者和 MetaSound 预设编辑器的界面构建。

## 使用场景

- **开发 MetaSound 预设编辑器**：需要将 MetaSound 内部的线性增益值显示为分贝滑块，或频率乘数显示为半音控件。
- **制作音频调试工具**：快速将 AudioComponent 的状态绑定到 UI 元素（如播放指示灯、波形监视器）。
- **用 MVVM 方式管理音频 UI**：避免手动监听音频组件事件，利用 FieldNotify 实现响应式 UI。

## 蓝图用法

本插件主要提供 UObject 和 ViewModel 类，可在蓝图中创建实例或作为变量类型使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Audio Component` | 设置 ViewModel 绑定的 UAudioComponent 实例。调用后自动监听状态变化。 | `UAudioComponentViewModel` |
| `Get Play State` | 返回音频组件的播放状态（Playing/Stopped/FadingIn/FadingOut等）。 | `UAudioComponentViewModel` |
| `Is Playing` | 判断当前是否正在播放。 | `UAudioComponentViewModel` |
| `Is Stopped` | 判断当前是否停止。 | `UAudioComponentViewModel` |
| `Is Fading In` | 判断是否正在淡入。 | `UAudioComponentViewModel` |
| `Is Fading Out` | 判断是否正在淡出。 | `UAudioComponentViewModel` |
| `Is Virtualized` | 判断音频组件是否已虚拟化（超出范围播放）。 | `UAudioComponentViewModel` |

### 使用示例（蓝图描述）

1. **在 UMG 中显示音频播放状态**：
   - 在蓝图控件中创建一个 `AudioComponentViewModel` 变量。
   - 在 BeginPlay 中，使用 `Set Audio Component` 将一个已有的 AudioComponent 赋值给它。
   - 将一个 Image 的 Visibility 绑定到 ViewModel 的 `Is Playing` 属性（通过 FieldNotify 自动变量绑定）。
   - 当音频开始播放时，Image 自动可见；停止时自动隐藏。

2. **制作音量映射滑块**：
   - 创建一个 `UTechAudioToolsFloatMapping` 对象（在蓝图类中作为实例变量）。
   - 设置 `MappingType` 为 `Volume`，`SourceVolumeUnits` 为 `LinearGain`，`DisplayVolumeUnits` 为 `Decibels`。
   - 在 UI 滑块的值变化事件中，调用 `TechAudioTools::ConvertUnit`（C++ 函数，蓝图暂不直接暴露）或手动使用内置映射逻辑。
   - 注意：当前版本中 `ConvertUnit` 和 `ConvertRange` 为 `FORCEINLINE` 命名空间函数，**未标记为 BlueprintCallable**，蓝图无法直接使用。映射逻辑主要在 C++ 端。

## C++ 用法

### 头文件引入

```cpp
#include "TechAudioToolsFloatMapping.h"
#include "Viewmodels/AudioComponentViewModel.h"
#include "TechAudioToolsTypes.h"
```

### 基本用法

**使用浮点映射（C++）**：
```cpp
// TechAudioTools/Source/TechAudioTools/Public/TechAudioToolsFloatMapping.h

// 线性增益转分贝
float LinearGain = 0.5f;
float Decibels = TechAudioTools::ConvertUnit(
    ETechAudioToolsVolumeUnit::LinearGain,
    ETechAudioToolsVolumeUnit::Decibels,
    LinearGain
); // 约 -6.02 dB

// 半音转频率乘数
float Semitones = 12.f;
float FreqMultiplier = TechAudioTools::ConvertUnit(
    ETechAudioToolsPitchUnit::Semitones,
    ETechAudioToolsPitchUnit::FrequencyMultiplier,
    Semitones
); // 2.0 (一个八度)

// 转换整个范围
FFloatInterval SourceRange(0.0f, 1.0f);
FFloatInterval DBRange = TechAudioTools::ConvertRange(
    ETechAudioToolsVolumeUnit::LinearGain,
    ETechAudioToolsVolumeUnit::Decibels,
    SourceRange
); // 注意：分贝范围是负无穷到0，此处会反转
```

**使用 AudioComponentViewModel**：
```cpp
// 头文件
#include "Viewmodels/AudioComponentViewModel.h"

// 在 Actor 或 Widget 中
UAudioComponentViewModel* ViewModel = NewObject<UAudioComponentViewModel>();
ViewModel->SetAudioComponent(MyAudioComponent); // 开始监听

// 后续可通过 ViewModel->IsPlaying(), GetPlayState() 等获取状态
// 也可以在 UMG 中通过 MVVM 绑定属性（自动更新）
```

**创建 FloatMapping 对象**：
```cpp
// 用来描述一个滑块的范围和单位
UTechAudioToolsFloatMapping* Mapping = NewObject<UTechAudioToolsFloatMapping>();
Mapping->MappingType = ETechAudioToolsFloatMappingType::Volume;
Mapping->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
Mapping->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;
// 设置 SourceRange/DisplayRange 后可以在编辑器细节面板中预览
```

### 进阶用法

**自定义映射逻辑**：
如果需要将内部线性增益映射到自定义 UI 范围（例如 -60 dB ~ 12 dB），可以组合使用 `ConvertRange` 和 `FMath::GetMappedRangeValueUnclamped`：

```cpp
// 伪代码，当前插件未直接提供线性重映射+单位转换的复合函数
float InternalValue = 0.3f; // 线性增益
float DBValue = TechAudioTools::ConvertUnit(
    ETechAudioToolsVolumeUnit::LinearGain,
    ETechAudioToolsVolumeUnit::Decibels,
    InternalValue
); // 约 -10.46 dB

// 如果需要将 dB 值映射到 UI 滑块位置（0-1），需要自行处理
```

**响应 AudioComponent 虚拟化事件**：
ViewModel 自动绑定 `OnAudioVirtualizationChanged` 委托，可在子类中重写 `OnVirtualizationChanged` 以自定义行为。

## Demo 示例

以下是一个最小 C++ 示例，展示如何在 Actor 中使用 AudioComponentViewModel 和浮点映射。

**MyAudioToolActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/AudioComponent.h"
#include "Viewmodels/AudioComponentViewModel.h"
#include "TechAudioToolsFloatMapping.h"
#include "MyAudioToolActor.generated.h"

UCLASS()
class AMyAudioToolActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    UAudioComponent* AudioComponent;

    UPROPERTY()
    UAudioComponentViewModel* AudioViewModel;

    UPROPERTY()
    UTechAudioToolsFloatMapping* VolumeMapping;
};
```

**MyAudioToolActor.cpp**
```cpp
#include "MyAudioToolActor.h"

void AMyAudioToolActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建 AudioComponent（假设在构造函数中已设置 Sound）
    AudioComponent = NewObject<UAudioComponent>(this);
    AudioComponent->RegisterComponent();

    // 创建 ViewModel 并绑定
    AudioViewModel = NewObject<UAudioComponentViewModel>(this);
    AudioViewModel->SetAudioComponent(AudioComponent);

    // 创建音量映射（内部线性增益 → UI 分贝）
    VolumeMapping = NewObject<UTechAudioToolsFloatMapping>(this);
    VolumeMapping->MappingType = ETechAudioToolsFloatMappingType::Volume;
    VolumeMapping->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
    VolumeMapping->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;

    // 启动播放
    AudioComponent->Play();

    // 通过 ViewModel 检查状态
    if (AudioViewModel->IsPlaying())
    {
        UE_LOG(LogTemp, Log, TEXT("Audio is playing"));
    }
}
```

## 模块依赖

根据各模块 Build.cs 和 `.uplugin` 可知，本插件依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Metasound` | 提供 MetaSound 节点与运行时支持 |
| `ModelViewViewModel` | 提供 MVVM ViewModel 基类及 FieldNotify 支持 |
| `AudioExtensions` | 音频扩展接口（如虚拟化事件） |
| `SignalProcessing` | 提供 `Audio::ConvertToDecibels`、`ConvertToLinear`、`GetSemitones`、`GetFrequencyMultiplier` 等 DSP 函数 |

**注意**：`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UMG`, `InputCore` 等常见依赖省略。

## 维护状态

### 近期更新

- 2025-09-29 `e2b39300` — Remove clamp when converting between source and display values while using Default mapping
- 2025-09-03 `085d445f` — added BandwidthOct and Tempo as new float unit types for label formatting
- 2025-09-03 `a5101638` — Added AudioComponentViewModel
- 2025-09-03 `13481976` — fixed documentation errors
- 2025-09-02 `8eab906f` — added viewmodel classes for each MetaSound literal type

### 维护评价

该插件创建于 2025 年 9 月，至今仅约 1 个月，属于**非常早期的实验性插件**。从提交记录看，更新集中在功能添加和修复，最近一周还有更新，表明处于**活跃开发阶段**。但由于实验性标签且版本号仅为 1.0，API 可能不稳定，不适合用于生产项目。建议仅在开发或原型中使用，并密切关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TechAudioTools)
- [官方文档](https://docs.unrealengine.com)（当前插件无独立文档页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TechAudioTools/Tests)（可能存在，但当前未提供）