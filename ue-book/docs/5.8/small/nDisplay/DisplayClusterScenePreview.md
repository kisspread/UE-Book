# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染系统 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、蓝图资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🆕（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于实现**多台PC同步集群渲染**的系统，支持单声道和立体声模式。它解决的核心问题是：如何将一个虚拟场景同时渲染到多个物理显示器或投影仪上，并保持完美同步。

这个插件主要应用于以下场景：
1. **大型沉浸式显示环境**：如CAVE系统、穹顶影院、大型LED屏幕
2. **多通道投影**：多台投影仪拼接成一个大的连续画面
3. **虚拟制片**：在影视制作中使用LED墙实时显示背景
4. **模拟器训练**：驾驶舱、飞行模拟器等多屏显示系统
5. **主题公园体验**：多屏幕互动娱乐设施

nDisplay通过配置文件定义显示集群的拓扑结构（屏幕位置、形状、投影方式），然后协调所有参与渲染的PC，确保它们同步渲染各自负责的视口部分，最终拼接成一个完整的画面。

## 使用场景

- 你需要创建一个**3面CAVE系统**用于建筑可视化 → 使用nDisplay配置3个墙面的投影参数
- 你在制作**虚拟制片**场景，需要将UE场景实时渲染到LED墙上 → 使用nDisplay配置LED墙的几何形状和投影映射
- 你在开发**驾驶模拟器**，需要同步渲染前、左、右三个屏幕 → 使用nDisplay定义三个屏幕的视角和同步参数
- 你需要**颜色校准**多个投影仪 → 使用nDisplay的颜色分级模块进行统一调整
- 你需要**录制多屏幕内容** → 使用nDisplay的MoviePipeline模块进行同步录制

## 蓝图用法

nDisplay插件本身是运行时模块，主要通过配置文件和C++ API进行控制。蓝图中可直接使用的节点主要集中在场景预览和灯光卡编辑功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRendererRootActor` | 为预览渲染器设置根Actor | `IDisplayClusterScenePreview` |
| `AddActorToRenderer` | 将Actor添加到渲染器场景 | `IDisplayClusterScenePreview` |
| `RemoveActorFromRenderer` | 从渲染器场景移除Actor | `IDisplayClusterScenePreview` |
| `RenderQueued` | 排队渲染预览图像 | `IDisplayClusterScenePreview` |
| `SpawnStageActor` | 在舞台上生成新的Actor | `FDisplayClusterLightCardEditorHelper` |
| `AddLightCardsToRootActor` | 将灯光卡添加到根Actor | `FDisplayClusterLightCardEditorHelper` |
| `MoveActorsToPixel` | 将灯光卡移动到屏幕像素位置 | `FDisplayClusterLightCardEditorHelper` |

### 使用示例（蓝图描述）

**场景：在编辑器中预览nDisplay配置**
1. 使用`CreateRenderer`创建预览渲染器实例
2. 调用`SetRendererRootActor`设置你的nDisplay根Actor
3. 使用`AddActorToRenderer`添加需要预览的灯光卡Actor
4. 调用`RenderQueued`请求渲染预览图像
5. 在委托中接收渲染结果并显示在UI中

**场景：移动灯光卡到球面坐标**
1. 创建`FDisplayClusterLightCardEditorHelper`实例
2. 设置投影模式（如球面投影）
3. 调用`MoveActorsTo`传入球面坐标系参数
4. 灯光卡会自动移动到指定的球面位置

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterScenePreview.h"
#include "DisplayClusterLightCardEditorHelper.h"
```

### 基本用法

```cpp
// 来源: DisplayClusterScenePreviewModule.h
// 创建并配置一个场景预览渲染器

// 获取场景预览模块接口
IDisplayClusterScenePreview& ScenePreviewModule = IDisplayClusterScenePreview::Get();

// 创建渲染器实例
int32 RendererId = ScenePreviewModule.CreateRenderer();

// 设置根Actor（假设已获取指针）
ADisplayClusterRootActor* MyRootActor = /* ... */;
FDisplayClusterRootActorPropertyOverrides PropertyOverrides;
ScenePreviewModule.SetRendererRootActor(RendererId, MyRootActor, PropertyOverrides);

// 添加灯光卡到渲染器
ADisplayClusterLightCardActor* LightCard = /* ... */;
ScenePreviewModule.AddActorToRenderer(RendererId, LightCard);

// 排队渲染预览
FDisplayClusterMeshProjectionRenderSettings RenderSettings;
RenderSettings.ViewLocation = FVector::ZeroVector;
FIntPoint ImageSize(512, 512);

FRenderResultDelegate ResultDelegate;
ResultDelegate.BindLambda([RendererId](FRenderTarget* RenderTarget)
{
    if (RenderTarget)
    {
        // 处理渲染结果
        UE_LOG(LogTemp, Log, TEXT("渲染完成，渲染器ID: %d"), RendererId);
    }
});

ScenePreviewModule.RenderQueued(RendererId, RenderSettings, ImageSize, ResultDelegate);

// 清理资源
ScenePreviewModule.DestroyRenderer(RendererId);
```

