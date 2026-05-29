# Water

> Full suite of water tools and rendering techniques to easily add oceans, river, lakes or custom water bodies that carve landscape and interacts with gameplay

| 属性 | 值 |
|---|---|
| 中文名 | 水体系统 |
| 分类 | Water |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `Water` (Runtime), `WaterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Water) | |

---

# Water 插件 — 汇总页

## 用途

Water 插件是 UE5 的完整水体解决方案，提供了一套从创作到渲染到物理交互的全流程工具链。它解决了以下核心问题：

1. **水体创建与管理**：通过样条线（Spline）定义河流、湖泊、海洋和自定义水体，支持自动切割地形（Landscape Carving），水面高度随地形适配
2. **水面渲染**：基于四叉树（Quadtree）的 GPU 驱动水面网格系统，支持多级 LOD、遮挡剔除、GPU 光线追踪，并能高效渲染无限延伸的海洋
3. **海浪模拟**：基于 Gerstner 波的水面波浪系统，支持从频谱数据（Phillips、Pierson-Moskowitz、JONSWAP）生成逼真海浪
4. **物理交互**：浮力组件（Buoyancy Component）支持物体漂浮、河流推力、岸边推力、下游旋转等物理行为；浮力计算支持异步物理模拟路径
5. **游戏玩法集成**：水下后处理（Post Process）、音频强度随水深/流速变化、Niagara 水体数据接口、导航网格（NavMesh）水体区域支持
6. **浅水模拟**：支持烘焙的浅水模拟数据，用于小型河流/池塘的水流效果

**为什么需要手动启用**：该插件默认未启用（`EnabledByDefault=false`），因为它的依赖较重（Niagara、Landmass、GeometryProcessing），且仍处于实验状态。

## 模块总览

| 模块 | 类型 | 说明 |
|---|---|---|
| [`Water`](docs/large/Water/WaterModule.md) | Runtime | 核心运行时模块：水体 Actor/Component、浮力系统、Gerstner 波、水面渲染、四叉树 |
| [`WaterEditor`](docs/large/Water/WaterEditorModule.md) | Editor | 编辑器工具：水体创建向导、水体画刷、地形切割工具、可视化调试 |

## 子模块文档

| 文档 | 说明 |
|---|---|
| [Water 核心运行时](docs/large/Water/WaterModule.md) | 水体系统运行时 API：水体 Actor/Component、浮力系统、Gerstner 波、水面网格、四叉树、Niagara 集成、水下后处理 |
| [WaterEditor 编辑器工具](docs/large/Water/WaterEditorModule.md) | 编辑器工具链：水体画刷、地形切割、水体创建向导、可视化面板 |

## 插件依赖

| 插件 | 说明 |
|---|---|
| `Landmass` | 地形雕刻工具，Water 用于水体对地形的切割 |
| `Niagara` | 粒子系统，Water 提供水体数据接口用于水面粒子效果 |
| `GeometryProcessing` | 几何处理库，Water 用于水体网格布尔运算（排除体积） |
| `BlueprintMaterialTextureNodes` | 蓝图材质纹理节点，用于水体材质的蓝图编辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `5fd19ba7` | [Water] Trash the old ocean collision components to free up their path names so new components will | 清理旧海洋碰撞组件以释放路径名 |
| 2026-05-14 | `1e201bfa` | Fix UWaterSplineMetadata parallel-curve desync when Depth, WaterVelocityScalar, or AudioIntensity ar | 修复水样条元数据的并行曲线同步问题 |
| 2026-05-12 | `dc876c8f` | [Water] Restored the behavior where if a water body has an unset material and "always generate water" | 恢复未设置材质的水体始终生成水面瓦片的行为 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 统一硬件光线追踪的网格批次所有权管理 |
| 2026-05-12 | `40da2015` | Only perform the water body static mesh conservative rasterization check if the static mesh is valid | 仅在静态网格有效时才执行保守光栅化检查 |

### 维护评价

**活跃维护中**。Water 插件在近 6 个月内持续有功能性更新和 bug 修复，Epic 团队仍在积极开发。作为实验性插件，API 在大版本间可能有破坏性变更（从源码中可以看到大量 `DEPRECATED` 标记）。目前仍标记为 `IsExperimentalVersion=true`，不建议用于生产环境的正式发布版本，但用于原型开发和内部项目是可行的。

---

# Water 核心运行时模块

## 蓝图用法

Water 插件提供了丰富的蓝图 API，按功能分组如下：

### 水体管理（WaterSubsystem）

`UWaterSubsystem` 是运行时访问水体信息的主入口，通过 `UWaterSubsystem::GetWaterSubsystem(World)` 获取。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Water Subsystem` | 获取水体子系统实例 | `UWaterSubsystem` |
| `Is Water Rendering Enabled` | 检查水面渲染是否启用 | `UWaterSubsystem` |
| `Is Underwater Post Process Enabled` | 检查水下后处理是否启用 | `UWaterSubsystem` |
| `Is Shallow Water Simulation Enabled` | 检查浅水模拟是否启用 | `UWaterSubsystem` |
| `Get Ocean Base Height` | 获取海洋基准高度（Z 坐标） | `UWaterSubsystem` |
| `Get Ocean Flood Height` | 获取海洋洪水高度偏移 | `UWaterSubsystem` |
| `Get Ocean Total Height` | 获取海洋总高度（基准+洪水） | `UWaterSubsystem` |
| `Set Ocean Flood Height` | 设置海洋洪水高度 | `UWaterSubsystem` |
| `Get Water Time Seconds` | 获取水体时间（用于波浪动画） | `UWaterSubsystem` |
| `Get Camera Underwater Depth` | 获取相机水下深度 | `UWaterSubsystem` |
| `Print To Water Log` | 输出日志到水体日志 | `UWaterSubsystem` |

