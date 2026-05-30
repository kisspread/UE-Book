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

GeometryCache 插件提供了对 **几何缓存动画** 的完整支持。它主要用于导入、播放和控制来自外部 DCC（数字内容创建）工具（如 Maya、Houdini）的逐帧几何体动画数据，最常见的格式是 Alembic (.abc)。

传统骨骼动画（Skeletal Mesh）适用于角色关节运动，但对于复杂的几何形变效果，如面部表情、布料模拟、流体、粒子特效或精确的产品动画，往往力不从心。Geometry Cache 通过存储每一帧独立的网格顶点数据来解决这个问题，能够实现任意复杂的、非拓扑结构的几何变形动画。该插件是 UE5 Alembic 导入流程的核心支持模块。

## 使用场景

- 你需要制作角色的高质量、高细节面部表情动画 → 使用 Geometry Cache 导入 DCC 工具中烘焙好的面部变形目标序列。
- 你在做一个产品展示应用，需要播放精确的机械装配或运动模拟动画 → 使用 Geometry Cache 导入模拟软件的输出。
- 你需要在游戏中实现高质量的布料、毛发或流体模拟效果 → 使用 Geometry Cache 导入 Houdini 等软件模拟出的逐帧几何体。
- 你有一个包含复杂拓扑变化（如分裂、合并）的特效动画 → Geometry Cache 是处理此类动画的理想选择。

## 蓝图用法

核心的交互通过 `UGeometryCacheComponent` 完成。在蓝图中，你可以将此组件添加到 Actor 上，并为其指定一个 `UGeometryCache` 资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 从头开始播放动画 | `UGeometryCacheComponent` |
| `PlayFromStart` | 从头开始播放（确保从第一帧开始） | `UGeometryCacheComponent` |
| `Pause` | 暂停当前动画播放 | `UGeometryCacheComponent` |
| `Stop` | 停止播放并将时间重置到开头 | `UGeometryCacheComponent` |
| `SetPlaybackSpeed` | 设置播放速度倍率（例如 `2.0` 为2倍速） | `UGeometryCacheComponent` |
| `SetLooping` | 设置是否循环播放 | `UGeometryCacheComponent` |
| `SetStartFrame` / `SetEndFrame` | 设置动画播放的起始/结束帧 | `UGeometryCacheComponent` |
| `SetGeometryCache` | 运行时更换正在播放的几何缓存资产 | `UGeometryCacheComponent` |
| `IsPlaying` | 查询当前是否正在播放 | `UGeometryCacheComponent` |
| `GetPlaybackSpeed` | 获取当前的播放速度倍率 | `UGeometryCacheComponent` |
| `GetLooping` | 查询是否设置了循环播放 | `UGeometryCacheComponent` |
| `GetAnimationTime` | 获取当前动画播放时间（秒） | `UGeometryCacheComponent` |
| `GetDuration` | 获取动画总时长（秒） | `UGeometryCacheComponent` |
| `GetNumberOfFrames` | 获取动画总帧数 | `UGeometryCacheComponent` |
| `GetCurrentFrame` | 获取当前播放的帧号 | `UGeometryCacheComponent` |

### 使用示例（蓝图描述）

1.  在你的 Actor 蓝图中，添加一个 `Geometry Cache Component`。
2.  在细节面板中，将 `Geometry Cache` 属性设置为你导入的 `.uasset` 文件。
3.  要开始播放，在 `BeginPlay` 事件后连接 `Play` 或 `PlayFromStart` 节点。
4.  要实现慢动作效果，可以在某个事件（如玩家按键）后，调用 `SetPlaybackSpeed` 并将速度设置为 `0.5`。
5.  要实现来回播放效果，可以结合 `GetAnimationTime`、`GetDuration` 和 `SetPlaybackSpeed`（设置为负数）来实现。
6.  使用 `Sequence` 节点或事件图表，根据 `OnFinished` 事件（如果组件提供了该委托）来触发后续逻辑。

## C++ 用法

C++ 用法主要围绕 `UGeometryCacheComponent` 类展开。

### 头文件引入

```cpp
#include "GeometryCacheComponent.h"
#include "GeometryCache.h"
```

### 基本用法

**创建并初始化组件（通常在 Actor 构造函数中）：**

