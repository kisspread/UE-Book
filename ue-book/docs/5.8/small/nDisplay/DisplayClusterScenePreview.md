# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 多机同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、蓝图资产、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterMultiUser` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个功能极其强大的 Unreal Engine 插件，其核心目的是实现**多台计算机（PC）的同步集群渲染**，以驱动大规模的显示器阵列、LED 墙幕或穹顶/圆柱投影系统。它并非一个简单的多显示器扩展，而是一个完整的分布式渲染和同步框架。

该插件通过定义一套名为 **nDisplay 配置（.ndisplay）** 的文件来描述整个显示集群的拓扑结构，包括：
- **节点（Node）**： 每一台参与渲染的计算机。
- **视口（Viewport）**： 每台计算机上渲染的虚拟“屏幕”区域。
- **投影（Projection）**： 视口内容如何映射到物理屏幕（平面、圆柱、网格、MPCDI等）。
- **同步（Sync）**： 确保所有节点在精确的同一时刻渲染同一帧。

其存在意义是为**虚拟制片（Virtual Production）**、**大型沉浸式体验**和**专业可视化**等领域提供技术基础，解决单台计算机算力不足以驱动超大分辨率或多角度同步渲染的难题。

## 使用场景

- **虚拟制片（LED墙拍摄）**： 你在搭建一个 LED 墙影棚，需要多台渲染服务器（称为 Render Nodes）协同工作，实时渲染摄像机视角对应的虚拟场景，并无缝显示在物理 LED 屏幕上，实现演员与虚拟背景的实时互动。→ 使用 nDisplay。
- **穹顶或圆柱投影**： 你需要一个环绕观众的360度或半球形投影系统，这超出了单张显卡的输出能力。→ 需要 nDisplay 将画面分割并同步到多台投影仪对应的计算机上。
- **多通道CAVE系统**： 你正在构建一个沉浸式VR CAVE系统，用户身处一个立方体空间内，四面墙壁和地板/天花板都由投影仪覆盖。每个面由一台PC驱动。→ 使用 nDisplay 进行同步和几何校正。
- **超高清视频墙**： 你需要驱动一个由多个显示器拼接而成的8K或更高分辨率的视频墙。→ 使用 nDisplay 将渲染负载分布到多台PC上，并保证画面拼接准确。

## 蓝图用法

nDisplay 的核心配置通过 **.ndisplay 配置文件**和编辑器内的 **nDisplay 配置器**完成，而非大量运行时蓝图节点。其主要的蓝图暴露接口集中在**场景预览**和**灯光卡（Light Card）编辑**的辅助功能上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Scene Preview Renderer` | 创建一个用于在编辑器中预览 nDisplay 场景的渲染器实例，返回渲染器ID。 | `IDisplayClusterScenePreview` |
| `Set Renderer Root Actor` | 为指定的预览渲染器设置一个 `ADisplayClusterRootActor` 作为预览场景的根。 | `IDisplayClusterScenePreview` |
| `Add Actor to Renderer` | 将一个 Actor（如灯光卡）添加到预览渲染器的场景中。 | `IDisplayClusterScenePreview` |
| `Render Preview` | 使用指定的渲染器和设置执行一次即时预览渲染到画布。 | `IDisplayClusterScenePreview` |
| `Spawn Stage Actor` | 在舞台系统中生成一个新Actor（如灯光卡），并可选地将其添加到根Actor的管理下。 | `FDisplayClusterLightCardEditorHelper` |

**说明**： 上述 `IDisplayClusterScenePreview` 接口通常由 C++ 代码直接调用，而非直接暴露为蓝图节点。它主要服务于 nDisplay 的编辑器工具（如灯光卡编辑器、场景预览窗口）。实际运行时的集群控制逻辑主要由 nDisplay 的主模块和配置系统处理。

### 使用示例（蓝图描述）

一个典型的编辑器工具蓝图用法是**灯光卡编辑器**的一部分。当用户在 nDisplay 预览视口中移动一个灯光卡时：
1.  蓝图或 C++ 代码通过 `IDisplayClusterScenePreview::Get()` 获取预览模块。
2.  使用 `CreateRenderer()` 创建一个预览渲染器。
3.  调用 `SetRendererRootActor()` 将当前关卡中的 `ADisplayClusterRootActor` 设为根。
4.  调用 `AddActorToRenderer()` 将需要预览的灯光卡 Actor 添加进渲染场景。
5.  在需要更新预览时（如每帧），调用 `RenderQueued()` 或 `Render()` 来生成投影到特定屏幕几何的预览图像。
6.  `FDisplayClusterLightCardEditorHelper` 会被用来处理鼠标点击到投影空间坐标的转换，从而实现灯光卡在预览视口中的直观拖拽移动。

## C++ 用法

### 头文件引入

使用 nDisplay 的场景预览和灯光卡编辑功能，主要包含以下头文件：
```cpp
#include "IDisplayClusterScenePreview.h"
#include "DisplayClusterLightCardEditorHelper.h"
#include "DisplayClusterScenePreviewEnums.h"
```

### 基本用法

以下代码展示了如何使用 `IDisplayClusterScenePreview` 接口来创建一个简单的预览渲染流程。

```cpp
// 获取场景预览模块接口
IDisplayClusterScenePreview& ScenePreviewModule = IDisplayClusterScenePreview::Get();
if (!IDisplayClusterScenePreview::IsAvailable())
{
    return;
}

