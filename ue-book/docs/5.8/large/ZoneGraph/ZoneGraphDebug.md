# Zone Graph

> Description missing.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 区域图 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ZoneGraph` (Runtime), `ZoneGraphDebug` (Runtime), `ZoneGraphEditor` (Editor), `ZoneGraphTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph) | |

## 用途

ZoneGraph 插件提供了一个高性能的、基于区域的导航图（Zone Graph）数据结构和查询系统。它旨在解决在大型、复杂场景中进行高效AI寻路和空间查询的问题。与传统的导航网格（NavMesh）不同，ZoneGraph 通常由设计师或程序化工具预定义和构建，将世界划分为具有特定语义（如道路、人行道、建筑内部）的连通区域（Zone）和路径（Lane）。AI代理（如NPC、车辆）可以基于这些预定义的“车道”进行精确、可控的导航，并支持复杂的车道变换、优先级和标签过滤，使其特别适用于模拟交通系统、城市环境导航等需要高保真度和可控性的场景。

## 使用场景

- **开放世界游戏交通模拟**：为车辆和行人NPC创建逼真的、遵循交通规则的行驶和行走路径。
- **城市环境AI寻路**：NPC在复杂的街区、建筑内外进行导航，支持不同的移动方式（行走、驾驶）。
- **精确的路径规划**：当需要AI严格遵循特定路线（如巡逻路线、固定班车路线）时，替代通用的寻路网格。
- **复杂空间查询**：在具有多层结构（如立交桥、室内）的场景中，进行基于标签的、精确的空间位置查询。

## 蓝图用法

该插件主要提供用于测试和调试的蓝图节点，核心功能通常通过C++接口访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableCustomTests` | 启用对自定义测试（`UZoneLaneTest`）的通知，当测试Actor的车道位置更新时，会调用它们的回调。 | `UZoneGraphTestingComponent`, `AZoneGraphTestingActor` |
| `DisableCustomTests` | 禁用自定义测试通知。当前活动的测试将收到一个无效的位置更新。 | `UZoneGraphTestingComponent`, `AZoneGraphTestingActor` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `AZoneGraphTestingActor`。
2.  在其细节面板中，配置 `UZoneGraphTestingComponent` 的属性，如 `SearchExtent`（搜索范围）、`AdvanceDistance`（推进距离）和 `QueryFilter`（查询过滤器）。
3.  创建一个继承自 `UZoneLaneTest` 的蓝图类，覆盖 `OnLaneLocationUpdated` 事件以实现自定义测试逻辑（例如绘制调试信息）。
4.  将自定义测试蓝图实例添加到 `TestingComponent` 的 `CustomTests` 数组中。
5.  通过蓝图调用 `EnableCustomTests` 来激活测试。当Actor在世界中移动时，自定义测试将会收到车道位置更新的通知。

## C++ 用法

ZoneGraph的核心API通过 `UZoneGraphSubsystem` 提供。`ZoneGraphDebug` 模块主要用于开发时的调试和测试可视化。

### 头文件引入

```cpp
#include "ZoneGraphTestingActor.h"
#include "ZoneGraphSubsystem.h"
```

### 基本用法：实现自定义车道测试

可以继承 `UZoneLaneTest` 来创建自定义的测试逻辑，用于调试或扩展功能。

```cpp
// 来自 Public/ZoneGraphTestingActor.h 中 UZoneLaneTest 的定义
UCLASS()
class UMyCustomLaneTest : public UZoneLaneTest
{
    GENERATED_BODY()

public:
    // 当测试组件所在的车道位置更新时被调用
    virtual void OnLaneLocationUpdated(const FZoneGraphLaneLocation& PrevLaneLocation, const FZoneGraphLaneLocation& NextLaneLocation) override
    {
        // 此处可以访问当前和下一帧的车道位置信息
        // 例如，打印当前车道的标签或进行自定义逻辑判断
        UE_LOG(LogTemp, Log, TEXT("Lane Updated: From %s to %s"), *PrevLaneLocation.LaneHandle.ToString(), *NextLaneLocation.LaneHandle.ToString());
    }