### 水体查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Water Surface Info At Location` | 查询指定位置的水面信息（位置、法线、速度、深度） | `UWaterBodyComponent` |
| `Get Water Body Type` | 获取水体类型（河流/湖泊/海洋/自定义） | `AWaterBody` |
| `Get Water Body Component` | 获取水体组件 | `AWaterBody` |
| `Get Water Spline` | 获取水体样条线 | `AWaterBody` |

### 浮力系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is In Water Body` | 检查浮力组件是否在水体中 | `UBuoyancyComponent` |
| `Is Overlapping Water Body` | 检查是否与水体重叠 | `UBuoyancyComponent` |
| `Get Current Water Body Components` | 获取当前接触的水体组件列表 | `UBuoyancyComponent` |
| `Get Last Water Surface Info` | 获取最近一次的水面信息 | `UBuoyancyComponent` |
| `On Pontoon Entered Water` | 浮筒进入水面事件回调 | `UBuoyancyComponent` |
| `On Pontoon Exited Water` | 浮筒离开水面事件回调 | `UBuoyancyComponent` |

### Niagara 水体集成

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Water Body Component` | 将水体组件设置到 Niagara 粒子系统的水体数据接口 | `UNiagaraWaterFunctionLibrary` |

### 使用示例（蓝图描述）

**让物体浮在水面上**：
1. 给物体添加 `UBuoyancyComponent`
2. 在 `BuoyancyData` 中配置 `Pontoons`（浮筒数组），每个浮筒定义半径和相对位置
3. 调整 `BuoyancyCoefficient`（浮力系数）、`BuoyancyDamp`（阻尼）等参数
4. 在场景中放置 `AWaterBodyOcean` 或其他水体 Actor
5. 物体进入水体后会自动计算浮力

**查询水面高度**：
1. 获取 `UWaterSubsystem` → 调用 `GetOceanTotalHeight()` 获取海洋总高度
2. 或者直接在 `UWaterBodyComponent` 上调用 `GetWaterSurfaceInfoAtLocation()` 获取精确的水面信息（包括波浪扰动）

**河流中的物体推动**：
1. 在 `UBuoyancyComponent` 的 `BuoyancyData` 中启用 `bApplyRiverForces`
2. 设置 `WaterVelocityStrength`（水流推力强度）、`WaterShorePushFactor`（岸边推力系数）
3. 启用 `bApplyDownstreamAngularRotation` 让物体自动朝向水流方向旋转

---

## C++ 用法

### 头文件引入

```cpp
// 核心水体系统
#include "WaterSubsystem.h"
#include "WaterBodyActor.h"
#include "WaterBodyComponent.h"

// 浮力系统
#include "BuoyancyComponent.h"
#include "BuoyancyManager.h"

// Gerstner 波浪
#include "GerstnerWaterWaves.h"
#include "WaterWaves.h"

// Niagara 集成
#include "NiagaraDataInterfaceWater.h"
#include "NiagaraWaterFunctionLibrary.h"

// 水体类型与查询
#include "WaterBodyTypes.h"
```

### 基本用法 — 查询水面信息

```cpp
// 来源: Public/WaterSubsystem.h, Public/WaterBodyTypes.h

// 1. 通过子系统获取海洋高度
UWaterSubsystem* WaterSubsystem = UWaterSubsystem::GetWaterSubsystem(GetWorld());
if (WaterSubsystem)
{
    float OceanHeight = WaterSubsystem->GetOceanTotalHeight();
    float BaseHeight = WaterSubsystem->GetOceanBaseHeight();
    float FloodHeight = WaterSubsystem->GetOceanFloodHeight();
}

