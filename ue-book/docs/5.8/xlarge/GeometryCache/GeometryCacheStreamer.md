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
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

`GeometryCache` 插件提供了一套用于流式传输和播放“蒸馏”几何体动画的框架。它并非直接创建动画，而是作为处理如 Alembic (.abc) 等格式导入的顶点级变形动画（即几何缓存）的核心运行时支撑。其主要解决的问题是：复杂的、逐帧变形的网格动画（如毛发布料模拟、流体表面、复杂的角色面部形变）数据量巨大，无法一次性全部加载到内存中。该插件通过实现异步流式加载、内存管理和序列化播放，使得这些大型动画能够在游戏或实时应用中流畅播放。

## 使用场景

- **电影或过场动画**：当你需要将离线渲染的复杂毛发、布料或破碎动画引入到 UE5 中进行实时播放时。
- **高细节角色动画**：角色拥有基于模拟或扫描的复杂面部表情、身体肌肉形变动画，数据以 Alembic Cache 格式存储。
- **大量复杂物体**：场景中存在大量需要播放相同或不同几何缓存动画的物体（如植被、人群），流式系统能有效管理内存。
- **需要精确同步的动画**：通过 `Sequencer` 模块，可以将几何缓存动画与时间轴上的其他事件（音频、特效、摄像机）精确同步。

## 蓝图用法

### 核心设置节点

几何缓存流式系统的行为可以通过项目设置进行全局配置。这些设置在蓝图中可读，但通常需要在编辑器中预先设置。

| 设置项 | 说明 | 所在类 |
|---|---|---|
| `LookAheadBuffer` | 预加载动画的秒数（流式缓冲区大小）。值越大，播放越平滑，但内存占用和预加载时间越长。 | `UGeometryCacheStreamerSettings` |
| `MaxMemoryAllowed` | 所有流式传输允许占用的最大内存（MB）。当达到此限制时，系统会根据需要卸载旧的帧数据。 | `UGeometryCacheStreamerSettings` |

### 使用示例（蓝图描述）

在“项目设置” -> “引擎” -> “Geometry Cache”类别下，找到“Geometry Cache Streamer”设置组，可以调整“Look-Ahead Buffer (in seconds)”和“Maximum Memory Allowed (in MB)”的值。这些设置将影响游戏中所有几何缓存资源的播放行为。在运行时，这些值也可以通过 C++ 代码动态调整。

## C++ 用法

### 头文件引入

```cpp
#include "IGeometryCacheStreamer.h"
#include "GeometryCacheStreamBase.h"
```

### 基本用法

获取流式系统单例并与几何缓存轨道交互。

```cpp
// 来源: IGeometryCacheStreamer.h
#include "IGeometryCacheStreamer.h"

// 获取流式管理器单例
IGeometryCacheStreamer& Streamer = IGeometryCacheStreamer::Get();

// 检查一个几何缓存轨道是否已注册
UGeometryCacheTrack* MyTrack = /* ... */;
if (Streamer.IsTrackRegistered(MyTrack))
{
    // 尝试获取指定帧的网格数据（异步，可能失败）
    FGeometryCacheMeshData MeshData;
    if (Streamer.TryGetFrameData(MyTrack, FrameIndex, MeshData))
    {
        // 成功获取到数据，用于渲染或其他处理
    }
}
```

### 进阶用法：实现自定义流

继承 `FGeometryCacheStreamBase` 来为自定义数据源（如网络、特殊文件格式）创建流式读取器。

```cpp
// 来源: GeometryCacheStreamBase.h
#include "GeometryCacheStreamBase.h"

class FMyCustomGeometryCacheStream : public FGeometryCacheStreamBase
{
public:
    FMyCustomGeometryCacheStream(int32 ReadConcurrency, FGeometryCacheStreamDetails&& Details)
        : FGeometryCacheStreamBase(ReadConcurrency, MoveTemp(Details))
    {
    }

protected:
    // 必须实现此函数，从自定义数据源加载指定帧的网格数据。
    // 此函数将在工作线程中被调用，必须保证线程安全。
    virtual void GetMeshData(int32 FrameIndex, int32 ReadConcurrencyIndex, FGeometryCacheMeshData& OutMeshData) override
    {
        // 例如：从你的内存数据库、网络或自定义文件中加载第 FrameIndex 帧的数据，
        // 并填充到 OutMeshData 结构体中。
        OutMeshData.Positions = /* ... */;
        OutMeshData.Normals = /* ... */;
        // ... 其他顶点数据
    }
};

// 使用自定义流
void RegisterMyStream(UGeometryCacheTrack* Track, const FString& SourcePath)
{
    // 1. 获取动画详情（通常从资源或解析源数据获得）
    FGeometryCacheStreamDetails Details;
    Details.NumFrames = 120;
    Details.Duration = 4.0f;
    Details.SecondsPerFrame = 1.0f / 30.0f;

    // 2. 创建你的流实例，设置适当的并发读取数（例如4）
    FMyCustomGeometryCacheStream* MyStream = new FMyCustomGeometryCacheStream(4, MoveTemp(Details));

    // 3. 注册到流式管理器（管理器获得流的所有权）
    IGeometryCacheStreamer::Get().RegisterTrack(Track, MyStream);
}
```

