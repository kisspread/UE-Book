# Geometry Cache

> Support for distilled Geometry animations

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-04-12 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

GeometryCache 插件用于播放**预烘焙的逐帧网格动画**。与骨骼动画不同，GeometryCache 存储的是每一帧完整的顶点位置数据（拓扑结构通常保持不变），适用于无法用骨骼系统表达的复杂形变效果。

典型数据来源是 Alembic (.abc) 文件——由 DCC 工具（Houdini、Maya、Blender 等）中的流体模拟、布料模拟、刚体破碎等效果烘焙导出。插件将这些数据压缩存储为 `.uasset`，运行时按时间索引解码并渲染。

**核心解决的问题**：将 DCC 工具中产生的复杂几何体动画（顶点级形变）高效地导入、压缩、流式加载并在 UE 中实时播放。

## 使用场景

- 你在 Houdini 中模拟了一段布料飘动效果 → 导出为 Alembic → 作为 GeometryCache 导入 UE
- 你需要播放一个预烘焙的流体/烟雾网格动画 → 用 GeometryCacheComponent 播放
- 你有一个角色面部的 blendshape 动画（非骨骼驱动）→ 用 GeometryCache 存储逐帧网格
- 你需要在 Niagara 粒子系统中使用预烘焙的几何体动画 → 使用 NiagaraGeometryCacheRenderer
- 你需要在 Sequencer 中精确控制几何体动画的时间轴 → 使用 GeometryCacheSequencer 模块
- 你有大量帧数据需要流式加载而非全部驻留内存 → 使用 GeometryCacheStreamer 模块

## 模块架构

本插件包含 5 个模块，按职责划分：

| 模块 | 类型 | 职责 |
|---|---|---|
| `GeometryCache` | Runtime | 核心运行时：资产、组件、渲染代理、编解码器、流式管理 |
| `GeometryCacheEd` | Runtime | 编辑器支持：导入器、资产编辑器、缩略图 |
| `GeometryCacheSequencer` | Runtime | Sequencer 集成：时间轴轨道、关键帧编辑 |
| `GeometryCacheStreamer` | Runtime | 流式加载管理器：按需加载/卸载数据块 |
| `GeometryCacheTracks` | Runtime | 额外轨道类型和动画曲线支持 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 开始播放 GeometryCache | `UGeometryCacheComponent` |
| `PlayFromStart` | 从头开始播放 | `UGeometryCacheComponent` |
| `PlayReversed` | 反向播放 | `UGeometryCacheComponent` |
| `PlayFromStartReversed` | 从末尾反向播放 | `UGeometryCacheComponent` |
| `Pause` | 暂停播放 | `UGeometryCacheComponent` |
| `Stop` | 停止播放并重置 | `UGeometryCacheComponent` |
| `IsPlaying` | 是否正在播放 | `UGeometryCacheComponent` |
| `IsPaused` | 是否已暂停 | `UGeometryCacheComponent` |
| `IsReversed` | 是否反向播放 | `UGeometryCacheComponent` |
| `GetPlaybackSpeed` | 获取播放速度倍率 | `UGeometryCacheComponent` |
| `SetPlaybackSpeed` | 设置播放速度倍率 | `UGeometryCacheComponent` |
| `GetStartTimeOffset` | 获取起始时间偏移 | `UGeometryCacheComponent` |
| `SetStartTimeOffset` | 设置起始时间偏移 | `UGeometryCacheComponent` |
| `GetDuration` | 获取动画总时长 | `UGeometryCacheComponent` |
| `GetAnimationTime` | 获取当前播放时间 | `UGeometryCacheComponent` |
| `SetGeometryCacheAsset` | 设置要播放的 GeometryCache 资产 | `UGeometryCacheComponent` |
| `GetGeometryCacheAsset` | 获取当前 GeometryCache 资产 | `UGeometryCacheComponent` |
| `GetNumberOfFrames` | 获取总帧数 | `UGeometryCacheComponent` |
| `GetNumberOfMaterials` | 获取材质数量 | `UGeometryCacheComponent` |
| `SetMotionVectorScale` | 设置运动矢量缩放 | `UGeometryCacheComponent` |
| `GetMotionVectorScale` | 获取运动矢量缩放 | `UGeometryCacheComponent` |
| `GetGeometryCacheComponent` | 获取组件引用 | `AGeometryCacheActor` |

### 使用示例（蓝图描述）

**基本播放控制**：
1. 在场景中放置 `AGeometryCacheActor`（或手动添加 `UGeometryCacheComponent`）
2. 在组件的 Details 面板中设置 `GeometryCache` 属性为你的 `.uasset`
3. 蓝图中调用 `Play` 开始播放，`Pause` 暂停，`Stop` 停止

**循环播放**：
1. 在组件 Details 面板中勾选 `bLooping`
2. 调用 `Play`，动画将自动循环

**速度控制**：
1. 调用 `SetPlaybackSpeed`，传入 `2.0` 表示 2 倍速，`0.5` 表示半速
2. 负值可实现反向播放效果