// 2. 查询特定位置的水面详细信息
UWaterBodyComponent* WaterBody = /* 获取水体组件 */;
if (WaterBody)
{
    FVector SurfaceLocation;
    FVector SurfaceNormal;
    FVector Velocity;
    float Depth;

    bool bInWater = WaterBody->GetWaterSurfaceInfoAtLocation(
        QueryLocation, SurfaceLocation, SurfaceNormal, Velocity, Depth);
}
```

### 基本用法 — 浮力组件

```cpp
// 来源: Public/BuoyancyComponent.h, Public/BuoyancyTypes.h

// 给 Actor 添加浮力
UBuoyancyComponent* BuoyancyComp = NewObject<UBuoyancyComponent>(MyActor);

// 配置浮筒（Pontoon）—— 浮力计算的采样点
FSphericalPontoon Pontoon;
Pontoon.RelativeLocation = FVector(0, 0, -50);  // 相对位置
Pontoon.Radius = 100.0f;                         // 采样半径
Pontoon.bFXEnabled = true;                       // 允许产生进入水面的效果

BuoyancyComp->BuoyancyData.Pontoons.Add(Pontoon);

// 调整浮力参数
BuoyancyComp->BuoyancyData.BuoyancyCoefficient = 0.15f;
BuoyancyComp->BuoyancyData.MaxBuoyantForce = 5000000.f;

// 监听水面事件
BuoyancyComp->OnEnteredWaterDelegate.AddDynamic(this, &AMyActor::OnEnterWater);
BuoyancyComp->OnExitedWaterDelegate.AddDynamic(this, &AMyActor::OnExitWater);
```

### 进阶用法 — Gerstner 波浪系统

```cpp
// 来源: Public/GerstnerWaterWaves.h, Public/WaterWaves.h

// 创建 Gerstner 波浪生成器
UGerstnerWaterWaveGeneratorSimple* Generator = NewObject<UGerstnerWaterWaveGeneratorSimple>();
Generator->NumWaves = 32;
Generator->MinWavelength = 100.0f;
Generator->MaxWavelength = 5000.0f;
Generator->MinAmplitude = 2.0f;
Generator->MaxAmplitude = 60.0f;
Generator->WindAngleDeg = 45.0f;           // 主风向
Generator->DirectionAngularSpreadDeg = 90.0f; // 方向扩散角

// 创建波浪实例
UGerstnerWaterWaves* Waves = NewObject<UGerstnerWaterWaves>();
Waves->GerstnerWaveGenerator = Generator;
Waves->RecomputeWaves(true);

// 应用到水体
AWaterBody* WaterBody = /* 获取水体 */;
WaterBody->SetWaterWaves(Waves);

// 手动查询波浪高度
FVector Normal;
float WaveHeight = Waves->GetWaveHeightAtPosition(
    WorldPosition, WaterDepth, CurrentTime, Normal);
float SimpleHeight = Waves->GetSimpleWaveHeightAtPosition(
    WorldPosition, WaterDepth, CurrentTime);
```

### 进阶用法 — 自定义水体查询标志

```cpp
// 来源: Public/WaterBodyTypes.h

// 使用详细的查询标志获取水体信息
EWaterBodyQueryFlags Flags = 
    EWaterBodyQueryFlags::ComputeLocation     // 计算水面位置
    | EWaterBodyQueryFlags::ComputeNormal      // 计算法线
    | EWaterBodyQueryFlags::ComputeVelocity    // 计算流速
    | EWaterBodyQueryFlags::ComputeImmersionDepth // 计算浸入深度
    | EWaterBodyQueryFlags::IncludeWaves;      // 包含波浪扰动

// 通过 TryQueryWaterInfoClosestToWorldLocation 进行安全查询
TValueOrError<FWaterBodyQueryResult, EWaterBodyQueryError> Result = 
    WaterBodyComponent->TryQueryWaterInfoClosestToWorldLocation(WorldPos, Flags);

if (Result.HasValue())
{
    const FWaterBodyQueryResult& QueryResult = Result.GetValue();
    if (QueryResult.IsInWater())
    {
        FVector SurfacePos = QueryResult.GetWaterSurfaceLocation();
        FVector Normal = QueryResult.GetWaterSurfaceNormal();
        float Immersion = QueryResult.GetImmersionDepth();
        FVector Vel = QueryResult.GetVelocity();
    }
}
```

### 进阶用法 — Niagara 水体粒子

```cpp
// 来源: Public/NiagaraDataInterfaceWater.h, Public/NiagaraWaterFunctionLibrary.h

