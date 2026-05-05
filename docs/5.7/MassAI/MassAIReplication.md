# MassAI

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 Unreal Engine Mass Entity 框架的 AI 扩展插件，为大规模实体（Mass Entity）提供完整的 AI 行为和导航能力。它解决了传统 AI 系统（如 Behavior Tree + Navigation Mesh）在处理成千上万个 AI 代理时的性能瓶颈问题。

核心功能包括：
- **大规模 AI 行为系统**：基于 Mass Entity 的高性能行为决策
- **多路径导航支持**：ZoneGraph 车道导航、NavMesh 导航等多种导航方式
- **网络复制**：在多人游戏中高效同步大量 AI 代理的状态和路径数据
- **调试工具**：可视化调试 Mass AI 代理的行为和导航状态

## 使用场景

- 你在开发开放世界游戏，需要同时模拟数千个 NPC 的行为和移动 → 用 MassAI
- 你需要在多人游戏中同步大量 AI 代理的导航状态 → 用 MassAIReplication
- 你使用 ZoneGraph 系统定义车道网络，需要 AI 代理沿车道移动 → 用 MassZoneGraphNavigation
- 你需要 AI 代理在 NavMesh 上进行路径规划 → 用 MassNavMeshNavigation
- 你需要可视化调试大量 AI 代理的决策过程 → 用 MassAIDebug

## 模块架构

```
MassAI/
├── MassAIBehavior          ← 核心 AI 行为系统
├── MassAIBehaviorEditor    ← 行为系统编辑器支持
├── MassAIDebug             ← 调试可视化工具
├── MassAIReplication       ← 网络复制支持
├── MassAITestSuite         ← 自动化测试
├── MassNavigation          ← 导航核心功能
├── MassNavigationEditor    ← 导航编辑器支持
├── MassNavMeshNavigation   ← NavMesh 导航实现
└── MassZoneGraphNavigation ← ZoneGraph 车道导航
```

## 蓝图用法

### MassAIReplication 模块

#### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetBubblePathData` | 在服务器端设置客户端气泡中的路径数据 | `TMassClientBubblePathHandler` |
| `InitEntity` | 从复制数据初始化实体的导航状态 | `FReplicatedAgentPathData` |
| `ApplyToEntity` | 将复制的路径数据应用到实体 | `FReplicatedAgentPathData` |

#### 使用示例

在自定义的 `FReplicatedAgentBase` 派生类中添加路径复制支持：

```
1. 创建继承自 FReplicatedAgentBase 的结构体
2. 添加 FReplicatedAgentPathData 成员变量
3. 实现 GetReplicatedPathDataMutable() 访问器函数
4. 在 TClientBubbleHandlerBase 派生类中使用 TMassClientBubblePathHandler
```

## C++ 用法

### 头文件引入

```cpp
#include "MassReplicationPathHandlers.h"
#include "MassNavigationFragments.h"
#include "MassZoneGraphNavigationFragments.h"
```

### 基本用法

**定义支持路径复制的 Agent 数据结构**：

```cpp
// 来源: MassReplicationPathHandlers.h

// 1. 定义复制的 Agent 数据，包含路径信息
USTRUCT()
struct FMyReplicatedAgent : public FReplicatedAgentBase
{
    GENERATED_BODY()
    
    // 路径复制数据
    UPROPERTY(Transient)
    FReplicatedAgentPathData PathData;
    
    // 必须提供此访问器
    FReplicatedAgentPathData& GetReplicatedPathDataMutable()
    {
        return PathData;
    }
};

// 2. 从复制数据初始化实体
void InitializeEntityFromReplication(const UWorld& World, 
    const FMassEntityView& EntityView,
    const FReplicatedAgentPathData& ReplicatedData)
{
    FMassZoneGraphLaneLocationFragment LaneLocation;
    FMassMoveTargetFragment MoveTarget;
    FMassZoneGraphPathRequestFragment PathRequest;
    
    // 从复制数据初始化片段
    ReplicatedData.InitEntity(World, EntityView, 
        LaneLocation, MoveTarget, PathRequest);
}
```

