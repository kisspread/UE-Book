# MassAI

> AI-specific functionality extending MassGameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模AI |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI) | |

## 用途

`MassAI` 是 `MassGameplay` 框架的AI功能扩展插件。其核心目的是为海量实体（例如成百上千的NPC、生物或载具）提供高性能的AI功能，特别是导航与寻路。

它通过模块化设计，将传统AI（如行为树）的能力与ECS（实体组件系统）风格的MassEntity框架相结合，解决了在开放世界或大规模场景中同时运行大量AI代理的性能瓶颈和管理复杂性问题。默认不启用且标记为实验性，表明这是一个面向未来、仍在积极发展和测试中的高级AI系统。

## 使用场景

-   **开放世界游戏**：管理城市、森林或战场上成千上万NPC的群体移动、避障和寻路行为。
-   **即时战略游戏 (RTS)**：为大量作战单位提供高效、可预测的路径规划与编队移动。
-   **动态人群模拟**：在交通枢纽、体育场或商业街模拟大规模人流。
-   **基于ZoneGraph或NavMesh的复杂导航**：在利用`ZoneGraph`车道或传统`NavMesh`的大地图上进行高性能寻路。

## 蓝图用法

该插件的蓝图节点主要服务于**编辑器工具**和**调试**目的，用于在编辑器中测试导航功能。运行时AI逻辑通常通过其他Mass模块（如`MassAIBehavior`）的ECS处理器来驱动。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Pin Lane` | 将当前测试Actor所在的ZoneGraph车道固定，用于后续调试和可视化。 | `AMassNavigationTestingActor` |
| `Clear Pinned Lane` | 清除已固定的车道。 | `AMassNavigationTestingActor` |

### 使用示例（蓝图描述）

1.  在关卡编辑器中，放置一个 `AMassNavigationTestingActor`。
2.  在其 `Details` 面板中，调整 `Search Extent`、`Agent Radius`、`Goal Position` 等属性来定义测试的代理和目标。
3.  在编辑器中移动该Actor，使其位于`ZoneGraph`的车道附近。
4.  调用 `Pin Lane` 节点（可通过蓝图或Actor的按钮），锁定当前所在车道。
5.  观察调试绘制（Debug Draw）以查看路径计算结果和代理的预期移动轨迹。
6.  调用 `Clear Pinned Lane` 进行重置或测试其他位置。

## C++ 用法

`MassNavigationEditor` 模块主要用于编辑器扩展和调试可视化，不直接提供运行时API。运行时导航逻辑位于 `MassNavigation` 和 `MassZoneGraphNavigation` 等模块中。

### 头文件引入

```cpp
#include "MassNavigationEditorModule.h"
#include "MassNavigationTestingActor.h"
```

### 基本用法

该模块主要提供编辑器工具。以下是如何在C++中创建和操作一个导航测试Actor的示例。

*来源：`Private/MassNavigationTestingActor.h`*

```cpp
// 在编辑器工具或调试代码中
AMassNavigationTestingActor* TestActor = GetWorld()->SpawnActor<AMassNavigationTestingActor>();
if (TestActor)
{
    // 获取其测试组件并设置参数
    UMassNavigationTestingComponent* TestComp = TestActor->GetDebugComp();
    if (TestComp)
    {
        TestComp->SearchExtent = FVector(100.f, 100.f, 100.f);
        TestComp->AgentRadius = 50.f;
        TestComp->GoalPosition = FVector(1000.f, 500.f, 0.f);
        TestComp->UpdateTests(); // 触发路径计算和调试绘制更新
    }
}
```

### 进阶用法

通过继承 `UMassNavigationTestingComponent` 或 `AMassNavigationTestingActor`，可以创建自定义的导航测试工具，用于验证特定的导航场景或调试复杂的移动问题。需要重写 `CreateDebugSceneProxy` 和 `UpdateTests` 来实现自定义的可视化逻辑。

## Demo 示例

一个在编辑器插件中创建 `MassNavigationTestingActor` 并进行测试的最小示例。

```cpp
// MyEditorTool.h
#pragma once
#include "CoreMinimal.h"
#include "MassNavigationTestingActor.h"

