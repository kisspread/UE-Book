# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群投影 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源、材质模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途
nDisplay 是 Unreal Engine 中用于构建大型沉浸式可视化和虚拟制作环境的高级插件。它的核心功能是**将 Unreal Engine 的渲染画面同步、无损地输出到多个物理显示设备上**，这些设备通常由多台联网的 PC（集群）驱动。与简单的多显示器扩展不同，nDisplay 专注于解决以下专业问题：
- **精确几何校正与边缘融合**：支持对非平面（如曲面屏、穹顶）和多平面屏幕组合进行精确的几何扭曲（Warp）和边缘融合（Blend），以消除投影缝隙并实现无缝画面。
- **多通道立体渲染**：支持为立体（Stereo）显示（如 VR 头显、被动式立体投影）独立渲染左右眼视图。
- **集群同步**：确保集群中所有 PC 的渲染状态（时间、动画、物理等）完全同步，避免画面撕裂或不同步。
- **灵活的投影策略**：通过可扩展的“投影策略”（Projection Policy）系统，集成第三方硬件校准解决方案（如 MPCDI、EasyBlend、VIOSO、Domeprojection）或使用手动/相机/网格等多种方式定义视口和视锥体。

简而言之，当你的项目需要将 UE 画面输出到由多块屏幕组成的复杂物理显示系统（如 CAVE 洞穴、飞行模拟器视景系统、环幕影院、大型 LED 墙）时，nDisplay 是官方提供的核心解决方案。

## 使用场景
- **虚拟制片（Virtual Production）**：在 LED Volume 墙幕上实时渲染并同步显示背景画面，用于电影和电视制作。
- **建筑与工程可视化**：在 CAVE 系统或沉浸式房间里，以第一人称视角交互式地浏览大型建筑或工业模型。
- **驾驶/飞行模拟器**：将模拟器的多个屏幕（前视、侧视）无缝连接，形成广阔的视景环境。
- **主题公园与大型娱乐设施**：控制环幕、穹顶等特殊投影形状的同步渲染和几何校正。
- **科学数据可视化**：在多显示器阵列上同步展示和交互大规模科学计算或仿真结果。

## 蓝图用法
nDisplay 提供蓝图接口以动态控制投影策略，尤其是用于虚拟制片中的相机管理。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Camera` | 为指定的 nDisplay 视口设置摄像机投影策略使用的 `UCameraComponent`。常用于虚拟制片中，动态将 LED Volume 屏幕内容“聚焦”到场景中的特定摄影机上。 | `UDisplayClusterProjectionBlueprintLib` |

### 使用示例（蓝图描述）
1.  在你的角色蓝图或关卡蓝图中，添加一个 `UCameraComponent` 作为虚拟制作摄像机。
2.  使用 `Set Camera` 蓝图节点。
3.  将 `Viewport ID` 参数连接到你想要控制的 nDisplay 视口名称（在 nDisplay 配置文件中定义，例如 `"vp_1"`）。
4.  将 `New Camera` 参数连接到你的 `UCameraComponent` 引用。
5.  （可选）调整 `FOV Multiplier` 参数以微调摄像机视场角对投影的影响。
6.  当该节点执行时，指定视口的投影将跟随你设置的摄像机移动和旋转。

## C++ 用法
### 头文件引入
要使用 nDisplay 的投影策略系统，主要需要引入投影模块的头文件。
```cpp
#include "IDisplayClusterProjection.h"
```

### 基本用法：获取投影模块并查询策略
以下代码展示了如何检查 nDisplay 投影模块是否可用，并获取支持的投影类型列表。
（来源：基于 `IDisplayClusterProjection` 接口和 `FDisplayClusterProjectionModule` 实现推断）

```cpp
// 检查模块是否可用
if (IDisplayClusterProjection::IsAvailable())
{
    // 获取模块单例
    IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();

    // 查询所有已注册的投影策略类型
    TArray<FString> SupportedTypes;
    ProjectionModule.GetSupportedProjectionTypes(SupportedTypes);

    // 输出支持的类型
    for (const FString& TypeName : SupportedTypes)
    {
        UE_LOG(LogTemp, Log, TEXT("Supported Projection Type: %s"), *TypeName);
    }
    // 输出可能包括: "mpcdi", "camera", "manual", "easyblend", "vioso", "domeprojection" 等
}
```

### 进阶用法：应用 MPCDI 投影策略
以下代码片段展示了如何在 C++ 中配置并应用一个 MPCDI 投影策略到视口上。这是 nDisplay 最常用的高级投影校准方式之一。
（来源：基于 `FDisplayClusterProjectionMPCDIPolicy` 和 `IDisplayClusterProjectionPolicy` 接口推断）

```cpp
// 假设我们已经有了一个指向 IDisplayClusterViewport 的指针 InViewport
// 以及从 nDisplay 配置解析出的投影参数 Map

// 1. 从配置中构建 MPCDI 策略参数
TMap<FString, FString> MPCDIParams;
MPCDIParams.Add(TEXT("type"), TEXT("mpcdi"));
MPCDIParams.Add(TEXT("file"), TEXT("path/to/your/calibration.mpcdi"));
MPCDIParams.Add(TEXT("buffer"), TEXT("default"));
MPCDIParams.Add(TEXT("region"), TEXT("region_1"));
MPCDIParams.Add(TEXT("origin"), TEXT("camera_origin_component")); // 指定原点场景组件

// 2. 通过 nDisplay 的工厂系统创建策略实例
// 通常在 nDisplay 的内部初始化流程中自动完成，但理解其原理很重要。
IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();
TSharedPtr<IDisplayClusterProjectionPolicyFactory> MPCDIFactory = ProjectionModule.GetProjectionFactory(TEXT("mpcdi"));

