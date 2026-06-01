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
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

GeometryCache 插件提供了一套完整的**预烘焙几何体动画**播放系统。它将网格顶点在每一帧的完整快照（位置、法线、切线、UV、颜色、运动向量）存储为连续采样数据，在运行时直接回放，而不需要实时模拟或骨骼驱动。

这解决了一个核心问题：**当动画涉及大规模顶点变形（如布料、流体、毛发、刚体碎片）时，骨骼网格体或变形目标无法高效表达这类效果**。GeometryCache 通过将 DCC 工具（Houdini、Maya、Blender 等）中模拟好的结果"烘焙"为 Alembic/USD 文件，导入引擎后直接播放，既保证了视觉效果的精确还原，又将运行时计算降到最低。

插件内部包含：
- **多轨道架构**：单个 GeometryCache 可包含多条独立轨道（对应 DCC 中的多个物体/LOD）
- **流式加载系统**：大文件按 Chunk 分段异步加载，避免一次性占用过多内存
- **Huffman 压缩编解码器（V1）**：使用差分预测 + 霍夫曼编码大幅压缩帧数据
- **帧间插值/外推**：支持拓扑不变时的顶点位置插值，以及基于运动向量的拓扑变化外推
- **Niagara 集成**：支持在 Niagara 粒子系统中批量渲染几何缓存实例

## 使用场景

- 你从 Houdini 导出了一段刚体破碎/布料模拟的 Alembic 文件 → 用 GeometryCache 导入并播放
- 你需要在游戏运行时播放一个复杂的环境动画（如地面塌陷、建筑变形）→ 用 GeometryCacheComponent
- 你想在 Niagara 粒子系统中用预制的几何体动画替代粒子 Mesh → 用 Niagara GeometryCache Renderer
- 你需要 Sequencer 时间轴中精确控制几何体动画的播放、混合和事件 → 用 GeometryCache Sequencer 模块
- 你有一个大型几何缓存文件（数 GB）不想全部载入内存 → 用 GeometryCacheStreamer 流式加载

## 蓝图用法

GeometryCache 插件的核心蓝图 API 集中在 `UGeometryCacheComponent` 上，提供完整的播放控制。`UGeometryCache` 资产本身也有少量可查询的蓝图接口。

### 核心播放控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 从当前位置开始播放 | `UGeometryCacheComponent` |
| `PlayFromStart` | 从头开始播放 | `UGeometryCacheComponent` |
| `PlayReversed` | 从当前位置反向播放 | `UGeometryCacheComponent` |
| `PlayReversedFromEnd` | 从末尾开始反向播放 | `UGeometryCacheComponent` |
| `Pause` | 暂停播放 | `UGeometryCacheComponent` |
| `Stop` | 停止播放（重置状态） | `UGeometryCacheComponent` |

### 播放状态查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsPlaying` | 是否正在播放 | `UGeometryCacheComponent` |
| `IsPlayingReversed` | 是否反向播放中 | `UGeometryCacheComponent` |
| `IsLooping` | 是否循环播放 | `UGeometryCacheComponent` |
| `GetPlaybackSpeed` | 获取播放速度倍率 | `UGeometryCacheComponent` |
| `GetPlaybackDirection` | 获取播放方向（1.0 或 -1.0） | `UGeometryCacheComponent` |

### 播放参数设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLooping` | 设置是否循环 | `UGeometryCacheComponent` |
| `SetPlaybackSpeed` | 设置播放速度（0~512） | `UGeometryCacheComponent` |
| `SetStartTimeOffset` | 设置起始时间偏移（秒） | `UGeometryCacheComponent` |
| `SetInterpolateFrames` | 启用帧间插值（拓扑不变时） | `UGeometryCacheComponent` |
| `SetExtrapolateFrames` | 启用帧外推（拓扑变化时） | `UGeometryCacheComponent` |
| `SetMotionVectorScale` | 设置运动向量缩放系数 | `UGeometryCacheComponent` |
| `SetGeometryCache` | 运行时替换几何缓存资产 | `UGeometryCacheComponent` |

