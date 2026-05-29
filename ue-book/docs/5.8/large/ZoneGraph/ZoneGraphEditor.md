# Zone Graph

> Description missing.

| 属性 | 值 |
|---|---|
| 中文名 | 区域图 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ZoneGraph` (Runtime), `ZoneGraphEditor` (Editor), `ZoneGraphDebug` (Runtime), `ZoneGraphTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph) | |

## 用途

ZoneGraph 是一套基于**区域（Zone）和车道（Lane）**的 AI 寻路导航框架。它用可视化的方式在场景中绘制区域形状（样条线或多边形），然后根据预定义的**车道配置（Lane Profile）**自动生成车道网络。AI 代理可以在这个车道网络上进行路径规划和移动。

与 NavMesh 的区别在于：ZoneGraph 更侧重于**交通规则和车道约束**——每条车道有宽度、方向、标签等属性，适合模拟车辆交通、巡逻路线、队列移动等需要精确车道控制的场景。

核心概念：
- **Zone Shape（区域形状）**：用样条线或多边形定义的可通行区域
- **Lane Profile（车道配置）**：定义区域内车道的宽度、方向和标签
- **Tag 系统**：用标签过滤和分类不同的区域/车道，支持 Any/All/Not 组合查询
- **Zone Graph Data**：运行时自动生成的车道网络数据

## 使用场景

- 你在做一个开放世界赛车游戏 → 用 ZoneGraph 定义道路车道，AI 车辆按车道行驶
- 你需要 NPC 沿特定路线巡逻 → 用样条线形状定义巡逻路径，配置单向车道
- 你的 AI 系统需要基于标签过滤可通行区域 → 用 Tag 系统标记不同类型区域（人行道、机动车道、禁区等）
- 你需要可视化的交通网络编辑工具 → 用 ZoneGraph Editor 在编辑器中交互式绘制和编辑区域形状

## 蓝图用法

ZoneGraph 插件主要提供运行时数据查询接口，编辑端通过 ZoneGraph Editor 模块在编辑器中操作。

### 核心节点

ZoneGraph 运行时模块暴露的核心类型和组件（基于源码分析）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UZoneShapeComponent` | 区域形状组件，附加到 Actor 上定义可通行区域 | `UZoneShapeComponent` |
| `FZoneGraphTag` | 单个标签，用于标记车道/区域属性 | `FZoneGraphTag` |
| `FZoneGraphTagMask` | 标签掩码，组合多个标签进行过滤 | `FZoneGraphTagMask` |
| `FZoneGraphTagFilter` | 标签过滤器，支持 Any/All/Not 逻辑 | `FZoneGraphTagFilter` |
| `FZoneLaneDesc` | 车道描述，包含宽度、方向、标签 | `FZoneLaneDesc` |
| `FZoneLaneProfile` | 车道配置，定义一组车道的布局 | `FZoneLaneProfile` |

### 使用示例（蓝图描述）

1. **创建区域形状**：在场景中放置一个 Actor，添加 `UZoneShapeComponent`，在 Details 面板中绘制样条线或多边形轮廓
2. **配置车道**：在组件属性中选择或创建 Lane Profile，设置车道宽度、方向和标签
3. **构建区域图**：通过编辑器菜单 "Build Zone Graph" 生成运行时数据
4. **查询车道网络**：在运行时通过 ZoneGraph 查询接口获取车道信息进行 AI 路径规划

## C++ 用法

### 头文件引入

```cpp
// 运行时模块
#include "ZoneGraphTypes.h"
#include "ZoneGraphData.h"
#include "ZoneShapeComponent.h"

// 编辑器模块（仅编辑器使用）
#include "ZoneGraphEditorModule.h"
```

### 基本用法

标签系统是 ZoneGraph 的核心交互方式：

```cpp
// 来源: ZoneGraphTags.h (推断)
// 创建和使用标签
FZoneGraphTag MyTag;
MyTag.Bit = 0;  // 标签使用位索引