**Sequencer 集成**：
1. 在 Sequencer 中添加 GeometryCache 轨道
2. 通过关键帧精确控制播放时间、速度等参数

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCache.h"
#include "GeometryCacheComponent.h"
#include "GeometryCacheActor.h"
#include "GeometryCacheMeshData.h"
#include "GeometryCacheConstantTopologyWriter.h"
```

### 基本用法：程序化创建 GeometryCache 资产

使用 `FGeometryCacheConstantTopologyWriter` 从代码创建 GeometryCache：

```cpp
// 来源: GeometryCacheConstantTopologyWriter.h
#include "GeometryCache.h"
#include "GeometryCacheConstantTopologyWriter.h"

void CreateGeometryCacheProgrammatically()
{
    // 创建或获取一个 GeometryCache 资产
    UGeometryCache* Cache = NewObject<UGeometryCache>();
    
    // 配置写入器
    UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter::FConfig Config;
    Config.FPS = 30.0f;
    Config.PositionPrecision = 0.001f;
    Config.TextureCoordinatesNumberOfBits = 10;
    
    // 创建写入器（会清除已有轨道）
    UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter Writer(*Cache, Config);
    
    // 添加材质
    // Writer.AddMaterials(...);
    
    // 创建轨道写入器
    auto& TrackWriter = Writer.AddGetTrackWriter();
    
    // 设置静态数据（索引、UV、颜色等）
    TrackWriter.Indices = { 0, 1, 2, 2, 3, 0 }; // 三角形索引
    TrackWriter.UVs = { FVector2f(0,0), FVector2f(1,0), FVector2f(1,1), FVector2f(0,1) };
    
    // 准备逐帧位置数据
    TArray<TArray<FVector3f>> AllFramePositions;
    // 帧 0: 4 个顶点
    AllFramePositions.Add({ 
        FVector3f(0,0,0), FVector3f(1,0,0), FVector3f(1,1,0), FVector3f(0,1,0) 
    });
    // 帧 1: 顶点位置变化（拓扑不变）
    AllFramePositions.Add({ 
        FVector3f(0,0,0.5f), FVector3f(1,0,0.5f), FVector3f(1,1,0.5f), FVector3f(0,1,0.5f) 
    });
    
    // 写入并关闭轨道
    TrackWriter.WriteAndClose(AllFramePositions);
}
```

### 基本用法：从 MeshDescription 转换

```cpp
// 来源: GeometryCacheHelpers.h
#include "GeometryCacheHelpers.h"

void ConvertMeshDescriptionToCacheData()
{
    FGeometryCacheMeshData MeshData;
    FMeshDescription MeshDesc;
    
    UE::GeometryCache::Utils::FMeshDataConversionArguments Args;
    Args.MaterialOffset = 0;
    Args.FramesPerSecond = 24.0f;
    Args.bUseVelocitiesAsMotionVectors = true;
    Args.bStoreImportedVertexNumbers = false;
    
    UE::GeometryCache::Utils::GetGeometryCacheMeshDataFromMeshDescription(
        MeshData, MeshDesc, Args
    );
}
```

### 进阶用法：带法线和切线的逐帧写入

```cpp
// 来源: GeometryCacheConstantTopologyWriter.h
void WriteFrameDataWithNormalsAndTangents()
{
    UGeometryCache* Cache = NewObject<UGeometryCache>();
    UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter Writer(*Cache);
    
    auto& TrackWriter = Writer.AddGetTrackWriter();
    TrackWriter.Indices = { 0, 1, 2 };
    
    // 准备包含法线和切线的帧数据
    TArray<UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter::FFrameData> FrameDataArray;
    
    for (int32 Frame = 0; Frame < 30; ++Frame)
    {
        UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter::FFrameData FrameData;
        FrameData.Positions = { FVector3f(0,0,Frame*0.1f), FVector3f(1,0,0), FVector3f(0,1,0) };
        FrameData.Normals = { FVector3f(0,0,1), FVector3f(0,0,1), FVector3f(0,0,1) };
        FrameData.TangentsX = { FVector3f(1,0,0), FVector3f(1,0,0), FVector3f(1,0,0) };
        FrameDataArray.Add(MoveTemp(FrameData));
    }
    
    // 使用带法线/切线的写入接口
    TrackWriter.WriteAndClose(FrameDataArray);
}
```

### 进阶用法：可见性控制

```cpp
// 来源: GeometryCacheConstantTopologyWriter.h
void SetTrackVisibility()
{
    UGeometryCache* Cache = NewObject<UGeometryCache>();
    UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter Writer(*Cache);
    
    auto& TrackWriter = Writer.AddGetTrackWriter();
    
    // 设置可见性采样：在特定帧隐藏/显示
    TArray<UE::GeometryCacheHelpers::FGeometryCacheConstantTopologyWriter::FVisibilitySample> Visibility;
    Visibility.Add({ 0, true });   // 帧 0 可见
    Visibility.Add({ 10, false }); // 帧 10 开始隐藏
    Visibility.Add({ 20, true });  // 帧 20 重新可见
    
    // TrackWriter 可见性数据在 WriteAndClose 前设置
}
```

### 进阶用法：运行时控制组件播放

```cpp
// 来源: GeometryCacheComponent.h
#include "GeometryCacheComponent.h"