### 时间与帧信息

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAnimationTime` | 获取当前动画时间（含偏移） | `UGeometryCacheComponent` |
| `GetElapsedTime` | 获取已流逝时间（不含偏移） | `UGeometryCacheComponent` |
| `GetDuration` | 获取动画总时长（秒） | `UGeometryCacheComponent` |
| `GetNumberOfFrames` | 获取总帧数 | `UGeometryCacheComponent` |
| `GetNumberOfTracks` | 获取轨道数量 | `UGeometryCacheComponent` |

### 手动 Tick 控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TickAtThisTime` | 手动指定时间点进行 Tick | `UGeometryCacheComponent` |
| `SetManualTick` | 切换手动/自动 Tick 模式 | `UGeometryCacheComponent` |

### 外观覆盖

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetOverrideWireframeColor` | 启用线框颜色覆盖 | `UGeometryCacheComponent` |
| `SetWireframeOverrideColor` | 设置线框覆盖颜色 | `UGeometryCacheComponent` |
| `GetWireframeOverrideColor` | 获取当前线框覆盖颜色 | `UGeometryCacheComponent` |

### 使用示例（蓝图描述）

**基本播放控制：**
1. 在 Actor 上添加 `GeometryCacheComponent`
2. 将 GeometryCache 资产拖入 `GeometryCache` 属性槽
3. 在 BeginPlay 中连接 `SetLooping(true)` → `SetPlaybackSpeed(1.0)` → `Play`

**事件驱动播放：**
1. 创建自定义事件（如 "StartAnimation"）
2. 事件内调用 `SetStartTimeOffset(0)` → `PlayFromStart`
3. 用 `IsPlaying` 节点配合 DoOnce 检测播放开始，用 `GetElapsedTime` 检测播放结束

**手动 Tick 控制（用于 Sequencer 集成）：**
1. 先调用 `SetManualTick(true)`
2. 在需要更新时调用 `TickAtThisTime(Time, true, false, false)`

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCache.h"
#include "GeometryCacheComponent.h"
#include "GeometryCacheTrack.h"
#include "GeometryCacheTrackStreamable.h"
#include "GeometryCacheMeshData.h"
#include "GeometryCacheSceneProxy.h"
```

### 基本用法：查询几何缓存数据

从 `UGeometryCache` 资产中获取指定时间点的网格数据。来源：`Classes/GeometryCache.h`。

```cpp
// 获取 GeometryCache 资产的网格数据
UGeometryCache* MyCache = LoadObject<UGeometryCache>(nullptr, TEXT("/Game/MyGeometryCache"));

if (MyCache)
{
    // 查询持续时间
    float Duration = MyCache->CalculateDuration();
    
    // 获取起止帧
    int32 StartFrame = MyCache->GetStartFrame();
    int32 EndFrame = MyCache->GetEndFrame();
    
    // 获取指定时间的帧号
    int32 FrameAtTime = MyCache->GetFrameAtTime(0.5f);
    
    // 获取指定时间的网格数据
    TArray<FGeometryCacheMeshData> MeshDataArray;
    MyCache->GetMeshDataAtTime(0.5f, MeshDataArray);
    
    for (const FGeometryCacheMeshData& MeshData : MeshDataArray)
    {
        UE_LOG(LogTemp, Log, TEXT("Vertices: %d, Indices: %d, Batches: %d"),
            MeshData.Positions.Num(),
            MeshData.Indices.Num(),
            MeshData.BatchesInfo.Num());
    }
}
```

### 基本用法：组件播放控制

`UGeometryCacheComponent` 继承自 `UMeshComponent`，提供与蓝图等价的 C++ 控制接口。来源：`Classes/GeometryCacheComponent.h`。

