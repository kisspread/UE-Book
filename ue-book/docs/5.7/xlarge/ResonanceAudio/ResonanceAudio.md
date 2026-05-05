# Resonance Audio

> 3D audio spatialization and room acoustics simulation plugin by Google.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ResonanceAudio` (Runtime), `ResonanceAudioEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-13 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ResonanceAudio) | |

## 用途

Resonance Audio 是由 Google 开发的高级音频插件，旨在为 Unreal Engine 项目提供沉浸式的 3D 音频体验。它不仅仅是一个简单的空间化工具，而是一个完整的音频渲染解决方案，核心功能包括：

1.  **基于 HRTF 的双耳渲染**：通过头部相关传输函数 (HRTF) 将 3D 空间中的声音精确渲染到用户的双耳，创造出逼真的方位感和距离感，特别适用于 VR/AR 应用。
2.  **房间声学模拟**：能够模拟声音在不同材质和形状的房间内的反射、混响和遮挡效果，极大地增强了环境的真实感。
3.  **声源指向性与扩散控制**：允许开发者定义声音的发射模式（如全向、心形、8字形）和扩散角度，模拟真实世界中不同声源的特性。
4.  **与 UE 音频引擎深度集成**：作为音频插件，它无缝接入 UE 的 Submix 和 Soundfield 系统，允许在复杂的音频处理链中使用。

该插件解决了在游戏和交互式媒体中创建可信、动态且高性能 3D 音频的挑战，是追求顶级音频沉浸感项目的理想选择。

## 使用场景

-   **VR/AR 应用**：你需要精确的头部追踪音频，让用户能够通过声音判断虚拟物体的准确位置和距离。
-   **恐怖或探索类游戏**：你需要模拟脚步声在走廊中的回声，或者远处传来的、带有明显方向感的低语。
-   **建筑或空间演示**：你需要向客户展示一个虚拟房间在不同材质（如地毯、大理石、玻璃）下的声学效果。
-   **音乐或播客应用**：你需要将多个音轨放置在虚拟的 3D 空间中，为听众提供环绕声体验。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Global Reverb Preset` | 设置 Resonance Audio 的全局混响预设，影响所有使用该预设的声源。 | `UResonanceAudioBlueprintFunctionLibrary` |
| `Get Global Reverb Preset` | 获取当前设置的全局混响预设。 | `UResonanceAudioBlueprintFunctionLibrary` |
| `Set Sound Source Directivity` | 设置指定声源的指向性模式（Pattern）和锐度（Sharpness）。 | `UResonanceAudioSpatializationSourceSettings` |
| `Set Sound Source Spread` | 设置指定声源的扩散（宽度）角度。 | `UResonanceAudioSpatializationSourceSettings` |

### 使用示例（蓝图描述）

1.  **配置全局混响**：
    *   创建一个 `UResonanceAudioReverbPluginPreset` 资产，配置房间大小、混响时间等参数。
    *   在游戏开始时，调用 `Set Global Reverb Preset` 节点，将该预设资产作为输入。之后所有启用混响的声源都会应用此效果。

2.  **调整单个声源特性**：
    *   获取一个 `UAudioComponent` 的引用。
    *   从该组件获取其 `ResonanceAudioSpatializationSourceSettings` 对象（通常在组件的详细信息面板中设置）。
    *   调用 `Set Sound Source Directivity` 节点，将 `Pattern` 设为 `0.7`（心形指向），`Sharpness` 设为 `2.0`，使声音主要从声源前方发出。
    *   调用 `Set Sound Source Spread` 节点，将 `Spread` 设为 `45.0`，使声音在45度的锥形范围内扩散。

## C++ 用法

### 头文件引入

```cpp
#include "ResonanceAudioBlueprintFunctionLibrary.h"
#include "ResonanceAudioSpatializationSourceSettings.h"
```

### 基本用法

```cpp
// 设置全局混响预设 (来自 ResonanceAudioBlueprintFunctionLibrary.h)
UResonanceAudioReverbPluginPreset* MyReverbPreset = LoadObject<UResonanceAudioReverbPluginPreset>(nullptr, TEXT("/Game/Audio/MyReverbPreset"));
if (MyReverbPreset)
{
    UResonanceAudioBlueprintFunctionLibrary::SetGlobalReverbPreset(MyReverbPreset);
}

// 配置声源空间化设置 (来自 ResonanceAudioSpatializationSourceSettings.h)
UResonanceAudioSpatializationSourceSettings* SpatialSettings = NewObject<UResonanceAudioSpatializationSourceSettings>();
SpatialSettings->SpatializationMethod = ERaSpatializationMethod::HRTF;
SpatialSettings->Pattern = 0.5f; // 心形指向
SpatialSettings->Sharpness = 5.0f;
SpatialSettings->Spread = 60.0f;
SpatialSettings->Rolloff = ERaDistanceRolloffModel::LOGARITHMIC;
SpatialSettings->MinDistance = 100.0f;
SpatialSettings->MaxDistance = 10000.0f;