## Demo 示例

以下是一个最小化的自定义几何缓存流实现，它从预先加载到内存中的 `TArray<FGeometryCacheMeshData>` 里读取数据。

```cpp
// MyInMemoryGeometryCacheStream.h
#pragma once
#include "GeometryCacheStreamBase.h"

class FMyInMemoryGeometryCacheStream : public FGeometryCacheStreamBase
{
public:
    FMyInMemoryGeometryCacheStream(int32 ReadConcurrency, FGeometryCacheStreamDetails&& Details, TArray<FGeometryCacheMeshData>&& InFrameData);
    virtual ~FMyInMemoryGeometryCacheStream();

protected:
    virtual void GetMeshData(int32 FrameIndex, int32 ReadConcurrencyIndex, FGeometryCacheMeshData& OutMeshData) override;

private:
    TArray<FGeometryCacheMeshData> PreloadedFrames;
};
```

```cpp
// MyInMemoryGeometryCacheStream.cpp
#include "MyInMemoryGeometryCacheStream.h"

FMyInMemoryGeometryCacheStream::FMyInMemoryGeometryCacheStream(int32 ReadConcurrency, FGeometryCacheStreamDetails&& Details, TArray<FGeometryCacheMeshData>&& InFrameData)
    : FGeometryCacheStreamBase(ReadConcurrency, MoveTemp(Details))
    , PreloadedFrames(MoveTemp(InFrameData))
{
}

FMyInMemoryGeometryCacheStream::~FMyInMemoryGeometryCacheStream()
{
}

void FMyInMemoryGeometryCacheStream::GetMeshData(int32 FrameIndex, int32 ReadConcurrencyIndex, FGeometryCacheMeshData& OutMeshData)
{
    // 直接从预加载的数组中拷贝数据
    if (PreloadedFrames.IsValidIndex(FrameIndex))
    {
        OutMeshData = PreloadedFrames[FrameIndex];
    }
    else
    {
        // 处理无效帧索引的情况
        UE_LOG(LogTemp, Warning, TEXT("FMyInMemoryGeometryCacheStream: Invalid frame index %d"), FrameIndex);
    }
}
```

## 模块依赖

从 `Build.cs` 文件分析，使用此插件的主要模块（`GeometryCache`）需要以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 用于网格数据处理的通用工具函数和结构体。 |

**注意**：`GeometryCacheStreamer` 模块本身依赖较少，主要提供流式接口和基础实现。使用者的项目模块若只需使用 `IGeometryCacheStreamer` 接口，则无需直接依赖 `MeshUtilitiesCommon`。`UnrealEd` 属于编辑器依赖，在运行时模块中通常不会被客户端项目引用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构，优化客户端关联/解除关联的通知逻辑 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了一次更改 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构，优化客户端关联/解除关联的通知逻辑 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移为 UE_LOGF 格式 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | [序列器] 简单视图与可操作时间轴初始版本发布 |

### 维护评价

该插件创建于 2022 年初，年龄较新。从 git 记录看，最后一次实质性提交（涉及其模块）集中在 2024 年左右，近期提交多为全局性的引擎代码重构（如日志宏迁移、视口重构）波及此插件。这表明该插件处于**维护状态**，功能稳定，但近期无主动的功能性开发。作为 UE5 的官方插件，它是一个可靠的选择，特别适合处理由 Alembic 导入器生成的几何缓存数据。如果需要高度定制流式源，其提供的 `IGeometryCacheStream` 接口扩展性良好。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/GeometryCache)