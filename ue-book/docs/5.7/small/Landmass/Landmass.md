# Landmass

> （描述为空）

|属性|值|
|---|---|
|中文名|地形雕刻|
|分类|Other|
|默认启用|❌ 否|
|包含内容|❌ 无|
|模块|`Landmass` (Runtime), `LandmassEditor` (Editor)|
|实验性|⚠️ 是|
|创建时间|2025-02-13|
|年龄标签|🆕（约 1 年）|
|[源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Landmass)||

---

## 用途

Landmass 插件为 Unreal Engine 的 Landscape（地形）系统提供了一组可蓝图编辑的结构体和枚举，用于定义雕刻笔刷的效果参数。它本身不包含任何执行逻辑，而是作为数据定义层，被 Landscape 编辑器的笔刷系统消费。通过该插件，开发者可以直接在蓝图中配置笔刷的混合模式、衰减方式、模糊、卷曲噪声、位移贴图等效果，实现精细的地形雕刻控制。

---

## 使用场景

- 在 Landscape 编辑器中制作山谷、山脉、河床等复杂地形，需要精确控制笔刷的抬升/下凹范围、边缘过渡和纹理细节。
- 需要程序化或半程序化生成地形，通过蓝图组合多种笔刷效果（如模糊边缘后叠加位移）。
- 自定义地形雕刻工具，利用暴露的结构体快速构建笔刷效果预设。

---

## 蓝图用法

本模块的所有核心结构体均标记为 `BlueprintType`，可在蓝图中创建、编辑和传递。它们共同构成一道笔刷的完整配置。

### 核心数据结构

|结构体/枚举|说明|关键属性|
|---|---|---|
|`FLandmassTerrainCarvingSettings`|笔刷整体设置，包含混合模式、形状反转、衰减与效果列表|`BlendMode`, `bInvertShape`, `FalloffSettings`, `Effects`, `Priority`|
|`EBrushBlendType`|材质混合模式：`AlphaBlend`（上下同时）、`Min`（仅降低）、`Max`（仅抬升）、`Additive`（叠加，以 Z=0 为基准）|–|
|`FLandmassFalloffSettings`|笔刷边缘衰减设置|`FalloffMode`（角度/宽度）、`FalloffAngle`、`FalloffWidth`、`EdgeOffset`、`ZOffset`|
|`EBrushFalloffMode`|衰减模式：`Angle`（按坡度角）、`Width`（按水平宽度）|–|
|`FLandmassBrushEffectsList`|笔刷效果组合，包含四个子效果|`Blurring`, `CurlNoise`, `Curves`, `Displacement`|
|`FBrushEffectBlurring`|形状模糊效果|`bBlurShape`（启用）、`Radius`（模糊半径）|
|`FBrushEffectCurlNoise`|卷曲噪声（制造蜿蜒、侵蚀感）|`Curl1Amount`、`Curl2Amount`、`Curl1Tiling`、`Curl2Tiling`|
|`FBrushEffectCurves`|曲线通道（沿笔刷形状的高度曲线）|`bUseCurveChannel`, `ElevationCurveAsset`, `ChannelEdgeOffset`, `ChannelDepth`, `CurveRampWidth`|
|`FBrushEffectDisplacement`|位移贴图偏移|`DisplacementHeight`、`DisplacementTiling`、`Texture`（贴图）、`Midpoint`、`Channel`、`WeightmapInfluence`|

### 使用示例（蓝图描述）

1. **创建笔刷配置**：在蓝图中新建一个 `FLandmassTerrainCarvingSettings` 变量，并设置 `BlendMode = Max`（仅抬升地形）。
2. **配置衰减**：展开 `FalloffSettings`，设置 `FalloffMode = Width`、`FalloffWidth = 500`，使笔刷从中心到边缘平滑过渡 500 单位。
3. **添加模糊**：展开 `Effects.Blurring`，勾选 `bBlurShape = true`，`Radius = 4`，使雕刻形状边缘柔化。
4. **应用到位移**：展开 `Effects.Displacement`，指定一个 `Texture`，设置 `DisplacementHeight = 100`，以纹理灰度驱动额外高度变化。
5. **传递给地形笔刷**：将此结构体通过 Landscape 编辑器的自定义笔刷接口（通常由 `LandmassEditor` 模块提供）应用到地形操作。

