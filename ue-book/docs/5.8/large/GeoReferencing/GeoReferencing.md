# GeoReferencing

> GeoReferencing tools for UE worlds

| 属性 | 值 |
|---|---|
| 中文名 | 地理参考 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GeoReferencing` (Runtime), `GeoReferencingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeoReferencing) | |

## 用途

GeoReferencing 插件提供了一套完整的工具，用于在虚幻引擎（UE）世界和真实世界的地理坐标系统之间建立对应关系。它解决的核心问题是：如何将UE中创建的虚拟世界精确地映射到地球表面的特定位置，并支持各种标准地理坐标系（如经纬度、投影坐标系、地心坐标系）之间的相互转换。

插件内置了基于 PROJ 库的强大坐标转换引擎，支持平面投影（如 UTM）和地球曲面（球体）两种模式。这使得开发者能够轻松处理从城市级建模到全球范围模拟的各种地理空间应用，例如智慧城市、地理信息系统（GIS）、飞行模拟器或任何需要真实地理定位的虚拟现实（XR）项目。

**为什么存在？**
标准UE坐标系是线性的、无界的笛卡尔坐标系，无法直接表示地球的曲率、经纬度或处理投影变形。当开发者需要融合来自卫星影像、激光雷达（LiDAR）、CAD软件或 GIS 数据库的地理空间数据时，就必须进行精确的坐标系统转换。GeoReferencing 插件通过封装复杂的数学计算和 PROJ 库调用，将这一专业功能以易用的API形式提供给蓝图和C++开发者。

## 使用场景

- **你在构建一个基于真实地理位置的数字孪生或智慧城市项目** → 使用 `GeoReferencingSystem` 将UE世界原点设置到项目的实际地理坐标（如经纬度或UTM坐标），然后直接使用地理坐标数据放置建筑、设施或传感器。
- **你需要为一个全球范围的飞行模拟器创建可飞行地形** → 设置 `PlanetShape` 为 `RoundPlanet`，利用 `RoundPlanetPawn` 实现平滑的全球漫游，自动处理地形跟随和方向调整。
- **你有一组来自外部工具（如AutoCAD、QGIS）的地理坐标数据（经纬度或投影坐标），需要在UE中精确放置** → 使用 `GeographicToEngine` 或 `ProjectedToEngine` 函数将外部坐标转换为UE世界坐标，然后用于生成Actor的位置。
- **你需要在球形地球上放置物体并保持正确的局部朝向** → 使用 `GetTangentTransformAtGeographicLocation` 或 `GetENUVectorsAtGeographicLocation` 获取特定地理位置的切线变换或东-北-天（ENU）坐标系，用于对齐物体。
- **你需要在运行时动态切换坐标参考系统或更新原点** → 调用 `ApplySettings()` 函数在代码中更新 `GeoReferencingSystem` 的属性（如CRS定义或原点位置）。

## 蓝图用法

核心功能主要通过 `AGeoReferencingSystem` Actor 和 `ARoundPlanetPawn` Pawn 暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Geo Referencing System` | 获取当前世界中的 `AGeoReferencingSystem` 实例（通常为单例）。 | `AGeoReferencingSystem` |
| `Engine To Geographic` | 将UE引擎空间坐标（FVector）转换为地理坐标（纬度、经度、海拔）。 | `AGeoReferencingSystem` |
| `Geographic To Engine` | 将地理坐标（纬度、经度、海拔）转换为UE引擎空间坐标（FVector）。 | `AGeoReferencingSystem` |
| `Engine To Projected` | 将UE引擎空间坐标转换为投影坐标系坐标（如UTM东距、北距）。 | `AGeoReferencingSystem` |
| `Projected To Engine` | 将投影坐标系坐标转换为UE引擎空间坐标。 | `AGeoReferencingSystem` |
| `Get ENU Vectors At Geographic Location` | 在指定地理坐标处获取局部东、北、天方向向量（在引擎坐标系中）。 | `AGeoReferencingSystem` |
| `Get Tangent Transform At Geographic Location` | 获取在指定地理坐标处与地球椭球体相切的变换（Transform），用于放置物体。 | `AGeoReferencingSystem` |
| `Fly To Location Geographic` | 使 `RoundPlanetPawn` 平滑飞行至指定的地理坐标。 | `ARoundPlanetPawn` |
| `Fly To Location Latitude Longitude Altitude` | `Fly To Location Geographic` 的重载版本，参数更直观。 | `ARoundPlanetPawn` |
| `Interrupt Fly To Location` | 中断当前的飞行移动。 | `ARoundPlanetPawn` |
| `Increase Speed Scalar` / `Decrease Speed Scalar` | 调整 `RoundPlanetPawn` 的移动速度倍率。 | `ARoundPlanetPawn` |

### 使用示例（蓝图描述）

**示例1：将外部地理坐标点放置到场景中**
1.  在场景中放置一个 `AGeoReferencingSystem` Actor，并在其细节面板中配置 `ProjectedCRS`（例如 `EPSG:32631`）和 `GeographicCRS`（通常为 `EPSG:4326`），并设置合适的 `Origin`。
2.  在蓝图中，使用 “Get Geo Referencing System” 节点获取该系统。
3.  使用 “Geographic To Engine” 节点。将外部数据中的纬度、经度、海拔值连接到 `Geographic Coordinates` 输入。
4.  将输出的 `Engine Coordinates` 连接到一个 Actor 的 `Set Actor Location` 节点。该Actor就会被放置在对应的真实世界位置。

**示例2：实现从A点飞到B点的相机**
1.  将游戏模式默认Pawn类设置为 `ARoundPlanetPawn` 或其子类。
2.  在蓝图中（例如在关卡蓝图里），使用 “Get Player Pawn” 获取该Pawn的引用并转换为 `ARoundPlanetPawn`。
3.  当需要飞行时（例如按键触发），调用 “Fly To Location Latitude Longitude Altitude” 节点。
4.  将目的地的纬度、经度、海拔值连接到对应输入，并设置到达时的偏航角（`YawAtDestination`）和俯仰角（`PitchAtDestination`）。
5.  可选地，将 `Can Interrupt By Moving` 设置为 `True`，允许玩家通过移动摇杆来中断自动飞行。

## C++ 用法

### 头文件引入

```cpp
// 核心系统和数据结构
#include "GeoReferencingSystem.h"
#include "GeographicCoordinates.h"

