# SourceFilteringTrace 模块

> 运行时过滤引擎：实现过滤器类、过滤管理器、World 过滤和 Trace 数据输出。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Runtime |
| LoadingPhase | PostEngineInit |
| TargetConfigurationDenyList | Shipping |

## 职责

SourceFilteringTrace 是插件的核心运行时模块，负责：

1. 定义 `UDataSourceFilter` 和 `UDataSourceFilterSet` 基类
2. 管理每个 World 的过滤状态（`FSourceFilterManager`）
3. 跟踪 World 生命周期并应用 World 级别过滤（`FTraceWorldFiltering`）
4. 将过滤器状态输出到 Unreal Trace 系统（`FSourceFilterTrace`）
5. 提供全局单例管理过滤集合和设置（`FTraceSourceFiltering`）
6. 优化过滤器执行顺序和异步调度

## 源文件

### Public 头文件

| 文件 | 说明 |
|---|---|
| `DataSourceFilter.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Public/DataSourceFilter.h) — 过滤器基类 |
| `DataSourceFilterSet.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Public/DataSourceFilterSet.h) — 过滤器集合 |
| `SourceFilterCollection.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Public/SourceFilterCollection.h) — 过滤器数据资产 |
| `EmptySourceFilter.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Public/EmptySourceFilter.h) — 缺失类占位 |
| `SourceFilterTrace.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Public/SourceFilterTrace.h) — Trace 输出宏 |
| `TraceSourceFiltering.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Public/TraceSourceFiltering.h) — 全局单例 |
| `TraceWorldFiltering.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Public/TraceWorldFiltering.h) — World 过滤 |
| `TraceSourceFilteringProjectSettings.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Public/TraceSourceFilteringProjectSettings.h) — 项目设置 |
| `TraceSourceFilteringTestBase.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Public/TraceSourceFilteringTestBase.h) — 测试基类 |

### Private 实现

| 文件 | 说明 |
|---|---|
| `SourceFilterManager.h/cpp` | 每个 World 的过滤管理器 |
| `SourceFilterSetup.h/cpp` | 全局过滤器配置优化 |
| `SourceFilter.h` | 内部 FFilter 结构 |
| `SourceFilterSet.h` | 内部 FFilterSet 结构 |
| `ResultCache.h/cpp` | 过滤结果缓存 |
| `ActorFiltering.h` | Actor 收集和迭代器 |
| `SourceFilteringAsyncTasks.h/cpp` | 异步过滤任务 |
| `SourceFilteringTickFunction.h/cpp` | 自定义 Tick 函数 |
| `TraceSourceFiltering.cpp` | 全局单例实现 |
| `TraceWorldFiltering.cpp` | World 过滤实现 |
| `TraceSourceFilteringTestBase.cpp` | 测试基类实现 |
| `SourceFilterTrace.cpp` | Trace 输出实现 |
| `SourceFilterPresets.h/cpp` | 预设加载/管理 |
| `DataSourceFilterSet.cpp` | FilterSet 实现 |
| `SourceFilterCollection.cpp` | Collection 实现 |
| `SourceFilteringTraceModule.cpp` | 模块初始化 |

## 核心类

### UDataSourceFilter

所有自定义过滤器的基类。继承自 `UObject` 并实现 `IDataSourceFilterInterface`。

```cpp
UCLASS(MinimalAPI, Blueprintable)
class UDataSourceFilter : public UObject, public IDataSourceFilterInterface
{
    // 判断 Actor 是否通过过滤（蓝图可重写）
    UFUNCTION(BlueprintNativeEvent)
    bool DoesActorPassFilter(const AActor* InActor) const;

    // C++ 重写点（内部实现）
    virtual bool DoesActorPassFilter_Internal(const AActor* InActor) const;

    // 过滤器配置（EditDefaultsOnly，可在蓝图中设置）
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FDataSourceFilterConfiguration Configuration;
};
```

**关键设计**：
- `DoesActorPassFilter` 是 BlueprintNativeEvent，允许 Blueprint 和 C++ 两种方式重写
- `IsEnabled()` 和 `GetConfiguration()` 是 `final`，不可重写
- 通过 `Configuration.bOnlyApplyDuringActorSpawn` 可标记为仅生成时过滤
- 通过 `Configuration.bCanRunAsynchronously` 可声明可异步执行

### UDataSourceFilterSet

过滤器集合，继承自 `UDataSourceFilter` 并实现 `IDataSourceFilterSetInterface`。一个 FilterSet 可以包含多个子过滤器，并通过 AND/OR/NOT 模式组合结果。

```cpp
UCLASS(MinimalAPI, NotBlueprintable)
class UDataSourceFilterSet : public UDataSourceFilter, public IDataSourceFilterSetInterface
{
    const TArray<TObjectPtr<UDataSourceFilter>>& GetFilters() const;
    void SetFilterMode(EFilterSetMode InMode);
    virtual EFilterSetMode GetFilterSetMode() const override;

protected:
    virtual bool DoesActorPassFilter_Internal(const AActor* InActor) const override;

