# Landmass

> 

| 属性 | 值 |
|---|---|
| 中文名 | 地形雕刻 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Landmass` (Runtime), `LandmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Landmass) | |

## 用途

Landmass 是一个用于 Unreal Engine 地形（Landscape）系统的程序化雕刻插件。它提供了一套基于画笔（Brush）的地形变形工具链，允许开发者通过材质和各种效果参数来程序化地塑造地形高度图。

核心功能包括：
- **混合模式控制**：支持 Alpha Blend、Min（仅降低）、Max（仅升高）、Additive（叠加）四种地形混合方式
- **衰减控制**：通过角度或宽度模式控制画笔边缘的过渡效果
- **丰富的画笔效果**：模糊、卷曲噪声、曲线通道、置换贴图、平滑混合、梯田效果等
- **效果组合**：所有效果可叠加组合，通过 FLandmassBrushEffectsList 统一管理

该插件主要服务于需要程序化或半程序化生成地形的工作流，例如开放世界游戏中的地形关卡设计。

## 使用场景

- 你在做一个开放世界游戏，需要基于程序化规则快速雕刻大面积地形 → 用 Landmass
- 你需要在画笔基础上叠加模糊、噪声、梯田等效果来创建自然地形特征 → 用 Landmass
- 你希望用曲线资产（Curve Float）定义河流/山谷等线性地形特征 → 用 Landmass 的 Curves 通道
- 你需要精确控制地形升降方向（仅升高/仅降低）→ 用 Landmass 的 Min/Max 混合模式

## 蓝图用法

该插件主要通过 USTRUCT 的 BlueprintReadWrite 属性在蓝图中配置参数，无独立的 BlueprintCallable 节点。

### 核心结构体

| 结构体 | 说明 | 关键属性 |
|---|---|---|
| `FLandmassTerrainCarvingSettings` | 地形雕刻总配置 | BlendMode, bInvertShape, FalloffSettings, Effects, Priority |
| `FLandmassFalloffSettings` | 画笔衰减设置 | FalloffMode, FalloffAngle, FalloffWidth, EdgeOffset, ZOffset |
| `FLandmassBrushEffectsList` | 画笔效果集合 | Blurring, CurlNoise, Displacement, SmoothBlending, Terracing |
| `FBrushEffectBlurring` | 模糊效果 | bBlurShape, Radius |
| `FBrushEffectCurlNoise` | 卷曲噪声效果 | Curl1Amount, Curl2Amount, Curl1Tiling, Curl2Tiling |
| `FBrushEffectCurves` | 曲线通道效果 | bUseCurveChannel, ElevationCurveAsset, ChannelEdgeOffset, ChannelDepth, CurveRampWidth |
| `FBrushEffectDisplacement` | 置换贴图效果 | DisplacementHeight, Texture, Midpoint, Channel, WeightmapInfluence |
| `FBrushEffectSmoothBlending` | 平滑混合效果 | InnerSmoothDistance, OuterSmoothDistance |
| `FBrushEffectTerracing` | 梯田效果 | TerraceAlpha, TerraceSpacing, TerraceSmoothness, MaskLength, MaskStartOffset |

### 枚举类型

| 枚举 | 值 | 说明 |
|---|---|---|
| `EBrushBlendType` | AlphaBlend | 影响高度图上下方向 |
| | Min | 仅降低地形 |
| | Max | 仅升高地形 |
| | Additive | 叠加混合，以 Z=0 平面为输入 |
| `EBrushFalloffMode` | Angle | 基于角度的衰减 |
| | Width | 基于宽度的衰减 |

### 使用示例（蓝图描述）

在蓝图中创建一个 `FLandmassTerrainCarvingSettings` 变量，在细节面板中配置：
1. 设置 `BlendMode` 为 `Additive`（叠加模式，保留原有细节）
2. 展开 `FalloffSettings`，设置 `FalloffMode` 为 `Width`，调整 `FalloloffWidth` 控制边缘过渡
3. 展开 `Effects`：
   - 启用 `Blurring`，设置 `Radius=4` 柔化边缘
   - 启用 `Terracing`，设置 `TerraceSpacing=512` 创建梯田效果
   - 启用 `CurlNoise`，设置 `Curl1Amount=0.5` 添加自然噪声

## C++ 用法

### 头文件引入

```cpp
#include "BrushEffectsList.h"
#include "TerrainCarvingSettings.h"
#include "FalloffSettings.h"
```

### 基本用法

创建并配置地形雕刻设置（基于源码中的结构体定义）：

```cpp
// 创建地形雕刻配置
FLandmassTerrainCarvingSettings CarvingSettings;
CarvingSettings.BlendMode = EBrushBlendType::Additive;
CarvingSettings.bInvertShape = false;
CarvingSettings.Priority = 0;

// 配置衰减
CarvingSettings.FalloffSettings.FalloffMode = EBrushFalloffMode::Width;
CarvingSettings.FalloffSettings.FalloffWidth = 0.5f;
CarvingSettings.FalloffSettings.EdgeOffset = 0.0f;

// 启用模糊效果
CarvingSettings.Effects.Blurring.bBlurShape = true;
CarvingSettings.Effects.Blurring.Radius = 4;

// 启用梯田效果
CarvingSettings.Effects.Terracing.TerraceAlpha = 0.8f;
CarvingSettings.Effects.Terracing.TerraceSpacing = 256.0f;
CarvingSettings.Effects.Terracing.TerraceSmoothness = 0.5f;
```

### 进阶用法

组合多种效果创建自然地形特征：