// 如果需要使用圆形地球 Pawn
#include "RoundPlanetPawn.h"
```

### 基本用法

以下示例展示了如何获取 `GeoReferencingSystem` 并进行基本坐标转换。
(参考自 `AGeoReferencingSystem` 的公共接口)

```cpp
// 在一个 Actor 或 Component 中
void AMyActor::ConvertLocation()
{
    // 1. 获取 GeoReferencingSystem 实例
    AGeoReferencingSystem* GeoRefSystem = AGeoReferencingSystem::GetGeoReferencingSystem(GetWorld());
    if (!GeoRefSystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("GeoReferencingSystem not found in world."));
        return;
    }

    // 2. 定义一个地理坐标 (例如: 北京天安门广场)
    FGeographicCoordinates BeijingCoord;
    BeijingCoord.Latitude = 39.9087;   // 纬度
    BeijingCoord.Longitude = 116.3975; // 经度
    BeijingCoord.Altitude = 50.0;      // 海拔（米）

    // 3. 将地理坐标转换为引擎世界坐标
    FVector EnginePosition;
    GeoRefSystem->GeographicToEngine(BeijingCoord, EnginePosition);

    // 4. 使用转换后的坐标（例如，放置一个物体）
    SetActorLocation(EnginePosition);

    // 5. 反向转换验证（可选）
    FGeographicCoordinates OutGeoCoord;
    GeoRefSystem->EngineToGeographic(EnginePosition, OutGeoCoord);
    UE_LOG(LogTemp, Log, TEXT("Round-trip verification: Lat=%f, Lon=%f, Alt=%f"),
        OutGeoCoord.Latitude, OutGeoCoord.Longitude, OutGeoCoord.Altitude);
}
```

### 进阶用法

获取特定位置的ENU坐标系，并用于对齐物体。
(参考自 `AGeoReferencingSystem` 的 `GetENUVectorsAtGeographicLocation` 接口)

```cpp
void AMyActor::AlignObjectToGround()
{
    AGeoReferencingSystem* GeoRefSystem = AGeoReferencingSystem::GetGeoReferencingSystem(GetWorld());
    if (!GeoRefSystem) return;

    // 假设要对齐的位置
    FGeographicCoordinates TargetLocation(116.3975, 39.9087, 50.0); // 经度，纬度，海拔

    // 获取该位置的局部 ENU 方向向量（在引擎坐标系中）
    FVector East, North, Up;
    GeoRefSystem->GetENUVectorsAtGeographicLocation(TargetLocation, East, North, Up);

    // 构建一个旋转矩阵，使其 X轴 指向东，Y轴 指向北，Z轴 指向上（天）
    FMatrix AlignmentMatrix;
    AlignmentMatrix.SetAxes(&East, &North, &Up, nullptr);

    // 从矩阵创建旋转器（Rotator）
    FRotator AlignmentRotation = AlignmentMatrix.Rotator();

    // 应用此旋转到当前 Actor，使其与当地地面“平行”并对齐地理方向
    SetActorRotation(AlignmentRotation);
}

// 更简单的替代方法：直接使用 GetTangentTransform
void AMyActor::AlignObjectUsingTransform()
{
    AGeoReferencingSystem* GeoRefSystem = AGeoReferencingSystem::GetGeoReferencingSystem(GetWorld());
    if (!GeoRefSystem) return;

    FGeographicCoordinates TargetLocation(116.3975, 39.9087, 50.0);
    FTransform TangentTransform = GeoRefSystem->GetTangentTransformAtGeographicLocation(TargetLocation);

    // 此变换包含正确的位置、旋转（与地表相切）和缩放（1.0）
    // 可以直接设置给Actor，或者单独提取旋转应用
    SetActorTransform(TangentTransform);
}
```

## Demo 示例

一个最小化的C++示例，演示如何从一个地理坐标点创建并渲染一个简单的球体。
(此示例基于 `AGeoReferencingSystem` 的核心转换功能)

```cpp
// MyGeoMarker.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GeographicCoordinates.h"
#include "MyGeoMarker.generated.h"

