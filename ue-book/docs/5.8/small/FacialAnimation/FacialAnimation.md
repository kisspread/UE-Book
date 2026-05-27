# Facial Animation Bulk Importer

> Bulk importer for facial animation curves and audio. Imports facial animation curve tables (from FBX) into sound waves.

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画批量导入器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FacialAnimation` (Runtime), `FacialAnimationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation) | |

## 用途

此插件旨在解决**语音驱动面部动画（Lip-Sync）** 工作流中的一个核心痛点：将外部音频工具生成的口型动画数据高效、批量地整合到虚幻引擎项目中。

传统的工作流程中，动画师可能需要为每段对话语音手动调整或在引擎中录制面部骨骼/变形目标曲线，过程繁琐且难以与音频精确同步。`Facial Animation Bulk Importer` 插件通过以下方式简化此流程：
1.  **数据导入**：批量导入包含音频（`.wav`）和对应面部动画曲线（以 FBX 格式保存的 `Curve Table`）的文件。
2.  **资产烘焙**：将导入的动画曲线数据直接烘焙到 `USoundWave` 资产中。这样，当游戏播放该音频资产时，其内置的曲线数据即可被用于驱动角色的面部动画。

其核心价值在于**将音画同步数据打包在同一个音频资产中**，使得后续在游戏逻辑中播放语音时，可以自动、精确地驱动口型和表情，无需再进行额外的同步设置，极大地提升了动画制作和集成效率。

## 使用场景

-   **角色对话密集的 RPG 或互动叙事游戏**：游戏中存在大量语音对话，需要为每段语音精确匹配口型动画。
-   **虚拟人或数字人项目**：需要实时、准确的口型同步效果。
-   **使用第三方音频/动画面部动画工具**的项目：例如使用 Adobe Animate、FaceFX 等工具生成面部动画曲线和音频，需要批量导入引擎。
-   **需要将动画数据与音频资源进行强绑定**的场景：确保任何播放该音频的地方都能自动获得正确的动画驱动数据。

## 蓝图用法

此插件的蓝图功能主要体现在提供的 `UAudioCurveSourceComponent` 组件上，它允许音频播放与动画曲线驱动同步。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Curve Source Binding Name` | 设置此组件作为曲线源的绑定名称，动画蓝图通过此名称寻找曲线源。 | `UAudioCurveSourceComponent` |
| `Get Curve Source Binding Name` | 获取当前的曲线源绑定名称。 | `UAudioCurveSourceComponent` |
| `Set Curve Sync Offset` | 设置音频播放位置与曲线求值位置之间的时间偏移（秒），用于微调口型与声音的同步。 | `UAudioCurveSourceComponent` |
| `Get Curve Value` | 获取指定名称的动画曲线在当前时刻的值。 | `UAudioCurveSourceComponent` |
| `Get Curves` | 获取当前时刻所有曲线的值，以 `TArray<FNamedCurveValue>` 形式返回。 | `UAudioCurveSourceComponent` |

### 使用示例（蓝图描述）

1.  **创建组件**：在你的角色或 Actor 蓝图中，添加一个 `Audio Curve Source Component` 组件。
2.  **绑定名称**：在组件的属性面板或通过蓝图设置 `Curve Source Binding Name`，例如设为 `“Mouth”`。这个名称需要与你动画蓝图中 `Curve Source` 节点的 `Binding Name` 相匹配。
3.  **播放音频**：通过蓝图调用此组件的 `Play` 函数播放已导入了曲线数据的 `SoundWave` 资产。
4.  **驱动动画**：在动画蓝图中，使用一个 `Curve Source` 节点，并设置其 `Curve Source` 为 `Self`（如果曲线源在同一个 Actor 上），并填入相同的 `Binding Name`（`“Mouth”`）。该节点会自动获取 `AudioCurveSourceComponent` 提供的曲线值，进而驱动变形目标或骨骼动画。

## C++ 用法

此插件的核心运行时逻辑封装在 `UAudioCurveSourceComponent` 中，它继承自 `UAudioComponent` 并实现了 `ICurveSourceInterface` 接口。

### 头文件引入

```cpp
#include "AudioCurveSourceComponent.h"
#include "Components/CurveSourceInterface.h"
```

### 基本用法

创建并配置一个音频曲线源组件，并手动驱动其 Tick 以求值曲线。
*来源文件：`Engine/Plugins/Editor/FacialAnimation/Source/FacialAnimation/Public/AudioCurveSourceComponent.h`*

```cpp
// 在某个 Actor 类中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
TObjectPtr<UAudioCurveSourceComponent> AudioCurveSource;