// 创建标签掩码
FZoneGraphTagMask Mask;
Mask.AddTag(MyTag);

// 使用过滤器查询
FZoneGraphTagFilter Filter;
Filter.AnyTags.AddTag(MyTag);  // 匹配包含此标签的任意车道
```

### 进阶用法

车道配置用于定义区域内的车道布局：

```cpp
// 定义单条车道
FZoneLaneDesc LaneDesc;
LaneDesc.Width = 400.0f;                           // 车道宽度（厘米）
LaneDesc.Direction = EZoneLaneDirection::Forward;   // 车道方向
LaneDesc.Tags.AddTag(MyTag);                        // 车道标签

// 定义车道配置
FZoneLaneProfile Profile;
Profile.Name = TEXT("TwoLaneRoad");
Profile.Lanes.Add(LaneDesc);
```

标签过滤器支持复杂的组合查询：

```cpp
// 多条件标签过滤
FZoneGraphTagFilter Filter;
Filter.AnyTags.AddTag(PedestrianTag);   // 匹配任一标签
Filter.AllTags.AddTag(SafeZoneTag);     // 必须包含所有标签
Filter.NotTags.AddTag(DangerTag);       // 排除特定标签
```

## Demo 示例

### Zone Shape 组件自定义

```cpp
// MyZoneActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "ZoneShapeComponent.h"
#include "MyZoneActor.generated.h"

UCLASS()
class AMyZoneActor : public AActor
{
    GENERATED_BODY()

public:
    AMyZoneActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UZoneShapeComponent> ZoneShapeComponent;

    /** 查询此区域内的车道数量 */
    UFUNCTION(BlueprintCallable)
    int32 GetLaneCount() const;

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyZoneActor.cpp
#include "MyZoneActor.h"
#include "ZoneShapeComponent.h"

AMyZoneActor::AMyZoneActor()
{
    ZoneShapeComponent = CreateDefaultSubobject<UZoneShapeComponent>(TEXT("ZoneShape"));
    RootComponent = ZoneShapeComponent;
}

int32 AMyZoneActor::GetLaneCount() const
{
    if (ZoneShapeComponent)
    {
        // 通过 ZoneShapeComponent 获取生成的车道信息
        return ZoneShapeComponent->GetLaneDescriptions().Num();
    }
    return 0;
}

void AMyZoneActor::BeginPlay()
{
    Super::BeginPlay();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ZoneGraph` | 核心运行时模块（区域图数据、车道计算） |
| `ZoneGraphEditor` | 编辑器可视化编辑和属性自定义 |
| `ZoneGraphDebug` | 运行时调试绘制 |
| `ZoneGraphTestSuite` | 自动化测试 |

ZoneGraph 核心模块依赖 `EditorFramework` 和 `UnrealEd`（含编辑器依赖是因为区域图构建在编辑器中完成）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 日志宏迁移到 UE_LOGF 格式 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | Mass 框架重构，移动头文件目录 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 中提取 MassCore 模块 |
| 2025-11-21 | `d1de0b8a` | Zone Graph: Add an extra FZoneDrawAnnotator parameter to be able to customize zone graph draw debugs | 新增 FZoneDrawAnnotator 参数用于自定义区域图调试绘制 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件命名规范化 |

### 维护评价

- **实验性状态**：插件标记为 `IsExperimentalVersion=true`，且默认未启用，表明 Epic 仍在迭代开发中
- **维护活跃**：2026 年仍有代码改动，但近期更新主要是 Mass 框架重构的附带改动和日志宏迁移，非功能性更新
- **ZoneGraph 专属更新**：最后一次实质性功能更新是 2025-11-21 的调试绘制自定义
- **API 可能变动**：作为实验性插件，未来版本可能有 API 变更
- **建议**：适合研究和原型开发，不建议在生产项目中重度依赖。关注 Mass 框架整合带来的架构变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph/Source/ZoneGraphTestSuite)