### 进阶用法

**在客户端气泡处理器中集成路径复制**：

```cpp
// 来源: MassReplicationPathHandlers.h

// 1. 定义客户端气泡处理器
class UMyClientBubbleHandler : public TClientBubbleHandlerBase<FMyReplicatedAgent>
{
    // 2. 添加路径处理器
    TMassClientBubblePathHandler<FMyReplicatedAgent> PathHandler;
    
public:
    UMyClientBubbleHandler() : PathHandler(*this) {}
    
    // 3. 服务器端：设置路径数据
    void ServerSetPathData(FMassReplicatedAgentHandle Handle,
        const FMassZoneGraphPathRequestFragment& PathRequest,
        const FMassMoveTargetFragment& MoveTarget,
        const FMassZoneGraphLaneLocationFragment& LaneLocation)
    {
        PathHandler.SetBubblePathData(Handle, PathRequest, MoveTarget, LaneLocation);
    }
    
    // 4. 客户端：配置生成查询
    static void ConfigureSpawnQuery(FMassEntityQuery& Query)
    {
        TMassClientBubblePathHandler<FMyReplicatedAgent>::AddRequirementsForSpawnQuery(Query);
    }
    
    void CacheForSpawnQuery(FMassExecutionContext& Context)
    {
        PathHandler.CacheFragmentViewsForSpawnQuery(Context);
    }
};
```

## Demo 示例

### 自定义路径复制 Agent

```cpp
// MyReplicatedAgent.h
#pragma once

#include "MassReplicationTypes.h"
#include "MassReplicationPathHandlers.h"
#include "MyReplicatedAgent.generated.h"

USTRUCT()
struct FMyReplicatedAgent : public FReplicatedAgentBase
{
    GENERATED_BODY()
    
    UPROPERTY(Transient)
    FReplicatedAgentPathData PathData;
    
    FReplicatedAgentPathData& GetReplicatedPathDataMutable()
    {
        return PathData;
    }
};
```

```cpp
// MyReplicatedAgent.cpp
#include "MyReplicatedAgent.h"

// FReplicatedAgentPathData 的构造函数会自动从片段提取数据
// InitEntity 和 ApplyToEntity 用于在客户端重建实体状态
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass Entity 核心框架 |
| `MassReplication` | Mass 实体网络复制基础 |
| `MassNavigation` | 导航片段和功能 |
| `MassZoneGraphNavigation` | ZoneGraph 导航片段 |
| `ZoneGraph` | ZoneGraph 车道系统 |

## 维护状态

### 近期更新

```
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 939cc6e51c10 Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- e21fd848e1d8 [Mass Navigation] Prevent MoveTarget progress to continue without it's entity. Improved tangent computation on FMassNavMeshShortPathFragment. Change verbosity of navmesh boundary update log. #jira UE-227557 #rb Mieszko.Zielinski
```

- `ec9009980d52` - 代码生成优化，添加内联宏
- `939cc6e51c10` - DLL 导出符号规范化
- `e21fd848e1d8` - 修复导航问题，改进切线计算

### 维护评价

**活跃维护中** ✅

- **创建时间**：2021 年，约 4 年历史
- **实验性状态**：标记为 `IsExperimentalVersion=true`，API 可能变化
- **更新频率**：近期有实质性功能更新和 bug 修复
- **开发团队**：Epic Games 官方维护，用于 Fortnite 等项目
- **推荐程度**：适合需要大规模 AI 的项目，但需注意实验性 API 的稳定性风险

⚠️ **注意**：此插件默认禁用（`EnabledByDefault=false`），需要在项目设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI)
- [Mass Entity 框架文档](https://docs.unrealengine.com/en-US/mass-entity-in-unreal-engine/)
- [ZoneGraph 系统](https://docs.unrealengine.com/en-US/zone-graph-in-unreal-engine/)