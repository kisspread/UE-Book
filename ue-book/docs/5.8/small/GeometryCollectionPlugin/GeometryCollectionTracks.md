# Geometry Collection

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何体集合 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

该插件为 UE5 引入了一套完整的**可破坏物体**（Destructible）工作流核心——`GeometryCollection`。它不仅仅是一个容器，而是一个用于存储、管理、模拟和缓存复杂物体破碎过程的系统。其核心功能包括：
1.  **几何体集合容器**：存储一个模型的“破碎版本”，包含多个碎块（Geometry Group）及其层级关系（Transform Hierarchy）。
2.  **物理模拟支持**：与 Chaos 物理引擎深度集成，用于实时计算物体的破碎、碰撞和碎块运动。
3.  **模拟缓存**：通过 `GeometryCollectionCache` 资产，将一次破碎模拟的结果记录下来，可以在 Sequencer 中精确回放，或用于避免重复计算。
4.  **动画控制**：通过 Sequencer 轨道（`GeometryCollectionTracks`），将破碎缓存作为动画片段进行播放控制。

**简言之，该插件是 UE5 Chaos 破坏系统（可破坏几何体）的运行时基础和 Sequencer 集成部分。**

## 使用场景

-   你在制作一个需要墙体、玻璃、家具等被击碎或压碎的游戏或过场动画 → 使用 `GeometryCollection` 制作可破坏物体，并利用 `GeometryCollectionCache` 缓存其破碎过程。
-   你需要在 Sequencer 过场动画中精确控制一个物体何时、以何种速度破碎并回放其过程 → 将缓存好的 `GeometryCollectionCache` 拖拽到 Sequencer 的 `GeometryCollectionTrack` 上。
-   你正在开发一个基于物理的解谜或破坏模拟游戏，需要大量可交互的破碎物体 → 该插件提供了底层的 `GeometryCollection` 数据结构和模拟接口。

## 蓝图用法

该插件的蓝图接口主要集中在 `GeometryCollectionTracks` 模块中，用于 Sequencer 的集成。在 Sequencer 编辑器中操作为主，但部分参数可从蓝图访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddNewAnimation` | 向 Sequencer 的几何体集合轨道中，在指定时间点添加一个新的动画（缓存）片段。 | `UMovieSceneGeometryCollectionTrack` |

### 使用示例（蓝图描述）

1.  **在 Sequencer 中使用**：
    1.  创建一个 `Level Sequence`。
    2.  将一个带有 `GeometryCollectionComponent` 的 Actor 添加到 Sequencer 中。
    3.  在 Sequencer 大纲中，找到该 Actor 的轨道，点击 `+` 号，选择 “Geometry Collection Track”。
    4.  在轨道上右键，选择 “Add Geometry Collection”，然后选择一个预录好的 `GeometryCollectionCache` 资产。
    5.  你可以通过移动和缩放轨道上的片段来控制破碎动画在时间线上的起止时间和播放速率。

2.  **从蓝图动态创建 Sequencer 动画**（概念描述）：
    ```cpp
    // 在C++中，通常通过Sequencer API或直接操作MovieScene对象来实现，
    // 纯蓝图直接创建复杂轨道较为困难，通常在编辑器内完成。
    // 获取一个有效的 Sequencer 和 GeometryCollectionComponent...
    UMovieSceneGeometryCollectionTrack* GeomTrack = ...; // 如何获取轨道
    FFrameNumber Time(...); // 设置关键帧时间
    UGeometryCollectionComponent* GeomComp = ...; // 目标组件
    GeomTrack->AddNewAnimation(Time, GeomComp); // 调用蓝图可调用函数
    ```

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneGeometryCollectionTrack.h"
#include "MovieSceneGeometryCollectionSection.h"
```

### 基本用法

以下代码展示了如何配置一个用于 Sequencer 的破碎动画参数。**(来源于 `MovieSceneGeometryCollectionSection.h`)**

```cpp
// 假设你已经有一个 UMovieSceneGeometryCollectionSection* Section;
FMovieSceneGeometryCollectionParams& Params = Section->Params;

// 1. 指定要使用的破碎缓存资产
FSoftObjectPath CachePath = FSoftObjectPath(TEXT("/Game/Path/To/MyCache.MyCache"));
Params.GeometryCollectionCache = CachePath;

// 2. 设置播放速率（1.0为原始速度）
Params.PlayRate = 1.0f;

// 3. 设置起始和结束帧偏移（相对于缓存数据）
Params.StartFrameOffset = FFrameNumber(0);
Params.EndFrameOffset = FFrameNumber(0); // 0表示不裁剪末尾

// 4. 获取调整播放速率后的总时长
float ActualDuration = Params.GetDuration();
```

### 进阶用法

通过 `GeometryCollectionTracks` 模块，在 C++ 中程序化地向 Sequencer 轨道添加动画片段。