### 进阶用法

```cpp
// 来源: DisplayClusterLightCardEditorHelper.h
// 使用灯光卡编辑助手进行球面坐标系操作

// 创建灯光卡编辑助手
FDisplayClusterLightCardEditorHelper LightCardHelper(RendererId);
LightCardHelper.SetProjectionMode(EDisplayClusterMeshProjectionType::UV);
LightCardHelper.SetRootActor(*MyRootActor);

// 定义球面坐标系中的位置
FDisplayClusterLightCardEditorHelper::FSphericalCoordinates SphericalCoords;
SphericalCoords.Radius = 1000.0f;          // 距离中心点的距离
SphericalCoords.Inclination = FMath::DegreesToRadians(45.0f);  // 俯仰角（0到180度）
SphericalCoords.Azimuth = FMath::DegreesToRadians(90.0f);     // 方位角（-180到180度）

// 移动灯光卡到指定球面坐标
TArray<FDisplayClusterWeakStageActorPtr> LightCards;
LightCards.Add(MakeWeakObjectPtr(LightCard));
LightCardHelper.MoveActorsTo(LightCards, SphericalCoords);

// 转换坐标系
FVector CartesianPosition = SphericalCoords.AsCartesian();
UE_LOG(LogTemp, Log, TEXT("笛卡尔坐标: %s"), *CartesianPosition.ToString());

// 坐标拖拽操作（模拟编辑器中的拖拽）
FIntPoint DragPixelPos(256, 256);
FSceneView SceneView; // 从当前视口获取
FVector DragWidgetOffset = FVector::ZeroVector;

LightCardHelper.DragActors(LightCards, DragPixelPos, SceneView,
    FDisplayClusterLightCardEditorHelper::ECoordinateSystem::Spherical,
    DragWidgetOffset, EAxisList::XY);
```

## Demo 示例

```cpp
// DisplayClusterPreviewDemo.h
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterScenePreview.h"
#include "DisplayClusterLightCardEditorHelper.h"
#include "GameFramework/Actor.h"
#include "DisplayClusterPreviewDemo.generated.h"

UCLASS()
class ADisplayClusterPreviewDemo : public AActor
{
    GENERATED_BODY()

public:
    ADisplayClusterPreviewDemo();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 场景预览渲染器ID
    int32 PreviewRendererId = INDEX_NONE;

    // 灯光卡编辑助手
    TUniquePtr<FDisplayClusterLightCardEditorHelper> LightCardHelper;

    // 预览图像纹理
    UPROPERTY()
    UTexture2D* PreviewTexture;

    // 渲染结果委托
    FRenderResultDelegate RenderResultDelegate;

    // 委托回调函数
    void OnPreviewRenderCompleted(FRenderTarget* RenderTarget);

public:
    UFUNCTION(BlueprintCallable, Category = "nDisplay Demo")
    void StartPreviewRender(ADisplayClusterRootActor* RootActor);

    UFUNCTION(BlueprintCallable, Category = "nDisplay Demo")
    void MoveLightCardToSphericalPosition(ADisplayClusterLightCardActor* LightCard, float Radius, float Inclination, float Azimuth);

    UFUNCTION(BlueprintCallable, Category = "nDisplay Demo")
    UTexture2D* GetLastPreviewTexture() const { return PreviewTexture; }
};
```

