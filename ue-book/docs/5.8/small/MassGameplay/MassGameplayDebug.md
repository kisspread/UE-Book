# Mass Gameplay Debug

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | Mass 游戏调试模块 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（调试可视化蓝图资产） |
| 模块 | `MassGameplayDebug` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayDebug) | |

## 用途

MassGameplayDebug 是 MassGameplay 插件的调试可视化模块，为基于 MassEntity 框架的大规模实体模拟提供调试和可视化工具。该模块解决了在编辑器和运行时中观察、选择、检查成千上万个 Mass 实体的困难。

具体功能包括：

- **实体调试形状绘制**：通过 `UMassDebuggerSubsystem` 收集并绘制实体的调试形状（Box、Cone、Cylinder、Capsule）
- **实体选择与信息查看**：支持选中单个 Mass 实体并查看其详细信息
- **实例化静态网格调试可视化**：通过 ISM（InstancedStaticMeshComponent）以高性能方式渲染大量实体的调试网格
- **调试可视化 Trait 系统**：通过 `UMassDebugVisualizationTrait` 为实体模板附加调试可视化能力
- **LOD 友好的调试绘制**：提供线批处理器（`FLineBatcher`）封装，支持持久和临时调试绘制

该模块仅在 `WITH_MASSGAMEPLAY_DEBUG` 宏开启时生效，大部分功能受 `WITH_EDITORONLY_DATA` 保护，是一个面向开发阶段的诊断工具。

## 使用场景

- 你在开发一个大规模 NPC 模拟系统（如城市中的上千个行人），需要在编辑器中直观看到实体的分布和状态 → 用 MassGameplayDebug
- 你需要调试某个 Mass 实体的 Fragment 数据，想在视口中选中单个实体查看其详细信息 → 用 `UMassDebuggerSubsystem::SetSelectedEntity`
- 你为实体配置了不同类型的调试网格（不同颜色/形状），需要快速预览 → 用 `UMassDebugVisualizationTrait` + `FAgentDebugVisualization`
- 你需要在运行时为 Mass 实体绘制调试形状（方向箭头、包围盒等）→ 用 `UE::Mass::Debug::FLineBatcher`

## 蓝图用法

该模块主要面向 C++ 和编辑器配置，直接的 BlueprintCallable 节点较少。核心用法通过 **Entity Trait** 系统暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Debug Visualization` (Trait) | 为实体模板添加调试可视化，配置网格、材质、剔除距离等 | `UMassDebugVisualizationTrait` |

### 使用示例（蓝图描述）

1. **配置实体调试可视化**：在 Mass Entity 配置资产中，添加 `Debug Visualization` Trait。在细节面板中设置：
   - **Mesh**：指定用于调试显示的静态网格资产
   - **Material Override**：可选的材质覆盖
   - **VisualNearCullDistance / VisualFarCullDistance**：配置近/远剔除距离（默认 5000/7500）
   - **WireShape**：如果未设置 Mesh，则使用此线框形状（Box/Cone/Cylinder/Capsule）

2. **调试数据表配置**：通过 `FAgentDebugVisualization` 数据表行，可在 DataTable 中集中管理多种 Agent 类型的调试外观，方便批量切换。

## C++ 用法

### 头文件引入

```cpp
#include "MassDebuggerSubsystem.h"
#include "MassDebugDrawHelpers.h"
#include "MassDebugVisualizationComponent.h"
```

### 基本用法 — 调试形状绘制

```cpp
// 通过 World 子系统获取调试器
UMassDebuggerSubsystem* Debugger = GetWorld()->GetSubsystem<UMassDebuggerSubsystem>();

// 检查是否正在收集数据（仅在调试类别启用时）
if (Debugger && Debugger->IsCollectingData())
{
    // 添加调试形状
    Debugger->AddShape(EMassEntityDebugShape::Box, EntityLocation, 50.f);
    Debugger->AddShape(EMassEntityDebugShape::Cone, EntityForwardPos, 100.f);
    
    // 通知数据收集完成
    Debugger->DataCollected();
}
```

### 基本用法 — 实体选择与信息查看

```cpp
// 选中一个 Mass 实体（通常由处理器或编辑器交互触发）
FMassEntityHandle TargetEntity = /* ... */;
Debugger->SetSelectedEntity(TargetEntity);

