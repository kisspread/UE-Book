# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 分布式显示渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、媒体资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于实现**多机同步集群渲染**的核心插件。它解决的核心问题是：当一台 PC 无法满足超大分辨率或多屏幕拼接渲染需求时，如何让多台 PC 各自渲染场景的一部分，最终在物理空间中无缝拼接成一个完整的画面。

典型应用包括：
- **LED 虚拟影棚（Virtual Production）**：电影拍摄中使用巨大的 LED 墙实时渲染背景，这是 nDisplay 最重要的应用场景。通过 ICVFX（In-Camera Visual Effects）技术，让摄影机拍摄到的画面中 LED 墙的渲染内容与真实场景完美融合
- **多投影仪融合（Multi-Projector）**：穹顶影院、CAVE 洞穴投影、飞行模拟器等需要多台投影仪拼接覆盖复杂几何表面的场景
- **多显示器拼接**：赛车/飞行模拟器的多屏环绕显示，电竞转播的多角度监控墙
- **Warp & Blend**：通过 MPCDI 格式的网格变形数据，对投影画面进行几何校正和边缘融合

插件通过 `DisplayClusterRootActor` 定义整个显示集群的物理布局，包括视口（viewport）、投影几何、ICVFX 摄像机和灯光卡（Light Card）。所有参与渲染的 PC 通过网络同步，保持帧级精确的同步渲染。

## 使用场景

- 你在做一个虚拟制片的 LED 影棚 → 用 nDisplay + ICVFX 摄像机
- 你需要多台投影仪拼接投射到穹顶/曲面幕布 → 用 nDisplay + MPCDI Warp & Blend
- 你在搭建飞行/赛车模拟器的多屏环绕系统 → 用 nDisplay 多视口配置
- 你需要在多台 PC 上同步渲染同一个场景的不同视角 → 用 nDisplay 集群渲染
- 你需要通过 Movie Pipeline 渲染 nDisplay 画面 → 用 DisplayClusterMoviePipeline 子模块
- 你需要在编辑器中预览 nDisplay 场景 → 用 DisplayClusterScenePreview 子模块

## 蓝图用法

nDisplay 的蓝图 API 分布在多个子模块中，核心功能围绕 `ADisplayClusterRootActor` 展开。

### 核心节点

#### 场景预览（DisplayClusterScenePreview）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateRenderer` | 创建一个预览渲染器实例，返回 Renderer ID | `IDisplayClusterScenePreview` |
| `DestroyRenderer` | 销毁指定的预览渲染器 | `IDisplayClusterScenePreview` |
| `SetRendererRootActor` | 为预览渲染器设置根 Actor（DCRA） | `IDisplayClusterScenePreview` |
| `SetRendererRootActorPath` | 通过路径设置预览渲染器的根 Actor（跨关卡持久） | `IDisplayClusterScenePreview` |
| `GetRendererRootActor` | 获取渲染器当前使用的根 Actor | `IDisplayClusterScenePreview` |
| `GetRendererRootActorOrProxy` | 获取渲染器的根 Actor 或其代理对象 | `IDisplayClusterScenePreview` |
| `AddActorToRenderer` | 向渲染器的预览场景中添加 Actor | `IDisplayClusterScenePreview` |
| `RemoveActorFromRenderer` | 从渲染器的预览场景中移除 Actor | `IDisplayClusterScenePreview` |
| `ClearRendererScene` | 清空渲染器的预览场景 | `IDisplayClusterScenePreview` |
| `Render` | 立即执行一次预览渲染 | `IDisplayClusterScenePreview` |
| `RenderQueued` | 将预览渲染任务加入队列（异步） | `IDisplayClusterScenePreview` |
| `IsRealTimePreviewEnabled` | 检查是否启用了实时预览更新 | `IDisplayClusterScenePreview` |

#### 灯光卡编辑辅助（DisplayClusterScenePreview）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MoveActorsToPixel` | 将灯光卡移动到视口中的指定像素位置 | `FDisplayClusterLightCardEditorHelper` |
| `MoveActorsTo` | 将灯光卡移动到球面坐标指定的位置 | `FDisplayClusterLightCardEditorHelper` |
| `DragActors` | 模拟拖拽灯光卡到视口中的新位置（支持多种坐标系） | `FDisplayClusterLightCardEditorHelper` |
| `SpawnStageActor` | 在舞台上生成新的 Actor（灯光卡等） | `FDisplayClusterLightCardEditorHelper` |
| `AddLightCardsToRootActor` | 将灯光卡添加到根 Actor | `FDisplayClusterLightCardEditorHelper` |

### 使用示例

**创建预览渲染器并渲染画面：**

