# Zone Graph

> Description missing.

| 属性 | 值 |
|---|---|
| 中文名 | 区域图 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ZoneGraph` (Runtime), `ZoneGraphDebug` (Runtime), `ZoneGraphEditor` (Editor), `ZoneGraphTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph) | |

## 用途

ZoneGraph 是一个实验性的运行时系统，用于定义和查询游戏世界中的离散区域（Zone）以及它们之间的连接（Lane）关系。它解决的核心问题是**结构化、高性能地表示和查询游戏空间**，特别适用于需要对大规模开放世界进行导航、分区或逻辑划分的场景，例如 AI 移动、交通系统或区域化游戏逻辑。它提供了一种数据驱动的方式来构建世界空间图。

## 使用场景

- 你在制作一个大型开放世界游戏，需要为AI或载具定义复杂的道路和导航网络 → 使用 ZoneGraph 创建车道图。
- 你需要基于空间区域（如街区、房间、兴趣点）来触发游戏逻辑或AI行为 → 使用 ZoneGraph 定义并查询区域。
- 你需要一个高效的系统来管理世界分区，并在运行时快速查询某个点所在的区域及其连接信息 → 使用 ZoneGraph。
- 你希望可视化、编辑和调试复杂的区域网络 → 使用 ZoneGraph Editor 和 Debug 模块。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindNearestZone` | 在给定位置附近查找最近的区域。 | `UZoneGraphSubsystem` |
| `GetConnectedZones` | 获取与指定区域直接相连的所有区域。 | `UZoneGraphSubsystem` |
| `CalculatePath` | 计算两个区域之间的连接路径。 | `UZoneGraphSubsystem` |
| `GetZoneAtLocation` | 获取指定位置所在的区域。 | `UZoneGraphSubsystem` |
| `GetLaneData` | 获取特定连接（Lane）的详细数据。 | `UZoneGraphSubsystem` |

### 使用示例（蓝图描述）

1.  **查找并获取区域信息**：在你的角色蓝图中，使用 `GetGameInstance` 节点获取实例，然后调用 `GetSubsystem` 节点并选择 `ZoneGraphSubsystem`。将角色位置（`GetActorLocation`）连接到 `GetZoneAtLocation` 或 `FindNearestZone` 的输入，即可获得当前所在的 `FZoneHandle` 或最近区域的信息。
2.  **规划移动路径**：获取起点和终点的 `ZoneHandle` 后，将它们连接到 `CalculatePath` 节点。该节点会输出一个路径（`FZoneGraphPath`），其中包含一系列连续的区域和连接信息，可用来指导 AI 角色移动。

## C++ 用法

### 头文件引入

```cpp
#include "ZoneGraphSubsystem.h"
#include "ZoneGraphTypes.h"
#include "ZoneGraphQuery.h"
```

### 基本用法

```cpp
// 假设你已经通过编辑器或数据构建工具生成了一个 UZoneGraphAsset。
// 以下代码展示如何在运行时查询区域图。
void AMyActor::QueryZoneGraph()
{
    UWorld* World = GetWorld();
    if (!World) return;

    // 1. 获取 ZoneGraph 子系统
    UZoneGraphSubsystem* ZoneGraphSubsystem = World->GetSubsystem<UZoneGraphSubsystem>();
    if (!ZoneGraphSubsystem) return;

    // 2. 查找当前位置所在的区域
    FVector MyLocation = GetActorLocation();
    FZoneHandle CurrentZone = ZoneGraphSubsystem->GetZoneAtLocation(MyLocation);

    // 3. 获取该区域的数据
    if (CurrentZone.IsValid())
    {
        const FZoneData* ZoneData = ZoneGraphSubsystem->GetZoneData(CurrentZone);
        if (ZoneData)
        {
            UE_LOG(LogTemp, Log, TEXT("Current Zone Tag: %s"), *ZoneData->Tags.ToString());
        }
    }
}
```
*(基于 ZoneGraphSubsystem 的典型查询逻辑)*

### 进阶用法

```cpp
// 组合查询：找到当前位置的区域，然后查找一个特定标签的相邻区域。
void AMyActor::FindAdjacentSpecialZone()
{
    UZoneGraphSubsystem* ZoneGraphSubsystem = GetWorld()->GetSubsystem<UZoneGraphSubsystem>();
    if (!ZoneGraphSubsystem) return;

    FZoneHandle MyZone = ZoneGraphSubsystem->GetZoneAtLocation(GetActorLocation());
    if (!MyZone.IsValid()) return;

    // 获取所有连接的区域（邻居）
    TArray<FZoneHandle> ConnectedZones;
    ZoneGraphSubsystem->GetConnectedZones(MyZone, ConnectedZones);

    // 在邻居中查找带有特定标签的区域
    for (const FZoneHandle& Neighbor : ConnectedZones)
    {
        const FZoneData* NeighborData = ZoneGraphSubsystem->GetZoneData(Neighbor);
        if (NeighborData && NeighborData->Tags.HasTag(MySpecialTag))
        {
            UE_LOG(LogTemp, Log, TEXT("Found adjacent special zone!"));
            // ... 对找到的区域进行操作
            break;
        }
    }
}
```
*(展示了如何结合 GetZoneAtLocation、GetConnectedZones 和标签过滤进行组合查询)*

## Demo 示例

**ZoneGraphDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ZoneGraphDemo.generated.h"

UCLASS()
class AZoneGraphDemo : public AActor
{
    GENERATED_BODY()

public:
    AZoneGraphDemo();
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Demo")
    bool bRunQuery = true;

private:
    void RunBasicQuery() const;
};
```

