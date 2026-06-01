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

GeometryCache插件提供了一套完整的工作流，用于导入、存储、播放和流式处理以“蒸馏”形式（例如Alembic (.abc)文件）存储的复杂几何体网格顶点动画数据。它解决的是标准静态网格（Static Mesh）无法高效表示和播放包含大量逐顶点位置变化动画的问题。这个插件的核心是为这类数据创建了一种专门的资产类型（`UGeometryCache`）和播放组件（`UGeometryCacheComponent`），并将其与引擎的Sequencer和流式加载系统深度集成。

## 使用场景

-   你需要在虚幻引擎中导入并播放来自DCC软件（如Houdini、Blender、Maya）通过Alembic格式导出的顶点动画（如破碎、流体模拟、布料模拟）。
-   你需要处理大规模、长时段的顶点动画，并希望通过流式加载（Streaming）来优化内存和性能。
-   你需要在Sequencer中精确控制几何缓存动画的播放、速度、时间映射等。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Geometry Cache` | 设置要播放的几何缓存资产 | `UGeometryCacheComponent` |
| `Play` / `Play From Start` / `Pause` / `Stop` | 控制几何缓存动画的播放状态 | `UGeometryCacheComponent` |
| `Set Playback Speed` | 设置播放速度倍数 | `UGeometryCacheComponent` |
| `Set Playback Time` | 跳转到指定播放时间 | `UGeometryCacheComponent` |
| `Get Playback Speed` | 获取当前播放速度 | `UGeometryCacheComponent` |
| `Get Duration` | 获取几何缓存动画的总时长 | `UGeometryCache` |

### 使用示例（蓝图描述）

1.  在关卡中放置一个 `Geometry Cache Component` 组件。
2.  使用 `Set Geometry Cache` 节点，将其指向一个导入的 `.abc` 文件所生成的 `GeometryCache` 资产。
3.  通过 `Play` 节点开始播放。可以通过 `Set Playback Speed` 节点调整速度，或通过 `Set Playback Time` 节点进行帧精确跳转。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheComponent.h"
#include "GeometryCache.h"
```

### 基本用法

创建和控制几何缓存组件。
（*来源：GeometryCache模块测试用例*）

```cpp
// 假设你已经有了一个加载的 UGeometryCache* MyCacheAsset
UGeometryCacheComponent* CacheComp = NewObject<UGeometryCacheComponent>(OwnerActor);
CacheComp->SetGeometryCache(MyCacheAsset);
CacheComp->RegisterComponent();
CacheComp->Play();
CacheComp->SetPlaybackSpeed(1.5f);
```

### 进阶用法

结合资产流代理（`UGeometryCacheStream`）处理流式资产。
（*来源：GeometryCacheStreamer模块*）

```cpp
// 获取几何缓存资产的流式加载代理
UGeometryCache* Cache = ...; // 你的缓存资产
UGeometryCacheStream* Stream = Cache->GetCacheStream();
if (Stream)
{
    // 流式系统会自动管理数据的加载和卸载
    // 你也可以手动查询状态
    bool bIsReady = Stream->IsFinishedLoading();
}
```

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 提取。

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 用于网格数据的公共工具 |
| `GeometryCacheStreamer` | 核心模块依赖流式加载器来处理流式几何缓存资产 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视图端口重构，改进客户端关联/断开时的通知逻辑。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了之前的某个更改（CL53913857）。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视图端口重构，改进客户端关联/断开时的通知逻辑。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 UE_LOG 迁移为新式 UE_LOGF。 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer模块：发布了带可操作时间线的简单视图初始版本。 |

### 维护评价

**活跃维护**。插件在2022年从实验性模块转为正式模块。从近期Git历史看，它在2026年4-5月仍有持续的更新，包括底层视图系统的重构、日志系统的现代化迁移，以及与Sequencer的新功能集成。这表明该插件仍在被Epic Games积极维护和开发，是处理顶点动画的推荐方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache/Tests)