1. 获取 `IDisplayClusterScenePreview` 模块接口
2. 调用 `CreateRenderer()` 获取 Renderer ID
3. 调用 `SetRendererRootActor(RendererId, MyRootActor, PropertyOverrides)` 绑定 DCRA
4. 调用 `AddActorToRenderer(RendererId, SomeLightCard)` 添加灯光卡到预览场景
5. 调用 `RenderQueued(RendererId, RenderSettings, ImageSize, ResultDelegate)` 异步渲染
6. 在 `ResultDelegate` 回调中获取 `FRenderTarget` 用于显示

**使用代理模式编辑场景（避免修改真实关卡）：**

1. 设置 `EDisplayClusterScenePreviewFlags::UseRootActorProxy` 标志
2. 调用 `SetRendererRootActor(RendererId, Actor, Overrides, PreviewFlags)` 时传入该标志
3. 通过 `GetRendererRootActorOrProxy()` 获取代理对象进行编辑操作
4. 代理对象的所有修改会自动同步回原始 Actor

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterScenePreview.h"
#include "DisplayClusterLightCardEditorHelper.h"
#include "DisplayClusterScenePreviewEnums.h"
```

### 基本用法：创建预览渲染器并渲染

```cpp
// 来源: Public/IDisplayClusterScenePreview.h

#include "IDisplayClusterScenePreview.h"

void MyClass::SetupPreviewRenderer()
{
    // 获取场景预览模块
    IDisplayClusterScenePreview& ScenePreviewModule = IDisplayClusterScenePreview::Get();
    
    // 创建预览渲染器
    int32 RendererId = ScenePreviewModule.CreateRenderer();
    
    // 设置根 Actor（DisplayClusterRootActor）
    FDisplayClusterRootActorPropertyOverrides PropertyOverrides;
    ScenePreviewModule.SetRendererRootActorPath(
        RendererId,
        TEXT("/Game/MyLevel.MyLevel:PersistentLevel.MyNDisplayRootActor"),
        PropertyOverrides,
        EDisplayClusterScenePreviewFlags::AutoUpdateStageActors
    );
    
    // 添加灯光卡到预览场景
    ADisplayClusterLightCardActor* LightCard = GetMyLightCard();
    ScenePreviewModule.AddActorToRenderer(RendererId, LightCard);
    
    // 同步渲染到 Canvas
    FDisplayClusterMeshProjectionRenderSettings RenderSettings;
    // ... 配置渲染设置
    FCanvas* Canvas = GetMyCanvas();
    ScenePreviewModule.Render(RendererId, RenderSettings, *Canvas);
}
```

### 基本用法：异步队列渲染

```cpp
// 来源: Public/IDisplayClusterScenePreview.h

void MyClass::QueueAsyncRender()
{
    IDisplayClusterScenePreview& ScenePreviewModule = IDisplayClusterScenePreview::Get();
    
    int32 RendererId = ScenePreviewModule.CreateRenderer();
    // ... 设置根 Actor ...
    
    FDisplayClusterMeshProjectionRenderSettings RenderSettings;
    FIntPoint ImageSize(1920, 1080);
    
    // 异步渲染，结果通过回调返回
    ScenePreviewModule.RenderQueued(
        RendererId,
        RenderSettings,
        ImageSize,
        FRenderResultDelegate::CreateLambda([this](FRenderTarget* RenderTarget)
        {
            if (RenderTarget)
            {
                // 使用渲染结果（例如显示在 UI 上）
                UpdatePreviewTexture(RenderTarget);
            }
        })
    );
}
```

### 进阶用法：使用代理模式和自定义过滤器

```cpp
// 来源: Public/IDisplayClusterScenePreview.h, Private/DisplayClusterScenePreviewModule.h

void MyClass::SetupProxyPreview()
{
    IDisplayClusterScenePreview& ScenePreviewModule = IDisplayClusterScenePreview::Get();
    
    int32 RendererId = ScenePreviewModule.CreateRenderer();
    
    // 使用代理模式，避免直接修改关卡中的 Actor
    EDisplayClusterScenePreviewFlags Flags = 
        EDisplayClusterScenePreviewFlags::UseRootActorProxy |
        EDisplayClusterScenePreviewFlags::AutoUpdateStageActors |
        EDisplayClusterScenePreviewFlags::ProxyFollowSceneRootActor;
    
    FDisplayClusterRootActorPropertyOverrides PropertyOverrides;
    ScenePreviewModule.SetRendererRootActor(RendererId, MyRootActor, PropertyOverrides, Flags);
    
    // 添加 Actor 时使用自定义图元过滤器
    ScenePreviewModule.AddActorToRenderer(
        RendererId,
        SomeActor,
        [](const UPrimitiveComponent* PrimComp) -> bool
        {
            // 只添加可见的图元组件
            return PrimComp->IsVisible();
        }
    );
    
    // 设置 Actor 选中回调
    ScenePreviewModule.SetRendererActorSelectedDelegate(
        RendererId,
        FDisplayClusterMeshProjectionRenderer::FSelection::CreateLambda(
            [this](AActor* SelectedActor)
            {
                HandleActorSelection(SelectedActor);
            })
    );
    
    // 设置简单元素渲染回调（用于绘制自定义叠加层）
    ScenePreviewModule.SetRendererRenderSimpleElementsDelegate(
        RendererId,
        FDisplayClusterMeshProjectionRenderer::FSimpleElementPass::CreateLambda(
            [this](const FSceneView& View, FCanvas& Canvas)
            {
                DrawCustomOverlay(View, Canvas);
            })
    );
    
    // 清理时销毁渲染器
    ScenePreviewModule.DestroyRenderer(RendererId);
}
```

### 进阶用法：灯光卡编辑辅助工具

```cpp
// 来源: Public/DisplayClusterLightCardEditorHelper.h