```cpp
// 获取组件引用
UGeometryCacheComponent* CacheComp = MyActor->FindComponentByClass<UGeometryCacheComponent>();

if (CacheComp)
{
    // 设置循环和速度
    CacheComp->SetLooping(true);
    CacheComp->SetPlaybackSpeed(1.5f);
    
    // 启用帧间插值（拓扑不变时平滑过渡）
    CacheComp->SetInterpolateFrames(true);
    
    // 设置运动向量缩放（用于运动模糊）
    CacheComp->SetMotionVectorScale(1.0f);
    
    // 开始播放
    CacheComp->Play();
    
    // 运行时查询状态
    float CurrentTime = CacheComp->GetAnimationTime();
    float Elapsed = CacheComp->GetElapsedTime();
    float Dur = CacheComp->GetDuration();
    int32 NumFrames = CacheComp->GetNumberOfFrames();
    int32 NumTracks = CacheComp->GetNumberOfTracks();
    
    UE_LOG(LogTemp, Log, TEXT("Time: %.2f, Elapsed: %.2f, Duration: %.2f"),
        CurrentTime, Elapsed, Dur);
}
```

### 进阶用法：手动 Tick 与精确时间控制

当需要与 Sequencer 或自定义时间线精确同步时，使用手动 Tick 模式。来源：`Classes/GeometryCacheComponent.h`。

```cpp
UGeometryCacheComponent* CacheComp = GetGeometryCacheComponent();

// 切换为手动 Tick
CacheComp->SetManualTick(true);

// 在自定义 Tick 中手动推进动画
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 累积时间
    CurrentAnimTime += DeltaTime * PlaybackSpeed;
    
    // 手动驱动组件更新
    CacheComp->TickAtThisTime(
        CurrentAnimTime,
        true,   // bInIsRunning
        false,  // bInBackwards
        true    // bInIsLooping
    );
}

// 随机跳转到指定时间
CacheComp->SetCurrentTime(2.5f);

// 帧级控制
int32 FrameIndex = CacheComp->GetFrameAtTime(1.0f);
float FrameTime = CacheComp->GetTimeAtFrame(30);
```

### 进阶用法：运行时替换几何缓存资产

来源：`Classes/GeometryCacheComponent.h`。

```cpp
UGeometryCacheComponent* CacheComp = GetGeometryCacheComponent();

// 加载新的几何缓存资产
UGeometryCache* NewCache = LoadObject<UGeometryCache>(nullptr, TEXT("/Game/NewAnimation"));

// 运行时替换（返回是否成功）
bool bSuccess = CacheComp->SetGeometryCache(NewCache);

if (bSuccess)
{
    CacheComp->PlayFromStart();
}
```

### 进阶用法：使用 FGeometryCacheConstantTopologyWriter 程序化创建几何缓存

这是引擎内部用于从代码生成几何缓存资产的高级 API。来源：`Public/GeometryCacheConstantTopologyWriter.h`。

```cpp
#if WITH_EDITOR
#include "GeometryCacheConstantTopologyWriter.h"
#include "GeometryCache.h"

void CreateGeometryCacheProgrammatically()
{
    UGeometryCache* NewCache = NewObject<UGeometryCache>();
    
    // 配置编码参数
    UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter::FConfig Config;
    Config.FPS = 30.0f;
    Config.PositionPrecision = 0.001f;  // 位置精度 0.001cm
    Config.TextureCoordinatesNumberOfBits = 10;
    
    // 创建 writer（会清空已有轨道）
    UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter Writer(*NewCache, Config);
    
    // 添加材质
    Writer.AddMaterials({Material1, Material2});
    
    // 创建轨道 writer
    auto& TrackWriter = Writer.AddTrackWriter(FName("MainTrack"));
    
    // 设置顶点索引（拓扑不变，只设置一次）
    TrackWriter.Indices = { 0, 1, 2, 2, 3, 0 }; // 三角形索引
    TrackWriter.UVs = { {0,0}, {1,0}, {1,1}, {0,1} };
    TrackWriter.Colors = { FColor::White, FColor::White, FColor::White, FColor::White };
    
    // 准备多帧位置数据
    TArray<TArray<FVector3f>> AllFramePositions;
    for (int32 Frame = 0; Frame < 100; ++Frame)
    {
        TArray<FVector3f> FramePositions;
        // 生成每帧的顶点位置...
        AllFramePositions.Add(MoveTemp(FramePositions));
    }
    
    // 写入并关闭轨道
    TrackWriter.WriteAndClose(MakeArrayView(AllFramePositions));
}
#endif
```

