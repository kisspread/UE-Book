# Water

> Full suite of water tools and rendering techniques to easily add oceans, river, lakes or custom water bodies that carve landscape and interacts with gameplay

| 属性 | 值 |
|---|---|
| 中文名 | 水体系统 |
| 分类 | Water |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、网格体） |
| 模块 | `Water` (Runtime), `WaterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Water) | |

## 用途

Water 插件提供了一整套水体创作与渲染工具链，允许开发者快速在关卡中添加海洋、河流、湖泊或自定义水体。这些水体不仅具备高质量的视觉表现（如 Gerstner 波、动态水面反射），还能自动雕刻地形、与 Landscape 交互、支持物理浮力、Niagara 粒子特效以及环境查询系统。插件旨在解决 **开放世界水体的完整工作流**，从地形雕刻到游戏逻辑（浮力、游泳、水下效果）全覆盖。

## 使用场景

- 你正在制作一个包含广阔海洋的航海游戏，需要自动管理水体的碰撞、波浪和远距离渲染 → 使用 Ocean + WaterZone
- 你需要一条蜿蜒的河流，它能根据样条自动生成网格并雕刻河床 → 使用 River 水体
- 你需要一个湖面，周围有岛屿，并且湖底地形随样条变化 → 使用 Lake 水体 + Island 画笔
- 你希望角色进入水面后触发浮力效果，并受到水流影响 → 使用 BuoyancyComponent
- 你需要用 Niagara 粒子模拟水花、泡沫或雨滴，且粒子系统能采样水体信息 → 使用 NiagaraDataInterfaceWater

## 蓝图用法

以下节点均从 `Public/*.h` 中提取的 `UFUNCTION(BlueprintCallable)`。

### 水体控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetWaterBodyType` | 返回水体类型（River/Lake/Ocean/Custom） | `AWaterBody` |
| `GetWaterSpline` | 获取水体的样条组件 | `AWaterBody`、`AWaterBodyIsland` |
| `SetLakeTransitionMaterial` | 设置河流与湖泊过渡材质 | `UWaterBodyRiverComponent` |
| `SetOceanTransitionMaterial` | 设置河流与海洋过渡材质 | `UWaterBodyRiverComponent` |
| `SetLakeAndOceanTransitionMaterials` | 同时设置两种过渡材质 | `UWaterBodyRiverComponent` |
| `GetRiverWidthAtSplineInputKey` | 获取指定样条位置的河流宽度 | `UWaterBodyRiverComponent` |
| `GetRiverDepthAtSplineInputKey` | 获取指定样条位置的河流深度 | `UWaterBodyRiverComponent` |
| `SetRiverWidthAtSplineInputKey` | 设置指定样条位置的河流宽度 | `UWaterBodyRiverComponent` |
| `SetRiverDepthAtSplineInputKey` | 设置指定样条位置的河流深度 | `UWaterBodyRiverComponent` |

### 浮力系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCurrentWaterBodyComponents` | 获取当前所有重叠的水体组件 | `UBuoyancyComponent` |
| `IsOverlappingWaterBody` | 是否与任何水体重叠 | `UBuoyancyComponent` |
| `IsInWaterBody` | 是否处于水体内部（沉浸） | `UBuoyancyComponent` |
| `OnPontoonEnteredWater` / `OnPontoonExitedWater` | 浮筒进入/离开水体的蓝图事件委托 | `UBuoyancyComponent` |

### Niagara 集成

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetWaterBodyComponent` | 为 Niagara 组件的水体数据接口设置水体组件 | `UNiagaraWaterFunctionLibrary` |

### 环境查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RunTest`（内部实现） | 环境查询测试：测试一点是否在水体内 | `UEnvQueryTest_InsideWaterBody` |

### 浅水模拟（实验性）

`FShallowWaterSimulationGrid` 结构体提供 `SampleShallowWaterSimulationAtPosition`、`QueryShallowWaterSimulationAtPosition` 等函数，可在蓝图中用于查询预烘焙的浅水模拟数据（水速、水深、水面高度）。这些函数标注了 `UE_API` 但并未标记 `BlueprintCallable`，因此当前版本仅限 C++ 使用。

### 使用示例（蓝图）

1. **检测角色是否在湖中**：在 Actor 上添加 `BuoyancyComponent`，连接其 `On Pontoon Entered Water` / `On Pontoon Exited Water` 事件，可触发游泳动画切换。
2. **动态调整河流宽度**：获取 `WaterBodyRiver` 的样条，用 `Get River Width at Spline Input Key` 读取当前宽度，然后在游戏运行时调用 `Set River Width at Spline Input Key` 制造阻塞或拓宽效果。
3. **Niagara 水花**：在 Niagara 发射器中添加 `Water` 数据接口，然后在 BeginPlay 时调用 `Set Water Body Component`，粒子即可采样水面高度、波浪、速度等信息。

## C++ 用法

### 头文件引入

```cpp
#include "WaterBodyComponent.h"
#include "WaterBodyOceanComponent.h"
#include "WaterBodyRiverComponent.h"
#include "BuoyancyComponent.h"
#include "NiagaraWaterFunctionLibrary.h"
```

### 基本用法

#### 获取所有水体并遍历

```cpp
#include "WaterBodyManager.h"

// 从 World 获取水体管理器
if (UWorld* World = GetWorld())
{
    FWaterBodyManager& Manager = World->GetSubsystem<UWaterBodySubsystem>()->GetManager();
    Manager.ForEachWaterBodyComponent([&](UWaterBodyComponent* WaterBodyComp)
    {
        // 处理每个水体组件
        UE_LOG(LogTemp, Log, TEXT("WaterBody: %s"), *WaterBodyComp->GetName());
        return true; // 继续遍历
    });
}
```

*来源：`WaterBodyManager.h`*

#### 使用 BuoyancyComponent 进行浮力查询

```cpp
#include "BuoyancyComponent.h"

UBuoyancyComponent* Buoyancy = FindComponentByClass<UBuoyancyComponent>();
if (Buoyancy && Buoyancy->IsOverlappingWaterBody())
{
    const TArray<UWaterBodyComponent*>& WaterBodies = Buoyancy->GetCurrentWaterBodyComponents();
    for (UWaterBodyComponent* WaterBody : WaterBodies)
    {
        // 获取水面高度（包含波浪）
        FVector SurfacePos, PlaneLocation, PlaneNormal, Velocity;
        float Depth;
        WaterBody->GetWaterSurfaceInfoAtPosition(GetActorLocation(), /*bIncludeWaves*/true, SurfacePos, PlaneLocation, PlaneNormal, Depth, Velocity);
        DrawDebugSphere(GetWorld(), SurfacePos, 50.f, 12, FColor::Cyan);
    }
}
```

*来源：`BuoyancyComponent.h`、`WaterBodyComponent.h`（GetWaterSurfaceInfoAtPosition 由 UWaterBodyComponent 提供，此处为示意）*

#### 运行时修改河流宽度

```cpp
#include "WaterBodyRiverComponent.h"

