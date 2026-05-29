# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 分布式渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产、材质、网格体） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个完整的分布式渲染和显示管理框架，远不止简单的“多屏显示”。它专为大型、复杂的沉浸式显示环境设计，例如：
- **大规模 LED 墙/卷帘屏**：在虚拟制作（Virtual Production）片场中驱动整个 LED 体积。
- **穹顶投影、CAVE（洞穴自动虚拟环境）系统**：需要精确几何校正和多台投影仪融合的场景。
- **多窗口/多视口同步渲染**：例如驾驶模拟器、主题公园游乐设施，需要多个物理屏幕或投影仪提供同步且几何校正正确的视图。
- **硬件同步与集群渲染**：支持使用多台 PC（集群）通过硬件同步（如 NVIDIA Quadro Sync、Genlock）来分担渲染负载，确保画面撕裂最小化，并实现帧级同步。

其核心功能包括：
1.  **投影校正（Warp & Blend）**：支持从 MPCDI、PFM 文件、静态网格或程序化网格体加载校准数据，对投影仪的光路变形和边缘混合进行实时校正。
2.  **集群视口管理**：将整个显示场景划分为多个逻辑视口，并将每个视口分配给集群中的特定节点进行渲染。
3.  **ICVFX（实时视觉特效）支持**：为虚拟制作中的 LED 面板渲染正确的摄像机视角，包括抠像（Chroma Key）、色彩校正等。
4.  **远程控制与监控**：提供工具和接口，用于在运行时远程监控、调整和控制所有集群节点。

## 使用场景

- 你在搭建一个虚拟制作片场，使用多台 Unreal Engine PC 驱动一块巨大的 LED 墙幕 → 使用 **nDisplay** 配置集群、设置同步、并加载 LED 面板的 MPCDI 校准文件。
- 你需要为一个驾驶模拟器设置三块环绕式屏幕，并且每台 PC 负责一块屏幕的渲染 → 使用 **nDisplay** 定义三个视口，并为每个视口分配到对应的集群 PC，同时进行投影校正。
- 你正在开发一个穹顶影院的影片预览工具，需要将 Unreal 的画面投影到半球形银幕上 → 使用 **nDisplay** 的投影校正功能，并结合自定义的 Warp 策略（如 `InFrustumFit`）来适配非平面的显示表面。
- 你需要在多个独立显示器上展示同一个 3D 场景的不同视角，且要求它们保持严格的画面同步 → 使用 **nDisplay** 的集群功能实现硬件同步的多视口渲染。

## 蓝图用法

**核心节点**