// 1. 创建一个预览渲染器
int32 RendererId = ScenePreviewModule.CreateRenderer();

// 2. 设置渲染器的根Actor（假设你已经有一个有效的 ADisplayClusterRootActor 指针）
ADisplayClusterRootActor* MyDCRA = /* ... 从场景中获取或创建 ... */;
FDisplayClusterRootActorPropertyOverrides PropertyOverrides; // 通常使用默认值
ScenePreviewModule.SetRendererRootActor(RendererId, MyDCRA, PropertyOverrides);

// 3. （可选）向场景中添加其他需要预览的Actor，比如一个灯光卡
ADisplayClusterLightCardActor* MyLightCard = /* ... */;
ScenePreviewModule.AddActorToRenderer(RendererId, MyLightCard);

// 4. 配置渲染设置
FDisplayClusterMeshProjectionRenderSettings RenderSettings;
RenderSettings.ProjectionType = EDisplayClusterMeshProjectionType::UV; // 例如使用UV投影
RenderSettings.ViewLocation = FVector::ZeroVector;
// ... 设置其他参数如FOV、分辨率等

// 5. 执行即时渲染到一个画布
FCanvas Canvas(/* ... 渲染目标等参数 ... */);
if (ScenePreviewModule.Render(RendererId, RenderSettings, Canvas))
{
    // 渲染成功，Canvas现在包含预览图像
}

// 6. 或者，排队一个异步渲染
FIntPoint DesiredSize(1920, 1080);
FRenderResultDelegate ResultDelegate = FRenderResultDelegate::CreateLambda(
    [](FRenderTarget* InRenderTarget)
    {
        if (InRenderTarget)
        {
            // 处理渲染结果，例如创建纹理或显示在UI上
        }
    });
ScenePreviewModule.RenderQueued(RendererId, RenderSettings, DesiredSize, ResultDelegate);

// 7. 在使用完毕后销毁渲染器，释放资源
ScenePreviewModule.DestroyRenderer(RendererId);
```

**来源文件路径**: 基于 `Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterScenePreview/Public/IDisplayClusterScenePreview.h` 和 `Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterScenePreview/Private/DisplayClusterScenePreviewModule.h` 的接口分析。

### 进阶用法

使用 `FDisplayClusterLightCardEditorHelper` 进行精确的坐标转换和交互。
```cpp
// 创建一个灯光卡编辑器辅助器，它内部会创建或复用一个预览渲染器
FDisplayClusterLightCardEditorHelper LightCardHelper(RendererId); // 传入已有的渲染器ID

// 设置投影模式，例如用于穹顶投影
LightCardHelper.SetProjectionMode(EDisplayClusterMeshProjectionType::Spherical);

