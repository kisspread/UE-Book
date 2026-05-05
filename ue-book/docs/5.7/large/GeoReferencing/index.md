# Geo Referencing

> GeoReferencing tools for UE worlds

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、UI控件、3D模型、曲线） |
| 模块 | `GeoReferencing` (Runtime), `GeoReferencingEditor` (Editor), `PROJ` (External) |
| 实验性 | 否 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeoReferencing) | |

## 用途

GeoReferencing 插件解决了 UE 世界坐标与真实地球坐标之间的转换问题。它基于 [PROJ](https://proj.org/) 库，支持任意 CRS（坐标参考系统）之间的转换，是 GIS、数字孪生、城市规划、地球规模仿真等场景的基础能力。

核心功能：
- 在 UE Engine 空间、Projected CRS（如 UTM）、Geographic CRS（经纬度，如 WGS84）、ECEF（地心地固坐标系）四套坐标之间自由转换
- 支持 FlatPlanet（平面投影）和 RoundPlanet（球面地球）两种模式
- 提供 ENU（东-北-天）局部坐标系和椭球面切线变换
- 内置 RoundPlanetPawn 可在球面上平滑飞行
- 提供编辑器工具库，支持视口拾取和射线检测

## 使用场景

- 你有一个城市级 GIS 数据集，需要在 UE 中精确对齐 → 配置 Projected CRS 为对应的 UTM 分带，设置原点坐标
- 你在做地球规模的数字孪生，需要在整个行星表面漫游 → 使用 RoundPlanet 模式 + RoundPlanetPawn
- 你需要把 UE 中的位置输出为经纬度给外部系统 → 使用 EngineToGeographic 转换
- 你有来自 Google Earth 或其他 GIS 工具的坐标数据 → 使用 ECEF 或 Geographic 坐标输入

## 蓝图用法

### 坐标转换节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Engine To Projected` | UE 坐标 → 投影坐标 | `AGeoReferencingSystem` |
| `Projected To Engine` | 投影坐标 → UE 坐标 | `AGeoReferencingSystem` |
| `Engine To ECEF` | UE 坐标 → 地心坐标 | `AGeoReferencingSystem` |
| `ECEF To Engine` | 地心坐标 → UE 坐标 | `AGeoReferencingSystem` |
| `Engine To Geographic` | UE 坐标 → 经纬度 | `AGeoReferencingSystem` |
| `Geographic To Engine` | 经纬度 → UE 坐标 | `AGeoReferencingSystem` |
| `Projected To Geographic` | 投影坐标 → 经纬度 | `AGeoReferencingSystem` |
| `Geographic To Projected` | 经纬度 → 投影坐标 | `AGeoReferencingSystem` |
| `Projected To ECEF` | 投影坐标 → 地心坐标 | `AGeoReferencingSystem` |
| `ECEF To Projected` | 地心坐标 → 投影坐标 | `AGeoReferencingSystem` |
| `Geographic To ECEF` | 经纬度 → 地心坐标 | `AGeoReferencingSystem` |
| `ECEF To Geographic` | 地心坐标 → 经纬度 | `AGeoReferencingSystem` |

### ENU 与变换节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get ENU Vectors At Engine Location` | 获取引擎位置处的东-北-天向量 | `AGeoReferencingSystem` |
| `Get ENU Vectors At Projected Location` | 获取投影坐标处的 ENU 向量 | `AGeoReferencingSystem` |
| `Get ENU Vectors At Geographic Location` | 获取经纬度处的 ENU 向量 | `AGeoReferencingSystem` |
| `Get ENU Vectors At ECEF Location` | 获取 ECEF 处的 ENU 向量 | `AGeoReferencingSystem` |
| `Get ECEF ENU Vectors At ECEF Location` | 获取纯 ECEF 帧下的 ENU 向量 | `AGeoReferencingSystem` |
| `Get Tangent Transform At Engine Location` | 获取引擎位置处的椭球切线变换 | `AGeoReferencingSystem` |
| `Get Tangent Transform At Geographic Location` | 获取经纬度处的切线变换 | `AGeoReferencingSystem` |
| `Get Planet Center Transform` | 获取行星中心变换 | `AGeoReferencingSystem` |

### 工具节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Geo Referencing System` | 获取世界中的 GeoReferencingSystem 单例 | `AGeoReferencingSystem` |
| `Is CRS String Valid` | 验证 CRS 字符串是否有效 | `AGeoReferencingSystem` |
| `Get Geographic Ellipsoid Max/Min Radius` | 获取地理椭球最大/最小半径 | `AGeoReferencingSystem` |
| `Get Projected Ellipsoid Max/Min Radius` | 获取投影椭球最大/最小半径 | `AGeoReferencingSystem` |
| `Apply Runtime Changes` | 运行时应用 CRS 配置变更 | `AGeoReferencingSystem` |

### 坐标格式化节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ToFullText` (GeographicCoordinates) | 格式化为 `Lat= Lon= Alt=` 文本 | `UGeographicCoordinatesFunctionLibrary` |
| `ToCompactText` (GeographicCoordinates) | 格式化为 `(Lat, Lon, Alt)` 文本 | `UGeographicCoordinatesFunctionLibrary` |
| `ToSeparateTexts` (GeographicCoordinates) | 分离输出纬度/经度/高度文本 | `UGeographicCoordinatesFunctionLibrary` |
| `MakeGeographicCoordinates` | 从 FVector 构造经纬度坐标 | `UGeographicCoordinatesFunctionLibrary` |
| `ToFullText` (FVector) | 格式化大坐标为 `X= Y= Z=` 文本 | `UGeoReferencingBFL` |
| `ToCompactText` (FVector) | 格式化大坐标为 `(X, Y, Z)` 文本 | `UGeoReferencingBFL` |
| `ToSeparateTexts` (FVector) | 分离输出大坐标的 X/Y/Z 文本 | `UGeoReferencingBFL` |

### RoundPlanetPawn 飞行节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Fly To Location ECEF` | 飞行到 ECEF 坐标位置 | `ARoundPlanetPawn` |
| `Fly To Location Geographic` | 飞行到经纬度位置 | `ARoundPlanetPawn` |
| `Fly To Location Latitude Longitude Altitude` | 飞行到经纬高位置 | `ARoundPlanetPawn` |
| `Interrupt Fly To Location` | 中断当前飞行 | `ARoundPlanetPawn` |
| `Reset Speed Scalar` | 重置飞行速度 | `ARoundPlanetPawn` |
| `Increase/Decrease Speed Scalar` | 增减飞行速度 | `ARoundPlanetPawn` |

### 编辑器工具节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Viewport Cursor Location` | 获取编辑器视口鼠标位置 | `UGeoReferencingEditorBPLibrary` |
| `Get Viewport Cursor Information` | 获取视口光标的世界位置和方向 | `UGeoReferencingEditorBPLibrary` |
| `Line Trace Viewport` | 从视口鼠标位置做射线检测 | `UGeoReferencingEditorBPLibrary` |
| `Line Trace` | 从指定位置方向做射线检测 | `UGeoReferencingEditorBPLibrary` |

### 使用示例（蓝图描述）

**场景：获取玩家在地球上的经纬度**

1. 在关卡中放置 `AGeoReferencingSystem` Actor，配置 Projected CRS（如 `EPSG:32631` UTM 31N）和 Geographic CRS（`EPSG:4326` WGS84）
2. 设置原点的投影坐标或经纬度
3. 蓝图中：获取玩家 Pawn 位置 → 调用 `Get Geo Referencing System` → 调用 `Engine To Geographic` → 得到 `FGeographicCoordinates` → 用 `ToFullText` 显示

**场景：将 GPS 数据放置到 UE 世界**

1. 获取 GPS 经纬度数据
2. 蓝图中：构造 `FGeographicCoordinates` → 调用 `Geographic To Engine` → 得到 UE 世界坐标 → 设置 Actor 位置

**场景：在 RoundPlanet 上飞行到目标位置**

1. 使用 `BP_RoundPlanetPawn` 作为 Player Pawn
2. 蓝图中：调用 `Fly To Location Geographic` 传入目标经纬度和朝向

## C++ 用法

### 头文件引入

```cpp
#include "GeoReferencingSystem.h"
#include "GeographicCoordinates.h"
#include "Ellipsoid.h"
```

### 基本用法

```cpp
// 获取 GeoReferencingSystem 实例
AGeoReferencingSystem* GeoRefSystem = AGeoReferencingSystem::GetGeoReferencingSystem(this);
if (!GeoRefSystem) return;

// UE 引擎坐标转经纬度
FVector EnginePos = GetActorLocation();
FGeographicCoordinates GeoCoords;
GeoRefSystem->EngineToGeographic(EnginePos, GeoCoords);

UE_LOG(LogTemp, Log, TEXT("Lat: %f, Lon: %f, Alt: %f"),
    GeoCoords.Latitude, GeoCoords.Longitude, GeoCoords.Altitude);

// 经纬度转 UE 引擎坐标
FGeographicCoordinates TargetCoords(2.3522, 48.8566, 0.0); // 巴黎
FVector UEPosition;
GeoRefSystem->GeographicToEngine(TargetCoords, UEPosition);
```

### 进阶用法

```cpp
// 获取 ENU 局部坐标系（用于放置朝向正确的物体）
FVector East, North, Up;
GeoRefSystem->GetENUVectorsAtEngineLocation(EnginePos, East, North, Up);

// 获取椭球面切线变换（用于在地球表面放置物体）
FTransform TangentTransform = GeoRefSystem->GetTangentTransformAtEngineLocation(EnginePos);
MyActor->SetActorTransform(TangentTransform);

// ECEF 转换（用于与卫星数据对接）
FVector ECEFPos;
GeoRefSystem->EngineToECEF(EnginePos, ECEFPos);

// 验证 CRS 字符串
FString Error;
bool bValid = GeoRefSystem->IsCRSStringValid(TEXT("EPSG:32631"), Error);
```

### Demo 示例

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "GeoReferencing",
    "Core",
    "Engine"
});
```

**最小示例 - 打印当前位置的经纬度：**

```cpp
// MyGeoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyGeoActor.generated.h"