// 在构造函数或初始化中创建
void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    
    if (!AudioCurveSource)
    {
        AudioCurveSource = NewObject<UAudioCurveSourceComponent>(this, UAudioCurveSourceComponent::StaticClass(), TEXT("AudioCurveSource"));
        AudioCurveSource->RegisterComponent();
        AudioCurveSource->AttachToComponent(RootComponent, FAttachmentTransformRules::KeepRelativeTransform);
    }
    
    // 设置曲线源的绑定名，动画蓝图将通过此名称识别它
    AudioCurveSource->CurveSourceBindingName = FName("LipSync");
    
    // 可选：设置曲线与音频的同步偏移（秒），用于补偿音频预滚动延迟
    AudioCurveSource->CurveSyncOffset = -0.4f; // 示例：提前0.4秒求值曲线，以应对音频预滚动
}
```

### 进阶用法

手动获取指定时刻的曲线值，或在自定义的 Tick 逻辑中集成曲线求值。
*注意：`UAudioCurveSourceComponent` 的 `TickComponent` 会自动同步其内部的播放状态和曲线求值时间，通常情况下直接使用其提供的 `GetCurveValue` 即可。*

```cpp
void AMyActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    
    if (AudioCurveSource && AudioCurveSource->IsPlaying())
    {
        // 获取名为 "JawOpen" 的曲线在当前时刻的值
        float JawOpenValue = AudioCurveSource->GetCurveValue(FName("JawOpen"));
        
        // 根据曲线值驱动某个自定义逻辑（例如，控制一个对话气泡的大小）
        UpdateDialogBubble(JawOpenValue);
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个自定义的动画曲线源组件。
*此示例假设你已在项目中启用了 `FacialAnimation` 插件。*

### MyAnimationCurveSourceComponent.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Components/CurveSourceInterface.h"
#include "MyAnimationCurveSourceComponent.generated.h"

UCLASS(ClassGroup=(Animation), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyAnimationCurveSourceComponent : public UActorComponent, public ICurveSourceInterface
{
    GENERATED_BODY()

public:
    UMyAnimationCurveSourceComponent();

    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    // ICurveSourceInterface 接口实现
    virtual FName GetBindingName_Implementation() const override;
    virtual float GetCurveValue_Implementation(FName CurveName) const override;
    virtual void GetCurves_Implementation(TArray<FNamedCurveValue>& OutCurve) const override;

    /** 用于外部输入模拟曲线值的接口 */
    UPROPERTY(BlueprintReadWrite, Category = "Animation Curves")
    TMap<FName, float> SimulatedCurveValues;

    /** 此曲线源的绑定名称 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation Curves")
    FName BindingName;

private:
    /** 内部缓存的曲线值，用于 ICurveSourceInterface 返回 */
    mutable TMap<FName, float> CachedCurveValues;
};
```

### MyAnimationCurveSourceComponent.cpp

```cpp
#include "MyAnimationCurveSourceComponent.h"

UMyAnimationCurveSourceComponent::UMyAnimationCurveSourceComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.bStartWithTickEnabled = true;
    BindingName = FName("CustomCurveSource");
}

void UMyAnimationCurveSourceComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    // 每 Tick 将蓝图可写的 SimulatedCurveValues 同步到内部缓存，供接口查询
    CachedCurveValues = SimulatedCurveValues;
}

