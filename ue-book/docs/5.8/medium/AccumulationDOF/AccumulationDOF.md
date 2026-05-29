# Accumulation Depth of Field

> Thin-lens aperture-sampled depth of field for production rendering（照抄，不翻译）

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

AccumulationDOF 是一种面向影视级渲染的景深解决方案，通过薄透镜模型在光圈平面上多次采样并累积渲染结果，从根本上解决了传统实时 DOF 因缺少视差信息而产生的常见伪影（如背景边缘的锯齿、光斑不连贯等），同时保留了延迟渲染管线的 LookDev 一致性。

核心原理：对每个光圈采样点计算独立的离轴投影矩阵，分别渲染场景，然后使用 GPU shader 将所有采样结果加权累积，最终归一化输出。渲染时间与采样数成线性关系，因此仅适合离线/预览场景，不适合实时游戏玩法。

**主要特色**：
- Petzval 旋涡焦外（Swirly Bokeh）
- 猫眼效应（桶形暗角 / Cat's Eye）
- 变形压缩因子（Anamorphic Squeeze）
- 多频段横向色差（Multi-band Lateral CA）
- 多频段轴向色差（Multi-band Axial CA）
- 球差（Spherical Aberration）和彗差（Coma Aberration）
- 自定义散景纹理（Bokeh Texture）
- 光圈叶片形状模拟（圆形 / 直刃 / 圆刃）

## 使用场景

- 你需要为电影/广告级 CG 镜头渲染真实的浅景深效果 → 使用此插件的 MRG（Movie Graph）渲染通道
- 你在编辑器中需要预览高级 DOF 效果 → 在 Level Viewport 的 Scalability 菜单中启用 Accumulation DOF
- 标准引擎 DOF 无法满足你的视觉要求（如需要真实的散景光斑形状、色差等）→ 使用此插件
- 你在使用 CineCameraActor 进行影视制作 → 将 AccumulationDOFComponent 附加到相机上进行配置

## 蓝图用法

### 核心组件：AccumulationDOFComponent

将 `UAccumulationDOFComponent` 附加到 CineCameraActor 上即可配置景深渲染参数。

#### 基础设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `NumSamples` | 光圈采样数量，越多质量越高但耗时越长（默认 256） | `UAccumulationDOFComponent` |
| `DOFSplatSize` | DOF 扇片大小占主光圈直径的比例（0.125 = 1/8，0 = 禁用） | `UAccumulationDOFComponent` |
| `bEnableMotionBlur` | 是否在累积 DOF 结果上启用运动模糊 | `UAccumulationDOFComponent` |
| `SamplingPattern` | 采样模式：Halton / Golden Hexaweb / Vogel Spiral | `UAccumulationDOFComponent` |

#### 散景（Bokeh）设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BokehTexture` | 自定义散景纹理（应为线性空间，可带 Alpha 通道） | `UAccumulationDOFComponent` |
| `bEnableBokehTexture` | 是否启用自定义散景纹理 | `UAccumulationDOFComponent` |
| `WeightChannel` | 散景纹理权重通道：Alpha / Luminance | `UAccumulationDOFComponent` |
| `TintStrength` | 散景着色强度 (0.0 - 1.0) | `UAccumulationDOFComponent` |
| `BokehEdgeSoftness` | 散景边缘柔化程度 (0.0 - 1.0) | `UAccumulationDOFComponent` |

#### 色差设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AxialChromaticAberrationIntensity` | 轴向色差强度（占焦点距离百分比） | `UAccumulationDOFComponent` |
| `AxialChromaticAberrationNumBands` | 轴向色差频段数 (3 - 19) | `UAccumulationDOFComponent` |
| `bSpectralLateralChromaticAberration` | 启用光谱横向色差（取代引擎默认横向色差） | `UAccumulationDOFComponent` |

#### 单色像差设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SphericalAberration` | 球差系数 (Seidel W040)，单位 cm | `UAccumulationDOFComponent` |
| `ComaAberration` | 彗差强度 (Seidel W131)，0.0 - 1.0 | `UAccumulationDOFComponent` |

#### MovieGraph 修改器节点