UCLASS()
class AMyGeoActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
};

// MyGeoActor.cpp
#include "MyGeoActor.h"
#include "GeoReferencingSystem.h"

void AMyGeoActor::BeginPlay()
{
    Super::BeginPlay();

    AGeoReferencingSystem* GeoRef = AGeoReferencingSystem::GetGeoReferencingSystem(this);
    if (!GeoRef) return;

    FGeographicCoordinates GeoCoords;
    GeoRef->EngineToGeographic(GetActorLocation(), GeoCoords);

    UE_LOG(LogTemp, Log, TEXT("Position: Lat=%.6f, Lon=%.6f, Alt=%.2f"),
        GeoCoords.Latitude, GeoCoords.Longitude, GeoCoords.Altitude);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `Engine` | 引擎核心功能 |
| `CoreUObject` | UObject 系统 |
| `PROJ` | 第三方 PROJ 坐标转换库（外部模块） |
| `Projects` | 插件管理接口 |
| `SQLiteCore` | PROJ 数据库访问所需 |
| `RHI` | 渲染硬件接口 |
| `InputCore` | 输入系统 |
| `Slate` / `SlateCore` | UI 框架（编辑器模块） |
| `UnrealEd` | 编辑器功能（编辑器模块） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-12 | `4a7c2bb` | Replace some usages of FORCEINLINE with inline in WorldBuilding modules | 代码规范调整，将 FORCEINLINE 替换为 inline |
| 2025-05-27 | `37df175` | Proj uses arm64 uwp library for Windows Arm64 for the time being | 增加 Windows ARM64 平台支持 |
| 2024-12-12 | `3aa35e2` | Fix missing file warning from GeoReferencing in non-editor builds | 修复非编辑器构建中的文件缺失警告 |

### 维护评价

- **创建时间**：2021-04-29，约 5 年历史
- **维护状态**：活跃维护中。2025 年仍有功能性更新（ARM64 支持），2024 年有 bug 修复
- **内容资产**：包含 24 个 .uasset，有完整的示例蓝图（RoundPlanetPawn、坐标检查器、探针等）
- **平台支持**：Windows、Mac、Linux、iOS、Android 全平台
- **推荐程度**：✅ 强烈推荐。这是 UE 中做 GIS 集成的唯一官方方案，PROJ 库是行业标准，API 设计清晰完善

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeoReferencing)
- [PROJ 官方文档](https://proj.org/)
- [EPSG 坐标系查询](https://epsg.io/)