```cpp
// DisplayClusterPreviewDemo.cpp
#include "DisplayClusterPreviewDemo.h"
#include "Engine/Texture2D.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterLightCardActor.h"

ADisplayClusterPreviewDemo::ADisplayClusterPreviewDemo()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ADisplayClusterPreviewDemo::BeginPlay()
{
    Super::BeginPlay();

    // 绑定渲染结果委托
    RenderResultDelegate.BindUObject(this, &ADisplayClusterPreviewDemo::OnPreviewRenderCompleted);
}

void ADisplayClusterPreviewDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 销毁预览渲染器
    if (PreviewRendererId != INDEX_NONE && IDisplayClusterScenePreview::IsAvailable())
    {
        IDisplayClusterScenePreview::Get().DestroyRenderer(PreviewRendererId);
        PreviewRendererId = INDEX_NONE;
    }

    Super::EndPlay(EndPlayReason);
}

void ADisplayClusterPreviewDemo::StartPreviewRender(ADisplayClusterRootActor* RootActor)
{
    if (!IDisplayClusterScenePreview::IsAvailable() || !RootActor)
    {
        UE_LOG(LogTemp, Warning, TEXT("场景预览模块不可用或根Actor无效"));
        return;
    }

    IDisplayClusterScenePreview& ScenePreview = IDisplayClusterScenePreview::Get();

    // 创建或重新使用渲染器
    if (PreviewRendererId == INDEX_NONE)
    {
        PreviewRendererId = ScenePreview.CreateRenderer();
    }

    // 配置渲染器
    FDisplayClusterRootActorPropertyOverrides Overrides;
    ScenePreview.SetRendererRootActor(PreviewRendererId, RootActor, Overrides);

    // 创建灯光卡编辑助手（使用同一个渲染器）
    LightCardHelper = MakeUnique<FDisplayClusterLightCardEditorHelper>(PreviewRendererId);
    LightCardHelper->SetRootActor(*RootActor);

    // 请求渲染
    FDisplayClusterMeshProjectionRenderSettings RenderSettings;
    RenderSettings.ViewLocation = FVector::ZeroVector;
    FIntPoint PreviewSize(1024, 1024);

    ScenePreview.RenderQueued(PreviewRendererId, RenderSettings, PreviewSize, RenderResultDelegate);

    UE_LOG(LogTemp, Log, TEXT("开始nDisplay预览渲染，渲染器ID: %d"), PreviewRendererId);
}

void ADisplayClusterPreviewDemo::MoveLightCardToSphericalPosition(
    ADisplayClusterLightCardActor* LightCard, 
    float Radius, 
    float Inclination, 
    float Azimuth)
{
    if (!LightCardHelper.IsValid() || !LightCard)
    {
        UE_LOG(LogTemp, Warning, TEXT("灯光卡助手或灯光卡无效"));
        return;
    }

    // 设置球面坐标
    FDisplayClusterLightCardEditorHelper::FSphericalCoordinates SphericalCoords;
    SphericalCoords.Radius = Radius;
    SphericalCoords.Inclination = FMath::DegreesToRadians(Inclination);
    SphericalCoords.Azimuth = FMath::DegreesToRadians(Azimuth);

    // 转换为灯光卡Actor数组
    TArray<FDisplayClusterWeakStageActorPtr> LightCards;
    LightCards.Add(MakeWeakObjectPtr(LightCard));

    // 移动灯光卡
    LightCardHelper->MoveActorsTo(LightCards, SphericalCoords);

    UE_LOG(LogTemp, Log, TEXT("灯光卡已移动到球面坐标: 半径=%.1f, 俯仰=%.1f°, 方位=%.1f°"), 
        Radius, Inclination, Azimuth);
}

void ADisplayClusterPreviewDemo::OnPreviewRenderCompleted(FRenderTarget* RenderTarget)
{
    if (RenderTarget)
    {
        // 将渲染目标转换为纹理
        // 注意：实际项目中需要根据渲染目标格式进行适当处理
        UE_LOG(LogTemp, Log, TEXT("预览渲染完成，渲染目标大小: %dx%d"), 
            RenderTarget->GetSizeX(), RenderTarget->GetSizeY());

        // 这里可以将RenderTarget转换为UTexture2D或直接用于显示
        // 简化示例：记录渲染完成
        PreviewTexture = NewObject<UTexture2D>();
        
        // 触发蓝图事件（如果有需要）
        // OnPreviewRenderedEvent.Broadcast(PreviewTexture);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("预览渲染失败"));
    }
}
```

## 模块依赖

从 Build.cs 分析，nDisplay 插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器集成和编辑器专用功能 |
| `EditorWidgets` | 编辑器UI控件 |
| `LevelEditor` | 关卡编辑器集成 |
| `D3D12RHI` | Direct3D 12 渲染硬件接口（用于共享内存媒体） |

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 添加EXR多层支持，用于电影图和nDisplay的集成 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将WarpBlendAlpha模式合并到WarpBlend中，简化电影管道配置 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复拓扑感知相机命名和MPCDI/ICVFX着色器中的不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码回退时的Gamma值处理 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复GUI纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** - nDisplay插件处于积极维护状态。最近更新集中在以下方面：
1. **功能增强**：添加EXR多层支持，改进电影管道集成
2. **Bug修复**：解决各种渲染问题和兼容性问题
3. **性能优化**：修复闪烁和渲染问题
4. **API简化**：合并相关功能模块

该插件创建于2018年，已有约8年历史，是Epic Games官方支持的成熟产品。它广泛应用于虚拟制片、主题公园、模拟训练等专业领域，是UE5中最重要的多显示器渲染解决方案。

虽然`EnabledByDefault=false`，但这只是因为该插件需要特定的硬件配置和场景需求，不代表它是实验性或不可靠的。实际上，这是Epic Games在商业项目中广泛使用的技术。

**推荐使用**：如果你的项目需要多屏幕同步渲染、投影映射或沉浸式显示环境，nDisplay是最佳选择。它提供了完整的工具链，从编辑器配置到运行时控制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)（基于一般UE文档结构）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)