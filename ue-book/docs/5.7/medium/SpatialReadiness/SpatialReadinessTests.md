# SpatialReadiness

> A plugin for managing spatial readiness of physics objects, enabling efficient spatial queries and synchronization with Chaos physics.

| 属性 | 值 |
|---|---|
| 中文名 | 空间就绪度 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SpatialReadiness` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025‑07‑21 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SpatialReadiness) | |

## 用途

SpatialReadiness 是一个实验性插件，用于优化 Chaos 物理引擎中的空间查询性能。它允许开发者显式标记场景中的物体（如刚体）为“就绪”状态，从而让引擎更高效地管理物理查询（如射线检测、碰撞过滤）。通过引入“冻结体”排序和空间就绪度切换，该插件可以减少物理场景中不必要的碰撞计算，特别适用于需要大量动态物体交互的大型开放世界或模拟场景。

该插件的核心机制包括：
- 控制物理物体的空间就绪性，避免每次查询都扫描所有物体。
- 提供调试工具（如排序冻结体列表、周期统计）以分析性能成本。
- 通过 Console Variable（CVar）在运行时动态启用/禁用，便于性能调优。

## 使用场景

- **大型开放世界**：你需要处理成千上万个动态物体（如 debris、载具碎片），希望只对“就绪”的物体进行碰撞检测，减少无效计算。
- **物理沙盒测试**：在 Standalone 模式下运行物理模拟，通过开启空间就绪度来验证物体交互的正确性与性能。
- **碰撞过滤优化**：配合 ChaosUserDataPT 插件，对特定碰撞通道做更精细的过滤，避免全局重算。
- **性能分析**：使用内置的周期统计（cycle stats）定位物理查询中的热点代码。

## 蓝图用法

目前插件公开的蓝图可调用接口较少，主要面向 C++ 开发。以下是从源码中可识别的可能蓝图节点（需确认）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSpatialReadiness` | 设置指定 Actor 或组件的空间就绪状态 | `USpatialReadinessSubsystem` （假设） |
| `GetSpatialReadiness` | 查询当前空间就绪状态 | `USpatialReadinessSubsystem` （假设） |
| `IsSpatialReadinessEnabled` | 检查插件是否全局启用 | `USpatialReadinessSubsystem` （假设） |

> **注意**：这些节点名称根据插件功能推断，实际 API 请查阅插件头文件或官方文档。

### 使用示例（蓝图描述）

1. **启用空间就绪度**：在游戏开始时，调用 `SetSpatialReadiness Enabled` 或使用 CVar（Console Variable）`spatialreadiness.Enable 1`。
2. **标记物体就绪**：对于需要参与精确碰撞检测的物体（如玩家控制的车辆），通过 `SetSpatialReadiness(TargetActor, true)` 将其设为就绪。
3. **性能调试**：在 PlayerController 中，通过 `GetSpatialReadiness` 检查状态，并配合 `PrintString` 输出当前是否启用。

## C++ 用法

### 头文件引入

```cpp
#include "SpatialReadinessSubsystem.h"   // 假定文件名
#include "SpatialReadinessStatics.h"     // 假定工具类
```

### 基本用法

```cpp
// 获取子系统
USpatialReadinessSubsystem* ReadinessSystem = GEngine->GetEngineSubsystem<USpatialReadinessSubsystem>();
if (ReadinessSystem)
{
    // 启用空间就绪度（通常通过 CVar 控制）
    IConsoleManager::Get().FindConsoleVariable(TEXT("spatialreadiness.Enable"))->Set(1);

    // 标记一个 PrimitiveComponent 为就绪
    UPrimitiveComponent* Comp = ...;
    ReadinessSystem->MarkReadiness(Comp, ESpatialReadinessState::Ready);
}
```

**来源文件**：`Engine/Plugins/Experimental/SpatialReadiness/Source/SpatialReadiness/Private/SpatialReadinessSubsystem.cpp`（假设）

### 进阶用法

从测试用例（`SpatialReadinessTests`）可提取以下模式：

```cpp
// 创建一个测试场景
UWorld* World = FAutomationTestBase::GetWorld();
AActor* TestActor = World->SpawnActor<AActor>();
UPrimitiveComponent* TestComp = ...;

// 设置空间就绪状态
USpatialReadinessSubsystem* Subsys = World->GetSubsystem<USpatialReadinessSubsystem>();
Subsys->SetReadiness(TestComp, true);

// 验证：模拟物理查询，检查是否只包含就绪物体
TArray<FOverlapResult> Results;
World->OverlapMultiByChannel(Results, ...);
// 断言 Results 只包含 TestComp 或其他就绪组件
```

更完整的测试案例请参阅 `Engine/Plugins/Experimental/SpatialReadiness/Tests` 目录。

## Demo 示例

由于插件尚处于早期实验阶段，没有提供完整的 Demo 资源。以下是一个最小化的 C++ 示例，展示如何在游戏模块中集成空间就绪度。

### MyReadinessActor.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyReadinessActor.generated.h"

UCLASS(Blueprintable)
class AMyReadinessActor : public AActor
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "SpatialReadiness")
    void EnableReadiness(bool bEnable);

    UPROPERTY()
    UPrimitiveComponent* PhysComp;
};
```

### MyReadinessActor.cpp

```cpp
#include "MyReadinessActor.h"
#include "SpatialReadinessSubsystem.h"

void AMyReadinessActor::EnableReadiness(bool bEnable)
{
    if (USpatialReadinessSubsystem* Subsys = GetWorld()->GetSubsystem<USpatialReadinessSubsystem>())
    {
        Subsys->SetReadiness(PhysComp, bEnable);
    }
}
```

> 注意：上述代码基于假设的 API，实际接口可能不同。请参考插件源码调整。

## 模块依赖

本插件依赖 `ChaosUserDataPT` 和常见标准模块。在你的项目 `Build.cs` 中添加：

| 模块 | 用途 |
|---|---|
| `ChaosUserDataPT` | 提供 Chaos 物理线程的用户数据扩展，用于空间就绪标记的底层数据传递 |

其他依赖均为引擎标准模块（如 `Core`, `Engine`, `Chaos`），无需额外声明。

## 维护状态

### 近期更新

```
- 2025-08-01 8579b7cd — Allow spatial readiness to be enabled in Standalone mode, for testing in the physics sandbox
- 2025-07-30 54ad2e53 — Sort list of frozen bodies in spatial readiness debug print
- 2025-07-28 a41f6737 — Collision Filter Refactor Part 2
- 2025-07-25 68072e32 — Add more cycle stats to spatial readiness to isolate cost of debug code
- 2025-07-21 c2eeb0e8 — Juno-specific cvar for spatial readiness toggle, and analytics
```

### 维护评价

- **创建时间**：2025‑07‑21，仅数周。
- **近期更新**：截止 2025‑08‑01 仍在活跃开发，每次提交均为功能性改进（Standalone 支持、排序优化、性能统计、重构等）。
- **活跃状态**：更新频繁，属于**活跃维护**阶段。
- **已知限制**：作为实验性插件，API 可能不稳定，且默认不启用。其目的是为特定项目（Juno）优化，通用性待验证。
- **推荐度**：如果你正在开发基于 Chaos 的大型开放世界项目，并面临物理查询性能瓶颈，可以尝试启用并测试。但对于小型或标准项目不建议冒险引入实验功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SpatialReadiness)
- [官方文档](https://docs.unrealengine.com/5.7/Plugins/SpatialReadiness)（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SpatialReadiness/Tests)