nDisplay 的主要交互通过编辑器和配置资产（`.ndisplay` 配置文件）完成，但在蓝图运行时，可以通过其暴露的组件和功能进行控制。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Enable Frustum Fit` | 控制是否启用“视锥适配”投影模式 | `UDisplayClusterInFrustumFitCameraComponent` |
| `Set Camera Projection Mode` | 设置摄像机的投影模式（适配 `Fit` 或 填充 `Fill`） | `UDisplayClusterInFrustumFitCameraComponent` |
| `Set Camera View Target` | 设置视锥适配计算时的观察目标（几何中心 `GeometricCenter` 或匹配视点 `MatchViewOrigin`） | `UDisplayClusterInFrustumFitCameraComponent` |
| `Show Frustum Fit Preview` | 在编辑器中显示视锥适配的预览网格 | `UDisplayClusterInFrustumFitCameraComponent` |

**使用示例（蓝图描述）**

1.  在你的 nDisplay 根演员（`ADisplayClusterRootActor`）中，找到用于定义视锥适配的摄像机组件（`UDisplayClusterInFrustumFitCameraComponent`）。
2.  在蓝图图表中，对该组件引脚，使用“Set Members in Struct”节点，可以设置 `bEnableCameraProjection`、`CameraProjectionMode` 和 `CameraViewTarget` 属性，以在运行时动态调整视锥适配行为。
3.  例如，要创建一个按钮来切换“适配”和“填充”模式，可以将按钮的 `OnClicked` 事件连接到一个 `Set Camera Projection Mode` 节点，并为该节点提供要设置的模式枚举值。

## C++ 用法

**头文件引入**

```cpp
#include "IDisplayClusterWarp.h"
#include "DisplayClusterWarpBlend.h"
```

**基本用法**

通过 `IDisplayClusterWarp` 模块接口创建 `WarpBlend` 实例。这是应用投影校正的核心。

```cpp
// 来源：Public/IDisplayClusterWarp.h
// 获取 Warp 模块
if (IDisplayClusterWarp::IsAvailable())
{
    IDisplayClusterWarp& WarpModule = IDisplayClusterWarp::Get();

    // 示例1：从 MPCDI 文件创建
    FDisplayClusterWarpInitializer_MPCDIFile MPCDIInit;
    MPCDIInit.MPCDIFileName = TEXT("/Game/nDisplay/Calibration/calibration.mpcdi");
    MPCDIInit.BufferId = TEXT("buffer_0");
    MPCDIInit.RegionId = TEXT("region_0");

    TSharedPtr<IDisplayClusterWarpBlend> WarpBlendMPCDI = WarpModule.Create(MPCDIInit);

    // 示例2：从静态网格体创建
    FDisplayClusterWarpInitializer_StaticMesh MeshInit;
    MeshInit.WarpMeshComponent = MyWarpMeshComponent; // 指向UStaticMeshComponent的指针
    MeshInit.OriginComponent = MyOriginComponent;

    TSharedPtr<IDisplayClusterWarpBlend> WarpBlendMesh = WarpModule.Create(MeshInit);
}
```

**进阶用法**

获取创建好的 `WarpBlend` 实例后，可用于管理其生命周期和访问其内部数据。

```cpp
// 假设你已经持有一个有效的 TSharedPtr<IDisplayClusterWarpBlend> WarpBlendInstance;

// 通知 WarpBlend 当前场景开始（例如关卡加载后）
WarpBlendInstance->HandleStartScene(MyViewport);

// 更新几何上下文（当世界缩放或几何数据变化时调用）
WarpBlendInstance->UpdateGeometryContext(1.0f);

// 为新的眼睛/上下文（例如立体渲染的左眼）计算视锥上下文
TSharedPtr<FDisplayClusterWarpEye> WarpEye = MakeShared<FDisplayClusterWarpEye>(MyViewport, 0);
WarpBlendInstance->CalcFrustumContext(WarpEye);

// 获取计算后的几何上下文（包含包围盒、法线等信息）
const FDisplayClusterWarpGeometryContext& GeoContext = WarpBlendInstance->GetGeometryContext();

// 导出 WarpMap 几何数据为 OBJ 格式（用于调试）
FDisplayClusterWarpGeometryOBJ ExportedOBJ;
WarpBlendInstance->ExportWarpMapGeometry(ExportedOBJ, 64); // 最大维度64个顶点

// 标记几何组件需要更新（当源网格体发生变化时）
WarpBlendInstance->MarkWarpGeometryComponentDirty(FName("MyWarpMesh"));
```

## Demo 示例

以下是一个最小的 C++ 示例，展示如何初始化并使用 `DisplayClusterWarp` 模块创建一个基于 MPCDI 文件的 `WarpBlend` 实例。

**WarpDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "IDisplayClusterWarpBlend.h"
#include "WarpDemo.generated.h"

UCLASS(ClassGroup=(nDisplay), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UWarpDemo : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    void DoWarpBlendDemo();

private:
    TSharedPtr<IDisplayClusterWarpBlend, ESPMode::ThreadSafe> WarpBlendInstance;
};
```

