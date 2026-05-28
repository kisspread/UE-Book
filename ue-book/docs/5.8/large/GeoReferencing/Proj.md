# GeoReferencing

> GeoReferencing tools for UE worlds

| 属性 | 值 |
|---|---|
| 中文名 | 地理参考 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、坐标系配置资产） |
| 模块 | `GeoReferencing` (Runtime), `GeoReferencingEditor` (Editor), `Proj` (External) |
| 实验性 | 否 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeoReferencing) | |

## 用途

GeoReferencing 插件解决了 UE 世界坐标与真实世界地理坐标之间的映射问题。它允许开发者将 UE 关卡中的位置绑定到地球上任意坐标系统，使得 UE 虚拟世界能够精确对应真实地理位置。

插件核心依赖 **PROJ 库**（v9.1.1），这是一个成熟的开源坐标参考系转换库，支持数千种坐标参考系（CRS）之间的转换，包括各种投影坐标系（如 UTM、Lambert、Mercator 等）和大地坐标系（如 WGS84、各种国家基准面等）。

**为什么存在**：许多行业应用（数字孪生、建筑可视化、自动驾驶仿真、GIS 可视化）需要将真实世界的地理数据（卫星影像、地形高程、建筑物模型等）精确放置到虚拟场景中，这就要求引擎能够理解并转换地理坐标。

## 使用场景

- 你在做**数字孪生**项目，需要将真实城市 BIM/GIS 数据准确导入 UE → 用 GeoReferencing 配合对应的 CRS
- 你在做**自动驾驶仿真**，需要将 OpenDRIVE 地图数据对齐到真实经纬度 → 设置原点和坐标系
- 你在做**城市规划可视化**，需要叠加真实卫星影像到虚拟地形上 → 配置投影坐标系
- 你需要将多个不同坐标系的**地理数据源**统一到同一个 UE 世界中 → 使用 CRS 转换功能
- 你需要计算 UE 场景中两点之间的**真实世界距离** → 使用经纬度逆算功能

## 蓝图用法

### 核心节点

| 芯点 | 说明 | 所在类 |
|---|---|---|
| `Set Geographic CRS` | 设置世界使用的地理坐标参考系（如 EPSG:4326） | `UGeoReferencingSubsystem` |
| `Set Projected CRS` | 设置世界使用的投影坐标参考系（如 EPSG:32632 UTM 32N） | `UGeoReferencingSubsystem` |
| `Set Origin at Geographic Coordinates` | 将 UE 世界原点绑定到指定经纬度坐标 | `UGeoReferencingSubsystem` |
| `Set Origin at Projected Coordinates` | 将 UE 世界原点绑定到指定投影坐标 | `UGeoReferencingSubsystem` |
| `Geographic to Unreal` | 将经纬度坐标转换为 UE 世界坐标 | `UGeoReferencingSubsystem` |
| `Unreal to Geographic` | 将 UE 世界坐标转换为经纬度坐标 | `UGeoReferencingSubsystem` |
| `Projected to Unreal` | 将投影坐标转换为 UE 世界坐标 | `UGeoReferencingSubsystem` |
| `Unreal to Projected` | 将 UE 世界坐标转换为投影坐标 | `UGeoReferencingSubsystem` |
| `Geographic to Projected` | 将经纬度坐标转换为投影坐标 | `UGeoReferencingSubsystem` |
| `Projected to Geographic` | 将投影坐标转换为经纬度坐标 | `UGeoReferencingSubsystem` |

### 使用示例（蓝图描述）

**基本地理参考设置**：
1. 从 `Get GeoReferencing Subsystem` 节点获取子系统引用
2. 调用 `Set Geographic CRS`，输入 `"EPSG:4326"`（WGS84 经纬度）
3. 调用 `Set Projected CRS`，输入 `"EPSG:32632"`（UTM 32N）
4. 调用 `Set Origin at Geographic Coordinates`，设置原点经纬度（如 48.8566, 2.3522，巴黎坐标）
5. 之后使用 `Geographic to Unreal` 将任意经纬度转换为场景中的世界坐标

**坐标转换链**：
```
[地理坐标 (经纬度)] → [Geographic to Unreal] → [UE 世界坐标 (XYZ)]
[UE 世界坐标] → [Unreal to Projected] → [投影坐标 (米制)]
```

## C++ 用法

### 头文件引入

```cpp
#include "GeoReferencingModule.h"
#include "GeoReferencingSubsystem.h"
```

### 基本用法