UWaterBodyRiverComponent* RiverComp = Cast<UWaterBodyRiverComponent>(WaterBodyComp);
if (RiverComp)
{
    float CurrentWidth = RiverComp->GetRiverWidthAtSplineInputKey(0.5f);
    RiverComp->SetRiverWidthAtSplineInputKey(0.5f, CurrentWidth * 1.5f);
    // 调用 OnUpdateBody 触发网格重建（编辑器下会自动调用，运行时需手动）
    RiverComp->UpdateBody(false);
}
```

*来源：`WaterBodyRiverComponent.h`*

### 进阶用法

#### 生成水体碰撞组件（海洋 + 排除体积）

```cpp
#include "WaterBooleanUtils.h"

// 假设已有 Ocean 的边界框和排除体积列表
FBoxSphereBounds OceanBounds = ...;
TArray<AWaterBodyExclusionVolume*> Exclusions = ...;
FTransform ActorTransform = ...;

TArray<FBoxSphereBounds> OutBoxes;
TArray<TArray<FKConvexElem>> OutMeshConvexes;
FWaterBooleanUtils::BuildOceanCollisionComponents(
    OceanBounds, ActorTransform, Exclusions,
    OutBoxes, OutMeshConvexes, 500.0, 10.0
);
```

*来源：`WaterBooleanUtils.h`*

#### 构建水体静态网格（绕过 WaterZone）

```cpp
#include "WaterBodyMeshBuilder.h"
#include "WaterBodyInfoMeshComponent.h"

UWaterBodyComponent* WaterBodyComp = ...;
TArray<TObjectPtr<UWaterBodyInfoMeshComponent>> InfoMeshes;
// ... 创建 InfoMeshes 并配置

