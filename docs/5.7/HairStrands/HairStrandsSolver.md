# Groom

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、LOD 配置、Groom 缓存资产） |
| 模块 | `HairStrandsCore` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsDataflow` (Runtime), `HairCardGeneratorFramework` (Runtime), `HairStrandsEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands（Groom）插件是 UE5 中用于**毛发/发型渲染与物理模拟**的完整解决方案。它解决的核心问题是：如何在实时渲染中高效地表现角色毛发的外观（渲染）和动态行为（物理模拟）。

该插件提供了以下核心能力：

- **Strand-based 毛发渲染**：基于发丝的渲染管线，支持百万级发丝的实时渲染，包括光照散射、阴影、透明度排序等
- **Groom 物理模拟**：通过 Chaos 物理引擎驱动毛发的动态模拟，支持碰撞、弯曲、重力等物理效果
- **Groom 缓存系统**：通过 Chaos Cache 系统录制和回放毛发模拟数据，避免运行时重复计算
- **Dataflow 集成**：将毛发模拟接入 UE5 的 Dataflow 节点图系统，支持可视化编程方式配置模拟流程
- **Hair Card 生成**：自动生成用于 LOD 优化的 Hair Card（面片毛发），在远距离用低面数几何体替代发丝渲染
- **Deformer 集成**：通过 Optimus Deformer Graph 对毛发进行 GPU 变形处理

该插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动开启。

## 使用场景

- 你在制作写实角色，需要高质量的发型渲染 → 启用 HairStrands 插件，导入 Alembic Groom 资产
- 你需要角色毛发在运动中产生自然的物理摆动 → 使用 GroomComponent 的模拟功能配合 GroomSolverComponent
- 你需要将毛发模拟结果缓存下来以提升运行时性能 → 使用 GroomCache 系统录制模拟数据
- 你需要在远距离用低面数面片替代发丝渲染以优化性能 → 使用 Hair Card Generator 自动生成 LOD 资产
- 你需要通过可视化节点图配置复杂的毛发模拟流程 → 使用 Dataflow 节点（如 AddSolverDeformerNode）
- 你需要对毛发进行 GPU 端的自定义变形（如风吹效果）→ 使用 HairStrandsDeformer 模块配合 Optimus

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Groom` | 设置 Groom 资产到组件 | `UGroomComponent` |
| `Set PhysicsAsset` | 设置用于碰撞的物理资产 | `UGroomComponent` |
| `Set NiagaraComponent` | 关联 Niagara 粒子系统用于毛发效果 | `UGroomComponent` |
| `ResetSimulation` | 重置毛发模拟状态 | `UGroomSolverComponent` |
| `SetSolverSettings` | 设置求解器参数（LOD 距离、最大点数等） | `UGroomSolverComponent` |

### 使用示例

**基本毛发组件设置**：
1. 在角色蓝图中添加 `GroomComponent`
2. 将导入的 Groom 资产（.abc 文件导入后生成）赋值给组件的 Groom 属性
3. 设置 `Hair Width`、`Hair Shadow Density` 等渲染参数
4. 如需物理模拟，启用 `Simulation Settings` 并配置碰撞和约束

**使用 GroomSolverComponent 进行批量模拟**：
1. 添加 `GroomSolverComponent` 到场景
2. 将多个 `GroomComponent` 的 `Solver` 属性指向该 SolverComponent
3. 在 SolverComponent 上配置 `MaxLODDistance`、`MinLODDistance` 控制 LOD 切换
4. 通过 Dataflow 图连接 `AddSolverDeformerNode` 添加自定义变形器

## C++ 用法

### 头文件引入

```cpp
#include "GroomComponent.h"
#include "GroomSolverComponent.h"
#include "GroomCacheAdapter.h"
#include "GroomCache.h"
```

### 基本用法

**创建和配置 GroomComponent**（基于 GroomComponent.h）：

```cpp
// 在 Actor 中创建 GroomComponent
UGroomComponent* GroomComp = NewObject<UGroomComponent>(this);
GroomComp->SetupAttachment(RootComponent);
GroomComp->RegisterComponent();

// 设置 Groom 资产
GroomComp->SetGroom(GroomAsset);

// 启用模拟
GroomComp->SetEnableSimulation(true);
```

### 进阶用法

**使用 GroomSolverComponent 配置 LOD 和模拟**（基于 GroomSolverComponent.h）：

```cpp
// 创建 Solver 组件
UGroomSolverComponent* SolverComp = NewObject<UGroomSolverComponent>(this);
SolverComp->SetupAttachment(RootComponent);
SolverComp->RegisterComponent();

// 配置求解器设置
FGroomSolverSettings Settings;
Settings.MaxLODDistance = 2000.0f;   // 超过 2000 单位不模拟
Settings.MinLODDistance = 100.0f;    // 100 单位内全精度模拟
Settings.MaxPointsCount = 50000;     // 最大模拟点数

// 将 GroomComponent 绑定到 Solver
GroomComp->SetSolverComponent(SolverComp);
```

**使用 GroomCacheAdapter 录制模拟缓存**（基于 GroomCacheAdapter.h）：

```cpp
// GroomCacheAdapter 通过 Chaos Cache 系统自动工作
// 在编辑器中使用 Sequencer 录制毛发模拟数据
// 录制结果保存为 UGroomCache 资产，可在运行时回放