void MyClass::EditLightCards()
{
    // 创建灯光卡编辑辅助器
    FDisplayClusterLightCardEditorHelper LightCardHelper;
    
    // 设置根 Actor
    LightCardHelper.SetRootActor(*MyRootActor);
    
    // 设置投影模式
    LightCardHelper.SetProjectionMode(EDisplayClusterMeshProjectionType::UV);
    
    // 移动灯光卡到球面坐标位置
    FDisplayClusterLightCardEditorHelper::FSphericalCoordinates Coords;
    Coords.Radius = 100.0;
    Coords.Inclination = FMath::DegreesToRadians(45.0);
    Coords.Azimuth = FMath::DegreesToRadians(90.0);
    
    TArray<FDisplayClusterWeakStageActorPtr> Actors;
    Actors.Add(MyLightCard);
    LightCardHelper.MoveActorsTo(Actors, Coords);
    
    // 像素级移动
    FIntPoint PixelPos(512, 384);
    FSceneView* View = GetMySceneView();
    LightCardHelper.MoveActorsToPixel(Actors, PixelPos, *View);
    
    // 拖拽操作（带坐标系约束）
    FVector DragOffset = FVector::ZeroVector;
    LightCardHelper.DragActors(
        Actors, PixelPos, *View,
        FDisplayClusterLightCardEditorHelper::ECoordinateSystem::Spherical,
        DragOffset, EAxisList::XY
    );
    
    // 获取 Actor 的球面坐标
    auto CurrentCoords = LightCardHelper.GetActorCoordinates(Actors[0]);
    UE_LOG(LogTemp, Log, TEXT("Radius: %f, Inclination: %f, Azimuth: %f"),
        CurrentCoords.Radius,
        FMath::RadiansToDegrees(CurrentCoords.Inclination),
        FMath::RadiansToDegrees(CurrentCoords.Azimuth));
    
    // 生成新的舞台 Actor
    FDisplayClusterLightCardEditorHelper::FSpawnActorArgs SpawnArgs;
    SpawnArgs.RootActor = MyRootActor;
    SpawnArgs.ActorClass = ADisplayClusterLightCardActor::StaticClass();
    SpawnArgs.ActorName = TEXT("NewLightCard");
    SpawnArgs.ProjectionMode = EDisplayClusterMeshProjectionType::UV;
    
    AActor* SpawnedActor = FDisplayClusterLightCardEditorHelper::SpawnStageActor(SpawnArgs);
}
```

## Demo 示例

以下展示如何创建一个最小的场景预览渲染示例：

```cpp
// MyNDisplayPreview.h
#pragma once

#include "CoreMinimal.h"

class IDisplayClusterScenePreview;
class ADisplayClusterRootActor;

class FMyNDisplayPreview
{
public:
    FMyNDisplayPreview();
    ~FMyNDisplayPreview();
    
    /** 初始化预览渲染器 */
    bool Initialize(ADisplayClusterRootActor* InRootActor);
    
    /** 执行一次渲染 */
    void RenderPreview();
    
    /** 清理资源 */
    void Shutdown();

private:
    /** 预览渲染器 ID */
    int32 RendererId = -1;
    
    /** 是否已初始化 */
    bool bInitialized = false;
};
```

```cpp
// MyNDisplayPreview.cpp
#include "MyNDisplayPreview.h"
#include "IDisplayClusterScenePreview.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterScenePreviewEnums.h"
#include "CanvasTypes.h"

FMyNDisplayPreview::FMyNDisplayPreview()
{
}

FMyNDisplayPreview::~FMyNDisplayPreview()
{
    Shutdown();
}