**WarpDemo.cpp**
```cpp
#include "WarpDemo.h"
#include "IDisplayClusterWarp.h"

void UWarpDemo::BeginPlay()
{
    Super::BeginPlay();
    DoWarpBlendDemo();
}

void UWarpDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理实例，通知场景结束
    if (WarpBlendInstance.IsValid())
    {
        WarpBlendInstance->HandleEndScene(nullptr); // 在此示例中Viewport为nullptr，实际需根据情况传入
    }
    WarpBlendInstance.Reset();
    Super::EndPlay(EndPlayReason);
}

void UWarpDemo::DoWarpBlendDemo()
{
    if (!IDisplayClusterWarp::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("DisplayClusterWarp module is not available."));
        return;
    }

    // 1. 初始化参数
    FDisplayClusterWarpInitializer_MPCDIFile InitParams;
    InitParams.MPCDIFileName = TEXT("/Game/nDisplay/Calibration/test.mpcdi");
    InitParams.BufferId = TEXT("buffer_0");
    InitParams.RegionId = TEXT("region_0");

    // 2. 创建实例
    IDisplayClusterWarp& WarpModule = IDisplayClusterWarp::Get();
    WarpBlendInstance = WarpModule.Create(InitParams);

    if (!WarpBlendInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create WarpBlend instance from MPCDI file."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Successfully created WarpBlend instance."));

    // 3. 模拟场景开始和几何更新
    WarpBlendInstance->HandleStartScene(nullptr); // 传入有效的Viewport指针
    WarpBlendInstance->UpdateGeometryContext(1.0f); // 使用世界缩放因子1.0

    // 4. 获取一些信息
    const auto& GeoCtx = WarpBlendInstance->GetGeometryContext();
    const auto& MPCDIAttrs = WarpBlendInstance->GetMPCDIAttributes();
    UE_LOG(LogTemp, Log, TEXT("Geometry Valid: %s, Profile Type: %s"),
        GeoCtx.AABBox.IsValid ? TEXT("true") : TEXT("false"),
        *UEnum::GetValueAsString(MPCDIAttrs.ProfileType));
}
```

## 模块依赖

`DisplayClusterWarp` 模块本身依赖 `UnrealEd`，但这通常是编辑器功能所需。对于使用其核心 `IDisplayClusterWarp` 和 `IDisplayClusterWarpBlend` 接口的运行时代码，主要的隐式依赖是 Unreal Engine 的核心和渲染模块。

| 模块 | 用途 |
|---|---|
| `ScalableMPCDI` (External) | 第三方库，用于解析和处理 MPCDI 校准文件格式 |
| `DisplayClusterRender` (假设存在) | 提供渲染相关的接口和工具，如 `IDisplayClusterRender_Texture` |

**注意**：为了成功编译和使用，你的项目 `Build.cs` 文件通常需要添加对 `DisplayCluster` 或 `DisplayClusterWarp` 模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 在 MovieGraph 和 nDisplay 中增加 EXR 多图层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | nDisplay 电影管线：将 WarpBlendAlpha 模式合并到 WarpBlend 主模式中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知的摄像机命名问题；修复 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码回退时尊重非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

**综合评价：活跃维护中，推荐使用。**

- **活跃维护**：`nDisplay` 作为 Epic Games 虚拟制作管线的核心组件，在最近（2026年5月）仍有频繁的功能更新（EXR多层、MoviePipeline集成）和重要的错误修复（着色器、闪烁、Gamma）。这表明它在持续开发以支持新的工作流（如 Movie Graph）。
- **成熟度**：插件自2018年创建以来已有8年历史，属于成熟的生产级工具。拥有庞大的代码库（1300+文件），包含编辑器工具、测试模块、第三方库集成等，是 Unreal Engine 中功能最完善的插件之一。
- **推荐使用**：对于任何涉及多PC同步渲染、复杂投影校正或虚拟制作的项目，`nDisplay` 是官方且功能完备的首选方案。尽管它默认未启用且学习曲线较陡，但其稳定性和功能深度值得投入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/ndisplay-in-unreal-engine/)（Unreal Engine 官方文档入口）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)