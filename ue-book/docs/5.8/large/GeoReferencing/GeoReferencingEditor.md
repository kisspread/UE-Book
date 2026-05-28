# GeoReferencing

> GeoReferencing tools for UE worlds

| 属性 | 值 |
|---|---|
| 中文名 | 地理配准 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（第三方 Proj 库） |
| 模块 | `GeoReferencing` (Runtime), `GeoReferencingEditor` (Editor), `Proj` (External) |
| 实验性 | 否 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeoReferencing) | |

## 用途

GeoReferencing 插件为 UE5 世界提供**真实世界地理坐标系统**的绑定与坐标转换能力。

在 GIS、数字孪生、城市规划、自动驾驶仿真等场景中，UE 场景需要与真实地球位置精确对应。该插件通过集成 [Proj](https://proj.org/) 坐标转换库，实现了以下核心能力：

- **坐标参考系（CRS）定义**：在场景中放置 `AGeoReferencingSystem` Actor，配置源 CRS（如 WGS84 经纬度、UTM 投影坐标等）和目标 CRS
- **坐标转换**：在 UE 引擎坐标、地心地固坐标（ECEF）、地理坐标（经纬度+高度）、投影坐标之间互相转换
- **原点偏移管理**：解决 UE 使用单精度浮点导致大世界精度丢失的问题，通过设定地理原点将世界坐标映射到精确的地球位置

## 使用场景

- **数字孪生 / 智慧城市**：将 UE 场景绑定到真实地理坐标，导入 GIS 数据（如 CityGML、3D Tiles）时保持空间一致
- **自动驾驶仿真**：将高精地图的经纬度坐标精确映射到 UE 场景中，确保虚拟车辆轨迹与现实对齐
- **建筑可视化**：根据真实地块的经纬度自动设置太阳角度、日照方向
- **航空 / 航海仿真**：使用 ECEF 坐标系进行大范围场景的精确定位
- **GIS 数据导入**：将 Shapefile、GeoTIFF 等带有投影坐标的数据正确放置到 UE 场景中

## 蓝图用法

### 核心节点

以下是 GeoReferencingRuntime 模块暴露的核心蓝图节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EngineToECEF` | 将 UE 引擎坐标转换为 ECEF 地心坐标 | `AGeoReferencingSystem` |
| `ECEFToEngine` | 将 ECEF 地心坐标转换为 UE 引擎坐标 | `AGeoReferencingSystem` |
| `EngineToGeographic` | 将 UE 引擎坐标转换为地理坐标（经纬度+高度） | `AGeoReferencingSystem` |
| `GeographicToEngine` | 将地理坐标（经纬度+高度）转换为 UE 引擎坐标 | `AGeoReferencingSystem` |
| `EngineToProjected` | 将 UE 引擎坐标转换为投影坐标 | `AGeoReferencingSystem` |
| `ProjectedToEngine` | 将投影坐标转换为 UE 引擎坐标 | `AGeoReferencingSystem` |
| `GeographicToProjected` | 将地理坐标转换为投影坐标 | `AGeoReferencingSystem` |
| `ProjectedToGeographic` | 将投影坐标转换为地理坐标 | `AGeoReferencingSystem` |
| `GetGeoReferencingSystem` | 获取当前世界中的 GeoReferencingSystem 单例 | `UGeoReferencingBPLibrary` |

### Editor 工具节点

以下是 GeoReferencingEditor 模块提供的编辑器专用蓝图节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewportCursorLocation` | 获取鼠标在关卡编辑器视口中的屏幕坐标 | `UGeoReferencingEditorBPLibrary` |
| `GetViewportCursorInformation` | 获取鼠标下方视口的相机位置和方向 | `UGeoReferencingEditorBPLibrary` |
| `LineTraceViewport` | 从鼠标位置向场景发射射线并返回命中结果 | `UGeoReferencingEditorBPLibrary` |
| `LineTrace` | 从指定世界位置和方向发射射线 | `UGeoReferencingEditorBPLibrary` |

### 使用示例（蓝图描述）

**示例 1：将地理坐标放置到场景中**

1. 在场景中放置一个 `GeoReferencingSystem` Actor
2. 在其 Details 面板中设置 Coordinate Reference System（如 `EPSG:4326` 代表 WGS84）
3. 设置 Geographic CRS Origin 为场景对应的经纬度原点
4. 在蓝图中调用 `GetGeoReferencingSystem` 获取实例
5. 使用 `GeographicToEngine` 节点，传入经纬度高度，获取对应的 UE 引擎坐标
6. 将获取的坐标用于设置 Actor 的 `SetActorLocation`

**示例 2：从编辑器视口拾取地理坐标**

1. 调用 `GetViewportCursorInformation` 获取鼠标指向的世界位置和方向
2. 调用 `LineTrace` 进行射线检测，获取命中点的引擎坐标
3. 调用 `EngineToGeographic` 将命中点转换为经纬度
4. 输出结果用于 UI 显示或日志记录

## C++ 用法

### 头文件引入

```cpp
#include "GeoReferencingModule.h"

// 如果需要直接访问 GeoReferencingSystem
#include "GeoReferencingSystem.h"

// 如果需要编辑器视口工具
#include "GeoReferencingEditorBPLibrary.h"
```

### 基本用法

从编辑器模块源码提取的视口射线检测用法（来源：`Public/GeoReferencingEditorBPLibrary.h`）：

```cpp
#include "GeoReferencingEditorBPLibrary.h"

// 获取编辑器视口中的鼠标光标位置
bool bFocused = false;
FVector2D ScreenLocation;
UGeoReferencingEditorBPLibrary::GetViewportCursorLocation(bFocused, ScreenLocation);

if (bFocused)
{
    UE_LOG(LogTemp, Log, TEXT("Mouse screen position: %s"), *ScreenLocation.ToString());
}

// 获取视口相机信息
FVector WorldLocation, WorldDirection;
UGeoReferencingEditorBPLibrary::GetViewportCursorInformation(bFocused, ScreenLocation, WorldLocation, WorldDirection);

// 从鼠标位置执行射线检测
bool bSuccess = false;
FHitResult HitResult;
TArray<AActor*> ActorsToIgnore;
UGeoReferencingEditorBPLibrary::LineTraceViewport(
    ScreenLocation,
    ActorsToIgnore,
    true,   // bTraceComplex
    false,  // bShowTrace
    bSuccess,
    HitResult
);

if (bSuccess)
{
    FVector HitLocation = HitResult.Location;
    UE_LOG(LogTemp, Log, TEXT("Hit world location: %s"), *HitLocation.ToString());
}
```

### 进阶用法

使用 GeoReferencingSystem 进行坐标转换（结合射线检测获取地理坐标）：

```cpp
#include "GeoReferencingSystem.h"
#include "GeoReferencingEditorBPLibrary.h"

// 假设场景中已放置 GeoReferencingSystem 并配置好 CRS
AGeoReferencingSystem* GeoRefSystem = AGeoReferencingSystem::GetGeoReferencingSystem(GetWorld());
if (GeoRefSystem)
{
    // 从编辑器视口鼠标位置射线检测到世界中的一个点
    bool bFocused = false;
    FVector2D ScreenPos;
    UGeoReferencingEditorBPLibrary::GetViewportCursorLocation(bFocused, ScreenPos);

    if (bFocused)
    {
        FHitResult HitResult;
        TArray<AActor*> Ignore;
        bool bHit = false;
        UGeoReferencingEditorBPLibrary::LineTraceViewport(ScreenPos, Ignore, true, false, bHit, HitResult);

        if (bHit)
        {
            // 将引擎坐标转换为地理坐标（经纬度+高度）
            FGeographicCoordinates GeographicCoordinates;
            GeoRefSystem->EngineToGeographic(HitResult.Location, GeographicCoordinates);

            UE_LOG(LogTemp, Log, TEXT("Hit point: Lat=%.6f, Lon=%.6f, Alt=%.2f"),
                GeographicCoordinates.Latitude,
                GeographicCoordinates.Longitude,
                GeographicCoordinates.Altitude);

            // 也可以转换为投影坐标
            FVector ProjectedCoordinates;
            GeoRefSystem->EngineToProjected(HitResult.Location, ProjectedCoordinates);
        }
    }
}
```

### 反向转换：将地理坐标放置到场景

```cpp
// 将已知经纬度转为 UE 坐标，用于放置物体
FGeographicCoordinates GeoCoords;
GeoCoords.Latitude = 48.8566;   // 巴黎纬度
GeoCoords.Longitude = 2.3522;   // 巴黎经度
GeoCoords.Altitude = 35.0;      // 埃菲尔铁塔高度（米）

FVector EngineLocation;
GeoRefSystem->GeographicToEngine(GeoCoords, EngineLocation);

// 在计算出的引擎坐标放置一个 Actor
GetWorld()->SpawnActor<AActor>(SomeClass, EngineLocation, FRotator::ZeroRotator);
```

## Demo 示例

以下示例展示一个自定义 Actor，放置后自动将自身地理位置信息打印到日志：

```cpp
// GeoRefDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GeoRefDemoActor.generated.h"

UCLASS()
class AGeoRefDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AGeoRefDemoActor();

    virtual void BeginPlay() override;

    /** 打印当前 Actor 所在位置的地理坐标 */
    UFUNCTION(BlueprintCallable, Category = "GeoRefDemo")
    void PrintGeographicCoordinates() const;
};
```

```cpp
// GeoRefDemoActor.cpp
#include "GeoRefDemoActor.h"
#include "GeoReferencingSystem.h"

AGeoRefDemoActor::AGeoRefDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AGeoRefDemoActor::BeginPlay()
{
    Super::BeginPlay();
    PrintGeographicCoordinates();
}

void AGeoRefDemoActor::PrintGeographicCoordinates() const
{
    AGeoReferencingSystem* GeoRefSystem = AGeoReferencingSystem::GetGeoReferencingSystem(GetWorld());
    if (!GeoRefSystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("No GeoReferencingSystem found in the world."));
        return;
    }

    FVector ActorLocation = GetActorLocation();

    // 转换为地理坐标
    FGeographicCoordinates GeoCoords;
    GeoRefSystem->EngineToGeographic(ActorLocation, GeoCoords);

    UE_LOG(LogTemp, Log,
        TEXT("Actor '%s' geographic position: Lat=%.6f°, Lon=%.6f°, Alt=%.2fm"),
        *GetName(),
        GeoCoords.Latitude,
        GeoCoords.Longitude,
        GeoCoords.Altitude);

    // 转换为 ECEF 坐标
    FVector ECEF;
    GeoRefSystem->EngineToECEF(ActorLocation, ECEF);

    UE_LOG(LogTemp, Log,
        TEXT("  ECEF: X=%.2f, Y=%.2f, Z=%.2f"),
        ECEF.X, ECEF.Y, ECEF.Z);
}
```

## 模块依赖

GeoReferencing 插件的 Build.cs 依赖如下：

| 模块 | 用途 |
|---|---|
| `Proj` | 第三方坐标转换库（PROJ），提供各种 CRS 之间的坐标转换 |
| `SQLiteCore` | Proj 库内部使用 SQLite 进行坐标参考系数据库管理 |
| `Slate` | Runtime 模块的 UI 依赖 |

无其他特殊依赖（仅标准 Core/Engine/CoreUObject 等）。

**使用者需注意**：如果你的模块需要使用 GeoReferencing 功能，在你的 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "GeoReferencing"  // 运行时坐标转换
});

