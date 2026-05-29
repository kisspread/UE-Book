# Resonance Audio

> 3D audio spatialization and room acoustics simulation plugin by Google.

| 属性 | 值 |
|---|---|
| 中文名 | 共振音频 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（音频资产、HRIR 数据、预设资产） |
| 模块 | `ResonanceAudio` (Runtime), `ResonanceAudioEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-13 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ResonanceAudio) | |

## 用途

Resonance Audio 是 Google 开发的高品质空间音频渲染引擎，基于 HRTF（头部相关传输函数）实现双耳立体声渲染。它解决了以下核心问题：

- **3D 空间化**：将虚拟声源以双耳立体声方式渲染，使声音具有精确的方向感和距离感，适用于耳机回放
- **房间声学模拟**：基于鞋盒体（shoebox）房间模型，模拟早期反射和晚期混响，让声音有真实的空间感
- **Ambisonics 解码**：支持一阶到三阶 Ambisonics 声场的双耳解码，用于全景声内容
- **声源特性**：支持遮挡、散射、近场效应、指向性等高级声源属性

插件内部集成了 Google 的 Resonance Audio C++ SDK（`Private/ResonanceAudioLibrary/`），通过音频图（Audio Graph）方式将各种 DSP 节点（反射、混响、HRTF 卷积、增益混合等）串联起来进行实时音频处理。

## 使用场景

- 你在做 VR/AR 应用，需要高品质的 3D 空间音频 → 用 Resonance Audio
- 你需要模拟真实房间的声学效果（不同材质墙壁的反射、混响时间）→ 用 Resonance Audio
- 你有 Ambisonics 格式的全景声素材需要双耳渲染 → 用 Resonance Audio
- 你需要声源遮挡效果（声音穿过墙壁时的衰减）→ 用 Resonance Audio
- 你只需要简单的立体声播放不需要空间化 → 不需要此插件

## 蓝图用法

### 核心节点

#### 空间化设置（UResonanceAudioSpatializationSourceSettings）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSoundSourceDirectivity` | 设置声源指向性模式（0.0=全向，0.5=心形，1.0=8 字形）和锐度 | `UResonanceAudioSpatializationSourceSettings` |
| `SetSoundSourceSpread` | 设置声源散射角度（0°~180°），控制声源宽度 | `UResonanceAudioSpatializationSourceSettings` |

#### 混响预设（UResonanceAudioReverbPluginPreset）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetEnableRoomEffects` | 启用/禁用房间效果 | `UResonanceAudioReverbPluginPreset` |
| `SetRoomPosition` | 设置房间中心位置 | `UResonanceAudioReverbPluginPreset` |
| `SetRoomRotation` | 设置房间旋转 | `UResonanceAudioReverbPluginPreset` |
| `SetRoomDimensions` | 设置房间尺寸 | `UResonanceAudioReverbPluginPreset` |
| `SetRoomMaterials` | 设置六面墙的声学材质 | `UResonanceAudioReverbPluginPreset` |
| `SetReflectionScalar` | 设置早期反射增益乘数（默认 1.0） | `UResonanceAudioReverbPluginPreset` |
| `SetReverbGain` | 设置混响增益乘数（默认 1.0） | `UResonanceAudioReverbPluginPreset` |
| `SetReverbTimeModifier` | 设置混响时间缩放因子（默认 1.0） | `UResonanceAudioReverbPluginPreset` |
| `SetReverbBrightness` | 设置混响亮度（-1.0~1.0，影响高频混响时间） | `UResonanceAudioReverbPluginPreset` |

#### 全局混响管理（UResonanceAudioBlueprintFunctionLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetGlobalReverbPreset` | 设置全局混响预设 | `UResonanceAudioBlueprintFunctionLibrary` |
| `GetGlobalReverbPreset` | 获取当前全局混响预设 | `UResonanceAudioBlueprintFunctionLibrary` |

### 使用示例

**设置声源指向性（蓝图描述）：**
1. 获取目标 Actor 上的 Audio Component
2. 从 Audio Component 获取 Resonance Audio Spatialization Source Settings 引用
3. 调用 `SetSoundSourceDirectivity(0.5, 10.0)` → 创建一个心形指向、锐度为 10 的声源

**配置房间混响（蓝图描述）：**
1. 创建一个 `UResonanceAudioReverbPluginPreset` 资产
2. 在预设中配置房间参数：
   - `SetEnableRoomEffects(true)` → 启用房间效果
   - `SetRoomDimensions(500, 300, 400)` → 设置 5m×3m×4m 的房间
   - `SetRoomMaterials([BrickPainted, BrickPainted, Concrete, PlasterRough, BrickPainted, BrickPainted])` → 设置墙材质
   - `SetReverbTimeModifier(1.5)` → 增加混响时间
3. 调用 `SetGlobalReverbPreset(Preset)` → 应用全局混响

## C++ 用法

### 头文件引入