class FMyEditorTool
{
public:
    void SpawnAndConfigureTestActor(UWorld* World);
    void RunNavigationTest(AMassNavigationTestingActor* TestActor);
};
```

```cpp
// MyEditorTool.cpp
#include "MyEditorTool.h"
#include "MassNavigationTestingComponent.h"

void FMyEditorTool::SpawnAndConfigureTestActor(UWorld* World)
{
    if (!World) return;

    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    AMassNavigationTestingActor* TestActor = World->SpawnActor<AMassNavigationTestingActor>(
        AMassNavigationTestingActor::StaticClass(),
        FVector::ZeroVector,
        FRotator::ZeroRotator,
        SpawnParams);

    if (TestActor)
    {
        // 配置测试属性
        UMassNavigationTestingComponent* DebugComp = TestActor->GetDebugComp();
        if (DebugComp)
       DebugComp->GoalPosition = FVector(500.f, 500.f, 0.f);
    }
}

void FMyEditorTool::RunNavigationTest(AMassNavigationTestingActor* TestActor)
{
    if (TestActor)
    {
        // 固定当前车道并更新测试可视化
        TestActor->PinLane();
    }
}
```

## 模块依赖

由于 `MassAI` 包含多个子模块，依赖关系因具体使用场景而异。

- **若仅使用运行时导航功能**：你的模块需依赖 `MassNavigation` 和 `MassZoneGraphNavigation`（或 `MassNavMeshNavigation`），它们通常还依赖 `MassGameplay` 和 `MassEntity`。
- **若使用编辑器调试工具**：你的编辑器模块需依赖 `MassNavigationEditor`。
- **若使用完整AI行为**：需依赖 `MassAIBehavior` 等其他运行时模块。

请参考具体子模块的 `Build.cs` 文件以获取确切依赖。无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 移除 INFINITY 的使用以修复最新 Windows SDK 上的编译错误。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量转换为浮点数产生的警告代码。 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | 修复 Mass 调试器在无效实体上运行的问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致乱码输出的问题。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | [倒带调试器] 更新。 |

### 维护评价

`MassAI` 插件创建于 2021 年，目前处于**活跃开发**阶段。从近期（2026年）的 commit 记录来看，团队持续在进行编译错误修复、警告清理和功能调试工作，表明该框架仍在被积极维护和改进。

然而，其 `.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这表示**这是一个实验性功能**，API和功能可能会发生重大变化，不建议在追求稳定性的商业项目中直接使用。它更适合作为技术预研或在可控范围内进行原型开发。

**建议**：如果你的项目需要处理大规模AI实体且对性能有极致要求，可以关注并试验此插件，但需做好应对未来API变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassAITestSuite)

---

# MassNavigationEditor

> Mass Navigation Editor module.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模导航编辑器 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MassNavigationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassNavigationEditor) | |

## 用途

`MassNavigationEditor` 是 `MassAI` 插件中的一个**编辑器工具模块**。它不提供运行时的AI功能，而是为开发者（特别是关卡设计师和技术美术）提供在虚幻编辑器内**测试、调试和可视化**大规模导航系统（特别是基于`ZoneGraph`的导航）的工具。

它解决的核心问题是：在传统的游戏运行时测试大量AI代理的导航行为既耗时又难以精确复现和观察。通过此模块，开发者可以在编辑器内即时放置测试代理，观察其路径计算、车道选择、避障预测等行为的可视化结果，从而高效地迭代和验证导航数据的正确性。

## 使用场景

