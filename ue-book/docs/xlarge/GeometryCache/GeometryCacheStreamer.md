# Geometry Cache Streamer

> Support for distilled Geometry animations（照抄，不翻译）

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

`GeometryCacheStreamer` 模块是 `GeometryCache` 插件的核心流式加载组件。它解决的核心问题是：如何高效地播放和加载可能包含数万帧、数据量巨大的几何缓存（Geometry Cache）动画，同时避免一次性将所有数据加载到内存中导致内存溢出。

该模块通过 `IGeometryCacheStreamer` 接口管理所有注册的几何缓存轨道（`UGeometryCacheTrack`）的流式加载。它使用 `IGeometryCacheStream` 接口抽象数据源（如磁盘上的 Alembic 文件），并通过 `FGeometryCacheStreamBase` 提供了一套基础的流式加载框架，包括预取、内存管理、并发读取和状态跟踪。开发者可以基于此框架实现自定义的流式数据源。

## 使用场景

- **影视与过场动画预览**：在编辑器中预览由 Alembic 或其他格式导入的大型角色或环境动画，无需等待全部加载完成。
- **建筑可视化**：播放复杂的建筑生长动画或机械运动模拟，这些动画通常帧数多、数据量大。
- **游戏中的复杂角色动画**：对于使用几何缓存实现的、非骨骼驱动的复杂角色变形动画（如面部表情、布料模拟），需要按需加载以节省运行时内存。
- **任何需要播放大型、预计算几何动画的场景**：当动画数据无法全部常驻内存时，流式加载是必需的。

## 蓝图用法

该模块主要通过项目设置暴露蓝图可配置的属性，核心流式逻辑在 C++ 层面运作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LookAheadBuffer` (属性) | 设置流式加载的前瞻缓冲时间（秒），决定提前加载多少帧数据。 | `UGeometryCacheStreamerSettings` |
| `MaxMemoryAllowed` (属性) | 设置所有流式加载允许使用的最大内存（MB），用于全局内存控制。 | `UGeometryCacheStreamerSettings` |

### 使用示例（蓝图描述）

在 **项目设置 (Project Settings)** 中，找到 **Plugins -> Geometry Cache** 分类。你可以直接在蓝图编辑器中修改 `Look Ahead Buffer` 和 `Maximum Memory Allowed` 的值。这些设置会全局影响所有 `GeometryCache` 资产的流式加载行为。通常，增大前瞻缓冲可以减少播放卡顿，但会增加内存占用；设置合理的内存上限可以防止应用内存溢出。

## C++ 用法

### 头文件引入

```cpp
#include "IGeometryCacheStreamer.h"
#include "IGeometryCacheStream.h"
#include "GeometryCacheStreamBase.h"
```

### 基本用法

以下示例展示了如何实现一个简单的内存流，并将其注册到流式管理器中。这通常由 `UGeometryCacheTrack` 的子类在初始化时完成。

```cpp
// 假设我们有一个自定义的流式数据源类
class FMyMemoryStream : public FGeometryCacheStreamBase
{
public:
    FMyMemoryStream(FGeometryCacheStreamDetails&& Details, const TArray<FGeometryCacheMeshData>& InFrameData)
        : FGeometryCacheStreamBase(1, MoveTemp(Details)) // 1个并发读取
        , FrameData(InFrameData)
    {}

protected:
    // 实现从数据源获取网格数据的核心方法
    virtual void GetMeshData(int32 FrameIndex, int32 ReadConcurrencyIndex, FGeometryCacheMeshData& OutMeshData) override
    {
        if (FrameData.IsValidIndex(FrameIndex))
        {
            OutMeshData = FrameData[FrameIndex];
        }
    }

private:
    const TArray<FGeometryCacheMeshData>& FrameData; // 持有所有帧数据的引用
};

