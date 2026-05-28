# TechAudioTools

> A collection of audio-related tools and utilities.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音频技术工具 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 插件旨在为音频工具开发提供底层支持，特别是围绕 **MetaSound** 生态。它主要解决两个核心问题：
1.  **数值域映射与转换**：在音频系统（如 MetaSound）内部使用的数值域（如线性增益、频率乘数）与用户界面（UI）或预设控件中显示的域（如分贝、半音）之间进行精确、非线性的转换。这允许开发者创建直观的音频参数控件，而无需在内部逻辑和UI显示之间手动编写复杂的转换代码。
2.  **MVVM 状态绑定**：提供 ViewModel 层，用于将 `UAudioComponent` 的实时播放状态（播放、停止、淡入、淡出等）与 UI 控件（如 UMG）进行数据绑定，简化音频状态可视化工具的开发。

## 使用场景

-   你正在开发一个自定义的 MetaSound 预设或参数编辑器，并希望用分贝滑块控制内部的线性增益参数。
-   你需要在游戏 UI 或编辑器工具中实时显示 `UAudioComponent` 的播放状态（播放、停止、虚拟化等）。
-   你在构建音频相关的编辑器工具，需要一套标准化的音频单位转换和映射逻辑。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SourceToDisplay` | 将源域值转换为显示域值 | `UTechAudioToolsFloatMapping` |
| `DisplayToSource` | 将显示域值转换为源域值 | `UTechAudioToolsFloatMapping` |
| `NormalizedToSource` | 将 [0,1] 归一化值转换为源域值 | `UTechAudioToolsFloatMapping` |
| `SourceToNormalized` | 将源域值转换为 [0,1] 归一化值 | `UTechAudioToolsFloatMapping` |
| `NormalizedToDisplay` | 将 [0,1] 归一化值转换为显示域值 | `UTechAudioToolsFloatMapping` |
| `DisplayToNormalized` | 将显示域值转换为 [0,1] 归一化值 | `UTechAudioToolsFloatMapping` |
| `GetSourceMin` / `GetSourceMax` | 获取源域范围的最小/最大值 | `UTechAudioToolsFloatMapping` |
| `GetDisplayMin` / `GetDisplayMax` | 获取显示域范围的最小/最大值 | `UTechAudioToolsFloatMapping` |
| `GetUnits` | 获取指定端点（源或显示）使用的单位 | `UTechAudioToolsFloatMapping` |
| `SetAudioComponent` | 设置此 ViewModel 要绑定的音频组件 | `UAudioComponentViewModel` |
| `GetPlayState` | 获取音频组件的枚举播放状态 | `UAudioComponentViewModel` |
| `IsPlaying` / `IsStopped` 等 | 查询音频组件是否处于特定状态（布尔值） | `UAudioComponentViewModel` |

### 使用示例（蓝图描述）

1.  **音量映射**：创建一个 `UTechAudioToolsFloatMapping` 对象。在细节面板中，将 `MappingType` 设置为 `Volume`。设置 `SourceVolumeUnits` 为 `LinearGain`，`DisplayVolumeUnits` 为 `Decibels`，并调整 `DisplayRange_Decibels` 为 `-60` 到 `6`。在 UI 中，将滑块（范围 0-100）的值通过 `NormalizedToDisplay` 节点转换为分贝值，再通过 `DisplayToSource` 转换为线性增益，最后传递给 MetaSound 的输入。
2.  **播放状态绑定**：在 UMG Widget 的 ViewModel 设置中，选择 `UAudioComponentViewModel`。在蓝图中，调用 `SetAudioComponent` 绑定目标组件。然后，可以直接将 Widget 的文本属性（如可见性、文本内容）绑定到 `IsPlaying`、`PlayState` 等 Field Notify 属性上，实现状态自动更新。

## C++ 用法

### 头文件引入

```cpp
#include "TechAudioToolsFloatMapping.h"
#include "Viewmodels/AudioComponentViewModel.h"
```

### 基本用法

**创建和使用浮点映射器**
```cpp
// 创建一个用于音量映射的映射器实例
UTechAudioToolsFloatMapping* VolumeMapper = NewObject<UTechAudioToolsFloatMapping>();
VolumeMapper->MappingType = ETechAudioToolsFloatMappingType::Volume;
VolumeMapper->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
VolumeMapper->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;
VolumeMapper->DisplayRange_Decibels = FFloatInterval(-60.f, 6.f);

// 在 UI 或预设系统中，将显示值（如滑块输入的 -24.f dB）转换为源值（线性增益）
float DisplayValue_dB = -24.f;
float SourceValue_Linear = VolumeMapper->DisplayToSource(DisplayValue_dB);

// 也可以进行归一化转换，便于通用 UI 控件（如 0-1 滑块）操作
float NormalizedValue = 0.5f; // 滑块在中间位置
float SourceValue = VolumeMapper->NormalizedToSource(NormalizedValue);
```

**绑定音频组件视图模型**
```cpp
// 获取或创建视图模型实例
UAudioComponentViewModel* ViewModel = NewObject<UAudioComponentViewModel>();