// 如果仅在编辑器中使用视口工具
if (Target.bBuildEditor)
{
    PrivateDependencyModuleNames.Add("GeoReferencingEditor");
}
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF |
| 2026-03-04 | `32fcdd48` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4`. | 移除 UE 5.4 版本废弃的头文件包含守卫 |
| 2025-06-12 | `4a7c2bb3` | Replace some usages of FORCEINLINE with inline in WorldBuilding modules. | 将部分 FORCEINLINE 替换为 inline |
| 2025-05-27 | `37df175a` | Proj uses arm64 uwp library for Windows Arm64 for the time being. | Proj 库临时使用 arm64 UWP 版本支持 Windows Arm64 |

### 维护评价

- **创建时间**：2021 年 4 月，随 UE5 初始分支引入
- **更新频率**：近期 commit 均为**编译兼容性修复和代码风格调整**，无功能性更新。最后一次实质性功能提交距今已超过 1 年
- **维护状态**：**稳定但不活跃**。插件功能已经成熟，处于维护模式，仅随引擎升级做适配性修复
- **已知限制**：
  - 依赖 Proj 第三方库，会增加包体大小
  - 单精度浮点在超大范围场景中仍有精度限制
  - CRS 定义需要用户了解 EPSG 编码或 Proj 字符串语法
- **推荐使用**：✅ **推荐**。对于需要真实世界地理坐标对齐的项目（数字孪生、GIS 可视化、自动驾驶仿真），这是 Epic 官方提供的标准方案，功能完整且稳定。对于普通游戏项目则不需要使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeoReferencing)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现该插件专用测试文件）