    TArray<TObjectPtr<UDataSourceFilter>> Filters;
    EFilterSetMode Mode;
};
```

**注意**：`NotBlueprintable` — FilterSet 不能直接在蓝图中创建，只能通过 `USourceFilterCollection` API 创建。

### USourceFilterCollection

过滤器集合数据资产（`UDataAsset`），管理所有活跃的过滤器实例。支持序列化/反序列化，可保存为 `.uasset` 预设。

核心 API：

| 方法 | 说明 |
|---|---|
| `AddFilterOfClass(Class)` | 添加指定类的过滤器实例 |
| `AddFilterOfClassToSet(Class, Set)` | 将过滤器添加到指定集合 |
| `RemoveFilter(Filter)` | 移除过滤器 |
| `ReplaceFilter(Dest, Src)` | 替换过滤器 |
| `MoveFilter(Filter, Dest)` | 移动过滤器到目标集合（null=根级） |
| `SetFilterState(Filter, bEnabled)` | 启用/禁用过滤器 |
| `ConvertFilterToSet(Filter, Mode)` | 将单个过滤器转为集合 |
| `MakeFilterSet(F1, F2, Mode)` | 创建包含两个过滤器的集合 |
| `MakeEmptyFilterSet(Mode)` | 创建空集合 |
| `SetFilterSetMode(Set, Mode)` | 设置集合的逻辑模式 |
| `AddClassFilter(Class)` | 添加 Actor 类过滤 |
| `RemoveClassFilter(Class)` | 移除 Actor 类过滤 |
| `AddFiltersFromPreset(Names, Mapping)` | 从预设数据重建过滤器树 |
| `CopyData(Other)` | 从另一个集合复制数据 |
| `Reset()` | 清空所有过滤器 |

### FTraceSourceFiltering

全局单例，管理 `USourceFilterCollection` 和 `UTraceSourceFilteringSettings`。

```cpp
class FTraceSourceFiltering : public FGCObject
{
    static void Initialize();
    static FTraceSourceFiltering& Get();

    USourceFilterCollection* GetFilterCollection();
    UTraceSourceFilteringSettings* GetSettings();

    // 处理远程命令（来自 Insights UI）
    void ProcessRemoteCommand(const FString& Command, const TArray<FString>& Arguments);
};
```

### FTraceWorldFiltering

World 级别过滤的静态管理器，跟踪所有活跃 World 实例并管理其过滤状态。

```cpp
struct FTraceWorldFiltering
{
    static void Initialize();
    static void Destroy();

    // 查询
    static const FSourceFilterManager* GetWorldSourceFilterManager(const UWorld* World);
    static const TArray<const UWorld*>& GetWorlds();
    static bool IsWorldTypeTraceable(EWorldType::Type InType);
    static bool IsWorldNetModeTraceable(ENetMode InNetMode);

    // 设置
    static void SetStateByWorldType(EWorldType::Type WorldType, bool bState);
    static void SetStateByWorldNetMode(ENetMode NetMode, bool bState);
    static void SetWorldState(const UWorld* InWorld, bool bState);