// 绑定到目标音频组件
UAudioComponent* MyComponent = GetMyAudioComponent();
if (MyComponent)
{
    ViewModel->SetAudioComponent(MyComponent);
}

// 查询状态（例如，在 Tick 或响应式更新中）
if (ViewModel->IsPlaying())
{
    // 更新 UI 显示为“正在播放”
}
EAudioComponentPlayState CurrentState = ViewModel->GetPlayState();
```

## Demo 示例

**音频工具 Widget 头文件 (MyAudioToolWidget.h)**
```cpp
// MyAudioToolWidget.h
#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "MyAudioToolWidget.generated.h"

class UTechAudioToolsFloatMapping;
class UAudioComponent;
class UAudioComponentViewModel;

UCLASS()
class UMyAudioToolWidget : public UUserWidget
{
    GENERATED_BODY()

protected:
    virtual void NativeConstruct() override;

    UPROPERTY()
    UTechAudioToolsFloatMapping* VolumeMapper;

    UPROPERTY()
    UAudioComponentViewModel* ComponentViewModel;

    UFUNCTION(BlueprintCallable)
    void OnVolumeSliderChanged(float NewNormalizedValue);

    UPROPERTY(BlueprintReadOnly)
    float CurrentDisplayVolumeDB;

    UPROPERTY(BlueprintReadOnly)
    bool bIsAudioPlaying;
};
```

**音频工具 Widget 实现 (MyAudioToolWidget.cpp)**
```cpp
// MyAudioToolWidget.cpp
#include "MyAudioToolWidget.h"
#include "TechAudioToolsFloatMapping.h"
#include "Viewmodels/AudioComponentViewModel.h"
#include "Components/AudioComponent.h"

void UMyAudioToolWidget::NativeConstruct()
{
    Super::NativeConstruct();

    // 初始化音量映射器
    VolumeMapper = NewObject<UTechAudioToolsFloatMapping>(this);
    VolumeMapper->MappingType = ETechAudioToolsFloatMappingType::Volume;
    VolumeMapper->SourceVolumeUnits = ETechAudioToolsVolumeUnit::LinearGain;
    VolumeMapper->DisplayVolumeUnits = ETechAudioToolsVolumeUnit::Decibels;
    VolumeMapper->DisplayRange_Decibels = FFloatInterval(-60.f, 0.f);

    // 初始化音频组件视图模型
    ComponentViewModel = NewObject<UAudioComponentViewModel>(this);
    // 假设我们已知要绑定的音频组件
    UAudioComponent* TargetComponent = /* ... 获取目标组件 ... */;
    ComponentViewModel->SetAudioComponent(TargetComponent);
}

void UMyAudioToolWidget::OnVolumeSliderChanged(float NewNormalizedValue)
{
    if (VolumeMapper)
    {
        // 1. 将 UI 滑块的归一化值 (0-1) 转换为显示域值 (dB)
        CurrentDisplayVolumeDB = VolumeMapper->NormalizedToDisplay(NewNormalizedValue);
        
        // 2. 将显示域值 (dB) 转换为源域值 (线性增益)
        float LinearGain = VolumeMapper->DisplayToSource(CurrentDisplayVolumeDB);
        
        // 3. 应用源域值到 MetaSound 或音频组件
        // SetVolume(LinearGain); // 伪代码
    }
    
    if (ComponentViewModel)
    {
        // 查询播放状态以更新 UI
        bIsAudioPlaying = ComponentViewModel->IsPlaying();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Metasound` | 核心 MetaSound 框架，用于音频图运行时和编辑器集成 |
| `ModelViewViewModel` | UE 的 MVVM 框架，用于创建可绑定 UI 的 ViewModel |
| `TechAudioToolsMetaSound` | 本插件的 MetaSound 集成模块，包含具体的节点和功能 |
| `TechAudioToolsMetaSoundEditor` | 本插件的 MetaSound 编辑器扩展模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 重构 MetaSound 引脚类型注册和编辑器行为，代码整合。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退一个导致编译错误的提交。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 对 MetaSound 引脚系统进行整理和统一。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound Literal ViewModel 添加事务支持，便于编辑器撤销/重做。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 重命名 `DocumentConfiguration` 为更明确的 `MetaSoundTemplate`。 |

### 维护评价

-   **创建时间**：2025年4月，插件历史约1.5年，属于较新的实验性插件。
-   **更新频率**：最近半年（2026年3月-4月）有持续的功能性更新和重构（如 ViewModel 事务支持、MetaSound 编辑器代码整合），表明**正在活跃维护**。
-   **状态**：作为 `IsBetaVersion=true` 和 `IsExperimentalVersion=false` 的实验性插件，其 API 和功能可能不稳定，未来可能发生变化。
-   **推荐度**：如果你的项目深度依赖 MetaSound 并需要开发复杂的音频工具或 UI，这个插件提供了有价值的基础架构。但由于其**实验性状态**，在生产项目中使用需谨慎，建议密切关注其更新日志和 breaking changes。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools/Tests) (路径推测，可能位于插件根目录或Engine/Tests下)