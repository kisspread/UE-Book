# Resonance Audio

> 3D audio spatialization and room acoustics simulation plugin by Google.

| 属性 | 值 |
|---|---|
| 中文名 | 共振音频 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ResonanceAudio` (Runtime), `ResonanceAudioEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-13 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ResonanceAudio) | |

## 用途

ResonanceAudio 是一个由 Google 开发的第三方音频空间化插件。它为 Unreal Engine 提供了基于物理的 3D 音频渲染能力，核心功能包括**双耳（Binaural）空间化**和**实时房间声学模拟**。此插件旨在解决在 VR/AR、游戏及影视内容中创建逼真、沉浸式空间音频的复杂问题，通过模拟声音在空间中的传播、反射和吸收，使听觉体验与虚拟环境的高度几何和材质属性相匹配，超越简单的立体声或 5.1 环绕声效果。

其主要存在意义是为需要高品质空间音频的项目（尤其是 VR）提供一个经过优化、跨平台的解决方案，相较于引擎内置的某些空间化方案（如早期的 Oculus Audio），它提供了一套更统一的配置和工作流。

## 使用场景

-   你正在开发一个 VR 体验或游戏，需要音频具有精确的 3D 定位和头部追踪（HRTF），让玩家能清晰地分辨出声音来自上方、下方或身后。
-   你的虚拟场景中有复杂的空间结构（如大厅、隧道、房间），你希望音频能真实地反映声音在其中的传播、回响和隔音效果。
-   你需要为移动端（Android, iOS）或桌面端（PC, Mac, Linux）的项目集成一个统一的、高质量的音频空间化方案。

## 蓝图用法

插件提供了用于配置单个声源空间化属性和全局混响效果的蓝图资产类型。其核心蓝图节点主要围绕“创建”和“配置”这些资产。

### 核心资产配置

**1. 空间化源设置 (Resonance Audio Spatialization Source Settings)**
此资产用于配置单个声源的空间化行为。
| 蓝图属性/节点 | 说明 | 所在类 |
|---|---|---|
| `SpatializationMode` | 设置空间化模式（双耳或立体声） | `UResonanceAudioSpatializationSourceSettings` |
| `Pattern` | 设置声音辐射模式（例如全向、心形） | `UResonanceAudioSpatializationSourceSettings` |
| `Sharpness` | 控制声音辐射的聚焦程度 | `UResonanceAudioSpatializationSourceSettings` |

**2. 混响插件预设 (Resonance Audio Reverb Plugin Preset)**
此资产用于配置空间的全局混响效果。
| 蓝图属性/节点 | 说明 | 所在类 |
|---|---|---|
| `RoomProperties` | 设置房间的尺寸、材质吸收率等物理属性 | `UResonanceAudioReverbPluginPreset` |
| `ReflectionScalar` | 控制反射声的强度 | `UResonanceAudioReverbPluginPreset` |
| `ReverbGain` | 控制混响的整体增益 | `UResonanceAudioReverbPluginPreset` |

### 使用示例（蓝图描述）

要让一个声源使用 Resonance 的空间化：
1.  创建或在内容浏览器中找到一个 `Resonance Audio Spatialization Source Settings` 资产。
2.  在场景中放置一个 `Audio Component`，或修改一个已有音源。
3.  在该 `Audio Component` 的细节面板中，找到“Attenuation” -> “Spatialization” -> “Plugin Settings”，将其指向你创建的 `Resonance Audio Spatialization Source Settings` 资产。
4.  运行时，该声源的声音将根据该设置资产的配置进行空间化渲染。

要为场景应用全局混响：
1.  创建或在内容浏览器中找到一个 `Resonance Audio Reverb Plugin Preset` 资产。
2.  将其配置到项目的音频设置中，或通过蓝图在运行时动态激活。

## C++ 用法

虽然此插件主要通过蓝图资产进行配置，但其底层模块也暴露了 C++ 接口，允许开发者进行更底层的控制或集成。

### 头文件引入

```cpp
#include "ResonanceAudio.h"
```

### 基本用法