void ControlPlayback(UGeometryCacheComponent* Comp)
{
    // 播放控制
    Comp->Play();
    Comp->PlayFromStart();
    Comp->PlayReversed();
    Comp->PlayFromStartReversed();
    Comp->Pause();
    Comp->Stop();
    
    // 状态查询
    bool bPlaying = Comp->IsPlaying();
    bool bPaused = Comp->IsPaused();
    bool bReversed = Comp->IsReversed();
    
    // 速度控制
    Comp->SetPlaybackSpeed(2.0f);
    float Speed = Comp->GetPlaybackSpeed();
    
    // 时间控制
    float Duration = Comp->GetDuration();
    float CurrentTime = Comp->GetAnimationTime();
    Comp->SetStartTimeOffset(1.0f);
    
    // 运动矢量
    Comp->SetMotionVectorScale(FVector(1.0f, 1.0f, 1.0f));
    
    // 帧信息
    int32 NumFrames = Comp->GetNumberOfFrames();
    int32 NumMaterials = Comp->GetNumberOfMaterials();
}
```

## Demo 示例

### 完整的 GeometryCache 组件使用示例

**MyGeometryCacheActor.h**
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

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UGeometryCacheComponent> CacheComponent;

    UFUNCTION(BlueprintCallable)
    void TogglePlayback();

    UFUNCTION(BlueprintCallable)
    void SetSpeed(float NewSpeed);

protected:
    virtual void BeginPlay() override;

private:
    bool bIsPlaying = true;
};
```

**MyGeometryCacheActor.cpp**
```cpp
#include "MyGeometryCacheActor.h"
#include "GeometryCacheComponent.h"

AMyGeometryCacheActor::AMyGeometryCacheActor()
{
    CacheComponent = CreateDefaultSubobject<UGeometryCacheComponent>(TEXT("GeometryCache"));
    RootComponent = CacheComponent;
}

void AMyGeometryCacheActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 确保有资产后开始播放
    if (CacheComponent && CacheComponent->GetGeometryCacheAsset())
    {
        CacheComponent->PlayFromStart();
        bIsPlaying = true;
    }
}

void AMyGeometryCacheActor::TogglePlayback()
{
    if (!CacheComponent) return;
    
    if (bIsPlaying)
    {
        CacheComponent->Pause();
        bIsPlaying = false;
    }
    else
    {
        CacheComponent->Play();
        bIsPlaying = true;
    }
}

void AMyGeometryCacheActor::SetSpeed(float NewSpeed)
{
    if (CacheComponent)
    {
        CacheComponent->SetPlaybackSpeed(NewSpeed);
    }
}
```

**MyModule.Build.cs**
```csharp
using UnrealBuildTool;

public class MyModule : ModuleRules
{
    public MyModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "GeometryCache"  // 核心运行时模块
        });
    }
}
```

## 模块依赖

从各模块 Build.cs 提取的非标准依赖：

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 网格工具通用功能（GeometryCache 核心模块依赖） |
| `Niagara` | Niagara 粒子系统集成（GeometryCacheRenderer） |
| `MeshDescription` | MeshDescription 到 GeometryCacheMeshData 的转换 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 近期 | `4b00fef8173e` | [HWRT] Fix FGeometryCacheSceneProxy modifying RayTracingGeometry.Initializer before calling ReleaseRHI() | 修复硬件光线追踪兼容性问题，确保 RHI 资源生命周期正确 |
| 近期 | `b92ef8d6074c` | Fixed GeometryCache not binding Position/Tangent/MotionBlur attributes when creating DummyVF | 修复虚拟顶点工厂创建时属性绑定遗漏，影响渲染正确性 |
| 近期 | `1d7d2cdb2f20` | Add missing include from some no-PCH configurations | 编译兼容性修复，处理 PCH 禁用场景下的头文件缺失 |

### 维护评价

**综合评价：稳定维护中**

- **创建时间**：2018 年，约 7 年历史，属于成熟插件
- **更新频率**：近期有持续的 bug 修复和兼容性更新，包括硬件光线追踪支持等现代渲染特性适配
- **维护状态**：活跃维护中。作为 Epic 官方维护的核心插件，持续跟进引擎新特性（HWRT、Niagara 集成等）
- **已知限制**：
  - 部分旧版轨道类（`GeometryCacheTrack_TransformAnimation`、`GeometryCacheTrack_TransformGroupAnimation`、`GeometryCacheTrack_FlipbookAnimation`）已标记为 `deprecated`
  - 大型 GeometryCache 资产的内存占用较高，建议使用流式加载（GeometryCacheStreamer 模块）
- **推荐使用**：✅ 推荐。这是 UE 官方支持的几何体动画方案，功能完整，文档齐全，适合生产环境使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)