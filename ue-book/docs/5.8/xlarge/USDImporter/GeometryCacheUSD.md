# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

---

## 用途

USDImporter 为 Unreal Engine 提供了对 Pixar Universal Scene Description (USD) 文件格式的完整支持。它不仅仅是简单的导入工具，而是一个端到端的 USD 工作流集成方案，涵盖：

- **USD Stage 导入**：将 `.usd`/`.usda`/`.usdc` 文件作为可编辑的 Stage 加载到引擎中，支持 Prim 层级浏览、属性编辑和实时更新
- **几何缓存 (Geometry Cache)**：将 USD 的网格动画数据以流式方式加载为 GeometryCache 资产，支持逐帧播放
- **USD Schema 映射**：将 USD 的 Prim 类型映射为 UE 对应的 Actor/Component（如 Mesh、Light、Camera）
- **导出功能**：支持将 UE 场景导出为 USD 格式
- **Stage 编辑器**：提供专用的编辑器面板用于浏览和操作 USD Stage 内容

该插件默认禁用且标记为实验性，需要在项目设置中手动启用。

## 使用场景

- 你从 Maya/Houdini/Blender 导出 USD 场景，需要在 UE 中导入并保持层级关系 → 用 USD Stage Importer
- 你的管线使用 USD 作为资产交换格式（大型影视/动画制作） → 用 USDImporter 整个工作流
- 你需要在 UE 中播放由 DCC 工具导出的网格动画（如布料模拟、变形体） → 用 GeometryCacheUSD
- 你需要将 UE 中的场景资产导出回 USD 格式供 DCC 工具使用 → 用 USDExporter
- 你需要在 UE 编辑器中实时浏览和编辑 USD Prim 属性 → 用 USDStageEditor

## 蓝图用法

> ⚠️ 本插件大部分功能通过编辑器面板和 C++ API 暴露，蓝图接口有限。以下为从源码中提取的可用蓝图节点。

### GeometryCacheUSD 核心类

| 节点 | 说明 | 所在类 |
|---|---|---|
| （组件）USD Geometry Cache | 在场景中放置一个由 USD 驱动的几何缓存组件 | `UGeometryCacheUsdComponent` |
| `PostDuplicate` | 处理组件复制逻辑（PIE 等场景） | `UGeometryCacheUsdComponent` |

`UGeometryCacheUsdComponent` 继承自 `UGeometryCacheComponent`，可使用父类的播放控制节点（Play、Pause、SetPlaybackSpeed 等）。

### 使用示例

1. 在 Actor 上添加 `USD Geometry Cache` 组件
2. 通过 C++ 初始化关联的 `UGeometryCacheTrackUsd`，传入 USD Stage 路径和 Prim 路径
3. 使用标准 GeometryCache 蓝图节点控制播放

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheUSD/GeometryCacheTrackUSD.h"
#include "GeometryCacheUSD/GeometryCacheUSDComponent.h"
#include "GeometryCacheUSD/GeometryCacheUSDStream.h"
```

### 基本用法：创建 USD GeometryCache Track

```cpp
// 基于 GeometryCacheUSD 模块源码分析
// 创建一个基于 USD 文件的几何缓存轨道

#include "GeometryCacheTrackUSD.h"

// 假设已有 USD Stage 引用
UE::FUsdStage Stage = /* ... */;

// 创建 Track 对象
UGeometryCacheTrackUsd* UsdTrack = NewObject<UGeometryCacheTrackUsd>();

// 初始化：指定 Stage、Prim 路径、帧范围和读取函数
auto ReadFunc = [](const TWeakObjectPtr<UGeometryCacheTrackUsd> Track,
                    float Time,
                    FGeometryCacheMeshData& OutMeshData) -> bool
{
    // 自定义网格数据读取逻辑
    return true;
};

UsdTrack->Initialize(Stage, TEXT("/Root/MyMesh"), 0, 120, ReadFunc);

// 加载 Stage（从 weak 引用升级为 pinned）
if (UsdTrack->LoadUsdStage())
{
    // Stage 加载成功，可以读取网格数据
    FGeometryCacheMeshData MeshData;
    UsdTrack->GetMeshData(0, MeshData);
}
```

### 进阶用法：自定义流式加载

```cpp
// 自定义流式读取回调，用于异步加载 USD 网格数据
FReadUsdMeshFunction ReadFunc = [](const TWeakObjectPtr<UGeometryCacheTrackUsd> TrackPtr,
                                    float Time,
                                    FGeometryCacheMeshData& OutMeshData) -> bool
{
    if (UGeometryCacheTrackUsd* Track = TrackPtr.Get())
    {
        // 从 USD Stage 读取指定时间点的网格数据
        // MeshConversionOptions 可用于控制转换参数
        return true;
    }
    return false;
};