-   **导航数据调试**：在编辑器中放置测试代理，检查其是否能够正确找到通往目标点的路径，路径是否平滑、是否经过预期的区域。
-   **ZoneGraph车道测试**：验证`ZoneGraph`的车道连接、标签过滤和属性是否设置正确，观察代理如何在不同车道间切换。
-   **性能预测**：虽然不在运行时，但可视化结果可以帮助判断复杂路径计算在运行时可能带来的开销。
-   **关卡设计反馈**：设计师可以实时看到导航代理将如何在他们设计的场景中移动，从而调整场景布局。

## 蓝图用法

该模块提供的蓝图节点主要绑定在测试Actor上，用于控制调试可视化。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Pin Lane` | 将当前测试Actor所在的ZoneGraph车道固定，用于后续调试和可视化。 | `AMassNavigationTestingActor` |
| `Clear Pinned Lane` | 清除已固定的车道。 | `AMassNavigationTestingActor` |

### 使用示例（蓝图描述）

1.  在关卡编辑器中，从放置Actor面板找到 `Mass Navigation Testing Actor` 并放置到场景中。
2.  选中该Actor，在 `Details` 面板中找到 `Default` 分类。
3.  调整 `Goal Position`（目标位置，可拖拽编辑器控件设置）和 `Search Extent`（搜索范围）等参数。
4.  移动Actor，使其位于`ZoneGraph`车道附近。
5.  点击 `Details` 面板 `Mass Navigation Testing` 分类下的 `Pin Lane` 按钮（此按钮对应蓝图节点）。
6.  观察场景中绘制的调试线：白色线为固定车道，彩色线为计算出的路径或代理预期轨迹。
7.  要重置，点击 `Clear Pinned Lane` 按钮。

## C++ 用法

该模块的API主要面向编辑器扩展开发，用于程序化地创建和控制测试实例。

### 头文件引入

```cpp
#include "MassNavigationTestingActor.h"
```

### 基本用法

以下示例展示如何在C++编辑器工具中实例化并配置一个导航测试Actor。

*来源：`Private/MassNavigationTestingActor.h`*

```cpp
// 在某个编辑器工具的函数中
void FMyEditorUtility::CreateNavigationTest(UWorld* InWorld, FVector TestLocation, FVector TestGoal)
{
    // 确保在编辑器世界中操作
    if (!InWorld || !InWorld->IsEditorWorld()) return;

    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    // 生成测试Actor
    AMassNavigationTestingActor* TestActor = InWorld->SpawnActor<AMassNavigationTestingActor>(
        TestLocation,
        FRotator::ZeroRotator,
        SpawnParams);

    if (TestActor)
    {
        // 获取其核心组件并进行配置
        UMassNavigationTestingComponent* TestComp = TestActor->GetDebugComp();
        if (TestComp)
        {
            TestComp->GoalPosition = TestGoal;
            TestComp->SearchExtent = FVector(200.f, 200.f, 200.f);
            TestComp->AgentRadius = 35.f;
            
            // 强制触发一次测试更新和绘制
            TestComp->UpdateTests();
            
            // (可选) 立即固定当前车道
            TestActor->PinLane();
        }
    }
}
```

### 进阶用法

通过监听 `UMassNavigationTestingComponent` 内部的委托（如 `OnZoneGraphDataChanged`），可以在导航数据（如`ZoneGraph`）发生变化时自动触发测试更新，实现动态调试环境。

```cpp
// 在自定义的测试组件中
void UMyCustomNavTestComponent::BeginPlay()
{
    Super::BeginPlay();
    
    // 监听ZoneGraph数据变化
    if (UZoneGraphSubsystem* ZGSubsystem = GetWorld()->GetSubsystem<UZoneGraphSubsystem>())
    {
        ZGSubsystem->OnZoneGraphDataChanged.AddUObject(this, &UMyCustomNavTestComponent::HandleZoneGraphChanged);
    }
}