// 将设置应用到音频组件
MyAudioComponent->SetSpatializationPluginSettings(SpatialSettings);
```

### 进阶用法

结合枚举类型 `ERaMaterialName`，可以在运行时动态改变房间表面的声学材质，以模拟环境变化。

```cpp
// 假设有一个管理房间材质的系统
void UpdateRoomMaterial(ERaMaterialName NewMaterial)
{
    // 获取当前的全局混响预设
    UResonanceAudioReverbPluginPreset* CurrentPreset = UResonanceAudioBlueprintFunctionLibrary::GetGlobalReverbPreset();
    if (CurrentPreset)
    {
        // 修改预设中的材质属性 (具体属性名需查阅 UResonanceAudioReverbPluginPreset 类定义)
        // CurrentPreset->SetMaterialProperty(NewMaterial);
        // 由于修改了预设，需要通知系统更新
        CurrentPreset->UpdateSettings();
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个带有自定义空间化设置的音频组件。

**MySpatialAudioActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySpatialAudioActor.generated.h"

class UAudioComponent;
class USoundCue;
class UResonanceAudioSpatializationSourceSettings;

UCLASS()
class AMySpatialAudioActor : public AActor
{
    GENERATED_BODY()

public:
    AMySpatialAudioActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    UAudioComponent* AudioComp;

    UPROPERTY(EditAnywhere, Category = "Audio")
    USoundCue* SoundToPlay;

    UPROPERTY()
    UResonanceAudioSpatializationSourceSettings* SpatialSettings;
};
```

**MySpatialAudioActor.cpp**
```cpp
#include "MySpatialAudioActor.h"
#include "Components/AudioComponent.h"
#include "Sound/SoundCue.h"
#include "ResonanceAudioSpatializationSourceSettings.h"

AMySpatialAudioActor::AMySpatialAudioActor()
{
    PrimaryActorTick.bCanEverTick = false;
    AudioComp = CreateDefaultSubobject<UAudioComponent>(TEXT("AudioComp"));
    RootComponent = AudioComp;
}

void AMySpatialAudioActor::BeginPlay()
{
    Super::BeginPlay();

    if (SoundToPlay)
    {
        AudioComp->SetSound(SoundToPlay);

        // 创建并配置空间化设置
        SpatialSettings = NewObject<UResonanceAudioSpatializationSourceSettings>(this);
        SpatialSettings->SpatializationMethod = ERaSpatializationMethod::HRTF;
        SpatialSettings->Pattern = 0.8f; // 强指向性
        SpatialSettings->Sharpness = 10.0f;
        SpatialSettings->Spread = 30.0f;

        // 应用设置到音频组件
        AudioComp->SetSpatializationPluginSettings(SpatialSettings);

        AudioComp->Play();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ProceduralMeshComponent` | 用于在编辑器中可视化声源的指向性模式。 |
| `AudioMixer` | Resonance Audio 作为音频插件，深度集成于 UE 的 Audio Mixer 子系统。 |
| `SignalProcessing` | 可能用于底层的音频信号处理算法。 |

## 维护状态

### 近期更新

```
- 9530dbfc27ba Use PRAGMAs for unreachable code warnings where appropriate and put in clang disabling as needed Fix some unreachable code warnings
- 6ae573356bbf Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- b059f7b46335 Fix trivial unreachable code warnings.
```

### 维护评价

Resonance Audio 插件由 Google 创建于 2017 年，是一个相对成熟但标记为实验性（`IsBetaVersion=true`）的插件。从近期的 git 历史来看，最近的提交（2025年）均为代码质量改进和编译警告修复，**没有实质性的功能更新或新特性添加**。这表明该插件可能处于**维护不活跃**状态，主要进行必要的兼容性维护。

**注意事项**：
1.  **实验性状态**：尽管默认启用，但其 `IsBetaVersion=true` 标志意味着 API 和功能在未来版本中可能发生不兼容的变更。
2.  **平台限制**：运行时模块仅支持 Android, iOS, Linux, Mac, Win64。
3.  **依赖关系**：它依赖 `ProceduralMeshComponent` 插件，确保项目已启用该插件。

**推荐**：如果你的项目（尤其是 VR/AR 项目）需要高质量的 HRTF 空间音频和房间混响，并且可以接受其“实验性”状态和潜在的维护风险，那么 Resonance Audio 仍然是一个功能强大的选择。对于新项目，建议评估 UE5 原生音频系统或其他更活跃维护的第三方音频解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ResonanceAudio)
- [官方文档](https://developers.google.com/resonance-audio/develop/unreal/getting-started)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ResonanceAudio/Tests) (如果存在)

---
# Resonance Audio (Runtime 模块)

> Resonance Audio 插件的核心运行时模块，负责所有音频空间化、渲染和混响处理。

| 属性 | 值 |
|---|---|
| 模块名 | `ResonanceAudio` |
| 类型 | Runtime |
| 加载阶段 | PreDefault |
| 平台支持 | Android, IOS, Linux, Mac, Win64 |

## 模块概述

此模块是插件的心脏，包含了实现 HRTF 渲染、房间声学模拟、声源指向性处理等所有核心功能的代码。它作为音频插件注册到 UE 的音频引擎中，在运行时处理所有与 Resonance Audio 相关的音频数据流。

## 主要类与功能

### 1. 空间化设置 (`UResonanceAudioSpatializationSourceSettings`)
*   **功能**：为单个声源配置空间化参数。
*   **关键属性**：
    *   `SpatializationMethod`: 选择立体声平移或 HRTF 渲染。
    *   `Pattern` & `Sharpness`: 控制声源的指向性（全向、心形等）和锐度。
    *   `Spread`: 控制声源的扩散角度。
    *   `Rolloff`, `MinDistance`, `MaxDistance`: 配置距离衰减模型。
*   **蓝图函数**：`SetSoundSourceDirectivity`, `SetSoundSourceSpread`。

### 2. 声场设置 (`UResonanceAudioSoundfieldSettings`)
*   **功能**：配置用于 Submix 的声场编码模式。
*   **关键属性**：
    *   `RenderMode`: 选择渲染质量，从立体声平移到三阶 Ambisonics 的双耳渲染。
*   **用途**：通常在 Submix 的详细信息面板中设置，决定该 Submix 下所有音频的渲染方式。

### 3. 全局混响预设 (`UResonanceAudioReverbPluginPreset`)
*   **功能**：定义全局的房间混响参数。
*   **管理**：通过 `UResonanceAudioBlueprintFunctionLibrary` 的 `SetGlobalReverbPreset` 和 `GetGlobalReverbPreset` 函数进行全局设置和获取。

### 4. 枚举类型
*   `EResonanceRenderMode`: 定义声场渲染质量级别。
*   `ERaQualityMode`, `ERaSpatializationMethod`, `ERaDistanceRolloffModel`, `ERaMaterialName`: 提供各种配置选项的蓝图友好枚举。

## 音频处理流程

1.  **声源注册**：当一个 `UAudioComponent` 使用 Resonance Audio 空间化设置时，它会向此模块注册。
2.  **参数应用**：模块读取声源的 `UResonanceAudioSpatializationSourceSettings`，应用指向性、扩散、衰减等参数。
3.  **HRTF 渲染**：根据全局或 Submix 的 `UResonanceAudioSoundfieldSettings` 中的 `RenderMode`，使用相应的 Ambisonics 阶数和 HRTF 数据集进行双耳渲染。
4.  **混响处理**：将声源信号送入由 `UResonanceAudioReverbPluginPreset` 定义的房间混响引擎进行处理。
5.  **输出**：将处理后的双耳音频信号输出到音频设备。

---
# Resonance Audio Editor (Editor 模块)

> Resonance Audio 插件的编辑器模块，提供编辑器内的工具、资产类型和自定义界面。

| 属性 | 值 |
|---|---|
| 模块名 | `ResonanceAudioEditor` |
| 类型 | Editor |
| 加载阶段 | PostEngineInit |
| 平台支持 | Linux, Mac, Win64 |

## 模块概述

此模块仅在 Unreal Editor 中加载，负责提供与 Resonance Audio 相关的编辑器体验。它不包含任何运行时逻辑，主要功能是扩展编辑器以更好地支持该插件的资产和工作流。

## 主要功能

1.  **资产类型注册**：注册 `UResonanceAudioReverbPluginPreset` 等自定义资产类型，使其可以在内容浏览器中创建、编辑和管理。
2.  **详细信息面板自定义**：为 `UResonanceAudioSpatializationSourceSettings`、`UResonanceAudioSoundfieldSettings` 等类提供自定义的详细信息面板界面，可能包括可视化控件（如指向性模式的 3D 预览）。
3.  **编辑器工具**：可能包含用于测试、调试或可视化 Resonance Audio 设置的编辑器工具或窗口。
4.  **资产验证**：对 Resonance Audio 相关的资产进行编辑器内的验证和错误检查。

## 与运行时模块的交互

编辑器模块主要通过以下方式与运行时模块交互：
*   **创建和编辑资产**：在编辑器中创建的 `UResonanceAudioReverbPluginPreset` 资产，其数据会被运行时模块在打包后的游戏中加载和使用。
*   **配置声源**：在 Actor 的 `UAudioComponent` 上设置 `UResonanceAudioSpatializationSourceSettings`，这些设置在编辑器中配置，在运行时生效。
*   **预览**：可能利用运行时模块的部分功能在编辑器视图中提供音频效果的近似预览。