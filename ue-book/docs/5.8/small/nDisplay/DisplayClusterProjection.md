# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染投影 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图API、配置字符串） |
| 模块 | `DisplayClusterProjection` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`DisplayClusterProjection` 是 nDisplay 插件的核心模块之一，负责实现多屏幕/多通道渲染中的**投影策略**。它解决的核心问题是：如何将单个 UE 场景的渲染内容，通过不同的**几何校正**和**边缘融合**技术，正确地映射到由多台 PC（集群节点）驱动的多块物理屏幕（如环幕、CAVE 系统、异形幕等）上。该模块通过抽象出统一的 `IDisplayClusterProjectionPolicy` 接口，集成了多种第三方或原生的校准方案（如 MPCDI、EasyBlend、VIOSO、Domeprojection 等），使得 nDisplay 可以适配各种复杂的投影硬件和校准软件，实现精准的多屏视觉拼接。

## 使用场景

- **虚拟制片**：在 LED Volume（如 VP Stage）中，为摄像机视锥体周围的 LED 面板提供精确的投影校准。
- **大型环幕影院或飞行模拟器**：校准多个投影仪，确保画面在曲面屏幕上无缝拼接和融合。
- **CAVE 沉浸式系统**：为多个投射到房间墙壁和地面上的画面应用正确的几何变换。
- **任何需要多通道、多 GPU 渲染并应用外部硬件或软件校准的场合**。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CameraPolicySetCamera` | 为指定的视口（Viewport）设置一个相机组件作为 `camera` 投影策略的来源，并可设置 FOV 缩放因子。 | `UDisplayClusterProjectionBlueprintLib` |

### 使用示例（蓝图描述）

1.  从 **“nDisplay|Projection”** 分类下，找到并拖放 **“Set camera”** 节点。
2.  将其 **“ViewportId”** 引脚连接到你的 nDisplay 视口 ID（字符串）。
3.  将 **“NewCamera”** 引脚连接到场景中你希望用作投影来源的 `UCameraComponent` 引用。
4.  可选地调整 **“FOVMultiplier”** 值来改变最终投影的视场角。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterProjection.h"
```

### 基本用法

获取 `DisplayClusterProjection` 模块接口，并查询系统支持哪些投影策略。

```cpp
// (来源: IDisplayClusterProjection.h)
if (IDisplayClusterProjection::IsAvailable())
{
    IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();

    // 获取所有支持的投影策略类型列表
    TArray<FString> SupportedProjectionTypes;
    ProjectionModule.GetSupportedProjectionTypes(SupportedProjectionTypes);
    
    for (const FString& ProjType : SupportedProjectionTypes)
    {
        UE_LOG(LogTemp, Log, TEXT("Supported Projection Policy: %s"), *ProjType);
    }
}
```

### 进阶用法

为特定的投影策略工厂创建一个投影策略实例。这通常在 nDisplay 内部的视口管理中使用，但了解其机制有助于扩展。

```cpp
// (来源: IDisplayClusterProjection.h, DisplayClusterProjectionPolicyFactoryBase.h)
if (IDisplayClusterProjection::IsAvailable())
{
    IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();
    
    // 以 MPCDI 策略为例
    const FString PolicyType = TEXT("mpcdi");
    TSharedPtr<IDisplayClusterProjectionPolicyFactory> Factory = ProjectionModule.GetProjectionFactory(PolicyType);
    
    if (Factory.IsValid())
    {
        // 假设你拥有一个 FDisplayClusterConfigurationProjection 配置对象
        // （通常从 .ndisplay 配置文件解析而来）
        // FDisplayClusterConfigurationProjection* Config = ...;
        // TSharedPtr<IDisplayClusterProjectionPolicy> NewPolicy = Factory->Create(PolicyType + TEXT("_0"), Config);
    }
}
```

## Demo 示例

一个最简单的示例，演示如何访问投影模块。

```cpp
// MyNDisplayProjectionUser.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyNDisplayProjectionUser.generated.h"

UCLASS()
class UMyNDisplayProjectionUser : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    void LogProjectionInfo();
};

// MyNDisplayProjectionUser.cpp
#include "MyNDisplayProjectionUser.h"
#include "IDisplayClusterProjection.h"

void UMyNDisplayProjectionUser::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    LogProjectionInfo();
}

void UMyNDisplayProjectionUser::LogProjectionInfo()
{
    if (!IDisplayClusterProjection::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DisplayClusterProjection module is not loaded."));
        return;
    }

    IDisplayClusterProjection& ProjModule = IDisplayClusterProjection::Get();
    TArray<FString> Types;
    ProjModule.GetSupportedProjectionTypes(Types);
    
    UE_LOG(LogTemp, Log, TEXT("nDisplay supports %d projection policies:"), Types.Num());
    for (const FString& Type : Types)
    {
        UE_LOG(LogTemp, Log, TEXT("  - %s"), *Type);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。
*注意：该插件整体包含多个模块，`DisplayClusterProjection` 模块内部依赖 `UnrealEd`，但这属于编辑器功能，对于纯运行时使用不影响。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | nDisplay 支持 EXR 多层图像输出，用于 Movie Graph。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 优化电影渲染管线中的 Alpha 通道融合处理。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中相机命名和 MPCDI 着色器的 Alpha 通道问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码时未使用自定义 DisplayGamma 的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时的画面闪烁问题。 |

### 维护评价

- **创建时间**：7年前（2018年）。
- **近期活动**：非常活跃，最近一周内有多次实质性更新，主要涉及电影渲染管线集成、Shader 修复和输出功能增强。
- **维护状态**：**积极维护中**。作为 Unreal 的虚拟制片和大型沉浸式体验的关键支柱模块，由 Epic Games 持续开发和优化。
- **已知限制**：作为一个功能复杂且深度集成硬件的模块，其配置和使用门槛较高，需要 nDisplay 的整体配置知识。部分第三方投影策略（如 VIOSO、EasyBlend）依赖于外部 SDK 的兼容性。
- **推荐使用**：**强烈推荐**用于任何需要专业级多屏幕校准和集群渲染的项目。对于单机或多视图基础需求，可使用 UE 内置的 nDisplay 功能；但对于复杂的物理投影环境，`DisplayClusterProjection` 模块是必不可少的。注意，该插件默认**未启用**，需要在插件设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：（本插件的 .uplugin 中未提供 DocsURL，请参考 Unreal Engine 官方文档站中关于 nDisplay 和虚拟制片的章节）