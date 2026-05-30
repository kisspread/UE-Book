# Geometry Cache

> Support for distilled Geometry animations（从实验性模块移出的几何缓存系统）

| 属性 | 值 |
|---|---|
| 中文名 | 几何缓存 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-08-01 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

GeometryCache 是 Unreal Engine 的**顶点动画缓存系统**，用于播放预先烘焙的网格顶点动画数据。它解决的核心问题是：如何高效地播放**每帧顶点位置都发生变化**的动画（如破碎、布料模拟、流体表面、角色形变等），而无需在运行时重新模拟。

与骨骼动画不同，GeometryCache 存储的是每帧的完整或差异网格数据（顶点位置、法线、切线、UV、颜色、运动向量），通过压缩编解码器（Huffman + 量化编码）减小内存占用，并支持流式加载大尺寸缓存。

**为什么存在**：
- 骨骼动画只能处理刚性骨骼绑定的形变，无法表达任意拓扑变化（如破碎后碎片分离、布料撕裂）
- 运行时物理模拟代价高昂且难以精确控制，而离线烘焙的缓存可以精确复现 DCC 工具中的模拟结果
- 支持从 Alembic (.abc) 文件导入，这是影视行业标准的缓存交换格式

## 子模块文档

- [GeometryCache 核心模块](GeometryCacheCore.md) — 资产、组件、编解码、渲染代理
- [GeometryCacheStreamer 流式加载模块](GeometryCacheStreamer.md) — 分块流式加载大尺寸缓存
- [GeometryCacheTracks 轨道模块](GeometryCacheTracks.md) — Sequencer 轨道集成
- [GeometryCacheSequencer 序列器模块](GeometryCacheSequencer.md) — 编辑器中的 Sequencer 面板
- [NiagaraGeometryCacheRendererProperties Niagara 集成](NiagaraIntegration.md) — 在 Niagara 粒子中渲染几何缓存

## 使用场景

- 你在做一个破碎系统，DCC 中模拟了 300 帧碎片飞散动画 → 导入为 GeometryCache 并用 `UGeometryCacheComponent` 播放
- 你需要在 Niagara 粒子中用预烘焙的动画网格替代简单 Mesh → 使用 `UNiagaraGeometryCacheRendererProperties`
- 你需要在 Sequencer 中精确控制几何缓存的播放时机和范围 → 使用 GeometryCacheTracks 提供的 Sequencer 轨道
- 你的几何缓存文件非常大（数百 MB），无法一次性加载到内存 → 使用 GeometryCacheStreamer 分块流式加载
- 你在程序化生成顶点动画数据（如运行时布料烘焙）→ 使用 `FGeometryCacheConstantTopologyWriter` 写入资产

## 蓝图用法

蓝图功能集中在 `UGeometryCacheComponent` 上，可通过 `AGeometryCacheActor` 放置到场景中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 从当前位置开始播放 | `UGeometryCacheComponent` |
| `PlayFromStart` | 从头开始播放 | `UGeometryCacheComponent` |
| `PlayReversed` | 反向播放 | `UGeometryCacheComponent` |
| `PlayReversedFromEnd` | 从末尾开始反向播放 | `UGeometryCacheComponent` |
| `Pause` | 暂停播放 | `UGeometryCacheComponent` |
| `Stop` | 停止播放 | `UGeometryCacheComponent` |
| `IsPlaying` | 是否正在播放 | `UGeometryCacheComponent` |
| `SetLooping` | 设置是否循环 | `UGeometryCacheComponent` |
| `SetPlaybackSpeed` | 设置播放速度（0.0~4.0） | `UGeometryCacheComponent` |
| `SetStartTimeOffset` | 设置起始时间偏移 | `UGeometryCacheComponent` |
| `GetAnimationTime` | 获取当前动画时间 | `UGeometryCacheComponent` |
| `GetDuration` | 获取动画总时长 | `UGeometryCacheComponent` |
| `GetNumberOfFrames` | 获取总帧数 | `UGeometryCacheComponent` |
| `GetNumberOfTracks` | 获取轨道数 | `UGeometryCacheComponent` |
| `SetGeometryCache` | 更换使用的 GeometryCache 资产 | `UGeometryCacheComponent` |
| `SetInterpolateFrames` | 启用/禁用帧间插值 | `UGeometryCacheComponent` |
| `SetExtrapolateFrames` | 启用/禁用帧外推 | `UGeometryCacheComponent` |
| `SetMotionVectorScale` | 设置运动向量缩放 | `UGeometryCacheComponent` |
| `SetOverrideWireframeColor` | 覆盖线框颜色 | `UGeometryCacheComponent` |
| `SetManualTick` | 启用手动 Tick 模式 | `UGeometryCacheComponent` |
| `TickAtThisTime` | 在手动 Tick 模式下指定时间更新 | `UGeometryCacheComponent` |

### 使用示例（蓝图描述）

**基本播放**：
1. 将 `AGeometryCacheActor` 拖入场景
2. 在 Details 面板中设置 `GeometryCache` 属性为你的 `.abc` 导入资产
3. 蓝图中获取该 Actor 的 `GeometryCacheComponent` 引用
4. 调用 `Play` 节点开始播放
5. 通过 `IsPlaying` 检查播放状态，`GetAnimationTime` 获取当前时间