// 在某个地方（例如 UGeometryCacheTrack 的初始化函数中）使用
void InitializeMyGeometryCacheTrack(UGeometryCacheTrack* Track, const TArray<FGeometryCacheMeshData>& AllFrameData)
{
    // 1. 准备流详情
    FGeometryCacheStreamDetails Details;
    Details.NumFrames = AllFrameData.Num();
    Details.Duration = AllFrameData.Num() / 24.0f; // 假设24fps
    Details.SecondsPerFrame = 1.0f / 24.0f;
    Details.StartFrameIndex = 0;
    Details.EndFrameIndex = AllFrameData.Num() - 1;

    // 2. 创建流实例
    IGeometryCacheStream* Stream = new FMyMemoryStream(MoveTemp(Details), AllFrameData);

    // 3. 注册到流式管理器
    IGeometryCacheStreamer::Get().RegisterTrack(Track, Stream);
}
```
*（来源：基于 `IGeometryCacheStream` 和 `FGeometryCacheStreamBase` 接口推断的典型用法）*

### 进阶用法

流式管理器会自动调用流对象的方法来驱动加载。你可以通过 `IGeometryCacheStreamer` 查询状态或获取数据。

```cpp
// 查询某轨道在特定帧的数据（非阻塞）
FGeometryCacheMeshData MeshData;
if (IGeometryCacheStreamer::Get().TryGetFrameData(MyTrack, DesiredFrameIndex, MeshData))
{
    // 数据已就绪，可以用于渲染
    ApplyMeshDataToComponent(MeshData);
}
else
{
    // 数据尚未加载，可能需要显示占位符或等待
}

// 在轨道销毁时，记得注销
IGeometryCacheStreamer::Get().UnregisterTrack(MyTrack);
```
*（来源：基于 `IGeometryCacheStreamer` 接口推断的典型用法）*

## Demo 示例

一个最小的、可编译的自定义几何缓存流实现。

**MyGeometryCacheStream.h**
```cpp
#pragma once
#include "GeometryCacheStreamBase.h"

class FMyGeometryCacheStream : public FGeometryCacheStreamBase
{
public:
    FMyGeometryCacheStream(FGeometryCacheStreamDetails&& Details, TFunction<FGeometryCacheMeshData(int32)> InDataProvider);
    virtual ~FMyGeometryCacheStream() = default;

protected:
    virtual void GetMeshData(int32 FrameIndex, int32 ReadConcurrencyIndex, FGeometryCacheMeshData& OutMeshData) override;

private:
    TFunction<FGeometryCacheMeshData(int32)> DataProvider;
};
```

**MyGeometryCacheStream.cpp**
```cpp
#include "MyGeometryCacheStream.h"

FMyGeometryCacheStream::FMyGeometryCacheStream(FGeometryCacheStreamDetails&& Details, TFunction<FGeometryCacheMeshData(int32)> InDataProvider)
    : FGeometryCacheStreamBase(2, MoveTemp(Details)) // 使用2个并发读取线程
    , DataProvider(MoveTemp(InDataProvider))
{
}

void FMyGeometryCacheStream::GetMeshData(int32 FrameIndex, int32 ReadConcurrencyIndex, FGeometryCacheMeshData& OutMeshData)
{
    if (DataProvider)
    {
        OutMeshData = DataProvider(FrameIndex);
    }
}
```

**YourModule.Build.cs** (依赖说明)
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "GeometryCache",
    "GeometryCacheStreamer"
});
```

## 模块依赖

从 `GeometryCacheStreamer` 模块的 `Build.cs` 及其头文件推断，它主要依赖于 `GeometryCache` 核心模块。使用者需要确保自己的模块依赖了 `GeometryCache`。

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 提供核心数据类型（如 `FGeometryCacheMeshData`）和 `UGeometryCacheTrack` 等基础类。 |

## 维护状态

### 近期更新

1.  **`775179f9f987`** (2024-05-10): `Call static FTSTicker::RemoveTicker in ~FGeometryCacheStreamer to fix nodiscard warning on Clang 20`
    *   **解读**：修复了在 Clang 20 编译器下，`FGeometryCacheStreamer` 析构函数中调用 `FTSTicker::RemoveTicker` 时产生的 `nodiscard` 警告。这是一个编译器兼容性修复。
2.  **`2739c3d30ebc`** (2024-04-26): `Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n`
    *   **解读**：使用工具批量更新头文件，确保 `UE_API` 等 DLL 导出宏正确地应用于函数和静态变量，而不是类型。这是代码规范化和跨平台兼容性维护的一部分。
3.  **`66e9bb39ff7e`** (2024-04-25): `Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base`
    *   **解读**：移除了在 UE 5.2 中已废弃的头文件包含顺序相关的预处理宏。这是代码清理工作，简化了代码库。

### 维护评价

`GeometryCacheStreamer` 模块创建于 2018 年，是一个相对成熟的模块。从近期提交记录看，它仍在被积极维护，主要进行编译器兼容性修复、代码规范化和清理工作，而非功能性大改。这表明该模块功能稳定，Epic 仍在确保其在新版引擎和编译器下的可用性。

**综合评价**：**维护中**。该模块是 `GeometryCache` 插件的核心且稳定的部分，推荐在需要流式加载大型几何动画的项目中使用。没有发现明显的废弃迹象或已知重大限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache/Tests) (如果存在)