// 假设我们在处理一个鼠标点击事件，想在预览视口中放置一个灯光卡
FIntPoint PixelPos = /* 鼠标点击的像素坐标 */;
const FSceneView& SceneView = /* 从编辑器视口获取的当前场景视图 */;

// 计算从该像素位置发射出的世界空间射线原点和方向
FVector RayOrigin, RayDirection;
LightCardHelper.CalculateOriginAndDirectionFromPixelPosition(PixelPos, SceneView, FVector::ZeroVector, RayOrigin, RayDirection);

// 使用该射线与舞台几何体进行求交，以获得一个合理的放置点
FVector HitLocation, HitNormal;
if (LightCardHelper.CalculateNormalAndPositionInDirection(RayOrigin, RayDirection, HitLocation, HitNormal))
{
    // 将命中点转换为球面坐标，用于设置灯光卡位置
    FDisplayClusterLightCardEditorHelper::FSphericalCoordinates SphericalCoords(HitLocation);
    // 创建灯光卡
    FDisplayClusterLightCardEditorHelper::FSpawnActorArgs SpawnArgs;
    SpawnArgs.RootActor = MyDCRA;
    SpawnArgs.ActorClass = ADisplayClusterLightCardActor::StaticClass();
    SpawnArgs.ProjectionMode = EDisplayClusterMeshProjectionType::Spherical;
    AActor* NewActor = FDisplayClusterLightCardEditorHelper::SpawnStageActor(SpawnArgs);
    
    // 将新创建的灯光卡移动到计算出的球面坐标
    TArray<FDisplayClusterWeakStageActorPtr> ActorsToMove;
    ActorsToMove.Add(NewActor);
    LightCardHelper.MoveActorsTo(ActorsToMove, SphericalCoords);
}
```

## Demo 示例

一个最小化的可编译示例，展示如何在游戏运行时初始化并请求一次预览渲染。

```cpp
// MyNDisplayPreviewDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IDisplayClusterScenePreview.h"
#include "MyNDisplayPreviewDemo.generated.h"

UCLASS()
class MYPROJECT_API AMyNDisplayPreviewDemo : public AActor
{
    GENERATED_BODY()
    
public:
    AMyNDisplayPreviewDemo();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable, Category = "nDisplay Preview")
    void RequestPreviewRender();

private:
    int32 PreviewRendererId;
    FDelegateHandle RenderResultHandle;

    void OnPreviewRendered(FRenderTarget* RenderTarget);
};

// MyNDisplayPreviewDemo.cpp
#include "MyNDisplayPreviewDemo.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterScenePreviewEnums.h"

AMyNDisplayPreviewDemo::AMyNDisplayPreviewDemo()
{
    PrimaryActorTick.bCanEverTick = false;
    PreviewRendererId = INDEX_NONE;
}

void AMyNDisplayPreviewDemo::BeginPlay()
{
    Super::BeginPlay();
    
    if (IDisplayClusterScenePreview::IsAvailable())
    {
        IDisplayClusterScenePreview& PreviewModule = IDisplayClusterScenePreview::Get();
        PreviewRendererId = PreviewModule.CreateRenderer();
        
        // 尝试在场景中查找一个ADisplayClusterRootActor作为预览根
        TArray<AActor*> FoundActors;
        UGameplayStatics::GetAllActorsOfClass(GetWorld(), ADisplayClusterRootActor::StaticClass(), FoundActors);
        if (FoundActors.Num() > 0)
        {
            ADisplayClusterRootActor* DCRA = Cast<ADisplayClusterRootActor>(FoundActors[0]);
            FDisplayClusterRootActorPropertyOverrides Overrides;
            PreviewModule.SetRendererRootActor(PreviewRendererId, DCRA, Overrides);
        }
    }
}

void AMyNDisplayPreviewDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (IDisplayClusterScenePreview::IsAvailable() && PreviewRendererId != INDEX_NONE)
    {
        IDisplayClusterScenePreview& PreviewModule = IDisplayClusterScenePreview::Get();
        PreviewModule.DestroyRenderer(PreviewRendererId);
        PreviewRendererId = INDEX_NONE;
    }
    Super::EndPlay(EndPlayReason);
}