// 追加选中实体的调试信息
Debugger->AppendSelectedEntityInfo(FString::Printf(TEXT("Health: %.1f"), HealthValue));
Debugger->AppendSelectedEntityInfo(FString::Printf(TEXT("State: %s"), *StateName));

// 读取选中实体信息
const FMassEntityHandle& Selected = Debugger->GetSelectedEntity();
const FString& Info = Debugger->GetSelectedEntityInfo();
```

*来源：`Public/MassDebuggerSubsystem.h`*

### 基本用法 — 调试形状遍历

```cpp
// 遍历特定类型的所有调试形状
Debugger->ForEachShape(EMassEntityDebugShape::Box, [](const UMassDebuggerSubsystem::FShapeDesc& Shape)
{
    UE_LOG(LogTemp, Log, TEXT("Box at %s, size: %.1f"), *Shape.Location.ToString(), Shape.Size);
});
```

*来源：`Public/MassDebuggerSubsystem.h` — `ForEachShape` 方法*

### 进阶用法 — 线批处理器绘制

```cpp
#include "MassDebugDrawHelpers.h"

void DrawAgentDebug(const UWorld* World, const FVector& Location, const FVector& Forward)
{
    // 创建线批处理器（非持久，帧内有效）
    UE::Mass::Debug::FLineBatcher Batcher = 
        UE::Mass::Debug::FLineBatcher::MakeLineBatcher(World, /*bPersistentLines=*/false, /*LifeTime=*/-1.f);

    // 绘制实心包围盒
    Batcher.DrawSolidBox(Location, FVector(50.f, 50.f, 100.f), FColor::Green);

    // 绘制线框包围盒
    Batcher.DrawWireBox(Location, FVector(60.f, 60.f, 110.f), FColor::Yellow);

    // 绘制球体
    Batcher.DrawSphere(Location + FVector(0, 0, 150.f), 30.f, FLinearColor::Red);

    // 绘制方向箭头
    FTransform ArrowTransform(FRotationMatrix::MakeFromX(Forward).ToQuat(), Location);
    Batcher.DrawArrow(ArrowTransform, 200.f, FColor::Cyan);

    // 持久绘制（生命周期 5 秒）
    UE::Mass::Debug::FLineBatcher PersistentBatcher = 
        UE::Mass::Debug::FLineBatcher::MakeLineBatcher(World, false, 5.0f);
    PersistentBatcher.DrawSphere(Location, 50.f, FLinearColor::Green);
}
```

*来源：`Public/MassDebugDrawHelpers.h`*

### 进阶用法 — 自定义调试可视化处理器

```cpp
// 继承 UMassProcessor 实现自定义调试数据收集
UCLASS()
class UMyCustomDebugProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyCustomDebugProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

    FMassEntityQuery EntityQuery;
};

UMyCustomDebugProcessor::UMyCustomDebugProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EMassProcessingPhase::PostPhysics; // 在后物理阶段执行
}

void UMyCustomDebugProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddTagRequirement<FMassDebuggableTag>(EMassFragmentPresence::All);
    EntityQuery.RegisterWithProcessor(*this);
}

void UMyCustomDebugProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    UMassDebuggerSubsystem* Debugger = GetWorld()->GetSubsystem<UMassDebuggerSubsystem>();
    if (!Debugger || !Debugger->IsCollectingData()) return;

    EntityQuery.ForEachEntityChunk(EntityManager, Context, 
        [Debugger](FMassExecutionContext& ExecContext)
        {
            const int32 NumEntities = ExecContext.GetNumEntities();
            const TConstArrayView<FTransformFragment> Transforms = 
                ExecContext.GetFragmentView<FTransformFragment>();

            for (int32 i = 0; i < NumEntities; ++i)
            {
                Debugger->AddShape(EMassEntityDebugShape::Sphere, 
                    Transforms[i].GetTransform().GetLocation(), 25.f);
            }
        });

    Debugger->DataCollected();
}
```

*来源：`Public/DebugVisLocationProcessor.h` 及 `Public/MassDebuggerSubsystem.h`*

## Demo 示例

```cpp
// MyMassDebugExample.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "MassDebuggerSubsystem.h"
#include "MassDebugDrawHelpers.h"
#include "MassEntityTypes.h"
#include "MyMassDebugExample.generated.h"