```cpp
#include "ResonanceAudioSpatializationSourceSettings.h"
#include "ResonanceAudioReverbPluginPreset.h"
#include "ResonanceAudioBlueprintFunctionLibrary.h"
#include "IResonanceAudioModule.h"
```

### 基本用法

**获取模块实例并检查可用性：**

```cpp
// 来源: Public/IResonanceAudioModule.h
if (IResonanceAudioModule::IsAvailable())
{
    IResonanceAudioModule& ResonanceModule = IResonanceAudioModule::Get();
}
```

**设置声源空间化参数：**

```cpp
// 来源: Public/ResonanceAudioSpatializationSourceSettings.h
// 获取或创建空间化源设置
UResonanceAudioSpatializationSourceSettings* SpatialSettings = 
    GetMutableDefault<UResonanceAudioSpatializationSourceSettings>();

// 设置指向性: 0.5 = 心形模式，锐度 10.0
SpatialSettings->SetSoundSourceDirectivity(0.5f, 10.0f);

// 设置散射: 45 度
SpatialSettings->SetSoundSourceSpread(45.0f);
```

**配置房间混响：**

```cpp
// 来源: Public/ResonanceAudioReverbPluginPreset.h
UResonanceAudioReverbPluginPreset* ReverbPreset = 
    NewObject<UResonanceAudioReverbPluginPreset>();

// 启用房间效果
ReverbPreset->SetEnableRoomEffects(true);

// 设置房间位置和尺寸
ReverbPreset->SetRoomPosition(FVector(0.f, 0.f, 0.f));
ReverbPreset->SetRoomRotation(FQuat::Identity);
ReverbPreset->SetRoomDimensions(FVector(500.f, 400.f, 300.f));  // cm

// 设置墙面材质
TArray<ERaMaterialName> Materials;
Materials.SetNum(6);
Materials[0] = ERaMaterialName::BRICK_PAINTED;  // 左
Materials[1] = ERaMaterialName::BRICK_PAINTED;  // 右
Materials[2] = ERaMaterialName::CONCRETE;        // 地板
Materials[3] = ERaMaterialName::PLASTER_SMOOTH;  // 天花板
Materials[4] = ERaMaterialName::BRICK_PAINTED;  // 前
Materials[5] = ERaMaterialName::BRICK_PAINTED;  // 后
ReverbPreset->SetRoomMaterials(Materials);

// 调整混响参数
ReverbPreset->SetReflectionScalar(1.5f);     // 增强反射
ReverbPreset->SetReverbGain(1.0f);           // 正常混响增益
ReverbPreset->SetReverbTimeModifier(1.2f);   // 略微延长混响
ReverbPreset->SetReverbBrightness(0.3f);     // 略亮

// 设置为全局混响预设
UResonanceAudioBlueprintFunctionLibrary::SetGlobalReverbPreset(ReverbPreset);
```

### 进阶用法

**使用 Resonance Audio API 进行底层空间化控制：**

```cpp
// 来源: Private/ResonanceAudioLibrary/resonance_audio/api/resonance_audio_api.h
// 通过模块获取 Resonance Audio API（底层 C++ 接口）
// 注意：以下代码展示了底层 API 的典型用法，实际集成需要通过音频线程安全地调用

// 渲染模式选择
enum RenderingMode {
    kStereoPanning = 0,          // 立体声平移（最快，无 HRTF）
    kBinauralLowQuality,         // 一阶 Ambisonics HRTF
    kBinauralMediumQuality,      // 二阶 Ambisonics HRTF
    kBinauralHighQuality,        // 三阶 Ambisonics HRTF（最高品质）
    kRoomEffectsOnly,            // 仅房间效果，无 HRTF
};

// 距离衰减模型
enum DistanceRolloffModel {
    kLogarithmic = 0,   // 对数衰减（默认，最自然）
    kLinear,             // 线性衰减
    kNone,               // 无衰减（手动控制）
};
```

**空间化设置的详细属性：**

```cpp
// 来源: Public/ResonanceAudioSpatializationSourceSettings.h
// UResonanceAudioSpatializationSourceSettings 的完整配置示例

// 空间化方法选择
SpatialSettings->SpatializationMethod = ERaSpatializationMethod::STEREO_PANNING; // 或 HRTF

// 距离衰减配置
SpatialSettings->Rolloff = ERaDistanceRolloffModel::LOGARITHMIC;
SpatialSettings->MinDistance = 100.0f;   // cm
SpatialSettings->MaxDistance = 50000.0f; // cm

// 遮挡强度（通过 Audio Volume 的遮挡系统传递）
// 数值范围 [0, inf)，0 = 无遮挡
```

## Demo 示例

一个最小可编译的自定义房间混响效果管理器：