```cpp
// 创建一个带有噪声和置换的自然山丘效果
FLandmassTerrainCarvingSettings HillSettings;
HillSettings.BlendMode = EBrushBlendType::Max;  // 仅升高地形
HillSettings.Priority = 10;

// 使用曲线定义山丘剖面
HillSettings.Effects.Curves.bUseCurveChannel = true;
HillSettings.Effects.Curves.ChannelDepth = 200.0f;
HillSettings.Effects.Curves.CurveRampWidth = 1024.0f;
// ElevationCurveAsset 需要从内容浏览器加载
// HillSettings.Effects.Curves.ElevationCurveAsset = LoadObject<UCurveFloat>(...);

// 添加卷曲噪声增加自然感
HillSettings.Effects.CurlNoise.Curl1Amount = 0.3f;
HillSettings.Effects.CurlNoise.Curl1Tiling = 32.0f;
HillSettings.Effects.CurlNoise.Curl2Amount = 0.1f;
HillSettings.Effects.CurlNoise.Curl2Tiling = 8.0f;

// 使用置换贴图添加表面细节
HillSettings.Effects.Displacement.DisplacementHeight = 50.0f;
HillSettings.Effects.Displacement.DisplacementTiling = 256.0f;
HillSettings.Effects.Displacement.Midpoint = -128.0f;
HillSettings.Effects.Displacement.WeightmapInfluence = 0.5f;

// 平滑混合防止硬边
HillSettings.Effects.SmoothBlending.InnerSmoothDistance = 0.1f;
HillSettings.Effects.SmoothBlending.OuterSmoothDistance = 0.2f;
```

## Demo 示例

```cpp
// LandmassDemoComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TerrainCarvingSettings.h"
#include "BrushEffectsList.h"
#include "FalloffSettings.h"
#include "LandmassDemoComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API ULandmassDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    ULandmassDemoComponent();

    /** 地形雕刻配置，可在编辑器中调整 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Landmass")
    FLandmassTerrainCarvingSettings CarvingSettings;

    /** 用 Additive 模式预设创建山丘 */
    UFUNCTION(BlueprintCallable, Category = "Landmass")
    void ApplyHillPreset();

    /** 用 Min 模式预设创建山谷 */
    UFUNCTION(BlueprintCallable, Category = "Landmass")
    void ApplyValleyPreset();
};
```

```cpp
// LandmassDemoComponent.cpp
#include "LandmassDemoComponent.h"

ULandmassDemoComponent::ULandmassDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    ApplyHillPreset();
}

void ULandmassDemoComponent::ApplyHillPreset()
{
    CarvingSettings.BlendMode = EBrushBlendType::Additive;
    CarvingSettings.bInvertShape = false;
    CarvingSettings.Priority = 0;

    // 宽度衰减，边缘柔和
    CarvingSettings.FalloffSettings.FalloffMode = EBrushFalloffMode::Width;
    CarvingSettings.FalloffSettings.FalloffWidth = 0.3f;
    CarvingSettings.FalloffSettings.ZOffset = 0.0f;

    // 轻微模糊
    CarvingSettings.Effects.Blurring.bBlurShape = true;
    CarvingSettings.Effects.Blurring.Radius = 2;

    // 添加自然噪声
    CarvingSettings.Effects.CurlNoise.Curl1Amount = 0.2f;
    CarvingSettings.Effects.CurlNoise.Curl2Amount = 0.1f;
}

void ULandmassDemoComponent::ApplyValleyPreset()
{
    CarvingSettings.BlendMode = EBrushBlendType::Min;
    CarvingSettings.bInvertShape = false;
    CarvingSettings.Priority = 5;

    CarvingSettings.FalloffSettings.FalloffMode = EBrushFalloffMode::Angle;
    CarvingSettings.FalloffSettings.FalloffAngle = 45.0f;

    // 梯田效果
    CarvingSettings.Effects.Terracing.TerraceAlpha = 0.5f;
    CarvingSettings.Effects.Terracing.TerraceSpacing = 128.0f;
    CarvingSettings.Effects.Terracing.TerraceSmoothness = 0.3f;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Landscape` | 地形系统核心模块，Landmass 的画笔效果直接作用于 Landscape 高度图 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移为 UE_LOGF 新格式 |
| 2025-08-27 | `5ac9e159` | Landscape - Deprecating non-edit layer based landscapes | 废弃非编辑图层的地形系统 |
| 2025-05-29 | `8bd3e004` | Fix blutility module not guaranteed to be loaded when Landmass engine plugin compiles its content de | 修复 Blutility 模块加载时序问题 |
| 2025-05-01 | `0faa16c2` | Landscape Editor - Making BPBrushBase non placeable to ensure brushes are only added from Landscape | 限制 BPBrushBase 不可直接放置 |
| 2025-03-07 | `1a599460` | Remove codepaths related to HasNormalCaptureBPBrushLayer. No longer required with new landscape bor | 移除旧版画笔图层相关代码 |

### 维护评价

Landmass 插件自 2019 年创建以来一直处于实验性状态（`IsBetaVersion=true`，`EnabledByDefault=false`）。近期的提交主要是跟随 Landscape 系统的整体重构进行适配性更新（废弃旧图层、清理旧代码路径），而非 Landmass 本身的功能增强。

**关键风险**：
- 2025 年 8 月的提交标记了 `Deprecating non-edit layer based landscapes`，表明旧版地形工作流正在被淘汰，Landmass 依赖的底层 API 可能进一步变动
- 插件仍为实验性，Epic 尚未将其标记为稳定可用
- `Installed=false` 表明默认不会随引擎安装，需要手动启用

**结论**：⚠️ 该插件仍在维护中但功能稳定无重大更新，适合作为学习地形程序化雕刻的参考。生产环境使用需谨慎，建议关注 Landscape 系统的整体演进方向。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Landmass)
- [官方文档]()（无）