典型用法是通过 `FResonanceAudioAPI` 单例与 Resonance 引擎交互。以下示例展示了如何查询和应用空间化源设置。
*(基于插件模块接口和典型用法推断)*

```cpp
// 获取 Resonance Audio API 的单例引用
// 注意：实际的API类名需要根据头文件确认，此处为示意
if (IResonanceAudioModule* ResonanceModule = FModuleManager::GetModulePtr<IResonanceAudioModule>(“ResonanceAudio”))
{
    // 通常插件会通过模块管理器提供全局单例或服务接口
    // 具体用法需参考 ResonanceAudio 模块的公共头文件
}
```

### 进阶用法

对于需要动态调整多个声源空间化属性的场景，可以在 C++ 中创建和配置设置资产实例，然后将其应用到声源组件上。这通常涉及到与 `UAudioComponent` 的交互。

## Demo 示例

以下是一个最小示例，展示如何在 C++ 中创建一个使用 Resonance 空间化的声源。假设你的项目已经启用了 ResonanceAudio 插件。

**MySpatializedSoundActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySpatializedSoundActor.generated.h"

class UAudioComponent;
class UResonanceAudioSpatializationSourceSettings;

UCLASS()
class MYPROJECT_API AMySpatializedSoundActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMySpatializedSoundActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UAudioComponent* AudioComp;

    // 空间化设置资产实例
    UPROPERTY()
    UResonanceAudioSpatializationSourceSettings* SpatializationSettings;
};
```

**MySpatializedSoundActor.cpp**
```cpp
#include "MySpatializedSoundActor.h"
#include "Components/AudioComponent.h"
#include "Sound/SoundCue.h"
#include “ResonanceAudioSpatializationSourceSettings.h” // 插件资产类头文件

AMySpatializedSoundActor::AMySpatializedSoundActor()
{
    PrimaryActorTick.bCanEverTick = false;

    AudioComp = CreateDefaultSubobject<UAudioComponent>(TEXT(“Audio”));
    RootComponent = AudioComp;
}

void AMySpatializedSoundActor::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时创建空间化设置资产的实例
    // 注意：更常见的做法是在编辑器中预先创建资产并引用，这里仅为演示动态创建。
    SpatializationSettings = NewObject<UResonanceAudioSpatializationSourceSettings>(this);
    if (SpatializationSettings)
    {
        // 配置空间化参数（例如使用双耳模式）
        // SpatializationSettings->SpatializationMode = ...;
        // 将配置应用到音频组件
        // 具体应用方式取决于UE版本和插件暴露的API，可能是设置 attenuation 或 plugin settings。
        // AudioComp->SetSpatializationSettings(SpatializationSettings);
    }
}
```

## 模块依赖

作为第三方插件，其核心依赖通过 `.uplugin` 文件中的 `Plugins` 字段声明。
使用此插件的模块无需在 `Build.cs` 中添加特殊依赖，插件本身已将其依赖（如 `ProceduralMeshComponent`）打包。你的项目模块只需确保启用了 `ResonanceAudio` 插件即可。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单分类。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-01-20 | `7cfdbde4` | AudioMixerDevice - Add ref count to submixes using the register/unregister API. When no longer referenced, automatically unregister. | 为子混音添加引用计数机制，当无引用时自动注销。 |
| 2025-11-10 | `3ecbd390` | Fixed broken printf specifier strings. | 修复了损坏的 printf 格式说明符字符串。 |

### 维护评价

ResonanceAudio 插件仍在**积极维护**中。尽管其 `.uplugin` 中标记为实验性 (`IsBetaVersion: true`)，但从近期的提交记录看，它在 2026 年仍有针对编译警告、日志系统迁移和底层音频混合器功能的更新。作为 Google 提供的第三方插件，其更新频率可能依赖于上游 SDK 和 Epic 与 Google 的集成工作。目前没有迹象表明它被废弃。推荐用于需要高质量空间音频且目标平台在插件支持列表内的项目（Android, iOS, Linux, Mac, Win64）。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ResonanceAudio)
-   [官方文档](https://developers.google.com/resonance-audio/develop/unreal/getting-started)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ResonanceAudio) （插件目录内，如有）