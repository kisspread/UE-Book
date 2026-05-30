# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多屏同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 插件用于驱动基于 UE5 的沉浸式显示环境。其核心功能是将单个 UE5 应用程序的渲染输出，通过多台 PC（集群）同步，分别输出到多个物理显示器或投影仪上，形成一个无缝拼接的大视场角画面（如 CAVE、LED 墙、穹顶投影等）。它解决了在超大分辨率或特殊几何形状的显示设备上进行实时渲染的问题，并提供几何校正、色彩校准、多视图同步等高级功能。

简单来说：如果你需要将游戏或应用画面同时、同步地输出到几十甚至上百个屏幕上，并且需要精确控制每个屏幕上的画面内容（如边缘融合、曲面校正），就需要 nDisplay。

## 使用场景

- **电影虚拟制作 (Virtual Production)**：在 LED 墙 Volume 中，nDisplay 负责同步驱动构成整面墙的多个 LED 面板，确保虚拟场景与真实摄影机运动完美匹配。
- **主题公园/沉浸式体验**：为驾驶模拟器、飞行模拟器或全景投影体验提供多路同步输出。
- **建筑可视化/数字展厅**：将建筑模型或艺术装置渲染到复杂的多屏或环形屏幕上。
- **舞台表演/现场活动**：控制舞台背景的大型 LED 屏幕集群。

## 蓝图用法

nDisplay 的蓝图接口主要用于配置和控制渲染集群的运行时状态。由于 nDisplay 是一个大型插件，其蓝图节点分布在多个模块中，以下是一些核心的功能分类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start` | 启动 nDisplay 集群会话 | `UDisplayCluster` |
| `Stop` | 停止当前 nDisplay 集群会话 | `UDisplayCluster` |
| `SetViewportArea` | 设置指定视口（屏幕）的渲染区域和偏移 | `UDisplayCluster` |
| `GetGameViewportSize` | 获取主游戏视口的尺寸（用于计算偏移） | `UDisplayCluster` |
| `SetRootActor` | 设置场景中作为渲染原点的根 Actor | `UDisplayCluster` |

**注意**：具体可用节点需在编辑器中通过“nDisplay”类别查找。配置集群拓扑（哪些PC、屏幕如何连接）通常通过编辑器中的 nDisplay 配置工具完成，而非蓝图。

## C++ 用法

以下示例展示了如何使用 `DisplayClusterLightCardEditorShaders` 模块中的 `FDisplayClusterMeshProjectionRenderer` 进行非线性投影渲染。这对于编辑器工具或自定义视口效果很有用。

### 头文件引入

```cpp
#include "DisplayClusterMeshProjectionRenderer.h"
```

### 基本用法

创建一个渲染器实例并渲染场景。

```cpp
// 来源: Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterLightCardEditorShaders/Public/DisplayClusterMeshProjectionRenderer.h
// 创建一个网格投影渲染器
FDisplayClusterMeshProjectionRenderer MeshRenderer;

// 假设我们有一个场景和画布
FSceneInterface* Scene = ...;
FCanvas* Canvas = ...;

// 配置渲染设置
FDisplayClusterMeshProjectionRenderSettings Settings;
Settings.ProjectionType = EDisplayClusterMeshProjectionType::Azimuthal; // 使用球面等距投影
Settings.RenderType = EDisplayClusterMeshProjectionOutput::Color; // 输出颜色

// 执行渲染
MeshRenderer.Render(Canvas, Scene, Settings);
```

### 进阶用法

管理渲染的 Actor 列表，并设置投影过滤器。

```cpp
// 来源: Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterLightCardEditorShaders/Public/DisplayClusterMeshProjectionRenderer.h
FDisplayClusterMeshProjectionRenderer MeshRenderer;
AActor* MyActor = ...;

// 添加 Actor 到渲染列表
MeshRenderer.AddActor(MyActor);

// 添加带有过滤器的 Actor（只渲染特定组件）
MeshRenderer.AddActor(MyActor, [](const UPrimitiveComponent* Comp)
{
    // 只渲染标记为特定Tag的组件
    return Comp->ComponentHasTag(TEXT("Renderable"));
});

// 在渲染前，可以配置投影设置
FDisplayClusterMeshProjectionRenderSettings Settings;
Settings.ProjectionType = EDisplayClusterMeshProjectionType::UV;
Settings.ProjectionTypeSettings.UVProjectionIndex = 0;

// 进行渲染
FCanvas Canvas(...);
MeshRenderer.Render(&Canvas, Scene, Settings);

// 清理
MeshRenderer.ClearScene();
```

### 投影与反投影

```cpp
// 来源: Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterLightCardEditorShaders/Public/DisplayClusterMeshProjectionRenderer.h
// 静态函数：将视图空间坐标投影到指定投影类型的空间
FVector ViewPos = FVector(100, 50, 10);
FVector ProjectedPos = FDisplayClusterMeshProjectionRenderer::ProjectViewPosition(
    ViewPos,
    EDisplayClusterMeshProjectionType::Azimuthal
);

// 反投影：将投影后的坐标转换回视图空间
FVector RecoveredViewPos = FDisplayClusterMeshProjectionRenderer::UnprojectViewPosition(
    ProjectedPos,
    EDisplayClusterMeshProjectionType::Azimuthal
);

// 或者使用可传递的 Transform 对象
FDisplayClusterMeshProjectionTransform Transform(EDisplayClusterMeshProjectionType::Azimuthal, ViewMatrix);
FVector WorldPos = FVector(100, 200, 300);
FVector ProjectedWorld = Transform.ProjectPosition(WorldPos);
FVector BackToWorld = Transform.UnprojectPosition(ProjectedWorld);
```

## Demo 示例

一个最小化的 nDisplay C++ 配置示例，展示如何从 C++ 侧配置和启动一个简单的单节点集群。

```cpp
// MyNDisplayManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNDisplayManager.generated.h"

class UDisplayCluster;

UCLASS()
class MYPROJECT_API AMyNDisplayManager : public AActor
{
    GENERATED_BODY()

public:
    AMyNDisplayManager();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // nDisplay 核心对象
    UPROPERTY()
    TObjectPtr<UDisplayCluster> DisplayClusterComponent;

    // 配置资产路径
    UPROPERTY(EditAnywhere, Category = "nDisplay")
    FSoftObjectPath ClusterConfigurationPath;
};

// MyNDisplayManager.cpp
#include "MyNDisplayManager.h"
#include "DisplayCluster.h"
#include "DisplayClusterConfiguration.h"

AMyNDisplayManager::AMyNDisplayManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyNDisplayManager::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建 DisplayCluster 组件
    DisplayClusterComponent = NewObject<UDisplayCluster>(this);

    // 2. 加载配置资产（通常在编辑器中预先创建好 .ndisplay 资产）
    UDisplayClusterConfiguration* Config = Cast<UDisplayClusterConfiguration>(
        ClusterConfigurationPath.TryLoad()
    );

    if (Config && DisplayClusterComponent)
    {
        // 3. 应用配置并启动集群
        DisplayClusterComponent->ApplyConfiguration(Config);
        DisplayClusterComponent->Start();
        UE_LOG(LogTemp, Log, TEXT("nDisplay cluster started with config: %s"), *ClusterConfigurationPath.ToString());
    }
}

void AMyNDisplayManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (DisplayClusterComponent)
    {
        DisplayClusterComponent->Stop();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

nDisplay 插件本身包含 29 个模块，模块间依赖复杂。当您的项目需要使用 nDisplay 时，通常无需直接依赖其所有内部模块。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 的核心运行时模块，管理集群会话和渲染同步。 |
| `DisplayClusterConfiguration` | 定义和存储 nDisplay 集群配置数据（.ndisplay 资产）。 |
| `DisplayClusterProjection` | 实现各种几何投影校正算法（MPCDI、Warping等）。 |
| `DisplayClusterMedia` | 集成媒体框架，处理视频输入输出（依赖 `D3D12RHI`）。 |
| `SharedMemoryMedia` | 提供基于共享内存的高性能帧数据传输（依赖 `D3D12RHI`）。 |
| `DisplayClusterWarp` | 处理高级网格扭曲（Warping）和边缘融合（Blending）。 |

**给使用者的建议**：您的游戏模块通常只需要依赖 `DisplayCluster` 和 `DisplayClusterConfiguration`。只有在需要自定义媒体管线或深度定制投影算法时，才需要依赖其他子模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 在 MovieGraph 中添加 EXR 多图层渲染支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 电影管线中合并了 WarpBlendAlpha 模式到 WarpBlend 模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知的相机命名问题；修复了 MPCDI/ICVFX 着色器中不透明度的问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在输出帧编码回退路径中未正确应用非默认 DisplayGamma 的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时可能出现的闪烁问题。 |

### 维护评价

- **活跃维护**：从近期提交历史看，nDisplay 在 2026 年 5 月仍有密集的功能更新和 Bug 修复，特别是与电影管线（MovieGraph）的集成以及渲染稳定性的改进。
- **长期支持**：该插件自 2018 年（UE 4.20 时期）引入，是 Epic 用于虚拟制作的核心技术之一，有超过 8 年的历史，属于成熟且持续维护的“企业级”功能。
- **推荐使用**：对于需要同步多屏渲染、沉浸式显示或虚拟制作的项目，nDisplay 是官方推荐且功能完备的解决方案。虽然启用它（`EnabledByDefault: false`）和配置有一定复杂度，但其稳定性和持续更新保证了可靠性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档]() （注：.uplugin 中 `DocsURL` 为空，请查阅 UE 官方文档站搜索 “nDisplay”）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)