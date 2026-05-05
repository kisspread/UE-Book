# ZoneGraph — 核心运行时模块

> ZoneGraph plugin 的核心模块，包含所有运行时数据类型、空间索引、查询 API 和 A* 寻路。

## 模块概览

| 属性 | 值 |
|---|---|
| 模块名 | `ZoneGraph` |
| 类型 | Runtime |
| 加载阶段 | Default |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ZoneGraph/Source/ZoneGraph) | |

## 架构

ZoneGraph 核心模块由以下子系统组成：

```
UZoneGraphSubsystem (WorldSubsystem)
├── 注册/管理 AZoneGraphData 实例
├── 统一查询接口（跨多个 ZoneGraphData）
├── 编辑器端：FZoneGraphBuilder 构建器
└── 标签管理

AZoneGraphData (Actor)
├── FZoneGraphStorage（核心数据存储）
│   ├── TArray<FZoneData> Zones
│   ├── TArray<FZoneLaneData> Lanes
│   ├── TArray<FVector> BoundaryPoints / LanePoints
│   ├── TArray<FZoneLaneLinkData> LaneLinks
│   └── FZoneGraphBVTree ZoneBVTree
└── UZoneGraphRenderingComponent（可视化）

UZoneShapeComponent (编辑器端)
├── 定义形状（Spline / Polygon）
├── 引用 LaneProfile（车道配置模板）
├── 连接器系统（Connector / Connection）
└── 构建时 → 转换为 ZoneGraphStorage

FZoneGraphBuilder (构建器)
├── 注册/管理所有 UZoneShapeComponent
├── HashGrid 空间索引
├── 构建形状连接
└── 输出 FZoneGraphStorage 到 AZoneGraphData
```

## 核心类型

### 标签系统

| 类型 | 说明 |
|---|---|
| `FZoneGraphTag` | 单个标签（0-31 的 bit 索引） |
| `FZoneGraphTagMask` | 标签位掩码（uint32），支持按位运算 |
| `FZoneGraphTagFilter` | 标签过滤器：AnyTags + AllTags + NotTags |
| `FZoneGraphTagInfo` | 标签元数据：名称 + 颜色 |

标签系统最多支持 32 个自定义标签，在项目设置 `UZoneGraphSettings` 中配置。

```cpp
// 创建标签
FZoneGraphTag Sidewalk(0);  // 人行道
FZoneGraphTag Road(1);      // 车行道

// 创建掩码
FZoneGraphTagMask Mask;
Mask.Add(Sidewalk);
Mask.Add(Road);

// 过滤
FZoneGraphTagFilter Filter;
Filter.AnyTags = FZoneGraphTagMask(Sidewalk);  // 至少包含人行道
Filter.NotTags = FZoneGraphTagMask(FZoneGraphTag(5));  // 排除标签5

if (Filter.Pass(SomeLanesTags)) { /* 匹配 */ }
```

### 区域和车道数据

| 类型 | 说明 |
|---|---|
| `FZoneData` | 区域数据：边界点范围、车道范围、包围盒、标签 |
| `FZoneLaneData` | 车道数据：宽度、标签、点范围、链接范围、所属区域 |
| `FZoneLaneDesc` | 车道描述（编辑器端）：宽度 + 方向 + 标签 |
| `FZoneLaneProfile` | 车道配置模板：名称 + 多条并行车道描述 |
| `FZoneLaneProfileRef` | 车道配置引用（通过 GUID 引用） |

### 车道方向

```cpp
enum class EZoneLaneDirection : uint8
{
    None = 0x0,      // 无移动，作为间隔或中线
    Forward = 0x1,   // 相对于标记正向
    Backward = 0x2,  // 相对于标记反向
};
```

### 车道链接

| 类型 | 说明 |
|---|---|
| `EZoneLaneLinkType` | Outgoing（出口）、Incoming（入口）、Adjacent（相邻） |
| `EZoneLaneLinkFlags` | Left/Right/Splitting/Merging/OppositeDirection |
| `FZoneLaneLinkData` | 存储端链接数据 |
| `FZoneGraphLinkedLane` | 查询端链接数据（含完整 LaneHandle） |

### Handle 类型

