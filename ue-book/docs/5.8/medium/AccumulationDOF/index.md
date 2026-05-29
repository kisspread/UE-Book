# Accumulation Depth of Field

> Thin-lens aperture-sampled depth of field for production rendering

| 属性 | 值 |
|---|---|
| 中文名 | 累积景深 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AccumulationDOF` (Runtime), `AccumulationDOFEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AccumulationDOF) | |

## 用途

这是一个专为**影视级渲染**设计的景深插件，通过在多个光圈位置采样并累积场景渲染结果来模拟真实镜头的景深效果。其主要目的是解决传统实时景深算法中因缺少视差信息导致的视觉伪影（如错误的遮挡关系），同时尽可能保持延迟渲染的外观开发（Lookdev）特性。它并非为游戏玩法设计，渲染时间随采样数线性增加。

## 使用场景

- 你在进行电影、广告或电视节目的**后期渲染或虚拟制片**，需要比默认景深更真实的光学效果。
- 标准景深算法在复杂遮挡场景下产生明显伪影（如物体边缘光晕），需要更准确的遮挡关系。
- 你需要模拟特定镜头的光学特性，如Petzval漩涡散景、猫眼形（桶形畸变）光斑、变形宽银幕挤压或复杂的色差效果。
- 你正在使用 Movie Render Graph (MRG) 进行最终帧渲染，并希望获得高质量的景深和运动模糊。

## 蓝图用法概述

该插件主要通过后处理设置进行控制。核心节点集成为后处理体积（Post Process Volume）中的“累积景深（Accumulation DOF）”设置组。

### 核心功能

| 功能 | 说明 |
|---|---|
| **后处理设置** | 在后处理体积或摄像机设置中，通过“累积景深”类别控制所有参数。 |
| **编辑器内预览** | 在关卡视口 > 可伸缩性下拉菜单中，找到“累积景深”选项以实时预览效果。 |

### 主要可配置参数（蓝图属性）

- **采样数 (NumSamples)**：控制光圈上的采样点数量，直接影响渲染时间和质量。
- **散点大小 (Splats Size)**：控制用于填充散景的默认景深散点的大小（占光圈直径的比例），用于改善散景填充感。
- **镜头特性设置**：包括Petzval扭曲、变形挤压、球面像差、色差等高级参数。
- **自定义散景纹理**：允许使用自定义纹理作为散景形状。

## C++ 用法概述

该插件的 C++ 接口主要用于与渲染管线和 Movie Render Graph 深度集成。对于大多数用户，通过蓝图/编辑器设置进行控制即可。

### 核心集成

插件作为后处理扩展点接入 UE 的渲染管线。主要的 C++ 逻辑位于 `AccumulationDOF` 模块中，负责实现光圈采样、累积渲染和与延迟渲染通道的集成。

### 使用方式

1.  **编辑器预览**：直接在后处理体积的 Details 面板中调整参数。
2.  **MRG 渲染**：在 Movie Render Graph 中，使用 **`Accumulation Depth of Field` 渲染通道**。根据首次提交说明，应将空间采样设置为1，时间采样设置为高以获取运动模糊效果。

## Demo 示例

一个在 C++ Actor 中配置并启用累积景深后处理设置的最小示例。

```cpp
// MyCharacter.h
#pragma once
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

protected:
    virtual void BeginPlay() override;

private:
    // 用于控制累积景深的后处理组件
    UPROPERTY(VisibleAnywhere)
    class UPostProcessComponent* PostProcessComp;
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "PostProcess/PostProcessComponent.h"
// 假设 AccumulationDOF 提供了可包含的设置结构体头文件
// #include "AccumulationDOFSettings.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建并附加后处理组件
    PostProcessComp = CreateDefaultSubobject<UPostProcessComponent>(TEXT("PostProcessComp"));
    PostProcessComp->SetupAttachment(RootComponent);
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (PostProcessComp)
    {
        // 在后处理设置中启用累积景深并调整参数
        // 以下为示意代码，具体属性名称需参考插件头文件
        // FPostProcessSettings& Settings = PostProcessComp->Settings;
        // Settings.bOverride_AccumulationDOFNumSamples = true;
        // Settings.AccumulationDOFNumSamples = 256;
        // Settings.bOverride_AccumulationDOFEnable = true;
        // Settings.AccumulationDOFEnable = true;
    }
}
```

**说明**：此示例展示了如何通过后处理组件应用设置。具体的属性名和包含的头文件需要参考插件源码（例如 `AccumulationDOFSettings.h`）。在蓝图中，这些设置通常通过后处理体积的细节面板直接配置。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieRenderPipeline` | 用于与 Movie Render Graph (MRG) 集成，实现最终帧的高质量景深渲染。 |

（注意：`AccumulationDOF` 模块依赖 `PropertyEditor`，但此为编辑器插件常见依赖，已省略。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `6aedc10e` | MoviePipeline: Updated ADOF support within MRG to support high-res tiling. | 增强在 MRG 中对高分辨率分块渲染的支持。 |
| 2026-05-12 | `3af0fac2` | MoviePipeline: Added some telemetry for newly-added graph features, and existing MRQ/MRG features wh | 为 MRG 新功能添加遥测数据支持。 |
| 2026-05-12 | `67c6995d` | AccumulationDOF: Reduce default aperture NumSamples from 512 to 256 | 将默认光圈采样数从512降低至256，优化默认性能。 |
| 2026-05-12 | `657a7d63` | MoviePipeline: Removed Accumulation Depth of Field support from MRQ. ADOF support in MRQ was tempora | 从旧版 Movie Render Queue (MRQ) 中移除支持，重心转向 MRG。 |
| 2026-05-12 | `bc8a105a` | MRG: Fix lens distortion renders being over-cropped due to MRG always cropping the overscan. | 修复MRG中镜头畸变渲染被过度裁剪的BUG。 |

### 维护评价

- **活跃维护**：插件创建时间极短，处于积极开发期。最近一个月内有多次实质性功能更新和集成优化（主要是MRG相关）。
- **发展方向**：开发重点已明确从旧的MRQ转向新的Movie Render Graph (MRG)。
- **注意事项**：标记为**实验性** (`IsExperimentalVersion: true`)，且默认未启用。接口和行为可能发生变化。
- **使用建议**：如果你正在使用或计划使用 MRG 进行最终渲染，并且对景深质量有极高要求，可以尝试使用此插件。对于游戏运行时渲染，因其性能开销和实验性，不建议使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AccumulationDOF)
- [模块文档：AccumulationDOF](AccumulationDOF.md)
- [模块文档：AccumulationDOFEditor](AccumulationDOFEditor.md)