```cpp
// MyActor.h
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
TObjectPtr<UGeometryCacheComponent> CacheComponent;

// MyActor.cpp
AMyActor::AMyActor()
{
    CacheComponent = CreateDefaultSubobject<UGeometryCacheComponent>(TEXT("GeometryCacheComp"));
    RootComponent = CacheComponent;
}

// 设置缓存资产（通常在 PostInitializeComponents 或 BeginPlay 中）
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 通过资产路径加载
    UGeometryCache* Cache = LoadObject<UGeometryCache>(nullptr, TEXT("/Game/Path/To/MyGeometryCache"));
    if (Cache)
    {
        CacheComponent->SetGeometryCache(Cache);
    }

    // 开始播放
    CacheComponent->Play();
    CacheComponent->SetLooping(true);
    CacheComponent->SetPlaybackSpeed(1.5f);
}
```

### 进阶用法

**精确控制播放位置和查询状态：**

```cpp
// 跳转到动画中间点
float HalfDuration = CacheComponent->GetDuration() * 0.5f;
CacheComponent->SetStartTime(HalfDuration); // 设置起始播放时间

// 根据帧号查询网格数据（用于程序化处理）
FFrameNumber TargetFrame = FFrameNumber(120);
if (CacheComponent->GetGeometryCache()->HasDataForFrameIndex(TargetFrame.Value))
{
    // ... 在此可以访问该帧的几何数据
}

// 在 Tick 中动态调整速度以实现交互式拉伸效果
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bShouldStretch)
    {
        float StretchFactor = CalculateStretchFactor(); // 自定义计算
        CacheComponent->SetPlaybackSpeed(StretchFactor);
    }
}
```

## Demo 示例

一个最小可编译的 Actor，加载并播放几何缓存动画。

**MyGeometryCacheActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGeometryCacheActor.generated.h"

class UGeometryCacheComponent;

UCLASS()
class AMyGeometryCacheActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGeometryCacheActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta = (AllowPrivateAccess = "true"))
    TObjectPtr<UGeometryCacheComponent> GeometryCacheComponent;
};
```

**MyGeometryCacheActor.cpp**
```cpp
#include "MyGeometryCacheActor.h"
#include "GeometryCacheComponent.h"
#include "GeometryCache.h"

AMyGeometryCacheActor::AMyGeometryCacheActor()
{
    GeometryCacheComponent = CreateDefaultSubobject<UGeometryCacheComponent>(TEXT("GeoCacheComp"));
    RootComponent = GeometryCacheComponent;
}

void AMyGeometryCacheActor::BeginPlay()
{
    Super::BeginPlay();

    // 假设资产路径为 "/Game/Demo/SM_DancingShape"
    const FString AssetPath = TEXT("/Game/Demo/SM_DancingShape");
    UGeometryCache* LoadedCache = LoadObject<UGeometryCache>(nullptr, *AssetPath);

    if (LoadedCache)
    {
        GeometryCacheComponent->SetGeometryCache(LoadedCache);
        GeometryCacheComponent->Play();
        UE_LOG(LogTemp, Log, TEXT("Started playing Geometry Cache: %s"), *AssetPath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Geometry Cache asset: %s"), *AssetPath);
    }
}
```

## 模块依赖

从 `GeometryCache` 模块的 Build.cs 分析，除标准依赖外，使用此插件需要以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 用于网格体处理相关的工具函数 |
| `UnrealEd` | **注意**：仅在编辑器环境下需要，用于资产导入、编辑器集成（如时间轴、视口）等。运行时打包时不应依赖此模块。 |

对于使用 `GeometryCacheEd`（编辑器功能）的项目，需确保项目构建目标已正确配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端代码，通过关联/解除关联事件减少冗余代码。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了一个更改（CL53913857）。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 另一次对视口客户端关联事件的重构。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式 `UE_LOG` 迁移至新的 `UE_LOGF` 宏，属于日志系统现代化更新。 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | 在 Sequencer（序列器）中添加了一个带有可操作时间轴的简单视图初始版本。 |

### 维护评价

- **活跃维护**：从 Git 记录看，该插件在近几个月内（截至 2026 年 5 月）仍有频繁的功能性更新和代码优化，表明处于**积极维护**状态。
- **创建与发展**：该插件于 2022 年从实验性模块正式移出，成为正式功能。至今约 4 年，功能已相当成熟和稳定。
- **已知问题**：文档中未提及严重的已知问题。其依赖于 `UnrealEd` 模块，意味着在编辑器环境外（如独立服务器）使用时需要特殊处理或分离编辑器功能。
- **推荐**：**强烈推荐**在任何需要播放高质量、逐帧几何体动画的场景中使用此插件。它是 UE5 处理此类需求的官方标准解决方案，文档和社区支持相对完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)