| 类型 | 说明 |
|---|---|
| `FZoneHandle` | 区域句柄（索引） |
| `FZoneGraphDataHandle` | ZoneGraphData 句柄（Index + Generation） |
| `FZoneGraphLaneHandle` | 车道句柄（LaneIndex + DataHandle） |
| `FZoneGraphLaneLocation` | 车道上的完整位置信息（位置+方向+切线+上方向+段索引+距离） |
| `FZoneGraphCompactLaneLocation` | 精简版位置（仅 LaneHandle + 距离） |
| `FZoneGraphLaneSection` | 车道段（起止距离） |
| `FZoneGraphLanePath` | 车道路径（多个 LaneHandle 序列） |

### 数据存储

`FZoneGraphStorage` 是核心数据结构，存储一个 ZoneGraphData 的全部信息：

```cpp
struct FZoneGraphStorage
{
    TArray<FZoneData> Zones;           // 所有区域
    TArray<FZoneLaneData> Lanes;       // 所有车道
    TArray<FVector> BoundaryPoints;    // 区域边界点
    TArray<FVector> LanePoints;        // 车道点
    TArray<FVector> LaneUpVectors;     // 车道上方向
    TArray<FVector> LaneTangentVectors;// 车道切线
    TArray<float> LanePointProgressions; // 车道点进度距离
    TArray<FZoneLaneLinkData> LaneLinks; // 车道链接
    FBox Bounds;                       // 总包围盒
    FZoneGraphBVTree ZoneBVTree;       // BV树空间索引
};
```

### 形状系统

| 类型 | 说明 |
|---|---|
| `FZoneShapeType` | Spline（样条线）或 Polygon（多边形） |
| `FZoneShapePoint` | 形状控制点：位置、旋转、切线长度、类型 |
| `FZoneShapePointType` | Sharp/Bezier/AutoBezier/LaneProfile |
| `EZoneShapePolygonRoutingType` | Bezier 或 Arcs |
| `FZoneShapeConnector` | 形状连接器（端点位置+法线+车道配置） |
| `FZoneShapeConnection` | 两个连接器之间的连接 |

### 构建设置

`FZoneGraphBuildSettings` 控制构建行为：

| 设置 | 说明 |
|---|---|
| `CommonTessellationTolerance` | 通用细分容差（默认 1.0） |
| `SpecificTessellationTolerances` | 按标签的细分容差 |
| `LaneConnectionAngle` | 车道连接最大角度（默认 120°） |
| `LaneConnectionMask` | 用于检查连接的标签掩码 |
| `TurnThresholdAngle` | 左/右转判断角度阈值（默认 5°） |
| `PolygonRoutingRules` | 多边形路由规则 |
| `ConnectionSnapDistance` | 连接吸附距离（默认 25） |
| `ConnectionSnapAngle` | 连接吸附角度（默认 10°） |
| `DragEndpointAutoConnectRange` | 拖拽端点自动连接范围（默认 250） |

## 关键类

### UZoneGraphSubsystem

世界子系统，是运行时访问 ZoneGraph 的主要入口。

**查询方法**：

| 方法 | 说明 |
|---|---|
| `FindNearestLane` | 在所有注册数据中查找最近车道 |
| `FindOverlappingLanes` | 查找与边界重叠的车道 |
| `FindLaneOverlaps` | 查找完全重叠的车道段 |
| `AdvanceLaneLocation` | 沿车道前进指定距离 |
| `CalculateLocationAlongLane` | 计算车道上指定距离处的位置 |
| `FindNearestLocationOnLane` | 在指定车道上查找最近位置 |
| `IsLaneValid` | 验证车道句柄有效性 |
| `GetLaneLength/Width/Tags` | 获取车道属性 |
| `GetLinkedLanes` | 获取连接的车道列表 |
| `GetFirstLinkedLane` | 获取第一个匹配的连接车道 |
| `GetTagByName/GetTagName` | 标签名称查询 |

### UZoneShapeComponent

编辑器端形状组件（`IsEditorOnly() = true`），定义区域和车道。

**关键方法**：