bool FMyNDisplayPreview::Initialize(ADisplayClusterRootActor* InRootActor)
{
    if (!InRootActor || !IDisplayClusterScenePreview::IsAvailable())
    {
        return false;
    }
    
    IDisplayClusterScenePreview& ScenePreview = IDisplayClusterScenePreview::Get();
    
    // 创建渲染器
    RendererId = ScenePreview.CreateRenderer();
    if (RendererId < 0)
    {
        return false;
    }
    
    // 设置根 Actor，启用自动更新舞台 Actor
    FDisplayClusterRootActorPropertyOverrides PropertyOverrides;
    bool bSuccess = ScenePreview.SetRendererRootActor(
        RendererId,
        InRootActor,
        PropertyOverrides,
        EDisplayClusterScenePreviewFlags::AutoUpdateStageActors
    );
    
    if (!bSuccess)
    {
        ScenePreview.DestroyRenderer(RendererId);
        RendererId = -1;
        return false;
    }
    
    bInitialized = true;
    return true;
}

void FMyNDisplayPreview::RenderPreview()
{
    if (!bInitialized || !IDisplayClusterScenePreview::IsAvailable())
    {
        return;
    }
    
    IDisplayClusterScenePreview& ScenePreview = IDisplayClusterScenePreview::Get();
    
    // 使用异步队列渲染
    FDisplayClusterMeshProjectionRenderSettings RenderSettings;
    FIntPoint Size(512, 512);
    
    ScenePreview.RenderQueued(
        RendererId,
        RenderSettings,
        Size,
        FRenderResultDelegate::CreateLambda([](FRenderTarget* RenderTarget)
        {
            if (RenderTarget)
            {
                // 渲染完成，可以使用 RenderTarget 中的数据
                UE_LOG(LogTemp, Log, TEXT("Preview render completed: %dx%d"),
                    RenderTarget->GetSizeX(), RenderTarget->GetSizeY());
            }
        })
    );
}

void FMyNDisplayPreview::Shutdown()
{
    if (bInitialized && IDisplayClusterScenePreview::IsAvailable())
    {
        IDisplayClusterScenePreview::Get().DestroyRenderer(RendererId);
        RendererId = -1;
        bInitialized = false;
    }
}
```

## 模块依赖

nDisplay 插件包含 29 个模块，依赖非常广泛。以下是各子模块的独特依赖（从 Build.cs 提取）：

| 模块 | 用途 |
|---|---|
| `DisplayClusterMedia` | 依赖 D3D12RHI，用于 GPU 共享内存的媒体输入输出 |
| `SharedMemoryMedia` | 依赖 D3D12RHI，用于跨进程共享内存传输渲染帧 |
| `ScalableMPCDI` | 第三方库，MPCDI 格式解析，用于投影仪几何校正与边缘融合数据 |
| `DisplayClusterProjection` | 依赖 UnrealEd，投影几何处理与调试工具 |
| `DisplayClusterWarp` | 依赖 UnrealEd，网格变形（Warp）与混合（Blend）实现 |
| `DisplayClusterShaders` | 依赖 UnrealEd，ICVFX / 后处理着色器 |
| `DisplayClusterScenePreview` | 依赖 UnrealEd，编辑器内场景预览渲染 |
| `DisplayClusterFillDerivedDataCache` | DDC 填充工具，用于离线准备资产缓存 |

> **注**：由于 nDisplay 属于虚拟制片工具链，许多模块标记为 Runtime 但实际同时包含编辑器功能代码（通过 `#if WITH_EDITOR` 宏），因此对 UnrealEd 有广泛依赖。使用者的 Build.cs 需要依赖 `DisplayCluster` 和具体使用的子模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 支持 nDisplay 的 EXR 多层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 MoviePipeline 的 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄像机命名和 MPCDI/ICVFX 着色器的不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时正确处理非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** — nDisplay 是 Epic Games 虚拟制片（Virtual Production）技术栈的核心组件，持续获得高频更新。

- **创建时间**：2018 年 6 月（UE 4.20 时代），至今已维护约 8 年
- **更新频率**：近期几乎每周都有更新，最近 5 次提交集中在 10 天内
- **更新内容**：涵盖新功能（EXR 多层输出）、着色器修复、兼容性改进、bug 修复等多个方面
- **模块规模**：29 个模块、1351 个源文件，是 UE5 中规模最大的插件之一
- **平台支持**：支持 Win64 和 Linux
- **推荐使用**：✅ 强烈推荐用于任何涉及多机同步渲染、LED 虚拟影棚、投影仪融合的项目。这是 Epic 官方维护的核心技术，质量有保障

> ⚠️ **注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。它主要面向虚拟制片和专业 AV 行业，普通游戏项目通常不需要使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplayOverview/)（Unreal Engine 官方 nDisplay 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)