---

## C++ 用法

### 头文件引入

```cpp
#include "TerrainCarvingSettings.h"
#include "FalloffSettings.h"
#include "BrushEffectsList.h"
```

### 基本用法

创建并填充笔刷设置（来源：`Engine/Plugins/Experimental/Landmass/Source/Runtime/Public/TerrainCarvingSettings.h`）：

```cpp
FLandmassTerrainCarvingSettings BrushSettings;

// 混合模式：仅抬升地形
BrushSettings.BlendMode = EBrushBlendType::Max;

// 衰减：角度模式，30° 内完全影响，之后平滑衰减
BrushSettings.FalloffSettings.FalloffMode = EBrushFalloffMode::Angle;
BrushSettings.FalloffSettings.FalloffAngle = 30.0f;
BrushSettings.FalloffSettings.EdgeOffset = 0.0f;
BrushSettings.FalloffSettings.ZOffset = 0.0f;

// 启用形状模糊
BrushSettings.Effects.Blurring.bBlurShape = true;
BrushSettings.Effects.Blurring.Radius = 2;

// 卷曲噪声 - 制造河流蜿蜒效果
BrushSettings.Effects.CurlNoise.Curl1Amount = 50.0f;
BrushSettings.Effects.CurlNoise.Curl2Amount = 20.0f;
BrushSettings.Effects.CurlNoise.Curl1Tiling = 8.0f;
BrushSettings.Effects.CurlNoise.Curl2Tiling = 2.0f;

// 优先级（影响多个笔刷叠加时的顺序）
BrushSettings.Priority = 10;
```

### 进阶用法

创建一个自定义笔刷效果预设工厂（组合 `FLandmassTerrainCarvingSettings` 供重复使用）：

```cpp
#include "TerrainCarvingSettings.h"

class FBrushPresetFactory
{
public:
    static FLandmassTerrainCarvingSettings CreateRiverBrush()
    {
        FLandmassTerrainCarvingSettings Settings;
        Settings.BlendMode = EBrushBlendType::Min;            // 仅降低地形（挖河床）
        Settings.bInvertShape = false;
        
        // 宽衰减
        Settings.FalloffSettings.FalloffMode = EBrushFalloffMode::Width;
        Settings.FalloffSettings.FalloffWidth = 2000.0f;
        
        // 卷曲噪声模拟蜿蜒
        Settings.Effects.CurlNoise.Curl1Amount = 100.0f;
        Settings.Effects.CurlNoise.Curl2Amount = 40.0f;
        
        // 轻微模糊边缘
        Settings.Effects.Blurring.bBlurShape = true;
        Settings.Effects.Blurring.Radius = 3;
        
        Settings.Priority = 20;
        return Settings;
    }

    static FLandmassTerrainCarvingSettings CreateMountainBrush()
    {
        FLandmassTerrainCarvingSettings Settings;
        Settings.BlendMode = EBrushBlendType::Max;            // 仅抬升（造山）
        Settings.FalloffSettings.FalloffMode = EBrushFalloffMode::Angle;
        Settings.FalloffSettings.FalloffAngle = 45.0f;
        Settings.Effects.Blurring.bBlurShape = true;
        Settings.Effects.Blurring.Radius = 1;                 // 锐利边缘
        Settings.Priority = 5;
        return Settings;
    }
};
```

---

## Demo 示例

以下是一个完整的 C++ 类，演示如何在 Actor 中创建并输出一个笔刷配置（最小可编译）。需要将文件放置在包含 Landmass 模块依赖的项目中。

**DemoActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TerrainCarvingSettings.h"
#include "DemoActor.generated.h"

UCLASS(Blueprintable)
class ADemoActor : public AActor
{
    GENERATED_BODY()

public:
    ADemoActor();

    /** 创建并返回一个谷地雕刻笔刷配置 */
    UFUNCTION(BlueprintCallable, Category = "Landmass Demo")
    FLandmassTerrainCarvingSettings CreateValleyBrush() const;

    /** 创建并返回一个河流雕刻笔刷配置 */
    UFUNCTION(BlueprintCallable, Category = "Landmass Demo")
    FLandmassTerrainCarvingSettings CreateRiverBrush() const;
};
```

**DemoActor.cpp**

```cpp
#include "DemoActor.h"