FWaterBodyMeshBuilder Builder;
bool bMakeConservativeRasterCompatible = true;
Builder.BuildWaterInfoMeshes(WaterBodyComp, InfoMeshes[0], InfoMeshes[1], bMakeConservativeRasterCompatible);
```

*来源：`WaterBodyMeshBuilder.h`*

## Demo 示例

以下是一个最小示例，展示如何在游戏运行时创建一座湖泊并让角色浮在水面上。

### MyWaterDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyWaterDemo.generated.h"

class AWaterBodyLake;
class UBuoyancyComponent;

UCLASS()
class MYGAME_API AMyWaterDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyWaterDemo();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SpawnLakeAt(const FVector& Center, float Radius);

private:
    UPROPERTY()
    AWaterBodyLake* LakeActor;

    UPROPERTY()
    UBuoyancyComponent* BuoyancyComponent;
};
```

### MyWaterDemo.cpp

```cpp
#include "MyWaterDemo.h"
#include "WaterBodyLakeActor.h"
#include "WaterBodyLakeComponent.h"
#include "WaterSplineComponent.h"
#include "BuoyancyComponent.h"
#include "Components/SplineComponent.h"

AMyWaterDemo::AMyWaterDemo()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建一个基本的角色组件用于浮力演示（这里简单用默认场景根）
    BuoyancyComponent = CreateDefaultSubobject<UBuoyancyComponent>(TEXT("BuoyancyComponent"));
}

void AMyWaterDemo::BeginPlay()
{
    Super::BeginPlay();
    // 寻找到湖泊并注册浮力
    if (LakeActor)
    {
        BuoyancyComponent->AddWaterBody(LakeActor->GetWaterBodyComponent()); // 假设有 AddWaterBody 方法（实际是自动检测）
    }
}

void AMyWaterDemo::SpawnLakeAt(const FVector& Center, float Radius)
{
    // 注意：AWaterBodyLake 需要 World 支持，此处仅示意
    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    LakeActor = GetWorld()->SpawnActor<AWaterBodyLake>(Center, FRotator::ZeroRotator, SpawnParams);

    // 获取水体样条组件并设置形状（圆形湖）
    UWaterSplineComponent* Spline = LakeActor->GetWaterSpline();
    // 添加四个点构成近似圆形的四边形
    float D = Radius * FMath::Sqrt(2.f) / 2.f;
    Spline->SetSplinePoints({
        FVector(Center.X - D, Center.Y, Center.Z),
        FVector(Center.X, Center.Y + D, Center.Z),
        FVector(Center.X + D, Center.Y, Center.Z),
        FVector(Center.X, Center.Y - D, Center.Z)
    }, ESplineCoordinateSpace::World, true);

    // 强制重建水体网格和碰撞
    LakeActor->GetWaterBodyComponent()->UpdateBody(false);
}
```

**注意**：实际项目中，`AWaterBodyLake` 的生成通常应通过编辑器放置或 World Partition 工作流，此处仅为概念演示。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Landmass` | 提供 Landscape 雕刻交互（笔刷、曲线等） |
| `Niagara` | Niagara 粒子系统与水体数据接口 |
| `GeometryProcessing` | 布尔运算、动态网格生成（水体碰撞构建等） |
| `BlueprintMaterialTextureNodes` | 材质编辑器中暴露的节点，用于水体材质 |

此外，`WaterEditor` 模块还依赖 `UnrealEd`、`LandscapeEditor` 等编辑器模块，但运行时无需。

## 维护状态

### 近期更新

- 2025-10-02 bfb2aaa5 — Post Process Volume:  Improvement to determinism of post process volume sorting.
- 2025-09-23 76aaaaf9 — [HWRT] Fix crash due to FWaterMeshSceneProxy moving FRayTracingGeometry in memory.
- 2025-09-23 34fe4187 — World Partition - HLOD: Store an HLOD build report property in the HLOD actors
- 2025-09-03 b34c0c64 — [Water] Fixed warning due to mismatching operand types in ternary operator
- 2025-09-03 9730d902 — [Water] Fixed crash due to caching FMaterialRenderProxy instead of UMaterialInterface

### 维护评价

Water 插件创建于 2025 年 9 月，属于全新实验性插件。从 git log 看，开发团队正积极修复 Bug 和优化性能，近一个月内有多次提交。虽然标记为实验性，但功能完整度较高，适合在 UE5.7 及以上版本中使用。推荐用于需要高质量水体的项目，但请注意：

- 仍需手动在插件列表中启用（默认关闭）。
- 实验性版本可能会在后续更新中出现破坏性变更。
- 浅水模拟（`BakedShallowWaterSimulationComponent`）仍处于早期阶段，仅提供 C++ API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Water)
- [官方文档]（当前无独立文档，可参考 UE 官方论坛与社区资源）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Water/Tests)（如存在）