    // 用于绘制自定义的调试可视化信息
    virtual void Draw(FPrimitiveDrawInterface* PDI) const override
    {
        // 使用PDI绘制线段、点等调试形状
        if (PDI && GetOwner())
        {
            const FZoneGraphLaneLocation& CurrentLocation = GetOwner()->LaneLocation;
            if (CurrentLocation.IsValid())
            {
                PDI->DrawPoint(CurrentLocation.Position, FColor::Green, 10.f, SDPG_Foreground);
            }
        }
    }
};
```

### 进阶用法：从组件获取图数据存储

可以通过测试组件来获取底层的 `FZoneGraphStorage`，用于更底层的查询。

```cpp
// 在拥有 UZoneGraphTestingComponent 的 Actor 或逻辑中
if (ZoneGraphTestingComp)
{
    const FZoneGraphLaneHandle SomeLaneHandle = /* ... 获取一个句柄 ... */;
    const FZoneGraphStorage* Storage = ZoneGraphTestingComp->GetZoneGraphStorage(SomeLaneHandle);
    if (Storage)
    {
        // 现在可以使用 Storage 指针进行底层数据访问
        // 例如访问车道、区域的具体属性
    }
}
```

## Demo 示例

以下是一个最小化的C++示例，展示如何创建一个自定义测试类并在测试组件中使用。

### MyZoneGraphTest.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "ZoneGraphTestingActor.h"
#include "MyZoneGraphTest.generated.h"

UCLASS()
class MYPROJECT_API UMyZoneGraphTest : public UZoneLaneTest
{
	GENERATED_BODY()

public:
	virtual void OnLaneLocationUpdated(const FZoneGraphLaneLocation& PrevLaneLocation, const FZoneGraphLaneLocation& NextLaneLocation) override;
	virtual void Draw(FPrimitiveDrawInterface* PDI) const override;

private:
	// 记录上一帧的位置用于绘制轨迹
	FVector LastPosition = FVector::ZeroVector;
};
```

### MyZoneGraphTest.cpp
```cpp
#include "MyZoneGraphTest.h"
#include "ZoneGraphTestingComponent.h"

void UMyZoneGraphTest::OnLaneLocationUpdated(const FZoneGraphLaneLocation& PrevLaneLocation, const FZoneGraphLaneLocation& NextLaneLocation)
{
	// 存储新位置用于绘制
	if (const UZoneGraphTestingComponent* Owner = GetOwner())
	{
		LastPosition = Owner->LaneLocation.Position;
	}
}

void UMyZoneGraphTest::Draw(FPrimitiveDrawInterface* PDI) const
{
	if (!PDI) return;

	// 从当前位置向前绘制一条黄色射线，表示朝向
	const UZoneGraphTestingComponent* Owner = GetOwner();
	if (Owner && Owner->LaneLocation.IsValid())
	{
		const FVector Start = Owner->LaneLocation.Position;
		const FVector End = Start + Owner->LaneLocation.Direction * 200.f;
		PDI->DrawLine(Start, End, FColor::Yellow, SDPG_Foreground, 2.0f);
	}

	// 如果存在上一帧的位置，绘制一条灰色线表示轨迹
	if (!LastPosition.IsZero())
	{
		const UZoneGraphTestingComponent* Owner = GetOwner();
		if (Owner)
		{
			PDI->DrawLine(LastPosition, Owner->LaneLocation.Position, FColor(128, 128, 128), SDPG_Foreground, 1.0f);
		}
	}
}
```

**使用方式**：
1.  编译上述代码。
2.  在编辑器中放置 `AZoneGraphTestingActor`。
3.  在 `UZoneGraphTestingComponent` 的 `CustomTests` 数组中添加一个 `UMyZoneGraphTest` 的实例。
4.  移动Actor，即可在视口中看到绘制的朝向射线和轨迹线。

## 模块依赖

根据提供的模块信息，`ZoneGraphDebug` 模块依赖 `EditorFramework` 和 `UnrealEd`，这表明它主要用于编辑器内的调试和测试可视化功能。使用该插件核心的运行时寻路功能，主要依赖 `ZoneGraph` 核心模块本身。对于插件使用者，通常无需在自己的 `Build.cs` 中显式添加这些特殊依赖，除非你需要扩展或调试 ZoneGraph 系统本身。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | MassCore 模块重构，移动头文件位置。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 中提取 MassCore 模块。 |
| 2025-11-21 | `d1de0b8a` | Zone Graph: Add an extra FZoneDrawAnnotator parameter to be able to customize zone graph draw debugs | 为区域图调试绘制添加自定义注释器参数。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件命名规范更新。 |

### 维护评价

-   **状态**：**维护不活跃，实验性**。
-   **分析**：ZoneGraph 插件创建于2021年底，至今已近5年，被标记为实验性且默认不启用。从近期更新日志看，最近一次与ZoneGraph功能直接相关的实质性更新在2025年11月。2026年的更新均为UE引擎大规模重构（如Mass模块拆分）或日志系统更新带来的被动修改，而非针对ZoneGraph功能本身的积极开发或问题修复。
-   **建议**：鉴于其**实验性**标签和长期缺乏实质性功能更新，不建议在正式生产项目中重度依赖此插件。它更适合作为一个**技术预览或内部研究工具**，用于探索基于区域的导航方案。对于关键的AI导航需求，目前仍然推荐使用官方长期维护的 Navigation Mesh (NavMesh) 系统。如果项目需要此插件特有的功能，使用者必须准备好自行进行深度定制和问题排查。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph)
- [官方文档]( )（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph/Source/ZoneGraphTestSuite)