```cpp
// 获取或创建 Sequencer 的 MovieScene
UMovieScene* MovieScene = ...;

// 为目标对象（如 Actor）添加轨道
UMovieSceneGeometryCollectionTrack* GeomTrack = MovieScene->AddTrack<UMovieSceneGeometryCollectionTrack>(ObjectBindingID);

// 创建一个新的 Section
UMovieSceneGeometryCollectionSection* NewSection = Cast<UMovieSceneGeometryCollectionSection>(GeomTrack->CreateNewSection());

// 配置 Section 参数 (同上)
NewSection->Params.GeometryCollectionCache = ...;
NewSection->Params.PlayRate = ...;

// 将 Section 添加到轨道并设置其时间范围
FFrameNumber SectionStartFrame(...);
FFrameNumber SectionEndFrame = SectionStartFrame + FFrameNumber(static_cast<int32>(NewSection->Params.GetDuration() * MovieScene->GetTickResolution().AsDecimal()));
NewSection->SetRange(TRange<FFrameNumber>(SectionStartFrame, SectionEndFrame));
GeomTrack->AddSection(*NewSection);
```

## Demo 示例

一个演示如何在 C++ 中创建 `UMovieSceneGeometryCollectionSection` 并配置参数的最小示例。

### GeometryCollectionDemoComponent.h
```cpp
#pragma once
#include "Components/ActorComponent.h"
#include "GeometryCollectionDemoComponent.generated.h"

class UMovieSceneGeometryCollectionSection;
class UGeometryCollectionCache;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UGeometryCollectionDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    // 在蓝图或构造函数中设置
    UPROPERTY(EditAnywhere, Category = "Geometry Collection")
    TSoftObjectPtr<UGeometryCollectionCache> CacheAsset;

    // 创建并配置一个 Sequencer 动画 Section 的演示函数
    UFUNCTION(BlueprintCallable, Category = "Geometry Collection")
    UMovieSceneGeometryCollectionSection* CreateDemoSequencerSection();

protected:
    virtual void BeginPlay() override;
};
```

### GeometryCollectionDemoComponent.cpp
```cpp
#include "GeometryCollectionDemoComponent.h"
#include "MovieSceneGeometryCollectionSection.h"

UMovieSceneGeometryCollectionSection* UGeometryCollectionDemoComponent::CreateDemoSequencerSection()
{
    // 1. 创建一个新的 Section 对象 (注意：在实际 Sequencer 工作流中，它属于某个 Track)
    UMovieSceneGeometryCollectionSection* NewSection = NewObject<UMovieSceneGeometryCollectionSection>();

    if (NewSection && !CacheAsset.IsNull())
    {
        // 2. 配置参数
        FMovieSceneGeometryCollectionParams& Params = NewSection->Params;
        Params.GeometryCollectionCache = CacheAsset.ToSoftObjectPath();
        Params.PlayRate = 0.5f; // 半速播放
        Params.StartFrameOffset = FFrameNumber(10); // 从第10帧开始
        // 3. 验证时长
        float Duration = Params.GetDuration();
        UE_LOG(LogTemp, Log, TEXT("配置的破碎动画时长: %f 秒 (PlayRate: 0.5)"), Duration);
    }
    return NewSection;
}

void UGeometryCollectionDemoComponent::BeginPlay()
{
    Super::BeginPlay();
    // 可以在BeginPlay中尝试创建
    // CreateDemoSequencerSection();
}
```

## 模块依赖

该插件的模块主要依赖引擎核心的 Sequencer 和动画系统。使用者需要根据所使用的功能，在自己的模块 `.Build.cs` 中添加相应依赖。

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心框架 |
| `MovieSceneTracks` | Sequencer 标准轨道基础 |
| `GeometryCollectionEngine` | 运行时几何体集合组件和缓存 |
| `Chaos` | Chaos 物理引擎核心（破碎模拟基础） |
| `Dataflow` | 用于几何体集合节点构建的数据流图框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 本地化警告 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | Dataflow 相关功能更新 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 回滚了一次代码提交 |
| 2026-05-14 | `88fb5004` | Dataflow: | Dataflow 相关功能更新 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | 新增 Dataflow 节点，用于为几何体集合创建外部碰撞 |

### 维护评价

-   **创建时间**：2018年创建，历史悠久。
-   **近期更新**：最近一次更新在2026年5月，内容主要是与 `Dataflow` 模块协同的功能添加和 bug 修复。
-   **活跃状态**：**维护中**。作为 Chaos 破坏系统的核心部分，它仍在持续接收更新，以支持新的工具流（如 Dataflow）和引擎版本。
-   **已知问题/限制**：作为实验性（`IsBetaVersion=true`）且默认禁用的插件，其 API 和工作流可能随版本发生变化。
-   **推荐使用**：**推荐**用于 UE5 的破坏效果开发。它是官方 Chaos 破坏系统的组成部分，是实现高级破碎效果和 Sequencer 动画控制的标准方式。在使用时需留意其实验性标签，并关注版本更新说明。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)