**手动控制播放**：
1. 调用 `SetManualTick(true)` 启用手动模式
2. 在每帧 Tick 中调用 `TickAtThisTime(Time, true, false, true)` 驱动播放
3. 可自由控制时间进度，如绑定到 Slider 控件

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCache.h"
#include "GeometryCacheComponent.h"
#include "GeometryCacheTrack.h"
#include "GeometryCacheMeshData.h"
```

### 基本用法

创建 GeometryCache 组件并控制播放：

```cpp
// 在 Actor 中创建并设置 GeometryCache 组件
UGeometryCacheComponent* CacheComp = NewObject<UGeometryCacheComponent>(this);
CacheComp->RegisterComponent();
CacheComp->AttachToComponent(RootAttachment, FAttachmentTransformRules::KeepRelativeTransform);

// 设置缓存资产
UGeometryCache* MyCache = LoadObject<UGeometryCache>(nullptr, TEXT("/Game/Path/To/MyGeometryCache"));
CacheComp->SetGeometryCache(MyCache);

// 播放控制
CacheComp->Play();
CacheComp->SetLooping(true);
CacheComp->SetPlaybackSpeed(1.5f);

// 查询状态
float AnimTime = CacheComp->GetAnimationTime();
float Duration = CacheComp->GetDuration();
int32 NumFrames = CacheComp->GetNumberOfFrames();
```

### 程序化写入几何缓存

使用 `FGeometryCacheConstantTopologyWriter` 从代码生成 GeometryCache 资产：

```cpp
#if WITH_EDITOR
#include "GeometryCacheConstantTopologyWriter.h"

// 创建缓存资产
UGeometryCache* NewCache = NewObject<UGeometryCache>();
FGeometryCacheConstantTopologyWriter Writer(*NewCache);

// 添加材质
TArray<TObjectPtr<UMaterialInterface>> Mats;
Mats.Add(MyMaterial);
Writer.AddMaterials(Mats);

// 创建轨道并写入数据
auto& TrackWriter = Writer.AddTrackWriter();

// 设置网格拓扑（每帧不变的部分）
TrackWriter.Indices = IndexArray;      // TArray<uint32>
TrackWriter.UVs = UVArray;            // TArray<FVector2f>
TrackWriter.Colors = ColorArray;      // TArray<FColor>

// 写入每帧的顶点位置
TArray<TArray<FVector3f>> AllFrames;
for (int32 Frame = 0; Frame < NumFrames; ++Frame)
{
    AllFrames.Add(GetPositionsForFrame(Frame));
}
TrackWriter.WriteAndClose(AllFrames);
#endif
```

### 从 SkeletalMesh 创建缓存

```cpp
#if WITH_EDITOR
#include "GeometryCacheConstantTopologyWriter.h"

USkeletalMesh* SkelMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/MySkelMesh"));
UGeometryCache* NewCache = NewObject<UGeometryCache>();
FGeometryCacheConstantTopologyWriter Writer(*NewCache);

// 从 SkeletalMesh 创建轨道
int32 TrackIndex = UE::GeometryCacheHelpers::AddTrackWriterFromSkinnedAsset(Writer, *SkelMesh);

if (TrackIndex != INDEX_NONE)
{
    // 收集骨骼动画各帧的网格位置
    TArray<FGeometryCacheConstantTopologyWriter::FFrameData> Frames;
    for (float Time = 0.0f; Time < Duration; Time += 1.0f / 30.0f)
    {
        FGeometryCacheConstantTopologyWriter::FFrameData Frame;
        // ... 计算该时间点的顶点位置
        Frames.Add(MoveTemp(Frame));
    }
    Writer.GetTrackWriter(TrackIndex).WriteAndClose(Frames);
}
#endif
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 网格工具函数（UV 优化、索引重排等） |
| `UnrealEd` | 编辑器功能（仅 GeometryCache 模块声明了此依赖，用于导入） |
| `Niagara` | Niagara 粒子系统集成（GeometryCacheTracks 中使用） |
| `Sequencer` | Sequencer 编辑器集成（GeometryCacheTracks 中使用） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport | 视口关联/解耦通知机制重构 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退之前的提交 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport | 视口关联通知重构（与 cfb610df 相关） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 日志宏迁移到新 API |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 简单视图模式初版 |

### 维护评价

GeometryCache 是 Epic 官方维护的成熟插件，**仍在持续维护中**。近期更新主要是基础设施层面的迁移（日志宏更新、视口接口重构），而非功能改动。该插件自 2016 年从 Experimental 移出后一直作为核心 Runtime 插件存在，默认启用。

**注意事项**：
- 部分旧版 Track 类（`GeometryCacheTrack_FlipbookAnimation`、`GeometryCacheTrack_TransformAnimation` 等）已标记为 `deprecated`
- 插件包含完整的压缩编解码器（Huffman + 量化），支持无损和有损压缩
- 流式加载系统支持大文件按需加载，但需要正确配置分块大小

**推荐使用**：✅ 推荐。这是 UE5 中处理顶点动画缓存的标准方案，功能完整且稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Runtime/GeometryCache/Source/GeometryCache/Private/CodecV1Test.h)