# Geometry Cache

> Support for distilled Geometry animations

| 属性 | 值 |
|---|---|
| 中文名 | 几何缓存 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

GeometryCache 插件的核心作用是**支持几何体缓存动画**。传统的网格体动画（骨骼网格体）通过骨骼驱动网格体变形，而几何体缓存则是将网格体顶点在每一帧的精确位置预先计算并存储起来。播放时，直接用缓存数据更新顶点位置，无需复杂的骨骼计算。这种方法非常适合于从 DCC 工具（如 Maya、Houdini）导出的复杂顶点动画、布料模拟、流体模拟等烘焙好的动画序列。插件从实验性状态毕业并成为标准运行时功能，旨在为这类“烘焙”动画提供高性能的播放方案。

## 使用场景

- 你从 Houdini 或其他 DCC 工具导出了一个复杂的流体模拟或粒子效果的 Alembic (.abc) 文件，希望在 UE 中作为几何体缓存高效回放。
- 你有一个需要高精度顶点动画的角色（例如面部表情），希望通过烘焙为缓存来获得稳定的性能和质量。
- 你使用 Sequencer 编辑动画，需要在时间线上精确控制几何体缓存动画的播放、循环和混合。

## 蓝图用法

主要功能通过 `UGeometryCacheComponent` 暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 开始播放几何体缓存动画 | `UGeometryCacheComponent` |
| `Pause` | 暂停播放 | `UGeometryCacheComponent` |
| `Stop` | 停止播放并重置到起点 | `UGeometryCacheComponent` |
| `SetPlaybackSpeed` | 设置播放速度 | `UGeometryCacheComponent` |
| `SetLooping` | 设置是否循环播放 | `UGeometryCacheComponent` |
| `GetPlaybackSpeed` | 获取当前播放速度 | `UGeometryCacheComponent` |
| `IsPlaying` | 检查是否正在播放 | `UGeometryCacheComponent` |
| `GetAnimationTime` | 获取当前动画播放时间 | `UGeometryCacheComponent` |
| `SetAnimationTime` | 设置动画播放到指定时间 | `UGeometryCacheComponent` |

### 使用示例（蓝图描述）

1. 在 Actor 蓝图中添加 `UGeometryCacheComponent` 组件。
2. 在组件的“详细信息”面板中，将“Geometry Cache”属性设置为你导入或创建的 `UGeometryCache` 资产。
3. 在事件图表中，例如在 `BeginPlay` 事件后，调用 `Play` 节点。
4. 你也可以通过 `SetPlaybackSpeed`、`SetLooping` 等节点在运行时动态控制播放行为。

## C++ 用法

核心 C++ 接口围绕 `UGeometryCacheComponent` 和 `UGeometryCache` 资产展开。

### 头文件引入

```cpp
#include "GeometryCacheComponent.h"
#include "GeometryCache.h"
```

### 基本用法

创建并控制一个几何体缓存组件的播放。
(代码示例逻辑基于 UE 典型的组件用法)

```cpp
// 假设在某个 Actor 类中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 通过蓝图或代码创建并获取 GeometryCacheComponent
    UGeometryCacheComponent* GeoCacheComp = FindComponentByClass<UGeometryCacheComponent>();
    if (GeoCacheComp)
    {
        // 设置缓存资产 (通常在构造函数或蓝图中完成)
        // GeoCacheComp->SetGeometryCache(MyGeometryCacheAsset);

        // 播放动画
        GeoCacheComp->Play();

        // 设置为循环播放，播放速度为 1.5 倍
        GeoCacheComp->SetLooping(true);
        GeoCacheComp->SetPlaybackSpeed(1.5f);
    }
}
```

### 进阶用法

通过 C++ 精确控制动画时间和监听播放状态。