FName UMyAnimationCurveSourceComponent::GetBindingName_Implementation() const
{
    return BindingName;
}

float UMyAnimationCurveSourceComponent::GetCurveValue_Implementation(FName CurveName) const
{
    if (const float* FoundValue = CachedCurveValues.Find(CurveName))
    {
        return *FoundValue;
    }
    return 0.0f;
}

void UMyAnimationCurveSourceComponent::GetCurves_Implementation(TArray<FNamedCurveValue>& OutCurve) const
{
    OutCurve.Empty();
    for (const TPair<FName, float>& CurvePair : CachedCurveValues)
    {
        OutCurve.Add(FNamedCurveValue(CurvePair.Key, CurvePair.Value));
    }
}
```

**使用方式**：
1.  将 `UMyAnimationCurveSourceComponent` 添加到你的 Actor。
2.  在蓝图或其他代码中，写入 `SimulatedCurveValues` Map 来驱动曲线值。
3.  在动画蓝图中，使用 `Curve Source` 节点，将 `Binding Name` 设置为与组件的 `BindingName` 属性一致，即可接收这些曲线值。

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 该插件主要依赖引擎核心和编辑器标准模块，用于资产导入和 UI。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为包含生成代码的源文件添加了内联宏，以优化编译。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 统一方法/静态变量的 DLL 导出声明。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件级别文件目录调整。 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 为未来更改预添加头文件包含。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了内置插件的链接地址以使用 HTTPS。 |

### 维护评价

`Facial Animation Bulk Importer` 是一个**历史悠久的实验性插件**。它于 2016 年创建，旨在为 UE4 时代的语音驱动动画提供批量导入方案。

**评价**：
1.  **年龄与状态**：创建于 2016 年，已超过 8 年，属于“文物”级插件。`.uplugin` 中明确标记为 `IsBetaVersion: true`（实验性），且自创建起一直保持此状态。
2.  **维护活跃度**：**极不活跃**。从 git 历史看，自 2023 年初的目录调整后，再无针对此插件本身的功能性更新。后续的更新（2025年）均属于全局性的代码库维护（如宏统一、链接更新），与插件功能无关。可以判断该插件处于 **“维护不活跃，接近废弃”** 状态。
3.  **功能与兼容性**：核心功能（FBX 曲线导入、`UAudioCurveSourceComponent`）在后续引擎版本中可能仍能工作，但由于长期未更新，**未经验证**其与最新 UE5 特性（如 Metahuman、增强输入、新版音效系统）的兼容性。作为实验性插件，其 API 和行为在未来版本中可能被更改或移除。
4.  **已知问题与限制**：
    *   标记为“实验性”，API 不稳定，不推荐在生产环境中依赖。
    *   导入工作流（FBX → Curve Table → SoundWave）可能比 UE5 现代化的对话系统或 MetaHuman 的解决方案更复杂。
    *   缺乏官方文档和持续支持。
5.  **推荐使用**：
    *   **不推荐用于新项目**。对于新项目，应优先评估 UE5 内置的、更新的对话动画或 MetaHuman 工具链。
    *   **可用于遗留项目**：如果你有一个长期运行的 UE4/UE5 项目，并且已经基于此插件构建了稳定的工作流，可以继续使用，但需注意其“实验性”身份，并做好在未来版本中被移除或需要替换的心理准备。
    *   **学习与研究**：其源码（特别是 `ICurveSourceInterface` 的实现）对于理解 UE 的音频-动画同步机制有一定参考价值。

**总结：这是一个功能明确但已停止积极维护的实验性插件。除非有强烈的历史遗留原因，否则在新项目中应避免使用。**

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation)
-   [官方文档]( ) (无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Editor/FacialAnimation) (路径待确认)