// 验证组件是否支持缓存
UE::Groom::FGroomCacheAdapter Adapter;
bool bSupported = Adapter.SupportsComponentClass(UGroomComponent::StaticClass());

// 初始化录制
FObservedComponent Observed;
Adapter.InitializeForRecord(GroomComponent, Observed);

// 录制完成后，缓存数据存储在 UGroomCache 资产中
// 回放时通过 InitializeForPlayback 加载缓存
Adapter.InitializeForPlayback(GroomComponent, Observed, CurrentTime);
```

## Demo 示例

**创建一个带物理模拟的 Groom Actor**：

```cpp
// GroomActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GroomActor.generated.h"

class UGroomComponent;
class UGroomSolverComponent;
class UGroomAsset;

UCLASS()
class AGroomActor : public AActor
{
    GENERATED_BODY()

public:
    AGroomActor();

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UGroomSolverComponent> SolverComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UGroomComponent> GroomComponent;

    UPROPERTY(EditAnywhere, Category = "Groom")
    TObjectPtr<UGroomAsset> GroomAsset;

    UPROPERTY(EditAnywhere, Category = "Groom|LOD")
    float MaxLODDistance = 1500.0f;

    UPROPERTY(EditAnywhere, Category = "Groom|LOD")
    float MinLODDistance = 200.0f;

    UFUNCTION(BlueprintCallable, Category = "Groom")
    void ResetGroomSimulation();
};
```

```cpp
// GroomActor.cpp
#include "GroomActor.h"
#include "GroomComponent.h"
#include "GroomSolverComponent.h"
#include "GroomAsset.h"

AGroomActor::AGroomActor()
{
    // 创建 Solver 组件
    SolverComponent = CreateDefaultSubobject<UGroomSolverComponent>(TEXT("GroomSolver"));
    RootComponent = SolverComponent;

    // 创建 Groom 组件并附加到 Solver
    GroomComponent = CreateDefaultSubobject<UGroomComponent>(TEXT("Groom"));
    GroomComponent->SetupAttachment(RootComponent);
}

void AGroomActor::ResetGroomSimulation()
{
    if (SolverComponent)
    {
        // 重置求解器中的所有毛发模拟状态
        // 通过 Dataflow 系统触发重置事件
        SolverComponent->ResetSimulation();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | 毛发核心数据结构（Strands、GroomAsset、GroomBuilder） |
| `HairStrandsRuntime` | 运行时毛发渲染管线 |
| `HairStrandsSolver` | 毛发物理求解器、GroomCache 适配器、Dataflow 节点 |
| `HairStrandsDeformer` | GPU 毛发变形器（Optimus 集成） |
| `HairStrandsDataflow` | Dataflow 节点图集成 |
| `HairCardGeneratorFramework` | Hair Card 自动生成框架 |
| `HairStrandsEditor` | 编辑器工具（Groom 导入、预览） |
| `Chaos` | Chaos 物理引擎（模拟驱动） |
| `Dataflow` | Dataflow 节点图框架 |
| `Niagara` | 粒子系统集成（毛发特效） |
| `Optimus` | GPU 计算图框架（Deformer Graph） |

## 维护状态

### 近期更新

```
- d41996b25d54 Fix dataflow crash when reseting simulation while groom deformers are running
  → 修复了在 Dataflow 模拟重置时 Groom Deformer 运行中导致的崩溃
- cb28d8f41d3d Bending model for groom + geometric collision+ guides solver
  → 新增弯曲模型、几何碰撞和引导线求解器，毛发物理模拟能力显著增强
- 0591fc2e61cc Fix CIS with bad includes in the groom solver component
  → 修复 GroomSolverComponent 中的头文件引用问题
```

### 维护评价

HairStrands（Groom）插件自 2019 年创建以来持续活跃维护，是 UE5 毛发系统的核心组件。从近期 commit 可以看出：

- **活跃维护**：最近的更新包含重要的功能增强（弯曲模型、几何碰撞）和关键 bug 修复，说明 Epic 仍在积极开发
- **功能成熟度高**：经过 6 年迭代，已从实验性功能发展为生产级毛发解决方案，被广泛用于 MetaHuman 等项目
- **架构复杂**：7 个子模块覆盖了从核心数据、渲染、物理模拟、缓存、变形器到编辑器工具的完整管线
- **默认不启用**：`EnabledByDefault: false` 表明该插件仍被视为可选功能，可能因为性能开销较大
- **推荐使用**：对于需要高质量毛发渲染和模拟的项目（如写实角色、MetaHuman），强烈推荐启用

⚠️ 注意：该插件对 GPU 性能有一定要求，低端设备上建议使用 Hair Card LOD 方案替代 Strand 渲染。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HairStrands)
- [GroomSolverComponent 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/HairStrands/Source/HairStrandsSolver/Public/GroomSolverComponent.h)
- [GroomCacheAdapter 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/HairStrands/Source/HairStrandsSolver/Public/GroomCacheAdapter.h)
- [AddSolverDeformerNode 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/HairStrands/Source/HairStrandsSolver/Public/AddSolverDeformerNode.h)