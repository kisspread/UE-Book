# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 物理缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Sequencer支持） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

该插件的核心是提供一套完整的系统，用于**录制（Record）和回放（Playback）基于 Chaos 物理引擎的模拟结果**。它解决的核心问题是：如何精确地重现复杂的物理交互（如破碎、布料模拟、刚体堆叠等），以便在电影制作、游戏玩法测试或过场动画中进行反复、一致地播放，而无需每次都重新运行昂贵的物理模拟。

它将模拟过程中的物理状态（位置、旋转、速度等）以缓存（Cache）的形式存储在 `UChaosCacheCollection` 资产中，并通过 `AChaosCacheManager` Actor 在场景中驱动物体的运动，从而实现物理动画的“录制”与“回放”。

## 使用场景

- **电影与过场动画制作**：需要精确、可重复播放的破碎或物理特效镜头。
- **游戏玩法测试与回放**：录制玩家与环境的物理交互（如破坏场景），用于回放、分析或作为游戏内演出的一部分。
- **性能优化**：预先录制复杂的物理场景，在运行时直接播放缓存结果，避免实时计算开销。
- **跨版本一致性**：确保物理效果在不同引擎版本或不同硬件上播放结果一致。

## 蓝图用法

该插件的蓝图功能主要集中在通过 `Take Recorder` 进行物理模拟的录制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ChaosCacheManager` (属性) | 指定要作为录制源的 `AChaosCacheManager` Actor | `UTakeRecorderChaosCacheSource` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `AChaosCacheManager` Actor 并配置好需要缓存的物理组件。
2.  打开 `Take Recorder` 窗口。
3.  点击 “+” 添加源，在 “Chaos” 分类下选择 “Chaos Cache”。
4.  在新添加的源属性中，将上一步的 `AChaosCacheManager` Actor 指定给 `Chaos Cache` 属性。
5.  开始录制，场景中的物理模拟将被记录到关卡序列（Level Sequence）中的 Chaos Cache 轨道上。

## C++ 用法

### 头文件引入

```cpp
#include "Chaos/CacheManager.h"
#include "Chaos/CacheCollection.h"
```

### 基本用法

创建和使用 `AChaosCacheManager` 与 `UChaosCacheCollection`。

```cpp
// 假设 World 指针有效
UWorld* World = GetWorld();

// 1. 创建一个缓存管理器 Actor
AChaosCacheManager* CacheManager = World->SpawnActor<AChaosCacheManager>();

// 2. 创建或加载一个缓存收集资产
UChaosCacheCollection* CacheCollection = NewObject<UChaosCacheCollection>();
// 或从资产加载: UChaosCacheCollection* CacheCollection = LoadObject<UChaosCacheCollection>(nullptr, TEXT("/Game/MyCaches.MyCaches"));

// 3. 将缓存收集资产分配给管理器
CacheManager->SetCacheCollection(CacheCollection);

// 4. 设置缓存模式 (Record 或 Playback)
CacheManager->SetCacheMode(ECacheMode::Record); // 开始录制
// CacheManager->SetCacheMode(ECacheMode::Playback); // 开始回放
```

### 进阶用法

结合 Sequencer 进行程序化控制。

```cpp
#include "Chaos/ChaosCacheTrack.h"
#include "MovieScene.h"

// 获取 Sequencer 和缓存轨道的引用（示例）
UMovieSceneChaosCacheTrack* ChaosCacheTrack = ...;
UMovieSceneSequence* Sequence = ...;

// 在指定帧添加一个关键帧，将当前的 ChaosCacheManager 状态绑定到序列
FFrameNumber KeyTime(100); // 第100帧
FKeyPropertyResult Result = ChaosCacheTrack->AddKey(KeyTime, CacheManager);
```

## Demo 示例

一个最小示例，展示在 C++ 中如何设置一个用于录制物理模拟的缓存管理器。

```cpp
// MyPhysicsCacheDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPhysicsCacheDemo.generated.h"

class AChaosCacheManager;
class UChaosCacheCollection;
class UStaticMeshComponent;

UCLASS()
class AMyPhysicsCacheDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyPhysicsCacheDemo();

protected:
    virtual void BeginPlay() override;

private:
    // 要录制的物理网格体
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> PhysicsMesh;

    // 缓存管理器
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<AChaosCacheManager> CacheManager;

    // 缓存收集资产 (在编辑器中设置)
    UPROPERTY(EditAnywhere)
    TObjectPtr<UChaosCacheCollection> CacheCollectionAsset;
};
```

```cpp
// MyPhysicsCacheDemo.cpp
#include "MyPhysicsCacheDemo.h"
#include "Chaos/CacheManager.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

AMyPhysicsCacheDemo::AMyPhysicsCacheDemo()
{
    PrimaryActorTick.bCanEverTick = false;

    PhysicsMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PhysicsMesh"));
    RootComponent = PhysicsMesh;
    PhysicsMesh->SetSimulatePhysics(true); // 启用物理模拟

    static ConstructorHelpers::FObjectFinder<UStaticMesh> MeshAsset(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (MeshAsset.Succeeded())
    {
        PhysicsMesh->SetStaticMesh(MeshAsset.Object);
    }
}

void AMyPhysicsCacheDemo::BeginPlay()
{
    Super::BeginPlay();

    // 如果缓存收集资产已设置，则创建并配置缓存管理器
    if (CacheCollectionAsset)
    {
        CacheManager = GetWorld()->SpawnActor<AChaosCacheManager>();
        if (CacheManager)
        {
            CacheManager->SetCacheCollection(CacheCollectionAsset);
            // 可以在此处进一步配置管理器要缓存哪些组件
            // CacheManager->CacheComponents(...);
            CacheManager->SetCacheMode(ECacheMode::Record); // 开始录制
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。此插件深度集成 Unreal 的 Sequencer 和 Take Recorder 系统，这些是引擎的标准模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复几何体集合缓存适配器处理根代理时的逻辑问题。 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 向 Chaos 事件中继添加尾随数据。 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | 内容浏览器新增“物理”添加菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

该插件属于**实验性**状态（`IsExperimentalVersion=true` 且 `EnabledByDefault=false`），表明 Epic 可能仍在评估其稳定性和最终 API 设计。

**积极信号**：
- **维护活跃**：最近（2026年5月）仍有实质性代码更新，包括 bug 修复（几何体集合、浮点警告）和功能增强（事件中继），证明其仍在积极开发中。
- **集成深入**：插件与 Unreal 核心系统（Sequencer, Take Recorder）深度绑定，表明它是一个重要的内部工具链组件。

**需要注意**：
- **实验性警告**：API 和功能可能会在未来版本中发生破坏性变更。
- **默认禁用**：需要手动在插件管理器中启用才能使用。

**推荐**：对于需要在项目中精确录制和回放 Chaos 物理模拟的开发者，此插件是目前官方提供的唯一方案，值得尝试和关注。但鉴于其实验性状态，不建议用于对稳定性要求极高的生产环境核心路径中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- 官方文档：暂无
- 测试用例：源码中未包含公共测试路径，可能位于引擎测试目录内部。