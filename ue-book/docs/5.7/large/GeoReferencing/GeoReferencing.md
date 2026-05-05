# GeoReferencing 模块（Runtime）

> 核心运行时模块，提供坐标转换、ENU 计算、椭球面操作等全部地理参考功能。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Runtime |
| LoadingPhase | Default |
| 平台 | Android, iOS, Linux, Mac, Win64 |

## 源码文件

### Public Headers

| 文件 | 说明 |
|---|---|
| [`GeoReferencingSystem.h`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GeoReferencing/Source/GeoReferencing/Public/GeoReferencingSystem.h) | 核心 Actor 类，管理 CRS 配置和所有坐标转换 |
| [`GeographicCoordinates.h`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GeoReferencing/Source/GeoReferencing/Public/GeographicCoordinates.h) | 经纬度坐标结构体 `FGeographicCoordinates` |
| [`Ellipsoid.h`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GeoReferencing/Source/GeoReferencing/Public/Ellipsoid.h) | 椭球体结构体 `FEllipsoid`，用于法线和半径计算 |
| [`RoundPlanetPawn.h`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GeoReferencing/Source/GeoReferencing/Public/RoundPlanetPawn.h) | 球面漫游 Pawn，支持在地球表面飞行 |
| [`GeoReferencingBFL.h`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GeoReferencing/Source/GeoReferencing/Public/GeoReferencingBFL.h) | 蓝图函数库，大坐标格式化工具 |
| [`UFSProjSupport.h`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GeoReferencing/Source/GeoReferencing/Public/UFSProjSupport.h) | UFS 文件系统适配层，使 PROJ 能读取 Pak 中的数据 |
| [`GeoReferencingModule.h`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GeoReferencing/Source/GeoReferencing/Public/GeoReferencingModule.h) | 模块定义和日志分类 |

### Private Sources

| 文件 | 说明 |
|---|---|
| `GeoReferencingSystem.cpp` | PROJ 初始化、所有坐标转换实现、ENU/切线变换计算（~1000 行） |
| `GeographicCoordinates.cpp` | 坐标格式化实现（度分秒转换等） |
| `Ellipsoid.cpp` | 椭球体几何计算 |
| `RoundPlanetPawn.cpp` | 球面飞行 Pawn 的移动和飞行逻辑 |
| `GeoReferencingBFL.cpp` | 大坐标格式化实现 |
| `UFSProjSupport.cpp` | UFS 文件 API 适配 PROJ 的 Open/Read/Seek/Close |
| `GeoReferencingModule.cpp` | 模块启动（注册 PROJ 的 UFS 文件系统） |

## 核心类

### AGeoReferencingSystem

继承自 `AInfo`，是整个插件的核心。每个关卡应放置**恰好一个**此 Actor。

**属性（在编辑器 Details 面板中配置）：**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `PlanetShape` | `EPlanetShape` | FlatPlanet | 地球形状模式：Flat（平面投影）或 Round（球面） |
| `ProjectedCRS` | `FString` | `EPSG:32631` | 投影坐标系定义（EPSG 代码、WKT 或 PROJ 字符串） |
| `GeographicCRS` | `FString` | `EPSG:4326` | 地理坐标系定义 |
| `bOriginAtPlanetCenter` | `bool` | false | UE 原点是否在行星中心（仅 Round 模式） |
| `bOriginLocationInProjectedCRS` | `bool` | true | UE 原点是否用投影坐标表达 |
| `OriginLatitude` / `OriginLongitude` / `OriginAltitude` | `double` | 0.0 | 地理坐标表达的原点 |
| `OriginProjectedCoordinatesEasting/Northing/Up` | `double` | 500000/5000000/0 | 投影坐标表达的原点 |

**坐标系关系图：**

```
                    Projected CRS (UTM等)
                   ↕ ProjectedToGeographic
Geographic CRS (WGS84 经纬度)
                   ↕ GeographicToECEF
          ECEF (EPSG:4978 地心坐标)
                   ↕ ECEFToEngine
          Engine (UE 世界坐标)
```

所有四套坐标之间可以两两转换，共 12 种转换路径。

**内部实现要点：**
- 使用 `TPimplPtr<FGeoReferencingSystemInternals>` 隐藏 PROJ 依赖
- PROJ 上下文在 `Initialize()` 时创建，`BeginDestroy()` 时销毁
- FlatPlanet 模式下 Engine ↔ Projected 是简单的平移变换（1 UE 单位 = 1 cm）
- RoundPlanet 模式下通过 ECEF 矩阵变换实现 Engine ↔ ECEF
- UE 的 Y 轴反转（左手坐标系）在转换中自动处理

### FGeographicCoordinates

BlueprintType 结构体，表示经纬度坐标。

| 成员 | 类型 | 说明 |
|---|---|---|
| `Longitude` | `double` | 经度（度） |
| `Latitude` | `double` | 纬度（度） |
| `Altitude` | `double` | 高度（米） |

提供格式化方法：`ToFullText()`、`ToCompactText()`、`ToSeparateTexts()`，支持度分秒格式。

### FEllipsoid

椭球体结构体，存储半径信息并提供法线计算。

| 方法 | 说明 |
|---|---|
| `GetMaximumRadius()` | 获取最大半径 |
| `GetMinimumRadius()` | 获取最小半径 |
| `GeodeticSurfaceNormal(FVector)` | 从 ECEF 位置计算地表法线 |
| `GeodeticSurfaceNormal(FGeographicCoordinates)` | 从经纬度计算地表法线 |

### EPlanetShape

```cpp
enum class EPlanetShape : uint8 {
    FlatPlanet,   // 平面投影模式，适合中小范围环境
    RoundPlanet   // 球面模式，适合行星规模环境
};
```

### ARoundPlanetPawn

继承自 `ADefaultPawn`，专为球面漫游设计的 Pawn。

**核心特性：**
- 自动根据球面法线调整 "上" 方向，保持画面始终正确
- `FlyToLocation` 系列函数支持平滑飞行到任意经纬度或 ECEF 位置
- 速度系统：`BaseSpeedKmh × SpeedScalar × AltitudeSpeedModifier`
- `OrbitalMotion` 模式下移动沿椭球面切线方向

**配置属性：**

| 属性 | 说明 |
|---|---|
| `AltitudeProfileCurve` | 飞行高度曲线（0-1 归一化） |
| `MaximumAltitudeCurve` | 按距离计算最大飞行高度 |
| `ProgressCurve` | 飞行进度缓动曲线 |
| `FlyDuration` | 飞行时长（秒） |
| `GranularityDegrees` | 飞行轨迹精度（度） |
| `BaseSpeedKmh` | 基础移动速度 |
| `OrbitalMotion` | 是否沿切线方向移动 |

### FUFSProj

静态工具类，将 UE 的 UFS（虚幻文件系统）适配为 PROJ 的文件 API。使 PROJ 能在打包后的游戏（.pak 文件）中正确读取 `proj.db` 等数据文件。

## 依赖关系

```
GeoReferencing (Runtime)
├── Core, Engine (Public)
├── CoreUObject, InputCore (Private)
├── PROJ (Private, External) ← 第三方坐标转换库
├── Projects (Private) ← 插件路径查询
├── SQLiteCore (Private) ← PROJ 数据库访问
└── RHI (Private)
```

插件级别还依赖 `SQLiteCore` 插件。
