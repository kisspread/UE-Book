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
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ResonanceAudio) | |

## 用途

Resonance Audio 是由 Google 开发的高级音频插件，其核心功能远超简单的 3D 音效定位。它旨在为虚拟现实（VR）、增强现实（AR）和游戏应用提供**高度逼真的空间音频和房间声学模拟**。

该插件解决的核心问题是：如何在虚拟环境中模拟声音在真实物理空间中的传播行为。这包括：
1.  **精确的 3D 空间化**：基于头部相关传输函数（HRTF）或 Ambisonics 技术，让声音听起来确实来自 3D 空间中的特定点。
2.  **房间声学模拟**：根据虚拟房间的几何形状、大小和表面材质（如木材、玻璃、地毯），实时计算声音的反射、混响和遮挡效果，模拟出不同空间（如小房间、大厅、山谷）的声学特性。
3.  **声源传播模拟**：模拟声音从源头传播到听者耳朵过程中的衰减、衍射等物理现象。

它不仅仅是一个音效播放器，而是一个完整的**声学环境模拟系统**，旨在提升沉浸感和真实感。

## 使用场景

-   你在开发一个 VR 密室逃脱游戏 → 使用 Resonance Audio 模拟不同房间（如木制书房、瓷砖浴室）独特的混响和回声效果，增强空间感知。
-   你在制作一个建筑可视化项目 → 使用 Resonance Audio 预览不同设计方案（如开放式办公室 vs. 隔音会议室）的声学效果。
-   你在开发一个第一人称射击游戏 → 使用 Resonance Audio 精确模拟枪声在不同地形（室内、峡谷、开阔地）的传播和反射，为玩家提供战术听觉信息。
-   你需要为移动端（Android/iOS）应用提供高质量的 3D 音频 → Resonance Audio 提供了跨平台的优化解决方案。

## 蓝图用法

Resonance Audio 主要通过组件（Component）的方式在蓝图中使用。核心功能围绕 `UResonanceAudioSourceComponent` 和 `UResonanceAudioReverbComponent` 展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Sound Source Directivity` | 设置声源的指向性模式（如全向、心形、八字形）和锐度，模拟不同扬声器的辐射特性。 | `UResonanceAudioSourceComponent` |
| `Set Sound Source Spread` | 设置声源的扩散角度，控制声音的“宽度”。0度为点声源，180度为完全扩散。 | `UResonanceAudioSourceComponent` |
| `Set Sound Source Gain` | 设置声源的音量增益。 | `UResonanceAudioSourceComponent` |
| `Set Room Properties` | 动态设置房间的几何形状、尺寸和表面材质，实时改变混响效果。 | `UResonanceAudioReverbComponent` |
| `Set Reverb Preset` | 快速应用预设的混响效果（如小房间、大厅、板式混响）。 | `UResonanceAudioReverbComponent` |
| `Set Occlusion Intensity` | 设置声源被障碍物遮挡时的衰减强度。 | `UResonanceAudioSourceComponent` |

### 使用示例（蓝图描述）

1.  **为声源添加空间化**：
    -   在场景中的 Actor（如一个播放音乐的收音机）上，添加 `Resonance Audio Source` 组件。
    -   将该组件的 `Sound` 属性设置为你的音频资产。
    -   在事件图表中，可以调用 `Set Sound Source Directivity` 节点，将模式设为 `Cardioid`（心形），锐度设为 `0.5`，模拟一个有方向性的扬声器。

2.  **为房间设置声学环境**：
    -   在代表房间的 Actor（或场景根 Actor）上，添加 `Resonance Audio Reverb` 组件。
    -   在组件的细节面板中，勾选 `Enable Room`。
    -   通过 `Set Room Properties` 节点，可以动态传入一个 `FResonanceAudioRoomProperties` 结构体，其中包含房间的尺寸（长宽高）和六个面的材质（如 `Brick`、`Wood`、`Glass`）。
    -   或者，直接使用 `Set Reverb Preset` 节点选择一个预设，如 `Large Hall`。

## C++ 用法

### 头文件引入

```cpp
#include "ResonanceAudio.h"
#include "ResonanceAudioSourceComponent.h"
#include "ResonanceAudioReverbComponent.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建并配置一个 Resonance Audio 声源组件。

```cpp
// 在你的 Actor 头文件 (.h) 中
#include "Components/ResonanceAudioSourceComponent.h"

UCLASS()
class AMySoundActor : public AActor
{
    GENERATED_BODY()

public:
    AMySoundActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    UResonanceAudioSourceComponent* ResonanceSourceComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
    USoundBase* SoundAsset;
};

// 在你的 Actor 实现文件 (.cpp) 中
#include "Components/ResonanceAudioSourceComponent.h"

AMySoundActor::AMySoundActor()
{
    // 创建组件
    ResonanceSourceComponent = CreateDefaultSubobject<UResonanceAudioSourceComponent>(TEXT("ResonanceSource"));
    RootComponent = ResonanceSourceComponent;

    // 设置默认属性
    ResonanceSourceComponent->SetSound(SoundAsset);
    ResonanceSourceComponent->SetDirectivity(0.5f); // 设置指向性锐度
    ResonanceSourceComponent->SetSpread(90.0f); // 设置扩散角度
    ResonanceSourceComponent->bAutoDestroy = false;
}
```

### 进阶用法

结合房间组件，动态创建一个具有自定义声学特性的房间。