在 MRG 的 Graph 中，可以使用 `UMovieGraphAccumulationDOFModifierNode` 覆盖场景中所有相机的 AccumulationDOF 组件设置：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableAccumulationDepthOfField` | 启用/禁用累积景深组件 | `UMovieGraphAccumulationDOFModifierNode` |
| `NumSamples` | 覆盖采样数量 | `UMovieGraphAccumulationDOFModifierNode` |
| `DOFSplatSize` | 覆盖扇片大小 | `UMovieGraphAccumulationDOFModifierNode` |

### 使用示例（蓝图描述）

1. **基本设置**：在场景中选择 CineCameraActor → Add Component → 添加 "Accumulation DOF" 组件 → 在 Details 面板中调整 NumSamples、DOFSplatSize 等参数。

2. **编辑器预览**：打开 Level Viewport → 点击 Viewport 工具栏的 Scalability & Performance 下拉菜单 → 启用 "Accumulation DOF"。渲染会逐步累积，底部会显示进度条。

3. **MovieGraph 渲染**：在 MRG Graph 中，将 "Accumulation DOF" 渲染通道添加到 Deferred Renderer 节点 → 设置 Spatial Samples 为 1，Temporal Samples 为你需要的时间采样数 → 该通道会自动从绑定的 CineCamera 读取镜头参数和 AccumulationDOFComponent 配置。

## C++ 用法

### 头文件引入

```cpp
#include "AccumulationDOFComponent.h"
#include "AccumulationDOFTypes.h"
#include "MovieGraphAccumulationDOFPass.h"
```

### 基本用法：读取组件参数

从 CineCameraActor 上获取 AccumulationDOFComponent 并读取/修改设置：

```cpp
// 来源: Public/AccumulationDOFComponent.h
UCineCameraActor* CineCam = /* 获取 CineCameraActor */;
UAccumulationDOFComponent* DOFComponent = CineCam->FindComponentByClass<UAccumulationDOFComponent>();
if (!DOFComponent)
{
    DOFComponent = NewObject<UAccumulationDOFComponent>(CineCam);
    DOFComponent->RegisterComponent();
}

// 配置参数
DOFComponent->NumSamples = 512;
DOFComponent->DOFSplatSize = 0.125f;
DOFComponent->bEnableMotionBlur = false;
DOFComponent->SamplingPattern = EApertureSamplingPattern::Hexaweb;
DOFComponent->bEnableBokehTexture = false;
DOFComponent->AxialChromaticAberrationIntensity = 5.0f;
DOFComponent->SphericalAberration = 0.0f;
```

### 进阶用法：ApertureSampler 直接控制

`UApertureSampler` 提供了完整的光圈采样管线控制，适合需要精细控制渲染流程的场景：

```cpp
// 来源: Private/Rendering/ApertureSampler.h
#include "Rendering/ApertureSampler.h"

// 创建采样器
UApertureSampler* Sampler = NewObject<UApertureSampler>();

// 配置采样参数
AccumulationDOF::FApertureSamplerConfig Config;
Config.NumSamples = 1024;
Config.DOFSplatSize = 0.125f;
// ... 设置其他配置参数

// 配置相机状态
AccumulationDOF::FApertureSamplerCameraState CameraState;
// ... 从 CineCameraComponent 提取参数

// 初始化
Sampler->Initialize(Config, CameraState);

// 方式一：阻塞式渲染所有采样
Sampler->RenderAllSamples();

// 方式二：分帧渲染（预览模式下可增量更新）
while (!Sampler->IsComplete())
{
    Sampler->RenderAmortizedSamples();
    // 可在此处更新 UI 进度
    const auto& Progress = Sampler->GetProgress();
    UE_LOG(LogAccumulationDOF, Log, TEXT("Progress: %d/%d samples"), 
           Progress.CurrentSample, Progress.ActualNumSamples);
}

// 获取结果
UTextureRenderTarget2D* Result = Sampler->GetAccumulatedResult();

// 清理
Sampler->Shutdown();
```

### 进阶用法：带后期处理的渲染

```cpp
// 来源: Private/Rendering/ApertureSampler.h
// 渲染完成后，注入后期处理管线
UTextureRenderTarget2D* OutputRT = /* 输出渲染目标 */;
Sampler->RenderWithPostProcessing(
    OutputRT,
    false,   // bAllowSceneFringe - 禁用引擎默认横向色差（使用插件自带的光谱色差）
    1.0f,    // ProgressBarFraction - 显示完整进度条
    0.0f     // Overscan - 无过扫描裁剪
);
```

### 进阶用法：光圈采样模式枚举

```cpp
// 来源: Public/AccumulationDOFTypes.h
EApertureSamplingPattern::Halton   // Halton 序列 + Shirley-Chiu 圆盘映射
EApertureSamplingPattern::Hexaweb  // 金色六角蛛网（推荐，散景最均匀）
EApertureSamplingPattern::Vogel    // Vogel 螺旋
```

### 进阶用法：时间历史模式

```cpp
// 来源: Public/AccumulationDOFTypes.h
ETemporalHistoryMode::AllSamplesUpdate   // 所有采样都更新时序历史（Lumen/TAA）
ETemporalHistoryMode::LastSampleOnly     // 仅最后一个采样更新（推荐）
ETemporalHistoryMode::FirstSampleOnly    // 仅第一个采样更新
ETemporalHistoryMode::NoSamplesUpdate    // 不更新历史（用于对比测试）
```

## Demo 示例

一个最小的编辑器内预览示例——在 Tick 中逐步累积渲染景深并将结果显示到纹理：

**AccumulationDOFDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AccumulationDOFComponent.h"
#include "AccumulationDOFDemo.generated.h"

class UApertureSampler;
class UTextureRenderTarget2D;

UCLASS()
class AAccumulationDOFDemo : public AActor
{
    GENERATED_BODY()

public:
    AAccumulationDOFDemo();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** 目标 CineCamera Actor（必须包含 AccumulationDOFComponent） */
    UPROPERTY(EditAnywhere, Category = "DOF Demo")
    AActor* TargetCamera = nullptr;

    /** 输出渲染目标（用于显示结果） */
    UPROPERTY(VisibleAnywhere, Category = "DOF Demo")
    TObjectPtr<UTextureRenderTarget2D> OutputRT;

private:
    UPROPERTY(Transient)
    TObjectPtr<UApertureSampler> Sampler;

    bool bRenderingStarted = false;
};
```