```cpp
// 获取 GeoReferencing 子系统
UGeoReferencingSubsystem* GeoRefSubsystem = GetWorld()->GetSubsystem<UGeoReferencingSubsystem>();

// 设置地理坐标参考系为 WGS84
GeoRefSubsystem->SetGeographicCRS(TEXT("EPSG:4326"));

// 设置投影坐标参考系为 UTM 32N
GeoRefSubsystem->SetProjectedCRS(TEXT("EPSG:32632"));

// 设置 UE 世界原点对应的地理坐标
GeoRefSubsystem->SetOriginAtGeographicCoordinates(
    FGeographicCoordinates(48.8566, 2.3522, 0.0)  // 巴黎经纬度
);

// 将经纬度转换为 UE 世界坐标
FGeographicCoordinates GeoCoord(48.8600, 2.3400, 100.0);
FVector UnrealPosition;
GeoRefSubsystem->GeographicToUnreal(GeoCoord, UnrealPosition);

// 将 UE 世界坐标转换回经纬度
FGeographicCoordinates OutGeoCoord;
GeoRefSubsystem->UnrealToGeographic(UnrealPosition, OutGeoCoord);
```

（来源：基于 GeoReferencingSubsystem 公开 API 推断）

### 进阶用法

```cpp
// 使用投影坐标系统工作
FVector ProjectedPosition(255000.0, 5416000.0, 50.0);  // UTM 坐标（米）
FVector UnrealPos;
GeoRefSubsystem->ProjectedToUnreal(ProjectedPosition, UnrealPos);

// 反向转换
FVector OutProjected;
GeoRefSubsystem->UnrealToProjected(UnrealPos, OutProjected);

// 地理坐标与投影坐标互转（无需经过 UE 世界坐标）
FGeographicCoordinates GeoCoord(48.8566, 2.3522, 0.0);
FVector ProjectedCoord;
GeoRefSubsystem->GeographicToProjected(GeoCoord, ProjectedCoord);
```

## Demo 示例

```cpp
// GeoRefDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GeoRefDemo.generated.h"

UCLASS()
class AGeoRefDemo : public AActor
{
    GENERATED_BODY()
    
public:
    virtual void BeginPlay() override;
    
    // 在场景中标记地理位置
    UFUNCTION(BlueprintCallable)
    FVector PlaceObjectAtLocation(double Latitude, double Longitude, double Altitude);
};
```

```cpp
// GeoRefDemo.cpp
#include "GeoRefDemo.h"
#include "GeoReferencingSubsystem.h"

void AGeoRefDemo::BeginPlay()
{
    Super::BeginPlay();
    
    UGeoReferencingSubsystem* GeoRef = GetWorld()->GetSubsystem<UGeoReferencingSubsystem>();
    if (!GeoRef) return;
    
    // 配置坐标系
    GeoRef->SetGeographicCRS(TEXT("EPSG:4326"));
    GeoRef->SetOriginAtGeographicCoordinates(
        FGeographicCoordinates(48.8566, 2.3522, 0.0)
    );
}

FVector AGeoRefDemo::PlaceObjectAtLocation(double Latitude, double Longitude, double Altitude)
{
    UGeoReferencingSubsystem* GeoRef = GetWorld()->GetSubsystem<UGeoReferencingSubsystem>();
    if (!GeoRef) return FVector::ZeroVector;
    
    FGeographicCoordinates Coord(Latitude, Longitude, Altitude);
    FVector WorldPosition;
    GeoRef->GeographicToUnreal(Coord, WorldPosition);
    
    return WorldPosition;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SQLiteCore` | PROJ 库的数据库后端（CRS 定义数据库） |
| `Slate` | GeoReferencing 模块依赖（UI 相关） |

无其他特殊依赖（标准 Core/Engine 依赖已在模块中隐含）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新接口 |
| 2026-03-04 | `32fcdd48` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4`. | 清理已废弃的头文件引入 |
| 2025-06-12 | `4a7c2bb3` | Replace some usages of FORCEINLINE with inline in WorldBuilding modules. | 将 FORCEINLINE 替换为 inline |
| 2025-05-27 | `37df175a` | Proj uses arm64 uwp library for Windows Arm64 for the time being. | 为 Windows Arm64 平台使用 arm64 uwp 版本的 Proj 库 |

### 维护评价

GeoReferencing 插件处于**活跃维护**状态。自 2021 年创建以来，持续有更新，最近一次更新在 2026 年 5 月。更新主要集中在编译兼容性修复和平台适配（如 Arm64 支持），说明该插件仍在跟随引擎主线演进。作为 UE5 内置的地理参考工具，对于需要真实世界坐标映射的项目是**推荐使用**的官方方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeoReferencing)
- [PROJ 官方文档](https://proj.org/)
- [EPSG 坐标系查询](https://epsg.io/)