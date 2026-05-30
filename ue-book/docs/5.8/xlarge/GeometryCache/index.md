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

GeometryCache 插件用于在 Unreal Engine 中导入和播放预先烘焙的几何体动画序列。它解决了实时计算大量复杂网格变形（如布料、流体、头发模拟）所带来的性能问题。通过将 DCC 软件（如 Maya, Houdini）中模拟并导出的几何体动画序列（通常为 Alembic .abc 格式）导入为“几何缓存”资产，引擎可以高效地播放这些动画，而无需进行实时物理模拟。它本质上是一个高效的网格序列播放器。

## 使用场景

*   **影视与过场动画**：播放从特效软件（如 Houdini）导出的复杂模拟动画，如爆炸、烟雾、流体。
*   **角色表现**：为角色添加复杂的次级动画，如逼真的头发、衣物飘动和面部细微表情，这些动画由离线工具生成。
*   **过场动画与定格动画**：实现精确的、由关键帧驱动的逐帧动画，避免物理引擎的不确定性。
*   **资产优化**：对于极其复杂的单帧模型（如 3D 扫描），可以将其序列化为缓存进行动画播放，以节省内存。

## 模块列表

| 模块 | 类型 | 简述 |
|---|---|---|
| `GeometryCache` | Runtime | 核心运行时模块，提供 `UGeometryCache` 资产和 `UGeometryCacheComponent`，负责几何缓存的加载、存储和播放逻辑。 |
| `GeometryCacheEd` | Runtime | 编辑器支持模块，提供资产导入器、工厂和编辑器界面，用于将 Alembic 文件导入为几何缓存资产。 |
| `GeometryCacheSequencer` | Runtime | Sequencer 集成模块，提供 `UGeometryCacheSection` 和相关的自定义轨道，用于在 Sequencer 时间轴中控制几何缓存的播放。 |
| `GeometryCacheStreamer` | Runtime | 流式加载模块，负责管理几何缓存数据的异步流式加载，优化内存使用和加载性能。 |
| `GeometryCacheTracks` | Runtime | 提供 Sequencer 动画轨道的具体实现，是 `GeometryCacheSequencer` 模块中数据类型定义的核心。 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` / `Stop` / `Pause` | 控制几何缓存组件的播放、停止和暂停。 | `UGeometryCacheComponent` |
| `SetPlaybackSpeed` | 设置几何缓存的播放速度倍率。 | `UGeometryCacheComponent` |
| `GetAnimationTime` / `GetPlaybackSpeed` | 获取当前动画播放时间和播放速度。 | `UGeometryCacheComponent` |
| `SetLooping` | 设置动画是否循环播放。 | `UGeometryCacheComponent` |

### 使用示例（蓝图描述）

1.  将 `UGeometryCacheComponent` 添加到 Actor。
2.  将导入的 `UGeometryCache` 资产赋给该组件的 `GeometryCache` 属性。
3.  使用事件图表（Event Graph）或 Sequencer 控制组件的 `Play`、`Stop` 等节点来触发动画播放。
4.  可在运行时通过 `SetPlaybackSpeed` 动态调整动画播放速度。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheComponent.h"
#include "GeometryCache.h"
```

### 基本用法

操作几何缓存组件并播放动画。
```cpp
// 获取或创建一个几何缓存组件
UGeometryCacheComponent* CacheComp = MyActor->FindComponentByClass<UGeometryCacheComponent>();
if (!CacheComp)
{
    CacheComp = NewObject<UGeometryCacheComponent>(MyActor);
    CacheComp->RegisterComponent();
}

// 设置要播放的几何缓存资产
UGeometryCache* MyCacheAsset = LoadObject<UGeometryCache>(nullptr, TEXT("/Game/Path/To/MyGeometryCache"));
CacheComp->SetGeometryCache(MyCacheAsset);

// 设置属性并播放
CacheComp->SetLooping(true);
CacheComp->SetPlaybackSpeed(1.0f);
CacheComp->Play();
```

### 进阶用法

监听几何缓存播放结束的委托。
```cpp
// 绑定播放结束事件
CacheComp->OnGeometryCacheFinished.AddDynamic(this, &AMyActor::OnCachePlaybackFinished);

// 回调函数
void AMyActor::OnCachePlaybackFinished()
{
    UE_LOG(LogTemp, Log, TEXT("Geometry cache playback finished."));
    // 执行后续逻辑，如播放下一个动画或销毁Actor
}
```

## Demo 示例

### MyGeometryCacheActor.h
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyGeometryCacheActor.generated.h"

class UGeometryCacheComponent;

UCLASS()
class AMyGeometryCacheActor : public AActor
{
    GENERATED_BODY()
public:
    AMyGeometryCacheActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "GeometryCache")
    UGeometryCacheComponent* CacheComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "GeometryCache")
    bool bAutoPlay = true;

protected:
    virtual void BeginPlay() override;
};
```

### MyGeometryCacheActor.cpp
```cpp
#include "MyGeometryCacheActor.h"
#include "GeometryCacheComponent.h"

AMyGeometryCacheActor::AMyGeometryCacheActor()
{
    PrimaryActorTick.bCanEverTick = true;
    CacheComponent = CreateDefaultSubobject<UGeometryCacheComponent>(TEXT("GeoCacheComp"));
    RootComponent = CacheComponent;
}

void AMyGeometryCacheActor::BeginPlay()
{
    Super::BeginPlay();
    if (bAutoPlay)
    {
        CacheComponent->Play();
    }
}
```

## 模块依赖

您的项目模块若需使用 GeometryCache 插件的完整功能（特别是编辑器导入功能），可能需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 核心运行时功能，是使用几何缓存组件的基础。 |
| `MeshUtilitiesCommon` | 用于网格处理的通用工具，`GeometryCacheEd` 导入器可能依赖它进行网格数据处理。 |

*（注：`GeometryCacheEd` 依赖 `UnrealEd`，但这是编辑器模块，且 `UnrealEd` 是编辑器插件的常见依赖，故不单独列出。）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构：优化客户端关联/断开关联的通知逻辑，减少重复代码。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 代码回退。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 同 `cfb610df`，是本次重构的一部分。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，从 `UE_LOG` 切换到 `UE_LOGF`。 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 功能更新：发布可工具化时间轴的简单视图初始版本。 |

### 维护评价

**活跃维护**。GeometryCache 插件自 2022 年从实验性状态转为正式插件后，一直作为引擎的一部分被持续维护。从近期提交历史看，更新非常频繁（最近提交在 2026 年 5 月），并且涵盖了核心功能（Sequencer）增强和引擎底层重构（Viewport，日志宏）。这表明 Epic Games 仍在积极维护此插件，并随引擎主干一同演进。推荐有几何缓存动画需求的项目使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache/Tests)