**ZoneGraphDemo.cpp**
```cpp
#include "ZoneGraphDemo.h"
#include "ZoneGraphSubsystem.h"
#include "ZoneGraphTypes.h"

AZoneGraphDemo::AZoneGraphDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AZoneGraphDemo::BeginPlay()
{
    Super::BeginPlay();
    if (bRunQuery)
    {
        RunBasicQuery();
    }
}

void AZoneGraphDemo::RunBasicQuery() const
{
    UWorld* World = GetWorld();
    UZoneGraphSubsystem* ZoneGraphSubsystem = World->GetSubsystem<UZoneGraphSubsystem>();
    if (!ZoneGraphSubsystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("ZoneGraphSubsystem not found! Ensure the ZoneGraph plugin is enabled and a ZoneGraph asset is loaded."));
        return;
    }

    // 在 Actor 位置执行一次简单的区域查找
    FZoneHandle FoundZone = ZoneGraphSubsystem->GetZoneAtLocation(GetActorLocation());

    if (FoundZone.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("AZoneGraphDemo: Found a valid zone at my location."));
        // 此处可以进一步查询 FoundZone 的属性
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("AZoneGraphDemo: No zone found at my location."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ZoneGraph` | 核心运行时库，包含区域图数据的加载、查询和管理逻辑。 |
| `ZoneGraphDebug` | 运行时调试绘制工具，用于可视化区域图和连接。 |
| `ZoneGraphEditor` | 编辑器集成，提供区域图资产的编辑器和可视化工具。 |
| `ZoneGraphTestSuite` | 包含 ZoneGraph 功能的自动化测试用例。 |

**注意**：此插件的运行时模块 `ZoneGraph` 在其 Build.cs 中声明依赖 `EditorFramework` 和 `UnrealEd`，这是一个非常规的运行时依赖，可能表明它目前的设计或构建配置仍不完全成熟（与其“实验性”状态相符）。在独立的纯运行时游戏项目中使用时，可能需要审查或重构此依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 配合 Mass 模块重构，移动相关头文件位置。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 配合 Mass 模块重构，调整模块依赖。 |
| 2025-11-21 | `d1de0b8a` | Zone Graph: Add an extra FZoneDrawAnnotator parameter to be able to customize zone graph draw debugs | 为调试绘制增加了一个注解器参数，增强了自定义可视化能力。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 Base*.ini 重命名为 Default*.ini。 |

### 维护评价

ZoneGraph 插件仍处于**实验性**阶段（`IsExperimentalVersion=true`），且默认未启用。从提交历史看，近期的更新主要集中在配合引擎其他核心模块（如 Mass）的重构，以及基础的日志和配置改进，最后一次功能性更新在 2025 年底。这表明它**仍在维护中，但并非积极开发的核心功能**。作为一个实验性系统，它的 API 和内部实现可能发生变化。**建议在需要探索性项目或技术预研中使用**，不推荐直接用于需要长期稳定支持的商业项目生产环境。使用时需注意其对编辑器模块的依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph/Source/ZoneGraphTestSuite)