// 通过蓝图函数库设置水体
UNiagaraWaterFunctionLibrary::SetWaterBodyComponent(
    MyNiagaraComponent, 
    TEXT("WaterDI"),        // Niagara 系统中的数据接口参数名
    MyWaterBodyComponent    // 要关联的水体组件
);

// 在 C++ 中直接操作数据接口
UNiagaraDataInterfaceWater* WaterDI = NewObject<UNiagaraDataInterfaceWater>();
WaterDI->SetWaterBodyComponent(MyWaterBodyComponent);
// WaterDI 提供 GetWaterDataAtPoint 和 GetWaveParamLookupTableOffset 等 VM 函数
```

---

## Demo 示例

### 浮力物体完整示例

```cpp
// FloatingBarrel.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FloatingBarrel.generated.h"

class UStaticMeshComponent;
class UBuoyancyComponent;

UCLASS()
class AFloatingBarrel : public AActor
{
    GENERATED_BODY()

public:
    AFloatingBarrel();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> MeshComp;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UBuoyancyComponent> BuoyancyComp;
};
```

```cpp
// FloatingBarrel.cpp
#include "FloatingBarrel.h"
#include "Components/StaticMeshComponent.h"
#include "BuoyancyComponent.h"
#include "BuoyancyTypes.h"

AFloatingBarrel::AFloatingBarrel()
{
    MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComp;
    MeshComp->SetSimulatePhysics(true);

    BuoyancyComp = CreateDefaultSubobject<UBuoyancyComponent>(TEXT("Buoyancy"));
}

void AFloatingBarrel::BeginPlay()
{
    Super::BeginPlay();

    // 配置两个浮筒：前部和后部
    BuoyancyComp->BuoyancyData.Pontoons.Empty();

    FSphericalPontoon FrontPontoon;
    FrontPontoon.RelativeLocation = FVector(50, 0, -30);
    FrontPontoon.Radius = 40.0f;
    BuoyancyComp->BuoyancyData.Pontoons.Add(FrontPontoon);

    FSphericalPontoon BackPontoon;
    BackPontoon.RelativeLocation = FVector(-50, 0, -30);
    BackPontoon.Radius = 40.0f;
    BuoyancyComp->BuoyancyData.Pontoons.Add(BackPontoon);

    // 微调浮力参数
    BuoyancyComp->BuoyancyData.BuoyancyCoefficient = 0.12f;
    BuoyancyComp->BuoyancyData.MaxBuoyantForce = 500000.f;
    BuoyancyComp->BuoyancyData.bApplyDragForcesInWater = true;
    BuoyancyComp->BuoyancyData.DragCoefficient = 15.f;
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Landmass` | 地形雕刻接口（水体切割地形） |
| `Niagara` | 粒子系统水体数据接口 |
| `GeometryProcessing` | 动态网格布尔运算（排除体积处理） |
| `Chaos` | Chaos 物理引擎（异步浮力模拟） |

无特殊依赖（仅标准 Core/Engine/Slate 等）以外的依赖已在上表列出。

> 注意：`Water` 模块还依赖 `PhysicsCore`、`MeshDescription`、`MeshConversion`、`RenderCore`、`RHI` 等渲染/网格相关模块。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `5fd19ba7` | [Water] Trash the old ocean collision components to free up their path names so new components will | 清理旧海洋碰撞组件以释放路径名 |
| 2026-05-14 | `1e201bfa` | Fix UWaterSplineMetadata parallel-curve desync when Depth, WaterVelocityScalar, or AudioIntensity ar | 修复水样条元数据并行曲线同步问题 |
| 2026-05-12 | `dc876c8f` | [Water] Restored the behavior where if a water body has an unset material and "always generate water" | 恢复未设置材质水体始终生成瓦片的行为 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 统一硬件光线追踪网格批次管理 |
| 2026-05-12 | `40da2015` | Only perform the water body static mesh conservative rasterization check if the static mesh is valid | 仅在网格有效时执行保守光栅化检查 |

### 维护评价

- **创建时间**：2020-10-22，约 6 年历史
- **维护频率**：近 1 个月内有多次提交，属于**活跃维护**状态
- **实验状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`。API 在版本间存在大量废弃和迁移（如 `AWaterBody` 上的功能迁移到 `UWaterBodyComponent`，浮力组件数据结构重构等）
- **代码质量**：架构成熟，四叉树水面渲染系统支持 CPU 和 GPU 驱动两种路径，浮力系统支持同步和异步物理
- **推荐**：适合原型开发和内部项目。用于正式发布需谨慎，因为实验性 API 可能在后续版本中发生破坏性变更。建议密切关注 `WaterVersion.h` 中的版本迁移说明。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Water)
- [官方文档]()（暂无）