// 注册流式通道
UsdTrack->RegisterStream();

// 使用 FGeometryCacheUsdStream 进行异步帧数据请求
// 流式系统会自动管理并发读取和帧缓冲
```

### 关键 API 说明

```cpp
// 时间与帧索引转换
int32 SampleIndex = UsdTrack->FindSampleIndexFromTime(2.5f, false);
float Time = UsdTrack->GetTimeFromSampleIndex(30);

// 获取插值帧信息（用于渲染过渡）
int32 FrameIndex;
float Fraction;
UsdTrack->GetFractionalFrameIndexFromTime(2.5f, false, FrameIndex, Fraction);

// Stage 生命周期管理
UsdTrack->LoadUsdStage();    // 加载/重新加载 Stage
UsdTrack->UnloadUsdStage();  // 释放 Stage 引用，节省内存
```

## Demo 示例

### 最小 USD GeometryCache 组件示例

```cpp
// MyUsdGeometryActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "MyUsdGeometryActor.generated.h"

class UGeometryCacheUsdComponent;

UCLASS()
class AMyUsdGeometryActor : public AActor
{
    GENERATED_BODY()

public:
    AMyUsdGeometryActor();

    UPROPERTY(VisibleAnywhere)
    UGeometryCacheUsdComponent* UsdGeometryCacheComponent;
};
```

```cpp
// MyUsdGeometryActor.cpp
#include "MyUsdGeometryActor.h"
#include "GeometryCacheUSD/GeometryCacheUSDComponent.h"

AMyUsdGeometryActor::AMyUsdGeometryActor()
{
    UsdGeometryCacheComponent = CreateDefaultSubobject<UGeometryCacheUsdComponent>(
        TEXT("UsdGeometryCache")
    );
    RootComponent = UsdGeometryCacheComponent;
}
```

## 模块依赖

本插件包含 9 个模块，各模块间有复杂的内部依赖关系。以下列出使用者最可能需要依赖的模块：

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 几何缓存基类（UGeometryCacheTrack、UGeometryCacheComponent） |
| `GeometryCacheUSD` | USD 驱动的几何缓存轨道和组件 |
| `USDSchemas` | USD Prim 类型到 UE 类型的 Schema 映射 |
| `USDStage` | USD Stage 的运行时表示和操作 |
| `USDStageImporter` | USD 文件的导入流程实现 |
| `USDExporter` | UE 场景到 USD 的导出功能 |
| `USDClassesEditor` | 编辑器扩展的类定义 |
| `USDStageEditor` | USD Stage 的编辑器面板 |
| `USDStageEditorViewModels` | USD Stage 编辑器的 MVVM 视图模型 |

使用 GeometryCacheUSD 模块时，你的 Build.cs 需要包含：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "GeometryCache",
    "GeometryCacheUSD",
    "USDSchemas",
    "USDStage"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度到单精度截断警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 支持独立于蓝图的 Control Rig 分配 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | 解决 UE 26.03 更新导致 LOD 变化时 AnimQuery 内部引用失效问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 支持烘焙曝光动画轨道的所有帧 |

### 维护评价

**活跃维护中** ✅

- **创建时间**：2018 年 11 月，已持续开发约 7 年
- **更新频率**：2026 年 4-5 月密集更新，近一个月内有多次功能性提交
- **功能趋势**：近期聚焦于动画系统集成（Control Rig、AnimQuery）和浮点精度修复
- **状态**：尽管标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，但该插件仍在积极维护，功能持续完善
- **注意事项**：
  - 仍为实验性功能，API 可能在未来版本发生变化
  - GeometryCacheUSD 组件标记为 `Experimental`，在蓝图类浏览器中可能默认隐藏
  - 依赖外部 USD SDK（`USE_USD_SDK` 预处理器宏），需要正确配置 SDK 路径
- **推荐**：对于有 USD 管线需求的项目可以使用，但需注意 API 稳定性风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)