    // 事件
    static FTraceWorldFilterStateChanged& OnFilterStateChanged();
};
```

**World 跟踪机制**：通过 `FCoreUObjectDelegates::OnWorldCreated` 和 `UWorld::OnWorldCleanup` 回调自动跟踪 World 生命周期。

### FSourceFilterManager

每个 `UWorld` 对应一个 `FSourceFilterManager`，负责该 World 内所有 Actor 的过滤状态管理。

内部结构：
- **FSourceFilterSetup** — 全局过滤器配置，优化后的执行计划
- **FFilter** — 简化的过滤器描述（hash、interval、async 标记等）
- **FFilterSet** — 简化的过滤器集合描述
- **FFilteredActorCollector** — Actor 收集器，按类过滤
- **FResultCache** — 过滤结果位缓存

执行流程：
1. `ResetPerFrameData()` — 重置帧数据
2. `ApplyGameThreadFilters()` — 应用游戏线程过滤器
3. `ApplyAsyncFilters()` — 应用异步过滤器（TaskGraph）
4. `ApplyFilterResults()` — 将结果写入 Trace 状态
5. `DrawFilterResults()` — 调试绘制（如果启用）

### FSourceFilterSetup

全局过滤器配置优化器。将 `USourceFilterCollection` 中的 UObject 层级结构转换为优化的内部结构：

- 扁平化 FilterSet 层级
- 按预估成本排序过滤器（spawn-only 优先，异步优先）
- 预计算 spawn 过滤器的可跳过/可丢弃集合
- 分离游戏线程和异步过滤器

## 内部数据结构

### FFilter

```cpp
struct FFilter
{
    const UDataSourceFilter* Filter;  // UObject 引用
    uint32 FilterHash;                // 过滤器 hash
    uint32 FilterSetHash;            // 所属集合 hash
    uint32 TickFrameOffset;          // 间隔帧索引
    uint32 ResultOffset;             // 结果位数组偏移
    uint8 TickInterval;              // 评估间隔
    uint8 bExpectedValue : 1;        // 预期通过值（考虑 NOT）
    uint8 bNative : 1;               // 是否原生实现（跳过 thunk）
    uint8 bOnSpawnOnly : 1;          // 仅生成时评估
    uint8 bCanRunAsynchronously : 1; // 可异步执行
    uint8 bEarlyOutPass : 1;         // 通过时提前退出
    uint8 bEarlyOutDiscard : 1;      // 失败时提前丢弃
};
```

### FFilterSet

```cpp
struct FFilterSet
{
    TArray<FFilter, TInlineAllocator<8>> FilterEntries;  // 直接过滤器
    TArray<FFilterSet> ChildFilterSets;                   // 子集合
    uint32 FilterSetHash;
    uint32 ResultOffset;
    EFilterSetMode Mode;
    uint8 bContainsGameThreadFilter : 1;
    uint8 bContainsAsyncFilter : 1;
    uint8 bInitialPassingValue : 1;  // AND=false, OR=true, NOT=true
};
```

### FFilteredActorCollector

基于 `FActorClassFilter` 收集 World 中匹配的 Actor 实例。在编辑器中优化为直接遍历 `Level->Actors`，运行时使用 `ForEachObjectOfClasses`。

## Trace 输出

当 `SOURCE_FILTER_TRACE_ENABLED` 为 1 时（非 Shipping，非 Program），插件通过自定义 Trace Channel `TraceSourceFiltersChannel` 输出以下事件：

| 宏 | 说明 |
|---|---|
| `TRACE_FILTER_CLASS(Class)` | 输出过滤器类定义 |
| `TRACE_FILTER_INSTANCE(Filter)` | 输出过滤器实例 |
| `TRACE_FILTER_SET(Set)` | 输出过滤器集合 |
| `TRACE_FILTER_OPERATION(Inst, Op, Param)` | 输出过滤器操作（增删改） |
| `TRACE_FILTER_SETTINGS_VALUE(Name, Value)` | 输出设置变更 |
| `TRACE_WORLD_INSTANCE(World)` | 输出 World 实例信息 |
| `TRACE_WORLD_OPERATION(World, Op, Param)` | 输出 World 操作 |

这些 Trace 数据被 Unreal Insights 的 Source Filtering 页签消费，在 Editor UI 中重建过滤器状态。

## 异步执行

过滤器可以声明为异步安全（`bCanRunAsynchronously = true`），此时 `FSourceFilterManager` 会通过 TaskGraph 将过滤器评估分发到工作线程：

- `FActorFilterAsyncTask` — 在工作线程评估异步过滤器
- `FActorFilterApplyAsyncTask` — 在工作线程应用过滤结果
- `FActorFilterDrawStateAsyncTask` — 异步准备调试绘制数据

同步和异步过滤器通过两个独立的 `FGraphEventRef` 同步，最终在 `ApplyFilterResults` 中合并。

## 预设系统

通过 `FSourceFilterPresets` 提供预设管理：

- `GetPresets()` — 扫描资产注册表找到所有 `USourceFilterCollection` 资产
- `LoadPreset()` — 加载预设并替换当前过滤状态
- `ListAvailablePresets()` — 列出可用预设
- `LoadPresetCommand()` — 控制台命令支持

项目可通过 `UTraceSourceFilteringProjectSettings` 配置：
- `CookedSourceFilterClasses` — 打包时包含的过滤器类
- `DefaultFilterPreset` — 启动时自动加载的默认预设

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、TaskGraph |
| `CoreUObject` | UObject 系统 |
| `TraceLog` | Trace 日志基础设施 |
| `Engine` | AActor、UWorld、Tick 函数 |
| `SourceFilteringCore` | 接口和数据结构定义 |
| `PropertyPath` | 属性路径访问 |
| `AssetRegistry` | 资产扫描（预设发现） |
| `DeveloperSettings` | 项目设置基类 |
| `UnrealEd`（仅编辑器） | 编辑器集成 |
