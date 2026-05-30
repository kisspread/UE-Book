# Groom (Hair Strands Solver)

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 中文名 | 毛发求解器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、毛发缓存） |
| 模块 | `HairCardGeneratorFramework` (Runtime), `HairStrandsCore` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands 插件（FriendlyName: Groom）是 UE5 中用于毛发（Groom/Alembic Hair）渲染和物理模拟的完整解决方案。它解决的核心问题是：如何在实时渲染中高效地处理数万根毛发的渲染和物理交互。

该插件包含多个模块，各司其职：
- **HairStrandsCore**：核心数据结构和资产类型（UGroomAsset、UGroomBindingAsset 等）
- **HairStrandsRuntime**：运行时渲染（毛发的 Strands 渲染、LOD、插值等）
- **HairStrandsSolver**：基于 Dataflow 框架的物理求解器，支持多 Groom 联合模拟
- **HairStrandsDeformer**：网格变形器集成，将毛发模拟结果应用到 SkeletalMesh
- **HairCardGeneratorFramework**：毛发卡片生成（将 Strand 毛发烘焙为网格卡片用于 LOD）
- **HairStrandsDataflow**：Dataflow 图节点集成
- **HairStrandsEditor**：编辑器工具和资产导入

HairStrandsSolver 模块专注于**多毛发联合模拟求解**，通过 UGroomSolverComponent 将多个 GroomComponent 注册到同一个求解器中，实现协调一致的物理模拟效果，并支持碰撞、LOD 距离优化和 Chaos 缓存系统。

## 使用场景

- 你在制作角色毛发/毛皮，需要多股毛发协调模拟（如长发、马尾、胡须） → 创建 UGroomSolverComponent，将各 GroomComponent 添加到求解器
- 你需要毛发模拟支持碰撞（如毛发碰到肩膀、身体） → 使用 AddCollisionComponent 注册碰撞网格
- 你需要控制远处角色的毛发模拟性能 → 通过 FGroomSolverSettings 调整 MinLODDistance/MaxLODDistance
- 你需要录制/回放毛发模拟动画 → 使用 GroomCacheAdapter 与 Chaos Cache 系统集成
- 你需要在 Dataflow 图中编排毛发模拟流程 → 使用 FAddSolverDeformerDataflowNode 节点

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddGroomComponent` | 将一个 GroomComponent 添加到求解器中进行联合模拟 | `UGroomSolverComponent` |
| `RemoveGroomComponent` | 从求解器中移除一个 GroomComponent | `UGroomSolverComponent` |
| `ResetGroomComponents` | 重置求解器中的所有 GroomComponent | `UGroomSolverComponent` |
| `AddCollisionComponent` | 添加碰撞网格组件到求解器，需指定 LOD 索引 | `UGroomSolverComponent` |
| `RemoveCollisionComponent` | 从求解器中移除碰撞网格组件 | `UGroomSolverComponent` |
| `ResetCollisionComponents` | 重置求解器中的所有碰撞组件 | `UGroomSolverComponent` |
| `SetDeformerSolver` | 设置求解器使用的网格变形器 | `UGroomSolverComponent` |

### 使用示例（蓝图描述）

**基本设置：多毛发联合模拟**

1. 在角色 Actor 上放置一个 `UGroomSolverComponent`
2. 在 `Details` 面板中设置 `SolverSettings`：
   - `MinLODDistance`：低于此距离启用完整模拟（默认 100）
   - `MaxLODDistance`：高于此距离禁用模拟（默认 1000）
   - `MaxPointsCount`：最大模拟点数上限（默认 100000）
3. 在 `BeginPlay` 事件中，使用 `AddGroomComponent` 节点依次将各 `UGroomComponent`（头发、眉毛、胡须等）添加到求解器
4. 如需碰撞，在 `BeginPlay` 中使用 `AddCollisionComponent` 节点添加角色身体的 SkeletalMeshComponent，指定合适的 LODIndex

**Dataflow 模拟流程：**

1. 创建 `UGroomSolverComponent`，在 `Dataflow` 分类下设置 `SimulationAsset`
2. 在 Dataflow 图中使用 `FAddSolverDeformerDataflowNode` 节点（分类：Physics|Solver）
3. 将 `MeshDeformer`（如 Optimus Deformer）连接到该节点
4. 节点自动提供 SimulationTime 和 PhysicsSolvers 的输入/输出连接
5. 可动态添加/移除数值、向量、字符串、布尔、Transform 类型的输入 Pin

## C++ 用法

### 头文件引入

```cpp
#include "GroomSolverComponent.h"
#include "GroomCacheAdapter.h"
#include "AddSolverDeformerNode.h"
```

### 基本用法

以下示例展示如何以编程方式创建求解器并注册 Groom 组件：

```cpp
// 来源: Public/GroomSolverComponent.h

// 在 Actor 中创建求解器组件
UGroomSolverComponent* Solver = NewObject<UGroomSolverComponent>(this);
Solver->RegisterComponent();

// 设置求解器参数
// FGroomSolverSettings 控制 LOD 行为
// MinLODDistance: 低于此距离执行完整模拟
// MaxLODDistance: 高于此距离跳过模拟
// MaxPointsCount: 最大模拟点数

// 添加 Groom 组件到求解器
Solver->AddGroomComponent(MyGroomComponent);

// 添加碰撞组件（带 LOD 索引）
Solver->AddCollisionComponent(MyBodyMeshComponent, /*LODIndex=*/0);
```

### 进阶用法

使用 Dataflow 求解器代理和自定义变形器进行模拟：

```cpp
// 来源: Public/GroomSolverComponent.h, Public/AddSolverDeformerNode.h

// 获取求解器代理，用于 Dataflow 模拟管线
FDataflowGroomSolverProxy* Proxy = 
    static_cast<FDataflowGroomSolverProxy*>(Solver->GetSimulationProxy());

// 绑定网格变形器（如 Optimus Deformer）
Solver->SetDeformerSolver(MyOptimusDeformer);

// 访问变形器实例
UMeshDeformerInstance* Instance = Solver->GetMeshDeformerInstance();

// 获取已注册的组件列表
const TSet<TObjectPtr<UGroomComponent>>& Grooms = Solver->GetGroomComponents();
const TMap<TObjectPtr<UMeshComponent>, int32>& Colliders = Solver->GetCollisionComponents();

// 读取求解器设置
const FGroomSolverSettings& Settings = Solver->GetSolverSettings();
// Settings.MaxLODDistance - 最大 LOD 距离
// Settings.CurveDynamicIndices - 动态曲线索引列表
// Settings.CurveKinematicIndices - 运动学曲线索引列表
// Settings.PointDynamicIndices - 动态点索引列表
```

## Demo 示例

### 自定义 Groom 求解器 Actor

```cpp
// AGroomSolverActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GroomSolverActor.h"

class AGroomSolverActor : public AActor
{
    GENERATED_BODY()

public:
    AGroomSolverActor();

    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UGroomSolverComponent> GroomSolver;

    /** 要添加到求解器的 Groom 组件列表 */
    UPROPERTY(EditAnywhere, Category = "Groom")
    TArray<TObjectPtr<UGroomComponent>> GroomsToSimulate;

    /** 碰撞网格组件 */
    UPROPERTY(EditAnywhere, Category = "Groom")
    TObjectPtr<UMeshComponent> CollisionMesh;

    UPROPERTY(EditAnywhere, Category = "Groom")
    int32 CollisionLODIndex = 0;
};
```

```cpp
// AGroomSolverActor.cpp
#include "AGroomSolverActor.h" // 实际应为你的头文件路径
#include "GroomSolverComponent.h"
#include "GroomComponent.h"

AGroomSolverActor::AGroomSolverActor()
{
    GroomSolver = CreateDefaultSubobject<UGroomSolverComponent>(TEXT("GroomSolver"));
    RootComponent = GroomSolver;
}

void AGroomSolverActor::BeginPlay()
{
    Super::BeginPlay();

    // 将所有 Groom 注册到求解器
    for (UGroomComponent* Groom : GroomsToSimulate)
    {
        if (Groom)
        {
            GroomSolver->AddGroomComponent(Groom);
        }
    }

    // 添加碰撞体
    if (CollisionMesh)
    {
        GroomSolver->AddCollisionComponent(CollisionMesh, CollisionLODIndex);
    }
}
```

## 模块依赖

HairStrands 插件跨模块依赖较复杂。HairStrandsSolver 模块的核心独特依赖如下：

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | 毛发核心数据结构（FStrandsPositionOutput 等） |
| `Dataflow` | Dataflow 框架（模拟节点、上下文、资产） |
| `DataflowEngine` | Dataflow 运行时引擎 |
| `GeometryCache` | 几何缓存系统 |
| `Chaos` | Chaos 物理求解器集成 |
| `ChaosSolverEngine` | Chaos 求解器事件接口 |
| `HairStrandsRuntime` | 毛发运行时数据 |
| `MeshDescription` | 网格描述（碰撞处理） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `aa770ac7` | Remove crash in mobile renderer when using groom binding. | 修复移动端渲染器使用毛发绑定时的崩溃 |
| 2026-05-26 | `3da4e98e` | Fix crash when selecting the addSolverDeformer dataflow node | 修复选择 addSolverDeformer 数据流节点时崩溃 |
| 2026-05-26 | `d2f5bcd4` | Fix crash when recompiling BP while playing groom in dataflow editor + fix bad number of vertices ca | 修复在数据流编辑器播放毛发时重编译蓝图的崩溃及顶点数错误 |
| 2026-05-22 | `9ce84766` | Remove the CreateGroomDataflowAsset from the context menu | 从右键菜单移除创建毛发数据流资产选项 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：优化客户端关联/解除关联通知的重复代码 |

### 维护评价

- **创建时间**：2020-11-24，UE5 早期即存在，约 6 年历史
- **活跃度**：近期（2026 年 5 月）仍有密集的 bug 修复和功能调整，属于**活跃维护**状态
- **当前状态**：多个崩溃修复表明该功能仍处于快速迭代阶段，Dataflow 集成是近期开发重点
- **注意事项**：默认未启用（`EnabledByDefault: false`），需在项目设置中手动开启
- **推荐度**：⭐⭐⭐⭐ 推荐使用。这是 UE5 官方毛发解决方案的核心组件，Epic 持续投入维护。对于需要毛发物理模拟的项目（影视级角色、数字人），这是唯一官方支持的完整方案。注意 Dataflow 相关功能仍在快速迭代，生产环境使用需关注版本稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/groom-system-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands/Tests)