void AMyNDisplayPreviewDemo::RequestPreviewRender()
{
    if (!IDisplayClusterScenePreview::IsAvailable() || PreviewRendererId == INDEX_NONE)
    {
        return;
    }

    IDisplayClusterScenePreview& PreviewModule = IDisplayClusterScenePreview::Get();
    
    FDisplayClusterMeshProjectionRenderSettings Settings;
    Settings.ProjectionType = EDisplayClusterMeshProjectionType::UV; // 示例投影类型
    Settings.ViewLocation = GetActorLocation(); // 示例视图位置
    Settings.FOV = 90.0f;
    
    FIntPoint RenderSize(512, 512); // 小尺寸预览
    
    // 设置回调以接收渲染结果
    RenderResultHandle = PreviewModule.RenderQueued(
        PreviewRendererId, 
        Settings, 
        RenderSize, 
        FRenderResultDelegate::CreateUObject(this, &AMyNDisplayPreviewDemo::OnPreviewRendered)
    );
}

void AMyNDisplayPreviewDemo::OnPreviewRendered(FRenderTarget* RenderTarget)
{
    if (RenderTarget)
    {
        UE_LOG(LogTemp, Log, TEXT("nDisplay preview rendered successfully! Texture size: %dx%d"), 
            RenderTarget->GetSizeX(), RenderTarget->GetSizeY());
        // 这里可以将 RenderTarget 绑定到 UTextureRenderTarget2D 以显示在UI上，或用于其他用途。
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("nDisplay preview render failed."));
    }
    // 清除句柄（可选，取决于生命周期管理）
    RenderResultHandle.Reset();
}
```

## 模块依赖

从 `DisplayClusterScenePreview` 模块的构建文件分析，其独特依赖如下：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 提供编辑器相关的功能，如场景视图、Actor选择事件、蓝图编译事件等，用于实现场景预览和灯光卡编辑的交互逻辑。 |

**注**： nDisplay 插件整体依赖非常庞大且复杂，涉及渲染、媒体、网络、编辑器工具等多个子系统。`DisplayClusterScenePreview` 模块的依赖相对聚焦。其他核心模块如 `DisplayCluster`, `DisplayClusterProjection`, `DisplayClusterShaders` 等，可能依赖 `Renderer`, `RenderCore`, `MediaUtils`, `Networking` 等更底层的引擎模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 在MovieGraph和nDisplay中增加对EXR多图层格式的支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | nDisplay电影管线：将WarpBlendAlpha模式合并到WarpBlend模式中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复MRG中拓扑感知的相机命名；修复MPCDI/ICVFX着色器中的不透明alpha问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码回退路径中尊重非默认的DisplayGamma设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当GUI纹理尺寸小于视口尺寸时的闪烁问题。 |

### 维护评价

nDisplay 作为 Unreal Engine 虚拟制片战略的核心支柱之一，处于**极其活跃**的维护状态。
- **创建时间**： 始于 2018 年，是 UE4 时代为虚拟制片需求而生的老牌插件，已持续迭代约 8 年。
- **近期更新频率**： 从 git 记录看，**最近一个月（2026年5月）有5次实质性更新**，涵盖功能增强（EXR多图层）、Bug修复、着色器优化和电影管线整合。这表明 Epic 对其投入巨大。
- **活跃维护**： 是，不仅活跃，而且是 Epic 官方重点发展的领域。更新紧跟 UE5 新功能（如 MovieGraph、MPCDI标准）。
- **已知限制**： 由于其复杂性，配置和调试门槛较高。对网络同步和硬件（如同步信号发生器）有特定要求。
- **推荐使用**： **强烈推荐**给所有有专业级虚拟制片、沉浸式体验或多屏渲染需求的项目。它是 UE 在此领域的官方且成熟的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/nDisplay-in-Unreal-Engine/)（Unreal Engine 官方文档站有详细的nDisplay指南）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)