ADemoActor::ADemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

FLandmassTerrainCarvingSettings ADemoActor::CreateValleyBrush() const
{
    FLandmassTerrainCarvingSettings Settings;
    Settings.BlendMode = EBrushBlendType::AlphaBlend;
    Settings.bInvertShape = false;

    Settings.FalloffSettings.FalloffMode = EBrushFalloffMode::Width;
    Settings.FalloffSettings.FalloffWidth = 1500.0f;
    Settings.FalloffSettings.EdgeOffset = 0.0f;
    Settings.FalloffSettings.ZOffset = 0.0f;

    // 轻微模糊
    Settings.Effects.Blurring.bBlurShape = true;
    Settings.Effects.Blurring.Radius = 2;

    // 卷曲噪声模拟山谷蜿蜒
    Settings.Effects.CurlNoise.Curl1Amount = 30.0f;
    Settings.Effects.CurlNoise.Curl2Amount = 10.0f;
    Settings.Effects.CurlNoise.Curl1Tiling = 4.0f;
    Settings.Effects.CurlNoise.Curl2Tiling = 1.5f;

    Settings.Priority = 1;
    return Settings;
}

FLandmassTerrainCarvingSettings ADemoActor::CreateRiverBrush() const
{
    FLandmassTerrainCarvingSettings Settings;
    Settings.BlendMode = EBrushBlendType::Min;
    Settings.bInvertShape = false;

    Settings.FalloffSettings.FalloffMode = EBrushFalloffMode::Width;
    Settings.FalloffSettings.FalloffWidth = 800.0f;

    // 大卷曲噪声产生蜿蜒
    Settings.Effects.CurlNoise.Curl1Amount = 80.0f;
    Settings.Effects.CurlNoise.Curl2Amount = 30.0f;
    Settings.Effects.CurlNoise.Curl1Tiling = 6.0f;
    Settings.Effects.CurlNoise.Curl2Tiling = 2.0f;

    Settings.Effects.Blurring.bBlurShape = true;
    Settings.Effects.Blurring.Radius = 3;

    Settings.Priority = 2;
    return Settings;
}
```

构建后，可以在蓝图中调用 `CreateValleyBrush` 或 `CreateRiverBrush` 获取配置，再传递给 Landscape 编辑器的自定义笔刷函数（该函数由 `LandmassEditor` 模块提供，不在本文档讨论范围）。

---

## 模块依赖

|模块|用途|
|---|---|
|无特殊依赖（仅标准 Core/Engine/Slate 等）|Landmass 运行时模块只定义数据结构，不依赖其他模块。|

> **注意**：`LandmassEditor` 模块依赖于 `Landmass`、`Landscape`、`Blutility` 等，但这些是编辑器侧需求。

---

## 维护状态

### 近期更新

- 2025-08-27 `5ac9e159` Landscape - Deprecating non-edit layer based landscapes
- 2025-05-29 `8bd3e004` Fix blutility module not guaranteed to be loaded when Landmass engine plugin compiles its content de
- 2025-05-01 `0faa16c2` Landscape Editor - Making BPBrushBase non placeable to ensure brushes are only added from Landscape 
- 2025-03-07 `1a599460` Remove codepaths related to HasNormalCaptureBPBrushLayer. No longer required with new landscape bor
- 2025-02-13 `ec3fb596` Replaced `IsValid(this)` under the rest of Engine/

### 维护评价

- **创建时间**：2025-02-13，至今约 8 个月。
- **更新频率**：平均每月约 1 次提交，但 2025-08 之后未见新提交（截至当前）。
- **内容**：主要是配合 Landscape 系统升级和修复编译问题，非功能性增强。
- **状态**：该插件仍标记为实验性（`IsBetaVersion=true`），且近期有废弃非编辑图层景观的改动，可能未来会有较大的 API 调整或整合。
- **推荐使用**：适合需要自定义地形雕刻的开发者使用，但需注意其实验性状态，可能有后续变动。建议搭配 Landscape 编辑器的官方文档使用。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Landmass)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/landscape-terrain-editor)（Landscape 编辑器，其中涉及笔刷效果部分）