### 进阶用法：从已有网格体创建几何缓存

来源：`Public/GeometryCacheConstantTopologyWriter.h` 中的辅助函数。

```cpp
#if WITH_EDITOR
#include "GeometryCacheConstantTopologyWriter.h"
#include "SkeletalMesh.h"
#include "StaticMesh.h"

// 从 SkeletalMesh 创建
void CreateFromSkeletalMesh(UGeometryCache* OutCache, USkeletalMesh* SkelMesh)
{
    UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter Writer(*OutCache);
    
    // 自动从 SkeletalMesh 提取索引、UV、材质等
    int32 TrackIndex = UE::GeometryCacheHelpers::AddTrackWriterFromSkinnedAsset(Writer, *SkelMesh);
    
    if (TrackIndex != INDEX_NONE)
    {
        auto& TrackWriter = Writer.GetTrackWriter(TrackIndex);
        // 填充帧位置数据后调用
        TrackWriter.WriteAndClose(AllFramePositions);
    }
}

// 从 StaticMesh 创建
void CreateFromStaticMesh(UGeometryCache* OutCache, UStaticMesh* StatMesh)
{
    UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter Writer(*OutCache);
    
    int32 TrackIndex = UE::GeometryCacheHelpers::AddTrackWriterFromStaticMesh(Writer, *StatMesh);
    
    if (TrackIndex != INDEX_NONE)
    {
        auto& TrackWriter = Writer.GetTrackWriter(TrackIndex);
        TrackWriter.WriteAndClose(AllFramePositions);
    }
}
#endif
```

## Demo 示例

以下是一个完整的最小示例，演示如何创建一个可播放几何缓存动画的 Actor：

### MyGeometryCacheActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGeometryCacheActor.generated.h"

class UGeometryCacheComponent;
class UGeometryCache;

UCLASS()
class MYPROJECT_API AMyGeometryCacheActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGeometryCacheActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** 启动播放 */
    UFUNCTION(BlueprintCallable, Category = "GeometryCache")
    void StartAnimation();

    /** 暂停播放 */
    UFUNCTION(BlueprintCallable, Category = "GeometryCache")
    void PauseAnimation();

    /** 切换循环 */
    UFUNCTION(BlueprintCallable, Category = "GeometryCache")
    void ToggleLooping();

    /** 获取当前动画进度 (0.0 ~ 1.0) */
    UFUNCTION(BlueprintCallable, Category = "GeometryCache")
    float GetAnimationProgress() const;

protected:
    /** 几何缓存组件 */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UGeometryCacheComponent> GeometryCacheComponent;

    /** 播放速度倍率 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation", meta = (ClampMin = "0.0", ClampMax = "10.0"))
    float PlaybackSpeed = 1.0f;

    /** 是否循环播放 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    bool bLooping = true;

    /** 是否启用帧间插值 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation", AdvancedDisplay)
    bool bInterpolateFrames = true;

    /** 播放完成时的委托 */
    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnAnimationFinished);

    UPROPERTY(BlueprintAssignable, Category = "Animation")
    FOnAnimationFinished OnAnimationFinished;

private:
    bool bHasFinished = false;
};
```

### MyGeometryCacheActor.cpp

```cpp
#include "MyGeometryCacheActor.h"
#include "GeometryCacheComponent.h"
#include "GeometryCache.h"

AMyGeometryCacheActor::AMyGeometryCacheActor()
{
    PrimaryActorTick.bCanEverTick = true;

    GeometryCacheComponent = CreateDefaultSubobject<UGeometryCacheComponent>(TEXT("GeometryCache"));
    RootComponent = GeometryCacheComponent;
}