**AccumulationDOFDemo.cpp**
```cpp
#include "AccumulationDOFDemo.h"
#include "Rendering/ApertureSampler.h"
#include "AccumulationDOFComponent.h"
#include "Engine/TextureRenderTarget2D.h"
#include "CineCameraComponent.h"

AAccumulationDOFDemo::AAccumulationDOFDemo()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AAccumulationDOFDemo::BeginPlay()
{
    Super::BeginPlay();

    // 创建输出渲染目标
    OutputRT = NewObject<UTextureRenderTarget2D>(this);
    OutputRT->InitAutoFormat(1920, 1080);
    OutputRT->UpdateResourceImmediate(true);

    // 创建采样器
    Sampler = NewObject<UApertureSampler>();

    // 配置（实际项目中应从 AccumulationDOFComponent 和 CineCameraComponent 提取）
    AccumulationDOF::FApertureSamplerConfig Config;
    Config.NumSamples = 256;
    Config.DOFSplatSize = 0.125f;

    AccumulationDOF::FApertureSamplerCameraState CameraState;
    // ... 从相机提取参数 ...

    if (Sampler->Initialize(Config, CameraState))
    {
        // 设置进度回调
        Sampler->SetOnProgress([](const AccumulationDOF::FApertureSamplerProgress& Progress)
        {
            UE_LOG(LogTemp, Log, TEXT("DOF Progress: %d/%d"), 
                   Progress.CurrentSample, Progress.ActualNumSamples);
        });

        // 设置完成回调
        Sampler->SetOnComplete([this]()
        {
            UE_LOG(LogTemp, Log, TEXT("DOF Accumulation Complete!"));
        });

        bRenderingStarted = true;
    }
}

void AAccumulationDOFDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!bRenderingStarted || !Sampler) return;

    if (!Sampler->IsComplete())
    {
        // 分帧累积渲染
        Sampler->RenderAmortizedSamples();

        // 拷贝当前结果到输出 RT 用于预览
        Sampler->CopyToOutput(OutputRT, /* bDrawProgress */ true);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieRenderPipeline` | Movie Graph 渲染通道集成（MRG） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `6aedc10e` | MoviePipeline: Updated ADOF support within MRG to support high-res tiling. | MRG 中新增高分辨率分块渲染支持 |
| 2026-05-12 | `3af0fac2` | MoviePipeline: Added some telemetry for newly-added graph features, and existing MRQ/MRG features | 新增 MRG 图形特性遥测数据收集 |
| 2026-05-12 | `67c6995d` | AccumulationDOF: Reduce default aperture NumSamples from 512 to 256 | 将默认采样数从 512 降至 256 |
| 2026-05-12 | `657a7d63` | MoviePipeline: Removed Accumulation Depth of Field support from MRQ. ADOF support in MRQ was temporary | 移除对旧版 MRQ 的支持，仅保留 MRG 集成 |
| 2026-05-12 | `bc8a105a` | MRG: Fix lens distortion renders being over-cropped due to MRG always cropping the overscan. | 修复镜头畸变渲染被过度裁剪的 bug |

### 维护评价

- **状态**：🆕 活跃开发中（创建仅约 4 个月）
- **实验性**：`.uplugin` 中 `IsExperimentalVersion=true`，`IsInstalled=false`，需手动启用
- **活跃度**：近一周内有多次实质性功能更新（分块渲染支持、MRQ→MRG 迁移、默认参数调优），开发非常活跃
- **集成方向**：已从临时的 MRQ 支持迁移到正式的 Movie Graph 集成，方向明确
- **已知限制**：光圈渲染尚未跨时间采样分摊（Aperture renders are not currently amortized across temporal samples）；AA 和运动模糊仍在改进中
- **平台支持**：仅 Mac/Win64/Linux，不支持移动端
- **推荐**：适合影视级渲染使用，但注意仍为实验性功能，API 可能变动。推荐配合 Movie Graph 使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AccumulationDOF)
- 官方文档（暂无）