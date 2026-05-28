# GeoReferencing

> GeoReferencing tools for UE worlds

| 属性 | 值 |
|---|---|
| 中文名 | 地理坐标参考系统 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeoReferencing` (Runtime), `GeoReferencingEditor` (Editor), `Proj` (External) |
| 实验性 | 否 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeoReferencing) | |

## 用途

GeoReferencing 插件为 UE 世界提供地理坐标系统（Geographic Coordinate Systems）支持。它解决的核心问题是**将游戏引擎中的任意位置（UE 世界坐标）与现实世界的地理位置（如经纬度、高程）进行精确转换**。

该插件的存在是为了满足以下需求：
1. **地理空间应用**：构建基于真实地理数据的可视化、仿真或混合现实应用。
2. **数据叠加**：将来自 GIS（地理信息系统）的数据（如卫星影像、地形数据、建筑模型）精确对齐到 UE 场景中。
3. **精确位置服务**：开发需要真实世界定位的 AR/VR 应用或仿真训练系统。

它通过内置的 Proj 库（一个广泛使用的坐标转换库）来实现各种地理坐标系之间的转换，支持包括 WGS84 在内的众多标准。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`GeoReferencing`](GeoReferencing.md) | Runtime | 核心运行时模块，提供地理坐标转换、坐标系定义等核心功能和蓝图节点。 |
| [`GeoReferencingEditor`](GeoReferencingEditor.md) | Editor | 编辑器模块，提供编辑器内的工具、设置界面和资产类型，用于配置和测试地理参考系统。 |
| [`Proj`](Proj.md) | External | 第三方坐标转换库（Proj）的封装模块，提供实际的地理坐标计算能力。 |

## 使用场景

- **城市数字孪生**：在 UE 中构建真实城市的 3D 模型，并准确对应到真实的经纬度坐标。
- **自动驾驶仿真**：将 UE 场景中的道路网络与真实世界的地图数据（如 OpenStreetMap）对齐，用于算法测试。
- **建筑/工程 (AEC)**：在设计阶段，将 BIM（建筑信息模型）数据放置在真实的地理环境中进行可视化。
- **军事/航空仿真**：创建基于真实地形和坐标系的训练环境。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Geographic CRS` | 获取当前世界设置中配置的地理坐标参考系统（CRS）字符串。 | `UGeoReferencingSubsystem` |
| `Get Geographic Transform` | 获取用于将 UE 坐标转换为地理坐标（或反之）的变换参数。 | `UGeoReferencingSubsystem` |
| `Engine To Geographic` | 将 UE 引擎坐标转换为地理坐标（经纬度高程）。 | `UGeoReferencingSubsystem` |
| `Geographic To Engine` | 将地理坐标转换为 UE 引擎坐标。 | `UGeoReferencingSubsystem` |
| `Get CRS From String` | 根据给定的字符串（如 "EPSG:4326"）解析并创建一个 CRS 对象。 | `UProjectedCRS` / `UGeographicCRS` |

### 使用示例（蓝图描述）
1.  在世界设置（World Settings）中，配置 `Geo Referencing` 组件，设置项目的地理中心（原点）对应的经纬度以及使用的目标 CRS（如 WGS84）。
2.  在蓝图中，通过 `Get Game Instance Subsystem` 获取 `GeoReferencingSubsystem`。
3.  调用 `Engine To Geographic` 节点，输入一个场景中的世界坐标（Vector），即可得到对应的经纬度高程（GeographicLocation 结构体）。
4.  也可以使用反向节点 `Geographic To Engine`，将一个经纬度高程坐标转换回场景中的位置，用于生成物体。

## C++ 用法

### 头文件引入
```cpp
#include "GeoReferencingSubsystem.h"
#include "GeographicCoordinates.h"
```

### 基本用法
```cpp
// 获取子系统
UGeoReferencingSubsystem* GeoSubsystem = GetWorld()->GetSubsystem<UGeoReferencingSubsystem>();

// 将引擎坐标转换为地理坐标
FVector EngineLocation(1000.0f, 2000.0f, 0.0f);
FGeographicCoordinates GeoCoords;
if (GeoSubsystem->EngineToGeographic(EngineLocation, GeoCoords))
{
    // GeoCoords 现在包含经度、纬度和高程
    UE_LOG(LogTemp, Log, TEXT("Longitude: %f, Latitude: %f, Altitude: %f"), 
           GeoCoords.Longitude, GeoCoords.Latitude, GeoCoords.Altitude);
}

// 将地理坐标转换为引擎坐标
FGeographicCoordinates TargetCoords(121.473701, 31.230416, 0.0); // 上海附近
FVector EnginePos;
if (GeoSubsystem->GeographicToEngine(TargetCoords, EnginePos))
{
    // EnginePos 是场景中的位置
    // 可以用来生成 Actor
}
```
*注：代码基于典型用法推断，具体 API 需参考源码文档。*

## Demo 示例

由于 GeoReferencing 涉及运行时和编辑器模块的完整设置，一个最小的可编译示例需要配置 World Settings。以下是一个在编辑器中测试转换的简化 C++ 示例（需在拥有 World 的上下文中）：

```cpp
// MyGeoTest.cpp
#include "GeoReferencingSubsystem.h"
#include "GeographicCoordinates.h"
#include "Engine/World.h"

void AMyActor::TestGeoConversion()
{
    UWorld* World = GetWorld();
    if (!World) return;

    UGeoReferencingSubsystem* GeoSubsystem = World->GetSubsystem<UGeoReferencingSubsystem>();
    if (!GeoSubsystem) return;

    // 测试原点转换
    FVector WorldOrigin = FVector::ZeroVector;
    FGeographicCoordinates GeoOrigin;
    if (GeoSubsystem->EngineToGeographic(WorldOrigin, GeoOrigin))
    {
        UE_LOG(LogTemp, Warning, TEXT("World Origin corresponds to: Lat %f, Lon %f"), 
               GeoOrigin.Latitude, GeoOrigin.Longitude);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SQLiteCore` | 用于存储和查询 Proj 库所需的地理坐标参考系统（CRS）定义数据。 |
| `Slate` | 用于编辑器用户界面（GeoReferencingEditor 模块）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-03-04 | `32fcdd48` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4`. | 移除了在 UE 5.4 中已废弃的包含顺序守卫代码。 |
| 2025-06-12 | `4a7c2bb3` | Replace some usages of FORCEINLINE with inline in WorldBuilding modules. | 在 WorldBuilding 相关模块中，将部分 FORCEINLINE 替换为 inline。 |
| 2025-05-27 | `37df175a` | Proj uses arm64 uwp library for Windows Arm64 for the time being. | 为 Windows Arm64 平台暂时使用 arm64 uwp 版本的 Proj 库。 |

### 维护评价
- **活跃维护**：该插件由 Epic Games 官方维护，最近一次提交在 2026 年 5 月，更新非常活跃。
- **成熟稳定**：创建于 2021 年，已经历了约 4 年的开发和迭代，功能相对成熟。
- **跨平台支持**：根据 .uplugin 配置，支持主流桌面和移动平台（Win64, Mac, Linux, Android, iOS）。
- **推荐使用**：对于任何需要将 UE 场景与真实世界地理位置对齐的项目，这是官方提供的标准解决方案，**推荐使用**。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeoReferencing)
- [官方文档](https://docs.unrealengine.com) (需搜索“Geo Referencing”相关页面)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeoReferencing/Tests) (如果存在)