if (MPCDIFactory.IsValid())
{
    // 创建策略实例 (实际使用中，策略会通过更高级的接口与视口绑定)
    TSharedPtr<IDisplayClusterProjectionPolicy> MPCDIPolicy = MPCDIFactory->Create(TEXT("MyViewport_MPCDI_Policy"), nullptr /* ConfigProjectionPolicy */);

    if (MPCDIPolicy.IsValid())
    {
        // 策略在视口初始化时（HandleStartScene）会根据提供的参数（MPCDIParams）加载校准文件。
        // 之后，视口的渲染管线会在每帧调用策略的 CalculateView 和 GetProjectionMatrix 来获取正确的视图和投影矩阵。
        // 并在需要时调用 ApplyWarpBlend_RenderThread 进行后处理扭曲融合。
        UE_LOG(LogTemp, Log, TEXT("MPCDI Projection Policy created successfully."));
    }
}
```

## Demo 示例
一个最小的可运行示例，展示如何创建一个简单的 nDisplay 集群节点（模拟）。

### nDisplaySimulatorNode.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IDisplayClusterProjection.h" // 引入投影模块接口
#include "nDisplaySimulatorNode.generated.h"

UCLASS()
class AnDisplaySimulatorNode : public AActor
{
    GENERATED_BODY()

public:
    AnDisplaySimulatorNode();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    // 模拟的 nDisplay 视口 ID
    FString SimulatedViewportId = TEXT("SimViewport_0");

    // 持有的投影策略指针（示例中未实际创建，演示生命周期）
    TSharedPtr<IDisplayClusterProjectionPolicy> ProjectionPolicy;

    // 初始化 nDisplay 投影子系统（示例）
    void InitializeProjectionSystem();
    // 清理资源
    void CleanupProjectionSystem();
};
```

### nDisplaySimulatorNode.cpp
```cpp
#include "nDisplaySimulatorNode.h"
#include "IDisplayClusterProjection.h"

AnDisplaySimulatorNode::AnDisplaySimulatorNode()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AnDisplaySimulatorNode::BeginPlay()
{
    Super::BeginPlay();
    InitializeProjectionSystem();
}

void AnDisplaySimulatorNode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    CleanupProjectionSystem();
    Super::EndPlay(EndPlayReason);
}

void AnDisplaySimulatorNode::InitializeProjectionSystem()
{
    // 步骤 1: 检查 nDisplay 投影模块是否已加载
    if (!IDisplayClusterProjection::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("nDisplay Projection module is not loaded! Ensure the nDisplay plugin is enabled."));
        return;
    }

    IDisplayClusterProjection& ProjectionModule = IDisplayClusterProjection::Get();
    UE_LOG(LogTemp, Log, TEXT("nDisplay Projection module is available."));

    // 步骤 2: (模拟) 查询支持的投影类型
    TArray<FString> SupportedTypes;
    ProjectionModule.GetSupportedProjectionTypes(SupportedTypes);
    for (const FString& Type : SupportedTypes)
    {
        UE_LOG(LogTemp, Log, TEXT(" - Supported Projection Type: %s"), *Type);
    }

    // 步骤 3: (模拟) 尝试获取一个“manual”投影策略的工厂
    TSharedPtr<IDisplayClusterProjectionPolicyFactory> ManualFactory = ProjectionModule.GetProjectionFactory(TEXT("manual"));
    if (ManualFactory.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Manual projection policy factory found."));
        // 在实际应用中，这里会调用 ManualFactory->Create(...) 来创建一个策略实例，
        // 并将其绑定到由 nDisplay 配置定义的视口上。此处仅为演示模块接口。
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Manual projection policy factory not found. This simulation is incomplete."));
    }
}

void AnDisplaySimulatorNode::CleanupProjectionSystem()
{
    // 释放任何创建的投影策略资源
    ProjectionPolicy.Reset();
    UE_LOG(LogTemp, Log, TEXT("nDisplay Simulator Node cleanup complete."));
}
```

## 模块依赖
`DisplayClusterProjection` 模块的直接依赖。要在你的模块中使用其功能，需要在 `Build.cs` 中添加依赖。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 该模块内部依赖，用于编辑器内操作（如预览网格体）。使用者的 Runtime 模块通常不需要直接依赖它。 |

**无特殊依赖（仅标准 Core/Engine/Slate 等）**：对于纯运行时功能，你的模块通常只需依赖 `DisplayCluster` 或 `DisplayClusterProjection`，它们会带来核心依赖。如果你在编辑器工具中使用，则需要依赖 `UnrealEd`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的电影渲染管线添加了 EXR 多层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了电影管线中的扭曲混合 Alpha 模式，简化了相关设置。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了媒体注册图中的拓扑感知相机命名问题，并修正了 MPCDI/ICVFX 着色器中的不透明 Alpha 通道问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 使 nDisplay 在输出帧编码回退路径中能正确处理非默认的显示伽马值。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时可能出现的闪烁问题。 |

### 维护评价
- **创建时间**：2018年，已维护超过8年。
- **近期更新**：最近一次提交在2026年5月，**更新非常活跃**。提交记录显示持续进行功能增强（如 EXR 多层）、bug 修复和着色器优化。
- **维护状态**：**活跃维护中**。作为 Unreal Engine 虚拟制作工具链的核心组件，Epic Games 持续投入开发资源。
- **已知问题/限制**：插件非常复杂，配置调试需要专业知识（如校准文件、网络设置）。`EnabledByDefault: false` 表明它是一个需要用户主动启用的高级功能。
- **推荐使用**：如果你的项目涉及**多屏幕同步渲染、非标准投影几何校正或虚拟制片**，那么 nDisplay 是**官方推荐且必须使用的解决方案**。它功能强大且受到官方持续支持，但学习曲线较陡峭。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)