| 方法 | 说明 |
|---|---|
| `UpdateShape` | 更新形状（计算自动切线、调整车道点） |
| `UpdateShapeConnectors` | 从点更新连接器 |
| `UpdateConnectedShapes` | 更新与其他形状的连接 |
| `IsShapeClosed` | 形状是否闭合 |
| `GetSplineLaneProfile` | 获取样条线车道配置 |
| `GetPolygonLaneProfiles` | 获取多边形各点车道配置 |

### AZoneShape

独立的 Zone 标记 Actor（`IsEditorOnly() = true`），包含一个 `UZoneShapeComponent`。

### AZoneGraphData

存储构建后的 ZoneGraph 数据的 Actor。在编辑器中由 Builder 自动创建和更新。

### FZoneGraphBuilder

构建器，负责将所有 `UZoneShapeComponent` 转换为 `FZoneGraphStorage`。

| 方法 | 说明 |
|---|---|
| `RegisterZoneShapeComponent` | 注册形状组件 |
| `UnregisterZoneShapeComponent` | 注销形状组件 |
| `BuildAll` | 构建所有 ZoneGraphData |
| `BuildSingleShape` | 单个形状转存储（用于预览） |
| `FindShapeConnections` | 查找形状间的连接 |

### FZoneGraphBVTree

量化 BV 树，用于快速空间查询。

| 方法 | 说明 |
|---|---|
| `Build` | 从 FBox 数组构建 |
| `Query` | 查询与边界重叠的节点 |

### FZoneGraphAStar

基于 UE 的 `FGraphAStar` 实现的车道级 A* 寻路。

```cpp
// 使用方式
FZoneGraphAStarWrapper Wrapper(Storage);
FZoneGraphAStar AStar(Wrapper);
FZoneGraphPathFilter PathFilter(Storage, Start, End, TagFilter);
TArray<int32> Path;
AStar.FindPath(StartLaneIndex, EndLaneIndex, PathFilter, Path);
```

## 回调委托

| 委托 | 说明 | 编辑器/运行时 |
|---|---|---|
| `OnPostZoneGraphDataAdded` | ZoneGraphData 注册后 | 运行时 |
| `OnPreZoneGraphDataRemoved` | ZoneGraphData 注销前 | 运行时 |
| `OnZoneGraphDataBuildDone` | 构建完成 | 编辑器 |
| `OnZoneGraphTagsChanged` | 标签变更 | 编辑器 |
| `OnZoneGraphLaneProfileChanged` | 车道配置变更 | 编辑器 |
| `OnZoneGraphBuildSettingsChanged` | 构建设置变更 | 编辑器 |
| `OnZoneGraphRequestRebuild` | 请求重建 | 编辑器 |

## MassEntity 集成

ZoneGraph 模块依赖 `MassEntity`，`UZoneGraphSubsystem` 实现了 `TMassExternalSubsystemTraits`，可在 MassEntity 系统中被查询使用。`GameThreadOnly = false` 允许多线程读取。

## 文件列表

| 文件 | 说明 |
|---|---|
| `ZoneGraphTypes.h/cpp` | 所有核心数据类型定义 |
| `ZoneGraphSubsystem.h/cpp` | 世界子系统 |
| `ZoneGraphBuilder.h/cpp` | 构建器 |
| `ZoneGraphData.h/cpp` | ZoneGraphData Actor |
| `ZoneGraphBVTree.h/cpp` | BV 树空间索引 |
| `ZoneGraphQuery.h/cpp` | 低层查询 API |
| `ZoneGraphAStar.h/cpp` | A* 寻路 |
| `ZoneGraphSettings.h/cpp` | 项目设置 |
| `ZoneShapeComponent.h/cpp` | 形状组件 |
| `ZoneShapeActor.h/cpp` | 形状 Actor |
| `ZoneShapeUtilities.h/cpp` | 形状细分工具 |
| `ZoneGraphDelegates.h/cpp` | 回调委托 |
| `ZoneGraphRenderingComponent.h/cpp` | 渲染组件 |
| `ZoneGraphRenderingUtilities.h` | 渲染工具 |
| `ZoneGraphObjectCRC32.h` | 对象哈希工具 |
| `BezierUtilities.h` | 已废弃，重定向到 Curves/ |
| `IZoneGraphModule.h` | 模块接口 |
| `ZoneGraphModule.cpp` | 模块实现 |