```cpp
// ResonanceRoomEffectManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ResonanceRoomEffectManager.generated.h"

class UResonanceAudioReverbPluginPreset;
class UAudioComponent;

UCLASS(BlueprintType, Blueprintable)
class YOURPROJECT_API AResonanceRoomEffectManager : public AActor
{
    GENERATED_BODY()

public:
    AResonanceRoomEffectManager();

    UPROPERTY(EditAnywhere, Category = "Resonance|Room")
    FVector RoomDimensions = FVector(800.f, 600.f, 300.f);

    UPROPERTY(EditAnywhere, Category = "Resonance|Room")
    float ReverbTimeModifier = 1.0f;

    UPROPERTY(EditAnywhere, Category = "Resonance|Room")
    float ReflectionScalar = 1.0f;

    UPROPERTY(EditAnywhere, Category = "Resonance|Room")
    float ReverbBrightness = 0.0f;

    UPROPERTY(EditAnywhere, Category = "Resonance|Room")
    ERaMaterialName WallMaterial = ERaMaterialName::BRICK_PAINTED;

    UFUNCTION(BlueprintCallable, Category = "Resonance|Room")
    void ApplyRoomSettings();

    UFUNCTION(BlueprintCallable, Category = "Resonance|Room")
    void DisableRoomEffects();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UResonanceAudioReverbPluginPreset* ReverbPreset;
};
```

```cpp
// ResonanceRoomEffectManager.cpp
#include "ResonanceRoomEffectManager.h"
#include "ResonanceAudioReverbPluginPreset.h"
#include "ResonanceAudioBlueprintFunctionLibrary.h"

AResonanceRoomEffectManager::AResonanceRoomEffectManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AResonanceRoomEffectManager::BeginPlay()
{
    Super::BeginPlay();
    ReverbPreset = NewObject<UResonanceAudioReverbPluginPreset>();
    ApplyRoomSettings();
}

void AResonanceRoomEffectManager::ApplyRoomSettings()
{
    if (!ReverbPreset) return;

    // 启用房间效果
    ReverbPreset->SetEnableRoomEffects(true);

    // 使用 Actor 位置作为房间中心
    ReverbPreset->SetRoomPosition(GetActorLocation());
    ReverbPreset->SetRoomRotation(GetActorQuat());
    ReverbPreset->SetRoomDimensions(RoomDimensions);

    // 所有墙面使用相同材质
    TArray<ERaMaterialName> Materials;
    Materials.Init(WallMaterial, 6);
    ReverbPreset->SetRoomMaterials(Materials);

    // 设置反射和混响参数
    ReverbPreset->SetReflectionScalar(ReflectionScalar);
    ReverbPreset->SetReverbGain(1.0f);
    ReverbPreset->SetReverbTimeModifier(ReverbTimeModifier);
    ReverbPreset->SetReverbBrightness(ReverbBrightness);

    // 应用为全局混响预设
    UResonanceAudioBlueprintFunctionLibrary::SetGlobalReverbPreset(ReverbPreset);
}

void AResonanceRoomEffectManager::DisableRoomEffects()
{
    if (!ReverbPreset) return;
    ReverbPreset->SetEnableRoomEffects(false);
}
```

## 模块依赖

Build.cs 中的主要依赖关系：

| 模块 | 用途 |
|---|---|
| `ProceduralMeshComponent` | 用于直接性模式的可视化网格生成 |
| `RenderCore` | 渲染相关基础设施 |
| `RHI` | 渲染硬件接口（编辑器可视化） |

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单（非 Resonance 专属改动） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF（全局改动） |
| 2026-01-20 | `7cfdbde4` | AudioMixerDevice - Add ref count to submixes using the register/unregister API. | AudioMixer 设备为 submix 添加引用计数 |
| 2025-11-10 | `3ecbd390` | Fixed broken printf specifier strings. | 修复损坏的 printf 格式化字符串 |

### 维护评价

**⚠️ 有限维护状态**

- **创建时间**：2017 年 12 月，已超过 7 年
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，表明该插件一直处于"实验性"阶段
- **更新频率**：最近的提交大多是编译修复、代码清理和全局引擎改动，非功能性更新
- **Google 依赖**：该插件由 Google 创建和维护核心 SDK，Epic 侧仅做引擎集成。Google 的 Resonance Audio SDK 本身已不太活跃
- **已知限制**：
  - 仅支持鞋盒体（box）房间模型，不支持任意几何体
  - 混响基于频谱合成而非物理模拟，精度有限
  - 移动平台性能开销需关注（三阶 HRTF 卷积计算量大）
- **推荐程度**：适合 VR 项目快速原型和中小型项目使用。对于 AAA 级项目或需要更高级空间音频效果的场景，建议评估 UE5 原生的音频空间化方案或商业方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ResonanceAudio)
- [官方文档](https://developers.google.com/resonance-audio/develop/unreal/getting-started)
- [Google Resonance Audio 开发者主页](https://developers.google.com/resonance-audio)
- [社区支持](https://developers.google.com/resonance-audio/community/connect)