```cpp
// 在你的 Actor 头文件 (.h) 中
#include "Components/ResonanceAudioReverbComponent.h"
#include "ResonanceAudioRoom.h" // 用于 FResonanceAudioRoomProperties

UCLASS()
class AMyRoomActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRoomActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    UResonanceAudioReverbComponent* ResonanceReverbComponent;

    UFUNCTION(BlueprintCallable, Category = "Audio")
    void UpdateRoomAcoustics(FVector Dimensions, EResonanceAudioSurfaceMaterial WallMaterial);
};

// 在你的 Actor 实现文件 (.cpp) 中
#include "ResonanceAudioRoom.h"

AMyRoomActor::AMyRoomActor()
{
    ResonanceReverbComponent = CreateDefaultSubobject<UResonanceAudioReverbComponent>(TEXT("ResonanceReverb"));
    RootComponent = ResonanceReverbComponent;
    ResonanceReverbComponent->bEnableRoom = true;
}

void AMyRoomActor::UpdateRoomAcoustics(FVector Dimensions, EResonanceAudioSurfaceMaterial WallMaterial)
{
    FResonanceAudioRoomProperties RoomProperties;
    RoomProperties.Dimensions = Dimensions;
    // 设置所有墙面为同一种材质
    RoomProperties.LeftWallMaterial = WallMaterial;
    RoomProperties.RightWallMaterial = WallMaterial;
    RoomProperties.FloorMaterial = WallMaterial;
    RoomProperties.CeilingMaterial = WallMaterial;
    RoomProperties.FrontWallMaterial = WallMaterial;
    RoomProperties.BackWallMaterial = WallMaterial;

    ResonanceReverbComponent->SetRoomProperties(RoomProperties);
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个带有空间化声源和房间混响的 Actor。

**MyResonanceDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/ResonanceAudioSourceComponent.h"
#include "Components/ResonanceAudioReverbComponent.h"
#include "MyResonanceDemoActor.generated.h"

UCLASS()
class MYPROJECT_API AMyResonanceDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyResonanceDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    // 声源组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Resonance Audio")
    UResonanceAudioSourceComponent* AudioSource;

    // 房间混响组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Resonance Audio")
    UResonanceAudioReverbComponent* RoomReverb;

    // 要播放的声音资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Resonance Audio")
    USoundBase* TestSound;
};
```

**MyResonanceDemoActor.cpp**
```cpp
#include "MyResonanceDemoActor.h"
#include "ResonanceAudioRoom.h"

AMyResonanceDemoActor::AMyResonanceDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建根组件
    USceneComponent* SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    RootComponent = SceneRoot;

    // 创建并附加声源组件
    AudioSource = CreateDefaultSubobject<UResonanceAudioSourceComponent>(TEXT("AudioSource"));
    AudioSource->SetupAttachment(RootComponent);

    // 创建并附加房间混响组件
    RoomReverb = CreateDefaultSubobject<UResonanceAudioReverbComponent>(TEXT("RoomReverb"));
    RoomReverb->SetupAttachment(RootComponent);
    RoomReverb->bEnableRoom = true; // 启用房间效果
}

void AMyResonanceDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 设置声源
    if (AudioSource && TestSound)
    {
        AudioSource->SetSound(TestSound);
        AudioSource->Play();
    }

    // 配置一个简单的房间（例如 5x4x3 米的木制房间）
    if (RoomReverb)
    {
        FResonanceAudioRoomProperties RoomProps;
        RoomProps.Dimensions = FVector(500.0f, 400.0f, 300.0f); // 单位：厘米
        RoomProps.LeftWallMaterial = EResonanceAudioSurfaceMaterial::Wood;
        RoomProps.RightWallMaterial = EResonanceAudioSurfaceMaterial::Wood;
        RoomProps.FloorMaterial = EResonanceAudioSurfaceMaterial::Wood;
        RoomProps.CeilingMaterial = EResonanceAudioSurfaceMaterial::Plaster;
        RoomProps.FrontWallMaterial = EResonanceAudioSurfaceMaterial::Wood;
        RoomProps.BackWallMaterial = EResonanceAudioSurfaceMaterial::Wood;
        RoomReverb->SetRoomProperties(RoomProps);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ProceduralMeshComponent` | 用于在编辑器中可视化房间几何形状，或根据几何体动态生成声学网格。 |

## 维护状态

### 近期更新

```
- 91c57d395e6b Removed redundant module includes.
- e599d19e4b0d Removing redundant Private includes.
- 9a1d5b1ad40d [Engine/Plugins] * Ran IWYU on ~170 plugins to remove includes not needed. Public api still keep old includes inside #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2
```

以上提交均为代码清理和编译优化（IWYU - Include What You Use），没有引入新功能或修复特定 bug。

### 维护评价

**综合评价：维护不活跃，使用需谨慎。**

-   **年龄**：插件创建于 2017 年，已有约 7 年历史。
-   **近期活动**：最近的提交（2023 年）全部是代码维护性清理，**没有实质性功能更新或 bug 修复**。最后一次功能性更新可能更早。
-   **状态**：`.uplugin` 中标记为 `IsBetaVersion: true`，表明它可能从未达到完全稳定的正式版状态。
-   **已知限制**：作为 Google 的项目，其维护状态依赖于 Epic Games 的集成和更新。从提交历史看，Epic 主要进行的是编译兼容性维护，而非功能演进。
-   **推荐**：**不推荐用于新项目的关键路径**。如果项目对空间音频有极高要求且愿意承担潜在风险，可以评估使用。对于新项目，建议优先考虑 Epic 官方维护的音频解决方案（如 MetaSounds）或社区活跃的第三方插件。如果已有项目在使用，且功能满足需求，可继续使用，但需注意未来引擎版本升级可能带来的兼容性问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ResonanceAudio)
- [官方文档](https://developers.google.com/resonance-audio/develop/unreal/getting-started)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ResonanceAudio/Tests)