```cpp
// 在 Tick 函数或其他地方更新动画
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    UGeometryCacheComponent* GeoCacheComp = FindComponentByClass<UGeometryCacheComponent>();
    if (GeoCacheComp && GeoCacheComp->IsPlaying())
    {
        // 获取当前播放进度 (0.0 - 1.0)
        float Progress = GeoCacheComp->GetAnimationTime() / GeoCacheComp->GetDuration();
        UE_LOG(LogTemp, Log, TEXT("Geometry Cache Progress: %f"), Progress);

        // 在特定条件下跳转到动画末尾
        if (SomeCondition)
        {
            GeoCacheComp->SetAnimationTime(GeoCacheComp->GetDuration());
            GeoCacheComp->Pause();
        }
    }
}
```

## Demo 示例

一个最简单的几何体缓存 Actor，演示了组件的基本创建和播放控制。

### MyGeometryCacheActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGeometryCacheActor.generated.h"

class UGeometryCacheComponent;

UCLASS()
class MYPROJECT_API AMyGeometryCacheActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGeometryCacheActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Geometry Cache")
    UGeometryCacheComponent* GeometryCacheComponent;

    UFUNCTION(BlueprintCallable, Category = "Geometry Cache")
    void StartPlayback();

    UFUNCTION(BlueprintCallable, Category = "Geometry Cache")
    void StopAndResetPlayback();
};
```

### MyGeometryCacheActor.cpp

```cpp
#include "MyGeometryCacheActor.h"
#include "GeometryCacheComponent.h"

AMyGeometryCacheActor::AMyGeometryCacheActor()
{
    PrimaryActorTick.bCanEverTick = true;

    GeometryCacheComponent = CreateDefaultSubobject<UGeometryCacheComponent>(TEXT("GeometryCacheComponent"));
    RootComponent = GeometryCacheComponent;

    // 默认设置为循环播放
    GeometryCacheComponent->SetLooping(true);
}

void AMyGeometryCacheActor::BeginPlay()
{
    Super::BeginPlay();
    // 在 BeginPlay 后自动开始播放
    GeometryCacheComponent->Play();
}

void AMyGeometryCacheActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 这里可以添加运行时控制逻辑
}

void AMyGeometryCacheActor::StartPlayback()
{
    if (GeometryCacheComponent)
    {
        GeometryCacheComponent->Play();
    }
}

void AMyGeometryCacheActor::StopAndResetPlayback()
{
    if (GeometryCacheComponent)
    {
        GeometryCacheComponent->Stop();
    }
}
```

## 模块依赖

要使用 GeometryCache 插件，你的模块通常需要依赖其核心模块。以下是该插件独特且重要的依赖。

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 核心运行时模块，包含 `UGeometryCache`, `UGeometryCacheComponent` 等基础类。 |
| `GeometryCacheStreamer` | 负责几何体缓存的异步流式加载和管理，优化大缓存资产的内存使用。 |
| `GeometryCacheTracks` | 提供 Sequencer 和动画系统集成所需的轨道资产（如 `UMovieSceneGeometryCacheTrack`）。 |
| `MeshUtilitiesCommon` | 提供与网格体处理相关的通用工具函数，被 `GeometryCache` 核心模块依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口相关的代码重构，优化了客户端的关联通知逻辑。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了之前的一次提交（CL53913857）。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 与 `cfb610df` 内容相同的提交，可能是合并冲突后的重新提交。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将部分 UE_LOG 日志宏迁移到新的 UE_LOGF 格式。 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 更新，引入了可工具化时间线的简化视图初始版本。 |

### 维护评价

该插件自 2022 年 1 月从实验性状态移出后，已成为引擎的稳定标准功能。从近期提交记录看（2026 年仍有更新），插件仍在与引擎核心的视口和 Sequencer 系统同步维护，进行代码重构、格式迁移和功能对齐。虽然近期的更新不涉及几何体缓存本身的重大功能变更，但这表明它仍然是活跃维护的引擎组件，与 Sequencer 的集成良好。目前没有明显的废弃迹象，推荐在有相关需求时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache/Tests) (如果存在)