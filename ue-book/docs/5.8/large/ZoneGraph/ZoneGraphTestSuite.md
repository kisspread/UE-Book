# Zone Graph

> Description missing.

| 属性 | 值 |
|---|---|
| 中文名 | 区域图系统 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ZoneGraph` (Runtime), `ZoneGraphEditor` (Editor), `ZoneGraphTestSuite` (UncookedOnly), `ZoneGraphDebug` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph) | |

## 用途
ZoneGraph 是一个基于区域的、可配置的 AI 导航和查询系统。它通过定义由 **区域 (Zone)**、**车道 (Lane)** 和它们之间的连接组成的图结构，为 AI 代理提供环境认知和路径查询能力。与传统的 NavMesh 寻路不同，ZoneGraph 更侧重于构建一个结构化的、可供查询的空间表示，适用于复杂的环境（如城市街道、室内布局），能够为 AI 提供车道级别的精确引导和基于规则的移动约束。

## 使用场景
- 你需要为开放世界游戏模拟城市交通流，让车辆遵守车道规则并进行合理变道。
- 你需要在复杂的室内场景（如办公室、商场）中为机器人或 NPC 提供精确的、基于路线的导航。
- 你的 AI 系统需要查询“在当前位置前方200米处是否有路口”或“从当前位置到目标点最合理的车道路径是什么”这类结构化问题。
- 你希望构建一个可编辑、可视化的区域化 AI 导航方案，而不是依赖一个黑盒的导航网格。

## 蓝图用法
ZoneGraph 核心模块主要面向 C++ 使用，但其调试和查询功能可通过蓝图暴露。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Line Trace` | 沿指定方向进行射线检测，返回与 ZoneGraph 车道的相交信息。 | `UZoneGraphQuery` |
| `Find Nearest Lane` | 查找离给定位置最近的车道片段。 | `UZoneGraphQuery` |
| `Find Overlapping Lanes` | 查找与指定形状（如盒体、胶囊体）重叠的所有车道。 | `UZoneGraphQuery` |

*注：以上节点为根据系统功能推测，具体函数名需查阅引擎源码中的 `UFUNCTION(BlueprintCallable)` 定义。*

### 使用示例（蓝图描述）
1.  在你的 AI 蓝图中，添加一个 `ZoneGraph Query` 组件。
2.  使用 “Find Nearest Lane” 节点，输入 AI 当前位置，获取其所在的车道信息（`FZoneGraphLaneHandle`）。
3.  利用车道句柄，通过 “Get Lane Points” 等节点获取路径点，指导 AI 移动。
4.  使用 “Line Trace” 节点判断前方是否有可通行的路口或障碍。

## C++ 用法
核心使用涉及创建和查询 `ZoneGraph` 数据。

### 头文件引入
```cpp
#include "ZoneGraphQuery.h"
#include "ZoneGraphData.h"
#include "ZoneGraphTypes.h"
```

### 基本用法
查询最近的车道。
```cpp
// 来源：基于 ZoneGraph 核心查询功能
FZoneGraphLaneLocation LaneLocation;
FZoneGraphLaneHandle LaneHandle;
float Distance;

// 查询世界中 ZoneGraphData 的寻址方式需根据实际情况确定
UZoneGraphSubsystem* ZoneGraphSubsystem = GetWorld()->GetSubsystem<UZoneGraphSubsystem>();
if (ZoneGraphSubsystem)
{
    // 查找离 MyActor 位置最近的车道
    if (ZoneGraphSubsystem->FindNearestLane(MyActor->GetActorLocation(), /*SearchRadius=*/ 100.0f, LaneLocation, LaneHandle, Distance))
    {
        // 成功找到，LaneLocation 包含精确的车道位置信息
        // LaneHandle 可用于后续对该车道的查询
    }
}
```

### 进阶用法
进行射线检测，判断前方路口情况。
```cpp
// 来源：基于 ZoneGraphQuery 功能
FVector Start = MyActor->GetActorLocation();
FVector End = Start + MyActor->GetActorForwardVector() * 500.0f;
FZoneGraphLaneLocation HitLocation;
FZoneGraphLaneHandle HitLane;

// 沿射线方向检测车道
if (ZoneGraphSubsystem->LineTrace(Start, End, HitLocation, HitLane))
{
    // 检测到前方有车道，HitLocation 包含精确碰撞点信息
    // 可据此判断路口、变道机会等
}
```

## Demo 示例
一个最小的 C++ 类，演示如何获取当前世界的 ZoneGraph 子系统。
```cpp
// MyZoneGraphUser.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyZoneGraphUser.generated.h"

UCLASS()
class MYPROJECT_API AMyZoneGraphUser : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void QueryNearestLane();

private:
    UPROPERTY()
    class UZoneGraphSubsystem* CachedZoneGraphSubsystem;
};

// MyZoneGraphUser.cpp
#include "MyZoneGraphUser.h"
#include "ZoneGraphSubsystem.h"
#include "ZoneGraphTypes.h"

void AMyZoneGraphUser::BeginPlay()
{
    Super::BeginPlay();
    CachedZoneGraphSubsystem = GetWorld()->GetSubsystem<UZoneGraphSubsystem>();
}

void AMyZoneGraphUser::QueryNearestLane()
{
    if (!CachedZoneGraphSubsystem) return;

    FZoneGraphLaneLocation OutLocation;
    FZoneGraphLaneHandle OutLane;
    float OutDistance;

    if (CachedZoneGraphSubsystem->FindNearestLane(GetActorLocation(), 200.0f, OutLocation, OutLane, OutDistance))
    {
        UE_LOG(LogTemp, Log, TEXT("Found lane with ID: %s, Distance: %f"), *OutLane.ToString(), OutDistance);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No lane found nearby."));
    }
}
```

## 模块依赖
无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 将 MassCore 头文件移动到 Public/Mass/ 子目录并移除文件名前缀。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 将 MassCore 模块从 MassEntity 中提取出来。 |
| 2025-11-21 | `d1de0b8a` | Zone Graph: Add an extra FZoneDrawAnnotator parameter to be able to customize zone graph draw debugs | 为调试绘制器添加额外参数，支持自定义绘制。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 Base 前缀改为 Default 前缀。 |

### 维护评价
ZoneGraph 插件**创建于 2021 年**，属于实验性功能（`IsExperimentalVersion=true`，且默认禁用）。从 git 记录看，直到 2026 年仍有活跃的代码维护，包括功能增强和架构调整（如与 Mass 框架的解耦）。这表明它仍在**积极开发**中，并可能作为 Mass AI 框架的底层基础之一。然而，由于其实验性质和默认禁用状态，**不建议在正式生产项目中未经充分测试直接依赖**。它适合用于研究、原型开发或作为特定高级 AI 系统的基础组件。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph)
- 官方文档：暂无
- 测试用例：位于 `ZoneGraphTestSuite` 模块内 (`Engine/Plugins/Runtime/ZoneGraph/Source/ZoneGraphTestSuite/`)