void AMyGeometryCacheActor::BeginPlay()
{
    Super::BeginPlay();

    if (GeometryCacheComponent && GeometryCacheComponent->GeometryCache)
    {
        // 应用编辑器中设置的参数
        GeometryCacheComponent->SetLooping(bLooping);
        GeometryCacheComponent->SetPlaybackSpeed(PlaybackSpeed);
        GeometryCacheComponent->SetInterpolateFrames(bInterpolateFrames);
        GeometryCacheComponent->SetMotionVectorScale(1.0f);

        // 自动开始播放
        GeometryCacheComponent->Play();
    }
}

void AMyGeometryCacheActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!GeometryCacheComponent || !GeometryCacheComponent->IsPlaying())
    {
        return;
    }

    // 检测非循环播放是否结束
    if (!bLooping && !bHasFinished)
    {
        float Progress = GetAnimationProgress();
        if (Progress >= 1.0f)
        {
            bHasFinished = true;
            OnAnimationFinished.Broadcast();
        }
    }
}

void AMyGeometryCacheActor::StartAnimation()
{
    if (GeometryCacheComponent)
    {
        bHasFinished = false;
        GeometryCacheComponent->PlayFromStart();
    }
}

void AMyGeometryCacheActor::PauseAnimation()
{
    if (GeometryCacheComponent)
    {
        if (GeometryCacheComponent->IsPlaying())
        {
            GeometryCacheComponent->Pause();
        }
        else
        {
            GeometryCacheComponent->Play();
        }
    }
}

void AMyGeometryCacheActor::ToggleLooping()
{
    bLooping = !bLooping;
    if (GeometryCacheComponent)
    {
        GeometryCacheComponent->SetLooping(bLooping);
    }
}

float AMyGeometryCacheActor::GetAnimationProgress() const
{
    if (!GeometryCacheComponent)
    {
        return 0.0f;
    }

    float Duration = GeometryCacheComponent->GetDuration();
    if (Duration <= KINDA_SMALL_NUMBER)
    {
        return 0.0f;
    }

    float Elapsed = GeometryCacheComponent->GetElapsedTime();
    return FMath::Clamp(Elapsed / Duration, 0.0f, 1.0f);
}
```

## 模块依赖

从各模块 Build.cs 的依赖项分析，以下列出使用者需要注意的**特殊依赖**：

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 网格工具通用模块，用于预处理优化（顶点缓存优化等） |
| `Niagara` | Niagara 粒子系统集成（GeometryCacheTracks 模块） |
| `Sequencer` / `MovieScene` | Sequencer 时间轴集成（GeometryCacheSequencer 模块） |
| `AlembicImporter` | Alembic 格式文件导入支持 |

> 注意：GeometryCacheEd 模块类型为 Runtime 但实际面向编辑器功能（导入、预览等），使用者通常只需依赖 GeometryCache 运行时模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构，通知客户端关联/取消关联事件 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退之前的一次提交 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构相关改动（与上面为同一改动的不同版本） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF（日志宏格式化改进） |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 简化视图与可操作时间轴初始版本发布 |

### 维护评价

- **年龄**：约 4 年（2022 年 1 月从 Experimental 迁出正式发布）
- **更新频率**：持续活跃维护，近期有多次功能性更新（日志宏迁移、视口重构、Sequencer 集成改进）
- **维护状态**：**活跃维护中** — 最近几个月有实质性改动，Epic 持续投入
- **稳定性**：已从实验性标记毕业多年，`IsBetaVersion=false`，`EnabledByDefault=true`，属于引擎核心功能
- **已知注意**：
  - 旧版轨道类型 `GeometryCacheTrack_FlipbookAnimation` 和 `GeometryCacheTrack_TransformAnimation` 已标记 `deprecated`，应使用 `GeometryCacheTrackStreamable`
  - GeometryCacheEd 模块依赖 `UnrealEd`，打包后的游戏不能包含此模块
  - 大型几何缓存文件建议启用流式加载（GeometryCacheStreamer）以控制内存占用

**推荐使用** ✅ — 这是一个成熟、稳定、持续维护的核心运行时插件。如果你的项目需要播放预烘焙的几何体动画（尤其是从 DCC 工具导出的模拟数据），这是官方推荐的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)