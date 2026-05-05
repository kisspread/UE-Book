# ZoneGraphDebug — 调试可视化模块

> 提供运行时 ZoneGraph 的可视化调试工具，包括测试 Actor 和 Gameplay Debugger 集成。

## 模块概览

| 属性 | 值 |
|---|---|
| 模块名 | `ZoneGraphDebug` |
| 类型 | Runtime |
| 加载阶段 | Default |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ZoneGraph/Source/ZoneGraphDebug) | |

## 依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | Actor/Component |
| `GameplayTags` | Gameplay 标签 |
| `GameplayTasks` | Gameplay 任务 |
| `AIModule` | AI 模块 |
| `ZoneGraph` | ZoneGraph 核心 |

## 关键类

### AZoneGraphTestingActor

可视化测试 Actor，可在编辑器中放置用于调试 ZoneGraph 功能。

**功能**：
- 显示最近车道位置和方向
- 显示车道链接关系
- 显示 BV 树查询结果
- 沿车道前进模拟
- 支持自定义测试逻辑（通过 `UZoneLaneTest`）

**属性**：

| 属性 | 说明 |
|---|---|
| `SearchExtent` | 搜索范围 |
| `AdvanceDistance` | 沿车道前进距离 |
| `NearestTestOffset` | 最近点测试偏移 |
| `QueryFilter` | 查询标签过滤器 |
| `bDrawLinkedLanes` | 是否绘制连接的车道 |
| `bDrawLaneTangentVectors` | 是否绘制车道切线 |
| `bDrawLaneSmoothing` | 是否绘制车道平滑 |
| `bDrawBVTreeQuery` | 是否绘制 BV 树查询 |
| `bDrawLanePath` | 是否绘制车道路径（实验性） |
| `OtherActor` | 用于路径测试的另一个 Actor |
| `CustomTests` | 自定义测试数组 |

### UZoneGraphTestingComponent

测试组件，包含核心测试逻辑。

**蓝图方法**：

| 方法 | 说明 |
|---|---|
| `EnableCustomTests` | 启用自定义测试通知 |
| `DisableCustomTests` | 禁用自定义测试通知 |

### UZoneLaneTest

自定义车道测试基类（Abstract），可继承以实现自定义测试逻辑。

```cpp
UCLASS(Abstract, EditInlineNew)
class UZoneLaneTest : public UObject
{
    // 当车道位置更新时调用
    virtual void OnLaneLocationUpdated(
        const FZoneGraphLaneLocation& PrevLaneLocation,
        const FZoneGraphLaneLocation& NextLaneLocation) PURE_VIRTUAL(...);

    // 绘制调试信息
    virtual void Draw(FPrimitiveDrawInterface* PDI) const {};
};
```

## 使用方法

1. 在编辑器中放置 `AZoneGraphTestingActor`
2. 调整 `SearchExtent` 设置搜索范围
3. 设置 `QueryFilter` 过滤感兴趣的标签
4. 启用各种绘制选项查看调试信息
5. 移动 Actor 查看实时查询结果

## 文件列表

| 文件 | 说明 |
|---|---|
| `ZoneGraphTestingActor.h/cpp` | 测试 Actor 和组件 |
| `IZoneGraphDebug.h` | 模块接口 |
| `ZoneGraphDebug.cpp` | 模块实现（含 Gameplay Debugger 集成） |