void UMyCustomNavTestComponent::HandleZoneGraphChanged(const AZoneGraphData* ZoneGraphData)
{
    // 当世界中的ZoneGraph数据重建或变化时，重新运行测试
    UpdateTests();
}
```

## Demo 示例

一个完整的、可编译的编辑器工具类，用于一键创建和配置导航测试。

```cpp
// MassNavigationTestTool.h
#pragma once
#include "CoreMinimal.h"

class MASSNAVIGATIONEDITOR_API FMassNavigationTestTool
{
public:
    /** 在指定位置创建一个导航测试Actor，并面向给定的目标点。 */
    static AMassNavigationTestingActor* CreateTestActor(
        UWorld* World,
        const FVector& SpawnLocation,
        const FVector& GoalLocation,
        float AgentRadius = 40.f);
        
    /** 为给定的测试Actor随机设置一个附近的导航目标。 */
    static void RandomizeNearbyGoal(AMassNavigationTestingActor* TestActor, float Radius = 500.f);
};
```

```cpp
// MassNavigationTestTool.cpp
#include "MassNavigationTestTool.h"
#include "MassNavigationTestingActor.h"
#include "MassNavigationTestingComponent.h"
#include "NavigationSystem.h"

AMassNavigationTestingActor* FMassNavigationTestTool::CreateTestActor(
    UWorld* World,
    const FVector& SpawnLocation,
    const FVector& GoalLocation,
    float AgentRadius)
{
    if (!World) return nullptr;

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    
    AMassNavigationTestingActor* Actor = World->SpawnActor<AMassNavigationTestingActor>(SpawnLocation, FRotator::ZeroRotator, Params);
    if (Actor)
    {
        UMassNavigationTestingComponent* Comp = Actor->GetDebugComp();
        if (Comp)
        {
            Comp->GoalPosition = GoalLocation;
            Comp->AgentRadius = AgentRadius;
            Comp->UpdateTests(); // 初始化测试
        }
    }
    return Actor;
}

void FMassNavigationTestTool::RandomizeNearbyGoal(AMassNavigationTestingActor* TestActor, float Radius)
{
    if (!TestActor) return;
    UMassNavigationTestingComponent* Comp = TestActor->GetDebugComp();
    if (!Comp) return;
    
    const FVector Origin = TestActor->GetActorLocation();
    FVector RandomPoint;
    if (UNavigationSystemV1::K2_GetRandomReachablePointInRadius(GetWorld(), Origin, RandomPoint, Radius))
    {
        Comp->GoalPosition = RandomPoint;
        Comp->UpdateTests();
    }
}
```

## 模块依赖

该模块的依赖关系较为简单，主要用于编辑器功能。

| 模块 | 用途 |
|---|---|
| `MassNavigation` | 提供核心的导航功能和数据类型定义。 |
| `ZoneGraph` | 提供`ZoneGraph`车道和子系统的访问，用于基于车道的导航测试。 |

（注：根据提供的 `Build.cs` 片段，其还依赖 `EditorFramework` 和 `UnrealEd`，这些是常见编辑器依赖，按规范省略。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 修复编译错误，提升SDK兼容性。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 清理代码警告，提升代码规范性。 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | 修复调试器在无效实体上运行的Bug，提升调试工具稳定性。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复枚举格式化问题，改善调试信息可读性。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | 更新倒带调试器相关功能。 |

### 维护评价

`MassNavigationEditor` 作为 `MassAI` 的一部分，和主插件保持同步的活跃更新。近期的提交主要集中在**编译修复、代码警告清理和调试器Bug修复**上，这表明团队正在不断打磨这套实验性的工具链，使其更加稳定和可靠。

尽管如此，由于其宿主插件 `MassAI` 是实验性的，`MassNavigationEditor` 本身也应被视为**实验性工具**。它的API可能会随着底层MassEntity和MassGameplay框架的演进而改变。目前，它是学习和调试Mass导航系统不可或缺的工具，但在构建最终产品功能时，应谨慎依赖其具体实现细节。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassNavigationEditor)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassAITestSuite) (相关测试可能在MassAITestSuite中)