UCLASS()
class UMyMassDebugExampleSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    // 在每帧末尾绘制所有活跃实体的调试信息
    UFUNCTION(BlueprintCallable, Category = "Mass|Debug")
    void DrawEntityDebugOverlay(const TArray<FVector>& EntityLocations, 
                                 const TArray<float>& EntityRadii)
    {
        UWorld* World = GetWorld();
        if (!World) return;

        // 持续 0.1 秒的调试绘制
        UE::Mass::Debug::FLineBatcher Batcher = 
            UE::Mass::Debug::FLineBatcher::MakeLineBatcher(World, false, 0.1f);

        for (int32 i = 0; i < EntityLocations.Num(); ++i)
        {
            const FVector& Loc = EntityLocations[i];
            const float Radius = (i < EntityRadii.Num()) ? EntityRadii[i] : 50.f;

            // 每个实体画一个绿色球体
            Batcher.DrawSphere(Loc, Radius, FLinearColor::Green);
        }
    }

    // 使用调试子系统选中实体并附加信息
    UFUNCTION(BlueprintCallable, Category = "Mass|Debug")
    void DebugSelectEntity(const FMassEntityHandle& Entity, const FString& DebugInfo)
    {
        UMassDebuggerSubsystem* Debugger = GetWorld()->GetSubsystem<UMassDebuggerSubsystem>();
        if (!Debugger) return;

        Debugger->SetSelectedEntity(Entity);
        Debugger->AppendSelectedEntityInfo(DebugInfo);
    }

    // 清除所有调试形状
    UFUNCTION(BlueprintCallable, Category = "Mass|Debug")
    void ClearDebugShapes()
    {
        UMassDebuggerSubsystem* Debugger = GetWorld()->GetSubsystem<UMassDebuggerSubsystem>();
        if (Debugger)
        {
            Debugger->ResetDebugShapes();
        }
    }
};
```

## 模块依赖

MassGameplayDebug 的 Build.cs 声明了以下非常见依赖：

| 模块 | 用途 |
|---|---|
| `MassEntityEditor` | Mass 实体编辑器支持，用于编辑器内调试可视化 |

注：该模块还隐式依赖 MassGameplay 插件中的其他模块（如 `MassCommon`、`MassRepresentation`），因为同属一个插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚 MassAgentComponent 的先前改动 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | ISM 切换前等待 Actor 就绪，修复视觉闪烁 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复 Mass 人群中非木偶 Actor 的处理问题 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path | 修复 LOD 计算器逐查看器路径中的一系列已有 bug |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | 将手动计算的 Actor 保留逻辑迁移为使用新的 UE::M API |

### 维护评价

**MassGameplayDebug** 作为 MassGameplay 插件的调试子模块，随父插件一同维护。

- **创建时间**：2021-09-29，约 5 年历史
- **最近更新**：近期（2026-05）仍有关联的 Representation/LOD 模块修复，说明整体 Mass 体系仍在积极开发
- **实验性状态**：标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，属于实验性质
- **活跃程度**：MassGameplayDebug 模块本身相对稳定，近期更新集中在 Representation 和 LOD 等核心模块

⚠️ **注意**：该模块标记为实验性，API 可能在未来版本中发生变化。`GetShapes()` 方法已在 5.8 版本标记为 `UE_DEPRECATED`，推荐使用 `ForEachShape` 替代。建议在生产项目中谨慎使用，并做好 API 变更的准备。

**推荐**：适用于需要调试大规模 Mass 实体模拟的开发阶段，不建议在最终发布构建中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayDebug)
- [父插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [MassEntity 核心模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassEntity)