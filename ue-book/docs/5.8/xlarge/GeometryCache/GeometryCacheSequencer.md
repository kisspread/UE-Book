# Geometry Cache

> Support for distilled Geometry animations（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 几何缓存 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

GeometryCache 插件用于支持导入、管理和播放“几何缓存”动画。几何缓存是一种预烘焙的、逐帧的网格体顶点数据序列，常用于导入由 DCC 工具（如 Maya、Houdini、Blender）导出的复杂动画，例如流体模拟、布料模拟、粒子效果或复杂的角色变形动画。与传统骨骼动画不同，几何缓存直接存储每一帧的网格体几何数据，能够实现传统骨骼系统难以达到的高度复杂和精细的动画效果。该插件的核心功能是处理 Alembic (.abc) 等格式的几何缓存文件，并将其转化为 Unreal Engine 中的可播放资产。

## 使用场景

- 你从 Houdini 或 Maya 导出了一段复杂的流体或布料模拟动画（例如 `.abc` 格式），需要在 UE 中播放 → 使用 GeometryCache 插件导入并创建 `GeometryCache` 资产。
- 你需要为一个项目创建高度复杂的、非程序化的角色变形动画，例如角色缓慢融化或岩石碎裂的效果 → 使用 GeometryCache 存储每帧的顶点位置。
- 你需要在 Sequencer 中对预烘焙的几何缓存动画进行精确的时间线控制、编辑或混合 → 使用 `GeometryCacheTracks` 和 `GeometryCacheSequencer` 模块。
- 你的几何缓存文件非常大，需要流式加载以节省内存 → 使用 `GeometryCacheStreamer` 模块。

## 蓝图用法

该插件主要通过资产类型（`GeometryCache`）和组件（`GeometryCacheComponent`）提供蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 开始播放几何缓存动画。 | `UGeometryCacheComponent` |
| `Stop` | 停止播放几何缓存动画。 | `UGeometryCacheComponent` |
| `SetPlaybackSpeed` | 设置播放速度倍率。 | `UGeometryCacheComponent` |
| `SetLooping` | 设置是否循环播放。 | `UGeometryCacheComponent` |
| `SetStartTimeOffset` | 设置播放的起始时间偏移。 | `UGeometryCacheComponent` |
| `GetPlaybackSpeed` | 获取当前播放速度。 | `UGeometryCacheComponent` |
| `IsPlaying` | 检查动画是否正在播放。 | `UGeometryCacheComponent` |
| `SetGeometryCache` | 动态设置组件要播放的 `GeometryCache` 资产。 | `UGeometryCacheComponent` |
| `GetGeometryCache` | 获取当前播放的 `GeometryCache` 资产引用。 | `UGeometryCacheComponent` |

### 使用示例（蓝图描述）

1.  **创建和播放**：在场景中添加一个 `GeometryCacheComponent`（通常附属于一个 Actor）。在组件细节面板中，将 `GeometryCache` 属性设置为一个已导入的 `GeometryCache` 资产。勾选 `Play` 属性或在 BeginPlay 事件中调用 `Play` 节点，即可在运行时播放动画。
2.  **动态控制**：在事件图表中，可以通过获取 `GeometryCacheComponent` 的引用来调用 `Stop`、`SetPlaybackSpeed`（例如传入 2.0 实现快进）、`SetLooping`（设置为 true 以循环）等节点，实现对动画播放的实时控制。
3.  **事件响应**：可以绑定 `OnPlaybackFinished` 等事件（如果存在），在动画播放完成时执行特定逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCache.h"
#include "GeometryCacheComponent.h"
```

### 基本用法

以下示例展示了如何在 C++ 中动态创建和控制一个 `GeometryCacheComponent` 的播放。

```cpp
// 在你的 Actor 头文件 (.h) 中
class AMyGeometryCacheActor : public AActor
{
    // ...
private:
    UPROPERTY(VisibleAnywhere)
    UGeometryCacheComponent* GeometryCacheComponent;
};

// 在你的 Actor 实现文件 (.cpp) 中
#include "MyGeometryCacheActor.h"
#include "GeometryCacheComponent.h"

AMyGeometryCacheActor::AMyGeometryCacheActor()
{
    GeometryCacheComponent = CreateDefaultSubobject<UGeometryCacheComponent>(TEXT("GeoCacheComponent"));
    RootComponent = GeometryCacheComponent;
}

void AMyGeometryCacheActor::BeginPlay()
{
    Super::BeginPlay();

    // 假设已在编辑器中为组件指定了 GeometryCache 资产
    if (GeometryCacheComponent->GetGeometryCache())
    {
        // 设置属性
        GeometryCacheComponent->SetPlaybackSpeed(1.5f);
        GeometryCacheComponent->SetLooping(true);
        GeometryCacheComponent->SetStartTimeOffset(0.0f);

        // 开始播放
        GeometryCacheComponent->Play();
    }
}
```

### 进阶用法

结合 Sequencer 模块，可以在 C++ 中程序化地创建或修改几何缓存动画轨道。

```cpp
#include "GeometryCacheTrackEditor.h" // 来自 GeometryCacheSequencer 模块

// 假设你有一个 ULevelSequence 对象，并且你知道要绑定到哪个 ObjectBinding 的 GUID
FGuid ObjectBinding = /* ... */;

// 获取 Sequencer 模块
ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>("Sequencer");

// 注意：通常不直接实例化 TrackEditor，而是通过 Sequencer 的上下文操作。
// 更常见的操作是修改 UMovieSceneGeometryCacheSection 的属性。
// 例如，在某个已有的 Geometry Cache Section 上调整播放范围或循环设置。
// 具体操作依赖于 Sequencer 的内部 API 和上下文。
```

## Demo 示例

一个最小的 Actor，包含一个 `GeometryCacheComponent` 并在构造时播放。

```cpp
// GeometryCacheDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GeometryCacheDemoActor.generated.h"

class UGeometryCacheComponent;

UCLASS()
class AGeometryCacheDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AGeometryCacheDemoActor();

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "GeometryCache", meta = (AllowPrivateAccess = "true"))
	UGeometryCacheComponent* GeoCacheComp;
};
```

```cpp
// GeometryCacheDemoActor.cpp
#include "GeometryCacheDemoActor.h"
#include "GeometryCacheComponent.h"

AGeometryCacheDemoActor::AGeometryCacheDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;

	GeoCacheComp = CreateDefaultSubobject<UGeometryCacheComponent>(TEXT("GeometryCacheComponent"));
	RootComponent = GeoCacheComp;
}

void AGeometryCacheDemoActor::BeginPlay()
{
	Super::BeginPlay();

	// 如果组件中已设置了 GeometryCache 资产，则开始播放
	if (GeoCacheComp->GetGeometryCache())
	{
		GeoCacheComp->Play();
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("AGeometryCacheDemoActor: No GeometryCache asset assigned to the component."));
	}
}
```

## 模块依赖

从各模块的 Build.cs 中提取的独特依赖：

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 用于网格体处理相关的通用工具函数和类型。 |
| `Sequencer` | `GeometryCacheSequencer` 模块依赖它来注册和管理 Sequencer 轨道编辑器。 |
| `MovieScene` | `GeometryCacheTracks` 模块依赖它来定义电影场景轨道和区段。 |
| `RenderCore` | 可能用于底层的渲染资源管理。 |

**注意**：其他依赖（如 `Core`, `Engine`, `CoreUObject` 等）为标准依赖，已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口相关重构，涉及客户端通知。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了一次提交。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口相关重构（与 cf7610df 相同内容，可能是多次提交或分支合并）。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 宏迁移到新版 UE_LOGF 宏。 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 简单视图及可工具化时间线功能初始发布。 |

### 维护评价

GeometryCache 插件处于**活跃维护**状态。它最初从实验性插件迁移而来，目前是 UE5 标准功能的一部分。从 git 历史看，最近几个月有多次更新，包括 Sequencer 功能的增强和底层代码的现代化（如日志宏迁移）。这些更新表明 Epic Games 正在持续改进和维护该插件，以支持更复杂的内容创建管线。该插件功能稳定，是处理高保真预烘焙动画（如 Alembic 文件）的官方推荐方案，可以放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache/Tests) (如果存在)