class UStaticMeshComponent;

UCLASS()
class MYPROJECT_API AMyGeoMarker : public AActor
{
    GENERATED_BODY()

public:
    AMyGeoMarker();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UStaticMeshComponent* MarkerMesh;

    // 在编辑器或构造函数中设置
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Geo Reference")
    FGeographicCoordinates GeographicLocation;

protected:
    virtual void BeginPlay() override;
    virtual void OnConstruction(const FTransform& Transform) override;

private:
    void UpdateMarkerLocation();
};
```

```cpp
// MyGeoMarker.cpp
#include "MyGeoMarker.h"
#include "GeoReferencingSystem.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

AMyGeoMarker::AMyGeoMarker()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建一个简单的球体网格体
    MarkerMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MarkerMesh"));
    RootComponent = MarkerMesh;

    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMeshAsset(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if (SphereMeshAsset.Succeeded())
    {
        MarkerMesh->SetStaticMesh(SphereMeshAsset.Object);
        MarkerMesh->SetWorldScale3D(FVector(0.5f)); // 缩小一点
    }

    // 默认坐标：巴黎埃菲尔铁塔
    GeographicLocation = FGeographicCoordinates(2.2945, 48.8584, 300.0);
}

void AMyGeoMarker::BeginPlay()
{
    Super::BeginPlay();
    UpdateMarkerLocation();
}

void AMyGeoMarker::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    // 在编辑器中移动或修改属性时立即更新位置
    UpdateMarkerLocation();
}

void AMyGeoMarker::UpdateMarkerLocation()
{
    AGeoReferencingSystem* GeoRefSystem = AGeoReferencingSystem::GetGeoReferencingSystem(GetWorld());
    if (GeoRefSystem)
    {
        FVector EnginePos;
        GeoRefSystem->GeographicToEngine(GeographicLocation, EnginePos);
        SetActorLocation(EnginePos);

        // 可选：对齐到地表
        FTransform Tangent = GeoRefSystem->GetTangentTransformAtGeographicLocation(GeographicLocation);
        SetActorRotation(Tangent.GetRotation());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("AMyGeoMarker: Could not find GeoReferencingSystem. Marker will be at origin."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Proj` | **核心依赖**。一个外部的坐标转换库，用于处理所有地理坐标系统（CRS）之间的转换计算。插件通过 `Source/ThirdParty/Proj.Build.cs` 集成。 |
| `SQLiteCore` | **插件依赖**。`.uplugin` 中声明依赖，可能用于存储地理数据或坐标参考系统定义。 |
| `Slate` | 构建UI，用于编辑器工具或运行时控件（如果需要）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数导致的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 `UE_LOG` 宏迁移到 `UE_LOGF`（格式化日志宏）。 |
| 2026-03-04 | `32fcdd48` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4`. | 移除了受 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4` 宏保护的包含头。 |
| 2025-06-12 | `4a7c2bb3` | Replace some usages of FORCEINLINE with inline in WorldBuilding modules. | 在WorldBuilding相关模块中，将部分 `FORCEINLINE` 用法替换为 `inline`。 |
| 2025-05-27 | `37df175a` | Proj uses arm64 uwp library for Windows Arm64 for the time being. | PROJ 库目前对 Windows Arm64 平台使用 arm64 uwp 版本库。 |

### 维护评价

**总体评价：维护良好，功能稳定。**

- **创建时间**：插件于2021年4月创建，已有约4年历史，功能相对成熟。
- **更新频率**：最近一年（2025-2026）有多次提交，但更新内容主要是**维护性**和**平台兼容性**改进（如编译警告修复、日志API迁移、构建系统调整），而非重大新功能开发。这表明插件的核心功能已经稳定。
- **活跃度**：Epic Games 持续维护该插件，确保其与最新引擎版本兼容，并修复潜在问题。尽管不是每周更新，但仍在正常维护周期内。
- **已知问题/限制**：
    1.  插件默认未启用（`Installed: false`），需要在项目中手动启用。
    2.  使用平面投影模式（`FlatPlanet`）在超大范围环境下可能遇到精度问题，这在文档中有说明。
    3.  依赖外部 `Proj` 库，可能会增加包体大小，并在某些特定平台（如早期主机）带来集成复杂度。
- **是否推荐使用**：**强烈推荐**。对于任何需要与真实世界地理数据交互的UE项目，这是官方提供的、最可靠且功能完整的解决方案。其API设计清晰，同时支持蓝图和C++，文档（本示例）和社区资源也在逐渐丰富。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeoReferencing)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/georeferencing-in-unreal-engine/) (UE官方文档链接)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeoReferencing/Tests) (如果存在)